# SkinSense Application Context

## Overview
SkinSense aggregates CSGO skin data from various APIs ("Data Sources") into a Neon Postgres database and presents insights via a React frontend.

## Architecture
- **Backend**: Manages scheduled tasks and provides API endpoints to the frontend.
- **Frontend**: React application for displaying data insights.

## Database Model Hierarchy (Neon Postgres)
1.  **Global Models**: Shared across the application.
2.  **Bronze Models**: Raw data directly from APIs.
    - Naming: `{datasource_name}_...`
    - Mandatory column: `job_id`
3.  **Silver Models**: Standardized data.
    - Mandatory column: `datasource_id`

## Data Pipeline Lifecycle
Data ingestion is managed by `FeedLoader` objects located in `backend/chalicelib/loaders/{datasourcename}/`. Each `FeedLoader` has a `job_id` (EventBridge AWS ID).

### Pipeline Steps
1.  **Data Pulling** (`backend/chalicelib/connectors/`)
    - Fetches data from APIs.
    - Uses **Pydantic BaseModels** for schema definition.
2.  **Bronze Load**
    - Inserts data into the relevant Bronze table.
    - Includes the `job_id`.
3.  **Silver Transform**
    - Queries the Bronze table using the current `job_id`.
    - Transforms/cleans data into the standardized **Silver** format.
    - Inserts into Silver table with `datasource_id`.
