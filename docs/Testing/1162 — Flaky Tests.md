---
layout: default
title: "Flaky Tests"
parent: "Testing"
nav_order: 1162
permalink: /testing/flaky-tests/
number: "1162"
category: Testing
difficulty: ★★★
depends_on: Test Isolation, Integration Test, E2E Test
used_by: Developers, QA, DevOps
related: Test Isolation, Test Environments, Test Parallelization, Test Data Management
tags:
  - testing
  - flaky-tests
  - reliability
  - non-determinism
---

# 1162 — Flaky Tests

⚡ TL;DR — A flaky test is a test that produces inconsistent results (pass sometimes, fail sometimes) on the same code — undermining trust in the test suite, causing CI reruns, and masking real failures.

| #1162           | Category: Testing                                                             | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Test Isolation, Integration Test, E2E Test                                    |                 |
| **Used by:**    | Developers, QA, DevOps                                                        |                 |
| **Related:**    | Test Isolation, Test Environments, Test Parallelization, Test Data Management |                 |

---

### 🔥 The Problem This Solves

THE FLAKY CI NIGHTMARE:
A test fails. Developer checks the code — nothing changed. Reruns CI — it passes. "Just a flaky test." This cycle repeats 10 times per week. Eventually, teams stop trusting CI failures and re-run until green — which means they start ignoring real failures too. Google's research found that flaky tests at scale (millions of test runs per day) caused developers to spend ~2% of their total development time investigating false failures. The deeper problem: flaky tests erode the fundamental contract of automated testing — "if it's red, something is wrong."

---

### 📘 Textbook Definition

A **flaky test** is a test that is non-deterministic — it does not consistently produce the same pass/fail result for the same code under identical conditions. Flakiness causes include: **timing dependencies** (race conditions, async operations without proper awaiting), **test order dependency** (shared state contaminated by a previous test), **environment dependency** (network calls, external services, system time), **resource contention** (parallel tests competing for ports, files, database rows), and **random data** (tests that use random inputs without fixed seeds). Flaky tests are distinct from legitimately failing tests — a flaky test does not indicate a bug; it indicates a poorly written or poorly isolated test.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Flaky = sometimes red, sometimes green, same code — destroys CI trust.

**One analogy:**

> A flaky test is like a **faulty smoke detector** that sometimes goes off for no reason. You start ignoring it. Then there's a real fire, and you ignore that too. The detector has destroyed its own credibility and the safety system it was meant to provide.

---

### 🔩 First Principles Explanation

ROOT CAUSES TAXONOMY:

```
1. TIMING / ASYNC ISSUES (most common):

   BAD: Thread.sleep(500) hoping async operation completes
   Thread.sleep(500);
   assertThat(cache.get("key")).isEqualTo("value");
   // Flaky: on slow CI server, 500ms isn't enough

   GOOD: Await with timeout
   await().atMost(5, SECONDS).until(() -> cache.get("key") != null);
   // Deterministic: waits up to 5s, asserts immediately when condition met

   TOOLS: Awaitility (Java), waitFor (Jest), cy.wait (Cypress)

2. TEST ORDER DEPENDENCY:

   BAD: Test A creates user; Test B assumes user exists
   class UserServiceTest {
     @Test void createUser() { service.createUser("alice"); }
     @Test void getUserProfile() {
       User u = service.getUser("alice");  // Fails if createUser ran after
       assertThat(u).isNotNull();
     }
   }

   GOOD: Each test creates its own data:
   @Test void getUserProfile() {
     service.createUser("alice");  // self-sufficient
     assertThat(service.getUser("alice")).isNotNull();
   }

3. RESOURCE CONTENTION (parallel tests):

   BAD: Two tests both use port 8080
   // Test A: start server on 8080
   // Test B: start server on 8080 — BindException

   GOOD: Random port assignment
   @SpringBootTest(webEnvironment = RANDOM_PORT)
   // Each test gets a random available port

4. EXTERNAL DEPENDENCIES:

   BAD: Test calls real external API
   Weather weather = weatherClient.getCurrentWeather("London");
   assertThat(weather.getTemp()).isGreaterThan(-50);
   // Flaky: network failure, rate limit, API change

   GOOD: Mock external dependency
   when(weatherClient.getCurrentWeather("London"))
     .thenReturn(new Weather(20.0, "Sunny"));

5. TIME DEPENDENCY:

   BAD: assertEquals(LocalDate.now(), order.getCreatedDate());
   // Flaky at midnight (test runs just before midnight, assertion just after)

   GOOD: Use Clock abstraction
   Clock clock = Clock.fixed(Instant.parse("2024-01-15T10:00:00Z"), UTC);
   Order order = new Order(clock);
   assertEquals(LocalDate.parse("2024-01-15"), order.getCreatedDate());
```

DETECTING FLAKY TESTS:

```
1. Flakiness detection in CI (run N times):
   # GitHub Actions: retry failed tests
   ./mvnw test -Dsurefire.rerunFailingTestsCount=3

   If test passes on retry → flagged as flaky

2. Test run history analysis:
   Track pass rate per test over last 100 runs
   If pass rate < 99% → flaky candidate

3. Quarantine strategy:
   @Tag("flaky")
   @Disabled("Quarantined: flaky due to timing issue, tracked in JIRA-1234")
   @Test void someFlakeyTest() { ... }

   → Run main suite without @flaky tag
   → Run flaky suite separately (don't block CI)
   → Fix flaky tests with target SLA
```

---

### 🧪 Thought Experiment

THE CASCADING IGNORE:

```
Month 1: Test A starts failing 5% of the time. Team reruns until green.
Month 2: 3 more flaky tests appear. Team accepts re-run culture.
Month 3: Real bug introduced. Test B fails consistently.
          Developer re-runs. It fails again. "Hmm, probably flaky."
          Developer re-runs 3 times. It keeps failing.
          "Well, the CI is unreliable. Let me just merge."
          → Real bug ships to production.

The flaky tests didn't just waste time — they destroyed the diagnostic value
of the test suite. Zero flaky tests = zero tolerance culture.
```

---

### 🧠 Mental Model / Analogy

> Think of flaky tests as **broken gauges in an aircraft cockpit**. An altitude gauge that sometimes reads wrong doesn't just fail to provide information — it actively misleads. Pilots learn to distrust it, and over time, start doubting all gauges. One broken gauge degrades the whole instrument panel's credibility. Tests have the same dynamics: one flaky test makes developers distrust all test failures.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Flaky = non-deterministic. Root causes: timing, shared state, external dependencies, resource contention. Fix: isolation, proper async awaiting, mocking externals.

**Level 2:** Fix timing: replace `Thread.sleep()` with Awaitility (`await().atMost(5, SECONDS).until(...)`). Fix order dependency: `@BeforeEach` creates fresh data; `@AfterEach` deletes it. Fix port contention: `@SpringBootTest(webEnvironment = RANDOM_PORT)`. Fix time: inject `Clock` and fix it in tests.

**Level 3:** Quarantine strategy: `@Tag("flaky")` + `@Disabled` with JIRA link. Separate CI stage for quarantined tests (don't block main pipeline). Flakiness budget: track flakiness rate; if suite-wide flakiness > 1%, stop merging until it's fixed. Test retry: `surefire.rerunFailingTestsCount` — detect flakiness but don't hide it; log when a test passes on retry as a warning.

**Level 4:** At scale (Google, Meta): flakiness detection as a platform service. Every test run's result stored. ML model predicts if a specific failure is "likely flaky" (based on historical pass rate, error message, test duration variance). Automatically quarantine tests with >2% failure rate. Require teams to fix quarantined tests within N days (SLA). The lesson from industry: flakiness at scale is a product quality metric — tracked by engineering leadership, not just individual teams.

---

### 💻 Code Example

```java
// Fixing async flakiness with Awaitility
import static org.awaitility.Awaitility.*;

@Test
void cacheIsPopulatedAsync() {
    service.triggerCacheLoad("product-001");

    // BAD: Thread.sleep(1000) — hardcoded wait, flaky

    // GOOD: await with timeout
    await()
        .atMost(5, SECONDS)
        .pollInterval(100, MILLISECONDS)
        .untilAsserted(() ->
            assertThat(cache.get("product-001")).isNotNull()
        );
}

// Fixing time-dependent tests with Clock
class OrderService {
    private final Clock clock;

    OrderService(Clock clock) { this.clock = clock; }

    Order createOrder() {
        return Order.builder()
            .createdAt(LocalDateTime.now(clock))
            .build();
    }
}

@Test
void orderHasCorrectTimestamp() {
    Clock fixed = Clock.fixed(Instant.parse("2024-06-01T09:00:00Z"), UTC);
    OrderService service = new OrderService(fixed);

    Order order = service.createOrder();
    assertThat(order.getCreatedAt())
        .isEqualTo(LocalDateTime.parse("2024-06-01T09:00:00"));
    // Always deterministic
}
```

---

### ⚖️ Comparison Table

| Cause             | Symptom                        | Fix                                   |
| ----------------- | ------------------------------ | ------------------------------------- |
| Thread.sleep      | Fails on slow servers          | Awaitility await                      |
| Shared database   | Fails in parallel/random order | @BeforeEach setup, @AfterEach cleanup |
| Real network call | Fails on network issues        | Mock with WireMock/Mockito            |
| Hardcoded port    | BindException                  | RANDOM_PORT                           |
| LocalDate.now()   | Fails at midnight              | Inject fixed Clock                    |

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                      |
| ---------------------------------------- | ---------------------------------------------------------------------------- |
| "Just re-run it, flaky tests are normal" | Flaky tests are test bugs — they must be fixed; re-running hides the problem |
| "Retrying in CI fixes flakiness"         | Retry masks flakiness; only fixing the root cause eliminates it              |
| "Flaky = the test is wrong, delete it"   | Flaky tests often cover real behavior — fix the flakiness, keep the coverage |

---

### 🚨 Failure Modes & Diagnosis

**1. Flakiness Caused by Test Parallelization**
Cause: Two tests write to the same shared resource (file, database row, port).
Diagnosis: Run tests in random order; if failure correlates with test order, it's shared state.
Fix: Unique resource per test (unique port, unique DB record, temp directory per test).

**2. "Heisenbug" — Fails Only Under Load**
Cause: Test passes when run alone, fails when run with 50 other tests (resource contention, GC pauses, thread starvation).
Fix: Increase timeouts when running in parallel; reduce shared resource contention; use separate thread pools.

**3. Date/Time Flakiness at Midnight**
Cause: Test constructs expected date before midnight, assertion runs after midnight.
Fix: Inject `Clock` and fix it for all date/time operations in the system under test.

---

### 🔗 Related Keywords

- **Prerequisites:** Test Isolation, Integration Test, E2E Test
- **Related:** Awaitility, WireMock, Testcontainers, Test Parallelization, Test Order Dependency

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Test that sometimes passes, sometimes    │
│              │ fails — same code                        │
├──────────────┼───────────────────────────────────────────┤
│ TOP CAUSES   │ Thread.sleep, shared state, real network,│
│              │ port contention, LocalDate.now()         │
├──────────────┼───────────────────────────────────────────┤
│ FIXES        │ Awaitility, @BeforeEach cleanup,         │
│              │ RANDOM_PORT, Clock injection, mocking    │
├──────────────┼───────────────────────────────────────────┤
│ QUARANTINE   │ @Tag("flaky") + JIRA ticket → fix in SLA │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Zero tolerance: flaky tests destroy CI  │
│              │  trust; fix root cause, never just retry"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Shared database state is the most common cause of test order dependency flakiness. Describe a complete test isolation strategy for a Spring Boot application using PostgreSQL: (1) `@Transactional` on test class — how Spring's test transaction management works (transaction begun before test, rolled back after — never committed), (2) the limitation of `@Transactional` rollback (doesn't work for tests that spin up separate threads or use `@Async` services), (3) `@Sql` with `executionPhase = AFTER_TEST_METHOD` for explicit cleanup, (4) using TestContainers with `@DirtiesContext` to get a fresh container per test class, and (5) the performance impact of each strategy — which is fastest, which gives the strongest isolation guarantee?

**Q2.** Flaky E2E tests are the hardest to fix. Describe the systematic approach to diagnosing and fixing a flaky Selenium/Playwright test that "sometimes can't find the Login button": (1) determine if it's a timing issue (element not yet rendered), CSS selector issue (element exists but selector changed), or environment issue (test ran against wrong environment); (2) how explicit waits work (`waitForSelector`, `waitUntil` in Playwright) vs. implicit waits (global timeout — considered harmful); (3) the role of screenshots and network logs in flaky E2E test diagnosis; (4) "retry with screenshot on failure" as a CI strategy; and (5) whether the right fix is sometimes to re-architect the test (e.g., testing at a lower level where timing is more controllable).
