import { type CSSProperties } from "react";

interface RetrievalBadgeProps {
  passNumber: number;
  documentsRetrieved?: string[];
}

export function RetrievalBadge({ passNumber, documentsRetrieved }: RetrievalBadgeProps) {
  const style: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    gap: "4px",
    padding: "2px 8px",
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    borderRadius: "var(--radius-sm)",
    background: "rgba(76, 175, 80, 0.15)",
    border: "1px solid rgba(76, 175, 80, 0.3)",
    color: "#81C784",
  };

  const docsText = documentsRetrieved?.length
    ? ` (${documentsRetrieved.length} docs)`
    : "";

  return (
    <span style={style}>
      Pass {passNumber}{docsText}
    </span>
  );
}
