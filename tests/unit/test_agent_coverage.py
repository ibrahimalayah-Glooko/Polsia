import json
from unittest.mock import Mock, patch

from app.agents.ads_management.agent import AdsManagementAgent
from app.agents.base_agent import BasePolsiaAgent, settings
from app.agents.business_planning.agent import BusinessPlanningAgent
from app.agents.code_generation.agent import CodeGenerationAgent
from app.agents.competitor_research.agent import CompetitorResearchAgent
from app.agents.customer_support.agent import CustomerSupportAgent
from app.agents.email_outreach.agent import EmailOutreachAgent
from app.agents.finance.agent import FinanceAgent
from app.agents.orchestrator.agent import OrchestratorAgent
from app.agents.social_media.agent import SocialMediaAgent

TASK = {"title": "Launch growth plan", "description": "Focus on SMB clinics"}
CONTEXT = {
    "company": {
        "name": "Polsia",
        "mission": "Automate business operations",
        "github_repo": "ibrahimalayah-Glooko/Polsia",
    }
}


class ConcreteAgent(BasePolsiaAgent):
    def run(self, task, context):
        return {"summary": "ok"}


def test_base_agent_subprocess_and_json_helpers(monkeypatch):
    monkeypatch.delenv("CLAUDE_CLI_MOCK", raising=False)
    monkeypatch.setattr(settings, "llm_backend", "claude")
    monkeypatch.setattr(settings, "claude_cli_path", "/usr/local/bin/claude-test")

    completed = Mock(stdout=json.dumps({"result": "from subprocess"}))
    with patch("subprocess.run", return_value=completed) as mock_run:
        result = ConcreteAgent().call_claude("prompt")

    assert result == "from subprocess"
    mock_run.assert_called_once_with(
        ["/usr/local/bin/claude-test", "-p", "prompt", "--output-format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )


def test_base_agent_ollama_and_parse_result(monkeypatch):
    monkeypatch.delenv("CLAUDE_CLI_MOCK", raising=False)
    monkeypatch.setattr(settings, "llm_backend", "ollama")
    monkeypatch.setattr(settings, "ollama_host", "http://ollama")
    monkeypatch.setattr(settings, "ollama_model", "hermes3")

    response = Mock()
    response.json.return_value = {"response": "from ollama"}
    with patch("httpx.post", return_value=response) as mock_post:
        agent = ConcreteAgent()
        assert agent.call_claude("prompt") == "from ollama"

    response.raise_for_status.assert_called_once_with()
    mock_post.assert_called_once_with(
        "http://ollama/api/generate",
        json={"model": "hermes3", "prompt": "prompt", "stream": False},
        timeout=180,
    )

    agent = ConcreteAgent()
    assert agent.parse_result('{"summary": "done"}') == {"summary": "done"}
    assert agent.parse_result("plain text") == {"summary": "plain text"}


def test_ads_management_agent_parses_campaigns(monkeypatch):
    monkeypatch.setattr(
        AdsManagementAgent,
        "call_claude",
        lambda self, prompt: json.dumps(
            [{"platform": "meta", "name": "Retarget SMBs", "goal": "signups", "daily_budget_usd": "12.5"}]
        ),
    )

    result = AdsManagementAgent().run(TASK, CONTEXT)

    assert result == {
        "summary": "Proposed 1 ad campaign(s): Retarget SMBs",
        "ad_campaigns": [
            {
                "platform": "meta",
                "name": "Retarget SMBs",
                "goal": "signups",
                "daily_budget_usd": 12.5,
            }
        ],
    }


def test_business_planning_agent_parses_ideas(monkeypatch):
    monkeypatch.setattr(
        BusinessPlanningAgent,
        "call_claude",
        lambda self, prompt: json.dumps(
            [{"title": "Referral program", "rationale": "Warm leads", "expected_impact": "More demos"}]
        ),
    )

    result = BusinessPlanningAgent().run(TASK, CONTEXT)

    assert result == {
        "summary": "Proposed 1 business idea(s): Referral program",
        "business_ideas": [
            {
                "title": "Referral program",
                "rationale": "Warm leads",
                "expected_impact": "More demos",
            }
        ],
    }


def test_competitor_research_agent_parses_competitors(monkeypatch):
    monkeypatch.setattr(
        CompetitorResearchAgent,
        "call_claude",
        lambda self, prompt: json.dumps(
            [
                {
                    "name": "Acme AI",
                    "website": "https://acme.test",
                    "positioning": "Clinic ops",
                    "strengths": ["Brand"],
                    "weaknesses": ["Price"],
                }
            ]
        ),
    )

    result = CompetitorResearchAgent().run(TASK, CONTEXT)

    assert result == {
        "summary": "Researched 1 competitor(s): Acme AI",
        "competitors": [
            {
                "name": "Acme AI",
                "website": "https://acme.test",
                "positioning": "Clinic ops",
                "strengths": ["Brand"],
                "weaknesses": ["Price"],
            }
        ],
    }


def test_email_outreach_agent_parses_prospects(monkeypatch):
    monkeypatch.setattr(
        EmailOutreachAgent,
        "call_claude",
        lambda self, prompt: json.dumps(
            [
                {
                    "email": "sara@example.com",
                    "first_name": "Sara",
                    "company": "North Clinic",
                    "title": "CEO",
                }
            ]
        ),
    )

    result = EmailOutreachAgent().run(TASK, CONTEXT)

    assert result == {
        "summary": "Found 1 prospect(s): sara@example.com",
        "prospects": [
            {
                "email": "sara@example.com",
                "first_name": "Sara",
                "company": "North Clinic",
                "title": "CEO",
            }
        ],
    }


def test_finance_agent_parses_snapshot(monkeypatch):
    monkeypatch.setattr(
        FinanceAgent,
        "call_claude",
        lambda self, prompt: json.dumps(
            {
                "mrr_cents": 12345,
                "arr_cents": 148140,
                "active_subscribers": 18,
                "stripe_balance_cents": 4500,
            }
        ),
    )

    result = FinanceAgent().run(TASK, CONTEXT)

    assert result == {
        "summary": "Updated revenue snapshot: MRR $123.45, 18 active subscribers",
        "revenue_snapshot": {
            "mrr_cents": 12345,
            "arr_cents": 148140,
            "active_subscribers": 18,
            "stripe_balance_cents": 4500,
        },
    }


def test_customer_support_agent_wraps_plain_text(monkeypatch):
    monkeypatch.setattr(CustomerSupportAgent, "call_claude", lambda self, prompt: "Drafted reply")

    assert CustomerSupportAgent().run(TASK, CONTEXT) == {"summary": "Drafted reply"}


def test_orchestrator_agent_defaults_insights(monkeypatch):
    monkeypatch.setattr(OrchestratorAgent, "call_claude", lambda self, prompt: '{"summary": "Plan ready"}')

    assert OrchestratorAgent().run(TASK, CONTEXT) == {"summary": "Plan ready", "insights": []}


def test_social_media_agent_posts_generated_tweet(monkeypatch):
    monkeypatch.setattr(SocialMediaAgent, "call_claude", lambda self, prompt: '"Launch faster with Polsia!"')

    with patch("app.integrations.twitter_client.post_tweet", return_value={"tweet_id": "42", "simulated": False}):
        result = SocialMediaAgent().run(TASK, CONTEXT)

    assert result == {
        "summary": "Drafted and posted a tweet: Launch faster with Polsia!",
        "social_post": {
            "platform": "twitter",
            "content": "Launch faster with Polsia!",
            "status": "published",
            "tweet_id": "42",
        },
    }


def test_code_generation_agent_builds_website(monkeypatch):
    task = {"title": "Build website", "description": "New landing page"}
    monkeypatch.setattr(CodeGenerationAgent, "call_claude", lambda self, prompt: "<!DOCTYPE html><h1>Polsia</h1>")

    with patch(
        "app.services.website_service.save_site",
        return_value={"slug": "polsia", "url": "http://localhost/sites/polsia/"},
    ):
        result = CodeGenerationAgent().run(task, CONTEXT)

    assert result == {
        "summary": "Built and published a website at http://localhost/sites/polsia/",
        "website": {"slug": "polsia", "url": "http://localhost/sites/polsia/"},
    }


def test_code_generation_agent_opens_issue(monkeypatch):
    monkeypatch.setattr(CodeGenerationAgent, "call_claude", lambda self, prompt: "Ship a scheduling feature.")

    with patch(
        "app.integrations.github_client.open_issue",
        return_value={"issue_url": None, "simulated": True},
    ):
        result = CodeGenerationAgent().run(TASK, CONTEXT)

    assert result == {
        "summary": "Ship a scheduling feature.",
        "github_issue": {"issue_url": None, "simulated": True},
    }
