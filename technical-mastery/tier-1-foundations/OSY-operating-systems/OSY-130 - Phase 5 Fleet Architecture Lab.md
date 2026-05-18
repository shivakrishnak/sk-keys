---
id: OSY-130
title: Phase 5 Fleet Architecture Lab
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-121, OSY-126, OSY-128, OSY-129
used_by: []
related: OSY-128, OSY-129, OSY-131
tags:
  - lab
  - fleet-architecture
  - design
  - hands-on
  - capacity
  - governance
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 130
permalink: /technical-mastery/osy/phase-5-fleet-architecture-lab/
---

## TL;DR

A capstone architecture exercise: design the OS infrastructure
for a fleet of Java services at 100K+ req/s scale. Covers:
OS selection, kernel tuning decisions, cgroup governance,
observability stack, kernel patch strategy, capacity planning,
and anti-pattern prevention. There is no single correct answer
- the exercise is about coherent, justified decision-making.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-130 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | fleet architecture, OS design, capacity planning, governance, lab exercise |
| **Prerequisites** | OSY-121, OSY-126, OSY-128, OSY-129 |

---

### Lab Scenario

```
Context:
  Company: fintech startup, growing rapidly
  Current state:
    - 50 production hosts (various OS versions, some snowflakes)
    - 200 Java microservices
    - 80K req/s current load
    - p99 latency: 150ms (target: 50ms)
    - 3 engineers in platform/infra team
    
  Upcoming:
    - Series B: expected 3x load growth in 6 months
    - SOC 2 Type 2 audit in 4 months
    - New regulatory requirement: data isolation between customer tiers
    
  Budget: $50K/month cloud infrastructure
  
Architecture requirement:
  Design the complete OS infrastructure strategy:
    1. OS baseline selection and standardization
    2. Kernel tuning profile
    3. Container and JVM configuration
    4. Multi-tenant isolation approach
    5. Observability stack
    6. Patch strategy (for SOC 2)
    7. Capacity model for 3x growth
    8. Anti-snowflake measures
```

---

### Reference Architecture Design

```
Layer 1: OS Baseline

  Decision: Ubuntu 22.04 LTS with Ubuntu Pro
  Reasoning:
    - cgroups v2 needed for proper Kubernetes 1.27+ integration
    - Livepatch: zero-downtime security patches for SOC 2 patch SLA
    - Modern kernel (5.15): full eBPF support for observability
    - Ubuntu Pro: 10-year support; satisfies auditor requirements
    
  Standardization plan:
    - Month 1: build Packer AMI from Ubuntu 22.04 + sysctl profile
    - Month 2: rolling host replacement (old -> new AMI)
    - Month 3: all hosts on standard AMI; snowflakes eliminated

Layer 2: Kernel Tuning Profile

  /etc/sysctl.d/99-java-fintech.conf:
    vm.swappiness=1
    vm.dirty_background_ratio=2
    vm.dirty_ratio=5
    vm.dirty_writeback_centisecs=500
    net.core.somaxconn=32768
    net.ipv4.tcp_tw_reuse=1
    net.ipv4.tcp_keepalive_time=60
    net.ipv4.tcp_keepalive_intvl=10
    net.ipv4.tcp_keepalive_probes=3
    net.ipv4.ip_local_port_range=1024 65535
    fs.file-max=2097152
    kernel.mm.transparent_hugepage.enabled=madvise
    kernel.mm.transparent_hugepage.defrag=defer+madvise
    
  Validation: A/B test vs current config; target: -30ms p99
  Bake into AMI: not managed by Ansible alone (immutable)

Layer 3: Container and JVM Strategy

  Container base image: eclipse-temurin:17-jre + Distroless wrapper
    Multi-stage build: build stage (full JDK), runtime (Distroless)
    Benefit: minimal CVE surface; no shell attack vector
    
  JVM flags per pod:
    -XX:+UseContainerSupport
    -XX:MaxRAMPercentage=70.0     # 70% of container memory limit
    -XX:+UseG1GC
    -XX:+UseNUMA (on multi-socket bare metal; not cloud VMs)
    -XX:+AlwaysPreTouch           # predictable latency
    -Djdk.tracePinnedThreads=short # Java 21 virtual thread monitoring
    
  Container security:
    securityContext.runAsNonRoot: true
    readOnlyRootFilesystem: true
    capabilities.drop: ["ALL"]
    seccompProfile.type: RuntimeDefault

Layer 4: Multi-Tenant Isolation

  Requirement: data isolation between customer tiers (Premium, Standard)
  Solution: Kubernetes namespace per tier
  
  Premium tier namespace:
    ResourceQuota: 40% of cluster CPU/memory
    Dedicated nodes (nodeSelector): no Standard workloads
    NetworkPolicy: deny all cross-namespace traffic
    
  Standard tier namespace:
    ResourceQuota: 40% of cluster CPU/memory
    Shared nodes (best-effort isolation)
    
  Platform namespace:
    Remaining 20%: shared infra (monitoring, ingress, etc.)
    
  For stronger isolation between customer companies:
    Kata Containers (separate kernel per pod) - Phase 2 when needed
    Not immediate: adds 500ms startup overhead

Layer 5: Observability Stack

  Metrics:
    node_exporter: per-host OS metrics (15s scrape)
    JMX exporter: JVM metrics (30s scrape)
    Micrometer: application metrics (15s scrape)
    Prometheus: 15-day hot storage
    Thanos: 2-year long-term storage
    
  Key dashboards:
    OS: CPU/memory/disk/network per host (Grafana)
    JVM: heap/GC/threads per service instance (Grafana)
    Fleet: aggregate utilization, capacity headroom (Grafana)
    
  Alerts (Alertmanager):
    Critical -> PagerDuty (p99 > 200ms, OOM events)
    Warning -> Slack (CPU > 70%, disk < 20% free)
    Capacity -> weekly report (time-to-capacity forecast)
    
  Tracing:
    OpenTelemetry Java agent on all services
    Jaeger: trace storage (14-day retention)
    
  eBPF observability (phase 2):
    Beyla: HTTP request tracing without JVM agent
    BCC/bpftrace: ad-hoc deep dives

Layer 6: Patch Strategy (SOC 2)

  Kernel CVE response:
    Critical (CVSS 9+): apply Livepatch immediately (<4 hours)
    High (CVSS 7+): reboot patching within 7 days
    Medium: include in monthly patch cycle
    
  Monthly patch cycle:
    Week 1: patch dev/staging
    Week 2: patch production canary (5% of fleet)
    Week 3: patch production wave 2 (50%)
    Week 4: patch production wave 3 (100%)
    
  SOC 2 evidence:
    Automated: Ansible tracks patch dates per host
    Report: monthly patch compliance report (% patched < 30 days)
    Exception: document if patching delayed (change control ticket)

Layer 7: Capacity Model (3x growth)

  Current: 50 hosts, 80K req/s
  Target: 240K req/s in 6 months
  
  CPU utilization: currently 60% average
  At 240K req/s (3x): 180% (oversubscribed!)
  Required: scale hosts proportionally + headroom
  
  Calculation:
    Safe utilization: 70%
    Hosts for 240K req/s: 50 * 3 / (0.70/0.60) = 128.5 -> 130 hosts
    Buffer for burst: +20%: 156 hosts
    
  Cost estimate:
    Each host: m5.4xlarge (~$0.768/hr on-demand; ~$0.35/hr reserved)
    156 hosts * $0.35 * 720 hrs = $39,312/month (within $50K budget)
    
  Auto-scaling: Kubernetes Cluster Autoscaler
    Min: 50 nodes (current)
    Max: 160 nodes
    Scale-up trigger: CPU request > 70% cluster-wide for 5 minutes
    Scale-down trigger: CPU request < 40% for 15 minutes
    
  Headroom buffer: always maintain 20% unallocated capacity

Layer 8: Anti-Snowflake Measures

  Packer AMI: all OS config baked in (sysctl, packages, users)
  Terraform: all infrastructure defined as code
  
  No direct SSH to production: bastion + auditd + 4-eyes policy
  All changes: PR -> review -> Ansible apply -> validate
  
  Drift detection: daily Ansible dry-run on all hosts
  Alert: if any host deviates from spec
  
  Chaos engineering schedule:
    Month 1: terminate 1 non-critical host per week
    Month 3: terminate 1 production host per week (during business hours)
    Success criterion: service fully recovers within 3 minutes
```

---

### Lab Exercise Debrief Questions

Discuss after completing the design:

1. What trade-off did you make between isolation and density?
   (Kata Containers deferred - justified? What triggers Phase 2?)
   
2. The 3x growth calculation assumed linear CPU scaling.
   What would make CPU scale superlinearly? How would you detect it early?
   
3. If the SOC 2 auditor asks "how do you know your patch is applied
   everywhere?" - what specific evidence does your design produce?
   
4. The p99 latency target is 50ms (currently 150ms).
   Which layer of this design most directly addresses latency?
   What's the expected improvement from kernel tuning alone?
   
5. What would you change if budget doubled vs if budget halved?
