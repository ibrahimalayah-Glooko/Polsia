"""GitHub issue creation — the real API call, gated behind SANDBOX_MODE and configured credentials."""
from app.config import settings


def _configured() -> bool:
    return bool(settings.github_token)


def open_issue(repo: str | None, title: str, body: str) -> dict:
    """Open a GitHub issue. In SANDBOX_MODE (or without credentials), simulate instead."""
    if settings.sandbox_mode or not _configured() or not repo:
        return {"issue_url": None, "simulated": True}

    from github import Github

    client = Github(settings.github_token)
    gh_repo = client.get_repo(repo)
    issue = gh_repo.create_issue(title=title, body=body)
    return {"issue_url": issue.html_url, "simulated": False}
