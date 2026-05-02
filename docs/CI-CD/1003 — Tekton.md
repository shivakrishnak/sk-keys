---
layout: default
title: "Tekton"
parent: "CI/CD"
nav_order: 1003
permalink: /ci-cd/tekton/
number: "1003"
category: CI/CD
difficulty: ★★★
depends_on: Kubernetes, Pipeline as Code, Continuous Integration
used_by: Continuous Delivery, GitOps, ArgoCD
related: ArgoCD, Jenkins, GitLab CI
tags:
  - cicd
  - kubernetes
  - devops
  - advanced
  - containers
---

# 1003 — Tekton

⚡ TL;DR — Tekton is a Kubernetes-native CI/CD framework where pipeline tasks and runs are Kubernetes Custom Resources, enabling portable, cloud-agnostic pipelines that run entirely inside your cluster.

| #1003 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Kubernetes, Pipeline as Code, Continuous Integration | |
| **Used by:** | Continuous Delivery, GitOps, ArgoCD | |
| **Related:** | ArgoCD, Jenkins, GitLab CI | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Kubernetes-native organisation runs Jenkins for CI/CD. Jenkins is not a Kubernetes citizen — it has its own controller (a stateful Java process outside the cluster), its own agent lifecycle management, its own RBAC separate from Kubernetes RBAC, and its own storage for build artifacts. The CI/CD system is a second control plane alongside Kubernetes, requiring separate monitoring, scaling, and security policies. When the organisation wants portable pipelines that travel with the application across clusters or clouds, Jenkins' external coupling makes this impossible.

**THE BREAKING POINT:**
Non-Kubernetes CI systems can't leverage Kubernetes primitives (RBAC, service accounts, secrets, resource limits, cluster autoscaler) for pipeline execution. CI becomes the outlier — everything else is cloud-native, but CI is still managed as a special case.

**THE INVENTION MOMENT:**
This is exactly why Tekton was created: define CI/CD as Kubernetes Custom Resources so pipelines are first-class Kubernetes citizens, leverage all Kubernetes capabilities for execution, and run identically on any conformant Kubernetes cluster.

---

### 📘 Textbook Definition

**Tekton** is an open-source Kubernetes-native CI/CD framework originally developed by Google and donated to the CD Foundation (Linux Foundation). It defines a set of Kubernetes Custom Resource Definitions (CRDs): `Task` (a unit of work), `Pipeline` (an ordered sequence of Tasks), `TaskRun` (an instance of a Task execution), and `PipelineRun` (an instance of a Pipeline execution). Each TaskRun spawns a Kubernetes Pod; each step in a Task is a container in that pod. Tasks and Pipelines are reusable, parameterised, and versioned. Tekton Catalog provides a community repository of reusable Tasks (git-clone, kaniko, helm-upgrade, etc.).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Tekton turns CI/CD pipelines into Kubernetes objects — tasks become pods, pipelines become pod orchestrations.

**One analogy:**
> Tekton is like the Kubernetes Job API, but specifically designed for CI/CD. Instead of saying "run this workload occasionally" (Kubernetes Jobs), you say "run this sequence of workloads with these inputs and pass artifacts between them" (Tekton Pipeline). It speaks Kubernetes natively — using the same YAML, kubectl, RBAC, and secrets you already use.

**One insight:**
The key architectural distinction: in Tekton, **pipelines ARE Kubernetes resources**. They're stored in etcd, managed by `kubectl`, monitored by Kubernetes tooling, and subject to the same RBAC as any other cluster resource. There is no separate CI "controller" to manage — Tekton's controller is a Kubernetes controller-manager watching CRD objects.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each Task runs as a Kubernetes Pod — leveraging all Kubernetes scheduling and isolation guarantees.
2. Pipelines are declarative — the desired state, not imperative scripts.
3. Workspace volumes connect tasks — artifacts flow through shared PersistentVolumeClaims or ConfigMaps.
4. Everything is a Kubernetes resource — tasks, pipelines, runs, and triggers are CRDs.

**DERIVED DESIGN:**
Because Tasks are Pods, they inherit all Kubernetes capabilities: resource limits (CPU/memory per step), node selectors (run GPU step on GPU node), service accounts (scoped RBAC for each task), init containers, sidecars (for service dependencies), and pod security policies. These capabilities would require plugins or workarounds in non-Kubernetes CI systems.

Workspaces decouple task implementation from artifact storage strategy: a Pipeline may declare a `source` workspace; the PipelineRun binds it to a PVC, an emptyDir, or a ConfigMap — based on what's available in that cluster.

**THE TRADE-OFFS:**
**Gain:** Fully Kubernetes-native. No external CI system. Leverages RBAC, secrets, and cluster autoscaler. Portable across clusters and clouds.
**Cost:** High complexity for simple use cases. Verbose YAML (a "hello world" pipeline is 40+ lines). No built-in UI for pipeline visualisation (requires Tekton Dashboard separately). Managing PVCs for workspace storage adds operational concern. Steep learning curve for teams unfamiliar with Kubernetes CRDs.

---

### 🧪 Thought Experiment

**SETUP:**
A platform team must run identical CI pipelines in 3 different environments: a dev cluster (GKE), a staging cluster (EKS), and a production cluster (on-premises OpenShift).

**WHAT HAPPENS WITH JENKINS:**
Jenkins is installed on a VM outside all three clusters. It must authenticate to three different Kubernetes clusters. Changes to pipeline configuration require deploying to Jenkins (separate process). Security policies differ per cluster — Jenkins must manage three different credential sets. "Identical pipelines" actually diverge because Jenkins config is centralised, not cluster-local.

**WHAT HAPPENS WITH TEKTON:**
The same `Pipeline` and `Task` CRD YAML files are applied to all three clusters with `kubectl apply`. Each cluster runs pipelines locally using its own Kubernetes RBAC, secrets, and network policies. No central CI controller. "Identical pipelines" are literally the same YAML files — version-controlled, Helm-charts-deployable.

**THE INSIGHT:**
Tekton's portability comes from treating CI/CD as cluster configuration, not as an external service. The same GitOps tooling (Flux, ArgoCD) that manages application config also manages pipeline definitions.

---

### 🧠 Mental Model / Analogy

> Tekton is to CI/CD what CronJob is to scheduled tasks in Kubernetes: it takes a concept that previously needed an external system and makes it a native Kubernetes primitive. You define it in YAML, `kubectl apply` it, and Kubernetes manages the lifecycle. The difference is that Tekton's primitives are richer — tasks, pipelines, parameters, workspaces, and result passing — designed specifically for the CI/CD use case.

- "CronJob" → Tekton Task (a unit of execution)
- "Schedule spec" → PipelineRun (triggers a Pipeline)
- "Container in the CronJob" → Step in a Task
- "PersistentVolume mount" → Tekton Workspace
- "`kubectl get cronjobs`" → `kubectl get pipelineruns`

Where this analogy breaks down: CronJobs are always time-triggered and independent. Tekton Pipelines have explicit task dependencies, result passing between tasks, and externally-triggered runs (via Tekton Triggers) — far more orchestration complexity.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Tekton is a way to define and run your build-test-deploy process using Kubernetes itself. Instead of installing special CI software, you describe each step as a Kubernetes configuration file. Kubernetes then runs those steps using containers, the same way it runs your application.

**Level 2 — How to use it (junior developer):**
Install Tekton Pipelines in your cluster (`kubectl apply`). Create a `Task` YAML defining steps with container images and commands. Create a `Pipeline` YAML ordering those tasks. Apply both. Create a `PipelineRun` YAML to trigger a run — Kubernetes executes the pods and stores results. Install Tekton Dashboard for a web UI. Use `tkn` (Tekton CLI) to manage runs: `tkn pipelinerun list`, `tkn pipelinerun logs`.

**Level 3 — How it works (mid-level engineer):**
Tekton's controller watches for new `PipelineRun` objects. It computes the execution graph (DAG of tasks), creates `TaskRun` objects for ready tasks, and the TaskRun controller creates Pods for each TaskRun. Steps in a Task share a Pod (and thus a temporary filesystem). Results (string values up to 4KB) are passed via `/tekton/results/` files — Tasks write results, subsequent tasks receive them as parameters. Larger artifacts use Workspaces (PVC-backed volumes shared across tasks in a pipeline). `Tekton Triggers` implements webhook-based pipeline triggering: an `EventListener` Pod receives webhooks, `TriggerBinding` extracts parameters, and `TriggerTemplate` creates `PipelineRun` objects.

**Level 4 — Why it was designed this way (senior/staff):**
Tekton was designed at Google as the internal CI/CD primitive for Knative (the serverless Kubernetes framework). The CRD-based design was deliberate — it allows Tekton to piggyback on Kubernetes' reconciliation loop, watch semantics, and `kubectl` tooling without building a separate API server. The result vs workspace distinction (small strings vs large blobs) reflects the technical constraint that etcd (where CRD status is stored) has a max object size (~1.5 MB). By keeping results small and funnelling large blobs through Workspaces (PVCs), Tekton avoids overloading etcd. This design decision is often confusing for new users but critical for cluster stability at scale.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  TEKTON RESOURCE HIERARCHY                  │
├─────────────────────────────────────────────┤
│  Pipeline (CRD)                             │
│  ├─ Task: git-clone                         │
│  ├─ Task: maven-build (needs: git-clone)    │
│  ├─ Task: unit-test (needs: maven-build)    │
│  └─ Task: docker-push (needs: unit-test)    │
│                                             │
│  PipelineRun (CRD — triggers execution)     │
│  ├─ Workspace: source-code → PVC            │
│  ├─ Param: IMAGE=myorg/myapp                │
│  └─ Param: TAG=sha-abc123                   │
│                                             │
│  EXECUTION:                                 │
│  PipelineRun → TaskRun(git-clone) → Pod     │
│             → TaskRun(maven-build) → Pod   │
│             → TaskRun(unit-test) → Pod      │
│             → TaskRun(docker-push) → Pod    │
│                                             │
│  Each Pod: steps = init containers          │
│  Workspace: PVC mounted to each Pod         │
└─────────────────────────────────────────────┘
```

**Task definition:**
```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: maven-build
spec:
  params:
    - name: maven-goals
      type: string
      default: "package"
  workspaces:
    - name: source      # input: cloned repo
    - name: maven-repo  # Maven ~/.m2 cache (PVC)
  results:
    - name: jar-path    # output: path to built JAR
  steps:
    - name: build
      image: maven:3.9-eclipse-temurin-21
      workingDir: $(workspaces.source.path)
      script: |
        mvn $(params.maven-goals) -DskipTests \
          -Dmaven.repo.local=$(workspaces.maven-repo.path)
        JAR=$(find target -name "*.jar" | head -1)
        printf "%s" "$JAR" > $(results.jar-path.path)
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Webhook → Tekton Triggers EventListener Pod
  → TriggerBinding extracts: repo, branch, SHA
  → TriggerTemplate creates PipelineRun CRD
  → Tekton controller: PipelineRun → TaskRuns
  → TaskRun(git-clone): Pod created, PVC mounted
  → TaskRun(maven-build): waits for git-clone [← YOU ARE HERE]
    Pod created, same PVC mounted
  → TaskRun(unit-test): runs against built artifact
  → TaskRun(docker-push): builds + pushes image
  → PipelineRun status: Succeeded
  → GitHub commit status updated via pipeline step
```

**FAILURE PATH:**
```
TaskRun(unit-test) fails: 3 tests fail
  → PipelineRun status: Failed
  → Subsequent TaskRuns: skipped
  → `tkn pipelinerun describe` shows failed step
  → `tkn taskrun logs pipeline-run-abc-unit-test` shows output
  → Pod is automatically cleaned up (configurable retention)
```

**WHAT CHANGES AT SCALE:**
At 1000 pipeline runs per day, etcd is written frequently (each CRD status update is a write). PVC provisioning latency becomes a bottleneck if using dynamic provisioning — pipeline start time is gated on storage. Teams use VolumeClaimTemplates for per-run PVCs and pre-provisioned PVC pools for cache. PipelineRun retention policies are critical — keeping all historical PipelineRun objects fills etcd.

---

### 💻 Code Example

**Example 1 — Simple Pipeline definition:**
```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: java-ci-pipeline
spec:
  params:
    - name: git-url
    - name: image-name
    - name: image-tag
  workspaces:
    - name: source
    - name: maven-cache
  tasks:
    - name: fetch-source
      taskRef:
        resolver: cluster  # use Task from cluster catalog
        params:
          - name: kind
            value: task
          - name: name
            value: git-clone  # from Tekton Hub
      workspaces:
        - name: output
          workspace: source
      params:
        - name: url
          value: $(params.git-url)
        - name: revision
          value: main

    - name: build
      taskRef:
        name: maven-build  # custom Task defined above
      runAfter: [ fetch-source ]
      workspaces:
        - name: source
          workspace: source
        - name: maven-repo
          workspace: maven-cache

    - name: push-image
      taskRef:
        resolver: cluster
        params:
          - { name: name, value: kaniko }  # Tekton Hub task
      runAfter: [ build ]
      workspaces:
        - name: source
          workspace: source
      params:
        - name: IMAGE
          value: $(params.image-name):$(params.image-tag)
```

**Example 2 — PipelineRun (triggers execution):**
```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: java-ci-run-
spec:
  pipelineRef:
    name: java-ci-pipeline
  params:
    - name: git-url
      value: https://github.com/myorg/myapp
    - name: image-name
      value: myorg/myapp
    - name: image-tag
      value: sha-abc123
  workspaces:
    - name: source
      volumeClaimTemplate:   # fresh PVC per run
        spec:
          accessModes: [ ReadWriteOnce ]
          resources:
            requests:
              storage: 1Gi
    - name: maven-cache
      persistentVolumeClaim:
        claimName: maven-cache-pvc  # shared cache PVC
```

---

### ⚖️ Comparison Table

| Aspect | Tekton | Jenkins | GitHub Actions | ArgoCD |
|---|---|---|---|---|
| Architecture | Kubernetes CRDs | Controller + agents | GitHub-hosted runners | Kubernetes operator |
| Portability | Any K8s cluster | Anywhere with JVM | GitHub only | Any K8s cluster |
| UI | Dashboard (separate) | Built-in Blue Ocean | Built-in | Built-in |
| Complexity | Very High | High | Low | Medium |
| Best For | K8s-native platform teams | Enterprise, air-gapped | GitHub orgs | GitOps CD |

How to choose: Use Tekton when you're building a CI/CD platform for a Kubernetes-native organisation and need full control over execution. Use GitHub Actions or GitLab CI for individual team pipelines. Combine Tekton (CI) with ArgoCD (CD) for a fully Kubernetes-native CI/CD platform.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Tekton is a replacement for ArgoCD | Tekton handles CI (build, test, push image); ArgoCD handles CD (deploy to cluster). They complement each other. Tekton doesn't deploy applications; ArgoCD doesn't build them |
| Tekton Tasks are containers | Tekton Tasks are Pods — a Task has multiple steps that run as containers within the SAME Pod, sharing a filesystem and lifecycle |
| Result passing can handle large artifacts | Tekton Results are limited to ~4KB (stored in etcd). Large artifacts (JARs, Docker images) must use Workspaces backed by PVCs or push to external storage |
| Tekton is easy to use directly | Tekton is a building block for CI/CD platforms, not an end-user tool. Tools like Tekton Chains, Shipwright, and Konflux build opinionated workflows on top of Tekton primitives |

---

### 🚨 Failure Modes & Diagnosis

**1. PVC Provisioning Latency Stalls Pipeline Starts**

**Symptom:** PipelineRuns consistently take 2–3 minutes before the first pod starts. The pipeline log shows "Waiting for workspace PVC to be bound."

**Root Cause:** Dynamic PVC provisioning (StorageClass with `volumeBindingMode: WaitForFirstConsumer`) is slow in the cluster's storage backend.

**Diagnostic:**
```bash
# Check PVC binding status
kubectl get pvc -n tekton-pipelines \
  | grep Pending

# Check StorageClass provisioner latency
kubectl describe pvc source-pvc-xyz \
  | grep -A5 Events
```

**Fix:** Use pre-provisioned PVCs or change StorageClass to `volumeBindingMode: Immediate` with an appropriate storage backend.

**Prevention:** Benchmark storage provisioning latency during platform setup. Set a pipeline start-time SLO and alert if crossed.

---

**2. etcd Size Growth From Accumulated PipelineRun Objects**

**Symptom:** Kubernetes cluster health degrades — API server slowness, etcd write latency increases over weeks.

**Root Cause:** All PipelineRun and TaskRun objects accumulate in etcd indefinitely. Each run creates 5–20 CRD objects with status payload.

**Diagnostic:**
```bash
# Count accumulated PipelineRun objects
kubectl get pipelineruns -A | wc -l
kubectl get taskruns -A | wc -l

# Check etcd database size
kubectl exec -n kube-system etcd-master -- \
  etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint status --write-out=table
```

**Fix:** Configure Tekton's prune settings:
```yaml
# In TektonConfig CRD
apiVersion: operator.tekton.dev/v1alpha1
kind: TektonConfig
spec:
  pruner:
    resources: [ pipelinerun ]
    keep: 100           # keep last 100 per pipeline
    schedule: "0 * * * *"  # hourly cleanup
```

**Prevention:** Configure pruning from day 1. Never run Tekton without retention policies.

---

**3. Task Step Failing Due to Insufficient Memory**

**Symptom:** Maven build step OOMKilled. Pod restarts repeatedly. Pipeline run marked Failed with "reason: OOMKilled".

**Root Cause:** Container resource limits set too low for the build workload.

**Diagnostic:**
```bash
# Check container resource usage
kubectl top pod <taskrun-pod-name> -n tekton-pipelines

# Check OOM events
kubectl describe pod <taskrun-pod-name> \
  | grep -A5 "OOMKilled\|Limits"
```

**Fix:**
```yaml
steps:
  - name: maven-build
    image: maven:3.9-eclipse-temurin-21
    resources:
      requests:
        memory: "1Gi"
        cpu: "1"
      limits:
        memory: "4Gi"    # Maven needs heap room
        cpu: "2"
    env:
      - name: MAVEN_OPTS
        value: "-Xmx2g"  # keep JVM heap below limit
```

**Prevention:** Profile build memory usage before setting limits. Add 50% buffer above measured peak usage.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Kubernetes` — Tekton tasks run as Kubernetes Pods; deep Kubernetes knowledge is required
- `Pipeline as Code` — Tekton implements Pipeline as Code via CRD YAML definitions stored in Git
- `Continuous Integration` — Tekton implements the infrastructure layer of CI; the practice context is required

**Builds On This (learn these next):**
- `ArgoCD` — Tekton handles CI; ArgoCD handles CD — the two form a complete Kubernetes-native CI/CD platform
- `GitOps` — Tekton pipelines are typically managed as GitOps resources alongside the application they build
- `Continuous Delivery` — Tekton Pipelines implement the pipeline stages of CD

**Alternatives / Comparisons:**
- `GitHub Actions` — simpler hosted alternative for teams not requiring Kubernetes-native execution
- `Jenkins` — mature CI with plugins; predecessor pattern that Tekton was designed to improve upon
- `ArgoCD` — handles the CD (deployment) half of the CI/CD pipeline; complements Tekton

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kubernetes-native CI/CD: tasks and        │
│              │ pipelines defined as Kubernetes CRDs      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ External CI tools aren't Kubernetes       │
│ SOLVES       │ citizens — separate RBAC, scaling, ops    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Results are limited to 4KB (etcd); for    │
│              │ large artifacts, always use Workspaces    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Platform teams building Kubernetes-native │
│              │ CI/CD infrastructure across clusters      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small teams needing quick CI — GitHub     │
│              │ Actions is 10x simpler to get started     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Maximum Kubernetes integration vs         │
│              │ high complexity and verbose YAML          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your CI pipeline as kubectl apply —      │
│              │  runs where Kubernetes runs"              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ArgoCD → GitOps → Tekton Chains           │
│              │ (supply chain security)                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A platform team deploys Tekton in a multi-tenant Kubernetes cluster shared by 20 teams. Each team can create their own `Task` and `Pipeline` CRDs and trigger `PipelineRun` objects. A malicious tenant submits a Task with a step that uses `hostPID: true` and exfiltrates secrets from other pods on the same node. Design the complete Kubernetes security model — RBAC, PodSecurityAdmission, NetworkPolicy, ResourceQuota — that would prevent this attack without breaking legitimate pipeline execution.

**Q2.** Your organisation's Tekton-based CI platform processes 500 PipelineRuns per day. After 3 months, etcd sizes hit 6GB and the Kubernetes API server response time doubles. You implement the Tekton pruner but it unexpectedly deletes a PipelineRun from 2 days ago that a compliance auditor needed for evidence of a security scan. Design a retention policy that satisfies both operational needs (prevent etcd bloat) and compliance needs (retain evidence for 90 days) — considering where the long-term audit data should live instead of etcd.

