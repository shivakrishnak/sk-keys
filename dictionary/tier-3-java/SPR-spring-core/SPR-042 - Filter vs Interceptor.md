---
version: 1
layout: default
title: "Filter vs Interceptor"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /spring/filter-vs-interceptor/
id: SPR-042
category: Spring Core
difficulty: ★★☆
depends_on: DispatcherServlet, HandlerMapping, Bean
used_by: Spring Security, CORS, Logging, Authentication, Request Throttling
related: DispatcherServlet, HandlerMapping, AOP, OncePerRequestFilter, HandlerInterceptorAdapter
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - webdev
---

# SPR-042 - Filter vs Interceptor

⚡ TL;DR - Servlet **Filters** sit outside DispatcherServlet (raw byte-level, any servlet), while Spring **HandlerInterceptors** sit inside DispatcherServlet (post-routing, Spring-aware) - choose Filter for security/encoding/CORS; choose Interceptor for logging, auth checks that need Spring beans.

| #394            | Category: Spring Core                                                                   | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | DispatcherServlet, HandlerMapping, Bean                                                 |                 |
| **Used by:**    | Spring Security, CORS, Logging, Authentication, Request Throttling                      |                 |
| **Related:**    | DispatcherServlet, HandlerMapping, AOP, OncePerRequestFilter, HandlerInterceptorAdapter |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to: (a) reject unauthenticated requests before they reach any controller, (b) log the handler method name after routing, (c) add CORS headers to every response. Which mechanism handles each? Using the wrong mechanism (e.g., trying to access `HandlerMethod` details from a Servlet Filter) is impossible - the filter runs before routing, so the handler isn't known yet.

**THE INVENTION MOMENT:**
"Filter and Interceptor each have a specific position in the request lifecycle - understanding that position determines which one to use."

---

### 📘 Textbook Definition

A **Servlet Filter** (`javax.servlet.Filter` / `jakarta.servlet.Filter`) is a Java EE/Jakarta EE component that intercepts HTTP requests and responses at the Servlet container level - before any Servlet (including `DispatcherServlet`) processes the request. Filters operate at the byte/stream level and have access to the raw `HttpServletRequest` and `HttpServletResponse`. A **Spring HandlerInterceptor** (`org.springframework.web.servlet.HandlerInterceptor`) is a Spring MVC component that intercepts request processing INSIDE `DispatcherServlet`, after the handler (controller method) has been determined. It has access to the handler (the `@Controller` method reference) and the `ModelAndView`. Three phases: `preHandle()` (before handler - can abort), `postHandle()` (after handler, before view - has ModelAndView), `afterCompletion()` (after view/response, always - for cleanup).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Filter = outermost ring (pre-Servlet); Interceptor = inner ring (inside Spring MVC, post-routing).

**One analogy:**

> A courthouse. The metal detector at the entrance (Servlet Filter) checks everyone before they enter the building - it doesn't know what courtroom they're going to. The bailiff inside the courtroom (HandlerInterceptor) checks everyone entering Judge Smith's room - they know exactly which judge and case is involved. The metal detector handles security for the whole building; the bailiff handles room-specific protocol.

**One insight:**
The key question when choosing: "Do I need to know which handler (controller method) will handle this request?" If YES → Interceptor (the handler is known). If NO → Filter (the handler is unknown at this point).

---

### 🔩 First Principles Explanation

**LIFECYCLE POSITIONS:**

```
HTTP Request
    ↓
Filter 1 (doFilter before)
    ↓
Filter 2 (doFilter before)
    ↓
DispatcherServlet entry
    HandlerMapping: determine handler ← Interceptor gains handler knowledge HERE
    ↓
    HandlerInterceptor.preHandle(request, response, handler)
    ↓
    HandlerAdapter: invoke handler method
    ↓
    HandlerInterceptor.postHandle(request, response, handler, modelAndView)
    ↓
    ViewResolver / MessageConverter: render response
    ↓
    HandlerInterceptor.afterCompletion(request, response, handler, exception)
DispatcherServlet exit
    ↓
Filter 2 (doFilter after)
    ↓
Filter 1 (doFilter after)
    ↓
HTTP Response
```

**KEY DIFFERENCES:**

| Feature                   | Servlet Filter                             | HandlerInterceptor                           |
| ------------------------- | ------------------------------------------ | -------------------------------------------- |
| Level                     | Servlet container (pre-Spring)             | Spring MVC (inside DispatcherServlet)        |
| Handler knowledge         | No                                         | Yes (has `Object handler` / `HandlerMethod`) |
| Applies to                | ALL servlets, ALL URLs                     | Only requests through DispatcherServlet      |
| Spring bean access        | Must use WebApplicationContextUtils        | Direct injection (@Autowired)                |
| Call order                | Outermost                                  | Between Filter and Handler                   |
| Filter chain continuation | `chain.doFilter()` - mandatory to continue | Return `true` from `preHandle()` to continue |

---

### 🧪 Thought Experiment

**SETUP:**
Three requirements:

1. Add `X-Request-ID` header to every request/response
2. Log which controller method handled the request
3. Check JWT token before ANY processing

**ANALYSIS:**

1. `X-Request-ID` header: no handler knowledge needed → **Filter** (applies before any Servlet)
2. Log controller method name: needs handler name (only available after HandlerMapping) → **Interceptor**
3. JWT token check: must run before any processing, on all endpoints → **Filter** (Spring Security uses this)

**THE INSIGHT:**
Requirements 1 and 3 run before routing - they can't know the handler. Requirement 2 runs after routing - it CAN know the handler. Using an Interceptor for requirement 3 is technically possible but runs AFTER the JWT could have already been checked by Spring Security's filter chain - potentially with security gaps.

---

### 🧠 Mental Model / Analogy

> Filter is border control; Interceptor is customs within the destination country. Border control (Filter) checks documents for everyone crossing the border - they don't know where in the country the visitor is headed. Once inside the country, customs (Interceptor) at specific destinations checks what you're bringing to that specific place. Border control is independent of destination; customs is destination-specific.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Filters run before Spring even sees the request. Interceptors run inside Spring after it figures out which controller method to call. Use Filters for "block this before it gets to Spring." Use Interceptors for "do something knowing which endpoint was called."

**Level 2 - How to use it (junior developer):**
**Filter:** Implement `javax.servlet.Filter` (or extend `OncePerRequestFilter` to guarantee once-per-request) and annotate with `@Component` or register via `FilterRegistrationBean`.
**Interceptor:** Implement `HandlerInterceptor` (or extend `HandlerInterceptorAdapter`) and register via `WebMvcConfigurer.addInterceptors()`. Use `@Autowired` freely - it's a Spring bean.

**Level 3 - How it works (mid-level engineer):**
Filters are managed by the Servlet container (Tomcat/Jetty). `FilterChain.doFilter()` passes control to the next filter or the target servlet. Spring's `DelegatingFilterProxy` bridges the Servlet container's filter chain with Spring's ApplicationContext - allowing Spring beans to act as filters (Spring Security's `SecurityFilterChain` uses this). Interceptors are managed by Spring MVC: `HandlerExecutionChain.applyPreHandle()` iterates interceptors in order; if any returns `false`, `triggerAfterCompletion()` is called for already-run interceptors and the chain aborts.

**Level 4 - Why it was designed this way (senior/staff):**
Filters were the original Java EE mechanism - predating Spring MVC. Spring Interceptors were added to give Spring-aware pre/post processing that filters couldn't provide (access to the handler, the ModelAndView, Spring beans). Spring Security was designed as a Filter chain (not interceptors) for two critical reasons: (1) Filters run before DispatcherServlet - security must be able to reject requests before any Spring code runs; (2) Filters are portable across all Servlets, not just DispatcherServlet - a Spring Boot app might have multiple Servlets (e.g., an Actuator servlet). The `DelegatingFilterProxy` pattern (Servlet filter delegates to Spring bean) was the elegant solution: registered with the container as a raw Filter, but delegates to a full Spring bean (`springSecurityFilterChain`) that has access to the ApplicationContext.

---

### ⚙️ How It Works (Mechanism)

**Filter lifecycle:**

```java
public interface Filter {
    void init(FilterConfig config) throws ServletException;
    void doFilter(ServletRequest req, ServletResponse res,
                  FilterChain chain) throws IOException, ServletException;
    void destroy();
}

// Pattern:
public class RequestIdFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res,
                         FilterChain chain) throws Exception {
        String requestId = UUID.randomUUID().toString();
        ((HttpServletRequest) req).setAttribute("REQUEST_ID", requestId);
        res.setHeader("X-Request-ID", requestId);  // response header
        chain.doFilter(req, res);  // MUST call to continue chain
        // After chain: request has been fully processed
    }
}
```

**Interceptor lifecycle:**

```java
public interface HandlerInterceptor {
    // Before handler: return false to abort
    boolean preHandle(HttpServletRequest req, HttpServletResponse res,
                      Object handler) throws Exception;

    // After handler, before view (has ModelAndView)
    void postHandle(HttpServletRequest req, HttpServletResponse res,
                    Object handler, ModelAndView mv) throws Exception;

    // Always after (like finally) - even if exception
    void afterCompletion(HttpServletRequest req, HttpServletResponse res,
                         Object handler, Exception ex) throws Exception;
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**POST /users flow with Filter and Interceptor:**

```
POST /users (JWT token in header)
    ↓
JwtAuthFilter.doFilter():  ← Servlet Filter
  validate JWT
  set SecurityContext
  chain.doFilter()
    ↓
DispatcherServlet.doDispatch()
    ↓
HandlerMapping: POST /users → UserController.createUser()
    ↓
LoggingInterceptor.preHandle(): ← HandlerInterceptor
  log("POST /users → UserController.createUser")
  return true  ← continue
    ↓ ← YOU ARE HERE (Filter and Interceptor both applied)
UserController.createUser(body) executes
    ↓
LoggingInterceptor.postHandle():
  log("createUser returned 201")
    ↓
JSON response written
    ↓
LoggingInterceptor.afterCompletion():
  log("request complete: 201ms")
    ↓
JwtAuthFilter.doFilter() continues after chain.doFilter()
  (any cleanup)
    ↓
HTTP 201 Created
```

---

### 💻 Code Example

**Example 1 - OncePerRequestFilter for request ID:**

```java
@Component
@Order(1)
public class RequestIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws IOException, ServletException {
        String requestId = Optional
            .ofNullable(request.getHeader("X-Request-ID"))
            .orElse(UUID.randomUUID().toString());

        MDC.put("requestId", requestId);  // for logging
        response.setHeader("X-Request-ID", requestId);

        try {
            chain.doFilterInternal(request, response);
        } finally {
            MDC.remove("requestId");  // cleanup
        }
    }
}
```

**Example 2 - HandlerInterceptor for execution logging:**

```java
@Component
public class ExecutionLoggingInterceptor implements HandlerInterceptor {

    private static final String START_TIME = "startTime";

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) {
        request.setAttribute(START_TIME, System.currentTimeMillis());
        if (handler instanceof HandlerMethod hm) {
            log.debug("→ {}.{}",
                hm.getBeanType().getSimpleName(),
                hm.getMethod().getName());
        }
        return true;  // continue processing
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler, Exception ex) {
        Long start = (Long) request.getAttribute(START_TIME);
        if (start != null) {
            long ms = System.currentTimeMillis() - start;
            log.debug("← {} {} {}ms",
                request.getMethod(), request.getRequestURI(), ms);
        }
    }
}
```

**Example 3 - Registering Interceptor with URL pattern:**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired ExecutionLoggingInterceptor loggingInterceptor;
    @Autowired AdminAuthInterceptor adminInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loggingInterceptor)
                .addPathPatterns("/api/**");

        registry.addInterceptor(adminInterceptor)
                .addPathPatterns("/admin/**")
                .excludePathPatterns("/admin/health");
    }
}
```

---

### ⚖️ Comparison Table

| Feature               | Filter                            | HandlerInterceptor                     |
| --------------------- | --------------------------------- | -------------------------------------- |
| Position              | Before DispatcherServlet          | Inside DispatcherServlet               |
| Handler knowledge     | No                                | Yes (HandlerMethod)                    |
| Spring bean injection | Via DelegatingFilterProxy         | Direct @Autowired                      |
| Applies to            | All Servlets                      | Only DispatcherServlet-routed requests |
| Abort request         | Don't call chain.doFilter()       | Return false from preHandle()          |
| Use for               | Security, encoding, CORS, logging | Controller-aware pre/post processing   |

**Decision matrix:**

- Security (auth/authz): **Filter** (Spring Security standard)
- CORS: **Filter** or Spring MVC CORS config
- Request ID / MDC: **Filter** (needs to wrap entire call)
- Logging with handler method name: **Interceptor**
- Cache-Control headers: **Interceptor** (can inspect handler annotations)
- Request body reading/modification: **Filter** (via HttpServletRequestWrapper)

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Interceptors are "better" filters                                  | They're for different positions in the lifecycle. Neither is universally better.                                                                                                                                                                                    |
| Both run on every request                                          | Filter runs on requests matching its URL pattern (all by default). Interceptor runs ONLY on requests that go through DispatcherServlet - static resources served by Tomcat directly don't go through Interceptors.                                                  |
| afterCompletion() is like postHandle() - both run after the method | postHandle() runs after the handler METHOD but before view rendering. afterCompletion() runs after view rendering (and even if an exception occurred).                                                                                                              |
| Filters can inject @Autowired Spring beans                         | Standard filters can't inject @Autowired because the Servlet container creates them, not Spring. Use @Component + `FilterRegistrationBean` to make the filter a Spring bean, OR use DelegatingFilterProxy. Spring Boot's @Component auto-registration handles this. |

---

### 🚨 Failure Modes & Diagnosis

**Interceptor not running for static resources**

**Symptom:** Logging interceptor doesn't run for requests to `/static/style.css`.

**Root Cause:** Static resources bypass DispatcherServlet entirely (served directly by Tomcat's DefaultServlet). Interceptors only run inside DispatcherServlet.

**Fix:** Use a Servlet Filter for true cross-cutting concerns on static resources.

---

**Filter running multiple times per request**

**Symptom:** Request ID generated twice; filter body logged twice.

**Root Cause:** Using `javax.servlet.Filter` directly - can run multiple times for forwarded requests. Spring's `OncePerRequestFilter` prevents this.

**Fix:**

```java
// Use OncePerRequestFilter instead of Filter:
public class MyFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(...) { ... }  // runs exactly once
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `DispatcherServlet` - Interceptors live inside it; Filters are outside it

**Builds On This (learn these next):**

- `@Transactional` - transactions are often opened in Filters or Interceptors for request-scoped tx
- `Spring Security` - implemented entirely as Servlet Filters (FilterSecurityInterceptor is a filter)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FILTER        │ Servlet container level. Before/after    │
│               │ DispatcherServlet. No handler knowledge. │
│               │ Security, CORS, encoding, MDC.           │
├───────────────┼──────────────────────────────────────────┤
│ INTERCEPTOR   │ Inside DispatcherServlet. Post-routing.  │
│               │ Has handler (HandlerMethod). Spring bean │
│               │ injection. Controller-aware logging.     │
├───────────────┼──────────────────────────────────────────┤
│ KEY QUESTION  │ "Do I need handler (controller) info?"   │
│               │ YES → Interceptor. NO → Filter.          │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "Filter = border control.                 │
│               │  Interceptor = courtroom bailiff."       │
└───────────────┴──────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Security's `FilterSecurityInterceptor` (and its modern replacement `AuthorizationFilter`) runs as a Servlet Filter. But it needs to know the handler method (to check method-level security annotations like `@PreAuthorize`). How does Spring Security, running as a Filter (which has no handler knowledge), manage to check method-level security annotations? What mechanism gives it this capability without being an Interceptor?

**Q2.** A Filter registers with the Servlet container, but Spring Boot's `@Component` filter registration makes it a Spring bean. If a Filter is a Spring bean AND registered as a filter, does it get Spring AOP applied to its `doFilter()` method? Could a Filter's `doFilter()` be `@Transactional`? What would happen if it were?
