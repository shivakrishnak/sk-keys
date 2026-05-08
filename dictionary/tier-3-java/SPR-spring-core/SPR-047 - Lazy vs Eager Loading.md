---
layout: default
title: "Lazy vs Eager Loading"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /spring/lazy-vs-eager-loading/
id: SPR-047
category: Spring Core
difficulty: ★★☆
depends_on: IoC, DI, Bean, ApplicationContext
used_by: Performance Optimization, Spring Data JPA, Memory Management
related: Bean Scope, @Lazy, Prototype Bean
tags:
  - spring
  - springboot
  - internals
  - performance
  - intermediate
---

# SPR-047 - Lazy vs Eager Loading

⚡ TL;DR - Eager loading instantiates all beans at startup so problems surface immediately; lazy loading defers instantiation until first use, saving memory but hiding failures until runtime.

| #399            | Category: Spring Core                                        | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | IoC, DI, Bean, ApplicationContext                            |                 |
| **Used by:**    | Performance Optimization, Spring Data JPA, Memory Management |                 |
| **Related:**    | Bean Scope, @Lazy, Prototype Bean                            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a Spring application with 400 beans - REST controllers, JPA repositories, third-party SDK clients, scheduled job runners. In a microservice that serves only read-only queries, all 400 beans are instantiated at startup: the write-path beans, the batch-job beans, the admin-only beans. Startup takes 12 seconds. In production, the pod is killed by Kubernetes liveness checks before it finishes initializing. Every container restart becomes a reliability problem.

**THE BREAKING POINT:**
Startup time correlates directly with bean count. Each bean triggers dependency resolution, proxy generation, and possibly database connections. A large application with 1,000+ beans on resource-constrained Lambda functions or containers hits cold-start latency limits. Worse, the memory footprint is inflated by objects that may never be used in the lifetime of that pod.

**THE INVENTION MOMENT:**
"This is exactly why lazy loading was created."

---

### 📘 Textbook Definition

**Eager loading** is the default Spring ApplicationContext behavior: every singleton bean is instantiated and its dependencies injected during context refresh, before the application accepts any requests. **Lazy loading** (`@Lazy`) defers bean instantiation until the bean is first requested - either by another bean's dependency injection or by explicit `context.getBean()`. Lazy beans are wrapped in a proxy by Spring; on first invocation, the proxy triggers real instantiation. In Spring Boot 2.2+, global lazy initialization can be enabled via `spring.main.lazy-initialization=true`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Eager = everything built at startup; lazy = built on first request.

**One analogy:**

> A restaurant can pre-cook all dishes before opening (eager) - orders are fast but the kitchen is full of food that might not be ordered. Or it can cook each dish only when ordered (lazy) - the kitchen starts empty, but the first customer waits longer.

**One insight:**
The choice between eager and lazy is a trade-off between startup reliability and startup speed. Eager loading makes misconfigured beans fail loudly at startup, before serving any traffic. Lazy loading masks those failures until the first request triggers instantiation - potentially during a customer interaction.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Eager loading guarantees that by the time the application serves its first request, all beans are fully initialized and their wiring has been validated.
2. Lazy loading defers work - instantiation cost is paid on first use, not at startup.
3. Both modes produce identical runtime bean instances; the difference is only WHEN initialization occurs.

**DERIVED DESIGN:**
Spring's default eager strategy reflects the principle that infrastructure failures should fail fast. If a database is misconfigured, you want to know at deploy time, not when the first user hits the endpoint. This is why eager loading is the default for production systems.

Lazy loading earns its place in specific scenarios: functions-as-a-service with cold starts, tests that only exercise a slice of the application, and large monoliths where most beans are rarely used.

Spring implements lazy beans through CGLIB proxies. When you inject a `@Lazy` bean, you actually receive a proxy. The proxy holds the bean class and application context reference. On the first method call, the proxy asks the context for the real instance (creating it if not yet created), then delegates all subsequent calls to that real instance.

**THE TRADE-OFFS:**
**Gain:** Faster startup time, lower initial memory footprint, useful in test and serverless contexts.
**Cost:** Misconfigured beans fail at runtime instead of startup; first-call latency is higher; memory usage profile is less predictable; concurrency issues can arise if two threads simultaneously trigger lazy instantiation of the same bean.

---

### 🧪 Thought Experiment

**SETUP:**
A Spring Boot application with 500 beans. It runs as an AWS Lambda function triggered by HTTP requests. Cold starts are charged and affect user experience.

**WHAT HAPPENS WITHOUT LAZY LOADING:**
Lambda cold start: Spring loads all 500 beans - JPA repositories, S3 clients, SQS consumers, scheduled task executors. Even though the Lambda function only needs 30 beans for this specific endpoint. Cold start: 8 seconds. First request times out. User sees an error.

**WHAT HAPPENS WITH LAZY LOADING (`spring.main.lazy-initialization=true`):**
Lambda cold start: Spring registers all 500 bean definitions but initializes only the 30 beans actually needed for this request. Cold start: 1.2 seconds. First request succeeds. The remaining 470 beans are never instantiated in this function's lifetime.

**THE INSIGHT:**
Lazy loading trades fail-fast safety for startup speed. The right choice depends on your deployment model: long-lived servers benefit from eager (catch failures early); short-lived functions benefit from lazy (minimize cold start).

---

### 🧠 Mental Model / Analogy

> Think of beans as appliances in a house. Eager loading = the electrician wires and tests every appliance before you move in (takes longer up front, but everything works on day 1). Lazy loading = appliances are delivered to their spots but not plugged in until you try to use them (you can move in faster, but the first time you try to use the dishwasher you might discover it's broken).

- "Wiring and testing every appliance" → eager bean instantiation at startup
- "Delivered but not plugged in" → lazy bean - proxy registered, instance not created
- "First time you try to use it" → first method call on the injected proxy
- "Discovering the dishwasher is broken on first use" → runtime exception at first request instead of startup

Where this analogy breaks down: unlike physical appliances, Spring lazy beans are thread-safe by default - if two "people" try to use an uninitialized lazy bean simultaneously, Spring ensures it's only created once.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you start a Spring app, it can set up all its components immediately (eager) or wait and set them up only when first needed (lazy). The default is eager - everything ready before the first user arrives.

**Level 2 - How to use it (junior developer):**
To make a single bean lazy, annotate it with `@Lazy` on the class or on the `@Bean` method. To make all beans lazy globally in Spring Boot, set `spring.main.lazy-initialization=true` in `application.properties`. Use `@Lazy` on individual injection points if you want only one dependency to be lazy without changing the bean's default behavior globally.

**Level 3 - How it works (mid-level engineer):**
Spring's `AbstractApplicationContext.refresh()` calls `finishBeanFactoryInitialization()` which iterates all non-lazy singleton bean definitions and calls `getBean()` on each. Lazy beans are skipped here - only their `BeanDefinition` is registered. When a lazy bean is first requested (via DI or explicit `getBean()`), Spring checks `DefaultSingletonBeanRegistry`'s singleton cache; on a miss it goes through the full creation lifecycle: constructor, dependency injection, `@PostConstruct`, and BeanPostProcessors. With global lazy initialization, Spring Boot wraps all bean definitions in `LazyInitializationBeanFactoryPostProcessor` before context refresh.

**Level 4 - Why it was designed this way (senior/staff):**
The default-eager design reflects fail-fast engineering: deploy-time failures are cheaper than runtime failures. The `@Lazy` annotation was added as an opt-in mechanism - the designer's intent is that lazy is the exception, not the rule. Spring Boot 2.2's global lazy initialization was controversial because it trades operational safety (catching misconfigurations at startup) for a metric (startup time) that can be misleading - a faster startup that fails on first request is worse UX than a slow startup that reliably serves traffic. The feature is particularly useful in test slices (`@WebMvcTest`, `@DataJpaTest`) where only a subset of beans is needed.

---

### ⚙️ How It Works (Mechanism)

**Eager Initialization Path:**

```
ApplicationContext.refresh()
  │
  ├── registerBeanDefinitions() - all beans registered
  │
  └── finishBeanFactoryInitialization()
        │
        ├── for each non-lazy singleton BeanDefinition:
        │     getBean(beanName)
        │       → createBeanInstance() - constructor called
        │       → populateBean() - @Autowired injected
        │       → initializeBean() - @PostConstruct run
        │
        └── ApplicationContext ready - all beans live
```

**Lazy Initialization Path:**

```
ApplicationContext.refresh()
  │
  └── finishBeanFactoryInitialization()
        │ @Lazy beans: BeanDefinition registered, SKIPPED
        │
        └── ApplicationContext ready - lazy beans = proxies

First injection of LazyBean:
  Proxy.getTarget()
    → applicationContext.getBean("lazyBean")
      → createBeanInstance() - NOW initialized
      → cache in singletonObjects
```

---

### 💻 Code Example

**Example 1 - Bean-level lazy annotation:**

```java
// BAD: HeavyReportService initialized at startup
// even if reports are only run monthly
@Service
public class HeavyReportService {
    public HeavyReportService() {
        // loads 10MB of report templates - always
        loadReportTemplates();
    }
}

// GOOD: defer until first use
@Lazy
@Service
public class HeavyReportService {
    public HeavyReportService() {
        loadReportTemplates(); // only when first report runs
    }
}
```

**Example 2 - Lazy injection point:**

```java
@Service
public class OrderService {

    // Fraud check only needed for large orders
    // @Lazy here means: inject a proxy, instantiate
    // FraudCheckService only on first call
    @Lazy
    @Autowired
    private FraudCheckService fraudCheckService;

    public void processOrder(Order order) {
        if (order.amount() > 10_000) {
            // First call here triggers instantiation
            fraudCheckService.check(order);
        }
    }
}
```

**Example 3 - Global lazy initialization (Spring Boot):**

```properties
# application.properties
# Enables lazy init for ALL beans - use with caution
spring.main.lazy-initialization=true

# Useful in Lambda / serverless / test environments
# NOT recommended for standard long-lived services
```

```java
// Override specific beans to be EAGER even with global lazy
@Configuration
public class CriticalConfig {
    @Bean
    @Lazy(false) // force eager even when global lazy is on
    public DatabaseHealthCheck healthCheck() {
        // Must be ready before first health probe
        return new DatabaseHealthCheck();
    }
}
```

---

### ⚖️ Comparison Table

| Strategy            | Startup Time | Memory at Start | Failure Detection | Best For                       |
| ------------------- | ------------ | --------------- | ----------------- | ------------------------------ |
| **Eager (default)** | Slower       | Full footprint  | At startup        | Production long-lived services |
| Lazy (`@Lazy`)      | Faster       | Minimal         | First call        | Rarely-used heavy beans        |
| Global lazy         | Fastest      | Near-zero       | First call        | Lambda/serverless, test slices |
| Prototype scope     | N/A          | Per-request     | Each creation     | Request-scoped objects         |

How to choose: Use eager for any bean whose failure should be caught at deploy time (DB connections, external service clients). Use `@Lazy` selectively for beans that are expensive to create but only needed in edge-case code paths. Reserve global lazy for serverless environments or test configurations.

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Lazy beans are always better for performance                   | Lazy beans shift cost to first request; eager beans amortize startup cost before traffic arrives                       |
| `@Lazy` makes a prototype-scoped bean                          | `@Lazy` only defers initialization; scope (singleton vs. prototype) is orthogonal - use `@Scope("prototype")` for that |
| Global lazy initialization is safe for all production apps     | It hides bean configuration errors until runtime; a misconfigured DataSource won't fail until the first DB call        |
| Lazy beans are created every time they're accessed             | Lazy singletons are created once on first access and then cached; subsequent accesses hit the cache                    |
| `@Lazy` on `@Autowired` injection makes the bean globally lazy | It makes only THIS injection point lazy; other places that inject the same bean may still trigger eager creation       |

---

### 🚨 Failure Modes & Diagnosis

**1. Misconfigured Bean Masked Until Runtime**

**Symptom:** Application starts successfully with `spring.main.lazy-initialization=true`; first request to a specific endpoint throws `NoSuchBeanDefinitionException` or `BeanCreationException` with a configuration error.

**Root Cause:** The bean's initialization code (constructor, `@PostConstruct`) runs on first call, not at startup. A missing `@Value` property or unreachable datasource URL causes instantiation to fail mid-request.

**Diagnostic:**

```bash
# Check Spring context health at startup
grep "BeanCreationException\|NoSuchBean" app.log

# Force eager init of specific beans in production
# to catch failures early
```

**Fix:**

```java
// GOOD: selectively un-lazy critical beans
@Bean
@Lazy(false) // override global lazy for this bean
public DataSource dataSource() {
    // Will fail at startup if DB unreachable
    return DataSourceBuilder.create()...build();
}
```

**Prevention:** When using global lazy initialization, explicitly annotate critical infrastructure beans (`DataSource`, health indicators, external API clients) with `@Lazy(false)`.

---

**2. First-Request Latency Spike**

**Symptom:** P99 latency for first request after deployment is 10–30x higher than warm requests; subsequent requests are normal.

**Root Cause:** Global lazy initialization defers all bean creation to the first request. That single request triggers instantiation of dozens of beans sequentially, including proxy generation, database connection pool warm-up, and cache population.

**Diagnostic:**

```bash
# Enable Spring startup actuator endpoint
curl http://localhost:8080/actuator/startup

# Time bean initialization in startup logs
grep "Instantiating bean" app.log | head -20
```

**Fix:**

```java
// GOOD: use ApplicationRunner to warm up lazy beans
// after context is ready but before serving traffic
@Component
public class LazyBeanWarmer implements ApplicationRunner {
    @Autowired ApplicationContext ctx;

    @Override
    public void run(ApplicationArguments args) {
        // Trigger instantiation before traffic arrives
        ctx.getBean(OrderService.class);
        ctx.getBean(PaymentService.class);
    }
}
```

**Prevention:** Add a readiness probe warm-up step or `ApplicationRunner` that touches critical beans before the pod is marked ready in Kubernetes.

---

**3. Circular Dependency with @Lazy**

**Symptom:** `BeanCurrentlyInCreationException` at runtime (not startup) when using `@Lazy` to break a circular dependency.

**Root Cause:** `@Lazy` on a circular dependency creates a proxy. If both beans A and B use `@Lazy` on each other's injection, both proxies may be created before either real instance, but underlying object graph resolution can fail if the proxy is invoked during construction.

**Diagnostic:**

```bash
grep "BeanCurrentlyInCreationException" app.log
# Shows which bean triggered the cycle at runtime
```

**Fix:**

```java
// BAD: @Lazy used to silence a circular dependency warning
// without resolving the actual design problem
@Service
public class ServiceA {
    @Lazy @Autowired ServiceB b; // hack
}
@Service
public class ServiceB {
    @Autowired ServiceA a;
}

// GOOD: break the cycle via event-driven design
// or by extracting shared logic to a third service
@Service
public class SharedLogicService { ... }
```

**Prevention:** Treat circular dependencies as a design smell; use `@Lazy` to defer initialization, not to mask circular dependency design problems.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Bean` - understand what a Spring bean is before reasoning about when it's initialized
- `ApplicationContext` - the container that manages bean lifecycle and initialization order
- `IoC` - lazy loading is only meaningful within an IoC container's lifecycle model

**Builds On This (learn these next):**

- `Bean Lifecycle` - full picture of how Spring initializes, uses, and destroys beans
- `Auto-Configuration` - Spring Boot's auto-configuration uses `@ConditionalOn*` which interacts with lazy init
- `Spring Boot Actuator` - use the startup endpoint to diagnose bean initialization timing

**Alternatives / Comparisons:**

- `Bean Scope (prototype)` - prototype creates a new instance per injection; lazy creates the singleton on first use
- `@ConditionalOnProperty` - conditionally exclude beans entirely vs. lazily initializing them
- `@Profile` - exclude beans for specific environments entirely, more coarse-grained than lazy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Controls WHEN Spring creates a bean:      │
│              │ at startup (eager) or first use (lazy)    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Large apps have slow startup from         │
│ SOLVES       │ initializing all beans upfront            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Eager catches failures at deploy time;    │
│              │ lazy masks them until first request       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ @Lazy: heavy rarely-used beans;           │
│              │ global lazy: serverless / test slices     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Global lazy on production long-lived      │
│              │ services - hides config failures          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fast startup vs. fail-fast at deploy time │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Eager is the fire drill; lazy is hoping  │
│              │  nothing breaks on the first shift"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bean Lifecycle → Auto-Configuration →     │
│              │ Spring Boot Actuator                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - System Interaction) A Spring Boot microservice with global lazy initialization is deployed behind a Kubernetes readiness probe. The readiness probe calls `GET /actuator/health` which is also lazily initialized. The first call to `/actuator/health` triggers initialization of 50 beans including a slow database connection pool. Trace exactly what happens to pod traffic routing during this initialization window - and how would you prevent this race condition?

**Q2.** (TYPE C - Design Trade-off) A team argues that using global lazy initialization in production reduces cold start time from 15 seconds to 3 seconds, which justifies the risk of runtime failures. A second team argues this is false economy. Under what specific conditions is the first team correct, and what specific failure scenario would prove the second team right?
