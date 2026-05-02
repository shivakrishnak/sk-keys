---
layout: default
title: "Container Registry"
parent: "Containers"
nav_order: 829
permalink: /containers/container-registry/
number: "0829"
category: Containers
difficulty: ★★☆
depends_on: Docker, Docker Image, OCI Standard, Image Tag Strategy
used_by: Image Scanning, Image Tag Strategy, Docker BuildKit, Container Orchestration
related: Docker Image, Image Tag Strategy, Image Scanning, OCI Standard, Docker
tags:
  - containers
  - docker
  - devops
  - intermediate
  - architecture
---

# 829 — Container Registry

⚡ TL;DR — A container registry is the distribution hub for Docker images — push once, pull anywhere — enabling CI/CD pipelines, Kubernetes, and teams to share and deploy container images.

| #829 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Docker, Docker Image, OCI Standard, Image Tag Strategy | |
| **Used by:** | Image Scanning, Image Tag Strategy, Docker BuildKit, Container Orchestration | |
| **Related:** | Docker Image, Image Tag Strategy, Image Scanning, OCI Standard, Docker | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A development team builds a Docker image on one machine and needs to deploy it to 50 production servers. Without a registry, they have no way to distribute the image beyond their laptop. They could `docker save image.tar | ssh server cat > image.tar && docker load < image.tar` — but this is serial, manual, and completely impractical for 50 servers. And if the image needs to be available to a CI system, a staging environment, and a deployment pipeline, there is no shared location anyone can reliably pull from.

**THE BREAKING POINT:**
Build once, run anywhere requires a neutral distribution point — a "package repository" for container images, just as Maven Central or npm Registry serves software packages.

**THE INVENTION MOMENT:**
This is exactly why container registries were created — a versioned, accessible, HTTP-based storage service for OCI images that any authorised client (`docker pull`) can retrieve the same image from, regardless of where it was built.

---

### 📘 Textbook Definition

A **container registry** is a service that stores, versions, and distributes OCI-compliant container images using the OCI Distribution Specification (an HTTP API). Images are organised as `<registry>/<repository>/<name>:<tag>` (e.g., `docker.io/library/nginx:1.25`). A registry stores: image manifests (layer lists + config), image layers (compressed tar archives), and image tags (mutable references) and digests (immutable SHA256 identifiers). Public registries (Docker Hub, GitHub Container Registry) host community and vendor images. Private registries (AWS ECR, GCR, Azure ACR, self-hosted Harbor) host organisational images with access control.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A container registry is the app store for Docker images — publish once, install anywhere with `docker pull`.

**One analogy:**
> A container registry is like a library for blueprints. Engineers submit their blueprints (images) with a version number. Anyone with the right credentials can check out the exact blueprint they need. Multiple warehouses (build systems) can produce the same blueprint. Multiple factories (production hosts) can retrieve the same version simultaneously. The library keeps all versions so you can roll back to last week's blueprint if today's has a defect.

**One insight:**
Tags are mutable pointers to immutable content. `nginx:latest` can point to a different image tomorrow than it does today. `nginx@sha256:abc123` always refers to exactly one specific image and never changes. In production, always deploy by digest (immutable) — never by mutable `latest` tag. "Latest broke production" is the classic mistake fixed by digest-based deployment.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An image must be stored somewhere accessible to all systems that need to run it.
2. Images must be versioned so deployments are reproducible and rollbacks are possible.
3. Access control must determine which systems and people can push and pull which images.

**DERIVED DESIGN:**

A registry implements the OCI Distribution Specification API:
- `GET /v2/{name}/manifests/{ref}` — fetch manifest by tag or digest
- `PUT /v2/{name}/manifests/{tag}` — push image manifest (create/update tag)
- `GET /v2/{name}/blobs/{digest}` — fetch a layer by its SHA256
- `POST /v2/{name}/blobs/uploads/` — initiate layer upload

**Push flow:**
1. `docker push myapp:1.0` — Docker CLI checks which layers the registry already has (by SHA256).
2. Only layers the registry doesn't have are uploaded (reducing redundant transfers).
3. The image manifest (layer list + config) is uploaded last.
4. The tag `myapp:1.0` is atomically updated to point to the new manifest.

**Pull flow:**
1. `docker pull myapp:1.0` — Docker CLI fetches the manifest for tag `1.0`.
2. For each layer in the manifest: if the layer is not in the local layer store, download it.
3. Only missing layers are downloaded (layer deduplication by SHA256).

**THE TRADE-OFFS:**
**Gain:** Single source of truth for images; version history; layer deduplication (shared base layers stored once).
**Cost:** Registry is now a critical dependency for deploys — registry downtime = deployment downtime; large images with many tags consume expensive registry storage; without immutable tags, reproducibility is broken.

---

### 🧪 Thought Experiment

**SETUP:**
A Kubernetes deployment uses `image: myapp:latest`. A new version is pushed and `latest` is updated.

**WHAT HAPPENS WITH MUTABLE TAG `latest`:**
Kubernetes is configured to `imagePullPolicy: Always`. On a rolling deploy, some nodes pull the new `latest` during the rollout while others pull from cache. Half the pods run the new version, half run the old version — simultaneously. Rollback is also challenging because `latest` no longer points to the previous version. The team cannot reproduce "exactly what was running yesterday."

**WHAT HAPPENS WITH DIGEST-BASED DEPLOY:**
Kubernetes manifest specifies `image: myapp@sha256:3f8a...`. Every node pulls exactly this immutable layer set. The digest can never be reassigned. Rolling back means updating the manifest to the previous commit's digest — deterministic and auditable.

**THE INSIGHT:**
A container image digest is a cryptographic guarantee of identity. A tag is a convenience alias that can be reassigned. Production deployments should use digests; tags are for human readability. "Deploy what we tested" requires immutability at the image reference level.

---

### 🧠 Mental Model / Analogy

> A container registry is like a version control system for container images — not code, but built artifacts. Just as Git stores every commit of code with its hash, a registry stores every pushed image with its SHA256 digest. Tags in a registry are like Git branch names — human-readable aliases that can be moved. Digests are like Git commit hashes — permanently anchored, immutable, content-addressed.

**Mapping:**
- "Git repository" → registry repository (`myorg/myapp`)
- "Git commit hash" → image manifest digest (`sha256:3f8a...`)
- "Git branch name" → image tag (`latest`, `v1.0.2`)
- "git push origin main" → `docker push myapp:1.0`
- "git clone" → `docker pull myapp:1.0`

**Where this analogy breaks down:** Git stores code diffs efficiently; a registry stores layers which are full filesystem snapshots (not diffs of diffs). Git history is append-only; registry tags can be deleted or mutated (unless immutable tag policies are applied).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A container registry is like an app store for Docker images. Developers upload their images to the registry. Servers, CI systems, and Kubernetes clusters download the images from the registry. The registry keeps every version so you can always go back to an older one.

**Level 2 — How to use it (junior developer):**
Build and tag an image: `docker build -t registry.example.com/myteam/myapp:1.0 .`. Login to registry: `docker login registry.example.com`. Push: `docker push registry.example.com/myteam/myapp:1.0`. On another machine: `docker pull registry.example.com/myteam/myapp:1.0`. In Kubernetes `spec.containers.image`: use the registry path instead of Docker Hub.

**Level 3 — How it works (mid-level engineer):**
A registry stores data in two layers: metadata (manifest, tag → digest mapping, stored in a small DB) and blob storage (layer archives, stored in block storage or object storage like S3). Modern registries (ECR, GCR, Harbor) store blobs in cloud object storage. Layer deduplication: all repositories in a registry share the same blob storage — `nginx:1.25` layers used in `myapp:1.0` are stored once even if both images reside in the same registry. Authentication uses Docker Hub's token service or a registry-specific OAuth2 flow — the token is embedded in subsequent requests as a Bearer token. Many registries support image signing (Cosign, Notary) for supply chain security, and geo-replication for multi-region pull performance.

**Level 4 — Why it was designed this way (senior/staff):**
The OCI Distribution Specification (originally Docker Registry HTTP API v2) was designed as a content-addressed, RESTful blob store. The content-addressing design (SHA256 for both blobs and manifests) is what enables secure pull-through caches and geographic mirrors — a cache can verify the integrity of every layer it serves without trusting the source registry. The adoption of the OCI spec by all major registries (ECR, GCR, ACR, Harbor, GitHub Container Registry) created a level of interoperability that enables tools like Cosign (image signing), ORAS (OCI artifact push/pull), and Referrers API (attaching SBOMs and signatures to images) to work across registries.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  CONTAINER REGISTRY ARCHITECTURE                         │
│                                                          │
│  PUSH (docker push myapp:1.0)                           │
│  Client → check which layers registry has (HEAD /blobs) │
│  → upload only missing layers (PUT /blobs)              │
│  → upload manifest (PUT /manifests/1.0)                 │
│  → tag 1.0 → digest sha256:abc... updated atomically   │
│                                                          │
│  PULL (docker pull myapp:1.0)                           │
│  Client → GET /manifests/1.0 → receive manifest+digest │
│  → for each layer: check local cache (by SHA256)        │
│  → download only layers not in cache (GET /blobs/sha256)│
│  → verify each layer SHA256 (content integrity)         │
│  → assemble OverlayFS stack                             │
│                                                          │
│  STORAGE STRUCTURE                                       │
│  Registry:                                              │
│  ├── Repositories                                        │
│  │    └── myorg/myapp                                    │
│  │         ├── Tags: {1.0 → sha256:abc, latest → sha256:abc}│
│  │         └── Manifests: {sha256:abc: [{layer_sha}, ...]│
│  └── Blob Store (shared across repos)                   │
│       ├── sha256:layer1 (45 MB, nginx base)             │
│       ├── sha256:layer2 (12 MB, app deps)               │
│       └── sha256:layer3 (2 MB, app code)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
CI: docker build → docker push → [REGISTRY ← YOU ARE HERE]
→ tag points to new manifest digest
→ CD: Kubernetes pull → each node downloads missing layers
→ Pods start with new image
```

**FAILURE PATH:**
```
Registry unavailable during deploy → docker pull fails
→ Kubernetes pods cannot start on new nodes
→ existing running pods unaffected (image already on node)
→ fix: registry comes back online → retry pull
→ mitigation: image pull-through cache prevents single point of failure
```

**WHAT CHANGES AT SCALE:**
At 1,000 nodes deploying a 300 MB image simultaneously: 300 GB of bandwidth required. Solutions: (1) pull-through registry cache per region/zone (nodes pull from cache, not source registry); (2) image pre-pulling DaemonSet (pull before deploy event); (3) layer deduplication (update only changed layers, not full image); (4) P2P image distribution (Kraken, Dragonfly) — nodes share layers with each other.

---

### 💻 Code Example

Example 1 — Registry login and push (AWS ECR):
```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and tag for ECR
docker build -t 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0 .

# Push (only missing layers uploaded)
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0

# Get the immutable digest for production deployment
docker inspect --format='{{index .RepoDigests 0}}' \
  123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
# → 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp@sha256:3f8a...
```

Example 2 — Pull by digest (immutable, production-safe):
```bash
# Always tag reference (mutable - avoid in production)
docker pull myapp:latest  # could change between pulls

# Digest reference (immutable - use in production)
docker pull myapp@sha256:3f8a12bc4d567ef890abc1234567890abcdef12345678

# Kubernetes deployment with digest
# spec.containers[0].image:
# "myapp@sha256:3f8a12bc4d567ef890abc..."
```

Example 3 — Harbor self-hosted registry policies:
```bash
# Harbor CLI: create immutable tag policy (no overwrites)
curl -X POST https://harbor.internal/api/v2.0/projects/myproject/immutabletagrules \
     -H "Content-Type: application/json" \
     -d '{
       "disabled": false,
       "match": {"tags": {"patterns": ["release-*"]}},
       "scope": "currentProject"
     }'
# All tags matching "release-*" cannot be overwritten
```

---

### ⚖️ Comparison Table

| Registry | Hosting | Access Control | Image Signing | Scanning | Best For |
|---|---|---|---|---|---|
| **Docker Hub** | Public cloud | Free + paid tiers | Yes (Notary) | Yes | Public/community images |
| AWS ECR | AWS managed | IAM-based | Yes (Cosign) | Yes (Inspector) | AWS-native workloads |
| Google GCR/AR | GCP managed | IAM-based | Yes (Cosign) | Yes | GCP-native workloads |
| Azure ACR | Azure managed | RBAC | Yes (Notary) | Yes | Azure-native workloads |
| GitHub GHCR | GitHub managed | GitHub RBAC | Yes (Cosign) | Limited | GitHub Actions workflows |
| Harbor | Self-hosted | RBAC + LDAP | Yes | Yes (Trivy) | On-prem / private cloud |

**How to choose:** Use the managed registry that matches your cloud provider (ECR for AWS, GCR for GCP, ACR for Azure) — tight IAM integration eliminates credential management. Use Harbor for on-premises or regulated environments. Use Docker Hub only for public community images.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Deleting a tag deletes the image | Deleting a tag removes the tag reference but the manifest and layers may remain (especially if referenced by other tags or digest). Use registry garbage collection to reclaim storage. |
| `latest` means the newest image | `latest` is just a tag that must be explicitly set to the newest image at push time. If not pushed with `latest`, it won't update automatically. |
| Image layers in different repositories are stored separately | In most registries, all repositories in the same registry share the same blob store — the same base layer is stored once regardless of how many repositories reference it. |
| Public registries have no rate limits | Docker Hub has aggressive pull rate limits (100 pulls/6h for anonymous, 200/6h for free accounts). Production systems must authenticate or use a pull-through cache. |
| Image size in registry = image size on disk | Registry stores compressed layers. `docker images` shows uncompressed size. Actual network transfer = compressed layer size (often 40–70% of disk size). |

---

### 🚨 Failure Modes & Diagnosis

**Docker Hub Rate Limit Hit**

**Symptom:** CI builds fail with `toomanyrequests: Too Many Requests. Please see https://docs.docker.com/docker-hub/download-rate-limit/`

**Root Cause:** Anonymous or free-tier Docker Hub pulls exceeded rate limits. Common in large CI systems pulling `node:20` base images repeatedly.

**Diagnostic Command / Tool:**
```bash
# Check remaining rate limit (Docker Hub API)
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | jq -r .token)
curl -I -H "Authorization: Bearer $TOKEN" \
  https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest 2>&1 \
  | grep -i "ratelimit"
# RateLimit-Remaining header shows remaining pulls
```

**Fix:** (1) Authenticate Docker Hub pulls in CI; (2) deploy a pull-through cache (Docker Hub mirror) to proxy and cache pulls.

**Prevention:** Configure CI to always authenticate to Docker Hub. Use ECR/GCR as primary image source for base images (re-tag and push your own copies).

---

**Registry Down During Deploy**

**Symptom:** New Kubernetes pods fail to start with `ImagePullBackOff`. 

**Root Cause:** Registry is unreachable (network issue, maintenance, or outage).

**Diagnostic Command / Tool:**
```bash
kubectlt describe pod <pod-name>
# Shows: Failed to pull image: ... registry <HOST>: ... connection refused

# Check registry connectivity from node
kubectl run test --image=busybox -- nslookup registry.example.com
```

**Fix:** Enable `imagePullPolicy: IfNotPresent` — if the image is already on the node, the registry is not consulted. For new nodes, registry access is required.

**Prevention:** Deploy a pull-through cache per availability zone. Configure `imagePullPolicy: IfNotPresent` for stable image tags. Cache images on node before scheduling.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker Image` — what the registry stores and distributes
- `OCI Standard` — the specification that registries implement

**Builds On This (learn these next):**
- `Image Tag Strategy` — how to manage tags and digests for safe deployments
- `Image Scanning` — security scanning of images stored in registries

**Alternatives / Comparisons:**
- `Harbor` — self-hosted open-source registry with scanning, signing, and RBAC
- `OCI Artifacts` — extends registries to store non-image artifacts (Helm charts, SBOMs, signatures)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ HTTP-based image distribution service:   │
│              │ push once, pull anywhere by any system   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No way to distribute images from one     │
│ SOLVES       │ build to many deployment targets         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Tags are mutable, digests are immutable. │
│              │ Production must deploy by digest.        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every project needs a registry  │
│              │ from the first container deployment      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid Docker Hub rate limits in CI;      │
│              │ use managed cloud registry instead       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Central image distribution vs registry   │
│              │ becomes a critical deployment dependency │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "npm Registry for containers — version-  │
│              │  controlled, shared, pull anywhere"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Image Tag Strategy → Image Scanning →    │
│              │ OCI Standard                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your organisation uses AWS ECR in `us-east-1` for all container images. You are expanding to deploy workloads in `eu-west-1`. A critical deployment event causes all 200 Kubernetes nodes in `eu-west-1` to simultaneously pull a 400 MB image from `us-east-1`. Calculate the cross-region bandwidth cost and latency impact. Design the complete image distribution architecture that eliminates this cross-region pull bottleneck — including the technical mechanism and operational procedures for keeping the regional registry in sync.

**Q2.** An engineer discovers that your production deployments reference images by tag (`image: myapp:release-1.3`) not by digest. Three weeks ago, the `release-1.3` tag was retag'd to a new image (a silent CVE patch). All new deployments since then used the patched image, but you cannot be 100% certain which of your currently running pods are running the old vs new image. Design the audit and remediation procedure, and then change the deployment process to prevent this ambiguity permanently.

