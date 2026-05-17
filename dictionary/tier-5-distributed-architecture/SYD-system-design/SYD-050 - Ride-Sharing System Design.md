---
id: SYD-050
title: Ride-Sharing System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-031
used_by: ""
related: SYD-008, SYD-031, SYD-039, SYD-048
tags:
  - architecture
  - geospatial
  - matching
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /syd/ride-sharing-system-design/
---

# SYD-050 - Ride-Sharing System Design

⚡ TL;DR - A ride-sharing system matches riders to
nearby available drivers in real-time (< 5 seconds),
tracks driver location continuously, and coordinates
the trip lifecycle (request, match, pickup, in-progress,
complete, payment). The hard problems: location-based
matching (geospatial queries at scale - who is nearby
right now?), driver location tracking (millions of GPS
updates/second), and the matching algorithm (minimize
wait time, maximize driver utilization). Geohash or
QuadTree is used to bucket drivers by location for
efficient proximity queries.

| #050 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, Sharding | |
| **Related:** | Caching, Sharding, Distributed Locks, Chat System Design | |

---

### 🔥 The Problem This Solves

Uber has 5M+ drivers worldwide. When a rider requests
a trip in New York, the system must instantly find all
available drivers within 2km, select the best match,
and notify that driver - all in under 5 seconds. This
requires:
- Knowing the real-time location of 5M moving drivers
  (GPS updates every 3-5 seconds: 1-2M updates/second)
- Efficiently querying "all drivers within 2km of lat/lng"
  (geospatial query over 5M dynamic points)
- Handling concurrent requests (multiple riders requesting
  in the same area at the same time: each driver can
  match only one rider)

---

### 📘 Textbook Definition

**Ride-sharing system:** A platform that connects riders
requesting transportation with nearby drivers in real-time.
Core operations: (1) location tracking (continuous GPS
updates from driver apps), (2) proximity matching (find
available drivers near a rider's location), (3) trip
lifecycle management (request → match → pickup → complete),
(4) payment processing, and (5) real-time communication
between rider and driver.

**Geohash:** A hierarchical spatial indexing system that
encodes a geographic coordinate (lat/lng) into a short
alphanumeric string. Nearby locations share geohash
prefixes. Enables simple string-prefix queries instead
of complex geospatial range queries.

**QuadTree:** A tree structure that recursively divides
geographic space into 4 quadrants. Efficient for "find
all points within N km" queries by pruning irrelevant
quadrants.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Rider requests trip → find all available drivers within
radius → pick best → lock driver (atomic) → assign trip.

**One analogy:**
> A city taxi dispatcher:
>
> The dispatcher has a big board showing all taxis with
> blinking lights at their current positions. When a
> customer calls, the dispatcher looks at the board,
> finds the closest free taxi in the caller's neighborhood,
> calls that taxi and assigns the fare.
>
> If two customers call simultaneously and both are
> closest to the same taxi, the dispatcher must pick
> one call and tell the other to wait (the matching
> algorithm must be atomic - a driver cannot accept
> two trips simultaneously).

**One insight:**
The geospatial query is the core scalability challenge.
Naively: "SELECT drivers WHERE distance(lat, lng, driver.lat,
driver.lng) < 2km" scans all drivers - O(N). With geohash
indexing: convert rider's coordinates to a geohash prefix,
query drivers with the same geohash (neighboring area) -
O(1) lookup for the geohash bucket, then a small number
of distance calculations. This reduces the search space
from 5M to typically < 100 drivers.

---

### 🔩 First Principles Explanation

**GEOHASH FOR PROXIMITY:**
```
Geohash: encode lat/lng to a string.
  Precision level (character count) = area size:
  6 chars: ~1.2km × 0.6km cell
  7 chars: ~153m × 153m cell
  
  Riders and drivers at 6-char precision:
    Rider:  lat=40.7128, lng=-74.0060 → "dr5ru6"
    Driver: lat=40.7130, lng=-74.0062 → "dr5ru6" (same cell)
  
  To search nearby:
    1. Get rider's 6-char geohash "dr5ru6"
    2. Get the 8 neighboring geohashes
       (a cell has 8 neighbors)
    3. Look up available drivers in all 9 cells
       (rider's cell + 8 neighbors)
    4. For all found drivers, calculate exact distance
    5. Filter by 2km radius
  
  Result: 9 Redis lookups instead of full scan.
  
  Why search neighbors too?
    Edge case: rider is at the boundary of cell "dr5ru6"
    and the nearest driver is just across the boundary
    in cell "dr5ru5". Without checking neighbors, the
    nearest driver is missed.
```

**DRIVER LOCATION TRACKING:**
```
Driver app: sends GPS update every 3-5 seconds.
Update: {driver_id, lat, lng, status, timestamp}

At 5M drivers × 1 update/4 seconds:
  = 1.25M updates/second

Store current location in Redis:
  driver:{driver_id}:location = 
    {lat: 40.71, lng: -74.00, geohash: "dr5ru6"}
  
  Redis handles 1M+ operations/second on a cluster.
  TTL: 30 seconds (stale if no heartbeat received)

Redis Geo API (built-in geospatial support):
  GEOADD drivers:available {lng} {lat} {driver_id}
  GEORADIUS drivers:available {lng} {lat} 2 km ASC COUNT 10
  → returns nearest 10 available drivers within 2km

Redis GEORADIUS:
  Internally uses geohash with neighbor cell search.
  Precalculated for fast lookups. Production-ready.
```

**TRIP LIFECYCLE:**
```
States: REQUESTED → MATCHED → PICKUP → IN_PROGRESS
        → COMPLETED → CANCELLED

On rider request:
  1. Rider app: POST /trip/request {pickup, dropoff}
  2. Trip service: create trip (status=REQUESTED)
  3. Location service: GEORADIUS to find nearby drivers
  4. Matching service: rank drivers (distance, ratings)
  5. Offer trip to best driver (WebSocket push)
  6. Driver accepts: 
     a. Atomically claim driver:
        SET driver:{id}:trip_id {trip_id} NX EX 120
        (NX: only if not already assigned)
        If fails: driver already taken, try next
     b. Update trip status: MATCHED
     c. Update driver status: BUSY (remove from
        drivers:available sorted set)
  7. Notify rider: driver matched, ETA
```

---

### 🧪 Thought Experiment

**SIZING: Uber-scale ride matching**

Active cities: 1,000 cities. Largest city (NY): 50K
active drivers, 10K active riders, 500 trip requests/min.

**Location updates:**
50K drivers in NY × 1 update/4 sec = 12,500 updates/sec in NY.
Global: 5M drivers = 1.25M updates/sec. Redis Cluster: easily handled.

**Trip matching:**
500 requests/minute in NY = ~8 requests/sec.
Each request: GEORADIUS (1 Redis call) + matching + 1-3
driver offers (WebSocket). Sub-100ms per match is feasible.

**Concurrent match race condition:**
If 100 riders request at once and 5 available drivers
are nearby, multiple riders may select the same driver.
Solution: Redis SET NX (atomic claim) on driver assignment.
Expected retries: if top 5 drivers are all contended,
8th match attempt goes to driver 6, etc. Typical: 1-2
retries per request at peak load.

**Driver location store:**
5M drivers × ~100 bytes per geo entry = 500MB.
Trivial for Redis. Per-city Redis instances for isolation.

---

### 🧠 Mental Model / Analogy

> Ride-sharing matching is like a hospital emergency triage system:
>
> Patients (riders) arrive with varying urgency (surge pricing).
> Available doctors (drivers) are tracked on a hospital map.
> When a patient arrives, the triage nurse (matching service)
> checks the map for the nearest available doctor in the
> right department (geohash cell).
>
> If the nearest doctor is already with a patient (BUSY),
> the nurse checks the next nearest. When a doctor is
> assigned, the system marks them BUSY immediately (atomic)
> so the next patient does not also get assigned to them.
>
> The doctor's location is tracked continuously (GPS →
> Redis), so the map is always current.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A ride-sharing app connects people who need a ride with
nearby drivers. The app knows where all drivers are
(GPS), shows you nearby options, and matches you with
the closest available driver. You can track the driver
coming to you on the map.

**Level 2 - How to use it (junior developer):**
Driver app sends GPS location every few seconds to a
server. Store locations in a database with geospatial
indexing. When a rider requests a trip, query nearby
drivers, pick the closest, send them a trip request.
Use WebSocket for real-time communication between
rider and driver apps.

**Level 3 - How it works (mid-level engineer):**
Redis GEORADIUS for proximity queries (converts lat/lng
to geohash internally, queries nearby cells). Driver
location stored as Redis Geo entry with TTL. Trip
matching: GEORADIUS → rank by distance/rating → offer
to best driver → atomic claim with Redis SET NX (prevent
two riders from getting the same driver). WebSocket
for driver offer push, location updates to rider.

**Level 4 - Why it was designed this way (senior/staff):**
Redis is the right tool for driver location because it
provides: (1) in-memory speed (< 1ms location lookup),
(2) built-in geo commands (GEORADIUS abstracts the
geohash math), (3) TTL for automatic cleanup of offline
drivers (no heartbeat in 30s = removed from the
available set). The atomic claim (SET NX) prevents the
double-booking race condition: if two matching services
try to assign the same driver simultaneously, only one
succeeds (NX = only set if key doesn't exist). The loser
retries with the next best driver. Separate Redis keys
for "available" and "location" because drivers transition
between states (available → busy) without changing
location data.

**Level 5 - Mastery (distinguished engineer):**
The matching algorithm is where Uber/Lyft have the most
IP. It is not simply "closest driver." It optimizes for:
(1) minimizing rider wait time, (2) maximizing driver
utilization (reduce dead miles - time driving without
a passenger), (3) fairness (drivers with lower income
get offered trips too, not just top-rated drivers),
(4) surge pricing calibration (real-time supply/demand
balancing). This is a multi-objective optimization
problem solved with ML models trained on historical trip
data. At the system level, the matching service processes
matching "ticks" (every few seconds, batch-process all
open requests against all available drivers globally)
using LP (linear programming) or auction algorithms
to find the global optimum, rather than greedy per-
request matching. This is how shared rides (two riders
going in the same direction) are matched efficiently.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ RIDE-SHARING CORE FLOW                              │
│                                                      │
│ LOCATION TRACKING:                                  │
│  Driver App ──GPS update every 4s──►               │
│    Location Service ──GEOADD──► Redis Geo Set      │
│    ("drivers:available" or "drivers:busy")          │
│    TTL: 30s (auto-remove offline drivers)           │
│                                                      │
│ TRIP REQUEST:                                       │
│  Rider App ──POST /trip──► Trip Service            │
│  ──GEORADIUS drivers:available {lat} {lng} 2km──►  │
│    Redis: returns [{driver_id, distance}]           │
│  ──rank by distance + rating──►                    │
│    Best driver = driver_id_42                      │
│  ──WebSocket push "trip offer"──► Driver 42        │
│                                                      │
│ DRIVER ACCEPTS:                                     │
│  ──SET driver:42:trip_id {trip_id} NX EX 120──►    │
│    Success: driver claimed atomically              │
│    Failure: driver already claimed, retry next     │
│  ──ZREM drivers:available driver_42──►             │
│    Driver removed from available set (now BUSY)    │
│  ──WebSocket push to rider: driver matched, ETA    │
│                                                      │
│ TRIP TRACKING:                                      │
│  Driver location updates continue every 4s         │
│  Location Service: push driver location to rider   │
│    via WebSocket (rider sees driver moving on map) │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Driver location tracking and matching (Python/Redis)**
```python
import redis
import math
from typing import Optional

r = redis.Redis()
AVAILABLE_KEY = "drivers:available"
BUSY_KEY = "drivers:busy"

def update_driver_location(driver_id: int, lat: float,
                             lng: float, available: bool):
    """Update driver GPS location in Redis Geo set."""
    geo_set = AVAILABLE_KEY if available else BUSY_KEY

    # Add/update location in the geo set
    # GEOADD: score = geohash of (lng, lat)
    # Redis geo: longitude before latitude (GeoJSON order)
    r.geoadd(geo_set, [lng, lat, str(driver_id)])

    # Set heartbeat key with TTL
    # Driver auto-removed from consideration if no heartbeat
    r.setex(f"driver:{driver_id}:heartbeat", 30, "1")

    # Store full metadata (status, rating, etc.)
    r.hset(f"driver:{driver_id}", mapping={
        "lat": lat, "lng": lng,
        "status": "available" if available else "busy",
    })

def find_nearby_drivers(
    rider_lat: float, rider_lng: float,
    radius_km: float = 2.0,
    max_results: int = 10
) -> list:
    """
    Find available drivers within radius of rider.
    Returns list of (driver_id, distance_km).
    """
    # Redis GEORADIUS: returns drivers sorted by distance
    results = r.georadius(
        AVAILABLE_KEY,
        rider_lng, rider_lat,   # GeoJSON: lng first
        radius_km, "km",
        withcoord=True,
        withdist=True,
        sort="ASC",
        count=max_results
    )
    drivers = []
    for result in results:
        driver_id = int(result[0])
        distance = float(result[1])
        # Verify heartbeat is still fresh
        heartbeat = r.get(f"driver:{driver_id}:heartbeat")
        if heartbeat:
            drivers.append({
                "driver_id": driver_id,
                "distance_km": distance
            })
    return drivers

def atomic_assign_driver(driver_id: int,
                           trip_id: str) -> bool:
    """
    Atomically claim driver for a trip.
    Returns True if claimed, False if already taken.
    Uses SET NX to prevent double-booking race condition.
    """
    claim_key = f"driver:{driver_id}:trip_id"
    # NX: only set if key does not exist
    # EX 120: auto-release if trip not started in 2 min
    claimed = r.set(claim_key, trip_id, nx=True, ex=120)
    if claimed:
        # Move driver from available to busy
        # Atomically in a pipeline
        pipe = r.pipeline()
        pipe.zrem(AVAILABLE_KEY, str(driver_id))
        pipe.zadd(BUSY_KEY, {str(driver_id): 0})
        pipe.hset(f"driver:{driver_id}",
                  "status", "busy")
        pipe.execute()
    return bool(claimed)

def match_trip(rider_lat: float, rider_lng: float,
               trip_id: str) -> Optional[int]:
    """
    Find and claim the best available driver.
    Returns driver_id if matched, None otherwise.
    """
    nearby = find_nearby_drivers(
        rider_lat, rider_lng, radius_km=2.0)

    for driver in nearby:
        driver_id = driver["driver_id"]
        if atomic_assign_driver(driver_id, trip_id):
            return driver_id  # Successfully matched!

    return None  # No available drivers in radius
```

**Example 2 - Full table scan (BAD geospatial approach)**
```python
# BAD: Linear scan of all drivers
def find_nearby_drivers_bad(rider_lat, rider_lng):
    # SELECT * FROM drivers WHERE status='available'
    # Returns ALL 5M drivers, then filter in Python
    all_drivers = db.query(
        "SELECT id, lat, lng FROM drivers "
        "WHERE status = 'available'"
    )  # 5M rows transferred from DB to app server!
    
    nearby = []
    for d in all_drivers:
        dist = haversine(rider_lat, rider_lng,
                         d.lat, d.lng)
        if dist < 2.0:
            nearby.append((d.id, dist))
    return nearby
    # Latency: minutes at scale.
    # DB: cannot serve anything else during this query.
    # Kills the system at production load.

# GOOD: Use Redis GEORADIUS (geohash index)
# O(log N + k) where k = results near the query point
# Typical: 1ms for 5M drivers, returns top 10 nearby.
```

---

### ⚖️ Comparison Table

| Location Index | Lookup Complexity | Update Complexity | Suited For |
|---|---|---|---|
| **Full table scan** | O(N) | O(1) | Prototype only |
| **Redis GEORADIUS** | O(log N + k) | O(log N) | 5M drivers, < 1ms |
| **PostGIS spatial index** | O(log N) | O(log N) | Durable storage + complex queries |
| **QuadTree** | O(log N) | O(log N) | Custom in-memory spatial index |
| **Geohash prefix index** | O(1) lookup | O(1) update | Simple, good enough for most |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Closest driver = best match | Uber/Lyft use multi-objective matching: closest driver is one input, but driver rating, car type, route efficiency (especially for shared rides), and driver equity (ensuring work is distributed fairly) all influence the match. Simple greedy "closest driver" has worse overall metrics than optimized batch matching. |
| Driver location can be stored in a relational DB with geospatial index | It can, but SQL geospatial indexes (PostGIS) are optimized for durable persistent queries, not 1M+ write updates per second. Redis in-memory geo operations are 10-100x faster for this use case. Use Redis for real-time driver location; sync to a durable store (Postgres + PostGIS) for analytics and trip history. |
| The matching service can take as long as needed | Riders become frustrated after 5-10 seconds without a match result. The matching service has a hard 5-second SLA. If no driver is found within that window, the system either expands the search radius, retries with relaxed constraints, or returns "no drivers available." This timeout logic is critical for user experience. |

---

### 🚨 Failure Modes & Diagnosis

**Double-Booking: Same Driver Assigned to Two Trips**

**Symptom:**
Two riders both receive confirmation that Driver X
is matched to their trip. Driver X's app shows one
trip; the other rider's trip is stuck in "matching."
Riders complain about cancelled trips and poor ETA
estimates.

**Root Cause:** The matching service is horizontally
scaled (10 instances). Two instances simultaneously
ran `find_nearby_drivers` and both selected Driver X
as the best match. Both called `atomic_assign_driver`
within milliseconds of each other. Without atomic
claim, both succeeded.

**Diagnosis:**
Check matching service logs for `trip_id` assigned
to a driver that already had an active trip.
Check Redis for `driver:{id}:trip_id` key existing
before the second assignment.

**Fix (already shown in atomic_assign_driver above):**
```python
# Redis SET NX: only one assignment succeeds
claimed = r.set(claim_key, trip_id, nx=True, ex=120)
# The second matching service instance:
# claimed = None (False) → retry with next driver

# Monitoring: track atomic_assign_driver failure rate
# High failure rate → system under contention:
#   few available drivers, many concurrent requests
# Alerting: if failure rate > 30%, expand search radius
# or trigger surge pricing to incentivize more drivers

# Validate: integration test
# Send 100 concurrent trip requests in the same area
# with 5 available drivers. Assert 0 double-bookings.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - Redis for driver location storage,
  proximity queries, and atomic operations
- `Sharding` - driver data sharded by geo region
  for global scale

**Builds On This (learn these next):**
- `Distributed Locks` - Redis NX is a lightweight
  distributed lock for driver assignment
- `Chat System Design` - WebSocket pattern reused
  for real-time rider-driver communication

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LOCATION    │ Redis GEOADD every 4s. TTL 30s.           │
│             │ GEORADIUS for proximity (1ms for 5M pts). │
├─────────────┼──────────────────────────────────────────  │
│ MATCHING    │ GEORADIUS → rank → SET NX claim (atomic). │
│             │ Second match on same driver: fails → retry│
├─────────────┼──────────────────────────────────────────  │
│ GEOHASH     │ 6-char = ~1km cell. Search cell + 8      │
│             │ neighbors to handle boundary edges.      │
├─────────────┼──────────────────────────────────────────  │
│ RACE        │ Concurrent matches → Redis SET NX.       │
│             │ NX = only set if not exists. Atomic.     │
│             │ Loser retries with next best driver.     │
├─────────────┼──────────────────────────────────────────  │
│ REAL-TIME   │ WebSocket for trip offer push, rider     │
│             │ receives driver location updates.        │
├─────────────┼──────────────────────────────────────────  │
│ SLA         │ Match must complete in < 5 seconds.      │
│             │ Expand radius if no driver found in 3s.  │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Redis Geo + atomic SET NX = proximity  │
│             │  matching without double-booking"        │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Search System Design → Distributed Cache │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use Redis GEORADIUS for driver proximity queries.
   It is O(log N + k) - fast enough for 5M drivers.
   Store driver locations in a Redis Geo set, updated
   every 4 seconds. TTL of 30 seconds auto-removes
   offline drivers.
2. Atomic driver assignment is mandatory. Multiple matching
   service instances run concurrently. Without atomic
   claim (Redis SET NX), two riders can both get the same
   driver. SET NX guarantees only one succeeds; the other
   retries with the next best driver.
3. The matching SLA is 5 seconds. If no driver found
   in 2-3 seconds, expand the search radius (2km → 5km
   → 10km). If still none, return "no drivers available."
   Do not let the request spin indefinitely - rider UX
   degrades rapidly after 5 seconds without a response.

**Interview one-liner:**
"Ride-sharing: drivers send GPS every 4 seconds → Redis GEOADD with 30s TTL
(offline drivers auto-expire). Rider requests trip → GEORADIUS (2km radius) →
rank by distance/rating → offer to best driver. Atomic assignment: Redis SET NX
on driver:{id}:trip_id - only one matching instance can claim the driver. If NX
fails (already claimed): retry with next driver. Driver moves from 'available' to
'busy' geo set on assignment. Real-time: WebSocket for trip offer push and ongoing
location updates to rider. Match SLA: 5 seconds - expand radius progressively if
no drivers found."
