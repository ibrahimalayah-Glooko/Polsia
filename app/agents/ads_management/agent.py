from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class AdsManagementAgent(BasePolsiaAgent):
    agent_type = "ads_management"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the ads management agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Propose up to 3 ad campaigns to run right now, spreading spend across the platforms "
            "(Google, Meta) and audiences that best fit this company's target market and goals. "
            "Reply with ONLY a JSON array, each item shaped like "
            '{"platform": "google"|"meta", "name": str, "goal": str, "daily_budget_usd": number}.'
        )
        raw = self.call_claude(prompt)
        campaigns = self._parse_campaigns(raw)

        if campaigns:
            summary = f"Proposed {len(campaigns)} ad campaign(s): " + ", ".join(c["name"] for c in campaigns)
        else:
            summary = raw

        return {
            "summary": summary,
            "ad_campaigns": campaigns,
        }

    def _parse_campaigns(self, raw: str) -> list[dict]:
        import json

        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

        if not isinstance(parsed, list):
            return []

        campaigns = []
        for item in parsed:
            if not isinstance(item, dict) or "platform" not in item or "name" not in item:
                continue
            campaigns.append(
                {
                    "platform": item.get("platform", "google"),
                    "name": item.get("name", "Untitled campaign"),
                    "goal": item.get("goal"),
                    "daily_budget_usd": float(item.get("daily_budget_usd", 0) or 0),
                }
            )
        return campaigns
