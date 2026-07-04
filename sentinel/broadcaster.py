"""
WebSocket broadcaster for real-time event streaming.
Manages connected clients and broadcasts SentinelEvent objects to all of them.
"""
import asyncio
import json
from dataclasses import asdict
from sentinel.models import SentinelEvent

_loop: asyncio.AbstractEventLoop | None = None
_clients: set = set()


def set_event_loop(loop: asyncio.AbstractEventLoop):
    """Set the event loop for async WebSocket sends."""
    global _loop
    _loop = loop


def register_client(ws):
    """Register a WebSocket client to receive broadcasts."""
    _clients.add(ws)


def unregister_client(ws):
    """Unregister a WebSocket client."""
    _clients.discard(ws)


def broadcast(event: SentinelEvent):
    """
    Broadcast a SentinelEvent to all connected WebSocket clients.
    This function is synchronous and schedules async sends on the event loop.
    """
    if not _loop or not _clients:
        return
    
    payload = json.dumps(asdict(event), default=str)
    for ws in list(_clients):
        asyncio.run_coroutine_threadsafe(_send(ws, payload), _loop)


async def _send(ws, payload: str):
    """Send a payload to a WebSocket client, removing on error."""
    try:
        await ws.send_text(payload)
    except Exception:
        _clients.discard(ws)
