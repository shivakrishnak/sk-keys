---
layout: default
title: "On-Premises to Cloud Migration"
parent: "Microservices"
nav_order: 2281
permalink: /microservices/on-premises-to-cloud-migration/
number: "2281"
category: Microservices
difficulty: ★★★
depends_on: Cloud — AWS, Containers, Kubernetes, Infrastructure as Code, Technology Migration Strategy
used_by: Re-platforming vs Re-architecting, Technology Migration Strategy
related: Re-platforming vs Re-architecting, Technology Migration Strategy, Twelve-Factor App, Containers, Infrastructure as Code
tags:
  - cloud
  - architecture
  - advanced
  - microservices
  - devops
  - production
---

# 2281 — On-Premises to Cloud Migration

⚡ TL;DR — On-premises to cloud migration is an incremental journey through lift-and-shift, re-platforming, and re-architecting phases — chosen per workload based on value vs. effort.

| #2281 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Cloud — AWS, Containers, Kubernetes, Infrastructure as Code, Technology Migration Strategy | |
| **Used by:** | Re-platforming vs Re-architecting, Technology Migration Strategy | |
| **Related:** | Re-platforming vs Re-architecting, Technology Migration Strategy, Twelve-Factor App, Containers, Infrastructure as Code | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An enterprise runs 200 applications on self-owned data centres. Hardware refresh cycles every 5 years create unpredictable capital expenditure. Provisioning a new server takes 6 weeks. Scaling for peak (Black Friday) requires purchasing hardware that sits idle 350 days a year. Security patches require controlled maintenance windows that create 2am alerts for on-call engineers. The infrastructure team spends 70% of their time on "keeping the lights on" rather than enabling new business capabilities.

**THE BREAKING POINT:**
The cost of running on-premises infrastructure — capital expenditure, operational staffing, hardware refresh, physical space — becomes uncompetitive when compared to cloud offerings. Additionally, time-to-market for new services is constrained by hardware provisioning timelines. The decision to migrate is made; the question is how.

**THE INVENTION MOMENT:**
Cloud migration frameworks (AWS CAF, Google Cloud Adoption Framework) formalised the migration journey as a progression of strategies — from the lowest-effort Lift-and-Shift (move as-is) through Re-platforming (optimise for cloud) to Re-architecting (redesign as cloud-native). Organisations can choose the appropriate strategy per workload based on business value and migration effort.

---

### 📘 Textbook Definition

**On-Premises to Cloud Migration** is the process of transitioning IT infrastructure, applications, and data from self-managed data centres to cloud provider infrastructure (AWS, Azure, GCP). Migration strategies are categorised by the "6 Rs": **Rehost** (lift-and-shift: move VMs as-is), **Replatform** (minor cloud optimisations: managed DB, OS modernisation), **Refactor/Re-architect** (redesign as cloud-native microservices), **Repurchase** (switch to SaaS), **Retire** (decommission), and **Retain** (keep on-premises). A migration programme selects a strategy per application based on business value, technical complexity, and migration risk.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Move workloads to the cloud using the simplest viable strategy per application — lift-and-shift first, optimise later.

**One analogy:**
> Moving house, not redesigning it. You have three options per item: move it as-is (your sofa), replace it on arrival (rent furniture), or buy better in the new home (upgrade). You don't redesign your living arrangements mid-move; you get settled first, then optimise. Cloud migration works the same — get to the cloud first, modernise where value justifies it.

**One insight:**
The biggest risk in cloud migration is attempting to re-architect everything simultaneously — the "lift-and-modernise" fallacy. Lift-and-shift first reduces risk per workload and generates cloud familiarity, on which re-platforming and re-architecting can be built incrementally.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Not all applications have the same migration urgency or benefit from the same strategy.
2. Data migrations carry the highest risk — database migrations require ETL, validation, and often downtime windows.
3. Cloud migration is not an end state — it enables a modernisation journey.
4. Security and compliance requirements must be re-evaluated at every migration phase.
5. The "6 Rs" are a decision framework, not a sequential process — different apps use different Rs simultaneously.

**DERIVED DESIGN:**
From invariant 1: a portfolio assessment scores each application by: business value, technical complexity, cloud-native opportunity, and migration risk. High-value, low-complexity applications are migrated first to generate confidence and capabilities. High-complexity, low-value applications are retired or retained.

From invariant 2: database migration uses one of three strategies: **Migration Replication** (maintain both on-prem and cloud DB in sync during cutover), **Schema-on-Read** (migrate data to cloud object store, query on access), or **CDC Migration** (stream changes from on-prem to cloud DB continuously during transition, cut over when lag reaches zero).

**THE TRADE-OFFS:**
**Gain:** Elastic scaling; pay-as-you-go vs. capital expenditure; managed services reduce operational burden; global availability; faster time-to-market.
**Cost:** Cloud vendor lock-in; egress costs; security model transformation required; training investment; migration complexity for legacy applications; performance unpredictability for latency-sensitive workloads.

---

### 🧪 Thought Experiment

**SETUP:**
A company with 150 applications running on-premises. 30 are simple stateless web apps. 80 are middleware/integration applications. 40 are complex monolithic databases with years of stored procedures.

**WHAT HAPPENS with Re-Architect All:**
All 150 applications scheduled for full cloud-native redesign. Three years later: 15 applications migrated. 135 still on-premises. Hardware refresh cycle hit. $2M emergency capex spent. Executive confidence in cloud migration eroded.

**WHAT HAPPENS with 6Rs Portfolio Approach:**
30 simple web apps: **Rehost** to EC2 in 2 months. Migrating cost and skills built. 80 middleware apps: **Replatform** — manage own Tomcat → ECS Fargate. 6 months. 30 complex DB apps: **Retain** on-premises initially; 10 **Refactor** over 2 years (highest value). 10 legacy ERP systems: **Repurchase** — replace with SaaS (Salesforce, Workday). Year 1: 110 of 150 apps migrated. Hardware refresh eliminated for migrated apps.

**THE INSIGHT:**
Portfolio-driven 6R migration generates value incrementally and builds organisational cloud competency progressively. "Modernise everything" is a strategy that delivers nothing.

---

### 🧠 Mental Model / Analogy

> The 6 Rs are like a contractor's menu for renovating a neighbourhood of houses simultaneously. Some houses: pick up and move to the new location (Rehost). Some: install double-glazing and insulation without changing walls (Replatform). Some: demolish and build anew (Re-architect). Some: sell and buy a modern equivalent property (Repurchase). Some: demolish without rebuilding — they're not needed (Retire). Some: keep where they are for now — they're the listed buildings that can't be moved easily (Retain).

- "Pick up and move" → Rehost (lift-and-shift)
- "Install improvements" → Replatform
- "Demolish and rebuild" → Re-architect
- "Sell and buy new" → Repurchase (SaaS)
- "Demolish only" → Retire
- "Leave in place" → Retain

Where this analogy breaks down: houses can be moved physically without changing their inhabitants. Applications migrated to the cloud require their consumers (other apps, APIs, users) to be redirected — often requiring coordination with consumers that houses do not have.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Moving applications from company-owned computers and data centres to cloud computers rented from Amazon, Microsoft, or Google. The simplest approach is moving applications the same way they run today ("lift-and-shift"). The most complex is rebuilding them specifically for the cloud. Most migrations use a mix of both, depending on the application.

**Level 2 — How to use it (junior developer):**
Start with an application portfolio assessment. Score each app on: business criticality, technical complexity, and cloud opportunity. Choose a migration R per app. For Rehost: use AWS Server Migration Service or Azure Migrate to move VM snapshots to cloud instances. For Replatform: swap self-managed databases for RDS/Cloud SQL (same engine, managed service). For Re-architect: redesign as 12-Factor App in containers (Kubernetes/ECS).

**Level 3 — How it works (mid-level engineer):**
A migration factory approach: a dedicated team manages the tooling and process while application teams own their migration. Key tooling: **AWS Migration Hub** (portfolio tracking), **AWS DMS** (Database Migration Service), **AWS Server Migration Service** (VMware-to-EC2). For database Replatform: DMS replicates on-prem data to RDS in real time; when replication lag approaches zero, a brief maintenance window performs cutover (DNS switch). Post-migration: Infrastructure as Code (Terraform/CDK) captures the migrated configuration for reproducible deployments.

**Level 4 — Why it was designed this way (senior/staff):**
Cloud migration is ultimately a risk/reward optimisation problem. The 6Rs framework allows per-application risk/reward assessment: Rehost delivers 80% of the operational benefit (elastic scaling, managed network) at 10% of the effort. Re-architect delivers 100% of the cloud-native benefit at 10× the effort. The optimal migration programme concentrates Re-architect investment on applications where cloud-native design creates competitive advantage (high scaling, high velocity) and applies Rehost/Replatform to the long tail of applications where the primary goal is data-centre exit, not modernisation.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  6Rs MIGRATION DECISION FLOW                             │
│                                                          │
│  Is application still needed? ─ No → RETIRE             │
│         │ Yes                                            │
│  Does a SaaS alternative exist? ─ Yes → REPURCHASE       │
│         │ No                                             │
│  Regulatory/latency: must stay on-prem? ─ Yes → RETAIN  │
│         │ No                                             │
│  Minor cloud optimisation sufficient? ─ Yes → REPLATFORM │
│         │ No                                             │
│  High business value for redesign? ─ Yes → RE-ARCHITECT  │
│         │ No                                             │
│  REHOST (lift-and-shift) ←────────────────────────────── │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Rehost migration of a web application):**
```
Assessment: App scored → Rehost candidate
  → Phase 1: Networking (VPC, subnets, security groups)
    [← YOU ARE HERE: cloud infrastructure baseline]
  → Phase 2: VM migration (AWS SMS replicates VM to EC2)
  → Phase 3: Database (AWS DMS replicates on-prem DB to RDS)
  → Phase 4: Test environment validation in cloud
  → Phase 5: Traffic cutover (DNS update, 10% → 100%)
  → Phase 6: Monitor 30 days → decommission on-prem VM
```

**FAILURE PATH:**
```
Database cutover failure:
  → DMS replication lag spikes during peak traffic
  → Cutover window extended past maintenance window
  → Rollback: point DNS back to on-prem DB (pre-set)
  → Investigate: DMS instance undersized for data volume
  → Remediation: upsize DMS instance, retry cutover
```

**WHAT CHANGES AT SCALE:**
At 10 apps: manual migration manageable. At 100 apps: migration factory (dedicated team + tooling). At 500+ apps: portfolio management platform (AWS Migration Hub), automated discovery (AWS Application Discovery Service), and wave-based migration planning (50 apps/wave).

---

### 💻 Code Example

**Example 1 — Terraform for Rehost (EC2 + RDS):**

```hcl
# BAD: snowflake server manually configured on-premises
# No IaC, no reproducibility, no cloud benefits

# GOOD: Rehost via Terraform — reproducible cloud infra
resource "aws_instance" "app_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2
  instance_type = "t3.medium"
  subnet_id     = aws_subnet.private.id

  tags = { Name = "migrated-app-server" }
}

resource "aws_db_instance" "app_db" {
  identifier        = "migrated-app-db"
  engine            = "mysql"
  engine_version    = "8.0"  # same as on-premises
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  # DMS replication source for cutover
  username          = var.db_username
  password          = var.db_password
  skip_final_snapshot = false
}
```

**Example 2 — Twelve-Factor App (Re-architect target):**

```dockerfile
# Re-architect: containerised, 12-Factor App
FROM eclipse-temurin:17-jre-alpine

# Factor III: Config in environment, not code
ENV DB_HOST=""
ENV DB_PORT="5432"
ENV APP_PORT="8080"

COPY target/app.jar /app/app.jar

# Factor VI: Execute app as stateless process
ENTRYPOINT ["java", "-jar", "/app/app.jar"]

# Factor IX: Disposable — fast startup/shutdown
STOPSIGNAL SIGTERM
```

---

### ⚖️ Comparison Table

| Strategy | Effort | Cloud Benefit | Best For |
|---|---|---|---|
| **Rehost** | Low | Partial (elasticity, billing) | Legacy apps, fast DC exit |
| **Replatform** | Medium | Good (managed services, reduced ops) | Apps where managed services reduce ops burden |
| **Re-architect** | High | Full (cloud-native, microservices) | High-value, high-churn business capability |
| **Repurchase** | Low-Medium | Full (SaaS) | Commodity functions (HR, CRM, email) |
| **Retire** | None | N/A | Unused or duplicated applications |
| **Retain** | None | None | Regulatory/latency-constrained workloads |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Lift-and-shift saves money immediately | Rehosted VMs sized for on-prem peak require rightsizing to realise cloud cost savings. A VM running 24/7 in the cloud at original size can cost more than on-premises without rightsizing |
| Cloud migration eliminates all operational burden | IaaS (EC2, Azure VM) still requires OS patching, security hardening, and capacity management. PaaS and SaaS reduce burden; IaaS mostly moves it |
| Cloud migration is a one-time project | Cloud migration is a continuous journey — after initial migration, ongoing modernisation, cost optimisation, and architecture evolution continue |
| All on-premises workloads should move to cloud | Some workloads (high-performance computing, data sovereignty requirements, ultra-low latency) are better served on-premises or in hybrid configurations |

---

### 🚨 Failure Modes & Diagnosis

**1. Cost Explosion Post-Migration**

**Symptom:** Cloud bill 3× higher than expected on-prem costs after migration.

**Root Cause:** On-prem VMs were sized for peak and migrated as-is. Cloud instances run 24/7 at peak sizing — no rightsizing, no auto-scaling, no spot instances.

**Diagnostic:**
```bash
# AWS: find oversized instances
aws ce get-rightsizing-recommendation \
  --service EC2 \
  --query 'RightsizingRecommendations[*].[
    CurrentInstance.ResourceId,
    EstimatedMonthlySavings.Value
  ]' \
  --output table
```

**Fix:** Right-size instances using AWS Compute Optimizer recommendations. Enable Auto Scaling Groups. Convert suitable workloads to Spot Instances.

**Prevention:** Build rightsizing and Auto Scaling into the migration runbook — do not migrate without it.

---

**2. Security Group Misconfiguration — Open Attack Surface**

**Symptom:** Security audit reveals database ports open to `0.0.0.0/0` (the public internet).

**Root Cause:** On-premises security was enforced by network firewalls. During lift-and-shift, security groups were configured as "allow all" to avoid migration blockers and never locked down post-migration.

**Diagnostic:**
```bash
# AWS: find security groups with open inbound rules
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.cidr,\
             Values=0.0.0.0/0" \
  --query 'SecurityGroups[*].[
    GroupId, GroupName
  ]' --output table
```

**Fix:** Implement least-privilege security groups immediately post-migration. Database SG: allow only from application server SG. Application SG: allow only from load balancer SG.

**Prevention:** Include security group hardening as a migration checklist gate. Block migration sign-off until security review is complete.

---

**3. DNS Cutover Failure — Split-Brain State**

**Symptom:** Some users reaching cloud application, others still reaching on-premises application. Inconsistent behaviour — users see different data depending on which system serves them.

**Root Cause:** DNS TTL was too high (86400 seconds/24 hours). After DNS record update, some clients cached the old IP for up to 24 hours.

**Diagnostic:**
```bash
# Check DNS propagation globally:
for resolver in 8.8.8.8 1.1.1.1 208.67.222.222; do
  echo "=== $resolver ==="
  dig @$resolver your-app.company.com A +short
done
# Inconsistent IPs = propagation still in progress
```

**Fix:** Reduce DNS TTL to 60 seconds for 24 hours before planned cutover. After cutover, restore normal TTL. Run both environments simultaneously during propagation period.

**Prevention:** Always reduce DNS TTL 24+ hours before planned cutover. Plan rollback: keep on-premises environment live for 24 hours post-cutover.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Cloud — AWS` — understanding cloud infrastructure primitives (VPC, EC2, RDS, IAM) is required to implement any cloud migration strategy
- `Containers` — containerisation is a prerequisite for Replatform and Re-architect migrations that target container-based platforms (ECS, EKS, AKS)

**Builds On This (learn these next):**
- `Re-platforming vs Re-architecting` — the detailed decision framework for choosing between migration strategies per application; builds directly on the 6R framework introduced here
- `Infrastructure as Code (IaC)` — migrated infrastructure must be codified to enable reproducibility, disaster recovery, and ongoing cloud management

**Alternatives / Comparisons:**
- `Technology Migration Strategy` — the broader framework for any technology platform change, of which on-premises-to-cloud is one specific instance
- `Twelve-Factor App` — the application design methodology that defines what a cloud-native re-architected application should look like as the end state of migration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Strategy for moving workloads from        │
│              │ on-premises data centres to cloud         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ High capex, slow provisioning, limited    │
│ SOLVES       │ scalability of on-prem infrastructure     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Apply the right R per application — not   │
│              │ all apps need Re-architecting; Rehost      │
│              │ delivers most value at lowest risk        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Data centre exit; scaling limitations;    │
│              │ operational burden reduction              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Regulatory data residency constraints;    │
│              │ ultra-low latency on-prem requirements    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Elastic scale + reduced capex vs. cloud   │
│              │ vendor lock-in, egress costs, migration   │
│              │ complexity and risk                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Get to the cloud first using the         │
│              │  simplest viable strategy; modernise      │
│              │  incrementally once there."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Re-platforming vs Re-architecting →       │
│              │ Twelve-Factor App → FinOps → IaC          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial services company migrates 50 applications to AWS using lift-and-shift. Post-migration, the monthly cloud bill is 4× higher than expected on-premises costs. The CFO demands an explanation. Walk through the five most common root causes of post-migration cost overruns, the diagnostic approach for each, and the remediation steps to bring costs in line with projections.

**Q2.** Your company has a 20-year-old mission-critical Oracle database (500GB, 200 stored procedures, used by 30 applications). A cloud migration project proposes migrating it to Aurora PostgreSQL (Re-platform). Evaluate the migration complexity across five dimensions: stored procedure compatibility, application query compatibility, migration tooling, rollback strategy, and cutover window. What is your recommended migration approach?

**Q3.** The Retain strategy means keeping some workloads on-premises indefinitely in a hybrid architecture. This creates a hybrid connectivity requirement between on-premises and cloud environments. Describe the network topology, security model, and operational monitoring required to manage a production hybrid architecture where 30% of workloads remain on-premises and 70% run in cloud, with latency-sensitive cross-boundary API calls.

