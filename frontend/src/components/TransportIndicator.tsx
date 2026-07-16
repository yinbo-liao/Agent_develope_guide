import type { TransportType } from "../types/workflow";

const labels: Record<TransportType, string> = {
  auto: "Auto",
  websocket: "WebSocket",
  sse: "SSE",
  connecting: "Connecting",
};

export function TransportIndicator({ transport }: { transport: TransportType }) {
  return (
    <span className="inline-flex rounded-full border border-neutral-200 bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-700">
      {labels[transport]}
    </span>
  );
}
