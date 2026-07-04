"""
FastAPI server for SENTINEL.
Phase 5: WebSocket broadcasting + all previous phases.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from sentinel import broadcaster, eventbus
from sentinel.vector_store import init_collection, ingest
from sentinel.agent import run_agent, SCENARIOS, TASK_BRIEF
from sentinel.pipeline import SentinelPipeline
from sentinel.sequencer import seal_incident
from sentinel.models import DecisionRequest, RunRequest
from sentinel.orchestrator import get_action, register_tool_executor, resolve_frozen
from sentinel.tools import send_memo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup: initialize the vector store, ingest documents, set up the Sentinel pipeline,
    and wire the broadcaster to the eventbus for real-time WebSocket streaming.
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
    
    # Initialize the Sentinel pipeline (sets up the freeze policy)
    print("[SENTINEL] Initializing Sentinel pipeline...")
    SentinelPipeline(task_brief=TASK_BRIEF)
    register_tool_executor("send_escalation_memo", send_memo.run)
    register_tool_executor("send_confirmation_memo", send_memo.run)
    print("[SENTINEL] Sentinel pipeline initialized.")
    
    # Wire broadcaster to eventbus for WebSocket streaming
    loop = asyncio.get_event_loop()
    broadcaster.set_event_loop(loop)
    eventbus.subscribe_all(broadcaster.broadcast)
    print("[SENTINEL] WebSocket broadcaster wired to eventbus.")
    
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


@app.get("/api/corpus")
async def corpus():
    """
    Return the ingested document corpus so the UI can render source
    documents behind citations.
    """
    corpus_dir = Path("docs/demo_corpus")
    return {
        "documents": [
            {"name": doc.name, "content": doc.read_text()}
            for doc in sorted(corpus_dir.glob("*.md"))
        ]
    }


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    WebSocket endpoint for real-time event streaming.
    Clients receive all SentinelEvents as JSON messages.
    """
    await ws.accept()
    for payload in broadcaster.get_history():
        await ws.send_text(payload)
    broadcaster.register_client(ws)
    print(f"[SENTINEL] WebSocket client connected. Total clients: {len(broadcaster._clients)}")
    try:
        while True:
            # Keep connection alive, receive any messages from client (optional)
            await ws.receive_text()
    except WebSocketDisconnect:
        broadcaster.unregister_client(ws)
        print(f"[SENTINEL] WebSocket client disconnected. Total clients: {len(broadcaster._clients)}")


@app.get("/api/scenarios")
async def scenarios():
    """List the demo scenarios the agent can run."""
    return {
        "scenarios": [
            {"id": key, "label": value["label"]}
            for key, value in SCENARIOS.items()
        ]
    }


@app.post("/api/run")
async def trigger_agent(request: RunRequest | None = None):
    """
    Trigger the SENTINEL agent to run the full 7-step loop.
    The agent runs in a background thread and emits events via EventBus.
    """
    scenario = request.scenario if request else "breach"
    if scenario not in SCENARIOS:
        raise HTTPException(status_code=422, detail=f"Unknown scenario: {scenario}")
    print(f"[SENTINEL] Agent triggered via /api/run (scenario={scenario})")
    run_agent(scenario)
    return {
        "status": "agent_started",
        "scenario": scenario,
        "message": "Agent running in background. Monitor events via WebSocket at /ws.",
    }


@app.post("/api/decide")
async def decide(request: DecisionRequest):
    """
    Approve or abort a frozen action.
    Resolves the action and seals the incident record with SHA-256 hash.
    """
    action = get_action(request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if action.status.value != "frozen":
        raise HTTPException(
            status_code=409,
            detail=f"Action is not frozen (current status: {action.status.value})",
        )
    
    # Resolve the frozen action
    resolve_frozen(request.action_id, request.approved)
    
    # Seal the incident record
    report = seal_incident(action)
    
    return {
        "status": action.status.value,
        "integrity_hash": report["integrity_hash"],
    }
