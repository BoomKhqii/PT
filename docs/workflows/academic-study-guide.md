# End-to-end example: Academic workflow

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

Consider this request:

> "Hey PT, review my Data Science lectures, identify my weak topics, and generate a PDF study guide with explanations and practice questions."

The workflow would be:

1. Receive input: Capture the spoken command and transcribe it.
2. Classify: Identify the request as an academic document-generation workflow.
3. Resolve context: Identify the relevant Data Science course and current semester.
4. Retrieve performance: Load available question attempts and weak-topic evidence.
5. Retrieve documents: Search indexed lectures, notes, and practice exams, preserving page citations.
6. Create study plan: Prioritize weak topics and determine required explanations, examples, and exercises.
7. Generate content: Produce structured sections with source references and answer keys.
8. Validate: Check topic coverage, citation integrity, question-answer consistency, and document completeness.
9. Render: Generate the PDF in a temporary workspace, inspect the output, then publish it to the approved destination.
10. Respond: Display the file in the dashboard, give its location, and report the actual completion status.

This workflow combines retrieval, persistent state, reasoning, document generation, orchestration, and tool execution.

It also creates measurable outcomes: correct retrieval, useful practice questions, reliable citations, successful file generation, and improved study performance.
