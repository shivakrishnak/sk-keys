---
version: 1
layout: default
title: "Source vs Binary Distribution"
parent: "Maven & Build Tools"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/maven-build/source-vs-binary-distribution/
id: MVN-038
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Maven Lifecycle, Maven Release Plugin, pom.xml
used_by: Build Reproducibility, OWASP Dependency Check, Maven Release Plugin
related: Maven Release Plugin, Build Reproducibility, Maven Repository (local, central, remote)
tags:
  - maven
  - build-tools
  - distribution
  - packaging
  - java
  - deep-dive
---

⚡ TL;DR - A binary distribution is a pre-compiled, ready-to-run package (JAR, WAR, ZIP with scripts). A source distribution contains the original source code for recipients to compile themselves. Maven publishes both via the maven-source-plugin; understanding the distinction matters for open-source publishing, reproducibility verification, and legal compliance.

| #1094           | Category: Maven & Build Tools (Java)                                                   | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Lifecycle, Maven Release Plugin, pom.xml                                         |                 |
| **Used by:**    | Build Reproducibility, OWASP Dependency Check, Maven Release Plugin                    |                 |
| **Related:**    | Maven Release Plugin, Build Reproducibility, Maven Repository (local, central, remote) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You publish a JAR library. A user wants to: (1) step into library code in their debugger; (2) verify the JAR was compiled from the source code you claim; (3) understand how a specific method works internally; (4) comply with a licence that requires making source code available. Without a source JAR, none of these are easily possible.

**THE BREAKING POINT:**
Commercial open-source ecosystems, reproducibility verification, and legal compliance all require source availability alongside compiled artifacts. For enterprise consumers of internal libraries, stepping through library code in the debugger (with attached sources) is a basic development workflow expectation.

**THE INVENTION MOMENT:**
Maven establishes a convention: alongside `my-lib-1.0.0.jar`, publish `my-lib-1.0.0-sources.jar` (Java source files) and `my-lib-1.0.0-javadoc.jar` (generated documentation). Maven Central requires both sources and javadoc JARs for public library publication. IDEs automatically download and attach source JARs for step-through debugging and inline documentation.

---

### 📘 Textbook Definition

In Maven's artifact model, a **binary distribution** is the compiled output of a build: a JAR containing `.class` files (bytecode), resources, and a manifest - ready for direct JVM execution. A **source distribution** (source JAR, classifier `sources`) contains the original `.java` source files packaged as a JAR, enabling IDE source attachment, reproducibility verification, and licence compliance. A **javadoc distribution** (classifier `javadoc`) contains the generated API documentation. Together, these three artifacts - `artifact-1.0.jar`, `artifact-1.0-sources.jar`, `artifact-1.0-javadoc.jar` - represent a complete library release in the Maven ecosystem. Maven Central requires all three for published open-source artifacts.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Binary JAR = compiled `.class` files (run); source JAR = `.java` files (debug, verify, comply); javadoc JAR = API docs.

**One analogy:**

> A published book (binary), the manuscript (source), and the reading guide (javadoc). The book is what readers use; the manuscript is for translators, editors, and verifiers; the reading guide helps navigate the content. All three are distributed together for a complete publication.

**One insight:**
Source JARs are not just for open-source libraries. Internal enterprise libraries should also publish source JARs to enable IDE-based debugging across team boundaries - eliminating the "I can't see inside that library's code" friction.

---

### 🔩 First Principles Explanation

**MAVEN ARTIFACT CLASSIFIERS:**

```
my-lib-1.0.0.jar              ← main artifact (compiled
  binary)
my-lib-1.0.0-sources.jar      ← source JAR (classifier:
  sources)
my-lib-1.0.0-javadoc.jar      ← javadoc JAR (classifier:
  javadoc)
my-lib-1.0.0.pom              ← project object model
  (metadata)
my-lib-1.0.0.jar.sha1         ← checksum for integrity
```

**WHAT EACH CONTAINS:**

```
Binary JAR (no classifier):
  com/example/MyClass.class
  com/example/Utils.class
  META-INF/MANIFEST.MF

Sources JAR (-sources):
  com/example/MyClass.java
  com/example/Utils.java
  META-INF/MANIFEST.MF

Javadoc JAR (-javadoc):
  index.html
  com/example/MyClass.html
  com/example/Utils.html
  (Generated HTML API documentation)
```

**CONSUMING A SOURCE JAR IN IDE:**
When a developer adds `my-lib:1.0.0` as a Maven dependency, IntelliJ IDEA automatically detects `my-lib-1.0.0-sources.jar` in the repository and attaches it. Pressing Ctrl+Click on a library class opens the actual source file. Without a source JAR, the IDE shows decompiled bytecode - functional but imprecise and missing comments.

**GENERATING SOURCES AND JAVADOC:**

```xml
<!-- maven-source-plugin: creates -sources.jar -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-source-plugin</artifactId>
  <version>3.3.0</version>
  <executions>
    <execution>
      <id>attach-sources</id>
      <goals>
        <goal>jar-no-fork</goal>  <!-- creates sources JAR without re-running compile -->
      </goals>
    </execution>
  </executions>
</plugin>

<!-- maven-javadoc-plugin: creates -javadoc.jar -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-javadoc-plugin</artifactId>
  <version>3.6.3</version>
  <executions>
    <execution>
      <id>attach-javadocs</id>
      <goals>
        <goal>jar</goal>
      </goals>
    </execution>
  </executions>
</plugin>
```

**THE TRADE-OFFS:**

**Binary-only gain:** Smaller distribution, faster downloads, IP protection (source not exposed).

**Binary-only cost:** Cannot debug, cannot verify reproducibility, licence compliance issues, poor developer experience for consumers.

**Source+Binary gain:** Full developer experience (IDE debug, code inspection); reproducibility verification; licence compliance; trust-building for open source.

**Source+Binary cost:** Larger distribution; source may expose IP you'd prefer to protect; builds slightly slower (javadoc generation is slow for large codebases).

---

### 🧪 Thought Experiment

**SETUP:**
Your company publishes an internal shared library `auth-utils` to Nexus. Library consumers report that debugging their services is painful because stepping into `auth-utils` code shows decompiled bytecode with no comments.

**SOLUTION:**
Add `maven-source-plugin` to `auth-utils/pom.xml` and run `mvn deploy`. Nexus now hosts `auth-utils-2.3.0-sources.jar`. On IntelliJ IDEA, consumers: File → Project Structure → Libraries → select auth-utils → attach sources from `~/.m2/.../auth-utils-2.3.0-sources.jar`.

Or: IntelliJ automatically downloads sources if "Download sources and documentation" is enabled in Maven settings.

**THE LESSON:**
Source JAR publishing is a developer experience feature, not just an open-source compliance requirement. Internal teams benefit equally - stepping through well-commented library code is far superior to reading decompiled bytecode.

---

### 🧠 Mental Model / Analogy

> Binary vs source distribution is like distributing a compiled application versus distributing the full development kit (SDK). The binary is what users run; the sources are what developers study, verify, and debug. For libraries (as opposed to end-user applications), the SDK (sources + javadoc) is as important as the binary.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** When you publish a library, you publish a JAR (compiled code). You _should also_ publish a sources JAR (original `.java` files) so others can debug into your library. Maven provides `maven-source-plugin` for this.

**Level 2:** Classifiers differentiate artifact types in Maven's coordinate system: `groupId:artifactId:version:classifier:type`. The sources JAR classifier is `sources`; javadoc is `javadoc`. IDEs and the Maven dependency plugin use these conventions automatically.

**Level 3:** Maven Central requires sources and javadoc JARs for all published artifacts. The `maven-release-plugin` can be configured with a `release` profile that activates source and javadoc generation only for release builds (not every SNAPSHOT build, which would be slow). `jar-no-fork` goal avoids re-running compilation.

**Level 4:** Source distribution for entire applications (not just libraries): Maven Assembly Plugin or Maven Distribution ZIP can package source code with a build script into a distributable archive. For GPL/LGPL compliance: software that must provide source must include a mechanism for distribution - a source JAR attached to a Maven artifact is the standard mechanism. SPDX and CycloneDX SBOMs (Software Bill of Materials) extend this further by providing machine-readable licence and component metadata.

---

### ⚙️ How It Works (Mechanism)

```bash
# Generate sources JAR manually
mvn source:jar

# Generate javadoc JAR manually
mvn javadoc:jar

# See what classifiers were generated
ls target/
# my-lib-1.0.0.jar
# my-lib-1.0.0-sources.jar
# my-lib-1.0.0-javadoc.jar

# Deploy all classifiers to Nexus (automatically included in mvn
# deploy)
mvn deploy

# In a pom.xml dependency declaration, explicitly request sources:
# (This is just for reference - IDEs handle this automatically)
<dependency>
  <groupId>com.example</groupId>
  <artifactId>my-lib</artifactId>
  <version>1.0.0</version>
  <classifier>sources</classifier>  <!-- requests sources JAR explicitly -->
</dependency>
```

---

### 💻 Code Example

**Release profile that activates sources + javadoc for release builds only:**

```xml
<profiles>
  <profile>
    <id>release</id>
    <!-- Activated by Maven Release Plugin during release:perform -->
    <!-- or manually: mvn deploy -Prelease -->
    <build>
      <plugins>

        <!-- Generate sources JAR -->
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-source-plugin</artifactId>
          <version>3.3.0</version>
          <executions>
            <execution>
              <id>attach-sources</id>
              <goals><goal>jar-no-fork</goal></goals>
            </execution>
          </executions>
        </plugin>

        <!-- Generate javadoc JAR -->
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-javadoc-plugin</artifactId>
          <version>3.6.3</version>
          <configuration>
            <!-- Fail build on javadoc warnings/errors -->
            <failOnError>true</failOnError>
            <failOnWarnings>false</failOnWarnings>
          </configuration>
          <executions>
            <execution>
              <id>attach-javadocs</id>
              <goals><goal>jar</goal></goals>
            </execution>
          </executions>
        </plugin>

        <!-- GPG signing (required for Maven Central) -->
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-gpg-plugin</artifactId>
          <version>3.1.0</version>
          <executions>
            <execution>
              <id>sign-artifacts</id>
              <phase>verify</phase>
              <goals><goal>sign</goal></goals>
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

| Artifact              | Classifier | Contains                       | Purpose                |
| --------------------- | ---------- | ------------------------------ | ---------------------- |
| `lib-1.0.jar`         | (none)     | `.class` files, resources      | Run the library        |
| `lib-1.0-sources.jar` | `sources`  | `.java` source files           | Debug, verify, inspect |
| `lib-1.0-javadoc.jar` | `javadoc`  | HTML API documentation         | Browse API docs in IDE |
| `lib-1.0.pom`         | N/A        | Project metadata, dependencies | Dependency resolution  |
| `lib-1.0-tests.jar`   | `tests`    | Test `.class` files            | Reuse test utilities   |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Source JARs are only for open-source projects         | Internal libraries benefit equally - enables IDE debugging across teams                                             |
| `maven-source-plugin` runs at `package` automatically | Must be explicitly configured in `<executions>`                                                                     |
| Javadoc JARs are optional                             | Required by Maven Central; highly recommended for any shared library                                                |
| Source JAR = full source distribution                 | Source JAR contains `src/main/java` contents; a full source distribution includes build scripts, test sources, etc. |

---

### 🚨 Failure Modes & Diagnosis

**IDE shows decompiled bytecode instead of source**

**Root Cause:** No sources JAR published to the repository; or IDE doesn't have "auto-download sources" enabled.

**Fix:** Add `maven-source-plugin` to library's POM, redeploy. Or in IntelliJ: File → Project Structure → Libraries → select → download sources.

---

**`maven-javadoc-plugin` fails build with javadoc errors**

**Root Cause:** Javadoc strict mode catches missing `@param`, `@return`, or malformed javadoc comments.

**Fix:** Fix javadoc comments, or set `<failOnError>false</failOnError>` temporarily. Prefer fixing comments.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Lifecycle`, `Maven Release Plugin`, `pom.xml`

**Builds On This:** `Build Reproducibility`, `Maven Release Plugin`

**Related Patterns:** `Maven Release Plugin`, `Build Reproducibility`, `Maven Repository (local, central, remote)`

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ BINARY       │ my-lib-1.0.jar - .class files            │
├──────────────┼──────────────────────────────────────────┤
│ SOURCES      │ my-lib-1.0-sources.jar - .java files     │
├──────────────┼──────────────────────────────────────────┤
│ JAVADOC      │ my-lib-1.0-javadoc.jar - HTML docs       │
├──────────────┼──────────────────────────────────────────┤
│ PLUGIN       │ maven-source-plugin (jar-no-fork goal)   │
├──────────────┼──────────────────────────────────────────┤
│ REQUIRED     │ Maven Central requires sources + javadoc │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Binary=run; Source=debug/verify; Docs=re│
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your company's policy requires that any library published to Nexus that is used in a production service must also have a sources JAR published. How would you enforce this policy automatically - using either the Maven Enforcer Plugin or a CI pipeline check - so that any `mvn deploy` without a sources JAR fails?

**Q2.** A security team asks whether publishing source JARs for internal libraries could expose intellectual property. Under what circumstances would you withhold source JARs from an internal Nexus repository, and what developer experience trade-offs result from that decision?
