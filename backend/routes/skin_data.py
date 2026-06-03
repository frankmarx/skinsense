from chalice import Response
from chalicelib.db import SessionLocal
from chalicelib.models.silver.item_master import ItemMaster

def get_item_master():
    """
    Endpoint to retrieve the list of items from the master table.
    """
    with SessionLocal() as db:
        items = db.query(ItemMaster).all()
        
        item_data = []
        for item in items:
            item_data.append({
                "item_id": item.item_id,
                "full_name": item.full_name,
                "item_type": item.item_type,
                "wear": item.wear,
                "stat_track": item.stat_track
            })
            
        return Response(
            body={"items": item_data},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
