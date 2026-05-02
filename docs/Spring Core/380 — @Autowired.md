---
layout: default
title: "@Autowired"
parent: "Spring Core"
nav_order: 380
permalink: /spring/autowired/
number: "380"
category: Spring Core
difficulty: ★★☆
depends_on: DI (Dependency Injection), Bean, BeanPostProcessor, ApplicationContext
used_by: Circular Dependency, @Qualifier / @Primary, Bean Lifecycle
tags: #intermediate, #spring, #foundational, #architecture
---

# 380 — @Autowired

`#intermediate` `#spring` `#foundational` `#architecture`

⚡ TL;DR — `@Autowired` is the annotation that tells Spring to inject a dependency from the container by type. Constructor injection (implicit in Spring 5+ for single-constructor beans) is the recommended approach; field and setter injection are legacy patterns.

| #380            | Category: Spring Core                                                  | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | DI (Dependency Injection), Bean, BeanPostProcessor, ApplicationContext |                 |
| **Used by:**    | Circular Dependency, @Qualifier / @Primary, Bean Lifecycle             |                 |

---

### 📘 Textbook Definition

`@Autowired` is a Spring annotation that marks a constructor, field, setter method, or arbitrary method as an injection point — instructing the container to resolve and inject a matching bean from the `ApplicationContext`. Resolution is primarily by type (`Class` matching), with `@Qualifier` used to narrow by bean name when multiple candidates of the same type exist. `@Autowired` injection is processed by `AutowiredAnnotationBeanPostProcessor` during Phase 2/4 of the bean lifecycle. From Spring 4.3 onward, a class with a single constructor does not need `@Autowired` on it — the framework infers constructor injection implicitly. The `required` attribute (default `true`) controls whether the container throws `NoSuchBeanDefinitionException` if no matching bean is found; `required = false` makes the dependency optional. For collections (`List<T>`, `Set<T>`, `Map<String, T>`), Spring injects all beans of the matching type. Constructor injection is the strongly recommended approach over field injection because it enables immutability (`final` fields), makes dependencies explicit, and supports testing without the Spring container.

---

### 🟢 Simple Definition (Easy)

`@Autowired` tells Spring: "find a bean in the container that matches this type and inject it here." You do not call `new` — Spring provides the object for you.

---

### 🔵 Simple Definition (Elaborated)

Without `@Autowired`, you would have to construct and wire all your objects manually. `@Autowired` is the signal to Spring that says "I need this dependency — you provide it." You can place it on a constructor (Spring creates the bean passing in the matching dependency), on a setter method (Spring calls the setter after constructing the bean), or on a field (Spring directly sets the field value via reflection). Constructor injection is preferred because it makes dependencies visible, enforces them at construction time (the object is never in an incomplete state), allows `final` fields (immutable dependencies), and works perfectly in tests without Spring. Field injection is short to write but has hidden dependencies — you cannot tell from the public API what a class needs, and testing requires reflection hacks or the Spring container.

---

### 🔩 First Principles Explanation

**Three injection styles — with trade-offs:**

```java
// STYLE 1: Constructor injection ✅ RECOMMENDED
@Service
class OrderService {
    private final OrderRepository repo;     // final → immutable
    private final PaymentGateway gateway;   // final → immutable

    // @Autowired optional in Spring 4.3+ for single constructor
    @Autowired
    OrderService(OrderRepository repo, PaymentGateway gateway) {
        this.repo    = Objects.requireNonNull(repo,    "repo required");
        this.gateway = Objects.requireNonNull(gateway, "gateway required");
    }
}
// Pros: final fields, fail-fast null check, testable without Spring
// Test: new OrderService(mockRepo, mockGateway) — no container needed


// STYLE 2: Setter injection ⚠️ use for optional dependencies only
@Service
class ReportService {
    private NotificationService notifier;

    @Autowired(required = false)  // optional dep — app works without it
    void setNotifier(NotificationService notifier) {
        this.notifier = notifier;
    }
}
// Cons: field is mutable, nullable, object can be constructed without dep


// STYLE 3: Field injection ❌ avoid in production code
@Service
class UserService {
    @Autowired  // Spring sets via reflection — bypasses encapsulation
    private UserRepository repo;  // NOT final — mutable, no null check
}
// Cons: cannot test without Spring, hides dependencies, no final fields
```

**How `AutowiredAnnotationBeanPostProcessor` resolves the dependency:**

```
@Autowired UserRepository repo

Resolution algorithm:
  Step 1: Find all beans of type UserRepository in ApplicationContext
    → Found: JpaUserRepository, CachedUserRepository  (2 candidates)

  Step 2: Is there exactly ONE? No → proceed to disambiguation

  Step 3: Is one marked @Primary? Yes → use it
    Or: Does the field/param name match a bean name? Yes → use it

  Step 4: Is @Qualifier present?
    @Qualifier("cachedUserRepository") → use CachedUserRepository

  Step 5: No disambiguation → throw NoUniqueBeanDefinitionException
```

**Injecting collections — all beans of a type:**

```java
@Service
class NotificationService {
    private final List<NotificationChannel> channels;

    // Spring injects ALL beans implementing NotificationChannel
    // in @Order / Ordered order
    @Autowired
    NotificationService(List<NotificationChannel> channels) {
        this.channels = channels;
    }

    // Also works:
    // Set<NotificationChannel> channels → unordered set of all instances
    // Map<String, NotificationChannel> → beanName → bean mappings
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT `@Autowired`:

What breaks without it:

1. Developers must manually construct and wire every dependency — `new OrderService(new JpaOrderRepository(new HikariDataSource(...)))` — brittle object graphs in code.
2. No centralised control of dependency resolution — if `OrderRepository` implementation changes, every construction site must be updated.
3. No support for injecting all implementations of an interface — building plugin systems is complex.
4. Testing requires manually stubbing object graphs — no simple mock substitution.

WITH `@Autowired`:
→ Dependencies declared; Spring resolves and injects — application code does not know which implementation class is used.
→ Switching implementations requires only changing one `@Bean` definition or `@Primary` annotation.
→ Collection injection enables strategy and plugin patterns with zero code changes when new implementations are added.
→ Constructor injection makes test setup a simple `new ServiceClass(mockDep)` call.

---

### 🧠 Mental Model / Analogy

> Think of a hotel restaurant ordering system. `@Autowired` is like a kitchen station declaring: "I need a supplier for fresh tomatoes." The hotel procurement system (Spring container) looks at all registered suppliers (beans), finds the one that provides tomatoes (type match), and delivers them to the station. The kitchen station does not know which farm provides the tomatoes — it just uses them. If the hotel has two tomato suppliers, procurement asks the station to be more specific (add a `@Qualifier`). If the requirement is critical, procurement fails loudly if no supplier is found (`required = true`).

"Kitchen station declaring a need" = `@Autowired` annotation
"Procurement system" = `AutowiredAnnotationBeanPostProcessor`
"Supplier match by product type" = bean resolution by type
- "Two suppliers → need clarification" = multiple beans → need `@Qualifier`
- "Required supply, no supplier" = `required = true` → `NoSuchBeanDefinitionException`

---

### ⚙️ How It Works (Mechanism)

**AutowiredAnnotationBeanPostProcessor processing flow:**

```
postProcessBeforeInitialization(bean, beanName):
  1. Find all @Autowired / @Value injection points in bean class
     (constructor, fields, setter methods)

  2. For each injection point:
     a. Determine required type (OrderRepository)
     b. Resolve from BeanFactory:
        - beanFactory.getBean(OrderRepository.class)  [by type]
        - If multiple: check @Primary, then name match, then @Qualifier
        - If still ambiguous: NoUniqueBeanDefinitionException
        - If not found and required=true: NoSuchBeanDefinitionException

  3. Inject value:
     - Field: Field.set(bean, resolvedValue)  [via reflection]
     - Setter: method.invoke(bean, resolvedValue)
     - Constructor: injected at construction time (Phase 1)
```

**Spring 4.3+ implicit constructor injection:**

```java
// Spring 4.3+: single constructor → @Autowired implied, no annotation needed
@Service
class ProductService {
    private final ProductRepository repo;

    // No @Autowired — Spring infers constructor injection automatically
    ProductService(ProductRepository repo) {
        this.repo = repo;
    }
}

// Multiple constructors: must use @Autowired to designate the one to use
@Service
class LegacyService {
    @Autowired  // tells Spring which constructor to use for DI
    LegacyService(Repository repo, Validator validator) { ... }

    LegacyService(Repository repo) { ... }  // NOT used for injection
}
```

---

### 🔄 How It Connects (Mini-Map)

```
DI (Dependency Injection)
(the pattern — constructor, setter, interface)
        │
        ▼
@Autowired  ◄──── (you are here)
(Spring's annotation implementation of DI)
        │
        ├──── type-based resolution ──► multiple beans of same type
        │                                        │
        │                                        ▼
        │                               @Qualifier / @Primary
        │                               (disambiguation)
        │
        ├──── processed by ──────────► AutowiredAnnotationBeanPostProcessor
        │
        └──── circular dependency ───► Circular Dependency (potential issue)
                                        (constructor injection detects early,
                                         field injection may mask it)
```

---

### 💻 Code Example

**Example 1 — Constructor injection with validation (production pattern):**

```java
@Service
public class OrderService {
    private final OrderRepository    orderRepo;
    private final InventoryService   inventory;
    private final PaymentGateway     payment;

    // Spring 4.3+: no @Autowired annotation needed — single constructor
    public OrderService(OrderRepository orderRepo,
                        InventoryService inventory,
                        PaymentGateway payment) {
        this.orderRepo = Objects.requireNonNull(orderRepo,  "orderRepo is required");
        this.inventory = Objects.requireNonNull(inventory,  "inventory is required");
        this.payment   = Objects.requireNonNull(payment,    "payment is required");
    }

    // Test-friendly: new OrderService(mockRepo, mockInventory, mockPayment)
}
```

**Example 2 — Injecting all strategy implementations:**

```java
public interface TaxStrategy {
    BigDecimal calculate(Order order);
    String region();
}

@Component class USTaxStrategy    implements TaxStrategy { ... }
@Component class EUTaxStrategy    implements TaxStrategy { ... }
@Component class UKTaxStrategy    implements TaxStrategy { ... }

@Service
class TaxService {
    // Spring injects ALL three TaxStrategy beans automatically
    private final Map<String, TaxStrategy> strategies;

    // Map key = bean name; value = bean instance
    @Autowired
    TaxService(Map<String, TaxStrategy> strategies) {
        this.strategies = strategies;
    }

    public BigDecimal calculate(Order order, String region) {
        TaxStrategy strategy = strategies.get(region + "TaxStrategy");
        if (strategy == null) throw new UnsupportedRegionException(region);
        return strategy.calculate(order);
    }
    // Adding a new region: just add a new @Component implementing TaxStrategy
    // No changes to TaxService — open/closed principle
}
```

**Example 3 — Optional dependency with @Autowired(required = false):**

```java
@Service
class EmailService {
    private final EmailSender primarySender;
    private EmailSender fallbackSender; // optional — app works without it

    EmailService(EmailSender primarySender) {
        this.primarySender = primarySender;
    }

    @Autowired(required = false) // no NoSuchBeanDefinitionException if absent
    void setFallbackSender(EmailSender fallbackSender) {
        this.fallbackSender = fallbackSender;
    }

    void send(Email email) {
        try {
            primarySender.send(email);
        } catch (EmailException e) {
            if (fallbackSender != null) {
                fallbackSender.send(email);
            } else {
                throw e;
            }
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                     | Reality                                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@Autowired` is required on constructors in Spring Boot                           | Since Spring 4.3, a single constructor is automatically used for injection — no `@Autowired` annotation needed. The annotation is only required when there are multiple constructors                                                                                                                                                                                         |
| Field injection and constructor injection behave identically                      | Field injection uses reflection to set private fields; constructor injection provides values via the constructor. They differ in testability (constructor injection needs no Spring for tests), immutability (field injection cannot use `final`), and circular dependency detection (constructor injection fails fast; field injection may succeed with a proxy workaround) |
| `@Autowired` with `required = false` on a constructor means zero-arg construction | `required = false` means: if no matching bean is found, set the field to null (or skip setter call). A constructor with `required = false` on it is only valid on one of multiple constructors — it tells Spring which to prefer, not that the argument can be null                                                                                                          |
| Spring injects a new instance every time `@Autowired` is used                     | Spring injects from the container based on scope. For singleton-scoped beans (the default), the SAME instance is injected everywhere it is needed. A new instance is only created if the bean is prototype-scoped                                                                                                                                                            |

---

### 🔥 Pitfalls in Production

**Field injection breaks unit tests — hidden dependency problem**

```java
// BAD: field injection — dependencies invisible, test requires Spring
@Service
class PricingService {
    @Autowired private TaxService taxService;     // hidden dependency
    @Autowired private DiscountService discount;  // hidden dependency

    public BigDecimal price(Item item) {
        return item.getBasePrice()
                   .add(taxService.calculate(item))
                   .subtract(discount.apply(item));
    }
}

// Unit test requires: SpringRunner, context, or reflection hacks:
@SpringBootTest // loads full context — slow, brittle
class PricingServiceTest { ... }

// GOOD: constructor injection — dependencies explicit, test without Spring
@Service
class PricingService {
    private final TaxService taxService;
    private final DiscountService discount;

    PricingService(TaxService taxService, DiscountService discount) {
        this.taxService = taxService;
        this.discount   = discount;
    }
}

// Clean unit test — no Spring needed
class PricingServiceTest {
    PricingService svc = new PricingService(
        new FakeTaxService(),    // simple test double
        new FakeDiscountService()
    );

    @Test void calculatesCorrectly() { ... }
}
```

---

**Circular dependency via constructor injection — detected at startup (good), but signals design issue**

```java
// Spring throws BeanCurrentlyInCreationException at startup
@Service class ServiceA {
    ServiceA(ServiceB b) { } // A needs B
}
@Service class ServiceB {
    ServiceB(ServiceA a) { } // B needs A — circular!
}
// Spring cannot construct A without B, cannot construct B without A
// Constructor injection exposes this design flaw immediately

// Wrong fix: switch to field injection (hides the circular dep)
// Right fix: extract shared logic to a third ServiceC, or use an event
```

---

### 🔗 Related Keywords

- `DI (Dependency Injection)` — the principle that `@Autowired` implements in Spring
- `@Qualifier / @Primary` — annotation pair used to disambiguate when multiple beans of the same type exist
- `BeanPostProcessor` — specifically `AutowiredAnnotationBeanPostProcessor` which processes `@Autowired`
- `Circular Dependency` — the problem that arises when beans with `@Autowired` have mutually dependent constructors
- `Bean` — the container-managed object that `@Autowired` resolves and injects
- `ApplicationContext` — the registry from which `@Autowired` candidates are resolved

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RESOLUTION   │ By type → @Primary → name match →        │
│ ORDER        │ @Qualifier → NoUniqueBeanDefinitionEx     │
├──────────────┼───────────────────────────────────────────┤
│ INJECTION    │ ✅ Constructor — final fields, testable   │
│ STYLES       │ ⚠️  Setter — optional deps only          │
│              │ ❌ Field — avoid, hides deps              │
├──────────────┼───────────────────────────────────────────┤
│ SPRING 4.3+  │ Single constructor: @Autowired not needed │
├──────────────┼───────────────────────────────────────────┤
│ OPTIONAL DEP │ @Autowired(required = false)              │
│              │ or: Optional<T> / ObjectProvider<T>       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Autowired = tell Spring: 'I need this   │
│              │  — you find it and deliver it.'"          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@Autowired` resolves beans by type. If you have an interface `PaymentGateway` with three implementations — `StripeGateway` (`@Primary`), `PayPalGateway` (`@Profile("paypal")`), and `MockGateway` (`@Profile("test")`) — describe the full resolution sequence for: (a) a production environment where only `StripeGateway` is active, (b) a test environment where `MockGateway` is active and `@Primary` on `StripeGateway` is also present but `StripeGateway` is NOT profile-gated, and (c) a missing `@Qualifier` situation where BOTH `StripeGateway` (primary) and `PayPalGateway` (non-primary) are active. Explain which exception is thrown, when, and by which component.

**Q2.** When Spring processes `@Autowired` on a `List<SecurityFilter>` injection point, it injects all beans implementing `SecurityFilter` in registration order. However, `SecurityFilter` implementations need to run in a specific order (authentication before authorisation before rate-limiting). Describe three separate mechanisms Spring provides to control the order of beans in an `@Autowired` collection (`@Order`, `Ordered` interface, `PriorityOrdered`), explain which one takes precedence when multiple mechanisms are combined on the same bean, and identify the edge case where `@Order` on the bean class is ignored in favour of `@Order` on the `@Bean` factory method.
