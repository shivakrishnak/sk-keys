---
layout: default
title: "Redundancy / Failover"
parent: "System Design"
nav_order: 694
permalink: /system-design/redundancy-failover/
number: "694"
category: System Design
difficulty: ★★☆
depends_on: "RTO / RPO, Active-Passive"
used_by: "Active-Active, Disaster Recovery"
tags: #intermediate, #reliability, #distributed, #architecture, #foundational
---

# 694 — Redundancy / Failover

`#intermediate` `#reliability` `#distributed` `#architecture` `#foundational`

⚡ TL;DR — **Redundancy** eliminates single points of failure by duplicating critical components; **Failover** is the automatic or manual process of switching to a redundant system when the primary fails.

| #694            | Category: System Design          | Difficulty: ★★☆ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | RTO / RPO, Active-Passive        |                 |
| **Used by:**    | Active-Active, Disaster Recovery |                 |

---

### 📘 Textbook Definition

**Redundancy** is the practice of duplicating critical components, services, or resources so that a backup is available when the primary fails. Redundancy eliminates single points of failure (SPOFs) — any component whose failure causes the entire system to fail. Redundancy types: **hardware redundancy** (RAID, dual PSUs, redundant network paths), **software redundancy** (multiple service replicas), **geographic redundancy** (multi-region), and **data redundancy** (replication, backups). **Failover** is the process of automatically or manually switching from a failed primary component to a redundant standby. **Automatic failover** (e.g., RDS Multi-AZ, Kubernetes liveness probes, keepalived) detects failure and switches within seconds. **Manual failover** requires human intervention, increasing RTO. The goal of redundancy + failover combined is: achieving high availability by ensuring that no single failure event causes a user-visible outage.

---

### 🟢 Simple Definition (Easy)

Redundancy = having a spare. Failover = using the spare when the primary breaks. A plane with two engines: the second engine is redundancy. If engine 1 fails, the plane flies on engine 2 — that's failover. The combination ensures the plane reaches its destination even with one engine failure.

---

### 🔵 Simple Definition (Elaborated)

A single-server database is a SPOF: if it crashes, the whole system is down. Add a standby replica (redundancy): the replica mirrors all data. When the primary crashes, an automated health check detects the failure and promotes the replica to primary (failover). Users may see a brief pause (seconds to minutes) but the service resumes. Without redundancy: MTTR = time to provision new hardware + restore backup (hours). With redundancy + auto failover: MTTR = seconds.

---

### 🔩 First Principles Explanation

**Single Points of Failure (SPOFs) and how redundancy eliminates them:**

```
IDENTIFYING SPOFS — trace every critical path:

  User → DNS → Load Balancer → App Server → Database → Storage

  Each arrow is a potential SPOF:

  1. DNS: single DNS provider → all names unresolvable if provider fails
     FIX: multiple DNS providers (Route53 + Cloudflare), NS record redundancy

  2. Load Balancer: single instance → no traffic routing if LB fails
     FIX: Active-passive LB pair (keepalived VIP), or cloud-managed LB (inherently redundant)

  3. App Server: single instance → one crash = full outage
     FIX: Multiple instances behind LB + health checks → auto-replacement

  4. Database: single instance → most common SPOF in architectures
     FIX: Multi-AZ (RDS), Sentinel/Cluster (Redis), replica set (MongoDB)

  5. Storage: single disk → RAID for local; S3 (11-9s durability) for cloud
     FIX: RAID 1/5/6, cloud object storage with cross-region replication

AVAILABILITY FROM REDUNDANCY:

  Single component: availability = A
  Two components (active-passive): availability ≈ 1 - (1-A)^2

  Example: each component = 99% available
  Single:          99.00%
  Two (A-P):       1 - (0.01)^2 = 99.99%
  Three:           1 - (0.01)^3 = 99.9999%

  Important caveat: the FAILOVER mechanism itself must be reliable.
  If failover logic has a bug or requires manual intervention (slow MTTR),
  the theoretical availability gain is not realised.

FAILOVER TYPES:

  AUTOMATIC FAILOVER (preferred):
    Health check detects failure → redirects traffic → no human needed.

    Kubernetes: liveness probe fails → kubelet restarts pod
      livenessProbe:
        httpGet:
          path: /actuator/health/liveness
          port: 8080
        failureThreshold: 3
        periodSeconds: 10
    → Pod replaced within 30 seconds of failure

    RDS Multi-AZ: primary fails → standby promoted automatically
    → DNS endpoint updated → application reconnects in ~90 seconds

    keepalived (Linux VRRP): LB1 fails → LB2 takes over Virtual IP
    → No DNS change needed (VIP stays the same)
    → Failover: <1 second

  MANUAL FAILOVER (degraded option):
    Human detects failure, executes runbook, promotes standby.
    RTO: 30 minutes to hours (human response time + execution)
    When to use: when automatic failover risks data corruption/split-brain
    Example: database with async replication — auto-promote may lose data

  GRACEFUL vs. FORCED FAILOVER:
    GRACEFUL: primary drains connections, replication confirmed,
              then promotion. Data consistent. Takes longer.
    FORCED: immediate promotion regardless of replication lag.
            Faster but may lose in-flight transactions (RPO trade-off).

FAILOVER TESTING:

  Chaos engineering: deliberately trigger failovers in production.
  Netflix Chaos Monkey: terminates random EC2 instances.
  AWS Fault Injection Simulator (FIS): controlled failure injection.

  Without testing:
  - Failover scripts have bugs (discovered during actual outage)
  - Operators unfamiliar with failover procedure (slow manual execution)
  - Hidden dependencies not covered by redundancy (discovered mid-crisis)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Redundancy + Failover:

- Single component failure = complete system outage
- MTTR = time to detect + provision replacement + restore data
- Every component is a ticking time bomb (hardware fails, software crashes)

WITH Redundancy + Failover:
→ Single component failure handled automatically, invisibly to users
→ MTTR: seconds (auto failover) vs. hours (manual recovery)
→ Maintenance: rolling updates without downtime (take one component down, failover handles traffic)

---

### 🧠 Mental Model / Analogy

> Redundancy and failover in electrical power. A hospital has a generator (redundancy) that activates automatically when the main power fails (failover). The generator sits idle while mains power works — pure cost, no benefit on a good day. But when mains power fails (SPOF), the generator kicks in within seconds. The hospital stays operational. Without the generator (no redundancy), power failure = lights out + equipment shutdown. The cost of the generator is justified by the criticality of hospital operations.

"Main power" = primary system component
"Generator" = redundant standby component
"Automatic generator activation" = auto failover
"Transfer switch" = failover detection and switching mechanism

---

### ⚙️ How It Works (Mechanism)

**HAProxy health checks + automatic backend failover:**

```
HAProxy configuration — automatic failover between primary and replica:

frontend db_proxy
    bind *:5432
    default_backend postgres_pool

backend postgres_pool
    balance first           # send all to first available server
    option tcp-check        # TCP health check
    tcp-check connect

    # Primary (normal target)
    server pg-primary 10.0.1.1:5432 check inter 5s fall 2 rise 3
    # pg-primary:
    #   check: health check enabled
    #   inter 5s: check every 5 seconds
    #   fall 2: mark DOWN after 2 consecutive failures (10s to detect failure)
    #   rise 3: mark UP after 3 consecutive successes (15s to return traffic)

    # Standby (only used if primary DOWN)
    server pg-standby 10.0.1.2:5432 backup check inter 5s fall 2 rise 3
    # backup: only receives traffic when all non-backup servers are DOWN

# Failover flow:
# T+00: pg-primary health check fails (2nd consecutive failure)
# T+10: pg-primary marked DOWN by HAProxy
# T+10: pg-standby (backup) starts receiving traffic
# T+00 to T+10: 10 seconds of failed/dropped connections
# T+10+: all connections to pg-standby (note: standby may be read-only replica)
#        application must handle reconnection; standby may need manual promotion
```

---

### 🔄 How It Connects (Mini-Map)

```
Single Point of Failure (SPOF)
(any component whose failure = system failure)
        │
        ▼ (eliminate via duplication)
Redundancy ◄──── (you are here — the "having a spare" part)
        │
        ▼ (automated switching to spare)
Failover ◄──── (you are here — the "using the spare" part)
        │
        ├── Active-Passive (one standby, one primary)
        ├── Active-Active (both actively serving)
        └── Disaster Recovery (cross-region failover)
```

---

### 💻 Code Example

**AWS Route53 health check + DNS failover:**

```python
import boto3

route53 = boto3.client('route53')

# 1. Create health check for primary endpoint:
health_check = route53.create_health_check(
    CallerReference='primary-health-check-001',
    HealthCheckConfig={
        'IPAddress': '10.0.1.100',
        'Port': 443,
        'Type': 'HTTPS',
        'ResourcePath': '/actuator/health',
        'RequestInterval': 10,   # check every 10 seconds
        'FailureThreshold': 3,   # failover after 3 failures (30 seconds)
        'FullyQualifiedDomainName': 'api.primary.example.com',
    }
)
health_check_id = health_check['HealthCheck']['Id']

# 2. Primary DNS record (active while healthy):
route53.change_resource_record_sets(
    HostedZoneId='ZXXX',
    ChangeBatch={'Changes': [{
        'Action': 'CREATE',
        'ResourceRecordSet': {
            'Name': 'api.example.com',
            'Type': 'A',
            'SetIdentifier': 'primary',
            'Failover': 'PRIMARY',              # this is the PRIMARY record
            'TTL': 60,
            'ResourceRecords': [{'Value': '10.0.1.100'}],
            'HealthCheckId': health_check_id    # failover if unhealthy
        }
    }]}
)

# 3. Secondary (DR) DNS record (used only if primary health check fails):
route53.change_resource_record_sets(
    HostedZoneId='ZXXX',
    ChangeBatch={'Changes': [{
        'Action': 'CREATE',
        'ResourceRecordSet': {
            'Name': 'api.example.com',
            'Type': 'A',
            'SetIdentifier': 'secondary',
            'Failover': 'SECONDARY',            # only used if primary unhealthy
            'TTL': 60,
            'ResourceRecords': [{'Value': '10.0.2.100'}],
        }
    }]}
)
# Failover: primary health check fails → Route53 returns secondary IP
# With TTL=60: clients get new IP within 60 seconds
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                                                                        |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Redundancy eliminates all downtime              | Redundancy eliminates downtime from single component failures, not all downtime. Common failure modes NOT solved by N+1 redundancy: software bugs (affect all instances simultaneously), misconfigured deployments (affect all instances), shared infrastructure failure (network, DNS, cloud region), correlated failures (all instances on same hardware rack)               |
| Active-passive wastes the standby resource      | Active-passive standby isn't entirely idle: it runs health checks, receives replication, handles monitoring. For databases, the standby actively receives replication writes. For compute, standbys can serve read traffic (read replicas). The "waste" is in unused write capacity — which is the accepted cost of fast failover                                              |
| Automatic failover is always safer than manual  | For databases with async replication, automatic failover can cause split-brain or data loss. If both primary and standby believe they're primary simultaneously: two databases accepting writes → data divergence → corruption. Manual failover with careful sequencing prevents this. AWS RDS Multi-AZ uses synchronous replication specifically to enable safe auto-failover |
| Redundancy at the component level is sufficient | System-level availability requires redundancy at EVERY layer. A redundant database does not help if the load balancer is a SPOF. The weakest redundancy link determines system availability. Systematic SPOF analysis is essential                                                                                                                                             |

---

### 🔥 Pitfalls in Production

**Split-brain: both primary and standby believe they're primary:**

```
PROBLEM: Network partition causes split-brain

  Scenario: Primary DB and Standby DB connected via network.
  Network partition at T=0: Primary and Standby can't communicate.

  Without fencing mechanism:
  T=0:  Network partition. Primary still accepting writes.
  T=30: Standby: "Primary is unreachable!" → promotes itself to primary.
  T=30: Now TWO primaries: old Primary + new Primary.
  T=30-T=60: Application writes to new Primary (via health check redirect).
             Old Primary still accepting writes from some clients (no DNS update yet).
  T=60: Network restored. Two databases with diverged data.
        Which is authoritative? Data loss + corruption inevitable.

  SPLIT-BRAIN CONSEQUENCES:
  - Double writes: order placed twice (financial impact)
  - Conflicting updates: same record updated differently in both primaries
  - Undefined merge: which version is correct?

FIX 1: STONITH (Shoot The Other Node In The Head)
  Fencing: before standby promotes, send STONITH signal to primary.
  STONITH: sends IPMI/BMC power-off command to primary hardware.
  Primary: hard-powered-off → definitively cannot accept more writes.
  Standby: now safe to promote (only one primary).

  Cloud equivalent: terminate the primary EC2 instance via API before promotion.

FIX 2: Quorum-based consensus (Raft, Paxos)
  Promotion requires acknowledgement from MAJORITY of nodes.
  With 3 nodes: need 2/3 agreement to promote.
  Network partition: partitioned side with 1 node cannot achieve quorum.
  Cannot promote → no split-brain.

  etcd, Consul, ZooKeeper, Raft-based DBs (CockroachDB, TiDB) use this.

FIX 3: Synchronous replication + epoch fencing
  PostgreSQL synchronous_standby_names:
    Write committed only when standby confirms receipt.
    On partition: primary BLOCKS (cannot commit) → cannot diverge.
    Standby: promotes safely (has all committed data).
    Trade-off: primary blocks on partition → availability reduced during partition.
```

---

### 🔗 Related Keywords

- `Active-Passive` — the simplest redundancy pattern: one active, one standby
- `Active-Active` — both instances serve traffic; more complex but more efficient
- `Disaster Recovery` — cross-region redundancy and failover at the largest scale
- `RTO / RPO` — failover speed directly determines RTO achieved
- `Load Balancing` — distributes traffic and can reroute around failed instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Redundancy: eliminate SPOFs by duplicating│
│              │ Failover: auto-switch to spare on failure  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any component whose failure causes outage;│
│              │ high-availability requirements            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Auto-failover with async replication:     │
│              │ split-brain risk — use manual or fencing  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A hospital generator: idle cost every    │
│              │  day; priceless value when power fails."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Active-Passive → Active-Active            │
│              │ → Disaster Recovery                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing a database failover system for a PostgreSQL cluster. Two options: (A) synchronous replication with automatic failover (RPO=0, write latency +50ms for replication acknowledgement, auto-promotes on primary failure), (B) asynchronous replication with manual failover (RPO=seconds, no write latency overhead, manual promotion requiring engineer on-call). Your application is a real-time bidding system (RTB) that processes 50,000 bids per second with P99 latency SLO of 10ms. Which option fits your requirements and why? Are there hybrid approaches?

**Q2.** A three-tier web application (load balancer → app servers → database) has the following individual component availabilities: LB=99.99%, App Server (single)=99.5%, Database (single)=99.9%. Calculate: (a) overall availability with no redundancy, (b) availability with 3 app servers (any one can fail), (c) availability with DB Multi-AZ (standby = 99.9% available, failover detection = 99.9% reliable). Which component provides the most improvement per dollar if each redundant component costs the same to operate?
