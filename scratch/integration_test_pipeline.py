#!/usr/bin/env python3
"""
Phase 2 Integration Test — Pipeline with Thin Citations.

This script exercises the full SentinelPipeline with a deliberately
thin-citation action to verify that the compound OR-gate correctly
freezes the action. All three model tiers should be invoked.

Run from the project root:
    python scratch/integration_test_pipeline.py
"""
import os
import sys

# Ensure .env is loaded
from dotenv import load_dotenv
load_dotenv()

from sentinel.models import Action, RetrievalCitation
from sentinel.pipeline import SentinelPipeline
import sentinel.orchestrator as orch

print("=" * 60)
print("SENTINEL PHASE 2 — PIPELINE INTEGRATION TEST")
print("=" * 60)
print()
print("Setting up pipeline with task brief...")
print()

# Initialize the pipeline
TASK_BRIEF = "Monitor covenant breach in credit agreement per §4.2"
SentinelPipeline(task_brief=TASK_BRIEF)

# Create an action with deliberately thin citations (only 1 of 4 required)
a = Action(
    description="Send escalation memo to CFO regarding covenant breach",
    tool_name="send_escalation_memo",
    is_irreversible=True,
    citations=[
        RetrievalCitation(
            "credit_agreement.md",
            "covenant_definition",
            "Debt/EBITDA <= 4.5x",
        )
    ],
)

print(f"Action ID: {a.action_id}")
print(f"Description: {a.description}")
print(f"Is irreversible: {a.is_irreversible}")
print(f"Citations: {len(a.citations)} (only 1 of 4 required)")
print()
print("Running through pipeline (this will call all 3 model tiers)...")
print()

result = orch.attempt_action(a)

print()
print("=" * 60)
print("RESULTS")
print("=" * 60)
print()
print(f"Status:           {result.status.value}")
print(f"Freeze reason:    {result.freeze_reason}")
print()
print("Signal 1 — Drift (Core model):")
print(f"  Score:          {result.drift_score}")
print(f"  Model:          {result.drift_model}")
print()
print("Signal 2 — MAARS (Prime model):")
print(f"  Verdict:        {result.maars_verdict}")
print(f"  Confidence:     {result.maars_confidence}")
print(f"  Reasoning:      {result.maars_reasoning[:100] if result.maars_reasoning else 'None'}...")
print(f"  Model:          {result.maars_model}")
print()
print("Signal 3 — Citations (Flash model):")
print(f"  Score:          {result.citation_score}")
print(f"  Model:          {result.citation_model}")
print()

# Verify expectations
print("=" * 60)
print("VERIFICATION")
print("=" * 60)
print()

checks = [
    ("Status is 'frozen'", result.status.value == "frozen"),
    ("Drift score is populated", result.drift_score is not None),
    ("Drift model is populated", result.drift_model is not None),
    ("MAARS verdict is populated", result.maars_verdict is not None),
    ("MAARS confidence is populated", result.maars_confidence is not None),
    ("MAARS model is populated", result.maars_model is not None),
    ("Citation score is populated", result.citation_score is not None),
    ("Citation model is populated", result.citation_model is not None),
    ("Freeze reason is populated", result.freeze_reason is not None),
]

all_passed = True
for description, passed in checks:
    status = "✓" if passed else "✗"
    print(f"  {status} {description}")
    if not passed:
        all_passed = False

print()
if all_passed:
    print("✅ ALL CHECKS PASSED — Phase 2 is complete!")
    print()
    print("The pipeline correctly:")
    print("  • Invoked all three model tiers (Core, Prime, Flash)")
    print("  • Populated all signal fields on the Action")
    print("  • Froze the action due to thin citations")
    print("  • Provided a clear freeze reason for the operator")
else:
    print("❌ SOME CHECKS FAILED — investigate the output above")
    sys.exit(1)
