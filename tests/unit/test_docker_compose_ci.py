from pathlib import Path


def _service_block(compose_text: str, service_name: str) -> str:
    lines = compose_text.splitlines()
    block = []
    in_service = False

    for line in lines:
        if line.startswith(f"  {service_name}:"):
            in_service = True
        elif in_service and line.startswith("  ") and not line.startswith("    "):
            break

        if in_service:
            block.append(line)

    return "\n".join(block)


def test_ci_compose_exposes_backend_and_frontend_ports() -> None:
    compose_text = Path("docker-compose.ci.yml").read_text()

    backend_block = _service_block(compose_text, "backend")
    frontend_block = _service_block(compose_text, "frontend")

    assert '- "8000:8000"' in backend_block
    assert '- "3000:3000"' in frontend_block
