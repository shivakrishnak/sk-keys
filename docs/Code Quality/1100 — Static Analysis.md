---
layout: default
title: "Static Analysis"
parent: "Code Quality"
nav_order: 1100
permalink: /code-quality/static-analysis/
number: "1100"
category: Code Quality
difficulty: ★★☆
depends_on: Linting, Code Standards, AST
used_by: SonarQube, SAST, Code Review, CI/CD Pipeline
related: Linting, SonarQube, SpotBugs, PMD
tags:
  - bestpractice
  - intermediate
  - cicd
  - security
  - devops
---

# 1100 — Static Analysis

⚡ TL;DR — Static analysis examines source code without executing it to detect bugs, security vulnerabilities, code smells, and quality violations that linting cannot find.

| #1100 | Category: Code Quality | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Linting, Code Standards, AST | |
| **Used by:** | SonarQube, SAST, Code Review, CI/CD Pipeline | |
| **Related:** | Linting, SonarQube, SpotBugs, PMD | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java method receives a `User` object from an external API call. Internally, it accesses `user.getProfile().getAddress().getCity()`. The API sometimes returns a user with no profile — `getProfile()` returns `null`. The null pointer dereference causes a `NullPointerException` in production. The bug was always there. No linter caught it: naming and formatting are fine. No test caught it: the happy path always had a profile. It required a real production request to manifest.

**THE BREAKING POINT:**
As codebases grow, entire classes of bugs — null dereferences, SQL injections via string concatenation, insecure random number generation, infinite loops — cannot be detected by style checkers or by tests that only run happy paths. These bugs are structural. They exist in the code's *control flow and data flow*, not just its appearance.

**THE INVENTION MOMENT:**
This is exactly why **static analysis** was created: to analyse code as data — following every execution path, tracking data flow, detecting structural patterns that correlate with real bugs — without ever running the code.

---

### 📘 Textbook Definition

**Static analysis** is the automated examination of source code, compiled bytecode, or ASTs without execution, using program analysis techniques to detect defects, security vulnerabilities, code quality violations, and anti-patterns. Static analysis goes beyond linting by applying **dataflow analysis** (tracking how data moves through the program — detecting null pointer dereferences, uninitialized variables, SQL injection via user input reaching an SQL constructor), **control flow analysis** (detecting unreachable code, infinite loops, missing return statements), **inter-procedural analysis** (following calls across multiple methods/classes), and **taint analysis** (tracking untrusted input through the program to sensitive sinks). Key tools: **SpotBugs** (Java — bytecode-level bug detection), **PMD** (Java — AST-level rules), **SonarQube** (multi-language — integrates multiple analysis engines), **Semgrep** (multi-language pattern-based analysis), **Fortify/Veracode** (enterprise security-focused). Static analysis is a subcategory of **SAST (Static Application Security Testing)** when applied to security.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Automated deep code inspection that finds bugs by analysing all possible execution paths without running the code.

**One analogy:**
> Static analysis is like reading a map before a road trip to find potential dead ends. You don't have to drive every road to know which ones lead to cliffs — you can see it on the map. Static analysis reads the "map" of your code (data and control flow) and identifies paths that could lead to crashes, security holes, or infinite loops, without ever taking those journeys in production.

**One insight:**
Linting checks *how code is written*; static analysis checks *what code does*. A linter can tell you a method name is wrong. Static analysis can tell you this method always returns null when the input is negative — without executing the method once.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Code is data. Control and data flow through a program can be modelled as a graph (Control Flow Graph, Data Flow Graph) and analysed mathematically.
2. Analysing all execution paths statically is computationally expensive but produces no false executions — no side effects, no production impact.
3. Static analysis trades completeness for soundness: it may miss some bugs (true negatives) and flag some valid code (false positives), but it never crashes your production system.

**DERIVED DESIGN:**
Because code can be modelled as a graph, graph algorithms can detect structural properties: "Is there any path from this method entry to an exit that does not initialise this variable?" This is essentially a reachability problem on the control flow graph. Null pointer analysis is a data flow problem: "Can the value flowing through this expression path be null at this dereference point?" These analyses are mechanically impossible for humans to perform consistently across large codebases.

**THE TRADE-OFFS:**
Gain: Detects entire classes of bugs (null dereferences, SQL injections, resource leaks) that linting and testing may miss. Runs on every line of code, not just tested paths.
Cost: False positives (flagging valid code) create noise that developers learn to ignore. Deep inter-procedural analysis is computationally expensive — may take minutes. May require code annotation to reduce false positives.

---

### 🧪 Thought Experiment

**SETUP:**
A Java service has a method `processOrder(Order order)`. The `Order` can have a null `discountCode`. The method does: `order.getDiscountCode().toLowerCase()`. There is no null check.

**WHAT HAPPENS WITHOUT STATIC ANALYSIS:**
- Linter passes: the code is correctly named and formatted.
- Unit tests pass: the test data always includes a discount code.
- Integration tests pass: test orders always have a discount code.
- Code deploys to production. On day one, a customer submits an order without a discount code.
- `NullPointerException` at `order.getDiscountCode().toLowerCase()`.
- Production order processing fails for all customers without discount codes.
- Incident opened. Developer finds the line. Adds null check. Redeploys.
- Total impact: 2 hours of failed orders.

**WHAT HAPPENS WITH STATIC ANALYSIS:**
- SpotBugs/PMD runs during the build.
- Flags: `NullPointerException: getDiscountCode() may return null — see return type annotation or calling context`.
- Developer sees the flag during local development.
- Adds null check: `Optional.ofNullable(order.getDiscountCode()).map(String::toLowerCase).orElse("")`
- Bug never reaches production.

**THE INSIGHT:**
Static analysis catches the null path that no test ran. Tests only run the paths they test. Static analysis runs *every* structurally possible path.

---

### 🧠 Mental Model / Analogy

> Static analysis is like a safety inspector who reads blueprints before a building is constructed. The inspector doesn't wait for the building to collapse — they examine the plans and say: "this load-bearing wall is missing; this fire exit is too narrow; this electrical panel is incorrectly grounded." They find structural defects in the design, not in the result. Static analysis reads the "blueprint" of your code and finds structural defects before code reaches users.

- "Reading blueprints" → analysing AST and control/data flow graph
- "Load-bearing wall missing" → null pointer dereference on every code path
- "Fire exit too narrow" → resource leak (Stream never closed)
- "Electrical panel incorrectly grounded" → SQL injection via string concatenation
- "Building collapses" → production `NullPointerException`

Where this analogy breaks down: building blueprints are deterministic — if a wall is missing, the building definitely falls. Static analysis has false positives — it flags code that *could* fail structurally but may not in practice due to caller guarantees the tool cannot see.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Static analysis is a tool that reads your code and finds problems — deeper problems than a spell-checker. While a linter checks that your code looks right, static analysis checks that your code *behaves correctly* in all situations: "if this value is null, your program crashes"; "if this user input is passed directly to the database, you have a security hole." It finds these without running the program at all.

**Level 2 — How to use it (junior developer):**
Run the static analysis tool as part of your build: `mvn spotbugs:check` for SpotBugs, or `mvn pmd:check` for PMD in Java. In your IDE, install the SpotBugs or SonarLint plugin — it runs analysis as you type and highlights issues inline. Read every warning, understand it, then fix it. When a flag says "potential null pointer dereference", find where the value could be null and add a null check or use `Optional`. Do not suppress warnings without understanding them. A suppressed SpotBugs warning is a bug you chose not to fix.

**Level 3 — How it works (mid-level engineer):**
Static analysis tools build one or more of these representations: **AST** (syntactic structure), **CFG** (Control Flow Graph — all execution paths through a method), **DFG** (Data Flow Graph — how values propagate), **Call Graph** (method invocation relationships). Rules are predicates over these graphs. A "null dereference" rule asks: "Is there a path in the CFG from method entry to this field dereference where the value is null according to the DFG?" **Taint analysis** (used for security — SQL injection, XSS) asks: "Is there a path from a `Source` (user input) to a `Sink` (SQL constructor, HTML output) without passing through a `Sanitiser` (input validation, escaping)?" Inter-procedural analysis follows these paths across method calls — expensive but necessary for accurate results.

**Level 4 — Why it was designed this way (senior/staff):**
Static analysis is fundamentally a problem in **program verification** — the mathematical field concerned with proving properties of programs. Full program verification (proving a program always does what the spec says) is undecidable (Rice's Theorem). Practical static analysis accepts incomplete analysis: it finds *some* real bugs while producing *some* false positives, rather than claiming completeness. This is why different tools have different false positive profiles: tools with higher recall (fewer missed bugs) tend to have higher false positive rates, and vice versa. This is also why **annotation-driven analysis** (using `@NonNull`, `@Nullable`, `@Tainted` annotations) improves precision: human annotations reduce the analysis search space, allowing tools to make more precise claims. The evolution toward **AI-powered static analysis** (GitHub Copilot Autofix, Snyk Code) uses ML to flag patterns found in large vulnerability corpora, reducing false positives through pattern matching rather than formal proof.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  STATIC ANALYSIS ENGINE                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  Source / Bytecode                              │
│         │                                       │
│         ▼                                       │
│  AST Builder → Abstract Syntax Tree             │
│         │                                       │
│         ├─→ CFG Builder → Control Flow Graph    │
│         │   (all execution paths in method)     │
│         │                                       │
│         ├─→ DFG Builder → Data Flow Graph       │
│         │   (value propagation analysis)         │
│         │                                       │
│         └─→ Call Graph (inter-procedural)       │
│                                                 │
│  Rule Engine applies rules to graphs:           │
│  - NullDeref: DFG + CFG analysis                │
│  - SqlInjection: Taint analysis (source->sink)  │
│  - ResourceLeak: Lifecycle analysis             │
│  - UnreachableCode: CFG dead-path detection     │
│         │                                       │
│         ▼                                       │
│  Violations: file:line severity rule message    │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes processOrder(Order order)
  → IDE SonarLint runs in real-time
  → flags: "order.getDiscountCode() may be null"
    [← YOU ARE HERE — static analysis fires]
  → developer adds null check
  → no violation in CI static analysis step
  → PR review focuses on business logic
  → production: NullPointerException never occurs
```

**FAILURE PATH:**
```
SpotBugs finds 350 issues on first run
  → team disables all flagged rules
  → or sets threshold: "fail only if > 500 issues"
  → static analysis becomes security theater
  → real bugs not fixed, just hidden
  → production exceptions continue
→ Fix: triage findings, fix high-severity issues,
  document why low-severity findings are accepted
```

**WHAT CHANGES AT SCALE:**
At enterprise scale, static analysis results are tracked over time: "quality gate" — the build fails if the number of new issues (not total issues) exceeds a threshold. This prevents legacy debt from blocking all new development while still preventing new bugs from being introduced. SonarQube's "new code" concept: only code changed in the current PR is subject to strict quality gates.

---

### 💻 Code Example

**Example 1 — SpotBugs: null dereference detection (Java):**
```java
// BAD — SpotBugs flags NP_NULL_ON_SOME_PATH
public String processOrder(Order order) {
    // order.getDiscountCode() may return null
    // if no discount is applied
    return order.getDiscountCode().toLowerCase(); 
    // NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE
}

// GOOD — null-safe
public String processOrder(Order order) {
    return Optional.ofNullable(order.getDiscountCode())
        .map(String::toLowerCase)
        .orElse("");
}
```

**Example 2 — PMD: SQL injection detection:**
```java
// BAD — PMD flags SqlInjection
public List<User> findUser(String name, Connection conn) 
    throws SQLException {
    // Direct string concatenation with user input
    String query = "SELECT * FROM users WHERE name = '" 
        + name + "'";           // SQL_INJECTION
    return conn.createStatement()
               .executeQuery(query);
}

// GOOD — prepared statement
public List<User> findUser(String name, Connection conn)
    throws SQLException {
    String query = 
        "SELECT * FROM users WHERE name = ?";
    PreparedStatement ps = conn.prepareStatement(query);
    ps.setString(1, name);
    return ps.executeQuery();
}
```

**Example 3 — SpotBugs Maven plugin:**
```xml
<!-- pom.xml -->
<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
  <version>4.7.3.6</version>
  <configuration>
    <!-- fail on HIGH severity bugs only -->
    <threshold>High</threshold>
    <!-- exclude generated code -->
    <excludeFilterFile>
      spotbugs-exclude.xml
    </excludeFilterFile>
  </configuration>
  <executions>
    <execution>
      <goals><goal>check</goal></goals>
    </execution>
  </executions>
</plugin>
```

---

### ⚖️ Comparison Table

| Tool | Analysis Type | Language | Detects | Best For |
|---|---|---|---|---|
| Checkstyle | Style only | Java | Naming, formatting | Style enforcement |
| **PMD** | AST rules | Java | Code smells, simple bugs | Java quality |
| **SpotBugs** | Bytecode | Java | Null ptr, concurrency bugs | Java bug detection |
| **SonarQube** | Multi-engine | Multi | All of the above + security | Enterprise quality gate |
| **Semgrep** | Pattern matching | Multi | Custom patterns, security | Security + custom rules |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Static analysis and linting are the same | Linting checks style and simple patterns. Static analysis performs data flow, control flow, and inter-procedural analysis — finding bugs linting cannot see. |
| Static analysis finds all bugs | Static analysis cannot prove program correctness. It finds bugs that match its rule patterns with a false positive/negative trade-off. |
| Passing static analysis means the code is secure | Static analysis catches known patterns (e.g., SQL injection via concatenation). It may miss novel attack vectors, logical security flaws, or injection patterns the tool doesn't model. |
| 0 static analysis warnings means quality is high | Tools may be misconfigured with too-low thresholds, or entire rule categories may be disabled. Zero violations may mean no violations, or may mean no rules are checking for the violations. |
| False positives are acceptable to suppress silently | Every suppressed false positive should be documented with the reason. Undocumented suppressions are indistinguishable from suppressed real bugs. |

---

### 🚨 Failure Modes & Diagnosis

**1. Analysis Runs but No One Acts on Results**

**Symptom:** SonarQube shows 4,000 issues. Quality gate threshold is set to 5,000. Nobody fixes issues; the count slowly climbs toward the threshold.

**Root Cause:** Issues were never triaged and assigned. No team member owns the quality gate outcome. Threshold is too lenient to create pressure.

**Diagnostic:**
```bash
# Check SonarQube project metrics via API
curl "https://sonar.example.com/api/measures/component\
?component=my-project\
&metricKeys=open_issues,code_smells,bugs,vulnerabilities"
# Track trend: increasing = ignored
```

**Fix:** Set "new code" quality gate (fail on new issues, not total). Assign a code quality champion per team. Run weekly triage sessions until backlog is < 100 issues.

**Prevention:** Start with "new code" quality gate from day one. Never allow known issues to accumulate without a remediation plan.

---

**2. High False Positive Rate — Developers Ignore All Warnings**

**Symptom:** Developers view static analysis as noise. PRs show hundreds of static analysis annotations; none are fixed. The tool runs but has zero impact.

**Root Cause:** Rules are misconfigured for the codebase, or too many aggressive rules are enabled for legacy code. Developers have learned that "most are false positives" and stopped reading them.

**Diagnostic:**
```bash
# Check SpotBugs exclusion config
cat spotbugs-exclude.xml
# No excludes with legacy codebase = many false positive

# Sample 10 recent warnings manually
# What percentage are real issues?
mvn spotbugs:gui   # Review violations interactively
```

**Fix:** Triage last 50 reported bugs. Identify false-positive categories. Add exclusion rules or reduce enabled rule categories to those with < 10% false positive rate for your codebase.

**Prevention:** When enabling a new static analysis tool, run in "report-only" mode first. Tune the configuration before enabling as a CI gate.

---

**3. Analysis Missing Critical Inter-Procedural Paths**

**Symptom:** Static analysis passes, but SQL injection exists: user input flows from a REST controller through three service layers to a repository method that builds a raw query string. The injection path spans multiple classes.

**Root Cause:** The tool is configured for single-method analysis only (no inter-procedural analysis), or taint analysis is not enabled.

**Diagnostic:**
```bash
# Check if taint analysis is enabled in SonarQube
# (requires SonarQube Developer Edition or above)
# Or: use Semgrep with inter-procedural taint rules
semgrep --config "p/java-security-audit" src/
```

**Fix:** Enable inter-procedural taint analysis in SonarQube (Developer Edition) or add Semgrep with security rules as a complementary tool.

**Prevention:** Use SAST tools that explicitly support taint analysis for security-critical codebases.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linting` — static analysis extends linting to deeper code properties
- `AST (Abstract Syntax Tree)` — the data structure both linting and static analysis operate on

**Builds On This (learn these next):**
- `SonarQube` — the leading static analysis platform for enterprise teams
- `SAST` — security-focused application of static analysis
- `SpotBugs / PMD` — specific Java static analysis tools

**Alternatives / Comparisons:**
- `Dynamic Analysis (DAST)` — analyses code during execution; finds runtime issues static analysis misses
- `Linting` — simpler, faster subset; style and simple pattern checks only

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automated deep code analysis via control/ │
│              │ data flow graphs — without execution      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Entire classes of bugs (null dereference, │
│ SOLVES       │ SQL injection) invisible to linters/tests │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Linting checks how code looks; static     │
│              │ analysis checks what code does on all     │
│              │ possible execution paths                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every production codebase; mandatory for  │
│              │ security-sensitive systems                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip; but tune false-positive rate  │
│              │ before adding as mandatory CI gate        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Deep bug detection vs. false positive     │
│              │ noise and longer analysis time            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Safety inspector for code — reads the    │
│              │  blueprint and flags structural collapses"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SonarQube → SpotBugs → SAST               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your static analysis tool reports 3,000 open issues across a 200,000-line Java service. The CI quality gate currently allows up to 3,500 issues before failing (so your build still passes). You are tasked with getting the project to 0 high-severity bugs and implementing a quality gate that prevents regression, without halting feature development for months. Design the complete strategy: triage, remediation, quality gate configuration, and enforcement rollout.

**Q2.** Taint analysis can detect SQL injection across inter-procedural call chains. However, taint analysis has a high false positive rate for complex codebases. A security team wants 100% taint analysis coverage; a development team says it will make the tool "unusable" due to false positives. How would you design a taint analysis configuration that satisfies both concerns — providing meaningful SQL injection detection without making the tool's output a noise source developers learn to ignore?

