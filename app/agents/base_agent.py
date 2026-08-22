"""Base class for all Polsia agents — wraps the Claude Code CLI subprocess."""
import json
import os
import subprocess
import time
from abc import ABC, abstractmethod

from app.config import settings


class BasePolsiaAgent(ABC):
    agent_type: str = "base"

    @abstractmethod
    def run(self, task: dict, context: dict) -> dict:
        """Execute the agent's work for this task and return a result dict."""
        raise NotImplementedError

    def call_claude(self, prompt: str) -> str:
        """Generate a response for `prompt` using the configured LLM backend."""
        if os.getenv("CLAUDE_CLI_MOCK"):
            mock_response = json.loads(
                os.getenv("CLAUDE_CLI_MOCK_RESPONSE", '{"result": "Mock Claude response for testing"}')
            )
            return mock_response["result"]

        if settings.llm_backend == "ollama":
            return self._call_ollama(prompt)

        completed = subprocess.run(
            [settings.claude_cli_path, "-p", prompt, "--output-format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        return payload["result"]

    def _call_ollama(self, prompt: str) -> str:
        """Call a local Ollama model (e.g. hermes3) — no API key or Claude CLI login required."""
        import httpx

        response = httpx.post(
            f"{settings.ollama_host}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["response"]

    def call_claude_json(self, prompt: str) -> dict:
        """Invoke Claude and parse its result text as JSON."""
        return json.loads(self.call_claude(prompt))

    def parse_result(self, raw: str) -> dict:
        """Best-effort parse of a raw Claude result into a result dict."""
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return {"summary": raw}

    def timed_run(self, task: dict, context: dict) -> dict:
        start = time.monotonic()
        result = self.run(task, context)
        result["duration_secs"] = time.monotonic() - start
        return result
