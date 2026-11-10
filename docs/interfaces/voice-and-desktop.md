# User interaction architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

PT must support several different interfaces without duplicating its intelligence.

Voice

Wake word, microphone capture, transcriptions, spoken answers

Chat

Typed instructions, responses, document uploads

Desktop orb

Floating interface, live subtitles, status, confirmations

Dashboard

Manage tasks, memories, documents, integrations, history

All interfaces use the same PT service

FastAPI Application Gateway

REST endpoints + WebSocket events + session identity

### Voice pipeline

```
STANDBY
  |
  | "Hey PT" detected locally
  v
ACTIVATED
  |
  | Activation sound / overlay
  v
LISTENING
  |
  | Microphone + voice activity detection
  v
TRANSCRIBING
  |
  | whisper.cpp
  v
INTENT ANALYSIS
  |
  | Core orchestrator
  v
EXECUTING / REASONING
  |
  | Retrieve memory / call tools / generate response
  v
SPEAKING
  |
  | Piper TTS + visible subtitles
  v
FOLLOW-UP WINDOW
  |
  +-- Continued speech -> LISTENING
  |
  +-- Timeout -> STANDBY
```

Key implementation requirements:

- Standby audio is processed locally in a small memory buffer and is not routinely stored.
- Voice activity detection ends an utterance without requiring a fixed-length recording.
- Push-to-talk remains available when wake-word recognition fails.
- The user can interrupt PT while it is speaking.
- Audio output, subtitle display, and task execution must not block one another.
- Microphone muting must be immediate and visibly indicated.

### Desktop orb

The orb is a presentation client, not the AI engine. It listens to PT's events and renders the current state.

Orb states: **Standby**, **Listening**, **Thinking**, and **Speaking**. Listening indicates that PT is capturing the command.

For the first version, PySide6 is sufficient. Moving the overlay to C++/Qt would only be justified if actual profiling identifies significant performance, rendering, or integration limitations.
