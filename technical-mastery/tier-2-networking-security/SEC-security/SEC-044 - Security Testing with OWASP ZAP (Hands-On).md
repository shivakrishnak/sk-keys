---
id: SEC-044
title: "Security Testing with OWASP ZAP (Hands-On)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-014, SEC-016, SEC-040, SEC-041
used_by: SEC-063, SEC-064, SEC-077, SEC-100
related: SEC-001, SEC-014, SEC-016, SEC-040, SEC-041, SEC-063, SEC-064
tags:
  - security
  - zap
  - dast
  - security-testing
  - owasp
  - dynamic-analysis
  - penetration-testing
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/sec/security-testing-zap-hands-on/
---

⚡ TL;DR - OWASP ZAP (Zed Attack Proxy) is a DAST (Dynamic
Application Security Testing) tool: it sends real HTTP requests
to your running application and finds vulnerabilities by
observing how the application responds. Unlike SAST (which
reads source code), ZAP sees what attackers see: the live,
running application.

**Five-minute ZAP quickstart:**
```bash
# Pull ZAP Docker image
docker pull ghcr.io/zaproxy/zaproxy:stable

# Baseline scan: passive + limited active, 60 second limit
docker run --rm ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
  -t https://your-app.example.com \
  -r zap_report.html

# Full scan: complete active scanning (much longer)
docker run --rm ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py \
  -t https://your-app.example.com \
  -r zap_full_report.html
```

**What ZAP finds:** missing security headers, XSS, SQL injection,
CSRF issues, insecure cookies, directory traversal, XXE,
path disclosure, and hundreds of other vulnerability types.

---

| #044 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, XSS Prevention, SQL Injection Prevention, API Security, Security Code Review | |
| **Used by:** | DAST, Security Testing in CI/CD, Advanced SAST/DAST, Pentest Methodology | |
| **Related:** | SAST, DAST, Penetration Testing, Burp Suite, Security Headers | |

---

### 🔥 The Problem This Solves

**THE GAP BETWEEN CODE REVIEW AND RUNTIME BEHAVIOR:**
A security code review may flag: "this input is not validated."
But it cannot tell you:
- Is the application actually exploitable in the running environment?
- Are security headers actually set (not just in code, but being served)?
- Is the WAF intercepting the attack before it reaches the code?
- Does this configuration actually work in the deployed infrastructure?

SAST (code analysis) misses:
- Infrastructure misconfigurations (nginx, Apache, load balancer)
- Third-party integrations with different security postures
- Runtime behavior differences from code behavior
- Authentication bypass that only manifests with real HTTP traffic
- Security headers set in nginx (not in code, invisible to SAST)

**ZAP (DAST) finds these issues because it interacts with the
running application exactly as an attacker would:**
- Real HTTP requests hitting the actual deployed server
- Sees the full HTTP response including all headers
- Tests how the application handles malformed input at runtime
- Works without access to source code

---

### 📘 Textbook Definition

**DAST (Dynamic Application Security Testing):** Security testing
methodology that tests the application from the outside while
it is running. Sends crafted HTTP requests and analyzes responses
to identify vulnerabilities. Does not require source code access.

**OWASP ZAP (Zed Attack Proxy):** Free, open-source DAST tool
maintained by the OWASP foundation. Industry standard for
automated web application security testing. Available as:
GUI application, command-line tool, Docker container, and CI/CD integration.

**Passive Scanning:** ZAP observes traffic and identifies issues
without sending additional requests. Identifies: missing security
headers, insecure cookie configuration, information disclosure
in responses, HTTPS issues. Low risk: cannot cause side effects.

**Active Scanning:** ZAP sends crafted attack payloads to test
for specific vulnerabilities (XSS, SQL injection, command
injection, path traversal). Can cause side effects: creates
test data, may trigger account lockouts, could disrupt
unstable applications. Do NOT run active scans against
production without explicit authorization.

**Spider:** ZAP's crawler that discovers application pages,
forms, endpoints, and parameters by following links and
submitting forms. Required before scanning: ZAP must know
what to scan.

**ZAP vs Burp Suite:**
- ZAP: free, open-source, CLI/Docker for CI/CD, community-supported
- Burp Suite: commercial ($499/yr professional), more powerful
  active scanner, better for manual penetration testing,
  industry standard for professional pentesters

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ZAP is a proxy that sits between your browser and your
application, captures all traffic, then replays it with
thousands of attack variations to find security vulnerabilities.
Think of it as a robot penetration tester.

**One analogy:**
> ZAP is like a quality assurance robot for a lock factory.
> The factory produces locks (your application). The robot
> (ZAP) takes each lock (each endpoint) and tries thousands
> of lock-picking techniques: standard picks, specialty picks,
> bump keys, rakes, tension variations. Most techniques fail
> (the lock holds). Some succeed (a vulnerability is found).
> The robot compiles a report: "Lock model B-42 failed to pick
> technique #127 (SQL injection via login form)." The factory
> (development team) uses this report to improve the lock
> (fix the vulnerability). The robot does what a human
> lock-picker would do, but faster and more systematically
> across the entire product line.

---

### 🔩 First Principles Explanation

**ZAP's testing approach:**

```
ZAP SCAN WORKFLOW:

PHASE 1: Spider (Discovery)
  ZAP crawls the application to find all pages/endpoints:
    - Follow links in HTML
    - Submit forms
    - Parse JavaScript for fetch()/XMLHttpRequest() calls
    - Parse sitemap.xml and robots.txt
    - Try common paths (/admin, /api, /login, /register)
  
  OUTPUT: List of URLs, forms, parameters to test.
  
  LIMITATION: ZAP's spider cannot fully explore modern SPAs
  (Single Page Applications) that use JavaScript routing.
  FIX: Use ZAP's AJAX spider (runs Selenium headless browser)
  or manually drive the application through ZAP proxy first.

PHASE 2: Passive Scan (Zero-Risk Analysis)
  ZAP analyzes all captured responses WITHOUT sending additional requests.
  Finds issues visible in any response:
  
  MISSING HEADERS (check for absence):
    Content-Security-Policy: not present → XSS second-layer defense missing
    X-Frame-Options: not present → clickjacking possible
    Strict-Transport-Security: not present → downgrade attacks possible
    X-Content-Type-Options: nosniff not present → MIME sniffing possible
  
  INSECURE COOKIES:
    Set-Cookie: session=abc123 (missing Secure, HttpOnly, SameSite attributes)
  
  INFORMATION DISCLOSURE:
    Server: Apache/2.4.51 (version disclosed in header)
    X-Powered-By: PHP/8.1.2 (version disclosed)
    <!-- TODO: remove this debug code before production --> (HTML comment)
  
  MIXED CONTENT:
    HTTPS page loading HTTP resources (images, scripts, stylesheets)

PHASE 3: Active Scan (Attack Testing)
  ZAP sends crafted attack payloads and analyzes responses.
  
  FOR EACH PARAMETER IN EACH ENDPOINT:
  
  SQL Injection tests:
    Original: GET /search?q=shoes
    Modified: GET /search?q=shoes'
    Modified: GET /search?q=shoes' OR '1'='1
    Modified: GET /search?q=shoes; DROP TABLE products--
    Analysis: Does response change? Does error message appear?
  
  XSS tests:
    Original: GET /search?q=shoes
    Modified: GET /search?q=<script>alert(1)</script>
    Modified: GET /search?q="><img src=x onerror=alert(1)>
    Analysis: Does the payload appear unencoded in the response HTML?
  
  Path traversal tests:
    Modified: GET /file?name=../../../etc/passwd
    Modified: GET /file?name=%2e%2e%2f%2e%2e%2fetc%2fpasswd
    Analysis: Does the response contain /etc/passwd content?
  
  ... hundreds of other test types ...
  
  RISK LEVELS of findings:
    HIGH: Likely exploitable, significant impact
    MEDIUM: Potentially exploitable, investigation needed
    LOW: Minor issue or defense-in-depth improvement
    INFORMATIONAL: Not a vulnerability, but noteworthy

PHASE 4: Report Generation
  Findings listed with:
    - Vulnerability name
    - Risk level (High/Medium/Low/Info)
    - URL and parameter affected
    - Evidence (what ZAP actually observed)
    - Solution (recommended fix)
    - OWASP reference
  
  FALSE POSITIVE RATE: Active scanners produce false positives.
  Every HIGH and MEDIUM finding needs manual verification.
  "ZAP reported XSS at /search?q=" must be manually confirmed:
    Does the payload actually execute in a real browser?
    Is there a WAF blocking the attack in production?
```

---

### 🧪 Thought Experiment

**SCENARIO: Integrating ZAP into a CI/CD pipeline**

```
OBJECTIVE: Block deploys with HIGH-risk security findings.
  Don't alert on every informational finding (too noisy).

GITHUB ACTIONS WORKFLOW:

name: Security DAST Scan
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # Weekly full scan on Monday 2am

jobs:
  zap-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy staging environment
        run: |
          # Deploy to staging (not production)
          ./deploy-staging.sh
          # Wait for app to be ready
          sleep 30

      - name: ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.10.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'  # Include alpha rules
        # action-baseline fails the job if HIGH-risk findings exist
        # by default. Configure rules.tsv to tune false positives.
      
      - name: Upload ZAP Report
        uses: actions/upload-artifact@v3
        if: always()  # Upload even if scan fails
        with:
          name: zap-report
          path: report_html.html

  # Alternative: manual Docker approach for more control
  zap-scan-docker:
    runs-on: ubuntu-latest
    steps:
      - name: Run ZAP baseline scan
        run: |
          docker run --rm \
            -v $(pwd)/reports:/zap/wrk/:rw \
            ghcr.io/zaproxy/zaproxy:stable \
            zap-baseline.py \
            -t https://staging.example.com \
            -g gen.conf \
            -r report.html \
            -x report.xml \
            -J report.json \
            -I  # Ignore informational findings (reduce noise)
          # Exit code: 0 = no issues, 1 = warnings, 2 = alerts
          EXIT_CODE=$?
          if [ $EXIT_CODE -eq 2 ]; then
            echo "ZAP found HIGH-risk security issues. Deploy blocked."
            exit 1
          fi

RULES FILE (.zap/rules.tsv) for tuning false positives:
  # Rule ID | Action   | Reason
  10016   IGNORE      # Web Browser XSS Protection Not Enabled (obsolete header)
  10020   IGNORE      # X-Frame-Options (using CSP frame-ancestors instead)
  90033   WARN        # Loosely Scoped Cookie (downgrade HIGH to WARN)
  # Remove rules that are known false positives for your app

AUTHENTICATED SCANNING:
  ZAP can authenticate before scanning (scans authenticated pages):
  
  docker run --rm ghcr.io/zaproxy/zaproxy:stable \
    zap-baseline.py \
    -t https://staging.example.com \
    --hook=/zap/wrk/auth_hook.py
  
  # auth_hook.py:
  def zap_started(zap, target):
      zap.urlopen(target + '/login')
      zap.selenium.find_element_by_id('username').send_keys('testuser')
      zap.selenium.find_element_by_id('password').send_keys('testpassword')
      zap.selenium.find_element_by_id('login-btn').click()
```

---

### 🧠 Mental Model / Analogy

> ZAP's scan types map to different levels of security review:
>
> **Passive scan** = code review without running the code.
> You read the responses and flag obvious issues (missing headers,
> insecure configuration visible in the response). No risk:
> you're just observing.
>
> **Active scan** = penetration testing. You actively probe
> for vulnerabilities by sending attack payloads. There's risk:
> test data gets created, rate limiters may trigger, unstable
> features may break. Must be done against non-production targets.
>
> **Authenticated scan** = penetration testing after being
> given legitimate access. Tests the application as a real
> user would experience it - the authenticated surface is
> usually much larger than the public surface.
>
> The CI/CD baseline scan is like a daily passive inspection
> of the production line. The full authenticated scan is like
> a quarterly audit by an external firm. Both have a role;
> neither replaces the other.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ZAP is a free tool that automatically tries to hack your
website to find security problems. It sends thousands of
crafted requests and looks for signs of vulnerabilities
(like SQL injection or XSS). It then produces a report
of what it found. Think of it as an automated security
checker that you can run regularly.

**Level 2 - How to use it (junior developer):**
Run `docker run ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://your-app -r report.html`. Read the HTML report. Investigate HIGH and MEDIUM findings manually to confirm they're real. Fix confirmed issues. Don't panic about LOW and INFO findings until you've addressed the high-risk ones. Do NOT run active scans against production - use a staging environment.

**Level 3 - How it works (mid-level engineer):**
ZAP operates as an HTTP proxy and interception point. In GUI mode: configure browser to use ZAP as proxy (localhost:8080), browse your application normally, then run the scanner on captured traffic. In Docker mode: ZAP's built-in spider discovers pages automatically. Scans have two phases: passive (safe, no side effects) and active (sends attack payloads, can cause data creation/deletion). For CI/CD: use `zaproxy/action-baseline` GitHub Action. Tune false positives with rules.tsv. Block deploys on HIGH findings. Upload report as build artifact.

**Level 4 - Why it was designed this way (senior/staff):**
DAST and SAST are complementary, not redundant. SAST finds
vulnerabilities in code before deployment but misses runtime
configuration. DAST finds vulnerabilities in running applications
but can't trace them to the specific code line. An effective
security testing program uses both: SAST in the developer IDE
(shift-left: find issues before commit), SAST in CI on pull
requests, DAST in CI against deployed staging (integration testing),
and periodic deep manual pentest by security professionals.
ZAP occupies the "automated DAST in CI" role. It's not a
pentest replacement: professional pentesters use ZAP as a
starting point, then apply domain expertise, chaining, and
business logic testing that automated tools cannot perform.

**Level 5 - Mastery (distinguished engineer):**
ZAP's API enables programmatic control for complex scenarios:
scripted authentication flows (OAuth, SAML, MFA), custom
scan policies targeting specific vulnerability types, result
filtering and correlation with SAST findings, and integration
with defect tracking (automatically create Jira issues from
HIGH findings). ZAP's extension framework allows custom scan
rules for application-specific vulnerabilities that generic
rules can't detect. For enterprise scale: ZAP daemon mode
with multiple parallel scanners, results aggregated to a
SIEM or security dashboard. False positive management is
the primary operational challenge: too many alerts → team
ignores them (alert fatigue). Build false positive baselines
by running ZAP against a known-good implementation, then
use the baseline to suppress known-acceptable findings.

---

### ⚙️ How It Works (Mechanism)

**ZAP architecture and scan flow:**

```
ZAP ARCHITECTURE:

PROXY MODE (manual testing):
  Browser → ZAP Proxy (localhost:8080) → Application

  ZAP intercepts all traffic:
    - Records all requests/responses
    - Allows modification before forwarding
    - Passive scan runs on all captured traffic
  
  After browsing: launch active scanner on captured site tree.

DOCKER/CLI MODE (automated):

  [ZAP Process]
    │
    ├─ Spider: crawls target URL
    │    └─ Discovers: URLs, forms, parameters, cookies
    │
    ├─ AJAX Spider (optional): headless browser for SPAs
    │    └─ Discovers: JavaScript-rendered content
    │
    ├─ Passive Scanner: analyzes all captured responses
    │    └─ Finds: missing headers, insecure cookies, info disclosure
    │
    └─ Active Scanner: attacks each discovered parameter
         └─ Sends: thousands of attack payloads per parameter
         └─ Analyzes: responses for vulnerability evidence

SCAN TYPES AND USE CASES:

  zap-baseline.py    → Fast, safe, CI-friendly
    - Passive scan + quick active scan
    - Limited to ~60 seconds per target
    - Good for: every PR, daily CI runs
    - Finds: configuration issues, obvious vulnerabilities
  
  zap-full-scan.py   → Comprehensive, slow
    - Full active scan with all rules
    - Can take hours on complex applications
    - Good for: weekly scheduled runs, pre-release
    - Finds: SQL injection, XSS, and more complex vulns
  
  zap-api-scan.py    → API-focused (OpenAPI/Swagger)
    - Imports OpenAPI spec for complete endpoint coverage
    - Doesn't need to crawl: spec defines all endpoints
    - Good for: REST APIs with OpenAPI documentation
    - docker run ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py \
        -t https://api.example.com/openapi.yaml \
        -f openapi -r api_report.html

EXIT CODES:
  0 → Passed (no alerts above configured threshold)
  1 → Warnings (alerts at WARN level)
  2 → Failure (alerts at FAIL level - HIGH by default)
  3 → Error (ZAP failed to run)
  
  In CI/CD: exit 2 blocks the pipeline.
```

---

### 💻 Code Example

**Complete GitHub Actions workflow with ZAP and result parsing:**

```yaml
# .github/workflows/security-scan.yml
name: DAST Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  zap-baseline:
    runs-on: ubuntu-latest
    # Permissions for uploading security findings to GitHub
    permissions:
      security-events: write
      issues: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Start application (staging mode)
        run: |
          docker compose -f docker-compose.staging.yml up -d
          # Wait for health check
          timeout 60 bash -c 'until curl -f http://localhost:8080/health; \
            do sleep 2; done'
      
      - name: Run ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.10.0
        with:
          target: 'http://localhost:8080'
          # Rules configuration file
          rules_file_name: '.zap/rules.tsv'
          # ZAP options
          cmd_options: >
            -a
            -j
            -l WARN
          # -a: Include alpha passive scan rules
          # -j: Use AJAX spider (for SPAs)
          # -l WARN: Only fail on WARN+ (not INFO)
          
          # Create GitHub issue on failure
          issue_title: 'ZAP Baseline Scan Alert'
          fail_action: false  # Don't fail action (create issue instead)
          allow_issue_writing: true
      
      - name: Upload ZAP Report as Artifact
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: zap-baseline-report-${{ github.run_id }}
          path: |
            report_html.html
            report_json.json
          retention-days: 30
      
      - name: Parse ZAP results and fail on HIGH
        run: |
          # Use Python to parse the JSON report
          python3 << 'EOF'
          import json, sys
          
          with open('report_json.json') as f:
              report = json.load(f)
          
          high_alerts = []
          for site in report.get('site', []):
              for alert in site.get('alerts', []):
                  if alert['riskcode'] == '3':  # 3 = HIGH
                      high_alerts.append({
                          'name': alert['alert'],
                          'url': alert['instances'][0]['uri']
                              if alert.get('instances') else 'N/A'
                      })
          
          if high_alerts:
              print("HIGH-risk security findings:")
              for a in high_alerts:
                  print(f"  - {a['name']}: {a['url']}")
              sys.exit(1)  # Fail the build
          else:
              print("No HIGH-risk findings. Scan passed.")
          EOF
      
      - name: Cleanup
        if: always()
        run: docker compose -f docker-compose.staging.yml down
```

---

### ⚖️ Comparison Table

| Tool | Type | Cost | Best For | Weakness |
|:---|:---|:---|:---|:---|
| **OWASP ZAP** | DAST | Free | CI/CD automation, getting started | Needs tuning to reduce noise |
| **Burp Suite Pro** | DAST | $499/yr | Manual pentest, advanced testing | Expensive, not free-tier CI/CD |
| **Nikto** | DAST | Free | Quick server config checks | Noisy, dated rule set |
| **Nuclei** | DAST | Free | Template-based CVE scanning | Requires template knowledge |
| **SonarQube** | SAST | Free/Paid | Code-level vulnerability finding | No runtime/config issues |
| **Snyk** | SCA+SAST | Free/Paid | Dependency vulnerabilities | Not a DAST tool |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| ZAP replaces manual penetration testing | ZAP is an automated scanner that finds common, well-known vulnerabilities at scale. Manual penetration testing adds: business logic testing (can I use a coupon twice?), chained attack scenarios (IDOR + CSV injection = data exfiltration), custom payload crafting, and security judgment. OWASP estimates automated tools find approximately 20-30% of vulnerabilities; the rest require human expertise. ZAP is a cost-effective first layer that finds the easy wins; professional pentesters address the harder, application-specific vulnerabilities. |
| Run ZAP against production is fine for passive scan | Even passive scanning in production carries risk: ZAP's spider submits forms (creates test data, triggers emails, creates transactions), follows all links (potential DOS on slow pages), and generates significant traffic that may trigger monitoring alerts. Always use a dedicated staging environment for ZAP. Use the production application's OpenAPI spec with `zap-api-scan.py` if you need production testing - it scans based on spec without actually browsing. |

---

### 🚨 Failure Modes & Diagnosis

**Common ZAP issues and solutions:**

```
ISSUE: ZAP exits 0 but app has known vulnerabilities
  CAUSE: Spider didn't discover all pages
    (SPA with JavaScript routing, or authentication required)
  FIX: Use AJAX spider (-j flag) for SPAs.
    For authenticated pages: configure authentication hook.
    Manually drive the app through ZAP proxy first,
    then run active scanner.

ISSUE: Too many false positives (alert fatigue)
  CAUSE: Generic rules triggering on valid app behavior
  FIX: Investigate each false positive, add to rules.tsv:
    Format: [Rule-ID] [IGNORE|WARN|FAIL] (comment)
    Get rule ID from ZAP report's pluginId field.
    Build baseline: run ZAP against known-clean app,
    suppress all findings from that baseline run.

ISSUE: ZAP Docker container network cannot reach app
  CAUSE: App running on localhost, ZAP in Docker
  FIX: Use --network host flag or host.docker.internal:
    docker run --network host ghcr.io/zaproxy/zaproxy:stable \
      zap-baseline.py -t http://localhost:8080/
    OR: docker compose with ZAP on same network as app.

ISSUE: ZAP found SQL injection but developer can't reproduce
  CAUSE: ZAP tests parameter positions; payload may be
    blocked by WAF in test env
  FIX: Try the exact payload from ZAP report manually in browser.
    Check if WAF is enabled in test environment (it shouldn't be -
    test behind WAF masks application vulnerabilities).
    Review application code for the parameter ZAP identified.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10 Overview` - understanding what ZAP tests for
- `XSS Prevention` - understanding XSS to interpret ZAP findings
- `SQL Injection Prevention` - interpreting ZAP's injection findings
- `Security Code Review Checklist` - complementary SAST approach

**Builds on this:**
- `DAST in Depth` - advanced ZAP configuration and pentest tools
- `Security Testing in CI/CD` - full pipeline integration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BASELINE     │ docker run zaproxy:stable zap-baseline.py │
│              │ -t https://staging.example.com -r rpt.html│
├──────────────┼───────────────────────────────────────────┤
│ API SCAN     │ zap-api-scan.py -t /openapi.yaml -f openapi│
├──────────────┼───────────────────────────────────────────┤
│ NEVER        │ Run active scan against production.        │
│              │ Use staging or separate test environment.  │
├──────────────┼───────────────────────────────────────────┤
│ CI/CD        │ zaproxy/action-baseline GitHub Action;     │
│              │ exit code 2 = HIGH found, block deploy     │
├──────────────┼───────────────────────────────────────────┤
│ FALSE POS.   │ Tune .zap/rules.tsv (IGNORE/WARN per ID)  │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Test what you deploy, not just what you wrote."
SAST (testing what you wrote) and DAST (testing what you
deploy) are complementary, not substitutes. The gap between
code and deployment is where many vulnerabilities live:
infrastructure misconfiguration, missing security headers set
in the wrong config file, WAF rules that only apply to certain
environments, third-party components that behave differently
in production. DAST makes the deployed application the unit
of testing, not the source code. This is why a "code looks
fine" verdict doesn't end the security review. Both the code
AND the running deployment must be tested. Apply this principle
broadly: test in the environment that resembles production most
closely; unit tests catch code bugs, integration tests catch
deployment bugs.

---

### 💡 The Surprising Truth

When the UK's National Cyber Security Centre (NCSC) ran
automated DAST scans across a sample of UK government websites,
they found that missing security headers (X-Frame-Options,
Content-Security-Policy, Strict-Transport-Security) were present
in over 60% of tested sites. These issues require five minutes
to fix (three lines in an nginx config) and are trivially
detectable by any scanner. They weren't fixed not because they
were hard to fix, but because no one had scanned for them.
Running ZAP once - even just the passive baseline scan - against
an application will typically find issues that have existed for
years and are easily fixable once someone looks for them.
The barrier isn't the fix: it's the scan. "DAST results were
never reviewed" is a more common root cause in post-breach
analyses than "the vulnerability was too complex to prevent."

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **RUN** ZAP baseline scan against a staging environment using Docker
   and produce an HTML report.
2. **INTERPRET** ZAP findings: distinguish HIGH (critical, verify manually)
   from INFO (informational, may not need action).
3. **INTEGRATE** ZAP into a GitHub Actions CI/CD pipeline using the
   `zaproxy/action-baseline` action.
4. **TUNE** false positives using a `rules.tsv` file and explain why
   false positive management is essential for alert quality.

---

### 🎯 Interview Deep-Dive

**Q: What is DAST? How does ZAP differ from SAST tools like SonarQube?
How would you integrate ZAP into a CI/CD pipeline?**

*Why they ask:* Tests security testing maturity. Can the candidate
distinguish testing approaches and understand trade-offs?

*Strong answer includes:*
- DAST: Dynamic Application Security Testing - tests the running
  application. SAST: Static Application Security Testing - tests
  source code without running it.
- DAST finds: infrastructure misconfigurations, missing HTTP headers,
  runtime vulnerabilities, issues in third-party components.
- SAST finds: code-level issues (SQL injection in code, insecure
  function calls, hardcoded secrets), traced to specific code lines.
- ZAP Docker: `zap-baseline.py -t https://staging.example.com`.
  Two scan types: passive (safe, no side effects) and active
  (attack payloads, staging only, never production).
- CI/CD: `zaproxy/action-baseline` GitHub Action. Block deploys
  on HIGH findings. Upload report as artifact. Tune false positives
  with rules.tsv to reduce alert fatigue.
- Limitation: ZAP finds ~20-30% of vulnerabilities; professional
  pentest needed for business logic and complex chained attacks.