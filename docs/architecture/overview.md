# Overall system architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

PT (Personal Technology / Personal Assistant) is a Windows-first, locally hosted, modular AI assistant inspired by Jarvis. Its long-term purpose is to become an intelligent operating layer across your computer, academic work, daily productivity, and eventually algorithmic trading.

The target design includes:

- Local AI: Ollama, local speech recognition, local speech synthesis, and local data storage. No mandatory cloud AI.
- Natural interaction: Wake words such as "Hey PT", voice conversations, an on-screen orb, subtitles, and text chat.
- Persistent intelligence: PT remembers approved information, retrieves previous materials, and maintains context across sessions.
- Central orchestrator: One main assistant delegates tasks to Academic, Personal, and Trading specialists.
- Academic-first development: Lecture retrieval, studying, assessments, schedules, reminders, and PDF generation are the first substantial capabilities.
- Trading later: OrbCatcher analytics, backtest analysis, risk monitoring, and eventually more advanced financial research.
- Windows PC first: Raspberry Pi, mobile clients, and distributed deployments are future extensions.

This is the target architecture, not a claim that every subsystem has already been implemented.

SYSTEM LEVEL — TOP TO BOTTOM

User Interaction Layer

Microphone · Wake word · Chat · Desktop overlay · Dashboard

PT Core — Central Orchestrator

Intent routing · Planning · Context · Delegation · Verification

Academic

Lectures, studying, research, documents

Personal

Schedules, tasks, desktop actions

Trading

Backtests, statistics, risk analysis

Shared AI & Execution Services

Ollama / Qwen · LangGraph · RAG · Tool registry · Permissions

Persistence & Background Services

SQLite · Vector index · Files · Memory · Scheduler · Job queue

Operating System & External Data Boundaries

Windows applications · Local file system · Optional calendar sync · Future MT5 read-only integration

Security policy, permissions, validation, and audit logging apply across every layer.

PT's AI proposes actions. Trusted application code enforces permissions and executes approved actions.
