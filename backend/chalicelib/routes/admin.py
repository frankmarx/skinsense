import uuid
from chalice import Response
from chalicelib.orchestration.event_registry import enqueue_event
from chalicelib.orchestration.sqs_registry import EVENT_REGISTRY
from chalicelib.models import JobLogDetails
from chalicelib.db import SessionLocal

def trigger_sync_handler(app):
    data = app.current_request.json_body or {}
    event_type = data.get('event_type')

    if not event_type or event_type not in EVENT_REGISTRY:
        return Response(
            body={"status": "error", "message": f"Unknown event type: {event_type}", "valid_event_types": list(EVENT_REGISTRY.keys())},
            status_code=400,
            headers={"Content-Type": "application/json"}
        )

    event_id = enqueue_event(event_type, source='custom')
    return Response(
        body={"status": f"Event {event_type} queued", "event_id": event_id, "source": "custom"},
        status_code=202,
        headers={"Content-Type": "application/json"}
    )


def get_logs_handler():
    with SessionLocal() as db:
        logs = db.query(JobLogDetails).order_by(JobLogDetails.start_time.desc()).limit(100).all()

        log_data = []
        for log in logs:
            log_data.append({
                "id": log.id,
                "job_id": log.job_id,
                "event_id": log.event_id,
                "action": log.action,
                "status": log.status,
                "start_time": log.start_time.isoformat() if log.start_time else None,
                "end_time": log.end_time.isoformat() if log.end_time else None
            })

        return Response(
            body={"logs": log_data},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
