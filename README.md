# Minimal Temporal Job Service (FastAPI + Temporal)

This project implements a durable job execution service using **FastAPI** (Server) and **Temporal** (Workflow Orchestration). It ensures fault tolerance and automatic retries for background tasks.

## 📂 Project Structure (Clean Architecture)

- `src/main.py`: FastAPI application (Entry point for client requests)
- `src/workflows.py`: Temporal Workflow definitions (Orchestration logic)
- `src/activities.py`: Temporal Activity definitions (Business logic & computation)
- `src/worker.py`: Worker entry point (Polls tasks from Temporal server)
- `docker-compose.yaml`: Infrastructure definition for Temporal Server

---

## 🚀 How to Run

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Dependencies: `pip install fastapi uvicorn temporalio pydantic`

### 1. Start Temporal Server
We use the official `temporalio/server` image via Docker Compose for a local development environment.

```bash
docker-compose up -d
```
**Note**: Wait until the Temporal Web UI is accessible at http://localhost:8080.

### 2. Start the Worker (Terminal 1)
The worker connects to Temporal and listens for tasks in `my-task-queue`.

```bash
python -u -m src.worker
```

### 3. Start the API Server (Terminal 2)
The API server exposes endpoints to submit jobs and query status.

```bash
python -m uvicorn src.main:app --reload
```

## ✅ Verification Steps (Core Requirements)
You can verify the system using the **Swagger UI**: http://127.0.0.1:8000/docs

### Test 1: Controlled Failure & Automatic Retry
To demonstrate fault tolerance (Requirement #3), submit a job with the `fail_first_attempt` flag.

Request (`POST /jobs`):
```JSON
{
  "input": {
    "numbers": [10, 20, 30]
  },
  "options": {
    "fail_first_attempt": true
  }
}
```

### Verify:
1. Check the Worker Terminal. You should see:
- `🚨 Simulating failure per requirement!` (Attempt #1 fails)
- `✅ Job SUCCESS! Sum is 60` (Attempt #2 succeeds automatically)

2. Check the API Response (GET /jobs/{job_id}):
- The JSON response will include "attempts_taken": 2, proving the retry occurred.

## 💡Key Design Decisions
1. FastAPI & Pydantic:
- Used Pydantic models to strictly validate the nested JSON input/output requirements ensuring type safety between the API and Temporal Workflows.

2. Deterministic Workflows:
- The Workflow code (`src/workflows.py`) contains strictly no external I/O or random logic. All computation and side effects (like logging/prints) are delegated to Activities.

3. Separate Worker & API:
- Decoupled the API server from the Worker process to allow them to scale independently.

## 🤖 AI Usage Disclosure
**AI Assistant Used**: Google Gemini

### Usage Details:
- Scaffolding: Used AI to generate the initial boilerplate for Temporal connection and Pydantic models.
- Debugging: Used AI to troubleshoot Docker Compose network issues and specific Python import errors.
- Spec Compliance: Consulted AI to ensure the JSON input/output schemas strictly matched the provided requirements screenshots.

**Note**: All logic regarding the Retry Policy and Determinism constraints was manually verified and understood by the developer.