import { useState } from "react";

import type { WorkflowReviewData } from "../types/workflow";

export function HumanReviewPanel({
  details,
  onDecision,
}: {
  details?: WorkflowReviewData;
  onDecision: (decision: "approved" | "rejected", reviewerId: string, comment: string) => void;
}) {
  const [reviewerId, setReviewerId] = useState("reviewer-1");
  const [comment, setComment] = useState("");

  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
      <h3 className="text-lg font-semibold text-amber-900">Human Review Required</h3>
      <p className="mt-2 text-sm text-amber-800">
        This workflow paused for review. Use the controls below to approve or reject
        the run.
      </p>
      <div className="mt-4 space-y-3">
        <input
          className="w-full rounded-xl border border-amber-200 bg-white px-3 py-2 text-sm"
          value={reviewerId}
          onChange={(event) => setReviewerId(event.target.value)}
          placeholder="Reviewer ID"
        />
        <textarea
          className="min-h-24 w-full rounded-xl border border-amber-200 bg-white px-3 py-2 text-sm"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="Add an approval or rejection note"
        />
        {details?.factors?.length ? (
          <div className="rounded-xl bg-white p-3 text-sm text-amber-900">
            <p className="font-medium">Risk factors</p>
            <ul className="mt-2 space-y-1">
              {details.factors.map((factor) => (
                <li key={factor}>{factor}</li>
              ))}
            </ul>
          </div>
        ) : null}
        <div className="flex gap-3">
          <button
            className="rounded-xl bg-accent-600 px-4 py-2 text-sm font-medium text-white"
            onClick={() => onDecision("approved", reviewerId, comment)}
          >
            Approve
          </button>
          <button
            className="rounded-xl border border-amber-300 px-4 py-2 text-sm font-medium text-amber-900"
            onClick={() => onDecision("rejected", reviewerId, comment)}
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}
