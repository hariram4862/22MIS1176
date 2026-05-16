# 22MIS1176

Backend track submission containing three backend deliverables and one supporting system design document.

## Repository Structure

```text
22MIS1176/
├── logging_middleware/
├── vehicle_maintenance_scheduler/
├── notification_app_be/
├── notification_system_design.md
├── requirements.txt
├── README.md
└── .gitignore
```

## Deliverables

### 1. Logging Middleware

Reusable request logging middleware and related helpers for backend services.

Location:
- `logging_middleware/`

### 2. Vehicle Maintenance Scheduler

FastAPI service that fetches depots and vehicles, applies scheduling logic, and exposes the computed maintenance schedule.

Location:
- `vehicle_maintenance_scheduler/`

Default run command:

```powershell
uvicorn vehicle_maintenance_scheduler.main:app --reload
```

### 3. Notification Priority Inbox App

FastAPI service for Stage 6 that fetches live notifications from the protected upstream API, computes priority scores, and returns the top `n` ranked notifications.

Location:
- `notification_app_be/`

Default run command:

```powershell
uvicorn notification_app_be.main:app --reload
```

Primary endpoint:

```text
GET /api/v1/notifications/priority?top_n=10
```

### 4. Notification System Design

Detailed six-stage markdown submission covering REST API design, database design, query optimization, scalability, distributed notification delivery, and the priority inbox approach.

Location:
- `notification_system_design.md`

## Setup

### Prerequisites

- Python 3.10+
- Virtual environment
- Installed dependencies from `requirements.txt`

### Install Dependencies

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Configuration

Create or update `.env` in the repository root with:

```env
AUTH_TOKEN=<your_api_token>
LOG_API_URL=http://4.224.186.213/evaluation-service/logs
BASE_URL=http://4.224.186.213/evaluation-service
```

Notes:

- `AUTH_TOKEN` is required for the notification and scheduler APIs that call the protected upstream endpoints.
- If the token expires, replace it and restart the corresponding FastAPI server.

## Running the Services

### Vehicle Maintenance Scheduler

```powershell
uvicorn vehicle_maintenance_scheduler.main:app --reload
```

Suggested local checks:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/schedule`

### Notification Priority Inbox App

```powershell
uvicorn notification_app_be.main:app --reload
```

Suggested local checks:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/api/v1/notifications/priority?top_n=10`

Optional read-state simulation:

```text
http://127.0.0.1:8000/api/v1/notifications/priority?top_n=10&read_ids=<notification_id>
```

## Stage 6 Implementation Summary

The notification priority service implements:

- live notification fetch from the provided protected API
- score-based ranking
- priority weights: `Placement > Result > Event`
- unread bonus support
- recency-aware scoring
- top-`n` extraction using a min heap with `O(N log K)` complexity

## Submission Notes

- `notification_system_design.md` contains the complete six-stage written response.
- `notification_app_be` contains the Stage 6 working backend implementation.
- `vehicle_maintenance_scheduler` contains the scheduling API deliverable.
- `logging_middleware` contains the reusable logging component deliverable.
