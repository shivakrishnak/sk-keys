---
layout: default
title: "SAST (Static Analysis)"
parent: "CI/CD"
nav_order: 1007
permalink: /ci-cd/sast/
number: "1007"
category: CI/CD
difficulty: ★★☆
depends_on: Shift Left Testing, Pipeline, Static Analysis
used_by: DAST, SCA, Secret Scanning, Shift Left Testing
related: DAST, SCA, Code Quality, Dependency Scanning
tags:
  - cicd
  - security
  - devops
  - intermediate
  - bestpractice
---

# 1007 — SAST (Static Analysis)

⚡ TL;DR — SAST scans source code or compiled binaries without executing them, identifying security vulnerabilities and quality issues by analysing code patterns, data flows, and structural rules at CI pipeline time.

| #1007 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Shift Left Testing, Pipeline, Static Analysis | |
| **Used by:** | DAST, SCA, Secret Scanning, Shift Left Testing | |
| **Related:** | DAST, SCA, Code Quality, Dependency Scanning | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java developer writes a REST endpoint that concatenates user input directly into a SQL query: `"SELECT * FROM users WHERE id = " + userId`. The code looks correct at a glance. Code review misses it — reviewers are focused on business logic. QA doesn't test with malicious SQL input. The endpoint ships to production. A month later, an attacker discovers the SQL injection vulnerability, extracts the entire user database, and the company faces a data breach.

**THE BREAKING POINT:**
Human code review is inconsistent — reviewers get tired, overlook patterns, and lack specialised security training. Manual security testing covers selected paths, not all code. The same class of vulnerability appears repeatedly because there's no systematic pattern matching against known insecure code patterns.

**THE INVENTION MOMENT:**
This is exactly why SAST was created: automated, systematic pattern matching against known vulnerability signatures — finding the same class of bugs every time, on every line, on every commit, without reviewer fatigue.

---

### 📘 Textbook Definition

**SAST (Static Application Security Testing)** is a white-box security testing methodology that analyses application source code, bytecode, or binaries without executing the application. SAST tools scan code for known vulnerability patterns (SQL injection, XSS, command injection), insecure coding practices (hard-coded secrets, unsafe deserialization), and quality issues (null pointer dereferences, resource leaks). Analysis is performed via abstract syntax tree (AST) parsing, taint analysis (tracing user-controlled data through the code), control flow analysis, and pattern matching against curated vulnerability query databases. SAST runs in the CI pipeline and IDE, providing developers with findings before code reaches production.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SAST reads your code like a security expert — without running it — flagging dangerous patterns.

**One analogy:**
> SAST is like a factory's quality control inspector who reads the blueprint before building anything. By studying the blueprint, the inspector can identify structural weaknesses — "this beam can't hold the load" or "this electrical path creates a short circuit" — without having to actually build and test the structure. The inspection happens at design time, not disaster time.

**One insight:**
SAST's power is **systematic coverage at zero runtime cost**: it analyses 100% of code paths, including error-handling branches and edge cases that manual testing might never exercise. Its limitation is the false positive problem — pattern-matching can confuse safe patterns with dangerous ones, requiring tuning and developer education to reach high signal-to-noise ratios.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. SAST runs WITHOUT executing the code — no deployment, no runtime environment needed.
2. SAST analyses the code as text/AST — finding patterns, not behaviours.
3. SAST cannot find all vulnerabilities — only those with statically-detectable patterns.

**DERIVED DESIGN:**
SAST tools work in layers of increasing sophistication:
- **Pattern matching** (basic): regex-like rules on source text — fast but high false positive rate.
- **AST analysis**: parse into abstract syntax tree, match against structural rules — catches more patterns, fewer false positives.
- **Taint analysis** (advanced): tracks the flow of untrusted user input through the code graph. If `userId` comes from `request.getParameter("id")` (source = tainted) and flows to `query += userId` (sink = SQL execution) without sanitisation — that's a SQL injection finding.

Taint analysis is the key technique that separates sophisticated SAST (CodeQL, Semgrep Pro) from simple pattern matchers. It can trace untrusted data across function calls, class boundaries, and control flow branches.

**THE TRADE-OFFS:**
**Gain:** Finds security vulnerabilities systematically at commit time. Scales with the codebase. Language-agnostic tools (Semgrep) work across polyglot codebases.
**Cost:** False positive rate can be high without tuning. SAST cannot find runtime-only vulnerabilities (authentication bypass, business logic flaws). Deep taint analysis increases scan time. Tool licensing cost.

---

### 🧪 Thought Experiment

**SETUP:**
Same SQL injection scenario. Two developers add the same vulnerable code. Developer A's team uses SAST in CI; Developer B's team does not.

**WHAT HAPPENS WITHOUT SAST:**
Developer B pushes the vulnerable endpoint. CI runs unit tests (pass — tests use valid inputs). Staging smoke tests pass. Production: endpoint live. Penetration test 6 months later: SQL injection found. CVSS score 9.8 (Critical). 48-hour remediation sprint.

**WHAT HAPPENS WITH SAST:**
Developer A pushes to a PR. CI SAST scan using CodeQL. Within 8 minutes, the PR shows: "SQL injection: user-controlled value flows to database query without escaping." The finding links to the exact line and suggests parameterised queries. Developer A fixes it before merge. The vulnerability never reaches staging.

**THE INSIGHT:**
SAST finds a class of vulnerability that would require a security expert to review every line manually. It scales systematic security review to every commit, automatically.

---

### 🧠 Mental Model / Analogy

> SAST is like a spell-checker and grammar checker combined — but for code security. The spell-checker (pattern matching) finds obvious errors instantly. The grammar checker (taint analysis) understands context — "user input flows into this sink" the same way grammar-check understands "subject agrees with verb." Neither reads meaning; both check structure systematically.

- "Spell-check red underline" → simple pattern-match finding (hard-coded credential)
- "Grammar check blue underline" → taint analysis finding (data flow from source to sink)
- "Spell-check false positive ('colour' is valid in British English)" → SAST false positive (pattern matched but code is safe in context)
- "Ignoring spell-check" → suppressing SAST finding (requires justification)

Where this analogy breaks down: spell-check catches errors in isolation; SAST's most valuable feature is inter-procedural taint analysis — tracing data through multiple function calls. This is far more complex than checking individual words.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
SAST is an automated tool that reads your code and looks for common security mistakes — like storing passwords without encryption or letting user input control database queries without safety checks. It finds these problems without running the application, just like a grammar checker finds errors without reading the document aloud.

**Level 2 — How to use it (junior developer):**
Integrate a SAST tool in your CI pipeline: GitHub CodeQL (free for public repos), Semgrep (OSS), SonarQube, or Checkmarx. In GitHub Actions, add the CodeQL action — it instruments your build and analyses the compiled code. Results appear in the PR Security tab. Findings include: severity (Critical/High/Medium/Low), CWE category (e.g., CWE-89 SQL Injection), and the exact line. Fix Critical/High findings before merge; document justifications for false positives.

**Level 3 — How it works (mid-level engineer):**
Modern SAST tools like CodeQL work in two phases: (1) **Database creation** — instrument the build, capture the code graph (AST + control flow + data flow) into a queryable database; (2) **Query execution** — run predefined or custom queries against the database. A SQL injection query finds: "does any value from `HttpServletRequest.getParameter()` flow to `Statement.execute()` without passing through a sanitisation function?" The power is inter-procedural analysis — the flow can cross function and class boundaries. False positive rate is reduced by adding sanitisation functions to the query's "clean sources."

**Level 4 — Why it was designed this way (senior/staff):**
SAST evolved from lint tools (1970s) through language-specific pattern matchers to today's semantic analysis tools. The key design challenge is precision vs recall: simple pattern matchers have high recall (find all SQL strings) but low precision (many false positives). Taint analysis has higher precision but is computationally expensive (graph algorithms on large code bases). CodeQL's design — building a queryable database from the code — was chosen to allow ad-hoc security research queries, not just predefined rules. Semgrep's design — AST pattern matching with semantic variables — was optimised for easy custom rule writing. The OWASP Top 10 and CWE taxonomy provide the vulnerability classification framework that all SAST tools map findings to.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│         SAST EXECUTION (CODEQL)             │
├─────────────────────────────────────────────┤
│  Phase 1: Build Instrumentation             │
│  - codeql database create                   │
│  - Compile with instrumented JDK            │
│  - Capture: AST, CFG, DFG                   │
│    (Abstract Syntax / Control Flow /        │
│     Data Flow Graphs)                       │
│                                             │
│  Phase 2: Query Execution                   │
│  - Run QL queries on the captured graph     │
│  - SQL injection query:                     │
│    source = HttpServletRequest.getParameter │
│    sink = Statement.execute                 │
│    flow = dataflow(source → sink)           │
│    filter = "no sanitisation in flow"       │
│  - Match found → finding: line 47           │
│                                             │
│  Phase 3: Result Upload                     │
│  - SARIF format uploaded to GitHub          │
│  - Appears in PR Security tab               │
│  - Code annotation at vulnerable line       │
└─────────────────────────────────────────────┘
```

**Taint analysis trace** (conceptual):
```
// userId comes from HTTP request (TAINTED SOURCE)
String userId = request.getParameter("id");  // line 23

// Flows through helper method (propagates taint)
String sanitized = processInput(userId);     // line 31
// processInput() doesn't sanitise — still tainted

// Flows into SQL query (TAINTED SINK)
String sql = "SELECT * FROM users WHERE id=" + sanitized; // line 47
stmt.execute(sql);  // SAST: SQL injection at line 47
// FIX: use PreparedStatement with parameterised query
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (CI pipeline):**
```
Developer pushes PR
  → CI: Build stage compiles code
  → CodeQL: instruments build, creates database
  → CodeQL: runs security-extended query suite [← YOU ARE HERE]
  → 0 critical/high findings
  → Results: uploaded as SARIF to GitHub
  → PR Security tab: "No vulnerabilities detected"
  → Code review proceeds, merge approved
```

**FAILURE PATH:**
```
CodeQL: SQL injection found on line 47
  → SARIF with finding uploaded
  → PR Security tab: "1 Critical: SQL Injection"
  → GitHub: annotation on line 47 in the diff view
  → Branch protection: "Required security scan failed"
  → Merge blocked
  → Developer: fix with PreparedStatement → repush
  → Finding resolved → merge unblocked
```

**WHAT CHANGES AT SCALE:**
At 200 repositories, SAST results must be aggregated in a security dashboard (GitHub Advanced Security, Snyk, Veracode) — not reviewed per-pipeline. The security team sees organisation-wide finding trends: which CWE categories appear most, which repos have outstanding critical findings. SLA-based remediations: Critical = fix in 7 days, High = 30 days, tracked in the dashboard.

---

### 💻 Code Example

**Example 1 — CodeQL in GitHub Actions:**
```yaml
# .github/workflows/codeql.yml
name: CodeQL SAST

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '30 5 * * 1'  # weekly scan on main

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      actions: read

    strategy:
      matrix:
        language: [ java ]

    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended  # more thorough than default

      - name: Build (CodeQL intercepts the build)
        run: mvn --batch-mode compile

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:java"
          upload: true   # upload to GitHub Security tab
```

**Example 2 — Semgrep for custom rules:**
```yaml
# .semgrep.yml — custom rule for project-specific patterns
rules:
  - id: sql-string-concat
    patterns:
      - pattern: |
          "$QUERY" + $USER_INPUT
      - pattern-not: |
          PreparedStatement.$METHOD(...)
    message: |
      SQL query built by string concatenation.
      Use PreparedStatement with parameterised queries.
    languages: [ java ]
    severity: ERROR
    metadata:
      cwe: [ "CWE-89: SQL Injection" ]
      confidence: HIGH
```

```bash
# Run in CI
semgrep --config=.semgrep.yml \
  --config=p/java-security-audit \   # community rules
  --error \                           # exit 1 on findings
  src/
```

**Example 3 — BAD vs GOOD: suppress vs fix:**
```java
// BAD: suppress without fixing
// NOSONAR SQL injection — developer added suppression
// to silence the alert, not to fix the problem
String sql = "SELECT * FROM users WHERE id=" + userId;
stmt.execute(sql); //NOSONAR

// GOOD: fix the vulnerability
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE id = ?");  // parameterised
stmt.setString(1, userId);               // safe binding
ResultSet rs = stmt.executeQuery();
```

---

### ⚖️ Comparison Table

| Tool | Approach | Languages | False Positive Rate | Cost | Best For |
|---|---|---|---|---|---|
| **CodeQL** | Taint analysis + queries | Multi (Java, JS, Python, C++) | Medium-Low | Free for OSS / GH Advanced Security | GitHub repos, deep analysis |
| Semgrep | AST pattern matching | 30+ languages | Medium | OSS / paid for Pro | Custom rules, polyglot |
| SonarQube | AST + rules | 30+ languages | Medium-High | Community (free) / Enterprise | Code quality + security |
| Checkmarx | Taint analysis | Enterprise-grade | Low (tuned) | Enterprise | Enterprise, compliance |
| Snyk Code | AI-assisted patterns | Multi | Low | Free tier / paid | Developer-first experience |

How to choose: Use CodeQL for GitHub repositories — it's deeply integrated and free for OSS. Use Semgrep for custom rules or polyglot codebases. Use SonarQube when you need both code quality and security in one platform with a rich dashboard.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SAST and DAST are the same thing | SAST analyses source code without running the app. DAST tests the running application with simulated attacks. They find different vulnerability classes and complement each other |
| SAST finds all security vulnerabilities | SAST only finds statically-detectable patterns. Authentication bypass, race conditions, and business logic flaws require DAST or manual penetration testing |
| SAST zero findings means secure code | SAST scans for known patterns. Novel vulnerabilities, logic bugs, and infrastructure misconfiguration are invisible to SAST |
| Suppressing a SAST finding fixes the vulnerability | `//NOSONAR` silences the alert; it does not fix the code. Suppression should only be used when the finding is a confirmed false positive, with justification documented |

---

### 🚨 Failure Modes & Diagnosis

**1. SAST Scan Too Slow — Teams Bypass It**

**Symptom:** SAST stage takes 25+ minutes. Teams route around it with pipeline skips or ignore results.

**Root Cause:** Over-inclusive scanning (all code, all queries). No incremental scanning (rescanning unchanged files).

**Diagnostic:**
```bash
# CodeQL: check database creation time vs query time
# GitHub Actions: view step timing
gh run view <run-id> --log | grep -E "codeql|timing"
```

**Fix:** Use incremental analysis. Scan only changed files in PRs (full scan on main/nightly):
```yaml
- name: Analyze (PR: incremental)
  uses: github/codeql-action/analyze@v3
  with:
    # For PRs: analyze only changed files
    add-snippet-filter: true
```

**Prevention:** Set a SAST scan time budget. 15 minutes max for PR-blocking scans.

---

**2. High False Positive Rate Creates Alert Fatigue**

**Symptom:** Developers close SAST findings instantly as "false positive" without reading them. A real SQL injection finding is dismissed.

**Root Cause:** Default rules include low-confidence patterns. No tuning has been done for the team's technology stack.

**Diagnostic:**
```bash
# Audit dismissed findings over 3 months
# GitHub Security tab: filter by state="dismissed" + reason
# Measure: true positive rate = (true findings / total findings)
```

**Fix:** Configure to run only HIGH/CRITICAL confidence queries. Add custom suppressions for known safe patterns (framework-level validation):
```yaml
# CodeQL: exclude low-confidence queries
with:
  queries: +security-extended  # start from security-extended
  # Exclude path traversal queries if framework handles it:
config-file: .github/codeql/config.yml
```

```yaml
# .github/codeql/config.yml
query-filters:
  - exclude:
      problem.severity: warning  # only errors and recommendations
```

**Prevention:** Track and report on false positive rate monthly. Target >80% true positive rate.

---

**3. Secret Committed Despite SAST Secret Scanning**

**Symptom:** A database password is committed to the repo and SAST didn't catch it.

**Root Cause:** SAST is not the right tool for secret detection — it analyses security patterns in code logic. Secret scanning is a separate tool (git-secrets, truffleHog, GitHub Secret Scanning).

**Diagnostic:**
```bash
# Scan repo history for secrets
trufflehog git https://github.com/myorg/myapp \
  --only-verified
# Or use git-secrets
git secrets --scan-history
```

**Fix:** Supplement SAST with dedicated secret scanning. Add pre-commit hook:
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: [ '--baseline', '.secrets.baseline' ]
```

**Prevention:** Never rely on SAST alone for secret detection. Use secret scanning as a separate, independent control.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Shift Left Testing` — SAST is the security application of the shift-left principle; understanding the principle provides the context
- `Pipeline` — SAST runs as a stage in the CI pipeline; pipeline structure determines when and how SAST runs
- `Static Analysis` — SAST is a security-focused application of static analysis; understanding code analysis generically is foundational

**Builds On This (learn these next):**
- `DAST (Dynamic Analysis)` — complements SAST by testing running applications for vulnerabilities SAST cannot detect
- `SCA (Software Composition Analysis)` — scans third-party dependencies for known CVEs — a separate but related security scan
- `Secret Scanning` — detects committed credentials — a specific form of SAST that requires dedicated tooling

**Alternatives / Comparisons:**
- `DAST` — runtime complement to SAST; finds vulnerabilities requiring application execution
- `Code Quality` — broader static analysis that includes non-security quality metrics (complexity, duplication)
- `Dependency Scanning` — scans imported libraries for known vulnerabilities (SAST scans your code; dependency scanning scans third-party code)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Static code security scan: find           │
│              │ vulnerabilities without running the code  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Security vulnerabilities in code that     │
│ SOLVES       │ human review misses (SQL injection, XSS)  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Taint analysis (source → sink flow) is    │
│              │ what distinguishes deep SAST from pattern │
│              │ matching — it's why CodeQL finds what     │
│              │ grep-based scanners miss                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any application handling user input or    │
│              │ accessing databases, files, or networks   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ SAST alone is insufficient for compliance;│
│              │ combine with DAST, SCA, and pen testing   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Systematic coverage + zero runtime vs     │
│              │ false positives and scan time overhead    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A security expert reading every line —   │
│              │  while you write it, not after you ship"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DAST → SCA → Dependency Scanning          │
│              │ → Secret Scanning → SBOM                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A CodeQL scan on your Java microservice consistently produces 23 findings per run. After investigation: 8 are genuine SQL injection risks, 11 are false positives from a safely-wrapped DAO layer that CodeQL doesn't recognise as safe, and 4 are low-severity null pointer issues in test code. Design the complete suppression and tuning strategy: which findings to suppress, how to document the justification, how to configure CodeQL to avoid reintroducing the false positives on future code additions, and how to periodically audit that no real vulnerabilities are hidden in suppressions.

**Q2.** SAST found a path traversal vulnerability: a file download endpoint uses `../` in the filename to traverse directories. The developer argues: "Our framework validates the filename first — this is a false positive." The security engineer argues: "CodeQL's taint analysis shows the path flows from the request to `FileInputStream` without passing through the framework validator." Who is correct, and what evidence would definitively resolve the dispute? What would you examine in the source code to determine whether the framework validation is on the correct code path?

