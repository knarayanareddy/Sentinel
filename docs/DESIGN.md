# SENTINEL — Design Specification

## Tokens
Background #0D0D0D, text #F2F0EB.
Status: FROZEN #E53935, EXECUTED #2E7D32, PENDING #F9A825,
        ABORTED #546E7A, RESUMED #1565C0.
Display: IBM Plex Mono. Body: Inter 400/500 only.
Borders 1px, radius ≤4px. No gradients, no shadows, no blur.

## Screen Map

Screen 1 — Live Agent Monitor
  - Event stream, newest first
  - RETRIEVAL_PASS rows show pass number, documents retrieved, and
    reasoning_model badge (e.g. "VultronRetrieverPrime")
  - TOOL_CALLED rows show tool name + result
  - ACTION_FROZEN row: full-width red takeover

Screen 2 — Signal Breakdown (on freeze)
  - Three cards: Covenant Drift (Core model badge), MAARS Verdict (Prime
    model badge), Citation Score (Flash model badge)
  - Each card shows: score, reasoning, and which VultronRetriever tier ran it
  - Citations list below with document/clause/excerpt/retrieval_score

Screen 3 — Operator Gate + Incident Record
  - APPROVE (green, full-width) / ABORT (red outline, same weight)
  - Incident JSON preview + SHA-256 hash, labelled explicitly
  - Model attribution footer: "Reasoning by VultronRetrieverPrime/Core/Flash
    via Vultr Serverless Inference"

## Impeccable Workflow
  impeccable build --product docs/PRODUCT.md --design docs/DESIGN.md <component>
  impeccable critique --product docs/PRODUCT.md --design docs/DESIGN.md --visual
  impeccable audit --product docs/PRODUCT.md --design docs/DESIGN.md

## Non-Negotiables
- Freeze visible within 200ms of event
- Every signal card shows its VultronRetriever model attribution
- Citations visible by default
- Operator buttons full-width, equal visual weight
- Incident hash visible, labelled "SHA-256", copyable
