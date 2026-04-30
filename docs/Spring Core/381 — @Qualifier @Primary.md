---
layout: default
title: "@Qualifier / @Primary"
parent: "Spring Core"
nav_order: 381
permalink: /spring/qualifier-primary/
number: "381"
category: Spring Core
difficulty: ★★☆
depends_on: "@Autowired, Bean, ApplicationContext, Dependency Injection"
used_by: "Bean disambiguation, Spring Testing, @MockBean, @ConditionalOnBean"
tags: #java, #spring, #springboot, #intermediate, #pattern
---

# 381 — @Qualifier / @Primary

`#java` `#spring` `#springboot` `#intermediate` `#pattern`

⚡ TL;DR — `@Primary` marks one bean as the default when multiple match a type; `@Qualifier` picks a specific bean by name at each injection point — two complementary disambiguation tools.

| #381 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | @Autowired, Bean, ApplicationContext, Dependency Injection | |
| **Used by:** | Bean disambiguation, Spring Testing, @MockBean, @ConditionalOnBean | |

---

### 📘 Textbook Definition

When the Spring container resolves an `@Autowired` injection point and finds more than one bean matching the required type, it raises `NoUniqueBeanDefinitionException` unless disambiguation is provided. **`@Primary`** designates one bean as the default candidate — the container selects it whenever no other qualifier is specified. **`@Qualifier`** narrows selection at the injection point by specifying the target bean's name or a custom qualifier annotation. The two annotations serve complementary roles: `@Primary` is a blanket default set at the bean definition; `@Qualifier` is a per-injection-point override. Both can be combined: `@Primary` sets the default, `@Qualifier` overrides it where needed.

---

### 🟢 Simple Definition (Easy)

If two beans implement the same interface, Spring doesn't know which to inject. `@Primary` says "use this one by default." `@Qualifier("name")` says "use this specific one here."

---

### 🔵 Simple Definition (Elaborated)

Imagine you have `StripeGateway` and `PayPalGateway`, both implementing `PaymentGateway`. Without guidance, Spring can't choose. `@Primary` on `StripeGateway` makes it the default everywhere. If one endpoint must use PayPal, you add `@Qualifier("payPalGateway")` at that specific injection point to override the default. This pattern is especially useful in multi-datasource applications, where one is primary and others are explicitly selected by name in specific repositories.

---

### 🔩 First Principles Explanation

**The disambiguation problem:**

Spring's `@Autowired` resolves by type. When multiple beans share a type — common in real applications with multiple data sources, payment providers, notification channels, or feature flags — type-based resolution fails:

```java
@Component class StripeGateway  implements PaymentGateway {}
@Component class PayPalGateway  implements PaymentGateway {}
@Component class SquareGateway  implements PaymentGateway {}

@Service
class CheckoutService {
  // NoUniqueBeanDefinitionException:
  // expected single matching bean but found 3
  public CheckoutService(PaymentGateway gw) {...}
}
```

**Two complementary solutions:**

`@Primary` is a "global default" — set it once on the most commonly used bean. `@Qualifier` is a "local override" — used at specific injection points to select a non-default.

```
┌─────────────────────────────────────────────────────┐
│  RESOLUTION PRIORITY                                │
│                                                     │
│  1. @Qualifier at injection point (highest)         │
│     → selects specific bean by name/annotation      │
│                                                     │
│  2. @Primary on the bean definition                 │
│     → used when no @Qualifier present               │
│                                                     │
│  3. Parameter name matches bean name (fallback)     │
│     → e.g. param "stripeGateway" matches bean name  │
│                                                     │
│  4. NoUniqueBeanDefinitionException (fail)          │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT @Primary / @Qualifier:**

```
Without disambiguation:

  Multiple DataSource beans:
    JPA auto-configuration needs to pick one
    → NoUniqueBeanDefinitionException at startup
    → Multi-datasource app impossible without workaround

  Testing:
    @MockBean for PaymentGateway — but 3 impl exist
    → Spring doesn't know which to replace

  Framework autoconfiguration:
    Spring Boot DataSourceAutoConfiguration picks a
    primary DataSource for JPA transaction management
    → Must be @Primary or Boot can't configure JPA
```

**WITH @Primary / @Qualifier:**

```
→ @Primary on main DataSource → JPA auto-configures to it
→ @Qualifier("reporting") on secondary DataSource
  → reporting repositories get their own source
→ @MockBean replaces @Primary bean in tests
→ Multi-implementation patterns (Strategy via DI) work
→ Clean: no hardcoded bean names in most injection points
```

---

### 🧠 Mental Model / Analogy

> `@Primary` and `@Qualifier` are like the **default printer and the printer-specific dialog** on your OS. When you print, your default printer (marked `@Primary`) is used unless you open the specific printer dialog (`@Qualifier`) and type "Conference Room HP." The default works for 90% of cases; the dialog exists for the exceptions.

"Default printer" = `@Primary` bean
"Printing without opening dialog" = @Autowired with no @Qualifier
"Specific printer dialog" = `@Qualifier("conferencePrinter")`
"90% use default" = most injection points don't need @Qualifier
"Exceptions" = specific services that need a non-primary bean

---

### ⚙️ How It Works (Mechanism)

**`@Primary` — set at bean definition:**

```java
// The default PaymentGateway for all injection points
@Component
@Primary
class StripeGateway implements PaymentGateway {
  public Receipt charge(PaymentRequest r) { /* stripe */ }
}

// Alternative — requires @Qualifier at injection point
@Component
class PayPalGateway implements PaymentGateway {
  public Receipt charge(PaymentRequest r) { /* paypal */ }
}
```

**`@Qualifier` — set at injection point:**

```java
@Service
class CheckoutService {
  private final PaymentGateway defaultGateway;
  private final PaymentGateway legacyGateway;

  public CheckoutService(
      PaymentGateway defaultGateway,             // @Primary = Stripe
      @Qualifier("payPalGateway")                // explicit name
      PaymentGateway legacyGateway) {
    this.defaultGateway = defaultGateway;
    this.legacyGateway  = legacyGateway;
  }
}
```

**Custom qualifier annotations (preferred for large projects):**

```java
// Define semantic qualifiers
@Target({ElementType.FIELD, ElementType.PARAMETER,
         ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Qualifier
public @interface ReportingDataSource {}

// Apply to bean definition
@Bean
@ReportingDataSource
DataSource reportingDs(ReportingDsProperties p) {
  return DataSourceBuilder.create()
      .url(p.getUrl()).build();
}

// Apply at injection point — type-safe, refactor-safe
@Service
class ReportService {
  public ReportService(
      @ReportingDataSource DataSource ds) {...}
}
// No string "reportingDataSource" to typo or forget
```

---

### 🔄 How It Connects (Mini-Map)

```
Multiple beans of same type registered in context
        ↓
  @AUTOWIRED resolution (112)
  Finds > 1 matching bean → disambiguation needed
        ↓
  @PRIMARY (113)  ← you are here (global default)
  @QUALIFIER (113)  ← you are here (per-site override)
        ↓
  Used prominently in:
  Multi-DataSource apps (primary + read-replica)
  Payment gateway selection
  Feature-flagged bean alternatives
  Spring Boot test @MockBean replacement
```

---

### 💻 Code Example

**Example 1 — Multi-datasource with @Primary:**

```java
@Configuration
public class DataSourceConfig {
  @Bean
  @Primary   // Used by JPA auto-configuration and most repos
  @ConfigurationProperties("spring.datasource.primary")
  public DataSource primaryDataSource() {
    return DataSourceBuilder.create().build();
  }

  @Bean
  @Qualifier("analyticsDs")
  @ConfigurationProperties("spring.datasource.analytics")
  public DataSource analyticsDataSource() {
    return DataSourceBuilder.create().build();
  }
}

// 99% of repositories use primary DataSource automatically
@Repository
class UserRepository extends JpaRepository<User, Long> {}

// Analytics repo explicitly requests its own source
@Repository
class ClickEventRepository {
  private final JdbcTemplate jdbc;

  ClickEventRepository(
      @Qualifier("analyticsDs") DataSource ds) {
    this.jdbc = new JdbcTemplate(ds);
  }
}
```

**Example 2 — @Primary replaced by @MockBean in tests:**

```java
// Production: StripeGateway is @Primary
// Tests: @MockBean replaces the @Primary bean
@SpringBootTest
class CheckoutServiceTest {
  @MockBean
  PaymentGateway gateway; // replaces @Primary StripeGateway

  @Autowired
  CheckoutService service;

  @Test
  void shouldChargeOnCheckout() {
    when(gateway.charge(any())).thenReturn(mockReceipt());
    service.checkout(testCart());
    verify(gateway).charge(any(PaymentRequest.class));
  }
}
```

**Example 3 — Runtime bean selection with ApplicationContext:**

```java
@Service
class DynamicPaymentRouter {
  private final Map<String, PaymentGateway> gateways;

  // Inject ALL PaymentGateway beans by name
  DynamicPaymentRouter(
      Map<String, PaymentGateway> gateways) {
    this.gateways = gateways;
  }

  public Receipt route(Order order, String provider) {
    PaymentGateway gw = gateways.getOrDefault(
        provider + "Gateway",
        gateways.get("stripeGateway")); // fallback to primary
    return gw.charge(PaymentRequest.from(order));
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @Primary replaces @Qualifier | @Primary sets a default; @Qualifier at an injection point overrides it. They cooperate, not compete |
| @Qualifier value must match bean class name | @Qualifier value must match the bean's registered name. Default bean name is the lower-camel-case of the class name, but can be customised with @Component("name") |
| You can only have one @Primary per application | You can have multiple @Primary beans as long as each applies to a different type hierarchy — no two @Primary beans of the same type |
| @Qualifier and @Primary work at runtime dynamically | Both are resolved at context startup during normal injection. The Map<String, T> injection pattern is what enables runtime selection |

---

### 🔥 Pitfalls in Production

**1. Two @Primary beans of the same type**

```java
// BAD: two @Primary beans compete → NoUniqueBeanDef exception
@Component @Primary class StripeGateway implements PaymentGateway {}
@Component @Primary class PayPalGateway  implements PaymentGateway {}
// Spring throws NoUniqueBeanDefinitionException:
// more than one 'primary' bean found

// GOOD: only one @Primary per type; others via @Qualifier
@Component @Primary  class StripeGateway  implements PaymentGateway {}
@Component           class PayPalGateway  implements PaymentGateway {}
```

**2. String @Qualifier values causing typo bugs**

```java
// BAD: string qualifier — typo goes undetected until runtime
@Service
class ReportService {
  ReportService(@Qualifier("reportngDataSource") // typo!
                DataSource ds) {...}
  // Fails at startup with NoSuchBeanDefinitionException
  // Only caught by running the app
}

// GOOD: custom qualifier annotation — compile-time safe
@Service
class ReportService {
  ReportService(@ReportingDataSource DataSource ds) {...}
  // IDE catches @ReportingDataSource typos at compile time
}
```

---

### 🔗 Related Keywords

- `@Autowired` — the injection mechanism that triggers disambiguation
- `Bean` — the target objects being disambiguated
- `ApplicationContext` — stores beans by name and type for resolution
- `@MockBean` — replaces the `@Primary` bean of a type in Spring Boot tests
- `@ConditionalOnMissingBean` — auto-configuration uses @Primary to detect existing beans
- `DI (Dependency Injection)` — the pattern @Qualifier and @Primary serve

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ @Primary = global default for a type;     │
│              │ @Qualifier = local override at inject site │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple beans of same type; multi-ds;    │
│              │ strategy pattern via DI                   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ String @Qualifier in large projects —     │
│              │ use custom qualifier annotations instead  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Primary is the default printer;         │
│              │  @Qualifier opens the printer dialog."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Configuration / @Bean (114) →            │
│              │ Circular Dependency (115)                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot's `DataSourceAutoConfiguration` requires exactly one `@Primary` DataSource to configure JPA's `EntityManagerFactory` and `TransactionManager`. Describe the full startup failure mode when you add a second `DataSource` bean without marking either `@Primary` — what autoconfiguration condition fires, what exception is thrown, and what is the canonical Spring Boot multi-datasource configuration pattern (including which JPA and transaction manager beans must also be duplicated and marked @Primary).

**Q2.** `@Qualifier` resolves by bean name. Bean names are case-sensitive in Spring's registry. Explain the subtle ordering bug that occurs when a `@Configuration` class defines two `@Bean` methods that return the same interface type, neither is `@Primary`, one is named via `@Bean("primaryGateway")` and the other via `@Bean("legacyGateway")`, but the injection site uses `@Qualifier("PrimaryGateway")` (capital P) — is this resolved correctly, and how does Spring's `DefaultListableBeanFactory` handle case sensitivity in qualifier matching?

