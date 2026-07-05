import { useState, useEffect, useCallback, useRef } from "react";
import type { SentinelEvent } from "../types";

const defaultWs = typeof window !== 'undefined' 
  ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`
  : "ws://localhost:8000/ws";
const WS_URL = import.meta.env.VITE_WS_URL ?? defaultWs;
const RECONNECT_DELAY = 2000;

export function useEventStream() {
  const [events, setEvents] = useState<SentinelEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [frozenAction, setFrozenAction] = useState<SentinelEvent | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WS] Connected to", WS_URL);
        setConnected(true);
      };

      ws.onmessage = (e) => {
        try {
          const event: SentinelEvent = JSON.parse(e.data);
          // Server replays buffered history on connect; skip events already seen
          setEvents((prev) =>
            prev.some((p) => p.event_id === event.event_id) ? prev : [event, ...prev]
          );

          // Track frozen actions
          if (event.event_type === "RUN_STARTED") {
            setFrozenAction(null);
          }
          if (event.event_type === "ACTION_FROZEN") {
            setFrozenAction(event);
          }
          if (event.event_type === "OPERATOR_DECISION") {
            // Keep the frozen action visible until next freeze
          }
        } catch (err) {
          console.error("[WS] Failed to parse event:", err);
        }
      };

      ws.onclose = () => {
        console.log("[WS] Disconnected, reconnecting in", RECONNECT_DELAY, "ms");
        setConnected(false);
        reconnectTimeoutRef.current = window.setTimeout(connect, RECONNECT_DELAY);
      };

      ws.onerror = (err) => {
        console.error("[WS] Error:", err);
        ws.close();
      };
    } catch (err) {
      console.error("[WS] Connection failed:", err);
      reconnectTimeoutRef.current = window.setTimeout(connect, RECONNECT_DELAY);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { events, connected, frozenAction };
}
