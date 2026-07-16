import type { WorkflowStep } from "../types/workflow";

export function StepTimeline({
  steps,
  currentStep,
}: {
  steps: WorkflowStep[];
  currentStep: string;
}) {
  return (
    <div className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-soft">
      <h3 className="text-lg font-semibold text-neutral-900">Step Timeline</h3>
      <div className="mt-4 space-y-3">
        {steps.length === 0 ? (
          <p className="text-sm text-neutral-500">No workflow events received yet.</p>
        ) : (
          steps.map((step, index) => (
            <div
              key={`${step.stepName}-${step.status}-${index}`}
              className="flex items-start justify-between gap-4 rounded-xl border border-neutral-100 bg-neutral-50 px-4 py-3"
            >
              <div>
                <p className="font-medium text-neutral-900">{step.stepName}</p>
                <p className="text-sm text-neutral-500">{step.status}</p>
              </div>
              <div className="text-right text-xs text-neutral-500">
                <div>{step.stepName === currentStep ? "Current" : ""}</div>
                <div>{step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ""}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
