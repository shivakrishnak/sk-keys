---
layout: default
title: "Bean"
parent: "Spring & Spring Boot"
nav_order: 142
permalink: /spring/bean/
number: "142"
category: Spring & Spring Boot
difficulty: ★☆☆
depends_on: IoC, ApplicationContext, Java Classes
used_by: Bean Lifecycle, Bean Scope, @Autowired, BeanPostProcessor, AOP Proxy
tags: #java, #spring, #springboot, #foundational, #pattern
---

# 142 — Bean

`#java` `#spring` `#springboot` `#foundational` `#pattern`

⚡ TL;DR — Any Java object whose instantiation, configuration, and lifecycle is managed entirely by the Spring IoC container.

| #142 | Category: Spring & Spring Boot | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IoC, ApplicationContext, Java Classes | |
| **Used by:** | Bean Lifecycle, Bean Scope, @Autowired, BeanPostProcessor, AOP Proxy | |

---

### 📘 Textbook Definition

A **Spring Bean** is an object that is instantiated, assembled, and managed by the Spring IoC container. Beans are the building blocks of a Spring application — the container creates them, injects their dependencies, applies AOP proxies, and manages their complete lifecycle from initialisation to destruction. Beans are defined via stereotype annotations (`@Component`, `@Service`, `@Repository`, `@Controller`), `@Bean` factory methods in `@Configuration` classes, or XML configuration. By default, beans are singletons — one instance per container — though this is configurable via `@Scope`.

---

### 🟢 Simple Definition (Easy)

A Spring Bean is just a regular Java object — but instead of you creating it with `new`, Spring creates it, sets it up, and hands it to any class that needs it.

---

### 🔵 Simple Definition (Elaborated)

Every significant object in a Spring application is typically a bean: your services, repositories, controllers, data sources, security configurations. The Spring container reads your annotations or configuration, creates each bean in the right order (respecting dependencies), injects dependencies between beans, and optionally wraps them in proxies for cross-cutting features like transactions and security. You rarely call `new` directly for application-level objects — Spring does it for you. The term "bean" comes from JavaBeans — the original Java component specification — though Spring beans don't need to follow the JavaBeans conventions strictly.

---

### 🔩 First Principles Explanation

**Problem — manual object graph assembly:**

A non-trivial application has hundreds of objects. Assembling them manually means either a massive `main()` method or scattered `new` calls throughout the codebase:

```java
// Manual assembly — fragile and not scalable
DataSource ds = new HikariDataSource(config);
UserRepository userRepo = new JpaUserRepository(em);
PasswordEncoder encoder = new BCryptPasswordEncoder();
UserService userService = new UserServiceImpl(userRepo, encoder);
EmailService emailService = new SmtpEmailService(smtpConfig);
AuthService authService = new AuthServiceImpl(
    userService, emailService, jwtConfig
);
// ... 200 more objects
```

**Constraint — objects need to share infrastructure:**

The same `DataSource` should be shared. The same `PasswordEncoder` instance for efficiency. Managing sharing manually requires global variables or complex factories.

**Insight — define objects declaratively, let the container manage them:**

```java
// Declare: Spring will build and wire everything
@Service
class AuthService {
  public AuthService(UserService users,
                     EmailService email,
                     JwtConfig jwt) {
    // Spring injects matching beans — no new needed
  }
}

// One shared DataSource bean, reused everywhere
@Bean
DataSource dataSource() {
  return HikariDataSource(config);
}
```

The container builds a dependency graph from these declarations and resolves the creation order automatically.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT Spring Beans:**

```
WITHOUT the Bean abstraction:

  Object creation scattered:
    Each class creates its own dependencies
    → same DataSource created 15 times
    → 15 separate connection pools → OOM

  No lifecycle management:
    Who calls init() on startup?
    Who calls close() on shutdown?
    → resource leaks in production

  AOP impossible:
    Can't intercept method calls on an object
    you created with new
    → @Transactional doesn't work on self-new'd objects

  Testing harder:
    Must wire the full object graph for every test
    → 1-second test startup for simple unit tests
```

**WITH Spring Beans:**

```
→ One DataSource bean shared by all 200 repositories
→ @PostConstruct and @PreDestroy called automatically
→ AOP proxy wraps beans transparently
  (@Transactional, @Cacheable, @Async all work)
→ Test: @MockBean or constructor injection for mocks
  → fast, isolated unit tests
→ Singleton scope: thread-safe shared instances
→ Prototype scope: fresh copy per injection point
```

---

### 🧠 Mental Model / Analogy

> A Spring Bean is like a **employee badge in a large company**. HR (the container) issues the badge when you join (bean creation), wires you into the org chart (dependency injection), gives you access rights (AOP proxy — @Transactional, security), and revokes the badge when you leave (bean destruction). You don't manage your own access cards — HR does. Any colleague who needs to collaborate with you just contacts HR and asks for your contact details (injection), rather than finding you themselves.

"HR issuing the badge" = container creating the bean
"Org chart wiring" = dependency injection between beans
"Access rights" = AOP proxy (transactions, security)
"Badge revocation on leaving" = @PreDestroy / destruction callbacks
"Colleague asking HR for contact" = @Autowired / constructor injection

---

### ⚙️ How It Works (Mechanism)

**Three ways to define a bean:**

```java
// 1. Stereotype annotation — component scan picks it up
@Service                // detected by @ComponentScan
public class UserService {
  private final UserRepository repo;
  public UserService(UserRepository repo) {
    this.repo = repo;
  }
}

// 2. @Bean factory method inside @Configuration
@Configuration
public class InfrastructureConfig {
  @Bean(destroyMethod = "close")  // called on shutdown
  public DataSource dataSource() {
    HikariDataSource ds = new HikariDataSource();
    ds.setJdbcUrl(env.getProperty("spring.datasource.url"));
    return ds;
  }
}

// 3. XML (legacy, rarely used in new code)
// <bean id="userService" class="com.app.UserService"/>
```

**Bean naming:**

```java
// Default name: first-letter-lowercase class name
@Service
class OrderService {}   // bean name: "orderService"

// Custom name
@Service("orders")
class OrderService {}   // bean name: "orders"

// @Bean method name IS the bean name
@Bean
DataSource primaryDataSource() {} // name: "primaryDataSource"
```

**Singleton vs prototype — the most important distinction:**

```
┌────────────────────────────────────────────────────────┐
│  DEFAULT BEAN BEHAVIOUR                                │
│                                                        │
│  @Scope("singleton") — ONE instance per container     │
│  Container creates it ONCE on startup                  │
│  All injection points get the SAME instance            │
│                                                        │
│  @Scope("prototype") — NEW instance per injection     │
│  Container creates a fresh copy every time            │
│  Container does NOT manage prototype lifecycle        │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
@Component / @Service / @Bean declaration
        ↓
  BEAN  ← you are here
  (managed object in ApplicationContext)
        ↓
  Has: Bean Lifecycle (init → use → destroy)
  Has: Bean Scope (singleton/prototype/request)
  Has: AOP Proxy wrapper (if needed)
        ↓
  Injected via: @Autowired / constructor injection
  Found via: ApplicationContext.getBean()
  Customised by: BeanPostProcessor
```

---

### 💻 Code Example

**Example 1 — Typical service bean with constructor injection:**

```java
@Service
@Slf4j
public class PaymentService {
  private final PaymentGateway gateway;
  private final AuditRepository audit;

  // Constructor injection — Spring detects single constructor
  public PaymentService(PaymentGateway gateway,
                        AuditRepository audit) {
    this.gateway = gateway;
    this.audit   = audit;
  }

  public Receipt charge(PaymentRequest request) {
    Receipt receipt = gateway.process(request);
    audit.record(receipt);
    return receipt;
  }
}
```

**Example 2 — Conditional bean with @ConditionalOnProperty:**

```java
@Configuration
public class PaymentConfig {
  // Only creates StripeGateway bean if property is set
  @Bean
  @ConditionalOnProperty("payment.provider.stripe.enabled")
  public PaymentGateway stripeGateway(
      StripeProperties props) {
    return new StripePaymentGateway(props.getApiKey());
  }

  // Fallback: in-memory stub for development/testing
  @Bean
  @ConditionalOnMissingBean(PaymentGateway.class)
  public PaymentGateway stubGateway() {
    return new InMemoryPaymentGateway();
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Spring Beans must follow JavaBeans conventions (no-arg constructor, getters/setters) | Spring beans can use any constructor, including ones with parameters. JavaBeans conventions are not required |
| All objects in a Spring app are beans | Value objects, DTOs, domain entities created with new are NOT beans — they're plain Java objects. Only objects needing container management are beans |
| Singleton bean means thread-safe | Singleton scope means one instance — but if the bean has mutable state accessed by multiple threads, it is NOT thread-safe. Design singleton beans as stateless |
| @Bean and @Component are equivalent | @Component is detected by classpath scan; @Bean is a factory method in a @Configuration class for programmatic control (useful for third-party classes) |

---

### 🔥 Pitfalls in Production

**1. Mutable state in singleton beans causes race conditions**

```java
// BAD: singleton bean with mutable state → race condition
@Service
class OrderProcessor {
  private Order currentOrder; // shared across all threads!

  public Result process(Order order) {
    this.currentOrder = order;  // Thread-A sets this
    validate();                 // Thread-B overwrites it!
    return calculate();         // Thread-A uses Thread-B's order
  }
}

// GOOD: stateless singleton — use method-local variables
@Service
class OrderProcessor {
  public Result process(Order order) {
    validate(order);   // passed as parameter
    return calculate(order);
  }
}
```

**2. Injecting prototype bean into singleton bean**

```java
// BAD: prototype injected once into singleton
// → effectively becomes a singleton
@Service   // singleton
class ReportService {
  @Autowired
  private ReportContext context; // @Scope("prototype")
  // context is injected ONCE at startup
  // All calls share the same context instance
}

// GOOD: use @Lookup or ObjectProvider for per-call prototype
@Service
class ReportService {
  @Autowired
  private ObjectProvider<ReportContext> contextProvider;

  public Report generate() {
    ReportContext ctx = contextProvider.getObject();
    // Fresh prototype instance every time
    return processReport(ctx);
  }
}
```

---

### 🔗 Related Keywords

- `IoC (Inversion of Control)` — the principle behind beans; container manages creation and wiring
- `ApplicationContext` — the container that holds, manages, and provides beans
- `Bean Lifecycle` — the full lifecycle of a bean from definition to destruction
- `Bean Scope` — controls how many instances the container creates (singleton, prototype, request)
- `@Autowired` — the primary injection mechanism for wiring beans together
- `BeanPostProcessor` — allows modification of bean instances after creation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ A Spring-managed Java object — created,   │
│              │ wired, and lifecycle-managed by container  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any application-layer object: services,   │
│              │ repos, controllers, infrastructure config  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Value objects, DTOs, domain entities      │
│              │ created transiently — use new for these   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A bean is any object Spring adopted —    │
│              │  it handles birth, life, and death."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bean Lifecycle → Bean Scope →             │
│              │ BeanPostProcessor                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application starts and creates 200 singleton beans. During startup, `BeanPostProcessor` implementations fire and can modify every bean. One `BeanPostProcessor` wraps `@Transactional` methods in a CGLIB proxy. Explain why `BeanPostProcessor` beans must be created *before* all other beans, what happens if a `@Configuration` class (that defines regular beans) is accidentally imported by a `BeanPostProcessor`, and what Spring's warning "BeanPostProcessorChecker" detects and why.

**Q2.** A REST endpoint handler method is annotated `@Scope("request")` on its controller bean. Explain what happens when the controller bean (request-scoped) is injected into a singleton-scoped service bean using regular constructor injection — why this breaks, what proxy injection mechanism Spring uses to solve it, and how that proxy works at the bytecode level (CGLIB or JDK proxy, and why).

