---
version: 2
layout: default
title: "DispatcherServlet"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /spring/dispatcherservlet/
id: SPR-016
category: Spring Core
difficulty: ★★☆
depends_on: ApplicationContext, Bean, IoC
used_by: Spring MVC, Spring Boot, REST Controllers, @RequestMapping
related: HandlerMapping, Filter vs Interceptor, ViewResolver, HandlerAdapter, "@RequestMapping"
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - webdev
---

# SPR-025 - DispatcherServlet

⚡ TL;DR - DispatcherServlet is the single Front Controller for all HTTP requests in Spring MVC - it delegates to HandlerMapping (which controller?), HandlerAdapter (call it), and ViewResolver (render the response).

| #392            | Category: Spring Core                                                                | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | ApplicationContext, Bean, IoC                                                        |                 |
| **Used by:**    | Spring MVC, Spring Boot, REST Controllers, @RequestMapping                           |                 |
| **Related:**    | HandlerMapping, Filter vs Interceptor, ViewResolver, HandlerAdapter, @RequestMapping |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 50 REST endpoints. Without a single dispatcher, each URL needs its own Servlet registered in `web.xml`. Each Servlet has its own initialization, its own request parsing, its own exception handling. Adding cross-cutting behavior (authentication, logging, content negotiation) to all 50 Servlets means code in 50 places. URL routing logic is duplicated or hardcoded in each Servlet.

**THE BREAKING POINT:**
The raw Servlet model maps one URL pattern to one Servlet class. At scale (hundreds of endpoints), this O(N) configuration model becomes unmaintainable. There's no single place to add pre/post processing.

**THE INVENTION MOMENT:**
"This is exactly why the Front Controller pattern was applied - one entry point for all requests."

---

### 📘 Textbook Definition

**DispatcherServlet** (`org.springframework.web.servlet.DispatcherServlet`) is Spring MVC's central Front Controller - a single `HttpServlet` that handles ALL HTTP requests matching its URL mapping (typically `/`). It delegates request processing to a chain of collaborators: **HandlerMapping** (maps request to a handler - a `@Controller` method), **HandlerAdapter** (invokes the handler in a type-safe way), **HandlerExceptionResolver** (handles exceptions thrown by handlers), **ViewResolver** (resolves logical view names to concrete views - for REST, typically `MappingJackson2HttpMessageConverter`). Spring Boot auto-configures a `DispatcherServlet` bean and registers it with the embedded servlet container via `DispatcherServletAutoConfiguration`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DispatcherServlet is the single HTTP traffic cop - every request goes through it, and it routes to the right controller.

**One analogy:**

> DispatcherServlet is an airport terminal. Every passenger (HTTP request) enters the terminal (DispatcherServlet). The information desk (HandlerMapping) tells them which gate (controller method). The gate agent (HandlerAdapter) processes their boarding (invokes the method). The airline (ViewResolver/MessageConverter) packages their flight experience (response). Exceptions are handled at the customer service desk (HandlerExceptionResolver). The terminal itself doesn't know anything about each flight's details - it just coordinates.

**One insight:**
The Front Controller pattern converts N separate request handlers into 1 dispatcher + N routing rules. Pre/post processing (authentication, logging, CORS) is applied once, at the dispatcher level.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. One DispatcherServlet per web application (typically).
2. All requests matching the DispatcherServlet's URL pattern pass through it.
3. DispatcherServlet has its own WebApplicationContext (child context) that can access the root ApplicationContext.
4. Delegates to pluggable strategy beans (HandlerMapping, HandlerAdapter, etc.) - all configurable.
5. Spring Boot auto-configures the DispatcherServlet - you don't declare it manually.

**PROCESSING CHAIN:**

```
HTTP Request
    ↓
Filter chain (Servlet filters - OUTSIDE DispatcherServlet)
    ↓
DispatcherServlet.service()
    ↓
DispatcherServlet.doDispatch():
  1. getHandler() → HandlerMapping.getHandler() → HandlerExecutionChain
  2. getHandlerAdapter(handler) → HandlerAdapter
  3. HandlerInterceptor.preHandle() (Spring interceptors)
  4. HandlerAdapter.handle() → invoke controller method → ModelAndView
  5. HandlerInterceptor.postHandle()
  6. processDispatchResult() → ViewResolver / MessageConverter → response
  7. HandlerInterceptor.afterCompletion()
    ↓
HTTP Response
```

---

### 🧪 Thought Experiment

**SETUP:**
You want to add request timing (log duration of every request) and authentication (reject unauthorized requests) to all endpoints.

**WITHOUT DispatcherServlet (raw Servlet per endpoint):**

- 50 endpoints = 50 Servlets = add timing and auth code in 50 places

**WITH DispatcherServlet:**

- Timing: one Servlet `Filter` or one Spring `HandlerInterceptor` - zero changes to controllers
- Auth: one Spring Security `Filter` - zero changes to controllers

**THE INSIGHT:**
The single-entry-point model makes adding cross-cutting concerns O(1) regardless of how many endpoints exist.

---

### 🧠 Mental Model / Analogy

> DispatcherServlet is a corporate switchboard operator. Every incoming call (HTTP request) goes to the switchboard (DispatcherServlet). The operator looks up the directory (HandlerMapping), connects to the right department (controller), waits for the answer (method return), and routes the reply back to the caller (response). All calls go through the switchboard - you add hold music once (interceptor), not in each department.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
DispatcherServlet is the single "front door" for all HTTP requests in a Spring web application. Every request goes through it, and it decides which controller method handles each request.

**Level 2 - How to use it (junior developer):**
In Spring Boot, you don't configure DispatcherServlet - it's auto-configured. Your `@RestController` and `@RequestMapping` annotations tell HandlerMapping how to route requests. Customize it via `spring.mvc.*` properties. For multiple DispatcherServlets (different URL namespaces), register additional `DispatcherServletRegistrationBean` beans.

**Level 3 - How it works (mid-level engineer):**
`DispatcherServlet.initStrategies()` initializes the 9 strategy beans from its WebApplicationContext: `HandlerMapping`, `HandlerAdapter`, `HandlerExceptionResolver`, `ViewResolver`, `LocaleResolver`, `ThemeResolver`, `MultipartResolver`, `FlashMapManager`, `RequestToViewNameTranslator`. `doDispatch()` is the core method. For REST APIs: `RequestMappingHandlerMapping` maps to `@RequestMapping` methods; `RequestMappingHandlerAdapter` invokes the method; `HttpMessageConverter` (Jackson) serializes the return value. No `ViewResolver` needed for `@ResponseBody`.

**Level 4 - Why it was designed this way (senior/staff):**
The DispatcherServlet's pluggable strategy model is an example of the Strategy + Template Method patterns. The template (`doDispatch`) defines the fixed workflow; the strategies are configurable. This design allows Spring MVC to support radically different use cases (classical MVC with Thymeleaf, REST with JSON, file serving) through strategy substitution without forking the core dispatcher. Spring Boot's auto-configuration provides sensible defaults for all 9 strategies - enabling zero-config REST APIs - while keeping every strategy overridable. This "opinionated defaults with flexible overrides" model is the defining characteristic of Spring Boot's auto-configuration philosophy.

---

### ⚙️ How It Works (Mechanism)

**doDispatch() - abbreviated:**

```java
protected void doDispatch(HttpServletRequest request,
                           HttpServletResponse response) throws Exception {
    // 1. Determine handler (controller method)
    HandlerExecutionChain mappedHandler = getHandler(request);
    // throws NoHandlerFoundException if no mapping

    // 2. Get adapter that knows how to invoke the handler
    HandlerAdapter ha = getHandlerAdapter(mappedHandler.getHandler());

    // 3. Interceptors pre-handle
    mappedHandler.applyPreHandle(request, response);

    // 4. Invoke the handler (controller method)
    ModelAndView mv = ha.handle(request, response, mappedHandler.getHandler());

    // 5. Interceptors post-handle
    mappedHandler.applyPostHandle(request, response, mv);

    // 6. Resolve view and render / write response
    processDispatchResult(request, response, mappedHandler, mv, exception);
    // For @ResponseBody: Jackson serializes directly here

    // 7. Interceptors afterCompletion
    mappedHandler.triggerAfterCompletion(request, response, null);
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**REST request: POST /users:**

```
HTTP POST /users with JSON body
    ↓
Servlet filter chain (Spring Security auth filter, CORS filter)
    ↓
DispatcherServlet.doDispatch()
    ↓
HandlerMapping: POST /users → UserController.createUser()
    ↓ ← YOU ARE HERE (DispatcherServlet routes to controller)
HandlerInterceptor.preHandle() (logging, custom checks)
    ↓
HandlerAdapter: invoke createUser(User user)
  → @RequestBody deserialized via Jackson
  → UserController.createUser(User) → User result
    ↓
HandlerInterceptor.postHandle()
    ↓
@ResponseBody: Jackson serializes User → JSON
    ↓
HandlerInterceptor.afterCompletion()
    ↓
HTTP 201 Created with JSON response
```

---

### 💻 Code Example

**Example 1 - Spring Boot (DispatcherServlet auto-configured):**

```java
// Spring Boot creates and registers DispatcherServlet automatically
// Just write controllers:
@RestController
@RequestMapping("/users")
public class UserController {

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User createUser(@Valid @RequestBody CreateUserRequest req) {
        return userService.create(req);
    }

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id)
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND, "User not found: " + id));
    }
}
```

**Example 2 - Customize DispatcherServlet properties:**

```properties
# application.properties
spring.mvc.servlet.path=/api      # DispatcherServlet URL pattern
spring.mvc.throw-exception-if-no-handler-found=true
spring.web.resources.add-mappings=false  # disable default static resource handler
```

**Example 3 - Multiple DispatcherServlets (separate contexts):**

```java
@Configuration
public class MultiDispatcherConfig {

    @Bean  // default DispatcherServlet at /
    public DispatcherServletRegistrationBean apiDispatcher() {
        DispatcherServlet ds = new DispatcherServlet();
        ds.setApplicationContext(apiContext());
        DispatcherServletRegistrationBean reg =
            new DispatcherServletRegistrationBean(ds, "/api/*");
        reg.setName("apiDispatcher");
        return reg;
    }

    @Bean  // second DispatcherServlet at /admin
    public DispatcherServletRegistrationBean adminDispatcher() {
        // ... similar setup for /admin/* with separate context
    }
}
```

---

### ⚖️ Comparison Table

| Component              | Runs                           | Scope                               | Can Access Spring Context |
| ---------------------- | ------------------------------ | ----------------------------------- | ------------------------- |
| **Servlet Filter**     | Before/after DispatcherServlet | Entire HTTP pipeline                | Only if Spring-managed    |
| **HandlerInterceptor** | Inside DispatcherServlet       | After routing, before/after handler | Yes (Spring bean)         |
| **ControllerAdvice**   | Exception/response handling    | Post-handler                        | Yes                       |
| **AOP Aspect**         | On Spring bean method calls    | Business layer                      | Yes                       |

---

### ⚠️ Common Misconceptions

| Misconception                                                        | Reality                                                                                                                                                                                       |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spring Boot creates a new DispatcherServlet for each @RestController | One DispatcherServlet handles all controllers registered in the same WebApplicationContext.                                                                                                   |
| DispatcherServlet processes requests asynchronously by default       | Standard DispatcherServlet is synchronous. Async support requires @Async, DeferredResult, or WebFlux (different servlet).                                                                     |
| Filters and HandlerInterceptors are equivalent                       | Filters are Servlet-level (before DispatcherServlet). Interceptors are Spring MVC-level (inside DispatcherServlet, after routing). Filters can't access Spring beans directly unless wrapped. |

---

### 🚨 Failure Modes & Diagnosis

**404 Not Found for valid endpoint**

**Symptom:** `NoHandlerFoundException` or browser/curl gets 404 for a known endpoint.

**Root Cause:** Controller not in component-scan scope, wrong URL mapping, or DispatcherServlet not mapped to the request path.

**Diagnostic Command / Tool:**

```bash
# List all registered request mappings
curl http://localhost:8080/actuator/mappings | jq .
# Or log at startup:
logging.level.org.springframework.web.servlet.mvc.method.annotation=TRACE
```

**Fix:** Verify `@RestController` is in a package under `@SpringBootApplication`, or add `@ComponentScan(basePackages = "...")`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ApplicationContext` - DispatcherServlet lives in the WebApplicationContext

**Builds On This (learn these next):**

- `HandlerMapping` - how DispatcherServlet finds the right controller method
- `Filter vs Interceptor` - the pre/post processing hooks DispatcherServlet supports

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single Front Controller Servlet for all   │
│              │ HTTP requests in Spring MVC               │
├──────────────┼───────────────────────────────────────────┤
│ FLOW         │ Request → Filter → DispatcherServlet      │
│              │ → HandlerMapping → HandlerAdapter         │
│              │ → Controller method → MessageConverter    │
│              │ → Response                                │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ Auto-configured - no XML/annotation needed│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The single entry point that routes every │
│              │  HTTP request to the right controller."  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `DispatcherServlet` has its own `WebApplicationContext` (child context) that is separate from the root `ApplicationContext`. What is in each context? Why are there two separate contexts? When would having a single `ApplicationContext` be incorrect?

**Q2.** Spring Boot embeds a Tomcat/Jetty/Undertow server and registers `DispatcherServlet` programmatically rather than via `web.xml`. Trace the sequence of events from `SpringApplication.run()` to the first HTTP request being handled by `DispatcherServlet`. At what point is the embedded container started, and when does `DispatcherServlet` register itself?
