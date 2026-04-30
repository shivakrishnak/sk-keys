---
layout: default
title: "Spring Boot Startup Lifecycle"
parent: "Spring Framework"
nav_order: 135
permalink: /spring/spring-boot-startup-lifecycle/
number: "135"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: ApplicationContext, Auto-Configuration
used_by: Spring Boot initialization, ApplicationRunner
tags: #springboot, #spring, #internals, #intermediate
---

# 135 — Spring Boot Startup Lifecycle

`#springboot` `#spring` `#internals` `#intermediate`

⚡ TL;DR — Spring Boot's startup lifecycle orchestrates environment setup, ApplicationContext creation, auto-configuration, bean initialization, and web server startup in a defined sequence.

| #135 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ApplicationContext, Auto-Configuration | |
| **Used by:** | Spring Boot initialization, ApplicationRunner | |

---

### 📘 Textbook Definition

The Spring Boot application startup lifecycle encompasses the phases from `SpringApplication.run()` invocation through publishing `ApplicationReadyEvent`. It includes: creating and preparing the `SpringApplication`, preparing the environment (`Environment`), creating the `ApplicationContext`, loading bean definitions (including auto-configuration), refreshing the context (instantiating all singletons), starting the embedded server, and publishing lifecycle events.

### 🟢 Simple Definition (Easy)

When you call `SpringApplication.run()`, Spring Boot goes through a sequence of steps: set up properties, create the container, load all beans, start Tomcat, then announce "I'm ready." Hook into any of these steps with listeners.

### 🔩 First Principles Explanation

**Complete startup sequence:**
```
SpringApplication.run(MyApp.class)
     ↓
1. SpringApplication created, defaults set
     ↓
2. SpringApplicationRunListeners notified: starting
     ↓
3. Environment prepared (application.properties, profiles loaded)
     ↓
4. ApplicationContext created (AnnotationConfigServletWebServerApplicationContext)
     ↓
5. ApplicationContext prepared:
   - BeanDefinitions loaded (@Configuration, component scan)
   - Auto-configuration classes loaded (META-INF/spring/*.imports)
     ↓
6. ApplicationContext refreshed:
   - BeanFactoryPostProcessors run
   - All singleton beans instantiated + DI
   - BeanPostProcessors applied (AOP, etc.)
   - @PostConstruct called
     ↓
7. Web server started (Tomcat/Netty)
     ↓
8. CommandLineRunner / ApplicationRunner beans invoked
     ↓
9. ApplicationReadyEvent published ← APPLICATION IS READY
```

### 💻 Code Example
```java
// Hook 1: ApplicationContextInitializer — before context refresh
public class MyInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {
    @Override
    public void initialize(ConfigurableApplicationContext ctx) {
        System.out.println("Context initialized (before beans created)");
    }
}
// Hook 2: CommandLineRunner — after everything is ready, before ready event
@Component
@Order(1)
public class DataLoader implements CommandLineRunner {
    @Override
    public void run(String... args) {
        System.out.println("Loading initial data after startup...");
        // e.g., seed database with test data
    }
}
// Hook 3: ApplicationRunner — same as CommandLineRunner but typed args
@Component
public class HealthChecker implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) {
        System.out.println("Performing post-startup health check...");
    }
}
// Hook 4: ApplicationReadyEvent — fired when app is fully ready
@EventListener(ApplicationReadyEvent.class)
public void onReady(ApplicationReadyEvent event) {
    System.out.println("App ready in " + event.getTimeTaken().toMillis() + "ms");
}
// Hook 5: ApplicationFailedEvent — if startup fails
@EventListener(ApplicationFailedEvent.class)
public void onFailed(ApplicationFailedEvent event) {
    System.err.println("Startup failed: " + event.getException().getMessage());
    // alert, cleanup
}
```

### 🔗 Related Keywords

- **[ApplicationContext](./105 — ApplicationContext.md)** — the container created during startup
- **[Auto-Configuration](./133 — Auto-Configuration.md)** — runs during startup BeanDefinition loading
- **[Bean Lifecycle](./108 — Bean Lifecycle.md)** — happens during ApplicationContext refresh

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| EARLY HOOKS | ApplicationContextInitializer (before context)       |
+------------------------------------------------------------------+
| POST-REFRESH| CommandLineRunner / ApplicationRunner                |
+------------------------------------------------------------------+
| BOOT EVENTS | ApplicationStartingEvent → EnvironmentPreparedEvent  |
|             | → ContextRefreshedEvent → ApplicationReadyEvent      |
+------------------------------------------------------------------+
| FAIL HOOK   | ApplicationFailedEvent                               |
+------------------------------------------------------------------+
```
