#!/usr/bin/env python3
"""
Test script to verify the /api/decide endpoint and incident sealing.
This simulates the full flow: freeze action → approve/abort → seal incident.
"""
import os
import sys

# Set environment variables BEFORE any sentinel imports
os.environ["VULTR_API_KEY"] = "test-key-for-phase4"
os.environ["VULTRON_PRIME_MODEL"] = "test/prime-model"
os.environ["VULTRON_CORE_MODEL"] = "test/core-model"
os.environ["VULTRON_FLASH_MODEL"] = "test/flash-model"
os.environ["SANDBOX_EMAIL_SINK"] = "mailhog"
os.environ["SENTINEL_ENV"] = "demo"

from sentinel.models import Action, ActionStatus, RetrievalCitation, EventType
from sentinel.orchestrator import attempt_action, resolve_frozen, set_freeze_policy, get_action
from sentinel.sequencer import seal_incident
from sentinel.eventbus import subscribe

# Track events
events_received = []

def event_handler(event):
    events_received.append(event)
    print(f"[EVENT] {event.event_type.value}")

subscribe("*", event_handler)

print("=" * 80)
print("PHASE 4 TEST: /api/decide Endpoint + Incident Sealing")
print("=" * 80)
print()

# Set up a freeze policy that always freezes irreversible actions
def always_freeze(action):
    if action.is_irreversible:
        action.freeze_reason = "Test freeze policy: irreversible action"
        action.drift_score = 0.15
        action.drift_model = "test-drift-model"
        action.maars_verdict = "YES"
        action.maars_confidence = 85
        action.maars_reasoning = "Test MAARS reasoning"
        action.maars_model = "test-maars-model"
        action.citation_score = 0.90
        action.citation_model = "test-citation-model"
        return True
    return False

set_freeze_policy(always_freeze)

print("[1/3] Creating frozen action with citations...")
action = Action(
    description="Send escalation memo to CFO",
    tool_name="send_escalation_memo",
    parameters={"recipient": "cfo@example.com", "memo": "Breach detected"},
    is_irreversible=True,
    citations=[
        RetrievalCitation(
            document="credit_agreement.md",
            clause="§4.2 Debt/EBITDA Covenant",
            excerpt="Maximum Leverage Ratio: 4.50 to 1.00",
        ),
        RetrievalCitation(
            document="historical_ratios.md",
            clause="Q1 FY2025 Ratio",
            excerpt="Debt/EBITDA: 4.62x (BREACH)",
        ),
    ],
)

result = attempt_action(action)
print(f"Action status: {result.status.value}")
print(f"Action ID: {result.action_id}")
print(f"Freeze reason: {result.freeze_reason}")
print()

print("[2/3] Approving action (simulating /api/decide with approved=true)...")
resolved = resolve_frozen(result.action_id, approved=True)
print(f"Resolved status: {resolved.status.value}")
print(f"Operator decision: {resolved.operator_decision}")
print(f"Resolved at: {resolved.resolved_at}")
print()

print("[3/3] Sealing incident...")
report = seal_incident(resolved)
print(f"Incident ID: {report['incident_id']}")
print(f"Integrity hash: {report['integrity_hash']}")
print(f"Sealed at: {report['sealed_at']}")
print()

print("=" * 80)
print("VERIFICATION RESULTS")
print("=" * 80)
print()

# Verify the incident report
checks = {
    "incident_id matches action_id": report['incident_id'] == action.action_id,
    "integrity_hash is 64 chars": len(report['integrity_hash']) == 64,
    "action details preserved": report['action']['description'] == action.description,
    "citations preserved": len(report['citations']) == 2,
    "signals preserved": report['signals']['drift_score'] == 0.15,
    "operator decision recorded": report['operator_decision'] == 'approved',
    "resolved_at recorded": report['resolved_at'] is not None,
    "sealed_at recorded": report['sealed_at'] is not None,
}

all_pass = True
for check_name, check_result in checks.items():
    status = "✓" if check_result else "✗"
    print(f"  {status} {check_name}")
    if not check_result:
        all_pass = False

print()

# Verify incident file was created
import json
from pathlib import Path

incident_file = Path("incidents") / f"incident_{action.action_id[:8]}.json"
if incident_file.exists():
    print(f"✓ Incident file created: {incident_file}")
    with open(incident_file) as f:
        saved_report = json.load(f)
    
    # Verify the saved hash matches
    if saved_report['integrity_hash'] == report['integrity_hash']:
        print("✓ Saved integrity hash matches returned hash")
    else:
        print("✗ Saved integrity hash does NOT match")
        all_pass = False
    
    # Verify we can recompute the hash
    import hashlib
    report_without_hash = {k: v for k, v in saved_report.items() if k != 'integrity_hash'}
    canonical = json.dumps(report_without_hash, sort_keys=True)
    recomputed = hashlib.sha256(canonical.encode()).hexdigest()
    
    if recomputed == saved_report['integrity_hash']:
        print("✓ Integrity hash is stable (can be recomputed)")
    else:
        print("✗ Integrity hash is NOT stable")
        all_pass = False
else:
    print(f"✗ Incident file NOT created: {incident_file}")
    all_pass = False

print()
print("=" * 80)
if all_pass:
    print("✅ PHASE 4 TEST PASSED - Incident sealing works correctly!")
else:
    print("❌ PHASE 4 TEST FAILED - See verification results above")
print("=" * 80)
