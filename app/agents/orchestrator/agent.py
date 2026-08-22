from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class OrchestratorAgent(BasePolsiaAgent):
    agent_type = "orchestrator"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the orchestrator agent for this business.\n"
            f"{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Produce a concise plan or summary, and a short list of key insights."
        )
        raw = self.call_claude(prompt)
        result = self.parse_result(raw)
        result.setdefault("insights", [])
        return result
