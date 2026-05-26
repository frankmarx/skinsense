import pytest
from unittest.mock import patch, MagicMock
from chalicelib.events.csfloat_events import run_sync_item_listings
from chalicelib.connectors.csfloat import client as csfloat_client
from chalicelib.connectors.csfloat.schemas import Listing
from sqlalchemy import select
from chalicelib.db import get_db
from chalicelib.models import ItemMaster, ItemDayListing, Datasource

# --- SAMPLE DATA ---
SAMPLE_LISTINGS = [
    Listing(market_hash_name="AK-47 | Redline (Field-Tested)", price=1250.0, quantity=142),
    Listing(market_hash_name="AWP | Asiimov (Field-Tested)", price=6500.0, quantity=48),
]

@pytest.fixture
def db_session():
    """Provides a database session."""
    with get_db() as session:
        yield session

@pytest.fixture
def mock_app():
    """Provides a mock app object with a log method."""
    app = MagicMock()
    app.log = MagicMock()
    return app

def test_run_sync_item_listings_success(mock_app, db_session):
    """
    Tests that run_sync_item_listings successfully extracts, 
    loads into bronze, and transforms into silver.
    """
    # Patch the CSFloat client to return sample listings
    with patch('chalicelib.loaders.csfloat.load_item_listings.get_item_listings', return_value=SAMPLE_LISTINGS):
        # Setup: Ensure the datasource exists
        ds = Datasource(datasource_id="1", name="CSFloat", url="https://csfloat.com")
        db_session.add(ds)
        db_session.commit()
        
        job_id = "test-job-123"
        result = run_sync_item_listings(mock_app, job_id)
        
        # Verify result
        assert result["status"] == "success"
        assert result["processed_items"] == 2
        
        # Verify that logs were called
        mock_app.log.info.assert_any_call(f"Starting price sync... job_id: {job_id}")
        
        # Verify database state
        # 1. Check ItemMaster
        items = db_session.execute(select(ItemMaster)).scalars().all()
        assert len(items) == 2
        item_names = {item.full_name for item in items}
        assert "AK-47 | Redline (Field-Tested)" in item_names
        assert "AWP | Asiimov (Field-Tested)" in item_names
        
        # 2. Check ItemDayListing
        listings = db_session.execute(select(ItemDayListing)).scalars().all()
        assert len(listings) == 2

def test_public_api_access():
    """
    Integration test to ensure the CSFloat public API is accessible.
    Requires CSFLOAT_API_KEY to be set in the environment.
    """
    try:
        listings = csfloat_client.get_item_listings()
        # We don't assert on content since the API is live, 
        # just that it doesn't raise an exception and returns a list.
        assert isinstance(listings, list)
    except ValueError as e:
        pytest.fail(f"API Key missing or invalid: {e}")
    except Exception as e:
        pytest.fail(f"API request failed: {e}")
