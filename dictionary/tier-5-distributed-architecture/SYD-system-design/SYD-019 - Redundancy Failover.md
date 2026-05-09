---
id: SYD-019
title: Redundancy Failover
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008
used_by: SYD-020, SYD-021
related: SYD-020, SYD-021, SYD-022
tags:
  - reliability
  - intermediate
  - architecture
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /syd/redundancy-failover/
---

# SYD-019 - Redundancy Failover

⚡ TL;DR - Redundancy means having backup systems ready; failover means automatically switching to the backup when primary fails. Together they eliminate single points of failure and enable high availability.

| #694            | Category: System Design                          | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | High Availability, Load Balancing, Monitoring    |                 |
| **Used by:**    | Infrastructure Design, Reliability Engineering   |                 |
| **Related:**    | Active-Active, Active-Passive, Disaster Recovery |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Single server running the app. Server crashes. App down. Customers can't access service. No backup. Revenue lost.

**THE BREAKING POINT:**
Any single point of failure will eventually fail (hardware breaks, software bugs, operator mistakes). Business can't tolerate single points of failure.

**THE INVENTION MOMENT:**
"Have a backup ready. If primary fails, automatically switch to backup. Instant recovery, no manual intervention."

**EVOLUTION:**
Redundancy as an engineering principle predates computing - aerospace engineers duplicated flight-critical systems in the 1940s (dual engines, dual hydraulic systems). Computing adopted redundancy first for hardware (RAID for disk, dual power supplies for servers), then for software services (multiple application instances, database replicas). Cloud computing made redundancy cheap: deploying to two availability zones costs marginally more than one. Modern systems add application-level redundancy (circuit breakers, bulkheads) on top of infrastructure redundancy. The discipline evolved from hardware fault tolerance into a layered software architecture pattern.

---

### 📘 Textbook Definition

- **Redundancy:** Having multiple copies of critical components (servers, databases, network connections) so that if one fails, others continue operating.
- **Failover:** Automatic (or manual) process of switching traffic/workload from a failed primary component to a redundant backup component, typically triggered by monitoring alerts or health checks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Redundancy = have backup. Failover = automatically use backup if primary fails.

**One analogy:**

> A car has one steering wheel (primary). If it jams, the car is stuck. Better design: electric power steering (primary) + mechanical backup steering (redundant). If electric fails, driver can still steer mechanically (failover). Car keeps working.

**One insight:**
Redundancy without automatic failover (manual fix) = long downtime. Failover without redundancy = doesn't help. Both are required.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All components fail eventually (hardware wear, software bugs, operator mistakes)
2. Failure is not a question of "if" but "when"
3. Business criticality determines redundancy required
4. Automatic failover faster than manual recovery

**DERIVED DESIGN:**
For each critical component:

- Identify: Is it a single point of failure?
- If yes, add redundancy: replicate the component
- Add monitoring: detect failures quickly
- Add automatic failover: switch to backup without manual intervention
- Test: ensure failover works as designed

**THE TRADE-OFFS:**
**Gain:** No single point of failure. System continues even if component fails. Improved availability.

**Cost:** 2x infrastructure (extra servers, storage, bandwidth). Complexity (monitoring, failover logic, split-brain scenarios). Testing burden.

---

### 🧪 Thought Experiment

**SETUP:**
A web application requires 99.9% availability (SLA).

**Scenario A (No Redundancy):**

- Single web server: 99% uptime (small failure rate)
- System uptime = 99% (SLA not met, business fails)

**Scenario B (Database Redundancy Only):**

- Web servers: 1 (no redundancy), 99% uptime
- Database: 3-instance cluster, 99.9% uptime
- System uptime = min(99%, 99.9%) = 99% (web server is bottleneck)
- SLA not met

**Scenario C (Both Redundant with Failover):**

- Web servers: 3 instances with load balancer, 99.99% combined uptime
- Database: 3-instance cluster, 99.9% uptime
- Automatic failover if any instance fails (< 1 second)
- System uptime ≈ 99.95% (SLA met)

**THE INSIGHT:**
Redundancy of one component doesn't guarantee SLA if other components aren't redundant. Weakest link determines system availability. Must address all critical paths.

---

### 🧠 Mental Model / Analogy

> An airplane has 4 engines. Each engine has 99.5% reliability in flight. If any engine fails, the other 3 can still keep the plane flying (failover to remaining engines, auto-balancing thrust).

- Engines 1-4 → redundant system components
- "Fails" → component failure (hardware, software)
- "Other 3 can compensate" → automatic failover
- "Auto-balancing" → load rebalancing across remaining components

**Where analogy breaks down:** Airplanes have hard limits (can fly on min 2 engines). Software systems can be more flexible (scale down gracefully rather than requiring minimum capacity).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Have backup systems ready. If primary fails, automatically use backup. Service doesn't go down.

**Level 2 - How to use it (junior developer):**
For web tier: use load balancer with 3+ servers. If one fails, load balancer removes it automatically (healthcheck). For database: use replication to standby instance. If primary fails, promote standby to primary (automatic failover).

**Level 3 - How it works (mid-level engineer):**
Implement health checks: every 10 sec, check if component responding. If not, mark as failed. Load balancer routes around failed instance. For stateful components (databases), use replication + monitoring to detect failure + automatic promotion of standby.

**Level 4 - Why it was designed this way (senior/staff):**
Redundancy emerged from reliability engineering: eliminate single points of failure. Failover (vs. manual recovery) reduces downtime by orders of magnitude (minutes to seconds). Automatic failover requires: robust health detection (avoid false positives), fast rerouting (pre-configured standby), and idempotency (failover multiple times without corruption).

---

### ⚙️ How It Works (Mechanism)

Redundancy and failover mechanism:

```
IDENTIFY CRITICAL COMPONENTS:
  ├─ Web servers (stateless, easy to replicate)
  ├─ Databases (stateful, requires replication)
  ├─ Message queues (stateful, requires replication)
  └─ Load balancers (need redundancy too!)

ADD REDUNDANCY:
  Web Servers:
    [WEB-1] ──┐
    [WEB-2] ──┼─ Load Balancer ── Clients
    [WEB-3] ──┘

  If WEB-1 fails, traffic automatically routes to WEB-2 and WEB-3.

  Databases:
    [PRIMARY] ──(replication)── [REPLICA]

    If PRIMARY fails:
      1. Detect failure (replication lag detection, heartbeat)
      2. Promote REPLICA to PRIMARY
      3. Update connection strings (failover)

HEALTH CHECKING (Continuous):
  Every 10 seconds:
    ├─ Load Balancer pings each web server: "Are you alive?"
    ├─ Monitors check database replication lag
    ├─ Checks check message queue depth
    └─ All send heartbeat to monitoring system

FAILURE DETECTION:
  Component misses 3 health checks:
    → Marked as "unhealthy"
    → Removed from rotation (no new traffic)
    → Failover triggered
    → Alert sent to on-call engineer

AUTOMATIC FAILOVER:
  Web tier:
    Load Balancer removes failed instance from pool
    (No action needed, automatic)

  Database tier:
    Monitoring detects primary down
    → Promote replica to primary (automatic)
    → Update connection strings (application reconnects automatically)
    → Alert team to investigate root cause

GRACEFUL DEGRADATION:
  If 1 of 3 web servers fails:
    - System still operating at 66% capacity
    - Latency increases slightly (fewer servers handling load)
    - SLA still met (3-server design was SLA-driven)

  If 2 of 3 web servers fail:
    - System at 33% capacity
    - Still serving traffic
    - Alert escalated: "Critical degradation"

RECOVERY:
  Failed component repaired or replaced
  → Brought back online
  → Health checks pass
  → Automatically reintegrated into rotation
  → Load rebalanced
```

**Failover Timeline Example:**

```
14:30:00 - Primary database disk fails
14:30:05 - Monitoring detects replication lag > threshold
14:30:10 - Automatic failover triggered, replica promoted to primary
14:30:12 - Connection strings updated (app reconnects)
14:30:15 - Service restored (failover complete, ~15 seconds downtime)
14:35:00 - On-call engineer notified and investigating
15:00:00 - Root cause identified, disk replaced
15:15:00 - New replica spun up, replication starts
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Load Balancer
    ↓
Health Check Timer (every 10s)
    ├─ Ping WEB-1 → ALIVE
    ├─ Ping WEB-2 → ALIVE
    └─ Ping WEB-3 → NO RESPONSE
    ↓
WEB-3 marked UNHEALTHY
    ↓
Next request from client
    ├─ Load Balancer sends to WEB-1 or WEB-2
    └─ WEB-3 not in rotation
    ↓
Alert Sent to Monitoring
    ├─ Team notified (on-call paged)
    └─ Incident logged

Meanwhile:
WEB-3 repaired by ops team
    ↓
Health Check: WEB-3 now responding
    ↓
WEB-3 marked HEALTHY
    ↓
Next request:
    ├─ Load Balancer includes WEB-3 again
    └─ Traffic rebalanced (3 servers now)
```

---

### 💻 Code Example

Implementing redundancy and failover:

**Example 1 - Load Balancer Health Checks (Nginx):**

```nginx
upstream app_servers {
    # Define redundant servers
    server app1.internal:8080 max_fails=3 fail_timeout=10s;
    server app2.internal:8080 max_fails=3 fail_timeout=10s;
    server app3.internal:8080 max_fails=3 fail_timeout=10s;

    # Health check configuration
    # Nginx checks each server every 10 seconds
    # If 3 consecutive checks fail, mark unhealthy
    # Remove from rotation until it recovers
}

server {
    listen 80;
    location / {
        proxy_pass http://app_servers;
        # Automatic failover: if app1 fails, redirect to app2/app3
    }
}
```

**Example 2 - Database Failover (PostgreSQL):**

```bash
#!/bin/bash
# Automated database failover script

PRIMARY_HOST="db1.internal"
REPLICA_HOST="db2.internal"
VIP="db-virtual.internal"  # Virtual IP for applications

check_primary() {
    # Check if primary is responding
    if ! pg_isready -h "$PRIMARY_HOST" -p 5432 -q; then
        return 1  # Primary down
    fi
    return 0  # Primary up
}

failover_to_replica() {
    echo "Primary down. Failover to replica..."

    # 1. Promote replica to primary
    ssh "$REPLICA_HOST" "sudo -u postgres pg_ctl promote"

    # 2. Update virtual IP to point to new primary
    ssh "$REPLICA_HOST" "sudo ip addr add $VIP/32 dev eth0"

    # 3. Update connection strings (apps auto-reconnect to VIP)
    echo "Failover complete. Apps reconnecting to $VIP..."

    # 4. Alert ops team
    echo "Failover event: $PRIMARY_HOST → $REPLICA_HOST" | mail -s "DB Failover" ops@company.com
}

# Main loop
while true; do
    if ! check_primary; then
        echo "Primary database down. Initiating failover..."
        failover_to_replica
        break  # Failover complete
    fi
    sleep 10  # Check every 10 seconds
done
```

**Example 3 - Health Check Endpoint (Python Flask):**

```python
from flask import Flask, jsonify
import subprocess
import time

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for load balancer.
    Load balancer calls this every 10 seconds.
    Returns 200 if healthy, 5xx if unhealthy.
    """
    checks = {
        'database': check_database(),
        'disk_space': check_disk_space(),
        'memory': check_memory(),
        'services': check_services()
    }

    overall_healthy = all(checks.values())

    if overall_healthy:
        return jsonify({'status': 'healthy', 'checks': checks}), 200
    else:
        return jsonify({'status': 'unhealthy', 'checks': checks}), 503

def check_database():
    try:
        # Try to connect to database
        result = subprocess.run(
            ['psql', '-U', 'app', '-d', 'mydb', '-c', 'SELECT 1'],
            timeout=5,
            capture_output=True
        )
        return result.returncode == 0
    except:
        return False

def check_disk_space():
    try:
        # Check if disk usage > 90%
        result = subprocess.run(['df', '/'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        usage = int(lines[1].split()[4].rstrip('%'))
        return usage < 90
    except:
        return False

def check_memory():
    try:
        # Check if available memory > 10%
        result = subprocess.run(['free'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        mem_info = lines[1].split()
        used = int(mem_info[2])
        total = int(mem_info[1])
        usage_pct = (used / total) * 100
        return usage_pct < 90
    except:
        return False

def check_services():
    try:
        # Check if critical services are running
        result = subprocess.run(['systemctl', 'is-active', 'app-service'], capture_output=True)
        return result.returncode == 0
    except:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

---

### ⚖️ Comparison Table

| Aspect            | Redundancy                | Failover                                     | Combined                               |
| ----------------- | ------------------------- | -------------------------------------------- | -------------------------------------- |
| **Definition**    | Having backups ready      | Automatically switching                      | Prevents single points of failure      |
| **Without**       | One failure = system down | Downtime = manual recovery                   | Not viable for critical systems        |
| **Cost**          | 2-3x infrastructure       | Monitoring + automation                      | Higher upfront, lower operational cost |
| **Recovery Time** | N/A                       | Seconds (auto) vs. hours (manual)            | Automatic wins for SLA                 |
| **Example**       | 3 web servers vs. 1       | Load balancer detects failure, routes around | 99.9% uptime achievable                |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| "Redundancy guarantees no downtime"          | No. If failover fails or is slow, downtime still occurs. Must test failover constantly.                |
| "We only need redundancy for critical paths" | Correct, but "critical" might be more than you think. Load balancer itself is critical-must redundant. |
| "Manual failover is acceptable"              | For non-critical systems, maybe. For SLA-driven systems, automatic is required (manual is too slow).   |
| "More redundancy = infinite availability"    | No. More redundancy = more complexity = more failure modes. Diminishing returns exist.                 |
| "Redundancy = identical copies"              | Not always. Warm standby or cold backup also "redundant." Depends on RTO requirements.                 |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Failover Doesn't Trigger (Silent Failure)**

**Symptom:**
Primary server fails. Monitoring doesn't alert. Failover doesn't trigger. Service down. Customers angry.

**Root Cause:**
Health check endpoint broken or misconfigured. Load balancer misconfiguration (health check disabled). Network partition between load balancer and primary (LB can't reach primary, but doesn't know why).

**Diagnostic Command:**

```bash
# Test health check manually
curl http://primary-server:8000/health
# If 503 or timeout, primary is down (failover should trigger)

# Check load balancer config
nginx -T | grep -A 20 "upstream app_servers"

# Check health check settings
# Should show: max_fails, fail_timeout configured
```

**Fix:**
Bad approach: "Assume health checks work."
Good approach: (1) Test health checks regularly. (2) Verify load balancer can reach all backends. (3) Add alerting: if health checks failing > 3 times, escalate. (4) Implement circuit breaker: if unreachable, assume down (don't wait for timeout).

**Prevention:**
Regular chaos tests: kill primary server, verify failover triggers within < 15 seconds. Include load balancer in tests.

---

**Failure Mode 2: Split-Brain (Both Primary and Backup Accepting Traffic)**

**Symptom:**
Network partition between primary and backup. Both think they're primary. Both accepting writes. Data corruption (conflicting updates).

**Root Cause:**
Failover triggered on replica side (thinks primary is dead). But primary is still alive (network issue, not server failure). Now both are accepting writes.

**Diagnostic Command:**

```bash
# Check which nodes think they're primary
curl http://primary-candidate-1:8000/status | jq '.is_primary'
curl http://primary-candidate-2:8000/status | jq '.is_primary'

# If both return true: SPLIT BRAIN
```

**Fix:**
Bad approach: Try to merge data (impossible, conflicting updates).
Good approach: (1) Have quorum-based voting (3+ nodes decide who's primary, not just 2). (2) Use heartbeat from multiple paths. (3) Implement "fencing": if node can't talk to quorum, self-isolate (stop serving traffic). (4) Never promote backup if can't confirm primary is truly down.

**Prevention:**
Design failover logic to avoid split-brain: require majority vote (3+ nodes). Test network partitions during chaos engineering.

---

**Failure Mode 3: Failover Cascades (One Failure Causes Many)**

**Symptom:**
Primary database fails. Failover to replica. But during failover, connection floods trigger cascade failure in application tier. Then entire system down (worse than original failure).

**Root Cause:**
Failover logic not graceful. Applications reconnect all at once (thundering herd). Connection pool overwhelmed. Cascade failure.

**Diagnostic Command:**

```bash
# Monitor during failover event
watch -n 1 'curl http://app-lb/status | jq .connections'

# If connections spike to > max_pool, cascade detected
```

**Fix:**
Bad approach: "It's rare, don't worry."
Good approach: (1) Use circuit breakers on application side. (2) Implement exponential backoff for reconnects (spread them out). (3) Warm up connection pool gradually during failover. (4) Load-shedding: drop low-priority traffic if cascade detected.

**Prevention:**
Test failover under load. Simulate cascade scenarios. Implement rate limiting on reconnects.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-008 - Load Balancing]] - distributes traffic away from failed nodes

**Builds On This (learn these next):**
- [[SYD-020 - Active-Active]] - both nodes serve traffic simultaneously
- [[SYD-021 - Active-Passive]] - one node waits as standby
- [[SYD-022 - Disaster Recovery]] - larger-scale failover across regions

**Alternatives / Comparisons:**
- [[SYD-020 - Active-Active]] - both nodes active vs one passive
- [[SYD-021 - Active-Passive]] - simpler; one node waits as standby

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Redundancy = backup systems ready;   │
│              │ Failover = automatically switch      │
│              │ if primary fails                      │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Single point of failure = system      │
│ SOLVES       │ down if that component fails          │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Redundancy alone doesn't help;        │
│              │ must have automatic failover to       │
│              │ achieve high availability              │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Production systems; SLA requirements;  │
│              │ business criticality                  │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Non-critical systems; cost sensitive  │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [High availability, resilience] vs    │
│              │ [cost, complexity, testing burden]    │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Have backup, automatically use if    │
│              │ primary fails."                       │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Active-Active → Disaster Recovery →  │
│              │ Chaos Engineering                     │
└──────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Single points of failure are the enemy of availability. Any component in the critical path that has no redundant alternative becomes the limiting factor for system availability. This applies to supply chains (single-supplier risk), software architecture (single database primary, single message broker), and team structure (single person who knows a critical system). Identify the critical path, find the single points, and eliminate them systematically.

**Where else this pattern appears:**
- **Network paths:** Enterprise networks use redundant switches, routers, and ISP uplinks - the same principle at the network layer.
- **Power supply:** Servers in data centres have dual power supplies connecting to separate PDUs on separate circuits - physical redundancy.
- **Code paths:** Feature flags with fallback logic are code-level redundancy - if the primary code path fails, fall back to the simpler version.

---

### 💡 The Surprising Truth

Redundancy can create false confidence. A system with two servers and automatic failover is not 2x more available than a single server - it is only more available if the failure modes of the two servers are truly independent. A software bug that crashes Server 1 will crash Server 2 identically (correlated failure). A misconfigured network switch that isolates both servers simultaneously eliminates both (common-mode failure). Real redundancy requires fault isolation: different hardware, different availability zones, different software versions. Engineers who count replicas and assume independence often discover correlated failures the hard way.

---

### 🧠 Think About This Before We Continue

**Q1.** Your system has 3 redundant web servers with automatic failover. If one fails, the remaining 2 can't handle 100% of traffic (latency increases 50%). Is this acceptable design? Why or why not?

*Hint:* Think about what happens to latency when 2 servers absorb 100% of traffic intended for 3 - is a 50% latency increase acceptable, and does that depend on your current baseline latency and SLA? Explore whether over-provisioning (sizing for N+1) is the correct design choice.

**Q2.** During a failover event, your database replica is promoted to primary, but the old primary (now down) is still listed in DNS. Apps start connecting to both. How would you prevent split-brain scenarios?

*Hint:* Think about what split-brain means: both servers think they are the primary and accept writes. Explore STONITH (Shoot The Other Node In The Head), distributed consensus (Raft/Paxos), and database-level mechanisms that prevent dual-primary scenarios.

**Q3 (First Principles):** You have primary and standby databases with automatic failover. During testing, failover takes 30 seconds. Your application has connection retry logic with 5-second timeout - during those 30 seconds, 6 retry attempts fail. Design an application-level strategy that survives a 30-second failover transparently.

*Hint:* Think about what retry logic looks like at the application level - exponential backoff with jitter spreads the retry load. Explore whether the database driver's connection failover (JDBC failover URL) operates independently of application-level retry, and whether circuit breakers can hold requests rather than failing them during the failover window.
