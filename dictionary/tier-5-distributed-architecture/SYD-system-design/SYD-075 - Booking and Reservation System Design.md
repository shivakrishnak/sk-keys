---
id: SYD-075
title: Booking and Reservation System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-016, SYD-059
used_by: ""
related: SYD-016, SYD-059, SYD-058, SYD-071, SYD-033
tags:
  - architecture
  - booking
  - reservations
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 75
permalink: /syd/booking-reservation-system-design/
---

# SYD-075 - Booking and Reservation System Design

⚡ TL;DR - Booking systems (hotels, flights, concerts)
must prevent double-booking: two users cannot both
receive the last available seat/room. The core problem
is concurrent reservation of a finite resource. Four
approaches: (1) Pessimistic locking - SELECT FOR UPDATE
holds a DB lock, blocks concurrent reservations (simple,
correct, low throughput); (2) Optimistic locking -
version field, fail-fast on conflict (high throughput,
requires retry logic); (3) Queue-based serialization -
all reservations for one resource go through one queue
(ordered, no conflicts, higher latency); (4) Seat lease
- reserve a seat for N minutes (like an e-commerce cart
hold), then confirm or release. Each approach trades
consistency, throughput, and complexity.

| #075 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Distributed Transactions, Event Sourcing | |
| **Related:** | Distributed Transactions, Event Sourcing, CQRS, Payment System Design, Database Internals | |

---

### 🔥 The Problem This Solves

Beyoncé concert: 50,000 seats. 1 million fans hit
"Book Ticket" simultaneously at 10:00 AM. The booking
system must ensure: (1) exactly 50,000 tickets sold,
not 50,001 due to a race condition; (2) the last ticket
goes to exactly one buyer, not two buyers simultaneously;
(3) users who don't complete payment within 10 minutes
have their held seats released back to inventory.
Without proper concurrency control: two users book
seat 15A, both receive confirmation, both show up at
the venue. Crisis.

---

### 📘 Textbook Definition

**Reservation system:** A system that assigns exclusive
access to a finite resource (seat, room, appointment
slot) to one requester, preventing concurrent double-
booking.

**Inventory:** The set of available bookable units
(seats, rooms, time slots). May be limited (50,000
concert tickets) or large (millions of hotel rooms).

**Seat hold / lease:** A temporary exclusive reservation
of a resource for a limited time (e.g., 10 minutes)
while the user completes payment. If payment is not
completed within the time limit, the seat is released.

**Pessimistic locking:** Lock the row being reserved
(SELECT FOR UPDATE) before checking availability.
Concurrent transactions wait. Prevents double-booking
with no retry logic needed. Trade-off: low throughput
under high contention.

**Optimistic locking:** Read the row without locking.
On update, check that version field is unchanged.
If changed (someone else updated): fail, retry.
Higher throughput; requires retry on conflict.

**Overbooking:** Intentionally selling more reservations
than available units, anticipating cancellations.
Common in airlines. Out of scope for this entry
(described as a business policy, not a technical bug).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Booking = atomically decrementing a counter while
preventing concurrent double-decrement.
Hold the seat briefly; confirm when payment completes.

**One analogy:**
> Concert ticket line:
>
> Without concurrency control:
> Two people reach the last ticket simultaneously.
> Ticket agent shows both: "Ticket available!"
> Both say yes. Both receive the ticket. One person
> arrives at the concert without a seat. Crisis.
>
> With seat hold:
> Ticket agent: "I'm holding this for you for
> 10 minutes. Complete payment."
> During hold: ticket is NOT shown as available to others.
> After 10 minutes: if payment incomplete, hold released.
> First person to pay: gets the ticket.
> Second person: "Sorry, sold out."

**One insight:**
The seat hold pattern is the right balance for user
experience and correctness. Pure pessimistic locking:
if 1 million users try to book simultaneously, 999,999
are blocked waiting for the one lock holder. Seat holds:
each user gets a hold quickly (no blocking), but only
for 10 minutes. Users complete checkout at their own
pace. The system handles expiry gracefully (release hold
if payment not completed). This matches real-world booking:
Ticketmaster, Airbnb, and OpenTable all use seat/hold
patterns.

---

### 🔩 First Principles Explanation

**CONCURRENCY CONTROL APPROACHES:**

**Approach 1: Pessimistic Locking**
```sql
BEGIN;

-- Lock the inventory row exclusively.
-- Other transactions block here until lock released.
SELECT available_count 
FROM inventory 
WHERE resource_id = 'concert-2024-01-15-seat-15A'
FOR UPDATE;

-- available_count = 1: proceed
-- available_count = 0: ROLLBACK (sold out)

-- Create reservation
INSERT INTO reservations 
(user_id, resource_id, status)
VALUES (123, 'concert-2024-01-15-seat-15A', 'CONFIRMED');

-- Decrement inventory
UPDATE inventory 
SET available_count = available_count - 1
WHERE resource_id = 'concert-2024-01-15-seat-15A';

COMMIT;

-- Lock released. Next waiting transaction proceeds.
-- They will see available_count = 0: sold out.

Pros: Simple. Correct. No retry logic needed.
Cons: Under high contention, all threads queue behind
      the one lock holder. Throughput: limited to
      (lock hold time) per sequential request.
      For 1M concurrent requests: 999,999 in the queue.
```

**Approach 2: Optimistic Locking**
```sql
-- Read current state (no lock)
SELECT available_count, version
FROM inventory
WHERE resource_id = 'concert-...'

-- Assume available_count = 5, version = 42

-- Attempt atomic update with version check
UPDATE inventory
SET available_count = available_count - 1,
    version = version + 1
WHERE resource_id = 'concert-...'
  AND version = 42          -- Conflict check
  AND available_count > 0;  -- Availability check

-- rows_affected = 1: success. Proceed with reservation.
-- rows_affected = 0: conflict (someone else updated).
--   Retry: re-read, re-check availability, re-try.

Pros: High throughput (no blocking).
      Multiple users attempt concurrently.
Cons: Under high contention, many retries.
      Risk of starvation (unlucky users retry many times).
      Retry logic required.

Best for: medium contention (multiple available units).
Worst for: "last ticket" scenario (extreme contention).
```

**Approach 3: Seat Hold Pattern**
```
State machine for a reservation:
  AVAILABLE
    ↓ (user initiates checkout)
  HELD (expires in 10 minutes)
    ↓ (payment completes)
  CONFIRMED
    ↓ (user cancels or hold expires)
  RELEASED → AVAILABLE

Implementation:

1. User initiates booking:
   SELECT a seat that is AVAILABLE.
   INSERT INTO seat_holds 
     (user_id, seat_id, expires_at)
   VALUES 
     (123, 'A15', NOW() + INTERVAL '10 minutes');
   UPDATE seats SET status = 'HELD'
   WHERE id = 'A15' AND status = 'AVAILABLE';
   
   -- If UPDATE affects 0 rows: seat was taken.
   -- ROLLBACK and try another seat.

2. User sees: "Seat A15 held for 9 minutes 47 seconds."

3. User completes payment:
   UPDATE seats SET status = 'CONFIRMED'
   WHERE id = 'A15';
   UPDATE seat_holds SET confirmed = true
   WHERE user_id = 123 AND seat_id = 'A15';

4. Expiry worker (cron/background):
   UPDATE seats SET status = 'AVAILABLE'
   WHERE id IN (
     SELECT seat_id FROM seat_holds
     WHERE confirmed = false
     AND expires_at < NOW()
   );
   DELETE FROM seat_holds
   WHERE expires_at < NOW() AND confirmed = false;
```

**HIGH-THROUGHPUT: REDIS FOR SEAT HOLDS**
```
Problem: high-traffic concert sale.
DB locks under 1M concurrent requests → queue buildup.
Redis atomic operations for seat holds:

Pre-populate available seats in Redis Set:
  SADD available:concert:2024-01-15 A1 A2 ... F50000

User requests a seat:
  # Atomically move a seat from available to held
  # Redis Lua script (atomic execution):
  
  script = """
  local seat = redis.call('SPOP', KEYS[1])
  if seat then
    redis.call('SETEX', KEYS[2] .. seat, 600, ARGV[1])
    return seat
  end
  return nil
  """
  seat = redis.eval(script, 
    keys=["available:concert:2024-01-15",
          "hold:concert:2024-01-15:"],
    args=[user_id])
  
  # seat = "A15": successfully held for user_id, 600s TTL
  # seat = None: sold out

User completes payment:
  # Atomically confirm: delete hold, add to confirmed set
  redis.multi_exec:
    redis.delete("hold:concert:2024-01-15:A15")
    redis.sadd("confirmed:concert:2024-01-15:A15", user_id)

Hold expiry: Redis TTL handles it automatically.
  After 600 seconds, SETEX key expires.
  Key expiry event: restore seat to available set.
  (Using Redis keyspace notifications)

Write to DB asynchronously (after Redis success):
  Kafka event: {seat: A15, user_id: 123, status: CONFIRMED}
  DB consumer: INSERT reservation, UPDATE seat status.
  Redis is primary for availability; DB is audit trail.
```

---

### 🧪 Thought Experiment

**Beyoncé Concert: 1M Concurrent Requests, 50K Seats**

Strategy: Redis atomic SPOP + SETEX (seat holds).

T=0: sale opens. 1M users click "Book Ticket."
T=0.001s: first 50,000 requests arrive at Redis.
  Redis SPOP: 50,000 atomic pops from available set.
  50,000 users: each gets a different seat.
  950,000 users: SPOP returns nil. "Sold Out."

T=0-T+600s: 50,000 users in checkout.
  Each has 10 minutes to complete payment.
  Some will abandon. Their holds expire.

T=120s: user #1,234 abandons. TTL on A15 expires.
  Keyspace notification: restore A15 to available set.
  Waitlist user gets A15 via SPOP.

At T=600s: any remaining uncompleted holds expire.
  All released seats re-offered to waitlist.

DB writes: Kafka consumers process confirmations.
  Not in the critical path of the booking flow.
  User gets confirmation email based on Redis state.
  DB reflects confirmed state within seconds.

---

### 🧠 Mental Model / Analogy

> Booking = a game of musical chairs with rules:
>
> Available chairs: 50,000 seats.
> Players: 1 million users clicking "Book."
>
> Redis SPOP: each user "picks up" a chair (atomic).
> Only 50,000 chairs exist: 50,000 users get one.
> 950,000: no chair. Game over for them.
>
> Seat hold: user holds their chair while they go
> buy popcorn (complete payment). They have 10 minutes.
> If they don't return: chair goes back to the pile.
>
> Pessimistic lock: one user holds ONE chair at a
> time while everyone else stands in line. Slow.
>
> Optimistic lock: everyone grabs the same chair
> simultaneously. Only one wins; others retry.
> Fast but chaotic with many retries.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A booking system lets people reserve a limited resource
(hotel room, concert seat, flight seat). The hard part:
making sure two people can't book the same thing at the
same time. The system must be "atomic" - either you get
the seat or you don't. No half-bookings.

**Level 2 - How to use it (junior developer):**
Use database transactions with SELECT FOR UPDATE to lock
a seat row during the reservation. Check availability
inside the transaction. Create the reservation. Release
the lock on commit/rollback. Implement a seat hold:
mark seats as "held" with an expiry time; a background
job releases expired holds.

**Level 3 - How it works (mid-level engineer):**
Seat hold state machine: AVAILABLE → HELD (TTL) →
CONFIRMED or RELEASED. Pessimistic locking: SELECT FOR
UPDATE prevents concurrent booking (correct, lower
throughput). Optimistic locking: version check on UPDATE,
retry on 0-rows-affected (higher throughput, retry
complexity). Redis for high-concurrency: SPOP from
available set (atomic), SETEX for hold TTL.
Write to DB for audit trail after Redis success.

**Level 4 - Why it was designed this way (senior/staff):**
The seat hold pattern is an application-level solution
to the problem that pure database locking cannot solve
under extreme concurrency: holding a lock for 10 minutes
while a user completes checkout would block thousands
of concurrent requests. The hold converts a long-running
user interaction into a short atomic reservation step,
then decouples the payment completion. The 10-minute TTL
balances user experience (enough time to complete payment)
with system efficiency (seats released quickly if users
abandon). Ticketmaster uses holds; Airbnb uses a soft
hold with a "confirm in 24 hours" policy. The exact TTL
is a business decision: too short = poor UX (payment
didn't go through, seat released); too long = seats
unavailable to others for long periods.

**Level 5 - Mastery (distinguished engineer):**
Roblox's virtual item marketplace uses a hybrid approach:
for common items (thousands available), optimistic locking
(high throughput, low contention). For limited-edition
items (5 available), pessimistic locking (correctness
paramount). For single-item auction (1 available), a
serialized queue per item. Distinguishing these cases
requires knowing the expected contention ratio (requests
per available unit). At contention_ratio < 2: optimistic
locking is efficient. At contention_ratio > 100 (concert
tickets): optimistic locking degrades (high retry rate);
use Redis SPOP or queue-based serialization. The
algorithmic insight: the system must know the expected
contention before choosing a locking strategy, or
adaptively switch strategies based on current load.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ SEAT HOLD FLOW (High-Throughput)                    │
│                                                      │
│ Pre-load: SADD available:event:123 A1 A2...A50000  │
│                                                      │
│ User books:                                         │
│   Redis Lua: SPOP available:event:123              │
│   → seat = "A15" (or nil if sold out)              │
│   SETEX hold:event:123:A15 600 "user:456"          │
│                                                      │
│ User completes payment (10 min window):             │
│   POST /api/book/confirm {seat: A15, payment: ...} │
│   Payment service → charge card                    │
│   Redis: DEL hold:event:123:A15                    │
│   Redis: SADD confirmed:event:123 A15:user:456    │
│   Kafka: publish BookingConfirmed event           │
│                                                      │
│ Hold expiry (Redis TTL):                            │
│   After 600s: SETEX key expires                   │
│   Keyspace notification → restore A15 to avail.  │
│   SADD available:event:123 A15                    │
│                                                      │
│ DB write (async):                                   │
│   Kafka consumer: INSERT reservation, UPDATE seat  │
│   Source of truth for reporting, audit, support   │
│   Not in booking critical path                    │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Seat hold with PostgreSQL (Python)**
```python
from datetime import datetime, timedelta
from contextlib import contextmanager

HOLD_DURATION_MINUTES = 10

def hold_seat(user_id: int, event_id: int,
              seat_id: str) -> dict:
    """
    Atomically reserve a seat in HELD state.
    Uses optimistic locking (version check on UPDATE).
    """
    with db.transaction():
        # Atomic: update only if seat is AVAILABLE
        rows = db.execute(
            "UPDATE seats "
            "SET status = 'HELD', "
            "held_by_user_id = %s, "
            "hold_expires_at = %s, "
            "version = version + 1 "
            "WHERE id = %s "
            "AND event_id = %s "
            "AND status = 'AVAILABLE' "
            "RETURNING id, hold_expires_at",
            [
                user_id,
                datetime.utcnow() + timedelta(
                    minutes=HOLD_DURATION_MINUTES),
                seat_id,
                event_id
            ]
        )
        
        if not rows:
            return {"success": False,
                    "error": "Seat not available"}
        
        # Record the hold for expiry tracking
        db.execute(
            "INSERT INTO seat_holds "
            "(user_id, event_id, seat_id, expires_at) "
            "VALUES (%s, %s, %s, %s)",
            [user_id, event_id, seat_id,
             rows[0]['hold_expires_at']]
        )
        
        return {
            "success": True,
            "seat_id": seat_id,
            "expires_at": rows[0]['hold_expires_at'],
            "expires_in_seconds": HOLD_DURATION_MINUTES * 60
        }

def confirm_reservation(user_id: int, event_id: int,
                         seat_id: str,
                         payment_id: str) -> dict:
    """
    Confirm a held seat after successful payment.
    Validates hold is still valid (not expired).
    """
    with db.transaction():
        rows = db.execute(
            "UPDATE seats "
            "SET status = 'CONFIRMED', "
            "confirmed_user_id = %s, "
            "payment_id = %s, "
            "confirmed_at = NOW() "
            "WHERE id = %s "
            "AND event_id = %s "
            "AND held_by_user_id = %s "
            "AND status = 'HELD' "
            "AND hold_expires_at > NOW() "
            "RETURNING id",
            [user_id, payment_id, seat_id,
             event_id, user_id]
        )
        
        if not rows:
            return {
                "success": False,
                "error": "Hold expired or invalid"
            }
        
        return {"success": True, "seat_id": seat_id}

def release_expired_holds():
    """
    Background job: release expired holds.
    Run every minute.
    """
    released = db.execute(
        "WITH expired AS ("
        "  UPDATE seats "
        "  SET status = 'AVAILABLE', "
        "  held_by_user_id = NULL, "
        "  hold_expires_at = NULL "
        "  WHERE status = 'HELD' "
        "  AND hold_expires_at < NOW() "
        "  RETURNING id, event_id"
        ") "
        "DELETE FROM seat_holds "
        "WHERE (seat_id, event_id) IN "
        "  (SELECT id, event_id FROM expired) "
        "RETURNING seat_id"
    )
    return len(released)
```

**Example 2 - High-throughput Redis seat pool**
```python
import redis
import json
import uuid
from datetime import datetime

r = redis.Redis(host='redis.internal',
                decode_responses=True)

HOLD_TTL_SECONDS = 600  # 10 minutes

def initialize_event_inventory(event_id: str,
                                seat_ids: list):
    """
    Pre-load all available seats into Redis set.
    Run once when event goes on sale.
    """
    # Pipeline for efficiency
    pipe = r.pipeline()
    avail_key = f"seats:available:{event_id}"
    pipe.delete(avail_key)
    for seat_id in seat_ids:
        pipe.sadd(avail_key, seat_id)
    pipe.execute()
    print(f"Loaded {len(seat_ids)} seats for {event_id}")

HOLD_LUA_SCRIPT = """
local seat = redis.call('SPOP', KEYS[1])
if not seat then
  return nil
end
redis.call('SETEX', KEYS[2] .. seat, ARGV[1], ARGV[2])
return seat
"""

hold_script = r.register_script(HOLD_LUA_SCRIPT)

def hold_seat_redis(event_id: str, user_id: int) -> dict:
    """
    Atomically pop a seat from available pool
    and create a hold with TTL.
    O(1) time. No lock contention.
    """
    avail_key = f"seats:available:{event_id}"
    hold_prefix = f"seats:hold:{event_id}:"
    
    seat = hold_script(
        keys=[avail_key, hold_prefix],
        args=[HOLD_TTL_SECONDS, user_id]
    )
    
    if not seat:
        return {"success": False, "error": "Sold out"}
    
    return {
        "success": True,
        "seat_id": seat,
        "hold_key": f"{hold_prefix}{seat}",
        "expires_in": HOLD_TTL_SECONDS
    }

def confirm_seat_redis(event_id: str, seat_id: str,
                        user_id: int,
                        payment_id: str) -> bool:
    """
    Confirm a held seat after payment.
    Validate hold belongs to this user.
    """
    hold_key = f"seats:hold:{event_id}:{seat_id}"
    hold_user = r.get(hold_key)
    
    if str(hold_user) != str(user_id):
        return False  # Hold expired or wrong user
    
    # Atomic: delete hold, add to confirmed set
    pipe = r.pipeline()
    pipe.delete(hold_key)
    pipe.sadd(f"seats:confirmed:{event_id}",
              f"{seat_id}:{user_id}:{payment_id}")
    pipe.execute()
    
    # Async: publish to Kafka for DB persistence
    # (write-behind: Redis is primary for booking state,
    #  DB is audit trail and fallback)
    publish_booking_confirmed(event_id, seat_id,
                               user_id, payment_id)
    return True
```

---

### ⚖️ Comparison Table

| Strategy | Throughput | Correctness | Complexity | Use Case |
|---|---|---|---|---|
| **SELECT FOR UPDATE** | Low (sequential) | Perfect | Low | < 1,000 concurrent requests |
| **Optimistic locking** | High | Correct (with retries) | Medium | Medium contention (many seats) |
| **Redis SPOP + hold** | Very high | Correct | Medium | High-concurrency flash sales |
| **Queue per resource** | Serialized | Perfect | High | Ultra-high contention (last seat) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Check availability then book is atomic | `SELECT available WHERE status='AVAILABLE'` followed by `UPDATE status='BOOKED'` is a read-then-write race condition. Between the SELECT and UPDATE, another transaction can change the status. The check and the book must be one atomic operation: `UPDATE seats SET status='BOOKED' WHERE id=X AND status='AVAILABLE'`. Check the rows_affected count. 0 rows updated = someone else got it. |
| Seat hold prevents overbooking | A seat hold only prevents double-booking if every booking attempt goes through the hold flow and expired holds are reliably released. If the expiry job fails (cron outage), seats stay held forever and the inventory appears sold out even with available seats. Monitor: alert if `hold_expires_at < NOW() AND status='HELD'` count > 0 for more than 5 minutes. |
| High-concurrency = need NoSQL | Booking systems require strong consistency guarantees that most NoSQL databases sacrifice for availability/scale. PostgreSQL with proper indexing on seat_id and status handles tens of thousands of concurrent bookings per second. The solution for extreme scale (concert tickets) is Redis atomic operations, not NoSQL document stores. The right tool depends on the consistency requirement, not just scale. |

---

### 🚨 Failure Modes & Diagnosis

**Hold Expiry Worker Fails: Inventory Locked**

**Symptom:**
Event shows "Sold Out" but no one has confirmed tickets.
Redis or DB shows many HELD seats past their expiry.
Users: "I got a seat hold but it expired and I can't
book it again, and the show says sold out."
Support: sold out event with 0 confirmed bookings.

**Root Cause:**
Hold expiry background job (cron) crashed or fell behind.
Seats remain in HELD state indefinitely.
Available inventory: 0 (all held, none confirmed).

**Fix:**
```python
# Multiple layers of expiry - not just the cron job

# Layer 1: Redis TTL (most reliable)
# Redis automatically expires keys. If you use Redis
# for holds, TTL expiry is automatic and reliable.
# Redis keyspace notifications → restore to available.

# Layer 2: PostgreSQL-based expiry (belt+suspenders)
def get_available_count_ignoring_stale_holds(
        event_id: int) -> int:
    """
    Count seats available, treating expired holds
    as available even if not yet released by cron.
    """
    return db.query_one(
        "SELECT COUNT(*) as n FROM seats "
        "WHERE event_id = %s "
        "AND (status = 'AVAILABLE' "
        "OR (status = 'HELD' "
        "    AND hold_expires_at < NOW()))",
        [event_id]
    )['n']

# Layer 3: On hold_seat() failure, immediately attempt
# to claim expired holds before giving up:
def hold_seat_with_expiry_reclaim(
        user_id: int, event_id: int) -> dict:
    # Try normal hold first
    result = try_hold_available_seat(user_id, event_id)
    if result['success']:
        return result
    
    # No available seats: try to claim an expired hold
    with db.transaction():
        rows = db.execute(
            "UPDATE seats "
            "SET status = 'HELD', "
            "held_by_user_id = %s, "
            "hold_expires_at = NOW() + INTERVAL '10 min'"
            "WHERE event_id = %s "
            "AND status = 'HELD' "
            "AND hold_expires_at < NOW() "
            "LIMIT 1 "
            "RETURNING id",
            [user_id, event_id]
        )
        if rows:
            return {
                "success": True,
                "seat_id": rows[0]['id'],
                "reclaimed_expired_hold": True
            }
    
    return {"success": False, "error": "Sold out"}

# Layer 4: Monitoring alert
# Alert if count of expired-but-not-released holds > 0
# for more than 2 minutes (cron is not running)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Distributed Transactions` - the booking flow
  involves DB + payment; saga pattern coordinates them
- `Event Sourcing` - booking lifecycle as an event
  stream: CREATED → HELD → CONFIRMED events

**Builds On This (learn these next):**
- `CQRS` - separate write model (booking state machine)
  from read model (availability queries)
- `Payment System Design` - payment is the confirmation
  step; idempotency + outbox apply here
- `Database Internals` - understanding SELECT FOR UPDATE,
  MVCC, optimistic locking under the hood

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HOLD FLOW   │ AVAILABLE → HELD (10min TTL) → CONFIRMED │
│             │ Hold expiry: Redis TTL or cron job.      │
├─────────────┼──────────────────────────────────────────  │
│ PESSIMISTIC │ SELECT FOR UPDATE. Serial. Correct.      │
│             │ Low throughput under contention.        │
├─────────────┼──────────────────────────────────────────  │
│ OPTIMISTIC  │ UPDATE WHERE version=N. Check rows_affected│
│             │ 0 rows = conflict. Retry.               │
├─────────────┼──────────────────────────────────────────  │
│ REDIS       │ SPOP from available set (atomic).        │
│             │ SETEX for hold with TTL. 100K ops/sec.  │
├─────────────┼──────────────────────────────────────────  │
│ ATOMICITY   │ Check + book = ONE atomic SQL operation. │
│             │ Never: SELECT then UPDATE (race cond.)  │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Hold state machine + TTL expiry.       │
│             │  Redis SPOP for high contention."      │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Real-Time Collaboration System Design     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Check + book must be ONE atomic operation.
   `UPDATE seats SET status='HELD' WHERE status='AVAILABLE'`.
   Check rows_affected. 0 = seat was taken. Retry.
   Never: SELECT to check availability, then UPDATE.
   That's a race condition - another transaction can
   book between your SELECT and UPDATE.
2. Seat hold pattern: AVAILABLE → HELD (with TTL) →
   CONFIRMED. The hold expires automatically (Redis TTL
   or a background job). This handles abandoned carts
   without leaving inventory locked forever.
3. For high-throughput (concert tickets): Redis SPOP
   from an available seats set = O(1), atomic, no
   contention. For lower-throughput: PostgreSQL optimistic
   locking (UPDATE WHERE version=N, check rows_affected).

**Interview one-liner:**
"Booking system core: prevent double-booking with atomic UPDATE WHERE status='AVAILABLE'
- check rows_affected (0 = taken). Hold pattern: AVAILABLE → HELD (TTL=10min) →
CONFIRMED or RELEASED; expiry handled by Redis TTL or cron job. Pessimistic locking
(SELECT FOR UPDATE): correct but sequential, low throughput under contention.
Optimistic locking (version check): high throughput, retries on conflict, good for
moderate contention. High-throughput (concert sale): Redis SPOP from available set
(atomic O(1)); SETEX for hold with TTL. Write to DB async (Kafka) for audit trail.
Saga pattern for cross-service: hold seat, then charge payment, with compensation
(release hold) if payment fails."
