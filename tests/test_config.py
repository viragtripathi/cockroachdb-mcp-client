from cockroachdb_mcp_client import config

def test_resolve_server_env(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_URL", "http://test-server")
    assert config.resolve_server() == "http://test-server"

def test_resolve_token_env(monkeypatch):
    monkeypatch.setenv("MCP_API_TOKEN", "test-token")
    assert config.resolve_token() == "test-token"
