---
layout: default
title: "Bean Scope"
parent: "Spring Core"
nav_order: 377
permalink: /spring/bean-scope/
number: "377"
category: Spring Core
difficulty: ★★☆
depends_on: Bean, ApplicationContext, HTTP Request Lifecycle, Threads
used_by: Prototype scope, Request scope, Session scope, Thread safety
tags: #java, #spring, #springboot, #intermediate, #performance
---

# 377 — Bean Scope

`#java` `#spring` `#springboot` `#intermediate` `#performance`

⚡ TL;DR — The configuration that controls how many instances of a bean the container creates and how their lifecycle is bounded — from one global singleton to one per HTTP request.

| #377 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Bean, ApplicationContext, HTTP Request Lifecycle, Threads | |
| **Used by:** | Prototype scope, Request scope, Session scope, Thread safety | |

---

### 📘 Textbook Definition

**Bean scope** is the `@Scope` configuration that determines the number of bean instances the Spring container creates and the extent of their lifecycle. Spring defines six built-in scopes: **singleton** (one per ApplicationContext — default), **prototype** (new instance per injection point or `getBean()` call), **request** (one per HTTP request — web-aware), **session** (one per HTTP session), **application** (one per `ServletContext`), and **websocket** (one per WebSocket session). Custom scopes can be registered via `CustomScopeConfigurer`. The choice of scope directly impacts thread safety: singleton beans shared across threads must be stateless, while request-scoped beans are safe because they're never shared between concurrent requests.

---

### 🟢 Simple Definition (Easy)

Bean scope answers the question "how many of this bean exist?" Singleton: one for the whole app. Prototype: a fresh copy every time. Request: one per web request.

---

### 🔵 Simple Definition (Elaborated)

The default and most common scope is singleton — the container creates exactly one instance and shares it everywhere. This is fine for stateless services and repositories. When a bean holds per-user or per-request state, a singleton would be shared across all threads simultaneously — a concurrency disaster. Prototype scope creates a fresh instance each time the bean is requested, giving each caller independent state. Request and session scopes (available only in web applications) create beans per HTTP request or user session respectively, with the container automatically cleaning them up when the request/session ends.

---

### 🔩 First Principles Explanation

**Thread safety and state — the core problem scopes solve:**

```java
// BAD: singleton bean with request-specific state
@Service // singleton — one shared instance
class SearchService {
  private String currentQuery; // SHARED across all threads!

  public List<Result> search(String query) {
    this.currentQuery = query;   // Thread-A sets "java"
    // Thread-B sets "spring" before Thread-A reads it
    return executeSearch(currentQuery); // Thread-A reads "spring"
  }
}

// FIX: make it stateless (preferred)
@Service
class SearchService {
  public List<Result> search(String query) {
    return executeSearch(query); // query is method-local
  }
}

// OR: request-scoped bean for request-specific state
@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
class SearchContext {
  private String currentQuery;
  // Fresh instance per HTTP request — thread-safe
}
```

**Why request/session scopes need proxy injection:**

```
Problem: a singleton-scoped service cannot hold a direct
reference to a shorter-lived request-scoped bean.

At startup: the request-scoped bean doesn't exist yet
(no HTTP request is in flight)
→ Cannot inject it into the singleton constructor

Solution: inject a SCOPED PROXY instead
→ Proxy looks up the actual request-scoped bean
   via ThreadLocal at every method call
→ Singleton holds a stable proxy reference
→ Proxy delegates to the correct per-request instance
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT scope control:**

```
Without scope configuration:

  Everything singleton:
    User A and User B share the same ShoppingCart bean
    → A adds item, B sees it → data leak

  No request scope:
    Cannot track per-request state (correlation ID,
    current user context, audit trail) without
    ThreadLocal plumbing in every class

  No prototype:
    Cannot create independent instances for
    stateful workflows (wizard, batch job context)
    without manual factory boilerplate
```

**WITH bean scopes:**

```
→ Singleton: one DataSource shared by 200 repos (efficient)
→ Prototype: fresh ExcelReportBuilder per export job
→ Request: one SecurityContext per HTTP request
  (Spring Security uses request scope internally)
→ Session: user shopping cart lives with the session
→ Scope mismatch caught at startup (with proxy check)
```

---

### 🧠 Mental Model / Analogy

> Bean scope is like **printer allocation policy in an office**. Singleton: one high-volume printer shared by everyone — efficient, but you can't leave your private documents on it. Prototype: a personal laser printer issued to every employee — fast, isolated, but expensive to create. Request: a print job queue that's fresh for each print job — state tied to that one job, cleaned up automatically.

"Shared office printer" = singleton — one instance, all share
"Personal printer per employee" = prototype — new per request
"Print job queue" = request scope — tied to one HTTP request
"Leaving private docs on shared printer" = mutable singleton state bug

---

### ⚙️ How It Works (Mechanism)

**All six scopes:**

```
┌─────────────────────────────────────────────────────┐
│  SCOPE       │ INSTANCES    │ LIFECYCLE              │
├─────────────────────────────────────────────────────┤
│  singleton   │ 1 per ctx    │ full (managed)         │
│  prototype   │ 1 per request│ creation only (NOT     │
│              │              │ destroyed by container) │
│  request     │ 1 per HTTP   │ tied to HTTP request   │
│              │ request      │                        │
│  session     │ 1 per HTTP   │ tied to HTTP session   │
│              │ session      │                        │
│  application │ 1 per        │ tied to ServletContext │
│              │ ServletCtx   │                        │
│  websocket   │ 1 per WS     │ tied to WebSocket ses. │
│              │ session      │                        │
└─────────────────────────────────────────────────────┘
```

**`@Scope` annotation usage:**

```java
// Prototype: fresh instance each time
@Component
@Scope("prototype")
public class ReportBuilder { ... }

// Request scope with scoped proxy (required for injection
// into singleton beans)
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST,
       proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestScopedContext {
  private String correlationId;
  // set by filter, read by any service in same request
}

// Injection into singleton — works via scoped proxy
@Service
public class AuditService {
  private final RequestScopedContext reqCtx;

  public AuditService(RequestScopedContext reqCtx) {
    this.reqCtx = reqCtx; // injected as proxy, not instance
  }

  public void audit(String action) {
    // reqCtx.getCorrelationId() resolves via ThreadLocal
    // to current request's actual bean instance
    log.info("[{}] {}", reqCtx.getCorrelationId(), action);
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean definition (107)
        ↓
  BEAN SCOPE (109)  ← you are here
  (@Scope controls instance count and lifecycle)
        ↓
  singleton → one shared instance (default)
  prototype → new instance per getBean() / injection
  request   → new instance per HTTP request
  session   → new instance per HTTP session
        ↓
  Scope mismatch (singleton → shorter-lived):
  Solved by: SCOPED PROXY (CGLIB/JDK)
  → proxy resolves actual bean via ThreadLocal
        ↓
  Affects: Thread Safety, Memory, Test isolation
```

---

### 💻 Code Example

**Example 1 — Prototype scope for stateful processors:**

```java
@Component
@Scope("prototype")
public class CsvExportProcessor {
  private final List<String> rows = new ArrayList<>();

  public void addRow(String row) { rows.add(row); }
  public String export() {
    return String.join("\n", rows);
  }
}

// Service: get a fresh processor per export — no state sharing
@Service
public class ExportService {
  @Autowired
  private ObjectProvider<CsvExportProcessor> processors;

  public String exportOrders(List<Order> orders) {
    CsvExportProcessor proc = processors.getObject();
    orders.forEach(o -> proc.addRow(o.toCsvRow()));
    return proc.export();
  }
}
```

**Example 2 — Request scope for per-request correlation:**

```java
@Component
@Scope(value = "request",
       proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestCorrelationContext {
  private String correlationId;
  private String userId;

  // Setters / getters — safe: one instance per request
  public void setCorrelationId(String id) {
    this.correlationId = id;
  }
  public String getCorrelationId() { return correlationId; }
}

// Filter sets it once per request
@Component
public class CorrelationFilter implements Filter {
  @Autowired
  private RequestCorrelationContext ctx;

  @Override
  public void doFilter(ServletRequest req,
                       ServletResponse res,
                       FilterChain chain) throws Exception {
    ctx.setCorrelationId(
        req.getHeader("X-Correlation-Id"));
    chain.doFilter(req, res);
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Singleton scope means thread-safe | Singleton means one shared instance — thread safety depends entirely on whether the bean has mutable state accessed concurrently |
| Prototype beans are cleaned up by the container | Spring creates prototype beans but never destroys them. @PreDestroy is never called on prototype instances |
| Request scope works in any Spring application | Request scope requires a web-aware ApplicationContext (web app or Spring Boot with embedded server). It fails in standalone apps |
| Prototype injection into a singleton works directly | Injecting a prototype into a singleton via constructor gives you a single prototype instance — effectively singleton behaviour. Use ObjectProvider |

---

### 🔥 Pitfalls in Production

**1. Prototype injected into singleton — becomes a singleton**

```java
// BAD: prototype injected at construction → acts as singleton
@Service // singleton
class ReportService {
  @Autowired
  ReportContext ctx; // prototype — injected ONCE at startup

  public String generate(String id) {
    ctx.setId(id);        // Thread A sets "report-1"
    // Thread B sets "report-2" before Thread A reads!
    return ctx.build();   // Thread A reads "report-2"
  }
}

// GOOD: use ObjectProvider for per-call prototype
@Service
class ReportService {
  @Autowired ObjectProvider<ReportContext> ctxProvider;

  public String generate(String id) {
    ReportContext ctx = ctxProvider.getObject(); // fresh
    ctx.setId(id);
    return ctx.build();
  }
}
```

**2. Missing `proxyMode` on request-scoped bean injected into singleton**

```java
// BAD: no proxyMode → BeanCreationException at startup
// (no active HTTP request during context initialization)
@Component
@Scope(value = "request") // Missing proxyMode!
class RequestContext { String userId; }

@Service
class MyService {
  @Autowired RequestContext ctx; // FAILS at startup
}

// GOOD: always declare proxyMode for web scopes
@Component
@Scope(value = "request",
       proxyMode = ScopedProxyMode.TARGET_CLASS)
class RequestContext { String userId; }
```

---

### 🔗 Related Keywords

- `Bean` — the object whose instance count is controlled by scope
- `Bean Lifecycle` — prototype beans have a truncated lifecycle (no destruction)
- `ApplicationContext` — different context types support different scopes
- `Thread Safety` — singleton beans must be stateless or use concurrent data structures
- `@Transactional` — relies on singleton-scoped proxies; never put on prototype-scoped classes
- `ObjectProvider` — Spring's recommended API for on-demand prototype injection

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Controls how many instances exist and     │
│              │ how long they live — singleton is default  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Prototype: stateful per-call objects;     │
│              │ Request: per-request web state (audit, id)│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Prototype injected into singleton without │
│              │ ObjectProvider; request scope without     │
│              │ proxyMode in singleton injection          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Singleton shares everything;             │
│              │  prototype shares nothing."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanPostProcessor (110) →                 │
│              │ @Transactional (127) → Thread Safety      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's request-scoped proxy uses a `ThreadLocal` to resolve the actual bean per request. Explain what happens to the ThreadLocal binding when the request is handled by a reactive WebFlux handler (on a non-blocking Netty thread) rather than a Servlet thread — why the standard `ThreadLocal`-based request scope completely breaks in a reactive context — and describe the `ReactiveAdapterRegistry` and `ContextView` approach Reactor uses to carry per-request context safely across non-blocking threads.

**Q2.** A load test reveals that a `prototype`-scoped bean is being created for every call to a hot service method in a 10,000 RPS endpoint — causing 10,000 object creations per second and significant GC pressure. Prove that the prototype pattern is wrong for this use case, propose an alternative (hint: object pooling or redesign to stateless), and describe how you would use async-profiler or JVM flight recorder to identify prototype bean allocation pressure in production.

