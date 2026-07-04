"""
Vultr Vector Store integration.
Manual retrieval pattern: search returns raw chunks, then inject into VultronRetriever chat calls.
This is NOT the RAG endpoint — it's a decoupled two-call pattern for explicit reasoning attribution.

CRITICAL SCHEMA NOTES (from Phase -1 testing):
- Ingest payload: {"content": "...", "description": "..."}
- Search payload: {"input": "...", "top_k": N}  (NOT "query")
- Search response: {"results": [{"id": "...", "created": "...", "content": "..."}]}
  (NO description or score fields in results)
"""
import requests
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


def init_collection(name: str = "sentinel-finance-docs") -> str:
    """Create a new vector store collection."""
    global _collection_id
    r = requests.post(
        f"{_BASE}/vector_store",
        headers=_HEADERS,
        json={"name": name},
        timeout=10,
    )
    r.raise_for_status()
    _collection_id = r.json()["id"]
    return _collection_id


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
    r.raise_for_status()
    return r.json()["id"]


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
