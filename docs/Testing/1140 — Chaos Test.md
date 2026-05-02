---
layout: default
title: "Chaos Test"
parent: "Testing"
nav_order: 1140
permalink: /testing/chaos-test/
number: "1140"
category: Testing
difficulty: ★★★
depends_on: "Stress Test, Resilience, Observability"
used_by: "Netflix Chaos Monkey, chaos engineering, SRE, production readiness"
tags: #testing, #chaos-test, #chaos-engineering, #resilience, #fault-injection, #chaos-monkey
---

# 1140 — Chaos Test

`#testing` `#chaos-test` `#chaos-engineering` `#resilience` `#fault-injection` `#chaos-monkey`

⚡ TL;DR — **Chaos testing** (chaos engineering) deliberately injects failures into a running system — kill a pod, inject network latency, corrupt a dependency response — to verify that the system remains resilient and that alerts/recovery mechanisms work as expected. "Break things on purpose in a controlled way, before reality breaks them uncontrolled." Pioneered by Netflix (Chaos Monkey). Tools: **Chaos Monkey**, **Gremlin**, **LitmusChaos** (Kubernetes), **Chaos Toolkit**.

| #1140           | Category: Testing                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Stress Test, Resilience, Observability                             |                 |
| **Used by:**    | Netflix Chaos Monkey, chaos engineering, SRE, production readiness |                 |

---

### 📘 Textbook Definition

**Chaos engineering**: the discipline of experimenting on a system in production (or production-like environment) by introducing controlled failures to verify that the system can withstand turbulent conditions. Coined by Netflix in 2011 with **Chaos Monkey** (randomly terminates EC2 instances in production). Principles of Chaos Engineering (from principlesofchaos.org): (1) **Hypothesize around steady state behavior**: define what "normal" looks like (baseline metrics); (2) **Vary real-world events**: simulate real failures — server crashes, network partitions, database timeouts, disk full; (3) **Run experiments in production**: production has complexities staging can't replicate; (4) **Automate experiments continuously**: run chaos experiments on a schedule, not just before launch; (5) **Minimize blast radius**: start small, limit scope, have rollback. Failure types: (a) **Resource failures**: kill processes, pods, VMs, availability zones; (b) **Network failures**: latency injection, packet loss, network partition, DNS failure; (c) **Application failures**: inject exceptions, return wrong responses, slow dependency responses; (d) **Dependency failures**: simulate downstream service unavailability, timeouts, incorrect payloads. Tools: **Gremlin** (commercial, full-featured, GameDay scheduling), **LitmusChaos** (open-source, Kubernetes-native, CRD-based), **Chaos Toolkit** (open-source, extensible), **Netflix Chaos Monkey** (AWS, kills instances), **Istio fault injection** (service mesh, HTTP-level faults).

---

### 🟢 Simple Definition (Easy)

Netflix runs Chaos Monkey in production: it randomly kills servers. Why? Because real servers fail in production — hardware failures, network issues, cloud zone outages. If Netflix waits for real failures to find out their system handles them, that's a production incident affecting millions of users. Instead, they kill servers on purpose in a controlled way and verify: "Did the system stay up? Did it automatically recover? Did the alerts fire? Did the on-call engineer get paged correctly?" Controlled failures beat surprise failures.

---

### 🔵 Simple Definition (Elaborated)

Chaos engineering differs from stress testing:

- **Stress test**: apply more load than expected — does the system handle volume?
- **Chaos test**: inject infrastructure/application failures — does the system handle faults?

**The chaos engineering mindset**: "Everything will fail eventually. Let's practice now, under controlled conditions, so we're prepared when it happens unexpectedly."

**Chaos experiment structure**:

1. **Define steady state**: what does "normal" look like? (error rate < 0.1%, p99 < 500ms)
2. **Hypothesize**: "If we kill one of three API pods, the load balancer should route traffic to the remaining two, and steady state will be maintained."
3. **Run experiment**: kill one pod; observe system behavior
4. **Verify hypothesis**: did steady state hold? If yes — resilience confirmed. If no — found a real weakness.
5. **Fix** (if failed): improve resilience; repeat experiment until hypothesis holds

**Common hypotheses (and what fails)**:

- "If a database replica fails, the app switches to the primary." (fails if connection pool doesn't reconnect)
- "If the payment service is down, orders are queued and processed later." (fails if there's no queue — orders are lost)
- "If a pod crashes, Kubernetes restarts it within 30 seconds." (fails if liveness probe misconfigured)
- "If a downstream API is slow (2s latency), our circuit breaker opens." (fails if timeout not configured)

---

### 🔩 First Principles Explanation

```yaml
# LITMUS CHAOS — Kubernetes-native chaos engineering (CRD-based)

# Chaos Experiment 1: Kill one of three replicas of the API service
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: api-pod-kill-chaos
  namespace: production
spec:
  appinfo:
    appns: production
    applabel: "app=order-service"
    appkind: deployment

  chaosServiceAccount: litmus-admin

  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "300" # run for 5 minutes
            - name: CHAOS_INTERVAL
              value: "60" # kill a pod every 60 seconds
            - name: FORCE
              value: "false" # graceful termination (SIGTERM first)
            - name: PODS_AFFECTED_PERC
              value: "33" # kill 33% of pods (1 of 3)

  # STEADY STATE HYPOTHESIS: verified before and after experiment
  steadyStateHypothesis:
    title: "Order service handles pod deletion gracefully"
    probes:
      - name: "Error rate stays below 0.5%"
        type: promProbe
        mode: Continuous
        promProbe/inputs:
          endpoint: http://prometheus:9090
          query: "rate(http_requests_total{status=~'5..'}[1m]) / rate(http_requests_total[1m])"
          comparator:
            type: float
            criteria: "<"
            value: "0.005"

      - name: "p99 latency stays below 1000ms"
        type: promProbe
        mode: Continuous
        promProbe/inputs:
          endpoint: http://prometheus:9090
          query: "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[1m]))"
          comparator:
            type: float
            criteria: "<"
            value: "1.0"
```

```yaml
# Chaos Experiment 2: Inject network latency to the database
# Hypothesis: HikariCP connection pool handles 500ms DB latency without errors

apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: db-network-latency
spec:
  experiments:
    - name: pod-network-latency
      spec:
        components:
          env:
            - name: TARGET_CONTAINER
              value: "postgres"
            - name: NETWORK_LATENCY
              value: "500" # inject 500ms of network latency
            - name: JITTER
              value: "100" # ±100ms jitter
            - name: TOTAL_CHAOS_DURATION
              value: "120" # for 2 minutes
            - name: DESTINATION_IPS
              value: "10.0.0.50" # only inject latency to DB IP
```

```python
# CHAOS TOOLKIT experiment (portable, tool-agnostic)

{
  "title": "If the inventory service returns 500 errors, the checkout flow degrades gracefully",
  "description": "Inject HTTP 500 errors into inventory service and verify checkout handles them",

  "steady-state-hypothesis": {
    "title": "System is operating normally",
    "probes": [
      {
        "name": "checkout success rate > 99%",
        "type": "probe",
        "provider": {
          "type": "http",
          "url": "http://prometheus/api/v1/query",
          "params": {"query": "checkout_success_rate > 0.99"},
        },
        "tolerance": true
      }
    ]
  },

  "method": [
    {
      "type": "action",
      "name": "inject 500 errors into inventory service",
      "provider": {
        "type": "process",
        "path": "kubectl",
        "arguments": "patch deployment inventory-service -p '{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"chaos/inject-500\":\"true\"}}}}}'"
      }
    },
    {
      "type": "pause",
      "name": "wait 3 minutes while chaos runs",
      "duration": 180
    }
  ],

  "rollbacks": [
    {
      "type": "action",
      "name": "remove fault injection",
      "provider": {
        "type": "process",
        "path": "kubectl",
        "arguments": "patch deployment inventory-service -p '{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"chaos/inject-500\":null}}}}}'"
      }
    }
  ]
}
```

```
CHAOS MATURITY MODEL:

  Level 1 (Basic): Run chaos in staging/test environment
    → Kill processes, inject latency
    → Verify basic recovery

  Level 2 (Intermediate): Run chaos in production non-peak hours
    → Controlled blast radius (single service, small % of traffic)
    → Automated rollback if steady state violated
    → Observability to detect the impact

  Level 3 (Advanced): Run chaos in production continuously
    → Netflix Chaos Monkey: runs daily
    → GameDays: scheduled full-day chaos exercises
    → Chaos as code: experiments in version control
    → Hypothesis-driven: every experiment starts with a hypothesis

  BLAST RADIUS CONTROL:
  ─────────────────────────────────────────────────────
  • Target percentage: kill 33% of pods (not all)
  • Duration limit: run for 5 minutes max
  • Automated abort: if error rate > 1%, stop experiment
  • Off-peak timing: run during low-traffic windows initially
  • Staging first: validate experiment is safe before production
```

---

### ❓ Why Does This Exist (Why Before What)

Distributed systems fail in unexpected ways: cascading failures that no one predicted, timeout configurations that were never validated, alerts that don't fire for the failure modes they were supposed to detect, recovery procedures that fail because they were written but never tested. Traditional testing verifies that the system works correctly when everything is healthy. Chaos engineering verifies that the system works correctly when things fail — which in production, they inevitably do. The alternative to chaos engineering is discovering system weaknesses during real incidents, at the worst possible time.

---

### 🧠 Mental Model / Analogy

> **Chaos engineering is like fire drills**: fire marshals don't wait for real fires to test whether the evacuation procedure works — they schedule fire drills, watch what goes wrong (two teams chose the same exit, the fire doors were propped open), fix the procedures, and drill again. Similarly, chaos engineers don't wait for real infrastructure failures to find out if the system handles them — they schedule chaos experiments, observe what breaks (alerts didn't fire, circuit breaker wasn't configured, the fallback had a bug), fix the systems, and experiment again. The goal is to have experienced every failure mode in a controlled setting before experiencing it in an uncontrolled one.

---

### 🔄 How It Connects (Mini-Map)

```
Want to verify system resilience to infrastructure failures (not just load)
        │
        ▼
Chaos Test ◄── (you are here)
(inject failures; verify steady state maintained; test recovery; find unknown weaknesses)
        │
        ├── Stress Test: stress test = load; chaos test = infrastructure failure injection
        ├── Observability: chaos tests are useless without metrics/alerting to detect impact
        ├── Resilience Patterns: circuit breakers, retries validated by chaos tests
        └── SRE: chaos engineering is a core SRE practice (Game Days, Chaos Monkey)
```

---

### 💻 Code Example

```java
// FAULT INJECTION in tests (application-level chaos for unit/integration tests)
// Inject faults into mock dependencies to test resilience code

@SpringBootTest
class OrderServiceResilienceTest {

    @MockBean
    private InventoryServiceClient inventoryClient;

    @MockBean
    private PaymentServiceClient paymentClient;

    @Test
    @DisplayName("Order proceeds when inventory service is unavailable (circuit breaker open)")
    void orderProceeds_whenInventoryUnavailable_withFallback() {
        // INJECT FAULT: inventory service throws exception (simulates downtime)
        when(inventoryClient.checkStock(anyString()))
            .thenThrow(new ServiceUnavailableException("Inventory service is down"));

        // VERIFY: circuit breaker fallback is triggered
        when(inventoryClient.checkStock(anyString()))
            .thenReturn(new InventoryResponse("prod-1", true, -1));  // fallback: assume available

        // ACT: place an order
        OrderResponse response = orderService.createOrder(buildTestOrder());

        // ASSERT: order created (with degraded inventory info)
        assertThat(response.getStatus()).isEqualTo("CONFIRMED");
        assertThat(response.getInventoryWarning())
            .isEqualTo("INVENTORY_UNAVAILABLE");  // flagged for manual review
    }

    @Test
    @DisplayName("Slow payment service triggers timeout and retry")
    void paymentTimeout_triggersRetryAndEventualSuccess() {
        // INJECT FAULT: first two calls timeout; third succeeds
        when(paymentClient.charge(any()))
            .thenThrow(new TimeoutException("Payment service timeout"))  // attempt 1
            .thenThrow(new TimeoutException("Payment service timeout"))  // attempt 2 (retry)
            .thenReturn(new PaymentResponse("SUCCEEDED", "pay-123"));   // attempt 3 (success)

        OrderResponse response = orderService.createOrder(buildTestOrder());

        assertThat(response.getStatus()).isEqualTo("CONFIRMED");
        verify(paymentClient, times(3)).charge(any());  // verify 3 attempts
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Chaos testing is only for Netflix-scale systems | Chaos engineering scales to any size. A 3-service system still benefits from knowing: "What happens when service B is down? Does service A fail gracefully or crash? Do alerts fire?" Start with staging and simple experiments (kill a pod; inject 500ms latency). You don't need Chaos Monkey on Day 1 — manual chaos experiments via `kubectl delete pod` give most of the value. |
| Chaos testing means randomly breaking things    | Chaos engineering is disciplined and hypothesis-driven: "We hypothesize that killing one database replica will cause automatic failover in < 30 seconds with < 0.1% error rate impact." If the experiment disproves the hypothesis, you've found a real weakness. Random destruction without hypotheses and metrics is just vandalism, not chaos engineering.                        |
| Chaos testing replaces observability            | Chaos engineering REQUIRES observability to be useful. If you kill a pod and have no metrics to observe the impact, you can't tell if the hypothesis held. Observability (metrics, traces, logs) is the feedback loop that makes chaos experiments meaningful. A chaos experiment without observability is like a medical trial without measuring patient outcomes.                  |

---

### 🔗 Related Keywords

- `Stress Test` — stress test = load; chaos test = fault injection
- `Observability` — required to detect and measure impact of chaos experiments
- `Circuit Breaker` — a key resilience pattern validated by chaos experiments
- `Resilience` — chaos engineering's goal is to validate and improve system resilience
- `SRE` — chaos engineering is a core Site Reliability Engineering practice

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CHAOS ENGINEERING = controlled fault injection          │
│ GOAL: verify resilience before reality tests it        │
│                                                          │
│ EXPERIMENT STRUCTURE:                                   │
│  1. Define steady state (metrics baseline)             │
│  2. Hypothesize: "if X fails, system still works"      │
│  3. Inject fault (kill pod, add latency, 500 errors)   │
│  4. Verify steady state holds                          │
│  5. Fix if hypothesis fails; repeat until it holds     │
│                                                          │
│ TOOLS: LitmusChaos | Gremlin | Chaos Monkey | Istio   │
│ START: staging + manual experiments → production       │
│ RULE: always have automated rollback + blast radius    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Netflix runs Chaos Monkey continuously in production — it randomly terminates EC2 instances during business hours (not at night) because "if it can happen at 3 AM during low traffic, it should be able to happen at 3 PM during peak." The key enabler: Netflix is so confident in their resilience that they can absorb random instance termination with no user impact. What is the maturity prerequisite for running chaos experiments in production? Consider: redundancy requirements (N+1 or N+2?), observability requirements (what must you be able to see?), rollback automation requirements (must be automatic, not manual), on-call requirements (someone must be watching). Design a "chaos readiness checklist" for a team considering their first production chaos experiment.

**Q2.** Game Days are scheduled chaos engineering exercises: a team blocks out 4-8 hours, defines a set of chaos experiments (kill the primary database, exhaust the connection pool, saturate the message queue, inject 5-second latency into a critical API), and runs them as a team exercise. Game Days serve multiple purposes: test resilience, train the on-call team in incident response, verify runbooks are up to date, and build team confidence. Design a Game Day for a 3-service order management system (order-service, inventory-service, payment-service, PostgreSQL, Kafka). Define: the 5 chaos experiments you'd run, the expected outcomes (hypotheses), the success criteria, and the runbooks you'd test.
