---
layout: default
title: "Adapter"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /design-patterns/adapter/
id: DPT-050
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
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-017 - Adapter

⚡ TL;DR - Adapter converts one interface into another that clients expect, enabling incompatible interfaces to work together without changing either.

| DPT-017 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Polymorphism, Composition over Inheritance | |
| **Used by:** | Legacy System Integration, Third-party Library Wrappers, API Gateways | |
| **Related:** | Bridge, Decorator, Proxy, Facade, Wrapper | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A payment system uses a `PaymentGateway` interface: `processPayment(Payment p)`. A new integration is required with Stripe, which has its own API: `stripe.charges.create(ChargeParams params)`. The interfaces are incompatible - parameter types, method names, and return types differ. Without an adapter, the options are: (1) modify the existing `PaymentGateway` interface - breaking all existing callers; (2) modify Stripe's library - impossible (it's third-party); (3) scatter Stripe-specific code throughout the application - coupling the entire codebase to Stripe's API.

**THE BREAKING POINT:**
Option 3 is the usual choice under time pressure. Now Stripe-specific `ChargeParams` objects appear in services, controllers, and tests. When the business decides to switch to PayPal, every integration point must be identified and changed. The "quick integration" becomes a multi-week migration and regression nightmare.

**THE INVENTION MOMENT:**
This is exactly why the Adapter pattern was created. Build a `StripePaymentAdapter implements PaymentGateway`. This adapter receives `Payment` (the system's type), translates it to `ChargeParams` (Stripe's type), calls Stripe's API, and translates the result back. The rest of the application never knows Stripe exists. Switching to PayPal: write `PayPalPaymentAdapter`, swap the instance. Zero changes to any caller.

**EVOLUTION:**
Adapter was critical in the era of proprietary interfaces and
incompatible libraries. Java's introduction of generic
interfaces (`List`, `Comparator`, `Iterator`) provided standard
contracts that reduced the need for adapters between common
data structures. Modern adaptation scenarios shifted to:
REST/gRPC protocol adapters, database vendor adapters (JDBC
driver implementations), and cloud provider adapters (AWS SDK
abstracting S3, GCS). Spring's `HandlerAdapter` is a classic
production Adapter that maps HTTP requests to handler methods.

---

### 📘 Textbook Definition

The **Adapter** pattern (also called "Wrapper") is a structural design pattern that converts the interface of a class into another interface that clients expect. An Adapter class wraps an incompatible *adaptee* and exposes the interface the *target* (client) requires. The Adapter acts as a translation layer between the client's expected interface and the adaptee's actual interface. It can be implemented via class inheritance (class adapter) or object composition (object adapter); composition is preferred in modern Java.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A translator between two incompatible interfaces so they can work together unchanged.

**One analogy:**
> A travel power adapter. Your European laptop charger has a Type C plug. The US wall socket is Type A. You don't rewire your charger or the wall - you use an adapter that accepts one plug type and exposes the other. The laptop charges; nothing was modified.

**One insight:**
The Adapter's job is pure translation - no new behaviour, no added logic. If you find yourself adding business logic to an adapter, stop: you've crossed from Adapter into Decorator or Facade territory. A correct Adapter is a thin mapping layer.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A system has a target interface that clients are coded against.
2. An adaptee exists with useful behaviour but an incompatible interface.
3. Neither the client code nor the adaptee can (or should) be modified.

**DERIVED DESIGN:**
Given all three invariants: create a new class (the Adapter) that implements the target interface and wraps (holds a reference to) the adaptee. Each method of the target interface is implemented by translating the call to the corresponding adaptee method - adapting types, method names, and parameter orders as needed.

Two flavours of structural implementation:
- **Object Adapter (preferred):** Adapter holds a reference to the adaptee (composition). Works with adaptee subclasses; does not require source code access.
- **Class Adapter:** Adapter extends the adaptee and implements the target interface (multiple inheritance). Java doesn't support multiple class inheritance, so this is only possible with interfaces as the adaptee.

**THE TRADE-OFFS:**
**Gain:** Allows incompatible libraries to interoperate without modification; isolates foreign API details behind a known interface; enables drop-in replacement (swap one adapter for another); supports Open/Closed Principle.
**Cost:** One extra class per adaptee; if the target interface is large, the adapter becomes large; if the adaptee's interface changes, the adapter must change; pure translation only - cannot add new behaviour justified by the pattern.

---

### 🧪 Thought Experiment

**SETUP:**
A legacy system has a `Logger` interface: `log(String level, String message)`. A new structured logging library (SLF4J) is adopted. SLF4J uses: `logger.info(message)`, `logger.warn(message)`, `logger.error(message)` - separate methods per level.

**WHAT HAPPENS WITHOUT ADAPTER:**
Every class using `Logger` must be rewritten to use SLF4J directly. 500 classes reference the old `Logger`. The migration takes 3 weeks. During migration, some classes use old Logger and some use SLF4J - the log output is inconsistent.

**WHAT HAPPENS WITH ADAPTER:**
Create `SLF4JLoggerAdapter implements Logger`. Its `log(String level, String message)` method checks the level and calls `slf4jLogger.info()`, `.warn()`, or `.error()`. Swap the dependency injection binding. All 500 classes now transparently use SLF4J through the adapter - migration completed in 2 hours, zero changes to calling code.

**THE INSIGHT:**
Adapter allows legacy and modern code to coexist. The adapter is the compatibility shim that buys time to migrate properly - or permanently maintains the integration if migration is not worth the cost.

---

### 🧠 Mental Model / Analogy

> An Adapter is like a foreign language interpreter at a business meeting. Your team speaks English (target interface). The partner speaks Japanese (adaptee interface). The interpreter (adapter) sits between them: they hear English, translate to Japanese, relay the response in English. Nobody on either side changes how they speak.

- "English speakers" → client code using target interface
- "Japanese speakers" → adaptee (e.g., Stripe API, legacy service)
- "Interpreter" → the Adapter class
- "Target interface" → the English protocol expected by clients
- "Adaptee interface" → the Japanese protocol of the adaptee
- "Translation" → method name/parameter type conversion in adapter

Where this analogy breaks down: a real interpreter can sometimes misinterpret or add nuance. An Adapter must be an exact, lossless translation - any semantic change makes it something other than an Adapter.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An Adapter is a connector piece. When two systems don't speak the same language, the adapter translates between them. One side says its thing in its language; the adapter converts it; the other side receives it in its own language. Neither side needed to change.

**Level 2 - How to use it (junior developer):**
Define your target interface. Identify the adaptee. Create `AdapteeAdapter implements Target`. In the implementing methods, translate: convert input parameters to adaptee types, call the adaptee method, convert the return value back to the target type. Inject the adapter wherever the target interface is used. Done. Test the adapter independently by mocking the adaptee.

**Level 3 - How it works (mid-level engineer):**
The object adapter holds the adaptee as a field: `private final StripeClient stripeClient`. It is a standard composition relationship. The target interface is implemented by delegating to the adaptee with type conversion: `public PaymentResult process(Payment p) { ChargeParams cp = toStripeParams(p); Charge c = stripeClient.create(cp); return toPaymentResult(c); }`. The translation functions (`toStripeParams`, `toPaymentResult`) are the heart of the adapter - they are the only code that needs updating when Stripe changes its API. When the adaptee uses checked exceptions that don't exist in the target interface, the adapter catches and re-throws as the appropriate target exception type.

**Level 4 - Why it was designed this way (senior/staff):**
Adapter is one of the simplest structural patterns yet one of the most impactful in practice. Every enterprise codebase is an accumulation of adapters - ORMs adapt SQL to objects, serialisers adapt objects to bytes, REST client wrappers adapt HTTP responses to domain models. The critical design decision is where to draw the adapter boundary: too thin (only rename methods), and you expose adaptee-specific leakage (Stripe's error types bleed through). Too thick (full domain translation), and the adapter has become a facade or anti-corruption layer. The canonical rule: an Adapter translates interface; an Anti-Corruption Layer translates semantics. A Stripe `ChargeDeclined` event to a domain `PaymentFailureEvent` is Anti-Corruption Layer work - the event carries business meaning beyond interface differences.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│  ADAPTER STRUCTURE (Object Adapter)              │
│                                                  │
│  Target Interface                                │
│  ┌─────────────────────────────┐                 │
│  │ <<interface>>               │                 │
│  │ PaymentGateway              │                 │
│  │ + processPayment(Payment)   │                 │
│  └──────────────┬──────────────┘                 │
│                 │ implements                     │
│  ┌──────────────▼──────────────┐                 │
│  │ StripePaymentAdapter        │                 │
│  │ - stripeClient: StripeClient│ ← holds adaptee │
│  │                             │                 │
│  │ + processPayment(Payment p) │                 │
│  │   1. convert p → ChargeParam│                 │
│  │   2. stripeClient.charge()  │ ← calls adaptee │
│  │   3. convert Charge → Result│                 │
│  └──────────────┬──────────────┘                 │
│                 │ delegates to                   │
│  ┌──────────────▼──────────────┐                 │
│  │ StripeClient (Adaptee)      │                 │
│  │ + charge(ChargeParams)      │                 │
│  │ + refund(RefundParams)      │                 │
│  └─────────────────────────────┘                 │
└──────────────────────────────────────────────────┘
```

**Translation step in detail:**
```
processPayment(Payment payment) {
  // Step 1: translate Payment → ChargeParams
  ChargeParams params = new ChargeParams()
      .amount(payment.getAmountInCents())
      .currency(payment.getCurrency().toISOCode())
      .source(payment.getCardToken())
      .description(payment.getOrderId());

  // Step 2: call adaptee
  try {
      Charge charge = stripeClient.charges().create(params);

  // Step 3: translate result + exceptions
      return new PaymentResult(
          charge.getId(),
          PaymentStatus.SUCCESS);

  } catch (CardException e) {
      return new PaymentResult(
          null,
          PaymentStatus.DECLINED,
          e.getDeclineCode());
  }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Service layer
  → paymentGateway.processPayment(payment)
  → StripePaymentAdapter.processPayment()  ← YOU ARE HERE
  → translates Payment → ChargeParams
  → StripeClient.charges().create(params)
  → Stripe API HTTP call
  → response received
  → translates Charge → PaymentResult
  → PaymentResult returned to service layer
  → service layer proceeds without knowing about Stripe
```

**FAILURE PATH:**
```
Stripe API timeout
  → StripeClient throws StripeConnectException
  → Adapter catches StripeConnectException
  → Adapter throws PaymentGatewayException
     (target interface's exception type)
  → Service layer handles PaymentGatewayException
  → Service never knows it was Stripe-specific
```

**WHAT CHANGES AT SCALE:**
At high throughput (10,000+ transactions/second), the adapter becomes a hot code path. Translation overhead (object creation for `ChargeParams`) should be profiled. Object pooling or pre-allocated parameter objects can reduce GC pressure. At multi-regional scale, the same adapter may route to different Stripe regions - this logic belongs in the adapter's internal routing, not in client code.

---

### 💻 Code Example

**Example 1 - BAD: Stripe-specific code scattered in service:**
```java
// BAD: Service knows about Stripe internals
public class OrderService {
    private final StripeClient stripe; // Stripe-specific!

    public void placeOrder(Order order) {
        // Stripe-specific parameter construction scattered here
        ChargeParams params = new ChargeParams()
            .amount(order.getTotal() * 100)
            .currency("usd")
            .source(order.getCardToken());

        try {
            stripe.charges().create(params); // Stripe API!
        } catch (StripeException e) {
            // Stripe exception type leaked to service layer
            throw new RuntimeException(e);
        }
    }
}
// Switching from Stripe requires modifying OrderService
```

**Example 2 - GOOD: Adapter isolates Stripe:**
```java
// Target interface (system-level abstraction)
public interface PaymentGateway {
    PaymentResult processPayment(Payment payment);
}

// Adapter: wraps Stripe, exposes PaymentGateway
public class StripePaymentAdapter
        implements PaymentGateway {

    private final StripeClient stripeClient;

    public StripePaymentAdapter(StripeClient client) {
        this.stripeClient = client;
    }

    @Override
    public PaymentResult processPayment(Payment payment) {
        // Translate: Payment → Stripe's ChargeParams
        ChargeParams params = ChargeParams.builder()
            .amount(payment.amountInCents())
            .currency(payment.currency().code())
            .source(payment.cardToken())
            .description("Order: " + payment.orderId())
            .build();

        try {
            Charge charge =
                stripeClient.charges().create(params);
            // Translate: Stripe Charge → PaymentResult
            return PaymentResult.success(charge.getId());

        } catch (CardException e) {
            return PaymentResult.declined(
                e.getDeclineCode());
        } catch (StripeException e) {
            throw new PaymentGatewayException(
                "Stripe unavailable", e);
        }
    }
}

// Service layer - knows nothing about Stripe:
public class OrderService {
    private final PaymentGateway paymentGateway;

    public OrderService(PaymentGateway gateway) {
        this.paymentGateway = gateway;
    }

    public void placeOrder(Order order) {
        Payment payment = Payment.from(order);
        PaymentResult result =
            paymentGateway.processPayment(payment);
        if (!result.isSuccess()) {
            throw new PaymentDeclinedException(
                result.getDeclineCode());
        }
    }
}

// Wiring: inject the adapter
OrderService svc = new OrderService(
    new StripePaymentAdapter(new StripeClient(apiKey)));
```

**Example 3 - Bidirectional adapter for legacy + new system:**
```java
// Legacy code uses old interface
public interface OldEmailSender {
    void sendEmail(String to, String subject, String body);
}

// New library uses new interface
public interface EmailClient {
    void send(EmailMessage message);
}

// Adapter: makes new library look like old interface
public class EmailClientAdapter implements OldEmailSender {
    private final EmailClient client;

    public EmailClientAdapter(EmailClient client) {
        this.client = client;
    }

    @Override
    public void sendEmail(
            String to, String subject, String body) {
        // Translate old params into new EmailMessage
        client.send(EmailMessage.builder()
            .recipient(to)
            .subject(subject)
            .textBody(body)
            .build());
    }
}
```

---

### ⚖️ Comparison Table

| Pattern | Purpose | Changes Adaptee? | Adds Behaviour? | Best For |
|---|---|---|---|---|
| **Adapter** | Translate interface | No | No | Incompatible library integration |
| Facade | Simplify many interfaces | No | No (simplifies) | Hiding subsystem complexity |
| Decorator | Add behaviour | No | Yes | Transparent feature addition |
| Proxy | Control access | No | Access control | Caching, security, lazy loading |
| Bridge | Decouple abstraction | No | No | Multiple orthoganal dimensions |

How to choose: use Adapter when the problem is incompatible interfaces. Use Facade when the problem is too many interfaces (simplify access to a subsystem). Use Decorator when you need to add behaviour at runtime without changing the interface.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Adapter and Facade are the same | Adapter matches one interface to another (1:1 translation). Facade simplifies many interfaces into one simplified unified interface (many:1 simplification) |
| Adapter changes the adaptee's behaviour | Adapter only changes how the adaptee is accessed (interface). Behaviour remains unchanged. Adding new behaviour makes it a Decorator |
| Class adapter (via inheritance) is better in Java | Java doesn't support multiple class inheritance. Object adapter (composition) is the correct Java approach and is more flexible - it works with adaptee subclasses |
| Adapter is only for legacy systems | Adapters are used everywhere: ORMs, JSON mappers, REST client wrappers, test mocks. Any interface boundary with a type mismatch needs an adapter |
| One adapter per adaptee method is needed | An adapter implements ALL methods of the target interface. Each method may adapt a different adaptee method - the whole adapter is one class |

---

### 🚨 Failure Modes & Diagnosis

**1. Adaptee Exception Types Leaking Through Adapter**

**Symptom:** Service layer `catch (StripeException e)` - Stripe-specific exception type appearing in code that should not know about Stripe.

**Root Cause:** The adapter's method throws the adaptee's exception type instead of translating it to the target interface's exception type.

**Diagnostic:**
```bash
grep -r "StripeException\|StripeApiException" \
  src --include="*.java" \
  | grep -v "StripePaymentAdapter.java"
# Any result = Stripe exception leaking through adapter
```

**Fix:**
Every checked exception from the adaptee must be caught in the adapter and re-thrown as the target interface's exception type. Unchecked exceptions: wrap in a target-interface-appropriate unchecked exception.

**Prevention:** Define which exceptions the target interface permits. Code review: no adaptee-specific types in service/controller layer.

---

**2. Translation Drift - Adapter Out of Sync with Adaptee**

**Symptom:** After Stripe updated their API (v2 to v3), `ChargeParams.amount()` now expects a `Money` object instead of a long integer. The adapter still passes a `long` - a `ClassCastException` at runtime.

**Root Cause:** The adaptee's API changed but the adapter's translation logic was not updated.

**Diagnostic:**
```bash
# Add contract tests for the adapter:
mvn test -pl adapter-tests
# Contract tests call the real adaptee with adapter output
# and verify the call succeeds - catches interface drift early
```

**Fix:**
Update the adapter's translation logic for the new API. Add contract tests that test the adapter against the real adaptee (or an updated mock that reflects the new API).

**Prevention:** Contract tests between the adapter and the adaptee (or Pact tests in microservice contexts) detect API drift before production deployment.

---

**3. Adapter Adding Business Logic (Wrong Responsibility)**

**Symptom:** The adapter applies a currency conversion formula and validates card expiry dates. A bug in the formula causes incorrect charge amounts.

**Root Cause:** Business logic crept into the adapter. The adapter should only translate interfaces - any logic it contains is in the wrong place and will not be tested or discoverable as business logic.

**Diagnostic:**
```bash
# Adapter line count check - adapters should be thin:
wc -l src/StripePaymentAdapter.java
# If > 200 lines: likely contains business logic
grep -n "if\|calculate\|validate" \
  src/StripePaymentAdapter.java
# Business conditions/calculations in adapter = code smell
```

**Fix:**
Extract business logic to a dedicated service or domain object. The adapter becomes a pure translation layer.

**Prevention:** Code review rule: adapters contain only type conversions, method name translations, and exception wrapping. No conditionals based on business rules.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Interface` - the target interface is the contact point clients are coded against; understanding Java interface contracts is required
- `Composition over Inheritance` - object adapter uses composition (holds adaptee reference); understanding why composition is preferred over inheritance is essential
- `Polymorphism` - clients interact with the adapter polymorphically through the target interface - the adaptee type is invisible

**Builds On This (learn these next):**
- `Facade` - when multiple adaptees need to be unified into one simplified interface, Facade builds on Adapter concepts
- `Anti-Corruption Layer` - a Domain-Driven Design pattern extending Adapter to translate not just interface but also domain semantics between bounded contexts
- `Proxy` - the structural sibling; Proxy controls access to the same-interface object rather than translating between different interfaces

**Alternatives / Comparisons:**
- `Facade` - addresses too-complex interfaces (many methods); Adapter addresses incompatible interfaces (wrong type)
- `Bridge` - decouples abstraction from implementation for independent evolution; Adapter is a post-hoc fix for existing incompatibility
- `Decorator` - wraps same interface to add behaviour; Adapter wraps different interface to translate it

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Wrapper that translates one interface into │
│              │ another, enabling incompatible code to     │
│              │ work together                             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Client expects interface A; library        │
│ SOLVES       │ provides interface B - cannot change either│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Adapter translates interface only -        │
│              │ no new behaviour, no simplification       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Integrating third-party libraries, legacy  │
│              │ systems, or incompatible API versions     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Interfaces are compatible or only         │
│              │ slightly different - just modify the code │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Clean isolation + replaceability vs extra  │
│              │ indirection layer and translation overhead│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Same plug, different socket -            │
│              │  adapter in the middle."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Facade → Decorator → Proxy               │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you cannot change an interface but must use it with code
expecting a different interface, create a thin translation layer
rather than sprawling conditional code. Isolate the translation.

**Where else this pattern appears:**
- **Hardware device drivers:** The OS exposes a uniform device
  interface (`read()`, `write()`, `ioctl()`); each device vendor
  provides an adapter (driver) that translates to the device's
  actual protocol.
- **Currency exchange:** A currency adapter converts between
  monetary systems -- the underlying value is the same; the
  representation is adapted to the local context.
- **Protocol gateways (REST-to-SOAP):** An API gateway adapts
  REST calls to legacy SOAP services -- callers use modern
  HTTP/JSON; the adapter translates to XML and SOAP envelopes.

---

### 💡 The Surprising Truth

Java's `Arrays.asList()` returns a fixed-size `List` that is an
adapter over an array -- mutations to the list are reflected
in the underlying array and vice versa. Most Java developers
treat it as a standard `List`, not an Adapter, yet it is a
textbook two-way Adapter: the array is the adaptee, the `List`
interface is the target, and `Arrays.asList()` is the adapter
factory. The pattern is so embedded in the standard library
that engineers use it daily without recognising it.
---

### 🧠 Think About This Before We Continue

**Q1.** Your system has a `StorageService` interface with methods `upload(File f)` and `download(String key)`. You have an S3 adapter and an Azure Blob adapter. A new requirement: all file uploads must be virus-scanned before storage. Where exactly should the virus-scanning logic live - in each adapter, in a new class, or somewhere else? Justify your answer by explaining what principle is violated if you put it in the adapters.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** An Adapter for a legacy Oracle-based `CustomerRepository` translates the new domain's `Customer` object to the legacy `LegacyCustomerRecord` DTO. The legacy system uses a 6-character customer code (e.g., "SMITH1") while the new domain uses a UUID. The adapter maps new UUIDs to legacy codes using an in-memory `Map`. Identify the failure mode when the application restarts and describe what architectural component is missing from this adapter design.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A team must integrate with a legacy
SOAP service (exposing WSDL) from a modern Spring REST service.
They debate three approaches: (1) Adapter class wrapping the
SOAP client, (2) generating a REST facade service that calls SOAP,
(3) using Spring's integration framework. Map each option to
pattern territory and state the criteria for choosing each.

*Hint: The Comparison Table shows Adapter vs Facade -- option 1
is Adapter, option 2 is Facade+Adapter. The decision criteria
are ownership (can you change the SOAP side?) and blast radius
(how many callers need the translation?).*
