---
layout: default
title: "Docker Image"
parent: "Containers"
nav_order: 823
permalink: /containers/docker-image/
number: "0823"
category: Containers
difficulty: ★☆☆
depends_on: Docker, Container, Dockerfile, OCI Standard
used_by: Docker Layer, Multi-Stage Build, Container Registry, Image Tag Strategy, Distroless Images
related: Docker Layer, Dockerfile, Container Registry, Multi-Stage Build, Image Tag Strategy
tags:
  - containers
  - docker
  - devops
  - foundational
  - architecture
---

# 823 — Docker Image

⚡ TL;DR — A Docker image is an immutable, layered filesystem snapshot that packages everything needed to run a container — the portable artifact that travels from developer laptop to production server unchanged.

| #823 | Category: Containers | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Docker, Container, Dockerfile, OCI Standard | |
| **Used by:** | Docker Layer, Multi-Stage Build, Container Registry, Image Tag Strategy, Distroless Images | |
| **Related:** | Docker Layer, Dockerfile, Container Registry, Multi-Stage Build, Image Tag Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before standardised container images, deploying a new version of an application meant: SSH into servers, run a deploy script, install the right version of Node/Python/Ruby manually, copy the application files, restart the service. Each deploy step was an opportunity for the environment to differ from the previous deployment or differ from the test environment. "Works in staging, broken in production" was a weekly occurrence — and the answer was always "I'm not sure why, let me check the server manually."

**THE BREAKING POINT:**
The core problem: the application and its runtime environment were managed separately. The application was versioned (git). The environment was not — it drifted over time on each server as manual changes accumulated.

**THE INVENTION MOMENT:**
This is exactly why Docker images exist — treating the application AND its complete runtime environment as a single, versioned, immutable artifact. The image is the unit of deployment. It never changes after it is built. Deploy it to any host and you get exactly the same result.

---

### 📘 Textbook Definition

A **Docker image** is an immutable, read-only filesystem artifact built as an ordered stack of layers, conforming to the OCI (Open Container Initiative) image specification. Each layer is a compressed tar archive of filesystem changes (added, modified, or deleted files), content-addressed by its SHA256 digest. An image has a manifest (JSON file listing layers and configuration), a config object (environment variables, entrypoint command, exposed ports), and one or more read-only filesystem layers. A running container adds an additional, ephemeral writable layer on top of the image layers — the image itself is never modified. Images are stored in registries (Docker Hub, ECR, GCR) and identified by `name:tag` or by digest (`sha256:abc...`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Docker image is a frozen snapshot of a complete application environment — immutable, versioned, and runnable anywhere Docker is installed.

**One analogy:**
> A Docker image is like a factory-sealed frozen meal. Everything you need for the meal is inside: protein, vegetables, sauce, disposable tray. Sealed at the factory, identical in every store. You take it home (your production host), heat it (run the container), and get exactly what the factory made. No assembly required. No substitutions. The meal doesn't change after it's sealed — but you can eat it fresh every time you run a container from it.

**One insight:**
The "layered" design is not just an implementation detail — it is what makes Docker images economically viable. Image layers are shared across all images that share the same base. Pull `ubuntu:22.04` once, and every image built `FROM ubuntu:22.04` on that host reuses those cached layers. A 200-image system might actually only store 500 MB of data because 80% of the layers are shared.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An image is immutable — once built and pushed, it never changes. Any modification creates a new image.
2. Layers are content-addressed — a layer's identity IS its SHA256 content hash. Same content → same hash → always reused.
3. An image is the complete specification of a filesystem — the container's root filesystem is exactly what the image defines.

**DERIVED DESIGN:**
An image is built from a `Dockerfile`. Each instruction creates one layer:

```
FROM node:20-alpine           → base layer (node runtime)
WORKDIR /app                  → (no filesystem change — no layer)
COPY package.json .           → layer: adds package.json
RUN npm install               → layer: adds node_modules/
COPY . .                      → layer: adds application code
CMD ["node", "server.js"]    → (metadata only — no layer)
```

The final image is the union of all layers. When a container starts, OverlayFS merges all layers into a single filesystem view, adding a writable layer on top. Files from lower layers can be "overridden" by the writable layer on write (copy-on-write): the first write to a file copies it up to the writable layer; subsequent reads serve from the writable layer copy.

**Layer content-addressing:** If two images both have the same `FROM node:20-alpine` base, they share the exact same bytes on disk — pulled once, referenced many times. A layer change in the middle of a Dockerfile invalidates all subsequent layers in the cache — which is why order of instructions matters greatly for build performance.

**THE TRADE-OFFS:**
**Gain:** Immutability guarantees reproducibility; layer sharing reduces storage and bandwidth; content addressing prevents image tampering.
**Cost:** Large images waste network bandwidth on every pull; improper layer ordering defeats the cache; every `RUN apt-get install` creates a new layer, so bad practices cause image bloat.

---

### 🧪 Thought Experiment

**SETUP:**
Two microservices — `order-service` and `payment-service` — both built `FROM node:20-alpine`. The node:20-alpine image is 180 MB.

**WITHOUT LAYER SHARING:**
If images were not layered (monolithic blobs), every host running both services would store 180 MB × 2 = 360 MB just for Node.js runtime — plus application code. With 50 Node.js services, that is 9 GB of storage. Every image pull downloads 180 MB of redundant Node.js runtime.

**WITH LAYER SHARING:**
Both images reference the `node:20-alpine` layer by its SHA256. The host's Docker layer store holds one copy of the 180 MB Node.js layer, shared by both images. Only the application-specific layers (10–30 MB) are unique per image. With 50 Node.js services, total storage: 180 MB (shared base) + 50 × 15 MB (app layers) = 930 MB instead of 9 GB. Image pulls for a new version only download the changed application layers — the Node.js layer is already present.

**THE INSIGHT:**
Content-addressed layer sharing is what makes Docker economically viable in large fleet deployments. The efficiency is multiplicative: the more images share a base, the larger the savings.

---

### 🧠 Mental Model / Analogy

> A Docker image is like a git repository's commit history. Each commit (layer) records a diff from the previous state. Two branches (images) that share a common ancestor (base image) share all the commits up to the branch point — no duplication. `git checkout` reconstructs the working tree from the commit history; `docker run` reconstructs the container filesystem from the layer stack. Immutability, content addressing, and history are common to both.

**Mapping:**
- "Git repository" → Docker layer store (local image cache)
- "Git commit" → image layer (filesystem diff)
- "git checkout branch" → `docker run image:tag` (assembles layers into running container)
- "Common ancestor commit" → shared base layers (e.g. `node:20-alpine`)
- "Branch divergence" → unique application layers added on top of shared base

**Where this analogy breaks down:** Git tracks all history; Docker images track only forward diffs and do not retain deleted files' history. Also, git commits are compressed diffs; Docker layers are full file additions/replacements, not diffs of file content.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Docker image is like a sealed package that contains your application and everything it needs to run. You can send the same package to any computer with Docker and it will run exactly the same way. You can have many identical copies of this package running at the same time (containers).

**Level 2 — How to use it (junior developer):**
You build an image with `docker build -t myapp:1.0 .`. This creates an image in your local image store. You can run a container from it: `docker run myapp:1.0`. You can push it to a registry for others: `docker push myapp:1.0`. Tagging with a version (`1.0`, `1.1`, `latest`) tracks versions. Images are immutable once built — a new `docker build` creates a new image; it doesn't modify the existing one.

**Level 3 — How it works (mid-level engineer):**
An image is described by a manifest JSON: `{"schemaVersion": 2, "layers": [{"digest": "sha256:abc...", "size": 23456789}, ...]}`. Each layer SHA256 is both its identifier and its integrity check. The image config JSON specifies: `Cmd`, `Entrypoint`, `Env`, `ExposedPorts`, `WorkingDir`. When Docker pulls an image, it downloads the manifest, config, and any layers not already in the local content store. `docker images` shows the images; `docker image inspect` shows manifests and configs. `docker history` shows layers and their sizes.

**Level 4 — Why it was designed this way (senior/staff):**
The layer/content-addressed design was heavily influenced by distributed systems principles: immutable data + content addressing provides built-in integrity verification and natural deduplication. Solomon Hykes (Docker founder) later said the layer model was both Docker's greatest strength and greatest weakness — layering encourages `apt-get install` in separate `RUN` instructions, bloating images with unnecessary cache data that cannot be removed without squashing. Multi-stage builds (Docker 17.05+) solved the bloat problem by separating build-time dependencies from runtime images. The ongoing evolution: OCI image spec has been adopted by every container runtime, making Docker images the de facto standard independent of Docker itself.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────┐
│  IMAGE STRUCTURE                                    │
│                                                     │
│  Image Manifest (JSON):                             │
│  {                                                  │
│    "layers": [                                      │
│      {"digest": "sha256:Layer1", "size": 45MB},    │
│      {"digest": "sha256:Layer2", "size": 12MB},    │
│      {"digest": "sha256:Layer3", "size": 2MB}      │
│    ]                                                │
│  }                                                  │
│                                                     │
│  Image Config (JSON):                               │
│  { "Cmd": ["node", "server.js"],                   │
│    "Env": ["NODE_ENV=production"],                  │
│    "ExposedPorts": {"3000/tcp": {}} }               │
│                                                     │
│  OverlayFS stack when container runs:               │
│  [Writable Layer] ← container writes here          │
│  [Layer 3: app code] /app/*.js (2 MB)              │
│  [Layer 2: node_modules] (12 MB)                   │
│  [Layer 1: node:20-alpine base] (45 MB)            │
│                                                     │
│  Merged view → container's root filesystem (/)     │
└─────────────────────────────────────────────────────┘
```

**Layer reuse across images:**
```
  node:20-alpine (Layer1: 45 MB)
        │ shared by both images
  ┌─────┴──────┐
  │            │
  order-svc  payment-svc
  (Layer2+3) (Layer2+3)
  12 MB       15 MB
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Dockerfile → docker build → [IMAGE ← YOU ARE HERE]
           → docker tag → docker push → Registry
           → CI/CD: docker pull (on deploy host)
           → docker run → Container starts
```

**FAILURE PATH:**
```
docker pull fails (registry unavailable or auth expired)
→ "image pull failed" on deploy
→ if image already on host → docker run still works (cached)
→ new images cannot be deployed until registry is accessible
```

**WHAT CHANGES AT SCALE:**
At 1,000-node fleet, a deployment event causes 1,000 nodes to simultaneously pull a new image. A 500 MB image × 1,000 nodes = 500 GB of registry bandwidth in seconds. Solutions: (1) use a pull-through registry cache (Harbor, ECR pull-through) so nodes pull from a regional cache, not the source registry; (2) pre-warm images on nodes before deployment via image pre-pull DaemonSets in Kubernetes; (3) use image streaming (lazy loading) to start containers before all layers are downloaded.

---

### 💻 Code Example

Example 1 — Image operations:
```bash
# Build image from Dockerfile in current directory
docker build -t myapp:1.0 .

# List local images (shows size, layers)
docker images

# See layer sizes and how image was built
docker history myapp:1.0

# Inspect full image metadata
docker inspect myapp:1.0 | jq '.[0].Config'

# See image layers by digest
docker manifest inspect myapp:1.0
```

Example 2 — Optimising image size (layer order matters):
```dockerfile
# BAD: changes to app code invalidate npm install cache
FROM node:20-alpine
COPY . .                # ← all source files copied first
RUN npm install         # ← cache always missed if any file changes

# GOOD: only install deps when package.json changes
FROM node:20-alpine
COPY package.json package-lock.json ./  # ← only dependency files
RUN npm ci              # ← cached unless deps change
COPY . .                # ← app code (changes often) copied last
CMD ["node", "server.js"]
```

Example 3 — View image disk usage:
```bash
# Breakdown of image, container, volume disk usage
docker system df -v

# Specific image layer details
docker image inspect myapp:1.0 \
  | jq '.[0].RootFS.Layers'
# Lists SHA256 of each layer
```

---

### ⚖️ Comparison Table

| Image Type | Size | Startup | Attack Surface | Use Case |
|---|---|---|---|---|
| Full OS base (ubuntu:22.04) | ~80 MB | Fast | Large | General purpose development |
| Slim base (debian:slim) | ~30 MB | Fast | Medium | Production apps with OS tools |
| Alpine base | ~5 MB | Fast | Small | Production microservices |
| Distroless | ~2–20 MB | Fast | Minimal | Production security-sensitive |
| Scratch | 0 MB | Fast | Zero | Statically compiled Go/Rust binaries |

**How to choose:** Use `alpine` or `debian:slim` as the default production base. Use `distroless` for security-sensitive services. Use `scratch` only for fully statically compiled binaries. Never use full OS base images in production — they contain unnecessary utilities that bloat the image and expand the attack surface.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A container and an image are the same thing | An image is a read-only template; a container is a running instance of an image with an additional writable layer. Multiple containers can run from the same image. |
| `latest` always means the newest version | `latest` is just a tag — it only points to whatever was last pushed with that tag. It is not automatically the most recent or stable version. |
| Deleting a container deletes its image | Deleting a container removes its writable layer only; the image remains. Use `docker rmi` to remove images. |
| Smaller images are always better | Image size affects pull time and storage; it does not directly affect runtime performance or security beyond reducing attack surface. Overly minimal images can make debugging harder. |
| Changing a running container changes its image | Container writes go to the writable layer only. The underlying image is never modified. Changes are lost when the container is removed unless committed or stored in volumes. |

---

### 🚨 Failure Modes & Diagnosis

**Image Bloat**

**Symptom:** Image is 2 GB; pulls take 3+ minutes in CI; deployment is slow.

**Root Cause:** Build artifacts (compilers, test dependencies, intermediate files) left in image layers. Cleanup `RUN rm -rf` after `apt-get install` is in a separate layer — the previous layer still contains the data (it is immutable).

**Diagnostic Command / Tool:**
```bash
docker history myapp:1.0 --no-trunc | sort -k5 -rh
# Shows layers sorted by size — identify the bloat source

dive myapp:1.0
# Interactive layer explorer (github.com/wagoodman/dive)
```

**Fix:** Use multi-stage builds (build in one stage, copy only final artifacts to a clean final stage). Combine `apt-get install` and `apt-get clean` in a single `RUN` command.

**Prevention:** Set an image size budget (e.g., <200 MB) enforced in CI with `docker image inspect -f '{{.Size}}' myapp:1.0`.

---

**Cache Miss on Every Build**

**Symptom:** `docker build` re-runs `npm install` from scratch on every build even when only app code changed — CI builds take 8 minutes.

**Root Cause:** `COPY . .` (copies all source files including changing JS files) appears BEFORE `RUN npm install`, causing the install layer to be invalidated every time any source file changes.

**Diagnostic Command / Tool:**
```bash
# Add --progress=plain to see exactly which layers are cached/missed
docker build --progress=plain -t myapp . 2>&1 | grep -E "CACHED|RUN"
```

**Fix:** Reorder Dockerfile: COPY package.json first, RUN npm install, then COPY source code (see Code Example 2 above).

**Prevention:** Always put static/slow-changing operations (`npm install`, `pip install`) before fast-changing operations (`COPY . .`) in the Dockerfile.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker` — the tool that builds and runs images
- `Dockerfile` — the build specification that creates an image

**Builds On This (learn these next):**
- `Docker Layer` — the individual building blocks stored inside an image
- `Multi-Stage Build` — technique for creating minimal production images
- `Container Registry` — where images are stored and distributed

**Alternatives / Comparisons:**
- `Distroless Images` — ultra-minimal images to reduce attack surface
- `OCI Standard` — the specification all Docker images conform to; enables non-Docker tooling to use the same images

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Immutable, layered filesystem artifact   │
│              │ containing everything to run a container │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Environment drift between dev, test,     │
│ SOLVES       │ and production causing different behaviour│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Layer sharing via content addressing      │
│              │ makes 50 images store like 10 images     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — images are the standard unit    │
│              │ of container packaging and delivery      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid large base images in production;  │
│              │ avoid mutable image states (always rebuild│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Immutability + reproducibility vs        │
│              │ layer cache management complexity        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A factory-sealed frozen meal — exact    │
│              │  same result every time you heat it"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Docker Layer → Dockerfile →              │
│              │ Multi-Stage Build                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has 80 Docker images in production. All are based on `ubuntu:20.04`. A critical CVE is discovered in a library present in `ubuntu:20.04` base layer. You need to patch all 80 images. Describe the automated process you would build to: detect which images contain the vulnerable layer (without manually inspecting 80 images), rebuild them, verify the vulnerability is patched, and deploy them to production — targeting completion within 4 hours.

**Q2.** A `docker history myapp:latest` shows a layer of size 1.4 GB from `RUN npm install` and another layer removing `node_modules` from 200 lines later in the Dockerfile (size: -1.4 GB). The final image is 1.8 GB. An engineer says "we need the second layer to remove node_modules for a smaller image." Explain exactly why this approach does not work (the size does not actually reduce), and describe the correct approach to achieve an image that genuinely does not contain node_modules.

