# AdvisorX Engineering Specification
# E-mail Template Storage and Management

**Status:** Proposed  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** System

---

## 1. Purpose

This specification defines a e-mail template management for an application with a **markdown-based e-mail templates**.

This information is stored directly in the **System DynamoDB table**, which is the application system of record.

The system does not store:

- HTML-based templates;

---

# 2. Design Goals

The e-mail template architecture shall provide:

1. Upload and versioning the prepared markdown template
2. Generating HTML5 content based on markdown-syntax

---

# 3. Non-Goals

The system does not provide:

- edit or modification of the markdown templates

---

# 4. Typical Requests

* get template "id", in "ACTIVE" state, the last revision (version)

---

# 5. System DynamoDB Table

The entity primary key is defined by `TEMPLATE` (see [DynamoDB System Table](SPEC_data_system.md))

Example:

```text
PK                         SK
────────────────────────   ─────────────────────
TBD
```
---

# 6. Access

See [Role Model](role_model.md)