# 05 — Custom Output Templates

Different meetings need different outputs. A client workshop deserves a formal document with commitments and numbers. A daily standup deserves a one-page recap. hybrid-meeting-notes ships with four templates out of the box, and you can write your own in under 10 minutes.

## Built-In Templates

| Template | Best For |
|---|---|
| `templates/detailed_notes.md` | Default — comprehensive notes for most meetings |
| `templates/executive_brief.md` | C-suite readouts, board prep — bottom-line first |
| `templates/standup_recap.md` | Daily standups, short team syncs |
| `templates/client_meeting.md` | Client workshops, sales calls, external meetings |

Select a template via config:
```yaml
template: ./templates/executive_brief.md
```

Or env:
```bash
MEETING_TEMPLATE=./templates/executive_brief.md
```

## Writing Your Own

Templates are [Jinja2](https://jinja.palletsprojects.com/) markdown files. Create a new `.md` file in `templates/` and reference it in config.

### Available Variables

```
{{ meeting.title }}                   meeting title
{{ meeting.date }}                    ISO date
{{ meeting.duration }}                e.g. "1h 12m"
{{ meeting.attendees }}               list of strings
{{ meeting.organizer }}
{{ meeting.client }}                  optional
{{ meeting.project }}                 optional
{{ meeting.meeting_type }}            optional

{{ summary.one_liner }}               single-sentence TL;DR
{{ summary.topics }}                  list of {topic, bullets}

{{ action_items }}                    list of {owner, action, due}
{{ decisions }}                       list of {decision, decided_by}
{{ open_questions }}                  list of strings

{{ context.people_mentioned }}
{{ context.organizations_mentioned }}
{{ context.projects_mentioned }}
{{ context.numeric_values_mentioned }}

{{ provider_used }}                   which LLM produced this
{{ generated_at }}                    UTC timestamp string
```

### Example: Sales Call Template

```markdown
# {{ meeting.client }} — Sales Call Notes

**{{ meeting.date }} • {{ meeting.duration }}**

## Prospect's Priorities
{% for t in summary.topics %}
- **{{ t.topic }}**: {{ t.bullets | join('; ') }}
{% endfor %}

## Commitments Made
{% for a in action_items %}
- {{ a.owner }}: {{ a.action }} ({{ a.due or "TBD" }})
{% endfor %}

## Dollar Amounts Discussed
{{ context.numeric_values_mentioned | join(", ") or "None" }}

## Next Steps / Open Questions
{% for q in open_questions %}
- {{ q }}
{% endfor %}
```

Save as `templates/sales_call.md`, set `template: ./templates/sales_call.md`, done.

### Using Conditionals

Jinja2 supports `{% if %}...{% endif %}` blocks for clean handling of missing data:

```markdown
{% if meeting.client %}
**Client:** {{ meeting.client }}
{% endif %}

{% if action_items %}
## Action Items
{% for a in action_items %}
- {{ a.owner }}: {{ a.action }}
{% endfor %}
{% else %}
_No action items this meeting._
{% endif %}
```

### Filters

Common Jinja2 filters work out of the box:
- `| join(", ")` — concatenate a list
- `| default("—")` — fallback value
- `| upper` / `| lower` / `| title`
- `| length` — list size

## Sharing Templates

If you write a template you think others would like, PRs welcome. Drop it in `templates/` with a comment header explaining what kind of meeting it's for.
