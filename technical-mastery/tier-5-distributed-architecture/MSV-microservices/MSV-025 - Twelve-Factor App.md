---
id: MSV-025
title: Twelve-Factor App
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-002, MSV-003
used_by: MSV-085
related: MSV-003, MSV-002, MSV-085, MSV-068, MSV-080
tags:
  - microservices
  - architecture
  - intermediate
  - best-practices
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/microservices/twelve-factor-app/
---

⚡ TL;DR - The Twelve-Factor App is a methodology for
building cloud-native, scalable applications across 12
principles. Originally from Heroku (2012), it became
the blueprint for microservice design: stateless,
environment-configured, and independently deployable.
Five factors matter most in practice: config, stateless,
dependencies, processes, and logs.

| #025 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Microservices Architecture, Stateless Services | |
| **Used by:** | Monolith to Microservices Migration | |
| **Related:** | Stateless Services, Microservices Architecture, Monolith to Microservices Migration, Zero-Downtime Deployment, Conway's Law in Microservices | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (2011 context):**
Applications deployed to fixed servers. Configuration
hardcoded in source code or deployment scripts tied to
specific machines. "Works on my machine" syndrome.
Deploying a new version requires SSH to each server,
running scripts, praying. Scaling requires adding new
servers and manually configuring each one identically.
Logs scattered across server filesystems. No standard
way to run the app locally, in staging, or in production.

**THE INVENTION MOMENT:**
Adam Wiggins at Heroku published Twelve-Factor App (2012)
as a distillation of patterns observed across thousands
of apps on the Heroku platform. The 12 factors describe
how to build apps that: (1) scale horizontally, (2) are
deployable to any cloud, (3) have clean contracts
between app and OS/platform, (4) minimise divergence
between development and production.

The factors became the implicit design contract for
microservices: every microservice should be a
Twelve-Factor App.

---

### 📘 Textbook Definition

**Twelve-Factor App** is a methodology for building
cloud-native software-as-a-service applications that:
are portable across execution environments, deployable
on modern cloud platforms, scalable horizontally without
architectural changes, and manageable without system
administration. The 12 factors are: (1) Codebase,
(2) Dependencies, (3) Config, (4) Backing Services,
(5) Build/Release/Run, (6) Processes, (7) Port Binding,
(8) Concurrency, (9) Disposability, (10) Dev/Prod Parity,
(11) Logs, (12) Admin Processes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Twelve-Factor App is a checklist of 12 design principles
that make a service portable, scalable, cloud-native,
and easy to operate - the blueprint for a well-designed
microservice.

**One analogy:**
> A Twelve-Factor App is like a Lego set: standard
> connectors (port binding, config via env), stateless
> (can be added or removed without affecting others),
> identical blocks (dev/prod parity), disposable (add
> or remove any block without side effects). Any child
> can assemble Lego without knowing how the specific
> block was manufactured (platform independence).

**One insight:**
The 12 factors are not all equally important in practice.
The critical ones that are commonly violated: Factor 3
(Config in environment, not code), Factor 6 (Stateless
processes), Factor 11 (Logs as event streams, not files).
These three, if violated, cause the most operational
problems in microservices deployments.

---

### 🔩 First Principles Explanation

**THE 12 FACTORS WITH MICROSERVICES RELEVANCE:**

```
FACTOR 1 - CODEBASE:
  One codebase per service, tracked in version control
  Multiple deploys (staging, prod) from same codebase
  MSV relevance: each microservice = one Git repo
                 (or monorepo with independent deploy)

FACTOR 2 - DEPENDENCIES:
  Explicitly declare and isolate dependencies
  (Maven pom.xml, package.json, requirements.txt)
  Never rely on system-wide packages
  MSV relevance: Docker = the ultimate dependency
                 isolation (all deps in image)

FACTOR 3 - CONFIG (**critical):
  Store config in environment variables
  NOT hardcoded in code, NOT config files in repo
  What varies between deploys: URLs, API keys, ports
  MSV relevance: Kubernetes ConfigMaps + Secrets
                 Spring Boot: @Value("${ENV_VAR}")

FACTOR 4 - BACKING SERVICES:
  Treat databases, queues, etc as attached resources
  Access via URL + credentials from config (Factor 3)
  Swap backing service without code change
  MSV relevance: same app image connects to dev DB
                 and prod DB via different env vars

FACTOR 5 - BUILD/RELEASE/RUN:
  Strict separation of build, release, and run stages
  Build: artifact (Docker image)
  Release: artifact + config
  Run: execute release
  MSV relevance: CI builds image; CD deploys it

FACTOR 6 - PROCESSES (**critical):
  Execute app as stateless, share-nothing processes
  Sticky sessions and in-process cache are violations
  Persistent state in backing service (DB, Redis)
  MSV relevance: stateless enables horizontal scaling
                 and any-instance routing

FACTOR 7 - PORT BINDING:
  App exports HTTP as service via port binding
  Self-contained (embedded Tomcat, not deployed to app
    server)
  MSV relevance: Spring Boot embeds Tomcat
                 Container listens on configured port

FACTOR 8 - CONCURRENCY:
  Scale out via process model (horizontal scaling)
  Not by vertical scaling or threading models
  MSV relevance: add pod replicas, not bigger pods

FACTOR 9 - DISPOSABILITY (**important):
  Fast startup and graceful shutdown
  Startup: seconds (not minutes)
  Shutdown: drain in-flight requests, release resources
  MSV relevance: K8s kills and creates pods frequently
                 JVM startup optimisation matters

FACTOR 10 - DEV/PROD PARITY:
  Keep development, staging, production similar
  Time gap: hours (CD), personnel gap: devs deploy,
  tools gap: same DB in dev and prod
  MSV relevance: "use H2 in dev, PostgreSQL in prod"
                 = false dev/prod parity. Use Docker
                 Compose for local PostgreSQL.

FACTOR 11 - LOGS (**critical):
  Treat logs as event streams
  App writes to stdout, not to files
  Execution environment routes logs to storage/aggregation
  MSV relevance: container logs to stdout -> K8s collects
                 -> Fluentd -> Elasticsearch

FACTOR 12 - ADMIN PROCESSES:
  Run admin/management tasks as one-off processes
  Same release (code + config) as app processes
  Database migrations, scripts in same container
  MSV relevance: Flyway/Liquibase migrations run at
                 startup or as K8s Job
```

---

### 🧪 Thought Experiment

**VIOLATIONS AND THEIR CONSEQUENCES:**

```
VIOLATION: Factor 3 - Config in code
  DB_URL = "jdbc:postgresql://prod-db:5432/orders"
  (hardcoded in application.properties)
  
  Consequence:
    1. Can't deploy same artifact to staging
       (staging DB URL is different)
    2. Dev accidentally connects to prod DB
    3. Security: prod credentials in Git history
  
  Fix:
    spring.datasource.url=${DB_URL}
    # DB_URL provided as K8s Secret

VIOLATION: Factor 6 - In-process session state
  HttpSession stored in JVM memory
  User A's session on Pod 1
  Load balancer routes User A's next request to Pod 2
  Pod 2: session not found -> User A logged out
  
  Consequence:
    Requires sticky sessions (constraint on LB)
    Pod restart = all sessions lost
    Can't scale without sticky session complexity
  
  Fix:
    Externalise session to Redis (Spring Session)
    Any pod can serve any user

VIOLATION: Factor 11 - Logs to file
  log4j: appender -> /var/log/service.log
  
  Consequence:
    Container filesystem logs lost when pod restarts
    Log rotation required (ops overhead)
    Log aggregation requires file-based agent (Filebeat)
    vs simpler stdout-based log routing
  
  Fix:
    logging.file.name: (remove)
    Logback: ConsoleAppender -> stdout
    K8s: kubectl logs pod-name works automatically
```

---

### 🧠 Mental Model / Analogy

> The Twelve-Factor App is the microservice equivalent
> of the "clean code" principles for deployment. Just
> as clean code principles (single responsibility,
> no magic numbers, etc.) make code maintainable,
> Twelve-Factor principles make services deployable,
> scalable, and operable. A service that violates
> Factor 3 (config in code) is like a function that
> uses magic numbers - it works, but it breaks the
> moment you need to change the context.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The Twelve-Factor App is a list of 12 best practices
for building apps that work well in the cloud. They
teach things like "don't hardcode your database password"
and "write logs to the screen, not a file".

**Level 2 - How to use it (junior developer):**
Check your service against each factor. Factor 3:
search for hardcoded URLs or credentials in code.
Factor 6: check for in-memory session storage.
Factor 11: check if logging is configured for stdout.
Factor 9: measure startup time and verify graceful
shutdown is configured.

**Level 3 - How it works (mid-level engineer):**
The most impactful factors for Spring Boot microservices:
(3) Use `${ENV_VAR}` in application.yml. Kubernetes
provides ConfigMaps (non-secret config) and Secrets
(sensitive config) as environment variables or mounted
files. (6) Use Spring Session + Redis for session
externalisation. Remove local disk caches. (9) Configure
`server.shutdown=graceful` and `spring.lifecycle
.timeout-per-shutdown-phase=30s`. Minimise startup
time: avoid eager initialisation, use Spring Boot lazy
loading. (11) Remove file appenders; use ConsoleAppender.

**Level 4 - Why it was designed this way (senior/staff):**
The Twelve Factors emerged from Heroku's dyno model:
stateless processes that could be started, stopped,
and moved between physical hosts at will. The factors
are design for ephemerality: a process can be killed
at any time and a new one started from the same image
without data loss or user impact. Kubernetes adopted
the same model: pods are ephemeral. The factors are
not abstract principles; they are concrete requirements
for running on Kubernetes or any cloud-native platform.

**Level 5 - Mastery (distinguished engineer):**
Beyond the original 12, the "Beyond the Twelve-Factor
App" extension (Kevin Hoffman, 2016) adds:
(13) API-first, (14) Telemetry (observability built-in),
(15) Authentication and Authorisation (security first-class).
For microservices at scale: Factor 13 is critical -
API contract defined before implementation (Contract-First
API Design). Factor 14 maps to the OpenTelemetry
standard (metrics, logs, traces from day one). The
twelve factors are necessary but not sufficient for
production-grade microservices.

---

### ⚙️ How It Works (Mechanism)

**FACTOR 3 - CONFIG IN KUBERNETES:**

```yaml
# ConfigMap: non-sensitive config
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
data:
  DATABASE_HOST: postgres.db.svc.cluster.local
  DATABASE_PORT: "5432"
  KAFKA_BOOTSTRAP_SERVERS:
    kafka.kafka.svc.cluster.local:9092

---
# Secret: sensitive config
apiVersion: v1
kind: Secret
metadata:
  name: order-service-secrets
type: Opaque
data:
  # Base64-encoded values
  DATABASE_PASSWORD: cGFzc3dvcmQxMjM=
  API_KEY: c2VjcmV0a2V5

---
# Deployment: inject as env vars
containers:
  - name: order-service
    image: order-service:v1.1
    env:
      - name: DATABASE_HOST
        valueFrom:
          configMapKeyRef:
            name: order-service-config
            key: DATABASE_HOST
      - name: DATABASE_PASSWORD
        valueFrom:
          secretKeyRef:
            name: order-service-secrets
            key: DATABASE_PASSWORD
```

```yaml
# Spring Boot application.yml (Factor 3 compliant)
spring:
  datasource:
    url: jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT}/orders
    password: ${DATABASE_PASSWORD}
  kafka:
    bootstrap-servers: ${KAFKA_BOOTSTRAP_SERVERS}
server:
  shutdown: graceful  # Factor 9
logging:
  # Factor 11: no file appender - stdout only
  pattern:
    console: "%d [%X{correlationId}] %-5p %c - %m%n"
```

---

### 🔄 The Complete Picture - End-to-End Flow

**12-FACTOR MICROSERVICE CHECKLIST:**

```
DEVELOPMENT:
  ✓ Factor 1: One Git repo per service
  ✓ Factor 2: pom.xml / build.gradle declares all deps
  ✓ Factor 10: Docker Compose local = same stack as prod
     (PostgreSQL, Kafka, Redis - not H2/in-memory)

BUILD / CI:
  ✓ Factor 5: CI builds Docker image (immutable artifact)
  ✓ Factor 4: DB URL injected at runtime, not baked in

DEPLOYMENT / K8s:
  ✓ Factor 3: ConfigMap + Secret -> env vars
  ✓ Factor 7: Container exposes port ${SERVER_PORT}
  ✓ Factor 8: HPA scales pods horizontally
  ✓ Factor 9: server.shutdown=graceful,
               startup < 10s (avoid long init)

RUNTIME:
  ✓ Factor 6: No in-process session, no local disk cache
              Spring Session -> Redis for sessions
  ✓ Factor 11: Log to stdout -> K8s log routing
              -> Fluentd -> Elasticsearch
  ✓ Factor 12: DB migrations via Flyway K8s Job
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Factor 3 violation**

```java
// BAD: Factor 3 violation - config in code
@Repository
public class OrderRepository {
    // Hardcoded prod URL in source code
    // Cannot deploy same artifact to staging
    // Credentials in Git history (security issue)
    private static final String DB_URL =
        "jdbc:postgresql://prod-db.internal:5432/orders";
    private static final String DB_PASS = "pr0d_p@ssword";
}
```

```java
// GOOD: Factor 3 - config via environment
// application.yml:
// spring.datasource.url: ${DB_URL}
// spring.datasource.password: ${DB_PASSWORD}

// K8s: DB_URL from ConfigMap, DB_PASSWORD from Secret
// Dev: .env file (gitignored) with local values
// Same artifact (Docker image) runs in all environments
// Credentials never in source code or Git history
```

**Example 2 - Factor 11: logs as event streams**

```xml
<!-- BAD: Factor 11 violation - log to file -->
<!-- logback.xml -->
<appender name="FILE"
    class="ch.qos.logback.core.FileAppender">
    <file>/var/log/service/order-service.log</file>
</appender>
<!-- Pod restart = logs lost; rotation needed;
     kubectl logs doesn't work -->
```

```xml
<!-- GOOD: Factor 11 - stdout only -->
<!-- logback-spring.xml -->
<appender name="CONSOLE"
    class="ch.qos.logback.core.ConsoleAppender">
    <encoder>
        <pattern>%d{ISO8601} %-5level
          [%X{correlationId}] %logger - %msg%n</pattern>
    </encoder>
</appender>
<!-- kubectl logs pod-name works immediately -->
<!-- K8s routes stdout to log aggregation pipeline -->
<!-- No rotation, no disk management needed -->
```

---

### ⚖️ Comparison Table

| Factor | Common Violation | Consequence |
|---|---|---|
| **3 - Config** | Hardcoded credentials | Security breach, can't multi-env deploy |
| **6 - Stateless** | In-memory sessions | Can't horizontally scale, pod restart = session loss |
| **9 - Disposability** | 5-minute startup | K8s rolling deploy takes forever; pod death = outage |
| **10 - Dev/Prod Parity** | H2 in dev, PostgreSQL in prod | Prod bugs not caught in dev (different SQL behaviour) |
| **11 - Logs** | Log to file | Logs lost on pod restart, kubectl logs broken |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Twelve-Factor is only for Heroku/PaaS | The factors are a general blueprint for cloud-native applications, validated by 10+ years of Kubernetes adoption. Every cloud-native microservice should satisfy these factors. |
| Factor 9 (Disposability) just means fast startup | Disposability = fast startup AND graceful shutdown AND crash resilience. A service that starts in 2 seconds but holds connections open for 5 minutes during shutdown violates Factor 9. Both directions matter. |
| The 12 factors are enough for production microservices | The original 12 factors (2012) are necessary but insufficient. Modern production microservices require: structured logging, distributed tracing, health endpoints, circuit breaking, and API versioning - none of which are in the original 12 factors. |

---

### 🚨 Failure Modes & Diagnosis

**Factor 6 violation: in-process session state**

**Symptom:**
Users report being logged out randomly. Support sees:
"worked fine, then I had to log in again". Correlated
with pod restarts or scaling events.

**Root Cause:**
HTTP sessions stored in JVM memory (HttpSession). When
the pod serving a user is killed (K8s rolling deploy,
scaling down, OOMKill), all sessions on that pod are
lost. The load balancer routes the user to a different
pod: session not found -> user sees login page.

**Diagnostic:**
```bash
# Check if sessions are in-memory
grep -r "HttpSession\|SessionRegistry" src/
# If found without Spring Session: in-memory sessions

# Check if sticky sessions are configured (workaround)
kubectl get ingress -o yaml | grep affinity
# If sessionAffinity=ClientIP: workaround in place
# Fix required: externalise session to Redis

# Verify Spring Session is configured
grep -r "spring.session" src/ k8s/
# Should find: spring.session.store-type=redis
```

**Fix:**
```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.session</groupId>
    <artifactId>spring-session-data-redis</artifactId>
</dependency>
```
```yaml
# application.yml
spring:
  session:
    store-type: redis
    timeout: 3600s
    redis:
      namespace: "order-service:sessions"
# Sessions now in Redis: any pod can serve any user
# Pod restart: user session survives in Redis
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Microservices Architecture` - 12-Factor is the design
  blueprint for each microservice
- `Stateless Services` - Factor 6 is the core of stateless
  service design

**Builds On This (learn these next):**
- `Monolith to Microservices Migration` - applying
  12-Factor to a legacy monolith during migration

**Operational context:**
- `Zero-Downtime Deployment` - Factor 9 (disposability)
  is the prerequisite for zero-downtime deployments
- `Conway's Law in Microservices` - organisational
  structure influences whether teams can build
  12-Factor services

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ TOP 5        │ 3: Config in env vars (not code)         │
│ VIOLATIONS   │ 6: Stateless (no in-process sessions)    │
│              │ 9: Fast startup + graceful shutdown      │
│              │ 10: Same DB in dev and prod              │
│              │ 11: Logs to stdout (not files)           │
├──────────────┼──────────────────────────────────────────┤
│ SPRING FIX   │ F3: ${ENV_VAR} in application.yml       │
│              │ F6: Spring Session -> Redis              │
│              │ F9: server.shutdown=graceful             │
│              │ F11: ConsoleAppender, no FileAppender    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "12 principles for cloud-native apps:    │
│              │  stateless, env-configured, disposable" │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Stateless Services → Twelve-Factor Beyond│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Factor 3: Store ALL config (URLs, credentials, ports)
   in environment variables. Never in source code.
2. Factor 6: Stateless processes. Sessions and caches
   in Redis, not in JVM memory.
3. Factor 11: Log to stdout. Let the platform route
   logs to wherever they need to go.

**Interview one-liner:**
"The Twelve-Factor App (Heroku, 2012) is the blueprint
for cloud-native microservices. Key factors: (3) Config
in env vars not code, (6) stateless processes with state
externalised to Redis/DB, (9) fast startup and graceful
shutdown for K8s compatibility, (11) logs to stdout not
files. A microservice that violates these factors works
locally but breaks in Kubernetes: sessions lost on pod
restart (Factor 6), logs lost on pod death (Factor 11),
cannot multi-environment deploy (Factor 3)."

---

### 💡 The Surprising Truth

Factor 10 (Dev/Prod Parity) is the most commonly
ignored factor with the highest defect cost. The typical
violation: H2 (in-memory) database in tests, PostgreSQL
in production. H2 and PostgreSQL handle: NULL semantics,
case sensitivity in string comparisons, date arithmetic,
UUID generation, and JSONB storage differently. Bugs
caused by this difference are systematically invisible
in tests and only appear in production. The fix costs
~30 minutes (add Docker Compose with PostgreSQL container,
use `@DirtiesContext` or Testcontainers for integration
tests). The ongoing defect cost: easily 20+ production
bugs per year attributable to this difference. For
30 minutes of work, Testcontainers is one of the
highest-ROI investments in software quality.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **AUDIT** Given a Spring Boot service, identify which
   of the 12 factors are violated: find hardcoded config,
   in-process sessions, log file configuration, and
   non-graceful shutdown.
2. **FIX** Remediate all violations: externalise config
   to Kubernetes ConfigMap/Secret, migrate sessions to
   Spring Session + Redis, configure ConsoleAppender,
   add graceful shutdown.
3. **PREVENT** Add a CI check that fails the build if
   any hardcoded database URLs or passwords are found
   in application.yml.
4. **DISCUSS** Explain why using H2 in tests is a
   risk, and implement the Testcontainers alternative.
5. **EXTEND** Describe the "Beyond 12-Factor" additions
   (API-first, telemetry, security) and how they apply
   to a modern Spring Boot microservice.

---

### 🧠 Think About This Before We Continue

**Q1.** You inherit a Spring Boot microservice that:
(a) reads its DB URL from application.properties,
(b) stores user sessions in HttpSession,
(c) writes logs to /var/log/service.log,
(d) uses H2 for local development.
List every production problem this service will have
on Kubernetes. For each problem, describe the exact
failure scenario and the fix.

**Q2.** Factor 9 requires fast startup. Your Spring
Boot service starts in 45 seconds due to:
15 seconds of eager cache warming, 20 seconds of schema
validation, and 10 seconds of connection pool warming.
K8s pod startup timeout is 30 seconds. All pods fail
readiness probes. Design the fixes for each cause
while maintaining the same functionality.

**Q3.** The Twelve-Factor App was written in 2012.
Containerisation (Docker, Kubernetes) was nascent.
Identify 3 factors that Docker/Kubernetes make
automatic or irrelevant, 3 that are more important
than ever, and 3 that need updating for the 2024
microservices context.