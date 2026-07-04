def run(ratio, threshold, covenant_context, historical_context, transaction_context) -> str:
    return (
        f"ESCALATION MEMO — COVENANT BREACH DETECTED\n\n"
        f"Current Debt/EBITDA: {ratio:.2f}x (Threshold: {threshold}x)\n\n"
        f"Covenant Reference: {covenant_context[:200]}\n\n"
        f"Historical Context: {historical_context[:200]}\n\n"
        f"Transaction Root Cause: {transaction_context[:200]}\n\n"
        f"[DRAFT — pending operator approval]"
    )
