from .base import BaseLLMProvider
import anthropic
import os
from cockroachdb_mcp_client.config import load_config


class AnthropicProvider(BaseLLMProvider):
    def run(self, context: dict, input_text: str, stream: bool = False) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY") or load_config().get(
            "anthropic", {}
        ).get("api_key")

        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set.")

        client = anthropic.Anthropic(api_key=api_key)

        model = context.get("body", {}).get("model", "claude-3-opus-20240229")
        system_msg = context.get("body", {}).get(
            "description", "You are a helpful assistant."
        )
        user_prompt = input_text

        if stream:
            stream_resp = client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_msg,
                messages=[{"role": "user", "content": user_prompt}],
                stream=True,
            )
            # stream is a generator
            for chunk in stream_resp:
                if chunk.type == "content_block_delta":
                    print(chunk.delta.text or "", end="", flush=True)
            print()
            return ""
        else:
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_msg,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text.strip()
