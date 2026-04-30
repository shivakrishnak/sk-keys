---
layout: default
title: "HandlerMapping"
parent: "Spring & Spring Boot"
nav_order: 125
permalink: /spring/handler-mapping/
number: "125"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "DispatcherServlet, @RequestMapping, Spring MVC, HTTP"
used_by: "RequestMappingHandlerMapping, RouterFunctionMapping, Interceptor chain"
tags: #java, #spring, #springboot, #intermediate, #networking
---

# 125 — HandlerMapping

`#java` `#spring` `#springboot` `#intermediate` `#networking`

⚡ TL;DR — The Spring MVC strategy that maps an incoming HTTP request to the controller method (handler) that should process it, plus the interceptors to apply.

| #125 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DispatcherServlet, @RequestMapping, Spring MVC, HTTP | |
| **Used by:** | RequestMappingHandlerMapping, RouterFunctionMapping, Interceptor chain | |

---

### 📘 Textbook Definition

`HandlerMapping` is a Spring MVC interface with one key method: `getHandler(HttpServletRequest)`, which returns a `HandlerExecutionChain` containing the handler object (typically a `HandlerMethod` for `@RequestMapping`-annotated controllers) and any `HandlerInterceptor`s to apply. `DispatcherServlet` iterates through all registered `HandlerMapping` implementations in priority order (by `Ordered`) until one returns a non-null result. The primary implementation is `RequestMappingHandlerMapping`, which builds a map of URL patterns + HTTP methods + header/parameter conditions to `HandlerMethod` objects at startup. Additional implementations include `RouterFunctionMapping` (functional endpoints) and `SimpleUrlHandlerMapping` (static resources).

---

### 🟢 Simple Definition (Easy)

`HandlerMapping` is Spring's routing table. When a request arrives for `GET /api/orders`, HandlerMapping finds the specific controller method registered for that URL and method, and tells DispatcherServlet which one to call.

---

### 🔵 Simple Definition (Elaborated)

Every `@RequestMapping` annotation in your application is registered in `RequestMappingHandlerMapping` at startup — it builds an internal lookup table from URL patterns + HTTP methods to controller methods. When a request comes in, `DispatcherServlet` asks all registered `HandlerMapping`s "who should handle this?" The first one that recognises the request returns the handler. This strategy pattern allows Spring to support multiple handler styles: annotation-based controllers, functional route definitions, and Actuator endpoints all register different HandlerMappings that coexist.

---

### 🔩 First Principles Explanation

**The routing problem:**

`DispatcherServlet` receives the raw `HttpServletRequest` without knowing which of the 200 `@RequestMapping` methods in the application should handle it. A naive approach — linear scan of all methods — would be O(N) per request. `RequestMappingHandlerMapping` solves this with an indexed lookup structure built at startup.

**RequestMappingHandlerMapping's internal structure:**

```
┌────────────────────────────────────────────────────────┐
│  MAPPING REGISTRY (built at ApplicationContext start)  │
│                                                        │
│  Key: RequestMappingInfo                               │
│    patterns: ["/api/orders", "/api/orders/*"]          │
│    methods: [GET]                                      │
│    params: none                                        │
│    headers: none                                       │
│    consumes: none                                      │
│    produces: [application/json]                        │
│  Value: HandlerMethod                                  │
│    bean: orderController                               │
│    method: list(Pageable pageable)                     │
│                                                        │
│  Lookup: URL pattern match → HTTP method filter        │
│          → consumes/produces filter → best match       │
└────────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT a HandlerMapping abstraction:**

```
Without HandlerMapping:

  DispatcherServlet hardcodes routing logic:
    if (path.startsWith("/api")) useApiHandler()
    else if (path.startsWith("/admin")) useAdminHandler()
    → Every routing style requires DS code changes

  Can't mix @RequestMapping + functional routes
    → One routing style per application
  
  Can't prioritise: URL-template vs exact match
    → Ambiguous resolution, no clear winner rule
```

**WITH HandlerMapping:**

```
→ Strategy pattern: multiple HandlerMappings coexist
  in priority order (lowest order = checked first)
→ RequestMappingHandlerMapping: annotation-based
→ RouterFunctionMapping: WebFlux functional style
→ SimpleUrlHandlerMapping: static resources, Actuator
→ WelcomePageHandlerMapping: "/" → welcome page
→ DispatcherServlet iterates until one answers
→ No coupling between routing logic and DS
```

---

### 🧠 Mental Model / Analogy

> `HandlerMapping` is like a **post office sorting algorithm**. When mail arrives (HTTP request), the sorting machine checks the address (URL + method) against all registered delivery routes (handler registrations). The route with the most specific match wins — a street address beats a ZIP code match. Multiple sorting algorithms (HandlerMappings) run in order; the first one that claims the mail wins.

"Mail arriving" = HTTP request
"Sorting machine checking routes" = HandlerMapping.getHandler()
"Registered delivery routes" = @RequestMapping registrations
"Most specific match wins" = RequestMappingInfo specificity comparison
"Multiple sorting algorithms" = multiple HandlerMapping beans in priority order

---

### ⚙️ How It Works (Mechanism)

**HandlerMapping priority in Spring Boot:**

```
Priority order (lower number = checked first):
  0: RequestMappingHandlerMapping (@RequestMapping)
  1: RouterFunctionMapping (functional endpoints)
  2: BeanNameUrlHandlerMapping (bean-name URLs)
  3: WelcomePageHandlerMapping (/ → index.html)
  -1: SimpleUrlHandlerMapping (resources, actuator)
```

**Inspecting registered mappings:**

```java
// Programmatic inspection of all registered mappings
@Component
public class MappingInspector {
  @Autowired
  RequestMappingHandlerMapping mapping;

  @PostConstruct
  void printMappings() {
    mapping.getHandlerMethods().forEach((info, method) -> {
      log.info("{} → {}#{}", info,
               method.getBeanType().getSimpleName(),
               method.getMethod().getName());
    });
  }
}
// Output:
// {GET /api/orders} → OrderController#list
// {POST /api/orders} → OrderController#create
```

**URL pattern matching specifics:**

```
More specific matches win:
  /api/orders/active  (literal) beats
  /api/orders/{id}   (template) beats
  /api/**            (wildcard)

HTTP method specificity:
  GET /orders beats
  any /orders (no method constraint)

Produces/Consumes narrowing:
  application/json beats
  */* (any content type)
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP Request → DispatcherServlet (124)
        ↓
  HANDLER MAPPING (125)  ← you are here
  iterates: [RequestMappingHM, RouterFunctionHM, ...]
        ↓
  Returns: HandlerExecutionChain
    handler = HandlerMethod (e.g. OrderController.list)
    interceptors = [AuthInterceptor, AuditInterceptor]
        ↓
  DispatcherServlet invokes HandlerAdapter
  (adapts handler invocation per type)
        ↓
  Handler (@RequestMapping method) executes
        ↓
  RequestMappingHandlerAdapter resolves:
  @PathVariable, @RequestParam, @RequestBody
```

---

### 💻 Code Example

**Example 1 — Custom condition in RequestMapping:**

```java
// Only matches if X-API-Version: 2 header present
@GetMapping(value = "/api/orders",
    headers = "X-API-Version=2")
public List<OrderV2> listV2() { ... }

// Fallback for all other versions
@GetMapping("/api/orders")
public List<OrderV1> listV1() { ... }
// HandlerMapping selects more specific (headers constraint) first
```

**Example 2 — Actuator via SimpleUrlHandlerMapping:**

```bash
# Spring Boot registers Actuator endpoints via its own
# HandlerMapping at order Integer.MIN_VALUE + 1
curl http://localhost:8080/actuator/health

# Inspect what's registered at runtime via Actuator:
curl http://localhost:8080/actuator/mappings | \
 jq '.contexts.application.mappings.dispatcherServlets
      .dispatcherServlet[].details.requestMappingConditions'
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| HandlerMapping is invoked per request to scan annotations | HandlerMapping builds its routing table at startup. Per-request: it performs an indexed lookup, not a scan |
| Only one HandlerMapping can be active | Spring Boot registers 4–6 HandlerMappings. DispatcherServlet tries each in priority order until one returns a handler |
| URL matching is case-sensitive by default | Spring MVC's AntPathMatcher is case-sensitive by default. Path normalisation can affect this |
| HandlerMapping and HandlerAdapter are the same component | HandlerMapping finds the handler; HandlerAdapter invokes it. Different concerns: finding vs calling |

---

### 🔥 Pitfalls in Production

**1. Ambiguous handler mapping throws startup exception**

```java
// BAD: two methods map to identical URL+method
@GetMapping("/api/orders")
public List<Order> list() {...}

@GetMapping(value = "/api/orders", params = "!status")
public List<Order> listAll() {...}

// Ambiguous: empty params could match both
// → IllegalStateException at startup:
// "Ambiguous handler methods mapped for '/api/orders'"

// GOOD: use explicit, non-overlapping conditions
// or consolidate to one method with optional @RequestParam
```

**2. Path variable clash with trailing slash**

```java
// BAD: GET /api/orders/active might match orders/{id}
// where id="active" — unintended match
@GetMapping("/api/orders/{id}")
public Order get(@PathVariable Long id) {
  // id = "active" → NumberFormatException!
}

@GetMapping("/api/orders/active")
public List<Order> listActive() {...}
// Both registered — Spring resolves by specificity:
// literal "active" beats {id} template
// BUT: if listActive not registered, active hits get()
// GOOD: keep literal routes consistent
```

---

### 🔗 Related Keywords

- `DispatcherServlet` — iterates through all HandlerMappings to find the handler
- `@RequestMapping` — the annotation whose metadata is indexed by RequestMappingHandlerMapping
- `HandlerInterceptor` — returned in the HandlerExecutionChain alongside the handler
- `HandlerAdapter` — invokes the handler method found by HandlerMapping
- `RouterFunctionMapping` — the functional endpoint equivalent HandlerMapping
- `@ControllerAdvice` — works with HandlerExceptionResolver to handle exceptions post-dispatch

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Maps HTTP request (URL + method) to the   │
│              │ controller method + interceptors to apply  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Customise routing: version headers,       │
│              │ content-type routing, priority ordering   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't create ambiguous mappings — Spring  │
│              │ throws IllegalStateException at startup   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HandlerMapping is the post office        │
│              │  sorting machine — most specific wins."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Filter vs Interceptor (126) →             │
│              │ @RequestMapping → @ControllerAdvice       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `RequestMappingHandlerMapping` builds its handler registry at `ApplicationContext` startup by scanning all `@Controller` beans for `@RequestMapping` annotations. In Spring Boot with 500 controllers and 3,000 mappings, this initialisation can add 300–500ms to startup. Describe two strategies to reduce this — one at the Spring MVC level (hint: caching the handler mapping info) and one at the JVM level (Spring Boot 3 AOT) — and explain why the Actuator `/actuator/mappings` endpoint can still list all 3,000 mappings even when AOT-processed.

**Q2.** Spring MVC's URL matching changed significantly in Spring 6: `PathPatternParser` replaced `AntPathMatcher` as the default. Explain the key performance difference between the two — why `PathPatternParser` is faster for matched paths at runtime — and describe the specific backward-compatibility issue with trailing slashes (`/api/orders/` vs `/api/orders`) that caused breakage when upgrading from Spring Boot 2 to Spring Boot 3, and how the `spring.mvc.pathmatch.use-suffix-pattern=false` property relates.

