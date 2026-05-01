---
layout: default
title: "Service Locator Anti-Pattern"
parent: "Software Architecture Patterns"
nav_order: 764
permalink: /software-architecture/service-locator/
number: "764"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Dependency Injection Pattern, SOLID Principles, Inversion of Control"
used_by: "Anti-pattern identification, Code review, Legacy code analysis"
tags: #intermediate, #architecture, #anti-pattern, #coupling, #testing
---

# 764 — Service Locator Anti-Pattern

`#intermediate` `#architecture` `#anti-pattern` `#coupling` `#testing`

⚡ TL;DR — **Service Locator** provides a global registry where objects look up (pull) their dependencies — often considered an anti-pattern because it hides dependencies, makes classes hard to test in isolation, and couples code to the locator infrastructure rather than to explicit interfaces.

| #764 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Dependency Injection Pattern, SOLID Principles, Inversion of Control | |
| **Used by:** | Anti-pattern identification, Code review, Legacy code analysis | |

---

### 📘 Textbook Definition

**Service Locator** (Martin Fowler, "Inversion of Control Containers and the Dependency Injection Pattern," 2004): a design pattern (considered an anti-pattern by many modern practitioners) in which a centralized registry (the locator) provides access to services — objects call `ServiceLocator.get(ServiceType.class)` to obtain dependencies rather than having them injected. Fowler describes Service Locator as one form of IoC but prefers Dependency Injection: "The key difference is that with a Service Locator every user of a service has a dependency on the locator. The locator can hide dependencies to other implementations, but you do need to see the locator." Mark Seemann ("Dependency Injection in .NET") calls Service Locator an anti-pattern because: (1) it makes dependencies invisible, (2) it makes classes hard to unit-test, (3) it couples all code to the locator.

---

### 🟢 Simple Definition (Easy)

An office supply room vs. a delivery desk. Service Locator: when you need a stapler, you walk to the supply room and take one yourself. The supply room is always there (global). Anyone can walk in and take anything. DI: the supply room delivers what you need TO your desk. You declared what you needed in advance. Service Locator problem: any class, anywhere in the code, can silently take any dependency from the global room. You can't tell from outside a class what it's using — you have to look inside.

---

### 🔵 Simple Definition (Elaborated)

Without a DI container: `OrderService` uses `ServiceLocator.get(EmailService.class)` internally. What does `OrderService` depend on? You can't tell from its constructor or class signature. You have to read the entire class body to find all `ServiceLocator.get()` calls. In testing: `ServiceLocator` must be set up with mock implementations before every test — if you forget one: test fails with "service not found." With DI: `OrderService(EmailService email)` — dependencies visible immediately. Tests: just pass a mock. No locator setup.

---

### 🔩 First Principles Explanation

**Service Locator vs. Dependency Injection — the dependency visibility problem:**

```
SERVICE LOCATOR STRUCTURE:

  class ServiceLocator {
      private static Map<Class<?>, Object> registry = new HashMap<>();
      
      static <T> void register(Class<T> type, T impl) {
          registry.put(type, impl);
      }
      
      static <T> T get(Class<T> type) {
          T service = (T) registry.get(type);
          if (service == null) throw new ServiceNotFoundException(type);
          return service;
      }
  }
  
  // Usage — dependencies hidden INSIDE methods:
  class OrderService {
      void placeOrder(Order order) {
          // Dependencies not visible in class signature:
          EmailService email   = ServiceLocator.get(EmailService.class);
          PaymentGateway pay   = ServiceLocator.get(PaymentGateway.class);
          OrderRepository repo = ServiceLocator.get(OrderRepository.class);
          
          // ... use them
      }
  }
  
PROBLEMS:

  1. HIDDEN DEPENDENCIES (biggest problem):
  
     // From the outside, OrderService appears to have no dependencies:
     OrderService service = new OrderService();
     service.placeOrder(order);  // Works or FAILS AT RUNTIME if locator not set up
     
     // You cannot know what OrderService needs without reading its implementation.
     // Constructor injection shows dependencies explicitly:
     OrderService service = new OrderService(emailService, payment, repo);
     // Immediately visible: needs 3 things.
     
  2. DIFFICULT UNIT TESTING:
  
     // Test setup: must configure the GLOBAL locator:
     @BeforeEach
     void setup() {
         ServiceLocator.register(EmailService.class, new MockEmailService());
         ServiceLocator.register(PaymentGateway.class, new MockPaymentGateway());
         ServiceLocator.register(OrderRepository.class, new MockOrderRepository());
         // If any of these are missing: runtime exception, not compile error
     }
     
     @AfterEach
     void teardown() {
         ServiceLocator.clear();  // Must clean up global state between tests!
     }
     
     // Tests: ORDER-DEPENDENT if teardown fails. Global state contamination.
     
  3. GLOBAL STATE:
  
     ServiceLocator is a global singleton. All tests share it.
     Parallel test execution: race conditions on the shared locator.
     One test pollutes another's service registrations.
     
  4. RUNTIME FAILURES:
  
     // Missing registration discovered AT RUNTIME, not compile time:
     ServiceLocator.get(EmailService.class)  // ServiceNotFoundException at runtime
     
     // DI: missing dependency = application won't START (compile or startup error).
     // Service Locator: missing registration = fails on FIRST USE (could be in production).
     
  5. COUPLING TO LOCATOR:
  
     Every class that uses Service Locator is now COUPLED TO THE LOCATOR ITSELF.
     Change the locator mechanism: all classes must change.
     
     // Class is not reusable outside a Service Locator context.
     // Port to a different framework: must refactor every class.

WHEN SERVICE LOCATOR IS ACCEPTABLE (context matters):

  1. FRAMEWORK-LEVEL BOOTSTRAPPING:
     Spring's ApplicationContext.getBean() is used in main() to start the application.
     This is the "composition root" — the ONE place that orchestrates everything.
     Here, Service Locator is acceptable (it IS the composition root).
     
  2. LEGACY CODE / FRAMEWORK CONSTRAINTS:
     Static factory methods in frameworks sometimes must use Service Locator
     (e.g., JPA EntityListeners, deserializers that can't receive injected dependencies).
     Document it. Minimize scope.
     
  3. PLUGIN ARCHITECTURE (limited scope):
     A plugin registry where plugins look up core services by type.
     If the registry is explicitly typed and scoped to the plugin API, it's less problematic
     than a global God locator.
     
  FOWLER'S VERDICT: "With a Service Locator the application class asks for it explicitly
  by a message to the locator. With injection there is no explicit request, the service
  appears in the application class... The key difference is that with a Service Locator
  every user of a service has a dependency on the locator."

THE COMPOSITION ROOT PATTERN (the right use of Service Locator):

  // ONLY use Service Locator at the composition root (main / application start):
  
  class Application {
      public static void main(String[] args) {
          // Composition root: wire everything here:
          DataSource ds        = new HikariDataSource(config.dbUrl());
          OrderRepository repo = new JpaOrderRepository(ds);
          EmailService email   = new SmtpEmailService(config.smtpHost());
          PaymentGateway pay   = new StripeGateway(config.stripeKey());
          OrderService svc     = new OrderService(repo, email, pay);
          OrderController ctrl = new OrderController(svc);
          // Everything wired. No Service Locator inside any of these classes.
      }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Service Locator (pure DI):
- DI requires wiring the entire object graph at startup — verbose without a container

WITH Service Locator (the appeal):
→ "Call `ServiceLocator.get()` whenever you need anything — no wiring boilerplate"

The Problem: This convenience comes at the cost of invisible dependencies, untestable code, and global state coupling. DI containers (Spring) solve the boilerplate without the hidden-dependency problem.

---

### 🧠 Mental Model / Analogy

> An unlabeled pantry anyone can take from, vs. a restaurant that plates and delivers your order. Service Locator: any class can reach into the global pantry and take any ingredient. The chef (class) has no declared ingredient list — they rummage through the pantry internally. When the pantry is empty: the dish fails at cooking time. DI: the chef declares "I need eggs, flour, butter" (constructor). The kitchen prepares exactly these. Missing ingredient: the ORDER fails before cooking starts. You know what's needed before you start cooking.

"Anyone can reach into pantry" = Service Locator (global registry accessible anywhere)
"Chef has no declared ingredient list" = hidden dependencies
"Dish fails at cooking time" = runtime ServiceNotFoundException
"Chef declares ingredients upfront" = constructor injection (visible dependencies)
"Order fails before cooking" = startup failure if dependency is missing

---

### ⚙️ How It Works (Mechanism)

```
ANTI-PATTERN DETECTION:

  Signs of Service Locator in code:
  
  1. Classes with no-arg constructors that call ServiceLocator/Context.get() inside methods.
  
  2. Test setup that calls ServiceLocator.register(MockX.class) before each test.
  
  3. @Autowired ApplicationContext context in Spring — then context.getBean() inside methods.
     (Valid at composition root; anti-pattern everywhere else.)
  
  4. Static global maps or singletons that provide service lookups.
  
  REFACTORING TO DI:
  
  1. Find all ServiceLocator.get(X.class) calls in a class.
  2. Add X as a constructor parameter.
  3. Remove the ServiceLocator.get() calls; use the injected field.
  4. Update composition root (or DI container config) to provide X.
```

---

### 🔄 How It Connects (Mini-Map)

```
Object needs a dependency — options:
        │
        ├── Create it with new (worst: no swapping, hard to test)
        ├── Service Locator (pulls from global registry — hidden deps)
        └── Dependency Injection (pushed in — explicit, testable)
        
Service Locator Anti-Pattern ◄──── (you are here)
(global registry pattern — avoid in application code)
        │
        ├── Dependency Injection: the alternative (preferred approach)
        ├── Inversion of Control: Service Locator IS IoC but not the best form
        └── Composition Root: the one place where Service Locator usage is acceptable
```

---

### 💻 Code Example

```java
// SERVICE LOCATOR (anti-pattern):
class NotificationService {
    // Dependencies hidden inside the method body:
    void notify(UserId userId, String message) {
        EmailService email = ServiceLocator.get(EmailService.class);    // hidden dep #1
        SMSService sms     = ServiceLocator.get(SMSService.class);      // hidden dep #2
        UserPrefs prefs    = ServiceLocator.get(UserPrefsService.class) // hidden dep #3
                                           .getPrefs(userId);
        
        if (prefs.emailEnabled()) email.send(userId, message);
        if (prefs.smsEnabled())   sms.send(userId, message);
    }
}

// Test: must configure global ServiceLocator:
@BeforeEach void setup() {
    ServiceLocator.register(EmailService.class, mockEmail);
    ServiceLocator.register(SMSService.class, mockSms);
    ServiceLocator.register(UserPrefsService.class, mockPrefs);  // easy to forget!
}

// ────────────────────────────────────────────────────────────────────

// DEPENDENCY INJECTION (correct approach):
class NotificationService {
    private final EmailService email;
    private final SMSService sms;
    private final UserPrefsService prefs;
    
    // Dependencies declared EXPLICITLY — visible to all readers and tools:
    NotificationService(EmailService email, SMSService sms, UserPrefsService prefs) {
        this.email = email;
        this.sms   = sms;
        this.prefs = prefs;
    }
    
    void notify(UserId userId, String message) {
        UserPrefs p = prefs.getPrefs(userId);
        if (p.emailEnabled()) email.send(userId, message);
        if (p.smsEnabled())   sms.send(userId, message);
    }
}

// Test: just construct with mocks:
var service = new NotificationService(mockEmail, mockSms, mockPrefs);
// No global state. No ServiceLocator setup. Tests run in isolation.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Service Locator is not used in modern code | Service Locator appears in many modern codebases under different names: `ApplicationContext.getBean()` in Spring, `HttpContext.RequestServices.GetService()` in ASP.NET Core, static `Registry.get()` helpers. The anti-pattern is alive and common — recognizing it is important |
| Using Spring's ApplicationContext.getBean() is always an anti-pattern | Using `getBean()` in the composition root (main method, application initializer) is acceptable — that IS the wiring layer. Using `getBean()` inside application services or domain classes IS the anti-pattern. The distinction is LOCATION: composition root (OK) vs. application code (anti-pattern) |
| Service Locator is only a problem for unit tests | Invisible dependencies affect more than testing. They make code harder to understand (can't tell what a class needs without reading it). They make refactoring harder (can't safely change a service registration without knowing all its hidden consumers). They violate the principle of least surprise |

---

### 🔥 Pitfalls in Production

**Spring's ApplicationContext used as Service Locator in services:**

```java
// ANTI-PATTERN: ApplicationContext used as Service Locator inside a service:
@Service
class ReportOrchestrator {
    @Autowired
    private ApplicationContext ctx;  // Service Locator injected!
    
    void generate(ReportType type, ReportId id) {
        // Hidden dependency lookup inside the method:
        ReportGenerator gen = ctx.getBean(type.getGeneratorBeanName(), ReportGenerator.class);
        EmailService email  = ctx.getBean("emailService", EmailService.class);
        
        gen.generate(id);
        email.send(...);
    }
}
// Problem: what does ReportOrchestrator depend on? Can't tell from constructor.
// Test: must provide a real ApplicationContext or a mock that returns specific beans.

// FIX: Map-based DI (Spring injects all implementations):
@Service
class ReportOrchestrator {
    private final Map<ReportType, ReportGenerator> generators;
    private final EmailService email;
    
    // Spring collects all ReportGenerator beans into the map (keyed by qualifier/enum):
    ReportOrchestrator(Map<String, ReportGenerator> gens, EmailService email) {
        this.generators = gens.entrySet().stream()
            .collect(toMap(e -> ReportType.from(e.getKey()), Map.Entry::getValue));
        this.email = email;
    }
    
    void generate(ReportType type, ReportId id) {
        generators.get(type).generate(id);
        email.send(...);
    }
}
// Dependencies now explicit. Testable with map of mock generators + mock email.
```

---

### 🔗 Related Keywords

- `Dependency Injection` — the correct alternative to Service Locator
- `Inversion of Control` — broader principle; both Service Locator and DI are IoC implementations
- `Composition Root` — the ONE place where Service Locator usage is acceptable
- `Plugin Architecture` — sometimes uses a registry (similar to Service Locator, but scoped)
- `SOLID Principles` — Service Locator violates DIP (depends on locator, not abstraction) and SRP

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Classes PULL dependencies from a global   │
│              │ registry. Hidden deps, hard to test,      │
│              │ global state — prefer DI instead.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Composition root ONLY (wiring application)│
│              │ — never in application/domain code itself │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Any application service, domain class,    │
│              │ or library code — use constructor         │
│              │ injection instead                        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Unlabeled pantry everyone raids vs.      │
│              │  delivery to your desk with a receipt —  │
│              │  DI: you declare what you need upfront."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dependency Injection → IoC →              │
│              │ Composition Root → SOLID Principles       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team argues: "We use Spring's `ApplicationContext.getBean()` to dynamically look up plugins at runtime based on a user configuration. We can't use constructor injection because the plugin to use is only known at request time." Is this a valid use of the Service Locator pattern? How does this compare to the Plugin Architecture pattern which uses a typed registry? What makes this acceptable or not?

**Q2.** Spring's `@Lazy` annotation and `ObjectProvider<T>` are mechanisms where beans are looked up on-demand rather than injected eagerly. Are these forms of Service Locator? How does `ObjectProvider<T>` (injected at construction time) differ from `ApplicationContext.getBean()` (called anywhere)? When does "lazy injection" become Service Locator?
