---
layout: default
title: "Authentication"
parent: "Technical Mastery"
nav_order: 77
has_children: true
permalink: /technical-mastery/authentication/
---

# Authentication

The complete authentication engineering reference: password hashing
(bcrypt, Argon2), session mechanics, cookie security, MFA (TOTP,
push, hardware keys), FIDO2/WebAuthn/passkeys, SAML and OIDC login
flows, JWT validation, mTLS, Kerberos, SSH keys, brute-force defense,
session fixation, credential stuffing, account takeover prevention,
authentication at distributed scale, and specification design
rationale - from first principles to enterprise authentication
platform architecture.

> **Scope note:** This category covers HOW identity is proved
> (authentication mechanisms). For identity management, provisioning,
> and governance, see
> [Identity & Access Management](../IAM-iam-access/). For
> authorization models and policy engines, see
> [Authorization](../ATZ-authorization/). For the OAuth 2.0 protocol
> and OIDC spec details, see
> [OAuth 2.0 & OpenID Connect](../OAU-oauth/).

**Keywords:** ATH-001-ATH-065 (65 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| ATH-001 | The Authentication Problem | 🌱 |
| ATH-002 | What Authentication Actually Proves | 🌱 |
| ATH-003 | The Three Authentication Factors | 🌱 |
| ATH-004 | Authentication vs Authorization - The Boundary | 🌱 |
| ATH-005 | How Attackers Attack Authentication | 🌱 |
| ATH-006 | Username and Password Authentication | ★☆☆ |
| ATH-007 | Password Hashing (bcrypt, Argon2, scrypt) | ★☆☆ |
| ATH-008 | Session-Based Authentication | ★☆☆ |
| ATH-009 | Cookie Mechanics and Security Attributes | ★☆☆ |
| ATH-010 | Token-Based Authentication Overview | ★☆☆ |
| ATH-011 | HTTP Basic Authentication | ★☆☆ |
| ATH-012 | Multi-Factor Authentication (MFA) Basics | ★☆☆ |
| ATH-013 | TOTP (Time-Based One-Time Password) | ★☆☆ |
| ATH-014 | Remember Me and Persistent Sessions | ★☆☆ |
| ATH-015 | Logout and Session Invalidation | ★☆☆ |
| ATH-016 | Authentication Error Messages (Not Leaking Clues) | ★☆☆ |
| ATH-017 | Brute Force and Rate Limiting | ★★☆ |
| ATH-018 | Account Lockout Policy | ★★☆ |
| ATH-019 | Password Policy Design | ★★☆ |
| ATH-020 | Secure Password Reset Flow | ★★☆ |
| ATH-021 | Account Enumeration Prevention | ★★☆ |
| ATH-022 | OIDC Login Flow (Authentication via OAuth) | ★★☆ |
| ATH-023 | JWT Validation in Authentication | ★★☆ |
| ATH-024 | SAML 2.0 Authentication Flow | ★★☆ |
| ATH-025 | Social Login Implementation | ★★☆ |
| ATH-026 | Email Magic Link Authentication | ★★☆ |
| ATH-027 | SMS OTP Authentication | ★★☆ |
| ATH-028 | Hardware Security Keys (FIDO U2F) | ★★☆ |
| ATH-029 | Authenticator Apps (TOTP vs Push) | ★★☆ |
| ATH-030 | API Key Authentication Mechanics | ★★☆ |
| ATH-031 | Bearer Token Authentication | ★★☆ |
| ATH-032 | Refresh Token Patterns in Authentication | ★★☆ |
| ATH-033 | PKCE for Mobile and SPA Authentication | ★★☆ |
| ATH-034 | Session Fixation Attack | ★★☆ |
| ATH-035 | Credential Stuffing Defense | ★★☆ |
| ATH-036 | Phishing-Resistant MFA | ★★☆ |
| ATH-037 | FIDO2 and WebAuthn | ★★☆ |
| ATH-038 | Passkeys (Discoverable FIDO2 Credentials) | ★★☆ |
| ATH-039 | mTLS (Mutual TLS) Authentication | ★★☆ |
| ATH-040 | Certificate-Based Authentication | ★★☆ |
| ATH-041 | Kerberos Protocol | ★★☆ |
| ATH-042 | LDAP Authentication | ★★☆ |
| ATH-043 | SSH Key Authentication | ★★☆ |
| ATH-044 | Account Takeover Prevention | ★★★ |
| ATH-045 | JWT Signature Algorithm Security (RS256 vs HS256) | ★★★ |
| ATH-046 | Token Theft and Session Hijacking | ★★★ |
| ATH-047 | Authentication in Distributed Systems | ★★★ |
| ATH-048 | Service Identity and Workload Authentication | ★★★ |
| ATH-049 | mTLS in Service Mesh (Istio, Linkerd) | ★★★ |
| ATH-050 | Risk-Based and Adaptive Authentication | ★★★ |
| ATH-051 | Continuous Authentication | ★★★ |
| ATH-052 | Authentication Observability and Anomaly Detection | ★★★ |
| ATH-053 | Authentication Server Architecture | ★★★ |
| ATH-054 | Distributed Session Management | ★★★ |
| ATH-055 | Credential Manager and Secret Rotation | ★★★ |
| ATH-056 | Enterprise Authentication Architecture | ★★★ |
| ATH-057 | Identity Provider (IdP) Design | ★★★ |
| ATH-058 | Authentication Strategy for Multi-Cloud | ★★★ |
| ATH-059 | Federated Authentication Architecture | ★★★ |
| ATH-060 | Authentication Migration Strategy | ★★★ |
| ATH-061 | WebAuthn Specification Internals | ★★★ |
| ATH-062 | FIDO Alliance Protocol Design Rationale | ★★★ |
| ATH-063 | Formal Authentication Protocol Analysis | ★★★ |
| ATH-064 | Post-Quantum Authentication | ★★★ |
| ATH-065 | Authentication as Trust Chain Design (Pattern Bridge) | ★★★ |

**Keywords:** ATH-001-ATH-065 (65 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| ATH-001 | The Authentication Problem | 🌱 |
| ATH-002 | What Authentication Actually Proves | 🌱 |
| ATH-003 | The Three Authentication Factors | 🌱 |
| ATH-004 | Authentication vs Authorization - The Boundary | 🌱 |
| ATH-005 | How Attackers Attack Authentication | 🌱 |
| ATH-006 | Username and Password Authentication | ★☆☆ |
| ATH-007 | Password Hashing (bcrypt, Argon2, scrypt) | ★☆☆ |
| ATH-008 | Session-Based Authentication | ★☆☆ |
| ATH-009 | Cookie Mechanics and Security Attributes | ★☆☆ |
| ATH-010 | Token-Based Authentication Overview | ★☆☆ |
| ATH-011 | HTTP Basic Authentication | ★☆☆ |
| ATH-012 | Multi-Factor Authentication (MFA) Basics | ★☆☆ |
| ATH-013 | TOTP (Time-Based One-Time Password) | ★☆☆ |
| ATH-014 | Remember Me and Persistent Sessions | ★☆☆ |
| ATH-015 | Logout and Session Invalidation | ★☆☆ |
| ATH-016 | Authentication Error Messages (Not Leaking Clues) | ★☆☆ |
| ATH-017 | Brute Force and Rate Limiting | ★★☆ |
| ATH-018 | Account Lockout Policy | ★★☆ |
| ATH-019 | Password Policy Design | ★★☆ |
| ATH-020 | Secure Password Reset Flow | ★★☆ |
| ATH-021 | Account Enumeration Prevention | ★★☆ |
| ATH-022 | OIDC Login Flow (Authentication via OAuth) | ★★☆ |
| ATH-023 | JWT Validation in Authentication | ★★☆ |
| ATH-024 | SAML 2.0 Authentication Flow | ★★☆ |
| ATH-025 | Social Login Implementation | ★★☆ |
| ATH-026 | Email Magic Link Authentication | ★★☆ |
| ATH-027 | SMS OTP Authentication | ★★☆ |
| ATH-028 | Hardware Security Keys (FIDO U2F) | ★★☆ |
| ATH-029 | Authenticator Apps (TOTP vs Push) | ★★☆ |
| ATH-030 | API Key Authentication Mechanics | ★★☆ |
| ATH-031 | Bearer Token Authentication | ★★☆ |
| ATH-032 | Refresh Token Patterns in Authentication | ★★☆ |
| ATH-033 | PKCE for Mobile and SPA Authentication | ★★☆ |
| ATH-034 | Session Fixation Attack | ★★☆ |
| ATH-035 | Credential Stuffing Defense | ★★☆ |
| ATH-036 | Phishing-Resistant MFA | ★★☆ |
| ATH-037 | FIDO2 and WebAuthn | ★★☆ |
| ATH-038 | Passkeys (Discoverable FIDO2 Credentials) | ★★☆ |
| ATH-039 | mTLS (Mutual TLS) Authentication | ★★☆ |
| ATH-040 | Certificate-Based Authentication | ★★☆ |
| ATH-041 | Kerberos Protocol | ★★☆ |
| ATH-042 | LDAP Authentication | ★★☆ |
| ATH-043 | SSH Key Authentication | ★★☆ |
| ATH-044 | Account Takeover Prevention | ★★★ |
| ATH-045 | JWT Signature Algorithm Security (RS256 vs HS256) | ★★★ |
| ATH-046 | Token Theft and Session Hijacking | ★★★ |
| ATH-047 | Authentication in Distributed Systems | ★★★ |
| ATH-048 | Service Identity and Workload Authentication | ★★★ |
| ATH-049 | mTLS in Service Mesh (Istio, Linkerd) | ★★★ |
| ATH-050 | Risk-Based and Adaptive Authentication | ★★★ |
| ATH-051 | Continuous Authentication | ★★★ |
| ATH-052 | Authentication Observability and Anomaly Detection | ★★★ |
| ATH-053 | Authentication Server Architecture | ★★★ |
| ATH-054 | Distributed Session Management | ★★★ |
| ATH-055 | Credential Manager and Secret Rotation | ★★★ |
| ATH-056 | Enterprise Authentication Architecture | ★★★ |
| ATH-057 | Identity Provider (IdP) Design | ★★★ |
| ATH-058 | Authentication Strategy for Multi-Cloud | ★★★ |
| ATH-059 | Federated Authentication Architecture | ★★★ |
| ATH-060 | Authentication Migration Strategy | ★★★ |
| ATH-061 | WebAuthn Specification Internals | ★★★ |
| ATH-062 | FIDO Alliance Protocol Design Rationale | ★★★ |
| ATH-063 | Formal Authentication Protocol Analysis | ★★★ |
| ATH-064 | Post-Quantum Authentication | ★★★ |
| ATH-065 | Authentication as Trust Chain Design (Pattern Bridge) | ★★★ |
