import os
import yaml
from pathlib import Path

DEFAULT_SERVER = "http://localhost:8081"


def load_config():
    config_path = Path.home() / ".config" / "cockroachdb-mcp-client" / "config.yaml"
    if config_path.exists():
        with config_path.open() as f:
            return yaml.safe_load(f) or {}
    return {}


def resolve_server(cli_value: str = None) -> str:
    if cli_value:
        return cli_value
    return os.getenv("MCP_SERVER_URL") or load_config().get("server") or DEFAULT_SERVER


def resolve_token(cli_value: str = None) -> str | None:
    return cli_value or os.getenv("MCP_API_TOKEN") or load_config().get("token")
