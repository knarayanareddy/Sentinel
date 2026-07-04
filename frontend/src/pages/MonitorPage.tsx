import { type CSSProperties } from "react";
import type { SentinelEvent } from "../types";
import { EventRow } from "../components/EventRow";
import { FreezeAlert } from "../components/FreezeAlert";
import type { ActionFrozenPayload } from "../types";

interface MonitorPageProps {
  events: SentinelEvent[];
  connected: boolean;
  frozenAction: SentinelEvent | null;
  onViewSignals: () => void;
  onRunAgent: () => void;
}

export function MonitorPage({
  events,
  connected,
  frozenAction,
  onViewSignals,
  onRunAgent,
}: MonitorPageProps) {
  const containerStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    padding: "24px",
    height: "100vh",
    overflow: "hidden",
  };

  const headerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  };

  const titleStyle: CSSProperties = {
    fontSize: "24px",
    fontWeight: "600",
    color: "var(--color-text)",
  };

  const connectionStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
  };

  const statusDotStyle: CSSProperties = {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: connected ? "var(--color-executed)" : "var(--color-frozen)",
  };

  const controlsStyle: CSSProperties = {
    display: "flex",
    gap: "12px",
  };

  const buttonStyle: CSSProperties = {
    padding: "8px 16px",
    fontSize: "14px",
    fontFamily: "var(--font-body)",
    fontWeight: "500",
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-md)",
    color: "var(--color-text)",
    cursor: "pointer",
  };

  const streamStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    flex: 1,
    overflow: "auto",
    padding: "8px",
  };

  const emptyStyle: CSSProperties = {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100%",
    fontSize: "14px",
    color: "var(--color-text-muted)",
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h1 style={titleStyle}>SENTINEL — Live Monitor</h1>
        <div style={connectionStyle}>
          <div style={statusDotStyle} />
          {connected ? "Connected" : "Disconnected"}
        </div>
      </div>

      <div style={controlsStyle}>
        <button style={buttonStyle} onClick={onRunAgent}>
          ▶ Run Agent
        </button>
      </div>

      {frozenAction && (
        <FreezeAlert
          payload={frozenAction.payload as ActionFrozenPayload}
          onClick={onViewSignals}
        />
      )}

      <div style={streamStyle}>
        {events.length === 0 ? (
          <div style={emptyStyle}>
            No events yet. Click "Run Agent" to start.
          </div>
        ) : (
          events.map((event) => <EventRow key={event.event_id} event={event} />)
        )}
      </div>
    </div>
  );
}
