---
id: CTR-021
title: "OpenShift vs Kubernetes"
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-032, K8S-001
used_by: 
related: CTR-032, K8S-001
tags:
  - kubernetes
  - containers
  - advanced
  - tradeoff
status: complete
version: 2
layout: default
parent: "Containers"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/containers/openshift-vs-kubernetes/
---

⚡ **TL;DR -** OpenShift is a commercially supported, security-hardened Kubernetes distribution; vanilla Kubernetes is the open-source core - OpenShift adds enterprise features at the cost of licensing and opinionation.

| | |
|---|---|
| **Depends on** | Red Hat OpenShift, Kubernetes |
| **Used by** | Containers |
| **Related** | Red Hat OpenShift, Kubernetes, AWS ECS Fargate |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Platform engineering teams evaluating container orchestration face a spectrum from "pure community Kubernetes" to "fully managed PaaS." Each option has different security postures, operational burdens, feature sets, and cost profiles - but most comparisons are vendor marketing rather than engineering-first analysis.

**THE BREAKING POINT:** An organisation chooses vanilla Kubernetes to avoid lock-in, then spends six months assembling a production-grade platform: Ingress controller, image registry, build pipelines, network policies, PSA configuration, monitoring stack, and break-glass upgrade procedures. An organisation chooses OpenShift, then discovers their containerised apps fail SCC admission and must be rearchitected.

**THE INVENTION MOMENT:** Understanding the precise delta between OpenShift and Kubernetes - not a sales comparison but an engineering one - allows architects to make an evidence-based build-vs-buy decision for each layer of the platform.

**EVOLUTION:** OpenShift 3.x used Docker and custom SDN networking. OCP 4.x (2019) rewrote on RHCOS, CRI-O, OVN-K, and the Operator framework. OCP 4.14 deprecated DeploymentConfig. The 2024+ direction prioritises multi-cluster ACM and GitOps-first delivery via OpenShift GitOps (ArgoCD).

---

### 📘 Textbook Definition

**OpenShift vs Kubernetes** is the analysis of how Red Hat OpenShift Container Platform (OCP) differs from upstream Kubernetes in security model (SCCs vs PodSecurityAdmission), networking (Route vs Ingress), build and image management (BuildConfig/ImageStream vs external tooling), Operator ecosystem (OperatorHub vs community Helm), developer experience (web console, `oc` CLI), cluster lifecycle management (CVO vs manual), and commercial support model (Red Hat SLA vs community).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Same engine, different vehicle: Kubernetes is the open-source engine; OpenShift is the Red Hat enterprise car built around it.

> Comparing OpenShift to Kubernetes is like comparing RHEL to the Linux kernel. RHEL includes the kernel plus a tested, supported stack of userspace tools, security hardening, and a support contract. You can run the kernel alone, but RHEL packages it into a product.

**One insight:** Every valid Kubernetes manifest runs on OpenShift without modification - *except* manifests that assume root containers or rely on upstream-only APIs not yet in the OCP release.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. OpenShift passes the Kubernetes conformance test suite - it IS Kubernetes
2. OpenShift ships with an older Kubernetes version than the latest upstream release (typically 1–2 minors behind)
3. Additional abstractions in OpenShift are implemented as CRDs + Operators - not forks
4. Security defaults differ: OpenShift restricts by default, Kubernetes allows by default

**DERIVED DESIGN:** OpenShift adds layers above the Kubernetes API without forking it. Each OpenShift feature is implemented as a Kubernetes Custom Resource managed by an Operator, which means OpenShift can be incrementally updated via the Cluster Version Operator.

**THE TRADE-OFFS:**

**Gain (OpenShift):** Integrated, supported, security-hardened; shorter path to production for enterprises; OperatorHub ecosystem.

**Cost (OpenShift):** Licensing fee; version lag behind upstream; more opinionated (breaking changes when migrating vanilla manifests).

**Gain (vanilla K8s):** Latest features immediately; flexibility; no licensing; cloud-managed options (EKS, GKE, AKS).

**Cost (vanilla K8s):** Must assemble own platform stack; security hardening is your responsibility.

---

### 🧪 Thought Experiment

**SETUP:** Two identical Spring Boot microservices teams: Team A deploys to EKS (vanilla Kubernetes), Team B deploys to OpenShift OCP.

**WHAT HAPPENS ON EKS:** Team A deploys a Docker image with `USER root`. It runs. They create an `Ingress` resource, choose an Ingress controller, configure TLS via cert-manager. They set up ECR as image registry, build in GitHub Actions, and configure their own alerting stack.

**WHAT HAPPENS ON OPENSHIFT:** Team B's `USER root` image is rejected at admission. They rebuild with `USER 1001`. They create a `Route` - TLS is automatic. `BuildConfig` triggers a build on every git push. Monitoring is pre-configured. Deploy completes in half the time - but the image rebuild cost an hour.

**THE INSIGHT:** OpenShift's upfront friction (SCC compliance) prevents downstream security debt. EKS's upfront freedom delays security decisions - which often means they're never made.

---

### 🧠 Mental Model / Analogy

> Kubernetes is a Lego Technic set - all the pieces are there; you assemble the vehicle you want. OpenShift is a finished Lego Technic car - pre-assembled, with a warranty, but you can't substitute parts from other sets as easily.

- **Lego pieces** → Kubernetes primitives (Pod, Service, Ingress, RBAC)
- **Finished car** → OpenShift with integrated Route, SCC, BuildConfig, OperatorHub
- **Warranty** → Red Hat enterprise support SLA
- **Aftermarket parts** → Community Helm charts that may conflict with OCP Operators
- **Assembly instructions** → Platform engineering team (required for vanilla K8s)

Where this analogy breaks down: Unlike Lego, OpenShift does not prevent you from using raw Kubernetes primitives - you can use `Ingress` alongside `Route` on OCP; you can use Helm charts from the community alongside OperatorHub.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Kubernetes is the open-source tool that runs your containers. OpenShift is a product that includes Kubernetes plus many built-in features and professional support, but costs money.

**Level 2 - How to use it (junior developer):**
On vanilla Kubernetes: use `kubectl`, Helm charts, and choose your own Ingress controller. On OpenShift: use `oc` (superset of `kubectl`), `Route` objects for HTTP traffic, `BuildConfig` for builds. The main surprise: your Docker image must not run as root; rebuild with `USER <non-zero-uid>`.

**Level 3 - How it works (mid-level engineer):**
Key API differences: (1) `Route` vs `Ingress` - both work on OCP; Route is native with TLS defaults. (2) `SCC` vs `PodSecurityAdmission` - SCCs are more granular; PSA is the upstream v1.25+ mechanism. (3) `BuildConfig` vs external CI - OCP's native build is cluster-internal; most enterprise teams use Tekton (OCP Pipelines) or external CI. (4) `ImageStream` vs ECR/GCR - ImageStream adds change-trigger semantics to images stored in the cluster registry. (5) `Project` vs `Namespace` - Project wraps Namespace with RBAC templates and resource quota defaults.

**Level 4 - Why it was designed this way (senior/staff):**
The SCC vs PSA difference is architecturally significant. Kubernetes PodSecurityAdmission (PSA) has three modes: privileged, baseline, restricted - applied per namespace. SCCs are per-ServiceAccount grants with custom profiles, enabling "this specific database SA can run privileged, but nothing else in this namespace can." This granularity is why OCP retained SCCs after PSA was introduced upstream. The Cluster Version Operator design reflects a second key insight: a Kubernetes cluster cannot use Kubernetes to update itself (bootstrap problem). OCP solves this by making the CVO a systemd service on the control plane nodes, managing the cluster as an Operator would - declarative, reconciled, rollback-capable. This enables fully automated minor version upgrades, which vanilla Kubernetes leaves entirely to the operator.

---

### ⚙️ How It Works (Mechanism)

Feature delta map (OpenShift additions to vanilla K8s):

```
 Vanilla K8s              OpenShift OCP
 ──────────               ─────────────
 Namespace          ─►    Project (+ RBAC defaults)
 Ingress            ─►    Route (+ TLS, edge/passthrough)
 PodSecurityAdmission ─►  Security Context Constraints
 External registry  ─►    Integrated Quay / cluster
   registry
 External CI        ─►    BuildConfig + Tekton Pipelines
 (image reference)  ─►    ImageStream (+ change triggers)
 Manual upgrade     ─►    Cluster Version Operator (CVO)
 Community Helm     ─►    OperatorHub (curated Operators)
 Manual node mgmt   ─►    Machine API (autoscaling)
```

Kubernetes version lag:

```
 Upstream K8s release  ──►  OCP GA release
 e.g., K8s 1.30        ──►  OCP 4.17 (~2–3 months lag)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (vanilla K8s path):**
```
 Choose managed K8s (EKS/GKE/AKS)
         │
         ▼
 Install Ingress controller (nginx)
         │               ← YOU ARE HERE
         ▼
 Configure cert-manager for TLS
         │
         ▼
 Set up external image registry
         │
         ▼
 Configure PSA per namespace
         │
         ▼
 Build custom monitoring stack
```

**NORMAL FLOW (OpenShift path):**
```
 Install OCP (IPI or UPI)
         │
         ▼
 Route + TLS: built-in
         │               ← YOU ARE HERE
         ▼
 Registry + BuildConfig: built-in
         │
         ▼
 SCCs configured by default
         │
         ▼
 Monitoring stack: built-in
```

**FAILURE PATH:**
- Vanilla K8s: Ingress controller misconfigured → no TLS on any service
- OCP: SCC misconfiguration → all pods in a namespace rejected

**WHAT CHANGES AT SCALE:**
Vanilla K8s at scale requires platform engineering investment equivalent to what OCP includes by default. At 500+ nodes, the delta narrows because both require similar tooling; OCP's value is in the first 0–12 months of operational maturity.

---

### 💻 Code Example

**BAD - Kubernetes Ingress that requires manual TLS configuration:**
```yaml
# Vanilla K8s Ingress
# (requires cert-manager, ingress
#  controller, and secret management)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    cert-manager.io/cluster-issuer:
      letsencrypt-prod
    kubernetes.io/ingress.class: nginx
spec:
  tls:
    - hosts:
        - my-app.example.com
      secretName: my-app-tls
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 8080
```

**GOOD - OpenShift Route with automatic edge TLS:**
```yaml
# OpenShift Route
# TLS is automatic from cluster wildcard
# cert - no cert-manager required
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: my-app
  namespace: my-project
spec:
  # host: auto-generated if omitted
  port:
    targetPort: 8080-tcp
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  to:
    kind: Service
    name: my-app
    weight: 100
# Result: https://my-app-my-project
#   .apps.cluster.example.com
# TLS cert from cluster wildcard cert
```

**SCC comparison:**
```yaml
# Kubernetes PSA (namespace-scoped,
# three fixed levels only)
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    pod-security.kubernetes.io/enforce:
      restricted

---
# OpenShift SCC binding
# (ServiceAccount-scoped, custom profiles)
# Grant specific SA the anyuid SCC
# (allows non-zero arbitrary UID)
# oc adm policy add-scc-to-user \
#   anyuid \
#   system:serviceaccount:prod:db-sa
# Only the db SA can use anyuid;
# all other SAs use restricted-v2.
```

---

### ⚖️ Comparison Table

| Dimension | Vanilla Kubernetes | Red Hat OpenShift OCP |
|---|---|---|
| **Cost** | Free (CNCF) | Commercial license |
| **Support** | Community forums/GitHub | Red Hat 24/7 enterprise SLA |
| **Security default** | Permissive (root allowed) | Restrictive (SCCs, restricted-v2) |
| **Security mechanism** | PodSecurityAdmission (3 modes) | SCCs (per-SA, custom profiles) |
| **HTTP routing** | Ingress (controller varies) | Route (HAProxy, TLS built-in) |
| **Image build** | External CI only | BuildConfig, S2I, Tekton built-in |
| **Image registry** | External (ECR, GCR, Docker Hub) | Internal Quay / cluster registry |
| **Kubernetes version** | Latest stable | 1–2 minors behind upstream |
| **Cluster upgrades** | Manual / Cluster API | CVO automated, channel-based |
| **Node OS** | Any Linux | RHCOS (immutable, managed) |
| **Operator ecosystem** | Helm + community | OperatorHub (curated, supported) |
| **Developer console** | Dashboard (read-only) | Full developer + admin console |
| **Multi-tenancy unit** | Namespace | Project (Namespace + RBAC defaults) |
| **Lock-in risk** | Low | Medium (Route, SCC, OperatorHub APIs) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "OpenShift is a fork of Kubernetes" | OpenShift passes Kubernetes conformance; it adds CRDs/Operators on top, not a fork |
| "You must use Route; Ingress is unavailable" | Both Route and Ingress work on OCP; Route is the native preferred API |
| "SCCs and PSA are equivalent" | PSA has 3 fixed namespace levels; SCCs have per-SA custom profiles - fundamentally more granular |
| "OpenShift is always behind Kubernetes" | OCP ships 1–2 minor versions behind upstream; this is a deliberate stability gate, not neglect |
| "Switching from EKS to OCP is just a manifest copy" | SCC compliance, Route vs Ingress, and `DeploymentConfig` deprecation all require manifest changes |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Migration from vanilla K8s to OCP - SCC failures**

**Symptom:** All pods fail with `unable to validate against any security context constraint`.

**Root Cause:** Existing Dockerfiles use `USER root`; images pulled from public registries run as root.

**Diagnostic:**
```bash
# List all images in deployment YAMLs
grep -r "image:" k8s-manifests/ \
  | awk '{print $2}' | sort -u

# Inspect each image for USER directive
docker inspect <image> \
  --format '{{.Config.User}}'
# Empty or "root" = will fail OCP SCC
```
**Fix:**
BAD: Set namespace SCC to `privileged` for all workloads to unblock migration.
GOOD: Rebuild images with non-root `USER`; for third-party images, bind the specific ServiceAccount to `anyuid` SCC with a documented exception.

**Prevention:** Pre-migration audit using `oc adm policy scc-review` dry-run before cutover.

---

**Mode 2: OCP version lag causes upstream API incompatibility**

**Symptom:** Helm chart or Kubernetes manifest uses a beta/alpha API that OCP does not yet ship.

**Root Cause:** Community tooling targets latest Kubernetes; OCP trails by 1–2 minor versions.

**Diagnostic:**
```bash
# Check OCP Kubernetes version
oc version | grep Kubernetes

# Check which API versions are available
oc api-versions | grep \
  "networking\|policy\|batch"

# Validate manifest against cluster
kubectl --dry-run=server \
  apply -f manifest.yaml
```
**Fix:**
BAD: Assume API availability based on latest K8s docs.
GOOD: Check OCP release notes for API graduation; use `oc api-versions` before deploying manifests from community Helm charts.

**Prevention:** Pin Helm chart versions known to be OCP-compatible; maintain an OCP compatibility matrix in the platform team wiki.

---

**Mode 3: OperatorHub Operator conflicts with manually installed components**

**Symptom:** Two Prometheus Operators running in the cluster; custom rules are not scraped; metrics appear duplicated.

**Root Cause:** OCP ships a cluster-managed Prometheus Operator (Cluster Monitoring Operator); team also installed community Prometheus Operator via OperatorHub.

**Diagnostic:**
```bash
# Find all Prometheus-related Operators
oc get csv -A | grep prometheus

# Find all PrometheusRule CRD owners
oc get crd | grep monitoring.coreos
```
**Fix:**
BAD: Install community monitoring stack on top of OCP's built-in monitoring.
GOOD: Extend OCP's cluster monitoring via `user-workload-monitoring` feature; add custom `PrometheusRule` objects that are scraped by the managed Operator.

**Prevention:** Operator governance policy: before installing any Operator, check if OCP provides the same capability natively.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Kubernetes - full understanding of Kubernetes primitives required before evaluating the delta
- Red Hat OpenShift - specific knowledge of OpenShift additions (SCCs, Route, BuildConfig)

**Builds On This (learn these next):**
- OKD - community upstream of OpenShift (free, same codebase, no Red Hat support)
- Red Hat Advanced Cluster Management - multi-cluster management across OCP fleets
- AWS EKS - managed vanilla Kubernetes alternative for AWS-native workloads

**Alternatives / Comparisons:**
- Rancher (SUSE) - alternative enterprise K8s management platform; UI-first
- VMware Tanzu - enterprise K8s targeting vSphere + multi-cloud
- Amazon EKS - managed K8s without opinionated developer abstractions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────┐
│ WHAT IT IS    Engineering delta between  │
│               OCP and upstream K8s       │
│ PROBLEM       Uninformed platform choice │
│               leads to rework or debt    │
│ KEY INSIGHT   Same K8s core; OCP adds    │
│               SCCs, Route, CVO, OperHub  │
│ USE WHEN      Evaluating K8s platform    │
│               for enterprise deployment  │
│ AVOID WHEN    Already committed to one   │
│               platform                   │
│ TRADE-OFF     OCP integrated+cost vs     │
│               K8s flexible+assembly      │
│ ONE-LINER     RHEL : Linux :: OCP : K8s  │
│ NEXT EXPLORE  OKD, ACM, Rancher          │
└──────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Type F - Comparison)** OpenShift uses SCCs (ServiceAccount-scoped) while upstream Kubernetes uses PodSecurityAdmission (namespace-scoped). What class of multi-tenant security requirements can SCCs satisfy that PSA's three fixed modes cannot - and does this justify the complexity difference?

   *Hint:* Research how OpenShift SCCs interact with OCI image build pipelines and how hadolint DL3002 maps to SCC runAsNonRoot enforcement.

2. **(Type B - Scale)** The Cluster Version Operator enables automated minor-version upgrades of OpenShift clusters. At what cluster size and workload criticality does the operational risk of automated control-plane upgrades outweigh the operational cost of manual upgrade processes?

   *Hint:* Look at OpenShift's SCC implementation - it runs as a compiled admission plugin inside the API server binary, avoiding the network hop that external webhooks require.

3. **(Type C - Design Trade-off)** A team choosing between EKS and OpenShift calculates that OCP licensing costs £200K/year but saves two platform engineers. Under what conditions is the build-vs-buy trade-off clearly in favour of OCP - and what factors would flip the decision toward vanilla EKS?

   *Hint:* Compare OCP Deployment plus ArgoCD image updater to DeploymentConfig image-change triggers; research GitOps tools that provide equivalent push-based deploy on new image push.
