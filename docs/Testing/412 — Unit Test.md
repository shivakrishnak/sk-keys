---
layout: default
title: "Unit Test"
parent: "Testing"
nav_order: 412
permalink: /testing/unit-test/
number: "412"
category: Testing
difficulty: ★☆☆
depends_on: JUnit, Assertion Libraries
used_by: TDD, Test Pyramid, CI/CD
tags: #testing #foundational #java
---

# 412 — Unit Test

`#testing` `#foundational` `#java`

⚡ TL;DR — A test that verifies a single unit of code (method or class) in complete isolation from all external dependencies.

| #412 | Category: Testing | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | JUnit, Assertion Libraries | |
| **Used by:** | TDD, Test Pyramid, CI/CD | |

---

### 📘 Textbook Definition

A unit test is an automated test that verifies the smallest testable part of an application — typically a single method or class — in isolation from the rest of the system. All external dependencies (databases, services, file systems) are replaced with test doubles (mocks, stubs). Unit tests are fast, deterministic, and run thousands per second.

---

### 🟢 Simple Definition (Easy)

A unit test checks that **one small piece of code does exactly what you expect** — completely disconnected from databases, networks, or other services.

---

### 🔵 Simple Definition (Elaborated)

Unit tests are the foundation of the Test Pyramid. They are fast (milliseconds each), cheap to run, and pinpoint exactly which code is broken when they fail. By replacing real dependencies with mocks, unit tests test the logic of a single class without any external noise. They should form the majority of your test suite.

---

### 🔩 First Principles Explanation

**The core problem:**
You want to verify a specific algorithm or business rule in isolation. Running the full system to test one method is slow, brittle, and doesn't tell you which piece broke.

**The insight:**
> "Isolate the unit under test from everything else. Test only the logic of that unit with controlled inputs and observable outputs."

```
Method under test:
  double calculateDiscount(Customer c, double price)

Unit test verifies:
  given: premium customer, price = 100.0
  when:  calculateDiscount called
  then:  returns 15.0
  (No database, no HTTP call, no filesystem)
```

---

### ❓ Why Does This Exist (Why Before What)

Without unit tests, you only discover bugs when the whole system is assembled — by then, finding the source is like finding a needle in a haystack. Unit tests give you fast, precise feedback: this specific method, with this specific input, produces the wrong output.

---

### 🧠 Mental Model / Analogy

> A unit test is like testing a light switch in isolation before installing it in a house. You connect it to a power supply and a test bulb — not to the actual circuit. If the switch works in isolation, you can trust it when it's part of the larger system.

---

### ⚙️ How It Works (Mechanism)

```
Unit test structure — AAA pattern:

  Arrange: set up the unit under test and its inputs
       ↓
  Act:     call the method under test
       ↓
  Assert:  verify the output or state change

  All external dependencies replaced with:
  - Mocks: verify interactions (was a method called?)
  - Stubs: return controlled data (no real DB needed)
  - Fakes: lightweight in-memory implementations
```

---

### 🔄 How It Connects (Mini-Map)

```
[Unit Test]  <-- fastest; tests logic in isolation
     ↓
[Integration Test]  <-- tests units working together
     ↓
[E2E Test]  <-- tests full system
(Test Pyramid: Unit tests at the base — most numerous)
```

---

### 💻 Code Example

```java
// Class under test
class DiscountService {
    double calculateDiscount(Customer customer, double price) {
        if (customer.isPremium()) return price * 0.15;
        if (customer.isNewUser()) return price * 0.05;
        return 0;
    }
}

// Unit tests — JUnit 5 + Mockito
class DiscountServiceTest {
    private DiscountService service = new DiscountService();

    @Test
    void premiumCustomerGets15PercentDiscount() {
        // Arrange
        Customer customer = mock(Customer.class);
        when(customer.isPremium()).thenReturn(true);

        // Act
        double discount = service.calculateDiscount(customer, 100.0);

        // Assert
        assertThat(discount).isEqualTo(15.0);
    }

    @Test
    void newUserGets5PercentDiscount() {
        Customer customer = mock(Customer.class);
        when(customer.isPremium()).thenReturn(false);
        when(customer.isNewUser()).thenReturn(true);

        double discount = service.calculateDiscount(customer, 100.0);

        assertThat(discount).isEqualTo(5.0);
    }

    @Test
    void regularCustomerGetsNoDiscount() {
        Customer customer = mock(Customer.class);
        when(customer.isPremium()).thenReturn(false);
        when(customer.isNewUser()).thenReturn(false);

        double discount = service.calculateDiscount(customer, 100.0);

        assertThat(discount).isEqualTo(0.0);
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Unit tests are optional if integration tests exist | Unit tests pinpoint failures; integration tests confirm collaboration |
| 100% coverage = good test suite | Coverage measures lines hit, not logic verified — quality matters more |
| Unit tests only test happy paths | Test edge cases, nulls, boundaries, error paths too |
| Mocking is cheating | Mocking isolates the unit under test — that IS the point |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Testing Implementation, Not Behavior**
Tests that break when you refactor internals (even though behavior is unchanged).
Fix: test what comes OUT, not how it's computed internally.

**Pitfall 2: Overly Complex Test Setup**
Arrange section is 50 lines — the test is too coupled to implementation.
Fix: extract builders/factories; if setup is hard, the class is too complex (design smell).

**Pitfall 3: No Assertion (Test Passes for Wrong Reasons)**
```java
@Test void test() { service.doSomething(); }  // never fails — tests nothing
```
Fix: always have at least one `assertThat`; use `verify()` for void methods.

---

### 🔗 Related Keywords

- **Mocking** — replacing dependencies with controlled doubles in unit tests
- **TDD** — writing unit tests before implementing the code
- **Test Pyramid** — unit tests form the wide base
- **Integration Test** — tests multiple units working together
- **JUnit 5** — the standard Java unit testing framework

---

### 📌 Quick Reference Card


```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Test one unit of logic in complete isolation  │
│              │ — fast, deterministic, precise                │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Always — for every non-trivial method/class   │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Testing framework glue code or trivial getters│
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Test the logic here, in isolation — not the  │
│              │  whole system"                                │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Mocking --> TDD --> Test Pyramid               │
└─────────────────────────────────────────────────────────────┘
```
### 🧠 Think About This Before We Continue

**Q1.** What is the difference between a mock and a stub in unit testing?  
**Q2.** Why does 100% line coverage not guarantee a good test suite?  
**Q3.** When should you NOT use mocks in a unit test?

