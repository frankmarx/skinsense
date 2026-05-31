from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader

def run_sync_item_listings(app, job_id):
    app.log.info(f"Starting price sync... job_id: {job_id}")
    loader = CSFloatListingLoader(jobid=job_id, datasource_id="1")
    raw_data = loader.extract()
    loader.bronze_load(raw_data)
    result = loader.silver_transform(raw_data)
    app.log.info(f"Sync Result: {result}")
    return result

def register_events(app):
    @app.schedule('rate(12 hours)')
    def sync_item_listings(event):
        """
        AWS EventBridge trigger that runs every 12 hours.
        """
        return run_sync_item_listings(app, event.get('id', 'scheduled-sync'))
