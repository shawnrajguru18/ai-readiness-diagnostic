# Outbound Mail Transport — Decision Record

**Date:** 5 August 2026
**Status:** DECISION RECORD — retained for rationale and open dependencies. **Not normative.** The
normative requirements that grew out of this document now live in
[Outbound Mail Transport and Delivery](../../specs/SPEC_outbound_mail.md); where the two disagree, that
specification governs. Resolves `docs/architecture/authorization_model_phase1.md` §14 open point **E**.
**Verified against:** commit `3fb65ea` (branch `doc/auth-stage1`) for all current-state statements.
Microsoft and AWS product constraints verified against vendor documentation on 5 August 2026.
**Scope:** *Why* this transport and this sender identity were chosen, what was ruled out, and what
remains organizationally blocked. The design itself is no longer described here.
**Moved** from `docs/specs/outbound_mail_transport.md` on 10 August 2026, when `docs/specs/` became the
home of the normative `SPEC_*` family and this document stopped being normative. Citations to the old
path resolve here; see [analysis/INDEX.md](INDEX.md).

**Conventions.** Bare `§` references are to `docs/architecture/authorization_model_phase1.md`.
**MUST** / **MUST NOT** mark requirements that were intended to become normative; they have since
been restated as "shall" in the specification named above, which is the form of record. Statements
under "Current" describe the system as built and are verifiable against the referenced code. Items
marked **needs confirmation** are listed in §7.

---

## 1. Context

§1 makes email the sole authentication channel: every account — `user`, `power_user`, `partner` and
`admin` alike — is created by email invitation and authenticates by possession of the invited mailbox.
§1.1 states the consequence plainly: *"Mail is a single point of failure for all access."* §12.2 puts
sender verification on the critical path and characterises it as **elapsed time, not effort**.

**Current: no mail code exists.** `app/` has no mail imports; `requirements.txt` (10 lines) has no mail
library, no template engine, and no `msal`/`azure-identity`. `terraform/` has no SES, SNS, Route 53 or
ACM resources. The task role holds an enumerated DynamoDB action list on one table
(`PutItem`, `GetItem`, `Scan`, `UpdateItem`, `Query` — not `dynamodb:*`) and `bedrock:InvokeModel`
(`terraform/iam.tf:64-98`).

Two findings reframe the choice recorded in §14 point **E**.

**1. The proposal on record was answering a different question.** `docs/meetings/2026-08-03_meeting_summary.md:81`
recommends "request a shared mailbox via Uptime → configure an SMTP relay in the app → the Exchange team
grants the account relay access." Line 80 shows the context: this was the implementation path for
**email MFA codes** under a username-and-password model. §1.1 subsequently deleted that requirement —
*"a code sent to that same mailbox proves the same thing twice"* — and the recipient population changed
with it, from internal DXC staff to **external client executives** behind Mimecast, Proofpoint and
Defender for Office 365 (§6.3). The advice was sound for the problem it addressed; the problem changed.

**2. §4 `delivery_status` is the decisive differentiator.** §6.1 issuance rule 5 requires that *"a
failure to reach the mailbox is distinguishable from a recipient who has not yet clicked."* Microsoft
Graph `sendMail` returns `202 Accepted` and nothing further, so both states produce the same observable;
`complained` is not obtainable from Exchange Online at all, and `bounced` requires parsing NDRs out of
the shared mailbox under an additional, more sensitive permission. Amazon SES emits `DELIVERY`, `BOUNCE`
and `COMPLAINT` events natively. **Graph cannot implement §4 as written**, and its degraded two-value
version costs more application code than SES's complete one.

**The sender domain is settled: `air.dxc.com`.** This removes the larger half of point **E**. A
DXC-owned subdomain carries SES DKIM with exact DMARC alignment (`d=air.dxc.com` matches the From
domain), which recovers most of what an `@dxc.com` From address would have bought.

---

## 2. Decision

**Transport: Amazon SES.** **Sender:** `From: "DXC AI Readiness" <no-reply@air.dxc.com>`, with
`Reply-To` a real `@dxc.com` team mailbox. **Implementation:** behind a provider-agnostic interface, so
a later move to Microsoft Graph is a driver change rather than a rewrite.

This resolves point **E** *toward* the existing architecture of record —
`docs/architecture/aws_reference_architecture_and_cost_model.md:48` already names "Amazon SES (optional) —
Send report links to executives" — so it is not a deviation requiring separate justification.

### 2.1 Options ruled out

Each disqualification rests on a fact independent of the sender-domain question. The Microsoft mechanics
below are **needs confirmation** with the DXC Exchange team before any ticket is closed or withdrawn.

| Option | Ruled out because |
|---|---|
| Exchange **Direct Send** (`<domain>.mail.protection.outlook.com:25`) | Rejects recipients outside the tenant. Every invitee is external (§2: `user` = "Client executive, invited"). Absolute. |
| Exchange **High Volume Email** | External sending was removed in June 2025; internal-only at GA. Absolute for invitations. Could carry §6.5 rule 4 internal staff notifications, which is not worth a second transport. |
| Exchange **SMTP relay via inbound connector** | Requires a *static, unshared* source IP. `terraform/ecs.tf:133` sets `assign_public_ip = true` and there is **no NAT gateway, EIP or route table anywhere in `terraform/`** — the whole VPC layer is consumed as data sources (`terraform/security.tf:1-9`), so the task IP is ephemeral and changes on every task replacement. Remedying this means NAT + EIP + private subnets (~$36–69/mo, against a ~$196/mo lean AWS budget that explicitly says to avoid always-on NAT — `docs/architecture/aws_reference_architecture_and_cost_model.md:126`) plus a separate AWS request to lift the default outbound port-25 block, to send ~300 emails/month (`:69`). Microsoft additionally documents relay from third-party clouds as unsupported. **This is the mechanism the J5 ticket literally requests.** |
| **SMTP AUTH** (`smtp.office365.com:587`) | Functional but strictly dominated by Graph. Basic authentication is being retired, so it converges on XOAUTH2 — the same app registration and the same DXC queue as Graph, plus an MSAL dependency, plus hand-built MIME headers into a codebase with a live header-injection defect (`docs/architecture/architecture_topics.md:256`), plus a licensed mailbox and `Send As` — and the same unobtainable `delivered` and `complained`. |
| **Third-party ESP** (Postmark, SendGrid, Mailgun) | Non-viable on process rather than capability: procurement, InfoSec vendor assessment, and a DPA covering client-executive PII, to buy a ~$0.03/month capability an already-approved AWS account provides natively — and it still needs DKIM records in DXC DNS. |
| **Microsoft Graph** `sendMail` | **Deferred, not disqualified.** See §2.3. |

### 2.2 Why SES

1. **It is the only remaining option that satisfies §4 and §6.1 rule 5** as specified. Delivery,
   bounce and complaint arrive as events rather than as mail in a human's inbox.
2. **It needs no secret.** The ECS task role authenticates by SigV4. This matters because Secrets
   Manager is **not wired up**: `terraform/ecs.tf:65-92` has no `secrets` block, and the execution role
   (`terraform/iam.tf:19-44`) lacks `secretsmanager:GetSecretValue`, so adding one would fail task
   startup today. Graph and SMTP both carry that prerequisite; SES does not. The only change is one IAM
   statement on the task role.
3. **Its delivery-status path needs no inbound endpoint.** Configuration set → EventBridge/SNS → a small
   handler. This matters because the ALB's certificate is **self-signed** (`ONBOARDING.md:81`), so any
   webhook-dependent design — Graph change notifications, ESP webhooks — is serially blocked behind
   **P0-1**.
4. **It has a zero-dependency development path.** Sandbox mode sends to verified addresses immediately,
   and the mailbox simulator (`success@`, `bounce@`, `complaint@simulator.amazonses.com`) exercises the
   full §4 state machine with no real recipients and no DXC ticket. Under §12.2 — where mail is elapsed
   time on the critical path — this is the property that keeps Phase 1b and Phase 2 development moving
   while DNS is pending. No other option has it.

### 2.3 Sender identity, and what carries recipient trust

The recipient is an external executive receiving an authentication link, so sender trust is a
deliverability *and* a security-perception concern, not cosmetics.

- `From: no-reply@air.dxc.com` — a DXC-owned domain, DKIM-signed with exact DMARC alignment.
- `Reply-To:` a real `@dxc.com` team mailbox — no DNS or Exchange work, and it is what a suspicious
  recipient checks.
- **Human pre-announcement**, which is already the operating model: *"we do not want clients
  self-authenticating… we want engagement with those people"*
  (`docs/meetings/2026-08-03_meeting_summary.md:86`). A partner who tells the client a link is coming is
  the strongest anti-phishing control available, and it is free.

**Graph is kept as a driver swap.** Its one genuine advantage was an `@dxc.com` From address, and
`air.dxc.com` recovers most of that — so the case for ever building the Graph driver is weaker than it
was. The J5 ticket is already filed; let it land as free optionality. **Nothing on the critical path
depends on it**, and the connector-relay follow-up it implies should not be pursued (§2.1).

---

## 3. What became normative, and where it now lives

The application design this document originally carried — the mail layer's structure, the transport
interface and its four outcomes, the delivery-status state machine, the delivery-event webhook and its
two gates, complaint suppression, address normalization and header safety, template rendering, token
secrecy, link construction, the send site and the resend accounting — has been restated as normative
requirements in [Outbound Mail Transport and Delivery](../../specs/SPEC_outbound_mail.md) and removed
from here, so that there is one statement of each requirement rather than two.

Three things changed in the restatement rather than being carried across unaltered, and the change is
recorded here because a reader of this document would otherwise expect the original:

1. **Templates are not files.** This document specified stdlib `string.Template` triplets under
   `app/mail/templates/`. The specification family holds e-mail templates as versioned markdown in the
   System DynamoDB table, resolved by identifier in `ACTIVE` state at the latest version. Markdown is a
   wider input surface than placeholder substitution, so the specification additionally forbids raw HTML
   passthrough and the linkification of substituted values — hardening this document did not need.
2. **There is one credential concept, not two.** This document assumed separate `INVITATIONS` and
   `AUTH_LINKS` records, separate `invitation` and `signin` templates, and two message-id indexes. The
   authentication specification defines a single invitation: a returning user is issued another
   invitation, because a user who has authenticated remains eligible. One template, one delivery state,
   one index.
3. **Staff-event notification is excluded.** It rested on §6.5 rule 4 of the Phase 1 authorization
   model, which has no counterpart in the specification family. The background fan-out and its
   partial-failure residue therefore have no requirement behind them and were dropped rather than
   carried forward silently.

---

## 4. Amendments to the Phase 1 documents

**These entries concern `docs/architecture/authorization_model_phase1.md` and
`docs/architecture/data_architecture_phase1.md` only.** They are the record of what this decision
changed in the *Phase 1* document set in August 2026. An "Applied" mark below does **not** mean the
change is present in the `SPEC_*` specification family, which landed its own equivalents separately.

Eight were raised. Seven were applied to the Phase 1 documents; one was not.

| # | Amendment | Lands in | Status |
|---|---|---|---|
| **1** | **§14 point E** — close it, recording the decision in §2 and the disqualifications in §2.1. Carry forward only the `air.dxc.com` administration question as a Phase 0 DNS task, not an open decision. | `authorization_model_phase1.md` §14 | **Applied** 6 Aug 2026. The letter is retired, not reused; Phase 1b's blocker is now Phase 0, not an open point. |
| **2** | **§12.2 Phase 0** — fold "begin mail sender verification" into the same DNS work item as the ALB and ACM ask, since both now resolve on `air.dxc.com`. | `authorization_model_phase1.md` §12.2 | **Applied** 6 Aug 2026. |
| **3** | **§4 `INVITATIONS`** — add `queued` and `failed` to `delivery_status`; add `delivery_reporting`. | `authorization_model_phase1.md` §4 | **Applied** 6 Aug 2026, semantics only — see the redirect below. |
| **3b** | The delivery-event GSI, because the partition key is `token_hash` while events arrive keyed by SES `MessageId`. | `data_architecture_phase1.md` §4.6 | **Already existed** as `invitation_message_index`. Redirected — see below. |
| **4** | **Complaint suppression.** A `Complaint` event **MUST** write a suppression record (`MAIL_SUPPRESSION#<normalized_email>`), and issuance and resend **MUST** consult it before touching the transport. | Nowhere in the Phase 1 set | **NOT APPLIED there** — see below. |
| **5** | **§4 `AUTH_LINKS`** has no `delivery_status`, so a bounced sign-in link has nowhere to land: an audit entry plus a `mail_state` attribute on the `USERS` row, so support can see why an executive cannot get in. | `authorization_model_phase1.md` §4 and `data_architecture_phase1.md` §4.6 | **Applied** 6 Aug 2026, and extended — the token row also needed `provider_message_id` and an index, which the amendment as raised did not say. |
| **6** | **§6.3 / §6.4** — record the `resend_count` accounting rule. | `authorization_model_phase1.md` §6.3 | **Applied** 6 Aug 2026, with the `invitation_id` dependency stated: without it the cap never binds. |
| **7** | **§8.1** — add the webhook route, marked *network-reachable, payload-authenticated; not public in the authorization sense*. | `authorization_model_phase1.md` §8.1 | **Applied** 6 Aug 2026, with both gates made `MUST`. |
| **8** | **§6.3** — record the tracking-options prohibition and the public-base-URL rule. | `authorization_model_phase1.md` §6.3 | **Applied** 6 Aug 2026. |

**Amendment 3b was raised against the wrong document, and under the wrong name.** It asked the
authorization specification for a GSI called `message_id_index`. That specification does not own keys
or indexes — `data_architecture_phase1.md` is normative for those (its §4.4) — and the index in
question already existed there as **`invitation_message_index`**, on `provider_message_id`,
`KEYS_ONLY`, serving exactly this webhook. Applying the amendment as written would have produced one
index under two names in two documents, one of which has no authority to define it. **The name of
record in the Phase 1 set is `invitation_message_index`**, and `message_id_index` should not appear
anywhere. The companion index for sign-in links is `auth_link_message_index`, added under amendment 5.

**Amendment 4 was the one open spec gap, and it is now closed outside the Phase 1 set.** Nothing in the
Phase 1 documents defines where a suppression record lives — `data_architecture_phase1.md` §4.2 lists
fourteen tables and none of them is it, so it was a table design rather than a transcription, and it
could not be closed by editing prose. It was load-bearing: continuing to mail an address that has filed
a complaint gets the sending domain throttled or blocked, and under §1 the sending domain *is*
authentication, so the failure mode is total loss of access for every account. The specification family
has since given it a home as a Business-table entity keyed by normalized address, with a dictionary
entity type, an enforcement point before the transport is contacted, and an audited administrative
removal path. **The gap remains open in the Phase 1 set**, which is a reason to retire those documents
rather than to reopen the amendment.

---

## 5. Critical path

### 5.1 Unilateral — no DXC dependency, unblocks Phase 1b and Phase 2 in full

1. **Probe for SCP blocks first.** `aws sesv2 get-account`, then `create-email-identity` on a team
   address, in `us-east-1` under account `023138541872`. This is the single thing that can invalidate
   the decision — `deploy/aws/DEPLOY_AWS.md:118` warns that DXC SCPs and permission boundaries may block
   services per-region. Fallback if blocked: Azure Communication Services Email, which also satisfies
   §4 via Event Grid, at the cost of a second cloud and a cross-cloud secret.
2. Verify three or four team addresses; sandbox mode permits sending to verified addresses.
3. Add the IAM statement, build the mail layer to the specification, and test against the mailbox
   simulator.

At the end of step 3, Phase 1b and Phase 2 are functionally complete and demonstrable with nothing
pending from DXC.

### 5.2 DXC queue — file in parallel

4. **Settle how `air.dxc.com` DNS is administered** — the one remaining unknown. Request **NS
   delegation of `air.dxc.com` to a Route 53 hosted zone** in account `023138541872` rather than
   individual records: per-record publication means a new corporate ticket on every DKIM rotation and
   every new environment, and QA and production are separate names
   (`docs/meetings/2026-08-03_meeting_summary.md:114`). Records needed: three Easy DKIM CNAMEs; a custom
   MAIL FROM subdomain (`bounce.air.dxc.com` MX + SPF TXT) so SPF aligns rather than pointing at
   `amazonses.com`; and `_dmarc.air.dxc.com`.

   **Bundle this with the P0-1 TLS ask — it is one DNS conversation, not two.** §12.2 Phase 0 already
   owes "ALB, ACM certificate, DNS"; the app is currently reachable only at
   `ai-readiness-alb-751626769.us-east-1.elb.amazonaws.com` with a self-signed certificate
   (`ONBOARDING.md:9,81`); and the link host and the mail domain should be the same registrable domain.
   An emailed authentication link pointing at an `*.elb.amazonaws.com` host will be rewritten by
   Mimecast and *reads* as phishing regardless of DMARC. One delegation yields ACM DNS validation, the
   application hostname, and the SES records.

   *Check before requesting: `air.dxc.com` is plausibly the URL and certificate Andre already holds
   (`docs/meetings/2026-08-03_meeting_summary.md:113`), in which case part of this is already done.*
5. **SES production access request** — file as soon as the domain identity verifies. Cite the
   bounce-and-complaint pipeline built in step 3 and the ~300/month volume; a documented complaint
   pipeline is what these reviews look for.
6. **J5 (already filed)** — let it land as optionality for a later Graph driver. Do not pursue the
   connector-relay follow-up it implies (§2.1).

**Degraded path if the DNS ask slips.** Run the beta on SES sandbox with each tester's address verified
individually — viable because the beta population is DXC-provisioned and small
(`docs/meetings/2026-08-03_meeting_summary.md:92`). No other transport option has a degraded path.

---

## 6. Questions for DXC IT, Exchange and email security

1. **Is there already a DXC-standard transactional mail service for products** — an internal relay, an
   approved ESP tenant, an ACS resource, or an existing SES account with pre-approved DNS? *Ask first;
   it can supersede this entire document.*
2. **How is `air.dxc.com` administered today** — already NS-delegated to a zone we control, or records
   published in the corporate `dxc.com` zone on request? If the latter, will they delegate; if not, what
   is the lead time per record and the change cadence for DKIM rotation?
3. What is the current **DMARC policy on `dxc.com`** — `p=` and especially `sp=`, which governs
   `air.dxc.com` unless we publish `_dmarc.air.dxc.com` ourselves — and is there an approved pattern
   other DXC products already use for subdomain sending?
4. **Is `air.dxc.com` already used for mail by anything else**, and is there an existing SPF/DKIM/DMARC
   posture we would be changing rather than creating?
5. Do SCPs or permission boundaries block `ses:*`, `sns:*`, `events:*` or `secretsmanager:*` in
   `023138541872` / `us-east-1`, and who grants an exception?
6. **Is a sandbox AWS account acceptable for client-facing mail and client PII at all**, or must this
   move to a governed account before beta? *Potentially a larger blocker than mail itself.*
7. For a later Graph path: will DXC grant `Mail.Send` **application** permission with tenant admin
   consent, **scoped by RBAC for Applications to a single mailbox**? What is the queue time per step?
8. Are **Conditional Access policies applied to workload identities**? If any requires a named location,
   Graph also needs a static egress IP — and therefore the NAT that ruled out the SMTP relay.
9. **Is the certificate Andre already holds** (`docs/meetings/2026-08-03_meeting_summary.md:113`) for
   `air.dxc.com`, and can it terminate on the ALB, or is ACM DNS validation needed instead?
10. Which `@dxc.com` mailbox is `Reply-To`, and which alias receives operational mail alerts?
11. What is the **actual Uptime/Exchange queue time**, empirically? Recorded as unknown at
    `docs/meetings/2026-08-03_meeting_summary.md:209`; one data point converts it from risk to schedule.

---

## 7. Claims needing confirmation

| Claim | Status |
|---|---|
| Exchange Direct Send, HVE and connector-relay constraints as stated in §2.1 | Verified against Microsoft documentation on 5 August 2026. **Confirm with the DXC Exchange team** before closing or withdrawing the J5 ticket. |
| SMTP AUTH basic-authentication retirement timing | Microsoft has announced retirement with revised dates. Directionally certain, exact effective date **unverified** — and moot under this decision. |
| Whether `ses:*`, `sns:*` and `events:*` are SCP-permitted in account `023138541872` | **Unverified. The one assumption that can invalidate this decision.** Probe first (§5.1 step 1). |
| Whether DXC will delegate NS for `air.dxc.com` | The largest organizational assumption. The per-record fallback works but adds a ticket per DKIM rotation. |
| DXC's actual DMARC policy on `dxc.com` (`p=` / `sp=`) | Not checked. DKIM alignment on `air.dxc.com` passes DMARC regardless of policy, but the subdomain policy should be published deliberately rather than inherited. |
| Whether a sandbox AWS account is acceptable for client-facing mail and client PII | Unverified, and potentially a larger blocker than mail. |
| Whether the existing out-of-band ALB (`ONBOARDING.md:9,80`) can take an ACM certificate without a Terraform rewrite | It is absent from `terraform/`, so state reconciliation is an unknown. |
| Uptime / Exchange queue lead time | Recorded as unknown at `docs/meetings/2026-08-03_meeting_summary.md:209`. Still unknown. |
| Azure Communication Services Email pricing, for the fallback | Not obtained. Verify before promoting ACS. |

---

## 8. Deliberately left open

| Item | Tradeoff |
|---|---|
| **`air.dxc.com` delegation model** — the residue of point **E** | NS delegation makes DKIM rotation and new environments self-service; per-record publication means a corporate ticket each time. Does not block the build either way. |
| Scorecard PDF: attach or link | Attaching needs no authorization work, but is 1–3 MB and the deliverable then lives in a mailbox outside every retention and erasure control (§13.1). A link requires `GET /api/scorecard/{id}/*.pdf` to be gated first — currently public (§8.2). Leaning link-only, which makes it Phase 2 rather than Phase 1b. |
| Invitation validity window (§14 point **H**) | Affects copy only; templates render the interval from the record, so nothing blocks. |
| Suppression list authoritative or advisory | **Settled in the specification as authoritative with an audited administrative removal path**, on the grounds that the alternative risks the only channel the product has. Recorded here because the tradeoff was real: authoritative suppression can hard-block a partner from inviting their own client after one spam-button press. |
| A `queued`-row reaper | Needs a scheduler, and none exists. Leaving `queued` rows visible and manually resendable is honest and costs nothing for Phase 1. |
| `msal` for the Graph backend, if ever built | Client credentials is one httpx POST plus in-process token caching, holding `requirements.txt` at 10 lines; `msal` handles regional endpoints and CAE claims challenges. Only decidable if Graph is adopted. |

---

*Related: `docs/architecture/authorization_model_phase1.md` §1, §4, §6, §12.2, §14 point **E**;
`docs/architecture/aws_reference_architecture_and_cost_model.md:48,69`;
`docs/architecture/architecture_topics.md:253,256,262`;
`docs/meetings/2026-08-03_meeting_summary.md` §4, §5.*
