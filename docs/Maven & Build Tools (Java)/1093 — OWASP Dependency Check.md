---
layout: default
title: "OWASP Dependency Check"
parent: "Maven & Build Tools (Java)"
nav_order: 1093
permalink: /maven-build/owasp-dependency-check/
number: "1093"
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Maven Plugins, Dependency Convergence, Maven Enforcer Plugin
used_by: Build Reproducibility, Build Performance Optimization
related: Maven Enforcer Plugin, Build Reproducibility, SNAPSHOT vs RELEASE
tags:
  - maven
  - build-tools
  - security
  - owasp
  - vulnerability
  - java
  - deep-dive
---

# 1093 — OWASP Dependency Check

⚡ TL;DR — OWASP Dependency Check scans your project's dependencies against the National Vulnerability Database (NVD) and fails the build (or reports) if any dependency has a known CVE above a configurable severity threshold — shifting vulnerability detection left into the build pipeline.

| #1093           | Category: Maven & Build Tools (Java)                              | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Plugins, Dependency Convergence, Maven Enforcer Plugin      |                 |
| **Used by:**    | Build Reproducibility, Build Performance Optimization             |                 |
| **Related:**    | Maven Enforcer Plugin, Build Reproducibility, SNAPSHOT vs RELEASE |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your project uses `log4j:log4j:2.14.1`. CVE-2021-44228 (Log4Shell) is published. You don't know you're vulnerable until an alert arrives from your security team, a penetration tester, or — worst — an attacker. Days or weeks pass between the vulnerability disclosure and your awareness.

**THE BREAKING POINT:**
Modern Java applications have 50–300 transitive dependencies. Tracking CVE disclosures for every library manually is infeasible. A vulnerability in a deeply transitive library (`jackson-databind`, `netty`, `commons-text`) is invisible without automated tooling.

**THE INVENTION MOMENT:**
OWASP Dependency Check (and similar tools: Snyk, GitHub Dependabot, Trivy) automatically correlate your dependency list against the NVD (National Vulnerability Database) CVE feed. Integrated as a Maven plugin, it scans on every build — failing the build when a CVE above your configured CVSS score threshold is found.

---

### 📘 Textbook Definition

**OWASP Dependency Check** is an open-source software composition analysis (SCA) tool that identifies project dependencies and checks them against the NIST National Vulnerability Database (NVD) for known Common Vulnerabilities and Exposures (CVEs). The Maven plugin (`org.owasp:dependency-check-maven`) scans both direct and transitive dependencies, matches artifacts by CPE (Common Platform Enumeration) identifiers, and generates an HTML/XML/JSON report. It can be configured to fail the build when any dependency has a CVSS (Common Vulnerability Scoring System) score at or above a threshold (e.g., fail on CVSS ≥ 7.0 = High severity). The NVD database must be downloaded locally (or via a hosted mirror) before scanning.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OWASP Dependency Check = automated CVE scanner for your JAR dependencies, integrated into the Maven build.

**One analogy:**

> Like a metal detector at the airport — every dependency that enters your project passes through the scanner. Known dangerous items (CVEs) trigger an alarm and stop the build. Without it, you hand-check every bag manually (or don't check at all).

**One insight:**
Dependency Check fails builds on _known_ vulnerabilities. Unknown vulnerabilities (0-days) are not covered — the tool is a floor, not a ceiling. But catching known CVEs in CI is dramatically better than not scanning at all.

---

### 🔩 First Principles Explanation

**HOW IT WORKS:**

```
1. COLLECT: Enumerate all project dependencies (direct + transitive JARs)
2. IDENTIFY: Match each JAR to a CPE (Common Platform Enumeration) identifier
   - Uses manifest, filename, package analysis, and heuristics
   - e.g., log4j-core-2.14.1.jar → cpe:/a:apache:log4j:2.14.1
3. QUERY: Search local NVD database for CVEs matching CPE + version range
   - NVD database updated from https://nvd.nist.gov/vuln/data-feeds
4. REPORT: Generate HTML/XML/JSON report with CVE details, CVSS scores, remediation info
5. FAIL BUILD: If any CVE score >= configured threshold (e.g., 7.0)
```

**CVSS SCORE GUIDE:**

```
0.0 - 3.9  : Low
4.0 - 6.9  : Medium
7.0 - 8.9  : High
9.0 - 10.0 : Critical

Recommended build failure threshold: >= 7.0 (High+)
```

**PLUGIN CONFIGURATION:**

```xml
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
  <version>9.0.7</version>
  <configuration>
    <!-- Fail build if any CVE >= this score -->
    <failBuildOnCVSS>7</failBuildOnCVSS>
    <!-- Report output format -->
    <formats>
      <format>HTML</format>
      <format>XML</format>
      <format>JSON</format>
    </formats>
    <!-- Suppress false positives with suppressionFile -->
    <suppressionFiles>
      <suppressionFile>${project.basedir}/owasp-suppressions.xml</suppressionFile>
    </suppressionFiles>
    <!-- NVD API key for faster updates (rate limiting) -->
    <nvdApiKey>${env.NVD_API_KEY}</nvdApiKey>
  </configuration>
  <executions>
    <execution>
      <goals><goal>check</goal></goals>
    </execution>
  </executions>
</plugin>
```

**THE TRADE-OFFS:**
**Gain:** Automated CVE detection on every build; catches transitive vulnerabilities; integrates into existing Maven workflow; generates actionable reports; configurable severity threshold.
**Cost:** Slow: NVD database download takes minutes; subsequent checks are faster but full scans can add 2–10 minutes to build; false positives require suppression management; NVD rate limiting without API key; transitive vulnerability may be unexploitable (requires careful triage, not automatic fail).

---

### 🧪 Thought Experiment

**SETUP:**
Your build starts failing with:

```
[ERROR] CVE-2023-44487 (CVSS 7.5) in io.netty:netty-codec-http2:4.1.86.Final
  Published: 2023-10-10 | HTTP/2 Rapid Reset Attack
```

Netty is a transitive dependency of Spring Boot. You can't upgrade Spring Boot immediately (feature freeze).

**OPTIONS:**

1. **Suppress** with justification: create `owasp-suppressions.xml` with a time-bounded suppression and track the upgrade as a JIRA ticket
2. **Override Netty version**: add `<dependencyManagement>` to pin to the fixed Netty version (compatible with your Spring Boot version if available)
3. **Lower threshold**: raise `failBuildOnCVSS` to `8.0` to allow this 7.5 through (risky; hides other vulnerabilities)
4. **Emergency upgrade**: upgrade Spring Boot to a patched version now (preferred if possible)

**THE LESSON:**
Dependency vulnerabilities in transitive deps require triage, not blind suppression. A well-maintained suppression file with rationale and expiry dates is a legitimate tool; permanent suppressions without justification are a security debt.

---

### 🧠 Mental Model / Analogy

> OWASP Dependency Check is your project's periodic health screening. Just as a doctor checks your blood work against reference ranges for known markers of disease, Dependency Check compares your dependency list against the NVD's known CVE database. A failed test is an alert — not a diagnosis or a guaranteed harm — but something to investigate and treat.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** OWASP Dependency Check scans your project's JARs for known security vulnerabilities (CVEs) and reports them. It can fail the build if a high/critical CVE is found.

**Level 2:** The plugin downloads the NVD database, matches your JARs to known vulnerable versions, and generates an HTML report. `failBuildOnCVSS=7` fails the build for High/Critical CVEs. Suppression files handle false positives and accepted risks.

**Level 3:** False positives are common (CPE matching heuristics aren't perfect). Suppression files (`owasp-suppressions.xml`) allow individually suppressing CVE-artifact pairs with a rationale. `<suppressionFiles>` in configuration loads these. Use the NVD API key to avoid rate-limiting on database updates.

**Level 4:** Performance optimisation: run Dependency Check only on `verify`/`install` phase, not on `compile`; use a shared NVD database mirror (Nexus/Artifactory can proxy the NVD data feed); integrate with Nexus Lifecycle or Snyk for richer SCA with exploit intelligence, transitive-only risk triage, and policy-as-code beyond CVSS scores.

---

### ⚙️ How It Works (Mechanism)

```bash
# Run standalone check (not tied to lifecycle)
mvn dependency-check:check

# Run as part of full verify lifecycle
mvn verify

# Update NVD database only (without scanning)
mvn dependency-check:update-only

# Run check but never fail build (reporting mode)
mvn dependency-check:check -DfailBuildOnCVSS=11  # 11 = never fail

# Specify data directory (shared cache for team)
mvn dependency-check:check -Ddependency-check.data.directory=/shared/nvd-cache

# Output report location
ls target/dependency-check-report.html
```

---

### 💻 Code Example

**Suppression file for accepted risks:**

```xml
<!-- owasp-suppressions.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<suppressions xmlns="https://jeremylong.github.io/DependencyCheck/dependency-suppression.1.3.xsd">

  <!-- FALSE POSITIVE: CPE mismatch — this CVE affects Python boto3, not our Java library -->
  <suppress>
    <notes>False positive: CVE-2023-12345 is for Python boto3, not AWS SDK for Java</notes>
    <packageUrl regex="true">^pkg:maven/software\.amazon\.awssdk/.*@.*$</packageUrl>
    <cve>CVE-2023-12345</cve>
  </suppress>

  <!-- ACCEPTED RISK: Netty HTTP/2 — tracking in JIRA-5678; upgrade planned for v3.1 -->
  <!-- EXPIRES: Remove this suppression when Spring Boot 3.3 is adopted -->
  <suppress until="2025-03-01">
    <notes>JIRA-5678: Netty CVE-2023-44487 accepted risk until Spring Boot 3.3 upgrade</notes>
    <packageUrl regex="true">^pkg:maven/io\.netty/netty-codec-http2@.*$</packageUrl>
    <cve>CVE-2023-44487</cve>
  </suppress>

</suppressions>
```

**Binding to CI-only verification:**

```xml
<!-- Only run Dependency Check on CI (not every local build) -->
<profile>
  <id>ci-security</id>
  <activation>
    <property><name>env</name><value>ci</value></property>
  </activation>
  <build>
    <plugins>
      <plugin>
        <groupId>org.owasp</groupId>
        <artifactId>dependency-check-maven</artifactId>
        <version>9.0.7</version>
        <configuration>
          <failBuildOnCVSS>7</failBuildOnCVSS>
          <nvdApiKey>${env.NVD_API_KEY}</nvdApiKey>
        </configuration>
        <executions>
          <execution>
            <goals><goal>check</goal></goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</profile>
```

---

### ⚖️ Comparison Table

| Tool                   | Type                    | Integration         | Transitive | Exploit Intelligence |
| ---------------------- | ----------------------- | ------------------- | ---------- | -------------------- |
| OWASP Dependency Check | SCA (NVD)               | Maven/Gradle/CLI    | Yes        | No                   |
| Snyk                   | SCA + Remediation       | Maven/Gradle/GitHub | Yes        | Yes                  |
| GitHub Dependabot      | SCA + PR automation     | GitHub-native       | Yes        | Partial              |
| Nexus Lifecycle (IQ)   | Enterprise SCA + Policy | Nexus integration   | Yes        | Yes                  |
| Trivy                  | Universal SCA           | CLI/CI              | Yes        | Yes                  |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                             |
| --------------------------------------------------- | ----------------------------------------------------------------------------------- |
| A passing Dependency Check means no vulnerabilities | It means no _known_ vulnerabilities matching your _current_ NVD database snapshot   |
| High CVE = your app is exploitable                  | Depends on whether the vulnerable code path is reachable in your application        |
| Suppression = ignoring security                     | A documented, time-bounded suppression with tracking is responsible risk management |
| NVD database is always current                      | Default update is 4h; NVD itself may lag CVE publication by hours to days           |

---

### 🚨 Failure Modes & Diagnosis

**Slow builds: NVD database download adds 5+ minutes**

**Root Cause:** Full NVD data feed downloaded on first run or when stale.

**Fix:**

- Use NVD API key (`<nvdApiKey>`) for faster incremental updates
- Run `dependency-check:update-only` in a scheduled CI job (separate from PR builds)
- Use a shared NVD data directory cached between builds

---

**False positive: `dependency-check` flags a test-scoped library**

**Fix:** Configure `<skipTestScope>true</skipTestScope>` to skip test dependencies (if acceptable for your risk profile).

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Plugins`, `Dependency Convergence`, `Maven Enforcer Plugin`

**Builds On This:** `Build Reproducibility`

**Related Patterns:** `Maven Enforcer Plugin`, `Build Reproducibility`, `SNAPSHOT vs RELEASE`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOOL         │ org.owasp:dependency-check-maven          │
├──────────────┼───────────────────────────────────────────┤
│ DATABASE     │ NVD (nvd.nist.gov) — downloaded locally   │
├──────────────┼───────────────────────────────────────────┤
│ FAIL         │ failBuildOnCVSS=7 (High+ severity)        │
├──────────────┼───────────────────────────────────────────┤
│ FALSE-POS    │ owasp-suppressions.xml with expiry dates  │
├──────────────┼───────────────────────────────────────────┤
│ PERF         │ NVD API key + shared data directory       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "CVE scan every dep on every build"       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** OWASP Dependency Check reports CVE-2021-44228 (Log4Shell, CVSS 10.0 Critical) in `log4j-core:2.14.1`. However, `log4j-core` is only used in test scope in your project, and your production application never uses the vulnerable JNDI lookup feature. How do you assess the real risk, and what are your options for handling this finding?

**Q2.** Your CI pipeline runs Dependency Check on every PR and the full NVD database download adds 8 minutes to each build. Describe an architecture for your CI pipeline that maintains security scanning coverage while reducing this latency to under 1 minute per PR build.
