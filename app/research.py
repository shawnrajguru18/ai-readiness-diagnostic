"""Research agents B1 (SEC EDGAR financials) and B2 (news), best-effort.

These feed C2's research_adjustment + findings. They are network calls with short
timeouts and must NEVER break the pipeline — every failure degrades to a 'limited'
signal. On a corporate network that intercepts TLS, calls may fail; that is handled.
"""
from __future__ import annotations
import json
import httpx

from .config import settings

_UA = {"User-Agent": settings.sec_user_agent}
_TIMEOUT = 8.0


# ---------------- B1: SEC EDGAR ----------------
def _resolve_cik(company: str) -> tuple[str, str] | None:
    """Fuzzy-match a company name to a CIK via SEC's ticker map."""
    try:
        r = httpx.get("https://www.sec.gov/files/company_tickers.json", headers=_UA, timeout=_TIMEOUT)
        if r.status_code != 200:
            return None
        data = r.json()
        needle = company.lower().split(",")[0].strip()
        best = None
        for row in data.values():
            title = str(row.get("title", "")).lower()
            if needle and (needle in title or title in needle):
                best = (str(row["cik_str"]).zfill(10), row.get("title", ""))
                if needle == title:
                    break
        return best
    except Exception:
        return None


def b1_financial(company: str) -> dict:
    out: dict = {"agent": "B1", "research_status": "limited_public_data", "company": company, "signals": []}
    resolved = _resolve_cik(company)
    if not resolved:
        out["reasoning_summary"] = f"No public SEC filer matched '{company}' (private company or name mismatch)."
        return out
    cik, title = resolved
    out["company_canonical"] = title
    out["cik"] = cik
    try:
        r = httpx.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=_UA, timeout=_TIMEOUT)
        if r.status_code == 200:
            sub = r.json()
            recent = sub.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])[:8]
            dates = recent.get("filingDate", [])[:8]
            out["research_status"] = "partial"
            out["recent_filings"] = [{"form": f, "date": d} for f, d in zip(forms, dates)]
            out["sic_description"] = sub.get("sicDescription", "")
            out["signals"].append(
                f"Public filer ({title}); recent forms: {', '.join(sorted(set(forms))) or 'n/a'}."
            )
            out["reasoning_summary"] = (
                f"{title} is an SEC filer ({sub.get('sicDescription','')}). "
                "Filing parse for AI-relevant MD&A/risk-factor disclosure is the next step (deferred)."
            )
    except Exception as e:  # noqa: BLE001
        out["reasoning_summary"] = f"EDGAR submissions lookup failed: {type(e).__name__}."
    return out


# ---------------- B2: News ----------------
def b2_news(company: str) -> dict:
    """Best-effort AI-news posture. With no news API key configured, returns a structured
    'no_significant_signals' placeholder so triangulation has a slot (wire a news API per PRD)."""
    out: dict = {"agent": "B2", "research_status": "no_significant_signals", "company": company,
                 "ai_news_signals": []}
    # Optional: SEC EDGAR full-text search as a free proxy for recent AI-relevant filing mentions.
    try:
        r = httpx.get("https://efts.sec.gov/LATEST/search-index",
                      params={"q": f'"{company}" artificial intelligence'}, headers=_UA, timeout=_TIMEOUT)
        if r.status_code == 200:
            try:
                hits = r.json().get("hits", {}).get("total", {}).get("value", 0)
            except Exception:
                hits = 0
            if hits:
                out["research_status"] = "partial"
                out["ai_news_signals"].append({
                    "signal_type": "ai_investment",
                    "summary": f"~{hits} EDGAR full-text matches pairing '{company}' with AI language.",
                    "substance_level": "moderate",
                })
                out["overall_ai_posture_assessment"] = f"Public documents reference AI in proximity to {company}."
    except Exception:
        pass
    out.setdefault("overall_ai_posture_assessment",
                   f"No substantive public AI signals retrieved for {company} (news API not configured).")
    return out


def run_research(company: str) -> dict:
    """Run B1 + B2; always returns a dict, never raises."""
    research = {"B1": b1_financial(company), "B2": b2_news(company)}
    return research


def research_summary(research: dict) -> str:
    parts = []
    b1 = research.get("B1", {})
    if b1.get("reasoning_summary"):
        parts.append("Financial (B1): " + b1["reasoning_summary"])
    b2 = research.get("B2", {})
    if b2.get("overall_ai_posture_assessment"):
        parts.append("News (B2): " + b2["overall_ai_posture_assessment"])
    return " ".join(parts) or "No external research signals."
