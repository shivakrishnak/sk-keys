---
id: CTR-052
title: Containerization Migration Strategy
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-001, CTR-047, CTR-049
used_by:
related: CTR-056, CTR-011
tags:
  - containers
  - architecture
  - advanced
  - bestpractice
  - devops
status: complete
version: 2
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /ctr/containerization-migration-strategy/
---

# CTR-050 - Containerization Migration Strategy

⚡ TL;DR - Containerization migration strategy is the structured plan for moving workloads from VMs or bare metal to containers: assess, choose a migration pattern, migrate in phases, and validate operational readiness at each gate.

| Metadata        |                          |     |
| :-------------- | :----------------------- | :-- |
| **Depends on:** | CTR-001, CTR-047, CTR-049 |     |
| **Used by:**    |                          |     |
| **Related:**    | CTR-056, CTR-011         |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An organisation decides to "containerise everything" over a quarter.
Each team migrates independently. Some do lift-and-shift (copy the VM
filesystem into a container image - including cron jobs, syslog, and
SSH servers). Others re-architect everything from scratch and miss the
deadline. After the quarter, 20% of services are containerised, 80%
are in various states of partial migration, and the platform team
supports both worlds indefinitely.

**THE BREAKING POINT:**
A "big bang" containerisation programme: freeze all new features, migrate
all 150 services simultaneously, cut over on a single date. The cutover
date arrives. 30 services are not ready. 10 have hidden dependencies on
VM-specific behaviour (syslog, /proc mounts, cron). The cutover is
rolled back. 6 months of migration effort is wasted.

**THE INVENTION MOMENT:**
Containerisation migration is not a technical problem - it is a change
management problem. The technical patterns (lift-and-shift, re-platform,
re-architect) are well understood. The migration strategy defines which
pattern to apply to which workload, in which order, with which gates.

**EVOLUTION:**
2015: Docker adoption begins with stateless web services (easiest).
2017: Stateful services (databases, message queues) are containerised
with persistent volume support. 2019: Legacy monolith containerisation
becomes common as teams adopt strangler fig patterns. 2021: Migration
strategies include hybrid cloud patterns (some services on VMs, some
on containers, some serverless). 2023: AI/ML workload containerisation
emerges as a separate strategy track (GPU scheduling, model serving).

---

### 📘 Textbook Definition

**Containerization migration strategy** is the phased plan for moving
workloads from non-container environments (VMs, bare metal, PaaS) to
container-based environments, including workload assessment, pattern
selection (lift-and-shift vs. re-platform vs. re-architect), migration
sequencing (stateless before stateful, low-risk before high-risk), and
operational readiness gates (observability, security, CI/CD).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Migrate containers in phases - stateless first, stateful later, with
an operational readiness gate before each wave.

**One analogy:**

> Containerisation migration is like office relocation. You do not move
> everyone on the same day. You move IT infrastructure first (networking,
> servers), then teams that can work remotely (stateless services), then
> teams that need the physical space (stateful services), then retire the
> old building (decommission VMs). Each phase has a completion gate
> before the next begins.

**One insight:**
The sequence matters more than the speed. Migrating stateless services
first builds team capability and tooling before tackling harder stateful
workloads. Migrating high-traffic services last (after validation on
lower-risk services) reduces the risk of a high-impact failure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Stateless services are easier to containerise than stateful ones** -
   stateless services have no local disk state to migrate; stateful
   services require persistent volume management, backup, and failover.
2. **Operational readiness must precede migration** - CI/CD, logging,
   metrics, alerting, and secret management must be in place before
   the first production workload moves.
3. **Dual-stack operation is expensive** - running both VM and container
   infrastructure simultaneously doubles operational complexity. The
   migration must move fast enough to reach VM decommission.
4. **Hidden VM dependencies create migration blockers** - services that
   depend on VM-specific behaviour (syslog, mDNS, cron, SSH) require
   refactoring before containerisation.

**DERIVED DESIGN:**
Given invariant 1: sequence stateless before stateful. Given invariant 3:
set a hard decommission date for VMs that creates urgency to complete
the migration. Given invariant 4: conduct a pre-migration dependency
audit to identify and plan for hidden blockers before they become
mid-migration surprises.

**THE TRADE-OFFS:**
**Gain:** Phased migration with gates reduces blast radius, builds team
capability incrementally, and enables early validation before high-risk
workloads are moved.
**Cost:** Phased migration extends the dual-stack operation period and
requires discipline to avoid stalling in the "mostly migrated" state
indefinitely.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any migration must handle the stateless/stateful ordering,
dependency audit, operational readiness, and VM decommission.
**Accidental:** Custom migration tooling built instead of using existing
tools (Buildpacks, AWS App2Container, Google Migrate to Containers).

---

### 🧪 Thought Experiment

**SETUP:**
An organisation runs 60 services on EC2 VMs: 40 stateless APIs and
web services, 15 stateful services (databases, queues, caches), and 5
legacy monoliths.

**WHAT HAPPENS WITHOUT MIGRATION STRATEGY:**
All teams start containerising simultaneously. Some services migrate in
weeks, others stall for months. A stateful database is containerised
without understanding persistent volumes - data is lost on pod restart.
The legacy monolith is lifted-and-shifted into a container that runs
as root with 15 processes inside it. After 6 months, 30 services are
containerised, 30 are not, and the platform team supports both without
a decommission plan.

**WHAT HAPPENS WITH MIGRATION STRATEGY:**
Wave 1 (weeks 1-8): 15 stateless services migrated with full CI/CD,
logging, and metrics. Operational readiness validated. Wave 2 (weeks
9-20): remaining 25 stateless services migrated using patterns from
Wave 1. Wave 3 (weeks 21-36): 15 stateful services migrated with
persistent volumes and backup. Wave 4 (weeks 37-48): 5 monoliths
containerised using strangler fig. VMs decommissioned at week 52.

**THE INSIGHT:**
Migration strategy is primarily a sequencing and gate problem.
The technical patterns are known. The discipline to phase the work,
validate at gates, and maintain VM decommission pressure is the
differentiator between a successful migration and a 3-year "partially
containerised" state.

---

### 🧠 Mental Model / Analogy

> Containerisation migration is like a ship fleet conversion from steam
> to diesel engines. You do not convert the entire fleet simultaneously.
> You convert the smallest, least-critical vessel first (learn the
> conversion process), then progressively convert larger and more
> critical vessels, retiring steam infrastructure as each vessel
> is converted.

Element mapping:

- **Fleet** = all services in the organisation
- **Vessel size** = service complexity and traffic volume
- **Steam infrastructure** = VM/bare metal infrastructure
- **Diesel infrastructure** = container platform
- **Conversion** = containerisation migration
- **Decommission pressure** = VM cost and maintenance burden

Where this analogy breaks down: in ship conversion, the vessel stops
running during conversion; in containerisation, the service must
continue running (zero-downtime migration using blue-green or canary).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Containerisation migration strategy is the plan for moving applications
from servers to containers - deciding which to move first, how to move
them, and what to check before each move.

**Level 2 - How to use it (junior developer):**
Three migration patterns: (1) Lift-and-shift: Containerise as-is, no
code changes (fast but image may be bloated). (2) Re-platform: Minor
changes to fit container model (12-factor, env var config). (3) Re-
architect: Significant refactoring (microservices, stateless design).
Start with re-platform for simple services, re-architect only for
services that genuinely need it.

**Level 3 - How it works (mid-level engineer):**
Migration sequencing: stateless before stateful, low-traffic before
high-traffic, independent before coupled. Pre-migration gates: CI/CD
pipeline exists, logging/metrics integrated, secrets management ready,
security baseline enforced. Post-migration gates: latency and error
rate match VM baseline, all alerts firing correctly, rollback tested.

**Level 4 - Why it was designed this way (senior/staff):**
Migration strategy is a risk management problem. Each wave reduces risk
by building team capability and tooling before higher-risk workloads
are touched. The operational readiness gate exists because containerising
a service before the observability stack is in place means migrating
blind - you cannot validate success or detect failure. The VM
decommission date creates urgency that prevents the "mostly migrated"
indefinite state.

**Expert Thinking Cues:**

- "What is the decommission date for VMs? Does the organisation have
  budget and contract pressure to meet it?"
- "Which services have hidden dependencies on VM-specific behaviour?
  Have they been audited before migration planning?"
- "What is the rollback plan for a failed migration? Is it running the
  VM again, or is the VM already decommissioned?"

---

### ⚙️ How It Works (Mechanism)

**MIGRATION PATTERN SELECTION:**

```
Workload assessment:
  |
  ├─ Simple stateless, 12-factor-ready?
  |   └─ Re-platform (env var config,
  |       containerise as-is, minimal changes)
  |
  ├─ Complex stateless, legacy config?
  |   └─ Lift-and-shift first, re-platform
  |       later when stable
  |
  ├─ Stateful (DB, queue, cache)?
  |   └─ PersistentVolume strategy first,
  |       then migrate
  |
  └─ Legacy monolith with tight coupling?
      └─ Strangler fig + incremental
          extraction before containerise
```

**OPERATIONAL READINESS GATE:**

```
Before migrating any service to production:
  [ ] CI/CD pipeline produces container image
  [ ] Logging ships to central log store
  [ ] Metrics exported (Prometheus/CloudWatch)
  [ ] Alerting configured (error rate, latency)
  [ ] Secrets injected via Vault/K8s Secret
  [ ] Security baseline enforced (non-root,
      resource limits, network policy)
  [ ] Rollback procedure tested
  Pass all 7: proceed to migration
  Fail any: fix before migration
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Migration Programme Start
  |
  v
Phase 0: Operational Readiness
  (platform, CI/CD, observability, secrets)
  |
  v
Wave 1: Stateless Pilot (5-10 services)
  |  [validate, fix, document patterns]
  v          ← YOU ARE HERE
Wave 2: Stateless Bulk (remaining stateless)
  |  [reuse patterns from Wave 1]
  v
Wave 3: Stateful Services
  |  [PersistentVolume, backup, failover]
  v
Wave 4: Legacy / Monoliths
  |  [strangler fig, incremental extraction]
  v
VM Decommission (hard date)
```

**FAILURE PATH:**
Organisation skips Phase 0. Migrates a service before logging is in
place. The service has a latent bug that manifests in the container
environment. With no logs, the team cannot diagnose. The service is
rolled back to the VM. Trust in the migration programme is damaged.

**WHAT CHANGES AT SCALE:**
At 100+ services, the migration is too large for a single team. A
dedicated platform migration team owns the tooling, patterns, and
gates. Service teams own the migration execution for their services.
The platform team provides golden path Dockerfiles and CI templates.

---

### 💻 Code Example

```dockerfile
# BAD: lift-and-shift anti-pattern (VM in a container)
# Multiple processes, SSH server, syslog, cron
FROM ubuntu:20.04
RUN apt-get install -y openssh-server \
    rsyslog cron supervisor
COPY supervisord.conf /etc/supervisor/
COPY app/ /app/
# Runs multiple processes via supervisor
CMD ["/usr/bin/supervisord"]
```

```dockerfile
# GOOD: re-platform - single process, 12-factor
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY target/app.jar ./
RUN adduser -D -u 1000 appuser
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget -qO- http://localhost:8080/health || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
# Config via env vars, not config files in image
# Logs to stdout, not /var/log/
# Single process, not supervisor
```

```bash
# Pre-migration dependency audit script
#!/bin/bash
SERVICE=$1
echo "Auditing $SERVICE for VM dependencies..."

# Check for cron usage
grep -r "cron\|crontab" $SERVICE/src/ && \
  echo "WARNING: cron detected - use Kubernetes CronJob"

# Check for syslog usage
grep -r "syslog\|rsyslog" $SERVICE/src/ && \
  echo "WARNING: syslog detected - use stdout logging"

# Check for file-based config (not env vars)
find $SERVICE/ -name "*.conf" -o -name "*.properties" | \
  grep -v test | \
  echo "WARNING: file config detected - migrate to env vars"
```

**How to test / verify correctness:**

```bash
# Validate the containerised service matches VM baseline
# Run both versions and compare response time and error rate
ab -n 1000 -c 10 http://vm-service/api/health
ab -n 1000 -c 10 http://container-service/api/health

# Verify logs ship to central store
kubectl logs -f deployment/myservice | \
  jq '{level, message, timestamp}' | head -10
```

---

### ⚖️ Comparison Table

| Migration Pattern | Effort | Risk | Image Size | Container Best Practices |
|---|---|---|---|---|
| Lift-and-shift | Low | Medium | Large | No (multi-process, root) |
| Re-platform | Medium | Low-Medium | Medium | Partial (single process, env vars) |
| Re-architect | High | Low (long-term) | Small | Yes (12-factor, stateless) |
| Strangler Fig | Very High | Low | Small | Yes (incrementally) |

---

### 🔁 Flow / Lifecycle

**MIGRATION PROGRAMME PHASES:**

**Phase 0 - Operational Readiness (weeks 1-4):**
Container platform selected and operational. CI/CD pipeline template
created. Logging, metrics, and alerting baseline established. Secrets
management solution deployed. Security baseline policies enforced.
Golden path Dockerfile and Helm chart templates available.

**Phase 1 - Pilot Wave (weeks 5-12):**
5-10 stateless, low-traffic services migrated using golden path templates.
Patterns documented. Blockers identified and resolved. Operational
readiness gate validated against each service. Success metrics: same
latency and error rate as VM baseline, all alerts firing correctly,
rollback tested.

**Phase 2 - Bulk Stateless Migration (weeks 13-28):**
Remaining stateless services migrated using patterns from Phase 1. Each
team executes migration for their services. Platform team provides
support and resolves common blockers. Gate: VM equivalent decommissioned
for each migrated service.

**Phase 3 - Stateful and Complex (weeks 29-44):**
Databases, caches, and message queues migrated with PersistentVolume
strategy, backup automation, and failover testing. Legacy monoliths
addressed via strangler fig or full re-architecture.

**Phase 4 - Decommission (weeks 45-52):**
All remaining VMs decommissioned. Platform team validates no VM
dependencies remain. Cost savings realised.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Lift-and-shift is not real containerisation" | Lift-and-shift is a valid first step that delivers some container benefits (packaging, registry, deployment consistency) while deferring re-architecture. The anti-pattern is treating lift-and-shift as the final state. |
| "Containerising a database is too risky" | Stateful containerisation (databases on PersistentVolumes) is production-proven at scale (Kubernetes operators for PostgreSQL, MySQL, Cassandra). The risk is in the migration plan, not in the destination state. |
| "We should re-architect everything before containerising" | Re-architecture during containerisation doubles the risk and duration. Containerise first (re-platform), then re-architect from the stable container baseline. |
| "Migration is complete when all services are in containers" | Migration is complete when VMs are decommissioned. Services in containers with VMs still running is a "dual-stack" state that creates ongoing cost and complexity. |
| "The platform team should do the migration for all service teams" | Platform teams own the tooling and patterns. Service teams own the migration of their services. Centralising execution creates a bottleneck and removes service team ownership. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Dual-Stack Indefinite State**
**Symptom:** 60% of services are containerised after 12 months. VM costs
are not declining because the remaining 40% carry the infrastructure.
The migration is "stalled" and there is no completion date.
**Root Cause:** No VM decommission date creates no urgency. Service teams
deprioritise migration when product feature work competes. No mechanism
forces completion.
**Diagnostic:**

```bash
# Count services still on VMs vs. containers
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].Tags' | \
  grep -c "workload"

kubectl get deployments -A | grep -v kube-system | wc -l
```

**Fix:** Announce a hard VM decommission date. Schedule a chargeback
policy that increases VM costs progressively after the target date.
Assign migration completion as a platform team KPI.
**Prevention:** Set VM decommission dates at programme start. Make the
dual-stack cost visible (dollar amount per month) to service teams.

---

**Failure Mode 2: Loss of Data During Stateful Migration**
**Symptom:** A containerised database pod restarts and the data directory
is empty. Data loss has occurred. The backup has not been tested.
**Root Cause:** Database containerised without a PersistentVolume; data
was stored in the container ephemeral layer, which is discarded on
restart.
**Diagnostic:**

```bash
# Check if a pod uses persistent volumes
kubectl describe pod db-pod-xxx | grep -A 5 Volumes

# Check if PVC is bound
kubectl get pvc -n production

# Verify data survived a pod restart
kubectl delete pod db-pod-xxx  # force restart
kubectl exec -it db-pod-new-xxx -- \
  psql -c "SELECT COUNT(*) FROM critical_table"
```

**Fix:** Always use PersistentVolumeClaims for stateful workloads.
Test restore from backup before migrating to production.
**Prevention:** Operational readiness gate must include "backup tested"
for all stateful services. Never migrate a stateful service without
a validated restore procedure.

---

**Failure Mode 3: Hidden Dependency on VM Infrastructure (Security)**
**Symptom:** A containerised service fails to start in production. It
cannot reach a hardcoded internal DNS hostname that only exists in the
VM network (e.g., `ldap.internal.corp`).
**Root Cause:** Pre-migration dependency audit missed a hardcoded network
dependency. The VM network had custom DNS entries that the Kubernetes
DNS does not have.
**Diagnostic:**

```bash
# Test DNS resolution from inside the container
kubectl run dns-test --image=busybox:latest \
  --restart=Never --rm -it -- \
  nslookup ldap.internal.corp

# Capture all DNS queries the app makes at startup
kubectl exec -it <pod> -- \
  tcpdump -i any port 53 -n
```

**Fix:** Add an ExternalName Service or CoreDNS entry to resolve the
legacy hostname. Migrate the dependency to a container-native equivalent.
**Prevention:** Run the dependency audit script against all services
before migration planning. Include network dependency mapping.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-001 - What Is Containerization and Why It Matters]] - containerisation fundamentals
- [[CTR-047 - Container Platform Strategy]] - choose the platform before migrating
- [[CTR-049 - Container Image Strategy at Scale]] - image strategy for migrated services

**Builds On This (learn these next):**

- [[CTR-056 - Container Trade-off Framing]] - evaluate the trade-offs of containerising
- [[CTR-011 - Containerization Necessity Assessment]] - assess whether to containerise at all

**Alternatives / Comparisons:**

- [[CTR-056 - Container Trade-off Framing]] - when not to containerise
- [[CTR-011 - Containerization Necessity Assessment]] - is containerisation the right move?

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Phased plan to move to containers   │
│ PROBLEM     │ Big-bang migrations fail; stalling  │
│ KEY INSIGHT │ Stateless first, gates before waves │
│ USE WHEN    │ Migrating VM workloads to containers │
│ AVOID WHEN  │ N/A - always apply a strategy       │
│ TRADE-OFF   │ Migration speed vs. dual-stack cost │
│ ONE-LINER   │ Phase, gate, decommission, repeat  │
│ NEXT EXPLORE│ CTR-056 Trade-offs, CTR-011 Assess  │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Sequence matters: stateless before stateful, low-risk before high-risk,
   pilot before bulk.
2. Operational readiness gate (CI/CD, logging, metrics, secrets) must
   pass before any production migration - not after.
3. Set a hard VM decommission date - without it, the migration stalls
   indefinitely in the "mostly containerised" state.

**Interview one-liner:**
"Containerisation migration strategy is primarily a sequencing and gate
problem: migrate stateless services first to build capability, enforce
an operational readiness gate before each wave, and set a hard VM
decommission date to prevent permanent dual-stack operation."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Phased migrations with hard gates and decommission deadlines succeed;
big-bang migrations and open-ended dual-stack periods fail. The gate
ensures quality; the decommission deadline ensures completion. Both
are required - a gate without a deadline creates indefinite delay;
a deadline without a gate creates a rushed, low-quality migration.

**Where else this pattern appears:**

- **Database migrations:** Blue-green database migration: migrate reads
  to the new database, validate, migrate writes, validate, decommission
  the old database. Each step has a gate and a rollback path.
- **Cloud migration:** AWS Migration Acceleration Program uses the same
  wave-and-gate structure: assess, mobilise, migrate/modernise. The
  decommission date for on-premises data centres creates the urgency.
- **Software framework upgrades:** Upgrading a monolith from Java 8 to
  Java 21: compile and test in Java 8 mode first, fix deprecation warnings,
  migrate to Java 11, validate, migrate to Java 17, validate, migrate to
  Java 21. Phased with gates, not a single jump.

---

### 💡 The Surprising Truth

The biggest bottleneck in containerisation migrations is not
containerising the application - it is eliminating implicit dependencies
on the VM environment that no one documented. Services that ran
unmodified on VMs for years often depend on: the VM hostname being stable
(not ephemeral), a syslog daemon being present on the host, SSH access
for debugging, a cron daemon running in the same OS environment as the
application, or a specific kernel version for a native library. These
dependencies are invisible until the service runs in a container and
breaks. Organisations that invest in a pre-migration dependency audit
reduce their migration stalls by 60-70% compared to those that discover
dependencies during the migration.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A service team argues that re-architecting
their monolith (splitting into 5 microservices) should happen before
containerisation because "containers for a monolith are pointless." A
platform team argues for containerising first. What are the risks of
each approach, and what evidence would help decide?
*Hint:* Consider: re-architecture risk during migration doubles the
variables in play. A containerised monolith still benefits from
consistent deployment, registry management, and resource limits. What
are the failure modes if the re-architecture is incomplete when the VM
decommission deadline arrives?

**Q2 (B - Scale):** An organisation is migrating 200 services over 12
months. The platform team has 4 engineers. What are the two structural
approaches to scaling migration execution, and what governance mechanism
ensures quality does not degrade as execution scales?
*Hint:* Consider: centralised execution (platform team migrates all
services - bottleneck) vs. distributed execution (service teams execute
with platform team templates and gates). How does the operational
readiness gate function as a quality control in the distributed model?

**Q3 (A - System Interaction):** A service uses a persistent local file
cache on the VM filesystem for performance (cache files written to
`/var/cache/myservice/`). The cache is rebuilt from scratch on every
restart (takes 5 minutes). After containerisation, every pod restart
rebuilds the cache, causing 5-minute cold starts. How do you solve this
in the Kubernetes environment?
*Hint:* Consider: PersistentVolumeClaim (RWO) for single-pod cache,
emptyDir (lost on restart), Redis/Memcached for shared cache, or a
shared ReadWriteMany PVC. What are the trade-offs of each approach for
a service that scales to 10 replicas?