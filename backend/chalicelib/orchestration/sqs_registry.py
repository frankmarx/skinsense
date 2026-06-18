import datetime
import boto3
import json
import os
import uuid
import logging
from chalicelib.event_definition.csfloat_events import run_sqs_consumer, run_test_connection
from chalicelib.orchestration.logging import JobDetailLogger

logger = logging.getLogger('chalice')

# Command Registry for the SQS Consumer
COMMAND_REGISTRY = {
    'cs_float_item_listings': {
        'function': run_sqs_consumer,
        'data_source_id': '1'
    },
    'cs_float_test_connection': {
        'function': run_test_connection,
        'data_source_id': '1'
    }
}
# Default queue configuration
QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

sqs = boto3.client('sqs')

def sqs_consumer_logic(event):
    for record in event:
        message = json.loads(record.body)
        event_name = message.get('event')
        event_id = message.get('event_id')
        
        # For logging purposes, we still need a job_id. 
        # We will use event_id if no specific job_id is present, 
        # or generate one here to maintain the JobDetailLogger interface.
        job_id = event_id if event_id else str(uuid.uuid4())
        
        event_cfg = COMMAND_REGISTRY.get(event_name)
        handler = event_cfg.get('function') if event_cfg else None
        data_source_id = event_cfg.get('data_source_id') if event_cfg else 'unknown'
        
        if handler:
            logger.info(f"Executing job: {event_name} with ID: {job_id}")
            
            # Use JobDetailLogger
            job_logger = JobDetailLogger(job_id=job_id, data_source_id=data_source_id, event_name=event_name)
            
            try:
                # Pass the logger to the handler
                handler(job_id, job_logger)
            except Exception as e:
                logger.error(f"Job {job_id} failed: {e}")
        else:
            logger.error(f"No handler found for action: {event_name}")

def register_sqs_queue(app):
    # Registration now handled in app.py
    pass

def send_to_queue(message_body, queue_url=None):

    """Sends a message to an SQS queue."""
    url = queue_url or QUEUE_URL
    print(f"DEBUG: SQS QueueUrl being used: {url}")
    if not url:
        raise ValueError("SQS_QUEUE_URL is not set.")
        
    sqs.send_message(
        QueueUrl=url,
        MessageBody=json.dumps(message_body)
    )
