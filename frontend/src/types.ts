export type EventType =
  | "RUN_STARTED"
  | "AGENT_PLAN"
  | "ACTION_PROPOSED"
  | "RETRIEVAL_PASS"
  | "TOOL_CALLED"
  | "DRIFT_SCORED"
  | "MAARS_PROBE"
  | "CITATION_CHECKED"
  | "ACTION_EXECUTED"
  | "ACTION_FROZEN"
  | "INCIDENT_SEALED"
  | "OPERATOR_DECISION"
  | "ERROR";

export interface SentinelEvent {
  event_id: string;
  event_type: EventType;
  timestamp: number;
  payload: unknown;
  action_id?: string;
}

export interface Citation {
  document: string;
  clause: string;
  excerpt: string;
  retrieval_score?: number;
}

export type RunStartedPayload = {
  scenario: string;
  label: string;
};

export type AgentPlanPayload = {
  steps: string[];
  model: string;
};

export type RetrievalPassPayload = {
  pass_number: number;
  query: string;
  documents_retrieved: string[];
  reasoning_model: string;
  rerank_model?: string;
  result_summary: string;
};

export type ToolCalledPayload = {
  tool_name: string;
  parameters: Record<string, unknown>;
  result_summary: string;
};

export type DriftScoredPayload = {
  score: number;
  drifted: boolean;
  threshold: number;
  model: string;
};

export type MaarsProbePayload = {
  verdict: "YES" | "NO";
  confidence: number;
  reasoning: string;
  model: string;
  severity?: string;
};

export type CitationCheckedPayload = {
  score: number;
  missing_clauses: string[];
  model: string;
};

export type ActionFrozenPayload = {
  action_id: string;
  freeze_reason: string;
  drift_score: number;
  maars_verdict: string;
  maars_confidence: number;
  citation_score: number;
};

export type IncidentSealedPayload = {
  incident_path: string;
  integrity_hash: string;
  incident_id: string;
};

export type OperatorDecisionPayload = {
  decision: "approved" | "aborted";
  resolved_at: number;
};

export type ActionProposedPayload = {
  action: string;
  tool: string;
  is_irreversible: boolean;
};

export type ActionExecutedPayload = {
  action: string;
};

export type ErrorPayload = {
  message: string;
};
