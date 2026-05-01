---
layout: default
title: "Twelve-Factor App"
parent: "Microservices"
nav_order: 677
permalink: /microservices/twelve-factor-app/
number: "677"
category: Microservices
difficulty: ★★☆
depends_on: "Microservices Architecture, CI-CD Pipeline"
used_by: "Feature Flags, Cloud-Native"
tags: #intermediate, #microservices, #devops, #cloud, #architecture
---

# 677 — Twelve-Factor App

`#intermediate` `#microservices` `#devops` `#cloud` `#architecture`

⚡ TL;DR — The **Twelve-Factor App** is a methodology for building SaaS/microservice applications that are cloud-native, easily scalable, and deployable anywhere. Its 12 factors cover: codebase management, dependency isolation, config externalisation, backing services, build/release/run separation, stateless processes, port binding, concurrency, disposability, dev/prod parity, log streaming, and admin processes.

| #677            | Category: Microservices                    | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | Microservices Architecture, CI-CD Pipeline |                 |
| **Used by:**    | Feature Flags, Cloud-Native                |                 |

---

### 📘 Textbook Definition

The **Twelve-Factor App** methodology, published by Adam Wiggins (Heroku, 2011), defines 12 principles for building modern, cloud-deployable software-as-a-service applications. The methodology emerged from observation of patterns in hundreds of apps deployed on Heroku's PaaS. The twelve factors are: **I. Codebase** (one codebase tracked in version control, many deploys); **II. Dependencies** (explicitly declare and isolate dependencies); **III. Config** (store config in environment, not code); **IV. Backing Services** (treat backing services as attached resources); **V. Build, Release, Run** (strictly separate build and run stages); **VI. Processes** (execute app as one or more stateless processes); **VII. Port Binding** (export services via port binding); **VIII. Concurrency** (scale out via the process model); **IX. Disposability** (maximize robustness with fast startup and graceful shutdown); **X. Dev/Prod Parity** (keep development, staging, and production as similar as possible); **XI. Logs** (treat logs as event streams); **XII. Admin Processes** (run admin/management tasks as one-off processes). While some factors are now table stakes in Kubernetes environments, the methodology remains foundational for understanding cloud-native architecture constraints.

---

### 🟢 Simple Definition (Easy)

The Twelve-Factor App is a checklist for building microservices that can run anywhere (cloud, laptop, production) without modification. The key rules: store all config in environment variables (not in code), be stateless (don't save data locally between requests), treat logs as streams (don't write to files), and start/stop quickly. Follow these 12 rules and your app will be deployable, scalable, and operable in any cloud environment.

---

### 🔵 Simple Definition (Elaborated)

12-factor app rules in practice: Your service reads database URL from `DB_URL` env var (Factor III — config in env), not hardcoded in application.properties. Your service has no local state — all state in Redis or DB (Factor VI — stateless processes). Your service writes logs to stdout, not to `/var/log/myapp.log` (Factor XI — logs as event streams). Your service starts in under 5 seconds (Factor IX — disposability). These constraints make it deployable on Kubernetes: Kubernetes injects env vars, can kill/restart pods (stateless = safe to kill), and collects stdout logs automatically.

---

### 🔩 First Principles Explanation

**All 12 factors with practical application:**

```
FACTOR I — CODEBASE
  "One codebase tracked in revision control, many deploys"

  ✅ Correct: One Git repo → deployable to dev/staging/prod
  ❌ Wrong: Separate repos for dev vs prod (code diverges)
  ❌ Wrong: One repo with multiple apps (should be separate repos per service)

  In practice (Spring Boot):
    Single repository per microservice.
    CI/CD pipeline builds one artifact from main branch.
    Same Docker image deployed to: dev → staging → production.
    Only environment variables differ between deploys (Factor III).

FACTOR II — DEPENDENCIES
  "Explicitly declare and isolate all dependencies"

  ✅ Correct: All dependencies in pom.xml/build.gradle (Maven/Gradle)
  ❌ Wrong: System-installed tools assumed present ("assume curl is installed")
  ❌ Wrong: Implicit transitive dependency version assumptions

  In practice (Java):
    Maven/Gradle: all dependencies declared with exact versions
    Docker: all runtime deps in Dockerfile (no "apt install" at runtime)
    No "this library needs libssl.so to be present on the server"
    Docker image is self-contained: all deps baked in

FACTOR III — CONFIG
  "Store config in the environment"
  "Config: everything that varies between deploys (dev, staging, prod)"

  ✅ Correct: DB_URL, REDIS_URL, API_KEY as environment variables
  ❌ Wrong: application-prod.properties committed to repo (secrets in code)
  ❌ Wrong: Feature flags hardcoded in Java enums

  In practice (Spring Boot):
    # application.yml:
    spring:
      datasource:
        url: ${DB_URL}              # from environment variable
        username: ${DB_USER}
        password: ${DB_PASS}        # from Kubernetes Secret

    # Kubernetes Secret → mounted as env vars:
    env:
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: order-service-db-secret
          key: password

    TEST: Could you open-source your codebase right now without exposing credentials?
    If yes → your config is properly externalised. If no → credentials are in code.

FACTOR IV — BACKING SERVICES
  "Treat backing services as attached resources"
  "No distinction between local and third-party services"

  ✅ Correct: DB accessed via URL → same code works for local Postgres and RDS
  ❌ Wrong: Special code path for "if we're in production, use RDS; else use H2"

  In practice:
    Local dev: Docker Compose provides PostgreSQL at localhost:5432
    Production: AWS RDS at rds.amazonaws.com:5432
    Service code: identical. Only DB_URL env var changes.
    "Attach" a different backing service by changing an env var (no code change)

    # docker-compose.yml (local dev):
    services:
      postgres:
        image: postgres:16
        environment:
          POSTGRES_DB: orders
          POSTGRES_USER: app
          POSTGRES_PASSWORD: localdev
      order-service:
        image: order-service:latest
        environment:
          DB_URL: jdbc:postgresql://postgres:5432/orders  ← same code, different URL

    # Production K8s:
    env:
    - name: DB_URL
      value: jdbc:postgresql://orders.abcd1234.us-east-1.rds.amazonaws.com:5432/orders

FACTOR V — BUILD, RELEASE, RUN
  "Strictly separate build and run stages"

  BUILD stage: code + dependencies → executable artifact (Docker image)
  RELEASE stage: artifact + config → deployable unit (image + Kubernetes manifest)
  RUN stage: execute the release (pod running in cluster)

  ✅ Correct: Build produces immutable Docker image tagged with SHA
  ❌ Wrong: Running app downloads config files or patches itself at startup
  ❌ Wrong: Same image tagged "latest" overwritten on each build (mutable)

  In practice:
    # Immutable image tagging:
    docker build -t order-service:git-sha-abc1234 .
    docker push order-service:git-sha-abc1234
    # NEVER push to :latest (immutable by git SHA)
    # Rollback: redeploy the previous tagged image (no rebuild needed)

FACTOR VI — PROCESSES
  "Execute the app as one or more stateless, share-nothing processes"

  ✅ Correct: Session state in Redis, not in JVM heap
  ❌ Wrong: User session stored in memory (sticky sessions required)
  ❌ Wrong: File uploads stored to local filesystem /tmp/uploads

  In practice (Spring Boot):
    # Replace in-memory sessions with Redis sessions:
    spring.session.store-type=redis
    spring.data.redis.url=${REDIS_URL}

    # File uploads: stream directly to S3, not local disk
    @PostMapping("/uploads")
    void handleUpload(MultipartFile file) {
        s3Client.putObject(PutObjectRequest.builder()
            .bucket(bucket)
            .key("uploads/" + UUID.randomUUID() + "/" + file.getOriginalFilename())
            .build(), RequestBody.fromInputStream(file.getInputStream(), file.getSize()));
        // Never: file.transferTo(new File("/tmp/" + file.getOriginalFilename()))
        // /tmp is local to this pod — other pods can't access it
    }

FACTOR VII — PORT BINDING
  "Export services via port binding"

  ✅ Correct: Spring Boot embeds Tomcat, binds to port from SERVER_PORT env var
  ❌ Wrong: App deployed into an external Tomcat/JBoss container

  In practice:
    Spring Boot: embedded Tomcat → service is self-contained
    server.port=${SERVER_PORT:8080}
    Service receives requests on this port → no external web server needed
    Kubernetes Service: routes to pod on this port

FACTOR VIII — CONCURRENCY
  "Scale out via the process model"

  ✅ Correct: Scale horizontally by adding replicas (Kubernetes: replicas: 10)
  ❌ Wrong: Scale by adding threads to a single large JVM

  In practice:
    Horizontal pod autoscaler based on CPU/memory:
    kubectl autoscale deployment order-service --min=2 --max=20 --cpu-percent=70
    Each pod is a process. More load → more pods.
    Each pod handles concurrency internally with thread pool (Factor VIII = process model)

FACTOR IX — DISPOSABILITY
  "Maximize robustness with fast startup and graceful shutdown"

  ✅ Correct: Service starts in <10 seconds, shuts down gracefully (see #672)
  ❌ Wrong: 3-minute startup time (makes rolling updates slow, crashes expensive)

  In practice:
    Spring Boot: use lazy bean initialization to reduce startup time:
    spring.main.lazy-initialization=true

    GraalVM native image: startup in milliseconds (extreme case)

    Graceful shutdown: server.shutdown=graceful (Spring Boot)

FACTOR X — DEV/PROD PARITY
  "Keep development, staging, and production as similar as possible"

  ✅ Correct: Local dev uses Docker Compose with same images as production
  ❌ Wrong: "I use H2 locally but production uses PostgreSQL"
             (H2 SQL dialect differs → bugs only in production)
  ❌ Wrong: Dev skips authentication; prod has OAuth2

  In practice:
    Docker Compose for local: same PostgreSQL version as production (both 16.x)
    Same Redis version. Same Kafka version.
    LocalStack for AWS services (S3, SQS) locally.
    Testcontainers in tests: same real DB image as production.

    # Danger: H2 auto-creates columns; PostgreSQL requires explicit schema
    # H2 is case-insensitive by default; PostgreSQL is case-sensitive
    # Bugs found only in prod = dev/prod parity violated

FACTOR XI — LOGS
  "Treat logs as event streams"
  "App should not concern itself with routing or storage of its output stream"

  ✅ Correct: Log to stdout/stderr → collected by Fluentd/Logstash → Elasticsearch
  ❌ Wrong: log4j writes to /var/log/myapp/app.log (pod restarts → logs lost)
  ❌ Wrong: app compresses and rotates log files (infrastructure concern)

  In practice (Spring Boot / Logback):
    # logback-spring.xml:
    <configuration>
      <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
          <!-- JSON structured logs → easier for Elasticsearch ingestion -->
        </encoder>
      </appender>
      <root level="INFO">
        <appender-ref ref="STDOUT"/>
      </root>
    </configuration>
    # Kubernetes: collects stdout from each pod → routes to logging platform
    # Pod restarts: Fluentd buffers → no log loss

FACTOR XII — ADMIN PROCESSES
  "Run admin/management tasks as one-off processes"

  ✅ Correct: Database migration runs as a Kubernetes Job before deployment
  ✅ Correct: Data cleanup script runs as: kubectl run --image=order-service bash migration.sh
  ❌ Wrong: Admin endpoint in the running service that triggers DB migration via HTTP
  ❌ Wrong: SSH into production server and run migration manually

  In practice:
    Liquibase/Flyway migration as Kubernetes init container:
    initContainers:
    - name: db-migrate
      image: order-service:git-sha-abc1234
      command: ["java", "-jar", "app.jar", "--spring.profiles.active=migrate-only"]
      # Runs migration, exits 0 → main container starts
      # Same image = same Liquibase version as production code
```

---

### ❓ Why Does This Exist (Why Before What)

Before cloud/PaaS, applications were deployed onto fixed servers with specific configurations. Environment assumptions were baked into the application. Moving to cloud required a different philosophy: the application must be environment-agnostic, treating each deployment as a fresh process that receives its configuration externally. The 12 factors are the distilled lessons from what makes applications work well in this model.

---

### 🧠 Mental Model / Analogy

> The Twelve-Factor App is like the building code for cloud-native applications. Just as a building code specifies: "all wiring must be accessible in the walls," "all plumbing must route to the main sewer line," and "all electrical must go through the main panel" — the 12 factors specify constraints that make buildings (services) safe to operate, easy to maintain, and compatible with the shared infrastructure (cloud platform). A building that violates code may work fine... until the inspector (production incident) reveals the hidden problems.

---

### ⚙️ How It Works (Mechanism)

**Factor III violation: secrets in code — the most critical violation:**

```java
// VIOLATION — config in code:
@Configuration
class DatabaseConfig {
    @Bean DataSource dataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:postgresql://prod.rds.amazonaws.com:5432/orders")
            .username("app_user")
            .password("s3cur3P@ssword!")  // ← SECRET IN CODE
            .build();
    }
}
// Problem: git commit contains credentials
//          All developers have production DB password
//          Cannot change password without code change + deployment
//          Open-sourcing this code = credential leak

// CORRECT — Factor III:
@Configuration
class DatabaseConfig {
    @Bean DataSource dataSource(
            @Value("${DB_URL}") String url,
            @Value("${DB_USER}") String username,
            @Value("${DB_PASS}") String password) {
        return DataSourceBuilder.create()
            .url(url).username(username).password(password).build();
    }
}
// Credentials: Kubernetes Secret → injected as env vars at pod startup
// Rotate credentials: change Kubernetes Secret + restart pods (no code change)
```

---

### 🔄 How It Connects (Mini-Map)

```
Microservices Architecture     CI-CD Pipeline
(application architecture)     (build → release → run — Factor V)
        │                              │
        └──────────┬───────────────────┘
                   ▼
        Twelve-Factor App  ◄──── (you are here)
        (methodology for cloud-native services)
                   │
        ┌──────────┴──────────────┐
        ▼                         ▼
Feature Flags                Cloud-Native
(Factor III: config in env)  (Kubernetes satisfies many factors)
```

---

### 💻 Code Example

**Testcontainers: Factor X (Dev/Prod Parity) in tests:**

```java
// Use real PostgreSQL in tests (not H2) → dev/prod parity:
@SpringBootTest
@Testcontainers
class OrderRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("orders_test")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired OrderRepository orderRepository;

    @Test
    void shouldSaveAndRetrieveOrder() {
        // This test runs against REAL PostgreSQL (not H2)
        // → Same SQL dialect as production
        // → UUID types, JSONB types, etc. work correctly
        // → Dev/Prod Parity: test environment matches production environment
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                  |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The 12 factors are only for PaaS (Heroku)                | The factors apply to any cloud deployment: Kubernetes, ECS, Cloud Run, or raw VMs. Kubernetes actually enforces many factors: stateless pods (Factor VI), env var config (Factor III), stdout logging (Factor XI), and disposability (Factor IX)         |
| Factor VI (stateless) means services can't use databases | Stateless means no in-process state between requests (no in-memory session, no local files). Databases, Redis, and other backing services are explicitly allowed — they are the state store (Factor IV: backing services)                                |
| Following all 12 factors is always mandatory             | The factors are guidelines for specific problems (scalability, portability, operability). For a simple internal tool with one deployment, some factors (e.g., strict build/release/run separation) may add overhead without benefit. Apply pragmatically |
| Factor III means all config must be env vars             | Factor III says "store config in the environment." In Kubernetes, this includes: env vars, ConfigMaps, and Secrets mounted as files. The principle: config must not be in committed code, not that env vars are the only mechanism                       |

---

### 🔥 Pitfalls in Production

**Factor X violation: H2 in dev, PostgreSQL in prod:**

```
SCENARIO:
  Developer uses H2 (in-memory) for local development (Factor X violation).
  Integration tests: also H2.

  New feature: query using PostgreSQL-specific syntax:
    // Hibernate-generated query uses:
    SELECT * FROM orders WHERE data::jsonb @> '{"status": "PENDING"}'::jsonb
    -- PostgreSQL JSONB operator: @>
    -- H2: "Syntax error"... but developer used native query not executed locally

  Deploy to staging (PostgreSQL): feature works.
  Deploy to production: works.

  Another developer adds H2 test:
    @Test void shouldFilterPendingOrders() → passes on H2 (H2 uses LIKE fallback)

  The test passes but doesn't test what production runs.
  A later refactor: the PostgreSQL JSONB query changes → H2 test still passes
  → Production query breaks silently.

FIX:
  Replace H2 with Testcontainers (real PostgreSQL) in all tests.
  Docker Compose for local dev with real PostgreSQL 16.

  # docker-compose.yml:
  services:
    postgres:
      image: postgres:16  ← SAME VERSION as production

  Benefit: local tests catch PostgreSQL-specific syntax errors immediately.
  Cost: tests slower (Testcontainers startup ~3-5s first run, cached after).
```

---

### 🔗 Related Keywords

- `Microservices Architecture` — twelve-factor principles guide microservice design
- `CI-CD Pipeline` — implements Factors V (build/release/run) and I (codebase)
- `Feature Flags` — implements Factor III (config in environment)
- `Cloud-Native` — Kubernetes/containers naturally enforce many twelve-factor rules

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ I    Codebase      │ One repo, many deploys              │
│ II   Dependencies  │ Declare and isolate explicitly      │
│ III  Config        │ Store in environment (not code)     │
│ IV   Backing Svcs  │ Treat as attached resources         │
│ V    Build/Run     │ Strictly separate stages            │
│ VI   Processes     │ Stateless, share-nothing            │
│ VII  Port Binding  │ Self-contained, bind a port         │
│ VIII Concurrency   │ Scale out via processes             │
│ IX   Disposability │ Fast start + graceful shutdown      │
│ X    Dev/Prod Par  │ Same stack everywhere               │
│ XI   Logs          │ Stream to stdout (not files)        │
│ XII  Admin Procs   │ One-off processes (K8s Jobs)        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're reviewing a Spring Boot service. You find: (a) `application-prod.properties` is committed to the Git repo containing the RDS connection string (but not the password — the password is an env var); (b) the service writes temporary files to `/tmp/session-{userId}` during request processing and reads them back later in the same request; (c) logs are written to `/var/log/order-service/app.log` and rotated daily; (d) the Docker image is tagged as `order-service:latest`. For each finding: which twelve-factor principle does it violate, what is the specific risk, and how would you fix it?

**Q2.** Factor VIII (concurrency via process model) suggests scaling out horizontally by adding processes (pods) rather than scaling up (larger JVM heap, more threads). But Java applications are often sized with specific heap configurations (-Xmx). How do you reconcile the process model with JVM memory management? For a service that processes large batch jobs in memory, what does Factor VI (stateless processes) imply about where intermediate processing state should be stored, and what backing service would you use?
