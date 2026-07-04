import { type CSSProperties } from "react";

interface ModelBadgeProps {
  model: string;
}

// Map full model names to short display names
const MODEL_SHORT_NAMES: Record<string, string> = {
  "Qwen/Qwen3.6-27B": "Prime", // Used for both Prime and Core reasoning
  "deepseek-ai/DeepSeek-V4-Flash": "Flash",
  "vultr/VultronRetrieverFlash-Qwen3.5-0.8B": "ReRank",
};

export function ModelBadge({ model }: ModelBadgeProps) {
  const shortName = MODEL_SHORT_NAMES[model] ?? model.split("/").pop() ?? model;

  const style: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    padding: "2px 6px",
    fontSize: "10px",
    fontFamily: "var(--font-mono)",
    borderRadius: "var(--radius-sm)",
    background: "rgba(33, 150, 243, 0.15)",
    border: "1px solid rgba(33, 150, 243, 0.3)",
    color: "#64B5F6",
  };

  return (
    <span style={style} title={model}>
      {shortName}
    </span>
  );
}
