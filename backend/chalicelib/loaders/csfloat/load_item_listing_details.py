from datetime import date, datetime
from sqlalchemy.dialects.postgresql import insert as pg_insert
from chalicelib.db import db_transaction
from chalicelib.models import ItemListingDetail, CSFloatListingDetail
from chalicelib.connectors.csfloat.client import get_item_listing_details
from chalicelib.connectors.csfloat.schemas import ListingDetail
from chalicelib.event_definition.helpers.csfloat_helpers import parse_market_hash_name
from chalicelib.event_definition.helpers.generic_helpers import bulk_get_or_create_items
from chalicelib.loaders.feed_loader import FeedLoader

class CSFloatListingDetailLoader(FeedLoader):
    def extract(self, market_hash_names: list[str]):
        """
        Fetches every active CSFloat listing for each requested item.
        Parameter-only: the caller decides which items to fetch.
        """
        self.log(f"Extracting listing details from CSFloat for {len(market_hash_names)} item(s)")
        all_details: list[ListingDetail] = []
        for market_hash_name in market_hash_names:
            all_details.extend(get_item_listing_details(market_hash_name))
        self.log(f"Extracted {len(all_details)} listing detail record(s)")
        return all_details

    @db_transaction
    def bronze_load(self, raw_data, job_id: str, db=None):
        if not raw_data:
            return []

        bronze_records = [
            CSFloatListingDetail(
                job_id=job_id,
                listing_id=detail.id,
                created_at=detail.created_at,
                type=detail.type,
                price=detail.price,
                state=detail.state,
                is_seller=detail.is_seller,
                is_watchlisted=detail.is_watchlisted,
                watchers=detail.watchers,
                seller=detail.seller,
                item=detail.item,
                reference=detail.reference,
                auction_details=detail.auction_details,
            )
            for detail in raw_data
        ]
        db.add_all(bronze_records)
        return raw_data

    @db_transaction
    def silver_transform(self, raw_data, job_id: str, db=None):
        # Source: Bronze table (stamped by the loading job)
        bronze_records = db.query(CSFloatListingDetail).filter(
            CSFloatListingDetail.job_id == job_id
        ).all()

        if not bronze_records:
            return {"status": "error", "message": "No bronze records found for this job"}

        today = date.today()

        items_to_resolve = []
        for record in bronze_records:
            gun, skin, wear, stattrack = parse_market_hash_name(record.item['market_hash_name'])
            items_to_resolve.append({
                "full_name": record.item['market_hash_name'],
                "item_type": gun,
                "wear": wear,
                "stat_track": stattrack
            })

        item_map = bulk_get_or_create_items(db=db, items_data=items_to_resolve)

        detail_values = []
        for record in bronze_records:
            item_id = item_map.get(record.item['market_hash_name'])
            if not item_id:
                continue

            item = record.item
            detail_values.append({
                "listing_id": record.listing_id,
                "item_id": item_id,
                "datasource_id": self.datasource_id,
                "day": today,
                "listing_created_ts": datetime.fromisoformat(record.created_at.replace('Z', '+00:00')),
                "listing_type": record.type,
                "list_price": record.price,
                "def_index": item.get('def_index'),
                "paint_index": item.get('paint_index'),
                "paint_seed": item.get('paint_seed'),
                "float_value": item.get('float_value'),
                "is_stattrak": item.get('is_stattrak'),
                "is_souvenir": item.get('is_souvenir'),
            })

        if detail_values:
            detail_stmt = pg_insert(ItemListingDetail).values(detail_values)
            upsert_detail = detail_stmt.on_conflict_do_update(
                index_elements=['listing_id'],
                set_={
                    "item_id": detail_stmt.excluded.item_id,
                    "datasource_id": detail_stmt.excluded.datasource_id,
                    "day": detail_stmt.excluded.day,
                    "listing_created_ts": detail_stmt.excluded.listing_created_ts,
                    "listing_type": detail_stmt.excluded.listing_type,
                    "list_price": detail_stmt.excluded.list_price,
                    "def_index": detail_stmt.excluded.def_index,
                    "paint_index": detail_stmt.excluded.paint_index,
                    "paint_seed": detail_stmt.excluded.paint_seed,
                    "float_value": detail_stmt.excluded.float_value,
                    "is_stattrak": detail_stmt.excluded.is_stattrak,
                    "is_souvenir": detail_stmt.excluded.is_souvenir,
                }
            )
            db.execute(upsert_detail)

        return {"status": "success", "processed_items": len(bronze_records)}
