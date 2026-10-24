import logging
from chalicelib.event_definition.csfloat_events import run_test_connection as run_csfloat_test_connection
from chalicelib.event_definition.skinport_events import run_test_connection as run_skinport_test_connection

logger = logging.getLogger('chalice')

CONNECTOR_TESTS = {
    'csfloat': run_csfloat_test_connection,
    'skinport': run_skinport_test_connection,
}


def run_test_api_connectors(event_logger):
    """
    Runs the connection test for every registered connector.

    Each connector runs as its own job so the trace shows them
    individually; a failing connector is recorded and the remaining
    connectors still run. Raises at the end if any connector failed.
    """
    logger.info(f"Running API connector tests... event: {event_logger.event_id}")

    results = {}
    failures = []

    for connector, test in CONNECTOR_TESTS.items():
        try:
            results[connector] = test(event_logger)
        except Exception as e:
            results[connector] = {"status": "error", "message": str(e)}
            failures.append(connector)
            logger.error(f"Connector test failed for {connector}: {e}")

    if failures:
        raise RuntimeError(f"Connector test failed for: {', '.join(failures)}")

    logger.info(f"Connector Test Results: {results}")
    return results
