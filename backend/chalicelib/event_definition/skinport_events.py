from chalicelib.connectors.skinport.client import get_sales_history
import logging

logger = logging.getLogger('chalice')

def run_sales_history(event_logger):
    logger.info(f"Fetching SkinPort sales history... event: {event_logger.event_id}")

    with event_logger.job(action='Fetching Sales History'):
        history = get_sales_history()

    logger.info(f"Sales History Result: fetched {len(history)} items")
    return {"status": "success", "processed_items": len(history)}
