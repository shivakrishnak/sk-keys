---
layout: default
title: "Stubbing"
parent: "Testing"
nav_order: 419
permalink: /testing/stubbing/
number: "419"
category: Testing
difficulty: ★☆☆
depends_on: Unit Test, Mocking
used_by: Unit Test, Mocking, TDD
tags: #testing #foundational #java #mockito
---

# 419 — Stubbing

`#testing` `#foundational` `#java` `#mockito`

⚡ TL;DR — Configuring a test double to return a specific value when called, without recording or verifying interactions.

| #419 | Category: Testing | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Unit Test, Mocking | |
| **Used by:** | Unit Test, Mocking, TDD | |

---

### 📘 Textbook Definition

Stubbing is the practice of configuring a test double (stub) to return a predetermined response when a specific method is called, without recording interactions. A stub's sole purpose is to provide controlled input data to the system under test. Unlike mocks, stubs are not verified — their invocation is not asserted.

---

### 🟢 Simple Definition (Easy)

Stubbing means **telling a fake dependency what to return** when your code calls it. You don't care if it was called — you just need it to return the right data so your test can proceed.

---

### 🔵 Simple Definition (Elaborated)

Stubs are the most common and simplest form of test double. When you write `when(userRepo.findById(1)).thenReturn(user)`, you are stubbing — telling the fake repository to return a specific user when called with ID 1. The test uses this data to verify what the code under test produces, not whether or how the repository was called.

---

### 🔩 First Principles Explanation

**The core problem:**
Your code calls a repository or external service that you can't run in a test. You need the code to receive controlled data to test your logic.

**The insight:**
> "Replace the dependency with something that reliably returns the data your test needs — no real DB, no real API, always returns exactly what you configured."

```
Stub vs Mock distinction:

  Stub:  provides INPUT to the system under test
         "When called, return this value"
         Purpose: state-based testing (what comes out?)

  Mock:  records INTERACTIONS with the system under test
         "Verify this method was called with these args"
         Purpose: interaction-based testing (what happened inside?)

  Often: a mock ALSO stubs (Mockito `when().thenReturn()`),
         but stubbing alone doesn't verify anything.
```

---

### ❓ Why Does This Exist (Why Before What)

Without stubs, your code gets null or exceptions when it calls dependencies — you can't test the happy path. Stubs provide the controlled, predictable input data needed to put the code into the exact state required for each test scenario.

---

### 🧠 Mental Model / Analogy

> A stub is like a recorded answering machine response. When your code "calls" the dependency, the stub plays back the pre-recorded message you configured. It doesn't matter who called, when, or how many times — the message is always the same. The caller (code under test) receives the controlled data and proceeds.

---

### ⚙️ How It Works (Mechanism)

```
Mockito stubbing API:

  Basic return value:
    when(userRepo.findById(1L)).thenReturn(Optional.of(user));

  Return different values on successive calls:
    when(repo.getCount()).thenReturn(0, 1, 2);  // 0 first, 1 second, 2 third

  Throw exception:
    when(paymentGateway.charge(any())).thenThrow(new PaymentException());

  Return based on argument:
    when(repo.findById(anyLong())).thenAnswer(inv -> {
        Long id = inv.getArgument(0);
        return Optional.of(new User(id, "user-" + id));
    });

  Void method with behavior:
    doNothing().when(emailService).send(any());   // default, but explicit
    doThrow(new MailException()).when(emailService).send(any());
```

---

### 🔄 How It Connects (Mini-Map)

```
[Stub]: when(repo.findById(1)).thenReturn(user)
              ↓ provides data to
[Class Under Test]: processes user
              ↓ produces
[Result]: assertThat(result).satisfies(assertions)

(No verify() — we test what comes out, not how it was retrieved)
```

---

### 💻 Code Example

```java
// Pure stubbing — testing business logic with controlled data
class PricingServiceTest {

    @Mock ProductRepository productRepo;
    @Mock CustomerRepository customerRepo;
    @InjectMocks PricingService pricingService;

    @Test
    void premiumCustomerGets15PercentDiscount() {
        // Arrange — STUBS (provide input data, no verification)
        Product product = new Product("book", 100.0);
        Customer customer = new Customer(1L, CustomerTier.PREMIUM);

        when(productRepo.findById(10L)).thenReturn(Optional.of(product));
        when(customerRepo.findById(1L)).thenReturn(Optional.of(customer));

        // Act
        PricingResult result = pricingService.calculatePrice(10L, 1L);

        // Assert — STATE based (what came out?)
        assertThat(result.getDiscount()).isEqualTo(15.0);
        assertThat(result.getFinalPrice()).isEqualTo(85.0);
        // No verify() — we don't care HOW the price was calculated internally
    }

    @Test
    void when_productNotFound_throws_exception() {
        // Stub: product doesn't exist
        when(productRepo.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> pricingService.calculatePrice(99L, 1L))
            .isInstanceOf(ProductNotFoundException.class)
            .hasMessageContaining("99");
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Stub = Mock | Stub provides data; mock verifies interactions — distinct concepts |
| You always need verify() with stubs | Stubs are for state-based tests; verify() is for interaction-based tests |
| Stubbing is only `thenReturn()` | Also: `thenThrow()`, `thenAnswer()`, `doNothing()`, `thenCallRealMethod()` |
| Stubbing unnecessary dependencies is fine | Unused stubs make tests harder to understand; use lenient() or remove |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Stubbing Too Specifically**
`when(repo.findById(1L)).thenReturn(user)` — test breaks for any other ID.
Fix: use `anyLong()` or `eq()` matchers carefully matching what production code passes.

**Pitfall 2: UnnecessaryStubbingException**
You stub a method that the code never calls — Mockito (strict mode) throws.
Fix: remove unused stubs; they indicate either dead code or a wrong assumption.

**Pitfall 3: Mutable Stub Return Objects**
Returning the same mutable object from multiple stubs — one test modifying it breaks another.
Fix: always create fresh objects in each test or use immutable data.

---

### 🔗 Related Keywords

- **Mocking** — mocks use stubbing AND verify interactions
- **Faking / Spying** — other test double variants
- **Mockito** — `when().thenReturn()` is the primary Mockito stubbing API
- **State-Based Testing** — what stubbing is designed for: test outputs given controlled inputs
- **Interaction-Based Testing** — what mocks are for: verify the code interacted correctly

---

### 📌 Quick Reference Card

| #419 | Category: Testing | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Unit Test, Mocking | |
| **Used by:** | Unit Test, Mocking, TDD | |

---

### 🧠 Think About This Before We Continue

**Q1.** When should you use a stub vs a full mock — what guides that decision?  
**Q2.** Why does Mockito's strict stubbing mode (default in JUnit 5) throw on unused stubs?  
**Q3.** What is the difference between state-based testing (stubs) and interaction-based testing (mocks)?

