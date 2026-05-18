---
id: DPT-038
title: Service Locator
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-006
used_by: DPT-039, DPT-064
related: DPT-039, DPT-006, DPT-027
tags:
  - pattern
  - creational
  - intermediate
  - service-lookup
  - dependency-management
  - anti-pattern
  - jndi
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/design-patterns/service-locator/
---

⚡ TL;DR - Service Locator is a registry that allows
components to look up their dependencies by name or type,
centralizing service discovery - but it is generally
considered an anti-pattern in modern DI-based systems
because it hides dependencies and makes code hard to test.

| #38 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-006 | |
| **Used by:** | DPT-039, DPT-064 | |
| **Related:** | DPT-039, DPT-006, DPT-027 | |

---

### 🔥 The Problem This Solves

**HISTORICAL CONTEXT:**
Before Dependency Injection frameworks (pre-Spring era,
early 2000s), Java enterprise code (J2EE) lacked a
standard way to provide objects with their dependencies.
The alternatives were:
1. Static factories (hard-coded dependencies)
2. Passing dependencies through every constructor
   (constructor chaining)
3. Using JNDI to look up resources (EJB, datasources)

**THE PROBLEM:**
```java
// Without any registry: hard-coded, untestable
class OrderService {
    private final EmailService email =
        new EmailService("smtp.example.com", 25); // hard-coded
    private final DataSource db =
        DriverManager.getConnection("jdbc:...", "user", "pass");
        // hard-coded
}
```
Hard-coded dependencies: untestable, not configurable.

**THE INVENTION MOMENT:**
Service Locator: a central registry holds named services.
Objects that need a service call `ServiceLocator.get("emailService")`.
The registry returns the correct implementation. The
registry can be configured with test implementations
during testing - without changing the calling code.

**WHY IT IS CONSIDERED AN ANTI-PATTERN TODAY:**
Dependency Injection (DI) is a superior alternative:
the container pushes dependencies into the object
(constructor injection) rather than the object pulling
them from a registry. DI makes dependencies explicit
(visible in the constructor signature), testable (just
pass a mock), and analyzable (tools can verify the
dependency graph at startup). Service Locator hides
dependencies inside the method body - they are invisible
to callers.

**WHERE IT IS STILL USED:**
JNDI in Java EE (DataSource lookup). Spring's `ApplicationContext`
used as a Service Locator (Spring discourages this).
Plugin architectures (Eclipse, IntelliJ plugin system).
OSGi Service Registry. `java.util.ServiceLoader` (Java SPI).

---

### 📘 Textbook Definition

The **Service Locator** pattern is a design pattern that
provides a central registry (the Locator) where services
(objects, implementations of interfaces) can be registered
and retrieved by name or type. When an object needs a
dependency, it calls `ServiceLocator.getService(key)`
rather than receiving the dependency via injection or
creating it directly. The Locator encapsulates the logic
of locating the service (JNDI lookup, instantiation,
caching). The pattern centralizes service discovery but
hides dependencies from the object's public contract.
It is considered an anti-pattern in most modern DI-based
frameworks and is superseded by Dependency Injection.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Service Locator is a global phone book: objects call
the phone book to find their dependencies rather than
having dependencies handed to them.

**One analogy:**
> Service Locator is asking for directions at an information
> desk. When you need something (a dependency), you go
> to the information desk (Service Locator) and ask:
> "Where can I find the email service?" The desk looks
> it up in the registry and points you to it.
> Dependency Injection is having someone give you a map
> (all dependencies) when you check in - you never need
> to visit the desk.

**One insight:**
The fundamental difference between Service Locator and
Dependency Injection: Service Locator is PULL - the
dependent object requests its dependency. DI is PUSH -
the dependency is given to the object from outside.
PUSH makes dependencies visible and testable; PULL hides them.

---

### 🔩 First Principles Explanation

**CORE MECHANISM:**
```java
class ServiceLocator {
    private static final Map<String,
        Object> registry = new HashMap<>();

    static void register(String name, Object service) {
        registry.put(name, service);
    }

    @SuppressWarnings("unchecked")
    static <T> T get(String name, Class<T> type) {
        return type.cast(registry.get(name));
    }
}
```

**JNDI - THE J2EE SERVICE LOCATOR:**
`javax.naming.InitialContext.lookup("java:comp/env/jdbc/MyDB")` is
Service Locator. JNDI is the J2EE standard registry for:
DataSources, JMS ConnectionFactories, EJB references,
environment properties. The container registers objects
under JNDI names; components look them up.

**JAVA SPI (`java.util.ServiceLoader`) - A MODERN SERVICE LOCATOR:**
```java
ServiceLoader<PaymentProvider> loader =
    ServiceLoader.load(PaymentProvider.class);
for (PaymentProvider provider : loader) {
    // Use provider
}
```
Third-party JARs declare implementations in
`META-INF/services/com.example.PaymentProvider`.
`ServiceLoader` discovers and instantiates them. This
is Service Locator for plugin/extension points.

**TRADE-OFFS:**

**Gain:** Centralized service registry. Swappable
implementations (test vs prod). Plugin extensibility
without modifying host code. Legacy code that cannot
use DI can use Service Locator.

**Cost:** Hidden dependencies (constructor does not
reveal dependencies; callers cannot know without reading
code). Hard to test (must configure the Locator before
testing each class). Global state (static registry =
test pollution; one test's registration affects the next).
Magic: incorrect lookups fail at runtime, not at startup.

---

### 🧪 Thought Experiment

**SETUP:**
`OrderService` needs `EmailService` and `InventoryService`.

**Service Locator approach:**
```java
class OrderService {
    void placeOrder(Order o) {
        EmailService email =
            ServiceLocator.get("emailService", EmailService.class);
        InventoryService inv =
            ServiceLocator.get("inventoryService",
                InventoryService.class);
        // ...
    }
}
```
Test: must configure ServiceLocator with mocks BEFORE
testing. Forgot to register? Runtime exception in test.
Debugging: which service is used? Must read the method body.
New dev: cannot know what `OrderService` needs by looking
at its constructor.

**DI approach:**
```java
class OrderService {
    OrderService(EmailService email, InventoryService inv) {
        // Dependencies: explicit, visible, verifiable
    }
}
// Test: just pass mocks to constructor. No registry needed.
```

---

### 🧠 Mental Model / Analogy

> Service Locator vs DI is SELF-SERVICE vs TABLE SERVICE.
> Self-service (Service Locator): you walk to the counter
> and get what you need from the registry. No one sees
> what you took; your plate's contents are invisible
> until you sit down. Table service (DI): the waiter
> brings everything to your table. Everyone can see
> exactly what was ordered. If something is wrong: the
> waiter knows immediately (startup validation).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Service Locator is a global "store" where software
components can get the objects they need. Instead of
being given what they need (DI), they go fetch it
themselves. Modern developers generally avoid this and
prefer DI.

**Level 2 - How to use it (junior developer):**
In legacy code: Service Locator calls appear as static
method calls to get an object: `ServiceLocator.getBean("emailService")`.
In modern Spring code: `@Autowired` (DI) is always
preferred over `context.getBean()` (Service Locator).
If you see `applicationContext.getBean(...)` in a Spring
service: that's Service Locator anti-pattern. The exception:
framework-level code that dynamically chooses a service
at runtime.

**Level 3 - How it works (mid-level engineer):**
Spring's `ApplicationContext.getBean()` IS Service Locator.
JNDI (`InitialContext.lookup()`) IS Service Locator.
`ServiceLoader.load(SomeService.class)` IS Service Locator
(plugin discovery pattern). Java 9 module system's
`ServiceLoader` is used heavily in JDK itself:
`java.nio.file.spi.FileSystemProvider`, `java.net.spi.URLStreamHandlerProvider`
are all discovered via `ServiceLoader`. The JDK uses
Service Locator internally for plugin/SPI extension points.

**Level 4 - Why it is generally an anti-pattern (senior/staff):**
The core issue is the violation of explicit dependencies.
When a class has dependencies injected via its constructor,
the constructor is a contract: "to use this class, provide
these dependencies." IDE tools (IntelliJ, Eclipse) can
analyze the dependency graph. Spring Boot validates
the entire bean graph at startup. If a dependency is
missing: fail fast at startup. Service Locator pushes
the failure to runtime (when the lookup is called).
More critically: hidden dependencies make classes hard
to reason about. A class with 10 Service Locator calls
in its body has 10 hidden dependencies that only appear
when you read every line of every method. A class with
10 constructor parameters has 10 explicit dependencies
visible at the class API boundary.

**Level 5 - Mastery (distinguished engineer):**
Service Locator is correct in exactly one scenario:
when you do NOT know the dependency type at compile time.
`ServiceLoader` for plugin architectures: the main application
does not know what payment providers a customer will
install. It discovers them at runtime via `ServiceLoader`.
This is legitimate Service Locator: the alternative
(DI) requires knowing all implementations at compile
time to inject them. Similarly, Spring's own internal
`BeanFactory` uses Service Locator-style lookup when
creating beans for generic types like `List<Validator>`
(Spring collects all `Validator` implementations and
injects the list). The key distinction: Service Locator
is an implementation detail of the framework/container;
application code should use DI. When application code
calls `context.getBean()`: that's the anti-pattern.
When the DI framework itself uses a registry to resolve
dependencies: that's the pattern being used correctly.

---

### ⚙️ How It Works (Mechanism)

```
Service Locator vs Dependency Injection
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ SERVICE LOCATOR (pull):                                 │
│   OrderService.placeOrder() {                           │
│       EmailService = Locator.get("email")  ← hidden     │
│       InvService   = Locator.get("inv")    ← hidden     │
│   }                                                     │
│   Dependencies: INVISIBLE to caller of placeOrder()     │
│   Test: must configure Locator with mocks first         │
│                                                         │
│ DEPENDENCY INJECTION (push):                            │
│   OrderService(EmailService email, InvService inv) {    │
│       this.email = email;     ← explicit                │
│       this.inv   = inv;       ← explicit                │
│   }                                                     │
│   Dependencies: VISIBLE in constructor signature        │
│   Test: pass mocks directly, no registry setup          │
│                                                         │
│ LEGITIMATE USE: runtime plugin discovery                │
│   ServiceLoader<Plugin> plugins =                       │
│     ServiceLoader.load(Plugin.class);                   │
│   // Discovers all Plugin implementations in classpath  │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
JNDI Service Locator in Java EE (historical context):

container startup:
  JNDI registry.bind("java:comp/env/jdbc/MyDB", dataSource)
  JNDI registry.bind("java:comp/env/mail/Session",
    mailSession)

OrderService.placeOrder():
  DataSource ds = (DataSource)
      new InitialContext().lookup("java:comp/env/jdbc/MyDB"
  MailSession ms = (MailSession)
      new InitialContext().lookup("java:comp/env/mail/Sessi

Modern equivalent (preferred):
  @Service
  class OrderService {
      @Autowired DataSource ds;         // injected
      @Autowired JavaMailSender mailer; // injected
  }
  // Spring resolves and injects at startup; fails fast if
    missing
```

---

### 💻 Code Example

**Example 1 - Service Locator (anti-pattern in application code):**

```java
// BAD: Service Locator in application code
// Dependencies are hidden; hard to test; global state

class ServiceLocator {
    private static final Map<String,
        Object> registry = new HashMap<>();

    static void register(String key, Object service) {
        registry.put(key, service);
    }

    @SuppressWarnings("unchecked")
    static <T> T get(String key, Class<T> type) {
        Object service = registry.get(key);
        if (service == null)
            throw new ServiceNotFoundException("No service: " + key);
        return type.cast(service);
    }
}

// Anti-pattern: application service uses Service Locator
class OrderService {
    void placeOrder(Order order) {
        // Hidden dependencies: caller cannot see these
        EmailService email =
            ServiceLocator.get("emailService", EmailService.class);
        InventoryService inv =
            ServiceLocator.get("inventoryService",
                InventoryService.class);

        orderRepo.save(order);
        inv.reduceStock(order.items());
        email.sendConfirmation(order);
    }
    // Constructor tells nothing: dependencies are hidden
}
```

**Example 2 - Dependency Injection (preferred):**

```java
// GOOD: DI - explicit, testable, visible

@Service
class OrderService {
    private final OrderRepository orderRepo;
    private final EmailService email;
    private final InventoryService inventory;

    // Constructor: explicit dependency declaration
    OrderService(OrderRepository orderRepo,
                 EmailService email,
                 InventoryService inventory) {
        this.orderRepo  = orderRepo;
        this.email      = email;
        this.inventory  = inventory;
    }

    void placeOrder(Order order) {
        orderRepo.save(order);
        inventory.reduceStock(order.items());
        email.sendConfirmation(order);
    }
}

// Test: dependencies are explicit, pass mocks
@Test
void testPlaceOrder() {
    EmailService mockEmail = mock(EmailService.class);
    InventoryService mockInv = mock(InventoryService.class);
    OrderRepository mockRepo = mock(OrderRepository.class);

    OrderService service = new OrderService(mockRepo, mockEmail,
        mockInv);
    service.placeOrder(testOrder);

    verify(mockInv).reduceStock(testOrder.items());
    verify(mockEmail).sendConfirmation(testOrder);
}
```

**Example 3 - Legitimate ServiceLoader usage (plugin discovery):**

```java
// LEGITIMATE: ServiceLoader for plugin architecture

// define service interface in core module
public interface ReportExporter {
    String format(); // "PDF", "EXCEL", "CSV"
    byte[] export(ReportData data);
}

// Third-party plugin: creates JAR with META-INF/services file
// META-INF/services/com.example.ReportExporter:
// com.acme.PdfExporter

// Main application: discovers all plugins at runtime
class ReportExportService {
    private final Map<String, ReportExporter> exporters;

    ReportExportService() {
        exporters = new HashMap<>();
        ServiceLoader<ReportExporter> loader =
            ServiceLoader.load(ReportExporter.class);
        for (ReportExporter exporter : loader) {
            exporters.put(exporter.format(), exporter);
        }
        // Discovers all JAR-provided implementations automatically
    }

    byte[] export(String format, ReportData data) {
        ReportExporter exporter = exporters.get(format.toUpperCase());
        if (exporter == null)
            throw new UnsupportedFormatException(format);
        return exporter.export(data);
    }
}
// Plugin discovery: CORRECT use of Service Locator
// The main app cannot know plugin implementations at compile time
```

**Example 4 - Spring anti-pattern vs correct usage:**

```java
// BAD: using Spring ApplicationContext as Service Locator
@Service
class BadOrderService {
    @Autowired
    private ApplicationContext context; // Service Locator

    void placeOrder(Order order) {
        // Service Locator call: hidden dependency, hard to test
        EmailService email = context.getBean(EmailService.class);
        email.sendConfirmation(order);
    }
}

// GOOD: inject the dependency directly
@Service
class GoodOrderService {
    @Autowired
    private EmailService email; // explicit dependency

    void placeOrder(Order order) {
        email.sendConfirmation(order);
    }
}
// Exception: using ApplicationContext is acceptable
// in @Configuration classes for conditional bean creation
// and in framework-level code only
```

---

### ⚖️ Comparison Table

| Aspect | Service Locator | Dependency Injection |
|---|---|---|
| Dependency visibility | Hidden (inside method body) | Explicit (constructor signature) |
| Testability | Requires registry setup | Pass mocks directly |
| Fail-fast behavior | Runtime (when lookup fails) | Startup (missing bean detected) |
| Global state | Yes (static registry) | No |
| Runtime discovery | Yes (can look up any registered type) | Compile-time known |
| Correct use case | Plugin discovery, SPI, legacy | Application code, everywhere |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| JNDI lookup is just Service Locator boilerplate, avoid it | In Java EE / Jakarta EE environments, JNDI is the official mechanism for DataSource, JMS, and resource lookup. Spring wraps JNDI lookups in `@Bean` factory methods - the JNDI is still happening, just hidden inside Spring's infrastructure code |
| Using ApplicationContext.getBean() is acceptable in Spring | Using `context.getBean()` in application code is the Service Locator anti-pattern in Spring. The exception: `ApplicationContextAware` in a framework utility class that dynamically resolves types, or in code that genuinely cannot know the type at compile time |
| Service Locator is a legacy pattern with no modern use | Java's ServiceLoader is heavily used in the JDK itself (JDBC drivers, `java.nio.file.spi`, `java.util.logging.Handler`). Spring uses `ServiceLoader` to discover `AutoConfiguration` classes. The pattern is alive; the issue is using it in application code instead of framework/SPI code |
| Service Locator and Dependency Injection are interchangeable | They solve the same problem (providing dependencies) but in fundamentally different ways. Service Locator: the class controls when/how it gets dependencies (pull). DI: the framework controls dependency injection at construction time (push). The difference matters for testability and clarity |

---

### 🚨 Failure Modes & Diagnosis

**Runtime ClassCastException on Service Lookup**

**Symptom:**
`ClassCastException: SomeImpl cannot be cast to SomeService`
at runtime during a lookup operation.

**Root Cause:**
The service was registered under a different type or
the wrong class was registered. The Service Locator's
registry accepts `Object` - no compile-time type checking.

**Diagnosis:**
```java
// Debug: inspect the registry
Object rawService = ServiceLocator.get("emailService");
System.out.println("Actual type: " + rawService.getClass().getName());
// Compare with expected type
```

**Fix:**
Use typed keys (generic registry) or use DI (which provides
compile-time type safety):
```java
// Typed registry: prevents ClassCastException
Map<Class<?>, Object> typedRegistry = new HashMap<>();
<T> void register(Class<T> type, T impl) {
    typedRegistry.put(type, impl);
}
<T> T get(Class<T> type) {
    return type.cast(typedRegistry.get(type));
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Singleton` - DPT-006; the Service Locator registry
  is typically a Singleton (global, shared state)

**Builds On This (learn these next):**
- `Dependency Injection Pattern` - DPT-039; DI is the
  superior alternative to Service Locator for application
  code - understand both to know when each applies

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Global registry: components look up     │
│              │ dependencies by name/type (pull model)  │
├──────────────┼──────────────────────────────────────────┤
│ VS DI        │ Service Locator: PULL (hidden deps).    │
│              │ DI: PUSH (explicit deps in constructor) │
├──────────────┼──────────────────────────────────────────┤
│ AVOID IN     │ Application code: use @Autowired (DI)   │
│              │ Not: context.getBean() in @Service       │
├──────────────┼──────────────────────────────────────────┤
│ CORRECT USE  │ Plugin discovery (ServiceLoader),        │
│              │ JNDI in Jakarta EE, SPI extension points │
├──────────────┼──────────────────────────────────────────┤
│ JAVA API     │ java.util.ServiceLoader,                 │
│              │ javax.naming.InitialContext (JNDI)       │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Dependency Injection → Specification Pat.│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Service Locator is a PULL model: objects fetch their
   dependencies. DI is PUSH: dependencies are given to
   objects. PULL hides dependencies; PUSH makes them
   explicit. Explicit > hidden for testability and
   maintainability.
2. In Spring: NEVER use `applicationContext.getBean()`
   in application service code. That is the Service Locator
   anti-pattern. Use `@Autowired` (DI) instead. Exception:
   framework-level code that cannot know the type at compile time.
3. `java.util.ServiceLoader` IS Service Locator used correctly:
   plugin/SPI architectures where the main application
   cannot know all implementations at compile time.
   Java's JDBC driver loading (`Class.forName(...)` in older
   code, or automatic via `ServiceLoader` in Java 6+) is
   a canonical example.

