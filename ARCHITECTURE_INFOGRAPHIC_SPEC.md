# Architecture Infographic — Design Spec

Instructions for designing the infographic you'll include with the LinkedIn post. Target: a clean, single-image architecture diagram that reads well on LinkedIn mobile + desktop.

## Dimensions & Format

- **Aspect ratio:** 1.91:1 (LinkedIn preview-optimized). 1200 × 628 pixels is the sweet spot.
- **Format:** PNG with a white or light-neutral background. Avoid dark themes on LinkedIn — readability tanks on mobile.
- **Font:** Inter, IBM Plex Sans, or Segoe UI. System-safe and clean.

## Content Layout (Left-to-Right Flow)

```
┌────────────────┐       ┌────────────────┐       ┌──────────────────┐       ┌─────────────┐       ┌──────────┐
│    INPUT       │ ────► │   NORMALIZE    │ ────► │  HYBRID ROUTER   │ ────► │  TEMPLATE   │ ────► │  OUTPUT  │
│                │       │                │       │                  │       │  RENDERER   │       │          │
│  • Teams VTT   │       │  Strip         │       │  ┌──────────┐    │       │             │       │  • .md   │
│  • .srt        │       │  timestamps /  │       │  │  LOCAL   │    │       │  Jinja2     │       │  • .json │
│  • .txt        │       │  cue IDs,      │       │  │  Ollama  │    │       │  (your      │       │          │
│  • .json       │       │  keep speaker  │       │  │  Gemma / │    │       │  template)  │       │  Stays   │
│  • Paste       │       │  + content     │       │  │  Llama / │    │       │             │       │  on your │
│                │       │                │       │  │  Mistral │    │       │             │       │  disk.   │
│                │       │                │       │  └────┬─────┘    │       │             │       │          │
│                │       │                │       │       │          │       │             │       │          │
│                │       │                │       │       ▼          │       │             │       │          │
│                │       │                │       │  ┌──────────┐    │       │             │       │          │
│                │       │                │       │  │  CLOUD   │    │       │             │       │          │
│                │       │                │       │  │  Claude /│    │       │             │       │          │
│                │       │                │       │  │  OpenAI /│    │       │             │       │          │
│                │       │                │       │  │  Azure   │    │       │             │       │          │
│                │       │                │       │  └──────────┘    │       │             │       │          │
│                │       │                │       │                  │       │             │       │          │
│                │       │                │       │  local-first  or │       │             │       │          │
│                │       │                │       │  cloud-first     │       │             │       │          │
│                │       │                │       │  failover        │       │             │       │          │
└────────────────┘       └────────────────┘       └──────────────────┘       └─────────────┘       └──────────┘
```

## Color Palette

Use the same hues as your hybrid-llm-deployment-guide for visual consistency:

- **Local components** (Normalize, Ollama, disk output): warm gold/amber — e.g. `#FBC02D` fills with `#B7950B` borders
- **Cloud components** (Claude/OpenAI/Azure): cool blue — e.g. `#E1F5FE` fills with `#01579B` borders
- **Routing/orchestration** (the Hybrid Router box): neutral white with a thick dark border — `#FFFFFF` fill, `#333` 3px stroke
- **Input/Output boxes**: soft green — `#C8E6C9` fill with `#2E7D32` borders

## Annotations / Callouts

Add three small annotation blocks around the diagram:

### Top-left callout (near INPUT)
> "Your transcript — Teams, Zoom, anywhere"

### Top-right callout (near OUTPUT)
> "Your template — totally customizable"
> *Shows a tiny sample markdown snippet with `{{ summary }}` syntax*

### Bottom callout (under HYBRID ROUTER)
> "Local-only, cloud-only, or hybrid — one codebase serves all three"

## Headline / Title Bar

Top of image:
> **hybrid-meeting-notes**
> Local-first meeting intelligence with hybrid LLM routing

Bottom of image (small):
> github.com/HarmanSingh-CCG/hybrid-meeting-notes  •  MIT licensed

## What NOT to Include

- No company logos (Microsoft, Anthropic, OpenAI) — legal + messy
- No emoji
- No screenshot of actual notes output — save that for a second slide if you do a carousel
- No metrics (ms latency, $ savings) — those are LinkedIn post text, not image
- No animated elements

## Recommended Tools

- **Canva** — fastest, templates exist for 1.91:1 LinkedIn posts
- **Excalidraw** — if you want the hand-drawn look (matches open-source / technical feel)
- **Figma** — most control, slowest
- **draw.io / diagrams.net** — free, functional but less polished

## Alternative: Carousel (5 slides)

If you want to maximize engagement, a LinkedIn carousel hits harder than a single image:

1. **Slide 1 — Hook:** "Meeting intelligence SaaS is $10-20/user/mo. Here's the open-source alternative." With the architecture diagram as the hero.
2. **Slide 2 — The problem:** "Your transcripts are currently going through someone else's servers." Simple split-screen: SaaS (data leaves) vs Local (data stays).
3. **Slide 3 — The architecture:** The main diagram from above.
4. **Slide 4 — The flexibility:** Screenshot of a template file with `{{ placeholders }}` next to rendered markdown output.
5. **Slide 5 — CTA:** "Take it, fork it, make it yours. github.com/HarmanSingh-CCG/hybrid-meeting-notes"

Carousels get ~3x the dwell time of single images on LinkedIn.
