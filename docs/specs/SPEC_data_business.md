# AdvisorX Engineering Specification
# Business Data Storage and Management

**Status:** Proposed  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** Business

---

## 1. Purpose

This specification defines a business data storage system for an application with a **single DynamoDB table**.

The authentication entities in this table — users, email lookups, invitations and sessions — are
specified in [Passwordless Email Authentication](SPEC_passwordless_email_auth.md). This document
specifies the business entities that share the table.

---

# 2. Design Goals

The data storage architecture shall provide:

1. A single-table design serving the application's actual access patterns.
2. Business entities keyed under the owning user, so that a user's data is retrievable in one query.
3. Reference to the user by `userId` only, with no duplication of authoritative identity attributes.
4. Minimal duplication of PII.
5. User-oriented erasure within a single partition.
6. Consistent entity naming, drawn from ENTITY_TYPE in [Common Dictionaries](dictionaries.md).

---

# 3. Non-Goals

The system does not provide:

- authentication or session storage — see [Passwordless Email Authentication](SPEC_passwordless_email_auth.md);
- versioned reference data such as consents, prompts, templates or settings — see [DynamoDB System Table](SPEC_data_system.md);
- audit or security event history, which lives in the Audit table;
- technical or operational diagnostics, which live in Amazon CloudWatch.

---

# 4. Business DynamoDB Table

The Business table contains:

* Users
* Invitations
* Sessions
* Mail suppression records
* Interviews
* Synth outputs
* Quick wins
* Consent acceptance facts

A single-table design is recommended.

Example:

```text
PK                              SK
─────────────────────────────   ─────────────────────
USER#01JXYZ...                  PROFILE
USER#01JXYZ...                  INTERVIEW#01KINT...
USER#01JXYZ...                  SYNTH_OUTPUT#01KINT...
USER#01JXYZ...                  QUICK_WINS#01KINT...
USER#01JXYZ...                  CONSENT_ACCEPTANCE#01JCNSA...#0002

MAIL_SUPPRESSION#john@ex.com     METADATA
```

Business entities are keyed under the `USER#<userId>` partition of their owning user.

Mail suppression records are the exception, and deliberately so. They are keyed by normalized email
address because suppression follows the mailbox rather than the account: a mailbox reassigned to
another user is the same mailbox to the mail transport. Their content and lifecycle are specified in
[Outbound Mail Transport](SPEC_outbound_mail.md) §14; the consequence for erasure — that they lie
outside the user's partition and are not found by querying it — is recorded in
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §34.

> **Open:** the example keys `SYNTH_OUTPUT` and `QUICK_WINS` by the interview they derive from, which
> permits at most one of each per interview. If either may exist in more than one instance per
> interview, they require their own identifiers instead. This is not yet decided.

Permitted `entityType` values are defined by ENTITY_TYPE in
[Common Dictionaries](dictionaries.md).

Interviews and their related entities are specified further in
[Interview Storage and Management](SPEC_data_business_interviews.md).

Consent acceptance facts are the Business-table half of the consent model: the consents that exist are
versioned reference data in the System table, and what a user decided about them is a fact about that
user. Both halves are specified in
[Consents Storage and Management](SPEC_data_system_consents.md); the item shape is in its §9. Their sort
key carries the consent version, so a later decision about the same consent is a new item rather than an
overwrite — these records are evidence, and the erasure and retention consequences are covered in
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §35.

---

# 5. Identity Reference

Business entities shall reference the user by `userId`.

Preferred:

```json
{
  "interviewId": "01KINT...",
  "userId": "01JXYZ..."
}
```

Avoid unnecessary duplication:

```json
{
  "interviewId": "01KINT...",
  "userId": "01JXYZ...",
  "email": "john@example.com",
  "fullName": "John Smith",
  "companyName": "Northwind Manufacturing"
}
```

Business entities shall not duplicate the authoritative identity attributes `email`, `fullName`,
`companyName`, `position`, `orgId` or `role`. The `USER#<userId> / PROFILE` item remains the source of
those values.

This reduces PII duplication and prevents inconsistent copies of user information.

Historical business records should only contain denormalized identity information when there is a documented business requirement for doing so.

---

# 6. Access Patterns

### Retrieve a user's business data

```text
PK = USER#<userId>
```

### Retrieve a single business entity

```text
PK = USER#<userId>
SK = <ENTITY_TYPE>#<entityId>
```

### Retrieve entities of one type for a user

```text
PK = USER#<userId>
SK begins_with <ENTITY_TYPE>#
```

The exact business entity patterns shall be designed around actual application access patterns.

One entity extends the `<ENTITY_TYPE>#<entityId>` form. A consent acceptance is keyed
`CONSENT_ACCEPTANCE#<consentId>#<version>`, because a user may decide the same consent more than once and
each decision is kept. The `begins_with` patterns above still serve it, at either level of the compound
suffix; see [Consents Storage and Management](SPEC_data_system_consents.md) §10.

Because every business entity for a user shares that user's partition, the erasure workflow specified
in [Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §34 can locate a user's
business data with a single query.

---

# 7. Secondary Indexes

Every access pattern in §6 is served by the primary key. One pattern is not, and requires a global
secondary index.

### providerMessageIdIndex

```text
PK = providerMessageId
```

Mail delivery events identify a message by the mail transport's own message identifier rather than by
`invitationId`, so the invitation they refer to cannot be located by primary key. This index resolves
that identifier to the invitation record, and exists for the ingestion path specified in
[Outbound Mail Transport](SPEC_outbound_mail.md) §13.

It need project only the attributes required to locate the base record, because applying a delivery
event reads and conditionally updates that record.

Only invitation records carry `providerMessageId`, so only they appear in the index.

Further indexes shall be introduced only for access patterns the primary key cannot serve.

---

# 8. Access

See [Role Model](role_model.md)
