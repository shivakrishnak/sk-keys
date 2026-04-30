---
layout: default
title: "Lazy vs Eager Loading"
parent: "Spring Framework"
nav_order: 131
permalink: /spring/lazy-vs-eager-loading/
---
# 131 — Lazy vs Eager Loading

`#spring` `#database` `#performance` `#intermediate`

⚡ TL;DR — Lazy loading fetches associated entities only when accessed; Eager loading fetches them immediately in the same query — trading upfront cost for potential N+1 risk.

| #131 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JPA, N+1 Problem | |
| **Used by:** | @OneToMany, @FetchType, Hibernate SQL optimization | |

---

### 📘 Textbook Definition

In JPA/Hibernate, **Lazy Loading** (`FetchType.LAZY`) defers loading of an association until it is first accessed at runtime, using a proxy. **Eager Loading** (`FetchType.EAGER`) fetches the associated entities immediately as part of the parent query using a JOIN. The JPA defaults are: `@ManyToOne` and `@OneToOne` → EAGER; `@OneToMany` and `@ManyToMany` → LAZY.

### 🟢 Simple Definition (Easy)

Lazy = "load only when I ask for it." Eager = "load everything right now when loading the parent." Lazy is usually faster but requires an open session; Eager is simpler but may load data you don't need.

### 🔩 First Principles Explanation
```sql
-- LAZY: only fires when you call order.getCustomer().getName()
SELECT * FROM orders;                    -- initial
SELECT * FROM customers WHERE id = ?;    -- only when accessed
-- EAGER: always fires one JOIN when loading Order
SELECT o.*, c.* FROM orders o JOIN customers c ON o.customer_id = c.id
```
**Default JPA fetch types:**
```
@OneToOne        → EAGER (bad default — change to LAZY)
@ManyToOne       → EAGER (bad default — change to LAZY)
@OneToMany       → LAZY  (good default)
@ManyToMany      → LAZY  (good default)
```

### 💻 Code Example
```java
@Entity
public class Order {
    // Bad default: EAGER — always JOINs customer even when not needed
    @ManyToOne(fetch = FetchType.EAGER)
    private Customer customer;
    // Good: LAZY — load on demand
    @ManyToOne(fetch = FetchType.LAZY)
    private Customer customer;
    // LAZY collection (default for @OneToMany)
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    private List<OrderItem> items;
}
// Force load in transaction when needed:
@Transactional
public OrderDto getOrderDetails(Long id) {
    Order order = orderRepo.findByIdWithCustomer(id); // uses JOIN FETCH
    return new OrderDto(order.getId(), order.getCustomer().getName(),
                        order.getItems().size());  // safe — in transaction
}
// Common mistake: accessing lazy outside transaction
Order order = orderRepo.findById(1L).get();  // transaction ends here
order.getCustomer().getName();  // LazyInitializationException!
```

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| EAGER is always safer | EAGER always joins — causes unnecessary data loading and slows every query |
| LAZY causes LazyInitializationException always | Only when accessed OUTSIDE an active Hibernate session/transaction |
| @ManyToOne default is LAZY | JPA default for @ManyToOne is EAGER — explicitly change to LAZY |

### 🔗 Related Keywords

- **[N+1 Problem](./130 — N+1 Problem.md)** — the main risk of LAZY loading naively
- **[@Transactional](./127 — @Transactional.md)** — Hibernate session must be open for LAZY loading

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| LAZY        | Load on first access — efficient, N+1 risk          |
+------------------------------------------------------------------+
| EAGER       | Always JOIN load — safe, potential over-fetching     |
+------------------------------------------------------------------+
| BEST PRACT. | Use LAZY everywhere; eagerly fetch with JOIN FETCH   |
+------------------------------------------------------------------+
| LAZE OUTSIDE TX | LazyInitializationException — always use TX     |
+------------------------------------------------------------------+
```
