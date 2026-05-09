---
id: SPR-069
title: Spring Configuration Trade-off Framing
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-025, SPR-030, SPR-044, SPR-061, SPR-068
used_by:
related: SPR-070, SPR-067, SPR-064
tags:
  - spring
  - java
  - advanced
  - mental-model
  - bestpractice
  - architecture
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /spr/spring-configuration-trade-off-framing/
---

# SPR-069 - Spring Configuration Trade-off Framing

⚡ TL;DR - Spring offers four configuration styles (`@Component`, `@Bean`, `@ConditionalOn*`, auto-configuration); choosing correctly requires matching the explicitness need and the ownership context, not personal preference.

| Field          | Value                                                                                                                                                                                                                                   |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-025 - @Component and Stereotype Annotations]], [[SPR-030 - @Configuration and @Bean]], [[SPR-044 - Spring Boot Auto-configuration Deep Dive]], [[SPR-061 - Spring Boot Configuration Strategy]], [[SPR-068 - IoC-First Thinking]] |
| **Used by**    | -                                                                                                                                                                                                                                       |
| **Related**    | [[SPR-070 - Framework Selection Mental Model]], [[SPR-067 - Spring Specification and Extension Points]], [[SPR-064 - Spring Framework Internals Deep Dive]]                                                                             |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A Spring Boot application has inconsistent configuration: some beans registered via `@Component`, some via `@Bean` in `@Configuration` classes, some activated by `@ConditionalOnProperty`. New developers cannot predict where to add new beans or how to override existing ones. Library integration duplicates configuration across projects. `@Configuration(proxyBeanMethods=true)` creates unexpected proxy overhead. `@ConditionalOnMissingBean` overrides fail silently because of registration order.

**THE BREAKING POINT:**

Configuration style affects testability, override-ability, proxy creation, and library reuse. Choosing `@Component` vs `@Bean` based on "whatever I'm used to" leads to: library beans that cannot be overridden by application code, CGLIB proxies where none are needed, and auto-configuration that activates in tests when it should not.

**THE INVENTION MOMENT:**

Spring's four configuration styles were designed for different ownership contexts. Understanding the ownership model makes the right choice obvious: `@Component` for application-owned domain objects; `@Bean` for infrastructure or third-party objects; auto-configuration for library defaults; `@ConditionalOnMissingBean` for overridable library defaults.

**EVOLUTION:**

- **2004:** XML beans → externally owned, always explicit
- **2007:** `@Component` scan → reduces XML for application beans
- **2010:** Java `@Configuration` / `@Bean` → typesafe replacement for XML `<bean>`
- **2013:** Spring Boot auto-configuration → convention-over-configuration at library level
- **2018:** `@Configuration(proxyBeanMethods=false)` → reduces CGLIB overhead for lite configurations
- **2022:** Spring Framework 6 AOT → all configuration styles must be AOT-compatible

---

### 📘 Textbook Definition

Spring provides four primary bean registration mechanisms: (1) **`@Component` + component scan** - used for application-owned beans where the class itself declares its Spring role; (2) **`@Bean` inside `@Configuration`** - used for third-party or infrastructure beans the application wires together; (3) **`@ConditionalOn*` in `@Configuration`** - used for conditional registration based on properties, class presence, or missing beans; (4) **Auto-configuration (`spring.factories` / `imports`)** - used by library authors to register defaults that applications can override. The trade-offs across these styles involve explicitness, override-ability, proxy creation cost, and ownership semantics.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Use `@Component` when you own the class; `@Bean` when you don't; auto-configuration when you're writing a library that others will include.

> Configuring Spring beans is like decorating a house. `@Component` is painting your own walls (you own them, mark them directly). `@Bean` is buying furniture (you don't own the furniture factory, so you configure the assembly in your living room). Auto-configuration is the interior designer who sets up a default layout (you can move the furniture later with `@ConditionalOnMissingBean`).

**One insight:** `@Component` vs `@Bean` is fundamentally an _ownership question_, not a style preference. If you own the source code, use `@Component`. If you don't, use `@Bean`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `@Component` couples the class to Spring - the annotation lives in the class source; not appropriate for third-party classes
2. `@Bean` keeps configuration external to the class - the class has no Spring coupling
3. `@ConditionalOnMissingBean` evaluation order depends on registration order - user `@Configuration` must be registered before the conditional fires
4. Auto-configuration runs _after_ application `@Configuration` (via `DeferredImportSelector`) - this is the mechanism that makes `@ConditionalOnMissingBean` work correctly
5. `@Configuration(proxyBeanMethods=true)` (default) wraps `@Bean` methods in CGLIB to enforce singleton semantics; `proxyBeanMethods=false` skips proxying for performance at the cost of `@Bean` method call guarantees

**DERIVED DESIGN:**

From invariant 1+2 → `DataSource`, `RestTemplate`, `ObjectMapper` are always configured via `@Bean` (third-party classes).
From invariant 4 → In a Spring Boot app, user `@Configuration` classes are always processed before auto-configuration. A user who defines their own `DataSource @Bean` prevents `DataSourceAutoConfiguration` from registering a default (`@ConditionalOnMissingBean(DataSource.class)`).
From invariant 5 → In `@Configuration` classes that do not call `@Bean` methods from other `@Bean` methods (the common case), use `@Configuration(proxyBeanMethods=false)` to eliminate unnecessary CGLIB subclass creation.

**THE TRADE-OFFS:**

**Gain of `@Component`:** Less boilerplate; class self-describes its role; Spring automatically detects in scan.

**Cost of `@Component`:** Class is coupled to Spring annotations; harder to test without Spring; cannot configure third-party classes.

**Gain of `@Bean` in `@Configuration`:** Full control over construction; testable via direct instantiation; works for any class; explicit dependency wiring visible in one place.

**Cost of `@Bean`:** More verbose; configuration classes can grow large; CGLIB proxy by default.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Different ownership contexts genuinely require different configuration mechanisms. A library default that applications can override is inherently more complex than an application bean.

**Accidental:** The `proxyBeanMethods` default (true, adds CGLIB proxy) was a Spring 3.0 design choice for correctness that adds overhead in the 90% case where `@Bean` methods are not called from other `@Bean` methods. Spring Boot 3's auto-configurations use `proxyBeanMethods=false` by default.

---

### 🧪 Thought Experiment

**SETUP:** A library provides a `MetricsCollector` class. The library wants Spring Boot applications to have a `MetricsCollector` bean automatically, but allow applications to provide their own.

**OPTION A - `@Component` on `MetricsCollector` in the library:**

Application includes the library JAR. Component scan picks up `MetricsCollector`. Application also defines `@Component CustomMetricsCollector implements MetricsCollector`. Spring context fails: `NoUniqueBeanDefinitionException` - two beans of the same type. Or if `@Primary` is added, the library `@Component` wins - overriding the application's choice.

**OPTION B - Auto-configuration in the library:**

```java
// In library: META-INF/spring/
//   org.springframework.boot.autoconfigure.
//   AutoConfiguration.imports
com.library.MetricsAutoConfiguration

@AutoConfiguration
public class MetricsAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public MetricsCollector metricsCollector() {
        return new DefaultMetricsCollector();
    }
}
```

Application defines `@Bean CustomMetricsCollector`. Auto-configuration runs after user config. `@ConditionalOnMissingBean` detects `CustomMetricsCollector`. Library's `DefaultMetricsCollector` is NOT registered. Application's bean wins. No conflict.

**THE INSIGHT:**

Auto-configuration + `@ConditionalOnMissingBean` is the correct pattern for library defaults. `@Component` in libraries creates unresolvable conflicts or silent overrides.

---

### 🧠 Mental Model / Analogy

> Spring configuration styles form a decision tree based on ownership and intent. `@Component` is a business card you print yourself (you own the identity). `@Bean` is a letter of introduction you write for someone else (third-party class, you configure it). Auto-configuration is a catering service's default menu (the caterer provides defaults; you override specific dishes). `@ConditionalOnMissingBean` is the clause "only if the client hasn't ordered their own": the caterer checks before plating the default dish.

**Element mapping:**

- Business card → `@Component` on your own class
- Letter of introduction → `@Bean` for third-party class
- Caterer's default menu → auto-configuration
- "Only if client hasn't ordered" → `@ConditionalOnMissingBean`
- Client overriding default dish → application `@Bean` before auto-config

Where this analogy breaks down: unlike a catering service, `@ConditionalOnMissingBean` checks at application startup (not reservation time) - the "ordering" must happen in the correct phase for the check to work.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring has different ways to register objects. The simplest is putting `@Component` on your own class. For objects from external libraries, you create a method with `@Bean`. Auto-configuration is how Spring Boot pre-registers sensible defaults you can replace.

**Level 2 - How to use it (junior developer):**
Rule of thumb: annotate your service and repository classes with `@Service`, `@Repository`, `@Component`. For external objects (DataSource, RestTemplate, ObjectMapper), use `@Bean` in a `@Configuration` class. Use `@Profile("test")` to swap beans in tests. Use `@ConditionalOnProperty` to enable/disable features via `application.yml`.

**Level 3 - How it works (mid-level engineer):**
`@Configuration(proxyBeanMethods=true)` (default): Spring CGLIB-subclasses the configuration class. When `@Bean` method `dataSource()` is called from another `@Bean` method (e.g., in `entityManagerFactory()`), the CGLIB proxy intercepts the call and returns the singleton from the registry. `proxyBeanMethods=false` disables this: `@Bean` methods are plain Java methods; calling one from another creates a new instance. In auto-configuration, `DeferredImportSelector` runs all auto-configuration classes _after_ all regular `@Configuration` classes - this ensures `@ConditionalOnMissingBean` evaluates after user config has registered its beans.

**Level 4 - Why it was designed this way (senior/staff):**
The `@Configuration(proxyBeanMethods=true)` default was chosen for correctness over performance: it makes the `@Configuration` class feel like an XML bean definition (calling the same factory method always returns the singleton). The trade-off was explicitly chosen by the Spring team as "safer default for application developers who might call `@Bean` methods directly." Spring Boot's move to `proxyBeanMethods=false` in all auto-configurations (2021) was a performance optimisation for the common case. This shift reflects 10 years of data: direct `@Bean` method calls between factory methods are rare in well-designed code; the CGLIB overhead is not.

**Expert Thinking Cues:**

- `@ConditionalOnClass` + `@ConditionalOnMissingBean` is the standard auto-configuration pair: only configure if the library is on the classpath AND the user hasn't configured it
- `@SpringBootApplication` disables component scan of packages that contain auto-configuration classes - use `spring.factories` / `imports`, not component scan, for library config
- `@Conditional` is composable: `@ConditionalOnProperty("feature.enabled") AND @ConditionalOnClass(SomeClass.class)` uses `@ConditionalOnAll`

---

### ⚙️ How It Works (Mechanism)

```
Configuration Registration Sequence:

1. Component scan (@SpringBootApplication scope)
   → All @Component / @Service / @Repository
   → All @Configuration classes in scan base

2. @Import from @Configuration classes
   → ImportSelector / ImportBeanDefinitionRegistrar

3. DeferredImportSelector (Spring Boot auto-config)
   → Reads META-INF/spring/
     ...AutoConfiguration.imports
   → Runs AFTER steps 1-2
   → @ConditionalOnMissingBean fires here
   → User beans from steps 1-2 are visible

Decision tree for new bean:
  ┌─ Do I own the class source?
  │    Yes → @Component / @Service / @Repository
  │    No  → @Bean in @Configuration
  │
  ├─ Is this a library default (overridable)?
  │    Yes → Auto-configuration +
  │           @ConditionalOnMissingBean
  │    No  → Regular @Bean
  │
  └─ Is this feature toggle-able?
       Yes → @ConditionalOnProperty
       No  → Unconditional @Bean
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW - override auto-configured DataSource:**

```
[Application startup]
     |
     ├─ Component scan processes
     |    └─ App's @Configuration beans registered
     |         ← YOU ARE HERE (user config phase)
     |
     ├─ DeferredImportSelector processes
     |    auto-configuration imports
     |
     ├─ DataSourceAutoConfiguration evaluates:
     |    @ConditionalOnMissingBean(DataSource.class)
     |    └─ App registered DataSource? YES
     |       → Skip auto-config DataSource
     |
[App uses its own DataSource; auto-config skipped]
```

**FAILURE PATH:**

- `@ConditionalOnMissingBean` fires before user config → user bean not seen → auto-config bean registered → `NoUniqueBeanDefinitionException`
- `@Component` in library + `@Component` in app → same type, no `@Primary` → ambiguous
- `proxyBeanMethods=true` + `@Bean` calling another `@Bean` from non-`@Configuration` class → new instance created each time (not a proxy)

**WHAT CHANGES AT SCALE:**

In a large monorepo with 20 modules, each module may define its own auto-configuration. Configuration registration order between modules becomes important. Use `@AutoConfigureBefore` / `@AutoConfigureAfter` to express ordering between auto-configurations explicitly.

---

### 💻 Code Example

**BAD - library uses `@Component`, conflicts with application bean:**

```java
// In library JAR (bad practice)
@Component  // Picked up by component scan!
public class DefaultHttpClient
        implements HttpClient {
    // ...
}

// In application - tries to override
@Component  // Now TWO beans of HttpClient type
public class CustomHttpClient
        implements HttpClient {
    // ...
}
// Result: NoUniqueBeanDefinitionException
// or silent override depending on scan order
```

**GOOD - library uses auto-configuration:**

```java
// In library: AutoConfiguration.imports
// com.library.HttpClientAutoConfiguration

@AutoConfiguration
@ConditionalOnClass(HttpClient.class)
public class HttpClientAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean(HttpClient.class)
    public HttpClient defaultHttpClient() {
        return new DefaultHttpClient();
    }
}

// In application - clean override
@Configuration
public class AppConfig {
    @Bean  // Auto-config skips DefaultHttpClient
    public HttpClient customHttpClient() {
        return new CustomHttpClient(
            // custom settings
        );
    }
}
```

**`proxyBeanMethods=false` for performance:**

```java
// BAD: Unnecessary CGLIB proxy when @Bean methods
// are not called from each other
@Configuration  // proxyBeanMethods=true (default)
public class ServiceConfig {

    @Bean
    public OrderService orderService() {
        // Never calls paymentGateway() directly
        return new OrderService(paymentGateway());
        // ^ This call IS intercepted by CGLIB proxy
        //   (returns singleton) - needed here!
    }

    @Bean
    public PaymentGateway paymentGateway() {
        return new StripeGateway(stripeKey());
    }

    @Bean
    public String stripeKey() {
        return env.getProperty("stripe.key");
    }
}

// GOOD: proxyBeanMethods=false when @Bean methods
// are NOT called from each other
@Configuration(proxyBeanMethods = false)
public class ServiceConfig {

    private final Environment env;

    public ServiceConfig(Environment env) {
        this.env = env;
    }

    @Bean
    public OrderService orderService(
            PaymentGateway gateway) {  // injected
        return new OrderService(gateway);
        // ^ No direct @Bean method call needed
    }

    @Bean
    public PaymentGateway paymentGateway() {
        return new StripeGateway(
            env.getProperty("stripe.key"));
    }
}
```

---

### ⚖️ Comparison Table

| Style                                     | Ownership         | Proxy? | Override-able?                | Best For                                  |
| ----------------------------------------- | ----------------- | ------ | ----------------------------- | ----------------------------------------- |
| `@Component` / `@Service`                 | You own the class | No     | Via `@Primary` / `@Qualifier` | Application domain objects                |
| `@Bean` (proxyBeanMethods=true)           | Third-party class | CGLIB  | Via bean name                 | Infrastructure with `@Bean` method calls  |
| `@Bean` (proxyBeanMethods=false)          | Third-party class | None   | Via bean name                 | Infrastructure without cross-method calls |
| Auto-config + `@ConditionalOnMissingBean` | Library author    | No     | By defining same-type bean    | Library defaults                          |
| `@ConditionalOnProperty`                  | Any               | No     | Via property                  | Feature flags                             |

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "`@Component` and `@Bean` are interchangeable"                | `@Component` annotates a class you own; `@Bean` annotates a factory method for any class. They solve different ownership scenarios.                                                                    |
| "`proxyBeanMethods=false` is always better"                   | `proxyBeanMethods=false` breaks the singleton guarantee when `@Bean` methods call other `@Bean` methods directly. Use it only when you inject dependencies via method parameters, not direct calls.    |
| "`@ConditionalOnMissingBean` is the same as `@Primary`"       | `@ConditionalOnMissingBean` prevents the bean from being registered at all if an existing bean matches. `@Primary` registers both beans and marks one as preferred for injection. Different semantics. |
| "Auto-configuration runs before my @Configuration"            | Auto-configuration runs _after_ user `@Configuration` (via `DeferredImportSelector`). This is what makes `@ConditionalOnMissingBean` work.                                                             |
| "Field injection is simpler so it's fine in `@Configuration`" | `@Configuration` classes should also use constructor injection. `@Configuration` classes can and should be unit-tested by instantiating them with mock environment values.                             |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Auto-configuration bean registered despite user override**

**Symptom:** Application defines `@Bean DataSource` but `DataSourceAutoConfiguration` still creates a `HikariCP` DataSource bean; `NoUniqueBeanDefinitionException` on `DataSource`.

**Root Cause:** User's `@Configuration` class is in a package scanned by Spring Boot, but `@Bean DataSource` is inside a `@Profile("prod")` block. The profile is not active, so the conditional bean is not registered. `@ConditionalOnMissingBean(DataSource.class)` finds no `DataSource` and registers the auto-config bean.

**Diagnostic:**

```bash
# Check which beans are registered
curl http://localhost:8080/actuator/beans \
  | jq '.contexts[].beans | to_entries[]
    | select(.key | contains("dataSource"))'
# Check which profiles are active
curl http://localhost:8080/actuator/env \
  | jq '.activeProfiles'
```

**Fix:** Ensure the user `DataSource` bean is registered unconditionally (not profile-gated) OR ensure the correct profile is active in the environment where conflict occurs.

**Prevention:** Integration test that asserts exactly one `DataSource` bean in the context: `assertThat(context.getBeanNamesForType(DataSource.class)).hasSize(1)`.

---

**Mode 2: `@ConditionalOnProperty` silently disables required feature in production**

**Symptom:** Email notifications stop in production; no errors; feature silently inactive.

**Root Cause:** `@ConditionalOnProperty("email.enabled")` on `EmailSender` bean. `email.enabled` missing from production `application.yml` (not in `application-prod.yml` either). Property defaults to `false` (missing = not present = `matchIfMissing` default = false). Bean not registered.

**Diagnostic:**

```bash
curl http://localhost:8080/actuator/conditions \
  | jq '.contexts[].notMatched
    | to_entries[] | select(
      .value[].condition == "OnPropertyCondition")'
# Shows all beans NOT registered and why
```

**Fix:** Set `matchIfMissing = true` for properties that should default to enabled, or add the property to a shared `application.yml` with an explicit default.

**Prevention:** Include all `@ConditionalOnProperty`-gated beans in an integration test with a dedicated `@TestPropertySource` asserting the bean IS registered.

---

**Mode 3: Prototype beans in singleton via `@Bean` call (Security failure mode)**

**Symptom:** `@Scope("prototype") @Bean` credentials holder is created once and reused; all requests share the same credentials object; isolation broken.

**Root Cause:** `@Configuration(proxyBeanMethods=true)` with singleton `@Bean sessionFactory()` calling prototype `@Bean credentials()` directly. CGLIB intercepts the `credentials()` call and returns the _singleton_ instance from the registry - not a new prototype.

**Diagnostic:**

```java
@SpringBootTest
class ScopeTest {
    @Autowired ApplicationContext ctx;

    @Test
    void credentialsAreNotSingleton() {
        // Should be different instances
        var c1 = ctx.getBean(Credentials.class);
        var c2 = ctx.getBean(Credentials.class);
        assertThat(c1).isNotSameAs(c2);  // FAILS
    }
}
```

**Fix:** Inject `ObjectProvider<Credentials>` into singleton beans; call `provider.getObject()` at request time to create a new prototype instance.

**Prevention:** Architecture test asserting `@Scope("prototype")` beans are only injected via `ObjectProvider`, never directly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-025 - @Component and Stereotype Annotations]] - the component scan mechanism
- [[SPR-030 - @Configuration and @Bean]] - the `@Bean` factory method mechanism
- [[SPR-044 - Spring Boot Auto-configuration Deep Dive]] - the auto-configuration layer
- [[SPR-068 - IoC-First Thinking]] - the design philosophy that informs these choices

**Builds On This (learn these next):**

- [[SPR-070 - Framework Selection Mental Model]] - extends this framing to framework-level decisions
- [[SPR-067 - Spring Specification and Extension Points]] - the extension API for library authors

**Alternatives / Comparisons:**

- Micronaut compile-time DI - `@Bean` equivalent is `@Factory`; no runtime auto-configuration
- Dagger 2 - `@Provides` methods = `@Bean`; compile-time; no conditional registration
- XML configuration (Spring legacy) - externally-owned, always explicit - the pre-annotation baseline

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Decision framework for choosing between  |
|               | Spring's 4 configuration mechanisms      |
| PROBLEM       | Inconsistent config style causes silent   |
|               | overrides, proxy overhead, test failures  |
| KEY INSIGHT   | Ownership determines style: you own it   |
|               | → @Component; you don't → @Bean         |
| USE WHEN      | Every time you register a new Spring bean|
| AVOID WHEN    | @Component on third-party classes; @Bean |
|               | for classes you can annotate directly    |
| TRADE-OFF     | @Component brevity vs @Bean explicitness |
| ONE-LINER     | @Component=own class; @Bean=third-party;  |
|               | autoconfig=library default with override  |
| NEXT EXPLORE  | SPR-070 (Framework Selection Mental Model)|
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Use `@Component` for classes you own; `@Bean` for classes you don't - this is an ownership decision
2. Library defaults belong in auto-configuration with `@ConditionalOnMissingBean`, not in `@Component` - otherwise user overrides conflict
3. `proxyBeanMethods=false` is correct when `@Bean` methods are not called from other `@Bean` methods in the same class

**Interview one-liner:** "Spring configuration style choice is driven by ownership: `@Component` for your own annotatable classes, `@Bean` for third-party, auto-configuration for library defaults that applications override via `@ConditionalOnMissingBean`; `proxyBeanMethods=false` removes CGLIB overhead when `@Bean` methods don't call each other."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Match the configuration mechanism to the ownership context._ When a system provides multiple configuration styles, the correct choice is determined by who owns the artifact being configured, not by personal preference or brevity. Ownership defines the correct boundary for configuration.

**Where else this pattern appears:**

- **Kubernetes RBAC** - ServiceAccount (you own) vs ClusterRole (admin owns); correct binding depends on ownership level
- **npm package.json** - `dependencies` vs `devDependencies` vs `peerDependencies` - each for a different ownership/usage context
- **Terraform modules** - module inputs (explicit, owned by caller) vs local values (implicit, owned by module) - same ownership framing

---

### 💡 The Surprising Truth

`@Configuration(proxyBeanMethods=true)` - the default for 14 years - creates a CGLIB subclass of every `@Configuration` class even in applications that never call `@Bean` methods from other `@Bean` methods. In a typical Spring Boot application with 20 `@Configuration` classes, this creates 20 unnecessary CGLIB subclasses at startup. Spring Boot's internal move to `proxyBeanMethods=false` (completed in 2021 for all auto-configurations) reduced the startup overhead of Spring Boot itself by roughly 15-20%. The feature that was the default for correctness (preventing double-instantiation of prototype/singleton beans in factory method chains) is the minority use case. The safer default turned out to be the slower one in nearly all real-world applications - a textbook example of a default that optimised for correctness at the cost of performance.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** A team is building an internal library that provides audit logging for all Spring Boot microservices. They have three proposals: (A) provide a JAR with `@Component AuditLogger` in a known package for applications to scan; (B) provide a JAR with a `@Bean` factory in a `@Configuration` class the application must `@Import` explicitly; (C) provide a JAR with auto-configuration that registers `AuditLogger` via `@ConditionalOnMissingBean`. Evaluate each option from the perspective of: discoverability, override-ability, and risk of unexpected activation.

_Hint:_ Option A requires component scan configuration; can conflict with application beans. Option B requires explicit opt-in; cannot be accidentally activated. Option C is automatic but conditional; consider what "unexpected activation" means in a test environment.

**Question 2 (A - System Interaction):** A Spring Boot application uses `@ConditionalOnProperty("cache.enabled=true")` to activate caching. The application has 3 environments: `dev`, `staging`, `production`. The property is set in `application-production.yml` only. Describe what happens in integration tests (which use `@SpringBootTest` with `@ActiveProfiles("test")`), staging (no cache property), and production (cache enabled). Does caching activate in each environment?

_Hint:_ Trace the property resolution order for each environment. Does `application-test.yml` exist? Is `cache.enabled` set anywhere? What is `matchIfMissing` default?

**Question 3 (E - First Principles):** Why does `@ConditionalOnMissingBean` reliably detect user-defined beans when used in auto-configuration, but _unreliably_ detect them when used in a `@Configuration` class that is processed at the same time as other `@Configuration` classes (not via auto-configuration)?

_Hint:_ The answer is in the processing order: auto-configuration uses `DeferredImportSelector` which runs after all regular configuration. A regular `@Configuration` class with `@ConditionalOnMissingBean` runs during the first pass of `ConfigurationClassPostProcessor`, before other user `@Configuration` classes have been fully processed. What information is available to evaluate the condition at each point?
