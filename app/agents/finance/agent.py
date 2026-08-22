from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class FinanceAgent(BasePolsiaAgent):
    agent_type = "finance"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the finance agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Estimate today's revenue snapshot from the context above. Reply with ONLY a JSON object shaped like "
            '{"mrr_cents": int, "arr_cents": int, "active_subscribers": int, "stripe_balance_cents": int}.'
        )
        raw = self.call_claude(prompt)
        snapshot = self._parse_snapshot(raw)

        if snapshot:
            summary = (
                f"Updated revenue snapshot: MRR ${snapshot['mrr_cents'] / 100:.2f}, "
                f"{snapshot['active_subscribers']} active subscribers"
            )
        else:
            summary = raw

        return {
            "summary": summary,
            "revenue_snapshot": snapshot,
        }

    def _parse_snapshot(self, raw: str) -> dict | None:
        import json

        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

        if not isinstance(parsed, dict):
            return None

        return {
            "mrr_cents": int(parsed.get("mrr_cents", 0) or 0),
            "arr_cents": int(parsed.get("arr_cents", 0) or 0),
            "active_subscribers": int(parsed.get("active_subscribers", 0) or 0),
            "stripe_balance_cents": int(parsed.get("stripe_balance_cents", 0) or 0),
        }
