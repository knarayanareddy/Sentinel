import { type CSSProperties } from "react";
import type { ActionFrozenPayload } from "../types";

interface FreezeAlertProps {
  payload: ActionFrozenPayload;
  onClick: () => void;
}

export function FreezeAlert({ payload, onClick }: FreezeAlertProps) {
  const alertStyle: CSSProperties = {
    width: "100%",
    padding: "16px 24px",
    background: "rgba(229, 57, 53, 0.15)",
    border: "2px solid var(--color-frozen)",
    borderRadius: "var(--radius-md)",
    cursor: "pointer",
    transition: "all 0.2s ease",
  };

  const headerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  };

  const titleStyle: CSSProperties = {
    fontSize: "18px",
    fontWeight: "600",
    color: "var(--color-frozen)",
    fontFamily: "var(--font-mono)",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  };

  const timestampStyle: CSSProperties = {
    fontSize: "12px",
    color: "var(--color-text-muted)",
    fontFamily: "var(--font-mono)",
  };

  const reasonStyle: CSSProperties = {
    fontSize: "14px",
    color: "var(--color-text)",
    lineHeight: "1.5",
    marginBottom: "12px",
  };

  const metricsStyle: CSSProperties = {
    display: "flex",
    gap: "24px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
  };

  const metricLabelStyle: CSSProperties = {
    color: "var(--color-text-muted)",
    marginRight: "4px",
  };

  const metricValueStyle: CSSProperties = {
    color: "var(--color-text)",
    fontWeight: "500",
  };

  return (
    <div style={alertStyle} onClick={onClick}>
      <div style={headerStyle}>
        <span style={titleStyle}>⚠ ACTION FROZEN</span>
        <span style={timestampStyle}>
          {new Date().toLocaleTimeString()}
        </span>
      </div>
      <div style={reasonStyle}>{payload.freeze_reason}</div>
      <div style={metricsStyle}>
        <div>
          <span style={metricLabelStyle}>Drift:</span>
          <span style={metricValueStyle}>{(payload.drift_score ?? 0).toFixed(2)}</span>
        </div>
        <div>
          <span style={metricLabelStyle}>MAARS:</span>
          <span style={metricValueStyle}>{payload.maars_verdict ?? "—"}</span>
        </div>
        <div>
          <span style={metricLabelStyle}>Citation:</span>
          <span style={metricValueStyle}>{(payload.citation_score ?? 0).toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
