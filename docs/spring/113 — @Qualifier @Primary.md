---
layout: default
title: "@Qualifier / @Primary"
parent: "Spring Framework"
nav_order: 113
permalink: /spring/qualifier-primary/
---

`#spring` `#internals` `#foundational`

⚡ TL;DR — @Primary marks the default bean to use when multiple candidates match; @Qualifier explicitly names which bean to inject.
## 📘 Textbook Definition
`@Primary` is a class-level annotation designating a bean as the preferred candidate when multiple beans of the same type exist. `@Qualifier` is a parameterized annotation used at the injection point (or on the bean definition) to select a specific bean by name, narrowing the injection when type-based resolution is ambiguous.
## 🟢 Simple Definition (Easy)
If you have two payment services (Stripe and PayPal), add `@Primary` to Stripe to make it the default. Use `@Qualifier("paypalPaymentService")` when you specifically need PayPal.
## 🔵 Simple Definition (Elaborated)
Spring resolves injection by type first. When multiple beans match, it needs help: `@Primary` on a bean says "use me when nothing else specifies" — the default fallback. `@Qualifier("name")` at the injection point says "specifically use this named bean." These two annotations work together to handle the multi-implementation pattern cleanly.
## 🔩 First Principles Explanation
```
Multiple beans of same type
         ↓
@Autowired PaymentService p → AMBIGUOUS!
         ↓
Resolution order:
1. Any @Qualifier at injection point? → use it
2. Any @Primary bean? → use it
3. Name match to field/param name? → use it
4. NoUniqueBeanDefinitionException
```
## 💻 Code Example
```java
public interface PaymentService { void charge(double amount); }
@Service
@Primary  // default — used when no @Qualifier specified
public class StripePaymentService implements PaymentService { ... }
@Service
public class PaypalPaymentService implements PaymentService { ... }
// Usage:
@Service
public class OrderService {
    @Autowired
    PaymentService defaultPayment; // gets Stripe (Primary)
    @Autowired
    @Qualifier("paypalPaymentService") // explicit override
    PaymentService paypalPayment;
}
// Custom qualifier annotation (cleaner than String names)
@Target({ElementType.FIELD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Qualifier
public @interface Paypal { }
@Service @Paypal
public class PaypalPaymentService implements PaymentService { ... }
@Autowired @Paypal PaymentService paypal; // type-safe!
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| @Qualifier only works with bean name | @Qualifier can be a custom annotation — not just name strings |
| @Primary overrides @Qualifier | @Qualifier at injection point ALWAYS wins over @Primary |
| @Primary works per-injection-point | @Primary is on the bean definition — applies everywhere unless overridden |
## 🔗 Related Keywords
- **[@Autowired](./112 — @Autowired.md)** — injection annotation that @Qualifier/@Primary disambiguate
- **[DI (Dependency Injection)](./104 — DI (Dependency Injection).md)** — the underlying mechanism
- **[Bean](./107 — Bean.md)** — the objects being disambiguated
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| @PRIMARY    | Bean-level — default when multiple candidates exist  |
+------------------------------------------------------------------+
| @QUALIFIER  | Injection-point-level — explicit selection by name   |
+------------------------------------------------------------------+
| PRIORITY    | @Qualifier wins over @Primary                        |
+------------------------------------------------------------------+
| BEST PRACTICE| Create custom @Qualifier annotations for type safety |
+------------------------------------------------------------------+
```
## 🧠 Think About This Before We Continue
**Q1.** Can a bean have both `@Primary` and `@Qualifier`? What does each do independently?
**Q2.** If you have a `@Configuration` class with two `@Bean` methods both returning `DataSource`, how do you handle injection of a specific one in another bean?
**Q3.** What is `@ConditionalOnMissingBean` in Spring Boot, and how does it relate to the `@Primary` / default bean concept?
