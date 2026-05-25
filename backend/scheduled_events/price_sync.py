from backend.chalicelib.loaders.csfloat_loader import populate_csfloat_item_listings

def register_scheduled_events(app):
    @app.schedule('rate(12 hours)')
    def scheduled_price_sync(event):
        """
        AWS EventBridge trigger that runs every 12 hours.
        """
        app.log.info("Cron Trigger: Starting scheduled price sync...")
        result = populate_csfloat_item_listings()
        app.log.info(f"Cron Result: {result}")
        return result
