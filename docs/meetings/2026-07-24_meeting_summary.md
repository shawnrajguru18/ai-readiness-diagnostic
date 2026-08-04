# AdvisoryX — Intro / Scoping Call

**Date:** Friday, 2026-07-24
**Participants:** Shawn Rajguru (DXC — project lead, built the POC), Alex Schick (Scrum Master / BA), Denis Morozov (candidate developer)
**Also present briefly:** Eddie (staffing coordinator — dropped off after intros)
**Purpose:** Introduce the AI Diagnostic initiative, assess fit, agree start date and next steps.

> Transcript caveat: speaker labels in the raw transcript are unreliable — "Participant 1" covers both Shawn and Alex, and several of Denis's lines are mis-attributed. The summary below reflects the corrected reading.

---

## 1. Executive summary

DXC is building an **executive AI diagnostic** — an AI-led, voice-based maturity assessment that client executives complete on their own time, in place of a human advisor-led discovery session. It is explicitly a **sales funnel asset**, not a standalone product: the output is deliberately calibrated to be useful enough to be credible, but incomplete enough that the client books a follow-up.

A POC already exists (built solo by Shawn, running on AWS). The ask is to **harden it into a production MVP in roughly three weeks of development**, with production release at week five. Denis was assessed as a strong fit — relevant multi-agent, evals/guardrails and full-stack experience — and confirmed he can take the build end-to-end and dedicate full time. **Earliest start: Thursday, 2026-07-30** (training in San Francisco Mon–Tue).

The one live blocker is **repository access**, which was not resolved during the call.

---

## 2. The product

### Stage 1 — AI Diagnostic (this engagement)
- Client executive takes an **adaptive, voice-led AI interview**, built on the **ElevenLabs** agentic voice platform.
- Duration target: **20–30 minutes max** (Shawn quoted both "20–30" and "20–25" — needs pinning down).
- Assessment domains: **strategy, governance, people, process, technology, data**. *(Shawn said "five areas" and then listed six, then referred to "all six" — requires confirmation.)*
- **Role-adaptive questioning**: a CFO gets CFO-relevant questions, a CTO gets CTO-relevant questions. Initial implementation to be **deterministic** (curated question lists per role), evolving to agentic question generation later.
- **Multi-respondent, company-scoped**: several executives from the same organisation (e.g. CFO then CTO at Bank of America) can each take the interview; responses are attributed to the individual but **aggregated and categorised to the company** for a company-level maturity picture.
- **Immediate output** (LLM-generated) after completion: prioritised risks and impacts, peer benchmark insight, business-case focus areas, regulatory exposure.
- Follow-up by a human advisor within **24 hours**.

### Stage 2 — Process mining (out of scope now, but shapes the architecture)
- Deep dive into client systems: CMDB, ERP, ServiceNow, CRM.
- Leverages an existing process-mining tool referred to as **"Access AI"** *(name to be confirmed)*, plus LLM calls against client artefacts, to synthesise a targeted findings report.

### Stage 3 — Delivery
- The resulting consulting engagement.

### Long term
- Folds into the **Converse** platform (agentic AI platform built by the DXC India team), intended as DXC's equivalent of an internal/client-facing "oasis"-style destination. Implication: **architecture must be judged on whether it scales to multi-client, multi-use-case**, not just on whether the MVP ships.

---

## 3. Technical picture

| Area | Current state |
|---|---|
| Voice/agent layer | ElevenLabs agentic voice platform; vendor has supplied a list of optimisation recommendations |
| Backend | Python, with an orchestrator component |
| Frontend | TypeScript / React, Tailwind |
| Cloud | AWS — ECR, Docker containers |
| IaC | Terraform (Shawn tears down / brings up the stack) |
| Repos | Multi-repo (app backend + web) |
| Auth | **None today** — exposed via raw IP/URL |
| Team | Shawn alone so far; Alex running sprint zero / backlog (~20 draft stories) |

### Known defects raised on the call
- **Model invocation failures**: Shawn has observed errors in the AWS console — some model calls fire, some do not. Root cause unknown; needs triage.

### Denis's technical positioning (as stated)
- Built **six AI agents** at a hedge fund client, including a broker-selection trading support agent fusing a dozen-plus data sources (live rates + historical broker execution quality).
- Built a **"Judge" verification layer** — a second-tier agent that validates verifiable data (numbers, symbols, rates) before the pipeline proceeds. Directly relevant to the hallucination risk in this product.
- Built AI-driven **incident/log triage agents** over Kibana and Datadog traces, pinpointing failing code paths pre-emptively.
- Languages: TypeScript/JavaScript (primary), Python (current AI work), Java historically.
- Docker: 10+ years. Runs a home server farm for model experimentation.
- **AWS: self-declared not proficient** — has used declarative/YAML-driven provisioning and rolled workloads out to AWS, but this is the main capability gap against the role.
- Has previously implemented **Entra ID** login.
- Working style: operates as an architect, running parallel Claude sessions across git worktrees rather than delegating to junior developers.

---

## 4. Timeline

| Milestone | Date / window |
|---|---|
| Denis — SF training | Mon 27 – Tue 28 Jul |
| Denis — reading repo/backlog (flight) | Wed 29 Jul |
| **Denis start date** | **Thu 30 Jul** |
| Next joint call — Denis presents his read of goals, structure, architecture | Fri 31 Jul *(conflict — see risks)* |
| Architecture review | Week of 28 Jul |
| Development complete | ~2.5–3 weeks from start (≈ w/c 18 Aug) |
| Testing / internal "customer zero" (DXC orgs) | Week 4 |
| Production MVP | **Week 5 — hard expectation from leadership** |

Scope note: this initiative was **descoped from a 15-week, 20-agent engagement** to the current narrow Stage 1 focus.

---

## 5. Analysis — risks and gaps

### Blocking now
1. **Repository access is unresolved.** DXC runs two GitHub instances (internal, and `partnergithub.dxc.com`). Denis's DXC credentials do not work on the partner instance; a ServiceNow request is in flight with a ~24h SLA. Alex is separately blocked at 404 and needs adding to the **Catalyst** org — the admin appears to be Andre. Shawn shared a personal clone during the call which Denis *was* able to open, so reading can start; write access and the canonical repo are still pending. **Every downstream date depends on this.**

### High
2. **Single-developer delivery risk.** One developer is expected to harden an unfamiliar POC, add features, secure it, add evals and a QA agent, and ship to production in five weeks. There is no slack. Shawn is not available to co-develop ("busy with other projects"), so he is a review/decision dependency, not a capacity buffer.
3. **Bus factor of one on the existing code.** Shawn built the POC alone; no one else has worked in it. Knowledge transfer needs to be explicit, not incidental.
4. **AWS proficiency gap.** The stack is AWS + Terraform + ECR and Denis flagged AWS as his weakest area. Manageable, but it should be named and covered — either time-boxed ramp-up or a named AWS/infra point of contact.
5. **Hallucination risk in a client-facing sales asset.** The report goes in front of a prospect's CFO/CTO. A fabricated regulatory claim or benchmark figure is a commercial and reputational failure, not just a bug. Denis's "Judge" pattern and the proposed QA review agent are the right mitigation — this should be a first-class requirement with acceptance criteria, not a nice-to-have story.
6. **Peer benchmark has no identified data source.** The output promises "peer benchmark insight," but no benchmark dataset or methodology was discussed. Without a real corpus this is the single most likely thing for the model to invent. **Needs an owner and a source decision before build.**

### Medium
7. **Authentication is undecided.** Alex raised mid-call that Entra ID may be wrong if respondents are external client executives, and deferred it to a later meeting. This gates the security story and affects the frontend, so it needs closing in week one.
8. **Data privacy / confidentiality was not discussed at all.** Executives will disclose candid governance, regulatory and capability weaknesses. Retention, storage location, tenancy separation between client companies, voice-recording consent, and what may be reused for benchmarking all need answers before customer zero, let alone external clients.
9. **Requirements are still in motion.** Question lists are owed by senior partners (Rob, Chris); stakeholder meetings were still happening the same afternoon and into the following week. Development starting 30 Jul against a backlog that is still "draft" is a rework risk.
10. **Scope inconsistencies to resolve:** five vs six assessment domains; 20–25 vs 20–30 minute interview; deterministic vs agentic question selection cut-off for MVP.
11. **Next-call scheduling conflict.** Fri 31 Jul was agreed, but Shawn also stated he returns from San Francisco that day. Confirm.

### Positive signals
- Denis and Shawn are both US Eastern (Florida / New Jersey) — same time zone, unlike Denis's previous distributed engagement.
- A working POC already exists; this is hardening, not greenfield.
- Denis independently articulated the funnel/relationship framing ("we build a relationship, not just a product"), which matched Shawn's intent — good commercial alignment.
- Denis confirmed he can dedicate full time and continue beyond the initial engagement; Shawn explicitly signalled intent to scale the work.

---

## 6. Action items

### Shawn Rajguru
| # | Action | Due |
|---|---|---|
| S1 | Grant Denis access to the canonical POC repo on `partnergithub.dxc.com` (blocked on his ServiceNow request) | 25 Jul |
| S2 | Escalate to Andre for org-level (Catalyst) admin rights so collaborators can be added directly | 25 Jul |
| S3 | Share the ServiceNow partner-GitHub access form link with Denis | Done / confirm |
| S4 | Share the personal clone link as the interim read-only artefact | Done in call |
| S5 | Triage which model calls are failing in the AWS console and share findings | Before 30 Jul |
| S6 | Walk Denis through the deployed app and Terraform stack (deferred — deploy was still coming up) | Week of 28 Jul |
| S7 | Confirm the assessment domain list (5 vs 6) and the interview duration target | Week of 28 Jul |
| S8 | With Rob and Chris, deliver the role-based question lists and the full list of supported executive roles | Week of 28 Jul |

### Alex Schick
| # | Action | Due |
|---|---|---|
| A1 | Send Denis a screenshot / export of the current draft user stories after the stakeholder meeting | 24 Jul |
| A2 | Finalise sprint-zero backlog after stakeholder sessions; flag changes to Denis | w/c 28 Jul |
| A3 | Schedule the architecture review session | w/c 28 Jul |
| A4 | Close the authentication decision — Entra ID vs external-user identity | w/c 28 Jul |
| A5 | Consolidate the ElevenLabs vendor optimisation recommendations into stories | w/c 28 Jul |
| A6 | Specify the frontend additions: calendar booking on interview completion, confirmation email when scorecard is ready | w/c 28 Jul |
| A7 | Write acceptance criteria for output quality / QA review agent | w/c 28 Jul |

### Denis Morozov
| # | Action | Due |
|---|---|---|
| D1 | Complete the ServiceNow request for a partner GitHub account; confirm access once granted | 25 Jul |
| D2 | Review the repo (Python backend + orchestrator, TS/Tailwind web) and the draft backlog | 29 Jul (flight) |
| D3 | Prepare and present understanding of project goals, structure and proposed architecture | Fri 31 Jul call |
| D4 | Come to the architecture review with a scale-out view: multi-client, multi-use-case, not just MVP | w/c 28 Jul |
| D5 | Propose the evals / guardrails / verification approach (Judge-style validation layer) as a concrete design | Fri 31 Jul call |
| D6 | Raise the benchmark data-source question and the data-privacy/retention question explicitly | Fri 31 Jul call |
| D7 | Start on the engagement | Thu 30 Jul |

### Joint / unassigned
| # | Action |
|---|---|
| J1 | Confirm the Fri 31 Jul call given Shawn's return travel that day |
| J2 | Identify the owner and data source for the peer benchmark output |
| J3 | Define data retention, tenancy separation and consent handling before customer-zero testing |
| J4 | Nominate an AWS/infra escalation contact to cover the Terraform/ECR surface |
| J5 | Confirm commercial/onboarding logistics — not covered on the call |

---

## 7. Questions to raise on the next call

1. Where does the peer benchmark data come from, and who owns it?
2. Five or six assessment domains — and what is the maturity scoring model?
3. Deterministic question lists for MVP — at what point (and on what trigger) does it become agentic?
4. Who are the respondents' identities and how do we authenticate external executives?
5. What are the data retention, residency and confidentiality rules for interview transcripts and voice recordings?
6. What does "done" look like at week five — which of the ~20 stories are MVP-blocking vs deferrable?
7. Is there any test coverage or evaluation harness in the POC today, or does that start from zero?
8. Who is the decision-maker when scope and the five-week date collide?

## 9. Links
- [project repo](https://partner-github.dxc.com/SAM-Prime-X/ai-readiness-diagnostic)

## 10. Contacts
- [Alex Schick](mailto://alex.schick@dxc.com)
- [Shawn Rajguru](mailto://shawn.rajguru@dxc.com)
