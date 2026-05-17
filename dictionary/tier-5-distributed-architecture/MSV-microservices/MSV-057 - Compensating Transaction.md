---
id: MSV-057
title: Compensating Transaction
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-046, MSV-056
used_by: MSV-046, MSV-056
related: MSV-046, MSV-056, MSV-049, MSV-058, MSV-054, MSV-047
tags:
  - microservices
  - distributed
  - deep-dive
  - transactions
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 57
permalink: /microservices/compensating-transaction/
---

# MSV-057 - Compensating Transaction

⚡ TL;DR - A Compensating Transaction is a business
transaction that semantically undoes the effects
of a previously committed transaction. Unlike
database ROLLBACK (which physically reverts
uncommitted data): compensating transactions apply
AFTER commit. They are NEW transactions that
reverse the business effects. Example: PaymentProcessed
-> (failure later) -> PaymentRefunded. PaymentRefunded
IS the compensating transaction. Core mechanism in
Saga Pattern: if a saga step fails, previously
completed steps are undone by compensating transactions
in reverse order.

| #057 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Saga Pattern, Two-Phase Commit | |
| **Used by:** | Saga Pattern, Two-Phase Commit | |
| **Related:** | Saga Pattern, Two-Phase Commit, Eventual Consistency in Microservices, Idempotency in Microservices, Outbox Pattern, Distributed Transaction | |

---

### 🔥 The Problem This Solves

In distributed systems: transactions span multiple
services, each with their own database. 2PC is
impractical. Saga Pattern uses local transactions:
each step commits locally. If step 3 fails after
steps 1 and 2 committed: database ROLLBACK cannot
undo steps 1 and 2 (they are committed in other
services' databases). The solution: execute
compensating transactions for steps 2 and 1 (in
reverse order). Compensating transactions are how
Sagas achieve "undo" without 2PC rollback.

---

### 📘 Textbook Definition

**Compensating Transaction** is a business logic
operation that semantically reverses the effect of
a previously committed transaction. Unlike a database
ROLLBACK (which aborts an uncommitted transaction
by restoring previous state from the transaction
log), a compensating transaction is an independent
committed transaction that applies new business
logic to undo the business effects of a prior
transaction. The history is preserved: both the
original transaction and the compensating transaction
exist in the audit trail. Compensating transactions
must be: idempotent (safe to re-execute if the
compensation itself fails), explicitly designed
(the developer must implement the "undo" logic),
and may not perfectly reverse all effects (e.g.,
an email sent cannot be "unsent" - only a follow-
up email can acknowledge the cancellation).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Compensating transaction: a NEW committed transaction
that reverses the BUSINESS EFFECT of a previous
committed transaction. Not a DB ROLLBACK - a deliberate
undo operation.

**One analogy:**
> You buy a book online (forward transaction:
payment deducted, order created). You later decide
to return it (compensating transaction: refund
processed, order cancelled). The purchase was
never "rolled back" - you can see the original
purchase in your order history. The return is a
separate event. Both are recorded. The net effect:
you have no book and your money back. The bank
cannot "undo" your debit - it issues a credit
(compensating transaction). This is compensating
transaction in everyday business.

**One insight:**
Compensating transactions may be IMPOSSIBLE for
some actions. Sending an email: cannot be unsent.
Printing a document: cannot be unprinted. Launching
a rocket: cannot be unlaunched. For these: you
design "best effort" compensations (send a
cancellation email, notify the rocket is a loss).
In business software: most state changes CAN be
compensated (money: refund; reservation: release;
order: cancel). Design your Saga to identify:
which steps can be fully compensated, which are
partial, and which are irreversible (pivot transactions
- once past this point, compensation changes meaning).

---

### 🔩 First Principles Explanation

**SAGA WITH COMPENSATING TRANSACTIONS:**

```
ORDER PLACEMENT SAGA (3 steps):

FORWARD TRANSACTIONS (T):
  T1: CreateOrder      (order-service)   -> PENDING
  T2: ProcessPayment   (payment-service) -> $deducted
  T3: ReserveInventory (inventory-service)-> 1 unit locked
  T4: ConfirmOrder     (order-service)   -> CONFIRMED

COMPENSATING TRANSACTIONS (C) - reverse of T:
  C3: ReleaseInventory -> undo T3
  C2: RefundPayment    -> undo T2
  C1: CancelOrder      -> undo T1 (T4 not needed if aborted)

FAILURE SCENARIO: T3 fails (insufficient inventory)

  T1: CreateOrder      -> SUCCESS
  T2: ProcessPayment   -> SUCCESS
  T3: ReserveInventory -> FAILED (0 units available)
  
  Saga compensates in reverse:
  C2: RefundPayment    (reverse T2)
  C1: CancelOrder      (reverse T1)
  
  Result: order cancelled, payment refunded
  Audit trail: T1, T2, T3(failed), C2, C1 all recorded
  No database ROLLBACK: each was locally committed
  State: eventually consistent (refund may take 1-3 days
         for credit card; order: immediately cancelled)

PIVOT TRANSACTION:
  T3 is the pivot in this saga
  If T3 succeeds: saga continues to T4 (CONFIRMED)
  If T3 fails: saga compensates backward
  Once T4 completes: saga is COMMITTED (no compensation)
```

**COMPENSATION DESIGN RULES:**

```
RULE 1: IDEMPOTENT
  C2 (RefundPayment) may be called multiple times
  if compensation infrastructure retries
  Must: check if already refunded; skip if yes
  Never: double-refund on duplicate execution

RULE 2: EVENTUALLY EXECUTE
  Compensation must be retried until it succeeds
  If RefundPayment fails (payment service down):
  retry with exponential backoff
  Cannot give up: customer paid and must be refunded

RULE 3: MAY NOT FULLY REVERSE
  Email sent during T2: cannot be unsent
  Best effort: send cancellation email
  Document in saga design: which effects are partial

RULE 4: ORDERED (reverse of forward)
  Compensate in reverse order:
  C3 before C2 before C1
  Reason: business semantics may require ordering
  (cancel order before refunding payment)
```

---

### 🧪 Thought Experiment

**FLIGHT BOOKING SAGA:**

```
FLIGHT + HOTEL + CAR SAGA:
  T1: ReserveFlight   (flight-service)  -> confirmed
  T2: ReserveHotel    (hotel-service)   -> confirmed
  T3: ReserveCar      (car-service)     -> FAILED
                                        (no cars available)
  
  Compensate:
  C2: CancelHotelReservation -> hotel-service
  C1: CancelFlightReservation -> flight-service
  
  COMPLICATION: Hotels have cancellation policies
  If within 24 hours of check-in: 50% fee
  C2 may not FULLY reverse T2 (still pay 50%)
  
  DESIGN DECISION:
  Who bears the 50%? Business rule:
  Option A: user pays (poor UX)
  Option B: system absorbs (business decision)
  Option C: prevent T2 if T3 is unavailable
            (check car availability before hotel)
  
  Best practice: order saga steps to minimize
  expensive-to-compensate steps early
  Put irreversible or expensive steps LAST
  Validate all prerequisites BEFORE executing
```

---

### 🧠 Mental Model / Analogy

> Compensating transactions are like accounting
> journal entries. A debit ($100 expense) cannot
> be deleted from the ledger - it's committed.
> To reverse it: issue a credit entry ($100 credit).
> The ledger shows both: the original debit AND
> the compensating credit. Net effect: zero. Both
> entries exist; the history is complete. This is
> how compensating transactions work: the original
> transaction stays in the audit trail. The compensation
> is a NEW entry. The net business state is as if
> the original transaction never happened - but
> the history records that it did, and that it was
> reversed. This auditability is superior to
> database ROLLBACK which erases history.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A compensating transaction is a "reverse action"
for something that already happened. Like a refund
for a purchase: the purchase isn't deleted; the
refund is a new action. Both are recorded.

**Level 2 - How to design (junior developer):**
For every saga step T: design its compensation C.
Ask: if T succeeds and we need to undo it later,
what API call or event reverses the business effect?
Document T -> C pairs before implementing the saga.
Ensure C is idempotent (can be called multiple
times safely).

**Level 3 - How to implement (mid-level engineer):**
Saga orchestrator: on failure, iterate backward
through completed steps and call their compensation
APIs. Each compensation: idempotent, retried with
backoff. Store saga state in DB: which steps
completed, which compensations executed. Compensation
events: published to Kafka for choreography-based
sagas (OrderCancelled, PaymentRefunded, etc.).

**Level 4 - Why it matters (senior engineer):**
Compensating transactions reveal the REAL business
rules. When you design compensations: you discover
business rules that weren't explicit. "What happens
if payment succeeds but shipping address is invalid?"
-> You need a RefundPayment compensation. This
question often reveals missing business logic.
The process of designing compensations for all
saga steps is a powerful domain modeling exercise
that catches edge cases during design, not during
production incidents.

**Level 5 - Mastery (principal engineer):**
Compensation semantics: some compensations are
"countermanding" (fully reverse effect), some are
"counterbalancing" (add an offsetting entry), some
are "void" (notify that the prior action is void
but effect already occurred). Financial systems:
use countermanding for ledger entries (credits
for debits). Reservation systems: countermanding
(release reservation). Email systems: void (send
cancellation email, acknowledge original was sent).
For regulatory compliance: compensations must be
audit-logged exactly as the original transactions.
The compensation trail IS the evidence of corrective
action in regulated industries.

---

### ⚙️ How It Works (Mechanism)

```java
// SAGA ORCHESTRATOR with compensation logic
@Service
public class OrderSagaOrchestrator {

    @Transactional
    public void orchestrate(OrderSaga saga) {
        try {
            // Forward transactions
            paymentService.processPayment(
                saga.getOrderId(),
                saga.getAmount());
            saga.markStepCompleted("PAYMENT");

            inventoryService.reserveStock(
                saga.getOrderId(),
                saga.getProductId(), 1);
            saga.markStepCompleted("INVENTORY");

            shippingService.createShipment(
                saga.getOrderId());
            saga.markStepCompleted("SHIPPING");

            orderService.confirmOrder(saga.getOrderId());
            saga.markCompleted();

        } catch (SagaStepFailedException e) {
            log.error("Saga step failed: {}", e.getStep());
            compensate(saga);  // Run compensations
        }
    }

    private void compensate(OrderSaga saga) {
        // Execute compensations in REVERSE order
        // Only for steps that COMPLETED
        List<String> completed = saga.getCompletedSteps();

        if (completed.contains("SHIPPING")) {
            executeWithRetry(() ->
                shippingService.cancelShipment(
                    saga.getOrderId()));
        }

        if (completed.contains("INVENTORY")) {
            executeWithRetry(() ->
                inventoryService.releaseStock(
                    saga.getOrderId(),  // Idempotency key
                    saga.getProductId(), 1));
        }

        if (completed.contains("PAYMENT")) {
            executeWithRetry(() ->
                paymentService.refundPayment(
                    saga.getOrderId(),  // Idempotency key
                    saga.getAmount()));
        }

        orderService.cancelOrder(saga.getOrderId());
        saga.markFailed();
    }

    private void executeWithRetry(
            Supplier<Void> compensation) {
        // Retry until success: compensation MUST execute
        RetryTemplate retry = RetryTemplate.builder()
            .exponentialBackoff(1000, 2, 30000)
            .retryOn(Exception.class)
            .build();
        retry.execute(ctx -> {
            compensation.get();
            return null;
        });
    }
}

// COMPENSATING OPERATION: idempotent refund
@Service
public class PaymentService {

    // Idempotency key: orderId ensures no double refund
    @Transactional
    public void refundPayment(OrderId orderId,
                              Money amount) {
        // Check if already refunded
        if (refundRepo.existsByOrderId(orderId)) {
            log.info("Refund already processed for {}",
                orderId);
            return;  // Idempotent: skip duplicate
        }
        // Process refund
        paymentGateway.refund(orderId, amount);
        refundRepo.save(new Refund(orderId, amount));
        // Event: PaymentRefunded
        eventPublisher.publish(new PaymentRefundedEvent(
            orderId, amount));
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
COMPENSATING TRANSACTION FLOW:

FORWARD:
  T=0: ProcessPayment     -> SUCCESS ($99.99 debited)
  T=1: ReserveInventory   -> SUCCESS (1 unit locked)
  T=2: CreateShipment     -> FAILED (courier unavailable)
  
  Saga: detected failure at T=2
  Compensation: execute C1, C0 (reverse order)
  
COMPENSATION:
  T=3: CancelShipment     -> (T=2 failed; nothing to cancel)
  T=4: ReleaseInventory   -> SUCCESS (1 unit unlocked)
       Idempotency check: not yet released; proceed
  T=5: RefundPayment      -> SUCCESS ($99.99 credited)
       Idempotency check: not yet refunded; proceed
  T=6: CancelOrder        -> SUCCESS (order CANCELLED)
  
AUDIT TRAIL:
  T=0: PaymentProcessed    (+$99.99)
  T=1: InventoryReserved   (SKU-123, qty=1)
  T=2: ShipmentFailed      (no couriers)
  T=4: InventoryReleased   (SKU-123, qty=1) [compensation]
  T=5: PaymentRefunded     (-$99.99)         [compensation]
  T=6: OrderCancelled                         [compensation]
  
NET EFFECT: customer's money returned; order cancelled
AUDIT: complete record of what happened and why
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: non-idempotent compensation**

```java
// BAD: non-idempotent refund - double refund on retry
@Service
public class PaymentService {
    public void refundPayment(OrderId orderId,
                              Money amount) {
        // No idempotency check!
        paymentGateway.refund(orderId, amount);
        // If called twice: customer gets 2 refunds
        // Saga retries compensation on failure:
        // could call this N times = N refunds
    }
}
```

```java
// GOOD: idempotent refund
@Service
public class PaymentService {
    @Transactional
    public void refundPayment(OrderId orderId,
                              Money amount) {
        // Idempotency: check for existing refund
        if (refundRepo.existsByOrderId(orderId)) {
            return;  // Already refunded; safe to skip
        }
        paymentGateway.refund(orderId, amount);
        refundRepo.save(new Refund(orderId, amount,
            Instant.now()));
        // Called N times: exactly 1 refund issued
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | DB ROLLBACK | Compensating Transaction |
|---|---|---|
| **When executed** | Before commit (undo uncommitted) | After commit (reverse committed) |
| **Mechanism** | Transaction log undo | New business transaction |
| **History** | Original transaction erased | Both original + compensation recorded |
| **Partial effects** | Fully reversed (DB only) | May not fully reverse (email sent) |
| **Cross-service** | Impossible (different DBs) | Works (each service applies its own) |
| **Audit trail** | None (rolled back data gone) | Complete (full history) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Compensating transactions guarantee exactly the same state as before | They guarantee the BUSINESS EFFECT is reversed, not byte-for-byte identical state. The original transaction and compensation are in the audit log. Other side effects (emails, external notifications, reporting entries) may not be fully reversible. Design compensations to address the BUSINESS reversal, accept that some effects are irreversible and handle them explicitly. |
| Compensation is optional ("nice to have") | Compensation is MANDATORY in Saga design. If a saga step fails: uncorrected forward transactions leave the system in an inconsistent state (customer charged but order cancelled without refund). Every saga step that modifies state MUST have a corresponding compensation transaction. No exceptions. |
| Compensations are called in forward order | Compensations execute in REVERSE order. If T1 -> T2 -> T3 -> T4 fails: compensate C3 -> C2 -> C1 (not C1 -> C2 -> C3). Reverse order is required because later steps may depend on earlier steps' state. Releasing inventory (C3 for T3) before refunding (C2 for T2) ensures inventory is correct before payment reversal. |

---

### 🚨 Failure Modes & Diagnosis

**Compensation fails repeatedly; customer overcharged**

**Symptom:**
Customer reports: order was cancelled, but bank
statement shows charge was not refunded after 5
days. Saga logs show: compensation C2 (RefundPayment)
has been attempted 47 times; all failing with
`PaymentGatewayTimeoutException`. Saga stuck in
compensation loop.

**Root Cause:**
Payment gateway had a 5-day outage (fraud detection
suspended all refunds). Saga compensation retried
with exponential backoff but eventually hit max
retry interval (30 minutes). Still retrying. But
operations team not notified.

**Fix:**
1. Alert on compensation retry count > 10:
   `SagaCompensationRetryCountAlert > 10`.
2. After N retries: move to a "compensation DLQ"
   (compensation dead letter queue) for manual
   processing.
3. Operations team: processes DLQ manually or via
   manual refund when gateway recovers.
4. Design: compensations MUST eventually succeed;
   add human-in-the-loop fallback for external
   service failures beyond system control.

---

### 🔗 Related Keywords

**Where compensating transactions are used:**
- `Saga Pattern` - compensating transactions are
  the undo mechanism in Sagas

**Context:**
- `Two-Phase Commit` - 2PC uses DB ROLLBACK;
  compensating transactions are the alternative
  for committed distributed transactions
- `Eventual Consistency in Microservices` -
  compensation takes time (eventual, not immediate)

**Required properties:**
- `Idempotency in Microservices` - compensations
  must be idempotent (retried until successful)
- `Outbox Pattern` - compensation events published
  reliably via outbox

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ New transaction that reverses business    │
│              │ effect of a committed transaction         │
├──────────────┼───────────────────────────────────────────┤
│ RULES        │ Idempotent, executed in reverse order     │
│              │ Mandatory for every saga step             │
├──────────────┼───────────────────────────────────────────┤
│ LIMITATIONS  │ Cannot unsend emails, unreversible effects │
│              │ Use "best effort" compensations for these │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Business undo for committed transactions; │
│              │  Saga's rollback; idempotent; reverse order"│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Compensating transaction = business undo for
   a committed transaction. Not a DB ROLLBACK.
   Both original and compensation remain in history.
2. Must be idempotent: compensation infrastructure
   retries on failure; must not double-compensate.
3. Execute in REVERSE order of forward transactions.
   Mandatory for every saga step that mutates state.

**Interview one-liner:**
"Compensating Transaction: a NEW committed business
transaction that reverses the effects of a previously
committed transaction. Unlike DB ROLLBACK (which
undoes uncommitted data): compensation applies after
commit and creates an audit trail. Used in Saga
Pattern: if step N fails, compensate N-1, N-2...
in reverse order. Design rules: idempotent (safe
to re-execute), eventually executes (retry until
success), may not fully reverse all effects (emails
cannot be unsent - send cancellation email instead)."

---

### 💡 The Surprising Truth

The most counterintuitive aspect of compensating
transactions: they increase the total number of
transactions. A saga with 4 steps that fails at
step 3 results in: 3 forward transactions + 2
compensations = 5 total transactions. The system
was more "busy" for the failing case than the
success case. At high failure rates (e.g., 20%
failure rate during peak load): compensation
transactions add significant write load. Design:
minimize saga steps; validate pre-conditions before
starting forward transactions (fail fast before
expensive steps); monitor compensation rates as
a leading indicator of system health (rising
compensation rate = rising failure rate).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** For a 5-step saga (create order,
   charge payment, reserve inventory, create
   shipment, confirm order): specify the compensating
   transaction for each step. Which steps have
   "best effort" compensations (irreversible effects)?
2. **IDEMPOTENCY** Implement an idempotent
   refundPayment compensation. What is the
   idempotency key? How is "already refunded"
   detected? What if the idempotency check and
   payment gateway call are not atomic?
3. **FAILURE** Compensation itself fails 10 times
   in a row (external payment gateway down). What
   is your strategy? Dead letter queue, alert,
   manual intervention process?
4. **AUDIT** Design the audit log schema for a
   saga with compensations. What fields are required
   for a compliance audit? How do you query:
   "show all orders where compensation was executed"?
5. **PIVOT** In a travel booking saga (flight +
   hotel + car): identify the pivot transaction.
   What happens if the user cancels BEFORE the
   pivot vs AFTER? How does the compensation
   strategy differ?

---

### 🧠 Think About This Before We Continue

**Q1.** A payment refund (compensating transaction)
takes 3-5 business days to appear in the customer's
account. The customer calls support after 1 day:
"I cancelled my order but I'm still charged."
How does your system communicate the compensation
status to the customer? What state does the saga
have during these 5 days? Design the customer
facing status (order status, payment status) to
accurately reflect this "compensation in progress" state.

**Q2.** You are building a healthcare appointment
booking system. A saga books: (1) doctor appointment,
(2) lab test slot, (3) sends confirmation email,
(4) adds to patient's health record. Steps 3 and
4 succeed, then the payment fails. Design the
compensating transactions for each step. Which
are fully reversible? Which require human notification
(the "email sent" problem)?

**Q3.** At what compensation RATE does a microservices
system have a "compensation problem"? If 5% of
sagas require compensation: normal (some orders
legitimately fail). If 30% require compensation:
something is wrong (systemic issue). Design the
monitoring and alerting strategy for compensation
rate. What Prometheus metrics would you create?
What thresholds would trigger investigation?