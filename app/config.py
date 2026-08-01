"""Configuration + model tiering (Companion 04).

Companion 04 assigns Opus to the analytically hardest agents (C2 Synthesis, C3 Quick Wins,
D2 Validation), Sonnet to research/personalization/output (A2, B1-B5, C1, D1), and Haiku to
A1 intake. We map those tiers to Bedrock model IDs (anthropic.* prefix).

Models are accessed via AWS Bedrock (SigV4 auth, no API key). Credentials resolved from:
environment variables, IAM roles, credential files per boto3 documentation.
Override any tier via env vars: AIDIAG_MODEL_OPUS, AIDIAG_MODEL_SONNET, etc.
"""
from __future__ import annotations
import os
import boto3

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def llm_available() -> bool:
    """True when AWS credentials are configured; otherwise the pipeline runs offline."""
    import logging
    logger = logging.getLogger(__name__)

    # Force LLM if environment variable is set (for debugging)
    force_llm_env = os.getenv("AIDIAG_FORCE_LLM", "false")
    force_llm = force_llm_env.lower() == "true"
    print(f"[DEBUG_CONFIG] AIDIAG_FORCE_LLM={force_llm_env!r} -> {force_llm}")
    if force_llm:
        logger.warning("AIDIAG_FORCE_LLM is set - forcing LLM invocation regardless of credential check")
        return True

    try:
        creds = boto3.Session().get_credentials()
        if creds:
            logger.info(f"AWS credentials available: {creds.access_key[:10]}...")
            return True
        else:
            logger.warning("boto3.Session().get_credentials() returned None")
            return False
    except Exception as e:
        logger.error(f"Error checking AWS credentials: {type(e).__name__}: {str(e)[:200]}")
        return False


class Settings:
    # AWS region for Bedrock
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # tiers -> Bedrock model IDs (API format from Bedrock console)
    model_opus: str = os.getenv("AIDIAG_MODEL_OPUS", "anthropic.claude-opus-4-8")
    model_sonnet: str = os.getenv("AIDIAG_MODEL_SONNET", "anthropic.claude-sonnet-5")
    model_haiku: str = os.getenv("AIDIAG_MODEL_HAIKU", "anthropic.claude-haiku-4-5")
    default_model: str = os.getenv("AIDIAG_MODEL_DEFAULT", "anthropic.claude-sonnet-5")
    effort: str = os.getenv("AIDIAG_EFFORT", "high")
    enable_research: bool = os.getenv("AIDIAG_ENABLE_RESEARCH", "false").lower() == "true"
    sec_user_agent: str = os.getenv("AIDIAG_SEC_USER_AGENT", "DXC AdvisoryX Diagnostic contact@dxc.com")


settings = Settings()
