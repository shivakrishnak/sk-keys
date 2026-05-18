---
id: DPT-012
title: Adapter
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005
used_by: DPT-041, DPT-018
related: DPT-013, DPT-015, DPT-018, DPT-041
tags:
  - pattern
  - structural
  - intermediate
  - integration
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/design-patterns/adapter/
---

⚡ TL;DR - Adapter converts the interface of a class into
the interface a client expects - allowing incompatible
interfaces to work together without modifying either side.

| #12 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005 | |
| **Used by:** | DPT-041, DPT-018 | |
| **Related:** | DPT-013, DPT-015, DPT-018, DPT-041 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your application was built against a `LegacyLogger` class
that has `log(String msg, int level)`. Your new code must
use a logging framework that expects an `SLF4J Logger`
interface: `logger.info(String)`, `logger.warn(String)`,
`logger.error(String)`. The two interfaces are incompatible.
Changing the legacy logger breaks existing code. Changing
the new interface breaks the framework contract.

**THE BREAKING POINT:**
Every call site in the existing codebase uses `LegacyLogger`.
The new framework is required for new features and compliance
logging. There are three unacceptable options: (1) rewrite
all existing code to use SLF4J (high risk, high cost),
(2) fork the legacy logger (duplicate maintenance), (3) have
two logging systems running simultaneously (chaotic).

**THE INVENTION MOMENT:**
Adapter: create a wrapper class that implements SLF4J's
`Logger` interface and internally delegates to `LegacyLogger`.
Neither the legacy code nor the new framework code is
modified. The wrapper TRANSLATES between the two interfaces.

**EVOLUTION:**
Adapter is the integration workhorse of enterprise systems.
Every time a new library, external API, or third-party
service must plug into an existing system, Adapter makes
the connection without modifying either side. Java's SLF4J
itself is an Adapter framework: SLF4J provides a standard
logging interface; behind it, adapters connect to Log4j,
Logback, java.util.logging, or any other backend.

---

### 📘 Textbook Definition

The **Adapter** pattern (also known as Wrapper) is a
Structural design pattern that converts the interface of
a class into another interface that clients expect. Adapter
lets classes work together that could not otherwise because
of incompatible interfaces. It wraps a class (the Adaptee)
with a new class that presents the Target interface. The
adapter translates calls from the Target interface into
the appropriate calls on the Adaptee.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Adapter wraps an object to make it look like something
else - a power plug converter for code interfaces.

**One analogy:**
> A US laptop charger (Target interface) requires a 3-prong
> US outlet. In the UK, you use a travel adapter (Adapter).
> The adapter accepts the US plug (Adaptee interface) and
> converts it to the UK socket. Neither the charger nor the
> UK outlet is modified.

**One insight:**
Adapter's purpose is INTEGRATION WITHOUT MODIFICATION. The
Open/Closed Principle says "open for extension, closed for
modification." Adapter IS this principle applied to third-party
or legacy code you cannot modify.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Neither the Target interface nor the Adaptee class is
   modified - Adapter is a pure intermediary.
2. The Adapter contains a REFERENCE to the Adaptee; it
   does not extend it (object adapter variant).
3. All calls to the Adapter are translated to calls on the
   Adaptee - no logic added, only translation.

**DERIVED DESIGN:**
Three participants:
- **Target**: the interface the client expects
- **Adaptee**: the existing class with an incompatible interface
- **Adapter**: implements Target, holds a reference to
  Adaptee, translates method calls

Two variants:
- **Object Adapter** (composition): Adapter holds a reference
  to the Adaptee. Preferred in Java - works with any Adaptee
  subclass and does not require inheriting from Adaptee.
- **Class Adapter** (inheritance): Adapter extends Adaptee
  AND implements Target (requires multiple inheritance,
  possible in C++ but not Java - not applicable in Java
  without workarounds).

**TRADE-OFFS:**

**Gain:** No modification to existing code. Clean integration
boundary. Legacy systems gain new interface compatibility.

**Cost:** Added indirection layer. If Adaptee's interface
changes, the Adapter must be updated. If many adapters
accumulate without cleanup, the codebase becomes hard to
follow (hidden translation layers).

---

### 🧪 Thought Experiment

**SETUP:**
Your service was built using a third-party payment gateway
`StripeClient` with method `charge(String customerId, int
amount, String currency)`. You must now also support
PayPal with `PayPalClient.processPayment(PaymentRequest req)`.
New checkout code should work with either gateway without
conditionals scattered through business logic.

**WHAT HAPPENS WITHOUT ADAPTER:**
`if (provider == STRIPE) stripeClient.charge(...) else
if (provider == PAYPAL) paypalClient.processPayment(...)`.
Every place in the codebase that processes payments needs
this conditional. Adding a third gateway (Braintree) requires
finding and modifying every payment-related code path.

**WHAT HAPPENS WITH ADAPTER:**
Define `PaymentGateway` interface: `processPayment(long
cents, String currency, String customerId)`. Create
`StripeAdapter implements PaymentGateway` and
`PayPalAdapter implements PaymentGateway`. Each adapter
translates the standard call to its specific gateway API.
All business logic uses `PaymentGateway` - zero conditionals.
Adding Braintree: one new Adapter class, zero changes to
business logic.

**THE INSIGHT:**
Adapter converts the variability of external interface
differences into a stable internal interface. The Adapter
boundary is where the external world's inconsistency is
absorbed, leaving the application's internals consistent.

---

### 🧠 Mental Model / Analogy

> Adapter is a TRANSLATION SERVICE between two parties that
> speak different languages. The client speaks English (Target
> interface). The legacy system speaks French (Adaptee
> interface). The Adapter translates every English request
> into French and every French response into English. Neither
> the client nor the legacy system learns a new language.

- "English-speaking client" = code using Target interface
- "French-speaking legacy system" = the Adaptee
- "Translator" = the Adapter
- "Translation dictionary" = the method translation logic
  inside the Adapter

**Where this analogy breaks down:**
A human translator can fail gracefully when a nuance does
not translate. An Adapter must handle every case, including
when the Adaptee cannot fulfill what the Target interface
requires - exceptions and error conditions must also be
translated correctly.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Adapter makes two incompatible pieces of code work together
without changing either piece. It is a middle layer that
speaks both "languages."

**Level 2 - How to use it (junior developer):**
Define the interface you want (`Target`). Create a class
that implements Target and takes the existing object
(`Adaptee`) in its constructor. In each Target method,
call the appropriate Adaptee method, translating parameters
and return types as needed.

**Level 3 - How it works (mid-level engineer):**
Object Adapter uses composition: the Adapter holds a private
reference to the Adaptee and delegates to it. This is
preferred over inheritance because it works with any subclass
of Adaptee and keeps the Adapter's implementation clean.
The key implementation question is parameter translation:
converting data types, units, or representations between
the two interfaces.

**Level 4 - Why it was designed this way (senior/staff):**
Adapter solves the "impedance mismatch" problem in interface
design - when two independently designed systems must
interact, their interfaces are almost never identical.
Adapter provides a principled place to put the mismatch
resolution code: in a dedicated class, not scattered through
business logic. This is preferable to modifying either side
because: you may not have the source code of either side
(third-party libraries), or modifying either side may break
other users of that interface.

**Level 5 - Mastery (distinguished engineer):**
Adapter is at its most powerful in the Ports and Adapters
architecture (Hexagonal Architecture). The application's
"ports" ARE interfaces (Target); "adapters" are Adapter
implementations connecting the domain core to external
systems (database, message queue, payment gateway, email
service). The domain core knows only the port interface;
the adapter handles the external system's specific API.
This makes the entire domain core testable with mock
adapters and deployable against different external systems
(SQLite in tests, PostgreSQL in production) without changing
the domain model.

---

### ⚙️ How It Works (Mechanism)

```
Adapter Structure (Object Adapter)
┌──────────────────────────────────────────────────────┐
│  <<interface>> Target                                │
│  + request(): Response                               │
│                                                      │
│  Adapter implements Target                           │
│  - adaptee: Adaptee          ← holds reference       │
│  + request(): Response       ← implements Target     │
│      // translate and delegate                       │
│      LegacyRequest req =                             │
│          translate(request)  ← transform params      │
│      LegacyResponse lr =                             │
│          adaptee.legacyOp(req) ← call adaptee        │
│      return translate(lr)    ← transform result      │
│                                                      │
│  Adaptee (existing class, NOT modified)              │
│  + legacyOp(LegacyRequest): LegacyResponse           │
│                                                      │
│  Client                                              │
│  - target: Target            ← knows only interface  │
│  + doWork()                                          │
│    target.request()          ← calls via Target      │
│    // never calls Adaptee directly                   │
└──────────────────────────────────────────────────────┘
```

**Call flow:**
1. Client calls `target.request()`
2. Adapter.request() translates parameters to Adaptee's format
3. Adapter calls `adaptee.legacyOp(translatedParams)`
4. Adapter translates Adaptee's response back to Target format
5. Client receives Target-compatible response
6. Client and Adaptee never interact directly

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client calls target.request(ClientRequest)
  → Adapter translates: ClientRequest → LegacyParams
  → Adapter calls adaptee.legacyOp(LegacyParams)
  → Adaptee executes and returns LegacyResponse
  → Adapter translates: LegacyResponse → ClientResponse
  → Client receives ClientResponse
All translation in one class; client knows nothing of
  Adaptee
```

**FAILURE PATH:**
```
Adaptee.legacyOp() throws LegacyException
  → Adapter must catch LegacyException
  → Translate to Target-expected exception type
  → If Adapter lets LegacyException propagate:
    client code must know LegacyException type
    (breaks the isolation that Adapter provides)
```

**WHAT CHANGES AT SCALE:**
Adapter adds one method call indirection per request.
The cost is a JVM method dispatch - nanoseconds. At
millions of requests per second, the cost is negligible.
The design risk at scale is adapter proliferation: many
adapters for many external systems, each with different
translation logic, becomes a maintenance burden.

---

### 💻 Code Example

**Example 1 - Without Adapter (scattered translation):**

```java
// BAD: translation logic scattered in business code
class PaymentService {
    private final StripeClient stripe;
    private final PayPalClient paypal;

    void pay(Order order, PaymentProvider provider) {
        if (provider == STRIPE) {
            // Stripe-specific conversion here
            stripe.charge(
                order.customerId(),
                (int)(order.total() * 100), // cents
                order.currency().code()
            );
        } else if (provider == PAYPAL) {
            // PayPal-specific conversion here
            PaymentRequest req = new PaymentRequest();
            req.setAmount(order.total());
            req.setCurrencyCode(order.currency().code());
            req.setPayerId(order.customerId());
            paypal.processPayment(req);
        }
        // Adding Braintree: modify this class again (OCP violation)
    }
}
```

**Example 2 - Adapter solution:**

```java
// GOOD: Adapter isolates each gateway's specifics

// Target interface: what business logic expects
interface PaymentGateway {
    void processPayment(String customerId,
                        BigDecimal amount,
                        Currency currency);
}

// Adapter A: wraps Stripe
class StripeAdapter implements PaymentGateway {
    private final StripeClient stripe; // Adaptee

    StripeAdapter(StripeClient stripe) { this.stripe = stripe; }

    @Override
    public void processPayment(String customerId,
                               BigDecimal amount,
                               Currency currency) {
        // Translate: BigDecimal → cents int, Currency → String
        int cents = amount.multiply(BigDecimal.valueOf(100))
                          .intValueExact();
        stripe.charge(customerId, cents, currency.getCurrencyCode());
    }
}

// Adapter B: wraps PayPal
class PayPalAdapter implements PaymentGateway {
    private final PayPalClient paypal; // Adaptee

    PayPalAdapter(PayPalClient paypal) { this.paypal = paypal; }

    @Override
    public void processPayment(String customerId,
                               BigDecimal amount,
                               Currency currency) {
        PaymentRequest req = new PaymentRequest();
        req.setAmount(amount);
        req.setCurrencyCode(currency.getCurrencyCode());
        req.setPayerId(customerId);
        paypal.processPayment(req);
    }
}

// Business logic: knows only PaymentGateway, zero provider logic
class PaymentService {
    private final PaymentGateway gateway; // injected

    void pay(Order order) {
        gateway.processPayment(
            order.customerId(), order.total(), order.currency());
        // Adding Braintree: new BraintreeAdapter, no change here
    }
}
```

**Example 3 - SLF4J as an Adapter framework:**

```java
// RECOGNITION: SLF4J is an Adapter Pattern framework
// Target interface: SLF4J Logger
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

Logger log = LoggerFactory.getLogger(MyClass.class);
log.info("Processing order {}", orderId);
// ↑ Client uses Target (SLF4J Logger)

// Internally, SLF4J uses an Adapter:
// - SLF4J-log4j12 adapter: translates SLF4J Logger → Log4j Logger
// - SLF4J-logback adapter: translates SLF4J Logger → Logback Logger
// The Adaptee is the actual logging backend
// Client code never imports Log4j or Logback directly
```

**How to test/verify correctness:**
Test the Adapter in isolation with a mock Adaptee: verify
parameter translation (correct units, types, formats). Test
that exception translation is complete: Adaptee exceptions
become the expected Target exception types. Test that the
client code works correctly against a mock Adapter without
needing the real Adaptee.

---

### ⚖️ Comparison Table

| Pattern       | Purpose                        | Modifies Original? | Wraps? | New Interface? |
| ------------- | ------------------------------ | ------------------ | ------ | -------------- |
| **Adapter**   | Interface conversion           | No                 | Yes    | Yes            |
| Decorator     | Behavior addition              | No                 | Yes    | No (same iface)|
| Proxy         | Access control / lazy load     | No                 | Yes    | No (same iface)|
| Facade        | Simplified interface for system| No                 | Yes    | Yes (simpler)  |
| Bridge        | Abstraction-implementation sep.| No                 | Via ref| Yes            |

**How to choose:**
- Need to make an incompatible interface compatible? Adapter
- Need to add behavior without changing interface? Decorator
- Need access control or lazy loading? Proxy
- Need to simplify a complex subsystem? Facade
- All three wrap an object; the difference is PURPOSE and
  whether the interface changes

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Adapter and Facade are the same | Facade simplifies a COMPLEX SUBSYSTEM with a simpler interface; Adapter converts ONE interface to another; Facade typically hides multiple classes, Adapter wraps one |
| Adapter and Decorator are the same | Decorator adds behavior, same interface; Adapter converts interface, behavior identical to Adaptee. If the interface changes: Adapter. If behavior changes: Decorator |
| Adapter should add validation or business logic | No - Adapter's job is TRANSLATION only; business logic in Adapter creates a hidden, untestable dependency. Logic belongs in the service, translation in the Adapter |
| Class Adapter (inheritance) is better in Java | Java does not support multiple inheritance; Object Adapter (composition) is the correct Java variant. Class Adapter is a C++ idiom |
| Adapter violates the Open/Closed Principle | Adapter IS the implementation of OCP: extend the system (via Adapter) without modifying existing code |

---

### 🚨 Failure Modes & Diagnosis

**Adapter With Business Logic - Hidden Coupling**

**Symptom:**
A bug in payment processing is traced to the `StripeAdapter`
- which, in addition to translating the Stripe call, also
applies a discount for preferred customers, converts
currency rates, and enforces spending limits. Testing
the payment service with a mock adapter produces different
results than production because the adapter has business
logic that is not tested separately.

**Root Cause:**
Business logic crept into the Adapter over time because
it was "close to the payment code." The Adapter is now
a hidden second service, not just a translator.

**Diagnostic Signal:**
Ask: "If I replace this Adapter with a mock that does
nothing but record calls, do any tests fail for non-
integration reasons?" If yes: the Adapter contains
business logic.

**Fix:**
Extract business logic from the Adapter into a service
class. The Adapter should contain only parameter translation
code - no conditions on order amount, customer type, etc.
Test the business logic in the service with a mock gateway.
Test the Adapter with a mock Adaptee to verify translation
only.

**Prevention:**
Code review rule: Adapter classes may contain only type
conversion, parameter mapping, and exception translation
code. Any domain condition (if/else based on business
state) is a sign of business logic that belongs in a service.

---

**Cascading Adapter Chain - Interface Archaeology**

**Symptom:**
A senior engineer needs to trace how a payment is processed
and discovers: `PaymentService` → `PaymentGateway` (Target)
→ `StripeAdapter` → `StripeCompatibilityAdapter` →
`StripeV2LegacyAdapter` → actual `StripeClient`. Four
layers of adapters accumulated over three years without
any being removed when the interface was finally updated.

**Root Cause:**
Adapters were added for each interface change but previous
adapters were never removed. Each addition was safe; no
removal was ever prioritized.

**Diagnostic Signal:**
Count adapter layers in an inheritance or delegation chain.
More than 2 layers between client and real implementation
is a design smell requiring review.

**Fix:**
Flatten the adapter chain: create one `StripeAdapter`
that directly adapts `StripeClient` to `PaymentGateway`.
Delete intermediate adapters. This is a refactoring, not
a feature - schedule it explicitly; it will not happen
organically.

**Prevention:**
When an Adaptee interface changes, update the Adapter
directly rather than adding a new Adapter wrapper. Adapters
should have unit tests that make the refactoring safe.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Are Design Patterns and Why They Exist` - vocabulary
  foundation for structural patterns

**Builds On This (learn these next):**
- `Decorator vs Proxy vs Adapter` - deep comparison of
  the three wrapping patterns; essential to distinguish them
  under interview pressure
- `Facade` - the sibling wrapping pattern that simplifies
  a SYSTEM rather than converting one interface

**Alternatives / Comparisons:**
- `Decorator` - same wrapping mechanism, different purpose;
  Decorator adds behavior without changing interface
- `Proxy` - same wrapping mechanism; Proxy controls access
  to the real object, does not change the interface

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Wrapper converting incompatible interface│
│              │ to the interface clients expect          │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Integrating external/legacy code without │
│ SOLVES       │ modifying either side                    │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Adapter = translation only; no business  │
│              │ logic inside the adapter class           │
├──────────────┼──────────────────────────────────────────┤
│ JAVA VARIANT │ Object Adapter (composition) - use this  │
│              │ Class Adapter (inheritance) - avoid in   │
│              │ Java (no multiple inheritance)           │
├──────────────┼──────────────────────────────────────────┤
│ VS DECORATOR │ Same structure, different intent:        │
│              │ Adapter changes interface, Decorator     │
│              │ adds behavior to same interface          │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ SLF4J Logger adapters (Log4j, Logback)   │
│              │ Spring HandlerAdapter, JDBC Driver       │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Business logic creeping into Adapter -   │
│              │ hard to test, hidden side effects        │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Facade → Decorator → Proxy → Bridge      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Adapter changes the INTERFACE; Decorator changes the
   BEHAVIOR. Both wrap an object. This distinction is the
   #1 interview question around structural patterns
2. Object Adapter (composition) is the Java idiom;
   Class Adapter (multiple inheritance) is not applicable
3. Adapter = translation only; business logic in an Adapter
   is an anti-pattern that makes the system harder to test

**Interview one-liner:**
"Adapter converts an incompatible interface into the interface
a client expects. The Object Adapter wraps the Adaptee via
composition and translates calls. SLF4J is the canonical
Java example: the SLF4J Logger interface is the Target;
Log4j/Logback implementations are Adaptees; SLF4J binding
JARs are the Adapters. It's the Structural pattern for
integration without modification."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define your application's interfaces before looking at the
tools you will use. Then write Adapters to connect the tools
to your interfaces. This keeps your application's core
independent of specific tools and makes testing, swapping,
and extending straightforward.

**Where else this pattern appears:**
- **Spring MVC HandlerAdapter** - Spring's `DispatcherServlet`
  uses the `HandlerAdapter` interface to call handlers of
  different types (Controller interface, @RequestMapping
  annotated methods, Servlet). Each type needs a different
  calling convention; HandlerAdapter is the Adapter that
  bridges DispatcherServlet's uniform dispatch to each
  handler's specific invocation method
- **Java InputStreamReader** - converts a byte-oriented
  `InputStream` to a character-oriented `Reader`: the Adaptee
  is InputStream, the Target interface is Reader,
  `InputStreamReader` is the Adapter
- **Hexagonal Architecture** - the entire "Adapters" concept
  in Ports-and-Adapters architecture is this pattern applied
  architecturally: application core = Target, external
  system = Adaptee, adapter class = Adapter

**Industry applications:**
- **Payment gateway integration** - every payment gateway
  (Stripe, PayPal, Adyen) has a different API; each
  integration is an Adapter to a common `PaymentPort`
  interface in the domain model
- **Cloud provider SDK abstraction** - a `StoragePort`
  interface adapted by `S3StorageAdapter`, `GcsStorageAdapter`,
  `AzureBlobStorageAdapter` allows the application core
  to be cloud-provider-independent

---

### 💡 The Surprising Truth

Java's `Arrays.asList()` is an Adapter. It converts an array
(which does not implement `List`) into an object that
implements `List`. The array is the Adaptee; `java.util.List`
is the Target interface; the returned `AbstractList`
subclass is the Adapter. The surprise: the returned List is
a FIXED-SIZE adapter backed by the array. Calling `add()`
on it throws `UnsupportedOperationException` - because the
underlying array cannot grow. This is an Adapter limitation:
the Target interface (`List`) promises `add()`, but the
Adaptee (array) cannot fulfill it. This demonstrates that
Adapters sometimes cannot fully fulfill the Target interface
contract when the Adaptee lacks the required capability -
and that partial fulfillment requires careful documentation
or a different design choice.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [DISTINGUISH] In one sentence each, state the difference
   between Adapter, Decorator, and Proxy - all three wrap
   an object but serve different purposes
2. [BUILD] Implement `InputStreamReader` as an Adapter
   from memory: state the Target interface, the Adaptee,
   and the translation that happens in `read()` method
3. [APPLY] Given a notification service needing to support
   SendGrid and Twilio with a single `NotificationPort`,
   sketch the Adapter design for both third-party SDKs
4. [EXPLAIN] Why is the Object Adapter variant preferred
   over Class Adapter in Java? What Java language feature
   makes Class Adapter impractical?
5. [DIAGNOSE] Given an Adapter that has grown to 200 lines
   and contains `if (order.isPreferred()) discount(...)`,
   identify the anti-pattern and describe the correct
   refactoring

---

### 🧠 Think About This Before We Continue

**Q1.** SLF4J is described as an "Adapter framework." How
does `LoggerFactory.getLogger(MyClass.class)` know which
concrete Logger implementation to return (Logback vs Log4j)?
What mechanism does SLF4J use to discover and select the
binding? Is this an Adapter or an Abstract Factory in the
way it selects the implementation?

*Hint: SLF4J uses classpath discovery - it calls
`org.slf4j.impl.StaticLoggerBinder.getSingleton()` which is
provided by whichever binding JAR is on the classpath.
Only one binding can be active (SLF4J warns if multiple are
detected). The binding JAR provides the Adapter; the binding
selection is closer to Service Locator or Abstract Factory.*

**Q2.** Java's `Collections.unmodifiableList(list)` returns
an unmodifiable view. Is this an Adapter? The returned object
implements `List` (same interface as input) but modifying
operations throw `UnsupportedOperationException`. If it does
not change the interface, is it an Adapter, a Decorator, or
a Proxy?

*Hint: Same interface input and output - not Adapter (Adapter
changes interface). Adds behavior restriction - not pure
Decorator (Decorator adds capability, not removes it). Controls
access (prevents write operations) - most like Proxy
(Protection Proxy). This example demonstrates that pattern
classification by structure alone is insufficient - the PURPOSE
must match. Collections.unmodifiableList IS a Proxy (Protection
Proxy variant), not an Adapter.*

**Q3.** Design an Adapter for a legacy system that takes
XML input but your new service works with JSON. The XML
adapter must: (1) accept the JSON request, (2) convert JSON
to XML, (3) call the legacy service with XML, (4) receive
XML response, (5) convert XML response to JSON, (6) return
JSON response to the caller. What are the error handling
requirements? What happens if the JSON-to-XML conversion
fails for a particular field type?

*Hint: The Adapter must translate both the happy path and
all error conditions. Conversion failure = translate to
a meaningful target-interface exception (not expose XML-
specific errors to JSON callers). The Adapter needs a
serialization library for both directions. Consider: should
the Adapter be stateless (new instance per request) or
stateful (reuse parser instances)? Stateless is simpler;
stateful is faster but requires thread-safety for the
parser instances.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the structural difference between Adapter
and Decorator? Give a code example of each.**

*Why they ask:* Most common structural pattern confusion;
tests precise understanding under pressure.

*Strong answer includes:*
- Both wrap an object via composition (Object Adapter and
  Decorator both hold a reference to the wrapped object)
- DIFFERENCE: Adapter changes the interface (implements a
  DIFFERENT interface than the wrapped object); Decorator
  keeps the same interface (implements the SAME interface
  as the wrapped object, adds behavior)
- Adapter example: `StripeAdapter implements PaymentGateway`,
  wraps `StripeClient` (different API)
- Decorator example: `LoggingPaymentGateway implements
  PaymentGateway`, wraps another `PaymentGateway` (same
  interface, adds logging before/after)

**Q2: Why is composition (Object Adapter) preferred over
inheritance (Class Adapter) in Java for implementing Adapter?**

*Why they ask:* Tests Java-specific pattern implementation
knowledge.

*Strong answer includes:*
- Java does not support multiple inheritance of classes
- Class Adapter would require: `class Adapter extends Adaptee
  implements Target` - not possible if Adaptee is a class
  and Target is also a class (only one class can be extended)
- Object Adapter works with any subclass of Adaptee (not
  tied to a specific class)
- Object Adapter can hold multiple Adaptees if needed
- Composition over inheritance is a general Java best practice:
  "favor composition over inheritance" (Effective Java Item 18)

**Q3: Where does Adapter appear in Java's standard library?
Give two examples.**

*Why they ask:* Tests ability to recognize patterns in
production code.

*Strong answer includes:*
- `Arrays.asList()`: Adaptee = array (Object[]), Target =
  `java.util.List`, Adapter = the returned fixed-size List
- `InputStreamReader`: Adaptee = `InputStream` (byte stream),
  Target = `Reader` (char stream), Adapter =
  `InputStreamReader` which reads bytes and decodes with
  a charset to produce chars
- Spring's `HandlerAdapter`: Adaptee = various handler
  types (@Controller, Servlet, HttpRequestHandler), Target =
  `HandlerAdapter.handle()`, Adapters = `RequestMappingHandlerAdapter`,
  `SimpleServletHandlerAdapter`, etc.

