---
layout: default
title: "Security"
nav_order: 7
parent: "Technical Mastery"
has_children: true
permalink: /technical-mastery/sec/
---

# Security

Application security, web vulnerabilities, secure coding, authentication
protocols, threat modeling, cryptographic application, incident response,
and enterprise security architecture - from first principles to
production-grade security engineering.

---

## Keywords

| ID       | Keyword                                                            | Level | Difficulty | Tags                                      |
| :------- | :----------------------------------------------------------------- | :---- | :--------- | :---------------------------------------- |
| SEC-001  | The Security Problem in Software Engineering                       | L0    | 🌱          | orientation, mindset                      |
| SEC-002  | CIA Triad (Confidentiality, Integrity, Availability)               | L0    | 🌱          | orientation, fundamentals                 |
| SEC-003  | What Attackers Actually Do (Threat Actor Mindset)                  | L0    | 🌱          | orientation, adversarial                  |
| SEC-004  | OWASP Top 10 Overview                                              | L0    | 🌱          | orientation, owasp                        |
| SEC-005  | Cost of a Security Breach                                          | L0    | 🌱          | orientation, business                     |
| SEC-006  | Why Security is Every Developer's Responsibility                   | L0    | 🌱          | orientation, culture                      |
| SEC-007  | Defense in Depth                                                   | L0    | 🌱          | orientation, strategy                     |
| SEC-008  | Authentication vs Authorization vs Auditing                        | L1    | ★☆☆         | authn, authz, fundamentals               |
| SEC-009  | Password Storage Anti-Pattern ⚠️ anti-critical                    | L1    | ★☆☆         | passwords, anti-pattern                   |
| SEC-010  | Hashing vs Encryption vs Encoding                                  | L1    | ★☆☆         | cryptography, fundamentals               |
| SEC-011  | SQL Injection                                                      | L1    | ★☆☆         | injection, owasp                          |
| SEC-012  | Cross-Site Scripting (XSS)                                         | L1    | ★☆☆         | xss, browser, owasp                       |
| SEC-013  | Cross-Site Request Forgery (CSRF)                                  | L1    | ★☆☆         | csrf, browser                             |
| SEC-014  | HTTP vs HTTPS - Why Encryption in Transit Matters                  | L1    | ★☆☆         | tls, https, transit                       |
| SEC-015  | TLS - Transport Layer Security Basics                              | L1    | ★☆☆         | tls, certificates                         |
| SEC-016  | Cookies and Session Management Basics                              | L1    | ★☆☆         | cookies, sessions                         |
| SEC-017  | Input Validation vs Output Encoding                                | L1    | ★☆☆         | validation, encoding                      |
| SEC-018  | Principle of Least Privilege                                       | L1    | ★☆☆         | authorization, design                     |
| SEC-019  | Security Headers (HTTP)                                            | L1    | ★☆☆         | http-headers, csp                         |
| SEC-020  | Same-Origin Policy (SOP) and Browser Security Model               | L1    | ★☆☆         | sop, browser, cors                        |
| SEC-021  | Secure Coding Practices - First Principles                         | L1    | ★☆☆         | secure-coding, sdlc                       |
| SEC-022  | OWASP ZAP - Getting Started 🔧                                     | L1    | ★☆☆         | tools, zap, testing                       |
| SEC-023  | Setting Up a Local Security Testing Environment 🏋️                | L1    | ★☆☆         | practice, lab                             |
| SEC-024  | Burp Suite Community - Introduction 🔧                             | L1    | ★☆☆         | tools, burpsuite                          |
| SEC-025  | Security Mindset - Thinking Like an Attacker                       | L1    | ★☆☆         | mindset, adversarial                      |
| SEC-026  | Common Security Terminology Glossary                               | L1    | ★☆☆         | terminology, vocabulary                   |
| SEC-027  | Vulnerability vs Exploit vs Attack                                 | L1    | ★☆☆         | fundamentals, terminology                 |
| SEC-028  | JSON Web Tokens (JWT)                                              | L2    | ★★☆         | jwt, tokens, authentication               |
| SEC-029  | OAuth 2.0 Basics                                                   | L2    | ★★☆         | oauth, authorization                      |
| SEC-030  | CORS (Cross-Origin Resource Sharing)                               | L2    | ★★☆         | cors, browser, http                       |
| SEC-031  | Content Security Policy (CSP)                                      | L2    | ★★☆         | csp, headers, xss                         |
| SEC-032  | SQL Injection Prevention in Practice                               | L2    | ★★☆         | injection, prepared-statements            |
| SEC-033  | XSS Prevention (Escaping, CSP, DOMPurify)                          | L2    | ★★☆         | xss, escaping, csp                        |
| SEC-034  | CSRF Prevention (CSRF Tokens, SameSite Cookies)                    | L2    | ★★☆         | csrf, cookies, tokens                     |
| SEC-035  | Bcrypt for Password Hashing                                        | L2    | ★★☆         | passwords, bcrypt, hashing                |
| SEC-036  | Secrets Management Basics (env vars, vaults)                       | L2    | ★★☆         | secrets, vault, env                       |
| SEC-037  | Dependency Vulnerability Scanning (Snyk, OWASP DC) 🔧             | L2    | ★★☆         | tools, sca, dependencies                  |
| SEC-038  | HTTPS Certificate Configuration                                    | L2    | ★★☆         | tls, certificates, nginx                  |
| SEC-039  | Session Security (SameSite, Secure, HttpOnly)                      | L2    | ★★☆         | sessions, cookies, flags                  |
| SEC-040  | API Security Basics                                                | L2    | ★★☆         | api, authentication, rate-limiting        |
| SEC-041  | Security Code Review Checklist                                     | L2    | ★★☆         | code-review, sdlc                         |
| SEC-042  | Error Handling and Information Disclosure ⚠️ anti-major           | L2    | ★★☆         | errors, anti-pattern                      |
| SEC-043  | Insecure Direct Object Reference (IDOR)                            | L2    | ★★☆         | idor, authorization, owasp                |
| SEC-044  | Security Testing with OWASP ZAP (Hands-On) 🏋️                    | L2    | ★★☆         | practice, zap, testing                    |
| SEC-045  | Authentication Method Decision Tree 🧭                             | L2    | ★★☆         | decision-framework, authentication        |
| SEC-046  | Hardcoded Credentials Anti-Pattern ⚠️ anti-critical               | L2    | ★★☆         | anti-pattern, secrets, credentials        |
| SEC-047  | Clickjacking and X-Frame-Options                                   | L2    | ★★☆         | clickjacking, headers                     |
| SEC-048  | HTTPS in Local Development                                         | L2    | ★★☆         | tls, development, mkcert                  |
| SEC-049  | Build a Secure Login System (Exercise) 🏋️                         | L2    | ★★☆         | practice, authentication                  |
| SEC-050  | Directory Traversal Vulnerability                                  | L2    | ★★☆         | path-traversal, file-access               |
| SEC-051  | Open Redirect Vulnerability                                        | L2    | ★★☆         | redirect, phishing                        |
| SEC-052  | File Upload Security                                               | L2    | ★★☆         | upload, malware, validation               |
| SEC-053  | Mass Assignment Vulnerability                                      | L2    | ★★☆         | mass-assignment, orm                      |
| SEC-054  | Security Monitoring Basics (audit logs) 📊                         | L2    | ★★☆         | monitoring, logs, audit                   |
| SEC-055  | OWASP Top 10 in Practice Workshop 🏋️                              | L2    | ★★☆         | practice, owasp, workshop                 |
| SEC-056  | JWT Security Anti-Patterns (alg:none, weak secrets) ⚠️ anti-critical | L3 | ★★☆      | jwt, anti-pattern, tokens                 |
| SEC-057  | OAuth 2.0 Deep Dive (flows, scopes, PKCE)                          | L3    | ★★☆         | oauth, pkce, flows                        |
| SEC-058  | OpenID Connect (OIDC)                                              | L3    | ★★☆         | oidc, sso, identity                       |
| SEC-059  | Threat Modeling with STRIDE                                        | L3    | ★★☆         | threat-modeling, stride, design           |
| SEC-060  | SSRF (Server-Side Request Forgery)                                 | L3    | ★★☆         | ssrf, server-side, injection              |
| SEC-061  | XXE (XML External Entity) Injection                                | L3    | ★★☆         | xxe, xml, injection                       |
| SEC-062  | Deserialization Vulnerabilities ⚠️ anti-critical                  | L3    | ★★☆         | deserialization, rce, anti-pattern        |
| SEC-063  | Race Condition Vulnerabilities (TOCTOU)                            | L3    | ★★☆         | race-condition, toctou, concurrency       |
| SEC-064  | Prototype Pollution                                                | L3    | ★★☆         | javascript, prototype, injection          |
| SEC-065  | Path Traversal Advanced Cases                                      | L3    | ★★☆         | path-traversal, bypass, advanced          |
| SEC-066  | TLS Configuration Best Practices (cipher suites, TLS 1.3)         | L3    | ★★☆         | tls, cipher-suites, configuration         |
| SEC-067  | Certificate Pinning                                                | L3    | ★★☆         | tls, certificates, pinning                |
| SEC-068  | SAST (Static Application Security Testing) 🔧                     | L3    | ★★☆         | tools, sast, ci-cd                        |
| SEC-069  | DAST (Dynamic Application Security Testing) 🔧                    | L3    | ★★☆         | tools, dast, ci-cd                        |
| SEC-070  | Software Composition Analysis and Supply Chain Security            | L3    | ★★☆         | sca, sbom, supply-chain                   |
| SEC-071  | Secrets Rotation and Lifecycle Management                          | L3    | ★★☆         | secrets, rotation, vault                  |
| SEC-072  | Container Security Basics                                          | L3    | ★★☆         | containers, docker, hardening             |
| SEC-073  | Security Logging and Monitoring Best Practices 📊                  | L3    | ★★☆         | logging, siem, monitoring                 |
| SEC-074  | OAuth 2.0 Security Best Practices (RFC 9700) 📋                   | L3    | ★★☆         | oauth, rfc, best-practices                |
| SEC-075  | PCI-DSS Overview 📋                                                | L3    | ★★☆         | compliance, pci-dss, payments             |
| SEC-076  | GDPR Security Requirements 📋                                      | L3    | ★★☆         | compliance, gdpr, data-protection         |
| SEC-077  | Security Testing in CI/CD Pipeline 🧪                             | L3    | ★★☆         | testing, ci-cd, devsecops                 |
| SEC-078  | Penetration Testing Methodology 🏋️                                | L3    | ★★☆         | practice, pentest, methodology            |
| SEC-079  | Security Control Performance Testing ⚡                            | L3    | ★★☆         | performance, waf, tls-overhead            |
| SEC-080  | Authentication Mechanism Migration 🔄                              | L3    | ★★☆         | migration, authentication, upgrade        |
| SEC-081  | TLS 1.2 to TLS 1.3 Migration 🔄                                   | L3    | ★★☆         | migration, tls, upgrade                   |
| SEC-082  | OAuth 2.0 vs SAML Decision Framework 🧭                           | L3    | ★★☆         | decision-framework, oauth, saml           |
| SEC-083  | Threat Modeling Workshop 🏋️                                       | L3    | ★★☆         | practice, threat-modeling, workshop       |
| SEC-084  | Business Logic Vulnerabilities ⚠️ anti-major                      | L3    | ★★☆         | business-logic, anti-pattern              |
| SEC-085  | Insufficient Logging Anti-Pattern ⚠️ anti-major                   | L3    | ★★☆         | logging, anti-pattern, observability      |
| SEC-086  | Heartbleed (2014) 🔴                                               | L4    | ★★★         | incident, tls, openssl                    |
| SEC-087  | Log4Shell (2021) 🔴                                                | L4    | ★★★         | incident, rce, log4j                      |
| SEC-088  | SolarWinds SUNBURST Supply Chain Attack (2020) 🔴                  | L4    | ★★★         | incident, supply-chain, apt               |
| SEC-089  | Equifax Data Breach (2017) 🔴                                      | L4    | ★★★         | incident, data-breach, patch-management   |
| SEC-090  | Advanced JWT Attacks (kid injection, jwks spoofing)                | L4    | ★★★         | jwt, attacks, advanced                    |
| SEC-091  | Advanced XSS (DOM clobbering, mutation XSS)                        | L4    | ★★★         | xss, dom, advanced                        |
| SEC-092  | CORS Misconfiguration as Security Vulnerability ⚠️ anti-critical  | L4    | ★★★         | cors, anti-pattern, misconfiguration      |
| SEC-093  | SSRF to Internal Service Exploitation                              | L4    | ★★★         | ssrf, internal, exploitation              |
| SEC-094  | OAuth 2.0 Implicit Flow Deprecation 🔄                             | L4    | ★★★         | oauth, implicit-flow, migration           |
| SEC-095  | TLS Protocol Attacks (BEAST, POODLE, DROWN)                        | L4    | ★★★         | tls, attacks, downgrade                   |
| SEC-096  | Certificate Transparency (CT) Logs                                 | L4    | ★★★         | tls, certificates, transparency           |
| SEC-097  | HTTP Strict Transport Security (HSTS)                              | L4    | ★★★         | hsts, headers, tls                        |
| SEC-098  | CVSS Scoring System                                                | L4    | ★★★         | cvss, vulnerability, scoring              |
| SEC-099  | CVE and NVD - Vulnerability Database                               | L4    | ★★★         | cve, nvd, vulnerability-management        |
| SEC-100  | Responsible Disclosure and Bug Bounty Programs                     | L4    | ★★★         | disclosure, bug-bounty, research          |
| SEC-101  | Security Incident Response (IR) Process                            | L4    | ★★★         | incident-response, ir, forensics          |
| SEC-102  | Digital Forensics Basics (memory, disk, network)                   | L4    | ★★★         | forensics, ir, analysis                   |
| SEC-103  | AWS Security Services (GuardDuty, IAM, WAF, Shield)                | L4    | ★★★         | aws, cloud-security, services             |
| SEC-104  | Kubernetes Security Fundamentals                                   | L4    | ★★★         | kubernetes, k8s, hardening                |
| SEC-105  | SAST in CI/CD (Semgrep, SonarQube, CodeQL) 🔧                     | L4    | ★★★         | tools, sast, ci-cd                        |
| SEC-106  | Security Observability and SIEM 📊                                  | L4    | ★★★         | siem, observability, alerts               |
| SEC-107  | Security at Scale (WAF throughput, TLS offloading) ⚡              | L4    | ★★★         | performance, waf, tls, scale              |
| SEC-108  | ISO 27001 Overview 📋                                               | L4    | ★★★         | compliance, iso27001, isms                |
| SEC-109  | SOC 2 Type II Basics 📋                                             | L4    | ★★★         | compliance, soc2, audit                   |
| SEC-110  | Chaos Engineering for Security (fault injection) 🧪               | L4    | ★★★         | testing, chaos, resilience                |
| SEC-111  | Privilege Escalation Techniques and Mitigation                     | L4    | ★★★         | privesc, exploitation, mitigation         |
| SEC-112  | Zero Trust Architecture Introduction                               | L4    | ★★★         | zero-trust, network, access               |
| SEC-113  | Red Team vs Blue Team vs Purple Team                               | L4    | ★★★         | red-team, blue-team, purple-team          |
| SEC-114  | Zero Trust Architecture Design at Enterprise Scale 🔥              | L5    | 🔥           | zero-trust, enterprise, architecture      |
| SEC-115  | DevSecOps Pipeline Design 🔥                                       | L5    | 🔥           | devsecops, ci-cd, pipeline                |
| SEC-116  | Security Champions Program Design 🔥                               | L5    | 🔥           | champions, culture, governance            |
| SEC-117  | Enterprise Security Architecture (ESA) 🔥                         | L5    | 🔥           | architecture, enterprise, governance      |
| SEC-118  | Company-Wide Secret Rotation Strategy 🔥                           | L5    | 🔥           | secrets, rotation, strategy               |
| SEC-119  | Security Governance and Policy Framework 🔥                        | L5    | 🔥           | governance, policy, compliance            |
| SEC-120  | Threat Intelligence Integration 🔥                                 | L5    | 🔥           | threat-intel, feeds, siem                 |
| SEC-121  | CSIRT Design and Playbook Development 🔥                           | L5    | 🔥           | csirt, ir, playbook                       |
| SEC-122  | Security Metrics and Risk Quantification (FAIR) 🔥                | L5    | 🔥           | metrics, fair, risk                       |
| SEC-123  | Supply Chain Security Strategy (SLSA Framework) 🔥                | L5    | 🔥           | slsa, sbom, supply-chain                  |
| SEC-124  | Platform Security Engineering 🔥                                   | L5    | 🔥           | platform, api-gateway, waf                |
| SEC-125  | Multi-Cloud Security Architecture 🔥                               | L5    | 🔥           | cloud, multi-cloud, architecture          |
| SEC-126  | Build vs Buy Security Decision Framework 🧭 🔥                    | L5    | 🔥           | decision-framework, tools, strategy       |
| SEC-127  | Security Architecture ADR Workshop 🏋️ 🔥                         | L5    | 🔥           | practice, adr, architecture               |
| SEC-128  | SIEM Architecture Design 🔥                                        | L5    | 🔥           | siem, elk, architecture                   |
| SEC-129  | Secure Software Development Lifecycle (SSDLC) 🔥                  | L5    | 🔥           | ssdlc, sdlc, governance                   |
| SEC-130  | TLS 1.3 Protocol Design Rationale 🔬                               | L6    | 🔬           | tls, rfc, protocol-design                 |
| SEC-131  | OAuth 2.0 and OIDC Specification Design Decisions 🔬               | L6    | 🔬           | oauth, oidc, rfc, specification           |
| SEC-132  | OWASP Methodology and Security Science 🔬                          | L6    | 🔬           | owasp, methodology, research              |
| SEC-133  | Secure by Design Principles (Saltzer and Schroeder) 🔬             | L6    | 🔬           | design-principles, saltzer, theory        |
| SEC-134  | Formal Verification of Security Protocols 🔬                       | L6    | 🔬           | formal-methods, verification, protocols   |
| SEC-135  | Web Security Model (Browser Security Architecture) 🔬              | L6    | 🔬           | browser, security-model, specification    |
| SEC-136  | Security Protocol Design Trade-offs 🔬                             | L6    | 🔬           | protocol-design, trade-offs, theory       |
| SEC-137  | Open Problems in Application Security 🔬                           | L6    | 🔬           | open-problems, research                   |
| SEC-138  | CVE Research and Responsible Disclosure Process 🔬                 | L6    | 🔬           | cve, research, disclosure                 |
| SEC-139  | Provable Security vs Practical Security 🔬                         | L6    | 🔬           | theory, formal-security, practical        |
| SEC-140  | Adversarial Thinking as a Design Tool 🧠                           | META  | 🔬           | meta, adversarial, mindset                |
| SEC-141  | Trust Boundary Analysis 🧠                                         | META  | 🔬           | meta, trust, boundaries                   |
| SEC-142  | Assume-Breach Reasoning 🧠                                         | META  | 🔬           | meta, zero-trust, incident                |
| SEC-143  | Security as Contract Management (Pattern Bridge) 🔗 pat 🧠        | META  | 🔬           | meta, pattern-bridge, contracts           |
| SEC-144  | Threat Modeling as Universal Risk Analysis 🧠                      | META  | 🔬           | meta, threat-modeling, risk               |
