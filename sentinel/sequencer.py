"""
SENTINEL Incident Sequencer
Creates tamper-evident incident records with SHA-256 integrity hashes.
"""
import json
import hashlib
import time
from pathlib import Path
from sentinel.models import Action, ActionStatus, EventType, SentinelEvent
from sentinel.eventbus import emit

INCIDENTS_DIR = Path("incidents")
INCIDENTS_DIR.mkdir(exist_ok=True)


def seal_incident(action: Action) -> dict:
    """
    Seal a frozen action into a tamper-evident incident record.
    
    Args:
        action: The Action object to seal
        
    Returns:
        dict: The complete incident report including integrity_hash
    """
    # Build the incident report
    report = {
        "incident_id": action.action_id,
        "action": {
            "description": action.description,
            "tool_name": action.tool_name,
            "parameters": action.parameters,
            "is_irreversible": action.is_irreversible,
        },
        "citations": [
            {
                "document": citation.document,
                "clause": citation.clause,
                "excerpt": citation.excerpt,
            }
            for citation in action.citations
        ],
        "signals": {
            "drift_score": action.drift_score,
            "drift_model": action.drift_model,
            "maars_verdict": action.maars_verdict,
            "maars_confidence": action.maars_confidence,
            "maars_reasoning": action.maars_reasoning,
            "maars_model": action.maars_model,
            "citation_score": action.citation_score,
            "citation_model": action.citation_model,
        },
        "freeze_reason": action.freeze_reason,
        "operator_decision": action.operator_decision,
        "resolved_at": action.resolved_at,
        "sealed_at": time.time(),
    }
    
    # Compute integrity hash over canonical JSON (sorted keys)
    # Exclude the hash field itself from the computation
    canonical = json.dumps(report, sort_keys=True)
    integrity_hash = hashlib.sha256(canonical.encode()).hexdigest()
    
    # Add hash to report
    report["integrity_hash"] = integrity_hash
    
    # Save to file
    incident_file = INCIDENTS_DIR / f"incident_{action.action_id[:8]}.json"
    with open(incident_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Emit incident sealed event
    event = SentinelEvent(
        event_type=EventType.INCIDENT_SEALED,
        action_id=action.action_id,
        payload={
            "incident_id": action.action_id,
            "incident_file": str(incident_file),
            "integrity_hash": integrity_hash,
            "operator_decision": action.operator_decision,
        }
    )
    emit(event)
    
    return report
