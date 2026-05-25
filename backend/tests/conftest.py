import pytest
from dotenv import load_dotenv
import os

# Load test-specific variables before the app loads
# This ensures DATABASE_URL is set before chalicelib.db is imported
env_path = os.path.join(os.path.dirname(__file__), '.env.test')
load_dotenv(env_path, override=True)

from sqlalchemy import text
from chalicelib.db import init_db, engine
from chalicelib.models import Base

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables in the test database once."""
    init_db()

@pytest.fixture(autouse=True)
def cleanup_database():
    """Truncate all tables after each individual test."""
    yield  # Test runs here
    
    with engine.connect() as conn:
        # Disable foreign key checks for truncation if necessary,
        # or use CASCADE to handle dependencies.
        # Note: Depending on your exact DB driver and version, 
        # TRUNCATE might behave slightly differently.
        for table in reversed(Base.metadata.sorted_tables):
            # Using 'CASCADE' ensures dependent records are deleted
            conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;"))
        conn.commit()
