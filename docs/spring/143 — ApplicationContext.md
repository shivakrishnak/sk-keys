---
layout: default
title: "ApplicationContext"
parent: "Spring & Spring Boot"
nav_order: 143
permalink: /spring/application-context/
number: "143"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: IoC, Bean, BeanFactory, Dependency Injection
used_by: Bean Lifecycle, AOP Proxy, Spring MVC, Spring Boot, EventPublisher
tags: #java, #spring, #springboot, #intermediate, #architecture
---

# 143 — ApplicationContext

`#java` `#spring` `#springboot` `#intermediate` `#architecture`

⚡ TL;DR — Spring's full-featured IoC container that holds all beans, wires them, publishes events, manages lifecycle, and integrates AOP, internationalisation, and resource loading.

| #143 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | IoC, Bean, BeanFactory, Dependency Injection | |
| **Used by:** | Bean Lifecycle, AOP Proxy, Spring MVC, Spring Boot, EventPublisher | |

---

### 📘 Textbook Definition

The **ApplicationContext** is Spring's central IoC container — a superset of `BeanFactory` that adds enterprise features including event publication, declarative transaction management, AOP integration, internationalisation support, and resource loading abstraction. It implements the `ApplicationContext` interface (which extends `BeanFactory`, `MessageSource`, `ApplicationEventPublisher`, and `ResourcePatternResolver`). The context eagerly initialises all singleton beans on startup, runs `BeanPostProcessor`s, applies AOP proxies, calls lifecycle callbacks, and publishes lifecycle events (`ContextRefreshedEvent`, `ContextClosedEvent`). In Spring Boot, it is created and configured automatically by `SpringApplication.run()`.

---

### 🟢 Simple Definition (Easy)

The ApplicationContext is Spring's "main memory" — it holds every object (bean) your application needs, knows how they connect to each other, and provides them on demand.

---

### 🔵 Simple Definition (Elaborated)

When your Spring application starts, the ApplicationContext is the first major thing created. It scans your codebase for annotated classes, reads configuration, creates all the beans, connects them together, wraps them in proxies for transactions and security, and then keeps them all alive for the duration of the application. Any part of your code that needs another object asks the container — either explicitly via `getBean()` or implicitly via injection. The ApplicationContext is also an event bus: beans can publish and subscribe to application events through it.

---

### 🔩 First Principles Explanation

**The problem — who orchestrates the application?**

In a large application, hundreds of objects must be created, configured, wired, and shut down cleanly. Without a central orchestrator:

```
Without ApplicationContext:

  Startup: who creates what in what order?
  DataSource created before UserRepo? Or after?
  Who calls init() on each? In what sequence?

  Wiring: who connects them?
  UserService needs UserRepo, PasswordEncoder, MailService
  → must be assembled somewhere → main() becomes 500 lines

  Shutdown: who cleans up?
  Connection pools must close, threads must stop
  → manual Runtime.getRuntime().addShutdownHook() everywhere

  AOP: who wraps @Transactional methods in proxies?
  → can't happen without a managed container
```

**The BeanFactory vs ApplicationContext distinction:**

`BeanFactory` is the minimal container — lazy instantiation, no AOP, no events. `ApplicationContext` extends it with:

```
┌─────────────────────────────────────────────────────┐
│  ApplicationContext = BeanFactory +                 │
│                                                     │
│  ✅ Eager singleton initialisation on startup       │
│  ✅ BeanPostProcessor auto-registration             │
│  ✅ AOP proxy auto-application                      │
│  ✅ MessageSource (i18n)                            │
│  ✅ ApplicationEventPublisher (event bus)           │
│  ✅ ResourceLoader (classpath, filesystem, URL)     │
│  ✅ Environment abstraction (profiles, properties)  │
│  ✅ ContextRefreshed / ContextClosed lifecycle hooks│
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT ApplicationContext:**

```
Without a central container:

  Bean wiring: you write the factory code manually
    → Hundreds of new statements
    → Dependency order resolved by you
    → One missed dependency → NullPointerException at runtime

  No @Transactional:
    Transaction proxies are created by BeanPostProcessor
    → No container = No BeanPostProcessor
    → @Transactional is just a comment — does nothing

  No events:
    @EventListener / ApplicationEvent impossible
    → Each service must directly call all listeners
    → Tight coupling between event producers and consumers

  No profiles:
    Can't swap dev vs prod configuration
    → Hardcoded config values everywhere
```

**WITH ApplicationContext:**

```
→ Fully wired application graph on startup
→ @Transactional, @Async, @Cacheable all work
  (via BeanPostProcessor + AOP proxy)
→ Publishing events: userService.publish(new UserCreated())
  → zero coupling to subscribers
→ @Profile("prod") / @Profile("dev") beans
  → different beans for different environments
→ Graceful shutdown: context.close() calls all
  @PreDestroy methods and closes resource beans
```

---

### 🧠 Mental Model / Analogy

> The ApplicationContext is like a **city's civil infrastructure system**. Before citizens can live in the city, the infrastructure is built: roads (wiring), utilities (shared services like DataSource), buildings (singleton beans). Each building is connected to utilities automatically. The city also has an emergency broadcast system (event publisher) and a registry of all buildings (bean registry). When the city shuts down, all utilities are properly turned off (shutdown hooks).

"City infrastructure built before citizens move in" = eager singleton init on startup
"Roads connecting buildings" = dependency injection wiring
"Utilities shared across all buildings" = singleton scoped beans
"Emergency broadcast" = ApplicationEventPublisher
"City registry" = bean registry (getBean by name/type)
"Utilities turned off on shutdown" = @PreDestroy / ContextClosedEvent

---

### ⚙️ How It Works (Mechanism)

**Context initialization sequence:**

```
┌─────────────────────────────────────────────────────┐
│  ApplicationContext STARTUP SEQUENCE                │
├─────────────────────────────────────────────────────┤
│  1. Parse configuration (annotations / XML)         │
│  2. Register BeanDefinitions                        │
│     (metadata — not instances yet)                  │
│  3. Run BeanFactoryPostProcessors                   │
│     (e.g. PropertySourcesPlaceholderConfigurer)     │
│  4. Instantiate BFPP-required beans                 │
│  5. Instantiate BeanPostProcessors                  │
│  6. Instantiate ALL singleton beans (eager)         │
│     For each bean:                                  │
│     a. Constructor injection                        │
│     b. Setter injection                             │
│     c. BeanPostProcessor.postProcessBefore*         │
│     d. @PostConstruct / InitializingBean.afterProps │
│     e. BeanPostProcessor.postProcessAfter*          │
│        (AOP proxy created here if needed)           │
│  7. Publish ContextRefreshedEvent                   │
│  8. Application runs...                             │
│  9. On shutdown: @PreDestroy, ContextClosedEvent    │
└─────────────────────────────────────────────────────┘
```

**ApplicationContext implementations:**

```java
// Spring Boot: auto-configured
@SpringBootApplication
public class App {
  public static void main(String[] args) {
    // Returns ConfigurableApplicationContext
    var ctx = SpringApplication.run(App.class, args);
    // ctx is a AnnotationConfigServletWebServerAppContext
    // or AnnotationConfigReactiveWebServerAppContext
    // depending on classpath
  }
}

// Standalone (non-Boot):
ApplicationContext ctx =
    new AnnotationConfigApplicationContext(AppConfig.class);

// With profiles active:
AnnotationConfigApplicationContext ctx =
    new AnnotationConfigApplicationContext();
ctx.getEnvironment().setActiveProfiles("production");
ctx.register(AppConfig.class);
ctx.refresh();
```

**Accessing the context (rarely needed directly):**

```java
// PREFER: constructor injection over direct context access
@Service
class MyService implements ApplicationContextAware {
  private ApplicationContext ctx;

  @Override
  public void setApplicationContext(ApplicationContext ctx) {
    this.ctx = ctx; // injected by Spring
  }

  // Use ctx only for runtime dynamic bean lookup
  public void doWork(String beanName) {
    Object bean = ctx.getBean(beanName); // dynamic lookup
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
@SpringBootApplication / @Configuration
(defines the application configuration)
        ↓
  APPLICATIONCONTEXT  ← you are here
  (full IoC container)
        │
        ├── holds: Bean registry (name → instance)
        ├── fires: BeanPostProcessors (AOP, etc.)
        ├── publishes: ApplicationEvents
        ├── provides: Environment (profiles, props)
        └── manages: Lifecycle (start, stop, destroy)
        ↓
  Provides beans to:
  @Autowired injection points
  Spring MVC web layer
  @Transactional, @Async, @Cacheable aspects
```

---

### 💻 Code Example

**Example 1 — ApplicationEvent and @EventListener:**

```java
// Publishing an event — zero coupling to listener
@Service
public class UserRegistrationService {
  private final ApplicationEventPublisher events;

  public UserRegistrationService(
      ApplicationEventPublisher events) {
    this.events = events;
  }

  public User register(RegisterRequest req) {
    User user = createUser(req);
    // Publisher doesn't know about EmailService, etc.
    events.publishEvent(new UserRegisteredEvent(user));
    return user;
  }
}

// Listener — completely decoupled from publisher
@Component
public class WelcomeEmailListener {
  @EventListener
  public void onUserRegistered(UserRegisteredEvent e) {
    emailService.sendWelcome(e.getUser());
  }
}
```

**Example 2 — Profile-based bean selection:**

```java
@Configuration
public class StorageConfig {
  @Bean
  @Profile("production")
  public FileStorage s3Storage(S3Properties props) {
    return new S3FileStorage(props);
  }

  @Bean
  @Profile({"development", "test"})
  public FileStorage localStorage() {
    return new LocalFileStorage("/tmp/uploads");
  }
}
// Active profile: spring.profiles.active=production
// → S3FileStorage bean; LocalFileStorage never created
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ApplicationContext and BeanFactory are interchangeable | BeanFactory is lazy-init only, no events, no AOP auto-application. Always use ApplicationContext in production |
| Context.getBean() is the right way to access beans | Direct getBean() is the Service Locator anti-pattern. Prefer constructor injection always — getBean() is for dynamic/runtime lookup only |
| ApplicationContext is recreated per request | The ApplicationContext is created once on startup and lives for the entire JVM lifetime. A new context is only created in tests |
| Child contexts are unusual | Spring MVC creates a child ApplicationContext for the web layer (DispatcherServlet). Parent-child hierarchy is common in large applications |

---

### 🔥 Pitfalls in Production

**1. Circular dependency causing startup failure**

```java
// BAD: A depends on B, B depends on A
// → ContextRefresh fails with BeanCurrentlyInCreationException
@Service class OrderService {
  public OrderService(PaymentService p) {...}
}
@Service class PaymentService {
  public PaymentService(OrderService o) {...}
}

// GOOD: extract shared logic, or use @Lazy
@Service class OrderService {
  public OrderService(
      @Lazy PaymentService p) {...} // breaks cycle
}
// Better: redesign to remove the cycle entirely
```

**2. Context loading in tests recreating the context per class**

```java
// BAD: new context for every test class → slow test suite
// (if each test class has different @MockBean config)
@SpringBootTest
@MockBean PaymentGateway mockGateway // different beans
class TestA { ... }

@SpringBootTest
@MockBean EmailService mockEmail  // different beans
class TestB { ... }
// Each @MockBean change invalidates the context cache
// → 2 context loads (each 3-5 sec for a large app)

// GOOD: centralise @MockBean into a shared base class
@SpringBootTest
abstract class IntegrationTestBase {
  @MockBean PaymentGateway gateway;
  @MockBean EmailService email;
}
// All tests share ONE context → test suite 5× faster
```

---

### 🔗 Related Keywords

- `IoC` — the principle; ApplicationContext is the Spring IoC container implementation
- `Bean` — the objects ApplicationContext creates, manages, and provides
- `Bean Lifecycle` — the full initialisation and destruction cycle managed by ApplicationContext
- `BeanPostProcessor` — hooks into context startup to modify or proxy beans
- `@EventListener` — subscribes to ApplicationEvents published through the context
- `Spring Boot` — auto-creates and configures ApplicationContext via SpringApplication.run()

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Central Spring container: creates beans,  │
│              │ wires them, publishes events, manages life │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Accessing event publisher, profiles,      │
│              │ dynamic bean lookup (avoid if possible)   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use getBean() directly — prefer     │
│              │ constructor injection at all times        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ApplicationContext is the city —         │
│              │  beans are the buildings it manages."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanPostProcessor → Bean Lifecycle →      │
│              │ Spring Boot Auto-Configuration            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot applications with many beans can take 3–8 seconds to start. The startup sequence involves parsing BeanDefinitions, running BeanFactoryPostProcessors, and eagerly initialising all singletons. Spring Framework 6 / Spring Boot 3 introduced AOT (Ahead-of-Time) compilation for GraalVM native images. Explain what AOT compilation does at the ApplicationContext level — specifically, what traditionally happens at runtime that AOT moves to build time — and what categories of runtime Spring behaviour (e.g. reflection, dynamic proxy creation, classpath scanning) are problematic for GraalVM native and why.

**Q2.** A Spring Boot application uses `@SpringBootTest` for integration tests. The ApplicationContext is cached between tests by the Spring TestContext Framework. However, after a `@DirtiesContext` annotation, the context is destroyed and recreated. Trace exactly what happens during context destruction (ContextClosedEvent, DisposableBean, @PreDestroy, connection pool shutdown) and reconstruction — and explain the specific scenario where a test that doesn't use `@DirtiesContext` still causes the next test's context to be a fresh instance despite caching.

