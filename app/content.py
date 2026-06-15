"""Loaders for static reference content: the question pool, quick-wins library, fixtures."""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
FIXTURE_DIR = ROOT / "fixtures"


@lru_cache(maxsize=1)
def load_question_pool() -> dict:
    return yaml.safe_load((CONTENT_DIR / "question_pool.yaml").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def questions_by_id() -> dict[str, dict]:
    return {q["id"]: q for q in load_question_pool()["questions"]}


@lru_cache(maxsize=1)
def load_quick_wins() -> list[dict]:
    return yaml.safe_load((CONTENT_DIR / "quick_wins.yaml").read_text(encoding="utf-8"))["patterns"]


@lru_cache(maxsize=1)
def quick_wins_by_id() -> dict[str, dict]:
    return {p["pattern_id"]: p for p in load_quick_wins()}


def load_fixture(name: str) -> dict:
    return yaml.safe_load((FIXTURE_DIR / f"{name}.yaml").read_text(encoding="utf-8"))
