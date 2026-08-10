# AdvisorX Engineering Specification
# Prompt Storage and Management

**Status:** Proposed  
**Persistence:** Amazon DynamoDB  
**DynamoDB tables:** System

---

## 1. Purpose

This specification defines a prompt storage and management system for an application with a **single DynamoDB table**.

---

# 2. Design Goals

The prompt architecture shall provide:

1. Upload and versioning the prepared YAML prompt definition
2. Provide the prompt, its id and its version by request
3. Marked as removed prompts won't be used in the new interviews

---

# 3. Non-Goals

The system does not provide:

- removal of the uploaded prompts, prompts marked as removed, but do not delete

---

# 4. Typical Requests

* get prompt "id", in "ACTIVE" state, the last revision (version)

---

# 5. System DynamoDB Table

The entity primary key is defined by `PROMPT` (see [DynamoDB System Table](SPEC_data_system.md))

Example:

```text
PK                         SK
────────────────────────   ─────────────────────

```

---

# 6. Access

See [Role Model](role_model.md)