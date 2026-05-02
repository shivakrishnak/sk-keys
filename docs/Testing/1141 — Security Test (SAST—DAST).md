---
layout: default
title: "Security Test (SAST—DAST)"
parent: "Testing"
nav_order: 1141
permalink: /testing/security-test-sast-dast/
number: "1141"
category: Testing
difficulty: ★★★
depends_on: CI-CD, Code Quality, HTTP and APIs
used_by: Security Engineers, DevSecOps, SRE, Compliance
related: SonarQube, OWASP, Penetration Testing, Dependency Scanning, CVE
tags:
  - testing
  - security
  - devsecops
  - sast
  - dast
---

# 1141 — Security Test (SAST/DAST)

⚡ TL;DR — Security testing verifies that software cannot be exploited. SAST (Static Application Security Testing) analyses source code for vulnerabilities without running it; DAST (Dynamic Application Security Testing) attacks a running application like a hacker would.

| #1141           | Category: Testing                                               | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | CI-CD, Code Quality, HTTP and APIs                              |                 |
| **Used by:**    | Security Engineers, DevSecOps, SRE, Compliance                  |                 |
| **Related:**    | SonarQube, OWASP, Penetration Testing, Dependency Scanning, CVE |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A developer writes `String query = "SELECT * FROM users WHERE id = " + userId;` — a SQL injection vulnerability. It passes all unit tests, all integration tests, all load tests. It ships to production. An attacker sends `userId = "1 OR 1=1"` and downloads the entire users table. Without security testing, functional correctness tests miss security vulnerabilities entirely — because the code is functionally correct, it just responds to malicious input unexpectedly.

THE CRITICAL INSIGHT:
Security vulnerabilities are not bugs in the traditional sense. The code does exactly what the developer intended — it just also does what the attacker intended. Only security-specific testing can find them.

### 📘 Textbook Definition

**SAST (Static Application Security Testing):** Analysis of source code, bytecode, or binary without executing the program. Finds: hardcoded credentials, SQL injection patterns, XSS patterns, insecure cryptography, path traversal. Tools: SonarQube, Checkmarx, Semgrep, SpotBugs.

**DAST (Dynamic Application Security Testing):** Testing a running application by sending malicious inputs — attacking it like a real adversary. Finds: authentication bypass, session management flaws, injection at runtime, server misconfiguration. Tools: OWASP ZAP, Burp Suite, Nikto.

**SCA (Software Composition Analysis):** Scans dependencies for known CVEs. Tools: Snyk, OWASP Dependency-Check, GitHub Dependabot.

### ⏱️ Understand It in 30 Seconds

**One line:**
SAST = security code review at scale (automated); DAST = automated pen test against running app.

**One analogy:**

> SAST is a structural inspection of a building's blueprints for fire code violations (before the building is built). DAST is a fire marshal walking through the completed building, trying every door and exit to find actual hazards.

### 🔩 First Principles Explanation

OWASP TOP 10 (2021) — what security tests catch:

```
A01: Broken Access Control  ← DAST (try accessing /admin without auth)
A02: Cryptographic Failures  ← SAST (detect weak cipher usage in code)
A03: Injection (SQL, LDAP, OS) ← SAST + DAST (pattern + runtime test)
A04: Insecure Design        ← Threat modeling (manual)
A05: Security Misconfiguration ← DAST (probe headers, defaults)
A06: Vulnerable Components  ← SCA (dependency CVE scan)
A07: Auth/Session Failures  ← DAST (session fixation, brute force)
A08: Software Integrity     ← SAST + SCA (CI pipeline integrity)
A09: Logging Failures        ← SAST (check for sensitive data in logs)
A10: SSRF                   ← DAST (probe internal endpoints)
```

DEVSECOPS PIPELINE:

```
Developer commit →
  [SAST: Semgrep/SonarQube] → scan on every PR, fail on HIGH severity
  [SCA: Snyk] → scan dependencies, fail on CVSS ≥ 7.0
  [Secrets scan: Gitleaks/truffleHog] → fail on any hardcoded credential
  ↓ (only if all pass)
Deploy to staging →
  [DAST: OWASP ZAP baseline scan] → passive scan, no active attack
  ↓ (on release branch)
Deploy to pre-prod →
  [DAST: OWASP ZAP full scan] → active attack simulation
  [Pen test: manual] → quarterly, by external team
```

### 🧪 Thought Experiment

SAST FINDS WHAT DAST MISSES:

```java
// SAST catches this immediately:
private static final String SECRET = "my-secret-key-12345"; // hardcoded credential

// SAST: "Hardcoded credential at UserService.java:42"
// DAST: cannot see this — it's in memory, not in HTTP responses
```

DAST FINDS WHAT SAST MISSES:

```
SAST on a JWT authentication endpoint: code looks correct
DAST test: send JWT with algorithm "none" (alg=none attack)
  → server accepts the token without signature verification
  → authentication bypass
SAST couldn't find this because the algorithm check was in a third-party library
  the library version had a known vulnerability that SAST didn't flag
```

### 🧠 Mental Model / Analogy

> SAST + DAST = a dual security audit. SAST is the **inside auditor** who reads all the source code, policies, and configurations looking for violations. DAST is the **external red team** who is given only the URL and tries every known attack. Both find different things; neither is complete without the other.

### 📶 Gradual Depth — Four Levels

**Level 1:** SAST scans your code for security mistakes (like a spell-checker for vulnerabilities). DAST attacks your running app like a hacker would. Both are needed because they find different types of issues.

**Level 2:** Add SAST to your CI pipeline: SonarQube or Semgrep on every PR. Configure rules for your language (Java, JavaScript, Python). Set severity thresholds: block merge on HIGH/CRITICAL, warn on MEDIUM. Add SCA (Snyk/Dependabot) to fail builds with CVSS ≥ 7.0 dependencies. DAST: add OWASP ZAP baseline scan in staging pipeline (passive scan only — no active attack). Progress to ZAP full scan (active attack) in pre-prod environment only.

**Level 3:** SAST false positive management: SAST tools have 20-40% false positive rates; teams must triage and suppress confirmed false positives with in-code annotations (`// NOSONAR` for SonarQube). DAST scoping: define which URLs to include/exclude in scans; authenticated DAST (provide session cookie to scan authenticated areas); avoid scanning third-party URLs. IAST (Interactive Application Security Testing): instruments the running application (JVM agent) to observe security issues from the inside while DAST exercises it from the outside — lower false positive rate.

**Level 4:** Threat modeling (pre-SAST/DAST): before writing code, model threats using STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege). Threat modeling identifies design-level security issues that neither SAST nor DAST can find (e.g., "the design assumes only admins can access this endpoint, but there is no enforcement mechanism"). Shift-left security: the cost to fix a vulnerability grows exponentially from design → code → test → production. NIST estimates: $100 to fix at design, $1,500 at code, $10,000 in QA, $30,000 in production.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│                SAST vs DAST COVERAGE MAP                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  SAST (source code):          DAST (running app):       │
│  ✓ Hardcoded secrets          ✓ Auth bypass             │
│  ✓ SQL injection patterns     ✓ Session management      │
│  ✓ Insecure crypto API use    ✓ HTTP security headers    │
│  ✓ Path traversal patterns    ✓ XSS in responses        │
│  ✓ Dependency vulnerabilities ✓ CORS misconfiguration   │
│  ✗ Runtime auth bypass        ✗ Hardcoded secrets       │
│  ✗ Server misconfiguration    ✗ Logic-level code bugs   │
│                                                          │
│  TOGETHER: comprehensive coverage of OWASP Top 10       │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

```
Developer: adds new /api/admin/users endpoint
CI pipeline:
  1. SAST (Semgrep): scans controller code
     → WARN: no @PreAuthorize annotation on admin endpoint
  2. Developer: adds @PreAuthorize("hasRole('ADMIN')")
  3. SAST re-run: PASS

Staging deployment:
  4. OWASP ZAP baseline scan:
     → ALERT: missing X-Content-Type-Options header
  5. Developer: adds security headers in SecurityConfig
  6. ZAP re-run: PASS

Pre-prod:
  7. ZAP full active scan:
     → attempts 500+ attack payloads (XSS, SQL injection, etc.)
     → PASS: all rejected with 400/403
  8. Manual pen test: PASS

Result: security issues found and fixed BEFORE production
```

### 💻 Code Example

{% raw %}
```yaml
# GitHub Actions: SAST + SCA on every PR
name: Security Scan
on: [pull_request]
jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Semgrep SAST
        uses: returntocorp/semgrep-action@v1
        with:
          config: "p/java p/owasp-top-ten"
          # Fails on HIGH/CRITICAL by default

  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk SCA
        uses: snyk/actions/maven@master
        with:
          args: --severity-threshold=high # fail on HIGH+ CVEs
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```
{% endraw %}

```java
// Spring Security: example of what SAST looks for
@RestController
@RequestMapping("/api")
public class UserController {

    // BAD: SAST flags this — no authorization check
    @GetMapping("/admin/users")
    public List<User> getAllUsers() { ... }

    // GOOD: SAST passes this
    @GetMapping("/admin/users")
    @PreAuthorize("hasRole('ADMIN')")
    public List<User> getAllUsers() { ... }

    // BAD: SAST flags SQL injection pattern
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable String id, JdbcTemplate jdbc) {
        return jdbc.queryForObject(
            "SELECT * FROM users WHERE id = " + id,  // SAST: SQL injection
            User.class);
    }

    // GOOD: parameterized query
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable String id, JdbcTemplate jdbc) {
        return jdbc.queryForObject(
            "SELECT * FROM users WHERE id = ?",
            new Object[]{id}, User.class);
    }
}
```

### ⚖️ Comparison Table

|                 | SAST           | DAST             | SCA             | Manual Pen Test |
| --------------- | -------------- | ---------------- | --------------- | --------------- |
| When            | At build time  | At test time     | At build time   | Quarterly       |
| What            | Code patterns  | Runtime behavior | Dependency CVEs | Logic flaws     |
| False positives | High (20-40%)  | Low              | Low             | Very low        |
| Speed           | Fast (minutes) | Slow (hours)     | Fast            | Slow (days)     |
| Cost            | Low            | Medium           | Low             | High            |

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                            |
| ------------------------------------ | ---------------------------------------------------------------------------------- |
| "SAST is enough"                     | SAST misses runtime issues (auth bypass, server misconfiguration, logic flaws)     |
| "DAST replaces manual pen testing"   | DAST tools can't reason about business logic; manual pen testers find design flaws |
| "100% SAST clean = secure"           | SAST has 20-40% false negatives; "clean SAST" is necessary, not sufficient         |
| "Security testing slows development" | Shift-left: fixing in CI is 100× cheaper than fixing in production                 |

### 🚨 Failure Modes & Diagnosis

**1. Too Many SAST False Positives → Team Ignores All Alerts**

Cause: Default SAST rules tuned for all languages/frameworks, not your specific codebase.
Fix: Tune rules for your framework (disable irrelevant rules, add custom rules). Require triage for every new HIGH alert before suppressing.

**2. DAST Scans Never Run Because They're Too Slow**

Cause: Full ZAP active scan takes 2-4 hours; not practical for every PR.
Fix: Run passive (baseline) scan on every PR (fast); active scan only on staging/release branches.

### 🔗 Related Keywords

- **Prerequisites:** CI-CD, HTTP and APIs, Code Quality
- **Builds on:** Penetration Testing, Threat Modeling, DevSecOps
- **Related:** SonarQube Quality Gate, OWASP, CVE, Dependency Scanning

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SAST         │ Code analysis, no execution, finds code  │
│              │ patterns → CI pipeline, every commit     │
├──────────────┼───────────────────────────────────────────┤
│ DAST         │ Attack running app → staging/pre-prod    │
├──────────────┼───────────────────────────────────────────┤
│ SCA          │ Dependency CVEs → every build            │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Semgrep, SonarQube, OWASP ZAP, Snyk      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "SAST reads your code; DAST attacks your │
│              │  app; both are required for security"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** SQL injection has been the #1 or #2 web vulnerability for 20+ years despite being well-understood and having known fixes (parameterized queries). SAST tools reliably detect string-concatenated SQL since ~2000. Explain the gap: (1) why developers still introduce SQL injection despite SAST tools available, (2) why ORM frameworks (Hibernate, JPA) reduced but didn't eliminate SQL injection (HQL injection, native queries, `@Query` with string concat), (3) the specific category of SQL injection SAST tools miss (second-order injection: stored user input later used in a query), and (4) how DAST tests specifically for second-order injection.

**Q2.** The "shift-left" security principle says: find vulnerabilities earlier = cheaper to fix. But there's a tension: SAST run on every commit will flag hundreds of issues in a legacy codebase, overwhelming the team. Describe the phased approach to introducing SAST in a 500,000-line legacy Java codebase: (1) baseline suppression (suppress all existing issues, only alert on new issues in changed files), (2) incremental remediation (fix 1 category per sprint), (3) quality gate escalation (start with CRITICAL only, add HIGH after 3 months), and (4) how you measure whether the program is actually improving security posture.
