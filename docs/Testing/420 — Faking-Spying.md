---
number: "420"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, Mocking, Stubbing
used_by: Unit Test, Mocking, TDD
tags: #testing #intermediate #java #mockito
---

# 420 — Faking / Spying

`#testing` `#intermediate` `#java` `#mockito`

⚡ TL;DR — Fakes are lightweight working implementations (e.g., in-memory DB). Spies are real objects that also record interactions for selective verification.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #420         │ Category: Testing                    │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ Unit Test, Mocking, Stubbing                                      │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ Unit Test, Mocking, TDD                                           │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

A **Fake** is a test double with a working but simplified implementation — an in-memory implementation of a repository, for example. A **Spy** is a test double that wraps a real object and delegates calls to it by default, while also recording calls for selective verification. Unlike mocks, spies call the real method unless explicitly stubbed.

---

## 🟢 Simple Definition (Easy)

A **fake** is a simplified working substitute (like an in-memory database). A **spy** is a real object with recording attached — it does real work AND records what was called.

---

## 🔵 Simple Definition (Elaborated)

Fakes and spies occupy different positions in the test double spectrum. Fakes are handwritten implementations that work correctly but are simplified (e.g., HashMap instead of real DB). Spies are Mockito-created wrappers around real objects — the real method runs, but you can also verify specific interactions. Spies are risky: the real code runs in tests, which can cause unintended side effects.

---

## 🔩 First Principles Explanation

**The problem with mocks:**
Mocks return null by default — if you forget to stub a method, the code gets null silently. This can create unrealistic test scenarios.

**The problem with real objects in tests:**
They're slow (DB), have side effects (sending emails), or are expensive to set up.

**Fake insight:**
> "Write a simple, working implementation that behaves like the real thing for test purposes but has no external dependencies."

**Spy insight:**
> "Run the real code, but tap into it — verify specific method calls without replacing the real implementation entirely."

```
Test Double Spectrum:

  Dummy  -->  Stub  -->  Fake  -->  Spy  -->  Mock
  (unused)  (returns)  (works)  (real+record)  (controlled)
  simplest ---------------------------------> most controlled
```

---

## ❓ Why Does This Exist (Why Before What)

Fakes exist when a stub is too simplistic (needs to actually store and retrieve data) but a real implementation is too expensive. Spies exist when you need to run real code but also want to verify specific behaviors — common for legacy code where full mocking is impractical.

---

## 🧠 Mental Model / Analogy

> **Fake**: A stage prop car that actually drives (simplified, no engine, no safety features) but allows filming real driving scenes. Works for the specific test scenario, not full production use.

> **Spy**: A secret agent embedded in a real organization. They do their actual job, but they're also reporting back to headquarters about what they're doing. Real work happens; it's also observed.

---

## ⚙️ How It Works (Mechanism)

```
FAKE — handwritten implementation:
  interface UserRepository { Optional<User> findById(Long id); void save(User u); }

  class InMemoryUserRepository implements UserRepository {
    private final Map<Long, User> store = new HashMap<>();

    @Override public Optional<User> findById(Long id) { return Optional.ofNullable(store.get(id)); }
    @Override public void save(User user) { store.put(user.getId(), user); }
  }
  // Used instead of real DB — lightweight, works correctly, no infrastructure

SPY — Mockito wrapping real object:
  EmailService realEmailService = new RealEmailService();
  EmailService spy = Mockito.spy(realEmailService);

  // Default: calls the real method
  // Selective stubbing: override specific behavior
  doNothing().when(spy).sendConfirmation(any());  // prevent real email sending

  // After test:
  verify(spy).sendConfirmation("alice@example.com");  // verify it was called
```

---

## 🔄 How It Connects (Mini-Map)

```
[Test doubles taxonomy]
  Dummy   -- filler; never used
  Stub    -- returns data; no record
  Fake    -- works correctly; simplified
  Spy     -- real + records; selective stub
  Mock    -- controlled; records all; verify all
```

---

## 💻 Code Example

```java
// FAKE: in-memory repository for fast, realistic tests
class InMemoryOrderRepository implements OrderRepository {
    private final Map<String, Order> store = new HashMap<>();
    private long counter = 0;

    @Override
    public Order save(Order order) {
        String id = "ORD-" + (++counter);
        Order saved = order.withId(id);
        store.put(id, saved);
        return saved;
    }

    @Override
    public Optional<Order> findById(String id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public List<Order> findByCustomerId(Long customerId) {
        return store.values().stream()
            .filter(o -> o.getCustomerId().equals(customerId))
            .collect(toList());
    }
}

// Test using fake — behaves correctly, no real DB
class OrderServiceFakeTest {
    private OrderRepository orderRepo = new InMemoryOrderRepository(); // FAKE
    @Mock EmailService emailService;  // MOCK (prevent real emails)
    private OrderService service = new OrderService(orderRepo, emailService);

    @Test
    void orderCanBeRetrievedAfterPlacing() {
        Order order = new Order(customerId: 1L, items: List.of(new Item("book", 29.99)));
        OrderResult result = service.placeOrder(order);

        // Can actually retrieve from fake — unlike a pure mock
        Optional<Order> found = orderRepo.findById(result.getOrderId());
        assertThat(found).isPresent();
        assertThat(found.get().getCustomerId()).isEqualTo(1L);
    }
}

// SPY: wrapping a real object
@ExtendWith(MockitoExtension.class)
class DiscountCalculatorSpyTest {

    @Spy
    DiscountCalculator calculator = new DiscountCalculator(); // REAL object wrapped

    @Test
    void premiumDiscountIsCalculatedCorrectly() {
        // Real method runs — not stubbed
        double discount = calculator.calculate(CustomerTier.PREMIUM, 100.0);
        assertThat(discount).isEqualTo(15.0);

        // Verify the real method was called
        verify(calculator).calculate(CustomerTier.PREMIUM, 100.0);
    }
}
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Fake = mock | Fake has real working logic; mock has no logic, only configured returns |
| Spy always stubs all methods | Spy calls real methods by default; only stubbed methods are overridden |
| Spies are safe for all tests | Spies run real code — side effects can still occur if not carefully controlled |
| Fakes are too much work | For complex state-based behavior (repositories), fakes are often less work than many stubs |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Spy Leaking Real Behavior**
You spied a class expecting to stub one method, but forgot — the real method ran and sent 100 emails.
Fix: use `doNothing().when(spy)` or `doReturn().when(spy)` syntax (safer than `when().thenReturn()` for spies).

**Pitfall 2: Fake Diverging from Real Implementation**
Fake validates email as true for any string; real implementation is strict — tests pass, prod fails.
Fix: test your fake against the same contract tests as the real implementation.

**Pitfall 3: Over-Relying on Fakes (Skipping Integration Tests)**
All tests use fakes → never tested with real DB → production breaks on DB constraints.
Fix: fakes enable fast unit/service tests; integration tests (Testcontainers) validate real DB behavior.

---

## 🔗 Related Keywords

- **Mocking** — mocks control and record interactions; fakes provide working implementations
- **Stubbing** — configuring return values; simpler than fakes for state
- **Testcontainers** — provides a real DB for integration tests; fakes are for unit tests
- **@Spy (Mockito)** — annotation to create a spy on a real object
- **Test Doubles** — the umbrella term for dummy, stub, fake, spy, and mock

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     Fake: working lightweight impl (no infra)       │
│              Spy: real object + interaction recording        │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     Fake: repository behavior more complex than     │
│              stubs; Spy: wrapping legacy code / real object  │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   Spy with side effects (real code runs!);        │
│              Fake when integration test is more appropriate  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    "Fake does the real job cheaply;                │
│              Spy watches the real job actually happen"       │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE Mocking --> Test Doubles --> Testcontainers      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** When is a fake preferable to a mock + stubs for testing a repository?  
**Q2.** What is the key risk when using `@Spy` in Mockito — and how do you mitigate it?  
**Q3.** How do you ensure your fake repository doesn't diverge from the real one's behavior over time?

