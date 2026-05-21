/**
 * SSE client hook for the Live Concierge Agent.
 *
 * Subscribes to `GET /arrival-brief/{stayId}/stream` and exposes the
 * running list of {@link AgentEvent}s, the final brief once it lands,
 * plus a derived status flag the UI uses to drive the "running…" pill.
 *
 * The hook is intentionally idle until {@link useAgentStream.start} is
 * called — judges click "Build my brief" to kick the stream off, which
 * makes the live web-search opt-in explicit.
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { API_BASE_URL } from "./api";
import type {
  AgentEvent,
  ArrivalBriefResponse,
  ToolCallSummary,
} from "./types";

export type AgentStreamStatus =
  | "idle"
  | "connecting"
  | "running"
  | "done"
  | "error";

export interface AgentStreamState {
  status: AgentStreamStatus;
  events: AgentEvent[];
  brief: ArrivalBriefResponse | null;
  toolCalls: ToolCallSummary[];
  liveSearchUsed: boolean;
  error: string | null;
}

interface UseAgentStreamOptions {
  /** Forwarded to the backend; gated behind the consent toggle. */
  liveSearch?: boolean;
}

export function useAgentStream(
  stayId: string | null,
  opts: UseAgentStreamOptions = {},
): AgentStreamState & {
  start: () => void;
  reset: () => void;
} {
  const [state, setState] = useState<AgentStreamState>({
    status: "idle",
    events: [],
    brief: null,
    toolCalls: [],
    liveSearchUsed: false,
    error: null,
  });
  const sourceRef = useRef<EventSource | null>(null);

  const cleanup = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    cleanup();
    setState({
      status: "idle",
      events: [],
      brief: null,
      toolCalls: [],
      liveSearchUsed: false,
      error: null,
    });
  }, [cleanup]);

  const start = useCallback(() => {
    if (!stayId) return;
    cleanup();

    const url = new URL(
      `arrival-brief/${stayId}/stream`,
      `${API_BASE_URL}/`,
    );
    url.searchParams.set("live_search", opts.liveSearch ? "true" : "false");

    setState((s) => ({ ...s, status: "connecting", error: null, events: [] }));

    // EventSource always sends credentials on same-origin; for our
    // backend on a different port we rely on the unauthenticated brief
    // endpoint (see arrival_brief router docstring).
    const es = new EventSource(url.toString(), { withCredentials: true });
    sourceRef.current = es;

    es.onopen = () => {
      setState((s) => ({ ...s, status: "running" }));
    };

    es.onmessage = (msg) => {
      handleMessage(msg.data);
    };
    // Handle named events from the backend (event: tool_call_started, etc.)
    [
      "agent_started",
      "tool_call_started",
      "tool_call_finished",
      "agent_thinking",
      "final_brief",
      "agent_finished",
      "agent_error",
    ].forEach((name) => {
      es.addEventListener(name, (e) => {
        handleMessage((e as MessageEvent).data);
      });
    });

    es.onerror = () => {
      setState((s) =>
        s.status === "done"
          ? s
          : { ...s, status: "error", error: "Stream disconnected" },
      );
      cleanup();
    };

    function handleMessage(raw: string): void {
      try {
        const ev = JSON.parse(raw) as AgentEvent;
        setState((s) => {
          const events = [...s.events, ev];
          let next: AgentStreamState = { ...s, events };
          if (ev.type === "final_brief") {
            const payload = ev.payload as {
              brief?: Partial<ArrivalBriefResponse>;
              tool_calls?: ToolCallSummary[];
              live_search_used?: boolean;
            };
            const defaults: ArrivalBriefResponse = {
              stay_id: stayId!,
              guest_id: "",
              hotel: "",
              city: "",
              check_in: "",
              check_out: "",
              generated_at: new Date().toISOString(),
              generated_by: "litellm",
              greeting: "",
              weather_summary: "",
              weather_forecast: [],
              packing_tips: [],
              events: [],
              dining: [],
              transit: "",
              property_note: "",
              eco_note: null,
            };
            const merged: ArrivalBriefResponse = {
              ...defaults,
              ...(payload.brief as ArrivalBriefResponse),
              tool_calls: payload.tool_calls ?? [],
              live_search_used: payload.live_search_used ?? false,
            };
            next = {
              ...next,
              brief: merged,
              toolCalls: payload.tool_calls ?? [],
              liveSearchUsed: payload.live_search_used ?? false,
            };
          }
          if (ev.type === "agent_finished") {
            next = { ...next, status: "done" };
            cleanup();
          }
          if (ev.type === "agent_error") {
            next = {
              ...next,
              status: "error",
              error:
                (ev.payload as { error?: string }).error ?? "Unknown error",
            };
            cleanup();
          }
          return next;
        });
      } catch {
        // ignore malformed frames
      }
    }
  }, [cleanup, opts.liveSearch, stayId]);

  useEffect(() => () => cleanup(), [cleanup]);

  return { ...state, start, reset };
}
