# Adding a New Public API Datasource

Follow these steps to add a new Public API as a datasource, based on the CSFloat implementation.

## 1. Connector Setup
Create a new directory in `backend/chalicelib/connectors` named after the datasource. Inside this directory, create:
- `schemas.py`: Define the shape of the data coming from the API.
- `client.py`: Implement the logic to call the API and return the schema objects (or lists of schema objects) defined in `schemas.py`.

## 2. Bronze Models
Add new models in `backend/chalicelib/models/bronze`. These bronze models should represent exactly what the data looks like from the API and should closely mirror the schemas defined in the connector.

## 3. Loaders
Create a new directory in `backend/chalicelib/loaders` named after the datasource. For each function defined in `client.py`, create a corresponding file. In each file, define a class that extends `FeedLoader` and implements:
- `extract()`: Use the connector client to fetch data from the API.
- `bronze_load(raw_data, job_id)`: Load the API data directly into the corresponding bronze model, tagging it with the provided `job_id`.
- `silver_transform(raw_data, job_id)`: Transform the data from the bronze table (selected by `job_id`) into a shape that fits the silver table.

## 4. Events
Create a new file in `backend/chalicelib/event_definition` named `{datasource_name}_events`. Define a function that accepts an `EventLogger`, runs each stage of the loader inside `event_logger.job(action=...)` blocks, and lets the job context manager record Completed/Failed status for each stage.
