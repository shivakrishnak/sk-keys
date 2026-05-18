---
layout: default
title: "OAuth 2.0 & OpenID Connect"
parent: "Technical Mastery"
nav_order: 76
has_children: true
permalink: /technical-mastery/oauth/
---

# OAuth 2.0 & OpenID Connect

The OAuth 2.0 protocol suite and OpenID Connect (OIDC): delegation
model, authorization flows (Authorization Code, Client Credentials,
Device, Implicit), PKCE, refresh token lifecycle, token introspection,
security attacks (Mix-Up, CSRF, token leakage, authorization code
injection), DPoP, PAR, Rich Authorization Requests (RAR), FAPI
compliance, enterprise OAuth patterns, and specification design
rationale - from the delegation problem through to production-grade
OAuth platform design.

> **Scope note:** This category covers the OAuth 2.0 protocol and
> OIDC specification in depth. For authentication mechanisms
> (password hashing, MFA, FIDO2), see
> [Authentication](../ATH-authentication/). For authorization models
> (RBAC, OPA, Zanzibar), see [Authorization](../ATZ-authorization/).
> For identity management and enterprise IAM, see
> [Identity & Access Management](../IAM-iam-access/).

**Keywords:** OAU-001-OAU-070 (70 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| OAU-001 | The Delegation Problem - Why OAuth Exists | 🌱 |
| OAU-002 | OAuth vs Authentication (What OAuth Is NOT) | 🌱 |
| OAU-003 | The API Authorization Landscape | 🌱 |
| OAU-004 | OAuth 1.0 Pain and Why 2.0 Was Needed | 🌱 |
| OAU-005 | Where You Have Already Used OAuth | 🌱 |
| OAU-006 | The Four Actors in Every OAuth Dance | 🌱 |
| OAU-007 | OAuth 2.0 Roles | ★☆☆ |
| OAU-008 | Access Token | ★☆☆ |
| OAU-009 | Authorization Code Flow | ★★☆ |
| OAU-010 | Client Credentials Flow | ★★☆ |
| OAU-011 | Scope | ★☆☆ |
| OAU-012 | Redirect URI | ★☆☆ |
| OAU-013 | Client ID and Client Secret | ★☆☆ |
| OAU-014 | State Parameter | ★☆☆ |
| OAU-015 | Bearer Token | ★☆☆ |
| OAU-016 | Token Response Structure | ★☆☆ |
| OAU-017 | OAuth 2.0 Endpoints | ★☆☆ |
| OAU-018 | Grant Types Overview | ★☆☆ |
| OAU-019 | Consent Screen | ★☆☆ |
| OAU-020 | Refresh Token | ★☆☆ |
| OAU-021 | Public vs Confidential Clients | ★☆☆ |
| OAU-022 | PKCE (Proof Key for Code Exchange) | ★★☆ |
| OAU-023 | Token Validation | ★★☆ |
| OAU-024 | Token Introspection (RFC 7662) | ★★☆ |
| OAU-025 | Token Revocation (RFC 7009) | ★★☆ |
| OAU-026 | Refresh Token Lifecycle | ★★☆ |
| OAU-027 | OAuth Error Responses | ★★☆ |
| OAU-028 | OAuth 2.0 with Spring Security | ★★☆ |
| OAU-029 | Device Authorization Flow (RFC 8628) | ★★☆ |
| OAU-030 | Dynamic Client Registration (RFC 7591) | ★★☆ |
| OAU-031 | Multi-Tenant OAuth Configuration | ★★☆ |
| OAU-032 | OAuth Scopes in Practice | ★★☆ |
| OAU-033 | Implicit Flow and Why It Was Deprecated | ★★☆ |
| OAU-034 | Resource Owner Password Credentials Flow | ★★☆ |
| OAU-035 | JWT Access Tokens (RFC 9068) | ★★☆ |
| OAU-036 | OAuth 2.0 Threat Model (RFC 6819) | ★★☆ |
| OAU-037 | Authorization Code Interception Attack | ★★☆ |
| OAU-038 | CSRF in OAuth and State Parameter Validation | ★★☆ |
| OAU-039 | Open Redirect via Redirect URI Hijacking | ★★☆ |
| OAU-040 | Token Leakage via Referrer Header | ★★☆ |
| OAU-041 | Proof of Possession Tokens - DPoP (RFC 9449) | ★★☆ |
| OAU-042 | OAuth 2.0 Token Exchange (RFC 8693) | ★★☆ |
| OAU-043 | Pushed Authorization Requests - PAR (RFC 9126) | ★★☆ |
| OAU-044 | mTLS Client Authentication for OAuth (RFC 8705) | ★★☆ |
| OAU-045 | Refresh Token Rotation Security | ★★☆ |
| OAU-046 | OAuth 2.0 Rich Authorization Requests (RFC 9396) | ★★☆ |
| OAU-047 | Token Audience Validation and Binding | ★★☆ |
| OAU-048 | Authorization Server Architecture | ★★★ |
| OAU-049 | JWKS and Public Key Discovery | ★★★ |
| OAU-050 | Authorization Server Metadata Discovery (RFC 8414) | ★★★ |
| OAU-051 | OAuth 2.0 Mix-Up Attack | ★★★ |
| OAU-052 | SSRF via OAuth Redirect URI Manipulation | ★★★ |
| OAU-053 | Token Substitution Attack | ★★★ |
| OAU-054 | OAuth 2.0 in Financial Services (FAPI) | ★★★ |
| OAU-055 | OAuth Production Debugging and Observability | ★★★ |
| OAU-056 | OAuth 2.0 in Zero Trust Architecture | ★★★ |
| OAU-057 | Authorization Server Clustering and High Availability | ★★★ |
| OAU-058 | Enterprise OAuth 2.0 Architecture Patterns | ★★★ |
| OAU-059 | Authorization Server Selection Framework | ★★★ |
| OAU-060 | OAuth 2.0 Migration Strategy | ★★★ |
| OAU-061 | Centralized vs Decentralized Authorization Design | ★★★ |
| OAU-062 | Cross-Organization OAuth Federation | ★★★ |
| OAU-063 | OAuth 2.0 for Internal Developer Platforms | ★★★ |
| OAU-064 | OAuth 2.0 RFC 6749 Design Rationale | ★★★ |
| OAU-065 | OAuth 2.1 Consolidation and Simplification | ★★★ |
| OAU-066 | GNAP (Grant Negotiation and Authorization Protocol) | ★★★ |
| OAU-067 | Formal Security Analysis of OAuth 2.0 | ★★★ |
| OAU-068 | Delegated Authorization as a Universal Pattern | ★★★ |
| OAU-069 | Trust Boundary Thinking in Authorization Design | ★★★ |
| OAU-070 | Specification-Driven Security Engineering | ★★★ |
