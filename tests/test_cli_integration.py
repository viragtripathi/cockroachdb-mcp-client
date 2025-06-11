import subprocess
import pytest

def test_real_list_contexts():
    result = subprocess.run(["cockroachdb-mcp-client", "list", "contexts"], capture_output=True, text=True)
    if "Failed to connect" in result.stdout:
        pytest.skip("MCP server not running in CI")
    assert result.returncode == 0
