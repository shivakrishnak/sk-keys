---
layout: default
title: "@Autowired"
parent: "Spring Core"
nav_order: 380
permalink: /spring/autowired/
number: "380"
category: Spring Core
difficulty: ★★☆
depends_on: Dependency Injection, Bean, ApplicationContext, @Qualifier
used_by: Constructor injection, Field injection, Setter injection, Spring Testing
tags: #java, #spring, #springboot, #intermediate, #pattern
---

# 380 — @Autowired

`#java` `#spring` `#springboot` `#intermediate` `#pattern`

⚡ TL;DR — Spring's primary injection annotation that marks a constructor, field, or setter as an injection point — the container resolves the matching bean and provides it automatically.

| #380 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Dependency Injection, Bean, ApplicationContext, @Qualifier | |
| **Used by:** | Constructor injection, Field injection, Setter injection, Spring Testing | |

---

### 📘 Textbook Definition

`@Autowired` is Spring's annotation for marking an injection point — a constructor, setter method, or field — where the container should provide a matching bean. By default, injection is required and Spring throws `NoSuchBeanDefinitionException` if no matching bean exists; `@Autowired(required = false)` makes the dependency optional. Bean resolution follows three rules in order: type match, then `@Qualifier` name match, then parameter name match. Since Spring 4.3, a class with a single constructor does not require `@Autowired` — the single constructor is auto-detected as the injection point. The preferred pattern is constructor injection; field injection is discouraged in production code.

---

### 🟢 Simple Definition (Easy)

`@Autowired` tells Spring "fill this in for me." Put it on a constructor or field, and Spring finds the right bean and injects it automatically.

---

### 🔵 Simple Definition (Elaborated)

Without `@Autowired`, you'd have to look up every dependency manually or wire them in XML. With it, you simply annotate your constructor (or field) and Spring does the lookup and injection. The container finds the right implementation, verifies it exists, checks for ambiguity (if two beans match the type, it looks for a qualifier or primary), and injects it at runtime. Since Spring 4.3, even the `@Autowired` annotation itself is optional on single-constructor classes — the presence of the constructor is enough. The annotation is a declaration of need: the container is responsible for fulfilling it.

---

### 🔩 First Principles Explanation

**Resolution algorithm — how Spring picks the right bean:**

When Spring encounters an `@Autowired` injection point, it follows this resolution chain:

```
┌─────────────────────────────────────────────────────┐
│  @AUTOWIRED RESOLUTION ALGORITHM                    │
│                                                     │
│  1. Find all beans matching the declared TYPE       │
│     (e.g. PaymentGateway.class)                    │
│                                                     │
│  2. If exactly one match → inject it               │
│                                                     │
│  3. If multiple matches:                            │
│     a. Is one annotated @Primary? → use it         │
│     b. Is @Qualifier present on injection point?   │
│        → match by qualifier value (bean name)       │
│     c. Does parameter name match a bean name?       │
│        → use that bean                             │
│     d. Still ambiguous?                            │
│        → NoUniqueBeanDefinitionException           │
│                                                     │
│  4. If zero matches:                               │
│     required=true (default) → NoSuchBeanDef…Exc   │
│     required=false → leave null (setter/field)     │
│     Optional<T> → inject Optional.empty()          │
└─────────────────────────────────────────────────────┘
```

**Constructor injection is the recommended pattern from Spring 4.3:**

```java
// Modern pattern: @Autowired not needed on single constructor
@Service
public class CheckoutService {
  private final CartService cart;
  private final PaymentGateway gateway;
  private final OrderRepository orders;

  // Single constructor → auto-detected, no @Autowired needed
  public CheckoutService(CartService cart,
                         PaymentGateway gateway,
                         OrderRepository orders) {
    this.cart    = Objects.requireNonNull(cart);
    this.gateway = Objects.requireNonNull(gateway);
    this.orders  = Objects.requireNonNull(orders);
  }
}
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT @Autowired:**

```
Without @Autowired (pre-annotation Spring or manual):

  Option A: XML wiring
    <bean id="checkout" class="CheckoutService">
      <constructor-arg ref="cartService"/>
      <constructor-arg ref="paymentGateway"/>
    </bean>
    → XML diverges from code → hard to maintain
    → Rename a class → update XML → runtime failures

  Option B: Manual getBean()
    CartService cart = ctx.getBean(CartService.class);
    // Service Locator anti-pattern
    // Hidden dependency — not visible in constructor
    // Untestable without Spring context
```

**WITH @Autowired:**

```
→ Dependencies declared in constructor — visible, verifiable
→ Container wires everything automatically — no XML
→ Constructor injection: testable with plain new MyService(mock)
→ Spring Boot: zero XML, zero manual wiring
→ @Autowired(required=false): optional deps without NPE
→ List<T> injection: all beans of that type injected together
```

---

### 🧠 Mental Model / Analogy

> `@Autowired` is like a **purchase order** in a warehouse. You fill out a PO saying "I need 1× PaymentGateway, medium urgency." The warehouse manager (Spring container) checks the inventory, finds the right item, and delivers it to your workstation. You don't visit the warehouse yourself — you just fill in the form. If two items match your description, the manager asks you for more specifics (`@Qualifier`). If the item is out of stock, the manager either yells at you (`NoSuchBeanDefinitionException`) or leaves your desk empty (`required=false`).

"Purchase order" = @Autowired annotation
"Warehouse manager" = Spring container
"Inventory" = registered beans
"Item description" = the declared interface/class type
"Asking for specifics" = @Qualifier resolution
"Out of stock" = NoSuchBeanDefinitionException

---

### ⚙️ How It Works (Mechanism)

**Three injection styles:**

```java
// 1. CONSTRUCTOR injection (preferred)
@Service
public class UserService {
  private final UserRepository repo;

  // Spring 4.3+: @Autowired optional for single constructor
  public UserService(UserRepository repo) {
    this.repo = repo;
  }
}

// 2. SETTER injection (for optional dependencies)
@Service
public class NotificationService {
  private MetricsRecorder metrics;

  @Autowired(required = false) // optional
  public void setMetrics(MetricsRecorder m) {
    this.metrics = m;
  }
}

// 3. FIELD injection (avoid in production)
@Service
public class OrderService {
  @Autowired
  private PaymentGateway gateway; // hidden dependency
  // Cannot be final, cannot be tested without Spring
}
```

**Special injection forms:**

```java
// Inject ALL beans of a type
@Autowired
private List<MessageSender> senders;
// Injects [EmailSender, SmsSender, PushSender]

// Inject as a Map (key = bean name)
@Autowired
private Map<String, PaymentGateway> gateways;
// {"stripeGateway": StripeGateway, "paypalGateway": ...}

// Inject Optional for nullable dep
@Autowired
private Optional<FeatureFlagService> flagService;
// Optional.empty() if no FeatureFlagService bean

// Inject ObjectProvider for lazy/prototype deps
@Autowired
private ObjectProvider<ReportContext> contextProvider;
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean registered in ApplicationContext
        ↓
  @AUTOWIRED (112)  ← you are here
  (marks injection points in constructors/fields)
        ↓
  Resolved by:
  AutowiredAnnotationBeanPostProcessor (a BPP)
        ↓
  Disambiguation via:
  @Primary (113) — default candidate
  @Qualifier (113) — name-based selection
        ↓
  Injection styles:
  Constructor injection (preferred)
  Setter (optional deps)
  Field (avoid)
  List<T>, Map<String,T>, Optional<T>
```

---

### 💻 Code Example

**Example 1 — Multiple implementations resolved by @Qualifier:**

```java
@Component("stripe")
class StripeGateway implements PaymentGateway {
  public Receipt charge(PaymentRequest r) { /* stripe */ }
}

@Component("paypal")
class PayPalGateway implements PaymentGateway {
  public Receipt charge(PaymentRequest r) { /* paypal */ }
}

@Service
class CheckoutService {
  private final PaymentGateway gateway;

  // Qualifier disambiguates which bean to inject
  public CheckoutService(
      @Qualifier("stripe") PaymentGateway gateway) {
    this.gateway = gateway;
  }
}
```

**Example 2 — Injecting all implementations for a notification fan-out:**

```java
// All senders registered as beans
@Component class EmailSender implements Notifier { ... }
@Component class SmsSender   implements Notifier { ... }
@Component class PushSender  implements Notifier { ... }

@Service
class NotificationService {
  private final List<Notifier> notifiers;

  // Spring injects ALL Notifier beans
  public NotificationService(List<Notifier> notifiers) {
    this.notifiers = notifiers;
  }

  public void notify(User u, String msg) {
    notifiers.forEach(n -> n.send(u, msg));
  }
}
```

**Example 3 — Unit test without Spring context:**

```java
// Constructor injection makes this trivially testable
class CheckoutServiceTest {
  CheckoutService service;

  @BeforeEach
  void setUp() {
    PaymentGateway mockGw = mock(PaymentGateway.class);
    service = new CheckoutService(mockGw); // plain Java!
  }

  @Test
  void shouldChargeOnCheckout() {
    service.checkout(testCart());
    verify(mockGw).charge(any(PaymentRequest.class));
  }
}
// No @SpringBootTest, no context startup, runs in <10ms
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @Autowired is required on every constructor | Since Spring 4.3, a class with a single constructor does not need @Autowired — the constructor is auto-detected |
| @Autowired injects by bean name by default | @Autowired injects by type first. The parameter name is used as a fallback bean-name hint only when multiple type matches exist |
| Field injection and constructor injection behave the same | Field injection uses reflection, cannot be final, hides dependencies, breaks unit tests without Spring, and can produce null fields before injection completes |
| @Autowired(required=false) on a constructor is safe | A required=false on a constructor means the entire constructor injection can be skipped — the bean will still be created via the no-arg constructor |

---

### 🔥 Pitfalls in Production

**1. Ambiguous injection causing NoUniqueBeanDefinitionException**

```java
// Two beans of same type — no @Primary, no @Qualifier
@Component class MysqlRepo implements UserRepository {...}
@Component class MongoRepo  implements UserRepository {...}

@Service
class UserService {
  // FAILS: NoUniqueBeanDefinitionException
  public UserService(UserRepository repo) {...}
}

// FIX option 1: @Primary on preferred impl
@Component @Primary
class MysqlRepo implements UserRepository {...}

// FIX option 2: @Qualifier on injection point
@Service
class UserService {
  public UserService(
      @Qualifier("mysqlRepo") UserRepository repo) {...}
}
```

**2. Circular dependency via field injection — silent at runtime**

```java
// BAD: circular field injection resolves silently (Spring uses proxy)
@Service class A {
  @Autowired B b;
}
@Service class B {
  @Autowired A a;
}
// Spring 6.x throws BeanCurrentlyInCreationException
// Spring 5.x may silently resolve via early reference
// → b.a may be the unproxied raw instance, not @Transactional proxy

// GOOD: constructor injection exposes the cycle at compile/startup:
@Service class A {
  public A(B b) {...} // FAILS at startup → must redesign
}
```

**3. @Autowired on a static field — never works**

```java
// BAD: @Autowired on static field is ignored
@Service
class MyService {
  @Autowired
  private static UserRepository repo; // ALWAYS null!
  // Spring injects instance fields, not static fields
}

// GOOD: use instance field or a @PostConstruct setter
@Service
class MyService {
  @Autowired
  private UserRepository repo; // instance field — works
}
```

---

### 🔗 Related Keywords

- `Dependency Injection` — the pattern @Autowired enables: declare need, container provides
- `@Qualifier` — resolves ambiguity when multiple beans match an injection point type
- `@Primary` — marks a bean as the default when multiple type-matches exist
- `Bean` — the object the container provides at the @Autowired injection point
- `ApplicationContext` — the container that resolves and performs @Autowired injection
- `AutowiredAnnotationBeanPostProcessor` — the BPP that processes @Autowired annotations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Marks injection point; container provides │
│              │ matching bean by type, then qualifier     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Constructor injection (always preferred); │
│              │ setter for optional; List<T> for all impls│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Field injection in production code;       │
│              │ static fields (never injected by Spring)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fill out the PO —                        │
│              │  Spring delivers to your workstation."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Qualifier / @Primary (113) →             │
│              │ @Configuration / @Bean (114) →            │
│              │ Circular Dependency (115)                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring resolves `@Autowired` injection points using `AutowiredAnnotationBeanPostProcessor`. This BPP runs during bean creation and processes each `@Autowired` field/constructor. However, when Spring's context is starting up and a bean has a circular dependency — A depends on B, B depends on A — Spring resolves it using "early bean references" (a half-initialised proxy). Trace exactly what A receives from B when the circle involves field injection vs constructor injection, and explain why constructor injection *correctly* throws `BeanCurrentlyInCreationException` while field injection *incorrectly* resolves silently.

**Q2.** Spring Boot's `@SpringBootTest` with `@MockBean` replaces a real bean with a Mockito mock. Internally, `@MockBean` is processed by `MockitoPostProcessor` — a `BeanFactoryPostProcessor` — that registers the mock as a BeanDefinition before context startup. Explain why this must happen at the BFPP phase rather than the BPP phase, how the mock's BeanDefinition replaces the real bean's definition without affecting the bean's injection points in other beans, and what happens to all the beans that were already injected with the real bean before the mock was registered (hint: they're not yet created).

