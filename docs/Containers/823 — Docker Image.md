---
layout: default
title: "Docker Image"
parent: "Containers"
nav_order: 823
permalink: /containers/docker-image/
number: "823"
category: Containers
difficulty: â˜…â˜†â˜†
depends_on: "Docker, Container, Docker Layer"
used_by: "Dockerfile, Container Registry, Docker Build Context, Multi-Stage Build"
tags: #containers, #docker, #image, #layers, #oci, #immutable
---

# 823 â€” Docker Image

`#containers` `#docker` `#image` `#layers` `#oci` `#immutable`

âš¡ TL;DR â€” A **Docker image** is an immutable, layered, read-only snapshot of a filesystem and execution configuration. Images are built from Dockerfiles, stored in registries, and instantiated as containers at runtime. Each layer is a diff; layers are shared and cached across images. OCI-standard: portable across Docker, Kubernetes (containerd/CRI-O), and all OCI-compliant runtimes.

| #823            | Category: Containers                                                    | Difficulty: â˜…â˜†â˜† |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Docker, Container, Docker Layer                                         |                 |
| **Used by:**    | Dockerfile, Container Registry, Docker Build Context, Multi-Stage Build |                 |

---

### ðŸ“˜ Textbook Definition

**Docker image**: an ordered collection of read-only filesystem layers plus an image manifest (metadata). Each layer is an immutable, content-addressable diff (tar archive) identified by its SHA256 hash. The manifest describes the layers, their order, and the container configuration (entrypoint, environment variables, exposed ports, working directory, labels, architecture). Images comply with the OCI (Open Container Initiative) Image Specification, making them portable across all OCI-compliant runtimes. An image is a **template** â€” it never runs directly. A **container** is a running instance of an image, with an additional writable layer added on top. Images are referenced by **name:tag** (`nginx:1.24`, `python:3.11-slim`) with `latest` as the default tag. Images are immutable after build â€” a `docker build` creates a new image (new content hashes), it never modifies an existing image.

---

### ðŸŸ¢ Simple Definition (Easy)

An image is the blueprint for a container. It contains: the filesystem (OS files, app code, libraries) and instructions for how to run the app (what command to start, what ports to expose, what environment variables to set). You build the image once (with `docker build`), store it in a registry, and then run N containers from it anywhere. The image is read-only â€” containers add a writable layer on top.

---

### ðŸ”µ Simple Definition (Elaborated)

Images are composed of **layers** â€” think of them as git commits for a filesystem. Each Dockerfile instruction (`RUN`, `COPY`, `ADD`) creates a new layer that adds/modifies/removes files from the previous layer. Layers are content-addressed by SHA256 hash and cached: if layer 3 of your image hasn't changed, Docker reuses the cached layer without re-executing the `RUN` command.

Multiple images sharing the same base layer (e.g., `ubuntu:22.04`) share that layer on disk â€” it's stored once and reused. This is how 100 containers can run on a host without 100 Ã— 200MB of disk per container.

The image manifest (JSON) is what identifies an image version:

- `nginx:1.24` â†’ a tag pointing to a manifest â†’ manifest lists layers by hash
- Tags are mutable (`latest` can change); digests are immutable (`nginx@sha256:abc123...`)

---

### ðŸ”© First Principles Explanation

```
IMAGE STRUCTURE (OCI Image Spec):

  Registry storage:
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ Image: myapp:2.1                                        â”‚
  â”‚                                                         â”‚
  â”‚ Manifest (JSON):                                        â”‚
  â”‚ {                                                       â”‚
  â”‚   "schemaVersion": 2,                                   â”‚
  â”‚   "mediaType": "application/vnd.docker.distribution...",â”‚
  â”‚   "config": {                                           â”‚
  â”‚     "digest": "sha256:config_hash",                     â”‚
  â”‚     "size": 4567                                        â”‚
  â”‚   },                                                    â”‚
  â”‚   "layers": [                                           â”‚
  â”‚     {"digest":"sha256:layer1_hash","size":29126148},    â”‚
  â”‚     {"digest":"sha256:layer2_hash","size":15234567},    â”‚
  â”‚     {"digest":"sha256:layer3_hash","size":2048123},     â”‚
  â”‚     {"digest":"sha256:layer4_hash","size":125432}       â”‚
  â”‚   ]                                                     â”‚
  â”‚ }                                                       â”‚
  â”‚                                                         â”‚
  â”‚ Config (JSON):                                          â”‚
  â”‚ {                                                       â”‚
  â”‚   "architecture": "amd64",                              â”‚
  â”‚   "os": "linux",                                        â”‚
  â”‚   "config": {                                           â”‚
  â”‚     "Cmd": ["node", "server.js"],                       â”‚
  â”‚     "WorkingDir": "/app",                               â”‚
  â”‚     "Env": ["NODE_ENV=production", "PORT=3000"],        â”‚
  â”‚     "ExposedPorts": {"3000/tcp": {}},                   â”‚
  â”‚     "User": "appuser"                                   â”‚
  â”‚   },                                                    â”‚
  â”‚   "rootfs": {"type":"layers","diff_ids":["sha256:..."]} â”‚
  â”‚ }                                                       â”‚
  â”‚                                                         â”‚
  â”‚ Layers (tar.gz blobs, content-addressed by SHA256):     â”‚
  â”‚ sha256:layer1_hash â†’ ubuntu base filesystem (29MB)      â”‚
  â”‚ sha256:layer2_hash â†’ nodejs runtime (15MB)              â”‚
  â”‚ sha256:layer3_hash â†’ app dependencies (2MB)             â”‚
  â”‚ sha256:layer4_hash â†’ app source code (125KB)            â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

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

  Total disk: â‰ˆ debian_base + python311 + v1_deps + v1_code + v2_deps + v2_code
  (NOT 2 Ã— full image; shared layers stored once)

  If 100 containers run myapp:v2:
  All 100 share the same read-only layers on disk
  Each container only adds a thin writable layer (megabytes)
  Total additional disk for 100 containers: 100 Ã— (writable layer size)

IMAGE TAGS vs DIGESTS:

  TAGS (mutable):
  nginx:1.24       â†’ today: points to manifest sha256:abc123
  nginx:1.24       â†’ after patch: points to manifest sha256:def456
  nginx:latest     â†’ always points to most recent build

  Risk: "nginx:latest" in your Kubernetes deployment pulled 6 months ago
  is different from "nginx:latest" pulled today â†’ unintended upgrade

  DIGESTS (immutable):
  nginx@sha256:abc123...def  â†’ ALWAYS refers to exactly this manifest
  â†’ content-addressed â†’ cryptographic guarantee of identity

  âœ… PRODUCTION RULE: pin to digest, not tag
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

### â“ Why Does This Exist (Why Before What)

The image abstraction solves the "works on my machine" problem: by packaging the entire filesystem (OS libraries + runtime + app code + config) into a content-addressed, immutable artifact, the image guarantees that "build once, run anywhere" is literally true. The layered model makes this practical: without layers, every image would be a monolithic gigabyte-scale tar archive, slow to build and push. Layers enable incremental builds (cache), incremental pushes (only new layers), and storage efficiency (shared base layers).

---

### ðŸ§  Mental Model / Analogy

> **A Docker image is a layered cake with a recipe card**: each layer of cake is a filesystem diff (base OS, runtime, dependencies, source code). The recipe card (image config) says how to serve the cake (what command to run, what port to listen on). When you want a slice (run a container): you don't modify the cake â€” you put it on a plate and add your frosting on top (the writable container layer). The same cake can be on 100 plates simultaneously (100 containers). Different cakes sharing the same bottom layers (base OS): bakers only bake those shared layers once and reuse them.

---

### âš™ï¸ How It Works (Mechanism)

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
  â†’ Docker copies /etc/hosts to the writable layer
  â†’ Container's writes go to writable layer
  â†’ Original layer 1 /etc/hosts unchanged (other containers unaffected)

PULL: efficient delta download

  docker pull myapp:2.0  (previously had myapp:1.0)
  â†’ Fetch manifest for myapp:2.0
  â†’ Compare layer hashes: layers already present? â†’ skip
  â†’ Download ONLY the new layers (e.g., new code layer)
  â†’ "Already exists: sha256:abc..." for shared layers
```

---

### ðŸ”„ How It Connects (Mini-Map)

```
Need a portable, reproducible deployment artifact
        â”‚
        â–¼
Docker Image â—„â”€â”€ (you are here)
(layered, immutable, OCI-compliant filesystem + config)
        â”‚
        â”œâ”€â”€ Docker Layer: each layer is a filesystem diff
        â”œâ”€â”€ Dockerfile: instructions that create each layer
        â”œâ”€â”€ Container Registry: stores and distributes images
        â”œâ”€â”€ Multi-Stage Build: reduces final image size
        â””â”€â”€ Container: a running instance of an image
```

---

### ðŸ’» Code Example

{%- raw -%}
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
# dive nginx:1.24  â†’ shows each layer's filesystem changes interactively

# Export/import (for air-gapped environments)
docker save myapp:1.0 | gzip > myapp_1.0.tar.gz      # export to tar
docker load < myapp_1.0.tar.gz                        # import on another machine

# Scan image for vulnerabilities
docker scout cves nginx:1.24                          # Docker Scout (built-in)
# or: trivy image nginx:1.24  (Aqua Trivy, widely used)
```
{%- endraw -%}

---

### âš ï¸ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Deleting a container deletes the image                 | `docker rm` removes the container (its writable layer). The image remains until `docker rmi`. Containers are instances; images are templates.                                                                                                                                                             |
| `:latest` tag means most recently pushed to Docker Hub | `latest` is just a convention â€” image publishers are expected to tag their most recent stable release as `latest`, but it's not enforced. Some projects don't update `latest` or use it for a different branch. Never rely on `latest` in production.                                                     |
| A smaller image is always better                       | Smaller images reduce attack surface and pull time. BUT: distroless/scratch images lack debugging tools (no shell, no curl). For production: use slim/distroless and accept limited debuggability. For debugging: have a separate debug image or use `kubectl debug` / `docker run --pid=container:<id>`. |

---

### ðŸ”¥ Pitfalls in Production

```
PITFALL: secrets baked into image layers

  # âŒ DANGEROUS: API key in RUN command (becomes part of image layer)
  FROM ubuntu:22.04
  RUN export API_KEY=sk-secret-123 && curl -H "Authorization: $API_KEY" ...
  # Even if you unset API_KEY in a later layer, it's in layer N's history
  # docker history --no-trunc shows the full command including the secret
  # Anyone with docker pull access can read the secret

  # âœ… CORRECT: use build secrets (Docker BuildKit)
  # syntax=docker/dockerfile:1
  FROM ubuntu:22.04
  RUN --mount=type=secret,id=api_key \
      API_KEY=$(cat /run/secrets/api_key) && \
      curl -H "Authorization: $API_KEY" ...
  # Secret available ONLY during this build step; not baked into any layer

  # Build: docker buildx build --secret id=api_key,src=./api_key.txt .

PITFALL: using :latest tag causes surprise upgrades

  # âŒ Kubernetes deployment (will pull latest on node restart)
  containers:
  - name: myapp
    image: nginx:latest     # â† what version is this today? next week?

  # âœ… Pin to specific version
  containers:
  - name: myapp
    image: nginx:1.24.0     # explicit version
  # or even better:
    image: nginx@sha256:3b4def...  # cryptographic pin
```

---

### ðŸ”— Related Keywords

- `Docker Layer` â€” each layer is a filesystem diff; caching and sharing
- `Dockerfile` â€” instructions that generate each image layer
- `Docker Build Context` â€” files sent to Docker daemon during `docker build`
- `Multi-Stage Build` â€” reduce image size by discarding build-time layers
- `Container Registry` â€” stores, tags, and distributes images

---

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ IMAGE = manifest + config + ordered layers (SHA256)      â”‚
â”‚ LAYER: read-only filesystem diff (tar archive)           â”‚
â”‚ SHARED: layers shared on disk across images/containers   â”‚
â”‚ TAGS: mutable (latest can change) â†’ don't use in prod   â”‚
â”‚ DIGESTS: immutable sha256 â†’ pin in production            â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Rules:                                                   â”‚
â”‚ â€¢ Never bake secrets into layers                        â”‚
â”‚ â€¢ Pin to digest (not tag) in production K8s             â”‚
â”‚ â€¢ Order Dockerfile: rarely changed â†’ frequently changed â”‚
â”‚   (base â†’ deps â†’ code) for optimal layer caching        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

**Q1.** Multi-architecture images (multi-platform manifests) allow the same `nginx:1.24` tag to serve both `linux/amd64` and `linux/arm64`. The registry stores a "manifest list" (OCI image index) that maps platform to the appropriate platform-specific manifest. When `docker pull nginx:1.24` runs on an ARM machine, how does Docker know to pull the ARM image? What happens in Kubernetes when you have a mixed ARM + x86 node pool and deploy `nginx:1.24` â€” which image does each node pull?

**Q2.** Distroless images (from Google) contain only the application and its runtime dependencies â€” no shell, no package manager, no OS utilities. A `gcr.io/distroless/java17-debian11` image is ~50MB vs `openjdk:17-jdk` at ~350MB. What are the security benefits of distroless? What operational challenges does it create (debugging, shell access, `kubectl exec`)? How do you debug a running distroless container in production?
