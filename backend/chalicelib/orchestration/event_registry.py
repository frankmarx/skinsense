import os
import json
import uuid
import os
import json
import uuid
from datetime import datetime
from chalicelib.db import SessionLocal
from chalicelib.orchestration.logging import EventDetailLogger
from chalicelib.orchestration.sqs_registry import send_to_queue

# Grouping jobs by frequency
SCHEDULE_GROUPS = {
    'once_daily': ['cs_float_test_connection'],
    'twice_daily': ['cs_float_item_listings'],
}

def register_events(app):
    # Scheduled Orchestrators
    @app.schedule('rate(12 hours)')
    # def master_scheduler_twice_daily(event):
    #     """
    #     AWS EventBridge trigger that runs every 12 hours.
    #     """
    #     trigger_event(event, 'twice_daily', "Added twice-daily events to the queue.")
    #     return {'status': 'orchestrated', 'group': 'twice_daily'}
    # @app.schedule('rate(24 hours)')

    def master_scheduler_once_daily(event):
        """
        AWS EventBridge trigger that runs every 24 hours.
        """
        trigger_event(event, 'once_daily', "Added once-daily events to the queue.")
        return {'status': 'orchestrated', 'group': 'once_daily'}

def trigger_event(event, group_name, action_desc):
    # EventBridge 'id' is in the top-level of the event object
    event_id = event.get('id', str(uuid.uuid4()))
    
    # Use EventDetailLogger
    logger = EventDetailLogger(action=action_desc, job_id=event_id)
    logger.create_log_entry()
    
    trigger_jobs(group_name, event_id)

def trigger_jobs(group_name, event_id):
    jobs = SCHEDULE_GROUPS.get(group_name, [])
    for event in jobs:
        send_to_queue({
            'event': event,
            'event_id': event_id
        })



