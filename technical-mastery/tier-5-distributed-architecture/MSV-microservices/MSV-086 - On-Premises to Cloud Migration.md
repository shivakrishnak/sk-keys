---
id: MSV-086
title: On-Premises to Cloud Migration
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-085, MSV-087, MSV-088
used_by: MSV-085, MSV-087
related: MSV-085, MSV-087, MSV-088, MSV-001, MSV-080, MSV-081
tags:
  - microservices
  - cloud
  - deep-dive
  - migration
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 86
permalink: /technical-mastery/microservices/on-premises-to-cloud-migration/
---

⚡ TL;DR - On-Premises to Cloud Migration:
moving workloads from self-managed data center
infrastructure to cloud providers (AWS, Azure,
GCP). The 6 Rs framework (Gartner/AWS): Retire,
Retain, Rehost (lift-and-shift), Replatform
(lift-tinker-shift), Refactor/Re-architect,
Repurchase (move to SaaS). Most migrations
start with Rehost (fastest, lowest risk) then
optimize. Key difference: cloud migration vs
microservices migration are SEPARATE concerns
that often happen together. Running monolith
on cloud is fine. Lift-and-shift first: then
modernize. Key risks: network latency (on-prem
services still talk to each other; now cross-
cloud boundaries), security perimeter changes
(no more VPN-only access; must implement
zero trust), and cost estimation errors
(cloud often MORE expensive than on-prem
if not optimized).

| #086 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, Monolith to Microservices Migration, Technology Migration Strategy, Re-platforming vs Re-architecting | |
| **Used by:** | Monolith to Microservices Migration, Technology Migration Strategy | |
| **Related:** | Monolith to Microservices Migration, Technology Migration Strategy, Re-platforming vs Re-architecting, What are Microservices, Conway's Law in Microservices, Team Topologies | |

---

### 🔥 The Problem This Solves

**INFRASTRUCTURE SCALING AND AGILITY LIMITS:**
Large enterprise: 200 servers in an on-premises
data center. Black Friday: needs 10x compute
for 6 weeks. Options: (1) buy 2,000 servers
(capital expense; idle 46 weeks/year); (2)
tried renting colocation: still provisioning
takes 8 weeks. Cloud option: provision 2,000
virtual machines in 5 minutes; release them
after 6 weeks (pay only for what you use).
Beyond scaling: developer productivity (no
more waiting 3 weeks for a new VM), global
reach (data centers in every region), managed
services (no more maintaining own Kafka,
PostgreSQL, Elasticsearch: use managed versions).

---

### 📘 Textbook Definition

**On-Premises to Cloud Migration** is the
process of moving applications, data, and
infrastructure from self-managed data center
equipment to cloud provider-managed
infrastructure (AWS, Azure, GCP, or others).

**The 6 Rs of Cloud Migration (AWS):**

1. **Retire**: shut down unused applications.
   Typically 10-20% of portfolio is unused
   or redundant. Just turn them off.

2. **Retain**: keep on-premises. Applications
   that: can't migrate due to regulatory
   requirements (data sovereignty), latency
   requirements (real-time industrial systems),
   or cost (expensive to migrate, no benefit).

3. **Rehost (Lift-and-Shift)**: move the
   application as-is to cloud VMs. No code
   changes. Fastest path to cloud. Benefits:
   data center consolidation, OpEx vs CapEx.
   Limitation: doesn't use cloud-native features.
   Use when: speed of migration is priority.

4. **Replatform (Lift-Tinker-Shift)**: minor
   optimizations without re-architecting. Example:
   move from self-managed PostgreSQL to AWS RDS
   (same code; managed service instead of self-
   managed). Or: containerize the app (Docker)
   without changing architecture. Sweet spot
   for most migrations.

5. **Refactor/Re-architect**: redesign the
   application to use cloud-native patterns
   (microservices, serverless, event-driven).
   Highest cost, highest long-term benefit.
   Do after migration, not during.

6. **Repurchase**: move to a SaaS alternative.
   Example: self-managed Salesforce on-prem ->
   Salesforce.com. Self-managed email server
   -> G Suite/Microsoft 365.

**Cloud migration waves**: large migrations
are done in waves. Wave 1: dev/test environments
(low risk, learn the cloud). Wave 2: non-critical
production workloads. Wave 3: critical production.
Wave N: regulatory/legacy last.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
6 Rs: Retire, Retain, Rehost, Replatform,
Refactor, Repurchase. Start with Rehost
(lift-and-shift). Modernize after migration.

**One analogy:**
> On-premises-to-cloud migration is like moving
> houses. Lift-and-shift (Rehost): put everything
> in moving boxes, move to new house, unpack
> exactly as it was (fast, no optimization;
> you're just in a new house). Replatform: while
> moving, upgrade the sofa (keep same room
> layout; just better furniture). Re-architect:
> completely redesign the floor plan after
> moving in (most effort; most benefit). The
> common mistake: trying to redesign the floor
> plan WHILE moving (Big Bang; everything is
> in boxes AND you're redesigning; chaos).
> Move first. Then optimize.

**One insight:**
The most common cloud migration mistake is
conflating cloud migration with application
modernization. These are separate concerns
with different risk profiles. Cloud migration
(Rehost): move the VM to AWS EC2. Low risk.
Application modernization (Refactor to microservices):
high risk, high reward. Doing both simultaneously:
doubles the risk and the number of things
that can go wrong. Best practice: Rehost first
(get off-premises), then Replatform (use
managed services), then Refactor (modernize
architecture). Three separate initiatives,
not one Big Bang.

---

### 🔩 First Principles Explanation

**6 Rs DECISION FRAMEWORK:**

```
For each application in the portfolio:

Step 1: Should it exist?
  Is it actively used? (check access logs)
  If unused: RETIRE (decommission)
  Save: hosting + maintenance cost

Step 2: Should it migrate?
  Data sovereignty requirements?
  Latency requirements (< 1ms = on-prem only)?
  Regulatory (GDPR data in EU only)?
  If yes: RETAIN (keep on-prem)

Step 3: How complex is the application?
  Simple, stable application?
  -> REHOST (lift-and-shift, just move it)
  OR REPURCHASE (is there a SaaS equivalent?)

Step 4: Small optimizations valuable?
  Self-managed DB? -> move to managed RDS
  Raw VMs? -> containerize with Docker
  -> REPLATFORM (minor changes, big managed
     service benefits)

Step 5: Architecture is the bottleneck?
  Monolith: can't scale at cloud speed?
  Needs serverless/event-driven to be cost-
  effective in cloud?
  -> REFACTOR (post-migration project;
     not during migration)
```

**MIGRATION WAVE PLANNING:**

```
WAVE 0 (prep, 1-2 months):
  - Cloud account structure
  - Network: VPN/Direct Connect (on-prem <-> cloud)
  - IAM: SSO, baseline policies
  - Observability: centralized logging/metrics
  - Landing Zone: VPCs, subnets, security groups
  
WAVE 1 (dev/test, 2-3 months):
  - Move all dev/test environments
  - Low risk; high learning
  - Validate: network, security, tooling
  - Build: migration playbook
  
WAVE 2 (non-critical prod, 3-4 months):
  - Internal tools, reporting, analytics
  - Practice production migration process
  - Validate: operational runbooks
  
WAVE 3 (critical prod, 6-12 months):
  - Customer-facing services
  - Database migration (most complex)
  - Requires: dual-run period
  
WAVE N (legacy/regulated):
  - Mainframe: complex, often stays
  - Regulatory: work with compliance team
```

---

### 🧪 Thought Experiment

**AWS'S OWN MIGRATION: EATING THEIR OWN DOG FOOD**

```
Amazon (2010-2015):
  Moved amazon.com FROM their own data centers
  TO AWS (their own cloud)
  
  Why: AWS services (EC2, RDS, S3) were
  often better than what Amazon's internal
  teams could maintain themselves
  
  Their approach: not Big Bang
  - Service by service migration
  - Years of effort
  - Internal teams: chose their own timing
  
  Lessons learned:
  1. Even AWS struggled with the migration
     (database migrations took longest)
  2. Cultural shift: developers managing
     their own infrastructure (not Ops team)
     = biggest challenge, not technical
  3. Replatforming first: move to managed RDS,
     managed Elasticsearch - even before
     re-architecting
  4. Cost savings: partially offset by
     developer productivity gains
     (faster provisioning, global scale)
     
Conclusion:
  If even AWS's internal teams found migration
  hard: your team will too. Plan for 2-3x
  longer timeline than initial estimate.
  The technical work is less than 50% of
  the effort; organizational change is > 50%.
```

---

### 🧠 Mental Model / Analogy

> Cloud migration decisions are like furniture
> rental vs ownership. On-premises: you own
> the furniture (CapEx: one-time purchase, you
> maintain it, it depreciates, you replace it
> every 10 years). Cloud: you rent the furniture
> (OpEx: pay monthly, provider maintains it,
> upgrade anytime, return if not needed).
> Lift-and-shift: move your owned furniture
> to a rental apartment (still your furniture,
> just different address). Replatform: rent
> furniture from the landlord (same rooms,
> different furniture provider). Re-architect:
> redecorate the entire apartment (new layout,
> new furniture, new look). Cost: same for
> basic compute; cloud often cheaper for
> scale + managed services; more expensive
> for steady-state workloads (don't over-
> provision cloud VMs - you'll pay more than
> on-prem for 24/7 static workloads).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Cloud migration: move your servers/apps from
your own data center to AWS/Azure/GCP. Biggest
benefit: elastic scaling (pay for what you use);
biggest risk: cost overrun if not optimized.

**Level 2 - Lift-and-shift basics (junior developer):**
Rehost = create an AMI (machine image) of the
on-prem VM, launch it as an EC2 instance on AWS.
Application: same code, same OS, same config.
Difference: hardware managed by AWS (no more
racking servers). AWS Migration Service (SMS)
or AWS Application Migration Service: automate
this process.

**Level 3 - Database migration (mid-level):**
Database migration: most complex step. AWS DMS
(Database Migration Service): continuous
replication from on-prem source DB to target
RDS. Steps: (1) create target RDS; (2) start
DMS replication task (full load + CDC); (3)
verify data parity; (4) cut over application
connection string (maintenance window); (5)
stop on-prem DB. Replication lag: key metric
during transition (target for < 1 second before
cutover).

**Level 4 - Cost optimization (senior):**
Cloud cost optimization: often 30-40% savings
possible post-migration. Strategies: Reserved
Instances (1-3 year commitments: 40-60% vs
on-demand), Savings Plans (flexible commitment),
right-sizing (AWS Compute Optimizer: identifies
over-provisioned instances), auto-scaling
(stop paying for peak capacity 24/7), Spot
Instances for batch workloads (90% discount,
interruptible). Without optimization: cloud
is MORE expensive than on-prem for steady-state
workloads. Cost optimization: a separate
post-migration project.

**Level 5 - Landing Zone architecture (principal):**
Enterprise cloud landing zone: the foundational
infrastructure that all migrated workloads run
within. AWS Control Tower: multi-account structure
(management account, log archive account,
audit account, workload accounts). Key decisions:
VPC CIDR planning (non-overlapping with on-prem),
Direct Connect vs VPN (bandwidth + latency),
centralized logging (CloudWatch Logs to central
S3), security baselines (GuardDuty, Security
Hub, Config), tagging strategy (cost allocation,
ownership). Landing zone: must be designed
before any migration wave begins. Retrofitting:
costs 3x more than doing it right upfront.

---

### ⚙️ How It Works (Mechanism)

```
AWS DATABASE MIGRATION SERVICE (DMS) FLOW:

  On-Premises:
    PostgreSQL primary
    (production database)
        |
        v (AWS DMS replication)
        v
  AWS DMS Replication Instance:
    Full Load Phase (hours):
      - Copies all existing data to RDS
      - Application: still uses on-prem DB
    CDC (Change Data Capture) Phase:
      - Streams changes: on-prem -> RDS
      - Replication lag: target < 1 second
        |
        v
  AWS RDS PostgreSQL (target):
    - In sync with on-prem DB
    - Lag: < 1 second

  CUTOVER WINDOW (maintenance window):
    1. Verify lag < 500ms
    2. Stop application writes to on-prem DB
    3. Wait for lag = 0 (full sync)
    4. Update application connection string
       (point to RDS endpoint)
    5. Start application on RDS
    6. Verify: application works with RDS
    7. Stop on-prem DB (read-only snapshot)
    
  Rollback (if issues):
    Reverse connection string in < 5 minutes
    On-prem DB: still intact (read-only snapshot)
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CLOUD MIGRATION PROJECT: end-to-end

  DISCOVERY (1-2 months):
    Application portfolio: all apps catalogued
    Dependency mapping: which apps talk to which
    6 Rs decision: per application
    TCO analysis: on-prem vs cloud cost
    Landing Zone design: VPC, accounts, security

  FOUNDATION (1-2 months):
    AWS accounts: multi-account structure
    VPC: CIDR planning, subnets
    Direct Connect: on-prem <-> AWS (10Gbps)
    IAM: SSO, policies, roles
    Centralized logging: CloudWatch + S3

  WAVE 1 (dev/test, 2-3 months):
    Rehost: all dev/test VMs
    Learn: what breaks (networking, auth, logging)
    Build: migration runbooks

  WAVE 2-N (production, 6-18 months):
    Application by application
    Database migrations: with DMS
    DNS cutover: per application
    Monitor: CloudWatch dashboards per service

  OPTIMIZATION (ongoing):
    Reserved Instances: for steady-state workloads
    Right-sizing: monthly review
    Replatforming: managed services adoption
    Cost allocation: per team/product
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Skip landing zone vs foundational setup**

```yaml
# BAD: Start migrating workloads without
# foundational account structure
# "Let's just get one workload into AWS first"
# Result after 12 months:
#   - 50 workloads: all in ONE AWS account
#   - No cost separation per team
#   - Security: blast radius = entire company
#   - Log management: chaos (everyone shares
#     one CloudWatch environment)
#   - Tagging: inconsistent (no enforcement)
#   - Networking: IP overlap issues
#   - Retrofix: takes 6 months, disrupts workloads
# Cost of "just get started": 6 months of
# expensive remediation work
```

```yaml
# GOOD: AWS Control Tower landing zone FIRST
# Takes 2 months; pays back over years

# AWS Organizations structure:
# ROOT
#   Management Account (billing, governance)
#   |-- Security OU
#   |     |-- Log Archive Account (centralized logs)
#   |     |-- Audit Account (security findings)
#   |-- Production OU
#   |     |-- payments-prod account
#   |     |-- orders-prod account
#   |     |-- catalog-prod account
#   |-- Non-Production OU
#   |     |-- payments-dev account
#   |     |-- orders-dev account
#   |-- Sandbox OU
#         |-- developer-experiments account

# Benefits:
#   Blast radius: limited to one account
#   Cost visibility: per account (per team)
#   Security: SCPs (Service Control Policies)
#     per OU (e.g., non-prod can't run in
#     us-east-1 by SCP enforcement)
#   Audit: all logs centralized in log-archive
#   Tagging: enforced by Config rules
```

---

### ⚖️ Comparison Table

| Strategy | Effort | Risk | Time to Migrate | Cloud Benefit |
|---|---|---|---|---|
| **Retire** | Lowest | None | Immediate | N/A (decommission) |
| **Retain** | None | None | N/A | None |
| **Rehost** | Low | Low | Weeks | Data center exit |
| **Replatform** | Medium | Medium | Months | Managed services |
| **Refactor** | High | High | 6-24 months | Full cloud-native |
| **Repurchase** | Medium | Medium | Months | No maintenance |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Cloud is always cheaper than on-premises | Cloud is cheaper for: variable/spiky workloads (pay for peak usage only during peaks), teams that over-provision on-prem (cloud forces right-sizing), workloads using managed services (vs self-managed equivalent). Cloud is MORE expensive for: steady-state, predictable workloads (on-demand pricing vs amortized hardware), lift-and-shift without optimization (same workload, cloud pricing), and teams that don't optimize (Reserved Instances, Savings Plans). Realistic outcome: 20-40% savings with optimization; potential cost INCREASE without optimization. |
| Lift-and-shift is a "temporary" step that should be refactored immediately | Lift-and-shift is a valid long-term state for many applications. Not every application needs to be re-architected. A stable back-office application that runs fine as a VM on-prem: runs fine as a VM on EC2. The cost of re-architecting (3-6 months of engineering) must be justified by specific benefits (scale, cost, developer productivity). For most legacy enterprise applications: Replatform (move to managed DB, containerize) is the optimal end state. Refactor only when the business case is clear. |
| Cloud migration is primarily a technology project | Cloud migration is 30% technology and 70% organizational change. Key organizational challenges: (1) developers learning cloud tooling (IAM, VPC, managed services); (2) operations teams shifting from hardware management to cloud operations; (3) finance shifting from CapEx to OpEx budgeting; (4) security teams adapting perimeter model to zero trust; (5) procurement adjusting to consumption-based billing. Without addressing these: the technology migration succeeds but the organization reverts to old patterns (over-provisioning cloud VMs like on-prem servers). |

---

### 🚨 Failure Modes & Diagnosis

**Cloud cost explosion: lift-and-shift without optimization**

**Symptom:**
Company migrated 200 on-prem servers to AWS
EC2 (lift-and-shift). On-prem cost: $800K/year
(hardware + datacenter + staff). AWS bill:
month 1: $220K (annualized $2.6M). CFO: furious.
"You said cloud would save money."

**Root Cause:**
Lift-and-shift: matched on-prem VM sizes
1:1 with EC2 instances (24 vCPU on-prem = c5.6xlarge
on AWS on-demand). On-prem: hardware already
paid for (sunk cost). Cloud: every CPU-hour costs
money. On-prem: 40% average CPU utilization
(over-provisioned for peak). Cloud: paying for
40% utilization on on-demand pricing.

**Diagnosis:**
```
AWS Cost Explorer analysis:
  Top 10 instance types by cost
  Average CPU utilization per instance
  (CloudWatch: CPUUtilization metric)
  
  Findings:
    80% of instances: < 20% avg CPU utilization
    -> massively over-provisioned
    
  Recommendation from Compute Optimizer:
    Downsize: 60% of instances by 1-2 sizes
    Convert to Reserved: stable workloads
    Spot: batch processing workloads
```

**Fix:**
```
WEEK 1: Quick wins
  Reserved Instances (1-year, no upfront):
  for top 20 steady-state instances
  Savings: 40% vs on-demand immediately
  
MONTH 1: Right-sizing
  Compute Optimizer recommendations:
  downsize over-provisioned instances
  Savings: additional 20-30%
  
MONTH 2-3: Replatform
  Move DB VMs to RDS (eliminate DB admin cost)
  Auto-scaling: for variable workloads
  
Result: AWS bill drops from $220K/mo to $90K/mo
  (still higher than on-prem hardware cost;
   but on-prem: had hidden costs: staff,
   power, cooling, hardware refresh)
```

---

### 🔗 Related Keywords

**Migration strategy:**
- `Technology Migration Strategy` - general
  principles applied to cloud migration
- `Re-platforming vs Re-architecting` - specific
  strategies within the 6 Rs framework
- `Monolith to Microservices Migration` - often
  concurrent concern with cloud migration

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| RETIRE      | Unused: just turn off             |
| RETAIN      | Data sovereignty / latency        |
| REHOST      | Lift-and-shift (fastest)          |
| REPLATFORM  | Managed services (sweet spot)     |
| REFACTOR    | Microservices (post-migration)    |
| REPURCHASE  | SaaS alternative                  |
+--------------+---------------------------------+
| WAVE ORDER  | Dev/test first; prod last        |
| NEVER       | Skip landing zone; Big Bang      |
+--------------+---------------------------------+
| ONE-LINER   | "Rehost first, optimize later.  |
|             |  Never conflate migration with   |
|             |  modernization."                 |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. 6 Rs: Retire, Retain, Rehost (lift-and-shift),
   Replatform (managed services), Refactor
   (microservices - do AFTER migration), Repurchase.
2. Landing Zone first: multi-account structure,
   VPC, IAM, centralized logging. 2 months
   investment prevents 6 months of remediation.
3. Cloud costs: optimize post-migration. Reserved
   Instances (40% discount), right-sizing (Compute
   Optimizer), auto-scaling. Without optimization:
   cloud is MORE expensive than on-prem.

**Interview one-liner:**
"On-premises to cloud migration: 6 Rs framework -
Retire (unused), Retain (regulatory/latency), Rehost
(lift-and-shift: fastest, no code change), Replatform
(managed services: RDS vs self-managed DB), Refactor
(microservices: do AFTER migration, not during),
Repurchase (SaaS). Migration waves: dev/test first;
critical prod last. Key mistakes: skipping landing
zone setup (multi-account structure), conflating
migration with modernization, expecting cost savings
without optimization (Reserved Instances + right-
sizing required)."

---

### 💡 The Surprising Truth

The most expensive cloud migration decision
is choosing between AWS Direct Connect and
VPN for on-prem connectivity, and most teams
choose wrong. VPN: cheap ($50/month), but
bandwidth limited (< 100Mbps practical) and
latency variable (internet routing). Direct
Connect: expensive ($1,000-5,000/month for
dedicated connection), but bandwidth dedicated
(1-10Gbps), latency consistent (< 10ms to
AWS region). Teams that choose VPN: realize
during migration that their database replication
(DMS) takes 10x longer (VPN bandwidth throttles
initial full-load replication from multi-TB
databases). After 3 months of slow migration:
they order Direct Connect (8-12 week lead
time for physical installation). Migration:
delayed 4 months for a $1,500/month cost
difference. Lesson: evaluate Direct Connect
before any wave of production database migrations.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **6 RS ANALYSIS** Given a portfolio of 20
   applications: classify each using the 6 Rs.
   Include: analysis criteria used (access logs,
   data sovereignty requirements, SLA, TCO).
2. **LANDING ZONE** Design an AWS landing zone
   for a 5-team company: accounts structure,
   VPC CIDR plan, IAM policy architecture, and
   centralized logging configuration.
3. **DATABASE MIGRATION** Design the AWS DMS
   migration for a 500GB PostgreSQL on-prem DB.
   What is the full-load time estimate (at
   Direct Connect bandwidth)? What is the
   maintenance window plan? What is the rollback
   procedure?
4. **COST ANALYSIS** Given 50 migrated EC2
   instances with average 25% CPU utilization:
   design the right-sizing and Reserved Instance
   purchase plan. Estimate monthly savings
   vs current on-demand billing.
5. **WAVE PLANNING** Create a 12-month migration
   wave plan for a 50-application portfolio.
   What goes in wave 1 vs wave 3? What are
   the go/no-go criteria for each wave?

---

### 🧠 Think About This Before We Continue

**Q1.** Your company has a real-time trading
application: 200 microsecond latency requirement
for order matching. It's currently co-located
in a data center next to the stock exchange.
The CEO asks: "Should we migrate this to cloud?"
Using the 6 Rs: what is your recommendation
and justification? What would need to change
(technically or strategically) for cloud to
become viable for this application?

**Q2.** During cloud migration: you discover
that your CRM system (running on-prem) is
actually Salesforce running on a self-managed
server (someone "installed" Salesforce on a
VM years ago). What is the correct 6R strategy?
What is the cost/risk comparison between
Rehost (lift to cloud VM), Replatform (move
to Salesforce.com), and keeping it as-is (Retain)?

**Q3.** Your organization chose not to set up
a landing zone before starting migration ("we'll
do it later"). 6 months later: 30 workloads
are in a single AWS account with no tagging
standards, no cost allocation, and mixed
development/production workloads. You're now
tasked with retroactively implementing a proper
landing zone. What is the migration plan from
chaos to multi-account structure? What are
the risks of this retrofix? What can be done
without downtime?