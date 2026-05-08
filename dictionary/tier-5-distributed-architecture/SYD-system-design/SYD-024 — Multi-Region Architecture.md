---
layout: default
title: "Multi-Region Architecture"
parent: "System Design"
nav_order: 24
permalink: /system-design/multi-region-architecture/
id: SYD-024
category: System Design
difficulty: ★★★
depends_on: Geo-Replication, Load Balancing, Disaster Recovery
used_by: Global Systems, High Availability
related: Geo-Replication, Active-Active, Sharding
tags:
  - distributed-systems
  - advanced
  - global-scale
  - disaster-recovery
  - architecture
---

# SYD-024 — Multi-Region Architecture

⚡ TL;DR — Deploying systems across multiple geographic regions simultaneously. Enables global low latency, improved reliability, and disaster recovery at data center scale.

| #699            | Category: System Design                            | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Geo-Replication, Load Balancing, Disaster Recovery |                 |
| **Used by:**    | Global Systems, High Availability                  |                 |
| **Related:**    | Geo-Replication, Active-Active, Sharding           |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Single data center (US). Global users. Japan users: 100ms latency (slow). Network issues in US? All users impacted (no geographic redundancy).

**THE BREAKING POINT:**
Global business requires: low latency for all regions, disaster recovery across continents, regulatory compliance (data residency).

**THE INVENTION MOMENT:**
"Deploy in multiple regions. Users route to nearest. Data center in each region survives continent-wide disasters."

---

### 📘 Textbook Definition

**Multi-Region Architecture:** Deploying application and data infrastructure across geographically separated regions (US, EU, Asia). Each region independently serves local users (low latency) while coordinating with other regions for global consistency, failover, and disaster recovery.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Same app/data deployed in US, EU, Asia. Users route to nearest. If one region fails, others survive.

**One analogy:**

> McDonald's with locations worldwide: (1) each location independently serves local customers, (2) supply chain syncs across regions, (3) if Tokyo burns down, NYC location still operates.

**One insight:**
Multi-region is expensive but enables truly global, resilient systems.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Each region has full infrastructure (compute, storage, networking)
2. Users routed to nearest region (low latency)
3. Data synchronized between regions (consistency challenge)
4. Each region must handle full load independently (expensive but necessary)
5. Failure of one region doesn't impact others

**DESIGN PATTERNS:**

1. **Read-Only Replicas**: Primary in one region, read replicas in others (simple, but writes go to primary)
2. **Active-Active**: All regions serve both reads and writes (complex, requires consistency)
3. **Sharded by Geography**: EU users → EU region, US users → US region (no cross-region sync needed)

**THE TRADE-OFFS:**
**Gain:** Global low latency. Geographic disaster recovery. Regulatory compliance (data residency).

**Cost:** 3-4x infrastructure (replicate in 3+ regions). Operations complexity (monitoring multiple regions). Network bandwidth (sync between regions).

---

### 🧪 Thought Experiment

**SETUP:**
Streaming video service. Users globally. Single US region.

**Single Region (Bad):**

- US users: 20ms latency (good)
- EU users: 100ms latency (poor)
- Japan users: 150ms latency (very poor)
- If US region fails: 100% downtime globally

**Multi-Region (Better):**

- US region: US users 20ms, EU users 100ms (cached from CDN), Japan users 150ms (cached from CDN)
- EU region: EU users 20ms, US users 100ms, Japan users 150ms
- Japan region: Japan users 20ms, US users 150ms, EU users 150ms
- If US fails: EU and Japan users still served (low latency from their regions)

**Trade-off:**
Cost 3x, but low latency globally + disaster recovery.

---

### 🧠 Mental Model / Analogy

> Book distribution: (1) central warehouse in NYC (single region). (2) vs. warehouses in NYC, London, Tokyo (multi-region). (3) Customers in Tokyo: warehouse in NYC has 30-day delivery. Tokyo warehouse has 2-day delivery. (4) If NYC warehouse burns, London/Tokyo warehouses still ship. (5) Cost: 3x warehouse space, but customer satisfaction much better.

- "Warehouse" → data center region
- "Customers" → end users
- "Delivery time" → latency
- "Central warehouse failing" → region outage

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
App deployed in US, EU, Japan. Each serves local users (fast). Data syncs between regions. If one region fails, others keep running.

**Level 2 — How to use it (junior developer):**
Code deployed to 3 AWS regions. Users routed by DNS to nearest region. Database replicated across regions. If us-east-1 fails, traffic reroutes to eu-west-1 and ap-southeast-1.

**Level 3 — How it works (mid-level engineer):**
Infrastructure-as-Code in each region (replicated). Global load balancer routes requests by geolocation (Route53, GeoDNS). Data replicated between regions (eventually consistent or multi-master). Monitoring alerts on regional failures. Automated failover reroutes traffic.

**Level 4 — Why it was designed this way (senior/staff):**
Multi-region evolved from need for: (1) global low latency (Netflix, YouTube, Twitch), (2) regulatory compliance (GDPR: EU data in EU), (3) disaster recovery (survive continent-scale outages). Tradeoff: cost vs. resilience. Most large tech companies: 3-4 regions minimum. Each region independent-ish (can survive alone, but inconsistency if partition).

---

### ⚙️ How It Works (Mechanism)

Multi-region architecture:

```
DEPLOYMENT TOPOLOGY:
  US-EAST Region:
    [Load Balancer] → [Web Servers] → [Cache] → [Database]

  EU-WEST Region:
    [Load Balancer] → [Web Servers] → [Cache] → [Database]

  AP-SOUTHEAST Region:
    [Load Balancer] → [Web Servers] → [Cache] → [Database]

  Global:
    [GeoDNS Router] → Routes users to nearest region

USER REQUEST FLOW:
  1. User in Tokyo makes request
  2. GeoDNS determines: Tokyo → nearest region is AP-SOUTHEAST
  3. Request routed to ap-southeast region
  4. Local servers handle request (20ms latency)
  5. Response returned

DATA SYNC BETWEEN REGIONS:
  Option A: Async Replication (Common)
    [US-EAST DB] → (1-5 sec lag) → [EU-WEST DB]
                 → (1-5 sec lag) → [AP-SOUTHEAST DB]
    Pros: Fast writes, low latency
    Cons: Eventual consistency (regions temporarily out of sync)

  Option B: Multi-Master (Complex)
    [US-EAST DB] ←→ [EU-WEST DB] ←→ [AP-SOUTHEAST DB]
    Pros: Writes in any region
    Cons: Conflicts possible (same data modified in multiple regions)

  Option C: Sharding by Geography (Simple)
    EU users write to EU-WEST DB (authoritative for EU data)
    US users write to US-EAST DB (authoritative for US data)
    No cross-region write conflicts
    Cons: Can't easily change user's "home region"

REGIONAL FAILURE HANDLING:
  US-EAST region goes down:
    1. Monitoring detects all servers in US-EAST unreachable
    2. GeoDNS updated: US traffic now routes to US-WEST
    3. Users in US reconnect, get rerouted
    4. EU/AP users unaffected (their regions still up)
    5. Data in US-EAST eventually recovered (from replicas)

EVENTUAL CONSISTENCY:
  Scenario: User writes in US, reads in EU within 1 sec
    - Write goes to US-EAST DB
    - Committed immediately
    - Replicated to EU-WEST DB (1-5 sec lag)
    - EU user reads: might get old data (not yet replicated)
    - After 5 sec: all regions consistent
```

**Regional Architecture:**

```
Each region is self-contained:
┌─────────────────────────────────────────┐
│ REGION (e.g., us-east-1)                │
├─────────────────────────────────────────┤
│ Internet Gateway (entry point)          │
│    ↓                                     │
│ Load Balancer (distribute traffic)      │
│    ↓                                     │
│ Auto-scaling web servers (7 replicas)   │
│    ↓                                     │
│ Cache Layer (Redis) [replicated]        │
│    ↓                                     │
│ Database Primary + Replicas             │
│    ↓                                     │
│ Object Storage (S3-like)                │
│    ↓                                     │
│ Outbound Replication Links to other     │
│ regions (async data sync)               │
└─────────────────────────────────────────┘

All regions have identical structure
Replicated across geographies
```

---

### 💻 Code Example

**Example 1 — Multi-Region Deployment (Terraform):**

```terraform
# Global configuration
variable "regions" {
  default = ["us-east-1", "eu-west-1", "ap-southeast-1"]
}

# Deploy to each region
module "regional_infrastructure" {
  for_each = toset(var.regions)

  source = "./modules/region"

  region                  = each.value
  instance_count          = 7  # Web servers per region
  database_replication_lag = "5s"

  # Tag for billing/monitoring
  tags = {
    Region = each.value
  }
}

# Global load balancer (Route53)
resource "aws_route53_zone" "global" {
  name = "app.company.com"
}

resource "aws_route53_record" "geolocation" {
  zone_id = aws_route53_zone.global.zone_id
  name    = "app.company.com"
  type    = "A"

  # Geolocation routing
  set_identifier = "us"
  geolocation_location {
    country = "US"
  }
  alias {
    name                   = module.regional_infrastructure["us-east-1"].load_balancer_dns
    zone_id                = module.regional_infrastructure["us-east-1"].zone_id
    evaluate_target_health = true
  }
}

# Similar for EU and Asia...
```

**Example 2 — GeoDNS Routing (Python):**

```python
from geolite2 import geolite2

class GlobalLoadBalancer:
    def __init__(self):
        self.region_endpoints = {
            'us': 'us-east-1.app.internal',
            'eu': 'eu-west-1.app.internal',
            'asia': 'ap-southeast-1.app.internal',
        }

    def get_regional_endpoint(self, user_ip):
        """Route user to nearest region"""
        try:
            match = geolite2.reader().get(user_ip)
            continent = match['continent']['code']

            if continent in ['NA', 'SA']:
                return self.region_endpoints['us']
            elif continent in ['EU', 'AF']:
                return self.region_endpoints['eu']
            elif continent in ['AS', 'OC']:
                return self.region_endpoints['asia']
        except:
            pass

        return self.region_endpoints['us']  # Default fallback

    def health_check_endpoints(self):
        """Monitor regional health"""
        for region, endpoint in self.region_endpoints.items():
            try:
                response = requests.get(f"http://{endpoint}/health", timeout=5)
                is_healthy = response.status_code == 200
                print(f"Region {region}: {'✓ Healthy' if is_healthy else '✗ Down'}")
            except:
                print(f"Region {region}: ✗ Unreachable")

# Usage
lb = GlobalLoadBalancer()
endpoint = lb.get_regional_endpoint('210.156.67.89')  # User in Tokyo
# Returns: 'ap-southeast-1.app.internal' (nearest region)
```

**Example 3 — Cross-Region Data Consistency:**

```python
import json
from datetime import datetime

class MultiRegionConsistency:
    def __init__(self):
        self.regions = {
            'us': {'lag': 0, 'data': {}},
            'eu': {'lag': 0, 'data': {}},
            'asia': {'lag': 0, 'data': {}},
        }

    def write(self, region, key, value):
        """Write in primary region, replicate asynchronously"""
        # 1. Write to primary
        self.regions[region]['data'][key] = value
        self.regions[region]['last_write'] = datetime.now()

        # 2. Replicate to other regions (async, with lag)
        for other_region in self.regions:
            if other_region != region:
                # Simulate replication lag (1-5 seconds)
                self.regions[other_region]['lag'] = 5  # seconds
                # In real system, async job replicates

    def read(self, region, key):
        """Read from region (may be stale if not yet replicated)"""
        if key in self.regions[region]['data']:
            lag = self.regions[region]['lag']
            return {
                'value': self.regions[region]['data'][key],
                'lag': lag,
                'note': f'Data {lag}s old from replication'
            }
        return None

    def ensure_consistency(self):
        """Reduce replication lag over time"""
        for region in self.regions:
            if self.regions[region]['lag'] > 0:
                self.regions[region]['lag'] -= 1  # Reduce lag

                # Copy any new data from primary
                for key, value in self.regions['us']['data'].items():
                    if key not in self.regions[region]['data']:
                        self.regions[region]['data'][key] = value

# Usage
consistency = MultiRegionConsistency()

# User in US writes
consistency.write('us', 'user:123', {'name': 'Alice'})

# User in EU reads immediately (might get stale)
eu_read = consistency.read('eu', 'user:123')
print(f"EU read: {eu_read}")  # May be None (not yet replicated)

# Simulate time passing, replication catching up
for _ in range(5):
    consistency.ensure_consistency()

# User in EU reads again (now consistent)
eu_read = consistency.read('eu', 'user:123')
print(f"EU read after sync: {eu_read}")  # Should have data now
```

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                 |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| "Multi-region guarantees zero downtime"       | No. Regional failures still cause user rerouting (1-30 sec downtime). Only active-active + fast failover approach zero. |
| "Multi-region eliminates all latency"         | No. Inter-region replication has latency. Users far from all regions still have high latency.                           |
| "Multi-region is essential for all companies" | No. Cost justified only if: global user base, high-uptime requirement, or regulatory needs.                             |
| "All data must replicate across all regions"  | No. Sharding by geography avoids cross-region writes (simpler).                                                         |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Cascading Failure Across Regions**

**Symptom:**
US-EAST fails. Traffic reroutes to EU-WEST. EU-WEST becomes overloaded (not sized for 2x traffic), fails. Then AP-SOUTHEAST overloaded. Cascading failure across all regions.

**Prevention:**
Size each region to handle full global load independently. Or implement graceful degradation (reject low-priority traffic if overloaded).

---

**Failure Mode 2: Data Corruption Replicates to All Regions**

**Symptom:**
Bug in US causes data corruption. Corrupted data replicates to EU and AP. All regions affected. Backup required.

**Prevention:**
Implement data validation during replication. Detect corruption before replicating. Keep immutable backups (different region).

---

### 🔗 Related Keywords

**Prerequisites:**

- `Geo-Replication`, `Load Balancing`, `Disaster Recovery`

**Builds On This:**

- `Sharding`, `Active-Active`, `Global Consistency`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ App deployed across multiple          │
│              │ geographic regions                    │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Single region: high latency for       │
│ SOLVES       │ distant users; no geographic DR      │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Expensive but enables global          │
│              │ resilience and low latency            │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Deploy everywhere, users get low     │
│              │ latency, survives region failures."   │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Multi-region system: write in US, read in EU within 1 second. Replication lag = 5 seconds. What data does EU user see? Is this acceptable?

**Q2.** You're building multi-region system. Budget allows only 2 regions (US and EU). Where should Asia traffic go? What are the tradeoffs?
