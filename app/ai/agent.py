"""Pydantic-AI Agent configuration and factory.

Initializes LLM model connections from application settings and provides
factory functions to create task-specific agents for matching and moderation.

Agents are created fresh per call (not cached) so that callers can freely
override model, instructions, or output_type per run.
"""

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.core.config import settings


def _build_model() -> OpenAIChatModel:
    """Build an OpenAIChatModel instance from application settings.

    Uses the PDAI_* environment variables to configure the LLM endpoint.

    Returns:
        A configured OpenAIChatModel ready for use with pydantic_ai.Agent.
    """
    provider = OpenAIProvider(
        base_url=settings.PDAI_BASE_URL,
        api_key=settings.PDAI_API_KEY,
    )
    return OpenAIChatModel(
        model_name=settings.PDAI_MODEL,
        provider=provider,
    )


def create_agent(**kwargs) -> Agent:
    """Create a new Agent instance with the project's default model.

    Args:
        **kwargs: Forwarded to the Agent constructor (output_type,
            system_prompt, instructions, etc.).

    Returns:
        A configured pydantic_ai.Agent ready to execute runs.
    """
    model = _build_model()
    return Agent(model, **kwargs)
