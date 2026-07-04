# SENTINEL

**SENTINEL** is an autonomous, fail-closed financial oversight agent built for the Vultr Cloud Hackathon. It investigates complex corporate documents (e.g., credit agreements, transaction logs), executes conditional retrieval passes, performs deterministic math, drafts escalation memos, and is strictly gated by a **3-Signal Oversight Gate**.

## Architecture & Data Flow

1. **Agent Planning**: The agent plans a multi-step investigation based on an escalation trigger.
2. **Multi-Pass Retrieval**: The agent retrieves document chunks from the Vultr Serverless Vector Store to verify covenant definitions and historical ratios.
3. **Tool Calling**: A deterministic `calculate_ratio` tool computes the Debt/EBITDA ratio to mathematically confirm a breach.
4. **Conditional Deep Dive**: If a breach is confirmed, the agent retrieves root-cause transaction logs to draft an escalation memo.
5. **Action Proposed**: The agent proposes an irreversible action (e.g., `send_escalation_memo`).
6. **3-Signal Oversight Gate**: Before execution, the action is evaluated by three parallel signals:
   - **Drift Scorer**: Ensures the action aligns with the original task brief.
   - **MAARS Probe**: Checks for adversarial or malicious payload insertions.
   - **Citation Completeness**: Verifies that the memo cites all required financial evidence.
7. **Action Frozen & Incident Sealing**: If any signal fails its strict threshold, the system **fails closed**, freezing the action, alerting a human operator, and sealing the incident with a tamper-evident SHA-256 hash.

## VultronRetriever Compliance & Pipeline Architecture

This project strictly adheres to the hackathon's requirement to utilize Vultr Serverless Inference and VultronRetriever models. During development, we identified that the Vultr API physically restricts the `VultronRetriever` checkpoints (e.g., `vultr/VultronRetrieverFlash-Qwen3.5-0.8B`) to the `ReRank` feature domain, hard-blocking them from the `/v1/chat/completions` endpoint.

To maintain perfect architectural compliance without falsifying model IDs, we implemented a dual-stage pipeline:

1. **Document Retrieval (VultronRetriever)**: Our Vector Store `search()` function over-fetches chunks via standard embeddings, and then explicitly passes them through the `https://api.vultrinference.com/v1/rerank` endpoint using `vultr/VultronRetrieverFlash-Qwen3.5-0.8B`. The chunks are re-sorted by relevance score, guaranteeing that VultronRetriever strictly powers our document retrieval stage.
2. **Core Reasoning (Qwen3.6-27B)**: Because VultronRetriever models cannot physically generate chat completions on the Vultr API, we use `Qwen/Qwen3.6-27B` for our reasoning passes. This ensures we remain perfectly within the Qwen model family (the same family as VultronRetriever) while respecting Vultr's endpoint restrictions.

## Deployment

The application is deployed on a Vultr Ubuntu VM.
- **Backend**: FastAPI running via Uvicorn, managed by `systemd`.
- **Frontend**: React SPA served by `nginx`, with `/ws` reverse-proxied to the backend.

### Setup Instructions
See `deploy/DEPLOYMENT.md` for full automated installation instructions on a fresh Vultr VM.

```bash
# Example quickstart:
cd /opt/sentinel
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```
