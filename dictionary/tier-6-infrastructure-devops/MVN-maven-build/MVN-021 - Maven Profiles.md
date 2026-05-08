---
layout: default
title: "Maven Profiles"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /maven-build/maven-profiles/
id: MVN-021
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: pom.xml, Maven Lifecycle, Maven Plugins
used_by: Maven Multi-Module Project, Build Performance Optimization, CI-CD
related: Maven Multi-Module Project, Maven Wrapper (mvnw), Build Performance Optimization
tags:
  - maven
  - build-tools
  - profiles
  - configuration
  - java
  - deep-dive
---

# MVN-021 - Maven Profiles

⚡ TL;DR - Maven profiles conditionally activate sets of POM configuration (dependencies, plugins, properties, resources) based on environment, JDK version, OS, or explicit flags - enabling a single `pom.xml` to drive development, CI, and production builds with different behaviours.

| #1081           | Category: Maven & Build Tools (Java)                                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | pom.xml, Maven Lifecycle, Maven Plugins                                          |                 |
| **Used by:**    | Maven Multi-Module Project, Build Performance Optimization, CI-CD                |                 |
| **Related:**    | Maven Multi-Module Project, Maven Wrapper (mvnw), Build Performance Optimization |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have one `pom.xml`. Local development needs H2 in-memory database; CI needs PostgreSQL. Production packaging excludes test utilities; the dev build includes them. You end up with multiple `pom.xml` variants, checked-in separately - `pom-dev.xml`, `pom-ci.xml`, `pom-prod.xml` - manually kept in sync. Adding a new plugin means updating all three.

**THE BREAKING POINT:**
Build configuration that varies by environment creates fork divergence - the CI build uses different settings than the developer's build, silently. Bugs that exist in CI but not locally, or vice versa, are expensive and demoralising.

**THE INVENTION MOMENT:**
Maven profiles allow a single `pom.xml` to declare named configuration blocks, each activated by explicit flag, environment variable, JDK version, or OS. The build system is unified; only the activated profile varies.

---

### 📘 Textbook Definition

A **Maven profile** is a named block of POM configuration (`<properties>`, `<dependencies>`, `<plugins>`, `<repositories>`, `<build>`, `<reporting>`) declared inside `<profiles>` in `pom.xml`, `settings.xml`, or `~/.m2/settings.xml`. Profiles are activated by: explicit command-line activation (`-P profileId`); default activation (`<activation><activeByDefault>true</activeByDefault></activation>`); environment conditions (JDK version, OS, presence of a file, or a property value). When active, the profile's configuration is merged into the effective POM, overriding or extending the base configuration.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Profiles are named "if this condition, apply this extra config" blocks in your POM.

**One analogy:**

> A restaurant menu with dietary-modification options: "add vegan profile" swaps the default burger for a plant patty - same meal, same kitchen, different ingredients activated by a single request.

**One insight:**
Profile activation replaces the need for multiple `pom.xml` variants. The build varies by condition, not by file - keeping the source of truth unified.

---

### 🔩 First Principles Explanation

**PROFILE STRUCTURE:**

```xml
<profiles>
  <profile>
    <id>production</id>           <!-- unique identifier -->
    <activation>
      <!-- How this profile is triggered -->
      <property>
        <name>env</name>
        <value>prod</value>      <!-- activated when -Denv=prod -->
      </property>
    </activation>
    <properties>
      <db.url>jdbc:postgresql://prod-db:5432/mydb</db.url>
    </properties>
    <dependencies>
      <!-- production-only dependencies -->
    </dependencies>
    <build>
      <plugins>
        <!-- production-only plugin config -->
      </plugins>
    </build>
  </profile>
</profiles>
```

**ACTIVATION TYPES:**

```xml
<!-- 1. Command-line explicit: mvn package -Pproduction -->
<activation><activeByDefault>false</activeByDefault></activation>

<!-- 2. Default: always active unless another profile activates -->
<activation><activeByDefault>true</activeByDefault></activation>

<!-- 3. JDK version -->
<activation><jdk>11</jdk></activation>
<activation><jdk>[11,17)</jdk></activation>  <!-- range -->

<!-- 4. OS -->
<activation>
  <os><family>Windows</family></os>
</activation>

<!-- 5. Property presence -->
<activation>
  <property><name>skipTests</name></property>
</activation>

<!-- 6. Property value -->
<activation>
  <property><name>env</name><value>ci</value></property>
</activation>

<!-- 7. File existence -->
<activation>
  <file><exists>${basedir}/src/main/resources/prod.properties</exists></file>
</activation>
```

**MERGE SEMANTICS:**
Profiles _extend_ the base POM - they don't replace it. Most elements are additive. Some elements (like `<properties>`) override individual entries; others (like `<dependencies>`) add to the list.

**THE TRADE-OFFS:**
**Gain:** Single `pom.xml` for all environments; explicit, documented variation; conditions captured in version control; profile-aware IDEs show effective configuration.
**Cost:** Implicit activation (environment or file conditions) can surprise developers who don't know a profile is active; `activeByDefault` profiles behave unexpectedly when another profile is explicitly activated (they deactivate); profiles in `settings.xml` are not visible in the project repo - creating invisible variation.

---

### 🧪 Thought Experiment

**SETUP:**
You have a profile that's `<activeByDefault>true</activeByDefault>`. Your colleague activates the `ci` profile with `-Pci`. The `activeByDefault` profile silently deactivates (Maven behaviour: `activeByDefault` is ignored when any profile is explicitly activated).

**CONSEQUENCE:**
The configuration from your `activeByDefault` profile (database properties, plugin versions) is now absent. The CI build uses neither profile's config in the expected way.

**FIX OPTIONS:**

1. Don't use `activeByDefault` - use explicit property-based activation instead
2. Combine configs: use a base profile with a marker property, not `activeByDefault`
3. Make all profiles additive and orthogonal (no exclusive mutual dependency on `activeByDefault`)

**THE LESSON:**
`activeByDefault` has a surprising interaction with explicit activation. Prefer property-based activation for predictable, composable profiles.

---

### 🧠 Mental Model / Analogy

> Maven profiles are like feature flags for build configuration. In the same way your app can have `feature.dark-mode=true` at runtime to change UI behaviour, a Maven profile can be `env=ci` at build time to change which plugins run, which dependencies are included, and which properties are set - without changing any source code.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** A profile is a named group of extra build settings. You turn it on with `-P profileName` and Maven applies those extra settings.

**Level 2:** Profiles contain `<properties>`, `<dependencies>`, and `<plugins>` blocks. They can be auto-activated by JDK version, OS, environment variable, or file presence - not just explicit flags.

**Level 3:** Profile placement: `pom.xml` (project-scoped, version-controlled), `settings.xml` (user/CI-scoped, not in repo), Maven root `settings.xml` (system-wide). The `activeByDefault` pitfall: deactivates when any profile is explicitly activated - prefer property-based activation.

**Level 4:** Profile composition: multiple profiles can be active simultaneously (`-Pprofile1,profile2`). Profiles in `settings.xml` can inject credentials or repository URLs that the project POM shouldn't contain (security separation). In multi-module projects, profiles in the root POM propagate to all modules.

---

### ⚙️ How It Works (Mechanism)

```bash
# Activate explicitly
mvn clean package -Pproduction

# Activate with property
mvn clean package -Denv=prod

# See active profiles and effective POM
mvn help:active-profiles
mvn help:effective-pom -Pproduction

# Activate multiple profiles
mvn clean deploy -Pproduction,release

# Deactivate a default profile
mvn clean package -P!default-profile
```

---

### 💻 Code Example

**Multi-environment `pom.xml` with profiles:**

```xml
<properties>
  <!-- Base / development defaults -->
  <db.driver>org.h2.Driver</db.driver>
  <db.url>jdbc:h2:mem:devdb</db.url>
</properties>

<profiles>

  <!-- CI profile: activated by property -Denv=ci -->
  <profile>
    <id>ci</id>
    <activation>
      <property><name>env</name><value>ci</value></property>
    </activation>
    <properties>
      <db.driver>org.postgresql.Driver</db.driver>
      <db.url>jdbc:postgresql://ci-postgres:5432/testdb</db.url>
    </properties>
    <dependencies>
      <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <version>42.7.0</version>
      </dependency>
    </dependencies>
  </profile>

  <!-- Release profile: skip tests, generate sources/javadoc -->
  <profile>
    <id>release</id>
    <activation>
      <property><name>performRelease</name><value>true</value></property>
    </activation>
    <build>
      <plugins>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-source-plugin</artifactId>
          <executions>
            <execution>
              <goals><goal>jar-no-fork</goal></goals>
            </execution>
          </executions>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-javadoc-plugin</artifactId>
          <executions>
            <execution>
              <goals><goal>jar</goal></goals>
            </execution>
          </executions>
        </plugin>
      </plugins>
    </build>
  </profile>

  <!-- JDK 21-specific profile -->
  <profile>
    <id>jdk21</id>
    <activation>
      <jdk>21</jdk>
    </activation>
    <properties>
      <maven.compiler.source>21</maven.compiler.source>
      <maven.compiler.target>21</maven.compiler.target>
    </properties>
  </profile>

</profiles>
```

---

### ⚖️ Comparison Table

| Activation Method | Explicit       | Portable    | Visible in Repo | Common Use            |
| ----------------- | -------------- | ----------- | --------------- | --------------------- |
| `-P flag`         | Yes            | Yes         | Yes             | Manual / CI flag      |
| Property (`-D`)   | Yes (indirect) | Yes         | Yes             | Environment switch    |
| JDK version       | No (auto)      | Yes         | Yes             | Cross-JDK compat      |
| OS type           | No (auto)      | Conditional | Yes             | Native/OS plugins     |
| File presence     | No (auto)      | Yes         | Yes             | Opt-in features       |
| `activeByDefault` | No             | Yes         | Yes             | Base defaults (risky) |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                         |
| ------------------------------------------ | --------------------------------------------------------------- |
| `activeByDefault` profiles always run      | Deactivates when any other profile is explicitly activated      |
| Profiles replace the base POM              | Profiles extend (merge) the base POM; base always applies       |
| Profiles in `settings.xml` are per-project | They're per-developer/CI config - invisible to the project repo |
| Multiple profiles can't be active at once  | They can: `-Pprofile1,profile2`                                 |

---

### 🚨 Failure Modes & Diagnosis

**Profile not activating when expected**

**Symptom:** `-Denv=prod` doesn't trigger the profile.

**Root Cause:** Profile activation property has a typo, or the POM has a different property name.

**Diagnosis:**

```bash
mvn help:active-profiles -Denv=prod
# Lists currently active profiles
```

---

**`activeByDefault` profile silently deactivates**

**Root Cause:** CI uses `-Pci` flag; this deactivates any `activeByDefault` profile.

**Fix:** Replace `activeByDefault` with explicit property-based activation.

---

### 🔗 Related Keywords

**Prerequisites:** `pom.xml`, `Maven Lifecycle`, `Maven Plugins`

**Builds On This:** `Maven Multi-Module Project`, `Build Performance Optimization`

**Related Patterns:** `Maven Multi-Module Project`, `Maven Wrapper (mvnw)`, `Build Performance Optimization`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ACTIVATE     │ -P profileId or -Dproperty=value          │
├──────────────┼───────────────────────────────────────────┤
│ AUTO-TRIGGER │ JDK, OS, file presence, property value    │
├──────────────┼───────────────────────────────────────────┤
│ MERGE        │ Profiles extend base POM (additive)       │
├──────────────┼───────────────────────────────────────────┤
│ INSPECT      │ mvn help:active-profiles                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ activeByDefault (surprise deactivation)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Named conditional config blocks"         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your `pom.xml` has a profile with `<activeByDefault>true</activeByDefault>` that sets the database URL for local development. Your CI pipeline passes `-Pci` to activate the CI database profile. What happens to the `activeByDefault` profile, and what are the consequences for the build?

**Q2.** Your team wants different logging verbosity in development (DEBUG) versus production builds (INFO), controlled via a `logback.xml` resource file. Describe how you would use Maven profiles to swap the resource file at build time without duplicating the rest of `pom.xml`.
