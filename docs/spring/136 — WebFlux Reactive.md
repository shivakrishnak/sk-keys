---
layout: default
title: "WebFlux / Reactive"
parent: "Spring Framework"
nav_order: 136
permalink: /spring/webflux-reactive/
---
⚡ TL;DR — Spring WebFlux is Spring's reactive web framework that handles thousands of concurrent connections with minimal threads using non-blocking I/O and the Reactor library.
## 📘 Textbook Definition
Spring WebFlux is Spring's reactive-stack web framework, introduced in Spring 5. Built on Project Reactor and Reactive Streams specification, it uses non-blocking I/O (Netty or Servlet 3.1 async) to process requests without blocking threads while waiting for I/O. It enables high-concurrency scenarios with a small, fixed thread pool — contrasted with Spring MVC's thread-per-request model.
## 🟢 Simple Definition (Easy)
Traditional Spring MVC blocks a thread while waiting for the database. With WebFlux, when the app waits for DB or HTTP, that thread is freed to handle other requests. This lets a small number of threads serve millions of concurrent requests.
## 🔵 Simple Definition (Elaborated)
WebFlux uses the Reactor library's `Mono` (0-1 items) and `Flux` (0-N items) as its primary types. Controllers return these reactive types instead of plain objects. The framework pipelines the data through a chain of operators without blocking any thread — ideal for high-concurrency microservices, real-time streaming, and event-driven systems.
## 🔩 First Principles Explanation
```
Spring MVC (Blocking):
Thread 1: Request → Block waiting for DB (10ms) → Response
Thread 2: Request → Block waiting for DB (10ms) → Response
...100 concurrent requests = 100 threads blocked!
Spring WebFlux (Non-blocking):
Thread 1: Request → Register DB callback → FREE (handles next request)
Thread 2: Request → Register DB callback → FREE (handles next request)
... DB responds → Thread 1 picks up the callback → sends response
Same 2 threads handle 100 concurrent requests!
```
## 💻 Code Example
```java
// WebFlux controller — returns Mono/Flux instead of plain objects
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("/{id}")
    public Mono<User> getUser(@PathVariable Long id) {
        return userRepository.findById(id)  // reactive repo returns Mono<User>
            .switchIfEmpty(Mono.error(new UserNotFoundException(id)));
    }
    @GetMapping
    public Flux<User> getAllUsers() {
        return userRepository.findAll()  // returns Flux<User>
            .filter(User::isActive);
    }
    @PostMapping
    public Mono<ResponseEntity<User>> createUser(@RequestBody Mono<User> userMono) {
        return userMono
            .flatMap(userRepository::save)
            .map(saved -> ResponseEntity.created(
                URI.create("/api/users/" + saved.getId()))
                .body(saved));
    }
}
// Server-Sent Events — real-time streaming
@GetMapping(value = "/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> streamEvents() {
    return Flux.interval(Duration.ofSeconds(1))
        .map(i -> "Event #" + i)
        .take(100);
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| WebFlux is always faster than MVC | WebFlux shines under HIGH concurrency — for low concurrency, MVC is simpler |
| You can mix blocking code in WebFlux | Blocking in WebFlux stalls the entire event loop — use `subscribeOn(Schedulers.boundedElastic())` |
| WebFlux replaces Spring MVC | They coexist — choose based on use case; WebFlux needs reactive drivers (R2DBC, reactive MongoDB) |
## 🔗 Related Keywords
- **[Mono / Flux](./137 — Mono Flux.md)** — reactive types used in WebFlux
- **[Backpressure](./138 — Backpressure.md)** — flow control in reactive streams
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Non-blocking request handling — high concurrency     |
+------------------------------------------------------------------+
| TYPES       | Mono<T> (0-1 items) and Flux<T> (0-N items)         |
+------------------------------------------------------------------+
| SERVER      | Netty (default in Boot) or Servlet 3.1 async         |
+------------------------------------------------------------------+
| AVOID       | Blocking code in reactive pipelines                   |
+------------------------------------------------------------------+
```
