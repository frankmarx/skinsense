import json
import pytest
import requests
from chalicelib.orchestration.sqs_registry import EVENT_REGISTRY
from chalicelib.orchestration.logging import EventLogger
from chalicelib.connectors.skinport.client import SKINPORT_SALES_HISTORY_URL
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
    sample = requests.get(
        SKINPORT_SALES_HISTORY_URL,
        params={"app_id": 730, "currency": "USD", "market_hash_name": "AK-47 | Redline (Field-Tested)"},
        headers={"Accept-Encoding": "br", "User-Agent": "Skinsense-Price-Aggregator/1.0"},
        timeout=30,
    )
    sample.raise_for_status()
    print("\n--- SkinPort /v1/sales/history sample response ---")
    print(json.dumps(sample.json(), indent=2))

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
