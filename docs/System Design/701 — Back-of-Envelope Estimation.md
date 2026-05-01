---
layout: default
title: "Back-of-Envelope Estimation"
parent: "System Design"
nav_order: 701
permalink: /system-design/back-of-envelope-estimation/
number: "701"
category: System Design
difficulty: ★★☆
depends_on: "Capacity Planning, Vertical Scaling, Horizontal Scaling"
used_by: "Capacity Planning, Sharding (System)"
tags: #intermediate, #architecture, #foundational, #performance, #distributed
---

# 701 — Back-of-Envelope Estimation

`#intermediate` `#architecture` `#foundational` `#performance` `#distributed`

⚡ TL;DR — **Back-of-Envelope Estimation** is the skill of quickly calculating system scale, storage, and throughput requirements using rough numbers and approximations — essential for system design interviews and capacity planning.

| #701 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Capacity Planning, Vertical Scaling, Horizontal Scaling | |
| **Used by:** | Capacity Planning, Sharding (System) | |

---

### 📘 Textbook Definition

**Back-of-Envelope Estimation** (also called fermi estimation or order-of-magnitude calculation) is a method of quickly deriving approximate answers to complex quantitative questions using simplified assumptions, known constants, and arithmetic rounding. In system design, it is used to estimate: QPS (Queries Per Second), storage requirements, bandwidth, memory, and number of servers needed for a given system. The goal is not precision (within 10%) but rather the correct order of magnitude (within 10×). Key reference numbers used in back-of-envelope calculations include: powers of two for data sizes, latency numbers for different operation types (memory access = nanoseconds, disk = milliseconds, network = milliseconds), and common traffic patterns. This skill is foundational in both system design interviews and production capacity planning.

---

### 🟢 Simple Definition (Easy)

Back-of-Envelope Estimation: quickly calculating "about how many servers / how much storage do we need?" using rough maths. You don't need the exact answer — just the right ballpark. Is it 10 servers or 10,000? 1 TB or 1 PB? These rough estimates guide architecture decisions without needing weeks of modelling.

---

### 🔵 Simple Definition (Elaborated)

Twitter-like system design interview. You need to estimate: daily active users (500M), tweets per day (50M), storage per tweet (300 bytes), 10 years retention. Calculation: 50M tweets/day × 300 bytes = 15 GB/day × 365 × 10 = ~55 TB of tweet text storage. Add media: 10% of tweets have images, average 200 KB = 50M × 10% × 200KB = 1 TB/day media → 3.65 PB over 10 years. Now you know the storage tier is petabytes → object storage (S3), not a single MySQL database. The estimate guided the architecture decision.

---

### 🔩 First Principles Explanation

**The essential reference numbers (memorise these):**

```
LATENCY REFERENCE TABLE (nanoseconds and beyond):

  L1 cache access:              0.5 ns
  L2 cache access:              7 ns
  L3 cache access:              ~30 ns
  Main memory (RAM) access:     100 ns
  Compress 1 KB with Snappy:    3,000 ns  (3 µs)
  Read 1 MB from memory:        250 µs
  Round trip within datacenter: 500 µs
  SSD random read:              100 µs (0.1 ms)
  Read 1 MB from SSD:           1,000 µs (1 ms)
  HDD random read (seek):       10,000 µs (10 ms)
  Read 1 MB from HDD:           20 ms
  Round trip same city:         1 ms
  US → Europe roundtrip:        150 ms
  
  KEY INSIGHT: Memory is 10,000× faster than disk.
               Network disk (object storage) adds 100-200ms.
               In-process cache (RAM): sub-millisecond always.

DATA SIZE REFERENCE:

  Powers of 2:
  2^10 = 1,024 ≈ 1 thousand (K)
  2^20 = 1,048,576 ≈ 1 million (M)
  2^30 ≈ 1 billion (G)
  2^40 ≈ 1 trillion (T)
  
  Character: 1 byte
  English word: 5 bytes average
  URL: ~2,000 characters = 2 KB
  Tweet text: 280 characters = 280 bytes ≈ 300 bytes
  User profile record: ~1 KB
  Small image thumbnail: ~100 KB
  High-res photo (JPEG): 1-5 MB
  Short video (1 min, 720p): ~30 MB
  
  Approximate: always round to nearest power of 10 for simplicity.

TIME REFERENCE:

  Seconds per minute:       60
  Seconds per hour:         3,600  (≈ 3,600)
  Seconds per day:          86,400 ≈ 100,000 (for rough maths)
  Seconds per month:        2.6 million ≈ 3 million
  Seconds per year:         31.5 million ≈ 30 million
  
  TRICK: 10% of day = 86,400 × 0.1 ≈ 10,000 seconds
         If 10M requests/day: 10M / 100,000 = 100 RPS (average)

STANDARD ESTIMATION PROCEDURE:

  1. ESTABLISH SCALE: How many users? How many actions per user per day?
  
  2. CALCULATE THROUGHPUT (QPS):
     Total requests/day = users × actions_per_user
     QPS_avg = total_requests / 86,400
     QPS_peak = QPS_avg × peak_factor (usually 2-5×)
     
  3. CALCULATE STORAGE:
     Storage/day = writes_per_day × size_per_write
     Storage_total = Storage/day × retention_days
     
  4. CALCULATE BANDWIDTH:
     Read bandwidth = QPS_read × average_response_size
     Write bandwidth = QPS_write × average_write_size
     
  5. SERVER COUNT:
     servers = QPS_peak / (QPS_per_server)
     Typical QPS per server: web app = 5,000-10,000; DB = 1,000-5,000

COMPLETE EXAMPLE: Design Twitter-scale system

  GIVEN:
    DAU (Daily Active Users): 500 million
    Each user: reads 100 tweets/day, posts 0.1 tweets/day (1 tweet per 10 days)
    Tweet size: 300 bytes (text only)
    Media: 10% of tweets have a 200 KB image
    Retention: 5 years
    Read:Write ratio: 1000:1 (heavily read-dominant)
  
  THROUGHPUT:
    Writes/day:    500M × 0.1 = 50M tweets/day
    Writes QPS:    50M / 86,400 = 578 ≈ 600 writes/sec
    Reads/day:     500M × 100 = 50B reads/day
    Reads QPS:     50B / 86,400 ≈ 578,703 ≈ 600,000 reads/sec
    Peak QPS read: 600,000 × 2.5 = 1.5M reads/sec (peak)
    
  STORAGE:
    Tweet text:   50M/day × 300 bytes = 15 GB/day
    Image data:   50M × 10% × 200KB = 5M × 200KB = 1 TB/day
    Total/day:    ~1 TB/day
    5-year total: 1 TB × 365 × 5 = 1,825 TB ≈ 2 PB
    
  BANDWIDTH:
    Write bandwidth: 600 writes/sec × 300 bytes = 180 KB/sec (negligible)
    Read bandwidth: 600,000 reads/sec × 300 bytes = 180 MB/sec (text only)
    Media read (CDN): separate estimation
    
  SERVER COUNT (for read path):
    Assumption: 1 web server handles 10,000 reads/sec (after caching)
    Servers needed: 1.5M / 10,000 = 150 servers for peak read QPS
    
  STORAGE TIER:
    2 PB → object storage (S3) for media
    Text: ~27 TB over 5 years → fits in distributed DB cluster
    
  CONCLUSIONS:
    → Need distributed caching (Redis) to handle 1.5M reads/sec without DB hits
    → DB: handles ~1,500 reads/sec (1% of total, rest from cache)
    → Media storage: S3 + CDN
    → ~150 app servers for peak
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Back-of-Envelope Estimation:
- Architecture decisions based on gut feel: wrong scale choices
- Under-provisioning: system fails under real load
- Over-provisioning: expensive over-engineered system for simple scale

WITH Back-of-Envelope Estimation:
→ Right-size architecture decisions: 10 servers vs. 100 servers vs. 10,000
→ Identify bottlenecks before building: "storage will be 2 PB → need object store"
→ Design interview signals competence: engineers who estimate are trusted to build

---

### 🧠 Mental Model / Analogy

> Estimating how long a road trip takes. You don't calculate exact traffic, fuel stops, and construction delays. You know: distance = 500 miles, average speed = 60 mph, → roughly 8 hours. Add 1-2 hours for stops. Good enough to decide: "leave by 8 AM to arrive by 6 PM." Back-of-envelope: good enough to plan, not precise enough to publish. The goal is the right order of magnitude, not the right decimal.

"Road trip distance" = system scale (users, data)
"Average speed" = throughput per component (QPS per server)
"Total time = distance / speed" = servers needed = total QPS / QPS per server
"Add buffer for stops" = add 2-3× safety factor for peak traffic
"Don't need GPS-precision to plan the trip" = order of magnitude is sufficient

---

### ⚙️ How It Works (Mechanism)

**Worked example: design a URL shortener (system design classic):**

```
REQUIREMENTS (from interviewer):
  - 100M URLs shortened per day
  - Average URL lifetime: 10 years
  - Read:Write = 100:1 (every short URL is accessed 100 times)
  
STEP 1: QPS
  Write QPS: 100M / 86,400 = 1,157 ≈ 1,200 writes/sec
  Read QPS:  100M × 100 / 86,400 = 115,700 ≈ 120,000 reads/sec
  Peak read: 120,000 × 3 = 360,000 reads/sec (peak 3×)
  
STEP 2: STORAGE
  Short URL record: { short_id: 7 chars, long_url: 2KB avg, created_at: 8 bytes }
  = 7 + 2,048 + 8 ≈ 2,063 bytes ≈ 2 KB per record
  
  Records over 10 years: 100M/day × 365 × 10 = 365B records
  Storage: 365B × 2 KB = 730 TB ≈ 1 PB
  
  → 1 PB is too large for a single relational database.
  → Requires: sharding, or NoSQL (Cassandra, DynamoDB)
  
STEP 3: BANDWIDTH
  Read bandwidth: 360,000 reads/sec × (7 bytes short + 300 bytes avg response)
                = 360,000 × 307 bytes ≈ 110 MB/sec
  → CDN or caching in front of database
  
STEP 4: SERVERS
  Assumption: 1 server handles 50,000 reads/sec (cached in Redis)
  Servers needed: 360,000 / 50,000 ≈ 8 servers
  → Very modest fleet, but database is the bottleneck
  
STEP 5: SHORT URL ID SPACE
  7 characters from [a-z, A-Z, 0-9] = 62 characters
  62^7 = 3.5 trillion possible IDs
  10 years × 100M/day × 365 = 365 billion URLs
  3.5 trillion >> 365 billion → sufficient for 10 years (95 years actually)
  
CONCLUSIONS:
  - Database: sharded NoSQL (data too large for single MySQL)
  - Caching: Redis (hot URLs: 80/20 rule → 20% of URLs = 80% of traffic)
  - ID generation: distributed (Snowflake-style ID, not auto-increment)
  - CDN: serve redirects at edge for ultra-low latency
```

---

### 🔄 How It Connects (Mini-Map)

```
System Requirements (scale/traffic)
        │
        ▼ (quantify requirements)
Back-of-Envelope Estimation ◄──── (you are here)
(QPS, storage, bandwidth, server count)
        │
        ├── Capacity Planning (formal version of estimation)
        ├── Sharding (estimation reveals storage too large for one DB)
        └── Caching (estimation reveals read QPS too high without cache)
```

---

### 💻 Code Example

**Python: quick estimation helper utility:**

```python
class Estimator:
    """Back-of-envelope estimation helper."""
    
    SECONDS_PER_DAY = 86_400
    SECONDS_PER_YEAR = 31_536_000
    
    @staticmethod
    def qps(requests_per_day: float, peak_multiplier: float = 2.0) -> dict:
        avg = requests_per_day / Estimator.SECONDS_PER_DAY
        peak = avg * peak_multiplier
        return {"avg_qps": round(avg), "peak_qps": round(peak)}
    
    @staticmethod
    def storage_gb(records_per_day: float, bytes_per_record: int, 
                   retention_years: int) -> float:
        total_records = records_per_day * 365 * retention_years
        total_bytes = total_records * bytes_per_record
        return round(total_bytes / (1024**3), 1)  # convert to GB
    
    @staticmethod
    def servers_needed(peak_qps: float, qps_per_server: int = 5000) -> int:
        return max(2, -(-peak_qps // qps_per_server))  # ceiling division

# Twitter estimation:
e = Estimator()

dau = 500_000_000
tweets_per_user_day = 0.1
reads_per_user_day = 100

write_qps = e.qps(dau * tweets_per_user_day)
print(f"Write QPS: {write_qps}")
# Write QPS: {'avg_qps': 578, 'peak_qps': 1157}

read_qps = e.qps(dau * reads_per_user_day, peak_multiplier=2.5)
print(f"Read QPS: {read_qps}")
# Read QPS: {'avg_qps': 578703, 'peak_qps': 1446759}

tweet_storage_gb = e.storage_gb(
    records_per_day=dau * tweets_per_user_day,
    bytes_per_record=300,
    retention_years=5
)
print(f"Tweet text storage: {tweet_storage_gb:.0f} GB = {tweet_storage_gb/1024:.1f} TB")
# Tweet text storage: 27375 GB = 26.7 TB

servers = e.servers_needed(read_qps["peak_qps"], qps_per_server=10000)
print(f"App servers needed (peak): {servers}")
# App servers needed (peak): 145
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Back-of-envelope must be precise to be useful | The goal is order of magnitude accuracy (within 10×), not exact numbers. Getting the answer to within 2× is excellent for planning purposes. The key insight is whether something is 1 TB or 1 PB — a 2× error in either direction doesn't change the architecture decision |
| You need to know exact benchmarks for QPS per server | Rough benchmarks are sufficient. Common rules of thumb: web API server = 5,000-10,000 RPS (with caching); relational DB = 1,000-5,000 QPS; Redis = 100,000-1,000,000 ops/sec. Knowing the rough order of magnitude is enough to decide cache vs. DB vs. in-memory |
| Estimation is only useful in interviews | Production capacity planning uses exactly these techniques. SRE teams, capacity engineers, and architects use back-of-envelope estimation to size infrastructure, forecast growth, and evaluate database tier choices |
| Complex mathematical models are always better than rough estimates | For early architecture decisions, a 10-minute back-of-envelope is often more valuable than a 2-week detailed model. The 2-week model is appropriate for procurement decisions; the 10-minute estimate is appropriate for choosing between architectural approaches |

---

### 🔥 Pitfalls in Production

**Estimating averages — ignoring peak and tail:**

```
PROBLEM: infrastructure sized for average QPS, not peak

  Estimation: 100M requests/day = 1,157 avg QPS
  Infrastructure: 6 servers at 200 QPS each = 1,200 QPS capacity
  "Great: 200 QPS buffer above average."
  
  REALITY:
  Traffic is NOT uniform throughout the day:
    2 AM: 50 QPS (quiet hours)
    12 PM: 3,500 QPS (lunch peak)
    8 PM: 5,000 QPS (evening peak — Netflix effect)
    
  Traffic follows power law during events:
    Product launch: 10,000 QPS surge for 5 minutes
    
  6 servers at 200 QPS capacity = 1,200 QPS MAX
  Evening peak: 5,000 QPS → servers overloaded → outage.
  
CORRECT ESTIMATION:

  1. AVERAGE QPS: 100M / 86,400 = 1,157
  2. PEAK MULTIPLIER: 3-5× for normal business hours peak
     Peak QPS: 1,157 × 4 = 4,628
  3. BURST MULTIPLIER: 10-20× for viral/launch events
     Burst QPS: 1,157 × 15 = 17,355
  4. SIZE FOR: peak (not average); add auto-scaling for burst
     
  Capacity planning:
    Baseline (always-on): handle 4,628 QPS (8 servers at 600 QPS each)
    Auto-scale: up to 17,355 QPS during bursts (provision 30 servers max)
  
  STORAGE: be precise about retention
    Average record size: be careful of median vs. mean.
    Text posts: 90th percentile = 300 bytes; 99th percentile = 10 KB (with media URLs)
    Use 95th percentile for storage estimation (covers most users' data)
```

---

### 🔗 Related Keywords

- `Capacity Planning` — formal version of back-of-envelope estimation with ongoing monitoring
- `Sharding (System)` — estimation determines when single-node DB storage is insufficient
- `Vertical Scaling` — estimation determines whether single-server scaling is feasible
- `Horizontal Scaling` — estimation determines server count needed for QPS requirements
- `Rate Limiting (System)` — estimation identifies QPS that must be rate-limited

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Quick order-of-magnitude calculations:    │
│              │ QPS, storage, bandwidth, server count     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ System design: architecture decisions;    │
│              │ interviews; early capacity planning       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using averages instead of peaks; ignoring │
│              │ 10× safety factor for viral/burst traffic │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "8 hours to drive 500 miles at 60 mph —  │
│              │  good enough to plan the trip."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Capacity Planning → Sharding              │
│              │ → Consistent Hashing                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design a Google Photos-scale system. Given: 1 billion users, average 5 photo uploads per user per day, average photo size = 4 MB (original) + 500 KB (thumbnail). Retention: forever. Estimate: (a) daily storage added, (b) total storage after 10 years, (c) daily bandwidth for uploads, (d) daily bandwidth for views (assume 20 views per user per day, each serving only thumbnails). What storage tier and CDN strategy does your estimation imply?

**Q2.** A SaaS platform processes financial transactions: 50 million users, each averaging 10 transactions per day, peak at 5× average. Each transaction record is 2 KB. The system requires 7-year audit retention. Calculate: (a) average and peak transactions per second, (b) total storage over 7 years, (c) number of database servers assuming each handles 2,000 TPS and you need 2× overhead. Based on your storage estimate, would you use a single database server, a sharded relational database, or a NoSQL distributed database? Justify your choice.
