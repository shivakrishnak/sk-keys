---
layout: default
title: "API Gateway Patterns"
parent: "HTTP & APIs"
nav_order: 28
permalink: /http-apis/api-gateway-patterns/
number: "API-028"
category: HTTP & APIs
difficulty: ★★★
depends_on: API Gateway, BFF (Backend for Frontend), Microservices, API Management Platform, REST
used_by: API Management Platform, Apigee, Service Mesh
related: BFF (Backend for Frontend), Service Mesh, API Management Platform, Ambassador Pattern
tags:
  - api
  - architecture
  - pattern
  - microservices
  - advanced
  - deep-dive
---

# API-028 — API Gateway Patterns

⚡ TL;DR — API Gateway Patterns define different topologies for routing, aggregating, and securing API traffic: single gateway, BFF, federated gateway, and multi-layer gateway.

| #2292 | Category: HTTP & APIs | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | API Gateway, BFF (Backend for Frontend), Microservices, API Management Platform, REST | |
| **Used by:** | API Management Platform, Apigee, Service Mesh | |
| **Related:** | BFF (Backend for Frontend), Service Mesh, API Management Platform, Ambassador Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company begins with one API gateway. As the organisation grows: mobile teams need different payload sizes than web teams; internal services need different authentication than external consumers; partner APIs need different rate limits than developer sandbox APIs; B2B APIs need XML, consumer APIs need JSON. Applying all requirements to a single gateway creates a configuration nightmare — one change risks breaking unrelated consumers. Teams start bypassing the gateway for their special cases.

**THE BREAKING POINT:**
A single monolithic API gateway serving all consumers, all clients, and all teams becomes a shared bottleneck — the hardest anti-pattern in API architecture to fix once embedded. Configuration policy conflicts, deployment coordination between unrelated teams, and unbounded scope make the "one gateway to rule them all" approach a serious organisational risk at scale.

**THE INVENTION MOMENT:**
API Gateway Patterns emerged to describe the right topologies for different organisational and technical requirements: when to use a single gateway, when to split by client type (BFF), when to federate ownership, and when to layer gateways for security separation.

---

### 📘 Textbook Definition

**API Gateway Patterns** are architectural topologies for deploying API proxies and gateways between API consumers and backend services. Key patterns: **Single Gateway** (all traffic through one proxy), **BFF (Backend for Frontend)** (separate gateway per client type), **Aggregation Gateway** (gateway composes calls to multiple backends), **Federated Gateway** (gateway mesh where teams own their own gateways behind a shared edge), **Layered Gateway** (external security perimeter gateway + internal routing gateway), and **Service Mesh + Gateway** (gateway for north-south traffic, mesh for east-west). Each pattern addresses different ownership, performance, and security concerns.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Different gateway topologies solve different problems: single for simplicity, BFF for client-specific needs, federated for team autonomy, layered for security.

**One analogy:**
> A shopping centre can be architectured as: one massive entrance for everyone (single gateway), separate entrances for shoppers and delivery trucks (BFF), a security lobby followed by individual shop entrances (layered gateway), or a mall where each shop has its own entrance but shares a common parking authority (federated). The right layout depends on the mix of visitors, security needs, and operational ownership.

**One insight:**
The central question in gateway pattern selection is: who owns the gateway configuration? If one team owns it, a single gateway works. If each product team owns their API concerns, a federated or BFF model is required to maintain autonomy and deploy velocity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A gateway is a proxy — it intercepts traffic and applies policies before forwarding.
2. Every gateway adds a network hop; multiple gateway layers add multiple hops.
3. Cross-cutting concerns (authentication, rate limiting, observability) should live at the outermost gateway layer where possible.
4. Gateway topology should reflect team topology (Conway's Law); misalignment creates bottlenecks.
5. Backends should be shielded from consumer concerns — consumers should never receive backend-internal hostnames or implementation details.

**DERIVED DESIGN:**
From invariant 4: if five product teams independently own their APIs, each team can own a BFF or per-service gateway, federated behind a shared edge for common security. A single shared gateway would require all five teams to coordinate deployments — a Conway's Law violation.

From invariant 3: authentication and DDoS protection belong at the edge (outermost) gateway. Rate limiting per consumer belongs at the edge. Backend-specific transformation and aggregation belong at an inner gateway layer closer to the backend.

**THE TRADE-OFFS:**
**Gain (multi-pattern):** Autonomy per team; client-optimised payloads; clear security boundaries; independent deployability.
**Cost:** Multiple gateway hops add latency; distributed configuration is harder to audit; more infrastructure to operate; potential policy inconsistency across gateways.

---

### 🧪 Thought Experiment

**SETUP:**
A fintech company has: a React web app, an iOS app, a B2B partner API, and an internal microservices API — all calling the same set of 15 backend services.

**WHAT HAPPENS with Single Gateway:**
All four consumers share one gateway config. The mobile team needs gzip compression and smaller payloads — adding that breaks the B2B partner who depends on the full response. The B2B partner needs XML — adding XML transformation adds latency to mobile calls. Partners get rate-limited by configuration changes made for the developer sandbox. Every change requires coordinating 4 consumer teams. Deployments slow to biweekly cycles.

**WHAT HAPPENS with BFF + Federated:**
Each consumer type has a dedicated BFF: `mobile-bff`, `web-bff`, `partner-bff`. A shared **edge gateway** handles authentication (OAuth2), DDoS protection, and TLS termination for all four. Teams deploy their BFF independently. Mobile team enables gzip; partner team enables XML — no cross-team coordination needed. Security policies are managed once at the edge. Deployments daily.

**THE INSIGHT:**
The correct gateway topology is often not "what is technically possible" but "what enables teams to deploy independently." BFF and federated patterns trade infrastructure complexity for organisational velocity.

---

### 🧠 Mental Model / Analogy

> Think of API gateway patterns as crowd management at a large event venue. A single gateway is one entrance — everyone goes through the same line (simple, bottleneck). BFF is separate VIP and general admission entrances — very different experiences without interference. Federated is each event area having its own entrance managed by the area's operator, with a shared venue perimeter security. Layered is a perimeter fence that all visitors cross, followed by each area's own access check.

- "Single entrance" → Single API Gateway
- "VIP entrance + general entrance" → BFF pattern
- "Each event area's own entrance" → Federated gateway
- "Perimeter fence + area entrance" → Layered gateway (edge + inner)
- "Perimeter security guards" → edge-layer cross-cutting policies (auth, DDoS)

Where this analogy breaks down: venue entrances are stateless. API gateways maintain session/quota state, routing tables, and policy configurations — making consistency across federated gateways a non-trivial distributed systems problem.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An API gateway is a single entry point for your API. When you have many different types of users — mobile apps, web apps, partners — you can either send them all through the same door (one gateway) or give each type their own customised door (multiple gateways). API Gateway Patterns describe when to use which door configuration and why.

**Level 2 — How to use it (junior developer):**
Choose your pattern based on who consumes your APIs and who owns the gateway config. Single gateway: small team, few consumers, one team owns the gateway. BFF: mobile/web/partner need different responses (payload size, protocol, schema). Federated: multiple product teams each own their own API surface. Layered: regulated environment needing security separation between the public perimeter and internal routing.

**Level 3 — How it works (mid-level engineer):**
**Single gateway** (Kong/Apigee): one gateway process or fleet; all routes configured centrally. **BFF**: each BFF is a dedicated service (Node.js/GraphQL typically) that aggregates calls to multiple backend services and shapes responses for one specific client type. The BFF may itself sit behind an edge gateway for security. **Federated**: an edge gateway (e.g., Nginx or Apigee) performs authentication and DDoS protection, then routes to individual team-owned gateways (Kong instances or Apigee environments) which handle team-specific routing and transformation. **Layered**: DMZ-deployed edge processes TLS, auth, and IP filtering; internal gateway handles routing and protocol translation.

**Level 4 — Why it was designed this way (senior/staff):**
Conway's Law is the primary driver of gateway pattern selection. Single gateways create a "shared bottleneck" organisational pattern — a change to the central gateway config requires coordination across all teams. BFF and federated patterns explicitly mirror the team structure: each team owns their gateway boundary, deploying independently. This is why Netflix, Spotify, and Amazon each have multiple API gateways rather than one: not for technical reasons first, but organisational velocity reasons. The technical benefit (client-optimised responses) follows from the organisational benefit (team autonomy).

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────────────┐
│  API GATEWAY PATTERN TOPOLOGY OVERVIEW                │
│                                                       │
│  SINGLE GATEWAY:                                      │
│  Web/Mobile/Partner → [Gateway] → Backends            │
│                                                       │
│  BFF PATTERN:                                         │
│  Mobile App → [Mobile BFF] ─┐                        │
│  Web App   → [Web BFF]    ──┼→ Backends               │
│  Partners  → [Partner GW] ─┘                         │
│                                                       │
│  LAYERED (Edge + Inner):                              │
│  Internet → [Edge GW: auth, DDoS, TLS]                │
│               → [Inner GW: routing, transform]        │
│               → Backends                              │
│                                                       │
│  FEDERATED:                                           │
│  Internet → [Edge GW: shared security]                │
│               → [Team A GW] → Team A services         │
│               → [Team B GW] → Team B services         │
│               → [Team C GW] → Team C services         │
└───────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Layered Gateway):**
```
Mobile app: GET /v1/profile (Bearer: token)
  → Edge Gateway (perimeter)
    [← YOU ARE HERE: outer security layer]
  → Validate OAuth2 token → VALID
  → DDoS / rate check → PASS
  → Route to: Mobile BFF cluster
  → Mobile BFF: calls User Service + Preference Service
  → Aggregates: {user_profile} + {preferences}
  → Applies mobile-specific transform: reduces payload
  → Returns combined 200 to mobile client
```

**FAILURE PATH:**
```
Single Gateway configuration conflict:
  → Team A deploys rate-limit policy change
  → Policy regex matches Team B's /users/* routes unexpectedly
  → Team B consumers throttled unintentionally
  → No isolation: all consumers affected by one team's config
  [This failure mode drives adoption of BFF/Federated patterns]
```

**WHAT CHANGES AT SCALE:**
At 5 services: single gateway is sufficient. At 20 services/3 client types: introduce BFF. At 50 services/10 teams: federated gateway with GitOps config management per team. At 100+ services/global traffic: layered gateway with CDN edge (CloudFront/Cloudflare) as L7 outermost layer, regional API gateways as middle layer, service mesh for east-west.

---

### 💻 Code Example

**Example 1 — BFF aggregation (Node.js/Express):**

```javascript
// BAD: mobile client makes 3 separate API calls
// → 3 network round-trips, over-fetching data

// GOOD: Mobile BFF aggregates into one response
// mobile-bff/routes/profile.js
app.get('/v1/profile', authenticate, async (req, res) => {
  const userId = req.auth.sub;

  // Parallel calls to internal services
  const [user, prefs, recentOrders] = await Promise.all([
    userService.getUser(userId),        // internal call
    prefService.getPreferences(userId), // internal call
    orderService.getRecent(userId, 3),  // internal call
  ]);

  // Mobile-optimised payload (no desktop-only fields)
  res.json({
    id: user.id,
    name: user.displayName,       // not: full_legal_name
    avatar: user.avatarThumbnail, // not: full_resolution
    theme: prefs.mobileTheme,     // not: all preferences
    recentOrders: recentOrders.map(o => ({
      id: o.id,
      total: o.total,             // not: full order details
    })),
  });
});
```

**Example 2 — Layered gateway config (Nginx edge + Kong inner):**

```nginx
# Edge gateway (Nginx): TLS termination, IP allowlist, auth
# /etc/nginx/conf.d/edge.conf
server {
  listen 443 ssl;
  ssl_certificate /certs/api.crt;
  ssl_certificate_key /certs/api.key;

  # DDoS: limit request rate at edge
  limit_req zone=api_zone burst=20 nodelay;

  # Route to inner gateway (Kong)
  location /v1/ {
    # JWT validation at edge
    auth_jwt "API Realm";
    auth_jwt_key_file /certs/jwk.json;
    proxy_pass http://kong-internal:8000;
    # Strip auth header — inner GW trusts edge
    proxy_set_header X-Authenticated-User
      $jwt_claim_sub;
  }
}
```

**Example 3 — Federated gateway with team ownership:**

```yaml
# Team A owns: Kong declarative config for their routes
# teams/team-a/kong.yaml (GitOps managed)
_format_version: "3.0"
services:
- name: orders-service-team-a
  url: http://orders-svc.team-a.svc:8080
  routes:
  - name: orders-route
    paths: ["/team-a/v1/orders"]   # namespaced path
    hosts: ["api.company.com"]
  plugins:
  - name: rate-limiting
    config:
      minute: 500    # team-a specific limit
      policy: redis
# Team A deploys this independently via ArgoCD
# Edge gateway routes /team-a/* to team-a's Kong instance
```

---

### ⚖️ Comparison Table

| Pattern | Ownership | Latency | Best For | Risk |
|---|---|---|---|---|
| **Single Gateway** | Central platform team | One hop | Small orgs, few consumers | Shared bottleneck, config conflicts |
| **BFF** | Per client-type team | Two hops (edge + BFF) | Multi-client (mobile/web/partner) | BFF duplication across languages |
| **Aggregation GW** | Central team | One hop + backend fan-out | Reducing client round-trips | Complex aggregation logic in gateway |
| **Federated** | Per product team | Two hops (edge + team GW) | Large multi-team orgs | Policy inconsistency across gateways |
| **Layered** | Split (security team + product team) | Two+ hops | Regulated environments | Latency from multiple hops |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More gateway layers = more security | Each gateway layer adds security only if it implements unique policy checks. Multiple layers with identical policies add latency without adding security value |
| BFF means one per client OS (iOS, Android) | BFF means one per client experience type (mobile, web, partner). iOS and Android mobile apps typically share a single mobile BFF since they need similar optimisations |
| Federated means no central governance | Federated gateways still need an edge layer for shared security policies. "Federated" means team-level autonomy for routing and transformation, not freedom from baseline security standards |
| Service mesh replaces the API gateway | Service mesh manages east-west (service-to-service) traffic within a cluster. API gateway manages north-south (external consumer to service) traffic. They are complementary, not substitutes |

---

### 🚨 Failure Modes & Diagnosis

**1. BFF Overload — All Consumers Affected**

**Symptom:** Mobile BFF is CPU-saturated due to heavy aggregation logic. Mobile consumers experience high latency and timeouts.

**Root Cause:** BFF is too thin and delegates aggregation to the consumer, or too fat and performs expensive joins/transforms inline. Or BFF is not independently scalable from edge gateway.

**Diagnostic:**
```bash
# Check BFF resource usage:
kubectl top pod -n mobile-bff
# If CPU near limit: scale or optimise aggregation

# Check call latency breakdown:
kubectl logs -n mobile-bff deployment/mobile-bff \
  | grep "downstream_latency\|upstream_latency"
```

**Fix:** Extract BFF aggregation into dedicated async background workers for expensive operations. Cache frequently requested aggregations. Use `Promise.allSettled()` instead of `Promise.all()` to avoid single-backend failure cascading.

**Prevention:** Set BFF HPA with CPU target 70%. Load test BFF aggregation patterns at 2× expected peak before launch.

---

**2. Federated Policy Drift — Security Gap**

**Symptom:** Penetration test reveals one team's gateway does not enforce authentication. Unauthenticated requests reach a backend service.

**Root Cause:** Team C's Kong instance was deployed without the `jwt` or `oauth2` plugin. The edge gateway handles auth for most routes but the edge routing rule for `/team-c/*` was mis-configured to bypass auth.

**Diagnostic:**
```bash
# Audit all team gateways for auth plugin presence:
for team in team-a team-b team-c; do
  echo "=== $team ==="
  kubectl exec -n $team deployment/kong -- \
    curl -s localhost:8001/plugins \
    | jq '.data[].name' | grep -E "jwt|oauth2|key-auth"
done
# Missing output for a team = auth gap
```

**Fix:** Enforce baseline policy at the edge for all routes. Use OPA (Gatekeeper) to prevent gateway deployments without required plugins. Periodic automated audit of all team gateways.

**Prevention:** Implement `gateway-policy-enforcer` as a CI check: every team's Kong config must include auth plugin before merge is allowed.

---

**3. BFF Schema Drift — Mobile Client Breaks**

**Symptom:** Mobile app crashes after a backend service updates its response schema. BFF was passing through the backend response unchanged.

**Root Cause:** BFF was not transforming the backend schema — it was a transparent proxy, not a real BFF. When the backend changed `user.full_name` to `user.first_name + user.last_name`, the mobile app failed to parse.

**Diagnostic:**
```bash
# Check BFF response diff vs. mobile contract:
diff <(curl -s mobile-bff/v1/profile | jq 'keys') \
     <(cat mobile-contract.json | jq 'keys')
# Any diff = schema contract violation
```

**Fix:** Implement explicit response mapping in BFF: backend schema → BFF contract schema. Consumer-driven contract tests (Pact) between mobile client and BFF validate schema independently of backend changes.

**Prevention:** BFF must own its response contract independently of backend contracts. Test BFF contract with every backend deployment via contract tests in CI.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `API Gateway` — the fundamental proxy component that all gateway patterns build upon; understanding routing, policy enforcement, and load balancing is prerequisite
- `BFF (Backend for Frontend)` — the most widely adopted gateway pattern; understanding the BFF pattern's client-specific optimisation concept is central to multi-pattern topology

**Builds On This (learn these next):**
- `Service Mesh` — the east-west (internal service) complement to the north-south API gateway; together their topologies form the full traffic management architecture
- `API Management Platform` — platforms like Apigee and Kong implement multiple gateway patterns under one roof; understanding platform capabilities is the next step

**Alternatives / Comparisons:**
- `Service Mesh` — handles east-west traffic; API gateway patterns handle north-south; both approaches must be designed together for a complete traffic management architecture
- `Ambassador Pattern` — a per-service outbound proxy pattern; the microscopic version of the API gateway applying concerns at the individual service level

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Topologies for deploying API proxies:     │
│              │ single, BFF, federated, layered           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single gateway becomes a bottleneck when  │
│ SOLVES       │ multiple teams/clients have different API │
│              │ concerns and ownership                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Gateway topology should mirror team       │
│              │ topology — Conway's Law applies here too  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple client types: BFF. Multiple      │
│              │ teams: federated. Security zones: layered │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Over-engineering a simple 1-team, 1-      │
│              │ client API — start with a single gateway  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Autonomy + client optimisation vs.        │
│              │ additional hops + distributed config mgmt │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One door works for one family; a city    │
│              │  needs many entrances for many purposes." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BFF Pattern → Service Mesh → Federated    │
│              │ Identity → API Management Platform        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A company is redesigning their gateway topology. They currently have a single Nginx gateway handling 500 routes for 8 teams and 4 client types (web, iOS, Android, B2B partner). Each team reports slow deployment cycles because gateway changes require coordinating with 7 other teams. Design a target gateway topology, specifying which patterns to apply, who owns which layer, and how you would migrate from the current single gateway without a big-bang cutover.

**Q2.** A BFF for mobile aggregates calls to 5 backend services using `Promise.all()`. One of the 5 backends (Preferences Service) has a P95 of 800ms. The other 4 have P95 of 30ms. Analyse: (A) the P95 latency impact on the BFF response, (B) whether `Promise.all()` is the right approach, (C) what optimisations reduce the Preferences Service's impact on BFF response time, and (D) the trade-offs of each optimisation.

**Q3.** The Layered Gateway pattern places authentication at the edge and routing at the inner layer. A security team argues that repeating authentication at the inner layer (defence in depth) is worth the latency cost. A performance team argues that double-auth adds unacceptable P99 latency. Evaluate both positions and design a compromise that satisfies the security team's threat model without adding full double-authentication latency to every request.

