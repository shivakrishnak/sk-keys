---
layout: default
title: "Gradle Build Cache"
parent: "Maven & Build Tools (Java)"
nav_order: 23
permalink: /maven-build/gradle-build-cache/
number: "MVN-023"
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Gradle Incremental Build, Gradle Tasks, Gradle Build Script
used_by: Build Performance Optimization, Build Reproducibility
related: Gradle Incremental Build, Build Reproducibility, Build Performance Optimization
tags:
  - gradle
  - build-tools
  - build-cache
  - performance
  - java
  - deep-dive
---

# MVN-023 — Gradle Build Cache

⚡ TL;DR — Gradle's build cache stores task outputs keyed by a fingerprint of all inputs. If a developer or CI agent requests the same task with identical inputs, outputs are restored from the cache — the task never executes again. Remote build cache extends this sharing across the whole team and CI fleet.

| #1088           | Category: Maven & Build Tools (Java)                                            | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Gradle Incremental Build, Gradle Tasks, Gradle Build Script                     |                 |
| **Used by:**    | Build Performance Optimization, Build Reproducibility                           |                 |
| **Related:**    | Gradle Incremental Build, Build Reproducibility, Build Performance Optimization |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Incremental build (`UP-TO-DATE`) only helps if _this machine_ previously ran the task successfully. CI agents are typically ephemeral — fresh containers, no `.gradle/` state. Every CI run is a full cold build. Developer pulls a branch that CI already built — they recompile everything locally even though CI already produced the exact same outputs.

**THE BREAKING POINT:**
Large teams with fast CI cycles waste enormous compute. If 20 developers check out the same commit and build locally, each recompiles the same 10,000 class files independently. 20x redundant work.

**THE INVENTION MOMENT:**
Gradle build cache: after a task completes, its outputs are stored in a cache keyed by a stable input fingerprint (hash of all inputs: source files, compile classpath, Gradle version, JDK version, task configuration). Any other build with the same input fingerprint retrieves the cached output instead of executing the task. A remote build cache server extends this across all machines on the team.

---

### 📘 Textbook Definition

The **Gradle build cache** is a content-addressable store of task outputs, indexed by a stable hash of all task inputs (the **build cache key**). The local build cache (`~/.gradle/caches/build-cache/`) stores outputs on the current machine. The remote build cache (Gradle Enterprise/Develocity, or a custom HTTP server) stores outputs accessible by any machine. When Gradle executes a cacheable task, it computes the cache key from all declared inputs; if an entry exists in the cache, outputs are restored without executing the task (reported as `FROM-CACHE`). Tasks must be marked `@CacheableTask` (or enable `outputs.cacheIf { true }`) to participate in the build cache.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Build cache = "has anyone with these exact same inputs already run this task? If yes, use their outputs."

**One analogy:**

> A shared printer queue that remembers all previously printed documents. If you send the same document someone else printed yesterday (identical content), the printer retrieves the printed copy from a storage room instead of printing again. No ink used, instant delivery.

**One insight:**
Incremental build is local and temporal ("did I run this before on this machine?"). Build cache is global and persistent ("has anyone, anywhere, run this task with these exact inputs?"). The build cache survives `gradle clean`, new CI containers, and fresh developer checkouts.

---

### 🔩 First Principles Explanation

**CACHE KEY COMPUTATION:**

```
Cache key for :compileJava = hash of:
  ├── All .java source file contents
  ├── Compile classpath contents (JAR file hashes)
  ├── Compiler configuration (source/target version, flags)
  ├── Gradle version
  ├── JDK version and vendor
  └── Task implementation (plugin code hash)
```

**CACHE HIT FLOW:**

```
./gradlew compileJava
  │
  ▼
Compute cache key: SHA-abc123
  │
  ▼
Check local cache → not found
Check remote cache → FOUND (CI ran this 2 hours ago with same sources)
  │
  ▼
Download outputs from remote cache → restore to build/classes/
  │
  ▼
> Task :compileJava FROM-CACHE
```

**ENABLING THE BUILD CACHE:**

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        removeUnusedEntriesAfterDays = 30
    }
    remote<HttpBuildCache> {
        url = uri("https://gradle-cache.mycompany.com/cache/")
        credentials {
            username = providers.environmentVariable("GRADLE_CACHE_USER").get()
            password = providers.environmentVariable("GRADLE_CACHE_TOKEN").get()
        }
        isPush = System.getenv("CI") != null  // only CI pushes; devs only pull
    }
}
```

**THE TRADE-OFFS:**
**Gain:** Eliminates redundant work across the entire team; CI warm-up time drops dramatically; `FROM-CACHE` builds complete in seconds for unchanged work; survives `clean`.
**Cost:** Remote cache server infrastructure (Develocity is paid; custom HTTP cache adds ops burden); cache key correctness critical (non-deterministic task outputs cause cache poisoning); network overhead for cache upload/download; disk space management for local and remote cache.

---

### 🧪 Thought Experiment

**SETUP:**
Your Gradle task generates a JAR and embeds the current timestamp in the MANIFEST.MF:

```kotlin
tasks.named<Jar>("jar") {
    manifest {
        attributes("Build-Time" to System.currentTimeMillis())  // BAD!
    }
}
```

**PROBLEM:**
The timestamp changes every execution. The cache key includes task outputs, but more importantly — two builds with identical source code now produce different outputs. If you push to cache: every CI run uploads a new entry. If the task is `@CacheableTask`, two builds with identical inputs produce different outputs (non-reproducible) — cache entries accumulate with no hits.

**FIX:**

```kotlin
manifest {
    // Use a deterministic value, or omit the timestamp
    attributes("Build-Version" to project.version)
}
```

**THE LESSON:**
Non-deterministic outputs defeat the build cache. Task outputs must be reproducible for the same inputs to benefit from caching.

---

### 🧠 Mental Model / Analogy

> The build cache is the Git object store for build outputs. Just as Git stores file content by SHA hash (two identical files = one stored object, retrieved by hash), Gradle stores task outputs by input fingerprint hash. Any build that produces the same inputs will retrieve the same stored output — regardless of when or where it was built.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Gradle stores build outputs in a cache. If another build runs the same task with the same inputs (same source files, same JDK), it gets the outputs from cache instead of running again.

**Level 2:** Each task has a cache key computed from all its declared inputs. A remote cache server shares this across all team members and CI. `FROM-CACHE` in output means "retrieved from cache."

**Level 3:** `@CacheableTask` annotation marks a task as safe to cache. For this to work, the task must be deterministic (same inputs → same outputs, always). Non-deterministic outputs (timestamps, PIDs, random seeds) must be removed or moved to non-cached fields.

**Level 4:** Gradle Enterprise / Develocity provides a managed remote build cache with build scan integration. Custom HTTP build cache server: implement the Gradle Build Cache API (simple HTTP PUT/GET by cache key). Cache relocation: task outputs often contain absolute paths — Gradle handles path normalization automatically for standard tasks (file paths in compiled Java bytecode are relative); custom tasks must handle this manually.

---

### ⚙️ How It Works (Mechanism)

```bash
# Enable local build cache (also in gradle.properties or settings.gradle.kts)
./gradlew build --build-cache

# Or add to gradle.properties:
org.gradle.caching=true

# Check if a task was restored from cache
./gradlew build --build-cache 2>&1 | grep "FROM-CACHE"

# Clear local build cache
rm -rf ~/.gradle/caches/build-cache/

# Debug cache misses (why wasn't this a cache hit?)
./gradlew :compileJava --build-cache --info 2>&1 | grep -A5 "Build cache"
```

---

### 💻 Code Example

**Making a custom task cacheable:**

```kotlin
// Annotate with @CacheableTask and use @PathSensitive for file inputs
@CacheableTask
abstract class GenerateApiDocs : DefaultTask() {

    @get:InputFiles
    @get:PathSensitive(PathSensitivity.RELATIVE)  // normalize paths for cache key
    abstract val sourceFiles: ConfigurableFileCollection

    @get:Input
    abstract val apiVersion: Property<String>

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun generate() {
        // generate docs into outputDir
        // must be deterministic: same inputs → same outputs always
    }
}

// Register:
tasks.register<GenerateApiDocs>("generateApiDocs") {
    sourceFiles.from(sourceSets.main.get().allJava)
    apiVersion.set(project.version.toString())
    outputDir.set(layout.buildDirectory.dir("docs/api"))
    outputs.cacheIf { true }
}
```

**`gradle.properties` for all-builds cache config:**

```properties
# Enable local build cache globally
org.gradle.caching=true

# Enable configuration cache (Gradle 8+)
org.gradle.configuration-cache=true

# Enable parallel execution
org.gradle.parallel=true
```

---

### ⚖️ Comparison Table

| Feature                      | Incremental Build          | Build Cache                          |
| ---------------------------- | -------------------------- | ------------------------------------ |
| Scope                        | Local, this machine        | Local + remote, any machine          |
| Survives `clean`             | No (clean deletes outputs) | Yes (cache independent of build dir) |
| Survives new container       | No                         | Yes (remote cache)                   |
| Survives different developer | No                         | Yes (remote cache)                   |
| Requires network             | No                         | Remote cache yes; local no           |
| Task marker                  | UP-TO-DATE                 | FROM-CACHE                           |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                           |
| ---------------------------------------------- | --------------------------------------------------------------------------------- |
| Build cache and incremental build are the same | Different mechanisms with different scopes; complementary                         |
| All tasks benefit from build cache             | Only `@CacheableTask`-annotated tasks (or `outputs.cacheIf { true }`) participate |
| Non-deterministic outputs only waste space     | They also cause cache poisoning (bad outputs served to other builds)              |
| Remote build cache requires Gradle Enterprise  | Any HTTP server implementing the Gradle cache protocol works (or self-host)       |

---

### 🚨 Failure Modes & Diagnosis

**Cache miss every time (no FROM-CACHE)**

**Root Cause:** Non-deterministic input (timestamp, environment variable not declared but read inside task action).

**Diagnosis:**

```bash
./gradlew :taskName --build-cache --info 2>&1 | grep "cache"
# Build scan (Gradle Enterprise): shows exact cache key and what changed
```

**Fix:** Remove non-deterministic elements from task outputs; declare all environment-based inputs explicitly so they become part of the cache key.

---

### 🔗 Related Keywords

**Prerequisites:** `Gradle Incremental Build`, `Gradle Tasks`, `Gradle Build Script`

**Builds On This:** `Build Performance Optimization`, `Build Reproducibility`

**Related Patterns:** `Gradle Incremental Build`, `Build Reproducibility`, `Build Performance Optimization`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY          │ Hash of all task inputs                   │
├──────────────┼───────────────────────────────────────────┤
│ LOCAL        │ ~/.gradle/caches/build-cache/             │
├──────────────┼───────────────────────────────────────────┤
│ REMOTE       │ HTTP server or Gradle Enterprise          │
├──────────────┼───────────────────────────────────────────┤
│ ENABLE       │ --build-cache or org.gradle.caching=true  │
├──────────────┼───────────────────────────────────────────┤
│ CACHEABLE    │ @CacheableTask + deterministic outputs    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Store outputs by input hash; share all"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team uses a shared remote build cache. CI pushes outputs to the cache. Developers pull from it. After a week, you discover developers are never getting `FROM-CACHE` hits — always full rebuilds. What are the most likely causes, and how would you diagnose them?

**Q2.** Explain the difference in what happens after `./gradlew clean` when (a) only incremental build is enabled, and (b) build cache is also enabled. Why does `clean` not invalidate the build cache?
