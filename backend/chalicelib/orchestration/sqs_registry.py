import datetime
import boto3
import json
import os
import uuid
from chalicelib.event_definition.csfloat_events import run_sync_item_listings, run_test_connection
from chalicelib.orchestration.logging import JobDetailLogger

# Command Registry for the SQS Consumer
COMMAND_REGISTRY = {
    'cs_float_item_listings': {
        'function': run_sync_item_listings,
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

def register_sqs_queue(app):
        # SQS Consumer
    @app.on_sqs_message(queue=os.environ.get('SQS_QUEUE_NAME'), batch_size=1)
    def handle_sqs_message(event):
        for record in event:
            message = json.loads(record.body)
            event_name = message.get('action')
            event_id = message.get('event_id')
            
            # For logging purposes, we still need a job_id. 
            # We will use event_id if no specific job_id is present, 
            # or generate one here to maintain the JobDetailLogger interface.
            job_id = event_id if event_id else str(uuid.uuid4())
            
            event_cfg = COMMAND_REGISTRY.get(event_name)

            
            event_cfg = COMMAND_REGISTRY.get(event_name)
            handler = event_cfg.get('function') if event_cfg else None
            data_source_id = event_cfg.get('data_source_id') if event_cfg else 'unknown'
            
            if handler:
                app.log.info(f"Executing job: {event_name} with ID: {job_id}")
                
                # Use JobDetailLogger
                logger = JobDetailLogger(job_id=job_id, data_source_id=data_source_id, event_name=event_name)
                
                try:
                    # Pass the logger to the handler
                    handler(app, job_id, logger)
                except Exception as e:
                    app.log.error(f"Job {job_id} failed: {e}")
            else:

                app.log.error(f"No handler found for action: {event_name}")

def send_to_queue(message_body, queue_url=None):
    """Sends a message to an SQS queue."""
    url = queue_url or QUEUE_URL
    if not url:
        raise ValueError("SQS_QUEUE_URL is not set.")
        
    sqs.send_message(
        QueueUrl=url,
        MessageBody=json.dumps(message_body)
    )
