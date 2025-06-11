import json
import logging
import requests
import typer
import yaml
from pathlib import Path
from rich import print
from cockroachdb_mcp_client.utils import handle_connection_error
from cockroachdb_mcp_client.config import resolve_server, resolve_token
from cockroachdb_mcp_client.logging_config import setup_logging
from tenacity import retry, stop_after_attempt, wait_fixed

app = typer.Typer()
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
def post_context(base_url: str, headers: dict, data: dict) -> requests.Response:
    """POST to /contexts with retry logic."""
    return requests.post(f"{base_url}/contexts", json=data, headers=headers)


@app.command("context")
def create_context(
    server: str = typer.Option(None, "--server", help="Override MCP server URL"),
    token: str = typer.Option(None, "--token", help="Bearer token for auth"),
    file: Path = typer.Option(
        ..., "--file", "-f", help="YAML or JSON file describing the context"
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Set logging level"),
):
    setup_logging(log_level)
    """
    Create a new context from a YAML or JSON file.
    """
    if not file.exists():
        print(f"[red]❌ File {file} does not exist.[/red]")
        raise typer.Exit(code=1)

    try:
        content = file.read_text()
        if file.suffix.lower() in [".yaml", ".yml"]:
            data = yaml.safe_load(content)
        elif file.suffix.lower() == ".json":
            data = json.loads(content)
        else:
            print("[yellow]⚠️ Unknown file type. Attempting YAML parse...[/yellow]")
            data = yaml.safe_load(content)

        base_url = resolve_server(server)
        headers = (
            {"Authorization": f"Bearer {resolve_token(token)}"}
            if resolve_token(token)
            else {}
        )

        logger.debug("Posting to %s/contexts with headers=%s", base_url, headers)
        response = post_context(base_url, headers, data)
        response.raise_for_status()

        ctx_name = response.json().get("context_name", "unknown")
        print(f"[green]✅ Context created:[/green] {ctx_name}")

    except requests.ConnectionError:
        handle_connection_error(base_url)
    except requests.RequestException as e:
        logger.exception("HTTP error while creating context")
        print(f"[red]❌ Request failed:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception("Unexpected error during context creation")
        print(f"[red]❌ Error parsing or sending request:[/red] {e}")
        raise typer.Exit(code=1)
