export function ReActThoughtViewer({
  summary,
  factors,
}: {
  summary: string | null;
  factors: string[];
}) {
  return (
    <div className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-soft">
      <h3 className="text-lg font-semibold text-neutral-900">Analysis Notes</h3>
      <div className="mt-4 space-y-4">
        <div className="rounded-xl bg-neutral-50 p-4 text-sm leading-6 text-neutral-700">
          {summary ?? "No generated response yet."}
        </div>
        <div>
          <h4 className="text-sm font-semibold text-neutral-900">Risk Factors</h4>
          <ul className="mt-2 space-y-2 text-sm text-neutral-600">
            {factors.length === 0 ? (
              <li>No elevated risk factors detected.</li>
            ) : (
              factors.map((factor) => <li key={factor}>{factor}</li>)
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
