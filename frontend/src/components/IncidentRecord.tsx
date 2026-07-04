import { useState, type CSSProperties } from "react";
import type { IncidentSealedPayload } from "../types";

interface IncidentRecordProps {
  payload: IncidentSealedPayload;
}

export function IncidentRecord({ payload }: IncidentRecordProps) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const containerStyle: CSSProperties = {
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

  const toggleButtonStyle: CSSProperties = {
    padding: "4px 8px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    background: "transparent",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-sm)",
    color: "var(--color-text-muted)",
    cursor: "pointer",
  };

  const hashContainerStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    padding: "12px",
    background: "rgba(0, 0, 0, 0.2)",
    borderRadius: "var(--radius-sm)",
  };

  const hashLabelStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  };

  const hashValueStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    fontSize: "13px",
    fontFamily: "var(--font-mono)",
    color: "#81C784",
    wordBreak: "break-all",
  };

  const copyButtonStyle: CSSProperties = {
    padding: "4px 8px",
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    background: "rgba(129, 199, 132, 0.15)",
    border: "1px solid rgba(129, 199, 132, 0.3)",
    borderRadius: "var(--radius-sm)",
    color: "#81C784",
    cursor: "pointer",
    whiteSpace: "nowrap",
  };

  const jsonStyle: CSSProperties = {
    padding: "12px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    background: "rgba(0, 0, 0, 0.2)",
    borderRadius: "var(--radius-sm)",
    color: "var(--color-text-muted)",
    whiteSpace: "pre-wrap",
    wordBreak: "break-all",
    maxHeight: "300px",
    overflow: "auto",
  };

  const handleCopyHash = () => {
    navigator.clipboard.writeText(payload.integrity_hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <span style={titleStyle}>Incident Record</span>
        <button
          style={toggleButtonStyle}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Hide" : "Show"} JSON
        </button>
      </div>

      <div style={hashContainerStyle}>
        <div style={hashLabelStyle}>SHA-256 Integrity Hash</div>
        <div style={hashValueStyle}>
          <code>{payload.integrity_hash}</code>
          <button style={copyButtonStyle} onClick={handleCopyHash}>
            {copied ? "✓ Copied" : "Copy"}
          </button>
        </div>
      </div>

      {expanded && (
        <pre style={jsonStyle}>
          {JSON.stringify(payload, null, 2)}
        </pre>
      )}
    </div>
  );
}
