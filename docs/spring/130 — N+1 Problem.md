---
layout: default
title: "N+1 Problem"
parent: "Spring Framework"
nav_order: 130
permalink: /spring/n1-problem/
---
⚡ TL;DR — The N+1 problem occurs when loading a parent entity also triggers N separate queries to load each child entity — instead of one efficient JOIN query.
## 📘 Textbook Definition
The N+1 select problem is a performance anti-pattern in ORM frameworks where fetching N parent entities results in N additional queries to fetch their associated child entities — one query per parent — instead of a single query using a JOIN or IN clause. It causes significant database load and latency at scale.
## 🟢 Simple Definition (Easy)
You load 100 orders (1 query). Each order has a customer. Instead of loading all customers in one query, the ORM fires 100 separate customer queries. 1 + 100 = 101 queries total. That's the N+1 problem.
## 🔵 Simple Definition (Elaborated)
JPA/Hibernate by default uses LAZY loading on associations — it doesn't fetch related entities until they're accessed. When you iterate over a list and access a lazy-loaded field on each entity, Hibernate fires a separate SQL query per entity. In production with thousands of records, this creates a query avalanche that can overwhelm the database.
## 🔩 First Principles Explanation
```
// N orders loaded
List<Order> orders = orderRepo.findAll();  // Query 1: SELECT * FROM orders
// Loop accesses lazy-loaded customer for each order
for (Order order : orders) {
    order.getCustomer().getName();   // Query 2,3,4...N+1: SELECT * FROM customers WHERE id=?
}
// 1 + N queries total!
// Fix: JOIN FETCH — one query with JOIN
@Query("SELECT o FROM Order o JOIN FETCH o.customer")
List<Order> findAllWithCustomer();
// Just 1 query with JOIN — no lazy loading triggered
```
## 💻 Code Example
```java
// Entity definition (LAZY by default for @ManyToOne in Hibernate)
@Entity
public class Order {
    @ManyToOne(fetch = FetchType.LAZY)  // N+1 trap!
    @JoinColumn(name = "customer_id")
    private Customer customer;
}
// ── BAD: N+1 ─────────────────────────────────────────────────────────────────
@Transactional
public List<String> getCustomerNames() {
    List<Order> orders = orderRepo.findAll(); // 1 query
    return orders.stream()
        .map(o -> o.getCustomer().getName())  // N queries — one per order!
        .collect(toList());
}
// ── FIX 1: JOIN FETCH in JPQL ─────────────────────────────────────────────────
@Query("SELECT DISTINCT o FROM Order o JOIN FETCH o.customer")
List<Order> findAllWithCustomer();
// ── FIX 2: @EntityGraph ───────────────────────────────────────────────────────
@EntityGraph(attributePaths = {"customer"})
List<Order> findAll();  // Spring Data auto-adds JOIN FETCH
// ── FIX 3: Batch fetching (Hibernate-specific) ────────────────────────────────
// In entity: @BatchSize(size=25) — loads 25 customers per query
@BatchSize(size = 25)
@ManyToOne(fetch = LAZY)
private Customer customer;
// ── FIX 4: DTO projection — skip entity loading entirely ──────────────────────
@Query("SELECT new com.example.OrderCustomerDto(o.id, c.name) " +
       "FROM Order o JOIN o.customer c")
List<OrderCustomerDto> findOrdersWithCustomerName();
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Eager loading prevents N+1 | EAGER loading causes a JOIN for EVERY query, even when association isn't needed |
| N+1 only happens with LAZY loading | N+1 can also occur with EAGER loading through certain query patterns |
| JOIN FETCH solves all N+1 | Joining multiple collections with FETCH can cause Cartesian product explosion |
## 🔥 Pitfalls in Production
**Pitfall: JPA N+1 in REST endpoint**
```java
// Bad: controller triggers N+1 without noticeable warning in tests
@GetMapping("/orders")
public List<OrderDto> getOrders() {
    return orderRepo.findAll().stream()  // triggers N order.getCustomer() calls!
        .map(OrderMapper::toDto)
        .collect(toList());
}
// Fix: use DTO projection query or @EntityGraph on the repository method
```
## 🔗 Related Keywords
- **[@Transactional](./127 — @Transactional.md)** — required context for lazy loading to work
- **[Lazy vs Eager Loading](./131 — Lazy vs Eager Loading.md)** — the mechanism behind N+1
- **[HikariCP](./132 — HikariCP.md)** — N+1 exhausts connection pool quickly
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| PROBLEM     | 1 + N queries instead of 1 JOIN query               |
+------------------------------------------------------------------+
| CAUSE       | LAZY loading of associations + iterating results     |
+------------------------------------------------------------------+
| FIX 1       | JOIN FETCH in JPQL                                   |
+------------------------------------------------------------------+
| FIX 2       | @EntityGraph on repository method                    |
+------------------------------------------------------------------+
| FIX 3       | DTO projection — don't load entities at all          |
+------------------------------------------------------------------+
```
## 🧠 Think About This Before We Continue
**Q1.** You use `JOIN FETCH` for both `order.customer` and `order.items` where items is a collection. What performance problem can arise?
**Q2.** `OpenSessionInViewFilter` is a common Spring pattern that keeps the Hibernate session open for the entire HTTP request. How does this relate to N+1?
**Q3.** You have a Spring Data repository using `@EntityGraph`. Does this work with `Page<Order>` (pagination)? What limitation exists?
