# AdvisoryX — Work Session: Scope Alignment, Authorization Model, Roadmap Demand

**Date:** Wednesday, 2026-08-05, 15:32 — 1h 02m
**Participants:** Chris Bryson (DXC — senior stakeholder / product authority), Alex Schick (Scrum Master / BA), Denis Morozov (lead developer / architect), Shawn Rajguru (DXC — project lead, built the POC), Robb Shally (one attributed line, 5:13: *"Yep, sure does"*)
**Absent, referenced throughout:** Andre Milhomem (owner of **Catalyst** / **Access AI**)
**Referenced but not present:** Dan and Ramnath (executive sponsors — the audience for the roadmap Chris is asking for)
**Purpose:** Confirm everyone is aligned on objectives before building. Chris's framing: *"we don't want to do the wrong thing quickly."* In practice the session covered the phase-one/phase-two picture, Denis's authorization model, data-governance and legal exposure, the deterministic-vs-dynamic interview question, and a demand for a roadmap.

> **Transcript note.** Unlike 3 Aug, **this export appears continuous** — timestamps run 0:03 to 1:01:54 without gaps. Nothing below is reconstructed across missing windows.
>
> ASR artifacts are frequent and resolved silently where unambiguous: *"on Tropic"* = **Anthropic**, *"11 labs"* = **ElevenLabs**, *"entry ID"* / *"delivery ID"* = **Entra ID** / **Delivery ID**, *"cloud code"* = **Claude Code**, *"Andreas"* = **Andre**, *"Ramanov"* = **Ramnath**, *"funeral of interest"* = **funnel**, *"Netherland"* = *"rather than"*, *"air dot catalyst one"* = a `catalyst1` subdomain, *"sturdy scoring"* = *"steady/strict scoring."* Unresolved: **"APR process"** (Chris, 17:45 — the stage-two engagement is meant, but the acronym is not established anywhere in the documentation and should be confirmed); the interjections *"Blue."*, *"Patients."*, *"Yes, no, baby."*, *"Gupta."*, *"Behm."*, *"R."* are noise.
>
> **Cadence note.** The agreed cadence is Tue + Thu 15:00. This was a Wednesday, following sessions on Mon 3 Aug and Tue 4 Aug, with another agreed for Thu 6 Aug. Meetings are now effectively daily. Nobody remarked on it.

---

## 1. Executive summary

A scope-and-alignment session rather than a delivery review. Five things of consequence happened.

**Chris expanded the architectural target well beyond phase one — and it is a coherent expansion, not scope creep for its own sake.** The direction: treat the **AI interview agent as generic and objective-driven**. Give the same agent a different context or objective document and it derives a different question set, working backwards from the output it must produce to the inputs it needs. The diagnostic is then one instantiation; stage-two discovery across five-plus stakeholder personas is another. A **second, separate agent** then maps individual interviews together — identifying overlaps, conflicts needing resolution, and gaps still needing data. Denis confirmed this matches the approach he is already taking, and gave the concrete case: compare what a CFO said against what an accountant in the same firm said, and surface the difference. This is the most important content of the meeting and it needs to land in the architecture, not just the transcript.

**Denis presented the authorization model, and it silently supersedes the 3 Aug authentication decision.** On 3 Aug the group agreed **username + password for V1**, email MFA for V2, Entra ID for internal and admin roles. What was presented on 5 Aug is **passwordless magic-link for every role, no stored credential of any kind, no second factor, and Entra explicitly deferred** — including for DXC staff. Four roles: `user` / `power_user` client-side, `partner` / `admin` DXC-side, with the deliberate separation that **`admin` cannot read reports at all**. The model is better reasoned than what it replaces and Denis gave sound reasons for it. **But the reversal was never named as a reversal, and nobody registered it as one.** It needs recording as a decision, not left as a document Alex and Shawn were asked to review.

**Chris introduced a requirement that no part of the current design covers: the invitation must come from the client's own executive.** Prior experience is that completion rates depend on a senior client leader saying *"this is important, do it in the next 48 hours"* — not on an email arriving from DXC. Denis correctly identified this as administrative policy rather than architecture, and it is technically compatible with the invitation model, but **there is no mechanism for it and no owner.** Left as *"whatever is the streamlined way to do that."*

**Chris named the deterministic question set as a critical core capability question.** Shawn confirmed the analysis and scoring layers are agentic (with deterministic fallback), but **the questions themselves are a fixed baseline.** Chris: *"any deterministic interview is going to be of limited value… it doesn't really reflect what we're trying to achieve"* — because the product claims questions generated dynamically from role, industry and prior answers. Denis argued for sequencing: close authentication, data governance and the admin panel first, then add dynamic questioning onto a stable foundation. Shawn agreed and Chris accepted. **The question is acknowledged as critical and explicitly deferred without a date.**

**The 19 Aug demo and 21 Aug beta dates were never mentioned, and Chris asked for a timeline as though none exists** — *"is it going to be two weeks, 3 weeks, 10 months?"* Two days after those dates were the operating targets, the deliverable for tomorrow is a roadmap that establishes MVP scope, timeline and resource needs for leadership. Either the dates have quietly lapsed or leadership has not been reset. This needs to be stated out loud.

Also decided: the domain is **`air.dxc.com`** (AIR = *AI Interview*), treated as temporary pending marketing. Also agreed in principle: a **simple cost/usage dashboard in phase one**, and Denis's use of a **Claude Code–based "software factory"** to accelerate delivery.

**What was not discussed at all: the peer benchmark data source, and the Phase 1 security remediation gate.** Both were raised on 3 Aug, both were in Denis's 4 Aug decision list, and neither surfaced. See §14.

---

## 2. Scope framing and the ask to Denis (1:05 – 6:45)

Chris's framing, in order:

- **Get the scope right first.** *"I know there's a lot of interest in us moving quickly… but we don't want to do the wrong thing quickly."*
- **Think about the big picture, then narrow to phase one** — so the MVP is architected to scale into what follows rather than being rebuilt.
- **Current source of truth:** the **PRD**, of which **V5** is described as the latest, and an **MVP scope** document derived as a subset of PRD V5. Chris flagged both are **June-dated** — *"if we need to review and update that, we should do that"* — while still representing the defined scope.
- **The resource and duration figures in the MVP build-out are estimates.** Chris asked Denis directly to assess: given the scope, what will it actually take, and **do you need more help?**
- **The Catalyst question, restated:** which of the existing assets, tools and "infrastructure" Andre's team built around Catalyst can accelerate this — or do we build some things standalone in the name of time and **realign later**? Chris was explicit that he does not know the answer and wants Denis and Andre to determine the technical path. *"We do want to merge these together, but I don't know whether that's the first step or maybe a next step."*

Chris pressed for confirmation of understanding before proceeding, noting Denis is *"the guy on the hot seat… the lead developer architect on this,"* and invited escalation: clear goals, additional resources, systems people, *"big piles of cash, whatever you need."* Also named the pressure honestly — *"a lot of executive… support and attention, but you can interpret that to be whatever you want it to be. Pressure is another maybe less kind way of saying it."*

Denis's response set the tone for the rest of the session: *"we don't need to get things done quickly… we have to have things done properly because otherwise it's going to bite us on the next phase."* Chris agreed twice over — *"go as fast as you can, not as fast as you can't."*

Shawn confirmed alignment between Denis and Andre on the MVP scope items being stood up (5:15).

> **Note.** PRD V5 and the derived MVP scope document are **not in the repository** — `docs/product/` holds the five June-dated companion specifications, not the PRD. If PRD V5 is authoritative for scope, it needs a location the team can cite. This matters more now that Chris has flagged it as possibly stale.

---

## 3. The bigger picture — and the architectural direction that follows from it (8:03 – 18:45)

Chris shared the process deck. The shape:

### Stage 1 — the diagnostic (current MVP; *"our foot in the door, their foot in our door"*)
| Step | Content |
|---|---|
| 1 | The **interview**, with immediate results generated from it |
| 2 | A **richer version two** — the interview findings augmented with additional research and context: other KPIs and library assets applied against the client's industry, the client's role, and where they are |

### Stage 2 — the paid deeper assessment engagement (*"that's really where we're trying to go"*)
| Component | Content |
|---|---|
| **Data mining** | Empirical data from client systems, to support hypotheses, understandings and ultimately findings |
| **AI-enabled discovery** | Multi-persona interviewing — the deck says six personas, Chris said *"there's probably X number of them"* |

Personas Chris enumerated: the **executive view**, the **line of business / person actually doing the work**, their **management chain**, **IT**, and **risk and compliance** — *"all these different kind of personas or perspectives"* on whatever workflows or use cases are under analysis.

### The architectural direction (14:00 – 15:31) — the most important content of the meeting

> *"That AI interview agent is generic. And if we can provide the agent with a context or an objective for that particular interview… The same agent can take that different objective, come up with a different set of questions, and formulate based on what it knows it needs to get as an output, figure out what… inputs it needs from whoever it's talking to."*

Three properties Chris is asking for:

1. **The interview process is consistent; the objective is parameterised.** The diagnostic's objective is the maturity assessment. Stage-two discovery has a different persona, a different intent, a different output. Chris was careful not to over-specify the mechanism — *"I don't want to presume it's just simply a document, but a different objective."*
2. **Output-driven question derivation.** The agent reasons backwards from the output it must produce to the inputs it needs from the person in front of it.
3. **A separate synthesis agent.** Takes all individual interviews, **maps them together, identifies overlaps, identifies conflicts that need resolving, and identifies gaps where more data is still needed.**

*"I think we need to think about how we architect this so that it's more modular, so that it's dynamic and we can use this interview capability in a variety of contexts based on how we give the agent objectives."*

### Denis's confirmation and extension (15:31 – 17:31)

Denis said this matches the approach already in flight, and characterised the current state precisely:

- **There is a "rigid core"** — Shawn's work: the agent harness for textual and voice interviews, combining into the database. Denis credited it twice, unprompted (*"Shawn did the perfect work"*).
- **What is missing is the scaffolding around it** — starting with the authentication/authorization gap, and the ability to reuse collected interviews and data to build something new.
- **The concrete cross-interview case:** interviews exist from a CFO; the accountant in the same firm is then interviewed; the agent compares the two and **surfaces the difference.** *"Okay, you think the process goes that way, but in reality the process looks different"* — because of corporate rules or established procedures.

### Chris's extension: cross-use-case stitching (17:32 – 18:45)

Beyond stitching interviews within one use case, stitch **across** use cases to an **organisation-wide process map**, because *"there's going to be a lot of cross-functional value"* and pieces of one use case overlap or conflict with another.

> *"That's the ultimate perfect goal for this — not just, as Robb likes to talk about, how do we speed up an existing process, but how do we reinvent processes? How do we go across multiple processes and maybe eliminate processes?"*

With the commercial rationale: *"what we found working with clients is they can't necessarily imagine this. So we need to get the understanding and then we need to help bring the ideas around how this could be optimized."*

---

## 4. The 15-minute challenge and the single-stakeholder problem (8:23 – 15:31)

Raised by Chris as a value-of-the-product concern, and it is the sharpest unresolved product tension in the meeting.

- **Ramnath's feedback on seeing the presentation: *"can we make it 15 minutes? 30 is too much."***
- **Chris's counter-position:** the product assesses maturity across six dimensions. *"How much information can we get in 15 minutes? Can we get the information to provide a meaningful assessment or diagnostic in only 15 minutes? **My gut tells me no.** Maybe we'll be surprised. **I'm not even sure 30 minutes is enough.**"*
- **And the larger version of the same doubt:** *"as I thought about this, **I'm not even sure a single stakeholder is enough.** We might need multiple stakeholders to make the assessment of enough depth and value to be meaningful."*
- **The framing he wants kept in view:** *"we need to really keep in mind the goal first, and that is to provide an assessment that is of value. If it's not of value, then it's just a waste of time altogether."*
- **The reframed MVP question:** *"what's the **minimum viable information** that we need to be able to produce a meaningful result output to a client?"*
- **Not a stop order:** *"I'm not saying we need to stop what we're doing here with a single interviewer."* The suggested resolution is progressive enrichment — *"we give them something intermediate that's of some value, but gets richer over time with more people."*

> **Assessment.** This collides directly with what the voice agent currently tells respondents — *"about 10 questions"*, *"most conversations run about 20 to 25 minutes"* — and with the 20-question specification in `companion_01_questionnaire_specification.md`. Three positions are now live simultaneously: **15 minutes** (executive sponsor), **20–25 minutes** (what the agent says today), and **more than 30 minutes plus multiple stakeholders** (the product authority's own judgment). No decision was taken. This is an unresolved product definition, not a UI detail, and it determines the question pool, the scorecard's defensibility and the completion rate.

---

## 5. The authorization model as presented (18:46 – 29:34, 36:12 – 37:00)

Denis walked the group through `architecture/authorization_model_phase1.md` (dated 4 Aug).

### Identity
- **Passwordless. Server-side session model.** *"We don't store any credentials at all… all we need is user email."* Confirm the email, send a **magic link** on every authentication. The session lives for a period, then disappears.
- **Rationale:** *"this way we avoid all secrets storage and hashes."*
- **Precedent cited:** Anthropic's own console — *"I don't need to know even my password… I simply post my email and they send a magic link back."* Denis characterised it as *"industry proven."*
- **Anti-abuse property:** links are only ever sent to addresses already registered and confirmed in the system. *"If I decided to put my own email — no, it won't work."*
- **Token lifecycle** was written up in detail; Denis flagged it as technical and did not walk it in the meeting.

### The four roles
| Role | Side | What it can do |
|---|---|---|
| `user` | Client | Submit an assessment; read **own** reports. Most restricted category |
| `power_user` | Client | As `user`, plus **read all reports across their organization** — the CEO-visibility case, *"to see who told what"* |
| `partner` | DXC | Owns organizations; **approves and sends back reports**; adds users; promotes `user` → `power_user` |
| `admin` | DXC | Manages organizations and partners — and **cannot read reports** |

Two deliberate design positions Denis called out:

1. **`power_user` cannot add users.** Stated as *"my initial judgment"* and explicitly open — *"it's discussionable, of course."* The reason is commercial control: *"I would like to keep it controlled from our side… who we are going to add to assessment, and not expose this capability to the client side."*
2. **`admin` has no report access at all.** *"A strong, strong decision… admin is just admin. They cannot read reports, cancel reports or send approvals. Only partner can do that."* Rationale is separation of duties **and legal posture** — *"this way we can have a clear separation of roles on our side and from a legal perspective as well. We claim only what we do and nothing more."*

### The invitation flow as drawn
1. **Partner uploads a CSV or Excel sheet** of users — full names, emails, positions, roles, organization — *or* enters them one at a time on a manual back-office form.
2. **The diagnostic API performs row-level validation.**
3. **Invitations are issued** and the mail sender delivers them to the client mailboxes.
4. **The client opens the link and completes a "registration" form** — which Denis noted is a misleading term, since the partner has already supplied names, emails and positions. *"What we do here is just confirming that invitation sent and invitation received"* — plus the fact that the user clicked.
5. **The invitee proceeds to the assessment.**
6. **Returning later:** go to the site, click login, enter the email, receive a fresh magic link.

**Chris's challenge (25:14):** *"is a spreadsheet the right way to collect this data? Would a web form be easier?"* Denis's answer: for office users, Excel is the tool they already know and can simply upload — but the manual form exists too, and *"I don't expect that on the first stage we have dozens or even hundreds of accounts… maybe it's one or two people, so they can do it manually."* Both paths stay; the manual form is the likely first-stage default.

### Funnel telemetry — a design output, not just an implementation detail
Denis highlighted this as *"the most interesting part"*: the model makes the acquisition funnel measurable — **invitations sent → email confirmed → assessment completed.** *"This way we form kind of telemetry or stats which can be proven ground for our further movements… maybe we are wrong and we need a different approach to invite users, or a different approach to ask them questions."*

### Entra ID deliberately deferred (32:17 – 37:00)
- *"During the pretty harsh schedule we have, I would like to keep things as simple as possible. That's why I don't even think about using Entra ID, Delivery ID, whatever we have on our side… it definitely will complicate the whole solution as of now."*
- **Phase two is agreed in principle:** *"if we have more time, we can switch to use Entra ID."*
- **And the schema is additive-ready:** *"the proposed schema easily absorbs a new authorization mechanism for our own people — partners and admins."*
- Chris assented in the moment (*"Yeah, yeah, yeah. Yep."*) without engaging the substance.

### The ask
Denis asked **Alex and Shawn to review and approve the document** so he can start closing the authorization gap, and offered to circulate the link to the group. He stated he could **start implementation the same day** if the group agrees on the email-based approach.

> ### ⚠ This supersedes the 3 Aug authentication decision, and nobody said so
>
> | | Agreed 3 Aug | Presented 5 Aug |
> |---|---|---|
> | V1 credential | **Username + password** | **None — magic link only** |
> | Second factor | Email MFA in V2 | **None for any role**; an email code is explicitly rejected as *not* an independent factor when the mailbox is already the first factor |
> | Internal / admin identity | **Entra ID** | **Same magic link as clients**; Entra deferred |
> | Delivery ID / Okta | Dropped | Dropped *(unchanged)* |
> | No client self-provisioning | Yes | Yes *(unchanged, and hardened — `power_user` cannot invite either)* |
>
> The new model is the better-reasoned of the two, and the email-code argument in §1.1 of the specification is correct. **The problem is procedural, not technical:** a decision the group made on Monday was replaced by Wednesday without being flagged as a replacement, and the two people asked to approve it were asked to approve a *document*, not a *change*. Andre — who argued the 3 Aug position in detail and recommended the email-MFA path with a specific SMTP implementation route — **was not on this call and does not know.** Record it as a decision, state what it supersedes, and tell Andre.
>
> Note also that **single-factor cross-organization access** (`partner` and `admin` read across orgs on the strength of one mailbox) is an accepted risk in the specification, logged there as open point B. It has not been accepted by anyone outside the document.

---

## 6. New requirement — the invitation must come from the client's executive (29:34 – 32:17)

Chris raised this from prior client experience, and it is a genuine addition to the design:

> *"What we found is people are going to do it… much more if it comes from like, we had it sent from their CEO or from a president. A senior leader says, this is a program we're doing, it's important that we do this, and we want you to complete this assessment in the next 48 hours."*

> *"We need a mechanism where the client leader, the client executive, is telling their own people to do it. **They're not just getting something from DXC.**"*

Positions in the discussion:
- **Chris:** either the client executive distributes the link, or *"maybe it's just a message saying, expect an email from DXC inviting you to this assessment, it's critical that you do that."* Also framed the cost of getting it wrong: *"the client is going to be having to wait to get their people to do this… just doing something from DXC is not likely to be completed as well as something that comes from their own executive."*
- **Denis:** *"we actually right now drift into administrative policies rather than technical discussion"* — and confirmed it is compatible with the partner-controlled invitation model. *"This is absolutely controllable."*
- **Shawn:** client partners already hold the relationship and can have the conversation directly — *"they know the emails, they have the interaction with them."*

**Outcome:** agreed as necessary, **left with no mechanism, no owner, and no story.** Chris's own summary was *"whatever is the streamlined way to do that."*

> **Assessment.** Denis is right that the *policy* is administrative, but the *mechanism* is not free. It plausibly requires: partner-facing template text for the executive to send, a sequenced pre-announcement, invitation timing that follows the executive's message rather than the CSV upload, and a deadline the system can express and chase. On current evidence none of that exists in the invitation flow, and completion rate is the metric the funnel telemetry in §5 is being built to measure.

---

## 7. Data governance and the legal questions Denis escalated (32:37 – 36:12)

Denis named data governance as one of two large pieces of current work, and escalated three legal exposures **to the stakeholders explicitly** — *"a real question to stakeholders."*

| # | Exposure | As stated |
|---|---|---|
| 1 | **ElevenLabs recording retention** | *"How are we going to handle legal questions about, for example, ElevenLabs — do they store recordings or not?"* |
| 2 | **Sensitive disclosure in the interview itself** | *"People are going to tell maybe not convenient statements about the processes, or simply can expose business sensitive information as a part of this assessment. We have to make sure that we handle this data carefully."* |
| 3 | **GDPR right to erasure** | For European clients: *"we should not just mark records as deleted in our database. We definitely should delete those records from the database."* Plus accidental PII in transcripts |

Denis's reason for pressing: *"this had bitten me in the past."*

**Chris endorsed it without qualification (35:33):**
> *"That's an important one… Before you can get this off the ground, you've got to get it past their compliance and security people, and they're going to want to understand what do you do with the data, how do we protect it, how is it secured."*

**And committed to a concrete artefact:** Chris will assemble a file of what DXC had to produce and work through with **another client on a similar engagement**, as *"a starting point for requirements."*

Denis also flagged that the data-governance work is what unblocks the cross-interview capability from §3 — the current data model has *"a plain list [of interviews], and that list doesn't link to itself… we need to parse every record to find their specific interview related to the same company."* Versioning per interview and organization-level linkage are prerequisites for Chris's stage-two vision, not separate nice-to-haves.

Denis expected to finish the data governance architecture **the same day**, then start implementation with **authentication first**.

---

## 8. Deterministic vs dynamic questions — the critical capability question (39:50 – 47:38)

Alex opened it (41:00): is the big challenge *"changing it from the deterministic demo that it currently is to an agentic process"*?

### What the system actually does today
- **Denis:** scoring is *"a very algorithmic model"* — deterministic. AI is used *"just as a translator of dry numbers to something which users can consume."* The report arrives practically immediately after the user responds, with **no review stage**; the `partner` role is what introduces one. *"Apart from that, we don't use the model for anything else"* — ElevenLabs excluded as a third-party ingest.
- **Shawn's correction (44:40):** *"right now it is agentic. It's not just deterministic. It actually falls back to deterministic when there's an issue with the agents, but it is firing right now across not just the scoring, but also in the actual analysis."*
- **Reconciled:** deterministic scoring, agentic narrative generation over those scores, deterministic fallback on agent failure. Both parties agreed this is what they each meant.

### Chris's actual question (45:27)
> *"Are the questions themselves deterministic, or are those objectively derived… and then based on the answers the client gives, it's trying to fill in the blanks — trying to either dig deeper or move on to different topics dynamically?"*

**Answer from both Denis and Shawn: the questions are a fixed baseline. Deterministic.**

### Chris's position (46:06 – 46:56)
> *"I think that is a fundamental question that we need to address… **any deterministic interview is going to be of limited value.** And it doesn't really reflect what we're trying to achieve. **We're saying that it's dynamically generated based on the role, of the industry and the company, and the answers they give.**… I think it's a critical core question in the capability of what we're doing. If it's too complex for us to be able to do in phase one, maybe so be it, but I think it's a critical question we need to get an answer to."*

### The agreed sequencing (46:56 – 47:38)
Denis: **fix the gaps first, then inject dynamic questioning.** *"We have a rigid core… now we have to make it mature, and then we can proceed with agentic questions based on user responses or even the user's company responses, to make it more sophisticated and context enriched."* Shawn: *"Agreed."* Chris: *"Okay."*

> **Assessment.** The sequencing argument is sound — dynamic question generation on top of an unversioned, untenanted, unauthenticated data layer would be built twice. But note precisely what state this leaves: **a capability the product's own claims depend on is acknowledged as critical, agreed to be deferred, and has no date, no owner and no acceptance criteria.** It also directly conflicts with §4 — a 15-minute interview is far more plausible with adaptive questioning than with a fixed pool, so the duration decision and the dynamic-questions decision are coupled and are being taken separately.

---

## 9. The roadmap demand — what tomorrow is actually for (47:42 – 51:36, 1:00:37 – 1:01:49)

This is Chris's principal ask, and the reason the 6 Aug session exists.

> *"We need a plan… a bit of the roadmap of what we're doing for this phase and maybe the next phase, because **we're going to get asked by leadership.**"*

What leadership (**Dan and Ramnath**) will ask:
1. **For the MVP, what's in scope?** What should they expect?
2. **What's the timeline for when we think we can deliver this?**
3. **What resources do we need in order to complete that?**

Chris's shaping constraints:
- **Two horizons only** — immediate scope and the next scope. *"We don't need to go too far out… and then we could just parking lot everything beyond that."*
- Framed against the sponsor's real question: *"when are we going to have something that they can take on TV and tell everybody we have this great thing?"*
- And the resourcing purpose: *"do we need to get you more people? Do we need to get you more resources in other ways — access to systems, tools… so that there's no delays once we try to execute."*

### Denis's "working engine" (49:06 – 50:15)

Chris pushed for a definition and got one:

> *"I would like to have a working engine. And then we can improve it whatever way we want. Because right now we don't have an engine, we have just a core of it."*

| Component | Scope as stated |
|---|---|
| **Authorization** | The magic-link model in §5 |
| **Data management** | The data governance architecture in §7 |
| **Minimal back office** | *"Pretty minimal"* — enough for a partner to enter client people and send invitations. *"That's it. Pretty simple."* |

The completion criterion is the **end-to-end path**: *"email sent, email received, assessment taken. We have this path from beginning to the end accomplished."* Only then: *"we can improve our engines to build questions on the fly, based on the context, based on the previous answers."*

Chris accepted the definition and asked the follow-on question that was **not** answered: *"then what comes after the working engine? What are all the pieces that need to get built in place for phase one for the MVP?"* That list is the roadmap deliverable for 6 Aug.

### The testing and rollout ladder (1:00:37 – 1:01:49)

Chris laid out the sequence he expects, unprompted:

1. **Agents test basic functionality**
2. **Internal users**
3. **Internal IT, using it in the context of their actual jobs** — *"kind of initial, what I'll actually call a beta test"*
4. **Then a client**

The dependency he flagged: *"we can get ahead of it by getting those things lined up. We just need to know, **is it going to be two weeks, 3 weeks, 10 months?** When do we need to get those people in place?"*

> ### ⚠ The 19 Aug / 21 Aug dates were never mentioned
>
> On 3 Aug the operating targets were a **leadership demo ~19 Aug** and a **beta-tester URL ~21 Aug**, inside a 3–4 week total effort. Two days later, the product authority is asking for a timeline from scratch and offering *"two weeks, 3 weeks, 10 months"* as the range. Nobody restated the dates, defended them, or withdrew them.
>
> Either those dates have quietly lapsed — in which case leadership is still holding them and needs resetting — or they are still live, in which case a roadmap produced on 6 Aug has **nine working days** to a demo, against a phase-one scope that grew in this meeting. Both readings require the same action: **say out loud, on the 6 Aug call, whether 19 and 21 Aug are still real.**

---

## 10. Denis's two proposals — both accepted

### 10.1 A cost and usage dashboard in phase one (51:36 – 52:53)

> *"You cannot control something if you don't see the numbers."*

Scope proposed: **tokens spent, reports handled**, and the economics of the project generally. Offered with a genuine question attached — *"or is it too early? It's up to you."*

**Chris: accepted.** *"Even if it's a pretty simple dashboard, I think the idea of having something where we can track those metrics… was a great idea. We can have a simpler first version."*

> This is the second measurement surface added in one meeting, alongside the §5 acquisition funnel. Both are cheap and both are the right instinct. Both are also new phase-one scope and should be sized, not assumed free.

### 10.2 A Claude Code "software factory" for delivery acceleration (52:53 – 56:10)

Denis's framing: *"a collection of engines which write code for you, and they perform review… which can generally speed up the whole process."* Proposed as the vehicle for **closing the authorization gap — "it may be several hours."**

- **On the bottleneck it addresses:** *"the main problem with all this agentic development is that you, as a senior architect or senior developer, become the narrow point of the whole schema, because you need to continuously review what they did, how it fits into requirements. So I implemented a factory which actually does it by itself, and only raises questions when it cannot solve it by itself."*
- *"You cannot compete with an excavator. The excavator always wins."* And: *"this thing simply replaces 5 or 7 developers easily."*
- **Chris asked which platform** — DXC Converge, Cursor, or Claude Code. Denis: **Claude Code based**, used on previous projects and on this one, *"it definitely speeds things up."* Access already in place, including API access.
- **Shawn removed the governance concern:** *"within our organization we all use Claude Code, so I think we're good."*
- **Denis will raise a PR so Shawn can see how it works** in the current environment.
- Chris: *"that's always the fastest — the thing you already have."*

---

## 11. Domain decision — `air.dxc.com` (37:00 – 39:37)

Needed now because **it determines the sending domain for the invitation emails.** Denis reported that per yesterday's conversation with Alex and Andre, **Andre can secure any URL required.**

| Proposal | From | Outcome |
|---|---|---|
| `air.catalyst1…` (Catalyst subdomain) | Denis, opening | Not taken |
| `advisoryx-ai-diagnostic.com` | Shawn | *"That's fine"* but superseded |
| `aiinterview.dxc.com` | Chris | Superseded — *"or something fairly simple"* |
| **`air.dxc.com`** — AIR = **AI Interview** | Denis | **Agreed.** Chris: *"I think that's it. Let's go with that."* Posted in the meeting chat |

Two constraints Chris set:
- **A DXC subdomain**, *"just to keep it in our control."*
- **Expect it to change.** *"Part of this is going to be a little bit marketing. Nobody knows what Catalyst is… marketing's going to get a hold of this and change everything."*

Shawn flagged the durability risk: *"once we register it, it becomes difficult to change."* Denis's position is that it is explicitly temporary — *"we can use it like a temporary."*

> **Note for the record:** two `.dxc.com` name variants appear in the transcript (`air.dxc.com`, and a garbled *"air dxc.com"* / *"AIinterview.dxe.com"*). Confirm the exact string with Andre before the certificate is issued, and remember from 3 Aug that **two environments means two names and two certificates** — QA and production.

---

## 12. Email infrastructure — the concrete blocker, and the resource ask (57:21 – 1:00:22)

**Denis's blocker is information, not effort:**

> *"I definitely need someone who can help me with email infrastructure, because I'm not familiar with what DXC has for developers… **We need to send emails directly from the service** — mailbox is just a part of the problem… I don't know where even to find this information, how it works in DXC. Maybe you can provide me links so I can dig it out."*

And, twice, unambiguously: *"I don't need a developer, I need information."* Chris agreed with the sharper version — *"we need what's in their brains and their documentation."*

**Chris's structural response — and it is the more valuable outcome of this thread:**

> *"I think Andre, or if there's someone on Andre's team that he could get us as **a daily point of contact** — because if it's always Andre, he's a busy guy. Maybe we can get halftime of someone on his team that is familiar with all of what's built there. So if Denis has a question, he can work with that guy and they can work through the details."*

> *"This is just one example, because I think there'll be a bunch of others… someone that knows everything that's been built with Andre and his team, so we don't need to reinvent the wheel."*

**Resolution:** Denis will ping Andre directly (Shawn: *"he's pretty responsive"*), and Alex asked Denis for **a short bullet list of the information needed.** Note that email is on the critical path in a way it was not before: with the passwordless model, **mail is the sole authentication channel for every role** — an unverified sender domain blocks all provisioning and all sign-in, internal accounts included.

---

## 13. Alex's backlog and process updates (39:50 – 41:31, 56:10 – 57:21)

- **New story added, flagged as a priority:** *"architect and create the full user lifecycle"* — the step-zero admin page and user authentication piece.
- **Existing story updated:** architect and create the **data governance process**.
- **Recorded:** Chris to send the previous-client compliance document to Denis, referenced against the data-governance work in *"step three in the back end and the agentic process."*
- **Acknowledged rework:** *"we do know we need to rework some of the work breakdown that we've done over the past week, to augment it and expand it and be able to now include some more of these agentic workflows."*
- **Tomorrow's agenda (6 Aug):** the roadmap on paper; identifying and laying out the next feature requirements; possibly **returning 30 of the 60 minutes to Denis**; and **beta testers** — Shawn has spoken with Robb and *"has a couple people maybe identified in Robb's organization."* Open: who tests, and what the feedback-gathering process looks like. Alex also raised whether to start laying groundwork with other DXC teams sooner.

---

## 14. Analysis — risks and gaps

### New this meeting

**N1 — The 3 Aug authentication decision was replaced without the replacement being named. (High)**
Passwordless-for-all-roles is, on the merits, the better design and the reasoning behind it is sound. The risk is entirely procedural: Alex and Shawn were asked to approve *a document*; nobody said *"this reverses what we agreed on Monday."* Andre, who argued the 3 Aug position in detail and supplied the SMTP implementation route for email MFA, was absent and is unaware. **Write it as a decision record stating what it supersedes, and tell Andre before he builds or advises against the old model.** Also surface, for explicit acceptance outside the document, that `partner` and `admin` hold cross-organization report access on a single factor.

**N2 — Interview duration and stakeholder count now have three incompatible answers. (High)**
15 minutes (Ramnath), 20–25 minutes (what the agent tells respondents today, against a 20-question specification), and *more than 30 minutes plus multiple stakeholders* (Chris's own judgment, stated twice). This is not a preference disagreement; it determines the question pool, whether the six-dimension scorecard is defensible, and completion rates. **It is also coupled to N3** — adaptive questioning is what would make 15 minutes plausible — and the two are being decided separately, in different sessions, by different people.

**N3 — Dynamic question generation is acknowledged critical and deferred with no date, owner or criteria. (High)**
Chris's words: *"any deterministic interview is going to be of limited value… it doesn't really reflect what we're trying to achieve."* The claim already made externally is that questions adapt to role, industry, company and prior answers. The sequencing argument for deferring is legitimate. **What is missing is the artefact: it needs to be a logged, dated roadmap item with acceptance criteria, not an agreed verbal deferral** — otherwise it reappears as a surprise in front of leadership, which is exactly the scenario Chris is preparing for.

**N4 — The client-executive-sourced invitation has no mechanism and no owner. (Medium-high)**
Agreed as necessary by everyone, resolved as *"whatever is the streamlined way to do that."* Needs: template text for the client executive, a pre-announcement step, invitation timing sequenced behind the executive's message, and a deadline the system can express. Directly determines the completion rate that the new funnel telemetry exists to measure. **Owner needed — most plausibly Alex as a story, with Chris supplying the language from prior engagements.**

**N5 — Phase one grew materially in this meeting, and the June scope documents were flagged as possibly stale in the same session. (Medium-high)**
Added or reinforced: the generic objective-driven interview agent, the cross-interview synthesis agent, cross-use-case process mapping, the client-executive invitation flow, the cost/usage dashboard, and the acquisition funnel telemetry. Alex has acknowledged the work breakdown needs reworking. **Meanwhile PRD V5 and the derived MVP scope are June-dated, are not in the repository, and Chris himself said they may need review.** R12 from 3 Aug — label everything MVP / not-MVP at the moment it is raised — applies with more force now. The roadmap due tomorrow is the correct vehicle; it should also settle which document is authoritative for scope and where it lives.

**N6 — The 19 Aug demo and 21 Aug beta dates went unmentioned while a timeline was requested from scratch. (High)**
See §9. *"Is it going to be two weeks, 3 weeks, 10 months?"* is not a question the product authority asks two days after firm dates were set, unless the dates are no longer operative. **Resolve explicitly on 6 Aug.** If they have lapsed, leadership needs resetting; if they are live, the roadmap has nine working days of runway against a grown scope.

**N7 — The peer benchmark was not mentioned in this meeting at all. (High, carried and now overdue)**
Raised 24 Jul (item J2), raised again 3 Aug (R2, J1), listed as decision request #5 in Denis's 4 Aug brief. **Third consecutive session with no owner.** The voice agent still tells respondents they will be compared to *"peer financial services companies of similar scale,"* and the output still renders a score out of 100 and a peer-ranked spider chart with no corpus behind either. This is the item most likely to cause commercial damage and the item receiving the least attention — the pattern is now the risk.

**N8 — The Phase 1 security remediation gate was not discussed. (High, carried)**
Denis's 4 Aug brief asked for it to be approved as a hard gate on public traffic: 12–16 hours of work, against a documented finding that the application is *not suitable for untrusted input* (prompt injection, path traversal, SSRF, email header injection, CORS wildcard). It did not come up. If any beta URL is issued, this is the thing that has to clear first, and **email header injection is now doubly load-bearing** because mail is the sole authentication channel.

**N9 — Of the five decisions Denis requested on 4 Aug, most remain open. (Medium)**
Synchronous-vs-asynchronous delivery: **not discussed** — and it is the decision Denis called the highest-leverage on the list, since it scopes the partner review gate, email delivery, portal links and SLA tracking. Tenant boundary: **partially answered** by the four-role model, though the specific question — can a CFO's findings be disclosed to a CIO without permission — was not put. Retention and residency: **raised again, still unanswered**, now with Chris supplying prior-client material as input. Security remediation: not discussed. Benchmark owner: not discussed. **Two consecutive sessions of asking is a signal about the forum, not about the questions.**

**N10 — Meeting cadence has become daily without a decision. (Low, worth watching)**
Agreed cadence is Tue + Thu 15:00. Actual: Mon 3rd, Tue 4th, Wed 5th, Thu 6th. Alex is already proposing to hand 30 of tomorrow's 60 minutes back to Denis, which is the right instinct — the person who needs to produce the working engine is in alignment meetings daily.

### Carried from 3 Aug — status
| Item | Status after 5 Aug |
|---|---|
| **R1 — HTTPS / DNS critical path** | **Progressed.** Andre can secure the URL; the name is now decided (`air.dxc.com`). Still needs the certificate connected, and **two** names for QA + prod. Not confirmed live |
| **R2 / J1 — Peer benchmark unowned** | **No change. Not mentioned.** See N7 |
| **R3 — Steps 4 and 5 undefined** | **Partially addressed from an unexpected direction.** Denis's `partner` role introduces the review gate that distinguishes them, and Denis noted today's report arrives immediately with no review stage. The product definition of what differs between the two outputs is still unwritten |
| **R4 — Sensitive data handling** | **Escalated properly and endorsed.** Denis raised ElevenLabs retention, disclosure risk and GDPR erasure; Chris agreed it is a gate on client compliance review and committed a prior-client document. **Still no decision on retention, residency or consent text** |
| **R5 — Timeline compression** | **Superseded by something larger.** See N6 |
| **R6 — Catalyst fit decision** | **Loosened, deliberately.** Chris explicitly opened the option to *"do some things standalone in the name of time"* and *"realign those things a little bit down the line"* — and said he does not know whether merging is the first step or a later one. **Still no criteria, no date, and Andre still absent from the conversation** |
| **R8 — Dimensions and question count** | **Worse.** N2 adds a third duration position and a multi-stakeholder question on top of the existing six-vs-seven dimension and 20-vs-95 question discrepancies |
| **R11 — Email MFA external dependency** | **Obsolete as scoped, replaced by a harder dependency.** Email MFA is out; but outbound service mail is now the sole authentication channel for every role, and nobody at DXC has yet told Denis how to send it. See §12 |
| **R12 — Scope accretion** | **Recurred.** See N5 |

### Positive signals
- **The architectural direction and the implementer's instincts converged independently.** Chris described a generic objective-driven interview agent plus a separate cross-interview synthesis agent; Denis had already been designing towards it and produced the CFO-versus-accountant case unprompted. That is a genuinely strong signal for a team four days in.
- **Denis is escalating the right things early, at cost to their own comfort** — legal exposure, GDPR erasure, ElevenLabs retention, and the "we need information not developers" ask — and Chris is receiving all of it well and converting it into commitments.
- **Chris is holding the value question above the delivery question**, including pushing back on the executive sponsor's own 15-minute request. *"If it's not of value, then it's just a waste of time altogether."*
- **The sequencing discipline held under pressure.** Faced with the most interesting problem in the room (dynamic questions), the team chose to finish the foundations first, and the product authority accepted it.
- **The `admin`-cannot-read-reports separation is a mature design instinct**, and Denis tied it to legal posture rather than to convention.
- **Two measurement surfaces were proposed by the implementer, not demanded by management** — the acquisition funnel and the cost dashboard. Teams that instrument themselves voluntarily tend not to need governance imposed later.
- **Shawn's correction on the agentic layers was accurate and taken well in both directions**, and Shawn removed the tooling-governance blocker on Claude Code in one sentence.
- **The domain question went from open to decided in under two minutes**, with the durability risk correctly noted and correctly discounted.

---

## 15. Action items

### Denis Morozov
| # | Action | Due |
|---|---|---|
| D1 | Circulate the **authorization model** link to the whole group, and record it as a **decision that supersedes the 3 Aug username/password + Entra decision** — stating explicitly what changed and why | 6 Aug |
| D2 | Begin **authentication implementation** once approval lands — stated as startable same-day | 5–6 Aug |
| D3 | Finish the **data governance architecture** (was expected same-day), including per-interview versioning and organization linkage — the prerequisite for the cross-interview capability in §3 | 5–6 Aug |
| D4 | Send Alex the **bullet list of email-infrastructure information needed**, and ping Andre directly | 6 Aug |
| D5 | Contribute the engineering half of the **roadmap**: components after the "working engine," sequence, and durations | 6 Aug |
| D6 | State the **resource and access needs** explicitly — Chris asked twice and the roadmap requires it | 6 Aug |
| D7 | Confirm the exact domain string with Andre and request **two certificates** (QA + prod), not one | This week |
| D8 | Raise the **peer benchmark** ownership question for the third time, and the **security Phase 1 gate** — neither was discussed today *(carried: D7 of 3 Aug, item 5 of the 4 Aug brief)* | 6 Aug |
| D9 | Re-put **sync vs async delivery** — the highest-leverage decision on the 4 Aug list, not discussed today | 6 Aug |
| D10 | Raise the **PR demonstrating the software factory** for Shawn | This week |
| D11 | Produce the **Catalyst fit assessment** — now with Chris's explicit permission to build standalone and realign later *(carried: D9 of 3 Aug)* | Propose a date 6 Aug |

### Alex Schick
| # | Action | Due |
|---|---|---|
| A1 | Produce the **roadmap on paper** — MVP scope, timeline, resource needs, two horizons, parking lot beyond. Chris's primary ask | 6 Aug |
| A2 | **Rework the work breakdown** to absorb the agentic workflow scope added today *(already acknowledged on the call)* | This week |
| A3 | Log as stories: **full user lifecycle / step-zero admin page** (already added), **data governance process** (already updated), **client-executive-sourced invitation** (N4), **cost/usage dashboard**, **funnel telemetry** | 6 Aug |
| A4 | Log **dynamic question generation** as a dated roadmap item with acceptance criteria — not a verbal deferral (N3) | 6 Aug |
| A5 | Get an explicit answer on whether **19 Aug demo / 21 Aug beta** are still live (N6) | 6 Aug |
| A6 | Pin the **interview duration and stakeholder count** decision — 15 vs 20–25 vs 30+, single vs multiple (N2) | This week |
| A7 | Confirm **where PRD V5 and the MVP scope document live**, and whether they need updating as Chris suggested | This week |
| A8 | Define the **beta-tester group and feedback-gathering process** with Shawn and Robb | 6 Aug |
| A9 | Carried: **step 4 vs step 5 output definition** and the **curated report template** *(A2, A4 of 3 Aug — still open)* | This week |

### Chris Bryson
| # | Action | Due |
|---|---|---|
| C1 | Send Denis the **prior-client compliance and data-handling file** as a requirements starting point *(committed on the call)* | This week |
| C2 | Confirm whether **19 Aug / 21 Aug** stand, and reset leadership expectations if they do not (N6) | 6 Aug |
| C3 | Secure a **named half-time point of contact from Andre's team** for Denis — daily access to what Catalyst/Access AI already solved | This week |
| C4 | Supply the **client-executive invitation language** from prior engagements, so N4 becomes buildable | This week |
| C5 | Tell **Andre** two things directly: that authentication is now passwordless magic-link (superseding the 3 Aug position Andre argued), and the Catalyst *product-need-wins* position *(C2 of 3 Aug, still open)* | ASAP |
| C6 | Take a position on **interview duration and multiple stakeholders**, including back to Ramnath on the 15-minute request (N2) | This week |
| C7 | Confirm whether **PRD V5 / MVP scope** need reissuing, having flagged the June date | This week |

### Shawn Rajguru
| # | Action | Due |
|---|---|---|
| S1 | **Review and approve** the authorization model document *(explicitly asked)* | 6 Aug |
| S2 | Review Denis's **software factory PR** | This week |
| S3 | Confirm with **Robb** which people in Robb's organization are beta testers | 6 Aug |
| S4 | Ping **Andre** on email infrastructure as backup to Denis | 6 Aug |
| S5 | State what the **peer-benchmark comparison is derived from today** *(S5 of 3 Aug, still open)* | 6 Aug |
| S6 | Confirm which layers are agentic vs deterministic **in writing**, so the record settles — today's exchange resolved it verbally only | This week |

### Andre Milhomem *(absent — needs briefing)*
| # | Action | Due |
|---|---|---|
| N1 | Secure **`air.dxc.com`** — plus a second name for QA — and connect the existing certificate | This week |
| N2 | Provide the **email-from-service** information Denis needs, or name someone on the team who holds it | This week |
| N3 | Nominate a **daily point of contact** for Denis (Chris's ask, §12) | This week |
| N4 | Be briefed that authentication is now **passwordless magic-link for all roles**, superseding the 3 Aug position — and respond if there is an objection | ASAP |

### Robb Shally
| # | Action | Due |
|---|---|---|
| B1 | Identify **beta testers** from the organization, with Shawn | 6 Aug |

### Joint / unassigned
| # | Action |
|---|---|
| J1 | **Name an owner and data source for the peer benchmark.** Carried from 24 Jul, unmentioned on 5 Aug. Third session |
| J2 | **Approve or reject the Phase 1 security remediation as a gate on public traffic** (N8) |
| J3 | **Decide sync vs async V1 delivery** (N9) — scopes the partner gate, email delivery, portal links, SLA tracking |
| J4 | **Decide retention, residency and consent text**, provisionally if necessary, and engage Legal in parallel |
| J5 | **Set criteria and a date for the Catalyst decision** — now loosened by Chris's standalone-then-realign permission, which makes drift more likely, not less |
| J6 | **Decide whether a `power_user` may invite users** — Denis's *"initial judgment"* is no, flagged as *"discussionable"* |
| J7 | Accept, outside the specification, the **single-factor cross-organization access** held by `partner` and `admin` |

---

## 16. Questions to raise on the 6 Aug call

1. **Are 19 Aug and 21 Aug still the dates?** If not, what replaces them, and who tells Dan and Ramnath?
2. **Is the authorization model approved** — and is everyone aware it replaces Monday's username/password + Entra decision? Does Andre get a say before implementation starts?
3. **Where does the peer benchmark data come from, and who owns it?** Asked 24 Jul, 3 Aug, and in the 4 Aug brief. The agent is still promising peer comparison to respondents.
4. **Is V1 delivery synchronous or asynchronous?** Unanswered across two sessions, and it scopes the partner review gate, email delivery and SLA tracking.
5. **How long is the interview, and how many stakeholders?** 15 minutes as Ramnath asked, 20–25 as the agent says today, or 30+ with multiple stakeholders as Chris suspects is actually needed?
6. **Does the Phase 1 security remediation get approved as a gate on public traffic?** Beta testers are being identified now.
7. **When does dynamic question generation happen, and what does "done" look like?** Agreed critical, agreed deferred, undated.
8. **What is the mechanism for the client executive sending or pre-announcing the invitation**, and who owns it?
9. **Retention, residency and consent** — what is the provisional answer we build against this week, and when is Legal engaged?
10. **Who is the named daily contact from Andre's team**, and by when?
11. **Where do PRD V5 and the MVP scope document live, and are they being reissued** now that the June date has been flagged?
12. **Can a `power_user` invite users?** And, the version not yet asked: can a CFO's findings be shown to a CIO in the same organization without permission?
13. **Is the cost/usage dashboard in phase-one scope formally**, and at what size?

---

## 17. Decisions recorded

| # | Decision | Standing |
|---|---|---|
| 1 | **Domain: `air.dxc.com`** (AIR = AI Interview), a DXC subdomain, explicitly temporary pending marketing | Agreed by Chris on the call |
| 2 | **Passwordless magic-link authentication for all four roles; no stored credentials; no second factor; Entra ID deferred to phase two** | Presented and unopposed — but **pending formal approval from Alex and Shawn**, and **supersedes the 3 Aug decision without that being stated** |
| 3 | **Four roles:** `user`, `power_user` (client); `partner`, `admin` (DXC). **`admin` cannot read reports** — separation of duty and legal posture | Presented, unopposed, same approval caveat |
| 4 | **Build order: authentication → data governance → minimal admin panel**, reaching an end-to-end path (email sent → received → assessment taken) before adding dynamic questioning | Agreed by Denis, Shawn and Chris |
| 5 | **Dynamic question generation deferred past the "working engine"** — acknowledged as a critical capability question | Agreed verbally; no date or criteria |
| 6 | **A simple cost/usage dashboard is in phase one** — tokens spent, reports handled | Agreed by Chris |
| 7 | **Claude Code–based "software factory" approved for use**, starting with the authorization gap | Chris receptive; Shawn confirmed org-wide use, no restriction |
| 8 | **Invitations must originate from or be pre-announced by the client's own executive** | Agreed as necessary; **no mechanism, no owner** |
| 9 | **Both CSV/Excel upload and a manual entry form** for invitee provisioning; manual likely the first-stage default | Agreed after Chris's challenge |

---

## 18. Links
- [project repo](https://partner-github.dxc.com/SAM-Prime-X/ai-readiness-diagnostic)
- [authorization_model_phase1.md](../architecture/authorization_model_phase1.md) — the document presented in §5
- [architecture_topics.md](../architecture/architecture_topics.md) — the ten-topic assessment behind the 4 Aug brief
- [2026-08-04_architecture_review_brief.md](2026-08-04_architecture_review_brief.md) — the five decisions requested, most still open
- [2026-08-03_meeting_summary.md](2026-08-03_meeting_summary.md) — the authentication decision now superseded
- `air.dxc.com` — posted in the meeting chat; not yet secured
- PRD **V5** and the derived **MVP scope** — *referenced by Chris as the current source of truth; June-dated; location not stated and not in this repository*

## 19. Contacts
- [Alex Schick](mailto:alex.schick@dxc.com)
- [Shawn Rajguru](mailto:shawn.rajguru@dxc.com)
- [Denis Morozov](mailto:denis.morozov@dxc.com)
- Chris Bryson — *address not captured*
- Andre Milhomem — *address not captured*
- Robb Shally — *address not captured*
- Dan, Ramnath — *executive sponsors; surnames and addresses not captured*
