---
layout: default
title: "Nexus  Artifactory"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /maven-build/nexus-artifactory/
id: MVN-019
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Repository (local, central, remote), Maven Dependencies, SNAPSHOT vs RELEASE
used_by: Build Performance Optimization, OWASP Dependency Check, Maven Release Plugin
related: Maven Repository (local, central, remote), SNAPSHOT vs RELEASE, Build Reproducibility
tags:
  - maven
  - build-tools
  - repository-manager
  - nexus
  - artifactory
  - java
  - intermediate
---

# MVN-019 — Nexus  Artifactory

⚡ TL;DR — Nexus Repository and JFrog Artifactory are artifact repository managers that act as a local proxy to Maven Central, a private SNAPSHOT/release store, and an access-control layer — making enterprise builds faster, more secure, and auditable.

| #1079           | Category: Maven & Build Tools (Java)                                                  | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Maven Repository (local, central, remote), Maven Dependencies, SNAPSHOT vs RELEASE    |                 |
| **Used by:**    | Build Performance Optimization, OWASP Dependency Check, Maven Release Plugin          |                 |
| **Related:**    | Maven Repository (local, central, remote), SNAPSHOT vs RELEASE, Build Reproducibility |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every developer and every CI agent downloads JARs directly from Maven Central. A 100-developer team downloading the same Spring Boot release independently is 100 × 50 MB = 5 GB of redundant downloads per release. CI agents race to download on cold runs. Maven Central is a public internet dependency — an outage breaks every build globally. No record of which artifacts were used in which release.

**THE BREAKING POINT:**
Enterprise Java projects need: (1) repeatably fast builds regardless of internet conditions; (2) control over which third-party libraries developers can use; (3) a home for internally-built artifacts (SNAPSHOTs and releases); (4) an audit trail for compliance.

**THE INVENTION MOMENT:**
An artifact repository manager sits between your builds and the internet. It proxies public repositories (downloading once, caching forever), hosts private repositories, and enforces security policies — all through a single URL that all builds point to.

---

### 📘 Textbook Definition

**Nexus Repository** (Sonatype) and **JFrog Artifactory** are artifact repository managers for Maven (and other package managers). They serve three roles: (1) **proxy repositories** — cache artifacts from remote sources (Maven Central, npm, PyPI) to avoid repeated internet downloads; (2) **hosted repositories** — store internally built artifacts (SNAPSHOTs and releases); (3) **group/virtual repositories** — aggregate multiple repositories behind a single URL. Developers and CI systems configure Maven to point to the repository manager instead of Maven Central; all resolution, caching, and publishing flows through it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Nexus/Artifactory is a central artifact hub: it caches public JARs, stores your team's JARs, and enforces policies — all through one URL.

**One analogy:**

> A corporate mailroom. External packages (Maven Central JARs) are received, logged, and delivered internally. Internal packages (your builds) are stored and dispatched to requesters. Every artifact in or out is logged.

**One insight:**
Once your team sets up a repository manager, Maven Central becomes an implementation detail — your builds never directly touch the internet during normal operation.

---

### 🔩 First Principles Explanation

**REPOSITORY MANAGER ROLES:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Nexus / Artifactory                      │
│                                                             │
│  Proxy Repos:         Hosted Repos:       Group/Virtual:   │
│  ┌───────────────┐   ┌──────────────┐   ┌─────────────┐   │
│  │ maven-central │   │ my-releases  │   │ maven-public│   │
│  │ (caches       │   │ (company     │   │ (aggregates │   │
│  │  Central JARs)│   │  release     │   │  all above) │   │
│  └───────────────┘   │  artifacts)  │   └─────────────┘   │
│                      ├──────────────┤         ▲           │
│                      │ my-snapshots │         │           │
│                      │ (dev builds) │         │           │
│                      └──────────────┘         │           │
└────────────────────────────────────────────── │ ──────────┘
                                                │
        All Maven builds point here: ──────────┘
        https://nexus.mycompany.com/repository/maven-public/
```

**HOW PROXY CACHING WORKS:**

1. Build requests `com.google.guava:guava:32.0-jre`
2. Nexus checks its local store — not present
3. Nexus fetches from Maven Central, stores in proxy repo
4. Nexus returns artifact to build
5. Next request for same artifact: Nexus returns from local store (no internet call)

**HOW SNAPSHOT PUBLISHING WORKS:**

```
mvn deploy (with version 1.0.0-SNAPSHOT)
    → authenticates against Nexus
    → publishes to my-snapshots repo
    → URL: .../my-snapshots/com/example/my-app/1.0.0-SNAPSHOT/
    → each deploy generates: my-app-1.0.0-20241201.123456-1.jar
    → Nexus metadata.xml tracks latest SNAPSHOT pointer
```

**THE TRADE-OFFS:**
**Gain:** Single internet egress point; build speed (LAN download vs internet); private artifact hosting; access control (block certain licenses/groups); audit trail; works offline after initial cache warm.
**Cost:** Infrastructure to maintain; additional failure point (Nexus outage breaks builds); storage cost (cache can grow to hundreds of GBs); initial configuration burden.

---

### 🧪 Thought Experiment

**SETUP:**
Your Nexus instance goes offline for 30 minutes during a critical release deployment. CI tries to `mvn deploy` the release. Maven attempts to publish to Nexus — fails. It also tries to resolve a few dependencies — they're all in the local `.m2` cache on the CI agent.

**QUESTIONS:**

1. Does the build fail entirely or partially?
2. What Maven flags would allow the build to proceed in degraded mode (using only cached dependencies)?
3. What architectural change to Nexus would prevent single-instance downtime?

**THE LESSON:**
The proxy role (reading from Nexus) can be resilient with caching; the publishing role (writing to Nexus) cannot be bypassed — making Nexus HA setup important for release pipelines.

---

### 🧠 Mental Model / Analogy

> Think of Nexus/Artifactory as the corporate IT-managed software library. You can request any book (JAR) — the librarian gets it from the national library (Maven Central) if they don't have it, keeps a copy, and restricts access to books on the banned list (license policy). Your team can also donate books (publish internal JARs). Everyone draws from the same curated collection.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Nexus/Artifactory stores and serves Maven JARs for your team, so you don't download everything from the internet every time.

**Level 2:** It has three repository types: proxy (cache from Central), hosted (store your own), and group (one URL combines many repos). All your builds point to the group URL.

**Level 3:** Maven `settings.xml` configures Nexus as a mirror (`mirrorOf=*`). Server credentials for publishing are stored in `settings.xml` servers section (referenced by `id` matching `<distributionManagement>` repo id). SNAPSHOTs and releases are stored in separate hosted repos with different policies.

**Level 4:** Nexus Pro / Artifactory Pro adds: component lifecycle management (block transitive CVEs), licence compliance (fail build if LGPL detected), replication across data centres, cleanup policies (delete old SNAPSHOTs), virtual repos for multi-format (Maven + npm + Docker in one system), and REST API for automation.

---

### ⚙️ How It Works (Mechanism)

```bash
# Verify Maven is routing through Nexus
mvn dependency:resolve -Dverbose 2>&1 | grep "Downloading from"
# Should show: Downloading from nexus-central: https://nexus.mycompany.com/...

# Publish a SNAPSHOT
mvn deploy
# Requires distributionManagement + server credentials in settings.xml

# Check what's been published
curl -u ci-user:password \
  "https://nexus.mycompany.com/service/rest/v1/search?repository=maven-snapshots&group=com.example"
```

---

### 💻 Code Example

**Maven `settings.xml` for Nexus:**

```xml
<settings>
  <mirrors>
    <!-- Route ALL repo lookups through Nexus group -->
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>https://nexus.mycompany.com/repository/maven-public/</url>
    </mirror>
  </mirrors>

  <servers>
    <server>
      <id>nexus-releases</id>
      <username>deployer</username>
      <password>${env.NEXUS_TOKEN}</password>
    </server>
    <server>
      <id>nexus-snapshots</id>
      <username>deployer</username>
      <password>${env.NEXUS_TOKEN}</password>
    </server>
  </servers>

  <profiles>
    <profile>
      <id>nexus</id>
      <repositories>
        <repository>
          <id>central</id>
          <url>https://nexus.mycompany.com/repository/maven-public/</url>
          <snapshots><enabled>true</enabled></snapshots>
        </repository>
      </repositories>
    </profile>
  </profiles>
  <activeProfiles><activeProfile>nexus</activeProfile></activeProfiles>
</settings>
```

**`pom.xml` `<distributionManagement>`:**

```xml
<distributionManagement>
  <repository>
    <id>nexus-releases</id>
    <url>https://nexus.mycompany.com/repository/maven-releases/</url>
  </repository>
  <snapshotRepository>
    <id>nexus-snapshots</id>
    <url>https://nexus.mycompany.com/repository/maven-snapshots/</url>
  </snapshotRepository>
</distributionManagement>
```

---

### ⚖️ Comparison Table

| Feature                  | Nexus OSS | Nexus Pro | JFrog Artifactory OSS | JFrog Pro |
| ------------------------ | --------- | --------- | --------------------- | --------- |
| Maven proxy/hosted/group | ✓         | ✓         | ✓                     | ✓         |
| npm, Docker support      | Partial   | ✓         | Partial               | ✓         |
| HA / clustering          | ✗         | ✓         | ✗                     | ✓         |
| CVE / licence policy     | ✗         | ✓         | ✗                     | ✓         |
| Build integration (CI)   | Basic     | Full      | Basic                 | Full      |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                         |
| ----------------------------------------------- | ------------------------------------------------------------------------------- |
| Nexus replaces Maven                            | Nexus is a server Maven talks to; Maven still resolves and builds               |
| Nexus automatically blocks vulnerable libraries | Only with Lifecycle (Pro) or an external scanner (OWASP) — not by default       |
| Any JAR uploaded to Nexus is "safe"             | Nexus stores whatever is uploaded; policy enforcement is separate configuration |
| `mirrorOf=*` blocks all internet access         | Only Maven artifact downloads; other HTTP calls from plugins are unaffected     |

---

### 🚨 Failure Modes & Diagnosis

**Builds fail: 401 Unauthorized when deploying**

**Root Cause:** `settings.xml` server `<id>` doesn't match `pom.xml` `<distributionManagement>` repository `<id>`.

**Fix:** Ensure both IDs match exactly (e.g., both `nexus-releases`).

---

**Proxy repo not caching: every build re-downloads from Central**

**Root Cause:** `mirrorOf` pattern doesn't match the repo ID in use, or proxy repo's remote URL is misconfigured.

**Diagnosis:** `mvn dependency:resolve -Dverbose` — look for download URLs.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Repository (local, central, remote)`, `Maven Dependencies`, `SNAPSHOT vs RELEASE`

**Builds On This:** `Build Performance Optimization`, `OWASP Dependency Check`, `Maven Release Plugin`

**Related Patterns:** `Maven Repository (local, central, remote)`, `SNAPSHOT vs RELEASE`, `Build Reproducibility`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOOLS        │ Sonatype Nexus, JFrog Artifactory         │
├──────────────┼───────────────────────────────────────────┤
│ PROXY REPO   │ Caches public artifacts (Central etc.)    │
├──────────────┼───────────────────────────────────────────┤
│ HOSTED REPO  │ Stores your internal builds               │
├──────────────┼───────────────────────────────────────────┤
│ GROUP REPO   │ One URL → many repos combined             │
├──────────────┼───────────────────────────────────────────┤
│ PUBLISH      │ mvn deploy + distributionManagement       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Central proxy + private store + policy"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your CI pipeline runs `mvn package` (not `deploy`) and all tests pass. A colleague on the same project runs `mvn package` and gets "Could not find artifact com.mycompany:my-shared-lib:1.2.0". What's the most likely cause, and how would you fix it?

**Q2.** Your team decides to use JFrog Artifactory as a Docker registry in addition to a Maven repository. What architectural advantage does consolidating package management (Maven + Docker) into one tool provide for your CI/CD pipeline?
