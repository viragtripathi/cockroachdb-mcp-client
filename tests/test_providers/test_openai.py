from cockroachdb_mcp_client.providers.openai import OpenAIProvider
import pytest

def test_openai_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        OpenAIProvider().run({}, "test")
