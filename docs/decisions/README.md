# Final architecture decisions

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

| Decision                        | Recommendation                                     |
| ------------------------------- | -------------------------------------------------- |
| Single LLM or many LLMs?        | One primary model first; provider adapters later   |
| One giant agent or specialists? | One orchestrator with domain-specific workflows    |
| Microservices or monolith?      | Modular monolith first                             |
| Database?                       | SQLite initially                                   |
| Vector search?                  | Add when the academic knowledge corpus requires it |
| Cloud-dependent?                | No, except explicitly enabled integrations         |
| All modules immediately?        | No, academic first                                 |
| Orb implementation?             | PySide6 first; C++ only if justified               |
| Autonomous file/system access?  | Strictly permissioned tools                        |
| Trading execution?              | Not in initial scope                               |
| Main engineering deliverable?   | Reliable, evaluated academic workflows             |

### The flagship PT vision

PT should evolve into a local-first, stateful AI operating platform: an assistant that understands requests, finds evidence in the user's documents, plans workflows, safely uses tools, remembers approved context, produces validated outputs, and continues scheduled work reliably.

For your initial release, the central success story is simple:

A user speaks a request, PT retrieves relevant university material, reasons over the evidence, generates a useful document, saves it correctly, and remembers the resulting task state.

That end-to-end capability is a stronger foundation for an AI Engineer or Software Engineer portfolio than implementing dozens of disconnected Jarvis-style features. The Trading Agent can then build on the same infrastructure without forcing you to redesign the entire application.
