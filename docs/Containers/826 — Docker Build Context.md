---
layout: default
title: "Docker Build Context"
parent: "Containers"
nav_order: 826
permalink: /containers/docker-build-context/
number: "0826"
category: Containers
difficulty: ★★☆
depends_on: Dockerfile, Docker Image, Docker Layer, Docker
used_by: Multi-Stage Build, Docker BuildKit, Container Security
related: Dockerfile, Docker Layer, Docker BuildKit, Multi-Stage Build, Container Security
tags:
  - containers
  - docker
  - devops
  - intermediate
  - performance
---

# 826 — Docker Build Context

⚡ TL;DR — The Docker build context is the set of files sent to the Docker daemon when you run `docker build` — everything in the specified directory unless excluded by `.dockerignore`.

| #826 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Dockerfile, Docker Image, Docker Layer, Docker | |
| **Used by:** | Multi-Stage Build, Docker BuildKit, Container Security | |
| **Related:** | Dockerfile, Docker Layer, Docker BuildKit, Multi-Stage Build, Container Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `docker build .` in a large monorepo takes 3 minutes before any Dockerfile instruction executes — just to send files to the Docker daemon. The developer wonders why `COPY package.json .` runs fine but the build context upload is painfully slow. Accidentally running `docker build /` (root directory) would attempt to send the entire operating system to the Docker daemon. Without understanding build context, developers inadvertently include `.git/` directories (hundreds of MB), `node_modules/` (hundreds of MB), and test datasets in their images — making them gigantic.

**THE BREAKING POINT:**
The Docker build model separates the daemon (server that builds images) from the client (CLI). The client must send all files that COPY instructions might need to the daemon before the build starts — but by default "all files" means the entire directory tree at `.`, which can be enormous.

**THE INVENTION MOMENT:**
This is exactly why the build context concept and `.dockerignore` exist — so engineers can precisely control which files are sent to the Docker daemon, keeping context small, builds fast, and images lean.

---

### 📘 Textbook Definition

The **Docker build context** is the set of files and directories made available to the Docker build engine during the execution of a `docker build` command. When you run `docker build <PATH>`, all files within `<PATH>` (respecting `.dockerignore` exclusions) are packaged and sent to the Docker daemon (or BuildKit) as a tar archive. Only files present in the build context can be referenced by `COPY` or `ADD` instructions in the Dockerfile. The build context is sent before the first Dockerfile instruction executes — its size directly determines the startup latency of every build.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The build context is the folder Docker zips up and hands to the build engine — `.dockerignore` controls what goes in, keeping it small and secure.

**One analogy:**
> Running `docker build .` is like calling a contractor to renovate your house and first handing them a box of everything they might need. Without constraints, you might hand them every item in your home — furniture, appliances, paperwork, old food — wasting everyone's time. `.dockerignore` is your packing list: "Only give the contractor the blueprints, materials, and tools they actually need." The contractor (build engine) cannot use anything not in the box.

**One insight:**
The build context travels over a network connection (even on the same machine, via Unix socket to the Docker daemon). Large build contexts — especially accidentally including `node_modules/` (200 MB) or `.git/` (1 GB in large repos) — add seconds to minutes of pure upload time before a single layer is built. A proper `.dockerignore` can reduce a 2 GB context to 5 MB.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. `COPY` and `ADD` in a Dockerfile can only access files that were in the build context — files outside it are invisible to the build.
2. The entire context is sent before any Dockerfile instruction executes.
3. BuildKit can lazily fetch specific paths from the context (with `--mount=type=bind` or targeted `COPY`), but the default mode sends all context upfront.

**DERIVED DESIGN:**

When you run `docker build -t myapp:1.0 .`:
1. Docker CLI reads the Dockerfile at `.` (or `--file` path).
2. Docker CLI reads `.dockerignore` in the build context root; builds an exclusion list.
3. Docker CLI tars the entire `.` directory tree (excluding `.dockerignore` matches) into a compressed archive.
4. The tar archive is sent via HTTP/Unix socket to the Docker daemon (or BuildKit).
5. BuildKit unpacks the context into a temporary directory — this is the "build context" namespace.
6. Dockerfile instructions execute. `COPY src/ /app/src/` resolves `src/` relative to the context root.

**Context sources (modern BuildKit):**
- Local directory: `docker build .` — standard case
- Remote URL: `docker build https://github.com/org/repo.git` — clones the repo as context
- stdin: `docker build - < Dockerfile` — Dockerfile from stdin, empty context
- Named context: `--build-context name=PATH` — add additional named contexts for multi-stage builds

**THE TRADE-OFFS:**
**Gain:** Any file in the context is accessible to COPY; context is versioned with the code.
**Cost:** Large contexts add build startup latency; forgotten secrets in context can end up in the image; context size is not visible without inspection.

---

### 🧪 Thought Experiment

**SETUP:**
A developer runs `docker build .` in a Node.js project directory. The directory contains `node_modules/` (250 MB), `.git/` (80 MB), and actual application source code (2 MB).

**WHAT HAPPENS WITHOUT `.dockerignore`:**
CLI tars 332 MB (250 + 80 + 2) and sends to daemon. Upload time to local Docker daemon: ~10 seconds. Upload time to remote BuildKit on CI server: ~45 seconds (at 60 MB/s network). Every PR build starts with a 45-second pause before any layer executes. The `node_modules/` from the host may also conflict with the `npm install` inside the Dockerfile, causing non-deterministic behaviour.

**WHAT HAPPENS WITH `.dockerignore`:**
`node_modules/` and `.git/` excluded. CLI tars 2 MB. Upload time: <1 second locally, ~0.03 seconds on CI. Additionally, `.git/` not included means `git` history metadata will not leak into the image even if accidentally `COPY . .`'d.

**THE INSIGHT:**
The build context is not just a performance detail — it is a security surface. Any file in the build context could be accidentally included in the image via a broad `COPY . .` instruction. A minimal `.dockerignore` is both a performance optimisation and a security control.

---

### 🧠 Mental Model / Analogy

> The build context is like the materials you load onto a delivery truck before sending it to the construction site. Everything on the truck can be used by the builders. Nothing that was left off the truck is accessible. Loading the whole house onto the truck (no `.dockerignore`) means the truck takes 3 hours to load and workers have to search through furniture for the actual building materials. A proper manifest (`.dockerignore`) means only the bricks and timber go on the truck — 5 minutes to load, exactly what's needed.

**Mapping:**
- "Delivery truck" → context tar archive sent to Docker daemon
- "Construction site" → Docker build engine environment
- "Materials manifest / packing list" → `.dockerignore` file
- "Builders can only use what's on-site" → COPY can only access context files
- "Accidentally loading furniture" → including `node_modules/` or `.git/` in context

**Where this analogy breaks down:** In real construction, you can call for more materials mid-build. In Docker, the context is fixed when the build starts — you cannot add files to the context mid-build. BuildKit's `--build-context` flag is the closest equivalent to a scheduled "additional delivery."

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you tell Docker to build an image, it needs to know which files you want to include. The build context is simply the folder you point it to. Docker packages up that folder and uses it during the build. The `.dockerignore` file is like a "do not pack" list.

**Level 2 — How to use it (junior developer):**
Always create a `.dockerignore` in your project root. At minimum, exclude: `node_modules/`, `.git/`, `*.log`, `dist/`, and any `.env` files. The context is the directory you pass to `docker build` — usually `.` for current directory. You can specify a custom path: `docker build -f docker/Dockerfile.prod ./`. The path after `-f` is the Dockerfile location; the path at the end is the build context directory (they can differ).

**Level 3 — How it works (mid-level engineer):**
The Docker CLI sends the build context as a tar archive to the Docker daemon's `/build` endpoint. With classic build, the entire archive (minus `.dockerignore` exclusions) is sent. With BuildKit, context files are sent lazily when they are actually referenced by a `COPY` instruction — this is an optimisation that prevents pre-sending huge contexts for multi-stage Dockerfiles where the first stage may never use most files. BuildKit also supports named build contexts (`--build-context name=path`), allowing multiple source directories to be addressed as named contexts in a Dockerfile (`COPY --from=local_context file .`  with `# syntax=docker/dockerfile:1.4`).

**Level 4 — Why it was designed this way (senior/staff):**
The client-server architecture of Docker (CLI → daemon) was designed for remote buildability — you could point your Docker CLI at a remote server and build there. This required the entire context to be transferred. The design proved to be a mistake for large repositories: monorepos with hundreds of packages send gigabytes of irrelevant files. BuildKit's lazy context transfer mitigates this, but the fundamental "client sends context to daemon" model remains. Alternatives: Kaniko runs the build entirely inside a container without a local Docker daemon — context is pulled from a GCS/S3 bucket or git repo, eliminating the client-upload step entirely. Remote build caches (BuildKit `--cache-from=registry`) further reduce the need for context transfers.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  BUILD CONTEXT FLOW                                      │
│                                                          │
│  docker build . (client side)                           │
│  1. Read .dockerignore → build exclusion list           │
│  2. Scan project directory (.)                          │
│  3. Exclude: node_modules/, .git/, *.log (per .ignore)  │
│  4. Tar remaining files → context.tar.gz                │
│  5. Send to daemon via /var/run/docker.sock             │
│                                                          │
│  Docker daemon / BuildKit (server side)                 │
│  6. Receive and extract context.tar.gz                  │
│  7. Execute Dockerfile instruction by instruction        │
│  8. COPY src/ /app/src/ → resolves src/ from context    │
│                                                          │
│  Build context directory structure:                     │
│  . (sent to daemon)                                     │
│  ├── Dockerfile                                         │
│  ├── package.json           ← included                  │
│  ├── src/                   ← included                  │
│  │   └── server.js                                      │
│  ├── node_modules/          ← EXCLUDED (.dockerignore)  │
│  └── .git/                  ← EXCLUDED (.dockerignore)  │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer: docker build -t myapp:1.0 .
→ CLI reads .dockerignore → tarball context created
→ [BUILD CONTEXT sent to daemon ← YOU ARE HERE]
→ Daemon starts Dockerfile execution
→ COPY instructions resolve from context
→ Image layers built → image created
```

**FAILURE PATH:**
```
"COPY failed: file not found in build context"
→ The file exists on developer's machine but is excluded by .dockerignore
→ or developer ran docker build from wrong directory
→ Fix: check .dockerignore, use correct build path
```

**WHAT CHANGES AT SCALE:**
In monorepo CI environments, context size can be several GB even with good `.dockerignore` files. Solutions: (1) use `docker build -f services/myapp/Dockerfile services/myapp/` to narrow context to one service; (2) use BuildKit `--build-context` to reference only needed subdirectories; (3) use Kaniko or remote contexts to move context out of the CI runner entirely.

---

### 💻 Code Example

Example 1 — Comprehensive `.dockerignore`:
```
# Dependencies (installed inside container)
node_modules/
vendor/
.venv/
__pycache__/

# Version control
.git/
.gitignore
.gitattributes

# IDE and OS files
.DS_Store
.idea/
.vscode/
*.swp
Thumbs.db

# Build artifacts (built inside container)
dist/
build/
*.pyc
*.class
*.jar

# Test files
tests/
test/
spec/
coverage/
.nyc_output/

# Logs and temp files
*.log
tmp/
temp/

# Secrets (never in context!)
.env
.env.*
*.pem
*.key
*_secret.*

# Documentation
README.md
docs/
```

Example 2 — Build with different context and Dockerfile location:
```bash
# Dockerfile at ./docker/Dockerfile.prod
# Build context at ./src/
docker build \
  -f docker/Dockerfile.prod \
  -t myapp:prod \
  ./src/
# Dockerfile.prod's COPY instructions reference files in ./src/

# Build from remote git repository (git URL as context)
docker build https://github.com/myorg/myrepo.git#main:frontend/
# Clones the repo, uses /frontend/ subdirectory as context
```

Example 3 — BuildKit named contexts (advanced):
```dockerfile
# syntax=docker/dockerfile:1.4
FROM alpine AS base

# Reference a named context added via --build-context
COPY --from=configs /etc/myapp/ /etc/myapp/
```
```bash
# Pass the named context:
docker build \
  --build-context configs=/path/to/config/files \
  -t myapp:1.0 .
```

---

### ⚖️ Comparison Table

| Context Source | Use Case | Latency | Freshness |
|---|---|---|---|
| **Local directory (`.`)** | Standard development | Depends on size | Immediate |
| Narrowed local directory | Monorepo single service | Fast | Immediate |
| Remote git URL | CI from git tag | Clone time | Git ref locked |
| Stdin (empty context) | Dockerfile only, no COPY | Instant | N/A |
| BuildKit named context | Multi-source builds | Per source | Flexible |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `.dockerignore` path patterns work like `.gitignore` exactly | `.dockerignore` uses a different matching engine — double-star `**` patterns and negation rules differ slightly from `.gitignore` |
| Files excluded from context can still be COPY'd | Excluded files are completely invisible to the build engine. COPY will fail with "file not found" if you exclude a file and then COPY it. |
| Large build contexts only waste upload time | A large context can also cause the build to fail if the daemon's `/tmp` filesystem fills up during context extraction |
| The Dockerfile must be in the build context directory | You can specify Dockerfile with `-f` flag to any path. The build context and Dockerfile location are independent. |
| BuildKit always sends the entire context at once | Modern BuildKit uses lazy context transfer — it only fetches from the context the files referenced by `COPY` instructions, when those instructions are reached |

---

### 🚨 Failure Modes & Diagnosis

**Accidentally Including `.env` in Image**

**Symptom:** Security scan finds database credentials inside the container image; `docker history --no-trunc` shows `.env` file was copied.

**Root Cause:** `COPY . .` in Dockerfile copies everything in context, including `.env`. No `.dockerignore` excludes `.env`.

**Diagnostic Command / Tool:**
```bash
# Check if sensitive files ended up in the image
docker run --rm myapp cat /app/.env
# Or:
docker create --name inspect myapp
docker cp inspect:/ /tmp/image_contents/
# Existence of /tmp/image_contents/app/.env confirms the problem
```

**Fix:** Add `.env` and `.env.*` to `.dockerignore`. Remove the compromised image from the registry immediately. Rotate all credentials in the `.env` file.

**Prevention:** Add to CI: `docker run --rm myapp ls /app | grep -i "env\|secret"` → fail build if these files exist in the container.

---

**Slow Build Context Upload (Large Context)**

**Symptom:** `docker build` prints "Sending build context to Docker daemon: 1.2GB" — build takes 2 minutes before any layer starts.

**Root Cause:** Missing `.dockerignore`; `node_modules/` (800 MB) and `.git/` (400 MB) included in context.

**Diagnostic Command / Tool:**
```bash
# Measure what would be sent (du of the would-be context)
du -sh . --exclude=".git" --exclude="node_modules"
# Compare to full: du -sh .

# Preview what docker would include (no actual build)
# Use: https://github.com/pwaller/docker-show-context
docker-show-context
```

**Fix:** Create `.dockerignore` with `node_modules/` and `.git/`.

**Prevention:** Add a CI build context size check: `bash -c 'tar czf /dev/null . 2>&1 | ...` — alert if context > 50 MB.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dockerfile` — the build specification that uses the build context
- `Docker Image` — what the build produces from the Dockerfile + context

**Builds On This (learn these next):**
- `Docker BuildKit` — modern build engine with lazy context transfer and named contexts
- `Multi-Stage Build` — uses build context efficiently across multiple stages

**Alternatives / Comparisons:**
- `Kaniko` — builds images without sending context to a Docker daemon; context pulled from remote storage
- `BuildKit Remote Cache` — allows context and cache to live in a registry rather than on the build machine

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Files packaged and sent to the Docker    │
│              │ daemon before build starts               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Large contexts (node_modules, .git) make │
│ SOLVES       │ builds slow; secrets leak into images    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ .dockerignore = performance + security:  │
│              │ smaller context, no secret leaks         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always create .dockerignore in every     │
│              │ project that has a Dockerfile            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never include secrets, node_modules/,   │
│              │ .git/, or build artifacts in context     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Larger context = all files available vs  │
│              │ slow builds + secret exposure risk       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The packing list for the build engine — │
│              │  .dockerignore keeps it lean and safe"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Multi-Stage Build → Docker BuildKit      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team runs `docker build .` in a monorepo root containing 50 services. Each service has its own `Dockerfile`. There is one `.dockerignore` at the root. When building `services/payments/Dockerfile`, the context includes all files from all 50 services (5 GB). Describe three different architectural approaches to solving this context bloat — ranging from a simple file-system change to a full build tool adoption — and analyse the trade-offs of each in terms of developer experience and CI cache effectiveness.

**Q2.** A developer commits their `docker build` command wrapped in a Makefile: `docker build --no-cache -f Dockerfile.prod .`. The `--no-cache` flag means every build starts fresh. In a team with 20 developers pushing multiple PRs per day, what is the exact performance and cost impact of this flag compared to a properly cached build? Design the caching architecture that allows the CI system to achieve cache hits across different PR builds efficiently.

