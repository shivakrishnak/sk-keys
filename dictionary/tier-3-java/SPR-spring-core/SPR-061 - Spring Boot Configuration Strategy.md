---
id: SPR-061
title: Spring Boot Configuration Strategy
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-003, SPR-044, SPR-045
used_by:
related: SPR-059, SPR-062, SPR-067
tags:
  - spring
  - java
  - advanced
  - architecture
  - bestpractice
  - production
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /spr/spring-boot-configuration-strategy/
---

# SPR-061 - Spring Boot Configuration Strategy

⚡ TL;DR - A configuration strategy defines which values live in code, which in property files, which in environment variables, and which in a remote config server - with a clear override hierarchy and secret management plan.

| Field          | Value                                                                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Depends on** | [[SPR-003 - Why Spring Boot Changed Java Development]], [[SPR-044 - Auto-Configuration]], [[SPR-045 - Spring Boot Actuator]]                           |
| **Used by**    | -                                                                                                                                                      |
| **Related**    | [[SPR-059 - Spring Architecture at Scale]], [[SPR-062 - Spring Security Architecture Design]], [[SPR-067 - Spring Specification and Extension Points]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Database passwords hardcoded in `application.properties`. The same file committed to Git. All environments (dev, staging, prod) share one configuration file with `if prod` comments. Rotating a database password requires rebuilding and redeploying the application. Developers discover production configuration by reading production logs after an incident.

**THE BREAKING POINT:**

A single configuration antipattern - a secret in a committed file - causes a security incident. The post-mortem recommends "better configuration management." Without a strategy, the fix is partial: move the password to an environment variable but leave everything else as-is. The next incident targets a different hardcoded value.

**THE INVENTION MOMENT:**

The 12-Factor App methodology (2012) formalised the principle: _configuration is what changes between deployments_. Credentials, URLs, feature flags, and environment-specific values are configuration; algorithm implementations, business rules, and library versions are code. These have fundamentally different change rates, sensitivity levels, and ownership models.

**EVOLUTION:**

- **2012:** 12-Factor App defines config as environment-separate from code
- **2014:** Spring Cloud Config server provides centralised external configuration
- **2016:** Kubernetes ConfigMaps and Secrets provide container-native config injection
- **2020:** HashiCorp Vault + Spring Cloud Vault enable dynamic secrets with automatic rotation
- **2023:** Spring Boot 3.1 SSL Bundles provide declarative TLS certificate management
- **2024:** Spring Boot 3.2 `@ConfigurationProperties` records (Java 16+) type-safe binding

---

### 📘 Textbook Definition

**Spring Boot Configuration Strategy** is the set of decisions governing _where_ configuration values are stored, _how_ they are injected into the application, _which layer wins_ when the same property is defined in multiple places, and _how secrets are managed_ without appearing in version control. Spring Boot supports 17 property sources in a defined priority order; a configuration strategy decides which of these sources to use for which values.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Configuration strategy answers: what lives in code, what in files, what in environment, what in a vault - and who can change what.

> Configuration is like a building's thermostat system. The setpoints (environment variables) are changed by the facilities team. The HVAC program (application.yml) is maintained by building management. The physical wiring (code defaults) is only changed by engineers. Having one person control all three creates chaos.

**One insight:** Spring Boot's 17-source override hierarchy means the same property defined in multiple places has a deterministic winner - knowing the hierarchy lets you predict exactly what value will be active in any environment.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Secrets must never appear in version-controlled files
2. Configuration that changes between environments must be externalised
3. A property defined in a higher-priority source always wins
4. Type-safe binding catches misconfiguration at startup, not at runtime
5. Configuration changes should not require application redeployment if possible

**DERIVED DESIGN:**

From invariant 1 → secrets come from environment variables, Kubernetes Secrets, or Vault; never from `application.properties`.
From invariant 2 → environment-specific values go in `application-{profile}.yml`, not the base file.
From invariant 3 → command-line args (`--key=value`) override everything; code defaults are last resort.
From invariants 4+5 → `@ConfigurationProperties` with JSR-303 validation + Spring Cloud Config for live reload.

**THE TRADE-OFFS:**

**Gain:** Security (no secrets in Git); portability (same JAR deploys to any environment); auditability (who changed what config when).

**Cost:** External config sources (Config Server, Vault) become availability dependencies; complex override hierarchy requires documentation; `@ConfigurationProperties` requires more boilerplate than `@Value`.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Different environments genuinely have different values; secrets genuinely require different handling from non-secrets.

**Accidental:** The 17-source override hierarchy is more complex than most applications need. Most teams only need 3-4 sources.

---

### 🧪 Thought Experiment

**SETUP:** You have a Spring Boot application deployed to dev, staging, and production. Database URL, pool size, and API keys differ per environment.

**WHAT HAPPENS without strategy:**

One `application.properties` file with prod values checked into Git. `DB_URL=jdbc:postgresql://prod-db:5432/myapp` is visible to every developer with Git access. Changing staging configuration requires a code commit and CI build. An audit shows the prod API key has been visible in Git history for 18 months.

**WHAT HAPPENS with strategy:**

`application.yml` contains only defaults valid for all environments (timeouts, pool sizes, feature flags). `application-{env}.yml` contains environment-specific non-secret values (URLs, hostnames). Secrets (`DB_PASSWORD`, `API_KEY`) come from Kubernetes Secrets or Vault, mounted as environment variables. Developers never see prod secrets. Config changes deploy in seconds via ConfigMap update without redeployment.

**THE INSIGHT:**

A configuration strategy is a _security document_ as much as a technical one. Treating all configuration equally (same source, same visibility) is a security failure waiting to happen.

---

### 🧠 Mental Model / Analogy

> Configuration layers are like a legal override chain. The constitution (code defaults) is the foundation. Laws (application.yml) refine it. State laws (profile yml) further specialise. Executive orders (environment variables) can override for urgency. Emergency powers (command-line args) can override everything. Each level can only be changed by the authority that owns it.

**Element mapping:**

- Constitution → Spring Boot defaults (hardcoded in auto-config)
- Laws → `application.yml` in JAR
- State laws → `application-{profile}.yml`
- Executive orders → environment variables / Kubernetes ConfigMaps
- Emergency powers → command-line arguments (`--server.port=9090`)
- Secret laws (classified) → Vault / Kubernetes Secrets (restricted access)

Where this analogy breaks down: unlike law, Spring Boot's hierarchy is strictly numerical - `command-line > env vars > application-{profile}.yml > application.yml > defaults` with no room for political interpretation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Configuration strategy is the plan for where different settings live and which settings override others. Some settings are safe to put in files in your code (like timeout values), some must be kept secret (like passwords), and some change between development and production (like database addresses). The strategy says which goes where.

**Level 2 - How to use it (junior developer):**
Use `application.yml` for safe defaults. Use `application-dev.yml`, `application-prod.yml` for environment overrides. Use `@Value("${my.property}")` for simple injection. Use `@ConfigurationProperties(prefix = "my")` for grouped properties with validation. Never put passwords in yml files - use `${MY_SECRET}` and set the env var at deployment time.

**Level 3 - How it works (mid-level engineer):**
Spring Boot's `Environment` abstraction aggregates `PropertySource` objects in priority order. When `@Value("${server.port}")` is resolved, `Environment.getProperty("server.port")` iterates the source list in order and returns the first match. Active profiles are determined by `spring.profiles.active` (itself a property, with the same override rules). `@ConfigurationProperties` binds a property prefix to a Java class, validating with `@NotNull`, `@Min` etc. at context startup.

**Level 4 - Why it was designed this way (senior/staff):**
The 17-source hierarchy was designed to support the entire deployment spectrum: from a developer running locally (command-line overrides, local yml) through CI testing (system properties, test annotations) to production Kubernetes (env vars, ConfigMaps). Each source type corresponds to an actor who legitimately needs to override configuration: ops teams use env vars; developers use local files; CI uses system properties. The hierarchy ensures predictable override semantics without requiring any code changes across the spectrum.

**Expert Thinking Cues:**

- `@TestPropertySource` and `@SpringBootTest(properties=...)` insert test sources at the top of the hierarchy
- `spring.config.import` (Boot 2.4+) allows importing Vault, AWS Parameter Store, or Config Server as additional sources
- `@RefreshScope` enables live configuration reload without application restart when using Spring Cloud Config

---

### ⚙️ How It Works (Mechanism)

Spring Boot property source priority (highest to lowest):

```
1.  Devtools global settings (~/.spring-boot-devtools.properties)
2.  @TestPropertySource annotations
3.  @SpringBootTest properties attribute
4.  Command-line arguments (--key=value)
5.  SPRING_APPLICATION_JSON (env var / system property)
6.  ServletConfig init parameters
7.  ServletContext init parameters
8.  JNDI attributes (java:comp/env)
9.  Java System properties (System.getProperties())
10. OS environment variables
11. RandomValuePropertySource (random.*)
12. application-{profile}.properties outside JAR
13. application-{profile}.properties inside JAR
14. application.properties outside JAR
15. application.properties inside JAR
16. @PropertySource annotations on @Configuration
17. Default properties (SpringApplication.setDefaultProperties)
```

Most production applications only use sources 4, 10, 12/13, 14/15, and 17.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Developer workstation]
     ├─ application.yml (in JAR - source 15)
     ├─ application-dev.yml (in JAR - source 13)
     └─ SPRING_PROFILES_ACTIVE=dev (env - source 10)

[CI/CD Pipeline]
     ├─ application.yml (in JAR)
     ├─ application-test.yml (in JAR)
     ├─ --spring.datasource.url=... (cmd - source 4)
     └─ SPRING_PROFILES_ACTIVE=test
              ← YOU ARE HERE

[Production Kubernetes]
     ├─ application.yml (in JAR - non-secret defaults)
     ├─ application-prod.yml (in JAR - prod URLs)
     ├─ DB_PASSWORD=*** (Kubernetes Secret - source 10)
     ├─ SPRING_PROFILES_ACTIVE=prod
     └─ Spring Cloud Config Server (external - source 12)
```

**FAILURE PATH:**

- Missing required property → startup fails with `MissingRequiredPropertiesException` if `@NotNull` validation
- Wrong profile active → wrong database URL used silently (no error until first query)
- Secret in `application.yml` committed to Git → security incident; rotate all affected credentials immediately

**WHAT CHANGES AT SCALE:**

Large organisations centralise configuration via Spring Cloud Config or AWS Parameter Store / Secrets Manager. Each service declares what properties it needs; the platform provides values per environment. Configuration changes become audited operations with approval workflows, separate from code deployments.

---

### 💻 Code Example

**BAD - inline secrets and no type safety:**

```yaml
# application.yml - NEVER DO THIS
spring:
  datasource:
    url: jdbc:postgresql://prod.db:5432/myapp
    password: sup3rS3cret! # SECRET IN VERSION CONTROL!
payment:
  api-key: pk_live_abc123 # SECRET IN VERSION CONTROL!
```

```java
// Fragile string injection - no validation
@Value("${payment.api-key}")
private String apiKey; // typo = NPE at runtime
```

**GOOD - externalised secrets with type-safe binding:**

```yaml
# application.yml - safe defaults only
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/myapp
    # password comes from env var DB_PASSWORD
  hikari:
    maximum-pool-size: 20

payment:
  timeout-ms: 5000
  retry-count: 3
  # api-key comes from env var PAYMENT_API_KEY
```

```java
// Type-safe, validated configuration binding
@ConfigurationProperties(prefix = "payment")
@Validated
public record PaymentProperties(
    @NotNull String apiKey,           // from PAYMENT_API_KEY
    @Min(100) @Max(30000) int timeoutMs,
    @Min(0) @Max(10) int retryCount
) {}

// Enable in @SpringBootApplication or @Configuration
@EnableConfigurationProperties(PaymentProperties.class)
```

```bash
# Kubernetes deployment - secrets injected as env vars
# (Never in the YAML committed to Git)
kubectl create secret generic payment-secrets \
  --from-literal=PAYMENT_API_KEY=pk_live_abc123
```

**How to test / verify correctness:**

```java
@SpringBootTest(properties = {
    "payment.api-key=test-key",
    "payment.timeout-ms=1000",
    "payment.retry-count=2"
})
class PaymentConfigTest {
    @Autowired PaymentProperties props;

    @Test
    void propertiesLoadCorrectly() {
        assertThat(props.apiKey()).isEqualTo("test-key");
        assertThat(props.timeoutMs()).isEqualTo(1000);
    }

    @Test
    void invalidTimeoutFailsValidation() {
        // Validation should prevent startup
        // Test via @SpringBootTest with invalid value
        assertThatThrownBy(() ->
            new AnnotationConfigApplicationContext() {{
                register(PaymentProperties.class);
                refresh();
            }}
        ).isInstanceOf(BeanCreationException.class);
    }
}
```

---

### ⚖️ Comparison Table

| Config Source               | Use For                          | Secret-safe        | Live Reload            | Complexity |
| --------------------------- | -------------------------------- | ------------------ | ---------------------- | ---------- |
| `application.yml` in JAR    | Defaults, algorithm config       | No                 | No (requires redeploy) | Low        |
| `application-{profile}.yml` | Environment-specific non-secrets | No                 | No                     | Low        |
| Environment variables       | Secrets, URL overrides           | Yes (with RBAC)    | No                     | Low        |
| Kubernetes ConfigMap        | Cluster-scoped config            | No                 | Yes (with sidecar)     | Medium     |
| Kubernetes Secret           | Cluster-scoped secrets           | Yes (with RBAC)    | Yes (with sidecar)     | Medium     |
| Spring Cloud Config         | Centralised, versioned           | Depends on backend | Yes (with Bus)         | High       |
| HashiCorp Vault             | Dynamic secrets, rotation        | Yes                | Yes                    | High       |
| AWS Parameter Store         | AWS-native, IAM-controlled       | Yes (SecureString) | Yes                    | Medium     |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                              |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Environment variables are secure"                    | Env vars are visible to all processes running as the same user, visible in `/proc/<pid>/environ`, and often logged by orchestrators. They are safer than files in Git but not equivalent to a proper secret manager. |
| "`@Value` is the recommended injection"               | `@ConfigurationProperties` is recommended for any non-trivial config set: it provides type safety, validation, IDE support, and documentation via `spring-configuration-metadata.json`.                              |
| "application.yml overrides application-prod.yml"      | The opposite: profile-specific files override the base file for matching properties. Source 13 (profile-specific inside JAR) is higher priority than source 15 (base inside JAR).                                    |
| "Spring Cloud Config is required for external config" | Kubernetes ConfigMaps + Secrets mounted as env vars provide external config without Spring Cloud Config complexity for most use cases.                                                                               |
| "Configuration validation happens at first use"       | With `@ConfigurationProperties` + `@Validated`, validation happens at application startup. Missing or invalid properties fail fast at boot, not at the first request.                                                |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Wrong profile active in production**

**Symptom:** Production service connects to dev database; no errors (dev DB exists and accepts connections).

**Root Cause:** `SPRING_PROFILES_ACTIVE` env var not set in production; defaults to no profile; `application-dev.yml` not loaded; base `application.yml` has dev URL as default.

**Diagnostic:**

```bash
curl http://prod-service/actuator/env \
  | jq '.activeProfiles'
# Should show ["prod"]; if empty: wrong profile
curl http://prod-service/actuator/env \
  | jq '.propertySources[] | select(.name |
    contains("application")) | .properties."spring.datasource.url"'
```

**Fix:** Set `SPRING_PROFILES_ACTIVE=prod` in deployment. Add startup assertion in CI that verifies active profile.

**Prevention:** Default `spring.profiles.active=prod` in production base image; require explicit override for non-prod environments.

---

**Mode 2: Secret leaked in Git**

**Symptom:** Security scan flags plaintext password in `application.yml` commit history.

**Root Cause:** Developer added `spring.datasource.password=mypassword` to the committed config file.

**Diagnostic:**

```bash
# Scan entire Git history for secrets
git log -p --all -- "*.yml" "*.properties" \
  | grep -i "password\|secret\|api.key\|token"
# Use truffleHog or gitleaks for full scan:
gitleaks detect --source . --verbose
```

**Fix:** Rotate ALL credentials that appeared in the history immediately. Remove secret from history using `git filter-repo`. Add `.pre-commit-config.yaml` with detect-secrets hook.

**Prevention:** Install `gitleaks` as a pre-commit hook; add CI secret scanning as a gating check.

---

**Mode 3: Config property typo silently uses null (Security failure mode)**

**Symptom:** Security feature (e.g., JWT secret, CORS origin restriction) silently disabled because property resolves to `null` or empty string.

**Root Cause:** `@Value("${security.jwt.secret:}")` - the `:` default makes the property optional; typo in property name goes undetected.

**Diagnostic:**

```bash
curl http://localhost:8080/actuator/env \
  | jq '."security.jwt.secret"'
# If null or "": property not loaded
```

**Fix:**

```java
// BAD: silent null if property missing
@Value("${security.jwt.secret:}")
private String jwtSecret;

// GOOD: fail-fast with @ConfigurationProperties
@ConfigurationProperties("security.jwt")
@Validated
public record JwtProperties(
    @NotBlank String secret,       // fail startup if missing
    @Min(3600) int expirySeconds
) {}
```

**Prevention:** All security-critical properties must use `@NotNull` / `@NotBlank` validation. Never use default values for security properties.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-003 - Why Spring Boot Changed Java Development]] - the Boot configuration model
- [[SPR-044 - Auto-Configuration]] - how auto-config reads properties
- [[SPR-045 - Spring Boot Actuator]] - `/actuator/env` for config debugging

**Builds On This (learn these next):**

- [[SPR-062 - Spring Security Architecture Design]] - applying config strategy to security values
- [[SPR-011 - Spring Cloud Config]] - centralised external configuration
- [[SPR-059 - Spring Architecture at Scale]] - config at multi-team scale

**Alternatives / Comparisons:**

- HashiCorp Vault - dynamic secret management with automatic rotation
- AWS Parameter Store / Secrets Manager - cloud-native secret management
- Kubernetes Secrets - cluster-native secret injection

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Decisions about where config lives & wins |
| PROBLEM       | Secrets in Git; wrong env in prod; no type|
|               | safety; config drift across environments  |
| KEY INSIGHT   | Classify config by sensitivity + change   |
|               | rate; use appropriate source for each     |
| USE WHEN      | Any app with >1 environment               |
| AVOID WHEN    | -                                         |
| TRADE-OFF     | Simplicity vs security + flexibility      |
| ONE-LINER     | Defaults in yml, env-specifics in profiles,|
|               | secrets in env vars / Vault              |
| NEXT EXPLORE  | SPR-062 (Security Config), SPR-011        |
|               | (Spring Cloud Config)                     |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Secrets never go in version-controlled files - use env vars, Kubernetes Secrets, or Vault
2. `@ConfigurationProperties` with `@Validated` catches misconfiguration at startup, not at runtime
3. Higher-priority sources (command-line, env vars) always override lower-priority ones (yml files)

**Interview one-liner:** "A Spring Boot configuration strategy separates secrets (env vars/Vault), environment-specifics (profile yml), and safe defaults (base yml), using `@ConfigurationProperties` validation to fail fast on misconfiguration at startup."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Classify before storing._ Configuration properties have different sensitivity, change rate, and ownership. The storage mechanism must match the classification: public defaults in code, environment-specifics in config files, secrets in vaults. This classification principle applies to any system that manages configuration.

**Where else this pattern appears:**

- **Kubernetes** - ConfigMaps for non-secret configuration, Secrets for sensitive data, both mounted as env vars or volumes
- **AWS Parameter Store** - `String` type for public config, `SecureString` (KMS-encrypted) for secrets, same API
- **GitHub Actions** - Repository variables for public config, Repository secrets for sensitive data, same substitution syntax

---

### 💡 The Surprising Truth

Spring Boot's `@ConfigurationProperties` generates IDE completion metadata via `spring-boot-configuration-processor`, a compile-time annotation processor that produces `META-INF/spring-configuration-metadata.json`. This JSON file is what enables your IDE to autocomplete `spring.datasource.hikari.maximum-pool-size` in `application.yml`. Every Spring Boot property you see autocompleted in your IDE was generated from `@ConfigurationProperties` classes in the Spring Boot source code - the same mechanism you use for your own properties. The entire documentation in `application.yml` autocomplete is generated from code, not written by hand.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** `@RefreshScope` allows beans to be re-created when configuration changes at runtime (via Spring Cloud Config + Spring Cloud Bus). What categories of beans are dangerous to mark with `@RefreshScope`, and what happens to in-flight requests that are being processed by a `@RefreshScope` bean when a refresh is triggered?

_Hint:_ Consider stateful beans, database connections, thread pools, and security filter chains - what happens if these are replaced mid-request?

**Question 2 (B - Scale):** A platform team serves 200 microservices, each with 5 environment-specific configuration files. That is 1,000 configuration files across environments, some containing secrets that must be rotated quarterly. Describe an architecture using Spring Cloud Config or an equivalent that allows secret rotation without touching any of the 200 service codebases.

_Hint:_ Look at Spring Cloud Config's Git backend, Vault's dynamic secret generation in [[SPR-011 - Spring Cloud Config]], and how `@RefreshScope` + actuator `/refresh` endpoint can propagate the change.

**Question 3 (E - First Principles):** Spring Boot defines 17 property source priorities. Why does the command-line (`--key=value`) have the highest priority (after test sources), and what operational scenarios does this design decision enable?

_Hint:_ Think about emergency configuration changes in production (hotfixing a misconfiguration without redeployment), Kubernetes pod-level overrides, and A/B testing configuration variants.
