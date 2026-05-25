from chalice import Response
from backend.chalicelib.loaders.csfloat_loader import populate_csfloat_item_listings

def register_admin_routes(app):
    @app.route('/sync', methods=['GET'], cors=True)
    def trigger_sync():
        """
        Manual trigger endpoint for local testing.
        Visit http://localhost:8000/sync to run the population logic.
        """
        app.log.info("Manual trigger: Syncing CSFloat data...")
        result = populate_csfloat_item_listings()
        return Response(
            body={"status": "Manual Sync Triggered", "result": result},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
