import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chalice import Chalice, CORSConfig
from dotenv import load_dotenv
import os

# 1. Load .env immediately
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

# 2. Now import everything else that depends on DB
from chalicelib.db import init_db
from chalicelib.orchestration.event_registry import register_events
from chalicelib.orchestration.sqs_registry import register_sqs_queue
from chalicelib.routes.route_registry import register_all_routes

app = Chalice(app_name='skinsense-backend')

# Apply CORS config to allow frontend access
app.api.cors = CORSConfig(
    allow_origin='*', 
    allow_headers=['Content-Type', 'Authorization'],
    allow_credentials=True
)

# Initialize database tables
init_db()

# Register schedules and queues
register_events(app)

from chalicelib.utils.config import get_sqs_queue_name
from chalicelib.orchestration.sqs_registry import sqs_consumer_logic

@app.on_sqs_message(queue=get_sqs_queue_name(), batch_size=1, name='sqs-consumer')
def sqs_consumer(event):
    return sqs_consumer_logic(event)

# Register all routes
register_all_routes(app)
