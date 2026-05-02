---
layout: default
title: "Spying"
parent: "Testing"
nav_order: 1147
permalink: /testing/spying/
number: "1147"
category: Testing
difficulty: ★★★
depends_on: Mocking, Stubbing, Unit Test
used_by: Developers, TDD Practitioners
related: Mocking, Stubbing, Faking, Test Doubles, Mockito Spy
tags:
  - testing
  - spying
  - test-doubles
  - partial-mocking
---

# 1147 — Spying

⚡ TL;DR — A spy wraps a real object, delegates all calls to its real implementation, but records every interaction — allowing you to verify what was called while the real code actually executes. Spies also enable selective stubbing (override specific methods while keeping the rest real).

| #1147           | Category: Testing                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Mocking, Stubbing, Unit Test                         |                 |
| **Used by:**    | Developers, TDD Practitioners                        |                 |
| **Related:**    | Mocking, Stubbing, Faking, Test Doubles, Mockito Spy |                 |

### 🔥 The Problem This Solves

Sometimes you have a class with real logic you want to exercise, but you also need to: (1) verify that specific internal methods were called, or (2) override just ONE method without replacing the whole object with a mock. A full mock replaces all logic. A spy gives you the real logic with observation and selective override capability.

### 📘 Textbook Definition

A **spy** (or partial mock) is a test double that wraps a real object. By default, all method calls delegate to the real implementation. The spy records all interactions (like a mock), enabling `verify()` calls. Specific methods can be selectively stubbed using `doReturn(...).when(spy).method()` while all other methods use the real implementation. In Mockito: created with `spy(realObject)` or `@Spy` annotation.

### ⏱️ Understand It in 30 Seconds

**One line:**
Spy = real object with a wiretap + selective method override capability.

**One analogy:**

> A spy is a **surveillance camera** on a real employee: the employee does their actual job (real implementation), but a camera records every action (interaction recording). If needed, you can also intercept specific actions ("if they try to open the safe, redirect them to a dummy safe" — selective stubbing).

### 🔩 First Principles Explanation

SPY LIFECYCLE IN MOCKITO:

```java
// Create spy from real object
List<String> realList = new ArrayList<>();
List<String> spyList = spy(realList);

// Real behavior: calls actual ArrayList methods
spyList.add("hello");
spyList.add("world");
assertThat(spyList.size()).isEqualTo(2);  // real ArrayList size = 2

// Verify interactions (spy records all calls)
verify(spyList).add("hello");
verify(spyList).add("world");

// Selective stub: override one method only
doReturn(42).when(spyList).size();  // lie about size
assertThat(spyList.size()).isEqualTo(42);  // stubbed
assertThat(spyList.get(0)).isEqualTo("hello");  // real (NOT stubbed)
```

KEY RULE — USE `doReturn()` NOT `when()` WITH SPIES:

```java
// WRONG: when() with spy calls the real method FIRST, then stubs
when(spy.someMethod()).thenReturn("mocked");
// someMethod() IS CALLED for real during when() setup → potential NPE/side effects

// CORRECT: doReturn() avoids calling the real method during setup
doReturn("mocked").when(spy).someMethod();
// Real method NOT called; stub applied directly
```

WHEN TO USE A SPY:

```
Use Spy when:
  ✓ You want to test a real implementation but verify it calls collaborators
  ✓ You need to override ONLY ONE method of a real class (partial mock)
  ✓ You're testing legacy code that can't be easily restructured
  ✓ The class under test has a method that calls another method you want to stub

Prefer full mock when:
  ✓ You want to replace the entire behavior (no real code)
  ✓ The dependency is external (database, API)

Spies used CORRECTLY: testing integration within a class
Spies used AS CODE SMELL: hiding design problems (class is too large to mock cleanly)
```

### 🧪 Thought Experiment

SPYING ON AN ABSTRACT CLASS TEMPLATE METHOD:

```java
// Abstract class with template method pattern
public abstract class DataExporter {
    public void export(List<Data> items) {
        List<Data> filtered = filter(items);    // abstract: override in subclass
        List<String> lines = format(filtered);  // abstract: override in subclass
        write(lines);                           // real: writes to file
    }
    protected abstract List<Data> filter(List<Data> items);
    protected abstract List<String> format(List<Data> items);
    protected void write(List<String> lines) { /* real file I/O */ }
}

// Test: spy on concrete subclass, stub write() to avoid real file I/O
DataExporter exporter = spy(new CsvDataExporter());
doNothing().when(exporter).write(anyList());  // suppress file I/O

exporter.export(testData);

// Verify filter and format were called correctly
verify(exporter).filter(testData);
verify(exporter).format(filteredData);
// Real filter() and format() logic was exercised
// Real write() was NOT called (stubbed)
```

### 🧠 Mental Model / Analogy

> A spy is a **method interceptor**: transparent to the object under test (it executes real code), but each method call passes through an observation layer first. You can see all traffic (verify calls), and you can intercept specific calls to return different responses (selective stubbing). Like a proxy server that normally passes traffic through but can intercept specific requests.

### 📶 Gradual Depth — Four Levels

**Level 1:** A spy lets real code run while recording what methods were called. You can also override specific methods on the real object.

**Level 2:** Use `@Spy` on a real object. Call `doReturn().when(spy).method()` to stub specific methods. Use `verify(spy).method()` to check it was called. Remaining methods call the real implementation.

**Level 3:** Spy with `@InjectMocks`: combining `@Spy` and `@InjectMocks` allows injecting a partially-real object. Use case: `@Spy @InjectMocks UserService service` — spy on the service itself (record its own method calls), inject real or mock dependencies. Advanced use: verifying internal method delegation without changing the class. Warning: this is often a design smell — if you need to spy on the class under test, consider refactoring.

**Level 4:** Spies in the context of hexagonal architecture: spies are most appropriate at the domain/application layer boundary when you want to verify that a domain service triggered the right application-level events or callbacks, while the domain logic itself runs for real. They become problematic when used to "fix" a class that has too many responsibilities — the right fix is to extract the responsibility into a separate, mockable dependency.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              SPY INTERCEPTION MECHANISM                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  spy(realObject) → creates wrapper (cglib proxy)        │
│                                                          │
│  Call: spyList.add("hello")                             │
│    → Spy proxy: record interaction {add, "hello"}       │
│    → Is "add" stubbed? No                               │
│    → Delegate to real ArrayList.add("hello") ✓          │
│                                                          │
│  Call: spyList.size()                                   │
│    → Spy proxy: record interaction {size}               │
│    → Is "size" stubbed? Yes (doReturn(42))              │
│    → Return 42 (real method NOT called)                 │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

```
Testing AuditService that wraps UserService:

AuditService:
  UserService userService (real dependency)
  AuditLog auditLog (mock)

  public User createUser(UserDto dto) {
    User user = userService.createUser(dto);  // calls real UserService
    auditLog.record("USER_CREATED", user.getId());  // call to mock
    return user;
  }

Test:
  UserService spyUserService = spy(new UserService(fakeRepo));
  AuditLog mockAuditLog = mock(AuditLog.class);
  AuditService service = new AuditService(spyUserService, mockAuditLog);

  User created = service.createUser(new UserDto("alice@test.com"));

  // Verify real UserService was called correctly
  verify(spyUserService).createUser(any(UserDto.class));

  // Verify audit log was called with correct user ID
  verify(mockAuditLog).record(eq("USER_CREATED"), eq(created.getId()));

  // Real UserService logic ran → user actually created in fakeRepo
  assertThat(fakeRepo.findById(created.getId())).isPresent();
```

### 💻 Code Example

```java
@ExtendWith(MockitoExtension.class)
class NotificationServiceTest {

    @Spy
    private EmailFormatter emailFormatter = new EmailFormatter(); // real object
    @Mock
    private SmtpClient smtpClient;
    @InjectMocks
    private NotificationService service;

    @Test
    void sendWelcomeEmail_formatsAndSendsEmail() {
        // EmailFormatter runs for real; SmtpClient is mocked (no real email sent)
        service.sendWelcomeEmail("alice@example.com", "Alice");

        // Verify real formatter was called (spy records the interaction)
        verify(emailFormatter).formatWelcome("Alice");

        // Verify SMTP client received the formatted email
        verify(smtpClient).send(eq("alice@example.com"), contains("Welcome, Alice"));
    }

    @Test
    void sendWelcomeEmail_withCustomTemplate_usesCustomFormat() {
        // Stub ONE method on real EmailFormatter
        doReturn("CUSTOM WELCOME").when(emailFormatter).formatWelcome(anyString());

        service.sendWelcomeEmail("bob@example.com", "Bob");

        verify(smtpClient).send(eq("bob@example.com"), eq("CUSTOM WELCOME"));
    }
}
```

### ⚖️ Comparison Table

|                 | Mock                                           | Spy                                        |
| --------------- | ---------------------------------------------- | ------------------------------------------ |
| Base behavior   | All methods stubbed (return null/0 by default) | All methods delegate to real object        |
| Creation        | `mock(Class.class)`                            | `spy(realObject)`                          |
| Stubbing syntax | `when(mock.method()).thenReturn(x)`            | `doReturn(x).when(spy).method()`           |
| Use case        | Replace entire dependency                      | Observe/partially override real object     |
| Risk            | Tests don't exercise real logic                | May cause real side effects if not careful |

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                  |
| ------------------------------------ | ---------------------------------------------------------------------------------------- |
| "Spy is a safer mock"                | Spy exercises real code — real side effects (DB writes, emails) can occur if not stubbed |
| "`when(spy.method())` is correct"    | Calls real method first! Use `doReturn().when(spy).method()` instead                     |
| "Spies are always better than mocks" | Spies are better when you WANT real logic; mocks are better for external dependencies    |

### 🚨 Failure Modes & Diagnosis

**1. Real Method Called During Spy Setup (NPE in `when()`)**

Cause: `when(spy.riskyMethod()).thenReturn(x)` — `riskyMethod()` is called for real during setup, throws NPE.
Fix: Always use `doReturn(x).when(spy).riskyMethod()` with spies.

**2. Spy Causes Real Side Effects in Tests (Database Written, Email Sent)**

Cause: A method that wasn't stubbed executed its real implementation.
Fix: Identify all methods with side effects and stub them with `doNothing()` or `doReturn()`. Or: use a Fake instead of a Spy.

### 🔗 Related Keywords

- **Prerequisites:** Mocking, Stubbing
- **Related:** Partial Mock, Test Doubles, Mockito, Interceptor, Proxy Pattern

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Wraps real object; records calls;        │
│              │ allows selective stubbing                │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Use doReturn().when() NOT when().then()  │
├──────────────┼───────────────────────────────────────────┤
│ CREATION     │ spy(new RealObject()) or @Spy            │
├──────────────┼───────────────────────────────────────────┤
│ WHEN TO USE  │ Partial override; verify internal calls; │
│              │ legacy code that can't be restructured   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Real code + wiretap + selective override"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The use of `@Spy @InjectMocks` in Mockito is considered a "test smell" by many practitioners. The scenario: you have a `UserService` with a `sendWelcomeEmail()` method that you want to stub in tests of the same `UserService`. To do this, you create a spy on `UserService` itself. Describe why this is a design smell (the service is doing too many things — user management AND email sending), what the correct refactoring is (extract `EmailService` as a separate dependency), and how after refactoring, you'd use a plain `@Mock EmailService` instead of a `@Spy UserService`.

**Q2.** Argument captors and spies are both observation tools. Compare: `ArgumentCaptor<Order> captor = ArgumentCaptor.forClass(Order.class); verify(orderRepo).save(captor.capture()); assertThat(captor.getValue().getStatus()).isEqualTo(CONFIRMED)` vs using a `FakeOrderRepository` that stores the saved order and allows direct inspection. For what test scenarios is ArgumentCaptor better? For what scenarios is the Fake approach better? Include: readability, test fragility, and what each approach fails to verify.
