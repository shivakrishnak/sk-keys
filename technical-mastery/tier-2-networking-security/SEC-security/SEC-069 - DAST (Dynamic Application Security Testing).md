---
id: SEC-069
title: "DAST (Dynamic Application Security Testing)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★★
depends_on: SEC-001, SEC-013, SEC-016, SEC-041, SEC-055, SEC-068, SEC-077
used_by: SEC-078, SEC-105, SEC-115, SEC-129
related: SEC-001, SEC-013, SEC-016, SEC-041, SEC-055, SEC-068, SEC-077, SEC-078
tags:
  - security
  - dast
  - dynamic-testing
  - zap
  - owasp-zap
  - penetration-testing
  - black-box-testing
  - devsecops
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 69
permalink: /technical-mastery/sec/dast-dynamic-security-testing/
---

⚡ TL;DR - DAST (Dynamic Application Security Testing) tests a
running application by sending crafted HTTP requests and analyzing
responses for security vulnerabilities. Unlike SAST (which reads code),
DAST sees what the application actually does at runtime - including
misconfigured server headers, exposed admin panels, and authentication
bypass. Primary tool: OWASP ZAP (open-source). ZAP in CI: use the
Automation Framework, not the legacy Spider + Active Scan combo.
Best suited for: finding OWASP A05 misconfigurations, authentication
issues, and injection vulnerabilities that only manifest at runtime.

---

| #069 | Category: Security | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Input Validation, Security Code Review, OWASP Workshop, SAST, Security Testing in CI/CD | |
| **Used by:** | Pentest Methodology, SAST in CI/CD, DevSecOps Pipeline Design, SSDLC | |
| **Related:** | SAST, SCA, Pentest, OWASP ZAP, Burp Suite | |

---

### 🔥 The Problem This Solves

**WHY DAST EXISTS (and what SAST misses):**

```
SAST vs DAST - COMPLEMENTARY, NOT COMPETING

THINGS SAST CANNOT FIND:
  1. Server misconfiguration:
     Is the server returning X-Content-Type-Options: nosniff?
     Is HTTPS enforced? Is HTTP/2 enabled?
     SAST: reads code. Cannot see server configuration at runtime.
     DAST: sends a request, reads the response headers.
  
  2. Authentication bypass via parameter tampering:
     Can I set role=admin in a cookie and get admin access?
     SAST: would need to trace all request parameter flows to auth logic.
         This is context-dependent and complex.
     DAST: sends request with role=admin, sees if it gets admin response.
  
  3. Session management issues:
     Is the session ID random enough? Does logout invalidate the session?
     Can I reuse a session cookie after password change?
     SAST: cannot tell - randomness and session state are runtime properties.
     DAST: captures session IDs, measures entropy, attempts replays.
  
  4. Exposed sensitive endpoints not visible in code:
     /actuator/heapdump (Spring Boot exposed debug endpoint)
     /.git/config (version control file exposed via web server)
     /phpinfo.php (debug file left on server)
     SAST: scans application code. Web server serving static files
           or misconfigured paths are not in the application code.
     DAST: brute-forces common paths, finds exposed endpoints.
  
  5. Third-party component vulnerabilities at runtime:
     A CDN-loaded JavaScript library with known XSS.
     SAST: scans your code, not CDN-loaded content.
     DAST: executes the page, sees all loaded content.

THINGS DAST FINDS THAT COMPLEMENT SAST:
  - Reflected XSS (sends payloads, sees if they reflect in response)
  - SQL injection with runtime-visible error messages
  - SSRF (sends probe URLs, checks for callbacks)
  - Open redirects (follows redirects, checks final destination)
  - Exposed debug endpoints, admin panels
  - Missing security headers (CSP, HSTS, X-Frame-Options)
  - CORS misconfiguration (sends cross-origin requests, sees permissions)
  - Insecure cookie attributes (HttpOnly, Secure, SameSite)

WHAT NEITHER SAST NOR DAST FINDS:
  - Business logic vulnerabilities (specific to your app's logic)
  - IDOR (Insecure Direct Object Reference) that requires user context
  - Privilege escalation across user roles (requires authenticated testing)
  These require manual penetration testing with real user accounts.
```

---

### 📘 Textbook Definition

**DAST (Dynamic Application Security Testing):** Testing a running
application by interacting with it externally - sending HTTP requests,
analyzing responses, and probing for security vulnerabilities without
access to the source code. "Black box" testing from the attacker's
perspective.

**Active scan:** DAST sends attack payloads (SQL injection strings,
XSS vectors, path traversal sequences) to every endpoint and parameter,
then analyzes responses for signs of vulnerability.

**Passive scan:** DAST intercepts legitimate application traffic (proxied
or mirrored) and analyzes it for security issues without sending
additional attack traffic. Safer for production; less comprehensive.

**Authenticated DAST:** Running the active scanner with a valid session
token. This discovers vulnerabilities in authenticated functionality,
not just public-facing endpoints. Critical for finding vulnerabilities
in the 80% of an application that's behind a login.

**OWASP ZAP (Zed Attack Proxy):** The leading open-source DAST tool.
Features: intercepting proxy, spider/crawler, active scanner, passive
scanner, Automation Framework for CI/CD.

**Burp Suite:** The professional standard for DAST and manual pentesting.
Burp Pro required for the active scanner and automation features.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DAST is a robot that attacks your running application the way
a hacker would - sending malicious inputs to every endpoint and
watching for vulnerabilities in the responses. It sees the app
as an attacker would: no source code, just HTTP traffic.

**One analogy:**
> SAST is like a building code inspector who reads the blueprints.
> DAST is like a burglar who actually tries every door and window.
>
> The inspector reads the plans: "The fire door specs look correct."
> The burglar tries the door: "It opens without a key."
>
> The plans may show everything correctly; the actual building
> (runtime behavior) may behave differently.
>
> DAST sends actual attack payloads to your actual running application.
> What the application ACTUALLY DOES matters more than what the code
> THEORETICALLY SHOULD DO. Runtime behavior catches:
> - Misconfigured middleware
> - Third-party components not in your source
> - Deployment-specific issues
> - Server configuration problems

---

### 🔩 First Principles Explanation

**OWASP ZAP in CI/CD using the Automation Framework:**

```
DAST SCAN TYPES:

1. SPIDER/CRAWLER:
   ZAP discovers all application endpoints by crawling links,
   forms, JavaScript, and API schemas.
   
   Modern: Ajax Spider (executes JavaScript, discovers SPA routes)
   Classical: Spider (HTML links only - misses JavaScript-rendered content)

2. PASSIVE SCAN:
   Analyzes traffic as-is. No attack payloads.
   Finds: missing headers, insecure cookies, information disclosure.
   Safe for production (just observes, doesn't attack).

3. ACTIVE SCAN:
   Sends attack payloads to every parameter of every discovered endpoint.
   Attack vectors: SQLi, XSS, path traversal, SSRF, command injection, XXE.
   NOT SAFE FOR PRODUCTION: can trigger SQL errors, create test data,
   cause unexpected behavior.
   Run in: test environment, staging.

ZAP AUTOMATION FRAMEWORK (recommended for CI/CD):

  Legacy approach (avoid):
    # Old, limited, hard to configure:
    zap.sh -quickurl http://localhost:8080 -quickprogress
    
  Modern approach - Automation Framework (YAML-based):
    # zap-automation.yml
    ---
    env:
      contexts:
        - name: "App Context"
          urls:
            - http://localhost:8080
          authentication:
            method: form
            parameters:
              loginUrl: http://localhost:8080/api/login
              loginRequestBody: '{"username":"{%username%}","password":"{%password%}"}'
            verification:
              method: response
              loggedInRegex: '"token":'
          users:
            - name: "test-user"
              credentials:
                username: testuser@example.com
                password: TestPass123!
    
    jobs:
      - type: spider
        name: "Spider"
        parameters:
          context: "App Context"
          user: "test-user"
          maxDuration: 2
          acceptCookies: true
      
      - type: passiveScan-wait
        name: "Passive Scan"
        parameters:
          maxDuration: 5
      
      - type: activeScan
        name: "Active Scan"
        parameters:
          context: "App Context"
          user: "test-user"
          maxRuleDurationInMins: 1
          policy: "API-Scan"  # Reduced scan policy for speed
      
      - type: report
        name: "Report"
        parameters:
          reportDir: /zap/reports
          reportFile: zap-report
          template: risk-confidence-html  # or sarif, json
          reportTitle: "DAST Scan Report"
```

---

### 🧪 Thought Experiment

**SCENARIO: Authenticated DAST for a REST API**

```
CHALLENGE: Most DAST tools scan public-facing URLs only.
90% of application functionality is behind authentication.
Unauthenticated DAST coverage: ~10% of attack surface.

AUTHENTICATED DAST APPROACHES:

Approach 1: ZAP form authentication
  ZAP logs in via the login form, maintains session cookies.
  Coverage: all authenticated pages ZAP discovers.
  
  Limitation: JWT-based APIs are not "form" authenticated.

Approach 2: ZAP HTTP token authentication
  ZAP: send Authorization: Bearer <token> on every request.
  
  Step 1: Obtain JWT token via test user credentials.
  Step 2: Configure ZAP to add the token header.
  
  In GitHub Actions:
    # Get JWT token
    TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","password":"TestPass123!"}' \
      | jq -r .token)
    
    # Run ZAP with the token
    docker run --network=host \
      -v $(pwd)/zap:/zap/wrk/:rw \
      ghcr.io/zaproxy/zaproxy:stable \
      zap-api-scan.py \
        -t http://localhost:8080/api/openapi.json \
        -f openapi \
        -r report.html \
        -D "Authorization=Bearer $TOKEN"

Approach 3: OpenAPI/Swagger-driven scan
  If your API has an OpenAPI spec: ZAP uses it to discover ALL endpoints,
  not just the ones it finds by crawling.
  
  Advantage: comprehensive coverage (DAST covers every documented endpoint).
  
  zap-api-scan.py:
    Designed for REST APIs with OpenAPI/Swagger/GraphQL schemas.
    Much better for modern APIs than the web spider approach.
  
  Command:
    docker run --network=host ghcr.io/zaproxy/zaproxy:stable \
      zap-api-scan.py \
        -t http://localhost:8080/api/openapi.json \
        -f openapi \
        -r report.html \
        -x report.xml
  
  Findings are linked to specific API endpoints in the OpenAPI spec.

GITHUB ACTIONS: DAST ON EVERY PR

  jobs:
    dast:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        
        - name: Start application
          run: docker-compose up -d
        
        - name: Wait for app to be ready
          run: |
            timeout 60 bash -c 'until curl -s http://localhost:8080/health; do sleep 2; done'
        
        - name: OWASP ZAP API Scan
          uses: zaproxy/action-api-scan@v0.7.0
          with:
            target: 'http://localhost:8080/api/openapi.json'
            format: openapi
            fail_action: true  # Fail CI on HIGH findings
            allow_issue_writing: true  # Create GitHub Issues for findings
            rules_file_name: '.zap/rules.tsv'  # Override specific rules
        
        - name: Upload ZAP Report
          uses: actions/upload-artifact@v4
          if: always()
          with:
            name: zap-report
            path: report_html.html

MANAGING DAST FALSE POSITIVES (ZAP rule overrides):
  
  # .zap/rules.tsv (disable noisy rules):
  10015  IGNORE  (Incomplete or No Cache-Control Header Set - accept for APIs)
  10096  IGNORE  (Timestamp Disclosure - expected in API responses)
  10021  IGNORE  (X-Content-Type-Options Header Missing - set at load balancer)
```

---

### 🧠 Mental Model / Analogy

> DAST is like hiring a professional burglar to test your building's security.
>
> The burglar doesn't read blueprints (source code).
> They walk up to the building (your running application).
> They try every door handle (every endpoint).
> They test window latches (every parameter).
> They check if the alarm triggers (security headers).
> They look for a key under the doormat (/admin?debug=true).
>
> They find:
> - The back door was left unlocked (exposed admin endpoint).
> - One window has no latch (missing authentication on /api/internal).
> - The alarm doesn't cover the garage (missing X-Frame-Options header).
>
> None of these would be visible from the blueprints alone.
> The building code was correct. The physical implementation was not.
>
> DAST provides the "physical implementation" perspective.
> SAST provides the "blueprint review" perspective.
> You need both.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
DAST tools automatically attack a running web application to find security bugs. They try SQL injection in every form field, look for XSS in every output, check if security headers are present, and try to access admin areas. They work like an automated penetration tester checking the most common vulnerabilities. OWASP ZAP is the free, open-source standard.

**Level 2 - How to use it (junior developer):**
Use `zap-api-scan.py` with your OpenAPI spec for REST APIs. Start the application in your CI environment, then run ZAP against it. Use `zaproxy/action-api-scan` GitHub Action for easy setup. Review findings by severity (HIGH first). Use `.zap/rules.tsv` to suppress false positives. Ensure you run against a TEST environment, not production.

**Level 3 - How it works (mid-level engineer):**
ZAP's active scanner works by: (1) crawling/spidering all endpoints (or reading an OpenAPI spec), (2) for each endpoint: identifying all parameters (URL, form, cookie, header), (3) for each parameter: inserting attack vectors from each attack category (SQLi, XSS, path traversal, etc.), (4) analyzing HTTP responses for signatures of vulnerability (SQL error message in response, XSS payload reflected, time delay for blind SQLi). Authentication is handled by maintaining a session cookie or Authorization header across all requests. ZAP's passive scanner only analyzes traffic without injecting - safe for production monitoring of traffic.

**Level 4 - Why it was designed this way (senior/staff):**
DAST was the original application security testing approach (black-box testing, like real attackers). SAST was developed later as a way to find vulnerabilities earlier (code analysis). The shift-left movement elevated SAST. But DAST remained necessary because it tests the actual deployed application - all layers: web server, application framework, business logic, and infrastructure together. Modern DAST tools integrate with OpenAPI/Swagger schemas to provide comprehensive endpoint coverage (older tools relied on crawling, which missed API endpoints not linked from HTML). The ZAP Automation Framework replaced the older API in 2022 to provide proper YAML-based configuration for CI/CD, addressing the CI integration complexity that was a major barrier to DAST adoption.

**Level 5 - Mastery (distinguished engineer):**
Advanced DAST: IAST (Interactive Application Security Testing) combines DAST and SAST by instrumenting the application at runtime. A SAST agent embedded in the application watches all code paths exercised by DAST traffic. When DAST sends a SQL injection payload: the IAST agent reports the exact code path, parameter, and query that was affected (not just "SQL injection found at endpoint X"). Tools: Contrast Security, Seeker. IAST reduces false positives significantly but requires language-specific agents. At scale: DAST in CI must run in a dedicated environment (not shared with production). Data isolation: DAST will create test data, send payloads that may trigger business logic (cancellations, orders). CI DAST environment needs a clean database reset between runs. API rate limiting: DAST active scans can trigger DDoS-like traffic patterns; exclude DAST environment from rate limiting rules (or add to bypass list).

---

### ⚙️ How It Works (Mechanism)

```
DAST ACTIVE SCAN PROCESS:

1. DISCOVERY (Spider/OpenAPI):
   Crawler: GET /
   → finds links: /about, /login, /api/users, /api/orders
   → JavaScript spider: executes page, finds AJAX calls
   → OpenAPI spec: reads all endpoints from /openapi.json
   
   Endpoint inventory:
   GET  /api/users/{id}
   POST /api/orders
   PUT  /api/orders/{id}
   DELETE /api/orders/{id}

2. PARAMETER IDENTIFICATION:
   For GET /api/users/{id}:
   Parameters: id (URL path), Authorization (header), token (cookie)
   
   For POST /api/orders:
   Parameters: userId, productId, quantity (JSON body), Authorization (header)

3. ATTACK PAYLOAD INJECTION (per parameter, per attack type):
   Injection attack on POST /api/orders.userId:
   
   Normal: POST /api/orders {"userId": "123", ...}
   SQLi test: POST /api/orders {"userId": "123' OR '1'='1", ...}
   SQLi test: POST /api/orders {"userId": "1; DROP TABLE orders--", ...}
   XSS test:  POST /api/orders {"userId": "<script>alert(1)</script>", ...}
   (Hundreds of payloads per parameter)

4. RESPONSE ANALYSIS:
   SQLi detection:
   - SQL error messages in response body
   - Response time significantly different (blind SQLi time-based)
   - Different row counts than expected (boolean-based SQLi)
   
   XSS detection:
   - Payload reflected unescaped in response body
   - <script> tag appears in response HTML

5. REPORTING:
   Finding: SQL Injection in POST /api/orders.userId
   Evidence: "You have an error in your SQL syntax..."
   Severity: HIGH
   CWE: CWE-89
   OWASP: A03:2021
```

```mermaid
flowchart TD
    A[Start App in Test Environment] --> B[ZAP: Discover Endpoints]
    B --> C{Discovery method?}
    C -->|OpenAPI spec| D[Read all endpoints from spec]
    C -->|Spider| E[Crawl HTML links + JavaScript]
    D --> F[Parameter Identification]
    E --> F
    F --> G[Active Scan: Inject Payloads]
    G --> H{Response Analysis}
    H -->|SQL error in response| I[HIGH: SQL Injection]
    H -->|Payload reflected unescaped| J[HIGH: XSS]
    H -->|Missing header| K[LOW/MED: Misconfiguration]
    H -->|No vulnerability| L[Pass]
    I --> M[SARIF Report to GitHub Security]
    J --> M
    K --> M
```

---

### 💻 Code Example

**Complete ZAP DAST GitHub Actions workflow:**

```yaml
# .github/workflows/dast.yml
name: DAST Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Nightly full scan

jobs:
  dast:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: appdb
        ports: ["5432:5432"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and start application
        run: |
          docker build -t myapp:test .
          docker run -d -p 8080:8080 \
            -e DATABASE_URL=postgresql://postgres:testpassword@localhost/appdb \
            -e JWT_SECRET=test-only-secret \
            myapp:test
      
      - name: Wait for application startup
        run: |
          timeout 60 bash -c '
            until curl -sf http://localhost:8080/actuator/health; do
              echo "Waiting for app..." && sleep 3
            done
          '
      
      # Lightweight API scan (fast, for every PR)
      - name: OWASP ZAP API Scan (OpenAPI)
        uses: zaproxy/action-api-scan@v0.7.0
        with:
          target: 'http://localhost:8080/v3/api-docs'  # Springdoc OpenAPI
          format: openapi
          fail_action: true  # Fail CI on HIGH findings
          rules_file_name: '.zap/rules.tsv'
        
      - name: Upload ZAP HTML Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: dast-report-${{ github.run_number }}
          path: report_html.html

# .zap/rules.tsv - Suppress false positives:
# ID    Action   Reason
# 10015 IGNORE   Cache-Control missing: acceptable for REST API
# 10021 IGNORE   X-Content-Type: set at nginx level, not app
```

---

### ⚖️ Comparison Table

| Aspect | SAST | DAST | IAST |
|:---|:---|:---|:---|
| **Source** | Source code | Running application | Instrumented runtime |
| **Timing** | Build time | Test/staging | Test with runtime agent |
| **False positive rate** | Higher | Medium | Low |
| **Business logic** | Limited | Limited | Good (sees code path) |
| **Authentication** | N/A | Complex setup | Built-in |
| **Production safe** | Yes | No (active scan) | Yes (passive) |
| **Best for** | Known patterns, code review | Misconfigurations, runtime | Authenticated, complex apps |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "DAST finds everything because it tests the real application." | DAST tests only what it can reach. An API endpoint that requires specific parameters DAST doesn't know about (undocumented, non-linked) may not be tested. DAST with OpenAPI spec coverage is better but still misses: (1) business logic vulnerabilities (price manipulation, workflow bypass), (2) IDOR (requires knowledge of different users' object IDs), (3) privilege escalation across user roles (requires multiple accounts and complex test logic). DAST + SAST together cover more; a human penetration test is still needed for complete coverage. "DAST tested the running app" doesn't mean the app is secure. |
| "ZAP active scan in CI will slow down the pipeline too much." | A ZAP API scan against an API with an OpenAPI spec typically completes in 5-15 minutes depending on the number of endpoints and the scan policy. Using ZAP's "API-Scan" policy (pre-configured for speed) rather than the full active scan policy reduces time significantly. Additionally: run SAST on every PR (fast: 1-3 min), DAST nightly (15 min is acceptable), full penetration test quarterly. Not every scan type needs to run on every commit. The GitHub Actions `on: schedule` cron syntax allows nightly DAST without blocking every PR. |

---

### 🚨 Failure Modes & Diagnosis

**Common DAST integration problems:**

```
PROBLEM 1: DAST can't discover endpoints (SPA or JWT API)
  
  Symptom: ZAP spider finds 5 endpoints; your app has 200.
  
  Fix: Provide OpenAPI spec for REST APIs.
       Use AJAX Spider for SPA (executes JavaScript).
       Provide authentication token for authenticated scanning.
  
  Command for OpenAPI-driven scan:
    zap-api-scan.py -t http://localhost:8080/openapi.json -f openapi

PROBLEM 2: Authentication fails during DAST
  
  Symptom: All findings say "Unauthenticated" or test endpoints return 401.
  
  Fix:
    Obtain a test JWT before running DAST:
      TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
        -d '{"user":"tester","pass":"Test123!"}' | jq -r .token)
    
    Pass token to ZAP:
      docker run ... ghcr.io/zaproxy/zaproxy:stable \
        zap-api-scan.py ... \
        -D "Authorization=Bearer $TOKEN"

PROBLEM 3: DAST creates side effects in the test database
  
  Symptom: After DAST run, database has garbage data;
  subsequent test runs fail.
  
  Fix:
    Use a fresh database for each DAST run.
    Docker: stop and recreate the DB container after DAST.
    Or: run DAST against a read-only snapshot.
    Or: use database transaction rollback after each DAST request
        (complex, requires app modification).

PROBLEM 4: Too many false positives on INFO/LOW findings
  
  Symptom: DAST report has 200 findings, most are LOW severity noise.
  
  Fix:
    Focus on HIGH and MEDIUM findings.
    Suppress known false positives in .zap/rules.tsv:
      10015  IGNORE  Cache-Control missing - acceptable for JSON APIs
    Use SARIF output + GitHub Security Alerts:
      Only MEDIUM+ findings create GitHub Security Alerts.
      INFO/LOW findings are visible in the report but don't clutter alerts.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `SAST` - static analysis counterpart
- `OWASP Top 10` - what DAST finds
- `Security Testing in CI/CD` - integration context

**Builds on this:**
- `Pentest Methodology` - DAST as automated component of pentesting
- `DevSecOps Pipeline Design` - DAST in the full pipeline
- `SAST in CI/CD` - combined SAST+DAST pipeline

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PRIMARY TOOL │ OWASP ZAP (free), Burp Suite Pro (paid)  │
├──────────────┼───────────────────────────────────────────┤
│ SAST vs DAST │ SAST: read code; DAST: attack running app │
├──────────────┼───────────────────────────────────────────┤
│ API SCAN     │ zap-api-scan.py -t openapi.json -f openapi│
│ CI ACTION    │ zaproxy/action-api-scan@v0.7.0            │
├──────────────┼───────────────────────────────────────────┤
│ TIMING       │ Active scan: TEST only (not production)   │
│              │ Passive scan: production-safe              │
├──────────────┼───────────────────────────────────────────┤
│ FINDS        │ Missing headers, exposed endpoints,       │
│              │ SQLi, XSS, SSRF (at runtime)              │
│ MISSES       │ Business logic, IDOR, complex auth flows  │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Test at the system boundary, not just the component level."
DAST tests the entire deployed system: web server + application
framework + business logic + database + infrastructure together.
SAST tests the application code in isolation.
Integration testing tests component interactions.
Unit tests test individual functions.
Each level catches different bugs. Bugs that only manifest at
the system boundary (server misconfiguration, middleware behavior,
combined component interactions) are invisible to lower-level tests.
The same principle in non-security testing:
- Unit test: function returns correct value with valid input.
- Integration test: function + database interaction works correctly.
- End-to-end test: user can complete the full workflow in the browser.
- Load test: the system handles expected concurrent user volume.
- Security DAST: the deployed system behaves securely under attack.
No single testing level subsumes another. Each catches failures
that other levels miss. A comprehensive testing strategy includes
all levels, proportionate to the risk and cost of each.

---

### 💡 The Surprising Truth

OWASP ZAP was born from a fork of Paros Proxy in 2010, created
by Psiinon (Simon Bennetts) who wanted to make web application
security testing accessible to developers, not just security
experts. Within a decade, ZAP became the most widely used DAST
tool in the world - partly because it was free and open-source,
and partly because OWASP gave it community credibility.
The surprising thing: despite ZAP's widespread use in CI/CD
pipelines globally, most organizations using it are scanning
less than 30% of their actual attack surface in CI.
The problem: DAST in CI is usually configured to scan the
unauthenticated surface (login page, public endpoints) because
setting up authentication is complex. The authenticated attack
surface (everything behind login) is 80% of a typical application.
So most CI DAST scans are testing the 20% that attackers need
to pass through to reach the 80%.
The fix is technical (authenticated scanning via OpenAPI + JWT),
but it requires investment in test user management and API spec
maintenance. Organizations that invest in authenticated DAST
find dramatically more vulnerabilities in CI than those running
unauthenticated scans.
ZAP's new Automation Framework was released specifically to make
authenticated API scanning more accessible - addressing the main
barrier to effective CI DAST coverage.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DIFFERENTIATE** SAST vs DAST: what each finds, what each misses,
   when to use each (and why you need both).
2. **CONFIGURE** an authenticated ZAP API scan in GitHub Actions using
   `zaproxy/action-api-scan` with an OpenAPI spec and JWT token.
3. **MANAGE** ZAP findings: suppress false positives in `.zap/rules.tsv`,
   upload SARIF reports to GitHub Security, fail CI only on HIGH severity.
4. **EXPLAIN** IAST: how it combines DAST and SAST via runtime instrumentation,
   and when it's preferable.

---

### 🎯 Interview Deep-Dive

**Q: What is DAST? How does it differ from SAST? How do you integrate
it in a CI/CD pipeline?**

*Why they ask:* DevSecOps knowledge. Tests whether candidate knows
when to use SAST vs DAST, not just what they are.

*Strong answer covers:*
- SAST: reads source code, finds patterns (SQL concat, dangerous functions).
  No execution. Fast, finds issues during development.
- DAST: attacks the running application, finds runtime issues.
  Execution-based. Finds: server misconfigurations, auth bypass, runtime injection.
- What SAST misses: server configs, middleware behavior, third-party components.
  What DAST misses: code patterns, hardcoded secrets.
  What both miss: business logic, IDOR.
- Integration: use OpenAPI spec for comprehensive endpoint coverage.
  Run in test environment (not production - active scan can corrupt data).
  Authenticated scan: obtain JWT token before ZAP run, pass via header.
  Use `zaproxy/action-api-scan` GitHub Action. SARIF output to GitHub Security.
  Fail CI on HIGH findings. Suppress false positives in rules.tsv.
- Timing: SAST on every PR (fast), DAST nightly (more time-consuming).
  IAST if need authenticated+code-path coverage.
- OWASP ZAP free/open-source. Burp Suite Pro for manual pentesting. 
  ZAP Automation Framework for CI/CD (replaces older ZAP API).