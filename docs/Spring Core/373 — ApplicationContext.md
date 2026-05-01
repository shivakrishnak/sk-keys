---
layout: default
title: "ApplicationContext"
parent: "Spring Core"
nav_order: 373
permalink: /spring/application-context/
number: "373"
category: Spring Core
difficulty: ★★☆
depends_on: IoC (Inversion of Control), DI (Dependency Injection), BeanFactory
used_by: Spring Boot, Spring MVC, Bean Lifecycle, @SpringBootApplication
tags: #intermediate, #spring, #internals, #architecture
---

# 373 — ApplicationContext

`#intermediate` `#spring` `#internals` `#architecture`

⚡ TL;DR — `ApplicationContext` is Spring's full-featured IoC container: it manages beans, resolves dependencies, handles events, internalises messages, and integrates with AOP — all built on top of `BeanFactory`.

| #373            | Category: Spring Core                                              | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | IoC (Inversion of Control), DI (Dependency Injection), BeanFactory |                 |
| **Used by:**    | Spring Boot, Spring MVC, Bean Lifecycle, @SpringBootApplication    |                 |

---

### 📘 Textbook Definition

`ApplicationContext` is the central interface of the Spring Framework's IoC container, extending `BeanFactory` with enterprise-oriented features. Beyond bean instantiation and dependency injection, `ApplicationContext` provides: automatic `BeanPostProcessor` and `BeanFactoryPostProcessor` registration, application event publication and listener registration (`ApplicationEventPublisher`), message source for i18n (`MessageSource`), resource loading (`ResourceLoader`), and `Environment` / `@PropertySource` integration. In Spring Boot, the concrete implementation used is `AnnotationConfigServletWebServerApplicationContext` (for servlet-based apps) or `AnnotationConfigReactiveWebServerApplicationContext` (for reactive apps), bootstrapped by `SpringApplication.run()`. The context is a singleton per JVM process in standard usage, and its lifecycle spans the full application runtime.

---

### 🟢 Simple Definition (Easy)

`ApplicationContext` is the Spring container — the object that holds all your beans, wires their dependencies, and manages everything from startup to shutdown.

---

### 🔵 Simple Definition (Elaborated)

When a Spring Boot application starts, `SpringApplication.run()` creates an `ApplicationContext`. This context reads your `@Component`, `@Service`, `@Repository`, and `@Configuration` classes, instantiates beans in dependency order, injects their dependencies, runs post-processors (like AOP proxy creators), and makes every bean available for lookup. The context also handles: publishing application events (like `ApplicationReadyEvent`), resolving `@Value` and `@PropertySource` properties, exposing `Environment` (active profiles, configuration), and managing the graceful shutdown sequence. In daily Spring development, you rarely interact with `ApplicationContext` directly — Spring Boot wires everything automatically — but it is the central object every Spring feature ultimately depends on.

---

### 🔩 First Principles Explanation

**BeanFactory vs ApplicationContext — what extra features the context adds:**

```
BeanFactory (base interface)
  ├── getBean(name/type)    ← basic bean retrieval
  ├── containsBean(name)
  └── getBeanDefinition()

ApplicationContext (extends BeanFactory + adds):
  ├── ApplicationEventPublisher  ← publish/listen to events
  ├── MessageSource              ← i18n message resolution
  ├── ResourceLoader             ← classpath / file resource access
  ├── EnvironmentCapable         ← @Value, profiles, properties
  ├── BeanPostProcessor auto-reg ← AOP, @Autowired auto-registration
  └── BeanFactoryPostProcessor   ← @Configuration processing, etc.
```

**Why use ApplicationContext over BeanFactory directly:**

`BeanFactory` initialises beans lazily on first `getBean()` call, does NOT auto-register `BeanPostProcessor` instances, and does NOT publish container lifecycle events. In production, this means:

- `@Autowired` annotation processing does NOT happen automatically.
- `@PostConstruct` and `@PreDestroy` do NOT fire.
- AOP proxies are NOT created automatically.

`ApplicationContext` eagerly initialises all singleton beans at startup (detecting configuration errors early), auto-detects and registers all `BeanPostProcessor` and `BeanFactoryPostProcessor` beans, and publishes events.

**Concrete ApplicationContext implementations:**

```
AnnotationConfigApplicationContext        ← Java config / @ComponentScan
ClassPathXmlApplicationContext            ← XML config
GenericWebApplicationContext              ← Web, programmatic
AnnotationConfigServletWebServer...       ← Spring Boot MVC
AnnotationConfigReactiveWebServer...      ← Spring Boot WebFlux
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT ApplicationContext (using BeanFactory only):

What breaks without it:

1. `BeanPostProcessor` beans are NOT auto-detected — `@Autowired`, `@PostConstruct`, `@PreDestroy` do NOT work without manual registration.
2. AOP proxies (and therefore `@Transactional`, `@Cacheable`, `@Async`) do NOT work.
3. Application events cannot be published or received.
4. `@Value("${property}")` property injection does NOT work.
5. Profile-based conditional configuration does NOT activate.

WITH ApplicationContext:
→ All `BeanPostProcessor` and `BeanFactoryPostProcessor` implementations are auto-detected from the bean registry.
→ The entire AOP proxy infrastructure (`AnnotationAwareAspectJAutoProxyCreator`) is set up automatically.
→ Properties from `application.properties`, environment variables, and system properties are unified under `Environment`.
→ Application events (`ApplicationReadyEvent`, `ContextRefreshedEvent`, `ContextClosedEvent`) fire at lifecycle milestones.

---

### 🧠 Mental Model / Analogy

> Think of `ApplicationContext` as a fully-staffed company headquarters, and `BeanFactory` as an empty building with just a reception desk. The reception desk can tell you where someone's office is (getBean). The full headquarters adds: an HR department (BeanPostProcessors auto-registering), an events calendar (ApplicationEventPublisher), an intercom system (MessageSource/i18n), a facilities manager who knows about every resource (ResourceLoader), and a people directory (Environment/properties). Spring Boot's auto-configuration fills the entire building with the right departments on startup.

"Reception desk only" = BeanFactory (basic bean lookup)
"Full headquarters" = ApplicationContext with all enterprise features
"HR department" = BeanPostProcessor auto-registration
"Events calendar" = ApplicationEventPublisher
"Intercom / messaging" = MessageSource (i18n)
"Filling the building on startup" = Spring Boot auto-configuration bootstrapping the ApplicationContext

---

### ⚙️ How It Works (Mechanism)

**ApplicationContext startup sequence:**

```
┌──────────────────────────────────────────────┐
│   ApplicationContext Refresh Sequence         │
│                                              │
│  1. prepareRefresh()                         │
│     — validate environment, init listeners   │
│           ↓                                  │
│  2. obtainFreshBeanFactory()                 │
│     — load BeanDefinitions from config       │
│           ↓                                  │
│  3. prepareBeanFactory()                     │
│     — register built-in post-processors      │
│           ↓                                  │
│  4. postProcessBeanFactory()                 │
│     — subclass hook (web: register scope)    │
│           ↓                                  │
│  5. invokeBeanFactoryPostProcessors()        │
│     — run @Configuration, @PropertySource   │
│           ↓                                  │
│  6. registerBeanPostProcessors()             │
│     — register AOP creator, @Autowired proc  │
│           ↓                                  │
│  7. initMessageSource()                      │
│  8. initApplicationEventMulticaster()        │
│           ↓                                  │
│  9. onRefresh()                              │
│     — start embedded web server (Boot)       │
│           ↓                                  │
│  10. registerListeners()                     │
│           ↓                                  │
│  11. finishBeanFactoryInitialization()       │
│     — eagerly instantiate all singletons     │
│           ↓                                  │
│  12. finishRefresh()                         │
│     — publish ContextRefreshedEvent          │
└──────────────────────────────────────────────┘
```

**Accessing ApplicationContext from within the application:**

```java
// Option 1: Inject it (rarely needed — usually over-engineering)
@Service
class ConfigDumper {
    private final ApplicationContext ctx;

    ConfigDumper(ApplicationContext ctx) { this.ctx = ctx; }

    void listBeans() {
        Arrays.stream(ctx.getBeanDefinitionNames())
              .forEach(System.out::println);
    }
}

// Option 2: Implement ApplicationContextAware
@Component
class AppContextHolder implements ApplicationContextAware {
    private static ApplicationContext context;

    @Override
    public void setApplicationContext(ApplicationContext ctx) {
        AppContextHolder.context = ctx;
    }

    public static <T> T getBean(Class<T> type) {
        return context.getBean(type);
    }
}
// Use sparingly — prefer direct injection; this is a Service Locator pattern
```

---

### 🔄 How It Connects (Mini-Map)

```
BeanFactory
(base container — lazy, no auto-processing)
        │  ← extended by →
        ▼
ApplicationContext  ◄──── (you are here)
        │
        ├───────────────────────────────────────┐
        ▼                                       ▼
Bean Lifecycle                     ApplicationEventPublisher
(eager singleton init, callbacks)  (events: Ready, Refresh, Close)
        │                                       │
        ▼                                       ▼
BeanPostProcessor                   Environment / @Value
(AOP, @Autowired wiring)            (properties, profiles)
        │
        ▼
Spring Boot (@SpringBootApplication)
(auto-configures and starts the context)
```

---

### 💻 Code Example

**Example 1 — Application events via ApplicationContext:**

```java
// Publish a custom event
@Service
class OrderService {
    private final ApplicationEventPublisher eventPublisher;

    OrderService(ApplicationEventPublisher publisher) {
        this.eventPublisher = publisher;
    }

    void placeOrder(Order order) {
        orderRepo.save(order);
        eventPublisher.publishEvent(new OrderPlacedEvent(order)); // async-capable
    }
}

// Listen to the event — decoupled from OrderService
@Component
class EmailNotificationListener {
    @EventListener
    void onOrderPlaced(OrderPlacedEvent event) {
        emailService.sendConfirmation(event.getOrder());
    }
}
// OrderService has no reference to EmailNotificationListener — loose coupling
```

**Example 2 — Context lifecycle events for startup / shutdown hooks:**

```java
@Component
class StartupTask implements ApplicationListener<ApplicationReadyEvent> {
    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        // Runs AFTER all beans are initialised and the server is ready
        System.out.println("App ready. Beans: "
            + event.getApplicationContext().getBeanDefinitionCount());
    }
}

@Component
class ShutdownTask {
    @PreDestroy
    void onShutdown() {
        // Runs when context closes (graceful shutdown)
        System.out.println("Shutting down — releasing resources");
    }
}
```

**Example 3 — Profile-based bean selection via ApplicationContext:**

```java
@Configuration
class DataSourceConfig {
    @Bean
    @Profile("prod")
    DataSource productionDataSource() {
        return new HikariDataSource(prodConfig());
    }

    @Bean
    @Profile("test")
    DataSource testDataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2).build();
    }
}
// ApplicationContext reads active profile from environment
// and registers only the matching DataSource bean
```

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ApplicationContext` is created once globally and is always the same type  | In tests (`@SpringBootTest`, `@WebMvcTest`), Spring creates separate, isolated contexts per test class. In multi-module apps, parent/child context hierarchies can exist (e.g., Spring MVC's DispatcherServlet has a child context of the root context)             |
| All beans are created lazily in ApplicationContext                         | `ApplicationContext` eagerly creates all singleton beans during `refresh()`. Prototype beans and `@Lazy` beans are created on first request. Lazy initialisation of ALL beans can be enabled with `spring.main.lazy-initialization=true` but delays error detection |
| You should inject `ApplicationContext` whenever you need beans dynamically | This is the Service Locator anti-pattern. Inject `ApplicationContext` only when you genuinely need dynamic bean lookup (e.g., plugin systems, strategy registries). For most cases, inject the specific dependency type directly                                    |
| `ContextRefreshedEvent` fires only once at startup                         | `ContextRefreshedEvent` fires every time `refresh()` is called. In tests, it can fire multiple times. Use `ApplicationReadyEvent` (Spring Boot) for one-time post-startup logic                                                                                     |

---

### 🔥 Pitfalls in Production

**Bean count growing unbounded — context memory leak via dynamic context creation**

```java
// BAD: creating a new ApplicationContext per request or task
// (seen in multi-tenant systems where devs try to isolate tenants)
@RequestMapping("/process")
void process(String tenantId) {
    SpringApplication app = new SpringApplication(TenantConfig.class);
    ConfigurableApplicationContext ctx = app.run(); // NEW context per request!
    ctx.getBean(TenantService.class).process(tenantId);
    // ctx.close() often forgotten → memory + thread leak
}
// Each new context creates 50+ background threads and holds all bean memory

// GOOD: use a single shared context with tenant-scoped beans or
// use a strategy registry pattern keyed by tenantId
```

---

**Accessing a bean before the context is fully refreshed — NullPointerException**

```java
// BAD: accessing a Spring bean in a static initialiser block
// Static blocks run when the class is loaded, potentially before Spring is ready
public class AppConstants {
    static final String CONFIG_VALUE;
    static {
        // ApplicationContext may not exist yet!
        CONFIG_VALUE = SpringContext.getBean(ConfigService.class).getValue();
        // NPE or IllegalStateException if context not yet initialised
    }
}

// GOOD: inject the value into a Spring-managed bean at construction time
@Component
class AppConstants {
    final String configValue;
    AppConstants(ConfigService config) {
        this.configValue = config.getValue(); // safe: Spring injects after context is ready
    }
}
```

---

### 🔗 Related Keywords

- `BeanFactory` — the parent interface; `ApplicationContext` extends it with enterprise features
- `Bean Lifecycle` — the sequence managed by `ApplicationContext` from instantiation to destruction
- `BeanPostProcessor` — post-processors auto-detected and registered by `ApplicationContext`
- `IoC (Inversion of Control)` — the principle `ApplicationContext` implements as Spring's IoC container
- `Spring Boot Startup Lifecycle` — how `SpringApplication.run()` bootstraps and refreshes the `ApplicationContext`
- `@SpringBootApplication` — the meta-annotation that triggers component scanning and auto-configuration of the `ApplicationContext`
- `ApplicationEventPublisher` — the interface embedded in `ApplicationContext` for the event publication mechanism

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Full-featured IoC container: beans +      │
│              │ events + properties + AOP + i18n          │
├──────────────┼───────────────────────────────────────────┤
│ VS FACTORY   │ BeanFactory: lazy init, no auto-processing│
│              │ ApplicationContext: eager + all features  │
├──────────────┼───────────────────────────────────────────┤
│ EVENTS       │ ContextRefreshedEvent, ApplicationReady,  │
│              │ ContextClosedEvent, custom events         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ApplicationContext is Spring's brain:    │
│              │ wires, manages, and orchestrates all      │
│              │ beans from birth to death."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bean Lifecycle → BeanPostProcessor →      │
│              │ Auto-Configuration → Spring Boot Startup  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application uses `@SpringBootTest` for integration tests. The test suite has 15 test classes, each testing a different slice of functionality but all loading the full application context. The test suite takes 8 minutes to run. A colleague suggests adding `@DirtiesContext` to every test class to ensure isolation. Explain why this makes the problem worse, describe exactly what Spring does to cache and reuse `ApplicationContext` instances across tests, and propose a strategy that achieves test isolation without rebuilding the context 15 times.

**Q2.** Spring MVC traditionally uses a parent-child ApplicationContext hierarchy: the root context (loaded by `ContextLoaderListener`) contains services and repositories; the DispatcherServlet has a child context containing controllers and view resolvers. The child context can see parent beans, but the parent cannot see child beans. Explain why this hierarchy was introduced historically, describe a specific production bug that occurs when a service annotated with `@Transactional` is declared in the child (DispatcherServlet) context instead of the root context, and explain why Spring Boot eliminates this hierarchy by default.
