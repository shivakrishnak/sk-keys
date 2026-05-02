---
layout: default
title: "Docker Build Context"
parent: "Containers"
nav_order: 826
permalink: /containers/docker-build-context/
number: "826"
category: Containers
difficulty: ★★☆
depends_on: "Dockerfile, Docker Layer, Docker Image"
used_by: "Multi-Stage Build, CI-CD pipelines"
tags: #containers, #docker, #build-context, #dockerignore, #buildkit
---

# 826 — Docker Build Context

`#containers` `#docker` `#build-context` `#dockerignore` `#buildkit`

⚡ TL;DR — The **Docker build context** is the set of files sent to the Docker daemon when you run `docker build`. By default, it's the entire current directory (`.`). Large build contexts (including `node_modules`, `.git`) slow builds and waste bandwidth. Solution: `.dockerignore` file to exclude irrelevant files. BuildKit enables remote contexts, Git URLs, and more efficient context handling.

| #826            | Category: Containers                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------- | :-------------- |
| **Depends on:** | Dockerfile, Docker Layer, Docker Image |                 |
| **Used by:**    | Multi-Stage Build, CI-CD pipelines     |                 |

---

### 📘 Textbook Definition

**Docker build context**: the set of files and directories that are available to the `COPY` and `ADD` instructions in a Dockerfile during `docker build`. When `docker build .` is executed, the Docker CLI **tars up the entire build context directory** and sends it to the Docker daemon (which may be remote). The daemon has no direct access to the client's filesystem — the build context is the only way to provide files. Key implications: (1) any file referenced in `COPY` must be inside the build context; (2) the build context is sent in full before any build step executes — a large context (GB of `node_modules`) adds significant latency before the first layer is processed; (3) the `.dockerignore` file (in the build context root) specifies patterns to exclude from the context, analogous to `.gitignore`. Build context sources: a local directory (`.`), a URL (Git repo, tar archive), or stdin (`docker build - < archive.tar.gz`). BuildKit enables more efficient context transfer: only changed files, parallel layer building, and support for remote contexts.

---

### 🟢 Simple Definition (Easy)

`docker build .` — the `.` is the build context. Docker tars up everything in that directory and sends it to the Docker daemon. The `COPY` instruction in your Dockerfile can only copy files that were in that tar. Problem: if your directory has `node_modules/` (500MB), Docker sends 500MB to the daemon before doing anything. Solution: `.dockerignore` file — like `.gitignore` — tells Docker "don't include these files."

---

### 🔵 Simple Definition (Elaborated)

The build context is a source of three problems:

1. **Size/speed**: 500MB `node_modules` + 200MB `.git` history → Docker sends 700MB to the daemon before processing the first Dockerfile line. In CI, this is bandwidth + time waste.

2. **Security**: accidentally `COPY . .` with a `.env` file containing secrets, a private key, or credentials in the context → secrets baked into the image. Anyone with image access has the secrets.

3. **Cache invalidation**: if any file in the `COPY . .` context changes (even log files, build artifacts, `.DS_Store`), the COPY layer cache is invalidated → rebuilds all subsequent layers. Selective COPY + `.dockerignore` maintains cache stability.

The `.dockerignore` file is the primary mitigation for all three.

---

### 🔩 First Principles Explanation

```
HOW BUILD CONTEXT WORKS:

  User runs: docker build -t myapp:1.0 .

  Step 1: Docker CLI reads .dockerignore
  Step 2: Docker CLI tars context directory (excluding .dockerignore patterns)
  Step 3: Sends tar to Docker daemon via Unix socket (or TCP for remote daemon)
  Step 4: Daemon unpacks tar into a temporary directory
  Step 5: Processes Dockerfile; COPY reads from unpacked context directory

  Timeline:
  [0ms]    CLI starts context tar
  [2000ms] Context tar (700MB) sent to daemon ← THE BOTTLENECK
  [2001ms] First Dockerfile instruction processed
  [2002ms] FROM: pull base image (if not cached)
  [3000ms] RUN: execute command
  [3100ms] COPY app.py /app/  ← reads from context (already in daemon)
  ...

  With .dockerignore (context = 2MB):
  [0ms]    CLI starts context tar
  [10ms]   Context tar (2MB) sent to daemon
  [11ms]   First Dockerfile instruction processed ← 200x faster start

.dockerignore SYNTAX:

  .git                  # exclude entire .git directory
  node_modules          # exclude node_modules (npm)
  __pycache__           # exclude Python bytecode cache
  *.pyc                 # exclude .pyc files
  .env                  # CRITICAL: exclude env files with secrets
  .env.*                # exclude .env.local, .env.production, etc.
  dist/                 # exclude built output (rebuilt in Docker)
  coverage/             # exclude test coverage reports
  .DS_Store             # macOS metadata
  Thumbs.db             # Windows thumbnail cache
  *.log                 # exclude log files
  .dockerignore         # exclude itself (good practice)
  Dockerfile*           # exclude Dockerfiles from context (not needed by COPY)
  **/*.test.ts          # exclude test files (if not needed in image)
  !important.log        # re-include specific file (! prefix = negation)

  PATTERN RULES (same as .gitignore):
  /dir       → root-level dir only
  dir/       → any dir named "dir"
  *.txt      → any .txt file at any depth
  **/*.txt   → any .txt file at any depth (explicit)
  !keep.txt  → re-include after previous exclusion

BUILD CONTEXT SOURCES:

  1. Local directory (default):
  docker build .                          # context = current directory
  docker build /path/to/project          # context = specific path
  docker build -f myapp/Dockerfile .      # Dockerfile at different path

  2. Git URL (BuildKit):
  docker build https://github.com/user/repo.git
  docker build https://github.com/user/repo.git#main:subdir
  # Clones repo; uses repo root (or subdir) as context
  # No local files needed!

  3. Tar archive:
  docker build - < archive.tar.gz        # stdin
  docker build https://example.com/context.tar.gz

  4. Remote Dockerfile + no context (BuildKit):
  docker build --no-context -f Dockerfile .
  # Dockerfile uses only RUN (no COPY); context size = 0

BUILDKIT CONTEXT EFFICIENCY:

  Legacy builder: sends ENTIRE context directory on every build
  BuildKit: sends only CHANGED files (incremental context transfer)

  File content hash comparison:
  BuildKit: "have you seen sha256:abc for file app.py?" → "yes" → skip
  Legacy: sends app.py every time regardless

  Result: large codebases, small code changes → BuildKit sends only deltas

  Enable BuildKit: export DOCKER_BUILDKIT=1 or add to /etc/docker/daemon.json:
  {"features": {"buildkit": true}}
  (Default since Docker 23.0)
```

---

### ❓ Why Does This Exist (Why Before What)

The Docker architecture separates the CLI (client) from the daemon (server) — the daemon may be remote (on a different machine, in a VM on Mac/Windows). Since the daemon has no direct filesystem access to the client, the build context is the explicit mechanism for providing files. This design enables remote Docker daemons and remote builds (Docker-in-Docker in CI, remote build clusters with Docker Buildx builders). The size problem is a consequence of this design: the context must be fully transferred before the build begins.

---

### 🧠 Mental Model / Analogy

> **The build context is the ingredients you bring to the chef's kitchen**: `docker build .` is like going to a cooking class and bringing your entire pantry (including the things the recipe doesn't call for). The chef (Docker daemon) can only work with what you brought. If you brought 500MB of ingredients you don't need, you wasted time carrying them. `.dockerignore` is your shopping list — it tells you exactly which ingredients to pack. `COPY` in the Dockerfile is the chef picking specific ingredients from what you brought.

---

### ⚙️ How It Works (Mechanism)

```
CONTEXT SIZE DIAGNOSTIC:

  # Check what would be in the context (without building):
  docker build --no-cache --progress=plain 2>&1 | head -5
  # Output: "Sending build context to Docker daemon  2.048kB"

  # Or use .dockerignore check:
  docker build --dry-run .  # (BuildKit only: shows context files without building)

MULTI-STAGE BUILD WITH CONTEXT:

  # Only the final stage uses files from context
  FROM node:18 AS builder
  COPY package*.json ./        ← needs package.json from context
  RUN npm ci
  COPY src/ ./src/             ← needs src/ from context
  RUN npm run build

  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html  ← copies from builder stage, NOT context
  # COPY nginx.conf .         ← if you need nginx.conf, it needs to be in context

  # .dockerignore for this project:
  node_modules/                # don't need (RUN npm ci rebuilds it)
  dist/                        # don't need (RUN npm build recreates it)
  .git/                        # never needed
  .env*                        # SECURITY: never send secrets
  coverage/
  *.test.ts
```

---

### 🔄 How It Connects (Mini-Map)

```
docker build needs files to COPY into the image
        │
        ▼
Docker Build Context ◄── (you are here)
(files sent to daemon; filtered by .dockerignore)
        │
        ├── Dockerfile: COPY/ADD instructions reference files in the context
        ├── Docker Layer: context files trigger cache invalidation when changed
        ├── Multi-Stage Build: only final stage needs context files
        └── BuildKit: incremental context transfer (only changed files)
```

---

### 💻 Code Example

```
# Typical .dockerignore for a Node.js project
node_modules/
npm-debug.log*
yarn-error.log

# Build artifacts
dist/
build/
.next/

# Test artifacts
coverage/
.nyc_output/
**/*.test.js
**/*.spec.js
__tests__/

# Git
.git/
.gitignore

# Environment / secrets
.env
.env.*
!.env.example      # keep the example file (no real secrets)

# Editor
.vscode/
.idea/
*.swp
.DS_Store

# Docker itself
Dockerfile*
.dockerignore

# Logs
*.log
logs/
```

```bash
# Verify context size before building
docker build --no-cache . 2>&1 | grep "Sending build context"
# Expected: "Sending build context to Docker daemon  1.234MB"
# Problem: "Sending build context to Docker daemon  1.234GB" → check .dockerignore

# Build from Git URL (no local files needed)
docker build \
  --build-arg VERSION=1.2.3 \
  https://github.com/myorg/myapp.git#v1.2.3
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                     |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The Dockerfile must be inside the build context       | The Dockerfile and build context are independent. `docker build -f /path/to/Dockerfile .` uses a Dockerfile outside the context directory. The build context is just the directory from which `COPY` reads. |
| Files excluded by .dockerignore can't be used in COPY | Correct — files excluded from the build context simply don't exist from the daemon's perspective. `COPY` of an excluded file fails with "file not found."                                                   |
| The build context is re-sent on every build           | BuildKit (default since Docker 23) performs incremental context transfer: only files that have changed since the last build are re-sent. The legacy builder re-sends the full context every time.           |

---

### 🔥 Pitfalls in Production

```
PITFALL: .env files in build context → secrets in image

  # ❌ Project has .env file:
  # .env:
  # DATABASE_URL=postgresql://user:secretpassword@prod-db:5432/app
  # AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7...

  # Dockerfile:
  COPY . /app/   ← copies .env into image

  # Anyone with image access: docker run myapp cat /app/.env → secrets exposed
  # Also: CI/CD artifacts, ECR images, Docker Hub public images

  # ✅ FIXES:
  # 1. Add .env to .dockerignore (prevents it from entering context)
  echo ".env" >> .dockerignore
  echo ".env.*" >> .dockerignore

  # 2. Never COPY . . — always COPY specific files
  COPY src/ /app/src/
  COPY package.json /app/
  # Never copies .env even if not in .dockerignore

  # 3. Secrets at runtime: inject via environment variable
  docker run -e DATABASE_URL="$DATABASE_URL" myapp
  # or Kubernetes Secrets, AWS Secrets Manager, Vault
```

---

### 🔗 Related Keywords

- `Dockerfile` — the recipe that uses the build context via `COPY`/`ADD`
- `Docker Layer` — context file changes trigger layer cache invalidation
- `Multi-Stage Build` — reduces the context files needed in the final stage
- `Docker` — the CLI that tars and sends the build context to the daemon
- `BuildKit` — enables incremental context transfer and remote build contexts

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BUILD CONTEXT: files tarred + sent to Docker daemon     │
│ Default: entire current directory (docker build .)      │
│ .dockerignore: exclude files (like .gitignore)          │
│                                                          │
│ ALWAYS EXCLUDE:                                          │
│   node_modules/ .git/ .env* dist/ coverage/ *.log       │
│                                                          │
│ SOURCES: local dir | git URL | tar archive | stdin      │
│ BuildKit: incremental context (only changed files)      │
├──────────────────────────────────────────────────────────┤
│ Rule: context < 10MB for fast CI builds                 │
│ Security: .env* in .dockerignore is non-negotiable     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In a monorepo with 50 services, each service has its own Dockerfile. Running `docker build .` from the monorepo root sends the ENTIRE monorepo as the build context, even though each service only needs its own directory and perhaps some shared libraries. Docker Buildx supports the `--context` flag and BuildKit supports `--build-context name=path` for named contexts. How would you structure a monorepo Docker build to minimize context size while still sharing common code between services?

**Q2.** BuildKit supports building Docker images from a Git URL: `docker build https://github.com/org/repo.git#main`. This means the build happens without any local files. What are the security implications? When a CI system builds from a Git URL, what guarantees do you have about which code is being built? How do you prevent supply-chain attacks where someone modifies the repo between your code review and the CI build?
