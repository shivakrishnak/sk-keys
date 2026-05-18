---
id: DST-075
title: Chaos Engineering in Production
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-007, DST-008, DST-068
used_by: []
related: DST-007, DST-008, DST-033, DST-055, DST-068
tags:
  - distributed
  - chaos-engineering
  - resilience
  - game-day
  - fault-injection
  - netflix
  - production
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 75
permalink: /technical-mastery/distributed-systems/chaos-engineering/
---

⚡ TL;DR - Chaos engineering is the practice of
deliberately injecting failures into production (or
staging) systems to discover weaknesses before they
cause incidents; Netflix invented the term with Chaos
Monkey (random EC2 termination) in 2010; a proper
chaos experiment follows: hypothesize (system will
behave X under fault Y), define steady state (a
measurable metric), inject the fault, observe the
blast radius, and roll back; the key principle is
"fail on purpose in a controlled way before the
failure happens on its own in an uncontrolled way."

---

### 📋 Entry Metadata

| #075 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Cascading Failures, Blast Radius, S3 Outage Case Study | |
| **Used by:** | N/A (operational practice) | |
| **Related:** | Cascading Failures, Circuit Breakers, Observability, S3 Outage | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT CHAOS ENGINEERING:**
An engineering team builds a new payment service
with circuit breakers, retries, and timeouts. They
tested it in staging. It works perfectly. Staging,
however, does not have: the same traffic patterns,
the same network topology, or the 3-year-old slow
database that production has inherited.

On a Tuesday afternoon: a single downstream API
adds a 2-second delay to 10% of responses. This
was never tested. The circuit breaker threshold is
50 errors per minute. With the 2-second delay:
threads pile up, connection pool fills, errors spike
to 200/min, circuit opens, the entire service becomes
unavailable. 2 hours of downtime. The fix: tune the
circuit breaker's slow-call rate threshold.

Chaos engineering would have found this: run a
controlled experiment in production (10% latency
injection on the downstream API), observe behavior,
find the threshold mismatch, fix it before it causes
a real outage.

---

### 📘 Textbook Definition

**Chaos engineering** (Chaos Engineering Principles,
Netflix, 2016): "the discipline of experimenting on
a system in order to build confidence in the system's
capability to withstand turbulent conditions in production."

**Key distinction from testing:**
Testing verifies known behavior ("does the retry work?").
Chaos engineering discovers unknown weaknesses
("what happens when the retry encounters something
we didn't anticipate?").

**Chaos Monkey:** Netflix's original tool (2010).
Randomly terminates EC2 instances in production.
Forces engineers to design services that survive
instance termination.

**Simian Army:** Netflix's suite of chaos tools:
Chaos Monkey (instance termination), Latency Monkey
(network latency injection), Conformity Monkey (checks
for best practices), Security Monkey (checks for
security issues).

---

### ⏱️ Understand It in 30 Seconds

```
CHAOS EXPERIMENT TEMPLATE:

1. DEFINE STEADY STATE:
   What metric represents "system is healthy"?
   Example: 99% of checkout requests succeed within 500ms.
   Measure this BEFORE the experiment.

2. FORM HYPOTHESIS:
   "Injecting X fault will NOT affect the steady state
   metric because [mechanism Y protects against it]."
   Example: "Terminating one payment-service node will
   not change checkout success rate because the LB
   will route to the remaining 2 nodes within 5 seconds."

3. INJECT THE FAULT (small blast radius first):
   Start with 1% of traffic, 1 node, or 1 region.
   Tools: Chaos Monkey, Toxiproxy, tc netem,
     AWS FIS (Fault Injection Simulator),
     Gremlin, ChaosBlade.

4. OBSERVE:
   Is the steady state metric affected?
   What is the actual blast radius vs hypothesized?
   Did any unexpected services fail?

5. ROLL BACK:
   Remove the fault injection.
   Observe recovery time.

6. LEARN AND FIX:
   If hypothesis was correct: confidence increased.
   If hypothesis was wrong: you found a real weakness.
   Fix the weakness. Re-run experiment to confirm.
```

---

### 🔩 First Principles Explanation

**CATEGORIES OF CHAOS EXPERIMENTS:**

**Category 1: Resource Exhaustion**

```bash
# CPU saturation experiment:
# Hypothesis: service handles CPU spike gracefully
# because thread pool limits concurrent work.

# Inject: stress test on a single node
stress --cpu 8 --timeout 60s

# Observe: 
# - Does the service shed load (429 responses)?
# - Or does it become unresponsive (timeouts)?
# - Do other services notice (circuit breakers)?

# EXPECTED (healthy): thread pool limits CPU usage.
# Upstream gets 429 (Too Many Requests).
# Circuit breaker opens on upstream.
# Other services are unaffected.

# UNHEALTHY: service becomes unresponsive.
# Upstream timeouts pile up. Connection pool exhausted.
# Cascade to other services.
```

**Category 2: Network Faults**

```bash
# Using tc netem (Linux traffic control):

# Inject packet loss on eth0:
sudo tc qdisc add dev eth0 root netem loss 10%

# Inject latency:
sudo tc qdisc add dev eth0 root netem delay 200ms 50ms
# "200ms delay ± 50ms jitter" (random distribution)

# Inject latency to specific IP (better blast radius):
sudo tc qdisc add dev eth0 root handle 1: prio
sudo tc qdisc add dev eth0 parent 1:3 handle 30: \
  netem delay 500ms
sudo tc filter add dev eth0 protocol ip parent 1:0 \
  prio 3 u32 match ip dst 10.0.0.1/32 flowid 1:3
# Only delays traffic to 10.0.0.1

# Remove:
sudo tc qdisc del dev eth0 root

# USING TOXIPROXY (application-level, safer):
# Start toxiproxy:
toxiproxy-server &

# Create proxy:
toxiproxy-cli create --listen=localhost:5433 \
  --upstream=db:5432 db_proxy

# Inject latency:
toxiproxy-cli toxic add db_proxy \
  -t latency -a latency=500

# Remove:
toxiproxy-cli toxic delete db_proxy latency_downstream

# Toxiproxy is MUCH safer than tc netem for production:
# - Scoped to specific proxy (not all network traffic)
# - Easily removed without kernel manipulation
# - Supports: latency, jitter, bandwidth throttle,
#   slow_close, timeout, slicer, limit_data
```

**Category 3: Service Termination**

```bash
# Chaos Monkey approach: terminate random pod.

# Kubernetes:
kubectl get pods -n prod -l app=payment-service \
  -o name | shuf -n 1 | xargs kubectl delete -n prod

# Observe:
# - How long until a new pod starts? (restartPolicy)
# - What happens to in-flight requests during termination?
# - Does the LB stop routing to the terminated pod
#   before it's gone? (readinessProbe matters here)
# - Do upstream services handle the brief 503 gracefully?

# GOOD: readinessProbe removes pod from LB rotation
# before SIGTERM is sent. Zero downtime.
# BAD: readinessProbe not configured. LB still routes
# to pod during termination. Brief errors.
```

**Category 4: Clock Skew**

```bash
# On a test node: advance the clock by 1 second:
sudo date -s "$(date '+%Y-%m-%d %H:%M:%S' \
  --date='+1 second')"

# Or use faketime for a specific process:
faketime '2024-01-01 00:00:00' your_service &
# Run the service in a controlled clock environment.

# WHAT TO OBSERVE:
# - Does the distributed lock break? (expired leases)
# - Does the Raft election fire prematurely?
# - Does the TLS certificate appear expired?
# - Does the rate limiter break? (time-window based)

# For Spanner/HLC-based systems:
# Introduce NTP skew:
sudo systemctl stop systemd-timesyncd
sudo date -s "$(date '+%Y-%m-%d %H:%M:%S' \
  --date='+600 milliseconds')"
# A 600ms skew exceeds typical epsilon bounds.
# Observe: does the system detect and handle this?
```

**CHAOS MATURITY MODEL:**

```
Level 1 (Chaos in Staging):
  Fault injection only in non-production environments.
  LOW value: staging doesn't have production traffic
    patterns.
  
Level 2 (Chaos Canary):
  Inject faults on a small percentage of production
  traffic (e.g., 1% of users get 100ms extra latency).
  Observe: does steady state metric change?
  
Level 3 (Chaos in Production - controlled):
  Full production fault injection with:
  - Automatic rollback if steady state metric degrades >
    threshold.
  - Limited blast radius (single AZ, single pod, etc.)
  - Scheduled during low-traffic periods initially.
  
Level 4 (Continuous Chaos):
  Chaos experiments run automatically as part of CI/CD.
  Every deploy is tested with a chaos experiment.
  High confidence in resilience.
  Netflix operates at this level.
```

**AUTOMATIC ROLLBACK:**

```python
# Chaos experiment with automatic rollback
# using a steady state metric check.

import time
import requests

def run_chaos_experiment(
    inject_fn,
    restore_fn,
    steady_state_check,
    experiment_duration_s: int = 60,
    check_interval_s: int = 5
) -> bool:
    """
    Run a chaos experiment with automatic rollback.
    
    inject_fn: function that injects the fault.
    restore_fn: function that removes the fault.
    steady_state_check: function that returns True
      if steady state is maintained.
    
    Returns: True if hypothesis held (steady state maintained).
    """
    print("Measuring steady state before experiment...")
    if not steady_state_check():
        print("ABORT: Steady state not healthy before experiment.")
        return False

    print("Injecting fault...")
    inject_fn()
    
    start = time.time()
    try:
        while time.time() - start < experiment_duration_s:
            time.sleep(check_interval_s)
            if not steady_state_check():
                print("ROLLBACK: Steady state degraded!")
                return False
            elapsed = time.time() - start
            print(f"  {elapsed:.0f}s: Steady state holding.")
        print("Experiment complete: hypothesis confirmed.")
        return True
    finally:
        print("Restoring system...")
        restore_fn()


# Example: inject 500ms DB latency, verify checkout OK.
def check_checkout_success_rate() -> bool:
    resp = requests.get(
        "http://prometheus:9090/api/v1/query",
        params={"query":
            "rate(checkout_requests_total{status='ok'}[1m]) "
            "/ rate(checkout_requests_total[1m])"}
    )
    success_rate = float(
        resp.json()["data"]["result"][0]["value"][1]
    )
    print(f"  Checkout success rate: {success_rate:.2%}")
    return success_rate >= 0.99  # 99% threshold

result = run_chaos_experiment(
    inject_fn=lambda: requests.post(
        "http://toxiproxy:8474/proxies/db/toxics",
        json={"name": "db_latency", "type": "latency",
              "attributes": {"latency": 500}}
    ),
    restore_fn=lambda: requests.delete(
        "http://toxiproxy:8474/proxies/db/toxics/db_latency"
    ),
    steady_state_check=check_checkout_success_rate,
    experiment_duration_s=120
)
print("Experiment result:", "PASS" if result else "FAIL")
```

---

### 🧠 Mental Model / Analogy

> Chaos engineering is like a fire drill for your
> distributed system. You know your office has fire
> exits, fire extinguishers, and a fire alarm. But
> you don't know if they all work under real conditions
> until you test them. A fire drill (controlled chaos)
> reveals: the exit door that sticks, the alarm that's
> too quiet on floor 3, the employee who doesn't know
> the assembly point. You fix all these before the
> real fire. The alternative: discover them during
> an actual fire at 2 AM. Chaos engineering finds
> your "sticky exits" before the real incident.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The basic concept:**
Inject failures on purpose, in a controlled way, to
discover weaknesses before they cause uncontrolled
incidents.

**Level 2 - Steady state is key:**
The experiment is only meaningful if you define
what "healthy" looks like first (the steady state
metric). Without it, you don't know if the fault
actually impacted the system.

**Level 3 - Blast radius control:**
Start small: 1% of traffic, 1 pod, 1 AZ. Increase
scope as confidence grows. Never run a chaos
experiment that risks the entire production system
on the first run.

**Level 4 - Automatic rollback:**
Production chaos experiments must have automatic
rollback: if the steady state metric degrades beyond
a threshold, remove the fault immediately without
human intervention.

**Level 5 - Continuous chaos:**
At maturity: every code change is tested against
a chaos scenario in CI. The chaos experiment is a
gate before production deployment. Netflix reached
this level. Most teams are at Level 2-3.

---

### 💻 Code Example

*See the complete fault injection examples and the
`run_chaos_experiment` function with auto-rollback
in the First Principles section above.*

---

### ⚖️ Comparison Table

| Tool | Use Case | Blast Radius Control | Production Safe? |
|---|---|---|---|
| **tc netem** | Network latency, loss, jitter | Low (affects all traffic on interface) | Risky |
| **Toxiproxy** | Per-proxy network faults | High (scoped to specific service) | Yes |
| **Chaos Monkey** | EC2/pod termination | Medium (scope by tag/namespace) | With guardrails |
| **AWS FIS** | Cloud resource faults | High (precise targeting) | Yes |
| **Gremlin** | Full-featured SaaS chaos | High (role-based, per-target) | Yes |
| **ChaosBlade** | Kubernetes + JVM + OS | High | With config |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Chaos engineering is only for companies at Netflix scale" | Chaos engineering benefits any system that needs to be reliable. A 5-service e-commerce platform benefits from chaos experiments. You discover: does the payment service circuit-break correctly when the inventory service is slow? Does the LB remove a crashed pod quickly enough? |
| "Run chaos experiments only in staging" | Staging lacks production traffic patterns, data, and scale. Real weaknesses often only appear in production. Start in staging to build confidence, then move to production with strict blast radius controls. |
| "Chaos engineering is dangerous" | Uncontrolled outages are dangerous. Controlled chaos experiments with auto-rollback are safer than discovering the same failure by accident at 2 AM. The discipline of defining steady states, limiting blast radius, and automatic rollback makes chaos engineering safer than it appears. |
| "You need a dedicated chaos engineering team" | You need engineers who understand the system and can define meaningful steady states and hypotheses. A single on-call engineer with 2 hours per week can run effective chaos experiments. Tooling is the enabler, not headcount. |

---

### 🚨 Failure Modes & Diagnosis

**Chaos Experiment with Uncontrolled Blast Radius**

**Symptom:** A chaos experiment intended to test one
service brought down three unrelated services. The
experiment was "inject 10% packet loss on the payment
service's network interface." But payment-service shares
a host (Kubernetes node) with user-service and
notification-service. The tc netem rule applied to
the node's interface, not just payment-service's
network. All three services lost 10% of their packets.

**Root Cause:** tc netem operates at the Linux network
interface level, not the pod/container level. All
pods on the node share the same network interface.

**Diagnosis:**
```bash
# Before any chaos experiment: verify blast radius.
# Check: what else runs on this node?
kubectl get pods -n prod --field-selector \
  spec.nodeName=<node-name>
# If other services run on the same node: tc netem
# will affect all of them.

# SAFER ALTERNATIVES:
# 1. Use Toxiproxy at the application level (proxy-based).
#    Blast radius: only the specific proxy.
# 2. Use CNI-level policies (Cilium, Calico) for
#    per-pod network faults.
# 3. Use AWS FIS or Gremlin which provide container-
#    level targeting.
# 4. Run chaos on a dedicated node (kubectl cordon
#    all other pods first).
```

---

### 🔗 Related Keywords

**Prerequisites:** `Cascading Failures` (DST-007),
`Blast Radius Reduction` (DST-008),
`S3 Outage 2017` (DST-068)

**Related:** `Circuit Breakers` (DST-033),
`Observability` (DST-055)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CHAOS EXPERIMENT STEPS                                  │
│ 1. Define steady state metric (measurable)              │
│ 2. Form hypothesis ("will NOT be affected")             │
│ 3. Inject fault (small blast radius first)              │
│ 4. Observe (steady state metric + blast radius)         │
│ 5. Roll back (automatically if metric degrades)         │
│ 6. Learn and fix (if hypothesis was wrong)              │
├─────────────────────────────────────────────────────────┤
│ TOOLS: Toxiproxy (network), Chaos Monkey (termination), │
│   AWS FIS (AWS infra), Gremlin (full SaaS)              │
├─────────────────────────────────────────────────────────┤
│ START AT: Level 2 (production canary, 1% traffic)      │
│ TARGET:   Level 3 (controlled production + auto-rollback│
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Chaos engineering makes explicit the principle that
assumptions are the most dangerous part of any
complex system. Engineers assume: "the circuit breaker
will open when the downstream is slow." The circuit
breaker will open - but does it open at the right
threshold? Does the upstream service handle 429s
gracefully? Does the alert fire before user-facing
errors occur? These are all assumptions until tested.
Chaos engineering converts assumptions into verified
facts or discovered weaknesses. This principle
transfers beyond operations: in software design,
testing is "chaos engineering for your code":
deliberately putting your code in failing states
to discover weaknesses. In security, penetration
testing is chaos engineering for your security
posture. The discipline of controlled, hypothesis-
driven failure injection is universally applicable.

---

### 💡 The Surprising Truth

Netflix's Chaos Monkey was built by accident. In 2010,
Netflix was migrating to AWS and discovered that EC2
instances could fail unexpectedly. An engineer wrote
a script to randomly terminate EC2 instances during
business hours to force engineers to design for
failure. The name "Chaos Monkey" came from the
analogy of a monkey in a data center pulling cables
at random. The key constraint: it ran only during
business hours. If it caused a problem, engineers
were present to fix it. This constraint - run chaos
during business hours when engineers can respond -
is still the right default for teams starting with
chaos engineering. Running chaos at 3 AM is only
appropriate for mature systems with proven resilience
and robust auto-remediation. Start with business
hours. Build confidence. Expand scope.

---

### ✅ Mastery Checklist

1. [DESIGN] Define a chaos experiment for a circuit
   breaker: hypothesis, steady state metric, fault
   injection method, blast radius, rollback criterion.
2. [RUN] Using Toxiproxy locally: inject 500ms latency
   on a dependency. Observe: does your retry logic
   create a stampeding herd (all retries at the same
   time)? How do you fix this?
3. [CONFIGURE] Implement `run_chaos_experiment` from
   this entry with an actual steady state metric
   from your service (use Prometheus). Run it against
   a staging environment.
4. [AUDIT] List three assumptions your current system
   makes about its dependencies. Design a chaos
   experiment that would validate or invalidate each.
5. [LEVEL UP] Describe what would be needed to run
   chaos experiments in CI/CD (continuous chaos).
   What guardrails are required? What steady state
   metrics would you use as a deployment gate?
