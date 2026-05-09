---
id: CTR-003
title: The Container Ecosystem Map
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★☆☆
depends_on: CTR-001, CTR-002
used_by: CTR-008, CTR-009
related: CTR-009, CTR-025, CTR-026
tags:
  - containers
  - docker
  - foundational
  - mental-model
  - architecture
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 3
permalink: /containers/the-container-ecosystem-map/
---

# CTR-003 - The Container Ecosystem Map

⚡ **TL;DR -** The container ecosystem spans build tools, runtimes, registries,
and orchestrators - understanding the map prevents picking tools blindly.

| | |
|---|---|
| **Depends on** | CTR-001, CTR-002 |
| **Used by** | CTR-008, CTR-009 |
| **Related** | CTR-009, CTR-025, CTR-026 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A developer reads "use containers" and immediately
installs Docker. Six months later the team is using `docker-compose` in
production, has no image scanning, tags everything `latest`, and wonders
why the security team is raising flags. They don't know what they don't know
because nobody gave them a map of the full ecosystem.

**THE BREAKING POINT:** Container tooling has exploded since 2013. There are
now competing runtimes (`docker`, `containerd`, `CRI-O`, `podman`), image
formats (OCI, Docker V2 schemas), registries (Docker Hub, ECR, GCR, GHCR),
security scanners (`trivy`, `grype`, `snyk`), build tools (`docker build`,
`buildah`, `kaniko`, `buildkit`), and orchestrators (Kubernetes, Nomad, ECS).
Without a map, engineers are paralysed by choice or, worse, commit to the
wrong tool for their scale.

**THE INVENTION MOMENT:** The container standard war ended with OCI (Open
Container Initiative, 2015). Once the image format and runtime spec were
standardised, the ecosystem split cleanly into four layers: Build, Distribute,
Run, and Orchestrate. Every tool in the ecosystem lives in one of these layers.

**EVOLUTION:** 2013: Docker ships one monolithic tool for all four layers.
2016: Kubernetes rises; Docker Swarm loses the orchestration war. 2017: OCI
formalises image and runtime specs. 2018: `containerd` extracted from Docker;
`CRI-O` emerges. 2019-2022: `podman`/`buildah` as daemonless Docker
alternatives. 2023+: Supply-chain security (SBOMs, attestations, Sigstore)
becomes a fifth layer that runs across the other four.

---

### 📘 Textbook Definition

The **container ecosystem** is the set of standardised tools, specifications,
and platforms that collectively implement the build-distribute-run-orchestrate
lifecycle for OCI-compliant container images. It is structured into four
functional layers: (1) **Build** - tools that create container images;
(2) **Distribute** - registries that store and serve images; (3) **Run** -
container runtimes that execute images as isolated processes; (4) **Orchestrate** -
platforms that schedule, scale, and manage containers across hosts.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Four layers - build, store, run, orchestrate - and every
container tool lives in exactly one of them.

> The container ecosystem is like a supply chain for physical goods: a factory
> (build tools) manufactures a product, a warehouse (registry) stores it, a
> delivery driver (container runtime) delivers it to a customer's door, and a
> logistics company (orchestrator) coordinates thousands of deliveries
> simultaneously.

**One insight:** OCI standardisation is what makes the layers interchangeable.
You can build with `buildah`, push to ECR, pull with `containerd`, and
orchestrate with Kubernetes - because all layers speak the same standard.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every container journey starts with an OCI image (built by a build tool)
2. Images are stored in and distributed from registries
3. A runtime executes an image as a container on a Linux host
4. An orchestrator manages many containers across many hosts

**DERIVED DESIGN:** The four-layer model follows naturally from the lifecycle
of any software artifact: create → store → execute → manage. Container
tooling maps directly onto this generic pattern. OCI standards are the APIs
between layers - any OCI-compliant tool can plug into any layer.

**THE TRADE-OFFS:**
**Gain:** Modularity - swap build tools without changing the runtime; switch
registries without changing the orchestrator.
**Cost:** More moving parts; integration complexity; each layer has its own
authentication, security model, and failure modes.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The four-layer structure is inherent in the problem of packaging,
distributing, running, and managing software at scale.
**Accidental:** The proliferation of competing tools within each layer (Docker
vs Podman, Docker Hub vs ECR vs GCR) is ecosystem fragmentation, not
fundamental complexity.

---

### 🧪 Thought Experiment

**SETUP:** You need to run a containerised app in production. The only tool
you know is `docker run`.

**WHAT HAPPENS WITHOUT AN ECOSYSTEM MAP:** You run `docker run` on one server.
It works. You need three instances for availability. You `docker run` on three
servers manually. An instance crashes at 2 AM. Nobody restarts it. You add
a cron job. The cron job is on the server that crashed. You have no image
scanning. Your image has 47 critical CVEs.

**WHAT HAPPENS WITH AN ECOSYSTEM MAP:** You build with `Dockerfile` + Docker
BuildKit, push to ECR (registry), scan with `trivy` (security layer), deploy
to Kubernetes (orchestrator) which manages replicas, health checks, rolling
updates, and automated restarts. Each layer does one job well.

**THE INSIGHT:** "Just use Docker" is fine for one server. The ecosystem
exists because real production has multiple hosts, failures, updates, and
security requirements that a single tool cannot address.

---

### 🧠 Mental Model / Analogy

> The container ecosystem is like a postal system. A printer (build tool)
> produces a package. A post office (registry) stores and routes it. A
> van driver (container runtime) delivers it to a specific address.
> A logistics network (orchestrator) coordinates thousands of drivers,
> tracks deliveries, and reroutes when a van breaks down.

- **Build tools** (`docker build`, `buildah`, `kaniko`) → the printer/packager
- **Registries** (Docker Hub, ECR, GCR, GHCR) → post office and warehouse
- **Container runtimes** (`runc`, `containerd`, `CRI-O`) → the delivery driver
- **Orchestrators** (Kubernetes, Nomad, ECS) → the logistics network
- **OCI spec** → the standard parcel dimensions all systems agree on

Where this analogy breaks down: Unlike packages, container images are
immutable and infinitely copyable at near-zero cost once stored in a registry.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Think of it like a factory-to-customer chain. Someone builds the product
(build tools), it goes into a warehouse (registry), a driver delivers it
(runtime), and a courier company manages thousands of deliveries at once
(orchestrator).

**Level 2 - How to use it (junior developer):**
Start with Docker: `docker build` (build layer), `docker push` to Docker Hub
(registry layer), `docker run` (runtime layer). For production with multiple
instances, add Kubernetes (orchestration layer). For security, add `trivy`
image scanning between build and push.

**Level 3 - How it works (mid-level engineer):**
Each layer communicates through standards. Build tools produce OCI images
(OCI Image Spec). Registries serve images via OCI Distribution Spec (HTTP
API). The Container Runtime Interface (CRI) is the API between Kubernetes
and low-level runtimes like `containerd`. `containerd` calls `runc` (OCI
Runtime Spec) to actually create the container namespaces and cgroups.
Security scanning tools (Trivy, Grype) inspect image layer SBOMs for known
CVEs in the NVD and OSV databases.

**Level 4 - Why it was designed this way (senior/staff):**
The ecosystem started as a Docker monolith intentionally - shipping one tool
lowered the adoption barrier. As Kubernetes emerged, the monolith became a
liability: Kubernetes needed to plug in any runtime, not just Docker's daemon.
This forced the extraction of `containerd` (runtime) from Docker Engine and
the CRI specification (interface between k8s and runtime). The OCI specs
completed the decoupling. This is a classic example of a monolith being
deliberately decomposed under competitive pressure into a standards-based
ecosystem. The lesson for platform engineers: the current Docker monolith
experience is a convenience abstraction over a four-layer architecture that
you need to understand when it breaks.

**Expert Thinking Cues:**
- When debugging a container issue, identify which layer it lives in first:
  is it a build problem (image corrupt?), registry problem (pull fails?),
  runtime problem (OOM killed?), or orchestration problem (scheduling failed?)?
- "Docker" refers to four things: the company, the daemon, the CLI, and the
  image format. Be precise about which you mean.

---

### ⚙️ How It Works (Mechanism)

**ECOSYSTEM LAYER MAP:**

```
┌───────────────────────────────────────────┐
│  LAYER 4: ORCHESTRATE                     │
│  Kubernetes  ECS  Nomad  OpenShift        │
├───────────────────────────────────────────┤
│  LAYER 3: RUN (Container Runtime)         │
│  containerd  CRI-O  Docker Engine         │
│  └─ calls → runc  (OCI Runtime)           │
├───────────────────────────────────────────┤
│  LAYER 2: DISTRIBUTE (Registry)           │
│  Docker Hub  ECR  GCR  GHCR  Quay        │
├───────────────────────────────────────────┤
│  LAYER 1: BUILD                           │
│  docker build  buildah  kaniko  buildkit  │
└───────────────────────────────────────────┘
         ← OCI standard links all layers →
```

**KEY STANDARDS LINKING LAYERS:**
- **OCI Image Spec** → build → registry handoff
- **OCI Distribution Spec** → registry → runtime handoff
- **OCI Runtime Spec** → runtime → Linux kernel handoff
- **CRI (Container Runtime Interface)** → orchestrator → runtime handoff

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Developer writes Dockerfile
         │
         ▼
  Build (Layer 1)        ← YOU ARE HERE
  docker build / kaniko
  → OCI image created
         │
         ▼
  Scan (Security)
  trivy image / grype
         │
         ▼
  Push (Layer 2)
  docker push → Registry
         │
         ▼
  Schedule (Layer 4)
  Kubernetes pod spec
         │
         ▼
  Pull + Run (Layer 3)
  containerd pulls from registry
  runc creates container
         │
         ▼
  Running Container
```

**FAILURE PATH:**
- Build fail → `Dockerfile` error; fix and rebuild
- Scan fail → critical CVE; update base image and rebuild
- Push fail → auth error; `docker login` and retry
- Pull fail → registry unreachable; check network/DNS, use pull-through cache
- Runtime fail → OOM, seccomp block; check `dmesg` and cgroup limits

**WHAT CHANGES AT SCALE:**
At 1,000 pods: the registry becomes a hot read path - use regional replicas
or pull-through caches. Image scan time matters for CI speed - cache scan
results by image digest. CRI authentication at scale requires credential
refresh mechanisms (IRSA for ECR on EKS).

---

### ⚖️ Comparison Table

| Layer | Open Source Options | Managed Options |
|-------|------------------|-----------------|
| Build | `docker build`, `buildah`, `kaniko` | Cloud Build, CodeBuild |
| Registry | Harbor, Distribution | ECR, GCR, GHCR, ACR |
| Runtime | `containerd`, `CRI-O`, `runc` | Managed K8s nodes |
| Orchestrate | Kubernetes, Nomad | EKS, GKE, AKS, ECS |
| Scan | `trivy`, `grype`, `syft` | ECR scan, Prisma, Snyk |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Docker is the container runtime in Kubernetes" | Kubernetes deprecated Docker as a runtime (v1.20+). It uses containerd or CRI-O via the CRI. |
| "Docker Hub is the only registry" | ECR, GCR, GHCR, Quay, and self-hosted Harbor are all OCI-compatible alternatives. |
| "The orchestrator starts containers" | The orchestrator schedules and manages. The container runtime (containerd/runc) actually creates container processes. |
| "You need Docker installed to run containers on Kubernetes" | False. Kubernetes uses the CRI to talk to containerd or CRI-O directly - Docker is not required. |
| "Build tools and runtimes are the same" | They are separate layers. You build an image once; you run it many times on different runtimes across different hosts. |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong Layer Diagnosis - Wasted Debug Time**

**Symptom:** Team spends hours debugging a "container crash" that is actually
a Kubernetes scheduling failure (pod never starts, crashes at zero).
**Root Cause:** No framework for which layer the failure originated in.
**Diagnostic:**
```bash
# Identify the layer
kubectl describe pod <name>   # orchestration layer
kubectl get events --field-selector involvedObject.name=<pod>
crictl ps -a                  # runtime layer
journalctl -u containerd      # runtime logs
```
**Fix:** Always start diagnosis at the highest layer (orchestrator events)
and work down.
**Prevention:** Document the four layers in your runbook; train on each
layer's diagnostic commands.

---

**2. Registry Authentication Failure at Scale**

**Symptom:** Image pulls fail across all nodes simultaneously after ~1 hour
(token expiry).
**Root Cause:** ECR tokens expire after 12 hours; static credentials in
Kubernetes secrets expire.
**Diagnostic:**
```bash
kubectl get events -A | grep "Failed to pull image"
crictl pull <image>  # test pull on node
```
**Fix:** Use IRSA (IAM Roles for Service Accounts) on EKS for automatic
credential refresh; or use a registry credential helper.
**Prevention:** Never use static ECR tokens in long-running workloads.
Use dynamic credential mechanisms native to your cloud provider.

---

**3. Security - Public Registry Pull Without Scanning**

**Symptom:** Production image has known critical CVEs; security team audit
failure; compliance finding.
**Root Cause:** Images pulled from Docker Hub without scanning in CI pipeline.
**Diagnostic:**
```bash
trivy image nginx:latest
# Scans all layers for CVEs in NVD/OSV
```
**Fix:** Add scanning to CI between build and push; block on CRITICAL/HIGH
severity CVEs.
**Prevention:** Enforce via admission policy in Kubernetes (Kyverno, OPA
Gatekeeper) that only allows images from approved, scanned registries.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `[[CTR-001 - What Is Containerization and Why It Matters]]`
- `[[CTR-002 - VMs vs Containers - A Mental Model]]`

**Builds On This (learn these next):**
- `[[CTR-009 - Docker]]` - the build + runtime toolchain
- `[[CTR-016 - Container Registry]]` - the distribution layer
- `[[CTR-025 - containerd]]` - the production runtime
- `[[CTR-026 - Container Orchestration]]` - the orchestration layer
- `[[CTR-024 - OCI Standard]]` - the standards linking all layers

**Alternatives / Comparisons:**
- `[[CTR-035 - Podman]]` - Docker-compatible daemonless alternative
- `[[CTR-036 - Buildah]]` - daemonless image build tool
- `[[CTR-042 - Container Runtime Interface (CRI)]]` - the runtime API

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────┐
│ WHAT IT IS    4-layer ecosystem: build,      │
│               registry, runtime, orchestrate │
│ PROBLEM       Engineers pick tools without   │
│               understanding which layer      │
│               each tool addresses            │
│ KEY INSIGHT   OCI standards link all layers; │
│               any OCI tool works together    │
│ USE WHEN      Planning containerization      │
│               strategy or debugging failures │
│ AVOID WHEN    N/A - this is a mental model,  │
│               not a tool                     │
│ TRADE-OFF     Modularity vs complexity -     │
│               more layers = more joints      │
│ ONE-LINER     Build → Store → Run →          │
│               Orchestrate, linked by OCI     │
│ NEXT EXPLORE  CTR-009, CTR-024, CTR-025      │
└──────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Four layers: Build, Distribute (Registry), Run (Runtime), Orchestrate
2. OCI standards are the contracts between layers - enabling tool swaps
3. Kubernetes does NOT use Docker runtime - it uses containerd/CRI-O via CRI

**Interview one-liner:** "The container ecosystem has four layers - build,
registry, runtime, orchestration - connected by OCI standards that let any
compliant tool plug into any layer."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Complex systems should be decomposed into
layers with standardised interfaces between them. The interface standard
(OCI, in this case) is more valuable than any individual tool - it enables
competition and evolution within each layer without breaking the system.

**Where else this pattern appears:**
- **TCP/IP network stack** - four layers (Application, Transport, Network,
  Link) with standardised protocols between; any compliant implementation
  can be swapped at each layer
- **CI/CD pipeline** - build, test, artifact store, deploy are four stages
  linked by artifact handoffs; each stage tool (Jenkins, GitHub Actions,
  Nexus, ArgoCD) is independently replaceable
- **Database access layers** - JDBC/ODBC (interface spec) between application
  and database allows driver swaps without changing application code

---

### 💡 The Surprising Truth

When Kubernetes deprecated Docker as a container runtime in v1.20 (2020),
it triggered widespread panic - articles declared "Docker is dead!" In
reality, nothing changed for 99% of Docker users. Docker images still worked.
The only thing removed was the `dockershim` adapter that let Kubernetes call
Docker's daemon instead of a proper CRI runtime. The images themselves - OCI
format - continued to work identically. The panic revealed how poorly
engineers understood the layer separation: "Docker" the image format (which
lived in the build/registry layer) was confused with "Docker" the runtime
(which Kubernetes was replacing). Four distinct tools wore the same name.

---

### 🧠 Think About This Before We Continue

1. **(Type A - System Interaction)** When a Kubernetes node loses network
   access to the container registry during a rolling update, what happens
   to pods already running on that node vs new pods being scheduled? Which
   layer causes the failure, and which layer detects it?

   *Hint:* Examine how `imagePullPolicy: Always` vs `IfNotPresent` changes
   the registry dependency at pod startup. Look at how containerd caches
   pulled layers locally.

2. **(Type B - Scale)** At 500 CI pipeline runs per day, each building and
   scanning a 200 MB image, the registry and scan cache become hot paths.
   What architectural choices in the build and distribute layers reduce
   redundant work and latency for developers?

   *Hint:* Investigate BuildKit layer caching (remote cache backends),
   Trivy DB caching, and how image digest-based deduplication in OCI
   registries avoids storing duplicate layers.

3. **(Type C - Design Trade-off)** The OCI standardisation split Docker's
   monolith into four interchangeable layers. But interchangeability requires
   every team to know which tool lives in which layer and how to configure
   the interfaces. What is the operational cost of this modularity, and
   under what conditions does a "one vendor, all layers" platform (like
   Docker Desktop or a fully managed EKS + ECR stack) justify the lock-in?

   *Hint:* Compare the operational model of a team using Docker Desktop
   (build+run+compose in one tool) vs a team maintaining separate buildah,
   Harbor registry, containerd config, and Kubernetes - at different scales.
