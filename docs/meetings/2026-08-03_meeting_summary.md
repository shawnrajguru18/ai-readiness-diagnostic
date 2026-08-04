# AdvisoryX — Kickoff / Process & Architecture Review

**Date:** Monday, 2026-08-03
**Participants:** Chris Bryson (DXC — senior stakeholder / product authority), Shawn Rajguru (DXC — project lead, built the POC), Alex Schick (Scrum Master / BA), Andre Milhomem (owner of **Catalyst** / **Access AI** — left at ~1:00), Denis Morozov (developer)
**Invited, no attributed lines:** Robb *(Alex noted at 3:07 that Robb accepted and was "showing presenting"; Alex addresses "Chris, Shawn, or Robb" at 1:01:04)*
**Purpose:** Kickoff. Confirm scope and timeline, walk the end-to-end process, demo the current build, resolve authentication and hosting, agree cadence.

> **Transcript caveat.** The export is partial — roughly 20 of 63 minutes are missing across five gaps: **0:00–2:58** (open), **16:26–18:17**, **28:19–35:19**, **39:27–42:44**, **51:11–57:48**. Nothing below is inferred about those windows; where a thread is cut off mid-answer it is marked. Notably, Chris's question *"that output — that's a static output, correct?"* (51:11) falls straight into a gap and **its answer is not in the record**. Two garbled entries ("Behm." 3:06, "Gulshan." 1:03:31) are unresolved.

---

## 1. Executive summary

Kickoff for the AI diagnostic build. Shawn framed it as a **3–4 week effort: ~2 weeks development, ~2 weeks testing and fixes**, folding later into **Access AI / Converge**. Alex has the scope broken into 8–9 categories and 20–30 backlog tasks, targeting a **leadership demo ~19 Aug** and a **beta-tester URL ~21 Aug**.

Three substantive outcomes:

**Authentication got largely decided, and deliberately de-scoped.** Andre laid out the DXC identity landscape in detail and argued strongly for simplicity: **username + password for V1**, email-based MFA for V2, and **explicitly drop Delivery ID / Okta** unless the app later integrates with a DXC system like Salesforce. Chris added the commercial constraint that settles the client side: **no client self-provisioning.** DXC controls who enters the system — a DXC employee uploads names and emails, and the system issues time-limited registration invitations. Chris also proposed **Entra ID for internal/admin roles** with simple auth only for the interview-taker. This closes an open item carried from 24 Jul.

**HTTPS is the critical path, and it is closer than feared.** The browser microphone only works over HTTPS on a real DNS name; the app is currently served **from a raw IP**. Alex reported that **Andre already has both a URL and a certificate** — they simply have not been connected. Denis added a requirement that had not been on the table: **at least two environments, QA and production**, plus the point that a secured endpoint is also budget protection against outside abuse.

**Chris set two architectural guardrails.** First, this is *phase one of a roadmap* — architect for the bigger picture, "so we're not painting ourselves into a corner." Second, at the very end and with Andre already gone: **Catalyst is welcome if it fits, but the product must not be reverse-engineered around it.** Shawn confirmed he is working in a separate, self-contained repo and that integration is a later decision.

The demo ran and the voice interview worked end-to-end. **The most significant unowned risk it exposed: the report promises peer benchmarking against "financial services companies of similar scale," and there is still no benchmark data source** — Shawn described training on past data and industry reports as "iteration part 2."

Cadence agreed: **Tuesday and Thursday at 15:00, one hour, for four weeks.**

---

## 2. Scope, timeline and targets

| Item | As stated |
|---|---|
| Total effort | **3–4 weeks max** — ~2 weeks development, ~2 weeks testing and fixes |
| Scope structure | 8–9 categories; **20–30 backlog tasks** identified by Alex |
| Leadership demo | **~19 Aug** |
| Beta-tester URL | **~21 Aug** |
| Working cadence | **Tue + Thu, 15:00, 1 hour, for 4 weeks** |
| Long-term home | Folds into **Access AI** / **Converge** (next-generation platform) |
| Current state | MVP "up and running" from Shawn's build; served from a raw IP address |

**Note a compression against 24 Jul.** The prior session framed this as ~2.5–3 weeks development with production MVP at week five. Today's framing is ~2 weeks development with a leadership demo on 19 Aug. With Denis having started 30 Jul, a two-week development window closes ~13 Aug — leaving under a week to the demo. Worth confirming whether the dates moved or the development window narrowed.

---

## 3. The end-to-end process (Alex's five steps)

| Step | Content | Open questions raised |
|---|---|---|
| 1 | **Landing page** — standalone URL, user enters their details | Behind Entra ID? A one-time generated URL (Denis's suggestion)? Or attached to the DXC website front page? *(→ largely resolved in §4)* |
| 2 | **Interview** — voice, adaptive Q&A | — |
| 3 | **Processing** — application/LLM processing of responses | — |
| 4 | **Immediate output** — overview scorecard, report, next steps | What exactly does the step-4 output contain? |
| 5 | **Human-reviewed output** — DXC person reviews within the 24-hour window and sends a fuller version with extra context | **What is the difference between step 4 and step 5?** |

**Chris's ask (11:53):** each step needs written requirements and definition — specifically what step 4 produces and how step 5 differs. This is currently the biggest specification gap.

### Alex's highlighted open backlog questions
- What does the **template for the curated report** look like?
- What is the **workflow once the report goes to the partners**?
- How is **automated follow-up** handled?
- Is there an **additional QA review** step?
- Are results **saved to a database**?
- **How is sensitive client information handled** if a company discloses it? *(raised by Denis; Alex flagged it as one of the important key questions — **not answered on the call**)*

---

## 4. Authentication — the main decision of the meeting

### Andre's briefing on the DXC identity landscape (18:48 – 23:20)

| Path | Applies when | What it costs you |
|---|---|---|
| **Entra / SSO** | App is used by the **CIO organization** | Architecture review, DR review, create a CI, request Entra access, implement Entra |
| **Delivery ID** (built on **Okta**) | App is **delivery**-side — salespeople, customer success managers, delivery staff. *Andre believes this is where the project fits* | Fill in spreadsheets, create an ID on Platform X, request access. **Every user must create their own Delivery ID — nobody at DXC has one by default.** Login flow becomes: extra screen → username/password → Okta → face recognition or code → app |
| **Username + password (+ email MFA)** | Andre's recommendation | Fully self-contained; no dependency on other teams |

**Andre's recommendation:** *"unless this thing is going to be in the future connected to one of the DXC applications such as Salesforce… my suggestion is drop this entire Delivery ID, keep it simple with username and password, one multi-factor authentication."*
- **V1: username and password**, plus a support email for problems.
- **V2: email-based MFA** — code valid 10 minutes, a pattern everyone already knows. He has an article explaining the approach.
- **Implementation path for email MFA:** request a **shared mailbox** via Uptime → configure an **SMTP relay** in the app → the Exchange team grants the account relay access. *"That's the easiest, simple way."*
- Rationale: *"We don't need to complicate all our lives now. We need to make it simpler. We will complicate it later."* Also forward-looking — **customers cannot have a Delivery ID and cannot use DXC's Entra**, so if State of AI is ever exposed to customers, an email-based authenticator is the only thing that already works.

### Chris's constraint — no client self-provisioning (25:41 – 28:19)
- Two distinct processes are needed: **internal access/authentication**, and **how clients are granted access**.
- *"My official thinking is we do not want clients self-authenticating."* From a sales and client-engagement perspective DXC wants to **know who is entering the system** and to have engagement with those people — not have people arrive at a website, answer the questions and collect outputs **without prior DXC engagement**.
- Mechanism: likely **collect names and emails from the client**, then provision them so they receive links.
- Caveated as possibly changing later: *"I could be wrong. We might change that."*

### The agreed model (35:30 – 36:02)
Denis restated it and Chris confirmed *"that sounds right"*:
> A DXC employee (e.g. from marketing) gathers names and email addresses and **uploads them into the system**. The system then knows which address to send the invitation to. The client receives a **time-limited (≈24-hour) registration link**, sets their own password, and takes the interview.

### Chris on internal roles (36:02 – 36:34)
- **Entra ID for internal roles** — admin / super-user — since those are all DXC people.
- **Simple authentication only for the end user** taking the interview.

### Andre's addition — results routed via DXC (24:41 – 25:19)
The result should go to the **DXC person first**, who validates it, sends it to the client, and can create an engagement from it. Generating a secure client link is then trivially in-app: create a secure link, email it, email a code alongside it — *"it's in our control of the app. We don't depend on any of these guys."*

**Assessment:** this is a coherent, low-dependency design that satisfies Chris's commercial constraint and Andre's simplicity constraint at once, and it aligns step 5 of the process flow with the auth model. It should be written up as a decision record and stories this week, before it drifts.

### Related
- Shawn (23:24): end goal is rolling this into **Converge**; clients may already have their own SSO and would reach the app via links.
- Client-side admin tiers (36:34) — client admins wanting to see all interviews, who has taken them and who hasn't. **Explicitly roadmap, not MVP.** Denis: this makes the back office *"more than a CRM system"*; Shawn: *"an enhanced Salesforce."*

---

## 5. Hosting, HTTPS and environments

- **Current state: served from a raw IP address.** Needs DNS — CloudFront or another hosted platform (Shawn, 13:50).
- **Why it blocks everything:** the voice interview uses the **browser microphone**, which only works on an **HTTPS session tied to a real DNS name**. Without it there is no voice flow. Shawn asked for it to be prioritised; he raised it again unprompted in the wrap-up.
- **Good news:** Alex reported (14:13) that **Andre already has a URL and a certificate** — they *"just hadn't been connected yet."* A user story exists; Denis and Andre to connect on it.
- **Denis's requirements (15:22, 16:05):**
  1. **At least two endpoints — QA and production.** *"I don't want to test with production at all."* Needed to iterate while something stays up in production.
  2. **A secured endpoint is also cost control** — it prevents someone outside from *"simply spending all our budgets."*
- The demo itself ran without HTTPS (Shawn, 43:30: *"if this was HTTPS, you'd have to…"*).

---

## 6. The demo — what the product actually does today

Shawn had to check logs for one component that misbehaved; Chris redirected: *"let's just look at the voice anyway, that's the one we're gonna focus on."*

### The voice interview as it ran (43:30 – 48:00)
Opening script: *"Thank you for making time for the DXC Advisory X AI diagnostic. I'll be asking you about **10 questions** covering different aspects of your organization's AI readiness — data, governance, investments you've made, and where you see the value. There are no right or wrong answers… Most conversations run about **20 to 25 minutes**."*

Questions observed, in order:
1. **Data availability** — when someone needs data for a real operational decision, is it there or is there friction?
2. **Data readiness for AI** — can a new AI initiative access and prepare data easily, or does each project need significant engineering?
3. **Governance ownership** — who owns AI risk decisions; who is accountable when something goes wrong?
4. **Governance maturity** — is there a formal framework (policies, risk tiers, approval process), and is it actually used or just documented intent?
5. **Investment portfolio** — mostly experiments and pilots, or AI in production generating measurable value?
6. **Investment trajectory** — next 12 months: increasing, flat, or pulling back to fix foundations?
7. **Leadership alignment** — is the senior team pointing the same direction, or is there genuine debate about pace?
8. **Workforce posture** — curiosity and engagement, or anxiety and resistance?
9. **Value identification** — specific processes with a rough-sized business case, or a conviction that AI matters while still looking for the *where*? *(Shawn: "the question that often tells us the most about where an organization really is")*
10. **Regulatory exposure** — EU AI Act, FCA/PRA guidance for UK financial services, FINRA/SEC disclosure, HIPAA for healthcare data.

Closing promise made to the respondent:
- A **detailed AI readiness scorecard within 24 hours**
- Scored across **the six dimensions we covered**
- **Compared to peer financial services companies of similar scale**
- A specific recommendation for next steps
- Plus **a short memo on two or three AI patterns implementable in the next 90 days**

### The generated output (48:09 – 51:02)
Fires the LLM models off the interview input and produces:
- A **maturity classification** — developing / emerging / leader *(transcript garbled)* — and a **score out of 100 ranked against peers**
- An **executive summary** explaining why that rating was given, across AI investment, governance, etc.
- A **spider chart** across the six maturity areas, ranked against peers *(Shawn again wavered aloud between five and six)*
- **Three high-impact areas** where the client can make immediate impact
- **Recommended next steps** — the conversation-continuation hook; Shawn floated an **MCP call hitting the email server** Andre described
- **90-day quick wins**
- An **opportunity map** — value versus difficulty

Shawn noted the benchmarking could be trained on past data and specific industry reports, but *"a lot of that stuff will probably be… the iteration part 2."*

**Chris's question at 51:11 — "that's a static output, correct?" — falls into a transcript gap. The answer is not in the record and needs re-asking.**

### Avatar vs abstract UI (57:48 – 59:41) — new requirement
- **Denis:** his wife is currently job-hunting and most AI-led interviews use an abstract shape or orb that changes colour — *"it doesn't look creepy… it looks modern enough."*
- **Andre:** found talking to a realistic face genuinely off-putting, especially when it followed up by email afterwards. *"This is creepy."*
- **Chris:** *"some people might be uncomfortable talking to a face and might be more comfortable talking to a bubble."* Wants this captured and **user-tested** to see how people react.
- **Emerging idea:** offer a **choice** — make it the first question. *"Do you want to talk to an avatar, or something more abstract?"*
- Shawn: *"UI UX 101."*

---

## 7. Catalyst, taxonomy, and models

### Chris's guardrail (1:01:58 – 1:02:50) — stated after Andre left
> *"Using Catalyst is fantastic **if we can use it**. But I don't want to force a square peg in a round hole… we can't reverse engineer based on what he has. It really has to fit what this project needs… **we can't start making architectural decisions based on Catalyst instead of what is the product need**."*

Options he left open: use it, **evolve** it, or **build something alongside**. Chris noted the call was recorded so Andre would see it — *"I'm not talking behind his back"* — but **Andre has not responded to this position.**

**Shawn's answer (1:02:59):** he already has *"a separate repo… everything is self-contained in that repo and it's separate altogether."* Integration gets decided once the thing is up and operational.

### Andre's taxonomy-import proposal (37:20 – 39:27)
- Tracked on his **Asana** project as the task **"Create Taxonomy"** import.
- Purpose: load the **client's stack and existing DXC footprint** so that when the system generates use cases it already knows *"here's what we do at this client already."*
- **Data source: an internal SharePoint site** (link posted in the meeting chat). The maintainer keeps the list on SharePoint and pushes it to Salesforce — so **SharePoint is the source of truth for the DXC services taxonomy, not Salesforce.**
- Positioned by Andre as a future feature, not current scope.

### Catalyst access and models
- **Denis provisioned as administrator** on Catalyst — *"you can do everything."* Username is his DXC email address; the initial password was posted **in the meeting chat** and must be changed on first login.
- Models Andre uses on Catalyst: **Opus 4.7** and **GPT-5**. The API keys expose all available models — free choice.
- Andre was blunt about vendor value for money on one of the services in play (*"it's an extortion because it doesn't do the freaking job and takes a lot of money"*) — the specific vendor is in the 16:26–18:17 gap.

---

## 8. Analysis — risks and gaps

### Blocking now
1. **R1 — HTTPS / DNS is the critical path for the core user journey.** No microphone, no voice interview, no product. The pieces reportedly exist (Andre's URL + certificate) but are unconnected, and ownership is *"Denis and Andre will talk"* — too informal for the one thing everything else depends on. **Needs a named owner and a date this week.** Denis's two-environment requirement (QA + prod) should be folded in now rather than retrofitted, which means **two** certificates and names, not one.

### High
2. **R2 — The peer benchmark is promised to the client and has no data source.** The voice agent explicitly tells respondents they will be *"compared to peer financial services companies of similar scale,"* and the output renders a score out of 100 and a peer-ranked spider chart. Shawn described training on real data as *"iteration part 2."* **As built, the benchmark is LLM-generated with no corpus behind it.** This was flagged on 24 Jul (item J2) and is still unowned. It is the single highest-consequence item in the product: a fabricated peer comparison in front of a prospect's CFO is a commercial and reputational failure, not a bug. Either source a real corpus, or change the language the agent uses and the way the output is framed.
3. **R3 — Steps 4 and 5 are undefined.** Chris asked directly for requirements per step and for the difference between the immediate output and the human-reviewed output. Without that, the report template, the partner workflow, and the automated follow-up all stay unbuildable. **This is the biggest specification gap and it sits on the 19 Aug demo path.**
4. **R4 — Sensitive client data handling was raised and not answered.** Denis flagged it, Alex listed it among the important questions, and the discussion moved on. Executives will disclose candid governance and regulatory weaknesses. Retention, storage, tenancy separation between client companies, and voice-recording consent all need answers **before beta testers get a URL on 21 Aug**, not after.
5. **R5 — The timeline compressed against 24 Jul without an explicit decision.** ~2 weeks of development from a 30 Jul start closes ~13 Aug, against a 19 Aug leadership demo and 21 Aug beta. The earlier framing was 2.5–3 weeks development with production at week five. Confirm which is authoritative and what is MVP-blocking versus deferrable.
6. **R6 — The Catalyst fit decision is open with no criteria, no owner and no date.** Chris set the principle; nobody owns the evaluation. Meanwhile Andre is provisioning accounts and proposing Catalyst-side features while Shawn builds in an isolated repo. Three parties, three working assumptions. **Andre also has not heard the position directly** — relying on him watching the recording is fragile. Tell him, framed as a fit assessment.

### Medium
7. **R7 — "Is the output static?" is unanswered.** Chris's question at 51:11 is lost to the transcript gap. It matters: static rendering versus live regeneration changes storage, caching, and whether a report can be revised after the human review in step 5. Re-ask it.
8. **R8 — Dimension list and question count need pinning to a single source.** The agent's own script says *"the six dimensions we covered"* and *"about 10 questions"* / *"20 to 25 minutes"* — but Shawn wavered aloud between five and six while showing the spider chart, and the dimensions actually exercised in the demo (data, governance, investment, leadership alignment, workforce, value/business case, regulatory) **do not match the 24 Jul list** (strategy, governance, people, process, technology, data). One canonical list, in one place, before the report template is written.
9. **R9 — Admin credential posted in meeting chat.** Denis holds a full-admin Catalyst account whose initial password sits in a retained chat window. Rotate on first login (already forced) and confirm the chat-shared value is dead.
10. **R10 — Avatar comfort is a real product question, not a polish item.** Three of five participants independently found the realistic face off-putting. If respondents are client executives, a UI that reads as creepy costs completion rates directly. The "let them choose" idea is cheap and should be tested with beta users.
11. **R11 — Email MFA has an external dependency with unknown lead time.** V2's shared mailbox + SMTP relay requires an Uptime request and Exchange team action. If V2 is in scope at all, start the request now — the queue, not the code, is the long pole.
12. **R12 — Scope is still accreting.** Taxonomy import, client admin tiers, and avatar choice all appeared today. All were correctly deferred, but 24 Jul already flagged requirements-in-motion as a rework risk. **Label everything new MVP / not-MVP at the moment it is raised.**

### Positive signals
- **Authentication moved from open question to a coherent design in one meeting** — and in the simplifying direction, with the two people who could have made it complicated arguing against doing so.
- **Chris is engaged at the right altitude**, on both the roadmap ("not painting ourselves into a corner") and platform independence ("square peg in a round hole").
- **The HTTPS blocker is smaller than it first appeared** — certificate and URL already exist.
- **Shawn had already isolated the work in a separate repo**, so the Catalyst decision remains genuinely reversible.
- **The voice interview works end-to-end** and the question set is credible and well-pitched; this is hardening, not greenfield.
- Denis contributed substantively on his second working day — the QA/prod split and the budget-abuse angle were both new to the group, and Andre's reaction (*"that's when you find out you got the guy that actually works"*) suggests good standing.
- Twice-weekly cadence in place from week one, with an explicit slot for Denis's blockers.

---

## 9. Action items

### Denis Morozov
| # | Action | Due |
|---|---|---|
| D1 | Connect with Andre on the existing URL + certificate; get **HTTPS live** | This week |
| D2 | Specify **two environments — QA and production** — as part of the DNS/cert work | This week |
| D3 | Log into Catalyst, rotate the chat-shared admin password, confirm access | 4 Aug |
| D4 | Present the **architecture review**, **first next steps and recommendations**, and **blockers** | 4 Aug (next call) |
| D5 | Re-ask Chris's unanswered question: **is the report output static or regenerated?** | 4 Aug |
| D6 | Push the **sensitive-data handling** question to a decision — retention, storage, tenancy, consent — before 21 Aug beta | This week |
| D7 | Raise the **peer-benchmark data source** explicitly as a product risk, not a story | 4 Aug |
| D8 | Confirm he holds the **ElevenLabs requirements documentation** (asserted on the call, location unnamed) | 4 Aug |
| D9 | Produce a **Catalyst fit assessment** — requirements vs capability, with a build / evolve / alongside recommendation | Propose a date at next call |

### Alex Schick
| # | Action | Due |
|---|---|---|
| A1 | Schedule the recurring work session — **Tue + Thu 15:00, 1 hour, 4 weeks** | 3 Aug |
| A2 | Write **requirements and definitions per process step**, especially step 4 vs step 5 output (Chris's explicit ask) | This week |
| A3 | Write up the **authentication decision** as stories: V1 username/password, DXC-uploaded invitee list, 24-hour registration link, Entra for internal/admin roles | This week |
| A4 | Define the **curated report template** and the **partner workflow** after the report is produced | This week |
| A5 | Get a decision on **sensitive data handling** and **whether results are stored in a database** | Before 21 Aug |
| A6 | Log **taxonomy import**, **client admin tiers**, and **avatar-choice UX** as roadmap items, explicitly out of MVP | w/c 3 Aug |
| A7 | Confirm which timeline is authoritative (see R5) and which of the 20–30 tasks are MVP-blocking | 4 Aug |
| A8 | Compile and circulate **key open questions still needing answers** | 4 Aug (next call) |
| A9 | Pin the **canonical dimension list and question count** in one place (see R8) | This week |

### Chris Bryson
| # | Action | Due |
|---|---|---|
| C1 | Deliver the **high-level roadmap presentation** — where this goes beyond phase one | 4 Aug (next call) |
| C2 | Communicate the Catalyst "product need wins" position to **Andre directly**, not via the recording | ASAP |
| C3 | Confirm the client-access process — the DXC-uploads-invitees model as restated by Denis | 4 Aug |

### Shawn Rajguru
| # | Action | Due |
|---|---|---|
| S1 | Get **DNS / CloudFront** in front of the app; move off the raw IP | This week |
| S2 | Triage the component that failed during the demo (was checking logs) | This week |
| S3 | Keep work self-contained in the separate repo until the Catalyst decision is made | Ongoing |
| S4 | Name where the **ElevenLabs requirements** live | 4 Aug |
| S5 | State what the peer-benchmark comparison is actually derived from today | 4 Aug |

### Andre Milhomem
| # | Action | Due |
|---|---|---|
| N1 | Hand over the **existing URL and certificate** to Denis and help connect them | 4 Aug |
| N2 | Share the **email-MFA article** and the Delivery ID spreadsheets/instructions for reference | This week |
| N3 | Confirm Denis's Catalyst admin account; share the **Asana project link** | 4 Aug |
| N4 | Confirm the **SharePoint taxonomy link** landed in chat and is accessible | 4 Aug |
| N5 | Review the recording for Chris's Catalyst position and respond | ASAP |

### Joint / unassigned
| # | Action |
|---|---|
| J1 | **Identify the owner and data source for the peer benchmark** — carried from 24 Jul, still open, now demonstrably load-bearing |
| J2 | Set a **decision date and evaluation criteria** for Catalyst vs standalone |
| J3 | Define **data retention, tenancy separation and consent** before beta testers get access |
| J4 | Decide whether the back-office/admin surface is built in-house or delegated to an existing CRM |
| J5 | Start the **shared mailbox / SMTP relay** request if email MFA is in scope for V2 |
| J6 | Re-export the transcript segments still missing (see caveat) if the lost threads matter |

---

## 10. Questions to raise on the next call

1. **Where does the peer benchmark data come from, and who owns it?** The agent already promises peer comparison to respondents.
2. **Is the report output static or regenerated?** (Chris's question, lost to the transcript gap.)
3. **What exactly differs between step 4 and step 5 output**, and what is the report template?
4. What are the **data retention, residency and confidentiality rules** for transcripts and voice recordings — and does anything get reused for benchmarking?
5. **Which timeline is authoritative** — 2 weeks development to a 19 Aug demo, or the earlier week-five production framing? What is MVP-blocking?
6. **Six dimensions — which six?** The demo's dimensions do not match the 24 Jul list.
7. **What are the criteria for the Catalyst decision, and who makes the call?**
8. Is **email MFA** in scope for this build, or genuinely V2? (Determines whether the Exchange request starts now.)
9. Who handles the **QA environment** provisioning, and does it get its own certificate?
10. Do we test **avatar vs abstract UI** with beta users, and does the choice become the first interview question?

---

## 11. Links
- [project repo](https://partner-github.dxc.com/SAM-Prime-X/ai-readiness-diagnostic)
- Catalyst instance — *URL shared in chat, not captured in the transcript*
- Catalyst Asana project (task: *Create Taxonomy*) — *link shared in chat, not captured*
- DXC services taxonomy — *internal SharePoint site; link shared in chat, not captured. Source of truth; feeds Salesforce.*

## 12. Contacts
- [Alex Schick](mailto:alex.schick@dxc.com)
- [Shawn Rajguru](mailto:shawn.rajguru@dxc.com)
- Chris Bryson — *address not captured*
- Andre Milhomem — *address not captured*
- Robb — *surname and address not captured*
