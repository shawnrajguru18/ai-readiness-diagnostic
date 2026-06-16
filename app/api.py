"""FastAPI backend for the React UI + partner-review dashboard + PDF deliverable.

  GET  /api/questions             question pool (questionnaire screen)
  GET  /api/fixture/{name}        run a demo fixture -> scorecard (stored, returns id)
  POST /api/assess               {submission, consent, responses} -> scorecard (stored, returns id)
  GET  /api/review/queue          partner review queue
  GET  /api/review/{id}           full scorecard + validation + reasoning for review
  POST /api/review/{id}/decision  {decision: approved|sent_back, note}
  GET  /api/scorecard/{id}/pdf    server-side PDF deliverable (reportlab)
  /                              React app (web/index.html)
  /review                        partner review dashboard (web/review.html)

Run:  python -m uvicorn app.api:app --reload   (from repo root)
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .content import load_question_pool, load_fixture
from .models import TIER_COLORS, Session
from .orchestrator import build_session, run_pipeline
from .pdf import (build_scorecard_pdf, build_quickwins_memo_pdf, build_appendix_pdf,
                  build_action_plan_pdf, build_board_brief_pdf)

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"

app = FastAPI(title="DXC AI Readiness Diagnostic", version="0.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve vendored front-end libs (React/ReactDOM/Babel/Tailwind) locally — no external CDN.
_VENDOR = ROOT / "web" / "vendor"
if _VENDOR.is_dir():
    app.mount("/vendor", StaticFiles(directory=str(_VENDOR)), name="vendor")

# In-memory store (V0; PostgreSQL per Companion 05 in production).
STORE: dict[str, dict[str, Any]] = {}


def _serialize(session: Session) -> dict[str, Any]:
    sc = session.scorecard
    d = sc.model_dump()
    for dim in d["dimensions"]:
        dim["color"] = TIER_COLORS.get(dim["tier"], "#FFAE41")
    d["overall_color"] = TIER_COLORS.get(sc.overall_tier, "#FFAE41")
    d["validation"] = session.validation.model_dump() if session.validation else None
    d["persona"] = session.persona.primary_persona
    return d


def _store(session: Session) -> str:
    sid = uuid.uuid4().hex[:10]
    STORE[sid] = {
        "id": sid,
        "session": session,
        "scorecard": _serialize(session),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "partner_review_queued",
        "partner_note": "",
    }
    return sid


class AssessRequest(BaseModel):
    submission: dict
    consent: dict = {}
    responses: dict = {}
    persona_hint: Optional[str] = None


class DecisionRequest(BaseModel):
    decision: str  # "approved" | "sent_back"
    note: str = ""


@app.get("/api/questions")
def questions():
    return load_question_pool()


@app.get("/api/fixture/{name}")
def fixture(name: str):
    try:
        fx = load_fixture(name)
    except FileNotFoundError:
        raise HTTPException(404, f"Unknown fixture: {name}")
    session, hint = build_session(fx.get("submission", {}), fx.get("consent", {}),
                                  fx.get("responses", {}), fx.get("persona_hint"))
    run_pipeline(session, persona_hint=hint)
    sid = _store(session)
    out = dict(_serialize(session)); out["id"] = sid
    return JSONResponse(out)


@app.post("/api/assess")
def assess(req: AssessRequest):
    session, hint = build_session(req.submission, req.consent, req.responses, req.persona_hint)
    run_pipeline(session, persona_hint=hint)
    sid = _store(session)
    out = dict(_serialize(session)); out["id"] = sid
    return JSONResponse(out)


# ---------------- Partner review (Screen 6) ----------------
@app.get("/api/review/queue")
def review_queue():
    rows = []
    for rec in STORE.values():
        sc = rec["scorecard"]; val = sc.get("validation") or {}
        flags = val.get("flags", [])
        rows.append({
            "id": rec["id"],
            "company": sc["company_name"],
            "overall_score": sc["overall_score"],
            "overall_tier": sc["overall_tier"],
            "created_at": rec["created_at"],
            "status": rec["status"],
            "flag_count": len(flags),
            "validation_status": val.get("overall_status", "passed"),
            "priority": val.get("partner_review_priority", "standard"),
        })
    # expedited first, then by flag count
    order = {"expedited": 0, "standard": 1, "deferred": 2}
    rows.sort(key=lambda r: (order.get(r["priority"], 1), -r["flag_count"]))
    return {"queue": rows}


@app.get("/api/review/{sid}")
def review_detail(sid: str):
    rec = STORE.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    sc = rec["scorecard"]
    session: Session = rec["session"]
    return {
        "id": sid, "status": rec["status"], "partner_note": rec["partner_note"],
        "scorecard": sc,
        "reasoning": {
            "dimension_reasoning": [{"dimension": d.dimension, "label": d.label, "reasoning": d.reasoning,
                                     "confidence": d.confidence} for d in session.scorecard.dimensions],
            "partner_attention_flags": session.scorecard.partner_attention_flags,
        },
    }


@app.post("/api/review/{sid}/decision")
def review_decision(sid: str, req: DecisionRequest):
    rec = STORE.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    rec["status"] = "approved_for_delivery" if req.decision == "approved" else "sent_back_for_reprocessing"
    rec["partner_note"] = req.note
    if rec["session"]:
        rec["session"].partner_approved = req.decision == "approved"
    return {"id": sid, "status": rec["status"]}


# ---------------- PDF deliverable ----------------
@app.get("/api/scorecard/{sid}/pdf")
def scorecard_pdf(sid: str):
    rec = STORE.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    pdf = build_scorecard_pdf(rec["session"].scorecard)
    fname = f"AI-Readiness-Scorecard-{rec['scorecard']['company_name']}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{fname}"'})


def _pdf_response(rec, builder, label):
    pdf = builder(rec["session"].scorecard) if builder is not build_appendix_pdf else builder(rec["session"])
    fname = f"{label}-{rec['scorecard']['company_name']}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{fname}"'})


@app.get("/api/scorecard/{sid}/quickwins.pdf")
def quickwins_pdf(sid: str):
    rec = STORE.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    return _pdf_response(rec, build_quickwins_memo_pdf, "Quick-Wins-Memo")


@app.get("/api/scorecard/{sid}/appendix.pdf")
def appendix_pdf(sid: str):
    rec = STORE.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    return _pdf_response(rec, build_appendix_pdf, "Findings-Appendix")


@app.get("/api/scorecard/{sid}/action-plan.pdf")
def action_plan_pdf(sid: str):
    rec = STORE.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    return _pdf_response(rec, build_action_plan_pdf, "90-Day-Action-Plan")


@app.get("/api/scorecard/{sid}/board-brief.pdf")
def board_brief_pdf(sid: str):
    rec = STORE.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    return _pdf_response(rec, build_board_brief_pdf, "Board-Brief")


# ---------------- static pages ----------------
def _page(name: str) -> HTMLResponse:
    f = WEB / name
    if f.exists():
        return HTMLResponse(f.read_text(encoding="utf-8"))
    return HTMLResponse(f"<h1>{name} not found</h1>", status_code=404)


@app.get("/", response_class=HTMLResponse)
def index():
    return _page("index.html")


@app.get("/review", response_class=HTMLResponse)
def review_page():
    return _page("review.html")
