---
layout: default
title: "Line Coverage"
parent: "Code Quality"
nav_order: 1109
permalink: /code-quality/line-coverage/
number: "1109"
category: Code Quality
difficulty: ★★☆
depends_on: Code Coverage, Unit Test, CI/CD Pipeline
used_by: SonarQube, Branch Coverage, Code Coverage
related: Branch Coverage, Code Coverage, Mutation Testing
tags:
  - bestpractice
  - intermediate
  - testing
  - cicd
  - java
---

# 1109 — Line Coverage

⚡ TL;DR — Line coverage measures the percentage of source code lines executed during a test run, providing the simplest baseline measure of which code has been exercised by tests.

| #1109 | Category: Code Quality | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Code Coverage, Unit Test, CI/CD Pipeline | |
| **Used by:** | SonarQube, Branch Coverage, Code Coverage | |
| **Related:** | Branch Coverage, Code Coverage, Mutation Testing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team writes tests. Tests pass. The team believes they have "good coverage." A developer later adds an if-else block to handle a new edge case. The else branch — handling the case where the input is invalid — is never tested. Nobody knows because there is no measurement. The else branch has a bug. It ships to production and causes an error for 2% of users.

**THE BREAKING POINT:**
Testing without measuring which lines are covered is like painting a house and not knowing which walls you've painted. At a glance, you think you're done — but you've never precisely verified which parts were covered. Line coverage is the painter's tape: it shows exactly which lines were touched and which weren't.

**THE INVENTION MOMENT:**
This is exactly why **line coverage** was created: to provide the simplest, most direct answer to "which lines of code were run when tests ran?" — making the gaps in test coverage visible and measurable.

---

### 📘 Textbook Definition

**Line coverage** (also called **statement coverage**) is a code coverage metric that measures the percentage of executable source code lines that are executed at least once during the test suite run. It is computed as: `(lines executed / total executable lines) × 100`. Non-executable lines (blank lines, comments, declarative annotations) are excluded. Line coverage is the most commonly reported coverage metric due to its simplicity and direct visual mapping: in a coverage report, each source file shows every line highlighted green (covered) or red (not covered). Tools: **JaCoCo** for Java (reports as `LINE` counter), **Istanbul/NYC** for JavaScript/TypeScript, **coverage.py** for Python, **SimpleCov** for Ruby. Line coverage is distinct from branch coverage: a line with an `if-else` can be line-covered (the line was executed) without being branch-covered (only the `if` branch was taken, never the `else`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Which lines of code did the tests actually touch?

**One analogy:**
> Line coverage is like tracking which pages of a book have been read. You highlight every page you've read. At the end, unhighlighted pages are ones you haven't read. Line coverage highlights every line your tests execute. Unhighlighted lines are lines your tests never ran. Just as unread pages might contain important information you missed, uncovered lines might contain bugs your tests never encountered.

**One insight:**
Line coverage can be 100% while bugs remain completely undetected. If every line runs but no assertions check the output, line coverage is 100% and test effectiveness is 0%. Line coverage is a necessary precondition for testing, not a sufficient one.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A line that is never executed during tests cannot have test-detected bugs — it's a guaranteed blind spot.
2. A line that is executed during tests might have bugs that the tests don't detect — execution is necessary but not sufficient.
3. Line coverage is the coarsest-grained coverage metric: the fastest to compute, easiest to understand, and weakest at detecting test completeness.

**DERIVED DESIGN:**
Because untested lines are guaranteed blind spots, measuring which lines are untested is the minimum viable test completeness measurement. Line coverage provides this minimum viable measurement with high performance (can be computed for large codebases quickly) and direct visual feedback (green/red line highlighting). It is the starting point, not the ending point, of test quality measurement.

**THE TRADE-OFFS:**
Gain: Simple to understand; direct visual feedback; fast to compute; widely supported across all language ecosystems.
Cost: Weakest coverage metric — a line with an `if (x > 0) { ... } else { ... }` is "line covered" even if only the `if` branch was tested; doesn't distinguish between executed and verified code.

---

### 🧪 Thought Experiment

**SETUP:**
This Java method:
```java
public String getLabel(int value) {
    String label;
    if (value > 0) {
        label = "positive";
    } else {
        label = "non-positive";
    }
    return label;
}
```

**WITH ONLY THIS TEST:**
```java
@Test
void test() {
    String result = service.getLabel(5);
    assertThat(result).isEqualTo("positive");
}
```

**Line coverage result:** 85% line coverage — the `return` line and `if` branch are covered. But the `else` branch (`label = "non-positive"`) is NOT covered.

**What happens if we introduce a bug:**
```java
} else {
    label = null; // bug: should be "non-positive"
}
```

Line coverage: still 85%. The bug line `label = null` is red (not covered). Tests still pass because the `else` branch was never executed.

**THE INSIGHT:**
Line coverage shows the else branch is red/uncovered — which is the signal that should prompt a developer to add a test for the negative case. Line coverage IS useful here: it accurately shows the gap. The developer's job is to notice the red line and write the missing test.

---

### 🧠 Mental Model / Analogy

> Line coverage is like a heat map for a museum. The map shows which rooms were visited (green/warm) and which were not (red/cool). After a day, the director can see: "Gallery 3 was well-visited; Gallery 7 was empty." What the heat map doesn't show: did visitors in Gallery 3 actually look at the paintings, or did they walk straight through? Line coverage shows where you went; it doesn't show if you engaged with what was there.

- "Visited rooms" → lines executed by tests
- "Empty rooms" → lines never executed
- "Museum director inspects" → developer reads coverage report
- "Did they look at paintings" → did the tests actually assert correctness?

Where this analogy breaks down: museum visitors have inherent value just by entering a room (presence creates opportunity). Tests that execute a line without asserting create false confidence (presence without value).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Line coverage is a number (like 83%) telling you: "of all the lines of code that can run, 83% of them were actually run when tests ran." The other 17% are lines that no test ever executed. Those uncovered lines might have bugs that will never be detected by your tests.

**Level 2 — How to use it (junior developer):**
Run `mvn test jacoco:report` then open `target/site/jacoco/index.html`. Every file shows line coverage as a percentage. Click into individual files: green lines were covered, red lines were not. Red lines in business logic classes need tests. Red lines in generated code or trivial getters can often be excluded. Start with the files that have the lowest coverage percentages in your critical business logic.

**Level 3 — How it works (mid-level engineer):**
JaCoCo instruments bytecode at basic block boundaries. Each basic block is contiguous code without branching — every basic block is either fully executed or not (no partial execution). JaCoCo maps basic blocks back to source lines. A source line is "covered" if the basic block containing it executed at least once. This mapping means: a source line that contains an `if` condition is covered if the `if` evaluates — but the `then` and `else` branches may or may not be covered. This is the distinction between line coverage and branch coverage: line coverage counts the `if` line as covered, while branch coverage requires BOTH the `then` AND `else` branches to have been executed.

**Level 4 — Why it was designed this way (senior/staff):**
Line coverage is the simplest coverage metric by design: it requires only execution tracking (was this line run?), not flow analysis (which decision was made once this line ran?). The simplicity is its strength and its weakness. Strength: fast, visual, easy to explain to stakeholders. Weakness: missing branches are invisible. This trade-off explains why mature quality programs use a two-metric approach: line coverage as the floor (all lines must be executed), branch coverage as the quality bar (all decisions must be tested both ways). SonarQube exposes both metrics; quality gates typically require both to be above threshold. The move toward mutation testing represents the logical next step: if line + branch coverage can still miss bugs, what metric would measure whether tests *detect* bugs? (Mutation score does.)

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  LINE COVERAGE CALCULATION                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  Source Method:        Executed?  Coverage      │
│  ─────────────         ─────────  ────────      │
│  line 10: method entry  YES  →   covered        │
│  line 11: int x = 5     YES  →   covered        │
│  line 12: if (x > 0) {  YES  →   covered        │
│  line 13:   doA()       YES  →   covered        │
│  line 14: } else {      ---      (implicit)     │
│  line 15:   doB()       NO   →   NOT COVERED    │
│  line 16: }             ---      (implicit)     │
│  line 17: return x      YES  →   covered        │
│                                                 │
│  Line Coverage: 5/6 = 83%                       │
│  Branch Coverage: 1/2 = 50% (only if taken)     │
│                                                 │
│  Key distinction:                               │
│  Line 12 is "covered" (line coverage = yes)     │
│  Branch coverage: if-branch=yes, else-branch=no │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes tests
  → mvn test (JaCoCo instruments + runs tests)
  → Coverage data: jacoco.exec generated
  → mvn jacoco:report
  → Report shows: OrderService 78% line coverage
  [← YOU ARE HERE: red lines visible]
  → Developer sees: processRefund() method = 0%
  → Adds test for processRefund()
  → Coverage: 84% line → CI gate passes (80%)
  → Quality gate in CI passes
```

**FAILURE PATH:**
```
Test written that executes every line but asserts nothing:
  → Line coverage: 100%
  → Bug: refund calculates negative amount (negative sign)
  → Test: asserts assertNotNull(result) — passes
  → Bug ships; users get negative refund amounts
→ Root cause: line coverage != test quality
→ Fix: mutation testing + meaningful assertions
```

**WHAT CHANGES AT SCALE:**
At large scale, per-class coverage breakdown is more actionable than overall project coverage. SonarQube shows coverage at class/method level, highlighting specific methods with 0% coverage. Coverage trend over time (is it improving or declining with each sprint?) is more important than a point-in-time snapshot.

---

### 💻 Code Example

**Example 1 — JaCoCo line coverage thresholds:**
```xml
<!-- Set line and branch coverage minimums -->
<execution>
  <id>check</id>
  <goals><goal>check</goal></goals>
  <configuration>
    <rules>
      <rule>
        <element>CLASS</element>
        <limits>
          <!-- Per-class line coverage minimum -->
          <limit>
            <counter>LINE</counter>
            <value>COVEREDRATIO</value>
            <minimum>0.75</minimum>
          </limit>
        </limits>
        <!-- Exclude generated code per class pattern -->
        <excludes>
          <exclude>*Dto</exclude>
          <exclude>*Entity</exclude>
          <exclude>*Config</exclude>
        </excludes>
      </rule>
      <!-- Overall bundle minimum -->
      <rule>
        <element>BUNDLE</element>
        <limits>
          <limit>
            <counter>LINE</counter>
            <value>COVEREDRATIO</value>
            <minimum>0.80</minimum>
          </limit>
        </limits>
      </rule>
    </rules>
  </configuration>
</execution>
```

**Example 2 — Reading a coverage report:**
```
UserService.java — Line Coverage: 73%

Line  Code                           Covered?
  10: public User getUser(Long id) { GREEN
  11:   User user = repo.find(id);   GREEN
  12:   if (user == null) {          GREEN (line covered)
  13:     log.warn("not found: {}",  RED   ← untested path
  14:         id);
  15:     throw new NotFound(id);    RED   ← untested path
  16:   }
  17:   return user;                 GREEN
  18: }
```

Lines 13-15 are red: the "user not found" path is never tested. This should trigger a test for the not-found case.

---

### ⚖️ Comparison Table

| Metric | What It Measures | Misses | Speed | Best For |
|---|---|---|---|---|
| **Line Coverage** | Lines executed | Branch alternatives | Fastest | Baseline coverage |
| Branch Coverage | Decision paths | Path combinations | Fast | If/else-heavy logic |
| Method Coverage | Methods called | Internal logic | Fastest | Quick assessment |
| Mutation Score | Bug detection | — | Slowest | Test quality validation |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 80% line coverage means 80% of bugs will be caught | 80% line coverage means 80% of lines were executed. Tests may execute those lines without asserting anything — the bug-detection rate is unrelated to the coverage rate. |
| Green lines are tested | Green lines were *executed* by tests. They were tested only if the test also asserted against their output. A green line with no assertion is executed but not tested. |
| 100% line coverage is achievable for any project | Some code is genuinely difficult or impossible to cover: dead code, defensive null checks, application entry points (main()), third-party integrations. Practical targets exclude these. |
| Line coverage and branch coverage measure the same thing | They are related but distinct. A line with `if (a > 0)` can be line-covered (line runs) while only one branch is tested. Branch coverage requires both `if` and `else` paths to be tested. |

---

### 🚨 Failure Modes & Diagnosis

**1. Coverage Drop on PR — Caused by Excluded Config Class**

**Symptom:** A PR adds a new Spring `@Configuration` class (with no logic, just bean definitions). Line coverage drops from 82% to 78% because these lines are not tested. CI fails.

**Root Cause:** Configuration classes and DTOs have "code" (method definitions) that JaCoCo counts in line coverage, but these are not logically equivalent to business logic that needs testing.

**Diagnostic:**
```bash
mvn test jacoco:report
# Open report, find newly failed class
# Is it a configuration, DTO, or mapper?
```

**Fix:**
```xml
<!-- Exclude config/DTO classes from coverage -->
<configuration>
  <excludes>
    <exclude>**/*Config.class</exclude>
    <exclude>**/*Configuration.class</exclude>
    <exclude>**/dto/**</exclude>
    <exclude>**/*Properties.class</exclude>
  </excludes>
</configuration>
```

**Prevention:** Define coverage exclusion patterns at project start based on common non-business-logic class categories.

---

**2. 100% Coverage But Bugs in Production**

**Symptom:** Line coverage is 95-100%. Yet production bugs occur regularly in covered code.

**Root Cause:** Tests execute code but don't meaningfully assert. Tests verify `assertNotNull` or `assertEquals(result, result)` — technically validating something but not the actual business behaviour.

**Diagnostic:**
```bash
# Run mutation testing to measure actual test effectiveness
mvn org.pitest:pitest-maven:mutationCoverage \
  -DtargetClasses="com.example.*" \
  -DreportDir=target/pit-reports
# Check: mutation score vs. line coverage
# Large gap (90% line, 40% mutation) = coverage gaming
```

**Fix:** Audit tests with high line coverage but low mutation scores. Improve assertions: test return values, side effects (verify interactions), exception messages.

**Prevention:** Add mutation testing as a quality gate alongside line coverage.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Code Coverage` — line coverage is one type of code coverage; understanding the parent concept first
- `Unit Test` — line coverage measures what unit tests cover

**Builds On This (learn these next):**
- `Branch Coverage` — the next step up from line coverage; captures decision paths
- `Mutation Testing` — addresses coverage's fundamental limitation

**Alternatives / Comparisons:**
- `Branch Coverage` — stricter than line coverage; catches branch alternatives line coverage misses
- `Path Coverage` — covers all unique execution paths; too expensive for most projects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ % of source lines executed by tests;      │
│              │ simplest coverage baseline metric         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ "We have coverage" is assertion without   │
│ SOLVES       │ proof; line coverage provides the proof   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Green line = executed, not tested.        │
│              │ Only assertions make execution meaningful.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every project: as minimum coverage        │
│              │ baseline, always enforce it               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never sole metric — pair with branch      │
│              │ coverage and meaningful assertions        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple, visual gap identification vs.     │
│              │ insufficient on its own for branch safety │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A highlight of visited pages — valid     │
│              │  as a minimum, insufficient as a max."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Branch Coverage → Mutation Testing →      │
│              │ Code Coverage                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A finance service has the following code structure: 30% is entity/DTO classes (no logic), 20% is Spring configuration beans (no logic), 10% is the main entry point, and 40% is actual business logic. If your CI enforces 80% overall line coverage, what effective coverage target are you actually requiring for the business logic? How would you redesign the coverage configuration to target 80% of the business logic specifically?

**Q2.** Two safety-critical systems both report 90% line coverage. System A is an air traffic control system; System B is an internal HR portal. Should they use the same coverage strategy, or should coverage requirements differ based on criticality? What additional test quality metrics beyond line coverage would be appropriate for each, and why?

