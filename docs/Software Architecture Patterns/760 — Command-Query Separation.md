---
layout: default
title: "Command-Query Separation"
parent: "Software Architecture Patterns"
nav_order: 760
permalink: /software-architecture/command-query-separation/
number: "760"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Tell Don't Ask, SOLID Principles, Object-Oriented Programming"
used_by: "API design, Domain Model, CQRS, Clean code"
tags: #intermediate, #architecture, #oop, #api-design, #cqrs
---

# 760 — Command-Query Separation

`#intermediate` `#architecture` `#oop` `#api-design` `#cqrs`

⚡ TL;DR — **Command-Query Separation (CQS)** states that every method should either be a **command** (changes state, returns nothing) OR a **query** (returns data, changes no state) — never both — making code predictable because a query call can never have unexpected side effects.

| #760 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Tell Don't Ask, SOLID Principles, Object-Oriented Programming | |
| **Used by:** | API design, Domain Model, CQRS, Clean code | |

---

### 📘 Textbook Definition

**Command-Query Separation (CQS)** (Bertrand Meyer, "Object-Oriented Software Construction," 1988): a principle that a function or method should be either a COMMAND that performs an action and returns nothing (returns void or unit), OR a QUERY that returns data without any observable side effects — but NOT both. Commands: change state. Queries: read state. Mixing them: dangerous side effects when code expects a side-effect-free query. Meyer's formulation: "Asking a question should not change the answer." Note: CQS is a method-level design principle (different from CQRS — Command Query Responsibility Segregation — which is an architectural pattern that scales CQS to the system level with separate models for reads and writes).

---

### 🟢 Simple Definition (Easy)

A light switch vs. a light sensor. Query: the light sensor reports "is it dark?" — it does NOT change the light state. You can call it a million times: same answer, no side effects. Command: the light switch changes the state (on/off) — it doesn't tell you what the state is, just changes it. Anti-CQS: a light switch that changes state AND returns the previous state. Now every time you check "what was it?" you accidentally flip the light.

---

### 🔵 Simple Definition (Elaborated)

`stack.pop()` in most languages violates CQS: it RETURNS the top element (query behavior) AND REMOVES it from the stack (command behavior). If you call `stack.pop()` just to check the top element, you changed the stack. CQS-compliant stack: `stack.peek()` (query: returns top, no mutation) and `stack.pop()` (command: removes top, returns nothing). Now you can safely call `peek()` repeatedly without side effects. Pop only when you intend to remove.

---

### 🔩 First Principles Explanation

**Why mixing commands and queries creates bugs and confusion:**

```
THE PROBLEM WITH MIXED METHODS:

  // MIXED (violates CQS):
  boolean saveAndValidate(Order order) {
      if (!order.isValid()) return false;
      repository.save(order);     // SIDE EFFECT: saves to database
      return true;                // RETURN VALUE: validation result
  }
  
  // Caller checks return value:
  if (saveAndValidate(order)) { ... }
  
  // Problem 1: Reader sees "if saveAndValidate(order)..." and thinks it's a pure check.
  // Actually: it SAVED to the database. Surprise side effect.
  
  // Problem 2: Can you call saveAndValidate() twice to check validation?
  // First call: validates AND saves. Second call: saves AGAIN (duplicate).
  
  // Problem 3: In tests, calling the "validation check" also saves — test contamination.
  
  // Problem 4: If save fails (exception), did validation pass?
  // Control flow becomes unpredictable.
  
CQS-COMPLIANT SEPARATION:

  // QUERY (no side effects):
  boolean isValid(Order order) { return order.validate().isEmpty(); }
  
  // COMMAND (no return value):
  void save(Order order) { repository.save(order); }
  
  // Caller explicitly sequences:
  if (isValid(order)) {
      save(order);
  }
  
  Benefits:
  1. isValid() called any number of times: no side effects.
  2. save() intent is clear: "I know this changes state."
  3. Tests: test validation with isValid(). Test saving with save(). Separately.
  4. Debug: side effects only happen at explicit Command calls.
  
COMMAND TYPES:

  Commands change state. They return void.
  They may throw exceptions on failure (exceptional condition).
  They should NOT return the new state (that's a CQS violation).
  
  void placeOrder(OrderCommand cmd)    // creates order
  void confirmPayment(PaymentId id)    // changes payment state
  void cancelOrder(OrderId id, Reason r) // changes order state
  void addItem(OrderId id, Item item)  // mutates order
  
QUERY TYPES:

  Queries return data. They have NO side effects.
  Idempotent: calling a query N times = same as calling once.
  No mutation, no logging of domain events, no writes.
  
  Order findOrder(OrderId id)             // returns order
  List<Order> findPendingOrders()         // returns list
  boolean isOrderEligibleForDiscount(id)  // returns boolean
  Money calculateShipping(Order order)    // computes, no mutation
  
CQS IN REST APIS:

  HTTP methods naturally align with CQS:
  
  COMMANDS (state-changing):          QUERIES (read-only):
  POST /orders                        GET /orders
  PUT /orders/{id}                    GET /orders/{id}
  DELETE /orders/{id}                 GET /orders?status=pending
  PATCH /orders/{id}/cancel
  
  CQS violation: GET /orders/next (returns the next order AND marks it as "in progress")
                 ← GET that has side effects is a CQS violation in REST too.
                 
  CQS-compliant: GET /orders?status=available (pure query)
                 POST /orders/{id}/claim (explicit command)
                 
EXCEPTIONS — WHEN CQS IS PRAGMATICALLY VIOLATED:

  1. stack.pop(): hard to make CQS-pure without awkward API.
     CQS-pure alternative: peek() + pop() (two calls).
     
  2. queue.poll(): removes and returns in one call.
     Concurrent context: between peek() and pop(), another thread could dequeue.
     Atomicity requires combining in some concurrency scenarios.
     
  3. CAS (Compare-And-Swap): atomically checks+changes state. Returns boolean.
     By definition: mixed. Necessary for concurrency.
     
  4. Builder: order.withItem(item) returns new order (immutable style).
     Each with() is functionally a command+query — but on IMMUTABLE objects:
     no state mutation, returns NEW object. Not a violation (object is immutable).
     
  RULE: Violate CQS intentionally and explicitly, not accidentally.
  
CQS vs. CQRS:

  CQS: Method-level principle. One class, methods segregated into commands/queries.
       The same class handles both, but each method is one or the other.
       
  CQRS: Architectural pattern. Separate MODELS (classes, databases, services) for
        write side and read side.
        
  CQRS is CQS scaled up:
    CQS:  Order.getTotal()  and  Order.cancel()  (same class, separate methods)
    CQRS: OrderWriteModel (aggregates, commands) and OrderReadModel (DTOs, queries)
          stored in different databases, served by different services.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT CQS:
- `getUser()` has a hidden side effect (logs access, increments view count) — callers get surprising behavior
- Tests: calling "validation" triggers database writes — tests contaminate each other

WITH CQS:
→ Queries safe to call anywhere: no side effects, predictable
→ Commands explicitly signal "this will change state" — readers know to expect side effects

---

### 🧠 Mental Model / Analogy

> A library catalog vs. checking out a book. Query: searching the catalog tells you where the book is — zero times, ten times, doesn't matter. The catalog is never changed by searching it. Command: checking out a book changes the library's state (book is now "on loan"). You know when you're searching vs. checking out — they're different actions, different interfaces. Anti-CQS: a "search" that also automatically reserves the book. Now every search has side effects.

"Searching the catalog (no side effects)" = pure query
"Checking out a book (changes state)" = command
"Search that auto-reserves (unexpected side effect)" = CQS violation
"Different interfaces for search vs. checkout" = explicit separation of queries and commands

---

### ⚙️ How It Works (Mechanism)

```
CQS IDENTIFICATION PATTERN:

  For each method, ask two questions:
  
  1. Does it change observable state? (writes DB, modifies fields, triggers side effects)
     YES: it's a COMMAND. Should return void.
     
  2. Does it return data?
     YES: it's a QUERY. Should have no side effects.
     
  If BOTH answers are yes: CQS violation. Split it.
  
  SPLITTING STRATEGY:
    Mixed method: ResultType doSomething(Params)
    
    Split 1: void doCommand(Params)        // command: does the action, returns nothing
    Split 2: ResultType queryResult(Params) // query: returns what you need, no side effects
    
    Caller: doCommand(params); ResultType r = queryResult(params);
```

---

### 🔄 How It Connects (Mini-Map)

```
Methods that both change state and return data (mixed responsibility)
        │
        ▼ (separate command from query)
Command-Query Separation ◄──── (you are here)
(every method: either command OR query, not both)
        │
        ├── CQRS: CQS scaled to architecture (separate write/read models)
        ├── Tell Don't Ask: TDA = tell objects to command themselves; CQS = shape of those methods
        ├── REST API design: HTTP verbs naturally map (GET=query, POST/PUT/DELETE=command)
        └── Functional Programming: pure functions (no side effects) are the CQS query ideal
```

---

### 💻 Code Example

```java
// CQS VIOLATION — method that both returns AND mutates:
class TokenService {
    // PROBLEM: This is a query (returns token) AND a command (creates + saves token):
    String getOrCreateToken(UserId userId) {
        return tokenCache.computeIfAbsent(userId, id -> {
            String token = generateToken();
            tokenRepository.save(new Token(id, token, Instant.now())); // SIDE EFFECT!
            return token;
        });
    }
}
// Caller says "get token" — might actually CREATE one. Unexpected.

// ────────────────────────────────────────────────────────────────────

// CQS-COMPLIANT:
class TokenService {
    // COMMAND: creates a token (void — does not return):
    void createToken(UserId userId) {
        String token = generateToken();
        tokenRepository.save(new Token(userId, token, Instant.now()));
    }
    
    // QUERY: retrieves an existing token (no side effects):
    Optional<String> getToken(UserId userId) {
        return tokenRepository.findActiveToken(userId)
            .map(Token::value);
    }
}

// Caller sequence is explicit:
class AuthService {
    String ensureToken(UserId userId) {
        return tokenService.getToken(userId).orElseGet(() -> {
            tokenService.createToken(userId);      // explicit command
            return tokenService.getToken(userId)   // explicit query
                .orElseThrow(() -> new TokenCreationException(userId));
        });
    }
}
// Two calls, but behavior is transparent. No hidden side effects in any query.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CQS means commands can never return any value | Commands can return acknowledgment IDs or error information in some pragmatic designs (e.g., HTTP 201 Created with Location header). The strict interpretation (commands return void) is pure CQS. The pragmatic version allows commands to return only IDs or error status. The key: commands should never return the domain state (that's a query's job) |
| CQS and CQRS are the same thing | CQS is a method-level design principle (Bertrand Meyer, 1988). CQRS is an architectural pattern (Greg Young, ~2010) that separates entire object models — write models and read models. CQRS is inspired by CQS but is dramatically more complex: different databases, eventual consistency, event sourcing. Many systems apply CQS at the method level without ever needing CQRS architecture |
| A query that caches the result violates CQS | Caching is considered a benign side effect for CQS purposes. CQS's prohibition is on OBSERVABLE state changes — changes that affect the result of future queries or are visible to other components. An in-memory cache that doesn't change domain state is acceptable. Logging is similarly acceptable |

---

### 🔥 Pitfalls in Production

**REST endpoint with GET that has side effects:**

```java
// CQS VIOLATION in REST API — GET with side effect:
@GetMapping("/orders/next-available")
Order getNextAvailableOrder() {
    Order order = orderQueue.poll(); // DEQUEUES (command) and returns (query)!
    return order;                    // Clients calling GET expecting to "see" next order
                                     // actually CONSUME it (removes from queue).
}
// Load balancer retries GET on timeout → order consumed twice.
// Monitoring probes GET endpoint → consumes orders.
// Developer reads "GET" → assumes safe to call for inspection.

// CQS-COMPLIANT:
@GetMapping("/orders/next-available")
Optional<Order> peekNextAvailableOrder() {
    return orderQueue.peek(); // QUERY: no mutation, just reads
}

@PostMapping("/orders/{id}/claim")
void claimOrder(@PathVariable String id) {
    orderService.claim(OrderId.of(id)); // COMMAND: explicit intent to consume
}
// Now GET is safe to call by monitoring, retries, inspections.
// Only explicit POST /claim actually dequeues.
```

---

### 🔗 Related Keywords

- `CQRS` — Command Query Responsibility Segregation: CQS scaled to architecture level
- `Tell Don't Ask` — TDA tells objects to command themselves; CQS shapes those method signatures
- `REST API design` — HTTP methods naturally embody CQS (GET=query, POST/PUT/DELETE=command)
- `Functional Programming` — pure functions are the theoretical ideal of CQS queries
- `Domain Model` — CQS helps structure domain object methods (commands change state, queries read it)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Every method: command (changes state,     │
│              │ returns void) OR query (returns data,     │
│              │ no side effects). Never both.             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing domain object methods; REST API │
│              │ endpoints; any method that currently both │
│              │ returns data AND has side effects         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Concurrency atomicity requires it (CAS,  │
│              │ atomic dequeue); pragmatic violations are │
│              │ fine if intentional and documented       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Search the library catalog safely a      │
│              │  hundred times; only checkout actually   │
│              │  changes the library's state."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Tell Don't Ask →                   │
│              │ Functional Programming → REST API design  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `Iterator.next()` violates CQS: it returns the next element (query) AND advances the iterator position (command). Should the Iterator pattern be redesigned to be CQS-compliant? What would CQS-compliant iteration look like (`peek()` + `advance()`)? What are the trade-offs of the current design vs. the CQS-pure design, especially in concurrent contexts?

**Q2.** An event-sourced system uses `aggregate.handle(command)` which: (a) validates the command, (b) applies the state change, (c) returns the resulting domain event. This is technically a CQS violation (command that returns data). Is this acceptable? How do event-sourced systems reconcile the need to capture the resulting event with CQS? What does Greg Young say about CQS vs. CQRS in the context of event sourcing?
