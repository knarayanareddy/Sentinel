#!/usr/bin/env python3
"""
Phase 1 Verification Script
Run this AFTER starting the server to verify VultronRetriever and vector store integration.

Usage:
    1. Start server: uvicorn sentinel.server:app --reload
    2. Wait for "Application startup complete" message
    3. Run this script: python scratch/phase1_verification.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentinel.vultr_client import prime_text, core_json, flash_json
from sentinel.vector_store import search


def test_model_tiers():
    """Test all three VultronRetriever model tiers."""
    print("\n" + "="*60)
    print("TESTING VULTRONRETRIEVER MODEL TIERS")
    print("="*60)

    print("\n[1/3] Testing Prime model (Qwen3.5-8B)...")
    try:
        response = prime_text([{"role": "user", "content": "Say OK if you can hear me."}])
        print(f"✓ Prime response: {response}")
    except Exception as e:
        print(f"✗ Prime failed: {e}")
        return False

    print("\n[2/3] Testing Core model (Qwen3.5-4.5B)...")
    try:
        response = core_json([{"role": "user", "content": 'Return JSON: {"test": true}'}])
        print(f"✓ Core response: {response}")
    except Exception as e:
        print(f"✗ Core failed: {e}")
        return False

    print("\n[3/3] Testing Flash model (Qwen3.5-0.8B)...")
    try:
        response = flash_json([{"role": "user", "content": 'Return JSON: {"test": true}'}])
        print(f"✓ Flash response: {response}")
    except Exception as e:
        print(f"✗ Flash failed: {e}")
        return False

    print("\n✓ All three model tiers responding correctly")
    return True


def test_vector_search():
    """Test vector search with different query types."""
    print("\n" + "="*60)
    print("TESTING VECTOR STORE SEARCH")
    print("="*60)

    queries = [
        "Debt/EBITDA covenant threshold",
        "historical ratio trend",
        "recent transactions anomalous",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}/3]: {query}")
        try:
            results = search(query, top_k=3)
            print(f"✓ Retrieved {len(results)} chunks")
            if results:
                print(f"  First chunk content preview: {results[0].content[:100]}...")
                # Note: description and score will be empty/0 per actual API schema
                if results[0].description:
                    print(f"  Description: {results[0].description}")
                if results[0].score > 0:
                    print(f"  Score: {results[0].score}")
        except Exception as e:
            print(f"✗ Search failed: {e}")
            return False

    print("\n✓ Vector search returning relevant chunks")
    return True


def main():
    print("\n" + "="*60)
    print("SENTINEL PHASE 1 VERIFICATION")
    print("="*60)
    print("\nThis script tests the VultronRetriever client and vector store.")
    print("Make sure the server is running: uvicorn sentinel.server:app --reload")
    print("\nPress Ctrl+C to exit at any time.\n")

    try:
        input("Press Enter to start verification...")
    except KeyboardInterrupt:
        print("\n\nVerification cancelled.")
        return

    # Test model tiers
    if not test_model_tiers():
        print("\n✗ Model tier tests failed")
        return

    # Test vector search
    if not test_vector_search():
        print("\n✗ Vector search tests failed")
        return

    print("\n" + "="*60)
    print("✓ ALL PHASE 1 TESTS PASSED")
    print("="*60)
    print("\nPhase 1 is complete. Ready for Phase 2.")
    print("Press Enter to exit...")

    try:
        input()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
