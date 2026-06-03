from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader
from chalicelib.connectors.csfloat.client import test_connection

def run_sqs_consumer(app, job_id, logger):
    app.log.info(f"Starting price sync... job_id: {job_id}")
    
    try:
        # Pass logger into loader
        loader = CSFloatListingLoader(jobid=job_id, datasource_id="1", logger=logger)
        raw_data = loader.extract()
        loader.bronze_load(raw_data)
        result = loader.silver_transform(raw_data)
        app.log.info(f"Sync Result: {result}")
        return result
    except Exception as e:
        app.log.error(f"Job {job_id} failed: {e}")
        raise e

def run_test_connection(app, job_id, logger):
    app.log.info(f"Running CSFloat API connection test... job_id: {job_id}")
    logger.create_log_entry(status='Testing Connection')
    
    try:
        result = test_connection()
        app.log.info(f"Connection Test Result: {result}")
        logger.update_log_entry(status='Testing Connection', success=True)
        return result
    except Exception as e:
        logger.update_log_entry(status='Testing Connection', success=False)
        raise e
