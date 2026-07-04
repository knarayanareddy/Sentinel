import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import type { SentinelEvent } from "../types";
import { EventRow } from "../components/EventRow";
import { FreezeAlert } from "../components/FreezeAlert";
import { StepRail } from "../components/StepRail";
import { DocumentDrawer } from "../components/DocumentDrawer";
import { useCorpus } from "../hooks/useCorpus";
import type { ActionFrozenPayload } from "../types";

const SCENARIOS = [
  { id: "breach", label: "Q2 FY2025 · breach" },
  { id: "compliant", label: "Q3 FY2023 · compliant" },
];

interface MonitorPageProps {
  events: SentinelEvent[];
  frozenAction: SentinelEvent | null;
  onViewGate: () => void;
  onRunAgent: (scenario: string) => void;
}

export function MonitorPage({
  events,
  frozenAction,
  onViewGate,
  onRunAgent,
}: MonitorPageProps) {
  const streamRef = useRef<HTMLDivElement>(null);
  const chronological = useMemo(() => [...events].reverse(), [events]);
  const corpus = useCorpus();
  const [openDoc, setOpenDoc] = useState<string | null>(null);
  const [scenario, setScenario] = useState("breach");

  useEffect(() => {
    const el = streamRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [events.length]);

  const containerStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    padding: "24px",
    height: "100%",
    overflow: "hidden",
  };

  const headerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  };

  const titleStyle: CSSProperties = {
    fontSize: "20px",
    fontWeight: "600",
    color: "var(--color-text)",
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

  const bodyStyle: CSSProperties = {
    display: "flex",
    gap: "16px",
    flex: 1,
    overflow: "hidden",
  };

  const streamStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    flex: 1,
    overflow: "auto",
    padding: "2px",
  };

  const corpusBarStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
  };

  const corpusLabelStyle: CSSProperties = {
    letterSpacing: "0.1em",
    textTransform: "uppercase",
  };

  const docChipStyle: CSSProperties = {
    padding: "3px 8px",
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-sm)",
    color: "#81C784",
    fontFamily: "var(--font-mono)",
    fontSize: "11px",
    cursor: "pointer",
  };

  const scenarioGroupStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
  };

  const scenarioLabelStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    letterSpacing: "0.1em",
    textTransform: "uppercase",
  };

  const scenarioChipStyle = (active: boolean): CSSProperties => ({
    padding: "6px 12px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    background: active ? "rgba(242, 240, 235, 0.08)" : "var(--color-surface)",
    border: `1px solid ${active ? "var(--color-text-muted)" : "var(--color-border)"}`,
    borderRadius: "var(--radius-md)",
    color: active ? "var(--color-text)" : "var(--color-text-muted)",
    cursor: "pointer",
  });

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
        <h1 style={titleStyle}>Live Monitor</h1>
        <div style={scenarioGroupStyle}>
          <span style={scenarioLabelStyle}>Scenario</span>
          {SCENARIOS.map((s) => (
            <button
              key={s.id}
              style={scenarioChipStyle(scenario === s.id)}
              onClick={() => setScenario(s.id)}
            >
              {s.label}
            </button>
          ))}
          <button style={buttonStyle} onClick={() => onRunAgent(scenario)}>
            ▶ Run Agent
          </button>
        </div>
      </div>

      {corpus.length > 0 && (
        <div style={corpusBarStyle}>
          <span style={corpusLabelStyle}>Corpus · {corpus.length} docs</span>
          {corpus.map((doc) => (
            <button
              key={doc.name}
              style={docChipStyle}
              onClick={() => setOpenDoc(doc.name)}
              title={`Open ${doc.name}`}
            >
              {doc.name}
            </button>
          ))}
        </div>
      )}

      {frozenAction && (
        <FreezeAlert
          payload={frozenAction.payload as ActionFrozenPayload}
          onClick={onViewGate}
        />
      )}

      <div style={bodyStyle}>
        <StepRail events={events} />
        <div ref={streamRef} style={streamStyle}>
          {chronological.length === 0 ? (
            <div style={emptyStyle}>
              No events yet. Click "Run Agent" to start.
            </div>
          ) : (
            chronological.map((event) => <EventRow key={event.event_id} event={event} />)
          )}
        </div>
      </div>

      {openDoc && (
        <DocumentDrawer documentName={openDoc} onClose={() => setOpenDoc(null)} />
      )}
    </div>
  );
}
