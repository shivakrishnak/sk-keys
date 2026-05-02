---
layout: default
title: "Regression Test"
parent: "Testing"
nav_order: 1136
permalink: /testing/regression-test/
number: "1136"
category: Testing
difficulty: ★★☆
depends_on: "Unit Test, Integration Test, E2E Test"
used_by: "CI-CD pipelines, release validation, bug fix verification"
tags: #testing, #regression-test, #bug-fix, #test-coverage, #ci-cd
---

# 1136 — Regression Test

`#testing` `#regression-test` `#bug-fix` `#test-coverage` `#ci-cd`

⚡ TL;DR — **Regression testing** verifies that previously working functionality hasn't broken after a code change. A "regression" is a bug reintroduced after being fixed — or a feature that was working and now isn't. Every bug fix should be followed by a regression test: write a test that would have caught the bug, then keep it running forever. A regression test suite grows continuously — it's the institutional memory of "things that have broken before."

| #1136 | Category: Testing | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Unit Test, Integration Test, E2E Test | |
| **Used by:** | CI-CD pipelines, release validation, bug fix verification | |

---

### 📘 Textbook Definition

**Regression test**: an automated test that verifies that a change (bug fix, new feature, refactoring) hasn't broken functionality that was previously working. Origin: "regression" in mathematics means going back to a prior state; in software, a regression is a bug that reappears after being fixed, or functionality that worked and no longer does after a change. Regression testing practices: (1) **Bug-fix regression tests**: when a bug is found and fixed, write a test that would have caught it before fixing, commit the test alongside the fix, and never remove it; (2) **Full regression suite**: run the entire test suite before each release to verify no existing functionality is broken; (3) **Selective regression**: when time is limited, run tests most likely affected by the changed code (test impact analysis); (4) **Visual regression**: screenshot-based comparison to catch unintended UI changes. Regression test scope spans all test levels: unit, integration, and E2E. The regression test suite is a living document — it grows with every bug found in production. It is the team's codified knowledge of "things that have broken before."

---

### 🟢 Simple Definition (Easy)

You fixed a bug where `user.getAge()` returned -1 for new accounts. You write a test: "new account age should be 0, not -1." That test is now a regression test. Six months later, a colleague refactors the `User` class — the test fails. The regression was caught before production. Without the test, the bug would have silently re-emerged.

---

### 🔵 Simple Definition (Elaborated)

Regression tests serve two purposes:
1. **Catch bug recurrence**: a specific bug was fixed; the test ensures it doesn't come back
2. **Catch unintended side effects**: a change in one area accidentally breaks something else

**Regression test lifecycle**:
1. Bug found in production (e.g., order total calculation rounds incorrectly)
2. Developer reproduces the bug with a failing test
3. Developer fixes the bug → test passes
4. Test is committed with the fix and runs in CI forever
5. If anyone ever breaks order total calculation again → test fails immediately

**Full regression suite vs selective regression**:
- **Full regression**: run ALL tests before each release — comprehensive but slow (could take hours)
- **Selective/targeted regression**: test impact analysis — identify which tests are affected by changed code files and run only those — faster but risks missing indirect effects
- Modern CI practice: full regression runs nightly or before production releases; selective regression runs on every PR

**Difference from other test types**: regression tests aren't a different technical type of test — they're unit, integration, or E2E tests. The distinction is PURPOSE: a test specifically written because a bug was found and fixed is a regression test. Many tests serve dual purpose (both validate current behavior AND guard against regression).

---

### 🔩 First Principles Explanation

```java
// REGRESSION TESTS - written to guard against specific previously-found bugs

// Bug ticket #BUG-4421: "Order total is null when all items have free shipping"
// Fix date: 2024-03-15
// Without this test, a future refactor of OrderCalculator could reintroduce this bug

@Test
@DisplayName("BUG-4421: order total is zero (not null) when all items have free shipping")
void bug4421_orderTotalIsZeroNotNullForFreeShippingItems() {
    // ARRANGE: order with items that have free shipping (price = 0 for shipping)
    Order order = new Order();
    order.addItem(new OrderItem("prod-1", 29.99, Shipping.FREE));
    order.addItem(new OrderItem("prod-2", 19.99, Shipping.FREE));
    
    // ACT
    BigDecimal total = orderCalculator.calculateTotal(order);
    
    // ASSERT: total should be sum of item prices (not null, not NPE)
    assertThat(total).isNotNull();
    assertThat(total).isEqualByComparingTo(new BigDecimal("49.98"));
    // Note: this test is deliberately named with the bug ticket for traceability
}

// Bug ticket #BUG-5902: "Concurrent requests cause duplicate order IDs"  
// Fix: added unique constraint + retry logic
// Regression test: verifies concurrent orders don't generate duplicate IDs

@Test
@DisplayName("BUG-5902: concurrent order creation does not produce duplicate order IDs")
void bug5902_concurrentOrdersHaveUniqueIds() throws InterruptedException {
    int threads = 20;
    ExecutorService executor = Executors.newFixedThreadPool(threads);
    ConcurrentHashMap<String, Boolean> orderIds = new ConcurrentHashMap<>();
    CountDownLatch latch = new CountDownLatch(threads);
    AtomicInteger failures = new AtomicInteger(0);
    
    for (int i = 0; i < threads; i++) {
        executor.submit(() -> {
            try {
                String orderId = orderService.createOrder(buildTestOrder());
                if (orderIds.putIfAbsent(orderId, true) != null) {
                    failures.incrementAndGet();  // duplicate ID found!
                }
            } catch (Exception e) {
                failures.incrementAndGet();
            } finally {
                latch.countDown();
            }
        });
    }
    
    latch.await(10, TimeUnit.SECONDS);
    executor.shutdown();
    
    assertThat(failures.get())
        .as("No duplicate order IDs should be generated under concurrent load")
        .isZero();
}

// Bug ticket #BUG-6110: "Negative quantity items crash checkout"
// Input validation was missing; fixed by validating in CartService

@Test
@DisplayName("BUG-6110: adding item with negative quantity throws validation error")
void bug6110_negativeQuantityThrowsValidationError() {
    // ARRANGE
    Cart cart = new Cart("user-1");
    
    // ACT + ASSERT: negative quantity must be rejected, not cause NPE or DB error
    assertThatThrownBy(() -> cartService.addItem(cart, "prod-1", -5))
        .isInstanceOf(ValidationException.class)
        .hasMessageContaining("Quantity must be positive");
    
    // Cart should be unchanged
    assertThat(cart.getItems()).isEmpty();
}
```

```java
// SELECTIVE REGRESSION - Test Impact Analysis approach

// Modern CI tools (like JaCoCo + test impact analysis plugins) can identify
// which tests are affected by changed source files.
// Example: when OrderCalculator.java changes, run:
// - OrderCalculatorTest (direct)
// - OrderServiceTest (uses OrderCalculator)
// - CheckoutIntegrationTest (uses OrderService)
// But NOT: UserServiceTest, ProductCatalogTest (unrelated)

// Manual version: use Maven Surefire with test tags
// Run bug-regression tests only for bug-fix PRs:
// mvn test -Dgroups=regression-bug-fixes

@Tag("regression-bug-fixes")   // run on every PR
@Tag("regression-full")        // run before every release
class OrderCalculatorRegressionTest {
    
    @Test @Tag("regression-bug-fixes")
    @DisplayName("BUG-4421: ...")
    void bug4421() { ... }
}

// Maven/Gradle profiles:
// PR pipeline: mvn test -Dgroups="unit | regression-bug-fixes"
// Release pipeline: mvn test -Dgroups="unit | integration | regression-full | e2e"
```

```
REGRESSION TEST CULTURE CHECKLIST:

  EVERY BUG FIX MUST INCLUDE:
  ✓ A failing test that reproduces the bug BEFORE the fix
  ✓ The fix makes the test pass
  ✓ The test is committed alongside the fix
  ✓ The test references the bug ticket ID in its name/javadoc
  ✓ The test is never removed

  REGRESSION TEST NAMING:
  ✓ Include bug ticket ID: "BUG-4421: ..."
  ✓ Describe the regressed behavior, not just the fix
  ✓ Makes the failure message self-explanatory

  WHEN REGRESSION TEST FAILS:
  1. Look up the bug ticket (ID is in the test name)
  2. Understand the original bug
  3. The new code has re-introduced the same bug
  4. Fix it (again), possibly with a better fix
```

---

### ❓ Why Does This Exist (Why Before What)

In a codebase with hundreds of thousands of lines changed over years, it's impossible to remember every bug that was fixed and every edge case that was discovered. Without regression tests, the same bugs reappear — and are fixed again — repeatedly, wasting engineering time. Regression tests are the codebase's institutional memory: every regression test encodes "this broke once; here's how to detect if it breaks again." They transform tribal knowledge into automated enforcement.

---

### 🧠 Mental Model / Analogy

> **Regression tests are scar tissue**: just as biological scar tissue forms after an injury to strengthen the exact spot that was damaged, regression tests form after a bug to protect the exact behavior that was broken. The scar is permanent — it persists as long as the code exists. And just as scar tissue protects against re-injury at the same spot, regression tests protect against re-introducing the same bug.

---

### 🔄 How It Connects (Mini-Map)

```
Bug found in production → fixed → need to ensure it never returns
        │
        ▼
Regression Test ◄── (you are here)
(unit/integration/E2E test specifically guarding against known bugs)
        │
        ├── Unit Test: most regression tests are unit tests (fast, targeted)
        ├── Integration Test: some regressions require integration-level tests
        ├── E2E Test: critical path regressions verified end-to-end
        └── CI-CD Pipeline: regression suite runs on every PR and before release
```

---

### 💻 Code Example

```java
// E2E regression test for a critical production bug
// Bug: when user had >10 items in cart, checkout button disappeared (CSS z-index issue)

@Test
@Tag("regression-e2e")
@DisplayName("BUG-7203: checkout button visible when cart has more than 10 items")
void bug7203_checkoutButtonVisibleWithMoreThan10CartItems(Page page) {
    // Add 11 items to the cart
    loginAs(page, "test@example.com");
    for (int i = 0; i < 11; i++) {
        addProductToCart(page, "prod-" + i);
    }
    
    page.navigate(BASE_URL + "/cart");
    
    // ASSERT: checkout button is visible AND clickable (not hidden by z-index issue)
    Locator checkoutButton = page.locator("[data-testid='checkout-button']");
    assertThat(checkoutButton).isVisible();
    assertThat(checkoutButton).isEnabled();
    
    // Verify we can actually proceed to checkout
    checkoutButton.click();
    assertThat(page).hasURL(Pattern.compile(".*/checkout"));
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Regression tests are a separate test type | Regression tests are unit, integration, or E2E tests — differentiated by purpose, not implementation. A unit test written because a bug was found IS a regression test. Most tests serve as both behavioral tests AND regression guards. |
| All tests are regression tests | While all tests guard against future regressions incidentally, the term "regression test" typically refers to tests specifically written in response to a bug. This distinction matters because it: (1) tracks which tests came from production bugs, (2) prioritizes these tests in selective regression, and (3) provides traceability to bug tickets. |
| Once a regression test passes, the bug is gone for good | The test prevents that exact regression, but similar bugs can appear in related code paths not covered by the test. Regression tests are targeted guards, not comprehensive coverage. After finding a bug, consider: "what similar code could have the same problem?" and add tests there too. |

---

### 🔗 Related Keywords

- `Unit Test` — most regression tests are implemented as unit tests
- `Bug Fix` — every bug fix should produce a regression test
- `CI-CD Pipeline` — regression tests run automatically on every code change
- `Smoke Test` — a subset of regression tests for critical paths, run after deployment
- `Test Coverage` — regression tests improve coverage of historically buggy code

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REGRESSION TEST = guard against bug recurrence          │
│                                                          │
│ WORKFLOW:                                               │
│ 1. Bug found → write failing test reproducing bug      │
│ 2. Fix bug → test passes                               │
│ 3. Commit test + fix together                          │
│ 4. Test runs forever in CI                             │
│                                                          │
│ NAMING: include bug ticket ID ("BUG-4421: ...")        │
│ NEVER remove a regression test                         │
│                                                          │
│ TYPES: unit | integration | E2E                        │
│ (same implementation, different purpose)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Test impact analysis (TIA) tools (like Gradle Enterprise's predictive test selection or Microsoft Research's "STARTS") analyze code change sets and test coverage data to predict which tests need to run for a given change. Instead of running 2,000 tests on every PR, TIA might run 200 relevant tests in 2 minutes. The trade-off: TIA can miss indirect effects (module A changes; module B uses A; module B's tests might not be flagged). How should teams balance speed (run fewer tests per PR via TIA) vs confidence (run all tests to catch indirect effects)? When is it acceptable to rely on TIA, and when must you run the full suite?

**Q2.** "Test debt" is the accumulation of missing regression tests for known production bugs — bugs that were fixed but never had a regression test added. This happens when teams are in "fix and ship" mode under pressure. The debt compounds: the same bugs re-appear, are fixed again without tests, and the pattern repeats. Design a test debt reduction strategy: how do you identify which production bugs lack regression tests? How do you prioritize which debt to pay off first? How do you enforce the "bug fix = regression test" rule going forward without slowing down incident response?
