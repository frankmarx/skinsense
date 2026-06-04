from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader
from chalicelib.connectors.csfloat.client import test_connection
import logging

logger = logging.getLogger('chalice')

def run_sqs_consumer(job_id, job_logger):
    logger.info(f"Starting price sync... job_id: {job_id}")
    
    try:
        # Pass logger into loader
        loader = CSFloatListingLoader(jobid=job_id, datasource_id="1", logger=job_logger)
        raw_data = loader.extract()
        loader.bronze_load(raw_data)
        result = loader.silver_transform(raw_data)
        logger.info(f"Sync Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        raise e

def run_test_connection(job_id, job_logger):
    logger.info(f"Running CSFloat API connection test... job_id: {job_id}")
    job_logger.create_log_entry(status='Testing Connection')
    
    try:
        result = test_connection()
        logger.info(f"Connection Test Result: {result}")
        job_logger.update_log_entry(status='Testing Connection', success=True)
        return result
    except Exception as e:
        job_logger.update_log_entry(status='Testing Connection', success=False)
        raise e
