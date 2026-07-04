"""
Citation Completeness Checker — powered by VultronRetrieverFlash (via flash_json).

Checks whether an action has sufficient documentary evidence across required
citation categories. Returns (score, missing_clauses, model_used).

Fail-closed: any error → (0.0, REQUIRED_CLAUSES, model_name) — the action is frozen.
"""
from sentinel.vultr_client import flash_json
from sentinel.config import CONFIG
from sentinel.models import Action

REQUIRED_CLAUSES = [
    "covenant_definition",
    "breach_threshold",
    "historical_trend",
    "transaction_evidence",
]


def check_citation_completeness(action: Action) -> tuple[float, list[str], str]:
    """
    Returns (citation_score, missing_clauses, model_used).
    Fail-closed: any error → (0.0, REQUIRED_CLAUSES, model_name).
    """
    model_name = CONFIG["vultron_flash"]
    cited = [c.clause for c in action.citations] or ["(none)"]

    messages = [
        {"role": "system", "content": "You are a compliance evidence auditor."},
        {"role": "user", "content": f"""Cited clauses: {cited}
Required categories: {REQUIRED_CLAUSES}

Return JSON: {{"covered": [...], "missing": [...], "score": <float 0.0-1.0>}}"""},
    ]

    try:
        result = flash_json(messages)
        score = max(0.0, min(1.0, float(result.get("score", 0.0))))
        return score, result.get("missing", REQUIRED_CLAUSES), model_name
    except Exception:
        return 0.0, REQUIRED_CLAUSES, model_name
