# Architecture Analysis Index

**Updated:** 10 August 2026

Analyses, decision records and investigations that sit behind the design — the reasoning, the options
ruled out, and the organizational dependencies that remain.

**Nothing in this directory is normative.** Each document records *why* a choice was made and what was
considered; the requirements that resulted are stated in the specifications under
[docs/specs/](../../specs/INDEX.md), and where an analysis and a specification disagree the
specification governs. A document that becomes normative does not stay here.

**Why keep them.** A specification states what shall be true. It does not state which alternatives were
examined, which vendor constraint closed one off, or which question is still waiting on someone outside
the team. That reasoning is what makes a decision reviewable a year later, and it is the first thing lost
when a decision record is deleted once its requirements land.

**Phase** — the delivery stage the content targets: `R&D`, `MVP`, `PROD`.
**Status** — `ACTIVE` (the reasoning still holds) or `ARCHIVE` (superseded; kept for the record).

---

## Documents

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-08-05 | [outbound_mail_transport.md](outbound_mail_transport.md) | **Decision record — not normative.** Why the transport is **Amazon SES** behind a provider-agnostic interface, and why each alternative was ruled out: Exchange Direct Send rejects external recipients and every invitee is external; High Volume Email lost external sending in June 2025; SMTP relay via inbound connector needs a static unshared source IP, which means NAT plus an EIP plus a port-25 exception to send ~300 messages a month; SMTP AUTH converges on the same app registration as Graph with more code; a third-party ESP fails on procurement rather than capability. The deciding argument is delivery reporting — Microsoft Graph `sendMail` returns `202 Accepted` and nothing further and cannot report a complaint at all, so it cannot distinguish a failed delivery from an unopened message, which is the one thing an issuer needs. Graph is retained as a driver swap, on nobody's critical path. Also carries the SES sandbox and mailbox-simulator development path, the DNS and DXC IT critical path, eleven questions for Exchange and email security, nine claims needing confirmation, and six tradeoffs deliberately left open. §3 records the three things that changed when its design was restated as requirements; §4 is the amendment register against the Phase 1 documents, seven of eight applied. **Moved from `docs/specs/` on 10 Aug 2026.** | MVP | ACTIVE |

---

## Relationship to the rest of `docs/`

| Directory | Holds | Normative |
|---|---|---|
| [specs/](../../specs/INDEX.md) | The `SPEC_*` family — what shall be true | **Yes** |
| `architecture/` | Target-state design and gap analyses | Draft specifications, in part |
| `architecture/analysis/` | This directory — reasoning and decision records | No |

**Superseded reading.** The Phase 1 documents in the parent directory — `authorization_model_phase1.md`
and `data_architecture_phase1.md` — cite this document at its former path,
`../specs/outbound_mail_transport.md`. Those citations are stale as paths and correct as references. Both
documents are retained as a historical record of the Phase 1 design and are not being revised, so the
paths are left as written rather than rewritten in documents that are no longer maintained.
