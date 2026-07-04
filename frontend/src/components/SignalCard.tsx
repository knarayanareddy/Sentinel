import { type CSSProperties } from "react";
import { ModelBadge } from "./ModelBadge";

interface SignalCardProps {
  title: string;
  score?: number;
  verdict?: string;
  confidence?: number;
  reasoning?: string;
  model: string;
  threshold?: number;
}

export function SignalCard({
  title,
  score,
  verdict,
  confidence,
  reasoning,
  model,
  threshold,
}: SignalCardProps) {
  const cardStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    padding: "16px",
    background: "var(--color-surface)",
    borderRadius: "var(--radius-md)",
    border: "1px solid var(--color-border)",
  };

  const headerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  };

  const titleStyle: CSSProperties = {
    fontSize: "14px",
    fontWeight: "500",
    color: "var(--color-text)",
  };

  const scoreStyle: CSSProperties = {
    fontSize: "28px",
    fontWeight: "500",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text)",
  };

  const metaStyle: CSSProperties = {
    display: "flex",
    gap: "12px",
    fontSize: "12px",
    color: "var(--color-text-muted)",
    fontFamily: "var(--font-mono)",
  };

  const reasoningStyle: CSSProperties = {
    fontSize: "13px",
    lineHeight: "1.5",
    color: "var(--color-text-muted)",
    padding: "8px",
    background: "rgba(0, 0, 0, 0.2)",
    borderRadius: "var(--radius-sm)",
  };

  const displayValue =
    verdict !== undefined
      ? `${verdict}${confidence !== undefined ? ` (${confidence}%)` : ""}`
      : score !== undefined
      ? score.toFixed(2)
      : "N/A";

  return (
    <div style={cardStyle}>
      <div style={headerStyle}>
        <span style={titleStyle}>{title}</span>
        <ModelBadge model={model} />
      </div>
      <div style={scoreStyle}>{displayValue}</div>
      {threshold !== undefined && (
        <div style={metaStyle}>
          Threshold: {threshold.toFixed(2)}
        </div>
      )}
      {reasoning && (
        <div style={reasoningStyle}>{reasoning}</div>
      )}
    </div>
  );
}
