import pytest
from unittest.mock import patch
from chalicelib.orchestration.sqs_registry import EVENT_REGISTRY
from chalicelib.orchestration.logging import EventLogger
from chalicelib.db import get_db
from chalicelib.models import JobLogDetails, EventLogDetails


@pytest.fixture
def db_session():
    """Provides a database session."""
    with get_db() as session:
        yield session


def test_event_test_api_connectors(db_session):
    """
    Tests the test_api_connectors event: one event, two jobs (one per
    connector). Both connector clients are mocked; requires no network.
    """
    handler = EVENT_REGISTRY['test_api_connectors']
    event_logger = EventLogger(event_type='test_api_connectors', source='test')
    event_logger.create_event()

    with patch(
        'chalicelib.event_definition.csfloat_events.test_connection',
        return_value={"status": "success", "status_code": 200},
    ), patch(
        'chalicelib.event_definition.skinport_events.test_connection',
        return_value={"status": "success", "status_code": 200},
    ):
        result = handler(event_logger)

    assert result["csfloat"]["status"] == "success"
    assert result["skinport"]["status"] == "success"

    event = db_session.query(EventLogDetails).filter(
        EventLogDetails.event_id == event_logger.event_id
    ).one()
    assert event.event_type == 'test_api_connectors'
    assert event.source == 'test'
    assert event.start_time is not None

    jobs = db_session.query(JobLogDetails).filter(
        JobLogDetails.event_id == event_logger.event_id
    ).order_by(JobLogDetails.start_time, JobLogDetails.id).all()
    assert [job.action for job in jobs] == [
        'Testing CSFloat Connection',
        'Testing SkinPort Connection',
    ]
    assert all(job.status == 'Completed' for job in jobs)
    assert all(job.end_time is not None for job in jobs)


def test_event_test_api_connectors_partial_failure(db_session):
    """
    A failing connector is recorded as a Failed job without stopping the
    other connector's test, and the handler raises at the end.
    """
    handler = EVENT_REGISTRY['test_api_connectors']
    event_logger = EventLogger(event_type='test_api_connectors', source='test')
    event_logger.create_event()

    with patch(
        'chalicelib.event_definition.csfloat_events.test_connection',
        return_value={"status": "error", "message": " simulated failure"},
    ), patch(
        'chalicelib.event_definition.skinport_events.test_connection',
        return_value={"status": "success", "status_code": 200},
    ):
        with pytest.raises(RuntimeError, match="csfloat"):
            handler(event_logger)

    jobs = db_session.query(JobLogDetails).filter(
        JobLogDetails.event_id == event_logger.event_id
    ).order_by(JobLogDetails.start_time, JobLogDetails.id).all()
    assert [job.action for job in jobs] == [
        'Testing CSFloat Connection',
        'Testing SkinPort Connection',
    ]
    assert jobs[0].status == 'Failed'
    assert jobs[1].status == 'Completed'
