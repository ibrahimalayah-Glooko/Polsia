import re
from pathlib import Path

from app.config import settings


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "site"


def _strip_markdown_fence(html: str) -> str:
    """Strip ```html ... ``` fences if the model wrapped its output in one."""
    match = re.search(r"```(?:html)?\s*(.*?)```", html, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else html.strip()


def save_site(company_name: str, html: str) -> dict:
    """Write a generated single-page website to the shared sites volume and return its URL."""
    slug = _slugify(company_name)
    site_dir = Path(settings.sites_dir) / slug
    site_dir.mkdir(parents=True, exist_ok=True)

    index_path = site_dir / "index.html"
    index_path.write_text(_strip_markdown_fence(html), encoding="utf-8")

    return {"slug": slug, "url": f"http://localhost/sites/{slug}/"}
