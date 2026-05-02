---
layout: default
title: "Dockerfile"
parent: "Containers"
nav_order: 825
permalink: /containers/dockerfile/
number: "825"
category: Containers
difficulty: ★☆☆
depends_on: "Docker Image, Docker Layer, Docker"
used_by: "Docker Build Context, Multi-Stage Build, Container Registry"
tags: #containers, #docker, #dockerfile, #build, #image
---

# 825 — Dockerfile

`#containers` `#docker` `#dockerfile` `#build` `#image`

⚡ TL;DR — A **Dockerfile** is a text file with instructions that define how to build a Docker image. Each instruction creates a layer. Key instructions: `FROM` (base image), `RUN` (execute commands), `COPY`/`ADD` (copy files), `ENV`, `EXPOSE`, `USER`, `CMD`/`ENTRYPOINT`. Writing an optimized Dockerfile = ordering instructions for cache efficiency + using multi-stage builds for minimal final images.

| #825            | Category: Containers                                        | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Docker Image, Docker Layer, Docker                          |                 |
| **Used by:**    | Docker Build Context, Multi-Stage Build, Container Registry |                 |

---

### 📘 Textbook Definition

**Dockerfile**: a text file containing an ordered set of instructions that Docker reads to automatically build an image. Each instruction corresponds to one image layer (for filesystem-modifying instructions). The Dockerfile DSL defines: the base image (`FROM`), shell commands to run during build (`RUN`), files to copy into the image (`COPY`, `ADD`), environment variables (`ENV`), working directory (`WORKDIR`), exposed network ports (`EXPOSE`), the runtime user (`USER`), metadata labels (`LABEL`), build arguments (`ARG`), the container entry command (`CMD`, `ENTRYPOINT`), health checks (`HEALTHCHECK`), and volume declarations (`VOLUME`). Processed by `docker build` (or BuildKit). Best practices: use official minimal base images, minimize layer count for size-sensitive instructions, order from least to most frequently changed (cache optimization), use `.dockerignore` to exclude unnecessary files from the build context, never bake secrets into layers, run as non-root user.

---

### 🟢 Simple Definition (Easy)

A Dockerfile is a recipe for building a container image. You write instructions line by line: "start from Ubuntu," "install Python," "copy my code," "when the container starts, run this command." Docker reads the recipe and bakes the image. Anyone with the Dockerfile can reproduce the exact same image.

---

### 🔵 Simple Definition (Elaborated)

The Dockerfile is the most important artifact in a container workflow. A good Dockerfile produces:

1. A **small** image (fewer attack surface, faster pull)
2. A **fast** build (layer caching)
3. A **secure** image (non-root user, no secrets)
4. A **reproducible** image (pinned base image, exact dependency versions)

The single most impactful optimization: **multi-stage builds** — use a large builder image (with compilers, test tools), compile/test, then copy only the final artifact into a minimal runtime image. The final image has zero build tools.

---

### 🔩 First Principles Explanation

```
DOCKERFILE INSTRUCTION REFERENCE:

  FROM <image>:<tag>            # Base image; every Dockerfile starts with this
                                # Use: FROM ubuntu:22.04, FROM python:3.11-slim,
                                #      FROM scratch (empty; for fully static binaries)

  RUN <command>                 # Execute shell command; creates new layer
                                # RUN apt-get update && apt-get install -y python3
                                # Chain with && to combine in one layer

  COPY <src> <dest>             # Copy files from build context to image
                                # COPY . /app/
                                # COPY --chown=user:group src/ /app/

  ADD <src> <dest>              # Like COPY but: also extracts .tar.gz; supports URLs
                                # Prefer COPY for predictability; use ADD only for tars

  ENV <key>=<value>             # Set environment variable (available at build + runtime)
                                # ENV NODE_ENV=production PORT=3000

  ARG <name>[=<default>]        # Build-time variable (NOT available at runtime)
                                # ARG BUILD_VERSION=1.0
                                # Override at build: docker build --build-arg BUILD_VERSION=2.0

  WORKDIR <path>                # Set working directory for subsequent instructions
                                # Creates directory if it doesn't exist

  EXPOSE <port>[/tcp|udp]       # Document which port the container listens on
                                # DOCUMENTATION ONLY — does not actually publish the port
                                # Publishing: docker run -p 8080:3000

  USER <user>[:<group>]         # Set user for subsequent instructions + CMD/ENTRYPOINT
                                # USER appuser or USER 1001

  LABEL <key>=<value>           # Metadata (author, version, description)
                                # LABEL maintainer="team@example.com" version="1.2"

  VOLUME ["/data"]              # Declare mount point; creates anonymous volume if not mounted
                                # Useful to document stateful paths

  HEALTHCHECK [options] CMD ... # Container health check
                                # HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
                                #   CMD curl -f http://localhost:3000/health || exit 1

  ENTRYPOINT ["executable"]     # Fixed part of container command; not overridden by docker run args
                                # ENTRYPOINT ["java", "-jar", "app.jar"]

  CMD ["arg1", "arg2"]          # Default arguments to ENTRYPOINT, or default command
                                # CMD ["server.js"]  (with ENTRYPOINT ["node"])
                                # CMD ["node", "server.js"]  (without ENTRYPOINT)
                                # docker run myapp --port=8080 → overrides CMD

ENTRYPOINT vs CMD:

  ENTRYPOINT ["java", "-jar", "app.jar"]  ← always runs
  CMD ["--server.port=8080"]              ← default arg (overridable)

  docker run myapp                     → java -jar app.jar --server.port=8080
  docker run myapp --server.port=9090  → java -jar app.jar --server.port=9090

  docker run --entrypoint="" myapp bash ← override ENTRYPOINT (for debugging)

EXEC vs SHELL FORM:

  SHELL form: RUN apt-get install -y python3
    → /bin/sh -c "apt-get install -y python3"
    → Processes SHELL variable substitution
    → Vulnerable to shell injection (avoid with external input)

  EXEC form: RUN ["apt-get", "install", "-y", "python3"]
    → Executes directly; no shell
    → Required for proper signal handling in CMD/ENTRYPOINT
    → No shell expansion (use ENV for variables)

  ✅ Use EXEC form for CMD and ENTRYPOINT (signal handling)
  ✅ Either form for RUN (shell form is usually more readable)

COMPLETE EXAMPLE — Node.js production Dockerfile:

  # syntax=docker/dockerfile:1
  # ← enables BuildKit features (mount secrets, etc.)

  # Stage 1: install dependencies
  FROM node:18-alpine AS deps
  WORKDIR /app
  COPY package.json package-lock.json ./
  RUN npm ci --only=production

  # Stage 2: build
  FROM node:18-alpine AS builder
  WORKDIR /app
  COPY --from=deps /app/node_modules ./node_modules
  COPY . .
  RUN npm run build && npm run test

  # Stage 3: minimal runtime
  FROM node:18-alpine AS runtime

  # Security: run as non-root
  RUN addgroup -S appgroup && adduser -S appuser -G appgroup

  WORKDIR /app

  # Copy only runtime artifacts
  COPY --from=deps /app/node_modules ./node_modules
  COPY --from=builder /app/dist ./dist
  COPY package.json ./

  # Metadata
  LABEL org.opencontainers.image.title="MyApp"
  LABEL org.opencontainers.image.version="1.0"

  # Document port
  EXPOSE 3000

  # Health check
  HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

  # Non-root user
  USER appuser

  # Exec form for proper signal handling (SIGTERM on docker stop)
  ENTRYPOINT ["node"]
  CMD ["dist/server.js"]
```

---

### ❓ Why Does This Exist (Why Before What)

Without a Dockerfile, building a consistent container image requires manual steps (install packages, copy files, configure runtime) that are hard to reproduce and version-control. The Dockerfile makes the entire image build process declarative, reproducible, and reviewable in version control. It's the single source of truth for "what's in this container image." This enables: automated CI/CD builds, code review of infrastructure changes, security scanning of the build process, and disaster recovery (rebuild from scratch using only the Dockerfile + source code).

---

### 🧠 Mental Model / Analogy

> **A Dockerfile is like a recipe card for a kitchen**. `FROM ubuntu:22.04` is "start with a clean kitchen (base utensils, stove, pantry staples)." Each `RUN` instruction is a cooking step ("chop the vegetables," "boil the pasta"). `COPY` is "bring in your secret ingredient from outside." `CMD` is the plating instructions — "serve the finished dish this way." Anyone with the recipe card can produce the exact same dish in any kitchen. The kitchen itself (the container host) doesn't need any special setup — the recipe is self-contained.

---

### ⚙️ How It Works (Mechanism)

```
docker build -t myapp:1.0 .

1. Docker reads the Dockerfile line by line
2. For each instruction:
   a. Check cache: is this instruction + parent layer hash cached? → reuse
   b. Cache miss: execute instruction in a temporary container
   c. Capture filesystem diff → create new layer (SHA256)
3. After all instructions: assemble image manifest
4. Tag image: myapp:1.0 → points to final manifest

CACHE KEY:
For RUN: hash of (instruction text + parent layer hash)
For COPY: hash of (file content + instruction + parent layer hash)

→ COPY requirements.txt: if file content changes → cache miss for this + all subsequent
→ RUN npm ci: if requirements.txt unchanged → cache hit (same parent hash)
```

---

### 🔄 How It Connects (Mini-Map)

```
Need a reproducible, automated way to build a container image
        │
        ▼
Dockerfile ◄── (you are here)
(FROM, RUN, COPY, ENV, USER, CMD, ENTRYPOINT, HEALTHCHECK)
        │
        ├── Docker Layer: each instruction creates a layer
        ├── Docker Build Context: files available to COPY instructions
        ├── Multi-Stage Build: multiple FROM stages in one Dockerfile
        └── Docker Image: the output of docker build
```

---

### 💻 Code Example

```dockerfile
# Java Spring Boot Dockerfile (production-grade)
# syntax=docker/dockerfile:1

ARG JAVA_VERSION=17
ARG APP_VERSION=1.0.0

# Stage 1: build with Maven
FROM eclipse-temurin:${JAVA_VERSION}-jdk-alpine AS builder

WORKDIR /build

# Cache Maven dependencies separately from source code
COPY pom.xml ./
COPY .mvn/ .mvn/
COPY mvnw ./
RUN ./mvnw dependency:go-offline -B   # download deps; cache this layer

# Copy source and build
COPY src/ src/
RUN ./mvnw package -DskipTests -B     # build JAR; skip tests (run in CI separately)

# Stage 2: minimal JRE runtime (no JDK, no Maven, no source)
FROM eclipse-temurin:${JAVA_VERSION}-jre-alpine AS runtime

# Security: non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy only the fat JAR from builder stage
COPY --from=builder /build/target/*.jar app.jar

# JVM tuning (container-aware)
ENV JAVA_OPTS="-XX:+UseContainerSupport \
               -XX:MaxRAMPercentage=75.0 \
               -XX:+ExitOnOutOfMemoryError"

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1

USER appuser

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                                                                                                                                                                                                                              |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EXPOSE` publishes a port              | `EXPOSE` is documentation only. It tells operators which port the app uses but does NOT publish it. Publishing requires `-p 8080:3000` on `docker run` or `ports:` in Docker Compose.                                                                                                                                                                                |
| `ENV` secrets are safe (not in layers) | `ENV` values are stored in the image config (visible via `docker inspect`). Any `ENV SECRET=value` is readable by anyone with access to the image. For build-time secrets: use `ARG` + `--build-arg` (not stored in final image). For runtime secrets: inject via environment variable at runtime (not in Dockerfile) or use secret management (Vault, K8s Secrets). |
| `CMD` and `ENTRYPOINT` are the same    | `ENTRYPOINT` is the fixed executable; `CMD` is the default arguments. `docker run myapp extra-args` replaces CMD but not ENTRYPOINT. `CMD` alone without `ENTRYPOINT`: the entire command. Use `ENTRYPOINT` for the core binary; `CMD` for configurable defaults.                                                                                                    |

---

### 🔥 Pitfalls in Production

```
PITFALL: improper signal handling (zombie processes, slow shutdown)

  # ❌ Shell form CMD: java wrapped in /bin/sh -c
  CMD "java -jar app.jar"
  # docker stop → sends SIGTERM to /bin/sh → shell doesn't forward to java
  # java keeps running → 10-second timeout → SIGKILL (hard kill)
  # → in-flight requests dropped; connections not closed gracefully

  # ✅ EXEC form CMD: java is PID 1, receives SIGTERM directly
  ENTRYPOINT ["java"]
  CMD ["-jar", "app.jar"]
  # docker stop → SIGTERM → java handles gracefully → clean shutdown

  # For complex init needs (multiple processes), use tini:
  FROM ubuntu:22.04
  RUN apt-get install -y tini
  ENTRYPOINT ["/usr/bin/tini", "--"]
  CMD ["/app/start.sh"]
  # tini properly reaps zombie processes + forwards signals

PITFALL: using ADD for local files (use COPY instead)

  # ❌ ADD has implicit tar extraction + URL download behavior
  ADD myapp.tar.gz /app/     # extracts tar (sometimes intentional)
  ADD https://example.com/file /app/  # downloads from URL (not reproducible!)

  # ✅ Use COPY for predictable, explicit behavior
  COPY myapp.tar.gz /app/
  # If you need tar extraction: COPY then RUN tar -xzf
  # For URL download: use curl/wget in RUN with explicit hash verification
  RUN curl -fsSL https://example.com/file -o /tmp/file && \
      echo "sha256hash /tmp/file" | sha256sum --check
```

---

### 🔗 Related Keywords

- `Docker Layer` — each Dockerfile instruction creates a layer
- `Docker Build Context` — the files available to `COPY` instructions
- `Multi-Stage Build` — multiple `FROM` stages in one Dockerfile for minimal images
- `Docker Image` — the output artifact of `docker build`
- `Docker` — the tool that processes Dockerfiles

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY INSTRUCTIONS:                                        │
│ FROM: base image            RUN: execute command         │
│ COPY: copy files (prefer)   ADD: copy+extract tar       │
│ ENV: runtime env var        ARG: build-time var only     │
│ WORKDIR: set directory      USER: set user (non-root!)   │
│ EXPOSE: document port       HEALTHCHECK: liveness check  │
│ ENTRYPOINT: fixed binary    CMD: default args (exec form)│
├──────────────────────────────────────────────────────────┤
│ ORDERING: COPY deps file → RUN install → COPY source    │
│ SIZE: combine RUN+cleanup or use multi-stage builds     │
│ SECURITY: USER nonroot; no secrets in ENV/RUN           │
│ SIGNAL: EXEC form for CMD/ENTRYPOINT (not shell form)   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Dockerfile's `HEALTHCHECK` instruction defines how Docker checks if a container is healthy. Kubernetes has its own health probes: `livenessProbe`, `readinessProbe`, and `startupProbe`. These serve different purposes. Explain the difference between Docker's `HEALTHCHECK`, Kubernetes `livenessProbe` (restart if unhealthy), and `readinessProbe` (stop sending traffic if not ready). If you have both a Dockerfile HEALTHCHECK and a Kubernetes readinessProbe defined, which one controls Kubernetes traffic routing?

**Q2.** The `ARG` instruction defines build-time variables that are NOT available at runtime and NOT stored in the final image config. However, `ARG` values that are used in `RUN` commands ARE baked into those layers (the command is cached based on the ARG value). Can you recover an `ARG` value from an image if you have access to the image? What is the actual security boundary of `ARG` vs `ENV` for sensitive build-time values like API keys needed only during npm install?
