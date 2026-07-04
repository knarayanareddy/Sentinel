from collections import defaultdict
from typing import Callable
from sentinel.models import SentinelEvent

_subscribers: dict[str, list[Callable]] = defaultdict(list)


def subscribe(event_type: str, handler: Callable):
    _subscribers[event_type].append(handler)


def subscribe_all(handler: Callable):
    _subscribers["*"].append(handler)


def emit(event: SentinelEvent):
    for h in _subscribers.get(event.event_type, []):
        h(event)
    for h in _subscribers.get("*", []):
        h(event)
