import { type CSSProperties } from "react";

interface ModelBadgeProps {
  model: string;
}

// Map full model names to short display names
const MODEL_SHORT_NAMES: Record<string, string> = {
  "nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16": "Prime",
  "nvidia/llama-3.2-1b-instruct": "Core",
  "nvidia/llama-3.2-3b-instruct": "Flash",
  "deepseek-ai/DeepSeek-V4-Flash": "Secondary",
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
