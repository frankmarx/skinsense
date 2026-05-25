from chalice import Response
from chalicelib.loaders.csfloat.load_item_listings import CSFloatListingLoader

def register_admin_routes(app):
    @app.route('/sync', methods=['GET'], cors=True)
    def trigger_sync():
        """
        Manual trigger endpoint for local testing.
        Visit http://localhost:8000/sync to run the population logic.
        """
        app.log.info("Manual trigger: Syncing CSFloat data...")
        loader = CSFloatListingLoader(jobid="manual-sync", datasource_id="1")
        raw_data = loader.extract()
        loader.bronze_load(raw_data)
        result = loader.silver_transform()

        return Response(
            body={"status": "Manual Sync Triggered", "result": result},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
