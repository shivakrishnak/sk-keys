---
layout: default
title: "Docker Image"
parent: "Containers"
nav_order: 823
permalink: /containers/docker-image/
number: "823"
category: Containers
difficulty: ★☆☆
depends_on: "Docker, Container, Docker Layer"
used_by: "Dockerfile, Container Registry, Docker Build Context, Multi-Stage Build"
tags: #containers, #docker, #image, #layers, #oci, #immutable
---

# 823 — Docker Image

`#containers` `#docker` `#image` `#layers` `#oci` `#immutable`

⚡ TL;DR — A **Docker image** is an immutable, layered, read-only snapshot of a filesystem and execution configuration. Images are built from Dockerfiles, stored in registries, and instantiated as containers at runtime. Each layer is a diff; layers are shared and cached across images. OCI-standard: portable across Docker, Kubernetes (containerd/CRI-O), and all OCI-compliant runtimes.

| #823            | Category: Containers                                                    | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Docker, Container, Docker Layer                                         |                 |
| **Used by:**    | Dockerfile, Container Registry, Docker Build Context, Multi-Stage Build |                 |

---

### 📘 Textbook Definition

**Docker image**: an ordered collection of read-only filesystem layers plus an image manifest (metadata). Each layer is an immutable, content-addressable diff (tar archive) identified by its SHA256 hash. The manifest describes the layers, their order, and the container configuration (entrypoint, environment variables, exposed ports, working directory, labels, architecture). Images comply with the OCI (Open Container Initiative) Image Specification, making them portable across all OCI-compliant runtimes. An image is a **template** — it never runs directly. A **container** is a running instance of an image, with an additional writable layer added on top. Images are referenced by **name:tag** (`nginx:1.24`, `python:3.11-slim`) with `latest` as the default tag. Images are immutable after build — a `docker build` creates a new image (new content hashes), it never modifies an existing image.

---

### 🟢 Simple Definition (Easy)

An image is the blueprint for a container. It contains: the filesystem (OS files, app code, libraries) and instructions for how to run the app (what command to start, what ports to expose, what environment variables to set). You build the image once (with `docker build`), store it in a registry, and then run N containers from it anywhere. The image is read-only — containers add a writable layer on top.

---

### 🔵 Simple Definition (Elaborated)

Images are composed of **layers** — think of them as git commits for a filesystem. Each Dockerfile instruction (`RUN`, `COPY`, `ADD`) creates a new layer that adds/modifies/removes files from the previous layer. Layers are content-addressed by SHA256 hash and cached: if layer 3 of your image hasn't changed, Docker reuses the cached layer without re-executing the `RUN` command.

Multiple images sharing the same base layer (e.g., `ubuntu:22.04`) share that layer on disk — it's stored once and reused. This is how 100 containers can run on a host without 100 × 200MB of disk per container.

The image manifest (JSON) is what identifies an image version:

- `nginx:1.24` → a tag pointing to a manifest → manifest lists layers by hash
- Tags are mutable (`latest` can change); digests are immutable (`nginx@sha256:abc123...`)

---

### 🔩 First Principles Explanation

```
IMAGE STRUCTURE (OCI Image Spec):

  Registry storage:
  ┌─────────────────────────────────────────────────────────┐
  │ Image: myapp:2.1                                        │
  │                                                         │
  │ Manifest (JSON):                                        │
  │ {                                                       │
  │   "schemaVersion": 2,                                   │
  │   "mediaType": "application/vnd.docker.distribution...",│
  │   "config": {                                           │
  │     "digest": "sha256:config_hash",                     │
  │     "size": 4567                                        │
  │   },                                                    │
  │   "layers": [                                           │
  │     {"digest":"sha256:layer1_hash","size":29126148},    │
  │     {"digest":"sha256:layer2_hash","size":15234567},    │
  │     {"digest":"sha256:layer3_hash","size":2048123},     │
  │     {"digest":"sha256:layer4_hash","size":125432}       │
  │   ]                                                     │
  │ }                                                       │
  │                                                         │
  │ Config (JSON):                                          │
  │ {                                                       │
  │   "architecture": "amd64",                              │
  │   "os": "linux",                                        │
  │   "config": {                                           │
  │     "Cmd": ["node", "server.js"],                       │
  │     "WorkingDir": "/app",                               │
  │     "Env": ["NODE_ENV=production", "PORT=3000"],        │
  │     "ExposedPorts": {"3000/tcp": {}},                   │
  │     "User": "appuser"                                   │
  │   },                                                    │
  │   "rootfs": {"type":"layers","diff_ids":["sha256:..."]} │
  │ }                                                       │
  │                                                         │
  │ Layers (tar.gz blobs, content-addressed by SHA256):     │
  │ sha256:layer1_hash → ubuntu base filesystem (29MB)      │
  │ sha256:layer2_hash → nodejs runtime (15MB)              │
  │ sha256:layer3_hash → app dependencies (2MB)             │
  │ sha256:layer4_hash → app source code (125KB)            │
  └─────────────────────────────────────────────────────────┘

LAYER SHARING ON DISK:

  Image A: python:3.11-slim + myapp-v1
  Layers: [debian_base, python311, myapp_v1_deps, myapp_v1_code]

  Image B: python:3.11-slim + myapp-v2
  Layers: [debian_base, python311, myapp_v2_deps, myapp_v2_code]

  On disk:
  debian_base: stored ONCE (both images reference same SHA256)
  python311: stored ONCE
  myapp_v1_deps and myapp_v2_deps: separate layers (different content)
  myapp_v1_code and myapp_v2_code: separate layers

  Total disk: ≈ debian_base + python311 + v1_deps + v1_code + v2_deps + v2_code
  (NOT 2 × full image; shared layers stored once)

  If 100 containers run myapp:v2:
  All 100 share the same read-only layers on disk
  Each container only adds a thin writable layer (megabytes)
  Total additional disk for 100 containers: 100 × (writable layer size)

IMAGE TAGS vs DIGESTS:

  TAGS (mutable):
  nginx:1.24       → today: points to manifest sha256:abc123
  nginx:1.24       → after patch: points to manifest sha256:def456
  nginx:latest     → always points to most recent build

  Risk: "nginx:latest" in your Kubernetes deployment pulled 6 months ago
  is different from "nginx:latest" pulled today → unintended upgrade

  DIGESTS (immutable):
  nginx@sha256:abc123...def  → ALWAYS refers to exactly this manifest
  → content-addressed → cryptographic guarantee of identity

  ✅ PRODUCTION RULE: pin to digest, not tag
  image: nginx@sha256:3b34bca...  (in K8s Deployment manifest)

WHAT'S IN AN IMAGE (typical breakdown):

  FROM ubuntu:22.04          [Layer 1: 27MB - base OS: glibc, apt, core utils]
  RUN apt-get update && \    [Layer 2: 50MB - package metadata]
      apt-get install -y python3 pip
  COPY requirements.txt .    [Layer 3: 1KB - requirements file]
  RUN pip install -r req.txt [Layer 4: 180MB - Python libraries]
  COPY . /app/               [Layer 5: 2MB - application source code]

  Total: ~260MB

  If 100 different apps use the same ubuntu:22.04 base:
  Layer 1 (27MB): stored once on the registry, pulled once per host
  The 99MB of ubuntu+python shared across all apps
```

---

### ❓ Why Does This Exist (Why Before What)

The image abstraction solves the "works on my machine" problem: by packaging the entire filesystem (OS libraries + runtime + app code + config) into a content-addressed, immutable artifact, the image guarantees that "build once, run anywhere" is literally true. The layered model makes this practical: without layers, every image would be a monolithic gigabyte-scale tar archive, slow to build and push. Layers enable incremental builds (cache), incremental pushes (only new layers), and storage efficiency (shared base layers).

---

### 🧠 Mental Model / Analogy

> **A Docker image is a layered cake with a recipe card**: each layer of cake is a filesystem diff (base OS, runtime, dependencies, source code). The recipe card (image config) says how to serve the cake (what command to run, what port to listen on). When you want a slice (run a container): you don't modify the cake — you put it on a plate and add your frosting on top (the writable container layer). The same cake can be on 100 plates simultaneously (100 containers). Different cakes sharing the same bottom layers (base OS): bakers only bake those shared layers once and reuse them.

---

### ⚙️ How It Works (Mechanism)

```
OVERLAY2 FILESYSTEM (how containers see the image layers):

  Image layers (read-only, on disk):
  Layer 1: /bin/bash, /usr/lib/libc.so, /etc/...
  Layer 2: /usr/bin/python3, /usr/lib/python3.11/...
  Layer 3: /app/requirements.txt
  Layer 4: /usr/local/lib/python3.11/site-packages/flask/...

  Container writable layer (thin, ephemeral):
  /app/logs/access.log  (written by app at runtime)
  /tmp/uploaded_file.tmp

  What the container process sees (merged view via overlay2):
  All layers merged into one filesystem view
  Writes go to the writable layer (copy-on-write)
  Reads from lower layers if not in writable layer

  COW (Copy-on-Write): if container modifies /etc/hosts (from layer 1):
  → Docker copies /etc/hosts to the writable layer
  → Container's writes go to writable layer
  → Original layer 1 /etc/hosts unchanged (other containers unaffected)

PULL: efficient delta download

  docker pull myapp:2.0  (previously had myapp:1.0)
  → Fetch manifest for myapp:2.0
  → Compare layer hashes: layers already present? → skip
  → Download ONLY the new layers (e.g., new code layer)
  → "Already exists: sha256:abc..." for shared layers
```

---

### 🔄 How It Connects (Mini-Map)

```
Need a portable, reproducible deployment artifact
        │
        ▼
Docker Image ◄── (you are here)
(layered, immutable, OCI-compliant filesystem + config)
        │
        ├── Docker Layer: each layer is a filesystem diff
        ├── Dockerfile: instructions that create each layer
        ├── Container Registry: stores and distributes images
        ├── Multi-Stage Build: reduces final image size
        └── Container: a running instance of an image
```

---

### 💻 Code Example

{% raw %}
```bash
# Inspect image structure
docker image ls                                       # list local images
docker image inspect nginx:1.24                      # full metadata JSON
docker history nginx:1.24                            # show layers + sizes + commands

# Pull by digest (immutable reference)
docker pull nginx@sha256:3b4...                       # pin to exact content

# Image size analysis
docker image ls --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | sort -k2 -h

# Dive tool (interactive layer explorer):
# dive nginx:1.24  → shows each layer's filesystem changes interactively

# Export/import (for air-gapped environments)
docker save myapp:1.0 | gzip > myapp_1.0.tar.gz      # export to tar
docker load < myapp_1.0.tar.gz                        # import on another machine

# Scan image for vulnerabilities
docker scout cves nginx:1.24                          # Docker Scout (built-in)
# or: trivy image nginx:1.24  (Aqua Trivy, widely used)
```
{% endraw %}

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Deleting a container deletes the image                 | `docker rm` removes the container (its writable layer). The image remains until `docker rmi`. Containers are instances; images are templates.                                                                                                                                                             |
| `:latest` tag means most recently pushed to Docker Hub | `latest` is just a convention — image publishers are expected to tag their most recent stable release as `latest`, but it's not enforced. Some projects don't update `latest` or use it for a different branch. Never rely on `latest` in production.                                                     |
| A smaller image is always better                       | Smaller images reduce attack surface and pull time. BUT: distroless/scratch images lack debugging tools (no shell, no curl). For production: use slim/distroless and accept limited debuggability. For debugging: have a separate debug image or use `kubectl debug` / `docker run --pid=container:<id>`. |

---

### 🔥 Pitfalls in Production

```
PITFALL: secrets baked into image layers

  # ❌ DANGEROUS: API key in RUN command (becomes part of image layer)
  FROM ubuntu:22.04
  RUN export API_KEY=sk-secret-123 && curl -H "Authorization: $API_KEY" ...
  # Even if you unset API_KEY in a later layer, it's in layer N's history
  # docker history --no-trunc shows the full command including the secret
  # Anyone with docker pull access can read the secret

  # ✅ CORRECT: use build secrets (Docker BuildKit)
  # syntax=docker/dockerfile:1
  FROM ubuntu:22.04
  RUN --mount=type=secret,id=api_key \
      API_KEY=$(cat /run/secrets/api_key) && \
      curl -H "Authorization: $API_KEY" ...
  # Secret available ONLY during this build step; not baked into any layer

  # Build: docker buildx build --secret id=api_key,src=./api_key.txt .

PITFALL: using :latest tag causes surprise upgrades

  # ❌ Kubernetes deployment (will pull latest on node restart)
  containers:
  - name: myapp
    image: nginx:latest     # ← what version is this today? next week?

  # ✅ Pin to specific version
  containers:
  - name: myapp
    image: nginx:1.24.0     # explicit version
  # or even better:
    image: nginx@sha256:3b4def...  # cryptographic pin
```

---

### 🔗 Related Keywords

- `Docker Layer` — each layer is a filesystem diff; caching and sharing
- `Dockerfile` — instructions that generate each image layer
- `Docker Build Context` — files sent to Docker daemon during `docker build`
- `Multi-Stage Build` — reduce image size by discarding build-time layers
- `Container Registry` — stores, tags, and distributes images

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ IMAGE = manifest + config + ordered layers (SHA256)      │
│ LAYER: read-only filesystem diff (tar archive)           │
│ SHARED: layers shared on disk across images/containers   │
│ TAGS: mutable (latest can change) → don't use in prod   │
│ DIGESTS: immutable sha256 → pin in production            │
├──────────────────────────────────────────────────────────┤
│ Rules:                                                   │
│ • Never bake secrets into layers                        │
│ • Pin to digest (not tag) in production K8s             │
│ • Order Dockerfile: rarely changed → frequently changed │
│   (base → deps → code) for optimal layer caching        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Multi-architecture images (multi-platform manifests) allow the same `nginx:1.24` tag to serve both `linux/amd64` and `linux/arm64`. The registry stores a "manifest list" (OCI image index) that maps platform to the appropriate platform-specific manifest. When `docker pull nginx:1.24` runs on an ARM machine, how does Docker know to pull the ARM image? What happens in Kubernetes when you have a mixed ARM + x86 node pool and deploy `nginx:1.24` — which image does each node pull?

**Q2.** Distroless images (from Google) contain only the application and its runtime dependencies — no shell, no package manager, no OS utilities. A `gcr.io/distroless/java17-debian11` image is ~50MB vs `openjdk:17-jdk` at ~350MB. What are the security benefits of distroless? What operational challenges does it create (debugging, shell access, `kubectl exec`)? How do you debug a running distroless container in production?
