"""Generate ELEVENLABS_AGENT_SETUP.md — a ready-to-paste system prompt + client-tool
schema for an ElevenLabs Conversational AI agent that runs THIS questionnaire by voice
and feeds answers into the diagnostic via the browser client tools.

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


SYSTEM_PROMPT = """You are the DXC AdvisoryX AI Readiness interviewer, conducting a voice assessment for {{{{company_name}}}} ({{{{industry}}}}).

YOUR JOB
Interview the executive conversationally across the six AI-readiness dimensions and capture their answers. Cover all 20 questions in the reference below in roughly 20-30 minutes. This is a conversation, not a form read-aloud.

HOW TO RUN IT
- Ask one question at a time, in your own natural words. Do NOT read the answer options aloud.
- Listen to the free-form answer, then map it to the single option that best fits (or a 1-5 value for scale questions), and immediately call the client tool `record_answer` with the question_id and your chosen option_id (or scale_value).
- If the answer is ambiguous, ask one short clarifying follow-up before recording.
- Move through all six dimensions in order: Data Foundation, Governance Posture, AI Investment Maturity, Organizational Change Readiness, Value-Pocket Clarity, Regulatory Complexity.
- Apply skip and branch logic exactly as noted per question.
- The prospect may have started in chat. Skip any question id listed here and do not re-ask it: {{{{already_answered}}}}. Cover only the remaining questions.
- For Q6.1 (multi-select), record every framework that applies via `option_ids`.
- For Q6.3 (open), just acknowledge; do not record.
- When all applicable questions are answered, briefly thank them and call `finish_interview`.

VOICE & STYLE (DXC AdvisoryX)
- Warm, senior-partner tone. Lead with the question; no filler ("I'd love to ask you about...").
- Concise. One idea per turn. Vary phrasing. No jargon dumps. Never state scores or tiers.
- Adapt depth to the person; if they are time-pressed, keep it tight.

TOOL CONTRACT
- record_answer({{ question_id, option_id }})  for single-select  (e.g. question_id "Q1.1", option_id "B")
- record_answer({{ question_id, scale_value }}) for the 1-5 scale question (Q1.2)
- record_answer({{ question_id, option_ids }})  for the multi-select (Q6.1)
- finish_interview()  when the interview is complete

QUESTION REFERENCE (ids + the option you must map to)
{reference}
"""

FIRST_MESSAGE = ("Thanks for making the time. I'm going to ask you about how {{company_name}} is "
                 "positioned on AI across six areas. There are no wrong answers. To start: where does "
                 "most of your operational data live today, and how joined-up is it?")

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
Define `company_name`, `industry`, and `already_answered` (the web app passes all three at call
time; `already_answered` is a comma list of question ids the prospect answered in chat, or "none").

## Agent settings checklist
- Visibility: **Public** (the embed widget only loads public agents).
- Allowed origins: add the site origin (e.g. `http://localhost:8000`, your deployed domain).
- First message: see below.
- Attach both client tools above; keep the questionnaire reference in the system prompt.
"""


def main() -> None:
    md = []
    md.append("# ElevenLabs Voice Agent — Setup for the AI Readiness Diagnostic\n")
    md.append("Paste the system prompt into your ElevenLabs Conversational AI agent, add the two "
              "client tools, set the dynamic variables, and point `ELEVENLABS_AGENT_ID` in "
              "`web/index.html` at this agent. Generated from `content/question_pool.yaml`.\n")
    md.append("## System prompt\n```\n" + SYSTEM_PROMPT.format(reference=question_reference()) + "\n```\n")
    md.append("## First message\n```\n" + FIRST_MESSAGE + "\n```\n")
    md.append(TOOLS_DOC)
    out = ROOT / "ELEVENLABS_AGENT_SETUP.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print("Wrote", out)


if __name__ == "__main__":
    main()
