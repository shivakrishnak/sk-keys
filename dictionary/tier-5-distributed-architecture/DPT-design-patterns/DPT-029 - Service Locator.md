---
layout: default
title: "Service Locator"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /design-patterns/service-locator/
id: DPT-054
category: Design Patterns
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - antipattern
status: complete
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-054 - Service Locator

⚡ TL;DR - Service Locator is a central registry that provides a global access point to look up services by name or type - widely considered an anti-pattern compared to Dependency Injection.

| DPT-054 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Dependency Injection Pattern, Interface, IoC | |
| **Used by:** | Legacy Systems, Plugin Frameworks, OSGi, JavaEE JNDI Lookup | |
| **Related:** | Dependency Injection Pattern, Factory Method, Registry Pattern, IoC Container | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT OR DI:**
A `CheckoutService` needs a `PaymentGateway`, a `TaxCalculator`, and an `InventoryService`. Without any dependency management, the constructor does `new PaymentGateway()`, `new TaxCalculator()`, `new InventoryService()`. Testing is impossible without running the real payment gateway. Swapping implementations requires modifying the constructor. Configuration (database URLs, API keys) leaks into business logic classes.

**THE BREAKING POINT:**
Direct instantiation couples the class to its concrete dependencies. Unit tests must use real infrastructure. Configuration changes require code changes. Alternative implementations require code changes.

**THE INVENTION MOMENT:**
This is why the Service Locator pattern was created. A central `ServiceLocator` registry holds service instances. Classes request what they need: `ServiceLocator.get(PaymentGateway.class)`. The registry decides which concrete implementation to provide. This was the dominant dependency management pattern before Dependency Injection frameworks became mainstream.

**EVOLUTION:**
Service Locator was the dominant dependency management pattern
before IoC containers matured (circa 1998-2004). Rod Johnson's
"Expert One-on-One J2EE Design and Development" (2002) and
Martin Fowler's "Inversion of Control Containers and the
Dependency Injection Pattern" (2004) systematically argued that
DI was superior to Service Locator for testability and explicit
dependencies. Spring popularised constructor injection (2003-2005),
effectively retiring Service Locator as a primary pattern. It
survives in OSGi container contexts and legacy code bases where
refactoring to DI is impractical.

---

### 📘 Textbook Definition

The **Service Locator** pattern provides a centralised registry (the **locator**) that holds references to service instances. Clients request services by a key (class, string name, or type) and receive the appropriate implementation. The Service Locator abstracts the creation and location of service implementations from client code. In Java EE, JNDI lookup is Service Locator. In OSGi, the Service Registry is Service Locator. In modern applications, Dependency Injection frameworks have largely superseded Service Locator, which is now often considered an anti-pattern due to hidden dependencies and testability issues.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A global directory where you look up services by type - the opposite of having services handed to you.

**One analogy:**
> A hotel concierge book. When you need something - a taxi, a restaurant recommendation, a dry cleaner - you call the concierge (Service Locator), who looks up the right provider. You don't know the provider's phone number; you ask the concierge. The concierge knows everything and provides the right contact.

**One insight:**
Service Locator solves "who creates my dependencies?" by asking "how do I find them at runtime?" Dependency Injection solves the same problem differently: "someone gives them to me upfront." The key difference: with DI, dependencies are declared and visible. With Service Locator, dependencies are hidden inside method bodies - callers can't tell what a class needs just by looking at its constructor.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A class needs services it should not instantiate directly.
2. The specific service implementation should be configurable.
3. Services must be accessible from anywhere in the application.

**DERIVED DESIGN:**
Given invariants 1+2+3: a static (or singleton) registry maps service types to instances. A one-time setup step registers implementations: `registry.register(PaymentGateway.class, new StripeGateway())`. At runtime, any class calls `registry.get(PaymentGateway.class)` to receive the implementation. No constructor injection needed.

The pattern technically decouples concrete types. However, the dependency on the locator itself replaces the dependency on concrete services. Worse: the locator dependency is implicit - nothing in the method signature declares it.

**THE TRADE-OFFS:**
**Gain:** Centralised service management; no dependency on concrete classes; configurable implementations; accessible from anywhere (including code where injection is difficult - Servlets in pre-CDI JavaEE).
**Cost:** Hidden dependencies - class signature doesn't declare what it needs; testability is harder (must configure the locator before every test); tight coupling to the locator itself; global state issues (locator configuration bleeds between tests); violates explicit interface principle.

---

### 🧪 Thought Experiment

**SETUP:**
`CheckoutService.processCheckout()` needs `PaymentGateway` for tests.

**WITH SERVICE LOCATOR:**
```java
public class CheckoutService {
    public void processCheckout(Cart cart) {
        PaymentGateway pg = ServiceLocator.get(PaymentGateway.class);
        pg.charge(cart.total());
    }
}
// Test: MUST set up locator globally before the test
ServiceLocator.register(PaymentGateway.class, mockGateway);
new CheckoutService().processCheckout(cart);
// Danger: if forget to reset, other tests use same mock
```

**WITH DEPENDENCY INJECTION:**
```java
public class CheckoutService {
    private final PaymentGateway paymentGateway;
    public CheckoutService(PaymentGateway pg) {
        this.paymentGateway = pg;
    }
    public void processCheckout(Cart cart) {
        paymentGateway.charge(cart.total());
    }
}
// Test: just pass the mock
new CheckoutService(mockGateway).processCheckout(cart);
// Clean, isolated, no global state
```

**THE INSIGHT:**
With Service Locator, the class's dependencies are invisible from the outside - you must read the method body. With DI, a class constructor declares exactly what it needs. DI's explicitness is not just style; it's a correctness guarantee enforced by the compiler.

---

### 🧠 Mental Model / Analogy

> Service Locator is like a Yellow Pages phone book. To get a service, you look it up (ServiceLocator.get(X)). The phone book (Locator) is global - everyone uses the same one. You can't tell what phone numbers someone needs just by looking at them; you must wait and see what they look up. Dependency Injection is like pre-loaded contacts: someone puts the numbers you need directly in your phone upfront - you never look anything up; your contacts list IS your explicit dependency declaration.

- "Yellow Pages" → Service Locator registry
- "Looking up a plumber" → `ServiceLocator.get(PlumbingService.class)`
- "Can't tell what someone needs without watching them" → hidden dependencies
- "Pre-loaded contacts" → constructor injection makes dependencies explicit
- "Different phone book in different cities" → locator can be configured per environment

Where this analogy breaks down: the Yellow Pages is a known reference pattern - everyone understands you use it. Service Locator makes dependencies implicit in a way that modern practice considers bad architecture. The analogy captures the mechanism but not the design smell.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Service Locator is a "lookup book" for software services. Instead of knowing where everything is, your code looks up what it needs in a central directory. The directory gives you the right service for the job.

**Level 2 - How to use it (junior developer):**
Implement a `ServiceLocator` singleton (or static class) with a `Map<Class<?>, Object> registry`. Register services at startup: `locator.register(PaymentGateway.class, new StripePaymentGateway())`. Use from code: `PaymentGateway gateway = locator.get(PaymentGateway.class)`. In Java EE: `InitialContext ctx = new InitialContext(); DataSource ds = (DataSource) ctx.lookup("java:comp/env/jdbc/mydb")` - JNDI is Service Locator.

**Level 3 - How it works (mid-level engineer):**
Modern Spring applications rarely use Service Locator explicitly, but Spring's `ApplicationContext.getBean(Class<T>)` IS Service Locator when called outside of normal DI injection. This is sometimes unavoidable (dynamic plugin loading, code that runs before Spring context is available). The `ServiceLocatorFactoryBean` in Spring explicitly generates type-safe Service Locator interfaces from an interface definition - bridging Service Locator with Spring's DI container to provide some explosion safety while maintaining locator semantics. In OSGi, the bundle service registry is a formal Service Locator with dynamic registration and unregistration of services at runtime - this is a legitimate use case where DI cannot work (plugins are loaded/unloaded dynamically).

**Level 4 - Why it was designed this way (senior/staff):**
Service Locator was the state of the art in 2001–2004 (JavaEE era), before Spring (2003) popularised constructor injection. JNDI (a Service Locator) was the only portable way to get JTA transactions, DataSources, and EJBs in J2EE. Martin Fowler's seminal 2004 paper "Inversion of Control Containers and the Dependency Injection pattern" explicitly compared the two patterns and argued DI's advantage: it makes dependencies visible at compile time. Mark Seemann's book "Dependency Injection in .NET" (2011) formally categorised Service Locator as an anti-pattern. The consensus is: Service Locator is a legitimate pattern for dynamic component systems (OSGi, plugins) where services are not known at compile time. For standard application components where all dependencies are known at build time, Dependency Injection is strictly preferable.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  SERVICE LOCATOR - LOOKUP FLOW                       │
│                                                      │
│  Setup (once at startup):                            │
│    ServiceLocator.register(                          │
│      PaymentGateway.class, new StripeGateway())      │
│    ServiceLocator.register(                          │
│      EmailService.class, new SmtpEmailService())     │
│                                                      │
│  Registry (internal map):                            │
│    PaymentGateway.class → StripeGateway instance     │
│    EmailService.class   → SmtpEmailService instance  │
│                                                      │
│  Usage (runtime):                                    │
│    PaymentGateway pg =                               │
│      ServiceLocator.get(PaymentGateway.class)        │
│         ↑ hidden dependency - not in constructor     │
└──────────────────────────────────────────────────────┘
```

**DI vs Service Locator:**
```
Service Locator:
  class X {
    void doWork() {
      ServiceA a = locator.get(ServiceA.class); // hidden
    }
  }

Dependency Injection:
  class X {
    X(ServiceA a) { ... }  // explicit in constructor!
    void doWork() { a.call(); }
  }
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SERVICE LOCATOR FLOW:**
```
Application startup:
  → ServiceLocator.register(PaymentGateway.class, stripe)
  → ServiceLocator.register(Logger.class, logback)

HTTP request arrives:
  → CheckoutService.processCheckout(cart)
  → ServiceLocator.get(PaymentGateway.class)
             ← YOU ARE HERE (service lookup)
  → returns StripeGateway
  → charge(cart.total())
  → returns result
```

**FAILURE PATH:**
```
ServiceLocator.get(PaymentGateway.class) returns null
  → NullPointerException at charge() call
  → because: service was never registered at startup
  → or: registration happened after the lookup
  → Hard to debug: error is at runtime, not compile time
```

**IN TESTS:**
```
Test 1: ServiceLocator.register(PG.class, mockPG)
Test 2: ServiceLocator.register(PG.class, realPG??)
→ If test setup is shared (static locator): tests interfere
→ Must reset locator between tests explicitly
```

---

### 💻 Code Example

**Example 1 - Basic Service Locator implementation:**
```java
// Simple service locator
public class ServiceLocator {
    private static final Map<Class<?>, Object> registry =
        new ConcurrentHashMap<>();

    // Suppress instantiation
    private ServiceLocator() {}

    public static <T> void register(Class<T> type, T impl) {
        registry.put(type, impl);
    }

    @SuppressWarnings("unchecked")
    public static <T> T get(Class<T> type) {
        T service = (T) registry.get(type);
        if (service == null) {
            throw new ServiceNotFoundException(
                "No service registered for: " + type.getName());
        }
        return service;
    }

    // For testing: reset between tests
    public static void reset() { registry.clear(); }
}

// Setup (once at startup)
ServiceLocator.register(
    PaymentGateway.class, new StripeGateway(apiKey));
ServiceLocator.register(
    EmailService.class, new SmtpEmailService(smtpHost));

// Usage (in business logic - hidden dependency!)
public class CheckoutService {
    public void checkout(Cart cart) {
        // Hidden: nobody knows PaymentGateway is needed here
        PaymentGateway pg =
            ServiceLocator.get(PaymentGateway.class);
        pg.charge(cart.total());
    }
}
```

**Example 2 - JNDI (JavaEE Service Locator):**
```java
// JavaEE / Jakarta EE JNDI lookup - classic Service Locator
public class OrderDAO {
    private DataSource getDataSource() {
        try {
            Context ctx = new InitialContext();
            // String-keyed lookup: typos compile but fail at runtime
            return (DataSource) ctx.lookup(
                "java:comp/env/jdbc/orderDb");
        } catch (NamingException e) {
            throw new RuntimeException("DataSource not found", e);
        }
    }
}
// DI alternative (Spring):
// @Autowired private DataSource dataSource; // explicit + type-safe
```

**Example 3 - When Service Locator is legitimate (OSGi):**
```java
// OSGi BundleContext: genuine Service Locator necessity
// (plugins registered/unregistered dynamically at runtime)
@Component
public class PluginProcessor {
    @Reference(cardinality = MULTIPLE, policy = DYNAMIC)
    private volatile List<DataPlugin> plugins;

    // OSGi ServiceTracker as Service Locator for dynamic lookup
    public void processAll(Data data) {
        plugins.forEach(p -> p.process(data));
    }
}
// Here, Service Locator is justified: plugin count and
// types are not known at compile-time
```

---

### ⚖️ Comparison Table

| Approach | Dependencies Visible | Testability | Global State | Best For |
|---|---|---|---|---|
| **Service Locator** | No (hidden in methods) | Harder (global setup) | Yes | Dynamic plugin systems, OSGi |
| Dependency Injection | Yes (constructor) | Easy (inject mocks) | No (per-object) | Standard application code |
| Direct instantiation | No (hardcoded) | Impossible | No | Simple, final implementations |
| Factory Method | Partially | Medium (factory mock) | No | Creation abstraction |

How to choose: use Dependency Injection for all standard application code. Use Service Locator only for genuinely dynamic component systems where services are registered and deregistered at runtime (OSGi, plugin frameworks). Avoid static Service Locator in applications fully managed by a DI container.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Service Locator and Dependency Injection solve different problems | They solve the same problem (dependency management) with different trade-offs. DI is generally preferable for testability and explicitness |
| Service Locator is always an anti-pattern | It is appropriate for dynamic component systems (OSGi) where plugins register/deregister at runtime. It's an anti-pattern for static application code |
| Spring's ApplicationContext.getBean() is not Service Locator | It IS Service Locator. Avoid `applicationContext.getBean()` in production code; use constructor injection |
| Service Locator makes code more modular | It hides dependencies, making code harder to understand and test. DI makes code more modular by declaring dependencies explicitly |
| Service Locator cannot be tested | It can - but you must set up the locator before every test and reset it after, creating test order dependencies |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing Service Registration - Runtime NullPointerException**

**Symptom:** `ServiceNotFoundException: No service registered for PaymentGateway` at runtime. Works in dev, fails on deploying new configuration.

**Root Cause:** Service registration is a runtime step - if the code path that registers a service is missed (wrong startup order, missing config), the locator returns null.

**Diagnostic:**
```bash
grep "ServiceLocator.register\|PaymentGateway" \
  src/ -rn --include="*.java"
# Verify registration happens before lookup
# Add startup health check:
ServiceLocator.get(PaymentGateway.class); // fails fast at startup
```

**Fix:** Add validation at startup: attempt to get all required services; fail fast if any are missing - don't wait until the first request.

**Prevention:** With DI, unregistered dependencies cause application startup failure. Service Locator doesn't. Add explicit startup validation to compensate.

---

**2. Test Interference - Shared Locator State**

**Symptom:** Tests pass individually but fail in batch. Test A's mock payment gateway affects Test B's assertion about the real gateway.

**Root Cause:** Static Service Locator holds shared state. Test A registers a mock; Test B uses the same locator and finds the mock.

**Diagnostic:**
```bash
./gradlew test --tests "TestB" # passes
./gradlew test # fails (TestA registered mock before TestB)
```

**Fix:**
```java
// Add to each test class:
@AfterEach
void cleanup() { ServiceLocator.reset(); }

// Better: migrate to DI entirely
// No global state = no test interference
```

**Prevention:** Migrate to constructor injection. No global state, no interference.

---

**3. Service Locator Dependency in Non-Spring Code Only**

**Symptom:** Part of the application is properly DI-managed; another part uses Service Locator for legacy reasons. The two halves interact incorrectly in integration tests.

**Root Cause:** Legacy code calls `ServiceLocator.get()` for a service that Spring manages via DI. The locator's registry and Spring's context contain different instances.

**Diagnostic:**
```bash
# Check if two different instances exist
grep "ServiceLocator.register\|@Bean" src/ -rn
# If both register the same type: two instances possible
```

**Fix:** Bridge the gap: register Spring beans into the Service Locator at startup using an `ApplicationRunner` that calls `ServiceLocator.register(type, springBean)`.

**Prevention:** Migrate legacy Service Locator code to DI incrementally - Spring supports mixing DI + `getBean()` during migration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Interface` - Service Locator returns interfaces, not concrete types; the interface is the contract between clients and implementations
- `IoC (Inversion of Control)` - Service Locator is one form of IoC; understanding IoC explains why Service Locator improves on direct instantiation
- `Singleton` - Service Locator is typically a singleton (or uses static methods); the singleton's global state is its primary weakness

**Builds On This (learn these next):**
- `Dependency Injection Pattern` - the modern, preferred alternative to Service Locator; makes dependencies explicit and testable
- `IoC Container (Spring, Guice)` - frameworks that automate DI; the alternative to manual Service Locator configuration
- `Registry Pattern` - Service Locator is a specialised Registry for service instances

**Alternatives / Comparisons:**
- `Dependency Injection Pattern` - explicit dependencies via constructor; preferred for testability and clarity
- `Factory Method` - creates objects on demand; Service Locator retrieves pre-created objects; both abstract instantiation
- `JNDI Lookup` - JavaEE's standard Service Locator; string-based keys make it error-prone (typos fail at runtime only)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Central registry for looking up service   │
│              │ instances by type - a global directory    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Classes need services without direct      │
│ SOLVES       │ instantiation; configurable implementations│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Hides dependencies - constructor doesn't  │
│              │ reveal what a class needs (DI does)       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Dynamic plugin systems (OSGi); early-boot │
│              │ code before DI container is available     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ In standard Spring/DI-managed code -      │
│              │ use constructor injection instead         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Flexibility vs hidden dependencies and    │
│              │ test interference from global state       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Go find what you need" vs                │
│              │ "Here's what you need." (DI wins)         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dependency Injection Pattern →            │
│              │ IoC Container → Spring Core               │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Centralise service registration and lookup in one registry.
This removes the creation knowledge from callers -- callers
ask for a service by name or type rather than calling `new`.

**Where else this pattern appears:**
- **JNDI (Java Naming and Directory Interface):** Application
  servers publish DataSources, EJBs, and JMS queues to JNDI;
  clients look them up by name string. JNDI is Service Locator
  at Java EE scale.
- **DNS:** DNS is a global Service Locator for network services --
  clients ask "where is service X?" by name; DNS returns the
  address. Service Locator's failure mode (hidden dependency) is
  also DNS's: remove a record, everything silently breaks.
- **OSGi service registry:** Components publish services to the
  OSGi service registry; consumers look them up dynamically --
  a type-safe Service Locator for modular Java applications.

---

### 💡 The Surprising Truth

Martin Fowler did not declare Service Locator an anti-pattern in
his 2004 article -- he said it was "less preferred" than DI. The
conflation of "less preferred" with "anti-pattern" led to its
wholesale removal from codebases that could have reasonably used
it. Service Locator remains the correct pattern in specific
contexts: plugin architectures where dependencies are not known
at compile time, OSGi bundles with dynamic service binding, and
test harnesses that need to replace services without DI framework
support. The pattern is a legitimate tool; its overuse as a
substitute for DI is the actual anti-pattern.
---

### 🧠 Think About This Before We Continue

**Q1.** A legacy application uses Service Locator extensively. A team wants to migrate to Spring DI incrementally (one class at a time). `LegacyOrderService` uses `ServiceLocator.get(PaymentGateway.class)` and is not yet migrated. `ModernPaymentGateway` is now managed by Spring as a `@Bean`. Describe the exact coexistence strategy: how do you ensure `LegacyOrderService` receives the Spring-managed `ModernPaymentGateway` from the locator, and what risk does this introduce during the transition period?

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** Both Service Locator and Dependency Injection are implementations of Inversion of Control. A developer argues: "Service Locator achieves better modularity because the class isn't coupled to the specific implementations - it just asks for what it needs." A second developer argues: "DI achieves better modularity for a different reason." Who is right in what sense? Identify the precise technical claim where each developer is correct, and identify the one testability metric where DI is objectively superior to Service Locator in all cases.



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** An OSGi-based plugin system uses
Service Locator: plugins register services on startup;
the host application looks them up by interface type. A new
requirement: multiple implementations of the same service
type must coexist (e.g., two `PaymentGateway` implementations).
Describe the Service Locator API changes needed to support
this and compare this with how Spring's `@Autowired List<T>`
handles the same scenario.

*Hint: The Comparison Table's Service Locator vs DI row is
the relevant starting point. Consider qualifier-based
selection vs. collection injection as the two models.*
