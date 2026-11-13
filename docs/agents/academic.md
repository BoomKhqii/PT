# Academic Agent — first major release

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

Purpose: Manage university knowledge and academic productivity.

Academic Supervisor

Select workflow · Manage academic context · Verify results

Knowledge

Lectures, PDFs, search

Study

Tutoring, quizzes, grading

Documents

PDFs, notes, reports

Planning

Exams, tasks, reminders

Its capabilities include:

| Capability             | Implementation                         |
| ---------------------- | -------------------------------------- |
| Import lectures        | PDF/document ingestion pipeline        |
| Recall information     | Hybrid retrieval + cited evidence      |
| Explain concepts       | LLM with grounded context              |
| Create study materials | Study workflow + document renderer     |
| Generate mock exams    | Question generator + rubric manager    |
| Grade responses        | Rubric-based evaluation with feedback  |
| Track weaknesses       | Performance database and topic mastery |
| Manage assessments     | Calendar and task integrations         |
| Generate PDFs          | Structured content + PDF renderer      |
| Progress tracking      | Assignment and assessment records      |

For example, PT could maintain a knowledge hierarchy of `University -> Unit -> Semester -> Module -> Lecture -> Topic -> Source`.

It could associate a student's incorrect answer with a topic, retrieve the original lecture explanation, provide another practice question, and update mastery estimates.
