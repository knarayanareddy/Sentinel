import { useEffect, useRef, type CSSProperties } from "react";
import { useCorpus } from "../hooks/useCorpus";

interface DocumentDrawerProps {
  documentName: string;
  excerpt?: string;
  onClose: () => void;
}

function findMatch(content: string, excerpt: string): [number, number] | null {
  const cleaned = excerpt.replace(/^["'\s]+|["'\s.]+$/g, "").replace(/\.\.\.$/, "");
  if (!cleaned) return null;
  const haystack = content.toLowerCase();
  for (const probe of [cleaned, cleaned.slice(0, 60), cleaned.slice(0, 30)]) {
    const idx = haystack.indexOf(probe.toLowerCase());
    if (idx !== -1) return [idx, idx + probe.length];
  }

  // Fuzzy fallback: highlight the line sharing the most significant words
  const words = new Set(
    cleaned.toLowerCase().split(/\W+/).filter((w) => w.length > 3)
  );
  if (words.size === 0) return null;
  let best: [number, number] | null = null;
  let bestScore = 2;
  let offset = 0;
  for (const line of content.split("\n")) {
    const lineWords = new Set(line.toLowerCase().split(/\W+/));
    const score = [...words].filter((w) => lineWords.has(w)).length;
    if (score > bestScore && line.trim().length > 0) {
      bestScore = score;
      best = [offset, offset + line.length];
    }
    offset += line.length + 1;
  }
  return best;
}

export function DocumentDrawer({ documentName, excerpt, onClose }: DocumentDrawerProps) {
  const documents = useCorpus();
  const highlightRef = useRef<HTMLElement | null>(null);

  const doc = documents.find((d) => d.name === documentName);
  const match = doc && excerpt ? findMatch(doc.content, excerpt) : null;

  useEffect(() => {
    highlightRef.current?.scrollIntoView({ block: "center" });
  }, [doc, excerpt]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const overlayStyle: CSSProperties = {
    position: "fixed",
    inset: 0,
    background: "rgba(0, 0, 0, 0.55)",
    zIndex: 90,
  };

  const drawerStyle: CSSProperties = {
    position: "fixed",
    top: 0,
    right: 0,
    bottom: 0,
    width: "560px",
    maxWidth: "90vw",
    background: "var(--color-surface)",
    borderLeft: "1px solid var(--color-border)",
    zIndex: 91,
    display: "flex",
    flexDirection: "column",
  };

  const headerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 20px",
    borderBottom: "1px solid var(--color-border)",
  };

  const titleStyle: CSSProperties = {
    fontSize: "14px",
    fontFamily: "var(--font-mono)",
    color: "#81C784",
    fontWeight: "600",
  };

  const labelStyle: CSSProperties = {
    fontSize: "11px",
    fontFamily: "var(--font-mono)",
    letterSpacing: "0.1em",
    color: "var(--color-text-muted)",
    textTransform: "uppercase",
  };

  const closeStyle: CSSProperties = {
    padding: "6px 12px",
    fontSize: "13px",
    fontFamily: "var(--font-mono)",
    background: "transparent",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-sm)",
    color: "var(--color-text-muted)",
    cursor: "pointer",
  };

  const bodyStyle: CSSProperties = {
    flex: 1,
    overflow: "auto",
    padding: "20px",
    fontSize: "13px",
    fontFamily: "var(--font-mono)",
    lineHeight: "1.7",
    color: "var(--color-text)",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  };

  const highlightStyle: CSSProperties = {
    background: "rgba(249, 168, 37, 0.25)",
    outline: "1px solid var(--color-pending)",
    borderRadius: "2px",
    color: "inherit",
  };

  return (
    <>
      <div style={overlayStyle} onClick={onClose} />
      <div style={drawerStyle}>
        <div style={headerStyle}>
          <div>
            <div style={labelStyle}>Source Document</div>
            <div style={titleStyle}>{documentName}</div>
          </div>
          <button style={closeStyle} onClick={onClose}>
            ✕ Close
          </button>
        </div>
        <div style={bodyStyle}>
          {!doc && <span style={{ color: "var(--color-text-muted)" }}>Loading document…</span>}
          {doc && !match && doc.content}
          {doc && match && (
            <>
              {doc.content.slice(0, match[0])}
              <mark ref={highlightRef} style={highlightStyle}>
                {doc.content.slice(match[0], match[1])}
              </mark>
              {doc.content.slice(match[1])}
            </>
          )}
        </div>
      </div>
    </>
  );
}
