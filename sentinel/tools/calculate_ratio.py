def run(debt: float, ebitda: float) -> dict:
    ratio = debt / ebitda if ebitda != 0 else float("inf")
    return {
        "ratio": round(ratio, 2),
        "debt": debt,
        "ebitda": ebitda,
        "breaches_covenant": ratio > 4.5,
    }
