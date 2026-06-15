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


def render_scorecard_html(sc: Scorecard) -> str:
    rows = "".join(
        f'<tr><td>{d.label}{" (informational)" if d.informational else ""}</td>'
        f'<td style="text-align:right;font-weight:700">{d.score}</td>'
        f'<td><span class="tier" style="background:{TIER_COLORS[d.tier]}">{d.tier}</span></td></tr>'
        for d in sc.dimensions
    )
    findings = "".join(
        f'<li><b>{f.headline}.</b> {f.body}</li>' for f in sc.findings
    )
    qwins = "".join(
        f'<div class="qw"><b>{q.pattern_name}</b> — {q.one_line_description} '
        f'<span class="muted">({q.timeline_to_value})</span></div>' for q in sc.quick_wins
    )
    r = sc.recommended_next_step
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>AI Readiness Scorecard — {sc.company_name}</title>
<style>
  body{{font-family:'DM Sans',Arial,sans-serif;background:{CANVAS};color:{INK};margin:0}}
  .wrap{{max-width:900px;margin:0 auto;padding:40px}}
  .eyebrow{{letter-spacing:2px;text-transform:uppercase;font-size:11px;color:{MIDNIGHT};font-weight:700}}
  h1{{font-family:'Playfair Display',Georgia,serif;color:{MIDNIGHT};font-size:30px;margin:6px 0}}
  .meta{{font-size:12px;color:{INK};margin-bottom:6px}}
  .grid{{display:flex;gap:28px;flex-wrap:wrap;align-items:center;background:#fff;border:1px solid #E6E1DA;border-radius:14px;padding:24px;margin:18px 0}}
  .overall{{font-family:'Playfair Display',Georgia,serif;font-size:54px;color:{MIDNIGHT};line-height:1}}
  .tierbadge{{display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:13px}}
  .panel{{background:#fff;border:1px solid #E6E1DA;border-radius:14px;padding:24px;margin-bottom:18px}}
  h2{{font-size:12px;letter-spacing:1px;text-transform:uppercase;color:{MIDNIGHT};margin:0 0 12px}}
  table{{width:100%;border-collapse:collapse}} td{{padding:8px 6px;border-bottom:1px solid #EEE9E2;font-size:14px}}
  .tier{{padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700;color:{MIDNIGHT}}}
  ul{{margin:0;padding-left:18px}} li{{margin-bottom:10px;font-size:14px;color:{MIDNIGHT}}}
  .rec{{border-left:4px solid {ROYAL};background:#fff;padding:16px 18px;border-radius:10px}}
  .rec h2{{color:{ROYAL}}} .qw{{padding:8px 0;border-bottom:1px solid #EEE9E2;font-size:13px}}
  .muted{{color:#8A867E}} .qwhead{{color:#9a6a00}}
  .foot{{font-size:11px;color:#8A867E;margin-top:16px}}
</style></head><body><div class="wrap">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">{DXC_LOGO}
    <span style="width:1px;height:16px;background:{MIDNIGHT};opacity:.25"></span>
    <span class="eyebrow">AdvisoryX · AI Readiness Diagnostic</span></div>
  <h1>{sc.company_name}</h1>
  <div class="meta">{sc.industry_label} · {sc.assessment_date} · Reviewed by {sc.reviewed_by}</div>
  <div class="grid">
    <div>{_radar(sc)}</div>
    <div>
      <div class="eyebrow">Overall AI readiness</div>
      <div class="overall">{sc.overall_score}</div>
      <span class="tierbadge" style="background:{TIER_COLORS[sc.overall_tier]}">{sc.overall_tier}</span>
      <div class="meta" style="margin-top:8px">{sc.peer_reference}</div>
    </div>
  </div>
  <div class="panel"><h2>Dimensions</h2><table>{rows}</table></div>
  <div class="panel"><h2>What we found</h2><ul>{findings}</ul></div>
  <div class="panel rec"><h2>Recommended next step</h2>
    <p style="color:{MIDNIGHT};font-size:14px">{r.body}</p>
    <p class="muted">Duration: {r.duration_estimate_weeks}. Continue the conversation: {r.contact_name}, {r.contact_title} | {r.contact_email}</p>
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
