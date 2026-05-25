from typing import List
from chalicelib.db import get_db
from chalicelib.models import CSFloatListingDetail
from csfloat.client import get_item_listing_details # Assuming this exists
from objects.feed_loader import FeedLoader

class CSFloatListingDetailLoader(FeedLoader):
    def extract(self):
        self.log("Extracting raw item listing detail data from CSFloat")
        # In a real scenario, this would likely take a list of IDs as parameters
        data = get_item_listing_details() 
        return data

    def bronze_load(self, raw_data):
        if not raw_data:
            return []
            
        with get_db() as db:
            bronze_records = [
                CSFloatListingDetail(
                    job_id=self.jobid,
                    listing_id=item.get('id') if isinstance(item, dict) else getattr(item, 'id', None),
                    created_at=item.get('created_at') if isinstance(item, dict) else getattr(item, 'created_at', None),
                    type=item.get('type') if isinstance(item, dict) else getattr(item, 'type', None),
                    price=item.get('price') if isinstance(item, dict) else getattr(item, 'price', None),
                    state=item.get('state') if isinstance(item, dict) else getattr(item, 'state', None),
                    is_seller=item.get('is_seller') if isinstance(item, dict) else getattr(item, 'is_seller', None),
                    min_offer_price=item.get('min_offer_price') if isinstance(item, dict) else getattr(item, 'min_offer_price', None),
                    max_offer_discount=item.get('max_offer_discount') if isinstance(item, dict) else getattr(item, 'max_offer_discount', None),
                    is_watchlisted=item.get('is_watchlisted') if isinstance(item, dict) else getattr(item, 'is_watchlisted', None),
                    watchers=item.get('watchers') if isinstance(item, dict) else getattr(item, 'watchers', None),
                    seller=item.get('seller') if isinstance(item, dict) else getattr(item, 'seller', None),
                    item=item.get('item') if isinstance(item, dict) else getattr(item, 'item', None),
                )
                for item in raw_data
            ]
            db.add_all(bronze_records)
            db.commit()
            
        self.log(f"Loaded {len(raw_data)} records into csfloat_listing_detail bronze table.")
        return raw_data

    def silver_transform(self):
        self.log("Transforming item listing detail data from bronze (not implemented yet)")
        # Implement transformation logic: Query CSFloatListingDetail -> Load into silver
        return {"status": "success"}

