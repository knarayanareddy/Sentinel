import { useState, type CSSProperties } from "react";
import type { ActionFrozenPayload, ActionProposedPayload, Citation } from "../types";
import { CitationList } from "./CitationList";

interface OperatorGateProps {
  actionId: string;
  frozenPayload: ActionFrozenPayload;
  proposedPayload?: ActionProposedPayload;
  citations: Citation[];
  onDecision: (approved: boolean) => void;
}

export function OperatorGate({
  actionId,
  frozenPayload,
  proposedPayload,
  citations,
  onDecision,
}: OperatorGateProps) {
  const [loading, setLoading] = useState(false);
  const [armed, setArmed] = useState(false);

  const containerStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    padding: "24px",
    background: "var(--color-surface)",
    borderRadius: "var(--radius-md)",
    border: "1px solid var(--color-border)",
  };

  const headerStyle: CSSProperties = {
    fontSize: "16px",
    fontWeight: "500",
    color: "var(--color-text)",
  };

  const actionIdStyle: CSSProperties = {
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
  };

  const actionBoxStyle: CSSProperties = {
    padding: "14px 16px",
    background: "rgba(0, 0, 0, 0.25)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-sm)",
    fontSize: "14px",
    lineHeight: 1.6,
    color: "var(--color-text)",
  };

  const actionMetaStyle: CSSProperties = {
    marginTop: "8px",
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-pending)",
  };

  const signalsRowStyle: CSSProperties = {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
  };

  const signalChipStyle = (triggered: boolean): CSSProperties => ({
    display: "flex",
    flexDirection: "column",
    gap: "2px",
    padding: "10px 14px",
    minWidth: "140px",
    background: "rgba(0, 0, 0, 0.25)",
    border: `1px solid ${triggered ? "var(--color-frozen)" : "var(--color-border)"}`,
    borderRadius: "var(--radius-sm)",
  });

  const signalLabelStyle: CSSProperties = {
    fontSize: "10px",
    fontFamily: "var(--font-mono)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "var(--color-text-muted)",
  };

  const signalValueStyle = (triggered: boolean): CSSProperties => ({
    fontSize: "16px",
    fontFamily: "var(--font-mono)",
    fontWeight: 600,
    color: triggered ? "var(--color-frozen)" : "var(--color-text)",
  });

  const freezeReasonStyle: CSSProperties = {
    fontSize: "13px",
    color: "var(--color-frozen)",
    fontFamily: "var(--font-mono)",
  };

  const sectionLabelStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "var(--color-text-muted)",
  };

  const buttonsStyle: CSSProperties = {
    display: "flex",
    gap: "12px",
    alignItems: "center",
    marginTop: "4px",
  };

  const approveStyle: CSSProperties = {
    padding: "14px 28px",
    fontSize: "15px",
    fontWeight: "600",
    fontFamily: "var(--font-body)",
    borderRadius: "var(--radius-md)",
    cursor: loading ? "not-allowed" : "pointer",
    opacity: loading ? 0.6 : 1,
    transition: "all 0.2s ease",
    background: armed ? "var(--color-executed)" : "transparent",
    color: armed ? "white" : "var(--color-executed)",
    border: "2px solid var(--color-executed)",
  };

  const abortStyle: CSSProperties = {
    padding: "14px 28px",
    fontSize: "15px",
    fontWeight: "500",
    fontFamily: "var(--font-body)",
    borderRadius: "var(--radius-md)",
    cursor: loading ? "not-allowed" : "pointer",
    opacity: loading ? 0.6 : 1,
    background: "transparent",
    color: "var(--color-text-muted)",
    border: "1px solid var(--color-border)",
  };

  const armedHintStyle: CSSProperties = {
    fontSize: "12px",
    color: "var(--color-pending)",
    fontFamily: "var(--font-mono)",
  };

  const handleApprove = () => {
    if (loading) return;
    if (!armed) {
      setArmed(true);
      return;
    }
    setLoading(true);
    try {
      onDecision(true);
    } finally {
      setLoading(false);
    }
  };

  const handleAbort = () => {
    if (loading) return;
    setLoading(true);
    try {
      onDecision(false);
    } finally {
      setLoading(false);
    }
  };

  const drifted = frozenPayload.drift_score >= 0.4;
  const maarsTriggered = frozenPayload.maars_verdict === "NO";
  const citationLow = frozenPayload.citation_score < 0.6;

  return (
    <div style={containerStyle}>
      <div>
        <div style={headerStyle}>Operator Decision Required</div>
        <div style={actionIdStyle}>Action ID: {actionId}</div>
      </div>

      {proposedPayload && (
        <div>
          <div style={{ ...sectionLabelStyle, marginBottom: "6px" }}>Frozen Action</div>
          <div style={actionBoxStyle}>
            {proposedPayload.action}
            <div style={actionMetaStyle}>
              Tool: {proposedPayload.tool}
              {proposedPayload.is_irreversible && " · ⚠ IRREVERSIBLE"}
            </div>
          </div>
        </div>
      )}

      <div style={freezeReasonStyle}>■ {frozenPayload.freeze_reason}</div>

      <div style={signalsRowStyle}>
        <div style={signalChipStyle(drifted)}>
          <span style={signalLabelStyle}>Drift Score</span>
          <span style={signalValueStyle(drifted)}>{frozenPayload.drift_score.toFixed(2)}</span>
        </div>
        <div style={signalChipStyle(maarsTriggered)}>
          <span style={signalLabelStyle}>MAARS Verdict</span>
          <span style={signalValueStyle(maarsTriggered)}>
            {frozenPayload.maars_verdict} ({frozenPayload.maars_confidence}%)
          </span>
        </div>
        <div style={signalChipStyle(citationLow)}>
          <span style={signalLabelStyle}>Citation Score</span>
          <span style={signalValueStyle(citationLow)}>{frozenPayload.citation_score.toFixed(2)}</span>
        </div>
      </div>

      {citations.length > 0 && (
        <div>
          <div style={{ ...sectionLabelStyle, marginBottom: "6px" }}>Evidence Citations</div>
          <CitationList citations={citations} />
        </div>
      )}

      <div style={buttonsStyle}>
        <button style={approveStyle} onClick={handleApprove} disabled={loading}>
          {armed ? "✓ Confirm — Approve & Send" : "Approve & Send…"}
        </button>
        <button style={abortStyle} onClick={handleAbort} disabled={loading}>
          ✗ Abort Action
        </button>
        {armed && <span style={armedHintStyle}>Click again to confirm the irreversible send</span>}
      </div>
    </div>
  );
}
