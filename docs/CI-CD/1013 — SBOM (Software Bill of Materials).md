---
layout: default
title: "SBOM (Software Bill of Materials)"
parent: "CI/CD"
nav_order: 1013
permalink: /ci-cd/sbom/
number: "1013"
category: CI/CD
difficulty: ★★★
depends_on: Dependency Scanning, Container Scanning, SCA, Artifact Registry
used_by: Supply Chain Security, Compliance, SLSA
related: Dependency Scanning, Container Scanning, Secret Scanning, SCA
tags:
  - cicd
  - security
  - devops
  - compliance
  - deep-dive
---

# 1013 — SBOM (Software Bill of Materials)

⚡ TL;DR — An SBOM is a machine-readable inventory of every software component in an application, enabling automated vulnerability tracking and regulatory compliance across the entire supply chain.

| #1013 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Dependency Scanning, Container Scanning, SCA, Artifact Registry | |
| **Used by:** | Supply Chain Security, Compliance, SLSA | |
| **Related:** | Dependency Scanning, Container Scanning, Secret Scanning, SCA | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In December 2021, Log4Shell (CVE-2021-44228, CVSS 10.0) is published. Every major security team immediately asks: "Do we have Log4j, and if so, which versions, in which services?" At companies without SBOMs, engineers spend weeks manually grepping repositories, checking Dockerfiles, and emailing teams — because no one has an authoritative inventory. Some services are discovered to use Log4j only after production scans run. One team finds Log4j embedded 4 layers deep in a transitive dependency they've never heard of. The disclosure-to-patch timeline stretches to weeks for organisations that should have responded in hours.

**THE BREAKING POINT:**
Modern applications have thousands of direct and transitive dependencies. The question "do we use library X version Y?" should be answerable in seconds from a database — not require a week of manual discovery. Without a formal component inventory, vulnerability response is reactive, slow, and incomplete. The US government's Executive Order 14028 (2021) mandated SBOMs for all software sold to federal agencies precisely because the absence of inventories was a systemic national security risk.

**THE INVENTION MOMENT:**
This is exactly why SBOMs exist: generate and maintain a formal, machine-readable bill of materials for every software artefact — making "what's in this application?" a query, not a research project.

---

### 📘 Textbook Definition

A **Software Bill of Materials (SBOM)** is a formally structured, machine-readable list of all software components that constitute an application — including direct dependencies, transitive dependencies, OS packages, and metadata (version, license, supplier, hash). SBOMs are produced in standardised formats: **CycloneDX** (OWASP-led, JSON/XML, supply chain focus) and **SPDX** (Linux Foundation, ISO 5962:2021, compliance focus). They are generated at build time by tools such as Syft, Trivy, and Maven CycloneDX Plugin, then associated with the build artefact (container image, JAR). SBOMs enable downstream consumers (security scanners, compliance systems, procurement teams) to query the full component list without access to the source code. They are the foundation of automated vulnerability management and software supply chain transparency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A machine-readable list of every library and component inside your software, like a nutrition label for code.

**One analogy:**
> An SBOM is a nutrition facts label for software. When you pick up a food product, the nutrition label tells you every ingredient with exact quantities — enabling you to check for allergens or make health decisions without opening the package. An SBOM does the same for software: it lists every component, version, and supplier, so a security scanner can check for vulnerabilities without requiring access to the source code or running the application.

**One insight:**
The SBOM's power is not in the document itself, but in what becomes possible when the document exists. With an SBOM, the question "are we affected by this new CVE?" becomes a database JOIN — cross-reference the SBOM inventory against the CVE's affected component list. Without the SBOM, the same question requires running scanners against all running services in real-time. The SBOM converts reactive scanning into queryable state.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every piece of software is composed of other pieces of software — no application is built purely from scratch.
2. Dependencies have versions, and versions have known vulnerabilities — this is a knowable, enumerable set.
3. Vulnerability response requires knowing what you have before you can act on what's broken.

**DERIVED DESIGN:**
The SBOM must capture three levels of information:
- **Identity**: name, version, package URL (PURL — a standardised component identifier like `pkg:npm/lodash@4.17.21`)
- **Relationships**: which component depends on which (the dependency graph, not just a flat list)
- **Metadata**: supplier, license, hash/checksum, download location, known vulnerabilities (optional VEX integration)

For the SBOM to be actionable, it must be machine-readable and follow a standard schema. Ad-hoc text files or HTML reports don't enable automated querying. CycloneDX JSON and SPDX SPDX-JSON are the two dominant standards; CycloneDX has stronger tooling for security use cases, SPDX is required for NTIA/NIST compliance.

**VEX (Vulnerability Exploitability eXchange)** is SBOM's companion format: while an SBOM lists components, a VEX statement attaches exploitability assertions to each component-CVE pair: "this CVE exists in component X, but component X is used in a non-vulnerable code path in this product" — enabling downstream consumers to suppress known false positives.

**THE TRADE-OFFS:**
**Gain:** Instant component inventory; rapid CVE response; automated compliance; enables supply chain verification.
**Cost:** SBOM maintenance overhead — they become stale unless continuously regenerated at build time. SBOM tooling maturity varies by ecosystem. SBOMs reveal your entire technology stack to downstream consumers, which may have competitive disclosure implications.

---

### 🧪 Thought Experiment

**SETUP:**
A healthcare company ships a web application with 450 npm dependencies. Log4Shell drops with CVSS 10.0. The security team needs to know within 2 hours whether any service uses Log4j.

**WHAT HAPPENS WITHOUT AN SBOM:**
Security team SSHes into 12 production servers and runs `find / -name "log4j*.jar"`. Finds nothing (it's a Node.js app, not Java). But wait — the app's PDF generation service uses a Java-based background worker with Log4j as a transitive dependency. Nobody connects these dots in the 2-hour window. The worker is missed. Response is declared complete. Log4Shell is exploited through the PDF service 6 days later.

**WHAT HAPPENS WITH AN SBOM:**
Security team queries the SBOM database (GUAC — Graph for Understanding Artifact Composition): `SELECT * FROM components WHERE name = 'log4j' AND product = 'all'`. Returns 1 result: `log4j:2.14.0` in `pdf-worker-service:v3.2.1`. Within 15 minutes of the CVE publication, the correct team has an alert with context. The PDF worker is patched and redeployed the same day.

**THE INSIGHT:**
An SBOM converts a vulnerability response from a discovery problem into a lookup problem. The difference isn't technology — it's whether you invested in the inventory before the incident required it.

---

### 🧠 Mental Model / Analogy

> An SBOM is a ship's cargo manifest. Before a vessel enters port, it must submit a complete manifest of every item on board — item name, weight, origin, and handling requirements. Port security uses the manifest to check for prohibited goods without physically opening every container. An SBOM is that manifest for software: every component declared, enabling automated security checks without manual inspection of the codebase.

- "Ship's manifest" → SBOM document (CycloneDX / SPDX)
- "Cargo items" → software components (name + version + PURL)
- "Handling requirements" → licenses, known vulnerabilities (VEX)
- "Port security" → vulnerability scanner / compliance system
- "Prohibited goods list" → CVE database
- "Customs clearance" → SBOM-based compliance certification

Where this analogy breaks down: a ship's manifest is submitted once per voyage. An SBOM should be regenerated on every build — because new CVEs are published continuously against unchanged component lists. A six-month-old SBOM is like using last year's cargo manifest to clear today's customs.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An SBOM is an ingredient list for software. Just as food labels list every ingredient so you can check for allergens, an SBOM lists every library and component in an app so a security scanner can check for vulnerabilities without manually inspecting the code.

**Level 2 — How to use it (junior developer):**
Generate SBOMs using Trivy or Syft: `trivy image --format cyclonedx --output sbom.json myapp:latest` or `syft myapp:latest -o cyclonedx-json > sbom.json`. Store the SBOM alongside your build artefact in your CI/CD pipeline. For Java projects, the `cyclonedx-maven-plugin` generates SBOMs from the Maven dependency tree. Attach the SBOM to your container image using OCI annotations or Cosign. The SBOM should be regenerated on every build — treat it as a build artefact, not a one-time document.

**Level 3 — How it works (mid-level engineer):**
Syft generates SBOMs by running package-manager detection against a filesystem or container image, similar to container scanning, then serialising the result in CycloneDX or SPDX format. Each component entry includes: `name`, `version`, `purl` (e.g., `pkg:maven/org.apache.logging.log4j/log4j-core@2.14.0`), `hashes` (SHA-256 of the component), and optionally `licenses` and `externalReferences`. The `purl` (Package URL) format is critical — it's a standardised URI that enables cross-tool interoperability and database lookups. After SBOM generation, tools like `grype sbom:./sbom.json` can perform offline vulnerability analysis against the SBOM without re-scanning the image.

**Level 4 — Why it was designed this way (senior/staff):**
The SBOM standards landscape reflects competing institutional priorities: SPDX (Linux Foundation, 2011) was designed for license compliance in enterprise procurement; CycloneDX (OWASP, 2017) was designed for security use cases and vulnerability management. The US NTIA (National Telecommunications and Information Administration) published minimum SBOM elements in 2021, which both standards satisfy. The emerging GUAC (Graph for Understanding Artifact Composition) project treats SBOMs as graph nodes and creates queryable knowledge graphs across entire software supply chains — enabling queries like "which of my 500 applications transitively depend on openssl < 3.0?" without scanning every service individually. SLSA (Supply Levels for Software Artifacts) adds provenance attestations — not just "what's in this artefact" but "how was this artefact produced and by whom."

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│     SBOM GENERATION & USE PIPELINE      │
├─────────────────────────────────────────┤
│                                         │
│  GENERATE (at build time):              │
│  Docker image / JAR / NPM package       │
│  → Syft / Trivy filesystem scan         │
│  → Detect: npm, maven, pip, dpkg, apk  │
│  → Component list with PURLs + hashes   │
│  → Serialise: CycloneDX JSON or SPDX   │
│  → sbom.json (stored as build artifact) │
│                                         │
│  ATTACH (to artefact):                  │
│  cosign attach sbom --sbom sbom.json \  │
│    myregistry/myapp:sha256-...          │
│  → SBOM linked to image digest          │
│                                         │
│  CONSUME (vulnerability analysis):      │
│  grype sbom:sbom.json                   │
│  → Match PURLs against vuln DB          │
│  → Report: CVE-20XX-YYYY in log4j@2.14 │
│                                         │
│  CONSUME (compliance query):            │
│  GUAC ingest → graph DB                 │
│  Query: "log4j anywhere in fleet?"      │
│  → Result in <1 second                  │
│                                         │
│  CONSUME (license compliance):          │
│  FOSSA / SPDX tools                     │
│  → List all GPL components              │
│  → Flag license policy violations       │
└─────────────────────────────────────────┘
```

**CycloneDX component entry structure:**
```json
{
  "type": "library",
  "name": "log4j-core",
  "version": "2.14.0",
  "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.0",
  "hashes": [
    {
      "alg": "SHA-256",
      "content": "a84b...f3c2"
    }
  ],
  "licenses": [
    {"license": {"id": "Apache-2.0"}}
  ]
}
```

**PURL (Package URL) format:**
`pkg:<type>/<namespace>/<name>@<version>?<qualifiers>#<subpath>`
- `pkg:npm/lodash@4.17.21`
- `pkg:maven/org.springframework/spring-core@5.3.20`
- `pkg:deb/debian/curl@7.68.0`
- `pkg:docker/ubuntu@sha256:abc123`

PURLs are the key to cross-tool interoperability — a PURL uniquely identifies a component in a way that both Trivy and Grype understand.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer merges PR to main
  → CI pipeline triggered
  → docker build → image tagged
  → Trivy container scan (pass)
  → SBOM generation [← YOU ARE HERE]
     syft image myapp:sha-abc123
     -o cyclonedx-json > sbom.json
  → SBOM stored in artifact registry
  → SBOM signed with cosign
  → SBOM attached to image digest
  → Grype scans SBOM: 0 critical CVEs
  → Image deployed to production

  (Day 45): CVE-2024-XXXX published
  → SBOM database queried automatically
  → Component match: log4j@2.14 in 3 services
  → Automated PR: upgrade log4j → 2.17.2
  → NO new scan needed for detection
```

**FAILURE PATH:**
```
SBOM not generated (step skipped)
  → New CVE published
  → Team runs emergency scan of all services
  → 2 services missed (deprecated repos)
  → Vulnerable services run in production
  → Observable: CVE exploited in missed service
```

**WHAT CHANGES AT SCALE:**
At 1000+ microservices, individual SBOM generation scales horizontally (each service generates its own). The challenge shifts to SBOM aggregation and querying. GUAC (Graph for Understanding Artifact Composition) ingests SBOMs from all services and builds a unified dependency graph. "Which services are affected by CVE-2024-XXXX?" becomes a 2-second query across the entire fleet. Without GUAC or equivalent, the same question requires running scanners against all 1000 services simultaneously — taking hours.

---

### 💻 Code Example

**Example 1 — Syft SBOM generation:**
```bash
# Generate SBOM for a Docker image
syft myapp:latest -o cyclonedx-json > sbom.cyclonedx.json
syft myapp:latest -o spdx-json > sbom.spdx.json

# Generate SBOM for a directory (source)
syft dir:/path/to/repo -o cyclonedx-json > sbom.json

# Scan SBOM for vulnerabilities (offline)
grype sbom:sbom.cyclonedx.json
```

**Example 2 — SBOM generation in GitHub Actions CI:**
```yaml
# .github/workflows/sbom.yml
name: Build + SBOM
on:
  push:
    branches: [main]

jobs:
  build-sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Generate SBOM with Syft
        uses: anchore/sbom-action@v0
        with:
          image: myapp:${{ github.sha }}
          format: cyclonedx-json
          output-file: sbom.cyclonedx.json

      - name: Vulnerability scan against SBOM
        uses: anchore/scan-action@v3
        with:
          sbom: sbom.cyclonedx.json
          fail-build: true
          severity-cutoff: critical

      - name: Store SBOM as artifact
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.cyclonedx.json

      - name: Sign and attach SBOM to image
        run: |
          # Attach SBOM to image using cosign
          cosign attach sbom \
            --sbom sbom.cyclonedx.json \
            myregistry/myapp:${{ github.sha }}
```

**Example 3 — Maven CycloneDX plugin (Java):**
```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.cyclonedx</groupId>
  <artifactId>cyclonedx-maven-plugin</artifactId>
  <version>2.7.11</version>
  <executions>
    <execution>
      <phase>package</phase>
      <goals>
        <goal>makeAggregateBom</goal>
      </goals>
    </execution>
  </executions>
  <configuration>
    <projectType>library</projectType>
    <outputFormat>json</outputFormat>
    <!-- includes transitive deps in SBOM -->
    <includeDependencyGraph>true</includeDependencyGraph>
  </configuration>
</plugin>
```
```bash
# Generates: target/bom.json (CycloneDX)
mvn package
```

**Example 4 — Query SBOM for specific component:**
```bash
# Check if log4j exists in SBOM (bash)
cat sbom.cyclonedx.json | \
  jq '.components[] | select(.name | contains("log4j")) |
  {name, version, purl}'

# Output:
# {
#   "name": "log4j-core",
#   "version": "2.14.0",
#   "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.0"
# }
```

---

### ⚖️ Comparison Table

| Format | Owner | Use Case | Tooling | Compliant |
|---|---|---|---|---|
| **CycloneDX** | OWASP | Security / Vuln Mgmt | Trivy, Syft, many | NTIA, EO14028 |
| SPDX | Linux Foundation | License Compliance | FOSSology, Syft | ISO 5962, NTIA |
| SWID | ISO | Enterprise Inventory | Limited | ISO 19770-2 |

| Generator | Ecosystems | Container | Source | SBOM Format |
|---|---|---|---|---|
| **Syft** | 40+ | Yes | Yes | CycloneDX, SPDX |
| Trivy | 20+ | Yes | Yes | CycloneDX, SPDX |
| Maven CycloneDX Plugin | Maven | No | Yes | CycloneDX |
| cyclonedx-npm | npm | No | Yes | CycloneDX |

How to choose: Use **CycloneDX** format for security and vulnerability management workflows (better tooling support). Use **SPDX** for license compliance and government/enterprise procurement requirements. Use **Syft** as the default generator for broad ecosystem coverage. Use language-specific plugins (Maven, npm) for precise build-time SBOM generation from source.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Generating an SBOM once is sufficient | SBOMs go stale immediately. New CVEs are published daily against the same component versions. SBOMs must be regenerated on every build and re-analysed continuously as CVE databases update. |
| An SBOM replaces dependency scanning | SBOMs are the inventory; dependency scanning is the analysis. The SBOM provides the component list; a scanner like Grype or Snyk uses the SBOM data to check against vulnerability databases. Both are required. |
| SBOMs are only relevant for compliance | SBOMs are fundamentally a vulnerability response tool. The compliance requirement (EO 14028) brought them to mainstream attention, but their primary value is enabling rapid CVE impact assessment across large fleets. |
| SBOMs expose confidential technology information | SBOMs reveal component names and versions — information already available to anyone who can run the software, inspect dependencies, or perform binary analysis. For internal supply chains, SBOMs are shared in closed systems. |
| SBOMs are the same as lock files | Lock files (package-lock.json, Pipfile.lock) capture application-layer dependencies for a specific build tool. SBOMs capture all components including OS packages, multi-ecosystem transitive deps, and include metadata (hashes, licenses, PURLs) — they are a superset. |
| VEX is optional | Without VEX, every CVE in linked components generates an alert regardless of exploitability. VEX statements allow vendors to assert "this CVE exists but is not exploitable in our product" — eliminating false positives that cause alert fatigue at scale. |

---

### 🚨 Failure Modes & Diagnosis

**1. Stale SBOM Not Reflecting Current Production**

**Symptom:** Security team queries the SBOM database after Log4Shell: "no log4j found." Operations team later discovers a service hadn't been rebuilt in 6 months — its SBOM predates the new log4j dependency that was added via a transitive path.

**Root Cause:** SBOM generation is not tied to every build. Generated manually or quarterly. Running artefacts have different component sets than the SBOM database.

**Diagnostic:**
```bash
# Compare build timestamp vs SBOM timestamp
# In CycloneDX JSON:
cat sbom.cyclonedx.json | \
  jq '.metadata.timestamp'

# Compare against image build time
docker inspect myapp:prod | \
  jq '.[].Created'

# If SBOM timestamp << image created → stale
```

**Fix:** SBOM generation must be a mandatory CI step — not an optional or separate process. Add SBOM generation to the `docker build` GitHub Actions workflow. Gate deployment on SBOM attachment to image digest.

**Prevention:** Require SBOM presence as part of image admission control. In Kubernetes, use OPA Gatekeeper policy: reject pods if image digest has no associated SBOM signature.

---

**2. SBOM Missing Transitive Dependencies**

**Symptom:** SBOM reports 45 components. `docker inspect` and manual analysis reveals 380 OS packages not in the SBOM. Grype scan of the SBOM misses 12 CVEs caught by a direct container scan.

**Root Cause:** SBOM generated from `package.json` source scan only — application-layer scan without OS layer. Did not use image-based scanner (Trivy/Syft on the Docker image).

**Diagnostic:**
```bash
# Count components in SBOM
cat sbom.json | jq '.components | length'

# Count packages found by direct container scan
trivy image --format json myapp:latest | \
  jq '[.Results[].Packages[]?] | length'

# Compare: significant discrepancy = incomplete SBOM
```

**Fix:**
```bash
# WRONG: scan source directory only
syft dir:./src -o cyclonedx-json > sbom.json

# RIGHT: scan the built Docker image (includes OS packages)
syft myapp:latest -o cyclonedx-json > sbom.json
# This captures app deps + OS packages in the final image
```

**Prevention:** Always generate SBOMs from the built and tagged image, not from source directories. Run both application-level and image-level SBOM generation and merge results for complete coverage.

---

**3. SBOM Not Queryable at Incident Response Time**

**Symptom:** CVE published. Security team has SBOMs (stored as JSON files in S3). It takes 4 hours to write and run a script to check all 200 services. Response SLA breached.

**Root Cause:** SBOMs stored as static files without an indexed, queryable store. At incident time, cross-service analysis requires custom scripting.

**Diagnostic:**
```bash
# Time how long manual search takes
time for f in s3://sboms/*.json; do
  aws s3 cp $f - | jq '.components[] |
    select(.name == "log4j-core")' | grep -l log4j
done
```

**Fix:** Ingest SBOMs into a queryable graph store. Options:
- **GUAC** (open source): `guac ingest cyclonedx sbom.json` → graph DB
- **Dependency-Track** (open source): REST API + PostgreSQL backend
- **Snyk** / **Mend**: commercial SBOM management platforms

**Prevention:** Design the SBOM ecosystem before incidents require it. Implement SBOM ingestion into Dependency-Track as part of the initial CI pipeline setup. Test the incident response query at quarterly disaster recovery exercises.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dependency Scanning` — SBOM is the formal inventory that dependency scanning uses as input; understanding the scanning workflow is required
- `Container Scanning` — container scanning produces SBOM data for OS packages; SBOMs aggregate both OS and application-layer findings
- `SCA (Software Composition Analysis)` — SBOM is the formal output artefact of SCA; SCA is the practice, SBOM is the document

**Builds On This (learn these next):**
- `Supply Chain Security` — SBOMs are a foundational building block of software supply chain security alongside provenance attestations and image signing
- `SLSA (Supply Levels for Software Artifacts)` — the provenance framework that extends SBOM from "what's in this artefact" to "how and by whom was this artefact produced"
- `VEX (Vulnerability Exploitability eXchange)` — the companion format to SBOM that adds exploitability assertions to SBOM component-CVE pairs

**Alternatives / Comparisons:**
- `Dependency Scanning` — real-time scanning against live manifests; SBOM provides a persistent, queryable inventory that enables offline and historical analysis
- `Container Scanning` — scanner-level output; SBOM is a standardised inventory format that multiple scanners can produce and consume
- `Lock Files` — capture dependency versions for a build tool; SBOMs are a superset covering all components, ecosystems, OS packages, and metadata

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Machine-readable inventory of every       │
│              │ software component in an application      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ "Do we use Log4j?" taking weeks to answer │
│ SOLVES       │ instead of seconds during an incident     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ An SBOM converts vulnerability response   │
│              │ from discovery to a database lookup       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every build — generate + store SBOM as    │
│              │ a first-class build artefact              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — tune SBOM scope (image-based │
│              │ not source-based) for completeness        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Complete component visibility vs          │
│              │ SBOM storage and query infrastructure     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Nutrition facts label for your software  │
│              │  — every ingredient, machine-readable."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Supply Chain Security → SLSA →            │
│              │ VEX → Cosign/Sigstore                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your organisation generates CycloneDX SBOMs for all 300 microservices and ingests them into Dependency-Track. A critical CVE (CVSS 9.8) is published for `commons-text` (Apache). Dependency-Track identifies 23 services that use the affected version range. 8 of those services are in actively maintained repositories; 15 are in legacy repositories with no current assigned owners and no automated CI. Design the complete incident response protocol for both groups — what differs, what has to happen manually vs automated, and what is the escalation path for the legacy services?

**Q2.** An SBOM lists `libssl 1.1.1f` from a Debian-based base image. Your vulnerability database shows CVE-2022-0778 affects `libssl < 1.1.1n`. However, the Debian Security Tracker shows this package as "fixed" because Debian backported the patch to 1.1.1f. Your SBOM-based scanner reports it as vulnerable; your container scanner (which uses OS-specific advisories) reports it as fixed. How should your SBOM pipeline handle this discrepancy, and what does this reveal about the limitations of version-number-based vulnerability matching in SBOMs?

