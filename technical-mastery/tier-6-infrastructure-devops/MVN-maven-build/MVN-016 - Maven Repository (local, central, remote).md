---
version: 1
layout: default
title: "Maven Repository (local, central, remote)"
parent: "Maven & Build Tools"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/maven-build/maven-repository-local-central-remote/
id: MVN-019
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Dependencies, pom.xml, Maven Overview
used_by: Nexus / Artifactory, SNAPSHOT vs RELEASE, Maven Lifecycle
related: Nexus / Artifactory, SNAPSHOT vs RELEASE, Maven Dependencies
tags:
  - maven
  - build-tools
  - dependencies
  - repository
  - java
  - intermediate
---

⚡ TL;DR - Maven resolves dependencies from a tiered cache: local disk cache first (`~/.m2/repository`), then a configured remote repository (your company Nexus/Artifactory), then Maven Central on the internet. Understanding this tier prevents "works on my machine" build failures and CI download storms.

| #1078           | Category: Maven & Build Tools (Java)                         | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Dependencies, pom.xml, Maven Overview                  |                 |
| **Used by:**    | Nexus / Artifactory, SNAPSHOT vs RELEASE, Maven Lifecycle    |                 |
| **Related:**    | Nexus / Artifactory, SNAPSHOT vs RELEASE, Maven Dependencies |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every Java project manually downloads and manages JAR files. JARs live in version-controlled directories or shared file servers. Upgrading a library means manually finding the new JAR, verifying checksums, updating all projects that use it. Transitive dependencies (the library's own dependencies) must be manually tracked and downloaded. This is the pre-Maven world - it was exhausting.

**THE BREAKING POINT:**
As Java ecosystems grew - Spring, Hibernate, Apache Commons - with hundreds of transitively-linked JARs, manual dependency management became untenable. A single Spring web app might require 60+ JARs, each with its own transitive chain.

**THE INVENTION MOMENT:**
Maven repositories provide a standardized location structure for artifacts (JARs, POMs, sources, javadoc) identified by `groupId:artifactId:version`. Maven's build lifecycle automatically downloads, caches, and resolves them - with a simple 3-tier lookup strategy: local → configured remote → Central.

---

### 📘 Textbook Definition

A **Maven repository** is a directory-structured store of Maven artifacts (JARs, POMs, checksums) organized by `groupId/artifactId/version`. Maven operates with three repository tiers: the **local repository** (`~/.m2/repository` by default) is a per-developer disk cache; **remote repositories** are network-accessible servers (Nexus, Artifactory, or custom) configured in `settings.xml` or `pom.xml`; **Maven Central** (`https://repo.maven.apache.org/maven2`) is the global public default remote repository. Maven resolves artifacts by checking local first, then remotes in configured order, caching downloads locally for future use.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Maven checks your disk cache → your company proxy → the internet (Central) - in that order, and caches each download locally.

**One analogy:**

> A bookstore lookup: first check your own bookshelf (local), then the local library branch (remote/Nexus), then order from the national library system (Central). Once you have a book, it stays on your shelf.

**One insight:**
The local repository is both a cache and a deployment target. `mvn install` publishes your artifact to `~/.m2` - making it available to other local projects that depend on it without a remote server.

---

### 🔩 First Principles Explanation

**THE THREE TIERS:**

```
Dependency Request (pom.xml)
        │
        ▼
[1] LOCAL REPOSITORY: ~/.m2/repository
    ├── exists? → use it (done)
    └── missing? ↓

[2] REMOTE REPOSITORIES (in order):
    ├── Company Nexus/Artifactory (mirror or configured
      repo)
    │   ├── exists? → download, cache locally, use
    │   └── missing? ↓
    └── Maven Central (default, always last)
        ├── exists? → download, cache locally, use
        └── missing? → BUILD FAILURE
```

**LOCAL REPOSITORY:**
Default: `~/.m2/repository`
Customizable in `~/.m2/settings.xml`:

```xml
<settings>
  <localRepository>D:/maven-cache</localRepository>
</settings>
```

Structure:

```
~/.m2/repository/
  com/google/guava/guava/32.0-jre/
    guava-32.0-jre.jar
    guava-32.0-jre.pom
    guava-32.0-jre.jar.sha1
```

**REMOTE REPOSITORY CONFIGURATION:**

```xml
<!-- In pom.xml (project-specific) -->
<repositories>
  <repository>
    <id>my-company-nexus</id>
    <url>https://nexus.mycompany.com/repository/maven-public/</url>
  </repository>
</repositories>

<!-- In settings.xml (global, overrides pom.xml repos) -->
<mirrors>
  <mirror>
    <id>nexus-mirror</id>
    <mirrorOf>*</mirrorOf>  <!-- intercept ALL remote lookups -->
    <url>https://nexus.mycompany.com/repository/maven-public/</url>
  </mirror>
</mirrors>
```

**THE TRADE-OFFS:**

**Gain:** Network efficiency (download once, use many times); offline builds after first download; corporate security (proxy controls which artifacts are allowed); auditability (everything flows through your Nexus).

**Cost:** Stale local cache causes subtle SNAPSHOT bugs; cold CI builds download everything; local `~/.m2` can grow to several GBs; air-gapped environments require manual repository seeding.

---

### 🧪 Thought Experiment

**SETUP:**
Your CI pipeline runs `mvn package` on a fresh Docker container with no local repository. The build downloads 200 artifacts from Maven Central. It takes 4 minutes, mostly on downloads.

**APPROACHES:**

1. Mount a shared NFS `.m2` directory across all CI containers (shared local cache)
2. Set up Nexus as a proxy/mirror - containers download from Nexus, which caches from Central
3. Bake a pre-populated `.m2` into the Docker base image

**TRADE-OFFS:**
Option 1: Simple, but NFS contention; race conditions writing cache simultaneously.
Option 2: Standard enterprise approach; adds an infrastructure component.
Option 3: Fast, but image grows large; requires rebuilding image on dependency changes.

**THE LESSON:**
The three-tier model is designed for corporate optimization. Nexus/Artifactory fills the "remote" tier to avoid repeated Central downloads and to enable security controls.

---

### 🧠 Mental Model / Analogy

> Maven repositories work like a layered DNS cache. When your browser looks up `example.com`, it checks: OS cache → local router cache → ISP DNS server → root DNS. Each level caches results for future requests. Maven's lookup is the same hierarchy - but for JAR files instead of domain names.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Maven downloads JARs from the internet and stores them in your `~/.m2/repository` folder so it doesn't download them again.

**Level 2:** There are three tiers: local disk (`~/.m2`), your company's proxy server (Nexus/Artifactory), and Maven Central. Maven checks each in order, caches what it finds locally.

**Level 3:** `<repositories>` in `pom.xml` adds project-specific remote repos. `<mirrors>` in `settings.xml` intercepts and redirects repo lookups - a mirror with `mirrorOf=*` routes all requests through one server. `mvn install` deploys to local; `mvn deploy` deploys to the configured remote repository in `<distributionManagement>`.

**Level 4:** SNAPSHOT artifacts bypass the local cache check after the configured update interval (default 24h), re-fetching from remote to get the latest `-SNAPSHOT` build. Use `-U` (`--update-snapshots`) to force re-check. `<updatePolicy>` in `<repository>` config controls this: `always`, `daily`, `interval:N`, `never`.

---

### ⚙️ How It Works (Mechanism)

```bash
# Inspect local repo structure
ls ~/.m2/repository/org/springframework/spring-core/6.1.1/
# spring-core-6.1.1.jar
# spring-core-6.1.1.pom
# spring-core-6.1.1.jar.sha1
# spring-core-6.1.1.pom.sha1

# Force re-download of all snapshots
mvn clean install -U

# Offline mode: use only local cache, fail if missing
mvn clean install -o

# Purge specific artifact from local cache
mvn dependency:purge-local-repository -DmanualInclude="com.google.guava:guava"

# Show effective repository configuration
mvn help:effective-settings
```

---

### 💻 Code Example

**`settings.xml` with corporate mirror and credentials:**

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0">

  <!-- All remote lookups routed through Nexus -->
  <mirrors>
    <mirror>
      <id>nexus-central</id>
      <mirrorOf>central</mirrorOf>
      <url>https://nexus.mycompany.com/repository/maven-central/</url>
    </mirror>
    <mirror>
      <id>nexus-all</id>
      <mirrorOf>*</mirrorOf>
      <url>https://nexus.mycompany.com/repository/maven-public/</url>
    </mirror>
  </mirrors>

  <!-- Credentials for private repositories -->
  <servers>
    <server>
      <id>nexus-releases</id>
      <username>ci-user</username>
      <password>${env.NEXUS_PASSWORD}</password>  <!-- avoid plaintext -->
    </server>
    <server>
      <id>nexus-snapshots</id>
      <username>ci-user</username>
      <password>${env.NEXUS_PASSWORD}</password>
    </server>
  </servers>

</settings>
```

**`pom.xml` `<distributionManagement>` for `mvn deploy`:**

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

| Repository Type         | Location       | Updated When                  | Use Case                       |
| ----------------------- | -------------- | ----------------------------- | ------------------------------ |
| Local (`~/.m2`)         | Developer disk | On download / `mvn install`   | Personal cache + local publish |
| Corporate proxy (Nexus) | Company server | Download from Central on miss | Security, speed, audit         |
| Maven Central           | Internet       | Static (immutable releases)   | Public OSS artifacts           |
| Custom remote           | Any server     | As configured                 | Private/proprietary artifacts  |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                            |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `mvn install` publishes to Maven Central                 | It publishes to local `~/.m2` only; use `mvn deploy` for remote                    |
| Local cache is always fresh                              | SNAPSHOTs may be stale; RELEASEs are never re-downloaded once cached               |
| `<repositories>` in pom.xml is sufficient for all setups | CI environments should use `settings.xml` mirrors to centralize control            |
| Deleting `~/.m2` is always safe                          | Correct, but slow CI cold start follows; also loses locally `install`-ed artifacts |

---

### 🚨 Failure Modes & Diagnosis

**"Could not find artifact" - build fails on CI but works locally**

**Root Cause:** Artifact in local `~/.m2` on dev machine; not in CI's local/remote repos; or CI mirror doesn't have the artifact.

**Diagnosis:**

```bash
mvn dependency:resolve -Dverbose
# shows where each artifact was resolved from
```

**Fix:** Ensure CI uses a Nexus/Artifactory proxy that proxies Maven Central; or `mvn deploy` the custom artifact to the remote repo.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Dependencies`, `pom.xml`, `Maven Overview`

**Builds On This:** `Nexus / Artifactory`, `SNAPSHOT vs RELEASE`

**Related Patterns:** `Nexus / Artifactory`, `SNAPSHOT vs RELEASE`, `Maven Dependencies`

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LOCAL        │ ~/.m2/repository - disk cache            │
├──────────────┼──────────────────────────────────────────┤
│ REMOTE       │ Nexus/Artifactory - corporate proxy      │
├──────────────┼──────────────────────────────────────────┤
│ CENTRAL      │ repo.maven.apache.org - public OSS       │
├──────────────┼──────────────────────────────────────────┤
│ INSTALL      │ mvn install → local only                 │
├──────────────┼──────────────────────────────────────────┤
│ DEPLOY       │ mvn deploy → remote (Nexus)              │
├──────────────┼──────────────────────────────────────────┤
│ FORCE UPDATE │ mvn -U (re-fetch SNAPSHOTs)              │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer's `~/.m2` has `my-library:1.0.0-SNAPSHOT` from last week's local build. A newer SNAPSHOT was deployed to Nexus yesterday. The developer runs `mvn package` - which SNAPSHOT version does their build use? How would you force the use of the latest SNAPSHOT?

**Q2.** Your organisation's security policy prohibits direct internet access from build agents. How do you configure Maven to ensure all artifact downloads are routed through your corporate Nexus proxy, even for transitive dependencies not yet cached in Nexus?
