---
layout: default
title: "Container Registry"
parent: "Containers"
nav_order: 829
permalink: /containers/container-registry/
number: "829"
category: Containers
difficulty: â˜…â˜…â˜†
depends_on: "Docker Image, Docker Layer"
used_by: "Kubernetes, CI-CD pipelines, Multi-Stage Build"
tags: #containers, #docker, #registry, #ecr, #gcr, #image-distribution
---

# 829 â€” Container Registry

`#containers` `#docker` `#registry` `#ecr` `#gcr` `#image-distribution`

âš¡ TL;DR â€” A **container registry** is a storage and distribution system for Docker images. You `docker push` images to it from CI; your Kubernetes cluster (or any host) `docker pull` images from it at deploy time. Docker Hub is the public default. Enterprise deployments use private registries: AWS ECR, Google Artifact Registry, Azure ACR, or self-hosted Harbor. Tags (`:v1.2.3`, `:latest`, `:main-abc123`) identify image versions stored in the registry.

| #829            | Category: Containers                           | Difficulty: â˜…â˜…â˜† |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | Docker Image, Docker Layer                     |                 |
| **Used by:**    | Kubernetes, CI-CD pipelines, Multi-Stage Build |                 |

---

### ðŸ“˜ Textbook Definition

**Container registry**: a server-side application that stores and distributes Docker (OCI) container images. Architecture: a registry contains one or more **repositories** (collections of related images, e.g., `myorg/api`); each repository contains **tags** (named references to image manifests, e.g., `v1.2.3`); each image manifest references **layers** (content-addressable blobs identified by SHA256). The OCI Distribution Specification defines the standard HTTP API for push/pull. Clients: `docker push registry/repo:tag`, `docker pull registry/repo:tag`. Key operations: (1) push: upload layers that the registry doesn't already have (deduplication by SHA256) + push manifest; (2) pull: download manifest â†’ identify layer SHAs â†’ download only layers not in local cache. Registry types: **public** (Docker Hub: `docker.io/library/nginx`), **private** (organization-scoped), **hosted SaaS** (ECR, GCR, ACR, GitHub Container Registry), **self-hosted** (Harbor, Nexus). **Image digest**: immutable SHA256 of the manifest â€” `nginx@sha256:abc123`; more reliable than tags (`:latest` is mutable). Image scanning: most enterprise registries scan images for CVEs on push and block deployment of vulnerable images.

---

### ðŸŸ¢ Simple Definition (Easy)

A registry is like npm for Docker images. You publish your image with `docker push myregistry.io/myapp:v1.0`. Your servers pull it with `docker pull myregistry.io/myapp:v1.0`. Docker Hub is the default public registry (like npm's default registry). Your company uses a private registry (like a private npm registry) so your internal images aren't public. When Kubernetes deploys your app, it pulls the image from the registry.

---

### ðŸ”µ Simple Definition (Elaborated)

The registry is the critical link between CI/CD (where images are built) and deployment (where images run). The flow: developer pushes code â†’ CI builds Docker image â†’ CI pushes image to registry â†’ deployment system (Kubernetes) pulls image from registry â†’ container runs. Without a registry, you'd have to copy images manually to every server (impractical at scale). Registry features that matter in production: **image scanning** (CVE detection on every push), **image signing** (Cosign/Notary: cryptographic proof of who built the image), **retention policies** (auto-delete old images to manage storage costs), **geo-replication** (replicate registry to multiple regions for fast pulls), **access control** (RBAC: who can push to which repository), **pull-through cache** (proxy Docker Hub to avoid rate limits and single point of failure).

---

### ðŸ”© First Principles Explanation

```
REGISTRY ARCHITECTURE:

  Registry
  â”œâ”€â”€ Repository: myorg/api
  â”‚   â”œâ”€â”€ Tag: latest â†’ manifest SHA256:abc â†’ [layer1, layer2, layer3]
  â”‚   â”œâ”€â”€ Tag: v1.2.3 â†’ manifest SHA256:def â†’ [layer1, layer2, layer4]
  â”‚   â””â”€â”€ Tag: v1.2.2 â†’ manifest SHA256:ghi â†’ [layer1, layer2, layer5]
  â”œâ”€â”€ Repository: myorg/worker
  â”‚   â””â”€â”€ Tag: main-a1b2c3 â†’ manifest SHA256:jkl
  â””â”€â”€ Repository: myorg/frontend
      â””â”€â”€ Tag: v2.0.0 â†’ manifest SHA256:mno

  LAYER DEDUPLICATION:
  Both v1.2.2 and v1.2.3 share layer1 (base OS) and layer2 (Java runtime)
  The registry stores each layer ONCE (by SHA256 content address)
  Pull v1.2.3 when v1.2.2 is cached: only download layer4 (the diff)

IMAGE NAME ANATOMY:

  docker.io/library/nginx:1.24-alpine
  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  registry â”‚  org   â”‚repo â”‚  tag

  docker.io/library/nginx:latest         â† Docker Hub official image
  ghcr.io/myorg/myapp:v1.2.3            â† GitHub Container Registry
  123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:v1.2.3  â† AWS ECR
  us.gcr.io/myproject/myapp:v1.2.3      â† Google Container Registry
  myregistry.azurecr.io/myapp:v1.2.3    â† Azure Container Registry
  registry.mycompany.com/myapp:v1.2.3   â† self-hosted

  SHORT NAMES (Docker Hub defaults):
  nginx          â†’ docker.io/library/nginx:latest
  nginx:1.24     â†’ docker.io/library/nginx:1.24
  myorg/myapp    â†’ docker.io/myorg/myapp:latest

TAG vs DIGEST:

  # Tag (mutable): same tag can point to different manifests over time
  docker pull nginx:latest   â† today: SHA256:abc; tomorrow: SHA256:xyz (updated)

  # Digest (immutable): always the exact same image
  docker pull nginx@sha256:abc123def456...

  # Production rule: pin to digest (immutable) for reproducibility
  # CI: tag with commit SHA + semantic version
  myapp:v1.2.3-abc123  â† semantic version + git SHA
  myapp:v1.2.3         â† semantic version (reproducible)
  myapp:main-abc123    â† branch + commit SHA (CI artifact)
  myapp:latest         â† mutable; DO NOT use in Kubernetes deployments

  # Why :latest is dangerous in K8s:
  imagePullPolicy: Always  â† pulls :latest on every pod start
  # â†’ different pods may run different image versions if :latest was updated
  # â†’ can't roll back (what was :latest before?)
  # â†’ production instability

PUSH/PULL PROTOCOL (OCI Distribution Spec):

  PUSH:
  1. docker push myregistry/myapp:v1.0
  2. Client: calculate SHA256 for each layer
  3. For each layer: HEAD /v2/myapp/blobs/{sha} â†’ 404 (not found) or 200 (exists)
  4. If not found: PUT /v2/myapp/blobs/uploads/{uuid} â†’ upload layer bytes
  5. PUT /v2/myapp/manifests/v1.0 â†’ upload manifest (references all layer SHAs)

  PULL:
  1. docker pull myregistry/myapp:v1.0
  2. GET /v2/myapp/manifests/v1.0 â†’ manifest (list of layer SHAs)
  3. For each layer SHA: check local cache â†’ if cached, skip
  4. If not cached: GET /v2/myapp/blobs/{sha} â†’ download layer
  5. Assemble image from layers

REGISTRY COMPARISON:

  Docker Hub:
  âœ“ Default public registry; free for public images
  âœ— Rate limits: 100 pulls/6h (anonymous), 200 pulls/6h (free account)
  âœ— Outage = CI/CD blocked for everyone using public images
  â†’ Use pull-through cache to avoid rate limits

  AWS ECR:
  âœ“ Private by default; tight IAM integration
  âœ“ Image scanning (Clair/Trivy integration)
  âœ“ Lifecycle policies (auto-delete old images)
  âœ“ Cross-region replication
  âœ— Authentication via aws ecr get-login-password (expires 12 hours)
  â†’ Best for: AWS-native deployments; EKS clusters

  Google Artifact Registry (successor to GCR):
  âœ“ Private; IAM integration; regional by default
  âœ“ Multi-format: Docker, Maven, npm, Python
  âœ“ Vulnerability scanning
  â†’ Best for: GKE clusters

  Azure Container Registry (ACR):
  âœ“ Private; Azure AD integration; geo-replication
  â†’ Best for: AKS clusters

  GitHub Container Registry (ghcr.io):
  âœ“ Integrated with GitHub Actions; per-repo/org
  âœ“ Free for public repos; linked to GitHub packages
  â†’ Best for: open source, GitHub Actions CI

  Harbor (self-hosted):
  âœ“ Full control; RBAC; image signing; scanning
  âœ“ Pull-through cache (proxy Docker Hub)
  âœ— Ops burden (run + maintain the registry itself)
  â†’ Best for: air-gapped environments, large enterprises

PULL-THROUGH CACHE:

  Problem: k8s nodes pull from Docker Hub â†’ rate limits hit â†’ deployment fails

  Solution: Harbor or ECR Pull-Through Cache
  1. Configure: registry.mycompany.com proxies â†’ docker.io
  2. First pull: cache misses â†’ downloads from Docker Hub â†’ stores in Harbor
  3. Subsequent pulls: cache hit â†’ serves from Harbor (fast + no rate limit)
  4. Docker Hub rate limit: only once per layer (not per pull request from k8s)
```

---

### â“ Why Does This Exist (Why Before What)

Container images are large (hundreds of MB to GB), layer-structured, and need to be distributed to potentially thousands of nodes across multiple regions. A content-addressable, deduplicated, structured storage system with a standardized API (OCI Distribution Spec) is essential for this. Without a registry: manual SCP/rsync of image tarballs, no layer deduplication, no version management, no access control. The registry makes container distribution as reliable and efficient as package distribution (npm, Maven Central, PyPI).

---

### ðŸ§  Mental Model / Analogy

> **A container registry is like GitHub for Docker images**: just as GitHub stores code versions, a registry stores image versions. `docker push` is `git push`, `docker pull` is `git clone/pull`. Tags are like branches (mutable: `:latest` = `main`). Digests are like commit SHAs (immutable). Repositories are repos. Layer deduplication is like git's delta compression â€” only the differences are stored and transferred, not full copies.

---

### âš™ï¸ How It Works (Mechanism)

```
CI/CD PIPELINE WITH REGISTRY:

  1. GitHub push to main branch
  2. GitHub Actions triggers CI workflow
  3. docker build -t ghcr.io/myorg/myapp:main-$SHA .
  4. docker push ghcr.io/myorg/myapp:main-$SHA
  5. docker tag ... :latest && docker push ... :latest
  6. Update Kubernetes deployment manifest:
     image: ghcr.io/myorg/myapp:main-$SHA    â† pin to immutable tag
  7. kubectl apply -f k8s/deployment.yaml
  8. K8s nodes: pull ghcr.io/myorg/myapp:main-$SHA (only new layers)
  9. Rolling update: new pods start with new image â†’ old pods terminated
```

---

### ðŸ”„ How It Connects (Mini-Map)

```
Build produces an image; deployment needs the image
        â”‚
        â–¼
Container Registry â—„â”€â”€ (you are here)
(stores images; push from CI; pull at deploy time)
        â”‚
        â”œâ”€â”€ Docker Image: what's stored in the registry (manifest + layers)
        â”œâ”€â”€ Docker Layer: deduplicated storage; partial pulls (only new layers)
        â”œâ”€â”€ Multi-Stage Build: final (small) image is what gets pushed
        â”œâ”€â”€ CI-CD Pipeline: pushes images to registry after build
        â””â”€â”€ Kubernetes: pulls images from registry when deploying pods
```

---

### ðŸ’» Code Example

{% raw %}
```yaml
# GitHub Actions workflow: build + push to GitHub Container Registry
name: Build and Push

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }} # myorg/myapp

jobs:
  build-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write # permission to push to ghcr.io

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            # tag :latest on main branch push
            type=raw,value=latest,enable={{is_default_branch}}
            # tag with git SHA: main-abc1234
            type=sha,prefix={{branch}}-
            # tag with semver on release: v1.2.3, v1.2, v1
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha # GitHub Actions cache for layers
          cache-to: type=gha,mode=max
```
{% endraw %}

---

### âš ï¸ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                                                                                                                                      |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `:latest` tag is always up-to-date      | `:latest` is just a tag like any other â€” it's only updated if you explicitly `docker push myimage:latest`. If your CI only pushes `:v1.2.3`, `:latest` is stale. Many registries/workflows push both the versioned tag AND update `:latest`. Always pin to versioned tags in Kubernetes.     |
| Deleting a tag deletes the image layers | Deleting a tag only removes the tag reference to the manifest. The layers (blobs) remain in the registry until garbage collection runs. Most registries have a separate GC process that reclaims unreferenced blobs. This is intentional: multiple tags may reference the same layers.       |
| Private registry = secure by default    | Authentication prevents unauthorized pulls, but doesn't prevent: pushing a compromised image from a compromised CI system, images with embedded secrets (see Docker Build Context), unpatched CVEs in base images. Image scanning + signing (Cosign) are required for a secure supply chain. |

---

### ðŸ”¥ Pitfalls in Production

```
PITFALL: Docker Hub rate limits breaking CI

  # Pull from Docker Hub in CI: FROM nginx:alpine
  # 100 pulls/6h anonymous â†’ CI fails with "toomanyrequests"

  # FIX 1: authenticate to Docker Hub in CI (200 pulls/6h free, more on paid)
  docker login -u $DOCKERHUB_USERNAME -p $DOCKERHUB_TOKEN

  # FIX 2: mirror to private registry (best for production)
  # Replace: FROM nginx:alpine
  # With: FROM myregistry.com/cache/library/nginx:alpine
  # Harbor pull-through cache: myregistry.com/cache proxies docker.io

  # FIX 3: ECR public gallery (no rate limits for ECR auth'd pulls)
  FROM public.ecr.aws/nginx/nginx:alpine

PITFALL: :latest tag used in Kubernetes deployment

  # âŒ Don't do this in production:
  containers:
  - name: app
    image: myregistry.io/myapp:latest
    imagePullPolicy: Always

  # Problem: "latest" can change; can't roll back; pods may run different versions

  # âœ… Pin to immutable tag (git SHA or semantic version):
  containers:
  - name: app
    image: myregistry.io/myapp:v1.2.3
    # OR
    image: myregistry.io/myapp@sha256:abc123...   # digest: most immutable
    imagePullPolicy: IfNotPresent   # don't re-pull if already on node
```

---

### ðŸ”— Related Keywords

- `Docker Image` â€” the artifact stored in and distributed by the registry
- `Docker Layer` â€” the storage unit; deduplicated across images in the registry
- `CI-CD Pipeline` â€” pushes images to the registry after successful builds
- `Kubernetes` â€” pulls images from the registry when deploying pods
- `Docker` â€” the CLI used for `docker push` / `docker pull`

---

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ REGISTRIES: Docker Hub | ECR | GAR | ACR | ghcr.io | Harborâ”‚
â”‚ FORMAT: registry/org/repo:tag                           â”‚
â”‚ PUSH: docker push registry/myapp:v1.2.3                 â”‚
â”‚ PULL: docker pull registry/myapp:v1.2.3                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ RULES:                                                   â”‚
â”‚ â€¢ Never use :latest in K8s; pin to version or digest    â”‚
â”‚ â€¢ Private registry for proprietary images               â”‚
â”‚ â€¢ Mirror Docker Hub to avoid rate limits                â”‚
â”‚ â€¢ Image scanning on push (CVE detection)                â”‚
â”‚ â€¢ Image signing (Cosign) for supply chain security      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

**Q1.** Container image supply chain attacks (SolarWinds-style but for Docker images) are an active threat: an attacker compromises a popular base image on Docker Hub, introducing malware. Your CI pulls `FROM node:18` and unknowingly builds a compromised image. Design a defense-in-depth strategy using: (a) image signing with Cosign + sigstore, (b) admission controllers in Kubernetes (OPA/Kyverno/Connaisseur), (c) private registry mirroring, (d) digest pinning in Dockerfiles. How does this chain prevent the attack at each stage?

**Q2.** Registry storage costs can be significant at scale: thousands of builds per day, each producing a multi-layer image, each layer potentially hundreds of MB. Describe an image retention strategy using lifecycle policies that: (a) keeps all release (semver) tags indefinitely, (b) keeps the last N builds per branch, (c) deletes images older than 30 days that aren't tagged with a semver, (d) handles the case where multiple tags point to the same digest (you don't want to delete a layer that a kept image references). How do ECR lifecycle policies handle these requirements?
