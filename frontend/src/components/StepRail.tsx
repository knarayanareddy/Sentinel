import { type CSSProperties } from "react";
import type { SentinelEvent } from "../types";
import { STEP_LABELS, stepStates, type StepState } from "../steps";

interface StepRailProps {
  events: SentinelEvent[];
}

const STATE_COLORS: Record<StepState, string> = {
  pending: "var(--color-text-muted)",
  active: "var(--color-pending)",
  done: "var(--color-executed)",
  frozen: "var(--color-frozen)",
  aborted: "var(--color-aborted)",
};

const STATE_MARKS: Record<StepState, string> = {
  pending: "○",
  active: "●",
  done: "✓",
  frozen: "■",
  aborted: "✗",
};

export function StepRail({ events }: StepRailProps) {
  const states = stepStates(events);

  const railStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "2px",
    padding: "16px",
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-md)",
    width: "230px",
    flexShrink: 0,
    alignSelf: "flex-start",
  };

  const titleStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    marginBottom: "10px",
  };

  const rowStyle = (state: StepState): CSSProperties => ({
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "7px 8px",
    borderRadius: "var(--radius-sm)",
    background: state === "active" || state === "frozen" ? "rgba(242, 240, 235, 0.05)" : "transparent",
  });

  const markStyle = (state: StepState): CSSProperties => ({
    width: "16px",
    textAlign: "center",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    color: STATE_COLORS[state],
    flexShrink: 0,
  });

  const numStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    width: "12px",
    flexShrink: 0,
  };

  const labelStyle = (state: StepState): CSSProperties => ({
    fontSize: "13px",
    color: state === "pending" ? "var(--color-text-muted)" : "var(--color-text)",
    fontWeight: state === "active" || state === "frozen" ? 500 : 400,
  });

  return (
    <div style={railStyle}>
      <div style={titleStyle}>Agent Loop</div>
      {STEP_LABELS.map((label, i) => {
        const state = states[i];
        return (
          <div key={label} style={rowStyle(state)}>
            <span style={markStyle(state)}>{STATE_MARKS[state]}</span>
            <span style={numStyle}>{i + 1}</span>
            <span style={labelStyle(state)}>
              {label}
              {state === "frozen" && " — frozen"}
            </span>
          </div>
        );
      })}
    </div>
  );
}
