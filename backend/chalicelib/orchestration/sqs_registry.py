import boto3
import json
import logging
from chalicelib.utils.config import get_sqs_queue_url
from chalicelib.event_definition.csfloat_events import run_item_listings, run_test_connection
from chalicelib.orchestration.logging import EventLogger

logger = logging.getLogger('chalice')

# Event Registry for the SQS Consumer
EVENT_REGISTRY = {
    'cs_float_item_listings': run_item_listings,
    'cs_float_test_connection': run_test_connection,
}

# Default queue configuration
QUEUE_URL = get_sqs_queue_url()

sqs = boto3.client('sqs')

def sqs_consumer_logic(event):
    for record in event:
        message = json.loads(record.body)
        event_type = message.get('event_type')
        event_id = message.get('event_id')
        source = message.get('source', 'scheduled')

        handler = EVENT_REGISTRY.get(event_type)

        if not handler:
            logger.error(f"No handler found for event type: {event_type}")
            continue

        try:
            event_logger = EventLogger(event_id=event_id)
        except ValueError as e:
            logger.error(f"Dropping event {event_id} ({event_type}): {e}")
            continue

        logger.info(f"Executing job for event: {event_type} ({source}, event_id: {event_id})")

        try:
            handler(event_logger)
        except Exception as e:
            logger.error(f"Job for event {event_id} failed: {e}")

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
