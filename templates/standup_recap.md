# Standup Recap — {{ meeting.date }}

{% if meeting.attendees %}Team: {{ meeting.attendees | join(", ") }}{% endif %}

## What Shipped / Progress
{% if summary.topics %}
{% for t in summary.topics %}
**{{ t.topic }}**
{% for b in t.bullets %}
- {{ b }}
{% endfor %}

{% endfor %}
{% else %}
_No progress notes_
{% endif %}

## Today / Next Up
{% if action_items %}
{% for a in action_items %}
- {{ a.owner or "UNCLEAR" }}: {{ a.action }}{% if a.due %} ({{ a.due }}){% endif %}
{% endfor %}
{% else %}
_No actions captured_
{% endif %}

## Blockers
{% if open_questions %}
{% for q in open_questions %}
- {{ q }}
{% endfor %}
{% else %}
_None flagged_
{% endif %}

---
_{{ generated_at }} • via {{ provider_used }}_
