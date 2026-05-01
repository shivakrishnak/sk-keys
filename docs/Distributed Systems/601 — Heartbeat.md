---
layout: default
title: "Heartbeat"
parent: "Distributed Systems"
nav_order: 601
permalink: /distributed-systems/heartbeat/
number: "601"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Failure Modes, Gossip Protocol"
used_by: "ZooKeeper, Kubernetes, Kafka, Load Balancers, TCP Keepalive"
tags: #intermediate, #distributed, #failure-detection, #health-check, #availability
---

# 601 — Heartbeat

`#intermediate` `#distributed` `#failure-detection` `#health-check` `#availability`

⚡ TL;DR — **Heartbeat** is a periodic signal sent by a node to prove it's alive; the absence of expected heartbeats within a timeout window triggers failure detection and failover — the simplest mechanism for distributed liveness checking.

| #601            | Category: Distributed Systems                               | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Failure Modes, Gossip Protocol                              |                 |
| **Used by:**    | ZooKeeper, Kubernetes, Kafka, Load Balancers, TCP Keepalive |                 |

---

### 📘 Textbook Definition

**Heartbeat** is a periodic keep-alive signal used in distributed systems to verify that a remote process or node is alive and reachable. A sender (or receiver) emits periodic "I am alive" messages (heartbeats) at interval T; a monitor declares the sender dead if no heartbeat is received within a timeout window (typically 2T–3T) to account for network jitter. Heartbeat-based failure detection is the simplest form of liveness checking and underpins: ZooKeeper session keepalives (client→server ping every session_timeout/3 ms); Kubernetes liveness and readiness probes (kubelet pings HTTP/TCP/exec endpoints); Kafka broker heartbeats to ZooKeeper (default: 3s); TCP keepalive (kernel-level heartbeat over idle connections); load balancer health checks (HTTP GET /health every N seconds). **Limitations**: heartbeat timeout creates a trade-off between false positive rate (short timeout → more false positives from transient delays) and detection latency (long timeout → slow failure detection, long recovery time). Advanced alternatives: phi accrual failure detector (Cassandra — adaptive threshold based on heartbeat interval distribution), SWIM indirect ping (Consul — reduces false positives by triangulating via third nodes).

---

### 🟢 Simple Definition (Easy)

Heartbeat: a computer regularly sends "I'm alive" messages to its supervisor. If the supervisor doesn't hear from it for too long: it assumes it's dead. Like a soldier reporting in every hour. If no report for 3 hours: assume captured (declare dead). Used everywhere: load balancers checking if servers are up, Kubernetes checking if your app is healthy, ZooKeeper checking if connected clients are still connected.

---

### 🔵 Simple Definition (Elaborated)

Heartbeat in practice: two variants. Push heartbeat: sender proactively sends "alive" every T seconds. Monitor: "if I don't receive a heartbeat within 3T, sender is dead." Pull heartbeat (health check): monitor sends a probe request every T seconds; sender responds. Monitor: "if no response within timeout, sender is dead." Kubernetes uses pull-style: kubelet sends HTTP GET /health to your app every 10 seconds (configurable). No response within 1 second timeout, and it fails 3 times (failureThreshold=3): pod marked unhealthy and restarted. TCP keepalive: hybrid — kernel sends keepalive probe after idle period (push from kernel perspective, but only after inactivity).

---

### 🔩 First Principles Explanation

**Heartbeat variants, timeout trade-offs, and adaptive detection:**

```
HEARTBEAT VARIANTS:

  1. PUSH HEARTBEAT (sender-initiated):
     Sender: every T seconds, sends HB message to monitor.
     Monitor: "last_hb + timeout < now? → declare dead."
     Example: ZooKeeper client sends PING to ZooKeeper server every session_timeout/3 ms.
              If server doesn't receive PING in session_timeout ms: session expired → client dead.
              Default session_timeout=40,000ms → PING every ~13,333ms.

  2. PULL HEARTBEAT (monitor-initiated = health check):
     Monitor: every T seconds, sends probe (HTTP GET, TCP connect, exec) to sender.
     Sender: responds with 200 OK or echo.
     No response in timeout: sender unhealthy.
     Example: Kubernetes liveness probe:
       livenessProbe:
         httpGet:
           path: /health
           port: 8080
         initialDelaySeconds: 30
         periodSeconds: 10
         timeoutSeconds: 1
         failureThreshold: 3

  3. BIDIRECTIONAL:
     Both sender and monitor detect each other's failures.
     Example: Kafka broker and ZooKeeper.
             Kafka: sends heartbeats to ZK. ZK: checks session timeout.
             Also: ZK sends to Kafka (ZK watches → notifies on expiry).

TIMEOUT CONFIGURATION: THE TRADE-OFF MATRIX:

  Short timeout (T=1s, timeout=3s):
    PROS: Fast failure detection (3s to declare dead → fast failover).
    CONS: High false positive rate (transient network hiccup → wrongly declare dead → unnecessary failover).

  Long timeout (T=30s, timeout=90s):
    PROS: Low false positive rate (very resistant to transient hiccups).
    CONS: Slow failure detection (90s before failover starts → long downtime).

  OPTIMAL: timeout = max(expected_latency_jitter × safety_factor, acceptable_detection_latency).
    Production cloud: 99th percentile inter-DC heartbeat latency ≈ 50ms.
    Transient spikes (GC pauses, TCP retransmit): up to 2s.
    Timeout = max(2s × 3, 30s) = 30s. Failover within 30s. Acceptable for most services.

  TCP KEEPALIVE (kernel-level heartbeat):
    tcp_keepalive_time=7200s: sends first keepalive after 2 hours of inactivity.
    tcp_keepalive_intvl=75s: resends every 75s.
    tcp_keepalive_probes=9: after 9 failed probes: TCP reset (9×75s = 675s ≈ 11 minutes).

    Default: very long → appropriate for long-lived idle connections (SSH sessions, DB connections).
    Tune for distributed systems: set tcp_keepalive_time=60s to detect dead connections faster.

PHI ACCRUAL FAILURE DETECTOR (ADVANCED HEARTBEAT):

  Problem: fixed timeout is brittle — doesn't adapt to network conditions.

  Solution: instead of binary alive/dead threshold, compute probability of failure.

  Algorithm (Cassandra):
    Maintain sliding window of last N heartbeat arrival intervals.
    Fit normal distribution: mean μ, standard deviation σ.

    φ = -log10(P(t > t_now - t_last_heartbeat))

    Where P is the probability under the fitted distribution.

    If μ=1000ms (normal interval), σ=50ms (low jitter):
      After 1100ms without heartbeat: φ ≈ 2 (low suspicion).
      After 1500ms: φ ≈ 5 (moderate suspicion).
      After 2000ms: φ ≈ 8 (declare dead — convict_threshold=8).

    If μ=1000ms but σ=500ms (high jitter network):
      Same times → lower φ (network is normally jittery → longer tolerance).

    ADAPTIVE: high-jitter network → higher threshold before declaring dead.
    LOW-JITTER network → faster detection.

    Cassandra's phi_convict_threshold=8 means:
      Declaring dead = ~1 in 10^8 probability that node is actually alive.
      Very conservative (few false positives). Slower detection.
      For faster detection: lower threshold (phi_convict_threshold=5).

KUBERNETES PROBES (HEARTBEAT VARIANTS):

  1. Liveness probe: "Is the container alive?" → if fails: restart container.
  2. Readiness probe: "Is the container ready to serve traffic?" → if fails: remove from Service Endpoints (no traffic). Does NOT restart.
  3. Startup probe: "Has the container started?" → if fails: kill and restart. Prevents liveness probe from firing before app is ready.

  Use liveness: for unrecoverable failure (deadlock, OOM, stuck process).
  Use readiness: for temporary unavailability (loading data, warming up cache, dependency down).

  COMMON MISTAKE: Using liveness probe for something that returns 503 temporarily.
    App: returns 503 during cache warmup (30s startup).
    Liveness probe: 503 → restart. App restarts. 503 again. Restart loop.
    FIX: Use startup probe (ignores liveness/readiness until startup completes) OR
         increase initialDelaySeconds to be > startup time.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT heartbeat:

- No way to detect silent node failures (process crash, network partition, OOM kill)
- Load balancers send traffic to dead servers → connection timeouts for clients
- Cluster leader election: no way to detect if current leader is still alive

WITH heartbeat:
→ Timely failure detection: dead nodes identified within timeout window
→ Automatic recovery: load balancers remove unhealthy backends; Kubernetes restarts dead pods
→ Simple to implement: just a periodic ping + timeout check

---

### 🧠 Mental Model / Analogy

> A lighthouse keeper radioing mainland control every hour: "All clear." If control doesn't hear within 2 hours, they send a rescue boat (failover). Short radio interval = fast detection that keeper is in trouble, but thunderstorms may interfere. Long interval = fewer false alarms, but keeper could be struggling for hours before anyone knows.

"Radio every hour" = heartbeat interval T
"No response in 2 hours → rescue boat" = timeout window → failover trigger
"Thunderstorm interference" = network jitter causing false positives

---

### ⚙️ How It Works (Mechanism)

```
PULL HEARTBEAT (HTTP health check):

  Monitor: every periodSeconds, sends HTTP GET /health to container port.
  Container responds 200 OK (healthy) or non-200 / timeout (unhealthy).
  After failureThreshold consecutive failures: mark unhealthy → trigger action.
  After successThreshold consecutive successes (after failure): mark healthy.

PUSH HEARTBEAT (ZooKeeper session):

  Client: sends PING every session_timeout/3 ms.
  Server: notes last PING timestamp per session.
  Server: session sweeper thread runs periodically.
    For each session: if now - last_ping > session_timeout → expire session.
  On expiry: ephemeral znodes deleted → watches triggered → distributed locks released.
```

---

### 🔄 How It Connects (Mini-Map)

```
Failure Modes (how nodes fail — crash-stop, omission, partitions)
        │
        ▼
Heartbeat ◄──── (you are here)
(detect failures via periodic liveness signals)
        │
        ├── Circuit Breaker: uses failure detection to open circuit (stop sending requests)
        ├── Gossip Protocol: phi accrual failure detector is an advanced heartbeat variant
        └── Leader Election: heartbeat timeout triggers re-election when leader appears dead
```

---

### 💻 Code Example

**Spring Boot Actuator health endpoint + Kubernetes liveness probe:**

```java
// Spring Boot: /actuator/health endpoint (built-in readiness/liveness support)
// application.yaml:
management:
  endpoint:
    health:
      probes:
        enabled: true       # /actuator/health/liveness + /actuator/health/readiness
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true

// Custom health indicator:
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    private final DataSource dataSource;

    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            conn.createStatement().execute("SELECT 1"); // Quick ping
            return Health.up().withDetail("db", "connected").build();
        } catch (Exception e) {
            // Liveness: DB down → return DOWN → pod restarted. (Too aggressive — use readiness!)
            // Readiness: DB down → return DOWN → pod removed from LB. (Correct!)
            return Health.down().withDetail("error", e.getMessage()).build();
        }
    }
}
```

```yaml
# kubernetes/deployment.yaml:
spec:
  containers:
    - name: app
      image: myapp:1.0

      startupProbe: # Phase 1: app starting up (up to 5 min allowed)
        httpGet:
          path: /actuator/health/liveness
          port: 8080
        failureThreshold: 30 # 30 × 10s = 5 minutes max startup time
        periodSeconds: 10

      livenessProbe: # Phase 2: is app alive? (restart if not)
        httpGet:
          path: /actuator/health/liveness
          port: 8080
        periodSeconds: 10
        timeoutSeconds: 1
        failureThreshold: 3 # 3 consecutive failures → restart

      readinessProbe: # Is app ready to serve traffic? (remove from LB if not)
        httpGet:
          path: /actuator/health/readiness
          port: 8080
        periodSeconds: 5
        timeoutSeconds: 1
        failureThreshold: 3 # 3 failures → remove from Service endpoints
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A 200 OK from /health means the application is fully functional | /health endpoint only tests what you implement. A common mistake: /health returns 200 even when a critical dependency (database, message queue) is degraded. Design /health to check all critical dependencies. Spring Boot Actuator health composites: a DOWN sub-indicator cascades to the overall status. Tailor liveness (can the JVM run?) vs readiness (are all dependencies healthy?) separately                        |
| Heartbeat timeout should match the heartbeat interval           | Timeout must be significantly longer than the interval to account for jitter. Rule of thumb: timeout = 3× interval at minimum. For variable-latency networks: timeout = mean + 4×stddev of heartbeat delivery time. A timeout equal to the interval would cause false positives on every minor network hiccup. ZooKeeper example: PING every T/3, timeout = T (3× multiple)                                                    |
| Liveness and readiness probes serve the same purpose            | Liveness probe failure: pod is restarted (unrecoverable state). Readiness probe failure: pod is temporarily removed from traffic (Service Endpoints) but NOT restarted. Use liveness for: deadlock, OOM (unrecoverable). Use readiness for: slow startup, temporary dependency outage, rate limiting (temporarily stop receiving traffic). Using liveness for a temporary condition causes restart loops and amplifies outages |
| TCP keepalive ensures application-level health                  | TCP keepalive only verifies the TCP connection is alive — that the operating system on the other end responds to kernel-level probes. The application process can be deadlocked, OOM-killed, or returning errors while TCP keepalive succeeds. For application health: use HTTP health checks or application-level heartbeats that exercise the actual code path                                                               |

---

### 🔥 Pitfalls in Production

**Cascading restart loops from aggressive liveness probes:**

```
SCENARIO: Microservice with liveness probe on /health.
  /health checks: database connectivity, Redis connectivity, downstream API.
  Downstream API: having an outage (5xx responses).

  What happens:
    /health: GET /downstream/status → 503. Returns DOWN.
    Kubernetes liveness probe: 3 consecutive failures → KILL POD → RESTART.
    Restarted pod: same /health check → same 503 → KILL AGAIN.
    Result: CrashLoopBackOff. Your service is down during the downstream outage.
    WORSE: downstream recovers. Your pod is in exponential backoff (2min, 4min...).
    Recovery delayed. Total outage > downstream outage duration.

BAD: Liveness probe checking external dependencies:
  @GetMapping("/health")
  public ResponseEntity<Map<String, String>> health() {
      try {
          downstreamApiClient.getStatus(); // WRONG: external call in liveness check!
          return ResponseEntity.ok(Map.of("status", "UP"));
      } catch (Exception e) {
          return ResponseEntity.status(503).body(Map.of("status", "DOWN")); // Kills pod!
      }
  }

FIX: Separate liveness (is JVM alive?) from readiness (are dependencies OK?):
  @GetMapping("/health/liveness")
  public ResponseEntity<String> liveness() {
      // Only check: is the JVM alive and able to process requests?
      return ResponseEntity.ok("UP");
      // Do NOT check external dependencies here.
  }

  @GetMapping("/health/readiness")
  public ResponseEntity<Map<String, Object>> readiness() {
      Map<String, Object> status = new HashMap<>();
      boolean ready = true;

      // Check dependencies:
      try { db.getConnection(); status.put("db", "UP"); }
      catch (Exception e) { status.put("db", "DOWN"); ready = false; }

      try { downstreamApi.getStatus(); status.put("downstream", "UP"); }
      catch (Exception e) { status.put("downstream", "DOWN"); ready = false; }

      return ready
          ? ResponseEntity.ok(status)
          : ResponseEntity.status(503).body(status);
      // Readiness failure: pod removed from Service endpoints. NOT restarted.
  }
```

---

### 🔗 Related Keywords

- `Failure Modes` — heartbeat detects crash-stop and omission failures
- `Circuit Breaker` — uses failure rate (from probes) to open/close circuit to failing service
- `Gossip Protocol` — phi accrual failure detector: advanced heartbeat with adaptive threshold
- `Leader Election` — heartbeat timeout detection triggers re-election when leader is silent

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Periodic "alive" signal. Absence within  │
│              │ timeout window = declare dead → failover │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any distributed component needs liveness │
│              │ monitoring: load balancer backends, pods,│
│              │ cluster nodes, distributed lock holders  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Phi accrual or SWIM is more appropriate  │
│              │ (high-jitter networks where fixed timeout│
│              │ causes false positives at scale)         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Soldier checks in every hour; 3 missed  │
│              │  check-ins = declare MIA."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Failure Modes → Circuit Breaker →        │
│              │ Gossip Protocol → Kubernetes Probes      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A load balancer health checks a backend server every 5 seconds with a 1-second timeout and failureThreshold=3. The backend server experiences a 12-second GC pause. At what timestamp does the load balancer remove the backend from rotation? How long does it take to add it back (assume successThreshold=2)? What is the total duration of potential client errors if requests are not retried?

**Q2.** Kubernetes liveness probes and ZooKeeper session heartbeats both use heartbeat timeouts to detect failures. Compare the consequences of a false positive (declaring alive-node as dead) for each: what happens when Kubernetes wrongly restarts a pod vs. when ZooKeeper wrongly expires a session (which held a distributed lock)? Which false positive is more dangerous, and how does each system mitigate false positives?
