---
layout: default
title: "Bean Scope"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /spring/bean-scope/
id: SPR-025
category: Spring Core
difficulty: ★★☆
depends_on: Bean, Bean Lifecycle, ApplicationContext, DI
used_by: Lazy vs Eager Loading, Spring MVC, Session Management
related: Singleton Pattern, Prototype Pattern, Scoped Proxy
tags:
  - spring
  - springboot
  - internals
  - intermediate
  - concurrency
---

# SPR-025 — Bean Scope

⚡ TL;DR — Bean Scope controls how many instances Spring creates: singleton (one shared), prototype (new each time), or web-scopes (one per request/session).

| #377            | Category: Spring Core                                 | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, Bean Lifecycle, ApplicationContext, DI          |                 |
| **Used by:**    | Lazy vs Eager Loading, Spring MVC, Session Management |                 |
| **Related:**    | Singleton Pattern, Prototype Pattern, Scoped Proxy    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without scope control, every injected dependency is either shared (singleton) or you must write factory code to create new instances. A `ShoppingCart` bean that's singleton is a disaster — all users share the same cart. A `DatabaseConnectionPool` that's prototype is equally catastrophic — 10,000 concurrent requests each create a 20-connection pool. Without explicit scope semantics, developers either guess wrong (sharing state that shouldn't be shared) or write boilerplate factory code for every use-case that needs controlled instantiation.

**THE BREAKING POINT:**
State management in web apps is particularly critical. HTTP requests are stateless — each request is independent. HTTP sessions span multiple requests for one user. If Spring had only one scope, you'd either have thread-safety problems from shared mutable state or resource waste from excessive object creation. The breaking point is a `UserContext` bean that holds the currently-logged-in user: if it's singleton, user A's data leaks to user B. If it's always new (prototype), session-spanning state like a multi-step wizard is lost between requests.

**THE INVENTION MOMENT:**
"This is exactly why Bean Scope was created."

---

### 📘 Textbook Definition

**Bean Scope** defines the lifecycle and visibility of a bean instance within a Spring IoC container. Spring provides five built-in scopes: `singleton` (one instance per container, default), `prototype` (new instance per `getBean()` call), `request` (one instance per HTTP request, web contexts only), `session` (one instance per HTTP session, web contexts only), and `application` (one instance per `ServletContext`). Custom scopes can be registered via `ConfigurableListableBeanFactory.registerScope()`. Scope is declared via the `@Scope` annotation or the `scope` attribute of `@Bean`. Web scopes require `ApplicationContext` to be web-aware and use scoped proxy beans when injected into singleton beans.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Scope answers "how many instances should exist?" — one, one-per-request, one-per-user, or always-new.

**One analogy:**

> Think of hotel room types. A shared hostel dorm (singleton) — one room, shared by all guests. A private hotel room (prototype) — a new room for every booking. A daily hotel room (request scope) — yours for the day, cleaned and reassigned tomorrow. A weekly rental (session scope) — yours for the week. Scope is the hotel's booking policy.

**One insight:**
Singleton scope is safe only for _stateless_ beans or beans with _thread-safe state_. The moment a singleton holds mutable instance variables that change per-request (like "current user" or "request ID"), you have a concurrency bug waiting to happen under load. This is one of the most common Spring production bugs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Singleton: the container creates exactly one instance per container, cached, and returns it on every `getBean()`.
2. Prototype: the container creates a new instance on every `getBean()`, but tracks nothing after that — `@PreDestroy` is not called.
3. Web scopes: bound to a lifecycle external to the container — an HTTP request, session, or `ServletContext`.

**DERIVED DESIGN:**
Singletons work for stateless services (business logic, repositories) because concurrent access to stateless code is safe. Prototypes work for stateful, single-use objects (email builders, PDF generators). Web scopes solve the fundamental problem of HTTP: requests and sessions have bounded lifetimes that don't map to either "one shared forever" (singleton) or "new every time" (prototype).

**Scoped Proxy Problem:**
A singleton bean cannot directly hold a reference to a request-scoped bean — the singleton outlives the request. Spring solves this with a _scoped proxy_: the singleton holds a proxy that looks up the real request-scoped bean from the current HTTP request context on every method call.

**THE TRADE-OFFS:**

**Singleton Gain:** Zero memory overhead per request. No GC pressure. Thread-safe for stateless code.
**Singleton Cost:** Shared mutable state causes concurrency bugs. Must be stateless or explicitly thread-safe.

**Prototype Gain:** Fresh instance per use — inherently thread-safe for stateful computations.
**Prototype Cost:** No `@PreDestroy`. Higher GC pressure. Spring doesn't manage post-creation lifecycle.

---

### 🧪 Thought Experiment

**SETUP:**
You're building a checkout flow. `CheckoutWizard` tracks which step the user is on (step 1: cart review, step 2: address, step 3: payment). Two users check out simultaneously.

**WHAT HAPPENS WITH singleton scope:**

1. User A starts checkout — `wizard.step = 1`.
2. User B starts checkout — `wizard.step = 1`.
3. User A advances to step 2 — `wizard.step = 2`.
4. User B reads `wizard.step` — gets `2`, not `1`.
5. User B is now on the address page having skipped cart review.
6. Worse: User A's cart contents (mutable `List<Item>`) are shared with User B.

**WHAT HAPPENS WITH session scope:**

1. Spring creates one `CheckoutWizard` per HTTP session.
2. User A's session has its own `wizard` instance — `wizard.step = 1`.
3. User B's session has its own `wizard` instance — `wizard.step = 1`.
4. User A advances to step 2 — only their `wizard` is updated.
5. User B's wizard remains at step 1.
6. Data is perfectly isolated between users.

**THE INSIGHT:**
Session scope solves the "shared mutable per-user state" problem. The container manages one instance per session — you write stateful code as if there's only one user, and the container handles the isolation.

---

### 🧠 Mental Model / Analogy

> Bean scope is like a whiteboard policy. A singleton scope is one whiteboard in the entire office — everyone reads and writes the same content (dangerous if the content is personal). Prototype scope means every person gets a new whiteboard when they ask (personal, fresh, but abandoned after use). Request scope means one whiteboard per meeting room per day (cleared after the meeting). Session scope means one whiteboard per employee's office (persistent for their duration, private to them).

- "One shared office whiteboard" → singleton bean
- "New whiteboard per person" → prototype bean
- "Meeting room whiteboard" → request-scoped bean
- "Personal office whiteboard" → session-scoped bean
- "Whiteboard proxy" → scoped proxy in singleton that delegates to the right whiteboard

**Where this analogy breaks down:** Unlike whiteboards, singleton beans in Spring are typically _intentionally_ stateless — they don't write personal data. The analogy is more relevant for the web scopes where stateful beans are intentional.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Scope controls how many copies of a bean exist. Singleton: one copy shared by everyone. Prototype: each request gets its own fresh copy. Request/Session: one per web request or user session.

**Level 2 — How to use it (junior developer):**
Default is singleton — most beans (services, repositories, controllers) should be singleton. Add `@Scope("prototype")` for stateful, single-use objects. Add `@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)` for per-request beans that need injection into singletons. Never store request-specific state in a singleton bean field.

**Level 3 — How it works (mid-level engineer):**
Singleton beans are stored in `DefaultSingletonBeanRegistry.singletonObjects`. Prototype beans are never cached — `doGetBean()` creates a new instance each time. Web scopes are stored in `RequestAttributes` (for request scope) or `HttpSession` (for session scope). Scoped proxies use CGLIB to subclass the bean and override every method to delegate to `RequestContextHolder.currentRequestAttributes()` or the session for the current thread.

**Level 4 — Why it was designed this way (senior/staff):**
The scoped proxy was designed to solve the "widening scope" problem without requiring all beans to be redesigned. A singleton that needs request-specific data would otherwise need to use `RequestContextHolder.currentRequestAttributes()` directly — coupling it to the web layer. The scoped proxy is a wrapper that does this lookup transparently, letting the singleton remain portable. However, the proxy approach requires `proxyMode = TARGET_CLASS` for non-interface beans (CGLIB) or `proxyMode = INTERFACES` for interface-based proxies (JDK dynamic proxy) — the developer must explicitly choose based on whether the bean implements an interface.

---

### ⚙️ How It Works (Mechanism)

**Singleton Scope:**

```
getBean("userService") called
    ↓
Check singletonObjects cache
    ↓ (found)
Return cached instance ← same object every time
```

**Prototype Scope:**

```
getBean("reportBuilder") called
    ↓
Check scope: "prototype"
    ↓
Create new instance (no cache check)
    ↓
Inject dependencies into new instance
    ↓
Call @PostConstruct
    ↓
Return new instance — NOT stored anywhere
    ↓
Next getBean() call creates another new instance
```

**Request Scope (with scoped proxy):**

```
Singleton holds reference to RequestScopedProxy
    ↓
proxy.method() called during HTTP request
    ↓
Proxy internally calls:
    RequestContextHolder.currentRequestAttributes()
    attributes.getAttribute("userContext", REQUEST_SCOPE)
    ↓
If not present: create new UserContext, store in request attributes
If present: return existing UserContext
    ↓
Delegate method call to real UserContext
    ↓
At request end: UserContext removed from attributes (GC'd)
```

**Scope Registration (custom scope):**

```java
// Register a custom scope
context.getBeanFactory().registerScope("tenant",
    new TenantScope());  // implements Scope interface
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL REQUEST FLOW (with request-scoped beans):**

```
HTTP request arrives
    ↓
DispatcherServlet receives request
    ↓
RequestContextHolder.setRequestAttributes() called
    ↓
Controller method called
    ↓
Singleton service calls method on scoped proxy
    ↓
Proxy resolves real UserContext from request attributes
   ← YOU ARE HERE (scope determines instance resolution)
    ↓
Method executes with request-specific data
    ↓
Response sent
    ↓
RequestContextHolder cleared
    ↓
Request-scoped beans garbage collected
```

**FAILURE PATH:**

```
Request-scoped bean accessed outside request context
    ↓
RequestContextHolder returns null
    ↓
ScopeNotActiveException or IllegalStateException
    ↓
Typical cause: background thread tries to access
request-scoped data without request context
```

**WHAT CHANGES AT SCALE:**
At high request volume, request-scoped beans create substantial GC pressure — one object graph per request. Prototype beans in high-frequency paths can trigger frequent GC cycles. Profile with JVM heap analysis (`jmap -histo:live <pid>`) to see object count per class under load.

---

### 💻 Code Example

**Example 1 — Singleton (default) — stateless service:**

```java
@Service  // singleton by default — correct for stateless service
public class OrderCalculator {

    // SAFE: no instance state — purely functional
    public BigDecimal calculateTotal(List<OrderItem> items) {
        return items.stream()
            .map(i -> i.getPrice().multiply(i.getQuantity()))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
```

**Example 2 — Prototype — stateful single-use builder:**

```java
@Component
@Scope("prototype")  // new instance per injection/getBean()
public class ReportBuilder {

    private final List<ReportSection> sections = new ArrayList<>();

    public ReportBuilder addSection(ReportSection section) {
        sections.add(section);
        return this;
    }

    public Report build() {
        return new Report(sections);
    }
}

// In a singleton service — get fresh builder via BeanFactory
@Service
public class ReportService {
    private final BeanFactory beanFactory;

    public ReportService(BeanFactory beanFactory) {
        this.beanFactory = beanFactory;
    }

    public Report generateReport(ReportRequest req) {
        // Each call gets a fresh, empty builder
        ReportBuilder builder = beanFactory.getBean(ReportBuilder.class);
        return builder.addSection(buildHeader(req)).build();
    }
}
```

**Example 3 — Request scope with scoped proxy:**

```java
// Request-scoped bean: one instance per HTTP request
@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext {
    private String traceId;
    private String userId;

    @PostConstruct
    public void init() {
        traceId = UUID.randomUUID().toString();
    }

    public String getTraceId() { return traceId; }
    public void setUserId(String userId) { this.userId = userId; }
}

// Singleton service can inject it via scoped proxy
@Service
public class AuditService {
    private final RequestContext reqCtx; // proxy, not real instance

    public AuditService(RequestContext reqCtx) {
        this.reqCtx = reqCtx;
    }

    public void logAction(String action) {
        // proxy resolves current request's RequestContext here
        log.info("User {} performed {}", reqCtx.getUserId(), action);
    }
}
```

---

### ⚖️ Comparison Table

| Scope         | Instances            | Lifecycle Owner | @PreDestroy | Use Case                             |
| ------------- | -------------------- | --------------- | ----------- | ------------------------------------ |
| **singleton** | 1 per container      | Spring          | Yes         | Stateless services, repositories     |
| prototype     | 1 per request        | Caller          | No          | Stateful builders, converters        |
| request       | 1 per HTTP request   | Spring          | Yes         | Per-request context (trace ID, user) |
| session       | 1 per HTTP session   | Spring          | Yes         | Shopping cart, wizard state          |
| application   | 1 per ServletContext | Spring          | Yes         | App-wide shared state in web context |

**How to choose:** Default to singleton for all stateless beans (95% of beans). Use prototype for stateful, single-use computation objects. Use request scope for per-request metadata (tracing, security context). Use session scope sparingly — sessions consume server memory per active user.

---

### ⚠️ Common Misconceptions

| Misconception                                                               | Reality                                                                                                                                                                         |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Singleton beans are always thread-safe                                      | Thread safety depends on whether the bean has mutable instance state. A singleton with a mutable HashMap field is not thread-safe.                                              |
| Prototype beans have full lifecycle management                              | Spring creates and injects prototypes but does NOT call @PreDestroy on them. The caller is responsible for cleanup.                                                             |
| You can directly inject a request-scoped bean into a singleton              | Without proxyMode, Spring injects the request-scoped instance at context startup (outside any request) — it fails. Always use proxyMode for web-scoped beans in singletons.     |
| Session scope is for user authentication data                               | Spring Security's SecurityContextHolder already handles auth context. Session scope is for app-level multi-request state (wizards, carts).                                      |
| Prototype scope creates new instances automatically on each injection point | Prototype beans injected via @Autowired are only created once at context startup, just like singletons. To get a new instance each time, inject BeanFactory and call getBean(). |

---

### 🚨 Failure Modes & Diagnosis

**Singleton concurrency bug (mutable singleton state)**

**Symptom:**
Intermittent data corruption: user A sees user B's data. Request-specific values appear in the wrong responses. Heisenbug that appears only under concurrent load.

**Root Cause:**
A singleton bean holds a mutable instance variable that is set per-request: `private String currentUserId;`. Concurrent requests overwrite each other's value.

**Diagnostic Command / Tool:**

```bash
# Thread dump during load test to see threads in the same bean
jstack <pid> | grep -A 20 "YourSingletonService"
# Look for multiple threads inside the same method accessing instance fields
```

**Fix:**

```java
// BAD: mutable state in singleton
@Service
public class ReportService {
    private String currentUserId;  // shared by all threads!

    public Report generate(String userId) {
        this.currentUserId = userId;  // race condition!
        return buildReport();
    }
}

// GOOD: pass state as method parameters
@Service
public class ReportService {
    public Report generate(String userId) {  // stateless method
        return buildReport(userId);
    }
}
```

**Prevention:** Singletons must be stateless or hold only immutable or thread-safe state (e.g., `AtomicLong`, `ConcurrentHashMap`).

---

**ScopeNotActiveException (accessing request scope outside a request)**

**Symptom:**
`ScopeNotActiveException: Cannot request attribute 'scopedTarget.requestContext' because request is not active`

**Root Cause:**
A background thread, `@Scheduled` method, or async task tries to access a request-scoped bean. No HTTP request is active on that thread.

**Diagnostic Command / Tool:**

```bash
# Check stack trace for the thread attempting access
# Look for @Scheduled or @Async in the call stack
grep "ScopeNotActiveException" app.log -A 30
```

**Fix:**

```java
// BAD: @Scheduled tries to use request-scoped bean
@Scheduled(fixedDelay = 1000)
public void scheduledTask() {
    requestContext.getTraceId();  // no request active!
}

// GOOD: pass required data as parameters, not via scoped beans
@Scheduled(fixedDelay = 1000)
public void scheduledTask() {
    String traceId = UUID.randomUUID().toString();
    processWithTrace(traceId);  // stateless
}
```

**Prevention:** Never access request or session-scoped beans from scheduled tasks, event listeners, or async threads. Pass necessary data as method parameters.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Bean` — scope is a property of a bean; understand beans first
- `Bean Lifecycle` — scope determines how the lifecycle is managed
- `ApplicationContext` — the container that enforces scoping

**Builds On This (learn these next):**

- `Lazy vs Eager Loading` — when combined with scope, controls WHEN an instance is created
- `CGLIB Proxy` — the mechanism Spring uses for scoped proxies

**Alternatives / Comparisons:**

- `ThreadLocal` — an alternative to request scope for thread-local state; less Spring-managed, more explicit
- `CDI Scope (Jakarta EE)` — the equivalent concept in Jakarta EE; similar semantics, different annotations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ How many instances Spring creates:        │
│              │ one, one-per-request, one-per-session,    │
│              │ or always-new                             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shared mutable state bugs; resource waste │
│ SOLVES       │ from unnecessary object creation          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Singleton is safe ONLY for stateless beans│
│              │ Inject request-scoped into singleton via  │
│              │ scoped proxy, not direct reference        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Singleton: services/repos (stateless)     │
│              │ Request: trace IDs, user context per call │
│              │ Session: shopping carts, wizard state     │
│              │ Prototype: stateful computation objects   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never put request-specific state in a     │
│              │ singleton field                           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Singleton: memory-efficient vs thread-    │
│              │ safety risk; Prototype: safe vs no cleanup│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Scope is the container's answer to       │
│              │  'how many copies should exist?'"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bean Lifecycle → CGLIB Proxy →            │
│              │ Scoped Proxy                              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `@Service` singleton bean holds a `List<String>` instance field that is appended to on each request (not replaced). The test with a single thread works perfectly. The app works fine at 5 concurrent users. At 100 concurrent users, data from different requests appears mixed. Trace the exact sequence of operations that causes this bug, and explain why `synchronized` on the method would partially fix it but introduce a different problem.

**Q2.** Prototype-scoped beans injected via `@Autowired` are actually singletons in practice — Spring injects the prototype once at startup. To get a truly new prototype on every method call, you must inject `BeanFactory` and call `getBean()` each time. What are the three alternative patterns (other than BeanFactory injection) that Spring provides to solve this "singleton injecting prototype" problem, and what are their respective trade-offs?
