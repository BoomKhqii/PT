# Persistence and database architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

SQLite is suitable for PT's initial single-user local installation. It stores structured operational records, while original documents and generated artifacts live in a managed file store.

### Core entities

Structured records link sessions, messages, workflows, tool runs, memories, documents, courses, assessments, study attempts, tasks, and reminders. See the suggested tables below. The pasted source did not preserve a readable entity diagram; relationship cardinalities remain unspecified.

### Suggested tables

| Table                  | Primary contents                        |
| ---------------------- | --------------------------------------- |
| `sessions`             | Session ID, start/end, interaction mode |
| `messages`             | Role, content, timestamps, session ID   |
| `workflows`            | Type, state, status, checkpoints        |
| `tool_runs`            | Tool ID, arguments, outcomes, duration  |
| `memories`             | Content, scope, provenance, status      |
| `documents`            | File metadata, hash, version, path      |
| `document_chunks`      | Text segments, page, section, source    |
| `courses`              | Unit, semester, course metadata         |
| `assessments`          | Assessment type, date, weighting        |
| `study_attempts`       | Question, answer, rubric, score         |
| `tasks`                | Description, due date, priority, status |
| `reminders`            | Trigger, recurrence, last execution     |
| `integration_accounts` | Connection metadata, not raw tokens     |
| `audit_events`         | Actor, action, result, timestamp        |

Additional indexes would support semantic retrieval, full-text search, and efficient filtering by course, source, and date.

### Data storage separation

```
PT Data Directory
|
+-- pt.db                  Structured records
+-- indexes/               Semantic indexes
+-- documents/
|   +-- originals/         Imported source files
|   +-- extracted/         Cached text and metadata
|   +-- generated/         PDFs, reports, study guides
|
+-- models/                Optional local model assets
+-- checkpoints/           Workflow recovery state
+-- backups/               Protected database backups
+-- logs/                  Sanitized application logs
```

Do not place everything inside SQLite. Large PDFs, audio, and model weights belong in the filesystem or object storage.

Database records should reference files using controlled identifiers, rather than allowing arbitrary user-supplied paths.
