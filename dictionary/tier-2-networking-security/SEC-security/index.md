---
layout: default
title: "Security"
parent: "Technical Dictionary"
nav_order: 7
has_children: true
permalink: /security/
---

# Security

Application security (AppSec), web attack vectors (OWASP Top 10, XSS, CSRF, SQLi, SSRF, command injection), secrets management, security testing (SAST/DAST/pentest), secure SDLC, and DevSecOps. Authentication and authorization are in Identity & Access Management. Cryptographic algorithms are in Cryptography.

**Keywords:** SEC-001–SEC-143 (144 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| SEC-001 | Why Security Matters - The Adversarial Mindset | ★☆☆ |
| SEC-002 | The Security Threat Landscape - A Map | ★☆☆ |
| SEC-003 | How Attackers Think - Attack Surfaces and Vectors | ★☆☆ |
| SEC-004 | Defense in Depth - The Security Layering Principle | ★☆☆ |
| SEC-005 | The Security Ecosystem Map (AppSec NetSec CloudSec) | ★☆☆ |
| SEC-006 | Security Principles (OWASP, CWE, CVE) | ★☆☆ |
| SEC-007 | CIA Triad (Confidentiality, Integrity, Availability) | ★☆☆ |
| SEC-027 | Password and Credential Security Basics | ★☆☆ |
| SEC-028 | Principle of Least Privilege | ★☆☆ |
| SEC-029 | Secure Defaults | ★☆☆ |
| SEC-030 | OWASP Top 10 - Overview | ★☆☆ |
| SEC-008 | Security Misconfiguration | ★☆☆ |
| SEC-009 | Credentials and Secrets Management Basics | ★☆☆ |
| SEC-010 | Phishing | ★☆☆ |
| SEC-011 | Environment Variables for Secrets | ★☆☆ |
| SEC-012 | .env File Pattern | ★☆☆ |
| SEC-013 | Threat vs Vulnerability vs Risk | ★☆☆ |
| SEC-031 | Malware Overview | ★☆☆ |
| SEC-032 | Firewall (Conceptual) | ★☆☆ |
| SEC-033 | HTTPS Overview (Conceptual) | ★☆☆ |
| SEC-034 | Nonrepudiation | ★☆☆ |
| SEC-035 | Security vs Privacy | ★☆☆ |
| SEC-036 | Password Security Basics | ★☆☆ |
| SEC-037 | What is a Security Vulnerability | ★☆☆ |
| SEC-038 | Security Policy (Conceptual) | ★☆☆ |
| SEC-039 | Security Interview Preparation Guide | ★☆☆ |
| SEC-077 | Security Architecture Principles | ★★☆ |
| SEC-040 | Cryptography for Application Developers | ★★☆ |
| SEC-078 | Public Key Infrastructure (PKI) Basics | ★★☆ |
| SEC-041 | TLS and Secure Protocols for Developers | ★★☆ |
| SEC-042 | Cross-Site Scripting (XSS) | ★★☆ |
| SEC-043 | CSRF (Cross-Site Request Forgery) | ★★☆ |
| SEC-044 | SQL Injection | ★★☆ |
| SEC-045 | SSRF (Server-Side Request Forgery) | ★★☆ |
| SEC-046 | API Authentication Patterns | ★★☆ |
| SEC-047 | Input Validation and Output Encoding | ★★☆ |
| SEC-048 | Secure HTTP Headers (CSP, HSTS, X-Frame-Options) | ★★☆ |
| SEC-049 | CORS - Cross-Origin Security | ★★☆ |
| SEC-079 | Role-Based and Attribute-Based Access Control | ★★☆ |
| SEC-050 | API Key Security Patterns | ★★☆ |
| SEC-051 | Security Logging and Monitoring | ★★☆ |
| SEC-042 | Dependency and Supply Chain Security Basics | ★★☆ |
| SEC-053 | Secure Coding Practices | ★★☆ |
| SEC-054 | OWASP Top 10 - Deep Dive Per Vulnerability | ★★☆ |
| SEC-055 | Command Injection | ★★☆ |
| SEC-080 | Path Traversal | ★★☆ |
| SEC-056 | XXE Injection | ★★☆ |
| SEC-081 | Insecure Deserialization | ★★☆ |
| SEC-082 | Broken Access Control and IDOR | ★★☆ |
| SEC-083 | Secrets Management at Scale (Vault, AWS Secrets) | ★★☆ |
| SEC-084 | Zero Trust Security Model | ★★☆ |
| SEC-085 | Container Security | ★★☆ |
| SEC-086 | Threat Modeling (STRIDE, PASTA) | ★★☆ |
| SEC-087 | Penetration Testing Fundamentals | ★★☆ |
| SEC-088 | Security Audit and Code Review | ★★☆ |
| SEC-089 | Privilege Escalation Patterns | ★★☆ |
| SEC-090 | Vulnerable and Outdated Components | ★★☆ |
| SEC-091 | Brute-Force Attack | ★★☆ |
| SEC-092 | Man-in-the-Middle Attack | ★★☆ |
| SEC-093 | DDoS Attack | ★★☆ |
| SEC-094 | Social Engineering | ★★☆ |
| SEC-095 | Input Sanitization vs Escaping | ★★☆ |
| SEC-096 | Secrets Management | ★★☆ |
| SEC-097 | API Key Security | ★★☆ |
| SEC-098 | Rate Limiting for Security | ★★☆ |
| SEC-099 | Brute-Force Prevention | ★★☆ |
| SEC-100 | SAST (Static Application Security Testing) | ★★☆ |
| SEC-101 | CVE (Common Vulnerabilities and Exposures) | ★★☆ |
| SEC-102 | Dependency Scanning | ★★☆ |
| SEC-103 | CORS Security Implications | ★★☆ |
| SEC-104 | Insecure Direct Object Reference (IDOR) | ★★☆ |
| SEC-105 | Clickjacking | ★★☆ |
| SEC-057 | Open Redirect | ★★☆ |
| SEC-058 | Session Hijacking / Token Theft | ★★☆ |
| SEC-106 | OWASP API Security Top 10 | ★★☆ |
| SEC-107 | CIS Benchmarks (Security Hardening) | ★★☆ |
| SEC-108 | API Authorization Design Patterns | ★★★ |
| SEC-059 | Certificate Pinning and Trust Anchors | ★★★ |
| SEC-060 | Cryptographic Misuse and Common Errors | ★★★ |
| SEC-014 | Service-to-Service Security Patterns | ★★★ |
| SEC-061 | Supply Chain Attacks (SolarWinds, XZ Utils) | ★★★ |
| SEC-109 | Log4Shell - CVE-2021-44228 | ★★★ |
| SEC-110 | Heartbleed - CVE-2014-0160 | ★★★ |
| SEC-062 | Memory Safety Vulnerabilities and Exploitation | ★★★ |
| SEC-111 | Advanced Authentication Attack Patterns | ★★★ |
| SEC-112 | OAuth 2.0 Security Analysis | ★★★ |
| SEC-063 | Cryptographic Security Evaluation | ★★★ |
| SEC-015 | Lateral Movement Techniques | ★★★ |
| SEC-016 | Incident Response Playbook | ★★★ |
| SEC-113 | Security Hardening at Scale | ★★★ |
| SEC-064 | SSRF at Scale - Cloud Metadata Exploitation | ★★★ |
| SEC-065 | DDoS Attack Patterns and Defense | ★★★ |
| SEC-066 | Security Architecture Design Patterns | ★★★ |
| SEC-114 | DevSecOps Strategy and Pipeline Security | ★★★ |
| SEC-115 | Zero Trust Architecture Design | ★★★ |
| SEC-116 | Compliance-Driven Security (GDPR, SOC2, PCI-DSS) | ★★★ |
| SEC-097 | Cryptographic Primitive Design | ★★★ |
| SEC-118 | Security Protocol Formal Analysis | ★★★ |
| SEC-067 | Formal Verification of Security Properties | ★★★ |
| SEC-119 | SAST and DAST Pipeline Design and Automation | ★★★ |
| SEC-101 | Adversarial Thinking as Engineering Mindset | ★★★ |
| SEC-102 | Security Trade-off Framing | ★★★ |
| SEC-068 | Threat Modeling as First-Principles Tool | ★★★ |
| SEC-122 | OWASP A05 - Security Misconfiguration (Deep) | ★★★ |
| SEC-123 | Cryptographic Failures | ★★★ |
| SEC-124 | Credential Stuffing | ★★★ |
| SEC-107 | Timing Attack | ★★★ |
| SEC-125 | Replay Attack | ★★★ |
| SEC-126 | Supply Chain Attack | ★★★ |
| SEC-110 | Prompt Injection (AI Security) | ★★★ |
| SEC-127 | Content Security Policy (CSP) | ★★★ |
| SEC-128 | Security Headers (HSTS, X-Frame-Options) | ★★★ |
| SEC-017 | Vault (HashiCorp) | ★★★ |
| SEC-018 | Account Lockout Policy | ★★★ |
| SEC-019 | DDoS Protection | ★★★ |
| SEC-020 | WAF (Web Application Firewall) | ★★★ |
| SEC-021 | Penetration Testing | ★★★ |
| SEC-022 | Red Team / Blue Team | ★★★ |
| SEC-023 | DAST (Dynamic Application Security Testing) | ★★★ |
| SEC-024 | SCA (Software Composition Analysis) | ★★★ |
| SEC-025 | SBOM (Software Bill of Materials) | ★★★ |
| SEC-070 | CVSS Score | ★★★ |
| SEC-071 | Security Audit | ★★★ |
| SEC-072 | SIEM (Security Information and Event Management) | ★★★ |
| SEC-073 | Incident Response | ★★★ |
| SEC-074 | RASP (Runtime Application Self-Protection) | ★★★ |
| SEC-075 | Container Security Scanning | ★★★ |
| SEC-076 | Secret Scanning (in Git) | ★★★ |
| SEC-129 | mTLS (Mutual TLS) | ★★★ |
| SEC-130 | Memory Safety Vulnerabilities | ★★★ |
| SEC-131 | Side-Channel Attack (Deep) | ★★★ |
| SEC-132 | Container Security Hardening | ★★★ |
| SEC-133 | Network Segmentation Security | ★★★ |
| SEC-134 | Compliance-Driven Security (PCI-DSS, SOX, GDPR) | ★★★ |
| SEC-135 | OWASP LLM Top 10 | ★★★ |
| SEC-136 | Agent Permission Model | ★★★ |
| SEC-137 | Zero-Day Vulnerability | ★★★ |
| SEC-138 | Threat Intelligence (MITRE ATT&CK) | ★★★ |
| SEC-139 | Defense in Depth Architecture | ★★★ |
| SEC-140 | Security Architecture Review | ★★★ |
| SEC-141 | Digital Forensics (Basics) | ★★★ |
| SEC-142 | Exploit Development (Conceptual) | ★★★ |
| SEC-026 | OWASP Mobile Security Top 10 | ★★★ |
| SEC-143 | Security Architecture Decision Framework | ★★★ |
