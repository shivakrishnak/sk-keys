---
layout: default
title: "Regression Test"
parent: "Testing"
nav_order: 1136
permalink: /testing/regression-test/
number: "1136"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, Integration Test, CI-CD
used_by: CI-CD, Release Gating, Bug Fix Verification
related: Test Suite, Test Coverage, Flaky Tests, Bisect
tags:
  - testing
  - ci-cd
  - quality
  - regression
---

# 1136 — Regression Test

⚡ TL;DR — A regression test verifies that code changes don't break previously working functionality — it's the safety net that catches "it worked before your change" bugs.

| #1136           | Category: Testing                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, Integration Test, CI-CD             |                 |
| **Used by:**    | CI-CD, Release Gating, Bug Fix Verification    |                 |
| **Related:**    | Test Suite, Test Coverage, Flaky Tests, Bisect |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Feature A works. Developer fixes Bug B (in a different area). Feature A now breaks. Without regression tests: Feature A's breakage is discovered by a user 3 days later. The developer has since worked on 5 other things. Debugging: "which commit broke A?" requires `git bisect` through 20 commits.

**THE BREAKING POINT:**
Software has non-linear dependencies. Changing function X can break function Y through shared state, changed interface contracts, modified global configuration, or subtle ordering assumptions. These interactions are impossible to mentally track. Regression tests codify "this worked before" into executable checks that run on every change.

**THE INVENTION MOMENT:**
Regression testing emerged as a discipline in the 1970s–80s alongside the growth of large software projects where individual developers couldn't hold the entire system in their heads. The practice of codifying bugs as tests before fixing them (so the same bug never reappears) became standard by the 1990s.

---

### 📘 Textbook Definition

A **regression test** is any automated test that verifies previously working functionality still works after a code change. The term "regression" refers to a **regression bug** — when a change causes previously correct behavior to become incorrect. A regression test suite is typically the accumulation of all tests written over a project's lifetime: unit tests, integration tests, and E2E tests — collectively forming the safety net for future changes.

The specific practice of writing a regression test before fixing a bug (**bug-driven testing**) ensures the bug cannot silently reappear: if the fix is reverted or the code is refactored to re-introduce the bug, the regression test will fail.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Regression test = "this worked yesterday — prove it still works today."

**One analogy:**

> Every time a building inspector finds a code violation during an inspection, they add it to the checklist. Every future inspection includes that item. Buildings can't regress to the same violation. Regression tests are the growing inspection checklist for your software.

**One insight:**
The most valuable regression tests come from production bugs. Every production incident should generate a test that would have caught it. Over time, your test suite's "scar tissue" encodes years of production experience.

---

### 🔩 First Principles Explanation

BUG-DRIVEN TESTING WORKFLOW:

```
1. Bug reported: "Checkout fails for users with apostrophe in last name (O'Brien)"
2. Write failing test FIRST:
   @Test
   void checkout_userWithApostropheInName_succeeds() {
       User user = new User("O'Brien", "obrien@test.com");
       assertDoesNotThrow(() -> checkoutService.process(user, cart));
   }
   // Test FAILS → confirms bug

3. Fix bug (sanitize SQL query / use parameterized statement)
4. Run test → PASSES → confirms fix
5. Test stays in suite forever
6. If someone later introduces raw SQL with string concatenation → test FAILS → caught before production
```

REGRESSION TEST SELECTION:
When CI takes 30 minutes with 5000 tests, you can't run all tests on every commit. Strategies:

- **Test impact analysis**: only run tests that cover changed code (JVM: `mvn -Dsurefire.runOrder=testng -Dsurefire.failIfNoSpecifiedTests=false`)
- **Risk-based selection**: always run smoke tests; run integration tests on changes to integration layers; run full suite before release
- **Parallel execution**: split tests across workers (Maven Surefire `forkCount`, Gradle parallel)

**THE TRADE-OFFS:**
**Gain:** Automatic detection of regression bugs; confidence to refactor; documented production bug history.
**Cost:** Growing test suite = slower CI; maintaining tests as code evolves; flaky regression tests erode trust in the suite.

---

### 🧪 Thought Experiment

THE DATE PARSING REGRESSION:

```
Release 1.0: DateParser.parse("2024-01-15") works correctly
Developer: "I'll optimise date parsing with a regex"
Release 1.1: DateParser.parse("2024-01-15") still works
           DateParser.parse("2024-1-5") now returns null (single-digit months)

Without regression test:
  → CI: all new tests pass
  → Users with dates like "2024-1-5" (common in CSV imports) fail silently
  → Bug discovered in production after 2 weeks

With regression test (written after original date parsing feature):
  @ParameterizedTest
  @ValueSource(strings = {"2024-01-15", "2024-1-5", "2024-12-31", "2024-1-01"})
  void parseDate_variousFormats_succeeds(String date) {
      assertThat(DateParser.parse(date)).isNotNull();
  }
  → CI fails on the "2024-1-5" case immediately
  → Developer catches regression before release
```

---

### 🧠 Mental Model / Analogy

> A regression test suite is a **net under a trapeze act**. The net doesn't prevent you from doing new, ambitious acts (new features). It catches you if you fall (introduce a regression). The net gets stronger and bigger over time as more safety lines are added (tests from each bug fixed, each feature added). A circus with a good net = a team that can move fast and take risks.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Regression tests check that old features still work after you add or change something. Every time you find a bug and fix it, you write a test that would have caught the bug — so it can never sneak back in.

**Level 2:** In practice: your entire test suite is your regression suite. Every unit test and integration test runs on every PR (CI). When fixing a bug: write test first (red), fix bug (green), commit both together. Use `@Disabled` (not deletion) for temporarily broken tests — and add a JIRA ticket to fix. Parameterized tests (`@ParameterizedTest`) add coverage of many input variants with one test.

**Level 3:** Test suite health metrics: flaky test rate (target < 1%), test execution time (target < 10 min for PR checks), test coverage trends (coverage should not decrease over time). Git bisect automation: `git bisect run mvn test -pl module -Dtest=MyRegressionTest` → automatically finds the commit that introduced the regression. Mutation testing (PIT): introduces small code mutations (change `>` to `>=`) and verifies tests catch them — ensures tests are actually verifying behavior, not just executing code.

**Level 4:** The "zero-bug policy" approach (Microsoft teams): every bug gets a regression test before the fix is committed. Over time, the regression suite encodes the team's collective debugging experience. The test suite becomes a "scar tissue" map of the codebase's failure modes. Correlation: teams with high regression test density have lower bug escape rates (Google's research shows a strong correlation between test coverage density and production incident rate). The diminishing returns curve: going from 0% to 80% coverage eliminates ~80% of bugs; going from 80% to 100% eliminates only ~10% more — the remaining 10% require different approaches (formal verification, fuzzing).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│         CI REGRESSION GATE ON PULL REQUEST               │
├──────────────────────────────────────────────────────────┤
│  PR: "Fix checkout for international addresses"          │
│                                                          │
│  CI Pipeline:                                            │
│  1. Unit tests (changed modules): 45s                   │
│  2. Integration tests (affected layers): 3min           │
│  3. Regression suite (all tests): 8min                  │
│     → 2,847 tests pass                                  │
│     → 1 test FAILS:                                     │
│       ShippingCalculatorTest.calculate_USAddress         │
│       Expected: 5.99 but was: null                      │
│                                                          │
│  → PR blocked: cannot merge                             │
│  → Developer: "I changed the address normalization —    │
│    must have broken US address parsing"                 │
│  → Fix → all tests pass → merge                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
1. Production bug reported: "Order total shows negative for discount > 100%"
2. Developer writes regression test:
   @Test
   void calculateTotal_discountExceedsFull_clampsToZero() {
       Order order = Order.of("item1", BigDecimal.valueOf(100.00));
       BigDecimal result = pricingService.applyDiscount(order, 1.20);  // 120%
       assertThat(result).isEqualByComparingTo(BigDecimal.ZERO);  // FAILS
   }
3. Developer fixes bug (clamp discount to max 1.0)
4. Test passes
5. Commit: "fix: clamp discount to 100% max, add regression test"
6. PR: CI runs 3000+ tests including new regression test
7. Forever: any future change that re-introduces this bug fails CI
```

---

### 💻 Code Example

```java
// Regression test pattern: named after the bug/issue
// This test documents the exact bug and prevents recurrence

/**
 * Regression test for GH-1247: Checkout fails for users with
 * special characters in last name.
 * Fixed in commit abc123.
 */
@Test
@DisplayName("GH-1247: checkout should succeed for names with apostrophes")
void checkout_usernameWithApostrophe_doesNotThrow() {
    User user = User.builder()
        .firstName("Sean").lastName("O'Brien")
        .email("obrien@test.com").build();
    Cart cart = testCartWith("product-1", 2);

    assertThatCode(() -> checkoutService.process(user, cart))
        .doesNotThrowAnyException();

    Order saved = orderRepository.findByUserEmail("obrien@test.com")
        .orElseThrow();
    assertThat(saved.getStatus()).isEqualTo(OrderStatus.CONFIRMED);
}

// Parameterized regression: cover all special character variants
@ParameterizedTest(name = "last name ''{0}'' should not cause SQL error")
@ValueSource(strings = {"O'Brien", "van der Berg", "Smith-Jones",
                         "García", "Müller", "李明"})
void checkout_internationalNames_succeed(String lastName) {
    User user = User.builder()
        .firstName("Test").lastName(lastName)
        .email("test@example.com").build();

    assertThatCode(() -> checkoutService.process(user, minimalCart()))
        .doesNotThrowAnyException();
}
```

---

### ⚖️ Comparison Table

| Practice            | Goal                                | Trigger                  |
| ------------------- | ----------------------------------- | ------------------------ |
| **Regression Test** | Prevent known bugs from reappearing | Bug fix commits, all PRs |
| Unit Test           | Verify function behavior            | Development, TDD         |
| Smoke Test          | Verify deploy health                | Post-deployment          |
| E2E Test            | Verify user journeys                | Release gates            |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                               |
| ------------------------------------------ | ------------------------------------------------------------------------------------- |
| "Regression tests are a special test type" | All tests in your suite are regression tests — they all run to detect regressions     |
| "Only write regression tests for bugs"     | Write them for any behavior you want to preserve through future changes               |
| "100% regression test pass = no bugs"      | Tests can't cover unknown scenarios; they cover known scenarios                       |
| "Regression tests slow down development"   | Regression tests prevent the 10× more expensive rework of fixing same bugs repeatedly |

---

### 🚨 Failure Modes & Diagnosis

**1. Growing Regression Suite Slows CI to 45 Minutes**

**Root Cause:** 5000 tests run sequentially; no parallelism; integration tests mix with unit tests.
**Fix:** Parallel execution (`forkCount=1C` in Maven Surefire = 1× CPU count); separate unit/integration test phases; test impact analysis (only run tests touching changed code on PRs).

**2. Regression Test Suite Has 20% Flaky Rate**

**Root Cause:** Tests share state (static fields, shared DB, non-reset mocks); timing-dependent tests; environment-specific behavior.
**Fix:** Quarantine flaky tests (`@Disabled` + ticket); investigate root cause systematically; require `@BeforeEach` cleanup; use test-specific DB schemas.

---

### 🔗 Related Keywords

- **Prerequisites:** Unit Test, Integration Test, CI-CD
- **Builds on:** Flaky Tests, Test Coverage, Mutation Testing
- **Related:** Smoke Test, E2E Test, Test Pyramid

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Test that verifies old behavior survives │
│              │ new changes — the CI safety net          │
├──────────────┼───────────────────────────────────────────┤
│ KEY PRACTICE │ Write test BEFORE fixing bug; commit     │
│              │ both together                             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Test suite = scar tissue of past bugs;   │
│              │ grows richer with every incident         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ CI safety vs growing suite execution time│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "It worked before — prove it still does" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Flaky Tests → Mutation Testing → git bisect│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `git bisect` is a binary search algorithm for finding the commit that introduced a regression. `git bisect start; git bisect bad HEAD; git bisect good v1.0.0` checks out the middle commit; you mark it good or bad; it halves the search space. `git bisect run mvn test -Dtest=MyRegressionTest` automates this — the test itself determines good/bad. With 200 commits between v1.0.0 and HEAD: (a) how many commits does git bisect need to check (log₂(200) ≈ 8), (b) if the test takes 2 minutes to run, total bisect time is 16 minutes vs checking all 200 (400 min), (c) describe a scenario where `git bisect run` gives a false result (the test itself is flaky or the bug requires multiple commits together — a "compound regression").

**Q2.** Mutation testing (PITest in Java) modifies your production code with small mutations (change `>` to `>=`, negate a boolean, change a return value) and runs your test suite against each mutant. A mutant that survives (tests don't catch the change) indicates a gap in test coverage. A project with 85% line coverage but 40% mutation coverage means tests execute 85% of lines but only detect 40% of logic mutations. Explain: (1) why line coverage is a weaker signal than mutation score, (2) how to use mutation testing feedback to improve specific tests, (3) why targeting 100% mutation coverage is counterproductive (trivial mutations in getter/setters, logging), and (4) the computational cost issue (PITest creates N mutants × test suite runtime) and how PITest's incremental mode addresses it.
