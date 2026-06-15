"""Thin wrapper around the Anthropic SDK.

Two entry points:
  - complete_text(...)        free-text generation (questioner, narrative)
  - parse_structured(...)     schema-constrained output via messages.parse() (capture, scoring, probe)

Defaults to adaptive thinking (recommended for Claude 4.6+) and effort=high.
"""
from __future__ import annotations
from typing import Any, Sequence, Type, TypeVar
from pydantic import BaseModel

import anthropic

from .config import settings

T = TypeVar("T", bound=BaseModel)

# Resolves ANTHROPIC_API_KEY from the environment.
_client = anthropic.Anthropic()


def client() -> anthropic.Anthropic:
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
        output_config={"effort": effort or settings.effort},
    )
    if thinking:
        kwargs["thinking"] = {"type": "adaptive"}
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
    """Schema-constrained generation via messages.parse().

    NOTE: messages.parse() sets output_config.format from `output_format`, so we do
    NOT pass output_config here (effort defaults to high server-side) to avoid clobbering it.
    Structured outputs are compatible with adaptive thinking.
    """
    kwargs: dict[str, Any] = dict(
        model=model or settings.default_model,
        max_tokens=max_tokens,
        system=system,
        messages=list(messages),
        output_format=schema,
    )
    if thinking:
        kwargs["thinking"] = {"type": "adaptive"}
    resp = _client.messages.parse(**kwargs)
    parsed = resp.parsed_output
    if parsed is None:
        raise RuntimeError(
            f"Structured output failed (stop_reason={resp.stop_reason}). "
            "If refusal, inspect resp.stop_details."
        )
    return parsed
