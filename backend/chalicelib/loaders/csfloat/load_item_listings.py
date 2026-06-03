from datetime import date
from sqlalchemy.dialects.postgresql import insert as pg_insert
from chalicelib.db import db_transaction
from chalicelib.models import ItemMaster, ItemDayListing, CSFloatListing
from chalicelib.connectors.csfloat.client import get_item_listings
from chalicelib.connectors.csfloat.schemas import Listing
from chalicelib.event_definition.helpers.csfloat_helpers import parse_market_hash_name
from chalicelib.event_definition.helpers.generic_helpers import bulk_get_or_create_items
from chalicelib.loaders.feed_loader import FeedLoader

class CSFloatListingLoader(FeedLoader):
    def extract(self):
        self.logger.create_log_entry(status='Extracting')
        listings: list[Listing] = get_item_listings()
        self.logger.update_log_entry(status='Extracting', success=True)
        return listings

    @db_transaction
    def bronze_load(self, raw_data, db=None):
        if not raw_data:
            return []
        
        self.logger.create_log_entry(status='Loading Bronze')
        # Load into CSFloatListing bronze table
        bronze_records = [
            CSFloatListing(
                job_id=self.jobid,
                market_hash_name=listing.market_hash_name,
                quantity=listing.quantity,
                min_price=listing.price
            )
            for listing in raw_data
        ]
        db.add_all(bronze_records)
        self.logger.update_log_entry(status='Loading Bronze', success=True)
        return raw_data

    @db_transaction
    def silver_transform(self, raw_data, db=None):
        self.logger.create_log_entry(status='Transforming Silver')
        # Source: Bronze table
        bronze_records = db.query(CSFloatListing).filter(
            CSFloatListing.job_id == self.jobid
        ).all()
 
        if not bronze_records:
            return {"status": "error", "message": "No bronze records found for this job"}
 
        today = date.today()
        
        items_to_resolve = []
        for listing in bronze_records:
            gun, skin, wear, stattrack = parse_market_hash_name(listing.market_hash_name)
            items_to_resolve.append({
                "full_name": listing.market_hash_name,
                "item_type": gun,
                "wear": wear,
                "stat_track": stattrack
            })
 
        # Resolve items (Destination 1: ItemMaster)
        item_map = bulk_get_or_create_items(
            db=db, 
            items_data=items_to_resolve
        )
 
        # Prepare for Destination 2: ItemDayListing
        listing_values = []
        for listing in bronze_records:
            item_id = item_map.get(listing.market_hash_name)
            if not item_id: continue
 
            listing_values.append({
                "item_id": item_id,
                "datasource_id": self.datasource_id,
                "day": today,
                "listings_count": listing.quantity,
                "min_price": listing.min_price
            })
 
        if listing_values:
            listing_stmt = pg_insert(ItemDayListing).values(listing_values)
            upsert_listing = listing_stmt.on_conflict_do_update(
                index_elements=['item_id', 'datasource_id', 'day'],
                set_={
                    "listings_count": listing_stmt.excluded.listings_count,
                    "min_price": listing_stmt.excluded.min_price
                }
            )
            db.execute(upsert_listing)
        
        self.logger.update_log_entry(status='Transforming Silver', success=True)
        return {"status": "success", "processed_items": len(raw_data)}


