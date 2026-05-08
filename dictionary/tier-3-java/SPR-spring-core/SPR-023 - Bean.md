---
layout: default
title: "Bean"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /spring/bean/
id: SPR-023
category: Spring Core
difficulty: ★☆☆
depends_on: IoC, DI, BeanFactory
used_by: Bean Lifecycle, Bean Scope, BeanPostProcessor, ApplicationContext
related: Component, Service, Repository, BeanDefinition
tags:
  - spring
  - springboot
  - foundational
  - architecture
---

# SPR-023 - Bean

⚡ TL;DR - A bean is any object whose lifecycle - creation, wiring, and destruction - is managed by Spring's IoC container.

| #375            | Category: Spring Core                                             | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | IoC, DI, BeanFactory                                              |                 |
| **Used by:**    | Bean Lifecycle, Bean Scope, BeanPostProcessor, ApplicationContext |                 |
| **Related:**    | Component, Service, Repository, BeanDefinition                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a plain Java application, you create objects with `new`. Objects have no guaranteed lifecycle: they're created somewhere in a call chain, used, and eventually garbage collected. There's no central registry. You can't ask "is there a `UserRepository` somewhere?" You can't guarantee that two parts of the app share the _same_ instance of a service. You can't hook into an object's initialization or destruction. Every object is on its own.

**THE BREAKING POINT:**
Shared infrastructure objects (database connections, HTTP clients, thread pools) should exist exactly once per application. But `new` creates new instances every time. Without a managed lifecycle, connection pools leak, thread pools multiply, initialization logic runs multiple times, and cleanup on shutdown never happens. Applications grow unpredictable as each part of the codebase creates its own versions of shared resources.

**THE INVENTION MOMENT:**
"This is exactly why the Bean concept was created."

---

### 📘 Textbook Definition

A **bean** in Spring is an object that is instantiated, assembled, and managed by the Spring IoC container. Beans are defined through stereotype annotations (`@Component`, `@Service`, `@Repository`, `@Controller`), `@Bean` factory methods inside `@Configuration` classes, or (historically) XML `<bean>` declarations. The container stores metadata about each bean in a `BeanDefinition`, which specifies the class, scope, dependencies, initialization method, and destruction method. The container creates beans, injects their dependencies, calls lifecycle callbacks, and destroys them when the application shuts down.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A bean is a Spring-managed object: Spring creates it, wires it, and cleans it up.

**One analogy:**

> A bean is like a government-issued ID card holder. The government (Spring) issues the ID (registers the bean), knows exactly who holds one (singleton registry), can revoke them (destroy callbacks), and ensures everyone needing the same person gets the same ID holder - not a copy. Objects without Spring management are like people without IDs: untracked and unverifiable.

**One insight:**
The difference between a bean and a plain object is _management_. A plain object doesn't know who created it, how long it should live, or when it should be destroyed. A bean has a complete lifecycle managed externally - creation, dependency wiring, initialization, use, and destruction. This external management is what makes Spring's AOP, transactions, and event systems work.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A bean is registered with the container before it can be injected - you can't inject what Spring doesn't know about.
2. Singleton beans are created once and shared; the same object reference is returned to every consumer.
3. Bean metadata (the `BeanDefinition`) is separate from the bean instance - the recipe is stored independently of the cooked dish.

**DERIVED DESIGN:**
For a bean to be manageable, Spring needs:

- _Discovery:_ How to find the class (annotation scanning, explicit registration)
- _Description:_ How to create it (constructor, factory method), its scope, its lifecycle callbacks
- _Storage:_ Where to keep the instance (singleton cache) or the factory (prototype)

The `BeanDefinition` stores all description. The `BeanDefinitionRegistry` (inside `ApplicationContext`) stores all definitions. The singleton cache stores all instances.

**THE TRADE-OFFS:**

**Gain:** Shared instances, managed lifecycle, AOP proxy wrapping, dependency injection, and lifecycle callbacks - all free for any class registered as a bean.

**Cost:** Spring must know about the class before it can manage it. Beans created outside Spring (with `new`) are invisible to the container. A bean's `this` reference inside methods bypasses Spring's proxy - calling `this.method()` skips `@Transactional` and `@Cacheable`. Understanding this "self-invocation" trap is essential.

---

### 🧪 Thought Experiment

**SETUP:**
Your application has a `DatabasePool` that opens 20 connections to a PostgreSQL database. You need exactly one pool per application.

**WHAT HAPPENS WITHOUT beans (plain `new`):**

1. `UserRepository` creates `new DatabasePool()` - 20 connections opened.
2. `OrderRepository` creates `new DatabasePool()` - 20 more connections.
3. `ProductRepository` creates `new DatabasePool()` - 20 more.
4. With 10 repositories, you have 200 open connections.
5. PostgreSQL's default limit is 100. Database refuses connections.
6. The application crashes under normal load.

**WHAT HAPPENS WITH a singleton bean:**

1. Spring creates `DatabasePool` exactly once (singleton scope).
2. `UserRepository`, `OrderRepository`, `ProductRepository` all receive the _same_ `DatabasePool` instance via DI.
3. 20 connections total, shared across all repositories.
4. On shutdown, Spring calls `@PreDestroy` on the pool, closing all 20 connections cleanly.

**THE INSIGHT:**
Singleton beans enforce shared-instance semantics without the developer writing a singleton pattern. Spring's container _is_ the singleton registry - and it manages cleanup that manual singletons usually forget.

---

### 🧠 Mental Model / Analogy

> Beans are like registered businesses. When a business registers with the government (Spring), it gets a unique registration number (bean name), operates under known rules (scope, lifecycle), pays taxes on creation and dissolution (@PostConstruct / @PreDestroy), and is listed in public records (the bean registry). You can look up any registered business. Unregistered businesses (plain objects created with `new`) are invisible to the system.

- "Government registry" → Spring's `BeanDefinitionRegistry`
- "Business registration" → `@Component` / `@Bean` declaration
- "Single location of a franchise" → singleton scope (one instance)
- "New franchise location" → prototype scope (new instance per request)
- "Business closing procedures" → `@PreDestroy` / `DisposableBean`

**Where this analogy breaks down:** Unlike a government registry that's passive, Spring's container actively _creates_ the businesses it registers, injects their resources, and monitors their health - it's much more hands-on than passive registration.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A bean is any object that Spring knows about and takes care of. You tell Spring "here's a class" and Spring creates an object from it, gives it everything it needs, and cleans it up when your app shuts down.

**Level 2 - How to use it (junior developer):**
Add `@Component` (or `@Service`, `@Repository`, `@Controller`) to any class. Spring will find it during component scan and register it as a bean. To create beans from third-party classes (that you can't annotate), use `@Bean` factory methods inside a `@Configuration` class. Inject beans into each other via constructor injection and `@Autowired`.

**Level 3 - How it works (mid-level engineer):**
`ClassPathScanningCandidateComponentProvider` scans classpath for annotated classes. For each, it creates a `ScannedGenericBeanDefinition` (a subtype of `BeanDefinition`) and registers it in the `BeanDefinitionRegistry`. During context refresh, `DefaultListableBeanFactory.preInstantiateSingletons()` iterates all registered singletons and creates them via `AbstractBeanFactory.doGetBean()`. The instance is stored in `singletonObjects` (a `ConcurrentHashMap`).

**Level 4 - Why it was designed this way (senior/staff):**
The `BeanDefinition` abstraction was deliberately separated from the instantiation mechanism. This allows `BeanFactoryPostProcessors` like `PropertySourcesPlaceholderConfigurer` to modify bean definitions (e.g., resolve `${db.url}` placeholders) _before_ any instances are created. If definitions and instances were tightly coupled, late-binding property resolution would be impossible. The separation also enables lazy initialization, prototype scoping, and the three-level cache for circular dependency handling - none of which would work if Spring created instances at registration time.

---

### ⚙️ How It Works (Mechanism)

**Three ways to define a bean:**

```java
// Method 1: Component scan (most common)
@Service                    // stereotype annotation
public class UserService { ... }
// Spring finds this via ClassPathScanningCandidateComponentProvider

// Method 2: @Bean factory method (for third-party classes)
@Configuration
public class InfraConfig {
    @Bean                   // returns a managed bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:postgresql://localhost/app");
        return ds;
    }
}

// Method 3: Programmatic registration
GenericApplicationContext ctx = new GenericApplicationContext();
ctx.registerBean(UserService.class);
ctx.refresh();
```

**Bean lifecycle summary (detailed in Bean Lifecycle entry):**

```
BeanDefinition registered
    ↓
BeanFactoryPostProcessors run (modify definitions)
    ↓
Bean instantiated (constructor or factory method)
    ↓
Dependencies injected
    ↓
BeanPostProcessors run (before init)
    ↓
@PostConstruct / afterPropertiesSet() called
    ↓
BeanPostProcessors run (after init)
    ↓
Bean ready for use
    ↓
[application runs...]
    ↓
@PreDestroy / destroy() called on shutdown
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
@SpringBootApplication triggers component scan
    ↓
All @Component classes detected → BeanDefinitions created
    ↓
@Configuration classes processed → @Bean methods detected
    ↓
All definitions registered in BeanDefinitionRegistry
    ↓
ApplicationContext.refresh() instantiates singletons
   ← YOU ARE HERE (each class becomes a managed bean)
    ↓
Dependencies injected, lifecycle callbacks called
    ↓
Application serves requests using beans
    ↓
JVM shutdown → Spring destroys beans (@PreDestroy)
```

**FAILURE PATH:**

```
Bean instantiation fails (exception in constructor)
    ↓
BeanCreationException wraps the original exception
    ↓
Context refresh fails → Application exits
    ↓
Stack trace shows which bean failed and why
```

**WHAT CHANGES AT SCALE:**
The number of beans directly affects startup time. Each bean requires reflection-based instantiation, potential proxy wrapping (AOP), and `BeanPostProcessor` passes. A 1,000-bean application may take 15 seconds to start; a 10,000-bean application (some large enterprise apps) may take 2+ minutes. GraalVM native compilation eliminates this startup cost by pre-computing all bean instantiation at build time.

---

### 💻 Code Example

**Example 1 - Stereotype annotations (most common):**

```java
// @Service is @Component with semantic meaning for layering
@Service
public class ProductService {
    private final ProductRepository repo;

    public ProductService(ProductRepository repo) {
        this.repo = repo;
    }

    public List<Product> findAll() {
        return repo.findAll();
    }
}

// @Repository triggers persistence exception translation
@Repository
public class JpaProductRepository implements ProductRepository {
    // Spring wraps SQLException in DataAccessException
}
```

**Example 2 - @Bean for third-party libraries:**

```java
@Configuration
public class HttpClientConfig {

    @Bean
    @ConditionalOnMissingBean  // only create if no other bean exists
    public RestTemplate restTemplate() {
        RestTemplate template = new RestTemplate();
        template.setConnectTimeout(Duration.ofSeconds(5));
        return template;
    }

    @Bean("slowClient")     // named bean for disambiguation
    public RestTemplate slowRestTemplate() {
        RestTemplate template = new RestTemplate();
        template.setConnectTimeout(Duration.ofSeconds(30));
        return template;
    }
}
```

**Example 3 - Lifecycle callbacks:**

```java
@Component
public class ConnectionManager {
    private Connection connection;

    @PostConstruct          // runs after injection, before use
    public void connect() {
        connection = createConnection();
        log.info("Connection established");
    }

    @PreDestroy             // runs before Spring removes the bean
    public void disconnect() {
        connection.close();
        log.info("Connection closed");
    }
}
```

---

### ⚖️ Comparison Table

| Registration Method           | Use Case                    | Bean Name              | Third-party Classes |
| ----------------------------- | --------------------------- | ---------------------- | ------------------- |
| `@Component` / stereotypes    | Your own classes            | Class name (camelCase) | No                  |
| **`@Bean` in @Configuration** | Any class, explicit control | Method name            | Yes                 |
| `registerBean()` programmatic | Dynamic registration        | Specified              | Yes                 |
| XML `<bean>`                  | Legacy codebases            | Specified              | Yes                 |

**How to choose:** Use stereotype annotations for your own service, repository, and controller classes. Use `@Bean` factory methods for third-party library objects (datasources, HTTP clients, schedulers) or when you need fine-grained control over instantiation.

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| All objects in a Spring app are beans                     | Only objects explicitly registered with the container are beans. Plain objects created with `new` are not beans and get no Spring features.                                                                     |
| @Component and @Service are different at runtime          | Functionally identical. @Service, @Repository, @Controller are all meta-annotated with @Component. The difference is semantic and tooling-visible, not behavioral (except @Repository's exception translation). |
| Calling this.method() inside a bean uses the Spring proxy | self-invocation bypasses the proxy. @Transactional, @Cacheable, and @Async on this.method() are ignored when called as this.method().                                                                           |
| Beans are always singletons                               | Beans default to singleton scope, but can be prototype (new instance each time), request-scoped, session-scoped, or custom scoped.                                                                              |

---

### 🚨 Failure Modes & Diagnosis

**Self-invocation proxy bypass (@Transactional ignored)**

**Symptom:**
A `@Transactional` method is called but no transaction is started. Database changes are not rolled back on exception.

**Root Cause:**
Inside a bean, calling `this.anotherMethod()` bypasses Spring's proxy. The `@Transactional` interceptor lives in the proxy, not in `this`. The call goes directly to the method, skipping the interceptor.

**Diagnostic Command / Tool:**

```bash
# Enable transaction debug logging
logging.level.org.springframework.transaction=DEBUG
# Missing "Creating new transaction" log means the proxy was bypassed
grep "Creating new transaction" app.log
```

**Fix:**

```java
// BAD: self-invocation
@Service
public class OrderService {
    @Transactional
    public void processOrder(Order order) {
        this.validateOrder(order);  // self-invocation
        save(order);
    }

    @Transactional  // ignored! called via 'this', not proxy
    public void validateOrder(Order order) { ... }
}

// GOOD: inject self, or restructure to use a separate bean
@Service
public class OrderService {
    private final OrderValidator validator;  // separate bean

    public void processOrder(Order order) {
        validator.validateOrder(order);  // goes through proxy
        save(order);
    }
}
```

**Prevention:** Never call `this.method()` expecting Spring proxy behavior. Extract methods that need separate proxy interception into separate beans.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `IoC (Inversion of Control)` - beans are the objects whose lifecycle is inverted to the container
- `DI (Dependency Injection)` - the mechanism by which beans receive their dependencies
- `BeanFactory` - the container that creates and stores beans

**Builds On This (learn these next):**

- `Bean Lifecycle` - the complete lifecycle every bean goes through from definition to destruction
- `Bean Scope` - singleton, prototype, request, session - scope determines how many instances exist
- `BeanPostProcessor` - the extension point that runs after bean creation to add AOP, transactions, etc.

**Alternatives / Comparisons:**

- `CDI Bean (Jakarta EE)` - the Java EE equivalent; different annotations but similar lifecycle model
- `Plain POJO` - a Java object not managed by Spring; no lifecycle callbacks, no DI, no AOP

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Any object whose lifecycle Spring manages  │
│              │ - creation, wiring, initialization,        │
│              │ use, and destruction                       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Objects multiplied without control;        │
│ SOLVES       │ shared resources created N times           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ self-invocation (this.method()) bypasses   │
│              │ all Spring proxy features                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any service, repository, controller, or    │
│              │ infrastructure object in a Spring app      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Value objects, DTOs, data classes that     │
│              │ don't need lifecycle management            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Managed lifecycle + DI vs coupling to      │
│              │ Spring container and proxy limitations     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "If Spring doesn't know it, it can't       │
│              │  manage it."                               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bean Scope → Bean Lifecycle →              │
│              │ BeanPostProcessor                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring beans are, by default, singletons - shared across all threads in the application. A singleton `UserService` holds no mutable state and is safe. But a singleton bean that holds mutable instance state (e.g., a counter, a list of pending items) is a concurrency disaster. Where exactly does Spring's singleton guarantee end and your thread-safety responsibility begin?

**Q2.** Spring's proxy wrapping enables @Transactional and @Cacheable to work. But if you serialize a bean and deserialize it, the deserialized object is a plain instance - no proxy. If your application stores beans in a distributed cache (e.g., Redis) and retrieves them later, what happens to Spring's proxy features? How should you design Spring beans to avoid this category of error?
