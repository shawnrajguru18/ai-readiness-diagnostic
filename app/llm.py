"""Thin wrapper around the Anthropic SDK (AWS Bedrock backend).

Two entry points:
  - complete_text(...)        free-text generation (questioner, narrative)
  - parse_structured(...)     schema-constrained output via messages.parse() (capture, scoring, probe)

Defaults to adaptive thinking (recommended for Claude 4.6+) and effort=high.
Uses AWS Bedrock for Claude access (SigV4 auth via IAM, no API key needed).
"""
from __future__ import annotations
from typing import Any, Sequence, Type, TypeVar
from pydantic import BaseModel
import boto3

from anthropic import AnthropicBedrock

from .config import settings, llm_available

T = TypeVar("T", bound=BaseModel)

import logging
logger = logging.getLogger(__name__)

# Resolves AWS credentials from environment/IAM roles (SigV4).
import os
import sys
_aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "not set")
_aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "not set")
_aws_session = os.environ.get("AWS_SESSION_TOKEN", "not set")
_env_summary = f"Key={_aws_key[:10] if _aws_key != 'not set' else 'not set'}..., Secret set={_aws_secret != 'not set'}, Session set={_aws_session != 'not set'}"
logger.info(f"Environment credentials: {_env_summary}")

try:
    _creds = boto3.Session().get_credentials()
    if _creds:
        logger.info(f"boto3 found credentials: access_key={_creds.access_key[:10]}...")
    else:
        logger.warning("boto3.Session().get_credentials() returned None")
except Exception as e:
    logger.error(f"boto3 credential check failed: {e}")

try:
    _client = AnthropicBedrock(aws_region=settings.aws_region)
    logger.info(f"AnthropicBedrock client initialized for region {settings.aws_region}")
except Exception as e:
    logger.error(f"Failed to initialize AnthropicBedrock: {e}")
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
