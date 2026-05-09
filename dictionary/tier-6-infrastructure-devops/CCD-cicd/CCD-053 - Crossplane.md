---
version: 1
layout: default
title: "Crossplane"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /ci-cd/crossplane/
id: CCD-053
category: CI/CD
difficulty: ★★★
depends_on: Kubernetes, Infrastructure as Code, GitOps
used_by: CI-CD, Kubernetes
related: Terraform Overview, AWS CDK (Cloud Development Kit), ArgoCD
tags:
  - cicd
  - kubernetes
  - devops
  - advanced
---

# CCD-053 - Crossplane

⚡ **TL;DR -** Crossplane extends Kubernetes to manage cloud infrastructure - AWS, GCP, Azure resources - as Kubernetes custom resources, enabling GitOps-native IaC without a separate Terraform workflow.

| Field | Value |
|-------|-------|
| **Depends on** | Kubernetes, Infrastructure as Code, GitOps |
| **Used by** | CI-CD, Kubernetes |
| **Related** | Terraform Overview, AWS CDK (Cloud Development Kit), ArgoCD |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Application teams use Kubernetes to manage their workloads with GitOps. Infrastructure (RDS databases, S3 buckets, IAM roles) is managed separately in Terraform, with a different toolchain, different state management, different PR process, and a different team. Every app deployment that needs a new database requires a cross-team ticket, a Terraform PR in a separate repo, and a wait of hours to days.

**THE BREAKING POINT:** A developer needs an RDS instance for a new service. They open a Jira ticket for the platform team. The platform team runs Terraform. The database is created three days later. The developer cannot self-serve infrastructure - even though their application runs on a platform (Kubernetes) that has everything needed to manage it. The toolchain split is the bottleneck.

**THE INVENTION MOMENT:** What if cloud resources were just more Kubernetes objects? A developer who can already create a `Deployment` could also create a `PostgreSQLInstance` using the same tools, the same GitOps workflow, and the same RBAC. Crossplane installs providers that teach Kubernetes how to create and manage cloud resources as custom resources.

---

### 📘 Textbook Definition

**Crossplane** is a CNCF-graduated open-source framework that extends Kubernetes with the ability to manage cloud infrastructure resources (AWS, GCP, Azure, and others) as Kubernetes Custom Resources. It introduces Providers (controllers that translate Kubernetes reconciliation into cloud API calls), Managed Resources (one-to-one mappings to cloud resource types), Compositions (templates that assemble multiple managed resources into a higher-level abstraction), and Composite Resources (XR - instances of a Composition consumed by application teams).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Crossplane makes cloud infrastructure (RDS, S3, VPCs) into Kubernetes resources that your GitOps pipeline can manage.

> Think of Crossplane as a universal adapter plug. Your Kubernetes cluster is the socket (power source), and every cloud provider is a device that needs power. Crossplane is the adapter that makes any cloud device's plug fit the Kubernetes socket - so you manage all devices with the same wall socket.

**One insight:** The critical design insight is **the Kubernetes reconciliation loop as infrastructure automation**. Crossplane reuses the battle-tested controller pattern: desired state declared in YAML, actual state observed from the cloud API, controller continuously reconciles the difference. You get drift detection and self-healing for free - because it is the same mechanism that keeps your pods running.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Infrastructure is declarative desired state, just like Kubernetes workloads.
2. The controller reconciliation loop (observe → diff → act) is the universal infrastructure automation primitive.
3. RBAC-controlled access to Kubernetes resources is a solved problem - the same model should govern infrastructure resources.
4. Application teams should be able to self-serve infrastructure within platform-defined guardrails, without learning a separate toolchain.

**DERIVED DESIGN:** Crossplane installs Provider controllers (e.g., `provider-aws`) that register Kubernetes CRDs for every supported cloud resource type. A developer creates a `RDSInstance` custom resource; the provider controller watches it and calls the AWS API to create, update, or delete the actual RDS instance. Compositions add an abstraction layer: platform teams define a `PostgreSQLDatabase` Composition that assembles an RDSInstance, a SecurityGroup, a ParameterGroup, and a SubnetGroup - the developer only creates a simple `PostgreSQLDatabase` object.

**THE TRADE-OFFS:**
**Gain:** Unified control plane (Kubernetes), GitOps-native IaC, self-service infrastructure with RBAC guardrails, drift detection, and Kubernetes-native lifecycle management.
**Cost:** Kubernetes is now a dependency for ALL infrastructure management - including the infrastructure Kubernetes itself runs on. Crossplane Compositions are complex to author. Provider coverage is broad but not always at parity with Terraform's provider ecosystem. Debugging requires Kubernetes troubleshooting skills.

---

### 🧪 Thought Experiment

**SETUP:** Your company uses GitOps (ArgoCD) for Kubernetes workloads and Terraform for cloud infrastructure. A new microservice needs an S3 bucket and an SQS queue. Currently, that requires a Terraform PR in a separate repo reviewed by the platform team.

**WHAT HAPPENS WITHOUT CROSSPLANE:** Developer opens Jira ticket. Platform team reviews, writes Terraform HCL, opens a PR, gets it reviewed, runs `terraform apply`. Developer gets their bucket and queue 48 hours later. The provisioning is in a separate repo and pipeline, invisible to the developer's GitOps workflow.

**WHAT HAPPENS WITH CROSSPLANE:** Developer adds two YAML files to their application's GitOps repository:
```yaml
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: my-service-uploads
spec: { ... }
```
ArgoCD syncs the repository. Crossplane's provider-aws controller sees the new object, calls the S3 API, creates the bucket, and updates the object's status with the bucket ARN. Total time: under 2 minutes. Entire workflow is visible in the same GitOps dashboard as the application deployment.

**THE INSIGHT:** Crossplane eliminates the **toolchain boundary** between application and infrastructure. When both live in Kubernetes YAML managed by GitOps, the developer's delivery workflow is uniform - no context switching, no cross-team tickets, no separate state management.

---

### 🧠 Mental Model / Analogy

> Think of Crossplane as a **franchise model for cloud infrastructure**. The franchisor (platform team) defines the standard product specifications (Compositions): what a "database" or "message queue" means in your org - which cloud region, encryption settings, backup policy. Franchisees (application teams) order from the menu (Composite Resources) using a simple standard form, without knowing or caring about the underlying kitchen (cloud APIs). The franchise system (Kubernetes + Crossplane) ensures consistent quality across all orders.

- Franchisor = platform team defining Compositions
- Franchise menu = Composite Resource Definition (XRD) with self-service API
- A menu order = a Composite Resource (XR) instance
- Kitchen equipment = Provider and Managed Resources
- Franchise standards = RBAC + Composition constraints
- Quality audits = Kubernetes reconciliation drift detection

Where this analogy breaks down: A franchise menu is static; Crossplane Compositions can be updated, and existing XR instances will be reconciled to the new spec - sometimes causing unintended changes to live infrastructure if Composition upgrades are not carefully versioned.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Crossplane lets you create cloud resources (like databases and storage buckets) by writing Kubernetes YAML files, the same way you create application deployments. You don't need to learn Terraform - your team's existing Kubernetes workflow handles everything.

**Level 2 - How to use it (junior developer):**
Your platform team installs Crossplane and a cloud provider package (e.g., `provider-aws`) in your Kubernetes cluster. They create a `Composition` that defines what a PostgreSQL database means in your org. You create a `PostgreSQLDatabase` object in your namespace. Crossplane creates the RDS instance, security group, and parameter group automatically. The database connection string appears in a Kubernetes Secret in your namespace, ready for your app to consume.

**Level 3 - How it works (mid-level engineer):**
Crossplane has four main concepts. A **Provider** installs CRDs and controllers for a cloud service (e.g., `provider-aws` registers `RDSInstance`, `S3Bucket`, etc.). A **Managed Resource** (MR) is a one-to-one CRD mapping to a specific cloud resource type. A **Composite Resource Definition** (XRD) defines a custom API (e.g., `PostgreSQLDatabase`) that application teams use. A **Composition** defines how one XRD instance maps to a set of Managed Resources. When a developer creates an XR, the Composition controller creates the underlying MRs, which the Provider controllers then reconcile against the cloud API.

**Level 4 - Why it was designed this way (senior/staff):**
Crossplane's design rejects the imperative workflow of Terraform (plan → apply) in favour of the Kubernetes declarative control loop. This decision has deep implications: there is no `crossplane plan` command - the system continuously reconciles toward desired state. Drift is automatically detected and corrected (if permitted). This makes Crossplane suitable for long-lived infrastructure that must remain consistent, but it also means that changes to a Composition can propagate to live infrastructure immediately without an explicit apply gate - a sharp edge. The XRD/Composition abstraction layer was designed to give platform teams the ability to enforce organisational standards without exposing the complexity of underlying cloud APIs to developers - achieving the same goal as Terraform modules, but within a Kubernetes-native control plane that already manages RBAC, events, status conditions, and ownership references.

---

### ⚙️ How It Works (Mechanism)

```
Developer applies XR (PostgreSQLDatabase)
    │  kubectl apply -f database.yaml
    ▼
┌──────────────────────────────────────┐
│  Crossplane Composition Controller   │
│  XR → Composition template          │
│  creates Managed Resources:          │
│    RDSInstance (MR)                  │
│    DBSubnetGroup (MR)                │
│    SecurityGroup (MR)                │
└──────────┬───────────────────────────┘
           │ creates MR objects
           ▼
┌──────────────────────────────────────┐
│  Provider-AWS Controller             │
│  watches each MR                     │
│  observe: call AWS Describe API      │
│  diff: desired vs actual             │
│  act: call AWS Create/Update/Delete  │
└──────────┬───────────────────────────┘
           │ cloud API calls
           ▼
┌──────────────────────────────────────┐
│  AWS Cloud                           │
│  RDS Instance created                │
│  Status → Ready                      │
│  Connection secret → K8s Secret      │
└──────────────────────────────────────┘
```

**Key Crossplane objects:**

| Object | Role | Who creates it |
|--------|------|----------------|
| Provider | Installs CRDs + cloud controllers | Platform team |
| ProviderConfig | Cloud credentials + region | Platform team |
| Managed Resource (MR) | 1:1 cloud resource | Composition or direct |
| XRD | Defines custom API schema | Platform team |
| Composition | Maps XR → set of MRs | Platform team |
| Composite Resource (XR) | Instance of an XRD | Application team |
| Claim | Namespace-scoped XR reference | Application team |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Platform team defines Composition:
  XRD: PostgreSQLDatabase
  Maps to: RDSInstance + SubnetGroup + SecGroup
    │
    ▼
Developer creates Claim in namespace:
  kubectl apply -f postgres-claim.yaml ← YOU ARE HERE
    │
    ▼
Crossplane creates XR (cluster-scoped)
    │
    ▼
Composition controller creates 3 MRs
    │
    ▼
provider-aws reconciles each MR:
  RDSInstance: calls aws rds create-db-instance
  SubnetGroup: calls aws rds create-db-subnet-group
  SecGroup: calls aws ec2 create-security-group
    │
    ▼
AWS creates resources (~5-10 min for RDS)
    │
    ▼
MR status updated: Ready=True
XR status: Ready=True, connectionDetails synced
    │
    ▼
K8s Secret created in developer namespace:
  endpoint: mydb.xyz.us-east-1.rds.amazonaws.com
  password: <from AWS Secrets Manager>
    │
    ▼
Developer's app mounts Secret → connects to DB
```

**FAILURE PATH:**
```
MR: RDSInstance - provision fails
  AWS error: subnet group not in same VPC
    │
    ▼
MR status: Ready=False
  condition: "Error creating RDS instance"
    │
    ▼
XR status: Ready=False (propagated)
Claim status: Ready=False
    │
    ▼
kubectl describe postgresqlclaim my-db
  shows: Events → provision error + reason
    │
    ▼
Platform team fixes Composition (VPC reference)
    │
    ▼
Crossplane re-reconciles → creates RDS
```

**WHAT CHANGES AT SCALE:**
At scale, Composition versioning becomes critical - changing a Composition's template can trigger updates across hundreds of XR instances. Composition Revisions allow versioned Compositions with a migration path. The provider-aws controller generates significant Kubernetes API traffic at high MR counts; etcd performance becomes a concern above ~10,000 MRs. Multi-cluster Crossplane deployments use a dedicated management cluster to separate infrastructure control plane from application workloads.

---

### 💻 Code Example

**BAD - Terraform module requires separate workflow:**
```hcl
# BAD: separate toolchain, separate PR, separate state
# Developer must open ticket → platform team runs this
module "app_database" {
  source = "terraform-aws-modules/rds/aws"
  identifier = "my-service-db"
  engine     = "postgres"
  # ... 20+ parameters, separate repo, separate apply
}
```

**GOOD - Crossplane XRD + Composition (platform team):**
```yaml
# xrd.yaml - platform team defines the self-service API
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqldatabases.platform.example.com
spec:
  group: platform.example.com
  names:
    kind: XPostgreSQLDatabase
    plural: xpostgresqldatabases
  claimNames:
    kind: PostgreSQLDatabase
    plural: postgresqldatabases
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                parameters:
                  type: object
                  properties:
                    storageGB:
                      type: integer
                    instanceClass:
                      type: string
                      enum: ["db.t3.micro","db.t3.medium"]
```

**GOOD - Composition mapping XRD to Managed Resources:**
```yaml
# composition.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xpostgresqldatabases.platform.example.com
spec:
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: XPostgreSQLDatabase
  resources:
    - name: rds-instance
      base:
        apiVersion: rds.aws.upbound.io/v1beta1
        kind: Instance
        spec:
          forProvider:
            region: us-east-1
            engine: postgres
            engineVersion: "15.4"
            autoMinorVersionUpgrade: true
            skipFinalSnapshot: false
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.allocatedStorage
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.instanceClass
          toFieldPath: spec.forProvider.instanceClass
```

**GOOD - Developer creates a Claim (self-service):**
```yaml
# my-service-db.yaml - developer creates this
apiVersion: platform.example.com/v1alpha1
kind: PostgreSQLDatabase
metadata:
  name: my-service-db
  namespace: my-service
spec:
  parameters:
    storageGB: 20
    instanceClass: db.t3.micro
  writeConnectionSecretToRef:
    name: my-service-db-connection
```

---

### ⚖️ Comparison Table

| Feature | Crossplane | Terraform | AWS CDK | Pulumi |
|---------|------------|-----------|---------|--------|
| **Control plane** | Kubernetes (CRDs) | Terraform CLI + state | CloudFormation | State backend |
| **Desired-state model** | Continuous reconcile | Plan → apply | Stack deploy | Plan → apply |
| **Drift detection** | Automatic (controller) | Manual (`tf refresh`) | Drift detection | Manual |
| **GitOps native** | Yes (K8s manifests) | Via TFC/Atlantis | Via CDK Pipelines | Via CI |
| **Self-service API** | Yes (XRD/Composition) | Via modules | Via constructs | Via components |
| **Language** | YAML/CRDs | HCL | TypeScript/Python | TypeScript/Python |
| **K8s dependency** | Required | None | None | None |
| **CNCF graduated** | Yes | No (HashiCorp) | No (AWS) | No |
| **Complexity** | High | Medium | High | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Crossplane replaces Terraform" | They solve related but different problems. Crossplane excels at Kubernetes-native, GitOps self-service infrastructure. Terraform excels at complex multi-cloud orchestration and existing IaC portfolios. Many teams run both. |
| "Crossplane has no plan step - changes apply immediately" | Correct and intentional. Crossplane uses continuous reconciliation, not plan→apply. Governance is applied via Composition constraints and RBAC, not a pre-apply gate. This is a fundamental workflow difference from Terraform. |
| "Composition drift = automatic update of live resources" | Yes - when a Composition template is updated, Crossplane reconciles existing XR instances toward the new template. This can cause updates to live infrastructure without an explicit apply. Version and review Composition changes carefully. |
| "Crossplane only manages Kubernetes resources" | Crossplane manages cloud resources (AWS, GCP, Azure, etc.) via Providers. It extends Kubernetes to be a control plane for any infrastructure, not a tool for managing in-cluster K8s objects. |
| "You need one Crossplane per application cluster" | The recommended pattern is a dedicated management cluster running Crossplane that manages infrastructure for multiple application clusters. This separates infrastructure control plane concerns from application workload concerns. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Composition update causes unintended live infrastructure changes**
**Symptom:** After a platform team updates a Composition, dozens of existing RDS instances trigger modifications (e.g., parameter group change), some causing unexpected maintenance windows.
**Root Cause:** Composition was updated without a new Composition Revision; all existing XR instances reconcile toward the new template immediately.
**Diagnostic:**
```bash
# List Composition Revisions
kubectl get compositionrevisions \
  -l crossplane.io/composite-type=XPostgreSQLDatabase

# Check which revision each XR references
kubectl get xpostgresqldatabases \
  -o jsonpath='{range .items[*]}{.metadata.name}
{" "}{.spec.compositionRevisionRef.name}{"\n"}{end}'

# Check MR for pending changes
kubectl describe rdsinstance my-db-xyz | grep -A10 Status
```
**Fix:**
BAD - Revert the Composition and manually fix each instance.
GOOD - Use Composition Revisions with `compositionUpdatePolicy: Manual`. Existing XRs do not automatically adopt new revisions. Migrate XRs to new revision explicitly and test on one instance first.
**Prevention:** Always use Composition Revisions for any change that modifies live infrastructure. Treat Composition updates as infrastructure changes requiring testing and staged rollout.

**Failure Mode 2: Provider controller CrashLoopBackOff stops all resource reconciliation**
**Symptom:** All Managed Resources in a provider (e.g., all AWS resources) stop reconciling. New resources are not created; changes are not applied; drift is not corrected.
**Root Cause:** provider-aws controller pod is CrashLoopBackOff - often due to out-of-memory kill, IAM permission error, or provider version incompatibility after upgrade.
**Diagnostic:**
```bash
kubectl get pods -n crossplane-system
# Look for provider-aws pod in CrashLoopBackOff

kubectl logs -n crossplane-system \
  $(kubectl get pods -n crossplane-system \
  -l pkg.crossplane.io/revision=provider-aws-xyz \
  -o name) --previous

# Check for IAM errors or OOM kills
kubectl describe pod -n crossplane-system provider-aws-xyz
```
**Fix:**
BAD - Delete all Managed Resources and re-create.
GOOD - Fix the provider (increase memory limits, fix IAM policy, pin provider version); provider recovers and resumes reconciliation from where it left off - existing resources are not affected.
**Prevention:** Set resource limits on provider containers; pin provider versions in production (`provider-aws:v0.43.1`, not `latest`); monitor provider pod health with alerting.

**Failure Mode 3: XR Claim stuck in `Binding` state indefinitely**
**Symptom:** Developer creates a PostgreSQLDatabase Claim; it stays in `Synced=False, Ready=Unknown` for hours.
**Root Cause:** Composition references a Managed Resource type that is not registered (provider not installed or wrong version). The XR is created but the Composition cannot find the CRD to create the MR.
**Diagnostic:**
```bash
kubectl describe postgresqldatabase my-db -n my-service
# Look for events: "cannot get composed resource"

# Check if the MR CRD exists
kubectl get crds | grep rds.aws.upbound.io

# Check provider health
kubectl get providers
# Look for provider-aws: Installed=True, Healthy=True
```
**Fix:**
BAD - Delete and re-create the Claim.
GOOD - Install the missing provider package (`kubectl apply -f provider.yaml`); once the provider is healthy and CRDs are registered, the existing XR reconciles automatically without recreation.
**Prevention:** Validate that all CRDs referenced by Compositions are registered before promoting Compositions to production. Maintain a provider compatibility matrix (Composition version ↔ provider version).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Kubernetes - the control plane Crossplane extends with cloud infrastructure CRDs
- Infrastructure as Code - the paradigm Crossplane implements via the K8s reconciliation model
- GitOps - the delivery model that makes Crossplane infrastructure changes version-controlled

**Builds On This (learn these next):**
- ArgoCD - the GitOps engine often paired with Crossplane to sync XR manifests from Git
- Terraform Cloud / Enterprise - the alternative governed Terraform platform for IaC
- Composition Functions - Crossplane's programmable Composition model using OCI functions

**Alternatives / Comparisons:**
- Terraform - imperative plan→apply model; wider provider ecosystem; no Kubernetes dependency
- AWS CDK - infrastructure as TypeScript/Python generating CloudFormation; not GitOps-native
- Pulumi - imperative IaC in general-purpose languages; no Kubernetes control plane

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS     │ Kubernetes extension that manages   │
│                │ cloud infra as CRDs via GitOps       │
│ PROBLEM        │ Separate toolchains for K8s apps    │
│                │ vs cloud infrastructure              │
│ KEY INSIGHT    │ K8s reconcile loop = IaC engine     │
│ USE WHEN       │ K8s-native teams wanting self-service│
│ AVOID WHEN     │ No K8s, large existing Terraform    │
│                │ codebase, no Composition expertise   │
│ TRADE-OFF      │ Unified control plane vs Kubernetes │
│                │ dependency + Composition complexity  │
│ ONE-LINER      │ kubectl apply = cloud resource create│
│ NEXT EXPLORE   │ ArgoCD, Terraform Cloud, ComposeFns │
└─────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** Crossplane reuses the Kubernetes reconciliation loop for infrastructure management, which means there is no "plan" step. What class of infrastructure change is safe in a continuous-reconcile model - and what class of change (e.g., destructive schema migrations) is dangerous and requires an explicit gate that Crossplane does not natively provide?

2. **(Design Trade-off)** Crossplane Compositions create an abstraction layer that hides cloud API complexity from developers. What happens when a developer's requirements exceed what the Composition exposes - and how do you balance abstraction completeness against the risk of Composition proliferation?

3. **(Scale)** A management Kubernetes cluster runs Crossplane and manages 5,000 Managed Resources across 20 application clusters. The etcd in the management cluster begins to show high latency. What is the causal relationship between Managed Resource count and etcd load - and what architectural changes would you make to restore performance?
