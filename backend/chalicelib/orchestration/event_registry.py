import os
import json
import uuid
from datetime import datetime
from chalicelib.db import SessionLocal
from chalicelib.models.common.event_log_details import EventLogDetails
from chalicelib.orchestration.sqs_registry import send_to_queue

# Grouping jobs by frequency
SCHEDULE_GROUPS = {
    'twice_daily': ['cs_float_item_listings'],
}

def register_events(app):
    # Scheduled Orchestrators
    @app.schedule('rate(12 hours)')
    def master_scheduler_twice_daily(event):
        """
        AWS EventBridge trigger that runs every 12 hours.
        """
        trigger_event(event, 'twice_daily', "Added twice-daily events to the queue.")
        return {'status': 'orchestrated', 'group': 'twice_daily'}

def trigger_event(event, group_name, action_desc):
    # EventBridge 'id' is in the top-level of the event object
    event_id = event.get('id', str(uuid.uuid4()))
    start_time = datetime.now()
    
    # Log to DB
    with SessionLocal() as db:
        log = EventLogDetails(
            job_id=event_id,
            action=action_desc,
            start_time=start_time,
            end_time=datetime.now()
        )
        db.add(log)
        db.commit()
    
    trigger_jobs(group_name, event_id)

def trigger_jobs(group_name, event_id):
    jobs = SCHEDULE_GROUPS.get(group_name, [])
    for action in jobs:
        job_id = uuid.uuid4()
        send_to_queue({
            'action': action, 
            'job_details': {
                'job_id': event_id,
                'event_name': action
            }
        })



