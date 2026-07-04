def run(ratio, threshold, covenant_context, historical_context, transaction_context,
        breach: bool = True) -> str:
    if breach:
        header = "ESCALATION MEMO — COVENANT BREACH DETECTED"
        cause = f"Transaction Root Cause: {transaction_context[:200]}\n\n"
    else:
        header = "COMPLIANCE CONFIRMATION MEMO — COVENANT WITHIN THRESHOLD"
        cause = ""
    return (
        f"{header}\n\n"
        f"Current Debt/EBITDA: {ratio:.2f}x (Threshold: {threshold}x)\n\n"
        f"Covenant Reference: {covenant_context[:200]}\n\n"
        f"Historical Context: {historical_context[:200]}\n\n"
        f"{cause}"
        f"[DRAFT — pending operator approval]"
    )
