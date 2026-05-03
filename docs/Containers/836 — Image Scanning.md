---
layout: default
title: "Image Scanning"
parent: "Containers"
nav_order: 836
permalink: /containers/image-scanning/
number: "0836"
category: Containers
difficulty: ★★★
depends_on: Docker Image, Docker Layer, Container Security, Distroless Images, Dockerfile
used_by: Image Provenance / SBOM, CI/CD, Container Scanning
related: Container Security, Distroless Images, Image Provenance / SBOM, OCI Standard, SBOM
tags:
  - containers
  - docker
  - security
  - devops
  - advanced
  - bestpractice
---

# 836 — Image Scanning

⚡ TL;DR — Image scanning inspects every layer of a container image for known CVEs, misconfigurations, and exposed secrets before the image ever reaches production.

| #836 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker Image, Docker Layer, Container Security, Distroless Images, Dockerfile | |
| **Used by:** | Image Provenance / SBOM, CI/CD, Container Scanning | |
| **Related:** | Container Security, Distroless Images, Image Provenance / SBOM, OCI Standard, SBOM | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your team builds a containerised Java application on top of `openjdk:11-jre`. It ships to production. Six months later a critical CVE is disclosed: `log4j 2.14.1` — embedded in a transitive dependency of a library baked into layer 3 of your base image. Nobody notices. The vulnerability has been live in production for six months. The first sign of compromise is an outbound connection to a C2 server at 3 AM.

**THE BREAKING POINT:**
A container image is a layered archive of filesystem snapshots. Each layer can contain thousands of packages, libraries, and binaries. No human can audit all of them. The base image alone (`openjdk:11-jre`) contains 300+ packages. Each one may carry known vulnerabilities. Without automated scanning, the only discovery mechanism is luck or breach notification.

**THE INVENTION MOMENT:**
This is exactly why image scanning was invented — automated parsing of image contents against continuously-updated vulnerability databases (NVD, OSV, GitHub Advisory Database) to surface CVEs, misconfigured permissions, hardcoded secrets, and policy violations before the image reaches a running container.

---

### 📘 Textbook Definition

**Image scanning** is the automated static analysis of container image layers to identify: known CVEs in OS packages and language-level dependencies, embedded secrets (API keys, credentials), dangerous Dockerfile misconfigurations (running as root, exposed ports, overly broad permissions), and deviations from security policy. Scanners parse the image's Software Bill of Materials (SBOM), cross-reference it against vulnerability databases (NVD, OSV, GHSA), and report findings with severity ratings (CRITICAL, HIGH, MEDIUM, LOW). Scanning is a preventive control in a defence-in-depth strategy and does not replace runtime security.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Image scanning is an automated X-ray of your container that finds dangerous software before it ever runs.

**One analogy:**
> Imagine sending a package through airport security before boarding a plane. The X-ray machine scans the contents — not by opening every layer, but by pattern-matching against a database of prohibited items. If it finds a match, the package is flagged before it boards. Container image scanning does exactly this: every layer of every image is parsed and cross-referenced against a list of "prohibited" software (CVEs) before the image is allowed to run in production.

**One insight:**
The critical insight is that scanning must happen *before* the image is deployed — "shift left" security. A CVE discovered in production means thousands of live containers may already be exploitable. A CVE discovered at `docker build` time means zero exposure. The scanner's value is directly proportional to how early in the pipeline it sits.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every package in an image that has a known CVE is a potential attack vector — regardless of whether your application uses that code path.
2. The threat surface of a container image equals the union of all CVEs in all packages across all layers.
3. Static detection (before deployment) is cheaper by orders of magnitude than post-breach remediation.

**DERIVED DESIGN:**

A scanner must solve three sub-problems:

1. **SBOM extraction:** Parse the image manifest and layer tarballs. Extract all installed packages from OS package databases (`/var/lib/dpkg/status`, `/var/lib/rpm/`, Alpine `apk`) and language-level dependency files (`pom.xml`, `package-lock.json`, `requirements.txt`, JAR manifests).

2. **Vulnerability matching:** Cross-reference the extracted package inventory (name + version) against vulnerability advisory databases. NVD provides CVE IDs and CVSS scores. OSV provides language-ecosystem advisories. GHSA covers GitHub-hosted projects.

3. **Policy enforcement:** Evaluate findings against a policy: "fail build if any CRITICAL CVE with CVSS score > 9.0 is present in the final image."

```
┌──────────────────────────────────────────────────────────┐
│            Image Scanning Pipeline                       │
├──────────────────────────────────────────────────────────┤
│  OCI Image                                               │
│       ↓                                                  │
│  Layer extraction & SBOM synthesis                       │
│  (OS pkgs + language deps)                               │
│       ↓                                                  │
│  Vulnerability DB lookup                                 │
│  (NVD / OSV / GHSA)                                      │
│       ↓                                                  │
│  Secret detection                                        │
│  (regex + entropy analysis)                              │
│       ↓                                                  │
│  Misconfiguration checks                                │
│  (Dockerfile best practices)                             │
│       ↓                                                  │
│  Policy gate  ── PASS → registry push                    │
│               └─ FAIL → pipeline broken + alert         │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

**Gain:** Known-vulnerable packages are caught before deployment. Security policy is enforceable as code.

**Cost:** Scanners produce false positives (especially for OS packages that distributions have backport-patched). Scanner databases lag NVD by hours to days. Scanning adds 30–120 seconds to CI pipeline. Scanning does NOT catch zero-days or runtime exploits.

---

### 🧪 Thought Experiment

**SETUP:**
Your CI pipeline builds `myapp:latest` every commit. The base image is `debian:bullseye-slim`. You add a Java application JAR. Total pipeline time: 3 minutes. No scanning.

**WHAT HAPPENS WITHOUT IMAGE SCANNING:**
A new CVE is published: `CVE-2023-XXXX` — CVSS 9.8, affects `libssl1.1` in Debian Bullseye. Your image ships to production. 2,000 replicas run. The security team discovers the CVE two weeks later during a quarterly audit. Patching requires rebuilding all images, redeploying all services. Two weeks of exposure window. Incident report required.

**WHAT HAPPENS WITH IMAGE SCANNING:**
The same CVE is published. The scanner's vulnerability database updates within 12 hours. On the next commit, the pipeline runs Trivy. Trivy flags `libssl1.1 CVE-2023-XXXX CRITICAL`. The build fails before the image is pushed. The developer adds `RUN apt-get upgrade -y` to the Dockerfile, rebuilds, Trivy passes. The vulnerability never reaches a single container in production.

**THE INSIGHT:**
Scanning converts a reactive, breach-driven security posture into a proactive, pipeline-enforced one. The earlier the gate, the smaller the exposure window.

---

### 🧠 Mental Model / Analogy

> Image scanning is a customs checkpoint for container images. Before a package enters the country (production), customs officers (the scanner) check every item against a watchlist of prohibited goods (the CVE database). Anything flagged is held at the border. Nothing dangerous crosses without inspection.

Mapping:
- "Customs checkpoint" → image scanner (Trivy, Grype, Snyk, Docker Scout)
- "Every item in the package" → OS packages + language dependencies in image layers
- "Watchlist of prohibited goods" → NVD / OSV / GHSA vulnerability database
- "Country border (production)" → container registry + CI/CD gate
- "Held at the border" → build fails, image not pushed
- "Certificate of clearance" → scan report with zero CRITICAL findings

Where this analogy breaks down: customs inspect physical items once at import. Image scanning must be re-run on every new build — the "watchlist" grows daily as new CVEs are published, so an image that passed yesterday may fail today.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you build a container, it includes software packages — some of which may have security flaws. Image scanning is an automatic check that reads all those packages and warns you if any have known security problems, just like antivirus software scans files for known malware signatures.

**Level 2 — How to use it (junior developer):**
Run a scanner like Trivy against any image: `trivy image myapp:latest`. It outputs a table of CVEs grouped by severity (CRITICAL, HIGH, MEDIUM, LOW). Configure your CI pipeline to fail if CRITICAL CVEs are found: `trivy image --exit-code 1 --severity CRITICAL myapp:latest`. This prevents vulnerable images from being pushed to your registry.

**Level 3 — How it works (mid-level engineer):**
Trivy (and similar tools like Grype, Snyk Container) decompress each image layer, parse OS package databases (dpkg, rpm, apk) and language manifests (JAR `META-INF/MANIFEST.MF`, `package-lock.json`). They extract a package inventory (name, version, source). Each entry is matched against the vulnerability database using CPE (Common Platform Enumeration) identifiers. Fixed version data is used to determine if a fix exists. Secret scanning uses regex patterns + Shannon entropy to detect hardcoded credentials. Misconfiguration checks read the Dockerfile embedded in the image metadata.

**Level 4 — Why it was designed this way (senior/staff):**
Container images are immutable artifacts — the attack surface is baked in at build time. This is both the problem (you cannot patch in-place) and the solution (you can verify the surface exhaustively before deployment). Vulnerability matching against package databases is feasible only because Linux distributions publish machine-readable security advisory feeds (Debian Security Tracker, Red Hat OVAL, Alpine secdb). Language-ecosystem vulnerability data is harder: Maven, npm, PyPI CVEs require ecosystem-specific advisories (GHSA, OSV). The fundamental limitation of image scanning is that it only catches *known* vulnerabilities — zero-days and logic flaws are invisible to static analysis. Runtime security (Falco, eBPF probes) complements scanning by detecting exploitation in real time.

---

### ⚙️ How It Works (Mechanism)

Image scanning follows a five-phase pipeline:

**Phase 1 — Image fetch**
The scanner pulls the OCI image manifest and layer blobs from the registry (or reads them from a local `.tar` export). No image is executed — analysis is entirely static.

**Phase 2 — Layer decompression and file extraction**
Each layer tarball is extracted. The scanner builds a merged filesystem view (respecting `whiteout` files for deleted paths) and locates known package database paths:
- Debian/Ubuntu: `/var/lib/dpkg/status`
- RHEL/CentOS: `/var/lib/rpm/Packages`
- Alpine: `/lib/apk/db/installed`
- Node.js: `**/node_modules/.package-lock.json`
- Java: `**/*.jar` → parsed `META-INF/MANIFEST.MF` / `pom.properties`
- Python: `**/site-packages/*.dist-info/METADATA`

**Phase 3 — SBOM construction**
From the extracted files, the scanner builds a Software Bill of Materials: a structured list of `(package_name, version, ecosystem, layer)` tuples. This SBOM can be exported in SPDX or CycloneDX format for compliance purposes.

**Phase 4 — Vulnerability database lookup**
Each SBOM entry is matched against an advisory database. Trivy uses its own bundled advisory database (updated daily from NVD, OSV, GitHub Advisory). For each match: CVE ID, CVSS score, severity, fixed version, and description are retrieved.

```
┌──────────────────────────────────────────────────────────┐
│        Trivy Output Sample                               │
├───────────────────┬───────────┬──────────┬──────────────┤
│ Package           │ Version   │ Severity │ Fixed in     │
├───────────────────┼───────────┼──────────┼──────────────┤
│ libssl1.1         │ 1.1.1n-0  │ CRITICAL │ 1.1.1t-0     │
│ libc-bin          │ 2.31-13   │ HIGH     │ 2.31-13+deb  │
│ log4j-core        │ 2.14.1    │ CRITICAL │ 2.17.1       │
└───────────────────┴───────────┴──────────┴──────────────┘
```

**Phase 5 — Policy gate**
The scanner's exit code reflects policy outcome: `0` = pass, `1` = fail. CI/CD pipelines (`GitHub Actions`, `GitLab CI`, `Jenkins`) read this exit code to block or allow the image push. Policy configuration specifies severity thresholds, exception lists (ignored CVEs with justification), and grace periods.

**Secret scanning** runs in parallel: regex patterns match common secret formats (AWS Access Key IDs: `AKIA[0-9A-Z]{16}`, private key markers `-----BEGIN RSA PRIVATE KEY-----`). Entropy analysis catches random-looking strings that don't match known patterns.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer push → CI pipeline triggers
  → docker build (Dockerfile → image)
  → trivy image <image> ← YOU ARE HERE
      ↓ SBOM extracted
      ↓ CVE database queried
      ↓ Policy evaluated
  → PASS → docker push → registry
  → CD pulls image → deploy to cluster
```

**FAILURE PATH:**
```
trivy reports CRITICAL CVE
  → pipeline exit code 1
  → image NOT pushed to registry
  → developer notified (CI log + Slack alert)
  → fix: update base image or dependency
  → rebuild → re-scan → PASS → push
```

**WHAT CHANGES AT SCALE:**
At scale, scanning latency becomes a concern: `trivy image` on a 500MB image takes 30–90 seconds. Organisations run scanning in parallel with other CI steps and cache the vulnerability database locally. For continuous compliance, registries (ECR, GCR, Harbor) run rescan jobs nightly — an image that passed last week may be flagged today when new CVEs are published. At 10,000+ images, vulnerability management becomes a platform problem: dashboards, SLA-based remediation workflows, and suppression management are required.

---

### 💻 Code Example

**Example 1 — Basic Trivy scan:**
```bash
# Scan an image and print all findings
trivy image nginx:1.25.3

# Fail if any CRITICAL vulnerability found (for CI/CD)
trivy image --exit-code 1 --severity CRITICAL nginx:1.25.3

# Output as JSON for further processing
trivy image --format json --output report.json nginx:1.25.3
```

**Example 2 — CI/CD pipeline integration (GitHub Actions):**
```yaml
# .github/workflows/scan.yml
- name: Build Docker image
  run: docker build -t myapp:${{ github.sha }} .

- name: Run Trivy image scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: "myapp:${{ github.sha }}"
    format: "sarif"
    output: "trivy-results.sarif"
    severity: "CRITICAL,HIGH"
    exit-code: "1"        # fail pipeline on findings

- name: Upload scan results to GitHub Security
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: "trivy-results.sarif"
```

**Example 3 — Generate and export SBOM (CycloneDX):**
```bash
# Generate SBOM in CycloneDX JSON format
trivy image --format cyclonedx \
  --output sbom.json \
  myapp:latest

# Use Grype to scan a previously generated SBOM
grype sbom:sbom.json
```

**Example 4 — Ignoring false positives with .trivyignore:**
```
# .trivyignore — suppress accepted risks with justification
# Format: CVE-ID [expiry-date] [reason]

# Accepted: debian backport applied, not in NVD yet
CVE-2023-12345

# Accepted: dev-dependency only, not included in final image
CVE-2024-99999 exp:2025-01-01
```

---

### ⚖️ Comparison Table

| Scanner | Language Ecosystems | Speed | Secret Scanning | Best For |
|---|---|---|---|---|
| **Trivy** | OS + Java, npm, Python, Go, Ruby | Fast (cached DB) | Yes | All-purpose, CI/CD default |
| Grype | OS + major ecosystems | Fast | No | Anchore integration |
| Snyk Container | OS + major ecosystems | Medium | Yes | Snyk platform users |
| Docker Scout | OS + major ecosystems | Fast | Basic | Docker Desktop users |
| Clair | OS packages only | Slow (API-based) | No | On-prem registry integration |

How to choose: Trivy is the de facto standard for open-source use — fast, comprehensive, and CI-friendly. Snyk Container adds developer-experience features (fix PRs, license scanning) for teams already using the Snyk platform.

---

### 🔁 Flow / Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│         Image Scan Lifecycle                             │
├──────────────────────────────────────────────────────────┤
│  BUILD TIME                                              │
│  Dockerfile → docker build → image artifact              │
│       ↓                                                  │
│  SCAN GATE (CI)                                          │
│  trivy/grype/snyk → SBOM → CVE match → policy           │
│       ↓ PASS           ↓ FAIL                            │
│  PUSH TO REGISTRY   Build broken → dev fixes             │
│       ↓                                                  │
│  REGISTRY SCAN (continuous)                              │
│  Registry re-scans on new CVE DB update                  │
│       ↓ new CVE found                                    │
│  ALERT → team notified → image deprecated               │
│       ↓                                                  │
│  ADMISSION CONTROL (Kubernetes)                          │
│  OPA Gatekeeper / Kyverno block unscanned images         │
└──────────────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "If the image passed scan yesterday, it's safe today" | CVE databases update daily. A passing image becomes failing the moment a new advisory matches one of its packages. Re-scan continuously, not just at build time. |
| "Image scanning catches all vulnerabilities" | Scanning only catches *known* CVEs. Zero-days, logic flaws, misconfigurations in application code, and runtime exploits are invisible to static image analysis. |
| "A zero-vulnerability image is a secure image" | A zero-CVE image running as root with write access to the host filesystem, mounting `/var/run/docker.sock`, is critically insecure. CVEs are one dimension of security; runtime posture is another. |
| "All CRITICAL CVEs must be fixed immediately" | Many CRITICAL OS CVEs are in code paths your application never invokes, or have been backport-patched by the distribution without an NVD record update. Triage before panic. |
| "I don't need to scan if I use distroless images" | Distroless images dramatically reduce the scanning surface but do not eliminate CVEs. The JRE, glibc, OpenSSL, and CA cert packages they include are still subject to advisories. |
| "Scanning is the CI team's responsibility, not developers'" | Developers own service security. Scanner failures should appear in the developer's PR, not in a separate security console. Shift LEFT — developer feedback loop is essential. |

---

### 🚨 Failure Modes & Diagnosis

**Stale vulnerability database**

**Symptom:**
Scanner reports no findings but you know a CVE should be present. Or findings differ between local developer scans and CI.

**Root Cause:**
Trivy and Grype maintain a local vulnerability database cache. If the cache is stale (not updated in 24+ hours), new CVEs are invisible.

**Diagnostic Command / Tool:**
```bash
# Check Trivy DB age
trivy image --download-db-only 2>&1 | head
# Or check last update
ls -la ~/.cache/trivy/db/

# Force refresh
trivy image --reset --download-db-only
```

**Fix:**
In CI, always pass `--skip-db-update=false` (default) or use `--download-db-only` as a preparation step. Pin the scanner version and update it weekly.

**Prevention:**
Configure CI to pull a fresh scanner DB at the start of every pipeline run.

---

**False-positive suppression bloat (ignored CVEs accumulate)**

**Symptom:**
`.trivyignore` file grows to hundreds of entries. The gate passes but nobody knows which suppressions are still justified.

**Root Cause:**
Teams add CVE suppressions to "unblock" CI without documenting expiry or justification. Over time the gate becomes meaningless.

**Diagnostic Command / Tool:**
```bash
# Audit your ignore file for expired entries
while IFS= read -r line; do
  [[ "$line" =~ CVE ]] && echo "Check: $line"
done < .trivyignore
```

**Fix:**
Require expiry dates and justification comments for every suppression. Enforce via pre-commit hook that rejects `.trivyignore` entries without comments.

**Prevention:**
Policy: every suppression requires a ticket reference, a justification, and an expiry date. Review suppressions as part of quarterly security reviews.

---

**Scanner not blocking on CRITICAL (wrong configuration)**

**Symptom:**
CI passes. Production contains images with CRITICAL CVEs. Post-incident analysis reveals `--exit-code 0` in the pipeline configuration.

**Root Cause:**
The scanner ran but was configured to report only, not to gate. Common in initial setup when teams add scanning but don't want to "break" CI.

**Diagnostic Command / Tool:**
```bash
# Verify scanner returns non-zero on findings
trivy image --severity CRITICAL --exit-code 1 nginx:1.21 ; echo "Exit: $?"
```

**Fix:**
```yaml
# BAD — scanner runs but never fails pipeline
- run: trivy image myapp:latest

# GOOD — scanner fails pipeline on CRITICAL
- run: trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

**Prevention:**
Treat scanner configuration as security-critical code. Require review for changes to `--exit-code`, `--severity`, or `.trivyignore`.

---

**Registry re-scan not triggering redeployment**

**Symptom:**
Registry shows newly-discovered CRITICAL CVE on a running image. No alert is triggered. Vulnerable containers remain running for weeks.

**Root Cause:**
Registry scanning (ECR, Harbor, GCR) flags newly-vulnerable images but most registries do not integrate with Kubernetes to force pod redeployment.

**Diagnostic Command / Tool:**
```bash
# ECR: list images with CRITICAL findings
aws ecr describe-image-scan-findings \
  --repository-name myapp \
  --image-id imageTag=latest \
  --query 'imageScanFindings.findings[?severity==`CRITICAL`]'
```

**Fix:**
Implement a Kubernetes admission webhook (Kyverno, OPA Gatekeeper) that rejects images with unpatched CRITICAL CVEs from being scheduled. Pair with an image rebuild automation (Renovate Bot, Dependabot).

**Prevention:**
Design the closed-loop: CVE advisory → registry re-scan alert → automated PR → image rebuild → redeploy. The full loop must be automated for scale.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker Image` — image scanning operates on the image layer structure; understanding layers is essential to understand what is scanned
- `Docker Layer` — CVEs can exist in any layer; base image layers are the most common source
- `Container Security` — image scanning is one pillar of container security, not the complete picture
- `Distroless Images` — distroless images minimise the scanning surface; understand them to reduce findings

**Builds On This (learn these next):**
- `Image Provenance / SBOM` — the SBOM produced during scanning is the foundation for supply chain security and attestation
- `Container Runtime Interface (CRI)` — admission controllers at the CRI level can enforce scan-based policies
- `CI/CD` — image scanning must be embedded in CI/CD pipelines to be effective

**Alternatives / Comparisons:**
- `Container Security` — broader concept covering runtime security, network policies, and RBAC — scanning is a subset
- `OCI Standard` — the OCI image format is what scanners parse; understanding OCI explains why scanners work across registries
- `Distroless Images` — a complementary defence: reduce the attack surface so there is less to scan

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automated CVE/secret scan of image layers │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Known-vulnerable packages silently ship   │
│ SOLVES       │ to production with no detection           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Scanning must GATE the pipeline (exit 1)  │
│              │ — reporting without blocking is theatre   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every container build — no exceptions     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — suppress specific false      │
│              │ positives with documented justification   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Earlier gates vs false-positive friction  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A scanner that doesn't fail the build    │
│              │  is just a very expensive rubber stamp"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Image Provenance / SBOM →                 │
│              │ OCI Standard → Container Runtime (CRI)   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team's image scanning policy gates on CRITICAL severity. The CVE database is updated and five new HIGH severity CVEs appear in your production image's base layer — none qualify as CRITICAL. Your security team argues these HIGH CVEs collectively represent a CRITICAL-equivalent risk path because they chain together. How would you revise your scanning policy to capture compound-risk scenarios? What tooling supports this, and what trade-offs does a stricter policy introduce for developer velocity?

**Q2.** You adopt distroless images company-wide and your scanner reports zero CVEs on every image. Six months later a zero-day exploit in the JVM's class deserialization path is published. Trace step-by-step why image scanning provided no protection, what controls *would* have detected or prevented exploitation, and how you would redesign your security architecture to handle zero-days in runtimes you cannot remove from distroless images.

