---
layout: default
title: "Bean"
parent: "Spring Core"
nav_order: 375
permalink: /spring/bean/
number: "375"
category: Spring Core
difficulty: ★☆☆
depends_on: IoC, ApplicationContext, Java Classes
used_by: Bean Lifecycle, Bean Scope, @Autowired, BeanPostProcessor, AOP Proxy
tags: #java, #spring, #springboot, #foundational, #pattern
---

# 375 — Bean

`#java` `#spring` `#springboot` `#foundational` `#pattern`

⚡ TL;DR — Any Java object whose instantiation, configuration, and lifecycle is managed entirely by the Spring IoC container.

| #375 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | IoC, ApplicationContext, Java Classes | |
| **Used by:** | Bean Lifecycle, Bean Scope, @Autowired, BeanPostProcessor, AOP Proxy | |

---

### 📘 Textbook Definition

A **Spring Bean** is an object that is instantiated, assembled, and managed by the Spring IoC container. Beans are the building blocks of a Spring application — the container creates them, injects their dependencies, applies AOP proxies, and manages their complete lifecycle from initialisation to destruction. Beans are declared via stereotype annotations (`@Component`, `@Service`, `@Repository`, `@Controller`), `@Bean` factory methods inside `@Configuration` classes, or legacy XML. By default, beans are singletons — one instance per ApplicationContext — though this is configurable via `@Scope`.

---

### 🟢 Simple Definition (Easy)

A Spring Bean is a regular Java object that Spring creates for you. Instead of you writing `new UserService()`, Spring creates it, sets it up, and makes it available wherever it's needed.

---

### 🔵 Simple Definition (Elaborated)

Every significant component in a Spring application is a bean: services, repositories, controllers, scheduled tasks, data sources, security configurations. Spring reads your annotations or configuration, creates each bean in the correct dependency order, injects collaborating beans, and optionally wraps them in AOP proxies for cross-cutting features like transactions and caching. You rarely call `new` directly for application-layer objects — Spring does it, manages the shared instance, and cleans up on shutdown. The name "bean" comes from the JavaBeans specification, though Spring beans don't need to follow the JavaBeans conventions strictly.

---

### 🔩 First Principles Explanation

**Problem — manual object graph assembly doesn't scale:**

```java
// Manual assembly of a non-trivial application
DataSource ds       = new HikariDataSource(hikariConfig);
EntityManager em    = emf.createEntityManager();
UserRepository repo = new JpaUserRepository(em);
BCryptPasswordEncoder enc = new BCryptPasswordEncoder(12);
MailSender mail     = new SmtpMailSender(smtpConfig);
UserService svc     = new UserServiceImpl(repo, enc, mail);
// ... 200 more objects, many sharing ds, em, enc
// Who calls ds.close() on shutdown?
// Who calls svc.init() after injection?
// How do you swap JpaUserRepository for MongoUserRepository?
```

**Solution — declare with annotations, container manages:**

```java
@Repository
class JpaUserRepository implements UserRepository {
  JpaUserRepository(EntityManager em) {...}
}

@Service
class UserService {
  UserService(UserRepository repo,
              PasswordEncoder enc,
              MailSender mail) {...}
}
// Spring reads these, creates in order, injects, manages
```

**What makes an object a bean vs not a bean:**

```
IS a bean:           NOT a bean:
  @Service           Value objects (Money, Address)
  @Component         DTOs (UserResponse, OrderDto)
  @Repository        JPA @Entity classes (managed by JPA)
  @Controller        Lambdas / anonymous objects
  @Bean method       Most objects created inside methods
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT Beans (no container management):**

```
Without Spring beans:

  Multiple instances of DataSource:
    Each class creates its own → 200 connection pools
    → OOM at 100 concurrent users

  No lifecycle management:
    init() / destroy() called inconsistently
    → resource leaks on shutdown

  AOP impossible without container:
    @Transactional just an annotation — does nothing
    without a proxy wrapping the bean

  No singleton guarantee:
    Two "singletons" created by different code paths
    → inconsistent state, hard-to-find bugs
```

**WITH Spring beans:**

```
→ One DataSource shared by all 200 repositories
→ @PostConstruct / @PreDestroy called automatically
→ @Transactional proxy created transparently by BPP
→ Guaranteed singleton — one instance per context
→ @MockBean in tests swaps real bean for mock
  → no infrastructure in unit tests
```

---

### 🧠 Mental Model / Analogy

> A Spring Bean is like an **employee on a company payroll**. HR (the container) hires them (creates the object), issues them equipment (injects dependencies), gives them a security badge with specific access rights (applies AOP proxies), and processes their termination when they leave (calls `@PreDestroy`). You don't manage individual employees — you manage the org chart (configuration) and HR handles the rest. Any colleague who needs to collaborate with another just contacts HR (injection) rather than finding the person themselves.

"HR hiring the employee" = container creating the bean
"Issuing equipment" = dependency injection
"Security badge with access rights" = AOP proxy (transactions, security)
"Processing termination" = @PreDestroy and DisposableBean
"Contacting HR for a colleague" = @Autowired injection

---

### ⚙️ How It Works (Mechanism)

**Three ways to declare a bean:**

```java
// 1. Stereotype annotation — component scan detects it
@Service          // also: @Component, @Repository, @Controller
public class OrderService {
  public OrderService(PaymentGateway gw) { ... }
}

// 2. @Bean factory method in @Configuration class
@Configuration
public class InfraConfig {
  @Bean(destroyMethod = "close")
  public DataSource dataSource(DataSourceProperties p) {
    HikariDataSource ds = new HikariDataSource();
    ds.setJdbcUrl(p.getUrl());
    return ds;
  }
}

// 3. XML (legacy)
// <bean id="userService" class="com.app.UserServiceImpl"/>
```

**Bean naming rules:**

```
@Service             → bean name: "orderService" (class-derived)
@Service("orders")   → bean name: "orders" (explicit)
@Bean                → bean name: derived from method name
@Bean("primary")     → bean name: "primary"
```

**Singleton vs Prototype — the critical distinction:**

```
┌─────────────────────────────────────────────────────┐
│  SINGLETON (default)                                │
│  One instance per ApplicationContext                │
│  Created eagerly at startup                         │
│  All injection points receive the SAME instance     │
│  Container manages full lifecycle (init + destroy)  │
│                                                     │
│  PROTOTYPE                                          │
│  New instance per injection / getBean() call        │
│  Created lazily on each request                     │
│  NO @PreDestroy called — container does NOT track   │
│  Use for: stateful, non-thread-safe objects         │
└─────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
@Component / @Service / @Bean declaration
        ↓
  BEAN (107)  ← you are here
  (managed object in ApplicationContext)
        ↓
  Has: Bean Lifecycle (108) — init → use → destroy
  Has: Bean Scope (109) — singleton / prototype / request
  Has: AOP Proxy wrapping (if @Transactional etc.)
        ↓
  Injected via: @Autowired (112) / constructor
  Customised by: BeanPostProcessor (110)
  Defined as: BeanDefinition metadata
```

---

### 💻 Code Example

**Example 1 — Typical service bean with constructor injection:**

```java
@Service
public class PaymentService {
  private final PaymentGateway gateway;
  private final AuditRepository audit;

  // Single constructor — @Autowired not required (Spring 4.3+)
  public PaymentService(PaymentGateway gateway,
                        AuditRepository audit) {
    this.gateway = Objects.requireNonNull(gateway);
    this.audit   = Objects.requireNonNull(audit);
  }

  public Receipt charge(PaymentRequest request) {
    Receipt receipt = gateway.process(request);
    audit.record(receipt);
    return receipt;
  }
}
```

**Example 2 — Conditional @Bean registration:**

```java
@Configuration
public class PaymentConfig {
  // Created only if Stripe secret is configured
  @Bean
  @ConditionalOnProperty("payment.stripe.secret-key")
  PaymentGateway stripeGateway(StripeProperties props) {
    return new StripePaymentGateway(props.getSecretKey());
  }

  // Fallback for dev/test environments
  @Bean
  @ConditionalOnMissingBean(PaymentGateway.class)
  PaymentGateway stubGateway() {
    return new InMemoryPaymentGateway();
  }
}
```

**Example 3 — Checking bean type with AopUtils:**

```java
// After context startup, @Transactional beans are proxied
@Autowired OrderService service;

// Returns the proxy type (OrderService$$SpringCGLIB$$0)
service.getClass();

// Returns the actual class (OrderService)
AopUtils.getTargetClass(service);

// Is it proxied?
AopUtils.isAopProxy(service); // true if @Transactional
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Singleton bean means thread-safe | Singleton means one instance — not thread-safe. A singleton bean with mutable state accessed by multiple threads is a race condition waiting to happen |
| All objects in a Spring app are beans | DTOs, value objects, domain entities, and most objects created inside method bodies are NOT beans |
| @Bean and @Component serve the same purpose | @Component is for your own classes detected by scan; @Bean is for wiring third-party classes you can't annotate |
| Prototype scope bean's @PreDestroy is called | Spring tracks prototype instances only for creation — it never calls @PreDestroy on prototype beans |

---

### 🔥 Pitfalls in Production

**1. Mutable shared state in a singleton bean**

```java
// BAD: singleton bean with mutable instance field
@Service
class OrderProcessor {
  private Order currentOrder; // shared across ALL threads!

  public Result process(Order order) {
    this.currentOrder = order;      // Thread A sets this
    double tax = calculateTax();    // Thread B overwrites!
    return new Result(currentOrder, tax); // wrong order!
  }
}

// GOOD: stateless singleton — local variables only
@Service
class OrderProcessor {
  public Result process(Order order) {
    double tax = calculateTax(order); // method-local
    return new Result(order, tax);
  }
}
```

**2. Prototype bean injected into singleton — effective singleton**

```java
// BAD: intent is per-request state but gets singleton behaviour
@Service // singleton
class ReportService {
  @Autowired
  ReportContext ctx; // @Scope("prototype") bean
  // ctx injected ONCE at startup — never refreshed

  public Report generate(String id) {
    ctx.setReportId(id);    // shared across responses!
    return ctx.build();     // concurrency disaster
  }
}

// GOOD: use ObjectProvider for per-call prototype
@Service
class ReportService {
  private final ObjectProvider<ReportContext> ctxProvider;

  public ReportService(ObjectProvider<ReportContext> p) {
    this.ctxProvider = p;
  }

  public Report generate(String id) {
    ReportContext ctx = ctxProvider.getObject(); // fresh each time
    ctx.setReportId(id);
    return ctx.build();
  }
}
```

---

### 🔗 Related Keywords

- `IoC` — the principle; beans are what the container manages
- `ApplicationContext` — the container that creates, stores, and provides beans
- `Bean Lifecycle` — the ordered phases every singleton bean passes through
- `Bean Scope` — controls how many instances the container creates
- `@Autowired` — the primary injection annotation for wiring beans together
- `BeanPostProcessor` — hooks into bean creation to customise or proxy bean instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Container-managed Java object — created,  │
│              │ wired, proxied, and lifecycle-managed      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Services, repos, controllers, config      │
│              │ infrastructure, shared application objects │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ DTOs, value objects, JPA entities, objects│
│              │ created per-request inside methods        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A bean is any object Spring adopted —    │
│              │  it handles birth, life, and death."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bean Lifecycle (108) → Bean Scope (109) → │
│              │ BeanPostProcessor (110)                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A singleton service bean holds a `Map<String, List<Order>>` cache that is populated lazily and read by multiple request threads. You've verified the service is `@Service` (singleton), but under load you observe `ConcurrentModificationException`. Explain exactly what the concurrency failure mode is, why `synchronized(this)` on the service method is a poor solution at scale, and describe the correct data structure and access pattern that makes the cache both thread-safe and performant using Java's concurrent collections.

**Q2.** Spring allows you to define a bean with `@Scope("request")` so a fresh instance is created per HTTP request. When this request-scoped bean is injected into a singleton-scoped service via constructor injection, Spring cannot inject it directly. Explain the exact technical reason why direct injection fails, what "scoped proxy" Spring creates to solve it (CGLIB or JDK?), how the proxy resolves the actual request-scoped bean at method-invocation time, and what happens when `service.doWork()` is called outside of an HTTP request context.

