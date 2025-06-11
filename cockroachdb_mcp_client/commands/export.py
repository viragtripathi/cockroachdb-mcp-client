import typer
import requests
import yaml
import json
import logging
from pathlib import Path
from rich import print
from cockroachdb_mcp_client.config import resolve_server, resolve_token
from cockroachdb_mcp_client.utils import handle_connection_error
from tenacity import retry, stop_after_attempt, wait_fixed

app = typer.Typer()
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
def fetch_context(base_url: str, context_id: str, headers: dict) -> dict:
    response = requests.get(f"{base_url}/contexts/{context_id}", headers=headers)
    if response.status_code == 404:
        raise typer.Exit(code=1)
    response.raise_for_status()
    return response.json()


@app.command("context")
def export_context(
    context_id: str,
    file: Path = typer.Option(
        ..., "--file", "-f", help="Output file name (e.g. summarizer.yaml)"
    ),
    output: str = typer.Option("yaml", help="Output format: json or yaml"),
    server: str = typer.Option(None, "--server", help="Override MCP server URL"),
    token: str = typer.Option(None, "--token", help="Bearer token for auth"),
    log_level: str = typer.Option("INFO", "--log-level", help="Set logging level"),
):
    """Export a context by ID to a local YAML or JSON file."""
    from cockroachdb_mcp_client.logging_config import setup_logging

    setup_logging(log_level)

    try:
        base_url = resolve_server(server)
        headers = (
            {"Authorization": f"Bearer {resolve_token(token)}"}
            if resolve_token(token)
            else {}
        )
        logger.debug("Exporting context %s from %s", context_id, base_url)

        try:
            context = fetch_context(base_url, context_id, headers)
        except typer.Exit:
            print(f"[yellow]⚠️ Context {context_id} not found.[/yellow]")
            return

        context.pop("id", None)
        context.pop("created_at", None)
        file.parent.mkdir(parents=True, exist_ok=True)

        if output == "json":
            file.write_text(json.dumps(context, indent=2))
        elif output == "yaml":
            file.write_text(yaml.dump(context, sort_keys=False))
        else:
            print("[red]❌ Unsupported output format[/red]")
            raise typer.Exit(code=1)

        print(f"[green]✅ Exported context to:[/green] {file}")

    except requests.ConnectionError:
        handle_connection_error(base_url)
    except Exception as e:
        logger.exception("Export failed")
        print(f"[red]❌ Export failed:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("all")
def export_all(
    output_dir: Path = typer.Option(
        ..., "--output-dir", "-o", help="Directory to save exported files"
    ),
    output: str = typer.Option("yaml", help="Format: json or yaml"),
    server: str = typer.Option(None, "--server", help="Override MCP server URL"),
    token: str = typer.Option(None, "--token", help="Bearer token for auth"),
    log_level: str = typer.Option("INFO", "--log-level", help="Set logging level"),
):
    """Export all contexts to the specified directory."""
    from cockroachdb_mcp_client.logging_config import setup_logging

    setup_logging(log_level)

    base_url = resolve_server(server)
    headers = (
        {"Authorization": f"Bearer {resolve_token(token)}"}
        if resolve_token(token)
        else {}
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        index_response = requests.get(f"{base_url}/contexts", headers=headers)
        index_response.raise_for_status()
        context_refs = index_response.json().get("contexts", [])

        if not context_refs:
            print("[yellow]⚠️ No contexts found to export.[/yellow]")
            raise typer.Exit()

        for ref in context_refs:
            context_id = ref["id"]
            try:
                context = fetch_context(base_url, context_id, headers)
                context.pop("id", None)
                context.pop("created_at", None)

                ext = "yaml" if output == "yaml" else "json"
                filename = f"{context['context_name']}-{context_id[:8]}.{ext}"
                file_path = output_dir / filename

                if output == "yaml":
                    file_path.write_text(yaml.dump(context, sort_keys=False))
                else:
                    file_path.write_text(json.dumps(context, indent=2))

                print(f"[green]✅ Exported:[/green] {file_path}")
            except Exception as e:
                logger.warning("Failed to export context %s: %s", context_id, str(e))
                print(f"[red]❌ Failed to export context {context_id}:[/red] {e}")

    except requests.ConnectionError:
        handle_connection_error(base_url)
    except Exception as e:
        logger.exception("Failed to export all contexts")
        print(f"[red]❌ Failed to fetch context list:[/red] {e}")
        raise typer.Exit(code=1)
