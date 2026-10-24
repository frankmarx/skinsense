"""
AWS dev utility: add an event to the SQS job queue defined in .chalice/config.json.

The event is first registered in event_log_details (the SQS consumer drops
messages whose event_id it does not recognize), then sent to the queue.

Usage (from the backend folder):
    venv/bin/python dev-scripts/aws-dev.py <event_type> [key=value ...]

Examples:
    venv/bin/python dev-scripts/aws-dev.py test_api_connectors
    venv/bin/python dev-scripts/aws-dev.py cs_float_test_connection
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Make chalicelib importable when run as a plain script
sys.path.append(BASE_DIR)

from dotenv import load_dotenv

# Load local .env first (DB_URL etc.) so it takes precedence over config.json
load_dotenv(os.path.join(BASE_DIR, '.env'))


def load_chalice_config(stage='dev'):
    """Sets environment variables from .chalice/config.json for the given stage.

    Values already present in the environment (e.g. from .env) win, and
    empty placeholders in config.json are ignored.
    """
    config_path = os.path.join(BASE_DIR, '.chalice', 'config.json')
    with open(config_path) as f:
        config = json.load(f)

    try:
        env_vars = config['stages'][stage].get('environment_variables', {})
    except KeyError:
        raise ValueError(f"Stage '{stage}' not found in {config_path}")

    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value

    return env_vars


def add_event_to_queue(event_type, source='custom', params=None):
    """Registers the event in the database and adds it to the SQS queue."""
    from chalicelib.orchestration.event_registry import enqueue_event

    print("Event description")
    print(f"  event_type: {event_type}")
    print(f"  source:     {source}")
    if params:
        print(f"  params:     {params}")
    print(f"  queue_url:  {os.environ.get('SQS_QUEUE_URL')}")
    print()
    print("Adding to queue...")

    try:
        event_id = enqueue_event(event_type, source=source, params=params)
    except Exception as e:
        print(f"Failed to add event to the queue: {e}")
        sys.exit(1)

    print(f"Successfully added to queue (event_id: {event_id})")
    return event_id


if __name__ == '__main__':
    usage = (
        "Usage: venv/bin/python dev-scripts/aws-dev.py <event_type> [key=value ...]\n"
        "  e.g. venv/bin/python dev-scripts/aws-dev.py test_api_connectors"
    )
    if len(sys.argv) < 2:
        print(usage, file=sys.stderr)
        sys.exit(2)

    event_type = sys.argv[1]
    params = {}
    for arg in sys.argv[2:]:
        key, sep, value = arg.partition('=')
        if not sep:
            print(f"Invalid param {arg!r}, expected key=value", file=sys.stderr)
            sys.exit(2)
        params[key] = value

    load_chalice_config()
    add_event_to_queue(event_type, params=params or None)
