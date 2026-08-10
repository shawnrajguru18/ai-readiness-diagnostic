# How Signing In Works

**A plain-language overview for non-technical readers**

**Audience:** managers, marketing, legal, commercial and support colleagues
**Subject:** the sign-in design specified in `specs/SPEC_passwordless_email_auth.md`
**Date:** 10 August 2026
**Status:** **Proposed and not yet built.** Presented on 5 August, unopposed, and awaiting formal
approval. Nothing described here is live today.

This document is a summary, not a rulebook. Where it and the engineering specification differ, the
specification is correct — see [Where the detail lives](#where-the-detail-lives) at the end.

---

## In one paragraph

There are no passwords. We already know who every user is, because a DXC colleague entered their name
and work email before they were ever invited. When someone wants in, we email them a one-time sign-in
link. Clicking it, and then confirming on the page that opens, proves they control the mailbox we hold
for them — and that is what signs them in. They stay signed in for a while, then the session quietly
expires and they ask for a fresh link.

---

## Why we designed it this way

| Benefit | What it means in practice |
|---|---|
| **Nothing to steal** | We hold no passwords, no password hashes, no security questions. A breach of our database yields no credential that works anywhere. |
| **Nothing to forget** | There is no "forgot password" flow, because there is nothing to forget. Users cannot be locked out by a mistyped password. |
| **Nothing to support** | Password resets are the single largest category of access support tickets in most systems. This design does not have any. |
| **Invitation-only by construction** | The system cannot create an account for someone who was not entered by a DXC colleague. Not by mistake, not by design. |
| **Built for GDPR from the start** | Personal data sits in one place, is referenced everywhere else by an anonymous internal ID, and can be erased through a defined workflow. |
| **No third-party dependency** | No external login provider sits between our clients and our product, so there is no vendor to onboard, license or wait for. |

---

## Who can get in

Only people a DXC colleague has already entered into the system.

There is **no sign-up page**. A client executive cannot create their own account, and neither can
anyone else. The system holds each authorized person's work email, name, company, job title and the
organization they belong to, all supplied in advance by the DXC partner running the engagement.

If an email address is not already in the system, nothing we can do to that address will produce an
account. Typing an unknown address into the sign-in page produces no account, no email and no error
that reveals anything.

---

## What a user actually experiences

```
  1. A DXC colleague adds the person and sends an invitation
                      │
                      ▼
  2. An email arrives with a sign-in link
                      │
                      ▼
  3. They click the link
                      │
                      ▼
  4. A page opens showing their own name, company and job title
     — nothing to fill in, nothing to remember
     (First time only: the consents to agree to)
                      │
                      ▼
  5. They click Continue
                      │
                      ▼
  6. They are in
```

Two details worth knowing, because they shape the experience:

**Clicking the link does not, by itself, sign anyone in.** The user has to click *Continue* on the
page that opens. This is deliberate. Corporate email systems routinely open links in messages before
the recipient ever sees them, to scan for threats. If clicking were enough, those scanners would burn
the link and the real user would arrive to find it already used.

**The user is never asked to type their name, company or job title.** We already hold those, supplied
by the DXC colleague who set them up, and ours is the authoritative copy. Asking would invite typos
into the record and make the page look like a registration form, which it is not.

---

## Staying signed in, and getting back in

| | |
|---|---|
| **The sign-in link** | Works once, and expires shortly after it is sent. Requesting a new one cancels the old one. |
| **Idle timeout** | About 30 minutes of inactivity ends the session. Any activity resets the clock. |
| **Maximum session** | 30 days, however active the user is. Everyone re-proves control of their mailbox at least monthly. |
| **Getting back in** | The user goes to the site, enters their email, and a fresh link arrives. No administrator needs to be involved. |
| **Signing out** | Ends the session immediately. |

Both timeout values are settings, not hard-wired, and can be tuned once we see real usage.

---

## Consents

The first time someone signs in, the page shows the consents currently in force under the heading
**"I agree with the following consents"** — one tick box each, none pre-ticked. *Continue* stays
disabled until every mandatory box is ticked. Optional consents can be declined, and a declined
optional consent is not raised again at the next sign-in: asking repeatedly is pressure, not a
reminder, and consent given under pressure is weaker evidence than consent given once.

Consents are agreed **before** the first session exists, so there is no window in which we process
someone's data without a recorded basis for doing so.

If legal later adds a new mandatory consent, users holding a live session are asked inside that
session rather than being signed out. They see the new consent, decide it, and carry on with whatever
they were doing. An interview in progress is not lost.

Every decision — accepted or declined, and against which version of the wording — is recorded
permanently. Publishing new wording does not overwrite or invalidate the old record: what someone
agreed to in version 1 remains true about version 1.

---

## Who can do what

Four roles, and the boundary between them is a legal and commercial position as much as a technical
one:

| Role | Who | In short |
|---|---|---|
| **User** | Client employee | Takes their own assessment, reads their own report. |
| **Power user** | Client sponsor | Also reads every report in their own organization. |
| **Partner** | DXC engagement lead | Adds client people, sends invitations, reviews and approves reports for the organizations assigned to them. |
| **Admin** | DXC platform operator | Runs the platform — organizations, partners, templates, settings, audit log. |

**Admins cannot read client reports.** Not "should not" — the design forbids it. Whoever administers
the platform is separated from whoever sees client findings, and no single account holds both.
This is worth stating to clients, and it is a genuine differentiator.

Nobody, in any role, can obtain or set another person's credential — because no credential exists to
obtain.

---

## What we store, and what we never store

**We store:** work email, full name, company name, job title, organization, role, and account status.
That is the whole of the personal data behind sign-in.

**We never store:** passwords, password hashes, security questions, or any lasting secret belonging to
a user.

Everything else in the product — assessments, interviews, scorecards, quick wins — refers to a person
by an internal ID that means nothing on its own and contains no name, no email and no company. Their
personal details live in exactly one record. That is what makes an erasure request tractable rather
than a hunt.

Data is kept in four separate stores with separate access rules: what is true now, what happened
(the audit trail), the reference material in force (consent wording, email templates), and technical
diagnostics. Personal data is only put where the purpose of that store requires it.

---

## Safeguards, in plain terms

- **Every sign-in link works once.** Using it consumes it. Issuing a new one cancels the previous one.
- **Links are short-lived** and useless after they expire.
- **Links cannot be guessed.** They carry a randomly generated value long enough that guessing is not
  a realistic attack, and we store only a one-way fingerprint of it, never the value itself.
- **The link is only ever sent to the address in our records** — never to an address a visitor typed.
  A visitor's input is used to look someone up, never as a destination.
- **We never confirm whether an address is known to us.** The sign-in page gives the same answer for a
  known address, an unknown one, a suspended account and a blocked mailbox. Outsiders cannot use the
  page to work out who our clients are, or who our administrators are.
- **Suspending an account takes effect immediately**, cancelling live sessions and preventing new
  sign-ins.
- **Changing someone's role or organization ends their sessions**, so a change of permissions is never
  delayed by a session that is still open.
- **Everything security-relevant is logged** to a separate audit trail that ordinary operations cannot
  alter — who was invited, who signed in, who failed, what changed, who consented to what.
- **Mail delivery is tracked per invitation.** We can tell whether the email was delivered, bounced,
  or was marked as spam — which means "did they get it?" is an answerable question rather than a guess.
- **Mailboxes that complain are respected.** If someone marks our mail as spam, we stop mailing that
  address until the situation is resolved. This protects our ability to deliver to everyone else.
- **There is no master password anywhere.** Not for administrators, not at first installation, not
  once. Every account in the system, including the first administrator, gets in the same way: by
  receiving a link.

---

## When something goes wrong

| Situation | What happens |
|---|---|
| The user never received the email | We can see the delivery status against the invitation and say whether it was delivered, bounced or blocked. |
| The link was already used | They request a new one from the sign-in page themselves. |
| The link expired | Same — they request a new one. |
| Their session ended mid-interview | They request a fresh link and continue; work already recorded is not lost. |
| A user leaves the client | Their account is suspended, which ends their access at once. |
| A user asks to be deleted | A defined erasure workflow removes or anonymizes their records according to the retention policy. |
| We lose all our administrators | Recoverable from deployment configuration by a named, pre-agreed address — see below. |

---

## The honest limits

Worth knowing before anyone presents this externally.

**The mailbox is the front door.** Whoever controls a person's work email can sign in as that person.
The design assumes corporate mailboxes are reasonably secured — which is the same assumption behind
every "reset my password" link ever sent, but here it is the primary mechanism rather than the fallback.
We rely on the client's own email security, and on the DXC colleague having entered the right address.

**There is no second factor today.** The design deliberately does not add an emailed code on top of an
emailed link, because a second code sent to the same mailbox is not an independent check on the first.
If a client's security review requires a genuine second factor, one can be added later without
redesigning anything else.

**Email is the only way in, for everyone.** If our outbound mail stops working, nobody can sign in —
including administrators, and including at first installation. Mail is therefore on the critical path
in a way it would not be in a password-based system, and getting our sending domain properly set up is
a prerequisite for the platform working at all, not a nice-to-have.

**Losing every administrator is recoverable, but only from configuration.** A short list of addresses
held in the deployment configuration can obtain an administrator account. It confers the ability to be
sent a link — not an account, and not a way in without receiving that link. Two consequences are
written down rather than glossed: whoever can change our deployment configuration can become an
administrator, and this route also stops working if outbound mail is broken.

---

## For marketing: how to describe it

**Accurate and usable:**

- "No passwords. Sign in with a link sent to your work email."
- "Invitation only — accounts are created by DXC, never self-registered."
- "We store no passwords and no credentials of any kind."
- "Platform administrators cannot read client reports. Separation of duty is built in."
- "Consent is captured before any assessment begins, and every decision is recorded against the exact
  wording it was given for."
- "Personal data lives in one place and can be erased on request."

**Do not say:**

- "Multi-factor authentication" or "MFA" — there is one factor today. Saying otherwise is a claim a
  client security review will test.
- "Passwordless is more secure than passwords" without qualification — the honest framing is that it
  removes a whole class of risk (stolen, reused and forgotten passwords) and concentrates the remaining
  risk in the corporate mailbox, which the client already protects.
- "Zero trust", "bank-grade", "military-grade" — none of these mean anything here and all invite
  scrutiny we would rather spend elsewhere.
- Anything at all in the present tense. This is **proposed and unbuilt**. Until it ships, describe it
  as the design.

---

## Where the detail lives

| Question | Document |
|---|---|
| The full sign-in design | `specs/SPEC_passwordless_email_auth.md` |
| How the email is sent and tracked | `specs/SPEC_outbound_mail.md` |
| Consent wording, versioning and records | `specs/SPEC_data_system_consents.md` |
| Exactly what each role may do | `specs/role_model.md` |
| Why passwordless replaced the earlier username/password decision | `meetings/2026-08-05_meeting_summary.md` |

All paths are relative to `docs/`. Every specification in that family is currently marked **Proposed**
and none is implemented.
