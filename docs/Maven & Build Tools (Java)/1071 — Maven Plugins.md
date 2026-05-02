---
layout: default
title: "Maven Plugins"
parent: "Maven & Build Tools (Java)"
nav_order: 1071
permalink: /maven-build/maven-plugins/
number: "1071"
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: "Maven Goals, Maven Phases, pom.xml"
used_by: "Maven Lifecycle, CI-CD pipelines"
tags: #maven, #plugins, #mojo, #build-extensions, #compiler-plugin, #surefire
---

# 1071 — Maven Plugins

`#maven` `#plugins` `#mojo` `#build-extensions` `#compiler-plugin` `#surefire`

⚡ TL;DR — **Maven plugins** are the execution engine of Maven builds. Every build action is performed by a plugin: `maven-compiler-plugin` compiles Java, `maven-surefire-plugin` runs tests, `maven-jar-plugin` creates JARs, `spring-boot-maven-plugin` creates fat JARs. Plugins are JARs containing Mojo classes (one class = one goal). Plugins are configured in `pom.xml` under `<build><plugins>`. Plugins themselves are Maven artifacts — they're downloaded from Maven Central just like dependencies.

| #1071 | Category: Maven & Build Tools (Java) | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Maven Goals, Maven Phases, pom.xml | |
| **Used by:** | Maven Lifecycle, CI-CD pipelines | |

---

### 📘 Textbook Definition

**Maven plugin**: a JAR artifact containing one or more Mojos (Maven plain Old Java Objects), where each Mojo implements one Maven goal. Plugins extend Maven's core functionality — Maven core has no compile, test, or package logic built in; all such logic lives in plugins. Plugin types: (1) **Build plugins**: bound to build lifecycle phases (under `<build><plugins>`); (2) **Reporting plugins**: generate reports for `mvn site` (under `<reporting><plugins>`). Maven provides core plugins for the default lifecycle; third-party plugins (Spring Boot, Checkstyle, SpotBugs, JaCoCo, Docker) integrate into the lifecycle via the same mechanism. Plugin management: `<pluginManagement>` in parent POMs centralizes plugin version declarations (analogous to `<dependencyManagement>` for dependencies) — child modules inherit version without specifying it. Plugin prefix resolution: `maven-XXX-plugin` → prefix `XXX`; `XXX-maven-plugin` → prefix `XXX`; custom mappings in `plugin.xml`. Plugin versioning: always specify explicit plugin versions in production builds for reproducibility — snapshot plugin versions can cause non-deterministic builds.

---

### 🟢 Simple Definition (Easy)

Maven is like a general contractor who delegates all specialized work to subcontractors. The compiler subcontractor (`maven-compiler-plugin`) compiles Java code. The tester subcontractor (`maven-surefire-plugin`) runs JUnit tests. The packager subcontractor (`maven-jar-plugin`) makes the JAR. Maven just coordinates when each subcontractor runs. You can hire new subcontractors (add plugins) or give different instructions to existing ones (configure plugins in `pom.xml`).

---

### 🔵 Simple Definition (Elaborated)

Plugins divide into two categories:
1. **Maven Core plugins** (maintained by Apache): compiler, surefire, jar, install, deploy, resources, clean. These implement the default lifecycle.
2. **Third-party plugins**: spring-boot-maven-plugin, jacoco-maven-plugin, checkstyle-maven-plugin, dockerfile-maven-plugin, openapi-generator-maven-plugin. These extend the lifecycle with additional capabilities.

Plugin configuration in `pom.xml` has two levels:
- **Global plugin configuration** (`<configuration>` directly under `<plugin>`): applies to all executions of that plugin
- **Execution-level configuration** (`<configuration>` under `<execution>`): applies only when that execution runs

Plugin versions: always pin plugin versions (not just dependency versions) for reproducible builds. If you don't specify a version, Maven uses the latest release — which can change between builds.

---

### 🔩 First Principles Explanation

```
ESSENTIAL MAVEN PLUGINS (REFERENCE):

1. maven-compiler-plugin
   Goal: compile, testCompile
   Default bindings: compile → compile phase; testCompile → test-compile phase
   Key config:
   
   <plugin>
     <groupId>org.apache.maven.plugins</groupId>
     <artifactId>maven-compiler-plugin</artifactId>
     <version>3.12.0</version>
     <configuration>
       <release>17</release>          <!-- Java version (preferred over source/target) -->
       <compilerArgs>
         <arg>-parameters</arg>       <!-- retain parameter names for reflection -->
         <arg>-Xlint:all</arg>        <!-- enable all warnings -->
       </compilerArgs>
       <annotationProcessorPaths>     <!-- annotation processors (Lombok, MapStruct) -->
         <path>
           <groupId>org.projectlombok</groupId>
           <artifactId>lombok</artifactId>
           <version>${lombok.version}</version>
         </path>
       </annotationProcessorPaths>
     </configuration>
   </plugin>

2. maven-surefire-plugin
   Goal: test
   Default binding: test phase
   Runs: *Test.java, Test*.java, *Tests.java, *TestCase.java
   Key config:
   
   <plugin>
     <groupId>org.apache.maven.plugins</groupId>
     <artifactId>maven-surefire-plugin</artifactId>
     <version>3.2.2</version>
     <configuration>
       <parallel>methods</parallel>   <!-- parallel test execution -->
       <threadCount>4</threadCount>
       <forkCount>1</forkCount>       <!-- run in separate JVM process
       <argLine>-Xmx512m</argLine>   <!-- JVM args for test process -->
       <excludes>
         <exclude>**/*IT.java</exclude>  <!-- exclude integration tests -->
       </excludes>
     </configuration>
   </plugin>

3. maven-failsafe-plugin
   Goals: integration-test, verify
   Bindings: integration-test → integration-test; verify → verify
   Runs: *IT.java, IT*.java, *ITCase.java
   Difference from surefire: does NOT fail immediately → allows post-integration-test cleanup
   
   <plugin>
     <groupId>org.apache.maven.plugins</groupId>
     <artifactId>maven-failsafe-plugin</artifactId>
     <version>3.2.2</version>
     <executions>
       <execution>
         <goals>
           <goal>integration-test</goal>
           <goal>verify</goal>
         </goals>
       </execution>
     </executions>
   </plugin>

4. spring-boot-maven-plugin
   Goals: repackage (package phase), run, start, stop, build-image
   Key function: creates executable "fat JAR" with all dependencies bundled
   
   <plugin>
     <groupId>org.springframework.boot</groupId>
     <artifactId>spring-boot-maven-plugin</artifactId>
     <version>3.2.0</version>
     <configuration>
       <mainClass>com.example.Application</mainClass>   <!-- optional if @SpringBootApplication present -->
       <layers>
         <enabled>true</enabled>   <!-- layered JAR: deps/snapshot-deps/resources/app layers -->
       </layers>
     </configuration>
   </plugin>

5. maven-jar-plugin
   Goal: jar (package phase)
   Creates the standard JAR (thin JAR without dependencies)
   
   <plugin>
     <groupId>org.apache.maven.plugins</groupId>
     <artifactId>maven-jar-plugin</artifactId>
     <configuration>
       <archive>
         <manifest>
           <addClasspath>true</addClasspath>
           <mainClass>com.example.Application</mainClass>
         </manifest>
       </archive>
       <excludes>
         <exclude>**/application-local.properties</exclude>
       </excludes>
     </configuration>
   </plugin>

6. jacoco-maven-plugin (JaCoCo code coverage)
   Goals: prepare-agent, report, check
   
   <plugin>
     <groupId>org.jacoco</groupId>
     <artifactId>jacoco-maven-plugin</artifactId>
     <version>0.8.11</version>
     <executions>
       <execution>
         <goals><goal>prepare-agent</goal></goals>  <!-- adds -javaagent JVM arg -->
       </execution>
       <execution>
         <id>report</id>
         <phase>verify</phase>
         <goals><goal>report</goal></goals>         <!-- generate HTML/XML report -->
       </execution>
       <execution>
         <id>check</id>
         <phase>verify</phase>
         <goals><goal>check</goal></goals>           <!-- enforce coverage minimum -->
         <configuration>
           <rules>
             <rule>
               <limits>
                 <limit>
                   <counter>LINE</counter>
                   <value>COVEREDRATIO</value>
                   <minimum>0.80</minimum>
                 </limit>
               </limits>
             </rule>
           </rules>
         </configuration>
       </execution>
     </executions>
   </plugin>

PLUGIN MANAGEMENT (in parent POM):

  <build>
    <pluginManagement>
      <plugins>
        <!-- Declare version once; child modules use it without specifying version -->
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-surefire-plugin</artifactId>
          <version>3.2.2</version>
          <configuration>
            <!-- shared config for all child modules -->
            <argLine>-Xmx512m</argLine>
          </configuration>
        </plugin>
      </plugins>
    </pluginManagement>
  </build>
  
  <!-- Child module pom.xml: just declare the plugin, no version needed -->
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <!-- version inherited from parent pluginManagement -->
        <configuration>
          <!-- overrides parent's configuration -->
          <argLine>-Xmx1g</argLine>
        </configuration>
      </plugin>
    </plugins>
  </build>
```

---

### ❓ Why Does This Exist (Why Before What)

Maven's core is intentionally minimal — it understands lifecycles, plugins, and dependency resolution, but contains no build logic itself. This plugin architecture means: (1) new build capabilities can be added without modifying Maven core; (2) third parties (Spring, Docker, code quality tools) integrate as first-class citizens using the same API; (3) plugin updates are independent of Maven version updates; (4) projects use only the plugins they need. The alternative (build logic in Maven core) would create a monolith that requires core changes for every new build capability.

---

### 🧠 Mental Model / Analogy

> **Maven plugins are like power tool attachments for a power drill**: the drill (Maven core) provides the motor (dependency resolution, lifecycle management) and the standardized chuck (plugin API). The attachment (plugin) does the actual work: drill bit (compiler plugin) makes holes (compiles Java), screwdriver bit (surefire plugin) drives screws (runs tests), sander bit (checkstyle plugin) smooths surfaces (checks code style). You choose which attachments to use, configure them for your material (project), and the drill coordinates when each runs.

---

### 🔄 How It Connects (Mini-Map)

```
Maven needs tasks to perform; plugins provide those tasks
        │
        ▼
Maven Plugins ◄── (you are here)
(JARs containing Mojo classes; each Mojo = one goal)
        │
        ├── Maven Goals: goals are what plugins provide (one Mojo = one goal)
        ├── Maven Phases: goals from plugins bind to phases
        ├── Maven Lifecycle: plugins execute lifecycle phases
        └── pom.xml: <build><plugins> configures plugins + <pluginManagement> for inheritance
```

---

### 💻 Code Example

```bash
# List all plugins used in the build (effective POM):
mvn help:effective-pom | grep -A3 "<plugin>"

# Describe a plugin and all its goals:
mvn help:describe -Dplugin=org.apache.maven.plugins:maven-surefire-plugin -Ddetail

# Show all configurable parameters for a goal:
mvn help:describe -Dplugin=compiler -Dmojo=compile -Ddetail

# Check for plugin version updates:
mvn versions:display-plugin-updates

# Common plugin invocations:
mvn surefire:test                # run unit tests
mvn failsafe:integration-test    # run integration tests
mvn jacoco:report                # generate coverage report
mvn checkstyle:check             # check code style
mvn spotbugs:check               # static analysis
mvn dependency:analyze           # find unused/undeclared dependencies
mvn spring-boot:run              # run Spring Boot app
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Plugins and dependencies are the same thing | Both are Maven artifacts (JARs in Maven Central), but they serve different purposes. `<dependencies>` are added to the application classpath. `<build><plugins>` are tools used during the build — they run IN the Maven process (or a forked JVM) and are NOT added to the application classpath. Surefire is not in your JAR; it just runs your tests. |
| Specifying a plugin in `<pluginManagement>` activates it | `<pluginManagement>` only declares version and default configuration. The plugin is not active until it appears in `<build><plugins>` (or until a lifecycle phase that it's bound to by default is invoked). This is analogous to `<dependencyManagement>` vs `<dependencies>`. |
| Plugin configuration merges with parent configuration | By default, child module configuration REPLACES parent configuration (not merges). To merge: set `<combine.children="append">` or `<combine.self="merge">` attributes on the XML element. For lists (like `<argLine>`), replacement can cause missing parent args in the child. |

---

### 🔗 Related Keywords

- `Maven Goals` — what plugins provide; each Mojo = one goal
- `Maven Phases` — where goals bind in the lifecycle
- `Maven Lifecycle` — the lifecycle that plugins extend through goal bindings
- `pom.xml` — `<build><plugins>` configures plugins; `<pluginManagement>` declares versions
- `Maven Overview` — Maven core that loads and executes plugins

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ESSENTIAL PLUGINS:                                      │
│ maven-compiler-plugin  → compile (Java 17)             │
│ maven-surefire-plugin  → unit tests (*Test.java)       │
│ maven-failsafe-plugin  → integration tests (*IT.java)  │
│ maven-jar-plugin       → thin JAR                      │
│ spring-boot-maven-plugin → fat JAR, spring-boot:run    │
│ jacoco-maven-plugin    → coverage report + enforcement │
│ maven-checkstyle-plugin → code style                   │
├──────────────────────────────────────────────────────────┤
│ CONFIG:                                                 │
│ <build><plugins>       → activate + configure          │
│ <build><pluginManagement> → declare versions (inherit) │
│ mvn help:describe -Dplugin=X → explore plugin          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The `maven-surefire-plugin` by convention (with `forkCount=1`) runs tests in a forked JVM process. The JVM startup overhead for each test run is 1-3 seconds. For a project with 1000 tests taking 0.01s each, test execution is 10s but JVM startup is 2s — minor. For Quarkus or Spring Boot integration tests with application startup (5-10s each test), the overhead is huge. How does Surefire's `forkCount=0` (same JVM as Maven, no fork) trade-off isolation for speed? What test pollution issues arise? When do parallel test execution and test container reuse (`@TestcontainersTestcase`) strategies apply?

**Q2.** The `spring-boot-maven-plugin` creates a "layered JAR" to optimize Docker image layer caching. The JAR layers are: dependencies (rarely change), spring-boot-loader, snapshot-dependencies (change sometimes), and application (changes every build). When building a Docker image from this layered JAR, each layer becomes a separate Docker layer — changing application code only invalidates the top layer, not the 200MB dependencies layer. Compare this to the multi-stage Dockerfile approach for achieving the same optimization. When would you use layered JARs vs explicit multi-stage Dockerfile COPY statements for dependency layer optimization?
