Set-Location "c:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-5-distributed-architecture\DST-distributed-systems"

$newContent = @'
---
id: DST-062
title: Conflict Resolution Strategies
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-061
related: DST-061, DST-063
tags:
  - distributed
  - architecture
  - pattern
  - deep-dive
  - advanced
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 62
permalink: /distributed-systems/conflict-resolution-strategies/
---

# DST-062 - Conflict Resolution Strategies

⚡ TL;DR - Conflict Resolution Strategies are the policies a distributed system applies when two replicas have diverged due to concurrent writes — defining which value wins, who decides, or how to merge the conflicting versions into a single consistent state.

| Metadata | | |
|:---|:---|:---|
| **Depends on:** | DST-061 | |
| **Related:** | DST-061, DST-063 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Dynamo (Amazon's internal key-value store, 2007) allowed writes to succeed on multiple replicas simultaneously during network partitions (high availability). When the partition healed: two replicas had different values for the same key. No conflict resolution policy: undefined behavior. The system could silently discard one value, corrupt the other, or crash. Without a clear policy: developers can't reason about what their data contains after a partition.

**THE BREAKING POINT:**
Every distributed system with multi-master replication, active-active deployment, or offline-capable clients WILL experience conflicting concurrent writes. The question is not IF conflicts happen but WHAT HAPPENS WHEN THEY DO. Systems without a defined conflict resolution strategy: (1) silently lose writes (unacceptable for most applications), (2) crash on conflict (unacceptable for availability), or (3) leave the conflict unresolved forever (data corruption). The conflict resolution strategy is a first-class design decision — not an afterthought.

**THE INVENTION MOMENT:**
Conflict resolution has roots in database theory (multi-master replication, 1980s) and was formalized in the distributed systems context by Dynamo (Amazon, 2007): "In cases where conflicts do occur, the system provides mechanisms for the application to resolve them." Dynamo made the key observation: the "correct" resolution is application-specific. A shopping cart merge is different from a user profile update. No universal strategy works for all use cases. Dynamo's contribution: exposing the conflict to the application with enough context (vector clocks showing causality) to resolve it correctly.

**EVOLUTION:**
1980s: Multi-master database replication — first systematic conflict resolution. 1998: CouchDB introduces multi-value conflict storage + application resolution. 2007: Amazon Dynamo paper — vector clock-based conflict detection, application-level resolution. 2011: CRDTs (DST-061) — avoid conflicts by design. 2013: Riak 2.0 — built-in CRDT types as conflict-free alternatives. Today: conflict resolution is a core design consideration in any eventually consistent distributed system; CRDT adoption reduces but doesn't eliminate the need for resolution strategies.

---

### 📘 Textbook Definition

**Conflict Resolution Strategies** are the policies applied when two replicas in a distributed system have diverged: they hold different values for the same data item, resulting from concurrent writes during a partition, replication lag, or multi-master configuration. Strategies differ on: **Who decides** (the system vs the application), **What information is used** (timestamps, vector clocks, value comparison), and **What is lost** (nothing, one value, user intent). **Key strategies:** Last-Write-Wins (LWW): system picks the value with the higher timestamp. Multi-Value (MV): system stores all conflicting values, application resolves. CRDT (DST-061): data structure prevents conflicts mathematically. Application-defined merge: application provides a custom merge function. Server wins / client wins: asymmetric policies for client-server systems. **Causality tracking:** Vector clocks or version vectors provide the causality information needed for conflict detection and resolution — identifying whether two versions are concurrent (neither happened-before the other) or one supersedes the other.

---

### ⏱️ Understand It in 30 Seconds

**One line:** When two replicas diverge, the system must decide: which version wins, who chooses, and what context is preserved.

> Conflict Resolution Strategies are like resolving two people editing the same document simultaneously. Option 1: whoever saved last wins (Last-Write-Wins) — simple but the earlier edit is lost silently. Option 2: show both versions to the author and ask them to resolve (Multi-Value) — correct but requires human effort. Option 3: design the document sections so edits to different sections never conflict (CRDT) — no resolution needed, but only works for certain data shapes. Each strategy has different trade-offs in data loss, complexity, and user experience.

**One insight:** There is no universally correct conflict resolution strategy. The right strategy depends on the application semantics: for shopping carts, merging both versions (add items from both) is correct; for a bank balance, neither version is "correct" without knowing the causal order; for a user's last name, one version must win. Application semantics must drive the choice.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Two writes are concurrent if neither causally precedes the other.** Causality is tracked via vector clocks or Lamport clocks. Two writes V1=[A:1, B:2] and V2=[A:2, B:1] are concurrent (neither is greater than the other in all components). V3=[A:3, B:2] happens-after V1 (not concurrent — V1 is superseded). Only concurrent writes create conflicts requiring resolution.
2. **Any resolution strategy is a trade-off between availability and data fidelity.** LWW maximizes availability (always resolves, no blocking) at the cost of potential data loss. MV maximizes data fidelity (nothing is lost) at the cost of requiring application involvement. CRDT maximizes both but restricts operation semantics.
3. **The resolution strategy must be defined per data type, not per system.** A shopping cart (merge both) has different semantics from a bank balance (order matters, can't merge). Systems that apply a single global strategy (e.g., "always LWW") are wrong for some data types.

**DERIVED DESIGN - Strategy taxonomy:**
```
Strategy 1: Last-Write-Wins (LWW)
  Mechanism: pick version with highest timestamp
  Implementation: physical clock (NTP) or logical clock
  Risk: clock skew -> wrong version wins
        same-timestamp ties -> arbitrary choice
  Use case: user profile settings, config flags
  Data loss: YES (concurrent write with lower ts)

Strategy 2: Multi-Value (Siblings in Riak)
  Mechanism: store ALL concurrent versions
  Detection: vector clock shows no causality between versions
  Resolution: application reads all versions, picks/merges
  Implementation: Riak, CouchDB
  Use case: shopping carts, user-defined merge logic
  Data loss: NO (all versions preserved)
  Cost: application must handle multiple values

Strategy 3: CRDT (see DST-061)
  Mechanism: data structure prevents conflicts mathematically
  Use case: counters, sets, collaborative text
  Data loss: NO
  Restriction: only monotonic operations supported

Strategy 4: Application-Defined Merge
  Mechanism: application provides merge(v1, v2) -> v3
  Example: shopping cart merge = union of items
  Use case: domain-specific semantics
  Implementation: Dynamo application callbacks
  Data loss: depends on merge function quality

Strategy 5: Server Wins / Client Wins
  Mechanism: asymmetric — one side always wins
  Server wins: offline edits discarded on sync
  Client wins: server state overwritten on sync
  Use case: settings sync, non-critical preferences
  Data loss: YES (losing side's changes discarded)

Strategy 6: Operational Transform (OT)
  Mechanism: transform operations to be commutative
  Use case: real-time collaborative text editing
  Implementation: Google Docs (original)
  Data loss: NO
  Complexity: VERY HIGH (correct OT is notoriously hard)
```

**THE TRADE-OFFS:**
**Gain:** Defined behavior during conflicts — no undefined behavior, no crashes, no silent corruption.
**Cost:** Each strategy has costs: LWW silently loses data; MV requires application complexity; OT is extremely complex to implement correctly; CRDT restricts semantics.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The existence of conflicts is essential in any system that allows concurrent writes without coordination (CAP: you chose A over C). Resolution is irreducible.
**Accidental:** Specific vector clock implementations, causal broadcast protocols, and UI for surfacing conflicts to users.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce app has a shopping cart stored in DynamoDB (eventually consistent). User adds "Laptop" from their phone (replica A). Simultaneously (during network partition), a recommendation engine removes "Laptop" (expired deal) and adds "Laptop Pro" from a server process (replica B). Both replicas sync. What should the final cart contain?

**With LWW (Last-Write-Wins):**
- Replica A timestamp: T=1000 (user add Laptop)
- Replica B timestamp: T=1001 (system remove Laptop, add Laptop Pro)
- B wins: cart = ["Laptop Pro"] (user's choice LOST)
- User: "Where did my Laptop go?" (angry customer)

**With Multi-Value (Riak siblings):**
- System stores: V1=["Laptop"], V2=["Laptop Pro"]
- Application merge (union): cart = ["Laptop", "Laptop Pro"]
- User sees BOTH items in cart
- (User can review and remove unwanted item)

**With CRDT (OR-Set):**
- User's add: {("Laptop", tag1)}
- System's operations: remove ("Laptop", tag1), add {("Laptop Pro", tag2)}
- Merge: tag1 removed, tag2 present -> cart = ["Laptop Pro"]
- (CRDT gives "add-wins" semantics for concurrent add+remove of same item, but system's remove was explicit of tag1 -> respects system's intent)

**THE INSIGHT:** The "correct" answer depends on business logic: should system recommendation overrides win over user choices? The conflict resolution strategy must encode this business logic. No technical strategy can substitute for the business decision.

---

### 🧠 Mental Model / Analogy

> Conflict resolution strategies are like editing policies for a shared whiteboard. "Last to erase wins" (LWW): whoever edited most recently owns the board — quick, but earlier work gets erased. "Split the board" (Multi-Value): show both versions simultaneously — nothing lost, but the board is cluttered until someone decides. "Designated sections" (CRDT): each person has their own section to edit — no overlap possible, so no conflicts, but editing the other person's section isn't allowed. "Committee decides" (Application merge): a designated committee reviews both versions and produces a final merged version — most correct but slowest. The right policy depends on: how frequently conflicts occur, how important each person's edits are, and how quickly you need resolution.

**Mapping:**
- **Whiteboard content** -> replicated data item
- **Two people editing simultaneously** -> concurrent writes from two replicas
- **Erased work** -> data lost in LWW conflict
- **Split board** -> multi-value siblings stored by Riak/CouchDB
- **Committee** -> application-defined merge function

Where this analogy breaks down: in distributed systems, conflicts can happen across thousands of replicas simultaneously. "Committee decides" at scale means the application's merge function runs automatically — there's no human in the loop for each conflict.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When two computers update the same file at the same time without knowing about each other, they'll have different versions. When they reconnect, the system needs a rule for which version to keep. Different rules exist: "keep the newest one," "keep both and ask the user," or "design files so they can always be combined." Each rule has pros and cons.

**Level 2 - How to use it (junior developer):**
DynamoDB: uses "last-writer-wins" by default (based on timestamp). To get multi-value: use optimistic locking with conditional writes (`ConditionExpression: attribute_not_exists(version) OR version = :expected`). CouchDB: stores all conflicting revisions as "leaves" — read returns all revisions, application chooses. Cassandra: uses LWW by default — all writes have a timestamp, highest timestamp wins. For conflict-free counters: use Cassandra counters (CRDT-based). Riak: use CRDT types (`riak_dt_counter`, `riak_dt_set`, `riak_dt_map`) for conflict-free, or use vector clocks + sibling merge for application-defined resolution.

**Level 3 - How it works (mid-level engineer):**
Vector clock-based conflict detection: Each write carries a vector clock (e.g., `[A:2, B:1]` meaning "I've seen 2 writes from A and 1 from B"). When two versions are compared: if V1's vector clock is less-than-or-equal to V2's in all components (V1 <= V2), V1 is superseded (V2 happened-after). If neither V1 <= V2 nor V2 <= V1: they are CONCURRENT and a conflict exists. This is the precise definition of conflict: two versions where neither causally preceded the other.

```
V1 = [A:2, B:1]   (version after A wrote twice, B once)
V2 = [A:1, B:2]   (version after A wrote once, B twice)
V1 <= V2? No (A:2 > A:1)
V2 <= V1? No (B:2 > B:1)
-> CONCURRENT -> CONFLICT
```

**Level 4 - Why it was designed this way (senior/staff):**
The Dynamo paper's key insight: "The shopping cart application requires that 'never loses a customer's shopping cart data' even at the cost of having conflicting cart versions." This led to the multi-value approach: store all conflicting versions (called "siblings" in Riak), let the application merge on next write. Dynamo used vector clocks to track causality so the application knows WHICH versions are concurrent (need merging) vs which are superseded (safe to discard). The engineering lesson: conflict resolution strategy must match application semantics. Dynamo showed that a generic "last-write-wins" was wrong for shopping carts (loses customer intent) and a generic "multi-value" was wrong for simple flags (unnecessary complexity). The strategy is part of the data model design.

**Expert Thinking Cues:**
- "Our Cassandra cluster has data inconsistencies — wrong values after partition healed" -> Cassandra uses LWW with Cassandra-assigned timestamps. If clocks on nodes drift: wrong version wins. Check NTP sync across all nodes. Use application-assigned timestamps (or UUID-v1 with embedded time) for critical data. Consider: does your use case actually need LWW, or do you need application-defined merge?
- "Riak returning 'siblings' (multiple values) for every read" -> Normal behavior when multi-value is configured. Application must merge siblings on write: `riak_client.put(obj.resolve(mergeFunction))`. Alert: if sibling count grows unboundedly (>10): application is not resolving siblings. This is a bug — unresolved siblings grow on each write, eventually causing performance issues.
- "DynamoDB conditional write keeps failing under high concurrency" -> Optimistic locking is contended. With many concurrent writers: most fail the condition check and retry. For high-write scenarios: use DynamoDB's atomic `ADD` operation (CRDT-like: atomic increment/decrement) instead of read-modify-write pattern.

---

### ⚙️ How It Works (Mechanism)

**Vector clock conflict detection:**
```
Initial state: {} (no writes yet)

Write from A: value="Alice", vc=[A:1]
  Replica 1: "Alice", vc=[A:1]
  Replica 2: "Alice", vc=[A:1]  (replicated)

Network partition (Replica 1 and 2 diverge):
Write from A on Replica 1: value="Alice Smith", vc=[A:2]
Write from B on Replica 2: value="Alice Brown", vc=[A:1, B:1]

Partition heals. Compare versions:
  V1=[A:2]:       "Alice Smith"
  V2=[A:1, B:1]:  "Alice Brown"
  V1 <= V2? A:2 > A:1 -> NO
  V2 <= V1? B:1 > B:0 -> NO
  -> CONCURRENT -> CONFLICT

Resolution options:
  LWW: compare physical timestamps, pick newer
  MV:  store both ["Alice Smith", "Alice Brown"]
  App: merge(v1, v2) -> "Alice Smith Brown"?
       (depends on business logic)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**WRITE CONFLICT -> DETECTION -> RESOLUTION:**

```
Client  Replica A  Network  Replica B  Application
  |        |          |         |           |
  |-write->| "Alice"  |[partition]|          |
  |        |          |         |           |
  |        | A writes  |         | B writes  |
  |        | "A.Smith" |         | "A.Brown" |
  |        |          |[reconnect]|          |
  |        |--state-->|-------->|           |
  |        |          |   <- YOU ARE HERE   |
  |        |          |[conflict detected via vc]
  |        |          |         |--conflict->|
  |        |          |         |           |[merge()]
  |        |          |         |<--resolved-|
  |<-result|          |         |           |
```

**WHAT CHANGES AT SCALE:**
At very high write rates: vector clocks grow unboundedly (one entry per writer). DynamoDB removed vector clocks from its public API partly due to this issue — clock sizes grew with number of unique writers. Solutions: (1) bound vector clock size (prune old entries — risk: false negatives for conflict detection), (2) use hybrid logical clocks (HLC: combines physical + logical time), (3) use CRDT data structures to eliminate conflicts entirely.

---

### 💻 Code Example

**BAD - LWW without causality tracking (silent data loss):**
```java
// BAD: LWW with physical timestamps only
// No causality tracking: wrong version can win
// on clock skew; conflicts not surfaced to app

@DynamoDbBean
class UserProfile {
    String userId;
    String email;
    long lastModified; // physical timestamp -- DANGER
}

// Node A writes email=alice@a.com at T=1000
// Node B writes email=alice@b.com at T=999 (clock skew)
// Sync: B's T=999 < A's T=1000 -> A wins
// BUT: B wrote AFTER A in wall-clock time (just clock skew)
// B's actual later write is silently lost
```

**GOOD - Multi-Value with application merge (Riak-style):**
```java
// GOOD: multi-value with vector clocks + explicit merge
// No silent data loss; application defines semantics

class ShoppingCart {
    String cartId;
    List<String> items;
    VectorClock vectorClock;
}

// Custom merge: union of all sibling carts
// (Dynamo-style shopping cart merge)
static ShoppingCart merge(List<ShoppingCart> siblings) {
    Set<String> allItems = new LinkedHashSet<>();
    VectorClock mergedClock = new VectorClock();
    for (ShoppingCart sibling : siblings) {
        allItems.addAll(sibling.items);
        mergedClock = mergedClock.merge(sibling.vectorClock);
    }
    return new ShoppingCart(
        siblings.get(0).cartId,
        new ArrayList<>(allItems),
        mergedClock.increment(myNodeId) // advance clock on write
    );
}

// On read: check for siblings (concurrent versions)
List<ShoppingCart> carts = riakClient.fetch(cartId);
ShoppingCart resolved = carts.size() == 1
    ? carts.get(0)          // no conflict
    : merge(carts);          // merge siblings
riakClient.put(resolved);    // write back resolved version
// Items from ALL concurrent versions preserved -- no data loss

// How to verify: write concurrent carts -> read -> check
// both items present in merged result
```

---

### ⚖️ Comparison Table

| Strategy | Data Loss | Complexity | App Involvement | Use Case |
|:---|:---|:---|:---|:---|
| Last-Write-Wins | Yes (lower ts) | Low | None | Config, flags, preferences |
| Multi-Value | No | Medium | High (must merge) | Shopping carts, docs |
| CRDT | No | Medium | None (by design) | Counters, sets, text |
| OT | No | Very High | None | Real-time text editing |
| Application merge | Depends | Medium-High | High (define merge fn) | Domain-specific |
| Server/Client wins | Yes (losing side) | Low | None | Offline sync, settings |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Last-Write-Wins is safe if we use NTP-synchronized clocks" | NTP synchronization reduces clock skew but does not eliminate it. NTP typically achieves ~1ms accuracy but can drift up to 10-100ms under network load. Two writes 1ms apart from different nodes may have clock skew greater than 1ms -> wrong version wins. For high-value data: use logical clocks (Lamport, vector clocks) which track causality correctly. For low-value data (preferences, display settings): NTP-based LWW is acceptable. |
| "Storing multiple versions (Multi-Value) means the conflict is 'unresolved'" | Multi-Value is a STRATEGY, not an error state. Riak's "siblings" are intentionally stored concurrent versions — the application resolves them by reading all versions and writing a merged result. This is correct behavior, not a bug. The "conflict" is surfaced to the application that has the domain knowledge to resolve it correctly. Systems that hide conflicts (LWW) are actually LESS correct than systems that surface them (Multi-Value). |
| "CRDTs eliminate the need for conflict resolution" | CRDTs eliminate conflicts for the operations they support (add, increment, union). For operations outside CRDT semantics (arbitrary value replacement, application-specific merging), conflicts still occur and require resolution. CRDTs also don't handle "intent conflicts" — a CRDT shopping cart might add both "Laptop" and "Laptop Pro" when only one was intended. The user still needs to review and decide. |
| "Conflict resolution is only needed for multi-master databases" | Conflict resolution is needed in any system with multiple independent writers: (1) offline-first mobile apps (device writes without sync), (2) CDN edge caches (edge writes before syncing to origin), (3) microservices with local state (each service owns its replica of shared data), (4) eventual consistency databases even in single-master (replicas lag -> writes before replicas catch up -> partition -> conflict). Any system that prioritizes availability over consistency under network failure will experience conflicts. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Silent Data Loss from Clock Skew in LWW System**

**Symptom:** User updates profile name on mobile (T=1000ms) and on desktop (T=999ms, 1ms clock skew). Mobile sync happens after desktop. System applies LWW: desktop's timestamp 999 < mobile's 1000 -> mobile's update wins. But: the desktop update was actually made AFTER the mobile update (user corrected a typo on desktop after seeing it on mobile). The "later" physical write (desktop) has a lower timestamp due to clock skew -> silently lost.
**Root Cause:** Physical timestamps are an approximation of causality, not a guarantee. Clock skew (NTP drift, leap seconds, VM clock pause) can make timestamps unreliable for ordering concurrent writes. LWW picks "higher timestamp" not "causally later write."
**Diagnostic:**
```bash
# Check clock drift between nodes:
# On each node:
chronyc tracking | grep "System time"
# Acceptable drift: < 1ms within same datacenter
# > 10ms: LWW is unreliable for concurrent writes

# Check for frequent "same-timestamp" conflicts in DynamoDB:
aws dynamodb get-item ... | jq '.Item.last_modified'
# If timestamps frequently equal: LWW choices are arbitrary

# Check if user-reported data loss correlates with
# multi-device activity (offline + reconnect pattern):
grep "profile-update.*conflict" app.log | \
  sort | uniq -c | sort -rn
```
**Fix:** Switch from physical timestamps to hybrid logical clocks (HLC) for ordering: HLCs combine physical time + logical counter. HLC is always >= physical time and advances on each event. Two events on the same node: HLC is strictly ordered. Two events on different nodes: HLC correctly orders if causally related, treats as concurrent otherwise. For high-value data: use multi-value with explicit conflict surfacing instead of LWW.
**Prevention:** Use HLC (e.g., Cockroach DB's implementation) for any LWW system where ordering matters. Monitor clock drift — alert if any node's drift > 5ms. For offline-first apps: use logical clocks (vector clocks) not physical timestamps for conflict detection.

**Failure Mode 2: Riak Siblings Growing Unboundedly (Application Not Resolving)**

**Symptom:** A Riak cluster running with `allow_mult=true` (multi-value mode) starts showing degraded read performance and large object sizes. Monitoring: average sibling count = 50 per key. Some keys have 500+ siblings. Every write to a key creates a new sibling instead of resolving existing ones. Application never calls the merge function on read.
**Root Cause:** The application reads Riak values but doesn't check for siblings (multiple values). The application writes new values without first resolving siblings. Each write adds a new sibling. Over time: sibling count grows unboundedly. Riak stores ALL siblings — object size grows with every unresolved write. Reads become slow (returning 50+ sibling values).
**Diagnostic:**
```bash
# Check sibling count per bucket:
riak-admin bucket-type status shopping-cart | \
  grep "siblings"
# Check object size distribution:
riak-admin stat | grep "riak_kv_node_gets_siblings"

# Count siblings for a specific key:
riak-client.fetch("cart", user_id).siblings().size()
# If > 3: application not resolving conflicts

# Check application code for sibling handling:
grep -r "siblings\|resolve\|merge" app/riak_client.py
# If not found: application doesn't handle siblings
```
**Fix:** Implement sibling resolution on every read: always read all siblings, apply merge function, write back resolved value. This is the Riak-recommended pattern:
```python
def get_and_resolve(client, bucket, key, merge_fn):
    result = client.bucket(bucket).get(key)
    if result.exists:
        resolved = merge_fn(result.siblings)
        resolved.store()  # write back resolved value
    return resolved
```
**Prevention:** All Riak reads must use sibling resolution. Add integration tests that create conflicts and verify resolution. Monitor: alert if any key has > 5 siblings. Set `max_siblings` in Riak config to cap growth (writes fail when exceeded, forcing fix).

**Failure Mode 3: Security - Conflict Injection Attack via Timestamp Manipulation**

**Symptom:** A financial application uses LWW to resolve conflicts in a transaction ledger replica. An attacker with access to one node manipulates the system clock backward by 1 hour, writes a fraudulent transaction (sets balance to 0), then resets the clock. The fraudulent write has a timestamp 1 hour in the past. Legitimate writes after the fraudulent write have higher timestamps -> they "win" via LWW. Except: a replica that receives the fraudulent write before legitimate writes applies LWW, sees the fraudulent write's timestamp is lower -> discards fraudulent write? No: LWW picks HIGHEST timestamp. Fraudulent write (T-1 hour) < legitimate writes -> fraudulent write LOSES (discarded). But: what if the attacker sets clock FORWARD by 1 hour? Fraudulent write has T+1 hour. All legitimate writes have T (current time) < T+1 hour -> fraudulent write WINS. Balance overwritten to 0 for all future reads until another write happens after T+1 hour.
**Root Cause:** LWW's correctness depends on clock integrity. An attacker who can manipulate a node's clock can make any write "win" by setting the clock to the future. Physical timestamps are not Byzantine-fault-tolerant.
**Diagnostic:**
```bash
# Check for anomalous future timestamps in DynamoDB:
aws dynamodb query ... | jq '.Items[] | .timestamp' | \
  awk -v now=$(date +%s) '$1 > now+3600 {print "FUTURE:", $1}'
# Future timestamps: clock manipulation or bug

# Check node clock integrity:
timedatectl status | grep -E "synchronized|NTP"
# If NTP not synchronized: clock may drift or be manipulated

# Check for large clock jumps in logs:
journalctl -u chronyd | grep "offset\|step"
# Large jumps: clock was manipulated or NTP re-sync
```
**Fix:** For financial data: never use physical LWW. Use logical clocks (monotonically increasing sequence numbers from a trusted source, not node clocks). Use multi-value with explicit application resolution (auditor reviews conflicts). Use distributed consensus (Raft) for high-integrity financial data. Bound timestamp acceptance: reject any write with timestamp > now + 60 seconds (prevents future-dating attacks).
**Prevention:** Critical data must not use physical-timestamp LWW. Apply NTP bounds checking: if node clock jumps > 1 second, alert and halt writes until re-verified. Use mTLS between replicas — only authenticated nodes can submit writes. Apply write-time validation: reject writes with physically implausible timestamps (future or too far past).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-061 - CRDT (understanding what conflict-free alternatives look like)

**Builds On This (learn these next):**
- DST-063 - Anti-Entropy (how conflicting versions are discovered and resolved)

**Alternatives / Comparisons:**
- DST-061 - CRDT (alternative: design away conflicts mathematically)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Policy for resolving diverged  |
|                  | replica values after concurrent|
|                  | writes (LWW, MV, CRDT, merge)  |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Multi-master / offline writes  |
|                  | produce conflicting versions;  |
|                  | system needs defined behavior  |
+------------------+--------------------------------+
| KEY INSIGHT      | No universal strategy -- right |
|                  | choice depends on app semantics|
|                  | (shopping cart != bank balance)|
+------------------+--------------------------------+
| USE WHEN         | Any eventually consistent DB;  |
|                  | offline-first mobile; multi-   |
|                  | master replication; active-    |
|                  | active deployment              |
+------------------+--------------------------------+
| AVOID WHEN       | N/A: conflicts will happen in  |
|                  | any AP system -- strategy must |
|                  | be defined, cannot be avoided  |
+------------------+--------------------------------+
| TRADE-OFF        | Data fidelity vs complexity:   |
|                  | LWW (simple, loses data) vs    |
|                  | MV (complex, loses nothing)    |
+------------------+--------------------------------+
| ONE-LINER        | Concurrent writes WILL diverge;|
|                  | define resolution BEFORE it    |
|                  | happens, not after             |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-061 CRDT; DST-063 Anti-    |
|                  | Entropy; Dynamo paper (2007)   |
+------------------+--------------------------------+
```

**If you remember only 3 things:**
1. The right conflict resolution strategy is application-specific, not database-specific. Shopping cart: merge all versions (union). Bank balance: coordinate (don't allow concurrent writes). Display name: LWW is usually fine. Choosing the wrong strategy for your data causes either silent data loss (LWW on critical data) or unnecessary complexity (MV on non-critical data).
2. Last-Write-Wins requires clock integrity — physical timestamps are an approximation of causality. Clock skew, NTP drift, and clock manipulation can cause the "wrong" version to win. For high-value data: use logical clocks (vector clocks, HLC) or multi-value conflict surfacing.
3. Define your conflict resolution strategy BEFORE your system has its first partition. Retrofitting conflict resolution after a data loss incident is much harder than designing it upfront. Every eventually consistent database/configuration should have an explicit documented conflict resolution policy.

**Interview one-liner:**
"Conflict Resolution Strategies define what happens when replicas diverge due to concurrent writes. The main strategies: Last-Write-Wins (system picks highest timestamp — simple but can lose data to clock skew), Multi-Value (store all concurrent versions, application merges — no data loss but requires application logic), CRDT (design data structure to prevent conflicts mathematically — restricted operations), and Application-Defined Merge (custom merge function encoding domain semantics). The right strategy is application-specific: Amazon Dynamo's shopping cart uses multi-value union merge; user profile flags use LWW. Vector clocks detect WHICH versions are concurrent (neither causally precedes the other) — without causality tracking, conflict detection itself is unreliable."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define conflict resolution policy at data model design time, not at runtime when a conflict occurs. The principle: any data that can be written from multiple sources simultaneously MUST have a defined merge semantics. Retrofitting conflict resolution after data loss is costly and incomplete. This applies beyond distributed systems: version control (git merge strategies: recursive, ours, theirs), configuration management (which config file takes precedence?), and API versioning (what happens when a v1 client and v2 client update the same resource?). In all cases: define the resolution rule before the conflict happens, in the data model itself.

**Where else this pattern appears:**
- **Git merge strategies.** Git's `git merge` uses three-way merge (common ancestor + both branches). Conflicts occur when the same line is modified in both branches (no common ancestor resolution). Git's resolution strategies: `recursive` (default, handles most cases), `ours` (current branch wins), `theirs` (incoming branch wins), `octopus` (multi-branch merge). These are exactly the distributed conflict resolution strategies: `ours`/`theirs` = LWW (one side wins), `recursive` = application-defined merge (3-way merge algorithm). Git surfaces unresolvable conflicts to the developer (multi-value approach). The same mathematical structure as distributed database conflict resolution.
- **DNS TTL and zone file conflicts.** When multiple DNS servers have authority for the same zone (secondary nameservers), zone transfers propagate updates. If a primary and secondary have conflicting records (network partition + both updated): which record wins? DNS uses "higher serial number wins" (SOA serial number in zone file) — a form of LWW using a logical counter. This is version-based LWW: not physical timestamps, but a monotonically increasing counter. The pattern: use logical counters (not physical clocks) for LWW to avoid clock skew issues.
- **Document editors: autosave conflict handling.** When a document is open on two devices simultaneously (offline) and both autosave: Dropbox creates "conflicted copy" files (multi-value approach). Google Drive uses OT/CRDT for real-time collaboration. Office 365 shows conflict notification and lets user choose version (multi-value + user resolution). All three are valid conflict resolution strategies with different trade-offs: Dropbox prioritizes data preservation, Google prioritizes seamless merging, Office prioritizes user awareness.

---

### 💡 The Surprising Truth

The Amazon Dynamo paper (2007) that popularized vector clocks and application-level conflict resolution made a choice that most distributed systems engineers disagree with in hindsight: it shifted the burden of conflict resolution to application developers. Jeff Bezos and the Dynamo team argued: "The application developers know the semantics of their data better than the database can." For Amazon's shopping cart: this was correct (union merge is the right business logic). But: most applications don't have clear merge semantics. The surprising truth: **the vast majority of teams who deployed eventually consistent databases expecting to implement "custom conflict resolution" never actually implemented it** — they either accepted silent data loss (LWW was the default) or they discovered their application couldn't tolerate conflicts and reverted to strongly consistent databases. The Dynamo paper inspired an entire generation of NoSQL databases that exposed conflict resolution to applications — and most applications defaulted to LWW or accepted conflicts as acceptable data loss. The lesson: correct conflict resolution is hard enough that systems should default to preventing conflicts (CRDTs, strong consistency) rather than expecting applications to resolve them correctly.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A ride-sharing app stores driver location as a replicated value across 3 data centers (active-active). Drivers update their location every 2 seconds. The system currently uses LWW with physical timestamps. What are the failure modes? Under what conditions does LWW produce incorrect results? What alternative strategy would you recommend and why?
*Hint:* LWW failure modes for driver location: (1) Clock skew: if data center B's clock is 100ms behind A's, and driver updates from DC-A (T=1000) and DC-B (T=900 due to skew) are concurrent — DC-A's older location wins over DC-B's newer location. Driver appears to be at their 2-second-old position. (2) Partition + reconnect: if DC-A is partitioned for 30 seconds, DC-A has 15 stale location updates. On reconnect, some may have higher timestamps than DC-B's current values -> stale locations overwrite current positions. Alternative: Use HLC (Hybrid Logical Clocks) instead of physical timestamps — HLC is causally ordered and handles clock skew correctly. OR: for location data, LWW is actually acceptable (2-second old location is not critical data loss — driver is moving and will update again). The key question: what is the cost of a wrong location? For driver dispatch (which driver to assign): 2-second-old location matters but a brief incorrect assignment self-corrects on next update. For safety-critical tracking (911 service): strong consistency required. Strategy: for non-safety-critical: LWW with HLC is fine. For safety-critical: use a consensus-based approach (Raft leader per driver ID) to avoid conflicts entirely.

**Q2 (D - Root Cause):** A CouchDB deployment uses multi-value conflict storage (revision tree). After 6 months of operation, the ops team runs a routine consistency check and finds: 40% of documents have unresolved conflicts (multiple leaf revisions). Some documents have 100+ conflicting revisions. These conflicts are from 6 months ago. New writes continue adding revisions without resolving old conflicts. What went wrong? How do you fix 6 months of accumulated conflicts?
*Hint:* Root cause: the application writes to CouchDB but never reads-and-resolves conflicts. CouchDB's multi-value approach requires an active loop: read -> detect siblings -> merge -> write resolved version. If the application only writes (never reads-then-resolves): conflicts accumulate forever. Each write adds a new leaf revision without pruning the tree. After 6 months: the revision tree is a deep, branching structure. CouchDB sends ALL revisions in the tree on reads — O(n) where n = number of unresolved conflicts. Fix procedure: (1) write a migration script that iterates all documents, reads all revisions, applies merge function, writes resolved version; (2) run during low-traffic period (conflict resolution writes are normal writes); (3) verify conflict count decreases to 0. For 100+ conflict documents: the merge function might need to be run iteratively (merge pairs of conflicts, then merge results). Future prevention: implement a background conflict resolution worker — continuously polls for documents with > 1 revision and resolves them. Alert on conflict count > 5 per document.

**Q3 (A - System Interaction):** A distributed database uses vector clocks for causality tracking. The vector clock has one entry per UNIQUE WRITER. The system has 1000 clients writing directly to the database. After 6 months, each vector clock entry has 1000 entries (one per client). Write performance degrades: vector clock comparison is O(n). Reads are slow: vector clocks are returned with every object. What happens to vector clock size over time? What are the engineering solutions to this problem (at least 2 different approaches)?
*Hint:* Vector clock growth: each unique writer adds an entry to the vector clock. With 1000 clients, each vc has 1000 entries. If client population is ephemeral (new clients every hour), the vc grows unboundedly: 24 clients/hour × 24 hours × 180 days = 103,680 entries per vc after 6 months. Each vc comparison: O(n) = O(103,680) per read/write. At 10,000 writes/second: 10^9 vector clock comparisons/second. Engineering solutions: (1) VERSION VECTOR PRUNING: periodically compact vector clocks by removing entries where all other vector clocks have seen at least that version. This requires a "garbage collection" coordination round — all nodes agree on a global lower bound. Risk: false negatives (incorrectly merge causally unrelated versions). (2) DOTTED VERSION VECTORS: use node-based (not client-based) vector clocks. Instead of 1000 client entries: 3 database node entries. Clients don't get their own vc entry — the node that received the write represents it. Clients must include the node's vc entry, not their own. O(3) comparison instead of O(1000). Used in: Riak's vector clocks (node-based). (3) LOGICAL TIMESTAMPS WITH CAUSAL COOKIES: use HLC (Hybrid Logical Clock) — single monotonic timestamp per node. Clients carry the HLC cookie; servers compare cookies. O(n_nodes) not O(n_clients). Used in: CockroachDB's MVCC timestamps. (4) PESSIMISTIC LOCKING for high-conflict keys: if a specific key has many concurrent writers, use per-key leader election (Raft for that key) — eliminates conflicts entirely at the cost of coordination overhead for that key.
'@

$f = Join-Path $base "DST-062 - Conflict Resolution Strategies.md"
[System.IO.File]::WriteAllText($f, $newContent, [System.Text.Encoding]::UTF8)
Write-Host "DST-062 written: $((Get-Content $f -Encoding UTF8).Count) lines"
