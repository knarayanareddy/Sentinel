"""
MAARS — Multi-pass Adversarial Action Review System.
Powered by VultronRetrieverPrime (via prime_json).

Adversarial review of a proposed action before execution. Returns a verdict
(YES/NO), confidence, reasoning, severity, and remediation.

Fail-closed: any error or malformed response → verdict=NO, confidence=0.
"""
import json
from pathlib import Path
from sentinel.vultr_client import prime_json
from sentinel.config import CONFIG

# Load the MAARS prompt template from docs/
_TEMPLATE_PATH = Path(__file__).parent.parent / "docs" / "probe_prompt_template.md"
_TEMPLATE = _TEMPLATE_PATH.read_text()

REQUIRED_KEYS = {"verdict", "confidence", "reasoning", "severity", "remediation"}
VALID_VERDICTS = {"YES", "NO"}


def run_probe(action, drift_score: float, drifted: bool) -> dict:
    """
    Run the MAARS adversarial probe on a proposed action.

    Returns a dict with:
      - verdict: "YES" or "NO"
      - confidence: int 0-100
      - reasoning: str (specific, evidence-grounded)
      - severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
      - remediation: str (if NO: specific step; if YES: empty string)
      - model: str (the model used)

    Fail-closed: any error → verdict=NO, confidence=0.
    """
    model_name = CONFIG["vultron_prime"]
    _FALLBACK = {
        "verdict": "NO",
        "confidence": 0,
        "reasoning": "Probe failed to return valid JSON — failing closed.",
        "severity": "HIGH",
        "remediation": "Investigate probe failure.",
        "model": model_name,
    }

    # Format the prompt with action details
    prompt = _TEMPLATE.format(
        action_description=action.description,
        tool_name=action.tool_name,
        parameters_json=json.dumps(action.parameters, indent=2),
        citations_json=json.dumps(
            [
                {"document": c.document, "clause": c.clause, "excerpt": c.excerpt}
                for c in action.citations
            ],
            indent=2,
        ),
        drift_score=round(drift_score, 3),
        drift_threshold=CONFIG["drift_threshold"],
        drifted=drifted,
    )

    try:
        result = prime_json([{"role": "user", "content": prompt}])
    except Exception:
        return _FALLBACK

    # Validate the response structure
    if not isinstance(result, dict):
        return _FALLBACK

    if not REQUIRED_KEYS.issubset(result.keys()):
        return _FALLBACK

    if result.get("verdict") not in VALID_VERDICTS:
        return _FALLBACK

    # Confidence must be an integer 0-100
    confidence = result.get("confidence")
    if not isinstance(confidence, int):
        # Try to convert from float or string
        try:
            confidence = int(float(confidence))
            result["confidence"] = confidence
        except (ValueError, TypeError):
            return _FALLBACK

    if not (0 <= confidence <= 100):
        return _FALLBACK

    # Reasoning must be non-empty
    if not result.get("reasoning", "").strip():
        return _FALLBACK

    # Enforce confidence threshold: below MAARS_CONFIDENCE_MIN → force NO
    if result["confidence"] < CONFIG["maars_confidence_min"]:
        result["verdict"] = "NO"

    result["model"] = model_name
    return result
