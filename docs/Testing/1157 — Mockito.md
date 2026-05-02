---
layout: default
title: "Mockito"
parent: "Testing"
nav_order: 1157
permalink: /testing/mockito/
number: "1157"
category: Testing
difficulty: ★★☆
depends_on: Mocking, JUnit 5, Unit Test
used_by: Java Developers
related: Mocking, Stubbing, Spying, JUnit 5, Test Doubles
tags:
  - testing
  - mockito
  - java
  - mocking-framework
---

# 1157 — Mockito

⚡ TL;DR — Mockito is the dominant Java mocking framework: it generates mock objects at runtime, allows stubbing return values, captures arguments, and verifies method interactions — all with a fluent API designed to produce readable tests.

| #1157           | Category: Testing                                | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Mocking, JUnit 5, Unit Test                      |                 |
| **Used by:**    | Java Developers                                  |                 |
| **Related:**    | Mocking, Stubbing, Spying, JUnit 5, Test Doubles |                 |

---

### 🔥 The Problem This Solves

Pre-Mockito, Java developers wrote manual mock objects by hand (implementing interfaces with hardcoded return values and call trackers — hundreds of lines of boilerplate per mock). Mockito generates mock objects at runtime using bytecode manipulation, requiring zero boilerplate — the same mock that previously took 50 lines can be created with `mock(UserRepository.class)`.

---

### 📘 Textbook Definition

**Mockito** is a Java mocking framework that: (1) generates **mock objects** at runtime for any interface or class; (2) **stubs** method return values (`when().thenReturn()`); (3) **verifies** method interactions (`verify()`); (4) **captures arguments** (`ArgumentCaptor`); (5) creates **spies** on real objects. Integrates with JUnit 5 via `@ExtendWith(MockitoExtension.class)` and Spring Boot via `@MockBean`. Since Mockito 2.x: supports static mocking (via `Mockito.mockStatic()`), strict stubbing (fail on unused stubs), and inline mock maker (mock final classes).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Mockito = write `mock(ClassName.class)` instead of 50 lines of hand-written mock boilerplate.

**One analogy:**

> Mockito is a **professional costume designer**: you describe what role the actor should play (the interface), and Mockito dresses them in the perfect costume (mock object) instantly — complete with scripted responses for specific cues and a record of every scene they appeared in.

---

### 🔩 First Principles Explanation

COMPLETE MOCKITO REFERENCE:

```java
// ============ CREATION ============
UserRepo mock = mock(UserRepo.class);     // plain mock (all methods return null/0/false)
@Mock UserRepo repo;                       // annotation-based (with MockitoExtension)
UserRepo spy = spy(new UserRepoImpl());    // spy: real object with recording
@Spy UserRepoImpl realRepo;               // annotation-based spy

// ============ STUBBING ============
when(repo.findById(1L)).thenReturn(Optional.of(alice));         // return value
when(repo.findById(anyLong())).thenReturn(Optional.empty());    // wildcard arg
when(repo.save(any())).thenThrow(new DataException("full"));    // throw exception
when(repo.count()).thenReturn(1L).thenReturn(2L);               // consecutive calls
doNothing().when(repo).delete(any());     // void method — do nothing

// Spy stubbing (use doReturn, NOT when):
doReturn(42).when(spyList).size();

// ============ ARGUMENT MATCHERS ============
any(), any(Class.class)     // any value of any type
anyString(), anyInt(), anyLong(), anyDouble()
eq("exact")                 // exact value equality
argThat(user -> user.isActive())  // custom predicate
isNull(), isNotNull()
contains("substring"), matches("regex.*")
startsWith("prefix"), endsWith("suffix")

// ============ VERIFICATION ============
verify(repo).findById(1L);                       // called exactly once
verify(repo, times(3)).findById(anyLong());      // called exactly 3 times
verify(repo, never()).delete(any());             // never called
verify(repo, atLeastOnce()).save(any());         // called one or more times
verify(repo, atMost(2)).findAll();              // called at most twice
verifyNoMoreInteractions(repo);                  // no other calls
verifyNoInteractions(repo, emailService);        // no calls at all

// ============ ARGUMENT CAPTOR ============
ArgumentCaptor<User> captor = ArgumentCaptor.forClass(User.class);
verify(repo).save(captor.capture());
User saved = captor.getValue();
assertThat(saved.getEmail()).isEqualTo("alice@test.com");
assertThat(saved.isActive()).isTrue();

// Multiple captures:
verify(emailService, times(2)).send(captor.capture());
List<User> allNotified = captor.getAllValues();

// ============ INORDER VERIFICATION ============
InOrder inOrder = inOrder(validator, repo, emailService);
inOrder.verify(validator).validate(dto);
inOrder.verify(repo).save(any());
inOrder.verify(emailService).send(any());
```

MOCKITO ANNOTATIONS:

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock UserRepository repo;
    @Mock EmailService emailService;
    @Captor ArgumentCaptor<User> userCaptor;
    @InjectMocks UserService service;  // injects @Mock fields into service

    @Test void test() {
        // All annotations automatically initialized by MockitoExtension
    }
}
```

STRICT STUBBING (Mockito default since 3.x):

```java
// Strict mode:
// 1. Fails if a stub is never called during the test (UnnecessaryStubbingException)
//    → Keeps tests clean; catches stubs left from copy-paste
// 2. Fails if a stub is called with different args than configured (PotentialStubbingProblem)
//    → Catches argument mismatches

// Override for a specific test:
@Test
@MockitoSettings(strictness = LENIENT)  // disable strict for this test
void testWithFlexibleStubs() { ... }
```

---

### 🧪 Thought Experiment

ARGUMENTCAPTOR FOR COMPLEX OBJECT ASSERTIONS:

```java
@Test
void createUser_sendsWelcomeEmailWithCorrectContent() {
    service.createUser(new UserDto("Alice", "alice@test.com"));

    // How do you verify the email that was sent?
    // Option A: verify(email).send("alice@test.com", any()) — only checks email address
    // Option B: ArgumentCaptor to inspect the full Email object

    ArgumentCaptor<Email> emailCaptor = ArgumentCaptor.forClass(Email.class);
    verify(emailService).send(emailCaptor.capture());

    Email sentEmail = emailCaptor.getValue();
    assertThat(sentEmail.getTo()).isEqualTo("alice@test.com");
    assertThat(sentEmail.getSubject()).isEqualTo("Welcome to the platform!");
    assertThat(sentEmail.getBody()).contains("Hi Alice");
    assertThat(sentEmail.getBody()).contains("verify your email");
}
```

---

### 🧠 Mental Model / Analogy

> Mockito is a **dynamic proxy factory**: it creates a proxy object that intercepts all method calls. `when(...).thenReturn(...)` registers rules in the proxy's decision table. `verify(...)` queries the proxy's call log. The proxy is transparent to the code under test — it looks and acts like the real dependency, but every call is recorded and can be scripted.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `mock()` creates a fake object, `when().thenReturn()` programs responses, `verify()` confirms calls happened. That's 90% of what you need.

**Level 2:** Use `@Mock` + `@InjectMocks` + `@ExtendWith(MockitoExtension.class)` for annotation-driven setup. Use `ArgumentCaptor` to inspect complex objects passed to mocks. Use `@Spy` for partial mocking. Know the `any()` vs `eq()` distinction.

**Level 3:** Strict stubbing: Mockito 3+ enables strict stubbing by default — tests fail if you stub a method that's never called. This is a feature (catches dead stubs), not a bug. Use `@MockitoSettings(strictness = LENIENT)` to opt out for tests that need flexible stubs. `MockStatic`: mock static methods with `try (MockedStatic<Clock> mocked = mockStatic(Clock.class))` — use sparingly; code with testable static methods is usually poorly designed.

**Level 4:** Mockito internals: mocks are created using ByteBuddy (or cglib in older versions) — a subclass is created at runtime, overriding all non-final methods. `@InjectMocks` tries constructor injection first, then setter injection, then field injection — with silent failures if injection fails. The "final class" problem: before `MockitoInlineMockMaker`, final classes couldn't be mocked (subclassing doesn't work). The inline mock maker (`mockito-inline` dependency or `mockito-core` 5+) uses Java agent instrumentation to mock final classes and static methods. Spring Boot's `@MockBean`: creates a Mockito mock and registers it as a Spring bean, replacing the real bean in the application context — but this forces Spring to reload the context if the mock configuration changes between tests.

---

### 💻 Code Example

```java
// Real-world Mockito test — complete example
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock OrderRepository orderRepo;
    @Mock InventoryService inventory;
    @Mock NotificationService notifications;
    @Captor ArgumentCaptor<Order> orderCaptor;
    @InjectMocks OrderService orderService;

    @Test
    void placeOrder_sufficientInventory_createsAndNotifies() {
        // ARRANGE
        given(inventory.isAvailable("SKU-001", 2)).willReturn(true);
        given(orderRepo.save(any(Order.class))).willAnswer(inv -> {
            Order o = inv.getArgument(0);
            o.setId(UUID.randomUUID());
            return o;
        });

        // ACT
        Order result = orderService.placeOrder(new OrderRequest("SKU-001", 2, "alice@test.com"));

        // ASSERT result
        assertThat(result.getId()).isNotNull();
        assertThat(result.getStatus()).isEqualTo(CONFIRMED);

        // VERIFY order saved with correct fields
        verify(orderRepo).save(orderCaptor.capture());
        Order saved = orderCaptor.getValue();
        assertThat(saved.getSku()).isEqualTo("SKU-001");
        assertThat(saved.getQuantity()).isEqualTo(2);

        // VERIFY notification sent
        verify(notifications).sendOrderConfirmation(eq("alice@test.com"), any(Order.class));

        // VERIFY no unexpected calls
        verifyNoMoreInteractions(notifications);
    }

    @Test
    void placeOrder_insufficientInventory_throwsException() {
        given(inventory.isAvailable(anyString(), anyInt())).willReturn(false);

        assertThatThrownBy(() -> orderService.placeOrder(new OrderRequest("SKU-002", 5, "bob@test.com")))
            .isInstanceOf(InsufficientInventoryException.class);

        verifyNoInteractions(orderRepo, notifications);
    }
}
```

---

### ⚖️ Comparison Table

| Feature          | Mockito                          | Manual Mock           |
| ---------------- | -------------------------------- | --------------------- |
| Setup time       | `mock(Repo.class)`               | 50 lines of code      |
| Stub flexibility | Any method, any args, any return | Hard-coded            |
| Argument capture | `ArgumentCaptor`                 | Manual field tracking |
| Verification     | `verify()`                       | Counter fields        |
| Type safety      | Runtime (reflection)             | Compile time          |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                       |
| --------------------------------------- | --------------------------------------------------------------------------------------------- |
| "`when()` with spy is safe"             | `when(spy.method())` calls real method during setup — use `doReturn().when()`                 |
| "UnnecessaryStubbingException is a bug" | It's a valuable signal: a stub that's never used is dead code or a misaligned test            |
| "Mockito 5 changed everything"          | Core API is backward compatible; biggest changes: inline mock maker default, Java 17+ support |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CREATE       │ mock(), @Mock, spy(), @Spy               │
├──────────────┼───────────────────────────────────────────┤
│ STUB         │ when(m.method()).thenReturn(v)            │
│              │ doReturn(v).when(spy).method()            │
├──────────────┼───────────────────────────────────────────┤
│ VERIFY       │ verify(m).method(args)                   │
│              │ verify(m, times(n)) / never() / atLeast() │
├──────────────┼───────────────────────────────────────────┤
│ CAPTURE      │ @Captor ArgumentCaptor; .capture()        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The standard Java mock factory"         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@InjectMocks` uses three injection strategies in priority order: constructor injection, setter injection, field injection. Describe why constructor injection is preferred (explicit dependencies, immutable), when Mockito silently falls back to field injection (no constructor with matching types), and the hidden danger: if field injection succeeds for some mocks but not others, Mockito doesn't warn you — some dependencies are null. Write a test that proves this happens and describe how to detect and prevent it.

**Q2.** Mockito's `STRICT_STUBS` mode (default in Mockito 3+) adds two checks: (1) unused stubs fail the test; (2) potential stubbing problems (stub configured but invoked with different args) fail the test. These checks catch test quality issues. But there are legitimate cases where lenient stubs are needed: `@BeforeEach` stubs that not every test method uses. Describe: (1) how to use `lenient()` qualifier for specific stubs in a strict-mode test, (2) when `@MockitoSettings(strictness = LENIENT)` on the test class is appropriate, (3) the broader principle: why is a stub that's never used a test quality indicator (what does it mean about the test's relationship to the code)?
