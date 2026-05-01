---
layout: default
title: "Split Brain"
parent: "Distributed Systems"
nav_order: 592
permalink: /distributed-systems/split-brain/
number: "592"
category: Distributed Systems
difficulty: ★★★
depends_on: "Quorum, Leader Election"
used_by: "MySQL HA, Kubernetes etcd, DRBD clusters"
tags: #advanced, #distributed, #availability, #consistency, #failure-mode
---

# 592 — Split Brain

`#advanced` `#distributed` `#availability` `#consistency` `#failure-mode`

⚡ TL;DR — **Split Brain** is the catastrophic failure where a network partition causes two cluster partitions to each believe they are the authoritative primary — resulting in divergent writes, data corruption, and the distributed systems equivalent of two operating tables on the same patient simultaneously.

| #592            | Category: Distributed Systems            | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Quorum, Leader Election                  |                 |
| **Used by:**    | MySQL HA, Kubernetes etcd, DRBD clusters |                 |

---

### 📘 Textbook Definition

**Split Brain** is a failure scenario in replicated distributed systems where a network partition divides the cluster into two (or more) isolated subsets, and each subset independently elects a new leader or continues operating as primary — resulting in two simultaneous "primary" nodes accepting conflicting writes. Unlike a simple node failure (one primary continues, others follow), split-brain creates two diverging data streams with no mechanism for automatic reconciliation. Systems vulnerable to split-brain include: active-passive HA clusters (heartbeat loss → secondary promotes to primary while primary continues), multi-master databases without quorum enforcement, and any system where "primary" role is determined per-node without consensus. Prevention mechanisms: **quorum-based consensus** (Raft/Paxos — requires majority to elect leader; minority partition cannot elect → at most one primary possible); **STONITH (Shoot The Other Node In The Head)** — fencing mechanism that physically powers off or isolates suspected primary before promotion; **split-brain resolvers** (network-partition-aware tie-breaking logic). Recovery is complex: if split-brain occurred, divergent writes must be manually reconciled or one partition's writes must be discarded. The CAP theorem frames split-brain as the CP vs AP choice during network partition.

---

### 🟢 Simple Definition (Easy)

Split brain: imagine a 2-node database cluster. Primary and replica are connected. The network cable breaks. Primary thinks: "replica crashed, I'll continue." Replica thinks: "primary crashed, I'll become primary." Now: TWO primaries accepting writes. User A writes to old primary. User B writes to new primary. Different data. The network reconnects. Who's right? Nobody knows. Data is corrupted. Split brain = two generals both giving orders = chaos. Prevention: require that a node can only become primary if it has consensus from a majority of cluster nodes.

---

### 🔵 Simple Definition (Elaborated)

Split brain is the worst failure mode in distributed systems: it doesn't crash your system — it makes it appear to work while silently corrupting data. A partitioned cluster with two primaries will: accept reads and writes on both sides, return different results to different clients, and when the partition heals: have two conflicting versions of the data. Unlike crashes (detectable, recoverable), split-brain may go unnoticed for minutes/hours. The classic 2-node cluster is inherently vulnerable: you cannot distinguish "partner crashed" from "I lost network to partner" without a third tie-breaker (quorum witness, STONITH fence, or external arbitrator).

---

### 🔩 First Principles Explanation

**Split brain scenarios, quorum prevention, and STONITH:**

```
SCENARIO 1: 2-NODE MYSQL ACTIVE-PASSIVE CLUSTER (MHA without quorum)

  T=0: Primary P1 serving writes. Replica R1 replicating async.
  T=10s: Network partition. P1 ↔ R1 heartbeat lost.

  P1's perspective: "R1 crashed. I'll continue as primary. I'm the only node."
  P1: continues accepting writes. Active.

  R1's perspective: "P1 crashed. I should promote to primary for availability."
  R1: MHA detects missing heartbeat (after 30s timeout) → promotes R1 to primary.
  R1: Now accepting writes.

  SPLIT BRAIN STATE:
    T=40s: P1 and R1 are BOTH primary.
    Client A (routed to P1): INSERT INTO orders VALUES (1001, user_a, $100).
    Client B (routed to R1): INSERT INTO orders VALUES (1002, user_b, $200).
    P1: has order 1001. R1: has order 1002. DIVERGED.

  T=120s: Network heals.
  MHA: detects two primaries. Which one is right?
    Option a: Keep R1 (newer primary). Discard P1's writes (order 1001 lost).
    Option b: Keep P1 (original primary). Discard R1's writes (order 1002 lost).
    Option c: Merge — but auto-merge of conflicting INSERT is undefined.

  Outcome: one side's writes are lost. Someone was charged but has no order. Data integrity violated.

  WHY 2 NODES INHERENTLY VULNERABLE:
    P1 sees: {P1 alive, R1 absent}. Majority of {P1, R1}? P1 is 1 of 2. Not majority.
    R1 sees: {R1 alive, P1 absent}. Majority of {P1, R1}? R1 is 1 of 2. Not majority.

    Both have 50% of the cluster. Both believe they can be primary (no quorum requirement).
    With quorum (N=3, Q=2): neither partition can promote without 2 of 3 nodes.

SCENARIO 2: RAFT CLUSTER — SPLIT BRAIN PREVENTED:

  N=5 Raft cluster: N1(leader,term=3), N2, N3, N4, N5.
  Network partition: {N1, N2} and {N3, N4, N5}.

  Partition A {N1, N2}:
    N1: still leader. Sends AppendEntries to N2 only.
    N1 tries to commit new entry: needs 3 of 5 ACKs (majority).
    Gets: N1 (self) + N2 = 2 ACKs. 2 < 3 (quorum).
    N1: CANNOT COMMIT new entries. Blocks writes.

  Partition B {N3, N4, N5}:
    N3, N4, N5: miss heartbeats from N1. Election timer expires.
    N3 becomes candidate: gets votes from N4, N5 = 3 total (self + 2) = majority!
    N3 becomes leader in term=4.

  DUAL PRIMARY?
    N1 in term=3: accepting writes but CANNOT COMMIT (no quorum).
    N3 in term=4: accepting and COMMITTING writes (has quorum 3+).

  Only ONE node (N3) can actually commit. N1's writes are stalled (not committed to client).
  Split-brain? NO — only one committing leader. Clients waiting on N1 get errors/timeouts.

  TERM-BASED FENCING:
    Partition heals. N1 receives AppendEntries from N3 (term=4).
    N1: sees term=4 > term=3. Immediately reverts to FOLLOWER.
    N1 discards any uncommitted entries (those that never got quorum).
    N1: accepts N3 as leader. No conflicting committed writes.

  SAFETY MAINTAINED: no split-brain for committed writes.

SCENARIO 3: KUBERNETES ETCD SPLIT BRAIN:

  3-node etcd cluster: etcd1, etcd2, etcd3.
  etcd1: Kubernetes master. kube-apiserver reads/writes to etcd1.

  Partition: {etcd1} and {etcd2, etcd3}.

  etcd1 (alone):
    Quorum requires 2 of 3. etcd1 has only 1. CANNOT serve writes or reads.
    kube-apiserver: "etcd unavailable" → Kubernetes control plane suspended.

  {etcd2, etcd3}:
    Quorum = 2 of 3. Has 2. CAN elect leader and serve writes.
    New etcd leader elected in {etcd2, etcd3}.
    kube-apiserver (if it can reach etcd2 or etcd3): resumes with correct state.

  Single-node etcd cluster (WRONG — production anti-pattern):
    Only 1 etcd node. No quorum needed (N=1, Q=1).
    Single node failure = etcd down = Kubernetes down.
    No split-brain possible but NO HA.
    Never run etcd in production with less than 3 nodes.

STONITH (SHOOT THE OTHER NODE IN THE HEAD):

  Problem: quorum not available (e.g., 2-node cluster). Need split-brain prevention.
  Solution: STONITH — before a node can become primary, it must PHYSICALLY FENCE the other node.

  Mechanisms:
    1. IPMI/iDRAC power off: send power-off command to suspected primary's BMC (baseboard management controller).
    2. SAN zoning: revoke other node's access to shared storage.
    3. AWS: terminate the EC2 instance via API.
    4. Physical power switch: PDU-controlled power outlet.

  Protocol:
    P1 ↔ R1 heartbeat lost.
    R1: wants to promote to primary.
    R1: FIRST sends STONITH fence command to P1's IPMI interface.
    R1: waits for confirmation (P1 powered off).
    R1: promotes to primary.

    Now: P1 is powered off. Cannot accept writes. No split-brain.

    If STONITH fails (P1's IPMI unreachable):
      R1: REFUSES to promote (cannot confirm P1 is dead).
      R1: stays as replica. System unavailable until situation is resolved.
      This is the correct choice: unavailability > split-brain.

  STONITH failure modes:
    R1 sends STONITH to P1. P1 also sends STONITH to R1 (simultaneously). Both fence each other.
    Both nodes power off. System down. Requires manual intervention.
    (This is called "split-brain with mutual STONITH" — not common but possible.)

  STONITH is used in: Pacemaker/Corosync clusters, DRBD (Distributed Replicated Block Device),
                       VMware HA (uses STONITH-like "isolation response" to power off VMs).

SPLIT BRAIN IN KUBERNETES:

  Scenario: two Kubernetes master nodes (control plane), etcd split.
  Master A: thinks it's the only master.
  Master B: thinks it's the only master.

  Both A and B can schedule pods → same pod scheduled twice → duplicate workloads.
  Both A and B can update services → conflicting kube-proxy rules → network routing broken.

  Prevention: etcd is the single source of truth. Kubernetes masters are stateless —
              they only make decisions based on etcd state.
  If etcd has quorum (3-node): at most one "view" of cluster state.
  Masters reading from etcd: all see the same pods, services, etc.

  BUT: if a master caches state and the etcd connection drops briefly:
    Master A: cached state from 2 minutes ago. Schedules pods based on stale cache.
    Master B: fresh state. Schedules different pods.

  Kubernetes mitigation: kube-apiserver validates writes to etcd before acknowledging.
                          If etcd unreachable: kube-apiserver returns error, client retries.
                          Leader election for kube-controller-manager and kube-scheduler:
                          uses etcd leases → only one instance is active → no dual scheduling.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT split brain awareness:

- 2-node HA clusters: standard setup 10 years ago — all vulnerable to split-brain on any network glitch
- Silent data corruption: system appears healthy while two primaries diverge
- Recovery is manual and destructive: someone must choose which node's data to discard

WITH split brain prevention:
→ Quorum enforces: minority partition cannot elect → at most one primary
→ STONITH fences: physical isolation guarantees old primary stopped before new one starts
→ Explicit unavailability: better for system to stop than silently corrupt data

---

### 🧠 Mental Model / Analogy

> A pair of surgeons performing on the same patient in separate operating rooms due to a hospital communications blackout. Surgeon A thinks Surgeon B was in an accident and continues performing. Surgeon B thinks Surgeon A was in an accident and continues performing. Both make conflicting incisions. When communications restore: discovering two conflicting surgeries happened simultaneously — and neither surgeon knows the full picture. The solution: only one surgeon can operate at a time; before the second surgeon can proceed, they must physically confirm the first has stopped (equivalent to STONITH).

"Two surgeons operating simultaneously" = two primaries accepting writes in split brain
"Hospital communications blackout" = network partition
"Confirming first surgeon has stopped before proceeding" = STONITH fence before promotion
"One operating room at a time (quorum witness)" = majority quorum prevents both from proceeding

---

### ⚙️ How It Works (Mechanism)

**MySQL HA with MHA (Master High Availability) STONITH:**

```bash
# MHA (MySQL Master HA) configuration for split-brain prevention.
# /etc/mha/app1.cnf:
[server default]
manager_log=/var/log/mha/manager.log
manager_workdir=/var/lib/mha/app1

# STONITH script (called before promoting replica to master):
master_ip_failover_script=/etc/mha/master_ip_failover
# This script: 1) VIPs (virtual IPs) from old master, 2) confirms old master unreachable.

[server1]
hostname=db1.example.com
port=3306
ssh_host=db1.example.com

[server2]  # Replica that may be promoted
hostname=db2.example.com
port=3306
ssh_host=db2.example.com

# master_ip_failover script (simplified):
#!/usr/bin/env perl
# Before promoting db2 to master:
# 1. Attempt to SSH to old master (db1) and remove VIP:
#    ssh db1 "ip addr del 10.0.0.100/24 dev eth0"
# 2. If SSH fails (db1 unreachable): ASSUME db1 is dead. Proceed.
#    Note: this is a risk. db1 may still be alive but network-partitioned.
#    For true STONITH: use IPMI to power off db1.

# Safer: IPMI STONITH in Pacemaker:
# /etc/pacemaker/corosync.conf:
quorum {
    provider: corosync_votequorum
    expected_votes: 3   # 3-node cluster
    two_node: 0         # NOT a 2-node cluster (2-node needs special handling)
}

# STONITH resource (power off via IPMI):
# pcs stonith create db1-fence fence_ipmilan \
#   ipaddr="192.168.1.10" login="admin" passwd="secret" pcmk_host_map="db1:192.168.1.10"
# pcs stonith create db2-fence fence_ipmilan \
#   ipaddr="192.168.1.11" login="admin" passwd="secret" pcmk_host_map="db2:192.168.1.11"
# On split-brain detection: Pacemaker fences the other node via IPMI before proceeding.
```

---

### 🔄 How It Connects (Mini-Map)

```
Network Partition (network failure dividing cluster)
        │
        ▼
Split Brain ◄──── (you are here)
(two simultaneous primaries accepting conflicting writes)
        │
        ├── Quorum (prevents split-brain: minority can't elect)
        ├── Fencing and Epoch (mechanism to safely invalidate old primary)
        └── Leader Election (the operation that must be safe against split-brain)
```

---

### 💻 Code Example

**Application-level split-brain detection (etcd lease):**

```java
@Component
public class SingletonLeaderService {

    private final EtcdClient etcdClient;
    private final String leaseKey = "/leaders/singleton-service";
    private volatile boolean isLeader = false;
    private volatile long leaseId = 0;

    /**
     * Try to acquire leadership via etcd lease.
     * etcd lease: key expires if TTL passes without renewal.
     * Only one node can hold the key (CAS: create if absent).
     * Network partition: lease stops being renewed → key expires → other node can acquire.
     */
    @PostConstruct
    public void startLeaderElection() {
        CompletableFuture.runAsync(this::leaderElectionLoop);
    }

    private void leaderElectionLoop() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                if (!isLeader) {
                    tryAcquireLeadership();
                } else {
                    // Renew lease (keep alive):
                    etcdClient.keepAlive(leaseId);
                    Thread.sleep(5000); // Renew every 5 seconds.
                }
            } catch (EtcdException e) {
                if (e.isLeaseExpired() || e.isConnectionFailed()) {
                    // Lost connection to etcd → assume leadership lost.
                    // MUST stop acting as leader to prevent split-brain.
                    log.error("Lost etcd connection. Stepping down as leader.");
                    isLeader = false;
                    stopLeaderTasks(); // CRITICAL: stop before reconnecting.
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    private void tryAcquireLeadership() throws EtcdException {
        // Create lease with TTL=15s (key expires if not renewed within 15s).
        long newLeaseId = etcdClient.createLease(15);

        // Atomic: create key only if it doesn't exist (split-brain prevention).
        boolean acquired = etcdClient.putIfAbsent(leaseKey, getNodeId(), newLeaseId);

        if (acquired) {
            leaseId = newLeaseId;
            isLeader = true;
            log.info("Acquired leadership. Starting leader tasks.");
            startLeaderTasks();
        }
        // If not acquired: another node is leader. Retry after TTL.
    }

    // CRITICAL: never do leader-only work without checking isLeader:
    @Scheduled(fixedDelay = 10000)
    public void doLeaderOnlyWork() {
        if (!isLeader) return; // Safety check on every execution.

        // Do work ONLY if etcd confirms we're still leader:
        try {
            // Re-verify leadership (defense in depth against stale isLeader flag):
            String currentLeader = etcdClient.get(leaseKey);
            if (!getNodeId().equals(currentLeader)) {
                log.warn("Detected leadership changed. Stopping work.");
                isLeader = false;
                return;
            }
            performWork();
        } catch (EtcdException e) {
            log.error("Cannot verify leadership. Skipping work cycle.");
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Split brain only happens during network failures | Split brain can also occur during: (1) extreme CPU load causing heartbeat delays (node appears dead but is just slow), (2) storage latency spikes causing health check timeouts, (3) VM live migration causing brief network interruptions, (4) software bugs causing a node to stop responding to health checks. Any failure that makes a node appear unreachable to its peers without actually stopping it can trigger split-brain if the failover system isn't quorum-based |
| Raft clusters never experience split-brain       | Raft prevents split-brain for COMMITTED writes (quorum required to commit). But a partitioned Raft leader can still serve stale reads (if it's in the minority partition and doesn't know a new leader was elected). The old leader can serve reads that appear correct but don't reflect writes committed to the new leader. For fully linearisable reads: use Raft's ReadIndex protocol (leader confirms majority still recognises it before serving)                        |
| A 3-node cluster always prevents split-brain     | A 3-node quorum-based cluster prevents split-brain IF quorum is enforced. But if a node goes down and the remaining 2-node cluster still serves writes (because min_quorum=1 was configured, or STONITH failed silently), split-brain is still possible. Prevention requires quorum to be strictly enforced — a 2-node partition cannot proceed without verifying the third node cannot commit                                                                                 |
| STONITH always works reliably                    | STONITH depends on external management infrastructure (IPMI, PDU, cloud API). If STONITH itself fails (IPMI firmware bug, network path to BMC also partitioned), the node cannot fence the other node and must refuse to promote — causing extended downtime rather than split-brain. "No news is good news" is NOT safe for STONITH: "couldn't fence the node" must be treated as "fencing failed, do not promote"                                                            |

---

### 🔥 Pitfalls in Production

**2-node MySQL cluster without STONITH causes split-brain:**

```
REAL SCENARIO (reproduced monthly in production environments):

  2-node MySQL cluster: db1 (primary, IP 10.0.0.1), db2 (replica, IP 10.0.0.2).
  Virtual IP: 10.0.0.100 → points to db1.
  MHA Manager: monitors heartbeat between db1 and db2.
  MHA: configured to promote db2 if db1 unreachable for > 30 seconds.

  T=0: db1 primary. db2 replica. VIP on db1.
  T=10: db1's eth0 interface flaps. db1 ↔ db2 heartbeat lost.
         (db1 is ALIVE and still connected to its application server via different NIC)
  T=40: MHA sees db1 unreachable for 30s. Promotes db2 to primary.
         MHA moves VIP 10.0.0.100 to db2.
  T=40+: db1 is still alive. Application server directly connected to db1 still writes to db1.
          db2 is also primary. Application server (via VIP) writes to db2.
  T=300: eth0 heals. db1 and db2 can see each other. Two primaries!

HARM: Orders written to db1 since T=40 vs orders written to db2 since T=40.
  Auto-increment IDs conflict (both db1 and db2 may have issued id=10001).
  Database: cannot reconcile. Manual investigation: check binary logs for conflicts.

BAD: MHA without STONITH (proceeds with promotion without fencing old primary):
  # mha config — NO master_ip_online_change_script with STONITH:
  master_ip_failover_script=/usr/local/bin/failover_no_stonith.sh
  # Script: only moves VIP. Does NOT power off db1.
  # db1 continues operating! Split-brain.

FIX: Add STONITH step to MHA failover script:
  #!/bin/bash
  # master_ip_failover.sh — called by MHA before promoting replica.
  OLD_MASTER_HOST=$1

  # Step 1: Try graceful shutdown of old primary:
  ssh -o ConnectTimeout=5 $OLD_MASTER_HOST "mysqladmin -u root shutdown" 2>/dev/null

  # Step 2: If SSH fails, use IPMI STONITH to power off:
  if [ $? -ne 0 ]; then
      echo "SSH failed. Using IPMI to fence $OLD_MASTER_HOST"
      ipmitool -H ${OLD_MASTER_HOST}-ipmi -U admin -P secret power off
      if [ $? -ne 0 ]; then
          echo "STONITH FAILED. REFUSING TO PROMOTE. Operator must intervene."
          exit 1  # MHA: sees non-zero exit. Aborts promotion. No split-brain.
      fi
      sleep 10  # Wait for node to power off completely.
  fi

  # Step 3: Move VIP only after confirming old primary is fenced:
  # ip addr del 10.0.0.100/24 dev eth0 on old master (already dead)
  ip addr add 10.0.0.100/24 dev eth0  # Add VIP to this new primary.

  echo "Failover complete. New primary is $(hostname)."
  exit 0
```

---

### 🔗 Related Keywords

- `Quorum` — the mathematical foundation that prevents split-brain (minority cannot elect)
- `Fencing and Epoch` — mechanism to invalidate old primary's writes after split-brain
- `Leader Election` — the operation that split-brain corrupts (two leaders elected)
- `STONITH` — physical fencing: force-stopping the old primary before promotion

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Network partition → two primaries →       │
│              │ conflicting writes → data corruption.     │
│              │ Prevention: quorum or STONITH fencing.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing HA clusters; reviewing failover │
│              │ procedures; 2-node clusters especially    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ — (This is a failure mode, not a design  │
│              │ choice. Always prevent it.)              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two surgeons operating simultaneously:  │
│              │  confirm the first has stopped before     │
│              │  the second makes a single incision."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Quorum → Fencing and Epoch → Leader      │
│              │ Election → Raft → STONITH                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes cluster uses a 3-node etcd. The datacenter network switches fail, isolating each etcd node from the others (three-way partition: {etcd1}, {etcd2}, {etcd3}). None can form quorum. The kube-apiserver (connected to etcd1) returns errors for all writes. Kubernetes pods running on worker nodes: do they stop running? What happens to existing pods that were already scheduled and running? What does the kubelet do when it can't reach the kube-apiserver?

**Q2.** You are designing a 2-node MySQL cluster that MUST have high availability (no quorum witness available — single DC with only 2 physical servers). You cannot use STONITH hardware. What architectural alternatives exist to prevent split-brain in this constraint? Consider: read-your-own-writes requirements, acceptable RPO/RTO, and whether asynchronous replication is acceptable.
