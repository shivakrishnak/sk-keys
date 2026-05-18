---
version: 1
layout: default
title: "Spring Boot Startup Lifecycle"
parent: "Spring Core"
grand_parent: "Technical Mastery"
nav_order: 71
permalink: /technical-mastery/spring/spring-boot-startup-lifecycle/
id: SPR-009
category: Spring Core
difficulty: ★★★
depends_on: ApplicationContext, Bean Lifecycle, Auto-Configuration
used_by: Diagnostics, Startup Optimization, ApplicationRunner
related: ApplicationRunner, CommandLineRunner, SmartLifecycle
tags:
  - spring
  - springboot
  - internals
  - deep-dive
---

⚡ TL;DR - Spring Boot startup follows a precise sequence: load environment → create ApplicationContext → refresh (register beans, run auto-config, inject dependencies) → call runners - understanding each phase lets you diagnose startup failures and optimize cold-start time.

| #403            | Category: Spring Core                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | ApplicationContext, Bean Lifecycle, Auto-Configuration |                 |
| **Used by:**    | Diagnostics, Startup Optimization, ApplicationRunner   |                 |
| **Related:**    | ApplicationRunner, CommandLineRunner, SmartLifecycle   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Spring Boot application takes 30 seconds to start. The team has no idea which phase is slow. Is it loading properties? Scanning the classpath? Initializing JPA? Running migrations? The startup log shows thousands of lines with no clear phase boundaries. When a startup exception occurs - `BeanCreationException` in the middle of auto-configuration - the stack trace is 40 frames deep into Spring internals, and it's unclear whether the failure is in the bean's constructor, `@PostConstruct`, or an auto-configuration condition.

**THE BREAKING POINT:**
In Kubernetes, slow startup equals slow deployments and flapping pods. In Lambda, startup time is user-facing latency. Without understanding the lifecycle phases, optimization is guesswork and debugging is a full-day exercise.

**THE INVENTION MOMENT:**
"This is exactly why understanding the Spring Boot startup lifecycle is critical."

---

### 📘 Textbook Definition

The **Spring Boot startup lifecycle** is the ordered sequence of phases that execute when `SpringApplication.run()` is called until the application is ready to serve traffic. The main phases are: (1) `SpringApplication` initialization - configure environment, load `ApplicationContextInitializer`s, detect web application type; (2) ApplicationContext creation - instantiate the correct context type (`AnnotationConfigServletWebServerApplicationContext` for web apps); (3) ApplicationContext refresh - register bean definitions, apply `BeanFactoryPostProcessor`s, instantiate all singleton beans, apply auto-configuration, start embedded server; (4) Application runners - execute `ApplicationRunner` and `CommandLineRunner` beans after context is fully initialized; (5) `ApplicationReadyEvent` published - application is live. Each phase is extensible via listener interfaces.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Spring Boot startup is a pipeline: configure → create context → refresh (build all beans) → run startup code → go live.

**One analogy:**

> Starting a Spring Boot app is like opening a restaurant each day: prep the kitchen (load environment/properties) → hire staff (register bean definitions) → train and equip staff (inject dependencies, run @PostConstruct) → open the doors (start embedded Tomcat) → greet first customers (run ApplicationRunner code) → fully open (ApplicationReadyEvent).

**One insight:**
The `refresh()` phase is 80% of startup time and where most failures occur. Understanding it is the difference between reading a stack trace and understanding it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Bean definitions are registered before any beans are instantiated - the two-phase design (define then create) allows BeanFactoryPostProcessors to modify definitions before creation.
2. All singleton beans are fully created and their dependencies injected before the embedded web server starts accepting requests.
3. `ApplicationRunner` and `CommandLineRunner` beans execute after the context is fully refreshed but before `ApplicationReadyEvent` - they're the hook for "startup initialization" code (e.g., cache warm-up).

**DERIVED DESIGN:**
The two-phase design (define → instantiate) solves the bootstrapping problem: how can bean B declare that it depends on bean A if A hasn't been created yet? By separating definition (which describes the dependency graph) from instantiation (which resolves it), Spring can build the full dependency graph as a DAG and instantiate beans in topological order.

The `BeanFactoryPostProcessor` phase between definition and instantiation is critical - this is when auto-configuration conditions are evaluated (which bean definitions to add), when `@Value` placeholders are resolved, and when `@ConfigurationProperties` are bound.

**THE TRADE-OFFS:**

**Gain:** Predictable startup sequence; well-defined extension points; fail-fast behavior (missing dependencies fail at startup).

**Cost:** All complexity of dependency resolution, proxy generation, and auto-configuration conditions happens at startup - the cost is front-loaded; lazy initialization is the opt-in alternative.

---

### 🧪 Thought Experiment

**SETUP:**
You add a `@PostConstruct` method to a `@Service` class that calls another `@Service` bean's method. That other service's `@PostConstruct` hasn't run yet. What happens?

**TRACE THE LIFECYCLE:**
Spring instantiates ServiceA. Injects its dependencies (ServiceB is injected). Calls ServiceA's `@PostConstruct`. Inside `@PostConstruct`, you call `serviceB.doSomething()`. ServiceB has already been constructed (it was injected), but its `@PostConstruct` may not have run yet - Spring processes `@PostConstruct` methods one bean at a time during initialization. Calling into a bean whose lifecycle initialization isn't complete creates subtle ordering bugs.

**THE INSIGHT:**
`@PostConstruct` is for self-initialization only. Cross-bean coordination during startup belongs in `ApplicationRunner`/`CommandLineRunner`, which run after ALL beans are fully initialized.

---

### 🧠 Mental Model / Analogy

> Spring Boot startup is like building a house. First the architect draws the blueprint (register BeanDefinitions). Then the inspector reviews and approves plans - maybe adds required items (BeanFactoryPostProcessors, auto-config). Then construction happens in dependency order: foundation before walls, walls before roof (instantiate beans in topological order). Fixtures go in last (inject dependencies, @PostConstruct). Then the homeowner moves in and arranges furniture (ApplicationRunner). Then the house is open for guests (ApplicationReadyEvent).

- "Blueprint" → BeanDefinition
- "Inspector reviewing plans" → BeanFactoryPostProcessor (including auto-config)
- "Construction in dependency order" → singleton instantiation in topological sort order
- "Fixtures" → `@Autowired` injection, `@PostConstruct`
- "Homeowner arranges furniture" → `ApplicationRunner.run()`
- "Open for guests" → `ApplicationReadyEvent`, embedded server serving traffic

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you run a Spring Boot app, it goes through several ordered steps: reading configuration, setting up all your service classes, starting the web server, running any startup code you wrote, then opening for requests. Each step must complete before the next begins.

**Level 2 - How to use it (junior developer):**
Use `@PostConstruct` for initialization within a single bean after its dependencies are injected. Use `ApplicationRunner` (preferred) or `CommandLineRunner` for startup code that needs the full application context to be ready (cache loading, schema migration verification, external service handshakes). Listen to `ApplicationReadyEvent` for code that should run only after the embedded web server is accepting requests.

**Level 3 - How it works (mid-level engineer):**
`SpringApplication.run()` creates a `SpringApplicationRunListeners` and publishes events at each lifecycle phase. The `prepareContext()` method runs `ApplicationContextInitializer`s. The `refreshContext()` call delegates to `AbstractApplicationContext.refresh()` which: calls `invokeBeanFactoryPostProcessors()` (loads auto-config conditions, resolves placeholders), then `finishBeanFactoryInitialization()` (instantiates all non-lazy singletons in dependency order). After refresh, `callRunners()` invokes all `ApplicationRunner` and `CommandLineRunner` beans ordered by `@Order`. The embedded `WebServer` starts inside `refresh()` via `ServletWebServerApplicationContext.createWebServer()`, before runners execute.

**Level 4 - Why it was designed this way (senior/staff):**
The separation of `BeanFactoryPostProcessor` (modifies bean definitions) from `BeanPostProcessor` (modifies bean instances) is a key design decision. BFPPs run before any beans are created, allowing auto-configuration to add or modify bean definitions before instantiation. BPPs run after each bean is created, enabling proxy generation (AOP, `@Transactional`, `@Async`). The embedded server starting inside `refresh()` before runners is intentional - runners may need to make HTTP calls to themselves (e.g., warming up the embedded server's thread pool). Spring Boot 2.4 changed `spring.config.import` loading order and broke some applications because config loading sequence is precisely ordered and order-dependent - a reminder that the lifecycle is a contract.

---

### ⚙️ How It Works (Mechanism)

```
SpringApplication.run(args)
│
├─1. Create SpringApplication
│     ├── Detect web app type (NONE/SERVLET/REACTIVE)
│     ├── Load ApplicationContextInitializers
  (spring.factories)
│     └── Load SpringApplicationRunListeners
│
├─2. prepareEnvironment()
│     ├── Load application.properties / .yml
│     ├── Process @PropertySource
│     ├── Bind spring.profiles.active
│     └── Publish ApplicationEnvironmentPreparedEvent
│
├─3. createApplicationContext()
│     └──
  AnnotationConfigServletWebServerApplicationContext
│
├─4. prepareContext()
│     ├── Apply ApplicationContextInitializers
│     ├── Register main @SpringBootApplication class
│     └── Publish ApplicationContextInitializedEvent
│
├─5. refreshContext()  ←── THIS IS THE BIG PHASE (80% of
  time)
│     │
│     ├─ invokeBeanFactoryPostProcessors()
│     │    ├── ConfigurationClassPostProcessor
│     │    │    ├── Process @SpringBootApplication
│     │    │    ├── Run @ComponentScan
│     │    │    ├── Load AutoConfiguration.imports
│     │    │    └── Evaluate @Conditional annotations
│     │    └── PropertySourcesPlaceholderConfigurer
│     │         └── Resolve @Value("${...}") placeholders
│     │
│     ├─ registerBeanPostProcessors()
│     │    └── Register
  AutowiredAnnotationBeanPostProcessor
│     │         CommonAnnotationBeanPostProcessor, etc.
│     │
│     ├─ finishBeanFactoryInitialization()
│     │    └── Instantiate all non-lazy singletons
│     │         (constructor → @Autowired inject →
  @PostConstruct)
│     │
│     └─ onRefresh() → createWebServer() → Tomcat starts
│
├─6. afterRefresh()
│     └── callRunners()
│          ├── ApplicationRunner.run(ApplicationArguments)
│          └── CommandLineRunner.run(String... args)
│               (ordered by @Order)
│
└─7. Publish ApplicationReadyEvent
      └── Application is LIVE
```

---

### 💻 Code Example

**Example 1 - Startup code hooks:**

```java
// @PostConstruct: self-initialization within a single bean
@Service
public class CacheService {
    private Map<String, Object> cache;

    @PostConstruct
    public void init() {
        // Safe: 'this' bean is fully constructed
        // UNSAFE: don't call other beans' methods here
        // (their @PostConstruct may not have run yet)
        this.cache = new ConcurrentHashMap<>();
    }
}

// ApplicationRunner: runs after ALL beans are initialized
// Use for cross-bean startup coordination
@Component
@Order(1) // runs before other ApplicationRunners
public class DatabaseWarmup implements ApplicationRunner {

    @Autowired CacheService cacheService;
    @Autowired UserRepository userRepository;

    @Override
    public void run(ApplicationArguments args) {
        // Safe: both beans are fully initialized here
        List<User> frequent = userRepository
            .findTop100ByOrderByLoginCountDesc();
        cacheService.warmUp(frequent);
        log.info("Cache warmed with {} users",
            frequent.size());
    }
}
```

**Example 2 - Listening to startup events:**

```java
@Component
public class StartupListener {

    // Runs after context is refreshed but BEFORE runners
    @EventListener(ApplicationStartedEvent.class)
    public void onStarted(ApplicationStartedEvent event) {
        log.info("Context refreshed, runners about to execute");
    }

    // Runs after runners complete - app is serving traffic
    @EventListener(ApplicationReadyEvent.class)
    public void onReady(ApplicationReadyEvent event) {
        log.info("Application fully ready at {}",
            Instant.now());
        // Safe to register in service discovery here
        serviceRegistry.register();
    }

    // Fires on startup failure - use for alert/cleanup
    @EventListener(ApplicationFailedEvent.class)
    public void onFailed(ApplicationFailedEvent event) {
        log.error("Startup failed",
            event.getException());
        alerting.sendPage("Spring Boot startup failure");
    }
}
```

**Example 3 - Profiling startup with Actuator:**

```properties
# Enable startup endpoint (Spring Boot 2.4+)
management.endpoint.startup.enabled=true
management.endpoints.web.exposure.include=startup
```

```bash
# After startup, query which beans took longest to initialize
curl http://localhost:8080/actuator/startup | \
  python -m json.tool | \
  jq '.timeline.events | sort_by(.duration) | reverse | .[0:10]'
```

---

### ⚖️ Comparison Table

| Hook                                    | When It Runs                                   | Context Fully Ready?              | Use For                            |
| --------------------------------------- | ---------------------------------------------- | --------------------------------- | ---------------------------------- |
| `@PostConstruct`                        | After bean's own dependencies injected         | No (other beans may not be ready) | Self-initialization                |
| `ApplicationRunner`                     | After all beans initialized, before ReadyEvent | Yes                               | Cross-bean startup code            |
| `CommandLineRunner`                     | Same as ApplicationRunner                      | Yes                               | CLI-style startup tasks            |
| `SmartLifecycle.start()`                | During `finishRefresh()`                       | Yes                               | Start background threads           |
| `@EventListener(ApplicationReadyEvent)` | After runners complete                         | Yes + server live                 | Service registration, final checks |
| `InitializingBean.afterPropertiesSet()` | Same as @PostConstruct                         | No                                | Framework bean self-init           |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@PostConstruct` runs when the application is fully started | It runs when that single bean's dependencies are injected - before many other beans are even created                                              |
| `CommandLineRunner` and `ApplicationRunner` are equivalent  | Both run at the same lifecycle point; `ApplicationRunner` receives typed `ApplicationArguments`; `CommandLineRunner` receives raw `String[]` args |
| The embedded Tomcat starts before beans are initialized     | Tomcat starts inside `refreshContext()`, after beans are instantiated but before `ApplicationRunner` - so runners can make local HTTP calls       |
| Startup failures always occur in your code                  | Many startup failures are in auto-configuration beans (DataSource, JPA) - look for `BeanCreationException` and trace the `caused by` chain        |
| `@Order` on `ApplicationRunner` controls which runs first   | Yes, but lower values run first (opposite of natural number intuition): `@Order(1)` runs before `@Order(2)`                                       |

---

### 🚨 Failure Modes & Diagnosis

**1. Slow Startup - Unknown Phase**

**Symptom:** Application takes 30+ seconds to start; no obvious bottleneck in logs.

**Root Cause:** Could be JPA metamodel generation, Liquibase migration, HikariCP pool initialization, classpath scanning a large JAR set, or a slow `@PostConstruct` / `ApplicationRunner`.

**Diagnostic:**

```bash
# Spring Boot startup actuator shows per-bean timing
curl http://localhost:8080/actuator/startup | \
  python -m json.tool | \
  jq '.timeline.events[] | select(.duration > 1000)'

# Or: add startup timing to logs
# application.properties
logging.level.org.springframework.boot=DEBUG

# Count ComponentScan time in logs
grep "Finished Spring Data repository scanning" app.log
grep "HikariPool.*initialization completed" app.log
grep "Initialized JPA EntityManagerFactory" app.log
```

**Fix:**

```properties
# If classpath scan is slow: narrow the scan base
# Rather than scanning everything from root package

# If JPA is slow: defer schema validation
spring.jpa.hibernate.ddl-auto=validate  # not create-drop

# Global lazy initialization for dev/Lambda environments
spring.main.lazy-initialization=true
```

---

**2. BeanCreationException Buried in Stack Trace**

**Symptom:** Application fails to start with `Error starting ApplicationContext`; stack trace is 50 frames deep.

**Root Cause:** A bean's constructor, `@Autowired` injection, or `@PostConstruct` threw an exception. The real cause is usually in the `caused by` chain.

**Diagnostic:**

```bash
# Find the root cause - skip to the bottom of the stack
grep "Caused by:" app.log | tail -5

# For @PostConstruct failures - look for the bean name
grep "Error creating bean with name" app.log

# Enable startup failure analyzer
# (usually automatic in Spring Boot 2.4+)
# Look for the "APPLICATION FAILED TO START" section
```

**Fix pattern - trace the cause chain:**

```
BeanCreationException: Error creating bean 'orderService'
  Caused by: BeanCreationException: Error creating bean
    'dataSource'
    Caused by: HikariPool$PoolInitializationException:
      Failed to initialize pool: Connection refused
        Caused by: PSQLException: Connection to db:5432
          refused.
```

→ Root cause: database is not reachable. Not a Spring bug - infrastructure issue.

---

**3. ApplicationRunner Blocking Startup**

**Symptom:** Application starts but never publishes `ApplicationReadyEvent`; Kubernetes readiness probe never returns 200; pod is killed before serving traffic.

**Root Cause:** An `ApplicationRunner.run()` method blocks indefinitely (e.g., waiting for an external service to become available, running a long migration, or an infinite loop).

**Diagnostic:**

```bash
# Thread dump to see what's blocking
jcmd <pid> Thread.print | grep -A10 "ApplicationRunner"

# Or check logs - ApplicationReady is published AFTER runners
grep "ApplicationReadyEvent\|Started.*in" app.log
# If "Started" appears but no traffic → runner is blocking
```

**Fix:**

```java
// BAD: runner blocks waiting for external service
@Override
public void run(ApplicationArguments args) throws Exception {
    while (!externalService.isAvailable()) {
        Thread.sleep(1000); // blocks the startup thread
    }
}

// GOOD: async runner or move retry to health indicator
@Override
public void run(ApplicationArguments args) {
    // Start async background task - don't block
    CompletableFuture.runAsync(() ->
        externalService.waitForAvailability()
    );
    // Reflect external service status in HealthIndicator
    // not in ApplicationRunner
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ApplicationContext` - the central container being initialized during startup; understand its lifecycle
- `Bean Lifecycle` - individual bean init phases (@PostConstruct, @PreDestroy) are nested within application startup
- `Auto-Configuration` - fires during `invokeBeanFactoryPostProcessors()` inside `refresh()`

**Builds On This (learn these next):**

- `Spring Boot Actuator` - the `/actuator/startup` endpoint profiles each startup phase
- `Lazy vs Eager Loading` - lazy loading is the primary tool for optimizing startup time
- `Spring Cloud` - adds additional startup phases (service registration, config client bootstrap)

**Alternatives / Comparisons:**

- `Quarkus startup model` - AOT compilation moves startup work to build time; contrast with Spring's runtime reflection model
- `GraalVM Native Image` - eliminates the refresh phase by pre-computing everything at build time; dramatically reduces startup time
- `SmartLifecycle` - fine-grained lifecycle control for beans that need ordered start/stop (message listeners, scheduled tasks)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STARTUP      │ run() → prepareEnv → createCtx →         │
│ PHASES       │ refresh (80%) → runners → ReadyEvent     │
├──────────────┼──────────────────────────────────────────┤
│ REFRESH      │ BFPPs (auto-config) → BPPs → singleton   │
│ DEEP DIVE    │ instantiation → Tomcat start             │
├──────────────┼──────────────────────────────────────────┤
│ USE          │ @PostConstruct: self-init only           │
│ THE RIGHT    │ ApplicationRunner: cross-bean startup    │
│ HOOK         │ ReadyEvent: after server is live         │
├──────────────┼──────────────────────────────────────────┤
│ DEBUG        │ --debug flag, /actuator/startup,         │
│ SLOW START   │ grep "Caused by:" in stack trace         │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Fail-fast bean validation at startup vs. │
│              │ slow cold starts in serverless/Lambda    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "refresh() builds the bean graph;        │
│              │  runners run after the graph is complete"│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Lazy Loading → Actuator → GraalVM Native │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - System Interaction) A Spring Boot service uses `ApplicationRunner` to load 500,000 product records from the database into an in-memory cache on startup. The load takes 45 seconds. Kubernetes has a `readinessProbe.initialDelaySeconds=30`. Trace exactly what Kubernetes does during those 45 seconds, what traffic the pod receives (if any), and what the end user experiences. What is the correct configuration fix?

**Q2.** (TYPE E - Architecture) A team wants to run database migrations (Flyway) as part of `ApplicationRunner` to ensure migrations complete before the app serves traffic. A second team argues Flyway should run as a `BeanFactoryPostProcessor` during `refresh()` so it runs before JPA validates the schema. Which approach is correct and why - and what catastrophic failure does the wrong choice cause in a multi-pod Kubernetes deployment?
