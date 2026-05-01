---
layout: default
title: "HandlerMapping"
parent: "Spring Core"
nav_order: 393
permalink: /spring/handlermapping/
number: "393"
category: Spring Core
difficulty: ★★★
depends_on: "DispatcherServlet, ApplicationContext, Bean"
used_by: "DispatcherServlet, Filter vs Interceptor"
tags: #advanced, #spring, #internals, #architecture, #networking
---

# 393 — HandlerMapping

`#advanced` `#spring` `#internals` `#architecture` `#networking`

⚡ TL;DR — A **HandlerMapping** is the Spring MVC strategy that maps incoming HTTP requests to a handler (controller method, `HttpRequestHandler`, or other callable) and its associated `HandlerInterceptors`. `RequestMappingHandlerMapping` is the primary implementation that processes `@RequestMapping` and its shortcuts.

| #393            | Category: Spring Core                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | DispatcherServlet, ApplicationContext, Bean |                 |
| **Used by:**    | DispatcherServlet, Filter vs Interceptor    |                 |

---

### 📘 Textbook Definition

`HandlerMapping` is a Spring MVC interface that maps an `HttpServletRequest` to a `HandlerExecutionChain` — a wrapper containing the matched handler (typically a `HandlerMethod` referencing a `@Controller` method) and any associated `HandlerInterceptor` objects. The `DispatcherServlet` holds a list of `HandlerMapping` instances ordered by priority; it iterates them until one returns a non-null `HandlerExecutionChain`. The primary implementation, `RequestMappingHandlerMapping`, builds an internal registry of `@RequestMapping` annotations at startup — it indexes all `@Controller` beans, reads their `@RequestMapping`/`@GetMapping`/`@PostMapping` etc. annotations, and stores the resulting `RequestMappingInfo` objects in a `MappingRegistry`. For each request, it scores and selects the most specific matching `RequestMappingInfo` based on URL pattern, HTTP method, request parameters, headers, and content type. Other implementations include `SimpleUrlHandlerMapping` (explicit URL-to-handler registration) and `RouterFunctionMapping` (Spring WebFlux functional routing, also used in MVC via `RouterFunction` support).

---

### 🟢 Simple Definition (Easy)

HandlerMapping answers the question: "for this URL and HTTP method, which controller method should handle it?" It is the routing table of Spring MVC.

---

### 🔵 Simple Definition (Elaborated)

When a request arrives at the DispatcherServlet, it asks all registered HandlerMappings: "do you know who handles `POST /api/orders`?" The `RequestMappingHandlerMapping` looks at its registry of all `@RequestMapping` methods and finds `OrderController.createOrder()`, which is mapped to `@PostMapping("/api/orders")`. It returns that method wrapped in a `HandlerExecutionChain` that also includes any applicable `HandlerInterceptors`. The DispatcherServlet then asks a `HandlerAdapter` to actually invoke the handler. You rarely implement HandlerMapping directly — `@RequestMapping` annotations and auto-configuration handle this — but understanding it explains how URL routing, path variables, content negotiation, and method ambiguity resolution work.

---

### 🔩 First Principles Explanation

**`RequestMappingHandlerMapping` — how it builds the registry at startup:**

```
At startup, RMHM scans all @Controller/@RestController beans:
  For each bean:
    For each method:
      Is @RequestMapping (or alias @GetMapping etc.) present?
      YES → extract:
        url patterns:    ["/api/orders", "/api/v2/orders"]
        HTTP methods:    [POST]
        params:          []
        headers:         []
        consumes:        [application/json]
        produces:        [application/json]
      → build RequestMappingInfo
      → register: RequestMappingInfo → HandlerMethod(bean, method)

Registry structure:
  MappingRegistry {
    "/api/orders" POST → OrderController@123.createOrder(OrderRequest)
    "/api/orders" GET  → OrderController@123.getOrders()
    "/api/orders/{id}" GET → OrderController@123.getOrder(Long)
    ...
  }
```

**Request matching — how RMHM scores candidates:**

```
Request: GET /api/orders/123

Matching candidates from registry:
  1. GET /api/orders/{id}    ← URL matches with path variable
  2. GET /api/orders/**      ← wildcard match (lower priority)

Scoring (more specific = higher priority):
  1. Exact pattern match > path variable match > wildcard
  2. Most specific HTTP method match
  3. Most specific Content-Type / Accept match
  4. Most specific header / param conditions

Winner: GET /api/orders/{id} → OrderController.getOrder(Long id)

If TWO candidates score equally:
  → AmbiguousHandlerMethodsException at startup (detected early)
```

**HandlerExecutionChain — what getHandler() returns:**

```java
HandlerExecutionChain chain = handlerMapping.getHandler(request);
chain.getHandler();        // the HandlerMethod (controller method reference)
chain.getInterceptors();   // HandlerInterceptor[] applied to this request

// HandlerMethod provides:
HandlerMethod hm = (HandlerMethod) chain.getHandler();
hm.getMethod();            // java.lang.reflect.Method
hm.getBean();              // the controller bean instance
hm.getBeanType();          // OrderController.class
hm.getMethodParameters();  // MethodParameter[] (for argument resolution)
```

**Multiple HandlerMappings — DispatcherServlet priority ordering:**

```
DispatcherServlet holds List<HandlerMapping> sorted by @Order:
  1. RequestMappingHandlerMapping (order=0) ← @RequestMapping methods
  2. BeanNameUrlHandlerMapping (order=2)    ← beans named "/some/path"
  3. RouterFunctionMapping (order=-1)       ← Spring 5.2+ functional routes
  4. SimpleUrlHandlerMapping (order=max)    ← explicit URL registrations
     (includes static resource handlers)

For each request:
  Iterate in order → return first non-null HandlerExecutionChain
  → If none match: throw NoHandlerFoundException (if configured)
                   or forward to default servlet
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT HandlerMapping:

What breaks without it:

1. No way to map HTTP requests to Java methods without hardcoding routing logic.
2. `@RequestMapping` annotations would need to be processed by each servlet individually.
3. Path variable extraction (`/orders/{id}`), content negotiation, and parameter binding require a central registry.
4. HandlerInterceptors cannot be applied selectively based on URL pattern.

WITH HandlerMapping:
→ URL routing is declarative (`@GetMapping("/orders/{id}")`) and automatically registered.
→ Ambiguous mappings are detected at startup, not at runtime.
→ Content negotiation (Accept header, produces/consumes) is handled centrally.
→ HandlerInterceptors are associated with URL patterns cleanly.

---

### 🧠 Mental Model / Analogy

> Think of `RequestMappingHandlerMapping` as a well-organised switchboard operator with a complete directory. When a call arrives (HTTP request), the operator consults the directory (RequestMappingInfo registry) to find the right extension (controller method). The directory is compiled at startup from all the business cards distributed by staff members (all `@RequestMapping` annotations). Multiple scoring criteria ensure the most specific match is selected — if both a specific number and a "press 0 for general enquiries" option exist, the specific number wins. If two entries in the directory claim the same number (ambiguous mapping), the error is caught when compiling the directory (startup), not when the call arrives.

"Directory compiled at startup" = `MappingRegistry` built from `@RequestMapping` annotations
"Caller finding the right extension" = RMHM.getHandler(request) → HandlerMethod
"Most specific number wins" = specificity-based scoring (exact path > path variable > wildcard)
"Duplicate number catches at directory time" = `AmbiguousHandlerMethodsException` at startup

---

### ⚙️ How It Works (Mechanism)

**Content negotiation in HandlerMapping:**

```java
// Different handlers for same URL based on content type
@RestController
@RequestMapping("/api/orders")
class OrderController {

    // Handles: GET /api/orders  Accept: application/json
    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    List<Order> getOrdersJson() { ... }

    // Handles: GET /api/orders  Accept: application/xml
    @GetMapping(produces = MediaType.APPLICATION_XML_VALUE)
    OrderList getOrdersXml() { ... }

    // Handles: POST /api/orders  Content-Type: application/json
    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    Order createOrder(@RequestBody OrderRequest req) { ... }
}
// RMHM selects between methods using Accept and Content-Type headers
```

**Custom HandlerInterceptor registration via HandlerMapping:**

```java
@Configuration
class WebConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new RateLimitInterceptor())
                .addPathPatterns("/api/**")       // applies to these paths
                .excludePathPatterns("/api/health"); // not to health check
        registry.addInterceptor(new AuthInterceptor())
                .addPathPatterns("/api/admin/**")
                .order(1); // runs first among admin interceptors
    }
}
// WebMvcConfigurer adds interceptors to SimpleUrlHandlerMapping (or RMHM)
// They are included in the HandlerExecutionChain for matching requests
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP Request → DispatcherServlet
        │
        ▼
HandlerMapping  ◄──── (you are here)
(maps request → handler + interceptors)
        │
        ├── RequestMappingHandlerMapping → @RequestMapping methods
        ├── RouterFunctionMapping        → functional routes
        └── SimpleUrlHandlerMapping      → static resources, defaults
        │
        ▼
HandlerExecutionChain
  (handler: controller method + interceptors: pre/post hooks)
        │
        ▼
HandlerAdapter
(invokes the handler: argument resolution, @RequestBody binding, etc.)
        │
        ▼
Controller method execution
```

---

### 💻 Code Example

**Inspecting the handler mapping registry programmatically:**

```java
@Component
class HandlerMappingInspector implements CommandLineRunner {

    @Autowired
    RequestMappingHandlerMapping handlerMapping;

    @Override
    public void run(String... args) {
        Map<RequestMappingInfo, HandlerMethod> registry =
            handlerMapping.getHandlerMethods();

        registry.forEach((info, method) -> {
            log.info("Endpoint: {} {} → {}.{}",
                info.getMethodsCondition(),
                info.getPatternsCondition(),
                method.getBeanType().getSimpleName(),
                method.getMethod().getName());
        });
    }
}
// Output sample:
// Endpoint: {POST} {[/api/orders]} → OrderController.createOrder
// Endpoint: {GET}  {[/api/orders/{id}]} → OrderController.getOrder
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                            |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HandlerMapping` directly invokes controller methods            | `HandlerMapping` only maps requests to handlers — it does NOT invoke them. Invocation is done by `HandlerAdapter` (specifically `RequestMappingHandlerAdapter` for `@RequestMapping` methods)                                                      |
| There is only one `HandlerMapping` in a Spring MVC app          | Spring MVC maintains a list of `HandlerMapping` implementations. `DispatcherServlet` iterates them in `@Order` priority. `RequestMappingHandlerMapping` handles `@RequestMapping`; `SimpleUrlHandlerMapping` handles static resources and defaults |
| Ambiguous `@RequestMapping` definitions throw errors at runtime | `RequestMappingHandlerMapping` detects conflicting (ambiguous) `@RequestMapping` registrations at startup and throws `IllegalStateException` — this is a build-time safety check, not a runtime failure                                            |
| `@RequestMapping` on a `@Controller` class is required          | A class-level `@RequestMapping` is optional — it serves as a prefix for all method-level mappings. Without it, method-level mappings are absolute from root                                                                                        |

---

### 🔥 Pitfalls in Production

**Path variable type mismatch — 400 Bad Request with no logging**

```java
@GetMapping("/orders/{id}")
Order getOrder(@PathVariable Long id) { ... }

// Request: GET /orders/not-a-number
// Spring: cannot convert "not-a-number" to Long
// Result: MethodArgumentTypeMismatchException → 400 Bad Request
// Without @ExceptionHandler, the error message may be generic/missing

// GOOD: handle with @ExceptionHandler
@ExceptionHandler(MethodArgumentTypeMismatchException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
ErrorResponse handleTypeMismatch(MethodArgumentTypeMismatchException ex) {
    return new ErrorResponse("INVALID_PARAMETER",
        "Parameter '" + ex.getName() + "' must be of type "
        + ex.getRequiredType().getSimpleName());
}
```

---

### 🔗 Related Keywords

- `DispatcherServlet` — the controller that calls `HandlerMapping.getHandler()` for every request
- `Filter vs Interceptor` — HandlerInterceptors are part of the HandlerExecutionChain returned by HandlerMapping
- `ApplicationContext` — HandlerMapping scans `@Controller` beans from the context at startup

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INTERFACE    │ HandlerMapping.getHandler(request)        │
│              │ Returns: HandlerExecutionChain            │
├──────────────┼───────────────────────────────────────────┤
│ PRIMARY IMPL │ RequestMappingHandlerMapping              │
│              │ Processes @RequestMapping at startup      │
├──────────────┼───────────────────────────────────────────┤
│ SELECTION    │ Most specific pattern wins                │
│              │ Exact > path variable > wildcard          │
├──────────────┼───────────────────────────────────────────┤
│ AMBIGUITY    │ Detected at startup → IllegalStateException│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HandlerMapping = switchboard directory:  │
│              │  maps each incoming call to the right     │
│              │  controller extension."                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `RequestMappingHandlerMapping` selects the most specific matching `RequestMappingInfo` when multiple patterns could match a request. Describe the scoring algorithm: what is the ordering between an exact path match (`/orders/new`), a path variable match (`/orders/{id}`), and a wildcard (`/orders/**`)? Now describe the edge case where a request for `GET /orders/new` could match BOTH `/orders/{id}` (with `id="new"`) and `/orders/new` (an exact match for a "create new order" endpoint) — which wins and why? What is the implication for REST API design with user-provided IDs that could clash with reserved words?

**Q2.** In Spring Boot Actuator, endpoints like `/actuator/health` are registered via `WebMvcEndpointHandlerMapping` — a separate `HandlerMapping` implementation that registers actuator endpoints. Explain how having multiple `HandlerMapping` implementations in the same `DispatcherServlet` allows actuator endpoints to be secured differently from application endpoints: specifically, how does having separate `HandlerMapping` beans enable different `HandlerInterceptor` chains for different URL spaces? And what is the `@Order` value that `WebMvcEndpointHandlerMapping` uses relative to `RequestMappingHandlerMapping` to ensure actuator path precedence?
