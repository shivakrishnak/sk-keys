---
id: ATZ-058
title: "Policy Language Design Trade-offs"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-026, ATZ-027, ATZ-028, ATZ-029, ATZ-056
used_by: ATZ-059, ATZ-060
related: ATZ-027, ATZ-029, ATZ-059
tags:
  - security
  - authorization
  - policy-language
  - design
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/authorization/policy-language-design-trade-offs/
---

Policy language design sits at the intersection of security,
usability, and formal correctness. Every policy language makes
trade-offs among these dimensions.

**TL;DR:** Authorization policy languages trade expressiveness
for safety. Rego (OPA): general-purpose, Turing-complete,
expressive but complex - requires expertise. Cedar (AWS): purpose-
built, decidable (always terminates, formally verifiable), simpler
but less expressive. XACML: XML-based, powerful, verbose and
notoriously hard to read. The right choice depends on who writes
policies, how complex the access control logic is, and whether
formal correctness guarantees are needed.

---

### Textbook Definition

A policy language is a formal notation for expressing access
control rules. Design dimensions: expressiveness (what access
patterns can be expressed?), decidability (is evaluation
guaranteed to terminate?), safety (can policies accidentally
grant more than intended?), toolability (IDE support,
linting, testing), performance (evaluation speed), human
readability (can non-developers write policies?), and
separation of concerns (policy vs. data vs. application code).

---

### Comparison

| Property | Rego (OPA) | Cedar | XACML |
|---|---|---|---|
| Paradigm | Datalog-based | Structured | XML-based |
| Decidable? | No (Turing-complete) | Yes | No |
| Expressiveness | Very high | High | Very high |
| Readability | Medium | High | Low (XML verbosity) |
| Formal verify? | No | Yes (SMT solver) | No |
| Learning curve | Steep | Moderate | Steep |
| Performance | Good (indexing) | Excellent | Variable |
| Best for | Complex logic | Safety-critical | Legacy enterprise |

---

### Code Examples

**Rego (OPA) - general purpose, complex logic:**

```rego
# Rego: full Turing-complete policy
# Can express complex conditions but harder to verify
package authz

allow {
    some i
    input.user.roles[i] == "admin"
}

allow {
    input.resource.owner == input.user.id
    input.action in ["read", "update"]
    not data.denied_users[input.user.id]
}
```

**Cedar - decidable, formally verifiable:**

```cedar
// Cedar: purpose-built, always terminates
// AWS Verified Permissions uses Cedar
permit (
    principal in Group::"finance",
    action in [Action::"read", Action::"export"],
    resource in ResourceType::"Report"
)
when {
    resource.classification == "internal"
};

// Cedar policy can be formally analyzed:
// "Can any policy allow user X to delete admin resources?"
// SMT solver checks: guaranteed to find answer or prove none
```

---

*Authorization category: ATZ | Entry: ATZ-058 | v5.0*