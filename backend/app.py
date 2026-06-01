from chalice import Chalice, CORSConfig
from dotenv import load_dotenv
import os

# 1. Load .env immediately
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

# 2. Now import everything else that depends on DB
from chalicelib.orchestration.sqs_registry import register_sqs_queue
from chalicelib.db import init_db
from chalicelib.orchestration.event_registry import register_events
from routes.admin import register_admin_routes

app = Chalice(app_name='skinsense-backend')

# Apply CORS config to allow frontend access
app.api.cors = CORSConfig(
    allow_origin='*', 
    allow_headers=['Content-Type', 'Authorization'],
    allow_credentials=True
)

# Initialize database tables
init_db()

# Register schedules and routes
register_events(app)
register_sqs_queue(app)
register_admin_routes(app)
