---
id: CSF-091
title: Paradigm-Agnostic Problem Decomposition
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-086, CSF-001, CSF-002, CSF-014
used_by:
related: CSF-086, CSF-089, CSF-092, CSF-002, CSF-014
tags: [meta-skill, decomposition, problem-solving, paradigm, design]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 91
permalink: /technical-mastery/csf/paradigm-agnostic-problem-decomposition/
---

⚡ TL;DR - Paradigm-agnostic problem decomposition: split the problem into sub-problems
BEFORE choosing how to express the solution. The decomposition strategy emerges from
the PROBLEM STRUCTURE - not from the programmer's preferred paradigm. Four decomposition
lenses: functional (what transformations?), object (what entities and lifecycles?),
data (what data structures and access patterns?), and behavioral (what events and
state machines?). Choose the lens that fits the problem. Most real systems need all four
in different subsystems.

| #091 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-086 (Paradigm-Agnostic Thinking), CSF-001 (CS Map), CSF-002 (Why Paradigms Exist), CSF-014 (OOP) | |
| **Used by:** | (all architecture and design decisions) | |
| **Related:** | CSF-086 (Paradigm-Agnostic Thinking), CSF-089 (First-Principles Language Selection), CSF-092 (Trade-off as First-Principles Lens), CSF-002 (FP), CSF-014 (OOP) | |

---

### 🔥 The Problem This Solves

**PARADIGM-FIRST DECOMPOSITION: THE SILENT PRODUCTIVITY KILLER:**

Every programmer learns a dominant paradigm first. Java engineers: learn to decompose
problems into classes and objects. Functional programmers: decompose into transformations
and pipelines. Procedural programmers: decompose into procedures and shared state.

The pattern: engineers carry their decomposition habit into EVERY problem, regardless
of whether it fits:

```
JAVA ENGINEER ENCOUNTERS A DATA PIPELINE PROBLEM:
  "Process 10M records: parse CSV, validate, transform, aggregate."
  
  PARADIGM-FIRST DECOMPOSITION (OOP habit):
    class CsvRecord { ... }
    class CsvParser { ... }
    class Validator { ... }
    class Transformer { ... }
    class Aggregator { ... }
    
  RESULT: 5 classes, 200 lines of boilerplate, stateful objects
  passing records between them. The natural structure of this
  problem (a linear transformation pipeline) is HIDDEN inside
  class hierarchies. The code: harder to read, harder to test,
  harder to parallelize.
  
  PROBLEM-FIRST DECOMPOSITION:
    "What IS this problem? A data transformation pipeline:
    input -> parse -> validate -> transform -> aggregate -> output.
    Each step: a PURE FUNCTION. No shared state. No side effects."
    
  FUNCTIONAL DECOMPOSITION:
    parse: RawBytes -> CsvRecord
    validate: CsvRecord -> Either<ValidationError, ValidRecord>
    transform: ValidRecord -> TransformedRecord
    aggregate: Stream<TransformedRecord> -> AggregationResult
    
  RESULT: 4 composable functions. Parallelizable via Stream.parallel().
  Testable independently. The problem structure: directly visible in
  the solution structure.
```

The Java engineer's OOP habit: produced a technically correct but unnecessarily complex
solution. The paradigm-agnostic decomposition: revealed the natural structure.

**THE REVERSE FAILURE: FP FORCED ONTO OOP PROBLEMS:**

```
FUNCTIONAL PROGRAMMER ENCOUNTERS A DOMAIN MODEL PROBLEM:
  "Model a bank account with complex business rules:
   overdraft limits, daily withdrawal caps, transaction history."
  
  PARADIGM-FIRST (FP habit):
    type Account = { balance: number; history: Transaction[] }
    const withdraw = (acc: Account, amount: number): Account => ...
    // Immutable updates everywhere. State threading explicit.
    
  RESULT: explicit state threading through every operation.
  Overdraft check requires reading current balance AND daily history.
  Transaction addition requires creating a new Account object.
  Business rules: scattered across pure functions with no co-location.
  
  PROBLEM-FIRST DECOMPOSITION:
    "What IS this problem? An ENTITY with a lifecycle, business
    invariants, and a history of mutations. Entity = lifecycle +
    invariants + mutation semantics. This is the OOP core problem."
    
  OOP DECOMPOSITION:
    class BankAccount {
      private balance: Money;
      private dailyWithdrawals: DailyWithdrawalTracker;
      // Invariants co-located with entity
      void withdraw(Money amount) {
        this.overdraftPolicy.validate(this, amount);
        this.dailyLimitPolicy.validate(this, amount);
        this.balance = this.balance.subtract(amount);
        this.history.record(new Withdrawal(amount));
      }
    }
    
  RESULT: business invariants co-located with the entity they protect.
  Mutation semantics explicit. History naturally encapsulated.
```

**PROBLEM-FIRST DECOMPOSITION PREVENTS BOTH FAILURES.**

---

### 📘 Textbook Definition

**Problem Decomposition:** The process of breaking a complex problem into smaller
sub-problems that can be independently understood, implemented, and verified. The
goal: reduce the cognitive load of each sub-problem below the complexity threshold
where a single engineer can reason about it completely.

**Paradigm-Agnostic Decomposition:** Breaking a problem into sub-problems WITHOUT
assuming a particular paradigm (OOP, FP, procedural). The sub-problems are defined
in terms of the PROBLEM DOMAIN (what are the natural chunks of this problem?) not
in terms of the SOLUTION PARADIGM (what classes should I create?). The paradigm
is selected AFTER the decomposition is complete, based on which paradigm best expresses
each sub-problem's natural structure.

**Four Decomposition Lenses:**

1. **Functional Decomposition** (WHAT transformations?): Break the problem into
   a sequence of functions that transform data. Natural for: pipelines, data processing,
   stateless services. Signal: problem = "transform X to Y."

2. **Object Decomposition** (WHAT entities?): Break the problem into entities with
   state and behavior. Natural for: domain models, business logic, simulations. Signal:
   problem = "manage entity lifecycle with invariants."

3. **Data Decomposition** (WHAT structure?): Break the problem by data access pattern.
   Natural for: storage systems, indexes, caches. Signal: problem = "organize and retrieve
   data efficiently at scale."

4. **Behavioral Decomposition** (WHAT events?): Break the problem into states and
   transitions triggered by events. Natural for: UI, workflows, protocol handlers.
   Signal: problem = "respond to events, transition between states."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Decompose the PROBLEM first (what are the natural chunks?). Choose the PARADIGM second
(what best expresses each chunk?). Never reverse this order.

**One analogy:**

> Cooking analogy: recipe vs. grocery list.
>
> PARADIGM-FIRST (start from your tools):
>   "I have a frying pan, a steamer, and an oven.
>    What meal can I cook with these tools?"
>   -> You cook what your tools afford. You may not cook what you wanted.
>
> PROBLEM-FIRST (start from the meal):
>   "I want to make Thai green curry."
>   -> Step 1: decompose the recipe (sauce, protein, vegetables, rice).
>   -> Step 2: for each sub-task, choose the best tool.
>      Sauce: food processor. Protein: frying pan. Rice: rice cooker.
>   -> You cook what the PROBLEM calls for.
>
> Most programmers start from their tools (paradigm).
> Paradigm-agnostic decomposition: starts from the meal (problem).
> The tools (paradigm) are chosen to match the recipe (problem structure).

**One insight:**

The four decomposition lenses correspond to the four questions a problem can ask:
"WHAT does this transform?" (functional), "WHAT entity is this about?" (object),
"WHAT data structure enables this?" (data), "WHAT event triggers this?" (behavioral).
These questions are not paradigm-specific - they can be asked about ANY problem.
The answers: tell you which paradigm naturally fits each sub-problem.

---

### 🔩 First Principles Explanation

**THE DECOMPOSITION DECISION TREE:**

```
┌──────────────────────────────────────────────────────┐
│ DECOMPOSITION LENS SELECTOR                          │
│                                                      │
│ Q1: IS THE PROBLEM PRIMARILY ABOUT TRANSFORMING     │
│     DATA FROM ONE FORM TO ANOTHER?                  │
│     (Input -> Processing -> Output)                 │
│                                                      │
│     YES -> FUNCTIONAL DECOMPOSITION                 │
│       Sub-problem: each transformation step.        │
│       Structure: composed functions or pipeline.    │
│       Examples: ETL pipeline, API request handler,  │
│         compiler pass, data validation chain.       │
│                                                      │
│ Q2: IS THE PROBLEM ABOUT MANAGING ENTITIES THAT     │
│     HAVE IDENTITY, STATE, AND BUSINESS RULES?       │
│     (Lifecycle, invariants, mutations)              │
│                                                      │
│     YES -> OBJECT DECOMPOSITION                     │
│       Sub-problem: each entity and its rules.       │
│       Structure: classes with encapsulated state.   │
│       Examples: bank account, order, user profile,  │
│         inventory item, subscription.               │
│                                                      │
│ Q3: IS THE PROBLEM ABOUT HOW TO EFFICIENTLY         │
│     STORE, RETRIEVE, OR ORGANIZE DATA AT SCALE?    │
│     (Access patterns, query efficiency, storage)   │
│                                                      │
│     YES -> DATA DECOMPOSITION                       │
│       Sub-problem: each access pattern / structure. │
│       Structure: data structures, indexes, schemas. │
│       Examples: database schema, cache design,      │
│         search index, event store, graph DB schema. │
│                                                      │
│ Q4: IS THE PROBLEM ABOUT RESPONDING TO EVENTS AND  │
│     TRANSITIONING BETWEEN STATES OVER TIME?         │
│     (Asynchronous events, state machines, UI)       │
│                                                      │
│     YES -> BEHAVIORAL DECOMPOSITION                 │
│       Sub-problem: each state and transition.       │
│       Structure: state machines, event handlers.    │
│       Examples: checkout flow, network protocol,    │
│         game loop, order fulfillment workflow,      │
│         WebSocket session.                          │
└──────────────────────────────────────────────────────┘
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential complexity:** the inherent complexity of the problem.
A bank account with overdraft policies HAS business rules that must be checked.
That complexity cannot be removed. It is ESSENTIAL.

**Accidental complexity:** complexity introduced by the solution structure.
If the business rules are scattered across 15 functions because a functional
decomposition was forced onto an entity-lifecycle problem: that scattering IS
accidental complexity. It was introduced by the DECOMPOSITION CHOICE, not by
the PROBLEM itself.

**Paradigm-agnostic decomposition:** minimizes accidental complexity by choosing
the decomposition strategy that aligns with the problem structure. When the solution
structure mirrors the problem structure: engineers can navigate both simultaneously.
When they diverge: every change to the problem requires understanding two structures
and mapping between them.

---

### 🧪 Thought Experiment

**E-COMMERCE: FOUR DECOMPOSITIONS OF THE SAME SYSTEM**

An e-commerce system has the same underlying problem. How does each decomposition lens
see it?

```
PROBLEM: "Process online orders: cart -> checkout -> payment -> fulfillment."

FUNCTIONAL LENS (what transformations?):
  cart -> validateCart() -> addTaxes() -> calculateShipping()
       -> checkout -> processPayment() -> createOrder()
       -> fulfillOrder() -> notifyCustomer()
  Each: a pure function transforming an order state.
  NATURAL FOR: the payment processing pipeline (each step
    transforms the order record).
  NOT NATURAL FOR: managing the order entity's lifecycle
    over days (order can be modified, disputed, refunded).

OBJECT LENS (what entities?):
  class Order { ... }
  class Cart { ... }
  class Customer { ... }
  class Product { ... }
  class Payment { ... }
  class Shipment { ... }
  NATURAL FOR: the domain model (each entity has identity,
    state, and business rules).
  NOT NATURAL FOR: the payment processing pipeline (objects
    make it harder to see the linear transformation flow).

DATA LENS (what access patterns?):
  orders table: by order_id, by customer_id, by status, by date.
  products table: by product_id, by category, full-text search.
  inventory: by product_id (frequently updated, must be consistent).
  cart: by session_id (ephemeral, frequent reads/writes, TTL).
  NATURAL FOR: database schema and caching strategy.
  NOT NATURAL FOR: business rule enforcement.

BEHAVIORAL LENS (what events?):
  ORDER STATE MACHINE:
    PENDING -> PAYMENT_RECEIVED -> PROCESSING ->
    SHIPPED -> DELIVERED (or RETURNED or DISPUTED)
  Events: PaymentReceived, OrderShipped, OrderDelivered,
    ReturnRequested, DisputeOpened.
  NATURAL FOR: order fulfillment workflow, async processing.
  NOT NATURAL FOR: the payment calculation (no state machine).

THE SYNTHESIS:
  A real e-commerce system needs ALL FOUR:
  - Payment pipeline: functional decomposition.
  - Domain model: object decomposition.
  - Database and caching: data decomposition.
  - Order workflow: behavioral decomposition.
  
  The mistake: applying ONE lens to the whole system.
  The solution: applying each lens to the subsystem it fits.
```

---

### 🎯 Mental Model / Analogy

**THE CARTOGRAPHY ANALOGY**

```
┌──────────────────────────────────────────────────────┐
│ FOUR MAPS OF THE SAME CITY                          │
│                                                      │
│ A city has one physical reality.                    │
│ But cartographers make DIFFERENT MAPS depending on  │
│ what QUESTION they are answering.                   │
│                                                      │
│ ROAD MAP (functional):                              │
│   "How do I get from A to B?"                       │
│   Shows: routes, connections, directions.           │
│   Natural for: navigation (sequential steps).       │
│   Useless for: finding property ownership.          │
│                                                      │
│ PROPERTY MAP (object):                              │
│   "Who owns what parcel?"                           │
│   Shows: parcels, owners, zoning.                   │
│   Natural for: real estate (entity with identity).  │
│   Useless for: navigation.                          │
│                                                      │
│ UTILITY MAP (data):                                 │
│   "Where are the water mains?"                      │
│   Shows: infrastructure by access type.             │
│   Natural for: infrastructure (data by pattern).    │
│   Useless for: property records.                    │
│                                                      │
│ ZONING MAP (behavioral):                            │
│   "What can happen in this area?"                   │
│   Shows: states (residential, commercial, industrial)│
│   and allowed transitions.                          │
│   Natural for: planning (states and transitions).   │
│   Useless for: navigation.                          │
│                                                      │
│ PARADIGM-AGNOSTIC DECOMPOSITION:                    │
│ Using the RIGHT MAP for each question.              │
│ Not: using the road map for everything because      │
│   you know how to read road maps.                   │
│ Real cities (and real software): require all four.  │
└──────────────────────────────────────────────────────┘
```

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
When you have a big problem, you break it into smaller pieces before you start solving.
But the WAY you break it up should match the SHAPE of the problem. Breaking a sandwich
into three layers (bread, filling, bread) is the right decomposition for eating.
Breaking it into columns (left, middle, right) is wrong for the problem.

**Level 2 - Student:**
Two ways to decompose "build a calculator":
- OOP: `class Calculator`, `class Operation`, `class Display` (entity-focused)
- FP: `parse: String -> Tokens`, `evaluate: Tokens -> Number`, `display: Number -> String`
  (transformation-focused)

For a simple calculator: the FP decomposition is more natural (it IS a transformation
pipeline: text in -> number out). The OOP decomposition: forces entities onto a
transformation problem, adding unnecessary complexity. Match the decomposition to
the PROBLEM SHAPE, not to your preferred paradigm.

**Level 3 - Professional:**
Mixed decomposition in a real service:
```java
// Spring Boot REST service: e-commerce order placement.
// NOT uniform OOP across the whole service.

// FUNCTIONAL decomposition for request validation pipeline:
//   parseRequest -> validateCart -> calculatePricing
//   -> applyDiscounts -> validatePayment -> placeOrder
// Each: a function transforming an OrderRequest.
// Modeled as: @Component methods, or a Chain-of-Responsibility.

// OBJECT decomposition for the domain model:
//   Order, Cart, Customer, Product, Payment
// Each: an entity with identity, state, business rules.
// Modeled as: @Entity / domain objects.

// DATA decomposition for persistence:
//   Orders table: queries by status (polling), by customer,
//   by date range (reporting).
//   Product index: full-text search (Elasticsearch).
//   Session cart: Redis key (TTL-based).
// Modeled as: JPA entity + repository per access pattern.

// BEHAVIORAL decomposition for workflow:
//   OrderState: PENDING -> CONFIRMED -> PROCESSING ->
//   SHIPPED -> DELIVERED
//   Events: OrderConfirmed, PaymentFailed, OrderShipped.
// Modeled as: Spring StateMachine or event-driven @EventListener.

// The full service: uses ALL FOUR decompositions.
// Each subsystem: uses the one that fits its nature.
```

**Level 4 - Senior Engineer:**
Decomposition signals for common problem types:
```
Signal: "Process X in a pipeline."
-> Functional. Data flows through composed transformations.
   Java: Stream API, CompletableFuture.thenApply().
   Problem if OOP: each step is a class with process() method.
   "Visitor Pattern over your pipeline" = accidental complexity.

Signal: "Model a domain with complex business rules."
-> Object. Entity lifecycle + invariants + mutation semantics.
   Java: rich domain objects with package-private fields.
   Problem if FP: state threading through all functions.
   "Pass account record to every function" = accidental complexity.

Signal: "Build an async workflow with failure/retry."
-> Behavioral. States (PROCESSING, FAILED, RETRYING) and
   transitions triggered by events (Success, Failure, Timeout).
   Java: Spring State Machine, Temporal.io workflow, or
   explicit state machine with sealed classes + switch.
   Problem if OOP: scattered if-else chains checking status strings.
   "Check order.getStatus().equals('FAILED') everywhere" = accidental.

Signal: "Optimize a query over 1B records."
-> Data. Access patterns, not entity lifecycle.
   Decompose by: which queries need fast reads? Which need
   consistent writes? What are the cardinalities and joins?
   Design the schema for the queries, not for the entities.
   Problem if OOP: entity-first schema (normalized for the entity,
   not for the queries). "SELECT * FROM orders JOIN customers JOIN..."
   = accidental complexity from wrong decomposition lens.
```

**Level 5 - Expert:**
Conway's Law as decomposition constraint:
```
"Organizations design systems that mirror their own communication structure."
  - Melvin Conway, 1968.

IMPLICATION: the decomposition you CHOOSE creates the system boundaries.
System boundaries: create team boundaries (or vice versa).
Team boundaries: create communication overhead (and coordination cost).

EXPERT APPLICATION:
  When decomposing a large system: the decomposition IS an
  organizational decision, not just a technical one.

  "Do we decompose this as a monolith (single decomposition boundary:
   the module/package) or as microservices (decomposition boundary:
   the service/network)?"

  TEAM-SIZE-BASED DECOMPOSITION RULE:
    Two-pizza team (6-10 engineers): monolith decomposition.
      Each module = a team member or a pair. Low coordination cost.
      Microservices introduce deployment, testing, and operational overhead
      that a small team cannot absorb.
    Multiple two-pizza teams: microservice decomposition.
      Each service = one two-pizza team. Explicit API boundaries replace
      implicit module boundaries. The coordination cost is now explicit
      (service contracts) rather than hidden (module coupling).
  
  WRONG DECOMPOSITION SIGNALS AT SCALE:
    "We need to call 12 microservices to render a product page."
    = The decomposition crossed a BEHAVIORAL boundary (rendering one
      web page) with too many OBJECT/ENTITY boundaries (12 services).
    FIX: aggregate read-side view (BFF pattern) that denormalizes
    data for the behavioral (rendering) boundary.

  THE DECOMPOSITION IS NEVER FINAL:
    Initial decomposition: based on known problem structure.
    After 12 months in production: the problem structure reveals
    itself. Some decomposition boundaries: too coarse (module too
    large for a team). Some: too fine (services with no independent
    deployment reason). Refactor the decomposition when the signal
    is clear. The decomposition: is hypothesis, not ground truth.
```

---

### ⚙️ How It Works

**THE FIVE-STEP PARADIGM-AGNOSTIC DECOMPOSITION PROCESS:**

```
┌──────────────────────────────────────────────────────┐
│ STEP 1: DESCRIBE THE PROBLEM IN DOMAIN TERMS        │
│   Use NO technical vocabulary. No "class", "table", │
│   "function", "service". Pure domain language.      │
│   "Users put items in a cart, provide payment,      │
│    receive an order confirmation, goods are shipped."│
│                                                      │
│ STEP 2: IDENTIFY NATURAL PROBLEM BOUNDARIES         │
│   Find the seams: where does one "concern" end and  │
│   another begin?                                    │
│   "Cart management | Payment processing |           │
│    Order fulfillment | Shipping notification."      │
│   These are the SUB-PROBLEMS. Natural seams exist   │
│   in the problem domain, not in the solution.       │
│                                                      │
│ STEP 3: CLASSIFY EACH SUB-PROBLEM BY LENS           │
│   For each sub-problem:                             │
│   - Transformation? -> Functional lens.             │
│   - Entity lifecycle? -> Object lens.               │
│   - Data access? -> Data lens.                      │
│   - Event-driven state? -> Behavioral lens.         │
│                                                      │
│ STEP 4: CHOOSE THE PARADIGM FOR EACH SUB-PROBLEM    │
│   Select the language/paradigm that best expresses  │
│   the lens identified in step 3.                    │
│   Functional lens: Java Stream / CompletableFuture, │
│     Kotlin sequence, Python generator.              │
│   Object lens: Java/Kotlin classes, Spring @Entity. │
│   Data lens: SQL schema, Redis data structure,      │
│     Elasticsearch mapping.                          │
│   Behavioral lens: state machine, event sourcing,   │
│     Temporal workflow, Spring StateMachine.         │
│                                                      │
│ STEP 5: IDENTIFY CROSS-CUTTING CONCERNS             │
│   After decomposing: what crosses ALL sub-problems? │
│   Authentication, authorization, logging, tracing.  │
│   These: implemented as aspects or middleware,      │
│   NOT as cross-cutting concerns in every sub-problem│
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Single Lens vs Mixed Decomposition**

```java
// BAD: OOP lens forced onto a data transformation problem.
// Problem: validate, transform, and enrich incoming Kafka events.

public class KafkaEventProcessor {
    private final EventValidator validator;
    private final EventTransformer transformer;
    private final EventEnricher enricher;
    private final EventPublisher publisher;

    // Objects calling objects: transformation pipeline
    // hidden behind object graph.
    // Testing: requires mocking 4 collaborators.
    // Order of processing: not visible from class structure.
    public void process(RawEvent raw) {
        ValidatedEvent validated = validator.validate(raw);
        TransformedEvent transformed = transformer.transform(
            validated);
        EnrichedEvent enriched = enricher.enrich(transformed);
        publisher.publish(enriched);
    }
}
// The real structure (linear pipeline) is invisible.
// A new engineer: must trace all 4 classes to understand
// the processing order.

// GOOD: Functional lens for a transformation pipeline.
// The decomposition matches the problem structure: a pipeline.

public class KafkaEventPipeline {

    // Problem decomposition as composed functions.
    // Structure of the code = structure of the problem.
    private Function<RawEvent, ValidatedEvent> validate =
        raw -> {
            if (raw.payload() == null)
                throw new ValidationException("null payload");
            return new ValidatedEvent(raw.id(), raw.payload());
        };

    private Function<ValidatedEvent, TransformedEvent> transform =
        v -> new TransformedEvent(
            v.id(),
            v.payload().toUpperCase(),  // e.g. normalize
            Instant.now()
        );

    private Function<TransformedEvent, EnrichedEvent> enrich =
        t -> new EnrichedEvent(
            t.id(),
            t.payload(),
            t.timestamp(),
            lookupMetadata(t.id())  // e.g. add context
        );

    // Pipeline: the transformation order is VISIBLE in the code.
    public EnrichedEvent process(RawEvent raw) {
        return validate
            .andThen(transform)
            .andThen(enrich)
            .apply(raw);
    }
}
// Testing: each function independently testable (no mocking).
// New engineer: reads process() -> understands immediately.
// Adding a step: add .andThen(newStep) in one place.
```

**Example 2 - Production: Mixed Decomposition in a Real Service**

```java
// PRODUCTION: payment service using mixed decomposition.

// ----- OBJECT LENS: domain entity with invariants -----
public class Payment {
    private final String id;
    private Money amount;
    private PaymentStatus status;  // State field

    // Business rule co-located with the entity.
    public void markSuccessful() {
        if (this.status != PaymentStatus.PENDING) {
            throw new IllegalStateException(
                "Cannot mark non-pending payment successful");
        }
        this.status = PaymentStatus.SUCCESSFUL;
    }

    public void markFailed(String reason) {
        if (this.status != PaymentStatus.PENDING) {
            throw new IllegalStateException(
                "Cannot mark non-pending payment failed");
        }
        this.status = PaymentStatus.FAILED;
    }
}

// ----- FUNCTIONAL LENS: payment validation pipeline -----
// Each step: pure function. Composable. Testable.
private Function<PaymentRequest, ValidatedPayment> validateAmount =
    req -> {
        if (req.amount().isNegativeOrZero())
            throw new InvalidAmountException(req.amount());
        return new ValidatedPayment(req);
    };

private Function<ValidatedPayment, AuthorizedPayment> authorizePayment =
    vp -> gatewayClient.authorize(vp);

// ----- BEHAVIORAL LENS: payment workflow (state machine) ----
// States: PENDING -> AUTHORIZED -> CAPTURED -> REFUNDED
// Transitions driven by external events (gateway callbacks).
@Service
public class PaymentWorkflow {
    // Spring StateMachine or explicit event handler:
    @EventListener
    public void onGatewayAuthorized(GatewayAuthorizedEvent event) {
        Payment payment = paymentRepo.findById(event.paymentId());
        payment.markSuccessful();
        paymentRepo.save(payment);
        eventPublisher.publish(new PaymentSuccessEvent(payment));
    }
}

// ----- DATA LENS: access pattern-driven schema -----
// Queries: by customerId+status (pending payments),
//          by gatewayRef (reconciliation).
// Schema designed for the queries:
// CREATE INDEX idx_payments_customer_status
//   ON payments(customer_id, status)
//   WHERE status = 'PENDING';
// CREATE UNIQUE INDEX idx_payments_gateway_ref
//   ON payments(gateway_reference_id);
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Paradigm-agnostic decomposition means choosing a language that supports all paradigms" | The paradigm (and language) is chosen AFTER the decomposition, not before. Paradigm-agnostic decomposition means the ANALYSIS of the problem structure is done before any implementation language or paradigm is fixed. Even in a single-paradigm language (e.g., Java pre-lambdas): you can apply functional decomposition for pipeline problems using patterns like Chain-of-Responsibility, and object decomposition for entity problems using rich domain objects. The decomposition is independent of the language implementation. |
| "Breaking a problem into sub-problems always means breaking it into microservices" | Sub-problems can be implemented as modules, packages, classes, methods, or services depending on the scale of the problem and the team structure. A decomposition into four sub-problems: may be four methods in a single class (small problem), four modules in a monolith (medium problem), or four microservices (large problem with independent deployment requirements). The DECOMPOSITION is the analytical step. The PACKAGING (methods/modules/services) is the implementation decision, driven by operational requirements like independent deployability and team ownership, not by the decomposition itself. |
| "Functional decomposition means using a functional programming language" | Functional decomposition (breaking the problem into transformation steps) can be implemented in any language: Java Streams, Python generators, Go channels, SQL (pure functional: every query is a transformation). Conversely, a "functional programming language" like Haskell can implement object decomposition using type classes that model entity behavior. The decomposition LENS is a way of thinking about the problem; the IMPLEMENTATION can use any language's features to express it. |
| "The correct decomposition is obvious once you understand the problem" | Problem decomposition is a SKILL that requires practice, not an automatic result of understanding. Two engineers who fully understand the same problem may decompose it differently, and both decompositions can be valid with different trade-offs. What makes one decomposition BETTER: it aligns with the problem structure (low accidental complexity), it can be verified (sub-problems are independently testable), and it minimizes cross-boundary coordination (low coupling). These qualities: evaluated AFTER the decomposition is proposed, not determined automatically when the problem is understood. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Anemic Domain Model (OOP Problem, Functional Lens)**

**Symptom:** Domain objects are pure data containers (getters/setters only). All
business logic lives in service classes. Business rules: scattered across 10 service
methods. An overdraft check lives in `WithdrawalService.checkOverdraft()`, not in
`BankAccount.withdraw()`.

**Diagnosis:**
```java
// SYMPTOM: Business rule in service, not in entity.
// BAD: Anemic domain model.
public class BankAccount {
    private double balance;  // Just data
    public double getBalance() { return balance; }
    public void setBalance(double b) { balance = b; } // No rules!
}

public class WithdrawalService {
    // Business rule outside the entity that owns the data.
    public void withdraw(BankAccount account, double amount) {
        if (account.getBalance() - amount < -500) { // Overdraft
            throw new OverdraftException();
        }
        account.setBalance(account.getBalance() - amount);
    }
}
// PROBLEM: BankAccount has no protection. Anyone can call
// account.setBalance(-9999999) and bypass the rule.
// Multiple callers: each must duplicate the overdraft check.

// DIAGNOSIS SIGNAL: Domain object fields are public or have
// setters. Business rules are in Service, Manager, or Helper
// classes rather than in the entities they protect.

// FIX: Apply object lens correctly. Move rules to entity.
public class BankAccount {
    private Money balance;
    private OverdraftPolicy overdraftPolicy;

    public void withdraw(Money amount) {
        // Rule co-located with entity. Protected invariant.
        overdraftPolicy.validate(this.balance, amount);
        this.balance = this.balance.subtract(amount);
    }
}
```

---

**Failure Mode 2: Feature Envy (Object Problem, Procedural Lens)**

**Symptom:** Methods in class A constantly access data from class B. The method
"wants to be" in class B but was placed in A because of procedural thinking
(grouped by the action performed, not by the entity being managed).

**Diagnosis:**
```java
// SYMPTOM: ShippingCalculator uses only Order fields.
// BAD: Feature envy - wrong decomposition placement.
public class ShippingCalculator {
    public double calculate(Order order) {
        // This method only uses Order data.
        // It "lives" in the wrong place.
        return order.getWeight() * order.getShippingZone().getRate()
            + order.getItems().size() * 0.10;
    }
}

// FIX: The method belongs in Order (it uses Order's data).
// Move it to where the data lives.
public class Order {
    // Shipping calculation uses Order data -> belongs here.
    public Money calculateShippingCost() {
        return this.weight.multiply(
            this.shippingZone.getRate()
        ).add(Money.of(this.items.size() * 0.10));
    }
}
```

---

**Security Note:**

Wrong decomposition creates security vulnerabilities:

1. **Anemic domain model = bypassed security invariants:**
   ```java
   // BAD: Public setter bypasses authorization check.
   user.setRole("ADMIN");  // No check! Anyone can escalate role.
   
   // GOOD: Encapsulated in entity with authorization.
   user.promoteToAdmin(currentUser);  // Entity enforces permission check.
   // Object lens: business rule (role change requires permission)
   // co-located with entity (User) that owns the rule.
   ```

2. **Functional lens exposes too many transformation steps:**
   ```java
   // BAD: Expose intermediate transformation results.
   RawRequest raw = parseRequest(httpRequest);  // Contains PII
   logRequest(raw);  // LOGS PII BEFORE SANITIZATION
   ValidatedRequest validated = validate(raw);
   
   // GOOD: Sanitize before any logging or external access.
   ValidatedRequest validated = parseAndSanitize(httpRequest);
   logRequest(validated);  // Only sanitized data logged
   ```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Paradigm-Agnostic Thinking` (CSF-086) - the broader principle of which this is the application
- `Why Programming Paradigms Exist` (CSF-002) - why different paradigms have different decomposition strengths

**Builds On This (learn these next):**
- `Technology Trade-off as First-Principles Lens` (CSF-092) - how to evaluate trade-offs in the decomposition
- `Cross-Paradigm Design Patterns` (CSF-087) - specific patterns for each decomposition lens

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ LENS       │ Signal              │ Paradigm           │
├────────────┼─────────────────────┼────────────────────┤
│ Functional │ Transform X into Y  │ FP / Stream API    │
│ Object     │ Entity + invariants │ OOP / DDD          │
│ Data       │ Access patterns     │ SQL / Redis schema │
│ Behavioral │ Events + states     │ State machine / EDA│
├────────────┴─────────────────────┴────────────────────┤
│ PROCESS:                                               │
│   1. Describe in domain terms (no technical vocab)    │
│   2. Find natural seams (sub-problems)                │
│   3. Classify each seam by lens                       │
│   4. Choose paradigm per sub-problem                  │
│   5. Handle cross-cutting concerns separately         │
├──────────────────────────────────────────────────────┤
│ SIGNALS OF WRONG DECOMPOSITION:                       │
│   Anemic domain model -> use object lens for entities │
│   Feature envy -> method in wrong class/module        │
│   God class -> too coarse (split further)             │
│   Chatty API calls -> too fine (merge sub-problems)   │
└──────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Decompose the PROBLEM first, choose the PARADIGM second. The decomposition is
   an analysis of the problem's natural structure - transformations, entities,
   data access patterns, or event-driven states. The paradigm: is the implementation
   choice that best expresses each sub-problem's structure. Reversing this order
   (choosing paradigm first, forcing decomposition to fit) creates accidental complexity.
2. Four decomposition lenses: Functional (transformation pipeline), Object (entity
   lifecycle), Data (access patterns), Behavioral (event-driven states). Most real
   systems need all four in different subsystems. The mistake: applying one lens to
   the whole system. The skill: recognizing which lens fits each sub-problem.
3. The signal of wrong decomposition: accidental complexity. Anemic domain models
   (OOP problem decomposed with functional/procedural lens), feature envy (method
   in wrong class), scattered business rules (entity invariants in service layer).
   Correct the lens, not the symptoms.

**Interview one-liner:**
"Paradigm-agnostic decomposition: break the problem into sub-problems BEFORE
choosing a paradigm. Four lenses: functional (transformation), object (entity
lifecycle), data (access patterns), behavioral (events and states). Apply the
lens that fits each sub-problem's structure. Real systems: use all four. The wrong
lens creates accidental complexity: anemic models, feature envy, scattered invariants."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
STRUCTURE FOLLOWS PROBLEM, NOT SOLUTION. The decomposition principle applies
beyond programming paradigms:

- **Database normalization:** normalize to the PROBLEM structure (3NF: each
  fact in one place). Denormalize only for specific ACCESS PATTERNS (data lens).
  Don't denormalize because you prefer flat structures (solution preference).
- **Microservices decomposition:** decompose by BOUNDED CONTEXT (domain-driven
  design: where do the domain terms have different meanings?). Not by technology
  stack ("one service per programming language") or by team size alone.
- **Team decomposition (inverse Conway):** structure teams to match the desired
  SYSTEM architecture. If you want independent services: build independent teams.
  If you want a monolith: avoid team silos.
- **API design:** decompose endpoints by RESOURCE (REST: noun-based, object lens)
  or by COMMAND (RPC/GraphQL: verb-based, functional lens) based on what the API
  is modeling - state (REST) or operations (RPC).

---

### 💡 The Surprising Truth

The "correct" decomposition of a problem can change over time - not because the
problem changes, but because the SCALE changes. A monolith with module-level
decomposition IS the correct decomposition for a 3-person team building a startup.
The SAME application with the SAME problem domain: needs a completely different
decomposition (service-level boundaries, event-driven) for a 300-person engineering
organization. This is NOT because the technical problem changed - the e-commerce
problem is the same at 100 orders/day and at 10M orders/day. It changed because
the ORGANIZATIONAL problem (how do 300 engineers coordinate changes without blocking
each other?) changed. Conway's Law: the system structure MUST mirror the communication
structure. The decomposition: is as much a social engineering problem as a technical
one. This is why "copy Netflix's microservices architecture" for a 5-person startup:
is not just wasteful (operationally expensive for a small team) but WRONG (the
decomposition solves a coordination problem that does not exist at 5 people).
The correct decomposition: is always relative to the problem AND the team that
will maintain it.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[LENS IDENTIFICATION]** Given a problem description (e.g., "calculate tax for an order
   checkout"), identify which of the four decomposition lenses (functional, object, data,
   behavioral) is most natural, and explain WHY using the problem's signal characteristics.

2. **[WRONG LENS DIAGNOSIS]** Read a code snippet with an anemic domain model. Identify:
   (a) which decomposition lens was applied, (b) which lens should have been applied,
   (c) what specific accidental complexity was introduced by the mismatch.

3. **[MIXED DECOMPOSITION]** For a payment service (validation pipeline + domain entity +
   database schema + async workflow): decompose it using the correct lens for each
   subsystem and explain the paradigm you would use to implement each.

4. **[REFACTORING]** Given a "god class" with 50 methods (a common result of wrong
   decomposition): use the four lenses to identify natural seams and propose a
   decomposition into smaller units with clear boundaries.

5. **[SCALE ARGUMENT]** Explain why a correct decomposition for a 5-person team may
   be incorrect for a 100-person team, using Conway's Law and the organizational
   dimension of decomposition decisions.

---

### 🧠 Think About This Before We Continue

**Q1.** You are reviewing a Spring Boot service where every entity has only getters,
setters, and no behavior. All business logic is in 15 service classes. What decomposition
lens mismatch does this indicate? What is the accidental complexity it creates?
How would you fix it, and what migration risks does the fix introduce?

*Hint: DIAGNOSIS AND FIX:

LENS MISMATCH: The entities have the structure of a data decomposition (pure data
containers) applied to an entity-lifecycle problem (objects with invariants).
The service classes are applying a functional/procedural lens to entity management.

ACCIDENTAL COMPLEXITY CREATED:
1. Business rules scattered: the "account overdraft" rule may exist in 5 different
   service methods. Change the rule: find and update 5 places.
2. No protection of invariants: setters allow any caller to set any value without
   rule enforcement. account.setBalance(-9999999) is always possible.
3. Testing requires service context: to test one business rule, you need to wire up
   the service class with all its dependencies. Tests: slow and complex.
4. Data and behavior: in separate classes -> high coupling between entity class and
   service class (service class depends on entity structure intimately).

FIX: Introduce rich domain objects. Move business logic from services into entities.

MIGRATION RISKS:
1. Service classes may call setters that bypass rules -> adding rules to entities
   may break existing service callers that relied on unrestricted access.
   FIX: introduce rules incrementally. Each entity: add one rule at a time.
   Identify callers that would violate the rule. Fix them before adding the rule.
2. Testing: existing tests may test service logic that will move to entities.
   FIX: add entity-level unit tests first. Delete corresponding service tests after.
3. Transaction boundaries: services typically own @Transactional. Entities must not
   be @Transactional. The service layer: keeps transaction coordination. Entities:
   purely behavioral (business rules, no persistence concern).

LESSON: Migration from anemic to rich domain model is a significant refactoring.
Do it incrementally, entity by entity. Each entity: add one encapsulated behavior,
remove the corresponding service method, update tests.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is an anemic domain model and why is it a problem?"**

*Why they ask:* Tests understanding of OOP design and domain modeling. Expected for
mid-to-senior engineers at companies using DDD or complex domain logic.

*Strong answer includes:*
- Definition: entities with only getters/setters and no behavior. All business logic
  in service layer. Martin Fowler: "Anemic Domain Model" (2003) - named and described
  the anti-pattern.
- Why it is a problem: business rules scattered across service layer (not co-located
  with the entity they protect). No encapsulation (setters allow invariant violations).
  Service classes are tightly coupled to entity structure (know all field names).
- Root cause: functional/procedural decomposition applied to an entity-lifecycle problem.
  The data (entity) and behavior (services) were separated instead of co-located.
- Fix: rich domain model. Business rules move to entities. Entities: protect their
  own invariants. Service layer: coordination and infrastructure only (transactions,
  external calls), not business logic.

**Q2: "How do you decide whether to decompose a system as a monolith or as microservices?"**

*Why they ask:* Tests systems design judgment and Conway's Law awareness. Expected for
senior and staff engineers.

*Strong answer includes:*
- The decomposition question is SEPARATE from the packaging question (module vs service).
  First: decompose the problem into sub-problems with natural seams (bounded contexts).
  Second: decide whether each seam is implemented as a module (monolith) or a service
  (microservices).
- The packaging decision criteria: does this sub-problem need INDEPENDENT DEPLOYMENT
  (different release cadence, different scaling profile, different on-call team)?
  If no: module in a monolith. If yes: microservice.
- Team size is the strongest signal: less than 20 engineers: monolith default.
  More than 50 engineers: microservices as coordination mechanism.
  20-50 engineers: evaluate per team ownership.
- Anti-pattern: microservices first ("it will scale better"). Microservices add
  operational complexity (distributed tracing, service discovery, contract testing,
  network failure handling) that a small team cannot absorb.
- Conway's Law application: the system structure will mirror the team structure.
  If you want microservice independence: build teams that own their services. If teams
  share code constantly: services will be tightly coupled regardless of the network boundary.

> Entry stub. Generate full content using Master Prompt v4.0.
