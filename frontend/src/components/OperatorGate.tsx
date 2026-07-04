import { useState, type CSSProperties } from "react";

interface OperatorGateProps {
  actionId: string;
  onDecision: (approved: boolean) => void;
}

export function OperatorGate({ actionId, onDecision }: OperatorGateProps) {
  const [loading, setLoading] = useState(false);

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
    marginBottom: "8px",
  };

  const actionIdStyle: CSSProperties = {
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
    marginBottom: "16px",
  };

  const buttonsStyle: CSSProperties = {
    display: "flex",
    gap: "12px",
    width: "100%",
  };

  const buttonBaseStyle: CSSProperties = {
    flex: 1,
    padding: "16px",
    fontSize: "16px",
    fontWeight: "600",
    fontFamily: "var(--font-body)",
    borderRadius: "var(--radius-md)",
    cursor: loading ? "not-allowed" : "pointer",
    transition: "all 0.2s ease",
    opacity: loading ? 0.6 : 1,
  };

  const approveStyle: CSSProperties = {
    ...buttonBaseStyle,
    background: "var(--color-executed)",
    color: "white",
    border: "2px solid var(--color-executed)",
  };

  const abortStyle: CSSProperties = {
    ...buttonBaseStyle,
    background: "transparent",
    color: "var(--color-frozen)",
    border: "2px solid var(--color-frozen)",
  };

  const handleDecision = async (approved: boolean) => {
    if (loading) return;
    setLoading(true);
    try {
      onDecision(approved);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>Operator Decision Required</div>
      <div style={actionIdStyle}>Action ID: {actionId}</div>
      <div style={buttonsStyle}>
        <button
          style={approveStyle}
          onClick={() => handleDecision(true)}
          disabled={loading}
        >
          ✓ APPROVE
        </button>
        <button
          style={abortStyle}
          onClick={() => handleDecision(false)}
          disabled={loading}
        >
          ✗ ABORT
        </button>
      </div>
    </div>
  );
}
