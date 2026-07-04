import type {
  SentinelEvent,
  RetrievalPassPayload,
  ActionProposedPayload,
  ActionExecutedPayload,
  OperatorDecisionPayload,
} from "./types";

export const STEP_LABELS = [
  "Plan investigation",
  "Retrieve covenant",
  "Retrieve history",
  "Calculate ratio",
  "Root-cause retrieval",
  "Draft memo",
  "Oversight gate",
];

const RETRIEVAL_STEP: Record<number, number> = { 1: 2, 2: 3, 3: 5 };

/** Map an event to its 1-based agent-loop step, or null if it has none. */
export function stepForEvent(event: SentinelEvent): number | null {
  switch (event.event_type) {
    case "AGENT_PLAN":
      return 1;
    case "RETRIEVAL_PASS": {
      const p = event.payload as RetrievalPassPayload;
      return RETRIEVAL_STEP[p.pass_number] ?? 5;
    }
    case "TOOL_CALLED":
      return 4;
    case "ACTION_PROPOSED": {
      const p = event.payload as ActionProposedPayload;
      return p.is_irreversible ? 7 : 6;
    }
    case "ACTION_EXECUTED": {
      const p = event.payload as ActionExecutedPayload;
      return p.action.toLowerCase().includes("draft") ? 6 : 7;
    }
    case "DRIFT_SCORED":
    case "MAARS_PROBE":
    case "CITATION_CHECKED":
    case "ACTION_FROZEN":
    case "OPERATOR_DECISION":
    case "INCIDENT_SEALED":
      return 7;
    default:
      return null;
  }
}

export type StepState = "pending" | "active" | "done" | "frozen" | "aborted";

/** Compute the state of each of the 7 steps from the event stream. */
export function stepStates(events: SentinelEvent[]): StepState[] {
  const reached = new Set<number>();
  let frozen = false;
  let decision: string | null = null;
  for (const e of events) {
    const s = stepForEvent(e);
    if (s !== null) reached.add(s);
    if (e.event_type === "ACTION_FROZEN") frozen = true;
    if (e.event_type === "OPERATOR_DECISION") {
      decision = (e.payload as OperatorDecisionPayload).decision;
    }
  }
  const highest = reached.size > 0 ? Math.max(...reached) : 0;
  return STEP_LABELS.map((_, i) => {
    const step = i + 1;
    if (!reached.has(step)) return "pending";
    if (step < highest) return "done";
    if (step === 7) {
      if (decision === "aborted") return "aborted";
      if (decision === "approved") return "done";
      if (frozen) return "frozen";
    }
    return step === highest ? "active" : "done";
  });
}
