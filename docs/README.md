# PT documentation

This is the organized reference for **Project PT — Complete System Architecture, version 3.0 (November 2026)**, supplied by the project owner. It describes the target system, not completed implementation.

PT is a Windows-first, locally hosted personal AI assistant. Build a modular Python monolith, prioritize academic workflows, and keep tool permissions under trusted application code.

## Start here

1. [Vision and system overview](architecture/overview.md)
2. [Architecture decisions](decisions/README.md)
3. [Development roadmap](development/roadmap.md)
4. [Academic study-guide workflow](workflows/academic-study-guide.md)

## Architecture

- [Technology stack](architecture/technology-stack.md)
- [Core orchestrator](architecture/orchestrator.md)
- [Tool execution and permissions](architecture/tool-execution.md)
- [Security and privacy](architecture/security.md)

## Specialist agents

- [Agent organization](agents/README.md)
- [Academic Agent](agents/academic.md)
- [Personal Agent](agents/personal.md)
- [Trading Agent](agents/trading.md)

## Interfaces

- [Voice, desktop orb, chat, and dashboard](interfaces/voice-and-desktop.md)
- [API contracts, events, and background jobs](interfaces/api-and-events.md)

## Data and intelligence

- [Memory lifecycle](data/memory.md)
- [Document ingestion and RAG](data/knowledge-and-rag.md)
- [Database and file storage](data/storage.md)

## Operations

- [Scheduling and proactive tasks](operations/scheduling.md)
- [Reliability and observability](operations/reliability.md)
- [Deployment](operations/deployment.md)

## Development

- [Proposed repository structure](development/repository-structure.md)
- [Phased roadmap](development/roadmap.md)
- [Evaluation and acceptance targets](development/evaluation.md)
- [Engineering goals](development/engineering-goals.md)

## Source and maintenance

The supplied specification was divided by responsibility. Pasted browser styling and favicon artifacts were removed; readable workflow diagrams were reconstructed where possible. The roadmap was converted into a table. No external technology validation was performed as part of this documentation change; provisional choices remain provisional.

Keep each subsystem's requirements in its own document. Record changes to architectural choices in `decisions/`, and update this index when adding a topic. The repository tree in the development guide is a proposed layout, not a description of today's checkout.
