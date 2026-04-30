---
layout: default
title: "DispatcherServlet"
parent: "Spring & Spring Boot"
nav_order: 124
permalink: /spring/dispatcher-servlet/
number: "124"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "Servlet API, HTTP, ApplicationContext, Spring MVC"
used_by: "HandlerMapping, HandlerAdapter, @RequestMapping, Filter, Interceptor"
tags: #java, #spring, #springboot, #intermediate, #networking
---

# 124 — DispatcherServlet

`#java` `#spring` `#springboot` `#intermediate` `#networking`

⚡ TL;DR — Spring MVC's front controller servlet that receives every HTTP request and delegates to the appropriate handler, applying interceptors, view resolution, and exception handling along the way.

| #124 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Servlet API, HTTP, ApplicationContext, Spring MVC | |
| **Used by:** | HandlerMapping, HandlerAdapter, @RequestMapping, Filter, Interceptor | |

---

### 📘 Textbook Definition

The **`DispatcherServlet`** is Spring MVC's implementation of the Front Controller design pattern. It is a `javax.servlet.http.HttpServlet` (Jakarta EE in Spring 6) registered at the root URL mapping (typically `/`) of the web application. It delegates request processing through a coordinated chain: `HandlerMapping` selects the handler; `HandlerAdapter` invokes it; `HandlerInterceptor`s apply pre/post logic; `ViewResolver` resolves the logical view name to a concrete `View`; and `HandlerExceptionResolver` handles exceptions. In Spring Boot, it is auto-configured by `DispatcherServletAutoConfiguration` and embedded within the embedded Tomcat/Jetty/Undertow server — no `web.xml` required.

---

### 🟢 Simple Definition (Easy)

`DispatcherServlet` is Spring's traffic controller for HTTP requests. Every request hits it first, and it figures out which controller method should handle it, calls that method, and sends back the response.

---

### 🔵 Simple Definition (Elaborated)

In a plain Java EE application, you'd configure specific servlets for each URL. Spring flips this: one central `DispatcherServlet` handles all URLs and delegates internally. It reads the URL, finds the matching `@RequestMapping` method via `HandlerMapping`, invokes it via `HandlerAdapter`, converts arguments and return values, and handles any exceptions. This centralisation means cross-cutting concerns (authentication, logging, CORS) need to be configured in one place rather than per-servlet. Spring Boot removes even the `web.xml` configuration — `DispatcherServlet` is registered automatically via auto-configuration.

---

### 🔩 First Principles Explanation

**The problem — per-URL servlet explosion:**

Without a front controller:

```
web.xml (traditional approach):
  <servlet>
    <servlet-name>orders</servlet-name>
    <servlet-class>OrderServlet</servlet-class>
  </servlet>
  <servlet-mapping>
    <url-pattern>/orders/*</url-pattern>
  </servlet-mapping>

  <servlet>
    <servlet-name>users</servlet-name>
    <servlet-class>UserServlet</servlet-class>
  </servlet>
  <servlet-mapping>
    <url-pattern>/users/*</url-pattern>
  </servlet-mapping>
  <!-- Repeat for every resource type -->
```

Each servlet independently handles authentication, logging, content negotiation. Changing how sessions work means editing 50 servlets.

**The Front Controller pattern:**

```
┌─────────────────────────────────────────────────────┐
│  FRONT CONTROLLER PATTERN                           │
│                                                     │
│  ALL HTTP requests → DispatcherServlet              │
│                              │                      │
│          ┌───────────────────┤                      │
│          ↓                   ↓                      │
│    HandlerMapping      Filter Chain                 │
│    (find handler)      (security, CORS)             │
│          │                                          │
│          ↓                                          │
│    HandlerAdapter                                   │
│    (invoke handler)                                 │
│          │                                          │
│          ↓                                          │
│    ViewResolver / MessageConverter                  │
│    (render response)                                │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT DispatcherServlet:**

```
Without a front controller:

  Authentication: 50 servlets × auth check = 50 copies
  CORS: must configure on every servlet separately
  Content negotiation: each servlet decides JSON vs XML
  Exception handling: each servlet has its own catch block
  Request logging: wrapped around each servlet individually
  → Every cross-cutting change requires 50 edits
```

**WITH DispatcherServlet:**

```
→ One place to configure authentication (SecurityFilter)
→ One place for CORS (CorsConfig)
→ One place for exception handling (@ControllerAdvice)
→ One place for content negotiation (ContentNegotiationStrategy)
→ One place for request logging (HandlerInterceptor)
→ Add new endpoint: add @RequestMapping method — zero config
→ Spring Boot: zero web.xml, embedded server, auto-configured
```

---

### 🧠 Mental Model / Analogy

> `DispatcherServlet` is the **main reception desk of a large hotel**. Every guest (HTTP request) checks in here first. The receptionist (DispatcherServlet) looks up which room (controller handler) the guest is booked in, uses the right key system (HandlerAdapter — different for different handler types), applies the hotel's standard procedures (interceptors — check-in policy, welcome drink), and if something goes wrong sends the guest to the concierge (HandlerExceptionResolver). All guests go through one desk — no need to train every floor separately.

"Main reception desk" = DispatcherServlet
"Looking up the room booking" = HandlerMapping
"Key system" = HandlerAdapter (different handler types need different invocation)
"Standard procedures" = HandlerInterceptors
"Concierge for problems" = HandlerExceptionResolver

---

### ⚙️ How It Works (Mechanism)

**Request processing sequence:**

```
┌─────────────────────────────────────────────────────┐
│  DISPATCHERSERVLET REQUEST FLOW                     │
├─────────────────────────────────────────────────────┤
│  1. Servlet container calls service(req, res)       │
│  2. Determine locale / theme / multipart            │
│  3. HandlerMapping.getHandler(request)              │
│     → returns HandlerExecutionChain                 │
│       (handler + pre/post HandlerInterceptors)      │
│  4. HandlerInterceptor.preHandle() for each         │
│     → false = abort processing, return immediately  │
│  5. HandlerAdapter.handle(req, res, handler)        │
│     → argument resolution (@PathVariable, @Body…)   │
│     → invoke handler method                         │
│     → return ModelAndView or write response body    │
│  6. HandlerInterceptor.postHandle()                 │
│  7. processDispatchResult()                         │
│     → ViewResolver if ModelAndView present          │
│     → ExceptionResolver if exception occurred       │
│  8. HandlerInterceptor.afterCompletion()            │
└─────────────────────────────────────────────────────┘
```

**Spring Boot auto-configuration:**

```java
// DispatcherServletAutoConfiguration registers:
@Bean(name = DEFAULT_DISPATCHER_SERVLET_BEAN_NAME)
public DispatcherServlet dispatcherServlet(
    WebMvcProperties wp) {
  DispatcherServlet ds = new DispatcherServlet();
  ds.setThrowExceptionIfNoHandlerFound(
      wp.isThrowExceptionIfNoHandlerFound());
  return ds;
}

@Bean(name = DEFAULT_DISPATCHER_SERVLET_REGISTRATION_BEAN_NAME)
public DispatcherServletRegistrationBean registration(
    DispatcherServlet ds) {
  DispatcherServletRegistrationBean reg =
      new DispatcherServletRegistrationBean(ds, "/");
  return reg;
}
// Registers DS at "/" — handles all requests
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP Request arrives at embedded Tomcat
        ↓
  Servlet Filter Chain (security, CORS, encoding)
        ↓
  DISPATCHERSERVLET (124)  ← you are here
  (front controller — orchestrates dispatch)
        ↓
  HandlerMapping (125) → finds handler (@RequestMapping)
  HandlerInterceptor → pre/post hooks
  HandlerAdapter → invokes handler method
        ↓
  @RestController method executes
        ↓
  MessageConverter → JSON/XML serialisation
  ViewResolver → template rendering (if MVC)
        ↓
  HTTP Response returned
```

---

### 💻 Code Example

**Example 1 — Custom DispatcherServlet configuration:**

```java
// Customize DispatcherServlet behaviour in Spring Boot
@Bean
public DispatcherServletRegistrationBean
    dispatcherServletRegistration(
        DispatcherServlet ds) {
  DispatcherServletRegistrationBean reg =
      new DispatcherServletRegistrationBean(ds, "/api/*");
  // Mount only on /api/* (not root /)
  // Let other servlets handle non-API paths
  reg.setLoadOnStartup(1);
  return reg;
}

// OR via properties:
// spring.mvc.servlet.path=/api
```

**Example 2 — Diagnosing DispatcherServlet request handling:**

```yaml
# Enable request/response logging in Spring Boot
logging:
  level:
    org.springframework.web.servlet.DispatcherServlet: TRACE
# TRACE logs every step:
# "DispatcherServlet: GET /api/orders"
# "Mapped to com.example.OrderController#list()"
# "Using @ResponseBody with ...MappingJackson2HttpMessageConverter"
```

**Example 3 — Multiple DispatcherServlets (API + admin):**

```java
// Register two separate DispatcherServlets
// Each with its own ApplicationContext
@Configuration
public class WebConfig {
  @Bean
  @Primary
  DispatcherServletRegistrationBean apiServlet() {
    DispatcherServlet ds = new DispatcherServlet(apiContext);
    DispatcherServletRegistrationBean reg =
        new DispatcherServletRegistrationBean(ds, "/api/*");
    return reg;
  }

  @Bean
  DispatcherServletRegistrationBean adminServlet() {
    DispatcherServlet ds = new DispatcherServlet(adminContext);
    DispatcherServletRegistrationBean reg =
        new DispatcherServletRegistrationBean(ds, "/admin/*");
    return reg;
  }
}
```

---

### 🔁 Flow / Lifecycle

```
Spring Boot startup:
  1. Embedded Tomcat starts
  2. DispatcherServlet registered at "/"
  3. DispatcherServlet.init() → loads MVC components:
     HandlerMappings, HandlerAdapters,
     ViewResolvers, ExceptionResolvers
────────────────────────────────────────
HTTP GET /api/orders?page=0

  4. Filter chain: SecurityFilter, CorsFilter
  5. DispatcherServlet.doDispatch(req, res)
  6. HandlerMapping resolves → OrderController.list()
  7. Interceptor.preHandle() × N
  8. HandlerAdapter resolves @RequestParam page
  9. OrderController.list(page=0) executes
  10. Returns List<Order> → @ResponseBody
  11. Jackson serialises → JSON response body
  12. Interceptor.postHandle() × N
  13. Interceptor.afterCompletion() × N
────────────────────────────────────────
HTTP 200 OK, Content-Type: application/json
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DispatcherServlet and Filter are at the same level | Filters are in the Servlet container layer and run BEFORE DispatcherServlet. Interceptors are inside DispatcherServlet and run after it receives the request |
| Spring Boot creates a DispatcherServlet per controller | One DispatcherServlet handles all requests unless you explicitly register multiple instances for different URL paths |
| DispatcherServlet creates the ApplicationContext | The ApplicationContext is created by SpringApplication.run() before the embedded server starts. DispatcherServlet receives a reference to the existing context |
| Returning null from a handler method means 404 | Null return means "no model" — DispatcherServlet may still search for a view. @ResponseBody null returns HTTP 200 with empty body |

---

### 🔥 Pitfalls in Production

**1. 404 for unmapped requests eating memory via NoHandlerFoundException**

```yaml
# BAD: default: no exception thrown for missing handler
# → DispatcherServlet logs WARN and returns 404 silently
# Spring searches for default-servlet (Tomcat's) unnecessarily

# GOOD: configure explicit 404 via exception
spring:
  mvc:
    throw-exception-if-no-handler-found: true
  web:
    resources:
      add-mappings: false  # don't serve static files
# → NoHandlerFoundException → @ExceptionHandler → clean 404 JSON
```

**2. Slow startup from scanning large classpath for MVC components**

```java
// DispatcherServlet.initStrategies() scans for all handler
// mappings on startup. In large apps with 500+ controllers:
// HandlerMapping initialization can take 200-500ms

// Diagnostic:
logging:
  level:
    org.springframework.web.servlet: DEBUG
// Look for "Detected X mappings in DispatcherServlet"
// Fix: use @EnableWebMvc + explicit HandlerMapping config
//      or Spring Boot lazy initialization (spring.main.lazy-initialization=true)
```

---

### 🔗 Related Keywords

- `HandlerMapping` — resolves incoming requests to handler methods (entry #125)
- `Filter` — Servlet-level interceptor running before DispatcherServlet reaches it
- `HandlerInterceptor` — Spring MVC-level interceptor running inside DispatcherServlet
- `@RequestMapping` — the annotation whose mappings HandlerMapping works with
- `@ControllerAdvice` — global exception handling registered with ExceptionResolver
- `WebFlux` — Spring's reactive alternative; uses `DispatcherHandler` instead

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Front controller: all HTTP requests enter │
│              │ here → delegated to the right handler     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always active in Spring MVC; customise    │
│              │ path, exception handling, interceptors    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't configure DispatcherServlet at a    │
│              │ specific path if all requests should hit  │
│              │ it (the default "/" is correct)           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One reception desk for the whole hotel — │
│              │  all guests check in here first."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HandlerMapping (125) →                    │
│              │ Filter vs Interceptor (126)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot registers `DispatcherServlet` at the default path `/`. In a microservice, you also want Prometheus metrics at `/actuator/prometheus` and a health endpoint at `/health` served by a different thread pool to avoid blocking health checks when the app is under load. Describe the architecture using two `DispatcherServlets` (or one DispatcherServlet + a separate management port) — including how Spring Boot's `management.server.port` achieves separation, what `ManagementContextConfiguration` does, and whether the management context shares beans with the main application context.

**Q2.** In Spring MVC, `HandlerInterceptor.afterCompletion()` is guaranteed to fire even if the handler throws an exception. However, `HandlerInterceptor.postHandle()` is NOT called when an exception occurs. Explain the exact decision point in `DispatcherServlet.doDispatch()` source code where this branching happens, why `postHandle()` is skipped on exception, and describe the production scenario where a metric-recording `postHandle()` misses exception responses — causing your dashboards to show lower latency than actual (because the exception fast path is faster) and how to handle it correctly.

