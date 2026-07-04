import { type CSSProperties } from "react";
import type {
  SentinelEvent,
  IncidentSealedPayload,
  ActionFrozenPayload,
  ActionProposedPayload,
  OperatorDecisionPayload,
  Citation,
} from "../types";
import { OperatorGate } from "../components/OperatorGate";
import { IncidentRecord } from "../components/IncidentRecord";

interface GatePageProps {
  events: SentinelEvent[];
  frozenAction: SentinelEvent | null;
  onDecision: (approved: boolean) => void;
}

export function GatePage({ events, frozenAction, onDecision }: GatePageProps) {
  const containerStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "24px",
    padding: "24px",
    height: "100%",
    overflow: "auto",
  };

  const titleStyle: CSSProperties = {
    fontSize: "20px",
    fontWeight: "600",
    color: "var(--color-text)",
  };

  const footerStyle: CSSProperties = {
    padding: "12px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    borderTop: "1px solid var(--color-border)",
    marginTop: "auto",
  };

  const emptyStyle: CSSProperties = {
    padding: "48px 24px",
    textAlign: "center",
    fontSize: "14px",
    color: "var(--color-text-muted)",
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-md)",
  };

  const incidentEvent = events.find((e) => e.event_type === "INCIDENT_SEALED");
  const incidentPayload = incidentEvent?.payload as IncidentSealedPayload | undefined;

  const decisionEvent = events.find((e) => e.event_type === "OPERATOR_DECISION");
  const decisionPayload = decisionEvent?.payload as OperatorDecisionPayload | undefined;

  const frozenPayload = frozenAction?.payload as ActionFrozenPayload | undefined;
  const proposedEvent = events.find(
    (e) =>
      e.event_type === "ACTION_PROPOSED" &&
      (e.payload as ActionProposedPayload).is_irreversible
  );
  const proposedPayload = proposedEvent?.payload as ActionProposedPayload | undefined;
  const frozenEvent = events.find((e) => e.event_type === "ACTION_FROZEN");
  const citations: Citation[] =
    ((frozenEvent?.payload as { citations?: Citation[] } | undefined)?.citations) ?? [];

  return (
    <div style={containerStyle}>
      <h2 style={titleStyle}>Operator Gate</h2>

      {!frozenAction && !decisionEvent && (
        <div style={emptyStyle}>
          No action is awaiting a decision. When the oversight gate freezes an
          irreversible action, it will appear here for approval.
        </div>
      )}

      {frozenAction && frozenPayload && !decisionEvent && (
        <OperatorGate
          actionId={frozenAction.action_id!}
          frozenPayload={frozenPayload}
          proposedPayload={proposedPayload}
          citations={citations}
          onDecision={onDecision}
        />
      )}

      {decisionEvent && (
        <div style={{ padding: "16px", background: "var(--color-surface)", borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "14px", color: "var(--color-text-muted)", marginBottom: "8px" }}>
            Decision Made
          </div>
          <div style={{ fontSize: "18px", fontWeight: "600", color: decisionPayload?.decision === "approved" ? "var(--color-executed)" : "var(--color-aborted)" }}>
            {decisionPayload?.decision === "approved"
              ? "✓ Approved — escalation memo dispatched"
              : "✗ Aborted — action cancelled"}
          </div>
          {proposedPayload && (
            <div style={{ marginTop: "8px", fontSize: "13px", color: "var(--color-text-muted)" }}>
              {proposedPayload.action}
            </div>
          )}
        </div>
      )}

      {incidentPayload && <IncidentRecord payload={incidentPayload} />}

      <div style={footerStyle}>
        Reasoning by Qwen models. Retrieval by VultronRetriever.
      </div>
    </div>
  );
}
