---
title: "Cloud AWS - Architecture and Security"
topic: Cloud AWS
subtopic: Architecture and Security
keywords:
  - Multi-AZ and Disaster Recovery
  - AWS Security Best Practices
  - Cost Optimization
  - CloudWatch
  - Shared Responsibility Model
  - Auto Scaling Patterns
difficulty_range: medium-hard
status: complete
version: 1
---

# Multi-AZ and Disaster Recovery

**TL;DR** - Multi-AZ provides high availability within a region (automatic failover, synchronous replication), while disaster recovery strategies (backup/restore, pilot light, warm standby, active-active) provide cross-region resilience with different RTO/RPO trade-offs.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Single data center failure takes down your entire application. Even within AWS, a single AZ can experience issues. Without DR planning, a region-wide outage (rare but possible) means complete downtime until the region recovers.

---

### How It Works

```
High Availability (Multi-AZ) vs Disaster Recovery:
  HA (Multi-AZ): Survive AZ failure. Same region.
    Automatic. Milliseconds-to-minutes failover.
  DR (Multi-Region): Survive region failure.
    Manual or semi-auto. Minutes-to-hours recovery.

DR Strategies (increasing cost and speed):
  +----------------------------------------------------+
  | Strategy      | RTO     | RPO    | Cost   | Approach|
  |---------------|---------|--------|--------|---------|
  | Backup/Restore| Hours   | Hours  | $      | S3 cross-region, restore when needed |
  | Pilot Light   | 10min   | Minutes| $$     | Core infra running, scale on failover|
  | Warm Standby  | Minutes | Seconds| $$$    | Scaled-down copy running in DR region|
  | Active-Active | Seconds | Zero   | $$$$   | Full capacity in both regions        |
  +----------------------------------------------------+

Multi-AZ patterns by service:
  EC2 + ASG: Instances across AZs, ALB distributes
  RDS Multi-AZ: Sync standby, auto-failover (60-120s)
  Aurora: 6 copies across 3 AZs, <30s failover
  ElastiCache: Primary + replica in different AZ
  EFS: Multi-AZ by default
  S3: Multi-AZ by default (11 nines durability)

  Design rule: If a service offers Multi-AZ, ENABLE it.
  The cost is small. The protection is enormous.

Active-Active Multi-Region:
  Route 53 (latency routing)
    -> Region A: Full stack (ALB + ASG + Aurora Primary)
    -> Region B: Full stack (ALB + ASG + Aurora Global DB read)
  DynamoDB Global Tables: active-active multi-region
  S3 Cross-Region Replication: async data sync
```

---

### Quick Recall

**If you remember only 3 things:**

1. Multi-AZ = HA within region (auto-failover, sync). Multi-Region = DR across regions (higher cost, lower RTO). Always do Multi-AZ for production.
2. DR strategy selection: Backup/Restore (cheapest, hours RTO), Pilot Light (core ready, minutes), Warm Standby (scaled-down running), Active-Active (instant, expensive).
3. RPO (how much data you can lose) and RTO (how long you can be down) drive DR strategy choice. Business requirements dictate the investment level.

**Interview one-liner:**
"Multi-AZ for high availability within a region (always enabled in production), with DR strategy chosen based on RTO/RPO requirements - pilot light for cost-effective DR (minutes RTO), warm standby for critical workloads (seconds RPO), and active-active with DynamoDB Global Tables and Aurora Global DB for zero-downtime requirements."

---

---

# AWS Security Best Practices

**TL;DR** - AWS security is built on defense in depth: least-privilege IAM, encryption everywhere (at rest + in transit), network isolation (VPC + security groups), detective controls (CloudTrail, GuardDuty), and automated remediation - with the shared responsibility model defining the boundary.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
A single misconfigured S3 bucket exposes millions of records. An overly permissive IAM role allows lateral movement. No audit trail means breaches go undetected for months. Security as an afterthought = guaranteed incident.

---

### How It Works

```
Defense in Depth layers:
  1. Identity (IAM):
     - Least privilege (start with nothing, add needed)
     - Roles > Users (temporary credentials)
     - MFA everywhere (especially root, admin)
     - SCPs for organizational guardrails
     - Permission boundaries for delegated admin

  2. Network (VPC):
     - Private subnets for workloads (no public IP)
     - Security groups (allow-only, reference other SGs)
     - NACLs (subnet-level deny rules)
     - VPC endpoints (access AWS services privately)
     - WAF + Shield for edge protection

  3. Data Protection:
     - Encryption at rest: KMS (SSE-KMS for S3, EBS, RDS)
     - Encryption in transit: TLS 1.2+ everywhere
     - S3 Block Public Access (account-level default)
     - Secrets Manager for credentials (auto-rotation)
     - Macie for PII detection in S3

  4. Detective Controls:
     - CloudTrail: API audit log (who did what, when)
     - GuardDuty: Threat detection (ML-based)
     - Config: Resource compliance tracking
     - Security Hub: Aggregated security findings
     - VPC Flow Logs: Network traffic analysis

  5. Incident Response:
     - Automated remediation (Config rules + Lambda)
     - Forensic-ready (immutable logs, AMI snapshots)
     - Playbooks for common scenarios
     - Regular IR drills

Security checklist for any new workload:
  [ ] Root account: MFA enabled, no access keys
  [ ] CloudTrail: Enabled in all regions
  [ ] S3: Block Public Access at account level
  [ ] Encryption: KMS keys for all data at rest
  [ ] VPC: Private subnets, no unnecessary public IPs
  [ ] GuardDuty: Enabled (free tier available)
  [ ] Secrets: In Secrets Manager, not env vars/code
```

---

### Quick Recall

**If you remember only 3 things:**

1. Defense in depth: IAM (least privilege) + Network (private subnets, SGs) + Data (encryption everywhere) + Detection (CloudTrail, GuardDuty) + Response (automated remediation).
2. Day-1 essentials: CloudTrail on, GuardDuty on, S3 Block Public Access on, root MFA on, no root access keys, all secrets in Secrets Manager.
3. Shift-left: Security in CI/CD (cfn-nag, tfsec for IaC scanning), automated compliance (AWS Config rules), and regular access reviews (IAM Access Analyzer).

**Interview one-liner:**
"I implement defense in depth: least-privilege IAM with roles and SCPs, private subnets with security group chains, KMS encryption for all data, CloudTrail+GuardDuty+Config for detection, and automated remediation via Config rules - with security validated in CI/CD through IaC scanning."

---

---

# Cost Optimization

**TL;DR** - AWS cost optimization combines right-sizing (matching resources to actual usage), pricing models (Reserved/Savings Plans/Spot), architectural patterns (serverless, auto-scaling), and governance (budgets, tagging, organizational policies) to reduce waste while maintaining performance.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Cloud bill grows 30% quarter over quarter. Teams provision "just in case" and never downsize. Nobody knows which team/project owns which cost. Dev environments run 24/7 for 8 hours of use. No accountability, no visibility, no optimization.

---

### How It Works

```
Cost optimization pillars:

1. RIGHT-SIZING (biggest impact, do first):
   - CPU utilization <30%? Downsize instance type
   - Memory usage <40%? Switch to compute-optimized
   - Tools: Cost Explorer, Compute Optimizer, Trusted Advisor
   - Review monthly, act on recommendations

2. PRICING MODELS:
   On-Demand:    Pay as you go (baseline 100%)
   Reserved/SP:  1-3yr commitment (save 40-72%)
   Spot:         Unused capacity (save up to 90%)
   Strategy: RI for baseline + Spot for variable + OD for spikes

   Savings Plans vs Reserved Instances:
   | Feature      | Savings Plan     | Reserved Instance |
   |-------------|-----------------|-------------------|
   | Flexibility | Any instance type| Specific instance |
   | Scope       | Compute (any)    | Per instance      |
   | Discount    | Similar (~40-72%)| Similar           |
   | Recommendation| Usually better | Legacy, still valid|

3. ARCHITECTURAL PATTERNS:
   - Auto Scaling: match capacity to demand (no idle)
   - Serverless: Lambda, Fargate, Aurora Serverless
     (pay only for actual compute used)
   - Spot instances for fault-tolerant workloads
     (CI/CD runners, batch processing, dev environments)
   - S3 lifecycle policies (auto-archive cold data)
   - Schedule non-production (stop dev/test at night)

4. GOVERNANCE:
   - Tagging strategy (team, project, environment)
   - AWS Budgets + alerts (detect anomalies early)
   - Cost allocation reports by tag
   - Service Control Policies (prevent expensive resources)
   - FinOps team or champion (cultural change)

Quick wins (week 1):
  [ ] Delete unattached EBS volumes
  [ ] Release unused Elastic IPs
  [ ] Stop idle dev/test instances (or schedule)
  [ ] Delete old snapshots (>90 days)
  [ ] Right-size based on Compute Optimizer
  [ ] Enable S3 Intelligent-Tiering on data lakes
```

---

### Quick Recall

**If you remember only 3 things:**

1. Right-size first (biggest impact): CPU <30% = downsize, use Compute Optimizer. Then pricing models: Savings Plans for baseline (40-72% off), Spot for fault-tolerant (90% off).
2. Architecture matters: Auto Scaling (no idle capacity), serverless (pay per use), scheduled environments (dev off at night = 65% savings), S3 lifecycle policies.
3. Governance: tag everything (team, project, env), set AWS Budgets with alerts, review Cost Explorer monthly, use Organizations SCPs to prevent waste.

**Interview one-liner:**
"Cost optimization as a practice: right-sizing via Compute Optimizer, Savings Plans for steady-state, Spot with capacity-optimized allocation for fault-tolerant workloads, serverless where appropriate, environment scheduling, comprehensive tagging for allocation, and AWS Budgets for anomaly detection."

---

---

# CloudWatch

**TL;DR** - CloudWatch is AWS's monitoring and observability service - collecting metrics, logs, and traces from AWS resources, setting alarms for automated actions, creating dashboards, and enabling anomaly detection for proactive issue identification.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
No visibility into what's happening inside your AWS resources. Is the CPU high? Is the application throwing errors? How many requests are failing? When did the problem start? No metrics, no logs, no alarms = flying blind.

---

### How It Works

```
CloudWatch components:

1. METRICS (numbers over time):
   Default metrics: EC2 CPU, network, disk
   Custom metrics: Business KPIs, app-level data
   Namespaces: AWS/EC2, AWS/RDS, Custom/MyApp
   Resolution: Standard (60s) or High-res (1s)

2. ALARMS (react to metrics):
   Metric threshold -> State change -> Action
   States: OK | ALARM | INSUFFICIENT_DATA
   Actions: SNS notification, Auto Scaling, EC2 action
   Composite alarms: AND/OR multiple alarms

   Example:
   CPUUtilization > 80% for 5 minutes
     -> Alarm state -> SNS -> PagerDuty
     -> Auto Scaling: add 2 instances

3. LOGS (text data):
   Log Groups: /aws/lambda/my-function
   Log Streams: One per instance/container
   Insights: SQL-like queries across logs
   Metric Filters: Extract metrics from log patterns
     ERROR count from log text -> custom metric -> alarm

4. DASHBOARDS (visualization):
   Custom dashboards with widgets
   Cross-account, cross-region
   Automatic dashboards per service

5. ADVANCED:
   Anomaly Detection: ML-based (expected bands)
   Contributor Insights: Top-N contributors
   ServiceLens: Distributed tracing (X-Ray integration)
   Synthetics: Canary tests (simulate user traffic)

Key metrics to always monitor:
  EC2: CPUUtilization, StatusCheckFailed
  RDS: FreeableMemory, ReadLatency, Connections
  ALB: 5XXCount, TargetResponseTime, HealthyHostCount
  Lambda: Errors, Duration, Throttles, ConcurrentExec
  SQS: ApproximateAgeOfOldestMessage, DLQ depth
```

---

### Quick Recall

**If you remember only 3 things:**

1. CloudWatch = metrics + logs + alarms + dashboards. Default metrics are free (5-min resolution). Custom metrics and high-resolution (1s) cost extra.
2. Alarms drive automation: metric threshold -> SNS (alert humans) + Auto Scaling (add capacity) + Lambda (remediate). Always set alarms on critical metrics.
3. Logs Insights: SQL-like query language across log groups. Metric Filters: extract counts/values from logs into metrics. Both are essential for troubleshooting.

**Interview one-liner:**
"CloudWatch provides unified observability - I set alarms on golden signals (latency, errors, traffic, saturation), use Logs Insights for ad-hoc troubleshooting, metric filters to surface application errors as alarms, custom dashboards for service health, and anomaly detection for proactive alerting without static thresholds."

---

---

# Shared Responsibility Model

**TL;DR** - AWS secures the infrastructure (hardware, network, facilities, hypervisor) while customers secure everything they put IN the cloud (data, IAM, OS patching, network config, encryption) - the boundary shifts based on the service model (IaaS vs PaaS vs SaaS).

---

### The Problem This Solves

**WORLD WITHOUT IT:**
"We're in the cloud so AWS handles security." This misconception leads to publicly accessible S3 buckets, unpatched EC2 instances, overly permissive security groups, and unencrypted databases. Without clear responsibility boundaries, gaps emerge.

---

### How It Works

```
Shared Responsibility Model:
  +--------------------------------------------+
  | CUSTOMER RESPONSIBILITY ("Security IN the cloud") |
  | Data classification and encryption        |
  | IAM (users, roles, policies, MFA)         |
  | Operating system patching (EC2)           |
  | Network configuration (SG, NACL, routing)  |
  | Application security (code, dependencies) |
  | Client-side encryption                     |
  +--------------------------------------------+
  | AWS RESPONSIBILITY ("Security OF the cloud")      |
  | Physical data centers (access, power, cooling)    |
  | Network infrastructure (backbone, DDoS protection)|
  | Hypervisor and host OS                            |
  | Managed service infrastructure (RDS engine patching)|
  | Hardware lifecycle (decommissioning, destruction) |
  +--------------------------------------------+

Responsibility shifts by service model:
  EC2 (IaaS):
    You: OS patching, runtime, app, data, network config
    AWS: Hardware, hypervisor, physical security

  RDS (PaaS):
    You: Data, schema, IAM, network config, encryption
    AWS: OS patching, engine patching, HA, backups infra

  Lambda (Serverless):
    You: Function code, IAM, data
    AWS: Everything else (runtime, scaling, patching, OS)

  S3 (Managed):
    You: Bucket policies, encryption config, data class
    AWS: Storage infrastructure, durability, availability

Key principle:
  More managed service = less customer responsibility
  Less managed (IaaS) = more customer responsibility
  Choose managed services to reduce security surface area

Common customer failures:
  - S3 bucket with public access (customer misconfiguration)
  - EC2 with unpatched OS (customer forgot to patch)
  - Security group allowing 0.0.0.0/0 on port 22
  - RDS without encryption (customer didn't enable)
  - IAM user with admin access and no MFA
  (All of these are customer responsibility - not AWS)
```

---

### Quick Recall

**If you remember only 3 things:**

1. AWS = security OF the cloud (physical, hardware, hypervisor, managed service infrastructure). Customer = security IN the cloud (data, IAM, networking config, patching).
2. Responsibility shifts: EC2 (you patch OS) vs RDS (AWS patches OS) vs Lambda (AWS manages everything except your code). More managed = less responsibility.
3. Most breaches are customer misconfiguration (public S3, weak IAM, unpatched EC2). Use managed services + automation (Config rules) to reduce the surface area you must secure.

**Interview one-liner:**
"The Shared Responsibility Model defines AWS securing the infrastructure (physical, hypervisor, network backbone) while customers secure what's in it (data, IAM, network config, encryption) - I prefer managed services to minimize our responsibility surface and use AWS Config to enforce compliance on what remains ours."

---

---

# Auto Scaling Patterns

**TL;DR** - Auto Scaling automatically adjusts compute capacity based on demand using scaling policies (target tracking, step, scheduled) - maintaining performance during peaks and reducing costs during valleys, applicable to EC2, ECS, DynamoDB, and Aurora.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Fixed capacity: either over-provisioned (paying for idle 70% of the time) or under-provisioned (degraded performance during peaks). Manual scaling requires human intervention - too slow for traffic spikes, too expensive for continuous over-provisioning.

---

### How It Works

```
Auto Scaling components:
  1. Launch Template: WHAT to launch (AMI, instance type)
  2. Auto Scaling Group: WHERE (VPC, subnets/AZs)
  3. Scaling Policy: WHEN to scale (metrics, schedules)
  4. Health Check: HOW to detect unhealthy instances

Scaling policy types:
  Target Tracking (recommended - simplest):
    "Keep average CPU at 60%"
    ASG automatically adds/removes to maintain target
    Works like a thermostat. Set and forget.

  Step Scaling (granular control):
    CPU 60-70% -> add 1 instance
    CPU 70-80% -> add 2 instances
    CPU > 80% -> add 4 instances
    (Different actions at different thresholds)

  Scheduled Scaling (predictable patterns):
    "Scale to 10 instances at 8am, back to 2 at 8pm"
    "Scale to 20 on Black Friday"
    (Known traffic patterns, complement other policies)

  Predictive Scaling (ML-based):
    Analyzes historical patterns, pre-scales ahead
    Avoids lag of reactive scaling
    Works best with recurring patterns

Scaling beyond EC2:
  ECS Service Auto Scaling:
    Scale task count based on CPU/memory/ALB requests
  DynamoDB Auto Scaling:
    Scale read/write capacity based on utilization
  Aurora Auto Scaling:
    Add/remove read replicas based on connections/CPU
  Application Auto Scaling:
    Generic framework for any scalable resource

Best practices:
  - Scale OUT fast, scale IN slow (cooldown periods)
  - Use multiple AZs (rebalancing on scale events)
  - Right-size first, THEN auto-scale (don't scale junk)
  - Warm-up period: time for new instances to be ready
  - Mixed instances: On-Demand base + Spot for scaling
  - Monitor: GroupDesiredCapacity, InServiceInstances
```

---

### Quick Recall

**If you remember only 3 things:**

1. Target Tracking is the default choice (set CPU target 60-70%, ASG handles the rest). Add Scheduled for known patterns. Predictive for ML-based pre-scaling.
2. Scale out fast, scale in slow: short cooldown for adding instances (react quickly to spikes), longer cooldown for removing (avoid flapping).
3. Auto Scaling applies beyond EC2: ECS tasks, DynamoDB capacity, Aurora replicas, Lambda concurrency. Same principle, different resource types.

**Interview one-liner:**
"I use Target Tracking as the primary scaling policy (CPU or custom metric at 60-70%), supplemented with Scheduled Scaling for known patterns and Predictive Scaling for proactive capacity - scaling out aggressively (short cooldown) and in conservatively, with mixed instance policies for cost optimization."
