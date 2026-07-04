"""
Vultr Vector Store integration.
Manual retrieval pattern: Base search fetches chunks, which are then explicitly piped into VultronRetriever via /v1/rerank.
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


def _chunk_text(text: str, max_chunk_size: int = 800) -> list[str]:
    """
    Split text into chunks suitable for Vultr's embedding model.
    
    Strategy:
    1. Split by double-newlines (paragraph boundaries) for semantic chunks
    2. Merge small consecutive paragraphs until they'd exceed max_chunk_size
    3. If a single paragraph exceeds the limit, split by sentences or hard-break
    
    Args:
        text: The full text to chunk
        max_chunk_size: Maximum characters per chunk (default 800, safe margin below 1000)
    
    Returns:
        List of text chunks
    """
    # Handle empty or whitespace-only input
    if not text or not text.strip():
        return []
    
    if len(text) <= max_chunk_size:
        return [text]
    
    # Split by double-newlines (paragraph boundaries)
    paragraphs = text.split("\n\n")
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(para) + 2 > max_chunk_size:
            # Save current chunk if non-empty
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If single paragraph exceeds limit, split it further
            if len(para) > max_chunk_size:
                # Try splitting by sentences (period + space)
                sentences = para.replace(". ", ".|").split("|")
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    if len(current_chunk) + len(sentence) + 1 > max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        
                        # If single sentence still too long, hard-break
                        if len(sentence) > max_chunk_size:
                            for i in range(0, len(sentence), max_chunk_size):
                                chunks.append(sentence[i:i+max_chunk_size].strip())
                        else:
                            current_chunk = sentence
                    else:
                        if current_chunk:
                            current_chunk += " " + sentence
                        else:
                            current_chunk = sentence
            else:
                current_chunk = para
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Filter out empty chunks
    chunks = [c for c in chunks if c]
    
    return chunks


def ingest(content: str, description: str) -> list[str]:
    """
    Add a document to the vector store, automatically chunking if needed.
    
    Vultr's embedding model has a context window limit (~1000 chars).
    This function splits large documents into semantic chunks (by paragraphs)
    and ingests each chunk separately.
    
    Args:
        content: The full document text
        description: Document identifier (e.g., filename)
    
    Returns:
        List of ingested item IDs (one per chunk)
    """
    if not _collection_id:
        raise RuntimeError("Call init_collection() first.")
    
    # Chunk the content
    chunks = _chunk_text(content, max_chunk_size=800)
    
    print(f"[VECTOR_STORE] Splitting '{description}' into {len(chunks)} chunk(s)")
    
    ingested_ids = []
    for i, chunk in enumerate(chunks, 1):
        chunk_description = f"{description}:chunk_{i}" if len(chunks) > 1 else description
        
        r = requests.post(
            f"{_BASE}/vector_store/{_collection_id}/items",
            headers=_HEADERS,
            json={"content": chunk, "description": chunk_description},
            timeout=15,
        )
        
        # Print actual error on 422 instead of silently swallowing
        if r.status_code == 422:
            error_response = r.json()
            print(f"[VECTOR_STORE] ERROR ingesting chunk {i}: {error_response}")
            print(f"[VECTOR_STORE] Chunk content preview: {chunk[:200]}...")
            print(f"[VECTOR_STORE] Chunk length: {len(chunk)} chars")
            r.raise_for_status()
        
        r.raise_for_status()
        raw = r.json()
        # Tolerant ID extraction for ingested item
        item_id = raw.get("id", raw.get("item_id", raw.get("itemId", "unknown")))
        ingested_ids.append(str(item_id))
        print(f"[VECTOR_STORE] Ingested chunk {i}/{len(chunks)}: {chunk_description} (id: {item_id})")
    
    return ingested_ids


def search(query: str, top_k: int = 3) -> list[RetrievedChunk]:
    """
    Two-stage retrieval to satisfy VultronRetriever compliance:
    1. Base retrieval: Fetch top_k * 3 chunks using vector similarity.
    2. ReRank stage: Pass chunks to VultronRetriever via /v1/rerank API to sort by relevance.

    CRITICAL: Uses "input" field (not "query") for vector store per Vultr API schema.
    """
    if not _collection_id:
        raise RuntimeError("Vector store not initialised.")
    
    # 1. Base Retrieval (over-fetch)
    r = requests.post(
        f"{_BASE}/vector_store/{_collection_id}/search",
        headers=_HEADERS,
        json={"input": query, "top_k": top_k * 3},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    items = data.get("results", data.get("items", []))
    
    if not items:
        return []

    # 2. ReRank with VultronRetriever
    from sentinel.config import CONFIG
    rerank_model = CONFIG["vultron_rerank"]
    documents = [i.get("content", i.get("text", "")) for i in items]

    rerank_r = requests.post(
        f"{_BASE}/rerank",
        headers=_HEADERS,
        json={
            "model": rerank_model,
            "query": query,
            "documents": documents
        },
        timeout=20,
    )
    
    if rerank_r.status_code == 200:
        rerank_data = rerank_r.json()
        rerank_results = rerank_data.get("results", [])
        
        # Build chunks with VultronRetriever scores
        chunks = []
        for res in rerank_results:
            idx = res.get("index")
            score = res.get("relevance_score", 0.0)
            if idx is not None and idx < len(documents):
                chunks.append(RetrievedChunk(
                    content=documents[idx],
                    description="", # Empty per actual schema
                    score=float(score)
                ))
        
        # Sort by relevance descending
        chunks.sort(key=lambda x: x.score, reverse=True)
        return chunks[:top_k]
    else:
        # Fallback if ReRank fails (e.g. rate limit)
        print(f"[VECTOR_STORE] ReRank failed ({rerank_r.status_code}): {rerank_r.text}")
        return [
            RetrievedChunk(
                content=doc,
                description="",
                score=0.0
            )
            for doc in documents[:top_k]
        ]


def get_collection_id() -> Optional[str]:
    """Return the current collection ID (or None if not initialised)."""
    return _collection_id
