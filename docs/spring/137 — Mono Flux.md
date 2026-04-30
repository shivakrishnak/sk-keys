---
layout: default
title: "Mono / Flux"
parent: "Spring Framework"
nav_order: 137
permalink: /spring/mono-flux/
number: "137"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: WebFlux Reactive, Project Reactor
used_by: Backpressure, reactive pipeline, WebFlux endpoints
tags: #spring, #springboot, #concurrency, #advanced
---

# 137 — Mono Flux

`#spring` `#springboot` `#concurrency` `#advanced`

⚡ TL;DR — Mono represents an async 0-or-1 result; Flux represents an async 0-to-N stream of results — Project Reactor's core reactive types used throughout Spring WebFlux.

| #137 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | WebFlux Reactive, Project Reactor | |
| **Used by:** | Backpressure, reactive pipeline, WebFlux endpoints | |

---

### 📘 Textbook Definition

`Mono<T>` is a Reactive Streams `Publisher` that emits at most one item then completes (or errors). `Flux<T>` is a `Publisher` that emits zero to N items, then completes (or errors). Both are **lazy** — the pipeline only executes when something subscribes (or the framework subscribes on your behalf in WebFlux). They are the primary types of Project Reactor, Spring's reactive library.

### 🟢 Simple Definition (Easy)

`Mono` is an async Optional — it will eventually produce 0 or 1 value. `Flux` is an async List — it will eventually produce a stream of values. Neither does anything until subscribed to.

### 🔵 Simple Definition (Elaborated)

Think of `Mono<User>` like a `Future<User>` but with a rich operator library (map, filter, flatMap, zip, retry, timeout) for composing async flows without blocking. `Flux<Order>` is like a `Stream<Order>` but asynchronous and potentially infinite (e.g., a real-time event stream). The framework subscribes when a request comes in — you just declare the transformation pipeline.

### 💻 Code Example
```java
// ── Mono: 0 or 1 value ────────────────────────────────────────────────────────
Mono<User> userMono = userRepo.findById(userId)
    .map(user -> {
        user.setLastSeen(Instant.now());
        return user;
    })
    .switchIfEmpty(Mono.error(new UserNotFoundException(userId)))
    .doOnSuccess(u -> log.info("Found user: {}", u.getId()))
    .timeout(Duration.ofSeconds(5));
// ── Flux: 0 to N values ───────────────────────────────────────────────────────
Flux<Order> activeOrders = orderRepo.findByStatus("ACTIVE")
    .filter(o -> o.getAmount().compareTo(BigDecimal.ZERO) > 0)
    .map(OrderTransformer::toDto)
    .take(100)   // limit to 100
    .delayElements(Duration.ofMillis(10));  // throttle
// ── Combining ─────────────────────────────────────────────────────────────────
Mono<OrderSummary> summary = Mono.zip(
    userRepo.findById(userId),
    orderRepo.countByUserId(userId)
).map(tuple -> new OrderSummary(tuple.getT1(), tuple.getT2()));
// ── Error handling ────────────────────────────────────────────────────────────
Mono<User> resilient = userService.find(id)
    .onErrorReturn(TimeoutException.class, User.ANONYMOUS)  // fallback
    .retryWhen(Retry.backoff(3, Duration.ofSeconds(1)));    // retry 3x
// ── Converting between types ──────────────────────────────────────────────────
Mono<List<User>> userList = Flux.fromIterable(userIds)
    .flatMap(userRepo::findById)
    .collectList();  // Flux<User> → Mono<List<User>>
```

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Mono/Flux execute immediately | They are LAZY — nothing runs until someone subscribes |
| You must always subscribe manually | In WebFlux, the framework subscribes for you when returning from controller |
| Mono.block() is fine in WebFlux | Calling block() in WebFlux stalls the event loop — avoid entirely |

### 🔗 Related Keywords

- **[WebFlux / Reactive](./136 — WebFlux Reactive.md)** — the framework using Mono/Flux
- **[Backpressure](./138 — Backpressure.md)** — flow control Flux supports

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| MONO        | 0 or 1 item — async Optional / single async result  |
+------------------------------------------------------------------+
| FLUX        | 0 to N items — async stream / collection             |
+------------------------------------------------------------------+
| LAZY        | Nothing executes until subscribed                    |
+------------------------------------------------------------------+
| AVOID       | .block() in WebFlux — use operators instead          |
+------------------------------------------------------------------+
```
