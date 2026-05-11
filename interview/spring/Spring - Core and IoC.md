---
layout: default
title: "Spring - Core and IoC"
parent: "Spring"
grand_parent: "Interview Mastery"
nav_order: 1
permalink: /interview/spring/core-and-ioc/
topic: Spring
subtopic: Core and IoC
keywords:
  - IoC Container and Dependency Injection
  - ApplicationContext
  - Bean Lifecycle
  - Bean Scopes
  - Circular Dependencies
difficulty_range: ★☆☆ to ★★☆
status: in-progress
version: 2
---

# IoC Container and Dependency Injection

**TL;DR** - Inversion of Control means the framework creates and wires objects (beans) instead of your code creating them. Dependency Injection is the mechanism: Spring provides dependencies to objects rather than objects fetching their own dependencies.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every class creates its own dependencies: `new UserRepository(new DataSource(new ConnectionPool(...)))`. Changes cascade everywhere. Testing requires rewriting construction logic. Swapping implementations requires modifying every consumer.

**THE BREAKING POINT:**
Switching from MySQL to PostgreSQL requires changing 47 files that construct `MySqlDataSource`. Unit testing a service requires standing up a full database because the service directly instantiates the repository.

**THE INVENTION MOMENT:**
"This is exactly why IoC and Dependency Injection were created."

**EVOLUTION:**
Direct construction (new) -> Factory Pattern -> Service Locator -> Dependency Injection (Spring 2003) -> CDI (Java EE 6) -> Spring Boot auto-configuration.

---

### Textbook Definition

**Inversion of Control (IoC):** The principle where the framework controls object creation and lifecycle, inverting the traditional flow where application code controls everything.

**Dependency Injection (DI):** The pattern where dependencies are provided to an object from the outside (constructor, setter, or field) rather than created internally. The container resolves and injects all dependencies automatically.

---

### Understand It in 30 Seconds

**One line:**
You declare what you need; Spring figures out how to create and provide it.

**One analogy:**

> IoC is like ordering at a restaurant instead of cooking. You say "I want pasta" (declare dependency), the kitchen (container) prepares it, and the waiter (DI mechanism) brings it to you. You don't go to the kitchen to fetch ingredients.

**One insight:**
DI doesn't eliminate dependencies - it makes them explicit and externally configurable. The class still NEEDS a repository; it just doesn't know HOW it's created.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of building your own tools, you tell someone what tools you need and they hand them to you ready-made.

**Level 2 - How to use it (junior developer):**

```java
// BAD: Creating your own dependency
public class OrderService {
    private final OrderRepo repo =
        new JdbcOrderRepo(
            new HikariDataSource(...));
    // Tightly coupled. Untestable.
}

// GOOD: Dependencies injected
@Service
public class OrderService {
    private final OrderRepo repo;

    // Constructor injection (preferred)
    public OrderService(OrderRepo repo) {
        this.repo = repo;
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Spring's DI process:

1. Component scanning finds `@Component`/`@Service`/`@Repository` classes
2. BeanDefinition created for each
3. Container resolves dependency graph (topological sort)
4. Beans instantiated in dependency order
5. Dependencies injected via constructor/setter/field
6. Initialization callbacks invoked (`@PostConstruct`)

Three injection types:

```java
// 1. Constructor (PREFERRED - immutable, testable)
@Service
public class UserService {
    private final UserRepo repo;
    public UserService(UserRepo repo) {
        this.repo = repo;
    }
}

// 2. Setter (for optional dependencies)
@Autowired(required = false)
public void setCache(CacheManager cache) {
    this.cache = cache;
}

// 3. Field (avoid - untestable, hides deps)
@Autowired
private UserRepo repo; // hard to mock in tests
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Why constructor injection is superior:**

1. Dependencies are immutable (`final` fields)
2. Object is fully initialized after construction (no partially-constructed state)
3. Testable without Spring: just pass mocks to constructor
4. Makes dependency explosion visible (too many constructor args = class doing too much)
5. Prevents circular dependencies (fail-fast at startup)

**The container's resolution algorithm:**

- By type first (finds all beans of the required type)
- If ambiguous: by qualifier (`@Qualifier`), then by name
- If still ambiguous: `@Primary` wins, else startup fails


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Field injection (untestable):**

```java
@Service
public class PaymentService {
    @Autowired private PaymentGateway gateway;
    @Autowired private AuditLogger logger;

    // Can't instantiate without Spring
    // Can't inject mocks easily in tests
}
```

**GOOD - Constructor injection:**

```java
@Service
public class PaymentService {
    private final PaymentGateway gateway;
    private final AuditLogger logger;

    public PaymentService(
            PaymentGateway gateway,
            AuditLogger logger) {
        this.gateway = gateway;
        this.logger = logger;
    }
}

// Test: no Spring needed
@Test
void testPayment() {
    var service = new PaymentService(
        mockGateway, mockLogger);
    // test directly
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. IoC = framework controls object creation; DI = framework injects dependencies
2. Always use constructor injection (immutable, testable, explicit)
3. Spring resolves by type first, then qualifier, then name

**Interview one-liner:**
"IoC inverts who creates objects (framework, not you), DI is the mechanism (constructor injection preferred), making code loosely coupled, testable, and configurable without modification."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: What are the three types of dependency injection and which do you prefer?**

_Why they ask:_ Tests best-practice knowledge and reasoning.

_Strong answer:_

| Type        | Mechanism             | Pros                           | Cons                            |
| ----------- | --------------------- | ------------------------------ | ------------------------------- |
| Constructor | Constructor parameter | Immutable, testable, fail-fast | Verbose with many deps          |
| Setter      | Setter method         | Optional deps, reconfigurable  | Mutable, partially initialized  |
| Field       | @Autowired on field   | Concise                        | Untestable, hides deps, mutable |

**Constructor injection is always preferred because:**

- Fields can be `final` (thread-safe, immutable)
- Object is never in a partially-constructed state
- Can instantiate without Spring (easy testing)
- Too many parameters = class doing too much (design signal)
- Circular dependencies fail at startup (instead of runtime)

---

**Q2: How does Spring resolve ambiguous dependencies?**

_Why they ask:_ Tests understanding of bean resolution.

_Strong answer:_

When multiple beans match a dependency type:

```java
interface PaymentGateway {}

@Component class StripeGateway
    implements PaymentGateway {}
@Component class PayPalGateway
    implements PaymentGateway {}

// This fails at startup - ambiguous!
@Service
class PaymentService {
    PaymentService(PaymentGateway gw) {}
}
```

Resolution order:

1. `@Primary` annotation on one implementation
2. `@Qualifier("stripe")` on the injection point
3. Parameter name matching: `PaymentGateway stripeGateway` matches bean name
4. If still ambiguous: `NoUniqueBeanDefinitionException`

```java
// Fix 1: @Primary
@Primary @Component
class StripeGateway implements PaymentGateway {}

// Fix 2: @Qualifier
PaymentService(
    @Qualifier("stripe") PaymentGateway gw) {}

// Fix 3: Inject all
PaymentService(
    List<PaymentGateway> allGateways) {}
```

---

**Q3: What is the difference between BeanFactory and ApplicationContext?**

_Why they ask:_ Tests container hierarchy understanding.

_Strong answer:_

`BeanFactory` is the base interface: basic DI container (lazy bean creation, dependency resolution).

`ApplicationContext` extends BeanFactory adding:

- Event publication (`ApplicationEvent`)
- Internationalization (MessageSource)
- Resource loading (classpath, file, URL)
- AOP integration
- Bean lifecycle callbacks
- Automatic BeanPostProcessor registration
- Eager initialization (all singletons at startup)

In practice, you always use ApplicationContext. BeanFactory is an internal abstraction you never interact with directly. The split exists for modularity in the framework's design.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for IoC Container and Dependency Injection. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# ApplicationContext

**TL;DR** - ApplicationContext is the central interface of the Spring IoC container, responsible for instantiating, configuring, and managing all beans and providing application-level services like events, resources, and environment properties.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Without a central container, there's no single place that knows about all objects, their configurations, their lifecycle, and their relationships. Each component bootstraps itself, leading to scattered initialization and no unified way to configure the application.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ApplicationContext is Spring's "master registry" - it knows about every object in your application, how to create them, and how they connect to each other.

**Level 2 - How to use it (junior developer):**

```java
// Boot creates it automatically
@SpringBootApplication
public class App {
    public static void main(String[] args) {
        ApplicationContext ctx =
            SpringApplication.run(App.class, args);

        // Manual bean retrieval (rarely needed)
        UserService svc = ctx.getBean(
            UserService.class);
    }
}
```

**Level 3 - How it works (mid-level engineer):**

ApplicationContext startup sequence:

1. Create Environment (properties, profiles)
2. Component scan and BeanDefinition registration
3. Invoke BeanFactoryPostProcessors (modify definitions)
4. Instantiate singleton beans in dependency order
5. Invoke BeanPostProcessors (proxy creation, AOP)
6. Publish `ContextRefreshedEvent`
7. Application is ready

Common implementations:

- `AnnotationConfigApplicationContext` - Java config
- `GenericWebApplicationContext` - web apps
- `SpringApplication` (Boot) - auto-configured

**Level 4 - Mastery (senior/staff+ engineer):**

**BeanPostProcessor is where the magic happens:**

- `@Autowired` processing -> `AutowiredAnnotationBeanPostProcessor`
- `@Transactional` -> creates proxy via `AbstractAutoProxyCreator`
- `@Scheduled` -> `ScheduledAnnotationBeanPostProcessor`
- `@Async` -> proxy via `AsyncAnnotationBeanPostProcessor`

The context is hierarchical: child contexts can see parent beans but not vice versa. Used in Spring MVC (root context + servlet context).


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. ApplicationContext = Spring's IoC container holding all beans and services
2. Startup: scan -> definitions -> post-process definitions -> instantiate -> post-process beans
3. BeanPostProcessors create proxies for @Transactional, @Async, etc.

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: Explain the Spring Boot startup sequence.**

_Why they ask:_ Tests understanding of the bootstrap process.

_Strong answer:_

```
SpringApplication.run()
  |-> Create ApplicationContext
  |-> Load Environment (application.yml, env vars)
  |-> Apply SpringApplicationRunListeners
  |-> Component scan + auto-configuration
  |    |-> @EnableAutoConfiguration
  |    |-> META-INF/spring/org.springframework.
  |        boot.autoconfigure.AutoConfiguration
  |        .imports
  |    |-> Conditional evaluation (@ConditionalOn...)
  |-> BeanDefinition registration
  |-> BeanFactoryPostProcessors run
  |    |-> PropertySourcesPlaceholderConfigurer
  |    |-> ConfigurationClassPostProcessor
  |-> Singleton bean instantiation
  |-> BeanPostProcessors run (proxies, init)
  |-> ContextRefreshedEvent published
  |-> Embedded server starts (Tomcat/Netty)
  |-> ApplicationReadyEvent published
```

Key insight: Auto-configuration classes are just `@Configuration` classes that are conditionally enabled based on classpath, properties, and existing beans.

---

**Q2: What is the difference between @Component, @Service, @Repository, and @Controller?**

_Why they ask:_ Tests understanding of stereotype annotations.

_Strong answer:_

Functionally, `@Service`, `@Repository`, and `@Controller` are all `@Component` with no additional behavior difference (they're all detected by component scanning and create beans):

```java
@Component  // generic
@Service    // business logic layer
@Repository // data access layer
@Controller // web layer
```

Semantic differences (why they exist):

- **Code clarity:** Communicates the role of the class
- **AOP targeting:** You can apply aspects to `@Repository` only
- **Exception translation:** Spring automatically translates `@Repository` data access exceptions to `DataAccessException` hierarchy
- **Future framework hooks:** Spring can add behavior to specific stereotypes

The ONLY functional difference today: `@Repository` enables persistence exception translation.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for ApplicationContext. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Bean Lifecycle

**TL;DR** - Spring beans go through a defined lifecycle: instantiation -> property population -> initialization callbacks -> ready for use -> destruction callbacks. Understanding this enables proper resource management and initialization logic.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Without lifecycle hooks, you can't run initialization logic after all dependencies are injected (constructor runs before injection), can't validate configuration, and can't clean up resources (close connections, stop schedulers) on shutdown.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Beans have a birth, a life, and a death. Spring gives you hooks at each stage to run custom logic.

**Level 2 - How to use it (junior developer):**

```java
@Service
public class CacheService {
    private final RedisClient client;

    public CacheService(RedisClient client) {
        this.client = client;
    }

    @PostConstruct
    public void init() {
        // Runs AFTER constructor + injection
        client.connect();
        warmUpCache();
    }

    @PreDestroy
    public void cleanup() {
        // Runs on application shutdown
        client.disconnect();
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Complete bean lifecycle:

```
1. Instantiation (constructor)
2. Populate properties (@Autowired, @Value)
3. BeanNameAware.setBeanName()
4. BeanFactoryAware.setBeanFactory()
5. ApplicationContextAware.setAppContext()
6. BeanPostProcessor.postProcessBefore()
7. @PostConstruct / InitializingBean.afterSet()
8. Custom init-method
9. BeanPostProcessor.postProcessAfter()
   (AOP proxies created here!)
10. Bean is ready for use
    ...
11. @PreDestroy / DisposableBean.destroy()
12. Custom destroy-method
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Critical insight:** `@PostConstruct` runs BEFORE AOP proxies are created. So `this` inside `@PostConstruct` is the raw object, not the proxy. Calling `@Transactional` methods from `@PostConstruct` won't have transaction behavior.

```java
@Service
public class DataLoader {
    @PostConstruct
    public void init() {
        loadData(); // No transaction! Raw 'this'
    }

    @Transactional
    public void loadData() { /* ... */ }
}

// Fix: Use ApplicationReadyEvent
@EventListener(ApplicationReadyEvent.class)
public void onReady() {
    loadData(); // Called on proxy -> TX works
}
```

**SmartLifecycle** for ordering startup/shutdown:

```java
@Component
public class KafkaConsumer
        implements SmartLifecycle {
    public int getPhase() { return 10; }
    // Higher phase = starts later, stops first
    public void start() { consumer.subscribe(); }
    public void stop() { consumer.close(); }
}
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `@PostConstruct` runs after injection; `@PreDestroy` on shutdown
2. AOP proxies are created AFTER @PostConstruct (self-invocation won't have AOP)
3. Use `ApplicationReadyEvent` for logic that needs full proxy/transaction support

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: In what order do lifecycle callbacks execute?**

_Why they ask:_ Tests precise lifecycle knowledge.

_Strong answer:_

For initialization (in order):

1. Constructor (with injected dependencies)
2. `@PostConstruct` method
3. `InitializingBean.afterPropertiesSet()`
4. Custom `init-method` from `@Bean(initMethod="...")`

For destruction (in order):

1. `@PreDestroy` method
2. `DisposableBean.destroy()`
3. Custom `destroy-method` from `@Bean(destroyMethod="...")`

`@PostConstruct`/`@PreDestroy` are preferred (standard Java annotations, no Spring dependency in your class). `InitializingBean`/`DisposableBean` are older Spring-specific interfaces.

---

**Q2: Why doesn't @Transactional work when called from @PostConstruct?**

_Why they ask:_ Tests understanding of proxy timing.

_Strong answer:_

The bean lifecycle: Construction -> Injection -> @PostConstruct -> BeanPostProcessor (creates AOP proxy).

At `@PostConstruct` time, the AOP proxy doesn't exist yet. The method runs on the raw object. `@Transactional` requires the proxy to intercept the call and manage the transaction.

Fix: Use `ApplicationReadyEvent` (fires after all beans and proxies are created) or `SmartInitializingSingleton` (fires after all singletons are instantiated and proxied).

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Bean Lifecycle. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Bean Scopes

**TL;DR** - Bean scope controls how many instances Spring creates and how long they live. Singleton (one per container, default) vs Prototype (new instance per injection) vs Request/Session (web-scoped).

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Some objects should exist once (database connection pool), some should be created fresh each time (form builder with state), and some should live per HTTP request (user context). Without scopes, you'd manually manage all these lifecycles.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Scope answers: "How many of these objects exist and when are they created/destroyed?"

**Level 2 - How to use it (junior developer):**

```java
@Component
@Scope("singleton") // default - can be omitted
public class ConnectionPool { }

@Component
@Scope("prototype")
public class ReportBuilder { }

@Component
@Scope("request") // one per HTTP request
public class RequestContext { }
```

**Level 3 - How it works (mid-level engineer):**

| Scope       | Instances            | Created       | Destroyed          |
| ----------- | -------------------- | ------------- | ------------------ |
| singleton   | 1 per container      | Startup       | Container shutdown |
| prototype   | New each time        | On request    | Never (GC'd)       |
| request     | 1 per HTTP request   | Request start | Request end        |
| session     | 1 per HTTP session   | Session start | Session end        |
| application | 1 per ServletContext | App start     | App stop           |

**The prototype scope trap:**

```java
@Component // singleton
public class OrderService {
    @Autowired
    private ShoppingCart cart; // prototype?
    // WRONG! cart is injected ONCE (at startup)
    // Same cart instance for all users!
}
```

Fix: Use `ObjectFactory` or `Provider`:

```java
@Component
public class OrderService {
    private final ObjectFactory<ShoppingCart>
        cartFactory;

    public void process() {
        ShoppingCart cart = cartFactory.getObject();
        // New instance each time
    }
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Scoped proxies** solve the singleton-references-prototype problem:

```java
@Component
@Scope(value = "request",
       proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext {
    private User currentUser;
}

@Service // singleton
public class UserService {
    private final RequestContext ctx;
    // Injected proxy! Delegates to actual
    // request-scoped instance per request
}
```

The proxy (CGLIB subclass) intercepts method calls and dispatches to the correct scope instance (looked up from the current thread's request).

**Thread safety:** Singletons MUST be thread-safe (shared by all threads). Prototype/request/session beans inherently have less contention (shorter lifecycle or per-thread).


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Default is singleton (one instance, shared, MUST be thread-safe)
2. Prototype creates a new instance per injection/lookup (Spring doesn't manage destruction)
3. Injecting short-lived scope into singleton needs a proxy or ObjectFactory

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: What happens when a singleton bean depends on a prototype bean?**

_Why they ask:_ Tests understanding of scope interaction.

_Strong answer:_

The singleton is created once at startup. Its prototype dependency is injected once (also at startup). The singleton holds the same prototype instance forever - defeating the purpose of prototype scope.

```java
@Component // singleton, created once
class Service {
    @Autowired
    PrototypeBean bean; // injected ONCE
    // Same instance for all calls!
}
```

Solutions:

1. **ObjectFactory/Provider:** `Provider<PrototypeBean>` - call `.get()` each time
2. **Scoped proxy:** `@Scope(proxyMode = TARGET_CLASS)` - proxy delegates to fresh instance
3. **@Lookup method:** Spring overrides the method to return new instance
4. **ApplicationContext.getBean():** Direct container call (couples code to Spring)

Best practice: `ObjectFactory<T>` or `Provider<T>` - explicit, testable, no proxy magic.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Bean Scopes. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Circular Dependencies

**TL;DR** - Circular dependencies occur when Bean A depends on Bean B which depends on Bean A. Spring can resolve field/setter injection cycles (via early reference exposure) but fails fast on constructor injection cycles.

---

### The Problem This Solves

**WORLD WITHOUT IT (understanding):**
Without understanding circular dependencies, you get cryptic startup errors (`BeanCurrentlyInCreationException`) and may "fix" them by switching to field injection - which hides the design problem rather than solving it.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A needs B, but B also needs A. It's a chicken-and-egg problem - which do you create first?

**Level 2 - How to use it (junior developer):**

```java
// CIRCULAR: both need each other
@Service
public class OrderService {
    private final PaymentService payment;
    public OrderService(PaymentService p) {
        this.payment = p;
    }
}

@Service
public class PaymentService {
    private final OrderService order;
    public PaymentService(OrderService o) {
        this.order = o;
    }
}
// FAILS: BeanCurrentlyInCreationException
```

**Level 3 - How it works (mid-level engineer):**

Spring's three-level cache for resolving field/setter cycles:

1. Singleton pool (fully initialized beans)
2. Early singleton pool (partially initialized)
3. Singleton factory pool (ObjectFactory for early refs)

```
Creating A:
  1. A constructor runs (B not injected yet)
  2. A added to level-3 cache (factory)
  3. Inject B into A -> need to create B
     Creating B:
       1. B constructor runs
       2. Inject A into B -> found in level-3!
       3. B gets early reference to A
       4. B fully initialized
  4. Inject B into A
  5. A fully initialized
```

This only works with field/setter injection. Constructor injection fails because you can't expose an early reference (object doesn't exist until constructor completes).

**Level 4 - Mastery (senior/staff+ engineer):**

**The right fix is redesign, not workaround:**

Circular dependencies usually signal:

1. Two classes that should be one (merge them)
2. Missing abstraction (extract shared logic to a third class)
3. Event-based decoupling needed (A publishes event, B listens)

```java
// REDESIGN: Extract shared logic
@Service
class OrderService {
    private final OrderPaymentMediator mediator;
}
@Service
class PaymentService {
    private final OrderPaymentMediator mediator;
}
@Service
class OrderPaymentMediator {
    // Contains the shared logic that caused
    // the cycle
}
```

**Spring Boot 2.6+ (default):** Circular dependencies are BANNED by default. You must explicitly allow them:

```properties
spring.main.allow-circular-references=true
```

This is intentional - circular deps are almost always a design smell.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Constructor injection fails fast on circular deps (good - forces redesign)
2. Field/setter injection resolves cycles via early reference exposure (hides the problem)
3. The real fix: extract shared logic, use events, or merge the classes

**Interview one-liner:**
"Circular dependencies are a design smell resolved by extracting shared logic or using events, not by switching to field injection which just hides the coupling problem."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: How would you fix a circular dependency in production code?**

_Why they ask:_ Tests design skills and practical problem-solving.

_Strong answer:_

1. **Identify the cycle:** What do A and B need from each other?
2. **Common patterns:**
   - **Extract interface/mediator:** Move shared logic to a third bean
   - **Event-driven:** A publishes an event, B listens (async decoupling)
   - **Lazy injection:** `@Lazy` on one dependency (proxy injected, resolved on first use)

```java
// Quick fix: @Lazy breaks the cycle
@Service
public class OrderService {
    public OrderService(
            @Lazy PaymentService payment) {
        this.payment = payment;
        // Proxy injected, actual bean resolved
        // on first method call
    }
}
```

`@Lazy` is a workaround, not a solution. The proper fix restructures the dependency graph.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Circular Dependencies. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

