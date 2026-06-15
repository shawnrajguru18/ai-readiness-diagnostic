"""Generate ELEVENLABS_AGENT_SETUP.md — a ready-to-paste system prompt + client-tool
schema for an ElevenLabs Conversational AI agent that runs THIS questionnaire by voice,
tuned for a premium executive experience, feeding answers into the diagnostic via the
browser client tools.

  python -m scripts.gen_voice_agent
"""
from __future__ import annotations
from pathlib import Path
from app.content import load_question_pool

ROOT = Path(__file__).resolve().parent.parent


def question_reference() -> str:
    pool = load_question_pool()
    dims = pool["dimensions"]
    lines = []
    cur = None
    for q in pool["questions"]:
        if q["dimension"] != cur:
            cur = q["dimension"]
            lines.append(f"\n### {dims[cur]['label']}")
        t = q["type"]
        lines.append(f"\n**{q['id']}** ({t}) — {q['text']}")
        if t in ("single_select", "multi_select"):
            for o in q["options"]:
                lines.append(f"  - `{o['id']}` = {o['text']}")
        elif t == "scale_1_5":
            for a in q["scale_anchors"]:
                lines.append(f"  - `{a['value']}` = {a['text']}")
        elif t == "open_short":
            lines.append("  - (free text — acknowledge verbally; do not score)")
        if q.get("skip_if"):
            s = q["skip_if"]
            lines.append(f"  - SKIP this if {s['question']} answer is in {s['answer_in']}.")
        if q.get("branch_if"):
            b = q["branch_if"]
            lines.append(f"  - ONLY ask if {b['question']} includes any of {b['answer_in']}.")
    return "\n".join(lines)


# .format() is used on SYSTEM_PROMPT, so dynamic-variable braces are quadrupled ({{{{x}}}})
# to render as {{x}}, and tool-arg braces are doubled ({{ }}) to render as { }.
SYSTEM_PROMPT = """You are the DXC AdvisoryX AI Readiness interviewer, speaking with {{{{prospect_name}}}} ({{{{prospect_role}}}}) of {{{{company_name}}}} in {{{{industry}}}}. This is a senior executive. Make it feel like a sharp 20-minute conversation with a senior partner, not a survey.

OPEN (first ~20 seconds)
Greet them by name. State the shape: "about 20 minutes, six short topics." Reassure once: "Your responses are reviewed by a DXC senior partner before any scorecard is produced, and aren't shared outside this assessment." Then begin.

RESPECT THEIR TIME
- Ask one natural question at a time. Never read the answer options aloud.
- Give light progress cues ("two topics to go").
- If they signal they're pressed ("keep it tight", "I'm short on time"), switch to compressed mode: ask only the single highest-signal question per remaining dimension and infer the rest, confirming your inference in one line.

ADAPT TO THE PERSON
- Frame everything for their persona ({{{{persona}}}}) and preference ({{{{framing_preference}}}}): a CFO (P3) hears ROI, capital allocation and risk; a CIO/CTO/CDO (P2) hears implementation, architecture and governance feasibility; a CEO/COO (P1) hears strategy, competitive position and the board narrative.
- Use {{{{industry}}}} language and examples (e.g. claims and underwriting for financial services; revenue cycle for healthcare; shop-floor and supply chain for manufacturing).

LET THEM STAY IN CONTROL
- Clarify on demand: if they ask what a term means, explain briefly in plain business language, then re-ask.
- Confirm-back: after a substantive answer, reflect it in one sentence and confirm before recording ("So AI risk sits across CISO, Compliance and Legal with no single owner, is that right?").
- Graceful skip: if they decline, acknowledge and move on; do not record that item.
- Corrections: if they say "change my last answer", update it with a new record_answer for that question id.

CAPTURE (call the client tools as you go)
- Map each answer to the single best-fitting option and immediately call record_answer.
- Already answered in chat — skip these question ids and do not re-ask: {{{{already_answered}}}}.
- Cover the remaining questions in dimension order: Data Foundation, Governance Posture, AI Investment Maturity, Organizational Change Readiness, Value-Pocket Clarity, Regulatory Complexity.
- Apply skip/branch logic exactly as noted per question. For Q6.1 (multi-select) record every framework that applies via option_ids; for Q6.3 (open) just acknowledge.

CLOSE (end on value)
- Thank them by name. Tell them the scorecard arrives within 24 hours, reviewed by a DXC partner. Give one immediate observation in a single sentence (the strongest area or the clearest gap you heard). Then call finish_interview.

VOICE & STYLE (DXC AdvisoryX)
- Warm, senior-partner tone. Lead with the question; no filler. Concise, one idea per turn, vary phrasing. Never state numeric scores or tiers. Let them interrupt you and yield gracefully.

TOOL CONTRACT
- record_answer({{ question_id, option_id }})  single-select  (e.g. question_id "Q1.1", option_id "B")
- record_answer({{ question_id, scale_value }}) for the 1-5 question (Q1.2)
- record_answer({{ question_id, option_ids }})  for the multi-select (Q6.1)
- finish_interview()  when the interview is complete

QUESTION REFERENCE (ids + the option you must map to)
{reference}
"""

FIRST_MESSAGE = ("Hi {{prospect_name}}, thanks for the time. I'm the DXC AI Readiness interviewer. "
                 "This takes about 20 minutes across six short topics, and everything is reviewed by a "
                 "DXC senior partner before any scorecard is produced. To start: where does most of "
                 "{{company_name}}'s operational data live today, and how joined-up is it?")

TOOLS_DOC = """## Client tools to add to the agent

Add these as **Client tools** (type: client) in the ElevenLabs agent. The browser registers
implementations for them (see `web/index.html` -> VoiceInterview), so leave "Wait for response"
on and no server URL.

### Tool 1 — `record_answer`
Description: "Record the prospect's answer to one questionnaire item."
Parameters:
| name | type | required | description |
|------|------|----------|-------------|
| question_id | string | yes | The question id, e.g. "Q1.1" |
| option_id | string | no | Chosen option id for single-select, e.g. "A"/"B"/"C"/"D" |
| scale_value | number | no | 1-5 for the scale question (Q1.2) |
| option_ids | array(string) | no | Chosen option ids for the multi-select (Q6.1) |

JSON Schema:
```json
{
  "type": "object",
  "properties": {
    "question_id": {"type": "string", "description": "Question id, e.g. Q1.1"},
    "option_id":   {"type": "string", "description": "Option id for single-select (A/B/C/D)"},
    "scale_value": {"type": "number", "description": "1-5 for scale questions"},
    "option_ids":  {"type": "array", "items": {"type": "string"}, "description": "Option ids for multi-select"}
  },
  "required": ["question_id"]
}
```

### Tool 2 — `finish_interview`
Description: "End the interview and generate the scorecard. Call once, after all applicable questions are answered."
Parameters: none. JSON Schema: `{ "type": "object", "properties": {} }`

## Dynamic variables
Define these on the agent; the web app passes all of them at call time:

| variable | example | purpose |
|----------|---------|---------|
| prospect_name | "Sarah Chen" | greet by name, close by name |
| prospect_role | "Chief Digital Officer" | seniority + framing |
| company_name | "MeridianFS" | personalize questions and the open/close |
| industry | "Financial services" | industry-specific framing |
| persona | "P2" | P1 exec sponsor / P2 operational owner / P3 financial scrutineer |
| framing_preference | "technical-operational" | financial-quantitative / strategic-narrative / technical-operational |
| already_answered | "Q1.1, Q1.2" (or "none") | question ids answered in chat; skip these |

## Agent settings checklist (executive experience)
- Visibility: **Public** (the embed widget only loads public agents).
- Allowed origins: add the site origin (e.g. `http://localhost:8000`, your deployed domain).
- Voice: a warm, credible voice; tune **turn/latency** low and enable **interruptions (barge-in)** so it feels like a real conversation.
- First message: see below (uses prospect_name + company_name).
- Attach both client tools above; keep the questionnaire reference in the system prompt.
- Optional: a small **knowledge base** (dimension definitions) so the agent can clarify terms on demand.
"""


def main() -> None:
    md = []
    md.append("# ElevenLabs Voice Agent — Setup for the AI Readiness Diagnostic\n")
    md.append("Tuned for a premium executive experience (time-aware pacing, persona/industry framing, "
              "confirm-back, clarify-on-demand, graceful skip, value-first close). Paste the system "
              "prompt into your ElevenLabs Conversational AI agent, add the two client tools, define the "
              "dynamic variables, and point `ELEVENLABS_AGENT_ID` in `web/index.html` at this agent. "
              "Generated from `content/question_pool.yaml`.\n")
    md.append("## System prompt\n```\n" + SYSTEM_PROMPT.format(reference=question_reference()) + "\n```\n")
    md.append("## First message\n```\n" + FIRST_MESSAGE + "\n```\n")
    md.append(TOOLS_DOC)
    out = ROOT / "ELEVENLABS_AGENT_SETUP.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print("Wrote", out)


if __name__ == "__main__":
    main()
