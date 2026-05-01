---
layout: default
title: "Filter vs Interceptor"
parent: "Spring Core"
nav_order: 394
permalink: /spring/filter-vs-interceptor/
number: "394"
category: Spring Core
difficulty: ★★☆
depends_on: "DispatcherServlet, HandlerMapping, ApplicationContext"
used_by: "DispatcherServlet, Spring Security"
tags: #intermediate, #spring, #networking, #architecture, #security
---

# 394 — Filter vs Interceptor

`#intermediate` `#spring` `#networking` `#architecture` `#security`

⚡ TL;DR — **Filters** (Servlet API) run BEFORE the DispatcherServlet and see the raw request; **Interceptors** (Spring MVC) run INSIDE the DispatcherServlet and see the resolved handler. Use Filters for security, CORS, and encoding; use Interceptors for logging, auth checks, and request auditing that need Spring context access.

| #394            | Category: Spring Core                                 | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | DispatcherServlet, HandlerMapping, ApplicationContext |                 |
| **Used by:**    | DispatcherServlet, Spring Security                    |                 |

---

### 📘 Textbook Definition

**Filters** (`javax.servlet.Filter` / `jakarta.servlet.Filter`) are part of the Servlet specification and run in the Servlet container's filter chain — outside and before the Spring `DispatcherServlet`. Filters receive the raw `HttpServletRequest` and `HttpServletResponse`, can modify them, abort the chain, or wrap them. Filters are managed by the Servlet container (Tomcat) but can be Spring beans. They form a `FilterChain` where each filter calls `chain.doFilter()` to proceed. **HandlerInterceptors** (`org.springframework.web.servlet.HandlerInterceptor`) are a Spring MVC concept that runs inside the `DispatcherServlet` after the handler (controller) has been determined. They provide three hooks: `preHandle()` (before controller invocation), `postHandle()` (after controller, before view rendering), and `afterCompletion()` (always called, after complete response). Interceptors have access to the resolved `HandlerMethod` and the Spring `ModelAndView`. Spring Security is implemented as Filters (pre-DispatcherServlet), while Cross-Cutting concerns that need to know the controller being called (logging, rate limiting by controller) are typically Interceptors.

---

### 🟢 Simple Definition (Easy)

Filters are gatekeepers outside the Spring front door — they check requests before Spring even sees them. Interceptors are assistants inside Spring — they run after Spring has figured out which controller handles the request, giving you access to Spring context.

---

### 🔵 Simple Definition (Elaborated)

Imagine a building with a security checkpoint at the entrance (Filters) and a receptionist inside (Interceptors). Every visitor (request) must pass through security first — security does not know or care where the visitor is going. Once inside, the receptionist (Interceptor) greets them knowing exactly which office (controller) they are heading to and can make decisions based on that. Filters are the right place for security scanning (Spring Security), CORS headers, and character encoding because these should happen before any Spring processing. Interceptors are the right place for logging requests with the controller name, checking permissions based on which endpoint was called, and tracking response times per-endpoint.

---

### 🔩 First Principles Explanation

**Where in the request lifecycle each one runs:**

```
HTTP Request
        │
        ▼
Servlet Container (Tomcat)
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                    FILTER CHAIN                         │
│  Filter 1 (CorsFilter)  ─→  chain.doFilter()           │
│  Filter 2 (SecurityFilter) → chain.doFilter()          │
│  Filter 3 (CharacterEncodingFilter) → chain.doFilter() │
└─────────────────────────────────────────────────────────┘
        │
        ▼
DispatcherServlet.service(request, response)
        │
        ▼
HandlerMapping.getHandler() → resolves controller method
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                INTERCEPTOR CHAIN                        │
│  Interceptor1.preHandle(req, res, handler)              │
│  Interceptor2.preHandle(req, res, handler)              │
│         │ (if any returns false: stop here)             │
│         ▼                                               │
│  Controller method invoked                              │
│         │                                               │
│  Interceptor2.postHandle(req, res, handler, modelView)  │
│  Interceptor1.postHandle(req, res, handler, modelView)  │
│         │                                               │
│  View resolved / response body written                  │
│         │                                               │
│  Interceptor2.afterCompletion(req, res, handler, ex)    │
│  Interceptor1.afterCompletion(req, res, handler, ex)    │
└─────────────────────────────────────────────────────────┘
        │
        ▼
HTTP Response ← Servlet Container sends to client
```

**Key differences side by side:**

```
┌─────────────────────┬─────────────────────────────────┬──────────────────────────────────┐
│ Aspect              │ Filter                          │ HandlerInterceptor               │
├─────────────────────┼─────────────────────────────────┼──────────────────────────────────┤
│ Spec / Owner        │ Servlet API (container-managed) │ Spring MVC (DS-managed)          │
│ Position            │ Before DispatcherServlet        │ Inside DispatcherServlet         │
│ Knows handler?      │ No — raw request only           │ Yes — HandlerMethod available    │
│ Spring context?     │ Yes (if declared as @Bean)      │ Yes (always Spring-managed)      │
│ Spring DI?          │ Yes (FilterRegistrationBean)    │ Yes (autowired normally)         │
│ Hooks               │ doFilter() (before + after)     │ preHandle, postHandle, afterComp │
│ Can abort request?  │ Yes (don't call chain.doFilter) │ Yes (return false from preHandle)│
│ Can modify request? │ Yes (wrap HttpServletRequest)   │ Limited (no wrapping typically)  │
│ Handles all URLs?   │ Yes (configurable pattern)      │ Yes (configurable path pattern)  │
│ Use for:            │ Security, CORS, encoding, ZIP   │ Logging, auditing, rate limiting │
└─────────────────────┴─────────────────────────────────┴──────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT the two-layer system:

What breaks without it:

1. Spring Security's authentication/authorisation would need to be inside the DispatcherServlet — it could not intercept non-Spring requests (static files, actuator endpoints, error pages).
2. CORS headers must be added before the Servlet container processes the request — if done after, the browser's preflight response arrives too late.
3. Interceptors cannot be implemented inside Spring without access to the resolved handler — a `doFilter()` only sees URL patterns, not which Java method handles it.

WITH both layers:
→ Spring Security filters guarantee that unauthenticated requests never reach Spring MVC.
→ Character encoding filters ensure request body is read with correct encoding before any controller touches it.
→ Interceptors provide richer logging and auditing with controller class, method, and execution time.

---

### 🧠 Mental Model / Analogy

> Filters = airport security checkpoints. Every person (request) passes through them regardless of destination. The checkpoint officer does not care if you are heading to Gate A3 or the executive lounge — every person is screened. Interceptors = gate agents who know you specifically and which flight you are on. They verify your boarding pass (authentication token), check your specific seat (role for this endpoint), and note your arrival time for the flight manifest. If security (Filter) already rejected you, the gate agent (Interceptor) never sees you.

"Airport security" = Filters (Servlet-level, all requests, no routing knowledge)
"Your gate" = DispatcherServlet + HandlerMapping resolved the correct handler
"Gate agent with boarding pass" = HandlerInterceptor (has Handler and Spring context)
"Security rejected before gate" = SecurityFilter returning 401 before DispatcherServlet

---

### ⚙️ How It Works (Mechanism)

**Interceptor lifecycle with exception handling:**

```
preHandle:  Interceptor1 ✓  Interceptor2 ✓  Interceptor3 ✗ (returns false)
→ Chain STOPPED. postHandle NOT called for any interceptor.
→ afterCompletion called ONLY for Interceptor1 and Interceptor2 (those that ran preHandle).

preHandle:  Interceptor1 ✓  Interceptor2 ✓  Interceptor3 ✓
→ Controller throws RuntimeException
→ postHandle NOT called (skipped on exception)
→ afterCompletion called for ALL three (always runs, receives the exception)
→ HandlerExceptionResolver called to handle exception

preHandle: all ✓ → Controller returns OK → postHandle for all (reverse order)
→ Response written → afterCompletion for all (reverse order)
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP Request
        │
        ▼
Filter (Servlet layer)  ◄──── (you are here: left branch)
• CorsFilter (Spring Security)
• SecurityFilterChain (Spring Security)
• CharacterEncodingFilter
• CommonsRequestLoggingFilter
        │
        ▼
DispatcherServlet
        │
        ▼
HandlerInterceptor  ◄──── (you are here: right branch)
• LoggingInterceptor
• RateLimitInterceptor
• AuditInterceptor
        │
        ▼
@Controller method
```

---

### 💻 Code Example

**Filter vs Interceptor for request logging:**

```java
// FILTER approach: logs request timing at Servlet level
@Component
@Order(1)
class RequestTimingFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
        throws IOException, ServletException {

        HttpServletRequest request = (HttpServletRequest) req;
        long start = System.currentTimeMillis();
        String requestId = UUID.randomUUID().toString();

        MDC.put("requestId", requestId); // thread-local MDC for logging
        try {
            chain.doFilter(req, res); // MUST call to proceed
        } finally {
            long elapsed = System.currentTimeMillis() - start;
            log.info("Request {} {} completed in {}ms",
                request.getMethod(), request.getRequestURI(), elapsed);
            MDC.clear();
        }
    }
}

// INTERCEPTOR approach: logs with controller/method name
@Component
class ControllerAuditInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res,
                             Object handler) {
        if (handler instanceof HandlerMethod hm) {
            log.info("Calling {}.{} for {} {}",
                hm.getBeanType().getSimpleName(),
                hm.getMethod().getName(),
                req.getMethod(), req.getRequestURI());
        }
        return true; // return false to abort
    }

    @Override
    public void afterCompletion(HttpServletRequest req, HttpServletResponse res,
                                Object handler, Exception ex) {
        if (ex != null) {
            log.error("Request completed with exception", ex);
        }
    }
}

// Register the interceptor:
@Configuration
class WebConfig implements WebMvcConfigurer {
    @Autowired ControllerAuditInterceptor auditInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(auditInterceptor)
                .addPathPatterns("/api/**");
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Filters and Interceptors are interchangeable                    | They run at different levels. Filters run before Spring MVC and can intercept ALL requests (static files, error pages). Interceptors only run for requests handled by DispatcherServlet. Spring Security MUST be a Filter — a SecurityInterceptor would miss requests not routed through DispatcherServlet                         |
| You cannot use Spring beans in Filters                          | Filters can be Spring-managed beans if registered via `FilterRegistrationBean`. They support `@Autowired` and full Spring context access. Spring Boot auto-registers `@Component` `Filter` beans. The difference is that Filters are created by the Servlet container lifecycle, but Spring's `DelegatingFilterProxy` bridges them |
| `postHandle()` is always called after controller execution      | `postHandle()` is NOT called if the controller throws an exception — the exception propagates to `HandlerExceptionResolver`. `afterCompletion()` is always called (like `finally`) and receives the exception as a parameter. Cleanup logic belongs in `afterCompletion()`, not `postHandle()`                                     |
| Interceptors execute in declaration order for both pre and post | `preHandle()` executes in the order interceptors were registered. `postHandle()` and `afterCompletion()` execute in REVERSE order. If interceptors form a stack, the last-in is first-out for post-processing                                                                                                                      |

---

### 🔥 Pitfalls in Production

**Spring Security in an Interceptor does NOT protect static resources**

```java
// WRONG: Attempting to do security in a HandlerInterceptor
@Component
class SecurityInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object h) {
        // This ONLY runs for requests reaching DispatcherServlet
        // Static files (/css/**, /js/**), error pages → NEVER see this interceptor
        String token = req.getHeader("Authorization");
        if (token == null) {
            res.setStatus(401);
            return false;
        }
        return true;
    }
}
// WRONG: Static files are accessible without any auth check!

// CORRECT: Security MUST be a Filter (Spring Security handles this automatically)
// spring.security.filter.order configures where SecurityFilterChain runs
```

---

### 🔗 Related Keywords

- `DispatcherServlet` — filters run before DS; interceptors run inside DS as part of handler execution
- `HandlerMapping` — HandlerInterceptors are attached to HandlerMappings and returned in HandlerExecutionChain
- `Spring Security` — implemented entirely as Filters (before DispatcherServlet)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│              │ FILTER              │ INTERCEPTOR          │
├──────────────┼─────────────────────┼──────────────────────┤
│ Layer        │ Servlet (before DS) │ Spring MVC (in DS)   │
│ Spec         │ javax.servlet       │ Spring Framework     │
│ Knows handler│ NO                  │ YES (HandlerMethod)  │
│ All URLs?    │ YES                 │ Only via DispatcherS │
│ Use for      │ Security, CORS, enc │ Logging, audit, rate │
├──────────────┴─────────────────────┴──────────────────────┤
│ INTERCEPTOR HOOKS:                                        │
│ preHandle()    → before controller (can abort)           │
│ postHandle()   → after controller (skipped on exception) │
│ afterCompletion→ always (cleanup, exception access)      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Security uses a `FilterChain` with multiple ordered filters (`UsernamePasswordAuthenticationFilter`, `BearerTokenAuthenticationFilter`, `ExceptionTranslationFilter`, etc.). Explain why the order of these filters matters critically: what goes wrong if `ExceptionTranslationFilter` runs BEFORE `UsernamePasswordAuthenticationFilter`? Then explain what `DelegatingFilterProxy` is and why it is needed to bridge between the Servlet container's filter lifecycle and the Spring ApplicationContext (hint: the Servlet container creates filters before the Spring context is fully initialised).

**Q2.** `HandlerInterceptor.afterCompletion()` receives an `Exception` parameter. If a controller throws `RuntimeException`, `HandlerExceptionResolver` processes it (converts it to a 400/500 response), and THEN `afterCompletion()` is called with the original exception. However, by the time `afterCompletion()` runs, the response has already been committed by `HandlerExceptionResolver`. Describe the implications of a committed response: can the interceptor change the response status? Can it add headers? What happens if `afterCompletion()` also throws an exception? Trace the exact exception propagation path.
