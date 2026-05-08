---
layout: default
title: "HandlerMapping"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 41
permalink: /spring/handlermapping/
id: SPR-041
category: Spring Core
difficulty: ★★★
depends_on: DispatcherServlet, Bean, ApplicationContext
used_by: DispatcherServlet, Spring MVC, REST Controllers, WebFlux
related: DispatcherServlet, HandlerAdapter, "@RequestMapping", "@GetMapping", HandlerInterceptor
tags:
  - spring
  - springboot
  - advanced
  - pattern
  - webdev
---

# SPR-041 - HandlerMapping

⚡ TL;DR - HandlerMapping is the component DispatcherServlet uses to determine which controller method (handler) should handle an incoming HTTP request, based on URL, HTTP method, headers, and parameters - `RequestMappingHandlerMapping` processes `@RequestMapping` annotations.

| #393            | Category: Spring Core                                                               | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | DispatcherServlet, Bean, ApplicationContext                                         |                 |
| **Used by:**    | DispatcherServlet, Spring MVC, REST Controllers, WebFlux                            |                 |
| **Related:**    | DispatcherServlet, HandlerAdapter, @RequestMapping, @GetMapping, HandlerInterceptor |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`DispatcherServlet` receives all requests. But how does it know that `POST /users` goes to `UserController.createUser()` and `GET /users/42` goes to `UserController.getById(42)`? Without a routing mechanism, `DispatcherServlet` would need hardcoded URL-to-method mappings - fragile, not scalable.

**THE INVENTION MOMENT:**
"HandlerMapping is the lookup table that connects URLs to controller methods."

---

### 📘 Textbook Definition

**HandlerMapping** (`org.springframework.web.servlet.HandlerMapping`) is a Spring MVC interface that maps HTTP requests to a handler (a `@Controller` method, or any other request handler). `DispatcherServlet.getHandler()` iterates through all registered `HandlerMapping` beans in priority order and returns the first `HandlerExecutionChain` (handler + interceptors) that matches the request. The primary implementation is **`RequestMappingHandlerMapping`** - it discovers all `@RequestMapping`-annotated methods at startup, builds a map of request conditions (URL pattern, HTTP method, headers, params, media types) to handler methods, and performs matching via `MappingRegistry`. Other implementations: `BeanNameUrlHandlerMapping` (maps URL `/user` to bean named `/user`), `RouterFunctionMapping` (functional routing for WebFlux).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HandlerMapping is the routing table - it maps "POST /users" to "UserController.createUser()".

**One analogy:**

> HandlerMapping is a restaurant host's seating chart. When a party (HTTP request) arrives and says "table for two, near window" (POST /users, JSON body), the host consults the chart (HandlerMapping) and assigns table 7 (UserController.createUser). Multiple charts exist (multiple HandlerMappings) - the host checks them in priority order.

**One insight:**
HandlerMapping is evaluated at _request time_ - it's not a compile-time routing table. URL patterns with path variables (`/users/{id}`) require runtime path matching. This is why `RequestMappingHandlerMapping` stores pattern-based conditions, not literal URL strings.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Multiple HandlerMappings can coexist - DispatcherServlet iterates them in `@Order` priority.
2. `RequestMappingHandlerMapping` is the default and highest priority for `@RequestMapping` annotations.
3. Each HandlerMapping returns a `HandlerExecutionChain` = handler + list of `HandlerInterceptor`s.
4. The first HandlerMapping that matches the request wins.
5. If no HandlerMapping matches → `NoHandlerFoundException` → 404.

**REQUEST CONDITION MATCHING (in `RequestMappingHandlerMapping`):**

```
Incoming: GET /users/42 Accept: application/json

Match conditions evaluated:
  URL pattern: /users/{id} ← matches (id=42)
  HTTP method: GET ← matches
  Headers: (none required)
  Params: (none required)
  Content-Type: (not a GET, not checked)
  Accept: application/json ← matches (produces JSON)
  ↓
Handler: UserController.getById(Long id)
HandlerExecutionChain:
  handler = UserController.getById
  interceptors = [LoggingInterceptor, AuthInterceptor]
```

---

### 🧪 Thought Experiment

**SETUP:**
Two mappings match the same request:

```java
@GetMapping("/users/{id}")
public User getById(@PathVariable Long id) { ... }

@GetMapping("/users/{username}")
public User getByUsername(@PathVariable String username) { ... }
```

**AMBIGUITY RESOLUTION:**
`RequestMappingHandlerMapping` treats `{id}` and `{username}` as equally specific patterns for the same URL shape `/users/42`. Result: `AmbiguousHandlerMappingException` at startup. Spring cannot distinguish between the two at request time unless additional conditions (e.g., different HTTP methods, different params) differentiate them.

**FIX:**

```java
@GetMapping(value = "/users/{id}", params = "type=id")
public User getById(@PathVariable Long id) { ... }

@GetMapping(value = "/users/{username}", params = "type=username")
public User getByUsername(@PathVariable String username) { ... }

// Or: use different URL patterns
@GetMapping("/users/id/{id}")
@GetMapping("/users/name/{username}")
```

---

### 🧠 Mental Model / Analogy

> `RequestMappingHandlerMapping` is a multidimensional decision tree. The dimensions are: URL path pattern, HTTP method, Accept header, Content-Type header, query params, request headers. An incoming request traverses the decision tree - at each level, unmatching branches are pruned. The surviving leaf is the handler method. If multiple leaves survive, it's ambiguous (startup error). If no leaf survives, it's 404.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
HandlerMapping is the routing table that Spring MVC uses to decide "which controller method handles this HTTP request?" It looks at the URL, HTTP method, headers, and other request properties.

**Level 2 - How to use it (junior developer):**
You don't use HandlerMapping directly - `@RequestMapping`, `@GetMapping`, `@PostMapping`, etc., automatically register with `RequestMappingHandlerMapping`. To see all registered mappings: access `/actuator/mappings` (with Actuator) or enable debug logging.

**Level 3 - How it works (mid-level engineer):**
At startup, `RequestMappingHandlerMapping.afterPropertiesSet()` calls `initHandlerMethods()`, which scans all beans for `@RequestMapping` annotations and calls `registerHandlerMethod()` for each, building a `MappingRegistry`. At request time, `getHandler()` calls `lookupHandlerMethod()` which: (1) finds direct URL matches (exact), (2) finds pattern matches (with path variables), (3) scores candidates by specificity, (4) returns the best match. Path variable extraction is done by `UriTemplate` matching.

**Level 4 - Why it was designed this way (senior/staff):**
The `HandlerMapping` interface is an extension point. Spring's WebFlux uses `RouterFunctionMapping` (functional routing). Spring Security registers its own `HandlerMapping` for security endpoints. Spring Actuator registers `MvcEndpointHandlerMapping`. The ability to have multiple HandlerMappings in priority order allows different subsystems to register their own routing logic without conflicting. This is the Open/Closed principle at the framework level: the DispatcherServlet is closed for modification but open for extension via new HandlerMapping implementations. The `HandlerInterceptor`s returned in the `HandlerExecutionChain` are associated with specific URL patterns (via `addInterceptors` in `WebMvcConfigurer`) rather than applied globally - a finer-grained interception model than Servlet filters.

---

### ⚙️ How It Works (Mechanism)

**Startup registration:**

```
Application context refresh
    ↓
RequestMappingHandlerMapping.afterPropertiesSet():
  initHandlerMethods():
    For each Spring bean in context:
      hasRequestMappingAnnotation(bean)?
        YES → detectHandlerMethods(bean):
          For each method in class:
            @RequestMapping present?
              → getMappingForMethod(method)
              → creates RequestMappingInfo:
                  patterns = ["/users/{id}"]
                  methods = [GET]
                  produces = ["application/json"]
              → register in MappingRegistry
```

**Request-time lookup:**

```
DispatcherServlet.getHandler(request):
  for each HandlerMapping in ordered list:
    chain = handlerMapping.getHandler(request)
    if chain != null: return chain
  return null  →  404
```

---

### 🔄 The Complete Picture - End-to-End Flow

**REQUEST ROUTING:**

```
GET /users/42 Accept: application/json
    ↓
DispatcherServlet.getHandler()
    ↓
RequestMappingHandlerMapping.getHandler():
  lookupHandlerMethod("/users/42", GET):
    Candidates: [getById, getAll, createUser]
    Path match: /users/{id} → getById (score: specificity high)
    Method match: GET → matches getById
    Accept match: application/json → matches getById
    ↓ ← YOU ARE HERE (HandlerMapping selects handler)
    Best match: UserController.getById(Long id)
    Extract path vars: {id: "42"}
  ↓
Return HandlerExecutionChain:
  handler = UserController.getById
  interceptors = [AuthInterceptor, LoggingInterceptor]
    ↓
DispatcherServlet proceeds with HandlerAdapter.handle()
```

---

### 💻 Code Example

**Example 1 - @RequestMapping conditions:**

```java
@RestController
@RequestMapping("/users")
public class UserController {

    // GET /users - returns all users
    @GetMapping
    public List<User> getAll() { ... }

    // GET /users/42 - path variable
    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) { ... }

    // POST /users with JSON - creates user
    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    public User create(@Valid @RequestBody CreateUserRequest req) { ... }

    // GET /users?search=alice - query param based
    @GetMapping(params = "search")
    public List<User> search(@RequestParam String search) { ... }

    // GET /users with custom Accept header
    @GetMapping(produces = "application/vnd.company.user+json")
    public User getVndFormat() { ... }
}
```

**Example 2 - List all mappings (Actuator):**

```bash
# Requires spring-boot-starter-actuator and management.endpoints.web.exposure.include=mappings
curl http://localhost:8080/actuator/mappings | jq \
  '.contexts.application.mappings.dispatcherServlets.dispatcherServlet[]
   | select(.details.requestMappingConditions != null)
   | {method: .details.requestMappingConditions.methods,
      url: .details.requestMappingConditions.patterns}'
```

**Example 3 - Custom HandlerMapping (functional routing):**

```java
// Spring 5+ functional routing - alternative to @RequestMapping
@Configuration
public class RouterConfig {

    @Bean
    public RouterFunction<ServerResponse> userRoutes(UserHandler handler) {
        return RouterFunctions.route()
            .GET("/users/{id}", handler::getById)
            .POST("/users", handler::create)
            .DELETE("/users/{id}", handler::delete)
            .build();
    }
}
```

---

### ⚖️ Comparison Table

| HandlerMapping                 | Maps From                        | Used For                   |
| ------------------------------ | -------------------------------- | -------------------------- |
| `RequestMappingHandlerMapping` | @RequestMapping annotations      | 99% of Spring MVC apps     |
| `BeanNameUrlHandlerMapping`    | Bean name `/user` → bean `/user` | Legacy XML config          |
| `RouterFunctionMapping`        | RouterFunction                   | WebFlux functional routing |
| `SimpleUrlHandlerMapping`      | Static URL-to-handler map        | Custom static routing      |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HandlerMapping is only about URL matching                 | HandlerMapping matches on URL + HTTP method + headers + Accept + Content-Type + params. A GET and a POST to the same URL can map to different handlers. |
| @GetMapping is different from @RequestMapping(method=GET) | They're identical - @GetMapping is a composed meta-annotation for @RequestMapping(method=RequestMethod.GET).                                            |
| HandlerMapping runs on every request                      | The mapping registry is built at startup. Request-time lookup is a hash/tree lookup (fast), not a full re-scan.                                         |

---

### 🚨 Failure Modes & Diagnosis

**AmbiguousHandlerMappingException**

**Symptom:**
`java.lang.IllegalStateException: Ambiguous handler methods mapped for HTTP path '/users/42'`

**Root Cause:**
Two handler methods have identical request conditions (same URL pattern + method + conditions).

**Fix:**
Differentiate with additional conditions:

```java
@GetMapping(value = "/users/{id}", produces = "application/json")
@GetMapping(value = "/users/{id}", produces = "application/xml")
// OR use different URLs
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `DispatcherServlet` - HandlerMapping is one of DispatcherServlet's core strategies

**Builds On This (learn these next):**

- `Filter vs Interceptor` - HandlerInterceptors are returned with the handler from HandlerMapping
- `@Transactional` - often applied to service methods called by the controller that HandlerMapping routes to

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Routing table: request conditions →       │
│              │ handler method + interceptors             │
├──────────────┼───────────────────────────────────────────┤
│ DEFAULT IMPL │ RequestMappingHandlerMapping (processes   │
│              │ @RequestMapping annotations)              │
├──────────────┼───────────────────────────────────────────┤
│ MATCHES ON   │ URL pattern + HTTP method + Accept +      │
│              │ Content-Type + headers + params           │
├──────────────┼───────────────────────────────────────────┤
│ AMBIGUITY    │ Two mappings with identical conditions →  │
│              │ AmbiguousHandlerMappingException          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The routing table that connects HTTP      │
│              │  requests to controller methods."         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `RequestMappingHandlerMapping` returns a `HandlerExecutionChain` containing the handler method AND a list of `HandlerInterceptors`. These interceptors are added via `WebMvcConfigurer.addInterceptors()` with optional URL patterns. The DispatcherServlet calls `preHandle()` on interceptors BEFORE invoking the handler, and `postHandle()` AFTER. How does Spring handle the case where `preHandle()` returns `false` on the 3rd interceptor out of 5? What happens to the remaining interceptors and the handler?

**Q2.** Spring MVC and Spring WebFlux both use `HandlerMapping` concepts. But WebFlux uses `RouterFunctionMapping` and functional routing. What specific limitation of annotation-based `@RequestMapping` motivated the design of the functional routing alternative? Are there scenarios where functional routing is objectively better?
