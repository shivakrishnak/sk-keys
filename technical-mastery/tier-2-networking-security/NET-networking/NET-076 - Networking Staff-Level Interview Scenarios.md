---
id: NET-076
title: "Networking Staff-Level Interview Scenarios"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★★
depends_on: NET-053, NET-067, NET-074, NET-075
used_by: NET-083
related: NET-053, NET-067, NET-074, NET-075, NET-083
tags:
  - networking
  - interviews
  - staff
  - principal
  - system-design
  - scenarios
  - leadership
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 76
permalink: /technical-mastery/net/networking-staff-level-interview-scenarios/
---

**⚡ TL;DR** - Staff and principal engineer networking
interviews test judgment, not just knowledge. You'll be
asked to design systems where the "right" answer requires
defending trade-offs, estimating costs, and leading
through ambiguity. This entry covers 8 staff-level
scenarios with full model responses: network design
for 10M users, debugging a production network mystery,
designing a zero-trust migration, handling a cross-team
conflict over network ownership, and writing a
postmortem for a DNS-caused outage.

| #076 | Category: Networking | Difficulty: ★★★★★ |
|:---|:---|:---|
| **Depends on:** | Networking System Design (NET-053), Deep-Dive Q&A (NET-067), Decision Framework (NET-074), Build a Platform (NET-075) | |
| **Used by:** | Networking Career Paths (NET-083) | |
| **Related:** | System Design, Deep-Dive, Decision Framework, Build a Platform, Networking Career Paths | |

---

### 🔥 What Staff-Level Interviews Assess

```
At senior level: "Can you build this correctly?"
At staff level: "What SHOULD we build, and can you lead us to it?"

Staff interview dimensions:
  1. Scope and ambiguity:
     Start with a vague requirement, drive to specific design
     Show: how you gather requirements before designing
     
  2. Trade-off reasoning:
     Multiple valid approaches exist - defend your choice
     Show: you know when each approach is appropriate
     
  3. Cross-functional impact:
     Network changes affect security, compliance, cost, dev velocity
     Show: you think across team boundaries
     
  4. Failure modes and mitigations:
     Every design has failure modes - you should name them
     Show: you design defensively
     
  5. Execution and influence:
     How do you get 10 teams to adopt your network policy?
     Show: you can drive organizational change, not just write code
```

---

### ⚙️ Scenario 1 - Design the Network for 10M Users

**The question:**

```
"We're launching a new payments platform. We expect
10M users globally, 500 TPS peak, compliance with
PCI-DSS. Design the network architecture."
```

**Staff-level response pattern:**

```
Step 1 - Clarify requirements before designing:
  "Before I start, I have a few questions:
  - Are users global or US-only to start?
  - What's the latency requirement? (SLA for payment API)
  - Is this greenfield cloud-native, or migrating existing?
  - Which cloud provider? (impacts service availability)
  - What's the team size and ops maturity?
  
  [Wait for answers, then design to those specifics]"
  
Why this matters:
  10M users US-only: GeoDNS not needed, single region possible
  10M users globally: 3 regions minimum
  Team of 5: don't recommend service mesh day one
  Team of 50: service mesh is appropriate
  
Step 2 - State key assumptions explicitly:
  "Assuming: global users, 3 regions, mature DevOps team,
  AWS provider. Here's my design..."
  
Step 3 - Design with trade-off reasoning:
  VPC: 3 VPCs (main, CDE, sandbox) per region × 3 regions
  Cross-region: Transit Gateway (not VPC peering - 9+ VPCs)
  User routing: Route53 latency-based (not anycast - HTTP only)
  DDoS: AWS Shield Standard + WAF (not Advanced yet, cost)
  
  "I'd recommend starting with Shield Standard. If we see
  attack patterns, upgrade to Advanced. Advanced is $3K/month
  minimum - justify with actual attack surface."
  
  Service mesh: Istio
  "But I'd phase this: observability only (month 1-2),
  traffic management (month 3-4), mTLS (month 5-6).
  Don't enable strict mTLS until all 50 services are enrolled."
```

---

### ⚙️ Scenario 2 - Debug a Production Mystery

**The question:**

```
"Our checkout service has been experiencing 2% error
rate since yesterday's deploy. The error is inconsistent -
sometimes checkout succeeds, sometimes 504 timeout.
The deploy was a config change to the payment-api, not
a code change. What do you do?"
```

**Staff-level response:**

```
Initial assessment:
  "2% error rate, 504 (gateway timeout) - the upstream
  isn't responding in time. Config change to payment-api.
  
  My hypothesis: the config change affected connection pool,
  timeout, or a downstream service URL.
  
  Before touching anything: get more data."

Structured diagnostic approach:
  1. Timeline correlation:
     Deploy timestamp vs error rate spike - exact minute?
     Was there a staggered rollout (canary)? Is 2% the canary pods?
     
  2. Identify which requests fail:
     Filter: which 2% are failing?
     Are they from specific users, regions, request types?
     Check: Jaeger traces for failed requests vs successful
     
  3. Check the config change:
     What exactly changed in payment-api config?
     If timeout changed: was it made shorter? (now timing out more)
     If URL changed: is the new URL correct?
     If connection pool changed: smaller pool = exhaustion under load?
     
  4. Payment-api → downstream:
     payment-api talks to: fraud-service, card-vault, bank-api
     Which downstream? Check: error rate per upstream in Grafana
     One upstream spiked? → config change affected that connection
     
  5. Immediate mitigation:
     Rollback the config change (low risk, immediate mitigation)
     "Even if we don't know root cause: rollback reduces MTTM"
     After rollback: investigate safely
     
Prevent future:
  "Config changes should go through canary too, not just code.
  Any change to timeouts, URLs, or pool sizes: deploy to 10%,
  observe 5 minutes, then proceed."
```

---

### ⚙️ Scenario 3 - Zero Trust Migration Strategy

**The question:**

```
"Our company has 200 services all trusting each other
on the internal network. The CISO wants to move to
zero trust in 6 months. How do you approach this?"
```

**Staff-level response:**

```
Reality check first:
  "6 months for 200 services is aggressive. I want to set
  realistic expectations and present a phased plan. The risk
  of rushing zero trust is that strict mTLS enabled before
  all services are enrolled breaks production."
  
Assessment (Month 1):
  Inventory: how many services are on Kubernetes vs VMs?
  Kubernetes: service mesh is the path (automated certificate mgmt)
  VMs: consul connect or manual mTLS configuration (harder)
  
  Output: a service inventory with: K8s or VM, team owner,
          criticality, inbound/outbound dependencies
  
Phase planning:
  Phase 1 (months 1-2): Observability only
    Install Envoy sidecar in permissive mode
    Deploy Kiali service graph
    No behavior changes, no risk
    Goal: understand actual traffic patterns (discover undocumented flows)
    
  Phase 2 (months 2-4): Traffic management
    Canary deployments for critical services
    Circuit breakers on all external-facing services
    
  Phase 3 (months 4-6): STRICT mTLS by tier
    Start: analytics services (low criticality, lower risk)
    Then: auth services, app services
    Last: payment services (highest scrutiny)
    Never rush: each tier needs 2-week observation window
    
Cross-functional work (where staff engineering actually happens):
  Work with each team: explain what changes, provide runbooks
  Coordinate with security: what policies do they want enforced?
  Coordinate with compliance: audit log format for SOC 2 evidence
  Build tooling: automated enrollment check (dashboard of progress)
  
6-month realistic goal:
  "We can achieve full observability, traffic management,
  and STRICT mTLS for ~50% of services in 6 months.
  The remaining 50% (legacy/VM-based): 3 more months.
  I'll present a phased timeline to the CISO with risks
  of each acceleration option."
```

---

### ⚙️ Scenario 4 - Cross-Team Ownership Conflict

**The question:**

```
"The security team wants to enforce NetworkPolicy blocking
cross-namespace traffic in Kubernetes. The app team says
this will break their service-to-service calls that rely
on direct cross-namespace communication. Both teams come
to you. What do you do?"
```

**Staff-level response:**

```
Don't take sides immediately:
  "I want to understand both requirements before making any
  technical recommendation. Can we get both teams together?"

Gather requirements:
  Security team:
    What specific threat are they mitigating?
    (Lateral movement: if pod is compromised, prevent cross-namespace pivot)
    Is this driven by compliance (SOC 2, PCI)?
    What's the exception process?
    
  App team:
    Which services make cross-namespace calls?
    What namespaces to what namespaces?
    Are these calls well-understood and intentional?
    
Likely technical resolution:
  NetworkPolicy can ALLOW specific cross-namespace calls
  Not all-or-nothing - granular rules:
  
  Allow: checkout (ns: payments) → auth (ns: auth) on port 8080
  Deny: everything else cross-namespace
  
  This meets security's goal (block unintended lateral movement)
  while allowing intentional service dependencies
  
Action:
  1. Inventory all intentional cross-namespace calls
  2. Write explicit NetworkPolicy rules for each
  3. Default-deny (catch accidental future connections)
  4. Automated: service ownership in CODEOWNERS
     Any new cross-namespace call: PR reviewed by security
  
Organizational result:
  "Security and app teams both need to win here.
  The solution is precision: allow what's intended,
  block what's not. Neither team needs to compromise
  on their core requirement."
```

---

### ⚙️ Scenario 5 - Write a Postmortem

**The scenario:**

```
Incident: 2-hour outage caused by DNS misconfiguration.
A platform engineer updated the CoreDNS config to add a
new forwarding rule. A typo in the ConfigMap caused
CoreDNS to crash. All service-to-service DNS resolution
failed. All services returned connection errors.
Recovery: reverted the ConfigMap, CoreDNS restarted.
```

**Staff-level postmortem structure:**

```
POSTMORTEM: DNS Outage - CoreDNS Crash

Impact:
  Duration: 2 hours 14 minutes
  User impact: ~100% of checkout requests failed
  Revenue impact: $450K in lost transaction revenue
  
Timeline:
  14:22 - Engineer edits CoreDNS ConfigMap
  14:24 - CoreDNS pods crash (OOMKill after config parse error)
  14:25 - First monitoring alert: high error rate
  14:30 - First responder: investigates app logs (not DNS yet)
  14:55 - Second responder: checks pod health, sees CoreDNS down
  15:00 - Root cause identified: CoreDNS crash
  15:01 - CoreDNS ConfigMap reverted
  15:03 - CoreDNS pods healthy
  15:07 - Service error rate returns to baseline
  16:36 - All caches expired, full normal operation
  
Root cause:
  Typo in CoreDNS Corefile: missing closing brace
  CoreDNS: failed to parse config → crashed → kubernetes restart loop
  App services: DNS resolution failed → NXDOMAIN for all service names
  No fallback: no DNS-level retry configuration
  
Contributing factors:
  1. No validation of ConfigMap changes before apply
  2. No canary for DNS config changes
  3. Alert: "high error rate" fired, not "DNS failure" specifically
     → 30-minute diagnosis delay
  4. CoreDNS replicas: 2 (both crashed simultaneously)
     Would have needed >2 healthy to serve during rollout
     
Action items:
  [P1] Validate CoreDNS ConfigMap with conftest/rego before apply
  [P1] AlertManager: add alert for CoreDNS pod crash events
  [P2] Increase CoreDNS replicas to 5 (prevent total failure)
  [P2] Add DNS health check to app readiness probes
       (detect DNS failure faster at app layer)
  [P3] Runbook: "DNS failure" diagnostic playbook in PagerDuty
  [P3] Post-incident review: 30-min diagnosis gap
       Add: "check CoreDNS health" as step 1 in networking incident runbook
  
What went well:
  Second responder identified root cause methodically
  Rollback was fast once root cause known
  Blameless culture: engineer reported the change transparently
  
Lessons:
  Infrastructure config changes need the same rigor as code
  DNS failures present as application errors → misleads investigation
  Chaos engineering: test CoreDNS failure in staging monthly
```

---

### ⚙️ Scenario 6 - Networking Architecture for a Startup

**The question:**

```
"You're the first platform engineer at a 5-person startup.
You have a monolith running on 1 EC2 instance. 
Design the network for the next 2 years."
```

**Staff-level response (anti-overengineering):**

```
This is a test of NOT over-engineering:

Year 0-6 months:
  1 EC2 instance + RDS = don't touch the network
  Not needed: VPC segmentation, service mesh, Transit Gateway
  Add: Elastic IP (stable IP), security group (443 only)
  
Year 6-12 months (users growing, hiring):
  Add: Application Load Balancer (SSL termination)
  Add: Auto Scaling Group (multiple EC2s behind ALB)
  Add: private subnet for EC2s (not directly internet-accessible)
  Add: separate DB subnet (no internet access)
  Cost: ~$50/month extra
  
Year 12-24 months (if growth to 20+ services):
  Consider: EKS (if moving to containers)
  Consider: Istio in permissive mode (observability first)
  NOT YET: multi-region (cost > benefit for startup)
  NOT YET: Transit Gateway (only 1 VPC needed)
  
Key principle:
  Network complexity should match organizational complexity
  Don't build for 10M users when you have 1,000
  Add complexity when pain is real, not anticipated
  
What I would invest in early (high ROI):
  Terraform from day 1: small investment, huge DR benefit
  Security groups: principle of least privilege from start
  VPC with proper subnet tiers: cheap to do right from start
  (correcting VPC CIDR design later = major pain)
  
The staff signal here: knowing what NOT to build is as
important as knowing what to build
```
permalink: /technical-mastery/net/networking-staff-level-interview-scenarios/
---