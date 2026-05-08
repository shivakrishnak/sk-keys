---
layout: default
title: "Log Compaction"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /big-data-streaming/log-compaction/
id: BIG-019
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Kafka, Kafka Topic / Partition / Offset
used_by: Kafka Streams (KTable), Change Log Topics, State Restoration
related: Apache Kafka, Kafka Streams, KTable vs KStream
tags:
  - kafka-log-compaction
  - compacted-topics
  - changelog
  - ktable
  - deep-dive
---

# BIG-019 — Log Compaction

⚡ TL;DR — Kafka **log compaction** keeps only the **latest value for each key** in a topic partition — old records with the same key are removed (compacted away), keeping the log as a **changelog** of current state rather than full history; a **tombstone** (null value) marks a key as deleted; compacted topics are never time-expired — they retain the latest state indefinitely, making them ideal for KTable state restoration, cache population, and database change-log replication.

| #544            | Category: Big Data & Streaming                               | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, Kafka Topic / Partition / Offset               |                 |
| **Used by:**    | Kafka Streams (KTable), Change Log Topics, State Restoration |                 |
| **Related:**    | Apache Kafka, Kafka Streams, KTable vs KStream               |                 |

---

### 🔥 The Problem This Solves

**RETENTION WITHOUT INFINITE STORAGE — "ONLY THE LATEST VALUE MATTERS":**
A user profile topic: every profile update writes a new event. With time-based retention (7 days), after 7 days, the user's earliest events are gone — but if you need to rebuild a consumer's state (new service instance starting up), you can't recreate all current profiles from only the last 7 days of events. With log compaction: the log always contains the latest profile for every user. A new consumer reads the compacted log to get the current state of all users — no time pressure, correct current state, storage-efficient.

---

### 📘 Textbook Definition

**Log Compaction**: a Kafka retention policy (`cleanup.policy=compact`) where Kafka's log cleaner thread periodically scans partition segments and removes older records that have been superseded by a newer record with the same key. Result: for each key, only the latest value is retained.

**Compaction process**: the log is divided into two logical sections:

1. **Head (clean section)**: recent records not yet compacted. All records present. Written sequentially.
2. **Tail (dirty section)**: older records, compacted. Contains only the latest value per key in this section.

**Tombstone**: a record with a non-null key and a null value. Written to mark a key as deleted. After compaction, the tombstone persists for `delete.retention.ms` (default 24 hours), then is itself removed — allowing consumers time to see the deletion event.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Log compaction = keep only the latest record per key, remove superseded older records; null value (tombstone) = delete key; enables infinite retention of current state without infinite storage.

**One analogy:**

> Log compaction is like a city's address directory. Entries: John Smith → 123 Main St, John Smith → 456 Oak Ave (moved), John Smith → 789 Pine Rd (moved again). A directory with deletion cleanup keeps only the latest: John Smith → 789 Pine Rd. "Moved away" entries use a special mark (tombstone): John Smith → [moved away / deleted]. After 24 hours, the deletion mark is removed and Smith no longer appears. The directory always reflects current state, not the full history of every move.

**One insight:**
Log compaction enables **Kafka as a database**. A compacted topic becomes a materialized view of current state. Kafka Streams uses compacted topics for KTable changelog storage: when a new application instance starts, it reads the compacted changelog topic to restore its local RocksDB state store to the current state — without replaying months of event history. This is the fundamental mechanism behind Kafka Streams' fault tolerance and state restoration.

---

### 🔩 First Principles Explanation

**COMPACTION MECHANICS:**

```
BEFORE compaction (partition log):
  offset 0: key="user:1", value={name:"Alice", email:"a@a.com"}
  offset 1: key="user:2", value={name:"Bob",   email:"b@b.com"}
  offset 2: key="user:1", value={name:"Alice", email:"alice@new.com"}  (updated email)
  offset 3: key="user:3", value={name:"Carol", email:"c@c.com"}
  offset 4: key="user:2", value=null  (TOMBSTONE: Bob deleted)
  offset 5: key="user:1", value={name:"Alice Smith", email:"alice@new.com"} (name changed)
  offset 6: key="user:4", value={name:"Dave",  email:"d@d.com"}

AFTER compaction:
  offset 3: key="user:3", value={name:"Carol", email:"c@c.com"}  (no update)
  offset 4: key="user:2", value=null  (tombstone kept for delete.retention.ms)
  offset 5: key="user:1", value={name:"Alice Smith", email:"alice@new.com"}  (latest)
  offset 6: key="user:4", value={name:"Dave", email:"d@d.com"}  (no update)

  [offsets 0, 1, 2 are gone — superseded by offset 5 (user:1) and 4 (user:2 tombstone)]

  After 24h (delete.retention.ms):
  offset 3: user:3 (unchanged)
  offset 5: user:1 (unchanged)
  offset 6: user:4 (unchanged)
  [offset 4 (user:2 tombstone) is now also removed — user:2 fully gone]

KEY INSIGHT: offsets are preserved (not renumbered). Consumer reading from offset 5
still gets the user:1 record at offset 5. Compaction removes records but doesn't
renumber the remaining offsets.
```

**TOPIC CONFIGURATION:**

```bash
# Create a compacted topic:
kafka-topics.sh --create \
  --topic user-profiles \
  --partitions 6 \
  --replication-factor 3 \
  --config cleanup.policy=compact \
  --config min.cleanable.dirty.ratio=0.5 \     # compact when 50% of log is dirty
  --config segment.ms=86400000 \               # 24h segment roll (allows compaction)
  --config delete.retention.ms=86400000 \      # tombstones kept 24h
  --bootstrap-server kafka:9092

# Hybrid: compact + delete (keep history AND compact old records)
kafka-topics.sh --alter \
  --topic user-events \
  --config "cleanup.policy=compact,delete" \
  --config retention.ms=604800000 \            # delete after 7 days
  --config min.cleanable.dirty.ratio=0.5 \
  --bootstrap-server kafka:9092
# Result: events > 7 days old deleted; within 7 days: compacted (latest per key)

# Check topic config:
kafka-configs.sh --describe \
  --entity-type topics \
  --entity-name user-profiles \
  --bootstrap-server kafka:9092
```

**PRODUCING TO COMPACTED TOPICS:**

```java
@Service
public class UserProfileProducer {

    private final KafkaTemplate<String, UserProfile> kafkaTemplate;

    // UPDATE: write latest value for key → old values will be compacted away
    public void updateUserProfile(String userId, UserProfile profile) {
        // Key MUST be set for compaction to work (compaction is key-based)
        kafkaTemplate.send("user-profiles", userId, profile);
    }

    // DELETE: write tombstone (null value) → key will be removed after compaction
    public void deleteUserProfile(String userId) {
        // Null value = tombstone = mark for deletion
        // Use ProducerRecord directly to send null value:
        ProducerRecord<String, UserProfile> tombstone =
            new ProducerRecord<>("user-profiles", userId, null);
        kafkaTemplate.send(tombstone);
    }
}

// IMPORTANT: Never produce to a compacted topic WITHOUT a key
// Records without a key cannot be compacted (no key = no deduplication)
// Key = null → Kafka assigns random partition → NOT compactable
```

**KAFKA STREAMS KTABLE — POWERED BY COMPACTION:**

```java
// KTable uses a compacted changelog topic for state restoration
// When a KTable instance restarts, it reads the compacted changelog
// to restore local RocksDB state to current values

StreamsBuilder builder = new StreamsBuilder();

// KTable backed by compacted topic "user-profiles":
KTable<String, UserProfile> userProfiles = builder
    .table("user-profiles",
        Materialized.<String, UserProfile>as("user-profiles-store")
            .withKeySerde(Serdes.String())
            .withValueSerde(JsonSerde.of(UserProfile.class))
    );

// Each KTable record = latest value for that key (like a database table)
// Internally: Kafka Streams creates a compacted changelog topic
// If application restarts: reads changelog to restore state

// Join stream with KTable (enrich events with latest user profile):
KStream<String, OrderEvent> orders = builder.stream("orders");
KStream<String, EnrichedOrder> enriched = orders.join(
    userProfiles,
    (order, profile) -> new EnrichedOrder(order, profile)  // join func
);
// Join works because KTable always has the latest user profile
```

---

### 🧪 Thought Experiment

**COMPACTED TOPIC vs TIME-BASED RETENTION FOR SERVICE STARTUP:**

New instance of "inventory-service" starts up. It needs to know the current quantity for 1 million products.

Option A (time-based retention, 7 days):

- Read all events for 7 days → might have 100 million events
- Apply all updates in order → build current state
- Takes: 20 minutes to replay + process 100M events
- Problem: if a product was last updated 8 days ago, it's MISSING from the 7-day window

Option B (compacted topic):

- Read the compacted "product-inventory" topic
- Only 1 million records (one per product, latest value)
- Takes: 2 minutes to read 1M records
- Complete and accurate: every product present regardless of when last updated
- Storage: 10% of the time-based approach (no historical events)

Result: compacted topics are dramatically better for state restoration and bootstrapping.

---

### 🧠 Mental Model / Analogy

> Log compaction is like keeping a filing cabinet organized. Every time there's an update: file the new document (append to log). Periodically, a filing clerk (log cleaner thread) reviews the cabinet (segment compaction): if there are 5 updates to "Project Alpha" folder, keep only the most recent version — shred the older 4 (compaction). A sticky note that says "Project Beta: CLOSED" (tombstone) stays for 24 hours (delete.retention.ms) so anyone who missed the memo sees it, then gets shredded too. The result: the cabinet always reflects current status, takes minimal space, and any new employee can read it to get fully up to date.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Log compaction = keep only the latest value per key. Null value = tombstone (delete). Compacted topics retain current state indefinitely (no time expiry). Use for: KTable changelogs, cache population, CDC sink topics.

**Level 2:** `cleanup.policy=compact`: enables compaction. `min.cleanable.dirty.ratio=0.5`: compact when 50% of log is dirty (not yet compacted). `delete.retention.ms`: tombstones kept this long before final removal. Hybrid: `compact,delete`: compact old records + time-expire very old ones.

**Level 3:** Log cleaner: background thread checks all compacted topics. Compaction unit: a segment pair (head + tail). Cleaner creates an offset index per key → scans segment → writes new segment with only latest per key → swaps old segment. Active segment never compacted (too recent). Multiple log cleaner threads: `log.cleaner.threads` (default 1). `log.cleaner.min.cleanable.ratio` controls how "dirty" a partition must be before cleaning starts.

**Level 4:** Log compaction enables **Kafka as a distributed key-value store**. Combined with Kafka Streams, you can build materialized views: a KTable backed by a compacted changelog topic is a queryable state store (using Kafka Streams interactive queries). External applications can query the KTable state directly via the Kafka Streams state API (`store.get("user:42")`) — effectively using Kafka Streams as an embedded database backed by Kafka. This is the "Kafka as event-sourced state store" pattern used in high-throughput microservices that need per-entity state without a separate database.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ LOG COMPACTION PROCESS                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│ BEFORE:                                              │
│ [A:v1][B:v1][A:v2][C:v1][B:v2][A:v3][D:v1][A:null] │
│  off0   off1  off2  off3  off4  off5  off6   off7    │
│                           ↑ B updated        ↑ A tomb│
│                                                      │
│ Log Cleaner scans → key→latest offset map:           │
│   A → off7(null=tombstone), B → off4, C → off3, D → off6│
│                                                      │
│ AFTER compaction:                                    │
│ [B:v2][C:v1][D:v1][A:null] ← tombstone still there  │
│  off4   off3  off6   off7  (offsets preserved!)      │
│                                                      │
│ After delete.retention.ms passes:                    │
│ [B:v2][C:v1][D:v1]         ← A fully removed        │
│ [LOG COMPACTION ← YOU ARE HERE: current state only]  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
User profile service using compacted Kafka topic:

Initial state: topic "user-profiles" (compacted), empty

Day 1: 1M user registrations → 1M records written (user:1 → {...}, user:2 → {...}, ...)
Log cleaner: no duplicates yet (each user written once)

Day 5: 200K profile updates → 200K new records (user:42 → {updated...}, ...)
Log cleaner triggers (dirty ratio > 0.5):
  Scans old segments: finds 200K keys that now have newer records
  Compacts: removes old versions, keeps only latest
  Result: still ~1M records total (1M users, each with latest profile)

Day 10: user:999 closes account → producer writes tombstone (key=user:999, value=null)
Day 11: log cleaner runs → tombstone present in compacted log (visible to consumers)
Day 11 + 24h: tombstone removed → user:999 fully absent from topic

New service instance starts Day 10:
  Reads compacted topic from offset 0
  Gets 1M records (current state of all users, minus deleted)
  Takes 2 minutes (1M records at high throughput)
  Local state store fully populated
  Service ready to serve traffic
```

---

### ⚖️ Comparison Table

| Feature       | cleanup.policy=delete              | cleanup.policy=compact       | compact,delete               |
| ------------- | ---------------------------------- | ---------------------------- | ---------------------------- |
| Retention     | Time or size based                 | Indefinite (latest per key)  | Time + compacted             |
| Storage       | Grows with event rate              | ~Proportional to unique keys | Combined                     |
| Full history  | Yes (within retention window)      | No (latest only)             | Partial                      |
| State restore | Incomplete (might miss old events) | Complete (always latest)     | Partial                      |
| Use case      | Event streams, logs                | KTable, CDC state            | Audit trails + current state |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                           |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Log compaction runs constantly"                  | Log compaction is a background process that runs when the dirty ratio threshold is met. There's a delay between writing and compaction. The "head" (recent records) is never immediately compacted — consumers reading live events see all of them                |
| "Compacted topics have no duplicate keys"         | Only after compaction runs. Before the cleaner runs, a compacted topic may have multiple records per key in the uncompacted "head" section. The compaction guarantee is eventual, not immediate                                                                   |
| "Tombstones are immediately visible as deletions" | Tombstone records ARE visible to consumers when they're written — consumers see the null value. But the key isn't "gone" from the log until `delete.retention.ms` after compaction. This window ensures consumers that might be behind can see the deletion event |

---

### 🚨 Failure Modes & Diagnosis

**1. Compaction Not Keeping Up — Log Growing Unboundedly**

**Symptom:** Compacted topic disk usage grows continuously despite expected stable key count. Log cleaner falls behind.

**Root Cause:** Log cleaner is too slow — high write rate with many key updates outpacing the single cleaner thread. `min.cleanable.dirty.ratio` threshold isn't met fast enough, or cleaner is throttled.

**Diagnosis:**

```bash
kafka-log-dirs.sh --bootstrap-server kafka:9092 \
  --topic-list user-profiles --describe
# Shows segment details and dirty ratio

# Check cleaner metrics:
kafka-jmx.sh --jmx-url service:jmx:... --metrics kafka.log:name=max-dirty-percent
```

**Fix:**

```bash
# Increase log cleaner threads:
log.cleaner.threads=4  # in server.properties

# Reduce dirty ratio trigger (compact more aggressively):
kafka-configs.sh --alter --entity-type topics --entity-name user-profiles \
  --add-config min.cleanable.dirty.ratio=0.2 --bootstrap-server kafka:9092

# Remove cleaner throttle if applied:
log.cleaner.io.max.bytes.per.second=1073741824  # 1GB/s (unthrottled)
```

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Kafka Topic / Partition / Offset
**Builds On This:** Kafka Streams, KTable vs KStream
**Related:** Apache Kafka, Kafka Streams, KTable vs KStream

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ POLICY      │ cleanup.policy=compact                      │
│ EFFECT      │ Keep only latest value per key              │
│ TOMBSTONE   │ key + null value = mark for deletion        │
│ delete.ms   │ Tombstone kept this long before removal     │
│ DIRTY RATIO │ min.cleanable.dirty.ratio=0.5 (50% trigger)│
│ OFFSETS     │ Preserved (not renumbered after compaction) │
│ USE FOR     │ KTable changelogs, cache topics, CDC state  │
│ HYBRID      │ compact,delete = both policies combined     │
│ STARTUP     │ Read compacted topic → restore full state  │
│ ONE-LINER   │ "Infinite changelog: keep latest per key,  │
│             │  null = tombstone, ideal for state restore" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the difference between `cleanup.policy=delete` and `cleanup.policy=compact` for a Kafka topic? When would you use each? What is a tombstone and why is it needed?

**Q2.** (TYPE C — Design) You're building a product catalog service. Product data changes infrequently (average: once per month per product). 1 million products. 10 service instances each need a local cache of the full catalog. Describe how you'd use a Kafka compacted topic to implement this, including: topic configuration, startup state restoration, and handling of product deletions.
