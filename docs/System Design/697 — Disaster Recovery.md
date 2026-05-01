---
layout: default
title: "Disaster Recovery"
parent: "System Design"
nav_order: 697
permalink: /system-design/disaster-recovery/
number: "697"
category: System Design
difficulty: ★★★
depends_on: "RTO / RPO, Active-Passive, Redundancy / Failover"
used_by: "Geo-Replication, Multi-Region Architecture"
tags: #advanced, #reliability, #cloud, #architecture, #foundational
---

# 697 — Disaster Recovery

`#advanced` `#reliability` `#cloud` `#architecture` `#foundational`

⚡ TL;DR — **Disaster Recovery (DR)** is the planning, infrastructure, and procedures to restore systems after a catastrophic failure (region outage, data corruption, ransomware); DR tier selection is driven by RTO and RPO business requirements.

| #697 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | RTO / RPO, Active-Passive, Redundancy / Failover | |
| **Used by:** | Geo-Replication, Multi-Region Architecture | |

---

### 📘 Textbook Definition

**Disaster Recovery (DR)** is the process, policies, and procedures for enabling the recovery or continuation of technology infrastructure and systems following a natural or human-induced disaster. Unlike high availability (HA) — which handles routine component failures within a region — DR addresses catastrophic scenarios affecting an entire region or data centre: fires, floods, power grid failures, regional cloud outages, ransomware, accidental mass deletion, and extended regional outages. DR is characterised by its **Recovery Time Objective (RTO)** and **Recovery Point Objective (RPO)**, which drive the choice of DR tier: cold standby (backup and restore), warm standby (pilot light), hot standby (active-passive cross-region), or multi-site active-active. A **DR plan** documents: who declares a disaster, how failover is executed, how data integrity is verified, how failback to the original region is performed, and how frequently the DR plan is tested.

---

### 🟢 Simple Definition (Easy)

DR is your plan for "what if everything in our primary data centre goes dark?" HA handles one server failing. DR handles the whole building burning down. It requires: a copy of your data somewhere else (replication or backups), a way to run your services somewhere else (standby infrastructure), and a runbook for how to execute the switch.

---

### 🔵 Simple Definition (Elaborated)

A cloud region goes down (happened to AWS us-east-1 in December 2021). Without DR: every service in us-east-1 is gone for hours. With a warm standby in us-west-2: promote the standby database, spin up app servers, update DNS — service restored in 30-60 minutes. With active-active: traffic already flowing to us-west-2 — zero impact. DR is the combination of: (1) data durability across regions, (2) standby infrastructure, and (3) tested runbooks for the recovery process.

---

### 🔩 First Principles Explanation

**DR tiers and their cost-availability trade-offs:**

```
DISASTER RECOVERY TIERS (AWS Well-Architected):

TIER 1: BACKUP AND RESTORE (Cold Standby)
  RTO: 1-24 hours | RPO: 1-24 hours
  Cost: Very low (storage only, ~$200-500/month)
  
  Architecture:
    Primary (us-east-1): running normally
    Backups: daily snapshots → S3 cross-region replication → DR region bucket
    DR infrastructure: none (provision on demand during disaster)
    
  Recovery procedure (disaster declared):
    1. Provision new VPC + networking in DR region (CloudFormation)
    2. Restore RDS snapshot to new database (1-4 hours)
    3. Launch EC2 instances from AMI
    4. Update DNS to DR endpoints
    5. Smoke test
    
  Use: internal tools, dev environments, batch processing
  Risk: long recovery time is accepted by business

TIER 2: PILOT LIGHT (Minimal Warm Standby)
  RTO: 30-60 minutes | RPO: minutes
  Cost: Low (~$500-2,000/month for pilot light components)
  
  Architecture:
    Primary (us-east-1): running full capacity
    DR (us-west-2): pilot light only:
      - DB: Read replica (async replication, 1-60 min lag)
      - EC2/ECS: no instances running (AMIs stored, can launch quickly)
      - Networking: VPC + subnets pre-created
      - Load balancer: pre-created, no targets
      
  Recovery procedure:
    1. Promote DB read replica → primary (2-5 min)
    2. Launch app servers from AMIs (5-10 min)
    3. Register instances with LB (2 min)
    4. Update DNS → DR LB endpoint (1-5 min propagation)
    5. Scale up: increase instance count to full capacity
    Total: 20-40 minutes
  
  Use: most business-critical web applications

TIER 3: WARM STANDBY
  RTO: 5-30 minutes | RPO: seconds to minutes
  Cost: Moderate (~$2,000-8,000/month for reduced-capacity DR)
  
  Architecture:
    Primary (us-east-1): full production capacity
    DR (us-west-2): reduced capacity (e.g., 25% of production)
      - DB: read replica or Aurora secondary (continuously synced)
      - App: minimum scaled-down fleet (can serve degraded traffic)
      - LB: running, receiving no external traffic normally
      
  Recovery procedure:
    1. Promote DB replica → primary (2-5 min)
    2. Scale up app fleet to full capacity (5-10 min)
    3. DNS failover: Route53 health check triggers automatically
    Total: 5-15 minutes (partially automated)
    
  Degraded mode: DR region can serve traffic at reduced capacity immediately,
  scale to full within 10 minutes.
  
  Use: e-commerce, SaaS applications with business continuity requirements

TIER 4: HOT STANDBY (Multi-Site Active-Passive)
  RTO: < 5 minutes | RPO: seconds
  Cost: High (~$8,000-20,000/month for full-capacity DR)
  
  Architecture:
    Primary (us-east-1): full capacity, all traffic
    DR (eu-west-1): full capacity, zero traffic
    DB: synchronous replication or Aurora Global Database
    
  Recovery procedure:
    1. DNS failover: automated (Route53 health check + low TTL)
    2. DB failover: Aurora Global managed failover (<60 seconds)
    3. Total: 2-5 minutes (mostly automated)
    
  Use: financial services, critical B2B platforms, healthcare

TIER 5: ACTIVE-ACTIVE (Multi-Site)
  RTO: ~0 | RPO: ~0
  Cost: Highest (~$20,000-50,000+/month)
  
  Architecture: see Active-Active keyword
  Both regions: serving live traffic simultaneously
  Failure: traffic rerouted, no failover needed
  
  Use: global financial systems, safety-critical applications

DR DECLARATION CRITERIA:
  Not every outage requires a DR declaration.
  
  Criteria for DR declaration (example):
  1. Primary region unavailable > 30 minutes with no ETA from cloud provider
  2. Data corruption affecting production database
  3. Security incident requiring immediate isolation of primary region
  4. Primary region health check failing for > 15 minutes (automated trigger)
  
  DR declaration process:
  1. On-call identifies criteria met → pages DR team lead
  2. DR team lead: confirms criteria, declares disaster
  3. Incident commander: coordinates cross-team execution
  4. DR runbook: step-by-step execution with time checkpoints
  5. Communications: update status page, notify enterprise customers

FAILBACK:
  Often overlooked — returning to primary region after disaster is resolved.
  
  Challenges:
  1. DR region has accumulated new data (writes since failover)
  2. Primary region restored but with pre-disaster data state
  3. Must sync DR → primary (reverse replication)
  4. Must coordinate failback timing (avoid double writes)
  5. Risk of data loss during failback if not careful
  
  Failback procedure:
  1. Restore primary region to functional state
  2. Set up replication: DR → Primary (reverse direction)
  3. Monitor replication until caught up
  4. Failback window: maintenance window or low-traffic period
  5. Execute failback: DNS → Primary, disable writes to DR
  6. Verify data consistency (checksums, record counts)
  7. Resume normal operations
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Disaster Recovery:
- Cloud region outage = complete business disruption for hours or days
- Data loss from catastrophic failure: months of work lost
- Regulatory penalties: GDPR, HIPAA, SOC2 require documented DR capabilities

WITH Disaster Recovery:
→ Catastrophic failures become survivable events (minutes to hours, not days)
→ Business continuity: customers barely notice a regional outage
→ Compliance: documented DR plan satisfies regulatory requirements

---

### 🧠 Mental Model / Analogy

> City emergency management. A city plans for catastrophic events (earthquake, flood, fire). Plans include: backup power (generators), emergency water (tanks), evacuation routes (runbooks), and a backup city hall location (warm standby). The plan sits dormant most of the time. When a disaster strikes, the plan is executed: city hall moves to backup location, utilities run on generators. Regular drills ("fire drills") test whether the plan actually works. Without the plan: chaos. With the plan: structured, practiced response.

"City emergency plan" = DR plan and runbooks
"Backup city hall location" = DR region standby infrastructure
"Regular drills" = DR testing and fire drills
"Generator power" = redundant infrastructure in DR region
"Evacuation routes" = failover procedures (DNS, LB, DB promotion)

---

### ⚙️ How It Works (Mechanism)

**AWS DR architecture with Aurora Global Database:**

```
PRIMARY REGION (us-east-1):
  VPC: 10.0.0.0/16
  ALB → ECS Fargate (10 tasks) → Aurora Primary Cluster
  Route53: api.example.com → ALB (TTL=60)
  CloudWatch: monitors primary health
  Route53 Health Check: checks /health every 10s
  
DR REGION (eu-west-1):
  VPC: 10.1.0.0/16
  ALB (created, no targets) → ECS Fargate (0 tasks — scales to 10 on failover)
  Aurora Global Secondary Cluster (read-only, synced from primary, lag < 1s)
  Route53: api-dr.example.com → DR ALB (internal, not live)
  
FAILOVER PROCEDURE (automated + manual steps):
  T+00: Route53 health check fails (primary unhealthy for 3 consecutive checks = 30s)
  T+30: Route53 DNS failover: api.example.com → DR ALB
        [DNS propagation: 60s due to TTL=60]
  T+30: Parallel: Aurora Global failover initiated (managed)
        aurora: promote eu-west-1 secondary cluster to primary
        Managed failover: ~60 seconds
  T+90: DR region receiving traffic. DB: read-only (Aurora still failing over)
        Application: returns 503 for write operations during 60s DB failover
  T+120: Aurora eu-west-1 promoted. Full read-write capability restored.
  
  Total RTO: ~2 minutes (120 seconds)
  RPO: < 1 second (Aurora Global replication lag typically < 1s)
```

---

### 🔄 How It Connects (Mini-Map)

```
High Availability (HA)           RTO / RPO
(single-region component         (time/data targets for recovery)
 failure handling)
        │                               │
        └───────────────┬───────────────┘
                        ▼ (cross-region catastrophic failure handling)
                Disaster Recovery ◄──── (you are here)
                        │
                ┌───────┴────────┐
                ▼                ▼
        Geo-Replication    Multi-Region Architecture
        (data layer DR)    (compute + traffic layer DR)
```

---

### 💻 Code Example

**DR runbook automation with AWS Systems Manager (SSM) document:**

```yaml
# AWS SSM Document: automated DR failover procedure
schemaVersion: "2.2"
description: "Execute DR failover from us-east-1 to eu-west-1"

mainSteps:
  # Step 1: Verify DR region readiness
  - name: VerifyDRReadiness
    action: aws:executeAwsApi
    inputs:
      Service: rds
      Api: DescribeGlobalClusters
      GlobalClusterIdentifier: orders-global-cluster
    outputs:
      - Name: GlobalClusterStatus
        Selector: "$.GlobalClusters[0].Status"
    nextStep: PromoteAuroraGlobal
    
  # Step 2: Promote Aurora Global secondary to primary
  - name: PromoteAuroraGlobal
    action: aws:executeAwsApi
    inputs:
      Service: rds
      Api: FailoverGlobalCluster
      GlobalClusterIdentifier: orders-global-cluster
      TargetDbClusterIdentifier: "arn:aws:rds:eu-west-1:account:cluster:orders-dr"
      AllowDataLoss: false     # managed failover, not forced
    nextStep: WaitForPromotion
    
  # Step 3: Wait for Aurora promotion
  - name: WaitForPromotion
    action: aws:waitForAwsResourceProperty
    inputs:
      Service: rds
      Api: DescribeGlobalClusters
      GlobalClusterIdentifier: orders-global-cluster
      PropertySelector: "$.GlobalClusters[0].Status"
      DesiredValues: ["available"]
    timeoutSeconds: 300
    nextStep: UpdateDNS
    
  # Step 4: Update DNS to DR endpoint
  - name: UpdateDNS
    action: aws:executeScript
    inputs:
      Runtime: "python3.11"
      Handler: update_dns
      Script: |
        def update_dns(events, context):
            import boto3
            route53 = boto3.client('route53')
            route53.change_resource_record_sets(
                HostedZoneId=events['HostedZoneId'],
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': 'api.example.com',
                            'Type': 'A',
                            'TTL': 60,
                            'ResourceRecords': [
                                {'Value': events['DRAlbIp']}
                            ]
                        }
                    }]
                }
            )
            return {'status': 'DNS_UPDATED'}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DR is only for catastrophic natural disasters | Most DR activations are for: cloud provider outages, software bugs causing data corruption, ransomware/security incidents, and operator errors (accidental deletion). Natural disasters are rare; operational failures are common. DR must address all scenarios |
| Multi-AZ deployment IS disaster recovery | Multi-AZ (e.g., RDS Multi-AZ) is high availability within a region — it handles AZ-level failures. True DR requires cross-region capability to survive complete regional outages. Many organisations confuse these two levels |
| Untested DR plans are acceptable if documented | An untested DR plan is not a DR plan. Infrastructure changes, application updates, and configuration drift make documented-but-untested plans fail in practice. Regular DR testing is essential. If you haven't failed over to DR in the last year, assume your DR doesn't work |
| DR failover and failback are symmetric operations | Failover (primary → DR): well-practised, usually automated. Failback (DR → primary): rarely practised, often manual, requires data synchronisation in the reverse direction, higher risk of data loss. Always have a tested failback procedure |

---

### 🔥 Pitfalls in Production

**DR test reveals undiscovered dependencies — service won't start in DR:**

```
COMMON DR TEST FAILURE PATTERN:

  Documented DR: all services in us-east-1 can run in eu-west-1.
  First DR test: some services fail to start in DR.
  
  Root causes discovered during test:
  
  1. HARDCODED ENDPOINTS:
     Config: database.host=orders-db.us-east-1.rds.amazonaws.com (hardcoded)
     DR region: database is orders-db-dr.eu-west-1.rds.amazonaws.com
     Fix: use CNAME (orders-db.internal) or AWS parameter store
     
  2. CROSS-REGION API CALLS:
     payment-service calls third-party KYC API at fixed IP: 203.0.113.1
     KYC provider: only allows requests from us-east-1 NAT gateway IPs
     DR region: different NAT gateway IPs → KYC rejects all requests
     Fix: register DR region IPs with KYC provider in advance
     
  3. MISSING AMI IN DR REGION:
     EC2 launch template: references AMI ami-0abc123 (us-east-1 only)
     AMI not copied to eu-west-1
     Fix: AMI cross-region copy pipeline (automate on every release)
     
  4. SECRETS IN WRONG REGION:
     AWS Secrets Manager: secrets only in us-east-1
     Application in DR: cannot retrieve secrets → startup failure
     Fix: replicate secrets to DR region (Secrets Manager cross-region replication)
  
  5. DATA VOLUME MUCH LARGER THAN EXPECTED:
     Expected restore time: 30 minutes (based on 6-month-old estimate)
     Actual data size: 10x larger (fast-growing product)
     Actual restore time: 5+ hours
     Fix: regular DR testing + update RTO targets based on actual data size
  
DR TESTING PROGRAMME:
  
  MONTHLY: Tabletop exercise (review runbooks, walk through steps mentally)
  QUARTERLY: Partial DR test (restore backup to isolated DR environment)
  SEMI-ANNUALLY: Full DR test (production failover, limited customer impact)
  ANNUALLY: Full DR test with customer communication
  
  After each test: update runbook, fix discovered gaps, update RTO/RPO estimates.
  DR health metric: "Time since last successful DR test" → alert if > 90 days.
```

---

### 🔗 Related Keywords

- `RTO / RPO` — the business requirements that determine which DR tier to implement
- `Active-Passive` — the most common DR pattern (primary region + DR standby)
- `Active-Active` — the highest DR tier (both regions serve live traffic)
- `Geo-Replication` — the data layer of DR; keeps DR region data current
- `Multi-Region Architecture` — the compute/traffic layer of DR

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Plan + infrastructure + tested procedures │
│              │ to survive catastrophic regional failure  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any system where regional outage is       │
│              │ unacceptable; compliance requirements     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Untested DR plans — test quarterly or     │
│              │ you have no DR (you have a document)      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HA handles a server dying; DR handles    │
│              │  the whole data centre burning down."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Geo-Replication → Multi-Region            │
│              │ Architecture → Chaos Engineering          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your company's current DR strategy is: daily database snapshot to S3 (cross-region), no standby infrastructure. RTO is effectively 4-8 hours. The business now requires RTO=30 minutes, RPO=5 minutes after a new enterprise contract. Design the target DR architecture: specify which AWS services you would use, estimated monthly cost increase, and the complete runbook outline for executing a DR failover. Identify the three hardest operational challenges in implementing this upgrade.

**Q2.** During a DR test, the following is discovered: the primary database has 500GB that takes 3 hours to restore. The business requires RTO=60 minutes. Propose three architectural approaches to reduce DR restore time to under 60 minutes, ranked by: complexity of implementation, cost, and reliability. For each approach, identify any new failure modes introduced.
