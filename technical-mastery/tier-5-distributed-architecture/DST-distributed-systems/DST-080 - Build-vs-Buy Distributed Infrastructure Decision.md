---
id: DST-080
title: "Build-vs-Buy Distributed Infrastructure Decision"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-004, DST-030, DST-038
used_by: []
related: DST-004, DST-030, DST-038, DST-056, DST-077
tags:
  - distributed
  - build-vs-buy
  - infrastructure
  - kafka
  - redis
  - service-mesh
  - vendor-lock-in
  - total-cost-of-ownership
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/distributed-systems/build-vs-buy/
---

⚡ TL;DR - The build-vs-buy decision for distributed
infrastructure (message queues, caches, service
meshes, consensus services, databases) should be
driven by three questions: do you have a deep
operational need that existing tools cannot satisfy
(rare), can you afford the engineering and maintenance
burden of building (most teams cannot), and what
is the exit cost if the buy choice becomes wrong
(vendor lock-in vs migration complexity); the
default answer for most teams is "buy" (use managed
services), with clear criteria for when building
or self-hosting open-source is justified.

---

### 📋 Entry Metadata

| #080 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Discovery, Distributed Queues, Event Sourcing | |
| **Used by:** | N/A (decision framework) | |
| **Related:** | Service Discovery, Distributed Queues, Event Sourcing, Observability, Migration Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT A DECISION FRAMEWORK:**
A startup with 5 engineers decides to "build their
own message queue" because Kafka "seemed too complex."
They spend 4 months building a custom at-least-once
delivery system. It lacks: topic compaction, consumer
groups, replay from offset, multi-partition ordering,
schema registry, cross-cluster replication, and
observability tooling. Every new engineer asks "why
don't we just use Kafka?" The 4 months becomes 2
years of maintenance. Every incident is the custom
queue. The engineers who built it leave. Nobody
understands it. Migration cost: 6 months.

The inverse: a startup builds a data platform on
a proprietary managed data warehouse. 3 years later:
the vendor increases pricing by 300%. The migration
cost (all SQL, all integrations, all dashboards)
is 12 months of work. Lock-in was not evaluated
at the buy decision.

Both errors result from lacking a systematic framework
for the build-vs-buy decision.

---

### 📘 Textbook Definition

**Build-vs-buy** in infrastructure context: the
decision whether to build a custom infrastructure
component, buy (use) a SaaS managed service, or
self-host an open-source solution.

**Three choices (not binary):**
1. **Build:** custom in-house implementation. Full control.
   Highest cost. Justified only for core differentiators.
2. **Buy (SaaS/PaaS):** managed cloud service
   (AWS SQS, GCP Pub/Sub, Azure Service Bus).
   Lowest operational burden. Vendor dependency.
3. **Self-host open-source:** run Kafka, Redis, etcd,
   Consul yourself. OSS license. Operational cost.
   No vendor lock-in. Requires expertise.

---

### ⏱️ Understand It in 30 Seconds

```
DECISION FRAMEWORK (four questions):

Q1: Is this component CORE to your competitive advantage?
  Yes → Consider build (rare: only Dropbox storage,
    Netflix CDN).
  No  → Buy or self-host open-source.

Q2: Does your OPERATIONAL BURDEN allow self-hosting?
  3+ dedicated SREs with expertise in the OSS tool →
    self-host.
  < 3 SREs or lacking expertise → managed service (buy).
  
Q3: What is the MIGRATION COST if you get it wrong?
  Low (standard protocol, open format):
    → Any choice (easy to swap later).
  High (proprietary API, closed format):
    → Preference for OSS with open protocols.
    → Evaluate vendor lock-in risk before buying.

Q4: What is the TOTAL COST OF OWNERSHIP (TCO)?
  TCO(build) = engineering time + maintenance + incidents.
  TCO(buy)   = licensing + cloud costs + egress fees.
  TCO(self)  = cloud infra + ops time + patches.
  Build: usually 5-10x higher than estimated initially.
  Buy: usually 3-5x lower ops cost than self-hosting.
  Self: similar to buy in ops cost if team has expertise.
  
DEFAULT: Buy (managed service) unless Q1=Yes or Q3 is high.
```

---

### 🔩 First Principles Explanation

**KAFKA vs SQS - CASE STUDY:**

```
KAFKA (self-hosted or Confluent Cloud):
  Strengths:
    - Consumer groups (multiple consumers per topic)
    - Replay from any offset (log retention)
    - Topic compaction (key-based retention)
    - 1M+ messages/second throughput
    - Multi-partition ordering guarantees
    - Schema Registry + Avro/Protobuf support
    - Exactly-once semantics (Kafka Streams, transactions)
    - Cross-cluster replication (MirrorMaker 2)
  
  Self-host operational costs:
    - ZooKeeper (or KRaft) management
    - Broker sizing (JVM tuning, heap sizing)
    - Consumer lag alerting
    - Log retention management
    - TLS/ACL setup
    - Upgrade path (Kafka versions are disruptive)
    - Typical: 1 SRE-equivalent per Kafka cluster
  
  Confluent Cloud (managed Kafka):
    - No ZooKeeper management
    - Auto-scaling partitions (limited)
    - Cost: $0.11/GB + $0.09/CKU-hour
    - For 10TB/day: ~$3000-5000/month
    - Avoids SRE cost (~$200k/year) if team lacks expertise

SQS (AWS managed):
  Strengths:
    - Zero operational burden
    - Infinite scaling (AWS-managed)
    - FIFO queues (ordering within queue)
    - Dead-letter queues
    - Per-message visibility timeout
  
  Limitations vs Kafka:
    - No consumer groups (only one consumer reads each
      message)
    - No replay (consumed messages gone)
    - No compaction
    - Max message size: 256KB
    - FIFO max throughput: 3000 TPS per queue
    - No cross-account topic subscription model
  
  Cost:
    - $0.40 per million requests
    - For 100M messages/day: ~$40/day = $1200/month
    - Very cheap at typical startup scale.

DECISION:
  Use Kafka when:
    - Need replay/event sourcing.
    - Need exactly-once processing.
    - 1M+ messages/second.
    - Multiple consumer groups for same events.
    - Have SRE capacity to operate it (or use Confluent
      Cloud).
  
  Use SQS when:
    - Simple at-least-once delivery.
    - < 100k messages/second.
    - All-in on AWS (no cross-cloud concerns).
    - Want zero operational burden.
    - No need for replay or compaction.
  
  Use neither (build) when:
    - Your message queue IS your product
      (e.g., you are building a platform like Twilio).
    - Your protocol requirements are unique
      (e.g., ultra-low latency < 100us).
```

**REDIS vs ELASTICACHE vs SELF-HOSTED - CASE STUDY:**

```
SELF-HOSTED REDIS (open-source):
  Cost: EC2 + storage.
  Control: full. Can use any Redis module.
  Operations: manual failover, Sentinel/Cluster setup,
    memory management, persistence config.
  Risk: no SLA from Redis Inc. for OSS.
  
AWS ELASTICACHE FOR REDIS:
  Cost: 2-3x more than self-hosted EC2.
    r6g.xlarge: ~$380/month vs EC2 r6g.xlarge: ~$180/month.
  Benefit: managed failover (Sentinel included),
    automated backups, CloudWatch integration,
    multi-AZ auto-failover < 30s.
  Limitation: lags Redis version (~6 months behind).
    Some Redis modules unavailable.
    No SSH access to the instance.
  
REDIS CLOUD (Redislabs SaaS):
  Cost: 3-5x ElastiCache.
  Benefit: any Redis module, active-active geo-replication,
    multi-cloud, 99.999% SLA.
  Best for: Redis-as-product (not caching only),
    large-scale.
  
DECISION:
  Startup, < 10GB data: ElastiCache (zero ops burden).
  Startup, need Redis Modules (JSON, Search, etc.): Redis
    Cloud.
  Large company, 10+ engineers, Redis expertise:
    self-hosted.
  Need active-active multi-region: Redis Enterprise.
```

**VENDOR LOCK-IN EVALUATION:**

```
LOCK-IN RISK SPECTRUM:

LOW RISK (easy to migrate away):
  - Kafka (open protocol, can migrate to
    Confluent/MSK/Redpanda)
  - PostgreSQL (standard SQL, many managed options)
  - Redis (standard protocol, many managed options)
  - Elasticsearch (open standard, multiple providers)
  
MEDIUM RISK (migration effort: weeks):
  - AWS SQS → Azure Service Bus (different API, similar
    semantics)
  - AWS DynamoDB → MongoDB Atlas (different query model)
  - Azure Service Bus → Google Pub/Sub
  
HIGH RISK (migration effort: months):
  - AWS Kinesis Data Analytics (KDA) → Apache Flink
    (rewrite)
  - Google BigQuery → Snowflake (all SQL, pipelines,
    dashboards)
  - Snowflake → BigQuery (all SQL, connector
    reconfiguration)
  - AWS Step Functions → Temporal (different orchestration
    model)
  - DynamoDB with AWS-specific features (Streams,
    Accelerator) → any other

HOW TO EVALUATE LOCK-IN RISK:
  1. Is the API an open standard (OpenAPI, SQL, Kafka
    protocol)?
     YES → Low lock-in risk.
     NO  → Evaluate migration complexity.
  
  2. Is the data format open and portable?
     YES (Parquet, Avro, JSON) → Low risk.
     NO (proprietary binary format) → High risk.
  
  3. Are there multiple vendors/forks of this technology?
     YES (3+ options for Kafka: Confluent, MSK, Redpanda)
       → Low risk.
     NO (only one vendor) → High risk.
  
  4. If you needed to migrate: how many code changes,
     pipeline changes, dashboard changes, connector
     changes would be required?
     Estimate this BEFORE signing a contract.
```

**TCO MODEL:**

```
TCO = Direct Costs + Indirect Costs

DIRECT COSTS:
  Build: engineering-hours x hourly-rate
    Example: 4 months x 2 engineers x $80/h x 160h/month
    = $102,400 to build. Plus ongoing maintenance.
  
  Buy: SaaS pricing
    Example: Confluent Cloud 10TB/day = $4000/month
    = $48,000/year.
  
  Self-host: infra + ops time
    Example: 3 Kafka brokers (r5.2xlarge) = $540/month
    + 0.5 SRE FTE = $75,000/year.
    = $81,480/year.

INDIRECT COSTS:
  Build:
    - Incident cost: 6 incidents/year x 4 engineer-hours
      = 24 hours x $80 = $1,920
    - Opportunity cost: 4 months NOT building product
      features.
      For a startup: this is the most expensive cost.
    - Retention risk: engineers leave when maintaining
      poorly-built custom infra.
  
  Buy:
    - Egress cost (often underestimated):
      AWS data egress: $0.09/GB.
      10TB/day egress = $900/day = $27,000/month.
      CHECK THIS. Can be larger than SaaS cost itself.
    - Vendor risk: price increases, API changes,
      acquisitions.
  
  Self-host:
    - 1 major incident/year: $20,000 in SRE time.
    - Upgrades: 40 hours/year per service.
    - Training new engineers: 20 hours/engineer.

HIDDEN COST OF BUILD:
  The biggest hidden cost is opportunity cost.
  A feature that generates $50k/month in revenue
  delayed by 1 month = $50k/month lost.
  If building a custom message queue delays that feature
  by 4 months: opportunity cost = $200k.
  The SaaS that costs $4k/month pays back in 50 months.
  But the opportunity cost is 50x the SaaS cost in month 1.
```

---

### 🧠 Mental Model / Analogy

> Build-vs-buy for infrastructure is like a chef
> deciding whether to make their own pasta or buy it.
> A home cook buys pasta: the quality is good enough,
> the time saved is enormous, and pasta is not their
> core competency. A Michelin-starred chef making
> a signature dish: making the pasta IS the product;
> the specific texture and freshness is the
> differentiator. Most software teams are the home
> cook for infrastructure. Only companies for whom
> the infrastructure IS the product (Netflix CDN,
> Cloudflare's network, Dropbox's storage engine)
> are the Michelin-starred chef.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The default is buy:**
Unless you have specific reasons (core differentiator,
unique requirements), use managed services. The
operational burden of self-hosting is consistently
underestimated.

**Level 2 - TCO includes opportunity cost:**
Building custom infra costs engineering time that
could build product. The SaaS fee is cheap compared
to delayed product features.

**Level 3 - Evaluate lock-in before signing:**
Before choosing a managed service: estimate the
migration cost if you need to switch. Open protocols
= low lock-in. Proprietary APIs = high lock-in.
High lock-in requires higher bar for selection.

**Level 4 - Self-hosted open-source is the middle path:**
For teams with SRE capacity: self-hosted OSS (Kafka,
Redis, etcd) provides control without vendor lock-in,
at the cost of operational burden. The right choice
if you have expertise and TCO is favorable.

**Level 5 - The decision changes as you scale:**
At 3 engineers: buy everything.
At 30 engineers: buy commodity, self-host complex.
At 300 engineers: build only core differentiators.
The threshold for "build" rises with team size
because: more engineers = more operational capacity,
and the savings from building start to exceed the
build cost at scale.

---

### 💻 Code Example

*See Kafka vs SQS and TCO model in First Principles.*

---

### ⚖️ Comparison Table

| Component | Build | Self-Host OSS | Buy (SaaS) |
|---|---|---|---|
| **Message Queue** | Custom broker: 6+ months | Kafka, RabbitMQ | SQS, Pub/Sub, Service Bus |
| **Cache** | Custom in-memory: 3 months | Redis, Memcached | ElastiCache, Redis Cloud |
| **Service Mesh** | Custom sidecar: 12 months | Istio, Linkerd, Envoy | AWS App Mesh, GCP Traffic Director |
| **Consensus / Config** | Custom Raft: 6 months | etcd, ZooKeeper, Consul | AWS CloudMap, GCP Service Directory |
| **Database** | Custom storage engine: 2+ years | PostgreSQL, Cassandra, MongoDB | RDS, Spanner, CosmosDB |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Building gives us full control" | Building gives you full control over an unfinished product. OSS tools have more features, more test coverage, more battle-testing than any custom build will have in year 1. Full control over broken infrastructure is not an advantage. |
| "Open-source is free" | OSS licensing is free. Running OSS in production is NOT free: you pay with engineer time for operations, upgrades, security patches, and incident response. At 0.5 SRE FTE: that's $75k/year for a single OSS service. |
| "Managed services are too expensive" | Compare total cost: $4k/month for managed Kafka vs $80k/year for SRE time plus $6.5k/year in self-hosted infra = $86.5k/year self-hosted vs $48k/year managed. Managed is cheaper for most teams. |
| "We can migrate away from the vendor later" | Migration cost is almost always higher than estimated. "We'll migrate later" is rarely a plan; it is wishful thinking. Evaluate lock-in risk BEFORE choosing, not after. |

---

### 🚨 Failure Modes & Diagnosis

**Self-Hosted Kafka - Under-Resourced SRE Team**

**Symptom:** Kafka consumer lag grows unbounded
every Friday afternoon. Alerts fire. SRE on-call
spends 2 hours rebalancing partitions. The issue
recurs every week.

**Root Cause:** The self-hosted Kafka cluster was
sized for average load. Friday evening brings 3x
traffic. Consumer throughput is capped by broker
disk I/O (single EBS volume per broker, burstable
instance). The team does not have the Kafka expertise
to tune producer batch size, consumer fetch size,
or ISR settings. The operational burden was
underestimated at the build-vs-buy decision.

**Diagnosis:**
```bash
# Check consumer lag per consumer group:
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe --all-groups | \
  awk '$5 > 1000 {print $1, $2, "LAG:", $5}'
# Output: payment-processor checkout-events LAG: 85000

# Check broker disk I/O:
# (on Kafka broker node)
iostat -x 1 5
# %util=99% → disk I/O saturated.

# SOLUTION:
# Short-term: add partitions to the topic.
#   (increases parallelism for consumers)
# kafka-topics.sh --bootstrap-server kafka:9092 \
#   --alter --topic checkout-events \
#   --partitions 24  # was 12
# WARNING: adding partitions changes ordering guarantees
# for keyed messages. Verify downstream impact first.

# Long-term: migrate to managed Kafka (MSK or Confluent).
# The SRE time spent on this incident (2h/week * 52 weeks
# * $80/h = $8,320/year) plus risk of worse incidents
# justifies the managed service cost.
```

---

### 🔗 Related Keywords

**Prerequisites:** `Service Discovery` (DST-004),
`Distributed Queues` (DST-030),
`Event Sourcing` (DST-038)

**Related:** `Observability` (DST-056),
`Migration Strategy` (DST-077)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ BUILD-vs-BUY DECISION QUESTIONS                         │
│ 1. Core differentiator? No → don't build               │
│ 2. Operational capacity? < 3 SREs → buy managed        │
│ 3. Lock-in risk? High → prefer OSS / open protocol     │
│ 4. TCO? Include opportunity cost + egress + ops time   │
├─────────────────────────────────────────────────────────┤
│ DEFAULT: Buy managed service                            │
│ EXCEPTION: Self-host if team has expertise + TCO favors │
│ RARE: Build only when infra IS the product             │
├─────────────────────────────────────────────────────────┤
│ LOCK-IN: Open protocol/format = low risk               │
│          Proprietary API/format = evaluate exit cost   │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The build-vs-buy decision reveals a deep principle
about focus and leverage. Every hour spent maintaining
custom infrastructure is an hour not spent building
the product that earns revenue. Infrastructure
is not a competitive advantage unless infrastructure
IS your product. Netflix's CDN (Open Connect) IS
their product differentiator: by building it,
they saved $1B+ per year in CDN costs and gave
themselves control over the streaming quality
that defines the Netflix experience. Dropbox
building its own storage engine (instead of S3)
saved $75M/year at scale and gave them fine-
grained control over deduplication and block
storage that S3 could not provide. These are
the exceptions that prove the rule: build only
when the build is the product. For everything
else: buy.

---

### 💡 The Surprising Truth

AWS egress costs are the most commonly underestimated
cost in build-vs-buy decisions. Engineers compare
the SaaS license cost to the AWS instance cost
and conclude self-hosting is cheaper. They forget:
every byte of data that leaves AWS (to another
cloud, to an on-prem system, to a CDN, or to
the internet) costs $0.09/GB. A system that
processes 10TB/day and exports half of it incurs
$450/day = $13,500/month in egress costs ALONE.
This is often larger than the managed service
fee. Companies have found that "migrating off
AWS" was prevented not by migration complexity
but by AWS egress fees: the exit cost is priced
into the egress bill. When evaluating buy-vs-self
or buy-vs-buy: always calculate the egress cost
of your current and projected data volumes. It
is often the deciding factor.

---

### ✅ Mastery Checklist

1. [DECIDE] A 10-person startup needs a message queue
   for order events. They expect 10k messages/day now,
   with potential growth to 1M/day in 2 years. Evaluate:
   SQS, self-hosted Kafka, and Confluent Cloud.
   Which do you choose? At what scale does the answer change?
2. [CALCULATE] Calculate the total annual TCO for
   self-hosting a 3-broker Kafka cluster (r5.2xlarge
   instances) vs Confluent Cloud for 5TB/day of data.
   Include: infra cost, SRE time (0.3 FTE), and incidents.
3. [EVALUATE] Your company uses AWS Kinesis Data
   Analytics for stream processing. A new CTO wants
   to migrate to self-hosted Apache Flink. Estimate
   the migration complexity. What is the lock-in risk
   of staying on Kinesis vs migrating to Flink?
4. [AUDIT] List the infrastructure components your
   current system uses. For each: classify as build,
   self-host OSS, or buy (SaaS). Is each classification
   justified by the decision framework? Which one
   should be re-evaluated?
5. [PRESENT] A teammate wants to build a custom
   distributed cache because "Redis is overkill and
   we don't need that complexity." How do you respond?
   What data do you bring to the conversation?
