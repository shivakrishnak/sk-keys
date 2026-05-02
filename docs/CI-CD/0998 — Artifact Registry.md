---
layout: default
title: "Artifact Registry"
parent: "CI/CD"
nav_order: 998
permalink: /ci-cd/artifact-registry/
number: "0998"
category: CI/CD
difficulty: ★★☆
depends_on: Artifact, Build Stage, Docker Image
used_by: Continuous Delivery, Deployment Pipeline, Container Scanning
related: Artifact, Container Registry, SBOM
tags:
  - cicd
  - devops
  - containers
  - intermediate
  - build
---

# 0998 — Artifact Registry

⚡ TL;DR — An artifact registry is the central repository that stores, versions, and secures all pipeline build outputs — enabling any environment to pull the exact artifact that was tested, without rebuilding.

| #0998 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Artifact, Build Stage, Docker Image | |
| **Used by:** | Continuous Delivery, Deployment Pipeline, Container Scanning | |
| **Related:** | Artifact, Container Registry, SBOM | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team builds a Docker image on the CI server and deploys it directly to production by SSH-ing to each server and running `docker load`. When the production server needs to scale from 3 nodes to 20 nodes, 17 new servers must individually receive the image via SCP. When a security vulnerability is found in the base image, there's no central record of which services are using it. When an incident requires rolling back to the previous version, no one knows where that old image lives. Each developer's laptop may have different versions cached.

**THE BREAKING POINT:**
Without a central artifact store, there's no single source of truth for what's built, where it is, and what's in it. Audit, rollback, scanning, and distribution all break simultaneously at scale.

**THE INVENTION MOMENT:**
This is exactly why artifact registries exist: a central, authenticated, versioned store where pipelines push every built artifact and every deployment pulls from — creating a single source of truth for all deployable software.

---

### 📘 Textbook Definition

An **artifact registry** is a managed repository service that stores, versions, and distributes build artifacts produced by CI/CD pipelines. It supports multiple artifact formats — Docker images (OCI), Maven JARs, npm packages, Python wheels, Helm charts. Each artifact is identified by coordinates (name + version/tag) and a content digest (SHA256). The registry enforces access control (who can push/pull), supports vulnerability scanning of stored artifacts, and provides retention policies to manage storage costs. Common implementations: JFrog Artifactory, Sonatype Nexus, AWS ECR, Google Artifact Registry, GitHub Packages.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An artifact registry is the warehouse between "code is built" and "code is deployed."

**One analogy:**
> An artifact registry is like a pharmaceutical distribution warehouse. Factories (CI pipelines) manufacture products (artifacts) and ship them to the central warehouse. Hospitals and pharmacies (deployment environments) order directly from the warehouse — they never buy from the factory floor. The warehouse records every batch received, maintains cold chain (security), and can recall a batch instantly by lot number (version).

**One insight:**
The registry solves two distinct problems: **distribution** (every server gets the same artifact efficiently) and **governance** (who built it, when, what's in it, is it vulnerable). Without a registry, these can't be solved at scale.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Push once, pull many times — the registry is the single distribution point.
2. Artifacts are immutable — existing tags may be overridden but the original digest persists.
3. Access control separates producers (CI pipeline) from consumers (deployments).

**DERIVED DESIGN:**
The registry must be highly available — if it's down, deployments fail. It must be geographically replicated for multi-region deployments (pulling a 500 MB image from a US registry in a Tokyo data centre adds 2+ minutes per deployment). It needs a pull-through cache for public registries (Docker Hub) to avoid rate limiting and internet dependency.

Tag vs digest matters: a tag like `myapp:1.2.3` is a pointer that can be re-pointed to a new digest. A digest `myapp@sha256:abc123` is permanently bound to specific content. Production deployments should reference digests for absolute immutability.

**THE TRADE-OFFS:**
**Gain:** Centralised distribution, access control, vulnerability scanning, audit trail, efficient layer deduplication.
**Cost:** Operational overhead for self-hosted registries (Nexus, Artifactory). Storage costs for cloud registries (ECR, GCR). Single point of failure if not made highly available.

---

### 🧪 Thought Experiment

**SETUP:**
A team deploys 8 microservices to Kubernetes across 20 nodes. Each service image is 200 MB. No artifact registry — images are `docker save`-d and distributed manually.

**WHAT HAPPENS WITHOUT AN ARTIFACT REGISTRY:**
A new node joins the Kubernetes cluster. It needs all 8 service images: 8 × 200 MB = 1.6 GB to transfer to that node manually. When Service A is updated, 8 out of 20 node operators must be notified to update their cached image. When a critical CVE is found, someone must manually check each node for the affected image. Rollback requires finding the backup file from the previous deployment script run.

**WHAT HAPPENS WITH AN ARTIFACT REGISTRY:**
A new node joins. Kubernetes pulls the needed images from the registry on first pod placement — automatically. Docker's layer cache means only the changed layers (e.g., 15 MB) are pulled for each update, not the full 200 MB. `trivy` continuously scans images in the registry and alerts on new CVEs. Rollback: `kubectl set image deployment/service-a myapp=myorg/service-a:sha-9f2a1bc` — the registry serves the exact old image.

**THE INSIGHT:**
The registry isn't just storage — it's the central coordination point for all deployment-related operations. Vulnerability management, rollback, audit, and efficient distribution all depend on it.

---

### 🧠 Mental Model / Analogy

> An artifact registry is like a library with a strict cataloguing system. Books (artifacts) are dropped off by the printing press (CI pipeline) with an accession number (version tag). Borrowers (deployment environments) check out books by accession number — they always get exactly the right edition. The librarian (registry access control) decides who can borrow, who can add new books, and when old editions are archived.

- "Printing press" → CI pipeline build stage
- "Books" → Docker images or JAR artifacts
- "Accession number" → image tag or version
- "Library catalogue" → registry index (list of tags and digests)
- "Librarian access control" → registry IAM policies (who can push/pull)
- "Archiving old editions" → retention policies deleting old tags

Where this analogy breaks down: libraries hold unique physical copies; a registry holds one copy per layer, shared across all images that use it. Two images sharing the same JRE layer don't double the storage.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An artifact registry is a special kind of storage service specifically designed for software packages. After the CI system builds your software, it uploads it here. When you want to deploy, your servers download it from here. Everyone always gets the same version from the same place.

**Level 2 — How to use it (junior developer):**
`docker push myorg/myapp:sha-abc123` uploads your image to a Docker registry. `docker pull myorg/myapp:sha-abc123` downloads it. Kubernetes pulls images automatically using the `image:` field in the deployment spec. For Maven JARs, configure the `distributionManagement` in `pom.xml` to point to your Nexus/Artifactory URL. Use `mvn deploy` in CI to publish. Use the registry's UI to view all versions, scan results, and download counts.

**Level 3 — How it works (mid-level engineer):**
Docker registries implement the OCI Distribution Specification. Images are stored as a manifest (JSON describing layers and config) and content-addressed blobs (individual layer tar archives stored by SHA256 hash). When you `docker push`, the client first checks which layers the server already has (via a HEAD request per layer) — only missing layers are uploaded. This deduplication means a 200 MB image with a 180 MB shared base layer uploads only 20 MB if the base already exists in the registry.

**Level 4 — Why it was designed this way (senior/staff):**
The OCI Distribution Spec (derived from Docker Registry v2 API) was standardised to decouple registries from a single vendor. Any OCI-compliant client can push to any compliant registry. Content-addressable storage (layers stored by their SHA256) was chosen because it provides free deduplication — identical content (any two images sharing a base) wastes no storage. Immutable references (`@sha256:...`) provide reproducibility guarantees that are essential for supply chain security (SLSA framework). The shift to software supply chain security (SLSA, SBOM) has added signing (Sigstore, cosign), attestations, and SBOM storage as first-class registry features.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────┐
│         ARTIFACT REGISTRY OPERATIONS         │
├───────────────────────────────────────────────┤
│  PUSH (CI pipeline → registry)               │
│  docker push myorg/myapp:sha-abc123          │
│    1. Client hashes each layer               │
│    2. HEAD /v2/myorg/myapp/blobs/sha256:xxx  │
│       → 404: upload this layer               │
│       → 200: layer exists, skip              │
│    3. PUT manifest + config                  │
│    4. Registry stores: manifest, layers      │
│    5. Tag sha-abc123 → manifest digest       │
├───────────────────────────────────────────────┤
│  PULL (deployment → registry)                │
│  docker pull myorg/myapp:sha-abc123          │
│    1. GET /v2/myorg/myapp/manifests/sha-abc  │
│    2. Parse manifest: layer list             │
│    3. GET each layer (if not in local cache) │
│    4. Reconstruct image filesystem           │
├───────────────────────────────────────────────┤
│  LAYER DEDUPLICATION                         │
│  Image A: [OS=180MB][JRE=60MB][App=5MB]     │
│  Image B: [OS=180MB][JRE=60MB][App=3MB]     │
│  Storage: OS+JRE stored once (240MB)         │
│           App A (5MB) + App B (3MB) = 8MB   │
│  Total: 248MB vs naive 486MB                 │
└───────────────────────────────────────────────┘
```

**Vulnerability scanning integration:** AWS ECR Basic Scanning uses Clair to scan images on push. ECR Enhanced Scanning uses Amazon Inspector with continuous rescanning — if a new CVE is published for `libssl`, all images containing it are re-flagged without a new push. JFrog Xray provides similar functionality with integration into Artifactory.

**Access control patterns:**
```
CI pipeline IAM role  → push to myorg/*
Dev environment role  → pull from myorg/dev-*
Prod environment role → pull from myorg/* (read-only)
Security scanner role → pull + scan all tags
```

**Geographic replication:** AWS ECR replication, GCR multi-region, and JFrog Artifactory geo-replication ensure images are cached in each region. A Tokyo Kubernetes cluster pulls from a Tokyo cache, not from US-East — cutting startup latency from 90 seconds to 8 seconds for new nodes.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Build stage: docker build → image ready
  → docker push myorg/myapp:sha-abc123 [← YOU ARE HERE]
  → Registry: stores layers, creates manifest
  → Vulnerability scan: triggered on push
  → Scan result: no critical CVEs
  → CD pipeline: deploy to staging
  → Kubernetes: docker pull myorg/myapp:sha-abc123
  → Pod starts with verified image
  → Production deploy: same tag, same image
```

**FAILURE PATH:**
```
Vulnerability scan: CRITICAL CVE found in libssl
  → Registry policy: block pull until patched
    (or alert without blocking, team's choice)
  → Developer: rebuild with updated base image
  → New image sha-def456 pushed with clean scan
  → sha-abc123 retained but flagged
```

**WHAT CHANGES AT SCALE:**
At 200+ microservices each with daily deploys, registry bandwidth becomes a cost. Layer deduplication and regional mirrors are critical. Retention policies must run automatically — without cleanup, 1 year of 200 services × daily images ≈ 73,000 image tags. Scan results must be ingested into a central security dashboard (Snyk, Aqua) — reviewing individual registry scan results per service is not scalable.

---

### 💻 Code Example

**Example 1 — Push to AWS ECR in GitHub Actions:**
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/ci-push
    aws-region: us-east-1

- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push to ECR
  env:
    REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    IMAGE_TAG: ${{ github.sha }}
  run: |
    docker build \
      -t $REGISTRY/myapp:$IMAGE_TAG \
      -t $REGISTRY/myapp:latest \
      .
    docker push $REGISTRY/myapp:$IMAGE_TAG
    # push 'latest' as convenience alias only
    docker push $REGISTRY/myapp:latest
    echo "IMAGE=$REGISTRY/myapp:$IMAGE_TAG" \
      >> $GITHUB_OUTPUT
```

**Example 2 — Kubernetes pulls from private registry:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      # Secret with registry credentials
      imagePullSecrets:
        - name: ecr-credentials
      containers:
        - name: myapp
          # BAD: mutable tag - don't know what you deployed
          # image: myorg/myapp:latest

          # GOOD: immutable commit SHA tag
          image: 123456789.dkr.ecr.us-east-1.amazonaws.com\
/myapp:abc123def456
          imagePullPolicy: Always
```

**Example 3 — Inspect and scan image in registry:**
```bash
# List all tags for an image
aws ecr list-images \
  --repository-name myapp \
  --query 'imageIds[*].imageTag' \
  --output table

# Get image digest (use in deployment for immutability)
aws ecr describe-images \
  --repository-name myapp \
  --image-ids imageTag=abc123def456 \
  --query 'imageDetails[0].imageDigest'

# Scan locally before push
trivy image --severity HIGH,CRITICAL \
  123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:abc123

# Verify image signature (if using cosign)
cosign verify \
  --key cosign.pub \
  123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:abc123
```

---

### ⚖️ Comparison Table

| Registry | Hosting | Formats | Scanning | Best For |
|---|---|---|---|---|
| **AWS ECR** | Cloud (AWS) | Docker, OCI | Basic + Enhanced (Inspector) | AWS-native teams |
| Google Artifact Registry | Cloud (GCP) | Docker, Maven, npm, Python | Container Analysis | GCP-native teams |
| JFrog Artifactory | Self-hosted / Cloud | All formats | JFrog Xray | Enterprise, multi-format |
| Sonatype Nexus | Self-hosted | All formats | Nexus IQ | Java-heavy, air-gapped |
| GitHub Packages | Cloud (GitHub) | Docker, Maven, npm | Basic | GitHub-native workflows |
| Docker Hub | Cloud (public) | Docker | Snyk (paid) | Public OSS images |

How to choose: Use your cloud provider's managed registry (ECR, GAR) for simplicity and tight IAM integration. Use JFrog Artifactory or Nexus if you need multi-format support (Maven + Docker + npm in one place) or air-gapped operation.

---

### 🔁 Flow / Lifecycle

```
┌───────────────────────────────────────────────┐
│         IMAGE LIFECYCLE IN REGISTRY           │
├───────────────────────────────────────────────┤
│  ACTIVE TAG: sha-abc123 (in use in prod)      │
│         ↓ (new version deployed)              │
│  SUPERSEDED: sha-abc123 retained for rollback │
│         ↓ (30 days pass)                      │
│  RETENTION POLICY: keep last 10 tags only     │
│         ↓ (tag removed if > 10)               │
│  ARCHIVED: digest retained, tag removed       │
│         ↓ (90 days pass)                      │
│  PURGED: digest deleted, storage reclaimed    │
│                                               │
│  EXCEPTION: release tags (v1.2.3) never purge│
└───────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Deleting an image tag deletes the image | Deleting a tag removes the human-readable pointer; the underlying digest (content) may still exist if referenced by another tag or manifest list |
| Public Docker Hub images are always available | Docker Hub enforces rate limits (100 pulls/6h for anonymous, 200 for authenticated free). Pull-through cache or your own registry copy is essential for reliable CI |
| The registry is just a storage bucket | A registry implements the OCI Distribution API — authentication, manifest handling, layer deduplication, and scanning integration. It's not a generic object store |
| Registry downtime only affects new deployments | If `imagePullPolicy: Always` is set and the registry is down, existing pods may fail to restart after node failure. Use `imagePullPolicy: IfNotPresent` for prod stability |

---

### 🚨 Failure Modes & Diagnosis

**1. Registry Rate Limiting Breaks CI**

**Symptom:** CI pipelines start failing with `toomanyrequests: You have reached your pull rate limit` when pulling base images from Docker Hub.

**Root Cause:** Docker Hub's anonymous pull limit (100/6h per IP). CI runners share an IP — 100 jobs sharing one IP means 1 pull each before rate limiting kicks in.

**Diagnostic:**
```bash
# Check current rate limit status
TOKEN=$(curl -s \
  "https://auth.docker.io/token?service=registry.docker.io\
&scope=repository:ratelimitpreview/test:pull" \
  | jq -r .token)
curl -s --head \
  -H "Authorization: Bearer $TOKEN" \
  https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest \
  | grep RateLimit
```

**Fix:** Mirror base images to your private registry. Use Docker Hub Pro credentials in CI. Configure ECR/GAR pull-through cache.

**Prevention:** Never pull from Docker Hub directly in CI. Always use a pull-through cache or mirrored base image.

---

**2. Registry Unavailable — Deployments Blocked**

**Symptom:** Kubernetes pods fail to start: `ImagePullBackOff`. Nodes can't pull the image. All new deployments and pod restarts are blocked.

**Root Cause:** Single-region registry with no replication. Or registry credentials expired (ECR tokens expire every 12 hours).

**Diagnostic:**
```bash
# Check pod events
kubectl describe pod <pod-name> | grep -A5 "Events:"
# Manually test pull on the node
docker pull myregistry/myapp:sha-abc123
# Check ECR credential expiry
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS \
  --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
```

**Fix (immediate):** Refresh registry credentials. For ECR: update the `ecr-credentials` Kubernetes secret with a fresh token.

**Prevention:** Use IAM Roles for Service Accounts (IRSA) in EKS — eliminates token management. Enable registry replication across regions.

---

**3. Unbounded Storage Growth**

**Symptom:** Registry bill doubles every month. Disk usage reaches terabytes. Old builds from 2 years ago are still stored.

**Root Cause:** No retention policy configured. Every CI build pushes a new tag that is never cleaned up.

**Diagnostic:**
```bash
# AWS ECR: list repositories by size
aws ecr describe-repositories \
  --query 'repositories[*].{Name:repositoryName}' | \
  jq --arg REGISTRY "123456789.dkr.ecr.us-east-1.amazonaws.com" \
  '.[].Name' -r | while read repo; do
    aws ecr describe-images --repository-name "$repo" \
      --query 'sum(imageDetails[*].imageSizeInBytes)' --output text
  done
```

**Fix:** Configure ECR lifecycle policy to keep only the last N images:
```json
{
  "rules": [{
    "rulePriority": 1,
    "description": "Keep last 30 images",
    "selection": {
      "tagStatus": "any",
      "countType": "imageCountMoreThan",
      "countNumber": 30
    },
    "action": { "type": "expire" }
  }]
}
```

**Prevention:** Configure lifecycle policies at registry creation time, not after costs escalate.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Artifact` — the build output that is stored in the registry; understanding artifacts is required before understanding the registry that stores them
- `Build Stage` — the pipeline step that produces artifacts and pushes them to the registry
- `Docker Image` — the primary artifact format stored in modern container registries

**Builds On This (learn these next):**
- `Container Scanning` — security practice of scanning artifacts stored in the registry for known vulnerabilities
- `SBOM (Software Bill of Materials)` — the artifact metadata that documents every component in a stored image
- `Continuous Delivery` — uses the artifact registry as its artifact distribution layer between environments

**Alternatives / Comparisons:**
- `Container Registry` — a registry that specifically stores Docker/OCI images (a subset of artifact registry capabilities)
- `Nexus / Artifactory` — self-hosted artifact registry solutions vs cloud-hosted options (ECR, GAR)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Central store for all versioned pipeline  │
│              │ artifacts: Docker images, JARs, packages  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No single source of truth for built       │
│ SOLVES       │ artifacts; inconsistent deployments       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Tag is a pointer (mutable), digest is     │
│              │ the artifact (immutable) — use digest     │
│              │ for production deployments                │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — any team using CI/CD needs a     │
│              │ registry for artifact distribution        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — avoid pulling from public Docker Hub│
│              │ in CI; use a private registry or cache    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reliability + security + deduplication    │
│              │ vs operational overhead + storage costs   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The warehouse between build and deploy   │
│              │  — single source of truth for all         │
│              │  deployable software"                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Container Scanning → SBOM                 │
│              │ → Secret Scanning                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Kubernetes cluster in us-east-1 is healthy but a new region (ap-southeast-1) is being launched. The artifact registry is only in us-east-1. New pods in Asia Pacific take 4 minutes to start because they're pulling 400 MB images across the Pacific. Describe the complete solution — registry replication architecture, Kubernetes configuration changes, and cache warming strategy — that would bring pod startup time under 30 seconds in the new region.

**Q2.** A security researcher reports a critical CVE in `libssl` affecting your `eclipse-temurin:21-jre-alpine` base image. You have 47 microservices, each with Docker images in your registry. You need to identify every affected image and deploy patched versions within 4 hours. Describe the exact process: how you identify affected images, how you rebuild and verify them, and how you deploy 47 services safely in 4 hours without cascading failures.

