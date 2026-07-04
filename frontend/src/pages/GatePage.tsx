import { type CSSProperties } from "react";
import type {
  SentinelEvent,
  IncidentSealedPayload,
} from "../types";
import { OperatorGate } from "../components/OperatorGate";
import { IncidentRecord } from "../components/IncidentRecord";

interface GatePageProps {
  events: SentinelEvent[];
  frozenAction: SentinelEvent | null;
  onDecision: (approved: boolean) => void;
  onBack: () => void;
}

export function GatePage({ events, frozenAction, onDecision, onBack }: GatePageProps) {
  const containerStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "24px",
    padding: "24px",
    height: "100vh",
    overflow: "auto",
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

  const backButtonStyle: CSSProperties = {
    padding: "8px 16px",
    fontSize: "14px",
    fontFamily: "var(--font-body)",
    background: "transparent",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-md)",
    color: "var(--color-text-muted)",
    cursor: "pointer",
  };

  const footerStyle: CSSProperties = {
    padding: "12px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    borderTop: "1px solid var(--color-border)",
    marginTop: "auto",
  };

  // Find the incident sealed event
  const incidentEvent = events.find((e) => e.event_type === "INCIDENT_SEALED");
  const incidentPayload = incidentEvent?.payload as IncidentSealedPayload | undefined;

  // Find the operator decision event
  const decisionEvent = events.find((e) => e.event_type === "OPERATOR_DECISION");

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h2 style={titleStyle}>Operator Gate</h2>
        <button style={backButtonStyle} onClick={onBack}>
          ← Back to Signals
        </button>
      </div>

      {frozenAction && !decisionEvent && (
        <OperatorGate
          actionId={frozenAction.action_id!}
          onDecision={onDecision}
        />
      )}

      {decisionEvent && (
        <div style={{ padding: "16px", background: "var(--color-surface)", borderRadius: "var(--radius-md)" }}>
          <div style={{ fontSize: "14px", color: "var(--color-text-muted)", marginBottom: "8px" }}>
            Decision Made
          </div>
          <div style={{ fontSize: "18px", fontWeight: "600", color: "var(--color-text)" }}>
            {(decisionEvent.payload as any)?.decision === "approved" ? "✓ Approved" : "✗ Aborted"}
          </div>
        </div>
      )}

      {incidentPayload && <IncidentRecord payload={incidentPayload} />}

      <div style={footerStyle}>
        Reasoning by VultronRetriever models via Vultr Serverless Inference
      </div>
    </div>
  );
}
