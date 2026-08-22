import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { AgentStatusGrid } from "@/components/dashboard/AgentStatusGrid";
import { AgentTriggerButton } from "@/components/dashboard/AgentTriggerButton";
import { ChatPanel } from "@/components/dashboard/ChatPanel";
import { PanelCard } from "@/components/dashboard/PanelCard";
import { api, type DashboardSummary, type Task } from "@/lib/api";

// Fetches live data from the backend on every request instead of at build time.
export const dynamic = "force-dynamic";

type Config = {
  name: string;
  website_url: string | null;
  daily_cycle_hour: number;
};

type MemoryEntry = { id: number; category: string; title: string; created_at: string };
type SocialPost = { id: number; content: string; status: string };
type AdCampaign = { id: number; name: string; platform: string; status: string };
type Prospect = { id: number; email: string; status: string };

async function safeGet<T>(path: string, fallback: T): Promise<T> {
  try {
    return await api.get<T>(path);
  } catch {
    return fallback;
  }
}

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const days = Math.floor(diffMs / 86_400_000);
  if (days >= 1) return `${days}D AGO`;
  const hours = Math.floor(diffMs / 3_600_000);
  if (hours >= 1) return `${hours}H AGO`;
  const mins = Math.max(1, Math.floor(diffMs / 60_000));
  return `${mins}M AGO`;
}

export default async function DashboardPage() {
  const [summary, config, tasks, posts, campaigns, prospects, documents] = await Promise.all([
    safeGet<DashboardSummary | null>("/dashboard/summary", null),
    safeGet<Config | null>("/config", null),
    safeGet<Task[]>("/tasks?limit=5", []),
    safeGet<SocialPost[]>("/social/posts?limit=1", []),
    safeGet<AdCampaign[]>("/ads/campaigns", []),
    safeGet<Prospect[]>("/outreach/prospects?limit=1", []),
    safeGet<MemoryEntry[]>("/memory?limit=5", []),
  ]);

  const kpis = summary?.kpis ?? {};
  const latestPost = posts[0];

  return (
    <div className="bg-white text-black min-h-screen font-mono">
      <div className="flex items-center justify-between px-6 py-4 border-b border-black">
        <h1 className="text-lg font-bold">{config?.name ?? "Polsia"}</h1>
        <a href="/tasks" className="border border-black px-3 py-1.5 text-xs uppercase tracking-wide hover:bg-black hover:text-white">
          + New Task
        </a>
      </div>

      <div className="flex flex-wrap gap-6 p-6 items-start">
        {/* Column 1 — Company */}
        <div className="w-full sm:w-72 flex-shrink-0 space-y-6">
          <PanelCard title="Polsia">
            <p className="font-bold">{config?.name ?? "Your company"}</p>
            <p className="text-xs text-gray-600">Your company is live!</p>
            <div className="flex gap-2 text-[10px]">
              <span className="border border-black px-2 py-1 uppercase">
                Daily cycle: {config?.daily_cycle_hour ?? 6}:00
              </span>
            </div>
            <a
              href="/agents"
              className="block border border-black px-3 py-2 text-center text-xs uppercase tracking-wide hover:bg-black hover:text-white"
            >
              View AI Agents
            </a>
          </PanelCard>

          <PanelCard title="Business" linkHref="/finance" linkLabel="Finance">
            <div className="flex justify-between">
              <span className="text-gray-600">Active Customers</span>
              <span className="font-bold">{String(kpis.active_customers ?? "—")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">MRR</span>
              <span className="font-bold">{kpis.mrr_usd != null ? `$${kpis.mrr_usd}` : "—"}</span>
            </div>
            <a
              href="/finance"
              className="block border border-black px-3 py-2 text-center text-xs uppercase tracking-wide hover:bg-black hover:text-white"
            >
              Setup Payments
            </a>
          </PanelCard>

          <PanelCard title="AI Team" linkHref="/agents">
            <p className="text-xs text-gray-600">
              {summary?.active_agents.length ?? 9} agents on staff · {summary?.tasks_today_completed ?? 0} tasks
              completed today
            </p>
          </PanelCard>
        </div>

        {/* Column 2 — Tasks / Documents / Website */}
        <div className="w-full sm:w-80 flex-shrink-0 space-y-6">
          <PanelCard title="Tasks" linkHref="/tasks" linkLabel="Manage Tasks">
            {tasks.length === 0 && <p className="text-gray-400 text-xs">No tasks yet.</p>}
            {tasks.map((t) => (
              <div key={t.id} className="border border-gray-300 p-2">
                <p className="text-xs font-bold">{t.title}</p>
                <div className="flex justify-between mt-1 text-[10px] text-gray-600">
                  <span className="border border-gray-400 px-1.5 py-0.5 uppercase">{t.agent_type.replace(/_/g, " ")}</span>
                  <span className="uppercase">{t.status}</span>
                </div>
              </div>
            ))}
            <a
              href="/tasks"
              className="block border border-black px-3 py-2 text-center text-xs uppercase tracking-wide hover:bg-black hover:text-white"
            >
              New Task
            </a>
          </PanelCard>

          <PanelCard title="Documents" linkHref="/memory" linkLabel="Memory">
            {documents.length === 0 && <p className="text-gray-400 text-xs">No documents yet.</p>}
            {documents.map((d) => (
              <div key={d.id} className="flex justify-between text-xs">
                <span>{d.title}</span>
                <span className="text-gray-500">{timeAgo(d.created_at)}</span>
              </div>
            ))}
          </PanelCard>

          <PanelCard title="Website" linkHref="/settings" linkLabel="Edit">
            <p className="text-xs break-all">{config?.website_url || "No website set yet."}</p>
          </PanelCard>
        </div>

        {/* Column 3 — Social / Outreach / Ads */}
        <div className="w-full sm:w-72 flex-shrink-0 space-y-6">
          <PanelCard title="Twitter" linkHref="/social" linkLabel="View all">
            <p className="text-xs">{latestPost ? latestPost.content : "No tweets yet."}</p>
            <AgentTriggerButton agentType="social_media" label="Tweet" />
          </PanelCard>

          <PanelCard title="Outreach" linkHref="/outreach" linkLabel="View all">
            <p className="text-xs text-gray-600">{prospects.length > 0 ? `${prospects.length} prospect(s) tracked` : "No prospects yet."}</p>
            <div className="flex gap-2">
              <AgentTriggerButton agentType="email_outreach" label="Cold Outreach" />
              <AgentTriggerButton agentType="customer_support" label="Support" />
            </div>
          </PanelCard>

          <PanelCard title="Ads" linkHref="/ads" linkLabel="View all">
            <p className="text-xs text-gray-600">
              {campaigns.length > 0 ? `${campaigns.length} campaign(s) running` : "Not running yet"}
            </p>
            <AgentTriggerButton agentType="ads_management" label="Ads" />
          </PanelCard>
        </div>

        {/* Column 4 — Chat */}
        <div className="w-full lg:flex-1 lg:min-w-[360px] h-[600px]">
          <ChatPanel />
        </div>
      </div>

      {/* Live operations (existing agent status + activity feed) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 bg-gray-950">
        <div>
          <h2 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Agent Status</h2>
          <AgentStatusGrid />
        </div>
        <div className="h-96">
          <h2 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Live Activity</h2>
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}

