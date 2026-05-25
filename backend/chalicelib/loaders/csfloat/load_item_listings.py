from datetime import date
from sqlalchemy.dialects.postgresql import insert as pg_insert
from chalicelib.db import get_db
from chalicelib.models import ItemMaster, ItemDayListing
from csfloat.client import get_item_listings
from csfloat.schemas import Listing
from chalicelib.helpers.csfloat_helpers import parse_market_hash_name
from chalicelib.helpers.generic_helpers import bulk_get_or_create_items
from objects.feed_loader import FeedLoader

class CSFloatListingLoader(FeedLoader):
    def bronze_load(self):
        listings: list[Listing] = get_item_listings()
        self.log(f"Fetched {len(listings) if listings else 0} listings from CSFloat")
        return listings

    def silver_transform(self, raw_data):
        if not raw_data:
            return {"status": "error", "message": "No listings to transform"}

        datasource_id = self.parameters.get("datasource_id", "1")
        today = date.today()
        
        items_to_resolve = []
        for listing in raw_data:
            gun, skin, wear, stattrack = parse_market_hash_name(listing.market_hash_name)
            items_to_resolve.append({
                "full_name": listing.market_hash_name,
                "item_type": gun,
                "wear": wear,
                "stat_track": stattrack
            })

        with get_db() as db:
            item_map = bulk_get_or_create_items(
                db=db, 
                datasource_id=datasource_id, 
                items_data=items_to_resolve
            )

            listing_values = []
            for listing in raw_data:
                item_id = item_map.get(listing.market_hash_name)
                if not item_id: continue

                listing_values.append({
                    "item_id": item_id,
                    "datasource_id": datasource_id,
                    "day": today,
                    "listings_count": listing.quantity,
                    "min_price": listing.price
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
            
            db.commit()

        self.log(f"Processed {len(raw_data)} listings.")
        return {"status": "success", "processed_items": len(raw_data)}
