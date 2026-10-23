from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader
from chalicelib.connectors.csfloat.client import test_connection
import logging

logger = logging.getLogger('chalice')

def run_item_listings(event_logger):
    logger.info(f"Starting price sync... event: {event_logger.event_id}")
    loader = CSFloatListingLoader(datasource_id="1")

    with event_logger.job(action='Extracting Item Listings'):
        raw_data = loader.extract()

    with event_logger.job(action='Loading Bronze') as load_job_id:
        loader.bronze_load(raw_data, job_id=load_job_id)

    with event_logger.job(action='Transforming Silver'):
        result = loader.silver_transform(raw_data, job_id=load_job_id)

    logger.info(f"Sync Result: {result}")
    return result

def run_test_connection(event_logger):
    logger.info(f"Running CSFloat API connection test... event: {event_logger.event_id}")

    with event_logger.job(action='Testing Connection'):
        result = test_connection()
        if result.get("status") != "success":
            raise RuntimeError(f"Connection test failed: {result.get('message', result)}")

    logger.info(f"Connection Test Result: {result}")
    return result
