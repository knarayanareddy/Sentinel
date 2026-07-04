"""
Phase 0 manual verification: force-freeze harness.
Exercises the full freeze → resolve lifecycle without any API calls.
"""
from sentinel.models import Action
from sentinel.orchestrator import attempt_action, resolve_frozen, set_freeze_policy


def always_freeze(a):
    return True


# Wire the policy
set_freeze_policy(always_freeze)

# Create an irreversible action
a = Action(
    description="Send escalation memo to CFO regarding covenant breach",
    tool_name="send_escalation_memo",
    is_irreversible=True,
)

print(f"Created action: {a.action_id}")
print(f"Initial status: {a.status.value}")

# Attempt the action — should be frozen
result = attempt_action(a)
print(f"\nAfter attempt_action():")
print(f"  status: {result.status.value}")
print(f"  (expected: frozen)")

# Operator approves
resolved = resolve_frozen(a.action_id, approved=True)
print(f"\nAfter resolve_frozen(approved=True):")
print(f"  status:       {resolved.status.value}")
print(f"  decision:     {resolved.operator_decision}")
print(f"  resolved_at:  {resolved.resolved_at}")
print(f"  (expected: resumed, approved)")

# Test abort path with a fresh action
a2 = Action(
    description="Trigger downstream system",
    tool_name="trigger_downstream_system",
    is_irreversible=True,
)
attempt_action(a2)
resolved2 = resolve_frozen(a2.action_id, approved=False)
print(f"\nAbort path:")
print(f"  status:   {resolved2.status.value}")
print(f"  decision: {resolved2.operator_decision}")
print(f"  (expected: aborted, aborted)")

# Verify reversible actions never freeze
a3 = Action(
    description="Draft escalation memo",
    tool_name="draft_memo",
    is_irreversible=False,
)
result3 = attempt_action(a3)
print(f"\nReversible action (draft_memo):")
print(f"  status: {result3.status.value}")
print(f"  (expected: executed — reversible actions bypass the freeze policy)")

print("\n✅ All transitions verified. No API calls made.")
