from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    api_key: str = "dev-key"
    sandbox_mode: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///:memory:"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Claude CLI
    claude_cli_path: str = "/usr/local/bin/claude"

    # LLM backend — "claude" (default, uses the Claude Code CLI) or "ollama" (local model, no API key needed)
    llm_backend: str = "claude"
    ollama_host: str = "http://host.docker.internal:11434"
    ollama_model: str = "hermes3"

    # ChromaDB
    chroma_persist_dir: str = "/app/data/chroma"

    # Generated websites (code_generation agent output), served at /sites/<slug>/
    sites_dir: str = "/app/data/sites"

    # Scheduling
    morning_cycle_hour: int = 6
    evening_cycle_hour: int = 20

    # Integrations
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    sendgrid_api_key: str = ""
    tavily_api_key: str = ""
    github_token: str = ""


settings = Settings()
