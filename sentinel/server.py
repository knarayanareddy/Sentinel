"""
FastAPI server for SENTINEL.
Phase 3: Vector store initialization, health endpoint, and agent trigger.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from sentinel.vector_store import init_collection, ingest
from sentinel.agent import run_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup: initialize the vector store and ingest all demo corpus documents.
    """
    print("[SENTINEL] Initializing vector store...")
    init_collection()
    print("[SENTINEL] Vector store collection created.")

    corpus_dir = Path("docs/demo_corpus")
    for doc in sorted(corpus_dir.glob("*.md")):
        content = doc.read_text()
        description = doc.name
        item_id = ingest(content, description)
        print(f"[SENTINEL] Ingested: {description} (item_id: {item_id})")

    print(f"[SENTINEL] Ingested {len(list(corpus_dir.glob('*.md')))} documents into vector store.")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    """Health check endpoint for deployment verification."""
    return {"status": "ok"}


@app.post("/api/run")
async def trigger_agent():
    """
    Trigger the SENTINEL agent to run the full 7-step loop.
    The agent runs in a background thread and emits events via EventBus.
    """
    print("[SENTINEL] Agent triggered via /api/run")
    thread = run_agent()
    return {
        "status": "agent_started",
        "message": "Agent running in background. Monitor events via /api/events.",
    }
