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
    try:
        boto3.Session().get_credentials()
        return True
    except Exception:
        return False


class Settings:
    # AWS region for Bedrock
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # tiers -> Bedrock model IDs (Claude 5 / Opus 4.8, auto-enabled on first invocation)
    model_opus: str = os.getenv("AIDIAG_MODEL_OPUS", "anthropic.claude-opus-4-8-20250514-v1:0")
    model_sonnet: str = os.getenv("AIDIAG_MODEL_SONNET", "anthropic.claude-5-sonnet-20241022-v2:0")
    model_haiku: str = os.getenv("AIDIAG_MODEL_HAIKU", "anthropic.claude-haiku-4-5-20251001-v1:0")
    default_model: str = os.getenv("AIDIAG_MODEL_DEFAULT", "anthropic.claude-5-sonnet-20241022-v2:0")
    effort: str = os.getenv("AIDIAG_EFFORT", "high")
    enable_research: bool = os.getenv("AIDIAG_ENABLE_RESEARCH", "false").lower() == "true"
    sec_user_agent: str = os.getenv("AIDIAG_SEC_USER_AGENT", "DXC AdvisoryX Diagnostic contact@dxc.com")


settings = Settings()
