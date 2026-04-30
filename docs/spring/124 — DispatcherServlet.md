---
layout: default
title: "DispatcherServlet"
parent: "Spring Framework"
nav_order: 124
permalink: /spring/dispatcherservlet/
number: "124"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: Servlet API, ApplicationContext
used_by: HandlerMapping, Spring MVC, Filter vs Interceptor
tags: #spring, #networking, #internals, #intermediate
---

# 124 — DispatcherServlet

`#spring` `#networking` `#internals` `#intermediate`

⚡ TL;DR — DispatcherServlet is Spring MVC's front controller — it receives all HTTP requests and orchestrates routing to handlers, view resolution, and response rendering.

| #124 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Servlet API, ApplicationContext | |
| **Used by:** | HandlerMapping, Spring MVC, Filter vs Interceptor | |

---

### 📘 Textbook Definition
`DispatcherServlet` is the central `Servlet` of the Spring Web MVC framework. It acts as a **Front Controller**, delegating HTTP requests to Spring-configured handler components (controllers) via `HandlerMapping`, executing handler methods, resolving views via `ViewResolver`, and handling exceptions via `HandlerExceptionResolver`. In Spring Boot, it is auto-configured and registered automatically.
### 🟢 Simple Definition (Easy)
DispatcherServlet is the single "receptionist" of all HTTP requests. Every request comes to it, and it decides who handles it (which @Controller), waits for the result, and sends the response back.
### 🔵 Simple Definition (Elaborated)
Rather than having each URL mapped to a separate servlet (as in early Java EE), Spring MVC uses a single DispatcherServlet mapped to `"/"`. When a request arrives, DispatcherServlet consults `HandlerMapping` (which @RequestMapping handles this URL?), invokes the handler, resolves the return type (JSON via `HttpMessageConverter`, Thymeleaf template via `ViewResolver`, etc.), and writes the response.
### 🔩 First Principles Explanation
**Front Controller pattern:**
```
All requests → DispatcherServlet → route to correct handler
           ↑ single entry point for all HTTP traffic
Benefits:
- Centralized pre/post processing (filters, interceptors)
- Single place for cross-cutting concerns
- Decoupled controllers from request routing
```
**DispatcherServlet internal flow:**
```
HTTP Request
     ↓
DispatcherServlet.doDispatch()
     ↓
HandlerMapping → finds handler (Controller + method)
     ↓
HandlerAdapter → adapts and invokes the handler method
     ↓
Handler executes → returns ModelAndView or ResponseBody
     ↓
ViewResolver (if ModelAndView) → resolves template name to View
     ↓
View.render() → writes HTML / HttpMessageConverter writes JSON
     ↓
HTTP Response
```
### 💻 Code Example
```java
// Spring Boot — DispatcherServlet registered automatically
@SpringBootApplication  // registers DispatcherServlet on "/"
public class App { public static void main(String[] a) { SpringApplication.run(App.class, a); } }
// Your controllers are automatically picked up
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    @GetMapping("/{id}")
    public Order getOrder(@PathVariable Long id) { return orderService.findById(id); }
}
// Internally: DispatcherServlet → RequestMappingHandlerMapping finds OrderController.getOrder()
//             → RequestMappingHandlerAdapter invokes it
//             → MappingJackson2HttpMessageConverter converts Order → JSON response
// Advanced: multiple DispatcherServlets (rare, for different URL namespaces)
@Configuration
public class WebConfig {
    @Bean
    public ServletRegistrationBean<DispatcherServlet> adminServlet() {
        DispatcherServlet ds = new DispatcherServlet(adminContext);
        return new ServletRegistrationBean<>(ds, "/admin/*");
    }
}
```
### ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| DispatcherServlet is Spring Boot specific | It's Spring MVC (since Spring 2.0); Boot just auto-configures it |
| One DispatcherServlet per controller | One DispatcherServlet handles ALL controllers |
| DispatcherServlet processes filters | Filters run before DispatcherServlet; interceptors run inside it |
### 🔗 Related Keywords
- **[HandlerMapping](./125 — HandlerMapping.md)** — maps requests to handlers
- **[Filter vs Interceptor](./126 — Filter vs Interceptor.md)** — where in the pipeline they execute
- **[Auto-Configuration](./133 — Auto-Configuration.md)** — how Boot registers DispatcherServlet
### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Front Controller — single entry point for HTTP      |
+------------------------------------------------------------------+
| REGISTERS   | In Spring Boot: auto on "/" via DispatcherServletAutoConfiguration |
+------------------------------------------------------------------+
| PIPELINE    | HandlerMapping → HandlerAdapter → ViewResolver       |
+------------------------------------------------------------------+
| ONE-LINER   | "The traffic cop routing all HTTP requests"           |
+------------------------------------------------------------------+
```
### 🧠 Think About This Before We Continue
**Q1.** What is the difference between a `Filter` (javax.servlet) and a Spring `HandlerInterceptor`? At what point in the request lifecycle does each run relative to DispatcherServlet?
**Q2.** How does `DispatcherServlet` handle exceptions thrown from a `@Controller`? What components are involved?
**Q3.** In a Spring Boot app, what happens if you map a `@Controller` to `"/"` AND `DispatcherServlet` is also on `"/"`?
