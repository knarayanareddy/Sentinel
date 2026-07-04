import time
from typing import Callable, Optional
from sentinel.models import Action, ActionStatus, SentinelEvent, EventType
from sentinel.eventbus import emit

_action_registry: dict[str, Action] = {}
_freeze_policy: Optional[Callable] = None


def set_freeze_policy(fn: Callable):
    global _freeze_policy
    _freeze_policy = fn


def attempt_action(action: Action) -> Action:
    if action.action_id in _action_registry:
        emit(SentinelEvent(event_type=EventType.ERROR, action_id=action.action_id,
                           payload={"message": "Duplicate action_id — ignoring."}))
        return _action_registry[action.action_id]

    _action_registry[action.action_id] = action
    emit(SentinelEvent(event_type=EventType.ACTION_PROPOSED, action_id=action.action_id,
                       payload={"action": action.description, "tool": action.tool_name,
                                "is_irreversible": action.is_irreversible}))

    should_freeze = action.is_irreversible and _freeze_policy and _freeze_policy(action)

    if should_freeze:
        action.status = ActionStatus.FROZEN
        emit(SentinelEvent(event_type=EventType.ACTION_FROZEN, action_id=action.action_id,
                           payload={"freeze_reason": action.freeze_reason,
                                    "drift_score": action.drift_score,
                                    "maars_verdict": action.maars_verdict,
                                    "maars_confidence": action.maars_confidence,
                                    "citation_score": action.citation_score,
                                    "citations": [{"document": c.document, "clause": c.clause, "excerpt": c.excerpt} for c in action.citations] if action.citations else []}))
    else:
        action.status = ActionStatus.EXECUTED
        emit(SentinelEvent(event_type=EventType.ACTION_EXECUTED, action_id=action.action_id,
                           payload={"action": action.description}))
    return action


def resolve_frozen(action_id: str, approved: bool) -> Action:
    action = _action_registry.get(action_id)
    if not action or action.status != ActionStatus.FROZEN:
        raise ValueError(f"No frozen action with id {action_id}")
    action.status = ActionStatus.RESUMED if approved else ActionStatus.ABORTED
    action.operator_decision = "approved" if approved else "aborted"
    action.resolved_at = time.time()
    emit(SentinelEvent(event_type=EventType.OPERATOR_DECISION, action_id=action_id,
                       payload={"decision": action.operator_decision,
                                "resolved_at": action.resolved_at}))
    return action


def get_action(action_id: str) -> Optional[Action]:
    return _action_registry.get(action_id)
