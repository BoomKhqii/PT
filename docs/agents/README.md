# Multi-agent architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

PT has one central orchestrator and three domain specialists. They share inference, memory, storage, and execution infrastructure; each receives only its permitted tools.

- [Academic Agent — first major release](academic.md)
- [Personal Agent](personal.md)
- [Trading Agent — later release](trading.md)

Academic workflows are the first major release. Personal productivity expands the platform; Trading analytics follows later. See [orchestration](../architecture/orchestrator.md) and [tool execution](../architecture/tool-execution.md).
