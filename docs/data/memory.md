# Memory architecture

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

One of PT's distinguishing features should be persistent, user-controlled memory.

However, memory and document retrieval are different problems and should not be implemented as one undifferentiated vector database.

Memory Manager

Retrieval · Consolidation · Correction · Retention rules

Working Memory

Current request, recent turns, workflow state

Episodic Memory

Past interactions, outcomes, completed tasks

Semantic Memory

Approved facts, preferences, projects, goals

Knowledge Index

Lectures, notes, documents, source citations

### Memory lifecycle

```
Conversation / Tool Result
        |
        v
Memory candidate extraction
        |
        v
Relevance + sensitivity classification
        |
        v
Policy / user approval
        |
        v
Store structured memory with provenance
        |
        v
Index for retrieval
        |
        v
Retrieve when relevant
        |
        v
Correction / expiration / deletion
```

Each long-term memory should have a stable ID, source, creation date, last update, confidence or verification status, and retention policy.

A memory about a timetable must not be treated as permanently true. When an updated timetable arrives, PT needs to supersede the earlier record rather than retrieve both as equally authoritative.

The system must support reviewing, correcting, exporting, and deleting memories, including their associated retrieval-index entries.
