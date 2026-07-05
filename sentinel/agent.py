"""
SENTINEL Agent — Full 7-Step Enterprise Agent Loop.

This is the core autonomous agent that:
1. Plans an investigation
2. Retrieves covenant definition from vector store
3. Retrieves historical ratio trend
4. Calls deterministic ratio calculation tool
5. CONDITIONALLY retrieves transaction root cause (only if breach detected)
6. Synthesises an escalation memo (reversible)
7. Attempts to send the memo (irreversible → SENTINEL gate fires)

Step 5 is the key differentiator — it proves non-trivial, multi-step
retrieval behaviour beyond basic retrieve-then-answer.
"""
import time
import threading
from sentinel.models import Action, RetrievalCitation, SentinelEvent, EventType
from sentinel.eventbus import emit
from sentinel.vultr_client import prime_text
from sentinel.vector_store import search
import sentinel.orchestrator as orchestrator
from sentinel.tools import calculate_ratio, draft_memo
from sentinel.config import CONFIG

SCENARIOS = {
    "breach": {
        "label": "Q2 FY2025 — covenant breach",
        "debt": 462_000_000,
        "ebitda": 100_000_000,
    },
    "compliant": {
        "label": "Q3 FY2023 — compliant quarter",
        "debt": 430_000_000,
        "ebitda": 100_000_000,
    },
}

TASK_BRIEF = """
You are a covenant monitoring agent for a corporate finance team.
Your task: analyse the Debt/EBITDA covenant in the credit agreement,
assess whether the borrower is in breach based on current filings,
identify the root cause from recent transactions, and prepare an
escalation memo if a breach is detected.
"""


def run_agent(scenario: str = "breach"):
    """Start the agent loop in a background daemon thread."""
    thread = threading.Thread(target=_agent_loop, args=(scenario,), daemon=True)
    thread.start()
    return thread


def _reason_over(query: str, chunks) -> str:
    """
    Inject retrieved chunks as context into a Prime model call.
    This makes the reasoning attribution explicit — the model sees
    the raw documents and reasons over them.
    """
    # Build context from chunks — use content preview as label since
    # vector store results may have empty description fields
    context_parts = []
    for i, c in enumerate(chunks):
        label = c.description if c.description else f"Document {i + 1}"
        context_parts.append(f"[{label}]\n{c.content}")

    context = "\n\n".join(context_parts)

    return prime_text([
        {"role": "system", "content": TASK_BRIEF},
        {"role": "user", "content": (
            f"Retrieved context:\n\n{context}\n\n"
            f"Query: {query}\n\n"
            f"Summarise the relevant findings concisely."
        )},
    ])


def _agent_loop(scenario: str = "breach"):
    """
    The full 7-step agent loop.
    Each step emits an event via the EventBus for real-time UI updates.
    """
    financials = SCENARIOS.get(scenario, SCENARIOS["breach"])
    print(f"[AGENT] Scenario: {financials['label']}")

    emit(SentinelEvent(
        event_type=EventType.RUN_STARTED,
        payload={"scenario": scenario, "label": financials["label"]},
    ))

    print("[AGENT] Step 1: Planning investigation...")

    # ── Step 1: PLAN ──
    plan = prime_text([
        {"role": "system", "content": TASK_BRIEF},
        {"role": "user", "content": (
            "List the steps you will take to investigate a potential "
            "covenant breach. Return a numbered list."
        )},
    ])
    emit(SentinelEvent(
        event_type=EventType.AGENT_PLAN,
        payload={
            "steps": [s.strip() for s in plan.split("\n") if s.strip()],
            "model": CONFIG["reasoning_prime"],
        },
    ))
    time.sleep(1.0)

    # ── Step 2: RETRIEVE-1 — covenant definition ──
    print("[AGENT] Step 2: Retrieving covenant definition...")
    chunks_1, rerank_model = search(
        "Debt/EBITDA covenant threshold and breach conditions", top_k=3
    )
    r1 = _reason_over(
        "What is the covenant threshold and how is it defined?", chunks_1
    )
    emit(SentinelEvent(
        event_type=EventType.RETRIEVAL_PASS,
        payload={
            "pass_number": 1,
            "query": "Covenant definition",
            "documents_retrieved": [
                c.description or f"chunk_{i}" for i, c in enumerate(chunks_1)
            ],
            "reasoning_model": CONFIG["reasoning_prime"],
            "rerank_model": rerank_model,
            "result_summary": r1[:200],
        },
    ))
    time.sleep(1.0)

    # ── Step 3: RETRIEVE-2 — historical trend ──
    print("[AGENT] Step 3: Retrieving historical ratio trend...")
    chunks_2, rerank_model = search(
        "historical Debt/EBITDA ratio trend past 8 quarters", top_k=3
    )
    r2 = _reason_over("What is the historical ratio trend?", chunks_2)
    emit(SentinelEvent(
        event_type=EventType.RETRIEVAL_PASS,
        payload={
            "pass_number": 2,
            "query": "Historical ratio trend",
            "documents_retrieved": [
                c.description or f"chunk_{i}" for i, c in enumerate(chunks_2)
            ],
            "reasoning_model": CONFIG["reasoning_prime"],
            "rerank_model": rerank_model,
            "result_summary": r2[:200],
        },
    ))
    time.sleep(1.0)

    # ── Step 4: TOOL-CALL — deterministic ratio calculation ──
    print("[AGENT] Step 4: Calculating Debt/EBITDA ratio...")
    ratio_result = calculate_ratio.run(
        debt=financials["debt"], ebitda=financials["ebitda"]
    )
    emit(SentinelEvent(
        event_type=EventType.TOOL_CALLED,
        payload={
            "tool_name": "calculate_ratio",
            "parameters": {
                "debt": financials["debt"],
                "ebitda": financials["ebitda"],
            },
            "result_summary": (
                f"Debt/EBITDA = {ratio_result['ratio']:.2f}x "
                f"(threshold: 4.5x)"
            ),
        },
    ))
    time.sleep(1.0)

    # ── Step 5: RETRIEVE-3 — CONDITIONAL on breach ──
    breach_detected = ratio_result["ratio"] > 4.5
    r3, chunks_3 = "", []
    if breach_detected:
        print(f"[AGENT] Step 5: BREACH DETECTED ({ratio_result['ratio']:.2f}x > 4.5x). "
              f"Retrieving transaction root cause...")
        chunks_3, rerank_model = search(
            "transactions contributing to Q2 EBITDA decline", top_k=3
        )
        r3 = _reason_over(
            "Which transactions explain the decline?", chunks_3
        )
        emit(SentinelEvent(
            event_type=EventType.RETRIEVAL_PASS,
            payload={
                "pass_number": 3,
                "query": "Transaction root cause",
                "documents_retrieved": [
                    c.description or f"chunk_{i}"
                    for i, c in enumerate(chunks_3)
                ],
                "reasoning_model": CONFIG["reasoning_prime"],
                "rerank_model": rerank_model,
                "result_summary": r3[:200],
            },
        ))
        time.sleep(1.0)
    else:
        print(f"[AGENT] Step 5: No breach ({ratio_result['ratio']:.2f}x <= 4.5x). "
              f"Skipping conditional retrieval.")

    # ── Step 6: SYNTHESISE — draft memo (reversible) ──
    print("[AGENT] Step 6: Drafting memo...")
    memo_text = draft_memo.run(
        ratio=ratio_result["ratio"],
        threshold=4.5,
        covenant_context=r1,
        historical_context=r2,
        transaction_context=r3,
        breach=breach_detected,
    )
    memo_action = Action(
        description=(
            "Draft escalation memo for compliance team"
            if breach_detected
            else "Draft compliance confirmation memo"
        ),
        tool_name="draft_memo",
        parameters={"ratio": ratio_result["ratio"]},
        is_irreversible=False,
        citations=[
            RetrievalCitation(
                "credit_agreement.md",
                "§4.2 Debt/EBITDA Covenant",
                r1[:80],
            ),
            RetrievalCitation(
                "historical_ratios.md",
                "Q1–Q8 Trend",
                r2[:80],
            ),
            RetrievalCitation(
                "recent_transactions.md",
                "Q2 Transaction Anomalies",
                r3[:80] if r3 else "(not retrieved — no breach)",
            ),
        ],
    )
    orchestrator.attempt_action(memo_action)
    time.sleep(1.0)

    # ── Step 7: ACT — irreversible, SENTINEL gate fires ──
    if breach_detected:
        print("[AGENT] Step 7: Attempting to send escalation memo...")
        print("[AGENT] SENTINEL gate will evaluate this action.")
        send_action = Action(
            description=(
                f"Send escalation memo to CFO and legal team. "
                f"Debt/EBITDA ratio is {ratio_result['ratio']:.2f}x, "
                f"breaching the 4.5x covenant threshold (§4.2). "
                f"Root cause identified in Q2 transactions."
            ),
            tool_name="send_escalation_memo",
            parameters={
                "recipient": "cfo@example.com",
                "memo": memo_text[:100],
            },
            is_irreversible=True,
            citations=[
                RetrievalCitation(
                    "credit_agreement.md",
                    "covenant_definition",
                    r1[:80],
                ),
                RetrievalCitation(
                    "historical_ratios.md",
                    "historical_trend",
                    r2[:80],
                ),
                RetrievalCitation(
                    "recent_transactions.md",
                    "transaction_evidence",
                    r3[:80],
                ),
            ],
        )
        orchestrator.attempt_action(send_action)
    else:
        print("[AGENT] Step 7: No breach. Sending compliance confirmation memo...")
        print("[AGENT] SENTINEL gate will evaluate this action.")
        confirm_action = Action(
            description=(
                f"Send quarterly compliance confirmation memo to the compliance team. "
                f"Debt/EBITDA ratio is {ratio_result['ratio']:.2f}x, within the "
                f"4.5x covenant threshold (§4.2). No escalation required."
            ),
            tool_name="send_confirmation_memo",
            parameters={
                "recipient": "compliance@example.com",
                "memo": memo_text,
            },
            is_irreversible=True,
            citations=[
                RetrievalCitation(
                    "credit_agreement.md",
                    "covenant_definition",
                    r1[:80],
                ),
                RetrievalCitation(
                    "credit_agreement.md",
                    "breach_threshold",
                    "The Borrower shall not permit the ratio of Consolidated Total Debt to "
                    "Consolidated EBITDA to exceed 4.50 to 1.00",
                ),
                RetrievalCitation(
                    "historical_ratios.md",
                    "historical_trend",
                    r2[:80],
                ),
            ],
        )
        orchestrator.attempt_action(confirm_action)
    print("[AGENT] Agent loop complete.")
