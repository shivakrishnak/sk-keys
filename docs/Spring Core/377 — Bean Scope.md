---
layout: default
title: "Bean Scope"
parent: "Spring Core"
nav_order: 377
permalink: /spring/bean-scope/
number: "377"
category: Spring Core
difficulty: ★★☆
depends_on: Bean, Bean Lifecycle, ApplicationContext
used_by: Bean Lifecycle, @Transactional, Circular Dependency
tags: #intermediate, #spring, #internals, #architecture
---

# 377 — Bean Scope

`#intermediate` `#spring` `#internals` `#architecture`

⚡ TL;DR — Bean Scope controls how many instances of a bean the container creates: **singleton** (one shared instance), **prototype** (new instance per injection), or web scopes (**request**, **session**, **application**).

| #377            | Category: Spring Core                               | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, Bean Lifecycle, ApplicationContext            |                 |
| **Used by:**    | Bean Lifecycle, @Transactional, Circular Dependency |                 |

---

### 📘 Textbook Definition

**Bean Scope** determines the lifecycle boundaries of a Spring bean — specifically, how many instances are created, when each instance is created, and for how long each instance lives. Spring provides five built-in scopes: **singleton** (one instance per `ApplicationContext`, default), **prototype** (a new instance created every time the bean is requested), **request** (one instance per HTTP request, web contexts only), **session** (one instance per HTTP session), and **application** (one instance per `ServletContext`). Custom scopes can be registered via `ConfigurableBeanFactory.registerScope()`. Scope is declared via `@Scope("scopeName")` or the shorthand annotations `@RequestScope`, `@SessionScope`, and `@ApplicationScope`. The **scoped proxy** pattern (`@Scope(proxyMode = ScopedProxyMode.TARGET_CLASS)`) allows narrow-scoped beans (e.g., request-scoped) to be injected into wide-scoped beans (e.g., singletons) without holding a stale reference.

---

### 🟢 Simple Definition (Easy)

Bean scope answers: "How many copies of this bean does Spring create?" — singleton = one for the entire app, prototype = a new copy every time it is needed, request/session = one per HTTP request or session.

---

### 🔵 Simple Definition (Elaborated)

By default, Spring creates one instance of each bean and shares it across all classes that inject it — this is the singleton scope. If two services both inject `EmailService`, they get the exact same object. This works well for stateless services. But sometimes you need fresh state per use — a user-specific shopping cart, a per-request trace context, or a non-thread-safe object. Bean scopes handle this: prototype creates a new instance every time a bean is requested, request creates one instance per HTTP request, and session creates one per user session. The challenge is mixing scopes: a singleton holding a reference to a request-scoped bean would hold a stale reference after the request ends — Spring solves this with scoped proxies.

---

### 🔩 First Principles Explanation

**The five built-in scopes:**

```
Scope        | Instance created when?          | Lives until?
─────────────┼─────────────────────────────────┼──────────────────────────
singleton    | At context startup (by default) | Context closes
prototype    | Every call to getBean() / inject| Caller's choice (no tracking)
request      | Each HTTP request starts        | HTTP request completes
session      | Each HTTP session starts        | HTTP session expires/closes
application  | First access                    | ServletContext closes
```

**Declaring scopes:**

```java
// Singleton (default — no annotation needed)
@Service
class UserService { }

// Prototype
@Component
@Scope("prototype")               // new instance per injection/getBean call
class RequestContext { }

// Prototype using constant (preferred — no typos)
@Component
@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
class AuditEntry { }

// Request scope (web only)
@Component
@RequestScope                     // shorthand for @Scope("request")
class CartSession { }

// Session scope
@Component
@SessionScope                     // one instance per HTTP session
class UserPreferences { }

// CGLIB scoped proxy (for injecting narrow-scoped into singleton)
@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
class RequestAttributes { }
```

**The scoped proxy problem and solution:**

```java
// PROBLEM: singleton holds a request-scoped bean — stale reference!
@Service  // singleton — created once at startup
class ReportService {
    @Autowired
    RequestAttributes attrs; // INJECTED ONCE — same object for ALL requests!
    // attrs references a single request-scoped proxy that won't update
}

// SOLUTION: use ScopedProxyMode so the injected reference is a proxy
// that delegates to the current scope's instance on each method call

@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
class RequestAttributes {
    private final String requestId = UUID.randomUUID().toString();
    public String getRequestId() { return requestId; }
}

// Now singleton injects the PROXY, not the actual instance
@Service
class ReportService {
    @Autowired RequestAttributes attrs; // proxy injected once
    void report() {
        // Each call: proxy looks up actual RequestAttributes for the current request
        log.info("Request: {}", attrs.getRequestId()); // correct per-request value
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Bean Scope:

What breaks without it:

1. All objects are singletons — shared mutable state creates race conditions in concurrent requests.
2. No way to tie object lifetime to an HTTP request or session — user-specific data leaks across requests.
3. Non-thread-safe objects (parsers, formatters, builders) cannot be safely managed as beans.
4. Object graphs cannot express "give me a fresh instance for each unit of work."

WITH Bean Scope:
→ Singleton scope: stateless services shared efficiently — zero object allocation overhead per request.
→ Prototype scope: fresh state per use — DTOs, command objects, builders that must not be reused.
→ Request/Session scope: per-HTTP-unit objects — security contexts, shopping carts, user preferences.
→ Scoped proxies: safely inject short-lived beans into long-lived beans without stale references.

---

### 🧠 Mental Model / Analogy

> Think of hotel room categories. A singleton bean is like the hotel lobby — one shared space, open 24/7, everyone uses the same room. A prototype bean is like a rental car — you get your own car when you rent, and it is returned (or not — Spring does not track it) when you are done. A request-scoped bean is like a hotel room assigned for one night — new assignment per visit, private during the stay, cleaned up after checkout. A session-scoped bean is like a loyalty club membership — it persists across multiple visits as long as your membership (session) is active.

"Hotel lobby" = singleton (shared, one instance for all)
"Rental car" = prototype (new instance per requester, no tracking)
"Hotel room for one night" = request scope (per HTTP request)
"Loyalty membership" = session scope (per user session)
"Proxy room key" = scoped proxy (key always opens the right room for the current guest)

---

### ⚙️ How It Works (Mechanism)

**Singleton vs Prototype at the container level:**

```
Singleton:
  ApplicationContext.getBean(UserService.class)
    → Check singletonObjects map: found?
      YES → return same instance (cached in ConcurrentHashMap)
      NO  → create, cache, return

Prototype:
  ApplicationContext.getBean(RequestContext.class)
    → Always: create new instance, inject deps, run PostConstruct
    → Return new instance (NOT cached — Spring forgets about it)
    → No destruction callbacks called by Spring
```

**Scoped proxy mechanism:**

```
Without proxy:
  Singleton [ReportService]
    field: RequestAttributes → points to Object@123 FOREVER
                                (first request's instance — WRONG for subsequent requests)

With ScopedProxyMode.TARGET_CLASS:
  Singleton [ReportService]
    field: RequestAttributes → points to ScopedProxy@456 (CGLIB proxy — lives as long as singleton)
                                        │
                                        └→ on each method call:
                                           → look up current request's scope
                                           → find (or create) RequestAttributes for THIS request
                                           → delegate method call to that instance
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean (the managed object)
        │
        ▼
Bean Scope  ◄──── (you are here)
(how many instances, how long they live)
        │
        ├─── singleton ────► ApplicationContext cache (shared, long-lived)
        ├─── prototype ────► new instance per getBean (no tracking)
        ├─── request   ────► RequestContextHolder (HTTP request storage)
        ├─── session   ────► HttpSession (user session storage)
        │
        ▼
Scoped Proxy (ScopedProxyMode.TARGET_CLASS)
(bridges narrow-scoped beans into singleton injection points)
        │
        ▼
CGLIB Proxy / JDK Dynamic Proxy
(proxy mechanism used for scope delegation)
```

---

### 💻 Code Example

**Example 1 — Prototype scope for non-thread-safe parsers:**

```java
@Component
@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
class CsvParser {
    private List<String[]> rows = new ArrayList<>(); // mutable state — unsafe to share

    public List<String[]> parse(InputStream input) throws IOException {
        try (CSVReader reader = new CSVReader(new InputStreamReader(input))) {
            rows = reader.readAll();
            return Collections.unmodifiableList(rows);
        }
    }
}

// Usage — each injection gets a fresh CsvParser
@Service
class DataImportService {
    private final ApplicationContext ctx;
    DataImportService(ApplicationContext ctx) { this.ctx = ctx; }

    void importData(InputStream in) throws IOException {
        // Must use getBean for prototype — field injection gives one instance
        CsvParser parser = ctx.getBean(CsvParser.class); // fresh instance!
        List<String[]> rows = parser.parse(in);
        // ... process rows
    }
}
```

**Example 2 — Request-scoped bean with scoped proxy:**

```java
// Request-scoped bean: holds per-request trace ID
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST,
       proxyMode = ScopedProxyMode.TARGET_CLASS)
class RequestTrace {
    private final String traceId = UUID.randomUUID().toString();
    public String getTraceId() { return traceId; }
}

// Singleton service — safely injects the scoped proxy
@Service
class OrderService {
    private final OrderRepository repo;
    private final RequestTrace trace; // proxy — safe to inject into singleton

    OrderService(OrderRepository repo, RequestTrace trace) {
        this.repo = repo;
        this.trace = trace;
    }

    public Order createOrder(OrderRequest req) {
        log.info("[{}] Creating order", trace.getTraceId()); // correct per-request value
        return repo.save(new Order(req, trace.getTraceId()));
    }
}
```

**Example 3 — Prototype bean with ObjectFactory for lazy fresh instances:**

```java
@Service
class BatchProcessor {
    // ObjectFactory provides on-demand prototype creation
    private final ObjectFactory<BatchJob> jobFactory;

    BatchProcessor(ObjectFactory<BatchJob> jobFactory) {
        this.jobFactory = jobFactory;
    }

    public void process(List<Item> items) {
        BatchJob job = jobFactory.getObject(); // fresh prototype each time
        job.execute(items);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                                               | Reality                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Singleton beans are thread-safe                                                                             | Singleton scope means one instance, not thread-safe. If the bean has mutable fields, it requires explicit synchronisation. Stateless beans are naturally thread-safe; stateful singletons are not                                                                                        |
| Prototype scope calls `@PreDestroy` when done                                                               | Spring does not track prototype instances after creation. `@PreDestroy` is NEVER called. The caller is responsible for cleanup if the prototype holds resources                                                                                                                          |
| A singleton injecting a request-scoped bean automatically gets the current request's instance               | Without scoped proxy (`proxyMode = ScopedProxyMode.TARGET_CLASS`), the singleton gets the instance from the time it was created — a stale reference. Scoped proxy is required for correctness                                                                                            |
| `@Scope("prototype")` on a `@Bean` method creates a new instance each call within the same `@Configuration` | Due to CGLIB proxying of `@Configuration` classes, `@Bean` method calls are intercepted and return the cached scope instance. For prototype scope, Spring creates a new instance each time the `@Bean` method is called from OUTSIDE the configuration class, not when called internally |

---

### 🔥 Pitfalls in Production

**Injecting a prototype-scoped bean into a singleton via `@Autowired` — always the same instance**

```java
@Component
@Scope("prototype")
class AuditContext {
    private String userId; // per-operation state
    // setters...
}

// BAD: field injection of prototype into singleton
@Service
class AuditService {
    @Autowired
    private AuditContext ctx; // INJECTED ONCE — always the SAME instance!
    // Spring creates one AuditContext during AuditService construction
    // and reuses it forever — prototype scope has no effect here

    public void audit(String userId) {
        ctx.setUserId(userId); // race condition — shared ctx mutated
    }
}

// GOOD: use ApplicationContext.getBean() or ObjectFactory<>
@Service
class AuditService {
    private final ObjectProvider<AuditContext> ctxProvider;
    AuditService(ObjectProvider<AuditContext> ctxProvider) {
        this.ctxProvider = ctxProvider;
    }

    public void audit(String userId) {
        AuditContext ctx = ctxProvider.getObject(); // fresh instance each call
        ctx.setUserId(userId);
        // ...
    }
}
```

---

**Not using scoped proxy — singleton holds stale request-scoped reference**

The stale reference causes: for the first request, the correct user data is returned. For all subsequent requests, the first request's user data is returned — a serious data-leak security bug.

```java
// BAD: no proxy mode — SecurityContext from first request is captured at injection
@Component
@Scope("request")  // missing proxyMode!
class SecurityContext { private String currentUser; ... }

@Service // singleton — injected once, SecurityContext reference never updates
class DataService {
    @Autowired SecurityContext ctx; // BUG: always first request's ctx
}

// GOOD: add proxyMode
@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
class SecurityContext { ... }
```

---

### 🔗 Related Keywords

- `Bean` — the object whose scope is being configured
- `Bean Lifecycle` — scope controls how many lifecycle sequences occur (singleton = once, prototype = per-use)
- `CGLIB Proxy` — the mechanism behind `ScopedProxyMode.TARGET_CLASS` scoped proxies
- `JDK Dynamic Proxy` — alternative proxy mode for `ScopedProxyMode.INTERFACES`
- `@RequestScope / @SessionScope` — shorthand annotations for web scopes
- `ObjectFactory / ObjectProvider` — Spring helper for on-demand prototype retrieval without ApplicationContext coupling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SCOPE        │ INSTANCES  │ LIFECYCLE              │     │
│ singleton    │ 1 per ctx  │ startup → ctx close    │     │
│ prototype    │ 1 per req  │ creation → GC (no BPP) │     │
│ request      │ 1 per HTTP │ request start → end    │     │
│ session      │ 1 per sess │ session start → expire │     │
├──────────────┼────────────────────────────────────────────┤
│ PROXY TRAP   │ Injecting narrow into wide scope requires │
│              │ proxyMode = ScopedProxyMode.TARGET_CLASS  │
├──────────────┼────────────────────────────────────────────┤
│ PROTOTYPE    │ Spring forgets prototype beans after       │
│ CAVEAT       │ creation — @PreDestroy never called        │
├──────────────┼────────────────────────────────────────────┤
│ ONE-LINER    │ "Scope = how many rooms Spring rents:      │
│              │ one lobby (singleton) or a fresh room      │
│              │ per guest (prototype/request/session)."    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `@SessionScope` bean stores a shopping cart. A `@Service` singleton processes checkout. The singleton injects the session-scoped bean via `ScopedProxyMode.TARGET_CLASS`. Under load, 10,000 concurrent users each have an active session. Explain in detail how Spring resolves the correct shopping cart instance on each request: what data structure stores the session-scoped instances, where that data structure lives (thread-local vs `HttpSession`), how the CGLIB proxy knows which session is "current" for each request thread, and what happens if two threads for the same user's session call checkout concurrently.

**Q2.** Spring's `@Scope("prototype")` combined with `@Configuration`'s CGLIB interception means that calling a `@Bean` method multiple times within a `@Configuration` class returns the scoped result. However, `@Scope("prototype")` + `@Bean` inside a `@Component`-annotated class (a "lite mode" configuration) behaves differently. Explain the difference between `@Configuration` (full mode) and `@Component` (lite mode) for `@Bean` methods, why lite-mode `@Bean` methods are NOT intercepted by CGLIB, and what the implication is for prototype-scoped `@Bean` methods declared inside a `@Component` class called internally.
