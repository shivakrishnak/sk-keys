---
layout: default
title: "Multi-Stage Build"
parent: "Containers"
nav_order: 827
permalink: /containers/multi-stage-build/
number: "0827"
category: Containers
difficulty: ★★☆
depends_on: Dockerfile, Docker Layer, Docker Image, Docker Build Context
used_by: Distroless Images, Container Security, Image Tag Strategy, Docker BuildKit
related: Dockerfile, Docker Layer, Distroless Images, Docker BuildKit, Slim / Minimal Images
tags:
  - containers
  - docker
  - intermediate
  - bestpractice
  - security
---

# 827 — Multi-Stage Build

⚡ TL;DR — Multi-stage builds let you use one Dockerfile stage for building (with compilers, test tools) and a separate minimal stage for the runtime image — keeping production images small and secure.

| #827 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Dockerfile, Docker Layer, Docker Image, Docker Build Context | |
| **Used by:** | Distroless Images, Container Security, Image Tag Strategy, Docker BuildKit | |
| **Related:** | Dockerfile, Docker Layer, Distroless Images, Docker BuildKit, Slim / Minimal Images | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java application needs: JDK (350 MB) to compile, Maven (100 MB) to resolve dependencies, and test tools to run tests. All of this is only needed at build time — the final JAR just needs a JRE (120 MB) to run. Without multi-stage builds, every production image contains the full JDK + Maven + test tooling, despite those components having zero role at runtime. The production image is 600 MB when it needs to be 130 MB. Worse: the JDK, Maven, and compiler tools are attack surface in production. A vulnerability in Maven or a compiler tool now exists in your production container — code that runs during builds should never exist in a running service.

**THE BREAKING POINT:**
Build-time dependencies and runtime dependencies are fundamentally different concerns. Before multi-stage builds, the only solutions were: maintain two separate Dockerfiles (error-prone, drift-prone) or build outside Docker and copy the artifact in (breaks reproducibility).

**THE INVENTION MOMENT:**
This is exactly why multi-stage builds were added to Docker 17.05 — a single Dockerfile can now define multiple `FROM` stages, where the final stage copies only the built artifacts from earlier stages, discarding all build-time cruft.

---

### 📘 Textbook Definition

**Multi-stage build** is a Dockerfile feature (introduced in Docker 17.05) that allows a single `Dockerfile` to define multiple build stages, each with its own `FROM` base image. Intermediate stages can install build tools, compile code, and run tests without those tools appearing in the final image. The final stage selects only the built artifacts needed at runtime using `COPY --from=<stage_name>`. All intermediate stage layers, build tools, and intermediate files are excluded from the final image. The resulting image contains only what the production or runtime environment requires.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Multi-stage builds split Dockerfiles into a build stage (messy, with all tools) and a runtime stage (clean, minimal) — only the final binary crosses the finish line.

**One analogy:**
> Multi-stage builds are like manufacturing: a factory has a production floor with heavy machinery, raw materials, and workers (build stage). The finished product is boxed and shipped to stores (runtime stage). Customers never get the factory floor shipped to their home — they get the box. Before multi-stage builds, shipping "the factory" to customers was unavoidable. Now, you compile in the factory and ship only the product.

**One insight:**
Any file that "exists only in an intermediate build stage" is never part of the final image, no matter how it was created — including compiled binaries, downloaded Maven dependencies, npm cache, and temporary build artefacts. The `COPY --from=builder` instruction is the surgical incision that extracts only what is needed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Build-time tools (compilers, test runners, package managers) are not needed at runtime.
2. Any file present in the final image's layers is part of the attack surface — unnecessary files increase security risk.
3. A smaller final image pulls faster, starts faster, and costs less to store and transmit.

**DERIVED DESIGN:**

A multi-stage Dockerfile looks like multiple concatenated Dockerfiles, each starting with `FROM`:

```dockerfile
# Stage 1: build (heavy, disposable)
FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:resolve -q  # pre-cache deps
COPY src/ ./src/
RUN mvn package -DskipTests

# Stage 2: runtime (minimal, production)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /build/target/app.jar ./app.jar
USER nobody
ENTRYPOINT ["java", "-jar", "app.jar"]
```

The `builder` stage image (300 MB bigger) is discarded. The final image contains only the JRE base + `app.jar`.

**Stage naming and selective copy:**
- `AS builder` names the stage (optional but required for COPY --from)
- `COPY --from=builder /build/target/app.jar ./app.jar` copies one file from the builder stage
- Stages can be used as bases: `FROM builder AS test` inherits from builder to run tests in the same environment

**BuildKit parallel execution:**
With BuildKit, stages that do not depend on each other can be built in parallel. A `test` stage and a `runtime` stage can build simultaneously if neither depends on the other.

**THE TRADE-OFFS:**
**Gain:** Dramatically smaller runtime images; no build-time tools in production; single reproducible Dockerfile for entire pipeline; build tools cannot be exploited in production.
**Cost:** Slightly more complex Dockerfile; build cache is now spread across stages; errors in one stage are isolated, which can make debugging less obvious.

---

### 🧪 Thought Experiment

**SETUP:**
A Go microservice. The Go compiler is only needed to turn `main.go` into a compiled binary. The compiled binary is statically linked — it needs nothing from the OS at runtime.

**WITHOUT MULTI-STAGE BUILD:**
```dockerfile
FROM golang:1.22
COPY . .
RUN go build -o /app .
# Final image contains: Go compiler (700 MB) + Go libraries + source code + binary
# Total: ~900 MB
```
Container image: 900 MB. The Go compiler is exposed in production. Source code is in the image. A compromised container gives an attacker a full Go compiler and your source.

**WITH MULTI-STAGE BUILD:**
```dockerfile
FROM golang:1.22 AS builder
COPY . .
RUN CGO_ENABLED=0 go build -o /app .

FROM scratch          # EMPTY image - nothing at all
COPY --from=builder /app /app
ENTRYPOINT ["/app"]
# Final image: just the compiled binary
# Total: ~8 MB (binary only)
```
Container image: 8 MB. No compiler. No source. No OS. No shell. Attack surface: near zero.

**THE INSIGHT:**
For statically compiled languages (Go, Rust), multi-stage builds can produce `FROM scratch` images with ZERO base OS. For interpreted languages (Python, Node.js), the improvement is reducing from "runtime + all build tools" to "runtime only." The principle applies universally.

---

### 🧠 Mental Model / Analogy

> Multi-stage builds are like hiring a specialist translator. You hire a translator (build stage) — they read the original document (source code), translate it into English (compile), and hand you the English version. The translator does not move into your house. You have the translated document (binary/artifact). The skills, dictionaries, and reference books the translator used (compiler, build tools) stay with them, not in your home (production image).

**Mapping:**
- "Translator" → build stage (temporary — used for compilation, then discarded)
- "Original document + reference books" → source code + compilers + build tools in build stage
- "Translated English document" → compiled binary / JAR / bundled assets
- "Translator does not move into your house" → build stage layers are NOT in the final image
- "Your home" → production container image (final FROM stage)

**Where this analogy breaks down:** You always have the original document (source code in version control), but the translator is re-hired for every build — this is intentional for reproducibility. Unlike hiring a person, each build stage is disposable and deterministic.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Multi-stage builds let you use a powerful setup to build your software, then put only the finished product into the final container — not all the tools used to build it. It is like baking a cake in a full bakery kitchen but delivering only the cake, not the kitchen.

**Level 2 — How to use it (junior developer):**
Write multiple `FROM` sections in one Dockerfile. Name them with `AS build_stage_name`. In the final `FROM` section, use `COPY --from=build_stage_name /source/path /dest/path` to pull only the files you need. When you run `docker build`, only the final stage becomes the image. Test it: `docker build --target=builder .` to build only through the builder stage (useful for debugging).

**Level 3 — How it works (mid-level engineer):**
BuildKit analyses the Dockerfile DAG. Stages that are not referenced by the final stage (or specified `--target`) are pruned — not built at all. This means adding a test stage (`FROM builder AS test; RUN ./gradlew test`) that is not referenced from the final stage requires explicit `--target=test` to run it; without it, the test stage is skipped in a production build. Use `docker build --target=test .` to explicitly trigger tests as a separate build step in CI.

**Level 4 — Why it was designed this way (senior/staff):**
Before multi-stage builds, the workaround was shell scripts that: built code outside Docker, then `COPY` the artifact in. This broke the "Dockerfile is the complete reproducible specification" guarantee and required the host to have build tools installed. The multi-stage approach keeps everything inside Docker — reproducible on any host with Docker, no host-installed build tools required. The trade-off BuildKit made in the parallel execution design: independent stages build in parallel by default, but accessing a stage's file in another stage (`COPY --from`) creates a dependency edge that forces sequential execution at that point. Most multi-stage Dockerfiles benefit from parallel stage builds — e.g., frontend and backend built simultaneously, then both artifacts are copied into a final stage.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  MULTI-STAGE BUILD EXECUTION (BuildKit)                 │
│                                                          │
│  Dockerfile:                                            │
│  ─────────────────────────────                         │
│  FROM maven:3.9 AS builder              (Stage 1)       │
│  COPY pom.xml .                                         │
│  RUN mvn package                                        │
│                                                          │
│  FROM eclipse-temurin:21-jre AS runtime (Stage 2)       │
│  COPY --from=builder target/app.jar .                   │
│  CMD ["java","-jar","app.jar"]                         │
│  ─────────────────────────────                         │
│                                                          │
│  BuildKit DAG:                                          │
│  [builder stage] → produces layers (300 MB + app.jar)  │
│       ↓ COPY --from=builder                            │
│  [runtime stage] → produces final image (130 MB)       │
│       (builder layers NOT included in final image)      │
│                                                          │
│  Layer store after build:                               │
│  builder_layers: cached (used for next build speedup)  │
│  runtime_layers: used in final image                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
docker build -t myapp:1.0 .
→ BuildKit parses stages
→ Builder stage executes (maven:3.9) → app.jar created
→ [MULTI-STAGE: COPY --from=builder ← YOU ARE HERE]
→ Runtime stage starts (jre-alpine) → app.jar copied in
→ Final image: ~130 MB (JRE + app.jar only)
→ docker push → deploy
```

**FAILURE PATH:**
```
Build fails in builder stage (e.g. test failure)
→ Runtime stage is never built
→ No broken image is produced or pushed
→ observable: docker build exits non-zero
→ debug: docker build --target=builder to inspect builder stage
```

**WHAT CHANGES AT SCALE:**
In CI with many parallel builds, BuildKit's remote cache (`--cache-from=registry`) means the `maven dependency:resolve` layer is shared across all developers — the first build populates the cache, all subsequent builds reuse it. At scale: builder stage cache reuse is often more valuable than runtime stage reuse, since the builder stage is larger and slower.

---

### 💻 Code Example

Example 1 — Go application with scratch final stage:
```dockerfile
# Build stage: full Go toolchain
FROM golang:1.22-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
# CGO_ENABLED=0: statically linked (no runtime deps)
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s" \
    -o /app/server .

# Runtime stage: empty image
FROM scratch
COPY --from=builder /app/server /server
# Copy TLS certificates (needed for HTTPS calls)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt \
                    /etc/ssl/certs/
EXPOSE 8080
ENTRYPOINT ["/server"]
# Final image: ~10 MB vs ~400 MB without multi-stage
```

Example 2 — Node.js with separate build and runtime:
```dockerfile
# Build stage: install all deps (including devDependencies)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci             # includes dev deps
COPY . .
RUN npm run build      # compile TypeScript, bundle, etc.

# Runtime stage: only production deps + compiled output
FROM node:20-alpine AS runtime
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production  # no dev deps
COPY --from=builder /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
# Result: no TypeScript compiler, no test frameworks in production
```

Example 3 — Run tests in CI as a separate stage:
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
RUN pytest tests/ --tb=short

FROM base AS runtime
COPY src/ ./src/
USER nobody
ENTRYPOINT ["python", "src/main.py"]
```
```bash
# CI: run tests (test stage must be explicitly targeted)
docker build --target=test -t myapp:test .

# Production: build final runtime image
docker build -t myapp:prod .
# The test stage is NOT included in the production image
```

---

### ⚖️ Comparison Table

| Approach | Image Size | Build Tools in Prod | Reproducible | Complexity |
|---|---|---|---|---|
| **Multi-Stage Build** | Minimal | No | Yes | Low-Medium |
| Single-Stage (all in one) | Large | Yes | Yes | Low |
| External build + COPY | Depends | No | No (host-dependent) | Medium |
| Two separate Dockerfiles | Minimal | No | Partial (drift risk) | High |

**How to choose:** Multi-stage builds are the universally recommended approach for any compiled or built application. Single-stage is acceptable only for interpreted languages with no build step and no test tools to exclude. Never use "external build + COPY" — it breaks reproducibility and requires build tools on the CI host.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Intermediate stages are still in the final image | Intermediate stage layers are completely absent from the final image. Only items explicitly COPY'd from them exist in the final image. |
| multi-stage builds are only for compiled languages | They benefit interpreted languages too: separate devDependencies from production dependencies node.js, Python test tools from runtime, etc. |
| COPY --from= can only copy from a named stage | COPY --from can also reference an external image: `COPY --from=nginx:1.25 /etc/nginx/ /etc/nginx/` copies files directly from another image |
| All stages are always executed | BuildKit only builds stages needed to produce the target stage. An unreferenced stage is not built unless explicitly targeted with `--target`. |
| Multi-stage builds always slow down the build | BuildKit builds parallel-eligible stages simultaneously — a test stage and a build stage can run in parallel, not sequentially. |

---

### 🚨 Failure Modes & Diagnosis

**Wrong File Path in `COPY --from`**

**Symptom:** `docker build` fails with `COPY failed: file not found in build context or excluded by .dockerignore: stat /build/target/myapp.jar`

**Root Cause:** The builder stage creates the JAR at `/build/target/app.jar` but the COPY instruction uses the wrong path from the wrong stage.

**Diagnostic Command / Tool:**
```bash
# Build only to the builder stage and inspect
docker build --target=builder -t debug-builder .
docker run --rm debug-builder find /build/target -name "*.jar"
# See exact path produced by builder stage
```

**Fix:** Use the exact path shown by `find` in the `COPY --from=builder` instruction.

**Prevention:** During initial Dockerfile development, build `--target=builder` and inspect the result before writing the runtime stage.

---

**Test Stage Silently Skipped**

**Symptom:** Tests pass in `docker build` but a breaking change merged — turns out tests were never actually running.

**Root Cause:** Developer wrote a `test` stage but never referenced it from the runtime stage and never called `--target=test` in CI. BuildKit skipped it entirely.

**Diagnostic Command / Tool:**
```bash
# Verify test stage executes in CI
docker build --target=test -t myapp:test . 2>&1 | tail -5
# Should show pytest/mocha output
```

**Fix:** Add `docker build --target=test .` as an explicit step in the CI pipeline before the production build. Failure of this step must block deployment.

**Prevention:** CI pipeline must explicitly build the test stage. Never assume the test stage runs automatically during a production build.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dockerfile` — multi-stage builds are a Dockerfile feature
- `Docker Layer` — understanding layers explains why intermediate stage layers are discarded

**Builds On This (learn these next):**
- `Distroless Images` — combine with multi-stage builds for near-zero attack surface
- `Docker BuildKit` — parallel stage execution is a BuildKit feature

**Alternatives / Comparisons:**
- `Slim / Minimal Images` — alternative approach to size reduction by choosing smaller base images
- `Cloud Native Buildpacks` — auto-generates optimal multi-stage-equivalent builds without writing a Dockerfile

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single Dockerfile with multiple FROM      │
│              │ stages — build in one, ship from another  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Build tools (JDK, Maven, npm) in prod    │
│ SOLVES       │ images bloat size and expand attack surface│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ COPY --from=stage copies only what you   │
│              │ need; all build stage layers are discarded│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any compiled language; any project with  │
│              │ devDependencies / test tools to exclude  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Pure interpreted scripts with no build   │
│              │ step and no deps to exclude (rare)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Minimal, secure runtime image vs         │
│              │ slightly more complex Dockerfile         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build in the factory, ship only         │
│              │  the finished product"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distroless Images → Docker BuildKit →    │
│              │ Container Security                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Java service uses a multi-stage Dockerfile: Maven builder stage → JRE runtime stage. The builder stage downloads 150 MB of Maven dependencies from Maven Central. In CI, every build re-downloads all dependencies because the CI runner is ephemeral (new runner per build, no layer cache). Propose a caching strategy that allows the `Maven dependency:resolve` layer to be reused across different CI runners and different branches — specifically addressing the BuildKit cache type, storage backend, and the exact `docker build` flags required.

**Q2.** Your Go application's multi-stage build uses `FROM scratch` for the final stage. A penetration test finds that the application has a path traversal vulnerability that allows reading arbitrary files. The tester notes they "cannot escalate because there is no shell, no `cat`, no `curl`, and no writable filesystem." Describe exactly what the `FROM scratch` stage prevents and what it does NOT prevent. If a sophisticated attacker achieves remote code execution in this container, what can they access despite having no shell tools?

