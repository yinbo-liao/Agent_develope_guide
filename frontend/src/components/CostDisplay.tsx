export function CostDisplay({
  totalTokens,
  totalCost,
}: {
  totalTokens: number;
  totalCost: number;
}) {
  return (
    <div className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-soft">
      <h3 className="text-lg font-semibold text-neutral-900">Usage</h3>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl bg-neutral-50 p-4">
          <p className="text-sm text-neutral-500">Tokens</p>
          <p className="mt-2 font-mono text-2xl text-neutral-900">
            {totalTokens.toLocaleString()}
          </p>
        </div>
        <div className="rounded-xl bg-neutral-50 p-4">
          <p className="text-sm text-neutral-500">Estimated Cost</p>
          <p className="mt-2 font-mono text-2xl text-neutral-900">
            ${totalCost.toFixed(4)}
          </p>
        </div>
      </div>
    </div>
  );
}
