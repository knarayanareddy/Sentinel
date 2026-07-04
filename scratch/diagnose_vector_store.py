#!/usr/bin/env python3
"""
Diagnostic script: prints raw API responses for vector store operations.
Run this to see the exact schema returned by the Vultr vector store API.

Usage:
    python scratch/diagnose_vector_store.py
"""
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
from dotenv import load_dotenv
load_dotenv()

import requests

API_KEY = os.getenv("VULTR_API_KEY")
BASE_URL = os.getenv("VULTR_BASE_URL", "https://api.vultrinference.com/v1")

if not API_KEY:
    print("ERROR: VULTR_API_KEY not set in .env")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

print("="*60)
print("VULTR VECTOR STORE DIAGNOSTICS")
print("="*60)
print(f"Base URL: {BASE_URL}")
print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print()

# ─── Step 1: Create a test collection ───
print("─" * 60)
print("STEP 1: POST /v1/vector_store (create collection)")
print("─" * 60)
r = requests.post(
    f"{BASE_URL}/vector_store",
    headers=HEADERS,
    json={"name": "sentinel-diagnostic-test"},
    timeout=10,
)
print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Raw response body:")
try:
    body = r.json()
    print(json.dumps(body, indent=2, default=str))
except Exception:
    print(f"  (not JSON) {r.text[:500]}")

if r.status_code >= 400:
    print(f"\n⚠️  Collection creation failed with status {r.status_code}")
    print("The endpoint may require a different payload or URL structure.")
    print("\nTrying alternative endpoints...")
    
    # Try alternative endpoint patterns
    alternatives = [
        ("POST", f"{BASE_URL}/vector_stores", {"name": "sentinel-diagnostic-test"}),
        ("POST", f"{BASE_URL}/vector-store", {"name": "sentinel-diagnostic-test"}),
    ]
    for method, url, payload in alternatives:
        print(f"\n  Trying: {method} {url}")
        try:
            r2 = requests.request(method, url, headers=HEADERS, json=payload, timeout=10)
            print(f"  Status: {r2.status_code}")
            try:
                print(f"  Body: {json.dumps(r2.json(), indent=2, default=str)}")
            except:
                print(f"  Body: {r2.text[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

# ─── Step 2: If we got a collection ID, try listing/searching ───
print()
print("─" * 60)
print("STEP 2: GET /v1/vector_store (list collections)")
print("─" * 60)
r = requests.get(f"{BASE_URL}/vector_store", headers=HEADERS, timeout=10)
print(f"Status: {r.status_code}")
try:
    body = r.json()
    print(json.dumps(body, indent=2, default=str)[:2000])
except:
    print(f"  Body: {r.text[:500]}")

# ─── Step 3: Check available models ───
print()
print("─" * 60)
print("STEP 3: GET /v1/models (check available models)")
print("─" * 60)
r = requests.get(f"{BASE_URL}/models", headers=HEADERS, timeout=10)
print(f"Status: {r.status_code}")
try:
    body = r.json()
    models = body.get("data", body.get("models", []))
    print(f"Total models listed: {len(models)}")
    for m in models:
        model_id = m.get("id", m.get("name", "unknown"))
        model_type = m.get("type", m.get("model_type", "unknown"))
        print(f"  - {model_id}  (type: {model_type})")
except Exception as e:
    print(f"  Error parsing: {e}")
    print(f"  Body: {r.text[:500]}")

print()
print("="*60)
print("DIAGNOSTICS COMPLETE")
print("="*60)
