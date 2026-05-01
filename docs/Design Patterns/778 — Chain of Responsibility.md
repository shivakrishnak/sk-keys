---
layout: default
title: "Chain of Responsibility"
parent: "Design Patterns"
nav_order: 778
permalink: /design-patterns/chain-of-responsibility/
number: "778"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Decorator Pattern, Linked Lists"
used_by: "HTTP filter chains, Middleware, Event handling, Approval workflows"
tags: #intermediate, #design-patterns, #behavioral, #oop, #pipeline, #event-handling
---

# 778 — Chain of Responsibility

`#intermediate` `#design-patterns` `#behavioral` `#oop` `#pipeline` `#event-handling`

⚡ TL;DR — **Chain of Responsibility** passes a request along a chain of handlers — each handler decides to handle the request, pass it to the next handler, or both — decoupling senders from receivers and allowing multiple handlers to participate in request processing.

| #778 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Decorator Pattern, Linked Lists | |
| **Used by:** | HTTP filter chains, Middleware, Event handling, Approval workflows | |

---

### 📘 Textbook Definition

**Chain of Responsibility** (GoF, 1994): a behavioral design pattern that avoids coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. The receiving objects are chained, and the request is passed along the chain until an object handles it. Each handler in the chain has a reference to the next handler. GoF intent: "Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it." Two variants: (1) **Pure chain**: only ONE handler handles the request (like exception handling — caught at first matching catch); (2) **Modified chain**: MULTIPLE handlers may process the request (Servlet filter chain — all filters run).

---

### 🟢 Simple Definition (Easy)

A customer support escalation. You contact Tier 1 support (FAQ bot). It can't solve your problem — passes to Tier 2 (support agent). Agent can't solve it — passes to Tier 3 (technical specialist). Specialist can't solve it — passes to Tier 4 (engineering). Each level tries to handle. If they can, they respond to you. If not, they pass to the next. You don't know who will actually handle your request — you just submitted it to the chain.

---

### 🔵 Simple Definition (Elaborated)

Servlet filter chain: `LoggingFilter → AuthFilter → RateLimitFilter → CompressionFilter → Servlet`. Each filter processes the request, then calls `chain.doFilter()` to pass to the next. All filters run (modified chain). Or: leave request blocked at AuthFilter if not authenticated (pure chain — doesn't proceed to servlet). Unlike the GoF pure chain, HTTP filter chains always call the next handler unless explicitly stopped. Chain of Responsibility enables this flexible, ordered pipeline of handlers.

---

### 🔩 First Principles Explanation

**How the chain is built and how pass-through vs. stop decisions work:**

```
CHAIN OF RESPONSIBILITY STRUCTURE:

  // HANDLER INTERFACE:
  abstract class RequestHandler {
      protected RequestHandler next;        // link to next handler
      
      RequestHandler setNext(RequestHandler next) {
          this.next = next;
          return next;              // fluent: allows chaining setNext().setNext()...
      }
      
      abstract void handle(Request request);
      
      // Helper to pass to next:
      protected void passToNext(Request request) {
          if (next != null) next.handle(request);
          else System.out.println("End of chain: unhandled request");
      }
  }
  
  // CONCRETE HANDLERS:
  class AuthHandler extends RequestHandler {
      @Override
      void handle(Request request) {
          if (request.getToken() == null || !isValid(request.getToken())) {
              request.setResponse(Response.unauthorized());
              return;  // STOP: don't pass to next — request blocked
          }
          passToNext(request);  // PASS: auth passed, next handler runs
      }
  }
  
  class RateLimitHandler extends RequestHandler {
      @Override
      void handle(Request request) {
          if (rateLimiter.isExceeded(request.getClientId())) {
              request.setResponse(Response.tooManyRequests());
              return;  // STOP: rate limit hit
          }
          passToNext(request);  // PASS
      }
  }
  
  class LoggingHandler extends RequestHandler {
      @Override
      void handle(Request request) {
          log.info("Request: {} {} from {}", request.getMethod(), 
                   request.getPath(), request.getClientId());
          passToNext(request);  // ALWAYS pass (logging doesn't block)
          log.info("Response: {}", request.getResponse().getStatus());
      }
  }
  
  class BusinessHandler extends RequestHandler {
      @Override
      void handle(Request request) {
          // Actual business logic:
          request.setResponse(businessService.process(request));
          // No passToNext — last in chain
      }
  }
  
  // BUILD THE CHAIN (fluent):
  RequestHandler chain = new LoggingHandler();
  chain.setNext(new AuthHandler())
       .setNext(new RateLimitHandler())
       .setNext(new BusinessHandler());
  
  // INVOKE:
  chain.handle(incomingRequest);
  
  // Flow:
  // LoggingHandler → passes → AuthHandler (check auth)
  //   If invalid: STOP, return 401
  //   If valid  → passes → RateLimitHandler (check rate)
  //     If exceeded: STOP, return 429
  //     If ok → passes → BusinessHandler (process)
  
PURE CHAIN (Java exception handling as analogy):

  try {
      ...
  } catch (SpecificException e) {   // Handler 1: handles specific exception → STOP
      ...
  } catch (GeneralException e) {    // Handler 2: handles general → STOP (only if H1 didn't)
      ...
  } catch (Exception e) {           // Handler 3: fallback handler
      ...
  }
  // PURE CHAIN: only ONE catch block executes.
  
APPROVAL WORKFLOW — CLASSIC CHAIN:

  abstract class Approver {
      protected Approver next;
      protected final String name;
      protected final double maxApprovalAmount;
      
      void setNext(Approver next) { this.next = next; }
      
      void approve(PurchaseRequest request) {
          if (request.getAmount() <= maxApprovalAmount) {
              System.out.println(name + " approved $" + request.getAmount());
          } else if (next != null) {
              next.approve(request);
          } else {
              System.out.println("No one can approve $" + request.getAmount());
          }
      }
  }
  
  class Manager extends Approver {
      Manager() { super("Manager", 1_000); }   // can approve up to $1,000
  }
  class Director extends Approver {
      Director() { super("Director", 10_000); }
  }
  class CEO extends Approver {
      CEO() { super("CEO", 1_000_000); }
  }
  
  // Chain: Manager → Director → CEO
  Approver manager = new Manager();
  Approver director = new Director();
  Approver ceo = new CEO();
  manager.setNext(director);
  director.setNext(ceo);
  
  manager.approve(new PurchaseRequest(500));       // Manager approves
  manager.approve(new PurchaseRequest(5_000));     // Director approves
  manager.approve(new PurchaseRequest(500_000));   // CEO approves
  manager.approve(new PurchaseRequest(5_000_000)); // No one can approve
  
CHAIN vs DECORATOR vs COMMAND:

  Chain of Responsibility:
  - Request travels down chain; handlers may stop it.
  - Senders don't know which handler will respond.
  - Handler can STOP the chain (don't call next).
  
  Decorator:
  - ALL layers execute (no stopping).
  - Same component interface.
  - Adds behavior — doesn't have "handle or pass" logic.
  
  Command:
  - Encapsulates a request as an object.
  - One executor executes the command.
  - Chain of Responsibility may handle a queue of Commands.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Chain of Responsibility:
- One big handler with if/else/switch: "if auth fails... else if rate limit... else if logged in..."
- Adding new step: modify the big handler (OCP violation)

WITH Chain of Responsibility:
→ Each step is a separate handler class. Add new step: add new handler, insert in chain position
→ Handlers are independently testable. Client submits to chain — doesn't know which handler responds.

---

### 🧠 Mental Model / Analogy

> A help desk ticketing system with escalation levels. Level 1 tech: can solve password resets. Level 2: can solve software issues. Level 3: can solve hardware issues. Level 4 engineering: can solve everything. A ticket enters at Level 1. If solvable there — solved. If not — escalated to Level 2. And so on. You (sender) submit to the chain — you don't pick who handles. Each level decides: can I handle this? If yes: handle. If no: escalate.

"Ticket sender" = client (doesn't know who will handle)
"Each support level" = handler in chain
"Can I handle this?" = handler's condition check
"Escalate" = call next.handle(request)
"Solved at Level 2" = chain stops after Level 2 handles

---

### ⚙️ How It Works (Mechanism)

```
CHAIN:

  handler1 → handler2 → handler3 → ... → handlerN → (end of chain)
  
  Each handler:
  - If can handle: handle (and optionally pass to next)
  - If cannot handle: pass to next
  - If no next: request unhandled (or default handling)
```

---

### 🔄 How It Connects (Mini-Map)

```
Request with multiple potential handlers; sender doesn't know which handles
        │
        ▼
Chain of Responsibility ◄──── (you are here)
(linked handlers; each decides to handle/pass; stops or continues)
        │
        ├── Decorator: all layers always execute (vs CoR: may stop at any handler)
        ├── Command: CoR can process a queue of Command objects
        ├── Mediator: centralized coordination (vs CoR: decentralized chain)
        └── Servlet Filter Chain: HTTP-level CoR (all filters run unless stopped)
```

---

### 💻 Code Example

```java
// Validation chain for order processing:
abstract class OrderValidator {
    protected OrderValidator next;
    
    OrderValidator setNext(OrderValidator next) { this.next = next; return next; }
    
    abstract ValidationResult validate(Order order);
    
    protected ValidationResult passToNext(Order order) {
        return next != null ? next.validate(order) : ValidationResult.valid();
    }
}

class StockValidator extends OrderValidator {
    public ValidationResult validate(Order order) {
        for (OrderItem item : order.getItems()) {
            if (!inventory.hasStock(item.getSku(), item.getQuantity())) {
                return ValidationResult.error("Out of stock: " + item.getSku());
            }
        }
        return passToNext(order);  // all items in stock → pass to next
    }
}

class PriceValidator extends OrderValidator {
    public ValidationResult validate(Order order) {
        if (order.getTotal().compareTo(BigDecimal.ZERO) <= 0) {
            return ValidationResult.error("Order total must be positive");
        }
        return passToNext(order);
    }
}

class FraudValidator extends OrderValidator {
    public ValidationResult validate(Order order) {
        if (fraudDetectionService.isSuspicious(order)) {
            return ValidationResult.error("Suspicious order flagged for review");
        }
        return passToNext(order);
    }
}

// Build chain:
OrderValidator chain = new StockValidator();
chain.setNext(new PriceValidator()).setNext(new FraudValidator());

// Process:
ValidationResult result = chain.validate(incomingOrder);
if (result.isValid()) orderService.process(incomingOrder);
else log.warn("Order rejected: {}", result.getError());
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Chain of Responsibility always stops at the first handler that handles the request | This is the "pure chain" variant (GoF default). But many real implementations are "modified chains" where ALL handlers in the chain process the request (Servlet filter chains, Express.js middleware). In the modified chain, a handler only stops the chain by NOT calling next — otherwise all handlers run. |
| Chain of Responsibility requires a linked list of handler objects | The handlers can be stored in a `List<Handler>` and iterated in order — this is common in modern implementations. Many frameworks (Express, Koa middleware) use array-based chains internally. The key is ordered, sequential processing where each handler decides to proceed or not. |
| The client must know the chain structure | The client should only know the entry point of the chain. The chain building (which handler comes first, what order) should be configured externally. In Spring, filter chains are configured in `SecurityFilterChain`. In express.js, `app.use()` adds handlers. Client: just call `chain.handle(request)`. |

---

### 🔥 Pitfalls in Production

**Unhandled request silently falls through the chain:**

```java
// ANTI-PATTERN: No fallback at end of chain — request silently dropped:
class BusinessHandler extends RequestHandler {
    void handle(Request request) {
        if (isForThisService(request)) {
            request.setResponse(process(request));
        }
        // else: does nothing! If request isn't for this service, it's silently dropped.
        // No call to passToNext — chain ends here without handling.
    }
}

// Client gets null response — no error, no indication of failure.

// FIX: Always have a fallback/default handler at the end of the chain:
class DefaultHandler extends RequestHandler {
    void handle(Request request) {
        // Explicit "unhandled" case:
        log.warn("Unhandled request: {} {}", request.getMethod(), request.getPath());
        request.setResponse(Response.notFound("No handler found for this request"));
        // No passToNext — this is the terminal handler
    }
}

// Build chain with fallback:
chain.setNext(new AuthHandler())
     .setNext(new RateLimitHandler())
     .setNext(new BusinessHandler())
     .setNext(new DefaultHandler());  // ← always present, always handles "unhandled"
```

---

### 🔗 Related Keywords

- `Decorator Pattern` — all wrappers always execute; Chain: may stop at any handler
- `Servlet Filter Chain` — standard Chain of Responsibility in HTTP (all filters run)
- `Mediator Pattern` — central coordinator (vs Chain: decentralized sequential chain)
- `Command Pattern` — encapsulates requests; Chain may process Command objects
- `Event Bubbling` — DOM event propagation is a Chain of Responsibility from child to parent

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Linked handlers process a request in      │
│              │ order. Each: handle or pass to next.      │
│              │ Decouple sender from any specific handler.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple objects may handle a request;    │
│              │ handler isn't known upfront; ordered     │
│              │ pipeline: auth → rate-limit → business   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ All handlers must process every request  │
│              │ (use Decorator instead); debugging chain │
│              │ execution order is opaque               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Help desk escalation: Level 1 tries →   │
│              │  escalates → Level 2 tries → escalates  │
│              │  until someone resolves the ticket."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Decorator Pattern → Servlet Filter Chain →│
│              │ Command Pattern → Mediator Pattern        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Security's `SecurityFilterChain` is a Chain of Responsibility with 15+ filters in a specific order: `SecurityContextPersistenceFilter → UsernamePasswordAuthenticationFilter → BasicAuthenticationFilter → ExceptionTranslationFilter → FilterSecurityInterceptor → ...`. The order matters — ExceptionTranslationFilter must come before FilterSecurityInterceptor to catch its exceptions. How do you control filter ordering in Spring Security? What would happen if `FilterSecurityInterceptor` (authorization check) ran BEFORE `BasicAuthenticationFilter` (authentication)?

**Q2.** Node.js Express middleware is a Chain of Responsibility: `app.use(logger); app.use(authenticate); app.use('/api', apiRouter)`. Each middleware calls `next()` to pass to the next. If a middleware throws an error, Express uses a special error-handling middleware `(err, req, res, next)`. How does error propagation work in Express's chain? How does this compare to Java's Servlet filter chain's exception handling? What is the "express.js next(err)" pattern and which pattern does it implement?
