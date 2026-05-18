---
id: DPT-019
title: Chain of Responsibility
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-018
used_by: DPT-064, DPT-065
related: DPT-025, DPT-027, DPT-037
tags:
  - pattern
  - behavioral
  - intermediate
  - architecture
  - spring
  - request-pipeline
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/design-patterns/chain-of-responsibility/
---

⚡ TL;DR - Chain of Responsibility passes a request along
a linked chain of handlers; each handler decides to
process the request, pass it to the next handler, or
reject it - decoupling senders from receivers.

| #19 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-018 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-025, DPT-027, DPT-037 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An HTTP request arrives at a web application. Before the
controller logic runs, many checks must happen: log the
request, verify the JWT token, check rate limits, validate
the request body, check CORS headers. A monolithic filter:

```java
void handleRequest(Request req) {
    logRequest(req);
    if (!isAuthenticated(req)) return 401;
    if (isRateLimited(req)) return 429;
    if (!isValidBody(req)) return 400;
    if (!corsAllowed(req)) return 403;
    // finally: call controller
    controller.handle(req);
}
```

**THE BREAKING POINT:**
A new requirement: add IP allowlisting between rate limiting
and body validation. The entire handler must be modified.
New services need different subsets of these checks. Tests
for any single concern must set up the entire check pipeline.
The combined handler is now 200 lines, untestable in isolation,
and impossible to reuse individual checks across services.

**THE INVENTION MOMENT:**
Chain of Responsibility: each check becomes an independent
handler. Handlers are linked: logger → auth → rate limiter
→ body validator → CORS checker → controller. Each handler
processes what it is responsible for and calls `next.handle(req)`.
New handlers can be inserted at any position. Different
services use different handler chains. Each handler
is independently testable.

**EVOLUTION:**
Java Servlet Filters, Spring Security FilterChain, Spring
MVC HandlerInterceptors, Netty ChannelPipeline, and
Apache's FilterChain are all Chain of Responsibility
implementations. Every middleware pipeline in any HTTP
framework uses this pattern. Node.js Express middleware
(`app.use(fn)`) is Chain of Responsibility where `next()`
is the explicit pass-to-next call.

---

### 📘 Textbook Definition

The **Chain of Responsibility** pattern is a Behavioral
design pattern that decouples request senders from receivers
by giving multiple objects a chance to handle the request.
The receiving objects are chained, and the request is
passed along the chain until an object handles it (or the
chain ends). Each handler in the chain has a reference
to the next handler; it can decide to process the request
and/or pass it forward. The sender does not know which
handler will process its request.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Chain of Responsibility is a request that moves through
a pipeline of handlers, each one deciding "handle it,
pass it on, or stop it."

**One analogy:**
> An expense approval chain. An employee submits an expense.
> The team lead checks: "Is it under $100?" If yes, approve.
> If no, pass to manager. Manager checks: "Under $1,000?"
> If yes, approve. If no, pass to VP. VP approves anything
> above $1,000. The employee does not know who will approve
> - just that the chain will handle it.

**One insight:**
Chain of Responsibility is the pattern that makes
MIDDLEWARE possible. Every HTTP framework's pipeline is
a Chain of Responsibility - each "middleware" or "filter"
is a handler that either processes or passes the request
to the next.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each handler knows about the NEXT handler (linked list
   of handlers) but not the full chain.
2. A handler can: process the request and pass to next,
   process the request and stop (consume it), or
   pass without processing (delegate only).
3. The sender invokes the first handler; the chain
   handles the rest.

**DERIVED DESIGN:**
Three participants:
- **Handler interface**: defines `handle(request)` and
  holds a reference to the next handler
- **ConcreteHandler**: processes requests it is responsible
  for; passes others to next handler
- **Client**: constructs the chain, sends request to the
  first handler

**CHAIN CONSTRUCTION PATTERN:**
```java
// Builder style
Handler chain = new LoggingHandler(
    new AuthHandler(
        new RateLimitHandler(
            new BodyValidationHandler(
                new ControllerHandler()))));
chain.handle(request);
```

**TRADE-OFFS:**

**Gain:** Open/Closed Principle: add handlers without
modifying existing ones. Single Responsibility: each
handler does exactly one thing. Handlers are independently
testable. Chains are configurable at runtime.

**Cost:** No guarantee a request will be handled (it may
fall off the end of the chain unhandled). Hard to debug:
tracing which handler processed a request requires logging
or inspection. Chain ordering bugs are silent (handler
in wrong position processes requests incorrectly but no
exception is thrown).

---

### 🧪 Thought Experiment

**SETUP:**
A support ticket system with three tiers: Level-1
(simple issues, handle 80%), Level-2 (complex, handle
15%), Level-3 (escalation, handle 5%). Without CoR:
an if/else tree that must know all three levels.

**WITH CHAIN:**
L1Handler: if (ticket.isSimple()) process else next.handle(ticket)
L2Handler: if (ticket.isComplex()) process else next.handle(ticket)
L3Handler: always process (escalation - end of chain)

**INSIGHT:**
Each handler has ONE decision criterion. Adding L0 (FAQ
auto-resolution before L1) is one new handler class and
one chain configuration change. No existing handlers
modified. The chain ordering IS the business logic.

---

### 🧠 Mental Model / Analogy

> Chain of Responsibility is a PRODUCTION ASSEMBLY LINE.
> Each workstation processes one specific step on the item:
> inspection, painting, quality check, packaging.
> Each station either performs its task and passes forward,
> or flags a defect and stops the item. The item starts
> at station 1; the final station ships it.

- "Assembly line" = the chain
- "Workstation" = Handler
- "Item moving through" = the request
- "Flagging and stopping" = handler consuming/rejecting
- "Adding a new workstation" = adding a new handler at
  any position without changing others

**Where this analogy breaks down:**
A physical assembly line has a fixed order. CoR chains
can be reconfigured at runtime (different chain per request
type). Handlers can also SKIP THEMSELVES (pass without
processing), which assembly stations do not do.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When a request needs to pass through multiple checkpoints
(log it, check auth, check rate limit), Chain of Responsibility
lines them up and the request moves through each one
in sequence.

**Level 2 - How to use it (junior developer):**
Create a `Handler` interface with `setNext(Handler)` and
`handle(request)`. Implement each check as a separate
handler. In the `handle` method: process if responsible,
then call `next.handle(request)` to continue. Build the
chain by linking handlers. Pass the request to the first.

**Level 3 - How it works (mid-level engineer):**
Servlet Filters use CoR exactly: each `doFilter(request,
response, filterChain)` can add processing and call
`filterChain.doFilter(request, response)` to pass to the
next filter. Spring Security's `FilterChainProxy` maintains
a list of `SecurityFilter` implementations; each processes
its concern and calls `chain.doFilter()`. The `FilterChain`
object IS the "next" reference passed to each handler.

**Level 4 - Why it was designed this way (senior/staff):**
Chain of Responsibility solves the Open/Closed Principle
for request pipelines: the pipeline is open for extension
(add handlers) but closed for modification (existing
handlers are unchanged). This is how Spring Security can
add an entire authentication provider without changing
any existing security filter: add a new handler in the
chain at the correct position. Without CoR, adding an
auth provider requires modifying a monolithic auth handler.

**Level 5 - Mastery (distinguished engineer):**
Netty's `ChannelPipeline` is the most sophisticated CoR
implementation in Java networking: it supports bidirectional
pipelines (inbound handlers process data as it arrives;
outbound handlers process data as it is sent), dynamic
handler addition/removal while the pipeline is live, and
handler-specific execution contexts (each handler can
run in its own EventLoop). When a Netty connection receives
data: bytes -> decode -> decompress -> authenticate ->
deserialize -> route -> business logic. Each stage is an
independent ChannelHandler. Adding TLS to an existing
Netty pipeline: add an `SslHandler` at position 1 with
no other changes.

---

### ⚙️ How It Works (Mechanism)

```
Chain Structure
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Request → [Handler1] → [Handler2] → [Handler3] → null  │
│                                                         │
│  Each Handler:                                          │
│  ┌─────────────────────────────────────────┐            │
│  │ handle(request) {                        │           │
│  │   // pre-processing (log, check, modify) │           │
│  │   if (next != null)                      │           │
│  │     next.handle(request);               │            │
│  │   // post-processing (e.g., log response)│           │
│  │ }                                        │           │
│  └─────────────────────────────────────────┘            │
│                                                         │
│  Handler decides:                                       │
│  1. Process AND forward: call next.handle()             │
│  2. Process AND stop: do NOT call next.handle()         │
│  3. Forward only: call next.handle() without processing │
│  4. Reject: throw exception / return error response     │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SPRING SECURITY FILTERCHAIN FLOW:**
```
HTTP Request arrives at Servlet container
  → SecurityContextPersistenceFilter
      loads SecurityContext from session
      calls chain.doFilter()
  → UsernamePasswordAuthenticationFilter
      checks for login form POST
      calls chain.doFilter()
  → BasicAuthenticationFilter
      checks for Basic Auth header, authenticates
      calls chain.doFilter()
  → ExceptionTranslationFilter
      catches auth/access exceptions
      calls chain.doFilter()
  → FilterSecurityInterceptor
      checks authorization for the request URL
      if authorized: calls chain.doFilter()
      if not: throws AccessDeniedException
  → DispatcherServlet → Controller
```

**FAILURE PATH:**
```
At BasicAuthenticationFilter:
  Basic Auth header present but invalid credentials
  → AuthenticationException thrown
At ExceptionTranslationFilter:
  catches AuthenticationException
  → sends 401 Unauthorized response
  → chain terminates; controller is never reached
```

---

### 💻 Code Example

**Example 1 - Without CoR (monolithic handler):**

```java
// BAD: all concerns in one class
class RequestHandler {
    void handle(HttpRequest req, HttpResponse resp) {
        // Concern 1: logging
        logger.info("Request: " + req.path());

        // Concern 2: authentication
        if (!authService.isAuthenticated(req)) {
            resp.sendError(401);
            return;
        }

        // Concern 3: rate limiting
        if (rateLimiter.isExceeded(req.clientIp())) {
            resp.sendError(429);
            return;
        }

        // Concern 4: body validation
        if (!validator.isValid(req.body())) {
            resp.sendError(400);
            return;
        }
        // Business logic finally
        controller.handle(req, resp);
    }
}
// 4 concerns in one class, impossible to reorder,
// insert new concerns, or test individually
```

**Example 2 - Chain of Responsibility solution:**

```java
// GOOD: each handler has one responsibility

abstract class RequestFilter {
    private RequestFilter next;

    public RequestFilter setNext(RequestFilter next) {
        this.next = next;
        return next; // enables fluent chain building
    }

    public abstract void filter(
        HttpRequest req, HttpResponse resp);

    // Helper: pass to next or complete
    protected void proceed(
        HttpRequest req, HttpResponse resp) {
        if (next != null) {
            next.filter(req, resp);
        }
    }
}

class LoggingFilter extends RequestFilter {
    @Override
    public void filter(HttpRequest req, HttpResponse resp) {
        logger.info("IN  " + req.method() + " " + req.path());
        proceed(req, resp);
        logger.info("OUT " + resp.status());
    }
}

class AuthFilter extends RequestFilter {
    @Override
    public void filter(HttpRequest req, HttpResponse resp) {
        if (!authService.isAuthenticated(req)) {
            resp.sendError(401, "Unauthorized");
            return; // STOP - do not call proceed()
        }
        proceed(req, resp);
    }
}

class RateLimitFilter extends RequestFilter {
    @Override
    public void filter(HttpRequest req, HttpResponse resp) {
        if (rateLimiter.isExceeded(req.clientIp())) {
            resp.sendError(429, "Too Many Requests");
            return; // STOP
        }
        proceed(req, resp);
    }
}

class ControllerFilter extends RequestFilter {
    @Override
    public void filter(HttpRequest req, HttpResponse resp) {
        controller.handle(req, resp); // end of chain
        // proceed() not needed - last in chain
    }
}

// Build chain: LoggingFilter -> Auth -> RateLimit -> Controller
RequestFilter chain = new LoggingFilter();
chain.setNext(new AuthFilter())
     .setNext(new RateLimitFilter())
     .setNext(new ControllerFilter());

// Execute: one entry point
chain.filter(request, response);

// Adding IP allowlist between auth and rate limit:
// Create IPAllowlistFilter, insert in chain - nothing else changes
```

**Example 3 - Servlet Filter Chain (Java EE CoR):**

```java
// RECOGNITION: Java Servlet Filter IS Chain of Responsibility

@WebFilter("/*")
class LoggingServletFilter implements Filter {
    @Override
    public void doFilter(
        ServletRequest req, ServletResponse resp,
        FilterChain chain) // <-- the chain is passed in
        throws IOException, ServletException {

        HttpServletRequest httpReq = (HttpServletRequest) req;
        logger.info("Request: " + httpReq.getRequestURI());

        long start = System.currentTimeMillis();
        chain.doFilter(req, resp); // PASS to next filter
        long elapsed = System.currentTimeMillis() - start;
        logger.info("Response in " + elapsed + "ms");
        // Post-processing happens AFTER next chain completes
    }
}
// chain.doFilter() = proceed() in the manual implementation
// FilterChain = the "next" reference, managed by the container
```

**How to test/verify correctness:**
Test each handler independently: create the handler with
a mock `next`, verify it processes what it should and
calls `next` when it should not stop, and does NOT call
`next` when it should stop (auth failure, rate limit exceeded).
Integration test: build a chain, pass requests, verify
correct responses and which handlers processed them.

---

### ⚖️ Comparison Table

| Pattern | How request moves | Handler decides | Sender knows receiver? |
| --- | --- | --- | --- |
| **CoR** | Linear chain | Process/pass/stop | No |
| Command | Directly invoked | Execute | Yes (via Invoker) |
| Observer | Broadcast to all | React (no decision) | No |
| Strategy | Single handler | Execute | Yes |

**How to choose:**
- Request traverses multiple handlers, each with one
  concern, chain is configurable: Chain of Responsibility
- Request invoked by a specific object, supports undo/queue:
  Command
- Event broadcast to all interested parties: Observer
- Single algorithm selected from multiple: Strategy

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Every handler MUST process the request | Handlers can pass without processing - acting only as a relay (e.g., a monitoring handler that logs but always passes) |
| CoR and Command are similar because both handle requests | Command encapsulates a request as an object with undo/redo/queue semantics. CoR is a pipeline pattern - the request moves through a sequence of handlers. Different intent, different structure |
| The chain must always reach the last handler | A handler CAN and SHOULD stop the chain (by not calling next) when it detects a condition that should end processing (auth failure, rate limit, validation error) |
| Java Servlet Filters are not design patterns | Java Servlet Filter is a precise implementation of Chain of Responsibility: Filter = Handler, FilterChain = the chain's next reference, doFilter() = handle() + proceed() |
| CoR requires a linked list of Handler objects | Modern frameworks implement CoR as an ordered list/array of handlers iterated by a controller object (e.g., Spring Security's FilterChainProxy iterates a List<SecurityFilter>) - same semantics, different data structure |

---

### 🚨 Failure Modes & Diagnosis

**Handler Calls `proceed()` After Sending Error Response**

**Symptom:**
An auth filter sends 401 Unauthorized, but the request
STILL reaches the controller. The controller runs with
no auth context and throws a NullPointerException. Two
responses are committed: 401 and then 500.

**Root Cause:**
The auth filter calls `proceed()` (or `next.handle()`)
AFTER sending the error response. The chain continues
despite the error.

```java
// BAD: calls proceed after sending error
class AuthFilter extends RequestFilter {
    public void filter(Request req, Response resp) {
        if (!isAuthenticated(req)) {
            resp.sendError(401);
            // Missing: return!
        }
        proceed(req, resp); // STILL CALLED even after 401
    }
}
```

**Fix:**
```java
class AuthFilter extends RequestFilter {
    public void filter(Request req, Response resp) {
        if (!isAuthenticated(req)) {
            resp.sendError(401);
            return; // MUST return - do not call proceed
        }
        proceed(req, resp);
    }
}
```

**Prevention:**
Code review rule: any `if (error condition)` block in a
handler that sends a response MUST include an explicit
`return` before any `proceed()` call.

---

**Wrong Handler Order Causes Silent Security Bypass**

**Symptom:**
An IP rate limiter runs BEFORE authentication. A brute-
force attack is not stopped by auth failures because the
attacker's rate limit resets between bursts. The issue:
logging the attack happens but the system is still
vulnerable.

**Root Cause:**
Chain construction: Logger → RateLimiter → Auth.
The rate limiter counts ALL requests before auth - including
requests from unauthenticated sources. A more correct
order for the use case: Logger → Auth → RateLimiter
(rate limit authenticated users to prevent abuse of
authenticated endpoints; use a separate IP rate limiter
for login endpoints only).

**Diagnostic Signal:**
Security issues related to request pipeline ordering
are notoriously hard to trace. The feature works
individually but the interaction between handlers creates
the vulnerability.

**Prevention:**
Document the intended chain order and the REASON each
handler appears at its position. Sequence diagrams for
the chain, showing which handlers can short-circuit and
the security implications of the ordering.

---

**Request Falls Off End of Chain Unhandled**

**Symptom:**
Certain requests receive no response (connection times
out). Investigation shows the request reaches the last
handler but falls off - the last handler passed the
request to `next`, which is `null`, and the code either
does nothing or throws NullPointerException.

**Root Cause:**
Chain has no "catch-all" terminal handler. The last handler
calls `proceed()` expecting another handler, but the
chain ended.

**Fix:**
Add a terminal handler that ALWAYS provides a response
(default behavior, 404 response, or error):
```java
class NotFoundHandler extends RequestFilter {
    public void filter(Request req, Response resp) {
        resp.sendError(404, "Not Found for: " + req.path());
        // No proceed() - end of chain
    }
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Proxy` - DPT-018; Spring Security's FilterChainProxy
  uses both Proxy (to intercept) and Chain of Responsibility
  (the filter chain) - understanding Proxy first helps

**Builds On This (learn these next):**
- `Command` - Chain of Responsibility moves requests;
  Command encapsulates requests as objects - common
  combination in event-driven systems
- `Event Bus Pattern` - alternative to CoR for event routing;
  compare: CoR is sequential pipeline; Event Bus is
  publish-subscribe

**Alternatives / Comparisons:**
- `Observer` - all observers notified; CoR stops when
  a handler consumes the request
- `Strategy` - single algorithm selected; CoR processes
  through multiple handlers

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Request passed through linked handlers;  │
│              │ each processes, passes, or stops it      │
├──────────────┼──────────────────────────────────────────┤
│ KEY PROPERTY │ Sender does not know which handler       │
│              │ will process; handlers are decoupled     │
├──────────────┼──────────────────────────────────────────┤
│ STOP PATTERN │ Do NOT call next.handle() to stop chain  │
│              │ Always return after sending error resp   │
├──────────────┼──────────────────────────────────────────┤
│ JAVA EXAMPLE │ Servlet FilterChain, Spring Security     │
│              │ FilterChainProxy, Netty ChannelPipeline  │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Calling proceed() after error response   │
│              │ → chain continues, double response sent  │
├──────────────┼──────────────────────────────────────────┤
│ VS OBSERVER  │ Observer: all listeners notified         │
│              │ CoR: chain stops when request is handled │
├──────────────┼──────────────────────────────────────────┤
│ CONFIGURE    │ Chain order = business logic; document   │
│              │ and test the ordering explicitly         │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Command → Observer → Mediator            │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Each handler: process AND call next, OR stop (do not
   call next). Calling `proceed()` after sending an error
   response is the most common CoR bug
2. Servlet Filters, Spring Security FilterChain, Netty
   ChannelPipeline, and Express middleware are all
   Chain of Responsibility implementations - it is the
   foundation of ALL HTTP middleware pipelines
3. Handler ORDER is the business logic - wrong order = silent
   security vulnerabilities; always document and test the
   intended chain sequence

**Interview one-liner:**
"Chain of Responsibility passes requests through a linked
handler pipeline; each handler decides to process, pass on,
or stop the request. It is the pattern behind Servlet Filters,
Spring Security FilterChain, and all HTTP middleware pipelines.
The classic bug: calling next.handle() after sending an error
response - the chain continues executing when it should stop."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Request processing pipelines are the ideal context for
Chain of Responsibility. When a request needs N sequential
operations (authenticate, rate limit, validate, route),
each operation should be an independent handler in a
configurable chain. This makes each concern independently
testable, the chain reconfigurable without code changes,
and new concerns insertable without modifying existing
code - the Open/Closed Principle applied to pipelines.

**Where else this pattern appears:**
- **Express.js middleware** - `app.use(fn)` registers
  a handler in the chain; `next()` is the explicit
  pass-to-next call; `next(err)` passes an error to
  error-handling middleware
- **Netty ChannelPipeline** - bidirectional CoR for
  network I/O: inbound pipeline (bytes → decode → process),
  outbound pipeline (process → encode → bytes); handlers
  can be added/removed while the pipeline is live
- **AWS API Gateway** - request/response interceptors
  (authorizers, validators, transformers) form a CoR;
  each stage processes and passes or stops the request

**Industry applications:**
- **Spring Security** - 20+ security filters in a configured
  chain; each has one responsibility; Spring Boot's auto-
  configuration wires them in the correct security order
- **Logging frameworks** - Log4j/SLF4J appenders form a
  chain: each appender decides to handle (write to file,
  write to console) or pass; log level filtering is a
  CoR stop decision
- **Java Bean Validation** - constraint validators form
  a chain; first failing constraint stops validation
  with error details

---

### 💡 The Surprising Truth

Java's `try-catch-finally` block IS a form of Chain of
Responsibility for exception handling. When an exception
is thrown: the JVM searches up the call stack for a
matching `catch` block (the "chain"). Each stack frame
is a "handler." The first matching `catch` processes
the exception (stops the chain). If no `catch` matches:
the exception propagates to the thread's uncaught
exception handler (the terminal handler). The `finally`
block runs regardless - it is a handler that always
executes (processes + passes). Java exception propagation
is not usually described this way, but the structure is
identical: exception moves up a chain of potential
handlers until one catches it.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Describe what `chain.doFilter(request, response)`
   does in a Java Servlet Filter, connecting it to the
   Chain of Responsibility pattern's "proceed to next handler"
2. [IMPLEMENT] Build a handler chain for an HTTP pipeline
   with logging, JWT authentication, and request body
   validation - implement each as a separate handler class
   and construct the chain correctly
3. [DIAGNOSE] Given a Spring Security-secured endpoint
   that returns 401 but still executes controller logic,
   identify the "proceed after error" bug in the responsible
   filter and fix it
4. [EXPLAIN] Why Spring Security adds 20+ filters to the
   chain rather than combining them, connecting to the
   Open/Closed Principle and independent testability
5. [COMPARE] Explain the difference between Chain of
   Responsibility and Observer: when a request must be
   handled by exactly one handler (CoR) vs when an event
   must be received by all subscribers (Observer)

---

### 🧠 Think About This Before We Continue

**Q1.** In Spring Security's FilterChain, why does each
filter receive the `FilterChain` object as a parameter
rather than a direct reference to the NEXT filter? What
does this design decision enable that a direct "next filter"
reference would not?

*Hint: The FilterChain is a controller that can insert
additional logic between any two filters (e.g., tracking
which filter is next, enforcing ordering, adding wrapper
filters). If filters held direct references to the next
filter, inserting a new filter would require modifying
the previous filter's reference. With FilterChain as
the intermediary: the chain manager adds/removes filters
by updating its list; existing filters only call
`chain.doFilter()` - they never hold direct references.
This makes the chain dynamic and allows the container
to reconfigure it.*

**Q2.** Design a CoR-based request validation system
where the FIRST handler that can validate a request type
handles it (not all handlers see every request). For example:
JsonValidator handles JSON requests, XmlValidator handles
XML, and FormValidator handles form submissions. How does
this differ from the standard CoR where ALL handlers see
the request? What is the risk if you accidentally let
all handlers process the same request?

*Hint: This is the "exclusive handler" variant: handler
checks "can I handle this?" If yes: handle AND stop chain.
If no: pass to next. Standard CoR: handlers check "should
I process this?" independently. Exclusive variant: handler
checks "is this mine exclusively?" Risk of all handlers
processing: JSON gets validated by JsonValidator (correct),
then XmlValidator tries to parse it as XML (fails or
corrupts), then FormValidator tries again. Multiple
"handling" corrupts the request. The exclusive variant
MUST use a type discriminator before processing.*

---

### 🎯 Interview Deep-Dive

**Q1: How does Java's Servlet FilterChain implement Chain
of Responsibility? Walk through a request.**

*Why they ask:* Tests recognition of the pattern in the
most fundamental Java web framework component.

*Strong answer includes:*
- Each `javax.servlet.Filter` implements the Handler interface
- `doFilter(request, response, chain)` is the handle method
- `chain.doFilter(request, response)` is the "proceed to
  next handler" call
- The container assembles the FilterChain based on filter
  registration order (web.xml or @WebFilter)
- Pre-processing happens BEFORE `chain.doFilter()`
- Post-processing happens AFTER `chain.doFilter()` returns
- NOT calling `chain.doFilter()` stops the chain (the
  request never reaches the servlet)
- Example walk-through: Logging filter logs request, calls
  chain.doFilter(); Auth filter checks token, if invalid
  sends 401 (no chain.doFilter()); if valid calls
  chain.doFilter(); next filter continues

**Q2: What is the difference between Chain of Responsibility
and Observer pattern?**

*Why they ask:* Tests ability to distinguish behavioral
patterns with overlapping "multiple handlers" themes.

*Strong answer includes:*
- CoR: request moves SEQUENTIALLY through handlers; one
  handler can STOP the chain; handlers are ordered; sender
  does not know which handler will process
- Observer: event BROADCAST to ALL subscribers simultaneously;
  no handler can stop others from receiving; subscribers
  are independent; sender (publisher) does not know subscribers
- CoR: authentication filter STOPS the chain on failure;
  subsequent handlers never see the request
- Observer: when an Order event is published, ALL subscribers
  (EmailService, InventoryService, AnalyticsService) are
  notified; no one can stop others from being notified
- Use CoR when: exactly one handler should ultimately be
  responsible for a request; handlers form a sequential
  pipeline
- Use Observer when: all interested parties should know
  about an event; no handler should block others

**Q3: How would you implement middleware pipeline for a
message processing system (like Kafka consumer processing)
using Chain of Responsibility?**

*Why they ask:* Tests ability to apply the pattern beyond
HTTP to message-driven systems.

*Strong answer includes:*
- Define `MessageHandler` interface with
  `handle(Message msg, MessageHandler next)`
- Handlers: DeserializationHandler (JSON → POJO),
  IdempotencyHandler (check if already processed),
  AuthorizationHandler (check sender permissions),
  ValidationHandler (validate message content),
  BusinessLogicHandler (process the message)
- Chain: Deserialization → Idempotency → Authorization
  → Validation → BusinessLogic
- Idempotency handler: if already processed, stop chain
  (message was processed on a previous retry)
- Authorization handler: if unauthorized sender, stop
  chain (discard message, increment metric)
- This is exactly how Kafka consumer middleware frameworks
  (Spring Kafka @KafkaListener interceptors, message
  pre-processors) work

