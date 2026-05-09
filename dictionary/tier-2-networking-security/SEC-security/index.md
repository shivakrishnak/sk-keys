---
layout: default
title: "Security"
parent: "Technical Dictionary"
nav_order: 44
has_children: true
permalink: /security/
---

# Security

CIA triad, authentication & authorization, cryptography, common vulnerabilities (OWASP Top 10), attack types, defensive practices, security testing, and creator-level cryptography theory.

**Keywords:** SEC-001–SEC-156 (156 terms · 112 original + 44 gap-fill)

| ID      | Keyword                                                                    | Difficulty |
|---------|----------------------------------------------------------------------------|------------|
| SEC-001 | CIA Triad (Confidentiality, Integrity, Availability)                       | ★☆☆        |
| SEC-002 | Authentication vs Authorization                                            | ★☆☆        |
| SEC-003 | Identification, Authentication, Authorization, Accounting (IAAA)           | ★★☆        |
| SEC-004 | Principle of Least Privilege                                               | ★☆☆        |
| SEC-005 | Defense in Depth                                                           | ★★☆        |
| SEC-006 | Security by Design                                                         | ★★☆        |
| SEC-007 | Secure SDLC                                                                | ★★☆        |
| SEC-008 | Threat Modeling                                                            | ★★☆        |
| SEC-009 | STRIDE (Spoofing, Tampering, Repudiation, Info Disclosure, DoS, EoP)       | ★★★        |
| SEC-010 | Attack Surface                                                             | ★★☆        |
| SEC-011 | Zero Trust Security Model                                                  | ★★★        |
| SEC-012 | Security Misconfiguration                                                  | ★★☆        |
| SEC-013 | Session-Based Authentication                                               | ★★☆        |
| SEC-014 | Token-Based Authentication                                                 | ★★☆        |
| SEC-015 | Access Token                                                               | ★★☆        |
| SEC-016 | Refresh Token                                                              | ★★☆        |
| SEC-017 | HttpOnly Cookie                                                            | ★★☆        |
| SEC-018 | Secure Cookie Flag                                                         | ★★☆        |
| SEC-019 | SameSite Cookie                                                            | ★★★        |
| SEC-020 | JWT Anatomy (Header, Payload, Signature)                                   | ★★☆        |
| SEC-021 | JWT Verification Without DB Lookup                                         | ★★★        |
| SEC-022 | JWT Security Vulnerabilities                                               | ★★★        |
| SEC-023 | JWT Algorithm Confusion Attack                                             | ★★★        |
| SEC-024 | OAuth 2.0 Authorization Code Flow                                          | ★★★        |
| SEC-025 | OAuth 2.0 Client Credentials Flow                                          | ★★★        |
| SEC-026 | OAuth 2.0 PKCE                                                             | ★★★        |
| SEC-027 | OAuth 2.0 Implicit Flow (deprecated)                                       | ★★★        |
| SEC-028 | OpenID Connect (OIDC)                                                      | ★★★        |
| SEC-029 | SAML (Security Assertion Markup Language)                                  | ★★★        |
| SEC-030 | SSO (Single Sign-On)                                                       | ★★☆        |
| SEC-031 | MFA / 2FA                                                                  | ★★☆        |
| SEC-032 | TOTP (Time-Based One-Time Password)                                        | ★★★        |
| SEC-033 | Passkeys / WebAuthn                                                        | ★★★        |
| SEC-034 | RBAC (Role-Based Access Control)                                           | ★★☆        |
| SEC-035 | ABAC (Attribute-Based Access Control)                                      | ★★★        |
| SEC-036 | ACL (Access Control List)                                                  | ★★☆        |
| SEC-037 | Hashing (Bcrypt, Argon2, SHA-256)                                          | ★★☆        |
| SEC-038 | Encryption (AES, RSA)                                                      | ★★☆        |
| SEC-039 | Encoding (Base64)                                                          | ★☆☆        |
| SEC-040 | Hashing vs Encryption vs Encoding                                          | ★★☆        |
| SEC-041 | Symmetric vs Asymmetric Encryption                                         | ★★☆        |
| SEC-042 | Public Key / Private Key                                                   | ★★☆        |
| SEC-043 | PKI (Public Key Infrastructure)                                            | ★★★        |
| SEC-044 | Digital Signature                                                          | ★★★        |
| SEC-045 | Certificate Authority (CA)                                                 | ★★☆        |
| SEC-046 | TLS Certificate Lifecycle                                                  | ★★★        |
| SEC-047 | Certificate Pinning                                                        | ★★★        |
| SEC-048 | Key Management                                                             | ★★★        |
| SEC-049 | Hardware Security Module (HSM)                                             | ★★★        |
| SEC-050 | Key Rotation                                                               | ★★★        |
| SEC-051 | Envelope Encryption                                                        | ★★★        |
| SEC-052 | Password Storage Best Practices                                            | ★★☆        |
| SEC-053 | Salt (Cryptographic)                                                       | ★★☆        |
| SEC-054 | Rainbow Table Attack                                                       | ★★★        |
| SEC-055 | OWASP Top 10                                                               | ★★☆        |
| SEC-056 | XSS (Cross-Site Scripting)                                                 | ★★☆        |
| SEC-057 | Stored XSS                                                                 | ★★★        |
| SEC-058 | Reflected XSS                                                              | ★★★        |
| SEC-059 | DOM-Based XSS                                                              | ★★★        |
| SEC-060 | CSRF (Cross-Site Request Forgery)                                          | ★★☆        |
| SEC-061 | Anti-CSRF Token                                                            | ★★★        |
| SEC-062 | SQL Injection                                                              | ★★☆        |
| SEC-063 | Parameterized Queries                                                      | ★★☆        |
| SEC-064 | NoSQL Injection                                                            | ★★★        |
| SEC-065 | SSRF (Server-Side Request Forgery)                                         | ★★★        |
| SEC-066 | Command Injection                                                          | ★★★        |
| SEC-067 | Path Traversal                                                             | ★★★        |
| SEC-068 | XXE (XML External Entity)                                                  | ★★★        |
| SEC-069 | Insecure Deserialization                                                   | ★★★        |
| SEC-070 | Broken Access Control                                                      | ★★☆        |
| SEC-071 | OWASP A05 - Security Misconfiguration (Deep)                               | ★★★        |
| SEC-072 | Cryptographic Failures                                                     | ★★★        |
| SEC-073 | Vulnerable and Outdated Components                                         | ★★☆        |
| SEC-074 | Brute-Force Attack                                                         | ★★☆        |
| SEC-075 | Credential Stuffing                                                        | ★★★        |
| SEC-076 | Timing Attack                                                              | ★★★        |
| SEC-077 | Replay Attack                                                              | ★★★        |
| SEC-078 | Man-in-the-Middle Attack                                                   | ★★☆        |
| SEC-079 | DDoS Attack                                                                | ★★☆        |
| SEC-080 | Phishing                                                                   | ★☆☆        |
| SEC-081 | Social Engineering                                                         | ★★☆        |
| SEC-082 | Supply Chain Attack                                                        | ★★★        |
| SEC-083 | Prompt Injection (AI Security)                                             | ★★★        |
| SEC-084 | Input Sanitization vs Escaping                                             | ★★☆        |
| SEC-085 | Content Security Policy (CSP)                                              | ★★★        |
| SEC-086 | Security Headers (HSTS, X-Frame-Options)                                   | ★★★        |
| SEC-087 | Secrets Management                                                         | ★★☆        |
| SEC-088 | Environment Variables for Secrets                                          | ★☆☆        |
| SEC-089 | .env File Pattern                                                          | ★☆☆        |
| SEC-090 | Vault (HashiCorp)                                                          | ★★★        |
| SEC-091 | API Key Security                                                           | ★★☆        |
| SEC-092 | Rate Limiting for Security                                                 | ★★☆        |
| SEC-093 | Brute-Force Prevention                                                     | ★★☆        |
| SEC-094 | Account Lockout Policy                                                     | ★★★        |
| SEC-095 | DDoS Protection                                                            | ★★★        |
| SEC-096 | WAF (Web Application Firewall)                                             | ★★★        |
| SEC-097 | Penetration Testing                                                        | ★★★        |
| SEC-098 | Red Team / Blue Team                                                       | ★★★        |
| SEC-099 | SAST (Static Application Security Testing)                                 | ★★☆        |
| SEC-100 | DAST (Dynamic Application Security Testing)                                | ★★★        |
| SEC-101 | SCA (Software Composition Analysis)                                        | ★★★        |
| SEC-102 | SBOM (Software Bill of Materials)                                          | ★★★        |
| SEC-103 | CVE (Common Vulnerabilities and Exposures)                                 | ★★☆        |
| SEC-104 | CVSS Score                                                                 | ★★★        |
| SEC-105 | Security Audit                                                             | ★★★        |
| SEC-106 | SIEM (Security Information and Event Management)                           | ★★★        |
| SEC-107 | Security Logging and Monitoring                                            | ★★★        |
| SEC-108 | Incident Response                                                          | ★★★        |
| SEC-109 | RASP (Runtime Application Self-Protection)                                 | ★★★        |
| SEC-110 | Dependency Scanning                                                        | ★★☆        |
| SEC-111 | Container Security Scanning                                                | ★★★        |
| SEC-112 | Secret Scanning (in Git)                                                   | ★★★        |
| SEC-113 | Threat vs Vulnerability vs Risk                                            | ★☆☆        |
| SEC-114 | Malware Overview                                                           | ★☆☆        |
| SEC-115 | Firewall (Conceptual)                                                      | ★☆☆        |
| SEC-116 | HTTPS Overview (Conceptual)                                                | ★☆☆        |
| SEC-117 | Nonrepudiation                                                             | ★☆☆        |
| SEC-118 | Security vs Privacy                                                        | ★☆☆        |
| SEC-119 | Password Security Basics                                                   | ★☆☆        |
| SEC-120 | What is a Security Vulnerability                                           | ★☆☆        |
| SEC-121 | Security Policy (Conceptual)                                               | ★☆☆        |
| SEC-122 | CORS Security Implications                                                 | ★★☆        |
| SEC-123 | Insecure Direct Object Reference (IDOR)                                    | ★★☆        |
| SEC-124 | Clickjacking                                                               | ★★☆        |
| SEC-125 | Open Redirect                                                              | ★★☆        |
| SEC-126 | Session Hijacking / Token Theft                                            | ★★☆        |
| SEC-127 | OWASP API Security Top 10                                                  | ★★☆        |
| SEC-128 | CIS Benchmarks (Security Hardening)                                        | ★★☆        |
| SEC-129 | mTLS (Mutual TLS)                                                          | ★★★        |
| SEC-130 | Memory Safety Vulnerabilities                                              | ★★★        |
| SEC-131 | Side-Channel Attack (Deep)                                                 | ★★★        |
| SEC-132 | Container Security Hardening                                               | ★★★        |
| SEC-133 | Network Segmentation Security                                              | ★★★        |
| SEC-134 | Compliance-Driven Security (PCI-DSS, SOX, GDPR)                           | ★★★        |
| SEC-135 | OWASP LLM Top 10                                                           | ★★★        |
| SEC-136 | Agent Permission Model                                                     | ★★★        |
| SEC-137 | Zero-Day Vulnerability                                                     | ★★★        |
| SEC-138 | Threat Intelligence (MITRE ATT&CK)                                         | ★★★        |
| SEC-139 | Defense in Depth Architecture                                              | ★★★        |
| SEC-140 | Security Architecture Review                                               | ★★★        |
| SEC-141 | Digital Forensics (Basics)                                                 | ★★★        |
| SEC-142 | Exploit Development (Conceptual)                                           | ★★★        |
| SEC-143 | Cryptographic Primitive Design                                             | 🔬          |
| SEC-144 | Formal Security Proofs                                                     | 🔬          |
| SEC-145 | Provable Security (Reduction Theory)                                       | 🔬          |
| SEC-146 | Elliptic Curve Cryptography (Theory)                                       | 🔬          |
| SEC-147 | Post-Quantum Cryptography                                                  | 🔬          |
| SEC-148 | Secure Multiparty Computation                                              | 🔬          |
| SEC-149 | Zero-Knowledge Proofs                                                      | 🔬          |
| SEC-150 | Homomorphic Encryption                                                     | 🔬          |
| SEC-151 | TLS Protocol Design Rationale                                              | 🔬          |
| SEC-152 | OAuth 2.0 Specification Design Rationale                                   | 🔬          |
| SEC-153 | Capability-Based Security Model                                            | 🔬          |
| SEC-154 | Security Protocol Verification (BAN Logic)                                 | 🔬          |
| SEC-155 | Threat Modeling Formal Methods                                             | 🔬          |
| SEC-156 | Applied Cryptography Research                                              | 🔬          |
