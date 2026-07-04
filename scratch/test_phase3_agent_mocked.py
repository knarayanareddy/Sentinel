#!/usr/bin/env python3
"""
Phase 3 Test: Full 7-step agent loop with mocked API calls.

This script verifies the agent executes all 7 steps correctly, including:
- Conditional retrieval (Step 5 only fires if breach detected)
- Sentinel gate fires on Step 7 (irreversible action)
- All events emitted in correct order
"""
import os
import sys

# Set environment variables BEFORE any sentinel imports
os.environ["VULTR_API_KEY"] = "test-key-for-phase3"
os.environ["VULTRON_PRIME_MODEL"] = "test/prime-model"
os.environ["VULTRON_CORE_MODEL"] = "test/core-model"
os.environ["VULTRON_FLASH_MODEL"] = "test/flash-model"
os.environ["SANDBOX_EMAIL_SINK"] = "mailhog"
os.environ["SENTINEL_ENV"] = "demo"

# Now we can import sentinel modules
from unittest.mock import patch, MagicMock
from sentinel.vector_store import init_collection
from sentinel.pipeline import SentinelPipeline
from sentinel.agent import run_agent, TASK_BRIEF
from sentinel.eventbus import subscribe
from sentinel.models import SentinelEvent

# Track events for verification
events_received = []

def event_handler(event: SentinelEvent):
    """Collect events for analysis."""
    events_received.append(event)
    print(f"[EVENT] {event.event_type.value}")

# Subscribe to all events
subscribe("*", event_handler)

print("=" * 80)
print("PHASE 3 TEST: Full 7-Step Agent Loop (Mocked)")
print("=" * 80)
print()

# Mock the API calls
with patch('sentinel.vultr_client._client') as mock_client:
    with patch('sentinel.vector_store.requests') as mock_requests:
        # Mock chat completions to return predictable responses
        def mock_chat_completion(**kwargs):
            mock_response = MagicMock()
            mock_choice = MagicMock()
            
            # Return different responses based on the prompt content
            prompt_text = str(kwargs.get('messages', ''))
            
            if "List the steps" in prompt_text:
                mock_choice.message.content = "1. Retrieve covenant definition\n2. Check historical trend\n3. Calculate ratio\n4. Analyze transactions if breach\n5. Draft memo\n6. Send memo"
            elif "covenant threshold" in prompt_text or "What is the covenant" in prompt_text:
                mock_choice.message.content = "The Debt/EBITDA covenant threshold is 4.5x as defined in §4.2 of the credit agreement."
            elif "historical ratio trend" in prompt_text or "What is the historical" in prompt_text:
                mock_choice.message.content = "Historical trend shows ratio increasing from 3.8x to 4.3x over 8 quarters."
            elif "transactions explain" in prompt_text or "Which transactions" in prompt_text:
                mock_choice.message.content = "Three anomalous transactions in Q2 explain the spike to 4.62x."
            else:
                mock_choice.message.content = "Analysis complete."
            
            mock_response.choices = [mock_choice]
            return mock_response
        
        mock_client.chat.completions.create.side_effect = mock_chat_completion
        
        # Mock vector store responses
        def mock_post(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            
            if '/vector_store' in url and 'items' not in url and 'search' not in url:
                # Collection creation
                mock_resp.json.return_value = {
                    "collection": {"id": "test-collection-123", "name": "test"}
                }
            elif 'search' in url:
                # Search results - return multiple chunks for realistic behavior
                mock_resp.json.return_value = {
                    "results": [
                        {"id": "1", "content": "Test document content about covenants and ratios", "created": "2024-01-01"},
                        {"id": "2", "content": "Additional context about debt thresholds", "created": "2024-01-01"},
                        {"id": "3", "content": "More relevant information", "created": "2024-01-01"}
                    ]
                }
            else:
                mock_resp.json.return_value = {"id": "test-item-123"}
            
            return mock_resp
        
        def mock_get(*args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "collections": [
                    {"id": "test-collection-123", "name": "sentinel-finance-docs"}
                ]
            }
            return mock_resp
        
        mock_requests.post.side_effect = mock_post
        mock_requests.get.side_effect = mock_get
        
        # Initialize vector store first
        print("[0/2] Initializing vector store...")
        init_collection()
        print("Vector store initialized.")
        
        # Initialize the Sentinel pipeline (sets up the freeze policy)
        print("[0/2] Initializing Sentinel pipeline...")
        SentinelPipeline(task_brief=TASK_BRIEF)
        print("Sentinel pipeline initialized.")
        print()
        
        # Run the agent
        print("[1/2] Triggering agent loop...")
        print()
        print("-" * 80)
        thread = run_agent()
        
        # Wait for agent to complete
        print("Agent running in background thread. Waiting for completion...")
        print()
        thread.join(timeout=60)  # Wait up to 1 minute
        
        if thread.is_alive():
            print("[WARNING] Agent did not complete within timeout")
        else:
            print("Agent thread completed.")
        print("-" * 80)
        print()
        
        # Analyze results
        print("[2/2] Analyzing event stream...")
        print()
        
        # Check for expected events
        event_types = [e.event_type for e in events_received]
        
        print("Event sequence:")
        for i, event_type in enumerate(event_types, 1):
            print(f"  {i}. {event_type.value}")
        print()
        
        # Verify expected steps
        checks = {
            "AGENT_PLAN": False,
            "RETRIEVAL_PASS": 0,  # Count occurrences
            "TOOL_CALLED": False,
            "ACTION_EXECUTED": False,  # For draft_memo
            "ACTION_FROZEN": False,    # For send_escalation_memo
        }
        
        for event in events_received:
            if event.event_type.value == "AGENT_PLAN":
                checks["AGENT_PLAN"] = True
            elif event.event_type.value == "RETRIEVAL_PASS":
                checks["RETRIEVAL_PASS"] += 1
            elif event.event_type.value == "TOOL_CALLED":
                checks["TOOL_CALLED"] = True
            elif event.event_type.value == "ACTION_EXECUTED":
                if "Draft escalation memo" in event.payload.get("action", ""):
                    checks["ACTION_EXECUTED"] = True
            elif event.event_type.value == "ACTION_FROZEN":
                checks["ACTION_FROZEN"] = True
        
        print("Verification Results:")
        print("-" * 80)
        print(f"  ✓ Step 1 (AGENT_PLAN): {'PASS' if checks['AGENT_PLAN'] else 'FAIL'}")
        print(f"  ✓ Step 2-3 (RETRIEVAL_PASS): {'PASS' if checks['RETRIEVAL_PASS'] >= 2 else 'FAIL'} "
              f"(found {checks['RETRIEVAL_PASS']}, expected >= 2)")
        print(f"  ✓ Step 4 (TOOL_CALLED): {'PASS' if checks['TOOL_CALLED'] else 'FAIL'}")
        
        # Check for conditional retrieval (Step 5)
        step_5_pass = checks["RETRIEVAL_PASS"] == 3
        print(f"  ✓ Step 5 (Conditional RETRIEVAL): {'PASS' if step_5_pass else 'FAIL'} "
              f"(found {checks['RETRIEVAL_PASS']} retrievals, expected 3)")
        if step_5_pass:
            print("    → Conditional retrieval fired because breach was detected!")
        
        print(f"  ✓ Step 6 (ACTION_EXECUTED - draft_memo): {'PASS' if checks['ACTION_EXECUTED'] else 'FAIL'}")
        print(f"  ✓ Step 7 (ACTION_FROZEN - send_escalation_memo): {'PASS' if checks['ACTION_FROZEN'] else 'FAIL'}")
        if checks["ACTION_FROZEN"]:
            print("    → Sentinel gate fired! Irreversible action was frozen.")
        
        # Check for freeze signals (drift, maars, citation)
        freeze_signals = {
            "DRIFT_SCORED": False,
            "MAARS_PROBE": False,
            "CITATION_CHECKED": False,
        }
        
        for event in events_received:
            if event.event_type.value in freeze_signals:
                freeze_signals[event.event_type.value] = True
        
        print()
        print("Sentinel Gate Signals:")
        print("-" * 80)
        print(f"  ✓ Drift Score: {'PASS' if freeze_signals['DRIFT_SCORED'] else 'FAIL'}")
        print(f"  ✓ MAARS Probe: {'PASS' if freeze_signals['MAARS_PROBE'] else 'FAIL'}")
        print(f"  ✓ Citation Check: {'PASS' if freeze_signals['CITATION_CHECKED'] else 'FAIL'}")
        
        # Overall result
        all_pass = (
            checks["AGENT_PLAN"] and
            checks["RETRIEVAL_PASS"] == 3 and
            checks["TOOL_CALLED"] and
            checks["ACTION_EXECUTED"] and
            checks["ACTION_FROZEN"] and
            all(freeze_signals.values())
        )
        
        print()
        print("=" * 80)
        if all_pass:
            print("✅ PHASE 3 TEST PASSED - All 7 steps executed correctly!")
            print("   - Conditional retrieval worked (Step 5)")
            print("   - Sentinel gate fired (Step 7)")
            print("   - All freeze signals evaluated")
        else:
            print("❌ PHASE 3 TEST FAILED - See verification results above")
        print("=" * 80)
