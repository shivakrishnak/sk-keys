---
layout: default
title: "Security Test (SASTâ€”DAST)"
parent: "Testing"
nav_order: 1141
permalink: /testing/security-test-sast-dast/
number: "1141"
category: Testing
difficulty: â˜…â˜…â˜…
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

# 1141 â€” Security Test (SAST/DAST)

âš¡ TL;DR â€” Security testing verifies that software cannot be exploited. SAST (Static Application Security Testing) analyses source code for vulnerabilities without running it; DAST (Dynamic Application Security Testing) attacks a running application like a hacker would.

| #1141           | Category: Testing                                               | Difficulty: â˜…â˜…â˜… |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | CI-CD, Code Quality, HTTP and APIs                              |                 |
| **Used by:**    | Security Engineers, DevSecOps, SRE, Compliance                  |                 |
| **Related:**    | SonarQube, OWASP, Penetration Testing, Dependency Scanning, CVE |                 |

### ðŸ”¥ The Problem This Solves

WORLD WITHOUT IT:
A developer writes `String query = "SELECT * FROM users WHERE id = " + userId;` â€” a SQL injection vulnerability. It passes all unit tests, all integration tests, all load tests. It ships to production. An attacker sends `userId = "1 OR 1=1"` and downloads the entire users table. Without security testing, functional correctness tests miss security vulnerabilities entirely â€” because the code is functionally correct, it just responds to malicious input unexpectedly.

THE CRITICAL INSIGHT:
Security vulnerabilities are not bugs in the traditional sense. The code does exactly what the developer intended â€” it just also does what the attacker intended. Only security-specific testing can find them.

### ðŸ“˜ Textbook Definition

**SAST (Static Application Security Testing):** Analysis of source code, bytecode, or binary without executing the program. Finds: hardcoded credentials, SQL injection patterns, XSS patterns, insecure cryptography, path traversal. Tools: SonarQube, Checkmarx, Semgrep, SpotBugs.

**DAST (Dynamic Application Security Testing):** Testing a running application by sending malicious inputs â€” attacking it like a real adversary. Finds: authentication bypass, session management flaws, injection at runtime, server misconfiguration. Tools: OWASP ZAP, Burp Suite, Nikto.

**SCA (Software Composition Analysis):** Scans dependencies for known CVEs. Tools: Snyk, OWASP Dependency-Check, GitHub Dependabot.

### â±ï¸ Understand It in 30 Seconds

**One line:**
SAST = security code review at scale (automated); DAST = automated pen test against running app.

**One analogy:**

> SAST is a structural inspection of a building's blueprints for fire code violations (before the building is built). DAST is a fire marshal walking through the completed building, trying every door and exit to find actual hazards.

### ðŸ”© First Principles Explanation

OWASP TOP 10 (2021) â€” what security tests catch:

```
A01: Broken Access Control  â† DAST (try accessing /admin without auth)
A02: Cryptographic Failures  â† SAST (detect weak cipher usage in code)
A03: Injection (SQL, LDAP, OS) â† SAST + DAST (pattern + runtime test)
A04: Insecure Design        â† Threat modeling (manual)
A05: Security Misconfiguration â† DAST (probe headers, defaults)
A06: Vulnerable Components  â† SCA (dependency CVE scan)
A07: Auth/Session Failures  â† DAST (session fixation, brute force)
A08: Software Integrity     â† SAST + SCA (CI pipeline integrity)
A09: Logging Failures        â† SAST (check for sensitive data in logs)
A10: SSRF                   â† DAST (probe internal endpoints)
```

DEVSECOPS PIPELINE:

```
Developer commit â†’
  [SAST: Semgrep/SonarQube] â†’ scan on every PR, fail on HIGH severity
  [SCA: Snyk] â†’ scan dependencies, fail on CVSS â‰¥ 7.0
  [Secrets scan: Gitleaks/truffleHog] â†’ fail on any hardcoded credential
  â†“ (only if all pass)
Deploy to staging â†’
  [DAST: OWASP ZAP baseline scan] â†’ passive scan, no active attack
  â†“ (on release branch)
Deploy to pre-prod â†’
  [DAST: OWASP ZAP full scan] â†’ active attack simulation
  [Pen test: manual] â†’ quarterly, by external team
```

### ðŸ§ª Thought Experiment

SAST FINDS WHAT DAST MISSES:

```java
// SAST catches this immediately:
private static final String SECRET = "my-secret-key-12345"; // hardcoded credential

// SAST: "Hardcoded credential at UserService.java:42"
// DAST: cannot see this â€” it's in memory, not in HTTP responses
```

DAST FINDS WHAT SAST MISSES:

```
SAST on a JWT authentication endpoint: code looks correct
DAST test: send JWT with algorithm "none" (alg=none attack)
  â†’ server accepts the token without signature verification
  â†’ authentication bypass
SAST couldn't find this because the algorithm check was in a third-party library
  the library version had a known vulnerability that SAST didn't flag
```

### ðŸ§  Mental Model / Analogy

> SAST + DAST = a dual security audit. SAST is the **inside auditor** who reads all the source code, policies, and configurations looking for violations. DAST is the **external red team** who is given only the URL and tries every known attack. Both find different things; neither is complete without the other.

### ðŸ“¶ Gradual Depth â€” Four Levels

**Level 1:** SAST scans your code for security mistakes (like a spell-checker for vulnerabilities). DAST attacks your running app like a hacker would. Both are needed because they find different types of issues.

**Level 2:** Add SAST to your CI pipeline: SonarQube or Semgrep on every PR. Configure rules for your language (Java, JavaScript, Python). Set severity thresholds: block merge on HIGH/CRITICAL, warn on MEDIUM. Add SCA (Snyk/Dependabot) to fail builds with CVSS â‰¥ 7.0 dependencies. DAST: add OWASP ZAP baseline scan in staging pipeline (passive scan only â€” no active attack). Progress to ZAP full scan (active attack) in pre-prod environment only.

**Level 3:** SAST false positive management: SAST tools have 20-40% false positive rates; teams must triage and suppress confirmed false positives with in-code annotations (`// NOSONAR` for SonarQube). DAST scoping: define which URLs to include/exclude in scans; authenticated DAST (provide session cookie to scan authenticated areas); avoid scanning third-party URLs. IAST (Interactive Application Security Testing): instruments the running application (JVM agent) to observe security issues from the inside while DAST exercises it from the outside â€” lower false positive rate.

**Level 4:** Threat modeling (pre-SAST/DAST): before writing code, model threats using STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege). Threat modeling identifies design-level security issues that neither SAST nor DAST can find (e.g., "the design assumes only admins can access this endpoint, but there is no enforcement mechanism"). Shift-left security: the cost to fix a vulnerability grows exponentially from design â†’ code â†’ test â†’ production. NIST estimates: $100 to fix at design, $1,500 at code, $10,000 in QA, $30,000 in production.

### âš™ï¸ How It Works (Mechanism)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                SAST vs DAST COVERAGE MAP                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                          â”‚
â”‚  SAST (source code):          DAST (running app):       â”‚
â”‚  âœ“ Hardcoded secrets          âœ“ Auth bypass             â”‚
â”‚  âœ“ SQL injection patterns     âœ“ Session management      â”‚
â”‚  âœ“ Insecure crypto API use    âœ“ HTTP security headers    â”‚
â”‚  âœ“ Path traversal patterns    âœ“ XSS in responses        â”‚
â”‚  âœ“ Dependency vulnerabilities âœ“ CORS misconfiguration   â”‚
â”‚  âœ— Runtime auth bypass        âœ— Hardcoded secrets       â”‚
â”‚  âœ— Server misconfiguration    âœ— Logic-level code bugs   â”‚
â”‚                                                          â”‚
â”‚  TOGETHER: comprehensive coverage of OWASP Top 10       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### ðŸ”„ The Complete Picture â€” End-to-End Flow

```
Developer: adds new /api/admin/users endpoint
CI pipeline:
  1. SAST (Semgrep): scans controller code
     â†’ WARN: no @PreAuthorize annotation on admin endpoint
  2. Developer: adds @PreAuthorize("hasRole('ADMIN')")
  3. SAST re-run: PASS

Staging deployment:
  4. OWASP ZAP baseline scan:
     â†’ ALERT: missing X-Content-Type-Options header
  5. Developer: adds security headers in SecurityConfig
  6. ZAP re-run: PASS

Pre-prod:
  7. ZAP full active scan:
     â†’ attempts 500+ attack payloads (XSS, SQL injection, etc.)
     â†’ PASS: all rejected with 400/403
  8. Manual pen test: PASS

Result: security issues found and fixed BEFORE production
```

### ðŸ’» Code Example

{%- raw -%}
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
{%- endraw -%}

```java
// Spring Security: example of what SAST looks for
@RestController
@RequestMapping("/api")
public class UserController {

    // BAD: SAST flags this â€” no authorization check
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

### âš–ï¸ Comparison Table

|                 | SAST           | DAST             | SCA             | Manual Pen Test |
| --------------- | -------------- | ---------------- | --------------- | --------------- |
| When            | At build time  | At test time     | At build time   | Quarterly       |
| What            | Code patterns  | Runtime behavior | Dependency CVEs | Logic flaws     |
| False positives | High (20-40%)  | Low              | Low             | Very low        |
| Speed           | Fast (minutes) | Slow (hours)     | Fast            | Slow (days)     |
| Cost            | Low            | Medium           | Low             | High            |

### âš ï¸ Common Misconceptions

| Misconception                        | Reality                                                                            |
| ------------------------------------ | ---------------------------------------------------------------------------------- |
| "SAST is enough"                     | SAST misses runtime issues (auth bypass, server misconfiguration, logic flaws)     |
| "DAST replaces manual pen testing"   | DAST tools can't reason about business logic; manual pen testers find design flaws |
| "100% SAST clean = secure"           | SAST has 20-40% false negatives; "clean SAST" is necessary, not sufficient         |
| "Security testing slows development" | Shift-left: fixing in CI is 100Ã— cheaper than fixing in production                 |

### ðŸš¨ Failure Modes & Diagnosis

**1. Too Many SAST False Positives â†’ Team Ignores All Alerts**

Cause: Default SAST rules tuned for all languages/frameworks, not your specific codebase.
Fix: Tune rules for your framework (disable irrelevant rules, add custom rules). Require triage for every new HIGH alert before suppressing.

**2. DAST Scans Never Run Because They're Too Slow**

Cause: Full ZAP active scan takes 2-4 hours; not practical for every PR.
Fix: Run passive (baseline) scan on every PR (fast); active scan only on staging/release branches.

### ðŸ”— Related Keywords

- **Prerequisites:** CI-CD, HTTP and APIs, Code Quality
- **Builds on:** Penetration Testing, Threat Modeling, DevSecOps
- **Related:** SonarQube Quality Gate, OWASP, CVE, Dependency Scanning

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ SAST         â”‚ Code analysis, no execution, finds code  â”‚
â”‚              â”‚ patterns â†’ CI pipeline, every commit     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ DAST         â”‚ Attack running app â†’ staging/pre-prod    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ SCA          â”‚ Dependency CVEs â†’ every build            â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ TOOLS        â”‚ Semgrep, SonarQube, OWASP ZAP, Snyk      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "SAST reads your code; DAST attacks your â”‚
â”‚              â”‚  app; both are required for security"    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

**Q1.** SQL injection has been the #1 or #2 web vulnerability for 20+ years despite being well-understood and having known fixes (parameterized queries). SAST tools reliably detect string-concatenated SQL since ~2000. Explain the gap: (1) why developers still introduce SQL injection despite SAST tools available, (2) why ORM frameworks (Hibernate, JPA) reduced but didn't eliminate SQL injection (HQL injection, native queries, `@Query` with string concat), (3) the specific category of SQL injection SAST tools miss (second-order injection: stored user input later used in a query), and (4) how DAST tests specifically for second-order injection.

**Q2.** The "shift-left" security principle says: find vulnerabilities earlier = cheaper to fix. But there's a tension: SAST run on every commit will flag hundreds of issues in a legacy codebase, overwhelming the team. Describe the phased approach to introducing SAST in a 500,000-line legacy Java codebase: (1) baseline suppression (suppress all existing issues, only alert on new issues in changed files), (2) incremental remediation (fix 1 category per sprint), (3) quality gate escalation (start with CRITICAL only, add HIGH after 3 months), and (4) how you measure whether the program is actually improving security posture.
