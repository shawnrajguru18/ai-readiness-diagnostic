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


def client() -> Anthropic | None:
    if _client is None:
        logger.error("LLM client is None - Anthropic client failed to initialize. Check AWS credentials.")
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
    """Schema-constrained generation via tool-based enforcement (Bedrock-compatible)."""
    from .config import llm_available
    import json
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Invoking Bedrock: model={model or settings.default_model}, llm_available={llm_available()}")

    try:
        # Convert Pydantic schema to tool definition
        schema_dict = schema.model_json_schema()
        tool_def = {
            "name": "output_schema",
            "description": f"Structured output conforming to {schema.__name__}",
            "input_schema": {
                "type": "object",
                "properties": schema_dict.get("properties", {}),
                "required": schema_dict.get("required", list(schema_dict.get("properties", {}).keys())),
            }
        }

        # Call with tool enforcement (Bedrock-compatible)
        resp = _client.messages.create(
            model=model or settings.default_model,
            max_tokens=max_tokens,
            system=system,
            messages=list(messages),
            tools=[tool_def],
            tool_choice={"type": "tool", "name": "output_schema"},
        )

        # Extract JSON from tool call
        if resp.stop_reason != "tool_use":
            raise RuntimeError(f"Expected tool_use stop reason, got {resp.stop_reason}")

        tool_call = next((b for b in resp.content if b.type == "tool_use"), None)
        if not tool_call:
            raise RuntimeError("No tool_use block found in response")

        # Parse and validate
        parsed_data = schema.model_validate(tool_call.input)
        logger.info(f"Structured output succeeded via tool_use")
        return parsed_data

    except Exception as e:
        logger.error(f"Bedrock structured invoke failed: {type(e).__name__}: {str(e)[:500]}")
        raise
