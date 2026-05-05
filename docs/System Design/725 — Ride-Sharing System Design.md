---
layout: default
title: "Ride-Sharing System Design"
parent: "System Design"
nav_order: 725
permalink: /system-design/ride-sharing-system-design/
number: "0725"
category: System Design
difficulty: ★★★
depends_on: Geo-Replication, Matching Systems, Real-Time Updates
used_by: Mobility Platforms, Dispatch Systems, Real-Time Marketplaces
related: Chat System Design, Notification System Design, Capacity Planning
tags:
  - system-design
  - marketplace
  - realtime
  - advanced
  - geo
---

# 725 — Ride-Sharing System Design

⚡ TL;DR — Ride-sharing systems match riders and drivers in real time while tracking location, ETA, pricing, trip state, and payment. The hard parts are geo indexing, dispatch latency, surge logic, and correctness under rapid driver movement.

| #725            | Category: System Design                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Geo-Replication, Matching Systems, Real-Time Updates              |                 |
| **Used by:**    | Mobility Platforms, Dispatch Systems, Real-Time Marketplaces      |                 |
| **Related:**    | Chat System Design, Notification System Design, Capacity Planning |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Riders need nearby drivers fast, while drivers move continuously and supply-demand conditions change by area.

**SOLUTION:**
Keep fresh location state, index by geography, and run dispatch logic near real time.

---

### 📘 Textbook Definition

**Ride-Sharing System Design:** System design problem involving location ingestion, dispatch matching, trip lifecycle management, pricing, and payment for a real-time two-sided marketplace.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Track drivers, find the best nearby one, manage the trip lifecycle, and keep both parties updated.

**One analogy:**

> A taxi dispatcher with a live city map, but scaled to millions of riders and drivers with automated pricing and routing.

**One insight:**
This is not just maps plus payments; it is a real-time supply-demand coordination system.

---

### 🧠 Mental Model

```
driver locations -> geo index -> dispatch engine -> rider app / driver app -> trip state machine
```

---

### 📶 Gradual Depth

**Level 1:** Find a nearby driver and start a trip.

**Level 2:** Continuously update locations and ETAs.

**Level 3:** Use geo cells, dispatch scoring, trip state transitions, and async pricing/payment workflows.

**Level 4:** The core system is a high-frequency location stream feeding a matching engine that must stay both fast and fair under local market imbalance.

---

### ⚙️ How It Works

```
1. Drivers publish location every few seconds
2. System writes latest position into geo index
3. Rider requests trip
4. Dispatch engine finds candidate drivers nearby
5. Score candidates by ETA, acceptance likelihood, market rules
6. Offer trip, confirm acceptance, create trip state
7. Track progress through pickup, ride, completion, payment
```

---

### 💻 Code Example

```python
def score_driver(driver, rider_request):
    distance_penalty = driver["eta_seconds"]
    acceptance_bonus = driver.get("acceptance_rate", 0.8) * -30
    return distance_penalty + acceptance_bonus


drivers = [
    {"id": 1, "eta_seconds": 120, "acceptance_rate": 0.95},
    {"id": 2, "eta_seconds": 90, "acceptance_rate": 0.60},
]

best = min(drivers, key=lambda d: score_driver(d, {}))
print(best)
```

---

### ⚖️ Comparison Table

| Concern              | Common answer              |
| -------------------- | -------------------------- |
| Nearby lookup        | geo index / geohash        |
| Dispatch speed       | in-memory candidate search |
| State changes        | trip state machine         |
| Rider/driver updates | sockets + push fallback    |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                          |
| ----------------------------------------------------- | ---------------------------------------------------------------- |
| "Nearest driver is always best"                       | Acceptance rate, traffic, and market balancing also matter.      |
| "Location data can be strongly consistent everywhere" | Fresh-enough local accuracy matters more than global perfection. |

---

### 🚨 Failure Modes

**Failure Mode 1: Stale driver locations**

**Symptom:**
System repeatedly assigns drivers who are no longer nearby.

**Prevention:**
Short TTL on location state, freshness scoring, rapid update ingestion.

---

**Failure Mode 2: Dispatch thrash**

**Symptom:**
Same trip bounces among drivers with repeated accept/timeout cycles.

**Prevention:**
Reservation windows, acceptance timeouts, candidate ranking with suppression rules.

---

### 📌 Quick Reference

```
Ride-sharing design:
  ingest live locations
  maintain geo index
  dispatch nearby candidates fast
  manage trip lifecycle and payment asynchronously
```

---

### 🧠 Questions

**Q1.** Should dispatch optimize primarily for ETA, driver fairness, or marketplace efficiency?

**Q2.** How would you reduce incorrect matches caused by stale location updates?
