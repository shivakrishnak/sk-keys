---
layout: default
title: "Bean Scope"
parent: "Spring Framework"
nav_order: 109
permalink: /spring/bean-scope/
---
# 109 — Bean Scope

`#spring` `#internals` `#foundational`

⚡ TL;DR — Bean Scope defines how many instances of a bean Spring creates: singleton (one ever), prototype (one per injection), request (one per HTTP request), session (one per HTTP session).

| #109 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Bean, IoC | |
| **Used by:** | @Scope, Prototype Bean, Request Scope | |

---

### 📘 Textbook Definition

Bean Scope in Spring determines the lifecycle and visibility of a bean instance within the IoC container. The default scope is **singleton** (one shared instance per container). Other built-in scopes include **prototype** (new instance per injection), **request**, **session**, and **application** (web-aware scopes), plus **websocket**. Custom scopes can be registered.

---

### 🟢 Simple Definition (Easy)

Scope answers: "How many copies of this bean exist?" Singleton = one for the whole app. Prototype = a fresh one every time you ask. Request = one per web request.

---

### 🔵 Simple Definition (Elaborated)

By default, Spring creates exactly one instance of each bean and shares it everywhere. This is the **singleton** scope. But sometimes you want a fresh instance every time (stateful processing beans), or one per web request (user-specific context). Spring's scoping system lets you declare exactly that. The wrong scope for a component leads to either wasted memory or dangerous shared state.

---

### 🔩 First Principles Explanation

**The problem singleton solves:**
Stateless services should be shared — creating one `UserService` per request wastes memory and GC.
**The problem singleton creates:**
Stateful beans (e.g., a shopping cart) cannot be singleton — they'd be shared across all users!
**Scope table:**
```
Scope       | Instances          | Lifecycle               | Use case
────────────┼────────────────────┼─────────────────────────┼─────────────────────
singleton   | 1 per container    | container lifetime      | Stateless services
prototype   | 1 per injection    | caller-managed          | Stateful processing
request     | 1 per HTTP request | request duration        | Request-specific data
session     | 1 per HTTP session | session duration        | User session state
application | 1 per ServletCtx   | app lifetime (≈singleton)| Global web state
websocket   | 1 per WS session   | WS session duration     | WebSocket handlers
```

---

### ❓ Why Does This Exist (Why Before What)

Without scope control, you'd either have dangerous shared state (everything singleton) or wasteful object creation (everything new). Scopes let you match object lifetime to actual usage patterns.

---

### 🧠 Mental Model / Analogy

> Singleton = the **office printer** — one shared by everyone. Prototype = a **disposable coffee cup** — you get a fresh one each time. Request scope = a **conference room booking** — one per meeting, released when done. Session scope = a **personal locker** — one per employee, persists until they leave.

---

### 💻 Code Example
```java
// Singleton (default) — one instance per ApplicationContext
@Service                            // no @Scope needed — singleton is default
public class UserService { }
// Prototype — new instance every time
@Component
@Scope("prototype")
public class ReportBuilder {
    private List<String> rows = new ArrayList<>(); // safe: each caller gets their own
    public void addRow(String row) { rows.add(row); }
}
// Request scope — one per HTTP request
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext {
    private String requestId = UUID.randomUUID().toString();
    public String getRequestId() { return requestId; }
}
// Session scope — one per HTTP session
@Component
@Scope(value = WebApplicationContext.SCOPE_SESSION, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class ShoppingCart {
    private List<Item> items = new ArrayList<>();
    public void addItem(Item item) { items.add(item); }
}
// Singleton injecting prototype — PROBLEM: only gets one prototype instance!
@Service
public class DocumentProcessor {
    @Autowired private ReportBuilder builder; // Always the SAME instance — WRONG!
}
// Fix: use ObjectFactory or ApplicationContext.getBean()
@Service
public class DocumentProcessorFixed {
    @Autowired private ObjectFactory<ReportBuilder> builderFactory;
    public void process() {
        ReportBuilder builder = builderFactory.getObject(); // fresh instance each time
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Singleton in Spring = Singleton design pattern | Spring singleton = one per container (not per JVM); two containers = two instances |
| Prototype beans are destroyed by container | Container creates prototypes but never destroys them — caller must manage lifecycle |
| Request scope works without a web context | Request/session scopes require a web ApplicationContext |
| proxyMode is optional for request/session | Without proxyMode, a singleton injecting a request-scoped bean gets the wrong instance |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Singleton bean with mutable state**
```java
@Service // singleton — shared across threads
public class ContextHolder {
    private User currentUser; // DANGEROUS: shared across all requests!
}
// Fix: use ThreadLocal or request-scoped bean
```
**Pitfall 2: Singleton injecting shorter-lived beans without proxy**
```java
// Request-scoped bean injected into singleton WITHOUT proxy:
@Service
public class MyService {
    @Autowired RequestData data; // Always gets same (first-request) instance!
}
// Fix: add proxyMode = ScopedProxyMode.TARGET_CLASS to RequestData
```

---

### 🔗 Related Keywords

- **[Bean](./107 — Bean.md)** — the unit that scopes apply to
- **[Bean Lifecycle](./108 — Bean Lifecycle.md)** — lifecycle callbacks affected by scope
- **[DI (Dependency Injection)](./104 — DI (Dependency Injection).md)** — how scoped beans get resolved
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — scoped proxies use AOP under the hood

---

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| SINGLETON   | 1 per container — stateless services (DEFAULT)     |
+------------------------------------------------------------------+
| PROTOTYPE   | 1 per injection — stateful, caller destroys         |
+------------------------------------------------------------------+
| REQUEST     | 1 per HTTP request — needs proxyMode for singleton  |
+------------------------------------------------------------------+
| SESSION     | 1 per HTTP session — user-specific state             |
+------------------------------------------------------------------+
| PITFALL     | Singleton injecting shorter-lived = stale reference  |
+------------------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

**Q1.** A singleton service injects a session-scoped shopping cart. What exactly happens at first injection? How does Spring ensure the correct cart is returned for each user despite the singleton holding one reference?
**Q2.** Why does the container never call `@PreDestroy` on prototype beans? What does this mean for resource management?
**Q3.** What is the difference between `ScopedProxyMode.TARGET_CLASS` and `ScopedProxyMode.INTERFACES`? When would you use each?
