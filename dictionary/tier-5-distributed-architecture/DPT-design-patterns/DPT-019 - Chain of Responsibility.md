---
layout: default
title: "Chain of Responsibility"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /design-patterns/chain-of-responsibility/
id: DPT-019
category: Design Patterns
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-019 - Chain of Responsibility

⚡ TL;DR - Chain of Responsibility passes a request along a chain of handlers, where each handler decides to process the request or forward it to the next handler.

| DPT-019 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Linked List, Polymorphism | |
| **Used by:** | HTTP Middleware, Servlet Filters, Event Handling, Approval Workflows | |
| **Related:** | Decorator, Command, Observer, Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An expense approval system has these rules: expenses < $100 are auto-approved; $100–$1000 require manager approval; $1000–$10000 require director approval; > $10000 require VP approval. Without Chain of Responsibility, one `ApprovalService` contains a ladder of `if-else if` blocks. Adding a new approval tier (e.g., Senior Manager between Manager and Director) requires modifying this central class, touching working code, adding a new condition, and re-testing the entire ladder.

**THE BREAKING POINT:**
The `if-else if` ladder grows with every new tier, exception, or business rule. It becomes the most fragile file in the system - every new business rule requires touching it. The single class has coupled together all approval logic for all tiers. A bug in the Director approval logic risks affecting the VP approval logic because both live in the same block.

**THE INVENTION MOMENT:**
This is exactly why the Chain of Responsibility pattern was created. Each tier is an independent `Handler` object. Each handler knows only its own rule and whether to handle or forward. The chain is assembled at configuration time. Adding a new tier: create one new `Handler` class and insert it into the chain. Zero changes to existing handler classes.

**EVOLUTION:**
Chain of Responsibility was widely used in GUI event handling
(AWT event propagation) and servlet filter chains in the 1990s.
Java's `Servlet` `Filter` interface (1998) institutionalised
the pattern in web applications. Spring Security's filter chain
is a 20+ handler CoR. Modern equivalents include middleware
stacks (Express.js, ASP.NET Core middleware), gRPC interceptors,
and Kafka consumer interceptors. The pattern is now so embedded
in framework infrastructure that most engineers use it without
recognising the underlying pattern.

---

### 📘 Textbook Definition

The **Chain of Responsibility** pattern is a behavioural design pattern that allows a request to be passed along a chain of potential handlers. Each handler in the chain decides either to process the request or to pass it to the next handler. The chain decouples the sender of a request from its receiver by giving multiple objects a chance to handle the request. Handlers are assembled into a linked chain; the client sends a request to the first handler and the chain handles propagation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pass a request down a line of handlers until one agrees to handle it.

**One analogy:**
> A customer support escalation system. You call Level 1 support. They try to help. If they can't resolve it, they escalate to Level 2. If Level 2 can't solve it, they escalate to Level 3 engineer. Each level independently decides "I can handle this" or "this needs to go higher." The customer just calls the same number - the routing is invisible.

**One insight:**
The pattern decouples WHO sends the request from WHO handles it. The sender doesn't need to know which handler will process it - or even how many handlers exist. The chain can be reconfigured, extended, or reordered at runtime without changing the sender or any existing handler.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A request may be handled by any one of several potential handlers, and the correct handler depends on the request's properties.
2. The sender should not need to know which handler will process its request.
3. The set of handlers and their order may change independently of the sender.

**DERIVED DESIGN:**
Given invariant 1+2: the sender sends to the HEAD of the chain; the chain routes it. Given invariant 3: each handler holds only a reference to the NEXT handler - if it cannot handle the request, it delegates forward. This linked structure allows runtime chain reconfiguration.

Each handler is autonomous: it implements a `handle(request)` method that contains its own condition and action. If the condition is not met, it calls `next.handle(request)`. The chain terminates when: (1) a handler processes the request, or (2) the end of the chain is reached with no handler able to process it (unhandled case must be explicitly considered).

**THE TRADE-OFFS:**
**Gain:** Open/Closed Principle - add handlers without modifying existing ones; each handler is independently testable; chain order is configurable at runtime; long conditionals replaced by clean, single-purpose handler classes.
**Cost:** No guarantee that the request will be handled (if no handler matches, it falls through silently - must handle this case); harder to debug (the chain traversal can be difficult to trace); performance: traversing many handlers for every request adds overhead; circular chain reference causes infinite loop.

---

### 🧪 Thought Experiment

**SETUP:**
An authentication middleware chain must: (1) check if the request has a valid JWT token, (2) verify the token has not been revoked, (3) check that the user has the required role. All three must pass for the request to proceed to the controller.

**WHAT HAPPENS WITHOUT CHAIN:**
A single `AuthenticationFilter` has three nested conditionals. Adding OAuth2 support requires modifying this working class. A new "IP whitelist" check must be inserted between steps 2 and 3 - requiring careful surgery on the conditional logic to maintain correct ordering.

**WHAT HAPPENS WITH CHAIN:**
Three handlers: `JwtValidationHandler → RevocationCheckHandler → RoleCheckHandler`. Each calls `next.handle(request)` only after passing its own check. Adding an IP whitelist: create `IpWhitelistHandler` and insert it between `RevocationCheckHandler` and `RoleCheckHandler` - the configuration changes, no existing handler changes.

**THE INSIGHT:**
Chain of Responsibility makes middleware assembly a configuration problem, not a code-change problem. Each handler class is a reusable component. The chain is the policy; the handlers are the mechanisms.

---

### 🧠 Mental Model / Analogy

> Chain of Responsibility is like an airport security check. First: ticket validity check. Second: ID verification. Third: baggage screening. Fourth: body scanner. Each checkpoint handles its specific concern. If you pass a checkpoint, you move to the next. Each checkpoint is independently staffed and independently replaceable. Adding biometric scanning: insert a new checkpoint between ID verification and baggage - the other checkpoints don't change.

- "Airport checkpoints" → handler objects in the chain
- "Moving to next checkpoint" → `next.handle(request)` call
- "Failing a checkpoint" → handler processes (stops) the request
- "Passing all checkpoints" → request reaches its destination (controller)
- "Adding a new checkpoint" → inserting a new handler class in the chain

Where this analogy breaks down: in an airport, ALL checkpoints must be passed. In Chain of Responsibility, typically ONE handler handles the request and no further propagation occurs. Some variants (pure pipe-and-filter) let ALL handlers process, each potentially transforming the request.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Chain of Responsibility is a relay race for requests. A request is handed from one runner to the next. The first runner who can handle it finishes the race. Others pass the baton. New runners can be added to the relay without changing the race organiser's instructions.

**Level 2 - How to use it (junior developer):**
Define a `Handler` interface with `setNext(Handler next)` and `handle(Request request)`. Create concrete handlers implementing the interface. In `handle()`: if the condition is met, process the request (and optionally stop propagation); otherwise, call `if (next != null) next.handle(request)`. Assemble the chain by calling `h1.setNext(h2); h2.setNext(h3)`. Send to head: `h1.handle(request)`.

**Level 3 - How it works (mid-level engineer):**
Two variants differ in whether a handled request propagates further: (1) **Exclusive handling** - only ONE handler processes the request; once handled, propagation stops. Used for approval workflows (one approver decides). (2) **Inclusive handling (pipe-and-filter)** - EVERY handler in the chain processes the request in sequence, each potentially transforming it. Used for HTTP middleware (each filter adds/modifies headers). Java Servlet `Filter` API is the canonical inclusive chain: each `Filter.doFilter()` calls `chain.doFilter()` which invokes the next filter, and wrapping that call is how the filter adds pre/post-processing. Spring Security's `SecurityFilterChain` is a configurable inclusive chain of 15+ security filters.

**Level 4 - Why it was designed this way (senior/staff):**
Chain of Responsibility was formalised partly to replace hard-coded conditional dispatch (the `if-else if` ladder) with a flexible, runtime-configurable dispatch mechanism. Its purest form - the "hot path" of the chain - is a singly-linked list traversal with virtual dispatch at each node. The performance characteristic is O(n) where n is the number of handlers before the matching one. For approval workflows (n ≤ 5), this is negligible. For HTTP middleware (n = 20 filters on every request at 10,000 req/s), each handler contributes to latency - thus Spring Security carefully documents its filter order and provides skip conditions. The pattern's greatest value is demonstrated in Java Servlet Filters and Node.js Express middleware - both are Chain of Responsibility implemented at the framework level, enabling composable, testable, independent concern handling.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  CHAIN OF RESPONSIBILITY - STRUCTURE                 │
│                                                      │
│  Client                                              │
│    │ handle(request)                                 │
│    ▼                                                 │
│  ┌──────────────────┐                               │
│  │ SupportLevel1    │                               │
│  │ if canHandle():  │                               │
│  │   resolve()  ←── │ ─ HANDLES: stops here         │
│  │ else:            │                               │
│  │   next.handle()  │                               │
│  └──────┬───────────┘                               │
│         │ (if not handled)                          │
│         ▼                                           │
│  ┌──────────────────┐                               │
│  │ SupportLevel2    │                               │
│  │ if canHandle():  │                               │
│  │   resolve()  ←── │ ─ HANDLES: stops here         │
│  │ else:            │                               │
│  │   next.handle()  │                               │
│  └──────┬───────────┘                               │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────┐                               │
│  │ SupportLevel3    │                               │
│  │ resolve() always │ ← last resort, handles all    │
│  └──────────────────┘                               │
└──────────────────────────────────────────────────────┘
```

**Chain assembly:**
```java
Handler chain = new Level1Handler();
chain.setNext(new Level2Handler())
     .setNext(new Level3Handler()); // fluent builder
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (HTTP request through Spring Security filters):**
```
HTTP Request arrives
  → CorsFilter (passes through, adds CORS headers)
  → SecurityContextPersistenceFilter (loads session)
  → JwtAuthenticationFilter
                ← YOU ARE HERE
     → validates JWT token
     → sets SecurityContext
     → chain.doFilter() (forwards to next)
  → AuthorizationFilter (checks role)
  → DispatcherServlet (reaches controller)
  → Response returned through chain in reverse
```

**FAILURE PATH:**
```
JwtAuthenticationFilter: token invalid
  → does NOT call chain.doFilter()
  → writes 401 Unauthorized response directly
  → chain stops - controller never reached
```

**WHAT CHANGES AT SCALE:**
At 50,000 req/s with 20 handlers, each handler adds its overhead to every request. Handlers that can short-circuit early (return quickly without delegation) should be placed early in the chain. Expensive handlers (database lookups, network calls) should be placed last or behind early-exit conditions. At extreme scale, handler overhead can be measured with per-filter request tracing in Spring Boot Actuator.

---

### 💻 Code Example

**Example 1 - BAD: Monolithic if-else approval ladder:**
```java
// BAD: all approval logic coupled in one class
public class ExpenseApprover {
    public boolean approve(Expense expense) {
        if (expense.amount() < 100) {
            return autoApprove(expense);
        } else if (expense.amount() < 1000) {
            return managerApprove(expense); // Manager logic here
        } else if (expense.amount() < 10000) {
            return directorApprove(expense); // Director logic here
        } else {
            return vpApprove(expense);       // VP logic here
        }
        // Adding SeniorManager tier: modify THIS class
    }
}
```

**Example 2 - GOOD: Chain of Responsibility:**
```java
// Handler interface
public abstract class ApprovalHandler {
    private ApprovalHandler next;

    public ApprovalHandler setNext(ApprovalHandler next) {
        this.next = next;
        return next; // fluent for chaining
    }

    public abstract void handle(ExpenseRequest request);

    protected void passToNext(ExpenseRequest request) {
        if (next != null) {
            next.handle(request);
        } else {
            request.reject("No approver found for amount: "
                + request.getAmount());
        }
    }
}

// Concrete handler: auto-approval for small amounts
public class AutoApprovalHandler extends ApprovalHandler {
    @Override
    public void handle(ExpenseRequest request) {
        if (request.getAmount() < 100) {
            request.approve("Auto-approved (< $100)");
        } else {
            passToNext(request); // forward to next handler
        }
    }
}

// Concrete handler: manager approval
public class ManagerApprovalHandler extends ApprovalHandler {
    @Override
    public void handle(ExpenseRequest request) {
        if (request.getAmount() < 1000) {
            boolean approved = askManager(request);
            if (approved) request.approve("Manager approved");
            else          request.reject("Manager rejected");
        } else {
            passToNext(request);
        }
    }
}

// Chain assembly:
ApprovalHandler chain = new AutoApprovalHandler();
chain.setNext(new ManagerApprovalHandler())
     .setNext(new DirectorApprovalHandler())
     .setNext(new VpApprovalHandler());

// Usage:
ExpenseRequest req = new ExpenseRequest(500.0);
chain.handle(req);
System.out.println(req.getStatus()); // "Manager approved"
```

**Example 3 - Servlet Filter chain (Java EE / Jakarta EE):**
```java
// Inclusive chain: ALL filters execute in sequence
@WebFilter("/*")
public class RequestLoggingFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req,
                         ServletResponse res,
                         FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpReq =
            (HttpServletRequest) req;
        long start = System.currentTimeMillis();
        log.info("--> {} {}", httpReq.getMethod(),
            httpReq.getRequestURI());

        chain.doFilter(req, res); // call next filter in chain

        long elapsed = System.currentTimeMillis() - start;
        log.info("<-- {} {}ms",
            ((HttpServletResponse) res).getStatus(),
            elapsed);
        // Both pre and post-processing around each request
    }
}
```

---

### ⚖️ Comparison Table

| Pattern | Handles Request | All handlers run? | Chain configurable? | Best For |
|---|---|---|---|---|
| **Chain of Responsibility** | One (exclusive) or all (inclusive) | Optional | Yes (runtime) | Approval workflows, middleware |
| Decorator | Wraps only, delegates always | Yes (all wrap) | Yes (runtime) | Adding behaviour to objects |
| Command | Encapsulates request | N/A | N/A | Queuing, undo/redo |
| Strategy | Selects one algorithm | No (one selected) | Yes | Algorithm variations |
| Observer | Notifies all subscribers | Yes (all notified) | Yes | Event broadcasting |

How to choose: use Chain of Responsibility when a request should be handled by ONE of several potential handlers based on the request's properties, and the set of potential handlers should be extensible. Use Decorator when ALL wrapping layers must execute for every request. Use Observer when ALL subscribers must receive every event.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Chain of Responsibility always stops at the first handler | Only in "exclusive" mode. "Inclusive" mode (pipe-and-filter) passes the request through ALL handlers - Servlet Filters work this way |
| The chain must be linear (singly linked list) | The chain can branch (tree of handlers), or a handler can decide to skip handlers non-linearly. A linear chain is the most common form |
| Request is always handled by exactly one handler | In exclusive mode, 0 or 1 handlers processes it. The "0 handlers" case (unhandled request) must be explicitly designed for |
| Adding a new handler never breaks existing ones | True only if handler interfaces are stable. If the `Handler` interface changes, all handlers must be updated |
| Chain of Responsibility and Decorator are the same | Decorator always delegates to the wrapped object; it adds behaviour around the same call. Chain of Responsibility uses conditional forwarding - a handler may stop propagation |

---

### 🚨 Failure Modes & Diagnosis

**1. Silent Request Drop - No Handler Processes the Request**

**Symptom:** An expense request for $500 is submitted and nothing happens - no approval, no rejection, no log message.

**Root Cause:** The chain's `passToNext()` silently does nothing when `next == null`. No handler matched, but no "unhandled" action was defined.

**Diagnostic:**
```java
// Add logging to the pass-through:
protected void passToNext(ExpenseRequest request) {
    if (next != null) {
        next.handle(request);
    } else {
        log.warn("Unhandled request amount=${}: "
            + "no handler in chain matched",
            request.getAmount());
        request.reject("No approver configured");
    }
}
```

**Fix:**
Always add a "catch-all" handler at the end of the chain, or handle the `null` next case with a meaningful rejection/log.

**Prevention:** Design rule: every chain must have a final "default" handler that catches all unhandled requests and produces a well-defined outcome.

---

**2. Circular Chain - Infinite Loop**

**Symptom:** Expense request processing runs indefinitely; stack overflow or timeout after milliseconds.

**Root Cause:** Chain configuration accidentally set `handler3.setNext(handler1)`, creating a cycle.

**Diagnostic:**
```java
// Cycle detection during chain assembly:
Set<ApprovalHandler> visited = new HashSet<>();
ApprovalHandler current = chainHead;
while (current != null) {
    if (!visited.add(current)) {
        throw new IllegalStateException(
            "Circular chain detected at: "
            + current.getClass().getSimpleName());
    }
    current = current.getNext();
}
```

**Fix:**
Remove the circular reference. Use factory/builder methods to assemble chains to prevent accidental cycles.

**Prevention:** Validate chain at construction time using the cycle detection above.

---

**3. Handler Order Bug - Wrong Handler Fires**

**Symptom:** A $150 expense is director-approved instead of manager-approved.

**Root Cause:** `DirectorApprovalHandler` was accidentally inserted before `ManagerApprovalHandler` in the chain. The Director handler's condition matches `< $10000` which includes all manager-level expenses.

**Diagnostic:**
```java
// Print chain order at startup:
ApprovalHandler current = chainHead;
int pos = 0;
while (current != null) {
    log.info("Chain[{}]: {}",
        pos++, current.getClass().getSimpleName());
    current = current.getNext();
}
```

**Fix:**
Correct the chain assembly order. Consider using an ordered list of handler factories sorted by amount threshold.

**Prevention:** Unit-test the assembled chain with representative amounts from each tier. Verify which handler processes each test case.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linked List` - the chain is a singly-linked list of handler objects; understanding linked structure helps reason about traversal and cycles
- `Interface` - all handlers implement a common interface enabling uniform treatment in the chain
- `Polymorphism` - each handler's `handle()` implementation differs; runtime dispatch selects the right behaviour

**Builds On This (learn these next):**
- `Servlet Filter API` - the canonical Java application of Chain of Responsibility; all Java web frameworks layer on this pattern
- `Spring Security Filter Chain` - enterprise-scale Chain of Responsibility for security concerns; 15+ handlers in a configurable ordered chain
- `Middleware Pattern` - the generalisation across frameworks (Express, ASP.NET, Django); all use Chain of Responsibility

**Alternatives / Comparisons:**
- `Command` - encapsulates a request as an object for queuing/logging; doesn't chain handlers
- `Decorator` - always delegates along the chain; doesn't conditionally stop propagation
- `Strategy` - selects one algorithm for a request; doesn't chain candidate algorithms

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Linked chain of handlers where each       │
│              │ decides to handle or forward a request    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single class with giant if-else ladder    │
│ SOLVES       │ couples all handling logic together       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Exclusive mode: one handles; Inclusive:   │
│              │ all process (middleware/filter variant)   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Request may be handled by one of several  │
│              │ handlers; set of handlers changes         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Every handler must always run (use        │
│              │ Observer or Decorator instead)            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Extensibility + SRP vs potential silent   │
│              │ drops and hard-to-trace chain traversal  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pass it down the line - who can          │
│              │  handle it steps forward."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Servlet Filters → Spring Security Chain   │
│              │ → Middleware Pattern                      │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When multiple handlers might handle a request, avoid embedding
all handling conditions in one place. Form a chain where each
handler either handles or passes to the next, keeping each
handler focused on one responsibility.

**Where else this pattern appears:**
- **Servlet/Spring filter chains:** Authentication, CORS,
  rate-limiting, and logging filters form a chain -- each
  either rejects the request or passes to the next filter.
- **Exception handling chains (try/catch):** Multiple catch
  blocks form a chain where each handles its specific exception
  type and falls through to more general handlers.
- **Customer support escalation:** Tier-1 support resolves
  common issues; unresolved tickets pass to Tier-2, then
  Tier-3 -- each level handles what it can and escalates the rest.

---

### 💡 The Surprising Truth

Spring Security is built almost entirely on Chain of
Responsibility: the `SecurityFilterChain` contains 15-30+
individual `Filter` implementations, each handling one
security concern. When you add `@EnableWebSecurity`, you
are instantiating a Chain of Responsibility with over a dozen
handlers. Yet security misconfiguration bugs -- where the
wrong filter is placed in the wrong order in the chain --
are among the most common Spring Security vulnerabilities.
The pattern's flexibility (any handler can be added anywhere)
is also its security risk (a misconfigured chain silently
skips critical checks).
---

### 🧠 Think About This Before We Continue

**Q1.** A Chain of Responsibility implements an HTTP rate limiter: each handler checks a different scope - per-IP, per-user, per-API-key, per-endpoint. In exclusive mode, the first scope that is exceeded rejects the request. But a requirement says: "if per-IP limit is exceeded AND per-user limit is NOT exceeded, the IP limit may be overridden for trusted users." This conditional override breaks the chain's clean sequential model. Design a solution - either modifying the chain structure or adding new metadata to the request - that handles this cross-handler dependency without coupling the IP handler to the user handler directly.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A processing pipeline uses an inclusive Chain of Responsibility (all handlers run). Handler 3 of 10 transforms the request payload (removing PII fields for compliance). Handler 7 needs the original PII-containing payload for an audit log. But handler 7 receives the already-stripped version. Trace the problem and describe two architectural approaches to solve this within the chain pattern - without breaking the chain of handlers or creating direct coupling between handler 3 and handler 7.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A logging system uses CoR: DEBUG
handler → INFO handler → WARN handler → ERROR handler →
FATAL handler. A requirement says: all WARN and above should
also be written to a separate audit log. Describe two ways
to implement this in the existing chain and state the trade-
off between modifying the chain structure versus adding
a branching handler.

*Hint: The How It Works section describes the pass/handle
decision. Consider whether a "broadcast" handler (handling
AND passing) fits the chain model, or whether an Observer
pattern layered over the chain would better serve the audit
requirement.*
