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
  onBack: () => void;
  onProceedToGate: () => void;
}

export function SignalPage({ events, onBack, onProceedToGate }: SignalPageProps) {
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
      const citations: Citation[] = (frozenEvent?.payload as any)?.citations ?? [];

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h2 style={titleStyle}>Signal Breakdown</h2>
        <button style={backButtonStyle} onClick={onBack}>
          ← Back to Monitor
        </button>
      </div>

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
