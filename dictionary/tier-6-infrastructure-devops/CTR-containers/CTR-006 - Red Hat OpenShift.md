---
id: CTR-006
title: "Red Hat OpenShift"
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-008, CTR-009
used_by: CTR-007
related: CTR-007, CTR-026
tags:
  - kubernetes
  - containers
  - advanced
  - production
status: complete
version: 1
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /containers/red-hat-openshift/
---

# CTR-006 - Red Hat OpenShift

⚡ **TL;DR -** Red Hat OpenShift is an enterprise Kubernetes platform that layers developer tooling, security hardening, built-in CI/CD, and a commercial support model on top of upstream Kubernetes.

| | |
|---|---|
| **Depends on** | Kubernetes, Docker, Containers |
| **Used by** | Containers |
| **Related** | OpenShift vs Kubernetes, Kubernetes, OKD |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Running Kubernetes in a regulated enterprise - financial services, healthcare, government - requires assembling a production-grade platform from scratch: container registry, image scanning, RBAC hardening, CI/CD pipelines, monitoring, service mesh, network policies, and a vendor support contract. This takes specialised platform engineering teams months, and the result is unique to each organisation.

**THE BREAKING POINT:** A financial services company running 400 microservices needs to pass a security audit. Raw Kubernetes lets containers run as root by default. There is no built-in image registry, no integrated build pipeline, and no break-glass procedure for CVE patches. Every component must be sourced, integrated, and maintained separately.

**THE INVENTION MOMENT:** Red Hat packaged Kubernetes with opinionated defaults - security-first, developer-friendly, enterprise-supported - and called it OpenShift. The value proposition: organisations get a fully integrated, commercially-supported Kubernetes distribution rather than assembling one from open-source components.

**EVOLUTION:** OpenShift 3.x (2015-2018) used Docker and custom networking (SDN). OpenShift 4.x (2019+) was a full rewrite: RHCOS immutable nodes, CRI-O runtime replacing Docker, OVN-Kubernetes networking, and the Operator framework managing every cluster component. OCP 4.12+ enforces `restricted-v2` SCCs by default (PSA-aligned). OCP 4.14 deprecated `DeploymentConfig` in favour of standard Kubernetes `Deployment`. The 2023+ focus is on multi-cluster management (ACM), GitOps (ArgoCD-based OpenShift GitOps), and FIPS-compliant builds for government certification.

---

### 📘 Textbook Definition

**Red Hat OpenShift Container Platform (OCP)** is a commercially-supported enterprise Kubernetes distribution built by Red Hat. It extends upstream Kubernetes with additional abstractions (`Route`, `DeploymentConfig`, `BuildConfig`, `ImageStream`, `Project`), enforces stricter security defaults via Security Context Constraints (SCCs), and includes an integrated developer console, image registry (Quay), CI/CD pipeline framework (Tekton), service mesh (Istio/Ossm), and an Operator ecosystem (OperatorHub).

---

### ⏱️ Understand It in 30 Seconds

**One line:** OpenShift is Kubernetes with enterprise batteries included - security, pipelines, a registry, and a support contract.

> OpenShift is to Kubernetes what Red Hat Enterprise Linux is to the Linux kernel - the same open-source core, hardened, integrated, and supported for production enterprise use.

**One insight:** OpenShift doesn't replace Kubernetes - it is Kubernetes. Every `kubectl` command works. The additions are *on top of*, not *instead of*, the Kubernetes API.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. OpenShift is a certified Kubernetes distribution - all Kubernetes APIs are present
2. Security defaults are stricter than upstream: no root containers by default
3. Developer abstractions (`Route`, `BuildConfig`) layer above Kubernetes primitives
4. The Operator framework is the extension mechanism - everything is managed by Operators

**DERIVED DESIGN:** OpenShift wraps the Kubernetes control plane with CRDs and Operators that manage the additional components. The cluster itself is self-managing: the Cluster Version Operator (CVO) manages upgrades; the Machine Config Operator manages node configuration.

**THE TRADE-OFFS:**
**Gain:** Integrated platform; strict security posture out of the box; Red Hat enterprise support; certified for regulated workloads.
**Cost:** Licensing cost (OCP is commercial); more opinionated (some upstream community patterns don't directly apply); SCCs require app changes if apps assume root.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Enterprise Kubernetes needs security defaults, lifecycle management, and integrated tooling - this complexity is inherent in regulated production environments.
**Accidental:** The `oc` CLI, OpenShift-specific CRDs (`Route`, `BuildConfig`), and HAProxy router are implementation choices, not fundamental requirements for enterprise Kubernetes.

---

### 🧪 Thought Experiment

**SETUP:** A team migrates a containerised Spring Boot app from raw Kubernetes to OpenShift.

**WHAT HAPPENS WITHOUT OPENSHIFT KNOWLEDGE:** The Docker image is built with `USER root` for convenience. On OpenShift, the pod fails to start: `Error: container has runAsNonRoot and image will run as root`. The team must rebuild the image with a non-root user. Then they try to create an `Ingress` - the resource is present, but routes use `Route` objects in OpenShift, with automatic TLS termination. Three hours of documentation archaeology.

**WHAT HAPPENS WITH OPENSHIFT KNOWLEDGE:** The team builds the image with `USER 1001`, uses an `oc new-app` template that generates a `BuildConfig`, `DeploymentConfig`, `Service`, and `Route` in one command. TLS is automatic via the cluster's edge-termination default.

**THE INSIGHT:** OpenShift's additional primitives (`Route`, `BuildConfig`) aren't complexity for complexity's sake - they encode decades of enterprise deployment patterns into default workflows that plain Kubernetes leaves to the operator to assemble.

---

### 🧠 Mental Model / Analogy

> Kubernetes is a car engine and chassis. OpenShift is a fully assembled, safety-rated car from a manufacturer with a warranty. You can tune the engine, but it ships with airbags, lane assist, and a service centre network by default.

- **Kubernetes API** → engine and chassis
- **SCCs** → factory-fitted safety cage
- **Routes** → sat-nav integrated at factory (vs aftermarket `Ingress`)
- **OperatorHub** → dealership-installed approved accessories
- **Red Hat support** → 24/7 roadside assistance contract

Where this analogy breaks down: Unlike a car, OpenShift still exposes the engine directly. You can apply raw Kubernetes manifests (`kubectl apply`) without any OpenShift abstraction.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
OpenShift is a platform that runs your containerised applications in a cluster. It's like Kubernetes but with extra safety features and tools already included, plus professional support from Red Hat.

**Level 2 - How to use it (junior developer):**
Use `oc` (the OpenShift CLI, a superset of `kubectl`) to deploy apps. Use `oc new-app` to create a deployment from source code or an image. A `Route` exposes your service to the internet with automatic TLS. Projects (OpenShift's wrapper around `Namespace`) provide multi-tenancy. Use the web console at port 6443 for a visual view of your workloads.

**Level 3 - How it works (mid-level engineer):**
OpenShift adds four key primitives: (1) **Project** - a Namespace plus RBAC defaults and resource quotas. (2) **Route** - an Ingress plus TLS termination, edge/passthrough/re-encrypt modes. (3) **BuildConfig** - a native build pipeline (source-to-image, Docker, or custom strategy) that outputs to an ImageStream. (4) **DeploymentConfig** - a Deployment with additional triggers (image change, config change). SCCs replace PodSecurityAdmission; the `restricted-v2` SCC prevents root and privilege escalation by default.

**Level 4 - Why it was designed this way (senior/staff):**
OpenShift's architecture reflects a key insight: enterprise operators don't just need orchestration - they need *lifecycle management*. The Cluster Version Operator (CVO) represents OpenShift itself as a set of Operators, making the platform self-describing and self-updating. Every OpenShift component (authentication, network, storage, monitoring) is an Operator managing CRDs. This means the control plane upgrade path is the same mechanism as application Operator upgrades - `oc adm upgrade`. SCCs are more granular than Kubernetes PodSecurityAdmission because enterprises need workload-specific profiles (a database legitimately needs elevated privileges; an API server doesn't). The SCC admission webhook grants the *least-privileged SCC that the pod qualifies for*, not a user-chosen one - enforcing least privilege by default.

---

### ⚙️ How It Works (Mechanism)

OpenShift cluster architecture:

```
 ┌─────────────────────────────────────┐
 │         OpenShift Control Plane     │
 │  ┌──────────────┐ ┌──────────────┐  │
 │  │ Kube API     │ │ OpenShift    │  │
 │  │ Server       │ │ API Server   │  │
 │  └──────────────┘ └──────────────┘  │
 │  ┌──────────────────────────────┐   │
 │  │  Cluster Version Operator    │   │
 │  │  (manages platform upgrades) │   │
 │  └──────────────────────────────┘   │
 └─────────────────────────────────────┘
         │
 ┌───────┴──────────────────────────────┐
 │  Worker Nodes (RHCOS)                │
 │  ┌──────────┐ ┌───────┐ ┌────────┐  │
 │  │ CRI-O    │ │ OVN-K │ │ kubelet│  │
 │  └──────────┘ └───────┘ └────────┘  │
 └──────────────────────────────────────┘
```

Request flow: `Route` → `HAProxy Router` → `Service` → `Pod`

SCC admission flow:
```
 Pod submitted
      │
      ▼
 SCC Admission Webhook
      │
      ▼
 Find SCCs user/SA is allowed
      │
      ▼
 Pick least-privileged qualifying SCC
      │
      ▼
 Pod admitted or rejected
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
 Developer pushes code to Git
         │
         ▼
 BuildConfig webhook triggered
         │               ← YOU ARE HERE
         ▼
 Source-to-Image (S2I) build runs
 in cluster (no local Docker needed)
         │
         ▼
 New image pushed to ImageStream
         │
         ▼
 DeploymentConfig image-change
 trigger fires → rolling deploy
         │
         ▼
 Route serves new version with
 edge TLS termination
```

**FAILURE PATH:**
- Pod fails SCC check → `Error creating: pods is forbidden: unable to validate against any security context constraint`
- ImageStream tag not found → `DeploymentConfig` stuck in `Pending`
- Route TLS cert expired → 503 from HAProxy router

**WHAT CHANGES AT SCALE:**
Large clusters (500+ nodes) use the OpenShift Machine API for node autoscaling. Multi-cluster management uses Red Hat Advanced Cluster Management (ACM). GitOps delivery at scale uses OpenShift GitOps (ArgoCD). Observability uses the built-in cluster monitoring stack (Prometheus + Grafana + Alertmanager, managed by the Cluster Monitoring Operator).

---

### 💻 Code Example

**BAD - Dockerfile running as root (fails OpenShift SCC):**
```dockerfile
FROM openjdk:17-jdk-slim
# No USER directive: runs as root (uid 0)
# OpenShift restricted SCC will reject this
COPY target/app.jar /app/app.jar
ENTRYPOINT ["java","-jar","/app/app.jar"]
```

**GOOD - Non-root Dockerfile compatible with OpenShift:**
```dockerfile
FROM registry.access.redhat.com/\
  ubi9/openjdk-17:latest
# UBI base images default to non-root
# uid 185 (jboss user)

COPY --chown=185:185 \
  target/app.jar /deployments/app.jar

# Explicitly declare non-root user
USER 185

EXPOSE 8080
ENTRYPOINT ["java", \
  "-jar", "/deployments/app.jar"]
```

**OpenShift Route (YAML):**
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: my-app
  namespace: my-project
spec:
  host: my-app.apps.cluster.example.com
  port:
    targetPort: 8080-tcp
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  to:
    kind: Service
    name: my-app
    weight: 100
```

**BuildConfig (Source-to-Image):**
```yaml
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: my-app
spec:
  source:
    type: Git
    git:
      uri: https://github.com/org/my-app
      ref: main
  strategy:
    type: Source
    sourceStrategy:
      from:
        kind: ImageStreamTag
        name: openjdk-17:latest
        namespace: openshift
  output:
    to:
      kind: ImageStreamTag
      name: my-app:latest
  triggers:
    - type: GitHub
      github:
        secret: my-webhook-secret
    - type: ImageChange
```

---

### ⚖️ Comparison Table

| Feature | Vanilla Kubernetes | OpenShift OCP |
|---|---|---|
| Security defaults | Root containers allowed | Restricted SCC blocks root by default |
| Ingress | Ingress resource (controller varies) | Route (built-in HAProxy router) |
| Image registry | External (ECR, GCR, Docker Hub) | Integrated (Quay, internal registry) |
| Build pipelines | External (Jenkins, GitHub Actions) | BuildConfig + Tekton (built-in) |
| Multitenancy | Namespace + manual RBAC | Project (Namespace + RBAC defaults) |
| Cluster upgrades | Manual / Cluster API | CVO automated, channel-based |
| Support | Community (GitHub issues) | Red Hat enterprise SLA |
| Cost | Free (CNCF project) | Commercial license required |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "OpenShift replaces Kubernetes" | OpenShift IS Kubernetes - 100% compatible; `kubectl` works without modification |
| "DeploymentConfig is better than Deployment" | Red Hat deprecated DeploymentConfig in OCP 4.14; use standard `Deployment` for new workloads |
| "`oc` is different from `kubectl`" | `oc` is a superset - all `kubectl` commands work; `oc` adds OpenShift-specific subcommands |
| "OpenShift is just for Java / JBoss" | Language-agnostic; S2I builders exist for Go, Python, Node.js, Ruby, .NET, and custom builders |
| "SCCs are just PodSecurityAdmission" | SCCs predate and are more granular than PSA; SCCs support custom profiles per ServiceAccount |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Pod rejected by SCC - root container**

**Symptom:** Pod stays in `Pending`; event shows `unable to validate against any security context constraint`.
**Root Cause:** Container image runs as `root` (UID 0); `restricted-v2` SCC forbids this.
**Diagnostic:**
```bash
# Check pod events
oc describe pod <pod-name> -n <ns>

# Check which SCC the SA can use
oc adm policy who-can use scc \
  restricted-v2

# Check image's user
docker inspect <image> \
  --format '{{.Config.User}}'
```
**Fix:**
BAD: Add pod to `privileged` SCC to make the error go away.
GOOD: Fix the Dockerfile to use a non-root `USER` directive; or bind the ServiceAccount to `anyuid` SCC with a documented justification in an ADR.
**Prevention:** Add `hadolint` to CI with `DL3002` rule (no `USER root` at end of Dockerfile).

---

**Mode 2: Route not serving traffic - TLS misconfiguration**

**Symptom:** `curl https://my-app.apps.cluster.example.com` returns 503 or SSL handshake error.
**Root Cause:** Route termination mode mismatch; app listens on plain HTTP but Route uses `passthrough`.
**Diagnostic:**
```bash
# Inspect route configuration
oc get route my-app -n my-project -o yaml

# Check router pod logs
oc logs -n openshift-ingress \
  -l ingresscontroller.operator.openshift.io\
/owning-ingresscontroller=default \
  --tail=50
```
**Fix:**
BAD: `termination: passthrough` when app serves plain HTTP on 8080.
GOOD: Use `termination: edge` (TLS terminated at router, plain HTTP to pod) for standard Spring Boot apps; use `passthrough` only for apps doing their own TLS.
**Prevention:** Route configuration review in deployment checklist; validate with `oc status` after deploy.

---

**Mode 3: ImageStream tag not found - broken deployment trigger**

**Symptom:** `DeploymentConfig` or `Deployment` with ImageChange trigger stuck; new build doesn't trigger rollout.
**Root Cause:** ImageStream tag name in `DeploymentConfig` does not match the tag built by `BuildConfig`.
**Diagnostic:**
```bash
# List ImageStream tags
oc get imagestream my-app \
  -n my-project -o wide

# Check build output tag
oc get buildconfig my-app \
  -n my-project \
  -o jsonpath='{.spec.output.to}'
```
**Fix:**
BAD: `BuildConfig` outputs to `my-app:v1.2.3`; `DeploymentConfig` watches `my-app:latest` - no match.
GOOD: Consistently use `my-app:latest` for the tag in both `BuildConfig` output and `DeploymentConfig` trigger.
**Prevention:** Validate ImageStream tag alignment in CI using `oc process` dry-run.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Kubernetes - OpenShift is built on Kubernetes; all core concepts apply
- Docker / Containers - container image fundamentals required before understanding BuildConfig, ImageStream, and SCCs

**Builds On This (learn these next):**
- OpenShift vs Kubernetes - detailed comparison of differences and migration considerations
- OKD - the community upstream of OpenShift (free, unsupported)
- Red Hat Advanced Cluster Management (ACM) - multi-cluster OpenShift management

**Alternatives / Comparisons:**
- Amazon EKS - managed Kubernetes on AWS without OpenShift's additional abstractions
- Rancher (SUSE) - alternative enterprise Kubernetes management platform
- VMware Tanzu - enterprise Kubernetes platform targeting vSphere environments

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────┐
│ WHAT IT IS    Enterprise Kubernetes with │
│               security, tooling, support │
│ PROBLEM       Raw K8s needs assembly;    │
│               enterprise needs hardening │
│ KEY INSIGHT   IS Kubernetes + extras;    │
│               kubectl still works        │
│ USE WHEN      Regulated industries;      │
│               enterprise support needed  │
│ AVOID WHEN    Startup/dev; need latest   │
│               upstream K8s immediately   │
│ TRADE-OFF     Integrated platform /      │
│               licensing cost             │
│ ONE-LINER     RHEL for Kubernetes        │
│ NEXT EXPLORE  OpenShift vs K8s, OKD      │
└──────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. OpenShift IS Kubernetes - `kubectl` works; it adds security and tooling on top
2. SCCs enforce least-privilege by default - images must run as non-root
3. Routes + BuildConfig + ImageStream encode enterprise deployment patterns into defaults

**Interview one-liner:** "OpenShift is Red Hat's enterprise Kubernetes distribution - the same Kubernetes API with stricter security defaults (SCCs), integrated build pipelines, a built-in registry, and commercial support, targeting regulated industries."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When a platform targets regulated, enterprise
environments, security defaults must be opt-out (strict by default), not opt-in.
An insecure default that developers work around is never locked down in production.

**Where else this pattern appears:**
- **Spring Security** - requires explicit configuration to permit routes; all
  requests are denied by default (secure-by-default pattern)
- **AWS IAM** - deny by default; policies must explicitly allow; least-privilege
  is the starting point, not a hardening step
- **Bank network zones** - production systems start in the most restricted zone;
  exceptions require documented justification and review

---

### 💡 The Surprising Truth

OpenShift's Security Context Constraints (SCCs) predate Kubernetes Pod Security
Admission (PSA) by more than five years. When Kubernetes finally added PSA in
1.25 (2022), it was more coarse-grained than OpenShift's SCCs. Red Hat then had
to maintain both systems in OpenShift: SCCs for existing workloads and PSA for
upstream compliance. The platform that pioneered Kubernetes security had to add
a less capable version of its own feature to remain upstream-compatible. This
is a recurring pattern in open-source ecosystems: a downstream innovates, the
upstream standardises a simplified version, and the downstream must maintain both.

---

### 🧠 Think About This Before We Continue

1. **(Type D - Root Cause)** OpenShift's restricted SCC blocks root containers by default - a security control that breaks many Docker images pulled from public registries. What is the root cause of why public Docker images so commonly run as root, and how does OpenShift's SCC model create a forcing function for better supply chain security?

   *Hint:* Look at how Docker's original default (no USER = root) combined with Docker Hub's permissive image publishing created an ecosystem of insecure base images. Research how OpenShift SCC admission blocks these images at the platform gate.

2. **(Type B - Scale)** At 1,000 pods across 50 namespaces, the SCC admission webhook runs on every pod creation. How does OpenShift ensure this admission path does not become a latency bottleneck for cluster scheduling throughput?

   *Hint:* Research Kubernetes admission webhook timeout settings, the CVO's use of leader-elected controllers, and how OpenShift's SCC webhook is co-located with the API server to reduce network hops.

3. **(Type C - Design Trade-off)** Red Hat deprecated `DeploymentConfig` in OCP 4.14 in favour of standard Kubernetes `Deployment`. `DeploymentConfig` had image-change triggers that `Deployment` lacks natively. What does this deprecation decision reveal about the tension between platform-specific abstractions and upstream Kubernetes compatibility?

   *Hint:* Examine what "upstream compatibility" costs in terms of feature parity (what is lost when platform abstractions are removed). Look at how Argo CD or Flux with image reflection can replace image-change triggers using GitOps patterns.

