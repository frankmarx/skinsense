from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader

def register_scheduled_events(app):
    @app.schedule('rate(12 hours)')
    def sync_item_listings(event):
        """
        AWS EventBridge trigger that runs every 12 hours.
        """
        app.log.info("Cron Trigger: Starting scheduled price sync...")
        job_id = event.get('id', 'scheduled-sync')
        loader = CSFloatListingLoader(jobid=job_id, datasource_id="1")
        raw_data = loader.extract()
        loader.bronze_load(raw_data)
        result = loader.silver_transform()

        app.log.info(f"Cron Result: {result}")
        return result
