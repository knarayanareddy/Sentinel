"""
Vultr Vector Store integration.
Manual retrieval pattern: search returns raw chunks, then inject into VultronRetriever chat calls.
This is NOT the RAG endpoint — it's a decoupled two-call pattern for explicit reasoning attribution.

CRITICAL SCHEMA NOTES (from Phase -1 testing):
- Ingest payload: {"content": "...", "description": "..."}
- Search payload: {"input": "...", "top_k": N}  (NOT "query")
- Search response: {"results": [{"id": "...", "created": "...", "content": "..."}]}
  (NO description or score fields in results)
- Collection creation: response schema is NOT {"id": "..."} — must inspect actual response
"""
import requests
import json as _json
from dataclasses import dataclass
from typing import Optional
from sentinel.config import CONFIG

_BASE = CONFIG["vultr_base_url"]
_HEADERS = {
    "Authorization": f"Bearer {CONFIG['vultr_api_key']}",
    "Content-Type": "application/json",
}
_collection_id: Optional[str] = None


@dataclass
class RetrievedChunk:
    content: str
    description: str
    score: float = 0.0


def _get_existing_collection(name: str) -> str:
    """
    Find an existing collection by name and extract its ID.
    Used when init_collection() encounters a 422 Duplicate error.
    """
    global _collection_id
    
    print(f"[VECTOR_STORE] Querying existing collections...")
    r = requests.get(
        f"{_BASE}/vector_store",
        headers=_HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    
    raw_response = r.json()
    print(f"[VECTOR_STORE] GET /v1/vector_store response: {_json.dumps(raw_response, indent=2, default=str)}")
    
    # The response format is likely {"collections": [...]} or just a list
    collections = raw_response.get("collections", raw_response.get("data", []))
    
    if not isinstance(collections, list):
        # Maybe the response is just a list directly
        if isinstance(raw_response, list):
            collections = raw_response
        else:
            raise RuntimeError(
                f"Could not parse collections list from response. "
                f"Response: {raw_response}"
            )
    
    # Find the collection with matching name
    for coll in collections:
        if coll.get("name") == name:
            collection_id = coll.get("id")
            if collection_id:
                print(f"[VECTOR_STORE] Found existing collection '{name}' with ID: {collection_id}")
                _collection_id = str(collection_id)
                return _collection_id
    
    # Collection not found in list
    raise RuntimeError(
        f"Collection '{name}' not found in existing collections. "
        f"Available collections: {[c.get('name') for c in collections]}"
    )


def init_collection(name: str = "sentinel-finance-docs") -> str:
    """
    Create a new vector store collection.
    
    The actual response schema from POST /v1/vector_store is:
    {"collection": {"id": "...", "name": "...", "created": "..."}}
    
    If the collection already exists (422 Duplicate), it will reuse the existing
    collection by querying GET /v1/vector_store and finding the matching name.
    """
    global _collection_id
    
    r = requests.post(
        f"{_BASE}/vector_store",
        headers=_HEADERS,
        json={"name": name},
        timeout=10,
    )
    
    raw_response = r.json()
    print(f"[VECTOR_STORE] init_collection() raw response ({r.status_code}): {_json.dumps(raw_response, indent=2, default=str)}")
    
    # Handle duplicate collection name
    if r.status_code == 422 and "Duplicate collection name" in str(raw_response):
        print(f"[VECTOR_STORE] Collection '{name}' already exists. Reusing existing collection.")
        return _get_existing_collection(name)
    
    r.raise_for_status()
    
    # Tolerant ID extraction — try multiple possible key names
    possible_keys = ["id", "collection_id", "vector_store_id", "collectionId", "vectorStoreId"]
    collection_id = None
    for key in possible_keys:
        if key in raw_response:
            collection_id = raw_response[key]
            print(f"[VECTOR_STORE] Extracted collection_id from key '{key}': {collection_id}")
            break
    
    if collection_id is None:
        # If response is a dict with a nested structure, try common patterns
        if isinstance(raw_response, dict):
            # Check if it's wrapped in a top-level key
            for wrapper_key in ["collection", "vector_store", "data", "result"]:
                if wrapper_key in raw_response and isinstance(raw_response[wrapper_key], dict):
                    for key in possible_keys:
                        if key in raw_response[wrapper_key]:
                            collection_id = raw_response[wrapper_key][key]
                            print(f"[VECTOR_STORE] Extracted collection_id from '{wrapper_key}.{key}': {collection_id}")
                            break
                    if collection_id:
                        break
    
    if collection_id is None:
        print(f"[VECTOR_STORE] FATAL: Could not extract collection ID from response.")
        print(f"[VECTOR_STORE] Full response keys: {list(raw_response.keys()) if isinstance(raw_response, dict) else type(raw_response)}")
        raise RuntimeError(
            f"Could not extract collection ID from response. "
            f"Response keys: {list(raw_response.keys()) if isinstance(raw_response, dict) else type(raw_response)}. "
            f"Full response: {raw_response}"
        )
    
    _collection_id = str(collection_id)
    return _collection_id


def set_collection_id(collection_id: str):
    """Manually set the collection ID (useful if you know it from a previous run)."""
    global _collection_id
    _collection_id = collection_id
    print(f"[VECTOR_STORE] Collection ID manually set to: {collection_id}")


def ingest(content: str, description: str) -> str:
    """Add a document to the vector store."""
    if not _collection_id:
        raise RuntimeError("Call init_collection() first.")
    r = requests.post(
        f"{_BASE}/vector_store/{_collection_id}/items",
        headers=_HEADERS,
        json={"content": content, "description": description},
        timeout=15,
    )
    
    # Handle duplicate items gracefully (e.g., on server restart)
    if r.status_code == 422:
        print(f"[VECTOR_STORE] Item '{description}' may already exist, skipping.")
        return "duplicate"
    
    r.raise_for_status()
    raw = r.json()
    # Tolerant ID extraction for ingested item
    item_id = raw.get("id", raw.get("item_id", raw.get("itemId", "unknown")))
    return str(item_id)


def search(query: str, top_k: int = 3) -> list[RetrievedChunk]:
    """
    Manual retrieval — no RAG completion endpoint used.
    Chunks are injected into a VultronRetriever chat call by the caller.

    CRITICAL: Uses "input" field (not "query") per Vultr API schema.
    Response has "results" array with {id, created, content} — no description or score.
    """
    if not _collection_id:
        raise RuntimeError("Vector store not initialised.")
    r = requests.post(
        f"{_BASE}/vector_store/{_collection_id}/search",
        headers=_HEADERS,
        json={"input": query, "top_k": top_k},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    # Tolerant schema handling: "results" (confirmed) or "items" (fallback)
    items = data.get("results", data.get("items", []))
    return [
        RetrievedChunk(
            content=i.get("content", i.get("text", "")),
            description=i.get("description", ""),  # Will be empty per actual schema
            score=float(i.get("score", 0.0)),  # Will be 0.0 per actual schema
        )
        for i in items
    ]


def get_collection_id() -> Optional[str]:
    """Return the current collection ID (or None if not initialised)."""
    return _collection_id
