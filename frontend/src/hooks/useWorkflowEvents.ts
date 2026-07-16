import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { runtimeConfig } from "../lib/runtime";
import type { TransportType, WorkflowEvent, WorkflowState } from "../types/workflow";

const MAX_RECONNECT_ATTEMPTS = 5;
const BASE_DELAY_MS = 1000;
const MAX_DELAY_MS = 30000;

const emptyState = (taskId: string): WorkflowState => ({
  taskId,
  status: "idle",
  currentStep: "not-started",
  finalResponse: null,
  error: null,
  isHumanReviewNeeded: false,
  reviewData: undefined,
  totalTokens: 0,
  totalCost: 0,
  steps: [],
  transport: "connecting",
  connected: false,
});

function backoffDelay(attempt: number): number {
  const exponential = Math.min(MAX_DELAY_MS, BASE_DELAY_MS * Math.pow(2, attempt));
  // Add jitter: ±25%
  const jitter = exponential * 0.25 * (Math.random() * 2 - 1);
  return Math.round(exponential + jitter);
}

export function useWorkflowEvents(
  taskId: string | null,
  preferredTransport: TransportType = "auto",
) {
  const [state, setState] = useState<WorkflowState>(emptyState(taskId ?? ""));
  const wsRef = useRef<WebSocket | null>(null);
  const sseRef = useRef<EventSource | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    wsRef.current?.close();
    sseRef.current?.close();
    wsRef.current = null;
    sseRef.current = null;
  }, []);

  const appendStep = useCallback((event: WorkflowEvent) => {
    if (!event.stepName && !event.currentStep) {
      return;
    }
    setState((current) => {
      const stepName = event.stepName ?? event.currentStep ?? "unknown";
      const next = {
        stepName,
        status: event.stepStatus ?? event.status ?? "updated",
        timestamp: event.timestamp,
      };
      const alreadyPresent = current.steps.some(
        (step) => step.stepName === next.stepName && step.status === next.status,
      );
      return {
        ...current,
        steps: alreadyPresent ? current.steps : [...current.steps, next],
      };
    });
  }, []);

  const processEvent = useCallback(
    (event: WorkflowEvent) => {
      setState((current) => ({
        ...current,
        taskId: event.taskId || current.taskId,
        status:
          event.type === "error"
            ? "error"
            : event.isHumanReviewNeeded
              ? "paused"
              : (event.status as WorkflowState["status"]) || current.status,
        currentStep: event.currentStep ?? event.stepName ?? current.currentStep,
        finalResponse: event.finalResponse ?? current.finalResponse,
        error: event.error ?? current.error,
        isHumanReviewNeeded: event.isHumanReviewNeeded ?? current.isHumanReviewNeeded,
        reviewData: event.reviewData ?? current.reviewData,
        totalTokens: event.totalTokens ?? current.totalTokens,
        totalCost: event.totalCost ?? current.totalCost,
        connected: true,
      }));
      appendStep(event);
    },
    [appendStep],
  );

  const fetchState = useCallback(async () => {
    if (!taskId) {
      return;
    }
    const response = await fetch(`${runtimeConfig.apiBase}/api/v1/events/state/${taskId}`);
    if (!response.ok) {
      throw new Error("Failed to fetch workflow state");
    }
    const event = (await response.json()) as WorkflowEvent;
    processEvent(event);
  }, [processEvent, taskId]);

  const sendResume = useCallback(
    async (decision: "approved" | "rejected", reviewerId: string, comment: string) => {
      if (!taskId) {
        return;
      }

      const payload = {
        type: "resume",
        decision,
        reviewerId,
        comment,
      };

      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(payload));
        return;
      }

      await fetch(`${runtimeConfig.apiBase}/api/v1/human-review/decide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: taskId,
          reviewer_id: reviewerId,
          decision,
          comment,
        }),
      });
      await fetchState();
    },
    [fetchState, taskId],
  );

  useEffect(() => {
    if (!taskId) {
      setState(emptyState(""));
      disconnect();
      return;
    }

    setState((current) => ({
      ...emptyState(taskId),
      steps: current.taskId === taskId ? current.steps : [],
    }));
    disconnect();
    reconnectAttemptRef.current = 0;

    const scheduleReconnect = (
      label: string,
      connectFn: () => void,
      maxAttempts: number = MAX_RECONNECT_ATTEMPTS,
      onExhausted?: () => void,
    ) => {
      if (reconnectAttemptRef.current >= maxAttempts) {
        reconnectAttemptRef.current = 0;
        onExhausted?.();
        return;
      }
      const delay = backoffDelay(reconnectAttemptRef.current);
      reconnectAttemptRef.current += 1;
      setState((current) => ({ ...current, transport: "connecting" }));
      reconnectTimerRef.current = setTimeout(() => {
        connectFn();
      }, delay);
    };

    const connectSse = () => {
      const sse = new EventSource(`${runtimeConfig.apiBase}/api/v1/events/sse/${taskId}`);
      sseRef.current = sse;
      setState((current) => ({ ...current, transport: "sse", connected: true }));
      reconnectAttemptRef.current = 0;

      sse.onmessage = (message) => {
        processEvent(JSON.parse(message.data) as WorkflowEvent);
      };
      sse.onerror = () => {
        sse.close();
        setState((current) => ({ ...current, connected: false }));
        // Attempt SSE reconnection with backoff
        scheduleReconnect("SSE", connectSse);
      };
    };

    const connectWebsocket = () => {
      const transport: TransportType =
        preferredTransport === "auto" ? "websocket" : preferredTransport;

      if (transport === "sse") {
        connectSse();
        return;
      }

      const websocket = new WebSocket(
        `${runtimeConfig.wsBase}/api/v1/events/ws/${taskId}`,
      );
      wsRef.current = websocket;
      setState((current) => ({ ...current, transport: "websocket" }));

      websocket.onmessage = (message) => {
        processEvent(JSON.parse(message.data) as WorkflowEvent);
      };
      websocket.onopen = async () => {
        reconnectAttemptRef.current = 0;
        setState((current) => ({ ...current, connected: true }));
        try {
          await fetchState();
        } catch {
          // State will arrive via realtime events.
        }
      };
      websocket.onerror = () => {
        websocket.close();
      };
      websocket.onclose = () => {
        setState((current) => ({ ...current, connected: false }));
        if (preferredTransport === "websocket") {
          // Retry WebSocket with backoff, then give up
          scheduleReconnect("WebSocket", connectWebsocket, MAX_RECONNECT_ATTEMPTS);
          return;
        }
        // Auto mode: retry WS a few times then fall back to SSE
        scheduleReconnect("WebSocket", connectWebsocket, MAX_RECONNECT_ATTEMPTS, () => {
          connectSse();
        });
      };
    };

    // Initial fetch — only needed as bootstrap (WebSocket onopen also refreshes)
    void fetchState().catch(() => undefined);
    connectWebsocket();

    return () => {
      disconnect();
    };
  }, [disconnect, fetchState, preferredTransport, processEvent, taskId]);

  return useMemo(
    () => ({
      state,
      sendResume,
      refresh: fetchState,
    }),
    [fetchState, sendResume, state],
  );
}
