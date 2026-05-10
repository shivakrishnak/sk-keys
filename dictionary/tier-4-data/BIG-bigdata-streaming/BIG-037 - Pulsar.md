---
version: 2
layout: default
title: "Pulsar"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 37
permalink: /big-data-streaming/pulsar/
id: BIG-037
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Kafka, Topic/Partition, Consumer Lag
used_by: Multi-Tenant Streaming, Tiered Storage, Geo-Replication
related: Apache Kafka, RabbitMQ, Message Ordering
tags:
  - pulsar
  - bookkeeper
  - tiered-storage
  - multi-tenancy
  - messaging
---

# BIG-037 - Pulsar

⚡ TL;DR - **Apache Pulsar** is a distributed pub-sub messaging system that separates **compute (brokers) from storage (Apache BookKeeper)** - enabling elastic scaling of each independently; four subscription types: **exclusive** (1 consumer), **shared** (competing consumers), **failover** (active-standby), **key_shared** (ordered per key); native **tiered storage** (hot → BookKeeper, cold → S3/GCS), **multi-tenancy** (tenant/namespace/topic hierarchy), **geo-replication**, and **Pulsar Functions** (lightweight serverless compute); architectural difference from Kafka: Pulsar splits broker and storage layers, enabling faster broker scaling.

| #562            | Category: Big Data & Streaming                          | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Apache Kafka, Topic/Partition, Consumer Lag             |                 |
| **Used by:**    | Multi-Tenant Streaming, Tiered Storage, Geo-Replication |                 |
| **Related:**    | Apache Kafka, RabbitMQ, Message Ordering                |                 |

---

### 🔥 The Problem This Solves

**KAFKA'S ARCHITECTURAL LIMITATIONS:**
Kafka couples broker and storage: a partition's data lives on the broker that owns it. Scaling out means rebalancing partitions (moving data between brokers - slow, resource-intensive). Retention = expensive broker disk (you can't move cold data to cheap S3 without third-party plugins). Multi-tenancy requires separate Kafka clusters per team (no namespace isolation). Pulsar addresses all these: stateless brokers (can be added/removed instantly, no data migration), native tiered storage (old segments → S3 automatically), built-in multi-tenancy (tenant/namespace/topic hierarchy with quotas and ACLs per level).

---

### 📘 Textbook Definition

**Apache Pulsar** is an open-source, cloud-native pub-sub messaging and streaming platform originally developed at Yahoo!

**Core Architecture:**

- **Brokers** (compute layer): stateless message routing, receive writes, serve reads from cache. No persistent data stored. Adding/removing brokers: zero data migration.
- **Apache BookKeeper** (storage layer): distributed, append-only, persistent log storage. Ledgers = segments of topic data. BookKeeper = ensemble of Bookie nodes.
- **ZooKeeper**: cluster metadata, broker/topic ownership, BookKeeper ledger management.
- **Topic hierarchy**: `persistent://tenant/namespace/topic`. Three-level: tenant (org unit), namespace (application group, config policies), topic (individual stream).

**Four Subscription Types:**

- `Exclusive`: one active consumer per subscription. Error if another consumer subscribes.
- `Shared`: multiple consumers per subscription. Round-robin distribution. No ordering guarantee.
- `Failover`: multiple consumers, one active at a time. Failover to next on active crash (like Kafka's high-watermark failover).
- `Key_Shared`: multiple consumers; same key always routed to same consumer. Ordered per key, parallel across keys.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pulsar = stateless brokers + BookKeeper storage; four subscription types (exclusive/shared/failover/key_shared); built-in tiered storage, multi-tenancy, and geo-replication without plugins.

**One analogy:**

> Kafka = a hotel where the rooms (partitions) belong to specific floors (brokers). Moving a room requires massive renovation. Pulsar = a hotel with a central luggage warehouse (BookKeeper). Any concierge (broker) can retrieve any luggage. Adding concierge desks requires zero furniture moving.

**One insight:**
Pulsar is architecturally superior for: (1) **elastic scaling** (stateless brokers → add capacity instantly), (2) **infinite retention** (tiered storage to S3 - no disk pressure on brokers), (3) **multi-tenancy at scale** (namespaces with per-namespace quotas, ACLs, retention). Kafka is arguably simpler and has a larger ecosystem (Kafka Connect, ksqlDB, Schema Registry). For most teams: Kafka is the right default. Pulsar shines for large enterprises with multi-team platforms, long retention requirements, and multi-region deployments.

---

### 🔩 First Principles Explanation

**PULSAR TOPIC HIERARCHY (MULTI-TENANCY):**

```
Pulsar namespace structure:
  persistent://payments/fraud-detection/transactions
  │              │        │                └── topic
  │              │        └── namespace (team/app scope)
  │              └── tenant (org/BU scope)
  └── schema (persistent = durable, non-persistent = ephemeral)

Admin API: create tenant, namespace, topic
```

```java
// Spring Boot + Pulsar (spring-pulsar library):
// <dependency>
//   <groupId>org.springframework.pulsar</groupId>
//   <artifactId>spring-pulsar-spring-boot-starter</artifactId>
// </dependency>

// application.yml:
// spring:
//   pulsar:
//     client:
//       service-url: pulsar://pulsar-broker:6650
//     admin:
//       service-url: http://pulsar-broker:8080

// PRODUCER: send orders to Pulsar
@Service
public class OrderEventProducer {

    @Autowired
    private PulsarTemplate<Order> pulsarTemplate;

    public void publishOrder(Order order) throws PulsarClientException {
        // Topic: persistent://{tenant}/{namespace}/{topic}
        pulsarTemplate.send("persistent://ecommerce/orders/new-orders", order);
        // Same routing key as Kafka: set message key for ordering
    }

    // With explicit schema (Avro, Protobuf, JSON):
    @Bean
    public Schema<Order> orderSchema() {
        return Schema.JSON(Order.class);  // JSON schema for Order
    }
}

// CONSUMER - Exclusive subscription (single consumer):
@PulsarListener(
    topics = "persistent://ecommerce/orders/new-orders",
    subscriptionName = "order-processor-sub",
    subscriptionType = SubscriptionType.Exclusive  // single consumer
)
public void processOrder(Order order) {
    orderService.process(order);
}

// CONSUMER - Shared subscription (competing consumers, scalable):
@PulsarListener(
    topics = "persistent://ecommerce/orders/new-orders",
    subscriptionName = "order-processor-shared-sub",
    subscriptionType = SubscriptionType.Shared
    // Multiple instances of this @PulsarListener → load balanced
    // Messages distributed round-robin → no ordering
)
public void processOrderParallel(Order order) {
    orderService.process(order);  // idempotent required (may redeliver)
}

// CONSUMER - Key_Shared (ordered per orderId, parallel across orderIds):
@PulsarListener(
    topics = "persistent://ecommerce/orders/new-orders",
    subscriptionName = "order-keyed-sub",
    subscriptionType = SubscriptionType.Key_Shared
    // Pulsar routes by message key: same orderId → same consumer
    // Different orderIds: different consumers → parallelism
)
public void processOrderKeyed(Order order) {
    orderService.process(order);  // ordered per order
}

// CONSUMER - Failover (active-standby):
@PulsarListener(
    topics = "persistent://ecommerce/orders/new-orders",
    subscriptionName = "order-failover-sub",
    subscriptionType = SubscriptionType.Failover
    // One active consumer at a time; fails over to standby on crash
)
public void processOrderPrimary(Order order) {
    orderService.process(order);
}
```

**TIERED STORAGE (AUTO-OFFLOAD TO S3):**

```bash
# Pulsar broker configuration: offload-policies
# broker.conf:
managedLedgerOffloadDriver=s3
s3ManagedLedgerOffloadBucket=my-pulsar-offload
s3ManagedLedgerOffloadRegion=us-east-1

# Namespace policy: offload data older than 1 day to S3
pulsar-admin namespaces set-offload-threshold \
  --size 1G \          # offload when ledger > 1GB
  ecommerce/orders

# or: offload after 1 day
pulsar-admin namespaces set-offload-deletion-lag \
  --lag 1d \
  ecommerce/orders

# Result:
# Data < 1 day: served from BookKeeper (fast, SSD)
# Data > 1 day: transparently stored in S3 (cheap)
# Consumer reading old data: Pulsar fetches from S3 transparently
# Consumer sees no difference: same Pulsar API regardless of storage tier
# Retention: can be INFINITE (S3 cost per GB/month ≈ $0.023)
# Kafka equivalent: needs Confluent Tiered Storage (paid) or manual S3 archival
```

**PULSAR FUNCTIONS (LIGHTWEIGHT COMPUTE):**

```java
// Pulsar Functions: small compute functions that run inside Pulsar
// Input: Pulsar topic → compute → Output: Pulsar topic
// Like serverless Lambda for stream processing
// Deploy to: Pulsar cluster (no Flink/Spark needed for simple transforms)

public class OrderEnrichmentFunction implements Function<String, String> {

    @Override
    public String process(String orderJson, Context context) {
        // context: logger, metrics, state (key-value store)
        try {
            JsonNode order = objectMapper.readTree(orderJson);

            // Look up customer data (from Pulsar function state store):
            String customerId = order.get("customerId").asText();
            byte[] customerBytes = context.getState(customerId);  // Pulsar state store

            if (customerBytes != null) {
                JsonNode customer = objectMapper.readTree(customerBytes);
                ((ObjectNode) order).set("customerName", customer.get("name"));
                ((ObjectNode) order).set("customerTier", customer.get("tier"));
            }

            context.getLogger().info("Enriched order: {}", order.get("orderId").asText());
            context.recordMetric("orders-enriched", 1);

            return objectMapper.writeValueAsString(order);
        } catch (Exception e) {
            throw new RuntimeException("Failed to enrich order", e);
        }
    }
}

// Deploy:
// pulsar-admin functions create \
//   --jar /path/to/enrichment-function.jar \
//   --classname com.example.OrderEnrichmentFunction \
//   --inputs persistent://ecommerce/orders/new-orders \
//   --output persistent://ecommerce/orders/enriched-orders \
//   --name order-enrichment

// NO Flink/Kafka Streams cluster needed for simple stateless transforms
```

**GEO-REPLICATION:**

```bash
# Pulsar geo-replication: async cross-cluster replication
# Cluster A (us-east) ↔ Cluster B (eu-west)

# Create clusters:
pulsar-admin clusters create us-east --url http://us-east-broker:8080
pulsar-admin clusters create eu-west --url http://eu-west-broker:8080

# Enable geo-replication on namespace:
pulsar-admin namespaces set-replication-clusters \
  --clusters us-east,eu-west \
  ecommerce/orders

# Result: messages published to us-east/orders → also appear in eu-west/orders
# Consumers in either cluster: see all messages
# Latency: network RTT (async, not synchronous)
# Failure: if eu-west is down, us-east continues; syncs when eu-west recovers
```

---

### 🧪 Thought Experiment

**PULSAR vs KAFKA: SCALING SCENARIO:**

Kafka cluster (3 brokers, 90 partitions each):

- Need to scale: add 3 more brokers → must reassign 45 partitions to new brokers.
- Data migration: copy ~TB of data across network → slow (hours), risky.
- During migration: increased broker load, potential consumer lag spikes.

Pulsar cluster (3 stateless brokers + 3 BookKeeper nodes):

- Need to scale compute (more concurrent readers): add 3 more stateless brokers.
- No data migration: brokers are stateless (all data in BookKeeper).
- New brokers immediately available: pick up new topic assignments instantly.
- Need to scale storage: add BookKeeper nodes (data migration: ledger striping, gradual).

For read-heavy workloads with fluctuating concurrency, Pulsar's stateless brokers provide significantly faster horizontal scaling.

---

### 🧠 Mental Model / Analogy

> Kafka = **filing cabinets** in each employee's desk. Moving data = moving furniture. Pulsar = **central filing room** (BookKeeper) + **any employee can go get files** (stateless brokers). Need more employees? Hire instantly. No furniture moving needed.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Pulsar: stateless brokers + BookKeeper storage. Four subscription types. Native tiered storage + multi-tenancy + geo-replication. `persistent://tenant/namespace/topic`.

**Level 2:** Exclusive = 1 consumer. Shared = competing consumers (no order). Failover = active-standby. Key_Shared = ordered per key, parallel across keys. Tiered storage: BookKeeper (hot) → S3 (cold) automatically. Pulsar Functions: lightweight transform inside Pulsar cluster.

**Level 3:** BookKeeper internals: ensemble writes (write to N bookies, ack on quorum W). Ledgers: append-only segments of topic data. Journal: write-ahead log in BookKeeper for durability. Broker ownership: each broker owns a set of topics (ZooKeeper coordination). Bundle: virtual group of topics used for topic-to-broker assignment (not individual partition ownership).

**Level 4:** Pulsar vs Kafka for Kappa Architecture: Pulsar's native tiered storage enables infinite Kafka-like retention on S3. Reprocessing = subscribe with earliest offset on new subscription → replay from S3 transparently. No separate Kafka + S3 archival pipeline needed. Pulsar transactions (Pulsar 2.8+): cross-topic atomic publish + ack, similar to Kafka transactions. For Java teams already on Spring: Spring Pulsar autoconfiguration provides the same level of integration as Spring Kafka. Consider: ecosystem maturity - Kafka Streams, ksqlDB, Schema Registry, Kafka Connect (1000+ connectors) have no Pulsar equivalents. Pulsar ecosystem is growing but less mature.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PULSAR ARCHITECTURE                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Producer → Broker (stateless) → BookKeeper Bookie   │
│              ↑                       ↑              │
│         No local data            Persistent storage  │
│         (pure routing)            (Ledger/Journal)  │
│                                                      │
│ Consumer ← Broker ← cache (recent data) or          │
│             if cache miss: BookKeeper fetch         │
│             if old data: S3 tiered storage fetch    │
│                                                      │
│ ZooKeeper: broker discovery, topic ownership       │
│                                                      │
│ Scale brokers: add 3 more → zero data migration    │
│ Scale storage: add BookKeeper nodes → gradual       │
│                                                      │
│ Topic: persistent://tenant/namespace/topic          │
│ Subscription types:                                 │
│   Exclusive  → 1 consumer                          │
│   Shared     → N consumers, round-robin, no order  │
│   Failover   → N consumers, 1 active               │
│   Key_Shared → N consumers, ordered per key        │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
SaaS platform (B2B, 100 tenants): Pulsar multi-tenant architecture

Tenant hierarchy:
  persistent://tenant-a/billing/invoices      (Tenant A's billing events)
  persistent://tenant-b/billing/invoices      (Tenant B's billing events)
  persistent://tenant-c/analytics/pageviews   (Tenant C's analytics)

Per-namespace policies:
  tenant-a/billing: retention=7 days, replication=us-east+eu-west, max-throughput=10MB/s
  tenant-b/billing: retention=30 days, replication=us-east only, quota=5MB/s
  tenant-c/analytics: retention=1 day, tiered-storage=enabled (→S3 after 1h)

Result:
  Each tenant isolated: cannot read other tenants' data
  Per-tenant configuration: different retention, replication, throughput
  Single Pulsar cluster: all 100 tenants shared infrastructure (vs 100 Kafka clusters)

With Kafka:
  Option 1: One shared cluster → no tenant isolation
  Option 2: 100 separate clusters → 100× operational overhead
  Pulsar: one cluster + namespace isolation → built for this pattern
```

---

### ⚖️ Comparison Table

| Feature              | Apache Pulsar                                  | Apache Kafka                  |
| -------------------- | ---------------------------------------------- | ----------------------------- |
| Storage architecture | Separated (BookKeeper)                         | Coupled (broker disk)         |
| Broker scaling       | Instant (stateless)                            | Slow (partition rebalance)    |
| Tiered storage       | Native built-in                                | Confluent (paid) or manual    |
| Multi-tenancy        | Native (tenant/namespace)                      | Manual (separate clusters)    |
| Subscription types   | 4 types (exclusive/shared/failover/key_shared) | Consumer groups only          |
| Geo-replication      | Native built-in                                | MirrorMaker 2 (separate tool) |
| Ecosystem            | Growing (less mature)                          | Large (Kafka Connect, ksqlDB) |
| Transaction support  | Yes (Pulsar 2.8+)                              | Yes (Kafka 0.11+)             |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                             |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Pulsar is a drop-in replacement for Kafka" | Pulsar uses a different client API. Migration requires changing producers/consumers to Pulsar client or Spring Pulsar. Some Kafka-compatible APIs exist but are not full feature-parity             |
| "Pulsar is always faster than Kafka"        | For simple pub-sub at scale, Kafka and Pulsar have comparable throughput. Pulsar's advantage is operational (elastic scaling, tiered storage) not raw throughput                                    |
| "BookKeeper adds latency vs Kafka"          | BookKeeper write = journal write (sequential, fast SSD) + ensemble write. Kafka write = sequential disk write. Both are fast. Pulsar can achieve sub-millisecond publish latency with proper tuning |

---

### 🚨 Failure Modes & Diagnosis

**1. Topic Lookup Failures (ZooKeeper Issues)**

**Symptom:** Producer/consumer cannot connect to Pulsar; "Lookup failure: topic persistent://..." errors.

**Root Cause:** ZooKeeper session timeout or quorum failure. Brokers lose topic ownership information.

**Diagnosis:**

```bash
# Check ZooKeeper health:
pulsar-admin brokers list                   # should return broker addresses
pulsar-admin topics lookup persistent://tenant/ns/topic  # broker that owns topic

# ZooKeeper: check for session expiry in broker logs:
grep "ZooKeeper session expired" /var/log/pulsar/broker.log

# Fix: ensure ZooKeeper quorum (3+ ZK nodes, majority alive)
# Note: Pulsar 3.0+ replaces ZooKeeper with metadata service (etcd)
```

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Topic/Partition
**Builds On This:** Multi-Tenant Streaming, Tiered Storage
**Related:** Apache Kafka, RabbitMQ, Message Ordering

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ARCH        │ Stateless brokers + BookKeeper storage    │
│ HIERARCHY   │ tenant/namespace/topic                    │
│ EXCLUSIVE   │ 1 consumer per subscription               │
│ SHARED      │ Competing consumers, no order             │
│ FAILOVER    │ Active-standby                            │
│ KEY_SHARED  │ Ordered per key, parallel across keys    │
│ TIERED STG  │ BookKeeper (hot) → S3/GCS (cold, auto)  │
│ FUNCTIONS   │ Lightweight compute inside Pulsar         │
│ GEO-REPL    │ Native async cross-cluster replication    │
│ vs KAFKA    │ Pulsar: elastic scale, tiered storage,   │
│             │  multi-tenancy; Kafka: larger ecosystem   │
│ ONE-LINER   │ "Pulsar: stateless brokers + BookKeeper; │
│             │  4 sub types; native tiered storage"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What are the four subscription types in Apache Pulsar? For each, describe when you would use it and how it compares to a Kafka consumer group.

**Q2.** (TYPE C - Architecture) A large SaaS platform serves 200 enterprise tenants. Each tenant needs isolated message streams, different retention policies (1 day to 1 year), and the platform needs to minimize storage costs. Compare using 200 separate Kafka clusters vs one Pulsar cluster with multi-tenancy. What are the tradeoffs in operations, cost, and feature support?
