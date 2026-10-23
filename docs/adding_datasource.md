# Adding a New Public API Datasource

Follow these steps to add a new Public API as a datasource, based on the CSFloat and SkinPort implementations.

The same steps apply when adding a new endpoint to an existing datasource: add the schema and client function to the existing connector folder, add the bronze model, and migrate — only the loader and event registration differ in name.

## 1. Connector Setup
Create a new directory in `backend/chalicelib/connectors` named after the datasource. Inside this directory, create:
- `schemas.py`: Define the shape of the data coming from the API using pydantic models.
- `client.py`: Implement the logic to call the API and return the schema objects (or lists of schema objects) defined in `schemas.py`.

Conventions:
- Clients should raise on failure (`raise_for_status()`, no swallowing) so that job logging records truthful `Failed` statuses.
- If the API requires a key, add a getter in `backend/chalicelib/utils/config.py` following the existing pattern (env var with Secrets Manager fallback).

## 2. Bronze Models
Add new models in `backend/chalicelib/models/bronze`. These bronze models should represent exactly what the data looks like from the API and should closely mirror the schemas defined in the connector. Bronze rows are stamped with the `job_id` of the job that loaded them.

Then:
- Export the new model from `backend/chalicelib/models/__init__.py`.
- Develop the migration on the Neon dev branch first: run `make update-test-database` from `backend/` (prompts for a message, autogenerates + applies against the test branch). If you iterate on the model, follow the delete-draft-file + reset-dev-branch rule described in the README's Database Migrations section before regenerating.
- When confirmed, apply the single final migration to production with `make update-prod-database`.

## 3. Loaders
Create a new directory in `backend/chalicelib/loaders` named after the datasource. For each function defined in `client.py`, create a corresponding file. In each file, define a class that extends `FeedLoader` and implements:
- `extract()`: Use the connector client to fetch data from the API.
- `bronze_load(raw_data, job_id)`: Load the API data directly into the corresponding bronze model, tagging it with the provided `job_id`.
- `silver_transform(raw_data, job_id)`: Transform the data from the bronze table (selected by `job_id`) into a shape that fits the silver table.

## 4. Events
Create a new file in `backend/chalicelib/event_definition` named `{datasource_name}_events.py`. Define a function named `run_{operation}` (e.g. `run_sales_history`) that accepts an `EventLogger`, runs each stage of the loader inside `event_logger.job(action=...)` blocks, and lets the job context manager record `Completed`/`Failed` status for each stage.

Then wire it up:
- Register the event in `EVENT_REGISTRY` (`backend/chalicelib/orchestration/sqs_registry.py`) under an event type named `{datasource}_{operation}` (e.g. `skinport_sales_history`). This is what the SQS consumer and `POST /events/sync` dispatch on.
- If the event should run on a schedule, add its event type to a group in `SCHEDULE_GROUPS` (`backend/chalicelib/orchestration/event_registry.py`).
- Add a row for the datasource to the `datasource` table (silver tables have foreign keys to it).

## 5. Tests
Create `backend/chalicelib/tests/{datasource}/test_{datasource}.py`. Each event gets a test named `test_event_{event_type}()` that:
- Looks up the handler via `EVENT_REGISTRY` and calls it with a fresh `EventLogger(event_type=..., source='test')` after calling `create_event()`.
- Mocks the connector for full pipeline tests (extract -> bronze -> silver) and asserts on the `event_log_details` and `job_log_details` rows, including the job action trail and bronze linkage via the loading job's `job_id`.
- Hits the live API for connection-style tests (only if the API allows it; respect rate limits).

Tests run against the test branch database (a copy of main) via `.env.test`. Do not create or truncate tables in tests — the schema comes from the branch copy, and tests must stay rerun-safe by scoping assertions to the IDs they generate (silver writes upsert; bronze accumulates per `job_id`).
