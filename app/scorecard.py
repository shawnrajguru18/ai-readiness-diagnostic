"""Server-side scorecard render (Companion 03 + DXC brand). Produces HTML; PDF via
weasyprint if installed. The React app (web/) is the primary interactive view; this is
the deliverable/PDF path (Agent D1 output)."""
from __future__ import annotations
import math, re
from pathlib import Path
from .models import Scorecard, TIER_COLORS

CANVAS = "#F6F3F0"; MIDNIGHT = "#0E1020"; INK = "#3D3F50"; ROYAL = "#004AAC"; GOLD = "#FFAE41"

# Official DXC brand mark (from DXC Logo/Brand Mark), midnight for the canvas page.
_DXC_PATH = ("M220.055 60.7583C252.905 60.7583 279.643 87.4387 279.644 120.247C279.644 153.055 252.905 179.735 220.055 179.735H61V155.455H220.055C239.522 155.455 255.362 139.657 255.362 120.247C255.362 100.836 239.522 85.0396 220.055 85.0396H61V60.7583H220.055ZM798 85.0386H638.945C619.478 85.0386 603.638 100.836 603.638 120.247C603.638 139.657 619.478 155.454 638.945 155.454H798V179.735H638.945C606.08 179.735 579.357 153.054 579.356 120.247C579.356 87.4387 606.095 60.7573 638.945 60.7573H798V85.0386ZM556.104 85.0386C530.11 85.0387 511.856 96.5366 492.531 108.706C486.261 112.662 479.906 116.647 473.278 120.204C479.905 123.76 486.261 127.744 492.531 131.701C511.856 143.87 530.11 155.368 556.104 155.368V179.649C523.097 179.649 499.987 165.095 479.591 152.254C462.637 141.585 447.997 132.358 430.058 132.358C412.118 132.358 397.478 141.571 380.524 152.254C360.128 165.095 337.018 179.649 304.011 179.649V155.368C330.006 155.368 348.259 143.87 367.584 131.701C373.854 127.744 380.211 123.76 386.838 120.204C380.211 116.647 373.854 112.662 367.584 108.706C348.259 96.5366 330.006 85.0386 304.011 85.0386V60.7573C337.018 60.7573 360.128 75.3119 380.524 88.1665C397.478 98.8358 412.118 108.063 430.058 108.063V108.048C447.997 108.048 462.637 98.8364 479.591 88.1528C499.987 75.3125 523.097 60.7575 556.104 60.7573V85.0386Z")
DXC_LOGO = f'<svg viewBox="0 0 860 240" height="22" style="display:block"><path d="{_DXC_PATH}" fill="{MIDNIGHT}"/></svg>'


def _radar(sc: Scorecard, size=360) -> str:
    dims = [d for d in sc.dimensions]
    n = len(dims); cx = cy = size / 2; R = size * 0.34
    if n < 3:
        return ""
    def pt(i, frac):
        ang = (2 * math.pi * i / n) - math.pi / 2
        return cx + R * frac * math.cos(ang), cy + R * frac * math.sin(ang)
    grid = "".join(
        f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in (pt(i,t) for i in range(n)))}" '
        f'fill="none" stroke="#D9D5CE"/>' for t in (0.25, 0.5, 0.75, 1.0)
    )
    you = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, d.score / 100) for i, d in enumerate(dims)))
    color = TIER_COLORS[sc.overall_tier]
    labels = ""
    for i, d in enumerate(dims):
        lx, ly = pt(i, 1.16)
        anchor = "middle" if abs(lx - cx) < 14 else ("start" if lx > cx else "end")
        labels += (f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="10" fill="{MIDNIGHT}" '
                   f'text-anchor="{anchor}" dominant-baseline="middle">{d.label.split(" & ")[0]}</text>')
        vx, vy = pt(i, d.score / 100)
        labels += (f'<text x="{vx:.0f}" y="{vy:.0f}" font-size="10" font-weight="700" fill="{MIDNIGHT}" '
                   f'text-anchor="middle" dy="-4">{d.score}</text>')
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">{grid}'
            f'<polygon points="{you}" fill="{color}55" stroke="{color}" stroke-width="2"/>{labels}</svg>')


_QL = {"high_value_low_difficulty": "quick win", "high_value_high_difficulty": "strategic bet",
       "low_value_low_difficulty": "fill-in", "low_value_high_difficulty": "deprioritize"}


def _vd_svg(sc: Scorecard, size: int = 300):
    """Numbered value-difficulty 2x2 + legend html, matching the React/PDF version."""
    items = sc.value_difficulty
    if not items:
        return "", ""
    pad = 56
    s = size
    counts, idx, pts = {}, {}, []
    for it in items:
        key = (round(it.difficulty_score * 10), round(it.value_score * 10))
        counts[key] = counts.get(key, 0) + 1
    for i, it in enumerate(items, 1):
        key = (round(it.difficulty_score * 10), round(it.value_score * 10))
        k = idx.get(key, 0); idx[key] = k + 1; m = counts[key]
        dx = dy = 0.0
        if m > 1:
            a = 2 * math.pi * k / m; dx = math.cos(a) * 0.055; dy = math.sin(a) * 0.055
        vx = min(0.92, max(0.08, it.difficulty_score + dx))
        vy = min(0.92, max(0.08, it.value_score + dy))
        pts.append((i, it, pad + vx * s, pad + (1 - vy) * s))
    dots = "".join(
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="12" fill="{ROYAL}"/>'
        f'<text x="{x:.0f}" y="{y + 4:.0f}" font-size="12" font-weight="700" fill="#fff" text-anchor="middle">{i}</text>'
        for i, it, x, y in pts)
    svg = (
        f'<svg width="{s + pad + 16}" height="{s + pad + 30}" viewBox="0 0 {s + pad + 16} {s + pad + 30}">'
        f'<rect x="{pad}" y="{pad}" width="{s // 2}" height="{s // 2}" fill="#EAF2FF"/>'
        f'<rect x="{pad}" y="{pad}" width="{s}" height="{s}" fill="none" stroke="#C9C4BC"/>'
        f'<line x1="{pad + s // 2}" y1="{pad}" x2="{pad + s // 2}" y2="{pad + s}" stroke="#E6E1DA"/>'
        f'<line x1="{pad}" y1="{pad + s // 2}" x2="{pad + s}" y2="{pad + s // 2}" stroke="#E6E1DA"/>'
        f'<text x="{pad + 6}" y="{pad + 15}" font-size="10" font-weight="700" fill="{ROYAL}">QUICK WINS</text>'
        f'<text x="{pad + s - 6}" y="{pad + 15}" font-size="10" font-weight="700" fill="#8A867E" text-anchor="end">STRATEGIC BETS</text>'
        f'<text x="{pad + 6}" y="{pad + s - 6}" font-size="10" fill="#B7B1A8">FILL-INS</text>'
        f'<text x="{pad + s - 6}" y="{pad + s - 6}" font-size="10" fill="#B7B1A8" text-anchor="end">DEPRIORITIZE</text>'
        f'<text x="{pad + s // 2}" y="{pad + s + 22}" font-size="11" fill="{INK}" text-anchor="middle">Implementation difficulty &#8594;</text>'
        f'<text x="20" y="{pad + s // 2}" font-size="11" fill="{INK}" text-anchor="middle" transform="rotate(-90 20 {pad + s // 2})">Business value &#8594;</text>'
        f'{dots}</svg>')
    legend = "".join(
        f'<li><b>{i}.</b> {it.opportunity} <span class="muted">&middot; {_QL.get(it.quadrant, "")}</span></li>'
        for i, it, x, y in pts)
    return svg, f'<ol class="vdlegend">{legend}</ol>'


def render_scorecard_html(sc: Scorecard) -> str:
    graded = [d for d in sc.dimensions if not d.informational]
    strongest = max(graded, key=lambda d: d.score) if graded else None
    weakest = min(graded, key=lambda d: d.score) if graded else None
    summary = (f"{sc.company_name} is at the {sc.overall_tier} stage of AI readiness, scoring "
               f"{sc.overall_score} of 100."
               + (f" The strongest dimension is {strongest.label}; the priority gap is {weakest.label}."
                  if strongest and weakest else ""))
    vd_svg, vd_legend = _vd_svg(sc)

    def _bar(d):
        peer = sc.peer_benchmarks.get(d.dimension)
        tick = (f'<span style="position:absolute;left:{peer}%;top:-3px;bottom:-3px;width:2px;'
                f'background:{MIDNIGHT};border-radius:1px" title="peer average {peer}"></span>'
                if peer is not None else "")
        delta = ""
        if peer is not None and not d.informational:
            diff = d.score - peer
            col = "#1f9d55" if diff > 0 else ("#8A867E" if diff == 0 else "#c0392b")
            delta = (f'<span style="color:{col};font-weight:700"> vs peer {peer} '
                     f'({"+" if diff>0 else ""}{diff})</span>')
        return (
            f'<div style="margin-bottom:13px">'
            f'<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">'
            f'<span style="font-weight:600;color:{MIDNIGHT}">{d.label}'
            f'{" · informational" if d.informational else ""}</span>'
            f'<span style="color:{MIDNIGHT}"><b>{d.score}</b> · {d.tier}{delta}</span></div>'
            f'<div style="position:relative;height:8px;background:#ECE7E0;border-radius:4px">'
            f'<div style="width:{d.score}%;height:100%;background:{TIER_COLORS[d.tier]};border-radius:4px"></div>'
            f'{tick}</div></div>')
    bars = "".join(_bar(d) for d in sc.dimensions)
    findings = "".join(
        f'<li><b>{f.headline}.</b> {f.body}</li>' for f in sc.findings
    )
    qwins = "".join(
        f'<div class="qw"><b>{q.pattern_name}</b> — {q.one_line_description} '
        f'<span class="muted">({q.timeline_to_value})</span></div>' for q in sc.quick_wins
    )
    r = sc.recommended_next_step
    nar = sc.executive_narrative
    nar_panel = ""
    if nar and nar.paragraphs:
        nar_head = (f'<p style="font-family:\'Playfair Display\',Georgia,serif;color:{MIDNIGHT};'
                    f'font-size:22px;line-height:1.25;margin:0 0 14px">{nar.headline}</p>' if nar.headline else "")
        nar_body = "".join(f'<p style="margin:0 0 12px;font-size:15px;color:{MIDNIGHT};line-height:1.6">{t}</p>'
                           for t in nar.paragraphs)
        nar_panel = f'<div class="panel"><h2>Executive summary</h2>{nar_head}{nar_body}</div>'
    vd_panel = (f'<div class="panel"><h2>Opportunity map &middot; value vs difficulty</h2>'
                f'<p class="muted" style="margin:-6px 0 14px">Where each opportunity sits by business value and effort to implement.</p>'
                f'<div class="vd">{vd_svg}{vd_legend}</div></div>') if vd_svg else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>AI Readiness Scorecard — {sc.company_name}</title>
<style>
  body{{font-family:'DM Sans',Arial,sans-serif;background:{CANVAS};color:{INK};margin:0}}
  .wrap{{max-width:920px;margin:0 auto;padding:40px}}
  .eyebrow{{letter-spacing:2px;text-transform:uppercase;font-size:11px;font-weight:700}}
  h1{{font-family:'Playfair Display',Georgia,serif;color:{MIDNIGHT};font-size:40px;margin:6px 0 0;line-height:1}}
  .meta{{font-size:13px;color:{INK}}}
  .cover{{background:#fff;border:1px solid #E6E1DA;border-top:4px solid {ROYAL};border-radius:16px;padding:28px;display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap}}
  .reviewed{{font-size:13px;color:{MIDNIGHT};margin-top:8px}} .reviewed b{{color:{MIDNIGHT}}}
  .overall{{font-family:'Playfair Display',Georgia,serif;font-size:60px;color:{MIDNIGHT};line-height:1}}
  .overall span{{font-family:'DM Sans',Arial,sans-serif;font-size:20px;color:{INK}}}
  .tierbadge{{display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:13px;color:{MIDNIGHT}}}
  .summary{{background:#fff;border:1px solid #E6E1DA;border-radius:14px;padding:18px 24px;margin:16px 0;font-size:15px;color:{MIDNIGHT}}}
  .grid{{display:flex;gap:28px;flex-wrap:wrap;align-items:center;background:#fff;border:1px solid #E6E1DA;border-radius:14px;padding:24px;margin-bottom:18px}}
  .panel{{background:#fff;border:1px solid #E6E1DA;border-radius:14px;padding:24px;margin-bottom:18px}}
  h2{{font-size:12px;letter-spacing:1px;text-transform:uppercase;color:{MIDNIGHT};margin:0 0 12px}}
  table{{width:100%;border-collapse:collapse}} td{{padding:8px 6px;border-bottom:1px solid #EEE9E2;font-size:14px}}
  .tier{{padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700;color:{MIDNIGHT}}}
  ul{{margin:0;padding-left:18px}} li{{margin-bottom:10px;font-size:14px;color:{MIDNIGHT}}}
  .rec{{border-left:4px solid {ROYAL}}} .rec h2{{color:{ROYAL}}}
  .cta{{display:inline-block;margin-top:12px;padding:10px 18px;border-radius:8px;background:{ROYAL};color:#fff;text-decoration:none;font-weight:700;font-size:13px}}
  .qw{{padding:8px 0;border-bottom:1px solid #EEE9E2;font-size:13px}}
  .muted{{color:#8A867E}} .qwhead{{color:#9a6a00}}
  .vd{{display:flex;gap:28px;flex-wrap:wrap;align-items:flex-start}}
  .vdlegend{{list-style:none;padding:0;margin:0;font-size:13px}} .vdlegend li{{margin-bottom:8px}}
  .vdlegend b{{display:inline-block;width:20px}}
  .foot{{font-size:11px;color:#8A867E;margin-top:16px}}
</style></head><body><div class="wrap">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">{DXC_LOGO}
    <span style="width:1px;height:16px;background:{MIDNIGHT};opacity:.25"></span>
    <span class="eyebrow" style="color:{MIDNIGHT}">AdvisoryX</span></div>
  <div class="cover">
    <div>
      <div class="eyebrow" style="color:{ROYAL}">AI Readiness Diagnostic</div>
      <h1>{sc.company_name}</h1>
      <div class="meta" style="margin-top:10px">{sc.industry_label} &middot; {sc.assessment_date}</div>
      <div class="reviewed"><span style="color:{ROYAL};font-weight:700">&#10003;</span> Reviewed by <b>DXC AdvisoryX</b></div>
    </div>
    <div style="text-align:right">
      <span class="tierbadge" style="background:{TIER_COLORS[sc.overall_tier]}">{sc.overall_tier}</span>
      <div class="overall" style="margin-top:8px">{sc.overall_score}<span> /100</span></div>
      <div class="meta" style="margin-top:6px;max-width:230px;margin-left:auto">{sc.peer_reference}</div>
    </div>
  </div>
  <div class="summary">{summary}</div>
  {nar_panel}
  <div class="grid">
    <div>{_radar(sc)}</div>
    <div style="flex:1;min-width:280px">{bars}
      <div class="muted" style="font-size:11px;margin-top:6px"><span style="display:inline-block;width:2px;height:10px;background:{MIDNIGHT};vertical-align:middle;margin-right:5px"></span>peer average · {sc.peer_reference}</div>
    </div>
  </div>
  <div class="panel"><h2>What we found</h2><ul>{findings}</ul></div>
  {vd_panel}
  <div class="panel rec"><h2>Recommended next step</h2>
    <p style="color:{MIDNIGHT};font-size:14px">{r.body}</p>
    <p class="muted" style="margin-top:6px">Duration: {r.duration_estimate_weeks}.</p>
    <a class="cta" href="mailto:{r.contact_email}">Continue the conversation &#8594;</a>
    <p class="muted" style="margin-top:8px">{r.contact_name} &middot; {r.contact_email}</p>
  </div>
  <div class="panel"><h2 class="qwhead">90-day quick wins</h2>{qwins}</div>
  <div class="foot">Confidential — prepared for {sc.company_name}. Prepared by DXC AdvisoryX.</div>
</div></body></html>"""


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "subject").lower()).strip("-") or "subject"


def save_scorecard(sc: Scorecard, out_dir: str = "outputs") -> str:
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    path = d / f"scorecard-{_slug(sc.company_name)}.html"
    path.write_text(render_scorecard_html(sc), encoding="utf-8")
    return str(path)
