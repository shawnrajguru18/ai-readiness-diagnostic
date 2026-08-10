# AdvisorX Engineering Specification
# Interview Storage and Management

**Status:** Proposed  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** Business

---

## 1. Purpose

This specification defines a interviews and related scorecard storage and management system for an application with a **single DynamoDB table**.

---

# 2. Design Goals

The consent architecture shall provide:

1. Upload and versioning the prepared markdown consent definition
2. Provide the consent, its id and its version by request
3. Mark the selected consent as 

---

# 3. Non-Goals

The system does not provide:

- removal of the uploaded consents, prompts marked as removed, but do not delete

---

# 4. Business DynamoDB Table

The entity primary key is defined by `CONSENT` (see [DynamoDB System Table](SPEC_data_system.md))

Example:

```text
PK                         SK
────────────────────────   ─────────────────────

```

# 5. Access

See [Role Model](role_model.md)