from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class BusinessPlanningAgent(BasePolsiaAgent):
    agent_type = "business_planning"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the business planning agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Propose up to 5 concrete business ideas/growth levers for this company. "
            "Reply with ONLY a JSON array, each item shaped like "
            '{"title": str, "rationale": str, "expected_impact": str}.'
        )
        raw = self.call_claude(prompt)
        ideas = self._parse_ideas(raw)

        if ideas:
            summary = f"Proposed {len(ideas)} business idea(s): " + ", ".join(i["title"] for i in ideas)
        else:
            summary = raw

        return {
            "summary": summary,
            "business_ideas": ideas,
        }

    def _parse_ideas(self, raw: str) -> list[dict]:
        import json

        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

        if not isinstance(parsed, list):
            return []

        ideas = []
        for item in parsed:
            if not isinstance(item, dict) or "title" not in item:
                continue
            ideas.append(
                {
                    "title": item.get("title", "Untitled idea"),
                    "rationale": item.get("rationale"),
                    "expected_impact": item.get("expected_impact"),
                }
            )
        return ideas
