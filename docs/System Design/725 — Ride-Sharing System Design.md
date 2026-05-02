---
layout: default
title: "Ride-Sharing System Design"
parent: "System Design"
nav_order: 725
permalink: /system-design/ride-sharing-system-design/
number: "725"
category: System Design
difficulty: ★★★
depends_on: "Geospatial Indexing, WebSockets, Consistent Hashing"
used_by: "System Design Interview"
tags: #advanced, #system-design, #interview, #geospatial, #real-time
---

# 725 — Ride-Sharing System Design

`#advanced` `#system-design` `#interview` `#geospatial` `#real-time`

⚡ TL;DR — **Ride-Sharing System Design** matches riders to nearby drivers using geospatial indexing (Geohash/H3), broadcasts real-time location via WebSockets, and orchestrates the ride lifecycle (request → match → trip → payment) through an event-driven state machine.

| #725            | Category: System Design                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Geospatial Indexing, WebSockets, Consistent Hashing |                 |
| **Used by:**    | System Design Interview                             |                 |

---

### 📘 Textbook Definition

A **Ride-Sharing System** (e.g., Uber, Lyft, Grab) connects passengers requesting transportation with available drivers, processes real-time location updates, performs proximity matching, and manages a complete ride lifecycle from request to payment. Key technical challenges include: (1) **location ingestion** — processing millions of driver GPS updates per second efficiently; (2) **proximity search** — finding available drivers within N kilometres of a rider in sub-second time; (3) **driver matching** — selecting the optimal driver from candidates (ETA, price, driver rating); (4) **real-time tracking** — streaming live driver location to rider app during trip; (5) **surge pricing** — dynamic pricing based on supply/demand imbalance in geographic areas; (6) **ride state machine** — managing state transitions (REQUESTED → MATCHED → DRIVER_ARRIVING → IN_TRIP → COMPLETED → PAID) reliably with failure recovery. Reference systems: Uber H3 hexagonal geospatial indexing, Lyft's real-time location pipeline.

---

### 🟢 Simple Definition (Easy)

Ride-Sharing: you request a ride → the system finds nearby available drivers (using a map grid to search quickly) → picks the best match → both driver's and rider's apps show real-time location via a live connection (WebSocket). The entire ride is a state machine: "waiting for driver" → "driver on the way" → "in ride" → "completed" → "payment processed." Every 5 seconds, the driver's phone sends its GPS coordinates to the server.

---

### 🔵 Simple Definition (Elaborated)

Uber at scale: 5 million daily rides, millions of drivers sending GPS every 5 seconds. Challenge: "Find all available drivers within 3km of this rider" — executed millions of times per hour. Solution: divide the world map into Geohash grid cells. Store active driver locations in Redis: {geohash → set of driver_ids}. Query: "Find drivers in cells within 3km radius" = lookup 9 adjacent Geohash cells → get driver_ids → filter available → rank by ETA. Matching: assign best driver → both apps connect via WebSocket for real-time tracking until ride ends.

---

### 🔩 First Principles Explanation

**Ride-sharing system: location pipeline, geospatial matching, and ride state machine:**

```
GEOSPATIAL INDEXING:

  Problem: "Find all available drivers within 3km of (37.7749, -122.4194)"

  Naive: store driver locations in DB. Query: SELECT driver_id WHERE distance(lat,lng, 37.77, -122.41) < 3km
  Problem: distance function on every row = full table scan. 5M drivers = unacceptable.

  GEOHASH:
    Earth divided into rectangular cells at various precision levels.
    Precision 6: cell size ~1.2km × 0.6km (600m × 1200m). Good for driver search.
    Precision 5: cell size ~4.9km × 4.9km. Larger search area.

    (37.7749, -122.4194) → Geohash = "9q8yy"
    All points in the same Geohash share the same prefix.
    Nearby cells: 9q8yy's 8 adjacent cells (N, NE, E, SE, S, SW, W, NW).

    Driver search:
    1. Compute rider's Geohash at precision 6: "9q8yy"
    2. Get 8 adjacent cells: ["9q8yz", "9q8yu", "9q8yv", ...]
    3. Search Redis: SUNION drivers:9q8yy drivers:9q8yz drivers:9q8yu ... (9 cells)
    4. Result: all driver_ids in ~3×3km area → filter available → rank by ETA

    Limitation: cells are rectangles (not circles) → some false positives near borders.
    Fix: secondary filter: compute exact distance for candidate set (< 100 drivers) → O(n) where n is small.

  H3 (Uber's hexagonal indexing):
    Hexagons instead of rectangles: more uniform distance to all neighbours.
    H3 resolution 7: cell area ~5.16 km². Resolution 9: ~0.105 km².

    Advantages over Geohash: no edge distortion at poles, uniform shape,
                              clean API for area arithmetic.

    Uber uses H3 for: driver search, surge pricing zones, heat maps.

LOCATION INGESTION PIPELINE:

  Volume: 5M active drivers × 1 GPS update/5 seconds = 1M location updates/second (peak).

  Flow:
    Driver's phone → GPS update (lat, lng, timestamp, driver_id, availability)
    → WebSocket/gRPC to Location Update Service
    → Kafka "driver.locations" topic
    → Location Worker consumes → updates Redis:

      // Remove from old Geohash bucket:
      SREM drivers:{old_geohash} {driver_id}

      // Add to new Geohash bucket:
      SADD drivers:{new_geohash} {driver_id}

      // Store driver's current location:
      HSET driver:{driver_id} lat {lat} lng {lng} status {AVAILABLE} updated_at {ts}

  Redis SADD: O(1) per driver per update → 1M updates/second = manageable.
  Redis memory: 5M drivers × 100 bytes = 500MB → fits in one Redis instance.

  Why Kafka between Location Service and Redis?
    Decouples ingestion (burst tolerant) from processing.
    Location Service: accepts 1M updates/second without dropping.
    Redis workers: consume at Redis's max write speed, not GPS burst speed.
    Re-playable: if Redis fails, replay from Kafka offset.

DRIVER MATCHING:

  Rider requests ride at location R:

  1. Find candidate drivers:
     geohash = geohash(R, precision=6)
     adj_cells = [geohash] + get_neighbors(geohash)
     driver_ids = SUNION drivers:{cell} for each cell in adj_cells
     Filter: only AVAILABLE drivers

  2. Score candidates (pick top 10 for ETA calculation):
     Rough filter: Euclidean distance (fast) → keep closest 20 drivers
     ETA calculation: call routing service (OSRM, Google Maps) for top 20 → real road ETA

  3. Select best driver:
     Primary: lowest ETA (rider wants driver to arrive fastest)
     Secondary: driver rating (tie-breaking)
     Business rules: prefer electric vehicles if requested; surge eligibility

  4. OFFER to driver (not force-assign):
     Send offer: "Ride request from X, ETA 4 min, fare estimate $12"
     Wait for driver acceptance: 15 seconds timeout
     If no response / decline: try next driver in ranked list

     Offer sent via: WebSocket push notification to driver app

  5. On driver acceptance:
     Update ride: status = MATCHED, driver_id = selected_driver
     Update driver: status = BUSY (remove from available pool)
     Notify rider: "Driver John is on the way, 4 min away"

RIDE STATE MACHINE:

  States and transitions:

  RIDER_REQUESTED
      │ (driver accepts offer)
      ▼
  DRIVER_MATCHED
      │ (driver starts navigation to pickup)
      ▼
  DRIVER_ARRIVING
      │ (driver reaches pickup ± 50m, taps "arrived")
      ▼
  DRIVER_ARRIVED (waiting for rider)
      │ (rider enters car, driver taps "start trip")
      ▼
  IN_TRIP
      │ (driver reaches destination ± 50m, taps "end trip")
      ▼
  TRIP_COMPLETED
      │ (payment processed)
      ▼
  RIDE_PAID

  Failure modes and recovery:
    DRIVER_MATCHED → driver app crashes → no update for 60s → timeout → re-match
    IN_TRIP → server restart → restore from persistent state (MySQL/DynamoDB)
    TRIP_COMPLETED → payment fails → retry payment; ride stays COMPLETED until paid

  State persistence: MySQL (authoritative), Redis (cache for active rides).
  State machine enforced: service validates: can DRIVER_ARRIVING → IN_TRIP? No. Must go via DRIVER_ARRIVED.

REAL-TIME TRACKING (driver location → rider app during trip):

  High-frequency updates needed: driver moves every 2 seconds → rider sees smooth animation.

  Architecture:
    Driver app → location update → Location Service → Redis (driver:{driver_id} lat/lng)
    Rider app → WebSocket → Chat/Tracking Server → polls Redis every 2s → pushes to rider WebSocket

  OR (more efficient):
    Driver app → WebSocket → Location Service → Kafka → Tracking Worker → WebSocket to rider app
    Pure push: no polling. Driver location change → immediate push to rider.

  What data the rider sees:
    Driver: {lat, lng, bearing} every 2 seconds
    Client-side: smooth animation (interpolate between GPS points for fluid map movement)

SURGE PRICING:

  Supply/demand imbalance → price multiplier.

  Data:
    Available drivers per Geohash cell.
    Pending ride requests per Geohash cell.
    ratio = pending_requests / available_drivers per cell.

    ratio < 0.5: no surge
    ratio 0.5–1.0: 1.2× surge
    ratio 1.0–2.0: 1.5× surge
    ratio > 2.0: 2.0× surge

  Computed: every 60 seconds via batch job (Spark or Flink stream processing).
  Stored: Redis hash {geohash → surge_multiplier}.
  Displayed: rider sees surge multiplier before confirming ride.
  Legal: many jurisdictions require showing surge clearly before booking.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT ride-sharing architecture:

- Geospatial queries via SQL DISTANCE: full table scan on 5M drivers = seconds per query
- No real-time tracking: rider doesn't know where driver is (polling every 30s = outdated)
- No state machine: rides can get stuck in invalid states on failure → manual intervention

WITH ride-sharing architecture:
→ Geohash + Redis: O(1) driver lookup in any geographic area, sub-second matching
→ WebSocket: 2-second location updates push to rider → smooth real-time tracking
→ State machine: deterministic state transitions → automatic recovery from failures

---

### 🧠 Mental Model / Analogy

> A city's taxi dispatch system with a zone map. The city is divided into numbered blocks (Geohash cells). Available taxis are listed on a board under their current block number (Redis: set of drivers per Geohash). When a customer calls: dispatcher checks the board for all taxis in blocks adjacent to the customer's address, calls the nearest ones, connects customer and driver. During the ride: radio updates from the taxi's GPS (location updates) are broadcast to the customer's device (WebSocket push). Meter running = IN_TRIP state. Meter stops = TRIP_COMPLETED.

"Numbered city blocks" = Geohash cells (geographic area divided into addressable cells)
- "Board listing taxis per block" = Redis sets {geohash → driver_ids}
"Dispatcher checks adjacent blocks" = query 9 adjacent Geohash cells for available drivers
"Radio updates during ride" = WebSocket location push every 2 seconds
"Meter running" = IN_TRIP state (state machine)
- "Meter stops → payment" = TRIP_COMPLETED → RIDE_PAID transition

---

### ⚙️ How It Works (Mechanism)

**Driver search using Geohash and Redis:**

```java
@Service
public class DriverSearchService {

    @Autowired private RedisTemplate<String, String> redis;
    @Autowired private DriverRepository driverRepository;
    @Autowired private ETAService etaService;

    public List<DriverCandidate> findNearbyDrivers(double riderLat, double riderLng,
                                                    int radiusKm) {
        // 1. Compute Geohash for rider location (precision 6 = ~1.2km cells):
        String riderGeohash = GeoHashUtils.encode(riderLat, riderLng, 6);

        // 2. Get 8 adjacent cells + rider's cell (9 total):
        List<String> searchCells = new ArrayList<>();
        searchCells.add(riderGeohash);
        searchCells.addAll(GeoHashUtils.getNeighbors(riderGeohash));

        // 3. Union all driver IDs in those cells (one Redis SUNION):
        String[] redisKeys = searchCells.stream()
            .map(cell -> "drivers:" + cell)
            .toArray(String[]::new);

        Set<String> candidateDriverIds = redis.opsForSet().union(
            redisKeys[0], Arrays.asList(redisKeys).subList(1, redisKeys.length));

        if (candidateDriverIds == null || candidateDriverIds.isEmpty()) {
            return Collections.emptyList();
        }

        // 4. Fetch driver details (current location, status, rating):
        List<DriverCandidate> candidates = new ArrayList<>();
        for (String driverIdStr : candidateDriverIds) {
            long driverId = Long.parseLong(driverIdStr);
            Map<Object, Object> driverData = redis.opsForHash()
                .entries("driver:" + driverId);

            if (!"AVAILABLE".equals(driverData.get("status"))) continue;

            double driverLat = Double.parseDouble((String) driverData.get("lat"));
            double driverLng = Double.parseDouble((String) driverData.get("lng"));

            // 5. Exact distance filter (Haversine formula):
            double distanceKm = HaversineDistance.calculate(
                riderLat, riderLng, driverLat, driverLng);

            if (distanceKm <= radiusKm) {
                candidates.add(new DriverCandidate(driverId, driverLat, driverLng,
                                                   distanceKm));
            }
        }

        // 6. Sort by distance, take top 10 for ETA calculation:
        candidates.sort(Comparator.comparingDouble(DriverCandidate::getDistanceKm));
        List<DriverCandidate> top10 = candidates.subList(0, Math.min(10, candidates.size()));

        // 7. Compute real road ETA for top 10 (more accurate than Euclidean distance):
        return etaService.enrichWithETA(top10, riderLat, riderLng);
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Rider requests trip (geolocation + time constraint)
        │
        ▼
Ride-Sharing System Design ◄──── (you are here)
(Geohash search + WebSocket tracking + state machine)
        │
        ├── Geospatial Indexing (Geohash/H3 for proximity search)
        ├── WebSockets (real-time location streaming)
        └── Message Queues (Kafka for location update pipeline)
```

---

### 💻 Code Example

**Ride state machine with failure recovery:**

```java
@Service
@Transactional
public class RideStateMachine {

    @Autowired private RideRepository rideRepository;
    @Autowired private DriverRepository driverRepository;

    // Valid state transitions:
    private static final Map<RideStatus, Set<RideStatus>> VALID_TRANSITIONS = Map.of(
        RIDER_REQUESTED,    Set.of(DRIVER_MATCHED, CANCELLED),
        DRIVER_MATCHED,     Set.of(DRIVER_ARRIVING, CANCELLED),
        DRIVER_ARRIVING,    Set.of(DRIVER_ARRIVED, CANCELLED),
        DRIVER_ARRIVED,     Set.of(IN_TRIP, CANCELLED),
        IN_TRIP,            Set.of(TRIP_COMPLETED),
        TRIP_COMPLETED,     Set.of(RIDE_PAID),
        CANCELLED,          Set.of(),  // terminal state
        RIDE_PAID,          Set.of()   // terminal state
    );

    public void transition(long rideId, RideStatus newStatus) {
        Ride ride = rideRepository.findById(rideId)
            .orElseThrow(() -> new RideNotFoundException(rideId));

        // Validate transition:
        if (!VALID_TRANSITIONS.get(ride.getStatus()).contains(newStatus)) {
            throw new InvalidTransitionException(
                "Cannot transition from " + ride.getStatus() + " to " + newStatus);
        }

        // Apply side effects for specific transitions:
        switch (newStatus) {
            case DRIVER_MATCHED -> {
                driverRepository.updateStatus(ride.getDriverId(), DriverStatus.BUSY);
                // Remove driver from available pool (Geohash Redis sets)
                locationService.removeFromAvailablePool(ride.getDriverId());
            }
            case TRIP_COMPLETED -> {
                // Calculate fare (distance × rate × surge multiplier):
                BigDecimal fare = fareCalculator.calculate(
                    ride.getPickupLocation(), ride.getDropoffLocation(),
                    ride.getActualDistanceKm(), ride.getSurgeMultiplier());
                ride.setFinalFare(fare);
                // Trigger async payment processing:
                paymentService.processAsync(rideId, ride.getRiderId(), fare);
            }
            case CANCELLED -> {
                // Release driver back to available pool:
                if (ride.getDriverId() != null) {
                    driverRepository.updateStatus(ride.getDriverId(), DriverStatus.AVAILABLE);
                    locationService.addToAvailablePool(ride.getDriverId());
                }
                // Apply cancellation fee if applicable
            }
        }

        ride.setStatus(newStatus);
        ride.setUpdatedAt(Instant.now());
        rideRepository.save(ride);

        // Notify both parties via WebSocket:
        notificationService.notifyRideStatusChange(ride);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Geohash proximity search is always accurate                       | Geohash search has an edge case: two points very close to each other may be in different Geohash cells (on opposite sides of a cell boundary) with very different hashes. Searching only the rider's cell would miss nearby drivers just across the boundary. Fix: always search the rider's cell + all 8 adjacent cells (9 cells total). This guarantees no false negatives within the search radius                         |
| WebSockets can handle all 5M drivers simultaneously on one server | One server can maintain ~100K WebSocket connections (limited by file descriptors, memory). For 5M concurrent drivers, you need ~50 WebSocket servers. Load balancing must use sticky sessions (same driver always routes to same server, since WebSocket is stateful). Redis pub/sub provides cross-server communication when location updates need to reach riders on different servers                                      |
| Driver matching is a simple nearest-driver algorithm              | Optimal matching is an assignment problem (bipartite matching) balancing: ETA to rider, total system efficiency (minimise total empty miles driven), driver fairness (prevent some drivers getting all rides), rider preferences (car type, accessibility needs), business rules (surge zones, airport queues). Uber uses ML-based matching that optimises across multiple objectives simultaneously, not just nearest-driver |
| Surge pricing is computed in real-time per request                | Computing demand/supply balance per request would be too expensive (aggregating all pending requests and drivers per cell for every ride request). Surge multipliers are computed in batch (every 60 seconds) and cached in Redis per Geohash cell. This means surge pricing has up to 60-second lag, which is acceptable for practical purposes                                                                              |

---

### 🔥 Pitfalls in Production

**Ghost drivers: stale location data showing unavailable drivers as available:**

```
PROBLEM: Driver turns off app but still appears as "available" in Redis

  Driver: active on app, last GPS update at 10:00:00 AM.
  Driver: closes app (phone dies, airplane mode).
  Redis: "driver:456" still has status=AVAILABLE, last location from 10:00:00.

  Rider request at 10:05:00:
  System: finds driver 456 as candidate (within 2km).
  System: sends ride offer to driver 456.
  Driver 456: offline — no response.
  System: waits 15 seconds → no acceptance → tries next driver.
  Result: wasted 15 seconds for rider. Repeated for multiple ghost drivers.

  At scale: 10,000 ghost drivers → significant matching latency + rider frustration.

FIX 1: TTL-BASED AVAILABILITY IN REDIS:
  Store driver availability as Redis key with TTL, not just status field:
    SET driver:available:{driver_id} 1 EX 30  // expires in 30 seconds

  Driver sends GPS update every 5 seconds → refresh TTL.
  Driver goes offline → stops sending updates → key expires after 30s.

  Driver search: check driver:available:{driver_id} EXISTS before including in candidates.
  Ghost driver: key expired → not found → excluded from candidates.

  This is heartbeat-based TTL — same pattern as presence in chat system.

FIX 2: DRIVER HEARTBEAT (separate from GPS):
  Driver app: separate lightweight heartbeat every 5 seconds (tiny payload).
  Server: if heartbeat missed for > 15 seconds → mark driver UNAVAILABLE.

  Why separate from GPS? GPS update may be throttled by phone OS for battery.
  Heartbeat: tiny packet, OS allows it even in background.

FIX 3: OFFER TIMEOUT + AUTOMATIC RE-MATCH:
  Even with ghost driver prevention, set aggressive offer timeout (10-15 seconds).
  No response → automatically move to next candidate.
  Log: "driver 456 did not respond" → signal to investigate ghost driver issue.

  Alert: if same driver misses >3 offers in 30 minutes → deactivate automatically.
```

---

### 🔗 Related Keywords

- `Geospatial Indexing` — Geohash/H3 hexagonal indexing for O(1) proximity driver search
- `WebSockets` — persistent bidirectional connections for real-time location streaming
- `Consistent Hashing` — distributing location update processing across multiple workers
- `State Machine` — ride lifecycle management with valid transition enforcement

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Geohash cells in Redis for driver search; │
│              │ state machine for ride lifecycle          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Real-time proximity matching; location    │
│              │ tracking; event-driven lifecycle mgmt     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-cell Geohash search (miss boundary │
│              │ drivers); stale location without TTL      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "City block taxi board — blocks map to    │
│              │  Geohash; taxis listed by their block;    │
│              │  radio GPS updates in real-time."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Geospatial Indexing → H3 Hexagonal Grid   │
│              │ → Real-time Location Tracking             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Uber operates in 10,000 cities worldwide. Some cities have very high driver density (New York City — thousands of drivers per km²); others have very low density (rural areas — one driver per 50km²). A single Geohash precision level (e.g., precision 6 = ~1.2km cells) works well for NYC but would have empty cells in rural areas (requiring search of many adjacent cells to find any driver). Design an adaptive Geohash precision strategy: how do you determine the right precision level per city (or per area within a city)? What data would you use to make this decision, and how often would you recalculate?

**Q2.** A driver in San Francisco accepts a ride at 10:00 AM. At 10:05 AM (during pickup navigation), the driver's car is involved in a minor accident. The driver cannot complete the ride. Design the failure recovery: (a) how does the system detect that the driver can no longer fulfill the ride (driver closes app, calls support, or sends "cancel" event)? (b) what state transition occurs, and how is the rider notified? (c) how quickly can the rider be re-matched to a new driver? (d) is there any compensation or priority applied to the rider who was left stranded mid-match?
