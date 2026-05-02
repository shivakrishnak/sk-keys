---
layout: default
title: "Stubbing"
parent: "Testing"
nav_order: 1145
permalink: /testing/stubbing/
number: "1145"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, Mocking, Dependency Injection
used_by: Developers, TDD Practitioners
related: Mocking, Faking, Spying, Test Doubles, Mockito
tags:
  - testing
  - stubbing
  - test-doubles
  - unit-testing
---

# 1145 — Stubbing

⚡ TL;DR — A stub is a test double that returns pre-programmed responses to calls, allowing tests to control what a dependency returns without caring whether that method was actually called.

| #1145           | Category: Testing                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, Mocking, Dependency Injection       |                 |
| **Used by:**    | Developers, TDD Practitioners                  |                 |
| **Related:**    | Mocking, Faking, Spying, Test Doubles, Mockito |                 |

### 🔥 The Problem This Solves

Testing code that depends on external state (database queries, API responses, file reads) requires controlling what that external state returns. Stubs replace the dependency with a pre-programmed response — no network, no database, just the exact value needed for the test scenario.

### 📘 Textbook Definition

A **stub** is a test double that provides canned answers to calls made during a test. Unlike mocks, stubs do not verify that specific interactions occurred — they only control what values are returned. Stubs are used to put the system under test (SUT) into a specific state required for the test. Stubbing in Mockito: `when(dependency.method()).thenReturn(value)`.

### ⏱️ Understand It in 30 Seconds

**One line:**
Stub = fake return value; no verification of whether it was called.

**One analogy:**

> A stub is a **pre-recorded answer line**: when the code dials the number for "what's the user's credit score?" the stub answers "750" — regardless of what the question was or how many times the code asks. The stub doesn't care about the conversation; it just has a scripted answer.

### 🔩 First Principles Explanation

STUB VS MOCK — THE KEY DISTINCTION:

```java
// STUB: only programs return value, no verification
UserRepository stub = mock(UserRepository.class);
when(stub.findById(1L)).thenReturn(Optional.of(new User("Alice")));
// Test doesn't care whether findById was called or not
// The stub just ensures IF it's called, it returns Alice

// MOCK: programs return value AND verifies the call happened
UserRepository mockRepo = mock(UserRepository.class);
when(mockRepo.findById(1L)).thenReturn(Optional.of(new User("Alice")));
// ... test code ...
verify(mockRepo).findById(1L); // VERIFICATION: asserts it was called
```

In Mockito, the same object can act as both stub and mock:

- Stub behavior: `when(...).thenReturn(...)`
- Mock verification: `verify(...)`

Using it only as a stub (no `verify`) = stub usage.
Using it with `verify` = mock usage.

STUBBING SCENARIOS:

```java
// Stub: simple return value
when(repo.findById(1L)).thenReturn(Optional.of(user));

// Stub: throw exception (test error handling)
when(repo.findById(-1L)).thenThrow(new IllegalArgumentException());

// Stub: return different values on consecutive calls
when(repo.findAll())
    .thenReturn(List.of(user1))   // first call returns one user
    .thenReturn(List.of(user1, user2)); // second call returns two

// Stub: use argument matcher
when(repo.findByEmail(anyString())).thenReturn(Optional.empty());
when(repo.findByEmail("admin@company.com")).thenReturn(Optional.of(admin));
```

### 🧪 Thought Experiment

CONTROLLING TEST SCENARIOS WITH STUBS:

```
Test: OrderService.getOrderTotal() with discounts

Scenario 1: Standard customer (no discount)
  stub: customerRepo.findById(1L) → Customer(type=STANDARD)
  stub: discountService.getDiscount(STANDARD) → 0.0
  assert: total = itemTotal (no discount)

Scenario 2: Premium customer (10% discount)
  stub: customerRepo.findById(2L) → Customer(type=PREMIUM)
  stub: discountService.getDiscount(PREMIUM) → 0.10
  assert: total = itemTotal * 0.90

Scenario 3: Customer not found
  stub: customerRepo.findById(99L) → Optional.empty()
  assert: throws CustomerNotFoundException

Three distinct test scenarios with zero database calls.
Each test is deterministic and isolated.
```

### 🧠 Mental Model / Analogy

> A stub is a **pre-written deposition**: before the test begins, you "depose" the dependency ("if asked for user 1, say Alice; if asked for user 2, say Bob"). The test then runs, and the dependency says exactly what was scripted. No surprise answers, no network failures, no database state.

### 📶 Gradual Depth — Four Levels

**Level 1:** A stub says "if my code asks X, return Y." It doesn't check whether the code actually asked.

**Level 2:** In Mockito, create stubs with `when(mock.method(arg)).thenReturn(value)`. Use `any()` matchers for flexible argument matching. Use `thenThrow()` to test exception handling paths. The stub only activates if the exact argument match occurs.

**Level 3:** Stubbing in WireMock (HTTP stubs for integration tests): `stubFor(get("/api/users/1").willReturn(aResponse().withBody("{...}").withStatus(200)))`. WireMock stubs allow integration-level testing without real services. The same conceptual pattern: script the response to a specific request.

**Level 4:** Strict stubbing (Mockito 2.x+): `MockitoSettings(strictness = STRICT_STUBS)` fails tests with unused stubs (you programmed a response but the code never asked for it). This prevents "dead" stubs accumulating in tests after refactoring. The "unnecessary stubbing" failure is a valuable signal: either the test scenario is wrong, or the production code path no longer exercises that dependency.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  when(repo.findById(1L)).thenReturn(Optional.of(user))  │
│                                                          │
│  Mockito records: {method: findById, arg: 1L} → user    │
│                                                          │
│  Production code: repo.findById(1L)                     │
│  Mockito proxy: arg == 1L? → return Optional.of(user)   │
│                 arg != 1L? → return null (default)       │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

```
UserService.getUserProfile(userId):
  1. userRepo.findById(userId) → User
  2. accountRepo.findByUserId(userId) → Account
  3. preferencesRepo.findByUserId(userId) → Preferences
  4. return UserProfile(user, account, preferences)

Test: stub all three repos for fast, isolated unit test
  when(userRepo.findById(42L)).thenReturn(Optional.of(alice))
  when(accountRepo.findByUserId(42L)).thenReturn(Optional.of(aliceAccount))
  when(prefsRepo.findByUserId(42L)).thenReturn(alicePrefs)

  UserProfile profile = service.getUserProfile(42L)
  assertThat(profile.getDisplayName()).isEqualTo("Alice Smith")
  // No database. Runs in < 5ms.
```

### 💻 Code Example

```java
@ExtendWith(MockitoExtension.class)
class WeatherAlertServiceTest {

    @Mock
    private WeatherApi weatherApi;
    @InjectMocks
    private WeatherAlertService service;

    @Test
    void sendAlert_whenTemperatureExceedsThreshold() {
        // STUB: control what the API returns
        when(weatherApi.getCurrentTemperature("London"))
            .thenReturn(38.5);  // above alert threshold of 35°C

        service.checkAndAlert("London");

        // Verify alert was sent (mock behavior, not stub)
        verify(notificationService).sendAlert(eq("London"), contains("Heat Alert"));
    }

    @Test
    void noAlert_whenTemperatureNormal() {
        // STUB: different scenario, different return
        when(weatherApi.getCurrentTemperature("London"))
            .thenReturn(22.0);  // normal temperature

        service.checkAndAlert("London");

        verifyNoInteractions(notificationService);
    }
}
```

### ⚖️ Comparison Table

|                         | Stub | Mock | Fake              |
| ----------------------- | ---- | ---- | ----------------- |
| Returns scripted values | ✓    | ✓    | ✓ (real logic)    |
| Verifies calls          | ✗    | ✓    | ✗                 |
| Has real logic          | ✗    | ✗    | ✓                 |
| Framework needed        | Yes  | Yes  | No (hand-written) |

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                 |
| ----------------------------------------- | ----------------------------------------------------------------------- |
| "Stubbing and mocking are the same thing" | Stubs provide responses; mocks also verify interactions                 |
| "Stubs should have verify() calls"        | Stubs intentionally do NOT verify; use mock if you need verification    |
| "Unnecessary stubs are harmless"          | They indicate either dead code paths or misaligned tests; clean them up |

### 🚨 Failure Modes & Diagnosis

**1. Stub Returns Wrong Value Type → NullPointerException**

Cause: `when(repo.findAll()).thenReturn(null)` — null where a list is expected.
Fix: Always return sensible defaults from stubs: empty collections, empty Optionals. Use `thenReturn(Collections.emptyList())`.

**2. Stub Never Activates (Argument Mismatch)**

Cause: Stub set up with `eq("Alice")` but production code calls with `"alice"` (case mismatch).
Fix: Use `any()` for flexible matching, or debug argument values with `ArgumentCaptor`.

### 🔗 Related Keywords

- **Prerequisites:** Unit Test, Mocking
- **Related:** Faking, Spying, WireMock, Mockito, Test Doubles

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Pre-programmed return value for a        │
│              │ dependency call                          │
├──────────────┼───────────────────────────────────────────┤
│ VS MOCK      │ Stub = returns value, no verification    │
│              │ Mock = returns value + verifies call     │
├──────────────┼───────────────────────────────────────────┤
│ MOCKITO      │ when(dep.method(arg)).thenReturn(val)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Script the answer; don't check if asked"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Describe the difference between state verification and behaviour verification in tests, and when each is appropriate. State verification: after the test, assert that the object's state changed correctly (the returned value, the modified field). Behaviour verification: assert that the correct interactions with dependencies occurred (verify the right methods were called). Give three examples where state verification is sufficient and three examples where behaviour verification is necessary — and explain what class of bug only behaviour verification would catch.

**Q2.** WireMock stubs vs. Mockito stubs: both stub responses, but at different layers. When testing an HTTP client that calls an external REST API, compare: (1) mocking the `HttpClient` with Mockito — what you're actually verifying, what you're NOT verifying (HTTP headers, URL construction, request body serialization); (2) using WireMock to stub the actual HTTP server — what additional verification you get for free. Describe a specific bug that WireMock would catch but Mockito mocking of `HttpClient` would miss.
