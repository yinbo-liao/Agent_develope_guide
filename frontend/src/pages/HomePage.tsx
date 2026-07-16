import { useState } from "react";

import { CostWidget } from "../components/CostWidget";
import { WorkflowDashboard } from "../components/WorkflowDashboard";
import { runtimeConfig } from "../lib/runtime";
import type { WorkflowSummary } from "../types/workflow";

export function HomePage() {
  const [userId, setUserId] = useState("demo-user");
  const [query, setQuery] = useState("Review the deployment change plan for security impact.");
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [recentRuns, setRecentRuns] = useState<WorkflowSummary[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createWorkflow = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await fetch(`${runtimeConfig.apiBase}/api/v1/workflows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          input_query: query,
          token_budget: 10000,
          cost_budget_usd: 5,
        }),
      });
      if (!response.ok) {
        throw new Error("Failed to create workflow");
      }
      const workflow = (await response.json()) as WorkflowSummary;
      setActiveTaskId(workflow.id);
      setRecentRuns((current) => [workflow, ...current].slice(0, 5));
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Unknown error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900">
      <section className="mx-auto flex max-w-7xl flex-col gap-10 px-6 py-16">
        <div className="max-w-4xl space-y-5">
          <span className="inline-flex rounded-full border border-primary-100 bg-primary-50 px-3 py-1 text-sm font-medium text-primary-700">
            Wave 3 Monitoring
          </span>
          <h1 className="text-4xl font-semibold tracking-tight text-neutral-900">
            AI Workflow Platform
          </h1>
          <p className="text-lg leading-8 text-neutral-600">
            Create a workflow run, attach to its live event stream, and inspect step
            progression or human review state from the dashboard below.
          </p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
          <div className="space-y-6">
            <div className="rounded-2xl border border-neutral-200 bg-white p-6 shadow-soft">
              <h2 className="text-lg font-semibold text-neutral-900">Launch Workflow</h2>
              <div className="mt-4 space-y-4">
                <input
                  className="w-full rounded-2xl border border-neutral-200 px-4 py-3 text-sm"
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                  placeholder="User ID"
                />
                <textarea
                  className="min-h-40 w-full rounded-2xl border border-neutral-200 px-4 py-3 text-sm"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Workflow request"
                />
                <button
                  className="rounded-2xl bg-primary-600 px-5 py-3 text-sm font-medium text-white disabled:opacity-60"
                  disabled={isSubmitting}
                  onClick={() => void createWorkflow()}
                >
                  {isSubmitting ? "Creating..." : "Create and monitor workflow"}
                </button>
                {error ? <p className="text-sm text-red-600">{error}</p> : null}
              </div>
            </div>

            <div className="rounded-2xl border border-neutral-200 bg-white p-6 shadow-soft">
              <h2 className="text-lg font-semibold text-neutral-900">Recent Local Runs</h2>
              <div className="mt-4 space-y-3">
                {recentRuns.length === 0 ? (
                  <p className="text-sm text-neutral-500">
                    No runs created in this browser session yet.
                  </p>
                ) : (
                  recentRuns.map((run) => (
                    <button
                      key={run.id}
                      className="flex w-full items-center justify-between rounded-xl border border-neutral-200 px-4 py-3 text-left"
                      onClick={() => setActiveTaskId(run.id)}
                    >
                      <span className="font-mono text-xs text-neutral-600">{run.id}</span>
                      <span className="text-sm text-neutral-900">{run.current_status}</span>
                    </button>
                  ))
                )}
              </div>
            </div>

            <CostWidget userId={userId} />
          </div>

          <div>
            {activeTaskId ? (
              <WorkflowDashboard taskId={activeTaskId} />
            ) : (
              <div className="rounded-2xl border border-dashed border-neutral-300 bg-white p-8 text-sm text-neutral-500 shadow-soft">
                Create a workflow to open the realtime dashboard.
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
