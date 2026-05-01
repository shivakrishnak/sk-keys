---
layout: default
title: "Geo-Replication"
parent: "System Design"
nav_order: 698
permalink: /system-design/geo-replication/
number: "698"
category: System Design
difficulty: ★★★
depends_on: "Active-Passive, Active-Active, Disaster Recovery"
used_by: "Multi-Region Architecture"
tags: #advanced, #reliability, #distributed, #database, #architecture
---

# 698 — Geo-Replication

`#advanced` `#reliability` `#distributed` `#database` `#architecture`

⚡ TL;DR — **Geo-Replication** replicates data across geographically separated data centres or cloud regions — reducing read latency for global users, enabling cross-region DR, and keeping data local for compliance.

| #698            | Category: System Design                          | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Active-Passive, Active-Active, Disaster Recovery |                 |
| **Used by:**    | Multi-Region Architecture                        |                 |

---

### 📘 Textbook Definition

**Geo-Replication** (geographically distributed replication) is the continuous synchronisation of data across data centres or cloud regions in different geographic locations. It serves three primary purposes: (1) **Disaster Recovery** — maintaining a geographically separate copy of data for regional outage survival; (2) **Latency Reduction** — serving reads from a region close to the user to reduce round-trip time; (3) **Data Residency** — keeping data within specific geographic boundaries for regulatory compliance (GDPR, data sovereignty). Geo-Replication can be synchronous (commits blocked until remote region acknowledges — zero data loss, higher write latency) or asynchronous (commits proceed immediately, remote region updated in background — minimal write latency impact, small RPO). Systems offering geo-replication: AWS Aurora Global, Azure Cosmos DB, Google Spanner, CockroachDB, MongoDB Atlas, Redis Enterprise.

---

### 🟢 Simple Definition (Easy)

Geo-Replication: automatically keep copies of your data in multiple geographic locations. User in Tokyo reads from Tokyo data centre (fast). User in London reads from London data centre (fast). If your US data centre burns down, Europe and Asia copies survive. Three reasons: performance (local reads), resilience (regional backup), compliance (data stays in a country).

---

### 🔵 Simple Definition (Elaborated)

Without geo-replication: all users worldwide read from us-east-1 database. User in Sydney: 200ms latency (roundtrip to US). With geo-replication: read replica in ap-southeast-2 (Sydney) receives updates from us-east-1 continuously. Sydney users: read locally (10ms). Writes still go to us-east-1 primary (one authoritative source). Synchronous reads: slightly stale (100-500ms replication lag). The trade-off: faster reads for global users, at the cost of possible slight staleness.

---

### 🔩 First Principles Explanation

**Geo-replication: the distance-latency problem:**

```
SPEED OF LIGHT CONSTRAINT:
  Network latency = physical distance / speed of light × overhead factor

  New York → Sydney: ~16,000 km
  Speed of light in fibre: ~200,000 km/s
  Minimum RTT: (16,000 × 2) / 200,000 = 160ms
  Actual RTT: 180-220ms (routing, switches, processing overhead)

  Without geo-replication:
    Sydney user reads from New York database: 200ms per query
    Page load with 10 database calls: 2,000ms (2 seconds) just from latency
    Unacceptable for interactive applications

  With geo-replication (read replica in Sydney):
    Sydney user reads from Sydney replica: 5-15ms
    Page load: 50-150ms total

REPLICATION LAG:
  The price of geo-replication: reads may be slightly stale.

  Write at T=0 in us-east-1:
  → Write replicated to ap-southeast-2 at T+100ms (replication lag)

  Sydney user reads at T+50ms:
  → Reads from Sydney replica
  → Sydney replica doesn't have the write yet (it arrives at T+100ms)
  → Sydney user sees old data for 50ms

  Is this acceptable?
  - Product catalogue prices: yes (50ms stale is fine)
  - User account balance: depends (financial applications may need strong consistency)
  - Social media posts: yes
  - Medical records: NO (must always read latest)

  For read-your-writes: see Session Affinity / Sticky Sessions
  (route writes and immediately following reads to same region)

GEO-REPLICATION MODES:

  ASYNC (default for most databases):
    Primary: commits write → immediately returns success → replicates in background
    Replication lag: 10ms (same continent) to 300ms (cross-ocean)
    RPO: seconds (lag at time of failure)
    Write latency: unaffected

    Use: most web applications, social media, e-commerce, content platforms

  SYNCHRONOUS:
    Primary: commits write → waits for remote region to confirm → returns success
    Replication lag: 0 (all committed writes immediately in all regions)
    RPO: 0 (zero data loss)
    Write latency: increased by remote region RTT (100-300ms cross-ocean)

    Use: financial transactions requiring zero data loss across regions
    Usually impractical for global deployments (300ms per write too slow)

  SEMI-SYNCHRONOUS:
    Write must be acknowledged by at least ONE remote region (not all).
    Better durability than async. Less latency than fully synchronous.
    MySQL/PostgreSQL: synchronous_standby_names = 'ANY 1 (region-a, region-b)'

    Write latency: RTT to NEAREST remote region (not farthest)
    RPO: 0 for the acknowledged region; seconds for others

MULTI-MASTER GEO-REPLICATION:
  All regions: accept writes
  Conflict resolution required (see Active-Active keyword)

  DynamoDB Global Tables:
    All regions: read + write
    Conflict resolution: Last Write Wins (timestamp-based)
    Lag: typically < 1 second between regions

  Google Cloud Spanner:
    Global distributed database with external consistency
    All writes serialised globally via TrueTime API
    Write latency: proportional to distance between replicas
    "True" global consistency without conflict resolution needed

DATA RESIDENCY AND COMPLIANCE:
  GDPR (EU): personal data of EU residents must not be transferred
  outside EU without adequate protections.

  Without geo-replication:
    EU users' data in us-east-1 → potential GDPR violation

  With geo-replication + data partitioning:
    EU users: data written only to eu-west-1 or eu-central-1
    EU region: never replicates EU personal data to non-EU regions
    Non-EU regions: can replicate non-personal, anonymised data freely

  Implementation:
    User account creation: detect region → write to local regional shard
    Regional sharding: EU users always in EU database, never replicated out
    Anonymised analytics: replicated globally (not personal data)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Geo-Replication:

- Global users: high latency (200ms+ for trans-continental reads)
- Regional outage: all data in one region → catastrophic data loss risk
- Compliance: data may cross borders violating GDPR / data sovereignty laws

WITH Geo-Replication:
→ Local reads: <15ms for users in any replicated region
→ DR: data survives complete regional failure
→ Compliance: data stays within required geographic boundaries

---

### 🧠 Mental Model / Analogy

> A global newspaper with printing presses in multiple cities. The master layout (primary) is in New York. Each night, the layout is transmitted to London, Tokyo, and Sydney printing presses (replication). Local readers get the paper printed locally (fast, cheap delivery). If the New York HQ burns down, London/Tokyo/Sydney have the previous day's layout (DR). Each region prints for local compliance (some stories only in EU edition — data residency). The "paper" is your data; "printing presses" are regional replicas; "transmission" is replication.

"New York master layout" = primary database region
"Transmitting to regional presses" = asynchronous replication
"Local readers get local paper" = read from regional replica (low latency)
"HQ burns down but regional presses survive" = geo-replication for DR
"EU-only stories" = data residency / GDPR compliance

---

### ⚙️ How It Works (Mechanism)

**AWS Aurora Global Database — geo-replication setup:**

```
AURORA GLOBAL DATABASE:
  Primary cluster: us-east-1 (read + write)
  Secondary clusters: eu-west-1, ap-southeast-1 (read only, < 1s lag)

  Replication: storage level (not log shipping) → very low lag
  Failover to secondary: managed in < 60 seconds

Terraform:
resource "aws_rds_global_cluster" "orders" {
  global_cluster_identifier = "orders-global"
  engine                    = "aurora-postgresql"
  engine_version            = "15.4"
  database_name             = "orders"
  deletion_protection       = true
}

# Primary cluster (us-east-1):
resource "aws_rds_cluster" "primary" {
  provider                  = aws.us-east-1
  cluster_identifier        = "orders-primary"
  engine                    = "aurora-postgresql"
  engine_version            = "15.4"
  global_cluster_identifier = aws_rds_global_cluster.orders.id
  master_username           = "admin"
  manage_master_user_password = true
  db_subnet_group_name      = aws_db_subnet_group.primary.name
  vpc_security_group_ids    = [aws_security_group.db.id]
}

# Secondary (DR + local reads, eu-west-1):
resource "aws_rds_cluster" "eu_secondary" {
  provider                  = aws.eu-west-1
  cluster_identifier        = "orders-eu-secondary"
  engine                    = "aurora-postgresql"
  engine_version            = "15.4"
  global_cluster_identifier = aws_rds_global_cluster.orders.id
  db_subnet_group_name      = aws_db_subnet_group.eu.name
  # Secondary: automatically receives replication from primary
  # Read-only until promoted (for DR failover)
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Active-Passive           Active-Active
(single active region)   (all regions active)
        │                       │
        └───────────┬───────────┘
                    ▼ (the data layer for both patterns)
              Geo-Replication ◄──── (you are here)
              (continuously sync data across regions)
                    │
                    ▼
          Multi-Region Architecture
          (the full pattern: compute + data + traffic)
```

---

### 💻 Code Example

**Application-level geo-aware read routing:**

```java
@Configuration
public class DatabaseRoutingConfig {
    // Route reads to regional replica, writes to primary
    // AbstractRoutingDataSource: selects datasource per-request

    @Bean
    public DataSource routingDataSource() {
        RegionAwareRoutingDataSource routing = new RegionAwareRoutingDataSource();

        Map<Object, Object> sources = new HashMap<>();
        sources.put("PRIMARY", primaryDataSource());       // us-east-1 (writes)
        sources.put("EU_REPLICA", euReplicaDataSource());  // eu-west-1 (EU reads)
        sources.put("APAC_REPLICA", apacReplicaDataSource()); // ap-southeast-1

        routing.setTargetDataSources(sources);
        routing.setDefaultTargetDataSource(primaryDataSource());
        return routing;
    }
}

public class RegionAwareRoutingDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        String region = System.getenv("AWS_REGION");

        if (TransactionSynchronizationManager.isCurrentTransactionReadOnly()) {
            // Read operation: route to nearest regional replica
            return switch (region) {
                case "eu-west-1", "eu-central-1" -> "EU_REPLICA";
                case "ap-southeast-1", "ap-northeast-1" -> "APAC_REPLICA";
                default -> "PRIMARY";  // default: primary (us-east-1 or unknown)
            };
        }

        // Write operation: always go to primary
        return "PRIMARY";
    }
}

// Usage:
@Transactional(readOnly = true)  // → routed to regional replica
public List<Product> getProducts() { ... }

@Transactional                    // → routed to primary
public Order createOrder(OrderRequest req) { ... }
```

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                                                        |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Geo-replication guarantees consistent reads across regions | Asynchronous geo-replication means reads from regional replicas may be 10-500ms behind the primary. If a user writes data and immediately reads from a different region, they may see stale data. Applications must account for this and implement read-your-writes consistency where required |
| More regions always means better performance               | More regions means data must be replicated to more places, increasing replication overhead and complexity. For most applications, 2-3 strategic regions cover the majority of users. Adding a 6th region for 0.5% of traffic is rarely worth the operational overhead                          |
| Geo-replication replaces backups                           | Replication propagates changes, including mistakes. If a developer drops a table, the DROP is replicated to all regions within seconds. Backups with point-in-time recovery are essential regardless of geo-replication                                                                        |
| All regions should accept writes in geo-replication        | Write-accepting multi-region databases (Active-Active) require conflict resolution, which adds complexity. For most applications: single write region + multiple read regions (Active-Passive geo-replication) is simpler, correct, and sufficient                                             |

---

### 🔥 Pitfalls in Production

**GDPR violation via accidental cross-region replication:**

```
PROBLEM: EU user data replicated to non-EU regions accidentally

  Setup: Aurora Global Database
  Primary: eu-west-1 (for EU market)
  Secondary: us-east-1 (for US market) ← MISTAKE

  EU personal data: name, email, address → stored in eu-west-1
  Aurora Global: replicates ALL data to us-east-1 automatically

  Result: EU personal data in us-east-1 → GDPR violation
  Fine exposure: up to 4% of annual global turnover (GDPR Article 83)

CORRECT ARCHITECTURE for GDPR compliance:

  EU users → eu-west-1 cluster (EU data never leaves EU)
  US users → us-east-1 cluster (US data)

  Option A: Separate, non-replicated databases per region
    EU DB: eu-west-1 only. US DB: us-east-1 only.
    Shared data (non-personal): replicated freely (product catalogue, etc.)
    EU personal data: stays in eu-west-1. Never replicated.

  Option B: Logical data partitioning + geo-fencing at application layer
    Database: one global database schema
    Data access layer: region tag on every personal data record
    Replication: row-level filter → replicate only non-personal data cross-region
    EU personal data rows: region_tag='EU' → not replicated to non-EU

  Option C: DynamoDB Global Tables with attribute-level encryption
    EU personal data: encrypted with EU-only KMS key (stored in eu-central-1)
    Global replication: ciphertext replicated globally (data is encrypted)
    Only EU region: has KMS key → can decrypt → GDPR-compliant (data is not readable outside EU)

  COMPLIANCE CHECKLIST for geo-replication:
  - [ ] Data classification: which fields are personal data?
  - [ ] Geographic routing: EU users always write to EU region?
  - [ ] Replication scope: does any personal data cross regions?
  - [ ] DPA (Data Processing Agreement) with cloud provider?
  - [ ] Encryption: personal data encrypted with region-local keys?
  - [ ] Audit logging: track all access to personal data per region?
```

---

### 🔗 Related Keywords

- `Active-Passive` — most common geo-replication pattern: one write primary, many regional read replicas
- `Active-Active` — all regions accept writes; requires conflict resolution
- `Disaster Recovery` — geo-replication is the data layer of DR
- `Multi-Region Architecture` — geo-replication + multi-region compute + traffic routing
- `RTO / RPO` — geo-replication determines achievable RPO (depends on replication lag)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Replicate data across geographic regions: │
│              │ DR + low latency reads + data residency   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Global user base; cross-region DR; GDPR/  │
│              │ data sovereignty compliance requirements  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Strong read consistency required; GDPR    │
│              │ without partitioning (accidental transfer)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Global newspaper presses: NY masters the │
│              │  layout; London and Tokyo print locally." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Multi-Region Architecture → Consistent    │
│              │ Hashing → CRDT                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your application serves users in the US, EU, and Japan. You use Aurora Global Database with primary in us-east-1 and secondaries in eu-west-1 and ap-northeast-1. A user in Germany creates a post at T=0 (write goes to us-east-1). They immediately refresh their feed (read). With 120ms replication lag to eu-west-1, what do they see? Design a "read-your-writes" consistency strategy that ensures the user sees their own post immediately, without requiring synchronous cross-region writes. What are the implementation trade-offs?

**Q2.** You are designing geo-replication for a healthcare SaaS. Requirements: (a) HIPAA — US patient data must not leave the US, (b) GDPR — EU patient data must not leave the EU, (c) Disaster recovery RTO=30 minutes for each region, (d) Low latency reads for doctors in each region. Design the complete database architecture (which databases, which regions, what replication topology) and explain how you ensure both compliance boundaries and DR capability simultaneously.
