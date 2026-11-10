# Security and privacy architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

PT will control local applications and retain potentially sensitive academic and personal information. Security should therefore be part of its architecture from the beginning.

### Trust boundaries

```
UNTRUSTED
  User-provided documents
  Websites and external API responses
  Imported trading reports
  LLM-generated instructions
          |
          v
  Input validation / sanitization
          |
          v
TRUSTED APPLICATION LOGIC
  Permission engine
  Tool registry
  Path restrictions
  Confirmation manager
          |
          v
PRIVILEGED OPERATIONS
  File writes
  Calendar changes
  Application control
  Credential access via secure adapters
  Future trading execution boundary
```

The main controls are:

- Localhost-only backend initially: Do not expose Ollama or the PT control API directly to the internet.
- Least privilege: Each agent receives access only to approved tools and directories.
- Secret protection: Use Windows Credential Manager or an equivalent secure store for integration tokens.
- Explicit consent: Require approval for destructive actions and external side effects.
- Prompt-injection resistance: Treat retrieved documents and webpage text as data, never as authority to change PT's instructions.
- Audit logging: Record executed actions, approval decisions, and errors without indiscriminately storing private content.
- Privacy controls: Allow memory deletion, microphone muting, integration revocation, and backup management.
- Trading isolation: Future MT5 operations must sit behind an independently enforced risk and authorization boundary.

PT should fail safely. If a permission check, tool validation, or confirmation step fails, the action must not execute.
