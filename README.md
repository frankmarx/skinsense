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
- **`skinsense-backend-dev-master_scheduler_twice_daily` (Lambda Function):** A single orchestrator function triggered by EventBridge (CloudWatch Events) that queues multiple batch jobs.
- **`skinsense-backend-dev-handle_sqs_message` (Lambda Function):** The centralized SQS consumer function. It pulls jobs from the queue one-by-one using `batch_size=1` and dispatches them via the `COMMAND_REGISTRY`.
- **`skinsense-backend-dev` (Lambda Function):** The main entry point for your REST API, handling requests from the frontend via API Gateway.
- **`Rest API` (AWS API Gateway):** The front-door for your application, routing frontend HTTP requests to the appropriate backend Lambda functions.

### Prerequisites
- Python 3.9, 3.10, or 3.11 installed
- PostgreSQL database instance (or Docker)

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

4. **Database Configuration:**
   Chalice reads the database URI from the `DATABASE_URL` environment variable. Ensure this is configured locally or in your Chalice stage config.
   - Example Database URI format: `postgresql://username:password@localhost:5432/skinsense`

   Set the environment variable locally before running:
   - **macOS/Linux:**
     ```bash
     export DATABASE_URL="postgresql://username:password@localhost:5432/skinsense"
     ```
   - **Windows CMD:**
     ```cmd
     set DATABASE_URL=postgresql://username:password@localhost:5432/skinsense
     ```
   - **Windows PowerShell:**
     ```powershell
     $env:DATABASE_URL="postgresql://username:password@localhost:5432/skinsense"
     ```

5. **Start the local backend server:**
   ```bash
   chalice local --port 8000
   ```
    *Your API will now be running and accessible at `http://127.0.0.1:8000/prices`.*

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

## 🛠️ Local PostgreSQL Development (Docker Option)

If you don't have a PostgreSQL server installed on your system, you can quickly spin up a containerized DB using Docker:

```bash
docker run --name skinsense-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secretpass \
  -e POSTGRES_DB=skinsense \
  -p 5432:5432 \
  -d postgres:15
```

Using this container, your environment connection string will be:
`DATABASE_URL="postgresql://admin:secretpass@127.0.0.1:5432/skinsense"`

---

## ⚙️ Architecture & Features

### 🕒 Scheduled CRON Aggregator
In `app.py`, the `@app.schedule('rate(12 hours)')` decorator instructs AWS Lambda/CloudWatch to invoke the `fetch_and_update_prices` function every 12 hours.
- It pulls the latest index from the external **CSGOBackpack API**.
- Includes complete commented boilerplate demonstrating safe item parsing and database transactional upserts (`INSERT ... ON CONFLICT DO UPDATE`).

### 📡 Fault-Tolerant REST API Endpoint
The `/prices` endpoint has a fallback mechanism:
- If the database is empty, configuring, or offline, the API **will not crash**. It gracefully yields simulated dummy datasets containing premium items (e.g. M9 Bayonet, Karambit Doppler, AWP Asiimov) so frontend development can continue unimpeded.

### 🎨 Minimalist Frontend UI Theme
- **Dual Theme Support:** Fully reactive Dark & Light mode using standard CSS custom property injection. Responsive buttons allow quick toggle on top header.
- **Search & Sort Logic:** In-memory, highly-efficient filtering of items as you type, with select controls to sort prices ascending/descending or alphabetical.
