---
version: 2
layout: default
title: "Redis Persistence"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /nosql/redis-persistence/
id: NDB-029
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Redis Data Structures, Key-Value Store, Durability
used_by: Redis Data Structures, Caching, System Design
related: Redis Data Structures, Key-Value Store, Durability
tags:
  - nosql
  - redis
  - persistence
  - deep-dive
---

# NDB-029 - Redis Persistence

⚡ TL;DR - Redis offers two persistence mechanisms: **RDB** (point-in-time snapshots - fast restarts, some data loss) and **AOF** (append-only log - near-zero data loss, slower restarts); the default is no persistence, making Redis purely a cache; a hybrid RDB+AOF mode offers the best trade-offs for production deployments.

| #463            | Category: NoSQL & Distributed Databases            | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Redis Data Structures, Key-Value Store, Durability |                 |
| **Used by:**    | Redis Data Structures, Caching, System Design      |                 |
| **Related:**    | Redis Data Structures, Key-Value Store, Durability |                 |

---

### 🔥 The Problem This Solves

**REDIS IS IN-MEMORY - WHAT HAPPENS ON RESTART?**
Redis keeps all data in RAM. When the process crashes or restarts, all data is gone unless explicitly persisted. For pure caching use cases: losing data on restart is acceptable (cache warm-up happens naturally from the primary database). For use cases where Redis is a primary store (sessions, leaderboards, rate limiting counters, persistent queues): losing data on restart means losing user sessions, score history, or unconsumed jobs.

**PERSISTENCE OPTIONS:**
Not all Redis use cases have the same durability requirements. RDB snapshots sacrifice some data for fast restart. AOF sacrifices restart speed for near-zero data loss. The right choice depends on: what data lives in Redis, how much data loss is acceptable, and how long restart time can be. This is a classic durability vs. performance trade-off, but Redis makes the default explicit: no persistence by default (opt-in).

---

### 📘 Textbook Definition

Redis supports three persistence modes. **RDB (Redis Database)**: periodic **snapshots** of the in-memory dataset written to disk as a compact binary file (`dump.rdb`). Uses `fork()` system call to create a child process that writes the snapshot without blocking the parent (Copy-on-Write). Triggered by `SAVE` (blocking), `BGSAVE` (non-blocking/background), or auto-save rules (e.g., "save 60 seconds if at least 1000 keys changed"). **Data loss**: up to the interval between snapshots (minutes). **Restart time**: fast (load binary snapshot). **AOF (Append-Only File)**: logs every write command to a file (`appendonly.aof`) in human-readable format. Three fsync policies: `always` (fsync on every command - most durable, slowest), `everysec` (fsync every second - default, ≤1 second data loss), `no` (fsync delegated to OS - fastest, unpredictable data loss). **AOF Rewrite**: compact the AOF file by rewriting it as the minimal set of commands to reproduce the current state. **Hybrid mode** (Redis 4.0+): the AOF rewrite uses the RDB format for the base, then appends only new AOF commands - fast load + recent durability. **No persistence** (default): Redis as a pure cache; data lost on restart.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Redis persistence is a choice between "fast restart with some data loss" (RDB), "near-zero data loss with slow restart" (AOF), or "best of both" (hybrid AOF) - defaulting to no persistence because most Redis use cases are caching.

**One analogy:**

> A whiteboard (Redis RAM) and your backup strategy. "Photograph the whiteboard once an hour" (RDB): if it's erased, you lose the last hour's work. "Write every change into a notebook as you draw" (AOF always): if the whiteboard is erased, replay the notebook - you lose almost nothing, but writing slows you down. "Photograph hourly + notebook since the last photo" (hybrid): fast restore from photo + replay only recent notebook entries. "No backup" (no persistence): the whiteboard is for brainstorming; if erased, start fresh.

- "Photograph hourly" → RDB snapshot every N minutes
- "Write in notebook" → AOF append-only log
- "Photograph + notebook" → hybrid RDB+AOF (rewrite checkpoint)
- "No backup" → default Redis (pure cache, no persistence)
- "Erased whiteboard" → Redis restart / crash

**One insight:**
The `fork()` in RDB uses **Copy-on-Write (CoW)**: the child process gets a copy of the page table, not the actual memory. As long as neither parent nor child modifies a page, they share the same physical memory. Writes by the parent cause CoW: the modified page is copied for the parent; the child still sees the old version. This makes RDB snapshots relatively cheap - unless Redis is doing heavy writes during a snapshot, in which case CoW amplification can double Redis's memory usage temporarily.

---

### 🔩 First Principles Explanation

**RDB SNAPSHOT MECHANISM:**

```
                    BGSAVE triggered
                          │
                     fork()
                    /       \
      Parent Process         Child Process
      (continues serving)    (writes dump.rdb)
             │                      │
      Copy-on-Write (CoW)     reads in-memory data
      writes cause page copy   (snapshot = point-in-time)
             │                      │
      new writes go to             writes to temp file
      copied pages                  dump.rdb.tmp
             │                      │
      parent unaffected        rename to dump.rdb (atomic)
      ←─────────────────────────────┘

CoW amplification:
  Redis uses 10GB RAM
  Heavy write workload during BGSAVE
  → Every written page copied for parent
  → Peak memory: 10GB + (dirty pages × page size)
  → Worst case: ~20GB (all pages dirtied)
  → Risk: OOM kill if system doesn't have enough RAM
```

**AOF APPEND-ONLY FILE:**

```
# appendonly.aof format (human-readable RESP)
*3\r\n$3\r\nSET\r\n$7\r\nuser:42\r\n$5\r\nAlice\r\n
*3\r\n$4\r\nZADD\r\n$11\r\nleaderboard\r\n$5\r\n98500\r\n$5\r\nalice\r\n

# fsync policies:
appendfsync always    # fsync() after EVERY write command
                      # Durability: loses at most 0-1 command
                      # Performance: heavily impacts throughput
                      # Use for: financial, critical data

appendfsync everysec  # fsync() every 1 second (background thread)
                      # Durability: loses at most 1 second of writes
                      # Performance: near-full throughput (recommended)

appendfsync no        # never call fsync() explicitly (OS decides)
                      # Durability: unpredictable (OS buffer loss on crash)
                      # Performance: maximum
```

**AOF REWRITE (compaction):**

```
Problem: AOF file grows indefinitely
  INCR counter → called 1,000,000 times
  AOF contains 1M "INCR counter" commands
  On restart: replay all 1M commands to reconstruct value
  Restart time: grows proportionally with AOF size

AOF Rewrite:
  BGREWRITEAOF command (or automatic when AOF > threshold)
  fork() child process
  Child: reads current in-memory state → writes minimal AOF
    Instead of 1M INCRs → write: "SET counter 1000000"
  Parent: continues writing new commands to AOF buffer
  On rewrite complete:
    rename new compact AOF
    append buffered new commands
    Result: compact AOF file from current state

Hybrid Rewrite (Redis 4.0+, aof-use-rdb-preamble yes):
  Child writes RDB binary format (fast + compact) as header
  Then appends new AOF commands since rewrite started
  Restart: load RDB portion (fast) + replay recent AOF commands (few)
  Best of both: fast restart + near-zero data loss
```

**REDIS PERSISTENCE CONFIGURATION:**

```redis
# redis.conf - RDB configuration
save 3600 1       # save if at least 1 key changed in 3600s (1 hour)
save 300 100      # save if at least 100 keys changed in 300s (5 min)
save 60 10000     # save if at least 10000 keys changed in 60s (1 min)
dbfilename dump.rdb
dir /var/lib/redis/

# AOF configuration
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec          # recommended
aof-use-rdb-preamble yes      # hybrid mode
auto-aof-rewrite-percentage 100  # rewrite when AOF doubles its base size
auto-aof-rewrite-min-size 64mb   # minimum size to trigger rewrite

# No persistence (pure cache mode):
save ""              # disable all save rules
appendonly no        # disable AOF
```

**STARTUP RECOVERY:**

```
Redis starts with AOF enabled:
  → Load appendonly.aof (or .rdb preamble + .aof tail for hybrid)
  → Replay all commands → in-memory state rebuilt
  → If AOF is corrupt: "Redis can't load AOF: ...truncated"
    → redis-check-aof --fix appendonly.aof (truncates to last valid command)

Redis starts with RDB only:
  → Load dump.rdb (binary, fast)
  → In-memory state = snapshot at last save time
  → All data written after last save is lost

Startup priority: if both exist, AOF takes precedence
  (AOF is more up-to-date than RDB)
```

---

### 🧪 Thought Experiment

**SESSION STORE: HOW MUCH DATA LOSS IS ACCEPTABLE?**

Your Redis instance stores user session tokens with a 1-hour TTL. 100,000 active users. Redis crashes and restarts.

**SCENARIO A: No persistence (pure cache):**
All 100,000 sessions lost. All users immediately logged out. Support tickets flood in. Recovery: users log in again (TTL was 1 hour anyway; sessions were transient by design). For authentication tokens: this is often the right trade-off - sessions expire in 1-7 days; restart is rare; users can re-authenticate.

**SCENARIO B: RDB (snapshot every 5 minutes):**
Up to 5 minutes of sessions lost. ~8% of sessions (those created in last 5 min) are invalidated. Most users unaffected. Recovery: fast (binary snapshot load). For most web apps: acceptable.

**SCENARIO C: AOF everysec:**
At most 1 second of sessions lost. Virtually no users affected. Slower restart (replays full AOF log - could take minutes if AOF is large). For financial apps, gaming progress, rate limiting counters: 1 second loss is the maximum acceptable.

**SCENARIO D: AOF always:**
Zero data loss. Every session creation/update written to disk before confirming to the client. Throughput significantly reduced (disk fsync on every write). Latency increases: each SET now waits for disk I/O. Justified for: financial transactions, critical events, PCI-compliant environments.

**KEY INSIGHT:** The right persistence mode is a product decision, not a technical one. "What is the business impact of losing 5 minutes vs. 1 second vs. 0 seconds of Redis data?" drives the technical configuration choice.

---

### 🧠 Mental Model / Analogy

> Think of Redis as a chalkboard in a classroom. The **chalkboard** is fast to write on and read (RAM). Three backup strategies: (1) **Photography** (RDB): take a photo every 5 minutes; if erased, restore from the last photo; lose 5 minutes of work. (2) **Live transcription** (AOF): a secretary writes down every word spoken into a notebook in real-time; if the chalkboard is erased, replay the notebook; lose at most 1 sentence (1 second). (3) **Photo + recent transcription** (hybrid): restore from the last photo, then replay only the lines written after it. (4) **No backup**: the chalkboard is a scratch pad; losing it is expected.

- "Chalkboard" → Redis in-memory state (RAM)
- "Photo every 5 min" → RDB snapshot (fast restore, some data loss)
- "Live transcription" → AOF log (near-zero loss, slow replay)
- "Photo + recent transcript" → hybrid AOF rewrite
- "Scratch pad" → Redis as pure cache (no persistence needed)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** By default, Redis doesn't save anything to disk - restart = empty database. RDB writes a snapshot to disk periodically (like a database backup). AOF writes every command to a log file (like a journal). Most production deployments use AOF for durability. The hybrid mode (AOF + RDB header) is the modern recommendation.

**Level 2:** Configure for your use case: pure cache → no persistence. Session store → AOF everysec (acceptable 1s loss, fast enough). Financial counters/rate limiting → AOF always (no loss, lower throughput). Primary datastore (lists, sorted sets as your DB) → hybrid mode. Monitor: `INFO persistence` in redis-cli for `rdb_last_save_time`, `aof_current_size`, `aof_last_rewrite_time`, `loading` (1 = startup recovery in progress).

**Level 3:** RDB's fork() memory impact: `INFO memory → used_memory_rss` spikes during BGSAVE due to CoW. If Redis memory is tight (> 80% of available RAM), BGSAVE can trigger OOM kill. Mitigation: schedule RDB saves during low-traffic periods; ensure server has 2× Redis memory; use `vm.overcommit_memory = 1` on Linux (allows fork even when apparent memory overcommit). AOF corruption recovery: `redis-check-aof --fix appendonly.aof` truncates at first corruption point. For replicated Redis (Sentinel / Cluster): persistence is per-node; the replica's AOF is independent of the primary's. For Redis Cluster: persistence must be configured on all nodes.

**Level 4:** The persistence trade-off space reveals a fundamental tension in data systems: durability requires disk I/O; disk I/O is orders of magnitude slower than RAM. Redis's design choice - in-memory first, persistence as an option - maximizes throughput for the 99% use case (caching) while providing durability mechanisms for the 1% (primary datastore). The `fork()` + Copy-on-Write mechanism for RDB is clever but has hidden costs: CoW amplification is proportional to the write rate during snapshotting. For write-heavy Redis workloads (INCR, ZADD at high rates), RDB's memory spike can be severe. Some Redis practitioners prefer: no RDB + AOF everysec + Redis Replication (primary + replica) as the durability strategy - if primary crashes, replica takes over with near-zero data loss (replica also has AOF); the primary's memory spike from fork() is avoided. Redis 7.0 introduced Multi-Part AOF to address the single large AOF file problem: AOF is split into base file + incremental files, reducing lock contention during rewrite.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REDIS PERSISTENCE WRITE PATH                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Client: SET user:42 "Alice"                          │
│ Redis main thread:                                   │
│   1. Update in-memory dict                           │
│   2. [REDIS PERSISTENCE ← YOU ARE HERE]              │
│                                                      │
│ RDB path: (background, periodic)                     │
│   fork() → child process                            │
│   child: iterate all keys → write dump.rdb           │
│   parent: continues serving requests (CoW)           │
│                                                      │
│ AOF path: (always-on if appendonly yes)              │
│   Append "SET user:42 Alice\r\n" to AOF buffer       │
│   appendfsync=always: fsync() NOW (before reply)     │
│   appendfsync=everysec: background thread fsync/sec  │
│   appendfsync=no: OS controls fsync timing           │
│                                                      │
│ On crash + restart:                                  │
│   AOF: replay all commands → in-memory state rebuilt │
│   RDB: deserialize binary snapshot → instant state   │
│   Hybrid: load RDB portion → replay recent AOF       │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PRODUCTION REDIS WITH HYBRID PERSISTENCE:**

```
Application:
  ZADD leaderboard 98500 "alice"   (frequent writes)
  → AOF buffer: "ZADD leaderboard 98500 alice"
  → Background fsync thread: fsync every 1 second
  → Durability: at most 1 second of writes lost

Every 5 minutes (or when AOF doubles):
  → BGREWRITEAOF triggered automatically
  → [REDIS PERSISTENCE ← YOU ARE HERE: AOF rewrite]
  → fork() → child writes:
      RDB binary preamble (compact current state)
      + tail: new AOF commands since rewrite started
  → Rename to appendonly.aof
  → Result: compact AOF file, fast restart

Redis crash + restart:
  → Load appendonly.aof
  → Read RDB preamble (fast binary load, seconds)
  → Replay tail AOF commands (seconds, not minutes)
  → In-memory state recovered
  → "Loaded 1000000 keys from AOF in 2.5 seconds"
  → Ready to serve requests
```

---

### ⚖️ Comparison Table

| Mode                 | Data Loss                         | Restart Time                     | Disk Usage           | CPU Cost           | Use Case                      |
| -------------------- | --------------------------------- | -------------------------------- | -------------------- | ------------------ | ----------------------------- |
| **No persistence**   | All data on restart               | Instant                          | None                 | None               | Pure cache                    |
| **RDB**              | Up to snapshot interval (minutes) | Seconds (fast binary load)       | Compact (binary)     | fork() spike       | Backup, cache with tolerance  |
| **AOF everysec**     | ≤ 1 second                        | Slow (replay log)                | Large (verbose RESP) | Background fsync   | Session store, counters       |
| **AOF always**       | ≤ 1 command                       | Slow (replay log)                | Large                | Disk I/O per write | Financial, critical data      |
| **Hybrid (RDB+AOF)** | ≤ 1 second                        | Fast (RDB base + short AOF tail) | Medium               | fork() + fsync     | Recommended for primary store |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                        |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "RDB SAVE blocks Redis"                                    | BGSAVE forks a child process; the main thread is NOT blocked (except for the brief fork() syscall, which is usually < 1ms). SAVE (without BG) is blocking - only use SAVE explicitly for testing                               |
| "AOF everysec is 'safe enough' for financial transactions" | AOF everysec can lose up to 1 second of writes. For financial transactions (money movements), that may be unacceptable. Use AOF always, or don't use Redis as the single source of truth                                       |
| "Enabling persistence doesn't affect performance"          | RDB BGSAVE causes CoW memory spikes. AOF always reduces write throughput by 10-100×. AOF everysec is near-full throughput but still adds background I/O. Always benchmark with persistence enabled in staging                  |
| "Redis with AOF is as durable as PostgreSQL"               | PostgreSQL uses WAL with Group Commit + fsync guarantees and crash recovery. Redis AOF provides similar durability for individual commands but lacks full ACID transaction rollback and crash-safe WAL checkpointing semantics |

---

### 🚨 Failure Modes & Diagnosis

**1. CoW Memory Spike Causing OOM Kill During BGSAVE**

**Symptom:** Redis is killed by the Linux OOM killer during peak traffic. The last Redis log entry before crash: "Background saving started by pid XXXXX". Server had 16GB RAM; Redis was using 12GB.

**Root Cause:** BGSAVE fork() + high write rate → CoW causes each written page to be copied. Redis memory usage temporarily approaches 2× baseline.

**Diagnostic:**

```bash
# Check for OOM kill events
dmesg | grep -i "out of memory" | tail -20
# Look for: "Killed process [redis-pid] (redis-server)"

# Monitor memory during BGSAVE
redis-cli INFO memory | grep -E "used_memory_rss|mem_fragmentation"
# During BGSAVE: used_memory_rss should spike by up to used_memory value
```

**Fix:**

1. Set `vm.overcommit_memory = 1` in `/etc/sysctl.conf` (allows fork even when apparent memory exceeds physical; Linux will use CoW, so actual physical usage is what matters)
2. Reduce Redis memory below 50% of server RAM to leave headroom for CoW
3. Switch to AOF-only persistence (no RDB) to eliminate BGSAVE fork()
4. Add more RAM to the server

---

### 🔗 Related Keywords

**Prerequisites:** Redis Data Structures, Key-Value Store, Durability
**Builds On This:** Redis Data Structures, Caching
**Related:** Redis Data Structures, Key-Value Store

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ NO PERSIST  │ Default; pure cache; OK if data is warm-up │
│ RDB         │ Fast restart; minutes of data loss; CoW    │
│ AOF always  │ Zero loss; lowest throughput; financial    │
│ AOF everysec│ ≤1s loss; near-full throughput; recommended│
│ HYBRID      │ RDB base + AOF tail; best trade-off        │
│ COW RISK    │ BGSAVE can spike memory to 2× baseline     │
│ INFO CMD    │ redis-cli INFO persistence                  │
│ ONE-LINER   │ "RDB = fast restart; AOF = fast recovery;  │
│             │  hybrid = both; default = neither"         │
│ NEXT EXPLORE│ Cassandra Data Modeling → DynamoDB Patterns│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a Redis persistence strategy for a gaming platform where Redis stores: (a) user session tokens (1hr TTL), (b) real-time leaderboard (game scores), (c) player matchmaking queue (active games in progress). For each, specify: which persistence mode, what data loss is acceptable, how long restart can take, and whether Redis is the source of truth or a cache of another database.

**Q2.** (TYPE D - Failure Scenario) A Redis primary is storing rate limiting counters (Sorted Sets with timestamp scores) and user session tokens. Redis has 8GB RAM with RDB saves every 5 minutes and AOF everysec. Server has 12GB total RAM. At 3am, a cron job triggers a bulk data re-import (thousands of ZADD operations per second). Redis is killed at 3:07am. Root cause? What is the data loss? What would you change in the configuration?
