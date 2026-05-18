---
id: DPT-041
title: "Decorator vs Proxy vs Adapter"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-015, DPT-018, DPT-012
used_by: DPT-064
related: DPT-015, DPT-018, DPT-012, DPT-013, DPT-016
tags:
  - concept
  - comparison
  - structural
  - advanced
  - wrapper-patterns
  - design-decisions
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/design-patterns/decorator-vs-proxy-vs-adapter/
---

⚡ TL;DR - Decorator, Proxy, and Adapter all wrap an object,
but serve different intents: Decorator ADDS behavior to
an object, Proxy CONTROLS ACCESS to an object, Adapter
TRANSLATES one interface to another.

| #41 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-015, DPT-018, DPT-012 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-015, DPT-018, DPT-012, DPT-013, DPT-016 | |

---

### 🔥 Why This Comparison Matters

Three of the most commonly confused patterns in GoF.
All three wrap another object. All three use delegation.
A senior engineer can name any three differences between
them in 30 seconds. A junior engineer says "they're all
wrappers, aren't they?"

The confusion costs real design decisions:
- Using Proxy when Decorator is needed: the Proxy intercepts
  but does not compose, limiting stacking.
- Using Adapter when Decorator is needed: adapter changes
  the interface instead of preserving it.
- Using Decorator when Proxy is needed: loses the
  "access control" semantic, making intent unclear.

---

### 📘 Core Distinction

| Pattern | Intent | Changes interface? | Adds behavior? | Controls access? |
|---|---|---|---|---|
| **Decorator** | Add behavior dynamically | No (same interface) | Yes | No |
| **Proxy** | Control access to the real object | No (same interface) | No (or minimal) | Yes |
| **Adapter** | Make incompatible interfaces compatible | Yes | No | No |

---

### ⏱️ One-Paragraph Summary Per Pattern

**Decorator:**
Wraps the same interface. The wrapper adds behavior BEFORE
or AFTER delegating to the wrapped object. Multiple decorators
can be stacked (chained). Each layer adds one concern.
The caller uses the outermost wrapper and sees the same
interface. `Java.io.BufferedInputStream(new FileInputStream(...))`
is Decorator: `BufferedInputStream` adds buffering to
any `InputStream`.

**Proxy:**
Wraps the same interface. The proxy controls WHETHER
and HOW the real object is accessed: lazy initialization,
access control, caching, logging, remote invocation.
The caller does not know they are talking to a proxy.
Spring's `@Transactional` creates a proxy around the
service bean - the proxy begins/commits transactions;
the real bean handles business logic.

**Adapter:**
Wraps an INCOMPATIBLE object and presents a different
interface that the caller expects. The adapter translates
between two interfaces that were not designed to work
together. `Arrays.asList()` adapts an array to a `List`.
`InputStreamReader(InputStream)` adapts a byte stream
to a character stream.

---

### 🔩 First Principles

**WHY ALL THREE USE DELEGATION:**
Delegation is the universal mechanism for "adding behavior
to an existing object without modifying it." The variation
is in the PURPOSE:
- Decorator: "I extend you"
- Proxy: "I gate you"
- Adapter: "I translate you"

**INTERFACE RULE:**
- Decorator: caller interface = real object interface = wrapper interface.
  Same type. Stackable.
- Proxy: caller interface = real object interface.
  Same type. Usually not stacked.
- Adapter: caller interface DIFFERS from adaptee interface.
  Translation layer.

**STACKING BEHAVIOR:**
Only Decorator is designed to stack (multiple layers,
each adding one concern). Proxy can technically stack
but the intent is singular control. Adapter bridges
one incompatibility - stacking adapters indicates
a design problem.

---

### 🧪 Recognition Test

Given a wrapper class, ask THREE questions:
1. Does it CHANGE the interface? → Adapter
2. Does it ADD behavior ALWAYS (before/after every call)? → Decorator
3. Does it CONTROL access (decide whether to call, cache result, lazy-init)? → Proxy

---

### 🧠 Mental Models

**Decorator → LAYERS OF CLOTHING:**
T-shirt (base) → sweater (warmth decorator) → raincoat
(waterproof decorator). Same person underneath. Each
layer adds something. All layers share the same interface
("wearable"). You can add or remove layers without
changing the person.

**Proxy → SECRETARY / GATEKEEPER:**
The secretary (proxy) controls access to the executive
(real object). Screens calls (access control). Defers
meetings to next week (lazy initialization). Takes
messages (caching). The caller talks to the secretary;
the secretary manages when/whether the executive is
involved.

**Adapter → POWER ADAPTER:**
You have a US plug (incompatible). The hotel has EU
outlets. The adapter (physical or code) translates between
the two incompatible interfaces. After the adapter:
your US device works in a EU socket. The interfaces
were different; the adapter bridges them.

---

### 📶 Deep Dive - Key Distinctions

**DECORATOR vs PROXY:**
Both same interface. Both delegate. The distinguishing
question: "Is the primary purpose to ADD BEHAVIOR or
to CONTROL ACCESS?"

`java.io.BufferedInputStream`: adds buffering. No access
control. DECORATOR.

Spring's `@Transactional` proxy: wraps the service.
Begins a transaction before the method; commits/rolls
back after. The transaction demarcation IS access control
(controls the execution context). PROXY.

Spring's `@Cacheable` proxy: checks if result is cached.
Returns cached result (skips the real call entirely).
Decides WHETHER to call the real object. PROXY.

A logging wrapper that always calls the real object and
logs before/after: DECORATOR (adds logging behavior,
never controls access).

**DECORATOR vs ADAPTER:**
The interface rule is definitive. If the wrapper class
implements the same interface as the wrapped class:
Decorator (or Proxy). If the wrapper implements a
DIFFERENT interface: Adapter.

`Collections.synchronizedList(list)`: wraps a `List`,
returns a `List`. Same interface. Access is controlled
(synchronized). PROXY (or Decorator - the distinction
blurs here; most engineers call it Decorator with
a thread-safety concern).

`InputStreamReader(InputStream in)`: wraps an `InputStream`
(byte stream), returns a `Reader` (character stream).
Different interface. ADAPTER.

**PROXY vs ADAPTER:**
Proxy: same interface, controls access.
Adapter: different interface, translates.

A remote service proxy (stub): the caller calls the stub
with the same interface as if the service were local.
The stub translates to network calls internally. Some
call this Proxy (same interface); others call it Adapter
(local-to-remote translation). The GoF calls it Remote
Proxy. The interface-preservation criterion: Proxy.

---

### ⚙️ How Each Works (Mechanism)

```
Decorator (same interface, added behavior):
┌─────────────────────────────────────────────┐
│ Caller → LoggingDecorator → CachingDecorator │
│          → RateLimiterDecorator → RealService│
│ All implement: Service interface             │
│ Each layer adds one cross-cutting concern   │
└─────────────────────────────────────────────┘

Proxy (same interface, controlled access):
┌─────────────────────────────────────────────┐
│ Caller → @Transactional Proxy → RealService │
│          "begin tx" → real.method() →       │
│          "commit/rollback"                   │
│ Proxy may NOT call real service (cache hit) │
└─────────────────────────────────────────────┘

Adapter (different interfaces):
┌─────────────────────────────────────────────┐
│ Caller (expects Reader interface)            │
│    → InputStreamReader (Adapter)             │
│         → InputStream (Adaptee)             │
│ Caller interface ≠ Adaptee interface        │
└─────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Decorator (same interface, stacked behaviors):**

```java
// Decorator: add logging + caching to a service
interface OrderFetcher {
    List<Order> fetchByCustomer(String customerId);
}

class RealOrderFetcher implements OrderFetcher {
    @Override
    public List<Order> fetchByCustomer(String customerId) {
        return orderRepository.findByCustomerId(customerId);
    }
}

// DECORATOR: adds caching behavior
class CachingOrderFetcher implements OrderFetcher {
    private final OrderFetcher delegate; // wraps OrderFetcher
    private final Cache<String, List<Order>> cache;

    CachingOrderFetcher(OrderFetcher delegate) {
        this.delegate = delegate;
    }

    @Override
    public List<Order> fetchByCustomer(String customerId) {
        return cache.computeIfAbsent(customerId,
            k -> delegate.fetchByCustomer(k)); // adds behavior
    }
}

// DECORATOR: adds logging (stackable - same interface)
class LoggingOrderFetcher implements OrderFetcher {
    private final OrderFetcher delegate;

    LoggingOrderFetcher(OrderFetcher delegate) {
        this.delegate = delegate;
    }

    @Override
    public List<Order> fetchByCustomer(String customerId) {
        log.debug("Fetching orders for {}", customerId);
        List<Order> result = delegate.fetchByCustomer(customerId);
        log.debug("Fetched {} orders", result.size());
        return result;
    }
}

// Stacked: logging > caching > real
OrderFetcher fetcher =
    new LoggingOrderFetcher(
        new CachingOrderFetcher(
            new RealOrderFetcher()));
```

**Example 2 - Proxy (same interface, access control):**

```java
// PROXY: Spring @Transactional is a generated proxy
// You call: orderService.placeOrder(order)
// Spring calls: proxy.placeOrder(order)
//   proxy: begin transaction
//   proxy: realService.placeOrder(order)
//   proxy: commit (or rollback on exception)

// Simplified manual proxy:
class TransactionProxy implements OrderService {
    private final OrderService realService;
    private final TransactionManager txManager;

    TransactionProxy(OrderService real, TransactionManager tx) {
        this.realService = real;
        this.txManager   = tx;
    }

    @Override
    public void placeOrder(Order order) {
        TransactionStatus tx = txManager.beginTransaction();
        try {
            realService.placeOrder(order);
            // may not be called if guard fails
            txManager.commit(tx);
        } catch (Exception e) {
            txManager.rollback(tx);
            throw e;
        }
    }
}
// Proxy CONTROLS the context (transaction) around the call
// Proxy may also NOT call the real service (access denied, cache hit)
```

**Example 3 - Adapter (different interfaces):**

```java
// ADAPTER: old Logger interface, new SLF4J expected

interface OldLogger {          // old, incompatible interface
    void writeLog(int level, String msg);
    void writeError(Throwable t, String ctx);
}

// New code expects SLF4J Logger
interface Slf4jLogger {
    void info(String msg);
    void error(String msg, Throwable t);
}

// ADAPTER: wraps OldLogger, presents Slf4jLogger interface
class OldLoggerAdapter implements Slf4jLogger {
    private final OldLogger adaptee; // wraps incompatible type

    OldLoggerAdapter(OldLogger adaptee) {
        this.adaptee = adaptee;
    }

    @Override
    public void info(String msg) {
        adaptee.writeLog(1, msg); // translate: info → level 1
    }

    @Override
    public void error(String msg, Throwable t) {
        adaptee.writeError(t, msg); // translate: error → writeError
    }
}
// Interfaces changed: Slf4jLogger ≠ OldLogger → ADAPTER
```

---

### ⚖️ Decision Guide

**Ask these questions in order:**

1. **Does the wrapper change the interface?**
   YES → ADAPTER (translate between incompatible interfaces)

2. **Does the wrapper ALWAYS call the real object (just before/after)?**
   YES → DECORATOR (adds behavior, always delegates)

3. **Does the wrapper decide WHETHER to call the real object?**
   YES → PROXY (controls access, may skip, cache, lazily init)

**Blurry cases:**
- Spring's `@Cacheable` proxy: adds caching behavior (Decorator-like)
  BUT may skip the real call (Proxy behavior). Call it Proxy
  because the "may not call" behavior is the dominant concern.
- `Collections.synchronizedList()`: adds synchronization
  (Decorator behavior) around every call (no skipping).
  Call it Decorator (adds thread-safety behavior).
- JDK's `java.lang.reflect.Proxy` + `InvocationHandler`:
  depending on what the handler does - access control → Proxy,
  always-add-behavior → Decorator.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| AOP (Aspect-Oriented) creates Decorators | AOP (Spring's `@Transactional`, `@Cacheable`, `@Async`) creates PROXIES: they control access (transaction context, cache lookup, async execution), not just add behavior. Key difference: AOP advices can skip the real method (proceed() not called), which is Proxy behavior, not Decorator |
| Proxy and Decorator are interchangeable | Decorator is designed for stacking (multiple layers). Proxy is designed for a singular control mechanism. Stacking transaction proxies around transaction proxies is usually wrong; stacking logging decorators around caching decorators around rate-limiting decorators is designed behavior |
| You need a Proxy when you want lazy initialization | Lazy initialization (create the real object only when first used) IS a specific Proxy type (Virtual Proxy). The proxy holds a null reference, creates the real object on first call, then delegates. Hibernate's lazy-loaded entities are Virtual Proxies |
| Adapter and Facade are the same | Facade simplifies a complex subsystem by providing a simplified interface (no object wrapping, just orchestration). Adapter wraps one specific object to translate its interface. Facade: simplification. Adapter: translation |

---

### 🚨 Failure Modes & Diagnosis

**Self-Invocation Bypasses Spring Proxy (Missing Proxy)**

**Symptom:**
Method `A` calls method `B` in the same class. `B` is
annotated `@Transactional`. The transaction is NOT
started - no transaction in B's context.

**Root Cause:**
Spring's transaction proxy is on the OUTER bean. When
`A` calls `this.B()`, it bypasses the proxy (internal
call). The proxy's transaction advice is never invoked.

**Diagnosis:**
Check: is the `@Transactional` method called from the
same class? If yes: self-invocation bypasses the proxy.

**Fix:**
```java
// BAD: self-invocation bypasses proxy
@Service
class OrderService {
    void process(Order o) {
        this.save(o);  // bypasses @Transactional proxy
    }

    @Transactional
    void save(Order o) { ... }
}

// FIX option 1: inject self (ugly but works)
@Service
class OrderService {
    @Autowired
    private OrderService self; // inject own proxy

    void process(Order o) {
        self.save(o);  // calls through proxy
    }

    @Transactional
    void save(Order o) { ... }
}

// FIX option 2: move @Transactional method to a separate service
```

---

### 🔗 Related Keywords

**All three patterns:**
- `Decorator` - DPT-015
- `Proxy` - DPT-018
- `Adapter` - DPT-012

**Related structural patterns:**
- `Facade` - DPT-016: simplifies a subsystem (different from all three above)
- `Bridge` - DPT-013: separates abstraction from implementation hierarchy

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DECORATOR    │ Same interface + adds behavior always    │
│              │ Stackable. java.io streams.              │
├──────────────┼──────────────────────────────────────────┤
│ PROXY        │ Same interface + controls access         │
│              │ May skip real call. @Transactional.      │
├──────────────┼──────────────────────────────────────────┤
│ ADAPTER      │ DIFFERENT interface + translates         │
│              │ InputStreamReader. Arrays.asList().      │
├──────────────┼──────────────────────────────────────────┤
│ DECISION     │ 1. Changes interface? → ADAPTER          │
│              │ 2. Always delegates? → DECORATOR         │
│              │ 3. May skip real call? → PROXY           │
├──────────────┼──────────────────────────────────────────┤
│ AOP          │ @Transactional, @Cacheable = PROXIES     │
│              │ (control access, may skip real call)     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Anti-Patterns Overview → God Object      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. ADAPTER: the interface changes. `InputStreamReader`
   takes an `InputStream`, returns a `Reader`. Different
   input type, different return type. If interfaces differ:
   Adapter.
2. DECORATOR: same interface, always delegates, adds behavior.
   `BufferedInputStream(FileInputStream)` adds buffering to
   any InputStream. Stackable. If always-adds-behavior with
   same interface: Decorator.
3. PROXY: same interface, may NOT delegate (cache hit, access
   denied, lazy init). Spring's `@Transactional` begins a
   transaction then calls the real method. If controls access:
   Proxy. Self-invocation bypasses Spring proxies.

