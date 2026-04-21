# {{ meeting.title }} — Executive Brief

**{{ meeting.date }} • {{ meeting.duration }}**
{% if meeting.attendees %}_Attendees: {{ meeting.attendees | join(", ") }}_{% endif %}

## Bottom Line
{{ summary.one_liner or "_No summary_" }}

## Decisions
{% if decisions %}
{% for d in decisions %}
- **{{ d.decision }}**{% if d.decided_by %} _(— {{ d.decided_by }})_{% endif %}
{% endfor %}
{% else %}
_None_
{% endif %}

## Action Items (Top 5)
{% if action_items %}
{% for a in action_items[:5] %}
- **{{ a.owner or "UNCLEAR" }}** → {{ a.action }}{% if a.due %} _(by {{ a.due }})_{% endif %}
{% endfor %}
{% else %}
_None_
{% endif %}

## Open Risks / Questions
{% if open_questions %}
{% for q in open_questions %}
- {{ q }}
{% endfor %}
{% else %}
_None flagged_
{% endif %}

---
_Processed by {{ provider_used }} • {{ generated_at }}_
