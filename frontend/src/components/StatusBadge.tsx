import { type CSSProperties } from "react";

interface StatusBadgeProps {
  status: string;
}

const STATUS_COLORS: Record<string, string> = {
  frozen: "var(--color-frozen)",
  executed: "var(--color-executed)",
  pending: "var(--color-pending)",
  aborted: "var(--color-aborted)",
  resumed: "var(--color-resumed)",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const color = STATUS_COLORS[status.toLowerCase()] ?? "var(--color-text-muted)";

  const style: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    padding: "2px 8px",
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    border: `1px solid ${color}`,
    borderRadius: "var(--radius-sm)",
    color,
    background: `${color}14`,
  };

  return <span style={style}>{status}</span>;
}
