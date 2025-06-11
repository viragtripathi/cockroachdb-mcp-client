import typer
import yaml
import json
import logging
from pathlib import Path
from cockroachdb_mcp_client.providers import PROVIDERS
from rich import print

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command("context")
def simulate_context(
    provider: str = typer.Option(..., "--provider", "-p", help="LLM provider to use"),
    file: Path = typer.Option(..., "--file", "-f", help="Path to context YAML or JSON"),
    inputs: Path = typer.Option(
        ..., "--inputs", "-i", help="Text file or JSON array of inputs"
    ),
    output: str = typer.Option("text", help="Output format: text or json"),
    stream: bool = typer.Option(False, "--stream", "-s", help="Stream each response"),
    log_level: str = typer.Option("INFO", "--log-level", help="Set logging level"),
):
    """
    Run a batch of inputs through a model context.
    """
    from cockroachdb_mcp_client.logging_config import setup_logging

    setup_logging(log_level)

    if provider not in PROVIDERS:
        print(f"[red]❌ Unknown provider:[/red] {provider}")
        raise typer.Exit(code=1)

    if not file.exists() or not inputs.exists():
        print("[red]❌ Context or input file not found.[/red]")
        raise typer.Exit(code=1)

    try:
        with file.open() as f:
            context = (
                yaml.safe_load(f) if file.suffix.endswith("yaml") else json.load(f)
            )

        with inputs.open() as f:
            if inputs.suffix.endswith(".json"):
                input_lines = json.load(f)
            else:
                input_lines = [line.strip() for line in f.readlines() if line.strip()]

        llm = PROVIDERS[provider]()
        results = []

        for idx, input_text in enumerate(input_lines):
            print(f"\n[cyan]Input {idx + 1}:[/cyan] {input_text}")
            try:
                result = llm.run(context, input_text, stream=stream)
                if not stream:
                    print(f"[green]Output:[/green] {result}")
                    results.append({"input": input_text, "output": result})
            except Exception as e:
                logger.warning("Failed to process input %d: %s", idx + 1, str(e))
                print(f"[red]❌ Failed on input {idx + 1}:[/red] {e}")

        if output == "json" and not stream:
            print(json.dumps(results, indent=2))

    except Exception as e:
        logger.exception("Simulation failed")
        print(f"[red]❌ Simulation failed:[/red] {e}")
        raise typer.Exit(code=1)
