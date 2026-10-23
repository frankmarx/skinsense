import os
import json
import uuid
from chalicelib.orchestration.logging import EventLogger
from chalicelib.orchestration.sqs_registry import send_to_queue

# Grouping events by frequency
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
    #     trigger_events('twice_daily')
    #     return {'status': 'orchestrated', 'group': 'twice_daily'}
    # @app.schedule('rate(24 hours)')

    def master_scheduler_once_daily(event):
        """
        AWS EventBridge trigger that runs every 24 hours.
        """
        trigger_events('once_daily')
        return {'status': 'orchestrated', 'group': 'once_daily'}

def trigger_events(group_name):
    for event_type in SCHEDULE_GROUPS.get(group_name, []):
        enqueue_event(event_type, source='scheduled')

def enqueue_event(event_type, source):
    event_logger = EventLogger(event_type=event_type, source=source)
    event_logger.create_event()
    send_to_queue({
        'event_type': event_type,
        'event_id': event_logger.event_id,
        'source': source
    })
    return event_logger.event_id
