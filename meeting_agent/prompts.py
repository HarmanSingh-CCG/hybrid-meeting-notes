"""LLM prompt templates for meeting note enhancement.

Kept generic so users can run this against any meeting transcript — sales
calls, standups, client workshops, internal reviews, 1:1s, etc.
"""

SYSTEM_PROMPT = """You are a meeting intelligence assistant. You analyze meeting transcripts and produce structured notes.

Output rules:
1. Return STRICT JSON matching the schema provided. No preamble, no markdown fences, no trailing commentary.
2. Summary topics are topic-bucketed, not chronological.
3. Action items must have a clear owner. If unclear, set owner to "UNCLEAR".
4. Decisions only count if explicitly stated. Do not infer.
5. Extract dollar amounts and numeric figures verbatim (e.g., "$478K", "50k/month", "Q3 2026").
6. Do not editorialize. Report what was said.
7. If the transcript is ambiguous or the content sparse, return empty arrays rather than fabricating entries.
"""


USER_PROMPT_TEMPLATE = """Meeting metadata:
- Title: {title}
- Date: {date}
- Duration: {duration}
- Attendees: {attendees}

Transcript:
---
{transcript}
---

Produce notes as JSON matching this exact schema:
{{
  "summary": {{
    "one_liner": "<single-sentence summary>",
    "topics": [
      {{"topic": "<topic name>", "bullets": ["<point 1>", "<point 2>"]}}
    ]
  }},
  "action_items": [
    {{"owner": "<name or UNCLEAR>", "action": "<what>", "due": "<when or null>"}}
  ],
  "decisions": [
    {{"decision": "<what was decided>", "decided_by": "<who>"}}
  ],
  "open_questions": ["<unresolved question>"],
  "context": {{
    "people_mentioned": [],
    "organizations_mentioned": [],
    "projects_mentioned": [],
    "numeric_values_mentioned": []
  }}
}}"""


# Map-reduce for long transcripts

CHUNK_PROMPT_TEMPLATE = """This is chunk {chunk_index} of {chunk_total} from a meeting transcript.
Extract notes from THIS CHUNK ONLY in the same JSON schema.

Context from earlier chunks (for continuity):
{prior_context}

Chunk transcript:
---
{chunk}
---

Return JSON only."""


REDUCE_PROMPT_TEMPLATE = """You have {chunk_count} JSON note objects from sequential chunks
of the same meeting. Merge them into a single consolidated JSON object using the same schema.

Rules:
- Deduplicate topics (merge bullets under the same topic name)
- Deduplicate action items (same owner + same action = one entry)
- Preserve ALL decisions and open questions
- Union all context arrays, deduplicated

Chunk outputs:
---
{chunk_outputs}
---

Return consolidated JSON only."""
