---
layout: default
title: "Multi-Region Architecture"
parent: "System Design"
nav_order: 699
permalink: /system-design/multi-region-architecture/
number: "699"
category: System Design
difficulty: ★★★
depends_on: "Geo-Replication, Active-Active, Active-Passive"
used_by: "Disaster Recovery"
tags: #advanced, #reliability, #distributed, #cloud, #architecture
---

# 699 — Multi-Region Architecture

`#advanced` `#reliability` `#distributed` `#cloud` `#architecture`

⚡ TL;DR — **Multi-Region Architecture** runs application infrastructure across multiple geographic cloud regions simultaneously, enabling near-zero RTO, low global latency, and isolation from regional cloud failures.

| #699 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Geo-Replication, Active-Active, Active-Passive | |
| **Used by:** | Disaster Recovery | |

---

### 📘 Textbook Definition

**Multi-Region Architecture** is the design of a distributed system where application infrastructure — compute, networking, databases, caches, message queues, and storage — is deployed across two or more geographically separate cloud regions. Multi-region can be implemented as: Active-Passive (primary region handles all traffic, secondary is DR standby), Active-Active (all regions handle live traffic simultaneously), or read-local/write-global (reads served from nearest region, writes forwarded to a single primary). Key challenges include: data consistency across regions, inter-region latency for synchronous operations, distributed transaction coordination, and significantly higher operational complexity. Benefits: regional fault isolation, low-latency serving for geographically distributed users, data sovereignty compliance, and business continuity against cloud provider outages.

---

### 🟢 Simple Definition (Easy)

Multi-Region: run your application in multiple cloud regions (e.g., US, EU, Asia) at the same time. Users get served from the nearest region (fast). If one region fails entirely (cloud outage), others keep running. Costs more and is more complex — only justified when a single-region outage is unacceptable or when users are spread globally.

---

### 🔵 Simple Definition (Elaborated)

Most applications start in one cloud region. When the business grows globally or requires near-zero downtime, multi-region becomes necessary. The architecture has three layers: traffic routing (Global Accelerator, CloudFront, or GeoDNS — directs users to nearest region), compute (app servers in each region), and data (geo-replicated databases). Each region is designed to be as self-contained as possible ("regional independence") so it can operate during a network partition between regions. The design challenge is state: stateless services are easy to multi-region; databases are hard.

---

### 🔩 First Principles Explanation

**Multi-region design principles:**

```
PRINCIPLE 1: REGIONAL INDEPENDENCE (Bulkhead Pattern)

  Each region should function independently with minimal cross-region dependency.
  
  ANTI-PATTERN (tight coupling across regions):
    User request → us-east-1 (app) → eu-west-1 (authentication service)
    → ap-southeast-1 (session service) → us-west-2 (database)
    
    Cross-region hops: 4 × 100ms = 400ms per request
    If eu-west-1 goes down: authentication unavailable → all regions broken
    
  CORRECT PATTERN (regional self-sufficiency):
    Each region: local authentication, local session, local database replica
    Cross-region: only for writes (single source of truth) and replication
    
    User request → nearest region → local auth → local session → local read DB
    Write operation → nearest region → forwards to primary region (or local primary)
    
  Benefits:
  - Network partition: each region still serves cached/local data
  - Latency: all reads local (~5-10ms instead of 100-300ms)
  - Blast radius: one region's failure doesn't cascade to others

PRINCIPLE 2: TRAFFIC ROUTING LAYER

  METHOD 1: AWS Global Accelerator (AnyCast routing)
    Static anycast IP: global routing network routes to nearest AWS edge
    From edge: routes to nearest healthy region's endpoint
    Failover: detects regional health check failure → reroutes in < 30s
    Use: API traffic, non-HTTP (UDP, TCP games)
    
  METHOD 2: Route53 Geolocation + Health Checks
    EU users: routed to eu-west-1 (by geolocation)
    US users: routed to us-east-1
    Health check: if us-east-1 unhealthy → all users → eu-west-1
    Use: web applications, content where geographic routing matters
    
  METHOD 3: CloudFront (CDN) Multi-Region Origins
    CDN edge: serves cached content from 400+ edge locations
    Origin failover: primary origin (us-east-1) + secondary (eu-west-1)
    If primary origin fails: CloudFront switches to secondary
    Use: web sites, static assets, API with CDN caching

PRINCIPLE 3: DATA ARCHITECTURE (the hard part)

  STATELESS COMPUTE: trivially multi-region
    Docker containers: same image deployed to each region
    Configuration: per-region config (database endpoint, etc.)
    No consistency challenge: no local state
    
  READ-HEAVY DATA: best case for multi-region
    Pattern: single write primary + regional read replicas
    Reads (80-95% of traffic): served from local replica (low latency)
    Writes (5-20% of traffic): forwarded to primary region or local writer
    
  WRITE-HEAVY DATA: harder
    Option A: Route all writes to one region (single primary)
      Writes: routed to us-east-1 regardless of user location
      EU user writes: 100ms roundtrip to primary (visible latency)
      Reads: local replica (low latency)
      
    Option B: Regional write sharding
      EU users always write to eu-west-1 (their data lives in EU)
      US users always write to us-east-1
      No cross-region writes needed (data is partitioned)
      Cross-region replication: only for shared/global data
      Challenge: cross-user interactions (US user reads EU user's data)
      
    Option C: Multi-master with conflict resolution
      See Active-Active keyword
      DynamoDB Global Tables, CockroachDB, Google Spanner

PRINCIPLE 4: OPERATIONAL COMPLEXITY COST

  Multi-region multiplies operational overhead:
  
  Single region:
    Deployment: push to 1 region
    Monitoring: 1 set of dashboards
    Database operations: 1 database
    Incidents: 1 set of on-call runbooks
    
  3-region multi-region:
    Deployment: push to 3 regions (must be coordinated, not all at once)
    Monitoring: 3 × dashboards + cross-region view
    Database operations: replication monitoring, lag alerts per region
    Incidents: which region? cross-region impact analysis
    Deployment risk: partial rollout (region A on new version, B/C on old)
    
  Cost: typically 2-3× single-region infrastructure cost
        + 2-4× operational overhead (engineering + on-call)
  
  WHEN IS IT WORTH IT?
    Cost of 1-hour regional outage > monthly cost increase
    User base is genuinely global (>20% of users in each region)
    Regulatory compliance requires it (GDPR, data sovereignty)
    SLA requires <5 minute RTO for regional outages

TRAFFIC PATTERNS: regional vs. global data

  REGIONAL DATA (stays in one region):
  - User sessions, personalisation
  - Content created by regional users
  - Regulatory-partitioned data (GDPR: EU data in EU)
  
  GLOBAL DATA (replicated everywhere):
  - Product catalogue, pricing
  - Application configuration
  - Feature flags
  - Non-personal analytics aggregates
  
  DESIGN: identify regional vs. global data early.
  Global data: replicate freely, tolerate eventual consistency.
  Regional data: strict partitioning, no cross-region replication.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Multi-Region:
- Single-region cloud outage (AWS us-east-1 2021): all services down
- Global users: high latency serving from distant single region
- No GDPR/data sovereignty compliance for international expansion

WITH Multi-Region:
→ Regional cloud outages: traffic reroutes to healthy regions (near-zero RTO)
→ Global users: served from nearest region (<20ms for most users)
→ Compliance: data partitioned by region for regulatory requirements

---

### 🧠 Mental Model / Analogy

> A global bank with branches in New York, London, and Tokyo. Each branch serves local customers independently (regional self-sufficiency). The core ledger is synchronised across all branches each day (geo-replication). If the New York HQ floods, London and Tokyo branches continue serving customers (regional independence). Local customers get fast service at their local branch (local data). The complexity: ensuring the core ledger stays consistent across all three branches (the hardest part of multi-region — the data layer).

"Bank branches" = regional application deployments
"Local customers served locally" = low-latency regional serving
"Core ledger across all branches" = geo-replicated database
"New York floods, other branches open" = regional fault isolation
"Ledger consistency" = distributed data consistency (the hard part)

---

### ⚙️ How It Works (Mechanism)

**Multi-region architecture components in AWS:**

```
TRAFFIC LAYER:
  Route53 (GeoDNS + health checks)
    → EU users: api.example.com → eu-west-1 ALB
    → US users: api.example.com → us-east-1 ALB
    → Failover: if us-east-1 unhealthy → all → eu-west-1
  
  Global Accelerator (optional, for lower network jitter):
    Single anycast IP → routes to nearest healthy region via AWS backbone

COMPUTE LAYER (per region):
  ECS Fargate or EKS (identical container images, per-region config)
  Auto Scaling Group: scale per-region independently
  ECR (Elastic Container Registry): images replicated to each region

NETWORKING LAYER (per region):
  VPC: separate VPC per region (isolation)
  VPC Peering or Transit Gateway: cross-region private connectivity for shared services
  Security Groups, NACLs: identical security rules applied per region

DATA LAYER:
  Aurora Global Database (relational):
    Primary (us-east-1): read + write
    Secondaries (eu-west-1, ap-southeast-1): read only, < 1s lag
    Failover: managed global failover < 60 seconds
    
  DynamoDB Global Tables (key-value):
    All regions: read + write (Active-Active)
    Conflict: LWW (last write wins by timestamp)
    
  ElastiCache (Redis) per region:
    No global replication (cache is ephemeral, tolerates cold start)
    Each region: warm its own cache independently
    
  S3 Cross-Region Replication:
    S3 bucket in us-east-1 → auto-replicated to eu-west-1, ap-southeast-1
    Objects: available in all regions (CDN origin resilience)

DEPLOYMENT LAYER:
  CI/CD: deploy to ONE region first (canary), then others
  CodePipeline: Sequential cross-region deployment pipeline
  Stage: us-east-1 → (bake 30 min) → eu-west-1 → (bake 30 min) → ap-southeast-1
  Rollback: stop pipeline if error rate > threshold in any region
```

---

### 🔄 How It Connects (Mini-Map)

```
Geo-Replication         Active-Active / Active-Passive
(data layer)            (traffic pattern)
        │                       │
        └───────────┬───────────┘
                    ▼ (the complete architecture)
     Multi-Region Architecture ◄──── (you are here)
     (traffic + compute + data across regions)
                    │
                    ▼
           Disaster Recovery
           (multi-region enables the DR capability)
```

---

### 💻 Code Example

**Terraform: multi-region infrastructure with provider aliases:**

```hcl
# providers.tf: define AWS providers for each region
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
provider "aws" {
  alias  = "eu_west_1"
  region = "eu-west-1"
}
provider "aws" {
  alias  = "ap_southeast_1"
  region = "ap-southeast-1"
}

# Deploy ECS Fargate service to each region using module:
module "app_us" {
  source    = "./modules/app-service"
  providers = { aws = aws.us_east_1 }
  region    = "us-east-1"
  db_endpoint = module.aurora_global.primary_endpoint
}

module "app_eu" {
  source    = "./modules/app-service"
  providers = { aws = aws.eu_west_1 }
  region    = "eu-west-1"
  db_endpoint = module.aurora_global.eu_reader_endpoint
}

# Route53 Geolocation routing with health checks:
resource "aws_route53_record" "api_eu" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"
  set_identifier = "eu"
  
  geolocation_routing_policy {
    continent = "EU"
  }
  
  health_check_id = aws_route53_health_check.eu.id
  
  alias {
    name                   = module.app_eu.alb_dns_name
    zone_id                = module.app_eu.alb_zone_id
    evaluate_target_health = true
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Multi-AZ and Multi-Region are equivalent | Multi-AZ: redundancy within ONE region across different data centres in the same city (same metropolitan area). Multi-Region: redundancy across geographically separate regions (different countries or continents). An AWS regional outage takes down ALL AZs in that region simultaneously — Multi-AZ does not protect against this |
| Multi-region doubles your cost | Multi-region typically costs 2-3x, not 2x. Additional costs include: inter-region data transfer fees, replication overhead, more complex monitoring and tooling, and additional engineering/on-call overhead. Always calculate total cost including operational overhead, not just infrastructure |
| You need multi-region from day one | Most startups should start single-region. Multi-region adds significant complexity that slows development. Add multi-region when: (a) you have real global users who experience unacceptable latency, (b) you have a contractual SLA requiring regional outage protection, (c) regulatory requirements mandate it |
| Multi-region makes your system consistently consistent | Multi-region with async replication means regional copies lag. Reads from a regional replica may be stale. Distributed consistency requires careful design — multi-region is eventually consistent for most data unless you use synchronous multi-region writes (which adds latency) |

---

### 🔥 Pitfalls in Production

**Deployment without regional coordination — partial rollout breaks consistency:**

```
PROBLEM: Rolling deployment across regions without coordination

  Multi-region: 3 regions (us, eu, ap)
  Deployment pipeline: deploy all 3 regions simultaneously
  
  New feature: changes REST API response format
    Old: { "price": 10.00 } (float)
    New: { "price": "10.00", "currency": "USD" } (string + currency field)
  
  Deployment in progress:
    us-east-1: deployed new version (returns new format)
    eu-west-1: deploying (mixed old/new instances)
    ap-southeast-1: old version (returns old format)
    
  Cross-region calls during deployment:
    EU frontend (new version) → calls US API (new format): OK
    AP frontend (old version) → calls AP API (old format): OK
    AP frontend (old version) → Global Accelerator routes to EU API (new format): BROKEN
      JSON parse error: expected float, got string
    
  User impact: AP users randomly get broken responses (intermittent error)
  Debugging: difficult (intermittent, cross-region)
  
FIX 1: Sequential regional deployment with bake time
  Deploy to ONE region first → monitor for 30 minutes → deploy next region.
  If errors detected: stop pipeline, rollback deployed region.
  Feature flagged off globally until all regions deployed: then flip globally.
  
FIX 2: API versioning (backward compatibility)
  Old version: /api/v1/products → {price: 10.00}
  New version: /api/v2/products → {price: "10.00", currency: "USD"}
  Deploy: both v1 and v2 endpoints coexist
  Migration: clients migrate to v2 at their own pace
  No coordination required: old clients still work during rollout

FIX 3: Contract testing (consumer-driven contracts)
  Pact: generates API contracts between producer (backend) and consumers (frontends).
  CI pipeline: new backend version must pass all consumer contract tests before deploy.
  Incompatible change: contract test fails → pipeline blocked → no bad deploy.
```

---

### 🔗 Related Keywords

- `Geo-Replication` — the data layer of multi-region; keeps regional databases in sync
- `Active-Active` — all regions handle live traffic; highest tier of multi-region
- `Active-Passive` — simpler multi-region pattern; one active, one on standby
- `Disaster Recovery` — multi-region enables DR; DR is the reason for multi-region
- `Load Balancing` — GeoDNS + Global Accelerator route users to nearest region

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Compute + data + traffic across multiple  │
│              │ regions: fault isolation + low latency    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Regional outage unacceptable; global user │
│              │ base; data sovereignty compliance         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Early-stage product; small team; add when │
│              │ single-region limitations are proven      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Global bank branches: serve locally,     │
│              │  stay open when HQ floods."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Active-Active → Geo-Replication           │
│              │ → Disaster Recovery                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're architecting a multi-region system where each region must operate independently during an inter-region network partition (cells architecture). Your application has two types of state: (a) user session state (can be local per region, session loss on regional failover is acceptable), and (b) user wallet balance (must be globally consistent, cross-region reads must reflect latest writes). Design the data architecture that satisfies both requirements simultaneously in a 3-region active-active system.

**Q2.** Your multi-region system (us-east-1 + eu-west-1) experiences a "grey failure": eu-west-1 is not down, but it has elevated error rates (30% of requests failing) and high latency (P99 = 8 seconds). Route53 health checks are passing (the /health endpoint still returns 200 because the health check is too simple). Design a health check strategy that detects grey failures and triggers automatic regional failover before users experience significant degradation. What specific metrics should the health check monitor, and what thresholds should trigger failover?
