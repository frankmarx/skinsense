from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader
from chalicelib.connectors.csfloat.client import test_connection
import logging

logger = logging.getLogger('chalice')

def run_item_listings(event_logger):
    logger.info(f"Starting price sync... event: {event_logger.event_id}")
    job_id = event_logger.create_job(action='Syncing Item Listings')

    try:
        loader = CSFloatListingLoader(jobid=job_id, datasource_id="1")
        raw_data = loader.extract()
        loader.bronze_load(raw_data)
        result = loader.silver_transform(raw_data)
        logger.info(f"Sync Result: {result}")
        event_logger.finish_job(job_id, success=True)
        return result
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        event_logger.finish_job(job_id, success=False)
        raise e

def run_test_connection(event_logger):
    logger.info(f"Running CSFloat API connection test... event: {event_logger.event_id}")
    job_id = event_logger.create_job(action='Testing Connection')

    try:
        result = test_connection()
        logger.info(f"Connection Test Result: {result}")
        event_logger.finish_job(job_id, success=True)
        return result
    except Exception as e:
        event_logger.finish_job(job_id, success=False)
        raise e
