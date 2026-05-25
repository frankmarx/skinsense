from chalice import Chalice, CORSConfig
from dotenv import load_dotenv
import os
from chalicelib.db import init_db
from chalicelib.scheduled_events.csfloat_events import register_scheduled_events
from routes.admin import register_admin_routes

# Load .env from the backend directory and override existing environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

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
register_scheduled_events(app)
register_admin_routes(app)
