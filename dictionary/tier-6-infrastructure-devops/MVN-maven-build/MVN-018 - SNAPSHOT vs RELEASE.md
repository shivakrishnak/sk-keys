---
version: 1
layout: default
title: "SNAPSHOT vs RELEASE"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /maven-build/snapshot-vs-release/
id: MVN-023
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Repository (local, central, remote), Maven Dependencies, Maven Lifecycle
used_by: Maven Release Plugin, Nexus / Artifactory, Build Reproducibility
related: Maven Repository (local, central, remote), Maven Release Plugin, Build Reproducibility
tags:
  - maven
  - build-tools
  - versioning
  - snapshot
  - release
  - java
  - intermediate
---

# MVN-016 - SNAPSHOT vs RELEASE

⚡ TL;DR - A SNAPSHOT version (`1.0.0-SNAPSHOT`) is a mutable, always-latest development build that Maven re-downloads periodically; a RELEASE version (`1.0.0`) is immutable and cached forever. This distinction governs reproducibility, CI cache behaviour, and the deployment workflow.

| #1080           | Category: Maven & Build Tools (Java)                                                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Repository (local, central, remote), Maven Dependencies, Maven Lifecycle         |                 |
| **Used by:**    | Maven Release Plugin, Nexus / Artifactory, Build Reproducibility                       |                 |
| **Related:**    | Maven Repository (local, central, remote), Maven Release Plugin, Build Reproducibility |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You want to publish a library to your team while still developing it. Without a SNAPSHOT mechanism, you'd need to keep incrementing version numbers (`1.0.0-beta1`, `1.0.0-beta2`, …) for each development build, and consumers would need to manually update their `pom.xml` every day to get the latest version.

**THE BREAKING POINT:**
Active development produces dozens of builds per day across multiple branches. Manual version management during active development is noise - not signal. You want "give me the latest work-in-progress build of this library" semantics, not "give me exactly this immutable version."

**THE INVENTION MOMENT:**
Maven's SNAPSHOT convention: append `-SNAPSHOT` to any version and Maven automatically re-fetches the artifact from the repository at configurable intervals. Once development stabilises, run the Maven Release Plugin to strip `-SNAPSHOT`, tag the source, and publish an immutable release.

---

### 📘 Textbook Definition

In Maven's versioning model, a **SNAPSHOT version** is identified by the suffix `-SNAPSHOT` (e.g., `2.1.0-SNAPSHOT`) and represents a mutable, in-development artifact. Maven re-downloads SNAPSHOTs from remote repositories when they are newer than the cached local copy (by default, once per day per repository). Each deployed SNAPSHOT is internally timestamped (e.g., `2.1.0-20241201.143000-5`), with `maven-metadata.xml` tracking the latest. A **RELEASE version** (e.g., `2.1.0`) is immutable: once downloaded and cached in `~/.m2`, Maven never re-downloads it. RELEASE versions are suitable for production dependencies; SNAPSHOTs are for active development and inter-team collaboration.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SNAPSHOT = mutable latest dev build (auto-refreshed); RELEASE = immutable, versioned, cached forever.

**One analogy:**

> SNAPSHOT is like a shared Google Doc - everyone sees the latest edits automatically. RELEASE is like a printed, bound report - fixed and unchanging once distributed.

**One insight:**
SNAPSHOT coupling between teams is a double-edged sword: it enables rapid integration but means one team's broken deploy can break another team's build within 24 hours - with no explicit version change visible in the consuming POM.

---

### 🔩 First Principles Explanation

**HOW SNAPSHOT RESOLUTION WORKS:**

```
Local Cache: ~/.m2/.../my-lib/2.0.0-SNAPSHOT/
  my-lib-2.0.0-SNAPSHOT.jar (timestamp: yesterday)

Build request for my-lib:2.0.0-SNAPSHOT:
  1. Check local cache → found, but check update policy
  2. Update policy = daily → last checked > 24h ago → re-fetch
  3. Remote has newer timestamp → download new SNAPSHOT
  4. Update local cache
  5. Use new JAR

Next build today:
  1. Check local cache → found
  2. Update policy = daily → last checked < 24h ago → use cached
```

**HOW SNAPSHOTS ARE STORED IN NEXUS:**

```
nexus/maven-snapshots/com/example/my-lib/2.0.0-SNAPSHOT/
  my-lib-2.0.0-20241201.143000-1.jar   ← deploy #1
  my-lib-2.0.0-20241201.160000-2.jar   ← deploy #2
  my-lib-2.0.0-20241202.090000-3.jar   ← deploy #3 (latest)
  maven-metadata.xml                    ← points to #3
```

**HOW RELEASES ARE IMMUTABLE:**
Nexus and Artifactory enforce immutability on release repositories - attempting to re-deploy `1.0.0` after it's been published returns `409 Conflict`. This is by policy design: if `1.0.0` is in a project that shipped 6 months ago, you need to trust that `1.0.0` today is byte-for-byte identical to `1.0.0` at ship time.

**THE TRADE-OFFS:**
**SNAPSHOT gains:** Team integration during active development; no version churn in consuming POMs; "latest" semantics for CI pipelines.
**SNAPSHOT costs:** Non-deterministic builds (same POM, different results 24h apart); SNAPSHOT dependencies in production = reproducibility violation; stale SNAPSHOT cache causes confusing "works in CI, not locally" bugs.
**RELEASE gains:** Reproducibility; immutability guarantees; safe for production; cacheable forever.
**RELEASE costs:** Requires formal release process; can't be updated (must create new version for any change).

---

### 🧪 Thought Experiment

**SETUP:**
Team A owns `auth-service-client:3.0.0-SNAPSHOT`. Team B depends on it. Team A deploys a breaking API change to their SNAPSHOT at 11 AM. Team B's CI runs `mvn package` at 11:05 AM - it picks up the new SNAPSHOT and the build fails with a compilation error. Team B is blocked, but no version in their `pom.xml` changed.

**QUESTIONS:**

1. How would you detect that a SNAPSHOT update caused this failure?
2. What versioning discipline prevents this scenario?
3. Is there a valid use case where SNAPSHOT inter-team dependency is acceptable?

**THE LESSON:**
SNAPSHOT dependencies between teams (not just within a team/module) create invisible coupling. Best practice: SNAPSHOT within a team; RELEASE at team boundaries.

---

### 🧠 Mental Model / Analogy

> SNAPSHOT is the `latest` Docker tag: convenient for development, dangerous for production because it silently changes. RELEASE is a specific Docker image digest (`sha256:abc123...`): immutable, reproducible, safe to deploy.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** `1.0.0-SNAPSHOT` means "work in progress - get the latest." `1.0.0` means "this is the official release - fixed forever."

**Level 2:** Maven re-downloads SNAPSHOTs periodically (default: once per day). RELEASEs are downloaded once and cached forever. `-U` flag forces SNAPSHOT re-download.

**Level 3:** Nexus stores multiple timestamped SNAPSHOT builds; `maven-metadata.xml` tracks the latest pointer. Nexus enforces release repo immutability. `<repositories>` can configure `<snapshots><enabled>true/false</enabled>` to control which repos serve SNAPSHOTs.

**Level 4:** Maven Release Plugin (`mvn release:prepare release:perform`) automates the SNAPSHOT→RELEASE transition: validates no SNAPSHOT dependencies, strips `-SNAPSHOT`, tags in SCM, deploys release, bumps to next SNAPSHOT. CI workflows should have a gate: no SNAPSHOT dependencies in artifacts destined for production deployment.

---

### ⚙️ How It Works (Mechanism)

```bash
# Force re-download of all SNAPSHOTs right now
mvn clean install -U

# Build offline: use only local cache (fail if SNAPSHOT is missing/stale)
mvn clean install -o

# Check what version is in local cache
ls ~/.m2/repository/com/example/my-lib/2.0.0-SNAPSHOT/

# Detect SNAPSHOT dependencies (useful for pre-release validation)
mvn versions:display-dependency-updates | grep SNAPSHOT
# Or:
mvn dependency:list | grep SNAPSHOT
```

---

### 💻 Code Example

**Declaring SNAPSHOT vs RELEASE dependency:**

```xml
<!-- SNAPSHOT: for active development integration -->
<dependency>
  <groupId>com.mycompany</groupId>
  <artifactId>shared-utils</artifactId>
  <version>2.0.0-SNAPSHOT</version>  <!-- re-downloaded daily -->
</dependency>

<!-- RELEASE: for stable, production use -->
<dependency>
  <groupId>com.mycompany</groupId>
  <artifactId>shared-utils</artifactId>
  <version>2.0.0</version>  <!-- downloaded once, cached forever -->
</dependency>
```

**Controlling SNAPSHOT update policy:**

```xml
<repositories>
  <repository>
    <id>nexus-snapshots</id>
    <url>https://nexus.mycompany.com/repository/maven-snapshots/</url>
    <snapshots>
      <enabled>true</enabled>
      <updatePolicy>always</updatePolicy>  <!-- always | daily | interval:60 | never -->
    </snapshots>
    <releases>
      <enabled>false</enabled>  <!-- snapshots repo: no releases -->
    </releases>
  </repository>
</repositories>
```

**Enforcer rule: no SNAPSHOT deps in release builds:**

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-enforcer-plugin</artifactId>
  <executions>
    <execution>
      <id>no-snapshots-in-release</id>
      <goals><goal>enforce</goal></goals>
      <configuration>
        <rules>
          <requireReleaseDeps>
            <message>No SNAPSHOT dependencies allowed in release builds!</message>
            <failWhenParentIsSnapshot>true</failWhenParentIsSnapshot>
          </requireReleaseDeps>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

---

### ⚖️ Comparison Table

| Property                | SNAPSHOT                 | RELEASE                              |
| ----------------------- | ------------------------ | ------------------------------------ |
| Mutable                 | Yes (re-deployed freely) | No (immutable once published)        |
| Cache behaviour         | Re-checked periodically  | Cached forever (never re-downloaded) |
| Suitable for production | No                       | Yes                                  |
| Suitable for active dev | Yes                      | No (too much version churn)          |
| Maven Central accepts   | No                       | Yes                                  |
| Repository type (Nexus) | Snapshots repo           | Releases repo                        |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                              |
| --------------------------------------------- | ------------------------------------------------------------------------------------ |
| SNAPSHOT means "unstable code"                | It means "mutable version" - the code quality is irrelevant; the artifact is mutable |
| `-U` is always needed for SNAPSHOTs           | `-U` only needed if within the update interval (default: 24h) and you need fresh     |
| Releasing removes SNAPSHOT from all consumers | Consumers must manually update from `X-SNAPSHOT` to `X` in their `pom.xml`           |
| Maven Central accepts SNAPSHOTs               | Central does not host SNAPSHOTs (oss.sonatype.org does, separately)                  |

---

### 🚨 Failure Modes & Diagnosis

**"Stale SNAPSHOT" - CI gets different results than developer**

**Root Cause:** Developer has a locally `install`-ed SNAPSHOT that is newer than Nexus, or CI re-downloaded a newer SNAPSHOT from Nexus than developer's cached version.

**Diagnosis:**

```bash
# Check timestamp of local SNAPSHOT
ls -la ~/.m2/repository/com/example/my-lib/2.0.0-SNAPSHOT/
# Compare with what Nexus shows in its metadata
```

**Fix:** Align on update policy; or migrate to RELEASE at integration boundaries.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Repository (local, central, remote)`, `Maven Dependencies`, `Maven Lifecycle`

**Builds On This:** `Maven Release Plugin`, `Build Reproducibility`

**Related Patterns:** `Maven Repository (local, central, remote)`, `Maven Release Plugin`, `Build Reproducibility`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SNAPSHOT     │ Suffix: -SNAPSHOT | Mutable | Dev use    │
├──────────────┼───────────────────────────────────────────┤
│ RELEASE      │ No suffix | Immutable | Production use    │
├──────────────┼───────────────────────────────────────────┤
│ CACHE POLICY │ SNAPSHOT: re-checked daily | RELEASE: ∞  │
├──────────────┼───────────────────────────────────────────┤
│ FORCE UPDATE │ mvn -U (re-fetch SNAPSHOTs now)          │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ No SNAPSHOTs in production artifacts      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "SNAPSHOT = latest; RELEASE = forever"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your build server's `.m2` cache is shared across all 10 CI agents. One agent `mvn install`s a local SNAPSHOT that's broken (compilation errors checked in accidentally). All other agents pick it up within the hour. How does local-repository sharing amplify SNAPSHOT instability, and how would you architect CI to prevent this?

**Q2.** You are about to cut the `v2.0.0` release of your library. Your `pom.xml` still has `<version>2.0.0-SNAPSHOT</version>`. Walk through the steps required to promote this to a RELEASE version - both manually and using the Maven Release Plugin. What does the plugin validate before allowing the release to proceed?
