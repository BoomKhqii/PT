# Reliability and observability

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

### Error-handling policy

| Failure                          | Expected behavior                           |
| -------------------------------- | ------------------------------------------- |
| Wake word not detected           | Push-to-talk fallback                       |
| Speech transcription fails       | Request repetition                          |
| Local model unavailable          | Report unavailable service; preserve task   |
| Retrieval finds no evidence      | State that source evidence was not found    |
| Malformed tool arguments         | Reject before execution                     |
| Calendar service offline         | Queue only when explicitly appropriate      |
| PDF rendering fails              | Preserve structured draft and error         |
| Windows restarts during workflow | Restore from persisted checkpoint           |
| Duplicate scheduled event        | Idempotency check prevents duplicate action |
| Unauthorized request             | Deny operation and log reason               |

Observability should include latency, memory usage, model performance, retrieval effectiveness, tool failures, and workflow completion rates.

Keep an `execution_id` across the orchestrator, tool calls, and logs so you can trace one user request through the entire system.
