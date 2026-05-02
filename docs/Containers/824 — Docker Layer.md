---
layout: default
title: "Docker Layer"
parent: "Containers"
nav_order: 824
permalink: /containers/docker-layer/
number: "824"
category: Containers
difficulty: ★★☆
depends_on: "Docker Image, Docker, Dockerfile"
used_by: "Docker Build Context, Multi-Stage Build, Container Registry"
tags: #containers, #docker, #layers, #overlay2, #caching, #build-optimization
---

# 824 — Docker Layer

`#containers` `#docker` `#layers` `#overlay2` `#caching` `#build-optimization`

⚡ TL;DR — A **Docker layer** is an immutable, content-addressed filesystem diff created by each Dockerfile instruction (`RUN`, `COPY`, `ADD`). Layers are cached, reused across images, and stacked via overlay2 filesystem. Build optimization = order Dockerfile instructions from least-changing to most-changing to maximize cache hits and minimize rebuild time.

| #824            | Category: Containers                                        | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Docker Image, Docker, Dockerfile                            |                 |
| **Used by:**    | Docker Build Context, Multi-Stage Build, Container Registry |                 |

---

### 📘 Textbook Definition

**Docker layer**: each instruction in a Dockerfile that modifies the filesystem (`RUN`, `COPY`, `ADD`) creates a new, immutable layer. The layer is stored as a compressed tar archive and identified by its SHA256 content hash. Layers are stacked during container runtime using a union filesystem (typically **overlay2** on Linux) to present a merged view of all layers as a single filesystem. Key properties: (1) **Immutability** — once created, a layer never changes; a new build creates new layers; (2) **Content-addressing** — a layer's identity is its SHA256 hash; identical content → same hash → same layer; (3) **Caching** — Docker caches each layer; if the instruction and all preceding layers are unchanged, the cached layer is reused without re-execution; (4) **Sharing** — multiple images sharing the same layer store it once on disk (on the registry and on each host); (5) **Incremental push/pull** — only layers not already present at the destination are transferred. The **writable layer** added to a running container is also implemented as an overlay layer, but it is ephemeral — deleted when the container is removed.

---

### 🟢 Simple Definition (Easy)

Each `RUN`, `COPY`, or `ADD` instruction in a Dockerfile creates a new layer — a snapshot of what changed in the filesystem. Like git commits: each commit records the diff from the previous state. Layer 1: Ubuntu base files. Layer 2: added Python. Layer 3: added your app's libraries. Layer 4: added your app's source code. Docker caches each layer. If only your source code changes (layer 4), Docker rebuilds only layer 4 — layers 1, 2, 3 are reused from cache. This makes builds fast.

---

### 🔵 Simple Definition (Elaborated)

Layers matter for two reasons:

**Build performance**: if your `RUN npm install` (expensive: downloads 200MB of packages) is in layer 3, and only your source code (layer 4) changes, Docker reuses the cached npm install layer. A 3-minute npm install becomes 0.1 seconds. Wrong ordering (COPY all source → RUN npm install) means npm install re-runs on every code change.

**Image size**: every `RUN` creates a new layer. If you install a package, run a build script, then delete the build artifacts — but in separate `RUN` commands — the intermediate layers contain the deleted files. They're still in the image. Combine cleanup with installation in one `RUN` command:

```dockerfile
RUN apt-get update && apt-get install -y gcc && make build && apt-get remove -y gcc && rm -rf /var/cache/apt
```

Or use multi-stage builds to discard build layers entirely.

---

### 🔩 First Principles Explanation

```
LAYER MECHANICS:

  Dockerfile → Layer creation:

  FROM ubuntu:22.04        → references existing layer (pulled from registry)
                             Layer ID: sha256:a8a2...  (29MB)

  RUN apt-get install -y python3
                           → executes command → filesystem diff captured
                             What changed: added /usr/bin/python3, /usr/lib/python3.11/, ...
                             Layer ID: sha256:b3c4...  (45MB uncompressed)

  COPY requirements.txt /app/
                           → copies file → filesystem diff
                             Layer ID: sha256:d5e6...  (1KB)

  RUN pip install -r /app/requirements.txt
                           → installs packages → filesystem diff
                             Layer ID: sha256:f7a8...  (180MB)

  COPY src/ /app/src/      → copies source code → filesystem diff
                             Layer ID: sha256:b9c0...  (2MB)

LAYER CACHE INVALIDATION:

  Build 1 (initial): all layers executed; cache populated
  Build 2 (only src/ changed):

  FROM ubuntu:22.04         → sha256:a8a2... ✅ CACHE HIT
  RUN apt-get install python3 → sha256:b3c4... ✅ CACHE HIT
  COPY requirements.txt     → sha256:d5e6... ✅ CACHE HIT (file unchanged)
  RUN pip install -r req.txt → sha256:f7a8... ✅ CACHE HIT
  COPY src/ /app/src/       → sha256:NEW... ❌ CACHE MISS (source changed)
  → Build time: ~3 seconds (only last layer rebuilt)

  Build 3 (requirements.txt changed):
  FROM ubuntu:22.04         → ✅ CACHE HIT
  RUN apt-get install python3 → ✅ CACHE HIT
  COPY requirements.txt     → ❌ CACHE MISS (file changed)
  RUN pip install -r req.txt → ❌ MUST RE-RUN (dependencies on changed layer)
  COPY src/ /app/src/       → ❌ MUST RE-RUN
  → Build time: ~3 minutes (pip install re-runs)

  KEY RULE: once a layer cache is invalidated, ALL subsequent layers
  must be rebuilt (no partial cache after a miss)

OVERLAY2 FILESYSTEM (runtime):

  How the container sees a unified filesystem from stacked layers:

  Lower layers (read-only, bottom to top):
  Layer 1: {/bin/bash, /usr/lib/libc.so, /etc/passwd, ...}
  Layer 2: {/usr/bin/python3, /usr/lib/python3.11/, ...}
  Layer 3: {/app/requirements.txt}
  Layer 4: {/usr/local/lib/python3.11/site-packages/flask/, ...}
  Layer 5: {/app/src/main.py, /app/src/models.py, ...}

  Upper layer (writable, container-specific):
  Container A: {/app/logs/access.log, /tmp/session.tmp}
  Container B: {/app/logs/access.log (different content), /var/cache/...}

  Merged view (what each container process sees):
  /bin/bash, /usr/bin/python3, /app/src/main.py, /app/logs/access.log, ...

  COPY-ON-WRITE:
  Container modifies /etc/hosts (from layer 1):
  1. Copy /etc/hosts from layer 1 to upper (writable) layer
  2. Container writes to upper layer copy
  3. Layer 1 /etc/hosts: unchanged
  4. Other containers: unaffected

LAYER SIZE PITFALL:

  ❌ WRONG: delete in separate RUN command
  RUN apt-get install -y gcc     [Layer A: +30MB]
  RUN make build                 [Layer B: +50MB of compiled artifacts]
  RUN rm -rf /tmp/build artifacts [Layer C: "removes" files, but they're still in Layer B!]

  Total image: 80MB of "deleted" files still in layers A+B

  ✅ CORRECT: combine in single RUN to eliminate intermediate files
  RUN apt-get install -y gcc && \
      make build && \
      cp build/output /app/binary && \
      apt-get remove -y gcc && \
      rm -rf /tmp/* /var/cache/apt

  Single layer: only final state captured → garbage files never written to any layer

  EVEN BETTER: multi-stage build (completely eliminates build tools from final image)
  FROM ubuntu:22.04 AS builder
  RUN apt-get install gcc && make build

  FROM scratch AS final
  COPY --from=builder /app/binary /app/binary  ← ONLY the binary; gcc/source never in final
```

---

### ❓ Why Does This Exist (Why Before What)

Without layers, every Docker image would be a monolithic tar archive: rebuild = reconstruct the entire filesystem every time (minutes per build, gigabytes per image). Layers enable: (1) incremental builds (rebuild only changed layers); (2) storage efficiency (shared base layers stored once); (3) incremental registry transfers (push/pull only changed layers). The content-addressable design (SHA256) makes layer deduplication automatic: identical content → same hash → stored and transferred once.

---

### 🧠 Mental Model / Analogy

> **Layers are like an overhead transparency projector stack**: each transparency (layer) shows only what was added or changed from the previous one. The combined image is all transparencies stacked — the top one shows what's visible. If you want to draw on a transparency (container write): you place a new blank transparency on top and draw there — the lower transparencies remain unchanged. Other viewers using the same stack of transparencies: they also get a fresh blank top layer — they see the same base image but their writes don't affect each other.

---

### ⚙️ How It Works (Mechanism)

```
BUILDKIT (Docker's build backend, default since 20.10):

  BuildKit improvements over legacy builder:
  - Parallel layer builds: independent stages built in parallel
  - Better cache: cache based on content hash, not just instruction order
  - Mount secrets during build (--mount=type=secret)
  - SSH agent forwarding during build (--mount=type=ssh)
  - Remote cache: export/import cache from registry (for CI)

  CI LAYER CACHING:
  # GitHub Actions: cache Docker layers between runs
  - name: Set up Docker Buildx
    uses: docker/setup-buildx-action@v3

  - name: Build and push with cache
    uses: docker/build-push-action@v5
    with:
      cache-from: type=gha       # restore from GitHub Actions cache
      cache-to: type=gha,mode=max  # save to GitHub Actions cache

  Result: CI builds reuse cached layers → 3-minute build → 30-second build

DOCKER HISTORY:

  docker history myapp:1.0

  IMAGE         CREATED BY                                  SIZE
  sha256:b9c0   COPY src/ /app/src/                        2.1MB
  sha256:f7a8   RUN pip install -r /app/requirements.txt  180.4MB
  sha256:d5e6   COPY requirements.txt /app/               1.0kB
  sha256:b3c4   RUN apt-get install -y python3            45.2MB
  sha256:a8a2   /bin/sh -c #(nop) FROM ubuntu:22.04       29.1MB
```

---

### 🔄 How It Connects (Mini-Map)

```
Each Dockerfile instruction → creates/references a layer
        │
        ▼
Docker Layer ◄── (you are here)
(immutable diff; content-addressed; overlay2; cached)
        │
        ├── Docker Image: ordered collection of layers
        ├── Dockerfile: instructions that generate layers
        ├── overlay2: the Linux union filesystem that merges layers at runtime
        ├── Multi-Stage Build: discards build-time layers from final image
        └── Container Registry: stores and distributes layer blobs
```

---

### 💻 Code Example

```dockerfile
# Optimized Dockerfile: order for maximum cache utilization

# Stage 1: dependency layer (rarely changes)
FROM node:18-alpine AS deps

WORKDIR /app

# Copy ONLY package files first (before source code)
# → npm ci re-runs ONLY when package*.json changes
# → source code changes don't invalidate this layer
COPY package.json package-lock.json ./
RUN npm ci --only=production    # install exact dependency tree

# Stage 2: build layer (runs on every source change)
FROM node:18-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules   # reuse installed deps
COPY . .                                              # copy source (invalidates cache here)
RUN npm run build                                     # transpile/bundle

# Stage 3: minimal final image (NO build tools, NO dev dependencies)
FROM node:18-alpine AS final

# Run as non-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy ONLY what's needed for runtime
COPY --from=deps /app/node_modules ./node_modules    # production deps only
COPY --from=builder /app/dist ./dist                 # compiled output only
COPY package.json ./

USER appuser

EXPOSE 3000
CMD ["node", "dist/server.js"]

# Final image: ~120MB (no build tools, no source, no dev deps)
# vs naive approach: ~850MB
```

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                                                                                                                                                                 |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RUN rm` removes data from the image | `RUN rm` creates a new layer that marks files as deleted (whiteout files in overlay2). The deleted files still exist in earlier layers and are included in the image size. To truly remove files, combine add+delete in one `RUN` command or use multi-stage builds.                    |
| More layers = larger image           | The number of layers has minimal impact on image size — what matters is the content of the layers. 50 tiny layers vs 1 large layer with the same content = same size. Combining layers (chaining RUN commands with `&&`) reduces size only when you're deleting intermediate artifacts. |
| Layer cache is always reliable in CI | CI runners often start fresh (no local cache). BuildKit remote cache (`--cache-from`, `--cache-to`) explicitly exports/imports the layer cache from a registry or GitHub Actions cache. Without it, every CI build rebuilds from scratch.                                               |

---

### 🔥 Pitfalls in Production

```
PITFALL: large .dockerignore file omissions

  # ❌ Missing .dockerignore → build context includes everything
  COPY . /app/
  # Includes: node_modules/ (500MB), .git/ (200MB), *.log files
  # Build context sent to Docker daemon: 700MB → slow; triggers cache misses

  # ✅ .dockerignore file (like .gitignore for Docker builds)
  node_modules/
  .git/
  *.log
  .env*           # CRITICAL: don't accidentally copy .env with secrets
  dist/           # built output; rebuilt during docker build
  coverage/       # test coverage reports
  .DS_Store

  # Result: build context: ~2MB; fast transfer; correct cache behavior

PITFALL: COPY . after RUN (kills cache for expensive step)

  # ❌ WRONG ORDER: copies all source first
  COPY . /app/              ← changes on every commit
  RUN pip install -r /app/requirements.txt  ← cache miss every build!

  # ✅ CORRECT ORDER: copy dependencies first
  COPY requirements.txt /app/   ← only changes when deps change
  RUN pip install -r /app/requirements.txt  ← cached until deps change
  COPY . /app/                  ← changes every build (but it's fast, no install)
```

---

### 🔗 Related Keywords

- `Docker Image` — ordered collection of layers forming the complete image
- `Dockerfile` — the instructions that create each layer
- `Multi-Stage Build` — uses multiple FROM stages to discard build-only layers
- `Docker Build Context` — files sent to Docker daemon; affects which layers cache correctly
- `overlay2` — Linux union filesystem merging read-only layers with writable container layer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LAYER = filesystem diff; SHA256 hash; immutable; cached │
│ CACHE: miss on any layer → all subsequent layers rebuilt│
│ ORDER RULE: rarely-changing → frequently-changing       │
│   FROM → apt/yum install → COPY deps file → RUN install │
│   → COPY source                                         │
│ CLEANUP: combine RUN + rm in one command (or multi-stage)│
│ SECRETS: never in RUN (use --mount=type=secret)         │
│ .dockerignore: exclude node_modules, .git, .env         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Docker BuildKit introduced `RUN --mount=type=cache` which creates a persistent cache directory that is NOT stored in the resulting image layer. For example: `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`. This cache persists across builds (like a local cache) but never appears in any image layer. How is this different from simply having a layer with cached packages? What operations benefit most from mount caches, and what are the constraints (does it work across different build machines in CI)?

**Q2.** Squashing layers (`docker build --squash` or `docker export` + `docker import`) combines all layers into a single layer. This can reduce image size (by removing intermediate deleted files) but loses layer sharing benefits. If you squash `nginx:1.24`, every container using the squashed image has no shared base layers with `nginx:1.25`. When is squashing beneficial? When does it hurt? Under what circumstances would you squash a production image vs keep layers?
