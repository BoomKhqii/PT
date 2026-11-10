# Recommended project repository

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

```
project-pt/
|
+-- README.md
+-- pyproject.toml
+-- .env.example
+-- docs/
|   +-- architecture.md
|   +-- api-contracts.md
|   +-- security-model.md
|   +-- decisions/
|
+-- apps/
|   +-- desktop/                 # Qt orb and controls
|   +-- dashboard/               # React UI
|
+-- src/pt/
|   +-- main.py
|   +-- config/
|   |
|   +-- api/
|   |   +-- routes/
|   |   +-- events/
|   |   +-- schemas/
|   |
|   +-- core/
|   |   +-- orchestrator.py
|   |   +-- router.py
|   |   +-- state.py
|   |   +-- planner.py
|   |   +-- verifier.py
|   |
|   +-- agents/
|   |   +-- academic/
|   |   +-- personal/
|   |   +-- trading/
|   |
|   +-- inference/
|   |   +-- providers/
|   |   +-- prompts/
|   |   +-- model_registry.py
|   |
|   +-- voice/
|   |   +-- capture.py
|   |   +-- wakeword.py
|   |   +-- vad.py
|   |   +-- stt.py
|   |   +-- tts.py
|   |
|   +-- memory/
|   |   +-- manager.py
|   |   +-- store.py
|   |   +-- retrieval.py
|   |
|   +-- knowledge/
|   |   +-- ingestion.py
|   |   +-- extraction.py
|   |   +-- chunking.py
|   |   +-- embeddings.py
|   |   +-- search.py
|   |
|   +-- tools/
|   |   +-- registry.py
|   |   +-- executor.py
|   |   +-- validators.py
|   |   +-- windows/
|   |   +-- documents/
|   |
|   +-- documents/
|   |   +-- pdf_renderer.py
|   |   +-- quality_checks.py
|   |
|   +-- integrations/
|   |   +-- calendar/
|   |   +-- drive/
|   |   +-- metatrader/
|   |
|   +-- scheduler/
|   +-- security/
|   +-- storage/
|   +-- telemetry/
|
+-- migrations/
+-- tests/
|   +-- unit/
|   +-- integration/
|   +-- end_to_end/
|   +-- evaluations/
|
+-- scripts/
+-- benchmarks/
+-- data/                       # Gitignored
+-- logs/                       # Gitignored
```

This structure provides room for growth while keeping the first release as a coherent application rather than prematurely splitting it into services.
