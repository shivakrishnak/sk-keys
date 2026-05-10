---
layout: default
title: "Ambassador Pattern"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /design-patterns/ambassador-pattern/
id: DPT-059
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - containers
  - microservices
  - deep-dive
  - architecture
  - advanced
status: complete
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-059 - Ambassador Pattern

⚡ TL;DR - The Ambassador Pattern places a helper proxy beside the main service to handle all outbound network calls, providing retry, circuit breaking, service discovery, and auth transparently.

| DPT-059 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Sidecar Pattern, Proxy Pattern, Cross-Cutting Concerns, Containers, Microservices | |
| **Used by:** | Service Mesh, Kubernetes, API Gateway, Envoy Proxy | |
| **Related:** | Sidecar Pattern, Proxy Pattern, Adapter Pattern, Decorator Pattern, Service Mesh | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java microservice needs to call five downstream services. Each call requires: retry with exponential backoff, circuit breaking when the downstream is degraded, authentication header injection, connection pooling, metrics collection per-endpoint, and distributed trace propagation. The application team writes all of this into their service code. A Node.js service in the same fleet repeats the same logic in JavaScript. A Python service repeats it again. Three language-specific implementations of identical network resilience logic now exist in production.

**THE BREAKING POINT:**
When the retry policy must be updated (new RTO requirement), every team must update their own implementation. One team ships the change in week 1. Another team ships in week 4. A third team misses the requirement entirely. For six weeks, outbound calls behave differently across the fleet - some services retry 3 times, others 10, some never. Production SLAs are measured inconsistently.

**THE INVENTION MOMENT:**
The Ambassador Pattern was formalised to solve exactly this. Extract all outbound network intelligence into a co-located proxy - the ambassador - that the application delegates all outbound calls to. The application calls `localhost:8080`. The ambassador handles the rest. The application team writes zero network resilience code; the platform team owns the ambassador.

**EVOLUTION:**
Ambassador Pattern emerged alongside the Sidecar Pattern in the
container era (2015-2017) as a specialisation: while Sidecar is
generic, Ambassador specifically handles outbound service
communication. Netflix's client-side load balancing (Ribbon,
2013) was a pre-container Ambassador variant -- a library
embedded in the client that handled discovery and load balancing.
Service meshes (Istio, Linkerd) subsumed Ambassador into Envoy
proxy, which handles both inbound (Gateway) and outbound
(Ambassador) concerns. Dapr's service invocation component
is a managed Ambassador for cross-service calls without
service discovery code in the application.

---

### 📘 Textbook Definition

The **Ambassador Pattern** is a structural deployment pattern in which a helper service (the ambassador) is deployed alongside the main application in the same container group (e.g., a Kubernetes Pod). The ambassador acts as a transparent proxy for all outbound calls made by the main application. It intercepts outbound network traffic and applies cross-cutting network concerns: authentication, retry logic, circuit breaking, service discovery, connection pooling, protocol translation, and observability. The ambassador is a specialised form of the Sidecar Pattern, distinguished by its focus on **outbound** traffic management.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A co-located proxy handles all your outbound network calls so your application code focuses on business logic, not resilience plumbing.

**One analogy:**
> A diplomat never travels to foreign nations alone - they bring an ambassador who handles protocol, translation, security clearances, and communication formalities. The diplomat focuses on negotiating; the ambassador handles the mechanics of international communication. In software, the main service is the diplomat; the ambassador proxy handles the mechanics of all outbound calls.

**One insight:**
The Ambassador Pattern converts per-service resilience logic into a platform-level infrastructure concern. Every service in the fleet gets identical retry policies, circuit breakers, and observability for outbound calls - not because every team implemented them, but because the platform team deployed an ambassador.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The ambassador handles **outbound** traffic only - the main application's calls going out to other services or external APIs.
2. The ambassador is transparent to the application - the application calls a local address (e.g., `localhost:8080`), unaware that an ambassador sits in the middle.
3. The ambassador is co-located - deployed in the same Pod/host as the main service, sharing the same network namespace.
4. The ambassador is operationally owned by a different team than the application - typically the platform team.

**DERIVED DESIGN:**
From invariant 2: the ambassador must bind to a well-known local address that the application is configured to use as its "base URL" for all outbound calls. The application needs no knowledge that a proxy sits between it and the downstream.

From invariant 3: network round-trip to the ambassador is essentially zero-cost (loopback). The ambassador can add milliseconds of processing (retry logic, connection management) without adding network latency.

From invariant 4: resiliency policies (retry count, backoff curve, circuit breaker threshold) are deployed as ambassador configuration, not application configuration. Changing policy = updating the ambassador config across the fleet, not touching application code.

**THE TRADE-OFFS:**
**Gain:** Uniform outbound resilience across polyglot services; policies managed centrally; application teams free from network plumbing; retry/circuit-break behaviour testable at ambassador level.
**Cost:** Additional process per Pod (memory and CPU overhead); outbound traffic debugging requires understanding the ambassador layer; ambassador misconfiguration affects all outbound calls from that Pod; not appropriate for intra-process or in-memory calls.

---

### 🧪 Thought Experiment

**SETUP:**
A fleet of 30 microservices (Java, Go, Python) calls a shared Payment API that occasionally returns 503 errors under load. The team needs uniform retry-with-jitter + circuit breaker across all 30 services.

**WHAT HAPPENS WITHOUT Ambassador:**
Java team adds Resilience4j. Go team adds a custom retry loop. Python team uses the `requests` library's `Retry` adapter. Each implementation uses different backoff parameters, different circuit breaker thresholds. When the Payment API degrades, the Java services circuit-break at 5 failures; the Python services retry indefinitely, amplifying load on the already degraded upstream. A cascading failure results.

**WHAT HAPPENS WITH Ambassador:**
Platform team deploys an Envoy ambassador as a sidecar to every Pod. All services are configured with `PAYMENT_API_URL=http://localhost:9900`. Envoy: routes to the real Payment API, applies 3 retries with exponential jitter (50ms, 100ms, 200ms), circuit-breaks at 10 consecutive failures, resumes after 30 seconds. When the Payment API degrades, all 30 services respond identically - circuit-break together, recover together. No cascading failure.

**THE INSIGHT:**
The Ambassador Pattern makes resilience a property of deployment topology, not application code. The consistency guarantee comes not from governance across 30 teams, but from infrastructure uniformity.

---

### 🧠 Mental Model / Analogy

> Think of a large corporation's travel desk. Every employee (main service) who needs to travel abroad (make an outbound call) goes through the travel desk (ambassador). The travel desk handles visas (authentication), books the safest routes (service discovery), arranges backup plans if the flight is cancelled (retry), has a policy to cancel non-critical travel during emergencies (circuit breaker), and reports all travel activity (observability). The employee focuses on the purpose of the trip, not the logistics.

- "Employee" → main application service
- "Travel desk" → ambassador proxy
- "Visa" → outbound authentication (auth headers, mTLS certificates)
- "Backup plans" → retry with exponential backoff
- "Cancel travel during emergencies" → circuit breaker
- "Travel activity report" → outbound request metrics and traces

Where this analogy breaks down: a travel desk serves many employees. An Ambassador serves one service - it is co-located per service, not shared across services. This per-service deployment is what enables service-specific outbound policy configuration.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An ambassador is a small helper program running next to your service. When your service wants to call another service, it talks to the ambassador instead. The ambassador does the hard work - retrying if the call fails, stopping calls if the other service is broken, adding the right security credentials - and returns the result to your service.

**Level 2 - How to use it (junior developer):**
Configure your application's outbound HTTP client to point to `localhost:<ambassador-port>` instead of the real downstream URL. The ambassador receives the request, applies resilience logic (retry, circuit break, timeout), forwards to the real downstream, and returns the response. In Kubernetes, add an Envoy sidecar configured as an outbound proxy. Set the environment variable `PAYMENT_SERVICE_URL=http://localhost:9900` in your application.

**Level 3 - How it works (mid-level engineer):**
The ambassador binds to one or more local ports, each mapped to a specific upstream (e.g., port 9900 → Payment API, port 9901 → Inventory API). When the application POSTs to `localhost:9900/payments`, the ambassador receives it, checks the circuit breaker state (CLOSED/OPEN/HALF-OPEN), applies connection pooling, injects auth headers (e.g., a short-lived JWT fetched from a secrets sidecar), forwards the request with timeout enforcement, and on 503/429 responses applies retry with exponential backoff + jitter. All request/response metrics (latency, status code, retry count) are exported to Prometheus via the ambassador's `/metrics` endpoint.

**Level 4 - Why it was designed this way (senior/staff):**
The Ambassador Pattern solves the **polyglot resilience ownership problem** at scale. In a service mesh like Istio, Envoy sidecars handle both inbound (Sidecar Pattern role) and outbound (Ambassador Pattern role) traffic. The distinction matters organisationally: the Ambassador role is about giving the platform team control over how service A reaches service B - independently of what language A is written in or what SDK team A uses. At scale, this enables "resilience as a policy" - operators publish retry and circuit-breaker policies as `VirtualService` / `DestinationRule` CRDs in Kubernetes, and Envoy enforces them fleet-wide without touching application deployments. The Ambassador Pattern is also the foundation for protocol bridging (HTTP/1.1 → gRPC translation) and multi-cloud routing.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  KUBERNETES POD - AMBASSADOR PATTERN                   │
│                                                        │
│  ┌──────────────┐    localhost    ┌──────────────────┐ │
│  │  Main App    │ ─────────────→  │  Ambassador      │ │
│  │  (port 8080) │                 │  Proxy (Envoy)   │ │
│  │              │                 │                  │ │
│  │  calls:      │                 │  Per upstream:   │ │
│  │  localhost   │                 │  ✓ Auth inject   │ │
│  │  :9900       │                 │  ✓ Retry logic   │ │
│  │              │                 │  ✓ Circuit break │ │
│  └──────────────┘                 │  ✓ Timeout       │ │
│                                   │  ✓ Metrics       │ │
│                                   └──────┬───────────┘ │
└──────────────────────────────────────────┼─────────────┘
                                           │ (real network)
                                           ▼
                              ┌────────────────────────┐
                              │  Downstream Service    │
                              │  (Payment API, etc.)   │
                              └────────────────────────┘
```

**Request Path:**
1. App calls `POST http://localhost:9900/payments`
2. Envoy ambassador receives on port 9900
3. Checks circuit breaker state (CLOSED → proceed)
4. Injects `Authorization: Bearer <token>` header
5. Forwards to real Payment API endpoint
6. On 503: waits 50ms, retries (up to 3 times)
7. On success: returns response to app
8. Emits metrics: `upstream_requests_total{service="payment",code="200"}`

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
App: POST /payments
  → App calls localhost:9900
  → Ambassador receives request
    [← YOU ARE HERE: outbound proxy intercepts]
  → Ambassador: check circuit breaker → CLOSED
  → Ambassador: inject auth header from secret store
  → Ambassador: set timeout = 2000ms
  → Ambassador: forward to payment-api:443
  → Payment API: processes, returns 200
  → Ambassador: record success (circuit stats)
  → Ambassador: return 200 to App
App: process payment response
```

**FAILURE PATH:**
```
Payment API returns 503
  → Ambassador: attempt 1 failed (503)
  → Ambassador: wait 50ms + jitter, retry
  → Ambassador: attempt 2 failed (503)
  → Ambassador: wait 100ms + jitter, retry
  → Ambassador: attempt 3 failed (503)
  → Circuit breaker: record 3 failures
  → Ambassador: return 503 to App
  → App: activates fallback (e.g., queue payment)
  [If failures persist: circuit → OPEN]
  → Future calls: ambassador returns 503 immediately
    (no forwarding - fail fast during OPEN state)
```

**WHAT CHANGES AT SCALE:**
At 10 services, ambassador configuration is manageable per-service. At 100 services, a service mesh control plane (Istiod) distributes ambassador configuration uniformly via `DestinationRule` CRDs. At 1,000 services, per-upstream outbound routing rules (retry budgets, timeout policies) become a security and reliability governance requirement - enforced by the ambassador fleet, audited centrally.

---

### 💻 Code Example

**Example 1 - Kubernetes Pod with Envoy outbound ambassador:**

```yaml
# Pod with Envoy ambassador for outbound resilience
apiVersion: v1
kind: Pod
metadata:
  name: order-service
spec:
  containers:
  - name: order-service         # Main container
    image: myorg/order-service:1.0
    env:
    # App calls ambassador, not real upstream
    - name: PAYMENT_API_URL
      value: "http://localhost:9900"

  - name: ambassador            # Ambassador proxy
    image: envoyproxy/envoy:v1.28.0
    ports:
    - containerPort: 9900       # Outbound proxy port
    volumeMounts:
    - name: envoy-config
      mountPath: /etc/envoy/envoy.yaml
      subPath: envoy.yaml

  volumes:
  - name: envoy-config
    configMap:
      name: envoy-ambassador-config
```

**Example 2 - Envoy ambassador configuration (retry + circuit break):**

```yaml
# envoy-ambassador-config ConfigMap
static_resources:
  clusters:
  - name: payment_api
    connect_timeout: 1s
    type: STRICT_DNS
    load_assignment:
      cluster_name: payment_api
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: payment-api.svc.cluster.local
                port_value: 443
    # Circuit breaker config
    circuit_breakers:
      thresholds:
      - max_retries: 3
        max_pending_requests: 100
  listeners:
  - name: outbound_listener
    address:
      socket_address: { address: 0.0.0.0, port_value: 9900 }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          route_config:
            virtual_hosts:
            - name: payment
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route:
                  cluster: payment_api
                  retry_policy:
                    retry_on: "5xx,reset"
                    num_retries: 3
                    per_try_timeout: 2s
                    retry_back_off:
                      base_interval: 0.05s
                      max_interval: 1s
```

**Example 3 - Application code (zero resilience logic):**

```java
// BAD: resilience logic in application code
@Service
public class PaymentServiceClient {
    // Retry logic duplicated in every client, every language
    public PaymentResponse charge(ChargeRequest req) {
        int attempts = 0;
        while (attempts < 3) {
            try {
                return httpClient.post(
                    "https://payment-api:443/charge", req);
            } catch (ServiceUnavailableException e) {
                attempts++;
                Thread.sleep(50L * attempts);
            }
        }
        throw new PaymentException("max retries exceeded");
    }
}

// GOOD: application code delegates to ambassador
@Service
public class PaymentServiceClient {
    // Retry, circuit break, timeout: ambassador's responsibility
    // App just calls localhost - ambassador does the rest
    @Value("${PAYMENT_API_URL}")  // = http://localhost:9900
    private String paymentApiUrl;

    public PaymentResponse charge(ChargeRequest req) {
        return httpClient.post(
            paymentApiUrl + "/charge", req);
        // No retry logic. No circuit breaker.
        // Ambassador proxy handles all of that.
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Scope | Ownership | Language Agnostic | Upgrade Independence |
|---|---|---|---|---|
| **Ambassador** | Outbound only | Platform team | Yes | Yes |
| Sidecar | Inbound + Outbound | Platform team | Yes | Yes |
| In-process SDK (Resilience4j) | Inbound + Outbound | App team | No (per-language) | No |
| Service Mesh (full) | Network-wide policy | Platform team | Yes | Full |
| API Gateway | Inbound only | Platform/API team | Yes | Yes |

How to choose: use Ambassador when you need uniform outbound resilience across polyglot services without code changes. Use in-process SDK when you need fine-grained application-level control (business exception handling). Use Service Mesh when you need both inbound and outbound policy management fleet-wide.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Ambassador and Sidecar are the same pattern | Sidecar is the general pattern; Ambassador is a specialised role focussed on outbound calls. All Ambassadors are Sidecars; not all Sidecars are Ambassadors |
| Ambassador handles inbound traffic | Ambassador is specifically an outbound proxy. Inbound traffic handling is the general Sidecar role. In Istio, the Envoy sidecar plays both roles, but conceptually they are distinct |
| Ambassador eliminates all need for application error handling | Ambassador handles network-level transient failures (503, timeout). Application-level errors (invalid payment, insufficient funds) are business errors that must still be handled by the application |
| Ambassador is only for Kubernetes | The pattern applies anywhere a co-located proxy can be deployed - VMs, Docker Compose, bare metal. Kubernetes makes it operationally convenient via Pods |

---

### 🚨 Failure Modes & Diagnosis

**1. Ambassador Configuration Mismatch - Wrong Upstream**

**Symptom:** Application reports connection refused or 503 for all calls to a downstream, despite the downstream being healthy.

**Root Cause:** Ambassador configured with the wrong upstream hostname or port. App calls `localhost:9900` but ambassador routes 9900 to a decommissioned endpoint.

**Diagnostic:**
```bash
# Check ambassador routing config:
kubectl exec order-service-xxx \
  -c ambassador -- \
  curl -s localhost:9901/config_dump \
  | grep -A5 "payment_api"

# Verify the cluster address resolves:
kubectl exec order-service-xxx \
  -c ambassador -- \
  nslookup payment-api.svc.cluster.local
```

**Fix (BAD):** Restart the Pod hoping it fixes itself.
**Fix (GOOD):** Correct `envoy.yaml` cluster address, update the ConfigMap, restart the ambassador container only.

**Prevention:** Validate Envoy config via `envoy --mode validate -c envoy.yaml` in CI before deploying ConfigMap changes.

---

**2. Retry Storm - Amplified Load on Degraded Upstream**

**Symptom:** Ambassador retry metrics show spike; downstream receives 3× expected request volume during degradation; cascading failure accelerates instead of receding.

**Root Cause:** Too-aggressive retry policy without circuit breaker or retry budget. Every failed request retries 3 times → 3× load on an already struggling service.

**Diagnostic:**
```bash
# Check retry attempts vs. total requests:
kubectl exec order-service-xxx \
  -c ambassador -- \
  curl -s localhost:9901/stats \
  | grep "upstream_rq_retry\|upstream_rq_total"
# upstream_rq_retry >> upstream_rq_total = retry storm
```

**Fix:** Add circuit breaker threshold to trip after N consecutive failures. Set a retry budget (max retry:total ratio = 0.1). Add jitter to backoff to spread retry load.

**Prevention:** Test retry behaviour under load using chaos injection (Chaos Mesh). Set `max_retries` in circuit breaker config proportional to connection pool size.

---

**3. Ambassador Startup Race - App Calls Before Ambassador Ready**

**Symptom:** Application fails on startup with connection refused; errors reference `localhost:9900`. No traffic reaches downstream services.

**Root Cause:** Application container starts before ambassador is bound and listening on local ports.

**Diagnostic:**
```bash
# Check container start timestamps:
kubectl describe pod order-service-xxx \
  | grep -A5 "ambassador\|order-service" \
  | grep "Started\|Ready"
# If app Started before ambassador Ready → startup race
```

**Fix:** Use Kubernetes native sidecar support (1.29+) with `restartPolicy: Always` on the ambassador init container, ensuring it starts before the main container. Alternatively: add a readiness probe to the ambassador and a `postStart` hook on the main container.

**Prevention:** Use `kubectl wait --for=condition=Ready` or health-check scripts in the main container's `command` to delay startup until ambassador port responds.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Sidecar Pattern` - the Ambassador is a specialised Sidecar; understanding the general Sidecar Pattern (co-location, shared lifecycle, shared network namespace) is required to understand the Ambassador's deployment model
- `Proxy Pattern` - the Ambassador is the deployment-level realisation of the Proxy design pattern; understanding the Proxy's intent (transparent interception) explains the Ambassador's transparent interception of outbound calls

**Builds On This (learn these next):**
- `Service Mesh` - a fleet of Sidecars/Ambassadors managed by a centralised control plane; Istio's Envoy sidecar plays both the Ambassador and Sidecar roles, managed by Istiod
- `Circuit Breaker Pattern` - one of the primary resilience capabilities the Ambassador implements; understanding circuit breaker states (CLOSED/OPEN/HALF-OPEN) explains how the ambassador protects downstream services

**Alternatives / Comparisons:**
- `Sidecar Pattern` - the general case; Ambassador is a narrower specialisation focused on outbound network management
- `API Gateway` - handles inbound traffic management at the edge; Ambassador handles outbound traffic management per-service; they complement each other but address different directions of traffic

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A co-located proxy handling all outbound  │
│              │ calls from the main service               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Repeated per-language outbound resilience │
│ SOLVES       │ logic: retry, circuit break, auth,        │
│              │ service discovery in every service        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ App calls localhost; ambassador handles   │
│              │ all the network hard work transparently   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Polyglot fleet needing uniform outbound   │
│              │ resilience without per-service SDK work   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-language teams where in-process   │
│              │ SDK (Resilience4j) gives more control     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Uniform outbound resilience + platform    │
│              │ ownership vs. additional Pod resource     │
│              │ overhead and config complexity            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Let the ambassador handle the journey;  │
│              │  you focus on the destination."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Service Mesh → Envoy → Istio →            │
│              │ Circuit Breaker → Retry Pattern           │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When multiple services need to communicate with the same
external dependency using the same protocol, retry, discovery,
and observability logic, centralise that outbound communication
logic in a dedicated ambassador rather than replicating it
in every service.

**Where else this pattern appears:**
- **Outbound proxy (corporate proxy servers):** All corporate
  internet traffic routes through a proxy that enforces
  security policy, logs requests, and applies rate limits --
  an ambassador for all outbound internet communication.
- **Database connection proxy (PgBouncer, ProxySQL):** Database
  traffic from all application instances passes through a
  connection pool proxy that manages connections -- an
  ambassador for database communication.
- **API Gateway outbound calls:** An API Gateway that calls
  multiple backend services acts as an ambassador for all
  external callers -- request routing, retry, and circuit
  breaking are centralised.

---

### 💡 The Surprising Truth

Netflix's Ribbon library -- which performed client-side load
balancing and was one of the foundational microservices libraries
(used in millions of production instances from 2013-2020) --
was put into maintenance mode and replaced by Spring Cloud
LoadBalancer because it was incompatible with reactive
programming models. Ribbon used thread-local state and blocking
I/O, which prevented use with WebFlux and reactive HTTP clients.
This is the Ambassador pattern's fundamental tension: the
ambassador must be written with the same concurrency model as
the service it serves. A blocking Ambassador in a non-blocking
service is as harmful as no ambassador at all.
---

### 🧠 Think About This Before We Continue

**Q1.** Your fleet has 50 microservices using an Ambassador (Envoy) for outbound calls. A critical security vulnerability is discovered in the Envoy version deployed. Compare two remediation approaches: (A) update the Ambassador container image in every Pod via a rolling restart; (B) update every application's in-process resilience SDK dependency and rebuild/redeploy all 50 services. Evaluate across: blast radius, time-to-remediation, risk of regression, and team coordination overhead.

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** An Ambassador proxy applies retry-with-backoff for all `5xx` responses from a downstream. The downstream is a payment service. A payment request fails with `503` due to a database timeout - the payment was committed to the DB one millisecond before the timeout. The Ambassador retries. Analyse the correctness implications: what invariant must the downstream payment service guarantee for the Ambassador's retry to be safe, and what happens if that invariant is violated?

**Q3.** The Ambassador Pattern and the API Gateway Pattern both act as network intermediaries. Describe three fundamental architectural differences between them - in terms of deployment topology, traffic direction, scope of concern, and who owns the component - and explain under what conditions you would use both simultaneously in the same system.



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A Python service and a Java service
both call the same external inventory API, each implementing
their own retry, timeout, and circuit-breaker logic. A team
proposes an Ambassador sidecar that centralises this logic
for both services. Describe: (1) the network path change when
the Ambassador is introduced, (2) the failure modes introduced
by adding the Ambassador as an additional hop, (3) the conditions
under which this trade-off is justified.

*Hint: The Failure Modes section and the Sidecar comparison
both address the additional hop latency. The justification
threshold is: when the ambassador eliminates more bugs than
the additional operational complexity it introduces.*
