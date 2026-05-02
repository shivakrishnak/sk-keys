---
layout: default
title: "DispatcherServlet"
parent: "Spring Core"
nav_order: 392
permalink: /spring/dispatcherservlet/
number: "392"
category: Spring Core
difficulty: ★★☆
depends_on: "ApplicationContext, Bean, Spring Boot Startup Lifecycle"
used_by: "HandlerMapping, Filter vs Interceptor"
tags: #intermediate, #spring, #architecture, #networking
---

# 392 — DispatcherServlet

`#intermediate` `#spring` `#architecture` `#networking`

⚡ TL;DR — The **DispatcherServlet** is Spring MVC's central request router — a single front-controller servlet that receives all HTTP requests and delegates them to the appropriate controller, handler mapping, view resolver, and exception handler.

| #392            | Category: Spring Core                                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | ApplicationContext, Bean, Spring Boot Startup Lifecycle |                 |
| **Used by:**    | HandlerMapping, Filter vs Interceptor                   |                 |

---

### 📘 Textbook Definition

The **DispatcherServlet** (`org.springframework.web.servlet.DispatcherServlet`) is the front controller in Spring MVC — a single `javax.servlet.http.HttpServlet` that receives all incoming HTTP requests and orchestrates their processing through a pipeline of collaborating components: `HandlerMapping` (maps request to handler), `HandlerAdapter` (invokes the handler), `HandlerExceptionResolver` (handles errors), `ViewResolver` (resolves logical view names to views), and `MessageConverter` (reads/writes request/response bodies). Each `DispatcherServlet` owns a child `WebApplicationContext` that can override beans defined in the root `ApplicationContext`. In Spring Boot, the `DispatcherServlet` is auto-configured as a bean (`DispatcherServletAutoConfiguration`) registered with the embedded servlet container, mapped to `"/"` by default. Spring Boot creates one `DispatcherServlet` per `WebMvcAutoConfiguration` — multiple `DispatcherServlet` instances can be configured for separate URL path prefixes.

---

### 🟢 Simple Definition (Easy)

The DispatcherServlet is the main entry point for all HTTP requests in a Spring MVC app — it acts like a traffic controller, receiving every request and routing it to the correct controller method.

---

### 🔵 Simple Definition (Elaborated)

In a traditional Java web app, each URL pattern maps directly to a specific servlet. Spring MVC takes a different approach: one servlet (`DispatcherServlet`) receives every HTTP request and acts as a coordinator. It asks `HandlerMapping`: "which controller handles this URL?" It asks `HandlerAdapter`: "how do I invoke this controller?" It passes the request to the controller, receives a result (view name or response body), and renders the response. In Spring Boot REST applications, `@RestController` methods return objects that `HttpMessageConverter` serialises to JSON — the `DispatcherServlet` orchestrates all of this without you writing any of the routing plumbing.

---

### 🔩 First Principles Explanation

**The request processing pipeline:**

```
HTTP Request arrives at server
        │
        ▼
Servlet Container (Tomcat/Jetty/Undertow)
        │
        ▼
Servlet Filters (FilterChain — pre-DispatcherServlet processing)
  e.g., CorsFilter, SecurityFilter, LoggingFilter
        │
        ▼
DispatcherServlet.service(request, response)
        │
        ▼
  1. HandlerMapping.getHandler(request)
     → Determines which controller/handler handles this URL
     → Returns HandlerExecutionChain (handler + HandlerInterceptors)

  2. HandlerInterceptors.preHandle()
     → Pre-processing before controller is called
     → Can abort the request (return false)

  3. HandlerAdapter.handle(request, response, handler)
     → Invokes the controller method
     → Resolves @PathVariable, @RequestParam, @RequestBody
     → Handles validation, data binding

  4. HandlerInterceptors.postHandle()
     → Post-processing after controller, before view rendering
     → Can modify ModelAndView

  5. ViewResolver.resolveViewName() → view.render(model, request, response)
     OR
     HttpMessageConverter.write(returnValue, response)
     (for @RestController / @ResponseBody)

  6. HandlerInterceptors.afterCompletion()
     → Always called after request (like finally)
     → Resource cleanup, logging

  7. HandlerExceptionResolver (if any step threw)
     → @ExceptionHandler methods, ResponseEntityExceptionHandler
        │
        ▼
HTTP Response sent to client
```

**DispatcherServlet context hierarchy:**

```
Root ApplicationContext (BootstrapContext / Servlet WebApplicationContext)
  → Shared beans: @Service, @Repository, DataSource, etc.
  → Loaded by ContextLoaderListener (traditional) or auto-configured (Boot)

  ├── DispatcherServlet WebApplicationContext (child context)
  │     → Web-specific beans: @Controller, HandlerMapping,
  │     │  ViewResolver, HandlerExceptionResolver
  │     → Can override root context beans
  │
  └── (optional) Second DispatcherServlet WebApplicationContext
        → Different URL prefix, different @Controller set
```

**Spring Boot auto-configuration:**

```java
// DispatcherServletAutoConfiguration (Spring Boot) configures:
@Bean(name = DEFAULT_DISPATCHER_SERVLET_BEAN_NAME)
public DispatcherServlet dispatcherServlet() {
    DispatcherServlet ds = new DispatcherServlet();
    ds.setThrowExceptionIfNoHandlerFound(properties.isThrowExceptionIfNoHandlerFound());
    ds.setPublishEvents(properties.isPublishRequestHandledEvents());
    ds.setEnableLoggingRequestDetails(properties.isLogRequestDetails());
    return ds;
}

// Registered with the embedded server mapped to "/"
@Bean
DispatcherServletRegistrationBean dispatcherServletRegistration(DispatcherServlet ds) {
    return new DispatcherServletRegistrationBean(ds, "/");
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT DispatcherServlet (raw servlet model):

What breaks without it:

1. Each URL requires a separate servlet class — no central coordination or shared infrastructure.
2. No unified exception handling — each servlet handles errors independently.
3. No shared interceptors, filters, view resolvers, or content negotiation.
4. Mapping request parameters to Java objects requires manual parsing in each servlet.

WITH DispatcherServlet:
→ One entry point — all concerns (routing, interceptors, exception handling, content negotiation) are centralised.
→ `@ExceptionHandler` and `@ControllerAdvice` work globally because all errors pass through one place.
→ `HandlerInterceptors` apply to all requests without modifying controller code.
→ `@RequestMapping` + `@RestController` are the only annotations needed — all routing is automatic.

---

### 🧠 Mental Model / Analogy

> Think of the DispatcherServlet as an airport operations centre. All flights (HTTP requests) arrive at the main terminal (DispatcherServlet). Operations consults the flight schedule (HandlerMapping) to determine which gate (controller) this flight should go to. Ground crews (HandlerInterceptors) check and prepare the plane before and after docking. The gate agent (HandlerAdapter) manages the actual boarding process (method invocation). If there is an incident (exception), the incident management team (HandlerExceptionResolver) handles it. The same operations centre manages ALL flights — there is no separate operations centre for each gate.

"Airport operations centre" = DispatcherServlet (single coordination point)
- "Flight schedule" = HandlerMapping (URL → controller mapping)
"Gate" = @Controller or @RestController method
"Ground crew check before docking" = HandlerInterceptor.preHandle()
"Gate agent managing boarding" = HandlerAdapter (invokes controller method)
"Incident management" = HandlerExceptionResolver (@ExceptionHandler, @ControllerAdvice)

---

### ⚙️ How It Works (Mechanism)

**HandlerMapping resolution for @RequestMapping:**

```
Request: POST /api/orders
        │
        ▼
RequestMappingHandlerMapping.getHandler(request):
  → Looks up @RequestMapping registry
  → Finds: OrderController.createOrder() @PostMapping("/api/orders")
  → Returns HandlerExecutionChain:
      handler:      OrderController@bean.createOrder (method reference)
      interceptors: [LoggingInterceptor, SecurityInterceptor]

RequestMappingHandlerAdapter.handle(request, response, handler):
  → @RequestBody: reads request body → ObjectMapper.readValue → OrderRequest
  → @Valid: validates OrderRequest via Validator
  → Invokes: orderController.createOrder(orderRequest)
  → Return type @ResponseBody / @RestController:
    → HttpMessageConverter.write(returnedOrder, response)
    → Jackson: JSON serialisation → response body
  → HTTP 201 Created sent to client
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP Request
        │
        ▼
Servlet Filters (pre-Spring security, CORS, logging)
        │
        ▼
DispatcherServlet  ◄──── (you are here)
(front controller: orchestrates the web processing pipeline)
        │
        ├──── HandlerMapping    → maps URL to controller method
        ├──── HandlerAdapter    → invokes the controller
        ├──── HandlerInterceptor→ pre/post processing
        ├──── ViewResolver      → renders view (MVC) or
        │     HttpMessageConverter → serialises body (REST)
        └──── HandlerExceptionResolver → @ExceptionHandler
        │
        ▼
HTTP Response
```

---

### 💻 Code Example

**Custom DispatcherServlet configuration in Spring Boot:**

```java
// Override default DispatcherServlet behaviour
@Configuration
public class WebMvcConfig {

    @Bean
    public DispatcherServlet dispatcherServlet() {
        DispatcherServlet servlet = new DispatcherServlet();
        // Throw NoHandlerFoundException instead of responding 404 directly
        servlet.setThrowExceptionIfNoHandlerFound(true);
        // Allow @ExceptionHandler to handle 404 globally
        return servlet;
    }
}

// @ControllerAdvice to handle the 404 thrown by DispatcherServlet:
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NoHandlerFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(NoHandlerFoundException ex) {
        return new ErrorResponse("NOT_FOUND",
            "No handler for " + ex.getHttpMethod() + " " + ex.getRequestURL());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .collect(toList());
        return new ErrorResponse("VALIDATION_FAILED", errors.toString());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DispatcherServlet handles all exceptions automatically        | By default, `DispatcherServlet` sends a 500 status for unhandled exceptions. Global exception handling requires `@ControllerAdvice` + `@ExceptionHandler` methods. Without these, stack traces may appear in responses in development                                                       |
| Filters and Interceptors are the same thing                   | Filters are Servlet-level (outside `DispatcherServlet`) — they see the raw `HttpServletRequest`. Interceptors are Spring MVC-level (inside `DispatcherServlet`) — they have access to the resolved handler and model. Security filters (Spring Security) run before the `DispatcherServlet` |
| There is always exactly one DispatcherServlet per application | Spring Boot creates one by default, but you can configure multiple `DispatcherServlet` beans for different URL prefixes — for example, one for `/api/**` (REST) and one for `/admin/**` (Thymeleaf web UI)                                                                                  |
| The DispatcherServlet creates the Spring ApplicationContext   | In Spring Boot, the `SpringApplication` creates the `ApplicationContext` before the `DispatcherServlet` starts. The `DispatcherServlet` is a bean within that context, not the context creator                                                                                              |

---

### 🔥 Pitfalls in Production

**Static resource mapping conflicts — DispatcherServlet intercepts everything**

```java
// BAD: DispatcherServlet mapped to "/" intercepts static resource requests
// GET /static/app.js → DispatcherServlet → NoHandlerFoundException → 404

// GOOD: configure static resource handling
@Configuration
class WebConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/static/")
                .setCacheControl(CacheControl.maxAge(365, TimeUnit.DAYS));
    }
}
// OR in application.properties:
// spring.mvc.static-path-pattern=/static/**
// spring.web.resources.static-locations=classpath:/static/
```

---

### 🔗 Related Keywords

- `HandlerMapping` — the component within DispatcherServlet that maps URLs to controllers
- `Filter vs Interceptor` — Filter = Servlet level (before DS); Interceptor = MVC level (inside DS)
- `ApplicationContext` — the container from which DispatcherServlet retrieves all its collaborating beans
- `Spring Boot Startup Lifecycle` — DispatcherServlet is registered with embedded container during boot

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROLE         │ Front controller: single entry point      │
│              │ for all HTTP requests in Spring MVC       │
├──────────────┼───────────────────────────────────────────┤
│ PIPELINE     │ Filter → DS → HandlerMapping →            │
│              │ Interceptor.pre → HandlerAdapter →        │
│              │ Interceptor.post → ViewResolver/MsgConv  │
│              │ → Interceptor.afterCompletion             │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ Auto-configured, mapped to "/"            │
│              │ Embedded Tomcat registers it automatically │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "DispatcherServlet = airport ops centre:  │
│              │  all requests arrive here, get routed     │
│              │  to the right gate (controller)."        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The DispatcherServlet's `doDispatch()` method calls `HandlerExceptionResolver` only if an exception occurs during handler execution. But what if an exception occurs IN a `HandlerInterceptor.preHandle()` method? Trace the exact error handling path: does `HandlerExceptionResolver` still get called? Are `postHandle()` and `afterCompletion()` still called for interceptors that already ran `preHandle()` successfully? And what HTTP status code is returned if no `HandlerExceptionResolver` handles the exception from `preHandle()`?

**Q2.** In a Spring Boot REST application with `spring.mvc.throw-exception-if-no-handler-found=true` and `spring.mvc.static-path-pattern=/static/**`, describe what happens when a client requests `GET /favicon.ico`: (a) which component matches first — the static resource handler or the NoHandlerFoundException path, (b) what is the default Spring Boot behaviour for `/favicon.ico` requests (there is a specific `FaviconConfiguration`), and (c) how does `DefaultServletHttpRequestHandler` fit into this chain when `spring.mvc.default-servlet.enabled=true` is set?
