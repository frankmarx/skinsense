import os
from chalice import Response
from chalicelib.orchestration.sqs_helper import send_to_queue
from chalicelib.models.common.feed_loader_log import FeedLoaderLog
from chalicelib.db import SessionLocal

def register_admin_routes(app):
    @app.route('/events/sync', methods=['POST'], cors=True)
    def trigger_sync():
        """
        Manual trigger endpoint to queue the population logic.
        """
        queue_url = os.environ.get('SQS_QUEUE_URL')
        send_to_queue(queue_url, {'action': 'sync_item_listings', 'job_id': 'manual-sync'})
        return Response(
            body={"status": "Manual Sync Queued"},
            status_code=202,
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
