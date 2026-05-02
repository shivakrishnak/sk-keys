---
layout: default
title: "Docker Compose"
parent: "Containers"
nav_order: 828
permalink: /containers/docker-compose/
number: "0828"
category: Containers
difficulty: ★★☆
depends_on: Docker, Dockerfile, Container Networking, Volume Mounts
used_by: Container Orchestration, Container Health Check, Container Logging
related: Docker, Container Networking, Volume Mounts, Container Orchestration, Kubernetes Architecture
tags:
  - containers
  - docker
  - devops
  - intermediate
  - architecture
---

# 828 — Docker Compose

⚡ TL;DR — Docker Compose is a tool for defining and running multi-container applications with a single YAML file — spinning up a full local stack (app + database + cache) with one `docker compose up`.

| #828 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Docker, Dockerfile, Container Networking, Volume Mounts | |
| **Used by:** | Container Orchestration, Container Health Check, Container Logging | |
| **Related:** | Docker, Container Networking, Volume Mounts, Container Orchestration, Kubernetes Architecture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer needs to run their application locally. The app requires: a PostgreSQL database, a Redis cache, a message broker (RabbitMQ), and the application itself. Without Docker Compose, the developer has to: run `docker run postgres:16 ...` with the right env vars; run `docker run redis:7 ...`; run `docker run rabbitmq:3-management ...`; then run the app, making sure each container is configured with the right network settings to reach the others. If the developer restarts their laptop, none of it is running. If they onboard a new team member, they send a 15-step setup guide. If the versions in the guide drift from reality, the new developer's environment behaves differently.

**THE BREAKING POINT:**
Multi-container applications need a declarative way to define the full stack — all services, their dependencies, network connections, volumes, and environment configuration — as code, so the entire environment is reproducible with one command.

**THE INVENTION MOMENT:**
This is exactly why Docker Compose was created — a single `compose.yaml` file that describes the entire multi-service application. One `docker compose up` brings everything online. One `docker compose down` tears it all down.

---

### 📘 Textbook Definition

**Docker Compose** is a tool for defining and orchestrating multi-container Docker applications using a declarative YAML configuration file (`compose.yaml` or `docker-compose.yml`). A Compose file specifies services (containers), their images or Dockerfile build instructions, environment variables, port mappings, volume mounts, network connections, health check dependencies, and resource limits. Docker Compose is optimised for local development and simple single-host deployments — it is not a production orchestration platform (Kubernetes is). As of Compose v2 (2022), it ships as a Docker CLI plugin (`docker compose` vs legacy `docker-compose`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Docker Compose is the one file that defines your entire local multi-container stack so `docker compose up` replaces a dozen `docker run` commands.

**One analogy:**
> Docker Compose is like a stage director's script. Instead of separately telling each actor (container) where to stand, what to say, and when to enter, the director writes one script that coordinates everyone. `docker compose up` is "begin performance" — all actors take their places in the right order. `docker compose down` is "end performance, everyone go home." One script, full coordination.

**One insight:**
Docker Compose does not exist in production. Its value is reproducible local environments: every developer on the team runs the same `docker compose up` from the same `compose.yaml` and gets an identical environment — same database version, same config, same network topology. "Works on my machine" becomes "works on every machine that runs compose up."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Multi-container applications need startup ordering, networking, and configuration coordination.
2. That coordination must be expressed as code (reproducible, version-controllable) not manual instructions.
3. A developer should be able to spin up a complete local stack from a cold start with one command.

**DERIVED DESIGN:**

A `compose.yaml` defines:

```yaml
services:          # Named containers
  app:             # Service name (DNS name on compose network)
    build: .       # Build from local Dockerfile
    ports: ["8080:3000"]
    depends_on:
      db:
        condition: service_healthy  # Wait for DB health check
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/mydb

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: pass
    volumes:
      - pg_data:/var/lib/postgresql/data  # Named volume
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s
      retries: 5

volumes:
  pg_data:         # Persistent named volume
networks:
  default:         # Compose creates a shared network automatically
```

**Service discovery:** Compose creates a Docker network. Services are addressable by their service name as DNS within this network — `app` can connect to `db:5432` directly (no IP needed).

**Startup ordering:** `depends_on: condition: service_healthy` waits for the dependency's health check to pass before starting the dependent service.

**THE TRADE-OFFS:**
**Gain:** Single-command stack startup; reproducible developer environments; declarative, version-controlled config; service discovery by DNS name.
**Cost:** Not designed for production (no multi-host scheduling, no self-healing, no rolling deploys); `depends_on` only waits for health check, not application readiness; secrets management is basic (env vars in plain text unless using Compose secrets).

---

### 🧪 Thought Experiment

**SETUP:**
A new developer joins the team on a Monday morning. The application needs Postgres 16.2, Redis 7.2, RabbitMQ 3.12, and the Node.js app itself. There is no `compose.yaml`.

**WITHOUT DOCKER COMPOSE:**
The new developer receives a `SETUP.md` with 18 steps. They install Docker. Run `docker run postgres:16`. They forget the `-e POSTGRES_PASSWORD` flag — the container crashes silently. They Google the right flags. Start Postgres. Start Redis (correct this time). Start RabbitMQ — need to enable the management plugin. Enable it. Start the Node.js app — it cannot connect to Postgres because the container names were different from the README. Four hours later, it works. The environment is different from their colleague's because they used Redis 7.1 (latest at the time of the README) while the code assumes 7.2 behaviour.

**WITH DOCKER COMPOSE:**
Developer opens the repo. Reads `README.md`: "Run `docker compose up`." Runs it. All four services start. App is accessible at `localhost:8080`. Time: 4 minutes (image pull time). Environment is identical to every teammate's.

**THE INSIGHT:**
The `compose.yaml` file is not just a convenience — it is the environmental contract for the application. Every line is a documented decision: versions, configuration, network topology. Onboarding cost drops from days to minutes.

---

### 🧠 Mental Model / Analogy

> Docker Compose is like an orchestra score for containers. Each instrument (container) has its own part, but the score coordinates when each instrument plays, relative to the others. The conductor (Docker Compose) follows the score: bring in the strings first (database), then the woodwinds (cache), then the full orchestra (application). One score, one conductor, reproducible performance every time.

**Mapping:**
- "Orchestra score" → `compose.yaml` file
- "Each instrument" → each service/container
- "Conductor" → Docker Compose engine
- "When each instrument plays" → `depends_on` startup ordering
- "Same piece every performance" → identical environment on every `docker compose up`

**Where this analogy breaks down:** An orchestra has a single collective performance; Docker Compose services run independently and continue running after startup. The orchestra analogy works best for the startup phase, less well for the ongoing running state.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Docker Compose lets you describe your entire application — your app, its database, and any other services — in one text file. Then one command starts everything and another command stops everything. It is like a single "on/off switch" for your entire development environment.

**Level 2 — How to use it (junior developer):**
Create `compose.yaml` in your project root. Define services with `image:` or `build:`. Run `docker compose up -d` (detached mode). Check with `docker compose ps`. See logs with `docker compose logs -f app`. Update code, rebuild with `docker compose up --build app`. Tear down with `docker compose down` (add `-v` to delete volumes). Use `docker compose exec app bash` to open a shell in the running app container.

**Level 3 — How it works (mid-level engineer):**
Compose reads the YAML and translates it into Docker API calls: for each service, it resolves the image (build if `build:` is specified, pull if `image:` only), creates the container with the specified configs, attaches it to the compose-named network (`<project_dir>_default` by default), creates named volumes if they don't exist, starts containers in dependency order (respecting `depends_on`). Health checks are implemented as Docker health checks that continue running in the container — `service_healthy` condition polls the Docker health check status. Override files (`compose.override.yaml`) allow environment-specific customisation without modifying the base file.

**Level 4 — Why it was designed this way (senior/staff):**
Docker Compose was originally a separate Python tool called `fig` (acquired by Docker in 2014) and evolved into `docker-compose` (Python), then `docker compose` (Go, v2, 2022 as Docker CLI plugin). The Compose Specification was open-sourced in 2020, enabling third-party tools (Podman Compose, podman-compose) to implement the same YAML format. The design decision to make Compose explicitly single-host was intentional: multi-host scheduling (Swarm) was a separate tool. This clean boundary prevented Compose from becoming a half-baked Kubernetes — it stayed simple for its intended use case. The ongoing debate: should Compose be used for simple production deployments (single server)? The Compose Spec says yes for services that fit one host; engineers argue Kubernetes is always preferable for operational reasons (health checks, restarts, rolling deploys) even at small scale.

---

### ⚙️ How It Works (Mechanism)

```yaml
# compose.yaml — annotated
version: "3.9"  # Compose file version (optional in v2)

services:

  # ─── Application ─────────────────────────────────────
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:3000"              # host:container
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/myapp
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy  # wait for DB ready
      cache:
        condition: service_started  # just started is enough
    restart: unless-stopped         # restart policy

  # ─── PostgreSQL Database ──────────────────────────────
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - pg_data:/var/lib/postgresql/data  # persistent
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

  # ─── Redis Cache ──────────────────────────────────────
  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  pg_data:       # persists across compose down/up
  redis_data:

networks:
  default:
    name: myapp_network
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
docker compose up
→ Pull/build service images
→ Create named volumes (if not exist)
→ Create compose network
→ Start db and cache (no depends_on)
→ Wait for db health check to pass
→ [APP SERVICE STARTS ← YOU ARE HERE]
→ All services running, shared network, DNS resolution
→ docker compose ps → all "healthy/running"
```

**FAILURE PATH:**
```
db health check fails (e.g., Postgres misconfigured)
→ app service does not start (depends_on condition not met)
→ docker compose up shows: "Waiting for db to be healthy"
→ eventually times out / errors
→ diagnostic: docker compose logs db
```

**WHAT CHANGES AT SCALE:**
Docker Compose is single-host — everything runs on one machine. When an application grows beyond one machine's capacity, the path forward is Kubernetes. However, Docker Compose remains valuable even for large production services as the local development environment — teams run `docker compose up` locally and deploy to Kubernetes in CI/CD. The `compose.yaml` serves as a blueprint and documentation of the service topology even if it is not used directly in production.

---

### 💻 Code Example

Example 1 — Essential Compose commands:
```bash
# Start all services (detached, rebuild if needed)
docker compose up -d --build

# Check status (health, ports, running state)
docker compose ps

# Stream logs for all services
docker compose logs -f

# Stream logs for one service only
docker compose logs -f app

# Execute command in running container
docker compose exec app sh
docker compose exec db psql -U user -d myapp

# Rebuild and restart only one service
docker compose up --build --force-recreate app

# Stop all services (containers remain, volumes persist)
docker compose stop

# Stop and remove containers (volumes persist)
docker compose down

# Stop and remove EVERYTHING including volumes
docker compose down -v
```

Example 2 — Override file for CI environment:
```yaml
# compose.override.yaml (automatically merged with compose.yaml)
services:
  app:
    environment:
      DATABASE_URL: postgres://ci_user:ci_pass@db:5432/ci_db
      NODE_ENV: test
    command: ["npm", "test"]  # override default command for CI
  db:
    environment:
      POSTGRES_USER: ci_user
      POSTGRES_PASSWORD: ci_pass
      POSTGRES_DB: ci_db
```
```bash
# Use override file explicitly
docker compose -f compose.yaml -f compose.ci.yaml up
```

Example 3 — Health check + depends_on pattern:
```yaml
services:
  api:
    image: myapi:latest
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 3s
      retries: 10    # try 10 times before giving up
      start_period: 5s  # grace period before health checks start

  redis:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      retries: 5
```

---

### ⚖️ Comparison Table

| Tool | Scope | HA/Scaling | Rolling Deploys | Best For |
|---|---|---|---|---|
| **Docker Compose** | Single host | No | No | Local dev, simple deployments |
| Docker Swarm | Multi-host | Yes (limited) | Yes | Small prod on bare metal |
| Kubernetes | Multi-host cluster | Yes (full) | Yes | Production at any scale |
| Helm (on Kubernetes) | Multi-host | Yes (full) | Yes | Kubernetes application packaging |

**How to choose:** Docker Compose for local development — always. Production on a single server with no redundancy requirements — Docker Compose is viable but Kubernetes is better for operational reasons. Any multi-host or HA requirement — Kubernetes. The `compose.yaml` local dev file and the Kubernetes manifests for production are maintained separately.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Docker Compose is production-ready for all use cases | Compose lacks health-based routing, rolling deploys, multi-host scheduling, and automatic recovery — it is primarily a developer tool |
| `depends_on` guarantees the dependency is ready | `depends_on: condition: service_started` only waits for the container to start; the process inside may not be ready to accept connections. Use `service_healthy` with a health check for application-level readiness. |
| `docker compose down` removes everything | By default, `down` removes containers and networks but NOT volumes. Use `-v` to also remove volumes. |
| Changes to `compose.yaml` take effect immediately | You must run `docker compose up` again (or `docker compose up --build`) for changes to a service's image, config, or ports to take effect. |
| Compose is deprecated in favour of Kubernetes | Compose v2 is actively maintained and is the standard dev environment tool. Kubernetes is for production orchestration — the two serve different purposes. |

---

### 🚨 Failure Modes & Diagnosis

**Service Not Starting (Dependency Not Healthy)**

**Symptom:** `docker compose up` hangs; app service says "Waiting for db" indefinitely.

**Root Cause:** Database health check is misconfigured — `pg_isready` returns success before PostgreSQL is accepting connections.

**Diagnostic Command / Tool:**
```bash
# Check logs of the failing dependency
docker compose logs db

# Manually run the health check
docker compose exec db pg_isready -U user -d myapp
# If this hangs or fails → health check command is wrong

# Check what Docker thinks the health status is
docker inspect $(docker compose ps -q db) \
  | jq '.[0].State.Health'
```

**Fix:** Fix the health check command. For Postgres: use `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}`.

**Prevention:** Test your health check command manually (`docker exec`) before relying on it in `depends_on: service_healthy`.

---

**Port Already in Use**

**Symptom:** `docker compose up` fails with `Bind for 0.0.0.0:5432 failed: port is already allocated`.

**Root Cause:** A previously stopped (not removed) container or host process is already bound to port 5432.

**Diagnostic Command / Tool:**
```bash
# Find what's using the port on Linux/Mac
lsof -i :5432

# Find using Docker
docker ps -a | grep 5432
```

**Fix:** `docker compose down` to remove containers. Or kill the offending host process.

**Prevention:** Use `docker compose down` (not just `stop`) at end of day. Or map to non-standard ports in `compose.yaml` to avoid conflicts with host services.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker` — Compose is a higher-level abstraction over Docker
- `Dockerfile` — Compose uses Dockerfiles (via `build:`) or images directly

**Builds On This (learn these next):**
- `Container Networking` — Compose creates and manages a Docker network for all services
- `Container Orchestration` — Kubernetes is the production equivalent of Compose at scale

**Alternatives / Comparisons:**
- `Kubernetes (local: k3d/minikube)` — runs Kubernetes locally for production-parity environment
- `Docker Swarm` — Docker's native simple multi-host mode; uses a Compose-compatible format

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ YAML-defined multi-container orchestration│
│              │ for dev: one file, one command, full stack│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-container local dev requires many  │
│ SOLVES       │ manual docker run commands per developer  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The compose.yaml IS the environmental    │
│              │ contract — version-controlled, exact      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Local development, CI test environments, │
│              │ simple single-host demos                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Multi-host production; HA requirements;  │
│              │ rolling deploys — use Kubernetes instead  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Dead-simple dev env vs no production     │
│              │ orchestration capabilities               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The orchestra score for containers —    │
│              │  all instruments, one conductor command" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Container Networking → Container         │
│              │ Orchestration → Kubernetes               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team's `compose.yaml` has `POSTGRES_PASSWORD: mysecretpassword` as a plaintext environment variable. This file is committed to a public GitHub repository. A team member argues "it's fine because this is only local development — prod uses Kubernetes secrets." Identify every threat scenario where this plaintext password in a committed compose file creates a real security risk, including scenarios beyond "attacker reads GitHub." Then design the minimal change to `compose.yaml` and developer workflow that eliminates these risks without significantly increasing developer friction.

**Q2.** A microservices team has 8 services, each with its own `compose.yaml`. Developers need to run 3–5 services simultaneously for different feature branches. Currently, they manually start and stop individual service compose files. Design a developer environment architecture that allows a developer to spin up any combination of 3–5 services from different repositories with their inter-service networking and shared databases configured correctly — and specify how version mismatches between services are handled (e.g., service-A v1.2 expects service-B v2.0, but the developer has service-B v1.9 running).

