---
layout: default
title: "Filter vs Interceptor"
parent: "Spring & Spring Boot"
nav_order: 126
permalink: /spring/filter-vs-interceptor/
number: "126"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "Servlet API, DispatcherServlet, Spring MVC, HTTP"
used_by: "Authentication, CORS, Logging, Rate Limiting, Audit"
tags: #java, #spring, #springboot, #intermediate, #networking, #security
---

# 126 — Filter vs Interceptor

`#java` `#spring` `#springboot` `#intermediate` `#networking` `#security`

⚡ TL;DR — Filters run at the Servlet container level before DispatcherServlet touches the request; Interceptors run inside Spring MVC after DispatcherServlet, with access to the resolved handler.

| #126 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Servlet API, DispatcherServlet, Spring MVC, HTTP | |
| **Used by:** | Authentication, CORS, Logging, Rate Limiting, Audit | |

---

### 📘 Textbook Definition

A **Filter** is a `javax.servlet.Filter` (Jakarta in Spring 6) that intercepts HTTP requests and responses at the Servlet container layer — before `DispatcherServlet` is involved. Filters form a chain managed by the container; they can read/modify the raw `ServletRequest`/`ServletResponse`, short-circuit the request, or pass it along via `chain.doFilter()`. A **`HandlerInterceptor`** is a Spring MVC component registered with `DispatcherServlet` that runs after the handler (controller) has been resolved — it has access to the `HandlerMethod` (the specific `@RequestMapping` method), the `ModelAndView`, and exceptions. The key distinction: Filters are Servlet-specification infrastructure; Interceptors are Spring MVC-specific and Spring-context-aware.

---

### 🟢 Simple Definition (Easy)

A Filter is a bouncer at the building entrance — it sees every request before Spring does. An Interceptor is a greeter inside the building — it runs after Spring knows which room (controller) the visitor is going to.

---

### 🔵 Simple Definition (Elaborated)

Filters and Interceptors both let you add behaviour to HTTP request handling — but at different levels. Authentication is typically a Filter because it must reject requests before Spring even parses a body. Request tracing with method-level detail (e.g. which endpoint received request) is better as an Interceptor because Filters don't know which Spring controller handled the request. Filters can wrap the request/response streams (useful for logging bodies); Interceptors can access the resolved `HandlerMethod` and its annotations (useful for feature-flag or permission checks based on controller annotations).

---

### 🔩 First Principles Explanation

**Request processing layers:**

```
Embedded Tomcat receives HTTP request
        ↓
  ┌──────────────────────────────────────────┐
  │  FILTER CHAIN (Servlet container)        │
  │  CorsFilter → SecurityFilter →           │
  │  LoggingFilter → ...                     │
  │  Runs BEFORE DispatcherServlet           │
  │  No knowledge of Spring MVC handler      │
  └──────────────────────────────────────────┘
        ↓
  DispatcherServlet receives request
        ↓
  ┌──────────────────────────────────────────┐
  │  INTERCEPTOR CHAIN (Spring MVC)          │
  │  preHandle() → [controller] →            │
  │  postHandle() → afterCompletion()        │
  │  Runs INSIDE DispatcherServlet           │
  │  Has HandlerMethod, ModelAndView access  │
  └──────────────────────────────────────────┘
        ↓
  @RequestMapping method executes
```

**Capability comparison:**

```
┌──────────────────────────────────────────────────────┐
│  CAPABILITY            FILTER    INTERCEPTOR          │
├──────────────────────────────────────────────────────┤
│  Runs before DS        YES       NO                   │
│  Wrap request stream   YES       NO                   │
│  Access HandlerMethod  NO        YES                  │
│  Access ModelAndView   NO        YES (postHandle)     │
│  Short-circuit req     YES       YES (preHandle false)│
│  Spring bean injection YES*      YES (Spring context) │
│  Non-Spring requests   YES       NO                   │
│  Exception access      NO        YES (afterCompletion)│
└──────────────────────────────────────────────────────┘
* via GenericFilterBean or DelegatingFilterProxy
```

---

### ❓ Why Does This Exist (Why Before What)

**FILTER — why it must be before DispatcherServlet:**

```
Authentication must run before Spring parses
the request body (prevent resource consumption
on unauthenticated requests)

CORS preflight (OPTIONS) must return headers
before Spring MVC processes any route logic

Multipart/large body rejection must happen
before the body is read into memory by Spring

Static resources may bypass DS entirely
→ Filter covers all requests; Interceptors don't
```

**INTERCEPTOR — why it needs to be inside Spring:**

```
Access to resolved HandlerMethod:
  @RequiresPermission on controller method
  → read annotation from HandlerMethod
  → only known after HandlerMapping resolved

Access to @Controller exception context:
  Interceptor.afterCompletion(ex) receives the
  exception thrown by the handler

ModelAndView manipulation for all controllers:
  Inject common model attributes (user info)
  without modifying every controller
```

---

### 🧠 Mental Model / Analogy

> A Filter is like **customs and immigration at an airport's front door** — every passenger goes through it before entering the building, regardless of where they're flying. An Interceptor is like **gate agents at each departure gate** — they run after ticketing has identified which gate (controller) the passenger is going to, and they can check boarding pass details specific to that flight.

"Airport front door customs" = Filter (before DispatcherServlet)
"Knowing which gate" = Interceptor has HandlerMethod context
"Every passenger" = Filter sees all requests (incl non-Spring)
"Gate agents for that flight" = Interceptor for that specific handler
"Turning back at customs" = Filter returning 401 before request proceeds
"Turning back at gate" = Interceptor.preHandle() returning false

---

### ⚙️ How It Works (Mechanism)

**Implementing and registering a Filter:**

```java
// Option 1: @Component + implements Filter
@Component
@Order(1)  // lower = earlier in chain
public class RequestIdFilter extends OncePerRequestFilter {
  @Override
  protected void doFilterInternal(
      HttpServletRequest req,
      HttpServletResponse res,
      FilterChain chain) throws ServletException, IOException {
    String reqId = UUID.randomUUID().toString();
    res.setHeader("X-Request-Id", reqId);
    MDC.put("requestId", reqId);
    try {
      chain.doFilter(req, res); // continue chain
    } finally {
      MDC.remove("requestId"); // always clean up
    }
  }
}

// Option 2: FilterRegistrationBean for explicit control
@Bean
FilterRegistrationBean<RateLimitFilter> rateLimitFilter() {
  FilterRegistrationBean<RateLimitFilter> reg =
      new FilterRegistrationBean<>(new RateLimitFilter());
  reg.setUrlPatterns(List.of("/api/*"));  // scope to API
  reg.setOrder(2);
  return reg;
}
```

**Implementing and registering an Interceptor:**

```java
@Component
public class AuditInterceptor implements HandlerInterceptor {
  @Override
  public boolean preHandle(
      HttpServletRequest req,
      HttpServletResponse res,
      Object handler) {
    if (handler instanceof HandlerMethod hm) {
      // Access the actual @RequestMapping method
      RequiresAudit audit =
          hm.getMethodAnnotation(RequiresAudit.class);
      if (audit != null) {
        auditLog.start(req.getRequestURI(),
                       audit.level());
      }
    }
    return true; // true = continue; false = abort
  }

  @Override
  public void afterCompletion(
      HttpServletRequest req,
      HttpServletResponse res,
      Object handler,
      Exception ex) {
    auditLog.finish(ex != null ? "ERROR" : "OK");
  }
}

// Registration
@Configuration
public class MvcConfig implements WebMvcConfigurer {
  @Override
  public void addInterceptors(
      InterceptorRegistry registry) {
    registry.addInterceptor(auditInterceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/health");
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP Request
        ↓
  FILTER CHAIN  ← Servlet container level
  (OncePerRequestFilter, CorsFilter, SecurityFilter)
        ↓
  DISPATCHERSERVLET (124)
        ↓
  INTERCEPTOR CHAIN  ← Spring MVC level
  preHandle() × N
        ↓
  Handler/Controller executes
        ↓
  postHandle() × N (skipped on exception)
        ↓
  afterCompletion() × N (always)
        ↓
  FILTER CHAIN unwinds (reverse order)
        ↓
HTTP Response
```

---

### 💻 Code Example

**Example 1 — When to use Filter: Auth token extraction:**

```java
// AUTH must be a Filter — runs before body is read
@Component
public class JwtAuthFilter extends OncePerRequestFilter {
  private final JwtValidator validator;

  @Override
  protected void doFilterInternal(
      HttpServletRequest req,
      HttpServletResponse res,
      FilterChain chain) throws IOException, ServletException {
    String header = req.getHeader("Authorization");
    if (header != null && header.startsWith("Bearer ")) {
      String token = header.substring(7);
      try {
        Authentication auth = validator.validate(token);
        SecurityContextHolder.getContext()
            .setAuthentication(auth);
      } catch (JwtException e) {
        res.setStatus(HttpStatus.UNAUTHORIZED.value());
        return; // abort — no chain.doFilter()
      }
    }
    chain.doFilter(req, res);
  }
}
```

**Example 2 — When to use Interceptor: method annotation check:**

```java
// INTERCEPTOR — needs HandlerMethod to read @RateLimit
@Component
public class RateLimitInterceptor implements HandlerInterceptor {

  @Override
  public boolean preHandle(HttpServletRequest req,
      HttpServletResponse res, Object handler) throws Exception {
    if (!(handler instanceof HandlerMethod hm)) return true;

    RateLimit rl = hm.getMethodAnnotation(RateLimit.class);
    if (rl == null) return true;

    String clientIp = req.getRemoteAddr();
    if (!rateLimiter.tryAcquire(clientIp, rl.rpm())) {
      res.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
      return false; // abort request
    }
    return true;
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Filters and Interceptors are interchangeable | They operate at different layers. Filters cannot access HandlerMethod; Interceptors cannot intercept non-Spring requests (static resources bypassing DS) |
| Interceptors can wrap the request/response body | Interceptors receive HttpServletRequest directly — they cannot replace the body stream. ContentCachingRequestWrapper (used in a Filter) is required for body caching |
| Spring Security uses Interceptors for auth | Spring Security uses Filters (SecurityFilterChain), not Interceptors — it runs before DispatcherServlet, before the body is touched |
| `@Order` on Interceptors controls their order | @Order on Interceptor beans has no effect. Order is determined by the order of `registry.addInterceptor()` calls in `WebMvcConfigurer.addInterceptors()` |

---

### 🔥 Pitfalls in Production

**1. Reading request body in a Filter — leaves stream empty for Spring**

```java
// BAD: read body in Filter → stream exhausted → Spring gets empty body
@Override
protected void doFilterInternal(HttpServletRequest req, ...) {
  String body = new String(req.getInputStream().readAllBytes());
  log.info("Request body: {}", body);
  chain.doFilter(req, res); // Spring reads empty stream!
}

// GOOD: wrap in ContentCachingRequestWrapper first
ContentCachingRequestWrapper cachedReq =
    new ContentCachingRequestWrapper(req);
chain.doFilter(cachedReq, res);
// Read body AFTER chain.doFilter() — body cached
String body = new String(cachedReq.getContentAsByteArray());
```

**2. Interceptor registered but applying to wrong paths**

```java
// BAD: adds interceptor globally (all paths)
registry.addInterceptor(authInterceptor);
// Now /actuator/health requires auth → Kubernetes probe fails!

// GOOD: explicit path scope
registry.addInterceptor(authInterceptor)
        .addPathPatterns("/api/**")
        .excludePathPatterns("/api/public/**",
                             "/actuator/**");
```

---

### 🔗 Related Keywords

- `DispatcherServlet` — Interceptors are registered with DS; Filters are upstream of it
- `HandlerMapping` — Interceptors receive the resolved handler from HandlerMapping
- `Spring Security` — implemented as a Filter chain (SecurityFilterChain)
- `OncePerRequestFilter` — Spring's base Filter class guaranteeing single execution per request
- `WebMvcConfigurer` — the interface used to register Interceptors
- `CORS` — typically implemented as a Filter (CorsFilter) — must fire before Spring MVC

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Filter = Servlet-level (before DS);       │
│              │ Interceptor = Spring-level (inside DS);   │
│              │ Interceptor knows the resolved handler    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Filter: auth, CORS, body caching, rate    │
│              │ Interceptor: audit, method annotations    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Filter: don't access HandlerMethod        │
│              │ Interceptor: don't wrap body stream       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Filter is customs; Interceptor is the    │
│              │  gate agent who knows your flight."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Transactional (127) →                    │
│              │ Spring Security → DispatcherServlet (124) │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed tracing system needs to propagate a `X-Trace-Id` header from inbound HTTP requests to all outbound HTTP calls made by the application. The trace ID must be available to every service and repository called within the request. Explain whether this is better implemented as a Filter or an Interceptor — trace exactly how the ID is stored (MDC, ThreadLocal, Reactor Context?) and propagated to outbound calls — and describe the failure mode when `@Async` methods are used within the same request (hint: thread change breaks ThreadLocal propagation).

**Q2.** Spring Security's `SecurityFilterChain` operates inside the Servlet filter chain. It registers a single `DelegatingFilterProxy` that bridges the Servlet container world with the Spring ApplicationContext, allowing Security's filters to be Spring beans. Explain the exact problem this solves — why regular Spring beans cannot be directly registered as Servlet filters — and describe what `FilterChainProxy` (the bean that `DelegatingFilterProxy` delegates to) does with its list of `SecurityFilterChain` objects to decide which chain applies to which request.

