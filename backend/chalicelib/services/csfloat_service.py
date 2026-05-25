import uuid
from datetime import date
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from chalicelib.db import get_db
from chalicelib.models import ItemMaster, ItemDaySales, ItemDayListing
from csfloat.client import get_item_listings
from csfloat.schemas import Listing
from chalicelib.helpers.csfloat_helpers import parse_market_hash_name
from chalicelib.helpers.generic_helpers import bulk_get_or_create_items

def populate_csfloat_item_listings():
    """
    High-efficiency orchestration function to fetch CSFloat listings and update the DB.
    Uses bulk operations to minimize database roundtrips.
    """
    # 1. Fetch data from CSFloat
    listings: list[Listing] = get_item_listings()
    if not listings:
        return {"status": "error", "message": "No listings retrieved from CSFloat"}

    datasource_id = "1" 
    today = date.today()
    
    # Prepare data for the bulk helper
    items_to_resolve = []
    for listing in listings:
        gun, skin, wear, stattrack = parse_market_hash_name(listing.market_hash_name)
        items_to_resolve.append({
            "full_name": listing.market_hash_name,
            "item_type": gun,
            "wear": wear,
            "stat_track": stattrack
        })

    with get_db() as db:
        # --- STEP 1: Bulk Resolve Item IDs using the generic helper ---
        item_map = bulk_get_or_create_items(
            db=db, 
            datasource_id=datasource_id, 
            items_data=items_to_resolve
        )

        # --- STEP 2: Prepare Bulk Metrics Data ---
        listing_values = []
        sales_values = []

        for listing in listings:
            item_id = item_map.get(listing.market_hash_name)
            if not item_id: continue

            listing_values.append({
                "item_id": item_id,
                "datasource_id": datasource_id,
                "day": today,
                "listings_count": listing.quantity,
                "min_price": listing.price
            })

            sales_values.append({
                "item_id": item_id,
                "datasource_id": datasource_id,
                "day": today,
                "units_sold": 0, 
                "min_price": listing.price
            })

        # --- STEP 3: Bulk Upsert Metrics ---
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

        if sales_values:
            sales_stmt = pg_insert(ItemDaySales).values(sales_values)
            upsert_sales = sales_stmt.on_conflict_do_update(
                index_elements=['item_id', 'datasource_id', 'day'],
                set_={
                    "units_sold": sales_stmt.excluded.units_sold,
                    "min_price": sales_stmt.excluded.min_price
                }
            )
            db.execute(upsert_sales)

        db.commit()

    return {"status": "success", "processed_items": len(listings)}


