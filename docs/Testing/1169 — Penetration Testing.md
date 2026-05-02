---
layout: default
title: "Penetration Testing"
parent: "Testing"
nav_order: 1169
permalink: /testing/penetration-testing/
number: "1169"
category: Testing
difficulty: ★★★
depends_on: Security Test (SAST-DAST), Networking, HTTP & APIs
used_by: Security Teams, DevSecOps, Red Teams
related: Security Test (SAST-DAST), OWASP, DAST, Threat Modeling, DevSecOps
tags:
  - testing
  - security
  - penetration-testing
  - red-team
---

# 1169 — Penetration Testing

⚡ TL;DR — Penetration testing (pen testing) is authorized simulated cyberattack on a system — a security professional actively tries to exploit vulnerabilities to discover weaknesses before real attackers do.

| #1169           | Category: Testing                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Security Test (SAST-DAST), Networking, HTTP & APIs                 |                 |
| **Used by:**    | Security Teams, DevSecOps, Red Teams                               |                 |
| **Related:**    | Security Test (SAST-DAST), OWASP, DAST, Threat Modeling, DevSecOps |                 |

---

### 🔥 The Problem This Solves

AUTOMATED TOOLS MISS BUSINESS LOGIC FLAWS:
SAST finds SQL injection patterns in code. DAST sends fuzzing inputs. But a human attacker can: chain three low-risk vulnerabilities to achieve account takeover; exploit a business logic flaw ("what if I add -1 quantity to my cart?"); find a path through the application that automated scanning never follows; use social engineering vectors that no scanner tests. Pen testing adds the human attacker mindset.

COMPLIANCE REQUIREMENTS:
PCI DSS, ISO 27001, SOC 2, HIPAA all require regular penetration testing. "We run SAST" doesn't satisfy a pen test requirement in an audit.

---

### 📘 Textbook Definition

**Penetration testing** (pen testing) is a simulated cyberattack performed by authorized security professionals (pen testers / ethical hackers) against a computer system, application, or network to find and exploit security vulnerabilities. The goal is to identify weaknesses that an attacker could use, quantify the risk, and provide remediation guidance — before real attackers find them. Types: (1) **black box** — tester has no prior knowledge (simulates external attacker); (2) **white box** — tester has full source code and architecture info (most thorough); (3) **grey box** — tester has limited information (most common). Scope is defined in a **Rules of Engagement (RoE)** document — what systems are in scope, what attack types are permitted, timing restrictions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pen testing = hire an ethical hacker to attack your system before real attackers do.

**One analogy:**

> Pen testing is **hiring a professional locksmith to try to break into your building**: they use all the techniques a real burglar would (pick locks, test windows, social engineer the receptionist), but report what they found instead of robbing you. The goal is to discover weaknesses before a criminal does.

---

### 🔩 First Principles Explanation

METHODOLOGY — THE PTES (PENETRATION TESTING EXECUTION STANDARD):

```
PHASE 1: PRE-ENGAGEMENT
  → Define scope: which systems, applications, networks
  → Rules of Engagement: what's off-limits (production DBs?), timing
  → Emergency contacts: if tester accidentally causes an outage
  → Legal authorization: written permission (without this = criminal offense)

PHASE 2: RECONNAISSANCE (Information Gathering)
  → Passive: OSINT (open-source intelligence)
    - Shodan (internet-exposed ports/services)
    - LinkedIn (employee names → password spray targets)
    - GitHub (accidentally committed secrets)
    - DNS records (subdomains, MX records, SPF)
  → Active: direct probing of target systems
    - Port scanning (nmap)
    - Service fingerprinting
    - Web crawling/spidering

PHASE 3: THREAT MODELING
  → What are the high-value targets? (user PII, payment data, admin access)
  → What attack paths could reach them?
  → What is the likely attacker's capability level?

PHASE 4: VULNERABILITY ANALYSIS
  → Automated scanning: Nessus, OpenVAS, Burp Suite Pro
  → Manual analysis: test business logic, authentication flows
  → Common targets: OWASP Top 10
    - Injection (SQLi, command injection)
    - Broken authentication
    - Sensitive data exposure
    - XXE
    - Broken access control (IDOR)
    - Security misconfiguration
    - XSS
    - Insecure deserialization
    - Known vulnerable components
    - Insufficient logging

PHASE 5: EXPLOITATION
  → Attempt to exploit discovered vulnerabilities
  → Gain initial foothold
  → Escalate privileges (low user → admin → root)
  → Move laterally (from one server to others in the network)
  → Exfiltrate sample data (prove impact)

  TOOLS: Metasploit, Burp Suite, SQLMap, John the Ripper

PHASE 6: POST-EXPLOITATION
  → Determine how long tester could have persisted undetected
  → Assess detection capability of the target

PHASE 7: REPORTING
  → Executive summary: business impact, risk ratings
  → Technical findings: each vulnerability, CVSS score, PoC
  → Remediation: specific fix recommendations, priority
  → Re-test: verify fixes after remediation
```

COMMON FINDINGS (what pen testers find):

```
1. IDOR (Insecure Direct Object Reference):
   GET /api/orders/12345 returns YOUR order
   GET /api/orders/12344 returns ANOTHER USER's order
   → Access control not enforced per resource

2. Business Logic Bypass:
   Apply coupon code to already-discounted item
   → Server doesn't validate cumulative discount limits
   → $500 product for $0.01

3. Authentication Bypass:
   POST /reset-password with email=victim@example.com
   Server returns: token=abc123 in the response body (not just via email)
   → Account takeover without email access

4. Verbose Error Messages:
   POST /api/login with SQL injection in password
   Response: "Error: java.sql.SQLException: ORA-01756..."
   → Database type and schema structure leaked

5. Exposed Admin Interfaces:
   /admin accessible without authentication
   /actuator/env exposes application config (Spring Boot default)
   /phpinfo.php exposes server configuration
```

---

### 🧪 Thought Experiment

THE IDOR CHAIN:

```
Tester finds: GET /api/v1/users/profile?id=10045 returns user profile
Sequential IDs → tries id=10044 → another user's profile (IDOR)
Profile contains: email, phone, partial address

Then: POST /api/v1/password-reset with {"email": "victim@victim.com"}
Response body: {"message": "reset email sent", "debug_token": "abc123"}
(Developer accidentally left debug mode on)

Password reset token returned in response → account takeover without email access

Chain: IDOR (email discovery) + token exposure (account takeover)
Neither vulnerability alone is critical; combined = full account takeover

Lesson: pen testers think in chains. Automated tools find individual
vulnerabilities; pen testers combine them into attack paths.
```

---

### 🧠 Mental Model / Analogy

> Pen testing is **adversarial thinking applied systematically**: where a developer thinks "what should this do?", a pen tester thinks "what can I make this do that it shouldn't?" This mindset flip reveals attack paths that normal development processes don't consider.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Hire an authorized security professional to attack your application. They find vulnerabilities you didn't know about. They write a report. You fix the findings. Required by PCI DSS, SOC 2, ISO 27001.

**Level 2:** Types: black box (no info), grey box (limited info — most common), white box (full code + architecture access). Scope and Rules of Engagement are defined upfront. Findings rated by CVSS score (0-10: 0=informational, 7-10=critical). Critical findings: fix immediately. High: fix within 30 days. Medium: fix within 90 days.

**Level 3:** Continuous penetration testing (bug bounty programs): rather than annual pen tests, companies (HackerOne, Bugcrowd) run continuous programs where security researchers report vulnerabilities for rewards. This provides ongoing adversarial testing between annual formal pen tests. Internal red team: dedicated internal security team that continuously attacks the organization's own systems.

**Level 4:** Pen testing in the SDLC: shift-left security. Threat modeling during design. SAST/DAST in CI (automated, catches low-hanging fruit). Pen test before major releases or annually. Bug bounty program continuously. The pen test is NOT a replacement for building security in — it's the final verification layer. A mature DevSecOps pipeline has: secure coding training → SAST in IDE → SAST in CI → DAST against staging → pen test before launch → bug bounty ongoing.

---

### 💻 Code Example

```bash
# OWASP ZAP — automated DAST (part of CI pipeline, not a full pen test)
docker run -v $(pwd):/zap/wrk/:rw \
  owasp/zap2docker-stable zap-baseline.py \
  -t https://staging.myapp.com \
  -r zap-report.html

# Output: automated scan for common OWASP Top 10 issues
# Note: ZAP is DAST/automated scanning, NOT penetration testing
# Pen test requires a human tester thinking adversarially
```

```
# Example pen test finding (from report):
Finding ID: PT-2024-042
Title: Insecure Direct Object Reference (IDOR) in Order API
Severity: HIGH (CVSS 7.5)
Affected Endpoint: GET /api/v2/orders/{orderId}

Description:
  The API endpoint does not validate that the authenticated user owns the
  requested order. An attacker with a valid session can enumerate other users'
  order IDs and access their order data, including shipping address and items purchased.

Proof of Concept:
  1. Authenticate as user A (ID: 10045)
  2. Place an order (Order ID: ORD-99874)
  3. Authenticate as user B (ID: 10046)
  4. Request GET /api/v2/orders/ORD-99874
  5. Response: 200 OK with user A's complete order data

Impact:
  Exposure of PII (name, address), order history for all users.
  ~50,000 user orders accessible.

Remediation:
  Add authorization check: verify order.userId == authenticatedUser.id
  before returning order data. Return HTTP 403 if check fails.
  Do NOT return 404 (to prevent ID enumeration).
```

---

### ⚖️ Comparison Table

|                        | SAST                       | DAST                    | Pen Test                         |
| ---------------------- | -------------------------- | ----------------------- | -------------------------------- |
| What it finds          | Code-level vulnerabilities | Runtime vulnerabilities | Business logic + chained attacks |
| Speed                  | Seconds-minutes            | Minutes-hours           | Days-weeks                       |
| Human expertise        | No                         | No                      | Yes (critical differentiator)    |
| Business logic testing | No                         | Partially               | Yes                              |
| Compliance satisfies   | Partially                  | Partially               | Yes (PCI, SOC 2, ISO 27001)      |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| "SAST/DAST replaces pen testing"     | Automated tools miss business logic flaws, vulnerability chains, and novel attack paths that require human creativity   |
| "Once a year pen test is sufficient" | Annual pen tests miss new vulnerabilities introduced throughout the year; continuous program (bug bounty) fills the gap |
| "Pass = secure"                      | Pen test passing means no critical findings during that engagement; it doesn't mean no vulnerabilities exist            |

---

### 🚨 Failure Modes & Diagnosis

**1. Out-of-Scope Discoveries**
Situation: Pen tester discovers a critical vulnerability in a system not in scope.
Response: Immediately report via emergency contact. Don't exploit. Document and handle per Rules of Engagement.

**2. Findings Not Remediated After Test**
Cause: Report delivered, findings tracked in backlog, deprioritized over features.
Result: Next year's pen test finds same vulnerabilities.
**Fix:** Critical/High findings must have mandatory remediation SLAs. Re-test to verify fixes.

**3. Testing in Production Without Safeguards**
Risk: Pen test against production can cause outages (buffer overflow exploits, DoS as side effect).
**Fix:** Test against staging (production clone). If production testing required, out-of-hours window with rollback plan.

---

### 🔗 Related Keywords

- **Prerequisites:** Security Test (SAST-DAST), Networking, HTTP & APIs
- **Related:** OWASP Top 10, CVSS, Burp Suite, Metasploit, DAST, Threat Modeling, Bug Bounty, Red Team, DevSecOps

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Authorized simulated attack by ethical   │
│              │ hacker to find real vulnerabilities      │
├──────────────┼───────────────────────────────────────────┤
│ TYPES        │ Black box (no info) / Grey (limited) /   │
│              │ White (full source + architecture)       │
├──────────────┼───────────────────────────────────────────┤
│ REQUIRED BY  │ PCI DSS, SOC 2, ISO 27001, HIPAA        │
├──────────────┼───────────────────────────────────────────┤
│ PROCESS      │ Scope → Recon → Vulnerability Analysis  │
│              │ → Exploit → Report → Remediate → Retest │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Find it first — before attackers do;   │
│              │  human creativity catches what scanners  │
│              │  miss"                                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The OWASP Top 10 provides a framework for understanding common web application security risks. For each of these 3 critical categories, describe: (1) **Broken Access Control** (A01): beyond IDOR — describe horizontal vs. vertical privilege escalation, forced browsing (accessing /admin without following the navigation link), JWT manipulation (changing the `role` claim), and `cors` misconfiguration (`Access-Control-Allow-Origin: *` on authenticated endpoints); (2) **Injection** (A03): beyond SQL injection — OS command injection (`; cat /etc/passwd`), LDAP injection, template injection (Jinja2/Thymeleaf), and how parameterized queries/prepared statements prevent SQL injection but not other injection types; (3) **Security Misconfiguration** (A05): default credentials (admin/admin), Spring Boot Actuator endpoints exposed in production (`/actuator/heapdump` — memory dump with credentials), verbose error messages, S3 bucket public access, and how security hardening checklists prevent these.

**Q2.** The penetration tester's methodology for testing JWT-based authentication: (1) decode the JWT (base64-encoded, not encrypted — any user can read the claims without the secret key), (2) the `alg: none` attack (change algorithm to "none" in header — some libraries accept unsigned tokens), (3) the algorithm confusion attack (RS256 → HS256: if the server accepts both, use the public key as the HMAC secret), (4) claim manipulation (change `role: user` to `role: admin` — requires signature bypass first), (5) expiration bypass (set `exp` to future date — requires signature bypass), and (6) the proper secure implementation: always validate signature, enforce algorithm (never accept `alg: none`), validate all claims (iss, aud, exp), and use short expiration + refresh token rotation.
