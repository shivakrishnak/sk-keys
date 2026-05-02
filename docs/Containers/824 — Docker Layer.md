---
layout: default
title: "Docker Layer"
parent: "Containers"
nav_order: 824
permalink: /containers/docker-layer/
number: "0824"
category: Containers
difficulty: ★★☆
depends_on: Docker Image, Dockerfile, OCI Standard, Container
used_by: Multi-Stage Build, Distroless Images, Docker BuildKit, Image Scanning
related: Docker Image, Dockerfile, Multi-Stage Build, Docker BuildKit, OCI Standard
tags:
  - containers
  - docker
  - intermediate
  - architecture
  - performance
---

# 824 — Docker Layer

⚡ TL;DR — A Docker layer is an immutable, content-addressed filesystem diff — each Dockerfile instruction that changes the filesystem creates one, and they stack to form the complete image.

| #824 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Docker Image, Dockerfile, OCI Standard, Container | |
| **Used by:** | Multi-Stage Build, Distroless Images, Docker BuildKit, Image Scanning | |
| **Related:** | Docker Image, Dockerfile, Multi-Stage Build, Docker BuildKit, OCI Standard | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without layering, every Docker image would be a monolithic tarball — a single compressed archive of the entire filesystem. A `node:20-alpine` base image is 180 MB. Your application adds 20 MB of code on top. If images were monolithic, every pull of `myapp:1.1` after `myapp:1.0` would download the full 200 MB again — because there is no way to say "reuse the 180 MB base, only download the 20 MB that changed." Across 10 hosts pulling 50 different Node.js services, this would mean terabytes of redundant network traffic and gigabytes of wasted storage.

**THE BREAKING POINT:**
Container ecosystems need to ship application updates fast. If every update required re-downloading unchanged base OS and runtime layers, container deployments would be impractically slow.

**THE INVENTION MOMENT:**
This is exactly why Docker images are built from layers — each Dockerfile step that modifies the filesystem creates an immutable layer. Unchanged layers are never transferred or stored twice. Only the diff between versions travels over the network.

---

### 📘 Textbook Definition

A **Docker layer** is an immutable, read-only filesystem snapshot representing the filesystem changes made by a single Dockerfile instruction (or group of instructions). Each layer is a compressed tar archive of file additions, modifications, and deletions, identified by its SHA256 content digest. Layers are stacked using a union filesystem (OverlayFS on modern Linux) to produce a merged filesystem view. A running container adds one additional writable layer on top of the read-only image layers. Because layers are content-addressed, identical layers are stored once and referenced many times — enabling sharing between any images that have a common Dockerfile ancestry. Layer cache invalidation: when any layer changes, all subsequent layers in the build must be rebuilt.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Docker layer is one filesystem change checkpoint — stack them and you get a complete image; change one and Docker only rebuilds everything after it.

**One analogy:**
> A Docker image is like a stack of transparent acetate sheets. Each sheet (layer) adds its elements to the image you see. The base sheet has the OS. The next sheet adds the runtime. The top sheet adds your application code. When you shine a light through all sheets (run a container), you see the combined picture. To update just the application code, you only replace the top sheet — the OS and runtime sheets underneath are unchanged, undownloaded, and reused.

**One insight:**
The cache invalidation rule is the single most impactful thing to understand about layers. Once Docker sees a layer has changed (or cannot use the cache for it), it rebuilds ALL subsequent layers. This is why instruction order in a Dockerfile is not arbitrary — it is a performance decision. Put slow, rarely-changing operations first. Put fast, frequently-changing operations last.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each layer records only the filesystem changes made by its instruction — not the whole filesystem.
2. A layer's SHA256 is its identity and integrity guarantee — same hash = same bytes = same result, always.
3. Layers are ordered — the union mount presents the top-most version of each file.

**DERIVED DESIGN:**

**Layer creation:**
Every `RUN`, `COPY`, `ADD` instruction in a Dockerfile that results in filesystem changes creates a new layer. Non-filesystem instructions (`ENV`, `EXPOSE`, `LABEL`, `CMD`, `ENTRYPOINT`, `WORKDIR`) do not create layers.

**Union filesystem mechanics:**
OverlayFS presents 5 layers as one unified filesystem by:
- Starting with the lowest layer's files
- Overlaying each subsequent layer's additions and modifications
- Marking deletions as "whiteout files" (`.wh.*` entries that hide the lower layer's file)

**Layer cache mechanics:**
Docker caches layer output during `docker build`. For each instruction:
1. Is the instruction identical to the previous build? (exact string match)
2. Is the base image the same? (same layer SHA256)
3. For `COPY`/`ADD`: are the source files unchanged? (hash comparison)
If all three: cache hit, layer reused. Otherwise: cache miss, layer rebuilt, all subsequent layers invalidated.

**THE TRADE-OFFS:**
**Gain:** Pull only changed layers (fast updates); storage deduplication; incremental build caching.
**Cost:** Whiteout files do not shrink the image — a layer that deletes files is recorded as a whiteout, but the original layer is still present and occupies space. Over-layering (many small layers) adds OverlayFS overhead. Layer cache is invalidated by any change, including a comment in a preceding `RUN`.

---

### 🧪 Thought Experiment

**SETUP:**
A Node.js Dockerfile has two orderings:
- **Version A:** `COPY . .` then `RUN npm install`
- **Version B:** `COPY package.json .` then `RUN npm install` then `COPY . .`

The developer changes one line in `app.js` and runs `docker build`.

**WHAT HAPPENS WITH VERSION A:**
`COPY . .` copies ALL source files, including the changed `app.js`. Docker detects the `COPY` source has changed → cache miss on this layer → ALL subsequent layers rebuild, including `RUN npm install`. npm installs all packages again from scratch. Layer size: 200 MB. Build time: 3 minutes.

**WHAT HAPPENS WITH VERSION B:**
`COPY package.json .` — `package.json` is unchanged → CACHE HIT.
`RUN npm install` — previous layer cached → CACHE HIT. 0 seconds.
`COPY . .` copies changed `app.js` → cache miss on this layer only. Only the "copy source code" layer is rebuilt. Layer size: 2 MB. Build time: 8 seconds.

**THE INSIGHT:**
Layer ordering determines build speed. The developer who understands this ships 22× faster (8 seconds vs 3 minutes) with identical results. This is not a micro-optimisation — it is a fundamental design principle.

---

### 🧠 Mental Model / Analogy

> Docker layers are like Git commits for the filesystem. Each commit (layer) records the diff from the previous state. The full filesystem is the sum of all commits applied in order. If you change a commit in the middle, all commits that built on top of it must be re-applied (invalidated). The SHA256 of a layer is like a commit hash — it uniquely identifies the content. Just as `git pull` only fetches new commits, `docker pull` only fetches new layers.

**Mapping:**
- "Git commit hash" → layer SHA256 digest
- "Git diff between commits" → filesystem changes in one layer (tar archive)
- "git log" → `docker history image_name`
- "Git remote (remote object store)" → Container registry (layer store)
- "Cache invalidation chain" → when a commit changes, all subsequent commits in a branch must be re-made

**Where this analogy breaks down:** Git diffs are bidirectional (you can see what was removed and restore it). Docker layer whiteout files "hide" deleted files but the original data is still present in earlier layers — you cannot truly reclaim space from a layer that adds and then removes data in separate instructions.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Imagine building a cake layer by layer. The first layer is the sponge, the second layer is the cream, the top is the fruit. Each layer adds something new. Docker images work the same way — each layer adds files. When you update the recipe, you only replace the layers that changed.

**Level 2 — How to use it (junior developer):**
Understanding layers matters for build speed and image size. To see your image's layers: `docker history myapp:1.0`. To minimise an image: put `npm install` or `pip install` before `COPY . .` so code changes don't invalidate the dependency installation layer. To see what's in each layer: use `dive` tool or `docker inspect`.

**Level 3 — How it works (mid-level engineer):**
During `docker build`: BuildKit processes each instruction group. For a `RUN` instruction, it runs the command in a container derived from the current layer state, captures the filesystem diff (using OverlayFS lower/upper layer separation), compresses it as a tar.gz, computes its SHA256, and stores it in the build cache keyed by `(parent_layer_sha256, instruction_string, build_args)`. For `COPY`, the cache key includes the hash of all source files. At runtime, containerd mounts the layers using OverlayFS: `lower` dirs = all read-only image layers; `upper` dir = container's writable layer; `merged` dir = the unified view the container process sees.

**Level 4 — Why it was designed this way (senior/staff):**
The content-addressed, immutable layer design was inspired by academic append-only filesystems (Btrfs COW approach) and Git. Docker's choice to use a union filesystem (initially AUFS, now OverlayFS) rather than a fully separate filesystem per layer was an early performance compromise — OverlayFS has known limitations (max 128 layers in early versions, inode exhaustion issues with some workloads). Modern alternative: image mounting via fuse-overlayfs or Snapshotter plugins (in containerd) allows registries to use storage-optimised backends (zfs, btrfs) instead of OverlayFS. BuildKit's content-addressable build cache is more sophisticated than the original Docker build cache — it caches at a more granular level and supports garbage collection by reference count, not age.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  LAYER CREATION DURING BUILD                             │
│                                                          │
│  Dockerfile instruction executed in temp container:      │
│  ┌────────────────────────────────────────────────┐     │
│  │ State before: /etc/os, /usr/bin/node, ...      │     │
│  │ RUN npm install                                │     │
│  │ State after:  + /app/node_modules/ (added)     │     │
│  └────────────────────────────────────────────────┘     │
│  Diff (changes only) → compressed tar.gz                 │
│  SHA256(tar.gz) → layer digest (e.g. sha256:3f8a...)    │
│  Stored in layer cache, referenced in manifest          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  OVERLAYFS MOUNT AT RUNTIME                              │
│                                                          │
│  /var/lib/docker/overlay2/                              │
│    <Layer1_SHA> /  ← node:20-alpine base (read-only)    │
│    <Layer2_SHA> /  ← /app/node_modules (read-only)      │
│    <Layer3_SHA> /  ← /app/*.js (read-only)              │
│    <Container_upper> /  ← writable layer (empty at start│
│                                                          │
│  OverlayFS merges into:                                  │
│  /merged/  ← container sees complete filesystem here    │
│                                                          │
│  Container writes to /merged/app/logs/app.log:          │
│  1. OverlayFS checks: file in lower layers (read-only)  │
│  2. Copies file up to <Container_upper>/app/logs/       │
│  3. Subsequent writes go to upper layer directly        │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Dockerfile instruction → BuildKit executes → filesystem diff
→ [LAYER created ← YOU ARE HERE] → compressed + content-hashed
→ stored in local layer cache → referenced in image manifest
→ pushed to registry (only non-existent layers transferred)
→ pulled on deploy (only missing layers downloaded)
→ OverlayFS stacks layers → container starts
```

**FAILURE PATH:**
```
Layer pull fails (network error mid-download)
→ incomplete layer not stored (SHA256 verification prevents use)
→ pull retried automatically
→ observable: "layer already exists" on retry indicates resume
```

**WHAT CHANGES AT SCALE:**
At 1,000 container hosts, a single large image layer (e.g., 500 MB model weights) pulled simultaneously by all nodes overwhelms the registry. Solutions: (1) layer pre-warming DaemonSet pods pull images before they are scheduled; (2) pull-through registry cache placed in the same datacenter/region; (3) lazy loading (eStargz format / Seekable OCI) starts containers immediately, streaming needed layers on-demand.

---

### 💻 Code Example

Example 1 — View layers and their sizes:
```bash
# See all layers with size and command
docker history myapp:1.0
# CREATED BY column shows Dockerfile instruction  
# SIZE column shows layer size (0B = no filesystem change)
# <missing> in IMAGE column = base image intermediate layers

# Interactive layer explorer
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive myapp:1.0
```

Example 2 — Demonstrate cache invalidation:
```dockerfile
# Layer 1: base (cached unless FROM changes)
FROM node:20-alpine

# Layer 2: only rebuilt if package.json or package-lock.json change
COPY package.json package-lock.json ./
RUN npm ci --only=production
# ^ This 200MB layer is CACHED if deps haven't changed

# Layer 3: rebuilt on every code change (small)
COPY src/ ./src/

# Build once: all layers built (cold cache)
# Build twice (code change only): layers 1+2 cached, only 3 rebuilt
```

Example 3 — Combining RUN commands to avoid bloat:
```dockerfile
# BAD: separate layers, apt cache left in layer 1
RUN apt-get update                     # Layer A: 50 MB
RUN apt-get install -y curl wget       # Layer B: 40 MB
RUN rm -rf /var/lib/apt/lists/*        # Layer C: removes files
# Total: 90 MB (layer C cannot remove layer A's data from the image)

# GOOD: single layer, cleanup in same RUN → truly smaller image
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl wget \
    && rm -rf /var/lib/apt/lists/*
# Single layer: ~15 MB (apt cache removed within same OverlayFS snapshot)
```

---

### ⚖️ Comparison Table

| Layer Characteristic | Impact | Management |
|---|---|---|
| Small, frequent layers | Cache granularity good; OverlayFS overhead grows | Merge related `RUN` instructions |
| Large single layer | Cache is all-or-nothing; pull is large | Split into stable + changing parts where possible |
| Shared base layer | Pulled once, used by N images | Use common base images across services |
| Build-only tools in final image | Bloated production image | Use multi-stage builds |
| Sensitive data in layer | Always visible in history | Never `COPY` secrets; use build secrets or runtime env vars |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Deleting a file in a later layer reduces image size | The deletion creates a whiteout entry in the new layer; the original file data remains in the earlier layer. Total image size is not reduced. Use multi-stage builds to remove files. |
| More layers = slower container start | OverlayFS handles up to 128 layers efficiently; container start time is dominated by the application startup, not layer count |
| COPY and RUN always create layers | Only filesystem-modifying instructions create layers. COPY always does. RUN always does. But ENV, EXPOSE, LABEL, CMD, WORKDIR do not add filesystem layers. |
| The layer cache always works correctly across machines | Layer cache is local to the host. A different CI runner does not have the cache. BuildKit remote caches (registry-based, S3-based) solve this. |
| All layers must be pulled before a container starts | With lazy loading formats (eStargz), a container can start while remaining layers are streamed in the background |

---

### 🚨 Failure Modes & Diagnosis

**Secrets Exposed in Layer History**

**Symptom:** `docker history --no-trunc myapp` shows API key in `RUN npm config set //registry.npmjs.org/:_authToken=secret123` command.

**Root Cause:** Secrets passed via RUN command are persisted in the layer metadata, visible to anyone with access to the image.

**Diagnostic Command / Tool:**
```bash
# Inspect layer commands — reveals secrets in RUN instructions
docker history --no-trunc myapp:1.0 | grep -i "token\|password\|secret\|key"
```

**Fix:** Use BuildKit `--secret` mount (secret is not stored in any layer):
```dockerfile
RUN --mount=type=secret,id=npmrc,dst=/root/.npmrc npm install
```
Build with: `docker build --secret id=npmrc,src=.npmrc .`

**Prevention:** Never pass secrets in ENV, RUN, or COPY instructions. Secrets must either be BuildKit secrets (build time) or runtime environment variables.

---

**OverlayFS "Too Many Open Files" Error**

**Symptom:** Container fails to start with `too many layers` or underlying OverlayFS errors on older kernels.

**Root Cause:** Images with >128 layers on older kernels hit OverlayFS layer limit. Common in images built with many small RUN commands.

**Diagnostic Command / Tool:**
```bash
docker history myapp | wc -l
# If > 100 layers → approaching OverlayFS limits
```

**Fix:** Squash layers during build: `docker build --squash myapp .` or use multi-stage build to produce a final image with few layers.

**Prevention:** During Dockerfile authoring, count layers. Keep under 30 layers for production images. Combine related `RUN` instructions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker Image` — a Docker image is the ordered stack of layers
- `Dockerfile` — the build specification that creates layers

**Builds On This (learn these next):**
- `Multi-Stage Build` — uses multiple build stages to create minimal final images
- `Docker BuildKit` — the modern build engine with advanced caching and secret management

**Alternatives / Comparisons:**
- `OCI Standard` — defines the layer format; any OCI-compatible tool uses the same layer format
- `eStargz (Seekable OCI)` — optimised layer format for lazy loading, used in Kubernetes image streaming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Immutable filesystem diff per Dockerfile │
│              │ instruction, stacked via OverlayFS       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Re-downloading unchanged base layers on  │
│ SOLVES       │ every image update wastes time + storage │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cache invalidation: change any layer →   │
│              │ all subsequent layers must be rebuilt    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — layers are automatic; optimise  │
│              │ Dockerfile order for maximum cache reuse │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid separate RUN for cleanup (combine) │
│              │ Never store secrets in any layer         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Granular caching + sharing vs whiteout   │
│              │ can't recover disk from deleted content  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Git commits for filesystems — change    │
│              │  one, rebuild only what follows"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dockerfile → Multi-Stage Build →         │
│              │ Docker BuildKit                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A security scanner finds that your production Docker image contains a file `/etc/aws/credentials` with real AWS credentials. Your Dockerfile has a `RUN rm -rf /etc/aws` step near the end. The security scanner claims the credentials are still in the image. Explain exactly why this is true despite the `RUN rm -rf` instruction, and design the complete remediation — both for the immediate incident (the credentials must be revoked) and for the Dockerfile structure going forward (credentials must never appear in any layer).

**Q2.** Your team's BuildKit CI build cache is not being reused between builds — every `RUN npm install` runs from scratch even when `package.json` has not changed. You use a remote BuildKit cache in an S3 bucket. Describe the exact sequence of events in a BuildKit cache hit: what cache key is computed, where it's stored, how it's retrieved, and what condition (other than changing `package.json`) would cause a false cache miss that a developer might not expect.

