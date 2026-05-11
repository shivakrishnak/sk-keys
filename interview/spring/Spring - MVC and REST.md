---
layout: default
title: "Spring - MVC and REST"
parent: "Spring"
grand_parent: "Interview Mastery"
nav_order: 3
permalink: /interview/spring/mvc-and-rest/
topic: Spring
subtopic: MVC and REST
keywords:
  - DispatcherServlet and Request Processing
  - RestController and Request Mapping
  - Exception Handling
  - Validation
  - Filters and Interceptors
difficulty_range: easy to medium
status: in-progress
version: 3
---

**Keywords covered in this file:**

- [DispatcherServlet and Request Processing](#dispatcherservlet-and-request-processing)
- [RestController and Request Mapping](#restcontroller-and-request-mapping)
- [Exception Handling](#exception-handling)
- [Validation](#validation)
- [Filters and Interceptors](#filters-and-interceptors)

# DispatcherServlet and Request Processing

**TL;DR** - DispatcherServlet is the front controller that receives all HTTP requests and dispatches them to the appropriate handler (controller method) through a pipeline of handler mappings, adapters, and view resolvers.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Each URL requires its own servlet registered in web.xml. Routing logic scattered across dozens of servlets. No unified way to handle cross-cutting concerns (logging, auth, content negotiation).

**THE INVENTION MOMENT:**
"This is exactly why the front controller pattern was created."
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
DispatcherServlet is the traffic cop. Every request comes to it first, and it figures out which controller method should handle it.

**Level 2 - How to use it (junior developer):**

In Spring Boot, DispatcherServlet is auto-configured. You just write controllers:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Request processing pipeline:

```
HTTP Request
     |
     v
Filter Chain (Security, CORS, etc.)
     |
     v
DispatcherServlet.doDispatch()
     |
     v
HandlerMapping (find handler for URL)
     |  (returns HandlerExecutionChain)
     v
HandlerInterceptor.preHandle()
     |
     v
HandlerAdapter.handle()
     |  (invokes @Controller method)
     v
Return value processing
     |  (ResponseBody -> JSON)
     v
HandlerInterceptor.postHandle()
     |
     v
Response to client
```

**Level 4 - Mastery (senior/staff+ engineer):**

**HandlerMapping resolution order:**

1. `RequestMappingHandlerMapping` - @RequestMapping annotations
2. `RouterFunctionMapping` - functional endpoints
3. `SimpleUrlHandlerMapping` - static resources

**Content negotiation:**

- `Accept` header -> response format (JSON, XML)
- URL suffix (deprecated) or query param (`?format=xml`)
- `@RequestMapping(produces = "application/json")`

**Async request processing:**

```java
@GetMapping("/slow")
public Callable<Result> slowEndpoint() {
    return () -> {
        // Runs on async thread
        // Frees servlet thread for other requests
        return expensiveOperation();
    };
}
```




**The Senior-to-Staff Leap:**
A Senior says: "[TODO: What a competent senior would say]"
A Staff says: "[TODO: What demonstrates next-level abstraction]"
The difference: [TODO: 1 sentence - the mental model shift]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]
**TRIGGER PHRASE:** [TODO: 5-7 words activating full mental model]
**OPENING SENTENCE:** [TODO: First sentence showing immediate depth]

**If you remember only 3 things:**

1. All requests go through DispatcherServlet (front controller)
2. Pipeline: Filters -> Interceptors -> Handler -> Response
3. HandlerMapping resolves URL to controller method
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for DispatcherServlet and Request Processing. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between a Filter and a HandlerInterceptor?**

_Why they ask:_ Tests understanding of the request processing layers.

_Strong answer:_

| Aspect        | Filter                               | HandlerInterceptor           |
| ------------- | ------------------------------------ | ---------------------------- |
| Level         | Servlet API (javax/jakarta)          | Spring MVC                   |
| Scope         | All requests (including static)      | Only dispatched requests     |
| Access to     | Raw request/response                 | Handler, ModelAndView        |
| Wrap request? | Yes (ServletRequestWrapper)          | No                           |
| Use for       | Security, CORS, logging, compression | Auth checks, logging, timing |

Filters run BEFORE DispatcherServlet. Interceptors run INSIDE DispatcherServlet's processing.

```java
// Filter: wraps or blocks at servlet level
@Component
public class RequestIdFilter extends OncePerRequestFilter {
    protected void doFilterInternal(
            HttpServletRequest req,
            HttpServletResponse res,
            FilterChain chain) {
        String id = UUID.randomUUID().toString();
        MDC.put("requestId", id);
        res.setHeader("X-Request-Id", id);
        chain.doFilter(req, res);
        MDC.clear();
    }
}

// Interceptor: Spring-aware, has handler info
@Component
public class TimingInterceptor
        implements HandlerInterceptor {
    public boolean preHandle(
            HttpServletRequest req,
            HttpServletResponse res,
            Object handler) {
        req.setAttribute("start",
            System.nanoTime());
        return true;
    }
}
```
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# RestController and Request Mapping

**TL;DR** - `@RestController` combines `@Controller` + `@ResponseBody` for REST APIs, and `@RequestMapping` variants (`@GetMapping`, etc.) map HTTP methods and URLs to handler methods with automatic JSON serialization.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Manually reading request bodies, parsing JSON, setting content types, writing response bytes. Every endpoint repeats serialization/deserialization boilerplate.
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
You annotate a method with `@GetMapping("/users")`, return a Java object, and Spring automatically converts it to JSON and sends it as the HTTP response.

**Level 2 - How to use it (junior developer):**

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @GetMapping
    public List<Order> list(
            @RequestParam(defaultValue = "0")
            int page) {
        return orderService.findAll(page);
    }

    @GetMapping("/{id}")
    public Order get(@PathVariable Long id) {
        return orderService.findById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Order create(
            @Valid @RequestBody CreateOrderReq req) {
        return orderService.create(req);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        orderService.delete(id);
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Parameter binding annotations:

| Annotation       | Source              | Example           |
| ---------------- | ------------------- | ----------------- |
| `@PathVariable`  | URL path            | `/users/{id}`     |
| `@RequestParam`  | Query string        | `?page=2&size=10` |
| `@RequestBody`   | Request body (JSON) | POST/PUT body     |
| `@RequestHeader` | HTTP header         | `Authorization`   |
| `@CookieValue`   | Cookie              | Session cookie    |

**ResponseEntity for full control:**

```java
@GetMapping("/{id}")
public ResponseEntity<Order> get(
        @PathVariable Long id) {
    return orderService.findById(id)
        .map(order -> ResponseEntity.ok()
            .header("X-Order-Status",
                order.getStatus().name())
            .body(order))
        .orElse(ResponseEntity.notFound()
            .build());
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Jackson customization:**

```java
// Ignore nulls globally
spring.jackson.default-property-inclusion=non_null

// Per-class control
@JsonInclude(JsonInclude.Include.NON_NULL)
public record OrderResponse(
    @JsonProperty("order_id") Long id,
    @JsonFormat(pattern = "yyyy-MM-dd")
    LocalDate created,
    @JsonIgnore String internalNote) {}
```

**API versioning strategies:**

```java
// URL versioning (most common)
@RequestMapping("/api/v2/orders")

// Header versioning
@GetMapping(headers = "X-API-Version=2")

// Content negotiation
@GetMapping(produces =
    "application/vnd.myapp.v2+json")
```




**The Senior-to-Staff Leap:**
A Senior says: "[TODO: What a competent senior would say]"
A Staff says: "[TODO: What demonstrates next-level abstraction]"
The difference: [TODO: 1 sentence - the mental model shift]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]
**TRIGGER PHRASE:** [TODO: 5-7 words activating full mental model]
**OPENING SENTENCE:** [TODO: First sentence showing immediate depth]

**If you remember only 3 things:**

1. `@RestController` = `@Controller` + `@ResponseBody` (auto JSON)
2. Use `ResponseEntity<T>` when you need headers/status control
3. `@Valid` on `@RequestBody` triggers bean validation automatically
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for RestController and Request Mapping. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between @Controller and @RestController?**

_Why they ask:_ Tests basic Spring MVC understanding.

_Strong answer:_

`@Controller`: Returns view names (template rendering). Methods return String (view name) or ModelAndView. For server-side rendering (Thymeleaf, JSP).

`@RestController`: Every method return value is serialized directly to the response body (JSON/XML). Equivalent to `@Controller` + `@ResponseBody` on every method.

```java
@Controller
class WebController {
    @GetMapping("/page")
    String showPage(Model model) {
        model.addAttribute("name", "World");
        return "greeting"; // -> greeting.html
    }
}

@RestController
class ApiController {
    @GetMapping("/api/data")
    Data getData() {
        return new Data("value"); // -> JSON
    }
}
```
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Exception Handling

**TL;DR** - Spring provides `@ExceptionHandler`, `@ControllerAdvice`, and `ProblemDetail` (RFC 7807) for centralized, consistent error responses across all REST endpoints without try-catch in every controller.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every controller method has try-catch blocks returning different error formats. Some return 500 for business errors, others return 200 with error messages in the body. Clients can't reliably parse error responses.
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of catching exceptions in every method, you define one central place that converts exceptions to proper HTTP error responses.

**Level 2 - How to use it (junior developer):**

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ProblemDetail handleNotFound(
            NotFoundException ex) {
        ProblemDetail pd = ProblemDetail
            .forStatusAndDetail(
                HttpStatus.NOT_FOUND,
                ex.getMessage());
        pd.setTitle("Resource Not Found");
        return pd;
    }

    @ExceptionHandler(
        MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleValidation(
            MethodArgumentNotValidException ex) {
        ProblemDetail pd = ProblemDetail
            .forStatus(HttpStatus.BAD_REQUEST);
        pd.setTitle("Validation Failed");
        pd.setProperty("errors",
            ex.getFieldErrors().stream()
                .map(e -> Map.of(
                    "field", e.getField(),
                    "message",
                        e.getDefaultMessage()))
                .toList());
        return pd;
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Exception resolution order:

1. `@ExceptionHandler` in the same controller
2. `@ExceptionHandler` in `@ControllerAdvice` (global)
3. `ResponseStatusException` (inline in controller)
4. Default Spring error handling (whitelabel)

**RFC 7807 ProblemDetail (Spring 6+):**

```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User with ID 42 not found",
  "instance": "/api/users/42"
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Exception hierarchy for APIs:**

```java
public abstract class ApiException
        extends RuntimeException {
    abstract HttpStatus getStatus();
    abstract String getType();
}

public class NotFoundException extends ApiException {
    HttpStatus getStatus() {
        return HttpStatus.NOT_FOUND;
    }
}

// Single handler for all:
@ExceptionHandler(ApiException.class)
public ProblemDetail handle(ApiException ex) {
    ProblemDetail pd = ProblemDetail
        .forStatusAndDetail(
            ex.getStatus(), ex.getMessage());
    pd.setType(URI.create(ex.getType()));
    return pd;
}
```




**The Senior-to-Staff Leap:**
A Senior says: "[TODO: What a competent senior would say]"
A Staff says: "[TODO: What demonstrates next-level abstraction]"
The difference: [TODO: 1 sentence - the mental model shift]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]
**TRIGGER PHRASE:** [TODO: 5-7 words activating full mental model]
**OPENING SENTENCE:** [TODO: First sentence showing immediate depth]

**If you remember only 3 things:**

1. `@RestControllerAdvice` + `@ExceptionHandler` = centralized error handling
2. Use `ProblemDetail` (RFC 7807) for consistent error response format
3. Create an exception hierarchy with HTTP status mapping for clean code
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Exception Handling. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: How do you ensure consistent error responses across 50 microservices?**

_Why they ask:_ Tests architectural thinking.

_Strong answer:_

1. **Shared library:** Common exception classes + `@ControllerAdvice` in a shared starter
2. **RFC 7807 standard:** All services return ProblemDetail format
3. **Error catalog:** Documented error types with URIs
4. **Contract testing:** Validate error response schema in integration tests

```java
// Shared starter auto-configures:
@AutoConfiguration
public class ErrorHandlingAutoConfig {
    @Bean
    @ConditionalOnMissingBean
    public GlobalExceptionHandler handler() {
        return new GlobalExceptionHandler();
    }
}
```
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Validation

**TL;DR** - Spring integrates Jakarta Bean Validation (`@Valid`) to automatically validate request bodies, path variables, and method parameters, returning structured 400 errors for invalid input.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Manual if-checks for every field: `if (name == null || name.isBlank()) throw...`. Validation logic duplicated across controllers. Easy to forget a check. Inconsistent error messages.
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Annotate fields with rules (`@NotNull`, `@Size`, `@Email`), and Spring automatically rejects invalid requests before your code runs.

**Level 2 - How to use it (junior developer):**

```java
public record CreateUserRequest(
    @NotBlank String name,
    @Email String email,
    @Min(18) @Max(150) int age,
    @Size(min = 8) String password) {}

@PostMapping("/users")
public User create(
        @Valid @RequestBody CreateUserRequest req) {
    // Only reached if validation passes!
    return userService.create(req);
}
```

**Level 3 - How it works (mid-level engineer):**

Validation annotations:

- `@NotNull` / `@NotBlank` / `@NotEmpty`
- `@Size(min, max)` - string/collection length
- `@Min` / `@Max` - numeric bounds
- `@Email` / `@Pattern(regexp)` - format
- `@Past` / `@Future` - date constraints
- `@Valid` on nested objects - recursive validation

**Custom validator:**

```java
@Constraint(validatedBy = PhoneValidator.class)
@Target(FIELD)
@Retention(RUNTIME)
public @interface ValidPhone {
    String message() default "Invalid phone";
    Class<?>[] groups() default {};
    Class<?>[] payload() default {};
}

public class PhoneValidator implements
        ConstraintValidator<ValidPhone, String> {
    public boolean isValid(String value,
            ConstraintValidatorContext ctx) {
        return value != null &&
            value.matches("\\+\\d{10,15}");
    }
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Validation groups for different contexts:**

```java
interface OnCreate {}
interface OnUpdate {}

record UserRequest(
    @Null(groups = OnCreate.class)
    @NotNull(groups = OnUpdate.class)
    Long id,

    @NotBlank(groups = {OnCreate.class,
        OnUpdate.class})
    String name) {}

@PostMapping
public User create(
    @Validated(OnCreate.class)
    @RequestBody UserRequest req) {}
```




**The Senior-to-Staff Leap:**
A Senior says: "[TODO: What a competent senior would say]"
A Staff says: "[TODO: What demonstrates next-level abstraction]"
The difference: [TODO: 1 sentence - the mental model shift]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]
**TRIGGER PHRASE:** [TODO: 5-7 words activating full mental model]
**OPENING SENTENCE:** [TODO: First sentence showing immediate depth]

**If you remember only 3 things:**

1. `@Valid` + `@RequestBody` = automatic validation before handler executes
2. Failed validation throws `MethodArgumentNotValidException` (400)
3. Custom constraints: annotation + ConstraintValidator implementation
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Validation. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Filters and Interceptors

**TL;DR** - Filters operate at the servlet level (before/after DispatcherServlet), interceptors operate within Spring MVC (before/after handler execution). Use filters for cross-cutting concerns like security and logging; interceptors for handler-aware logic.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every controller method must check authentication, log timing, set CORS headers, and validate request IDs. Duplication across 100+ endpoints. Miss one and you have a security hole.
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Filters and interceptors are checkpoints that every request passes through before reaching your controller - like airport security before the gate.

**Level 2 - How to use it (junior developer):**

```java
// Filter: Servlet level
@Component
@Order(1)
public class LoggingFilter
        extends OncePerRequestFilter {
    protected void doFilterInternal(
            HttpServletRequest req,
            HttpServletResponse res,
            FilterChain chain) throws Exception {
        long start = System.currentTimeMillis();
        chain.doFilter(req, res);
        long ms = System.currentTimeMillis() - start;
        log.info("{} {} -> {} ({}ms)",
            req.getMethod(), req.getRequestURI(),
            res.getStatus(), ms);
    }
}
```

```java
// Interceptor: Spring MVC level
@Component
public class AuthInterceptor
        implements HandlerInterceptor {

    public boolean preHandle(
            HttpServletRequest req,
            HttpServletResponse res,
            Object handler) {
        String token = req.getHeader("Authorization");
        if (!authService.isValid(token)) {
            res.setStatus(401);
            return false; // stop processing
        }
        return true; // continue
    }
}

@Configuration
public class WebConfig
        implements WebMvcConfigurer {
    public void addInterceptors(
            InterceptorRegistry registry) {
        registry.addInterceptor(authInterceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/public/**");
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Execution order:

```
Request ->
  Filter 1 (before) ->
    Filter 2 (before) ->
      DispatcherServlet ->
        Interceptor preHandle ->
          Controller method ->
        Interceptor postHandle ->
      DispatcherServlet ->
    Filter 2 (after) ->
  Filter 1 (after) ->
Response
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Use cases:**

- **Filter:** Request/response wrapping, compression, CORS, rate limiting, request ID injection
- **Interceptor:** Auth checks needing handler info, audit logging, locale resolution, tenant resolution

Filter can wrap request/response (modify what downstream sees). Interceptor cannot.




**The Senior-to-Staff Leap:**
A Senior says: "[TODO: What a competent senior would say]"
A Staff says: "[TODO: What demonstrates next-level abstraction]"
The difference: [TODO: 1 sentence - the mental model shift]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]
**TRIGGER PHRASE:** [TODO: 5-7 words activating full mental model]
**OPENING SENTENCE:** [TODO: First sentence showing immediate depth]

**If you remember only 3 things:**

1. Filters: servlet level, wrap request/response, for security/logging/CORS
2. Interceptors: Spring MVC level, have handler info, for auth/audit
3. Order: Filters run first (outside), Interceptors run inside DispatcherServlet
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Filters and Interceptors. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]
