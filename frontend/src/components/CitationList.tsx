import { useState, type CSSProperties } from "react";
import type { Citation } from "../types";
import { DocumentDrawer } from "./DocumentDrawer";

interface CitationListProps {
  citations: Citation[];
}

export function CitationList({ citations }: CitationListProps) {
  const [openCitation, setOpenCitation] = useState<Citation | null>(null);

  if (!citations || citations.length === 0) {
    return (
      <div style={{ padding: "12px", color: "var(--color-text-muted)", fontSize: "13px" }}>
        No citations available
      </div>
    );
  }

  const containerStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    padding: "12px",
    background: "var(--color-surface)",
    borderRadius: "var(--radius-md)",
  };

  const citationStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    padding: "8px",
    background: "rgba(0, 0, 0, 0.2)",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--color-border)",
    cursor: "pointer",
    textAlign: "left",
    width: "100%",
    font: "inherit",
    color: "inherit",
  };

  const headerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
  };

  const documentStyle: CSSProperties = {
    color: "#81C784",
    fontWeight: "500",
  };

  const clauseStyle: CSSProperties = {
    color: "var(--color-text-muted)",
  };

  const openHintStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
  };

  const excerptStyle: CSSProperties = {
    fontSize: "13px",
    color: "var(--color-text)",
    lineHeight: "1.4",
    fontFamily: "var(--font-mono)",
  };

  const scoreStyle: CSSProperties = {
    fontSize: "11px",
    color: "var(--color-text-muted)",
    fontFamily: "var(--font-mono)",
  };

  return (
    <div style={containerStyle}>
      {citations.map((citation, idx) => (
        <button
          key={idx}
          style={citationStyle}
          onClick={() => setOpenCitation(citation)}
          title={`Open ${citation.document}`}
        >
          <div style={headerStyle}>
            <span style={documentStyle}>{citation.document}</span>
            <span style={clauseStyle}>{citation.clause}</span>
          </div>
          <div style={excerptStyle}>
            "{citation.excerpt}"
          </div>
          <div style={headerStyle}>
            {citation.retrieval_score !== undefined ? (
              <span style={scoreStyle}>Score: {citation.retrieval_score.toFixed(3)}</span>
            ) : (
              <span />
            )}
            <span style={openHintStyle}>View source →</span>
          </div>
        </button>
      ))}
      {openCitation && (
        <DocumentDrawer
          documentName={openCitation.document}
          excerpt={openCitation.excerpt}
          onClose={() => setOpenCitation(null)}
        />
      )}
    </div>
  );
}
