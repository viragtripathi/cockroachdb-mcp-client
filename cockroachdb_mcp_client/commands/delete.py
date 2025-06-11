import typer
import requests
import logging
from rich import print
from cockroachdb_mcp_client.config import resolve_server, resolve_token
from cockroachdb_mcp_client.utils import handle_connection_error
from tenacity import retry, stop_after_attempt, wait_fixed

app = typer.Typer()
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
def delete_from_server(
    base_url: str, context_id: str, headers: dict
) -> requests.Response:
    return requests.delete(f"{base_url}/contexts/{context_id}", headers=headers)


@app.command("context")
def delete_context(
    context_id: str,
    server: str = typer.Option(None, "--server", help="Override MCP server URL"),
    token: str = typer.Option(None, "--token", help="Bearer token for auth"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    log_level: str = typer.Option("INFO", "--log-level", help="Set logging level"),
):
    """
    Delete a context by its UUID.
    """
    from cockroachdb_mcp_client.logging_config import setup_logging

    setup_logging(log_level)

    if not yes:
        confirm = typer.confirm(
            f"Are you sure you want to delete context {context_id}?"
        )
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit()

    try:
        base_url = resolve_server(server)
        headers = (
            {"Authorization": f"Bearer {resolve_token(token)}"}
            if resolve_token(token)
            else {}
        )

        logger.debug("Sending DELETE to %s/contexts/%s", base_url, context_id)
        response = delete_from_server(base_url, context_id, headers)

        if response.status_code == 404:
            print(f"[yellow]⚠️ Context {context_id} not found.[/yellow]")
            raise typer.Exit(code=1)

        response.raise_for_status()
        print(f"[green]✅ Deleted:[/green] {context_id}")

    except requests.ConnectionError:
        handle_connection_error(base_url)
    except requests.RequestException as e:
        logger.exception("HTTP error while deleting context")
        print(f"[red]❌ Request failed:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception("Unexpected error while deleting context")
        print(f"[red]❌ Unexpected error:[/red] {e}")
        raise typer.Exit(code=1)
