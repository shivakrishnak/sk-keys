---
layout: default
title: "@Qualifier / @Primary"
parent: "Spring Core"
nav_order: 381
permalink: /spring/qualifier-primary/
number: "381"
category: Spring Core
difficulty: ★★☆
depends_on: "@Autowired, Bean, DI (Dependency Injection)"
used_by: "Circular Dependency, AOP (Aspect-Oriented Programming)"
tags: #intermediate, #spring, #architecture
---

# 381 — @Qualifier / @Primary

`#intermediate` `#spring` `#architecture`

⚡ TL;DR — When multiple beans of the same type exist, **`@Primary`** marks one as the default choice and **`@Qualifier("name")`** selects a specific bean by name — both resolve Spring's `NoUniqueBeanDefinitionException` at injection points.

| #381            | Category: Spring Core                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | @Autowired, Bean, DI (Dependency Injection)            |                 |
| **Used by:**    | Circular Dependency, AOP (Aspect-Oriented Programming) |                 |

---

### 📘 Textbook Definition

When the Spring container resolves an `@Autowired` injection point by type and finds multiple candidate beans, it throws `NoUniqueBeanDefinitionException`. Two annotations resolve this ambiguity. **`@Primary`** is placed on a bean definition to designate it as the preferred candidate for injection whenever no further qualifier is specified — it is a container-level default. **`@Qualifier("beanName")`** is placed at the injection point (or on a bean definition) to specify the exact bean name to inject, overriding both type-based matching and `@Primary`. The resolution algorithm is: (1) type match, (2) if multiple, check `@Primary` — use if exactly one, (3) if still ambiguous or no `@Primary`, check field/parameter name against bean names, (4) check `@Qualifier` at injection point, (5) throw if still ambiguous. Custom qualifier annotations (meta-annotated with `@Qualifier`) enable type-safe, IDE-refactorable qualifier aliases. `@Primary` applies globally; `@Qualifier` applies at the specific injection site.

---

### 🟢 Simple Definition (Easy)

When Spring finds two beans of the same type, it does not know which to inject. `@Primary` says "use me by default" and `@Qualifier("name")` says "use this specific one here."

---

### 🔵 Simple Definition (Elaborated)

Imagine you have two email sending implementations — `SmtpEmailSender` and `MockEmailSender`. Both implement `EmailSender`. When `OrderService` declares `@Autowired EmailSender sender`, Spring finds two candidates and fails. Solutions: mark `SmtpEmailSender` with `@Primary` (Spring uses SMTP everywhere unless told otherwise), or add `@Qualifier("mockEmailSender")` at a specific injection point to use the mock for that service only. `@Primary` is a global default; `@Qualifier` is a per-injection-point override. The combination lets you configure sensible defaults while allowing targeted overrides — for example, all services use the primary SMTP sender, but the test service uses the mock.

---

### 🔩 First Principles Explanation

**The ambiguity problem and solutions:**

```java
// Two beans of the same type — Spring cannot choose
@Component class SmtpEmailSender  implements EmailSender { ... }
@Component class MockEmailSender  implements EmailSender { ... }

@Service
class OrderService {
    @Autowired EmailSender sender; // NoUniqueBeanDefinitionException!
}

// ─────────────────────────────────────────────────────────────────
// SOLUTION 1: @Primary — declare a default for all injection points
@Component
@Primary                               // default for ALL EmailSender injections
class SmtpEmailSender implements EmailSender { ... }

// OrderService now gets SmtpEmailSender automatically
// Other services that need the mock must use @Qualifier explicitly

// ─────────────────────────────────────────────────────────────────
// SOLUTION 2: @Qualifier — specify at the injection site
@Service
class NotificationService {
    @Autowired
    @Qualifier("mockEmailSender")      // explicit by bean name
    EmailSender sender;
    // uses mockEmailSender; OrderService still uses @Primary SmtpEmailSender
}

// ─────────────────────────────────────────────────────────────────
// SOLUTION 3: @Qualifier on BOTH definition and injection point
// (type-safe custom qualifier — preferred over string names)
@Qualifier                // meta-annotation
@Retention(RUNTIME)
@interface MockSender {}  // custom qualifier annotation

@Component
@MockSender               // qualifier on definition
class MockEmailSender implements EmailSender { ... }

@Service
class TestNotificationService {
    @Autowired
    @MockSender            // qualifier at injection point — no string typos
    EmailSender sender;
}
```

**Resolution priority (Spring's algorithm):**

```
@Autowired EmailSender sender  →
  1. Find all beans of type EmailSender
     → SmtpEmailSender, MockEmailSender

  2. Is there exactly one? NO → continue

  3. Is one @Primary?
     → YES: SmtpEmailSender is @Primary → inject it
     → NO: continue

  4. Does the field/param name match a bean name?
     → field "sender" → no match
     → field "smtpEmailSender" → match! inject SmtpEmailSender

  5. Is there a @Qualifier at the injection point?
     → @Qualifier("mockEmailSender") → inject MockEmailSender

  6. No resolution → NoUniqueBeanDefinitionException
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT `@Qualifier` / `@Primary`:

What breaks without it:

1. Any application with more than one implementation of an interface fails at startup — `NoUniqueBeanDefinitionException`.
2. Test configurations cannot coexist with production beans of the same type.
3. Multi-datasource applications (primary DB + analytics DB) cannot wire the correct datasource to each repository.
4. Strategy pattern implementations (tax calculation for different regions) cannot be distinguished at injection points.

WITH `@Qualifier` / `@Primary`:
→ Multiple implementations coexist; `@Primary` provides a sensible default.
→ Test beans can override production beans without changing production code.
→ Multi-datasource setups are cleanly managed — `@Primary DataSource` for JPA, qualified `DataSource` for batch jobs.
→ Custom qualifier annotations make disambiguation type-safe and IDE-navigable.

---

### 🧠 Mental Model / Analogy

> Think of a hospital with multiple doctors on call, all of type "Cardiologist." When a patient arrives and says "I need a cardiologist," the charge nurse uses the `@Primary` rule: the head of cardiology is the default. But if a patient's case notes say "see Dr. Chen specifically" (`@Qualifier("drChen")`), the nurse routes to Dr. Chen regardless of who is primary. The default handles the common case; the explicit qualifier handles the specific case.

"Multiple doctors of the same specialty" = multiple beans of the same type
"Head of cardiology as default" = `@Primary` bean
"Patient case notes specifying Dr. Chen" = `@Qualifier("drChen")` at injection point
"Charge nurse routing" = `AutowiredAnnotationBeanPostProcessor` resolution algorithm
"Custom credential card type" = custom qualifier annotation (type-safe @Qualifier)

---

### ⚙️ How It Works (Mechanism)

**@Primary in a multi-datasource setup (common pattern):**

```java
@Configuration
class DataSourceConfig {

    @Bean
    @Primary                           // default for all DataSource injections
    DataSource primaryDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:postgresql://primary-db:5432/app")
            .build();
    }

    @Bean
    @Qualifier("analyticsDataSource")  // must use qualifier to get this one
    DataSource analyticsDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:clickhouse://analytics-db:8123/metrics")
            .build();
    }
}

@Repository
class UserRepository {
    // Gets primaryDataSource — @Primary used automatically
    UserRepository(DataSource dataSource) { ... }
}

@Repository
class MetricsRepository {
    MetricsRepository(
        @Qualifier("analyticsDataSource") DataSource dataSource // explicit
    ) { ... }
}
```

**Custom qualifier annotation (type-safe, avoids string literals):**

```java
// Define
@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Qualifier
public @interface Analytics {}

// Use on bean definition
@Bean
@Analytics
DataSource analyticsDataSource() { ... }

// Use at injection point — no string, no typo risk
@Repository
class MetricsRepository {
    MetricsRepository(@Analytics DataSource dataSource) { ... }
}
// Renaming beans: refactor the annotation, not the string
```

---

### 🔄 How It Connects (Mini-Map)

```
@Autowired (inject by type)
        │
        ▼  multiple candidates found
@Qualifier / @Primary  ◄──── (you are here)
(disambiguation layer)
        │
        ├──── @Primary on bean ──────► default for all unqualified injections
        │
        ├──── @Qualifier at site ───► specific bean for this injection only
        │
        └──── custom @Qualifier ────► type-safe alias, IDE-refactorable
                │
                ▼
      AutowiredAnnotationBeanPostProcessor
      (processes @Qualifier during resolution)
```

---

### 💻 Code Example

**Complete multi-implementation setup with @Primary and @Qualifier:**

```java
// ─── Interface ───────────────────────────────────────────────────
public interface CacheService {
    void put(String key, Object value);
    Optional<Object> get(String key);
}

// ─── Implementations ─────────────────────────────────────────────
@Component
@Primary                               // used for most services
class RedisCacheService implements CacheService {
    // Connects to Redis cluster
    public void put(String key, Object value) { ... }
    public Optional<Object> get(String key)   { ... }
}

@Component("localCache")               // explicit bean name for @Qualifier
class LocalCacheService implements CacheService {
    private final Map<String, Object> map = new ConcurrentHashMap<>();
    public void put(String key, Object value) { map.put(key, value); }
    public Optional<Object> get(String key)   { return Optional.ofNullable(map.get(key)); }
}

// ─── Services ─────────────────────────────────────────────────────
@Service
class ProductService {
    private final CacheService cache; // → RedisCacheService (@Primary)
    ProductService(CacheService cache) { this.cache = cache; }
}

@Service
class HealthCheckService {
    // Health check uses local cache — avoids Redis dependency for self-check
    private final CacheService cache;
    HealthCheckService(@Qualifier("localCache") CacheService cache) {
        this.cache = cache; // → LocalCacheService
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                      |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@Primary` and `@Qualifier` serve the same purpose                         | `@Primary` is a container-wide default (annotates the bean definition). `@Qualifier` is a per-injection-point selector (annotates the injection point). They operate at different scopes                                     |
| If a bean has `@Primary`, it is always selected regardless of `@Qualifier` | `@Qualifier` at an injection point overrides `@Primary`. Explicit qualifier always wins over the default                                                                                                                     |
| There can only be one `@Primary` bean per type                             | Spring allows multiple `@Primary` beans of the same type, but this causes `NoUniqueBeanDefinitionException` — the ambiguity is not resolved. Only exactly one `@Primary` bean per type is valid                              |
| `@Qualifier` must use the exact class name                                 | `@Qualifier` uses the _bean name_ (which defaults to the uncapitalised class name but can be overridden with `@Component("customName")` or `@Bean` method name). Using the wrong name causes `NoSuchBeanDefinitionException` |

---

### 🔥 Pitfalls in Production

**Forgetting `@Qualifier` on a `@Bean` method parameter — gets primary instead of intended bean**

```java
@Configuration
class BatchConfig {
    // BAD: intends to use analyticsDataSource, but gets primary (mainDataSource)
    @Bean
    JobRepository jobRepository(DataSource dataSource) {  // gets @Primary!
        return new JobRepositoryFactoryBean(dataSource).getObject();
    }

    // GOOD: qualify the parameter
    @Bean
    JobRepository jobRepository(
            @Qualifier("analyticsDataSource") DataSource dataSource) {
        return new JobRepositoryFactoryBean(dataSource).getObject();
    }
}
```

---

### 🔗 Related Keywords

- `@Autowired` — the injection annotation that triggers type-based resolution requiring disambiguation
- `Bean` — the container-managed objects that `@Primary` and `@Qualifier` select between
- `DI (Dependency Injection)` — the principle; `@Qualifier` and `@Primary` refine how DI resolution works
- `@Configuration / @Bean` — common location for declaring `@Primary` beans and qualified datasources

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ @Primary      │ On bean definition — global default      │
│ @Qualifier    │ On injection point — per-site override   │
├──────────────┼───────────────────────────────────────────┤
│ RESOLUTION   │ @Qualifier > field name match > @Primary  │
│ ORDER        │ > type-only → NoUniqueBeanDefinitionEx    │
├──────────────┼───────────────────────────────────────────┤
│ CUSTOM       │ @interface MyQual { @Qualifier }          │
│ QUALIFIER    │ → type-safe, refactorable, no strings     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Primary = default doctor on call;       │
│              │  @Qualifier = request a specific doctor." │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application has three `DataSource` beans: `primaryDs` (`@Primary`), `readReplicaDs`, and `analyticsDs`. JPA's `EntityManagerFactory` auto-configuration uses the `@Primary` datasource automatically. A custom `@Repository` class injects `@Qualifier("readReplicaDs") DataSource` for read queries. Describe what happens when a `@Transactional(readOnly = true)` method on a `@Service` calls this repository: does the transaction manager use `primaryDs` or `readReplicaDs`? Is there a way to route read-only transactions to the replica datasource transparently using `AbstractRoutingDataSource`? Describe the implementation pattern.

**Q2.** Custom qualifier annotations (meta-annotated with `@Qualifier`) can carry attributes. For example, `@DataSource(type = DataSourceType.ANALYTICS)`. Explain how Spring processes these attribute-carrying qualifiers: does `AutowiredAnnotationBeanPostProcessor` compare the annotation type only, or does it also compare the annotation's attribute values? What happens if you have two `@DataSource(type = ANALYTICS)` beans and one `@DataSource(type = PRIMARY)` bean and inject with `@DataSource(type = ANALYTICS)`?
