# Technology stack

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

The table lists the proposed technologies and their responsibilities.

| Layer               | Technology                         | Responsibility                    |
| ------------------- | ---------------------------------- | --------------------------------- |
| Core language       | Python 3.11+                       | Backend logic, agents, processing |
| API                 | FastAPI                            | Local application interface       |
| Orchestration       | LangGraph                          | Multi-step agent workflows        |
| Local LLM runtime   | Ollama                             | Local model serving               |
| Main LLM            | Qwen, benchmarked locally          | Reasoning and tool selection      |
| Speech recognition  | whisper.cpp                        | Speech-to-text                    |
| Wake-word detection | Porcupine or openWakeWord          | Local activation                  |
| Speech synthesis    | Piper                              | Text-to-speech                    |
| Desktop overlay     | PySide6 / Qt initially             | Orb, subtitles, indicators        |
| Web dashboard       | React + TypeScript                 | Management and monitoring UI      |
| Main database       | SQLite                             | Structured persistent information |
| Text search         | SQLite FTS5                        | Keyword and phrase retrieval      |
| Semantic search     | FAISS or equivalent                | Embedding similarity search       |
| Document processing | PyMuPDF, python-docx, ReportLab    | Academic documents and PDFs       |
| Scheduler           | APScheduler                        | Local recurring tasks             |
| Integrations        | Provider adapters                  | Calendar, Drive, future trading   |
| Testing             | pytest + integration tests         | Quality and correctness           |
| Packaging           | Python tooling + Windows installer | Deployment                        |

The model choice remains provisional: `qwen3.5:4b` was the earlier candidate. Before committing to it, verify the model's actual availability, license, hardware requirements, reasoning quality, and tool-calling performance.

The initial implementation uses a modular Python monolith. Distributed deployment is deferred.
