import pytest
from chalicelib.orchestration.sqs_registry import EVENT_REGISTRY
from chalicelib.orchestration.logging import EventLogger
from chalicelib.db import get_db
from chalicelib.models import JobLogDetails, EventLogDetails


@pytest.fixture
def db_session():
    """Provides a database session."""
    with get_db() as session:
        yield session


def test_event_skinport_sales_history(db_session):
    """
    Tests the skinport_sales_history event against the live SkinPort API:
    event creation, job logging, and a real sales history fetch.
    No API key required (public endpoint, rate limited to 8 requests / 5 min).
    """
    handler = EVENT_REGISTRY['skinport_sales_history']
    event_logger = EventLogger(event_type='skinport_sales_history', source='test')
    event_logger.create_event()

    result = handler(event_logger)

    assert result["status"] == "success"
    assert result["processed_items"] > 0

    event = db_session.query(EventLogDetails).filter(
        EventLogDetails.event_id == event_logger.event_id
    ).one()
    assert event.source == 'test'
    assert event.event_type == 'skinport_sales_history'
    assert event.start_time is not None

    jobs = db_session.query(JobLogDetails).filter(
        JobLogDetails.event_id == event_logger.event_id
    ).all()
    assert len(jobs) == 1
    assert jobs[0].action == 'Fetching Sales History'
    assert jobs[0].status == 'Completed'
    assert jobs[0].end_time is not None
