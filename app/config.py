"""Configuration + model tiering (Companion 04).

Companion 04 assigns Opus to the analytically hardest agents (C2 Synthesis, C3 Quick Wins,
D2 Validation), Sonnet to research/personalization/output (A2, B1-B5, C1, D1), and Haiku to
A1 intake. We map those tiers to the current model IDs (Opus 4.8 is the current Opus; the
Companion was authored against 4.7). Override any tier via env.
"""
from __future__ import annotations
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def llm_available() -> bool:
    """True when an Anthropic key is configured; otherwise the pipeline runs offline."""
    return bool(os.getenv("ANTHROPIC_API_KEY"))


class Settings:
    # tiers -> current model IDs
    model_opus: str = os.getenv("AIDIAG_MODEL_OPUS", "claude-opus-4-8")
    model_sonnet: str = os.getenv("AIDIAG_MODEL_SONNET", "claude-sonnet-4-6")
    model_haiku: str = os.getenv("AIDIAG_MODEL_HAIKU", "claude-haiku-4-5")
    default_model: str = os.getenv("AIDIAG_MODEL_DEFAULT", "claude-opus-4-8")
    effort: str = os.getenv("AIDIAG_EFFORT", "high")
    enable_research: bool = os.getenv("AIDIAG_ENABLE_RESEARCH", "false").lower() == "true"
    sec_user_agent: str = os.getenv("AIDIAG_SEC_USER_AGENT", "DXC AdvisoryX Diagnostic contact@dxc.com")


settings = Settings()
