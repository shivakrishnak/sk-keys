---
layout: default
title: "Smoke Test"
parent: "Testing"
nav_order: 1135
permalink: /testing/smoke-test/
number: "1135"
category: Testing
difficulty: ★☆☆
depends_on: E2E Test, Integration Test, CI-CD
used_by: Deployment Verification, CI-CD, Blue-Green Deployments
related: Sanity Test, E2E Test, Health Check, Canary Deployment
tags:
  - testing
  - deployment
  - ci-cd
  - fundamentals
---

# 1135 — Smoke Test

⚡ TL;DR — A smoke test is a fast, shallow check run immediately after deployment to verify the application starts, connects to its dependencies, and handles the most basic requests — before running the full test suite or routing production traffic.

| #1135 | Category: Testing | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | E2E Test, Integration Test, CI-CD | |
| **Used by:** | Deployment Verification, CI-CD, Blue-Green Deployments | |
| **Related:** | Sanity Test, E2E Test, Health Check, Canary Deployment | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You deploy a new version. The application starts — JVM launches, port binds — but the database password environment variable wasn't injected in the new deployment config. The application silently fails on every user request (connection pool throws on first query). No smoke test: 100% of user traffic hits the broken version for 5 minutes until someone notices the error rate spike.

THE BREAKING POINT:
You need a fast sanity check between "the process started" and "it's handling real traffic." A smoke test verifies: database connected, cache connected, critical endpoints respond, authentication works. If any smoke test fails, deployment is rolled back before any user traffic is routed.

THE INVENTION MOMENT:
The term comes from hardware testing: power on a new circuit board and check it doesn't "smoke" (catch fire). The electrical engineer doesn't run full diagnostics — just "did it survive powering on?" Applied to software deployment: does the application survive starting up and handling a basic request?

### 📘 Textbook Definition

A **smoke test** (also called **build verification test** or **BVT**) is a minimal set of automated tests executed immediately after a deployment to verify that the most critical functionality of the system is operational. Smoke tests are intentionally shallow — they do not test edge cases or full user flows. Their goal is to detect catastrophic failures (misconfigured environment, broken startup, unavailable database, missing configuration) within seconds or minutes, before full test suites run or production traffic is routed.

A **sanity test** is similar but typically verifies a specific area after a focused change, not the whole system.

### ⏱️ Understand It in 30 Seconds

**One line:**
Smoke test = "is it alive and not on fire?" — run right after deploy, before routing traffic.

**One analogy:**
> Before flying a commercial aircraft after maintenance, pilots do a pre-flight check: control surfaces move, instruments power on, fuel is loaded, engines turn over. They don't test every possible flight scenario — just enough to verify the aircraft is safe to take off. Smoke tests are the pre-flight check for software.

**One insight:**
A smoke test's value is in what it checks first and fast. It runs in 30–60 seconds; a full E2E suite might take 30 minutes. Those 30 minutes of broken production exposure are eliminated by the smoke test gate.

### 🔩 First Principles Explanation

WHAT A SMOKE TEST SHOULD CHECK:
```
1. Application starts: returns 200 on GET /health
2. Database connected: a basic query succeeds
3. Cache connected: Redis responds to PING
4. Downstream services reachable: GET /actuator/health/external shows UP
5. Authentication works: a login request succeeds
6. One critical API endpoint works: GET /api/products returns 200 with non-empty body

What smoke tests should NOT check:
- All business logic edge cases
- Full user journeys (use E2E tests)
- Performance (use load tests)
- Error handling edge cases (use unit tests)
```

DEPLOYMENT GATE PATTERN:
```
deploy.sh:
  1. Deploy new version → pod starts
  2. Wait for readinessProbe (Kubernetes) or health check
  3. Run smoke tests against new version
     If FAIL → rollback (kubectl rollout undo)
     If PASS → shift traffic (blue-green switch / canary increment)
  4. Run full regression suite (async, parallel)
```

THE TRADE-OFFS:
Gain: Catches catastrophic failures within 60s of deployment; prevents broken code from reaching users; fast feedback on deployment issues.
Cost: Must be maintained alongside deployment process; too many smoke tests = slow feedback (should be < 2 minutes total); false positives (flaky smoke tests block deployments).

### 🧪 Thought Experiment

SMOKE TEST SAVES PRODUCTION:
```
10:30 AM: New version deployed (feature: new payment provider)
10:30:01: Smoke test: GET /health → 200 ✓
10:30:02: Smoke test: DB ping → success ✓  
10:30:03: Smoke test: POST /api/payments (test card) → 500 ✗

Error: "Payment provider API key not set in environment"
→ Deployment pipeline: FAIL
→ Rollback triggered automatically
→ Old version restored: 10:30:45

User impact: 0 (no traffic was routed to broken version)
Without smoke test: 5 minutes of failed payments before human notices
```

### 🧠 Mental Model / Analogy

> A smoke test is a **tripwire** — it's placed at the entrance to production traffic. If the deployment is broken in the most obvious ways, it trips the wire and the deployment is stopped. It's not comprehensive — it's positioned to catch the 80% of deployment failures that are trivially detectable (service doesn't start, can't connect to DB, missing env vars) in under 60 seconds.

### 📶 Gradual Depth — Four Levels

**Level 1:** A smoke test is a quick check you run right after deploying to make sure your app is basically working — can it connect to the database, does the home page load, does login work.

**Level 2:** In Spring Boot: use `/actuator/health` (includes DB + cache + custom health indicators). In CI/CD: run 3–5 smoke test HTTP calls (via curl or Playwright) after deployment, before traffic switch. In Kubernetes: `readinessProbe` and `livenessProbe` are always-on smoke tests — they run every 10s throughout the pod's lifetime.

**Level 3:** Smoke tests in blue-green deployments: deploy to blue (inactive), run smoke tests, if pass switch ingress to blue. If smoke tests fail, rollback (keep green active) — zero user impact. In canary deployments: deploy to 5% of traffic, run smoke tests on canary + monitor error rates for 5 minutes, if all good increase to 25%, 50%, 100%. Smoke test infrastructure as code: smoke test scripts should be version-controlled alongside deployment scripts.

**Level 4:** Smoke tests should not share state with each other (create own test data, clean up). They should be idempotent: running the same smoke test twice shouldn't leave the system in a different state (use dedicated smoke-test user accounts, not production data). In chaos engineering: smoke tests are the "steady state" definition — before injecting failures, verify the smoke tests pass (system is healthy); after chaos experiment, verify smoke tests still pass (system recovered).

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│         SMOKE TEST IN CI/CD PIPELINE                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Build → Docker Image → Push to Registry                │
│                │                                         │
│                ▼                                         │
│  Deploy to staging/canary (kubectl apply)               │
│                │                                         │
│                ▼                                         │
│  Wait for pod Ready (readinessProbe passes)             │
│                │                                         │
│                ▼                                         │
│  Run smoke tests:                                       │
│    GET /actuator/health → 200 + {"status":"UP"}        │
│    POST /api/auth/login → 200 + token                   │
│    GET /api/products → 200 + [{id, name, price}]        │
│    POST /api/cart/add → 200 (idempotent test item)      │
│         │              │                                │
│       PASS           FAIL                               │
│         │              │                                │
│         ▼              ▼                                │
│  Route traffic      Rollback + alert                    │
│  Run full E2E       kubectl rollout undo                │
│  (async)                                                │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

KUBERNETES BLUE-GREEN WITH SMOKE TESTS:
```bash
# deploy.sh
NEW_VERSION="v1.2.3"
NAMESPACE="production"

# 1. Deploy to inactive (blue) environment
kubectl set image deployment/app-blue app=myapp:$NEW_VERSION

# 2. Wait for all pods ready
kubectl rollout status deployment/app-blue --timeout=120s

# 3. Run smoke tests against blue (not live yet)
SMOKE_URL="http://app-blue-svc.$NAMESPACE.svc.cluster.local"
curl --fail --silent --max-time 10 "$SMOKE_URL/actuator/health" || {
    echo "SMOKE FAILED: health check"
    kubectl rollout undo deployment/app-blue
    exit 1
}

curl --fail --silent --max-time 10 \
  -X POST "$SMOKE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"smoke-test@example.com","password":"smokepass"}' || {
    echo "SMOKE FAILED: authentication"
    kubectl rollout undo deployment/app-blue
    exit 1
}

# 4. All smoke tests passed → switch traffic
kubectl patch service app-svc -p '{"spec":{"selector":{"color":"blue"}}}'
echo "Deployment successful: traffic switched to blue"
```

### 💻 Code Example

```java
// Spring Boot: custom health indicator for smoke test
@Component
class PaymentProviderHealthIndicator implements HealthIndicator {
    private final PaymentGatewayClient client;

    @Override
    public Health health() {
        try {
            boolean reachable = client.ping();  // lightweight ping call
            return reachable
                ? Health.up().withDetail("provider", "stripe").build()
                : Health.down().withDetail("reason", "ping failed").build();
        } catch (Exception e) {
            return Health.down().withException(e).build();
        }
    }
}
```

```bash
# Smoke test script (bash/curl)
set -e
BASE_URL="${APP_URL:-http://localhost:8080}"

echo "Running smoke tests against: $BASE_URL"

# 1. Health check
curl --fail -s "$BASE_URL/actuator/health" | jq -e '.status == "UP"'
echo "✓ Health check passed"

# 2. Basic authentication
TOKEN=$(curl --fail -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"smoke@test.com","password":"smoketest123"}' \
  | jq -r '.token')
[ -n "$TOKEN" ] && echo "✓ Authentication passed"

# 3. Authenticated endpoint
curl --fail -s "$BASE_URL/api/products" \
  -H "Authorization: Bearer $TOKEN" | jq -e 'length > 0'
echo "✓ Products endpoint passed"

echo "All smoke tests passed ✓"
```

### ⚖️ Comparison Table

| Test Type | When Run | Duration | Coverage | Purpose |
|---|---|---|---|---|
| Unit test | Pre-commit / CI | <1s | Logic | Catch code bugs |
| Integration test | CI build | 1–5min | Components | Catch integration bugs |
| **Smoke test** | Post-deploy | 30–60s | Critical paths | Catch deployment failures |
| E2E test | Post-deploy (async) | 5–30min | User journeys | Full confidence |
| Load test | Scheduled | Hours | Performance | Capacity planning |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Smoke tests = comprehensive tests" | Smoke tests are intentionally shallow; they verify "alive and connected," not business logic |
| "Health check endpoint = smoke test" | Health check is part of a smoke test; a smoke test also includes basic API calls |
| "Smoke tests replace regression tests" | They complement; smoke tests are fast gates; regression tests are comprehensive verification |
| "More smoke tests = safer deployment" | More tests = slower deployment gate; keep smoke tests under 2 minutes |

### 🚨 Failure Modes & Diagnosis

**1. Smoke Test Blocks Valid Deployment (False Positive)**

Cause: Smoke test checks a non-critical dependency that's temporarily down; OR smoke test has timing race (pod not fully warmed up).
Fix: Health checks should reflect critical-path dependencies only. Use retries in smoke test: `curl --retry 3 --retry-delay 5`. Use readiness probe correctly: pod isn't marked Ready until startup is complete.

**2. Smoke Test Passes but Production is Broken**

Cause: Smoke test covers happy path; production failure is in an edge case; OR smoke test uses a different code path than production.
Fix: Smoke tests must exercise the same code paths users take. After production incident: add a smoke test for the specific failure scenario.

### 🔗 Related Keywords

- **Prerequisites:** E2E Test, Integration Test, CI-CD
- **Builds on:** Blue-Green Deployment, Canary Deployment, Health Check
- **Alternatives:** Readiness Probe (Kubernetes equivalent for pod lifecycle), Sanity Test (scoped to a specific changed area)

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fast post-deploy check: alive, connected,│
│              │ basic requests succeed                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Gate before traffic → catch deploy bugs  │
│              │ before users do, in under 60 seconds     │
├──────────────┼───────────────────────────────────────────┤
│ CONTENTS     │ /actuator/health + login + 1-2 API calls │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Speed (< 2min) vs depth (not comprehensive│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Does it start, connect, and respond?    │
│              │  If no → rollback before user sees it"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Blue-Green Deploy → Canary → Health Check │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** Kubernetes `livenessProbe` and `readinessProbe` are always-on automated smoke tests. `readinessProbe` failure removes the pod from the Service's endpoint list (stops receiving traffic); `livenessProbe` failure kills the pod and restarts it. A Spring Boot app with `/actuator/health` for both probes has a subtle problem: `actuator/health` includes disk space checks. If disk fills up (logs), the health check returns DOWN → readiness fails → pod removed from traffic. But the application is otherwise functional. Describe the correct configuration of Spring Boot Actuator health groups to have: (a) `readinessProbe` that only checks application-critical dependencies (DB, cache), (b) `livenessProbe` that only checks if the JVM is alive (not deadlocked), and (c) a separate `/actuator/health` endpoint that shows the full health picture for monitoring dashboards.

**Q2.** Netflix's "Production Verification Tests" concept runs a subset of automated E2E tests continuously in production using synthetic transactions (not real user data). Every 5 minutes, a robot places a test order using a dedicated test account, verifies it completes, and cleans up. This is contrasted with a traditional smoke test (run only at deploy time). Explain: (1) what class of bugs production verification tests catch that deploy-time smoke tests miss (bugs introduced by data degradation, third-party service changes, configuration drift over time), (2) the operational requirements for making synthetic transactions safe (idempotent test accounts, automatic cleanup, no financial side effects), and (3) why this approach is complementary to (not a replacement for) deploy-time smoke tests.
