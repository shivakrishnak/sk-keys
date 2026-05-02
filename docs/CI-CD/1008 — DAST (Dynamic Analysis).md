---
layout: default
title: "DAST (Dynamic Analysis)"
parent: "CI/CD"
nav_order: 1008
permalink: /ci-cd/dast/
number: "1008"
category: CI/CD
difficulty: ★★★
depends_on: SAST, Continuous Delivery, HTTP & APIs
used_by: SCA, Progressive Delivery, Deployment Pipeline
related: SAST, Penetration Testing, SCA
tags:
  - cicd
  - security
  - devops
  - advanced
  - testing
---

# 1008 — DAST (Dynamic Analysis)

⚡ TL;DR — DAST tests a running application by sending real HTTP attacks (SQL injection, XSS, auth bypass) and observing responses — finding vulnerabilities that only appear at runtime, which SAST cannot detect.

| #1008 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | SAST, Continuous Delivery, HTTP & APIs | |
| **Used by:** | SCA, Progressive Delivery, Deployment Pipeline | |
| **Related:** | SAST, Penetration Testing, SCA | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
SAST scans your source code and finds SQL injection patterns. But some vulnerabilities only appear at runtime: a JWT token that accepts `alg:none` (algorithm confusion attack), an API endpoint missing rate limiting that allows 1000 requests/second brute-force, a misconfigured CORS policy that allows any origin. These vulnerabilities don't exist in the code as patterns — they emerge from the configuration, framework version, or interaction between components. SAST sees none of them.

**THE BREAKING POINT:**
Static analysis has a fundamental ceiling: it can only find what's visible in the code. Runtime configuration, framework behaviour, server settings, and environment-specific vulnerabilities are invisible to any code scanner. A perfectly SAST-clean codebase can have Critical runtime vulnerabilities.

**THE INVENTION MOMENT:**
This is exactly why DAST was created: attack the running application the same way an adversary would — sending real HTTP requests, probing authentication, fuzzing inputs — to find vulnerabilities that only manifest when the application is alive and processing requests.

---

### 📘 Textbook Definition

**DAST (Dynamic Application Security Testing)** is a black-box security testing methodology that analyses a running application by sending it automated attack payloads and analysing responses. Unlike SAST (which needs source code), DAST only requires the application's URL. DAST tools simulate the techniques used by external attackers: SQL injection via query parameters, XSS via form inputs, broken authentication via token replay, directory traversal via path manipulation, and CSRF via cross-origin requests. Common DAST tools include OWASP ZAP (free), Burp Suite Enterprise, and Detectify. DAST runs against deployed environments (staging, pre-production) in the CI/CD pipeline, after the test stage and before production promotion.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DAST sends real attacks to your running app and checks what happens — like a hacker, automatically.

**One analogy:**
> SAST is like a building inspector reading the blueprints for fire hazards. DAST is the fire marshal who comes to the actual building, sets a small controlled fire, and checks whether the sprinklers work, whether doors seal correctly, and whether evacuation routes are clear. The blueprints might be fine; the actual building might still fail.

**One insight:**
SAST and DAST are **complementary, not competing**. SAST finds code-level vulnerabilities (SQL injection patterns, insecure cryptography usage) at commit time. DAST finds runtime vulnerabilities (misconfigured headers, broken OAuth flows, server-side behaviour) after deployment. A mature security program requires both.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. DAST targets a running application — it requires a deployed environment.
2. DAST is black-box — it needs no source code access, only an HTTP endpoint.
3. DAST simulates external attackers — it finds vulnerabilities from the outside-in perspective.

**DERIVED DESIGN:**
DAST scanners work in two phases: **crawl** (discover the application's attack surface — all URLs, forms, and API endpoints) and **attack** (send crafted payloads against each discovered endpoint, analysing responses for vulnerability signatures).

Modern API-first applications require **authenticated DAST**: the scanner must present valid auth tokens to test protected endpoints. This requires either a test login or an injected JWT token. Without authentication, DAST only tests the login page and publicly accessible endpoints — a very limited attack surface.

**THE TRADE-OFFS:**
**Gain:** Finds runtime vulnerabilities invisible to SAST. Can test from the attacker's perspective. Language-agnostic — works on any HTTP-serving application regardless of implementation language.
**Cost:** Requires a live deployed environment. Scan time: 45 minutes to 4 hours depending on application size. Risk of DAST payloads corrupting test data. False positives still occur. Cannot find vulnerabilities in non-HTTP logic.

---

### 🧪 Thought Experiment

**SETUP:**
A REST API uses JWT for authentication. The developer reads a blog post about JWT and uses `jjwt` version 0.6 which has a known algorithm confusion vulnerability: if `alg: none` is passed in the JWT header, the signature is not verified. SAST doesn't find it because there is no pattern to match — the code just calls `jjwt.parse(token)` which looks correct.

**WHAT HAPPENS WITHOUT DAST:**
The API ships. An attacker discovers the `alg:none` vector. Crafts a JWT token with `alg:none` and any user ID in the payload. The API accepts it as valid and returns the target user's data. Complete authentication bypass.

**WHAT HAPPENS WITH DAST (OWASP ZAP):**
DAST scans the authenticated endpoint. The scanner sends a request with a modified JWT where `alg` is set to `none` and the signature is stripped. The API returns a 200 with data → DAST flags: "JWT Authentication Bypass: alg:none accepted." The finding is reported before production deployment. Developer upgrades `jjwt` library and validates the `alg` header.

**THE INSIGHT:**
The vulnerability was in the framework's default behaviour, not in the developer's code. SAST cannot detect framework-level vulnerabilities. DAST caught it because it actually tried the attack.

---

### 🧠 Mental Model / Analogy

> DAST is a red team exercise on autopilot. A red team penetration tester manually tries to break into your application — DAST does the same, automatically, on every deployment. It won't be as creative as an expert human tester, but it will be consistent, fast, and available 24/7 in the pipeline.

- "Red team tester" → DAST scanner
- "Attack techniques" → fuzzing payloads, injection strings, auth bypass attempts
- "Testing the actual building" → running against the deployed application
- "Tester's report" → DAST findings with CVE/CWE classification
- "Consistent, repeatable" → every deployment gets the same attack suite

Where this analogy breaks down: a real red team has creativity, context, and chains multiple vulnerabilities together. DAST is automated and finds only known-pattern vulnerabilities. Business logic flaws (e.g., "customer can buy items at negative quantity") require human testers.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
DAST is a security robot that tries to hack your website automatically. It sends the same kinds of attacks real hackers use — but in a controlled, automatic way, against your test environment — and reports which attacks worked.

**Level 2 — How to use it (junior developer):**
Integrate DAST in the CD pipeline, after the staging deployment step. Use OWASP ZAP (free) or a cloud DAST service. Configure ZAP with: target URL, authentication method (API key or form login), and attack level (passive/active). Run in "active scan" mode for comprehensive testing. Review the HTML report for High/Critical findings. Address Critical findings before promoting to production. Block pipeline if Critical findings exceed threshold.

**Level 3 — How it works (mid-level engineer):**
ZAP's active scanner uses attack trees: for each discovered endpoint, it tests each input parameter with a suite of payloads (SQL injection strings, XSS vectors, path traversal sequences, LDAP injection). Responses are analysed: a SQL error message indicates SQL injection; reflected input in the response indicates XSS. ZAP also performs passive scanning — analysing all proxied HTTP traffic for misconfigured headers, insecure cookies, and information leakage without sending attack payloads. For REST APIs, provide an OpenAPI specification to ZAP — it maps all endpoints without crawling, enabling more complete coverage.

**Level 4 — Why it was designed this way (senior/staff):**
DAST occupies a unique position in the security testing ecosystem because it is the only tool that tests the complete deployed application stack — code + framework + server configuration + network environment. This completeness comes at the cost of complexity: DAST must navigate authentication flows, session management, and stateful interactions that static analysis avoids entirely. The emerging IAST (Interactive Application Security Testing) model attempts to bridge SAST and DAST: instruments the application's bytecode at runtime to trace which code paths were executed during DAST scanning — providing DAST's runtime coverage with SAST-style code attribution. Tools like Contrast Security and Seeker implement IAST.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│          DAST SCAN EXECUTION (ZAP)          │
├─────────────────────────────────────────────┤
│  Input: staging URL + authentication config │
│                                             │
│  Phase 1: SPIDER / CRAWL                    │
│  - Discover all URLs (follow links + forms) │
│  - For REST APIs: import OpenAPI spec       │
│  - Result: list of all endpoints + params   │
│                                             │
│  Phase 2: PASSIVE SCAN (0 attack payloads)  │
│  - Analyse HTTP headers for issues:         │
│    - Missing Content-Security-Policy        │
│    - Missing X-Frame-Options                │
│    - Insecure cookies (no HttpOnly/Secure)  │
│  - Result: low-risk configuration findings  │
│                                             │
│  Phase 3: ACTIVE SCAN (attack payloads)     │
│  For each endpoint × each parameter:        │
│  - SQL injection: '; DROP TABLE users; --   │
│  - XSS: <script>alert(1)</script>           │
│  - Path traversal: ../../../../etc/passwd   │
│  - Command injection: ; cat /etc/passwd     │
│  Analysis: is response different from base? │
│  → SQL error = SQL injection found           │
│  → Input reflected = XSS found              │
│                                             │
│  Phase 4: REPORT                            │
│  - SARIF / HTML / JSON output               │
│  - Findings with CVSS score + CWE ID        │
└─────────────────────────────────────────────┘
```

**Authenticated DAST configuration:**
```yaml
# ZAP API scan with JWT authentication
context:
  authentication:
    method: script
    # Custom script to obtain and refresh JWT token
    script: auth-scripts/get-jwt-token.js
    parameters:
      loginUrl: https://staging.example.com/auth/login
      username: dast-test-user
      password: ${{ secrets.DAST_TEST_PASSWORD }}
  # Attach token to all requests
  headerBasedAuth:
    headerName: Authorization
    headerValue: "Bearer %token%"
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
CD pipeline: application deployed to staging
  → Staging: health check passes
  → DAST triggered: target = https://staging.example.com
  → Phase 1: spider discovers 47 endpoints
  → Phase 2: passive scan — 2 medium findings (headers)
  → Phase 3: active scan (45 min) [← YOU ARE HERE]
  → 0 Critical / 0 High / 2 Medium findings
  → Report generated: SARIF uploaded to security dashboard
  → Gate: 0 Critical findings → PASS
  → CD pipeline: promote to production
```

**FAILURE PATH:**
```
Active scan: SQL injection found on /api/users?filter=
  → DAST finding: Critical, CWE-89
  → SARIF uploaded
  → Pipeline gate: "Critical DAST finding — block promotion"
  → Production deploy: BLOCKED
  → Slack alert: "staging DAST failed: SQL injection"
  → Developer investigates → fixes PreparedStatement
  → DAST reruns → no critical findings → unblocked
```

**WHAT CHANGES AT SCALE:**
At 50+ microservices, DAST 45-minute scans become a throughput bottleneck. Teams implement: (1) baseline scan (passive + fast checks in 5 minutes) blocking promotion, (2) full scan running asynchronously post-merge, (3) finding deduplication (same endpoint, same attack pattern = one finding, not 50), and (4) DAST result caching — skip re-scanning endpoints unchanged since the last scan.

---

### 💻 Code Example

**Example 1 — OWASP ZAP in GitHub Actions:**
```yaml
dast:
  needs: deploy-staging
  runs-on: ubuntu-latest
  steps:
    - name: Run ZAP API Scan
      uses: zaproxy/action-api-scan@v0.9.0
      with:
        target: 'https://staging.example.com'
        format: openapi
        # OpenAPI spec for comprehensive endpoint coverage
        file: 'api-spec/openapi.yaml'
        # Fail on Medium+ findings
        fail_action: true
        # Minimum finding severity to fail pipeline
        # Options: low, medium, high, critical
        cmd_options: '-l medium'
        rules_file_name: '.zap/rules.tsv'  # custom rules

    - name: Upload ZAP Report
      uses: actions/upload-artifact@v4
      if: always()  # upload even if scan failed
      with:
        name: zap-results
        path: report.*
```

**Example 2 — Custom suppression for known false positives:**
```tsv
# .zap/rules.tsv — disable specific ZAP rules
10016	IGNORE	# Web browser XSS protection header (handled by CSP)
10017	IGNORE	# X-Frame-Options (we use CSP frame-ancestors instead)
# Format: Rule ID  Action  Reason
```

**Example 3 — DAST data isolation — never use prod data:**
```bash
# DAST must run against a DEDICATED test environment
# With test data only — active scanner writes to the DB!

# BAD: DAST against staging with production data copy
TARGET=https://staging.example.com  # has real user data
# SQL injection test might write to the database
# DAST test user accounts may access real data

# GOOD: DAST against dedicated DAST environment
TARGET=https://dast.example.com      # test data only
# Wipe and repopulate before each scan
./scripts/reset-dast-environment.sh
```

---

### ⚖️ Comparison Table

| Testing Type | Needs Source? | Needs Running App? | Finds | Speed | Position |
|---|---|---|---|---|---|
| **DAST** | No | Yes | Runtime vulns, config issues | Slow (45min+) | Post-deploy (staging) |
| SAST | Yes | No | Code pattern vulns, data flows | Medium (5-15min) | Pre-deploy (CI) |
| SCA | No (just deps) | No | Known CVEs in dependencies | Fast (1-5min) | Pre-deploy (CI) |
| IAST | Yes | Yes | Both code + runtime | Medium | Post-deploy |
| Penetration Test | No | Yes | Novel, chained attacks | Days-weeks | Pre-release |

How to choose: Use SAST + SCA in the CI pipeline (fast, pre-deploy). Use DAST in the staging pipeline (comprehensive, post-deploy). Use manual penetration testing before major releases or for compliance (PCI DSS, ISO 27001). IAST is emerging but requires bytecode instrumentation — useful for complex applications where SAST and DAST have coverage gaps.

---

### 🔁 Flow / Lifecycle

```
┌───────────────────────────────────────────────┐
│          DAST IN CD PIPELINE PHASES           │
├───────────────────────────────────────────────┤
│  1. DEPLOY to staging [prerequisite]          │
│         ↓                                     │
│  2. BASELINE SCAN (5 min, non-blocking)       │
│     - Passive headers/config checks           │
│     - Quick authentication test               │
│         ↓                                     │
│  3. FULL ACTIVE SCAN (45 min, blocking gate)  │
│     - SQL injection                           │
│     - XSS                                     │
│     - Auth bypass                             │
│     - CSRF / CORS                             │
│         ↓                                     │
│  4. TRIAGE                                    │
│     - Critical → block promotion              │
│     - High → create Security ticket           │
│     - Medium/Low → log, review weekly         │
│         ↓ (no Critical)                       │
│  5. PROMOTE to pre-prod / production          │
│         ↓                                     │
│  6. REPORT → security dashboard               │
└───────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DAST can replace penetration testing | DAST automates known attack patterns. Pen testers chain vulnerabilities creatively, exploit business logic, and find novel attack paths. DAST and pen testing are complementary |
| DAST only scans websites, not APIs | Modern DAST tools (ZAP API scan, Burp API scanner) are purpose-built for REST/GraphQL APIs. Provide an OpenAPI spec for comprehensive API DAST coverage |
| DAST can run against production safely | DAST active scanning sends malicious payloads that can corrupt data, lock accounts, or crash the application. Always run against a dedicated test environment, never production |
| All DAST findings are exploitable | DAST has false positives — reflected parameters that appear as XSS but are sanitised by the browser. Triage each finding individually before treating it as confirmed |

---

### 🚨 Failure Modes & Diagnosis

**1. DAST Corrupts Test Data — Downstream Tests Fail**

**Symptom:** Integration tests that run after DAST pass individually but fail in the post-DAST run because test data has been modified or deleted by DAST payloads.

**Root Cause:** DAST active scanner sends write operations (POSTs, PUTs with injection payloads) that modify the database. Test data is corrupted.

**Diagnostic:**
```bash
# Check database state before and after DAST
# Before DAST:
psql -c "SELECT count(*) FROM test_users"
# Run DAST
# After DAST:
psql -c "SELECT count(*) FROM test_users"
# Different counts = DAST modified data
```

**Fix:** Reset test environment completely before and after each DAST run:
```bash
# Before DAST
./scripts/reset-test-db.sh && ./scripts/seed-test-data.sh
# Run DAST
# After DAST (restore for other tests)
./scripts/reset-test-db.sh && ./scripts/seed-test-data.sh
```

**Prevention:** Run DAST in a completely isolated environment provisioned solely for DAST. Never share a DAST environment with other test suites.

---

**2. DAST Times Out — Pipeline Blocks for 2 Hours**

**Symptom:** DAST scan takes 2+ hours instead of the expected 45 minutes. Pipeline is blocked. Developers can't merge.

**Root Cause:** Application has hundreds of endpoints. ZAP discovers all and runs the full attack suite against each. No timeout configured.

**Diagnostic:**
```bash
# Count endpoints being scanned
# ZAP: check the spider results tab in the gui
# Or in CI: check ZAP log for "Total items to scan: N"
grep "Total" zap.log
```

**Fix:** Limit scope and add timeout:
```yaml
uses: zaproxy/action-api-scan@v0.9.0
with:
  cmd_options: >
    -m 30    # max 30 minutes total
    -z '-config scanner.maxScanDurationInMins=25'
```

**Prevention:** Set hard timeout for DAST stage in pipeline. Design a "fast DAST" with passive scan only for PR-blocking and full DAST running asynchronously.

---

**3. DAST Can't Access Protected Endpoints — Finds Nothing**

**Symptom:** DAST scan completes in 5 minutes with 0 findings. Suspicious — the app has many sensitive endpoints. Post-investigation: DAST couldn't authenticate.

**Root Cause:** Authentication token expired mid-scan or the login script failed silently.

**Diagnostic:**
```bash
# Check ZAP scan log for authentication errors
grep -i "auth\|401\|403\|login" zap-scan.log | head -20
# If 401s throughout = DAST wasn't authenticated
```

**Fix:** Verify authentication separately before DAST:
```bash
# Verify auth token works before scan
TOKEN=$(curl -s -X POST https://staging/auth/login \
  -d '{"user":"dast-user","pass":"test"}' \
  | jq -r '.token')
echo "Token: $TOKEN"
curl -H "Authorization: Bearer $TOKEN" \
  https://staging/api/users
# Must return 200, not 401
```

**Prevention:** Add a "verify DAST authentication" pre-step that fails the pipeline explicitly if authentication fails. Don't let DAST run (and waste 45 minutes) if it can't authenticate.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SAST (Static Analysis)` — DAST complements SAST; understanding SAST clarifies what DAST adds and why both are necessary
- `Continuous Delivery` — DAST runs in the CD pipeline after staging deployment; CD pipeline structure is required knowledge
- `HTTP & APIs` — DAST attacks HTTP endpoints; understanding HTTP protocols and API structures is required to interpret findings

**Builds On This (learn these next):**
- `SCA (Software Composition Analysis)` — the third security pillar alongside SAST and DAST; scans dependencies for CVEs
- `Progressive Delivery` — DAST findings inform whether a canary deployment should be promoted or rolled back
- `Penetration Testing` — the manual, creative complement to automated DAST; required for compliance and novel vulnerability discovery

**Alternatives / Comparisons:**
- `SAST` — static complement to DAST; finds code-level vulnerabilities without requiring application deployment
- `IAST` — hybrid approach: instruments the running app during DAST scanning for more precise findings with code attribution
- `Penetration Testing` — manual testing by security experts; more thorough but far slower and more expensive

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automated security attack against a       │
│              │ running application — black-box testing   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Runtime vulnerabilities (misconfigured    │
│ SOLVES       │ headers, JWT bypass, CORS) invisible to   │
│              │ SAST and code review                      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ SAST and DAST find different vulnerability │
│              │ classes — use both; never substitute one  │
│              │ for the other                             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any HTTP-serving application handling     │
│              │ user input — must run against staging,    │
│              │ never production                          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never against production — active scan    │
│              │ can corrupt data and lock accounts        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Runtime vulnerability coverage vs slow    │
│              │ scan time (45min+) and environment cost  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The fire marshal who tests the actual    │
│              │  building, not just reads the blueprint"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SCA → Dependency Scanning → SBOM          │
│              │ → Penetration Testing                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your organisation's DAST scan runs against a staging environment that is 90% production-equivalent. The 10% difference: staging uses a read-only database replica (no writes), staging has rate limiting disabled (to avoid scan traffic being blocked), and staging uses self-signed TLS certificates. For each of the three differences, identify a class of vulnerability that this difference would either cause DAST to miss entirely OR cause DAST to report as a finding that wouldn't exist in production.

**Q2.** A DAST scan finds a reflected XSS vulnerability: the endpoint `/search?q=` reflects the `q` parameter value in the HTML page. The developer says: "This is a false positive — we use React on the frontend which auto-escapes all interpolated values, so even if the parameter contains `<script>`, it's never executed." The DAST tool still flags it as a finding. Walk through the technical argument for why THE DEVELOPER MIGHT BE WRONG and what additional conditions would make this a real, exploitable XSS despite React's auto-escaping.

