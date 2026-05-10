---
version: 2
layout: default
title: "@Qualifier  @Primary"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /spring/qualifier-primary/
id: SPR-059
category: Spring Core
difficulty: ★★☆
depends_on: "@Autowired, Bean, DI, BeanFactory"
used_by: Any Spring Service with Multiple Implementations, Feature Flags
related: "@Autowired, @Conditional, @Profile, Named"
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# SPR-018 - @Qualifier  @Primary

⚡ TL;DR - @Primary marks the default bean when multiple candidates exist; @Qualifier selects a specific bean by name at each injection point - they resolve @Autowired ambiguity.

| #381            | Category: Spring Core                                           | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Autowired, Bean, DI, BeanFactory                               |                 |
| **Used by:**    | Any Spring Service with Multiple Implementations, Feature Flags |                 |
| **Related:**    | @Autowired, @Conditional, @Profile, Named                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have two `DataSource` implementations: `ReadOnlyDataSource` for replica reads and `PrimaryDataSource` for writes. Both implement `DataSource`. Every service that needs the primary data source calls `@Autowired DataSource ds` and Spring throws `NoUniqueBeanDefinitionException` - it found two beans of type `DataSource` and has no way to choose. You must either merge them into one class (losing the read/write split) or avoid having two beans of the same type (losing polymorphism).

**THE BREAKING POINT:**
Type-based injection breaks the moment you have two implementations of the same interface. This is a common scenario in real applications: multiple `MessageSender` implementations (email, SMS, push), multiple `PaymentGateway` providers (Stripe, PayPal), multiple data sources (primary, replica, archive). Without disambiguation, you can't have multiple implementations of the same interface registered as beans simultaneously.

**THE INVENTION MOMENT:**
"This is exactly why @Primary and @Qualifier were created."

---

### 📘 Textbook Definition

**@Primary** is a Spring annotation placed on a `@Bean` method or `@Component` class to designate it as the preferred candidate when multiple beans of the same type exist. When `@Autowired` finds multiple candidates, the `@Primary` bean wins without any injection-point annotation required. **@Qualifier** is a Spring annotation placed at both the definition site (`@Component` / `@Bean`) and the injection point (`@Autowired` field/parameter) to provide name-based disambiguation. When `@Autowired` finds multiple candidates, `@Qualifier("beanName")` at the injection point selects the specific bean. The two are complementary: `@Primary` sets a sensible default; `@Qualifier` overrides the default at specific injection points.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
@Primary says "this is the default when there's a tie"; @Qualifier says "I want this specific one."

**One analogy:**

> Imagine a coffee shop with three baristas. @Primary marks one barista as the "on-call" default - any unspecified order goes to them. @Qualifier is a name tag - if you say "I want Alex's coffee specifically," you bypass the default and get Alex regardless of who's on call.

**One insight:**
`@Primary` is a definition-time hint; `@Qualifier` is an injection-point override. Use `@Primary` for "95% of the time, use this one" and `@Qualifier` for "in this specific place, use the other one." Together they give you an O(1) disambiguation system that scales across any number of implementations.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `@Primary` is resolved at the definition level - the bean itself says "I'm the default."
2. `@Qualifier` is resolved at the injection point - the consumer says "I want this specific one."
3. `@Qualifier` takes precedence over `@Primary` - the explicit always wins over the default.

**DERIVED DESIGN:**
The resolution algorithm (highest to lowest priority):

1. Exact type + `@Qualifier` match → inject the qualified bean
2. Exact type + `@Primary` mark → inject the primary bean
3. Exact type + field/parameter name matches a bean name → inject by name
4. Multiple candidates, no disambiguation → throw `NoUniqueBeanDefinitionException`

**THE TRADE-OFFS:**

**@Primary Gain:** Zero annotation overhead at every injection point. Default selection is centralized.
**@Primary Cost:** Only one `@Primary` per type. The "default" is baked into the bean definition - changing it requires code change, not just configuration.

**@Qualifier Gain:** Precise control at every injection point. Works with any number of implementations.
**@Qualifier Cost:** String-based bean names are not refactoring-safe. Custom qualifier annotations (enums, typed) solve this.

---

### 🧪 Thought Experiment

**SETUP:**
A notification system has `EmailSender` and `SmsSender`, both implementing `MessageSender`. 80% of the code uses email; 20% uses SMS for high-priority alerts.

**WHAT HAPPENS WITH @Primary only:**

1. `@Primary` added to `EmailSender`.
2. `@Autowired MessageSender sender` in 95 services → all get `EmailSender` automatically.
3. Alert service: `@Autowired MessageSender sender` → gets `EmailSender` (wrong for alerts).
4. Must add `@Qualifier("smsSender")` to the alert service only.

**WHAT HAPPENS WITHOUT @Primary, @Qualifier only:**

1. All 95 services need `@Qualifier("emailSender")`.
2. 95 places to update when `EmailSender` is renamed.
3. Easy to forget `@Qualifier` on a new service → runtime failure.

**COMBINED APPROACH (correct):**

- `@Primary` on `EmailSender` → default for the 95 services, no annotation needed.
- `@Qualifier("smsSender")` only on the alert service → explicit override.
- Total annotations: 1 (`@Primary`) + 1 (`@Qualifier`) instead of 95.

**THE INSIGHT:**
`@Primary` is about minimizing boilerplate for the common case. `@Qualifier` is about precision for the exceptional case. Use both together - they complement each other perfectly.

---

### 🧠 Mental Model / Analogy

> `@Primary` is the restaurant's "chef's recommendation" - the item starred on the menu that you get if you say "surprise me." `@Qualifier` is pointing at a specific dish on the menu and saying "I want that exact one." Most customers get the recommendation (no overhead); connoisseurs get their specific choice (@Qualifier).

- "Chef's recommendation" → `@Primary` bean
- "Pointing at specific dish" → `@Qualifier("beanName")`
- "Customer saying surprise me" → `@Autowired` without qualifier
- "Customer ordering by name" → `@Autowired @Qualifier("smsSender")`

**Where this analogy breaks down:** Unlike a restaurant, Spring allows only one `@Primary` per type in the entire context - having two `@Primary` beans of the same type causes the same `NoUniqueBeanDefinitionException` as having no qualifier at all.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When Spring finds two beans of the same type and you don't specify which one to inject, it panics. @Primary says "in case of tie, use me." @Qualifier says "always use this specific one here."

**Level 2 - How to use it (junior developer):**
Add `@Primary` to the bean definition of the most-used implementation. At injection points where you want the non-primary implementation, add `@Qualifier("beanName")` alongside `@Autowired`. The bean name defaults to the class name in camelCase, or you can specify it: `@Component("mySpecialName")`.

**Level 3 - How it works (mid-level engineer):**
During `@Autowired` resolution in `AutowiredAnnotationBeanPostProcessor`, `DefaultListableBeanFactory.determinePrimaryCandidate()` checks for `@Primary` among all candidates. `AutowireCandidateResolver.getSuggestedValue()` checks for `@Qualifier` at the injection point. The qualifier value is matched against bean names (and any custom qualifier annotations). Spring also supports `@Qualifier` as a meta-annotation, enabling typed custom qualifiers (e.g., `@Database(replica)`) that avoid string-based naming.

**Level 4 - Why it was designed this way (senior/staff):**
The two-annotation design reflects different ownership. `@Primary` is owned by the bean: "I am the canonical implementation." This is a design-time decision by the bean's author. `@Qualifier` is owned by the consumer: "I specifically need the non-default." This is a usage-time decision by the caller. Separating these concerns allows the bean author and the consumer to make independent decisions - changing which implementation is `@Primary` doesn't require changing every injection point, and adding a `@Qualifier` override at one site doesn't affect others. Custom `@Qualifier` annotations (using `@Qualifier` as a meta-annotation) extend this to type-safe disambiguation, eliminating the string-based refactoring problem.

---

### ⚙️ How It Works (Mechanism)

**Resolution sequence in `DefaultListableBeanFactory`:**

```
@Autowired UserRepository repo
Candidates: [jdbcRepo, jpaRepo]
    ↓
Step 1: Check @Qualifier at injection point
  @Qualifier("jdbcRepo") present?
    YES → inject jdbcRepo
    NO  → continue
    ↓
Step 2: Check @Primary on candidates
  Any candidate has @Primary?
    YES → inject the @Primary bean
    NO  → continue
    ↓
Step 3: Match by field/param name
  field name "repo" matches any bean name?
    YES → inject matched bean
    NO  → throw NoUniqueBeanDefinitionException
```

**Custom qualifier annotation (type-safe):**

```java
@Target({ElementType.FIELD, ElementType.PARAMETER,
         ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Qualifier  // meta-annotation
public @interface DatabaseType {
    Type value();
    enum Type { PRIMARY, REPLICA }
}

// On beans:
@Component
@DatabaseType(Type.PRIMARY)
public class PrimaryDataSource implements DataSource { ... }

@Component
@DatabaseType(Type.REPLICA)
public class ReplicaDataSource implements DataSource { ... }

// At injection points:
@Autowired
@DatabaseType(Type.REPLICA)
private DataSource readReplica;  // type-safe, rename-refactorable
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Multiple beans of same type registered
    ↓
@Autowired resolution triggered
    ↓
Check @Qualifier at injection point
   ← YOU ARE HERE (@Qualifier/Primary resolves ambiguity)
    ↓
Check @Primary on candidates
    ↓
Inject resolved bean
    ↓
Application continues startup
```

**FAILURE PATH:**

```
Two @Primary beans of the same type registered
    ↓
NoUniqueBeanDefinitionException:
"expected single matching bean but found 2 primary candidates"
    ↓
Context refresh fails
```

**WHAT CHANGES AT SCALE:**
Resolution is a startup-time operation - no runtime overhead. The concern at scale is _maintainability_: dozens of `@Qualifier` strings scattered across hundreds of injection points become error-prone. Custom qualifier annotations (type-safe) scale much better than string-based `@Qualifier("beanName")` in large codebases.

---

### 💻 Code Example

**Example 1 - @Primary for default implementation:**

```java
public interface PaymentGateway {
    PaymentResult charge(PaymentRequest req);
}

@Component
@Primary  // used by 95% of injection points
public class StripeGateway implements PaymentGateway { ... }

@Component
public class PayPalGateway implements PaymentGateway { ... }

// Most services - gets StripeGateway automatically
@Service
public class OrderService {
    @Autowired PaymentGateway gateway;  // gets Stripe (Primary)
}

// Exception - explicitly needs PayPal
@Service
public class LegacyOrderService {
    @Autowired
    @Qualifier("payPalGateway")
    PaymentGateway gateway;  // gets PayPal explicitly
}
```

**Example 2 - @Qualifier in constructor injection:**

```java
@Service
public class NotificationService {
    private final MessageSender primarySender;
    private final MessageSender backupSender;

    @Autowired
    public NotificationService(
            @Qualifier("emailSender") MessageSender primarySender,
            @Qualifier("smsSender") MessageSender backupSender) {
        this.primarySender = primarySender;
        this.backupSender = backupSender;
    }
}
```

**Example 3 - Custom qualifier annotation (production-grade):**

```java
// Type-safe qualifier
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.TYPE})
@Qualifier
public @interface ForReadReplica {}

// Bean definition
@Configuration
public class DataSourceConfig {

    @Bean
    @Primary  // default: primary DB
    public DataSource primaryDataSource() {
        return buildDataSource("jdbc:primary");
    }

    @Bean
    @ForReadReplica  // custom qualifier
    public DataSource replicaDataSource() {
        return buildDataSource("jdbc:replica");
    }
}

// Injection - refactoring-safe
@Service
public class ReportService {
    @Autowired
    @ForReadReplica
    private DataSource readSource;  // no string literals!
}
```

---

### ⚖️ Comparison Table

| Strategy             | Overhead                | Refactoring Safety       | Scope             | Use Case                    |
| -------------------- | ----------------------- | ------------------------ | ----------------- | --------------------------- |
| `@Primary`           | Zero at injection sites | N/A (definition-site)    | One per type      | 95% use the same impl       |
| `@Qualifier(String)` | Per injection point     | String - not rename-safe | Multiple per type | Need specific impl here     |
| Custom @Qualifier    | Per injection point     | Type-safe, rename-safe   | Multiple per type | Production, large codebases |
| `@Profile`           | Configuration-level     | Type-safe                | Whole profile     | env-specific beans          |

**How to choose:** Use `@Primary` for the dominant implementation. Use custom `@Qualifier` annotations (not string-based) for type-safe disambiguation in production codebases. Use `@Profile` when the implementation choice depends on the deployment environment.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                             |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| @Qualifier always takes precedence over @Primary | Correct - @Qualifier at the injection point wins over @Primary on the bean.                                                                         |
| Only one @Qualifier can exist in an application  | You can have as many @Qualifier values as you have beans. The issue is two @Primary beans of the same type - only one @Primary per type is allowed. |
| @Primary makes a bean "better" or "stronger"     | @Primary only affects injection disambiguation - it has no effect on bean behavior, lifecycle, or priority in any other context.                    |
| @Qualifier must match the bean's class name      | @Qualifier matches the bean name, which defaults to the lowercased class name but can be set explicitly: @Component("customName").                  |

---

### 🚨 Failure Modes & Diagnosis

**Two @Primary beans of same type**

**Symptom:**
`NoUniqueBeanDefinitionException: expected single matching bean but found 2 primary candidates: 'stripeGateway', 'paypalGateway'`

**Root Cause:**
Both candidates are annotated with `@Primary`. Spring can't determine which is "more primary."

**Diagnostic Command / Tool:**

```bash
# Find all @Primary beans
grep -r "@Primary" src/ --include="*.java"
```

**Fix:**

```java
// Remove @Primary from one; it should apply to exactly one impl per type
@Component
@Primary
public class StripeGateway implements PaymentGateway { }

@Component
// No @Primary here
public class PayPalGateway implements PaymentGateway { }
```

**Prevention:** Enforce one `@Primary` per interface via ArchUnit: `noClasses().that().areAnnotatedWith(Primary.class).should().haveMoreThanOneAnnotation(Primary.class)` (or a custom rule checking all `@Primary` beans by interface).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `@Autowired` - @Qualifier and @Primary exist to resolve @Autowired ambiguity
- `Bean` - you're disambiguating between multiple beans of the same type
- `DI` - the injection context where these annotations apply

**Builds On This (learn these next):**

- `@Configuration / @Bean` - how to define beans where @Primary can be applied
- `@Profile` - environment-based bean selection (alternative for env-specific disambiguation)
- `@Conditional` - programmatic condition-based bean selection

**Alternatives / Comparisons:**

- `@Named (JSR-330)` - the standard Java equivalent of @Qualifier
- `@Profile` - selects between implementations at the environment level, not injection-point level

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ @Primary: the default when types tie.     │
│              │ @Qualifier: the specific choice here      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ @Autowired fails when multiple beans of   │
│ SOLVES       │ the same type are registered              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ @Qualifier > @Primary - explicit always   │
│              │ overrides default. Use custom @Qualifier  │
│              │ annotations for type-safe disambiguation  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple implementations of same interface│
│              │ need to coexist as separate Spring beans  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid two @Primary beans of same type;    │
│              │ avoid string @Qualifier in large codebases│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ @Primary: low overhead vs inflexible;     │
│              │ @Qualifier: precise vs string fragility   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Primary is the standing order;          │
│              │  @Qualifier is the special request."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Configuration/@Bean → Circular Dependency│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's test support provides `@MockBean` to replace a real bean with a Mockito mock. When a `@MockBean` replaces a `@Primary` bean, does the mock also inherit the `@Primary` status? Trace what `@MockBean` does to the application context and determine whether other beans that expected the original `@Primary` implementation receive the mock or the real bean.

**Q2.** You have three `DataSource` implementations: one `@Primary` for production, one for read replicas, and one for test databases. A `@DataJpaTest` slice test should automatically use the test DataSource, not the production one. But `@DataJpaTest` doesn't use profiles. How does Spring Boot's test slice mechanism ensure the test DataSource is selected over the `@Primary` production one? What mechanism overrides `@Primary` in this case?
