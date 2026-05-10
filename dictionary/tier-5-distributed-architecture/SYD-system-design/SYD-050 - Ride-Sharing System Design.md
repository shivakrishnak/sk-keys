---
id: SYD-050
title: Ride-Sharing System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-023
used_by:
related: SYD-048, SYD-047, SYD-027
tags:
  - architecture
  - advanced
  - distributed
  - realtime
status: complete
version: 2
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /syd/ride-sharing-system-design/
---

# SYD-050 - Ride-Sharing System Design

⚡ TL;DR - Ride-sharing systems track driver locations in real
time via geospatial indexes, match riders to nearby drivers using
batch optimisation, and manage a two-sided marketplace with
dynamic pricing.

| Field           | Detail                            |
| :-------------- | :-------------------------------- |
| **Depends on:** | SYD-023 - Geo-Replication        |
| **Used by:**    | -                                 |
| **Related:**    | SYD-048, SYD-047, SYD-027        |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Traditional taxi dispatch was phone-based: customers called a
central number, a dispatcher radioed the nearest driver they knew
about, and accuracy depended entirely on drivers calling in their
location. There was no real-time visibility into driver positions,
no ETA estimation, and supply-demand imbalance was invisible until
wait times exploded.

**THE BREAKING POINT:**
GPS-enabled smartphones (2007) made real-time consumer location
sharing practical. Customers now expected to see nearby drivers
on a map, get accurate ETAs, and request a ride without phone
calls. The new product demand - millions of driver location updates
per second, sub-second matching, and dynamic surge pricing - was
impossible with phone dispatch.

**THE INVENTION MOMENT:**
The core insight: treat driver location as a continuously updated
geospatial index. Index drivers by geographic cell (not by driver
ID or proximity list). Match riders to the index, not to
individual drivers. Run matching as a batch optimisation (not
greedy nearest-driver) to maximise global efficiency.

**EVOLUTION:**
Ride-sharing emerged from GPS-enabled smartphones making real-time
location sharing practical at consumer scale. Uber (2009) and
Lyft (2012) demonstrated that a marketplace matching model -
riders bidding for supply dynamically - outperformed fixed-price
taxi dispatch. The engineering challenge evolved from basic
location tracking to surge pricing algorithms, ETA prediction
with traffic, and fraud detection at marketplace scale. The
discipline absorbed techniques from computational geometry
(geospatial indexing), operations research (optimal matching
under uncertainty), and real-time systems (sub-second dispatch
latency). Modern ride-sharing platforms are simultaneously
logistics systems, financial systems, and real-time two-sided
marketplaces.

---

### 📘 Textbook Definition

**Ride-Sharing System Design** is a system design problem
centred on ingesting and indexing continuous driver location
updates, matching riders to nearby available drivers using
optimisation algorithms, computing dynamic surge pricing from
supply-demand imbalance, and managing a two-sided marketplace
at internet scale.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Keep driver locations fresh in a geospatial index and match
riders to drivers using batch optimisation, not greedy nearest.

**One analogy:**

> An air traffic control system: aircraft positions stream in
> continuously, the radar screen shows real-time positions, and
> controllers assign landing slots by optimising for the entire
> airspace, not just the nearest available runway.

**One insight:**
Geospatial proximity queries need geospatial data structures.
Storing latitude/longitude in a relational database and running
radius queries at scale is a bottleneck; geospatial indexes
(H3, S2, QuadTree) answer proximity in O(log n).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Driver locations change continuously (every 3-5 seconds);
   any stale location is a potential mismatch.
2. Geographic proximity is the primary matching constraint -
   a driver 30 minutes away is irrelevant regardless of other
   attributes.
3. Supply-demand imbalance is local and real-time; pricing must
   reflect current conditions in a specific geographic cell.
4. Matching quality is global (optimise all active riders and
   drivers together), not local (greedily assign nearest driver
   to each rider independently).

**DERIVED DESIGN:**
Invariant 1 derives the streaming location ingest pipeline.
Invariant 2 derives geospatial indexing (not relational lat/lon).
Invariant 3 derives per-cell surge pricing computation.
Invariant 4 derives batch matching (not greedy).

**THE TRADE-OFFS:**
**Gain:** Low wait times; accurate ETAs; fair driver earnings;
dynamic supply incentivisation via surge.
**Cost:** Real-time geospatial index complexity; matching
algorithm latency budget (500ms for batch); surge pricing
user experience risk.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Location freshness; geospatial proximity queries;
supply-demand pricing; batch matching optimisation.
**Accidental:** Per-city database sharding (abstracted by
geographic cell sharding); routing graph recomputation
(use external map API); driver state machine complexity.

---

### 🧪 Thought Experiment

**SETUP:** You are building a ride-sharing app. You store driver
locations in a standard relational database with latitude and
longitude columns. You run a `WHERE distance(lat, lon) < 500m`
query on every ride request.

**WHAT HAPPENS WITHOUT IT:**
With 100,000 active drivers citywide, every ride request triggers
a full table scan (no spatial index). At 1,000 concurrent ride
requests per second, the database performs 100 million distance
comparisons per second. At 10,000 requests per second (peak
surge), the database falls over. Driver matches take 10+ seconds.
Riders see "finding driver..." forever.

**WHAT HAPPENS WITH IT:**
A geospatial index (H3 hexagonal grid) divides the city into
geographic cells. A driver update writes to the cell the driver
is in. A ride request queries only the cells within 500m radius.
With average cell populations of 10-50 drivers, matching
requires comparing 50-200 drivers, not 100,000. Query time is
sub-millisecond at any scale.

**THE INSIGHT:**
Geospatial problems require geospatial data structures. The
correct abstraction is the geographic cell, not the individual
driver record.

---

### 🧠 Mental Model / Analogy

> A cellular network tower map: the city is divided into coverage
> cells. When your phone moves between cells, the network updates
> your cell assignment. When you make a call, the network routes
> it through your current cell's tower, not by scanning every
> tower in the country.

Element mapping:
- Cell tower coverage area = geospatial cell (H3 hex / S2 cell)
- Your phone = driver (continuously reporting position)
- Network routing = matching engine (queries active cell)
- Call setup = ride matching (O(drivers in cell), not all drivers)
- Coverage handoff = driver moving between geographic cells

Where this analogy breaks down: cellular handoffs are geography-
deterministic; ride matching has multiple optimisation objectives
(ETA, driver fairness, marketplace efficiency) not just geography.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Ride-sharing apps see where all the nearby drivers are (because
drivers send their location constantly), and when you request a
ride, the app picks the most suitable driver quickly.

**Level 2 - How to use it (junior developer):**
Drivers send location updates every 4 seconds to a location
service. Store positions in Redis with geospatial commands
(`GEOADD`, `GEORADIUS`). On ride request, query nearby available
drivers, pick the closest, and send notifications to both rider
and driver.

**Level 3 - How it works (mid-level engineer):**
Location updates stream into a location ingest service that writes
to a geospatial index (Redis with H3 cell keys or a PostGIS
instance). The matching engine runs every 500ms as a batch: for
all unmatched riders, query available drivers in nearby cells,
run a linear assignment optimisation (minimising sum of ETAs),
and assign matches. Surge pricing computes per-cell supply-demand
ratio every 60 seconds and updates the multiplier in the pricing
service.

**Level 4 - Why it was designed this way (senior/staff):**
Greedy nearest-driver matching is locally optimal but globally
suboptimal: it can assign a driver 2 minutes away while a driver
4 minutes away is positioned to serve 3 future riders. Batch
matching (Hungarian algorithm or approximations) solves the global
assignment problem across all active riders and drivers in a city
in under 500ms. Uber's move from greedy to batch matching
increased driver earnings by 15% without adding new drivers.
Geographic cell sharding (rather than random database sharding)
ensures that all data for a geographic region is co-located,
making proximity queries local within a shard.

**Expert Thinking Cues:**
- "What is the staleness budget for driver location?" - 30-60
  seconds before a match is likely incorrect.
- "Why not use PostgreSQL with PostGIS?" - viable at small scale;
  at Uber scale (50K updates/sec/city), a specialised in-memory
  geospatial store is necessary.
- "How do you shard the geospatial index?" - by geographic cell
  prefix (H3 resolution level), not by driver ID.

---

### ⚙️ How It Works (Mechanism)

```
Driver update pipeline:
  Driver app (GPS) -> Location service (every 4s)
    -> Geospatial index update (H3 cell key in Redis)
    -> Driver state store (available/busy/offline)
    -> ETA service feed (for routing graph)

Ride matching pipeline (500ms batch):
  Ride requests -> Matching service
    -> Query geospatial index (nearby cells, r=2km)
    -> Filter: available drivers only
    -> Run batch assignment (linear optimisation)
    -> Assign matches, notify via push + in-app message
    -> Update driver state to 'en route'

Surge pricing pipeline (60s compute):
  Per-cell: supply_drivers / demand_riders
    -> multiplier = f(ratio, historical baseline)
    -> Write to pricing cache (Redis)
    -> Expose to rider app at request time
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
+----------+ (GPS, 4s) +----------+  write  +----------+
|  Driver  |---------->| Location |-------->|Geospatial|
|   App    |           | Ingest   |         |  Index   |
+----------+           +----------+         | (Redis)  |
                                            +----+-----+
                                                 |
+----------+ request   +----------+  query       |
|  Rider   |---------->| Matching |<-------------+
|   App    |           | Engine   |
+----------+           | (500ms   |
                        | batch)   |  <- YOU ARE HERE
                        +----+-----+  (batch optimisation)
                             |
                        assign match
                             |
                   +---------+---------+
                   |                   |
             +-----+----+        +-----+----+
             | Notify   |        | Notify   |
             | Driver   |        | Rider    |
             | (push)   |        | (push)   |
             +----------+        +----------+
```

**FAILURE PATH:**
- Location ingest overload: reduce update frequency (5s -> 10s);
  shed load for offline drivers.
- Matching engine timeout: fall back to greedy nearest-driver;
  slightly worse outcomes but instant.
- Geospatial index unavailable: read from replica; accept slight
  location staleness.

**WHAT CHANGES AT SCALE:**
- 50K location updates/sec/city: shard geospatial index by city
  and H3 cell prefix; use in-memory store.
- 10K concurrent ride requests: batch matching parallelised by
  geographic region; each batch solver handles one sub-region.
- Global deployment: per-city infrastructure; no cross-city
  geospatial queries needed.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
- Driver state transitions (available -> en_route -> in_trip ->
  available) must be atomic to prevent double-assignment.
- Matching reads and writes the same geospatial index; use
  optimistic locking or a single-writer matching service per
  region.
- Surge pricing writes every 60s; readers accept eventual
  consistency (rider sees slightly stale surge multiplier).

---

### 💻 Code Example

**BAD - Geospatial query on relational table:**

```python
# Full table scan; fails at > 10K drivers
def find_nearby_drivers(lat, lon, radius_km):
    return db.execute('''
        SELECT driver_id, lat, lon,
          6371 * acos(cos(radians(:lat))
            * cos(radians(lat))
            * cos(radians(lon) - radians(:lon))
            + sin(radians(:lat))
            * sin(radians(lat))) AS dist
        FROM drivers
        WHERE status = 'available'
        HAVING dist < :r
        ORDER BY dist
    ''', lat=lat, lon=lon, r=radius_km).all()
    # O(N) full table scan for every request
```

**GOOD - Geospatial index with H3 cells:**

```python
import h3

SEARCH_RADIUS_KM = 2.0
H3_RESOLUTION = 9  # ~0.1 km2 per hexagon

def update_driver_location(driver_id, lat, lon):
    cell = h3.geo_to_h3(lat, lon, H3_RESOLUTION)
    redis.geoadd(f"drivers:{cell}", lon, lat, driver_id)
    redis.setex(f"driver_cell:{driver_id}", 30, cell)

def find_nearby_drivers(lat, lon):
    origin_cell = h3.geo_to_h3(lat, lon, H3_RESOLUTION)
    nearby_cells = h3.k_ring(origin_cell, k=2)
    drivers = []
    for cell in nearby_cells:
        cell_drivers = redis.georadius(
            f"drivers:{cell}", lon, lat,
            SEARCH_RADIUS_KM, unit='km',
            withcoord=True
        )
        drivers.extend(cell_drivers)
    return drivers
    # O(k * drivers_per_cell) not O(all_drivers)
```

**How to test / verify correctness:**
- Unit: test that `update_driver_location` writes to the correct
  H3 cell key.
- Integration: insert 100K driver positions; verify
  `find_nearby_drivers` returns only drivers within 2km and runs
  in < 10ms.
- Load: simulate 50K location updates/sec; verify Redis write
  throughput and read latency remain within budget.

---

### ⚖️ Comparison Table

| Approach            | Use when                          | Limitation          |
| ------------------- | --------------------------------- | ------------------- |
| Redis GEORADIUS     | < 1M active drivers               | Single instance     |
| PostGIS             | Complex geo queries + persistence | Lower write rate    |
| H3 + Redis sharded  | > 1M drivers, city-scale          | Boundary complexity |
| S2 Geometry library | 3D geo (aviation, global scale)   | Higher complexity   |
| QuadTree in-memory  | Custom matching logic needed      | Memory-bound        |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Nearest driver is always the best match" | Greedy nearest-driver is locally optimal but globally suboptimal. Batch matching (considering all riders and drivers together) consistently outperforms greedy by 10-20% on average ETA. |
| "Storing lat/lon in PostgreSQL with an index is enough" | A B-tree index on lat/lon cannot efficiently answer radius queries. You need a spatial index (R-tree / GiST) or a dedicated geospatial tool. At > 10K updates/sec, relational databases require specialised extensions. |
| "Surge pricing is purely profit-driven" | Surge pricing is a two-sided marketplace signal: it incentivises more drivers to go online, increasing supply during high demand. Without surge, demand permanently exceeds supply during peaks and no drivers are incentivised to join. |
| "Driver location updates can be infrequent" | Location freshness directly determines match quality. A location 60 seconds old can place a driver 500m from their actual position. Staleness thresholds should be tuned to the mismatch cost. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Location staleness causing mismatched ETAs**

**Symptom:** Rider's app shows driver is 2 minutes away; actual
arrival is 8 minutes. Driver location on map appears frozen.

**Root Cause:** Driver's mobile app has lost data connectivity
but has not been marked offline. The geospatial index still
shows the last known position from 90 seconds ago.

**Diagnostic:**
```bash
# Check Redis key TTL for driver location
redis-cli TTL "driver_cell:driver_123"
# < 0 = key expired (driver offline)
# > 20 = location still fresh
# Check last update timestamp from driver app logs
grep "driver_id=driver_123" /var/log/location-ingest.log   | tail -5
```

**Fix:**

BAD: Assume driver is online if the key exists (no TTL).
GOOD: Set 30-second TTL on every location key. If TTL expires,
driver is automatically considered unavailable. Only refresh
TTL on incoming location update.

**Prevention:** Client-side dead reckoning (extrapolate position
from last known velocity); alert on drivers with > 30s since
last location update; exclude stale-location drivers from
matching pool.

---

**Failure Mode 2: Geospatial index shard hotspot**

**Symptom:** One Redis shard is at 100% CPU during peak hours.
Location update latency spikes for one geographic area. Driver
matches in that area have 5+ second delays.

**Root Cause:** A city's downtown area (high driver density) maps
to a small number of H3 cells, all assigned to the same shard.
All updates and queries for the busiest area hit one instance.

**Diagnostic:**
```bash
# Check per-shard command rate
redis-cli -h shard-03 info stats | grep instantaneous_ops
# Compare across shards; one at 10x others = hotspot
# Identify which H3 cells are on hot shard
redis-cli -h shard-03 scan 0 match "drivers:*" count 1000
```

**Fix:**

BAD: Shard by H3 cell ID modulo N (geographic hotspots stay
on the same shard).
GOOD: Shard by consistent hash of H3 cell ID with virtual
nodes; periodically rebalance hot cells to under-loaded shards.

**Prevention:** Monitor per-shard command rate; pre-analyse
geographic density for each city and pre-balance accordingly;
use Redis Cluster with automatic slot rebalancing.

---

**Failure Mode 3: Matching engine deadlock under surge**

**Symptom:** During surge events, ride assignments stop for
60-90 seconds. Riders see "Finding your driver..." indefinitely.
Driver app shows "Waiting for requests" despite nearby riders.

**Root Cause:** The batch matching engine holds a write lock on
the driver state store for the full duration of the optimisation
solve (2-3 seconds). Location update writes block on the same
lock, causing a deadlock across services.

**Diagnostic:**
```bash
# Check matching engine lock contention
grep "lock_wait_ms" /var/log/matching-engine.log   | awk '{print $NF}' | sort -n | tail -20
# Values > 1000ms indicate lock contention
```

**Fix:**

BAD: Single global write lock across matching + location update.
GOOD: Separate driver state (available/busy) from location data.
Match on a snapshot of state (read at batch start). Update state
atomically via CAS (compare-and-swap) after match assignment.
Location updates never block on matching lock.

**Prevention:** Measure lock wait time in matching engine; design
matching to operate on a snapshot, not live data; use region-
partitioned matching to reduce contention scope.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-023 - Geo-Replication]] - location data requires
  geographically distributed storage and indexing to serve
  drivers and riders in any region

**Builds On This (learn these next):**
- [[SYD-048 - Chat System Design]] - in-app messaging between
  driver and rider during the trip
- [[SYD-047 - Notification System Design]] - trip status and
  driver arrival push notifications
- [[SYD-027 - Capacity Planning]] - capacity planning for
  geospatial query load at peak demand events

**Alternatives / Comparisons:**
- [[SYD-048 - Chat System Design]] - contrasting real-time
  design (bidirectional messaging vs location-based matching)
- [[SYD-047 - Notification System Design]] - complementary
  notification layer for trip lifecycle events

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------------+
| WHAT IT IS  | Real-time geospatial matching of riders     |
|             | to drivers in a two-sided marketplace       |
+-----------------------------------------------------------+
| PROBLEM     | Driver locations change constantly; radius  |
|             | queries on relational tables don't scale    |
+-----------------------------------------------------------+
| KEY INSIGHT | Index by geography (H3 cells), not by       |
|             | driver ID; match in batch, not greedy       |
+-----------------------------------------------------------+
| USE WHEN    | Building a location-based matching system   |
|             | with thousands of moving entities           |
+-----------------------------------------------------------+
| AVOID WHEN  | Static assets (use regular geo search);     |
|             | < 1K active drivers (relational is fine)    |
+-----------------------------------------------------------+
| TRADE-OFF   | Geospatial index complexity vs O(1)         |
|             | proximity queries at any scale              |
+-----------------------------------------------------------+
| ONE-LINER   | Stream locations into geo index; batch-     |
|             | match globally; surge-price per cell        |
+-----------------------------------------------------------+
| NEXT EXPLORE| Notification System Design (SYD-047)       |
+-----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Geospatial indexes (H3/S2/QuadTree) not relational lat/lon.
2. Batch matching (global optimisation) beats greedy nearest.
3. Surge pricing is a supply incentive signal, not just pricing.

**Interview one-liner:** "Ride-sharing systems maintain a live
geospatial index of driver locations (refreshed every 4 seconds),
run batch matching optimisation every 500ms, and compute per-cell
surge pricing from real-time supply-demand ratios."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Index data by the dimension you query most. Traditional relational
databases cannot efficiently answer "find all entities within 500m"
at high update rates. Geospatial indexes answer proximity queries
in O(log n). This principle applies whenever the primary query
dimension differs from the natural identity dimension of the data.

**Where else this pattern appears:**
- **Time-series databases:** InfluxDB and TimescaleDB index data
  by time first - the primary query dimension. Non-time-indexed
  databases perform full scans for time-range queries.
- **Log search:** Elasticsearch indexes by token (the query
  dimension) not by log line number - enabling sub-second full-
  text search across billions of log entries.
- **Recommendation systems:** User-item matrices indexed by user
  ID for fast recommendation lookup - indexed by the query
  dimension (who is asking), not the item dimension (what exists).

---

### 💡 The Surprising Truth

Uber's early matching system was trivially simple: find the
nearest available driver and assign them. As Uber scaled, they
discovered that nearest-driver matching produced globally
suboptimal outcomes - it would match a rider to a driver 2
minutes away while a driver 4 minutes away was positioned to
serve 5 future riders the system could predict. The matching
problem evolved from a greedy local optimisation to a batched
global optimisation running at 500ms intervals - assigning
multiple riders to multiple drivers simultaneously for the
globally minimum expected wait time. The upgrade from greedy to
batch optimisation increased driver earnings by 15% without
adding a single new driver to the platform. The same supply
became 15% more valuable through smarter allocation alone.

---

### 🧠 Think About This Before We Continue

**Q1.** Should dispatch optimise primarily for ETA, driver
fairness, or marketplace efficiency?

*Hint:* Think about the tension between ETA (user experience),
driver fairness (equal work distribution), and marketplace
efficiency (maximise completed trips per driver-hour). Explore
whether a single objective function can capture all three or
whether multi-objective optimisation with weights is necessary
and how product metrics determine the weights.

**Q2.** How would you reduce incorrect matches caused by stale
driver location updates?

*Hint:* Think about what stale location means for matching: if
a driver's last known location is 30 seconds old, where are they
now? Explore whether you can predict the driver's current
position from their last known velocity and heading (dead
reckoning) and what threshold of staleness makes a match
incorrect enough to warrant exclusion.

**Q3 (Scale):** During New Year's Eve, demand spikes 10x and
driver supply remains flat. Surge pricing activates. Design the
surge pricing algorithm such that it increases supply (incentivises
drivers to come online) without causing rider churn (pricing out
most users).

*Hint:* Think about surge pricing as a two-sided marketplace
signal that must simultaneously incentivise supply and rationally
ration demand. Explore whether a capped surge multiplier
(1.0-2.5x) vs uncapped surge better balances the dual objective,
and how real-time measurement of driver-online response to surge
would inform the algorithm's feedback loop.
