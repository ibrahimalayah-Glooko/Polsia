"use client";
import { useRef, useState } from "react";
import { api } from "@/lib/api";

type ChatMessage = { role: "user" | "assistant"; content: string };

const POLL_INTERVAL_MS = 3000;
const MAX_POLLS = 40;

const BUILD_KEYWORDS = ["website", "web site", "webpage", "web page", "landing page", "site for", "build me"];

function pickAgent(message: string): { agentType: string; label: string } {
  const lower = message.toLowerCase();
  if (BUILD_KEYWORDS.some((kw) => lower.includes(kw))) {
    return { agentType: "code_generation", label: "code generation agent" };
  }
  return { agentType: "orchestrator", label: "orchestrator agent" };
}

async function waitForTask(taskId: number, agentLabel: string): Promise<string> {
  for (let i = 0; i < MAX_POLLS; i++) {
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
    const task = await api.get<{ status: string; result_summary: string | null; error_message: string | null }>(
      `/tasks/${taskId}`
    );
    if (task.status === "completed") return task.result_summary ?? "Done, but the agent returned no summary.";
    if (task.status === "failed") return `${agentLabel} run failed: ${task.error_message ?? "unknown error"}`;
  }
  return "Still working on it — check the Tasks page for the result.";
}

/** Sends the user's message to the right agent (code generation for build requests, orchestrator otherwise). */
export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Ask me anything, or tell me to build you a website and I'll actually generate and publish one.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  const send = async () => {
    const text = input.trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);

    const { agentType, label } = pickAgent(text);

    try {
      const { task_id } = await api.post<{ status: string; task_id: number }>(`/agents/${agentType}/trigger`, {
        task_title: text.slice(0, 80),
        task_description: text,
      });
      const reply = await waitForTask(task_id, label);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${String(err)}` }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <section className="border border-black bg-white text-black flex flex-col h-full min-h-[400px]">
      <div ref={listRef} className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
        {messages.map((m, i) => (
          <p key={i} className={m.role === "user" ? "text-black" : "text-gray-600"}>
            {m.content}
          </p>
        ))}
        {sending && <p className="text-gray-400 text-xs">Waiting for the orchestrator…</p>}
      </div>
      <div className="border-t border-black p-2 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask Polsia anything…"
          className="flex-1 border border-black px-3 py-2 text-sm font-mono focus:outline-none"
        />
        <button
          onClick={send}
          disabled={sending}
          className="border border-black px-4 py-2 text-xs uppercase tracking-wide hover:bg-black hover:text-white transition-colors disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </section>
  );
}
