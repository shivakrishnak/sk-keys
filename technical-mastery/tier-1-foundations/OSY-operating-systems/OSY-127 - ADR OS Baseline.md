---
id: OSY-127
title: ADR OS Baseline
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-116, OSY-119, OSY-120, OSY-126
used_by: []
related: OSY-119, OSY-120, OSY-128
tags:
  - ADR
  - architecture
  - decision
  - OS-baseline
  - documentation
  - governance
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 127
permalink: /technical-mastery/osy/adr-os-baseline/
---

## TL;DR

An Architecture Decision Record (ADR) template for OS
baseline decisions: choosing Linux distribution, kernel
version policy, sysctl profiles, container base images,
and kernel tuning standards for a production Java fleet.
Good ADRs document context, options considered, decision,
rationale, and consequences - enabling future teams to
understand WHY the baseline was chosen.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-127 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | ADR, architecture decision, OS baseline, documentation, governance |
| **Prerequisites** | OSY-116, OSY-119, OSY-120, OSY-126 |

---

### ADR Template

```markdown
# ADR-NNN: [Short Title]

Date: YYYY-MM-DD
Status: [Proposed | Accepted | Deprecated | Superseded by ADR-NNN]
Authors: [Team / Person]
Reviewers: [Team / Person]
Stakeholders: [Teams affected]

## Context

[Describe the situation: what decision needs to be made, 
what constraints exist, what problem is being solved.
Include: current state, problem observed, requirements.]

## Options Considered

### Option 1: [Name]
  Description: ...
  Pros: ...
  Cons: ...
  Risk: ...

### Option 2: [Name]
  (same structure)

## Decision

[State the decision clearly. Which option was chosen.]

## Rationale

[Why this option over others. What trade-offs were accepted.
What requirements this satisfies. What it intentionally
does NOT address.]

## Consequences

Positive:
  - ...

Negative:
  - ...

Neutral:
  - ...

## Review Date

[When should this ADR be reviewed for continued validity?]
```

---

### Example ADR: Linux Distribution Baseline

```markdown
# ADR-015: Linux Distribution Baseline for Java Production Fleet

Date: 2024-01-15
Status: Accepted
Authors: Platform Engineering Team
Reviewers: Security Team, Java Team Leads
Stakeholders: All teams deploying Java services

## Context

The organization operates 400 Java production hosts across
3 data centers and 2 cloud regions. Currently using a mix of:
  - Ubuntu 18.04 LTS (EOL April 2023, already past support)
  - CentOS 7 (EOL June 2024, approaching)
  - Ubuntu 20.04 LTS (some teams)

Problems:
  - Inconsistent kernel versions (4.15 on old Ubuntu, 3.10 on CentOS 7)
  - No cgroups v2 on CentOS 7 (blocks Kubernetes upgrade to 1.26+)
  - Ubuntu 18.04: critical CVEs no longer receive security patches
  - Security team: cannot meet SOC 2 patch SLAs on EOL OS

Requirements:
  1. Security: active security patching for 5+ years
  2. Compatibility: runs Java 17+ and Kubernetes 1.25+
  3. Stability: stable API; no disruptive changes mid-support
  4. Tooling: works with existing Ansible playbooks
  5. Cost: minimize licensing costs where possible

## Options Considered

### Option 1: Ubuntu 22.04 LTS
  Description: 
    Ubuntu LTS; supported April 2022 - April 2027 standard
    April 2027 - April 2032 with Ubuntu Pro
  Kernel: 5.15 (HWE: 6.5+)
  cgroups: v2 by default
  
  Pros:
    - Modern kernel (5.15): io_uring, full eBPF, cgroups v2
    - Ubuntu Pro: 10-year security support
    - Large community; excellent documentation
    - Canonical Livepatch available
    - Java Temurin distributions: first-class Ubuntu support
    
  Cons:
    - AppArmor (not SELinux): different from RHEL ecosystem
    - Faster release cycle than RHEL: more frequent changes
    - Some enterprise teams: unfamiliar with apt
    
  Risk: Medium. Package update cadence can occasionally break
  dependencies between major updates.

### Option 2: RHEL 9
  Description:
    Red Hat Enterprise Linux 9; supported May 2022 - May 2032
  Kernel: 5.14 (heavily backpatched)
  cgroups: v2 by default
  
  Pros:
    - Enterprise support SLA from Red Hat
    - SELinux default: aligns with regulated workloads
    - FIPS 140-2 validated: enables FedRAMP path
    - Conservative kernel backporting: predictable behavior
    - Familiar to RHEL-experienced ops teams
    
  Cons:
    - Subscription cost: ~$350/socket/year
    - 400 hosts * 2 sockets * $350 = $280,000/year additional cost
    - Older package versions (gcc, Python) affect developer tooling
    
  Risk: Low stability risk. Medium cost risk.

### Option 3: Rocky Linux 9 (RHEL-compatible, free)
  Description:
    Binary-compatible RHEL 9 clone; community-supported
  Kernel: same as RHEL 9
  
  Pros:
    - Free (no subscription)
    - Binary compatible with RHEL: same packages, behavior
    - Community security patches: within 24h of RHEL patches
    
  Cons:
    - No commercial support SLA
    - SOC 2 auditors may question non-commercial OS support
    - If RHEL changes build pipeline: Rocky may lag
    
  Risk: Medium. Acceptable for most workloads; concern for
  regulated workloads where auditors require commercial support.

## Decision

**Selected: Ubuntu 22.04 LTS with Ubuntu Pro**

## Rationale

1. Cost: Ubuntu Pro ($25/host/year) vs RHEL ($700/host/year)
   Fleet of 400 hosts: $10,000/year vs $280,000/year
   
2. Modern kernel requirements: Ubuntu 22.04 kernel 5.15 provides
   full cgroups v2, io_uring, and eBPF features needed for
   Kubernetes 1.28+ and virtual thread monitoring tools.
   
3. Support lifecycle: Ubuntu Pro provides 10-year security
   maintenance (until 2032), satisfying the 5-year requirement.
   
4. Livepatch: Canonical Livepatch enables zero-downtime security
   patching for critical CVEs, improving our patch SLA metrics.
   
5. Trade-off accepted: AppArmor vs SELinux. Security team
   reviewed AppArmor profiles; determined equivalent protection
   for our threat model. Not seeking FedRAMP at this time.
   
6. Rejected RHEL 9: cost-prohibitive for current fleet size.
   Rejected Rocky Linux 9: SOC 2 Type 2 auditors expressed
   preference for commercially-supported OS.

## Consequences

Positive:
  - Single OS baseline reduces Ansible playbook complexity
  - Modern kernel unlocks eBPF-based observability (Beyla, BCC)
  - 10-year support horizon eliminates OS EOL migrations until 2032
  - Livepatch reduces maintenance windows for CVE response

Negative:
  - Migration effort: 400 hosts from Ubuntu 18.04/CentOS 7
    Estimated: 6-month migration project
  - Teams accustomed to yum/dnf must learn apt
  - Some RHEL-specific tooling (Satellite, Insights) will not work

Neutral:
  - AppArmor profiles needed for container workloads
    (equivalent to existing SELinux effort)
  - Ubuntu Pro licensing: $25/host/year (budgeted)

## Review Date

January 2027 (3 years). Revisit if:
  - FedRAMP becomes a requirement (triggers RHEL evaluation)
  - Ubuntu Pro pricing changes significantly
  - Rocky Linux gains commercial support tier
```

---

### ADR: sysctl Profile

```markdown
# ADR-016: Standard sysctl Profile for Java Production

Date: 2024-01-20
Status: Accepted

## Decision

Deploy /etc/sysctl.d/99-java-production.conf to all hosts:
  vm.swappiness=1
  vm.dirty_background_ratio=2
  vm.dirty_ratio=5
  net.core.somaxconn=32768
  net.ipv4.tcp_tw_reuse=1
  net.ipv4.tcp_keepalive_time=60
  kernel.mm.transparent_hugepage.enabled=madvise

## Rationale

Load-tested each parameter change independently.
Results documented in PERF-2024-01 performance report.
Key findings:
  - vm.swappiness=1: eliminates swap-induced p99 spikes (+15% p99 reduction)
  - dirty ratios: reduces iowait spikes on write-heavy services (+8% p99)
  - THP madvise: reduces GC pause outliers (+12% GC p99 reduction)
  
Validation: 30-day canary on 5% of fleet; no regressions.

## Consequences
  Positive: consistent p99 improvement across Java fleet
  Negative: parameter drift detection required (Ansible verify job)
```

---

### ADR Quick Reference

| Field | Purpose |
|-------|---------|
| Status | Current state: Proposed/Accepted/Deprecated |
| Context | Why this decision was needed |
| Options Considered | What alternatives were evaluated |
| Decision | The specific choice made |
| Rationale | Why this choice over others |
| Consequences | What changes as a result |
| Review Date | When to re-evaluate |
