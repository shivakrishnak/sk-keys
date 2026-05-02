---
layout: default
title: "Smoke Test"
parent: "Testing"
nav_order: 1135
permalink: /testing/smoke-test/
number: "1135"
category: Testing
difficulty: ★☆☆
depends_on: "E2E Test, CI-CD Pipeline"
used_by: "Deployment pipelines, health checks, staging validation"
tags: #testing, #smoke-test, #sanity-check, #deployment, #health-check
---

# 1135 — Smoke Test

`#testing` `#smoke-test` `#sanity-check` `#deployment` `#health-check`

⚡ TL;DR — **Smoke tests** are a minimal subset of tests run immediately after deployment to verify that the application's critical functionality is working. Named after hardware testing: power on the circuit board — if smoke appears, something is fundamentally broken, stop immediately. In software: deploy → run smoke tests → if they fail, roll back before the bad deployment causes damage. Fast (seconds to 2 minutes), not comprehensive.

| #1135 | Category: Testing | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | E2E Test, CI-CD Pipeline | |
| **Used by:** | Deployment pipelines, health checks, staging validation | |

---

### 📘 Textbook Definition

**Smoke test** (also: *sanity test*, *build verification test (BVT)*): a shallow, rapid test suite that verifies the most fundamental operations of a system function after a new deployment. Origin: hardware engineering — power on a new circuit board; if it smokes (burns), testing stops immediately. Software equivalent: deploy → run a small set of critical tests → if ANY fail, roll back immediately; if ALL pass, proceed with full test suite or allow traffic. Characteristics: (1) **Fast** — 30 seconds to 2 minutes; (2) **Minimal** — tests only the most critical paths (login, health endpoint, homepage loads); (3) **Binary outcome** — all pass → deployment is "not obviously broken"; any fail → immediate rollback; (4) **Automated** — triggered automatically in the deployment pipeline; (5) **Run against deployed environment** — tests the actual deployed service, not mocked dependencies. Typical smoke tests: `GET /health` returns 200, user can log in, homepage renders, critical API endpoint responds. Smoke tests are NOT comprehensive — they're a first filter to catch catastrophic failures (app fails to start, database connection broken, misconfigured environment variables) before they affect users or before a full test suite wastes time.

---

### 🟢 Simple Definition (Easy)

You deploy a new version of your app. Before letting any users in, run 5 quick tests: "Does the homepage load? Can a user log in? Does the main API respond?" If any of these fail — something is fundamentally broken — roll back immediately. That's a smoke test. It takes 60 seconds and saves you from deploying a broken app to production users.

---

### 🔵 Simple Definition (Elaborated)

Smoke tests answer: **"Is the system basically alive?"** — not "is it 100% correct," but "is it minimally functional?"

**Typical smoke test checklist**:
- `GET /health` → 200 OK (app started successfully)
- `GET /health/db` → 200 OK (database connected)
- `POST /auth/login` with test credentials → 200 OK with token (auth working)
- `GET /` (homepage) → 200 OK (frontend serving)
- Core business API → 200 OK (critical functionality responding)

**Where smoke tests fit in the pipeline**:
```
Code push → Build → Unit tests → Integration tests → Deploy to staging
        → SMOKE TESTS → (pass) → Full E2E tests → Deploy to production
                                  (fail) → ROLLBACK immediately
```

**Why not just run the full test suite?**: Full E2E tests take 20-60 minutes. If the deployment is fundamentally broken (app won't start), you don't want to wait 30 minutes to find out — smoke tests tell you in 60 seconds.

**Distinction from health checks**:
- **Health check**: infrastructure-level, passive probe (Kubernetes liveness/readiness probes) — "is the process running?"
- **Smoke test**: test-level, active verification — "does the critical functionality work?"

---

### 🔩 First Principles Explanation

```java
// SMOKE TESTS using REST Assured (Java) - fast, minimal, deployment verification

@Tag("smoke")  // Mark as smoke tests — can run subset: mvn test -Dgroups=smoke
class SmokeTest {
    
    private static final String BASE_URL = System.getenv("APP_URL"); // deployed app URL
    
    @BeforeAll
    static void setup() {
        RestAssured.baseURI = BASE_URL;
        RestAssured.config = RestAssured.config()
            .httpClient(HttpClientConfig.httpClientConfig()
                .setParam(CoreConnectionPNames.CONNECTION_TIMEOUT, 5000)
                .setParam(CoreConnectionPNames.SO_TIMEOUT, 5000));  // fast timeout
    }
    
    @Test
    @DisplayName("Health endpoint is UP")
    void healthCheck() {
        given().when().get("/health")
            .then()
            .statusCode(200)
            .body("status", equalTo("UP"));
    }
    
    @Test
    @DisplayName("Database is reachable")
    void databaseHealth() {
        given().when().get("/health/db")
            .then()
            .statusCode(200)
            .body("status", equalTo("UP"))
            .body("database", equalTo("connected"));
    }
    
    @Test
    @DisplayName("Authentication endpoint responds")
    void authEndpoint() {
        given()
            .body(Map.of("email", SMOKE_TEST_USER, "password", SMOKE_TEST_PASSWORD))
            .contentType(ContentType.JSON)
        .when()
            .post("/auth/login")
        .then()
            .statusCode(200)
            .body("accessToken", notNullValue());
    }
    
    @Test
    @DisplayName("Core product API responds")
    void coreProductApi() {
        String token = getToken();  // reuse auth from previous test
        given()
            .header("Authorization", "Bearer " + token)
        .when()
            .get("/products?limit=1")
        .then()
            .statusCode(200)
            .body("items", notNullValue());
    }
}
```

```yaml
# GitHub Actions: smoke tests in deployment pipeline
name: Deploy and Smoke Test

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: ./deploy.sh staging ${{ github.sha }}
        
      - name: Wait for deployment healthy
        run: |
          for i in {1..30}; do
            if curl -f "$STAGING_URL/health"; then echo "Ready!"; break; fi
            echo "Waiting... ($i/30)"; sleep 10
          done
      
      - name: Run smoke tests
        run: mvn test -Dgroups=smoke -DAPP_URL=$STAGING_URL
        timeout-minutes: 2   # smoke tests should be FAST
        
      - name: Rollback on smoke test failure
        if: failure()
        run: ./rollback.sh staging  # revert to previous version immediately
        
  full-test:
    needs: deploy    # only run if smoke tests pass
    runs-on: ubuntu-latest
    steps:
      - name: Run full E2E test suite
        run: mvn test -Dgroups=e2e -DAPP_URL=$STAGING_URL
        timeout-minutes: 30
```

```
SMOKE TEST DESIGN PRINCIPLES:

  1. FAST: total runtime < 2 minutes
     (if it takes longer, it's not a smoke test anymore)
  
  2. CRITICAL ONLY: test paths that, if broken, make the app unusable
     ✓ App starts and responds
     ✓ Authentication works
     ✓ Core business function responds
     ✗ Edge cases, error handling, all features
  
  3. INDEPENDENT: don't depend on specific data in the database
     Use a dedicated smoke test user in all environments
     Use `GET` for read operations where possible (no data pollution)
  
  4. ENVIRONMENT AGNOSTIC: same smoke tests run in staging AND production
     Tests use the deployed app's URL via env variable
  
  5. IMMEDIATE ROLLBACK on any failure:
     One failed smoke test → entire deployment is suspect → rollback
     Don't cherry-pick which failures are "acceptable"
```

---

### ❓ Why Does This Exist (Why Before What)

Deployment pipelines deploy code automatically and frequently. Every deployment carries risk: a missing environment variable causes the app to crash at startup; a database migration applied in the wrong order breaks the schema; a new dependency version introduces a conflict. Full test suites take 30-60 minutes — too slow to catch these startup failures before they affect users. Smoke tests provide a 60-second sanity check between deployment and user traffic: catch the most catastrophic failures immediately, roll back, and preserve user experience.

---

### 🧠 Mental Model / Analogy

> **Smoke tests are the pre-flight checklist before takeoff**: before a pilot takes off, they run through a checklist of the most critical systems — engines responsive, flaps moving, instruments showing correct readings. They don't test every possible failure mode (that's done in maintenance). They check: "is anything obviously, catastrophically wrong?" If yes, stay on the ground. Software smoke tests are the same: deploy → run the pre-flight checklist → if anything critical fails, don't "take off" (don't send user traffic to this deployment).

---

### 🔄 How It Connects (Mini-Map)

```
Deployment completes; need to verify the deployed system is basically functional
        │
        ▼
Smoke Test ◄── (you are here)
(minimal, fast; critical paths only; binary pass/fail; triggers rollback on failure)
        │
        ├── E2E Test: smoke tests are a subset of E2E tests (the most critical ones)
        ├── CI-CD Pipeline: smoke tests are a pipeline stage between deploy and full test
        ├── Health Check: infrastructure-level (Kubernetes probes); smoke tests go further
        └── Regression Test: full regression only runs AFTER smoke tests pass
```

---

### 💻 Code Example

```bash
# Minimal smoke test script (shell) - for simple apps

#!/bin/bash
APP_URL="${1:-http://localhost:8080}"
FAILURES=0

check() {
  local name="$1" url="$2" expected_status="$3"
  actual=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$actual" = "$expected_status" ]; then
    echo "✓ $name"
  else
    echo "✗ $name — expected $expected_status, got $actual"
    FAILURES=$((FAILURES + 1))
  fi
}

echo "Running smoke tests against $APP_URL..."
check "Health endpoint"       "$APP_URL/health"       "200"
check "Database health"       "$APP_URL/health/db"    "200"
check "Homepage loads"        "$APP_URL/"             "200"
check "API responds"          "$APP_URL/api/products" "200"
check "Auth redirects"        "$APP_URL/login"        "200"

if [ $FAILURES -gt 0 ]; then
  echo "SMOKE TESTS FAILED: $FAILURES test(s) failed. Rolling back."
  exit 1
else
  echo "All smoke tests passed. Deployment is stable."
  exit 0
fi
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Smoke tests passing means the deployment is safe | Smoke tests only verify CRITICAL functionality. A passing smoke test means "it's not catastrophically broken." Bugs in non-critical paths, performance degradation, and edge-case failures won't be caught by smoke tests. The full regression suite still needs to pass. |
| Smoke tests should be thorough | The more comprehensive smoke tests become, the more they slow down the deployment pipeline and the more they resemble a full test suite. Keep smoke tests to 5-15 tests maximum, running in under 2 minutes. If you want more coverage, add it to the integration or E2E suite (which runs after smoke tests pass). |
| Smoke tests replace health checks | Health checks (Kubernetes liveness/readiness probes) are infrastructure-level: "is the process running and ready to serve traffic?" Smoke tests are test-level: "does the critical application logic work?" Both are needed. Health checks gate traffic routing; smoke tests gate deployment promotion. |

---

### 🔗 Related Keywords

- `E2E Test` — smoke tests are a minimal subset of E2E tests
- `CI-CD Pipeline` — smoke tests are a pipeline stage after deployment
- `Regression Test` — full regression runs after smoke tests pass
- `Unit Test` — runs before deployment; smoke tests run after deployment

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SMOKE TEST = "is it basically alive?"                   │
│ WHEN: immediately after every deployment                │
│ SPEED: < 2 minutes total                               │
│ SCOPE: 5-15 most critical tests only                   │
│                                                          │
│ MUST INCLUDE:                                           │
│  • /health → 200 OK                                    │
│  • /health/db → 200 OK (DB connected)                 │
│  • Core auth endpoint works                            │
│  • One or two core business functions respond          │
│                                                          │
│ ON FAILURE: rollback immediately — no exceptions       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Blue-green deployments and canary releases change when and how smoke tests run. In a blue-green deployment: new version (green) is deployed alongside the current version (blue); smoke tests run against green before traffic is switched. In a canary release: 5% of traffic is routed to the new version gradually. Where do smoke tests fit in the canary workflow? Can you run smoke tests against 5% traffic? Or do you need a pre-traffic smoke test environment? What happens if smoke tests pass but the canary shows elevated error rates for 5% of real users — is that a smoke test failure or a different signal?

**Q2.** Smoke test users (dedicated test accounts in every environment) create a security concern: these accounts have known credentials hardcoded or stored in CI secrets. In production: if the smoke test user credentials are compromised, an attacker has a valid account. Mitigation strategies: (a) smoke test user has minimal permissions (read-only, no payment capability); (b) credentials rotated regularly via secrets manager; (c) smoke test user is IP-restricted (only accessible from CI CIDR blocks); (d) use short-lived tokens (OAuth client credentials flow for smoke tests, not username/password). Design the smoke test authentication strategy for a production system where security is critical.
