import os
import json
from chalicelib.orchestration.csfloat_events import run_sync_item_listings
from chalicelib.orchestration.sqs_helper import send_to_queue

def register_events(app):
    # CSFloat
    @app.schedule('rate(12 hours)')
    def sync_item_listings(event):
        """
        AWS EventBridge trigger that runs every 12 hours.
        """
        queue_url = os.environ.get('SQS_QUEUE_URL')
        send_to_queue(queue_url, {'action': 'sync_item_listings', 'job_id': 'scheduled-sync'})
        return {'status': 'queued'}

    @app.on_sqs_message(queue=os.environ.get('SQS_QUEUE_NAME'), batch_size=1)
    def handle_sqs_message(event):
        for record in event:
            message = json.loads(record.body)
            if message['action'] == 'sync_item_listings':
                run_sync_item_listings(app, message.get('job_id', 'queued-sync'))
