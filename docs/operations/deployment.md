# Deployment architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

Initial deployment — One Windows computer

Windows Host

PT Desktop UI

FastAPI Backend

Local Worker

Ollama Server

Audio Services

SQLite + Indexes

Separate logical services can run as local processes on the same machine.

Authenticated connections (future)

Mobile Client

Remote chat and notifications

Raspberry Pi

Monitoring and read-only telemetry

The Windows computer remains the primary execution host. The Raspberry Pi should not be responsible for running the full LLM unless its performance and resource availability justify it.

Use local processes and normal Python packaging first. Containers, remote workers, message brokers, and distributed services become relevant only when there is evidence they solve an actual problem.
