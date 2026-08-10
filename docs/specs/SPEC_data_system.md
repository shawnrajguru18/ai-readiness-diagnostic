# AdvisorX Engineering Specification
# System Data Storage and Management

**Status:** Proposed  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** System

---

## 1. Purpose

This specification defines a general data storage system for an application with a **single DynamoDB table**.

---

# 2. Design Goals

The data storage architecture shall provide:

1. TBD

---

# 3. Non-Goals

The system does not provide:

- TBD

---

# 4. System DynamoDB Table

The System table contains:

* Versioned Consents, PK - CONSENT#..
* Consent label lookups, PK - CONSENT_LABEL#..
* Consent catalog metadata, PK - CONSENT_CATALOG
* Application Settings, PK - SETTING#..
* E-mail templates, PK - TEMPLATE#..
* Versioned Prompts, PK - PROMPT#..

A single-table design is recommended.

Example:

```text
PK                         SK
────────────────────────   ─────────────────────
TBD
```

Consents are specified in [Consents Storage and Management](SPEC_data_system_consents.md). What a user
decided about a consent is not held here; it is a fact about that user and lives in the Business table.

Settings are specified in §6. Not every setting is administratively editable, and §6.1 is the reason.

---

# 5. Secondary Indexes

### consentOrderIndex

```text
PK = consentStatus
SK = orderKey
```

Returns the consents in force, in presentation order, in one query. Only consent control items carry
these two attributes, so the index is sparse and contains no settings, templates, prompts or consent
version items. Specified in [Consents Storage and Management](SPEC_data_system_consents.md) §10.

Further indexes shall be introduced only for access patterns the primary key cannot serve.

---

# 6. Application Settings

Configurable values shall be held as setting items in this table, except where another specification
marks a value secret and holds it outside
([Outbound Mail Transport](SPEC_outbound_mail.md) §20.6, §21).

```text
PK = SETTING#<settingKey>
SK = METADATA
```

```json
{
  "PK": "SETTING#adminDomainAllowlist",
  "SK": "METADATA",
  "entityType": "SETTING",

  "settingKey": "adminDomainAllowlist",
  "value": ["catalyst.one", "example.com"],

  "updatedAt": "2026-08-10T09:00:00Z",
  "updatedBy": "SYSTEM#DEPLOYMENT"
}
```

Permitted `entityType` values are defined by ENTITY_TYPE in [Common Dictionaries](dictionaries.md).

## 6.1 Mutability classes

`ADMIN` may manage application settings ([Role Model](role_model.md)). That capability shall not extend
to every setting, because some settings are constraints on what an administrator may do, and a
constraint the constrained population can edit is not a constraint.

Every setting key therefore belongs to exactly one class:

| Class | Written by | Application route |
|---|---|---|
| **Managed** | `ADMIN`, through the application | Yes |
| **Protected** | Deployment provisioning only | **None** |

A write to a protected setting shall be refused by the application, whatever the caller's role. There is
no route that performs it, no administrative override, and no reason for either: the value changes when
the deployment changes it.

**The class is a property of the setting key, fixed by §6.2, and shall not be an attribute of the item.**
Storing the class alongside the value would make it editable by whoever can edit the value — an `ADMIN`
would reclassify a protected setting as managed and then write it, in two ordinary operations that each
look permitted. The application shall hold the classification and consult it before any write.

Every change to a setting shall write a `SETTING_CHANGED` audit event, of either class, recording the key
and that the value changed. It shall not record the previous or new value where the setting names people
or domains. A change to a managed setting shall additionally record the acting `userId`, since a managed
change has an actor and a protected one does not.

Auditing managed changes is not incidental. A managed setting is one an administrator may change, which
makes it the class where an unexplained change is possible at all; a protected setting changes only when
the deployment changes, and that is already recorded elsewhere. A refused write to a protected setting
shall also be recorded, and is the most interesting of the three: no legitimate caller attempts one.

## 6.2 Setting registry

| Key | Class | Purpose |
|---|---|---|
| `adminDomainAllowlist` | **Protected** | Mail domains from which an administrator may be drawn (§6.3) |
| `environment`, `publicBaseUrl`, `mailTransport` | **Protected** | Govern the production refusals of [Outbound Mail Transport](SPEC_outbound_mail.md) §10 and §16 |
| `fromEmail`, `replyToEmail` | **Protected** | Sender addresses ([Outbound Mail Transport](SPEC_outbound_mail.md) §6) |
| `mailEventTopic`, `mailDeliveryReportingConfigured` | **Protected** | Delivery-event trust and reported capability ([Outbound Mail Transport](SPEC_outbound_mail.md) §13, §12) |
| `fromName` | Managed | `From` display name ([Outbound Mail Transport](SPEC_outbound_mail.md) §6) |
| `mailSendTimeoutSeconds`, `mailMaxResends`, `invitationTemplateId` | Managed | Operational tuning and reviewed-template selection ([Outbound Mail Transport](SPEC_outbound_mail.md) §11, §15, §8) |

The three refusal-governing keys are protected for the same reason as the allowlist. They are what makes a
production deployment refuse a non-`https` link base and refuse a development transport; a managed
`environment` would let an administrator turn those refusals off, and an authentication link is the whole
of authentication ([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §13).

The **sender addresses** are protected because the `From` domain is bound to DNS records and to a verified
transport identity that no application write can change, because that identity is the scope of the send
authorization held in infrastructure permissions, and because a reply address must be a mailbox someone
has arranged to monitor ([Outbound Mail Transport](SPEC_outbound_mail.md) §6, §20.4, §22). A managed
sender address does not misdeliver mail; it stops mail, silently, for everyone.

`fromName` is managed, and is the illustrative case for where this boundary falls. It is part of the same
sender identity, and it is the value a recipient reads first — but it has no dependency outside the
application, requires no record to be published and no mailbox to exist, and is not what DMARC aligns on.
The class follows the dependency, not the apparent sensitivity: a setting is protected when writing it
through the application would leave something outside the application inconsistent, and managed when the
only requirement on it is that the value be well-formed. A managed setting whose format matters shall be
validated on the write, as that document's §6 requires for this one.

The mail settings are classified in the table of
[Outbound Mail Transport](SPEC_outbound_mail.md) §21, which shall agree with this registry. Where the two
disagree, this registry governs, because the class is a property of the key and this is where keys are
registered.

Further keys shall be added to this registry with their class stated. A setting introduced without a
class defaults to **protected**, because the failure of guessing wrong in that direction is an
administrator who has to file a deployment request, and in the other direction is a control that turns
out not to have been one.

## 6.3 adminDomainAllowlist

The mail domains from which an administrative account may be drawn.

```json
{
  "settingKey": "adminDomainAllowlist",
  "value": ["catalyst.one"]
}
```

Semantics:

- An address whose domain is not a member shall not become an `ADMIN` account by any path.
- Comparison shall be on the normalized address produced by the policy of
  [Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §8, matching the full domain
  label rather than a suffix. A suffix match would admit `catalyst.one.attacker.example`, which is the
  classic form of this mistake.
- An empty or absent value shall be treated as admitting nothing, not as admitting everything. A missing
  constraint that reads as permissive is a constraint that disappears the first time the item fails to
  load.

Its consumer today is the administrative recovery path of
[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §50, which validates the configured
administrator list against it at startup. The allowlist is stored here rather than beside that list
because it is a property of the deployment rather than of the recovery mechanism, and because a second
consumer — ordinary administrative provisioning of staff accounts — is the natural place for it to apply
next.

**It is protected, and that is what makes it usable as a separation-of-duty control.** An administrator
who could widen it could admit a domain they control, provision a staff account there, and hold both that
account and their own. The allowlist only constrains that if the population it constrains cannot edit it.

Validation at startup shall cover this setting and the administrator list together
([Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §50.1). Validating either alone
leaves the other stale: an allowlist narrowed without re-checking the list leaves entries in force that
no longer satisfy it.

