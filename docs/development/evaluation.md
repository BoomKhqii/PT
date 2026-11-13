# Engineering success criteria

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

These are proposed acceptance targets for PT.

| Metric                          | Target                                                 |
| ------------------------------- | ------------------------------------------------------ |
| Intentional wake detection      | At least 95% in controlled tests                       |
| Unintended wakeups              | Under 1 per 8 idle hours, measured                     |
| Simple voice command completion | Under 5 seconds where hardware permits                 |
| Unauthorized tool execution     | Zero in negative test suite                            |
| Lecture retrieval Recall@5     | At least 90% on labeled test questions                 |
| Citation correctness            | At least 95% on evaluated responses                    |
| PDF generation success          | At least 99% on valid test inputs                      |
| Restart recovery                | Resume or safely fail all persistent jobs              |
| Memory deletion                 | No deleted record returned in subsequent searches      |
| Local-only mode                 | No external network dependency for core chat and voice |

Hardware-dependent latency targets should be finalized only after benchmarking your Windows computer.

For technical rigor, evaluate the assistant on test datasets that include ambiguous requests, conflicting memories, missing document content, prompt-injection attempts, tool failures, and restarts.
