---
layout: default
title: "@Autowired"
parent: "Spring Framework"
nav_order: 112
permalink: /spring/autowired/
---
⚡ TL;DR — @Autowired tells Spring to inject a matching bean into a field, constructor parameter, or setter method — resolving the dependency by type.
## 📘 Textbook Definition
`@Autowired` is a Spring annotation that marks a dependency injection point. When placed on a constructor, setter method, or field, Spring's `AutowiredAnnotationBeanPostProcessor` resolves and injects the appropriate bean by type. If multiple beans of the same type exist, `@Qualifier` or `@Primary` is needed to disambiguate.
## 🟢 Simple Definition (Easy)
`@Autowired` is the "please give me this bean" annotation. Put it on a constructor or field, and Spring automatically finds and provides the matching object from its container.
## 🔵 Simple Definition (Elaborated)
`@Autowired` works by type-matching: Spring looks in its bean registry for a bean assignable to the declared type. For constructors, a single constructor in Spring 4.3+ doesn't even need the annotation — Spring infers injection automatically. For ambiguous multi-bean situations, combine with `@Qualifier("beanName")` or mark one bean `@Primary`.
## 🔩 First Principles Explanation
**Resolution algorithm:**
```
1. Find all beans matching the declared type
2. If exactly one → inject it
3. If zero → NoSuchBeanDefinitionException (unless required=false)
4. If multiple → check for @Primary bean → use it if found
5. If no @Primary → match by field name to bean name
6. If still ambiguous → NoUniqueBeanDefinitionException
→ Fix: add @Qualifier("specificBeanName")
```
## 🧠 Mental Model / Analogy
> `@Autowired` is like a **job posting listing required skills** (type). HR (Spring) searches all employees (beans) for someone with those skills. If one person matches, they're assigned. If multiple match, you need to specify the name (`@Qualifier`).
## 💻 Code Example
```java
// ── Constructor injection (PREFERRED — no @Autowired needed in Spring 4.3+) ──
@Service
public class OrderService {
    private final PaymentService paymentService;
    private final EmailService emailService;
    public OrderService(PaymentService paymentService, EmailService emailService) {
        this.paymentService = paymentService;
        this.emailService = emailService;
    }
}
// ── Field injection (CONVENIENT but avoid in production) ──────────────────
@Service
public class ReportService {
    @Autowired private UserRepository userRepo;      // injected by type
    @Autowired private CacheService cacheService;    // injected by type
}
// ── Setter injection (for optional dependencies) ──────────────────────────
@Service
public class NotificationService {
    private PushService pushService;
    @Autowired(required = false) // won't fail if no PushService bean exists
    public void setPushService(PushService ps) {
        this.pushService = ps;
    }
}
// ── Multiple implementations — need @Qualifier ────────────────────────────
@Service
public class PaymentProcessor {
    @Autowired
    @Qualifier("stripePaymentService") // specify which implementation
    private PaymentService paymentService;
}
// ── Inject all implementations ────────────────────────────────────────────
@Service
public class NotificationDispatcher {
    @Autowired
    private List<NotificationChannel> channels; // injects ALL beans of this type
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| @Autowired injects by name | Default is by type; falls back to name only for disambiguation |
| Must use @Autowired on every constructor | Single-constructor classes don't need @Autowired since Spring 4.3 |
| @Autowired always required=true | Can pass `required=false` or use `Optional<T>` for optional beans |
| Field injection is as good as constructor | Field injection is hidden coupling, breaks immutability, harder to test |
## 🔥 Pitfalls in Production
**Pitfall: NoUniqueBeanDefinitionException**
```java
// Two beans of same type:
@Service class StripePaymentService implements PaymentService {}
@Service class PaypalPaymentService implements PaymentService {}
// Fails: expected single matching bean, found 2
@Autowired PaymentService paymentService;
// Fix A: @Primary on preferred implementation
@Primary @Service class StripePaymentService implements PaymentService {}
// Fix B: @Qualifier to be explicit
@Autowired @Qualifier("stripePaymentService") PaymentService paymentService;
```
## 🔗 Related Keywords
- **[DI (Dependency Injection)](./104 — DI (Dependency Injection).md)** — the mechanism @Autowired implements
- **[@Qualifier / @Primary](./113 — @Qualifier @Primary.md)** — disambiguation for multiple matching beans
- **[BeanPostProcessor](./110 — BeanPostProcessor.md)** — @Autowired processed by AutowiredAnnotationBeanPostProcessor
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Inject a matching bean by type                      |
+------------------------------------------------------------------+
| PREFER      | Constructor injection — explicit, immutable, testable|
+------------------------------------------------------------------+
| AMBIGUITY   | @Qualifier or @Primary to resolve multiple matches  |
+------------------------------------------------------------------+
| OPTIONAL    | @Autowired(required=false) or Optional<T>            |
+------------------------------------------------------------------+
```
## 🧠 Think About This Before We Continue
**Q1.** Spring resolves `@Autowired` by type first, then by name. What exact field/parameter name does it use for name-based fallback resolution?
**Q2.** You have `@Autowired List<PaymentService>`. What does Spring inject? In what order are the elements sorted?
**Q3.** What is `@Inject` (JSR-330) and how does it differ from `@Autowired`?
