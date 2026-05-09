# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\write_ctr_b1.ps1
Set-Location "C:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-6-infrastructure-devops\CTR-containers"

# ── CTR-043 ──────────────────────────────────────────────────────────────
$ctr043 = @'
---
id: CTR-043
title: Container Platform Strategy
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-003, CTR-009, CTR-026, CTR-042
used_by: CTR-044, CTR-045, CTR-046
related: CTR-047, CTR-052
tags:
  - containers
  - docker
  - kubernetes
  - architecture
  - bestpractice
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /ctr/container-platform-strategy/
---

# CTR-043 - Container Platform Strategy

⚡ TL;DR - Choose the container orchestration platform that matches your team's operational maturity and workload scale - not your aspirational growth target.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | CTR-003, CTR-009, CTR-026, CTR-042 |     |
| **Used by:**    | CTR-044, CTR-045, CTR-046          |     |
| **Related:**    | CTR-047, CTR-052                   |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A startup adopts Docker because it is popular. A year later, the team
adds Kubernetes because blog posts say it is the right next step. Nobody
asks whether 10 services and 5 engineers need a full Kubernetes cluster.
The platform consumes more engineering time than the product it runs.

**THE BREAKING POINT:**
An enterprise migrates 200 services to containers. Each team picks its
own orchestrator: some use Kubernetes, some Docker Swarm, some bare
Docker Compose on EC2. Secrets management, networking, and observability
are solved four different ways. The "container strategy" has become a
container fragmentation problem.

**THE INVENTION MOMENT:**
Container platforms follow a capability/complexity curve. Docker alone
handles single-host deployments. Compose handles multi-service local and
small production. Kubernetes handles multi-host, multi-team, production-
grade workloads. Strategy is about matching the platform to today's
actual needs, not aspirational scale.

**EVOLUTION:**
2013: Docker standalone. 2015: Compose, Swarm, and Kubernetes compete.
2017: Kubernetes wins the orchestration war. 2019: Managed Kubernetes
(EKS, GKE, AKS) removes cluster-operations burden. 2021: Serverless
containers (Fargate, Cloud Run) offer orchestration without node
management. 2023: Internal Developer Platforms (IDPs) abstract
Kubernetes behind self-service APIs. Strategy now includes the question
"IDP or raw Kubernetes?"

---

### 📘 Textbook Definition

**Container platform strategy** is the deliberate selection and
governance of the container runtime, orchestration layer, registry,
security toolchain, and observability stack across an organisation. It
answers: what platform runs containers, who operates it, how services
are deployed, and how the platform evolves as the organisation scales.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Match your container platform to your actual complexity, not your
aspirational scale.

**One analogy:**

> Choosing a container platform is like choosing a kitchen: a solo chef
> needs a home kitchen (Docker Compose); a restaurant needs a commercial
> kitchen (managed Kubernetes); a hotel chain needs a commissary kitchen
> (multi-cluster platform engineering). Installing a commissary kitchen
> in a studio apartment is expensive and unnecessary.

**One insight:**
The most common container platform mistake is choosing Kubernetes before
the team has the operational maturity to run it. The second most common
is staying on Docker Compose after outgrowing it. The strategy question
is fundamentally a timing question.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Platform complexity must not exceed operational capacity** - a
   platform the team cannot operate safely in production is worse than
   a simpler platform operated well.
2. **Platform capability must meet workload requirements** - a platform
   that cannot deliver required availability, scaling, or isolation is
   a ceiling.
3. **Platform decisions have long half-lives** - migration between
   platforms is expensive; today's choice persists 2-5 years.
4. **Managed services shift ops burden to billing** - managed Kubernetes
   trades operational complexity for cost; usually worth it at scale.

**DERIVED DESIGN:**
Given invariant 1: start with the simplest platform the workload
requires. Add complexity only when the current platform is demonstrably
insufficient. Given invariant 3: evaluate platforms on a 3-year horizon,
not current needs alone.

**THE TRADE-OFFS:**
**Gain:** Matching platform to need reduces operational overhead,
accelerates developer velocity, and limits blast radius of failures.
**Cost:** Underestimating future needs leads to expensive re-
platforming. Overestimating leads to platform complexity that drains
engineering capacity.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any multi-service containerised system needs scheduling,
service discovery, health checking, and secrets management.
**Accidental:** Kubernetes YAML templating, CRD proliferation, and
multi-cluster federation beyond actual scale requirements.

---

### 🧪 Thought Experiment

**SETUP:**
A 12-person team runs 15 microservices serving 50,000 daily users.
They use Docker Compose in production on 3 EC2 instances.

**WHAT HAPPENS WITHOUT PLATFORM STRATEGY:**
When traffic doubles, the team adds more Compose instances. Service
discovery uses hardcoded IPs. A failed service is not restarted. Rolling
deployments are manual. An engineer spends a day per week on deployments.
The team adds Kubernetes "because it's time" and spends 3 months on
platform migration instead of product features.

**WHAT HAPPENS WITH PLATFORM STRATEGY:**
The team evaluates: 15 services, 3 nodes, need for auto-healing and
rolling deploys but not multi-cluster. Decision: managed Kubernetes (EKS)
with Fargate to eliminate node management. Migration takes 3 weeks.
Auto-healing, rolling deploys, and HPA are available from day one.

**THE INSIGHT:**
Platform strategy is not about choosing the "best" platform - it is
about choosing the right platform for the current team size, service
count, and operational maturity. The decision criteria are explicit and
revisited annually.

---

### 🧠 Mental Model / Analogy

> Think of container platform selection as choosing transportation. Docker
> alone is a bicycle - perfect for short local trips, zero infrastructure
> needed. Docker Compose is a car - handles most daily needs. Managed
> Kubernetes is a train - high capacity, someone else drives. Multi-
> cluster platform engineering is an airline network - maximum capacity,
> massive operational staff required.

Element mapping:

- **Distance** = number of services and nodes
- **Speed** = required deployment velocity
- **Driver** = operational maturity of the team
- **Fuel cost** = engineering time for platform operations
- **Passengers** = development teams consuming the platform

Where this analogy breaks down: transportation modes are mutually
exclusive; container platforms can be layered (Docker inside Kubernetes
inside a cloud provider), which has no direct transportation analogy.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Container platform strategy is deciding which software manages your
containers and making sure that decision matches your team's actual size
and skills.

**Level 2 - How to use it (junior developer):**
For a small project: Docker Compose. For production needing auto-restart,
rolling updates, and scaling: use managed Kubernetes (EKS, GKE, AKS).
Never manage your own Kubernetes control plane unless you have a
dedicated platform team.

**Level 3 - How it works (mid-level engineer):**
Evaluate platforms on 5 axes: scheduling (place containers on healthy
nodes), service discovery (find services without hardcoded IPs), secret
management (inject credentials securely), observability (see container
health and resource usage), and deployment strategy (rolling, blue-green,
canary). Docker Compose handles local dev and small production; Kubernetes
handles all axes at scale.

**Level 4 - Why it was designed this way (senior/staff):**
Container platforms decouple the application lifecycle from the
infrastructure lifecycle. The Kubernetes control loop model (desired state
vs. actual state) is the key insight: you declare what you want, the
platform converges to it. This handles node failures, restarts, and scale
events without human intervention. The strategy question is: at what scale
does the control loop benefit exceed the operational cost of running it?

**Expert Thinking Cues:**

- "What is our team's Kubernetes operational maturity? Can we debug a
  failing node or crashlooping pod under production pressure?"
- "At what service count does Docker Compose break for us specifically?"
- "What is the fully loaded cost of managing our own control plane vs.
  paying for a managed service?"

---

### ⚙️ How It Works (Mechanism)

**PLATFORM SELECTION DECISION TREE:**

```
Services 1-5, team 1-5, single host?
  └─ Docker Compose
Services 5-30, team 5-20, multi-host?
  └─ Managed Kubernetes (EKS/GKE/AKS)
Services 30+, teams 20+, multi-cluster?
  └─ Platform Engineering + GitOps
Stateless, bursty, no node management?
  └─ AWS Fargate or Google Cloud Run
```

**PLATFORM EVOLUTION PATH:**

```
Stage 1: Docker Compose (local + small prod)
  | Trigger: manual restarts, no auto-scaling
  v
Stage 2: Managed K8s (EKS/GKE) + Helm
  | Trigger: multi-team, env proliferation
  v
Stage 3: GitOps (ArgoCD) + Kustomize
  | Trigger: multi-cluster, multi-region
  v
Stage 4: Internal Developer Platform (IDP)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Platform Strategy Assessment
  │
  ├─ Assess: services, teams, scale, ops maturity
  │           ← YOU ARE HERE
  ├─ Choose: Compose / Managed K8s / Multi-cluster
  │
  ├─ Define: registry, secrets, observability, CI/CD
  │
  ├─ Implement: manifests, pipelines, monitoring
  │
  └─ Operate: on-call, upgrades, capacity planning
```

**FAILURE PATH:**
Team picks Kubernetes without completing the readiness checklist. First
production incident: a node goes NotReady. Team cannot diagnose (no
experience with `kubectl drain`, taints, or cordon). Incident lasts 4
hours. Fix: move to managed node groups or Fargate.

**WHAT CHANGES AT SCALE:**
At 30+ services, platform strategy must include GitOps (declarative
config management), progressive delivery (Argo Rollouts, Flagger), and
platform engineering (self-service namespaces, quotas, templates). The
platform becomes a product with its own roadmap.

---

### 💻 Code Example

```yaml
# BAD: no resource limits, no health checks, no restart policy
version: '3'
services:
  api:
    image: myapp:latest
    ports:
      - "8080:8080"
```

```yaml
# GOOD: production-ready Compose for small deployments
version: '3.8'
services:
  api:
    image: myapp:v1.4.2       # pinned tag, not :latest
    ports:
      - "8080:8080"
    restart: unless-stopped
    healthcheck:
      test: ["CMD","curl","-f","http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

```yaml
# GOOD: Kubernetes Deployment for production scale
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: api
        image: myapp:v1.4.2
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "1000m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

**How to test / verify correctness:**
For Compose: `docker compose config` validates the file. For Kubernetes:
`kubectl apply --dry-run=client -f deployment.yaml` validates the
manifest. Use `kubeval` or `kubeconform` in CI for schema validation.

---

### ⚖️ Comparison Table

| Platform | Best For | Ops Complexity | Auto-heal | Scaling |
|---|---|---|---|---|
| Docker Compose | Dev, small prod | Low | No | Manual |
| Docker Swarm | Simple clustering | Medium | Yes | Limited |
| Managed K8s (EKS/GKE) | Production multi-service | Medium | Yes | HPA/KEDA |
| Self-managed K8s | Regulated/air-gapped | High | Yes | Full |
| AWS Fargate | No node management | Low | Yes | Auto |
| Google Cloud Run | Stateless, burst workloads | Very Low | Yes | Auto |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Kubernetes is right for every production system" | Kubernetes is right when operational maturity, service count, and scale justify it. A 3-service startup on ECS Fargate outperforms a mismanaged Kubernetes cluster every time. |
| "Managed Kubernetes eliminates operational complexity" | Managed Kubernetes eliminates control plane operations only. Node management, networking, add-ons, upgrades, and application-layer issues remain your responsibility. |
| "Docker Compose is only for local development" | Compose is production-viable for small deployments (1-3 nodes, 1-10 services) with manual scaling accepted. Many startups run in production on Compose for years. |
| "Platform strategy is a one-time decision" | Platform strategy should be reviewed annually. Growth in services, team size, and traffic all shift the optimal platform choice. |
| "Serverless containers are always cheaper than Kubernetes" | Serverless containers can be 3-5x more expensive per vCPU at sustained high utilisation. They are cheaper at low or bursty utilisation. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Kubernetes Adopted Before Operational Readiness**
**Symptom:** Frequent incidents with long MTTR. Engineers spend more time
on platform issues than product features. On-call is overwhelmed.
**Root Cause:** Team lacks operational knowledge to diagnose and fix
Kubernetes failures (NotReady nodes, crashlooping pods, network policy).
**Diagnostic:**

```bash
# Check for chronic crashlooping pods
kubectl get pods -A | grep -v Running | grep -v Completed

# Check recent platform-level events
kubectl get events -A --sort-by='.lastTimestamp' | tail -20

# Check node health
kubectl get nodes -o wide
kubectl describe node <node> | grep -A 10 Conditions
```

**Fix:** Move to managed node groups (EKS managed, GKE Autopilot) to
eliminate node management. Add k9s or Lens for operational visibility.
**Prevention:** Complete a platform readiness checklist before production
adoption. Prefer Fargate or GKE Autopilot for teams without dedicated
platform engineers.

---

**Failure Mode 2: Platform Fragmentation Across Teams**
**Symptom:** Teams use Kubernetes, ECS, and Docker Compose on EC2.
Shared observability, secrets, and networking are impossible.
**Root Cause:** No platform strategy governance. Each team made
independent decisions.
**Diagnostic:**

```bash
# Audit container runtimes running in AWS
aws ecs list-clusters
aws eks list-clusters
# Check EC2 instances running containers directly
aws ec2 describe-instances \
  --filters "Name=tag:Workload,Values=container" \
  --query 'Reservations[*].Instances[*].InstanceId'
```

**Fix:** Define a golden path: one approved platform with standard
templates. Migrate outliers over 2 quarters.
**Prevention:** Establish a platform strategy document and review process
before team growth causes fragmentation.

---

**Failure Mode 3: Security Drift from Ungoverned Platform (Security)**
**Symptom:** CVE audit reveals containers running as root, host path
mounts, no resource limits, and privileged mode on several services.
**Root Cause:** No security baseline enforced at the platform level.
**Diagnostic:**

```bash
# Find privileged containers
kubectl get pods -A -o json | jq '
  .items[] |
  select(.spec.containers[].securityContext.privileged == true)
  | .metadata.name'
```

**Fix:** Implement Kyverno or OPA/Gatekeeper admission controllers to
enforce security baseline (no privileged, no root, resource limits
required).
**Prevention:** Security baselines enforced via admission control from
day one, not post-hoc audits.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-003 - The Container Ecosystem Map]] - the landscape this strategy navigates
- [[CTR-026 - Container Orchestration]] - what orchestrators do
- [[CTR-042 - Container Runtime Interface (CRI)]] - how runtimes plug in

**Builds On This (learn these next):**

- [[CTR-044 - Container Security Architecture]] - security layer on top of platform choice
- [[CTR-045 - Container Image Strategy at Scale]] - image management at platform scale
- [[CTR-046 - Containerization Migration Strategy]] - moving to your chosen platform

**Alternatives / Comparisons:**

- [[CTR-047 - Multi-Runtime Container Strategy (containerd, CRI-O)]] - runtime-layer choices
- [[CTR-052 - Container Trade-off Framing]] - trade-off framework for platform decisions

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Platform choice matched to team ops  │
│ PROBLEM     │ Platform complexity exceeds team ops  │
│ KEY INSIGHT │ Match platform to NOW, not aspirations│
│ USE WHEN    │ Evaluating / changing container stack │
│ AVOID WHEN  │ N/A - always apply before choosing   │
│ TRADE-OFF   │ Simplicity vs. capability ceiling    │
│ ONE-LINER   │ Right platform, right maturity, now  │
│ NEXT EXPLORE│ CTR-044 Security, CTR-046 Migration  │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Platform complexity must not exceed operational maturity - a
   mismanaged complex platform is worse than a well-run simple one.
2. Managed services (EKS, GKE, Fargate) shift ops burden to billing -
   almost always worth it without a dedicated platform team.
3. Platform strategy is reviewed annually, not set once - growth
   changes the optimal answer.

**Interview one-liner:**
"Container platform strategy is matching orchestration complexity to team
operational maturity and workload scale - choosing Kubernetes before the
team can operate it confidently creates more risk than the simpler
alternative it replaced."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Match tooling complexity to team capability and problem size. A tool too
powerful for the team operating it creates more risk than a simpler tool
operated expertly. The right tool is the simplest tool the team can
operate reliably under production conditions.

**Where else this pattern appears:**

- **Database selection:** A distributed SQL database requires significant
  operational expertise. A team without it is better served by managed
  RDS PostgreSQL even if the distributed database has better theoretical
  properties.
- **Message queue selection:** Apache Kafka provides high throughput but
  requires KRaft management. A team handling 10,000 messages/day is
  better served by SQS with zero operational overhead.
- **Observability stack:** A full self-managed stack (Prometheus + Thanos
  + Grafana + Loki) is powerful but demanding. Managed alternatives
  (Datadog, Grafana Cloud) are operated reliably at a fraction of the
  engineering effort.

---

### 💡 The Surprising Truth

Kubernetes was not designed to be the default container platform - it was
designed for Google's Borg workload at Google scale. The CNCF survey
consistently shows that most Kubernetes adopters use fewer than 10% of
Kubernetes features in production. The most-used features (Deployments,
Services, ConfigMaps, Secrets) are available in simpler platforms like
Docker Swarm or ECS. The industry converged on Kubernetes not because it
is optimal for most use cases, but because it won the vendor ecosystem
battle - every cloud provider, monitoring vendor, and tool vendor
supports it first.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A team of 8 engineers runs 12 services.
They are evaluating self-managed Kubernetes vs. AWS Fargate. Fargate
costs 40% more per vCPU but requires no node management. What factors
make Fargate worth the premium, and what factors favour self-managed K8s?
*Hint:* Consider the fully-loaded cost of node management time (on-call,
upgrades, patching) vs. the cost premium. At what engineer hourly rate
does the time saved break even?

**Q2 (B - Scale):** An organisation currently runs 15 services on Docker
Compose across 5 engineers. They project 50 services and 25 engineers in
18 months. At what point should they start the Kubernetes migration, and
why does the migration itself create a risk window?
*Hint:* Consider lead time for platform adoption (3-6 months for a team
new to Kubernetes), and the operational stability required during
migration when both platforms coexist.

**Q3 (A - System Interaction):** A platform team adopts Kubernetes with a
GitOps model (ArgoCD). A developer wants to `kubectl apply` a hotfix
directly to production. What are the risks of allowing this, and what
platform controls preserve emergency deployment capability?
*Hint:* Consider RBAC, ArgoCD sync policies, and a "break-glass"
procedure that bypasses GitOps safely under incident conditions.
'@

# ── CTR-044 ──────────────────────────────────────────────────────────────
$ctr044 = @'
---
id: CTR-044
title: Container Security Architecture
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-017, CTR-018, CTR-021, CTR-023
used_by: CTR-051, CTR-054
related: CTR-022, CTR-040
tags:
  - containers
  - security
  - architecture
  - advanced
  - bestpractice
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /ctr/container-security-architecture/
---

# CTR-044 - Container Security Architecture

⚡ TL;DR - Container security architecture is defense-in-depth applied to containers: secure the image, the runtime, the network, the secrets, and the admission layer - each independently, all together.

| Metadata        |                               |     |
| :-------------- | :---------------------------- | :-- |
| **Depends on:** | CTR-017, CTR-018, CTR-021, CTR-023 |     |
| **Used by:**    | CTR-051, CTR-054              |     |
| **Related:**    | CTR-022, CTR-040              |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team secures their application code carefully but runs it in a
container as root, with all Linux capabilities, mounting the host
filesystem, and pulling images from an unscanned registry. The container
isolation they thought they had is largely illusory.

**THE BREAKING POINT:**
A container escape vulnerability is disclosed (e.g. runc CVE-2019-5736).
An attacker who can execute code inside a container can overwrite the
host runc binary and achieve host root access. Teams without image
scanning, non-root enforcement, or admission control have no compensating
controls and no detection layer.

**THE INVENTION MOMENT:**
Container security architecture applies the same defense-in-depth
principle that secures networks and operating systems: no single control
is sufficient, and controls at different layers must independently block
or detect attacks. The layers for containers are: supply chain (image),
runtime (process), network (traffic), secrets (credentials), and
admission (policy enforcement).

**EVOLUTION:**
2015: Docker introduces user namespaces for rootless containers.
2018: OPA/Gatekeeper brings policy-as-code to Kubernetes admission.
2019: Falco provides runtime threat detection. 2020: Sigstore launches
for image signing and supply chain integrity. 2022: SLSA framework
standardises supply chain security levels. 2023: eBPF-based runtime
security (Tetragon, Cilium) provides kernel-level observability without
kernel modules.

---

### 📘 Textbook Definition

**Container security architecture** is the structured application of
security controls across the container lifecycle: image build and supply
chain, registry storage, runtime execution, network traffic, secrets
management, and admission policy enforcement. Each layer provides
independent protection; the combination achieves defense-in-depth.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Secure the image, the runtime, the network, and the admission gate -
independently and together.

**One analogy:**

> Container security is like physical building security: the supply chain
> control is vetting construction materials (image scanning); the runtime
> control is locking the doors (non-root, capabilities dropped); the
> network control is CCTV and access cards (network policies); the
> admission control is the security guard at the entrance (OPA/Kyverno).
> A thief who bypasses the guard can still be stopped by the locked door.

**One insight:**
The most dangerous container security posture is "secure application
code inside an insecure container." Application-level security is
necessary but cannot compensate for running as root, with host
privileges, or with unscanned images.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Containers are not VMs** - they share the host kernel. A kernel
   exploit defeats all container isolation unless additional controls
   (gVisor, Kata) add a separate kernel boundary.
2. **Least privilege applies to containers** - run as non-root, drop
   all capabilities not required, use read-only root filesystem.
3. **Images are the primary attack surface** - a vulnerable base image
   exposes all containers built from it; scanning must be continuous.
4. **Admission control is the last-resort gate** - enforce security
   policy at the cluster level so individual teams cannot bypass it.

**DERIVED DESIGN:**
Given invariant 1: assume the kernel can be reached from any container.
Add compensating controls (seccomp, AppArmor, gVisor) to reduce the
kernel attack surface. Given invariant 3: scan images in CI, at push,
and continuously in the registry (images age poorly).

**THE TRADE-OFFS:**
**Gain:** Each independent control layer reduces the probability of a
successful attack reaching the host or adjacent workloads.
**Cost:** Each control adds operational overhead (policy maintenance,
false positives in scanning, admission webhook latency).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Non-root, no privileged mode, network policies, image
scanning, secrets not in environment variables - these address real
attack vectors.
**Accidental:** Overlapping policy engines (OPA + Kyverno + PSP all
at once), scanning tools with unconfigured thresholds that block all
deployments.

---

### 🧪 Thought Experiment

**SETUP:**
A Kubernetes cluster runs 30 microservices. All containers run as UID 0
(root). Images are pulled from DockerHub with no scanning. Secrets are
injected as environment variables.

**WHAT HAPPENS WITHOUT CONTAINER SECURITY ARCHITECTURE:**
A remote code execution vulnerability in one service gives an attacker
shell access inside the container as root. Because the container runs as
root and has the `SYS_ADMIN` capability, the attacker mounts the host
filesystem, reads secrets from environment variables of other containers
via the Kubernetes API (if RBAC is misconfigured), and pivots to the
host. The blast radius is the entire cluster.

**WHAT HAPPENS WITH CONTAINER SECURITY ARCHITECTURE:**
The attacker achieves RCE in the container. The container runs as UID
1000 (non-root), has no capabilities beyond the minimum set, uses a
read-only root filesystem, and runs with a seccomp profile that blocks
unusual syscalls. The network policy prevents lateral movement to other
services. Falco detects the anomalous shell execution and alerts. The
blast radius is one container.

**THE INSIGHT:**
Container security architecture does not prevent vulnerabilities in
application code. It constrains what an attacker can do after exploiting
one - reducing blast radius from "entire cluster" to "one container."

---

### 🧠 Mental Model / Analogy

> Container security architecture is a castle with multiple independent
> defences: the moat (network policies - limit what can reach the castle),
> the drawbridge (admission control - block non-compliant workloads), the
> portcullis (runtime controls - limit what processes can do), the vault
> (secrets management - protect crown jewels separately), and the guards
> (runtime threat detection - detect anomalous behaviour).

Element mapping:

- **Moat** = Kubernetes NetworkPolicy
- **Drawbridge** = OPA/Gatekeeper or Kyverno admission webhooks
- **Portcullis** = seccomp, AppArmor, non-root, dropped capabilities
- **Vault** = Vault, AWS Secrets Manager (not env vars)
- **Guards** = Falco, Tetragon runtime threat detection

Where this analogy breaks down: a real castle's defences are sequential;
container security layers can be bypassed independently (a vulnerability
in the drawbridge does not help if the moat stops lateral movement).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Container security architecture is the set of controls that limit what
a container can do and what happens if one is compromised.

**Level 2 - How to use it (junior developer):**
Start with the 5 basics: (1) non-root user in Dockerfile, (2) no
`:latest` tag (use digest pinning), (3) scan images in CI with Trivy,
(4) set resource limits, (5) do not put secrets in env vars - use
Kubernetes Secrets mounted as files or a secrets manager.

**Level 3 - How it works (mid-level engineer):**
Apply controls at each layer: supply chain (image signing with Cosign,
SBOM generation), runtime (securityContext: non-root, readOnlyRootFilesystem,
drop all capabilities, add only required ones), network (NetworkPolicy
default-deny then allow-list), admission (Kyverno ClusterPolicy enforcing
security baseline), secrets (external-secrets-operator or Vault sidecar).

**Level 4 - Why it was designed this way (senior/staff):**
Each control layer exists because a different attack vector exists at
that layer. Image scanning addresses supply chain compromise (SolarWinds
model). Non-root + dropped capabilities address kernel exploit escalation.
Network policies address lateral movement after container escape.
Admission control addresses developer misconfiguration (the most common
real-world failure mode, not sophisticated attacks).

**Expert Thinking Cues:**

- "What is the blast radius if this container is fully compromised?"
- "Which controls would slow or detect an attacker who has shell access?"
- "Are admission policies enforced via webhook (preventing deployment)
  or audit only (logging but not blocking)?"

---

### ⚙️ How It Works (Mechanism)

**SECURITY LAYER MAP:**

```
[Build] Image scanning (Trivy, Grype)
        Image signing (Cosign + Sigstore)
        SBOM generation (Syft)
        |
[Push]  Registry scanning (ECR scanning,
        Harbor, Snyk Container)
        |
[Admit] Kyverno / OPA Gatekeeper policies
        (enforce security baseline)
        |
[Run]   securityContext (non-root, readOnly,
        dropped caps, seccomp, AppArmor)
        |
[Net]   NetworkPolicy (default-deny, allow-list)
        |
[Secrets] Vault / external-secrets-operator
          (no env var secrets)
        |
[Detect] Falco / Tetragon (runtime anomaly)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Developer pushes code
  |
  v
CI: build image + Trivy scan
  | (fail if Critical CVE)
  v
Registry: sign with Cosign
  |
  v
Kubernetes admission webhook
  | checks: non-root, limits, no privileged
  |           ← YOU ARE HERE
  v
Pod starts with securityContext enforced
  |
  v
Runtime: Falco monitors syscalls
  |
  v
Network: NetworkPolicy restricts traffic
```

**FAILURE PATH:**
Image with critical CVE slips through (scan not blocking in CI, only
reporting). Container deployed and exploited. Without runtime detection
(Falco), the attack is invisible until post-breach forensics.

**WHAT CHANGES AT SCALE:**
At scale, image scanning must be continuous (images in the registry age
as new CVEs are disclosed). Admission control must apply to all
namespaces including system ones. Secrets management must support
rotation without pod restarts.

---

### 💻 Code Example

```yaml
# BAD: privileged, root, no limits, host path access
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      privileged: true    # can access host
    volumeMounts:
    - mountPath: /host
      name: host-root     # full host filesystem
  volumes:
  - name: host-root
    hostPath:
      path: /
```

```yaml
# GOOD: hardened securityContext
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp@sha256:abc123  # digest pin
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
    volumeMounts:
    - mountPath: /tmp
      name: tmp-dir        # writable tmp only
  volumes:
  - name: tmp-dir
    emptyDir: {}
```

```yaml
# GOOD: Kyverno policy enforcing non-root cluster-wide
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-runAsNonRoot
    match:
      resources:
        kinds: [Pod]
    validate:
      message: "Containers must not run as root"
      pattern:
        spec:
          containers:
          - securityContext:
              runAsNonRoot: true
```

**How to test / verify correctness:**

```bash
# Scan an image for CVEs
trivy image myapp:v1.4.2

# Verify image signature
cosign verify --key cosign.pub myapp@sha256:abc123

# Check what capabilities a running container has
docker inspect <id> | jq '.[].HostConfig.CapAdd'

# Simulate admission policy in dry-run
kubectl apply --dry-run=server -f pod.yaml
```

---

### ⚖️ Comparison Table

| Layer | Tool Options | Enforcement Point | Blocks or Detects |
|---|---|---|---|
| Image scanning | Trivy, Grype, Snyk | CI / Registry | Blocks |
| Image signing | Cosign + Sigstore | Admission | Blocks |
| Admission policy | Kyverno, OPA/Gatekeeper | Kubernetes API | Blocks |
| Runtime isolation | seccomp, AppArmor, gVisor | Kernel | Blocks |
| Runtime detection | Falco, Tetragon | Kernel (eBPF) | Detects |
| Network control | NetworkPolicy, Cilium | CNI | Blocks |
| Secrets | Vault, external-secrets | App level | Protects |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Containers are isolated by default" | Containers share the host kernel. Without seccomp, AppArmor, and non-root enforcement, a kernel vulnerability can escape the container entirely. |
| "Scanning images in CI is sufficient" | Images age - new CVEs are disclosed after images are scanned and deployed. Continuous registry scanning and runtime CVE detection are required. |
| "Kubernetes Secrets are encrypted at rest by default" | Kubernetes Secrets are base64-encoded in etcd but NOT encrypted by default. Encryption at rest requires explicit EncryptionConfiguration and an external KMS. |
| "Running as non-root prevents all privilege escalation" | `allowPrivilegeEscalation: false` and `capabilities: drop: ALL` are also required. Non-root alone does not prevent a setuid binary from escalating. |
| "Network policies are enforced by default" | NetworkPolicy requires a CNI plugin that enforces them (Calico, Cilium). Default Kubernetes installation with a non-enforcing CNI ignores all NetworkPolicy manifests. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Container Running as Root (Security)**
**Symptom:** Post-breach forensics shows attacker achieved host access
from a compromised container. Container was running as UID 0.
**Root Cause:** No runAsNonRoot enforcement in securityContext or
admission policy. Developers default to root because it avoids permission
errors during development.
**Diagnostic:**

```bash
# Find all pods running as root
kubectl get pods -A -o json | jq '
  .items[] |
  select(
    (.spec.securityContext.runAsUser == 0 or
     .spec.securityContext.runAsNonRoot != true)
  ) | .metadata.name'

# Check effective UID inside a running container
kubectl exec -it <pod> -- id
```

**Fix:** Add `runAsNonRoot: true` and `runAsUser: 1000` to all pod
specs. Enforce via Kyverno ClusterPolicy in Enforce mode.
**Prevention:** Enforce non-root via admission webhook from cluster
creation. Test Dockerfiles with `docker run --user 1000`.

---

**Failure Mode 2: Secrets Exposed in Environment Variables**
**Symptom:** Breach investigation reveals database credentials and API
keys were readable from any process inside any pod via `/proc/*/environ`.
**Root Cause:** Secrets injected as environment variables rather than
mounted files. Env vars are visible to all processes in the container
and logged in crash dumps.
**Diagnostic:**

```bash
# Find pods with secrets as env vars (look for secretKeyRef)
kubectl get pods -A -o yaml | \
  grep -A 3 secretKeyRef | head -40

# Read env vars from inside a running pod
kubectl exec -it <pod> -- env | grep -i secret
```

**Fix:** Mount secrets as files (`volumeMounts` with `secret` volume)
rather than environment variables. Use external-secrets-operator or
Vault agent sidecar for automatic rotation.
**Prevention:** Kyverno policy that denies `secretKeyRef` in env vars
and requires file mounts.

---

**Failure Mode 3: Admission Policies in Audit Mode Only**
**Symptom:** Security review shows policy violations everywhere, but no
workloads have been blocked. All policies are in `audit` mode.
**Root Cause:** Team set policies to audit to avoid disruption but never
graduated them to enforce mode. Audit mode generates logs nobody reads.
**Diagnostic:**

```bash
# Check Kyverno policy enforcement actions
kubectl get clusterpolicies -o json | jq '
  .items[] |
  {name: .metadata.name,
   action: .spec.validationFailureAction}'

# Check OPA constraint enforcement actions
kubectl get constraints -A -o json | \
  jq '.items[] | {name:.metadata.name,
  action:.spec.enforcementAction}'
```

**Fix:** Graduate audit policies to enforce mode in non-production
namespaces first. Fix violations. Then promote to production.
**Prevention:** Start with enforce mode in new namespaces. Treat audit
mode as a transition state, not a permanent configuration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-017 - Linux Namespaces]] - kernel isolation primitives containers rely on
- [[CTR-018 - Cgroups]] - resource isolation for containers
- [[CTR-021 - Container Security]] - foundational container security concepts
- [[CTR-023 - Image Scanning]] - vulnerability scanning in the supply chain

**Builds On This (learn these next):**

- [[CTR-051 - Container Security Research (Rootless, gVisor)]] - advanced isolation
- [[CTR-054 - Container Security Mental Model]] - threat model thinking

**Alternatives / Comparisons:**

- [[CTR-022 - Distroless Images]] - reducing image attack surface at the build layer
- [[CTR-040 - Docker Secrets]] - secrets management approach in Compose environments

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Defense-in-depth for containers     │
│ PROBLEM     │ Single control cannot stop all attacks│
│ KEY INSIGHT │ Limit blast radius, not just entry  │
│ USE WHEN    │ Always - baseline for all containers │
│ AVOID WHEN  │ N/A - all layers should be present  │
│ TRADE-OFF   │ Security controls vs. ops overhead  │
│ ONE-LINER   │ Secure image, runtime, net, secrets │
│ NEXT EXPLORE│ CTR-051 Rootless, CTR-054 Threat    │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Containers share the host kernel - runtime controls (seccomp, non-root,
   dropped capabilities) are essential, not optional hardening.
2. Images age - scan continuously in the registry, not just at build time.
3. Admission control in audit mode is not security - graduate to enforce
   mode or it provides no protection.

**Interview one-liner:**
"Container security architecture applies defense-in-depth across five
layers - supply chain, runtime, network, secrets, and admission control -
because a container share the host kernel and a single misconfiguration
in any layer can expose the entire host."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Defense-in-depth means each layer must provide independent protection.
A layer that only works when all other layers are intact is not adding
security - it is adding complexity. Design each security control to
contain a breach that has already bypassed the previous layer.

**Where else this pattern appears:**

- **Web application security:** Input validation (supply chain), WAF
  (admission), RBAC (runtime), secrets management, and logging/alerting
  (detection) mirror the container security layers exactly.
- **Cloud account security:** SCPs (admission), IAM least privilege
  (runtime), VPC security groups (network), Secrets Manager (secrets),
  and CloudTrail (detection) follow the same independent-layers model.
- **Physical security:** Badge access (admission), locked server racks
  (runtime), CCTV (detection), and split-knowledge safe combinations
  (secrets) all apply independent controls that limit blast radius.

---

### 💡 The Surprising Truth

The most common real-world container security failure is not a
sophisticated supply chain attack or a kernel exploit - it is a developer
misconfiguration: a container running as root with `privileged: true`
because the developer could not get the application to work without it
and nobody enforced a policy preventing it. The CNCF Security Audit of
2021 found that the majority of security incidents in Kubernetes
environments were caused by misconfiguration, not vulnerability
exploitation. Admission control that blocks misconfigured workloads
prevents more real-world incidents than any vulnerability scanner.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** Kubernetes Secrets are base64-encoded in
etcd. Why is base64 not encryption? What three mechanisms together
provide actual secrets security in a Kubernetes cluster?
*Hint:* Consider etcd encryption at rest (EncryptionConfiguration + KMS),
Kubernetes RBAC on the Secret resource, and secrets injection method
(env var vs. mounted file). What does each mechanism protect against?

**Q2 (D - Root Cause):** A Falco alert fires: "A shell was spawned in a
container running nginx." This is almost certainly a breach indicator.
What are the 3 most likely attack vectors that would lead to a shell
spawning inside an nginx container?
*Hint:* Consider: remote code execution via nginx vulnerability, command
injection via application code, and developer `kubectl exec` during an
incident. How does Falco distinguish them?

**Q3 (C - Design Trade-off):** An admission webhook (Kyverno) is set to
Enforce mode and blocks any pod without `readOnlyRootFilesystem: true`.
A legacy application writes temporary files to its container filesystem
at startup and fails. How do you satisfy the security control without
modifying the legacy application?
*Hint:* Consider emptyDir volumes mounted at the specific paths the
application writes to. What is the security difference between
readOnlyRootFilesystem with emptyDir mounts vs. a writable root filesystem?
'@

# ── CTR-045 ──────────────────────────────────────────────────────────────
$ctr045 = @'
---
id: CTR-045
title: Container Image Strategy at Scale
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-010, CTR-011, CTR-016, CTR-033
used_by: CTR-043, CTR-046
related: CTR-022, CTR-034
tags:
  - containers
  - docker
  - architecture
  - advanced
  - bestpractice
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /ctr/container-image-strategy-at-scale/
---

# CTR-045 - Container Image Strategy at Scale

⚡ TL;DR - Container image strategy at scale governs base image selection, layer caching, tagging conventions, registry topology, and vulnerability lifecycle to maintain security and build speed across hundreds of images.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | CTR-010, CTR-011, CTR-016, CTR-033 |     |
| **Used by:**    | CTR-043, CTR-046                   |     |
| **Related:**    | CTR-022, CTR-034                   |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A 50-service organisation has 50 different base images: Ubuntu 20.04,
Ubuntu 22.04, Alpine 3.14, Debian Bullseye, scratch, and various
language-specific images in different versions. Each team manages its
own base image. A critical CVE in libssl affects 40 of the images, but
identifying and patching them takes 3 weeks because there is no
centralised tracking.

**THE BREAKING POINT:**
CI builds take 20 minutes because every build re-downloads dependencies
that were downloaded in the previous build. Registry storage costs
exceed $5,000/month for 10,000 image versions. A security audit finds
images in production that are 18 months old and contain 200+ known CVEs.
The "container strategy" never included image lifecycle management.

**THE INVENTION MOMENT:**
Image strategy at scale applies three disciplines: governance (approved
base images, tagging conventions), supply chain (scanning, signing, SBOM),
and lifecycle management (promotion pipeline, deprecation, storage
limits). Without these, each team reinvents image management badly.

**EVOLUTION:**
2014: Docker Hub becomes the default registry. 2015: Private registries
(Nexus, Artifactory) gain traction. 2017: ECR and GCR become standard
for cloud deployments. 2019: Cosign and image signing enter production.
2020: SBOMs become a compliance requirement (NIST, EO 14028).
2022: OCI Artifacts extend registries to store Helm charts, Wasm modules,
and SBOMs alongside images. Registries are now artifact stores, not just
image stores.

---

### 📘 Textbook Definition

**Container image strategy at scale** is the set of policies and
tooling governing how container images are built (base image selection,
layer structure, multi-stage builds), stored (registry topology, tag
retention), secured (scanning, signing, SBOM), and retired (deprecation,
purging old versions) across a large number of services and teams.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Govern base images, tag conventions, scanning, and lifecycle so 100
teams can manage images without creating a security and storage disaster.

**One analogy:**

> Container image strategy is like a corporate travel policy. Without
> it, everyone books flights on different airlines, using personal credit
> cards, with no expense tracking. With it, there are preferred airlines
> (approved base images), booking tools (approved registries), expense
> reporting (SBOM), and trip approval (admission scanning).

**One insight:**
The biggest image strategy failure is not a technical problem - it is a
governance problem. Teams make locally rational decisions (use the base
image that works) that collectively create an unmanageable security and
operational posture.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Every layer in every image is a potential vulnerability surface** -
   minimising layers and base image size directly reduces attack surface.
2. **Images age** - a clean image at build time accumulates CVEs as new
   vulnerabilities are disclosed against its packages. Scanning must be
   continuous, not one-time.
3. **Layer caching is the primary build performance lever** - ordering
   Dockerfile instructions to maximise cache hit rate reduces CI time
   from minutes to seconds.
4. **Tag mutability is a reliability risk** - `myapp:latest` can refer
   to different images at different times; digest pinning (`sha256:...`)
   is the only guarantee of reproducibility.

**DERIVED DESIGN:**
Given invariant 1: standardise on minimal base images (distroless,
Alpine, or scratch) for production. Use larger images (Ubuntu) only in
CI/dev where tooling is needed. Given invariant 3: put frequently
changing layers (application code) at the bottom of the Dockerfile,
infrequently changing layers (base OS, runtime) at the top.

**THE TRADE-OFFS:**
**Gain:** Standard base images reduce the CVE remediation scope from
N (one per service) to M (one per approved base image). Layer caching
reduces CI time. Tag conventions enable automated vulnerability tracking.
**Cost:** Base image standardisation requires teams to accept constraints.
Registry governance requires tooling and enforcement.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any multi-team image strategy needs base image governance,
scanning, and lifecycle management.
**Accidental:** Multiple competing internal registries, custom tagging
formats per team, manual vulnerability remediation tracking.

---

### 🧪 Thought Experiment

**SETUP:**
An organisation has 80 microservices. Each service has its own
Dockerfile. No base image standard exists. Images are tagged with
`:latest` only.

**WHAT HAPPENS WITHOUT IMAGE STRATEGY:**
A critical CVE is found in OpenSSL. The security team must audit 80
Dockerfiles to determine which use a vulnerable base image. 40 services
are affected. Each team must independently patch, rebuild, test, and
deploy. The process takes 3 weeks. During that time, 40 services are
vulnerable. After patching, the security team discovers 15 images were
rebuilt against the fixed base but not redeployed - production still
runs the vulnerable version.

**WHAT HAPPENS WITH IMAGE STRATEGY:**
The organisation has 3 approved base images (Java 21 distroless, Node 20
Alpine, Python 3.12 slim), each maintained centrally. When the CVE is
disclosed, the platform team updates the 3 base images. A CI trigger
automatically rebuilds all 40 affected services within 2 hours. Cosign
signatures on the new images allow the admission webhook to verify that
production containers use patched images within 4 hours.

**THE INSIGHT:**
Image strategy at scale is primarily a CVE remediation time reduction
strategy. The investment in base image standardisation pays its largest
dividend during security incidents.

---

### 🧠 Mental Model / Analogy

> Container images are like franchise restaurant recipes. Without central
> governance, each franchise invents its own recipe (base image). When
> a food safety issue (CVE) hits one ingredient (OpenSSL), identifying
> and patching all affected franchises is a crisis. With central recipe
> governance, the head office updates the master recipe (base image),
> and all franchises automatically use the updated version on next
> production run.

Element mapping:

- **Franchise** = individual microservice team
- **Recipe** = Dockerfile / base image
- **Ingredient** = OS package (OpenSSL, curl, libssl)
- **Head office recipe update** = platform team base image update
- **Production run** = CI rebuild triggered by base image change
- **Food safety certificate** = Cosign image signature

Where this analogy breaks down: in software, "production run" can be
triggered automatically (CI webhook on base image publish); in
restaurants, re-cooking requires physical presence.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Container image strategy is the set of rules that governs which base
images teams use, how images are named and versioned, and how old or
vulnerable images are retired.

**Level 2 - How to use it (junior developer):**
(1) Use the approved base image for your language runtime. (2) Pin to
a specific version tag, not `:latest`. (3) Use multi-stage builds to
keep production images small. (4) Never add secrets to images. (5) Run
`trivy image` before pushing.

**Level 3 - How it works (mid-level engineer):**
Image strategy has four components: build (layer ordering for cache
efficiency, multi-stage builds, distroless production layers), store
(registry topology: dev registry, staging registry, production registry
with promotion gates), secure (scanning at every stage, Cosign signing,
SBOM attachment), and lifecycle (semver tagging, retention policies,
automated deprecation of images older than 90 days with CVEs).

**Level 4 - Why it was designed this way (senior/staff):**
Image strategy exists because the collective effect of individually
rational team decisions creates an operationally unmanageable system.
Each team optimises locally (use the base image that works now), but
the aggregate result is 50 different base images, no cross-team CVE
tracking, and no automated remediation path. Central governance creates
the enabling constraint that makes scale manageable.

**Expert Thinking Cues:**

- "How many distinct base images do we have in production? What is the
  CVE remediation effort if one of them has a critical CVE?"
- "What is our image promotion pipeline? How does an image move from
  dev registry to production registry with security gates?"
- "What is our tag retention policy? How much registry storage do we
  accumulate monthly?"

---

### ⚙️ How It Works (Mechanism)

**IMAGE PROMOTION PIPELINE:**

```
Developer pushes code
  |
  v
CI: docker build (multi-stage)
  + Trivy scan (fail on Critical)
  + Syft SBOM generation
  + Cosign sign with dev key
  |
  v
Dev Registry (myregistry/dev/)
  |  [QA tests pass]
  v
Staging Registry (myregistry/staging/)
  | [Integration + security gate]
  v
Production Registry (myregistry/prod/)
  + Cosign sign with prod key
  + Immutable tag (semver + git SHA)
```

**LAYER CACHE OPTIMISATION ORDER:**

```
FROM base-image (changes rarely)
RUN install OS deps (changes rarely)
COPY requirements.txt (changes rarely)
RUN install app deps (changes on dep update)
COPY src/ (changes on every commit)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Base image CVE disclosed
  |
  v
Platform team patches base image
  |         ← YOU ARE HERE
  v
Automated rebuild trigger (CI webhook)
  |
  v
All dependent services rebuilt + scanned
  |
  v
Images promoted through dev/staging/prod
  |
  v
Admission webhook verifies Cosign signature
  |
  v
Old vulnerable images purged by retention
     policy after 7-day overlap
```

**FAILURE PATH:**
Base image updated but no automated rebuild trigger exists. Services
continue running on the old base image. The CVE remediation depends on
individual teams noticing and rebuilding, which takes weeks.

**WHAT CHANGES AT SCALE:**
At 100+ services, manual image management is impossible. Automated
triggers (on base image publish, rebuild dependent images), admission
policies (reject images older than 30 days with known Critical CVEs),
and storage policies (retain last 10 versions only) become mandatory.

---

### 💻 Code Example

```dockerfile
# BAD: single stage, large image, root user,
# no pinned version
FROM ubuntu:latest
RUN apt-get install -y curl wget build-essential \
    nodejs npm
COPY . /app
RUN npm install
CMD ["node", "/app/server.js"]
```

```dockerfile
# GOOD: multi-stage, minimal production image,
# non-root, pinned digest
FROM node:20-alpine3.19@sha256:abc123 AS builder
WORKDIR /build
COPY package*.json ./
RUN npm ci --only=production

FROM gcr.io/distroless/nodejs20-debian12 AS runtime
WORKDIR /app
COPY --from=builder /build/node_modules ./node_modules
COPY src/ ./src/
USER nonroot
EXPOSE 3000
CMD ["src/server.js"]
```

```yaml
# GitHub Actions: scan + sign pipeline
- name: Build image
  run: docker build -t $IMAGE_REF .

- name: Scan with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE_REF }}
    severity: 'CRITICAL'
    exit-code: '1'          # fail on Critical CVE

- name: Generate SBOM
  run: syft $IMAGE_REF -o spdx-json > sbom.json

- name: Sign image
  run: |
    cosign sign --key $COSIGN_KEY $IMAGE_REF
    cosign attach sbom --sbom sbom.json $IMAGE_REF
```

**How to test / verify correctness:**

```bash
# Check image size and layers
docker image history myapp:v1.4.2

# Verify Cosign signature
cosign verify --key cosign.pub myapp:v1.4.2

# Check SBOM attached to image
cosign verify-attestation --key cosign.pub \
  --type spdxjson myapp:v1.4.2
```

---

### ⚖️ Comparison Table

| Registry Option | Best For | Scanning | Signing | Storage Limits |
|---|---|---|---|---|
| Docker Hub | Public images, OSS | Basic | No | Limited free |
| Amazon ECR | AWS workloads | Built-in (ECR scan) | Cosign compatible | Lifecycle policies |
| Google Artifact Registry | GCP workloads | Vulnerability scan | Cosign compatible | Yes |
| Harbor | On-prem / air-gapped | Trivy built-in | Cosign + Notary | Configurable |
| GitHub Container Registry | GitHub Actions workflows | Via Actions | Cosign compatible | Package limits |

---

### 🔁 Flow / Lifecycle

**IMAGE LIFECYCLE PHASES:**

**Phase 1 - Build:** Multi-stage Dockerfile executes in CI. Dependencies
installed, application compiled, production layer assembled. Trivy scan
and SBOM generation occur. Image signed with dev key and pushed to
dev registry.

**Phase 2 - Test & Promote:** QA and integration tests run against the
dev registry image. On pass, image is promoted (re-tagged + re-signed)
to staging registry. Security gate verifies no unresolved Critical CVEs.

**Phase 3 - Production Release:** Image promoted to production registry
with immutable semver+SHA tag. Cosign signed with production key.
Admission webhook verifies production signature before allowing pod
scheduling.

**Phase 4 - Deprecation:** After 90 days or when a newer version is
deployed, image is marked deprecated. Retention policy purges after a
30-day overlap window. Registry storage cost is reclaimed. Security
scanning of deprecated images stops.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Pinning to a tag like `node:20-alpine` is safe" | Tags are mutable - `node:20-alpine` can point to a different image after a push. Only digest pinning (`@sha256:...`) guarantees reproducibility. |
| "Scanning images at build time is sufficient" | Images age - new CVEs are disclosed after deployment. Production registries must be continuously scanned. |
| "Multi-stage builds are only about image size" | Multi-stage builds also improve security (build tools not in production image) and cache efficiency (dependency installation cached separately from source copy). |
| "A small image is always more secure" | A small image with outdated packages is less secure than a larger image with current packages. Size reduction via distroless must accompany current package versions. |
| "Registry retention policies delete important images" | Retention policies should be configured to always retain production-tagged images regardless of age. Age-based retention applies to untagged or non-production images only. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Mutable Tags in Production**
**Symptom:** Two identical-looking deployments behave differently. The
`:latest` tag refers to different images in dev and production.
**Root Cause:** Mutable tags used in Kubernetes manifests. A push to the
registry changes what the tag resolves to without updating the manifest.
**Diagnostic:**

```bash
# Check what image SHA is actually running
kubectl get pods -o json | jq '
  .items[].status.containerStatuses[].imageID'

# Compare to what the manifest declares
kubectl get deployment myapp -o json | \
  jq '.spec.template.spec.containers[].image'

# If they differ, the tag was mutated after deployment
```

**Fix:** Use `imagePullPolicy: IfNotPresent` with digest-pinned images.
Set `imagePullPolicy: Never` for immutable images in air-gapped envs.
**Prevention:** CI pipeline outputs the image digest; manifests reference
the digest, never the mutable tag.

---

**Failure Mode 2: Registry Storage Runaway**
**Symptom:** Registry storage costs increase 20% per month. No one knows
what images are in the registry or whether they are still needed.
**Root Cause:** No retention policy. Every build pushes a new image tag
that is never cleaned up.
**Diagnostic:**

```bash
# ECR: list images sorted by push date
aws ecr describe-images \
  --repository-name myapp \
  --query 'sort_by(imageDetails, &imagePushedAt)' \
  --output table | head -20

# Count untagged images (usually safe to delete)
aws ecr list-images \
  --repository-name myapp \
  --filter tagStatus=UNTAGGED | jq '.imageIds | length'
```

**Fix:** Implement lifecycle policies: keep last 10 tagged images, delete
untagged images after 7 days, delete images older than 90 days that
are not referenced in any active Kubernetes deployment.
**Prevention:** Configure registry lifecycle policies at repository
creation time.

---

**Failure Mode 3: CVE in Widely-Used Base Image (Security)**
**Symptom:** Security scanner reports Critical CVE across 40 production
services. No automated rebuild mechanism exists.
**Root Cause:** No base image standardisation, no automated rebuild
trigger on base image update.
**Diagnostic:**

```bash
# Identify all images using a specific base image
# (requires SBOM or image inspect)
docker inspect myapp:v1.4.2 | \
  jq '.[].RootFS.Layers'

# Scan all running images for a specific CVE
trivy image --severity CRITICAL \
  --vuln-type os myapp:v1.4.2 | grep CVE-2024-XXXX
```

**Fix:** Standardise on approved base images. Create CI webhook that
triggers rebuild of all dependent images when a base image is updated.
**Prevention:** Implement base image registry with automatic rebuild
propagation (Docker Hub webhooks, ECR event triggers to CodePipeline).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-010 - Docker Image]] - image fundamentals
- [[CTR-011 - Docker Layer]] - layer model and caching
- [[CTR-016 - Container Registry]] - registry concepts
- [[CTR-033 - Image Tag Strategy]] - tagging foundations

**Builds On This (learn these next):**

- [[CTR-043 - Container Platform Strategy]] - platform context for image strategy
- [[CTR-046 - Containerization Migration Strategy]] - image strategy during migration

**Alternatives / Comparisons:**

- [[CTR-022 - Distroless Images]] - minimal base image approach
- [[CTR-034 - Docker BuildKit]] - build performance and layer caching

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Governance for images at scale      │
│ PROBLEM     │ CVE sprawl + storage runaway        │
│ KEY INSIGHT │ Standard base images = N-to-1 CVE  │
│ USE WHEN    │ Managing images across 5+ services  │
│ AVOID WHEN  │ N/A - always needed at any scale   │
│ TRADE-OFF   │ Base image constraints vs. CVE ops  │
│ ONE-LINER   │ Govern base, tag, scan, and retire │
│ NEXT EXPLORE│ CTR-043 Platform, CTR-022 Distroless│
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Tags are mutable - use digest pinning in production for reproducibility.
2. Images age - scan continuously in the registry, not just at build time.
3. Standardise on N approved base images so CVE remediation is N rebuilds,
   not one per service.

**Interview one-liner:**
"Container image strategy at scale solves the CVE remediation problem:
by standardising on approved base images and automating rebuild triggers,
a critical CVE in a base image can be patched across all services in
hours rather than weeks."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Shared dependencies create shared risk. When 40 services share a base
image, they share its vulnerabilities. The right response is not to
eliminate the shared dependency (each team writes their own OS layer -
absurd) but to govern it centrally so the shared risk can be mitigated
centrally. Central governance of shared dependencies is the only
scalable remediation strategy.

**Where else this pattern appears:**

- **NPM/Maven dependency management:** A centralised Artifactory or
  Nexus instance acts as an approved mirror. Teams pull from the mirror,
  which enables security scanning, licence compliance checking, and
  caching at one point rather than 50.
- **Golden AMI strategy:** Cloud teams maintain approved base AMIs with
  OS patches, security agents, and monitoring pre-installed. Autoscaling
  groups always launch from the current golden AMI. A patch to the golden
  AMI propagates to all services on next scale-out.
- **OS package management in enterprises:** Organisations run internal
  YUM/APT mirrors with approved package versions. Security teams can
  block vulnerable package versions at the mirror level without touching
  individual servers.

---

### 💡 The Surprising Truth

Layer caching in Docker has an unexpected property: a cache miss at
any layer invalidates all layers below it. This means a single poorly
ordered Dockerfile instruction can eliminate the entire build cache on
every CI run. The most common mistake is `COPY . .` before `RUN npm
install` - a change to any source file invalidates the `npm install`
cache, causing full dependency download on every build. Correct order
is `COPY package.json; RUN npm install; COPY src/` so that dependency
installation is cached until `package.json` changes. Build performance
is often improved by 80% by reordering three lines.

---

### 🧠 Think About This Before We Continue

**Q1 (B - Scale):** An organisation has 100 microservices all built
FROM `node:20-alpine`. A critical CVE is found in Alpine's `busybox`.
If the platform team updates the base image and CI is fully automated,
what are the remaining gaps that could leave some services vulnerable
even after the rebuild completes?
*Hint:* Consider: services that don't rebuild automatically (no webhook),
services that rebuild but whose deployment manifests are not updated,
Kubernetes pods that don't restart (if `imagePullPolicy: IfNotPresent`
and the node already has the old image cached).

**Q2 (C - Design Trade-off):** A security team proposes that all
production images must be signed with Cosign and the admission webhook
must reject unsigned images. A developer argues this will block
emergency hotfixes (no time to complete the signing pipeline). How do
you satisfy both requirements?
*Hint:* Consider a "break-glass" signing key held by on-call engineers,
time-limited emergency signing certificates, and an audit log of any
image deployed without the standard pipeline.

**Q3 (A - System Interaction):** A registry retention policy deletes
image tags older than 90 days. A Kubernetes Deployment is pinned to
`myapp@sha256:abc123`, and that digest is 4 months old (the service has
not been redeployed). The retention policy deletes the image. What
happens to the running pod? What happens on the next pod restart?
*Hint:* A running pod uses the image already on the node's local cache.
Kubernetes does not need to pull an image that is already present. But
what happens when a node is replaced, or the pod is rescheduled to a
new node?
'@

# ── CTR-046 ──────────────────────────────────────────────────────────────
$ctr046 = @'
---
id: CTR-046
title: Containerization Migration Strategy
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-001, CTR-043, CTR-045
used_by:
related: CTR-052, CTR-053
tags:
  - containers
  - architecture
  - advanced
  - bestpractice
  - devops
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /ctr/containerization-migration-strategy/
---

# CTR-046 - Containerization Migration Strategy

⚡ TL;DR - Containerization migration strategy is the structured plan for moving workloads from VMs or bare metal to containers: assess, choose a migration pattern, migrate in phases, and validate operational readiness at each gate.

| Metadata        |                          |     |
| :-------------- | :----------------------- | :-- |
| **Depends on:** | CTR-001, CTR-043, CTR-045 |     |
| **Used by:**    |                          |     |
| **Related:**    | CTR-052, CTR-053         |     |

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
- [[CTR-043 - Container Platform Strategy]] - choose the platform before migrating
- [[CTR-045 - Container Image Strategy at Scale]] - image strategy for migrated services

**Builds On This (learn these next):**

- [[CTR-052 - Container Trade-off Framing]] - evaluate the trade-offs of containerising
- [[CTR-053 - Containerization Necessity Assessment]] - assess whether to containerise at all

**Alternatives / Comparisons:**

- [[CTR-052 - Container Trade-off Framing]] - when not to containerise
- [[CTR-053 - Containerization Necessity Assessment]] - is containerisation the right move?

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
│ NEXT EXPLORE│ CTR-052 Trade-offs, CTR-053 Assess  │
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
'@

# ── Write files ───────────────────────────────────────────────────────────
$files = @{
    "CTR-043 - Container Platform Strategy.md" = $ctr043
    "CTR-044 - Container Security Architecture.md" = $ctr044
    "CTR-045 - Container Image Strategy at Scale.md" = $ctr045
    "CTR-046 - Containerization Migration Strategy.md" = $ctr046
}

foreach ($name in $files.Keys) {
    $path = Join-Path $base $name
    [System.IO.File]::WriteAllText(
        $path, $files[$name],
        [System.Text.UTF8Encoding]::new($false))
    $lines = (Get-Content $path -Encoding UTF8).Count
    Write-Host "Written: $name ($lines lines)"
}

# Verify encoding (first 3 bytes must NOT be 239,187,191)
foreach ($name in $files.Keys) {
    $path = Join-Path $base $name
    $bytes = [IO.File]::ReadAllBytes($path)
    $bom = "$($bytes[0]),$($bytes[1]),$($bytes[2])"
    Write-Host "BOM check $name : $bom (must NOT be 239,187,191)"
}
