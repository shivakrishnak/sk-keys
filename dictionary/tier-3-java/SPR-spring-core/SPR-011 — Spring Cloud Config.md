---
layout: default
title: "Spring Cloud Config"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 11
permalink: /spring/spring-cloud-config/
id: SPR-011
category: Spring Core
difficulty: ★★★
depends_on: Spring Cloud Overview, Spring Boot, Distributed Systems
used_by: Microservices, CI-CD
related: AWS Parameter Store, Vault (HashiCorp), Kubernetes ConfigMap
tags:
  - java
  - spring
  - microservices
  - distributed
  - advanced
---

# SPR-011 — Spring Cloud Config

⚡ **TL;DR —** Spring Cloud Config provides a centralized Git-backed configuration server that externalizes and dynamically refreshes properties across all microservice instances.

| Metadata | Values |
|---|---|
| **Depends on** | Spring Cloud Overview, Spring Boot, Distributed Systems |
| **Used by** | Microservices, CI-CD |
| **Related** | AWS Parameter Store, Vault (HashiCorp), Kubernetes ConfigMap |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** You have 15 microservices each with their own `application.properties` bundled inside their JARs. Database URLs, feature flags, API keys — all hardcoded per environment. A database password rotation means rebuilding and redeploying all 15 services. A typo in one service's config causes a midnight incident. There's no single source of truth for what configuration any environment is currently running.

**THE BREAKING POINT:** In a microservices system, configuration sprawl is inevitable without a dedicated solution: duplicated values across services (database connection pool size defined in 15 places), environment-specific configs bundled in artifacts (violating the 12-factor app principle), no audit trail for config changes, secrets stored in version control, and no way to push a config change without redeploying.

**THE INVENTION MOMENT:** Spring Cloud Config Server (2014) applies the principle of **external configuration** from the 12-factor app methodology to the Spring ecosystem. A single Config Server serves all microservices' configuration from a Git repository. Properties are fetched at startup (or dynamically with `@RefreshScope`), environment-specific files follow a naming convention, and the server itself has a REST API for direct inspection of what config is served to which service in which environment.

---

### 📘 Textbook Definition

**Spring Cloud Config** provides server-side and client-side support for externalized configuration in a distributed system. The **Config Server** is a Spring Boot application that exposes a REST API serving property files from a backend store (Git by default, also filesystem, Vault, JDBC, AWS S3). The **Config Client** is any Spring Boot microservice that fetches its configuration from the Config Server at startup. Properties are served based on the application name, active profile, and label (Git branch). Secrets can be encrypted with symmetric or asymmetric keys, stored as `{cipher}...` values, and decrypted transparently on the server or client.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A central HTTP server that serves environment-specific properties from Git to all your microservices.

> Think of a corporate HR handbook stored in a shared Google Drive: every department (microservice) reads its own section of the handbook (application-specific config), with overrides per office location (environment profile), and HR (Config Server) publishes updates that all employees pick up automatically.

**One insight:** The Config Server's REST API (`/{application}/{profile}/{label}`) is inspectable and version-controlled — you can `curl` exactly what any service will receive in any environment, and the Git history is the complete audit trail of every config change ever made.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Config is external to the artifact** — the same JAR runs in dev, staging, and production with different config; the JAR never changes
2. **Property resolution is hierarchical** — `{app}-{profile}.yml` overrides `{app}.yml` overrides `application.yml`; specific overrides general
3. **The Config Server is stateless** — it reads from a Git backend; its own restart doesn't lose config state
4. **Dynamic refresh requires `@RefreshScope`** — beans annotated `@RefreshScope` are re-initialized on `/actuator/refresh` without service restart
5. **Encryption is server-side by default** — `{cipher}` values are decrypted before serving; clients receive plaintext

**DERIVED DESIGN:**

The hierarchical property resolution (invariant 2) mirrors how Spring's `Environment` already works — the Config Server simply adds a remote property source at the top of the resolution chain. This means Config Server properties can be overridden by local `application.yml` — which enables local development without needing a running Config Server.

**THE TRADE-OFFS:**

**Gain:** Single source of truth for all config; Git-backed audit history; environment isolation; dynamic refresh without restart; encryption for secrets; CI/CD pipeline can change config independently of code.

**Cost:** Config Server is a single point of failure unless made HA (multiple instances behind a load balancer with shared Git backend); startup dependency — services fail to start if Config Server is unavailable (mitigated with retry config); Git repository latency adds to service startup time; `@RefreshScope` has subtleties (not all beans support it).

---

### 🧪 Thought Experiment

**SETUP:** You have 10 microservices across 3 environments (dev/staging/prod). Each has a database URL and connection pool size that differs by environment. Without Config Server, these are in 30 separate property files bundled in JARs.

**WHAT HAPPENS WITHOUT CONFIG SERVER:** DBA rotates the production database password. You update 10 `application-prod.properties` files, rebuild 10 JARs, redeploy 10 services. Total time: 2 hours. During the window, some services use the old password (failing) and some use the new one (succeeding). Monitoring shows cascading errors with no single root cause visible.

**WHAT HAPPENS WITH CONFIG SERVER:** DBA updates one value in the Git repository: `datasource.password` in `application-prod.yml`. You trigger a `POST /actuator/busrefresh` broadcast. All 10 services pick up the new password within seconds via `@RefreshScope`. No restarts. No redeploys. The Git commit records exactly when the change was made and by whom. Audit compliance is automatic.

**THE INSIGHT:** Config Server converts configuration management from a deployment problem into a data problem. Config changes are data changes — versioned, diffable, auditable — decoupled from code deployment.

---

### 🧠 Mental Model / Analogy

> A hotel key management system: the front desk (Config Server) issues room keys (property files) to each guest (microservice) based on their room number (application name) and floor (profile). Master keys (shared config) work on all rooms; room-specific keys add or override individual settings. A new guest policy (config change) is applied by updating the key template — guests re-issue their keys without changing rooms.

- **Front desk** → Config Server (serves config on request)
- **Guest room number** → application name (e.g., `order-service`)
- **Hotel floor** → profile (dev, staging, production)
- **Room key** → resolved property set for that app + profile
- **Master key** → `application.yml` (shared defaults for all services)
- **Room-specific override** → `order-service-prod.yml`
- **Key template update** → Git commit to config repository
- **Re-issuing key** → `/actuator/refresh` or `busrefresh`

Where this analogy breaks down: A real key system issues physical keys; Spring Cloud Config issues configuration — so "keys" can be changed without the guest physically returning them. `@RefreshScope` beans pick up new values without the service restarting.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
One central server stores all your configuration files. Every microservice asks it for its settings when it starts up. When you change a setting, you only change it in one place.

**Level 2 — How to use it (junior developer):**
Set up a `@EnableConfigServer` Spring Boot app pointing at a Git repo. In each microservice, add `spring-cloud-starter-config` and set `spring.config.import=configserver:http://config-server:8888`. Create property files in Git named `{service-name}.yml` and `{service-name}-{profile}.yml`. Spring Boot fetches them at startup and merges them with local config.

**Level 3 — How it works (mid-level engineer):**
Config clients send `GET /order-service/production/main` to the server. The server clones/pulls the Git repo, resolves the property sources in priority order: `order-service-production.yml` → `order-service.yml` → `application-production.yml` → `application.yml`. It returns a `PropertySource` list as JSON. The client's `ConfigServicePropertySourceLocator` adds this as a `PropertySource` at the top of Spring's `Environment`. Beans marked `@RefreshScope` are stored in a `RefreshScope` cache; calling `/actuator/refresh` clears the cache and re-fetches config, causing those beans to be re-initialized on next access.

**Level 4 — Why it was designed this way (senior/staff):**
The Config Server's design treats configuration as an immutable artifact per commit — any `GET` to a specific `/{app}/{profile}/{label}` with a Git commit SHA is deterministically reproducible. This enables GitOps-style config management: a CI/CD pipeline updates config in Git, tags the commit, and the config server serves that exact commit to the environment. The decision to use Git as the default backend (over a database) was intentional: Git provides free history, diffing, branching, pull request review, and access control — all the properties you want for auditable configuration management.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│              Git Repository                     │
│  application.yml          (shared defaults)     │
│  order-service.yml        (service defaults)    │
│  order-service-prod.yml   (prod overrides)      │
└────────────────────┬────────────────────────────┘
                     │ git pull / clone
                     ▼
┌─────────────────────────────────────────────────┐
│              Config Server                      │
│  GET /{app}/{profile}/{label}                   │
│  → resolves property source hierarchy           │
│  → decrypts {cipher}... values                  │
│  → returns PropertySource JSON                  │
└────────────────────┬────────────────────────────┘
                     │ HTTP GET at startup
                     ▼
┌─────────────────────────────────────────────────┐
│            Microservice (Config Client)         │
│  ConfigServicePropertySourceLocator             │
│  → adds remote PropertySource to Environment   │
│  → local application.yml overrides if needed   │
│                                                 │
│  @RefreshScope beans → re-initialized on        │
│  POST /actuator/refresh                         │
└─────────────────────────────────────────────────┘
```

**Property resolution priority (highest to lowest):**
1. `{app}-{profile}.yml` — most specific (e.g., `order-service-production.yml`)
2. `{app}.yml` — service-level defaults (e.g., `order-service.yml`)
3. `application-{profile}.yml` — shared profile overrides
4. `application.yml` — shared defaults for all services
5. Local `application.yml` — client's own file (overrides Config Server if `spring.cloud.config.allow-override=true`)

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[Service starts: order-service, profile=production]
      │ ← YOU ARE HERE
      ▼
[ConfigServicePropertySourceLocator]
  GET http://config-server:8888/
          order-service/production/main
      │
      ▼
[Config Server: git pull from origin]
  Resolve: order-service-production.yml
        → order-service.yml
        → application-production.yml
        → application.yml
  Decrypt {cipher}... values
  Return: merged PropertySource JSON
      │
      ▼
[Client: add as top-priority PropertySource]
[Spring Environment: config properties available]
[Application context: @Value, @ConfigurationProperties bound]
[Service: ready to serve traffic]
```

**CONFIG REFRESH FLOW:**
```
[Git commit: update database.pool.size = 20]
      │
      ▼
[POST /actuator/refresh (or busrefresh)]
      │
      ▼
[RefreshScope: invalidate @RefreshScope bean cache]
[Re-fetch config from Config Server]
[Re-bind @ConfigurationProperties beans]
      │
      ▼
[Next request to affected bean → re-initialized]
[New pool size = 20 active without restart]
```

**WHAT CHANGES AT SCALE:**
Multiple Config Server instances behind a load balancer are needed for HA. All instances must point at the same Git repository. For high-read scenarios, enable the Config Server's in-memory cache: `spring.cloud.config.server.git.clone-on-start=true` and `refreshRate`. For secrets, replace the Git backend with HashiCorp Vault for secret lease management and dynamic credential rotation.

---

### 💻 Code Example

**BAD — config bundled inside the service artifact:**
```java
// application-prod.properties inside the JAR:
// spring.datasource.url=jdbc:postgresql://prod-db/app
// spring.datasource.password=HARDCODED_SECRET_IN_JAR
// Changing password = rebuild + redeploy

@SpringBootApplication
public class OrderApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}
```

**GOOD — Config Server setup + Config Client integration:**
```java
// === CONFIG SERVER ===
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(
            ConfigServerApplication.class, args);
    }
}
```

```yaml
# config-server application.yml
server:
  port: 8888
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/config-repo
          default-label: main
          search-paths: '{application}'  # per-service folder
          clone-on-start: true
          # Credentials via environment variables
          username: ${GIT_USERNAME}
          password: ${GIT_TOKEN}
        encrypt:
          enabled: true
# Symmetric encryption key (use asymmetric in prod)
encrypt:
  key: ${ENCRYPT_KEY}
```

```yaml
# config-repo / order-service-production.yml (in Git)
spring:
  datasource:
    url: jdbc:postgresql://prod-db.internal:5432/orders
    # Encrypted with: POST /encrypt endpoint on Config Server
    password: '{cipher}AQA5g7J9kL2mN8pQrStu...'
    hikari:
      maximum-pool-size: 20
      connection-timeout: 3000
feature:
  new-checkout-flow: true
```

```java
// === CONFIG CLIENT (microservice) ===

// application.yml (local — only bootstrap config)
// spring:
//   application:
//     name: order-service
//   config:
//     import: "configserver:http://config-server:8888"
//   cloud:
//     config:
//       fail-fast: true     # fail startup if server down
//       retry:
//         max-attempts: 6   # retry 6 times before failing

@Configuration
@ConfigurationProperties(prefix = "feature")
@RefreshScope  // re-binds on /actuator/refresh
public class FeatureFlags {
    private boolean newCheckoutFlow;
    // getters/setters
    public boolean isNewCheckoutFlow() {
        return newCheckoutFlow;
    }
    public void setNewCheckoutFlow(boolean v) {
        this.newCheckoutFlow = v;
    }
}

@Service
@RequiredArgsConstructor
public class CheckoutService {
    // @RefreshScope on the config class means this
    // picks up new values after refresh without restart
    private final FeatureFlags featureFlags;

    public Order checkout(Cart cart) {
        if (featureFlags.isNewCheckoutFlow()) {
            return newCheckoutFlow(cart);
        }
        return legacyCheckoutFlow(cart);
    }
}
```

**Triggering broadcast refresh via Spring Cloud Bus:**
```bash
# Refresh all instances of all services
curl -X POST \
  http://config-server:8888/actuator/busrefresh

# Refresh only order-service instances
curl -X POST \
  http://config-server:8888/actuator/busrefresh/order-service
```

---

### ⚖️ Comparison Table

| Feature | Spring Cloud Config | Kubernetes ConfigMap / Secret | AWS Parameter Store | HashiCorp Vault |
|---|---|---|---|---|
| **Backend** | Git, Vault, filesystem | etcd (K8s) | AWS managed | Dedicated secret store |
| **History/Audit** | Full Git history | K8s audit log | Version history | Audit log (paid) |
| **Dynamic refresh** | Yes (`@RefreshScope`) | Pod restart / envFrom | Yes (SSM + Lambda) | Yes (lease renewal) |
| **Encryption** | Yes (`{cipher}`) | Secrets base64 (weak) | KMS encryption | Strong encryption |
| **Access control** | Git ACL | K8s RBAC | IAM policies | Fine-grained policies |
| **Secret rotation** | Manual Git update | Manual update | Automatic (rotation) | Automatic (dynamic) |
| **Best for** | Spring Boot in VMs | K8s-native workloads | AWS-native services | Secret management |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Config Server changes are instantly visible" | By default, Config Client only fetches on startup. Running services need `/actuator/refresh` or a restart. Spring Cloud Bus enables broadcast refresh without per-service calls. |
| "All Spring beans update automatically on refresh" | Only beans annotated `@RefreshScope` (or `@ConfigurationProperties` with refresh enabled) are re-initialized. `@Value` on a non-`@RefreshScope` bean retains the value from startup. |
| "`bootstrap.yml` is still required" | Spring Boot 2.4+ replaced bootstrap context with `spring.config.import=configserver:`. Spring Boot 3+ requires Config Data API — bootstrap support is removed. |
| "Config Server stores the config" | Config Server is stateless — it reads from a backend (Git). The config lives in Git, not the server. Restarting the Config Server doesn't lose config. |
| "Encryption in Config Server is optional" | For production, any secrets (DB passwords, API keys) in the config repository must be encrypted. Storing plaintext secrets in Git is a critical security vulnerability. |
| "One Config Server instance is fine" | A single Config Server instance is a single point of failure. All services fail to start if the Config Server is down and `fail-fast=true`. Always run Config Server behind a load balancer with multiple instances. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Services fail to start — Config Server unreachable**

**Symptom:** All services fail at startup with `Could not locate PropertySource: I/O error on GET request`.
**Root Cause:** Config Server is down or network partitioned. With `fail-fast: true`, Spring Boot refuses to start without fetching remote config.
**Diagnostic:**
```bash
# Verify Config Server health
curl http://config-server:8888/actuator/health

# Test config endpoint directly
curl http://config-server:8888/order-service/production
```
**Fix:**
```yaml
# Add retry to tolerate transient Config Server unavailability
spring:
  cloud:
    config:
      fail-fast: true
      retry:
        initial-interval: 1000
        multiplier: 1.5
        max-interval: 10000
        max-attempts: 6   # ~30s total retry window
```
**Prevention:** Run Config Server as HA (2+ instances behind LB). Use `fail-fast: true` in production but with retry configuration. Consider a local config fallback for critical services.

**Mode 2: `@RefreshScope` not refreshing `@Value` fields**

**Symptom:** After `/actuator/refresh`, a bean still uses the old property value.
**Root Cause:** `@Value` fields on beans not annotated `@RefreshScope` are bound at startup and never re-evaluated. `@RefreshScope` must be on the class containing the `@Value` annotation, not just on a downstream consumer.
**Diagnostic:**
```bash
# Check which properties changed after refresh
curl -X POST http://service:8080/actuator/refresh
# Response shows list of changed keys
# If your key appears but bean still has old value,
# the bean is not @RefreshScope
```
**Fix:**
```java
// BAD: @Value on non-refresh-scoped bean
@Service
public class FeatureService {
    @Value("${feature.enabled}")
    private boolean featureEnabled;  // never refreshed
}

// GOOD: @RefreshScope on the bean with the @Value
@Service
@RefreshScope
public class FeatureService {
    @Value("${feature.enabled}")
    private boolean featureEnabled;  // refreshed on call
}

// BETTER: @ConfigurationProperties + @RefreshScope
@ConfigurationProperties(prefix = "feature")
@RefreshScope
public class FeatureProperties {
    private boolean enabled;
    // getters/setters
}
```
**Prevention:** Prefer `@ConfigurationProperties` with `@RefreshScope` over raw `@Value` for dynamic properties. Annotate the configuration class, not the consumer.

**Mode 3: Stale config served after Git push**

**Symptom:** Config Server is running, Git has the new config, but services still get the old values after refresh.
**Root Cause:** Config Server caches the Git clone locally. Git pull is not triggered on every request — the `refreshRate` controls how often the server pulls from the remote Git origin.
**Diagnostic:**
```bash
# Force Config Server to re-fetch from Git
# by calling its own refresh endpoint
curl -X POST http://config-server:8888/actuator/refresh

# Or verify Git clone path and pull manually
ls -la /tmp/config-repo-*  # local clone location
git -C /tmp/config-repo-* log --oneline -5
```
**Fix:**
```yaml
# Set refresh rate (seconds) on Config Server
spring:
  cloud:
    config:
      server:
        git:
          refreshRate: 30  # pull from Git every 30s
          # Or use webhook: push notification from Git
          # to POST /monitor on Config Server (spring-cloud-config-monitor)
```
**Prevention:** Use Git webhooks (`spring-cloud-config-monitor`) to trigger Config Server refresh immediately on Git push. This eliminates the polling lag entirely.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Spring Cloud Overview (2124) — Spring Cloud ecosystem and module relationships
- Spring Boot — autoconfiguration, `@ConfigurationProperties`, application context
- Distributed Systems — configuration management as a distributed systems concern

**Builds On This (learn these next):**
- Spring Cloud Gateway (2126) — API gateway that can use Config Server for dynamic route configuration
- CI-CD — pipeline integration for automated config updates via Git commits

**Alternatives / Comparisons:**
- AWS Parameter Store — managed AWS config/secrets with KMS encryption and versioning
- HashiCorp Vault — dedicated secret management with dynamic credentials and fine-grained access control
- Kubernetes ConfigMap / Secret — K8s-native config injection; simpler but weaker for secrets

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS   │ Git-backed centralized config     │
│              │ server for Spring Boot services   │
│ PROBLEM      │ Config sprawl, secrets in JARs,  │
│              │ no audit trail, no dynamic update │
│ KEY INSIGHT  │ Config Server is stateless —      │
│              │ state lives in Git                │
│ USE WHEN     │ Spring Boot microservices need    │
│              │ centralized config management     │
│ AVOID WHEN   │ K8s native: use ConfigMap/Secret  │
│ TRADE-OFF    │ HA overhead + refresh complexity  │
│ ONE-LINER    │ Git → Server → @RefreshScope bean │
│ NEXT EXPLORE │ Spring Cloud Gateway              │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(A — System Interaction)** Your Config Server uses a private Git repository. During a network partition, the Config Server cannot reach GitHub. New service instances are starting. How does `fail-fast`, `retry`, and the Config Server's local Git clone interact to determine whether those instances start successfully or fail?

2. **(C — Design Trade-off)** You're deciding between storing database credentials in Spring Cloud Config (Git backend with encryption) vs HashiCorp Vault. Your DBA needs credentials to auto-rotate every 24 hours. Which system better supports automatic rotation, and what changes to your microservice code would each approach require?

3. **(D — Root Cause)** After a CI/CD pipeline deploys a Config Server config change, your monitoring shows that 3 of 12 service instances are still serving old property values 5 minutes later, while the other 9 updated correctly. What are the possible root causes of partial refresh propagation when using Spring Cloud Bus?
