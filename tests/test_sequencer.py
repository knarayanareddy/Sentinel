"""
Tests for the SENTINEL incident sequencer.
Verifies tamper-evident incident records with SHA-256 integrity hashes.
"""
import json
import hashlib
import tempfile
from pathlib import Path
from sentinel.models import Action, ActionStatus, RetrievalCitation
from sentinel.sequencer import seal_incident


def test_hash_is_stable():
    """Verify that the integrity hash can be recomputed and matches."""
    # Create a test action with all signal fields populated
    action = Action(
        description="Test action",
        tool_name="test_tool",
        parameters={"param1": "value1"},
        is_irreversible=True,
        citations=[
            RetrievalCitation(
                document="test_doc.md",
                clause="test_clause",
                excerpt="test excerpt",
            )
        ],
        status=ActionStatus.RESUMED,
        operator_decision="approved",
        resolved_at=1234567890.0,
        drift_score=0.15,
        drift_model="test-model",
        maars_verdict="YES",
        maars_confidence=85,
        maars_reasoning="Test reasoning",
        maars_model="test-model",
        citation_score=0.9,
        citation_model="test-model",
        freeze_reason="test freeze reason",
    )
    
    # Seal the incident
    report = seal_incident(action)
    
    # Recompute the hash over the same data (excluding integrity_hash field)
    report_without_hash = {k: v for k, v in report.items() if k != "integrity_hash"}
    canonical = json.dumps(report_without_hash, sort_keys=True)
    recomputed_hash = hashlib.sha256(canonical.encode()).hexdigest()
    
    # Verify the hash matches
    assert report["integrity_hash"] == recomputed_hash, "Integrity hash does not match"


def test_incident_file_written():
    """Verify that the incident file is actually created on disk."""
    # Use a temporary directory for this test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporarily override INCIDENTS_DIR
        import sentinel.sequencer as seq
        original_dir = seq.INCIDENTS_DIR
        seq.INCIDENTS_DIR = Path(tmpdir)
        
        try:
            # Create a test action
            action = Action(
                description="Test action for file writing",
                tool_name="test_tool",
                is_irreversible=True,
                status=ActionStatus.ABORTED,
                operator_decision="aborted",
            )
            
            # Seal the incident
            report = seal_incident(action)
            
            # Verify file was created
            expected_file = Path(tmpdir) / f"incident_{action.action_id[:8]}.json"
            assert expected_file.exists(), f"Incident file not created: {expected_file}"
            
            # Verify file contents match the report
            with open(expected_file) as f:
                saved_report = json.load(f)
            
            assert saved_report["incident_id"] == action.action_id
            assert saved_report["integrity_hash"] == report["integrity_hash"]
        finally:
            # Restore original INCIDENTS_DIR
            seq.INCIDENTS_DIR = original_dir


def test_report_includes_all_fields():
    """Verify that the incident report includes all required fields."""
    action = Action(
        description="Test action with citations",
        tool_name="test_tool",
        parameters={"key": "value"},
        is_irreversible=True,
        citations=[
            RetrievalCitation(
                document="doc1.md",
                clause="clause1",
                excerpt="excerpt1",
            ),
            RetrievalCitation(
                document="doc2.md",
                clause="clause2",
                excerpt="excerpt2",
            ),
        ],
        status=ActionStatus.RESUMED,
        operator_decision="approved",
        resolved_at=1234567890.0,
        drift_score=0.2,
        drift_model="drift-model",
        maars_verdict="YES",
        maars_confidence=90,
        maars_reasoning="Good reasoning",
        maars_model="maars-model",
        citation_score=0.95,
        citation_model="citation-model",
        freeze_reason="Test freeze reason",
    )
    
    report = seal_incident(action)
    
    # Verify top-level fields
    assert "incident_id" in report
    assert "action" in report
    assert "citations" in report
    assert "signals" in report
    assert "freeze_reason" in report
    assert "operator_decision" in report
    assert "resolved_at" in report
    assert "sealed_at" in report
    assert "integrity_hash" in report
    
    # Verify action fields
    assert report["action"]["description"] == "Test action with citations"
    assert report["action"]["tool_name"] == "test_tool"
    assert report["action"]["parameters"] == {"key": "value"}
    assert report["action"]["is_irreversible"] is True
    
    # Verify citations
    assert len(report["citations"]) == 2
    assert report["citations"][0]["document"] == "doc1.md"
    assert report["citations"][1]["document"] == "doc2.md"
    
    # Verify signals
    signals = report["signals"]
    assert signals["drift_score"] == 0.2
    assert signals["drift_model"] == "drift-model"
    assert signals["maars_verdict"] == "YES"
    assert signals["maars_confidence"] == 90
    assert signals["maars_reasoning"] == "Good reasoning"
    assert signals["maars_model"] == "maars-model"
    assert signals["citation_score"] == 0.95
    assert signals["citation_model"] == "citation-model"


def test_incident_id_format():
    """Verify that the incident_id matches the action_id."""
    action = Action(
        description="Test action",
        tool_name="test_tool",
        is_irreversible=True,
    )
    
    report = seal_incident(action)
    assert report["incident_id"] == action.action_id


def test_integrity_hash_format():
    """Verify that the integrity hash is a valid SHA-256 hex string."""
    action = Action(
        description="Test action",
        tool_name="test_tool",
        is_irreversible=True,
    )
    
    report = seal_incident(action)
    hash_value = report["integrity_hash"]
    
    # SHA-256 produces a 64-character hex string
    assert len(hash_value) == 64, f"Hash length is {len(hash_value)}, expected 64"
    
    # Verify it's a valid hex string
    try:
        int(hash_value, 16)
    except ValueError:
        raise AssertionError(f"Hash is not a valid hex string: {hash_value}")
