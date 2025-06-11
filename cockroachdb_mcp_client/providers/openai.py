from .base import BaseLLMProvider
import openai
import os
from cockroachdb_mcp_client.config import load_config


class OpenAIProvider(BaseLLMProvider):
    def run(self, context: dict, input_text: str, stream: bool = False) -> str:
        api_key = os.getenv("OPENAI_API_KEY") or load_config().get("openai", {}).get(
            "api_key"
        )

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set.")

        openai.api_key = api_key
        model = context.get("body", {}).get("model", "gpt-3.5-turbo")

        system_msg = context.get("body", {}).get(
            "description", "You are an AI assistant."
        )
        user_prompt = input_text

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ]

        if stream:
            response = openai.ChatCompletion.create(
                model=model, messages=messages, temperature=0.7, stream=True
            )
            for chunk in response:
                if "choices" in chunk and chunk.choices[0].delta.get("content"):
                    print(chunk.choices[0].delta["content"], end="", flush=True)
            print()
            return ""
        else:
            response = openai.ChatCompletion.create(
                model=model, messages=messages, temperature=0.7
            )
            return response.choices[0].message["content"].strip()
