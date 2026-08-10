# Specifications Index

**Updated:** 10 August 2026

The `SPEC_*` family: engineering specifications stating what shall be true, in "shall" language, one
subsystem per document. Plus the two shared references every specification draws on.

**These are the documents of record.** Where a specification and an analysis under
[architecture/analysis/](../architecture/analysis/INDEX.md) disagree, the specification governs. Where a
specification and one of the Phase 1 documents in [architecture/](../architecture/) disagree, the
specification governs and the Phase 1 document is history.

**Conventions across the family.**

- Section references are bare `§N` within a document, and named when they cross a document boundary —
  `[Passwordless Email Authentication](SPEC_passwordless_email_auth.md) §12`.
- Enumerated values are defined once, in [dictionaries.md](dictionaries.md), and are not restated in the
  document that uses them.
- Role capabilities are defined once, in [role_model.md](role_model.md), and are likewise not restated.
- Every requirement is stated in exactly one document. A specification that needs a rule owned elsewhere
  cites it rather than repeating it, because two copies of a requirement are two requirements that drift.
- Requirements carry their reasoning inline. A rule whose justification is not written down is a rule
  that gets relaxed by whoever finds it inconvenient.

**Status** — every document in this family is currently `Proposed`. None has been ratified, and none is
implemented.

---

## Authentication and mail

| Name | Subject | Tables | Status |
|---|---|---|---|
| [SPEC_passwordless_email_auth.md](SPEC_passwordless_email_auth.md) | **The root document of the family.** Passwordless authentication for a closed, pre-provisioned population: opaque `userId`, magic-link invitations that are single-use and never consumed on `GET`, sliding server-side sessions, server-side authorization by `role`. Also owns the email normalization policy, the eligibility definition, the audit-event inventory, the technical-logging rules, GDPR erasure, the consent gate at both the invitation page and mid-session (§49), administrative access recovery from deployment configuration (§50), and the known-issues register (§51). Other specifications cite it for all of these. | Business, Audit, System | Proposed |
| [SPEC_outbound_mail.md](SPEC_outbound_mail.md) | How the invitation is sent, and how its fate is recorded. Amazon SES behind an internal interface with four send outcomes; delivery state on the invitation record with a precedence-ordered state machine; delivery-event ingestion behind two independent gates; complaint suppression enforced before the transport is contacted; markdown template rendering; token secrecy through the mail path; sender identity and DNS requirements. An unacknowledged send is never retried, because one invitation becoming two credentials is worse than one that never arrives. | Business, Audit, System | Proposed |

## Data storage

| Name | Subject | Tables | Status |
|---|---|---|---|
| [SPEC_data_business.md](SPEC_data_business.md) | The Business table's business entities — the ones that are not authentication. Single-table design; entities reference the user by `userId` and do not duplicate identity attributes, which is what keeps erasure tractable. | Business | Proposed |
| [SPEC_data_business_interviews.md](SPEC_data_business_interviews.md) | Interviews and the scorecards derived from them. | Business | Proposed |
| [SPEC_data_system.md](SPEC_data_system.md) | The System table: versioned reference data in force. Owns application settings (§6) and the **mutability classes** — *managed* settings an `ADMIN` may edit through the application, *protected* settings written only by deployment provisioning. The class follows the dependency: a setting is protected when writing it through the application would leave something outside the application inconsistent. Also owns the setting registry and `adminDomainAllowlist`. | System | Proposed |
| [SPEC_data_system_consents.md](SPEC_data_system_consents.md) | Both halves of consent. The versioned catalog lives in the System table; what a user decided lives in the Business table as an immutable acceptance fact keyed by consent and version, so a decision about v1 stays true about v1 after v2 ships. Carries the `mandatoryGeneration` counter that makes the mid-session gate affordable, the presentation contract for both gate surfaces, and the rule that no box is ever pre-ticked. | System, Business | Proposed |
| [SPEC_data_system_templates.md](SPEC_data_system_templates.md) | Versioned markdown e-mail templates, resolved by identifier at the latest `ACTIVE` version. No HTML templates, and no fallback to content compiled into the application — content that has not been versioned has not been reviewed. | System | Proposed |
| [SPEC_data_system_prompts.md](SPEC_data_system_prompts.md) | Versioned prompts. | System | Proposed |

## Shared references

| Name | Subject |
|---|---|
| [dictionaries.md](dictionaries.md) | Every enumerated value in the family: `ENTITY_TYPE`, `ROLE`, `STATUS`, `DELIVERY_STATUS`, `DELIVERY_REPORTING`, `CONSENT_STATUS`, `CONSENT_DECISION_CONTEXT`. One definition per enum, cited rather than copied. |
| [role_model.md](role_model.md) | The capability matrix — what `user`, `power_user`, `partner` and `admin` may each do. Load-bearing beyond authorization: `ADMIN` reads no reports, and `ADMIN` manages application settings, and both facts are cited as constraints elsewhere in the family. |

---

## Reading order

`SPEC_passwordless_email_auth.md` first. It defines the identity model the rest assume, and it owns the
definitions the rest cite — normalization, eligibility, the audit inventory, the erasure workflow. Then
whichever subsystem you need; each names its own dependencies in §1.

`dictionaries.md` and `role_model.md` are lookups rather than reading.

## Open items

Recorded in the documents themselves rather than here, so that an open question sits beside the
requirement it qualifies:

| Where | Item |
|---|---|
| `SPEC_passwordless_email_auth.md` §51 | **K-1** — administrative recovery depends on outbound mail, so it does not recover a deployment whose mail is broken. **K-2** — it also depends on the System table holding a valid allowlist. |
| `SPEC_data_business.md` §5 | Whether `SYNTH_OUTPUT` and `QUICK_WINS` are keyed by the interview they derive from. |

## Not in this directory

The decision record behind the mail transport choice — why SES, and what was ruled out — is
[architecture/analysis/outbound_mail_transport.md](../architecture/analysis/outbound_mail_transport.md).
It lived here until 10 August 2026 and moved when this directory became the home of the normative family;
it is retained because a specification states what shall be true and does not record which alternatives
were examined.
