import os
import json
import boto3
from functools import lru_cache
from botocore.exceptions import ClientError

SECRET_NAME = "skinsense/production/config"

@lru_cache(maxsize=1)
def get_secrets():
    region_name = os.environ.get('AWS_REGION', 'us-east-1')

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(SecretId=SECRET_NAME)
    except ClientError as e:
        print(f"Error fetching secrets: {e}")
        raise e

    return json.loads(response['SecretString'])

def get_db_url():
    return os.environ.get('DB_URL') or get_secrets().get('DB_URL')

def get_cognito_client_id():
    return os.environ.get('COGNITO_CLIENT_ID') or get_secrets().get('COGNITO_CLIENT_ID')

def get_cognito_user_pool_id():
    return os.environ.get('COGNITO_USER_POOL_ID') or get_secrets().get('COGNITO_USER_POOL_ID')

def get_csfloat_api_key():
    return os.environ.get('CSFLOAT_API_KEY') or get_secrets().get('CSFLOAT_API_KEY')

def get_sqs_queue_url():
    return os.environ.get('SQS_QUEUE_URL')

def get_sqs_queue_name():
    return os.environ.get('SQS_QUEUE_NAME')
