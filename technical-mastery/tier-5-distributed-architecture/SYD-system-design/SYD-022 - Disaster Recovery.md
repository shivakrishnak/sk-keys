---
id: SYD-022
title: Disaster Recovery
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-018, SYD-019, SYD-021
used_by: ""
related: SYD-018, SYD-019, SYD-020, SYD-021, SYD-023, SYD-024
tags:
  - architecture
  - reliability
  - disaster-recovery
  - operations
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/syd/disaster-recovery/
---

⚡ TL;DR - Disaster Recovery (DR) is the strategy,
architecture, and processes for restoring a system
after a catastrophic failure that takes down an entire
availability zone, region, or data center. DR is
distinct from high availability: HA handles component-
level failures (a server, a pod); DR handles site-
level failures (an entire AZ or region). RTO and RPO
define the DR requirement; the architecture (cold/warm/
hot standby or active-active multi-region) delivers it.

| #022 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | RTO / RPO, Redundancy and Failover, Active-Passive | |
| **Used by:** | (terminal - builds on all HA concepts) | |
| **Related:** | RTO / RPO, Redundancy and Failover, Active-Passive, Active-Active, Geo-Replication, Multi-Region Architecture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
AWS us-east-1 has a major outage. Every service running
in us-east-1 goes down simultaneously. Teams scramble
to figure out what to do. There is no DR plan. They
begin manually standing up infrastructure in us-west-2
from scratch, restoring databases from S3 backups,
reconfiguring DNS, and testing. The process takes
14 hours. 14 hours of total downtime for every customer.

**THE BREAKING POINT:**
HA (replicas within the same region) does not protect
against a region-wide failure. AWS has had multi-hour
region outages (us-east-1: 2011, 2012, 2017, 2021).
A business that needs < 4-hour RTO cannot rely on a
single-region deployment. DR requires explicitly
designing for the scenario where an entire region
becomes unavailable.

---

### 📘 Textbook Definition

**Disaster Recovery (DR):** The set of policies,
tools, and procedures designed to enable the recovery
of technology infrastructure and systems after a
natural or human-induced disaster. In distributed
systems, DR specifically addresses site-level failures
(entire AZ, region, or data center becomes unavailable).
DR architecture is defined by two parameters: RTO
(maximum acceptable downtime) and RPO (maximum
acceptable data loss). The DR strategy choices are:
Cold standby (backup + restore), Warm standby (reduced-
capacity secondary always running), Hot standby (full-
capacity secondary, automated failover), and Active-
Active (all sites serving traffic, no failover needed).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DR is the plan and architecture for surviving a
complete site failure (entire region goes down).
RTO and RPO determine how much to spend on it.

**One analogy:**
> A city's emergency response plan for a major
> earthquake:
> - Cold standby: all city functions stop; rebuild
>   from scratch after the quake (weeks)
> - Warm standby: essential services (hospitals,
>   power) are partially pre-positioned outside
>   the city; can restore in hours
> - Hot standby: a shadow city is kept ready in
>   another location with everything needed; restore
>   in minutes
> - Active-active: government functions operate
>   from multiple cities simultaneously; residents
>   barely notice the primary city going down
>
> Each tier costs more to maintain but enables faster
> recovery. Which tier to choose depends on how long
> residents can wait.

---

### 🔩 First Principles Explanation

**THE FOUR DR TIERS:**

```
┌────────────────────────────────────────────────────────┐
│ TIER 4: COLD STANDBY                                   │
│ RTO: hours to days | RPO: hours to days                │
│ Architecture:                                          │
│   - Regular backups to cross-region object storage     │
│   - No infrastructure running in DR region             │
│   - Recovery: provision infra + restore from backup    │
│ Cost: Lowest ($storage only)                          │
│ Use case: Dev/test, internal tools, batch jobs        │
│                                                        │
│ Limitation: RTO dominated by infrastructure           │
│ provisioning time (~30-60 min) + restore time.        │
│ Not suitable for any customer-facing system.          │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ TIER 3: WARM STANDBY                                   │
│ RTO: 15 min to 1 hour | RPO: minutes                  │
│ Architecture:                                          │
│   - Secondary region with reduced-capacity infra       │
│   - Data replicated continuously (async)               │
│   - On disaster: scale up + redirect traffic           │
│ Cost: 20-50% extra vs primary region                  │
│ Use case: Internal business systems, B2B SaaS         │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ TIER 2: HOT STANDBY                                    │
│ RTO: < 15 minutes | RPO: seconds                      │
│ Architecture:                                          │
│   - Full-capacity secondary always running             │
│   - Synchronous or near-sync replication               │
│   - Automated failover via DNS/load balancer           │
│ Cost: 2x primary region (full duplicate)              │
│ Use case: Customer-facing SaaS, e-commerce            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ TIER 1: ACTIVE-ACTIVE MULTI-REGION                     │
│ RTO: ~0 | RPO: 0 (or near-zero)                      │
│ Architecture:                                          │
│   - Both regions serve production traffic              │
│   - Global load balancer (anycast, GeoDNS)             │
│   - Consensus-based writes or partitioned writes       │
│ Cost: 2x+ all regions (no "standby" = idle)           │
│ Use case: Financial systems, global consumer apps     │
└────────────────────────────────────────────────────────┘
```

**DR VERSUS HA - THE DISTINCTION:**

```
High Availability (HA):           Disaster Recovery (DR):
│ Scope: component or AZ     │    Scope: region or site
│ Failure: single server,    │    Failure: full region
│   single AZ outage         │      (AWS us-east-1 down)
│ RTO: seconds to minutes    │    RTO: minutes to hours
│ Mechanism: load balancer   │    Mechanism: region
│   removes failed node;     │      failover; DNS/BGP
│   replica promoted         │      update; data sync
│ Always-on                  │    Tested quarterly
│ Invisible to users         │    May cause brief outage
```

**THE TRADE-OFFS:**

**Cost vs RTO/RPO:** Each tier of DR improvement
roughly 5-10x increases cost and operational
complexity.

**Active-Active vs Hot Standby:** Active-active
eliminates the RTO at the cost of multi-region write
coordination (hard for stateful services).

**Test frequency:** Untested DR plans fail in real
disasters. The plan degrades as the system changes.
Quarterly DR drills are the only way to validate.

---

### 🧪 Thought Experiment

**SCENARIO: Netflix-style DR**

Netflix runs active-active in multiple AWS regions
(us-east-1, eu-west-1, etc.). How do they achieve
this for stateful content?

**Read path (video streaming):**
Videos are pre-positioned in CDN edge nodes globally.
A region outage does not affect CDN delivery.
CDN is inherently active-active.

**Write path (user watch history, billing):**
These are eventually consistent, sharded globally.
Writes go to a regional primary; replicate to other
regions asynchronously. On region failure: a few
minutes of watch history might not be in the DR
region. Business decision: losing 5 minutes of
watch history on a Netflix account is acceptable
during a DR event. RPO = 5 minutes for watch history.
Billing (RPO = 0): different system, synchronous
replication.

**The service decomposition insight:**
Not all data has the same DR requirements. Decompose
the system by business criticality:
- Payment/billing: RPO = 0, RTO < 5 min → active-active
- Watch history: RPO = 5 min, RTO < 30 min → warm/hot standby
- Recommendation engine: RPO = 1 day, RTO = 1 hour → cold
This is how Netflix runs on AWS: different tiers of
DR for different services within the same company.

---

### 🧠 Mental Model / Analogy

> DR tiers are like building materials:
> - Cold standby = tent: cheap to store, slow to
>   set up, minimal protection
> - Warm standby = portable building: some assembly
>   required, functional quickly, reasonable cost
> - Hot standby = pre-built house at another location:
>   expensive, but move in within hours
> - Active-active = living in two homes simultaneously:
>   you are always in both places; neither going offline
>   disrupts your life (very expensive)
>
> You would not store critical medications in a tent
> or keep a second home purely for disaster preparedness
> unless the cost was justified by the criticality of
> the contents.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
DR is the plan for keeping the business running when
a major failure happens (entire data center goes down).
Like a fire escape plan for your data.

**Level 2 - How to use it (junior developer):**
Every service should have documented RTO and RPO
targets. For each service: backups must be tested
(can you restore? how long does it take?). Runbooks
must exist for each failure scenario. Run a DR drill
at least once a year.

**Level 3 - How it works (mid-level engineer):**
DR architecture matches RTO/RPO targets. For RTO < 1
hour: need warm standby (infrastructure running in
DR region, data synced). For RTO < 15 min: hot standby
with automated failover. For RTO ≈ 0: active-active.
Each tier adds significant infrastructure cost and
operational complexity.

**Level 4 - Why it was designed this way (senior/staff):**
DR runbooks decay. Every code change, infrastructure
change, and team change makes the DR plan slightly
less accurate. Teams that do not practice DR fail
catastrophically when they need it. The solution:
chaos engineering / Game Days. Netflix's Chaos Monkey
was invented specifically because the team realized
they could not trust their HA setup without actively
testing it in production. Automated chaos tests
(random instance termination) ensure that HA/DR
mechanisms are exercised regularly.

**Level 5 - Mastery (distinguished engineer):**
The modern insight: DR should be a normal operational
mode, not a special procedure. If you have to "declare
a disaster" before executing the failover, the process
is too manual and will be delayed by organizational
friction (who has authority to declare? which manager
must approve?). The best DR architectures do not have
a "disaster" concept: traffic is continuously routed
around failing regions via health-check-driven global
load balancers. The system self-heals; operators are
notified after the fact. "DR" becomes the normal
failure-handling path, just at a larger scale.

---

### ⚙️ How It Works (Mechanism)

**Warm Standby DR for a web application:**

```
┌─────────────────────────────────────────────────────────┐
│ PRIMARY REGION (us-east-1) - Normal state              │
│                                                         │
│  Route53 → ALB → EC2 Auto Scaling Group (3 nodes)      │
│                          │                              │
│                    RDS Primary ←── S3 backups           │
│                          │                              │
│                    async replication                    │
│                          │                              │
│ DR REGION (us-west-2) - Warm standby                   │
│                                                         │
│  (ALB + 1 EC2 node - min capacity running)             │
│                          │                              │
│                    RDS Read Replica ← synced            │
│                          │                              │
│ DR EVENT:                                               │
│ 1. Route53 health check detects primary ALB failing    │
│ 2. Route53 DNS failover → DR ALB (propagates in <60s) │
│ 3. DR Auto Scaling Group scales up to full capacity   │
│ 4. DR RDS read replica promoted to primary            │
│ 5. Application in DR region connects to promoted DB   │
│                                                         │
│ Total RTO: ~15-20 min                                  │
│ RPO: async replication lag (typically < 1 min)         │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Route53 health check DR failover config**
```terraform
# Route53 failover routing policy:
# Primary: us-east-1 ALB
# Failover: us-west-2 ALB

# Health check for primary region
resource "aws_route53_health_check" "primary" {
  fqdn              = "alb.us-east-1.myapp.com"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3   # 3 failures before failover
  request_interval  = 10  # check every 10s
  # Detection time: 3 × 10 = 30 seconds
}

# Primary DNS record (failover type: PRIMARY)
resource "aws_route53_record" "primary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.myapp.com"
  type    = "A"

  alias {
    name    = aws_lb.us_east_1.dns_name
    zone_id = aws_lb.us_east_1.zone_id
    evaluate_target_health = false
  }

  failover_routing_policy {
    type = "PRIMARY"
  }
  health_check_id = aws_route53_health_check.primary.id
  set_identifier  = "primary"
}

# DR DNS record (failover type: SECONDARY)
# Receives traffic when primary health check fails
resource "aws_route53_record" "dr" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.myapp.com"
  type    = "A"

  alias {
    name    = aws_lb.us_west_2.dns_name
    zone_id = aws_lb.us_west_2.zone_id
    evaluate_target_health = false
  }

  failover_routing_policy {
    type = "SECONDARY"
  }
  set_identifier = "secondary"
  # No health_check_id: secondary always accepts if
  # it is the only option
}
```

**Example 2 - DR runbook validation test**
```bash
#!/bin/bash
# DR drill script: validate warm standby can serve traffic
# Run quarterly. Document results. Update runbook.

set -e
DR_REGION="us-west-2"
PRIMARY_REGION="us-east-1"
TARGET_RTO_MINUTES=20

echo "=== DR Drill: $(date) ==="
echo "Simulating primary region failure..."
DRILL_START=$(date +%s)

# Step 1: Disable primary health check
# (simulates region failure without actually failing it)
aws route53 update-health-check \
    --health-check-id $PRIMARY_HC_ID \
    --disabled \
    --region us-east-1

echo "Waiting for Route53 failover to DR region..."
while true; do
    RESOLVED=$(dig +short api.myapp.com | head -1)
    DR_ALB_IP=$(dig +short alb.us-west-2.myapp.com | head -1)
    if [ "$RESOLVED" = "$DR_ALB_IP" ]; then
        break
    fi
    sleep 5
done
echo "DNS resolved to DR region."

# Step 2: Scale up DR auto-scaling group
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name myapp-asg-dr \
    --desired-capacity 3 \
    --region $DR_REGION

# Step 3: Promote DR RDS replica
aws rds promote-read-replica \
    --db-instance-identifier myapp-db-dr \
    --region $DR_REGION

# Step 4: Wait for DB promotion
until aws rds describe-db-instances \
    --db-instance-identifier myapp-db-dr \
    --region $DR_REGION \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text | grep -q "available"; do
    sleep 10
done

DRILL_END=$(date +%s)
ACTUAL_RTO=$(( (DRILL_END - DRILL_START) / 60 ))
echo "Actual RTO: ${ACTUAL_RTO} minutes (
    target: ${TARGET_RTO_MINUTES})"

# Step 5: Smoke test
curl -sf https://api.myapp.com/health | python3 -m json.tool

# Step 6: Re-enable primary (end drill)
aws route53 update-health-check \
    --health-check-id $PRIMARY_HC_ID \
    --no-disabled \
    --region us-east-1
echo "DR drill complete."
```

---

### ⚖️ Comparison Table

| DR Tier | RTO | RPO | Cost Multiplier | Managed Tool Examples |
|---|---|---|---|---|
| Cold standby | Hours-days | Hours | 1.1x | S3 backups, AMI snapshots |
| Warm standby | 15-60 min | Minutes | 1.3-1.5x | AWS Elastic DR, Azure Site Recovery |
| Hot standby | < 15 min | Seconds | 1.8-2x | RDS Multi-Region, Route53 failover |
| Active-active | ~0 | ~0 | 2x+ | CockroachDB, Spanner, CloudFront + S3 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Backups = disaster recovery | Backups are a component of cold-standby DR. Restoring from backup typically takes hours. If your RTO is less than 4 hours, backups alone are insufficient. |
| DR only matters for large companies | Any company with revenue-dependent systems needs DR. The question is: what is the cost of downtime? If one hour of downtime costs more than the warm-standby DR infrastructure (typically 30-50% extra), DR investment is positive ROI. |
| Untested DR plans work | DR plans decay as systems change. A plan that worked 6 months ago may fail today due to infrastructure changes, key personnel leaving, or dependency changes. Quarterly drills are the minimum. |

---

### 🚨 Failure Modes & Diagnosis

**DR Region Has Stale Configuration**

**Symptom:**
A region failure occurs. Team fails over to DR region.
Application starts, but authentication fails for all
users. DR is "working" but unusable.

**Root Cause:**
Three months ago, the team rotated the JWT signing
key. They updated the primary region's secret store.
They did not update the DR region's secret store.
The application in DR is using the old key and cannot
validate tokens issued in the past 3 months.

**Prevention:**
```bash
# Automated config drift detection
# Run as part of CI/CD pipeline when any
# secret or config changes

# Compare primary vs DR config/secrets
PRIMARY_SECRETS=$(aws secretsmanager list-secrets \
    --region us-east-1 \
    --query 'SecretList[*].{Name:Name,LastChanged:LastChangedDate}' \
    --output json)

DR_SECRETS=$(aws secretsmanager list-secrets \
    --region us-west-2 \
    --query 'SecretList[*].{Name:Name,LastChanged:LastChangedDate}' \
    --output json)

# Alert if any secret in primary was updated
# more recently than the same secret in DR
python3 compare_secrets.py \
    --primary "$PRIMARY_SECRETS" \
    --dr "$DR_SECRETS" \
    --alert-on-drift
```

**Lesson:**
DR is not just about data and infrastructure. Every
configuration, secret, SSL certificate, and IAM role
must be synchronized. Treat configuration as data:
replicate it, version it, and validate it in DR drills.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `RTO / RPO` - the business requirements that define
  which DR tier to build
- `Active-Passive` - the base pattern that most DR
  strategies are built on

**Builds On This (learn these next):**
- `Geo-Replication` - the data replication mechanism
  that makes low-RPO DR possible across regions
- `Multi-Region Architecture` - the full architecture
  pattern for active-active DR

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Recovery from site-level failure        │
│               │ (region/data center goes down)          │
├───────────────┼─────────────────────────────────────────┤
│ DR != HA      │ HA = component failure (a server/pod)   │
│               │ DR = site failure (entire region)       │
├───────────────┼─────────────────────────────────────────┤
│ TIERS         │ Cold (hours) → Warm (15-60m) →          │
│               │ Hot (<15m) → Active-Active (~0)         │
├───────────────┼─────────────────────────────────────────┤
│ INPUTS        │ RTO + RPO per service → DR tier         │
├───────────────┼─────────────────────────────────────────┤
│ CRITICAL RULE │ Test DR quarterly. Untested DR fails.   │
├───────────────┼─────────────────────────────────────────┤
│ EASY MISTAKE  │ Updating config in primary but not DR   │
│               │ → DR works technically but fails logic  │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "DR is the plan for when an entire      │
│               │  region goes down. RTO drives which     │
│               │  tier to build; drills prove it works." │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Geo-Replication → Multi-Region Arch     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. DR handles site failures (entire region); HA handles
   component failures (a server). Different scope,
   different architecture.
2. Four tiers: Cold (hours RTO) → Warm (60min) →
   Hot (15min) → Active-Active (0). Each tier costs
   significantly more.
3. Untested DR plans fail. Run quarterly drills.
   Configuration drift (secrets, certs, IAM roles)
   is the most common hidden DR failure.

**Interview one-liner:**
"Disaster Recovery is the strategy for surviving a
complete site or region failure - distinct from HA which
handles component failures. DR architecture is defined
by RTO and RPO: cold standby (backup + restore, hours
RTO) → warm standby (replica running at low capacity,
15-60 min RTO) → hot standby (full capacity, automated
failover, < 15 min) → active-active (no failover needed,
~0 RTO). The critical operational requirement: test DR
quarterly. Untested DR plans fail when needed most,
often due to configuration drift that is invisible until
the failover is attempted."
