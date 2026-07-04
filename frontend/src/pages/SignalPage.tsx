import { type CSSProperties } from "react";
import type {
  SentinelEvent,
  DriftScoredPayload,
  MaarsProbePayload,
  CitationCheckedPayload,
} from "../types";
import { SignalCard } from "../components/SignalCard";
import { CitationList } from "../components/CitationList";
import type { Citation } from "../types";

interface SignalPageProps {
  events: SentinelEvent[];
  onProceedToGate: () => void;
}

export function SignalPage({ events, onProceedToGate }: SignalPageProps) {
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

  const emptyStyle: CSSProperties = {
    padding: "48px 24px",
    textAlign: "center",
    fontSize: "14px",
    color: "var(--color-text-muted)",
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-md)",
  };

  const cardsStyle: CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: "16px",
  };

  const sectionTitleStyle: CSSProperties = {
    fontSize: "16px",
    fontWeight: "500",
    color: "var(--color-text)",
    marginTop: "8px",
  };

  const proceedButtonStyle: CSSProperties = {
    padding: "12px 24px",
    fontSize: "14px",
    fontFamily: "var(--font-body)",
    fontWeight: "500",
    background: "var(--color-resumed)",
    border: "none",
    borderRadius: "var(--radius-md)",
    color: "white",
    cursor: "pointer",
    alignSelf: "flex-start",
  };

  // Extract the latest signal events
  const driftEvent = events.find((e) => e.event_type === "DRIFT_SCORED");
  const maarsEvent = events.find((e) => e.event_type === "MAARS_PROBE");
  const citationEvent = events.find((e) => e.event_type === "CITATION_CHECKED");

  const driftPayload = driftEvent?.payload as DriftScoredPayload | undefined;
  const maarsPayload = maarsEvent?.payload as MaarsProbePayload | undefined;
  const citationPayload = citationEvent?.payload as CitationCheckedPayload | undefined;

  // Extract citations from frozen action event
  const frozenEvent = events.find((e) => e.event_type === "ACTION_FROZEN");
  const citations: Citation[] =
    ((frozenEvent?.payload as { citations?: Citation[] } | undefined)?.citations) ?? [];

  const hasSignals = Boolean(driftPayload || maarsPayload || citationPayload);

  if (!hasSignals) {
    return (
      <div style={containerStyle}>
        <h2 style={titleStyle}>Signal Breakdown</h2>
        <div style={emptyStyle}>
          No signals yet. Run the agent from the Monitor — drift, MAARS, and
          citation scores will appear here once the oversight gate evaluates an
          action.
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <h2 style={titleStyle}>Signal Breakdown</h2>

      <div style={cardsStyle}>
        {driftPayload && (
          <SignalCard
            title="Covenant Drift"
            score={driftPayload.score}
            reasoning={driftPayload.drifted ? "Action drifted from task" : "Action aligned with task"}
            model={driftPayload.model}
            threshold={driftPayload.threshold}
          />
        )}

        {maarsPayload && (
          <SignalCard
            title="MAARS Verdict"
            verdict={maarsPayload.verdict}
            confidence={maarsPayload.confidence}
            reasoning={maarsPayload.reasoning}
            model={maarsPayload.model}
          />
        )}

        {citationPayload && (
          <SignalCard
            title="Citation Completeness"
            score={citationPayload.score}
            reasoning={
              citationPayload.missing_clauses.length > 0
                ? `Missing: ${citationPayload.missing_clauses.join(", ")}`
                : "All required citations present"
            }
            model={citationPayload.model}
          />
        )}
      </div>

      <div>
        <h3 style={sectionTitleStyle}>Evidence Citations</h3>
        <CitationList citations={citations} />
      </div>

      <button style={proceedButtonStyle} onClick={onProceedToGate}>
        Proceed to Operator Gate →
      </button>
    </div>
  );
}
