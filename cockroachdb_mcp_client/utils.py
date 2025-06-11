from rich import print
import typer


def handle_connection_error(base_url: str):
    print(f"[red]❌ Failed to connect to MCP server at {base_url}[/red]")
    print()
    print("[yellow]🔧 Is the server running? Start it with:[/yellow]")
    print("  scockroachdb-mcp-server serve --init-schema")
    print()
    print("[yellow]🌍 To override the MCP server URL:[/yellow]")
    print("  --server http://localhost:8081")
    print("  OR")
    print("  export MCP_SERVER_URL=http://localhost:8081")
    raise typer.Exit(code=1)
