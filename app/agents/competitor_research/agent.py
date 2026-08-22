from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class CompetitorResearchAgent(BasePolsiaAgent):
    agent_type = "competitor_research"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the competitor research agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Research up to 3 competitors. Reply with ONLY a JSON array, each item shaped like "
            '{"name": str, "website": str, "positioning": str, "strengths": [str], "weaknesses": [str]}.'
        )
        raw = self.call_claude(prompt)
        competitors = self._parse_competitors(raw)

        if competitors:
            summary = f"Researched {len(competitors)} competitor(s): " + ", ".join(c["name"] for c in competitors)
        else:
            summary = raw

        return {
            "summary": summary,
            "competitors": competitors,
        }

    def _parse_competitors(self, raw: str) -> list[dict]:
        import json

        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

        if not isinstance(parsed, list):
            return []

        competitors = []
        for item in parsed:
            if not isinstance(item, dict) or "name" not in item:
                continue
            competitors.append(
                {
                    "name": item.get("name"),
                    "website": item.get("website"),
                    "positioning": item.get("positioning"),
                    "strengths": item.get("strengths") or [],
                    "weaknesses": item.get("weaknesses") or [],
                }
            )
        return competitors
