from .anthropic import AnthropicProvider
from .openai import OpenAIProvider

PROVIDERS = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
}
