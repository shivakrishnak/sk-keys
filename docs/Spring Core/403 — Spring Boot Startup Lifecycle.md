---
layout: default
title: "Spring Boot Startup Lifecycle"
parent: "Spring Core"
nav_order: 403
permalink: /spring/spring-boot-startup-lifecycle/
number: "403"
category: Spring Core
difficulty: ★★★
depends_on: "Auto-Configuration, ApplicationContext, Bean Lifecycle, SpringApplication"
used_by: "ApplicationRunner, CommandLineRunner, @EventListener, Actuator"
tags: #java, #spring, #springboot, #advanced, #internals, #deep-dive
---

# 403 — Spring Boot Startup Lifecycle

`#java` `#spring` `#springboot` `#advanced` `#internals` `#deep-dive`

⚡ TL;DR — The ordered sequence from `SpringApplication.run()` to the first ready-to-serve HTTP request — spanning environment preparation, context creation, bean wiring, auto-configuration, and lifecycle callbacks.

| #403 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Auto-Configuration, ApplicationContext, Bean Lifecycle, SpringApplication | |
| **Used by:** | ApplicationRunner, CommandLineRunner, @EventListener, Actuator | |

---

### 📘 Textbook Definition

The **Spring Boot Startup Lifecycle** is the ordered sequence of operations from `SpringApplication.run(App.class, args)` to the application's readiness to serve requests. It encompasses: preparing the `Environment` (loading `application.yml`, resolving profiles); creating the `ApplicationContext` implementation; scanning and registering `BeanDefinition`s; running `BeanFactoryPostProcessor`s (property placeholder resolution, auto-configuration condition evaluation); instantiating and wiring singleton beans; running `ApplicationRunner`s and `CommandLineRunner`s; starting the embedded web server; and publishing `ApplicationReadyEvent`. Lifecycle events emitted throughout (`ApplicationStartingEvent`, `ApplicationEnvironmentPreparedEvent`, `ApplicationContextInitializedEvent`, `ApplicationStartedEvent`, `ApplicationReadyEvent`) allow extension at each phase.

---

### 🟢 Simple Definition (Easy)

When `main()` runs `SpringApplication.run()`, Spring Boot goes through a precise sequence: load config, create a context, scan classes, wire beans, run startup tasks, start the server, and signal readiness — in that order, every time.

---

### 🔵 Simple Definition (Elaborated)

The startup lifecycle is a pipeline of phases, each building on the last. Environment preparation reads files and environment variables. Context creation builds the container. Component scanning registers what exists. Auto-configuration decides what defaults to add. Bean wiring connects everything. Runners execute initialisation code after the context is ready but before traffic arrives. The web server starts and accepts connections. If any phase fails, startup aborts with a clear diagnostic. Understanding each phase tells you WHERE to plug in initialisation code and WHY some hooks fire earlier or later than others.

---

### 🔩 First Principles Explanation

**The complete startup sequence:**

```
┌─────────────────────────────────────────────────────┐
│  SPRING BOOT STARTUP SEQUENCE                       │
│                                                     │
│  1. SpringApplication.run()                         │
│  2. SpringApplicationRunListeners.starting()        │
│     → ApplicationStartingEvent published            │
│  3. Environment prepared                            │
│     → application.yml / .properties loaded         │
│     → Profiles activated                           │
│     → ApplicationEnvironmentPreparedEvent           │
│  4. Banner printed                                  │
│  5. ApplicationContext created                      │
│     (AnnotationConfigServletWebServerAppContext)    │
│  6. ApplicationContextInitializers run              │
│     → ApplicationContextInitializedEvent            │
│  7. SpringApplicationRunListeners.contextLoaded()   │
│  8. Context REFRESH:                                │
│     a. BeanDefinitions registered (scan + imports)  │
│     b. BeanFactoryPostProcessors run                │
│        - Placeholder resolution (@Value)            │
│        - Auto-configuration condition evaluation    │
│     c. BeanPostProcessors instantiated              │
│     d. Singleton beans instantiated & wired         │
│     e. @PostConstruct callbacks                     │
│     f. BPP.postProcessAfterInit (AOP proxies)       │
│     g. Lifecycle beans started                      │
│  9. Embedded server started (Tomcat port bound)     │
│  10. ApplicationStartedEvent published              │
│  11. ApplicationRunner / CommandLineRunner run()    │
│  12. ApplicationReadyEvent published                │
│      → Actuator readiness probe → DOWN until here  │
│      → K8s starts sending traffic                  │
│  13. Application serving requests                   │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**Why the ordering matters:**

```
ApplicationRunner runs at step 11 (not step 7):
  If Runner tries to use beans: at step 7 beans
  don't exist yet → NullPointerException

Actuator readiness = DOWN until step 12:
  K8s won't send traffic until app is ready
  → Prevents 503 during bean wiring startup

BeanFactoryPostProcessors (step 8b) before beans (8d):
  @Value resolution must happen before bean constructors
  → constructors can use resolved @Value fields

Embedded server (step 9) BEFORE runners (step 11):
  Some runners make HTTP calls — server must be up
  → Enables health-check validation in runners

ApplicationContextInitializer (step 6) before refresh:
  Must run before beans are created
  → Used for early property overrides, test support
```

---

### 🧠 Mental Model / Analogy

> The startup lifecycle is like **opening a restaurant for the day**. The kitchen is built and stocked overnight (environment prep + beans wired). Each station is connected — grill talks to prep, prep to expeditor (bean wiring). The head chef runs quality checks before opening (ApplicationRunner). Only after all prep is complete does the host unlock the front door (readiness → K8s routes traffic). If the walk-in refrigerator isn't working (a bean fails to initialise), the restaurant doesn't open at all.

"Building and stocking kitchen" = environment + bean wiring
"Connecting stations" = dependency injection
"Quality checks before opening" = ApplicationRunner
"Host unlocking front door" = ApplicationReadyEvent
"Refrigerator not working" = startup failure → context abort

---

### ⚙️ How It Works (Mechanism)

**Extension points at each lifecycle phase:**

```java
// PHASE 3: Before context — early property override
public class PropertyOverrideInitializer
    implements ApplicationContextInitializer<ConfigurableApplicationContext> {
  @Override
  public void initialize(ConfigurableApplicationContext ctx) {
    // Run before bean definitions processed
    // Add extra PropertySource here
    ctx.getEnvironment()
       .getPropertySources()
       .addFirst(new MapPropertySource("override",
           Map.of("server.port", "9090")));
  }
}

// PHASE 3 event: react to environment prepared
@Component
class EnvironmentListener
    implements ApplicationListener<ApplicationEnvironmentPreparedEvent> {
  @Override
  public void onApplicationEvent(
      ApplicationEnvironmentPreparedEvent event) {
    // Environment is ready, context is NOT yet created
    // Good for: early validation of required properties
  }
}

// PHASE 11: Run code after context ready, before traffic
@Component
class DataMigrationRunner implements ApplicationRunner {
  @Override
  public void run(ApplicationArguments args) throws Exception {
    // All beans available, TX works, server up
    // Good for: data migrations, cache warming
    migrationService.runIfNeeded();
  }
}

// PHASE 12: React to app fully ready
@EventListener(ApplicationReadyEvent.class)
@Async // avoid blocking the startup thread
void scheduleInitialSync() {
  syncService.triggerInitialSync();
}
```

**Startup time profiling:**

```bash
# Spring Boot 2.5+ startup actuator endpoint:
GET /actuator/startup
# Shows each step with duration in milliseconds

# Enable verbose startup logging:
spring.application.admin.enabled=true
logging.level.org.springframework.boot=DEBUG

# JVM startup profiling:
java -XX:+StartFlightRecording \
     -XX:FlightRecorderOptions=filename=startup.jfr \
     -jar app.jar
# Analyse startup.jfr in JDK Mission Control
```

---

### 🔄 How It Connects (Mini-Map)

```
main() → SpringApplication.run()
        ↓
  Environment prepared → profiles active
        ↓
  ApplicationContext created
        ↓
  Context REFRESH:
  BeanDefinitions → BFPP → BPP → Beans wired
  Auto-Configuration (133) runs during BFPP
        ↓
  Bean Lifecycle (108) for each singleton bean
        ↓
  SPRING BOOT STARTUP LIFECYCLE (135) ← you are here
  Embedded server started
        ↓
  ApplicationRunner / CommandLineRunner (11)
        ↓
  ApplicationReadyEvent (12)
  Actuator (134) readiness → UP
  K8s routes traffic
```

---

### 💻 Code Example

**Example 1 — ApplicationRunner for pre-traffic initialisation:**

```java
// Runs after all beans ready, before K8s sends traffic
@Component
@Order(1)  // ApplicationRunners execute in order
public class DatabaseMigrationRunner
    implements ApplicationRunner {

  private final FlywayMigrationService flyway;

  @Override
  public void run(ApplicationArguments args) {
    log.info("Running DB migrations before accepting traffic");
    flyway.migrate();  // all beans available, TX works
    log.info("Migrations complete — app ready");
  }
}

@Component
@Order(2)
public class CacheWarmingRunner implements ApplicationRunner {
  private final CacheService cache;

  @Override
  public void run(ApplicationArguments args) {
    log.info("Warming caches...");
    cache.warmTopProducts(100);
  }
}
// K8s readiness probe stays DOWN until both runners complete
// → Pod receives traffic only when fully initialised
```

**Example 2 — Measuring startup time per phase:**

```bash
# Spring Boot Actuator startup endpoint
# (requires spring.mvc.static-path-pattern or 3.x)
curl http://localhost:8080/actuator/startup | \
  jq '.timeline.events[] | {tag: .startupStep.name, ms: (.duration / 1000000)}'

# Typical output:
# {"tag": "spring.beans.instantiate", "ms": 287}
# {"tag": "spring.context.refresh", "ms": 1423}
# {"tag": "tomcat.start", "ms": 312}
# {"tag": "spring.boot.application.ready", "ms": 2187}
```

---

### 🔁 Flow / Lifecycle

```
SpringApplication.run(App.class) ─────────────────────
        1. Starting event
        2. Environment: profiles, yml, env vars
        3. Context type determined (Web / Reactive / None)
        4. ApplicationContextInitializers
        5. Context created (not yet refreshed)
────────────────────────────────────────── REFRESH ───
        6. BeanDefinition scanning (@ComponentScan)
        7. BeanFactoryPostProcessors
           - @Value placeholders resolved
           - Auto-configuration evaluated
        8. BeanPostProcessors instantiated
        9. Singleton beans created + wired
       10. @PostConstruct called on each
       11. BPP.postProcessAfterInit (AOP proxies)
       12. SmartLifecycle.start() beans
───────────────────────────────────────── POST-REFRESH
       13. Embedded Tomcat starts → binds port
       14. ApplicationStartedEvent
       15. ApplicationRunner.run() × N (ordered)
       16. ApplicationReadyEvent
           → Actuator readiness → UP
           → K8s routes traffic
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CommandLineRunner and ApplicationRunner are equivalent | Both run after context refresh. CommandLineRunner receives String[], ApplicationRunner receives ApplicationArguments — the latter supports named args (--key=value) |
| @PostConstruct is the best place for startup logic | @PostConstruct runs during bean creation (step 9) — before ApplicationRunner (step 15). If your logic needs ALL beans ready or depends on other services being initialised, use ApplicationRunner |
| ApplicationReadyEvent fires before the server starts | The embedded server starts at step 13 — BEFORE ApplicationReadyEvent at step 16. This means ApplicationRunner code can make HTTP calls to the app itself |
| Failing ApplicationRunner aborts the startup | A RuntimeException in ApplicationRunner does cause startup to fail — this is intentional: use it to enforce pre-traffic invariants (required DB migrations, etc.) |

---

### 🔥 Pitfalls in Production

**1. Blocking ApplicationRunner delaying readiness**

```java
// BAD: long cache warm-up in ApplicationRunner
// K8s readiness stays DOWN during entire warm-up
@Component
class CacheWarmingRunner implements ApplicationRunner {
  @Override
  public void run(ApplicationArguments args) {
    loadAllProductsIntoCache(); // 30 seconds!
  }
}
// K8s readinessProbe: initialDelaySeconds=30 not enough
// → app marked NotReady → rolling deploy stalls

// GOOD: async warm-up after startup
@EventListener(ApplicationReadyEvent.class)
@Async
void warmCacheAsync() {
  loadAllProductsIntoCache(); // fires after readiness=UP
  // K8s routes traffic immediately
  // Cache warms in background (app serves cold cache briefly)
}
```

**2. Using @PostConstruct where ApplicationRunner is needed**

```java
// BAD: @PostConstruct fires during bean creation
// Other beans may not be initialised yet
@PostConstruct
void init() {
  kafkaConsumer.subscribe(topics); // KafkaConsumer created?
  // If KafkaConsumer bean is created AFTER this bean:
  // kafkaConsumer is null during this @PostConstruct
}

// GOOD: ApplicationRunner fires after all beans ready
@Component
class KafkaStartupRunner implements ApplicationRunner {
  private final KafkaConsumer consumer;

  @Override
  public void run(ApplicationArguments args) {
    consumer.subscribe(topics); // all beans guaranteed ready
  }
}
```

---

### 🔗 Related Keywords

- `ApplicationContext` — created and refreshed during startup
- `Auto-Configuration` — evaluated during BFPP phase of context refresh
- `Bean Lifecycle` — each bean's init sequence runs during context refresh
- `ApplicationRunner` — post-refresh, pre-traffic initialisation hook
- `ApplicationReadyEvent` — signals full startup completion; triggers readiness probe
- `SpringApplicationRunListener` — extension point for all lifecycle phases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ 16-step sequence from run() to first      │
│              │ accepted request; each phase has hooks    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ ApplicationRunner: post-ready init;       │
│              │ @EventListener(ReadyEvent): async tasks   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ @PostConstruct for multi-bean logic;      │
│              │ blocking Runner for non-critical cache    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Opening a restaurant: cook, stock, prep, │
│              │  check — only then unlock the door."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WebFlux / Reactive (136) →               │
│              │ Actuator (134) → GraalVM native image     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot 3.x introduced AOT (Ahead-of-Time) processing for GraalVM native images. During AOT, most of the startup lifecycle (classpath scanning, `@Conditional` evaluation, auto-configuration selection, proxy generation) runs at BUILD TIME rather than at application startup. Describe which of the 16 startup steps are moved to build time vs. which must still run at runtime — and explain why environment preparation (step 2) must still run at runtime even in a native image, while bean definition scanning (step 6) does not.

**Q2.** `ApplicationRunner` beans execute after `SmartLifecycle.start()` (step 12) but before `ApplicationReadyEvent` (step 16). A common pattern is using `ApplicationRunner` to perform database schema validation. If the validation takes 45 seconds (large schema), Kubernetes' `readinessProbe.initialDelaySeconds` must be set high enough to avoid false failures. Describe the correct operational strategy for sizing `initialDelaySeconds` and `periodSeconds` when you have variable startup times — and explain why setting `initialDelaySeconds` too high causes problems during rolling deployments (hint: old pods may be overloaded while new pods are warming up).

