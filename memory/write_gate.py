from memory.store import store_memory
import json
import requests

# PT — Conditional Memory Write Trigger & User Fact Updater
WRITE_OFF_TRIGGER_PROMPT = """

## OBJECTIVE

Upgrade PT's existing conditional memory write trigger into a user-fact detection and update system.

The objective is to allow PT to gradually build and maintain an accurate, personalized understanding of the user across conversations.

PT should identify relevant information about the user even when they do not explicitly say "Remember this."

Examples:

- The user mentions their university or occupation.
- The user expresses a communication preference.
- The user changes a career objective.
- The user introduces a new project.
- The user changes an existing technical preference.
- The user mentions a recurring routine.
- The user updates their availability.

The system must distinguish between temporary conversational information and meaningful information that improves future interactions.

The system must support:

1. Explicit memory requests.
2. Automatic user-fact detection.
3. Existing fact updates.
4. Significant event detection.
5. Periodic memory consolidation.
6. Historical fact tracking.
7. Memory deduplication and conflict resolution.

Do not execute expensive memory extraction after every user message.

Prioritize memory accuracy, personalization, low latency, and maintainability.

## 1. INSPECT THE EXISTING IMPLEMENTATION

Before making modifications:

1. Inspect PT's conversation pipeline.
2. Identify how working memory is maintained.
3. Examine the existing memory manager and memory store.
4. Inspect the existing write trigger implementation.
5. Identify the current SQLite database schema.
6. Identify existing memory scopes and classifications.
7. Inspect the memory retrieval service.
8. Determine whether embeddings are already implemented.
9. Inspect existing LLM tool-calling and structured-output capabilities.
10. Identify existing asynchronous execution and background processing.

Do not assume these components already exist.

Reuse existing implementations wherever appropriate.

Avoid restructuring unrelated components.

## 2. MEMORY CLASSIFICATION

PT must distinguish between different types of information.

### A. User Profile Facts

Relatively stable information about the user that helps PT personalize its responses.

Examples:

- Educational background.
- Occupation and professional background.
- General location and timezone.
- Preferred language.
- Technical background.
- Communication preferences.
- Learning preferences.
- Long-term interests.

These facts should be maintained as an updatable user profile.

### B. Preferences

Information describing how the user prefers things to be done.

Examples:

- Preferred response length.
- Preferred explanation style.
- Preferred programming languages.
- Preferred development tools.
- Preferred working environment.
- Preferred study methods.
- Preferred scheduling arrangements.

Preferences should be specific enough to be useful.

Do not assume that a preference in one context applies universally.

### C. Goals and Priorities

Information describing what the user wants to accomplish.

Examples:

- Career objectives.
- Academic objectives.
- Financial or business objectives.
- Personal development goals.
- Short-term and long-term priorities.
- Project milestones.

Track changes in priorities rather than creating duplicate records.

### D. Skills and Experience

Information about the user's technical and professional capabilities.

Examples:

- Programming languages.
- Frameworks and technologies.
- Academic subjects.
- Professional experience.
- Certifications.
- Technical proficiency.
- Areas currently being learned.

Distinguish between beginner, intermediate, and advanced proficiency only when supported by explicit information or sufficient evidence.

Do not exaggerate the user's capabilities.

### E. Active Projects

Information about ongoing projects.

Examples:

- Project purpose.
- Technology stack.
- Architecture.
- Development status.
- Important technical decisions.
- Current blockers.
- Next milestones.
- Project priorities.

Keep project information organized and update existing records when the architecture or development direction changes.

### F. Routines and Availability

Information about recurring patterns.

Examples:

- Working hours.
- Study schedules.
- Preferred working periods.
- Recurring commitments.
- Availability.
- Quiet hours.
- Regular activities.

Time-sensitive schedules must have appropriate validity periods.

### G. Constraints and Resources

Information that affects recommendations and decisions.

Examples:

- Available hardware.
- Operating system.
- Development environment.
- Budget limitations.
- Time constraints.
- Software limitations.
- Internet availability.
- Technical dependencies.

Do not assume that temporary constraints are permanent.

### H. Interests and Recurring Topics

Identify subjects the user consistently engages with.

Examples:

- Artificial intelligence.
- Software engineering.
- Quantitative research.
- Algorithmic trading.
- Entrepreneurship.
- Academic subjects.

Do not infer a permanent interest from one isolated question.

Repeated engagement may create a candidate for confirmation or future profile consolidation.

### I. Important Decisions and Experiences

Maintain relevant information about:

- Confirmed decisions.
- Changes in direction.
- Previous approaches.
- Lessons learned.
- Significant outcomes.
- Resolved problems.
- Unresolved issues.

Preserve historical context when it explains the user's current decisions.

## 3. MEMORY WRITE TRIGGER

Create a lightweight, event-driven mechanism that determines when information should be evaluated for long-term storage.

Separate the following operations:

- Working memory updates: Every conversational turn.
- Conversation history persistence: Every turn or appropriate batch.
- User-fact evaluation: When a potentially relevant fact is detected.
- Long-term memory consolidation: When explicitly requested or triggered by significant events.
- Memory retrieval: When relevant information is needed for a response.

The trigger must not automatically execute expensive LLM-based extraction after every message.

Support the following independent trigger pathways.

### A. Explicit Memory Requests

Recognize direct instructions to:

- Remember information.
- Save information.
- Update an existing memory.
- Correct an existing fact.
- Forget information.
- Delete stored information.

Examples:

"Remember that I prefer Python."

"Update my career goal to AI Engineer."

"Forget my previous project priority."

"Don't save that information."

Route each request to the appropriate memory operation.

Do not interpret retrieval questions such as "Do you remember my project?" as requests to save information.

Explicit requests must receive appropriate confirmation after the operation has been verified.

### B. Automatic User-Fact Detection

This is a primary requirement.

PT should identify potentially useful user facts from ordinary conversation without requiring an explicit memory instruction.

Examples:

User:
"I'm currently studying Computer Science at Western Sydney University."

Candidate:
"The user is studying Computer Science at Western Sydney University."

User:
"I prefer explanations that walk me through the reasoning rather than just giving me the answer."

Candidate:
"The user prefers step-by-step explanations that emphasize reasoning."

User:
"I'm planning to focus on AI engineering for my career."

Candidate:
"The user's current career objective is to pursue AI engineering."

User:
"I've decided to use PostgreSQL instead of SQLite for this project."

Candidate:
"The project database decision has changed from SQLite to PostgreSQL."

User:
"I'm currently developing a personal AI assistant using Python and LangGraph."

Candidate:
"The user is developing a personal AI assistant using Python and LangGraph."

Automatic fact detection must:

- Identify information directly stated by the user.
- Determine whether it is relevant to future personalization.
- Identify the appropriate fact category and scope.
- Check whether the fact already exists.
- Determine whether it updates an existing fact.
- Preserve relevant contextual information.
- Avoid extracting unrelated information from the same message.
- Avoid turning temporary statements into permanent facts.
- Avoid storing unsupported assumptions.

Do not require the phrase "remember this" for automatic user-fact evaluation.

However, do not automatically store every statement.

### C. Significant Information Events

Allow memory evaluation when meaningful events occur.

Examples:

- A confirmed change in project architecture.
- A finalized long-term goal.
- A significant change in availability.
- A confirmed change in technical preferences.
- Completion of an important milestone.
- A change in academic or professional circumstances.
- A significant decision that affects future recommendations.

Prefer structured application events and existing main LLM decisions over additional classification calls.

A significant event initiates memory evaluation, not unconditional storage.

### D. Periodic Memory Consolidation

Support configurable consolidation of recent conversational context.

Possible triggers:

- A configurable number of conversation turns.
- End of a conversation session.
- Completion of a significant project milestone.
- A meaningful change in an ongoing project.

Consolidation should identify useful information that was not previously captured.

Prevent repeated processing of the same conversation segments.

Maintain processing checkpoints where appropriate.

## 4. USER FACT CATEGORIZATION

Use a consistent fact taxonomy.

Recommended categories:

- profile
- communication_preference
- learning_preference
- skill
- interest
- goal
- priority
- project
- routine
- availability
- constraint
- technical_environment
- domain_preference
- decision
- experience
- commitment

Use the existing memory scopes:

academic:
- Educational background.
- Courses and academic progress.
- Study preferences.
- Academic goals.
- Academic schedules.

personal:
- General user profile.
- Communication preferences.
- Personal goals.
- Professional context.
- Interests.
- Routines.
- Availability.
- Personal constraints.

trading:
- Trading preferences.
- Trading-related goals.
- Strategy configurations.
- Risk management preferences.
- Quantitative research decisions.

shared:
- Information relevant across multiple PT modules.
- PT architecture and project-wide decisions.
- Shared system preferences.
- General configurations.

Use the most specific appropriate scope.

Do not classify every user fact as shared.

Do not confuse facts about PT's architecture with facts about the user's personal profile.

## 5. FACT UPDATE AND UPSERT LOGIC

The system must update existing facts rather than continually inserting duplicate records.

Before saving a candidate:

1. Identify its category.
2. Identify its logical fact key.
3. Retrieve existing facts with the same key or meaning.
4. Compare the new information against existing records.
5. Determine whether it is new, unchanged, updated, conflicting, or temporary.
6. Select the appropriate operation.

Supported operations:

INSERT:
Create a new fact when no equivalent active fact exists.

UPDATE:
Update an existing fact when the user provides a clear correction or change.

NO-OP:
Do nothing when the information is already accurately stored.

SUPERSEDE:
Mark an older fact as superseded when a newer fact replaces it.

PENDING CONFIRMATION:
Hold an ambiguous or contradictory candidate without treating it as verified.

Examples:

Existing:
"The user is learning C#."

New:
"The user is now learning Python."

Action:
INSERT, because both facts can be true.

Existing:
"The user prefers detailed explanations."

New:
"I now prefer concise answers."

Action:
UPDATE or SUPERSEDE if the new preference is intended to replace the old one.

Existing:
"The user's current project priority is the Academic Agent."

New:
"The user has decided to prioritize the Trading Agent instead."

Action:
Update the current priority and preserve the previous decision as historical context where useful.

Do not automatically interpret every new statement as a contradiction.

A change in context may allow multiple preferences or facts to coexist.

## 6. FACT METADATA AND TEMPORAL ACCURACY

Preserve useful metadata for each fact.

Where supported by the existing architecture, maintain:

- Fact ID.
- User ID or profile identifier.
- Memory scope.
- Fact category.
- Fact key.
- Fact value.
- Source message or evidence reference.
- Source timestamp.
- Creation timestamp.
- Last update timestamp.
- Last confirmed timestamp.
- Valid-from date.
- Valid-until date.
- Current status.
- Superseded fact reference.
- Whether the information was explicitly stated or user-confirmed.

Distinguish between:

- Current facts.
- Historical facts.
- Temporary facts.
- Expired facts.
- Unverified candidates.

Examples:

A career objective may remain valid until the user changes it.

A semester timetable should expire when the semester ends or when a replacement timetable is confirmed.

A temporary work schedule should not be treated as a permanent availability preference.

Resolve relative dates using the actual system date and the user's configured timezone.

Do not invent missing dates.

## 7. MEMORY WRITE CLASSIFICATION

Inspect the existing LLM capabilities before implementing classification.

Use the following priority:

1. Deterministic detection for explicit commands and structured events.
2. Existing main LLM structured output or tool calling for relevant implicit fact candidates.
3. Conditional semantic classification when the previous methods cannot reliably resolve a potentially useful fact.

Avoid introducing a separate LLM call after every message.

Where possible, allow the existing response LLM to propose a structured memory update as part of its existing inference.

If the existing model does not support suitable tool calling or structured output, implement conditional evaluation only when a lightweight trigger identifies a potentially meaningful message.

Do not use a rigid keyword-only system.

The system must understand contextual statements and follow-up corrections.

## 8. STRUCTURED FACT CANDIDATE OUTPUT

Return exactly one JSON object. Do not include Markdown, code fences,
or explanations outside the JSON.

### Action domain

"action" must be one of these exact lowercase strings:

- "upsert": Save a fact that the user has clearly stated or confirmed.
  SQLite will insert or update the row using scope and fact_key.
- "no_op": There is no new or changed fact to save.
- "pending_confirmation": The fact or the intended memory is unclear.
- "supersede": A new fact replaces an older fact that should be preserved
  as history. This action does not write until history support is available.

Set "should_evaluate" to true only for "upsert".
For all other actions, set "should_evaluate" to false.

### Fields for an upsert

- "should_evaluate": true
- "action": "upsert"
- "scope": "general", "personal", "academic", "trading", or "shared"
- "fact_type": a short label describing the kind of fact
- "fact_key": a stable key identifying the specific memory within its scope
- "fact": a complete, standalone sentence containing the information to save
- "source": "explicit_user_request", "user_stated", "user_confirmed",
  or "structured_application_event"
- "valid_until": null unless the user provides a clear expiration date

Always put the actual memory text in "fact". Do not substitute
"current_value", "previous_fact", "value", or "content".

Reuse the existing scope and fact_key when correcting the same memory.
Use distinct keys for facts that should coexist, such as attendance at
two different schools.

### Example

User: Remember that I studied at Lourdes School of Mandaluyong.

{
    "should_evaluate": true,
    "action": "upsert",
    "scope": "personal",
    "fact_type": "education_background",
    "fact_key": "school_attended_lourdes_school_of_mandaluyong",
    "fact": "The user studied at Lourdes School of Mandaluyong.",
    "source": "explicit_user_request",
    "valid_until": null
}

When there is nothing to save, return:
{"should_evaluate": false, "action": "no_op"}

For pending_confirmation or supersede, return the same two fields
with the corresponding action.

## 9. MEMORY MANAGER

The Memory Manager coordinates the lifecycle of user facts.

Responsibilities:

- Receive candidate facts.
- Validate extracted information.
- Check the appropriate memory scope.
- Check whether information is useful for future personalization.
- Detect duplicates.
- Detect changes to existing facts.
- Handle contradictions.
- Determine insert, update, no-op, or supersede operations.
- Maintain temporal validity.
- Coordinate database persistence.
- Coordinate semantic index updates.
- Handle memory correction and deletion requests.

The Memory Manager must not blindly trust the classifier.

All candidate facts must be validated before persistence.

## 10. MEMORY STORE

The Memory Store is responsible for database operations.

Responsibilities:

- Save new facts.
- Update existing facts.
- Retrieve existing facts.
- Mark historical facts as superseded.
- Expire temporary facts.
- Delete authorized memories.
- Preserve metadata.
- Return verifiable operation results.

Inspect the existing SQLite schema.

Consider whether a dedicated user_facts table is appropriate alongside episodic memories.

A possible logical separation is:

user_facts:
Current user profile, preferences, goals, skills, constraints, and project facts.

episodic_memories:
Important past decisions, interactions, outcomes, and experiences.

conversation_history:
Original conversation records.

Do not create redundant tables if the existing schema already supports these distinctions.

Keep original source references where practical.

## 11. PERSONALIZATION REQUIREMENTS

The ultimate purpose of automatic user-fact updates is to improve PT's future responses.

Retrieved facts should help PT:

- Adjust explanation complexity.
- Adapt communication style.
- Understand the user's technical experience.
- Recognize ongoing projects.
- Remember current priorities.
- Avoid recommending technologies that conflict with established constraints.
- Account for available time and resources.
- Understand academic and professional context.
- Maintain continuity across conversations.
- Provide recommendations consistent with confirmed preferences.

Do not inject every stored fact into every prompt.

Retrieve only information relevant to the current request.

Use recency, relevance, source reliability, and temporal validity when selecting facts.

A stored fact must not override a newer explicit user statement.

## 12. PRIVACY AND MEMORY SAFETY

Do not automatically store:

- Passwords and API keys.
- Authentication tokens.
- Full bank or payment card details.
- Government identification numbers.
- Sensitive personal information.
- Unnecessary private information about third parties.
- Unverified personal assumptions.

Do not infer sensitive personal characteristics.

Require appropriate explicit authorization for sensitive information where storage is permitted by PT's privacy policy.

Respect instructions such as:

- "Don't remember that."
- "Forget that information."
- "Update my profile."
- "That's no longer accurate."

Support user review, correction, and deletion of stored facts.

A memory classifier's positive result is not sufficient authorization to bypass privacy rules.

## 13. RETRIEVAL INTEGRATION

Keep the read path separate from the write path.

The Retrieval Service should:

- Retrieve relevant user facts.
- Retrieve relevant episodic memories.
- Filter expired or superseded facts.
- Return source and timestamp information.
- Provide relevant context to the Context Builder.

The Context Builder should select only relevant information for the current LLM request.

Do not perform memory retrieval merely because a write trigger executes.

Do not confuse user-profile retrieval with academic document RAG.

## 14. PERFORMANCE REQUIREMENTS

- Update working memory every conversational turn.
- Persist conversation history according to the existing design.
- Avoid unconditional memory classification LLM calls.
- Reuse existing model tool-calling capabilities where possible.
- Keep optional consolidation asynchronous.
- Keep explicit memory requests reliable.
- Avoid unnecessary embedding generation.
- Update semantic indexes only when indexed content changes.
- Prevent duplicate jobs.
- Avoid repeated processing of the same messages.
- Use existing background execution infrastructure.
- Do not introduce Redis, Celery, or unnecessary services.

Optional memory processing must not unnecessarily delay normal conversation responses.

Explicit save, correction, and deletion requests must be verified before confirmation.

## 15. TESTING AND VALIDATION

Test the following:

1. Explicit memory requests are detected.
2. Ordinary statements containing useful user facts can trigger evaluation.
3. Ordinary factual questions do not trigger memory writes.
4. Communication preferences can be stored and updated.
5. Goals and priorities can be updated.
6. Project architecture changes update existing facts appropriately.
7. New skills do not overwrite unrelated skills.
8. Temporary facts receive appropriate validity periods.
9. Expired facts are not treated as current.
10. Duplicate facts are not repeatedly inserted.
11. Ambiguous contradictions are not silently overwritten.
12. Historical facts remain distinguishable from current facts.
13. Sensitive information is not automatically stored.
14. Explicit deletion requests reach the deletion workflow.
15. Normal conversational responses do not require an additional classifier call on every turn.
16. Existing memories can be retrieved after application restart.
17. Semantic indexes are updated only when necessary.
18. Database failures never produce false success confirmations.
19. Retrieval excludes superseded or expired facts where appropriate.
20. Contextual corrections update the correct existing fact.

Use actual test results.

Do not fabricate accuracy or performance measurements.

## 16. IMPLEMENTATION CONSTRAINTS

- Inspect the existing implementation before making changes.
- Preserve existing architecture wherever possible.
- Keep modifications limited to memory-related components and necessary integration points.
- Reuse the existing main LLM where appropriate.
- Reuse existing SQLite infrastructure.
- Do not introduce a second LLM unnecessarily.
- Do not introduce a vector database solely for fact updates.
- Do not refactor unrelated agents.
- Maintain backward compatibility where feasible.
- Document important architectural decisions.
- Use structured logging and appropriate error handling.
- Do not assume LangGraph is required for every memory operation.
- Use existing orchestration capabilities where appropriate.

Before modifying files, present the proposed changes and obtain my approval.

After approval, implement only the approved scope.

## 17. DELIVERABLES

Provide:

1. Analysis of the existing memory architecture.
2. Explanation of the proposed automatic user-fact detection mechanism.
3. Recommended user-fact categories.
4. Explanation of how existing facts will be updated rather than duplicated.
5. Proposed database schema changes, if necessary.
6. Explanation of current versus historical fact handling.
7. Files that need modifications.
8. Performance and privacy considerations.
9. Implementation and integration plan.
10. Tests and actual verification results.
11. Remaining limitations.

## PRIMARY OBJECTIVE

Build a conditional memory system that continuously develops an accurate and useful understanding of the user.

PT should not merely store isolated conversations.

It should maintain a structured, evolving user profile that captures relevant preferences, goals, skills, projects, constraints, routines, and important decisions.

The system must recognize new information, update outdated facts, preserve meaningful history, and retrieve relevant context when needed.

Prioritize accuracy, relevance, temporal correctness, privacy, and low-latency operation.

The ultimate goal is to make PT increasingly personalized through reliable memory management rather than indiscriminate information storage.

"""
MODEL = "qwen3.5:4b"

def write_path_trigger(message, history_snapshot):
    print("Write path trigger activated for message:", repr(message))
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": [
                { "role": "system", "content": WRITE_OFF_TRIGGER_PROMPT },
                *history_snapshot,
                { "role": "user", "content": message },
            ],
            "think": False, # skips the thinking step and returns the answer directly
            "format": "json",
            "stream": False
        },
        timeout=120
    )
    response.raise_for_status()
    generatedJson = json.loads(response.json()["message"]["content"])
    #decision = json.loads(generatedJson)

    print("Write path trigger output:", repr(generatedJson))
    # Issue: it prints in the middle of the user's input
    # Remember to redirect this block to a separate thread to avoid blocking the main conversation flow (Front-end wise)
    if store_memory(generatedJson) is not True:
         return
    print(
        f"[PT] Memory saved: "
        f"action: {generatedJson['action']}, "
        f"category: {generatedJson['scope']}, "
        f"content: {generatedJson['fact']}, "
        f"source: {generatedJson['source']}, "
        f"valid_until: {generatedJson.get('valid_until')}"
    )