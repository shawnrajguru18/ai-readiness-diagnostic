# LLM Architecture and Output Assurance — Phase 1 Specification

**Date:** 6 August 2026
**Status:** DRAFT SPECIFICATION — normative for Phase 1 implementation; §6 lists points not yet decided
**Verified against:** commit `89a8971` (branch `doc/data-governance-stage1`) for all current-state
statements. No application code has changed since `3fb65ea`, this document's previous baseline; the
five call sites in §2.1 were re-read at promotion and are unmoved.
**Scope:** Which decisions a model makes and which deterministic code makes; what untrusted content
reaches a prompt; how output is shown to be fit to send to a client executive; and the contract
between the platform and the one integration that speaks to a prospect directly (§5). Covers
`architecture_topics.md` §6, and the model-facing half of §5.

**Conventions.** **MUST** / **MUST NOT** are requirements on the implementation. **Phase 1** marks
scope for the current build; **Deferred** marks a later phase. Statements under "Current" describe the
system as built and are verifiable against the referenced code. Findings carry an **L-** prefix, to
keep them distinct from the authorization spec's **P0-/P1-** and the data spec's **D-**. §6 lists
points not yet decided; requirements appear only where the obligation is already determinate.

**Promoted from holding document on 6 August 2026.** Until that date this file was an explicitly
non-normative parking place for findings no specification owned. Promotion changed the register and
added §5; it did not answer the questions in §6, and no L-finding's remediation was invented to fill
the gap. Where a fix depends on an undecided product question, it stays in §6.

**Relationship to other documents.** `authorization_model_phase1.md` is normative for identity and
route authorization; `data_architecture_phase1.md` is normative for keys, versioning and concurrency.
Neither covers what happens *inside* a model call, and neither mentions prompt injection — that gap is
why this document exists. It extends those two and **MUST NOT** restate them differently.

---

## 1. What this document decides

Three boundaries the platform cannot leave unowned once a model output is sent to a client executive
under a partner's attestation:

1. **Where untrusted content meets a prompt.** Five call sites interpolate caller-controlled text
   into a prompt string with no validation (§2). This document names that surface, states what
   contains it today and what does not, and makes it a defect with an owner rather than an audit note.
2. **Where the determinism boundary sits.** Scoring deterministic, narrative generative
   (`architecture_topics.md:283-285`) is the project's strongest design decision. **D-1** is what
   happened when that boundary moved without being decided (§4). This document holds it.
3. **What the voice integration owes the platform** (§5). The one channel where a model both conducts
   the interview and produces the input to scoring is also the one with no configuration contract.

**Why it exists now.** `architecture_topics.md` §6 sequences this topic behind identity and data, and
that sequencing is right: it is the only one of the three that cannot be built until the other two are
settled. The side effect was not right. Prompt injection is rated **BLOCKER** in the audit
(`quick_reference.md:12`, test 1.1, 4–6h estimated) and appears in `architecture_topics.md:252` and
`workflows_and_data_governance_baseline.md:434`, but was named in neither architecture specification —
so at the point where the specifications were reviewed for outstanding blockers, it was invisible:
present in the audit, absent from the plan. This document closes that gap.

---

## 2. L-1 — untrusted input reaches every prompt unsanitized

**Rated BLOCKER** (`quick_reference.md:12`). No remediation is stated here: choosing one is §6 item 1,
and it depends on a decision this document does not take for the team.

### 2.1 The surface as built

Five call sites interpolate caller-controlled text directly into a prompt string. None validates,
escapes, delimits or length-bounds it:

| Site | Untrusted content | Reaches |
|---|---|---|
| `agents/__init__.py:53-54` | `prospect_name`, `prospect_role`, `company_name_raw`, and the email domain | A2 persona inference |
| `:107-111` | `company_name_raw`, **and the research payload** (§2.2) | C2 synthesis — findings, reasoning, next step |
| `:136` | `company_name_raw` | The deterministic C2 fallback body |
| `:244-246` | `company_name_raw` | C3 quick-win selection and framing |
| `:437-444` | `company_name_raw` **and the entire voice transcript** (§2.3) | The voice dimension scorer |

`models.py:39-49` applies no constraint to these fields beyond type. The audit's own payload for test
1.1 is a company name carrying an instruction.

### 2.2 Indirect injection, which the finding does not name

`:109` interpolates `json.dumps(research)[:2000]` into the C2 prompt. That payload is **fetched from
third parties** — B1 and B2 are live reads of SEC EDGAR and news (`orchestrator.py:86`,
`app/research.py`) — so the content of a prompt that produces client-facing findings is partly written
by whoever controls a page the researcher retrieved. The prospect does not have to be the attacker;
they only have to be researched.

This is **not currently reachable**: `config.py:58` defaults `enable_research` to `false`, and topic 6
records B1/B2/B3 as gated off. It becomes reachable the moment research is switched on, which is
scheduled work, not hypothetical. **Turning research on and defending the prompt are one change, not
two.**

### 2.3 The voice transcript is the largest surface, and it is new

`:432-435` joins every spoken answer into `answer_text` and interpolates it whole. Unlike a company
name this is unbounded, free-form, and by design conversational — the one input where "ignore your
previous instructions" arrives in a form indistinguishable from the intended content.

It did not exist before `ed667aa` (2 Aug), the same commit as **D-1**. The audit predates it
(10 July), so the BLOCKER rating was assigned against a smaller surface than the one now shipping.
**Re-rating is a prerequisite to costing the fix**, and it is not in issue #4's scope — #4 corrects
what that scorer *emits*, not what it *ingests*.

### 2.4 What partly contains it today, and what does not

Stated so a future reader does not over- or under-estimate the exposure:

- **Structured output helps with shape, not content.** A2, C2 and C3 go through
  `llm.parse_structured` (`llm.py:119`) into Pydantic models, so an injected instruction cannot change
  the *schema* of the reply. It can change every string inside it — `reasoning`, finding bodies, the
  recommended next step — and those are exactly what the client reads.
- **Nothing constrains the output path.** Model text flows to the scorecard and the PDF with no
  validation gate: D2 is a stub (`architecture_topics.md:295`), so the agent specified to catch output
  that "would mislead the prospect or embarrass DXC" (`companion_04:1116`) does not run.
- **The blast radius is a document, not a system.** No agent has tool access, no output is executed,
  and no model output reaches a shell, a query or a filesystem path. The realistic harm is a
  falsified, defamatory or manipulated deliverable going out under DXC's name and a partner's
  attestation — a reputational and contractual harm, not an RCE.
- **Adjacent, and separately rated:** PDF content injection (`master_audit_report.md:486-487`,
  CRITICAL ×2) is the same untrusted strings reaching ReportLab rather than a model. A single
  input-validation layer at the boundary would serve both, which is `architecture_topics.md:262`
  open item 1.

---

## 3. Further findings

Carried from `architecture_topics.md` §6 so this document is the single place topic 6 accumulates.
Each is live. Where a remediation depends on an undecided product question, that question is in §6
rather than answered here.

| # | Finding | Note |
|---|---|---|
| **L-2** | **D2 validation agent is a stub.** Open item #9, due 31 Jul, unclosed. Without it there is no automated assurance and no input to review priority | `architecture_topics.md:295,304` |
| **L-3** | **The human gate is promised and not built.** The voice agent, the Submitted screen and the scorecard's partner attestation all state a partner reviews before delivery; the code delivers synchronously. Either build it or stop promising it | `architecture_topics.md:313-316` |
| **L-4** | **No eval strategy for generative text.** `evaluation_suite.md` covers security and integrity only; "passing" is undefined for narrative output | `architecture_topics.md:306` |
| **L-5** | **Hallucination and source attribution** once research is enabled — per-source attribution with fetch timestamps is required and unimplemented | `companion_05:303-447` |
| **L-6** | **Cost ceiling and kill switch.** $0.95 measured against a <$1.00 target, for a control that does not exist | `performance_audit_summary.md:70` |
| **L-7** | **Silent fallback.** Every agent degrades to a deterministic stub on any exception, so a scorecard can contain no model output at all. The *recording* of this is specified as `fallback_used` in `data_architecture_phase1.md` §6.1; what to *do* about it is this document's question | **D-2** |

---

## 4. Boundary with the two written specifications

Recorded now, while the reasoning is fresh, so the boundary is not re-litigated later:

- **Prompt and content versioning belongs to the data specification.** `data_architecture_phase1.md`
  §6 already specifies the input fingerprint, including per-agent model identity, prompt hashes and
  `fallback_used`. This document consumes that; it does not redesign it.
- **Route authorization and rate limiting belong to the authorization specification** (**P0-3**),
  even though the cost they protect is a model cost.
- **The determinism boundary is this document's**, and it is the one thing topic 6 calls the project's
  strongest design decision: scoring deterministic, narrative generative
  (`architecture_topics.md:283-285`). **D-1** is what happens when that boundary moves without being
  decided — a deterministic scorer was replaced by a generative one in six minutes, and the taxonomy
  went with it.
- **Open point I2 moved here on 6 August 2026**, from `data_architecture_phase1.md` §19. It asks
  whether the voice interview returns to option ids or stays free text, which is the determinism
  boundary for the voice channel and therefore the bullet above, not a storage question. The data
  specification keeps a pointer because two of its sections are gated on the answer; the decision is
  §6 item 9 here. The findings it derives from — **D-1** and **D-8** — do **not** move: they are
  verified against code in that document's baseline, and splitting a finding from its evidence to
  follow a decision would be the wrong half to relocate.

---

## 5. Integrations

One integration runs a model outside this codebase and speaks to a prospect directly. It gets a
section because nothing else in the architecture set owns what that model is told, what it returns, or
what it is permitted to do.

### 5.1 ElevenLabs Voice Agent

The voice channel is the only place where a model both *conducts* the interview and *produces* the
input to scoring. §2.3 already names its transcript as the largest injection surface in the system.
What that section lacks — and what follows here — is the configuration contract the surface sits on.

**Benchmark.** Statements below are measured against the vendor's *Agent Deployment Guide v1.1*
(March 2026), held with the DXC briefs in the sibling `ai-readiness-diagnostic-context/ElevenLabs/`
folder. That folder is not version-controlled with this repository, so guide sections are cited by
number (`guide §4.3`) and briefs by date. One caveat on the guide itself: its §4.1 model table is
internally inconsistent — recommending GPT-5.4, then "start with GPT-4.1", then GPT-5.2 — and predates
current models. It is not a usable reference for model choice.

**Owned elsewhere.** The divergence between the documented tool contract and the live agent is
**D-8**; the dimension-taxonomy break it caused is **D-1** (`data_architecture_phase1.md` §14,
both tracked as issue #4). Neither is restated here. One piece of visible residue is worth recording
because it misleads a reader of the running app rather than of a document:
`web/src/screens/VoiceInterview.tsx:171` renders `{count} of 20`, where `count` is the number of
distinct free-text question *strings* the agent has sent (`:83`) and 20 is the size of
`content/question_pool.yaml`. The two are not the same key space, and the agent's own compressed mode
(`scripts/gen_voice_agent.py:53`) may legitimately end an interview after six answers. The denominator
is a claim the capture path cannot honour — the same drift as **D-8**, surfacing in the UI.

#### Current

| Capability | Guide § | As built |
|---|---|---|
| System prompt structure | 4.2 | Prose sections; no `## Guardrails` heading (`scripts/gen_voice_agent.py:45-85`) |
| Platform guardrails (Security tab) | 4.3 | None configured |
| Knowledge base | 4.4 | None; marked optional (`docs/integrations/elevenlabs_agent_setup.md:243`) |
| Tools | 4.5 | Two client tools (`web/src/screens/VoiceInterview.tsx:76-96`) |
| Channel | 4.6 | Web widget loaded from unpkg (`web/src/screens/VoiceInterview.tsx:63-69`) |
| Dynamic variables | 4.7 | Seven passed at call time (`web/src/screens/VoiceInterview.tsx:97-105`) |
| Pre- and post-call webhooks | 4.7 | None |
| Workflows | 4.8 | None; one monolithic prompt |
| Testing (three tiers) | 5.1 | None |
| Evaluation and Data Collection | 5.3 | None |
| Staged rollout, metrics | 6.1, 6.3 | None |

This is not partial configuration. It is an embed — a widget, a prompt and two tools — with none of
the apparatus the guide treats as prerequisite to real traffic. That is a defensible prototype posture
and an indefensible production one, and the distinction has never been written down anywhere. Which is
how `docs/integrations/elevenlabs_agent_setup.md`, a generated artefact, came to read as the
configuration record for an agent it no longer describes.

#### Findings

- **L-8 — the mechanism that keeps prompt and questionnaire in sync is disconnected.**
  `scripts/gen_voice_agent.py:160` writes `ELEVENLABS_AGENT_SETUP.md` at the repository root; the live
  document is `docs/integrations/elevenlabs_agent_setup.md`, moved by commit `7387cfc`; the root file
  does not exist. Regenerating therefore produces a second file and leaves the documented one stale.
  This is the mechanism that would have surfaced **D-8** on the next regeneration, and nothing owns it.
- **L-9 — no guardrail layer on the one agent that talks to a client executive.** The generated prompt
  has no `## Guardrails` section, which guide §4.2 singles out as the heading models attend to, and no
  platform guardrail from guide §4.3 (Focus, Manipulation, Content, Custom) is enabled. This compounds
  **L-1**: the voice agent is simultaneously the largest untrusted-input surface in §2 and the only
  model in the system with no control of either kind.
- **L-10 — agent-contract drift has no standing control.** No tests of any of the three tiers in guide
  §5.1 exist. A single tool-call test asserting `record_answer` fires with `question_id="Q1.1"` would
  have failed the moment the live agent stopped sending ids; instead the divergence was absorbed by
  changing the browser handler to match (**D-8**). Related to **L-4**: neither generative output nor
  agent behaviour has a definition of passing.
- **L-11 — the voice channel produces no server-side record.** Client tools only, so answers
  accumulate in browser memory until `finish_interview` (`web/src/screens/VoiceInterview.tsx:42,76-96`),
  at which point `web/src/App.tsx:82` posts `responses: {}` with the voice answers alongside. An
  abandoned call loses everything, and no artefact survives for review, re-scoring or dispute. Guide
  §4.7's post-call transcription webhook is the supported mechanism. Related to **L-7** and to
  `data_architecture_phase1.md` §7.
- **L-12 — a third dimension taxonomy exists.** `content/interview_definition.yaml:1-5` is still
  headed PLACEHOLDER, and its objective keys (`:10,22,34,46,58,70`) are
  `strategy / data / technology / process / people / governance` — neither the canonical six
  (`content/question_pool.yaml:15-21`) nor the divergent six that **D-1** records. Three taxonomies
  is what §4's determinism boundary looks like after two commits with no owner.

#### Requirements

| # | Requirement | Finding | Marks |
|---|---|---|---|
| **R1** | The live agent's tool contract and the generated setup document **MUST** describe one interface. The generated document is the single source and **MUST NOT** be hand-edited to close a divergence | D-8, L-8 | Phase 1 |
| **R2** | `scripts/gen_voice_agent.py` **MUST** write to `docs/integrations/elevenlabs_agent_setup.md`, and regeneration **MUST NOT** create a second file at the repository root | L-8 | Phase 1 |
| **R3** | The voice agent's system prompt **MUST** carry a `## Guardrails` section, and the platform Focus Guardrail **MUST** be enabled, before the agent serves public traffic | L-9, L-1 | Phase 1 |
| **R4** | A tool-call test asserting the `record_answer` contract **MUST** exist, and **MUST** pass before any change to the agent configuration is published | L-10 | Phase 1 |
| **R5** | Exactly one dimension taxonomy is canonical: the six in `content/question_pool.yaml:15-21`. `content/interview_definition.yaml` **MUST** be reconciled to it or retired | L-12, D-1 | Phase 1 |
| **R6** | The voice channel **MUST** produce a record of the interview that survives the browser session. Guide §4.7's post-call transcription webhook is the supported mechanism | L-11 | Deferred |
| **R7** | Prospect-identifying dynamic variables **MUST NOT** be sent to a Public agent once the channel carries production data. Recorded as a pointer only — the obligation belongs to the data and legal track (`architecture_topics.md:384`, and the 5 June 2026 decision that signed contracts precede production data) | — | Deferred |

#### Recommendation on I2

**I2** — whether the voice channel returns to option ids or stays free text — is §6 item 9 of this
document, and issue #4 owns the fix. This is the recommendation:

**Hybrid capture** — `record_answer({question_id, option_id, verbatim})`. The `question_id` and
`option_id` restore deterministic Companion-01 scoring and close **D-1** at its root. The consequence
that matters to this document is what it does to §2.3: the scoreable path stops ingesting free text
altogether, so the unbounded transcript becomes *stored data* rather than *scorer input*. That
**shrinks** the largest injection surface in the system instead of defending it — a structural
remedy available to no other call site in §2.1, because everywhere else the untrusted text is the
thing being reasoned about. The `verbatim` field retains the hedging, confidence and vocabulary that
the May 2026 demo brief argues is voice's entire reason for existing over a form.

---

## 6. Points not yet decided

No requirement is written for these. Each depends on a product decision this document does not take
for the team, and each is listed so its absence is visible rather than inferred:

1. **Injection defence strategy** — structural separation of instructions from data, sanitisation, or
   output constraints. Topic 6 open item 3 notes the constraint that makes this non-trivial: prospect
   names and spoken answers reach the model by design, so removal is not available.
2. **Where validation lives** — one boundary layer or per-call-site. Five findings share the same
   unvalidated fields (`architecture_topics.md:262`).
3. **Whether the human gate is mandatory or advisory in V1** (L-3). Everything client-facing assumes
   mandatory.
4. **What D2 blocks on, and what it merely flags** (L-2).
5. **Whether research is enabled for the beta**, which decides whether §2.2 is live.
6. **What "fit to send" means, testably** (L-4).
7. **Whether the voice agent's guardrail layer is prompt-level, platform-level or both** (L-9). Interacts
   with item 1: the same decision in a different position.
8. **Where the standing control against agent-contract drift runs** — repository CI, the vendor's Tests
   tab, or both (L-10). R4 requires the test; it does not choose the home.
9. **I2 — whether voice capture is bounded or unbounded.** *Owned here.* Whether the voice interview
   returns to option ids, restoring deterministic Companion-01 scoring, or stays free text with an LLM
   scorer keyed to the canonical ids (**D-8**). Stated as issue #4's Layer 2 options (a)/(b)/(c), which
   owns the fix; what is open is the choice. §5.1 records this document's recommendation.

   **Why it is this document's.** It decides where the determinism boundary sits for the voice
   channel — the boundary §4 keeps here — and it decides whether §2.3's surface is *reduced* or merely
   *defended*, so it is an injection-defence decision as much as a scoring one. The data specification
   inherits the consequence (whether §7 there can store a `question_id` at all) but does not take the
   decision; it was carried in that document's register until 6 August 2026 and moved here.

   **What it blocks.** R1 above; `data_architecture_phase1.md` §17 Stage 0a and §7; and, through
   Stage 0a → Stage 2, `authorization_model_phase1.md` §12.2 Phase 2 — because creating `assessments`
   with tenancy and creating it with a version chain are one act. It is a single edge, not a chain:
   that document's Stages 0b and 1 are independent of this decision and proceed today. That last
   consequence is the reason this point is worth answering early rather than whenever the voice work
   reaches it: **an unanswered question about the voice channel is currently sitting on the tenancy
   boundary.**

   **One nearby escape was withdrawn on 7 August 2026, and it was not an escape from this point.**
   Until then, `data_architecture_phase1.md` §4.4 amendment 2 offered to split the tenant and
   versioning backfills and pay a double rewrite over a table of demo records. The legacy table is now
   abandoned rather than migrated (§16 there), so there is no backfill to split — but what that bought
   was *scheduling*, letting the tenancy work land ahead of the versioning pass, not a way of writing
   versions without settling the taxonomy. **The exposure here is unchanged.** It has always been
   about newly written versions: backfilled ones were marked `fingerprint_incomplete` and barred as
   diff baselines whatever taxonomy produced them. The first version the system writes is a real
   client's, immutable, and permanently non-comparable to everything after the taxonomy is reconciled —
   as true on 6 August as now. This point is worth answering early because it costs a decision rather
   than work, not because anything made it more urgent. `data_architecture_phase1.md` §17 records the
   one escape that does remain.

   **The label is kept across the move.** `I2` reads as a sub-point of the data spec's **I**; it is
   not, and never was. It survives because issue #4 and four documents cite it by name, and a rename
   would cost more than the inconsistency does.

---

## 7. Delivery sequencing

Most of this document sits behind the identity model (`authorization_model_phase1.md`) and the data
model (`data_architecture_phase1.md`), which settle what a run *is* and what is recorded about it.
Three things do not.

- **L-1 depends on neither prerequisite.** It is a live BLOCKER against a public-traffic hold
  (`master_audit_report.md:47,155`) and can be fixed at any time; what it waits on is §6 item 1, a
  decision, not a sequence.
- **R1–R5 depend on neither prerequisite.** They concern an agent configuration, a generator output
  path, a prompt section, a test and a content file — none of which touch identity, keys or
  versioning. **R1 is the one with an internal dependency:** it is issue #4's Layer 2, and it cannot
  complete until I2 (§6 item 9) is answered, because the contract cannot be regenerated until its
  shape is chosen. R2–R5 can proceed today.
- **R3 has a deadline that is not ours to move.** It is expressed against public traffic, so it is
  gated by the same hold as L-1 rather than by this document's sequence.

**R6 and R7 are Deferred.** R6 lands with `data_architecture_phase1.md` §7's interview tables; R7 with
the data and legal track.

---

*Related: `architecture_topics.md` §6 (the outline this document answers) and §5 (the input
boundary L-1 sits on), `authorization_model_phase1.md` (normative for identity and routes),
`data_architecture_phase1.md` (normative for the fingerprint that records model identity;
**D-1**/**D-8** are tracked as
[`SAM-Prime-X/ai-readiness-diagnostic#4`](https://partner-github.dxc.com/SAM-Prime-X/ai-readiness-diagnostic/issues/4)),
`companion_04_agent_prompts.md` (agent contracts, model tiering, confidence thresholds, kill
switches), `quick_reference.md:12` and `evaluation_suite.md` test 1.1 (the BLOCKER rating and its
payload), `docs/integrations/elevenlabs_agent_setup.md` (the generated agent configuration §5.1
governs), and the vendor and DXC source documents in the sibling `ai-readiness-diagnostic-context/ElevenLabs/`
folder, where `agent_use_analysis.md` carries the long-term direction §5.1 deliberately does not.*
