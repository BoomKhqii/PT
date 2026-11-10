# API and event architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

FastAPI acts as PT's local backend interface.

It serves the Windows UI, the web dashboard, and later authenticated device clients.

### Example API surface

```
Conversation
POST   /api/v1/chat/messages
GET    /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{id}

Knowledge
POST   /api/v1/documents/import
GET    /api/v1/documents
POST   /api/v1/knowledge/search

Workflows
POST   /api/v1/workflows
GET    /api/v1/workflows/{id}
POST   /api/v1/workflows/{id}/cancel
POST   /api/v1/workflows/{id}/approve

Academic
GET    /api/v1/academic/courses
POST   /api/v1/academic/study-guide
POST   /api/v1/academic/mock-exam

Memory
GET    /api/v1/memories
PATCH  /api/v1/memories/{id}
DELETE /api/v1/memories/{id}

System
GET    /api/v1/system/health
GET    /api/v1/system/metrics
GET    /api/v1/system/permissions

Events
WS     /api/v1/events
```

These are proposed contracts, not existing PT endpoints.

For real-time feedback, the backend publishes events such as:

```
{
  "event": "workflow.progress",
  "workflow_id": "wf_1042",
  "stage": "retrieval",
  "status": "running",
  "message": "Searching lecture documents",
  "timestamp": "2026-11-10T00:00:00+11:00"
}
```

The desktop overlay and dashboard receive the same event. They present it differently but never need separate AI implementations.

### Background processing

Long-running tasks should not occupy an HTTP request for several minutes.

A background worker processes operations such as document extraction, embedding generation, PDF creation, and large backtest analysis.

For the initial monolith, a durable SQLite-backed job table and dedicated worker process are sufficient.

Each job needs retries, cancellation, status tracking, timeouts, and idempotency—so restarting PT does not accidentally execute the same action twice.
