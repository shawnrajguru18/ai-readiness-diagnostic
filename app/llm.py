"""Thin wrapper around the Anthropic SDK (AWS Bedrock backend).

Two entry points:
  - complete_text(...)        free-text generation (questioner, narrative)
  - parse_structured(...)     schema-constrained output via messages.parse() (capture, scoring, probe)

Defaults to adaptive thinking (recommended for Claude 4.6+) and effort=high.
Uses AWS Bedrock for Claude access via Bedrock API key + Mantle endpoint.
"""
from __future__ import annotations
from typing import Any, Sequence, Type, TypeVar
from pydantic import BaseModel
import os
import logging

from anthropic import Anthropic

from .config import settings, llm_available

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

# Check for Bedrock API key (required for Mantle endpoint)
_api_key = os.environ.get("ANTHROPIC_API_KEY")
_base_url = os.environ.get("ANTHROPIC_BASE_URL")
_aws_region = os.environ.get("AWS_REGION", settings.aws_region)

if _api_key:
    logger.info(f"Using Bedrock API key authentication with base_url: {_base_url}")
else:
    logger.warning("ANTHROPIC_API_KEY not set - LLM calls will fail. Set it in environment variables.")

# Build base_url if not explicitly set
if not _base_url and _api_key:
    _base_url = f"https://bedrock-mantle.{_aws_region}.api.aws/anthropic"
    logger.info(f"Constructed base_url: {_base_url}")

try:
    _client = Anthropic(api_key=_api_key or "", base_url=_base_url)
    logger.info(f"Anthropic client initialized with Bedrock Mantle endpoint")
except Exception as e:
    logger.error(f"Failed to initialize Anthropic client: {e}")
    _client = None


def client() -> AnthropicBedrock:
    if _client is None:
        logger.error("LLM client is None - AnthropicBedrock failed to initialize. Check AWS credentials.")
    return _client


def complete_text(
    system: str,
    messages: Sequence[dict[str, Any]],
    *,
    model: str | None = None,
    effort: str | None = None,
    thinking: bool = True,
    max_tokens: int = 4000,
) -> str:
    """Generate free text. Returns the concatenated text blocks."""
    kwargs: dict[str, Any] = dict(
        model=model or settings.default_model,
        max_tokens=max_tokens,
        system=system,
        messages=list(messages),
    )
    resp = _client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def parse_structured(
    system: str,
    messages: Sequence[dict[str, Any]],
    schema: Type[T],
    *,
    model: str | None = None,
    thinking: bool = True,
    max_tokens: int = 8000,
) -> T:
    """Schema-constrained generation via messages.parse()."""
    from .config import llm_available
    import logging
    logger = logging.getLogger(__name__)

    kwargs: dict[str, Any] = dict(
        model=model or settings.default_model,
        max_tokens=max_tokens,
        system=system,
        messages=list(messages),
        output_format=schema,
    )

    logger.info(f"Invoking Bedrock: model={kwargs['model']}, llm_available={llm_available()}")

    try:
        resp = _client.messages.parse(**kwargs)
        parsed = resp.parsed_output
        if parsed is None:
            raise RuntimeError(
                f"Structured output failed (stop_reason={resp.stop_reason}). "
                "If refusal, inspect resp.stop_details."
            )
        return parsed
    except Exception as e:
        logger.error(f"Bedrock invoke failed: {type(e).__name__}: {str(e)[:500]}")
        raise
