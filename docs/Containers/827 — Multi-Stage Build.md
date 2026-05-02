---
layout: default
title: "Multi-Stage Build"
parent: "Containers"
nav_order: 827
permalink: /containers/multi-stage-build/
number: "827"
category: Containers
difficulty: ★★☆
depends_on: "Dockerfile, Docker Layer, Docker Build Context"
used_by: "Container Registry, Kubernetes deployments, CI-CD pipelines"
tags: #containers, #docker, #multi-stage, #build-optimization, #image-size
---

# 827 — Multi-Stage Build

`#containers` `#docker` `#multi-stage` `#build-optimization` `#image-size`

⚡ TL;DR — **Multi-stage builds** use multiple `FROM` instructions in one Dockerfile to separate build-time and runtime concerns. Build stage: install compilers, run tests, compile. Final stage: copy only the output artifact into a minimal image. Build tools, source code, and test dependencies are NOT in the final image. Result: 10-20x smaller images with no build tools attack surface.

| #827 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Dockerfile, Docker Layer, Docker Build Context | |
| **Used by:** | Container Registry, Kubernetes deployments, CI-CD pipelines | |

---

### 📘 Textbook Definition

**Multi-stage build**: a Dockerfile feature (introduced in Docker 17.05) that allows multiple `FROM` instructions in a single Dockerfile. Each `FROM` instruction starts a new build stage with its own base image and layer set. Files can be copied between stages using `COPY --from=<stage>`. Only the final stage's layers are included in the output image — all intermediate stages are discarded. Named stages: `FROM ubuntu AS builder` allows `COPY --from=builder`. By stage index: `COPY --from=0`. Stages can be based on completely different base images (e.g., large build image → tiny runtime image). Benefits: (1) single Dockerfile (one source of truth); (2) final image contains only runtime artifacts (no build tools, no source code, no test dependencies); (3) smaller attack surface; (4) smaller image (faster push/pull); (5) build caching still works per stage (expensive compile step cached if source unchanged).

---

### 🟢 Simple Definition (Easy)

The problem: to compile a Go binary, you need the Go compiler (500MB). But to RUN the binary, you only need the binary (5MB). Without multi-stage builds, the final image includes the Go compiler — 500MB of attack surface that's useless at runtime.

Multi-stage build: Stage 1 uses the Go image, compiles the binary. Stage 2 starts from `scratch` (empty), copies only the binary. Final image: 5MB. The compiler stage is discarded — it's used only during build, not included in the final image.

---

### 🔵 Simple Definition (Elaborated)

Multi-stage builds solve the fundamental tension in container images: build-time needs (compilers, package managers, SDKs, test frameworks) vs runtime needs (minimal attack surface, small image, fast pull). Before multi-stage builds, teams maintained two Dockerfiles: one for building (large) and one for deploying (small), with a shell script to orchestrate: build → extract binary → build small image. Multi-stage builds collapse this into one Dockerfile, keeping the build/runtime separation without the complexity.

Common pattern:
- **Stage 1 (deps)**: install exact dependencies with lockfile (`npm ci`, `pip sync`)
- **Stage 2 (builder)**: copy deps + source, compile/test, produce artifacts
- **Stage 3 (runtime)**: copy ONLY artifacts into minimal base (alpine, distroless, scratch)

---

### 🔩 First Principles Explanation

```
BEFORE MULTI-STAGE (anti-pattern):

  FROM node:18             ← 900MB base (Node + npm + build tools)
  WORKDIR /app
  COPY . .
  RUN npm install          ← installs dev + prod deps (300MB)
  RUN npm run build        ← TypeScript compile
  CMD ["node", "dist/server.js"]
  
  Final image: ~1.2GB
  Contents: Node runtime + npm + TypeScript compiler + source code + test deps + dist/
  Security: TypeScript compiler and test dependencies in production? npm in production?

AFTER MULTI-STAGE:

  # Stage 1: install exact production dependencies
  FROM node:18-alpine AS deps
  WORKDIR /app
  COPY package.json package-lock.json ./
  RUN npm ci --only=production   ← only production deps; no devDependencies
  
  # Stage 2: build (has devDependencies for TypeScript)
  FROM node:18-alpine AS builder
  WORKDIR /app
  COPY package.json package-lock.json ./
  RUN npm ci                     ← all deps (prod + dev: TypeScript etc.)
  COPY --from=deps /app/node_modules ./node_modules  ← wait, override with prod deps
  COPY src/ ./
  RUN npm run build              ← TypeScript compile → dist/
  
  # Stage 3: minimal runtime (no TypeScript, no devDeps, no source)
  FROM node:18-alpine AS runtime
  RUN addgroup -S app && adduser -S app -G app
  WORKDIR /app
  COPY --from=deps /app/node_modules ./node_modules     ← prod deps only
  COPY --from=builder /app/dist ./dist                  ← compiled JS only
  COPY package.json ./
  USER app
  CMD ["node", "dist/server.js"]
  
  Final image: ~120MB (vs 1.2GB)
  Contents: Node runtime + prod node_modules + compiled JS
  Security: no TypeScript, no jest, no eslint, no source code in production

LANGUAGE-SPECIFIC PATTERNS:

  GO (smallest possible image: scratch):
  FROM golang:1.21-alpine AS builder
  WORKDIR /build
  COPY go.mod go.sum ./
  RUN go mod download              ← download dependencies
  COPY . .
  RUN CGO_ENABLED=0 GOOS=linux go build -o app .  ← static binary (no libc needed)
  
  FROM scratch AS runtime          ← empty image (0 bytes base)
  COPY --from=builder /build/app /app
  EXPOSE 8080
  ENTRYPOINT ["/app"]
  
  Final image: ~5MB (static binary only)
  
  JAVA (Spring Boot):
  FROM eclipse-temurin:17-jdk-alpine AS builder
  WORKDIR /build
  COPY mvnw pom.xml ./
  COPY .mvn/ .mvn/
  RUN ./mvnw dependency:go-offline -B
  COPY src/ src/
  RUN ./mvnw package -DskipTests -B
  
  # Use JLink to create minimal JRE (only needed modules):
  RUN jlink --add-modules $(jdeps --ignore-missing-deps -q \
        --recursive --multi-release 17 \
        --print-module-deps /build/target/app.jar) \
      --no-header-files --no-man-pages \
      --compress=2 --output /jre
  
  FROM debian:11-slim AS runtime
  COPY --from=builder /jre /jre
  COPY --from=builder /build/target/app.jar /app.jar
  ENV JAVA_HOME=/jre
  ENTRYPOINT ["/jre/bin/java", "-jar", "/app.jar"]
  # Final: ~120MB vs ~350MB (JDK) vs ~180MB (JRE)
  
  PYTHON:
  FROM python:3.11-slim AS builder
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --user --no-cache-dir -r requirements.txt  ← to ~/.local/
  
  FROM python:3.11-slim AS runtime
  WORKDIR /app
  COPY --from=builder /root/.local /root/.local  ← copy installed packages
  COPY src/ ./
  ENV PATH=/root/.local/bin:$PATH
  CMD ["python", "main.py"]

PARTIAL BUILDS (target a specific stage):

  # Build and test in CI without creating final image:
  docker build --target builder -t myapp-builder:latest .
  docker run myapp-builder:latest npm test  ← run tests in builder stage
  
  # If tests pass, build the final image:
  docker build --target runtime -t myapp:latest .
  
  # Parallel stage builds (BuildKit automatically parallelizes independent stages)

COPY --from external registry:

  # Copy files from a completely different image (not a stage):
  FROM ubuntu:22.04
  COPY --from=nginx:1.24 /usr/share/nginx/html /www
  # → copies nginx's static files into your image
  # Useful for: copying config templates, binaries, static assets
```

---

### ❓ Why Does This Exist (Why Before What)

The build environment and runtime environment have fundamentally different requirements. Build environments need: compilers, SDKs (hundreds of MB), test frameworks, linters, security scanners, source code. Runtime environments need: the compiled output, production dependencies, nothing else. Multi-stage builds enforce this separation structurally in a single Dockerfile. The alternative (two Dockerfiles + orchestration script) was error-prone and duplicated: developers could forget to rebuild the small image after changing the build, or accidentally use an outdated artifact.

---

### 🧠 Mental Model / Analogy

> **Multi-stage builds are like a factory assembly line with a showroom**: the factory (builder stage) has heavy machinery, raw materials, workers, and waste bins. The showroom (runtime stage) has only the finished product. You don't ship the factory to the customer — you ship the finished product. The factory exists only to produce the product. Multi-stage builds let you describe the factory AND the showroom in the same blueprint (Dockerfile) and automatically ship only the showroom.

---

### ⚙️ How It Works (Mechanism)

```
BuildKit execution:

  1. Parse Dockerfile → dependency graph of stages
  2. Analyze which stages are needed for the target (default: last stage)
  3. Parallel: build independent stages simultaneously
     (deps stage + builder stage can start together if independent)
  4. COPY --from: resolve output of named stage at that point
  5. Final stage: include ONLY these layers in the output image
  6. Intermediate stages: used for COPY --from, then DISCARDED

docker build --target builder ← stops at the named stage (for debugging/testing)
```

---

### 🔄 How It Connects (Mini-Map)

```
Need separate build and runtime environments in one Dockerfile
        │
        ▼
Multi-Stage Build ◄── (you are here)
(multiple FROM; COPY --from; discard build stages)
        │
        ├── Dockerfile: multi-stage builds are a Dockerfile feature
        ├── Docker Layer: only final stage's layers in the output image
        ├── Docker Build Context: context available to all stages
        └── Container Registry: final (small) image stored and distributed
```

---

### 💻 Code Example

```dockerfile
# Python FastAPI with multi-stage build

# Stage 1: install dependencies (cached separately)
FROM python:3.11-slim AS python-deps
WORKDIR /app

# Install build dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime (minimal, no build tools)
FROM python:3.11-slim AS runtime

# Runtime system deps only (libpq, no build-essential, no gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from deps stage
COPY --from=python-deps /install /usr/local

# Non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app
COPY --chown=appuser:appgroup app/ ./

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Each stage starts fresh (no layer cache from previous stages) | Each stage independently caches its layers based on its `FROM` image + instructions. The `python:3.11-slim` base layer in the runtime stage is cached and reused across builds. Cache works per-stage. |
| COPY --from copies the entire stage's filesystem | `COPY --from=builder /app/dist ./dist` copies only the specified path (`/app/dist`). You must explicitly specify what to copy — there's no automatic "copy everything from stage." |
| Multi-stage builds slow down the build | BuildKit builds independent stages in parallel. Stages that don't depend on each other run simultaneously. Multi-stage can actually be faster than single-stage by parallelizing dependency installation and compilation. |

---

### 🔥 Pitfalls in Production

```
PITFALL: forgetting to COPY runtime dependencies (only copying binary)

  FROM golang:1.21 AS builder
  RUN go build -o app .
  
  FROM scratch
  COPY --from=builder /build/app /app
  ENTRYPOINT ["/app"]
  
  # If app uses dynamic linking (e.g., uses CGO or net package without DNS override):
  # → /app fails: "no such file or directory" (missing libc, libpthread, etc.)
  
  # FIX 1: static build (CGO disabled)
  RUN CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o app .
  
  # FIX 2: use distroless/static (includes glibc for dynamic binaries)
  FROM gcr.io/distroless/static-debian11
  COPY --from=builder /build/app /app
  
  # FIX 3: alpine (has musl libc, small but has a libc)
  FROM alpine:3.18
  COPY --from=builder /build/app /app

PITFALL: not testing in the builder stage before building final image

  # ❌ Tests never run; broken code deployed
  FROM builder AS test
  RUN npm test     ← add this stage
  
  FROM runtime
  # ...
  
  # CI: run tests explicitly before final build:
  docker build --target test -t myapp-test .   ← fails if tests fail
  docker build --target runtime -t myapp:$VERSION .  ← only runs after test passes
```

---

### 🔗 Related Keywords

- `Dockerfile` — multi-stage builds are a Dockerfile feature
- `Docker Layer` — only final stage's layers appear in the output image
- `Docker Build Context` — shared across all stages
- `Docker Image` — the output of multi-stage build is one image (last stage)
- `Container Registry` — where the small final image is stored

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN:                                                 │
│   FROM large-builder AS builder  ← compile; test        │
│   RUN build && run_tests                                 │
│                                                          │
│   FROM minimal-runtime AS final  ← only runtime needs   │
│   COPY --from=builder /artifacts /app                   │
│   USER nonroot                                           │
│   CMD [...]                                              │
├──────────────────────────────────────────────────────────┤
│ SIZES:                                                   │
│   Go: scratch → ~5MB final image                        │
│   Node: node:alpine → ~120MB final image                │
│   Java: JRE + fat JAR → ~180MB final image              │
│ BuildKit: parallel stage builds; --target for testing   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Distroless images (Google) contain only the application runtime — no shell, no package manager, no OS utilities. A distroless Java image is ideal for production security. But when your production pod crashes and you need to debug: no `kubectl exec -it pod bash` because there's no bash. How do you debug a running distroless container? What Kubernetes features (`kubectl debug`, ephemeral containers) solve this problem, and how do they work?

**Q2.** Multi-stage builds are designed for building one artifact. But in a microservices monorepo, you have 20 services. Building each independently with its own Dockerfile doesn't share dependency installation across services that use the same packages. How would you design a multi-stage build strategy for a monorepo to maximize: (a) layer caching (shared base layers), (b) build parallelism (BuildKit), and (c) minimal final images per service? Consider Docker Buildx bake files as part of your answer.
