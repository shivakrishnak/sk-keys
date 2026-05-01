---
layout: default
title: "Capacity Planning"
parent: "System Design"
nav_order: 702
permalink: /system-design/capacity-planning/
number: "702"
category: System Design
difficulty: ★★★
depends_on: "Back-of-Envelope Estimation, Horizontal Scaling, Vertical Scaling"
used_by: "Auto Scaling, Rate Limiting (System), Sharding (System)"
tags: #advanced, #architecture, #distributed, #reliability, #performance
---

# 702 — Capacity Planning

`#advanced` `#architecture` `#distributed` `#reliability` `#performance`

⚡ TL;DR — **Capacity Planning** is the process of forecasting future resource needs (CPU, memory, storage, network) and provisioning infrastructure before demand exceeds supply, preventing outages from under-provisioning or waste from over-provisioning.

| #702            | Category: System Design                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Back-of-Envelope Estimation, Horizontal Scaling, Vertical Scaling |                 |
| **Used by:**    | Auto Scaling, Rate Limiting (System), Sharding (System)           |                 |

---

### 📘 Textbook Definition

**Capacity Planning** is a systematic, ongoing process of measuring current resource utilisation, forecasting future demand based on growth trends and anticipated events, and provisioning infrastructure to maintain target performance SLAs with appropriate headroom. It combines historical metrics analysis, demand forecasting (linear regression, seasonal models, event-based projections), resource modelling (how throughput scales with each resource dimension), and procurement or auto-scaling strategy. Effective capacity planning operates on multiple time horizons: short-term (days/weeks: auto-scaling decisions), medium-term (months: infrastructure procurement), and long-term (years: data centre capacity, technology migrations). Key metrics: utilisation percentage (CPU, memory, disk, network), saturation (queue depth, pending connections), and error rate correlated with load.

---

### 🟢 Simple Definition (Easy)

Capacity Planning: figuring out how many servers, how much storage, how much bandwidth you'll need — before you run out. Like a restaurant owner deciding how many chairs, tables, and kitchen staff they'll need for Friday night rush before it happens (not after customers are turned away).

---

### 🔵 Simple Definition (Elaborated)

You're running a video platform. Current: 1 million users, 100 servers. Growing at 20% per month. In 6 months: 1M × 1.2^6 = ~3 million users. At same ratio: ~300 servers needed. But procurement takes 3 months. So today, you order servers for 6 months from now — not for today. Capacity planning is proactive: order/provision before you need it. Add safety margin: order for 400 servers (1.3× safety factor) because growth forecasts are imprecise. Now you won't scramble during a traffic spike.

---

### 🔩 First Principles Explanation

**Capacity planning framework:**

```
CAPACITY PLANNING DIMENSIONS:

  1. CPU:
     Current: avg CPU utilisation = 40% across fleet
     Target ceiling: 70% (leave 30% headroom for spikes)
     Safety threshold: if avg > 60% → provision more capacity (10% lead time buffer)
     Calculation:
       Current load: 40 servers at 40% CPU = 16 server-equivalents of work
       If growth doubles: need 32 server-equivalents
       At 70% max utilisation: 32 / 0.70 = 46 servers needed
       Add 1.2× safety margin: 46 × 1.2 = ~56 servers for 2× growth

  2. MEMORY:
     Memory is not easily auto-scalable (fixed per instance type).
     Monitor: heap usage, GC frequency, OOM events.
     Rule: if p99 memory usage > 80%, provision larger instances or more instances.
     Key: Java apps with heap near limit → GC pressure → latency spikes BEFORE OOM.
     Capacity signal: GC pause > 200ms → memory insufficient (not just "memory full").

  3. STORAGE:
     Most predictable dimension (linear growth).
     Measure: daily growth rate (GB/day).
     Project: current_capacity / daily_growth = days_until_full
     Alert: when < 60 days until full (procurement lead time + safety buffer).

     Example:
       Current: 50 TB used, 100 TB total. Daily growth: 500 GB/day.
       Days until full: (100TB - 50TB) / 500GB = 50,000 GB / 500 GB = 100 days.
       Alert threshold: 60 days → alert triggers in 40 days.
       Action: order additional 100 TB → delivered in 30 days → buffer of 30 days.

  4. NETWORK:
     Measure: peak bandwidth utilisation (not average).
     Limit: 80% of NIC capacity (headroom for bursts).
     Typical: 10 GbE NIC → max 10 Gbps → capacity ceiling: 8 Gbps.
     Calculation: if peak = 7 Gbps → 7/8 = 87.5% → approaching limit → upgrade NIC or add servers.

FORECASTING MODELS:

  LINEAR GROWTH:
    next_month_users = current_users + monthly_addition
    Simple, works for stable mature businesses.

  EXPONENTIAL GROWTH:
    next_month_users = current_users × growth_rate
    Works for startup/hypergrowth phases.
    Dangerous: 20%/month × 12 months = 7.9× growth → underestimate leads to outage.

  SEASONAL MODELS:
    E-commerce: 10× traffic on Black Friday vs. average.
    Tax software: spike in April.
    Gaming: spike on holiday breaks.
    Solution: pre-provision peak capacity 2 weeks before known seasonal events.

  EVENT-BASED:
    Marketing campaign launch: forecast spike based on campaign reach × conversion rate.
    Sports events (streaming): spike at scheduled game time.
    Social features: viral post → unpredictable spike (impossible to pre-provision → auto-scale).

UTILISATION TARGETS BY RESOURCE TYPE:

  Resource      │ Target Avg │ Alert Threshold │ Hard Limit
  ──────────────┼────────────┼─────────────────┼───────────
  CPU           │ 40-50%     │ 70%             │ 90%
  Memory        │ 60%        │ 80%             │ 95%
  Disk          │ 60%        │ 80%             │ 90%
  Network       │ 50%        │ 70%             │ 85%
  DB connections│ 40%        │ 70%             │ 90%

CAPACITY HEADROOM FORMULA:

  headroom_factor = 1 / (1 - target_utilisation)

  At 70% target: headroom = 1 / (1 - 0.70) = 3.33×
  → If current load is 1000 RPS, provision for 3,330 RPS
  → You can absorb a 3.33× spike before hitting limits

  At 50% target: headroom = 1 / 0.5 = 2×
  → More comfortable but more expensive (50% of capacity sitting idle)

  Balance: critical services = 50% target (2× headroom);
           cost-sensitive services = 70% target (1.43× headroom)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Capacity Planning:

- Reactive: provision after outage (too late)
- Procurement takes weeks/months → outage lasts until new hardware arrives
- Over-provisioned systems from "just in case" purchases waste budget

WITH Capacity Planning:
→ Proactive provisioning: new capacity ready before demand peaks
→ Data-driven: growth trends from metrics, not gut feel
→ Cost optimisation: right-size instead of over-provisioning

---

### 🧠 Mental Model / Analogy

> A city water utility predicts next year's population, models water consumption per household, and builds reservoir capacity 2 years before the projected shortfall. They don't wait until taps run dry. They plan based on building permits issued (growth signals), seasonal consumption models (summer peak), and safety reserve (drought years). They over-provision slightly — empty reservoir space is cheap compared to a water crisis.

"Water utility reservoir" = infrastructure capacity (CPU, storage, servers)
"Population growth + building permits" = user growth metrics + growth signals
"Seasonal summer peak" = known traffic seasonality (Black Friday, tax season)
"Drought year safety reserve" = capacity headroom (20-50% idle always reserved)
"2-year lead time to build reservoir" = infrastructure procurement and deployment timelines

---

### ⚙️ How It Works (Mechanism)

**Capacity planning workflow:**

```
STEP 1: INSTRUMENT (measure everything)

  Metrics to collect:
  - Request rate (RPS/QPS) — p50, p95, p99, peak
  - Latency — p50, p95, p99 (not just averages)
  - Error rate (4xx, 5xx)
  - CPU utilisation (per instance, per service)
  - Memory utilisation + GC metrics (Java/JVM)
  - Disk usage + daily growth rate
  - Network bandwidth (in + out)
  - Database: connections in use, query latency, lock waits
  - Cache: hit rate, miss rate, eviction rate

STEP 2: ESTABLISH BASELINES

  Calculate: average, p95, and peak for each metric over 90 days.
  Identify: weekly seasonality (Monday traffic > Saturday).
  Identify: daily pattern (9 AM peak, 3 AM trough).
  Separate: organic growth trend from seasonal variation.

STEP 3: FORECAST DEMAND

  # Python: simple linear growth forecast
  import numpy as np

  # Historical RPS (last 90 days):
  rps_history = [1000, 1050, 1100, 1150, 1200, ...]  # 90 data points

  # Fit linear trend:
  days = np.arange(len(rps_history))
  slope, intercept = np.polyfit(days, rps_history, 1)

  # Forecast 90 days ahead:
  future_days = np.arange(len(rps_history), len(rps_history) + 90)
  forecast_rps = slope * future_days + intercept

  # Add seasonal adjustment:
  # (multiply by day-of-week factor from historical data)
  # Add 1.3× safety margin:
  capacity_target_rps = forecast_rps * 1.3

STEP 4: MODEL RESOURCE REQUIREMENTS

  Current: 1,200 RPS handled by 10 servers
  Efficiency: 120 RPS per server
  Forecast: 2,400 RPS in 6 months
  Required servers: 2,400 / 120 = 20 servers
  With headroom: 20 / 0.70 = 29 servers
  Add safety: 29 × 1.1 = ~32 servers

  Order: 22 additional servers (to go from 10 to 32)
  Lead time: 8 weeks → order in 4 months (6 months - 2 months lead time - safety buffer)

STEP 5: TRIGGER ALERTS + ACTIONS

  Capacity Alert Ladder:
  ┌──────────────────────────────────────────────────────┐
  │ GREEN   │ All resources < 50% utilisation          │
  │ YELLOW  │ Any resource 50-70%: review growth trend  │
  │ ORANGE  │ Any resource 70-80%: initiate procurement │
  │ RED     │ Any resource > 80%: trigger auto-scale    │
  │ CRITICAL│ Any resource > 90%: emergency procedures  │
  └──────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
Observability (metrics collection)
        │
        ▼
Back-of-Envelope Estimation (demand forecasting)
        │
        ▼
Capacity Planning ◄──── (you are here)
(provision before peak demand)
        │
        ├── Auto Scaling (short-term: automated)
        ├── Sharding (storage capacity exceeded)
        └── Rate Limiting (protect capacity ceiling)
```

---

### 💻 Code Example

**Spring Boot Actuator: capacity monitoring metrics endpoint:**

```java
@Component
public class CapacityMetrics {

    private final MeterRegistry meterRegistry;

    // Track request rate:
    @EventListener
    public void onRequest(RequestEvent event) {
        meterRegistry.counter("http.requests.total",
            "endpoint", event.getEndpoint(),
            "status", String.valueOf(event.getStatus())
        ).increment();
    }

    // Track DB connection pool utilisation (capacity signal):
    @Scheduled(fixedDelay = 10_000)
    public void recordDbPoolMetrics() {
        HikariPoolMXBean pool = getHikariPool();

        double utilisation = (double) pool.getActiveConnections()
                           / pool.getTotalConnections();

        meterRegistry.gauge("db.pool.utilisation", utilisation);

        // Alert if > 70%:
        if (utilisation > 0.70) {
            log.warn("DB pool utilisation at {}% — capacity review needed",
                String.format("%.0f", utilisation * 100));
        }
    }

    // Track heap memory as % of max:
    @Scheduled(fixedDelay = 30_000)
    public void recordMemoryMetrics() {
        MemoryMXBean memBean = ManagementFactory.getMemoryMXBean();
        long used = memBean.getHeapMemoryUsage().getUsed();
        long max  = memBean.getHeapMemoryUsage().getMax();

        double heapUtilisation = (double) used / max;
        meterRegistry.gauge("jvm.heap.utilisation", heapUtilisation);

        if (heapUtilisation > 0.80) {
            log.warn("Heap at {}% — OOM risk — scale up memory",
                String.format("%.0f", heapUtilisation * 100));
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Auto-scaling eliminates the need for capacity planning        | Auto-scaling handles short-term elasticity (minutes to hours), but can't solve procurement of physical hardware, data centre space, network capacity, or licensing. Capacity planning governs the ceiling that auto-scaling operates within. Auto-scaling without capacity planning means the ceiling is unknown |
| Capacity planning is about provisioning more hardware         | Modern capacity planning is equally about right-sizing (removing over-provisioned resources), identifying bottlenecks in architecture (not just hardware), and optimising code efficiency. Sometimes the right answer is "rewrite the inefficient query" rather than "buy 50 more servers"                       |
| Average utilisation is the right metric for capacity planning | Peak utilisation determines capacity needs, not average. A service averaging 30% CPU with 10-minute spikes to 95% will experience outages — the 95% peak is what matters for capacity planning. Always measure and plan for p99 peak, not average                                                                |
| Capacity planning is a one-time activity (done at launch)     | Capacity planning is a continuous process. Growth, feature changes, traffic patterns, and infrastructure efficiency all change over time. Leading engineering teams review capacity weekly/monthly and forecast rolling 6-12 months ahead                                                                        |

---

### 🔥 Pitfalls in Production

**Forgetting database connection pools during scaling:**

```
PROBLEM: Scale app servers, forget DB connection pool

  Before scaling:
    20 app servers × 50 connections each = 1,000 connections to DB
    DB max_connections = 1,200 (set in PostgreSQL config)
    Utilisation: 1,000 / 1,200 = 83% (already near limit)

  Auto-scaling event: traffic spike → scales to 40 app servers
    40 × 50 connections = 2,000 connections needed
    DB limit: 1,200
    Result: 800 new connections REFUSED by database
    App: "too many connections" errors on all endpoints

  FIX: pgBouncer (connection pooler) between app and DB
    pgBouncer: multiplexes 2,000 app connections → 200 actual DB connections
    Capacity planning MUST include ALL tiers, not just app servers.

  REVISED CAPACITY PLAN includes:
    - App servers (CPU, memory)
    - Database connections (require connection pooler if >500 app instances)
    - Database IOPS (SSD IOPS limit; AWS RDS has per-instance IOPS limits)
    - Network bandwidth (between tiers: app→DB, app→cache, app→message queue)
    - Cache memory (Redis: if capacity exceeded, eviction → cache miss spike)
```

---

### 🔗 Related Keywords

- `Back-of-Envelope Estimation` — initial estimation technique that feeds capacity planning
- `Auto Scaling` — short-term automated capacity response within pre-planned limits
- `Horizontal Scaling` — capacity expansion by adding more servers
- `Vertical Scaling` — capacity expansion by upgrading server size
- `Rate Limiting (System)` — protects systems from exceeding provisioned capacity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Forecast resource needs and provision     │
│              │ before demand exceeds supply              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ 3-12 month infrastructure forecasting;    │
│              │ known seasonal events; hypergrowth phases │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Planning for averages (plan for peaks);   │
│              │ treating auto-scaling as a full substitute│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Water utility builds reservoir 2 years   │
│              │  before the city needs it."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Auto Scaling → Sharding                   │
│              │ → Rate Limiting                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your SaaS product has 500,000 users growing at 15% per month. Current infrastructure: 20 app servers (each handling 500 RPS peak), 2 database servers (each handling 5,000 QPS peak). Current peak: 8,000 RPS app, 40,000 QPS database. Procurement lead time: 6 weeks. Current utilisation: app servers at 80%, DB servers at 40%. Which resource requires immediate attention? Calculate: how many additional app servers are needed today to bring utilisation to 60%? How many total app servers will you need 6 months from now?

**Q2.** An e-commerce platform has average daily traffic of 50,000 RPS but experiences 500,000 RPS on Black Friday (10× spike, predictable, occurs annually). The platform uses auto-scaling with a maximum scale-out limit of 200 servers. Each server handles 3,000 RPS. Is the maximum auto-scale capacity sufficient for Black Friday? If not, what is the correct approach: increase the auto-scale limit, pre-provision fixed capacity before Black Friday, or refuse the traffic above capacity via rate limiting? What are the trade-offs of each approach?
