from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class CustomerSupportAgent(BasePolsiaAgent):
    agent_type = "customer_support"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the customer support agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Read the inbox and draft replies to customer emails."
        )
        return self.parse_result(self.call_claude(prompt))
