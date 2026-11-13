# Tool execution architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

PT requires a tool registry: a collection of predefined actions the assistant may request.

The LLM should only produce a structured proposal. A separate tool executor validates permissions, inputs, environment, and expected effects.

### Example tool contract

```
{
  "name": "academic.generate_revision_pdf",
  "version": "1.0",
  "description": "Generate a PDF revision guide",
  "input_schema": {
    "unit": "string",
    "topics": ["string"],
    "output_name": "string"
  },
  "permissions": [
    "academic.read",
    "documents.create"
  ],
  "risk_level": "low",
  "requires_confirmation": false
}
```

An execution request would pass through these controls:

```
LLM proposes a tool call
    |
    v
Tool exists in registry?
    |
    v
Arguments match validated schema?
    |
    v
Is the action permitted?
    |
    v
Does it need user confirmation?
    |
    v
Execute via trusted code
    |
    v
Verify output and record audit event
    |
    v
Return structured result to orchestrator
```

A tool result should contain at least `status`, `output`, `error_code`, `artifacts`, and `execution_id`.

### Permission model

| Risk level       | Examples                                     | Default treatment                     |
| ---------------- | -------------------------------------------- | ------------------------------------- |
| Read-only        | Search lecture, read task                    | Allow within approved scope           |
| Low-impact write | Create new revision PDF                      | Allow in designated workspace         |
| Moderate write   | Edit a document, create a reminder           | Validate and confirm when appropriate |
| High-impact      | Delete files, send messages, change settings | Explicit confirmation                 |
| Critical         | Place trade, change broker risk settings     | Disabled in initial versions          |

Each agent receives only its required tools. The Academic Agent should not inherit trading privileges simply because it runs inside PT.

Permissions must be enforced by code, not solely through the model's system prompt.
