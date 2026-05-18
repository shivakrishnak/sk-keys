---
id: IAM-027
title: "IAM Platform Design at Scale"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★★
depends_on: IAM-026
used_by: IAM-028, IAM-029, IAM-030
related: IAM-026, IAM-028, IAM-030
tags:
  - iam
  - security
  - identity
  - scale
  - advanced
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/iam/iam-platform-design-at-scale/
---

⚡ TL;DR - IAM platform design at scale addresses the
engineering challenges of 100,000+ user identity systems:
auth path latency (sub-50ms token validation globally),
availability (auth is a critical single point of failure),
SCIM provisioning throughput (mass on/offboarding during
M&A), connector reliability (500+ app connections), and
token lifecycle management (billions of tokens issued,
rotated, and revoked). Techniques: stateless JWT validation
at CDN edge, global JWKS caching with key rotation, event-
driven provisioning pipelines, and circuit breakers on
SCIM connector pools.

---

### 🔥 The Problem This Solves

At 100,000 users and 200 connected applications:
- Every web request generates a token validation call
  (millions/second at peak)
- Mass onboarding (M&A, seasonal contractors) requires
  provisioning thousands of accounts in hours
- A single SCIM connector failure blocks all provisioning
  for that app silently
- Token revocation must be near-real-time (attacker
  with stolen token should lose access within seconds)
- Key rotation must be transparent (no user disruption
  when JWKS keys rotate)
- Conditional access policies evaluated per request
  slow down the auth path if not optimized

These problems do not exist at 1,000 users but become
engineering challenges at 100,000+.

---

### 📘 Textbook Definition

IAM platform design at scale refers to the engineering
patterns and system design decisions required to operate
identity infrastructure reliably, performantly, and
at enterprise scale (100,000+ users, 200+ applications,
billions of authentication events per day).

**Scale dimensions:**

**Auth throughput:** Number of token validation/issuance
events per second. At 100k users with modern web apps
making 10-50 API calls per minute: 10,000-100,000
token validations/second at peak.

**Provisioning throughput:** Number of user create/
update/delete operations per unit time. Normal: 10-100/hour.
M&A surge: 10,000+ in a few hours.

**Token revocation latency:** Time from "revoke token"
command to "token rejected at all validation points."
Network-based revocation: potentially instant. JWTs:
only at expiry unless token introspection is used.

**Connector reliability:** With 200+ SCIM connectors,
even 99.9% reliability = 2 connectors failing at any
moment. Failure must be detected, alerted, and not
block the rest of the provisioning pipeline.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
IAM at scale is about making token validation fast
globally, provisioning reliable under surges, token
revocation near-real-time, and the overall system
resilient to partial failures.

**One analogy:**
> Passport control at a large international airport:
>
> - Many lanes (token validation replicas)
> - Pre-check / trusted traveler lanes (cached sessions)
> - If one lane breaks: traffic re-routed, not stopped
> - Interpol watchlist checked per passenger (revocation)
> - Passport scanning (signature validation) done locally
>   with a shared key database (JWKS caching at edge)
> - Surge handling: additional staff deployed during
>   peak season (auto-scaling auth servers)

**One insight:**
The auth critical path and the provisioning path have
different failure modes and different SLOs. Auth must
never fail closed (blocking all access is worse than
a brief security gap); provisioning can be delayed
without immediate user impact. Design them independently
with different error handling strategies.

---

### 🔩 First Principles Explanation

**JWT validation optimization:**

OAuth access tokens as JWTs enable stateless validation:
the token contains all claims, signed with the IdP's
private key. Any service can validate without calling
the IdP, by checking the signature against the cached
public key (JWKS endpoint).

Optimization at scale:
1. Cache JWKS at CDN edge (not per-instance):
   sub-millisecond key fetch, not 100ms network roundtrip
2. JWT validation: pure CPU (signature verification);
   horizontally scalable without shared state
3. Token TTL trade-off: longer TTL (60min) = less
   validation overhead; shorter TTL (5min) = faster
   revocation but more token refresh traffic
4. Audience validation: cache by audience claim to
   avoid re-parsing all claims per request

**Revocation at scale:**

JWTs are self-contained; revocation requires out-of-band
checking. Options:

- **Short TTL:** token expires naturally (5-15 min);
  fast effective revocation but adds refresh traffic
- **Token introspection (RFC 7662):** call the IdP to
  validate each token. Accurate but adds latency (50-100ms
  round-trip). Only viable at lower throughput.
- **Revocation list:** maintain a list of revoked JTIs
  (JWT IDs). Check on every validation. Redis at sub-ms
  latency; must be globally replicated.
- **Refresh token rotation:** when an access token
  is revoked, the refresh token is also revoked.
  When attacker tries to refresh: denied. Access token
  still works until TTL (minutes). Acceptable trade-off.

---

### 🧪 Thought Experiment

**Mass provisioning during M&A (10,000 users in 4 hours):**

```
Challenge: Acme acquires 10,000 Globex users.
Day 1: all must have email access.
Day 30: all must be fully provisioned to all 200 apps.

Provisioning throughput analysis:
  Normal Okta SCIM push rate: ~10 provisioning events/sec
  10,000 users @ 10/sec = 1,000 seconds = 17 minutes
  (for Okta to process internally)

  But: 10,000 users x 200 apps = 2,000,000 SCIM operations
  At 10/sec to each app = 200,000 seconds per app
  Serial approach: days, not hours

  Scale approach:
  1. Prioritize critical path (email + VPN + core tools):
     ~5 apps x 10,000 = 50,000 operations
     With 50 parallel SCIM connections: ~100 seconds per app

  2. Batch remaining apps over 30 days (not day 1)
     SCIM with exponential backoff on throttling

  3. Use event-driven provisioning:
     Okta Universal Sync -> Kafka topic -> multiple consumers
     One consumer per application connector
     Dead-letter queue for failed provisioning events
     Retry with backoff; alert on > N failures

  4. Monitor provisioning pipeline:
     Dashboard: per-app provisioning queue depth
     Alert: queue depth > 100 for > 30 minutes
     Alert: error rate > 5% for any connector

  Result: critical apps provisioned in < 30 minutes;
          full 200-app provisioning over 30 days;
          no user-impacting bottleneck
```

---

### 🧠 Mental Model / Analogy

> IAM at scale is like a bank's transaction processing
> system:
>
> - **Normal auth validation** = ATM transaction (instant,
>   from cached local balance, no central call)
> - **Session establishment** = bank teller verification
>   (slower, checks central records, establishes cached
>   local state)
> - **Token revocation** = fraud freeze (near-real-time
>   propagation to all ATMs; short delay acceptable
>   but not indefinite)
> - **SCIM provisioning surge** = bank system upgrade
>   migration (batched, offline, does not block live
>   transactions)
> - **JWKS key rotation** = ATM PIN algorithm update
>   (rolled out gradually; old algorithm valid during
>   transition; transparent to customer)

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
At 100,000 users, making identity work fast and reliably
requires the same engineering effort as making a high-
traffic website fast: caching, replication, batching,
and circuit breakers.

**Level 2 (junior developer):**
Token validation best practices: cache the JWKS response
(public keys) in memory with a TTL of 1-24 hours.
Do not call the JWKS endpoint on every request. Use
a JWT library that handles JWKS caching automatically.
Refresh the cache when key rotation is detected
(signature validation failure with cached key -> refresh
once -> retry).

**Level 3 (mid engineer):**
SCIM connector resilience pattern: wrap every SCIM
provisioning call in a retry with exponential backoff
(1s, 2s, 4s, 8s, max 5 retries). Track per-connector
error rates. If error rate > 10% over 10 minutes:
circuit breaker opens; provisioning events for that
connector go to dead-letter queue; alert fires. SOC
investigates the connector. Prevents one failing connector
from backing up the entire provisioning pipeline.

**Level 4 (senior/staff):**
Conditional access policy optimization: evaluating
user risk, device trust, and IP reputation per request
can add 50-200ms to auth latency. At 10,000 requests/sec,
poorly optimized conditional access = 500-2000ms of
added latency per request. Optimizations:
- Cache conditional access results for session duration
  (re-evaluate only on session start or on risk signal)
- Async risk signal updates (risk score updated in
  background; sync validation uses cached score)
- Timeout budget: conditional access evaluation has a
  max latency budget; if not complete, use last known
  risk score + conservative policy

**Level 5 (distinguished):**
Global token validation architecture: deploy JWT
validation at CDN edge (Cloudflare Workers, Lambda@Edge).
Validation is CPU-bound (signature check): latency
is proportional to edge-to-origin distance. At the
edge, JWKS is cached with stale-while-revalidate pattern.
Result: <5ms auth latency for 95th percentile globally,
down from 150-300ms with central validation. Trade-off:
revocation latency is bounded by JWKS cache TTL at the
edge (default: 1 hour). High-security endpoints use
short-lived tokens (15 min) to bound revocation window
at the edge.

---

### ⚙️ How It Works (Mechanism)

```
Edge JWT Validation Architecture:

CDN Edge (Cloudflare Worker):
  1. Request arrives: GET /api/data
     Authorization: Bearer eyJhbGciOiJS...

  2. Edge Worker: get JWKS (cached, TTL=1h):
     fetch("https://idp.company.com/.well-known/jwks.json")
     -> cached: [{kid: "key-1", kty: "RSA", n: "...", e: "AQAB"}]

  3. Validate JWT:
     a. Parse header: {alg: "RS256", kid: "key-1"}
     b. Find key by kid in JWKS cache
     c. Verify RSA signature (CPU-bound, ~0.5ms)
     d. Check exp claim: not expired
     e. Check aud claim: api.company.com
     f. Check iss claim: https://idp.company.com

  4. Valid: add X-User-Id header, forward to origin
     Invalid: 401 response immediately (no origin call)

  Latency added: ~1-3ms (cached JWKS, pure CPU validation)
  vs. 150-300ms if validating at origin with IdP round-trip

JWKS Key Rotation (zero-downtime):
  1. IdP generates new key pair (kid: "key-2")
  2. IdP publishes JWKS with BOTH keys:
     [{kid: "key-1", ...}, {kid: "key-2", ...}]
  3. New tokens issued with kid: "key-2"
  4. Old tokens (kid: "key-1") still valid while key-1
     is in JWKS (key-1 validity period: 24h overlap)
  5. After 24h: key-1 removed from JWKS
  6. All edge JWKS caches refresh (TTL expiry or active
     cache invalidation)
  7. Old tokens: validation fails (key not found in JWKS)
     -> users prompted to re-authenticate

Provisioning Pipeline (event-driven):
  Okta event: user.lifecycle.activate
  -> Okta Event Hook -> SNS topic: identity-events
  -> SQS queues per connector (GitHub, Jira, AWS, ...)
  -> Lambda consumer per connector:
     - Calls app SCIM API with retry/backoff
     - Success: mark event processed
     - Failure after 5 retries: dead-letter queue (DLQ)
     - DLQ alert: SOC reviews failed provisioning

  Throughput:
  - SQS + Lambda: scales to 3000 concurrent Lambda
    invocations = 3000 concurrent connector calls
  - M&A surge: 10,000 users / 200 apps =
    2,000,000 events queued
  - Processing rate: 3,000 events/sec = 11 minutes
    for full provisioning (if apps support it)
```

---

### ⚖️ Comparison Table

| Pattern | Latency | Revocation Speed | Complexity | Best For |
|:---|:---|:---|:---|:---|
| Centralized token validation | 50-200ms | Instant | Low | Low traffic (<1k req/sec) |
| Edge JWT validation (JWKS cache) | 1-5ms | Bounded by JWKS TTL | Medium | High traffic, global |
| Token introspection (RFC 7662) | 50-150ms | Instant | Low-Medium | When instant revocation needed |
| Short-lived JWT (15 min TTL) | 1-5ms | 15 min max | Low | High security + high performance |
| Refresh token rotation | 1-5ms per access token | Next refresh attempt | Medium | Long user sessions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Short JWT TTL = frequent re-login for users" | Short access token TTL (5-15 min) is transparent to users if refresh tokens are used. The access token is silently refreshed by the client SDK; users only re-authenticate when the refresh token expires (days/weeks). |
| "JWKS caching breaks revocation" | JWKS cache TTL only affects the time window when a compromised signing KEY would still be trusted. JTI-based revocation (specific token blacklist) is independent of JWKS caching. Use both: JWKS for key validation, JTI list for individual token revocation. |
| "More SCIM retries = more reliable" | Unbounded retries can create thundering herds when a connector is genuinely down. Exponential backoff + circuit breaker + dead-letter queue is more reliable than infinite retries. |
| "Global JWKS caching is a single point of failure" | JWKS is a static public key - if the JWKS endpoint is unavailable, use cached value (stale-while-revalidate). Edge caches serve validation even if the IdP is temporarily unreachable. |

---

### 🚨 Failure Modes & Diagnosis

**JWKS cache stampede after key rotation**

```bash
# After IdP key rotation: all tokens fail validation
# because edge caches have expired key-1 but new
# tokens have kid: key-2 which is not in the stale cache

# Symptom: 401 errors for ALL requests simultaneously
# after a key rotation event

# Immediate check: what JWKS does the edge have?
curl -H "Cache-Control: no-store" \
  https://idp.company.com/.well-known/jwks.json
# Check: is key-2 present? When was it added?

# Check edge cache state (Cloudflare):
# Purge JWKS cache manually:
curl -X POST "https://api.cloudflare.com/client/v4/zones/
  $ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -d '{"files": ["https://idp.company.com/.well-known/jwks.json"]}'

# Prevention: IdP should publish dual-key JWKS for 24h
# before retiring old key. Token libraries should
# refresh JWKS on signature validation failure.
```

**SCIM connector silent failure**

```bash
# Users report: new employee cannot access GitHub
# but has Okta account and other apps work

# Check Okta provisioning logs for GitHub connector:
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/apps/$GITHUB_APP_ID/
   users?filter=status eq \"PROVISIONED\"" | \
  jq '.[] | select(.profile.email == "alice@company.com")'

# If user not in provisioned list: check connector health
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/apps/$GITHUB_APP_ID" | \
  jq '.features, .status'

# Check system log for provisioning errors:
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/logs?
   filter=eventType eq \"app.user_management.push_profile_failure\"
   AND target.displayName eq \"GitHub Enterprise\"
   &since=$(date -d '24h ago' -u +%FT%TZ)"
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-026` - Enterprise IAM Architecture: the full stack

**Builds On This:**
- `IAM-028` - Federated Identity at Enterprise Scale
- `IAM-029` - IAM Compliance: operational requirements
- `IAM-030` - IAM Observability: monitoring this stack

**Related:**
- `IAM-031` - IAM Specification Convergence: protocol standards at scale

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ IAM AT SCALE - KEY DESIGN DECISIONS                  │
├────────────────────────────────────────────────────── ┤
│ Token validation │ Edge JWT (JWKS cached) <5ms       │
│ Revocation       │ Short TTL (15min) + JTI blocklist │
│ Provisioning     │ Event-driven + circuit breaker    │
│ Key rotation     │ Dual-key overlap (24h)            │
│ High availability│ Multi-region IdP + emergency acct │
│ Surge handling   │ Queue-based SCIM + priority lanes │
└────────────────────────────────────────────────────── ┘
SLO targets:
  Auth validation: p99 < 50ms globally
  Provisioning: critical apps < 30 min
  Revocation: < 15 min for access tokens (15min TTL)
  Availability: 99.99% (< 53 min downtime/year)
```

**Interview one-liner:**
"IAM at scale requires edge JWT validation for sub-5ms
auth latency (JWKS cached at CDN), short token TTL
(15 min) for fast revocation, event-driven provisioning
with circuit breakers for SCIM connector resilience,
and dual-key JWKS publication for zero-downtime key
rotation. The auth critical path must never fail closed;
provisioning can queue and retry."

---

### 💎 Transferable Wisdom

The IAM scaling patterns are direct applications of
distributed systems fundamentals: (1) stateless validation
at the edge (same as stateless HTTP serving - scale
horizontally, no shared state); (2) JWKS caching with
stale-while-revalidate (same as CDN cache with origin
refresh); (3) circuit breaker on SCIM connectors (same
as circuit breaker for any external service dependency);
(4) event-driven provisioning (same as event-driven
microservice communication - decouple producers from
consumers, handle backpressure via queues). The IAM-
specific framing adds security constraints (revocation
latency, key rotation) on top of standard distributed
systems patterns. An engineer who knows distributed
systems fundamentals can design IAM at scale.

---

### ✅ Mastery Checklist

1. **DESIGN** Implement sub-10ms JWT validation for
   a globally distributed API with 100,000 requests/
   second. Describe the JWKS caching strategy, edge
   deployment, and how key rotation is handled without
   user disruption.

2. **ARCHITECT** Design an event-driven SCIM provisioning
   pipeline that handles a 10,000-user M&A onboarding
   surge to 200 apps while maintaining < 5% provisioning
   error rate and alerting on connector failures within
   5 minutes.

3. **OPTIMIZE** Your IAM team reports that token
   revocation takes up to 4 hours (JWKS cache TTL).
   Your security team requires < 15 minutes for compromised
   account revocation. Design a hybrid approach using
   JWT TTL, JTI blocklist, and cache invalidation to
   achieve the 15-minute SLO.

---

*Identity & Access Management | IAM-027 | v5.0*