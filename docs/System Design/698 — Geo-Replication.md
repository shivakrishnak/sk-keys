---
layout: default
title: "Geo-Replication"
parent: "System Design"
nav_order: 698
permalink: /system-design/geo-replication/
number: "0698"
category: System Design
difficulty: ★★★
depends_on: Replication, Distributed Systems, Disaster Recovery
used_by: Multi-Region Systems, High Availability
related: Multi-Region Architecture, Active-Active, Disaster Recovery
tags:
  - replication
  - distributed-systems
  - advanced
  - disaster-recovery
  - scalability
---

# 698 — Geo-Replication

⚡ TL;DR — Synchronizing data across geographically separated data centers in real-time. Reduces latency for global users and provides disaster recovery by ensuring data survives data center outages.

| #698            | Category: System Design                                     | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Replication, Distributed Systems, Disaster Recovery         |                 |
| **Used by:**    | Multi-Region Systems, High Availability                     |                 |
| **Related:**    | Multi-Region Architecture, Active-Active, Disaster Recovery |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Single data center in us-east. Users in Japan experience 150ms latency (slow). If DC goes down, all data lost (no geographic backup).

**THE BREAKING POINT:**
Global users want low latency. Regulators require geographic redundancy. Must replicate data across regions.

**THE INVENTION MOMENT:**
"Copy data to multiple geographic regions continuously. Users connect to nearest region (low latency). If one region fails, data survives in others."

---

### 📘 Textbook Definition

**Geo-Replication:** Real-time synchronization of data across multiple geographically separated data centers. Improves read latency (users connect to nearest DC) and provides disaster recovery (data survives DC outage).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Copy data to multiple regions in real-time. Users in each region get low latency. Data survives if any region fails.

**One analogy:**

> Library books: (1) copy books to branches in SF, NYC, Tokyo (geo-replication), (2) users check out from nearest branch (low latency), (3) if SF burns down, books still exist in NYC/Tokyo (disaster recovery).

**One insight:**
Geo-replication trades write latency for read latency and disaster recovery.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Data exists in multiple geographic locations
2. Replication takes time (network latency between regions)
3. Consistency across regions requires coordination
4. Users read from nearest region (low latency), but writes may require central coordination

**STRATEGIES:**

1. **Async Replication**: Write in primary region, replicate to others asynchronously (fast writes, eventual consistency)
2. **Sync Replication**: Write waits for replication (slow writes, stronger consistency)
3. **Read Replicas**: Each region has copy, can handle reads locally (scale reads globally)
4. **Multi-Master**: All regions can write, conflict resolution required

**THE TRADE-OFFS:**
**Gain:** Global low latency. Disaster recovery. Scale reads geographically.

**Cost:** Network bandwidth (replicating between regions). Write complexity (conflicts in multi-master). Operational complexity (managing multiple regions).

---

### 🧪 Thought Experiment

**SETUP:**
Photo sharing app. Primary DB in us-east. Users in SF (us-west), Tokyo, London.

**Without Geo-Replication:**

- Tokyo user uploads photo: sent to us-east (100ms latency one-way)
- Photo stored, but user sees 200ms delay
- Tokyo user views: request to us-east (100ms), response (100ms), total 200ms
- If us-east fails, Tokyo user can't see photos

**With Geo-Replication:**

- Tokyo user uploads: sent to us-west-tokyo region (10ms latency, local)
- Replicated to us-east and us-west asynchronously
- Tokyo user views: local region (10ms latency)
- If us-east fails, us-west and Tokyo regions survive (photos still accessible)

**Trade-off:**
Write is still sent to primary eventually, but users see low latency for reads. Write consistency: eventual (might take 1-5 sec for all regions to sync).

---

### 🧠 Mental Model / Analogy

> Newspaper print: (1) Editorial in NYC, (2) Articles sent to printing plants in LA, Chicago, Miami. (3) Each plant prints local edition (geo-replication). (4) Readers pick up nearest edition (low latency). (5) If NYC office burns, prints from other cities still available (disaster recovery).

- "Editorial office" → primary DC
- "Printing plants" → replica regions
- "Print editions" → replicated data
- "Nearest edition" → read from geographically close region
- "Burn and survive" → disaster recovery

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Data exists in multiple regions. Users read from nearby region (fast). Data backed up geographically (survives DC failure).

**Level 2 — How to use it (junior developer):**
Database has primary in us-east, replicas in us-west and eu-west. App reads from nearest region. Writes go to primary (replicated to replicas). If one region down, app reads from other regions.

**Level 3 — How it works (mid-level engineer):**
Implement replication streaming between regions (network link). Use async for speed (users don't wait) or sync for consistency (users wait). Monitor replication lag (should be < 1 second). Handle reads from nearest region (via DNS or load balancer routing).

**Level 4 — Why it was designed this way (senior/staff):**
Geo-replication emerged from need for: (1) global low latency (reduce user-perceived delay), (2) disaster recovery (survive DC outage), (3) scale reads globally. Google, Netflix use geo-replication. Tradeoff: write latency (writes replicate) vs. read latency (local reads). Async replication common (strong read scaling, some write delay acceptable). Conflicts arise if multiple regions accept writes (multi-master): need CRDTs or event sourcing to resolve.

---

### ⚙️ How It Works (Mechanism)

Geo-replication architecture:

```
SETUP:
  [DC-US-EAST] (Primary)
       ↓ (replication stream)
       ├→ [DC-US-WEST]
       ├→ [DC-EU-WEST]
       └→ [DC-ASIA-TOKYO]

  Each DC has full copy of data

WRITE FLOW (Async):
  1. User writes to nearest region (but primary receives)
  2. Write goes to DC-US-EAST (primary)
  3. Write committed locally
  4. User gets response (instant)
  5. Replication begins (asynchronously) to other regions
  6. After ~1-5 sec, other regions have copy

READ FLOW (Local):
  1. User in Tokyo reads
  2. DNS/LB routes to DC-ASIA-TOKYO
  3. Read served locally (10ms latency, not 100ms)
  4. Data might be slightly stale (replication lag)

REPLICATION MECHANISM:
  Binary log replication (MySQL style):
    - Primary writes to binary log
    - Replicas pull/stream log entries
    - Apply changes to local database
    - Lag: time to transmit + apply

  Document sync (MongoDB style):
    - Primary keeps changelog
    - Replicas pull changelog
    - Merge changes to local collection

  Both have network latency + processing lag

DISASTER: PRIMARY DC FAILS
  - US-EAST DC disappears
  - Other regions (US-WEST, EU-WEST, ASIA-TOKYO) still have data
  - Users in Tokyo can still read from ASIA-TOKYO
  - Writes must be rerouted to new primary (one of replicas promoted)
  - Some writes in flight (not yet replicated) are lost
  - Data loss = replication lag at failure time
```

**Geographic Replication Topology:**

```
Star Topology (Common):
  [Primary] ──→ [Replica-1]
      ↓
      ├→ [Replica-2]
      └→ [Replica-3]
  Pros: Simple, fast primary writes
  Cons: Primary is bottleneck for writes

Multi-Master Topology (Complex):
  [Region-A] ←→ [Region-B]
      ↓              ↓
  [Region-C] ←→ [Region-D]
  Pros: Writes work in any region
  Cons: Conflicts possible, complex consistency

Hierarchical Topology (Balanced):
  [Primary-US-EAST]
      ↓
  [Replica-US-WEST] → [Replica-EU-WEST]
      ↓
  [Replica-ASIA-TOKYO]
  Pros: Balance between simplicity and distribution
  Cons: Replication lag increases (multi-hop)
```

---

### 💻 Code Example

**Example 1 — Cross-Region Replication (AWS RDS):**

```terraform
# Primary database (us-east-1)
resource "aws_db_instance" "primary" {
  identifier       = "myapp-primary"
  engine           = "mysql"
  instance_class   = "db.t3.medium"
  allocated_storage = 100
  region           = "us-east-1"

  # Backup for disaster recovery
  backup_retention_period = 7
  backup_window           = "03:00-04:00"

  # Multi-AZ for high availability
  multi_az = true
}

# Cross-region read replica (us-west-2)
resource "aws_db_instance" "replica_us_west" {
  identifier             = "myapp-replica-us-west"
  replicate_source_db    = aws_db_instance.primary.identifier
  skip_final_snapshot    = true
  publicly_accessible    = false

  # Note: created in different region automatically
}

# Cross-region read replica (eu-west-1)
resource "aws_db_instance" "replica_eu_west" {
  identifier             = "myapp-replica-eu-west"
  replicate_source_db    = aws_db_instance.primary.identifier
  skip_final_snapshot    = true

  # Monitoring replication lag
  tags = {
    Name = "replica-eu-west"
  }
}
```

**Example 2 — Monitoring Replication Lag:**

```python
import boto3
from datetime import datetime

def check_replication_lag(primary_endpoint, replica_endpoint):
    """Monitor replication lag between regions"""

    import pymysql

    # Get primary binlog position
    conn_primary = pymysql.connect(host=primary_endpoint)
    cursor = conn_primary.cursor()
    cursor.execute("SHOW MASTER STATUS;")
    primary_log = cursor.fetchone()
    primary_file, primary_pos = primary_log[0], primary_log[1]

    # Get replica status
    conn_replica = pymysql.connect(host=replica_endpoint)
    cursor_replica = conn_replica.cursor()
    cursor_replica.execute("SHOW SLAVE STATUS;")
    slave_status = cursor_replica.fetchone()
    slave_file, slave_pos = slave_status[5], slave_status[6]

    # Calculate lag (simplified)
    if primary_file == slave_file:
        lag_bytes = primary_pos - slave_pos
    else:
        lag_bytes = "unknown (on different log file)"

    print(f"Replication Lag: {lag_bytes} bytes")

    # Alert if lag > 10MB (replication falling behind)
    if isinstance(lag_bytes, int) and lag_bytes > 10 * 1024 * 1024:
        print("⚠️  ALERT: Replication lag exceeding threshold!")
        return False

    return True

# Continuous monitoring
while True:
    check_replication_lag(
        primary_endpoint="myapp-primary.us-east-1.rds.amazonaws.com",
        replica_endpoint="myapp-replica-us-west.us-west-2.rds.amazonaws.com"
    )
    time.sleep(60)  # Check every minute
```

**Example 3 — Read from Nearest Region:**

```python
from geolite2 import geolite2
import pymysql

class GeoRoutedDatabase:
    def __init__(self):
        # Database endpoints by region
        self.endpoints = {
            'us': "myapp-us-west.rds.amazonaws.com",
            'eu': "myapp-eu-west.rds.amazonaws.com",
            'asia': "myapp-asia-tokyo.rds.amazonaws.com",
        }
        self.connections = {}

    def get_user_region(self, user_ip):
        """Determine user's region from IP"""
        try:
            match = geolite2.reader().get(user_ip)
            continent = match['continent']['code']
            if continent in ['NA', 'SA']:
                return 'us'
            elif continent in ['EU', 'AF']:
                return 'eu'
            elif continent in ['AS', 'OC']:
                return 'asia'
        except:
            pass
        return 'us'  # Default to US

    def get_connection(self, region):
        """Get connection to regional database"""
        if region not in self.connections:
            self.connections[region] = pymysql.connect(
                host=self.endpoints[region],
                user='app',
                password='secret',
                database='myapp'
            )
        return self.connections[region]

    def read(self, user_ip, query):
        """Read from nearest region"""
        region = self.get_user_region(user_ip)
        conn = self.get_connection(region)
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

# Usage
geo_db = GeoRoutedDatabase()

# User in Tokyo
result = geo_db.read('210.156.67.89', 'SELECT * FROM users WHERE id = 123')
# Routed to asia-tokyo region (low latency)

# User in London
result = geo_db.read('109.146.9.67', 'SELECT * FROM users WHERE id = 123')
# Routed to eu-west region (low latency)
```

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                              |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| "Geo-replication guarantees zero data loss"      | No. Async replication can lose data in flight (between regions). Sync replication loses write speed. |
| "All regions are equal"                          | No. Primary region has authoritative data. Replicas are read-only (in most setups).                  |
| "Geo-replication is automatic failover"          | Incomplete. Geo-replication provides data backup. Automatic failover requires additional automation. |
| "Writes are as fast as reads in geo-replication" | No. Writes must go to primary (may have latency). Reads from local replica (fast).                   |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Replication Lag So High It Defeats DR**

**Symptom:**
Primary DC fails. RPO target was 5 minutes. But replication lag = 30 minutes. 25 minutes of data lost.

**Root Cause:**
Network between regions congested. Replication streaming backlogged.

**Diagnostic Command:**

```bash
# Monitor replication lag continuously
watch -n 1 'mysql -h replica.aws.com -e "SHOW SLAVE STATUS\G" | grep Seconds_Behind_Master'
```

**Prevention:**
Monitor lag continuously. Alert if > RPO threshold. Provision network capacity for replication.

---

**Failure Mode 2: Replica Out of Sync (Silent Failure)**

**Symptom:**
Replication appears healthy. But data diverges (corruption, bugs). Failover promotes replica with bad data.

**Root Cause:**
Replication lag masked issue. Queries on replica fail silently. Not detected until failover.

**Diagnostic Command:**

```bash
# Periodic consistency check
mk-table-checksum --checksum-algorithm=ACCUM h=primary && h=replica
# Compare checksums, alert if different
```

**Prevention:**
Periodic data consistency checks. Test failover regularly (actual promotion, verify data).

---

### 🔗 Related Keywords

**Prerequisites:**

- `Replication`, `Distributed Systems`, `Disaster Recovery`

**Builds On This:**

- `Multi-Region Architecture`, `Active-Active`, `Geo-Sharding`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Real-time data sync across            │
│              │ geographic regions                     │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Users far from single DC have high    │
│ SOLVES       │ latency; no DR if DC fails            │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Trades write latency for read latency │
│              │ and disaster recovery                  │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Local reads globally, data survives  │
│              │ if any region fails."                 │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have geo-replication with 1-second lag. Users write. 0.5 seconds later, a different user (in different region) reads. What data do they see?

**Q2.** Multi-region write: Users in US and EU can both write to same document. Conflict possible. How do you resolve? Who wins?
