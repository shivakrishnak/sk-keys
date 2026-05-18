---
id: DPT-088
title: Leader Election Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-065
used_by: []
related: DPT-065, DPT-085, DPT-089, DPT-048
tags:
  - pattern
  - distributed
  - advanced
  - consensus
  - coordination
  - single-writer
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 88
permalink: /technical-mastery/design-patterns/leader-election-pattern/
---

⚡ TL;DR - Leader Election ensures exactly one instance
in a cluster performs a task at any time. Without it:
multiple instances may execute the same scheduled job
(duplicate sends, double charges). The leader holds
a distributed lock with a TTL; followers periodically
attempt to acquire the lock. If the leader fails: the
TTL expires and a follower wins the next election.

| #88 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-065 | |
| **Used by:** | N/A | |
| **Related:** | DPT-065, DPT-085, DPT-089, DPT-048 | |

---

### 🔥 The Problem This Solves

**THE DUPLICATE SCHEDULER PROBLEM:**
An e-commerce application runs 5 instances for high
availability. Each instance has a scheduled job that
runs every day at 9 AM: send promotional emails to
all active customers.

Without leader election: all 5 instances run the job.
All 1 million active customers receive 5 promotional
emails. Spam complaints. Unsubscribes. Brand damage.
The same bug applies to: sending invoices, running
billing cycles, purging old data, generating reports.

**THE LEADER ELECTION SOLUTION:**
One instance is elected leader. Only the leader runs
the scheduled job. If the leader fails: the election
runs again; a new leader is elected. Always exactly
one instance performs the singleton task.

---

### 📘 Textbook Definition

**Leader Election** is a distributed systems pattern
where one node in a cluster is designated as the "leader"
and given exclusive authority to perform certain tasks.
Other nodes are "followers."

> "Leader Election is the process of designating a
> single process as the organizer of some task distributed
> among several computers. Before the task is begun,
> all network nodes are unaware of which node will
> serve as the 'leader.' After a leader election
> algorithm has been run, however, each node throughout
> the network recognizes a particular, unique node
> as the task leader." (Wikipedia)

**Implementation approaches:**

1. **Distributed lock with TTL:**
   Leader acquires a lock in a coordination service
   (ZooKeeper, etcd, Redis) with a TTL. Leader renews
   the lock before TTL expiration. Failure: TTL expires,
   lock released, follower acquires lock (new leader).

2. **Consensus protocol:**
   Raft (used by etcd), Paxos - formal consensus algorithms
   that elect a leader through voting. Handles split-brain
   natively.

3. **External coordinator:**
   Kubernetes: only one pod runs a CronJob.
   Kubernetes Lease API: used by Kubernetes controllers
   themselves for leader election.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One instance holds a distributed lock; it is the leader.
Others wait. If the leader crashes: the lock expires;
a new leader is elected.

**One analogy:**
> A parking spot with a meter.
>
> First car to arrive: pays the meter (acquires the lock).
> That car occupies the spot (is the leader).
> Other cars: park elsewhere (are followers).
> The meter expires: the spot opens up.
> First car to reach it next: pays the meter (new leader).
>
> The meter TTL = the lock TTL.
> Paying the meter = renewing the lock.
> Car that drives away without paying: spot opens immediately (failure).
> No two cars in the same spot = no split-brain.

---

### 🔩 First Principles Explanation

**THE DISTRIBUTED LOCK WITH TTL:**
```
1. Instance X atomically acquires lock: SET key=leader NX
  EX 30
   (SET if Not eXists, EXpiry 30 seconds).
2. If SET succeeds: X is the leader. X runs the task.
3. X renews the lock every 15 seconds (half TTL): SET
  key=leader XX EX 30
   (SET if eXists = renewal, not new acquisition).
4. If X crashes: no renewal. At T+30s: lock expires.
5. Next instance to attempt SET key=leader NX EX 30: new
  leader.
```

**THE SPLIT-BRAIN PROBLEM:**
The worst failure mode: two instances BOTH believe they
are the leader simultaneously.
How it happens:
- Leader's GC pause or network partition causes it to
  miss the renewal window.
- Lock appears expired; a second instance acquires it.
- The original leader's pause ends; it resumes as leader.
- Two leaders simultaneously write to the same resource.

**PREVENTING SPLIT-BRAIN:**

1. **Fencing tokens**: each lock acquisition gets an
   incrementing token. The resource server rejects
   writes with a token lower than the last seen token.
   Stale leader's writes: rejected.

2. **Quorum-based locking**: Redlock algorithm
   acquires the lock on N/2+1 Redis nodes simultaneously.
   Single Redis node failure does not create split-brain.
   Controversial: Martin Kleppmann argues Redlock has
   fundamental safety issues under certain failure modes.

3. **Short TTL + fast renewal**: makes the window for
   false split-brain very small but does not eliminate it.

**THE "I AM THE LEADER" ASSUMPTION PROBLEM:**
A leader must never ASSUME it is still the leader. It must
VERIFY at the point of doing the work. Check-then-act:
```java
if (isLeader()) {  // check
    doSensitiveWork();  // act: may NOT still be leader!
}
```
Between `isLeader()` and `doSensitiveWork()`: GC pause,
thread preemption, network delay. Another instance may
have acquired leadership. Solution: fencing token validation
at the resource level (not just the lock level).

---

### 🧪 Thought Experiment

**THE FENCING TOKEN MECHANISM:**
```
Time 0: Instance A acquires lock, token = 42. A is leader.
Time 5: A attempts renewal. GC pause (3 seconds).
Time 8: Lock expires. B acquires lock, token = 43. B is
  leader.
Time 9: A's GC ends. A still believes it's leader. A
  writes to DB with token 42.
DB: sees token 42 < 43 (last seen). REJECTS A's write.
Time 10: B writes to DB with token 43. ACCEPTED.
```
Fencing token at the database level prevents stale leaders
from corrupting data, even if the lock layer fails.
This is "fencing" - cutting off the stale leader's
write access.

---

### 🧠 Mental Model / Analogy

> Leader Election = a "talking stick" in a distributed meeting.
>
> The talking stick: one stick, passed between participants.
> Only the holder may speak. If the holder is silent
> for too long (TTL): the facilitator takes the stick back.
> Next person to raise their hand: gets the stick.
>
> In distributed systems: the "stick" is a lock in Redis/ZooKeeper.
> The "holder" is the leader instance.
> "Speaking" = performing the singleton task.
> "Silent too long" = missing the renewal (process crashed).
> "Facilitator" = Redis/ZooKeeper/etcd (the coordination service).
>
> Only one holder at a time. Automatic recovery on failure.
> The holder must keep actively renewing ("speaking") or
> the stick goes to the next instance.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Basic leader election with Redis:**
Use `SET lock_key leader_id NX EX 30` for atomic acquisition.
Leader renews every 15 seconds. On failure: 30s gap before
new leader elected. Acceptable for non-critical jobs
with low consistency requirements.

**Level 2 - ShedLock for Spring scheduled tasks:**
ShedLock is a library specifically for Java scheduled
tasks that uses a database table for leader election.
The `@SchedulerLock` annotation prevents concurrent
execution across multiple instances. Transactional:
uses the application's existing database. No additional
infrastructure required.

**Level 3 - Raft and etcd:**
Kubernetes itself uses etcd for leader election in
its control plane components (controller manager,
scheduler). Raft consensus (the algorithm etcd uses)
ensures leader election even under network partitions.
Kubernetes provides a `Lease` resource that applications
can use for leader election with Raft guarantees,
without running their own etcd. The
`controller-runtime` leader election mechanism uses
Kubernetes Leases for distributed controller leader
election.

---

### ⚙️ How It Works (Mechanism)

```
Leader Election with TTL-based Lock
┌─────────────────────────────────────────────────────────┐
│  Instance A          Redis             Instance B       │
│      │                 │                   │            │
│  SET leader NX EX 30   │                   │            │
│  ────────────────────► │                   │            │
│       ◄─ OK (got lock) │                   │            │
│  [LEADER: A]           │                   │            │
│  Do work...            │                   │            │
│  SET leader XX EX 30   │                   │
  │ (renewal)
│  ────────────────────► │                   │            │
│       ◄─ OK (renewed)  │                   │            │
│  CRASH! (A dies)       │                   │            │
│                        │                   │            │
│                      (TTL expires after 30s)            │
│                        │  SET leader NX EX 30           │
│                        │ ◄──────────────────            │
│                        │  OK ──────────────►            │
│                        │            [LEADER: B]         │
│                        │            Do work...          │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - ShedLock for Spring Boot scheduled jobs:**

```xml
<!-- pom.xml dependencies: -->
<dependency>
    <groupId>net.javacrumbs.shedlock</groupId>
    <artifactId>shedlock-spring</artifactId>
    <version>5.10.0</version>
</dependency>
<dependency>
    <groupId>net.javacrumbs.shedlock</groupId>
    <artifactId>shedlock-provider-jdbc-template</artifactId>
    <version>5.10.0</version>
</dependency>
```

```sql
-- Required table (same DB as application):
CREATE TABLE shedlock (
    name          VARCHAR(64)  NOT NULL,
    lock_until    TIMESTAMP    NOT NULL,
    locked_at     TIMESTAMP    NOT NULL,
    locked_by     VARCHAR(255) NOT NULL,
    PRIMARY KEY (name)
);
```

```java
@Configuration
@EnableSchedulerLock(defaultLockAtMostFor = "10m")
public class SchedulerConfig {

    @Bean
    public LockProvider lockProvider(DataSource dataSource) {
        // Uses application's existing database. No Redis needed.
        return new JdbcTemplateLockProvider(
            JdbcTemplateLockProvider.Configuration.builder()
                .withJdbcTemplate(new JdbcTemplate(dataSource))
                .usingDbTime()  // use DB time, not node time
                .build()
        );
    }
}
```

```java
@Service
class PromoEmailScheduler {

    private final EmailService emailService;
    private final CustomerRepository customerRepo;

    @Scheduled(cron = "0 0 9 * * *")  // 9 AM daily
    @SchedulerLock(
        name = "promo-email-job",
        lockAtLeastFor = "5m",
        // hold lock even if job finishes fast
        lockAtMostFor = "2h"      // release if job hangs > 2 hours
    )
    public void sendDailyPromos() {
        // This method runs on EXACTLY ONE instance.
        // ShedLock prevents concurrent execution across instances.
        log.info("Promo email job starting on this node");
        List<Customer> customers = customerRepo.findActiveCustomers();
        customers.forEach(c -> emailService.sendPromo(c));
        log.info("Promo email job complete. Processed: {}",
            customers.size());
    }
}
// Result: 5 instances running. Only 1 runs sendDailyPromos().
// No duplicate emails. Automatic failover if leader crashes.
```

**Example 2 - Redis-based leader election (lower-level):**

```java
@Component
class RedisLeaderElection {

    private final StringRedisTemplate redis;
    private final String instanceId;
    private volatile boolean isLeader = false;

    // Acquire/renew every 15s. TTL = 30s.
    @Scheduled(fixedDelay = 15_000)
    public void elect() {
        String acquired = redis.opsForValue()
            .setIfAbsent("leader-lock",
                instanceId,
                Duration.ofSeconds(30)); // NX EX 30

        if (acquired != null) {
            // New acquisition: this instance just became leader.
            isLeader = true;
        } else {
            // Lock exists. Check if WE hold it.
            String currentHolder =
                redis.opsForValue().get("leader-lock");
            if (instanceId.equals(currentHolder)) {
                // Renewal:
                redis.expire("leader-lock", Duration.ofSeconds(30));
                isLeader = true;
            } else {
                // Another instance is leader.
                isLeader = false;
            }
        }
    }

    public boolean isLeader() { return isLeader; }
}
// Caveat: naive implementation. Use ShedLock or
// Kubernetes Lease for production-grade leader election.
```

---

### 🔥 Failure Scenarios

**THE GC PAUSE SPLIT-BRAIN:**
```
T=0: Instance A holds lock (token=5). A is leader.
T=15: A attempts renewal. Full GC: pauses A for 35 seconds.
T=30: Lock TTL expires. B acquires lock (token=6). B is
  leader.
T=50: A's GC ends. A still thinks it's leader. A writes to
  shared resource.
T=50: A's write carries token=5. Resource sees 5 < 6 (last
  seen). REJECTS.
T=51: B writes with token=6. ACCEPTED.
```
**Without fencing tokens**: A's stale write SUCCEEDS at T=50.
**With fencing tokens at resource level**: A's write rejected. Safe.

**REDIS FAILURE DURING ELECTION:**
```
Redis: single-node. Fails at T=0. TTL not enforced.
A: cannot renew (Redis unreachable). Believes it lost
  leadership.
B: cannot acquire (Redis unreachable). No leader elected.
C: cannot acquire. No leader.
All scheduled jobs: stop running. Outage until Redis
  recovers.
```
Mitigation: Redis Sentinel / Cluster for HA.
Or: use database-backed ShedLock (your database is already HA).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Leader election guarantees exactly-once execution | Leader election significantly reduces duplicate execution but cannot guarantee exactly-once under all failure scenarios (GC pauses, network partitions). Idempotent operations (DPT-085) + fencing tokens provide the additional safety layer |
| Short TTL prevents all split-brain issues | Short TTL reduces the split-brain window but does not eliminate it. A GC pause of TTL+1 duration causes split-brain. Fencing tokens at the resource level are the correct defense |
| Only single-instance deployments need leader election | Cloud-native deployments almost always run multiple instances for HA. Any scheduled job, background worker, or single-writer requirement in a multi-instance deployment needs leader election |
| Kubernetes ensures only one pod runs a CronJob | Kubernetes CronJob may create a new job before the previous one completes (depending on `concurrencyPolicy`). Use `concurrencyPolicy: Forbid` and `successfulJobsHistoryLimit`. Even then: if a pod is slow to be replaced, duplicates can occur. Application-level idempotency is still needed |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ One instance is leader. Only leader     │
│              │ performs singleton tasks.               │
├──────────────┼──────────────────────────────────────────┤
│ MECHANISM    │ Distributed lock with TTL. Leader renews│
│              │ before TTL. Crash → TTL expires → elect │
├──────────────┼──────────────────────────────────────────┤
│ SPLIT-BRAIN  │ Two leaders simultaneously. Prevention: │
│              │ fencing tokens at the resource level.   │
├──────────────┼──────────────────────────────────────────┤
│ JAVA LIB     │ ShedLock: @SchedulerLock + DB table.    │
│              │ No extra infra. Production-grade.       │
├──────────────┼──────────────────────────────────────────┤
│ K8S NATIVE   │ Lease resource. Used by K8s controllers.│
│              │ controller-runtime for Go apps.         │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-089: Graceful Degradation Pattern   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Leader Election = distributed lock with TTL. Leader
   acquires lock, renews before expiry, performs singleton task.
   Crash: TTL expires, follower acquires = new leader.
   Always-exactly-one executor across instances.
2. Split-brain risk: GC pauses or network delays can
   cause two instances to believe they are both leader.
   Fencing tokens at the resource level (not just the
   lock level) prevent stale leaders from corrupting data.
3. ShedLock for Spring: `@SchedulerLock` annotation +
   a `shedlock` database table. Uses your existing DB.
   No Redis needed. Prevents duplicate job execution
   across instances with minimal setup.

