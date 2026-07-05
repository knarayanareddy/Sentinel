"""
SentinelPipeline — The compound OR-gate policy for action approval.

Wires together three signal modules:
  1. Covenant Drift Scorer (Core model)
  2. MAARS Adversarial Probe (Prime model)
  3. Citation Completeness Checker (Flash model)

Any one signal triggering → action is frozen. This is the oversight gate
that prevents irreversible actions from executing without human review.
"""
from sentinel.models import Action, SentinelEvent, EventType
from sentinel.eventbus import emit
from sentinel.drift import score_drift, set_task_brief
from sentinel.probe import run_probe
from sentinel.citations import check_citation_completeness
from sentinel.config import CONFIG
import sentinel.orchestrator as orchestrator


class SentinelPipeline:
    """
    The Sentinel oversight pipeline.

    Initializes the task brief and registers the compound freeze policy
    with the orchestrator. Every irreversible action will be evaluated
    by all three signal modules before execution.
    """

    def __init__(self, task_brief: str):
        """
        Initialize the pipeline with a task brief and register the
        compound freeze policy with the orchestrator.
        """
        set_task_brief(task_brief)
        orchestrator.set_freeze_policy(self._compound_policy)

    def _compound_policy(self, action: Action) -> bool:
        """
        Evaluate all three signals for an action.

        Returns True if the action should be frozen (any signal triggered),
        False if the action can proceed.

        Each signal is evaluated independently and emits its own event.
        All signals run regardless of whether earlier signals triggered,
        so the operator sees the full picture.
        """
        triggers = []

        # ── Signal 1: Covenant Drift (Core model) ──
        drifted, drift_score, drift_model = score_drift(action.description)
        action.drift_score = drift_score
        action.drift_model = drift_model
        emit(
            SentinelEvent(
                event_type=EventType.DRIFT_SCORED,
                action_id=action.action_id,
                payload={
                    "score": drift_score,
                    "drifted": drifted,
                    "threshold": CONFIG["drift_threshold"],
                    "model": drift_model,
                },
            )
        )
        if drifted:
            triggers.append(f"drift_score={drift_score:.2f} exceeds threshold")

        # ── Signal 2: MAARS Adversarial Probe (Prime model) ──
        verdict = run_probe(action, drift_score, drifted)
        action.maars_verdict = verdict["verdict"]
        action.maars_confidence = verdict["confidence"]
        action.maars_reasoning = verdict["reasoning"]
        action.maars_model = verdict.get("model")
        emit(
            SentinelEvent(
                event_type=EventType.MAARS_PROBE,
                action_id=action.action_id,
                payload=verdict,
            )
        )
        if verdict["verdict"] != "YES":
            triggers.append(
                f"MAARS verdict=NO confidence={verdict['confidence']}"
            )

        # ── Signal 3: Citation Completeness (Flash model) ──
        citation_score, missing, citation_model = check_citation_completeness(
            action
        )
        action.citation_score = citation_score
        action.citation_model = citation_model
        emit(
            SentinelEvent(
                event_type=EventType.CITATION_CHECKED,
                action_id=action.action_id,
                payload={
                    "score": citation_score,
                    "missing_clauses": missing,
                    "model": citation_model,
                },
            )
        )
        if citation_score < CONFIG["citation_threshold"]:
            triggers.append(
                f"citation_score={citation_score:.2f} below threshold; missing: {missing}"
            )

        # ── Compound OR-gate decision ──
        if triggers:
            action.freeze_reason = " | ".join(triggers)
            return True
        return False
