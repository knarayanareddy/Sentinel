#!/usr/bin/env python3
"""
Test script to verify the duplicate collection handling fix.
This simulates the scenario where the collection already exists.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing duplicate collection handling")
print("=" * 60)

# Import after loading .env
from sentinel.vector_store import init_collection

# Try to initialize the collection
# If it already exists, should get 422 and fall back to finding existing
try:
    collection_id = init_collection("sentinel-finance-docs")
    print(f"\n✓ SUCCESS: Got collection ID: {collection_id}")
    print(f"✓ Duplicate handling worked correctly!")
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
