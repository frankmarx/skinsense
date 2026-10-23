import pytest
from unittest.mock import patch
from sqlalchemy import select
from chalicelib.orchestration.sqs_registry import EVENT_REGISTRY
from chalicelib.orchestration.logging import EventLogger
from chalicelib.connectors.csfloat.schemas import Listing
from chalicelib.db import get_db
from chalicelib.models import (
    ItemMaster,
    ItemDayListing,
    Datasource,
    CSFloatListing,
    JobLogDetails,
    EventLogDetails,
)

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


def test_event_cs_float_item_listings(db_session):
    """
    Tests the full cs_float_item_listings event: event creation, job logging,
    and the extract -> bronze load -> silver transform pipeline.
    """
    ds = db_session.query(Datasource).filter(Datasource.datasource_id == "1").first()
    if not ds:
        db_session.add(Datasource(datasource_id="1", name="CSFloat", url="https://csfloat.com"))
        db_session.commit()

    EVENT_TYPE = 'cs_float_item_listings'

    handler = EVENT_REGISTRY[EVENT_TYPE]
    event_logger = EventLogger(event_type=EVENT_TYPE, source='test')
    event_logger.create_event()

    with patch(
        'chalicelib.loaders.csfloat.load_item_listings.get_item_listings',
        return_value=SAMPLE_LISTINGS,
    ):
        result = handler(event_logger)

    assert result["status"] == "success"
    assert result["processed_items"] == 2

    event = db_session.query(EventLogDetails).filter(
        EventLogDetails.event_id == event_logger.event_id
    ).one()
    assert event.source == 'test'
    assert event.event_type == EVENT_TYPE
    assert event.start_time is not None

    jobs = db_session.query(JobLogDetails).filter(
        JobLogDetails.event_id == event_logger.event_id
    ).order_by(JobLogDetails.start_time, JobLogDetails.id).all()
    assert [job.action for job in jobs] == [
        'Extracting Item Listings',
        'Loading Bronze',
        'Transforming Silver',
    ]
    assert all(job.status == 'Completed' for job in jobs)
    assert all(job.end_time is not None for job in jobs)

    bronze_records = db_session.query(CSFloatListing).filter(
        CSFloatListing.job_id == jobs[1].job_id
    ).all()
    assert len(bronze_records) == 2

    items = db_session.execute(select(ItemMaster)).scalars().all()
    item_names = {item.full_name for item in items}
    assert "AK-47 | Redline (Field-Tested)" in item_names
    assert "AWP | Asiimov (Field-Tested)" in item_names

    listings = db_session.query(ItemDayListing).filter(
        ItemDayListing.datasource_id == "1"
    ).all()
    assert len(listings) >= 2


def test_event_cs_float_test_connection(db_session):
    """
    Tests the cs_float_test_connection event against the live CSFloat API:
    event creation, job logging, and a real connection check.
    Requires CSFLOAT_API_KEY to be set in the environment.
    """
    handler = EVENT_REGISTRY['cs_float_test_connection']
    event_logger = EventLogger(event_type='cs_float_test_connection', source='test')
    event_logger.create_event()

    result = handler(event_logger)

    assert result["status"] == "success"

    event = db_session.query(EventLogDetails).filter(
        EventLogDetails.event_id == event_logger.event_id
    ).one()
    assert event.source == 'test'
    assert event.event_type == 'cs_float_test_connection'
    assert event.start_time is not None

    jobs = db_session.query(JobLogDetails).filter(
        JobLogDetails.event_id == event_logger.event_id
    ).all()
    assert len(jobs) == 1
    assert jobs[0].action == 'Testing Connection'
    assert jobs[0].status == 'Completed'
    assert jobs[0].end_time is not None

