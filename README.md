# skinsense — CS2 Price Aggregator

A professional-grade, serverless full-stack Counter-Strike 2 (CS2) market price aggregator. The application fetches up-to-date pricing data using a scheduled lambda function, stores it in a secure PostgreSQL index, and serves it through a clean, modern, and minimalistic single-page dashboard.

---

## 📂 Project Structure

```text
skinsense/
├── README.md               # Main instructions and setup guide
├── backend/                # Serverless AWS Chalice Python Backend
│   ├── .chalice/
│   │   └── config.json     # AWS Chalice stage configurations
│   ├── app.py              # Backend API routes, scheduled tasks & helpers
│   └── requirements.txt    # Python package dependencies
└── frontend/               # Modern Vite + React Frontend Dashboard
    ├── index.html          # HTML Entrypoint
    ├── package.json        # JS/Node dependencies and scripts
    ├── vite.config.js      # Vite configuration (runs on port 3000)
    └── src/
        ├── main.jsx        # React DOM mounting
        ├── App.jsx         # Minimalist single-page dashboard component
        └── index.css       # Core styling & Light/Dark design variables
```

---

## ⚡ Quick Start: Backend Setup (Chalice)

The backend is built using **AWS Chalice**, which deploys your code as a set of managed AWS resources.

### Deployed AWS Resources
When you run `chalice deploy`, the following resources are created:
- **`skinsense-backend-dev-master_scheduler_twice_daily` (Lambda Function):** An orchestrator triggered by EventBridge on a twice-daily schedule, queuing batch jobs (e.g. CSFloat item listings).
- **`skinsense-backend-dev-master_scheduler_once_daily` (Lambda Function):** An orchestrator triggered by EventBridge on a once-daily schedule, queuing batch jobs (e.g. CSFloat connection test).
- **`skinsense-backend-dev-sqs-consumer` (Lambda Function):** The SQS consumer function. It pulls jobs from the queue one-by-one using `batch_size=1` and dispatches them via the command registry.
- **`Rest API` (AWS API Gateway):** The public HTTP endpoint the frontend calls; routes each request to the correct handler. A separate service from Lambda in the AWS console (search "API Gateway").
- **`skinsense-backend-dev` (Lambda Function):** Runs your Chalice app code, invoked by API Gateway for each incoming request.

### Prerequisites
- Python 3.9, 3.10, or 3.11 installed
- PostgreSQL database instance

### Installation Steps

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a Python virtual environment:**
   - **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Copy the example file into a local `.env` and populate it with your values:
   ```bash
   cp .env.example .env
   ```

   The variables defined in `.env.example`:

   | Variable | Description | Sensitive? | Production source |
   |---|---|---|---|
   | `DB_URL` | PostgreSQL connection string (e.g. `postgresql://user:pass@host:5432/db`) | Yes — credential | AWS Secrets Manager |
   | `CSFLOAT_API_KEY` | API key authenticating requests to the CSFloat API | Yes — credential | AWS Secrets Manager |
   | `COGNITO_CLIENT_ID` | Cognito App Client ID, used by the frontend for auth flows | No — public identifier | AWS Secrets Manager |
   | `COGNITO_USER_POOL_ID` | Cognito User Pool ID, used for auth configuration | No — public identifier | AWS Secrets Manager |
   | `SQS_QUEUE_NAME` | Name of the SQS queue that batch jobs are sent to | No — resource identifier | `.chalice/config.json` (plaintext Lambda env var) |
   | `SQS_QUEUE_URL` | URL of the SQS queue that batch jobs are sent to | No — resource identifier | `.chalice/config.json` (plaintext Lambda env var) |

   > **Note:** In production (Lambda), the sensitive values live in AWS Secrets Manager under the `skinsense/production/config` secret, while the non-sensitive `SQS_*` values are set as plaintext Lambda environment variables via `.chalice/config.json`. Locally, all of them are read from your `.env` file instead.
   >
   > ⚠️ The `SQS_*` variables have **no Secrets Manager fallback** — they are read only from the environment. They must always be set to real values (never empty), or the SQS consumer and job queueing will break.

5. **Start the local backend server:**
   ```bash
   chalice local --port 8000
   ```
    *Your API will now be running and accessible at `http://127.0.0.1:8000` (e.g. the `/skin-data/items` endpoint).*

### Database Migrations

When you change a model in `backend/chalicelib/models/`, follow these two steps:

1. **Generate a migration script:**
   ```bash
   cd backend
   ./venv/bin/alembic revision --autogenerate -m "description of change"
   ```

2. **Apply the migration to the database:**
   ```bash
   ./venv/bin/alembic upgrade head
   ```

---


## 💻 Quick Start: Frontend Setup (Vite + React)

The frontend is a lightweight, responsive dashboard built with **Vite**, **React**, and modern CSS variables, supporting real-time theme toggling (Light/Dark mode) and full searching/sorting capabilities.

### Prerequisites
- Node.js (v18+ recommended)
- npm or yarn package manager

### Installation Steps

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install package dependencies:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables (Optional):**
   By default, the frontend attempts to contact the Chalice local backend on port `8000`. You can explicitly set this using an `.env` file or environment variable if you host the backend elsewhere:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```

4. **Launch the Vite development server:**
   ```bash
   npm run dev
   ```
   *The application will launch automatically in your browser at `http://localhost:3000`.*

---

## ⚙️ Architecture & Features

### 🕒 Scheduled Data Aggregation
EventBridge scheduled triggers (defined in `backend/chalicelib/orchestration/event_registry.py`) enqueue batch jobs to an SQS queue on a recurring basis, grouped by frequency:
- **`once_daily`**: runs the CSFloat connection test each day.
- **`twice_daily`**: pulls the latest item listings from the **CSFloat API**.

A dedicated `sqs-consumer` Lambda pulls jobs from the queue one at a time (`batch_size=1`) and dispatches each to its handler via the command registry, keeping each sync isolated and independently retryable.

### 📡 REST API Endpoints
- **`GET /skin-data/items`** — returns the current item master list from the database.
- **`POST /events/sync`** — manually queues a sync job (e.g. CSFloat listings).
- **`GET /logs`** — returns recent job log entries.
- **`GET /config`** — returns frontend auth configuration (Cognito IDs).

### 🎨 Minimalist Frontend UI Theme
- **Dual Theme Support:** Fully reactive Dark & Light mode using standard CSS custom property injection. Responsive buttons allow quick toggle on top header.
- **Search & Sort Logic:** In-memory, highly-efficient filtering of items as you type, with select controls to sort prices ascending/descending or alphabetical.

