export type WorkflowRunStatus =
  | "pending"
  | "validating"
  | "retrieving"
  | "assessing"
  | "executing"
  | "reviewing"
  | "completed"
  | "failed"
  | "cancelled";

export type TransportType = "auto" | "websocket" | "sse" | "connecting";

export interface WorkflowStep {
  stepName: string;
  status: string;
  timestamp?: string;
}

export interface WorkflowReviewData {
  decision?: string | null;
  comment?: string | null;
  deadline?: string | null;
  factors?: string[];
}

export interface WorkflowEvent {
  type: string;
  taskId: string;
  timestamp?: string;
  status?: string;
  currentStep?: string;
  stepName?: string;
  stepStatus?: string;
  riskLevel?: string;
  isHumanReviewNeeded?: boolean;
  finalResponse?: string | null;
  error?: string | null;
  totalTokens?: number;
  totalCost?: number;
  reviewData?: WorkflowReviewData;
  decision?: string | null;
  comment?: string | null;
  transport?: string;
}

export interface WorkflowState {
  taskId: string;
  status: WorkflowRunStatus | "idle" | "paused" | "error";
  currentStep: string;
  finalResponse: string | null;
  error: string | null;
  isHumanReviewNeeded: boolean;
  reviewData?: WorkflowReviewData;
  totalTokens: number;
  totalCost: number;
  steps: WorkflowStep[];
  transport: TransportType;
  connected: boolean;
}

export interface WorkflowSummary {
  id: string;
  user_id: string;
  session_id: string | null;
  current_step: string;
  current_status: WorkflowRunStatus;
  risk_level: string;
  is_human_review_needed: boolean;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}
