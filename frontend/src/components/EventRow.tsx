import { type CSSProperties } from "react";
import type {
  SentinelEvent,
  AgentPlanPayload,
  RetrievalPassPayload,
  ToolCalledPayload,
  DriftScoredPayload,
  MaarsProbePayload,
  CitationCheckedPayload,
  ActionProposedPayload,
  ActionExecutedPayload,
  OperatorDecisionPayload,
  ErrorPayload,
} from "../types";
import { ModelBadge } from "./ModelBadge";
import { RetrievalBadge } from "./RetrievalBadge";
import { stepForEvent } from "../steps";

interface EventRowProps {
  event: SentinelEvent;
}

const EVENT_COLORS: Record<string, string> = {
  AGENT_PLAN: "#81C784",
  ACTION_PROPOSED: "#FFB74D",
  RETRIEVAL_PASS: "#81C784",
  TOOL_CALLED: "#64B5F6",
  DRIFT_SCORED: "#FFB74D",
  MAARS_PROBE: "#BA68C8",
  CITATION_CHECKED: "#4DD0E1",
  ACTION_EXECUTED: "#81C784",
  ACTION_FROZEN: "#E53935",
  INCIDENT_SEALED: "#81C784",
  OPERATOR_DECISION: "#64B5F6",
  ERROR: "#E53935",
};

export function EventRow({ event }: EventRowProps) {
  const color = EVENT_COLORS[event.event_type] ?? "var(--color-text)";
  const step = stepForEvent(event);

  const rowStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    padding: "12px 16px",
    background: "var(--color-surface)",
    borderRadius: "var(--radius-md)",
    border: `1px solid ${color}33`,
  };

  const headerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  };

  const eventTypeStyle: CSSProperties = {
    fontSize: "12px",
    fontWeight: "600",
    fontFamily: "var(--font-mono)",
    color,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  };

  const timestampStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
  };

  const stepChipStyle: CSSProperties = {
    fontSize: "10px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-sm)",
    padding: "1px 6px",
    letterSpacing: "0.05em",
  };

  const contentStyle: CSSProperties = {
    fontSize: "13px",
    color: "var(--color-text)",
    lineHeight: "1.5",
  };

  const badgesStyle: CSSProperties = {
    display: "flex",
    gap: "8px",
    flexWrap: "wrap",
  };

  const renderContent = () => {
    switch (event.event_type) {
      case "AGENT_PLAN": {
        const payload = event.payload as AgentPlanPayload;
        return (
          <div style={contentStyle}>
            <div>Agent planning investigation with {payload.steps.length} steps</div>
            <div style={badgesStyle}>
              <ModelBadge model={payload.model} />
            </div>
          </div>
        );
      }

      case "RETRIEVAL_PASS": {
        const payload = event.payload as RetrievalPassPayload;
        return (
          <div style={contentStyle}>
            <div>{payload.result_summary}</div>
            <div style={badgesStyle}>
              <RetrievalBadge
                passNumber={payload.pass_number}
                documentsRetrieved={payload.documents_retrieved}
              />
              <ModelBadge model={payload.reasoning_model} />
            </div>
          </div>
        );
      }

      case "TOOL_CALLED": {
        const payload = event.payload as ToolCalledPayload;
        return (
          <div style={contentStyle}>
            <div>{payload.result_summary}</div>
            <div style={{ ...badgesStyle, fontSize: "11px", color: "var(--color-text-muted)" }}>
              Tool: {payload.tool_name}
            </div>
          </div>
        );
      }

      case "DRIFT_SCORED": {
        const payload = event.payload as DriftScoredPayload;
        return (
          <div style={contentStyle}>
            <div>
              Drift Score: <strong>{payload.score.toFixed(2)}</strong>
              {payload.drifted && " ⚠ DRIFTED"}
            </div>
            <div style={badgesStyle}>
              <ModelBadge model={payload.model} />
            </div>
          </div>
        );
      }

      case "MAARS_PROBE": {
        const payload = event.payload as MaarsProbePayload;
        return (
          <div style={contentStyle}>
            <div>
              Verdict: <strong>{payload.verdict}</strong> ({payload.confidence}%)
            </div>
            <div style={{ fontSize: "12px", color: "var(--color-text-muted)", marginTop: "4px" }}>
              {payload.reasoning}
            </div>
            <div style={badgesStyle}>
              <ModelBadge model={payload.model} />
            </div>
          </div>
        );
      }

      case "CITATION_CHECKED": {
        const payload = event.payload as CitationCheckedPayload;
        return (
          <div style={contentStyle}>
            <div>
              Citation Score: <strong>{payload.score.toFixed(2)}</strong>
              {payload.missing_clauses.length > 0 && (
                <span style={{ color: "var(--color-frozen)" }}>
                  {" "}
                  — Missing: {payload.missing_clauses.join(", ")}
                </span>
              )}
            </div>
            <div style={badgesStyle}>
              <ModelBadge model={payload.model} />
            </div>
          </div>
        );
      }

      case "ACTION_PROPOSED": {
        const payload = event.payload as ActionProposedPayload;
        return (
          <div style={contentStyle}>
            <div>{payload.action}</div>
            <div style={{ ...badgesStyle, fontSize: "11px", color: "var(--color-text-muted)" }}>
              Tool: {payload.tool} {payload.is_irreversible && "⚠ IRREVERSIBLE"}
            </div>
          </div>
        );
      }

      case "ACTION_EXECUTED": {
        const payload = event.payload as ActionExecutedPayload;
        return <div style={contentStyle}>{payload.action}</div>;
      }

      case "ACTION_FROZEN":
        return (
          <div style={{ ...contentStyle, color: "var(--color-frozen)" }}>
            Action frozen — awaiting operator decision
          </div>
        );

      case "INCIDENT_SEALED":
        return (
          <div style={contentStyle}>
            Incident sealed with SHA-256 hash
          </div>
        );

      case "OPERATOR_DECISION": {
        const payload = event.payload as OperatorDecisionPayload;
        const approved = payload.decision === "approved";
        return (
          <div style={{ ...contentStyle, color: approved ? "var(--color-executed)" : "var(--color-aborted)" }}>
            Operator {approved ? "approved" : "aborted"} the frozen action
            {approved ? " — memo dispatched" : " — action cancelled"}
          </div>
        );
      }

      case "ERROR": {
        const payload = event.payload as ErrorPayload;
        return (
          <div style={{ ...contentStyle, color: "var(--color-frozen)" }}>
            Error: {payload.message}
          </div>
        );
      }

      default:
        return <div style={contentStyle}>{JSON.stringify(event.payload)}</div>;
    }
  };

  return (
    <div style={rowStyle}>
      <div style={headerStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {step !== null && <span style={stepChipStyle}>STEP {step}/7</span>}
          <span style={eventTypeStyle}>{event.event_type}</span>
        </div>
        <span style={timestampStyle}>
          {new Date(event.timestamp * 1000).toLocaleTimeString()}
        </span>
      </div>
      {renderContent()}
    </div>
  );
}
