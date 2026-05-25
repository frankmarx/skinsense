import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from sqlalchemy import select
from chalicelib.db import get_db
from chalicelib.models import ItemMaster, ItemDayListing
from backend.chalicelib.loaders.csfloat_loader import populate_csfloat_item_listings
from csfloat.schemas import Listing

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

def test_populate_new_items(db_session):
    """
    Scenario 1: Database is empty.
    Expectation: ItemMaster records are created and metrics are inserted.
    """
    # Mock the API call to return our sample data
    with patch('chalicelib.services.csfloat_service.get_item_listings', return_value=SAMPLE_LISTINGS):
        result = populate_csfloat_item_listings()
        
        assert result["status"] == "success"
        assert result["processed_items"] == 2

        # Verify ItemMaster was populated
        items = db_session.execute(select(ItemMaster)).scalars().all()
        assert len(items) >= 2
        
        # Verify metrics were populated for today
        listings = db_session.execute(select(ItemDayListing)).scalars().all()
        assert len(listings) >= 2

def test_populate_existing_items(db_session):
    """
    Scenario 2: Items already exist in ItemMaster.
    Expectation: No new ItemMaster records created, only metrics updated.
    """
    # 1. Setup: Pre-populate ItemMaster
    for l in SAMPLE_LISTINGS:
        item = ItemMaster(
            item_id="test-id-" + l.market_hash_name,
            datasource_id="1",
            full_name=l.market_hash_name,
            item_type="Gun",
            wear="FT",
            stat_track=False
        )
        db_session.add(item)
    db_session.commit()
    
    initial_item_count = db_session.query(ItemMaster).count()

    # 2. Run the population logic with mocked API
    with patch('chalicelib.services.csfloat_service.get_item_listings', return_value=SAMPLE_LISTINGS):
        result = populate_csfloat_item_listings()
        
        assert result["status"] == "success"
        
        # 3. Verify: ItemMaster count should NOT have increased
        final_item_count = db_session.query(ItemMaster).count()
        assert final_item_count == initial_item_count, "ItemMaster should not have duplicate entries"
        
        # Verify metrics still exist
        listings = db_session.execute(select(ItemDayListing)).scalars().all()
        assert len(listings) >= 2
