---
layout: default
title: "Mocking"
parent: "Testing"
nav_order: 418
permalink: /testing/mocking/
number: "418"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, Mockito, Dependency Injection
used_by: Unit Test, TDD, Integration Test
tags: #testing #intermediate #java #mockito
---

# 418 — Mocking

`#testing` `#intermediate` `#java` `#mockito`

⚡ TL;DR — Replacing a real dependency with a controlled fake that records interactions, allowing you to verify how the unit under test uses it.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #418         │ Category: Testing                    │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ Unit Test, Mockito, Dependency Injection                          │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ Unit Test, TDD, Integration Test                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Textbook Definition

A mock is a test double that both stubs return values AND records interactions — allowing tests to verify that specific methods were called with specific arguments. Mocks are typically created using a framework (Mockito in Java) and are configured with expectations about how the code under test should interact with its dependencies.

---

## 🟢 Simple Definition (Easy)

A mock is a **fake object that pretends to be a real dependency** and also **records what your code did with it** — so you can verify "was this method called? with what arguments?"

---

## 🔵 Simple Definition (Elaborated)

Test doubles are objects that stand in for real dependencies during testing. A mock is the most powerful kind: it can be configured to return specific values (like a stub) AND it records all method calls so you can verify behavior. You use mocks when the real dependency would be slow (database), non-deterministic (external API), or impossible to set up in a test (payment gateway).

---

## 🔩 First Principles Explanation

**The core problem:**
The class under test depends on a database, email service, or payment gateway. You can't run those in a unit test. You need something that behaves like the dependency — returns what you tell it to — without the real infrastructure.

**The insight:**
> "Replace real dependencies with objects you control completely. Tell them what to return, then verify how they were used."

```
Types of test doubles:

  Dummy:  passed but never used (fills parameter list)
  Stub:   returns configured values; no interaction recorded
  Mock:   records calls + verifiable expected interactions
  Spy:    wraps a real object; record calls to verify selectively
  Fake:   working lightweight implementation (e.g., in-memory DB)

Mocks answer two questions:
  1. What should the dependency return when called?  (stubbing)
  2. Was the dependency called as expected?         (verification)
```

---

## ❓ Why Does This Exist (Why Before What)

Without mocks, unit tests require real infrastructure — a database, a running email server, a payment API. This makes tests slow, non-deterministic, and expensive to set up. Mocks eliminate external dependencies from unit tests entirely.

---

## 🧠 Mental Model / Analogy

> A mock is like a flight simulator. A pilot trains in the simulator — it behaves like the real plane but is safe, controllable, and recordable. You can say "fly through a storm" and see exactly what the pilot (code) does. You couldn't train in a real storm safely.

---

## ⚙️ How It Works (Mechanism)

```
Mockito lifecycle:

  1. Create mock: EmailService mockEmail = mock(EmailService.class);

  2. Stub return values (what to return when called):
     when(mockEmail.send(any())).thenReturn(true);
     when(mockEmail.send(null)).thenThrow(new NullPointerException());

  3. Execute code under test:
     orderService.placeOrder(order);  // internally calls mockEmail.send()

  4. Verify interactions:
     verify(mockEmail).send(any(EmailRequest.class));  // was it called?
     verify(mockEmail, times(1)).send(any());           // exactly once?
     verify(mockEmail, never()).send(null);             // never with null?
     verifyNoMoreInteractions(mockEmail);               // nothing else called?
```

---

## 🔄 How It Connects (Mini-Map)

```
[Unit Test]
       ↓ uses
[Mock: EmailService]    [Stub: UserRepository]
(verify interactions)   (return test data)
       ↓
[Class Under Test: OrderService]
       ↓ uses both but
[No real DB, no real email server]
```

---

## 💻 Code Example

```java
// Class under test
class OrderService {
    private final OrderRepository repository;
    private final EmailService emailService;

    OrderResult placeOrder(Order order) {
        OrderResult result = repository.save(order);
        emailService.sendConfirmation(order.getCustomerEmail(), result.getOrderId());
        return result;
    }
}

// Unit test with mocks
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock OrderRepository repository;       // mock: records interactions
    @Mock EmailService emailService;        // mock: records interactions
    @InjectMocks OrderService orderService; // inject mocks via constructor

    @Test
    void placingOrderSendsConfirmationEmail() {
        // Arrange — stub what dependencies return
        Order order = new Order("alice@example.com", List.of());
        OrderResult savedResult = new OrderResult("ORD-123");
        when(repository.save(order)).thenReturn(savedResult);

        // Act
        OrderResult result = orderService.placeOrder(order);

        // Assert result
        assertThat(result.getOrderId()).isEqualTo("ORD-123");

        // Verify interaction — was email sent with correct args?
        verify(emailService).sendConfirmation("alice@example.com", "ORD-123");
        verifyNoMoreInteractions(emailService);  // nothing else called
    }

    @Test
    void whenSaveFails_emailIsNotSent() {
        Order order = new Order("alice@example.com", List.of());
        when(repository.save(order)).thenThrow(new DataAccessException("DB down") {});

        assertThatThrownBy(() -> orderService.placeOrder(order))
            .isInstanceOf(DataAccessException.class);

        // Verify email was NOT sent when save failed
        verifyNoInteractions(emailService);
    }
}
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Mock = stub | Mock records interactions; stub only returns values |
| Always mock every dependency | Over-mocking hides design problems; only mock what isolates the unit |
| Mocking is a testing smell | Necessary for unit testing; but too many mocks = class does too much |
| `@Spy` and `@Mock` are the same | Spy wraps real object; mock creates empty double |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Mocking What You Don't Own**
`mock(HttpClient.class)` — your mock won't behave like the real client; breaks when client updates.
Fix: wrap third-party APIs in your own interface; mock YOUR interface, not the third-party class.

**Pitfall 2: Verifying Instead of Asserting**
`verify(repo).save(order)` without asserting the return value — the test proves the call happened but not the outcome.
Fix: always assert the result AND verify critical interactions; don't choose one over the other.

**Pitfall 3: Too Many Mocks = Design Smell**
A class constructor with 8 dependencies requires 8 mocks.
Fix: simplify the class; split responsibilities; the test smell reveals a production design smell.

---

## 🔗 Related Keywords

- **Stubbing** — configuring a mock to return a specific value (a simpler kind of test double)
- **Mockito** — the leading Java mocking framework
- **Faking / Spying** — other test double variations
- **Unit Test** — mocks enable unit tests by eliminating real dependencies
- **@InjectMocks** — Mockito annotation for injecting mocks into the class under test

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Replace real dependencies with controlled     │
│              │ doubles that record interactions              │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Unit testing classes with external dependencies│
│              │ (DB, HTTP, email, queues)                     │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ When real dependencies are fast and available  │
│              │ (use integration tests instead)               │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Replace the real thing with something you     │
│              │  control — then verify what happened"         │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Mockito --> Stubbing --> Spy --> Test Doubles  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** What is the difference between `verify()` and `assertThat()` in a test — when do you need both?  
**Q2.** Why should you mock interfaces you own rather than third-party implementations?  
**Q3.** What does it signal when you need 6+ mocks to write a unit test?

