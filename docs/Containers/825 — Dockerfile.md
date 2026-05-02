---
layout: default
title: "Dockerfile"
parent: "Containers"
nav_order: 825
permalink: /containers/dockerfile/
number: "0825"
category: Containers
difficulty: ★☆☆
depends_on: Docker, Docker Image, Docker Layer, Container
used_by: Docker Build Context, Multi-Stage Build, Docker BuildKit, Container Security
related: Docker Layer, Multi-Stage Build, Docker Build Context, Docker BuildKit, Container Security
tags:
  - containers
  - docker
  - devops
  - foundational
  - bestpractice
---

# 825 — Dockerfile

⚡ TL;DR — A Dockerfile is the recipe that defines how a Docker image is built — listing the base image, copying files, running commands, and setting the entrypoint.

| #825 | Category: Containers | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Docker, Docker Image, Docker Layer, Container | |
| **Used by:** | Docker Build Context, Multi-Stage Build, Docker BuildKit, Container Security | |
| **Related:** | Docker Layer, Multi-Stage Build, Docker Build Context, Docker BuildKit, Container Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Dockerfiles, distributing a configured application environment meant writing bash scripts, Ansible playbooks, or detailed PDF instructions for setting up a server. Every team member had a different result — different OS versions, different library installations, different config values. "Infrastructure as code" tools (Chef, Puppet) existed but required system administration expertise and complex setup. None of them produced a portable, immutable artifact.

**THE BREAKING POINT:**
Reproducible build environments needed a standardised, simple, declarative format — short enough to understand in minutes, powerful enough to build any application image, and parseable by automated tools.

**THE INVENTION MOMENT:**
This is exactly why the Dockerfile was created — a declarative text file where each line is an instruction that builds up an image layer by layer, readable by humans and executed by Docker's build engine.

---

### 📘 Textbook Definition

A **Dockerfile** is a plain text file containing an ordered sequence of instructions that Docker's build engine (BuildKit) executes to create a Docker image. Each instruction performs a specific operation: specifying a base image (`FROM`), running commands (`RUN`), copying files (`COPY`), setting environment variables (`ENV`), exposing ports (`EXPOSE`), defining the startup command (`CMD` / `ENTRYPOINT`). Instructions that modify the filesystem create immutable layers in the resulting image. A Dockerfile is the source of truth for an image's contents — version-controlled, reviewable, and reproducible.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Dockerfile is a short text file — typically 10–20 lines — that tells Docker exactly how to build your application's container image.

**One analogy:**
> A Dockerfile is like a recipe card for a specific dish. "Start with a chicken breast (FROM). Marinate with spices (RUN). Place in a pan (COPY). Cook at 180°C for 25 minutes (RUN). Serve hot (ENTRYPOINT)." Anyone who follows the recipe gets the same dish. The recipe is the source of truth — share the card, not the finished meal. The Dockerfile is the recipe card for a container image.

**One insight:**
The order of instructions is a performance decision, not just a logical one. Because each instruction creates a layer and a changed layer invalidates all subsequent layers' caches, **slow operations (dependency installation) must come before fast operations (copying application code)** — so a code change doesn't force a full re-install of dependencies.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every Dockerfile must start with a `FROM` instruction — specifying the base image.
2. Instructions are executed in order; each creates a new layer (if filesystem-modifying).
3. The last `CMD` or `ENTRYPOINT` defines what runs when the container starts.

**DERIVED DESIGN:**

Key Dockerfile instructions and their purpose:

| Instruction | Creates Layer | Purpose |
|---|---|---|
| `FROM image:tag` | No | Set base image |
| `RUN command` | Yes | Execute command during build |
| `COPY src dest` | Yes | Copy files from build context |
| `ADD src dest` | Yes | Copy files (+ URL support + tar extraction) |
| `ENV KEY=value` | No | Set environment variable |
| `WORKDIR /path` | No | Set working directory |
| `EXPOSE port` | No | Document exposed port (informational) |
| `USER username` | No | Set the user to run as |
| `CMD ["exec", "arg"]` | No | Default command (overridable at `docker run`) |
| `ENTRYPOINT ["exec"]` | No | Fixed command (CMD becomes its args) |
| `ARG NAME=default` | No | Build-time variable |
| `LABEL key=value` | No | Image metadata |

**CMD vs ENTRYPOINT:**
- `CMD` alone: default command, overridable with `docker run image OTHER_CMD`
- `ENTRYPOINT` alone: fixed binary, `docker run` args become its arguments
- Both together: ENTRYPOINT is the fixed binary; CMD provides default arguments

**THE TRADE-OFFS:**
**Gain:** Human-readable, version-controllable image specification; reproducible builds; declarative format.
**Cost:** Requires understanding layer ordering for performance; easy to accidentally include secrets; verbose for complex multi-stage builds.

---

### 🧪 Thought Experiment

**SETUP:**
A Dockerfile for a Node.js app. Developer A puts `COPY . .` first. Developer B puts `COPY package.json .` first, then `RUN npm install`, then `COPY . .`.

**WHAT HAPPENS WITH DEVELOPER A's ORDER:**
- Day 1 (cold build): 4 minutes (npm install from scratch)
- Day 2 (fixed a typo in app.js): `COPY . .` layer changed → all subsequent layers rebuilt → `RUN npm install` re-runs → 4 minutes again
- Day 30: still 4 minutes on every code change

**WHAT HAPPENS WITH DEVELOPER B's ORDER:**
- Day 1 (cold build): 4 minutes (npm install from scratch)
- Day 2 (fixed a typo in app.js): `COPY package.json .` → CACHE HIT; `RUN npm install` → CACHE HIT; `COPY . .` changed → rebuild. 15 seconds.
- Day 30: virtually always 15 seconds (unless package.json changes)

**THE INSIGHT:**
Same application, same Dockerfile instructions, different order. Developer B's team ships 16× faster for every code-only change. Over a year with 50 engineers and daily builds, this is thousands of hours of CI time and developer waiting saved.

---

### 🧠 Mental Model / Analogy

> A Dockerfile is like theatre stage setup instructions. "Act 1 setup: place the chairs (base image). Act 2: hang the backdrop (install OS deps). Act 3: place props (install app deps). Act 4: bring out the actors (copy app code). Curtain call: start the show (CMD/ENTRYPOINT)." Each act must come in order — you can't place actor props before the stage is set. Directors can swap out just the actor props (app code) without resetting the whole stage, as long as the earlier acts haven't changed.

**Mapping:**
- "Stage setup acts" → Dockerfile instructions (each creates a layer)
- "Same stage layout every show" → reproducible image builds
- "Only replacing props between shows" → layer cache reuse when only code changes
- "Curtain call / start the show" → CMD/ENTRYPOINT (what runs when container starts)

**Where this analogy breaks down:** A theatre set can be partially reset between acts; Docker layers are strictly one-directional — you cannot go back and modify a previous layer without rebuilding from that point.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Dockerfile is a simple text file with instructions for building a container image. It says: "Start with this Linux base, install these programs, copy these files, and when the container starts, run this command." Anyone with Docker can follow the file to create the exact same container.

**Level 2 — How to use it (junior developer):**
Create a file literally named `Dockerfile` (no extension). Write instructions: `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`. Build with `docker build -t imagename:tag .` — the `.` means use the current directory as the build context. Use `.dockerignore` to exclude files from the build context (like `node_modules/` or `.git/`). Test the image locally. Once the image builds correctly, that same Dockerfile will produce the same image in CI.

**Level 3 — How it works (mid-level engineer):**
When `docker build` runs: BuildKit parses the Dockerfile into a dependency graph (not just top-to-bottom). For parallel execution, independent stages can build simultaneously. For each instruction, BuildKit computes a cache key from `(parent_layer_hash, instruction, build_args)`. It checks the build cache (local or remote registry cache). On cache miss, it executes the instruction, captures the OverlayFS upper-layer diff, compresses it, hashes it, and stores it. The final image manifest lists all layer hashes in order plus the config JSON.

**Level 4 — Why it was designed this way (senior/staff):**
The Dockerfile's design was intentionally simple to lower the barrier to adoption. The `FROM/RUN/COPY/CMD` model maps directly to how system administrators thought about server setup: start from a known base, install dependencies, copy files, start the app. The tradeoffs of this simplicity: no native loop/conditional logic in Dockerfile (workaround: `ARG` + shell `if`); no native secret handling in early versions (workaround: BuildKit `--secret`); no native parameterisation (workaround: `ARG`). Multi-stage builds (v17.05) addressed the build-vs-runtime dependency problem. BuildKit completely rewrote the execution engine to enable parallel stage execution, remote caching, and secret mounts. Alternative: Buildpacks (Cloud Native Buildpacks) remove the Dockerfile entirely — build tooling auto-detects language and produces an OCI image; useful when developers don't want to write or maintain Dockerfiles.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  DOCKERFILE BUILD PROCESS                                │
│                                                          │
│  Dockerfile          BuildKit execution:                 │
│  FROM node:20-alpine → Pull base image if not local     │
│        ↓              → Layer 0: node:20-alpine base    │
│  WORKDIR /app         → Sets working dir metadata only  │
│        ↓              → No new layer                    │
│  COPY package.json .  → Copy file from build context    │
│        ↓              → Layer 1: /app/package.json added│
│  RUN npm ci           → Execute command in container    │
│        ↓              → Layer 2: /app/node_modules added│
│  COPY . .             → Copy all source from context    │
│        ↓              → Layer 3: /app/*.js added        │
│  EXPOSE 3000          → Metadata only, no layer         │
│  USER node            → Metadata only, no layer         │
│  CMD ["node","app.js"]→ Metadata only, no layer         │
│                                                          │
│  Final image: base + 3 layers + config JSON            │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes Dockerfile → git commit → CI triggered
→ docker build . → [DOCKERFILE EXECUTED ← YOU ARE HERE]
→ layers created + cached → image tagged → pushed to registry
→ deployed to production environment
```

**FAILURE PATH:**
```
docker build fails with "RUN npm ci" error
→ check: is package.json correct? is registry accessible?
→ fix Dockerfile or dependency → re-run build
→ observable: build log shows exact failing instruction
```

**WHAT CHANGES AT SCALE:**
In large organisations (100+ services), Dockerfile sprawl means each team has their own base image choices and layer patterns. Centralised base images (`company/node-base:20-alpine-hardened`) enforce security standards while letting teams build on top. A vulnerability in the company base triggers a rebuild of all downstream images — automated by a CI pipeline that monitors base image updates and triggers dependant builds.

---

### 💻 Code Example

Example 1 — Well-structured Node.js Dockerfile:
```dockerfile
# Stage: runtime only (no build tools in final image)
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (changes less often)
COPY package.json package-lock.json ./
RUN npm ci --only=production \
    && npm cache clean --force

# Copy application source (changes most often)
COPY src/ ./src/

# Document the port
EXPOSE 3000

# Run as non-root for security
USER node

# Exec form: signals go directly to node process
ENTRYPOINT ["node", "src/server.js"]
```

Example 2 — Python application Dockerfile:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*  # Cleanup in same RUN!

# Install Python dependencies before copying source
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source last
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

USER nobody
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Example 3 — .dockerignore (always include):
```
# .dockerignore — prevent these from entering the build context
node_modules/
.git/
.gitignore
*.md
README.md
.env
.env.*
tests/
__tests__/
coverage/
.nyc_output/
dist/
build/
# ^ Excluding node_modules prevents 200MB from being sent
#   to the Docker daemon on every build
```

---

### ⚖️ Comparison Table

| Instruction | Creates Layer | Overridable at Run | Common Use |
|---|---|---|---|
| `RUN` | Yes | No | Install dependencies, build steps |
| `COPY` | Yes | No | Copy application files |
| `ADD` | Yes | No | URL fetch or tar extraction (prefer COPY) |
| `ENV` | No | Yes (`-e`) | Configure application |
| `ARG` | No | Yes (`--build-arg`) | Build-time parameters |
| `CMD` | No | Yes (positional args) | Default entrypoint args |
| `ENTRYPOINT` | No | Yes (`--entrypoint`) | Fixed executable |

**How to choose between CMD and ENTRYPOINT:** Use `ENTRYPOINT` for the main application binary (makes the container behave like an executable). Use `CMD` for default arguments that users might override. Use `CMD` alone for maximum flexibility. The combination `ENTRYPOINT ["node"] CMD ["server.js"]` lets users run `docker run myimage other_file.js` to override just the file.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| EXPOSE actually opens network ports | EXPOSE is documentation only — it does not open any ports. Port binding requires the `-p` flag in `docker run`. |
| ENV variables set in Dockerfile are secret | ENV variables are visible in the image config via `docker inspect`. Never use ENV for secrets. |
| WORKDIR creates the directory | Yes, WORKDIR creates the directory if it doesn't exist AND sets the working directory for subsequent instructions. |
| COPY and ADD are interchangeable | Prefer COPY for files from the build context. ADD has extra behaviour (URL fetching, tar auto-extraction) that can be surprising. Use ADD only when those features are needed. |
| The last RUN determines the user | The USER instruction sets the user for subsequent RUN, COPY, and ENTRYPOINT. It must be set BEFORE the CMD/ENTRYPOINT to take effect at runtime. |

---

### 🚨 Failure Modes & Diagnosis

**Secret in ENV Instruction**

**Symptom:** Security scan flags that API key is visible in image config.

**Root Cause:** Developer wrote `ENV API_KEY=abc123` in Dockerfile. ENV values are stored in image config JSON, visible to anyone who can pull the image.

**Diagnostic Command / Tool:**
```bash
docker inspect myapp:1.0 | jq '.[0].Config.Env'
# Will show: ["API_KEY=abc123", ...]
```

**Fix:** Remove secret from ENV. Pass at runtime: `docker run -e API_KEY=abc123 myapp:1.0`. Or use BuildKit secrets for build-time secrets.

**Prevention:** Code review all Dockerfiles. Add CI check: `grep -n "ENV.*KEY\|ENV.*SECRET\|ENV.*PASSWORD" Dockerfile` → fail build if found.

---

**Container Exits Immediately**

**Symptom:** `docker run myapp` starts and immediately exits with code 0 or non-zero.

**Root Cause 1 (shell form CMD in background):** `CMD service myapp start` starts the service and exits — the shell exits when the background process starts. Docker container exits when PID 1 exits.

**Diagnostic Command / Tool:**
```bash
docker run myapp         # exits immediately
docker logs myapp        # check for error messages
docker run -it myapp sh  # interactive shell to debug
```

**Fix:** Ensure the container's PID 1 is a foreground process:
```dockerfile
# BAD: runs in background, container exits
CMD service myapp start

# GOOD: runs in foreground, container stays alive
CMD ["myapp", "--foreground"]
# Or for daemons:
CMD ["nginx", "-g", "daemon off;"]
```

**Prevention:** Always test that `docker run -d myapp` shows status "Up" after 10 seconds. A container that exits immediately is always a PID 1 / daemon mode misconfiguration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker` — the tool that reads and executes Dockerfiles
- `Docker Layer` — each Dockerfile instruction creates one layer

**Builds On This (learn these next):**
- `Multi-Stage Build` — advanced Dockerfile pattern for minimal production images
- `Docker Build Context` — what files are available during the build
- `Docker BuildKit` — modern build engine with additional Dockerfile features

**Alternatives / Comparisons:**
- `Cloud Native Buildpacks` — auto-detect language and build without writing a Dockerfile
- `Kaniko` — Dockerfile-based builder that runs without Docker daemon (for Kubernetes CI)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Declarative text recipe for building     │
│              │ a Docker image — FROM to ENTRYPOINT      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Reproducible environments needed a       │
│ SOLVES       │ versionable, human-readable build spec   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Instruction ORDER is a cache performance │
│              │ decision — slow ops first, fast ops last │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — Dockerfile is the standard way  │
│              │ to define container images               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never put secrets in ENV or RUN;         │
│              │ never COPY everything before npm install │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple, readable spec vs requires        │
│              │ understanding layer caching for perf     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The recipe card for a container image — │
│              │  version-controlled, reproducible, exact"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Multi-Stage Build → Docker Build Context │
│              │ → Docker BuildKit                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer writes `RUN curl -o app.jar https://internal.repo/myapp-1.0.jar` in a Dockerfile. The URL is fetched at build time and the JAR is embedded in the image. Three months later, someone rebuilds the image with the same `1.0` tag on the URL but the JAR has been silently replaced at the server with a newer version. The image `tag` still says `1.0`. Describe the reproducibility failure this creates, why content-addressed layer caching doesn't protect you from this, and what Dockerfile instruction or build technique would make this build truly reproducible.

**Q2.** Your organisation has 300 microservices each with their own Dockerfile. A new security policy requires that all containers must run as a non-root user (UID > 0). How do you enforce this policy across all 300 Dockerfiles — both for new services going forward and for existing services — without manually reviewing each one? What automated tooling would you use, at what point in the CI/CD pipeline, and how do you handle the edge case where a service genuinely needs root for one specific operation?

