import typer
import yaml
import json
import logging
from pathlib import Path
from rich import print
from cockroachdb_mcp_client.providers import PROVIDERS

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command("context")
def run_context(
    provider: str = typer.Option(
        ..., "--provider", "-p", help="LLM provider to use (e.g. openai, anthropic)"
    ),
    file: Path = typer.Option(
        ..., "--file", "-f", help="Path to context YAML or JSON file"
    ),
    input_text: str = typer.Option(
        ..., "--input", "-i", help="Input text to send to the model"
    ),
    stream: bool = typer.Option(False, "--stream", "-s", help="Stream model output"),
    model_override: str = typer.Option(
        None, "--model", help="Override model name (e.g. gpt-4, claude-3-sonnet)"
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Set logging level"),
):
    """
    Simulate an LLM call using the given provider and context.
    """
    from cockroachdb_mcp_client.logging_config import setup_logging

    setup_logging(log_level)

    if provider not in PROVIDERS:
        print(f"[red]❌ Unknown provider:[/red] {provider}")
        logger.error("Unsupported provider: %s", provider)
        raise typer.Exit(code=1)

    if not file.exists():
        print(f"[red]❌ Context file not found:[/red] {file}")
        raise typer.Exit(code=1)

    try:
        content = file.read_text()
        context = (
            yaml.safe_load(content)
            if file.suffix.lower() in [".yaml", ".yml"]
            else json.loads(content)
        )

        if model_override:
            context["body"]["model"] = model_override
            logger.debug("Overriding model to: %s", model_override)

        logger.info("Running context with provider: %s", provider)
        llm = PROVIDERS[provider]()
        result = llm.run(context, input_text, stream=stream)

        if not stream:
            print(f"[bold green]✅ Model Response:[/bold green]\n{result}")

    except Exception as e:
        logger.exception("LLM run failed")
        print(f"[red]❌ Failed to run context:[/red] {e}")
        raise typer.Exit(code=1)
