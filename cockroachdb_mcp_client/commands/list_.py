import typer
import requests
import json
import logging
from rich import print_json
from cockroachdb_mcp_client.config import resolve_server, resolve_token
from cockroachdb_mcp_client.utils import handle_connection_error
from tenacity import retry, stop_after_attempt, wait_fixed

app = typer.Typer()
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
def fetch_contexts(base_url: str, headers: dict) -> requests.Response:
    return requests.get(f"{base_url}/contexts", headers=headers)


@app.command("contexts")
def list_contexts(
    server: str = typer.Option(None, "--server", help="Override MCP server URL"),
    token: str = typer.Option(None, "--token", help="Bearer token for auth"),
    output: str = typer.Option("json", help="Output format: json or yaml"),
    log_level: str = typer.Option("INFO", "--log-level", help="Set logging level"),
):
    """
    List all contexts from the MCP server.
    """
    from cockroachdb_mcp_client.logging_config import setup_logging

    setup_logging(log_level)

    try:
        base_url = resolve_server(server)
        headers = (
            {"Authorization": f"Bearer {resolve_token(token)}"}
            if resolve_token(token)
            else {}
        )

        logger.debug("Fetching contexts from %s with headers=%s", base_url, headers)
        response = fetch_contexts(base_url, headers)
        response.raise_for_status()
        data = response.json()

        if output == "json":
            print_json(json.dumps(data))
        elif output == "yaml":
            import yaml

            print(yaml.dump(data, sort_keys=False))
        else:
            print(f"[red]❌ Unsupported output format: {output}[/red]")

    except requests.ConnectionError:
        handle_connection_error(base_url)
    except requests.RequestException as e:
        logger.exception("HTTP error while listing contexts")
        print(f"[red]❌ Request failed:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception("Unexpected error while listing contexts")
        print(f"[red]❌ Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)
