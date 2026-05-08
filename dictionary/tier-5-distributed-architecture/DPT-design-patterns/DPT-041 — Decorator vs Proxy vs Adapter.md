---
layout: default
title: "Decorator vs Proxy vs Adapter"
parent: "Design Patterns"
nav_order: 41
permalink: /design-patterns/decorator-vs-proxy-vs-adapter/
id: DPT-041
category: Design Patterns
difficulty: ★★★
depends_on: Decorator, Proxy, Adapter, Object-Oriented Programming (OOP), Interface
used_by: Framework Design, AOP, API Integration, Cross-Cutting Concerns
related: Decorator, Proxy, Adapter, Bridge, Facade, Wrapper Pattern
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - tradeoff
---

# DPT-041 — Decorator vs Proxy vs Adapter

⚡ TL;DR — Decorator adds behaviour, Proxy controls access, Adapter changes interface — all wrap an object but for fundamentally different reasons.

| #801 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Decorator, Proxy, Adapter, Object-Oriented Programming (OOP), Interface | |
| **Used by:** | Framework Design, AOP, API Integration, Cross-Cutting Concerns | |
| **Related:** | Decorator, Proxy, Adapter, Bridge, Facade, Wrapper Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Three patterns share the same structural surface: they all wrap an object and delegate to it. At code-review time, a developer sees `class LoggingService { ... LoggingService(Service delegate) ... }` and cannot tell if this is adding logging behaviour (Decorator), controlling access (Proxy), or translating an interface (Adapter). The wrong mental model leads to wrong design decisions: does this wrapper affect all callers? Can we add more wrappers? Is the wrapped object interchangeable?

**THE BREAKING POINT:**
Without a clear mental model distinguishing the three, developers choose structurally based on what compiles rather than what's correct for their intent. A "logging wrapper" added to protect a service from overload (Proxy intent) may grow logging behaviour over time (Decorator intent) and then get repurposed to translate APIs (Adapter intent). The pattern becomes meaningless.

**THE INVENTION MOMENT:**
This is why understanding the distinction between all three matters. The intent — not the structure — defines the pattern.

---

### 📘 Textbook Definition

**Decorator:** Attaches additional responsibilities to an object dynamically. Decorator implements the same interface as the wrapped component and delegates to it while adding behaviour before or after. The client treats the decorator and the wrapped object identically.

**Proxy:** Provides a surrogate or placeholder to control access to an object. Proxy implements the same interface and delegates, but its purpose is access control, lazy initialisation, or remote access — not behaviour addition. The proxy manages how and when the subject is called.

**Adapter:** Converts the interface of a class into another interface clients expect. Adapter translates calls — the wrapped object has a DIFFERENT interface. The client's expectations and the adaptee's interface are incompatible; the adapter bridges them.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Decorator = "do more"; Proxy = "control when"; Adapter = "speak their language."

**One analogy:**
> **Decorator:** A travel mug (Decorator) wraps a coffee cup. Same liquid — but now it's insulated and has a lid. You get the same coffee plus extra features. **Proxy:** A hotel concierge (Proxy) is a middleman between you and a taxi service. You still get a taxi, but the concierge controls when, whether, and how (checks your loyalty status, pre-screens the driver). **Adapter:** A travel plug adapter (Adapter) lets your US laptop (different interface) plug into a UK socket. It doesn't add capabilities or control access — it translates the shape.

**One insight:**
The key is intent: if the wrapper adds behaviour → Decorator. If the wrapper controls access or lifecycle → Proxy. If the wrapper translates interface shape → Adapter. The same structural code can represent any of the three — only intent distinguishes them.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS FOR EACH:**

**Decorator invariants:**
1. Implements same interface as the component
2. Holds a reference to a component (can be null object or real)
3. Adds or augments behaviour; does not change when/whether the call happens

**Proxy invariants:**
1. Implements same interface as the subject
2. Controls access: may delay, cache, log, authenticate, redirect, or intercept
3. Behaviour addition is incidental; access/lifecycle control is primary

**Adapter invariants:**
1. The wrapped object has a DIFFERENT interface than what the client expects
2. The adapter translates calls from client interface to adaptee interface
3. Does not add behaviour or control access — translates

**DERIVED DESIGN:**
Decorator composes new behaviour by chaining: `new LoggingDecorator(new ValidationDecorator(new RealService()))`. Proxy often controls a single real subject (lazy-loaded or remote). Adapter solves interface mismatch — can only be "removed" when the client or adaptee interface changes.

**THE TRADE-OFFS:**
**Decorator:** Infinitely stackable; transparent to clients; can introduce call overhead with many layers.
**Proxy:** Single point of access control; transparent to clients; tight coupling between proxy and subject lifecycle.
**Adapter:** Solves hard interface incompatibility; not transparent at the type system level (client sees Adapter type, not Adaptee type unless using Target interface).

---

### 🧪 Thought Experiment

**SETUP:**
Three developers all write `class WrappedUserService { private final UserService delegate; ... }`.

**SCENARIO A (Decorator — adding behaviour):**
Developer A wraps to add audit logging: `delegate.getUser(id)` called after logging the request. The wrapper can be stacked with a `CachingWrapper`. All callers use it through the same `UserService` interface.

**SCENARIO B (Proxy — controlling access):**
Developer B wraps to add role-based access control: `if (!user.hasRole("ADMIN")) throw AccessDeniedException`. The wrapper guards the real service — it controls whether the call proceeds. This is Proxy, not Decorator.

**SCENARIO C (Adapter — translating interface):**
Developer C wraps an old `LegacyUserService` (with `fetchUser(int)`) to fit the new `UserService` interface (with `getUser(UUID)`): translates UUID to int, calls `legacy.fetchUser()`, converts the result. Interface mismatch = Adapter.

**THE INSIGHT:**
Same structure (wrapper with delegate). Three different intents. Correct naming matters for correct mental model, correct test expectations, and correct architectural reasoning about the wrapper's purpose.

---

### 🧠 Mental Model / Analogy

> Think of a pipeline of Russian nesting dolls. **Decorator** dolls add a hat, a coat, a backpack to the inner doll — each adds appearance. **Proxy** dolls check if you're allowed to open them, or delay opening until the right time — each controls access. **Adapter** dolls reshape from a round peg to a square peg — each translates compatibility. All nest the same way; the reason for nesting is what differs.

Comparison table:

| Dimension | Decorator | Proxy | Adapter |
|---|---|---|---|
| Purpose | Add behaviour | Control access | Translate interface |
| Same interface? | Yes | Yes | Client-facing Yes; Adaptee: No |
| Stacking? | Common (chain) | Rare (one per subject) | Usually one |
| Changes when call happens? | No | Yes (may deny/delay) | No (translates) |
| Changes what call does? | Yes (adds behaviour) | No (guards/caches) | No (translates) |

Where the analogy breaks down: real dolls are purely decorative. In code, all three wrappers participate in actual call delegation — the distinction is behavioural intent, not mechanical difference.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Three patterns wrap one object inside another. Decorator: "the outer one does more than the inner." Proxy: "the outer one decides IF and WHEN the inner runs." Adapter: "the outer one speaks a different language than the inner."

**Level 2 — How to use it (junior developer):**
Ask yourself: "Why am I wrapping?" — Add behaviour (caching, logging, validation) → Decorator. Control access (auth, lazy init, remote call) → Proxy. Translate interfaces → Adapter. Implement accordingly. In Spring: `@Transactional` uses a Proxy (controls transaction lifecycle); `InputStream` chain (e.g., `BufferedInputStream(FileInputStream(...))`) is Decorator; `Arrays.asList()` returning a `List` around an array is an Adapter.

**Level 3 — How it works (mid-level engineer):**
Spring AOP uses JDK Dynamic Proxy (for interfaces) or CGLIB Proxy (for classes) to implement `@Transactional`, `@Async`, `@Cacheable`. These are Proxies — their purpose is access control (transaction boundary management, async queue routing, cache lookup). The Decorator pattern appears in Java I/O: `PrintStream`, `BufferedReader`, and `DataInputStream` all wrap another stream and add capabilities while implementing the same `InputStream`/`OutputStream` interface. The Adapter appears in Java Collections: `Collections.enumeration(collection)` returns an `Enumeration` backed by an `Iterator` — adapting `Iterator` to the older `Enumeration` interface.

**Level 4 — Why it was designed this way (senior/staff):**
The three patterns derive from the same structural mechanism (composition + delegation) but solve different orthogonal problems in the design space. The reason they're grouped and compared rather than treated as completely distinct patterns is their shared structural DNA — a developer can accidentally implement the wrong one while solving a problem. The strategic importance: when deciding to wrap an object, the intent determines the lifecycle, testability strategy, and combinability. A Proxy should NOT be stacked (two transaction proxies = undefined behaviour). A Decorator SHOULD be stacked (logging + caching decorators are additive). An Adapter should NOT be composed with more Adapters (adapting twice = design problem). Understanding the three gives architectural guidance, not just naming conventions.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  THREE WRAPPER PATTERNS — STRUCTURAL COMPARISON      │
│                                                      │
│  DECORATOR:                                          │
│  Client → [Logging] → [Caching] → [RealService]     │
│  Same interface throughout; layers add behaviours    │
│  RealService always called (unless short-circuit)    │
│                                                      │
│  PROXY:                                              │
│  Client → [AuthProxy] → RealService                  │
│  Same interface; proxy may NOT call RealService      │
│  (rejects, caches response, loads lazily)            │
│                                                      │
│  ADAPTER:                                            │
│  Client → [Adapter] → LegacyService                  │
│  Client interface ≠ LegacyService interface          │
│  Adapter translates: adaptedMethod() → legacyCall()  │
└──────────────────────────────────────────────────────┘
```

**Code signatures:**
```java
// DECORATOR: same interface in and out
class LoggingPaymentDecorator implements PaymentGateway {
    private final PaymentGateway delegate; // same type
    PaymentResult charge(BigDecimal amt, String token) {
        log.info("Charging {}", amt);
        PaymentResult result = delegate.charge(amt, token);
        log.info("Result: {}", result);
        return result; // ALWAYS calls delegate
    }
}

// PROXY: same interface, controls access
class AuthPaymentProxy implements PaymentGateway {
    private final PaymentGateway target; // same type
    PaymentResult charge(BigDecimal amt, String token) {
        if (!secCtx.hasPermission("CHARGE"))
            throw new AccessDeniedException(); // MAY block
        return target.charge(amt, token);
    }
}

// ADAPTER: different interfaces
class LegacyPaymentAdapter implements PaymentGateway {// target
    private final LegacyBankClient client; // DIFFERENT type
    PaymentResult charge(BigDecimal amt, String token) {
        // Translate: new interface → old interface
        BankResponse r = client.processCharge(
            token, amt.doubleValue(), "USD");
        return new PaymentResult(r.transactionId());
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**TYPICAL SPRING STACK (all three present):**
```
HTTP POST /payments
  → Spring Controller
  → [AuthProxy − Proxy]      ← controls access (auth)
  → [LoggingDecorator − Dec] ← adds logging
  → [CachingDecorator − Dec] ← adds caching
  → [LegacyAdapater − Adap]  ← translates to old API
  → LegacyPaymentService

In Spring AOP terms:
  @Secured → Proxy (access control)
  @Cacheable → Proxy (cache lookup/storage)
  Manual logging wrapper → Decorator
  Service Adapter for 3rd-party → Adapter
```

**FAILURE PATH:**
```
AuthProxy denies → throws AccessDeniedException
  → PaymentGateway never reached
  → HTTP 403
  
LegacyPaymentAdapter receives malformed data:
  → BankClient rejects → LegacyBankException
  → Adapter must translate -> PaymentFailedException
  → HTTP 502
```

**WHAT CHANGES AT SCALE:**
With 7 Decorator layers stacked, each call adds 7 method invocations. At 100,000 requests/second, this is 700,000 extra method calls/second — negligible for I/O-bound services. For CPU-bound services with microsecond target latency, deep Decorator stacks must be profiled and possibly replaced with a single composed implementation.

---

### 💻 Code Example

**Side-by-side examples showing the same wrapped class used as Decorator, Proxy, and Adapter (explicitly labelled):**

```java
interface Reporter {
    void generateReport(String type);
}

class RealReporter implements Reporter {
    public void generateReport(String type) {
        System.out.println("Generating " + type);
    }
}

// ─── DECORATOR: adds timing ───────────────────────────
class TimedReporterDecorator implements Reporter {
    private final Reporter delegate;

    TimedReporterDecorator(Reporter delegate) {
        this.delegate = delegate;
    }

    @Override
    public void generateReport(String type) {
        long start = System.currentTimeMillis();
        delegate.generateReport(type); // ALWAYS called
        long end = System.currentTimeMillis();
        System.out.println("Took " + (end-start) + "ms");
    }
}

// ─── PROXY: controls access ───────────────────────────
class AdminOnlyProxy implements Reporter {
    private final Reporter target;

    AdminOnlyProxy(Reporter target) {
        this.target = target;
    }

    @Override
    public void generateReport(String type) {
        if (!currentUser().isAdmin())
            throw new AccessDeniedException(); // MAY block
        target.generateReport(type);
    }
}

// ─── ADAPTER: different interface ─────────────────────
class LegacyReportAdapter implements Reporter {
    private final LegacyReportSystem legacy; // DIFFERENT type

    LegacyReportAdapter(LegacyReportSystem legacy) {
        this.legacy = legacy;
    }

    @Override
    public void generateReport(String type) {
        // Translate: new interface → old interface
        int legacyTypeCode = switch(type) {
            case "SALES" -> 1; case "INVENTORY" -> 2;
            default -> throw new UnsupportedReport(type);
        };
        legacy.runReport(legacyTypeCode); // old API
    }
}
```

---

### ⚖️ Comparison Table

| Dimension | Decorator | Proxy | Adapter |
|---|---|---|---|
| **Primary intent** | Add behaviour | Control access | Transform interface |
| Wraps same interface | Yes | Yes | Partial (target yes, adaptee no) |
| May block the call | No | Yes | No |
| Can be stacked freely | Yes | Rarely | Usually no |
| Changes interface | No | No | Yes — that's the point |
| Spring examples | `@Slf4j` wrapper | `@Transactional`, `@Cached` | `JpaRepository` over JDBC |
| Java I/O examples | `BufferedReader` | — | `InputStreamReader` |

How to choose: state your intent first. Adding logging, validation, metrics → Decorator. Controlling transaction scope, auth, lazy init → Proxy. Integrating with a legacy or third-party API with an incompatible interface → Adapter.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Proxy and Decorator are the same because they look the same | Same structure; opposite intents. Proxy controls access; Decorator adds behaviour. The intent determines how they should be tested and composed |
| Adapter changes behaviour | Adapter only translates interface. Behaviour change belongs in Decorator or Proxy. An Adapter that also adds logging is doing two pattern jobs |
| Spring's AOP proxies are Decorators | Spring's `@Transactional` proxy is a Proxy (controls transaction lifecycle). `@Cacheable` is a Proxy (controls whether the real method is called). Not Decorators |
| Stacking multiple Proxies is fine | Multiple conflicting proxies (two transaction proxies) cause undefined behaviour. Decorators are designed to stack; Proxies typically control a single point of access |
| Adapter must translate method names | Adapter may call the same method name — the interface mismatch might be in parameter types or return types, not method names |

---

### 🚨 Failure Modes & Diagnosis

**1. Decorator Used as Proxy — Short-Circuiting Breaks Expectation**

**Symptom:** "Logging decorator" conditionally skips the real call for certain inputs. Callers find some requests silently not processed.

**Root Cause:** Developer named it a Decorator but implemented Proxy semantics (access control). Callers expect Decorator always delegates; they don't expect silent rejection.

**Diagnostic:**
```bash
grep -A 20 "class.*Decorator" src/ --include="*.java" \
  | grep "if\|throw\|return" 
# Decorator with guards/returns without delegate = Proxy behaviour
```

**Fix:** Rename to `*Proxy` or `*Guard` to reflect access-control intent. Or: separate concerns — Proxy for access control, Decorator for behaviour addition.

**Prevention:** Code review: every method in a Decorator must call the delegate unconditionally (except for known short-circuit decorators like caching). Access conditions → rename to Proxy.

---

**2. Adapter Accumulates Business Logic**

**Symptom:** `LegacyPaymentAdapter` now performs currency conversion, fraud detection, and retry logic in addition to interface translation. It's a 400-line class.

**Root Cause:** Developers kept adding to the adapter because "it's already there between the client and the legacy system." The adapter became a catch-all.

**Diagnostic:**
```bash
wc -l src/LegacyPaymentAdapter.java
# If >100 lines: too much responsibility for a pure adapter
```

**Fix:** Extract behaviour into Decorator layers wrapping the adapter. Adapter does translation only. `FraudCheckDecorator(RetryDecorator(CurrencyDecorator(adapter)))` separates concerns cleanly.

**Prevention:** Adapter's test should include ONLY: input translation and output translation. Anything else extracts to Decorator.

---

**3. Proxy Stack Without Documentation — Unexpected Behaviour**

**Symptom:** A method annotated `@Transactional @Cacheable @Secured @Async` behaves unexpectedly — async calls lose transaction context; cache stores results before the transaction commits.

**Root Cause:** Multiple proxies in an undocumented, order-dependent stack. `@Async` executes on a different thread with no transaction context. `@Cacheable` may cache before the outer transaction commits. The proxy interaction order matters.

**Diagnostic:**
```bash
# Spring: check effective proxy stack
@Autowired ApplicationContext ctx;
// Get bean and inspect proxy chain:
AopUtils.getTargetClass(bean) // reveals proxy layers
```

**Fix:** Use `@TransactionalEventListener` instead of combining `@Async` + `@Transactional`. Document the intended proxy application order. Test each combination of annotations explicitly.

**Prevention:** Each annotation = a proxy. Understand what each proxy does and in what order Spring applies them (controlled by `@Order` on `BeanPostProcessor` implementations).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Decorator` — Decorator pattern in depth; understanding what it adds and when to use it is required for this comparison
- `Proxy` — Proxy pattern in depth; access-control intent and lazy-init mechanics are essential
- `Adapter` — Adapter pattern in depth; interface translation mechanics and use cases required

**Builds On This (learn these next):**
- `AOP (Aspect-Oriented Programming)` — Spring AOP uses proxies to implement cross-cutting concerns; understanding Proxy vs Decorator classifies each AOP aspect
- `Facade` — provides a simplified interface to a complex subsystem; not a wrapper of one object but a facade over many
- `Bridge` — decouples abstraction from implementation; structural relationship orthogonal to Decorator/Proxy/Adapter

**Alternatives / Comparisons:**
- `Facade` — simplifies interface to a subsystem; different from Adapter (which maps one API to another) and from Decorator (which wraps one object)
- `Wrapper Pattern` — informal term that encompasses all three; "wrapper" is not specific enough to indicate intent
- `Delegation` — the implementation mechanism all three use; "delegation" describes the mechanism, not the pattern intent

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Three wrapper patterns with same struct.  │
│              │ but different intents                     │
├──────────────┼───────────────────────────────────────────┤
│ DECORATOR    │ Adds behaviour; always calls delegate;    │
│              │ stackable; same interface in/out          │
├──────────────┼───────────────────────────────────────────┤
│ PROXY        │ Controls access; may block call; single   │
│              │ point of access; same interface in/out    │
├──────────────┼───────────────────────────────────────────┤
│ ADAPTER      │ Translates interface; different input     │
│              │ interface than output; never stacked      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Same code structure; different intent     │
│              │ → choose by WHY you are wrapping          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Expressiveness (naming intent) vs         │
│              │ boilerplate of separate wrapper classes   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Do more (Dec) / Gate access (Prx) /      │
│              │  Speak their language (Adp)."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ AOP (Proxy) → Decorator (I/O streams) →  │
│              │ Adapter (Legacy integration)              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `SecurityWrapper` class wraps a `UserService`. It implements the same `UserService` interface. It checks the current user's role before any method call. If the user is admin, it calls the real service. If not, it throws `AccessDeniedException`. A manager asks: "Can we add multiple SecurityWrappers for different role levels?" Classify this wrapper (Decorator/Proxy/Adapter), justify the classification using all three invariants from the First Principles section, and explain why stacking multiple SecurityWrappers may or may not be safe.

**Q2.** Java's `Collections.unmodifiableList(list)` returns an `UnmodifiableList` that wraps the original list. `get()`, `size()`, and `iterator()` delegate to the inner list. `add()`, `remove()`, and `set()` throw `UnsupportedOperationException`. Classify this wrapper — Decorator, Proxy, or Adapter? Justify using all three pattern invariants. If a debate arises about whether this is Proxy or Decorator, identify the precise invariant where both arguments have merit and explain which classification is most accurate and why.

