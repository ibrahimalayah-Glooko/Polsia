from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt

WEBSITE_KEYWORDS = ("website", "web site", "webpage", "web page", "landing page", "site for")


class CodeGenerationAgent(BasePolsiaAgent):
    agent_type = "code_generation"

    def run(self, task: dict, context: dict) -> dict:
        request_text = f"{task.get('title') or ''} {task.get('description') or ''}".lower()

        if any(keyword in request_text for keyword in WEBSITE_KEYWORDS):
            return self._build_website(task, context)

        return self._open_github_issue(task, context)

    def _build_website(self, task: dict, context: dict) -> dict:
        company = context.get("company") or {}
        prompt = (
            f"You are the code generation agent, building a real website.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n\n"
            "Generate a complete, self-contained, production-quality single-page website as raw HTML. "
            "Include <style> CSS inline in the <head> — no external assets, no JavaScript frameworks. "
            "Reflect the company's name, mission, and value proposition in the copy. "
            "Reply with ONLY the raw HTML document, starting with <!DOCTYPE html>."
        )
        html = self.call_claude(prompt)

        from app.services.website_service import save_site

        site = save_site(company.get("name") or "my-company", html)

        return {
            "summary": f"Built and published a website at {site['url']}",
            "website": site,
        }

    def _open_github_issue(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the code generation agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Describe the feature you would ship for this task in 1-2 sentences, suitable as a GitHub issue body."
        )
        body = self.call_claude(prompt).strip()

        from app.integrations.github_client import open_issue

        github_repo = (context.get("company") or {}).get("github_repo") if context else None
        issue_result = open_issue(github_repo, title=task.get("title") or "Code generation task", body=body)

        return {
            "summary": body,
            "github_issue": issue_result,
        }
