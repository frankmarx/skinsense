import uuid
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from chalicelib.models import ItemMaster

def get_or_create_item(db, full_name: str, item_type: str = None, wear: str = None, stat_track: bool = None):
    """
    Generic helper to retrieve an existing ItemMaster record or create a new one.
    Used for single-item operations.
    """
    item = db.query(ItemMaster).filter(
        ItemMaster.full_name == full_name,
    ).first()

    if not item:
        item = ItemMaster(
            item_id=str(uuid.uuid4()),
            full_name=full_name,
            item_type=item_type,
            wear=wear,
            stat_track=stat_track
        )
        db.add(item)
        db.flush()
        
    return item

def bulk_get_or_create_items(db, items_data: list[dict]):
    """
    High-efficiency helper to resolve a batch of items.
    
    :param items_data: List of dicts containing {'full_name': ..., 'item_type': ..., 'wear': ..., 'stat_track': ...}
    :return: A dictionary mapping {full_name: item_id}
    """
    all_names = {item['full_name'] for item in items_data}
    
    # 1. Bulk fetch existing items
    existing_items = db.execute(
        select(ItemMaster.full_name, ItemMaster.item_id)
        .filter(ItemMaster.full_name.in_(all_names))
    ).all()
    
    item_map = {name: item_id for name, item_id in existing_items}
    
    # 2. Identify and bulk insert missing items
    missing_items = [item for item in items_data if item['full_name'] not in item_map]
    
    if missing_items:
        new_records = []
        for item in missing_items:
            item_id = str(uuid.uuid4())
            item_map[item['full_name']] = item_id
            
            new_records.append({
                "item_id": item_id,
                "full_name": item['full_name'],
                "item_type": item.get('item_type'),
                "wear": item.get('wear'),
                "stat_track": item.get('stat_track')
            })
        
        db.execute(pg_insert(ItemMaster), new_records)
        db.flush()
        
    return item_map
