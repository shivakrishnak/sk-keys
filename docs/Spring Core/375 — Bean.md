---
layout: default
title: "Bean"
parent: "Spring Core"
nav_order: 375
permalink: /spring/bean/
number: "375"
category: Spring Core
difficulty: ★☆☆
depends_on: IoC (Inversion of Control), DI (Dependency Injection)
used_by: Bean Lifecycle, Bean Scope, ApplicationContext, BeanFactory
tags: #foundational, #spring, #architecture
---

# 375 — Bean

`#foundational` `#spring` `#architecture`

⚡ TL;DR — A **bean** is any object whose lifecycle — instantiation, dependency wiring, and destruction — is managed by the Spring IoC container.

| #375            | Category: Spring Core                                 | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | IoC (Inversion of Control), DI (Dependency Injection) |                 |
| **Used by:**    | Bean Lifecycle, Bean Scope, ApplicationContext        |                 |

---

### 📘 Textbook Definition

In Spring, a **bean** is an object that is instantiated, assembled, and managed by the Spring IoC container. A class becomes a bean by being registered with the container — either via stereotype annotations (`@Component`, `@Service`, `@Repository`, `@Controller`), explicit `@Bean` methods in a `@Configuration` class, or XML bean definitions. The container stores a _bean definition_ (metadata describing class, scope, dependencies, and lifecycle callbacks) for each bean and uses it to create bean instances. The container manages the full lifecycle: instantiation → dependency injection → `BeanPostProcessor` processing → `@PostConstruct` initialisation → ready state → `@PreDestroy` cleanup → destruction. Beans are distinct from plain Java objects: they are container-aware, scoped, and wired.

---

### 🟢 Simple Definition (Easy)

A bean is any Java object that Spring creates and manages for you. You register it once; Spring creates it, wires it, and destroys it when done.

---

### 🔵 Simple Definition (Elaborated)

A regular Java object is created with `new MyClass()` and lives as long as a variable holds a reference to it. A Spring bean is different: you declare it (with an annotation or configuration), and Spring takes responsibility for creating it at the right time, injecting its dependencies, running any initialisation code, keeping it alive as long as needed (based on scope), and running cleanup code when it is no longer needed. The advantage is that you declare the entire graph of objects and their relationships once; Spring handles construction order, lifecycle, and teardown. Any `@Service`, `@Repository`, `@Controller`, `@Component`, or `@Bean` method result is a bean.

---

### 🔩 First Principles Explanation

**What makes an object a bean — three registration paths:**

```java
// PATH 1: Stereotype annotation (most common in Spring Boot)
@Service           // tells Spring: "manage this class as a bean"
class OrderService {
    private final PaymentGateway gateway; // dependency — also a bean
    OrderService(PaymentGateway gateway) { this.gateway = gateway; }
}

// PATH 2: Explicit @Bean method in a @Configuration class
@Configuration
class InfraConfig {
    @Bean
    DataSource dataSource() {          // Spring manages the returned object
        HikariConfig cfg = new HikariConfig();
        cfg.setJdbcUrl(System.getenv("DB_URL"));
        return new HikariDataSource(cfg); // THIS object becomes a bean
    }
}

// PATH 3: XML bean definition (legacy)
// <bean id="orderService" class="com.example.OrderService">
//   <constructor-arg ref="paymentGateway"/>
// </bean>
```

**BeanDefinition — the blueprint Spring stores:**

```
BeanDefinition for OrderService:
  beanClass:        com.example.OrderService
  scope:            singleton (default)
  lazyInit:         false (default)
  constructorArgs:  [ref: paymentGateway]
  propertyValues:   {}
  initMethod:       null (or @PostConstruct method name)
  destroyMethod:    null (or @PreDestroy method name)
  autowireMode:     CONSTRUCTOR
```

Spring stores bean definitions, not instances. Instances are created from definitions according to scope rules.

**Beans are NOT just any Java object — key distinctions:**

```java
// NOT a bean — created with new, unmanaged
List<String> names = new ArrayList<>();   // not a bean
String result = "hello";                  // not a bean
LocalDate today = LocalDate.now();        // not a bean (value object)

// IS a bean — managed by Spring
@Service OrderService service   // bean: scoped, wired, lifecycle-managed
@Repository UserRepo repo       // bean
@Bean HikariDataSource ds       // bean: Spring manages its connection pool lifecycle
```

DI only works between beans. `OrderService` can inject `PaymentGateway` only if both are beans. A plain `new ArrayList<>()` cannot be injected via Spring.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT the Bean concept:

What breaks without it:

1. No unified lifecycle management — every class constructs and destroys its own collaborators, leading to resource leaks (unclosed connections, uncleaned thread pools).
2. No single source of truth for singleton instances — multiple callers create multiple objects, leading to inconsistent state.
3. No central configuration for cross-cutting concerns — AOP, transactions, security, and caching cannot be applied without a container-managed object graph.
4. No testability via injection — classes create their own dependencies, preventing mock substitution.

WITH Beans:
→ Spring manages singleton lifecycle — one instance, shared safely.
→ `@PreDestroy` hooks ensure resources (connections, executors) are closed on shutdown.
→ AOP proxies wrap beans transparently — `@Transactional` and `@Cacheable` work without code changes.
→ Beans are replaceable by profile, condition, or test mock.

---

### 🧠 Mental Model / Analogy

> Think of a staffing agency roster. The agency (Spring) maintains a list of vetted professionals (beans). When you need a professional (declare a dependency), you don't hire and train them yourself — the agency provides someone from the roster, already cleared and equipped. The agency manages their contract (lifecycle), replaces them when they leave (destruction), and ensures only one person fills each unique role at a time (singleton scope). You interact with the professional, not the hiring process.

"Staffing agency roster" = the Spring bean registry (ApplicationContext)
"Vetted professional" = a Spring bean (instantiated, wired, ready)
"Hiring and training yourself" = calling `new ConcreteClass()` manually
"Singleton role" = default singleton scope (one instance per context)
"Contract management" = Spring bean lifecycle (init, destroy callbacks)

---

### ⚙️ How It Works (Mechanism)

**How Spring finds beans — component scan:**

```
┌──────────────────────────────────────────────┐
│  @ComponentScan("com.example")               │
│                                              │
│  Spring scans classpath under base package:  │
│    @Component → registers as bean            │
│    @Service   → @Component alias             │
│    @Repository→ @Component + exception trans │
│    @Controller→ @Component + web handler     │
│    @Bean method in @Configuration → bean     │
│                                              │
│  Each found class → BeanDefinition added     │
│  to DefaultListableBeanFactory registry      │
└──────────────────────────────────────────────┘
```

**Bean naming conventions:**

```java
// Default name: lowercase first letter of class name
@Service
class OrderService {}   // bean name: "orderService"

@Component("myCustomName")
class Processor {}      // bean name: "myCustomName"

@Bean
DataSource primaryDataSource() {}  // bean name: "primaryDataSource"

// Access by name or type:
OrderService svc = ctx.getBean("orderService", OrderService.class);
OrderService svc = ctx.getBean(OrderService.class); // by type (preferred)
```

---

### 🔄 How It Connects (Mini-Map)

```
IoC (Inversion of Control)
(principle: container manages object lifecycle)
        │
        ▼
Bean  ◄──── (you are here)
(an object managed by the container)
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
Bean Lifecycle                         Bean Scope
(instantiation → init → destroy)       (singleton, prototype, request...)
        │                                      │
        ▼                                      ▼
BeanPostProcessor                      ApplicationContext
(intercepts bean creation)             (holds and exposes all beans)
```

---

### 💻 Code Example

**Example 1 — The three common bean declaration styles:**

```java
// Style 1: @Component family (component scan)
@Service   // semantic alias for @Component in service layer
public class ProductService {
    private final ProductRepository repo;
    ProductService(ProductRepository repo) { this.repo = repo; }
}

@Repository  // @Component + persistence exception translation
public class JpaProductRepository implements ProductRepository { ... }

// Style 2: @Bean method (full control over construction)
@Configuration
public class SecurityConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12); // full control of constructor args
    }
}

// Style 3: @Bean with dependencies (explicit wiring)
@Configuration
public class AppConfig {
    @Bean
    public UserService userService(UserRepository repo,
                                   PasswordEncoder encoder) {
        return new UserService(repo, encoder); // Spring injects repo and encoder
    }
}
```

**Example 2 — Lifecycle callbacks:**

```java
@Component
public class ConnectionPool {
    private HikariDataSource dataSource;

    @PostConstruct          // called after injection is complete
    void initialize() {
        dataSource = new HikariDataSource(buildConfig());
        log.info("Connection pool started with {} connections",
                 dataSource.getMaximumPoolSize());
    }

    @PreDestroy             // called before the bean is destroyed
    void shutdown() {
        if (dataSource != null) dataSource.close();
        log.info("Connection pool closed");
    }
}
```

**Example 3 — Conditional bean registration:**

```java
// Bean only registered if property is set
@Bean
@ConditionalOnProperty(name = "feature.audit.enabled", havingValue = "true")
AuditService auditService(AuditRepository repo) {
    return new AuditService(repo);
}
// If property is false/absent: bean does not exist in context
// Injecting AuditService where it is optional requires @Autowired(required=false)
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                     |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every Java object in a Spring application is a bean       | Only objects registered with and managed by the Spring container are beans. DTOs, request/response objects, value objects, and ad-hoc `new` instances are not beans                                         |
| `@Service` and `@Component` behave differently at runtime | Both are component-scan markers that result in the same bean registration. `@Service` is a semantic convention for service-layer classes; there is no runtime difference                                    |
| Beans are always singletons                               | Singleton is the default scope; other scopes exist: prototype (new instance per request), request, session, and application. Prototype beans have no `@PreDestroy` callback                                 |
| You can only have one bean per type                       | You can have multiple beans of the same type. Spring resolves injection by type and uses `@Qualifier` or `@Primary` to disambiguate. Listing all beans of a type: `ctx.getBeansOfType(SomeInterface.class)` |

---

### 🔥 Pitfalls in Production

**Singleton bean holding mutable request-scoped state — thread safety bug**

```java
// BAD: singleton service stores per-request state in a field
@Service  // singleton — one instance shared across ALL threads
class OrderService {
    private Order currentOrder; // SHARED mutable field — race condition!

    void process(Order order) {
        this.currentOrder = order; // Thread A sets it
        validate();                // Thread B overwrites it between these lines
        save(this.currentOrder);   // Thread A saves Thread B's order
    }
}

// GOOD: keep all per-request state in local variables or method parameters
@Service
class OrderService {
    void process(Order order) {
        Order validated = validate(order);  // local — thread-safe
        save(validated);
    }
}
```

---

**Using `@Autowired(required = false)` on a critical dependency — silent null**

```java
// BAD: optional injection on a non-optional dependency
@Service
class PaymentService {
    @Autowired(required = false) // "optional" but actually required
    private PaymentGateway gateway;

    void charge(Order order) {
        gateway.charge(order); // NullPointerException if no bean found
        // No error at startup — only fails at first charge attempt
    }
}

// GOOD: required dependencies must fail fast at startup
@Service
class PaymentService {
    private final PaymentGateway gateway; // constructor — fails at context load

    PaymentService(PaymentGateway gateway) {
        this.gateway = Objects.requireNonNull(gateway);
    }
}
```

---

### 🔗 Related Keywords

- `IoC (Inversion of Control)` — the principle that makes beans container-managed
- `DI (Dependency Injection)` — the mechanism by which beans receive their dependencies
- `Bean Lifecycle` — the sequence of phases each bean passes through in the container
- `Bean Scope` — defines how many instances are created (singleton, prototype, request, session)
- `ApplicationContext` — the container that stores and manages all beans
- `@Component / @Service / @Repository` — stereotype annotations that register a class as a bean
- `BeanDefinition` — the metadata blueprint the container uses to create bean instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Any object whose lifecycle Spring manages:│
│              │ create, wire, init, use, destroy          │
├──────────────┼───────────────────────────────────────────┤
│ REGISTER     │ @Component/@Service/@Repository/@Bean     │
│              │ or XML — must be in a scanned package     │
├──────────────┼───────────────────────────────────────────┤
│ DEFAULT SCOPE│ Singleton — one instance per context      │
│              │ Prototype — new instance per request      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A bean is a Java object on Spring's      │
│              │ payroll — Spring hires, trains, and fires."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bean Lifecycle → Bean Scope →             │
│              │ BeanPostProcessor → @Autowired            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot service has 200 singleton beans. Each singleton is instantiated once at startup and reused for every request. One of these beans — `ReportService` — does an expensive computation in its `@PostConstruct` method (loading a 10 MB lookup table into memory). The lookup table changes every 6 hours from a database refresh. Describe at least three strategies to handle this "initialise once but needs periodic refresh" requirement within the Spring bean model, explain the thread-safety concern for each, and identify which strategy Spring's `@Scheduled` + `@RefreshScope` (Spring Cloud) addresses and why `@RefreshScope` must destroy and recreate the bean rather than just updating a field.

**Q2.** When Spring detects a `@Bean` method annotated with `@Scope("prototype")` inside a singleton `@Configuration` class, calling the `@Bean` method multiple times from within the same `@Configuration` class does NOT create multiple instances in standard Spring. Explain the mechanism Spring uses (CGLIB subclassing of `@Configuration` classes) that makes `@Bean` method calls idempotent for singletons, describe what happens at the bytecode level when the CGLIB proxy intercepts a `@Bean` method call, and explain why `@Scope("prototype")` beans require a different mechanism (`ObjectFactory<T>`, `@Lookup`, or scoped proxy) when injected into a singleton bean.
