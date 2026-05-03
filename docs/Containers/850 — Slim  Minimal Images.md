---
layout: default
title: "Slim / Minimal Images"
parent: "Containers"
nav_order: 850
permalink: /containers/slim-minimal-images/
number: "0850"
category: Containers
difficulty: ★★★
depends_on: Docker Image, Dockerfile, Multi-Stage Build, Distroless Images, Image Scanning
used_by: Image Scanning, Container Security, CI/CD, Image Tag Strategy
related: Distroless Images, Multi-Stage Build, Container Security, Image Scanning, Docker BuildKit
tags:
  - containers
  - docker
  - security
  - performance
  - advanced
  - bestpractice
---

# 850 — Slim / Minimal Images

⚡ TL;DR — Slim and minimal images strip container images down to only what the application needs to run, reducing attack surface, storage costs, and startup times.

| #850 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker Image, Dockerfile, Multi-Stage Build, Distroless Images, Image Scanning | |
| **Used by:** | Image Scanning, Container Security, CI/CD, Image Tag Strategy | |
| **Related:** | Distroless Images, Multi-Stage Build, Container Security, Image Scanning, Docker BuildKit | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A microservice that prints "Hello World" in Node.js ships as a Docker image based on `node:20`. The image is 1.1GB. It contains: the full Node.js runtime, npm, yarn, Python (for node-gyp), GCC, make, binutils, thousands of Ubuntu packages, bash, curl, wget, git, and every development tool needed to build native addons — none of which are needed to run a pre-built JavaScript file. This 1.1GB image is pulled on every new node in the autoscaling cluster. 100 nodes × 1.1GB = 110GB of network transfer just for one service to start up. The image has 800+ packages, each potentially harboring CVEs.

**THE BREAKING POINT:**
Images inherit everything from their base image. Without deliberate minimisation, production images become bloated with build tooling, development utilities, OS components, and entire programming language toolchains needed only for compilation. Size and attack surface grow unbounded.

**THE INVENTION MOMENT:**
This is exactly why minimal image practices — Alpine Linux, multi-stage builds, distroless, SlimToolkit — were developed: produce the smallest possible image that can correctly execute the application, by separating build tooling from runtime dependencies.

---

### 📘 Textbook Definition

A **slim or minimal container image** is one that includes only the components required for the application to execute at runtime: the application binary/code, its runtime dependencies (language runtime, shared libraries), and essential system files (CA certificates, timezone data). It excludes: package managers, build tools, shells, compilers, development libraries, test frameworks, and documentation. The primary approaches are: **Alpine Linux** (5MB base OS using musl libc), **Multi-stage builds** (build in a full image, copy only artifacts to a minimal runtime image), **Distroless images** (no OS layer at all — only runtime), **Scratch** (completely empty base for statically compiled binaries), and **SlimToolkit** (`slim build`: automated image slimming by analysing runtime behaviour).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Minimal images are container images with all the fat trimmed — only the muscle (runtime code) remains, not the bones and tendons (build tools).

**One analogy:**
> When you move to a new apartment, you pack only what you actually use — not every item from your childhood bedroom. A full Docker base image is like bringing everything from your parents' house: the camping gear you used once, the high school chemistry set, the broken clock. A minimal image is a carefully packed bag: the clothes, toiletries, and laptop you actually need. Less to carry, less that can go wrong, less that a thief can steal.

**One insight:**
Image size and security surface are correlated: every additional package is both more storage *and* more potential CVEs. Minimisation is simultaneously a cost optimisation (storage, network, startup time) and a security improvement (fewer CVEs, no shell for post-exploit attackers). The practices are not in tension — they reinforce each other.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A running container only needs: the application binary, its runtime dependencies, and system-level files it calls at runtime.
2. Every additional package beyond these is unnecessary CVE exposure and storage waste.
3. Build tools (compilers, linkers, package managers) are needed at build time but never at runtime.

**DERIVED DESIGN:**

**Minimal image strategies by use case:**

**Strategy 1: Alpine Linux base**
- Alpine uses musl libc instead of glibc, BusyBox utilities, apk package manager
- Base image: ~5MB (vs Ubuntu: ~77MB, Debian: ~124MB)
- Best for: scripted languages (Python, Go, Node) where a minimal OS is acceptable
- Risk: musl libc subtle ABI differences can break native extensions

**Strategy 2: Multi-stage build (copy artifacts)**
```dockerfile
# Stage 1: Build (full toolchain)
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY . .
RUN mvn package -DskipTests

# Stage 2: Runtime (minimal image)
FROM gcr.io/distroless/java21-debian12
COPY --from=build /src/target/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
# Final image: ~250MB (JRE only, no Maven, no JDK, no OS)
# vs 500MB build image
```

**Strategy 3: Distroless (no OS layer)**
- Only app runtime + direct system libraries
- No shell, no package manager, no busybox
- See entry 835 for full detail

**Strategy 4: Scratch (empty base)**
```dockerfile
FROM scratch               # Empty -- nothing
COPY myapp-static /myapp   # Only the statically compiled binary
ENTRYPOINT ["/myapp"]
# Final image: exact size of your binary (e.g., 6MB for a Go binary)
```
Go and Rust compile to static binaries that can run on scratch.

**Strategy 5: SlimToolkit (`slim build`)**
- Runs the container, instruments all filesystem access via ptrace/eBPF
- Produces a minimal image containing only files actually accessed at runtime
- Automates minimisation for legacy applications that can't be rewritten

**Size comparison for a Java Spring Boot API:**
```
┌────────────────────────────┬──────────┬────────────┐
│ Base Image                 │ Size     │ CVE Count  │
├────────────────────────────┼──────────┼────────────┤
│ eclipse-temurin:21-jdk     │ 428 MB   │ ~180       │
│ eclipse-temurin:21-jre     │ 279 MB   │ ~90        │
│ eclipse-temurin:21-jre-alpine │ 213 MB │ ~40       │
│ gcr.io/distroless/java21   │ 220 MB   │ ~15        │
└────────────────────────────┴──────────┴────────────┘
```

**THE TRADE-OFFS:**

**Gain:** Smaller images (faster pull, less storage, faster cold start). Fewer CVEs (smaller scan surface). No shell for attackers.

**Cost:** Harder debugging (no shell tools). Alpine musl libc compatibility issues for some native extensions. Distroless requires ephemeral containers for debugging. `slim build` may accidentally exclude needed runtime files.

---

### 🧪 Thought Experiment

**SETUP:**
A Node.js Express API. Current base: `node:20` (1.1GB). Deployed on Kubernetes with autoscaling. New nodes frequently join the cluster.

**WHAT HAPPENS WITH FULL NODE IMAGE:**
A new node starts. Kubernetes schedules 10 pods. Each pod pulls `1.1GB = 11GB` of image data. On a 1Gbps link, this takes ~90 seconds before any pod can start. During a traffic spike that triggers autoscaling, pods take 2 minutes to become Ready — the spike has already passed by the time new capacity is available.

**WHAT HAPPENS WITH MINIMAL NODE IMAGE (node:20-alpine):**
Image size: 180MB. Same 10 pods pull `1.8GB total`. Pull time: ~15 seconds. Pod ready within 20 seconds. Autoscaling responds to traffic spikes effectively.

**THE INSIGHT:**
Image minimisation directly impacts scaling responsiveness. In autoscaling scenarios, image pull time is the dominant factor in pod startup latency. A 6x image size reduction produces a 6x improvement in cold-start time — directly translating to better user experience during traffic spikes.

---

### 🧠 Mental Model / Analogy

> A minimal image is a racing bicycle stripped to the essentials: frame, wheels, handlebars, pedals, chain. A full base image is a cargo bicycle with a basket, a kickstand, lights, a lock, a child seat, mudguards, and a bell — useful features that add drag and weight. For daily urban commuting, all those features matter. For a race, every gram of unnecessary weight costs you. Container production environments are races: only the essentials belong on the bike.

Mapping:
- "Racing bicycle frame" → application binary + direct dependencies
- "Cargo bike attachments" → bash, curl, apt, gcc, test frameworks
- "Weight slowing the race" → startup latency + image pull time + CVEs
- "Deciding what stays" → multi-stage build + distroless selection

Where this analogy breaks down: a racing bike stripped of its lights is dangerous on the road. A "stripped" container that accidentally removes a needed shared library causes subtle runtime failures — harder to diagnose than a build error.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Minimal images are container images with all unnecessary software removed. Like packing only what you actually need for a trip instead of your entire wardrobe. The result is smaller, faster to download, and harder for attackers to misuse.

**Level 2 — How to use it (junior developer):**
Use `FROM node:20-alpine` instead of `FROM node:20` for Node apps. Use multi-stage builds to separate the build environment from the runtime image. For Go: compile a static binary and use `FROM scratch`. For Java: use `gcr.io/distroless/java21-debian12` as the runtime base. Start with multi-stage builds — it's the most widely applicable pattern.

**Level 3 — How it works (mid-level engineer):**
Multi-stage builds work because Docker/Buildah only includes layers from the final stage in the pushed image. The `COPY --from=build` instruction copies individual files or directories from a previous stage's filesystem into the current stage — without carrying forward that stage's layers. For Alpine images: the size reduction comes from replacing glibc with musl libc (~650KB vs ~1.5MB), BusyBox for GNU coreutils (~1MB vs ~10MB), and removing most development packages. Static binaries (Go, Rust) can use `FROM scratch` because `scratch` is a special empty image — zero bytes — and a statically compiled binary has all its dependencies linked in at compile time.

**Level 4 — Why it was designed this way (senior/staff):**
The multi-stage build solution is architecturally significant: it solves the "build environment contamination" problem by making build artifacts promotion across stage boundaries explicit. You must name what you want: `COPY --from=build /app/dist /app/dist`. Everything else is implicitly excluded. This is the opposite of the legacy pattern (install build tools, build, try to clean up, fail to achieve minimal result). Alpine's architectural choices — musl libc, BusyBox, apk — were made for embedded Linux and early container use. The musl/glibc compatibility issue was a known trade-off: musl is intentionally minimal and strict, which occasionally breaks assumptions in software written for glibc (thread cancellation semantics, locale data, certain regex extensions). For scripted languages (Python, Ruby, Node with pure-JS packages), Alpine works perfectly. For native extensions, Alpine-specific compatibility testing is required.

---

### ⚙️ How It Works (Mechanism)

**Multi-stage build: what gets included:**
```
Stage 1 (maven:3.9-jdk-21):
  Layers: maven base + JDK + maven repo + compiled JAR
  │
  └── COPY --from=build target/app.jar /app.jar
                    ↑
                Only this file crosses the stage boundary

Stage 2 (distroless/java21):
  Layers: distroless base layers + app.jar
  │
  Final image: ONLY stage 2 layers
  (stage 1's 500MB of Maven and JDK layers are discarded)
```

**Alpine internal structure:**
```
Alpine:3.19 (~5MB)
  ├── musl libc (~650KB)       # C standard library
  ├── BusyBox (~1MB)           # Core utilities (ash, ls, cat, etc.)
  ├── apk (package manager)    # Alpine Package Keeper
  └── /etc/ssl/certs/          # CA certificates
# Everything else: only what you install explicitly
```

**Scratch base:**
```
FROM scratch                    # 0 bytes — truly empty
COPY --chmod=755 app /app       # Statically compiled binary
ENTRYPOINT ["/app"]             # Must be statically linked
# Final image = exact binary size + metadata (~6MB for Go binary)
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (multi-stage):**
```
Dockerfile (multi-stage)
  → Build stage: full toolchain (Maven/JDK/npm/webpack)
  → Build executes: code compiled, tests run ← YOU ARE HERE
  → Runtime stage: minimal base + copy artifacts
  → docker build → final image: ~220MB (vs ~500MB full)
  → push to registry
  → K8s: pull 220MB (vs 500MB) → faster cold starts
```

**FAILURE PATH:**
```
Missing runtime dependency (stripped too aggressively):
  → Container starts, gets request
  → Runtime error: "shared library not found: libcrypto.so.1.1"
  → The library was removed in image minimisation
  → Fix: add missing library to runtime stage
  → COPY from build stage or install specifically in runtime stage
```

**WHAT CHANGES AT SCALE:**
At scale with 10,000 container starts per day, image pull time dominates cold start latency. A 300MB image vs a 900MB image represents 600MB less data per pull — at 1Gbps that's 5 seconds per pull × 10,000 = 14 hours of cumulative bandwidth saved daily. For global registry distribution, bandwidth costs are also real dollars.

---

### 💻 Code Example

**Example 1 — Node.js: slim Alpine build:**
```dockerfile
# Multi-stage Alpine Node.js build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production   # production deps only
COPY . .
RUN npm run build               # TypeScript compile

FROM node:20-alpine             # Runtime: Alpine only
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
USER node                       # Non-root
ENTRYPOINT ["node", "dist/index.js"]
# Final image: ~180MB (vs ~1.1GB with node:20)
```

**Example 2 — Go: scratch build (truly minimal):**
```dockerfile
FROM golang:1.21 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
# Build static binary: no external dependencies
RUN CGO_ENABLED=0 GOOS=linux go build \
  -ldflags="-w -s" \   # strip debug symbols
  -o /app ./cmd/main

FROM scratch             # Zero-byte base
COPY --from=build /app /app
COPY --from=build /etc/ssl/certs /etc/ssl/certs  # CA certs for HTTPS
ENTRYPOINT ["/app"]
# Final image: ~8MB
```

**Example 3 — Java: distroless runtime:**
```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY pom.xml .
RUN mvn dependency:go-offline   # Cache deps
COPY src ./src
RUN mvn package -DskipTests

FROM gcr.io/distroless/java21-debian12
COPY --from=build /src/target/app.jar /app.jar
ENTRYPOINT ["java", "-Xmx512m", "-jar", "/app.jar"]
# Final image: ~220MB (vs ~500MB with JDK image)
```

**Example 4 — Compare image sizes:**
```bash
# Build both versions
docker build -f Dockerfile.full -t myapp:full .
docker build -f Dockerfile.minimal -t myapp:minimal .

# Compare sizes
docker images | grep myapp
# myapp  minimal  xxx  250MB
# myapp  full     xxx  1.1GB

# Compare CVE counts
trivy image myapp:full --format table | grep CRITICAL
trivy image myapp:minimal --format table | grep CRITICAL
```

---

### ⚖️ Comparison Table

| Approach | Size | CVE Surface | Shell Available | Debug Ease | Best For |
|---|---|---|---|---|---|
| Full base (ubuntu, debian) | 500MB–1.1GB | High (300+ pkgs) | Yes | Easy | Dev/build images only |
| **Alpine base** | 50–250MB | Low (50–100 pkgs) | Yes (ash) | Moderate | Small OSS images with shell |
| Distroless | 50–250MB | Very low (5–20 pkgs) | No | Hard (ephemeral containers) | Production Java/Python/Go |
| Scratch | App size only | Zero (OS) | No | Very hard | Statically compiled binaries |
| SlimToolkit | 80% smaller than original | Optimised | Depends | Moderate | Legacy apps without Dockerfile refactoring |

How to choose: Alpine for any app needing a package manager or shell. Distroless for current best-practice Java/Python/Node production images. Scratch for Go/Rust statically compiled services. SlimToolkit when you can't refactor the Dockerfile but need to reduce size urgently.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Alpine is always smaller than distroless" | Not for JVM languages. `eclipse-temurin:21-jre-alpine` is ~213MB. `gcr.io/distroless/java21` is ~220MB — similar size, but distroless has far fewer CVEs because there's no Alpine package infrastructure. |
| "FROM scratch won't work with dynamic binaries" | Correct for dynamically linked binaries. Scratch requires `CGO_ENABLED=0` for Go or explicit `musl-linked` Rust. A dynamically linked binary on scratch fails with 'exec format error' or 'no such file or directory' (missing ld.so). |
| "Smaller images are always better" | Smaller images with missing runtime dependencies cause hard-to-diagnose production failures. The minimum viable image must include ALL files accessed at runtime — no more, no less. |
| "I should minimise by deleting files after installation" | Adding files and then deleting them in separate RUN instructions still creates layers with those files. The files are invisible in the final filesystem but exist in lower layers. Use multi-stage builds instead. |
| "Alpine causes performance problems with Java" | Alpine's musl libc causes specific JVM performance issues: slower thread creation due to musl's stack implementation, potential Java DNS resolution differences. For JVM workloads, distroless (Debian-based) is preferred over Alpine. |

---

### 🚨 Failure Modes & Diagnosis

**Runtime "library not found" errors after minimisation**

**Symptom:**
Container fails to start with: `error while loading shared libraries: libc.so.6: cannot open shared object file`. Works in the full build image, fails in the minimal runtime image.

**Root Cause:**
Application requires shared library (`libc`, `libssl`, custom library) not present in the minimal runtime image.

**Diagnostic Command / Tool:**
```bash
# Find all shared libraries the binary needs
docker run --rm -it --entrypoint ldd myapp:minimal /myapp
# Lists all dynamic library dependencies (if ldd is available)

# Alternative: strace the startup
docker run --rm myapp:minimal strace -e trace=open /myapp 2>&1 | grep "No such file"

# For Alpine: use readelf
readelf -d /myapp | grep NEEDED
```

**Fix:**
In runtime stage, install the missing library explicitly: `RUN apk add --no-cache libssl3` or `COPY --from=build /usr/lib/libssl.so.3 /usr/lib/`.

**Prevention:**
Test the minimal image against your full integration test suite immediately after building. Add a CI step that starts the minimal container and performs smoke tests before pushing to the registry.

---

**Alpine musl libc timezone/locale issues**

**Symptom:**
Application returns wrong timezones. Date formatting breaks. `java.util.TimeZone.getDefault()` returns UTC regardless of system setting on Alpine.

**Root Cause:**
Alpine's minimal base doesn't include timezone data by default. The JVM, Python, and other runtimes may need `tzdata` package.

**Diagnostic Command / Tool:**
```bash
# Check timezone data presence
docker run --rm myapp:alpine ls /usr/share/zoneinfo/
# If empty: tzdata not installed
```

**Fix:**
```dockerfile
FROM alpine:3.19
RUN apk add --no-cache tzdata    # Add timezone data
ENV TZ=America/New_York
```

**Prevention:**
Always test locale and timezone-dependent functionality with minimal images before production deployment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dockerfile` — minimisation is primarily a Dockerfile engineering problem
- `Multi-Stage Build` — the primary technique for minimal images
- `Distroless Images` — the deeper exploration of the minimal/no-OS extreme

**Builds On This (learn these next):**
- `Image Scanning` — minimal images drastically reduce CVE scan findings
- `Container Security` — minimal images are one layer of container security defence
- `Docker BuildKit` — BuildKit's parallel stages enhance the efficiency of multi-stage minimal builds

**Alternatives / Comparisons:**
- `Distroless Images` — the extreme of minimal images: no OS components at all
- `Multi-Stage Build` — the technique that enables minimal runtime images from full build environments
- `Image Scanning` — the tool that measures the security improvement from minimisation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Images containing only what runs the app: │
│              │ no build tools, no shells, no extras      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Full images: 1GB+, 300+ CVEs, slow pulls, │
│ SOLVES       │ large attack surface, bloated registries  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Multi-stage builds: build fat, ship lean. │
│              │ Only COPY artifacts across stage          │
│              │ boundaries — layers don't follow.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every production image — no exceptions    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Development/CI build images (need tools)  │
│              │ Scratch: unless binary is truly static    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Security + speed vs debuggability +       │
│              │ compatibility testing effort              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build fat. Ship lean. Separate build     │
│              │  tools from runtime reality."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distroless Images → Image Scanning →      │
│              │ Container Security                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Python ML service uses NumPy, SciPy, and OpenCV — all of which depend on native C libraries (BLAS, LAPACK, OpenCV shared objects). Currently built on `python:3.12` (900MB). You want to minimise the image using Alpine + multi-stage build. Trace step-by-step the compatibility challenges you would encounter (musl libc vs glibc, numpy compilation, OpenCV dependencies), and design the Dockerfile strategy that produces the smallest possible image while correctly running the application. What is the minimum viable base image, and what trade-offs does your choice make?

**Q2.** Your organisation uses SlimToolkit to automatically minimise images by tracing runtime file access. A service has been running in production for 6 months with the slimmed image. One day, a code update activates a code path never previously executed in production (an error-handling routine that writes a structured log to a file format only used in error scenarios). The slimmed image doesn't include the library needed for that code path. Describe the failure mode, trace how this slimmed-too-aggressively scenario creates a worse failure than a missing feature, and design a testing strategy for SlimToolkit-generated images that exercises error paths and edge cases.

