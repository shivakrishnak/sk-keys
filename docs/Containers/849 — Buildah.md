---
layout: default
title: "Buildah"
parent: "Containers"
nav_order: 849
permalink: /containers/buildah/
number: "0849"
category: Containers
difficulty: ★★★
depends_on: Docker, Dockerfile, OCI Standard, Podman, Linux Namespaces
used_by: CI/CD, Image Scanning, Image Provenance / SBOM
related: Podman, Docker BuildKit, Multi-Stage Build, OCI Standard, Container Security
tags:
  - containers
  - build
  - security
  - advanced
  - linux
---

# 849 — Buildah

⚡ TL;DR — Buildah is a daemonless, rootless OCI image builder that constructs images from Dockerfiles or shell scripts without ever needing a Docker daemon or root privileges.

| #849 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker, Dockerfile, OCI Standard, Podman, Linux Namespaces | |
| **Used by:** | CI/CD, Image Scanning, Image Provenance / SBOM | |
| **Related:** | Podman, Docker BuildKit, Multi-Stage Build, OCI Standard, Container Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Building container images in CI requires the Docker daemon to be running — which means either the CI runner runs as root, or the Docker socket is mounted into the CI container (Docker-in-Docker), granting every CI job implicit root access to the CI infrastructure. In environments with strict security policies — financial services, governments, regulated industries — running a root-privileged daemon just to build OCI images is unacceptable. Kaniko addresses part of this but still requires a privileged container. The fundamental problem: every mainstream image builder of 2017 required root.

**THE BREAKING POINT:**
Image building in security-hardened environments must work without root. The builder must produce standard OCI images, be auditable, and work in rootless CI environments. No existing tool achieved all three.

**THE INVENTION MOMENT:**
This is exactly why Buildah was developed by Red Hat — a command-line tool that builds OCI/Docker images fully daemonless and rootless, manipulating image working containers directly using host filesystem operations, without requiring the Docker daemon at build or run time.

---

### 📘 Textbook Definition

**Buildah** is an open-source command-line tool for building OCI and Docker-compatible container images without requiring a daemon or root privileges. It can build from Dockerfiles (`buildah bud`) or through a scripted low-level API (`buildah from`, `buildah copy`, `buildah run`, `buildah commit`) that gives programmable control over every image layer. Buildah creates "working containers" (writable containers used as build intermediaries) that it can mount, modify, and snapshot into final image layers. As the build backend for Podman and Red Hat OpenShift, Buildah is the reference implementation of OCI image building in the RHEL ecosystem.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Buildah builds container images as a normal user with no daemon running — by manipulating the image filesystem directly.

**One analogy:**
> Building a Docker image with the Docker daemon is like calling a professional printing shop every time you want to produce a document — you hand them your instructions and they print it on their professional-grade machine that requires special operator access. Buildah is like having your own printer at your desk — you do everything yourself, on your own device, without calling a special operator. The output is identical; the process doesn't require anyone else.

**One insight:**
The most powerful feature of Buildah beyond rootlessness is its low-level API: you can build images programmatically by mounting a working container, running shell commands, copying files, and committing layers — all without writing a Dockerfile. This enables image content to be generated dynamically from scripts, making image builds first-class participants in complex build pipelines.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An OCI image is just a series of filesystem snapshots (layers) + metadata (config.json + manifest).
2. Creating these layers requires only: a process that can modify a filesystem and snapshot it. Root is not required if user namespaces are available.
3. Standard OCI compliance means the resulting image runs in any OCI runtime regardless of how it was built.

**DERIVED DESIGN:**

Buildah's build model works at the image layer level:

1. `buildah from <base-image>` → creates a working container (a writable overlay of the base image)
2. `buildah mount <container>` → mounts the working container's filesystem to a host path
3. Operations on the mounted filesystem (copy files, run chroot'd commands, modify configs)
4. `buildah commit <container>` → creates a new immutable image layer from the filesystem diff
5. `buildah push <image>` → pushes the OCI image to a registry

**Dockerfile build (standard mode):**
`buildah bud -f Dockerfile -t myapp:latest .` — interprets Dockerfile instructions via the same mechanism as `docker build` but without needing dockerd or root.

**Script-based build (Buildah API):**
```bash
#!/bin/bash
container=$(buildah from ubuntu:22.04)
buildah run $container -- apt-get update
buildah run $container -- apt-get install -y python3
buildah copy $container ./app.py /app/app.py
buildah config --entrypoint '["python3", "/app/app.py"]' $container
buildah commit $container myapp:latest
buildah rm $container
```

**Rootless mechanism:**
Buildah uses user namespaces for rootless operation. Inside the build's user namespace, operations appear to run as root (installing packages, changing permissions). The kernel translates these to unprivileged operations on the host using `newuidmap`/`newgidmap` mappings from `/etc/subuid`.

**THE TRADE-OFFS:**

**Gain:** Daemonless, rootless, OCI-standard, programmable image building for secure CI environments.

**Cost:** Less tooling ecosystem than Docker/BuildKit. No built-in caching mechanism as sophisticated as BuildKit. The low-level scripted API requires more code than a Dockerfile. Less Windows/Mac support than Docker.

---

### 🧪 Thought Experiment

**SETUP:**
A regulated enterprise CI pipeline needs to build container images for financial services applications. The security team mandates: no root processes in CI, no Docker socket mounts, all image builds auditable (every layer change logged), all images produce an SBOM.

**WHAT HAPPENS WITH DOCKER:**
CI job requires Docker socket mount → implicit root → fails security audit. Docker-in-Docker (privileged container) → also fails. The team is blocked — no compliant way to build images with Docker.

**WHAT HAPPENS WITH BUILDAH:**
CI job runs as a non-root user. `buildah bud -f Dockerfile -t myapp:latest .` builds the image rootlessly using user namespaces. Every `buildah run` command is logged with the container name, command executed, and time. `buildah inspect` produces full image metadata. `buildah` integrates with external SBOM generators (Syft, cosign). Security audit: passes. Compliance: achieved.

**THE INSIGHT:**
Buildah's rootless + daemonless design makes it the tool of choice specifically for security-constrained environments. When Docker's daemon model is architecturally incompatible with an organisation's security policy, Buildah is the standard alternative.

---

### 🧠 Mental Model / Analogy

> Buildah is a cookbook that teaches you to cook meals at home, step by step, with whatever's in your kitchen. Docker's build system is a meal-kit delivery service that sends pre-measured ingredients in a box and has you follow their specific instructions — requiring a specific brand of pan (Docker daemon). Both produce the same dish (OCI image). Buildah gives you full control over every step, requires no delivery subscription (no daemon), and works with any kitchen (any Linux host with user namespace support).

Mapping:
- "Cooking at home" → building with Buildah (no daemon, full control)
- "Meal-kit service's specific pan requirement" → Docker daemon dependency
- "Step-by-step recipe" → Buildah scripted API (buildah from / run / copy / commit)
- "Standard recipe card (Dockerfile)" → `buildah bud -f Dockerfile`
- "The finished dish" → OCI image (identical regardless of builder)

Where this analogy breaks down: Buildah's caching is less sophisticated than BuildKit's. "Cooking from scratch every time" — Buildah doesn't have the same content-addressable cache layer deduplication as BuildKit. For cache-heavy CI workloads, BuildKit's registry cache is more efficient.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Buildah is a tool that creates container images, like Docker's `docker build`, but without needing Docker's background service to be running. It works as a normal user without any special admin access.

**Level 2 — How to use it (junior developer):**
For Dockerfile builds: `buildah bud -t myapp:latest .` — works like `docker build`. To push: `buildah push myapp:latest docker://registry.example.com/myapp:latest`. Buildah is integrated into Podman: `podman build` uses Buildah under the hood. For CI, use `buildah` in your pipeline script directly without Docker daemon setup.

**Level 3 — How it works (mid-level engineer):**
Buildah creates a "working container" by pulling the base image into local OCI storage (`~/.local/share/containers/storage/` in rootless mode) and creating a read-write overlay layer. `buildah run` executes commands inside the working container using `runc` with appropriate namespace setup. `buildah copy` uses the overlay mount to directly copy files into the container's filesystem. `buildah commit` snapshots the overlay diff into a new image layer, computes content hash, and records it in the image manifest. No communication with any daemon occurs during this process.

**Level 4 — Why it was designed this way (senior/staff):**
Buildah's scripted API (as opposed to Dockerfile-only) was designed to address Dockerfile's inherent opacity. A Dockerfile is a specification — you know what's IN the image but you cannot easily know WHY or prove that specific operations were or were not performed. Buildah's API allows integration with external audit systems: every `buildah run` can be logged to an immutable audit trail, every `buildah copy` can verify file hashes before copying. This makes Buildah the preferred tool for supply chain security frameworks (SLSA) where image build provenance must be cryptographically provable. The OCI-first design (no Docker daemon needed to produce images) was also strategic: it positioned Buildah as the builder for the post-Docker era, aligned with the CNCF's direction toward OCI-native tooling (containerd, CRI-O, ORAS).

---

### ⚙️ How It Works (Mechanism)

**Buildah build flow:**
```
┌──────────────────────────────────────────────────────────┐
│         Buildah Build Flow (Dockerfile mode)             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  buildah bud -f Dockerfile -t myapp:latest .             │
│       ↓                                                  │
│  Parse Dockerfile                                        │
│       ↓                                                  │
│  FROM ubuntu:22.04                                       │
│    → pull image to containers/storage                    │
│    → create working container (overlay)                  │
│       ↓                                                  │
│  RUN apt-get install -y python3                          │
│    → buildah run <wc>: spawn runc in working container   │
│    → user namespace: apt-get runs as "root" (UID 100000) │
│    → modifications written to overlay (read-write layer) │
│       ↓                                                  │
│  COPY app.py /app/                                       │
│    → mount working container overlay                     │
│    → copy app.py into mount point                        │
│       ↓                                                  │
│  buildah commit <wc>                                     │
│    → compute SHA256 of overlay diff                      │
│    → create new layer blob                               │
│    → update manifest and config.json                     │
│       ↓                                                  │
│  OCI image: myapp:latest (in local store)                │
│  buildah push → registry                                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
CI pipeline (non-root user)
  → git checkout
  → buildah bud -f Dockerfile -t myapp:main-sha . ← YOU ARE HERE
  → (no Docker daemon, user namespaces only)
  → buildah push myapp:main-sha registry.example.com
  → image available in registry
  → Kubernetes pulls from registry → deployment
```

**FAILURE PATH:**
```
subuid/subgid not configured for CI user:
  → buildah error: "no subuid ranges for user"
  → /etc/subuid missing entry for this user
  → fix: usermod --add-subuids 100000-165535 <ci-user>
```

**WHAT CHANGES AT SCALE:**
At 100+ parallel CI builds, Buildah's per-process model scales naturally — no daemon contention. However, pulling the same base images 100 times is wasteful. Solutions: pre-pull base images to node storage, use registry mirrors, or use Buildah's `--layers` caching with shared storage.

---

### 💻 Code Example

**Example 1 — Dockerfile build with Buildah:**
```bash
# Build from Dockerfile (identical to docker build)
buildah bud -f Dockerfile -t myapp:latest .

# Inspect the image
buildah inspect --type image myapp:latest | jq '.OCIv1'

# Push to registry
buildah push myapp:latest docker://registry.example.com/myapp:latest

# Or push as OCI format
buildah push myapp:latest oci://path/to/oci-layout
```

**Example 2 — Low-level scripted build:**
```bash
#!/bin/bash
set -euo pipefail

# Start from base image
container=$(buildah from --name builder alpine:3.19)

# Run commands inside container
buildah run $container -- apk add --no-cache python3 py3-pip

# Copy application files
buildah copy $container ./src /app/src
buildah copy $container ./requirements.txt /app/

# Install Python dependencies
buildah run $container -- pip3 install -r /app/requirements.txt

# Configure the image
buildah config \
  --workingdir /app \
  --entrypoint '["python3", "src/main.py"]' \
  --label "version=1.0" \
  $container

# Commit to create final image
buildah commit $container myapp:1.0.0

# Cleanup working container
buildah rm $container

echo "Image built: myapp:1.0.0"
```

**Example 3 — Multi-stage build equivalent:**
```bash
#!/bin/bash
# Stage 1: compile
build=$(buildah from golang:1.21)
buildah copy $build ./. /src/
buildah run $build -- sh -c \
  "cd /src && go build -o /app ./cmd/main.go"

# Stage 2: final minimal image
final=$(buildah from gcr.io/distroless/static-debian12)
buildah copy --from $build $final /app /app
buildah config --entrypoint '["/app"]' $final
buildah commit $final myservice:latest

# Cleanup
buildah rm $build $final
```

**Example 4 — Rootless CI with GitHub Actions:**
```yaml
# .github/workflows/build.yml
- name: Build image with Buildah (rootless)
  uses: redhat-actions/buildah-build@v2
  with:
    image: myapp
    tags: latest ${{ github.sha }}
    containerfiles: ./Dockerfile
    context: .

- name: Push image
  uses: redhat-actions/push-to-registry@v2
  with:
    image: myapp
    tags: latest ${{ github.sha }}
    registry: registry.example.com
```

---

### ⚖️ Comparison Table

| Builder | Daemon Required | Root Required | Dockerfile Support | Scripted API | CI Suitability |
|---|---|---|---|---|---|
| **Buildah** | No | No (rootless) | Yes (`bud`) | Yes | Excellent (secure CI) |
| Docker BuildKit | Yes (or buildkitd) | Partial | Yes | Limited | Good |
| Kaniko | No | Privileged container | Yes | No | Good (K8s CI) |
| Podman build | No | No (rootless) | Yes (uses Buildah) | Via Buildah | Excellent |
| ko (Go only) | No | No | No (Go specific) | Yes | Excellent (Go only) |

How to choose: Buildah for rootless, daemonless image building in security-constrained CI. Docker BuildKit for developer workstations with full Docker ecosystem. Kaniko for Kubernetes-native CI (builds inside a K8s pod without Docker). ko for Go-specific fast builds with minimal image overhead.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Buildah and Podman are the same thing" | Buildah builds images; Podman runs containers. They share the same underlying storage library but have distinct purposes. `podman build` uses Buildah under the hood. |
| "Buildah images are different from Docker images" | No. Buildah produces fully OCI-compliant images indistinguishable from Docker-built images. They run on any OCI runtime (Docker, containerd, Podman). |
| "Buildah's scripted API is only for unusual builds" | The scripted API enables builds that are impossible with Dockerfiles — dynamic layer generation, conditional build logic, external tool integration, and audit-friendly build pipelines. |
| "Rootless means I can't install packages in the image" | Package installation (apt-get, dnf, apk) works inside the build's user namespace where the build appears to run as root. The rootlessness is relative to the host; inside the build context, standard operations work. |
| "Buildah is slower than Docker" | For fresh builds, comparable. Without BuildKit's cache, repeat builds may be slower if base images are re-pulled. Use `--layers` flag to enable layer caching in Buildah. |

---

### 🚨 Failure Modes & Diagnosis

**No subuid/subgid ranges configured**

**Symptom:**
`buildah` fails with: `"cannot find newuidmap: exec: no subuid ranges"`  or `"user namespace not mapped"`.

**Root Cause:**
Rootless containers require UID range mappings in `/etc/subuid` and `/etc/subgid`. New CI users may not have these configured.

**Diagnostic Command / Tool:**
```bash
# Check if subuid configured for current user
grep $(whoami) /etc/subuid /etc/subgid

# If missing, configure:
sudo usermod --add-subuids 100000-165535 $(whoami)
sudo usermod --add-subgids 100000-165535 $(whoami)
```

**Prevention:**
In user provisioning automation, always add subuid/subgid ranges for users who will run containers.

---

**Filesystem storage quota exceeded**

**Symptom:**
`buildah bud` fails mid-build with `"no space left on device"`. Working containers accumulate and are not cleaned up.

**Root Cause:**
Each `buildah from` creates a working container. If CI jobs fail mid-build, working containers accumulate and fill storage.

**Diagnostic Command / Tool:**
```bash
# List all working containers
buildah containers

# Check storage usage
du -sh ~/.local/share/containers/storage/

# Remove all dangling working containers
buildah rm --all
```

**Prevention:**
CI cleanup step: `buildah rm --all` after every build, success or failure. Use CI trap/cleanup handlers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dockerfile` — Buildah's `bud` command interprets Dockerfiles; understand Dockerfiles first
- `OCI Standard` — Buildah produces OCI images; understand the image format
- `Podman` — Buildah is the build backend for Podman; they share storage and image formats

**Builds On This (learn these next):**
- `CI/CD` — Buildah is primarily a CI tool for rootless image building
- `Image Provenance / SBOM` — Buildah's scripted API enables detailed provenance tracking
- `Container Security` — rootless Buildah is part of a defence-in-depth container security strategy

**Alternatives / Comparisons:**
- `Docker BuildKit` — Docker's modern build engine with daemon; alternative for non-security-constrained environments
- `Podman` — the runtime companion to Buildah; run what Buildah builds
- `Multi-Stage Build` — Dockerfile feature that Buildah supports via `buildah bud` and its own scripted multi-stage API

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Daemonless, rootless OCI image builder    │
│              │ via Dockerfile or scripted API            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Docker daemon required root for image     │
│ SOLVES       │ builds — unacceptable in secure CI        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Scripted API: build images as code —      │
│              │ every layer operation is programmable,    │
│              │ auditable, and conditionally controlled   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Security-constrained CI (no root, no      │
│              │ daemon), RHEL/OpenShift environments      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Needing Docker Desktop experience or      │
│              │ BuildKit's advanced registry caching      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Security (rootless) vs BuildKit's         │
│              │ cache sophistication + ecosystem          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Buildah builds images without asking     │
│              │  permission from any daemon — or root"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Podman → Image Provenance/SBOM →          │
│              │ Container Security                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An organisation wants to achieve SLSA Level 3 build provenance for their container images. This requires that: builds are performed in an isolated environment on dedicated infrastructure, the build process is fully defined as code, and every build step is logged and signed. Explain how Buildah's scripted API (rather than a Dockerfile) enables each of these SLSA requirements — and describe what additional tooling (Sigstore, ORAS, Tekton) would be required to produce a complete, verifiable SLSA Level 3 provenance attestation alongside the built image.

**Q2.** A DevOps engineer migrates a complex 15-stage Dockerfile from Docker BuildKit to Buildah's scripted API. After migration, builds are 40% slower in CI despite identical layers in the final image. Analyse: what BuildKit cache features were being used (parallel stages, registry cache, content-addressed cache) that Buildah's scripted API does not replicate by default, and describe how to re-implement BuildKit's parallel stage execution in a Buildah script using background processes and explicit synchronization.

