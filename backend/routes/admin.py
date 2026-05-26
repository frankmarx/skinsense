from chalice import Response
from chalicelib.events.csfloat_events import run_sync_item_listings
from chalicelib.models.common.feed_loader_log import FeedLoaderLog
from chalicelib.db import SessionLocal

def register_admin_routes(app):
    @app.route('/events/sync', methods=['POST'], cors=True)
    def trigger_sync():
        """
        Manual trigger endpoint to run the population logic.
        """
        result = run_sync_item_listings(app, "manual-sync")
        return Response(
            body={"status": "Manual Sync Triggered", "result": result},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )

    @app.route('/logs', methods=['GET'], cors=True)
    def get_logs():
        """
        Endpoint to retrieve the last 100 logs.
        """
        with SessionLocal() as db:
            logs = db.query(FeedLoaderLog).order_by(FeedLoaderLog.time_logged.desc()).limit(100).all()
            
            log_data = []
            for log in logs:
                log_data.append({
                    "id": log.id,
                    "jobid": log.jobid,
                    "datasource_id": log.datasource_id,
                    "feed_name": log.feed_name,
                    "action": log.action,
                    "time_logged": log.time_logged.isoformat()
                })
            
            return Response(
                body={"logs": log_data},
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
