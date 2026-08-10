# AdvisorX Engineering Specification
# Passwordless Email Authentication with DynamoDB

**Status:** Proposed  
**Authentication model:** Passwordless, email-based magic link  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** Business, Audit, System

---

## 1. Purpose

This specification defines a passwordless authentication system for an application with a **closed, pre-provisioned user population**.

Users are not permitted to self-register.

The application already knows each authorized user's:

- email address;
- full name;
- company name;
- organization;
- application role (see [Role Model](role_model.md));
- position/title.

This information is stored directly in the **Business DynamoDB table**, which is the authoritative user directory and application system of record.

Authentication is based on proof of possession of the provisioned email account through a short-lived, single-use magic link.

The system does not store:

- passwords;
- password hashes;
- security questions;
- permanent authentication secrets associated with the user.

The system creates a temporary authenticated browser session after successful magic-link verification.

---

# 2. Design Goals

The authentication architecture shall provide:

1. Passwordless authentication.
2. No self-registration.
3. Authentication restricted to provisioned email addresses.
4. Single-use magic-link credentials.
5. Protection against email-security scanners consuming authentication links.
6. Sliding authenticated sessions.
7. Server-side authorization based on `userId`.
8. Separation of business data, audit data, and technical telemetry, the last of which is held outside DynamoDB.
9. Efficient user-oriented data deletion.
10. Minimal duplication of PII.
11. Explicit support for GDPR data-erasure workflows.
12. No dependency on an external identity provider.
13. Capture of the user's consent decisions before the first authenticated session exists.
14. A recovery path to administrative access that does not require an existing administrative account.

---

# 3. Non-Goals

The system does not provide:

- username/password authentication;
- password reset;
- self-service registration;
- arbitrary email registration;
- account recovery in any sense beyond re-sending a link to an address already in the directory (§12.1);
- identity verification beyond possession of the provisioned mailbox;
- government/official identity verification;
- independent MFA;
- a password-style break-glass or bootstrap credential.

The last exclusion is deliberate and has no exception. Administrative access is recovered by §50, which
uses the same mailbox-possession factor as every other account, so there is no account anywhere in the
system that authenticates by a stored secret — not once, not at first deployment.

If stronger authentication is required later, an additional authentication factor can be introduced without changing the fundamental user identity model.

---

# 4. High-Level Architecture

```text
                  ┌─────────────────────────────┐
                  │      Application Client     │
                  └──────────────┬──────────────┘
                                 │
                                 │ HTTPS
                                 ▼
                  ┌─────────────────────────────┐
                  │       Application API       │
                  │                             │
                  │ Authentication              │
                  │ Authorization               │
                  │ Business operations         │
                  └──────────────┬──────────────┘
                                 │
                ┌────────────────┼─────────────────┐
                │                │                 │
                ▼                ▼                 ▼
       ┌────────────────┐ ┌──────────────┐ ┌─────────────────────┐
       │    Business    │ │    Audit     │ │     System          │
       │    DynamoDB    │ │   DynamoDB   │ │   DynamoDB          │
       │                │ │              │ │                     │
       │ Users          │ │ Auth events  │ │ Versioned Consents  │
       │ Invitations    │ │ Security     │ │ Settings            │
       │ Sessions       │ │ Changes      │ │ E-mail templates    │
       │ Interviews     │ │ Erasure      │ │ Versioned Prompts   │
       │ Synth outputs  │ │              │ │                     │
       │ Quick wins     │ │              │ │                     │
       │ Consent facts  │ │              │ │                     │
       └────────────────┘ └──────────────┘ └─────────────────────┘
```

The **Business table** is the authoritative application database. This document specifies only its
authentication entities; its business entities are specified in
[DynamoDB Business Table](SPEC_data_business.md).

The **Audit table** is an append-oriented record of security and business-significant events.

The **System table** contains system global settings, versioned consents (text), versioned prompts and versioned e-mail templates.

Consents are split across two of these stores, and deliberately so. The consents that exist and may be
presented are versioned reference data in the System table; what a given user decided about them is a
fact about that user and lives in the Business table, under that user's partition. Both sides are
specified in [Consents Storage and Management](SPEC_data_system_consents.md); the moment the facts are
captured is specified in §49 of this document.

Outbound mail is not a fourth store but a dependency of the authentication path: the magic-link email
is composed from System-table templates, its delivery state is recorded on the Business-table
invitation record, and its outcomes are recorded in the Audit table. The transport, the sender
identity and the delivery model are specified in
[Outbound Mail Transport](SPEC_outbound_mail.md).

---

# 5. Authoritative User Directory

The Business DynamoDB table is the authoritative user directory.

There is no external identity provider or external user directory.

The configured administrator list of §50 is not an exception to this. It holds email addresses and
nothing else: no profile, no role assignment beyond the one role it can confer, and no authorization
input consulted on an authenticated request. It names who may cause an administrative record to exist
in this table; the record, once it exists, is the authority. A directory answers "who is this user";
that list answers only "may this address recover administrative access".

Each provisioned user has a unique, opaque `userId`.

Example:

```json
{
  "PK": "USER#01JXYZ...",
  "SK": "PROFILE",
  "entityType": "USER",

  "userId": "01JXYZ...",

  "email": "john.smith@example.com",
  "fullName": "John Smith",
  "companyName": "Northwind Manufacturing",
  "position": "Head of Operations",

  "orgId": "01JORG...",
  "role": "POWER_USER",

  "status": "PROVISIONED",

  "createdAt": "2026-08-09T15:00:00Z",
  "updatedAt": "2026-08-09T15:00:00Z"
}
```

The authoritative profile attributes are:

```text
email
fullName
companyName
position
orgId
role
status
```

`role` lives on the `USER#<userId> / PROFILE` item and is the single source of authorization truth
(§11). Permitted values are defined by ROLE in [Common Dictionaries](dictionaries.md), and the
capabilities of each role by the [Role Model](role_model.md).

`orgId` is the stable identifier of the organization the user belongs to. `companyName` is a display
snapshot and shall not be used as an organization identifier. The organization entity itself is
specified outside this document.

These values are not supplied by the browser during authentication.

---

# 6. User Identity

`userId` is the application's canonical identity identifier.

It shall be:

- opaque;
- stable;
- unique;
- non-meaningful;
- generated using a collision-resistant mechanism.

It shall not contain:

- email address;
- name;
- company name;
- position.

All business data should reference the user using `userId`.

Example:

```text
USER#01JXYZ...
```

rather than:

```text
USER#john.smith@example.com
```

This decouples application identity from mutable personal attributes.

---

# 7. User Provisioning

Users shall be provisioned through an authorized administrative or system process.

Provisioning creates the authoritative Business-table user record.

Example:

```text
Authorized administrator
          │
          ▼
Create user
          │
          ├── userId
          ├── email
          ├── fullName
          ├── companyName
          ├── position
          ├── orgId
          ├── role
          └── status=PROVISIONED
```

Only users who exist in the directory and are eligible (§9) may receive authentication invitations.

There is no public registration endpoint.

## 7.1 The first administrator

This section is circular on its own. Provisioning requires an authorized administrator, and an
administrator is a provisioned user, so a deployment whose directory is empty has no route by which its
first administrative record can come into existence. The same circularity recurs after first deployment
whenever the administrative population is lost rather than absent — every `ADMIN` account suspended in
error, deleted, or bound to a mailbox nobody can still reach.

The single origin of an administrative record that no authenticated administrator created is specified
in §50. It is the only provisioning path in this document not initiated by an authorized caller inside
the application, and it exists for that reason alone.

---

# 8. Email Uniqueness

Each active authoritative email address shall map to exactly one user.

The Business table should maintain an email lookup item.

Example:

```text
PK = EMAIL#john.smith@example.com
SK = USER
```

```json
{
  "PK": "EMAIL#john.smith@example.com",
  "SK": "USER",
  "entityType": "EMAIL_LOOKUP",
  "userId": "01JXYZ..."
}
```

User creation and email lookup creation shall be performed atomically.

A DynamoDB transaction or equivalent conditional-write strategy shall prevent two users from claiming the same normalized email address.

The application shall define and consistently apply an email normalization policy.

---

# 9. User Status

Recommended states:

```text
PROVISIONED
INVITED
ACTIVE
SUSPENDED
DELETED
```

### PROVISIONED

The user exists and is authorized to authenticate.

### INVITED

An authentication invitation has been issued.

### ACTIVE

The user has successfully authenticated.

### SUSPENDED

The user remains in the directory but cannot authenticate or access protected resources.

### DELETED

The user's data has been deleted or anonymized according to the applicable retention policy.

The application may simplify the model by omitting `INVITED` and deriving invitation state from active invitation records.

### Eligibility for authentication

A user is **eligible** for authentication when `status` is one of:

```text
PROVISIONED
INVITED
ACTIVE
```

A user is **not eligible** when `status` is one of:

```text
SUSPENDED
DELETED
```

This is the normative definition of eligibility. Every eligibility check in this document refers to
it, and no other definition shall be introduced.

A user who has already authenticated is `ACTIVE` and remains eligible; authentication is not a
one-time transition out of eligibility.

The administrative recovery path of §50 does not alter this definition and introduces no second one. It
can cause an eligible record to exist where none did; it cannot make a `SUSPENDED` or `DELETED` record
eligible. §50.2 states the consequence, which is that suspension remains effective against an address
named in the configured list.

---

# 10. Business DynamoDB Table

The authentication entities in the Business table are:

- authoritative users;
- email lookup records;
- authentication invitations;
- authentication sessions.

A single-table design is recommended.

Example:

```text
PK                         SK
────────────────────────   ─────────────────────
USER#01JXYZ...             PROFILE

EMAIL#john@example.com     USER

INVITATION#01KDEF...       METADATA

SESSION#9f2a7c...          METADATA
```

Application business entities share the same table and are specified in
[DynamoDB Business Table](SPEC_data_business.md). Their key layout is not defined here.

Permitted `entityType` values are defined by ENTITY_TYPE in
[Common Dictionaries](dictionaries.md).

---

# 11. Separation of Identity and Authorization

Authentication identifies the user:

```text
session → userId
```

Authorization determines what that user may do:

```text
userId → application permissions
```

The user's company position must not automatically be interpreted as an application role.

For example:

```text
position = "Head of Operations"
```

does not necessarily imply:

```text
role = "ADMIN"
```

Application authorization shall be represented separately, by `role`.

Example:

```text
USER#U123
│
├── fullName: John Smith
├── companyName: Northwind Manufacturing
├── position: Head of Operations
│
└── authorization
    ├── role: POWER_USER
    └── orgId: 01JORG...
```

The permitted values of `role` are defined by ROLE in [Common Dictionaries](dictionaries.md) and are
not restated here.

What each role may do is defined by the [Role Model](role_model.md) and is likewise not restated
here.

`role` and `orgId` are written server-side by the provisioning process (§7), or by the administrative
recovery path of §50 for the one role it can confer. They shall never be supplied by the browser,
consistent with §24.

---

# 12. Invitation Generation

An authorized application component shall generate invitations using `userId`.

Example:

```http
POST /auth/invitations
```

Request:

```json
{
  "userId": "01JXYZ..."
}
```

The server shall:

1. Retrieve the authoritative user record.
2. Verify that the user is eligible for authentication (§9).
3. Retrieve the authoritative email.
4. Verify that the email address is not suppressed
   ([Outbound Mail Transport](SPEC_outbound_mail.md) §14).
5. Generate a cryptographically secure random token.
6. Store only the token hash.
7. Create the invitation record, including its initial delivery state (§14).
8. Send the magic-link email through the outbound mail transport
   ([Outbound Mail Transport](SPEC_outbound_mail.md)).
9. Record the send outcome on the invitation record.

The invitation record shall be created before the email is sent. The reverse order permits a record
write to fail after a message has been delivered, leaving a live magic link in a mailbox that
validates against nothing and that no record knows exists.

The client shall not provide an arbitrary destination email address.

This endpoint requires a `userId` and therefore cannot serve a caller who does not know one. Two other
routes reach this issuance path with an email address instead: self-service re-authentication (§12.1) and
administrative recovery (§50). They are the only routes in this document that accept an email address
from the caller, and in both the address is a lookup key rather than a destination.

## 12.1 Self-service re-authentication

A user whose session has ended shall be able to obtain a new invitation without an administrator acting
for them.

```http
POST /auth/request-link
```

The route is specified at §41.8. This section specifies what the server does.

On receiving an address, the server shall:

1. Normalize the submitted address under §8.
2. Resolve it through the email lookup item (§8) to a `userId`.
3. Retrieve the authoritative user record.
4. Verify that the user is eligible for authentication (§9).
5. Verify that the address **on the user record** is not suppressed
   ([Outbound Mail Transport](SPEC_outbound_mail.md) §14).
6. Apply the resend and idempotency rules of
   [Outbound Mail Transport](SPEC_outbound_mail.md) §15, which govern whether this mints a new token,
   re-sends an existing one, or does nothing.
7. Issue through §12 where §15 calls for a send.

**The message is sent to the address on the user record, never to the submitted string.** After
normalization the two are equal whenever the lookup succeeded, so the rule appears to be a formality. It
is not: it means the destination is read from the directory in every case, and no future change to
normalization, to the lookup, or to this route can turn a caller-supplied string into a delivery target.
That is the property §12 protects, and it is preserved here rather than excepted.

**Every outcome returns the same response** (§41.8), including a successful send, an address that resolves
to nothing, an ineligible user, a suppressed address, and a resend limit already reached. §39 requires
this: a route that took an address and answered differently for a known one would enumerate the user
population, and this route is reachable by anyone.

**The refusals are recorded even though they are not reported.** Reaching the resend limit refuses the
send, and [Outbound Mail Transport](SPEC_outbound_mail.md) §15 requires that refusal to be visible rather
than silent. There is no issuer here to show it to, so visibility is satisfied by the audit event (§29) and
not by the response. A user who cannot get in and has been told to check their mail is a support case, and
the audit trail is what lets support answer it.

**This is not self-registration** (§3). No account is created, no attribute is accepted from the caller,
and an address with no record produces no record. The route can only cause a message to be sent to a
mailbox already in the directory.

Without this route, a session that ends leaves the user dependent on an administrator issuing a fresh
invitation for them. That is the condition §23's absolute lifetime creates on a schedule, for every user,
and it is not a support load any administrator should carry.

---

# 13. Magic-Link Token

The invitation token shall be generated using a cryptographically secure random number generator.

At least 256 bits of entropy are recommended.

Conceptually:

```text
token     = CSPRNG(256 bits)
tokenHash = SHA-256(token)
```

The email contains:

```text
https://app.example.com/invite/<token>
```

The Business table stores:

```text
tokenHash
```

and never the plaintext token.

The token shall be treated as a bearer credential.

The token is not the `invitationId`. These are two distinct values with two distinct purposes:

| Value | Purpose | Generation | Stored |
|---|---|---|---|
| `invitationId` | Record identifier (§14, §44) | May be a sortable identifier such as a ULID | Yes, in plaintext |
| `token` | Bearer credential in the magic link | CSPRNG, ≥256 bits | Never; only `tokenHash` |

An identifier that encodes a timestamp, is monotonic, or is otherwise predictable shall never be used
as a credential. A ULID is an identifier, not a credential.

---

# 14. Invitation Record

Example:

```json
{
  "PK": "INVITATION#01KDEF...",
  "SK": "METADATA",
  "entityType": "INVITATION",

  "invitationId": "01KDEF...",
  "userId": "01JXYZ...",

  "tokenHash": "<SHA-256>",
  "expiresAt": "2026-08-10T15:00:00Z",

  "deliveryStatus": "SENT",
  "deliveryReporting": "SUPPORTED",
  "deliveryDetail": null,
  "deliveredAt": null,
  "providerMessageId": "0100018f...",
  "templateVersion": 4,
  "resendCount": 0,

  "createdAt": "2026-08-09T15:00:00Z",
  "consumedAt": null
}
```

The delivery attributes record what is known about the email carrying this invitation. Permitted
values of `deliveryStatus` are defined by DELIVERY_STATUS, and of `deliveryReporting` by
DELIVERY_REPORTING, in [Common Dictionaries](dictionaries.md). Their semantics, the state machine
that governs transitions between them, and the accounting rule for `resendCount` are specified in
[Outbound Mail Transport](SPEC_outbound_mail.md) and are not restated here.

They live on the invitation record rather than in a technical log because a failure to reach the
mailbox denies access, and whoever issued the invitation shall be able to distinguish that failure
from a recipient who has simply not yet clicked.

The invitation references `userId` rather than duplicating:

```text
email
fullName
companyName
position
```

The authoritative user record remains the source of those attributes.

---

# 15. Invitation Properties

An invitation shall be:

- single-use;
- short-lived;
- associated with exactly one `userId`;
- invalid after consumption;
- invalid after expiration;
- invalid when the user is suspended;
- invalid when the user is deleted.

The system should normally maintain only one active invitation per user.

Issuing a new invitation should invalidate any previous active invitation for that user.

An invitation shall not be issued to a suppressed email address
([Outbound Mail Transport](SPEC_outbound_mail.md) §14). Suppression is a property of the mailbox
rather than of the user, and it is checked before the transport is contacted (§12).

---

# 16. Magic-Link GET

The magic link shall use:

```http
GET /invite/{token}
```

The GET operation shall **not authenticate the user**.

This is a deliberate security requirement because email security scanners, link preview systems, and other automated systems may execute GET requests.

The GET operation shall:

1. Validate token format.
2. Hash the supplied token.
3. Locate the invitation.
4. Verify that it exists.
5. Verify that it has not expired.
6. Verify that it has not been consumed.
7. Retrieve the associated user.
8. Verify that the user is eligible (§9).
9. Establish short-lived invitation state.
10. Render the invitation page.

The invitation shall not be consumed by GET.

---

# 17. Invitation Page

The invitation page may display information already known from the authoritative user record.

Example:

```text
Welcome, John Smith

Northwind Manufacturing
Head of Operations

[Continue]
```

The user shall not be asked to enter:

- email;
- full name;
- company;
- position.

These values are already authoritative.

The page shall provide an explicit user action to complete authentication.

At first login the page shall also present the consent block, under the heading **"I agree with the
following consents"**, above that action. The consents to present, their order and their mandatory
flags come from the consent catalog; the block itself, the gate it forms and the facts it produces are
specified in §49.

The consent block is the reason the explicit action of this section is not merely a step away from a
token-bearing URL (§18). It is also the affirmative act that the consent decisions record.

---

# 18. Invitation Context

After the GET operation validates the invitation, the server shall maintain a short-lived invitation context.

This may be implemented using:

- a short-lived secure cookie;
- a signed/encrypted short-lived cookie;
- server-side temporary state;
- another equivalent mechanism.

The invitation token shall not be unnecessarily exposed to client-side JavaScript or persistent browser storage.

The application should transition away from the token-bearing URL after processing the initial GET.

---

# 19. Session Creation

Authentication shall occur through an explicit POST:

```http
POST /session
```

The request does not need to contain identity information.

Example, when no consent is outstanding:

```json
{}
```

Example, when the consent gate was presented (§49):

```json
{
  "consents": [
    { "consentId": "01JCNSA...", "version": 2, "accepted": true },
    { "consentId": "01JCNSB...", "version": 1, "accepted": true },
    { "consentId": "01JCNSC...", "version": 1, "accepted": false }
  ]
}
```

The server obtains the identity exclusively from the validated invitation context.

The server shall:

1. Validate the invitation context.
2. Validate the invitation.
3. Retrieve the associated `userId`.
4. Retrieve the authoritative user record.
5. Verify that the user is eligible (§9).
6. Compute the outstanding consents server-side and validate the submitted decisions against them
   (§49).
7. Atomically consume the invitation, record the consent decisions and create the session.
8. Set the session cookie.
9. Redirect the user into the application.

No password is involved.

No user identity information is supplied by the browser.

A consent decision is not identity information. It is a decision the user makes in the browser, and it
is the one thing in this request the browser legitimately supplies. What the browser does not supply is
the set of consents that were required, their mandatory flags or their current versions: the server
holds all three and validates the submission against its own copy (§49).

---

# 20. Atomic Invitation Consumption

Invitation consumption shall be protected against concurrent replay.

A DynamoDB transaction or conditional write shall ensure that an invitation can be consumed only once.

Conceptually:

```text
Transaction
────────────────────────────────────
1. Verify invitation exists
2. Verify token hash
3. Verify not consumed
4. Verify not expired
5. Verify user is eligible (§9)
6. Mark invitation consumed
7. Record consent decisions (§49)
8. Create session
────────────────────────────────────
```

If the transaction fails, the session shall not be created.

Step 7 belongs inside this transaction rather than beside it. Recording the decisions after the session
exists permits an authenticated session with no recorded lawful basis for the processing it is about to
perform; recording them before permits consent facts for a session that was never created. Each
acceptance item is written conditional on its own non-existence, so a replayed request cannot produce a
second decision about the same consent version.

The transaction therefore holds the invitation item, the session item and one item per consent decided.
This shall remain within the DynamoDB limit on items per transaction, which bounds how many consents may
be outstanding at one login. For a catalog of the intended size the bound is not close, but it is a real
ceiling and not an arbitrary one.

This transaction governs consent decisions taken at the invitation page. A decision taken inside an
existing session consumes no invitation and creates no session, and its transaction is specified separately
at §49.6.3.

---

# 21. Session Model

A successful authentication creates an opaque session ID.

The session ID shall be generated using a cryptographically secure random generator.

```text
sessionId = CSPRNG(256 bits)
```

Unlike `invitationId` (§13), `sessionId` is itself the bearer credential presented by the browser
(§22). The record identifier and the credential are the same value, so the rule of §13 applies
directly: `sessionId` shall be CSPRNG output and shall not be a ULID or any other identifier that
encodes a timestamp or is otherwise predictable.

Session record:

```json
{
  "PK": "SESSION#9f2a7c...",
  "SK": "METADATA",
  "entityType": "SESSION",

  "sessionId": "9f2a7c...",
  "userId": "01JXYZ...",

  "invitationId": "01KDEF...",
  "consentGeneration": 7,

  "createdAt": "2026-08-09T15:00:00Z",
  "lastSeenAt": "2026-08-09T15:00:00Z",

  "expiresAt": "2026-08-09T15:30:00Z",
  "absoluteExpiresAt": "2026-09-08T15:00:00Z",

  "revokedAt": null
}
```

The session contains the identity relationship:

```text
sessionId → userId
```

`invitationId` records the invitation consumed to create this session. It is not a credential and is not
presented by the browser; it is the link back to the proof of mailbox possession this session rests on, and
a mid-session consent decision records it for that reason
([Consents Storage and Management](SPEC_data_system_consents.md) §9).

`consentGeneration` is the value of `mandatoryGeneration`
([Consents Storage and Management](SPEC_data_system_consents.md) §8) at the moment the session's consents
were last validated. §49.6 compares it against the current value on each authenticated request. It is
written at session creation and updated when a mid-session gate is satisfied, and it is the only attribute
of the session record that an ordinary authenticated request may change other than `lastSeenAt` and
`expiresAt`.

---

# 22. Session Cookie

The authenticated session shall be represented by a secure browser cookie.

The cookie shall use:

```text
Secure
HttpOnly
SameSite=Lax
```

The cookie shall contain only the opaque session credential.

It shall not contain:

- email;
- name;
- company;
- position;
- permissions;
- business identifiers.

---

# 23. Sliding Session

The system shall use a sliding idle timeout combined with an absolute lifetime.

Recommended initial values:

```text
Idle timeout:       30 minutes
Absolute lifetime:  30 days
```

On an authenticated request:

```text
expiresAt =
    min(now + idleTimeout, absoluteExpiresAt)
```

The exact values shall be configurable.

A continuously active session shall eventually expire because of the absolute lifetime.

---

# 24. Authenticated Request

Authentication of normal application requests follows:

```text
HTTP request
     │
     ▼
session cookie
     │
     ▼
SESSION#<sessionId>
     │
     ▼
userId
     │
     ▼
USER#<userId> / PROFILE
     │
     ▼
authorization
     │
     ▼
consent gate (§49.6)
     │
     ▼
business operation
```

The client shall never provide the authoritative authenticated `userId`.

The server derives it from the session.

The consent gate sits after authorization and before the business operation. It is placed there because it
is not an authorization decision — the user is permitted to perform the operation, and what is missing is a
lawful basis for the processing it would perform. A gate placed before authorization would also block
callers who were never entitled to the operation, and would answer them with the wrong reason.

---

# 25. Session Revocation

A session becomes invalid when:

- `expiresAt` has passed;
- `absoluteExpiresAt` has passed;
- `revokedAt` is set;
- the associated user is suspended;
- the associated user is deleted.

A session shall also be revoked when the associated user's `role` or `orgId` changes. Both determine
what the session is permitted to do, so neither change may wait for idle expiry.

**A change to the consent catalog is not a revocation trigger.** It resembles one — the conditions under
which the session was granted have changed — but the remedy differs: `role` and `orgId` change what the
session may do and cannot be repaired from inside it, whereas an outstanding mandatory consent can be
decided in place. §49.6 blocks such a session instead of revoking it, and states why.

Logout shall revoke the current session.

The application should support revoking all sessions for a user.

A user-level session version or revocation timestamp may be used to invalidate all sessions without enumerating them.

---

# 26. User Suspension

Suspending a user shall update:

```text
USER#<userId> / PROFILE
status = SUSPENDED
```

A suspended user shall not be able to:

- receive a valid new invitation;
- consume an invitation;
- create a new session;
- access protected resources.

Existing sessions should be revoked when the user is suspended.

---

# 27. Email Change

Because the email address is the authentication anchor, changing it is a security-sensitive operation.

The change shall be performed through an explicit email-verification workflow.

The operation shall atomically:

1. verify the new email is not assigned to another user;
2. create the new email lookup;
3. update the user profile;
4. remove or invalidate the old email lookup;
5. invalidate outstanding invitations.

For stronger security, all active sessions should be revoked following an email change.

---

# 28. Business Data

Business entities are specified in [DynamoDB Business Table](SPEC_data_business.md).

One rule belongs to this document, because the identity model depends on it:

> Business entities shall reference the user by `userId`, and shall not duplicate authoritative
> identity attributes.

This keeps the user profile the single source of those attributes, reduces PII duplication, and is
what makes user-oriented erasure (§34) tractable.

---

# 29. Audit Table

The Audit table shall contain security and business-significant events.

Examples:

```text
INVITATION_CREATED
INVITATION_CONSUMED
AUTHENTICATION_SUCCEEDED
AUTHENTICATION_FAILED
SESSION_CREATED
SESSION_REVOKED
USER_CREATED
USER_SUSPENDED
USER_REACTIVATED
USER_PROFILE_CHANGED
USER_ROLE_CHANGED
EMAIL_CHANGED
USER_ERASURE_REQUESTED
USER_ERASURE_COMPLETED
```

Mail events extend this list and are specified in
[Outbound Mail Transport](SPEC_outbound_mail.md) §17:

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

Consent events extend it further and are specified in
[Consents Storage and Management](SPEC_data_system_consents.md) §12:

```text
CONSENT_ACCEPTED
CONSENT_DECLINED
CONSENT_CREATED
CONSENT_VERSION_PUBLISHED
CONSENT_STATUS_CHANGED
CONSENT_POLICY_CHANGED
```

The first two are written per consent decided, in the subject user's partition. The remaining four are
administrative changes to the catalog, concern no single user, and are written under an administrative
partition instead.

Administrative recovery events extend it further and are specified in §50:

```text
ADMIN_RECOVERY_REQUESTED
ADMIN_RECOVERY_REFUSED
ADMIN_RECOVERY_ACCOUNT_CREATED
ADMIN_RECOVERY_LIST_OBSERVED
```

Self-service re-authentication (§12.1) extends it by two:

```text
AUTH_LINK_REQUESTED
AUTH_LINK_REQUEST_REFUSED
```

`AUTH_LINK_REQUESTED` is written where the request resulted in a send. `AUTH_LINK_REQUEST_REFUSED` is
written for every other outcome, carrying the cause — no such address, ineligible user, suppressed
address, resend limit reached. The cause is recorded here precisely because §41.8 does not return it, and
a user who cannot get in is otherwise a support case with no evidence attached. Where the address resolved
to no user there is no `userId` to key on, and the event is written under the administrative partition.

Application settings extend it by one event, specified in
[DynamoDB System Table](SPEC_data_system.md) §6.1:

```text
SETTING_CHANGED
```

It concerns no single user and is written under the administrative partition, carrying the acting `userId`
where the change had an actor. It is also written for a *refused* write to a protected setting, which is
the most interesting of its cases: no legitimate caller attempts one.

`ADMIN_RECOVERY_LIST_OBSERVED` is written at application startup and is the only audit event in this
document not caused by a request. It is what makes the configured list's contents auditable over time
(§50.5); the other three are written in the subject address's partition once a `userId` exists for it,
and under the administrative partition when it does not.

Example:

```json
{
  "PK": "USER#01JXYZ...",
  "SK": "2026-08-09T15:00:00.000Z#evt-123",

  "eventType": "AUTHENTICATION_SUCCEEDED",
  "userId": "01JXYZ...",
  "occurredAt": "2026-08-09T15:00:00Z"
}
```

---

# 30. Audit Data Principles

Audit records should be append-only from the application's perspective.

Normal application operations shall not modify historical audit events.

Audit records should use `userId` instead of unnecessary PII.

Prefer:

```json
{
  "eventType": "AUTHENTICATION_SUCCEEDED",
  "userId": "U123"
}
```

over:

```json
{
  "eventType": "AUTHENTICATION_SUCCEEDED",
  "email": "john@example.com",
  "fullName": "John Smith"
}
```

Audit access shall be more restrictive than normal Business-table access.

---

# 31. Technical Logs (Amazon CloudWatch)

Technical and operational diagnostics shall be written to Amazon CloudWatch.

They shall not be written to DynamoDB. There is no Logs table.

Examples:

- request metadata;
- application errors;
- authentication failures;
- DynamoDB errors;
- email delivery failures;
- integration failures;
- retries;
- latency;
- operational events.

An email delivery failure appears here as a diagnostic only. The durable, issuer-visible delivery
state is the invitation record's `deliveryStatus` (§14), not this log entry: a log expires under a
retention policy, and cannot afterwards answer why a user never received an invitation.

Log entries shall be emitted as structured JSON lines.

Example:

```json
{
  "level": "WARN",
  "service": "auth",
  "event": "INVITATION_VALIDATION_FAILED",
  "requestId": "req-123",
  "statusCode": 404,
  "occurredAt": "2026-08-09T15:00:00Z"
}
```

Technical logs shall not contain:

- magic-link tokens;
- token hashes unless explicitly required;
- session IDs;
- session cookies;
- authorization headers;
- passwords;
- password hashes;
- unnecessary email addresses;
- unnecessary names;
- unnecessary company information.

Where user correlation is required, use `userId`.

---

# 32. Business / Audit / System Separation

| Table | Purpose | Data examples | Primary characteristic |
|---|---|---|---|
| Business | Current application state | Users, sessions, invitations, business data | Mutable source of truth |
| Audit | Historical security/business events | Authentication, user changes, erasure events | Append-oriented |
| System | Reference data in force | Versioned consents, settings, e-mail templates, versioned prompts | Versioned reference data |

These tables shall have independent:

- IAM permissions;
- retention policies;
- access controls;
- backup policies;
- GDPR handling procedures.

CloudWatch is a fourth store, holding technical telemetry outside DynamoDB (§31). The same
requirements for independent IAM permissions, retention, access control and GDPR handling apply
to it.

---

# 33. Data Classification

### Personal/business identity data

```text
email
fullName
companyName
position
business-specific user information
```

### Authentication credentials

```text
magic-link token
session ID
```

These are security-sensitive bearer credentials.

### Audit data

```text
userId
event type
timestamp
security metadata
```

### Technical telemetry (CloudWatch)

```text
requestId
service
operation
latency
error type
HTTP status
```

The guiding rule is:

> PII shall be stored only where it is required for the purpose of that dataset.

---

# 34. GDPR User Erasure

The system shall provide a controlled user-erasure workflow.

The authoritative user identity is located by:

```text
USER#<userId>
```

The workflow shall identify all relevant user-related records, including:

```text
USER#<userId> / PROFILE
EMAIL#<email> / USER
INVITATION#... → userId
SESSION#... → userId
MAIL_SUPPRESSION#<email> / METADATA
```

together with the user's business entities, whose inventory is specified in
[DynamoDB Business Table](SPEC_data_business.md).

The email lookup and suppression records are keyed by email address rather than by `userId`, so
neither lies within the user's partition and neither is found by querying it. The workflow shall
locate them explicitly. The retention treatment of a suppression record is specified in
[Outbound Mail Transport](SPEC_outbound_mail.md) §19, because erasing it restores the ability to mail
an address that asked not to be mailed.

Records shall then be deleted or anonymized according to the applicable retention policy.

---

# 35. GDPR and Audit Data

Audit records may have separate legal or regulatory retention requirements.

Therefore, erasure shall not blindly delete every audit record associated with the user.

The organization shall classify audit events into:

- records that must be erased;
- records that may legally be retained;
- records that can be anonymized;
- records that must remain immutable.

Where possible, audit events should use only `userId`, allowing the user profile to be removed while minimizing directly identifying information in the retained audit trail.

The classification shall cover the consent acceptance facts of
[Consents Storage and Management](SPEC_data_system_consents.md) §9 explicitly. They are Business-table
records rather than audit records, so §34 deletes them by default, but they are the evidence that the
processing already performed was permitted. They reference the user by `userId` only, so severing the
profile leaves a trail that is no longer directly identifying — which is what makes retaining them an
option rather than a contradiction.

---

# 36. GDPR and Technical Logs (CloudWatch)

Technical logs should contain minimal PII.

Prefer:

```text
userId=U123
requestId=REQ456
```

over:

```text
email=john@example.com
fullName=John Smith
```

If PII enters the log group, the logging policy shall define:

- retention;
- access controls;
- deletion/anonymization;
- backup handling.

---

# 37. Backup and Recovery

DynamoDB backups and Point-in-Time Recovery may contain historical versions of deleted data.

The GDPR erasure process shall therefore include a documented backup policy covering:

- backup retention;
- access to historical data;
- restoration procedures;
- treatment of deleted users;
- reapplication of erasure after restoration.

A restored backup must not silently reintroduce a previously deleted user into an active application.

---

# 38. Security Requirements

## 38.1 HTTPS

All authentication and application endpoints shall require HTTPS.

## 38.2 Token generation

Invitation and session tokens shall use a cryptographically secure random generator.

## 38.3 Token storage

Plaintext magic-link tokens shall never be stored.

## 38.4 Cookie security

Authentication cookies shall use:

```text
Secure
HttpOnly
SameSite=Lax
```

## 38.5 CSRF

All state-changing browser requests shall have CSRF protection.

This includes:

```text
POST /session
POST /auth/consents
POST /logout
profile modifications
email changes
business state changes
```

`POST /auth/request-link` (§41.8) is unauthenticated and carries no session to protect, so CSRF protection
does not apply to it. Its abuse case is volume, which §38.6 addresses instead.

## 38.6 Rate limiting

Rate limiting shall be applied to:

- invitation generation;
- invitation validation;
- session creation;
- authentication failures;
- sign-in link requests (§41.8), per submitted address and globally;
- administrative recovery requests (§41.7).

Rate limits may be based on IP address, user, invitation, or other appropriate dimensions.

---

# 39. User Enumeration Protection

Unauthorized callers shall not be able to determine whether an email address belongs to a provisioned user.

Authentication responses should use generic failure messages.

For example, the client should not distinguish between:

```text
unknown invitation
expired invitation
already consumed invitation
suspended user
deleted user
```

The sign-in link request (§41.8) is subject to this requirement without exception. Its response shall be
identical for an address that resolves to an eligible user, an address that resolves to nothing, an
ineligible user, a suppressed address, and a resend limit already reached. This route is the most exposed
surface in the document — unauthenticated, reachable by anyone, and taking an address as input — so it is
the one where a distinguishable failure would be a directory-enumeration oracle rather than a nuisance.

The administrative recovery route (§41.7) is held to this requirement more strictly still, because the
population it would disclose is the platform's administrators. Its response shall be identical whether the address
is a member of the configured list, is not a member, matches a record holding some other role, or
matches a suspended one. A route that distinguished these would disclose the platform's administrators
to an unauthenticated caller, and under §48 an administrator's address is the whole of their
authentication.

Detailed diagnostic information may be written to the internal CloudWatch log entry.

---

# 40. Magic-Link Exposure

The token may appear in:

- the email;
- the browser URL;
- the initial HTTP request.

It shall not appear in:

- application logs;
- Audit records;
- analytics;
- error messages;
- persistent browser storage;
- database records in plaintext.

The application should transition away from the token-bearing URL after the initial GET.

Recommended sequence:

```text
GET /invite/<token>
        │
        ▼
validate token
        │
        ▼
establish temporary invitation context
        │
        ▼
POST /session
        │
        ▼
authenticated session
```

---

# 41. Authentication API

## 41.1 Create invitation

```http
POST /auth/invitations
```

Request:

```json
{
  "userId": "01JXYZ..."
}
```

The server retrieves the email from the authoritative user record, checks that the address is not
suppressed, and sends through the outbound mail transport
([Outbound Mail Transport](SPEC_outbound_mail.md)).

---

## 41.2 Open invitation

```http
GET /invite/{token}
```

Purpose:

- validate invitation;
- establish temporary invitation state;
- display the invitation page.

Does not authenticate the user.

---

## 41.3 Create session

```http
POST /session
```

Purpose:

- consume the invitation;
- record the consent decisions (§49);
- create an authenticated session.

No identity information is required from the client. Consent decisions are required when the gate
presented any (§49).

---

## 41.4 Current user

```http
GET /me
```

Example:

```json
{
  "userId": "01JXYZ...",
  "fullName": "John Smith",
  "companyName": "Northwind Manufacturing",
  "position": "Head of Operations",
  "orgId": "01JORG...",
  "role": "POWER_USER"
}
```

The response is generated from the authoritative Business-table user record.

---

## 41.5 Logout

```http
POST /logout
```

The server shall revoke the current session and clear the browser cookie.

---

## 41.6 Outstanding consents

```http
GET /auth/consents
```

Authorized by **either** the invitation context of §18 **or** a valid session cookie:

| Caller | Context | Consents returned for |
|---|---|---|
| A validated invitation holder with no session yet (§49.2) | Invitation context (§18) | The user the invitation identifies |
| A user held at the mid-session gate (§49.6) | Session cookie (§22) | The user the session identifies |

These are the only two states in which the question is meaningful, and neither one authorizes the other:
an invitation holder has no session, and a session holder has no invitation context. In both cases the
subject is derived server-side from the context presented, and never from the request.

Returns the outstanding consents in presentation order, one entry per consent:

```json
{
  "consents": [
    {
      "consentId": "01JCNSA...",
      "label": "C-1",
      "version": 2,
      "title": "I agree to participate in this AI Readiness interview.",
      "content": "PLACEHOLDER: I agree to participate ...",
      "order": 0,
      "mandatory": true
    }
  ]
}
```

An empty array means nothing is outstanding and the client shall render no consent block. This is the
normal response on every login after the first.

The response contains no `status` field. Only `ACTIVE` consents are returned, so the field would carry
one value and invite a client to filter on it — which is the server's job (§49).

---

## 41.7 Request administrative recovery

```http
POST /auth/admin-recovery
```

Request:

```json
{
  "email": "ops.lead@example.com"
}
```

Unauthenticated, and the only route in this document that accepts an email address from the caller. The
conditions under which it acts, and the record it may create, are specified in §50.

Response, in every case:

```json
{
  "status": "ACCEPTED"
}
```

`ACCEPTED` states that the request was received, not that a message was sent. The route returns the same
body and the same status code for a member address, a non-member address, an address held by a
non-`ADMIN` record and a suspended one (§39).

Rate limiting applies (§38.6) per address and globally. The global limit matters more here than on other
routes: this is the one endpoint whose input is an address of the caller's choosing, so an unbounded
version is a probe against the configured list.

---

## 41.8 Request a sign-in link

```http
POST /auth/request-link
```

Request:

```json
{
  "email": "john.smith@example.com"
}
```

Unauthenticated. The server behaviour is specified at §12.1.

Response, in every case:

```json
{
  "status": "ACCEPTED"
}
```

`ACCEPTED` states that the request was received. It does not state that an account exists, that a message
was sent, or that the address is deliverable — none of which may be disclosed to this caller (§39).

Rate limiting applies (§38.6) per submitted address and globally. Per-address limiting stops the route
being used to flood one mailbox; the global limit stops it being used to enumerate the directory at
volume, which the uniform response makes slow but not impossible.

---

## 41.9 Record consent decisions in a session

```http
POST /auth/consents
```

Request, in the shape §19 uses:

```json
{
  "consents": [
    { "consentId": "01JCNSA...", "version": 3, "accepted": true },
    { "consentId": "01JCNSD...", "version": 1, "accepted": false }
  ]
}
```

Authorized by the session cookie. Used only at the mid-session gate (§49.6), where the decisions of
§49.3 must be recorded for a user who already holds a session and therefore has no invitation to consume.

CSRF protection applies (§38.5). On success the response is the ordinary success of the route the client
was blocked on retrying; the server records the decisions and advances the session's `consentGeneration`
(§49.6.3).

This route does not create, extend or revoke a session. `POST /session` (§41.3) remains the only route
that creates one, and it remains the only place a consent decision is recorded alongside the consumption
of an invitation.

---

# 42. Successful Authentication Flow

```text
1. User exists in Business table
        │
        ▼
2. User has an eligible status (§9)
        │
        ▼
3. Authorized system requests invitation
        │
        ▼
4. Server retrieves authoritative email
        │
        ▼
5. Generate random token
        │
        ▼
6. Store token hash
        │
        ▼
7. Send magic-link email
   (Outbound Mail Transport)
        │
        ▼
8. User clicks link
        │
        ▼
9. GET /invite/<token>
        │
        ▼
10. Validate invitation
        │
        ▼
11. Display authoritative user information
        │
        ▼
12. Present outstanding consents (§49)
    (first login only)
        │
        ▼
13. User checks the mandatory boxes
    and decides the optional ones
        │
        ▼
14. User explicitly clicks Continue
        │
        ▼
15. POST /session, carrying the decisions
        │
        ▼
16. Validate decisions against the catalog
        │
        ▼
17. Atomically consume invitation,
    record consents, create session → userId
        │
        ▼
18. Set Secure/HttpOnly cookie
        │
        ▼
19. User enters application
```

---

# 43. Failed Authentication Flow

```text
GET /invite/<token>
        │
        ▼
token validation
        │
   ┌────┴─────┐
   │          │
 valid      invalid
   │          │
   ▼          ▼
 page       generic
            error
```

The external response shall not expose unnecessary details about the failure.

The internal CloudWatch log entry may contain the specific failure classification.

---

# 44. Recommended Business Table Access Patterns

The Business table shall support at minimum the following authentication access patterns. Business
entity access patterns are specified in [DynamoDB Business Table](SPEC_data_business.md).

### Retrieve user

```text
PK = USER#<userId>
SK = PROFILE
```

### Resolve email

```text
PK = EMAIL#<normalizedEmail>
SK = USER
```

### Retrieve session

```text
PK = SESSION#<sessionId>
SK = METADATA
```

### Retrieve invitation

```text
PK = INVITATION#<invitationId>
SK = METADATA
```

---

# 45. Recommended Audit Table Access Patterns

Primary access pattern:

```text
PK = USER#<userId>
SK = <timestamp>#<eventId>
```

Example:

```text
USER#U123
    │
    ├── 2026-08-09T15:00:00Z#evt001
    ├── 2026-08-09T15:05:00Z#evt002
    └── 2026-08-09T15:10:00Z#evt003
```

Additional GSIs may be introduced for:

- event type;
- global chronological auditing;
- administrative operations.

The design should follow actual audit-query requirements.

---

# 46. Technical Telemetry Conventions

Technical telemetry lives in CloudWatch (§31), not in DynamoDB, so it has no key schema and no access
patterns in the DynamoDB sense.

The following conventions shall apply instead:

### Log groups

Each service shall write to its own log group.

```text
/ecs/<application>
```

Retention is set by the log-group retention policy, which is the natural retention boundary.

### Entry format

Entries shall be structured JSON lines rather than free text, so that they can be queried by field.

### Correlation

Entries shall carry:

```text
requestId
service
event
```

Where user correlation is required, use `userId` (§31).

Correlating a user's activity across services shall be possible without placing PII in the log entry.

---

# 47. Security Boundary

The architecture has three important security boundaries:

```text
Email possession
      │
      ▼
Authentication
      │
      ▼
userId
      │
      ▼
Authorization
      │
      ▼
Business operation
```

Possession of an email link proves control of the provisioned mailbox.

It does not independently establish any authorization beyond what the server assigns to the corresponding `userId`.

---

# 48. Important Trust Assumption

This authentication model is appropriate only if:

> **Control of the provisioned email account is an acceptable authentication factor for the application's threat model.**

The system does not independently verify that:

- the person using the mailbox is the intended employee;
- the mailbox has not been compromised;
- the mailbox has not been delegated;
- the email address has not been incorrectly provisioned.

The security of the authentication system therefore depends in part on the security and correctness of the authoritative email directory and the associated mailboxes.

---

# 49. Consent Capture

Before a user's first authenticated session exists, the user shall decide the consents in force. The
decision is taken on the invitation page (§17), between the validating GET (§16) and the
session-creating POST (§19), and is recorded in the same transaction that consumes the invitation
(§20).

A consent that becomes mandatory while a user holds a live session is put to them inside that session,
without waiting for it to end. That is §49.6, and it is why this section is no longer titled for first
login alone.

The consents themselves, their storage, their versioning and the shape of the recorded facts are
specified in [Consents Storage and Management](SPEC_data_system_consents.md). This section specifies
the gate: when it appears, what the server accepts, and what happens when it is not satisfied.

## 49.1 Outstanding consents

> A consent is **outstanding** for a user when its `status` is `ACTIVE` and the user has no recorded
> decision for it at its `currentVersion`.

This is the normative definition, and every reference to outstanding consents in this document refers
to it.

The consequences follow mechanically from it, and each of them is intended:

| Situation | Outstanding? |
|---|---|
| User has never logged in | Yes, for every `ACTIVE` consent |
| User accepted the consent at its current version | No |
| User **declined** an optional consent at its current version | No |
| A new consent was published since the user last logged in | Yes |
| A new version of an already-decided consent was published | Yes |
| The consent is `DISABLED` | No, whatever `mandatory` says |

A declined optional consent is a recorded decision, not a missing one, so it is not outstanding and the
user is not asked again at the next login. Re-presenting a refused optional consent at every login is
not a reminder, it is pressure, and consent obtained under it is harder to call freely given.

The gate is therefore evaluated at every session creation, not only at the first one, and inside a live
session as well (§49.6). In practice it is empty on every login after the first, because nothing is
outstanding until an administrator changes the catalog. "First login" describes when users see it, not a
special case in the logic — a gate that only ever ran once would silently exempt every existing user from
every consent added later.

**Outstanding is computed, never stored.** Because the definition is scoped to `currentVersion`, publishing
a new version makes every earlier decision outstanding at once, for the whole population, with no write to
any user's records. There is no per-user consent status to maintain, no reset job on publication, and none
shall be introduced. Two reasons, and the second is the load-bearing one:

- A stored flag duplicates a derivable answer, and the two eventually disagree with nothing to say which is
  authoritative.
- Resetting would mean altering or removing an acceptance fact. Those facts are the evidence that
  processing already performed was permitted (§35), and a decision recorded against version 1 remains true
  about version 1 after version 2 is published. The correct outcome is a second fact beside the first, which
  is what recomputation produces and what
  [Consents Storage and Management](SPEC_data_system_consents.md) §9 requires by making the version part of
  the sort key and forbidding updates.

## 49.2 Presentation

The client obtains the outstanding consents through §41.6 and renders them under the heading
**"I agree with the following consents"**, in the order received, one checkbox per consent.

The presentation rules are specified in
[Consents Storage and Management](SPEC_data_system_consents.md) §11 and are not restated here. Two of
them matter to this document, because they are the difference between a gate and a formality:

- every box is rendered unchecked, mandatory ones included;
- the continue action stays disabled until every mandatory box is checked.

Both are user-interface affordances. Neither is the enforcement mechanism.

## 49.3 Server validation

On `POST /session` the server shall, before consuming the invitation:

1. Recompute the outstanding set from the catalog and the user's recorded decisions. The client's
   submission shall not be treated as evidence of what was required.
2. Verify that the submitted decisions correspond exactly to the outstanding set: every outstanding
   consent decided once, no duplicates, no unknown or non-outstanding `consentId`.
3. Verify that each submitted `version` equals that consent's `currentVersion`.
4. Verify that every outstanding consent with `mandatory: true` was submitted with `accepted: true`.
5. Accept `accepted: false` for a consent with `mandatory: false`, and record the refusal.

A failure of 2 or 3 means the catalog changed while the page was open: a consent was published,
withdrawn or re-versioned between the GET and the POST. The server shall refuse and re-present the gate.
It shall not record the submitted decisions and shall not silently record them against the current
version. A decision about text the user was not shown is not a consent, and it is worse than no record
at all, because it looks like one.

A failure of 4 means the user declined a mandatory consent. The user cannot continue.

## 49.4 The refusal path

A refusal under 49.3 shall leave no trace in the Business table. Specifically it shall not:

- consume the invitation;
- create a session;
- record any acceptance fact;
- change the user's `status`.

The invitation remains valid until it expires, and the user may return to the same link and decide
again.

This is deliberate. Consuming the invitation on refusal would mean that a user who hesitated over a
mandatory consent — or who submitted a stale page through no fault of their own — has destroyed their
only way in and must ask an administrator for a new invitation. The invitation exists to prove control
of the mailbox (§47), and declining a consent does not disprove it.

The refusal response may state which consent is outstanding, that a mandatory consent was not accepted,
or that the gate is stale. This does not weaken §39: the caller already holds a validated invitation
and therefore already knows a provisioned user exists behind it, so the response reveals nothing about
the user population that the caller did not supply.

## 49.5 Recording

On success, one acceptance fact per decided consent is written inside the transaction of §20, each
conditional on its own non-existence. The item shape is specified in
[Consents Storage and Management](SPEC_data_system_consents.md) §9.

The facts record the `invitationId` consumed alongside them. That is the evidentiary link between the
decision and the proof of mailbox possession that accompanied it: the same request that established who
the user was also carried what they agreed to.

A double-submitted POST is rejected by the invitation-consumption condition of §20, so it cannot produce
a second set of decisions.

`CONSENT_ACCEPTED` and `CONSENT_DECLINED` audit events (§29) are written per decision after the
transaction commits. The acceptance fact is the record of record; the audit event is the trail. If the
process fails between the two, the evidence of the decision survives and only its trail entry is
missing — the tolerable direction for that failure.

## 49.6 The mid-session gate

The gate of §49.2 sits on the invitation page, so it is reached only when a user authenticates. A consent
made mandatory today would otherwise not be put to a user holding a live session until that session ended,
which under §23 may be up to 30 days.

**The gate is therefore also evaluated inside a live session.** A user with an outstanding mandatory
consent is blocked from protected resources until they decide it, and is not signed out.

### 49.6.1 Evaluation on an authenticated request

On each authenticated request (§24), after authorization and before the business operation, the server
shall compare the session's `consentGeneration` (§21) with the current `mandatoryGeneration`
([Consents Storage and Management](SPEC_data_system_consents.md) §8).

```text
session.consentGeneration == mandatoryGeneration
        │
        ├── equal ──────▶ proceed; nothing further is read
        │
        └── differs ────▶ compute the outstanding set (§49.1)
                              │
                              ├── no mandatory consent outstanding
                              │      ▶ advance session.consentGeneration, proceed
                              │
                              └── a mandatory consent is outstanding
                                     ▶ refuse, and present the gate
```

The comparison is the whole of the common path, and the counter may be cached in the process for a short
interval. Recomputing the outstanding set per request would place two queries on every request the
application serves, to answer a question whose answer changes a handful of times in the life of the
deployment.

Where the generations differ but nothing mandatory is outstanding, the session's `consentGeneration` is
advanced without asking the user anything. This is the case of a catalog change that added or re-versioned
only optional consents, or one the user has already decided. The session stops re-evaluating, and the
optional consents are presented at the user's next login rather than interrupting them now.

**Only a mandatory outstanding consent blocks.** An optional one is a request, and a request that
suspends a user's access until answered is not optional in any sense the user would recognize. Optional
consents outstanding at the moment the gate triggers are presented alongside the mandatory ones, so that a
user interrupted once decides everything at once.

### 49.6.2 What is refused, and what is not

A blocked request shall be refused with a status distinguishing it from an authorization failure, and with
a machine-readable marker the client uses to present the gate. For a request under `/api/` the refusal
shall be JSON.

The following shall remain reachable while the gate is unsatisfied:

```text
GET  /me                 render the application shell
GET  /auth/consents      retrieve the outstanding consents
POST /auth/consents      decide them
POST /logout             leave
```

Everything else is refused. `POST /logout` is on that list deliberately: a user who will not accept a
mandatory consent shall be able to end their session rather than be held in one they cannot use.

**The session is not revoked, and §25 gains no consent trigger.** Revocation was the alternative
resolution, and it is rejected for three reasons. It would sign out every user on a catalog change and
require each to obtain a fresh magic link, which is a population-wide mail round-trip — and under §1 mail
is the single point of failure for all access, so an administrative consent change would become a
deliverability event. It would destroy authenticated context mid-task; an interview runs 20 minutes and a
revocation lands in the middle of one. And it would pay that cost to reach the same place this gate reaches
in one request, since a revoked user's next act is to authenticate and meet the gate of §49.2 anyway.

The mid-session gate loses nothing by comparison. Server-side turn append means in-flight work is not
discarded by a refusal, so a user interrupted mid-interview decides the consent and continues.

### 49.6.3 Recording a mid-session decision

Decisions arrive at `POST /auth/consents` (§41.9) and are validated exactly as §49.3 requires — the
outstanding set recomputed server-side, versions checked against `currentVersion`, mandatory consents
required to be accepted, optional refusals accepted and recorded.

There is no invitation to consume, so the transaction of §20 does not apply. The mid-session transaction
holds:

```text
Transaction
────────────────────────────────────
1. Verify the session is valid (§25)
2. Verify the user is eligible (§9)
3. Record consent decisions, each conditional
   on its own non-existence
4. Advance session.consentGeneration
────────────────────────────────────
```

Step 4 belongs inside it. Advancing the generation before the facts are written would let a failure leave a
session that believes it is current and a user who has recorded nothing; advancing it after would let a
successful decision be re-demanded on the next request. Each fact remains conditional on its own
non-existence, so a double-submitted request cannot record a second decision about the same version.

The facts record `decisionContext: SESSION` and the `invitationId` carried on the session record
([Consents Storage and Management](SPEC_data_system_consents.md) §9). The evidentiary link to mailbox
possession is preserved, and the record states honestly that the possession was proven when the session
began rather than in the same request as the decision.

`CONSENT_ACCEPTED` and `CONSENT_DECLINED` audit events (§29) are written per decision after the
transaction commits, as at §49.5.

### 49.6.4 The refusal path

A submission that fails validation shall leave no trace: no acceptance fact, no change to
`consentGeneration`, and no change to the session's validity. The user remains authenticated and remains
blocked, and may submit again.

A user who declines a mandatory consent stays in that state for as long as their session lasts. The session
is not revoked, is not extended by the refused request, and expires normally under §23. This is the
mid-session equivalent of §49.4: refusing a consent is not misconduct, and the response to it is to
withhold access rather than to destroy the means of reconsidering.

---

# 50. Administrative Access Recovery

Administrative access shall be recoverable from deployment configuration, without an existing
administrative account and without a stored secret.

§7.1 states the circularity this resolves. §50 is the only path by which an `ADMIN` record comes into
existence with no authenticated administrator behind it, and it confers no other role.

It is not a bootstrap. A bootstrap is spent once and thereafter guarantees nothing, which leaves a
deployment that loses its administrators with no way back; this path is standing and works every time it
is needed. That is also its principal cost, and §50.6 states it.

## 50.1 The configured administrator list

The list shall be supplied as deployment configuration in `AIDIAG_ADMIN_EMAILS`, as email addresses
normalized by the policy of §8 and separated by commas.

Example:

```text
AIDIAG_ADMIN_EMAILS=ops.lead@example.com,platform.owner@example.com
```

**The list itself shall not be held in the System table, protected or otherwise.** Its two failure modes
are the reason, and they are different from the allowlist's. First, a value stored in the table is
editable by whoever can write to the table directly, and the population that can do so overlaps the one
this path exists to reconstitute; deployment configuration narrows that to whoever can deploy, which is
the trust boundary §50.6 states. Second, and decisively, the scenarios of §7.1 include a data layer in an
unknown state — a fresh table, an interrupted migration, an item deleted in error. A recovery mechanism
whose own definition lives in the store that may be broken is not a recovery mechanism.

The list shall be held through a secret reference rather than as a plain value in a task or container
definition. It is not a credential, and treating it as one is not the reason: it is a list naming the
platform's administrators, and under §48 possession of an administrator's mailbox is the whole of that
administrator's authentication. An enumerable list of high-value phishing targets warrants the same
handling as a secret even though it confers nothing by itself.

The list shall be validated at application startup, and startup shall fail on:

- an entry that is not a syntactically valid email address;
- an entry that does not normalize cleanly under §8;
- a duplicate entry;
- an entry outside the configured administrative domain allowlist.

Failing closed at startup rather than skipping the offending entry is deliberate. A silently dropped
entry is a lockout that is discovered during the incident it was configured to resolve, at the moment
when there is no remaining path to diagnose it.

The **administrative domain allowlist** is the `adminDomainAllowlist` setting, specified in
[DynamoDB System Table](SPEC_data_system.md) §6.3. It constrains this list because the list would
otherwise be the way around it: an address at an arbitrary provider, named in configuration, would reach
`ADMIN` without passing any check that an administratively issued invitation must pass.

It is a **protected** setting (that document's §6.1), so no application route writes it and the `ADMIN`
capability to manage settings does not reach it. That protection is a precondition of this section rather
than an incidental property of where the value happens to live: an allowlist that an administrator could
widen would constrain nothing, and validating this list against it would be theatre.

Startup validation shall read the allowlist and the list together and shall fail if either is invalid or
if any entry in the list falls outside the allowlist as it currently stands.

**This couples the recovery path to the System table, and the coupling shall be stated rather than
discovered.** Because an absent allowlist admits nothing (that document's §6.3), a missing or unreadable
`adminDomainAllowlist` item blocks recovery as completely as an empty list would — so the argument above
for keeping the list out of the data layer does not fully hold for the constraint on it. Two requirements
follow. The deployment step that sets `AIDIAG_ADMIN_EMAILS` shall provision the allowlist item in the same
action, so that the two cannot be introduced separately or diverge. And the startup failure shall name
which of the two is at fault, since "administrative recovery is unavailable" is not an actionable message
when there are two independent causes and one of them is a missing table item.

An absent or empty list is permitted and means the deployment has no recovery path. This shall be
recorded at startup as an explicit condition rather than treated as the default absence of a setting,
because the two are indistinguishable in configuration and entirely different in consequence.

## 50.2 What the list authorizes

For an address named in the list, on a request under §41.7:

| Directory state of the address | Outcome |
|---|---|
| No user record exists | A record is created (§50.4) and an invitation is issued |
| A record exists with `role` `ADMIN`, eligible per §9 | An invitation is issued; no record is created |
| A record exists with any `role` other than `ADMIN` | **Refused.** No promotion, no invitation |
| A record exists with `status` `SUSPENDED` or `DELETED` | **Refused** |
| The address is suppressed ([Outbound Mail Transport](SPEC_outbound_mail.md) §14) | **Refused** |

Every refusal writes `ADMIN_RECOVERY_REFUSED` with its cause and returns the response of §41.7, which
does not carry the cause.

**No promotion, in either direction.** An address in the list that matches a record holding another role
is refused rather than elevated. Elevating it would let configuration silently confer `ADMIN` on a
`USER` or `PARTNER`, and in the `PARTNER` case would produce an account holding both report access and
platform administration — which the capability matrix separates deliberately, `ADMIN` reading no reports
at all ([Role Model](role_model.md)). Configuration is not the place that decision gets made. The
correct handling of a genuine collision is to resolve it administratively, or to name a different
address.

**Suspension survives the list.** This is the one deliberate limit on the recovery path, and it cuts
both ways. An address in the list whose record is suspended cannot recover, so a wrongly suspended
administrator is not restored by this path; in exchange, a listed administrator whose mailbox is known
to be compromised can be stopped immediately by an in-application action, rather than only by a
deployment. The alternative — a list that overrides `status` — would mean no listed address could ever be
de-privileged without a release, and a compromised mailbox would remain live for as long as that takes.
Immediate revocability is worth more than immediate restoration, because the failure it prevents is
active and the one it costs is recoverable by a second configuration change.

Removing an administrator therefore has two steps, in this order:

1. Suspend the account in the application, which takes effect at once and revokes its sessions (§25, §26).
2. Remove the address from the list at the next deployment.

Performing only the second leaves an account that another administrator can still invite through the
ordinary path of §12. Performing only the first leaves an address that a later un-suspension re-enables
without anyone revisiting the configuration.

## 50.3 The recovery request

The route is §41.7. It accepts an email address from an unauthenticated caller, which §12 forbids
everywhere else, and the exception needs stating precisely rather than merely noting.

What §12 protects against is a caller choosing where a credential is delivered. This route does not
permit that. The submitted address is not a destination — it is a lookup key, tested for membership in a
list the caller cannot influence, and every non-member value is refused. The set of addresses this route
can ever mail is fixed by configuration before the request arrives, so the caller selects from that set
at most, and gains nothing by selecting an address whose mailbox they do not control.

Once the record exists, issuance is ordinary: the invitation of §12 steps 5 through 9, the token rules of
§13, the record of §14, and the properties of §15. No new credential type is introduced, no separate link
format exists, and the magic link produced here is indistinguishable from any other. The GET of §16 and
the session creation of §19 are unchanged, including the consent gate of §49 — an administrator recovered
through this path decides the consents in force like anyone else.

## 50.4 Record materialization

Where no record exists for a listed address, the first successful request shall create one:

```json
{
  "PK": "USER#01JADM...",
  "SK": "PROFILE",
  "entityType": "USER",

  "userId": "01JADM...",

  "email": "ops.lead@example.com",
  "fullName": "ops.lead@example.com",
  "companyName": null,
  "position": null,

  "orgId": null,
  "role": "ADMIN",

  "status": "PROVISIONED",

  "createdBy": "SYSTEM#ADMIN_RECOVERY",

  "createdAt": "2026-08-10T09:00:00Z",
  "updatedAt": "2026-08-10T09:00:00Z"
}
```

The record and its email lookup item shall be created in one transaction, under §8. The conditional
write of §8 is what makes repeated requests safe: a second request finds the record and creates nothing.

**A record is created rather than a session minted directly, because audit requires a subject.** Audit
events are keyed on `USER#<userId>` (§29, §45). A principal acting without a record would leave every
administrative action it subsequently performs unattributable — and the actions this path leads to are
the most consequential in the system. The list confers the ability to obtain an account; it is not
itself an account.

`fullName` defaults to the address because §17 renders the profile on the invitation page and configuration
carries no name. This is the only account in the system whose display attributes are not administratively
provisioned, and the holder may correct them afterwards through the ordinary profile route. §17 shall
still not ask for them during authentication: an unauthenticated page that collects a name and writes it
to an `ADMIN` record is a defacement surface, and the value is cosmetic.

`orgId` is null. An administrator belongs to no organization, consistent with `ADMIN` reading no reports.

`createdBy` is not one of the authoritative profile attributes of §5 and is not an authorization input.
It records the origin of the record, and the fixed value `SYSTEM#ADMIN_RECOVERY` is what distinguishes an
account this path created from one an administrator provisioned. Without it, the two are
indistinguishable in the directory, and the question "which of these administrators was created by
configuration" has no answer outside the audit trail.

## 50.5 Notification and observability

Each of the following shall notify a security or operations address out of band, and all accounts holding
`role` `ADMIN`, in addition to writing its audit event:

- a successful recovery request;
- a refused recovery request;
- a change in the effective list, detected at startup.

**Notification is the control here, not the audit log.** Every other privileged action in this system is
taken by an authenticated actor whose authority was granted inside the application. This one is not:
nothing in the application authorized it, so no in-application review would surface it. An audit log is
read once someone suspects something; notification is what produces the suspicion. Without it, the
standing exposure of §50.6 is detected by nothing.

Startup shall write `ADMIN_RECOVERY_LIST_OBSERVED` to the Audit table carrying the entry count and a
digest of the normalized list, and shall compare that digest against the most recent such entry to
detect a change. The digest rather than the addresses, because §30 requires audit records to avoid
unnecessary PII and the addresses are already recorded in deployment configuration; the count alongside
it, because a digest alone cannot distinguish an addition from a substitution when someone is reading the
trail afterwards.

The Audit table holds this rather than the System table for the same reason the list itself does not live
there: `ADMIN` may manage application settings but cannot rewrite audit history (§30). The System table's
protected setting class ([DynamoDB System Table](SPEC_data_system.md) §6.1) would also serve, but audit
is the better home for a record whose value is that it accumulates rather than that it is current.

## 50.6 Standing exposure

Whoever can change deployment configuration can obtain `ADMIN`. This shall be stated rather than
mitigated, because it is a property of the mechanism and not a defect in it.

That principal already holds read access to the Business table and therefore to every user's PII, so the
path grants little that was not already available by other means. What it does grant is specifically
`ADMIN`, quietly, and with an application-level audit trail that shows an ordinary sign-in. The controls
are the IAM permissions on the configuration store and the notification of §50.5. Neither prevents it;
together they make it visible.

The list is standing rather than spent, and nothing in the application expires an entry. An address that
should no longer be there — a departed holder, a mailbox that changed hands — remains usable until a
deployment removes it, and no in-application action removes it (§50.2). Periodic review of the list is
therefore an operational requirement rather than an application feature, and the startup audit entry of
§50.5 is what makes the current contents reviewable without access to the deployment configuration.

## 50.7 What this path does not recover

Two conditions defeat administrative recovery, and both are recorded as known issues rather than resolved
here: a deployment whose outbound mail is not working (**K-1**), and one whose System table does not hold a
valid `adminDomainAllowlist` (**K-2**). §51 states both, and §50.1 carries the requirements that bound the
second.

Neither is a defect in the mechanism specified above. Both are consequences of the recovery path depending
on infrastructure that may itself be the thing that is broken, which is the general difficulty with
recovery paths and is not fully escapable.

---

# 51. Known Issues

Accepted and unresolved. Each entry states what it affects, why it has not been resolved, and what would
resolve it. **This section is not normative**; nothing here weakens a requirement stated elsewhere in this
document.

| # | Issue | Affects | Status |
|---|---|---|---|
| **K-1** | Administrative recovery depends on the outbound mail path, and so does not recover a deployment whose mail is not working | §50 | Accepted; resolution identified, not scheduled |
| **K-2** | Administrative recovery depends on the System table holding a valid allowlist, and so does not recover a deployment whose System table is empty or damaged | §50, §50.1 | Accepted; bounded by §50.1, residual remains |

## K-1 — Administrative recovery depends on outbound mail

The recovery path issues an ordinary magic link (§50.3) and therefore depends on the same outbound mail
transport as every other form of access ([Outbound Mail Transport](SPEC_outbound_mail.md)). It does not
recover a deployment whose mail is not working — an unverified sender identity, a transport not yet
released from its sending sandbox, a misconfigured envelope sender — and that is a plausible state for a
deployment at exactly the moment its first administrator is needed.

**Why it is accepted.** Mail is the authentication channel for the whole population, so a deployment that
cannot send mail has no working access for anyone, and the remedy is to fix mail — a configuration action
taken by the same principal who can already set `AIDIAG_ADMIN_EMAILS`. A recovery path that bypassed mail
would be a second authentication mechanism maintained for a fault that blocks everything else regardless.

**What would resolve it.** An operator procedure outside the application, authorized by infrastructure
credentials rather than by anything in this document, that writes the `ADMIN` record of §50.4 directly. It
introduces no stored secret and no new route, moves no authority that §50.6 has not already located with
the holder of deployment configuration, and works with the transport down. Its cost is a documented and
rehearsed procedure, plus a `SYSTEM#ADMIN_RECOVERY` audit entry written from outside the request path.

Taking this up adds a subsection to §50 and removes this entry. It changes no requirement already stated.

## K-2 — Administrative recovery depends on the System table

The configured administrator list is validated against `adminDomainAllowlist`
([DynamoDB System Table](SPEC_data_system.md) §6.3), an absent value admits nothing, and so a missing or
unreadable allowlist item blocks recovery as completely as an empty list would. The list itself is held in
deployment configuration partly so that recovery does not depend on a data layer in an unknown state
(§50.1) — and the constraint on the list reintroduces exactly that dependency.

**Why it is accepted.** The allowlist is a separation-of-duty control, and a control an administrator can
widen is not a control ([DynamoDB System Table](SPEC_data_system.md) §6.1). Holding it as a protected
setting is what makes it one. Holding a second copy in deployment configuration would create two values
that must agree and can be set independently, which is the failure mode §6 of
[Outbound Mail Transport](SPEC_outbound_mail.md) rejects for the sending domain, for the same reason.

**What bounds it today.** §50.1 requires the allowlist item to be provisioned by the same deployment
action that sets `AIDIAG_ADMIN_EMAILS`, so the two cannot be introduced separately, and requires the
startup failure to name which of the two is at fault.

**What would resolve it.** Nothing bounded. A deployment-configuration fallback consulted when the item is
absent would resolve the availability problem and reopen the divergence problem; the K-1 operator
procedure would sidestep both, since a procedure writing the record directly need not consult the
allowlist that constrains the list. That is one reason to prefer it.

---

# 52. Summary

The final architecture intentionally keeps identity management simple.

The Business DynamoDB table already knows:

```text
USER#U123
    │
    ├── email
    ├── fullName
    ├── companyName
    ├── position
    ├── orgId
    ├── role
    └── status
```

The authentication process does not ask the user to establish or declare their identity.

Instead:

```text
Provisioned user
       │
       ▼
Magic-link sent to authoritative email
       │
       ▼
User controls mailbox
       │
       ▼
Consents in force decided
       │
       ▼
Single-use invitation consumed
       │
       ▼
Temporary authenticated session
       │
       ▼
session → userId
       │
       ▼
server-side authorization
```

The three DynamoDB tables have clear responsibilities:

```text
Business
"What is true now?"

Audit
"What security/business events happened?"

System
"What reference data is in force?"
```

Technical telemetry sits outside DynamoDB, in CloudWatch:

```text
CloudWatch
"What happened technically?"
```

The one thing the application cannot already know is who its first administrator is, since there is no
administrator to tell it (§7.1). That single fact comes from deployment configuration, and it confers the
ability to obtain an account rather than an account — the magic link still has to be received (§50).

The fundamental authentication principle is:

> **The application already knows who the user is. The magic link proves possession of the provisioned email account. The resulting session binds that authenticated user to an opaque `userId`.**