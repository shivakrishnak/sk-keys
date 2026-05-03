---
layout: default
title: "OCI Standard"
parent: "Containers"
nav_order: 837
permalink: /containers/oci-standard/
number: "0837"
category: Containers
difficulty: ★★★
depends_on: Docker Image, Docker Layer, Container, Docker
used_by: containerd, Container Runtime Interface (CRI), Image Scanning, Image Provenance / SBOM
related: Docker, containerd, Container Runtime Interface (CRI), Image Scanning, Podman
tags:
  - containers
  - docker
  - internals
  - advanced
  - protocol
---

# 837 — OCI Standard

⚡ TL;DR — The OCI Standard is the open specification that defines what a container image IS and how it RUNs, freeing the ecosystem from Docker's proprietary formats.

| #837 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker Image, Docker Layer, Container, Docker | |
| **Used by:** | containerd, Container Runtime Interface (CRI), Image Scanning, Image Provenance / SBOM | |
| **Related:** | Docker, containerd, Container Runtime Interface (CRI), Image Scanning, Podman | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2014, Docker controls the entire container ecosystem: image format, registry protocol, runtime, and tooling are all Docker-specific. When CoreOS builds `rkt`, a competing container runtime, their images are incompatible with Docker images. When Google builds Kubernetes, it must either depend on Docker (giving one vendor enormous leverage over the ecosystem) or standardise on nothing. AWS builds its own runtime. Red Hat builds its own runtime. Every runtime has a unique image format. Tools that build images must target every runtime. Operators who deploy containers must use exactly the right runtime for each image format. The ecosystem fragments.

**THE BREAKING POINT:**
Ecosystem fragmentation means vendors cannot innovate independently. Every new runtime must solve the same problems from scratch. Every image build tool must support every format. No one can switch runtimes without rebuilding all their images. The cloud-native ecosystem stalls.

**THE INVENTION MOMENT:**
This is exactly why the Open Container Initiative (OCI) was founded in 2015 by Docker, CoreOS, Google, AWS, Red Hat, and others — to define open, vendor-neutral specifications for container image format and runtime behaviour. Any compliant image runs in any compliant runtime. Any compliant runtime runs on any compliant image. Standards replace vendor lock-in.

---

### 📘 Textbook Definition

The **OCI Standard** (Open Container Initiative) comprises three interrelated specifications: the **OCI Image Format Specification** (how a container image is structured and stored), the **OCI Runtime Specification** (how a runtime creates and runs a container from an image), and the **OCI Distribution Specification** (how images are pushed to and pulled from a registry). Together they define a complete, vendor-neutral contract: any OCI-compliant image can be run by any OCI-compliant runtime and stored in any OCI-compliant registry. The OCI was founded in 2015 under the Linux Foundation and publishes specifications as open standards.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OCI is the open standard that makes container images and runtimes interchangeable, like USB standardised device connectors.

**One analogy:**
> Before USB, every peripheral — keyboard, mouse, printer, camera — had its own connector. Computers needed a different port for each device. USB standardised the connector: any USB device plugs into any USB port, regardless of manufacturer. The OCI Standard does this for containers: any OCI image runs in any OCI runtime (Docker, containerd, Podman, rkt, etc.) and is stored in any OCI registry (Docker Hub, ECR, GCR, Harbor). The connector is standardised. The vendors compete on quality, not on lock-in.

**One insight:**
The OCI Standard's most consequential effect was enabling Kubernetes to define a generic runtime interface (CRI) that talks to ANY OCI-compliant runtime. This allowed Docker to be replaced as Kubernetes's default runtime (with containerd and CRI-O) without any change to image formats or Kubernetes itself. Standards enable competition. Competition improves everything.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A container image must be a portable, content-addressable, layered archive — independent of any specific runtime or registry.
2. A container runtime must deterministically produce a running process from a given image and configuration.
3. The image distribution protocol must be registry-agnostic and support content verification.

**DERIVED DESIGN:**

The OCI defines three specifications:

**1. OCI Image Format Specification:**
An OCI image is a content-addressable bundle stored as a manifest + configuration + layers:
```
OCI Image
├── manifest.json          (index of all parts, with digests)
├── config.json            (metadata: entrypoint, env, labels)
└── layers/
    ├── sha256:abc123.tar.gz  (layer 1 — base OS)
    ├── sha256:def456.tar.gz  (layer 2 — runtime)
    └── sha256:ghi789.tar.gz  (layer 3 — application)
```
Every component is identified by its SHA256 digest. Immutability and integrity are guaranteed by content addressing. Layers are compressed tarballs of filesystem changes (additions/deletions). The manifest references all components by digest — any tampering changes the digest and invalidates the reference.

**2. OCI Runtime Specification:**
Defines `config.json` — the container configuration that a runtime must honour. Specifies: process (entrypoint, args, env), mounts, namespaces to create, cgroups limits, capabilities, seccomp profile, rootfs path. The runtime spec is the contract between image builder and runtime operator.

**3. OCI Distribution Specification:**
Defines the HTTP API for registry interactions: `GET /v2/<name>/manifests/<reference>` (pull manifest), `PUT /v2/<name>/blobs/uploads/` (push layer), `HEAD /v2/<name>/blobs/<digest>` (check existence). All registries implementing this spec are interoperable: pull from Docker Hub, push to ECR, replication tools work universally.

**THE TRADE-OFFS:**

**Gain:** Vendor-neutral ecosystem. Tools, images, and runtimes interoperate. No vendor lock-in on image format.

**Cost:** Specification versioning requires careful management. OCI Image Spec v1.1 introduced new features (annotations, referrers API) not supported by older registries. Interoperability is only as good as conformance — some vendors implement partial subsets.

---

### 🧪 Thought Experiment

**SETUP:**
Your organisation builds container images using Docker on developer machines. You run Kubernetes on production. Kubernetes 1.24 removed the dockershim (the compatibility shim that allowed Kubernetes to use the Docker daemon as a runtime). Your operations team considers this a crisis.

**WHAT HAPPENS WITHOUT OCI:**
Without a standard, Docker images and Kubernetes are tightly coupled. When Kubernetes removes Docker support, you must either keep Docker in the chain, convert all images to a different format, or accept that your existing 10,000 images are no longer runnable. The migration is a years-long project.

**WHAT HAPPENS WITH OCI:**
Because Docker has produced OCI-compliant images since Docker Engine 18.09, and containerd (the new Kubernetes default runtime) is fully OCI-compliant, nothing changes. Your Dockerfiles still work. Your `docker build` commands still work. Your images in Docker Hub or ECR are OCI images. containerd runs them identically to Docker. The "removal of Docker" from Kubernetes is an infrastructure concern, not an image compatibility concern. Business as usual.

**THE INSIGHT:**
Standards insulate application developers from infrastructure changes. OCI means that "we changed our runtime" is an infrastructure event, not an application event. This is the entire value of standardisation.

---

### 🧠 Mental Model / Analogy

> The OCI Standard is the container ecosystem's equivalent of ISO shipping container standards. Before ISO 668 standardised shipping container dimensions in 1968, every shipping line had different-sized containers. A container that fit a Maersk ship couldn't fit a COSCO crane. Ports had to build custom equipment for each line. After standardisation, any ISO container could be loaded onto any compliant ship, crane, truck, and train — regardless of who manufactured them.

Mapping:
- "ISO shipping container standard" → OCI Standard
- "Container dimensions" → image format (manifest, config, layers)
- "Different shipping lines" → Docker, containerd, Podman, rkt
- "Ships, cranes, trucks" → runtimes and registries
- "Any ISO container on any compliant ship" → any OCI image in any OCI runtime

Where this analogy breaks down: ISO containers are passive physical objects. OCI image layers are active software — the runtime spec adds behavioural requirements (namespaces, cgroups) that have no physical equivalent.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The OCI Standard is an agreement between companies on what a container image looks like and how it runs. It means you can build an image with Docker and run it with any other compatible tool — just like a standard electrical plug fits any compatible socket.

**Level 2 — How to use it (junior developer):**
As a developer, OCI is largely invisible. When you run `docker build`, Docker produces an OCI-compliant image by default (since Docker 18.09). This image can be pushed to any OCI-compliant registry (Docker Hub, ECR, GCR, Harbor, Nexus) and run by any OCI runtime (Docker, containerd, Podman). You rarely need to think about OCI explicitly unless working with advanced tooling like BuildKit, Buildah, or registries that expose OCI manifests directly.

**Level 3 — How it works (mid-level engineer):**
The OCI Image Spec defines the manifest JSON (a content-addressed index of the image's config and layer digests), the config JSON (entrypoint, env vars, port metadata), and the layer tarballs (compressed filesystem diffs). Content addressing means every component is identified by its SHA256 digest — providing integrity guarantees and deduplication. The OCI Runtime Spec defines `config.json` — the specification a runtime must execute, covering namespaces (pid, net, mnt, uts, ipc), cgroups limits, capabilities, and seccomp profiles. The OCI Distribution Spec is the HTTP API that all registries must implement for push/pull.

**Level 4 — Why it was designed this way (senior/staff):**
Content addressing (SHA256 digests as identifiers) was a deliberate choice inspired by Git's content-addressable storage. It provides three properties in one: immutability (changing content changes the digest), integrity (any tampered layer is detected), and deduplication (identical layers share storage across images). The separation into three distinct specifications (image, runtime, distribution) was architecturally deliberate — it decouples build tools (which produce images), runtimes (which execute images), and registries (which store images) so each can evolve independently. OCI Image Spec v1.1 (2023) introduced the "referrers API" — allowing attestations, SBOMs, and signatures to be stored as OCI artifacts alongside the images they describe, enabling supply chain security tooling (Sigstore, ORAS) without modifying the core image format.

---

### ⚙️ How It Works (Mechanism)

**OCI Image Structure (content-addressable):**
```
┌──────────────────────────────────────────────────────────┐
│              OCI Image Layout                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  oci-layout (version marker)                             │
│  index.json                                              │
│    └── manifests:                                        │
│         ├── digest: sha256:aaa (linux/amd64)             │
│         └── digest: sha256:bbb (linux/arm64)             │
│                                                          │
│  blobs/sha256/                                           │
│    ├── aaa  ← manifest.json                              │
│    │    ├── config: sha256:ccc                           │
│    │    └── layers: [sha256:ddd, sha256:eee]             │
│    ├── ccc  ← config.json (entrypoint, env, etc.)        │
│    ├── ddd  ← layer 1 tarball (base OS)                  │
│    └── eee  ← layer 2 tarball (application)             │
└──────────────────────────────────────────────────────────┘
```

**Pull workflow (OCI Distribution Spec):**
1. Client requests manifest: `GET /v2/<name>/manifests/<tag>` → receives manifest JSON with layer digests
2. Client checks local cache for each layer digest
3. Client fetches missing layers: `GET /v2/<name>/blobs/<digest>` → compressed tarball
4. Client verifies each layer's SHA256 matches the manifest reference
5. Client unpacks layers in order, applying whiteout files to simulate deletions
6. Runtime reads config.json to determine entrypoint, env, exposed ports
7. Runtime creates `config.json` (Runtime Spec format) from image config
8. Runtime invokes the low-level OCI runtime (`runc`) with the config

**OCI Runtime Spec execution flow:**
```
┌──────────────────────────────────────────────────────────┐
│           OCI Runtime Create/Start Flow                  │
├──────────────────────────────────────────────────────────┤
│  containerd receives RunPodSandbox (from kubelet)        │
│       ↓                                                  │
│  containerd unpacks image layers → rootfs                │
│       ↓                                                  │
│  containerd generates config.json (OCI Runtime Spec)     │
│  {process, mounts, namespaces, cgroups, seccomp}         │
│       ↓                                                  │
│  containerd calls: runc create <id> --bundle <dir>       │
│       ↓                                                  │
│  runc: create Linux namespaces (pid, net, mnt, uts)      │
│  runc: configure cgroup limits (CPU, memory)             │
│  runc: apply seccomp/apparmor profiles                   │
│  runc: pivot_root to container rootfs                    │
│  runc: exec container entrypoint                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer: docker build → OCI image ← YOU ARE HERE
  → docker push → OCI registry (Docker Hub / ECR / GCR)
  → Kubernetes: kubelet → CRI → containerd
  → containerd pulls OCI image from registry
  → containerd unpacks layers
  → runc executes OCI runtime spec → running container
```

**FAILURE PATH:**
```
OCI spec version mismatch:
  → Registry stores OCI Image Spec v1.1 manifest
  → Old containerd supports only v1.0
  → containerd: "unknown media type" error
  → Pod fails to start
  → kubelet reports ImagePullBackOff
```

**WHAT CHANGES AT SCALE:**
At scale, the OCI Distribution Spec's layer deduplication becomes critical — shared base image layers are fetched once and cached. Multi-arch images (OCI Image Index) allow a single tag to reference platform-specific manifests, enabling heterogeneous clusters (amd64 + arm64) without tag management overhead. The OCI Referrers API (v1.1) enables registry-native SBOM and signature storage — at scale, this replaces out-of-band attestation systems.

---

### 💻 Code Example

**Example 1 — Inspect OCI manifest structure:**
```bash
# Pull and inspect an OCI manifest directly
docker manifest inspect nginx:1.25.3

# Use crane (OCI tool) to inspect manifest
crane manifest nginx:1.25.3 | jq .

# Export image in OCI layout format
docker save nginx:1.25.3 | tar -xf - -C ./oci-export/
```

**Example 2 — Build OCI-compliant image with Buildah (no Docker daemon):**
```bash
# Build OCI image without Docker daemon
buildah bud -f Dockerfile -t myapp:latest .

# Inspect resulting OCI manifest
buildah inspect myapp:latest | jq .OCIv1

# Push to OCI-compliant registry
buildah push myapp:latest docker://registry.example.com/myapp:latest
```

**Example 3 — Verify OCI compliance with oras:**
```bash
# ORAS: OCI Registry As Storage — works with any OCI registry
# Attach SBOM as OCI artifact (v1.1 referrers API)
oras attach \
  --artifact-type application/spdx+json \
  registry.example.com/myapp:latest \
  sbom.spdx.json:application/spdx+json

# List referrers (SBOMs, signatures, attestations)
oras discover registry.example.com/myapp:latest
```

---

### ⚖️ Comparison Table

| Specification Era | Image Format | Runtime API | Registry API | Portability |
|---|---|---|---|---|
| Pre-Docker (pre-2013) | None — custom per tool | Custom | Custom | None |
| Docker v1 (2013–2015) | Docker proprietary | libcontainer | Docker Registry v1 | Docker only |
| **OCI v1.0 (2017)** | **OCI Image Spec** | **OCI Runtime Spec** | **OCI Distribution Spec** | **Any OCI tooling** |
| OCI v1.1 (2023) | + Multi-platform index | + Referrers API | + Referrers Spec | + Supply chain tooling |

How to choose: OCI v1.0 is the universal minimum — every modern tool supports it. OCI v1.1 adds supply chain features (SBOMs, signatures via Referrers API) required for compliance-focused organisations. Check registry support before adopting v1.1 features.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "OCI and Docker images are different formats" | Docker images built with Docker Engine 18.09+ ARE OCI images. Docker simply added OCI compliance to their existing format. Pre-18.09 Docker images used Docker Image Spec v2.2 (similar but not identical). |
| "OCI means I don't need Docker to build images" | OCI defines what a valid image IS, not how to build it. You can use Docker, Buildah, Kaniko, or any OCI-compliant builder. OCI is format neutrality, not tooling dictation. |
| "All OCI-compliant runtimes behave identically" | OCI Runtime Spec defines the minimum contract. Runtime implementations add extensions (containerd plugins, Docker volumes, Podman rootless mode). Behaviour beyond the spec varies. |
| "The OCI Distribution Spec means all registries are identical" | They implement the same API but differ in auth, tagging, GC policies, UI, and OCI v1.1 feature support. Registry selection still matters operationally. |
| "OCI Image Spec v1.1 is universally supported" | As of 2024, many tools support v1.0. OCI v1.1 referrers API support varies by registry. Check compatibility before using v1.1 features in production. |

---

### 🚨 Failure Modes & Diagnosis

**Media type unknown error on pull**

**Symptom:**
`containerd` or `crictl` logs: `"unknown media type"` or `"unsupported manifest type"` when pulling an image.

**Root Cause:**
Image was pushed using OCI Image Spec v1.1 `application/vnd.oci.image.manifest.v1+json` but the runtime only recognises v1.0 Docker media types.

**Diagnostic Command / Tool:**
```bash
# Check manifest media type
crane manifest <image> | jq .mediaType

# Check containerd version and supported media types
containerd --version
ctr version
```

**Fix:**
Upgrade containerd to 1.7+ for full OCI v1.1 support. Or rebuild the image using a v1.0-compatible builder.

**Prevention:**
Pin builder and runtime versions together. Test new image format features in staging before rolling to production clusters.

---

**Digest mismatch on layer pull**

**Symptom:**
Pull fails with `"digest mismatch"` or `"unexpected EOF"`. Image pulls partially then fails.

**Root Cause:**
OCI content addressing means any corruption or truncation of a layer blob changes its SHA256 digest. Network errors, registry bugs, or storage corruption trigger this.

**Diagnostic Command / Tool:**
```bash
# Verify image digest from registry
crane digest <image>:<tag>

# Verify local image after pull
docker inspect <image> | jq '.[0].RootFS.Layers'

# Check containerd content store
ctr content ls
```

**Fix:**
Re-pull the image (`docker pull --no-cache <image>`). If persistent, check registry storage integrity.

**Prevention:**
Use immutable image references (digest-based: `nginx@sha256:abc123`) instead of mutable tags in production. Tags can be reassigned; digests cannot.

---

**Multi-arch manifest index mismatch**

**Symptom:**
`exec format error` when starting a container. The container starts on some nodes but not others in a mixed-architecture cluster.

**Root Cause:**
Image was built only for `linux/amd64` but some nodes are `linux/arm64`. The OCI Image Index (multi-arch manifest) is missing the arm64 entry.

**Diagnostic Command / Tool:**
```bash
# Check which platforms are in the image manifest index
docker buildx imagetools inspect <image>

# Or with crane
crane manifest <image> | jq '.manifests[].platform'
```

**Fix:**
```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t <image> --push .
```

**Prevention:**
Build and push multi-platform images for all clusters that mix architectures. Add architecture to CI build matrix.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker Image` — OCI Image Spec is the formalisation of Docker's image format; understand Docker images before OCI
- `Docker Layer` — OCI layers are the same concept formalised; content-addressed tarballs of filesystem changes
- `Container` — OCI Runtime Spec defines how a container is created from an image

**Builds On This (learn these next):**
- `containerd` — containerd is the primary OCI-compliant high-level runtime; it implements the image and distribution specs
- `Container Runtime Interface (CRI)` — Kubernetes's CRI is built on top of OCI runtimes
- `Image Provenance / SBOM` — OCI v1.1 Referrers API enables SBOM and signature storage as OCI artifacts

**Alternatives / Comparisons:**
- `Docker` — Docker pioneered container images; OCI standardised what Docker built
- `Podman` — Podman implements OCI specs without a daemon; competing runtime that builds on OCI
- `Image Scanning` — scanners parse OCI image manifests and layers; OCI standardisation enables universal scanner support

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 3 open specs: image format, runtime       │
│              │ behaviour, registry distribution API      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Container images locked to one vendor's   │
│ SOLVES       │ runtime (Docker); ecosystem fragmentation  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Content addressing (SHA256) gives         │
│              │ immutability + integrity + deduplication  │
│              │ simultaneously                            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — it's the default for all modern  │
│              │ container tooling since 2018              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ OCI v1.1 features: check runtime/registry │
│              │ support first                             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Portability vs innovation velocity        │
│              │ (standards slow down format evolution)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "OCI is the USB standard for containers:  │
│              │  any image, any runtime, any registry"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ containerd → CRI → Image Provenance/SBOM  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The OCI Image Spec uses SHA256 content-addressed digests to identify every component. Production teams often reference images by tag (`nginx:latest`) rather than digest (`nginx@sha256:abc...`). Trace step-by-step what can go wrong when a tag is silently re-pointed to a different digest in your registry, and design a policy that uses OCI's content addressing to prevent this class of failure in a Kubernetes production cluster.

**Q2.** OCI v1.1 introduced the Referrers API, allowing SBOMs, signatures, and attestations to be stored as OCI artifacts alongside the images they describe. At a company with 5,000 container images, 50 new releases per day, and three separate air-gapped environments (dev, staging, prod), what architectural challenges emerge when you try to ensure that SBOM and signature artifacts travel with their images across environment boundaries? What does the OCI Distribution Spec provide to help, and what does it leave to the implementer?

