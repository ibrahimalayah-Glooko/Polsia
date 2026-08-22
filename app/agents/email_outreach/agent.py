from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class EmailOutreachAgent(BasePolsiaAgent):
    agent_type = "email_outreach"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the email outreach agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Find up to 3 prospects that fit this company's target market. Reply with ONLY a JSON array, "
            'each item shaped like {"email": str, "first_name": str, "company": str, "title": str}.'
        )
        raw = self.call_claude(prompt)
        prospects = self._parse_prospects(raw)

        if prospects:
            summary = f"Found {len(prospects)} prospect(s): " + ", ".join(p["email"] for p in prospects)
        else:
            summary = raw

        return {
            "summary": summary,
            "prospects": prospects,
        }

    def _parse_prospects(self, raw: str) -> list[dict]:
        import json

        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

        if not isinstance(parsed, list):
            return []

        prospects = []
        for item in parsed:
            if not isinstance(item, dict) or "email" not in item:
                continue
            prospects.append(
                {
                    "email": item.get("email"),
                    "first_name": item.get("first_name"),
                    "company": item.get("company"),
                    "title": item.get("title"),
                }
            )
        return prospects
