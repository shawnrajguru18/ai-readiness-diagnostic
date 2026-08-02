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
    logger.info(f"✓ Anthropic client initialized with Bedrock Mantle endpoint")
    print(f"[LLM_INIT] ✓ Client initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize Anthropic client: {e}")
    print(f"[LLM_INIT] ✗ Client initialization FAILED: {type(e).__name__}: {e}")
    _client = None


def client() -> Anthropic | None:
    if _client is None:
        logger.error("LLM client is None - Anthropic client failed to initialize. Check AWS credentials.")
    return _client


def _remediate_payload(data: dict) -> dict:
    """Fix common hallucinations and missing fields before Pydantic validation."""
    import copy
    remediated = copy.deepcopy(data)

    # Fix missing confidence in dimension_reasoning
    if "dimension_reasoning" in remediated and isinstance(remediated["dimension_reasoning"], list):
        for item in remediated["dimension_reasoning"]:
            if "confidence" not in item:
                item["confidence"] = 1.0

    # Fix missing/malformed fields in findings
    if "findings" in remediated and isinstance(remediated["findings"], list):
        for idx, item in enumerate(remediated["findings"]):
            # Remap 'title' to 'headline' if needed
            if "title" in item and "headline" not in item:
                item["headline"] = item.pop("title")

            # Ensure all required fields exist with safe defaults
            if "finding_id" not in item:
                item["finding_id"] = f"finding_{idx}"
            if "headline" not in item:
                item["headline"] = "Finding"
            if "decision_relevance" not in item:
                item["decision_relevance"] = "Medium"
            if "confidence" not in item:
                item["confidence"] = 1.0

    return remediated


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
    import sys
    logger = logging.getLogger(__name__)

    print(f"[BEDROCK] parse_structured called for schema={schema.__name__}, model={model or settings.default_model}")
    logger.info(f"Invoking Bedrock: model={model or settings.default_model}, llm_available={llm_available()}")

    try:
        # Convert Pydantic schema to tool definition
        schema_dict = schema.model_json_schema()

        # Extract just the parts we need for the tool input schema
        # Include all properties and required fields from the main schema
        input_schema = {
            "type": "object",
            "properties": schema_dict.get("properties", {}),
            "required": schema_dict.get("required", []),
        }

        # If there are definitions (nested models), include them for full JSON Schema validation
        if "$defs" in schema_dict:
            input_schema["$defs"] = schema_dict["$defs"]

        tool_def = {
            "name": "output_schema",
            "description": f"Structured output conforming to {schema.__name__}. ALL fields marked as required must be included in the response.",
            "input_schema": input_schema
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

        # Remediate common hallucinations before validation
        remediated = _remediate_payload(tool_call.input)

        # Parse and validate
        parsed_data = schema.model_validate(remediated)
        logger.info(f"Structured output succeeded via tool_use")
        return parsed_data

    except Exception as e:
        error_msg = f"Bedrock structured invoke failed: {type(e).__name__}: {str(e)[:500]}"
        print(f"[BEDROCK] ✗ EXCEPTION: {error_msg}")
        logger.error(error_msg)
        raise
