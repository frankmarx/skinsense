import boto3
import json
import os

sqs = boto3.client('sqs')

def send_to_queue(queue_url, message_body):
    """Sends a message to an SQS queue."""
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )
