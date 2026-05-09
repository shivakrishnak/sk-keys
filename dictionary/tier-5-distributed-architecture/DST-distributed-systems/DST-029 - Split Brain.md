---
id: DST-029
title: Split Brain
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-028, DST-022, DST-006
used_by: DST-030
related: DST-028, DST-030, DST-006, DST-022
tags:
  - distributed
  - reliability
  - architecture
  - deep-dive
  - antipattern
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /distributed-systems/split-brain/
---

# DST-029 - Split Brain

⚡ TL;DR - Split brain is the catastrophic condition where a network partition causes two or more nodes to simultaneously believe they are the authoritative primary, resulting in divergent writes and irreconcilable data corruption.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-028, DST-022, DST-006          |     |
| **Used by:**    | DST-030                            |     |
| **Related:**    | DST-028, DST-030, DST-006, DST-022 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Understanding split brain is not about solving it — split brain is ITSELF the problem. It is the catastrophic failure mode in distributed systems that all replication and consensus protocols exist to prevent. A system that does not understand split brain cannot design against it.

**THE BREAKING POINT:**
A hospital runs a primary and a standby database for patient records. A network issue between the two sites lasts 45 seconds. During that time: the standby promotes itself to primary (the keepalived health check declares the primary "dead"). The original primary, still running, continues accepting writes (it sees itself as healthy — only the network link to the standby is broken). For 45 seconds, both databases accept writes. The network heals. Two conflicting versions of "truth" exist: lab results written to one, medication orders written to the other. Merging them is impossible without knowing which copy is correct. This is split brain.

**THE INVENTION MOMENT:**
Split brain became a recognized failure class when high-availability database clusters proliferated in the 1990s. MySQL master-master replication (without quorum), Heartbeat/DRBD Linux HA clusters, and early Oracle RAC implementations all encountered it. The solution frameworks — STONITH (Shoot The Other Node In The Head), quorum-based fencing, Paxos/Raft consensus — emerged directly as responses to observed split-brain incidents.

**EVOLUTION:**
1990s: Split brain encountered in early HA database clusters. 2000s: STONITH and fencing mechanisms formalized in Pacemaker/DRBD. 2007: Raft and Paxos become mainstream — consensus eliminates split brain by design. 2012: Jepsen project (Kyle Kingsbury) systematically exposed split-brain vulnerabilities in production databases (MongoDB, Redis, Elasticsearch). 2020s: Managed Kubernetes (etcd) and cloud databases (Aurora, Spanner) built on Raft/Paxos — split brain essentially eliminated in this tier.

---

### 📘 Textbook Definition

**Split brain** is a distributed systems failure mode in which a network partition causes two or more nodes to simultaneously claim the role of primary/leader and accept writes independently. Each node believes the other has failed (because it cannot communicate with it), promotes itself, and accepts writes. When the partition heals: the cluster has two divergent states with no deterministic merge strategy. Three necessary conditions: (1) **Multiple nodes capable of accepting writes** (no quorum requirement, or quorum improperly enforced); (2) **Network partition** (nodes cannot communicate); (3) **No external arbitration** (no STONITH, no fencing token, no quorum-based voting that would prevent both sides from proceeding). Prevention strategies: quorum-based voting (mathematical guarantee that two majorities can't form), fencing tokens (storage-level enforcement of single authority), STONITH (physically kill the other node before proceeding).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Split brain = network partition + two nodes both think they're primary = two conflicting databases = data corruption.

> Split brain is like a king dying with two heirs who can't reach each other. Each heir proclaims himself king. Each rules his territory. Each signs decrees. When messengers finally arrive between kingdoms: two conflicting sets of laws exist. Which king's decrees are valid? The kingdom has no way to decide.

**One insight:** Split brain is not a failure of hardware or software — it is a failure of the assumption that a primary can detect its own secondary-ness. A node cannot reliably determine whether it's been replaced: "Am I still the primary, or has a new primary been elected while I was partitioned?" Without external proof (fencing token, quorum ACK), the answer is unknowable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Single-writer requirement:** In a system with strong consistency, only ONE node may accept writes at any moment. Any protocol allowing two simultaneous writers produces divergent state.
2. **Partition detectability impossibility:** A partitioned node cannot distinguish "the other node is dead" from "I cannot reach the other node." Both look identical from inside the partition.
3. **Timeout-based promotion = race condition:** Any failover protocol based on "wait N seconds, then promote" creates a window where both primary and promoted secondary are simultaneously active.
4. **Quorum as mathematical split-brain prevention:** If both sides need N/2+1 nodes to proceed, and they can't collectively have N+2 nodes from N total, at most one side can proceed. This is the ONLY mathematical guarantee against split-brain.

**DERIVED DESIGN:**
Split brain prevention requires ONE of: (a) **Quorum voting** — only a majority can proceed (Raft, Paxos). (b) **Fencing** — before accepting writes, a new primary must prove it has invalidated the old primary's authority (fencing token, STONITH). (c) **External arbitration** — a quorum device or witness node that all sides must consult before promoting.

**THE TRADE-OFFS:**
**Gain:** Split brain prevention guarantees single-writer semantics even during network partitions.
**Cost:** A minority partition MUST stop accepting writes (CA→C; CP, not AP). Availability is sacrificed for safety. This is the CAP theorem in action: consistent or available, not both, during partitions.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** In an asynchronous network, you cannot build a protocol that is both safe (no split-brain) and live (always processes writes) during partitions. This is FLP impossibility applied to split-brain. Some writes must be blocked.
**Accidental:** Different split-brain prevention implementations (STONITH vs. Raft vs. quorum device) vary in operational complexity and failure modes, but the essential trade-off (sacrifice availability for safety) is unavoidable.

---

### 🧪 Thought Experiment

**SETUP:** Two database nodes: Primary (P) and Secondary (S). No quorum. Failover mechanism: "if heartbeat lost for 30 seconds, S promotes to Primary." Both P and S are healthy. A network switch firmware update takes 45 seconds and drops the P-S heartbeat link.

**TIMELINE WITHOUT QUORUM:**

- T=0s: Network switch restarts. P and S lose visibility of each other.
- T=0-30s: P continues serving writes. S waits (heartbeat timeout = 30s).
- T=30s: S declares P "dead." S promotes itself to primary. S starts accepting writes.
- T=30-45s: BOTH P and S are accepting writes. Clients routed to S (via VIP failover) write to S. Clients NOT yet re-routed write to P.
- T=45s: Network switch comes back up. P and S try to re-sync.
- PROBLEM: P has writes [W1, W2, W3]. S has writes [W4, W5]. These are different data at the same keys. No merge is possible.

**WITH QUORUM (3-node Raft cluster):**

- T=0s: Same network issue. P (leader) loses contact with S.
- T=0-election: P still has votes from a third node. Continues as leader.
- Or: P is partitioned from both S and third node. P now has 1 vote (only itself). Below quorum. P STOPS accepting writes. S and third node form majority (2 of 3). New leader elected. No split brain.

**THE INSIGHT:** Quorum is the mathematical proof that two primaries can't exist simultaneously. Timeout-based failover without quorum is the mathematical recipe for split brain.

---

### 🧠 Mental Model / Analogy

> Split brain is like two autonomous car systems simultaneously believing they have the steering wheel. When the wireless link between driver assistance and backup system drops: the backup assumes the primary is dead and takes control. Both systems now send conflicting steering signals. The car doesn't know which to follow.

**Mapping:**

- **Car** → database cluster
- **Steering control** → write authority / leader status
- **Wireless link drop** → network partition
- **Backup taking control** → secondary auto-promotion
- **Conflicting steering signals** → divergent writes
- **Car not knowing which to follow** → cluster with two primaries, no arbiter

Where this analogy breaks down: cars have physical hardwiring to resolve conflicts. Distributed systems have no such physical channel — all resolution must happen through the same unreliable network.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Split brain happens when a network problem causes two database servers to both think they're in charge, and both start accepting changes at the same time. When the network heals, the two servers have different data, and there's no way to know which one is correct. It's the most dangerous failure in distributed databases.

**Level 2 - How to use it (junior developer):**
As a developer, split brain means you should NEVER use a two-node HA database without a quorum device or arbiter. A two-node PostgreSQL cluster with keepalived failover is split-brain vulnerable: if the network between them drops, both sides promote. Use at minimum three nodes (or a cloud-managed database with built-in Raft, like Aurora, Cloud Spanner, or managed etcd).

**Level 3 - How it works (mid-level engineer):**
Split brain in MySQL master-master setups: both nodes accept writes. Writes replicate asynchronously. During partition: writes go to both nodes independently. Same row updated differently on each. On reconnection: replication detects duplicate key or conflicting row. `Duplicate key error` or silently last-write-wins by timestamp (which is wrong). Percona XtraDB Cluster with Galera uses wsrep quorum: a node must be part of a primary component (majority) to accept writes. Minority component goes read-only. This is quorum-enforced split-brain prevention at the middleware level.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental reason split brain is so dangerous is that it violates the atomic commitment property: a transaction committed on one node is considered final. When the same key is later written by a different "primary" on a different partition, you have two separate "committed" values at the same key from two different moments in time — and no master clock to determine ordering. The write ordering invariant is broken at the system level, not the application level. No application-layer merge logic can fix this: you'd need to understand the business semantics of every conflicting write to decide which is "correct." The only safe fix is to prevent the condition mathematically (quorum) or physically (STONITH) before divergence occurs. After divergence: you have a data integrity incident, not a distributed systems incident.

**Expert Thinking Cues:**

- "Our Redis Sentinel cluster shows two masters" → Classic split brain. Sentinel uses quorum voting but may be misconfigured (min-slaves-to-write not set). Both Sentinel groups may have independently promoted different replicas.
- "Jepsen tests show our database loses writes during partitions" → Could be split brain (writes accepted by both sides, one side's writes lost) or could be async replication loss. The difference: split brain diverges data; async loss drops data. Both are consistency violations.
- "Our PostgreSQL cluster took 40 seconds to failover" → If using Patroni with etcd: DCS (distributed configuration store) TTL-based. Not split brain if Patroni uses etcd quorum correctly. If without Patroni: timeout-based promotion → split brain risk.
- "Two pods claiming to be the leader in Kubernetes" → Leader election via ConfigMap/Lease object in Kubernetes API (backed by etcd). Unless client-side lease expiry check is skipped. Review leader election logic.

---

### ⚙️ How It Works (Mechanism)

**Split brain occurrence sequence:**

```
Normal state:
  Primary (P): accepting writes, replicating to S
  Secondary (S): replicating from P, ready for failover

Network partition event:
  P ←── partition ──→ S  (no communication)

Without quorum:
  P: "I'm still primary, S must be dead" → continues writes
  S: "P is dead (heartbeat timeout)" → promotes to primary
  BOTH ACTIVE → split brain

  Writes to P: [SET x=1, SET y=2]
  Writes to S: [SET x=99, SET z=3]  (different data!)

Partition heals:
  P and S reconnect. P has x=1, S has x=99.
  Which is correct? UNKNOWN.
  Last-write-wins by timestamp: which clock is authoritative?
  Application semantics: is x a counter? a flag? a price?
  No automatic merge possible without domain knowledge.
```

**STONITH prevention:**

```
With STONITH (Shoot The Other Node In The Head):
  S wants to promote. Before accepting any writes:
    1. S sends STONITH command to P's IPMI/iDRAC:
       IPMI: power-off P
    2. P is hard-powered off. Cannot accept writes.
    3. S is now provably the only writer.
    4. S promotes and accepts writes safely.

  Risk: STONITH itself can fail.
    If STONITH command doesn't reach P's power controller:
    S doesn't know if P is dead. Safe choice: S stays secondary.
    (Defensive: prefer split-service over split-brain)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Raft: partition with quorum prevention):**

```
5-node Raft: N1(leader), N2, N3, N4, N5 (Q=3)

Network partition: {N1,N2} | {N3,N4,N5}

{N1,N2}:                    {N3,N4,N5}:
  N1 sends heartbeats         No heartbeat from N1
  N2 responds                 Election triggered
  N1 waits for N3,N4,N5 ACK  N3 becomes candidate
  → can't get Q=3 from 2!    N3 gets votes: N3,N4,N5 (3=Q)
  → N1 STOPS ACCEPTING WRITES N3 becomes leader ✓
                              N3 accepts writes safely

  ← YOU ARE HERE: single writer {N3}; {N1,N2} paused
  No split brain: mathematical impossibility (2+3>5)

Partition heals:
  N1,N2 discover N3 has higher term
  N1 steps down, follows N3
  N1,N2 replay N3's log → catch up
  Cluster healthy again
```

**FAILURE PATH (heartbeat-only, no quorum):**
Same partition. P=N1 sees no heartbeat from N3,N4,N5 — continues. S=N3 sees no heartbeat from N1 — promotes. Both active. Writes diverge. This is the split-brain failure path.

**WHAT CHANGES AT SCALE:**
At large scale: network partitions are more frequent (more links, more switches). Split-brain without quorum becomes a WHEN, not an IF. In a 100-node cluster without quorum: any network blip risks partitioning into two groups that both exceed "50%" of their local view. Multi-datacenter: a DC-level partition creates two large groups. Without DC-aware quorum placement: both DCs may form local majorities within their own DC, causing a datacenter-level split brain (a "geo-split").

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multi-leader replication (CRDTs, geo-distributed systems) intentionally allows concurrent writes to different "primaries" with conflict resolution. This is NOT split brain — it's a deliberate design with defined merge semantics (CRDT merge functions, vector clocks, LWW with explicit policy). Split brain is accidental multi-leadership with undefined merge semantics. The difference is: intentional multi-leader systems design the conflict resolution BEFORE the system exists; split brain creates conflicts that the system was NEVER designed to resolve.

---

### 💻 Code Example

**BAD - Timeout-based promotion (split-brain vulnerable):**

```bash
# keepalived.conf: VRRP-based failover
# BAD: no quorum, timeout-only promotion
vrrp_script chk_mysql {
  script "/usr/bin/mysqladmin ping"
  interval 2   # check every 2 seconds
  fall 3        # 3 failures = VRRP failover
}

vrrp_instance VI_1 {
  state MASTER
  interface eth0
  virtual_router_id 51
  priority 100
  virtual_ipaddress {
    192.168.1.100
  }
  track_script {
    chk_mysql
  }
  # BAD: if network between MASTER and BACKUP drops,
  # but both MySQL instances are healthy:
  # BACKUP sees MASTER "fail" → promotes
  # MASTER continues (network to BACKUP only is down)
  # Both hold VIP via ARP conflict
  # Both accept writes → split brain
}
```

**GOOD - Patroni + etcd: quorum-enforced HA for PostgreSQL:**

```yaml
# patroni.yml: uses etcd as distributed configuration store
# GOOD: quorum-based, split-brain safe
scope: postgres-cluster
name: pg-node-1

etcd3:
  hosts: etcd1:2379,etcd2:2379,etcd3:2379
  # etcd = Raft-based quorum store
  # Leader election: only one node holds the etcd lock
  # Lock = key in etcd with TTL (lease)
  # If primary can't renew its etcd lease (partitioned):
  # lock expires → another node acquires it → promoted
  # If primary IS partitioned from etcd: it CANNOT renew
  # → it loses the lock → it steps down
  # → it refuses writes (PostgreSQL pg_ctl promote reversed)
  # Result: minority partition always loses authority

bootstrap:
  dcs:
    ttl: 30 # lease TTL seconds
    loop_wait: 10 # heartbeat interval
    retry_timeout: 10 # etcd operation timeout
    maximum_lag_on_failover: 1048576 # 1MB max lag for failover

postgresql:
  listen: 0.0.0.0:5432
  connect_address: pg-node-1:5432
  # Patroni checks etcd quorum before accepting any write
  # If etcd quorum lost: Patroni puts PostgreSQL in read-only
  # This is the "no quorum = no writes" enforcement
```

**Verifying split-brain prevention in production:**

```bash
# 1. Simulate network partition in staging:
#    Drop packets between primary and secondary:
iptables -A INPUT -s <secondary-ip> -j DROP
iptables -A OUTPUT -d <secondary-ip> -j DROP

# 2. Wait for timeout period. Check:
#    - Does secondary promote? (expected: yes with quorum)
#    - Does original primary step down? (expected: yes with Patroni)
#    - Are there 2 masters? (expected: NO — only 1 allowed)
patronictl -c patroni.yml list

# 3. Verify original primary stopped accepting writes:
psql -h <original-primary-ip> -c "SELECT pg_is_in_recovery();"
# Expected: t (in recovery = read-only follower, not primary)

# 4. Remove iptables rules (heal partition):
iptables -D INPUT -s <secondary-ip> -j DROP
iptables -D OUTPUT -d <secondary-ip> -j DROP

# 5. Verify cluster healed with single primary:
patronictl -c patroni.yml list
# Expected: 1 Leader, N-1 Replicas, all synced
```

---

### ⚖️ Comparison Table

| Prevention mechanism    | Safety guarantee                | Availability on partition        | Operational complexity | Recovery on failure          |
| :---------------------- | :------------------------------ | :------------------------------- | :--------------------- | :--------------------------- |
| Quorum (Raft/Paxos)     | Mathematical (N/2+1)            | Minority partition stops         | Low (built-in)         | Automatic                    |
| STONITH                 | Physical (one node powered off) | Both stop until STONITH succeeds | High (hardware)        | Manual                       |
| Fencing tokens          | Storage-layer enforcement       | Old primary's writes rejected    | Medium                 | Automatic                    |
| Lease-based (etcd DCS)  | Lease expiry + quorum renewal   | Minority can't renew lease       | Low-medium             | Automatic                    |
| None (timeout failover) | None — split brain possible     | Both sides may proceed           | Low                    | Manual (data reconciliation) |

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                  |
| :-------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Split brain only happens with misconfigured systems"           | Split brain happens whenever a system allows promotion without quorum or fencing. Many widely-deployed HA configurations (VIP-based failover without quorum device, MySQL master-master without wsrep) are split-brain vulnerable BY DESIGN. It is a common production failure.                                          |
| "A watchdog/heartbeat prevents split brain"                     | A heartbeat detects failure. It does NOT prevent split brain. If both nodes check a heartbeat and both decide the other is failed: both promote. The heartbeat is the trigger for split brain, not the prevention.                                                                                                       |
| "STONITH is a legacy solution"                                  | STONITH is still widely used in bare-metal HA clusters (Pacemaker on Linux HA). In cloud environments, similar functionality is provided by cloud APIs (terminate EC2 instance, stop Azure VM). The concept is modern; the tooling has evolved.                                                                          |
| "Redis Sentinel prevents split brain"                           | Redis Sentinel has a quorum parameter but it only governs when to TRIGGER a failover, not whether the old master stops accepting writes. The old Redis master can still accept writes after Sentinel promotes a new master. Redis Cluster (not Sentinel) is more split-brain resistant via cluster topology enforcement. |
| "Network partitions are rare — split brain risk is theoretical" | Netflix's Chaos Engineering, the Jepsen project, and database incident post-mortems show network partitions are routine. In a cluster of N nodes running for Y years: partition probability approaches 1 as N and Y increase. Split brain is not theoretical — it's a design requirement.                                |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Dual-Leader MySQL Cluster (Production Data Corruption)**

**Symptom:** After a network blip: replication monitoring shows two nodes claiming to be primary. Application writes succeed to both. Reads return inconsistent data. Eventually, replication broker reports "HA_ERR_FOUND_DUPP_KEY" — duplicate primary key conflict on reconnection.
**Root Cause:** MySQL master-master with VIP-based failover and no wsrep quorum. Both nodes declared each other dead during network interruption. Both accepted writes. Same rows written with different values.
**Diagnostic:**

```bash
# Check binary log positions on both nodes:
# On node1:
mysql -e "SHOW MASTER STATUS\G"
# On node2:
mysql -e "SHOW MASTER STATUS\G"
# If both show "Binlog_Do_DB" and have recent activity:
# Both accepted writes → split brain occurred

# Check for conflicting transactions:
mysqlbinlog /var/lib/mysql/mysql-bin.* | \
  grep -A5 "BEGIN" | head -50
# Look for overlapping timestamps on both nodes
# indicating concurrent write acceptance
```

**Fix:**
BAD: Attempting to reconcile conflicting data row by row.
GOOD: (1) Restore from backup taken BEFORE partition. (2) Migrate to Galera/XtraDB Cluster with wsrep quorum (won't write without majority). (3) Or migrate to Patroni + etcd (Raft-based quorum DCS). Data reconciliation after split brain is a business logic problem, not a database problem.
**Prevention:** Never run MySQL master-master without Galera wsrep quorum. Use `wsrep_cluster_size` monitoring to alert when cluster shrinks.

**Failure Mode 2: etcd Single-Node Split Brain During Leader Election**

**Symptom:** etcd 3-node cluster. One node is briefly unable to reach the other two. Kubernetes API server connects to that isolated node. Kubernetes reports stale data (Pods still "running" that were deleted 30 seconds ago).
**Root Cause:** The isolated etcd node is a FOLLOWER with stale reads. It's NOT a split-brain in the traditional sense (etcd uses Raft — true split brain is mathematically prevented). BUT: if Kubernetes API is connected to a follower WITHOUT linearizable reads: the follower serves stale data, appearing as split-brain behavior.
**Diagnostic:**

```bash
# Check if etcd API server connection is to leader:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=table | grep "IS LEADER"
# If the endpoint that Kubernetes API uses is not the leader:
# Check if Kubernetes is configured with all etcd endpoints:
grep -i "etcd-servers" /etc/kubernetes/manifests/kube-apiserver.yaml
# Should include ALL etcd member URLs, not just one

# Verify Kubernetes uses linearizable reads (etcd3):
# kube-apiserver uses --etcd-servers and reads with Linearizable
# by default — this should not be an issue in standard deployments
```

**Fix:**
BAD: Pointing Kubernetes API server to a single etcd node.
GOOD: Configure `--etcd-servers` with all etcd endpoints. kube-apiserver load balances and routes writes to the current leader automatically.
**Prevention:** Include all etcd endpoints in kube-apiserver configuration. Monitor `etcd_server_is_leader` Prometheus metric across all nodes.

**Failure Mode 3: Security - STONITH Failure Enables Split Brain Data Exfiltration**

**Symptom:** During a network partition event, STONITH fails to kill the old primary. The old primary continues accepting writes and serving reads for 3 minutes. An attacker with pre-existing write access uses this window to write malicious data to the old primary — data that will never be replicated to the new primary (or will be overwritten during reconciliation).
**Root Cause:** STONITH relied on an IPMI connection that was also affected by the network partition. Both the heartbeat link AND the IPMI management network link were on the same physical switch — single point of failure. STONITH command sent by secondary could not reach the primary's BMC.
**Diagnostic:**

```bash
# Verify STONITH device connectivity is independent of data network:
# Check if IPMI/BMC uses a separate management network:
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> \
  chassis power status
# If this fails during production network issues: STONITH will fail too

# Check Pacemaker STONITH logs:
journalctl -u pacemaker | grep -i "stonith" | tail -30
# Look for "Failed to fence" or "Unable to contact" messages
```

**Fix:**
BAD: STONITH management network on the same physical switch as the database replication network.
GOOD: (1) Separate physical management network for IPMI/iDRAC. (2) Or use cloud power APIs (EC2 terminate instance) which don't share the data network. (3) Configure Pacemaker with `stonith-timeout` and `stonith-max-attempts` appropriate for your BMC hardware.
**Prevention:** Test STONITH monthly by simulating partition and verifying the correct node is powered off within the expected timeout. Never deploy HA without working STONITH in a non-quorum architecture.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-028 - Quorum (the mathematical prevention mechanism for split brain)
- DST-022 - Leader Election (the distributed election process that split brain corrupts)
- DST-006 - CAP Theorem (split brain is the partition scenario in CAP — you must choose C or A)

**Builds On This (learn these next):**

- DST-030 - Fencing / Epoch (the storage-level enforcement mechanism that completes split-brain prevention after quorum failure)

**Alternatives / Comparisons:**

- DST-028 - Quorum (mathematical prevention vs. STONITH physical prevention)
- DST-030 - Fencing / Epoch (fencing token as the operational complement to quorum)
- DST-006 - CAP Theorem (formal framework for the availability-consistency trade-off split brain forces)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Two nodes simultaneously claim |
|                  | primary role → data corruption |
+------------------+--------------------------------+
| PROBLEM SOLVED   | (It IS the problem — all HA    |
|                  | systems exist to prevent this) |
+------------------+--------------------------------+
| KEY INSIGHT      | You can't detect "other node   |
|                  | is dead" vs "network is down"  |
+------------------+--------------------------------+
| USE WHEN         | N/A — this is the antipattern  |
|                  | to prevent, not to use         |
+------------------+--------------------------------+
| AVOID WHEN       | Always avoid: quorum or STONITH|
|                  | required in any HA setup       |
+------------------+--------------------------------+
| TRADE-OFF        | Prevention = stop minority from|
|                  | writing (availability loss)    |
+------------------+--------------------------------+
| ONE-LINER        | Partition + dual promotion     |
|                  | = divergent writes = corruption|
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-028 Quorum,                |
|                  | DST-030 Fencing/Epoch          |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Split brain = two nodes both think they're primary = two divergent databases = data that can't be reconciled without business knowledge of each conflicting write.
2. Prevention requires quorum (mathematical), STONITH (physical), or fencing tokens (storage-layer) — heartbeat/timeout alone is never sufficient.
3. After split brain occurs: you have a data integrity incident. The only safe recovery is restore from backup taken before the partition, not automated merge.

**Interview one-liner:**
"Split brain occurs when a network partition causes two nodes to simultaneously believe they are the authoritative primary, resulting in divergent writes. It's prevented by quorum (mathematical impossibility of two majorities from N nodes), STONITH (physically killing the old primary before the new one accepts writes), or fencing tokens (storage rejects writes from any node not holding the current epoch token). Timeout-based failover without quorum is the most common cause of split brain in production."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
In any system where multiple actors can independently claim authority, and where the actors cannot reliably communicate: you must have a mathematical or physical enforcement mechanism that makes it IMPOSSIBLE for two actors to simultaneously exercise authority — not just unlikely. "Unlikely" is not an engineering guarantee; mathematical impossibility is. This applies to distributed databases (quorum), distributed locks (fencing tokens), and any leader election protocol.

**Where else this pattern appears:**

- **DNS and BGP hijacking (network split brain):** When a BGP router and its peer lose connectivity, both may advertise the same IP prefix — two routers claiming authority over the same network. Traffic destabilizes. This is split brain at the network routing layer: the same "two authorities claim the same resource" problem. BGP's solution (hold-down timers, route dampening, RPKI) is analogous to fencing tokens: before accepting a new route advertisement, verify the advertising AS has authority.
- **Distributed lock managers (etcd/Chubby distributed locks):** When a process holds a lock and its network connection to the lock server breaks: does it still hold the lock? From the lock server's view: the lease expired → lock released → another process acquired it. From the process's view: it's still the lock holder. This is split brain at the application level. Fencing tokens solve it: the lock server issues a monotonically increasing token on each lock grant. The protected resource rejects writes with token < max_seen. The "stale lock holder" is fenced out automatically.
- **Version control merge conflicts (conceptual split brain):** When two developers simultaneously edit the same file on different branches: they've created a "split brain" of the file state. The merge conflict IS a split-brain event in version control. Git's resolution strategy: present both versions and require human merge (because only the developer knows the correct business intent). Distributed databases can't do this — there's no human to interpret the semantics of conflicting database row values. This is why preventing split brain (not recovering from it) is the only viable distributed systems strategy.

---

### 💡 The Surprising Truth

The most famous real-world split-brain incident didn't happen in a database cluster — it happened on the internet in 2010. On April 8, 2010, China Telecom incorrectly advertised 37,000 BGP routes from other ASes, including routes for major US government, military, and commercial networks. For 18 minutes, internet traffic destined for US networks was routed through China Telecom's infrastructure. Two routers were simultaneously claiming authority over the same IP prefixes — a global BGP split brain. This isn't a theoretical distributed systems problem: it's a live demonstration that "split brain" — two authoritative claims over the same resource — is a systems-level vulnerability that can affect infrastructure at internet scale, not just databases. The surprising truth: the same split-brain antipattern that causes MySQL data corruption also caused US military traffic to route through China for 18 minutes in 2010 — because BGP, like an improperly configured database cluster, has no quorum enforcement.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** Redis Sentinel is widely deployed for Redis HA. The Sentinel documentation states: "Sentinel quorum parameter: the number of Sentinel processes that need to agree that a master is down before triggering failover." If this quorum is satisfied and a new master is promoted: does the OLD master automatically stop accepting writes? Under what specific condition can the old master still accept writes after Sentinel promotes a new master — and what type of data does this affect?
_Hint:_ Sentinel quorum governs WHEN to promote — not whether the old master stops. The old master has no mechanism to "un-master" itself. After promotion: clients are reconfigured by Sentinel to point to the new master. But clients already connected to the old master continue writing until they reconnect. What does this mean for long-lived connections (connection pools with keep-alive)? And for data that was written to the old master between "old master last ACK to Sentinel" and "new master accepts first write"?

**Q2 (C - Design Trade-off):** Some distributed systems use "optimistic split-brain" recovery: instead of preventing split brain with quorum (which requires stopping minority writes), they allow both partitions to proceed with writes and use CRDT (Conflict-free Replicated Data Types) or LWW (Last Write Wins) for conflict resolution on reconnection. Amazon Dynamo uses this approach. Under what conditions is this design CORRECT, and under what conditions does it produce incorrect results? What types of data are safe for LWW/CRDT and what types are not?
_Hint:_ CRDTs are correct for data types where concurrent modifications can be merged mathematically: counters (G-Counter, PN-Counter), sets (G-Set, OR-Set), registers (LWW-Register with correct semantics). LWW is correct when the latest wall-clock timestamp is meaningful (last edit of a user profile field). Where LWW/CRDT CANNOT be correct: financial balances (concurrent debits may produce a negative balance after merge), inventory counts (concurrent decrements may double-sell), primary key uniqueness constraints (both partitions insert row with same PK).

**Q3 (A - System Interaction):** Kubernetes uses etcd as its state store. etcd uses Raft, which mathematically prevents split brain. Yet Kubernetes documentation warns about "stale reads" from etcd in certain configurations. If Raft prevents split brain, why can Kubernetes components still read stale data? What is the relationship between "split brain prevention" and "read staleness" in a Raft cluster, and what is the specific Kubernetes configuration that determines whether reads are linearizable or potentially stale?
_Hint:_ Raft prevents two primaries (split brain at write level). But Raft followers can serve reads without consulting the leader — and followers may lag behind the leader's commitIndex. If kube-apiserver reads from an etcd follower (stale read), it may see a resource version that doesn't reflect the latest committed state. The KEY API resource version (ResourceVersion) is Raft's commitIndex made visible to Kubernetes. Check: does kube-apiserver's `--etcd-servers` include all endpoints? Does it use `etcd3` (linearizable reads via ReadIndex) or `etcd2` (potentially stale)?

