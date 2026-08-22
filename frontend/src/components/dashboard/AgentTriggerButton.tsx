"use client";
import { useState } from "react";
import { api } from "@/lib/api";

interface AgentTriggerButtonProps {
  agentType: string;
  label: string;
  taskTitle?: string;
  taskDescription?: string;
}

/** Dispatches a real task to the given agent and reports back the queued task id. */
export function AgentTriggerButton({ agentType, label, taskTitle, taskDescription }: AgentTriggerButtonProps) {
  const [state, setState] = useState<"idle" | "sending" | "queued" | "error">("idle");
  const [taskId, setTaskId] = useState<number | null>(null);

  const trigger = async () => {
    setState("sending");
    try {
      const res = await api.post<{ status: string; task_id: number }>(`/agents/${agentType}/trigger`, {
        task_title: taskTitle ?? `${label} run`,
        task_description: taskDescription,
      });
      setTaskId(res.task_id);
      setState("queued");
    } catch {
      setState("error");
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={trigger}
        disabled={state === "sending"}
        className="border border-black px-3 py-1.5 text-xs uppercase tracking-wide hover:bg-black hover:text-white transition-colors disabled:opacity-50"
      >
        {state === "sending" ? "Sending…" : label}
      </button>
      {state === "queued" && taskId != null && (
        <span className="text-[10px] text-gray-600">Queued task #{taskId}</span>
      )}
      {state === "error" && <span className="text-[10px] text-red-600">Failed to queue</span>}
    </div>
  );
}
