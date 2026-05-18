---
id: SEC-022
title: "OWASP ZAP - Getting Started"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-004, SEC-011, SEC-012
used_by: SEC-039, SEC-064, SEC-077
related: SEC-001, SEC-004, SEC-011, SEC-012, SEC-024, SEC-039, SEC-064, SEC-077
tags:
  - security
  - owasp-zap
  - dast
  - penetration-testing
  - security-testing
  - tools
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/sec/owasp-zap-getting-started/
---

⚡ TL;DR - OWASP ZAP (Zed Attack Proxy) is a free, open-source
DAST (Dynamic Application Security Testing) tool for finding
security vulnerabilities in web applications by sending
actual HTTP requests and analyzing responses. It works as
an intercepting proxy sitting between your browser and the
target application. Main capabilities: proxy (intercept and
modify requests in real-time), active scanner (automated
attack payloads to find vulnerabilities), passive scanner
(identifies issues from observed traffic without sending
attacks), fuzzer (brute-force parameter values), spider
(discover all application URLs).

ZAP is the free alternative to Burp Suite Pro. Key use
cases: automated security testing in CI/CD pipelines,
manual security testing for developers learning web
security, OWASP Top 10 verification, and security review
before production deployment. In 2024: ZAP has been
moved to Software Security Project (SSP) under the Linux
Foundation after OWASP. Core functionality unchanged.

---

| #022 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, OWASP Top 10, SQL Injection, XSS | |
| **Used by:** | Security Testing ZAP Hands-On, DAST, Security Testing in CI/CD | |
| **Related:** | OWASP Top 10, Burp Suite, DAST, Penetration Testing, Security Testing in CI/CD | |

---

### 🔥 The Problem This Solves

**SECURITY TESTING WITHOUT DAST:**
A developer writes code, writes unit tests, passes all tests,
deploys to staging. The application has an IDOR vulnerability:
any user can access any other user's profile by changing
the ID in the URL. Unit tests don't test this - they test
that the correct user's profile is returned, not that
another user's profile is rejected. Code review may catch
it but relies on the reviewer's security knowledge.

ZAP (and DAST tools in general) test the running application
from the attacker's perspective. They send real HTTP requests
to the actual running application and look for unexpected
responses that indicate vulnerabilities. The IDOR test:
log in as user A, access user B's resources, does the server
return them? If yes: IDOR found.

DAST catches what SAST and code review miss: runtime behavior,
authentication bypass, access control failures, injection
through HTTP parameters that static analysis doesn't trace.

---

### 📘 Textbook Definition

**OWASP ZAP (Zed Attack Proxy):** A free, open-source web
application security scanner. It acts as a man-in-the-middle
between the browser and the application, allowing interception,
modification, and automated testing of HTTP/HTTPS traffic.

**Core Components:**

**Proxy:** ZAP listens on localhost:8080 (default).
Configure browser to use ZAP as HTTP proxy. All traffic
flows through ZAP, which logs and can modify requests/responses.

**Spider (Crawler):** Discovers all URLs in the application.
Traditional spider: follows HTML links, form actions.
AJAX Spider: executes JavaScript to discover dynamically
loaded content (required for SPAs).

**Passive Scanner:** Analyzes all observed traffic for
security issues WITHOUT sending additional attack requests.
Finds: missing security headers, cookie issues, information
leakage in responses. No impact on the application.

**Active Scanner:** Sends attack payloads to discovered
endpoints. Tests for: SQL injection, XSS, command injection,
path traversal, and many other OWASP Top 10 issues.
Impact: sends many requests, may modify data, can cause
application errors. Only use against authorized targets.

**Fuzzer:** Sends many variations of a parameter value.
Manual tool for brute-forcing auth tokens, testing unusual
inputs, finding edge cases.

**Authentication:** ZAP can handle form-based and script-based
authentication to test authenticated portions of the application.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ZAP = browser middleman that records, replays, and attacks
your web application's HTTP traffic to find vulnerabilities
automatically - free, open-source, CI/CD compatible.

**One analogy:**
> ZAP is like a security-testing postal worker. Instead of
> just delivering your letters (normal proxy), this postal
> worker also: photographs every letter (passive scan),
> opens them to see if anything suspicious is inside
> (analyze requests/responses), sends deliberately garbled
> versions to see how the recipient reacts (active scan/fuzzer),
> and maps out every address you communicate with (spider).
> All without you noticing - but the recipient (your app)
> gets tested for how it handles unusual messages.

---

### 🔩 First Principles Explanation

**How active scanning works - injection testing:**

```
ACTIVE SCANNER METHODOLOGY for SQL injection detection:

TARGET ENDPOINT: GET /search?q=shoes

STEP 1: ZAP discovers the URL and parameters
  URL: /search?q=shoes
  Parameters identified: q (query string)
  
STEP 2: Baseline request
  GET /search?q=shoes
  Response: 200 OK, 15 results for "shoes"
  Note: response length = 4500 bytes

STEP 3: Inject SQL syntax payloads into 'q' parameter
  Payload 1: GET /search?q=shoes' (single quote)
  Response: 500 Internal Server Error
             "You have an error in your SQL syntax"
  → FINDING: SQL error exposed. Potential SQL injection.
  
  Payload 2: GET /search?q=shoes' OR '1'='1
  Response: 200 OK, 15000 results (all products)
  → FINDING: SQL injection confirmed. Boolean bypass.
  
  Payload 3: GET /search?q=shoes'; WAITFOR DELAY '0:0:5'--
  Response: delayed by 5 seconds
  → FINDING: Time-based SQL injection. Code execution risk.

STEP 4: ZAP generates alert:
  Risk: HIGH
  Confidence: MEDIUM/HIGH
  Evidence: "You have an error in your SQL syntax"
  Solution: Use parameterized queries.
  References: OWASP SQL Injection Prevention Cheat Sheet.

FALSE POSITIVES:
  Active scanners have false positives (reported vulns that aren't real).
  ZAP's finding must be VERIFIED manually.
  In CI/CD: filter by confidence (Medium/High), not Low.
  Triage alerts before treating as confirmed vulnerabilities.

DAST LIMITATIONS:
  - Tests running application only (not static code)
  - Requires authenticated session for protected endpoints
  - Cannot discover all URLs (dynamic apps, SPAs need AJAX spider)
  - Active scan can modify data (safe for test environments only)
  - Misses business logic vulnerabilities (not parameterizable)
```

---

### 🧪 Thought Experiment

**SCENARIO: ZAP in CI/CD pipeline - automated security gate**

```
CI/CD PIPELINE INTEGRATION:

PIPELINE STAGE: "Security Test" after deployment to staging

SETUP:
  1. Deploy application to staging environment
  2. ZAP Docker container starts: owasp/zap2docker-stable
  3. ZAP baseline scan runs against staging URL

WHAT BASELINE SCAN TESTS:
  Passive checks: security headers, cookie flags, information leakage
  Active checks: subset of active scanner rules (low-risk payloads)
  Duration: 2-5 minutes (fast, low-impact)

PIPELINE DECISION:
  ZAP output: XML/JSON report with findings by severity
  
  High severity findings → FAIL the pipeline
    → Deployment blocked. Security team alerted.
    → Example: missing Content-Security-Policy header
    
  Medium severity findings → WARN (depends on policy)
    → Some teams fail on medium too
    → Example: server version disclosed in response header
  
  Low severity findings → REPORT only
    → Example: autocomplete not disabled on search field

EXAMPLE COMMAND (Jenkins/GitHub Actions):
  docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t https://staging.example.com \
    -r zap-report.html \
    -x zap-report.xml \
    -z "-config rules.maxAlertsPerRule=10"
  
  parse exit code: 0 = no issues, 1 = warnings, 2 = failures

FALSE POSITIVE MANAGEMENT:
  ZAP config file (false-positive list) per project:
    - Mark specific findings as false positives
    - Prevents recurrence in reports
    - Version-controlled alongside application code

AUTHENTICATED SCANNING (full coverage):
  ZAP API: log in as test user, export session
  Full spider: discovers authenticated endpoints
  Active scan: tests protected functionality
  Duration: 20-60 minutes (CI/CD nightly build)
```

---

### 🧠 Mental Model / Analogy

> ZAP is to web security what a building code inspector is
> to construction. After a developer builds a feature (frame
> a wall), a building inspector comes and checks it against
> safety codes without needing to understand exactly how it
> was built. The inspector applies a systematic checklist
> to the finished product. ZAP applies a systematic security
> checklist to the running web application. The inspector
> (ZAP) may occasionally fail something that's actually
> fine (false positive) or miss something subtle (false
> negative) - but covers the systematic, well-known safety
> issues consistently. It's not a substitute for good
> engineering - it's the final check before signing off.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ZAP is a tool that pretends to be a normal user visiting
your website but secretly tests it for security problems.
It sends unusual data to your forms and URLs and checks
if the application handles it safely. It's like a friendly
ethical hacker you can use for free.

**Level 2 - How to use it (junior developer):**
Three ways to use ZAP: (1) Set your browser to use ZAP
as a proxy (localhost:8080), browse your app, ZAP passively
scans traffic. (2) Give ZAP a URL, run automated scan.
(3) Use ZAP baseline scan Docker image in CI/CD. Start
with baseline scan in CI/CD - it's safe (non-destructive)
and catches obvious issues.

**Level 3 - How it works (mid-level engineer):**
ZAP's core: HTTP proxy + rules engine. Proxy intercepts
every request/response. Passive rules analyze observed
traffic (no new requests). Active rules send crafted payloads
to discovered endpoints. Rules are implemented as ZAP
plugins. The scan policy determines which rules run and
at what strength. For CI/CD: use ZAP's API or Docker
images (`zap-baseline.py`, `zap-api-scan.py`, `zap-full-scan.py`).
Report format: HTML, XML, JSON. Integrate with Jenkins,
GitHub Actions via parsing exit codes or report files.

**Level 4 - Why it was designed this way (senior/staff):**
DAST (Dynamic Application Security Testing) vs SAST (Static).
SAST analyzes source code: fast, no running app needed,
high false positives, misses runtime issues. DAST tests
the running application: actual behavior tested, fewer
false positives for injection, requires a running target,
misses code-level issues (unused code paths). IAST
(Interactive): instruments the running app to observe
internal state during testing. ZAP covers DAST. Ideal
pipeline: SAST in pre-commit (fast), DAST (ZAP) post-deploy
to staging, periodic full-scope DAST nightly, manual
pentest quarterly. ZAP is open-source and CI/CD friendly
which is why it's often the DAST choice for teams that
can't justify Burp Suite Pro licenses for pipeline use.

**Level 5 - Mastery (distinguished engineer):**
ZAP scripting and custom scan policies allow sophisticated
automated security testing: Zest scripts (record browser
interactions for replay), Selenium integration (drive
real browser for SPA testing), custom active scan rules
(test application-specific business logic). For large
application portfolios: ZAP Automation Framework allows
declarative scan configuration (YAML), parallel scanning,
integration with vulnerability management systems. The
ceiling of DAST: business logic vulnerabilities (IDOR,
authorization flaws) cannot be detected by tool scanning
alone - they require understanding what resources a user
SHOULD and SHOULD NOT be able to access. This requires
human-written test cases (OWASP ASVS-based) executed
against the running app, not just automated scanning.

---

### ⚙️ How It Works (Mechanism)

**ZAP proxy architecture and scan flow:**

```
ZAP ARCHITECTURE:

Browser ←→ ZAP Proxy (localhost:8080) ←→ Target App

                 ┌─────────────────────┐
                 │      ZAP CORE       │
                 │                     │
  Proxy ────────→│   Request Handler   │──→ Target App
                 │   Response Handler  │←── Target App
                 │                     │
                 │   Passive Scanner   │←── All traffic
                 │   (reads only)      │    No new requests
                 │                     │
                 │   Active Scanner    │──→ Sends attack
                 │   (writes attacks)  │    payloads
                 │                     │
                 │   Alert Manager     │
                 │   Report Generator  │
                 └─────────────────────┘

ZAP SCAN SEQUENCE:
  1. Spider discovers URLs
     (HTML spider: follows links, form actions)
     (AJAX spider: runs JS, discovers dynamic content)
  
  2. Passive scanner: analyzes all observed traffic
     Finds: missing headers, cookie issues, info leakage
     No additional requests
  
  3. Active scanner: sends attack payloads
     For each URL + parameter:
       - SQL injection payloads
       - XSS payloads
       - Path traversal payloads
       - And 100+ more
     Analyzes responses for vulnerability signatures
  
  4. Report generated: findings by severity
     HIGH / MEDIUM / LOW / INFORMATIONAL
```

---

### 💻 Code Example

**ZAP in CI/CD pipeline (GitHub Actions):**

```yaml
# .github/workflows/security.yml
# Run ZAP baseline scan against staging after deployment

name: Security Scan

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        # ... deployment steps ...

  zap-scan:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - name: Checkout (for false positive config)
        uses: actions/checkout@v3

      - name: ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.9.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'  # False positive config
          cmd_options: '-a'  # Include alpha passive scan rules
          # fail_action: true  # Fail workflow on HIGH findings
        # Report uploaded as artifact automatically

      - name: Upload ZAP report
        uses: actions/upload-artifact@v3
        if: always()  # Upload even if scan fails
        with:
          name: zap-scan-report
          path: report_html.html

# ZAP false positive configuration (.zap/rules.tsv)
# Format: ruleId\tACTION\tPARAMETER\tEVIDENCE
# 10027	IGNORE	(any)	(any)    # Ignore "Information Disclosure - Debug Errors"
# 10038	IGNORE	(any)	(any)    # Ignore CSP in report-only mode
```

```bash
# Manual ZAP scan using Docker (no install required)

# Baseline scan (passive only, safe for any target)
docker run -t owasp/zap2docker-stable \
  zap-baseline.py \
  -t https://your-app.example.com \
  -r report.html

# Full scan with authentication (aggressive, test env only)
docker run -v $(pwd):/zap/wrk/:rw \
  -t owasp/zap2docker-stable \
  zap-full-scan.py \
  -t https://staging.example.com \
  -g gen.conf \
  -r full-report.html \
  -x report.xml \
  -z "-config replacer.full_list(0).description=auth_token \
      -config replacer.full_list(0).enabled=true \
      -config replacer.full_list(0).matchtype=REQ_HEADER \
      -config replacer.full_list(0).matchstr=Authorization \
      -config replacer.full_list(0).replacement=Bearer_TOKEN"
```

---

### ⚖️ Comparison Table

| Tool | Type | Cost | Best For | CI/CD Fit |
|:---|:---|:---|:---|:---|
| **OWASP ZAP** | DAST | Free, open-source | Automated DAST, learning, CI/CD | Excellent (Docker images) |
| **Burp Suite Community** | DAST (manual) | Free | Manual security testing, learning | Poor (no automation in Community) |
| **Burp Suite Pro** | DAST | $449/year | Professional pentest, automation | Good (Burp API) |
| **Nikto** | DAST | Free | Quick server config checks | Limited |
| **OWASP DAST** | DAST | Free | GitLab CI integration | Good |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| ZAP replaces a penetration test | ZAP automates systematic testing for known vulnerability patterns (OWASP Top 10 coverage is good). It cannot test business logic (IDOR, privilege escalation specific to the application), assess the overall security posture, perform social engineering tests, or understand application-specific attack chains. A full pentest by an experienced human tester uncovers vulnerabilities that ZAP will never find. ZAP is "before the pentest" - catch the obvious issues before spending pentest budget on them. |
| Running ZAP against a site you don't own is fine for learning | Running an active scan (which is what makes ZAP interesting) against any target without explicit written permission is unauthorized access, illegal in most jurisdictions (Computer Fraud and Abuse Act in the US, Computer Misuse Act in the UK, and equivalents globally). Use ONLY: your own applications, intentionally vulnerable apps (DVWA, WebGoat, Juice Shop - designed for ZAP practice), or applications where you have explicit written authorization. |

---

### 🚨 Failure Modes & Diagnosis

**Common ZAP setup and usage issues:**

```bash
# ISSUE: ZAP doesn't see traffic (browser proxy not set)
# Verify ZAP is listening: 
curl -I -x localhost:8080 http://your-app.com
# If connection refused: ZAP not running or wrong port
# If proxied: ZAP is intercepting correctly

# ISSUE: HTTPS not working (certificate error in browser)
# ZAP generates its own CA certificate to intercept HTTPS.
# Install ZAP's CA cert in browser:
#   ZAP → Tools → Options → Dynamic SSL Certificates
#   Export the certificate → Install in browser certificate store
# Without this: browser rejects ZAP's HTTPS interception.

# ISSUE: Active scan too slow or finds nothing in CI/CD
# Tune scan policy for CI/CD:
zap.setActiveScanPolicy(
  enabledPassiveScanners=True,
  enabledActiveScanners=['SQL_INJECTION', 'CROSS_SITE_SCRIPTING'],
  strengthSetting='MEDIUM'  # Low, Medium, High, Insane
)
# Use zap-baseline.py (faster) instead of zap-full-scan.py
# for routine CI/CD. Full scan for nightly/release gates.

# ISSUE: Authenticated endpoints not scanned
# ZAP needs to authenticate to test protected pages.
# Configure via ZAP GUI: Authentication → Form-Based
# Or use script: set cookie/header from test user login
# Verify: check ZAP's Alerts for "Authentication Required" messages
# These indicate ZAP couldn't access authenticated content.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10` - what ZAP tests for
- `SQL Injection, XSS` - specific vulnerabilities ZAP tests

**Builds on this:**
- `Burp Suite Community Intro` - alternative manual tool
- `DAST` - dynamic application security testing in depth
- `Security Testing in CI/CD` - automated DAST pipelines

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MODES        │ Passive: analyze traffic, no attacks      │
│              │ Active: sends attack payloads (test env!) │
│              │ Spider: discovers all URLs                │
├──────────────┼───────────────────────────────────────────┤
│ CI/CD        │ owasp/zap2docker-stable (Docker)          │
│              │ zap-baseline.py (fast, safe, passive+mild)│
│              │ zaproxy/action-baseline (GitHub Actions)  │
├──────────────┼───────────────────────────────────────────┤
│ PROXY PORT   │ localhost:8080 (default)                  │
│ HTTPS SETUP  │ Install ZAP CA cert in browser            │
├──────────────┼───────────────────────────────────────────┤
│ LEGAL        │ ONLY scan apps you own or have explicit   │
│              │ written permission to test.               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ZAP = automated DAST. Sit between browser│
│              │  and app, test HTTP traffic for vulns.    │
│              │  Free. CI/CD compatible. Not a pentest." │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Test from the attacker's perspective, not the developer's."
Developers test that code does what it should. Security
testing checks what happens when code receives input it
shouldn't. DAST tools automate the "send unexpected input
and observe" pattern that security researchers use. This
perspective shift - "what can go wrong?" vs "does this
feature work?" - is the core of security testing. It applies
to manual code review (OWASP Code Review Guide), automated
scanning (ZAP, SAST), and penetration testing. The more
systematically you can automate "what can go wrong?" checks
at each stage of the SDLC, the more secure the output.

---

### 💡 The Surprising Truth

ZAP's most valuable scan mode for teams new to security
is NOT the active scanner (the scary "attack your own app"
mode). It's the passive scanner, run in proxy mode during
normal manual testing by developers. Every time a developer
tests their own feature through ZAP (with the browser
pointing to localhost:8080), ZAP passively scans all
traffic and reports: "Your login response sets a cookie
without the HttpOnly flag" or "Your API response doesn't
have a Content-Security-Policy header." Zero additional
effort from the developer - they're doing normal manual
testing, and ZAP provides security observations for free.
This passive scanning during development workflow catches
security issues at the exact moment they're most cheap
to fix (during development, not post-production).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the difference between passive and active
   scanning and when each is appropriate.
2. **SET UP** ZAP as a browser proxy, browse through your
   application, and interpret the passive scan findings.
3. **RUN** ZAP baseline scan via Docker in a CI/CD pipeline
   and configure it to fail on high-severity findings.
4. **EXPLAIN** ZAP's limitations: why automated scanning
   doesn't replace manual security testing or pen testing.

---

### 🎯 Interview Deep-Dive

**Q: How would you integrate security testing into a CI/CD pipeline?**

*Why they ask:* DevSecOps capability question. Tests whether
candidate can shift security left without stopping delivery.

*Strong answer includes:*
- Multi-stage approach:
  Pre-commit: SAST (Semgrep, SonarQube) in IDE/pre-commit hook.
  Fast feedback, no false positives from running code.
  CI/CD: SCA dependency scanning (Snyk, Dependabot) on every PR.
  Post-deploy to staging: DAST (ZAP baseline scan).
  Non-destructive, fast (2-5 min), catches runtime issues.
  Nightly: Full DAST scan with authenticated testing.
  Catches deeper issues without slowing CI.
  Release gate: manual security review for high-risk changes.
- ZAP specifically: Docker image, zap-baseline.py, exit codes
  for pass/fail. False positive management via rules.tsv.
- Balance: automated security gates must not be so strict
  they block all deployments. Start with "block on HIGH only,"
  tune based on false positive rate.
- Tool stack: Semgrep (SAST) + Snyk (SCA) + ZAP (DAST) covers
  most automated security testing needs with all free tiers.