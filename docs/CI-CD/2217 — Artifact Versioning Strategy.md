---
layout: default
title: "Artifact Versioning Strategy"
parent: "CI/CD"
nav_order: 2217
permalink: /ci-cd/artifact-versioning-strategy/
number: "2217"
category: CI/CD
difficulty: ★★★
depends_on: CI-CD, Semantic Versioning, Container Registry
used_by: CI-CD
related: Semantic Versioning, GitOps, Container Registry
tags:
  - cicd
  - devops
  - advanced
  - bestpractice
---

# 2217 — Artifact Versioning Strategy

⚡ **TL;DR —** Artifact versioning strategy defines how software artifacts are tagged, stored, and referenced so every deployed version is uniquely identifiable, immutable, and traceable to its source.

| Field | Value |
|-------|-------|
| **Depends on** | CI-CD, Semantic Versioning, Container Registry |
| **Used by** | CI-CD |
| **Related** | Semantic Versioning, GitOps, Container Registry |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** The production Docker image is tagged `latest`. A rollback means pushing a new `latest` and hoping caches are refreshed. Nobody knows which Git commit is running. A post-incident review finds three different team members have three different answers about what version deployed at 3:17 PM.

**THE BREAKING POINT:** A breaking change ships because a dependency was silently upgraded between two "identical" builds. The pipeline logs show the same source tag was built twice within one hour, each resolving a different version of a transitive library. The `latest` tag was overwritten mid-deployment and half the pods are running v1 while the other half run v2.

**THE INVENTION MOMENT:** The insight is that an artifact must carry its identity — not just a human-readable label. The version is the immutable cryptographic fingerprint of content plus metadata linking it to source. Every other property (human name, environment label, release marker) is derived from that identity.

---

### 📘 Textbook Definition

An **Artifact Versioning Strategy** is the set of rules that govern how software build outputs (Docker images, JARs, npm packages, Helm charts) are named, tagged, stored, and referenced throughout their lifecycle — ensuring each artifact has a unique, immutable identifier traceable to a source commit, enabling deterministic deployment, reliable rollback, and audit-quality provenance.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Every artifact gets a unique, immutable name that maps back to a specific source commit and build.

> Think of artifact versioning like a VIN (Vehicle Identification Number) on a car. The VIN encodes the factory, model year, and production sequence in an immutable code stamped at manufacture. A recall or investigation traces every vehicle back to its origin — you never re-stamp a VIN.

**One insight:** The worst tagging strategy is `latest` — it is mutable, provides no provenance, and makes rollback ambiguous. The best strategy uses content-addressed tags (Git SHA or image digest) as the authoritative identity, with human-readable semantic versions as derived aliases pointing to the same digest.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An artifact's identity must be deterministic and content-addressable.
2. A tag is mutable; a digest (SHA-256) is immutable.
3. Rollback requires knowing exactly what bytes ran in each environment at each time.
4. Human-readable versions (1.2.3) and deployment identifiers (Git SHA) serve different audiences and should coexist, not compete.

**DERIVED DESIGN:** Use the Git SHA as the primary immutable identifier, applied at build time. Apply a semantic version tag as a human-readable alias when a release decision is made. Store both in the registry. Reference production deployments by digest, not by mutable tag. Retain artifacts for their full retention policy before deletion.

**THE TRADE-OFFS:**
**Gain:** Full provenance chain from running pod back to source line; reliable rollback; deterministic environment promotion; compliance-quality audit trail.
**Cost:** Registry storage grows with every build; retention policies and cleanup automation become necessary; multi-arch manifests add complexity; Maven SNAPSHOT semantics must be carefully scoped.

---

### 🧪 Thought Experiment

**SETUP:** Your team builds a Docker image and tags it `myapp:v1.2`. After a successful prod deployment, a regression is found. You need to roll back to the version deployed last Thursday.

**WHAT HAPPENS WITHOUT A VERSIONING STRATEGY:** `v1.2` was overwritten by a hotfix build this morning. The image from last Thursday no longer exists under that tag. The registry has no old versions because `latest` is all that was kept. You must rebuild from a Git tag and hope the rebuild produces identical bytes — which it does not because a dependency published a patch.

**WHAT HAPPENS WITH A VERSIONING STRATEGY:** Last Thursday's deployment used `myapp:sha-a3f1c7b`. That digest still exists in the registry (within retention window). Your deployment manifest references the digest directly. Rollback is a one-line change to the manifest; it completes in 30 seconds.

**THE INSIGHT:** Versioning is not about naming. It is about **preserving the ability to reason about the past** — to know exactly what ran, when, and to restore it deterministically without rebuilding.

---

### 🧠 Mental Model / Analogy

> Think of artifact versioning as a **library cataloguing system combined with a freezer**. Every book (artifact) gets a unique ISBN (Git SHA/digest). The librarian assigns a human-readable call number (semantic version) as an alias. The book is sealed and cannot be changed after cataloguing. The freezer (registry) preserves exact copies for the retention period.

- The book = the artifact (Docker image, JAR, npm package)
- ISBN = Git SHA or image digest (immutable, content-addressed)
- Call number = semantic version (human-readable alias)
- Library catalogue = container registry or artifact repository
- Freezer duration = artifact retention policy
- Retrieval = rollback or audit investigation

Where this analogy breaks down: A library ISBN is assigned by a third party; artifact Git SHAs are computed from content — two identical builds (rare) would produce the same SHA, which is a feature, not a collision.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Artifact versioning means every time you build your software, the output gets a unique name that tells you exactly what code was compiled. You can always find the exact version that is running in production and go back to it if needed.

**Level 2 — How to use it (junior developer):**
In your CI pipeline, compute the Git SHA of the commit being built. Tag your Docker image with it: `myapp:abc1234`. Also tag with the semantic version if this is a release build: `myapp:2.4.1`. Push both tags. In Kubernetes manifests, reference the SHA tag — never `latest`. For Maven/npm packages, use the version from `pom.xml` or `package.json` and do not publish SNAPSHOT/pre-release to production registries.

**Level 3 — How it works (mid-level engineer):**
A complete versioning scheme uses multiple tag types with defined semantics: `myapp:sha-abc1234` (primary identity, always pushed), `myapp:2.4.1` (semantic release alias, pushed when a release is cut), `myapp:2.4` and `myapp:2` (floating aliases for major/minor, optional). In the registry, tag immutability prevents overwrite of SHA tags. Multi-arch images use an OCI manifest list referencing per-arch digests under one tag. The Helm chart version is versioned independently from the app version, and the `appVersion` field tracks the container image version the chart is designed for.

**Level 4 — Why it was designed this way (senior/staff):**
The dual-tag design (SHA + semver) resolves a tension between two audiences: machines (CD pipelines, rollback scripts) need a stable, immutable address that never changes once assigned — the SHA digest satisfies this. Humans (release managers, change reviewers) need a meaningful version that communicates intent and precedence — semantic versioning satisfies this. Digest-addressed references in production manifests (`myapp@sha256:abc...`) remove the registry as a single point of failure for tag resolution: the manifest itself carries the authoritative identity. This is the pattern GitOps and supply-chain security tools (cosign, SLSA) build on.

---

### ⚙️ How It Works (Mechanism)

```
Source Commit (abc1234)
    │
    ▼
┌──────────────────────────────────────┐
│  CI Build                            │
│  compute GIT_SHA=abc1234             │
│  docker build → image                │
│  digest: sha256:deadbeef             │
└──────────┬───────────────────────────┘
           │ push
           ▼
┌──────────────────────────────────────┐
│  Container Registry                  │
│  myapp:sha-abc1234 → sha256:deadbeef │
│  myapp:2.4.1       → sha256:deadbeef │
│  (same bytes, two name aliases)      │
└──────────┬───────────────────────────┘
           │ referenced by
           ▼
┌──────────────────────────────────────┐
│  Kubernetes Manifest                 │
│  image: myapp@sha256:deadbeef        │
│  (immutable digest reference)        │
└──────────────────────────────────────┘
```

**Tag taxonomy:**

| Tag pattern | Example | Mutable? | Purpose |
|-------------|---------|----------|---------|
| Git SHA | `sha-abc1234` | No | Primary identity |
| Full semver | `2.4.1` | No | Release alias |
| Minor float | `2.4` | Yes | Auto-minor updates |
| `latest` | `latest` | Yes | Development only |
| Branch | `main-abc1234` | No | Branch build identity |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
PR merged to main → CI starts ← YOU ARE HERE
    │
    ▼
Compute: GIT_SHA=abc1234
Build: myapp:sha-abc1234
    │  push to registry
    ▼
Registry stores: sha-abc1234 → sha256:dead
    │
    ▼
Dev manifest updated: image=sha-abc1234
    │  gate passes
    ▼
Staging manifest updated: image=sha-abc1234
    │  release decision made → cut v2.4.1
    ▼
Registry alias: 2.4.1 → sha256:dead (same)
    │
    ▼
Prod manifest updated: image@sha256:dead
    │  (digest reference, bypasses tag lookup)
    ▼
Artifact lifecycle: retain 90 days
    │  then cleaned up by registry policy
    ▼
Audit query: "what ran in prod on Jan 3?"
→ manifest git history → sha256:dead
→ registry provenance → sha-abc1234
→ git log abc1234 → exact commit + author
```

**FAILURE PATH:**
```
Build produces sha-abc1234
Registry rejects push: tag immutability
    │  (same SHA already exists — identical build)
    ▼
Pipeline proceeds — existing image used
    │  this is correct behaviour, not an error
    ▼
If different commit produces same SHA:
    │  (hash collision — astronomically rare)
    ▼
Investigate — likely a build config error
```

**WHAT CHANGES AT SCALE:**
Registry storage grows to terabytes; automated retention policies become mandatory. Multi-arch manifests (amd64 + arm64) require manifest list management. Software Bill of Materials (SBOM) attached per artifact digest becomes a compliance requirement. Cosign signatures and SLSA provenance attestations are added to the registry alongside the image.

---

### 💻 Code Example

**BAD — mutable latest tag, no provenance:**
```bash
# BAD: latest is mutable, no traceability
docker build -t myapp:latest .
docker push myapp:latest
# Rollback: rebuild and hope it's identical
# Audit: "which version ran in prod?" — unknown
```

**GOOD — immutable SHA tag with semver alias:**
```bash
#!/bin/bash
GIT_SHA=$(git rev-parse --short HEAD)
APP_VERSION=$(cat VERSION)  # e.g. "2.4.1"
IMAGE="myregistry.io/myapp"

# Build once
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag "${IMAGE}:sha-${GIT_SHA}" \
  --tag "${IMAGE}:${APP_VERSION}" \
  --push .

# Production manifest references digest (immutable)
DIGEST=$(docker inspect \
  --format='{{index .RepoDigests 0}}' \
  "${IMAGE}:sha-${GIT_SHA}")

# Update kustomization to use digest
kustomize edit set image \
  "myapp=${IMAGE}@${DIGEST}"
```

**GOOD — Maven release versioning (no SNAPSHOT in prod):**
```xml
<!-- pom.xml: release version only in production -->
<version>2.4.1</version>
<!-- CI sets this via: mvn versions:set -DnewVersion=2.4.1 -->
<!-- SNAPSHOT (2.4.1-SNAPSHOT) is for development only -->
<!-- Never deploy SNAPSHOT to prod artifact registry -->
```

---

### ⚖️ Comparison Table

| Strategy | Mutable? | Rollback | Provenance | Complexity | Recommended |
|----------|----------|----------|------------|------------|-------------|
| `latest` tag only | Yes | Impossible | None | None | Never |
| Branch tag | Partially | Hard | Partial | Low | Dev only |
| Git SHA tag | No | Reliable | Full | Low | Always |
| Semver tag | No (if enforced) | Reliable | Partial | Medium | Releases |
| Digest reference | Never | Guaranteed | Full + verified | Medium | Production |
| SNAPSHOT / RC | Varies | Risky | Partial | Low | Pre-release only |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Semantic versioning IS the artifact version" | Semver is a human-readable alias pointing to a specific artifact digest. The version number communicates intent; the digest is the immutable identity. |
| "Same Git tag = same artifact" | Not true without a deterministic build. Two builds from the same tag can produce different bytes if dependencies are resolved at build time. |
| "`latest` is fine for internal services" | `latest` is mutable. Two pods in the same deployment can pull different images if `latest` is overwritten mid-rollout. Always use immutable tags in Kubernetes. |
| "Multi-arch images are just two images" | Multi-arch images are OCI manifest lists: a single tag resolves to an architecture-specific digest. Pushing incorrectly can break the manifest list and silently serve the wrong arch. |
| "Registry tag immutability prevents all issues" | Tag immutability prevents overwrite but not deletion. An artifact deleted before its retention window expires breaks rollback. Retention policy enforcement is a separate control. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Mutable tag overwritten mid-deployment**
**Symptom:** Half the pods in a Deployment run v1, half run v2 after a rolling update. Kubernetes reports the Deployment as `Ready` but behaviour is inconsistent.
**Root Cause:** `imagePullPolicy: Always` combined with a mutable tag (`latest`) allows the registry to serve a newer image to some pods during rollout.
**Diagnostic:**
```bash
# Check image running on each pod
kubectl get pods -o jsonpath=\
'{range .items[*]}{.metadata.name}{"  "}\
{.status.containerStatuses[0].imageID}{"\n"}{end}'
# Different imageIDs confirm mixed versions
```
**Fix:**
BAD — Set `imagePullPolicy: Never` to stop re-pulling.
GOOD — Reference images by digest in manifests; set `imagePullPolicy: IfNotPresent`. Two pods referencing the same digest are guaranteed identical.
**Prevention:** Enforce digest-only references in production manifests via OPA/Kyverno admission policy.

**Failure Mode 2: SNAPSHOT artifact promoted to production**
**Symptom:** Production breaks because a transitive dependency changed overnight with no code change.
**Root Cause:** A Maven SNAPSHOT version was deployed to production; SNAPSHOTs re-resolve dependencies on each build/fetch.
**Diagnostic:**
```bash
# Check artifact version in prod
kubectl get deploy myapp -o json \
  | jq '.spec.template.spec.containers[0].image'

# In Nexus/Artifactory, check if version
# ends in -SNAPSHOT
```
**Fix:**
BAD — Pin the SNAPSHOT by locking the pom.xml dependency.
GOOD — Never publish SNAPSHOT to the prod artifact registry. CI gate rejects any deployment where the version string contains `-SNAPSHOT` or `-RC`.
**Prevention:** Add registry policy rule: prod-releases repository rejects artifacts with SNAPSHOT in version. CI pipeline validates version format before push.

**Failure Mode 3: Registry retention deletes artifacts before rollback window**
**Symptom:** Emergency rollback to a 45-day-old version fails because the image no longer exists in the registry.
**Root Cause:** Registry cleanup policy is set to 30 days; incident required a rollback beyond that window.
**Diagnostic:**
```bash
# Check if image exists in ECR
aws ecr describe-images \
  --repository-name myapp \
  --image-ids imageTag=sha-abc1234 \
  2>&1 | grep -i "does not exist\|ImageNotFoundException"
```
**Fix:**
BAD — Extend retention to 1 year globally (storage cost explosion).
GOOD — Implement tiered retention: all builds 30 days; release-tagged artifacts 1 year; prod-deployed artifacts never deleted until superseded + 90 days.
**Prevention:** Tag every image promoted to production with an additional `prod-deployed` label; retention policy excludes this label from cleanup.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- CI-CD — the pipeline that builds and tags artifacts
- Semantic Versioning — the human-readable version scheme used as artifact aliases
- Container Registry — the storage system that enforces tag immutability

**Builds On This (learn these next):**
- GitOps — uses artifact image tags/digests as the source of truth for environment state
- Environment Promotion Strategy — depends on immutable artifact tags to work correctly
- Supply Chain Security — SBOM, cosign signing, and SLSA provenance build on immutable digest identity

**Alternatives / Comparisons:**
- Git tags — the source version identifier; parallel but distinct from artifact version
- Helm chart versioning — artifact versioning for Kubernetes deployment manifests
- npm publish — the package registry equivalent of container image push

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS     │ Rules for naming and tracking       │
│                │ build artifacts across environments  │
│ PROBLEM        │ Mutable tags break rollback/audit   │
│ KEY INSIGHT    │ Digest = identity; semver = alias   │
│ USE WHEN       │ Any artifact deployed to production │
│ AVOID WHEN     │ (Always apply)                      │
│ TRADE-OFF      │ Rigour vs. registry storage cost    │
│ ONE-LINER      │ Git SHA tag + digest ref = truth    │
│ NEXT EXPLORE   │ Semantic Versioning, GitOps, SLSA   │
└─────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** If two different commits produce the same Docker image digest (identical bytes), should they share the same artifact version? What does this tell you about whether artifact identity should be based on content or on source lineage?

2. **(Scale)** With 50 microservices each building 20 images per day, registry storage grows rapidly. How would you design a tiered retention policy that guarantees rollback capability for production artifacts while controlling storage costs?

3. **(System Interaction)** A Helm chart and the Docker image it deploys are versioned independently. What coupling problems arise when the chart's `appVersion` drifts from the deployed image version — and what governance mechanism would you put in CI to detect and block this drift?
