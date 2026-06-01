import boto3
import json
import os
from chalicelib.event_definition.csfloat_events import run_sync_item_listings

# Command Registry for the SQS Consumer
COMMAND_REGISTRY = {
    'cs_float_item_listings': run_sync_item_listings,
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
            action = message.get('action')
            details = message.get('job_details', {})
            
            handler = COMMAND_REGISTRY.get(action)
            if handler:
                job_id = details.get('job_id')
                app.log.info(f"Executing job: {action} with ID: {job_id}")
                # Log entry for job_log_details
                from chalicelib.db import SessionLocal
                from chalicelib.models.common.job_log_details import JobLogDetails
                
                with SessionLocal() as db:
                    log = JobLogDetails(
                        job_id=job_id,
                        data_source_id=details.get('data_source_id', '1'),
                        event_name=action,
                        status='IN_PROGRESS'
                    )
                    db.add(log)
                    db.commit()

                handler(app, job_id)
            else:
                app.log.error(f"No handler found for action: {action}")

def send_to_queue(message_body, queue_url=None):
    """Sends a message to an SQS queue."""
    url = queue_url or QUEUE_URL
    if not url:
        raise ValueError("SQS_QUEUE_URL is not set.")
        
    sqs.send_message(
        QueueUrl=url,
        MessageBody=json.dumps(message_body)
    )
