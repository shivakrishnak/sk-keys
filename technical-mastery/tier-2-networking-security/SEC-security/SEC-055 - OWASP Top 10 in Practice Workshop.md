---
id: SEC-055
title: "OWASP Top 10 Workshop"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-003, SEC-013, SEC-016, SEC-041, SEC-043, SEC-054
used_by: SEC-086, SEC-095, SEC-105
related: SEC-001, SEC-003, SEC-013, SEC-016, SEC-041, SEC-043, SEC-044, SEC-054
tags:
  - security
  - owasp
  - owasp-top-10
  - web-security
  - vulnerability
  - workshop
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/sec/owasp-top-10-workshop/
---

⚡ TL;DR - The OWASP Top 10 is the industry-standard list of the
most critical web application security risks. Updated in 2021.
Every web developer should be able to identify, exploit (in a
test environment), and fix all 10 categories.

**The 2021 OWASP Top 10 at a glance:**

| # | Category | One-line fix |
|---|----------|-------------|
| A01 | Broken Access Control | Check authz per resource, not just route |
| A02 | Cryptographic Failures | TLS + bcrypt + AES-GCM for sensitive data |
| A03 | Injection | Parameterized queries; never concatenate user input |
| A04 | Insecure Design | Threat model; security requirements in design phase |
| A05 | Security Misconfiguration | CIS benchmarks; disable debug; change defaults |
| A06 | Vulnerable Components | Dependency scanner; update regularly |
| A07 | Auth and Session Failures | Rate-limit logins; secure session cookies; MFA |
| A08 | Software/Data Integrity Failures | Verify signatures on artifacts and serialized data |
| A09 | Logging and Monitoring Failures | Log auth events; alert on anomalies |
| A10 | SSRF | Allowlist outbound URLs; block internal IP ranges |

---

| #055 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Security Headers, Input Validation, Security Fundamentals, Security Code Review, IDOR, Security Monitoring | |
| **Used by:** | Heartbleed Analysis, OAuth Implicit Flow Deprecation, ISO 27001 | |
| **Related:** | All SEC entries - this is the comprehensive overview | |

---

### 🔥 The Problem This Solves

**WHY THE TOP 10 MATTERS AS A FRAMEWORK:**

```
THE PROBLEM:
  Web application security has thousands of potential vulnerabilities.
  A developer cannot know all of them.
  Security auditors cannot check for everything.
  Without prioritization, resources are spent on obscure edge cases
  while critical, common vulnerabilities go unfixed.

THE SOLUTION - OWASP Top 10:
  Data-driven list of the MOST prevalent and impactful vulnerabilities
  based on real-world breach data submitted by security companies
  and penetration testers.
  
  Updated periodically (2003, 2007, 2010, 2013, 2017, 2021).
  
  If you fix ONLY the Top 10: you address the vulnerabilities
  responsible for the majority of real-world web application breaches.

2021 vs 2017 CHANGES (notable):
  NEW in 2021:
    A04: Insecure Design (root cause, not just implementation)
    A08: Software and Data Integrity Failures (supply chain, Log4Shell)
    A10: SSRF (grew significantly after cloud adoption)
  
  RENAMED:
    A07: "Broken Authentication" → "Identification and Authentication Failures"
  
  MERGED/DOWNGRADED:
    XXE merged into A03 Injection
    Insecure Deserialization merged into A08
    Known Vulnerabilities elevated to A06 (was lower)

INDUSTRY ADOPTION:
  PCI-DSS requirement 6.2.4: address at minimum the OWASP Top 10.
  NIST SP 800-53: references OWASP as a web security standard.
  SOC 2 Type II: auditors check OWASP Top 10 as baseline.
  Bug bounty programs: categorize findings by OWASP.
  CVSS scoring: often maps to OWASP category.
```

---

### 📘 Textbook Definition

**OWASP Top 10:** A standard awareness document published by
the Open Web Application Security Project (OWASP) listing the
ten most critical security risks to web applications.
First published 2003, revised periodically based on community
data from security professionals worldwide. Used as a baseline
security standard in PCI-DSS, NIST guidance, and developer
security training.

**OWASP (Open Web Application Security Project):** Non-profit
foundation focused on improving software security. Produces
free tools (ZAP), documentation (Top 10, ASVS, SAMM), and
community resources. ASVS (Application Security Verification
Standard) is the comprehensive checklist; Top 10 is the
prioritized, developer-facing subset.

**Not a standard (yet):** OWASP Top 10 is an awareness
document, not a complete security standard. ASVS (450+ items)
is the comprehensive standard. PCI-DSS references both.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OWASP Top 10 = the 10 most important web security categories,
ranked by prevalence and impact. Every developer should know
them. Every application should defend against all 10.

**One analogy:**
> OWASP Top 10 is like a car safety checklist from a DMV:
> seat belts, brakes, lights, tire pressure - the basics that
> prevent the majority of accidents. It doesn't cover every
> possible failure mode (engine fire, electrical short), but
> if your car fails the basic checklist, you should fix those
> first before worrying about edge cases.
>
> Covering the Top 10 doesn't make your application fully secure
> (no list does), but it closes the vulnerabilities that account
> for the majority of real-world web application breaches.
> The data-driven ranking ensures it's the highest-value
> investment of security time and effort.

---

### 🔩 First Principles Explanation

**Deep dive on each of the 10 categories:**

```
A01: BROKEN ACCESS CONTROL (was A05 in 2017 - now #1)

  WHAT: User can access data or perform actions they're not authorized for.
  
  EXAMPLES:
    - IDOR: GET /api/users/456/orders (attacker is user 123)
    - Force-browsing to admin pages: /admin/users (unauthenticated)
    - JWT with elevated role: modify "role" claim from "user" to "admin"
    - CORS misconfiguration: allows credentialed requests from any origin
    - Missing function-level access control: DELETE /api/users/{id} has
      no admin check because the UI hides the button (security through obscurity)
  
  FIX:
    - Deny by default: unless explicitly permitted, deny.
    - Check authorization per resource access (not just at route level).
    - Server-side access control (not UI hiding).
    - Log access failures.
  
  SEE ALSO: SEC-043 (IDOR), SEC-001 (OWASP Top 10 overview)

A02: CRYPTOGRAPHIC FAILURES (was A03 "Sensitive Data Exposure" in 2017)

  WHAT: Data transmitted or stored without encryption, or with weak
  encryption. Focus shifted from "data exposure" to the crypto failures
  that cause it.
  
  EXAMPLES:
    - Transmitting sensitive data over HTTP (not HTTPS)
    - Passwords stored in plaintext or with fast hash (MD5, SHA1)
    - Credit card data stored unencrypted at rest
    - AES-ECB mode (patterns visible in ciphertext)
    - Weak keys (RSA-512, DH-512)
    - TLS 1.0/1.1 still supported (deprecated protocols)
  
  FIX:
    - Enforce HTTPS everywhere (HSTS)
    - bcrypt/scrypt/Argon2 for passwords (not MD5/SHA1/SHA256)
    - AES-GCM for symmetric encryption (authenticated encryption)
    - RSA-2048+ or ECDSA P-256+ for asymmetric
    - TLS 1.2 minimum (TLS 1.3 preferred)
  
  SEE ALSO: SEC-002 (HTTPS), SEC-003 (Password Hashing)

A03: INJECTION (covers SQL, LDAP, XPath, OS command, XXE, etc.)

  WHAT: Untrusted data sent to an interpreter as part of a command or query.
  Interpreter cannot distinguish between intended data and attacker's command.
  
  EXAMPLES:
    - SQL injection: SELECT * FROM users WHERE name = ''+OR+'1'='1
    - Command injection: os.system("ping " + user_input)
    - LDAP injection, XPath injection
    - XXE (XML External Entities): <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    - Template injection: {{7*7}} in Jinja2 template
  
  FIX:
    - Parameterized queries / prepared statements (SQL)
    - Input validation and allowlist
    - ORMs (which use parameterized queries internally)
    - Disable XML external entities (XXE)
    - Shell injection: use execv() with array args, not shell=True
  
  SEE ALSO: SEC-005 (SQL Injection), SEC-006 (XSS), SEC-007 (Command Injection)

A04: INSECURE DESIGN (NEW in 2021)

  WHAT: Security flaws in application architecture and design, not just
  implementation bugs. An insecure design cannot be fixed by good code
  implementation - the design must be rethought.
  
  EXAMPLES:
    - Password recovery via security questions (guessable answers)
    - Storing payment card numbers in your own database (you should use Stripe)
    - Building your own authentication system from scratch (use OAuth/OIDC)
    - Credential recovery "text me the password" (can't text what's hashed)
    - Microservice A calls Microservice B with no authentication between them
      (design flaw: trust everything on the internal network)
  
  FIX:
    - Threat modeling in design phase (STRIDE)
    - Security requirements before coding
    - Reference to established patterns (OAuth, OIDC, PKCE)
    - Zero-trust internal architecture
  
  SEE ALSO: SEC-059 (STRIDE), SEC-057 (OAuth), SEC-058 (OIDC)

A05: SECURITY MISCONFIGURATION

  WHAT: Insecure default configurations, unnecessary features enabled,
  verbose error messages, missing security hardening.
  
  EXAMPLES:
    - Django DEBUG=True in production (reveals stack traces, DB passwords)
    - Default credentials unchanged (admin/admin)
    - Directory listing enabled (can browse file system via URL)
    - Spring Boot Actuator /env endpoint exposed (reveals all env vars)
    - Unnecessary ports open (Redis on 0.0.0.0 with no auth)
    - Cloud storage bucket publicly readable (S3 misconfiguration)
    - Missing security headers (CSP, HSTS, X-Frame-Options)
  
  FIX:
    - CIS benchmarks for OS and application configuration
    - Separate config for development/production
    - Infrastructure as Code with security checks
    - Automated config scanning (AWS Config, Chef InSpec)
  
  SEE ALSO: SEC-008 (Security Headers), SEC-009 (Secrets Management)

A06: VULNERABLE AND OUTDATED COMPONENTS

  WHAT: Using third-party components (libraries, frameworks, OS) with
  known vulnerabilities that have not been patched.
  
  EXAMPLES:
    - Log4Shell (CVE-2021-44228): Log4j 2.0-2.14.1 in millions of apps
    - Struts 2 (CVE-2017-5638): led to Equifax breach (Equifax 2017)
    - Spring4Shell (CVE-2022-22965): critical Spring Framework vuln
    - Left-pad incident: JS ecosystem dependency chain collapse
    - Docker base images with unpatched CVEs
  
  FIX:
    - SCA (Software Composition Analysis): Snyk, OWASP Dependency-Check, GitHub Dependabot
    - SBOM (Software Bill of Materials)
    - Automated dependency update PRs
    - Container image scanning (Trivy, Clair)
    - Lock files + audit (npm audit, pip-audit, mvn dependency-check)
  
  SEE ALSO: SEC-076 (SCA and Supply Chain Security)

A07: IDENTIFICATION AND AUTHENTICATION FAILURES

  WHAT: Weaknesses in authentication and session management that allow
  attackers to assume other users' identities.
  
  EXAMPLES:
    - No rate limiting on login (brute force)
    - Weak passwords allowed (no policy)
    - Passwords stored in plaintext or weak hash
    - Session IDs in URL (referrer header leak)
    - Session not invalidated after logout
    - No MFA available for high-privilege users
    - "Remember me" token never expires
    - JWT with alg:none (no signature verification)
  
  FIX:
    - Rate limiting and account lockout
    - bcrypt for password storage
    - Secure, HttpOnly, SameSite session cookies
    - Session regeneration after authentication
    - MFA for admin access
    - JWT: verify signature and claims (exp, iss, aud)
  
  SEE ALSO: SEC-010 (Auth fundamentals), SEC-049 (Secure login exercise), SEC-056 (JWT anti-patterns)

A08: SOFTWARE AND DATA INTEGRITY FAILURES (NEW in 2021)

  WHAT: Code and infrastructure that does not verify integrity of
  software updates, critical data, or CI/CD pipelines. Also covers
  insecure deserialization.
  
  EXAMPLES:
    - SolarWinds SUNBURST: malicious code injected into build pipeline,
      signed by SolarWinds' certificate, distributed as "official update"
    - Insecure deserialization: accepting arbitrary Java serialized objects
      → remote code execution
    - pip install without hash verification (pip install --require-hashes)
    - Auto-update from CDN without integrity check (no SRI in HTML script tags)
    - GitHub Actions using third-party action at floating tag (not commit hash)
  
  FIX:
    - SRI (Subresource Integrity): <script integrity="sha384-..."> for CDN scripts
    - Signed releases: GPG-signed packages, sigstore/cosign for containers
    - Pinned dependencies: use commit hash not tag in GitHub Actions
    - Avoid accepting arbitrary serialized objects from users
    - SLSA framework (Supply chain Levels for Software Artifacts)
  
  SEE ALSO: SEC-082 (SolarWinds SUNBURST), SEC-115 (SLSA Framework)

A09: SECURITY LOGGING AND MONITORING FAILURES

  WHAT: Not logging security events, not monitoring for anomalies,
  not alerting on suspicious activity. Enables attacks to go undetected.
  
  EXAMPLES:
    - No logging of authentication events
    - Brute force attack runs for weeks without detection
    - Log monitoring system silently failed (Equifax 2017: broken SSL
      inspection certificate expired; monitoring blind for 19 months)
    - Logs written to host only (attacker deletes after compromise)
    - Unstructured logs that SIEM cannot parse
    - No alerting on anomalous data access patterns
  
  FIX:
    - Log auth events (success, failure, lockout)
    - Structured JSON logs for SIEM
    - Ship logs immediately to remote append-only storage
    - Alert on thresholds (5 failed logins/15min = brute force)
    - Monitor the monitoring (canary events to verify alerting works)
  
  SEE ALSO: SEC-054 (Security Monitoring Basics), SEC-100 (Insufficient Logging)

A10: SERVER-SIDE REQUEST FORGERY (SSRF) (NEW in 2021)

  WHAT: Server makes HTTP requests to a URL from user input without
  validating the URL is safe. Allows access to internal services.
  
  EXAMPLES:
    - Capital One 2019: SSRF to AWS metadata → IAM credentials → S3 bucket access
    - Server fetches images from user-provided URL → attacker provides 169.254.169.254
    - Import document from URL → attacker provides internal Redis URL
    - Webhook registration → attacker registers http://localhost:6379 (Redis)
    - Open redirect + SSRF: redirect followed by server → internal service access
  
  FIX:
    - Allowlist of allowed external URLs (not blocklist)
    - Block internal IP ranges: 127.0.0.1, 10.0.0.0/8, 172.16.0.0/12,
      192.168.0.0/16, 169.254.0.0/16 (AWS metadata)
    - DNS resolution check (after resolving, check the IP is not internal)
    - IMDSv2 (AWS instance metadata v2 requires session token - harder to access via SSRF)
  
  SEE ALSO: SEC-060 (SSRF Deep Dive)
```

---

### 🧪 Thought Experiment

**SCENARIO: Code review against Top 10**

```
REVIEW THIS CODE (intentionally vulnerable):

@app.route('/api/users/<int:user_id>/export', methods=['GET'])
def export_user_data(user_id: int):
    # Get user data
    query = f"SELECT * FROM users WHERE id = {user_id}"
    user = db.execute(query).fetchone()
    
    if not user:
        return {"error": "Not found"}, 404
    
    # Fetch their profile picture from external URL
    pic_url = user['profile_picture_url']
    pic = requests.get(pic_url).content
    
    # Export to temp file
    import os
    temp_path = f"/tmp/export_{user_id}.json"
    with open(temp_path, 'w') as f:
        json.dump(dict(user), f)  # Includes ALL user fields
    
    return send_file(temp_path)

ANALYSIS:

A01 - Broken Access Control:
  No authorization check. Any authenticated user can export
  ANY user's data. 
  Fix: check current_user.id == user_id (or admin role).

A03 - Injection (SQL):
  f"SELECT * FROM users WHERE id = {user_id}"
  user_id is from URL param - integer type in Flask helps,
  but parameterized query is the correct defense.
  Fix: db.execute("SELECT * FROM users WHERE id = ?", [user_id])

A02 - Cryptographic Failures (data exposure):
  json.dump(dict(user), f) - exports ALL user fields including
  password_hash, SSN, credit card (if stored).
  Fix: explicit allowlist of fields to export.

A10 - SSRF:
  requests.get(pic_url) with URL from database (user-controlled at upload).
  If user stored "http://169.254.169.254/latest/meta-data/" as profile pic URL,
  this fetches AWS metadata.
  Fix: validate pic_url against allowlist of image CDN domains.

A09 - Logging Failure:
  No logging of data export event (who exported which user's data, when).
  Fix: log export events with admin_id, target_user_id, timestamp.

SCORE: This 15-line function hits A01, A02, A03, A09, A10.
Five of the Top 10 in one function.
```

---

### 🧠 Mental Model / Analogy

> OWASP Top 10 is the building code for web applications.
>
> A building code doesn't describe every possible construction defect.
> It describes the minimum requirements that prevent the most common
> causes of structural failure, fire, and harm.
>
> A building without a code inspection might have:
> A01: Doors that anyone can open (no locks on stairwells)
> A02: No fire-proofing between floors (data exposed to adjacent systems)
> A03: Plumbing that allows contamination (injection: dirty water into clean)
> A05: Outdated circuit breaker that doesn't trip (misconfiguration)
> A06: Materials using recalled components (vulnerable libraries)
>
> A building inspector checks against the code.
> A security auditor checks against the Top 10.
> Passing the code doesn't mean the building is perfect.
> But failing means it's not safe to occupy.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
OWASP Top 10 is a list of the 10 most dangerous types of web security problems. It's updated every few years based on what attackers are actually exploiting. Every developer should know these 10 categories and make sure their applications don't have them.

**Level 2 - How to use it (junior developer):**
Use the OWASP Top 10 as a checklist in code review. Before any feature goes to production: do a Top 10 walk-through. A01: can users access data they shouldn't? A03: is any user input concatenated into a SQL query or shell command? A02: are passwords hashed with bcrypt? A07: is there rate limiting on login? A06: are dependencies up to date? These five catch the majority of common vulnerabilities.

**Level 3 - How it works (mid-level engineer):**
In 2021, OWASP added A04 (Insecure Design) and A10 (SSRF) based on changing threat patterns. Insecure Design reflects that many breaches come from architectural decisions, not just coding bugs. SSRF jumped into the Top 10 because cloud adoption made the AWS metadata endpoint (169.254.169.254) a universal SSRF target - before cloud, SSRF had limited impact; in cloud environments, it can mean full credential compromise. A08 (Software and Data Integrity) reflects supply chain attacks (SolarWinds, XZ Utils). The Top 10 evolves with the threat landscape.

**Level 4 - Why it was designed this way (senior/staff):**
OWASP Top 10 is driven by data: survey of security professionals and data from DAST tools run against production applications. The ranking reflects actual prevalence in the wild. A01 (Broken Access Control) moved to #1 in 2021 because access control failures are found in 94% of applications tested. This is partly because access control logic is application-specific (no framework auto-generates it), making it consistently underimplemented. ASVS provides 450+ checks organized in levels (L1: basic, L2: standard, L3: high security) for applications that need more than the Top 10.

**Level 5 - Mastery (distinguished engineer):**
The Top 10 framework maps to threat modeling: A01 maps to Elevation of Privilege (STRIDE-E), A03 to Tampering (T), A02 to Information Disclosure (I), A04 to all STRIDE categories (design-level threat). Understanding this mapping helps you prioritize during threat model reviews. At the organizational level: OWASP SAMM (Software Assurance Maturity Model) describes how to build a security program around these 10 categories: from basic developer training to automated SAST/DAST in CI/CD to security champions and threat modeling workshops. The Top 10 is the starting point; SAMM is the maturity framework.

---

### ⚙️ How It Works (Mechanism)

**OWASP Top 10 quick-reference with code patterns:**

```
A01 BROKEN ACCESS CONTROL - Pattern:

  WRONG (route-level check only):
    @require_login  # Only checks if logged in, not if authorized
    def view_document(doc_id):
        return Document.get(doc_id)  # No owner check!
  
  CORRECT (resource-level check):
    @require_login
    def view_document(doc_id):
        doc = Document.get(doc_id)
        if doc.owner_id != current_user.id and not current_user.is_admin:
            abort(403)
        return doc

A03 INJECTION - Pattern:

  WRONG (string concatenation):
    query = f"SELECT * FROM users WHERE email = '{user_email}'"
  
  CORRECT (parameterized):
    cursor.execute("SELECT * FROM users WHERE email = %s", [user_email])

A07 AUTH FAILURES - Pattern:

  WRONG (no rate limit):
    @app.post("/login")
    def login(creds): ...
  
  CORRECT (rate limit + account lockout):
    @limiter.limit("5 per minute")  # Flask-Limiter
    @app.post("/login")
    def login(creds): ...

A08 INTEGRITY - Pattern (GitHub Actions):

  WRONG (floating tag):
    - uses: actions/checkout@v3  # Tag can be moved to different commit
  
  CORRECT (pinned to commit hash):
    - uses: actions/checkout@v4.2.1  # Immutable reference
  
  SRI for CDN scripts:
    WRONG: <script src="https://cdn.example.com/lib.js"></script>
    
    CORRECT:
    <script src="https://cdn.example.com/lib.js"
      integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ..."
      crossorigin="anonymous"></script>
```

---

### 💻 Code Example

**Automated OWASP Top 10 scanning with ZAP in CI/CD:**

```yaml
# .github/workflows/security.yml - OWASP ZAP baseline scan
# Tests A01-A10 through active and passive scanning

name: OWASP Security Scan

on:
  pull_request:
    branches: [main]

jobs:
  zap-scan:
    name: OWASP ZAP Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4.2.1  # Pinned hash (A08)
      
      - name: Start application (background)
        run: |
          docker-compose up -d
          # Wait for app to be ready
          timeout 60 bash -c 'until curl -sf http://localhost:8080/health; do sleep 2; done'
      
      - name: ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.12.0
        with:
          target: 'http://localhost:8080'
          rules_file_name: '.zap/rules.tsv'  # False positive suppression
          fail_action: true  # Fail PR on new HIGH alerts
          cmd_options: '-l WARN'  # WARN and above trigger failure
      
      - name: Upload ZAP Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: zap-security-report
          path: report_html.html

# .zap/rules.tsv - suppress known false positives:
# 10016  IGNORE  (Web Browser XSS Protection - intentionally removed for modern browsers)
# 90003  IGNORE  (UTF-8 Charset not defined - handled by framework default)
```

---

### ⚖️ Comparison Table

| OWASP Category | 2017 Rank | 2021 Rank | Reason for Change |
|:---|:---|:---|:---|
| Broken Access Control | A05 | A01 | Found in 94% of tested apps |
| Cryptographic Failures | A03 | A02 | Renamed from "Sensitive Data Exposure" |
| Injection | A01 | A03 | Better framework protection reduced prevalence |
| Insecure Design | (not in 2017) | A04 | Architecture/design flaws recognized separately |
| Security Misconfiguration | A06 | A05 | Cloud misconfigs grew |
| Vulnerable Components | A09 | A06 | Supply chain attacks increased |
| Auth Failures | A02 | A07 | Better tooling reduced prevalence |
| Integrity Failures | (not in 2017) | A08 | SolarWinds, insecure deserialization |
| Logging Failures | A10 | A09 | Same importance, new name |
| SSRF | (not in 2017) | A10 | Cloud adoption made SSRF critical |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Passing an OWASP Top 10 scan means the application is secure. | The OWASP Top 10 is a subset of known vulnerability classes. Passing a ZAP scan (which tests for common patterns in the Top 10) means you pass those automated checks. It does NOT mean you're free of business logic flaws (A01 is hard to automate), all injection variants, or vulnerabilities specific to your application. The Top 10 is the minimum bar, not the goal. ASVS (450+ checks) and threat modeling for your specific application are needed for comprehensive coverage. The OWASP Testing Guide has over 90 test cases; ZAP automates perhaps 30% of them. |
| Injection (A03) is only about SQL injection. | A03 covers ANY injection where user input reaches an interpreter. This includes: SQL injection, LDAP injection, XPath injection, Command injection (os.system(), exec()), Template injection (Jinja2, Freemarker, Twig), XML injection / XXE, Log injection (newlines in log entries that fake log entries), SSML injection, GraphQL injection, CSV injection (formula injection in spreadsheets). The common thread: user input reaches an interpreter without proper escaping or parameterization. Each interpreter needs its own escaping/parameterization approach. |

---

### 🚨 Failure Modes & Diagnosis

**Workshop exercise: find the Top 10 in a vulnerable app:**

```
DELIBERATE PRACTICE (using DVWA or Juice Shop):

DVWA (Damn Vulnerable Web Application):
  docker run --rm -p 80:80 vulnerables/web-dvwa
  
  Exercise 1 (A03 SQL Injection):
    Navigate to: SQL Injection module
    Submit: 1' OR '1'='1 in the User ID field
    Goal: Extract all users from the database
    Fix: Use parameterized queries (see solution in DVWA source)
  
  Exercise 2 (A03 XSS):
    Navigate to: XSS Reflected
    Submit: <script>alert(document.cookie)</script>
    Goal: Steal session cookies
    Fix: Output encoding (html.escape() before rendering)
  
  Exercise 3 (A01 Broken Access Control):
    Navigate to: Insecure CAPTCHA
    Goal: bypass CAPTCHA using dev tools
    (Modify form to submit step=2 directly, skipping CAPTCHA)
    Fix: Server-side state tracking for multi-step operations

OWASP Juice Shop (more modern, realistic):
  docker run --rm -p 3000:3000 bkimminich/juice-shop
  
  A01 challenge: Access /administration without being admin
  A02 challenge: Change the price of a product to 0.00
  A03 challenge: Log in with SQL injection
  A07 challenge: Log in without credentials (JWT manipulation)
  
  Juice Shop tracks your completed challenges in the Score Board.

FOR PRODUCTION CODE REVIEW:
  Run OWASP Dependency-Check:
    mvn dependency-check:check  # Java/Maven
    npx audit-ci --high         # Node.js
  
  Run Bandit (Python static analysis for security):
    pip install bandit
    bandit -r ./src -l  # -l: report all severity levels
  
  Run Semgrep (polyglot SAST):
    semgrep --config "p/owasp-top-ten" ./src
```

---

### 🔗 Related Keywords

**Prerequisites:**
- All SEC L1 entries - foundations
- `Security Code Review Checklist` - practical review process
- `Security Testing with OWASP ZAP` - automated scanning

**Builds on this:**
- `Heartbleed` - real-world A06 case
- `Log4Shell` - real-world A06 case (Vulnerable Components)
- `ISO 27001` - OWASP as input to risk management framework

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ A01 Broken Access Control    → Check per resource        │
│ A02 Cryptographic Failures   → bcrypt + TLS + AES-GCM   │
│ A03 Injection                → Parameterized queries     │
│ A04 Insecure Design          → Threat model in design    │
│ A05 Security Misconfiguration→ CIS benchmarks; no debug  │
│ A06 Vulnerable Components    → SCA scanner + update      │
│ A07 Auth Failures            → Rate limit + MFA + secure │
│                                session cookies           │
│ A08 Integrity Failures       → SRI + signed artifacts    │
│ A09 Logging Failures         → Log auth; alert anomalies │
│ A10 SSRF                     → Allowlist outbound URLs   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Use a taxonomy to communicate risk, not to enumerate all risk."
The OWASP Top 10's value is not exhaustiveness - it's a shared
vocabulary. When you file a bug as "A01 - Broken Access Control,"
every security-aware engineer knows the category, severity, and
fix direction without a paragraph of explanation. Shared taxonomies
accelerate communication in security, as in other engineering domains.
CVSS score communicates severity. CVE ID communicates the specific
vulnerability. OWASP category communicates the class.
When reviewing code or filing security bugs: use the OWASP category
as part of the bug description. It anchors the discussion, sets
expectations, and links to well-known remediation guidance.
Cross-team: "this has A01 issues" is instantly meaningful to
developers, QA, PMs, and auditors alike.
The list is a communication protocol, not just a checklist.

---

### 💡 The Surprising Truth

In 2021, OWASP reorganized Injection (A03) to include XXE
(XML External Entities). Previously its own category (A04 in 2017),
XXE was merged because the root cause is the same: user-controlled
input reaching an interpreter (the XML parser) without sanitization.
The XML parser, instructed by attacker-controlled XML to "read this
external entity from file:///etc/passwd," reads it. The injection
is not SQL - it's an instruction injected into the XML parser.
The pattern is identical: untrusted input → interpreter → arbitrary
read/action.
Similarly, in 2021, Insecure Deserialization became part of A08
(Software and Data Integrity Failures). The insight: accepting
arbitrary serialized objects from untrusted sources is an integrity
problem - you're accepting code/data whose integrity you haven't
verified.
OWASP's consolidations reveal the deep structure: most web
vulnerabilities are instances of a few root causes (untrusted input,
missing access control, weak crypto, integrity failures).
Understanding the root causes is more powerful than memorizing
vulnerability names.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **RECITE** all 10 OWASP 2021 categories from memory with one-line descriptions.
2. **IDENTIFY** which Top 10 category a given vulnerability belongs to and why.
3. **EXPLOIT** A01, A03, and A07 in a practice environment (DVWA or Juice Shop).
4. **MAP** a STRIDE threat model finding to its OWASP Top 10 category.
5. **REVIEW** code against Top 10: find at least one instance of A01, A03,
   and A07 in a deliberately vulnerable code sample.

---

### 🎯 Interview Deep-Dive

**Q: Walk me through the OWASP Top 10 2021.
Which is most common and why?**

*Why they ask:* Fundamental knowledge baseline for security-aware developers.
Reveals depth of understanding beyond just knowing names.

*Strong answer covers:*
- A01 Broken Access Control - most prevalent (94% of apps). Authorization
  checked at route level but not per resource. IDOR example.
- A03 Injection - moved from #1 to #3 because modern frameworks (ORMs)
  provide parameterized queries by default. Still critical.
- A02 Cryptographic Failures - renamed from "Sensitive Data Exposure."
  bcrypt for passwords, TLS everywhere, AES-GCM for data at rest.
- A04 Insecure Design - NEW in 2021. Architecture-level flaws that good
  code cannot fix. Threat modeling in design phase is the prevention.
- A06 Vulnerable Components - why: third-party code is not reviewed by your team.
  Log4Shell, Equifax/Struts2. SCA scanning in CI/CD.
- A08 Integrity Failures - NEW. SolarWinds supply chain attack showed that
  build pipeline compromise can distribute signed malware.
- A10 SSRF - NEW. Cloud made this critical: AWS metadata at 169.254.169.254
  is accessible via SSRF from any cloud host. Capital One 2019.
- A01/A03/A07 are the "coding interview" categories - most commonly tested
  because they appear in every application.