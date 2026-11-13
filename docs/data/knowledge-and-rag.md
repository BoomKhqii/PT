# Document intelligence and RAG

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

RAG stands for Retrieval-Augmented Generation. It allows PT to locate relevant information from stored materials before asking the LLM to produce an answer.

### Ingestion pipeline

```text
Source document -> Extract text / OCR when needed -> Chunk with source metadata
                -> Generate embeddings -> Store text and metadata -> Index for retrieval
```

This is a textual reconstruction of the ingestion flow; the original pasted diagram was browser styling.

Source identifiers must travel with every chunk. For lecture PDFs, record the lecture, section, page, extraction quality, and document version.

### Retrieval pipeline

```
User question
     |
     v
Query normalization
     |
     +--> Full-text search (FTS5)
     |
     +--> Semantic similarity search
     |
     v
Merge and deduplicate results
     |
     v
Rerank relevant evidence
     |
     v
Fetch source excerpts + metadata
     |
     v
Grounded LLM response
     |
     v
Return explanation + page citations
```

The design uses SQLite FTS5 for full-text search.

For your academic use case, the system should prefer original lecture material when asked what a lecturer taught. It should distinguish that from general explanations based on model knowledge.

Scanned PDFs may require an OCR fallback, while slides containing charts, diagrams, and tables may need separate visual extraction. Plain-text chunking alone will not reliably preserve every figure.
