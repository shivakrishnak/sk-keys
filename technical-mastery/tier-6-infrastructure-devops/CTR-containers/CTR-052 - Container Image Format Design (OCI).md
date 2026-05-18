---
id: CTR-056
title: Container Image Format Design (OCI)
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-006, CTR-009, CTR-020
used_by: CTR-049
related: CTR-040, CTR-052
tags:
  - containers
  - internals
  - deep-dive
  - first-principles
  - docker
status: complete
version: 3
layout: default
parent: "Containers"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/ctr/container-image-format-design-oci/
---

⚡ TL;DR - An OCI container image is a content-addressable collection of layers (tar archives) plus a JSON manifest and image config - all stored in a registry as blobs identified by their SHA-256 digest.

| Metadata        |                        |     |
| :-------------- | :--------------------- | :-- |
| **Depends on:** | CTR-006, CTR-009, CTR-020 |     |
| **Used by:**    | CTR-049                |     |
| **Related:**    | CTR-040, CTR-052       |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2014, Docker had its own proprietary image format. CoreOS developed
rkt with a different image format (ACI). Running a container image built
for Docker on rkt was impossible. The container ecosystem was fragmenting
along runtime/image format lines before it had a chance to mature.

**THE BREAKING POINT:**
Cloud providers, CI tools, and orchestrators had to choose: support
Docker format only, or implement multiple format converters. Kubernetes
1.0 needed to work with both Docker and rkt. Every registry had to
understand both formats. The ecosystem needed a common standard.

**THE INVENTION MOMENT:**
The Open Container Initiative (OCI) was founded in 2015 by Docker,
CoreOS, Google, and others. Two specifications emerged: OCI Image Spec
(what an image is) and OCI Runtime Spec (how to run it). Any registry
that stores OCI images and any runtime that implements OCI Runtime Spec
can interoperate. Docker images were reformatted to comply with OCI
Image Spec v1.0 (2017).

**EVOLUTION:**
2017: OCI Image Spec v1.0. All major registries and runtimes converge.
2019: OCI Distribution Spec standardises the registry HTTP API (previously
only Docker Registry API v2 was used). 2021: OCI Artifacts extend the
spec to store non-image content (Helm charts, WASM modules, SBOMs)
in OCI registries using the same content-addressable model. 2023:
OCI Image Spec v1.1 adds referrers API (attaching SBOMs and signatures
to images without modifying the image itself).

---

### 📘 Textbook Definition

**OCI Image Spec** defines a container image as a content-addressable
artifact stored in an OCI-compliant registry. An image consists of: a
**manifest** (JSON document listing the config blob and layer blobs
by digest), an **image config** (JSON document with environment,
entrypoint, working directory, and the layer diff chain), and one or
more **layer blobs** (gzip-compressed tar archives of filesystem
changes). All blobs are identified by their SHA-256 digest, enabling
deduplication and integrity verification.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An OCI image = manifest (index) + config (metadata) + layers (filesystem
diffs), all stored as content-addressed SHA-256 blobs in a registry.

**One analogy:**

> An OCI image is like a recipe book. The manifest is the table of
> contents (lists all pages by page number). The config is the recipe
> intro (cooking instructions, temperature, time). Each layer is a
> recipe step (add these ingredients). The SHA-256 digest is the page
> number - if you know the page number (digest), you know exactly what
> is on that page (content-addressable).

**One insight:**
Content-addressability is the OCI image's most important property: the
SHA-256 digest of a blob is both its identifier and its integrity check.
You cannot have a valid blob with a wrong digest. This makes image
pull atomic: either you got the correct content, or the pull fails.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Content-addressability** - every blob is named by its SHA-256
   digest. Two blobs with the same content have the same name, enabling
   deduplication across images.
2. **Layers are filesystem diffs** - each layer is a tar archive of
   files added, modified, or deleted relative to the layer below. The
   union filesystem (overlayfs) merges layers at runtime.
3. **The manifest is the entry point** - to pull an image, you fetch
   the manifest by tag or digest. The manifest references all other
   blobs. Tags are mutable references to manifests; digests are
   immutable.
4. **Image configs are separate from layers** - the config stores
   metadata (environment, entrypoint, ports, labels) independently of
   the filesystem content. A config change creates a new image without
   re-uploading layers.

**DERIVED DESIGN:**
Given invariant 1: a base image layer shared by 100 images is stored
once in the registry and pulled once to a node. Deduplication is
automatic. Given invariant 3: pinning by digest (`myapp@sha256:abc123`)
is immutable and safe for production; pinning by tag (`myapp:v1.0`) is
mutable and risks silent changes.

**THE TRADE-OFFS:**

**Gain:** Content-addressable storage enables deduplication, integrity
verification, and immutable references. Layer sharing reduces registry
storage and pull bandwidth.

**Cost:** Layers are append-only. To "remove" a file from a layer below,
a whiteout file must be added in a higher layer - the file is hidden
but still present in the lower layer's blob. This means sensitive data
accidentally added to a lower layer cannot be truly removed without
rebuilding from scratch.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Content-addressable blobs, manifests, and image configs
are all required to enable deduplication, integrity, and metadata
separation.

**Accidental:** Docker Image Spec v1 (pre-OCI) embedded metadata inside
layers, making layer reuse difficult. OCI cleaned this up.

---

### 🧪 Thought Experiment

**SETUP:**
100 microservices all share the same Java 21 base image (150 MB). Each
service adds ~20 MB of application code on top.

**WHAT HAPPENS WITHOUT CONTENT-ADDRESSABLE STORAGE:**
Each of the 100 images stores its own copy of the 150 MB base layer.
Registry storage: 100 * 170 MB = 17 GB. Each node pull downloads the
full 170 MB per new service, even if the base layer is already present.

**WHAT HAPPENS WITH CONTENT-ADDRESSABLE OCI STORAGE:**
The 150 MB base layer has one SHA-256 digest. It is stored once in the
registry (150 MB). All 100 services reference this digest in their
manifests. Each service only stores its unique 20 MB layer.
Registry storage: 150 MB + (100 * 20 MB) = 2.15 GB (87% reduction).
A node that already has the base layer cached only pulls the 20 MB
service layer for each new service.

**THE INSIGHT:**
Content-addressable layer sharing is an emergent property of the OCI
design, not an explicit optimisation. It falls out automatically from
naming blobs by their content digest. The engineering insight is that
the same principle (content-addressable storage) used in Git and
BitTorrent is also the right model for container image distribution.

---

### 🧠 Mental Model / Analogy

> An OCI image in a registry is like a book in a library's card catalog
> system. The catalog entry (manifest) tells you: "This book uses
> chapter drafts 1a, 2b, and 3c (layer blobs)." Each draft is filed by
> its content hash (digest). If two books share chapter 1 text verbatim,
> there is only one physical copy of that chapter in storage. To read
> the book, you retrieve each chapter draft and stack them in order.

Element mapping:

- **Catalog entry** = OCI manifest
- **Chapter draft** = image layer blob (tar archive)
- **Content hash** = SHA-256 blob digest
- **Book title** = image tag
- **Reading the book** = overlayfs layer merge at runtime
- **Library** = OCI-compliant container registry

Where this analogy breaks down: library books are not stacked and merged
into a combined view; image layers are merged by overlayfs into a single
filesystem view at container runtime.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A container image is like a layered stack of filesystem changes, stored
in a registry. Each layer is a small compressed file. The registry
stores each unique layer once, even if many images share it.

**Level 2 - How to use it (junior developer):**
Understanding OCI format helps you optimise Dockerfiles: put frequently
changing layers (your app code) at the bottom; put stable layers
(base OS, runtime) at the top. This maximises cache sharing. Use
`docker image history` to see your image's layers and sizes.

**Level 3 - How it works (mid-level engineer):**
A registry stores blobs identified by digest. When you push an image,
the CLI computes SHA-256 of each layer, checks if the blob exists in
the registry (via HEAD request), and skips upload if it does. The
manifest references layer digests. When you pull, the CLI fetches the
manifest, then fetches each referenced blob (skipping ones already
in the local cache). containerd stores layers in its content store;
overlayfs merges them at container start.

**Level 4 - Why it was designed this way (senior/staff):**
Content-addressable storage (CAS) was chosen because it solves
deduplication and integrity simultaneously with no additional mechanism.
In a non-CAS system, you need a separate deduplication index and a
separate integrity check. In CAS, the name is the integrity check, and
deduplication is automatic (same content = same name = same blob).
Git uses the same principle for commits and trees. The OCI designers
explicitly borrowed from Git and the academic content-addressable
storage literature.

**Expert Thinking Cues:**

- "Is this image tag mutable? If we pin to the tag in production, can
  it silently change? Use digest pinning for production."
- "A file was added to layer 2 and deleted in layer 4. Is the file
  still present in registry storage? Yes - layer 2's blob still contains
  it. Security implication?"
- "If I change only the CMD in the Dockerfile (no filesystem changes),
  does that create a new layer? No - CMD is stored in the image config,
  not a layer."

---

### ⚙️ How It Works (Mechanism)

**OCI IMAGE STRUCTURE:**

```
Registry
  └─ myapp:v1.0  (tag - mutable pointer)
      └─ manifest.json  (sha256:abc...)
          ├─ config: sha256:def...
          │   { "Env": [...], "Cmd": [...],
          │     "RootFS": {"type": "layers",
          │     "diff_ids": [sha256:l1, ...]}}
          ├─ layer: sha256:l1...  (base OS)
          ├─ layer: sha256:l2...  (runtime)
          └─ layer: sha256:l3...  (app code)
```

**OVERLAYFS LAYER MERGE AT RUNTIME:**

```
Layer 3 (top, app code)    <- upperdir (writable)
Layer 2 (runtime)
Layer 1 (base OS, bottom)  <- lowerdir (read-only)
              |
              v overlayfs merge
              |
Unified view: / (container sees merged filesystem)
```

**WHITEOUT FILES (layer deletion):**

```
Layer 2 adds: .wh.secret.txt
-> Whiteout file signals: hide secret.txt from Layer 1
-> secret.txt is still in Layer 1 blob in the registry
-> It is just hidden from the container's filesystem view
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Image Pull):**

```
docker pull / containerd pull myapp:v1.0
  |
  v
GET /v2/myapp/manifests/v1.0  (resolve tag)
  |         ← YOU ARE HERE
  v
Fetch manifest.json by digest
  |
  v
For each layer blob in manifest:
  HEAD /v2/myapp/blobs/<digest>
  (skip if already in local cache)
  GET /v2/myapp/blobs/<digest>
  (decompress + store in content store)
  |
  v
Fetch config blob
  |
  v
Create overlayfs snapshot from layers
Container ready to start
```

**FAILURE PATH:**
A layer blob is corrupted in transit (SHA-256 mismatch). containerd
rejects the blob and retries. If retries fail, the pull fails with
`unexpected EOF` or `digest mismatch`. The container cannot start with
a corrupted image.

**WHAT CHANGES AT SCALE:**
At scale, a registry serving 10,000 pull requests per hour becomes
the critical path for pod startup latency. Layer caching on nodes
(containerd content store) is essential. An image pull time of 30s for
a cold pull must be reduced via registry mirrors, node-local caches,
or lazy-loading (eStargz, SOCI snapshotter).

---

### 💻 Code Example

```bash
# Inspect OCI image structure directly
# Pull and examine manifest
docker manifest inspect myapp:v1.0

# OR use skopeo (works without Docker daemon)
skopeo inspect --raw docker://myapp:v1.0 | python3 -m json.tool

# Example manifest output:
# {
#   "schemaVersion": 2,
#   "mediaType": "application/vnd.oci.image.manifest.v1+json",
#   "config": {
#     "digest": "sha256:def...",
#     "size": 7023
#   },
#   "layers": [
#     {"digest": "sha256:l1...", "size": 12345678},
#     {"digest": "sha256:l2...", "size": 23456789}
#   ]
# }

# Inspect image config
skopeo inspect docker://myapp:v1.0 | jq '{
  Env: .Env,
  Cmd: .Cmd,
  WorkingDir: .WorkingDir,
  Layers: .RootFS.Layers
}'

# View layer sizes (Dockerfile layer analysis)
docker image history myapp:v1.0 --no-trunc

# Export an OCI image to tarball for inspection
docker save myapp:v1.0 | tar -xv -C /tmp/image-inspect/
ls /tmp/image-inspect/
# blobs/   index.json   oci-layout
```

```bash
# Verify image digest matches expected value
# (detect tampering or corruption)
DIGEST=$(docker inspect --format='{{.Id}}' myapp:v1.0)
echo "Image digest: $DIGEST"

# Pin a deployment to a specific digest
docker pull myapp:v1.0
DIGEST=$(
    docker inspect --format='{{index .RepoDigests 0}}' myapp:v1.0)
echo "Deploy with: $DIGEST"
# myapp@sha256:abc123...
```

**How to test / verify correctness:**

```bash
# Verify OCI compliance of an image
# Install and run oci-image-tool
oci-image-tool validate --type image /tmp/image-inspect/

# Verify layer deduplication works
# Build two images sharing a base layer
docker build -t service-a -f Dockerfile.a .
docker build -t service-b -f Dockerfile.b .
# Both use same FROM base - only one copy stored locally
docker system df  # check image storage
```

---

### ⚖️ Comparison Table

| Format | Version | Manifest | Config | Layer | Registry API |
|---|---|---|---|---|---|
| Docker Image v1 | Pre-2017 | JSON in layer | In layer tarball | tar.gz | Docker Registry v2 |
| Docker Image v2 | 2016-2017 | Separate JSON | Separate JSON | tar.gz | Docker Registry v2 |
| OCI Image v1.0 | 2017 | Separate JSON | Separate JSON | tar.gz | OCI Distribution Spec |
| OCI Image v1.1 | 2023 | + Referrers API | Same | Same + zstd | OCI Distribution Spec v1.1 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Deleting a file in a Dockerfile removes it from the image" | A file deleted in a later layer has a whiteout entry hiding it, but the original file blob still exists in the registry. The image size includes the original layer. Use multi-stage builds to truly exclude files from the final image. |
| "Image tags are stable references" | Tags are mutable pointers to manifests. `myapp:latest` can point to a different manifest after a push. Only digest references (`myapp@sha256:...`) are immutable. |
| "A new CMD in Dockerfile creates a new layer" | CMD, ENV, LABEL, and EXPOSE are stored in the image config blob, not in filesystem layers. They do not add to the image filesystem size. |
| "OCI images require Docker to build" | OCI images can be built by Buildah, Kaniko, BuildKit, or ko. Docker is one builder, not the only one. The output of any compliant builder can be pushed to any OCI registry. |
| "Larger base images are always worse" | A distroless image with outdated packages may have more CVEs than a larger Alpine image with current packages. Size and vulnerability count are separate concerns. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Sensitive Data Leaked in Lower Layer**
**Symptom:** Security scan finds secrets (API keys, certificates) in
a container image layer that the developer thought was deleted.

**Root Cause:** A `RUN` instruction added a secret file; a later `RUN`
deleted it. The file is hidden by a whiteout in the upper layer but
still present in the lower layer's blob in the registry.

**Diagnostic:**

```bash
# Export image and inspect all layers
docker save myapp:v1.0 | tar xv -C /tmp/img/
cd /tmp/img/blobs/sha256/

# Extract each layer and search for secrets
for blob in *; do
  tar tz -f $blob 2>/dev/null | grep -i "secret\|key\|cert"
done
```

**Fix:** Rebuild the image from scratch using multi-stage build, never
adding the secret to any intermediate layer. Use `--secret` BuildKit
flag for build-time secrets (never persisted to layers).

**Prevention:** Use BuildKit secrets mount (`RUN --mount=type=secret`)
for all secrets used during build. Never copy secret files into the
image filesystem.

---

**Failure Mode 2: Image Pull Latency Causing Pod Start Timeout**
**Symptom:** Pods fail to start with `ImagePullBackOff`. Events show
`context deadline exceeded` during image pull. The image is large (2 GB).

**Root Cause:** Cold pull of a large image on a node that does not
have the layers cached. Registry is distant (cross-region) or slow.

**Diagnostic:**

```bash
# Check image pull time
time crictl pull myapp:v1.0

# Check registry response time
curl -o /dev/null -w "%{time_total}s\n" \
  https://registry.example.com/v2/myapp/manifests/v1.0

# Check node disk I/O during pull
iostat -x 1 5
```

**Fix:** Use a regional registry mirror or ECR pull-through cache. Use
lazy loading (eStargz or SOCI snapshotter) to start containers before
the full image is pulled. Reduce image size via multi-stage builds.

**Prevention:** Monitor image layer sizes in CI. Alert on images
exceeding 500 MB. Use registry mirrors for all production clusters.

---

**Failure Mode 3: Tag Mutation Causing Deployment Inconsistency**
**Symptom:** Two identical deployments behave differently. Investigation
reveals the `:latest` tag was pushed to with a new image between the
two deployments.

**Root Cause:** `imagePullPolicy: Always` with a mutable tag causes
different nodes to pull different versions of the same tag.

**Diagnostic:**

```bash
# Check what image SHA each pod is actually running
kubectl get pods -o json | jq '
  .items[] | {
    name: .metadata.name,
    imageID: .status.containerStatuses[].imageID
  }'

# Multiple different SHA256 values for the "same" image
# confirms tag mutation between pulls
```

**Fix:** Pin production deployments to image digests. Set
`imagePullPolicy: IfNotPresent` with digest-pinned images.

**Prevention:** CI pipeline outputs digest; CD pipeline uses digest
in manifests. Mutable tags (`latest`, `main`) are never used in
production Kubernetes manifests.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-006 - Docker Image]] - image fundamentals
- [[CTR-009 - Docker Layer]] - layer model and caching
- [[CTR-020 - OCI Standard]] - OCI overview

**Builds On This (learn these next):**

- [[CTR-049 - Container Image Strategy at Scale]] - strategy for managing images

**Alternatives / Comparisons:**

- [[CTR-040 - Docker BuildKit]] - the build tool that creates OCI images
- [[CTR-052 - Container Runtime Internals (runc, containerd)]] - how OCI images are consumed at runtime

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Content-addressable image format    │
│ PROBLEM     │ Format fragmentation pre-2015       │
│ KEY INSIGHT │ Digest = name + integrity check     │
│ USE WHEN    │ Understanding image pull, layer ops  │
│ AVOID WHEN  │ N/A - always the underlying model   │
│ TRADE-OFF   │ Layer immutability vs. secret leaks │
│ ONE-LINER   │ manifest + config + layers by SHA256│
│ NEXT EXPLORE│ CTR-049 Image Strategy, CTR-052 Runtime│
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. An OCI image = manifest + config + layers, all stored as SHA-256
   content-addressed blobs enabling automatic deduplication.
2. Tags are mutable; digests are immutable - use digest pinning in
   production for reproducible, tamper-evident deployments.
3. Files deleted in a later layer are hidden but not removed from the
   registry - secrets added to any layer are permanent until image
   is rebuilt from scratch.

**Interview one-liner:**
"An OCI image is a content-addressable artifact: manifest references
config and layer blobs by SHA-256 digest; digest naming enables automatic
deduplication, integrity verification, and immutable references; tags
are mutable pointers to manifests and should never be used for
production pinning."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Content-addressable storage solves deduplication and integrity as
emergent properties of naming by content hash. When the identifier of
a piece of data is derived from the data itself (SHA-256), you get
deduplication (same content = same identifier = stored once), integrity
(content that doesn't match its identifier is rejected), and immutability
(changing content changes the identifier) for free. Git, BitTorrent,
IPFS, and OCI images all use this principle.

**Where else this pattern appears:**

- **Git object storage:** Commits, trees, and blobs are named by
  SHA-1/SHA-256 of their content. The same file in two branches is
  stored once. Changing one byte creates a new object with a new hash.
  Git's integrity is inherent in its content-addressable model.
- **Package managers:** npm lockfiles and cargo.lock store package
  SHA-256 hashes. Installing from a lockfile verifies the content hash,
  preventing supply chain attacks where a package version is silently
  replaced.
- **Merkle trees (blockchains, Cassandra):** Distributed systems use
  content-addressed Merkle trees to verify data consistency across
  nodes without transmitting the full data.

---

### 💡 The Surprising Truth

Docker's original image format (v1, pre-2017) stored image metadata
inside the layer tarballs themselves - meaning two images with identical
filesystem content but different metadata (different author labels, for
example) stored different layer blobs and could not share layers in
the registry. This subtle design flaw meant that Docker's own layer
deduplication worked only for images with identical parent image
relationships. The OCI Image Spec v1 fixed this by separating the image
config from the layer content - metadata and filesystem are now stored
as separate blobs. This single architectural change made cross-image
layer deduplication truly universal and reduced registry storage for
large organisations by 40-60%.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** An OCI image has 5 layers. A container
is started from this image. The container writes a 100 MB file to its
filesystem. When the container is stopped, the image is unmodified (still
5 layers). Where did the 100 MB file go? What mechanism makes the
image immutable while the container can write?
*Hint:* overlayfs uses a writable upperdir per container instance.
The image's read-only layers are lowerdir. The container's writes go
to upperdir. The image blobs are never modified. What happens to the
upperdir when the container is removed?

**Q2 (C - Design Trade-off):** A DevOps team wants to attach a
vulnerability report (SBOM) to every container image in the registry
without modifying the image manifest (to avoid changing the image
digest). OCI Image Spec v1.1 provides a "referrers API" for this. What
would be the alternative (pre-v1.1) approach, and what are the
trade-offs?
*Hint:* Pre-v1.1, teams stored SBOMs as separate tagged images
(e.g., `myapp:v1.0-sbom`) with no formal link to the source image.
What are the discovery, association, and integrity problems with this
approach vs. the referrers API?

**Q3 (A - System Interaction):** A container registry uses the OCI
Distribution Spec. A client sends `GET /v2/myapp/manifests/v1.0`.
The registry returns the manifest. The client then sends HEAD requests
for each layer blob to check if they are already cached. One layer
(50 MB, sha256:abc) is already present on the client. The pull skips
that layer. Later, the registry operator deletes the blob sha256:abc
from the registry (storage cleanup). What happens to existing containers
running from images that reference sha256:abc?
*Hint:* Running containers use their local overlayfs snapshots (already
pulled). They do not need the registry blob. But what happens when a new
node tries to schedule a pod using the same image that references the
deleted blob?