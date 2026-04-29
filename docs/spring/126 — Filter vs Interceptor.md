---
layout: default
title: "Filter vs Interceptor"
parent: "Spring Framework"
nav_order: 126
permalink: /spring/filter-vs-interceptor/
---
⚡ TL;DR — Filters (Servlet API) run before DispatcherServlet and can intercept any request; Interceptors (Spring MVC) run inside DispatcherServlet and have access to handler metadata.
## 📘 Textbook Definition
**Filter** is a Java Servlet API component (`javax.servlet.Filter`) that intercepts HTTP requests/responses before they reach any Servlet (including DispatcherServlet), operating at the web container level with access to raw request/response. **HandlerInterceptor** is a Spring MVC component that intercepts requests within the DispatcherServlet lifecycle — after handler resolution — providing pre-handle, post-handle, and after-completion hooks with access to the handler and ModelAndView.
## 🟢 Simple Definition (Easy)
Filter is a security guard at the building entrance — it sees everyone before they enter. Interceptor is the receptionist inside — it sees visitors after they're in the building and knows which meeting room (controller) they're heading to.
## 🔩 First Principles Explanation
```
HTTP Request
    ↓
[Filter Chain]  ← Servlet API — no Spring context, raw request/response
    ↓
DispatcherServlet
    ↓
[HandlerMapping] → finds handler
    ↓
[Interceptor.preHandle()] ← Spring context! knows handler, can access Spring beans
    ↓
Controller executed
    ↓
[Interceptor.postHandle()] ← sees ModelAndView (before View rendered)
    ↓
View rendered
    ↓
[Interceptor.afterCompletion()] ← always runs (like finally)
    ↑
[Filter Chain] exiting ← response passes back through filters
```
## 💻 Code Example
```java
// ── FILTER (Servlet level — authentication, CORS, logging) ───────────────────
@Component
public class RequestLoggingFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        long start = System.currentTimeMillis();
        chain.doFilter(req, res); // run the rest of the chain
        System.out.printf("%s %s — %dms%n", request.getMethod(), request.getRequestURI(),
                System.currentTimeMillis() - start);
    }
}
// ── INTERCEPTOR (Spring MVC level — auth check, audit, metrics) ──────────────
@Component
public class AuthInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res,
                             Object handler) throws Exception {
        if (handler instanceof HandlerMethod hm) {
            if (hm.hasMethodAnnotation(RequiresAuth.class)) {
                String token = req.getHeader("Authorization");
                if (!tokenService.validate(token)) {
                    res.sendError(401);
                    return false; // STOPS processing
                }
            }
        }
        return true; // continue
    }
    @Override
    public void afterCompletion(HttpServletRequest req, HttpServletResponse res,
                                Object handler, Exception ex) {
        MDC.clear(); // cleanup logging context
    }
}
// Register interceptor
@Configuration
public class MvcConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(authInterceptor).addPathPatterns("/api/**");
    }
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Filters and interceptors are the same | Different layers — filter=servlet, interceptor=Spring MVC |
| Interceptors can catch all requests | Interceptors only work for requests going through DispatcherServlet |
| Interceptors can access Spring Security context | Yes — unlike filters before Spring Security, interceptors run after security processing |
## 🔗 Related Keywords
- **[DispatcherServlet](./124 — DispatcherServlet.md)** — interceptors run inside DispatcherServlet
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — alternative for method-level cross-cutting concerns
## 📌 Quick Reference Card
```
+-------------+--------------------------+----------------------------+
|             | Filter                   | Interceptor                |
+-------------+--------------------------+----------------------------+
| Level       | Servlet container         | Spring MVC                 |
| Runs        | Before DispatcherServlet  | Inside DispatcherServlet   |
| Spring beans| Limited (CDI needed)      | Full Spring context        |
| Handler info| No                        | Yes (HandlerMethod access) |
| Use case    | CORS, auth, logging       | Audit, auth, rate limit    |
+-------------+--------------------------+----------------------------+
```
