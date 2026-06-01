from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader
from chalicelib.connectors.csfloat.client import test_connection

def run_item_listings(app, job_id):
    app.log.info(f"Starting price sync... job_id: {job_id}")
    loader = CSFloatListingLoader(jobid=job_id, datasource_id="1")
    raw_data = loader.extract()
    loader.bronze_load(raw_data)
    result = loader.silver_transform(raw_data)
    app.log.info(f"Sync Result: {result}")
    return result

def run_test_connection(app):
    app.log.info("Running CSFloat API connection test...")
    result = test_connection()
    app.log.info(f"Connection Test Result: {result}")
    return result
