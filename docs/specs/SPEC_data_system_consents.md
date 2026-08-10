# AdvisorX Engineering Specification
# Consents Storage and Management

**Status:** Proposed  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** System (consent catalog), Business (acceptance facts)

---

## 1. Purpose

This specification defines the storage and management of the application's consents.

It covers two distinct things, which shall not be confused:

| | What it is | Where it lives |
|---|---|---|
| **Consent catalog** | The consents that exist and may be presented to a user, with their text and their presentation rules | System table |
| **Acceptance facts** | What a named user decided, about which consent, at which version, and when | Business table |

The catalog is versioned reference data, mutable only through an administrative process. An acceptance
fact is evidence of a decision a user made and is never rewritten.

The moments at which acceptance facts are captured — the consent gate on the invitation page, and the
mid-session gate that catches a session predating a catalog change — are specified in
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49 and §49.6. This document
specifies what is stored on both sides of that gate.

---

# 2. Design Goals

The consent architecture shall provide:

1. Upload and versioning of the prepared markdown consent definition.
2. Retrieval of a consent, its id and its version, by id or by label.
3. Retrieval of every consent in force, in presentation order, in one query.
4. A consent that is withdrawn from use without being deleted.
5. A distinction between consents a user must accept and consents a user may decline.
6. An acceptance fact that remains interpretable after the catalog moves on.
7. Recording of refusals, not only of acceptances.
8. Erasure-compatible acceptance facts, referencing the user by `userId` only.

---

# 3. Non-Goals

The system does not provide:

- deletion of consents; a consent withdrawn from use is marked `DISABLED` and retained;
- deletion or amendment of a published consent version;
- deletion or amendment of a recorded acceptance fact;
- self-service authoring of consent text by non-administrators;
- consent withdrawal after the fact, which is a separate workflow and is not specified here;
- legal review of the consent copy, which is not an engineering function (§16).

---

# 4. Consent Definition

A consent is identified by an opaque `consentId` and carries the following attributes.

| Attribute | Type | Versioned | Description |
|---|---|:--:|---|
| `consentId` | string | — | Opaque, stable identifier. Constant across all versions of the consent. |
| `label` | string | — | Short human-facing name, such as `C-1`. Unique across the catalog, permanent, never reused. |
| `title` | string | Yes | The checkbox label the user reads and agrees to. |
| `content` | markdown | Yes | The full consent text. |
| `order` | number | — | Presentation position. `0` is shown first (§7). |
| `status` | enum | — | `ACTIVE` or `DISABLED` (§8). |
| `mandatory` | boolean | — | Whether the user may proceed without accepting it (§8). |
| `version` | integer | Yes | Monotonic, starting at `1`. |
| `contentHash` | string | Yes | SHA-256 over the version's `title` and `content`. Pins the exact text a user agreed to. |

The split between versioned and unversioned attributes follows one rule:

> Everything the user reads is versioned and immutable. Everything that governs presentation or policy
> is current-state only and mutable.

`title` is therefore versioned. It is not decoration: it is the sentence next to the checkbox, and it
is what the user is most likely to have actually read.

Permitted `status` values are defined by CONSENT_STATUS in [Common Dictionaries](dictionaries.md).

---

# 5. System DynamoDB Table

The entity primary key is defined by `CONSENT` (see [DynamoDB System Table](SPEC_data_system.md)).

A consent occupies one control item, one immutable item per published version, and one label lookup
item.

```text
PK                              SK                  Purpose
─────────────────────────────   ─────────────────   ────────────────────────────────
CONSENT#01JCNSA...              METADATA            Mutable control item
CONSENT#01JCNSA...              VERSION#0001        Immutable published text
CONSENT#01JCNSA...              VERSION#0002        Immutable published text

CONSENT_LABEL#C-1               CONSENT             Label → consentId lookup
```

### Control item

```json
{
  "PK": "CONSENT#01JCNSA...",
  "SK": "METADATA",
  "entityType": "CONSENT",

  "consentId": "01JCNSA...",
  "label": "C-1",

  "order": 0,
  "status": "ACTIVE",
  "mandatory": true,

  "currentVersion": 2,

  "consentStatus": "ACTIVE",
  "orderKey": "0000#01JCNSA...",

  "createdAt": "2026-08-10T09:00:00Z",
  "updatedAt": "2026-08-10T11:30:00Z"
}
```

`consentStatus` and `orderKey` are derived duplicates of `status` and `order`, maintained server-side
in the same write, and exist only to key the secondary index of §10. `status` and `order` remain the
authoritative values.

### Version item

```json
{
  "PK": "CONSENT#01JCNSA...",
  "SK": "VERSION#0002",
  "entityType": "CONSENT_VERSION",

  "consentId": "01JCNSA...",
  "version": 2,

  "title": "I agree to participate in this AI Readiness interview.",
  "content": "PLACEHOLDER: I agree to participate ...",
  "contentHash": "<SHA-256>",

  "createdAt": "2026-08-10T11:30:00Z",
  "createdBy": "01JADMIN..."
}
```

The version number in the sort key shall be zero-padded to a fixed width, so that lexicographic order
equals numeric order and the highest version is the last item in the partition.

### Label lookup item

```json
{
  "PK": "CONSENT_LABEL#C-1",
  "SK": "CONSENT",
  "entityType": "CONSENT_LABEL_LOOKUP",
  "consentId": "01JCNSA..."
}
```

Creation of a consent and creation of its label lookup shall be performed atomically, under a
condition that the lookup does not already exist. This is the mechanism that makes `label` unique, and
it mirrors the email lookup of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §8.

A label is permanent. A `DISABLED` consent keeps its label and its lookup item, because acceptance
facts already recorded against that label (§9) must remain resolvable.

Permitted `entityType` values are defined by ENTITY_TYPE in
[Common Dictionaries](dictionaries.md).

---

# 6. Versioning

Publishing a new version shall:

1. write `VERSION#<n+1>` as a new item, conditional on its own non-existence;
2. update `currentVersion` on the control item from `n` to `n + 1`, conditional on it still being `n`.

Both writes shall occur in a single transaction. The condition on step 2 is what prevents two
concurrent publications from producing two version items where only one is reachable through
`currentVersion`.

A published version item shall never be updated or deleted. Correcting consent text means publishing a
further version.

Republishing does not invalidate acceptance facts recorded against earlier versions. Those facts remain
true: the user agreed to the text they were shown. Whether a new version requires the user to decide
again is determined at the gate, by comparing the user's recorded version against `currentVersion`
([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49).

---

# 7. Ordering

`order` determines presentation position. Lower values are presented first, `0` first of all.

Values need not be unique and need not be contiguous. Gaps are expected, and are useful: they allow a
consent to be inserted between two existing ones without rewriting the catalog.

Because values need not be unique, `order` alone is not a total order. The presentation order is:

```text
(order ascending, then consentId ascending)
```

This tie-break is not cosmetic. Two consents sharing an `order` value would otherwise render in an
arbitrary sequence that could differ between two page loads, and a consent block whose rows move
between renderings is a weak evidentiary record of what the user was shown.

`orderKey` on the control item encodes this total order directly, so that the index of §10 returns
rows already sorted and no client-side sort is required.

---

# 8. Status and the Mandatory Flag

### status

| Value | Meaning |
|---|---|
| `ACTIVE` | In force. Presented at the gate. |
| `DISABLED` | Withdrawn from use. Not presented, not deleted. |

Disabling a consent shall not delete it, shall not delete its versions, and shall not delete or alter
any acceptance fact recorded against it.

A `DISABLED` consent is not presented at the gate and shall not block a user from proceeding, even if
`mandatory` is `true`. `status` is evaluated before `mandatory`.

### mandatory

| Value | Effect at the gate |
|---|---|
| `true` | The user cannot proceed until the box is checked. |
| `false` | The user may proceed with the box unchecked. The refusal is recorded (§9). |

`mandatory` is a property of the consent, not of the user interface. The client renders it; the server
enforces it. A client that omits a mandatory consent, or reports it as declined, shall be refused
([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49).

Changing `mandatory` is a policy change, not a text change, and does not by itself produce a new
version. It shall be recorded in the Audit table (§12), because it changes the conditions under which
users may enter the application.

### The mandatory generation counter

A single System-table item shall hold a monotonically increasing counter:

```text
PK = CONSENT_CATALOG
SK = METADATA
```

```json
{
  "PK": "CONSENT_CATALOG",
  "SK": "METADATA",
  "entityType": "CONSENT_CATALOG",

  "mandatoryGeneration": 7,
  "updatedAt": "2026-08-10T09:00:00Z"
}
```

`mandatoryGeneration` shall be incremented, in the same transaction as the change, whenever any of the
following occurs:

- a new consent becomes `ACTIVE` with `mandatory` `true`;
- a new version is published for a consent that is `ACTIVE` and `mandatory`;
- `mandatory` changes from `false` to `true` on an `ACTIVE` consent;
- `status` changes from `DISABLED` to `ACTIVE` on a consent that is `mandatory`.

It shall **not** be incremented by a change affecting only optional consents, by disabling a consent, or
by a reordering. Those change what a user is *asked*, not what a user is *required* to have accepted, and
the counter exists to answer the second question only.

The counter exists so that the mid-session gate of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49.6 costs one integer comparison on
an ordinary authenticated request instead of a catalog query. Recomputing the outstanding set on every
request would put a query against this table, plus a query against the user's acceptance facts, on the
path of every request the application serves — for an answer that changes a handful of times in the life
of the deployment.

It is a counter rather than a timestamp because it shall be comparable for equality by a caller that holds
a stale copy, and because two changes in the same second must be distinguishable. It is monotonic and
shall never be reset; a reset would make every live session appear current when it is not, which is the
one failure this mechanism must not have.

---

# 9. Acceptance Facts

An acceptance fact records one user's decision about one version of one consent. It lives in the
Business table, under the owning user's partition, and is keyed:

```text
PK = USER#<userId>
SK = CONSENT_ACCEPTANCE#<consentId>#<version>
```

```json
{
  "PK": "USER#01JXYZ...",
  "SK": "CONSENT_ACCEPTANCE#01JCNSA...#0002",
  "entityType": "CONSENT_ACCEPTANCE",

  "userId": "01JXYZ...",

  "consentId": "01JCNSA...",
  "consentLabel": "C-1",
  "consentVersion": 2,
  "contentHash": "<SHA-256>",

  "accepted": true,
  "mandatoryAtDecision": true,

  "decidedAt": "2026-08-10T09:12:03Z",
  "decisionContext": "INVITATION",
  "invitationId": "01KDEF..."
}
```

The version forms part of the sort key, so a decision about a later version is a new item rather than
an overwrite of the earlier one. An acceptance fact shall never be updated. The user's current
standing decision about a consent is the item with the highest `version`; the earlier items are the
record of what they decided before, which is the part a consent trail is for.

`accepted` is recorded for refusals as well as acceptances. A recorded `false` against an optional
consent is not an absence of data — it is an instruction not to use the data that way, and it is worth
strictly more than a missing item, which is indistinguishable from a consent that was never presented.

`mandatoryAtDecision` captures whether the box could have been left unchecked at the time. Without it,
an `accepted: true` against a consent that is mandatory today cannot be distinguished from a free
choice made when it was optional.

`contentHash` pins the decision to exact text. `consentLabel` is denormalized deliberately, against the
general rule of [DynamoDB Business Table](SPEC_data_business.md) §5: an acceptance fact is an
evidentiary record that shall stay readable on its own, without resolving a reference into a versioned
catalog whose entry may since have been disabled. It is reference data rather than identity data, so
duplicating it creates no PII exposure.

`invitationId` records the magic-link invitation that proved mailbox possession for this decision. This
is the evidentiary link between the decision and that proof.

`decisionContext` states how close together the two were, and the distinction is evidentiary rather than
operational. Permitted values are defined by CONSENT_DECISION_CONTEXT in
[Common Dictionaries](dictionaries.md):

| Value | Meaning | `invitationId` is |
|---|---|---|
| `INVITATION` | Decided at the gate, in the transaction that consumed the invitation | The invitation consumed in that same transaction |
| `SESSION` | Decided inside an existing session, at the mid-session gate ([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49.6) | The invitation that created that session, recorded on the session record |

Both carry an `invitationId`, so both trace to a proof of mailbox possession. They differ in how recent
that proof was: under `INVITATION` the same request carried both, and under `SESSION` the possession was
proven when the session began and the decision was taken later. Recording them identically would assert a
contemporaneity that did not hold, which is precisely the kind of claim an evidentiary record must not
make on its own.

The record references the user by `userId` only. It carries no `email`, `fullName`, `companyName` or
`position`, consistent with [DynamoDB Business Table](SPEC_data_business.md) §5.

### Erasure

Acceptance facts sit inside the `USER#<userId>` partition, so the erasure workflow of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §34 locates them with the same
single query that finds the user's other business entities.

Whether they are then deleted is a retention decision rather than a mechanical one. They record the
lawful basis on which the user's data was processed, so deleting them removes the evidence that
processing was permitted. They contain no PII beyond `userId`, so severing the profile leaves an
acceptance trail that is no longer directly identifying. The classification exercise of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §35 shall cover them explicitly.

---

# 10. Access Patterns

### List the consents to present at the gate

Served by a global secondary index on the System table.

#### consentOrderIndex

```text
PK = consentStatus
SK = orderKey
```

```text
Query consentStatus = "ACTIVE", ascending
  → control items, already in presentation order (§7)
```

The query returns `consentId`, `label`, `order`, `mandatory` and `currentVersion`. The text is then
read with a single `BatchGetItem` over `CONSENT#<consentId> / VERSION#<currentVersion>`.

Only consent control items carry `consentStatus` and `orderKey`, so only they appear in the index.
Settings, e-mail templates, prompts and consent version items do not, which is the reason the gate can
use an index query rather than a table scan.

The index has two partitions, and the `ACTIVE` partition is read on every first login. The catalog is
a handful of items that change only through administrative action, so the application should cache the
resolved list rather than query it per request. Whichever it does, the enforcement of §8 remains
server-side.

### Get a consent by id, current version

```text
PK = CONSENT#<consentId>
SK = METADATA          → currentVersion
SK = VERSION#<n>       → title, content
```

A single query on `PK = CONSENT#<consentId>` with `SK begins_with VERSION#`, descending, limit 1, returns
the same text in one read, because the transaction of §6 keeps `currentVersion` and the highest version
item in agreement. The two-read form is still preferable on the gate path, which needs `order` and
`mandatory` from the control item regardless.

### Get a consent by label, current version

```text
PK = CONSENT_LABEL#<label>
SK = CONSENT           → consentId
```

then as above. This is the path used when seeding the catalog from
[consent copy](../../content/consent_copy.md), where consents are named `C-1` and `C-2` rather than by
identifier.

### Retrieve a user's decisions

```text
PK = USER#<userId>
SK begins_with CONSENT_ACCEPTANCE#
```

Returns every decision the user has made, across all consents and versions. The current standing
decision per consent is the highest `version` in each `consentId` group.

### Retrieve a user's decisions about one consent

```text
PK = USER#<userId>
SK begins_with CONSENT_ACCEPTANCE#<consentId>#
```

---

# 11. Client Presentation Contract

The consent block is presented in two places, and the rules below apply identically in both:

- on the invitation page, before a session exists
  ([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §17, §49);
- inside the application shell, where a mandatory consent became outstanding during a live session
  ([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49.6).

The block is the same block. The client obtains its contents from the same endpoint, renders the same
heading and rows, and submits the same decision shape; only the surface it is drawn on and the route it
submits to differ. Specifying one presentation for both is deliberate — a second, separately-written
consent block is where rule 5 below gets quietly relaxed.

The rows below are illustrative. Which consents appear, in what order, and which of them are mandatory
comes from the catalog and from nowhere else.

```text
I agree with the following consents

[ ] Participation & recording *
    I agree to participate in this AI Readiness interview...        (C-1, mandatory)

[ ] Data use *
    I understand my responses will be processed by...               (C-2, mandatory)

[ ] Anonymized benchmarking
    My responses may be included in anonymized benchmarks...        (C-3, optional)

                                                     [Continue]
```

The client shall:

1. render the block under the heading **"I agree with the following consents"**;
2. render one row per `ACTIVE` consent, in the order received, without re-sorting;
3. use the version's `title` as the row label, and make the version's `content` readable in place;
4. mark mandatory rows distinguishably from optional ones;
5. leave **every** box unchecked initially, mandatory and optional alike;
6. keep the continue action disabled until every mandatory box is checked;
7. submit a decision for every presented consent, including the unchecked optional ones.

Rule 5 is not a default that may be tuned. A box that arrives pre-ticked records the absence of an
action rather than the presence of one, and is not consent. This holds for mandatory consents in
particular: pre-ticking them makes the gate a formality that the user can pass without reading
anything.

There shall be no single control that accepts several consents at once. Each consent covers a distinct
purpose and shall be decidable on its own.

Rules 4 and 6 are user-interface affordances. They are not the enforcement mechanism, which is
server-side and is specified in
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49. A client that does not
implement rule 6 produces a rejected request, not an unconsented session.

The `content` is markdown and shall be rendered as such. Consent text is authored by Legal and may
contain links and emphasis; rendering it as plain text degrades the copy that Legal approved.

---

# 12. Audit Events

The following event types extend the list in
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §29:

```text
CONSENT_ACCEPTED
CONSENT_DECLINED
CONSENT_CREATED
CONSENT_VERSION_PUBLISHED
CONSENT_STATUS_CHANGED
CONSENT_POLICY_CHANGED
```

`CONSENT_ACCEPTED` and `CONSENT_DECLINED` are written per consent, per decision, in the user's audit
partition, and carry `consentId`, `consentVersion` and `contentHash`.

`CONSENT_POLICY_CHANGED` covers a change to `mandatory` or `order`. `CONSENT_STATUS_CHANGED` covers
activation and deactivation. Both are administrative events and shall record the acting administrator's
`userId`.

Catalog events concern no single subject user. They shall be written under an administrative partition
rather than under `USER#<userId>`, so that a user's audit partition remains the record of that user's
own history.

---

# 13. Management API

All endpoints in this section require the `ADMIN` role. `Manage consents` is an `ADMIN`-only capability
in the [Role Model](role_model.md), and is held by no other role.

```http
GET    /admin/consents                          List the catalog, including DISABLED
POST   /admin/consents                          Create a consent and its first version
GET    /admin/consents/{consentId}              Control item plus version history
POST   /admin/consents/{consentId}/versions     Publish a new version (§6)
PATCH  /admin/consents/{consentId}              Change order, status or mandatory (§8)
```

`PATCH` shall not accept `title` or `content`. Text changes are published as versions, and an endpoint
that silently mutated the text of a version already agreed to would break the guarantee that
`contentHash` pins what a user read.

**`POST`, `POST .../versions` and `PATCH` shall increment `mandatoryGeneration` (§8) in the same
transaction as the change, where the change meets one of the conditions listed there.** Incrementing
afterwards would leave a window in which a consent is mandatory and outstanding while every live session
still believes it is current — which is the exact gap
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49.6 exists to close, reintroduced by
the mechanism that closes it.

Each of these endpoints shall report whether it incremented the counter, so that an administrator making a
policy change learns that it will interrupt users in live sessions before they discover it from support
traffic.

`POST /admin/consents` shall reject a `label` already present in the catalog, including one held by a
`DISABLED` consent (§5).

The gate-side read path is not part of this API. It is served through the invitation context and is
specified in [Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §41.6.

---

# 14. Python Models

```python
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

ConsentStatus = Literal["ACTIVE", "DISABLED"]
ConsentDecisionContext = Literal["INVITATION", "SESSION"]


class ConsentModel(BaseModel):
    """Attributes and JSON payloads use camelCase; Python fields use snake_case."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---------- catalog (System table) ----------
class Consent(ConsentModel):
    """CONSENT#<consentId> / METADATA — mutable control item.

    The derived index attributes `consentStatus` and `orderKey` (§5) are absent by
    design: they are maintained by the persistence layer from `status` and `order`,
    and nothing above it should be able to set them independently.
    """

    consent_id: str
    label: str                                  # "C-1"

    order: int = Field(ge=0)                    # 0 is presented first
    status: ConsentStatus = "ACTIVE"
    mandatory: bool = False

    current_version: int = Field(ge=1)

    created_at: str
    updated_at: str


class ConsentVersion(ConsentModel):
    """CONSENT#<consentId> / VERSION#<version> — immutable published text."""

    consent_id: str
    version: int = Field(ge=1)

    title: str
    content: str                                # markdown
    content_hash: str

    created_at: str
    created_by: str                             # userId of the acting administrator


# ---------- gate payloads ----------
class ConsentPresentation(ConsentModel):
    """One row of the consent block, sent to the client at the gate."""

    consent_id: str
    label: str
    version: int
    title: str
    content: str                                # markdown
    order: int = Field(ge=0)
    mandatory: bool


class ConsentDecision(ConsentModel):
    """One row of the consent block, returned by the client with POST /session."""

    consent_id: str
    version: int                                # the version the client displayed
    accepted: bool


# ---------- acceptance fact (Business table) ----------
class ConsentAcceptance(ConsentModel):
    """USER#<userId> / CONSENT_ACCEPTANCE#<consentId>#<version> — immutable."""

    user_id: str

    consent_id: str
    consent_label: str
    consent_version: int = Field(ge=1)
    content_hash: str

    accepted: bool
    mandatory_at_decision: bool

    decided_at: str
    decision_context: ConsentDecisionContext
    invitation_id: Optional[str] = None
```

`ConsentPresentation` and `ConsentDecision` are separate types on purpose. The client receives text,
ordering and policy; it returns only an identifier, a version and a boolean. Reusing one type for both
directions invites a handler that trusts a client-supplied `mandatory` field, which is exactly the
check the server must make for itself.

`ConsentDecision.version` is not redundant. It is the version the client actually rendered, and the
server compares it against `currentVersion` to detect a page that went stale while the user was reading
it ([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §49).

---

# 15. TypeScript Models

```ts
export type ConsentStatus = 'ACTIVE' | 'DISABLED'

/** CONSENT#<consentId> / METADATA — admin views only. */
export interface Consent {
  consentId: string
  label: string
  order: number
  status: ConsentStatus
  mandatory: boolean
  currentVersion: number
  createdAt: string
  updatedAt: string
}

/** CONSENT#<consentId> / VERSION#<version> — admin views only. */
export interface ConsentVersion {
  consentId: string
  version: number
  title: string
  content: string
  contentHash: string
  createdAt: string
  createdBy: string
}

/** One row of the consent block, as received at the gate. */
export interface ConsentPresentation {
  consentId: string
  label: string
  version: number
  title: string
  content: string
  order: number
  mandatory: boolean
}

/** One row of the consent block, as submitted with POST /session. */
export interface ConsentDecision {
  consentId: string
  version: number
  accepted: boolean
}

/** USER#<userId> / CONSENT_ACCEPTANCE#<consentId>#<version> — admin/export views only. */
export interface ConsentAcceptance {
  userId: string
  consentId: string
  consentLabel: string
  consentVersion: number
  contentHash: string
  accepted: boolean
  mandatoryAtDecision: boolean
  decidedAt: string
  decisionContext: 'INVITATION' | 'SESSION'
  invitationId: string | null
}

/** Initial state: every box unchecked, mandatory and optional alike (§11 rule 5). */
export function initialDecisions(
  consents: ConsentPresentation[],
): Record<string, boolean> {
  return Object.fromEntries(consents.map((c) => [c.consentId, false]))
}

/** Gate rule: mandatory boxes cannot be skipped, optional ones can (§8). */
export function canContinue(
  consents: ConsentPresentation[],
  checked: Record<string, boolean>,
): boolean {
  return consents.every((c) => !c.mandatory || checked[c.consentId] === true)
}

/** Every presented consent is submitted, including the unchecked ones (§11 rule 7). */
export function toDecisions(
  consents: ConsentPresentation[],
  checked: Record<string, boolean>,
): ConsentDecision[] {
  return consents.map((c) => ({
    consentId: c.consentId,
    version: c.version,
    accepted: checked[c.consentId] === true,
  }))
}
```

`canContinue` governs whether the continue control is enabled. It is a user-interface convenience and
carries no security weight: the server applies the same rule to the submitted decisions and rejects a
request that fails it.

---

# 16. Consent Copy

The consent text is authored and approved outside engineering. The placeholder copy in
[consent copy](../../content/consent_copy.md) is not approved text and shall not be seeded into a
catalog used for a real interview.

Which consents are `mandatory` is likewise a Legal determination, not an engineering default. This
document specifies the mechanism by which a consent is mandatory; it does not decide which consents
are. A worked example, illustrative only:

```text
label   order   status    mandatory
─────   ─────   ───────   ─────────
C-1     0       ACTIVE    true        Participation & recording
C-2     10      ACTIVE    true        Data use
```

The engine records only which consent, at which version, was accepted or declined, by which `userId`,
and when (§9). It does not interpret the text.

---

# 17. Relationship to the Current Prototype

The prototype carries a fixed consent set: `ConsentRecord` in `app/models.py` and `ConsentData` in
`web/src/types.ts`, with `c1_use_for_scorecard` through `c4_cross_practice_sharing` as named boolean
fields.

That shape is superseded by this specification. Adding or rewording a consent in it requires a code
change and a deployment, nothing records which text the user saw, and two of its four fields default to
checked — including one that is submitted as permanently `true`. The catalog model replaces all three
properties: consents become data, decisions are pinned to `contentHash`, and §11 rule 5 forbids the
pre-checked defaults from carrying over.

---

# 18. Access

See [Role Model](role_model.md)
