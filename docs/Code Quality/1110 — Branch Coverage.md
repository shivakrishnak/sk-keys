---
layout: default
title: "Branch Coverage"
parent: "Code Quality"
nav_order: 1110
permalink: /code-quality/branch-coverage/
number: "1110"
category: Code Quality
difficulty: ★★★
depends_on: Line Coverage, Code Coverage, Unit Test
used_by: Mutation Testing, SonarQube, CI/CD Pipeline
related: Line Coverage, Code Coverage, Mutation Testing
tags:
  - bestpractice
  - advanced
  - testing
  - cicd
  - java
---

# 1110 — Branch Coverage

⚡ TL;DR — Branch coverage measures whether every decision branch (every true/false outcome of every conditional) has been executed by tests — a stronger guarantee than line coverage alone.

| #1110 | Category: Code Quality | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Line Coverage, Code Coverage, Unit Test | |
| **Used by:** | Mutation Testing, SonarQube, CI/CD Pipeline | |
| **Related:** | Line Coverage, Code Coverage, Mutation Testing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer writes tests for a discount calculation method. The method has `if (user.isPremium())` — if true, apply 20% discount; if false, apply no discount. The developer writes one test where `isPremium()` is `true`. Line coverage: 100% — every line of the method ran. But the `false` branch of `if (user.isPremium())` was never tested. A bug exists in the `false` branch: non-premium users receive a 5% discount due to an off-by-one error in the else block. Tests pass. Bug ships.

**THE BREAKING POINT:**
Line coverage cannot detect this class of bug. A line can be "covered" (executed) while only one of its possible conditional branches is tested. The other branch — potentially containing a bug — is invisible to line coverage.

**THE INVENTION MOMENT:**
This is exactly why **branch coverage** was developed: to require that every decision point in a program is tested in all possible outcomes — ensuring that `if (x)` is tested when `x` is `true` AND when `x` is `false`.

---

### 📘 Textbook Definition

**Branch coverage** (also called **decision coverage** or **condition coverage**) is a code coverage metric that measures the percentage of decision branches taken during test execution. A branch is any point where the execution flow can diverge: every `if` has a true branch and a false branch; every `switch` has one branch per case plus a default; every ternary operator (`? :`) has two branches; try-catch has the try branch and the catch branch. Branch coverage is computed as: `(branches taken / total branches) × 100`. A method with two `if` statements has 4 branches (2 true, 2 false) and requires all 4 to be exercised for 100% branch coverage. JaCoCo reports branch coverage separately from line coverage ("missed branches: indicates the number of branches not covered"). Branch coverage is a superset of line coverage: 100% branch coverage implies 100% line coverage (every line must be executed to execute both branches), but 100% line coverage does not imply 100% branch coverage.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Has every if/else, every condition, been tested both ways?

**One analogy:**
> Branch coverage is like testing every switch in a room, both on AND off. Line coverage says "we flipped every switch at least once." Branch coverage says "we tested every switch in both positions." A light that flickers only when turned off might look fine in your line coverage test (you turned it on) — but branch coverage requires you also test it off. Code bugs often hide in the untested direction of a decision.

**One insight:**
Most bugs in conditional logic are in the branch that is not the "happy path." Happy-path tests give high line coverage. Branch coverage forces testing the unhappy paths — the error conditions, the null cases, the "when this is false" paths where bugs typically lurk.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every conditional (`if`, `switch`, ternary) creates two or more possible execution paths. A bug can exist in any one of those paths.
2. Line coverage identifies the line containing the conditional as "covered" if that line executed — regardless of which path was taken.
3. Branch coverage identifies each path independently: both the `true` and `false` outcomes of every decision must be exercised for full branch coverage.

**DERIVED DESIGN:**
Since bugs can exist in any branch of a conditional, and since line coverage does not require all branches to be taken, branch coverage is the minimum metric that provides the guarantee "all decision paths were executed." Any codebase with conditionals needs branch coverage to avoid the "happy-path only" testing trap.

**THE TRADE-OFFS:**
Gain: Detects untested conditional paths (the most common source of production bugs not caught by line-coverage-only tests).
Cost: Harder to achieve 100% branch coverage than 100% line coverage (requires tests for both outcomes of every conditional, including defensive null checks that may never fire); more computationally expensive to measure.

---

### 🧪 Thought Experiment

**SETUP:**
```java
public BigDecimal calculateDiscount(User user) {
    if (user.isPremium()) {
        return PREMIUM_DISCOUNT;
    } else {
        return STANDARD_DISCOUNT;  // bug: returns 0.0 instead of 0.05
    }
}
```

**LINE COVERAGE TEST (catches nothing):**
```java
@Test void test() {
    User premiumUser = new User(true);
    BigDecimal result = service.calculateDiscount(premiumUser);
    assertThat(result).isEqualTo(PREMIUM_DISCOUNT);
}
// Line coverage: 100% (all lines executed for isPremium=true)
// Branch coverage: 50% (only true branch tested)
// Bug: hidden in else branch — never caught
```

**BRANCH COVERAGE TEST (catches the bug):**
```java
@Test void premiumUser_getsFullDiscount() {
    assertThat(service.calculateDiscount(new User(true)))
        .isEqualTo(PREMIUM_DISCOUNT);
}

@Test void standardUser_getsStandardDiscount() {
    assertThat(service.calculateDiscount(new User(false)))
        .isEqualTo(STANDARD_DISCOUNT);  // FAILS: actual is 0.0
    // Bug revealed!
}
// Branch coverage: 100% → bug detected
```

**THE INSIGHT:**
The bug was in the `else` branch. Line coverage could not detect it because the `else` branch line was never executed. Branch coverage required executing the `else` branch, which immediately revealed the bug.

---

### 🧠 Mental Model / Analogy

> Branch coverage is like testing every junction in a maze, both left AND right. Line coverage says "we walked through all the corridors." Branch coverage says "at every junction, we tried both left AND right." A trap door that activates only when you turn left might be invisible to a test that always turns right — even if that test covers all corridors. Branch coverage forces the left-turn tests that reveal the traps.

- "Maze corridors" → lines of code
- "Junctions" → conditional statements (if/else, switch)
- "Walking through corridors" → line coverage (all lines executed)
- "Testing both left AND right at every junction" → branch coverage
- "Trap door on left turn" → bug in the else-branch

Where this analogy breaks down: maze paths can be extremely long with many junctions in sequence; full branch coverage does not require testing every combination of junction decisions (that's path coverage), only every junction in isolation.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Branch coverage checks that in every `if` statement, your tests have tested both the "yes" case and the "no" case. If you have `if (user.isPaid())`, your tests must include one test where the user is paid AND one test where the user is not paid. Branch coverage ensures you haven't just tested the happy path.

**Level 2 — How to use it (junior developer):**
Look at your JaCoCo branch coverage report in the HTML output. Lines with `if` statements show a diamond icon (◇). The diamond is half-green/half-red if only one branch was taken. Your goal: every diamond should be fully green. For each half-red diamond: "what test would make the other half green?" Add that test. Usually: the tests you add for branch coverage are the most valuable tests — they test the error cases, null conditions, and edge cases that production bugs hide in.

**Level 3 — How it works (mid-level engineer):**
JaCoCo instruments branch points in bytecode: at each conditional bytecode instruction (`if_icmpeq`, `if_null`, `tableswitch`, etc.), JaCoCo inserts probes for each possible outcome. When tests execute, JaCoCo records which branch outcomes were reached. The HTML report shows: "2 of 4 branches missed" for a method with 2 `if` statements where only the true cases were tested. JaCoCo specifically covers: `if`/`else`, ternary (`? :`), `switch`, `try`/`catch` (try path and catch path), and short-circuit logical operators (`&&` and `||` — each has a "short-circuit true" and "short-circuit false" branch). Branch coverage is more expensive to achieve than line coverage because it requires at least 2 tests per conditional (one true, one false), leading to more test cases needed for complete coverage.

**Level 4 — Why it was designed this way (senior/staff):**
Branch coverage sits between two extremes: **line coverage** (insufficient — misses branch alternatives) and **path coverage** (complete — requires testing every unique execution path, which is exponential in the number of conditionals). Branch coverage is the practical compromise: it requires exhausting each decision's outcomes independently rather than exhaustively. For a method with 10 `if` statements: path coverage requires 2^10 = 1024 tests; branch coverage requires at most 20 tests (2 per `if`). This makes branch coverage achievable for real codebases. The relationship to mutation testing: branch coverage is a structural property (every branch was executed); mutation testing is a behavioural property (tests can detect changes to every branch's logic). Both are necessary for high-confidence testing: branch coverage without good assertions = still ineffective; good assertions without branch coverage = still missing paths.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  BRANCH COVERAGE ANALYSIS                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  Code:                          Branches:       │
│  if (a > 0) {         ─── true ──→ (covered)   │
│      doA();           ─── false─→ (NOT covered) │
│  }                                              │
│  if (b != null) {     ─── true ──→ (covered)   │
│      doB(b);          ─── false─→ (covered)    │
│  }                                              │
│                                                 │
│  Branch coverage: 3/4 = 75%                     │
│  Missing: first if-false path (a <= 0 case)     │
│                                                 │
│  JACOCO REPORT:                                 │
│  Line 10: diamond icon ◇ half-green/half-red    │
│  → "1 of 2 branches missed"                     │
│  → Test needed: where a <= 0                    │
│                                                 │
│  BRANCH TYPES JACOCO TRACKS:                    │
│  if/else: 2 branches each                       │
│  switch: N+1 branches (N cases + default)       │
│  try/catch: try-path + catch-path               │
│  &&, ||: short-circuit true + false             │
│  ? :: 2 branches                                │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes PaymentService (3 if statements)
  → Tests: only "payment succeeds" path tested
  → JaCoCo report: 100% line, 50% branch
    [← YOU ARE HERE: 3 red diamonds visible]
  → Developer writes 3 failure-path tests
  → 100% line, 95% branch (one exception handler
    legitimately impossible to trigger in isolation)
  → CI gate: branch ≥ 75% → passes
  → SonarQube: quality gate passed
```

**FAILURE PATH:**
```
Team enforces line coverage ≥ 80%, not branch
  → All tests pass happy paths
  → Line coverage: 92%
  → Branch coverage: 48%
  → Half of all conditionals never tested on false
  → A null check in order processing reads:
    if (payment != null) { ... } else { crash() }
  → Tests never pass null payment
  → Production: 0.01% null payments → crash
→ Fix: add branch coverage to CI gate (≥ 75%)
```

**WHAT CHANGES AT SCALE:**
In large codebases, branch coverage is reported per class. Priority: classes with 0% branch coverage in critical business logic (payment, auth, data processing) are highest risk. Classes with 0% branch coverage in generated code or DTO layers are lower risk and often excluded.

---

### 💻 Code Example

**Example 1 — JaCoCo branch coverage configuration:**
```xml
<execution>
  <id>check</id>
  <goals><goal>check</goal></goals>
  <configuration>
    <rules>
      <rule>
        <element>BUNDLE</element>
        <limits>
          <limit>
            <counter>LINE</counter>
            <value>COVEREDRATIO</value>
            <minimum>0.80</minimum>
          </limit>
          <!-- Add branch coverage requirement -->
          <limit>
            <counter>BRANCH</counter>
            <value>COVEREDRATIO</value>
            <minimum>0.75</minimum>
          </limit>
        </limits>
      </rule>
    </rules>
  </configuration>
</execution>
```

**Example 2 — Writing tests for branch coverage:**
```java
// Method under test:
public String formatUserStatus(User user) {
    if (user == null) {
        return "UNKNOWN";
    }
    if (user.isActive()) {
        return "ACTIVE";
    } else {
        return "INACTIVE";
    }
}

// Tests for ALL branches:
@Test
void nullUser_returnsUnknown() {
    assertThat(formatter.formatUserStatus(null))
        .isEqualTo("UNKNOWN");
    // Covers: if (user == null) true branch
}

@Test
void activeUser_returnsActive() {
    assertThat(formatter.formatUserStatus(activeUser))
        .isEqualTo("ACTIVE");
    // Covers: if (user == null) false AND
    //         if (user.isActive()) true branch
}

@Test
void inactiveUser_returnsInactive() {
    assertThat(formatter.formatUserStatus(inactiveUser))
        .isEqualTo("INACTIVE");
    // Covers: if (user.isActive()) false branch
}
// Result: 100% line coverage, 100% branch coverage
```

---

### ⚖️ Comparison Table

| Coverage | Catches | Misses | Required Tests | Cost |
|---|---|---|---|---|
| Line | Uncovered lines | Branch alternatives | Low | Low |
| **Branch** | Line + missing branches | Path combinations | Medium | Medium |
| Condition | Individual sub-conditions | Path combinations | High | Medium |
| Path | Every unique full path | — | Exponential | Very High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 100% line coverage implies 100% branch coverage | False. 100% line coverage only requires each line to execute once. 100% branch coverage requires each decision outcome (true AND false) to be tested. |
| 100% branch coverage proves the code is correct | 100% branch coverage proves every branch was executed. Tests can execute branches without asserting the result correctly. Execution ≠ verification. |
| Branch coverage requires you test every combination of conditions | No — branch coverage requires each branch outcome to be tested independently, not every combination. Testing every combination (path coverage) is exponentially more expensive. |
| 75% branch coverage is always sufficient | Critical branches (authentication, payment validation, error handling) may need 100% branch coverage. Coverage targets should be stratified by code criticality. |

---

### 🚨 Failure Modes & Diagnosis

**1. Branch Coverage Low Despite High Line Coverage**

**Symptom:** Line coverage 90%, branch coverage 55%. Report shows dozens of half-red diamonds on `if` statements.

**Root Cause:** Tests cover the happy path (true branches) but not the error/edge paths (false branches, null guards, exception handlers).

**Diagnostic:**
```bash
mvn test jacoco:report
# Open target/site/jacoco/
# Sort by "Missed Branches" column
# Highest = most urgent
# Click method: see yellow/red branch markers
```

**Fix:** For each red diamond: write the test that would turn it green. Start with the most critical business logic classes. Skip defensive guards in unreachable code (defensive programming checks that can't actually fire — these can be excluded).

**Prevention:** Add branch coverage to CI gate (≥ 75%). Developers see branch coverage red in their IDE when they write only happy-path tests.

---

**2. Branch Coverage Misleadingly High Due to Exception Handlers**

**Symptom:** Branch coverage appears high, but key business logic paths are not tested. Investigation: coverage is being "filled" by exception handler branches.

**Root Cause:** `try`/`catch` blocks contribute 2 branches each. If exception handling is tested (by mocking exceptions), branch coverage from handlers fills the metric while real business logic branches remain untested.

**Diagnostic:**
```bash
# In JaCoCo report: filter to specific business logic class
# Ignore infrastructure/exception-handling classes
# Check branch coverage specifically in:
# - Calculation methods
# - Validation methods  
# - State transition methods
```

**Fix:** Report branch coverage per business logic class separately. Set stricter branch coverage thresholds for critical domain classes.

**Prevention:** Use SonarQube per-class coverage views rather than overall bundle coverage.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Line Coverage` — branch coverage extends line coverage; understanding line coverage first
- `Code Coverage` — the parent concept of both line and branch coverage

**Builds On This (learn these next):**
- `Mutation Testing` — the next quality step after branch coverage; verifies tests detect bugs, not just execute paths

**Alternatives / Comparisons:**
- `Path Coverage` — covers all unique execution paths; exponentially more thorough, practically infeasible
- `Condition Coverage` — covers individual boolean sub-conditions; more granular than branch coverage

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ % of decision branches (true/false of     │
│              │ every if/switch/ternary) that tests take  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Line coverage misses bugs in untested     │
│ SOLVES       │ branch alternatives (else, null, error)   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ 100% line + 50% branch = half of all      │
│              │ decisions never tested in one direction   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All projects; especially conditional-heavy│
│              │ business logic (discount, auth, validation)│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip; but 100% branch coverage on   │
│              │ defensive guards may not justify cost     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Catches untested conditionals vs. requires│
│              │ more tests (2 per if) to reach target     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Test every switch both on AND off —       │
│              │  bugs hide in the direction you didn't    │
│              │  test."                                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Mutation Testing → Code Coverage →        │
│              │ SonarQube Quality Gate                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service has a complex validation method with 15 `if` statements. 100% branch coverage would require at least 30 tests (two per `if`). The team argues that writing 30 tests for one method creates test maintenance overhead that slows development more than the bugs branch coverage would catch. Design a risk-stratified coverage approach: how would you determine which of the 15 conditionals absolutely require both branches tested, and which could reasonably have only one branch covered?

**Q2.** Consider this code: `if (a && b)`. This creates the following logical scenarios: a=true/b=true (goes in), a=true/b=false (doesn't go in), a=false/b=false (doesn't — short-circuits on a). JaCoCo's branch coverage treats `&&` as having two branches: short-circuit (a is false) and non-short-circuit (a is true). It does NOT require testing a=true/b=false separately. MC/DC coverage (Modified Condition/Decision Coverage — used in aviation safety) would require all combinations. For which types of systems would you mandate MC/DC coverage over standard branch coverage, and why?

