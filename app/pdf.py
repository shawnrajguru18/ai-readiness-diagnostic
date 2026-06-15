"""Server-side PDF deliverable (Agent D1 render) using reportlab — pure-Python, no
system deps (works on Windows). Produces the one-page scorecard + quick-wins section.
"""
from __future__ import annotations
import io, math
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable, KeepTogether, PageBreak,
)

from .models import Scorecard, TIER_COLORS
from .content import questions_by_id

# Per-dimension guidance for the findings appendix (Companion 03 dimension detail).
DIMENSION_GUIDE = {
    "data_foundation": {
        "captures": "Whether data is integrated, current, accessible to AI, and trusted enough to build on.",
        "strong": "A unified, governed data layer where AI teams self-serve clean data through APIs and feature stores.",
        "actions": ["Prioritize the data domains behind your top use cases", "Stand up governance and clear ownership for those domains", "Expose curated, reusable datasets to AI teams"]},
    "governance_posture": {
        "captures": "Whether AI governance, risk ownership, and regulatory interpretation are operationalized, not just drafted.",
        "strong": "A mature framework with risk tiering, a clear AI risk owner, monitoring, and board oversight.",
        "actions": ["Name an accountable AI risk owner with a cross-functional committee", "Move from principles to operational review gates", "Operationalize industry AI guidance into controls"]},
    "ai_investment_maturity": {
        "captures": "How much AI has moved from pilots to production value, and the trajectory of investment.",
        "strong": "Multiple production AI applications with measurable, attributable business value and portfolio governance.",
        "actions": ["Define value pockets at scoping to lift production conversion", "Instrument outcomes so ROI is attributable", "Govern the initiative portfolio rather than funding ad hoc pilots"]},
    "org_change_readiness": {
        "captures": "Leadership alignment, change-management capacity, and workforce posture toward AI.",
        "strong": "Aligned leadership, strong change muscle, and a workforce helping shape AI adoption.",
        "actions": ["Align leadership on a single AI ambition and targets", "Invest change-management capacity ahead of scaling", "Engage the workforce as participants, not subjects"]},
    "value_pocket_clarity": {
        "captures": "Whether specific value pockets are identified, measured, and framed as reinvention rather than automation.",
        "strong": "An AI roadmap mapped to sized value pockets with baseline measurement and a reinvention-first frame.",
        "actions": ["Prioritize 2-3 processes with a real business case", "Set baseline and target outcomes per initiative", "Frame as process reinvention before automation"]},
    "regulatory_complexity": {
        "captures": "The regulatory and sovereignty constraints that shape which AI patterns are viable (informational).",
        "strong": "A proactive regulatory posture that turns constraint into a differentiator.",
        "actions": ["Classify in-flight and planned use cases by risk tier", "Close documentation, human-oversight, and monitoring gaps", "Track applicable frameworks (e.g. EU AI Act) on a horizon scan"]},
}

_ROOT = Path(__file__).resolve().parent.parent
_LOGO = _ROOT / "DXC Logo" / "Brand Mark" / "1 Color" / "RGB" / "DXC-1-Color-Dark.svg"


def _logo_flowable(width_pt: float = 84.0):
    """The DXC brand mark as a scaled reportlab Drawing, or None if unavailable."""
    try:
        from svglib.svglib import svg2rlg
        d = svg2rlg(str(_LOGO))
        if not d:
            return None
        s = width_pt / d.width
        d.scale(s, s)
        d.width, d.height = width_pt, d.height * s
        d.hAlign = "LEFT"
        return d
    except Exception:
        return None


MIDNIGHT = colors.HexColor("#0E1020")
INK = colors.HexColor("#3D3F50")
ROYAL = colors.HexColor("#004AAC")
LINE = colors.HexColor("#E6E1DA")


def _styles():
    ss = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=22,
                             textColor=MIDNIGHT, spaceAfter=2, alignment=0),
        "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold", fontSize=8, textColor=MIDNIGHT,
                                  spaceAfter=2, leading=10),
        "meta": ParagraphStyle("meta", fontName="Helvetica", fontSize=9, textColor=INK, leading=12),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=9, textColor=MIDNIGHT,
                             spaceAfter=6, leading=11),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, textColor=MIDNIGHT, leading=14),
        "finding": ParagraphStyle("finding", fontName="Helvetica", fontSize=10, textColor=MIDNIGHT,
                                  leading=14, spaceAfter=6, leftIndent=2),
        "rec": ParagraphStyle("rec", fontName="Helvetica", fontSize=10, textColor=MIDNIGHT, leading=14,
                              leftIndent=8, borderColor=ROYAL),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8, textColor=INK, leading=11),
    }


class Radar(Flowable):
    def __init__(self, dims, tier_color_hex, size=2.7 * inch):
        super().__init__()
        self.dims = dims
        self.color = colors.HexColor(tier_color_hex)
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        n = len(self.dims)
        cx = cy = self.size / 2
        R = self.size * 0.32
        def pt(i, frac):
            a = (2 * math.pi * i / n) - math.pi / 2
            return cx + R * frac * math.cos(a), cy + R * frac * math.sin(a)
        c.setStrokeColor(colors.HexColor("#D9D5CE"))
        c.setLineWidth(0.6)
        for t in (0.25, 0.5, 0.75, 1.0):
            pts = [pt(i, t) for i in range(n)]
            p = c.beginPath(); p.moveTo(*pts[0])
            for x, y in pts[1:]:
                p.lineTo(x, y)
            p.close(); c.drawPath(p)
        for i in range(n):
            x, y = pt(i, 1.0); c.line(cx, cy, x, y)
        you = [pt(i, d.score / 100) for i, d in enumerate(self.dims)]
        p = c.beginPath(); p.moveTo(*you[0])
        for x, y in you[1:]:
            p.lineTo(x, y)
        p.close()
        fill = colors.Color(self.color.red, self.color.green, self.color.blue, alpha=0.33)
        c.setFillColor(fill); c.setStrokeColor(self.color); c.setLineWidth(1.6)
        c.drawPath(p, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 7); c.setFillColor(MIDNIGHT)
        for i, d in enumerate(self.dims):
            lx, ly = pt(i, 1.14)
            c.drawCentredString(lx, ly, d.label.split(" & ")[0][:18])
            vx, vy = pt(i, d.score / 100)
            c.drawCentredString(vx, vy + 3, str(d.score))


class PeerBar(Flowable):
    """A 0-100 track with the prospect's score filled in tier color and a dark
    tick marking the peer average — the 'you vs peer' bar."""
    def __init__(self, score: int, peer, tier_hex: str, width: float = 2.6 * inch):
        super().__init__()
        self.score = score
        self.peer = peer
        self.color = colors.HexColor(tier_hex)
        self.width = width
        self.height = 7

    def draw(self):
        c = self.canv
        w, h = self.width, 5
        c.setFillColor(colors.HexColor("#ECE7E0")); c.roundRect(0, 0, w, h, 2, fill=1, stroke=0)
        c.setFillColor(self.color); c.roundRect(0, 0, max(2, w * self.score / 100), h, 2, fill=1, stroke=0)
        if self.peer is not None:
            px = w * self.peer / 100
            c.setStrokeColor(MIDNIGHT); c.setLineWidth(1.2); c.line(px, -1.5, px, h + 1.5)


def build_scorecard_pdf(sc: Scorecard) -> bytes:
    S = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            title=f"AI Readiness Scorecard — {sc.company_name}")
    story = []

    # Header
    logo = _logo_flowable()
    if logo is not None:
        story.append(logo)
        story.append(Spacer(1, 6))
    story.append(Paragraph("AI READINESS DIAGNOSTIC · DXC ADVISORYX", S["eyebrow"]))
    story.append(Paragraph(sc.company_name, S["h1"]))
    story.append(Paragraph(f"{sc.industry_label} &nbsp;·&nbsp; {sc.assessment_date} &nbsp;·&nbsp; "
                           f"Reviewed by {sc.reviewed_by}", S["meta"]))
    story.append(Spacer(1, 8))
    _graded = [d for d in sc.dimensions if not d.informational]
    if _graded:
        _st = max(_graded, key=lambda d: d.score); _wk = min(_graded, key=lambda d: d.score)
        story.append(Paragraph(
            f"<b>{sc.company_name}</b> is at the <b>{sc.overall_tier}</b> stage of AI readiness, scoring "
            f"{sc.overall_score} of 100. Strongest: {_st.label}. Priority gap: {_wk.label}.", S["body"]))
        story.append(Spacer(1, 10))

    # Radar + overall + dimension table (two columns)
    tier_hex = TIER_COLORS.get(sc.overall_tier, "#FFAE41")
    radar = Radar(sc.dimensions, tier_hex)
    dim_rows = [[Paragraph(f"<b>{sc.overall_score}</b> &nbsp; <font color='#3D3F50'>{sc.overall_tier}</font>",
                           ParagraphStyle("ov", fontName="Helvetica", fontSize=15, textColor=MIDNIGHT))]]
    dim_rows.append([Paragraph(sc.peer_reference + "  &nbsp;|&nbsp; <font color='#0E1020'>|</font> peer average",
                               S["small"])])
    for d in sc.dimensions:
        peer = sc.peer_benchmarks.get(d.dimension)
        delta = ""
        if peer is not None and not d.informational:
            diff = d.score - peer
            sign = "+" if diff > 0 else ""
            col = "#1f9d55" if diff > 0 else ("#8A867E" if diff == 0 else "#c0392b")
            delta = f" &nbsp; vs peer {peer} <font color='{col}'>({sign}{diff})</font>"
        label = Paragraph(f"<b>{d.label}</b> {'<font size=7 color=\"#8A867E\">informational</font>' if d.informational else ''}<br/>"
                          f"<font size=8 color='#3D3F50'>{d.score} · {d.tier}{delta}</font>", S["small"])
        dim_rows.append([label]); dim_rows.append([PeerBar(d.score, peer, TIER_COLORS[d.tier])])
    right = Table(dim_rows, colWidths=[3.0 * inch])
    right.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    grid = Table([[radar, right]], colWidths=[3.0 * inch, 3.1 * inch])
    grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 8),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(grid)
    story.append(Spacer(1, 12))

    # Findings
    story.append(Paragraph("WHAT WE FOUND", S["h2"]))
    for i, f in enumerate(sc.findings, 1):
        story.append(Paragraph(f"<b>{i}. {f.headline}.</b> {f.body}", S["finding"]))
    story.append(Spacer(1, 6))

    # Recommended next step
    r = sc.recommended_next_step
    rec_tbl = Table([[Paragraph("<b>RECOMMENDED NEXT STEP</b>", ParagraphStyle("rh", fontName="Helvetica-Bold",
                      fontSize=9, textColor=ROYAL))],
                     [Paragraph(r.body, S["body"])],
                     [Paragraph(f"Duration: {r.duration_estimate_weeks}. Continue the conversation: "
                                f"{r.contact_name} | {r.contact_email}", S["small"])]],
                    colWidths=[6.6 * inch])
    rec_tbl.setStyle(TableStyle([("LINEBEFORE", (0, 0), (0, -1), 3, ROYAL), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                                 ("TOPPADDING", (0, 0), (-1, -1), 3), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFF"))]))
    story.append(KeepTogether(rec_tbl))
    story.append(Spacer(1, 12))

    # Quick wins
    story.append(Paragraph("90-DAY QUICK WINS", S["h2"]))
    for q in sc.quick_wins:
        story.append(Paragraph(f"<b>{q.pattern_name}</b> — {q.one_line_description} "
                               f"<font color='#8A867E'>({q.timeline_to_value}, {q.implementation_effort} effort)</font>",
                               S["finding"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Confidential — prepared for {sc.company_name}. Prepared by DXC AdvisoryX.", S["small"]))

    doc.build(story)
    return buf.getvalue()


def _slug(name: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", (name or "subject").lower()).strip("-") or "subject"


def save_scorecard_pdf(sc: Scorecard, out_dir: str = "outputs") -> str:
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    path = d / f"scorecard-{_slug(sc.company_name)}.pdf"
    path.write_bytes(build_scorecard_pdf(sc))
    return str(path)


# ============================================================
# Value-difficulty 2x2 (light) — used in the appendix
# ============================================================
class VDChart(Flowable):
    def __init__(self, items, size=3.3 * inch):
        super().__init__()
        self.items = items
        self.size = size
        self.width = size + 0.8 * inch
        self.height = size + 0.6 * inch

    def draw(self):
        c = self.canv
        s = self.size
        ox, oy = 0.55 * inch, 0.4 * inch
        # priority quadrant tint (upper-left: high value, low difficulty)
        c.setFillColor(colors.HexColor("#EAF2FF"))
        c.rect(ox, oy + s / 2, s / 2, s / 2, fill=1, stroke=0)
        # frame + midlines
        c.setStrokeColor(colors.HexColor("#C9C4BC")); c.setLineWidth(0.8); c.rect(ox, oy, s, s)
        c.setStrokeColor(colors.HexColor("#E6E1DA"))
        c.line(ox + s / 2, oy, ox + s / 2, oy + s); c.line(ox, oy + s / 2, ox + s, oy + s / 2)
        # quadrant labels
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(ROYAL); c.drawString(ox + 4, oy + s - 10, "QUICK WINS")
        c.setFillColor(colors.HexColor("#8A867E")); c.drawRightString(ox + s - 4, oy + s - 10, "STRATEGIC BETS")
        c.setFillColor(colors.HexColor("#B7B1A8"))
        c.drawString(ox + 4, oy + 5, "FILL-INS"); c.drawRightString(ox + s - 4, oy + 5, "DEPRIORITIZE")
        # axis labels
        c.setFont("Helvetica", 7); c.setFillColor(INK)
        c.drawCentredString(ox + s / 2, oy - 12, "Implementation difficulty →")
        c.saveState(); c.translate(ox - 14, oy + s / 2); c.rotate(90)
        c.drawCentredString(0, 0, "Business value →"); c.restoreState()
        # spread overlapping points in a small ring
        import math as _m
        counts, idx = {}, {}
        for it in self.items:
            key = (round(it.difficulty_score * 10), round(it.value_score * 10))
            counts[key] = counts.get(key, 0) + 1
        for i, it in enumerate(self.items, 1):
            key = (round(it.difficulty_score * 10), round(it.value_score * 10))
            k = idx.get(key, 0); idx[key] = k + 1; m = counts[key]
            dx = dy = 0.0
            if m > 1:
                a = 2 * _m.pi * k / m; dx = _m.cos(a) * 0.055; dy = _m.sin(a) * 0.055
            vx = min(0.93, max(0.07, it.difficulty_score + dx))
            vy = min(0.93, max(0.07, it.value_score + dy))
            px, py = ox + vx * s, oy + vy * s
            c.setFillColor(ROYAL); c.circle(px, py, 7.5, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 8); c.setFillColor(colors.white)
            c.drawCentredString(px, py - 3, str(i))


# ============================================================
# Quick-wins memo (secondary deliverable, 1 page)
# ============================================================
def build_quickwins_memo_pdf(sc: Scorecard) -> bytes:
    S = _styles(); buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            title=f"90-Day Quick Wins — {sc.company_name}")
    ct = ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=12, textColor=MIDNIGHT)
    story = []
    logo = _logo_flowable()
    if logo is not None:
        story += [logo, Spacer(1, 6)]
    story.append(Paragraph(f"90-DAY QUICK WINS · {sc.company_name.upper()}", S["eyebrow"]))
    story.append(Paragraph("90-Day Quick Wins", S["h1"]))
    story.append(Paragraph(f"{sc.industry_label} &nbsp;·&nbsp; {sc.assessment_date}", S["meta"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Quick wins are AI patterns you can put in production in 90 days or less. Each has documented "
        "enterprise deployments with measurable results. They build momentum and prove execution "
        "capacity while the strategic roadmap takes shape through Discovery.", S["body"]))
    story.append(Spacer(1, 10))
    for q in sc.quick_wins:
        rows = [
            [Paragraph(q.pattern_name, ct)],
            [Paragraph(f"<i>{q.one_line_description}</i>", S["small"])],
            [Paragraph(f"<b>What this would do for {sc.company_name}:</b> {q.what_this_would_do}", S["body"])],
            [Paragraph("<b>Prerequisites you have:</b> " + ("  ".join("✓ " + p for p in q.prerequisites_you_have) or "(to confirm)"), S["small"])],
            [Paragraph(f"<b>Expected outcome:</b> {q.expected_outcome_range}", S["small"])],
            [Paragraph(f"<b>Timeline to value:</b> {q.timeline_to_value} &nbsp;&nbsp; <b>Effort:</b> {q.implementation_effort}", S["small"])],
        ]
        card = Table(rows, colWidths=[6.6 * inch])
        card.setStyle(TableStyle([("LINEBEFORE", (0, 0), (0, -1), 3, ROYAL),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 10),
                                  ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        story.append(KeepTogether(card)); story.append(Spacer(1, 12))
    r = sc.recommended_next_step
    story.append(Paragraph(f"Continue the conversation: {r.contact_name} | {r.contact_email}", S["small"]))
    doc.build(story)
    return buf.getvalue()


def save_quickwins_memo_pdf(sc: Scorecard, out_dir: str = "outputs") -> str:
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    path = d / f"quick-wins-{_slug(sc.company_name)}.pdf"
    path.write_bytes(build_quickwins_memo_pdf(sc))
    return str(path)


# ============================================================
# 90-Day Action Plan (1 page) — phased 30/60/90 sequencing
# ============================================================
def _phase_buckets(quick_wins):
    """Distribute quick wins across the three 30-day phases, fastest/lowest-effort first."""
    order = {"Low": 0, "Medium": 1, "High": 2}
    qs = sorted(quick_wins, key=lambda q: (q.ordering_priority, order.get(q.implementation_effort, 1)))
    buckets = ([], [], [])
    per = max(1, -(-len(qs) // 3))   # ceil(n/3) per contiguous group
    for i, q in enumerate(qs):
        buckets[min(2, i // per)].append(q)
    return buckets


def build_action_plan_pdf(sc: Scorecard) -> bytes:
    S = _styles(); buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            title=f"90-Day Action Plan — {sc.company_name}")
    story = []
    logo = _logo_flowable()
    if logo is not None:
        story += [logo, Spacer(1, 6)]
    story.append(Paragraph(f"90-DAY ACTION PLAN · {sc.company_name.upper()}", S["eyebrow"]))
    story.append(Paragraph("Your First 90 Days", S["h1"]))
    story.append(Paragraph(f"{sc.industry_label} &nbsp;·&nbsp; {sc.assessment_date} &nbsp;·&nbsp; "
                           f"Reviewed by {sc.reviewed_by}", S["meta"]))
    story.append(Spacer(1, 8))
    graded = [d for d in sc.dimensions if not d.informational]
    weakest = min(graded, key=lambda d: d.score) if graded else None
    story.append(Paragraph(
        "A pragmatic sequence to build momentum, prove execution capacity, and tee up the "
        "strategic roadmap — without waiting on a long program. Each phase is 30 days.", S["body"]))
    story.append(Spacer(1, 12))

    buckets = _phase_buckets(sc.quick_wins)
    phases = [
        ("DAYS 1–30", "Mobilize & prove", "Exec sponsor + delivery lead",
         "Name an accountable exec sponsor and a delivery lead. Confirm data and access "
         "prerequisites. Launch the first quick win.", buckets[0],
         "First win in flight; baseline metrics captured"),
        ("DAYS 31–60", "Expand & instrument", "Delivery lead + process owners",
         "Roll out the next pattern(s). Instrument outcomes so value is attributable, not anecdotal.",
         buckets[1], "Two-plus patterns live; outcome dashboard in place"),
        ("DAYS 61–90", "Scale & tee up Discovery", "Sponsor + DXC AdvisoryX",
         "Harden what works, measure realized value, and assemble the board-ready case for the "
         + (f"recommended next step — addressing the {weakest.label.lower()} gap." if weakest
            else "recommended next step."),
         buckets[2], "Value quantified; Discovery scoped and approved"),
    ]
    blue = ParagraphStyle("blue", parent=S["h2"], textColor=ROYAL, fontSize=10)
    for tf, focus, owner, desc, qs, outcome in phases:
        rows = [
            [Paragraph(f"{tf} &nbsp; <font color='#0E1020'>· {focus}</font>", blue)],
            [Paragraph(desc, S["body"])],
        ]
        if qs:
            rows.append([Paragraph("<b>Initiatives:</b> " + "; ".join(
                f"{q.pattern_name} <font color='#8A867E'>({q.timeline_to_value}, {q.implementation_effort} effort)</font>"
                for q in qs), S["small"])])
        rows.append([Paragraph(f"<b>Owner:</b> {owner} &nbsp;&nbsp; <b>Milestone:</b> {outcome}", S["small"])])
        card = Table(rows, colWidths=[6.6 * inch])
        card.setStyle(TableStyle([("LINEBEFORE", (0, 0), (0, -1), 3, ROYAL),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 10),
                                  ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                  ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFF"))]))
        story.append(KeepTogether(card)); story.append(Spacer(1, 12))

    r = sc.recommended_next_step
    story.append(Paragraph(f"After 90 days: {r.body}", S["small"]))
    story.append(Paragraph(f"Continue the conversation: {r.contact_name} | {r.contact_email}", S["small"]))
    doc.build(story)
    return buf.getvalue()


def save_action_plan_pdf(sc: Scorecard, out_dir: str = "outputs") -> str:
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    path = d / f"action-plan-{_slug(sc.company_name)}.pdf"
    path.write_bytes(build_action_plan_pdf(sc))
    return str(path)


# ============================================================
# Board Brief (1 page) — top-of-house summary for the board
# ============================================================
def build_board_brief_pdf(sc: Scorecard) -> bytes:
    S = _styles(); buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            title=f"Board Brief — {sc.company_name}")
    story = []
    logo = _logo_flowable()
    if logo is not None:
        story += [logo, Spacer(1, 6)]
    story.append(Paragraph("AI READINESS · BOARD BRIEF", S["eyebrow"]))
    story.append(Paragraph(sc.company_name, S["h1"]))
    story.append(Paragraph(f"{sc.industry_label} &nbsp;·&nbsp; {sc.assessment_date} &nbsp;·&nbsp; "
                           f"Reviewed by {sc.reviewed_by}", S["meta"]))
    story.append(Spacer(1, 12))

    graded = [d for d in sc.dimensions if not d.informational]
    strongest = max(graded, key=lambda d: d.score) if graded else None
    weakest = min(graded, key=lambda d: d.score) if graded else None
    peer_o = None
    if sc.peer_benchmarks and graded:
        # weighted-ish peer overall: simple average of graded peer benchmarks for the headline
        gp = [sc.peer_benchmarks[d.dimension] for d in graded if d.dimension in sc.peer_benchmarks]
        peer_o = round(sum(gp) / len(gp)) if gp else None

    # Headline band: tier + score vs peer
    pos = ""
    if peer_o is not None:
        diff = sc.overall_score - peer_o
        pos = (f" — {abs(diff)} points {'ahead of' if diff > 0 else 'behind' if diff < 0 else 'in line with'} "
               f"the peer benchmark")
    nar = sc.executive_narrative
    band_right = (nar.headline if nar and nar.headline else
                  f"{sc.company_name} is at the {sc.overall_tier} stage of AI readiness{pos}. "
                  + (f"Strongest: {strongest.label}. Priority gap: {weakest.label}." if strongest and weakest else ""))
    band = Table([[
        Paragraph(f"<font size=26><b>{sc.overall_score}</b></font><font size=12 color='#3D3F50'>/100</font><br/>"
                  f"<font size=11 color='#004AAC'><b>{sc.overall_tier}</b> stage of AI readiness</font>",
                  ParagraphStyle("bandl", fontName="Helvetica", textColor=MIDNIGHT, leading=20)),
        Paragraph(band_right, S["body"]),
    ]], colWidths=[1.9 * inch, 4.7 * inch])
    band.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                              ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F7FAFF")),
                              ("LINEAFTER", (0, 0), (0, 0), 3, ROYAL), ("LEFTPADDING", (0, 0), (-1, -1), 12),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 10),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    story.append(band)
    story.append(Spacer(1, 14))

    # Executive summary (C4 narrative, persona-framed)
    if nar and nar.paragraphs:
        story.append(Paragraph("EXECUTIVE SUMMARY", S["h2"]))
        for t in nar.paragraphs:
            story.append(Paragraph(t, S["body"]))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 6))

    # What matters most (top findings, decision-relevance first)
    story.append(Paragraph("WHAT MATTERS MOST", S["h2"]))
    rank = {"high": 0, "medium": 1, "low": 2}
    top = sorted(sc.findings, key=lambda f: rank.get(f.decision_relevance, 1))[:3]
    for i, f in enumerate(top, 1):
        story.append(Paragraph(f"<b>{i}. {f.headline}.</b> {f.body}", S["finding"]))
    story.append(Spacer(1, 8))

    # The ask
    r = sc.recommended_next_step
    ask = Table([[Paragraph("<b>THE ASK</b>", ParagraphStyle("ask", fontName="Helvetica-Bold", fontSize=9,
                  textColor=ROYAL))],
                 [Paragraph(r.body, S["body"])],
                 [Paragraph(f"Duration: {r.duration_estimate_weeks}. Continue the conversation: "
                            f"{r.contact_name} | {r.contact_email}", S["small"])]],
                colWidths=[6.6 * inch])
    ask.setStyle(TableStyle([("LINEBEFORE", (0, 0), (0, -1), 3, ROYAL), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFF"))]))
    story.append(KeepTogether(ask))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Confidential — prepared for the board of {sc.company_name}. Prepared by DXC AdvisoryX.", S["small"]))
    doc.build(story)
    return buf.getvalue()


def save_board_brief_pdf(sc: Scorecard, out_dir: str = "outputs") -> str:
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    path = d / f"board-brief-{_slug(sc.company_name)}.pdf"
    path.write_bytes(build_board_brief_pdf(sc))
    return str(path)


# ============================================================
# Findings appendix (tertiary deliverable, 5-8 pages)
# ============================================================
def _questionnaire_signals(session, dim: str) -> list[str]:
    qmap = questions_by_id()
    out = []
    for resp in session.responses:
        q = qmap.get(resp.question_id)
        if not q or q["dimension"] != dim:
            continue
        chosen = "(no answer)"
        t = q["type"]
        if t == "single_select" and resp.option_id:
            o = next((o for o in q["options"] if o["id"] == resp.option_id), None)
            if o:
                if "score" in o:
                    chosen = f"{o['text']} (score {o['score']})"
                elif "complexity" in o:
                    chosen = f"{o['text']} (complexity {o['complexity']})"
                else:
                    chosen = o["text"]
        elif t == "scale_1_5" and resp.scale_value is not None:
            a = next((a for a in q["scale_anchors"] if a["value"] == resp.scale_value), None)
            if a:
                chosen = f"{a['text']} (score {a['score']})"
        elif t == "multi_select":
            chosen = "; ".join(o["text"] for o in q["options"] if o["id"] in (resp.option_ids or [])) or "(none)"
        elif t == "open_short":
            chosen = resp.text or "(no answer)"
        out.append(f"{resp.question_id}: {q['text']} &rarr; {chosen}")
    return out or ["(no questions recorded for this dimension)"]


def _research_text(research) -> str:
    try:
        from .research import research_summary
        return research_summary(research or {})
    except Exception:
        return "No external research signals available."


def build_appendix_pdf(session) -> bytes:
    sc: Scorecard = session.scorecard
    S = _styles(); buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            title=f"Findings Appendix — {sc.company_name}")
    story = []
    logo = _logo_flowable()
    if logo is not None:
        story += [logo, Spacer(1, 6)]
    story.append(Paragraph("FINDINGS APPENDIX · DXC ADVISORYX", S["eyebrow"]))
    story.append(Paragraph(sc.company_name, S["h1"]))
    story.append(Paragraph(f"{sc.industry_label} &nbsp;·&nbsp; {sc.assessment_date} &nbsp;·&nbsp; "
                           f"Reviewed by {sc.reviewed_by}", S["meta"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("CONTENTS", S["h2"]))
    story.append(Paragraph("Methodology · Opportunity map (value vs difficulty) · Dimension-by-dimension "
                           "detail (six) · Sources and acknowledgments", S["small"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("METHODOLOGY", S["h2"]))
    story.append(Paragraph(
        "This assessment scores six AI-readiness dimensions on a 0-100 scale from a structured "
        "questionnaire, weighting each question by its diagnostic value. Tiers are Emerging (0-39), "
        "Developing (40-59), Established (60-79), Leading (80-100). Where available, public research "
        "signals adjust the questionnaire-derived score. Regulatory Complexity is informational and "
        "indicates constraint, not opportunity. A DXC senior partner reviews and approves the output "
        "before delivery.", S["body"]))
    story.append(Spacer(1, 10))

    if sc.value_difficulty:
        story.append(Paragraph("OPPORTUNITY MAP — VALUE vs DIFFICULTY", S["h2"]))
        story.append(Paragraph("Where each opportunity sits by business value and effort to implement. "
                               "Start upper-left (high value, low difficulty).", S["small"]))
        story.append(Spacer(1, 4))
        story.append(VDChart(sc.value_difficulty))
        story.append(Spacer(1, 4))
        _ql = {"high_value_low_difficulty": "quick win", "high_value_high_difficulty": "strategic bet",
               "low_value_low_difficulty": "fill-in", "low_value_high_difficulty": "deprioritize"}
        for i, it in enumerate(sc.value_difficulty, 1):
            story.append(Paragraph(f"<b>{i}.</b> {it.opportunity} — {_ql.get(it.quadrant, '')}", S["small"]))
        story.append(Spacer(1, 6))

    for d in sc.dimensions:
        g = DIMENSION_GUIDE.get(d.dimension, {})
        story.append(PageBreak())
        story.append(Paragraph(f"{d.label.upper()} — {d.score}/100 · {d.tier}"
                               + (" · informational" if d.informational else ""), S["h2"]))
        story.append(Paragraph(f"<b>What this captures.</b> {g.get('captures','')}", S["body"]))
        story.append(Paragraph(f"<b>Your score.</b> {d.reasoning}", S["body"]))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Questionnaire signals.</b>", S["body"]))
        for s in _questionnaire_signals(session, d.dimension):
            story.append(Paragraph("&bull; " + s, S["small"]))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Research signals.</b> {_research_text(session.research)}", S["small"]))
        peer = sc.peer_benchmarks.get(d.dimension)
        if peer is None:
            peer_txt = "Peer benchmark not available for this cohort."
        else:
            diff = d.score - peer
            rel = ("ahead of" if diff > 0 else "behind" if diff < 0 else "in line with")
            peer_txt = (f"Your score is {d.score} vs a peer average of {peer} — "
                        f"{abs(diff)} point(s) {rel} the cohort." if diff
                        else f"Your score is {d.score}, {rel} the peer average of {peer}.")
        story.append(Paragraph(f"<b>Peer comparison.</b> {peer_txt} <font color='#8A867E'>({sc.peer_reference})</font>", S["small"]))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>What strong looks like.</b> {g.get('strong','')}", S["body"]))
        if g.get("actions"):
            story.append(Paragraph("<b>Actions to improve.</b>", S["body"]))
            for a in g["actions"]:
                story.append(Paragraph("&bull; " + a, S["small"]))

    story.append(PageBreak())
    story.append(Paragraph("SOURCES & ACKNOWLEDGMENTS", S["h2"]))
    story.append(Paragraph(
        "Inputs: the prospect's self-reported questionnaire responses, and public research (SEC EDGAR "
        "filings and news) where available. This appendix is generated automatically and reviewed by a "
        f"DXC senior partner before delivery. Confidential — prepared for {sc.company_name}.", S["small"]))
    doc.build(story)
    return buf.getvalue()


def save_appendix_pdf(session, out_dir: str = "outputs") -> str:
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    path = d / f"appendix-{_slug(session.scorecard.company_name)}.pdf"
    path.write_bytes(build_appendix_pdf(session))
    return str(path)
