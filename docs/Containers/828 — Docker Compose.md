---
layout: default
title: "Docker Compose"
parent: "Containers"
nav_order: 828
permalink: /containers/docker-compose/
number: "828"
category: Containers
difficulty: ★★☆
depends_on: "Docker, Dockerfile, Docker Image"
used_by: "Local development environments, integration testing, CI pipelines"
tags: #containers, #docker, #docker-compose, #multi-container, #local-dev
---

# 828 — Docker Compose

`#containers` `#docker` `#docker-compose` `#multi-container` `#local-dev`

⚡ TL;DR — **Docker Compose** is a tool for defining and running multi-container applications. A `compose.yaml` file declares all services (app, database, cache, message broker) with their images, ports, volumes, networks, and environment variables. `docker compose up` starts the entire environment; `docker compose down` tears it down. Primary use: local development and integration testing where spinning up the full stack (app + dependencies) replaces "it works on my machine" problems.

| #828 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Docker, Dockerfile, Docker Image | |
| **Used by:** | Local development environments, integration testing, CI pipelines | |

---

### 📘 Textbook Definition

**Docker Compose**: a tool (originally `docker-compose` v1, now `docker compose` plugin v2) for defining and running multi-container Docker applications. Configuration: `compose.yaml` (or `docker-compose.yml`) — a YAML file declaring `services`, `networks`, `volumes`, and `configs`. Each service specifies a Docker image (or `build:` context for local builds), ports, environment variables, volumes, dependencies (`depends_on`), health checks, and resource limits. Compose creates a default network for all services (services can reach each other by service name as hostname). `docker compose up`: creates/starts all services in dependency order. `docker compose down`: stops and removes containers, networks (not volumes by default). `docker compose up --build`: rebuilds images before starting. Key design principle: Compose models the entire application stack as infrastructure-as-code — a single `compose.yaml` replaces a wiki page of "how to set up the dev environment." Docker Compose is NOT designed for production orchestration (Kubernetes handles that); it's designed for local development, testing, and single-host deployments.

---

### 🟢 Simple Definition (Easy)

A Node.js app needs: the app itself, a PostgreSQL database, a Redis cache, and a message broker. Without Docker Compose, you'd `docker run` each container with the right flags, networks, and volumes. You'd do this every time. Docker Compose lets you write all of this in one YAML file (`compose.yaml`), then `docker compose up` starts everything. `docker compose down` stops it. New developer joining the team: clone repo → `docker compose up` → full stack running.

---

### 🔵 Simple Definition (Elaborated)

Docker Compose solves the local development problem: production services depend on databases, caches, queues — running and configuring these manually is fragile and time-consuming. Compose treats the multi-container stack as code: versioned, reproducible, shareable. Key capabilities:

- **Service discovery**: services in the same Compose project can reach each other by service name (the app container reaches PostgreSQL via `postgres:5432`, not an IP address)
- **Dependency ordering**: `depends_on` + health checks ensure the database is ready before the app starts
- **Volume management**: named volumes persist database data across `docker compose down/up`
- **Environment overrides**: `compose.override.yaml` for dev overrides without changing the base file
- **Scale**: `docker compose up --scale worker=3` runs 3 instances of the worker service

**Important limits**: Compose is single-host. For multi-host production, use Kubernetes. Compose is not a replacement for Kubernetes — it's a development convenience.

---

### 🔩 First Principles Explanation

```
compose.yaml STRUCTURE:

  version: "3.9"     ← deprecated; Compose v2 doesn't need this
  
  services:          ← each service = one container (or scaled set)
    app:             ← service name (also: hostname on the default network)
      build:         ← build from Dockerfile (alternative to image:)
        context: .
        dockerfile: Dockerfile
        target: dev  ← multi-stage target
      image: myapp:dev
      ports:
        - "3000:3000"        ← host:container port mapping
      environment:           ← environment variables
        NODE_ENV: development
        DATABASE_URL: postgresql://postgres:password@postgres:5432/mydb
        REDIS_URL: redis://redis:6379
      env_file:              ← load env vars from file (.env)
        - .env.local
      volumes:
        - .:/app              ← bind mount: source:target (dev hot-reload)
        - /app/node_modules   ← anonymous volume: prevents host node_modules from overriding container's
      depends_on:
        postgres:
          condition: service_healthy   ← wait until postgres is healthy
        redis:
          condition: service_started   ← just wait until started
      networks:
        - backend
      restart: unless-stopped
    
    postgres:
      image: postgres:15-alpine
      environment:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: password
        POSTGRES_DB: mydb
      volumes:
        - postgres-data:/var/lib/postgresql/data   ← named volume: data persists
        - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql  ← init script
      ports:
        - "5432:5432"   ← expose to host for DB GUI tools
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U postgres"]
        interval: 5s
        timeout: 5s
        retries: 5
        start_period: 10s
      networks:
        - backend
    
    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"
      volumes:
        - redis-data:/data
      command: redis-server --appendonly yes   ← override default CMD
      networks:
        - backend
    
    worker:
      build: .
      command: ["node", "dist/worker.js"]    ← override CMD from Dockerfile
      environment:
        DATABASE_URL: postgresql://postgres:password@postgres:5432/mydb
      depends_on:
        postgres:
          condition: service_healthy
      deploy:
        replicas: 2       ← run 2 worker containers
      networks:
        - backend
  
  volumes:             ← named volumes (persist across down/up)
    postgres-data:
    redis-data:
  
  networks:            ← custom network (default: bridge)
    backend:
      driver: bridge

COMPOSE FILE OVERRIDE (compose.override.yaml):

  # docker compose up automatically merges this with compose.yaml
  # Use for: dev-only settings (debug ports, volume mounts, relaxed auth)
  
  services:
    app:
      environment:
        DEBUG: "true"
        LOG_LEVEL: verbose
      volumes:
        - .:/app           ← dev: mount source for hot-reload
      command: ["npm", "run", "dev"]   ← override prod CMD with dev server
    
    postgres:
      ports:
        - "5432:5432"   ← expose in dev; not in prod compose

  # Production:
  docker compose -f compose.yaml -f compose.prod.yaml up
  # Merges: compose.yaml (base) + compose.prod.yaml (prod overrides)

COMMON COMMANDS:

  docker compose up              ← start all services (foreground)
  docker compose up -d           ← detached mode (background)
  docker compose up --build      ← rebuild images before starting
  docker compose up --force-recreate  ← recreate containers even if unchanged
  docker compose down            ← stop + remove containers + networks
  docker compose down -v         ← also remove volumes (wipe DB data)
  docker compose logs -f app     ← follow logs for 'app' service
  docker compose exec app bash   ← shell into running 'app' container
  docker compose run app npm test  ← run one-off command in new container
  docker compose ps              ← list containers in this project
  docker compose build           ← build/rebuild images
  docker compose pull            ← pull latest images
  docker compose restart app     ← restart specific service
  docker compose scale worker=3  ← scale worker to 3 replicas

NETWORKING: service discovery

  # All services in same Compose project are on the same network
  # Services can reach each other via service name (DNS resolution)
  
  # From 'app' container:
  psql -h postgres -U postgres mydb   ← 'postgres' resolves to postgres container IP
  redis-cli -h redis                  ← 'redis' resolves to redis container IP
  
  # NOT localhost! The app cannot reach postgres via localhost:5432
  # Each container has its own network namespace
```

---

### ❓ Why Does This Exist (Why Before What)

Without Compose, running a multi-container app requires: `docker network create`, individual `docker run` commands with correct `--network`, `--volume`, `-e`, `-p` flags, and manual ordering (start DB first). This is 10+ commands per environment setup, fragile, undocumented, and not reproducible. Compose encodes all of this as declarative YAML — one file, one command. The key insight is that the relationships between services (which service connects to which DB, which network they share, which volumes are mounted) are as important as the individual container configuration — Compose captures all of this in one place.

---

### 🧠 Mental Model / Analogy

> **Docker Compose is a stage director for a theatre production**: each container is an actor. Without Compose, you'd call each actor individually, give them separate costume instructions, tell them which stage to stand on, and manually coordinate their entrances. Compose is the stage director with a script (`compose.yaml`) that specifies every actor's costume, position, entrance order, and lines. `docker compose up` is "action" — everyone follows the script simultaneously. `docker compose down` is "that's a wrap" — everyone goes home.

---

### ⚙️ How It Works (Mechanism)

```
docker compose up execution:

  1. Read compose.yaml (+ compose.override.yaml if present)
  2. Create project network (default: <project-name>_default)
  3. Create named volumes (if not exists)
  4. Build images (if build: specified and --build flag or image not cached)
  5. Start services in dependency order:
     a. Services with no depends_on → start first (postgres, redis)
     b. Health check: wait until postgres healthcheck passes
     c. Services with depends_on: [postgres] → start after postgres healthy
  6. Attach to container logs (or detach with -d)

Project name: directory name by default; override with -p flag or COMPOSE_PROJECT_NAME
  → used for naming: <project>_<service>_1, <project>_<network>_default, <project>_<volume>
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to run multi-container app with single command
        │
        ▼
Docker Compose ◄── (you are here)
(compose.yaml defines service topology; docker compose up starts it all)
        │
        ├── Docker: Compose uses Docker to create/manage containers
        ├── Dockerfile: build: context → Compose builds images from Dockerfiles
        ├── Docker Image: each service references an image
        ├── Docker Layer: Compose pull/build respects layer cache
        └── Container: each service runs as a container
```

---

### 💻 Code Example

```yaml
# compose.yaml — Full-stack development environment
# Java Spring Boot + PostgreSQL + Redis + Kafka + Zookeeper

services:
  app:
    build:
      context: .
      target: dev
    ports:
      - "8080:8080"
      - "5005:5005"    # JVM remote debug port
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/appdb
      SPRING_DATASOURCE_USERNAME: appuser
      SPRING_DATASOURCE_PASSWORD: apppassword
      SPRING_KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SPRING_REDIS_HOST: redis
      JAVA_TOOL_OPTIONS: "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005"
    volumes:
      - ./target:/app/target    # hot-reload with Spring DevTools
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
    restart: on-failure

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppassword
      POSTGRES_DB: appdb
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 10
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass redispassword
    ports:
      - "6379:6379"

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5

volumes:
  postgres-data:
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `depends_on` waits until the service is READY | By default, `depends_on` only waits until the container STARTS (not until the process is ready). For databases, use `condition: service_healthy` with a `healthcheck:` to actually wait until ready. Without this, the app starts before PostgreSQL is accepting connections. |
| Docker Compose is for production | Compose is for single-host local dev and testing. It has no auto-restart for failed nodes, no cross-host networking, no zero-downtime deployments, no autoscaling. Use Kubernetes for production. Docker Swarm (built on Compose file format) handles multi-host but is largely deprecated in favor of Kubernetes. |
| Stopping Compose removes data | `docker compose down` removes containers and networks but NOT named volumes. `docker compose down -v` is required to also remove volumes. This is intentional: you don't lose your database data when restarting the stack. |

---

### 🔥 Pitfalls in Production

```
PITFALL: .env file with real secrets committed to git

  # .env (auto-loaded by docker compose):
  POSTGRES_PASSWORD=mypassword123    ← if committed to git → secret exposure
  
  # FIX:
  echo ".env" >> .gitignore          ← never commit .env
  cp .env.example .env               ← developers copy and fill in their own values
  # .env.example: shows required variables, empty values or fake examples
  POSTGRES_PASSWORD=                 ← empty; developer fills in locally

PITFALL: bind mount overwrites container's installed dependencies

  services:
    app:
      volumes:
        - .:/app    ← bind mounts entire project, including host's (empty) node_modules
        # host node_modules overwrites container's node_modules → app breaks
  
  # FIX: anonymous volume for node_modules takes precedence over bind mount
      volumes:
        - .:/app
        - /app/node_modules   ← anonymous volume: persists container's node_modules
                               ← Docker mounts this AFTER bind mount; container version wins
```

---

### 🔗 Related Keywords

- `Docker` — Compose uses Docker to create and manage containers
- `Dockerfile` — Compose's `build:` directive builds images from Dockerfiles
- `Docker Image` — each Compose service references an image
- `Container` — each Compose service runs as a container
- `Kubernetes` — production alternative for multi-host orchestration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ docker compose up -d        # start all services         │
│ docker compose down -v      # stop + remove volumes      │
│ docker compose logs -f app  # follow service logs        │
│ docker compose exec app sh  # shell into container       │
│ docker compose run app test # one-off command            │
├──────────────────────────────────────────────────────────┤
│ KEY CONCEPTS:                                            │
│ • depends_on + healthcheck: wait until DB ready         │
│ • named volumes: data persists across down/up           │
│ • service name = hostname (app reaches postgres:5432)   │
│ • compose.override.yaml: auto-merged dev overrides      │
│ • NOT for production: use Kubernetes                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Docker Compose is not for production, yet many startups use it in production (on a single server) because it's simpler than Kubernetes. What are the specific failure scenarios that Compose doesn't handle but Kubernetes does? Consider: node failure, service crash recovery, zero-downtime deployments, resource limits, secret management. At what scale/reliability requirement does the Compose → Kubernetes migration become necessary?

**Q2.** In a CI/CD pipeline (GitHub Actions, GitLab CI), Docker Compose is commonly used to spin up integration test dependencies (PostgreSQL, Redis). A test suite requires a fresh database with specific schema on every run, but `docker compose up` reuses named volumes from previous runs. Design a CI strategy that: (a) starts services fast (uses layer caching), (b) guarantees a clean database state per CI run, (c) cleans up resources after the run, (d) runs multiple CI jobs in parallel without port conflicts.
