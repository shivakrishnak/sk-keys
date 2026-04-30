---
layout: default
title: "ApplicationContext"
parent: "Spring & Spring Boot"
nav_order: 105
permalink: /spring/application-context/
number: "105"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: IoC, Bean, BeanFactory, Dependency Injection
used_by: Bean Lifecycle, AOP Proxy, Spring MVC, Spring Boot, @EventListener
tags: #java, #spring, #springboot, #intermediate, #architecture
---

# 105 — ApplicationContext

`#java` `#spring` `#springboot` `#intermediate` `#architecture`

⚡ TL;DR — Spring's full-featured IoC container that holds all beans, wires them, publishes events, manages lifecycle, and integrates AOP, internationalisation, and resource loading.

| #105 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | IoC, Bean, BeanFactory, Dependency Injection | |
| **Used by:** | Bean Lifecycle, AOP Proxy, Spring MVC, Spring Boot, @EventListener | |

---

### 📘 Textbook Definition

The **ApplicationContext** is Spring's central IoC container — a superset of `BeanFactory` that adds enterprise features including event publication, declarative transaction support, AOP integration, internationalisation, and resource loading abstraction. It implements several interfaces simultaneously: `BeanFactory` (bean management), `MessageSource` (i18n), `ApplicationEventPublisher` (event bus), and `ResourcePatternResolver` (classpath/filesystem/URL resources). On startup, the context eagerly initialises all singleton beans, runs `BeanPostProcessor`s to apply AOP proxies, calls lifecycle callbacks, and publishes `ContextRefreshedEvent`. In Spring Boot, it is created and auto-configured by `SpringApplication.run()`.

---

### 🟢 Simple Definition (Easy)

The ApplicationContext is Spring's "main memory" — it holds every object (bean) your application needs, knows how they connect, and provides them on demand to any part of the app.

---

### 🔵 Simple Definition (Elaborated)

When your Spring application starts, the ApplicationContext is the first major thing created. It scans your codebase for annotated classes, reads configuration, creates all beans, connects them together, wraps them in AOP proxies for transactions and security, and keeps them alive for the application lifetime. Any code that needs another object asks the container — either through injection or (rarely) via `getBean()`. The ApplicationContext is also an event bus: beans can publish and subscribe to application events without coupling to each other directly.

---

### 🔩 First Principles Explanation

**The problem — who orchestrates the application?**

In a large application, hundreds of objects must be created, ordered, connected, and shut down cleanly. Without a central orchestrator:

- Who creates the `DataSource` before the `UserRepository`?
- Who calls `init()` on each component in the right order?
- Who closes connection pools on shutdown?
- Who creates AOP proxies for `@Transactional` methods?

**ApplicationContext vs BeanFactory:**

```
┌─────────────────────────────────────────────────────┐
│  APPLICATION CONTEXT = BEAN FACTORY +               │
│                                                     │
│  ✅ Eager singleton initialisation on startup       │
│  ✅ Automatic BeanPostProcessor registration        │
│  ✅ AOP proxy creation (via BPP)                    │
│  ✅ MessageSource (i18n text resolution)            │
│  ✅ ApplicationEventPublisher (decoupled events)    │
│  ✅ Environment (profiles, properties, secrets)     │
│  ✅ ResourceLoader (files, classpath, URLs)         │
│  ✅ ContextRefreshed/Closed lifecycle events        │
└─────────────────────────────────────────────────────┘
```

BeanFactory is lazy-init only with no events or AOP auto-application. Always use ApplicationContext in production.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT ApplicationContext:**

```
Without a central container:

  Bean wiring: manual factory code
    → Hundreds of new statements in main()
    → Dependency order resolved by hand
    → One missed dep → NullPointerException at runtime

  No @Transactional:
    Proxies require BeanPostProcessor
    → No container = no proxy = @Transactional does nothing

  No events:
    @EventListener impossible
    → Services call all listeners directly → tight coupling

  No profiles:
    Can't swap dev vs prod @Bean implementations
    → Hardcoded config, no environment separation
```

**WITH ApplicationContext:**

```
→ Fully wired beans on startup in correct order
→ @Transactional, @Async, @Cacheable all work
  (BeanPostProcessor creates AOP proxies)
→ Events: publish(new OrderPlaced(order))
  → zero coupling to subscribers
→ @Profile("prod"): different beans per environment
→ Graceful shutdown: context.close() calls
  all @PreDestroy and closes resource beans
```

---

### 🧠 Mental Model / Analogy

> The ApplicationContext is like a **city's civil infrastructure system**. Before citizens can live in the city, infrastructure is built: roads (wiring), utilities (shared DataSource beans), buildings (singleton beans). Each building connects to utilities automatically. The city has an emergency broadcast system (event publisher) and a building registry (bean registry). On shutdown, all utilities are properly turned off.

"Infrastructure built before citizens move in" = eager singleton init
"Roads connecting buildings" = dependency injection
"Shared utilities" = singleton beans (one DataSource for all repos)
"Emergency broadcast" = ApplicationEventPublisher
"Utilities off on shutdown" = @PreDestroy / ContextClosedEvent

---

### ⚙️ How It Works (Mechanism)

**Context startup sequence:**

```
┌─────────────────────────────────────────────────────┐
│  ApplicationContext STARTUP SEQUENCE                │
├─────────────────────────────────────────────────────┤
│  1. Parse @Configuration / classpath scan           │
│  2. Register BeanDefinitions (metadata, not beans)  │
│  3. Run BeanFactoryPostProcessors                   │
│     (PropertySourcesPlaceholderConfigurer, etc.)    │
│  4. Instantiate BeanPostProcessors (special order)  │
│  5. Eagerly instantiate all singleton beans:        │
│     a. Constructor injection                        │
│     b. Setter / field injection                     │
│     c. BPP.postProcessBefore (pre-init hooks)       │
│     d. @PostConstruct / afterPropertiesSet          │
│     e. BPP.postProcessAfter (AOP proxy here)        │
│  6. Publish ContextRefreshedEvent                   │
│  7. Application runs                                │
│  8. Shutdown: @PreDestroy, ContextClosedEvent       │
└─────────────────────────────────────────────────────┘
```

**Context implementations in Spring Boot:**

```java
// Spring Boot auto-selects based on classpath:
// Web MVC present → AnnotationConfigServletWebServerAppContext
// WebFlux present → AnnotationConfigReactiveWebServerAppContext
// None → AnnotationConfigApplicationContext

@SpringBootApplication
public class App {
  public static void main(String[] args) {
    // Returns ConfigurableApplicationContext
    ConfigurableApplicationContext ctx =
        SpringApplication.run(App.class, args);
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
IoC Principle (103) + DI Mechanism (104)
        ↓
  APPLICATION CONTEXT (105)  ← you are here
  (full IoC container — creates + wires + manages)
        │
        ├── bean registry: name → instance
        ├── fires: BeanPostProcessors
        │         (BPP creates AOP proxies)
        ├── publishes: ApplicationEvents
        └── provides: Environment / profiles
        ↓
  Used by everything:
  Spring MVC (124), @Transactional (127),
  Auto-Configuration (133), Actuator (134)
```

---

### 💻 Code Example

**Example 1 — ApplicationEvent for decoupled communication:**

```java
// Publisher — zero knowledge of who listens
@Service
public class UserRegistrationService {
  private final ApplicationEventPublisher events;

  public UserRegistrationService(
      ApplicationEventPublisher events) {
    this.events = events;
  }

  public User register(RegisterRequest req) {
    User user = createUser(req);
    events.publishEvent(new UserRegisteredEvent(user));
    return user;
  }
}

// Listeners — completely decoupled from publisher
@Component
class WelcomeEmailListener {
  @EventListener
  void onRegistered(UserRegisteredEvent e) {
    mailer.sendWelcome(e.getUser());
  }
}

@Component
class AnalyticsListener {
  @EventListener
  void onRegistered(UserRegisteredEvent e) {
    analytics.track("user.registered", e.getUser().getId());
  }
}
```

**Example 2 — Profile-based bean switching:**

```java
@Configuration
public class StorageConfig {
  @Bean
  @Profile("production")
  public FileStorage s3Storage(S3Properties props) {
    return new S3FileStorage(props.getBucket());
  }

  @Bean
  @Profile({"development", "test"})
  public FileStorage localStorage() {
    return new LocalFileStorage("/tmp/uploads");
  }
}
// spring.profiles.active=production → s3Storage created
// spring.profiles.active=test → localStorage created
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ApplicationContext and BeanFactory are interchangeable | BeanFactory is lazy-init only with no AOP auto-application or events. ApplicationContext adds critical enterprise features |
| getBean() is the recommended way to access beans | Direct getBean() is the Service Locator anti-pattern. Constructor injection is always preferred |
| The context is recreated per HTTP request | ApplicationContext is created once on startup and lives for the JVM lifetime. Request-scoped beans are proxied within the singleton context |
| Multiple ApplicationContexts are unusual | Spring MVC creates a child WebApplicationContext for the web layer — parent-child hierarchies are standard |

---

### 🔥 Pitfalls in Production

**1. Circular dependency on startup**

```java
// BeanCurrentlyInCreationException on startup
@Service class A { public A(B b) {...} }
@Service class B { public B(A a) {...} }
// Fix: redesign to remove cycle, or extract shared service
```

**2. @MockBean invalidating the test context cache**

```java
// BAD: different @MockBean per test class → new context each
@SpringBootTest
class TestA { @MockBean PaymentGateway pg; /* 5s start */ }
@SpringBootTest
class TestB { @MockBean EmailService es; /* 5s start again */ }

// GOOD: centralise all @MockBeans in a shared base class
@SpringBootTest
abstract class BaseIT {
  @MockBean PaymentGateway pg;
  @MockBean EmailService es;
  // All subclasses share ONE context → test suite 5× faster
}
```

---

### 🔗 Related Keywords

- `IoC` — the principle; ApplicationContext is its Spring implementation
- `BeanFactory` — the minimal parent interface; ApplicationContext extends it
- `Bean` — the objects ApplicationContext creates, manages, and provides
- `Bean Lifecycle` — the full initialisation and destruction sequence orchestrated by the context
- `BeanPostProcessor` — hooks fired by context to modify/proxy beans after creation
- `Spring Boot` — auto-creates and configures ApplicationContext via `SpringApplication.run()`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Central container: creates beans, wires   │
│              │ them, publishes events, manages lifecycle  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Inject ApplicationEventPublisher for      │
│              │ events; access Environment for profiles   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never use getBean() for normal access —   │
│              │ that's the Service Locator anti-pattern   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ApplicationContext is the city —         │
│              │  beans are the buildings it manages."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanFactory (106) → Bean Lifecycle (108)  │
│              │ → Auto-Configuration (133)                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot 3's AOT (Ahead-of-Time) compilation for GraalVM native images moves ApplicationContext startup work — bean discovery, condition evaluation, proxy generation — from runtime to build time. Explain what the ApplicationContext normally does at runtime startup that cannot happen in a GraalVM native image, why static analysis at build time cannot fully replicate dynamic classpath scanning, and what the `@ImportRuntimeHints` mechanism exists to solve.

**Q2.** `@SpringBootTest` caches the ApplicationContext between test classes to avoid repeated 3–5 second startup overhead. The cache key is based on the test configuration. Explain exactly what test-configuration elements invalidate the cache — listing at least four specific annotations or settings — and describe why a single out-of-place `@DirtiesContext(classMode = AFTER_CLASS)` in a commonly-extended base class can silently double the test suite runtime.

