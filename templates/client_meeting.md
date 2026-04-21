# Client Meeting — {{ meeting.client or meeting.title }}

| Field | Value |
|---|---|
| **Client** | {{ meeting.client or "—" }} |
| **Project** | {{ meeting.project or "—" }} |
| **Date** | {{ meeting.date }} |
| **Duration** | {{ meeting.duration }} |
| **Attendees** | {{ meeting.attendees | join(", ") or "—" }} |

## Executive Summary
{{ summary.one_liner }}

## What We Discussed
{% for t in summary.topics %}
### {{ t.topic }}
{% for b in t.bullets %}
- {{ b }}
{% endfor %}

{% endfor %}

## Decisions & Commitments
{% if decisions %}
| # | Decision | Owner |
|---|---|---|
{% for d in decisions %}
| {{ loop.index }} | {{ d.decision }} | {{ d.decided_by or "—" }} |
{% endfor %}
{% else %}
_No decisions recorded_
{% endif %}

## Our Follow-Ups
{% if action_items %}
{% for a in action_items %}
- [ ] **{{ a.owner or "UNCLEAR" }}** — {{ a.action }}{% if a.due %} _(due {{ a.due }})_{% endif %}
{% endfor %}
{% else %}
_No follow-ups captured_
{% endif %}

## Open Questions for Client
{% if open_questions %}
{% for q in open_questions %}
{{ loop.index }}. {{ q }}
{% endfor %}
{% else %}
_None_
{% endif %}

## Numbers Mentioned
{{ (context.numeric_values_mentioned or []) | join(", ") or "_None_" }}

---
_Draft — review before sending. Processed by {{ provider_used }} at {{ generated_at }}._
