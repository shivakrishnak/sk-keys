---
layout: default
title: "Active-Passive"
parent: "System Design"
nav_order: 696
permalink: /system-design/active-passive/
number: "0696"
category: System Design
difficulty: ★★☆
depends_on: Redundancy, High Availability, Monitoring
used_by: HA Architecture, Failover Systems
related: Active-Active, Redundancy, Failover
tags:
  - high-availability
  - reliability
  - intermediate
  - failover
  - architecture
---

# 696 — Active-Passive

⚡ TL;DR — Primary system handles all traffic; backup (passive) remains idle and ready to take over if primary fails. Simple and safe, but wastes backup capacity and requires failover delay.

| #696            | Category: System Design                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | Redundancy, High Availability, Monitoring |                 |
| **Used by:**    | HA Architecture, Failover Systems         |                 |
| **Related:**    | Active-Active, Redundancy, Failover       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Single server handles all traffic. If it fails, service down. No backup. Customers angry. SLA breached.

**THE BREAKING POINT:**
Business needs redundancy but complexity of active-active too high. Need simple HA: keep backup ready, switch if needed.

**THE INVENTION MOMENT:**
"One system actively serving. One system passively waiting. If active fails, promote passive. Simple, safe, proven."

---

### 📘 Textbook Definition

**Active-Passive:** Primary system actively serves all traffic. Secondary (passive) system remains standby, ready to take over. When primary fails, traffic is switched to secondary (failover). Secondary then becomes the new primary until original recovers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One system active. One system waiting. If active dies, switch to waiting one.

**One analogy:**

> A restaurant has 1 chef working, 1 chef on break. If working chef gets sick, bring break chef back. Simple.

**One insight:**
Simple and safe, but 50% of servers are idle (wasteful capacity).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. One system fully active, one fully passive
2. Data must replicate from active to passive (async is fine)
3. Passive must be ready to take over quickly
4. Simple data consistency (only one writer)

**DERIVED DESIGN:**

- Active: handles all requests, writes all data
- Passive: receives replication from active, does not accept requests
- Monitoring: checks if active is healthy
- Failover: if active fails, promote passive to active, update DNS/load balancer
- Recovery: if old active comes back, it becomes new passive (not re-promoted without verification)

**THE TRADE-OFFS:**
**Gain:** Simple. Data consistency easy (only one writer). Predictable. Low complexity.

**Cost:** 50% capacity wasted. Failover delay (5-15 seconds). Passive has no real-time experience (might have bugs when promoted).

---

### 🧪 Thought Experiment

**SETUP:**
E-commerce site. Active in us-east, passive in us-west.

**Normal:**

- Active: 10K requests/sec, fully utilized
- Passive: idle, receiving replication (minimal CPU)
- Both have replicas of inventory database

**Active Fails:**

- Detection: 5 seconds (monitoring alert)
- Failover: 10 seconds (DNS update, route traffic)
- Total failover: ~15 seconds
- Passive starts receiving traffic
- But passive now at 100% CPU (not idle anymore)

**Passive Overwhelmed:**

- Passive designed for idle ops, not peak load
- If active was at capacity, passive also at capacity (bad)
- Response time increases, some requests timeout
- Should have sized passive to handle full load (but that defeats cost savings)

**THE INSIGHT:**
Active-passive works if: (1) load not at capacity, or (2) passive is also fully sized (then why not active-active?). Tradeoff: cost vs. performance during failover.

---

### 🧠 Mental Model / Analogy

> Office has 1 employee at desk, 1 employee in break room. If desk employee quits, break room employee takes over. Works well: continuity maintained. But break room employee might not be as productive (out of practice). And having 50% of payroll in break room is wasteful.

- "Desk employee" → active system
- "Break room employee" → passive system
- "Quits" → component failure
- "Not as productive" → passive hasn't been processing requests, rusty
- "Wasteful" → unused capacity

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
One server handling all traffic. Another server sitting idle, ready to take over if first fails.

**Level 2 — How to use it (junior developer):**
Configure primary and secondary databases. Primary handles all writes. Secondary receives replicated data. If primary fails, promote secondary to primary. Application connects to secondary (now primary). Requires <15 second failover time.

**Level 3 — How it works (mid-level engineer):**
Primary and secondary databases connected via replication (async, master-slave). Monitoring checks primary health. If primary fails (replication lag > threshold, heartbeat missing), trigger failover: promote secondary to primary (stop accepting replication, start accepting writes). Update connection strings. Notify team. Monitor new primary stability before bringing original primary back.

**Level 4 — Why it was designed this way (senior/staff):**
Active-passive is traditional high-availability pattern. Simpler than active-active (no data consistency nightmare). Works well for: (1) read-heavy systems (replicas can handle reads while passive waits), (2) low-frequency writes (async replication sufficient), (3) systems where failover delay acceptable (RTO > 10 sec). Modern alternatives: active-active (if data consistency solved), multi-region active-passive (reduce latency while keeping simplicity).

---

### ⚙️ How It Works (Mechanism)

Active-passive architecture:

```
SETUP:
  [ACTIVE] ──(replication)──→ [PASSIVE]
           ← (heartbeat check) ←

  Load Balancer / DNS:
    Points to ACTIVE only

  Monitoring:
    Checks ACTIVE health every 10 sec

NORMAL OPERATIONS:
  Client Request
    → Load Balancer → ACTIVE
    → ACTIVE processes, writes to database
    → Data replicated to PASSIVE (async, slight lag)
    → ACTIVE sends response

  PASSIVE:
    - Receives replication stream
    - Applies updates to local database
    - Does NOT serve requests
    - Idle, low CPU usage

ACTIVE FAILS (Hardware Crash):
  Time 0:00 - ACTIVE crashes
  Time 0:05 - Monitoring detects (heartbeat missing)
  Time 0:10 - Failover triggered:
    1. PASSIVE promoted to ACTIVE (stop replication, start accepting writes)
    2. DNS updated (or load balancer updated) to point to PASSIVE
  Time 0:15 - New ACTIVE (formerly PASSIVE) receives first request

  Downtime: 15 seconds
  Data Loss: Potentially 5-10 sec of writes (replication lag at time of failure)

RECOVERY:
  ACTIVE recovered (server rebooted)
    → Old ACTIVE tries to resume as MASTER
    → But NEW ACTIVE (formerly PASSIVE) already master
    → Conflict! Need to resolve.

  Option 1: Old active becomes new passive
    - Stop old active
    - Wipe old active database
    - Resynchronize from new active (now primary)
    - Start old active in passive mode

  Option 2: Manual intervention
    - Team decides which should be primary
    - Promote chosen one, demote other
    - Avoid split-brain

SPLIT-BRAIN PREVENTION:
  - Only one system can be PRIMARY
  - If PRIMARY goes down, only PASSIVE can be promoted
  - PASSIVE can be promoted ONLY if confirms PRIMARY truly down (not network lag)
  - Fencing: OLD PRIMARY, if comes back up, self-isolates if can't become PRIMARY again
```

**Failover Timeline:**

```
14:30:00 - Active database process killed
14:30:05 - Monitoring detects "no heartbeat"
14:30:10 - Failover approval (automatic or manual)
14:30:12 - Passive promoted: replication stopped, starts accepting writes
14:30:13 - DNS/LB updated to point to passive
14:30:15 - First client request hits new active
14:30:20 - Service recovered (mostly transparent to users)
```

---

### 💻 Code Example

**Example 1 — PostgreSQL Primary-Replica Setup:**

```bash
#!/bin/bash
# Setup active-passive PostgreSQL

# PRIMARY (Active)
# postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64

# pg_hba.conf - allow replication connection
host replication replication 10.0.0.2/32 trust

# Start primary
sudo systemctl start postgresql

# SECONDARY (Passive)
# Start replication from primary
pg_basebackup -h 10.0.0.1 -D /var/lib/postgresql/14/main -U replication -v -P -W
# recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=10.0.0.1 port=5432 user=replication password=xxxx'

# Start passive (readonly mode)
sudo systemctl start postgresql

# Monitoring - Check replication lag
watch -n 1 'psql -c "SELECT slot_name, restart_lsn, restart_lsn IS NULL as unused FROM pg_replication_slots;"'

# FAILOVER - Promote passive to primary
# On PASSIVE:
sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl promote -D /var/lib/postgresql/14/main

# Update DNS / Load Balancer to point to new primary
# ...
```

**Example 2 — Monitoring Replication Lag:**

```python
import psycopg2
import time

def check_replication_lag(primary_host, secondary_host):
    """Check if replication lag exceeds threshold"""

    try:
        # Connect to primary
        conn_primary = psycopg2.connect(f"host={primary_host}")
        cur_primary = conn_primary.cursor()
        cur_primary.execute("SELECT pg_current_wal_lsn();")
        primary_lsn = cur_primary.fetchone()[0]

        # Connect to secondary
        conn_secondary = psycopg2.connect(f"host={secondary_host}")
        cur_secondary = conn_secondary.cursor()
        cur_secondary.execute("SELECT pg_last_wal_replay_lsn();")
        secondary_lsn = cur_secondary.fetchone()[0]

        # Calculate lag (bytes behind)
        lag = int(primary_lsn.split('/')[0], 16) - int(secondary_lsn.split('/')[0], 16)
        lag_mb = lag / (1024 * 1024)

        print(f"Replication lag: {lag_mb:.2f} MB")

        # Alert if lag > 100 MB (replication falling behind)
        if lag_mb > 100:
            print("ALERT: Replication lag exceeding threshold, trigger failover?")
            return False

        return True

    except Exception as e:
        print(f"Error checking replication: {e}")
        # If can't connect to primary, assume it's down
        print("Primary unreachable, trigger failover")
        return False

# Monitor continuously
while True:
    is_healthy = check_replication_lag("10.0.0.1", "10.0.0.2")
    if not is_healthy:
        print("Initiating failover...")
        # trigger_failover()
        break
    time.sleep(10)  # Check every 10 seconds
```

**Example 3 — Failover Automation (Bash Script):**

```bash
#!/bin/bash
# Automated failover script

PRIMARY="10.0.0.1"
SECONDARY="10.0.0.2"
FAILOVER_THRESHOLD_SEC=30

echo "Starting active-passive failover monitor..."

while true; do
    # Check if primary is responding
    if ! ping -c 1 -W 5 "$PRIMARY" > /dev/null 2>&1; then
        echo "[$(date)] Primary is not responding!"
        sleep 5

        # Confirm with second check
        if ! ping -c 1 -W 5 "$PRIMARY" > /dev/null 2>&1; then
            echo "[$(date)] PRIMARY CONFIRMED DOWN - INITIATING FAILOVER"

            # Promote secondary to primary
            ssh "postgres@$SECONDARY" "sudo -u postgres pg_ctl promote -D /var/lib/postgresql/14/main"

            # Update DNS (using AWS Route53 as example)
            aws route53 change-resource-record-sets \
              --hosted-zone-id Z1234567890ABC \
              --change-batch '{
                "Changes": [{
                  "Action": "UPSERT",
                  "ResourceRecordSet": {
                    "Name": "db.internal",
                    "Type": "A",
                    "TTL": 300,
                    "ResourceRecords": [{"Value": "'$SECONDARY'"}]
                  }
                }]
              }'

            # Alert team
            echo "Failover completed. New primary: $SECONDARY" | mail -s "DB Failover Alert" ops@company.com

            # Exit monitoring (can restart when primary recovered)
            break
        fi
    fi

    sleep 10  # Check every 10 seconds
done
```

---

### ⚖️ Comparison Table

| Aspect                   | Active-Passive                | Active-Active                |
| ------------------------ | ----------------------------- | ---------------------------- |
| **Failover Time**        | 10-15 seconds                 | Immediate (0 seconds)        |
| **Capacity Utilization** | 50% (passive idle)            | 100% (both active)           |
| **Data Consistency**     | Simple (one writer)           | Complex (multi-master)       |
| **Complexity**           | Low                           | High                         |
| **Cost**                 | Lower (passive doing nothing) | Higher (both at capacity)    |
| **Data Loss Risk**       | Low (replication can lag)     | Varies (depends on strategy) |

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                                     |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| "Active-passive has zero downtime"                                    | No. Failover still takes 10-15 sec. Only active-active has near-zero.                                                       |
| "Passive server is completely idle"                                   | Mostly. It's applying replication, but no user traffic.                                                                     |
| "If passive is fully sized for full load, why not use active-active?" | Good point. If passive sized for 100%, then yes, consider active-active. But then complexity increases.                     |
| "Data loss is impossible in active-passive"                           | No. Async replication can lose data (writes in flight when active fails). For zero loss, use sync replication (but slower). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Replication Lag Too High**

**Symptom:**
Replication lag = 500 MB. Primary fails. Secondary promoted. 500 MB of writes lost (transactions not replicated).

**Root Cause:**
Async replication with network lag. Writes queued on primary waiting to replicate.

**Diagnostic Command:**

```bash
# Check replication lag
psql -c "SELECT slot_name, restart_lsn FROM pg_replication_slots;" -h primary
```

**Fix:**
Either: (1) Use sync replication (slower but no data loss), or (2) Accept potential data loss and restore from backups.

---

**Failure Mode 2: Split-Brain (Both Think They're Primary)**

**Symptom:**
Primary goes down. Passive promoted. But network recovers and old primary comes back online. Both now accepting writes. Data corruption.

**Root Cause:**
Insufficient fencing. Old primary not self-isolating when it comes back.

**Diagnostic Command:**

```bash
# Check if both are primary
ssh primary "psql -c 'SHOW standby_mode;'"  # Should show OFF
ssh passive "psql -c 'SHOW standby_mode;'"  # Should show OFF (after promotion)
```

**Fix:**
Implement fencing: if old primary comes back and detects it's not the current primary, self-isolate (stop serving requests until manual intervention).

---

### 🔗 Related Keywords

**Prerequisites:**

- `Redundancy`, `High Availability`, `Replication`

**Builds On This:**

- `Active-Active`, `Disaster Recovery`, `Monitoring`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One active, one passive. Fail to      │
│              │ passive when active fails.            │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Need HA without active-active          │
│ SOLVES       │ complexity                            │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Simple, but wastes 50% capacity       │
│              │ and has failover delay                │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Traditional HA; low failover latency  │
│              │ acceptable; simple data consistency   │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Need zero failover delay; high        │
│              │ capacity utilization critical        │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Simple: one works, one waits."      │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Primary fails. Replication lag was 50MB. How much data is lost? How do you recover it?

**Q2.** After failover, passive is now primary. Old primary comes back online. How do you prevent it from accepting writes and corrupting data?
