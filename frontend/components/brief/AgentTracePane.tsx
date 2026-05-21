"use client";

/**
 * AgentTracePane — collapsible "Live Concierge" pane that subscribes to
 * the SSE stream from `/arrival-brief/{stay_id}/stream` and renders each
 * tool call as it lands. The component owns no business logic; it simply
 * visualizes the {@link AgentStreamState} returned by `useAgentStream`.
 *
 * UI contract:
 *   - one row per agent_thinking + tool_call event in arrival order
 *   - each tool row shows: name · args summary · live|mock pill · ms · ✓/✗
 *   - "Build my brief" CTA toggles live web search via the `liveSearch` prop
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, CircleDot, Sparkles, XCircle } from "lucide-react";

import type { AgentEvent, ArrivalBriefResponse } from "@/lib/types";
import { useAgentStream } from "@/lib/agent-stream";

export interface AgentTracePaneProps {
  stayId: string;
  /** When true, the agent is allowed to make live Tavily calls. */
  liveSearchEnabled: boolean;
  /** When true, the agent is started automatically on mount. Default false. */
  autoStart?: boolean;
  /** Notified once when the agent emits the final brief. */
  onFinalBrief?: (brief: ArrivalBriefResponse) => void;
}

export function AgentTracePane({
  stayId,
  liveSearchEnabled,
  autoStart = false,
  onFinalBrief,
}: AgentTracePaneProps): React.ReactElement {
  const stream = useAgentStream(stayId, { liveSearch: liveSearchEnabled });
  const [collapsed, setCollapsed] = useState(false);

  // Auto-start on mount when requested. Re-running is keyed on stayId so a
  // navigation between trips kicks a fresh agent run.
  const startedRef = useRef<string | null>(null);
  useEffect(() => {
    if (!autoStart) return;
    if (startedRef.current === stayId) return;
    if (stream.status !== "idle") return;
    startedRef.current = stayId;
    stream.start();
    // We intentionally depend only on the trigger inputs, not the whole
    // `stream` object (which is recreated each render).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoStart, stayId, stream.status]);

  // Notify the parent exactly once per stay when the brief arrives. Doing
  // this inside an effect (not during render) avoids the React warning
  // about setting state in another component while rendering.
  const notifiedRef = useRef<string | null>(null);
  useEffect(() => {
    if (!stream.brief) return;
    if (notifiedRef.current === stayId) return;
    notifiedRef.current = stayId;
    onFinalBrief?.(stream.brief);
  }, [stream.brief, stayId, onFinalBrief]);

  const rows = useMemo(() => buildRows(stream.events), [stream.events]);

  return (
    <section className="bg-[var(--color-bonvoy-ink)] text-white rounded-lg overflow-hidden mb-6 shadow-sm">
      <header className="flex items-center justify-between gap-3 px-5 py-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Sparkles size={14} className="text-[var(--color-eco-green)]" />
          <span className="text-[11px] uppercase tracking-[0.2em] text-white/70">
            Live Concierge
          </span>
          <StatusPill status={stream.status} />
        </div>
        <div className="flex items-center gap-2">
          {!autoStart && (stream.status === "idle" || stream.status === "error") ? (
            <button
              type="button"
              onClick={stream.start}
              className="text-[12px] px-3 py-1 rounded bg-[var(--color-marriott-red)] hover:bg-[var(--color-marriott-red-hover)] transition"
            >
              {stream.status === "error" ? "Retry" : "Build my brief"}
            </button>
          ) : null}
          {autoStart && stream.status === "error" ? (
            <button
              type="button"
              onClick={() => {
                startedRef.current = null;
                stream.start();
              }}
              className="text-[12px] px-3 py-1 rounded bg-[var(--color-marriott-red)] hover:bg-[var(--color-marriott-red-hover)] transition"
            >
              Retry
            </button>
          ) : null}
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            className="text-white/60 hover:text-white"
            aria-label={collapsed ? "Expand trace" : "Collapse trace"}
          >
            {collapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
          </button>
        </div>
      </header>
      {!collapsed ? (
        <div className="px-5 py-4 font-mono text-[12px] leading-[1.6] text-white/90 max-h-[260px] overflow-y-auto">
          {rows.length === 0 ? (
            <p className="text-white/50">
              {stream.status === "running" || stream.status === "connecting"
                ? "Connecting to live concierge agent…"
                : autoStart
                  ? "Live concierge will start automatically when the brief opens."
                  : liveSearchEnabled
                    ? "Click Build my brief to run the agent against live web search (Tavily)."
                    : "Click Build my brief to run the agent against seed-derived mock data."}
            </p>
          ) : (
            <ul className="space-y-1">
              {rows.map((r) => (
                <TraceRow key={r.id} row={r} />
              ))}
            </ul>
          )}
          {stream.error ? (
            <p className="text-[var(--color-marriott-red)] mt-3">
              {stream.error}
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

/* ------------------------------------------------------------------ */

interface TraceRowModel {
  id: string;
  ts: string;
  kind: "tool" | "thinking";
  name: string;
  argsSummary?: string;
  status?: "started" | "ok" | "error" | "fallback";
  source?: "live" | "mock";
  durationMs?: number;
  resultCount?: number;
  summary?: string;
}

function buildRows(events: AgentEvent[]): TraceRowModel[] {
  const rows: TraceRowModel[] = [];
  const byCallId = new Map<string, TraceRowModel>();

  for (const ev of events) {
    const ts = formatTime(ev.timestamp);
    if (ev.type === "agent_thinking") {
      const stage = (ev.payload as { stage?: string }).stage ?? "thinking";
      rows.push({
        id: `thinking-${ev.timestamp}-${stage}`,
        ts,
        kind: "thinking",
        name:
          stage === "plan"
            ? "agent: planning tools"
            : stage === "compose"
              ? "agent: composing brief"
              : `agent: ${stage}`,
      });
      continue;
    }
    if (ev.type === "tool_call_started") {
      const p = ev.payload as {
        call_id: string;
        name: string;
        arguments?: Record<string, unknown>;
      };
      const row: TraceRowModel = {
        id: p.call_id,
        ts,
        kind: "tool",
        name: p.name,
        argsSummary: argsBlurb(p.arguments ?? {}),
        status: "started",
      };
      byCallId.set(p.call_id, row);
      rows.push(row);
      continue;
    }
    if (ev.type === "tool_call_finished") {
      const p = ev.payload as {
        call_id: string;
        name: string;
        status: "ok" | "error" | "fallback";
        source: "live" | "mock";
        duration_ms: number;
        result_count: number;
        summary: string;
      };
      const existing = byCallId.get(p.call_id);
      if (existing) {
        existing.status = p.status;
        existing.source = p.source;
        existing.durationMs = p.duration_ms;
        existing.resultCount = p.result_count;
        existing.summary = p.summary;
      }
    }
  }
  return rows;
}

function argsBlurb(args: Record<string, unknown>): string {
  const parts: string[] = [];
  for (const [k, v] of Object.entries(args)) {
    if (Array.isArray(v) && v.length > 0) parts.push(`${k}=${v.join(",")}`);
    else if (typeof v === "string" && v) parts.push(`${k}=${v}`);
  }
  return parts.join(" · ");
}

function formatTime(iso: string): string {
  if (!iso) return "--:--:--";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(11, 19);
  return d.toLocaleTimeString(undefined, { hour12: false });
}

function TraceRow({ row }: { row: TraceRowModel }): React.ReactElement {
  if (row.kind === "thinking") {
    return (
      <li className="text-white/60">
        <span className="text-white/40">[{row.ts}]</span>{" "}
        <span className="italic">{row.name}…</span>
      </li>
    );
  }
  const statusIcon =
    row.status === "ok" ? (
      <CheckCircle2 size={12} className="text-[var(--color-eco-green)]" />
    ) : row.status === "error" ? (
      <XCircle size={12} className="text-[var(--color-marriott-red)]" />
    ) : (
      <CircleDot size={12} className="text-white/40 animate-pulse" />
    );
  return (
    <li className="grid grid-cols-[auto_auto_1fr_auto] gap-2 items-center">
      <span className="text-white/40">[{row.ts}]</span>
      <span className="text-white">{row.name}</span>
      <span className="text-white/60 truncate">
        {row.argsSummary ?? ""}
        {row.summary ? ` — ${row.summary}` : ""}
      </span>
      <span className="flex items-center gap-2 justify-end">
        {row.source ? <SourceBadge source={row.source} /> : null}
        {row.durationMs !== undefined ? (
          <span className="text-white/50">{row.durationMs}ms</span>
        ) : null}
        {statusIcon}
      </span>
    </li>
  );
}

function SourceBadge({ source }: { source: "live" | "mock" }): React.ReactElement {
  return (
    <span
      className={`text-[10px] uppercase tracking-[0.14em] px-1.5 py-[1px] rounded ${
        source === "live"
          ? "bg-[var(--color-eco-green)]/20 text-[var(--color-eco-green)]"
          : "bg-white/10 text-white/60"
      }`}
    >
      {source}
    </span>
  );
}

function StatusPill({
  status,
}: {
  status: "idle" | "connecting" | "running" | "done" | "error";
}): React.ReactElement {
  const map: Record<typeof status, { label: string; className: string }> = {
    idle: { label: "ready", className: "bg-white/10 text-white/60" },
    connecting: {
      label: "connecting",
      className: "bg-yellow-500/20 text-yellow-300",
    },
    running: {
      label: "running",
      className: "bg-[var(--color-marriott-red)]/30 text-white",
    },
    done: {
      label: "done",
      className: "bg-[var(--color-eco-green)]/20 text-[var(--color-eco-green)]",
    },
    error: {
      label: "error",
      className: "bg-[var(--color-marriott-red)]/40 text-white",
    },
  } as const;
  const cfg = map[status];
  return (
    <span
      className={`text-[10px] uppercase tracking-[0.16em] px-2 py-[2px] rounded ${cfg.className}`}
    >
      {cfg.label}
    </span>
  );
}
