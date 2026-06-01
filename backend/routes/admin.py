import os
import uuid
from chalice import Response
from chalicelib.orchestration.sqs_registry import send_to_queue
from chalicelib.models import JobLogDetails
from chalicelib.db import SessionLocal

def register_admin_routes(app):
    @app.route('/events/sync', methods=['POST'], cors=True)
    def trigger_sync():
        """
        Manual trigger endpoint to queue the population logic.
        """
        action = 'sync_item_listings'
        send_to_queue({
            'action': action, 
            'job_details': {
                'job_id': f"{action}-manual-{uuid.uuid4()}",
                'event_name': action
            }
        })
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
            logs = db.query(JobLogDetails).order_by(JobLogDetails.job_start_time.desc()).limit(100).all()
            
            log_data = []
            for log in logs:
                log_data.append({
                    "id": log.id,
                    "job_id": log.job_id,
                    "data_source_id": log.data_source_id,
                    "event_name": log.event_name,
                    "status": log.status,
                    "job_start_time": log.job_start_time.isoformat() if log.job_start_time else None,
                    "job_end_time": log.job_end_time.isoformat() if log.job_end_time else None
                })
            
            return Response(
                body={"logs": log_data},
                status_code=200,
                headers={"Content-Type": "application/json"}
            )

