"""
Tests for the citation completeness checker.
Uses unittest.mock.patch to mock flash_json — no live API calls.
"""
from unittest.mock import patch
from sentinel.models import Action, RetrievalCitation
from sentinel.citations import check_citation_completeness, REQUIRED_CLAUSES


@patch("sentinel.citations.flash_json")
def test_no_citations_fail_closed(mock_flash):
    """When the model call fails, citations should fail closed (score=0.0)."""
    mock_flash.side_effect = Exception("simulated failure")
    a = Action(
        description="send memo",
        tool_name="send_escalation_memo",
        is_irreversible=True,
    )
    score, missing, model = check_citation_completeness(a)
    assert score == 0.0
    assert missing == REQUIRED_CLAUSES
    assert model  # model name should still be populated


@patch("sentinel.citations.flash_json")
def test_full_citations_high_score(mock_flash):
    """When all clauses are covered, score should be 1.0."""
    mock_flash.return_value = {
        "covered": REQUIRED_CLAUSES,
        "missing": [],
        "score": 1.0,
    }
    a = Action(
        description="send memo",
        tool_name="send_escalation_memo",
        is_irreversible=True,
        citations=[
            RetrievalCitation("credit_agreement.md", c, "...")
            for c in REQUIRED_CLAUSES
        ],
    )
    score, missing, model = check_citation_completeness(a)
    assert score == 1.0
    assert missing == []


@patch("sentinel.citations.flash_json")
def test_partial_citations_mid_score(mock_flash):
    """When some clauses are covered, score should be between 0 and 1."""
    mock_flash.return_value = {
        "covered": ["covenant_definition"],
        "missing": ["breach_threshold", "historical_trend", "transaction_evidence"],
        "score": 0.25,
    }
    a = Action(
        description="send memo",
        tool_name="send_escalation_memo",
        is_irreversible=True,
        citations=[
            RetrievalCitation("credit_agreement.md", "covenant_definition", "...")
        ],
    )
    score, missing, model = check_citation_completeness(a)
    assert score == 0.25
    assert len(missing) == 3
    assert "covenant_definition" not in missing


@patch("sentinel.citations.flash_json")
def test_model_returns_garbage_score_clamped(mock_flash):
    """When the model returns a score outside [0,1], it should be clamped."""
    mock_flash.return_value = {
        "covered": [],
        "missing": REQUIRED_CLAUSES,
        "score": 2.5,  # out of range
    }
    a = Action(
        description="send memo",
        tool_name="send_escalation_memo",
        is_irreversible=True,
    )
    score, missing, model = check_citation_completeness(a)
    assert score == 1.0  # clamped to 1.0
