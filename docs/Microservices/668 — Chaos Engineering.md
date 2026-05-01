---
layout: default
title: "Chaos Engineering"
parent: "Microservices"
nav_order: 668
permalink: /microservices/chaos-engineering/
number: "668"
category: Microservices
difficulty: ★★★
depends_on: "Resilience4j, Circuit Breaker (Microservices), Bulkhead Pattern"
used_by: "Observability & SRE, Zero-Downtime Deployment"
tags: #advanced, #microservices, #reliability, #distributed, #testing
---

# 668 — Chaos Engineering

`#advanced` `#microservices` `#reliability` `#distributed` `#testing`

⚡ TL;DR — **Chaos Engineering** is the discipline of intentionally injecting failures (pod kills, network delays, CPU spikes) into production or pre-production systems to validate that resilience mechanisms (circuit breakers, retries, fallbacks) work under real conditions. "Break it on purpose, learn, fix" — before it breaks unexpectedly in production.

| #668            | Category: Microservices                                         | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Resilience4j, Circuit Breaker (Microservices), Bulkhead Pattern |                 |
| **Used by:**    | Observability & SRE, Zero-Downtime Deployment                   |                 |

---

### 📘 Textbook Definition

**Chaos Engineering** is a discipline in software engineering (coined by Netflix's Chaos Monkey, 2010; formalized by Principled Chaos Engineering — Rosenthal et al.) where practitioners deliberately inject failures into a running system — killed pods, network latency, disk full, CPU saturation, dependency outages — to discover weaknesses before they manifest in uncontrolled production incidents. The scientific method: define a **steady state hypothesis** ("system processes 99% of orders successfully at baseline load"), introduce a **variable** (kill the payment service), observe whether the system maintains steady state (circuit breaker triggers, fallback activates, orders queue for retry), and **learn** from deviations. Tools: **Chaos Monkey** (Netflix — random EC2 instance termination); **Chaos Toolkit** (open-source, declarative experiments); **LitmusChaos** (CNCF, Kubernetes-native); **Gremlin** (commercial SaaS). Chaos engineering differs from load testing (testing capacity) and failure testing (testing specific known failure paths) — it specifically explores unknown failure modes and validates that assumed resilience actually works.

---

### 🟢 Simple Definition (Easy)

Chaos Engineering: deliberately break things in your system on purpose, in a controlled way, to see what happens. Kill a server. Slow down network. Fill up a disk. Does your circuit breaker kick in? Does the system recover automatically? Find the surprises before your customers do — not after a 3am page.

---

### 🔵 Simple Definition (Elaborated)

Netflix's Chaos Monkey (2010): a tool that randomly kills virtual machine instances in Netflix's production environment, every day, during business hours. The goal: force engineering teams to design services resilient enough that a random machine death doesn't affect customers. Teams who haven't built resilience: their service goes down when Chaos Monkey hits. That failure happens during business hours with engineers awake — not at 3am during Black Friday. The pain motivates resilience investment. The key principle: failures WILL happen; chaos engineering makes them happen predictably so you can prepare.

---

### 🔩 First Principles Explanation

**Steady state hypothesis — the scientific foundation:**

```
CHAOS EXPERIMENT STRUCTURE:

1. DEFINE STEADY STATE:
   Observable metric that represents "system is healthy."
   Example: "95% of HTTP requests to /orders return 200 in < 500ms"
   Measurement: Prometheus query:
     sum(rate(http_server_requests_total{uri="/orders",status="200"}[1m]))
     / sum(rate(http_server_requests_total{uri="/orders"}[1m])) >= 0.95

2. DEFINE HYPOTHESIS:
   "If we kill one instance of payment-service, the system will maintain
    steady state because circuit breakers and fallbacks are in place."

3. INTRODUCE VARIABLE (the chaos):
   Action: delete one payment-service pod in Kubernetes:
     kubectl delete pod payment-service-abc123 -n production
   OR: inject latency: payment-service responds with 5-second delay for 50% of requests
   OR: introduce CPU saturation: 90% CPU on payment-service pod

4. OBSERVE:
   Monitor steady state metric during chaos injection.
   Did success rate stay above 95%? Did latency stay below 500ms?
   Did circuit breaker open? Did fallback activate?
   Did automatic recovery occur within expected time?

5. ROLLBACK:
   Remove chaos injection. Verify system returns to steady state.

6. LEARN:
   If hypothesis FAILED (system didn't maintain steady state):
   → Resilience mechanism missing or not configured correctly
   → Fix: add/tune circuit breaker, improve fallback, add retry with backoff

   If hypothesis PASSED:
   → Confidence increased in this specific failure scenario
   → Document as validated: "payment-service instance loss: resilient"
   → Increase experiment scope (kill 2 instances, longer duration)
```

**Chaos experiment types — the failure injection taxonomy:**

```
INFRASTRUCTURE CHAOS:
  Pod kill          → validates Kubernetes restart policies, circuit breakers
  Node failure      → validates pod redistribution, PVC portability
  Disk full         → validates graceful degradation on logging/storage failures
  CPU saturation    → validates timeout behavior under resource contention
  Memory pressure   → validates OOM handling, GC behavior under memory stress

NETWORK CHAOS:
  Latency injection → adds 200ms to all requests to service X
                      Validates: timeout configurations, user experience under latency
  Packet loss       → 10% of packets dropped to service X
                      Validates: retry mechanisms, TCP keepalive settings
  Network partition → service A cannot reach service B
                      Validates: circuit breaker open behavior, fallback activation
  Bandwidth limit   → throttle network to 1Mbps between services
                      Validates: behavior under I/O bound network bottleneck

APPLICATION CHAOS:
  Exception injection → service returns 500 for X% of requests
                        Validates: circuit breaker threshold, retry exhaustion handling
  Time manipulation → system clock skew between services
                       Validates: token expiry handling, cache TTL behavior
  Response corruption → service returns malformed JSON for X% of responses
                         Validates: deserialization error handling, fallbacks
  Dependency blackout → cut access to database / message broker
                         Validates: service behavior without primary data store

STATE CHAOS:
  Data corruption   → modify values in database to invalid states
                       Validates: data validation, error handling for corrupted data
  Cache invalidation → flush Redis cache unexpectedly
                        Validates: cache-miss fallback, DB load spike handling
```

**LitmusChaos — Kubernetes-native chaos experiment:**

```yaml
# LitmusChaos: kill one payment-service pod every 60 seconds for 5 minutes
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: payment-service-pod-kill
  namespace: production
spec:
  appinfo:
    appns: production
    applabel: "app=payment-service"
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "300" # 5 minutes of chaos
            - name: CHAOS_INTERVAL
              value: "60" # kill a pod every 60 seconds
            - name: PODS_AFFECTED_PERC
              value: "50" # kill 50% of pods (1 of 2 replicas)
            - name: FORCE
              value: "false" # graceful pod termination (not SIGKILL)
        probe:
          # Define the steady state check as part of the experiment:
          - name: "check-order-api-health"
            type: "httpProbe"
            mode: "Continuous"
            runProperties:
              probeTimeout: 2
              interval: 5
              attempt: 50
            httpProbe/inputs:
              url: "http://order-service.production.svc/health/readiness"
              insecureSkipTLS: false
              responseTimeout: 2000
              method:
                get:
                  criteria: "=="
                  responseCode: "200"
        # Experiment fails if probe fails (steady state violated)
```

---

### ❓ Why Does This Exist (Why Before What)

Distributed systems fail in unexpected ways. You implement a circuit breaker and THINK it will protect you from payment service outages. But: did you actually test it under production load? Is the threshold configured correctly? Does it open fast enough to prevent cascade? Chaos engineering is the empirical validation that assumed resilience is actual resilience. Without it, you discover failures at the worst possible time (high traffic events, weekends).

---

### 🧠 Mental Model / Analogy

> Chaos engineering is like fire drills for software systems. You know fires happen — you don't wait for one to discover that the fire exit is blocked and nobody knows the evacuation procedure. You schedule fire drills: simulate the fire in a controlled way, practice the response, find that the alarm doesn't work in the server room, and fix it before the real fire. Chaos engineering: schedule the "fire" (pod kill, network partition) in a controlled way, practice the automated response (circuit breaker, failover), find that the fallback throws a NullPointerException, and fix it before Black Friday.

---

### ⚙️ How It Works (Mechanism)

**Chaos Toolkit — declarative experiment definition:**

```json
// chaos-experiment.json — experiment to validate circuit breaker:
{
  "version": "1.0.0",
  "title": "Payment service pod kill: circuit breaker activates within 10 seconds",
  "description": "Kill payment-service pod and verify orders continue to succeed via fallback",
  "steady-state-hypothesis": {
    "title": "Order API returns 200 for 95% of requests",
    "probes": [
      {
        "type": "probe",
        "name": "order-api-health",
        "tolerance": true,
        "provider": {
          "type": "http",
          "url": "http://order-service/actuator/health",
          "expected_status": 200
        }
      }
    ]
  },
  "method": [
    {
      "type": "action",
      "name": "kill-payment-service-pod",
      "provider": {
        "type": "process",
        "path": "kubectl",
        "arguments": "delete pod -l app=payment-service -n production --grace-period=0"
      },
      "pauses": { "after": 30 } // wait 30 seconds after killing pod
    }
  ],
  "rollbacks": [
    {
      "type": "action",
      "name": "ensure-payment-service-running",
      "provider": {
        "type": "process",
        "path": "kubectl",
        "arguments": "rollout restart deployment/payment-service -n production"
      }
    }
  ]
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Resilience4j / Circuit Breaker / Bulkhead
(resilience mechanisms in place)
        │
        ▼
Chaos Engineering  ◄──── (you are here)
(validate that resilience mechanisms actually work)
        │
        ├── Observability & SRE → metrics used to measure steady state
        └── Zero-Downtime Deployment → chaos validates deployment resilience
```

---

### 💻 Code Example

**Verify circuit breaker opens during chaos — Spring Boot integration test:**

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CircuitBreakerChaosTest {

    @MockBean PaymentServiceClient paymentServiceClient;
    @Autowired TestRestTemplate restTemplate;

    @Test
    void circuitBreakerOpensAfterConsecutiveFailures() {
        // Simulate payment service failing (chaos injection via mock):
        when(paymentServiceClient.processPayment(any()))
            .thenThrow(new PaymentServiceException("Service unavailable"));

        // Send 10 requests → circuit breaker should open after threshold (5 failures):
        for (int i = 0; i < 10; i++) {
            ResponseEntity<OrderResponse> response = restTemplate.postForEntity(
                "/api/orders", new CreateOrderRequest("prod-1", "cust-1", 1), OrderResponse.class
            );
            // After circuit opens: should return 200 with FALLBACK response (not 500):
            if (i >= 5) {
                assertThat(response.getStatusCodeValue()).isEqualTo(200);
                assertThat(response.getBody().getStatus()).isEqualTo("PENDING_PAYMENT");
                // Fallback: order created in PENDING state, payment retried async
            }
        }

        // Verify circuit breaker state:
        CircuitBreaker cb = circuitBreakerRegistry.circuitBreaker("paymentService");
        assertThat(cb.getState()).isEqualTo(CircuitBreaker.State.OPEN);

        // After wait period: circuit moves to HALF-OPEN and attempts recovery:
        Thread.sleep(60_000);  // wait for waitDurationInOpenState
        assertThat(cb.getState()).isEqualTo(CircuitBreaker.State.HALF_OPEN);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chaos engineering is only for Netflix-scale systems                     | Chaos engineering principles scale to any distributed system. Even a 3-service system benefits from validating that circuit breakers open correctly and Kubernetes restarts broken pods. The tooling scales: LitmusChaos works on a single-node Kubernetes cluster                            |
| Chaos engineering should only run in staging, never production          | Netflix, Amazon, and Google run chaos experiments in production with appropriate safeguards. Staging may not accurately replicate production load patterns and state. The goal is always production resilience — staging experiments build confidence but don't replace production validation |
| Chaos engineering breaks things randomly                                | Principled chaos engineering is structured and scientific: define steady state, form hypothesis, inject specific controlled failures, observe, learn. Random chaos (Chaos Monkey) is one tool — but the discipline includes targeted, hypothesis-driven experiments                           |
| If all unit and integration tests pass, chaos engineering adds no value | Unit/integration tests verify correctness under normal conditions. Chaos engineering validates resilience under failure conditions — a completely orthogonal concern. A service can have 100% test coverage and still fall over when its database is 1 second slow                            |

---

### 🔥 Pitfalls in Production

**Running chaos experiments during business hours with no blast radius limit:**

```
SCENARIO:
  Team reads "Netflix runs Chaos Monkey in production during business hours."
  New team: no chaos engineering experience.
  Runs experiment: kill 50% of order-service pods.
  Forgot to verify: circuit breakers configured? Load balancer health checks?

  Result: order-service falls below minimum replicas for horizontal scaling trigger.
  New pods spinning up: 90 seconds startup time.
  Circuit breakers NOT configured — other services keep calling dead pods.
  Thread pool exhaustion cascade: 5 services affected.
  30% error rate in production for 3 minutes during morning peak.
  Incident declared. Post-mortem: chaos experiment caused customer-visible outage.

LESSON: START SMALL — chaos engineering maturity model:

  LEVEL 1 (start here): Run experiments in DEV/STAGING ONLY
    → Validate experiment mechanics and rollback procedures
    → Measure observability: can you see the steady state metric?

  LEVEL 2: Production during OFF-PEAK with human operator on standby
    → Small blast radius: one pod, short duration (60 seconds)
    → Rollback plan ready: kubectl apply -f payment-service.yaml
    → Manual abort if steady state violated beyond threshold

  LEVEL 3: Production during BUSINESS HOURS with automation
    → Automated steady state monitoring with automatic rollback
    → Pre-approved experiment library (chaos catalogue)
    → SRE team notified of experiment start/end
    → Netflix Chaos Monkey level: only after Levels 1-2 proven

BLAST RADIUS CONTROLS:
  1. PODS_AFFECTED_PERC: 25% (kill only 1 of 4 replicas)
  2. Duration: 60-120 seconds maximum for initial experiments
  3. Steady state abort threshold: if error rate > 1% → auto-rollback
  4. Time window: avoid experiments during: deployments, on-call transitions, peak load
```

---

### 🔗 Related Keywords

- `Circuit Breaker (Microservices)` — primary mechanism chaos engineering validates
- `Resilience4j` — the Java resilience library whose configuration chaos experiments test
- `Bulkhead Pattern` — isolation mechanism validated by chaos experiments
- `Observability & SRE` — metrics and alerting provide the steady state baseline for experiments

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PRINCIPLE    │ Break it on purpose, learn, fix           │
│ HYPOTHESIS   │ "If X fails, system maintains steady state"│
│ STEADY STATE │ Measurable metric: success rate, latency  │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ LitmusChaos (K8s), Chaos Toolkit, Gremlin │
│ FAILURE TYPES│ Pod kill, latency, partition, CPU, disk   │
├──────────────┼───────────────────────────────────────────┤
│ START SMALL  │ Dev/staging → off-peak prod → business hrs│
│ BLAST RADIUS │ 25% pods, 60 seconds, auto-rollback       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You want to run a chaos experiment to validate your Resilience4j circuit breaker for the `PaymentService` → `StripeAPI` dependency. Define the complete experiment: (a) steady state hypothesis with measurable metric, (b) exact failure to inject and how (LitmusChaos or manual), (c) expected system behaviour if resilience is working correctly, (d) expected system behaviour if resilience is misconfigured, (e) rollback procedure, (f) success/failure criteria. Then describe what "tuning" would be needed if the experiment shows the circuit breaker opens but orders are still failing (fallback not working).

**Q2.** Netflix's Chaos Monkey originally only terminated EC2 instances — a relatively "clean" failure (service just stops responding). Design a more sophisticated "grey failure" chaos experiment for a Kubernetes-based microservices system. Grey failures are partial failures that don't cause complete outages but degrade performance unpredictably: a service that responds correctly 95% of the time but with 10x normal latency. Describe: how to inject this failure in Kubernetes (tc netem, Istio fault injection, or application-level?), which monitoring metrics would reveal this failure type, and which Resilience4j patterns are specifically designed to detect and handle grey failures.
