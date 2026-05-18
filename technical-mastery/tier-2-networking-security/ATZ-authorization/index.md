---
layout: default
title: "Authorization"
parent: "Technical Mastery"
nav_order: 78
has_children: true
permalink: /technical-mastery/authorization/
---

# Authorization

The complete authorization engineering reference: RBAC and role
inheritance, ABAC, PBAC, Policy-Based Access Control, Open Policy
Agent (OPA), Cedar, Rego, Google Zanzibar (ReBAC), SpiceDB,
OpenFGA, access control lists, capability-based security, delegated
authorization, privilege escalation attacks, IDOR, broken access
control (OWASP Top 1), externalized authorization, multi-tenant
authorization design, distributed policy enforcement, policy-as-code
in CI/CD, formal access control theory (Bell-LaPadula, Biba, RBAC
theory), and enterprise authorization platform design - from first
principles to production-grade policy systems.

> **Scope note:** This category covers authorization models and
> enforcement mechanisms in depth - how permissions are defined and
> enforced. For identity management and governance, see
> [Identity & Access Management](../IAM-iam-access/). For
> authentication mechanisms (how identity is proved), see
> [Authentication](../ATH-authentication/). For the OAuth 2.0
> protocol and OIDC spec details, see
> [OAuth 2.0 & OpenID Connect](../OAU-oauth/).

**Keywords:** ATZ-001-ATZ-062 (62 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| ATZ-001 | The Authorization Problem | 🌱 |
| ATZ-002 | Why Authorization Is Hard to Get Right | 🌱 |
| ATZ-003 | Authorization vs Access Control - Terminology | 🌱 |
| ATZ-004 | The Principle of Least Privilege | 🌱 |
| ATZ-005 | What Break-Glass Access Means | 🌱 |
| ATZ-006 | Role-Based Access Control (RBAC) | ★☆☆ |
| ATZ-007 | Permissions and Policies | ★☆☆ |
| ATZ-008 | Allow vs Deny Semantics | ★☆☆ |
| ATZ-009 | Resource-Based vs Identity-Based Policies | ★☆☆ |
| ATZ-010 | Access Control Lists (ACL) | ★☆☆ |
| ATZ-011 | Superuser and Admin Privilege | ★☆☆ |
| ATZ-012 | Group-Based Access Management | ★☆☆ |
| ATZ-013 | RBAC Implementation Patterns | ★★☆ |
| ATZ-014 | Hierarchical RBAC and Role Inheritance | ★★☆ |
| ATZ-015 | Attribute-Based Access Control (ABAC) | ★★☆ |
| ATZ-016 | Claims-Based Authorization | ★★☆ |
| ATZ-017 | OAuth Scopes as Authorization | ★★☆ |
| ATZ-018 | JWT Claims for Authorization | ★★☆ |
| ATZ-019 | Row-Level Security (Database Authorization) | ★★☆ |
| ATZ-020 | API Gateway Authorization | ★★☆ |
| ATZ-021 | Permission Inheritance and Propagation | ★★☆ |
| ATZ-022 | Delegated Authorization Patterns | ★★☆ |
| ATZ-023 | Service Account Permissions | ★★☆ |
| ATZ-024 | Wildcard Permissions and Risks | ★★☆ |
| ATZ-025 | Authorization Testing Strategies | ★★☆ |
| ATZ-026 | Policy-Based Access Control (PBAC) | ★★☆ |
| ATZ-027 | Open Policy Agent (OPA) | ★★☆ |
| ATZ-028 | Cedar Policy Language | ★★☆ |
| ATZ-029 | Rego Policy Language (OPA) | ★★☆ |
| ATZ-030 | Externalized Authorization | ★★☆ |
| ATZ-031 | Authorization Decision Logging and Auditing | ★★☆ |
| ATZ-032 | Permission Caching Strategies | ★★☆ |
| ATZ-033 | Cross-Service Authorization | ★★☆ |
| ATZ-034 | Capability-Based Security | ★★☆ |
| ATZ-035 | Dynamic Authorization Policies | ★★☆ |
| ATZ-036 | Relationship-Based Access Control (ReBAC) | ★★★ |
| ATZ-037 | Google Zanzibar - Global Authorization System | ★★★ |
| ATZ-038 | SpiceDB and OpenFGA (Zanzibar Implementations) | ★★★ |
| ATZ-039 | Policy Evaluation Algorithms and Performance | ★★★ |
| ATZ-040 | Distributed Authorization Architecture | ★★★ |
| ATZ-041 | Privilege Escalation Attacks | ★★★ |
| ATZ-042 | Broken Access Control (OWASP #1) | ★★★ |
| ATZ-043 | Insecure Direct Object Reference (IDOR) | ★★★ |
| ATZ-044 | Forced Browsing and Missing Function Level Access | ★★★ |
| ATZ-045 | Authorization in Event-Driven Systems | ★★★ |
| ATZ-046 | Authorization Performance at Scale | ★★★ |
| ATZ-047 | Formal Access Control Models (Bell-LaPadula, Biba) | ★★★ |
| ATZ-048 | Multi-Tenant Authorization Design | ★★★ |
| ATZ-049 | Zero Trust Authorization Patterns | ★★★ |
| ATZ-050 | Authorization for Microservices Fleet | ★★★ |
| ATZ-051 | Enterprise Authorization Architecture | ★★★ |
| ATZ-052 | Central Policy Store vs Distributed Enforcement | ★★★ |
| ATZ-053 | Authorization Migration Strategy | ★★★ |
| ATZ-054 | Policy-as-Code in CI/CD | ★★★ |
| ATZ-055 | Authorization Observability and Policy Tracing | ★★★ |
| ATZ-056 | Zanzibar Paper (2019) Design Rationale | ★★★ |
| ATZ-057 | Formal RBAC Theory (Sandhu 1996) | ★★★ |
| ATZ-058 | Policy Language Design Trade-offs | ★★★ |
| ATZ-059 | Authorization Research Frontiers | ★★★ |
| ATZ-060 | ABAC and XACML Specification Analysis | ★★★ |
| ATZ-061 | Authorization as Explicit Trust Assertion | ★★★ |
| ATZ-062 | Policy as Code Across Domains (Pattern Bridge) | ★★★ |
