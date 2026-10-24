from chalicelib.connectors.skinport.client import get_sales_history, test_connection
import logging

logger = logging.getLogger('chalice')

def run_sales_history(event_logger):
    logger.info(f"Fetching SkinPort sales history... event: {event_logger.event_id}")

    with event_logger.job(action='Fetching Sales History'):
        history = get_sales_history()

    logger.info(f"Sales History Result: fetched {len(history)} items")
    return {"status": "success", "processed_items": len(history)}


def run_test_connection(event_logger):
    logger.info(f"Running SkinPort API connection test... event: {event_logger.event_id}")

    with event_logger.job(action='Testing SkinPort Connection'):
        result = test_connection()
        if result.get("status") != "success":
            raise RuntimeError(f"Connection test failed: {result.get('message', result)}")

    logger.info(f"Connection Test Result: {result}")
    return result
