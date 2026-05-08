---
layout: default
title: "Maven Release Plugin"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /maven-build/maven-release-plugin/
id: MVN-031
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: SNAPSHOT vs RELEASE, Maven Multi-Module Project, pom.xml, Nexus / Artifactory
used_by: Build Reproducibility, Build Performance Optimization
related: SNAPSHOT vs RELEASE, Maven Multi-Module Project, Nexus / Artifactory
tags:
  - maven
  - build-tools
  - release
  - versioning
  - java
  - deep-dive
---

# MVN-031 - Maven Release Plugin

⚡ TL;DR - The Maven Release Plugin automates the SNAPSHOT→RELEASE promotion cycle: it validates no SNAPSHOT dependencies, strips `-SNAPSHOT` from the version, runs tests, tags SCM, deploys to the release repository, then bumps to the next SNAPSHOT - all in two commands: `release:prepare` + `release:perform`.

| #1091           | Category: Maven & Build Tools (Java)                                          | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | SNAPSHOT vs RELEASE, Maven Multi-Module Project, pom.xml, Nexus / Artifactory |                 |
| **Used by:**    | Build Reproducibility, Build Performance Optimization                         |                 |
| **Related:**    | SNAPSHOT vs RELEASE, Maven Multi-Module Project, Nexus / Artifactory          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
To release `my-library`, a developer must manually: (1) check all SNAPSHOT dependencies are promoted; (2) update `<version>2.0.0-SNAPSHOT</version>` to `<version>2.0.0</version>` in every POM; (3) commit the change; (4) create a Git tag; (5) run `mvn deploy`; (6) update version to `2.1.0-SNAPSHOT`; (7) commit again. In a multi-module project, steps 2 and 6 touch 20+ files. A missed file or a typo leaves the project in an inconsistent state.

**THE BREAKING POINT:**
Manual release processes are slow, error-prone, and don't scale across dozens of modules or dozens of releases per sprint. A failed release midway leaves the repository in a partial state.

**THE INVENTION MOMENT:**
The Maven Release Plugin automates all of these steps transactionally. It validates prerequisites, applies version changes atomically, runs the build, tags SCM, deploys, and rolls back cleanly on failure - replacing a 15-step manual process with two commands.

---

### 📘 Textbook Definition

The **Maven Release Plugin** (`maven-release-plugin`) is a Maven plugin that automates the software release process. It consists of two primary goals: `release:prepare` - which validates the project (no SNAPSHOT deps, no uncommitted changes), strips `-SNAPSHOT` from all module versions, commits the version change, creates a SCM tag, and bumps to the next development SNAPSHOT; and `release:perform` - which checks out the tag, builds it, and deploys to the configured release repository. The plugin uses `<scm>` configuration in `pom.xml` to interact with version control (Git, SVN). In multi-module projects, it updates all module POMs simultaneously.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`mvn release:prepare release:perform` = validate → strip `-SNAPSHOT` → tag → deploy → bump to next SNAPSHOT.

**One analogy:**

> Like a deployment pipeline that checks every gate automatically before publishing: "Are all dependencies stable? Are all tests passing? Is the source clean? If yes, promote and tag - in one atomic, auditable operation."

**One insight:**
`release:prepare` is safe to run repeatedly until successful - it creates `release.properties` and rolls back if interrupted. `release:perform` does the actual deployment. This separation allows a failed prepare to be cleaned up without a broken deployment.

---

### 🔩 First Principles Explanation

**WHAT `release:prepare` DOES:**

```
1. Validate:
   - No uncommitted changes in working copy
   - No SNAPSHOT dependencies in any module

2. Prompt for versions:
   - Release version: 2.0.0-SNAPSHOT → 2.0.0
   - SCM tag: v2.0.0
   - Next dev version: 2.1.0-SNAPSHOT

3. Perform release changes:
   - Update all module <version> to 2.0.0
   - Run full build + tests: mvn verify
   - git commit "prepare release 2.0.0"
   - git tag v2.0.0

4. Update to next dev version:
   - Update all module <version> to 2.1.0-SNAPSHOT
   - git commit "prepare for next development iteration"

5. Write: release.properties (for release:perform)
```

**WHAT `release:perform` DOES:**

```
1. Checkout the tag (v2.0.0) into a temporary directory
2. Build the tag from the clean checkout
3. mvn deploy (to release repository in <distributionManagement>)
4. Clean up temporary directory
```

**REQUIRED `pom.xml` CONFIGURATION:**

```xml
<scm>
  <connection>scm:git:git://github.com/myorg/my-project.git</connection>
  <developerConnection>scm:git:git@github.com:myorg/my-project.git</developerConnection>
  <url>https://github.com/myorg/my-project</url>
  <tag>HEAD</tag>
</scm>

<distributionManagement>
  <repository>
    <id>nexus-releases</id>
    <url>https://nexus.mycompany.com/repository/maven-releases/</url>
  </repository>
</distributionManagement>
```

**THE TRADE-OFFS:**
**Gain:** Automated, consistent release process; SCM tags aligned with deployed artifacts; multi-module version synchronisation; validation prevents bad releases (SNAPSHOT deps, dirty working copy).
**Cost:** Two-step process (prepare + perform) adds complexity; failed releases leave local commits/tags requiring manual rollback; the plugin builds twice (once in prepare, once in perform) - slow for large projects; not well-suited for trunk-based development with feature flags (assumes version-bump-per-release model).

---

### 🧪 Thought Experiment

**SETUP:**
You run `mvn release:prepare` in a 10-module project. The build passes all validations and creates the tag. The CI server starts `release:perform`. During `perform`, the deploy to Nexus fails with a 403 (missing credentials). You now have:

- A local commit changing all versions to `2.0.0`
- A follow-up commit bumping to `2.1.0-SNAPSHOT`
- A Git tag `v2.0.0`
- No artifact in Nexus

**RECOVERY OPTIONS:**

1. Fix credentials and re-run `mvn release:perform` (release.properties still present)
2. `mvn release:rollback` - reverts version commits (but tag must be deleted manually)
3. Manual: push tag, re-deploy manually, clean up release.properties

**THE LESSON:**
`release:perform` is the risky step - it interacts with external systems (SCM push, Nexus deploy). Ensure credentials and connectivity are verified before running, or use CI-controlled release automation that validates these prerequisites in advance.

---

### 🧠 Mental Model / Analogy

> The Maven Release Plugin is like a book publishing workflow: an editor (prepare phase) checks the manuscript (no typos, no placeholder text, all chapters complete), creates the print-ready PDF, numbers the edition, archives it, and sends it to production; the printing department (perform phase) prints and distributes using the archived print-ready version. Two separate, auditable steps.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** `mvn release:prepare` runs tests, tags your repo, and bumps versions. `mvn release:perform` deploys the tagged version to Nexus.

**Level 2:** `prepare` requires: no SNAPSHOT dependencies (use `<requireReleaseDeps>` enforcer), clean working directory, `<scm>` configured. It updates ALL module versions in a multi-module project simultaneously.

**Level 3:** `release:prepare -DdryRun=true` runs the prepare logic without committing to SCM - useful for testing. `-DskipTests=true` skips tests during prepare (risky but faster in CI when tests already passed). `release.properties` stores the release state between prepare and perform.

**Level 4:** Modern alternative: CI-driven release (GitHub Actions, Jenkins). Instead of the plugin's two-step, CI runs: (1) bump version in POM, (2) commit + tag, (3) build from tag, (4) deploy. The Versions plugin (`versions:set`) handles version bumping; CI handles the orchestration. This avoids the plugin's "builds twice" overhead and integrates better with trunk-based development.

---

### ⚙️ How It Works (Mechanism)

```bash
# Dry run (validate without committing)
mvn release:prepare -DdryRun=true

# Full prepare (interactive: prompts for versions)
mvn release:prepare

# Non-interactive prepare (CI mode)
mvn release:prepare \
  -DreleaseVersion=2.0.0 \
  -DdevelopmentVersion=2.1.0-SNAPSHOT \
  -Dtag=v2.0.0 \
  -DautoVersionSubmodules=true \  # all modules get same version
  -DskipTests=false

# Perform the release (deploy from tag)
mvn release:perform

# Rollback a failed prepare
mvn release:rollback
# Then manually: git tag -d v2.0.0 (if tag was pushed: git push --delete origin v2.0.0)

# Clean up release.properties and backup POMs
mvn release:clean
```

---

### 💻 Code Example

**Complete plugin configuration in `pom.xml`:**

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-release-plugin</artifactId>
  <version>3.0.1</version>
  <configuration>
    <!-- All modules get the same version -->
    <autoVersionSubmodules>true</autoVersionSubmodules>
    <!-- Tag format: v2.0.0 -->
    <tagNameFormat>v@{project.version}</tagNameFormat>
    <!-- Don't build twice in perform (use already-built artifacts from prepare) -->
    <useReleaseProfile>false</useReleaseProfile>
    <!-- Goals to run during perform (just deploy; compile+test already done) -->
    <releaseProfiles>release</releaseProfiles>
    <goals>deploy</goals>
  </configuration>
</plugin>

<!-- Release profile: activate during release:perform -->
<profiles>
  <profile>
    <id>release</id>
    <build>
      <plugins>
        <!-- Source and Javadoc JARs for release to Maven Central -->
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
</profiles>
```

---

### ⚖️ Comparison Table

| Step                  | Manual Process      | Maven Release Plugin   |
| --------------------- | ------------------- | ---------------------- |
| Remove SNAPSHOT       | Edit 20+ POMs       | Automated              |
| Run full build        | `mvn clean verify`  | Automated (in prepare) |
| SCM commit            | `git commit`        | Automated              |
| SCM tag               | `git tag`           | Automated              |
| Deploy                | `mvn deploy`        | Automated (in perform) |
| Bump to next SNAPSHOT | Edit 20+ POMs       | Automated              |
| Rollback on failure   | Manual file restore | `mvn release:rollback` |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                   |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `release:perform` also runs tests     | It builds from the SCM tag - includes test execution unless `-DskipTests`                                 |
| Rollback undoes everything            | Rollback reverts local version commits; pushed tags and deployed artifacts must be manually deleted       |
| `release:prepare` is idempotent       | Partially - can be re-run if `release.properties` exists; but tag creation may fail if tag already exists |
| The plugin is the only way to release | CI pipelines can automate the same steps without the plugin (often preferred in modern projects)          |

---

### 🚨 Failure Modes & Diagnosis

**`[ERROR] Cannot release with unresolved dependency: X:SNAPSHOT`**

**Root Cause:** A dependency still on SNAPSHOT version; prepare blocks release.

**Fix:** Promote that dependency to a RELEASE first; or use `allowTimestampedSnapshots=true` (not recommended for production releases).

---

**`[ERROR] The working copy has local modifications`**

**Root Cause:** Uncommitted changes in working directory.

**Fix:** Commit or stash all changes before running `release:prepare`.

---

### 🔗 Related Keywords

**Prerequisites:** `SNAPSHOT vs RELEASE`, `Maven Multi-Module Project`, `pom.xml`, `Nexus / Artifactory`

**Builds On This:** `Build Reproducibility`

**Related Patterns:** `SNAPSHOT vs RELEASE`, `Maven Multi-Module Project`, `Nexus / Artifactory`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PREPARE      │ Validate → strip -SNAPSHOT → tag → bump   │
├──────────────┼───────────────────────────────────────────┤
│ PERFORM      │ Checkout tag → build → deploy             │
├──────────────┼───────────────────────────────────────────┤
│ REQUIRES     │ <scm> + <distributionManagement> in POM   │
├──────────────┼───────────────────────────────────────────┤
│ MULTI-MODULE │ -DautoVersionSubmodules=true              │
├──────────────┼───────────────────────────────────────────┤
│ ROLLBACK     │ mvn release:rollback (+ delete tag)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Automated SNAPSHOT→RELEASE pipeline"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You run `mvn release:prepare` and it fails midway with a test failure. You fix the bug, commit, and re-run `mvn release:prepare`. What state is the project in from the first failed run, and what must you do before re-running? What does `mvn release:clean` do in this context?

**Q2.** Your team has adopted continuous delivery and wants to release on every merge to `main`. How would you integrate the Maven Release Plugin into a GitHub Actions CI workflow to achieve fully automated releases without any manual `mvn release:prepare` invocations?
