import uuid
from chalice import Response
from chalicelib.orchestration.sqs_registry import send_to_queue
from chalicelib.models import JobLogDetails
from chalicelib.db import SessionLocal

def trigger_sync_logic(action='cs_float_item_listings'):
    # Generate a unique event_id since it is a manual trigger
    event_id = str(uuid.uuid4())
    send_to_queue({
        'action': action, 
        'event_id': event_id
    })
    return Response(
        body={"status": f"Manual {action} Queued", "event_id": event_id},
        status_code=202,
        headers={"Content-Type": "application/json"}
    )


def get_logs_logic():
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
