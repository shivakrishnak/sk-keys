---
layout: default
title: "Spring - Annotations"
parent: "Spring"
grand_parent: "Interview Mastery"
nav_order: 4
permalink: /interview/spring/annotations/
topic: Spring
subtopic: Annotations
keywords:
  - Component and Stereotype Annotations
  - Autowired and Injection
  - Configuration and Bean
  - Conditional Annotations
  - Profile
difficulty_range: ★☆☆ to ★★☆
status: in-progress
version: 2
---

# Component and Stereotype Annotations

**TL;DR** - `@Component`, `@Service`, `@Repository`, and `@Controller` are stereotype annotations that mark classes for auto-detection by component scanning, with `@Repository` and `@Controller` adding specific behavior (exception translation, request handling).

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every bean must be manually declared in XML or `@Configuration` classes. Adding a new service class requires editing a config file. Developers forget to register beans and get confusing `NoSuchBeanDefinitionException` at runtime.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Annotate a class, Spring auto-discovers it and manages its lifecycle. No manual registration needed.

**Level 2 - How to use it (junior developer):**

```java
@Service  // Business logic
public class OrderService {
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) {
        this.repo = repo;
    }
}

@Repository  // Data access
public class OrderRepository {
    // Spring translates SQL exceptions ->
    // DataAccessException hierarchy
}

@Controller  // Web layer (views)
@RestController  // Web layer (REST API)
```

**Level 3 - How it works (mid-level engineer):**

Hierarchy:

```
@Component (base - generic bean)
  |-- @Service (business logic - no extra behavior)
  |-- @Repository (+ exception translation)
  |-- @Controller (+ request mapping)
       |-- @RestController (+@ResponseBody)
```

**Key differences:**

- `@Component`: Generic. Use when no specific layer applies.
- `@Service`: Semantic marker. No technical difference from @Component.
- `@Repository`: Activates `PersistenceExceptionTranslationPostProcessor` - translates JPA/Hibernate exceptions into Spring's `DataAccessException`.
- `@Controller`: Enables `@RequestMapping` method resolution in DispatcherServlet.

**Level 4 - Mastery (senior/staff+ engineer):**

**Component scanning rules:**

```java
@SpringBootApplication
// Scans com.myapp and ALL sub-packages
// Main class should be in root package!

// Customize scan:
@ComponentScan(
    basePackages = "com.myapp",
    excludeFilters = @Filter(
        type = FilterType.REGEX,
        pattern = "com\\.myapp\\.legacy\\..*"))
```

**Custom stereotype annotation:**

```java
@Target(TYPE)
@Retention(RUNTIME)
@Service
@Transactional(readOnly = true)
public @interface ReadOnlyService {}

// Usage:
@ReadOnlyService
public class ReportService { }
// Gets both @Service and @Transactional behavior
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. All stereotypes are @Component - they're auto-detected by scanning
2. Only @Repository adds behavior (exception translation)
3. Component scan starts from @SpringBootApplication's package downward

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: When would you use @Component vs @Service?**

_Why they ask:_ Tests understanding of layered architecture.

_Strong answer:_

Use `@Service` for business logic classes (service layer). Use `@Component` for:

- Infrastructure beans (converters, validators, formatters)
- Classes that don't fit a specific layer
- Custom cross-cutting utilities

Functionally identical at runtime. The distinction is semantic - it communicates intent and aids code navigation. Teams should enforce consistent usage through code reviews or ArchUnit rules:

```java
// ArchUnit test:
@Test
void servicesShouldBeInServicePackage() {
    classes()
        .that().areAnnotatedWith(Service.class)
        .should().resideInAPackage("..service..")
        .check(importedClasses);
}
```

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Component and Stereotype Annotations. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Autowired and Injection

**TL;DR** - `@Autowired` tells Spring to inject a dependency. Constructor injection (preferred) makes dependencies explicit, immutable, and testable. Field injection is convenient but hides dependencies and complicates testing.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Classes create their own dependencies with `new`. Testing requires modifying production code. Changing an implementation requires touching every class that uses it.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of creating objects yourself, you declare what you need, and Spring provides it automatically.

**Level 2 - How to use it (junior developer):**

```java
// BAD: Field injection (hidden dependency)
@Service
public class OrderService {
    @Autowired
    private PaymentGateway gateway;
}

// GOOD: Constructor injection (explicit)
@Service
public class OrderService {
    private final PaymentGateway gateway;

    // @Autowired optional since Spring 4.3
    // (single constructor auto-wired)
    public OrderService(PaymentGateway gateway) {
        this.gateway = gateway;
    }
}
```

**Level 3 - How it works (mid-level engineer):**

**Injection types:**

| Type        | Pros                                     | Cons                                       |
| ----------- | ---------------------------------------- | ------------------------------------------ |
| Constructor | Immutable, testable, explicit, fail-fast | Verbose with many deps                     |
| Setter      | Optional deps, reconfigurable            | Mutable, nullable                          |
| Field       | Concise                                  | Untestable without reflection, hidden deps |

**Resolving ambiguity (multiple implementations):**

```java
public interface NotificationService {}

@Service class EmailNotification
    implements NotificationService {}
@Service class SmsNotification
    implements NotificationService {}

// 1. @Primary - default choice
@Primary @Service
class EmailNotification implements
    NotificationService {}

// 2. @Qualifier - explicit selection
@Service
class OrderService {
    OrderService(
        @Qualifier("smsNotification")
        NotificationService ns) {}
}

// 3. Collection injection - get all
@Service
class Dispatcher {
    Dispatcher(
        List<NotificationService> all) {
        // Contains both implementations
    }
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Why constructor injection is superior:**

1. **Immutable:** `final` fields - thread safe by construction
2. **Fail-fast:** Missing deps cause startup failure, not NPE at runtime
3. **Testable:** Just `new Service(mockDep)` in tests - no Spring context needed
4. **No reflection:** Constructor is a normal Java mechanism
5. **Circular dependency detection:** Fails immediately (not silently created via proxies)

**@Lazy for expensive beans:**

```java
@Service
class ReportService {
    // Proxy injected, real bean created on
    // first method call
    ReportService(@Lazy ExpensiveClient c) {
        this.client = c;
    }
}
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Constructor injection > setter > field (immutable, testable, fail-fast)
2. `@Qualifier` or `@Primary` resolves ambiguity with multiple beans
3. Single constructor doesn't need `@Autowired` (auto-detected since 4.3)

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: Why is field injection considered an anti-pattern?**

_Why they ask:_ Tests engineering principles understanding.

_Strong answer:_

1. **Hidden dependencies:** Can't see what a class needs without reading internals
2. **Untestable without Spring:** Must use reflection or start full context to inject mocks
3. **No immutability:** Can't make fields `final`
4. **Allows too many dependencies:** No constructor parameter count to signal "this class does too much"
5. **Circular dependency hiding:** Field injection allows Spring to create circular deps silently

Real impact: A class with field-injected 10 dependencies looks clean but violates SRP. With constructor injection, the 10-parameter constructor is an immediate code smell.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Autowired and Injection. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Configuration and Bean

**TL;DR** - `@Configuration` classes are special `@Component` classes that use `@Bean` methods to define beans programmatically, with CGLIB proxying ensuring that inter-method calls return the same singleton instance (full mode).

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Some beans require complex initialization logic, third-party library classes can't be annotated with `@Component`, and conditional bean creation requires programmatic control that annotations alone can't provide.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you can't put `@Component` on a class (third-party library), you write a factory method annotated with `@Bean` inside a `@Configuration` class.

**Level 2 - How to use it (junior developer):**

```java
@Configuration
public class AppConfig {

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(WRITE_DATES_AS_TIMESTAMPS);
    }
}
```

**Level 3 - How it works (mid-level engineer):**

**Full mode vs Lite mode:**

```java
// Full mode: @Configuration (CGLIB proxy)
@Configuration
public class FullConfig {
    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();
    }

    @Bean
    public JdbcTemplate jdbc() {
        // Calls dataSource() - returns SAME bean
        // (CGLIB intercepts the call)
        return new JdbcTemplate(dataSource());
    }
}

// Lite mode: @Component with @Bean
@Component
public class LiteConfig {
    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();
    }

    @Bean
    public JdbcTemplate jdbc() {
        // Calls dataSource() - creates NEW instance!
        // (No CGLIB proxy)
        return new JdbcTemplate(dataSource());
    }
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**proxyBeanMethods = false (Spring Boot standard):**

```java
// Spring Boot auto-configs use this for speed:
@Configuration(proxyBeanMethods = false)
public class LightConfig {
    // No CGLIB proxy overhead
    // But: don't call @Bean methods internally!
    // Use parameter injection instead:
    @Bean
    public JdbcTemplate jdbc(DataSource ds) {
        return new JdbcTemplate(ds);
    }
}
```

This is faster (no proxy class generation) and GraalVM native-image friendly. Rule: never call one @Bean method from another when using `proxyBeanMethods = false`.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `@Configuration` = CGLIB proxy ensuring @Bean method calls return singletons
2. Use `@Bean` for third-party classes you can't annotate
3. `proxyBeanMethods=false` for performance (Spring Boot's default in auto-configs)

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: What's the difference between @Configuration and @Component with @Bean methods?**

_Why they ask:_ Tests understanding of Spring internals.

_Strong answer:_

`@Configuration` (full mode): Spring creates a CGLIB subclass proxy. When one @Bean method calls another @Bean method, the proxy intercepts and returns the existing singleton from the container - not a new instance.

`@Component` (lite mode): No proxy. @Bean methods are plain Java methods. Calling one @Bean method from another creates a new instance each time - breaking singleton semantics.

```java
@Configuration
class Full {
    @Bean A a() { return new A(); }
    @Bean B b() { return new B(a()); }
    // a() returns same instance both times
}

@Component
class Lite {
    @Bean A a() { return new A(); }
    @Bean B b() { return new B(a()); }
    // a() creates NEW A each time - 2 instances!
}
```

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Configuration and Bean. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Conditional Annotations

**TL;DR** - `@Conditional` annotations enable beans to be created only when specific conditions are met (class on classpath, property set, bean missing), powering Spring Boot's auto-configuration magic.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
A library must work across different environments. Without conditionals, you'd need separate JARs or profiles for every possible configuration. Auto-configuration would be impossible.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
"Only create this bean IF...": if a class exists, if a property is set, if no other bean of this type exists. It's Spring's if-statement for bean creation.

**Level 2 - How to use it (junior developer):**

```java
// Only create if Redis is on classpath
@Configuration
@ConditionalOnClass(RedisTemplate.class)
public class RedisConfig {
    @Bean
    public RedisTemplate<String, Object>
            redisTemplate(
            RedisConnectionFactory factory) {
        RedisTemplate<String, Object> t =
            new RedisTemplate<>();
        t.setConnectionFactory(factory);
        return t;
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Common conditional annotations:

| Annotation                     | True when...                 |
| ------------------------------ | ---------------------------- |
| `@ConditionalOnClass`          | Class exists on classpath    |
| `@ConditionalOnMissingClass`   | Class NOT on classpath       |
| `@ConditionalOnBean`           | Bean of type exists          |
| `@ConditionalOnMissingBean`    | Bean of type does NOT exist  |
| `@ConditionalOnProperty`       | Property has specified value |
| `@ConditionalOnWebApplication` | Running in web context       |
| `@ConditionalOnExpression`     | SpEL expression is true      |

**This is how auto-configuration works:**

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(
    prefix = "spring.datasource",
    name = "url")
public class DataSourceAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(
            DataSourceProperties props) {
        // Only created if:
        // 1. DataSource class on classpath
        // 2. spring.datasource.url property set
        // 3. No user-defined DataSource bean
        return props.initializeDataSourceBuilder()
            .build();
    }
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Custom condition:**

```java
public class OnKubernetesCondition
        implements Condition {
    public boolean matches(
            ConditionContext ctx,
            AnnotatedTypeMetadata metadata) {
        return System.getenv(
            "KUBERNETES_SERVICE_HOST") != null;
    }
}

@Conditional(OnKubernetesCondition.class)
@Configuration
public class K8sConfig { }
```

**Debugging conditions:**

```properties
debug=true
# Startup log shows:
# Positive matches:
#   DataSourceAutoConfiguration matched:
#     @ConditionalOnClass found: DataSource
# Negative matches:
#   MongoAutoConfiguration did not match:
#     @ConditionalOnClass did not find:
#       MongoClient
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `@ConditionalOnMissingBean` = "back off if user defines their own"
2. `@ConditionalOnClass` = "only if this library is a dependency"
3. `debug=true` shows which auto-configs matched and why

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: How would you create a custom auto-configuration starter?**

_Why they ask:_ Tests deep Spring Boot understanding.

_Strong answer:_

Structure:

```
my-starter/
  src/main/java/
    com/lib/MyAutoConfiguration.java
  src/main/resources/
    META-INF/spring/
      org.springframework.boot.autoconfigure.
        AutoConfiguration.imports
```

```java
@AutoConfiguration
@ConditionalOnClass(MyLibrary.class)
@EnableConfigurationProperties(MyProps.class)
public class MyAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MyLibrary myLibrary(MyProps props) {
        return new MyLibrary(props.getUrl());
    }
}
```

Key principles:

1. Always use `@ConditionalOnMissingBean` (user can override)
2. Use `@ConfigurationProperties` for type-safe config
3. Use `@ConditionalOnClass` to avoid classpath issues
4. Test with `ApplicationContextRunner`

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Conditional Annotations. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Profile

**TL;DR** - `@Profile` activates beans or configuration classes only in specific environments (dev, test, prod), enabling environment-specific behavior without code changes.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
if-else chains checking environment variables at runtime. Accidentally connecting to production database during development. Test configurations leaking into production builds.

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Mark beans with the environment they belong to. Only beans matching the active profile get created.

**Level 2 - How to use it (junior developer):**

```java
@Configuration
@Profile("dev")
public class DevConfig {
    @Bean
    public DataSource dataSource() {
        // H2 in-memory for fast development
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }
}

@Configuration
@Profile("prod")
public class ProdConfig {
    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:postgresql://...");
        return ds;
    }
}
```

Activate: `spring.profiles.active=dev`

**Level 3 - How it works (mid-level engineer):**

**Multiple profiles and expressions:**

```java
@Profile("!prod")         // NOT production
@Profile("dev | test")    // dev OR test
@Profile("cloud & aws")   // cloud AND aws
```

**Profile-specific properties:**

```
application.yml          # always loaded
application-dev.yml      # loaded when dev active
application-prod.yml     # loaded when prod active
```

**Default profile:** `spring.profiles.default=dev` (used when no profile is explicitly active).

**Level 4 - Mastery (senior/staff+ engineer):**

**Profile groups (Boot 2.4+):**

```yaml
# application.yml
spring:
  profiles:
    group:
      production:
        - prod
        - metrics
        - ssl
      development:
        - dev
        - debug
```

Activate `production` -> activates `prod`, `metrics`, `ssl`.

**Testing with profiles:**

```java
@SpringBootTest
@ActiveProfiles("test")
class OrderServiceTest {
    // Uses test profile beans and properties
}
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `@Profile("dev")` = bean only exists when dev profile active
2. `application-{profile}.yml` loaded on top of `application.yml`
3. Profile groups combine multiple profiles under one name

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Profile. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

