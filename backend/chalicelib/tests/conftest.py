import os
import pytest
from dotenv import load_dotenv

# Load base .env first, then .env.test with override so test-specific
# values (e.g. DB_URL pointing to a test DB branch) take precedence.
base_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(base_dir, '..', '.env'))
load_dotenv(os.path.join(base_dir, '.env.test'), override=True)

from chalicelib.db import get_db


@pytest.fixture
def db_session():
    """Provides a database session."""
    with get_db() as session:
        yield session
