from sentinel.models import Action
from sentinel.orchestrator import attempt_action, resolve_frozen, set_freeze_policy


def always_freeze(a):
    return True


def test_reversible_never_frozen():
    set_freeze_policy(always_freeze)
    a = Action(description="fetch doc", tool_name="retrieve", is_irreversible=False)
    assert attempt_action(a).status.value == "executed"


def test_irreversible_frozen_by_policy():
    set_freeze_policy(always_freeze)
    a = Action(description="send memo", tool_name="send_escalation_memo",
               is_irreversible=True)
    assert attempt_action(a).status.value == "frozen"


def test_idempotency():
    a = Action(description="send memo", tool_name="send_escalation_memo",
               is_irreversible=True)
    r1, r2 = attempt_action(a), attempt_action(a)
    assert r1.action_id == r2.action_id


def test_operator_approve():
    set_freeze_policy(always_freeze)
    a = Action(description="send memo", tool_name="send_escalation_memo",
               is_irreversible=True)
    attempt_action(a)
    r = resolve_frozen(a.action_id, approved=True)
    assert r.status.value == "resumed" and r.operator_decision == "approved"


def test_operator_abort():
    set_freeze_policy(always_freeze)
    a = Action(description="send memo", tool_name="send_escalation_memo",
               is_irreversible=True)
    attempt_action(a)
    assert resolve_frozen(a.action_id, approved=False).status.value == "aborted"
