---
id: SYD-026
title: Back-of-Envelope Estimation
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-001, SYD-002
used_by: SYD-027
related: SYD-001, SYD-002, SYD-027, SYD-078
tags:
  - architecture
  - estimation
  - interview
  - system-design-process
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/syd/back-of-envelope-estimation/
---

⚡ TL;DR - Back-of-envelope estimation uses approximate
math to size a system before designing it. The goal
is to find the order of magnitude: do we need 1 server
or 100? 1 TB of storage or 1 PB? Precise numbers are
not required - the right order of magnitude informs
the correct architectural choices. This is a core
system design interview skill and a critical real-world
practice before starting any significant infrastructure
investment.

| #026 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | System Design, Non-Functional Requirements | |
| **Used by:** | Capacity Planning | |
| **Related:** | System Design, Non-Functional Requirements, Capacity Planning, System Design Interview Framework | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineering team designs a social media system.
They design a single PostgreSQL database for all
user data. They start building. Six months later,
with real traffic data, they realize they need 50TB
of storage for media, 500,000 QPS for reads, and
a distributed cache layer. The entire architecture
must be redesigned. Six months of work on the wrong
foundation.

**THE CORE NEED:**
Before designing, estimate: what is the scale of
the problem? A system serving 1 million daily users
needs fundamentally different architecture than one
serving 1 billion. The estimation must happen in
the first 5 minutes of architecture design, not
six months in.

---

### 📘 Textbook Definition

**Back-of-envelope estimation:** A rapid, approximate
calculation used to determine the order-of-magnitude
scale of a system's requirements before detailed
design. Named after the practice of doing quick math
on the back of an envelope (or napkin). Uses known
constants (byte sizes, network speeds, latency
numbers) and simple arithmetic to estimate storage,
bandwidth, throughput, and server count requirements.
Accuracy to within 1 order of magnitude (10x) is
sufficient; the goal is to determine correct
architectural tier choices, not precise numbers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Quick approximate math to size a system: "do we
need 1 server or 1,000 servers? 1 GB or 1 PB?"

**One analogy:**
> A contractor bidding on a kitchen renovation does
> not measure every cabinet before estimating cost.
> They walk through, note the approximate square
> footage, multiply by a cost-per-sqft heuristic,
> and give a ballpark: "$15k-20k." This is enough
> to decide whether to pursue the project and how
> to approach the design. The precise measurement
> comes later, in the actual design phase.
>
> Back-of-envelope estimation in system design is
> the same walk-through: quick numbers that determine
> the architectural approach before deep design.

**One insight:**
The most important output is NOT the exact number -
it is the decision about which architectural tier
is needed. Is the read QPS 100 (fits one DB)? Or
100,000 (needs caching + read replicas)? Or
10,000,000 (needs a distributed database + CDN)?
Different tiers → completely different designs.

---

### 🔩 First Principles Explanation

**THE ESSENTIAL CONSTANTS TO MEMORIZE:**

```
TIME:
  1 year ≈ 3 × 10^7 seconds (31.5 million)
  1 day = 86,400 seconds ≈ 10^5 seconds
  30 days ≈ 2.6 × 10^6 seconds

STORAGE SIZES:
  1 char = 1 byte
  1 KB = 10^3 bytes
  1 MB = 10^6 bytes
  1 GB = 10^9 bytes
  1 TB = 10^12 bytes
  1 PB = 10^15 bytes

  Typical row sizes:
  User record: ~1 KB
  Tweet/post: ~1-10 KB
  Photo metadata: ~1 KB
  Photo (compressed): ~1-3 MB
  Video (1 min, 1080p): ~100-500 MB

LATENCY NUMBERS (approx):
  L1 cache hit:     ~0.5 ns
  RAM access:       ~100 ns
  SSD read (4KB):   ~16 us
  Disk read (HDD):  ~2 ms
  Round trip same datacenter: ~0.5 ms
  Cross-country (US): ~40 ms
  Trans-Pacific:    ~150 ms
  Trans-Atlantic:   ~80 ms

THROUGHPUT BASELINES:
  Single DB (PostgreSQL): ~1,000 QPS (writes)
                          ~10,000 QPS (reads)
  Single Redis:           ~100,000 ops/sec
  Single web server:      ~10,000 req/sec
  1 Gbps network:         ~125 MB/s = 10^8 bytes/sec
```

**THE ESTIMATION PROCESS:**

```
Step 1: Define the scale
  "100 million daily active users (DAU)"

Step 2: Derive per-second rate
  DAU = 10^8
  Assume 10% active at peak hour
  Peak users = 10^7
  Assume each makes 10 requests/hour
  Peak QPS = 10^7 × 10 / 3600 ≈ 28,000 QPS
  Round: ~30,000 QPS

Step 3: Derive storage
  Write 1 post per day per active user
  Post size = 1 KB
  Daily writes: 10^8 × 1 KB = 10^11 bytes = 100 GB/day
  3 years retention: 100 GB × 365 × 3 ≈ 100 TB

Step 4: Derive bandwidth
  30,000 QPS × 1 KB per response = 30 MB/sec
  = 30 × 8 Mbps = 240 Mbps (well under 1 Gbps)

Step 5: Server count
  30,000 QPS / 10,000 QPS per web server = 3 servers
  (Use 5-10 with redundancy)
  For DB reads: 30,000 / 10,000 = 3 DB instances
```

**THE TRADE-OFFS:**

**Precision vs speed:** Estimates within 5-10x are
sufficient for design decisions. Do not chase 2-3%
accuracy. Spending 30 minutes on precise estimation
in an interview is wasted time.

**Assumptions matter:** State assumptions clearly.
"I am assuming 100M DAU, 10% peak hourly concurrency,
and 10 requests per user per hour." Wrong assumptions
produce wrong estimates but the process remains correct.

---

### 🧪 Thought Experiment

**FULL ESTIMATION EXAMPLE: Design Twitter**

**Given:** 300M monthly active users (MAU)
50% log in daily → 150M DAU
Average user sends 5 tweets/day
Average user reads 500 tweets/day
Average tweet: 280 chars = ~1 KB
Some tweets have media (10% have photos, 1% video)

**WRITE QPS (tweets posted):**
```
150M DAU × 5 tweets/day = 750M tweets/day
750M / 86,400 sec ≈ 8,700 tweets/sec
Peak (2x average): ~17,000 tweets/sec
```

**READ QPS (timeline reads):**
```
150M DAU × 500 reads/day = 75B reads/day
75B / 86,400 ≈ 868,000 reads/sec
Peak (2x): ~1.7M reads/sec
```

**STORAGE (text only, 5 years):**
```
8,700 tweets/sec × 86,400 sec/day × 365 days × 5 years
= 8,700 × 31.5M sec in 5 years
= 274B tweets × 1 KB = 274 TB (text)
= ~300 TB for text content
```

**STORAGE (media, 5 years):**
```
10% tweets have photos: 27B photos × 2 MB avg
= 54 PB (photos)
1% tweets have video: 2.7B videos × 100 MB avg
= 270 PB (video)
Total: ~325 PB
```

**ARCHITECTURAL CONCLUSIONS:**
- Read QPS 1.7M: cannot be served by a single DB.
  Need distributed cache (Redis cluster) + CDN.
- Write QPS 17,000: needs write sharding (DB cluster).
- Storage 300 TB text: distributed DB (Cassandra).
- Storage 325 PB media: dedicated object storage
  (S3-equivalent). Cannot store in DB.
- Media traffic: serve via CDN, not app servers.

**THE VALUE:** These estimates directly eliminate
wrong architectural choices (single DB, app-server
media serving) before any design is drawn.

---

### 🧠 Mental Model / Analogy

> Back-of-envelope estimation is like the Fermi
> estimation problems in physics:
> "How many piano tuners are in Chicago?"
> Answer: population 3M → households 1M → 5% have
> piano = 50K pianos → piano tuned 1x/year = 50K
> tunings/year → 1 tuner does 4/day × 250 days =
> 1,000/year → 50K/1,000 = 50 piano tuners.
>
> Actual answer: ~50-100 piano tuners. Order of
> magnitude correct. Useful for estimating market
> size before building a piano tuning app.
>
> System design estimation: "How many servers do
> we need for 100M users?" Same process. Same
> approach. Same accuracy goal: right order of
> magnitude, not exact.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Quick math to figure out how big the system needs
to be before designing it. "Do we need 1 server
or 1,000 servers?"

**Level 2 - How to use it (junior developer):**
Memorize the key constants: storage sizes (KB/MB/GB),
latency numbers, throughput per server. In interviews:
clarify scale (DAU, QPS, storage retention), derive
storage and QPS from DAU, then use server throughput
constants to count servers.

**Level 3 - How it works (mid-level engineer):**
Practice the five-step process for every interview:
(1) define scale, (2) peak QPS from DAU, (3) storage
from write rate, (4) bandwidth from QPS × response
size, (5) server count from QPS / server capacity.
Always state assumptions. Use round numbers (10^8
not 108,321,000).

**Level 4 - Why it was designed this way (senior/staff):**
The estimation is a forcing function for a critical
system design discipline: understanding scale before
choosing technology. A system with 1,000 QPS and
a system with 1,000,000 QPS need different solutions.
The estimation reveals which problem you are solving.
In real projects: capacity planning documents serve
this function, and pre-mortems use estimation to
identify where a design will fail under load.

**Level 5 - Mastery (distinguished engineer):**
Expert-level estimation incorporates cost modeling.
"100 TB of storage × $0.023/GB-month = $2,300/month."
"1.7M reads/sec for Twitter's architecture would
require ~170 Redis cache nodes at $200/month each =
$34,000/month for caching alone." This turns
estimation into a real cost-vs-architecture
tradeoff analysis. At staff/principal level, the
estimation output is not just "what architecture"
but "what does this cost and how do we optimize it?"

---

### 💻 Code Example

**Example 1 - Full estimation template (interview)**
```
BACK-OF-ENVELOPE TEMPLATE:
================================

1. SCALE DEFINITION
   MAU: ___M
   DAU: ___M (assume 50% of MAU)
   Peak concurrent: ___M (assume 10% of DAU at peak hour)
   
2. THROUGHPUT
   Write rate = DAU × writes_per_user / 86,400
   Read rate = DAU × reads_per_user / 86,400
   Peak multiplier: 2-3x average
   
3. STORAGE
   New data/day = write_rate × avg_record_size × 86,400
   Total (5yr) = daily × 365 × 5
   Media storage separate (10x-100x text)
   
4. BANDWIDTH
   Ingress = write_rate × avg_write_size
   Egress = read_rate × avg_response_size
   CDN offload: 80-90% of media reads
   
5. SERVER ESTIMATE
   App servers = peak_QPS / 10,000 (req/sec/server)
   DB (reads) = peak_read_QPS / 10,000
   Cache hits needed to reduce DB load: target 95%

NUMBERS TO REMEMBER:
  Day: 86,400 sec ≈ 10^5
  Year: 3.15 × 10^7 sec ≈ 3 × 10^7
  Web server: ~10K req/sec
  DB (reads): ~10K QPS
  Redis: ~100K ops/sec
  Network: ~10^8 bytes/sec (1 Gbps)
```

**Example 2 - Storage estimation (URL shortener)**
```
URL SHORTENER ESTIMATION:
==============================

Scale: 100M new URLs shortened per day
Read:write ratio = 100:1 (mostly redirects)

WRITE RATE:
  100M / 86,400 ≈ 1,160 writes/sec ≈ 1,200 writes/sec

READ RATE:
  1,200 × 100 = 120,000 reads/sec

STORAGE (per URL record):
  Original URL: ~200 bytes
  Short code: 7 chars = 7 bytes  
  Created_at, user_id, metadata: ~100 bytes
  Total per record: ~300 bytes

STORAGE (5 years):
  100M URLs/day × 365 × 5 = 182.5B URLs
  182.5B × 300 bytes = 54.75 TB ≈ 55 TB

BANDWIDTH:
  Read: 120,000 req/sec × 300 bytes = 36 MB/sec
  = ~288 Mbps (under 1 Gbps)

SERVERS NEEDED:
  App servers: 120,000 / 10,000 = 12 (use 15-20)
  DB reads: 120,000 → need caching (Redis)
  With 95% cache hit rate: 6,000 DB QPS (manageable)
  DB instances: 1-2 with read replicas
  Cache: 1-2 Redis instances (100K ops/sec each)

CONCLUSIONS:
  Storage: 55 TB → fits in a PostgreSQL cluster
  Read QPS: 120K → MUST cache (Redis or Memcached)
  Write QPS: 1,200 → single DB primary handles it
  No distributed DB needed at this scale
```

---

### ⚖️ Comparison Table

| Scale | Architecture Implication |
|---|---|
| < 1,000 QPS | Single DB + single app server |
| 1K - 10K QPS | Single DB + read replica + cache |
| 10K - 100K QPS | DB cluster + Redis cache + LB + CDN |
| 100K - 1M QPS | Sharded DB + Redis cluster + CDN |
| > 1M QPS | Distributed DB (Cassandra/DynamoDB) + CDN + microservices |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Estimation needs to be precise | Order of magnitude is sufficient. 28,000 QPS and 30,000 QPS lead to the same architectural decision. Do not agonize over exact numbers. |
| You need to know all constants from memory | In interviews: memorize ~10 key numbers. In real work: reference standard tables. The process (how to estimate) matters more than memorizing every constant. |
| Back-of-envelope is only for interviews | In real engineering: every significant infrastructure decision should start with a capacity estimate. Skipping this leads to either over-provisioning (wasted money) or under-provisioning (production failures). |

---

### 🚨 Failure Modes & Diagnosis

**Incorrect Assumption → Wrong Architecture**

**Symptom:**
A team estimates 1,000 QPS and designs for a single
PostgreSQL instance. In production, peak QPS is
150,000. The DB collapses on the first marketing
campaign. Post-mortem: the team estimated based on
MAU but used "1 request per user per day" instead
of "200 requests per user per day" (page views, API
calls, background refreshes).

**Lesson:**
Estimation accuracy depends on the request rate per
user. For consumer apps, the actual number of
API/DB calls per user session is often 10-100x
higher than naive estimates assume. Include:
background polling, page refreshes, asset requests,
API calls per page load.

**Better estimation:**
```
For a news app:
  DAU = 10M
  Sessions per day per user = 3
  Page views per session = 5
  API calls per page view = 10
  Total API calls = 10M × 3 × 5 × 10 = 1.5B/day
  Average QPS = 1.5B / 86,400 = 17,000 QPS
  Peak (2x): 34,000 QPS
  
  (Naive estimate: 10M × 1 = 10M calls/day = 116 QPS
   ← 300x wrong)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `System Design` - the context in which estimation
  is performed
- `Non-Functional Requirements` - estimation is how
  NFRs become concrete infrastructure requirements

**Builds On This (learn these next):**
- `Capacity Planning` - estimation is the first step
  in formal capacity planning processes

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PURPOSE       │ Find the order of magnitude for         │
│               │ storage, QPS, servers before design     │
├───────────────┼─────────────────────────────────────────┤
│ PROCESS       │ 1. Scale (DAU)                          │
│               │ 2. QPS = DAU×req/day / 86,400           │
│               │ 3. Storage = writes/day × size × years  │
│               │ 4. Bandwidth = QPS × response_size      │
│               │ 5. Servers = QPS / capacity_per_server  │
├───────────────┼─────────────────────────────────────────┤
│ KEY CONSTANTS │ Day = 10^5 s; Year = 3×10^7 s           │
│               │ Web server = 10K req/s                  │
│               │ DB (reads) = 10K QPS                    │
│               │ Redis = 100K ops/s                      │
│               │ 1Gbps = 10^8 bytes/s                    │
├───────────────┼─────────────────────────────────────────┤
│ KEY OUTPUT    │ Which architectural tier (single DB,    │
│               │ sharded DB, distributed DB)?            │
│               │ Need CDN? Cache? Distributed storage?   │
├───────────────┼─────────────────────────────────────────┤
│ ACCURACY      │ Within 1 order of magnitude is fine.    │
│               │ Exact numbers not required.             │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Quick math before design to find out   │
│               │  if we need 1 server or 1,000."         │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Capacity Planning                       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Process: Scale → QPS → Storage → Bandwidth → Servers.
   Five steps, done in 5-10 minutes.
2. Key constants: 1 day ≈ 10^5 sec, web server handles
   ~10K req/sec, Redis handles ~100K ops/sec.
3. Output is a decision about architectural tier, not
   exact numbers. 1 order of magnitude accuracy is enough.

**Interview one-liner:**
"Back-of-envelope estimation converts a system's scale
(100M DAU) into infrastructure requirements: QPS = DAU times
requests-per-day divided by seconds-per-day; storage = write
rate times record size times retention years; server count =
peak QPS divided by per-server capacity. The goal is determining
the architectural tier - single DB (< 10K QPS), DB with caching
(10K-100K QPS), sharded cluster (100K-1M QPS), or distributed
database (> 1M QPS) - not precise numbers. Order of magnitude
accuracy is sufficient for design decisions."
