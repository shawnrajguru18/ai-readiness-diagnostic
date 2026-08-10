# AdvisorX Engineering Specification
# Outbound Mail Transport and Delivery

**Status:** Proposed  
**Transport:** Amazon SES  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** Business, Audit, System

---

## 1. Purpose

This specification defines how the application sends outbound e-mail.

[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) makes the magic link the sole
authentication channel: every user of every role is provisioned and authenticates through a message
delivered to the provisioned mailbox. Its §12 step 7 requires the server to send that message but does
not specify the mechanism. This document specifies it.

Because mail is the only authentication channel, it is a single point of failure for all access. Two
consequences follow, and they shape this entire document:

- A message that never reaches the mailbox denies access as completely as a revoked session.
- Loss of sending reputation for the sending domain denies access to every user at once, not to one.

This specification therefore treats delivery as an observable outcome to be recorded, not an
assumption to be made.

The system does not treat a successful hand-off to the transport as proof of delivery.

---

# 2. Design Goals

The outbound mail architecture shall provide:

1. A single transport for all authentication mail.
2. A sender identity that authenticates the sending domain.
3. Delivery, bounce and complaint reported as events rather than inferred.
4. A failure to reach the mailbox distinguishable from a recipient who has not yet acted.
5. A durable, issuer-visible delivery state on the invitation record.
6. No permanent authentication secret on the send path.
7. The magic-link token confined to the rendered message body.
8. Complaint suppression honoured before the transport is contacted.
9. Message content resolved from versioned templates rather than embedded in the application.
10. Honest reporting where delivery cannot be known.

---

# 3. Non-Goals

The system does not provide:

- inbound mail reception or mailbox hosting;
- parsing of non-delivery reports from a mailbox;
- bulk, marketing or campaign mail;
- open tracking or click tracking (§20.2);
- mail-based multi-factor authentication, which
  [Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §3 excludes;
- staff or operator notification mail.

The last exclusion is deliberate rather than accidental. No requirement in this specification family
calls for notifying staff by e-mail. If such a requirement is introduced, it shall not be satisfied by
adding a second transport.

---

# 4. High-Level Architecture

```text
                  ┌─────────────────────────────┐
                  │       Application API       │
                  │                             │
                  │ Invitation issuance         │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                  ┌─────────────────────────────┐      ┌──────────────────┐
                  │        Mail Layer           │◀─────│     System       │
                  │                             │      │    DynamoDB      │
                  │ Suppression check           │      │                  │
                  │ Template resolution         │      │ E-mail templates │
                  │ Rendering                   │      │ Settings         │
                  │ Send                        │      └──────────────────┘
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                  ┌─────────────────────────────┐
                  │         Amazon SES          │
                  └──────────────┬──────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌───────────────┐        ┌──────────────────┐
            │   Recipient   │        │ Delivery events  │
            │    mailbox    │        └────────┬─────────┘
            └───────────────┘                 │
                                              ▼
                                   ┌──────────────────────┐
                                   │  Event Ingestion     │
                                   └──────────┬───────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                               ▼
                     ┌──────────────────┐          ┌──────────────────┐
                     │    Business      │          │      Audit       │
                     │    DynamoDB      │          │    DynamoDB      │
                     │                  │          │                  │
                     │ Delivery state   │          │ Mail events      │
                     │ Suppression      │          │                  │
                     └──────────────────┘          └──────────────────┘
```

The **mail layer** is the only component that contacts the transport. No other component composes or
sends a message.

The **System table** supplies message content (§8) and configuration (§21).

The **Business table** holds the delivery state of each invitation (§12) and the suppression list
(§14).

The **Audit table** records mail events (§17).

Technical diagnostics are written to Amazon CloudWatch (§18), not to DynamoDB.

---

# 5. Transport

The transport shall be **Amazon SES**.

The transport shall be reached behind an internal interface (§11), so that substituting a transport is
a change of one component rather than a change to the issuance path.

Three properties of this transport are specification-relevant, because requirements in this document
depend on them:

1. **Delivery, bounce and complaint are reported as events.** Design goals 3 and 4 and the delivery
   state machine (§12) are satisfiable only by a transport that reports these outcomes. A transport
   that acknowledges acceptance and reports nothing further cannot distinguish a failed delivery from
   an unopened message, and shall not be adopted without first amending §12.
2. **Sending is authorized by the workload's own identity.** No stored credential is required on the
   send path, satisfying design goal 6.
3. **Event reporting requires no inbound endpoint of its own.** Delivery events are published to a
   topic and delivered to the ingestion endpoint (§13).

Where a transport does not report delivery, §12 requires the delivery state to record that fact rather
than to imply an unknown outcome.

---

# 6. Sender Identity

The recipient is an external executive receiving an authentication link. Sender identity is therefore a
deliverability requirement and a security-perception requirement, not presentation.

### The identity is configuration

The sender identity shall be held as three application settings rather than embedded in this
specification or in the application:

| Setting | Header | Purpose |
|---|---|---|
| `fromName` | `From` display name | The name a recipient reads when deciding whether the message is genuine |
| `fromEmail` | `From` address, and the envelope sender | The address the message authenticates as |
| `replyToEmail` | `Reply-To` | A monitored organizational mailbox that receives replies |

Messages shall be sent with:

```text
From:      "<fromName>" <fromEmail>
Reply-To:  <replyToEmail>
```

For the deployment specified here the values are:

```text
fromName      DXC AI Readiness
fromEmail     no-reply@air.catalyst.one
replyToEmail  a monitored organizational mailbox
```

**The sending domain is the domain part of `fromEmail`.** It is not separately configured, because two
values that must agree and can be set independently will eventually disagree — and the failure of that
disagreement is silent DMARC misalignment, which denies access to every recipient at once (§1). For the
values above the sending domain is `air.catalyst.one`, and §22 specifies the records that domain requires.

### The two addresses are protected; the display name is managed

The mutability classes are those of [DynamoDB System Table](SPEC_data_system.md) §6.1:

| Setting | Class |
|---|---|
| `fromEmail` | **Protected** — deployment provisioning only, no application route |
| `replyToEmail` | **Protected** — deployment provisioning only, no application route |
| `fromName` | **Managed** — editable by `ADMIN` through the application |

The line falls where it does because the two addresses have dependencies outside the application and the
display name has none:

- **`fromEmail` is bound to published DNS and to a verified transport identity.** Changing it through the
  application would leave the new domain without the DKIM, envelope-sender and DMARC records of §22, and
  unverified at the transport. Every subsequent message would fail authentication at the recipient, or be
  refused at the transport, and neither failure announces its cause.
- **`fromEmail` is also the scope of send authorization.** §20.4 requires authorization to send to be
  scoped to this identity, and that scoping lives in the workload's infrastructure permissions rather than
  in the application. An administratively mutable value on one side of that pairing diverges from a fixed
  value on the other, and the symptom is that all sending stops.
- **`replyToEmail` must be a mailbox someone monitors**, which is an arrangement made outside the
  application and cannot be established by writing a value. A recipient who suspects a message inspects
  the reply address, so an address that routes nowhere is worse than the default.
- **`fromName` has no dependency outside the application.** It requires no DNS record, no transport
  verification and no mailbox to exist. It is also the value most likely to need a correction that should
  not wait for a release — a rebrand, a misspelling, a change of product name. Deployment provisioning is
  the wrong gate for a value whose only requirement is that it be well-formed.

Two consequences of `fromName` being managed, and both are requirements rather than observations:

- **Header safety is enforced on the write, not only at startup.** A managed setting changes at runtime,
  so the check that a display name contains no carriage return or line feed (§9) shall run when the value
  is written and shall refuse it there. Validating only at startup would accept an injected value and
  discover it on the next restart, having sent messages in between.
- **The display name is not part of what authenticates the message.** DMARC aligns on the `From` domain,
  which comes from `fromEmail`. A recipient reads the display name and the address together, and where
  they disagree the address governs — which is why the address is the protected half. An administrator can
  therefore make the sender look wrong, and cannot make it be someone else.

### Requirements on the values

The following shall hold, and shall be validated at startup rather than at first send. For `fromName` the
same checks additionally apply on every write, as above:

- `fromEmail` and `replyToEmail` shall each be a syntactically valid address, and shall pass the header
  safety rules of §9. `fromName` shall likewise pass them; a display name containing a line break is a
  header-injection attempt and shall be refused rather than sanitized.
- The domain of `fromEmail` shall be DKIM-signed, with the signing domain equal to that domain, so that
  DMARC alignment is exact (§22).
- A custom envelope-sender subdomain shall be configured for that domain, so that SPF also aligns to the
  sending organization rather than to the transport provider (§22).
- The domain of `fromEmail` shall share one registrable domain with `publicBaseUrl` (§10, §22).
- `replyToEmail` shall be a real, monitored mailbox. An unroutable reply address is itself a phishing
  signal. This cannot be verified by the application — §9 forbids network lookups on the issuance path —
  so it is a deployment obligation rather than a check, and it is stated here because nothing else will
  catch it.

The `From` address shall not accept replies, and the application shall not depend on receiving any. This
is why `replyToEmail` exists as a separate value rather than as an alias of `fromEmail`.

Recipients should be told out of band that an invitation is coming. A named person confirming that a
link is expected is the strongest available control against a recipient mistaking a genuine
authentication link for an attack, and against the converse.

---

# 7. Message Types

There is exactly one outbound message type: the **invitation**.

[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) defines a single credential
concept. Its §9 states that a user who has already authenticated remains eligible, and that
authentication is not a one-time transition out of eligibility. A returning user is therefore issued a
further invitation by the same §12 path. There is no separate sign-in credential, no separate record
type, and no separate message.

The application shall not introduce a second authentication message type. A second type would mean a
second token lifecycle, a second delivery state, and a second set of expiry and single-use rules to
keep consistent, for no difference the recipient can observe.

Sessions are outside this document. The sliding session of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §23 extends a session that
already exists and never issues a credential, so it never sends mail.

---

# 8. Template Resolution and Rendering

Message content shall be resolved from the System table, as specified in
[E-mail Template Storage and Management](SPEC_data_system_templates.md). It shall not be embedded in
the application.

### Resolution

For each send, the mail layer shall resolve the template by identifier, selecting the latest version in
`ACTIVE` state.

The resolved version identifier shall be recorded on the invitation record (§12), so that the content a
recipient was sent remains identifiable after a later version becomes `ACTIVE`.

If no `ACTIVE` version exists for the required template, the send shall fail before the transport is
contacted, and the delivery state shall be `FAILED` (§12). The application shall not fall back to
content compiled into the application, because content that has not been through template versioning
has not been reviewed.

### Rendering

Templates are markdown. The renderer shall produce both parts of a multipart message:

```text
text/plain    rendered from the markdown source
text/html     HTML5 generated from the markdown source
```

Both parts shall be present. A recipient whose client refuses HTML shall still receive a usable link.

### Variable substitution

Template variables shall be substituted by the renderer. The following shall hold:

- A variable present in the template with no supplied value shall cause the render to fail. It shall
  not be silently substituted with an empty string, which would ship a message containing a broken
  link or an empty salutation.
- A supplied value not present in the template shall cause the render to fail, because it indicates
  that the template and its caller have diverged.
- Escaping shall be applied to every substituted value inside the renderer, so that escaping is a
  property of the mechanism and not something the author of a template opts into.

### Markdown as an input surface

Markdown is a richer input surface than a plain placeholder substitution, and the following are
therefore required:

- Raw HTML embedded in a template shall not be passed through to the generated HTML5.
- Automatic linkification shall not be applied to substituted values. A substituted value shall never
  become a link target, because a value that becomes a link in an authentication message is
  indistinguishable to the recipient from the authentication link itself.
- The generated HTML5 shall contain no script, no embedded style capable of concealing content, and no
  remote content that would report on the recipient (§20.2).

Templates shall not hard-code the invitation validity interval. Where the message states how long a
link remains valid, the interval shall be rendered from the invitation record, so that the message and
the record cannot disagree.

---

# 9. Message Construction and Header Safety

The recipient address shall be taken from the authoritative user record, as required by
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §12. It shall never be supplied by
a client.

Two distinct operations apply to addresses and header values, and they shall not be combined:

| Operation | Behaviour | Applies to |
|---|---|---|
| Normalization | Transforms the value, per the normalization policy of §8 of [Passwordless Email Authentication](SPEC_passwordless_email_auth.md) | E-mail addresses, at the boundary, exactly once |
| Header safety | Refuses the value; never transforms it | Every header value, including display names and subjects |

Normalization determines the identity key of an account and cannot change without re-keying every
account. Header safety guards values that must not be transformed at all — lowercasing a subject line
would corrupt it. A single combined operation would either corrupt a subject or allow a display name to
become an identity key.

The following shall hold:

- No header value shall contain a carriage return or line feed. A value containing one shall be
  refused, not sanitized, because a sanitized value silently changes what was sent.
- Message assembly shall use a mechanism that refuses malformed header values structurally, as a second
  line of defence independent of the check above.
- Address validation shall not perform network lookups. Verifying deliverability by querying the
  recipient's domain places a network call on the issuance path, and the issuance path shall not depend
  on a third party being reachable.

---

# 10. Link Construction

The magic-link URL shall be constructed from a configured base URL (§21).

The base URL **shall not** be derived from the `Host` header, or from any other request-supplied value,
of the request that triggered the send. An attacker able to influence that value would receive an
authentication link pointing at a host under their control, which under
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §47 is the whole of
authentication.

The following shall hold:

- The configured base URL shall use `https`. A non-`https` value shall be refused in a production
  environment rather than accepted with a warning.
- The token shall appear in the URL path, as specified by
  [Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §13, and never in a query
  string. Query strings reach access logs and `Referer` headers; paths are also logged, which is why
  §18 additionally forbids logging the path of an invitation request.
- The link host and the sending domain shall share one registrable domain (§22).

---

# 11. Send Contract

The mail layer shall expose a send operation whose result is one of:

```text
SENT         accepted by the transport
REJECTED     refused by the transport; the message will not be delivered
DEFERRED     not accepted, but a retry may succeed
AMBIGUOUS    no response; the message may or may not have been accepted
```

These are transient outcomes of one call. They are not stored, and they are therefore not a dictionary
value; the stored state is `deliveryStatus` (§12), drawn from DELIVERY_STATUS in
[Common Dictionaries](dictionaries.md).

### The send operation shall not raise

A transport failure shall be returned as an outcome, not raised as an error. Issuance is a deliberate
administrative action whose outcome shall be reported to the issuer; an unhandled error would instead
present as a failed request, leaving the issuer unable to distinguish a mail problem from an
application fault.

Where an unexpected error escapes the transport, the mail layer shall convert it to `DEFERRED` and
record the error's type only. It shall not record the error's message, which may contain the rendered
body and therefore the token (§16).

### Retry

| Outcome | Retry |
|---|---|
| `SENT` | Not applicable |
| `REJECTED` | Never |
| `DEFERRED` | Once, after a randomized delay |
| `AMBIGUOUS` | **Never** |

`AMBIGUOUS` shall not be retried. A retry that succeeds after an unacknowledged send that also
succeeded places two live invitations in one mailbox. Under
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §13 a live token is a bearer
credential, so a duplicate is a duplicate credential — a worse outcome than a message the recipient
never receives, which is recoverable by a resend (§15).

### Capability reporting

The mail layer shall report whether the configured transport reports delivery, and this shall be
evaluated against live configuration rather than assumed from the choice of transport. Amazon SES
reports delivery events only when event publication is configured; a transport selected but not fully
configured does not report delivery, and shall not claim to.

The interface shall not assume that any transport reports delivery. Callers shall ask.

---

# 12. Delivery Status

### The record is written before the send

The invitation record shall be created, with its delivery state, **before** the transport is contacted.

The order is not an optimization. [Passwordless Email Authentication](SPEC_passwordless_email_auth.md)
§12 stores the token hash before sending; the reverse order — send, then record — allows a record write
to fail after a message has been delivered, leaving a live magic link in a mailbox that validates
against nothing. That link cannot be revoked, because nothing records that it exists.

### Attributes

The invitation record (§14 of [Passwordless Email Authentication](SPEC_passwordless_email_auth.md))
carries:

```json
{
  "deliveryStatus": "SENT",
  "deliveryReporting": "SUPPORTED",
  "deliveryDetail": null,
  "deliveredAt": null,
  "providerMessageId": "0100018f...",
  "templateVersion": 4,
  "resendCount": 0
}
```

Permitted values of `deliveryStatus` are defined by DELIVERY_STATUS, and of `deliveryReporting` by
DELIVERY_REPORTING, in [Common Dictionaries](dictionaries.md).

`deliveryDetail` is free text for an operator. It shall not contain the token, the rendered body, or a
transport error message (§16).

### State machine

```text
QUEUED ──SENT──▶ SENT ──event──▶ DELIVERED
   │                │
   │                ├──event──▶ BOUNCED
   │                │
   │                └──event──▶ COMPLAINED
   │
   ├──REJECTED, or DEFERRED exhausted──▶ FAILED
   │
   └──AMBIGUOUS──▶ SENT
```

`QUEUED` is the state at record creation, before the transport is contacted.

`AMBIGUOUS` resolves to `SENT`, with `deliveryDetail` recording that the transport gave no
confirmation. It shall not resolve to `FAILED`, because the message may have been delivered, and it
shall not resolve to `SENT` silently, because the issuer is entitled to know the difference.

`COMPLAINED` is terminal and additionally writes a suppression record (§14).

### Reporting capability is snapshotted

`deliveryReporting` shall be written at send time from the capability reported in §11, and shall not be
evaluated when the record is later read.

A record sent under a transport that reported delivery remains readable as such after the transport is
reconfigured or replaced. Evaluating capability at read time would retroactively reinterpret history.

### Honest presentation

Where `deliveryReporting` is `UNAVAILABLE`, an interface showing invitation state shall show `SENT`
together with an explanation that the transport does not report delivery.

It shall not show `DELIVERED`, which it cannot know, and it shall not show a pending indicator that
will never resolve. Under a non-reporting transport, design goal 4 is genuinely unmet, and the
interface shall say so rather than imply an answer.

---

# 13. Delivery Event Ingestion

Delivery events shall be received at:

```http
POST /mail/events/{secret}
```

The route shall be registered ahead of any catch-all route, so that it is not shadowed.

This endpoint is reachable without a session. It is network-public and payload-authenticated, and it
shall be recorded as such wherever the application's routes are enumerated. It is not public in the
authorization sense.

### Authentication

An unauthenticated version of this endpoint is a status-forgery vulnerability: any caller could mark an
invitation `BOUNCED` and drive an issuer into a resend loop, or mark it `COMPLAINED` and suppress a
legitimate recipient permanently (§14). Two independent gates shall therefore both be required:

1. A shared secret in the path, compared using a constant-time comparison.
2. Verification of the publisher's message signature. The topic identifier shall match configuration,
   and the host serving the signing certificate shall match an expected pattern for the transport
   provider's signing endpoints. A look-alike certificate host is the classic bypass of signature
   verification and shall be rejected on the host check alone.

Failure of either gate shall be logged (§18) and shall not reveal which gate failed.

### Application of events

Events shall be applied by locating the invitation through `providerMessageId` (§23).

The following shall hold:

- **Idempotent.** Event delivery is at-least-once. Applying the same event twice shall have the same
  effect as applying it once.
- **Ordered by precedence, not arrival.** Event delivery is unordered. State shall be applied under a
  conditional write honouring:

  ```text
  COMPLAINED > BOUNCED > DELIVERED > SENT > QUEUED
  ```

  A late `DELIVERED` shall not overwrite a `COMPLAINED`.
- **Only permanent failures set `BOUNCED`.** A transient failure shall record `deliveryDetail` and
  leave `deliveryStatus` as `SENT`. Treating a temporarily full mailbox as a bounce presents a correct
  address as a wrong one, and invites an operator to correct an address that is not wrong.

### Response

The endpoint shall return success for any event it accepts **or deliberately ignores**, and a failure
status only where the caller should retry. Publishers retry non-success responses for an extended
period, so returning failure for an event that will never be accepted produces sustained load and
obscures real failures.

---

# 14. Complaint Suppression

A recipient who reports a message as unsolicited shall not be mailed again.

This requirement is load-bearing rather than courteous. Continued sending to an address that has
complained degrades the sending domain's reputation, and under §1 the sending domain is the
authentication channel for every user. The failure mode is loss of access for the whole population,
not a degraded experience for one recipient.

### Record

A `COMPLAINED` event shall write a suppression record to the Business table:

```text
PK = MAIL_SUPPRESSION#<normalizedEmail>
SK = METADATA
```

```json
{
  "PK": "MAIL_SUPPRESSION#john.smith@example.com",
  "SK": "METADATA",
  "entityType": "MAIL_SUPPRESSION",

  "email": "john.smith@example.com",
  "reason": "COMPLAINT",
  "suppressedAt": "2026-08-09T15:00:00Z",
  "userId": "01JXYZ..."
}
```

The address shall be normalized by the same policy applied at §9, so that a lookup cannot miss a record
because of case.

`userId` records the account the complaint arrived from, where one is known. The suppression record is
keyed by address rather than by user because suppression follows the mailbox: a mailbox reassigned to
another account is the same mailbox to the transport provider.

### Enforcement

Invitation issuance and resend shall consult the suppression list **before** contacting the transport,
and shall refuse where a record exists.

Refusal shall be reported to the issuer as a distinct outcome, not as a generic failure. An issuer who
cannot tell suppression from a transport fault will retry indefinitely.

The suppression check is a precondition of issuance, and its result shall not be inferred from a later
delivery outcome.

### Removal

Removal of a suppression record shall be an explicit action available only to `ADMIN`
([Role Model](role_model.md)), and shall be recorded in the Audit table (§17).

Removal shall not be automatic and shall not expire on a timer. A record that lapses without anyone
deciding it should lapse reproduces the condition it exists to prevent.

### Relationship to provider-side suppression

The transport provider maintains its own suppression list. That list protects the sending domain but is
not visible to the application, so a send dropped by the provider is indistinguishable to the issuer
from one that succeeded. The application's own list exists so that the reason a message was not sent is
recorded where the issuer can see it.

---

# 15. Resend and Idempotency

Repeated issuance for the same user shall not mint a second live credential.
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §15 requires normally one active
invitation per user; this section specifies what a repeated request does.

| Condition at request | Action | `resendCount` |
|---|---|---|
| No live invitation | Mint a token and send | Set to 0 |
| Live invitation, `SENT` or `DELIVERED` | No action; report already invited | Unchanged |
| Live invitation, `QUEUED` or `FAILED` | Re-send the **existing** token | Increment |
| Live invitation, `BOUNCED` | Re-send the existing token | Increment |
| Address suppressed (§14) | Refuse; report suppressed | Unchanged |
| `resendCount` at the configured limit | Refuse; explicit re-issue required | Unchanged |

A re-send shall re-send the existing token rather than mint a new one, so that a repeated request
cannot leave two live credentials in one mailbox.

`resendCount` counts deliberate resends and resends following a delivery failure. It shall **not** be
incremented by:

- a repeated identical issuance request that results in no action, because one accidental duplicate
  request would otherwise consume the allowance for every affected user at once;
- the retry within a single send (§11), which retries one message at the transport level and is not
  visible above the send interface.

Reaching the limit shall not silently stop mail. It shall refuse, and the refusal shall be visible to
the issuer.

---

# 16. Token Secrecy in the Mail Path

[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §13 makes the token a bearer
credential and §40 restricts where it may appear. This section states what that requires of the mail
path, and requires it structurally rather than by convention.

The following shall hold:

- The raw token shall exist only as an input to rendering (§8) and within the resulting message body.
- The raw token shall never be an attribute of any record, a correlation identifier, or a field of a
  send outcome (§11). The invitation record stores `tokenHash` only.
- Diagnostic representations of a message shall redact the body and any attachment. A message object
  rendered into a log line or a stack trace shall not disclose the link.
- A development or test transport shall not write a token through the application's logging mechanism.
  Where standard output is collected as a log stream, writing a rendered message to standard output
  publishes the token to the log store.
- A test transport shall be distinct from a development transport, so that running tests neither prints
  nor persists a token.
- A transport intended for development shall refuse to start in a production environment. A deployment
  that omits transport configuration then fails on its first invitation instead of silently discarding
  all authentication mail — the safer failure, given §1.
- Open and click tracking shall be disabled (§20.2). Click tracking rewrites links, which places the
  raw token in the provider's event data and from there into telemetry.

---

# 17. Audit Events

The following event types extend the Audit table event list of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §29:

```text
INVITATION_EMAIL_QUEUED
INVITATION_EMAIL_SENT
INVITATION_EMAIL_FAILED
INVITATION_EMAIL_DELIVERED
INVITATION_EMAIL_BOUNCED
INVITATION_EMAIL_COMPLAINED
INVITATION_EMAIL_RESENT
MAIL_SUPPRESSION_ADDED
MAIL_SUPPRESSION_REMOVED
```

Audit records shall follow §30 of [Passwordless Email Authentication](SPEC_passwordless_email_auth.md):
keyed by `userId`, append-oriented, and carrying `userId` rather than unnecessary personal data.

`MAIL_SUPPRESSION_ADDED` and `MAIL_SUPPRESSION_REMOVED` necessarily concern an address rather than only
a user. They shall record the address, because a suppression record that cannot be traced to a decision
cannot be reviewed. `MAIL_SUPPRESSION_REMOVED` shall additionally record the acting `userId`, since
removal is an administrative action (§14).

No mail audit record shall contain the token, the rendered body, or the `providerMessageId` where the
latter is not required for correlation.

---

# 18. Technical Logs

Operational diagnostics for the mail path shall be written to Amazon CloudWatch, under §31 of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md). They shall not be written to
DynamoDB.

Delivery outcomes are **not** technical logs. A delivery outcome is a durable state an issuer acts on,
and it belongs on the invitation record (§12). A log entry that expires under a retention policy cannot
answer why a user never received an invitation.

Mail log entries shall not contain:

- magic-link tokens;
- the path of an invitation request, which contains the token;
- rendered message bodies, in whole or in part;
- transport error messages that may echo the body;
- template source;
- the shared secret of the ingestion endpoint (§13);
- recipient addresses, beyond where necessary to diagnose a delivery failure.

Where user correlation is required, `userId` shall be used.

---

# 19. GDPR

Two records introduced by this specification hold personal data and are therefore subject to §34 of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md).

### Delivery attributes on the invitation record

These live on a record the erasure workflow already locates through `userId`, and require no separate
treatment.

### Suppression records

A suppression record is keyed by an e-mail address and contains that address. It therefore holds
personal data, and it lies **outside** the erasing user's partition — it is keyed by
`MAIL_SUPPRESSION#<normalizedEmail>`, not by `USER#<userId>`.

The erasure workflow shall therefore locate suppression records explicitly, in the same way §34 locates
the email lookup record. A workflow that queries only the user's partition will miss it.

Whether a suppression record is erased with the user is a retention decision, not a technical one, and
the tension is real:

- Erasing it restores the ability to mail an address that asked not to be mailed.
- Retaining it keeps an address on file for a person who has asked to be forgotten.

The organization shall classify suppression records under §35 of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md), alongside audit records. Where
they are retained, the retained record shall hold the minimum required to prevent a further send, and
`userId` should be removed so that the retained address is no longer linked to an erased account.

---

# 20. Security Requirements

## 20.1 Transport security

Connections to the transport shall use TLS. Delivery event ingestion (§13) shall be served over HTTPS,
under §38.1 of [Passwordless Email Authentication](SPEC_passwordless_email_auth.md).

## 20.2 Tracking prohibition

Open tracking and click tracking shall be disabled at the transport.

Click tracking rewrites every link in the message, including the magic link. The rewritten link places
the raw token in the provider's event data and in any telemetry derived from it, which §16 and §40 of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) forbid. Open tracking embeds
remote content that reports on the recipient, which serves no purpose in an authentication message.

## 20.3 Ingestion endpoint authentication

Both gates of §13 shall be required. Neither alone is sufficient.

## 20.4 Send authorization

Authorization to send shall be scoped to the sending identity of §6. A workload compromised through
another path shall not be able to send from an arbitrary address of the sending domain.

## 20.5 Rate limiting

Rate limiting shall be applied to:

- invitation issuance, per user and in aggregate;
- resend requests;
- delivery event ingestion.

Aggregate limiting matters independently of per-user limiting: a fault that issues to many users once
each damages the sending domain as effectively as one that issues to one user many times.

## 20.6 Configuration integrity

The shared secret of §13 shall be held as a secret and shall not be stored in the System table (§21).
A value readable by anyone who can read application settings is not an authentication gate.

---

# 21. Configuration

Configurable values shall be held as application settings in the System table, as specified in
[DynamoDB System Table](SPEC_data_system.md), except where marked secret below.

The **Class** column is the mutability class of that document's §6.1. A **protected** setting is written
by deployment provisioning only, with no application route; a **managed** setting is editable by `ADMIN`
through the application. The classes are registered in that document's §6.2, and this table shall agree
with it.

| Setting | Class | Purpose |
|---|---|---|
| `mailTransport` | Protected | Selected transport, including development and test transports (§16) |
| `environment` | Protected | Whether the deployment is production, governing §10 and §16 refusals |
| `publicBaseUrl` | Protected | Base URL for link construction (§10) |
| `fromEmail` | Protected | `From` address and envelope sender; its domain is the sending domain (§6) |
| `fromName` | Managed | `From` display name; header safety checked on write (§6) |
| `replyToEmail` | Protected | Monitored reply mailbox (§6) |
| `mailSendTimeoutSeconds` | Managed | Timeout after which an unacknowledged send is `AMBIGUOUS` (§11) |
| `mailMaxResends` | Managed | Resend limit (§15) |
| `mailEventTopic` | Protected | Delivery event topic identifier, verified at ingestion (§13) |
| `mailDeliveryReportingConfigured` | Protected | Whether event publication is configured, determining reported capability (§11) |
| `invitationTemplateId` | Managed | Template identifier resolved at §8 |
| `mailEventSecret` | **Secret** | Shared secret of the ingestion endpoint (§13), held outside the System table entirely (§20.6) |

Values governing refusal in production — `environment`, `publicBaseUrl` and `mailTransport` — shall be
validated at startup rather than at first send, so that a misconfigured deployment fails before it
accepts an issuance request. The sender identity of §6 shall be validated in the same pass, for the same
reason: a deployment whose `From` domain has no published records cannot deliver anything, and the useful
moment to discover that is before the first invitation rather than during it.

Three of the protected classifications are worth their justification here, since the remainder follow
from §6 and §10:

- `mailEventTopic` and `mailDeliveryReportingConfigured` are the two halves of the delivery-event gate.
  Editing the topic identifier redirects which publisher is trusted at §13; editing the reporting flag
  makes the interface claim a capability the transport does not have, which §12 exists to prevent.
- `invitationTemplateId` is managed, because selecting a reviewed template is an ordinary administrative
  act. What protects it is that the template it names must itself be `ACTIVE` and versioned (§8), so the
  setting selects among reviewed content rather than supplying content.

---

# 22. DNS and Domain Requirements

The sending domain is the domain part of `fromEmail` (§6), which is `air.catalyst.one` for the deployment
specified there. Sending from it requires records to be published for that domain:

```text
DKIM            signing records for the sending domain
Envelope sender records for the custom envelope-sender subdomain
DMARC           policy record for the sending subdomain
```

The following shall hold:

- DKIM records shall be published for the sending domain itself, so that the signing domain and the
  `From` domain match exactly and DMARC aligns.
- Envelope-sender records shall be published for a subdomain of the sending domain, so that SPF aligns
  to the sending organization rather than to the transport provider.
- A DMARC policy shall be published for the sending subdomain deliberately, rather than inherited from
  the parent domain's subdomain policy.
- The application hostname and the sending domain shall share one registrable domain. An authentication
  link pointing at a host unrelated to the sending domain reads as an attack to a recipient and to
  intermediate mail security systems, regardless of how the message authenticates.

Record publication shall be arranged so that routine changes — key rotation, and the addition of an
environment — do not require an external change for each record.

---

# 23. Recommended Access Patterns

### Locate a suppression record

```text
PK = MAIL_SUPPRESSION#<normalizedEmail>
SK = METADATA
```

Consulted before every send (§14).

### Locate an invitation by provider message identifier

Delivery events identify a message by the transport provider's identifier, not by `invitationId`, so
the invitation cannot be located by primary key. This requires an index on `providerMessageId`,
specified in [DynamoDB Business Table](SPEC_data_business.md).

```text
providerMessageIdIndex
    PK = providerMessageId
```

The index need project only the keys required to locate the base record, since applying an event reads
and conditionally updates that record.

---

# 24. Access

See [Role Model](role_model.md)

---

# 25. Summary

The magic link is the only way into the application, so this specification treats the act of sending it
as a recorded operation rather than a side effect.

```text
Suppression checked
       │
       ▼
Invitation record written, QUEUED
       │
       ▼
Template resolved from the System table, ACTIVE, latest version
       │
       ▼
Rendered — token enters the body and nowhere else
       │
       ▼
Sent through Amazon SES from the sending domain
       │
       ▼
Outcome recorded: SENT, FAILED, or SENT with no confirmation
       │
       ▼
Delivery event received, authenticated twice, applied by precedence
       │
       ▼
DELIVERED, BOUNCED, or COMPLAINED — and a complaint suppresses the address
```

Three rules carry most of the weight:

```text
The record is written before the send,
    so a live link always validates against something.

An unacknowledged send is never retried,
    so one invitation never becomes two credentials.

Delivery is reported, never assumed,
    and where it cannot be reported, the interface says so.
```

The governing principle is:

> **A message handed to a transport is not a message delivered. The invitation record states what is
> actually known about the message, and where nothing is known, it says that instead of guessing.**
