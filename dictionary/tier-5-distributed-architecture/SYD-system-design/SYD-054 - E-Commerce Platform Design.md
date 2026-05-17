---
id: SYD-054
title: E-Commerce Platform Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-031
used_by: ""
related: SYD-008, SYD-031, SYD-039, SYD-028
tags:
  - architecture
  - ecommerce
  - inventory
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /syd/ecommerce-platform-design/
---

# SYD-054 - E-Commerce Platform Design

⚡ TL;DR - An e-commerce platform handles product
catalog browsing, cart management, inventory reservation,
order processing, and payment. The hardest problems are:
overselling prevention (inventory must be atomically
reserved before payment), flash sale traffic spikes
(10,000x normal traffic in seconds), and consistency
under high load (two users cannot buy the last item in
stock simultaneously). Solutions: Redis for inventory
counters (atomic DECR), database locks or optimistic
concurrency for order placement, and event-driven
architecture for post-payment processing.

| #054 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, Sharding | |
| **Related:** | Caching, Sharding, Distributed Locks, Rate Limiting | |

---

### 🔥 The Problem This Solves

Amazon Prime Day 2022 saw 300,000 items sold per minute.
During a flash sale (limited-quantity item at deep
discount), 50,000 users try to buy a product with only
100 units in stock - all within 30 seconds. Without
careful design:
- Overselling: 500 users successfully "buy" the same 100 items
- Race condition: two purchases simultaneously read "stock=1"
  and both decrement to 0 (but only 1 unit exists)
- Inventory inconsistency: database and display show different counts

---

### 📘 Textbook Definition

**E-commerce platform:** A system that enables consumers
to browse products, add to cart, and complete purchases
with inventory reservation and payment. Core domains:
product catalog, inventory management, cart service,
order service, and payment service.

**Inventory reservation:** Temporarily holding units
for a user who has begun checkout, preventing other
buyers from purchasing those units while payment
is being processed. Released if the checkout is
abandoned (timeout) or the payment fails.

**Overselling:** A critical failure mode where more
units are sold than exist in inventory. Caused by race
conditions in inventory decrement operations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Browse catalog → add to cart → reserve inventory →
pay → confirm order → fulfill. Inventory reservation
must be atomic and consistent.

**One analogy:**
> Booking concert tickets:
> When you click "checkout" on 2 tickets, the system
> holds those 2 tickets for you for 10 minutes (reservation).
> Nobody else can buy them while you complete payment.
> If you abandon checkout: tickets are released after 10 minutes.
> If you complete payment: tickets are permanently yours.
>
> Without the hold, two people could both proceed to
> payment for the last 2 tickets and both succeed -
> overselling 4 tickets from a 2-ticket availability.

**One insight:**
Inventory reservation is the hardest technical problem
in e-commerce. It requires atomic, consistent state
management: reading stock, checking availability, and
decrementing the count must happen as one indivisible
operation. Otherwise, concurrent checkouts race and
oversell. Redis DECR (atomic) or database optimistic
locking are the two main solutions.

---

### 🔩 First Principles Explanation

**INVENTORY MANAGEMENT - THREE APPROACHES:**
```
Approach 1: Database row locking (pessimistic)
  BEGIN TRANSACTION;
  SELECT stock FROM inventory
    WHERE product_id = X FOR UPDATE;
  -- Locks the row exclusively
  IF stock >= quantity:
    UPDATE inventory SET stock = stock - quantity
      WHERE product_id = X;
    INSERT INTO reservations (...);
  COMMIT;
  
  Pro: strictly consistent; no overselling
  Con: heavy locking; low throughput under contention
    50K concurrent checkouts → 50K locks queue up
    Most requests wait → system appears unresponsive

Approach 2: Optimistic concurrency (version-based)
  SELECT stock, version FROM inventory WHERE product_id = X;
  -- No lock taken
  IF stock >= quantity:
    UPDATE inventory SET stock = stock - quantity,
      version = version + 1
    WHERE product_id = X AND version = {read_version};
    -- IF 0 rows updated: another transaction changed it
    -- Retry the read + check + update
  
  Pro: no locks; high concurrency; only conflicts retried
  Con: high retry rate under extreme contention (flash sale)
    50K concurrent updates → most updates fail, retry loops

Approach 3: Redis atomic decrement (most scalable)
  DECR inventory:{product_id}
  -- Returns new value atomically
  IF new_value >= 0: reservation succeeded
  IF new_value < 0:
    INCR inventory:{product_id}  -- roll back
    return "out of stock"
  
  Pro: sub-millisecond; handles 100K+ ops/sec
  Con: Redis is not the source of truth; must sync to DB
    On Redis failure: fallback to DB approach
  
  Best for: flash sales, high-throughput inventory checks
```

**CART SERVICE:**
```
Cart is user-session data - not business-critical.
Storage: Redis (hash per cart)
  cart:{user_id} → HSET {product_id: quantity, ...}
  TTL: 30 days (abandoned cart cleanup)

Operations:
  Add to cart: HSET cart:{uid} {product_id} {qty}
  Remove: HDEL cart:{uid} {product_id}
  Clear: DEL cart:{uid}
  View: HGETALL cart:{uid}

Cart does NOT reserve inventory.
Inventory reservation happens at checkout, not at
"add to cart" - too many carts are never purchased.
```

**ORDER LIFECYCLE:**
```
CART → CHECKOUT_INITIATED → RESERVED → PAYMENT_PENDING
  → CONFIRMED → PAYMENT_CAPTURED → FULFILLMENT
  → SHIPPED → DELIVERED

Key events:
  CHECKOUT_INITIATED: user clicks "proceed to checkout"
  RESERVED: inventory locked for 10 minutes
  PAYMENT_PENDING: redirect to payment provider
  CONFIRMED: payment authorized; order locked in
  PAYMENT_CAPTURED: money collected
  FULFILLMENT: warehouse picks and packs

Post-CONFIRMED workflow (event-driven):
  ORDER_CONFIRMED event → Kafka
    → Fulfillment service (warehouse pick)
    → Email service (confirmation email)
    → Analytics service (revenue tracking)
    → Loyalty service (points awarded)
  Decoupled: payment service does not wait for all
  of these to complete before returning to the user
```

---

### 🧪 Thought Experiment

**SIZING: Flash sale - 100 units, 50K concurrent buyers**

Flash sale: 100 units, 50K users hit "buy" simultaneously.
Each buy attempt must atomically check and decrement inventory.

**Without Redis (DB optimistic lock):**
50K concurrent transactions all read stock=100.
50K UPDATE statements with version check.
Only 100 succeed (those that happen to commit first).
49,900 fail with "version conflict" → retry.
Retry storm: 49,900 retries, many fail again.
Database under extreme write contention. CPU spikes.
Result: system degrades for all users on the platform.

**With Redis DECR:**
50K DECR operations on inventory:{product_id}.
Redis processes them serially (single-threaded command
execution). First 100 DECR: result >= 0 → success.
Remaining 49,900: result < 0 → roll back INCR → "out of stock".
All 50K operations complete in < 100ms total.
No DB contention. Rest of the platform unaffected.

**Flash sale traffic spike:**
Normal: 1,000 product page views/sec.
Flash sale: 50,000/sec at 0 seconds, drops as inventory sells.
Need: rate limiter on flash sale checkout endpoint
(SYD-028). Limit: 5,000 checkout attempts/sec.
Queue the rest with a "queue" page (wait in line).
This protects the inventory service from being
overwhelmed beyond its throughput capacity.

---

### 🧠 Mental Model / Analogy

> E-commerce inventory management is like a ticket booth
> at a popular concert:
>
> - The ticket counter (inventory service) has exactly
>   100 tickets.
> - 50,000 people rush the counter simultaneously.
> - The booth has one window (Redis, single-threaded):
>   only one transaction happens at a time. First 100
>   people get tickets; everyone else is told "sold out"
>   without the booth collapsing.
> - A paper form + duplicate submissions (DB row lock):
>   the booth tries to handle all 50,000 people at once,
>   most of whom are filling out the same form - chaos.
>
> Redis is not about being smarter; it is about being
> architecturally simpler under contention.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An online store lets you browse products, add them to
your cart, and buy them. The hard part is making sure
the system does not sell the same item twice, especially
when thousands of people are trying to buy at the same time.

**Level 2 - How to use it (junior developer):**
Product catalog stored in a database. Cart stored in
Redis (hash, TTL). At checkout: read inventory, decrement
if available, create order, redirect to payment. After
payment confirms: finalize order and trigger fulfillment.

**Level 3 - How it works (mid-level engineer):**
Redis DECR for atomic inventory checks (handles flash
sales without DB contention). Order service creates an
order record (PENDING), reserves inventory, processes
payment, updates order to CONFIRMED. Post-CONFIRMED:
Kafka events trigger fulfillment, email, analytics.
Idempotency key on payment (prevent double charge on
network retry). TTL on reservations (release held
inventory on checkout timeout).

**Level 4 - Why it was designed this way (senior/staff):**
Redis DECR for inventory is the right tool because of
its single-threaded command execution: all DECR commands
are processed sequentially by Redis, eliminating the
need for locks or transactions. This gives much higher
throughput under contention than database locking or
optimistic concurrency. The trade-off: Redis is not
durable by default (AOF/RDB persistence mitigates this).
On Redis failure, fall back to DB optimistic locking.
The event-driven post-order processing (Kafka) decouples
the time-critical path (payment confirmation) from
non-critical work (analytics, email, loyalty points).
The user gets a confirmation response in < 500ms; the
downstream processing happens over the next few seconds.

**Level 5 - Mastery (distinguished engineer):**
Amazon's architecture separates inventory management into:
(1) available-to-promise (ATP) service - how much can be
sold today accounting for existing commitments, inbound
shipments, and fulfillment center capacity; (2) warehouse
management system (WMS) - physical location of items
in fulfillment centers; (3) order routing - which
fulfillment center should ship to minimize delivery time
and cost. At Amazon's scale, a product may have inventory
in 200+ fulfillment centers globally. The ATP calculation
aggregates across all of them. A single "add to cart"
reserves from the optimal fulfillment center based on
the customer's location. This is a multi-constraint
optimization problem (minimize delivery time, shipping
cost, risk of stockout) solved in < 100ms per add-to-cart.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ E-COMMERCE ORDER FLOW                               │
│                                                      │
│ BROWSE:                                             │
│  GET /products → CDN (cached product catalog)      │
│  Inventory count: read from cache (eventual)        │
│                                                      │
│ ADD TO CART:                                        │
│  HSET cart:{user_id} {product_id} {qty}            │
│  No inventory reservation yet                      │
│                                                      │
│ CHECKOUT:                                           │
│  1. DECR inventory:{product_id}                    │
│     >= 0: proceed. < 0: INCR (rollback), 409       │
│  2. Create order: PENDING in Orders DB             │
│  3. SET reservation:{product_id} TTL=600           │
│  4. Redirect to payment provider                   │
│                                                      │
│ PAYMENT CALLBACK:                                   │
│  Payment provider → POST /webhook → Order Service  │
│  Verify signature (prevent forgery)                │
│  Update order: CONFIRMED                           │
│  Publish to Kafka: ORDER_CONFIRMED                 │
│                                                      │
│ POST-ORDER (async, via Kafka):                      │
│  ──► Fulfillment: pick + pack + ship               │
│  ──► Email: confirmation                           │
│  ──► Analytics: revenue tracking                  │
│  ──► Loyalty: award points                        │
│                                                      │
│ TIMEOUT (reservation expired, payment not received):│
│  INCR inventory:{product_id}  (release reservation) │
│  Update order: CANCELLED                           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Atomic inventory reservation with Redis**
```python
import redis
import uuid
from fastapi import FastAPI, HTTPException

app = FastAPI()
r = redis.Redis()

RESERVATION_TTL = 600  # 10 minutes

def reserve_inventory(product_id: int,
                       quantity: int = 1) -> bool:
    """
    Atomically reserve inventory.
    Returns True if reserved, False if out of stock.
    """
    # Lua script: atomic check + decrement
    # Prevents race condition between check and decrement
    lua_script = """
    local stock = tonumber(redis.call(
        'GET', KEYS[1]) or 0)
    local qty = tonumber(ARGV[1])
    if stock >= qty then
        return redis.call('DECRBY', KEYS[1], qty)
    else
        return -1
    end
    """
    result = r.eval(
        lua_script, 1,
        f"inventory:{product_id}",
        quantity
    )
    return result >= 0

def release_inventory(product_id: int,
                       quantity: int = 1):
    """Release reserved inventory (on timeout/cancel)."""
    r.incrby(f"inventory:{product_id}", quantity)

def checkout(user_id: int, product_id: int,
              quantity: int) -> dict:
    """
    Checkout flow: reserve inventory, create order.
    Returns order_id or raises HTTPException.
    """
    # Step 1: Reserve inventory
    if not reserve_inventory(product_id, quantity):
        raise HTTPException(
            status_code=409,
            detail="Insufficient inventory"
        )

    # Step 2: Create order in PENDING state
    order_id = str(uuid.uuid4())
    try:
        db_create_order(order_id, user_id,
                         product_id, quantity,
                         status="PENDING")
        # Step 3: Set reservation TTL
        r.setex(
            f"reservation:{order_id}", RESERVATION_TTL,
            f"{product_id}:{quantity}"
        )
        return {
            "order_id": order_id,
            "payment_url": f"/pay/{order_id}"
        }
    except Exception as e:
        # Rollback inventory on DB failure
        release_inventory(product_id, quantity)
        raise HTTPException(status_code=500, detail=str(e))

def on_payment_confirmed(order_id: str):
    """Handle payment confirmation webhook."""
    # Idempotency: check if already processed
    if r.get(f"order:processed:{order_id}"):
        return  # Duplicate webhook, already handled
    r.setex(f"order:processed:{order_id}",
             86400, "1")

    # Update order status
    db_update_order_status(order_id, "CONFIRMED")
    # Clear reservation TTL (no longer auto-releases)
    r.delete(f"reservation:{order_id}")
    # Publish event for async downstream processing
    kafka_publish("order.confirmed", {
        "order_id": order_id})
```

**Example 2 - Overselling race condition (BAD)**
```python
# BAD: Non-atomic check + decrement
def reserve_inventory_bad(product_id: int) -> bool:
    stock = r.get(f"inventory:{product_id}")
    stock = int(stock) if stock else 0
    
    # RACE: Two concurrent requests both read stock=1
    # Both pass this check. Both call DECR.
    # Final stock: -1. Oversold.
    if stock <= 0:
        return False
    
    r.decr(f"inventory:{product_id}")
    return True

# GOOD: Use Lua script (shown above) for atomic
# check + decrement. The entire operation is
# indivisible - no other command can run between
# the check and the decrement.
```

---

### ⚖️ Comparison Table

| Approach | Consistency | Throughput | Complexity | Best For |
|---|---|---|---|---|
| **DB SELECT FOR UPDATE** | Strong | Low (locks) | Simple | Low traffic inventory |
| **Optimistic concurrency** | Strong | Medium (retries) | Medium | Moderate traffic |
| **Redis Lua DECR** | Strong (Redis) | High (100K+/sec) | Medium | Flash sales, high volume |
| **Queue-based (serialize)** | Strong | Medium (queue) | High | Extreme flash sales |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Add-to-cart should reserve inventory | If inventory is reserved at add-to-cart, it is held while the user browses other products, compares prices, or forgets about it. This blocks legitimate buyers. Reserve inventory only at checkout (when the user actively commits). Show "X left" warnings on the product page from a non-reserved count. |
| Payment should be processed synchronously before confirming the order | Payment providers typically take 200-500ms for authorization. The order can be created in PENDING state and updated to CONFIRMED upon payment webhook. This pattern is more resilient: the user gets an immediate response; payment confirmation is asynchronous via webhook. Always verify webhook signatures (shared secret or public key) to prevent fraudulent confirmation. |
| Inventory is a single number | At Amazon/Walmart scale, inventory is split across hundreds of fulfillment centers. The "available" count shown to customers is a near-real-time estimate across all locations, with reservation happening at the fulfillment center level. The number shown online may differ by a few units from the actual reservable quantity due to propagation lag. |

---

### 🚨 Failure Modes & Diagnosis

**Payment Webhook Not Received - Stuck Orders**

**Symptom:**
Orders are stuck in PENDING state indefinitely.
Users paid but never received confirmation.
Customer support is flooded with "where is my order?"
tickets. Payment provider says payments are successful.

**Root Cause:**
Payment webhook delivery failed (network issue,
server 500, incorrect endpoint configuration).
Payment provider retried but all retries failed.
No timeout mechanism on PENDING orders.

**Fix - Webhook retry + polling reconciliation:**
```python
# Fix 1: Accept webhooks idempotently (already done)
# Fix 2: Reconciliation job for stuck PENDING orders

def reconcile_pending_orders():
    """
    Check PENDING orders older than 15 minutes.
    Query payment provider API to confirm status.
    """
    # Find PENDING orders older than 15 minutes
    stale_orders = db_query("""
        SELECT order_id, payment_intent_id
        FROM orders
        WHERE status = 'PENDING'
          AND created_at < NOW() - INTERVAL '15 minutes'
    """)

    for order in stale_orders:
        # Poll payment provider for latest status
        payment_status = payment_provider_api.check(
            order["payment_intent_id"])

        if payment_status == "succeeded":
            db_update_order_status(
                order["order_id"], "CONFIRMED")
            kafka_publish("order.confirmed",
                           {"order_id": order["order_id"]})
        elif payment_status in ("failed", "cancelled"):
            db_update_order_status(
                order["order_id"], "CANCELLED")
            # Release inventory
            release_inventory_for_order(
                order["order_id"])
        # else: still pending (payment processing) - skip

# Run this job every 5 minutes as a safety net.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - product catalog and pricing cached at CDN
  and Redis for read performance
- `Sharding` - orders and products sharded by user_id
  or product_id for horizontal scale

**Builds On This (learn these next):**
- `Distributed Locks` - inventory reservation uses
  the same pattern as distributed locking
- `Rate Limiting (System)` - flash sale checkout
  endpoints need rate limiting to prevent overload

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INVENTORY   │ Redis Lua atomic DECR at checkout.        │
│             │ Release with INCR on timeout or cancel.  │
├─────────────┼──────────────────────────────────────────  │
│ CART        │ Redis hash: cart:{uid}. TTL 30 days.     │
│             │ No inventory reservation at add-to-cart. │
├─────────────┼──────────────────────────────────────────  │
│ ORDER FLOW  │ PENDING → CONFIRMED → FULFILLMENT.        │
│             │ Payment via webhook (async). Idempotent.  │
├─────────────┼──────────────────────────────────────────  │
│ POST-ORDER  │ Kafka: ORDER_CONFIRMED → fulfillment,    │
│             │ email, analytics (decoupled).            │
├─────────────┼──────────────────────────────────────────  │
│ FLASH SALE  │ Rate limit checkout endpoint.            │
│             │ Queue overflow with "wait in line" page. │
├─────────────┼──────────────────────────────────────────  │
│ FAILURE     │ Stuck PENDING: reconciliation job polls  │
│             │ payment provider every 5 min.            │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Redis Lua DECR = atomic inventory;     │
│             │  webhook + reconciliation = payment"    │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Web Crawler Design → API Gateway Design  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Inventory reservation must be atomic. Use Redis Lua
   scripting (check + DECRBY in one indivisible operation)
   to prevent overselling. Never read-then-decrement with
   two separate commands - that is a race condition.
2. Reserve inventory at checkout, not at add-to-cart.
   Release reservations with a TTL (10 minutes) if the
   user abandons checkout. Release on payment failure.
3. Payment confirmation via webhook is asynchronous.
   Process webhooks idempotently (check if order already
   confirmed). Run a reconciliation job every 5 minutes
   to poll the payment provider for PENDING orders older
   than 15 minutes - this catches missed webhooks.

**Interview one-liner:**
"E-commerce: product catalog in DB, cached at CDN. Cart in Redis hash (TTL 30 days,
no inventory reservation). Checkout: Lua script atomically checks + decrements
inventory:{product_id} in Redis. On success: create order (PENDING), set 10-min
TTL reservation. Redirect to payment provider. Payment callback: verify webhook
signature, update order to CONFIRMED, publish ORDER_CONFIRMED to Kafka (triggers
fulfillment, email, loyalty - decoupled). Missed webhook safety net: reconciliation
job every 5 min polls payment provider for PENDING orders > 15 min old."
