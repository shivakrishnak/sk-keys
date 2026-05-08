---
layout: default
title: "Java Servlet"
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /java/java-servlet/
id: JLG-008
category: Java & JVM Internals
difficulty: ★★☆
depends_on: HTTP & APIs, Java EE / J2EE Overview, Thread (Java)
used_by: JSP (Java Server Pages), Spring Core, Java EE / J2EE Overview
related: HTTP Methods, DispatcherServlet, Filter vs Interceptor
tags:
  - java
  - jvm
  - networking
  - intermediate
---

# JLG-008 — Java Servlet

⚡ TL;DR — A Servlet is a Java class that handles HTTP requests and produces responses, running inside a servlet container like Tomcat.

| #2102 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP & APIs, Java EE / J2EE Overview, Thread (Java) | |
| **Used by:** | JSP (Java Server Pages), Spring Core, Java EE / J2EE Overview | |
| **Related:** | HTTP Methods, DispatcherServlet, Filter vs Interceptor | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
To handle HTTP in Java before Servlets, developers wrote raw TCP socket code: open a `ServerSocket`, read bytes, parse HTTP headers manually, write response bytes. Any framework was vendor-specific. Deploying to a different server meant rewriting the HTTP-handling layer.

**THE BREAKING POINT:**
Every Java web framework reinvented HTTP parsing, threading, connection management, and session tracking. None was portable across servers.

**THE INVENTION MOMENT:**
The Servlet specification (1997) defined a standard Java API for HTTP request/response handling. Any compliant container (Tomcat, Jetty, WildFly) manages threads, parses HTTP, and calls your `doGet()`/`doPost()` methods. You write business logic; the container handles HTTP plumbing.

---

### 📘 Textbook Definition

A Java Servlet is a server-side component that extends `HttpServlet` and overrides HTTP-method-specific handlers (`doGet`, `doPost`, `doPut`, `doDelete`). The servlet container manages the servlet lifecycle: `init()` (one-time setup), `service()` (per-request dispatch to method handlers), and `destroy()` (cleanup on undeploy). Servlets are thread-safe by the contract that `doGet()` may be called concurrently — no instance state should be mutable without synchronisation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Java class with `doGet()`/`doPost()` methods that a web container calls when an HTTP request arrives.

**One analogy:**
> A Servlet is like a hotel concierge. Guests (HTTP requests) arrive and ask for things. The concierge (Servlet) handles each request type: "I need a room" (`doPost`) or "What's available?" (`doGet`). The hotel reception desk (container) manages check-in logistics, room keys (sessions), and staff rotas (thread pools).

**One insight:**
Spring's `DispatcherServlet` is itself a Servlet — the entire Spring MVC framework is built on one Servlet that delegates to controllers. Understanding Servlet lifecycle explains why Spring beans created in `DispatcherServlet` scope work the way they do.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Servlet instances are shared across requests — never store mutable per-request state in instance fields.
2. The container owns the thread pool — `service()` is called concurrently on the same instance.
3. Lifecycle is: `init()` → N × `service()` → `destroy()`.

**DERIVED DESIGN:**
Because servlets are shared, all per-request data must live in method parameters (`HttpServletRequest`, `HttpServletResponse`) or thread-local storage (`HttpSession` is per-user, not per-thread, so must be accessed carefully).

**THE TRADE-OFFS:**
**Gain:** Container manages HTTP, threading, sessions, and SSL termination; developer writes pure Java logic.
**Cost:** Servlets are stateful singletons — concurrency bugs are easy to introduce with mutable fields.

---

### 🧪 Thought Experiment

**SETUP:**
You add a field `private int requestCount = 0;` to your Servlet and increment it in `doGet()`.

**WHAT HAPPENS:**
Under concurrent load, multiple threads increment the same field simultaneously without synchronisation — classic race condition. `requestCount` will be wrong. The JVM may cache the value in a CPU register and never flush it to main memory.

**THE INSIGHT:**
Servlet's shared-instance model makes this a very common beginner bug. Using `AtomicInteger` or removing mutable fields entirely is the correct pattern.

---

### 🧠 Mental Model / Analogy

> A Servlet is like a chef in a restaurant who handles all table orders simultaneously. The chef (Servlet) is one person; the orders (requests) come in concurrently. The chef must not confuse ingredients for different tables — each order's specifics must stay on the order ticket (request object), not in the chef's head (instance fields).

- "Chef" → Servlet instance (one per container)
- "Order ticket" → `HttpServletRequest` (per request)
- "Response plate" → `HttpServletResponse`
- "Table's session" → `HttpSession`
- "Kitchen manager" → Servlet container (Tomcat)

Where this analogy breaks down: a real chef handles one order at a time; a Servlet handles them concurrently on multiple threads.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Servlet is a Java program that responds to web requests. When someone visits a URL on your server, the servlet reads what they asked for and sends back a response.

**Level 2 — How to use it (junior developer):**
Extend `HttpServlet`, annotate with `@WebServlet("/path")`, override `doGet()` or `doPost()`. Use `req.getParameter("name")` to read form data. Use `resp.getWriter().write("Hello")` or `req.getRequestDispatcher("/view.jsp").forward(req, resp)` to send a response.

**Level 3 — How it works (mid-level engineer):**
The container maps URL patterns to Servlet classes via `@WebServlet` or `web.xml`. On first request, it instantiates the class (one instance) and calls `init(ServletConfig)`. Per request, it takes a thread from the pool and calls `service(req, resp)`, which dispatches to `doGet()`, `doPost()`, etc. based on the HTTP method.

**Level 4 — Why it was designed this way (senior/staff):**
The single-instance model maximises memory efficiency — one object handles thousands of concurrent requests. This trades memory for the risk of concurrency bugs. The alternative (one instance per request) was used by CGI, which forked a new process per request — catastrophically expensive. Servlet's pooled-thread + single-instance model was the right trade-off for late-1990s hardware constraints.

---

### ⚙️ How It Works (Mechanism)

```
HTTP Request: GET /products
         │
         ▼
┌─────────────────────────┐
│  Servlet Container      │
│  URL → Servlet mapping  │
│  Assign thread from pool│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  ProductServlet         │
│  doGet(req, res)        │
│  ├─ req.getParameter()  │
│  ├─ call service layer  │
│  ├─ req.setAttribute()  │
│  └─ forward to JSP      │
└────────────┬────────────┘
             │
             ▼
      JSP renders HTML
      → HTTP Response
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
`Browser → HTTP GET → Container thread pool → Servlet.doGet() → business logic → forward to JSP/JSON response → HTTP 200` ← YOU ARE HERE

**FAILURE PATH:**
Unhandled exception in `doGet()` → container catches it → wraps in HTTP 500 → sends error page. Session expired → `HttpSession` returns `null` on `getSession(false)`.

**WHAT CHANGES AT SCALE:**
Under high load, the container's thread pool exhausts → requests queue → response time climbs → queue fills → HTTP 503. Solution: async Servlet (`asyncContext.start()`) or reactive programming with non-blocking I/O (Netty/Spring WebFlux).

---

### 💻 Code Example

**BAD — Mutable instance state:**
```java
@WebServlet("/counter")
public class CounterServlet extends HttpServlet {
    private int count = 0; // SHARED across all requests!

    protected void doGet(HttpServletRequest req,
                         HttpServletResponse res) throws IOException {
        count++; // Race condition under concurrency
        res.getWriter().write("Count: " + count);
    }
}
```

**GOOD — Stateless Servlet with request-scoped data:**
```java
@WebServlet("/products")
public class ProductServlet extends HttpServlet {

    @Override
    public void init(ServletConfig config) throws ServletException {
        super.init(config);
        // One-time setup (e.g. load config)
    }

    @Override
    protected void doGet(HttpServletRequest req,
                         HttpServletResponse res)
            throws ServletException, IOException {
        String category = req.getParameter("category");
        List<Product> products =
            ProductRepository.findByCategory(category);
        req.setAttribute("products", products);
        req.getRequestDispatcher("/WEB-INF/products.jsp")
           .forward(req, res);
    }

    @Override
    protected void doPost(HttpServletRequest req,
                          HttpServletResponse res)
            throws IOException {
        String name = req.getParameter("name");
        // validate, persist...
        res.sendRedirect("/products");
    }
}
```

---

### ⚖️ Comparison Table

| Feature | Servlet | Spring MVC Controller | JAX-RS Resource |
|---|---|---|---|
| HTTP mapping | `@WebServlet("/path")` | `@GetMapping("/path")` | `@Path("/path")` |
| DI support | Manual / CDI | Full Spring DI | CDI / Jersey |
| Response types | `PrintWriter` / `OutputStream` | Return value converted | Return `Response` |
| Filters | `Filter` chain | Interceptors | ContainerFilter |
| Async support | `startAsync()` | `DeferredResult` | `@Suspended` |
| Abstraction level | Low | High | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "One Servlet per request" | One Servlet instance handles all requests concurrently on different threads. |
| "Servlets are outdated" | Spring MVC's `DispatcherServlet` IS a Servlet — the abstraction, not concept, changed. |
| "`HttpSession` is thread-safe" | Session attributes are not thread-safe if multiple tabs send concurrent requests. |
| "Filters run inside the Servlet" | Filters wrap the Servlet — they run before and after `service()` in the container chain. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Thread pool exhaustion**
- **Symptom:** Requests queue up; response times spike; eventually HTTP 503.
- **Root Cause:** Servlet threads blocked on slow I/O (DB queries, external API calls).
- **Diagnostic:**
```bash
# Check Tomcat thread pool metrics via JMX or Actuator
curl http://localhost:8080/actuator/metrics/tomcat.threads.busy
```
- **Fix:** Increase pool size (short-term); switch to async Servlet or WebFlux (long-term).
- **Prevention:** Set query timeouts; use connection pooling with max-wait limits.

**Failure Mode 2: Session fixation attack**
- **Symptom:** Attacker reuses a known session ID to hijack an authenticated session.
- **Root Cause:** Session ID not regenerated after login.
- **Diagnostic:** Check whether `request.changeSessionId()` is called post-authentication.
- **Fix:**
```java
// After successful login:
request.changeSessionId();  // Servlet 3.1+
```
- **Prevention:** Always regenerate session ID on privilege escalation.

**Failure Mode 3: ClassCastException on getAttribute**
- **Symptom:** `ClassCastException` when casting `request.getAttribute("user")`.
- **Root Cause:** Attribute set with one classloader, read with another (common in hot-reload scenarios).
- **Diagnostic:**
```java
Object attr = req.getAttribute("user");
System.out.println(attr.getClass().getClassLoader());
```
- **Fix:** Restart the application server; avoid hot-reload in production.
- **Prevention:** Use canonical class names; avoid cross-classloader attribute sharing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
HTTP Methods, HTTP Status Codes, Thread (Java), Java EE / J2EE Overview

**Builds On This (learn these next):**
JSP (Java Server Pages), Spring MVC (DispatcherServlet), Filter vs Interceptor, Async I/O

**Alternatives / Comparisons:**
Spring WebFlux (reactive), JAX-RS, Node.js HTTP server, Vert.x

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS     │ Java class handling HTTP        │
│                │ requests in a container         │
│ PROBLEM        │ Raw TCP socket HTTP handling    │
│                │ was vendor-specific drudgery    │
│ KEY INSIGHT    │ One instance, N concurrent      │
│                │ threads — never use mutable     │
│                │ instance fields                 │
│ USE WHEN       │ Java EE apps; understanding     │
│                │ Spring MVC internals            │
│ AVOID WHEN     │ New projects — use Spring MVC   │
│                │ or JAX-RS controllers           │
│ TRADE-OFF      │ Memory efficiency vs concurrency│
│                │ bug risk                        │
│ ONE-LINER      │ "doGet() is your HTTP handler"  │
│ NEXT EXPLORE   │ DispatcherServlet, Filter,      │
│                │ Spring MVC                      │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(A — System Interaction)** Spring's `DispatcherServlet` is one Servlet that routes all requests. What happens if `DispatcherServlet.doGet()` throws an uncaught exception — and how does Spring's `HandlerExceptionResolver` interact with the Servlet spec?

2. **(B — Scale)** A Servlet application handles 5,000 concurrent requests. The container's thread pool is 200 threads. The remaining 4,800 requests queue. What metrics tell you this is happening, and what are your options?

3. **(C — Design Trade-off)** Servlet filters run in an ordered chain. If you add security, logging, and compression filters, what determines their order, and what happens if compression runs before security?
