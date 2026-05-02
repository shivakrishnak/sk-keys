---
layout: default
title: "Container Scanning"
parent: "CI/CD"
nav_order: 1011
permalink: /ci-cd/container-scanning/
number: "1011"
category: CI/CD
difficulty: ★★★
depends_on: Dependency Scanning, Docker, Container, CI/CD Pipeline
used_by: SBOM, Supply Chain Security, Kubernetes Security
related: Dependency Scanning, SAST, DAST, SCA
tags:
  - cicd
  - security
  - containers
  - devops
  - deep-dive
---

# 1011 — Container Scanning

⚡ TL;DR — Container scanning inspects Docker images layer by layer for OS-level CVEs and misconfigurations that language-level dependency scanning completely misses.

| #1011 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Dependency Scanning, Docker, Container, CI/CD Pipeline | |
| **Used by:** | SBOM, Supply Chain Security, Kubernetes Security | |
| **Related:** | Dependency Scanning, SAST, DAST, SCA | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java microservice team runs `npm audit` and OWASP Dependency Check on every PR. All application-layer dependencies pass. The Docker image ships with `ubuntu:20.04` as the base — which pulls in `libssl1.1`, `curl`, `bash`, and 400 other OS packages, many with known CVEs. The scans never touch any of these. The container runs in Kubernetes with root-level access and an unpatched OpenSSL version (CVE-2022-0778, CVSS 7.5) that allows a remote attacker to cause an infinite loop and denial-of-service. The team never knew. Application security and OS security lived in completely separate, unconnected silos.

**THE BREAKING POINT:**
Containers bundle an entire OS userland alongside your application. A secure Node.js app running on a `node:14` image (which defaults to Debian Bullseye) inherits every CVE in that Debian image — and Debian Bullseye ships with hundreds of packages you never asked for. Traditional dependency scanners only understand package manifests (`package.json`, `pom.xml`) — they have no concept of `apt`, `rpm`, or Alpine `apk` packages.

**THE INVENTION MOMENT:**
This is exactly why container scanning exists: inspect the image filesystem layer by layer, identify every installed OS package, and cross-reference each against vulnerability databases — closing the gap between application-layer and OS-layer security.

---

### 📘 Textbook Definition

**Container scanning** is the automated inspection of container images (Docker, OCI) to identify security vulnerabilities in OS-level packages, application dependencies embedded directly in the image, misconfigurations in the Dockerfile, and embedded secrets. Scanners parse each layer of the image filesystem using CycloneDX or SPDX formats, extract installed package manifests (`dpkg`, `rpm`, `apk`), and cross-reference against NVD, OSV, and distribution-specific advisories (Debian Security Tracker, Red Hat OVAL). Unlike dependency scanning (which reads CI-sourced `package.json` manifests), container scanning reads what is actually installed inside a built and tagged image at any point in its lifecycle.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Scan what's actually inside your Docker image, not just what's in your `package.json`.

**One analogy:**
> Dependency scanning checks the ingredients list on a box of cereal. Container scanning breaks open the box, extracts every physical component, and tests each one independently — including the cardboard box itself. The label can say "no harmful additives," but the container might still have something dangerous you didn't intentionally add.

**One insight:**
The critical distinction between dependency scanning and container scanning is the scope: application-level packages (`npm`, `mvn`) vs OS-level packages (`dpkg`, `rpm`, `apk`). A pristine Node.js application with zero CVEs can still run on a base image carrying 50 OS-level vulnerabilities. Container scanning is the only control that sees both layers simultaneously.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A container image is an ordered stack of immutable filesystem layers — each layer adds, modifies, or removes files.
2. OS packages installed via `apt`, `yum`, or `apk` are tracked in package manager databases inside the image, not in application manifests.
3. Any file present on the running container filesystem is in scope — including files added by base images the developer never consciously chose.

**DERIVED DESIGN:**
Because a container image is a layered filesystem snapshot, a scanner must unpack each layer (OCI tar archives), overlay them in order to reconstruct the complete filesystem, and then run package manager detection (look for `/var/lib/dpkg/status`, `/var/lib/rpm/Packages`, `/lib/apk/db/installed`). This gives the exact installed version of every OS package. The scanner then queries CVE databases that have OS-specific data — NVD alone is insufficient because many OS vendors backport security fixes without changing version numbers, so scanners must also query vendor-specific advisory feeds (Debian Security Tracker, Red Hat OVAL, Alpine secdb).

Container scanners also inspect application manifests found inside the image (e.g., `node_modules/` or a copy of `pom.xml`) — giving them dual coverage of both OS and application layers in a single scan.

Dockerfile misconfiguration detection is a third scanning dimension: detecting `USER root`, exposed unnecessary ports, secrets in `ENV` or `ARG`, missing `--no-cache` flags, and large unnecessary layers.

**THE TRADE-OFFS:**
**Gain:** Complete security coverage of the entire container surface — OS + application + configuration.
**Cost:** Slower than manifest-only dependency scans (image pull + extraction takes 30–120 seconds). Generates high-volume findings, requiring aggressive base-image pinning strategies and a well-defined triage process to remain actionable.

---

### 🧪 Thought Experiment

**SETUP:**
A team deploys a Python Flask API in a Docker container. The application code has zero CVEs — clean `pip audit`. The Dockerfile uses `FROM python:3.9` (which pulls Debian Buster). No container scanning in CI.

**WHAT HAPPENS WITHOUT CONTAINER SCANNING:**
Debian Buster ships with `libexpat1 2.2.6` which has CVE-2022-25236 (XML injection, CVSS 9.8). The Python application doesn't use `libexpat` directly — but `curl` (present in the base image) does. An attacker exploits a lateral vector through curl in the running container. The team's vulnerability dashboard shows zero findings. Incident post-mortem traces back to an OS package that no developer on the team ever installed.

**WHAT HAPPENS WITH CONTAINER SCANNING:**
Trivy scans the image at build time: `FROM python:3.9` → `libexpat1 2.2.6` → CVE-2022-25236 → CRITICAL. CI pipeline fails before the image reaches any registry. Developer updates Dockerfile to `FROM python:3.9-slim-bullseye` (newer Debian, patched libexpat). Rescan: clean. Image pushed. The vulnerability never reached production.

**THE INSIGHT:**
The threat surface of a container is the sum of every package in the image — not just what the developer explicitly installed. Container scanning is the only way to make the full surface visible before runtime.

---

### 🧠 Mental Model / Analogy

> Container scanning is like a full building inspection before occupancy — not just a review of the architect's blueprints. The blueprints (your `Dockerfile`) show what you intended to include. The inspection reveals what is physically present in the walls, floors, and utility systems — including materials the contractor sourced from suppliers you've never heard of.

- "Building blueprints" → `Dockerfile` / application manifests
- "Contractor-sourced materials" → base image OS packages
- "Building inspector" → Trivy / Grype / Snyk Container
- "Prohibited materials list" → NVD + vendor advisory databases
- "Certificate of occupancy" → image pushed to registry after clean scan
- "Unpermitted renovation" → packages added by base image layers

Where this analogy breaks down: building materials don't self-update after construction — but container base images can be patched daily. Even a previously clean image can become vulnerable as new CVEs are published against its OS packages.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you build a Docker container, you get a whole mini-operating-system bundled with your app. Container scanning checks every piece of that mini-OS for known security problems — the same way a building inspector checks every material in a new house, not just the paint you chose.

**Level 2 — How to use it (junior developer):**
Add Trivy or Grype to your CI pipeline after the `docker build` step. Run `trivy image myapp:latest` — it will list every CVE in both OS packages and application dependencies. For GitHub Actions, use `aquasecurity/trivy-action`. Set `--exit-code 1 --severity CRITICAL,HIGH` to fail builds on serious findings. Update base images frequently: prefer `FROM node:20-alpine` over `FROM node:20` to reduce the OS attack surface.

**Level 3 — How it works (mid-level engineer):**
Trivy extracts the image manifest (list of layer digests), fetches each layer (OCI tar), overlays the layers in order using Union FS semantics, then detects OS package managers by checking for their database files. For Debian: `/var/lib/dpkg/status`. For Alpine: `/lib/apk/db/installed`. For RPM: `/var/lib/rpm/Packages`. Each database entry gives exact package name + version. These are matched against Trivy's embedded vulnerability database (updated daily from NVD, OSV, and OS-specific feeds). Trivy also runs its own Dockerfile linting (via Conftest policies), scanning for `USER root`, unset `HEALTHCHECK`, exposed ports, and large layer anti-patterns.

**Level 4 — Why it was designed this way (senior/staff):**
The layered approach emerged because OCI images use content-addressable storage — each layer is a sha256-digested tar file. Scanners cache layer results by digest, making incremental rescanning fast: only changed layers need re-analysis. The vulnerability database embeds OS-specific advisory data because NVD CVSS scores alone are insufficient — many vendors backport patches without changing the upstream version number. Without vendor-specific advisories, scanners would produce massive false positives against Debian and RHEL packages. The emerging SLSA (Supply Levels for Software Artifacts) framework extends container scanning to provenance: not just "is this version vulnerable?" but "can I verify which source commit produced this image?" Image signing (cosign + Sigstore) and SBOMs are the next layer of the supply chain model.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│     CONTAINER SCANNING EXECUTION        │
├─────────────────────────────────────────┤
│  Input: docker image tag / OCI archive  │
│                                         │
│  STEP 1: Fetch image manifest           │
│  → list of layer sha256 digests         │
│                                         │
│  STEP 2: Extract & overlay layers       │
│  Layer 0: FROM ubuntu:22.04             │
│  Layer 1: RUN apt-get install curl      │
│  Layer 2: COPY app/ /app/               │
│  → merged virtual filesystem           │
│                                         │
│  STEP 3: OS package detection           │
│  /var/lib/dpkg/status → apt packages   │
│  /lib/apk/db/installed → apk packages  │
│  /var/lib/rpm/Packages → rpm packages  │
│                                         │
│  STEP 4: App dependency detection       │
│  /app/node_modules → npm packages      │
│  /app/go.sum → Go modules              │
│  /app/requirements.txt → pip packages  │
│                                         │
│  STEP 5: CVE lookup (embedded DB)       │
│  curl 7.81.0 → CVE-2022-32206 HIGH     │
│  libssl1.1 → CVE-2022-0778 HIGH        │
│                                         │
│  STEP 6: Policy evaluation              │
│  CRITICAL/HIGH → fail build             │
│                                         │
│  STEP 7: Report + SBOM output (optional)│
│  JSON / SARIF / CycloneDX              │
└─────────────────────────────────────────┘
```

**Trivy vulnerability database update cycle:**
Trivy embeds a compressed vulnerability database that is rebuilt hourly from NVD, GitHub Advisory, OSV, and distro-specific feeds (Debian Security Tracker, Red Hat OVAL, Alpine secdb, Ubuntu USN). The database is cached locally at `~/.cache/trivy/`. In CI, the database is downloaded fresh each run unless explicitly cached. Stale databases (>24 hours in air-gapped environments) produce missed findings.

**Image scanning vs runtime scanning:**
- **Image scanning** (pre-deployment): scan the OCI image before it enters the registry. Fast, shift-left.
- **Registry scanning**: scan images already in ECR/GCR/ACR continuously as new CVEs publish. Catches regressions without new code commits.
- **Runtime scanning** (Falco, eBPF): detect active exploitation attempts and unexpected syscalls. Complements static scanning with live observation.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer commits code
  → CI triggered
  → Unit tests pass
  → docker build myapp:sha-abc123
  → Container scan [← YOU ARE HERE]
     trivy image myapp:sha-abc123
     → CRITICAL: libssl CVE-2022-0778
     → HIGH: curl CVE-2022-32206
  → Build fails
  → Developer updates: FROM node:20-alpine
  → Rebuild → rescan: CLEAN
  → Image pushed to ECR
  → Kubernetes deploys image
```

**FAILURE PATH:**
```
Container scan misconfigured (--exit-code 0)
  → Critical CVEs not blocking pipeline
  → Vulnerable image pushed to registry
  → Kubernetes admits workload
  → CVE exploited at runtime
  → Observable symptom: unexpected outbound connections,
    high CPU from DoS exploit, privilege escalation alert
```

**WHAT CHANGES AT SCALE:**
At 100+ microservices, all sharing 4–5 base images, a single base image CVE generates identical findings across dozens of pipelines simultaneously. Teams implement a base image governance layer: a central team owns `approved-base-images` versions pinned in an internal registry, and all service teams must use approved bases. Dependabot or Renovate creates automated PRs against the base image registry when new CVE-free versions are published. This converts 100 simultaneous CVE alerts into 1 central base image upgrade.

---

### 💻 Code Example

**Example 1 — Basic Trivy scan (CLI):**
```bash
# Scan a local image after docker build
trivy image --severity CRITICAL,HIGH myapp:latest

# Output to JSON for downstream processing
trivy image --format json --output report.json \
  myapp:latest

# Fail CI if CRITICAL/HIGH found (exit code 1)
trivy image --exit-code 1 \
  --severity CRITICAL,HIGH \
  --ignore-unfixed \
  myapp:latest
# --ignore-unfixed: skip CVEs with no available fix
# (no patch = no actionable remediation)
```

**Example 2 — GitHub Actions with Trivy:**
```yaml
# .github/workflows/container-scan.yml
name: Container Scan
on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          exit-code: 1
          ignore-unfixed: true

      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif
```

**Example 3 — Dockerfile hardening patterns:**
```dockerfile
# BAD: large attack surface, runs as root
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["node", "server.js"]

# GOOD: minimal base, non-root user, pinned digest
FROM node:20-alpine3.19@sha256:abc123...
# Alpine has ~40% fewer packages than Debian
# → smaller CVE surface
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
# --omit=dev removes devDependencies from image
COPY . .
# Run as non-root user (principle of least privilege)
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup
USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
```

**Example 4 — Suppressing accepted risk:**
```yaml
# .trivyignore
# Accepted CVE: CVE-2022-XXXX
# Reason: library used in build stage only,
#         not present in final image.
# Accepted by: security@company.com
# Review date: 2026-07-01
CVE-2022-XXXX
```

---

### ⚖️ Comparison Table

| Tool | OS Packages | App Packages | Dockerfile Lint | SBOM Output | Free |
|---|---|---|---|---|---|
| **Trivy** | Yes | Yes | Yes | Yes (CycloneDX/SPDX) | Yes |
| Grype (Anchore) | Yes | Yes | No | No (use Syft separately) | Yes |
| Snyk Container | Yes | Yes | Yes | Yes | Limited |
| Clair | Yes | No | No | No | Yes |
| AWS ECR Scan | Yes | No | No | No | Yes (Basic) |
| Docker Scout | Yes | Yes | Yes | Yes | Limited |

How to choose: Use **Trivy** as the default for its breadth (OS + app + Dockerfile + SBOM in one tool) and zero cost. Use **Snyk Container** when you need developer-friendly triage UI and IDE integration. Use **Clair** or **AWS ECR Scan** in high-compliance air-gapped environments where SaaS calls to external APIs are prohibited.

---

### 🔁 Flow / Lifecycle

```
┌─────────────────────────────────────────┐
│  CONTAINER IMAGE SECURITY LIFECYCLE     │
├─────────────────────────────────────────┤
│                                         │
│  1. BUILD (CI)                          │
│     docker build → trivy scan           │
│     FAIL → developer fixes base image  │
│     PASS → continue                    │
│                                         │
│  2. PUSH (Registry)                     │
│     Image tagged + pushed to ECR/GCR   │
│     Registry scanner runs on admission  │
│     (ECR Enhanced Scanning / Snyk)     │
│                                         │
│  3. DEPLOY (Kubernetes)                 │
│     Admission controller checks policy  │
│     (OPA Gatekeeper / Kyverno)          │
│     No clean scan = pod rejected        │
│                                         │
│  4. RUNTIME (Post-deploy)               │
│     New CVE published → registry alert  │
│     Automated PR: bump base image tag  │
│     Re-pipeline → rescan → redeploy    │
│                                         │
│  ERROR PATH:                            │
│     Scan skipped → vulnerable image →  │
│     CVE exploited → incident →          │
│     retroactive emergency patching     │
└─────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Dependency scanning covers containers | Dependency scanning reads language manifests (`package.json`, `pom.xml`). Container scanning reads OS package databases inside the image. They are complementary — neither replaces the other. |
| A clean `npm audit` means the container is secure | The application layer may be clean, but the base image may carry dozens of OS-level CVEs that `npm audit` never touches. |
| Multi-stage builds eliminate all vulnerabilities | Multi-stage builds reduce the attack surface by discarding build tools, but the final stage still inherits OS packages from its base image — which must still be scanned. |
| Alpine images are always safe | Alpine images have a small package set, but they still carry CVEs. Alpine is a better starting point, not a guarantee of a clean scan. |
| Pinning image digest freezes CVE state | Pinning a digest freezes the image — but new CVEs are discovered against existing packages continuously. A pinned image becomes increasingly vulnerable over time without active rescanning. |
| Scanning only needs to happen at build time | Images in registries accumulate new CVEs as databases update. Registry-level continuous scanning catches post-deployment regressions without requiring a new commit. |

---

### 🚨 Failure Modes & Diagnosis

**1. Base Image with Hundreds of Unfixed CVEs**

**Symptom:** Every container scan fails with 200+ findings, blocking all builds. Half have no available fix versions.

**Root Cause:** Using `FROM ubuntu:latest` or `FROM node:18` (Debian-based) pulls in a full distribution with many unmaintained packages. "No fix available" means the CVE exists in a library that has not yet published a patched version.

**Diagnostic:**
```bash
# Count CVEs by severity and fixable status
trivy image --format json myapp:latest | \
  jq '.Results[].Vulnerabilities[]? |
  {sev: .Severity, fixed: (.FixedVersion // "none")}' | \
  sort | uniq -c | sort -rn

# Find which OS packages drive most CVEs
trivy image --format json myapp:latest | \
  jq '[.Results[].Vulnerabilities[]? |
  select(.FixedVersion == null)] |
  group_by(.PkgName) |
  map({pkg: .[0].PkgName, count: length}) |
  sort_by(-.count) | .[0:10]'
```

**Fix:**
```dockerfile
# BAD: Debian-based with hundreds of packages
FROM node:18

# GOOD: Alpine-based — minimal package set
FROM node:20-alpine3.19

# BEST: distroless — only runtime, no shell/package manager
FROM gcr.io/distroless/nodejs20-debian12
```

**Prevention:** Establish an approved base image registry with images pre-scanned and updated weekly. Enforce via Dockerfile linting in CI (Hadolint rule DL3006: always tag base images).

---

**2. Scanner Database Stale in Air-Gapped CI**

**Symptom:** CI passes with 0 findings. Security team's standalone scan finds 15 CVEs on the same image.

**Root Cause:** Trivy's embedded database is cached and not refreshed in CI (air-gapped environment or aggressive caching). The cached database is 7+ days old, missing newly published CVEs.

**Diagnostic:**
```bash
# Check age of local Trivy DB
trivy image --download-db-only 2>&1 | grep "DB"

# Force database refresh
trivy image --reset && trivy image myapp:latest

# Check database metadata
cat ~/.cache/trivy/db/metadata.json | jq '.UpdatedAt'
```

**Fix:**
```yaml
# In CI: always download fresh DB before scanning
- name: Update Trivy DB
  run: trivy image --download-db-only

- name: Scan image
  run: trivy image --skip-db-update myapp:latest
# Use --skip-db-update after explicit download step
# to prevent double downloads in the same job
```

**Prevention:** In air-gapped environments, mirror the Trivy database to an internal registry using `trivy image --download-db-only` + OCI push to internal registry. Configure CI to pull from mirror. Automate mirror refresh on a schedule.

---

**3. False Negatives from Distro Backporting**

**Symptom:** Trivy reports `libssl 1.1.1f` as CLEAN. Manual CVE research shows CVE-2022-0778 affects `libssl < 1.1.1n`. This seems like a missed finding.

**Root Cause:** Debian backports security fixes into old version numbers. `libssl 1.1.1f-1ubuntu2.15` contains the fix for CVE-2022-0778, even though the version number `1.1.1f` is below the upstream fix threshold `1.1.1n`. Trivy uses OS-specific advisory databases (Ubuntu USN) to handle backported fixes correctly.

**Diagnostic:**
```bash
# Verify Trivy uses OS-specific advisory sources
trivy image --debug ubuntu-app:latest 2>&1 | \
  grep -E "(ubuntu|debian|oval)"

# Check which vulnerability sources are active
trivy image --list-all-pkgs --format json \
  ubuntu-app:latest | jq '.Results[].Type'
```

**Fix:** Ensure Trivy's vulnerability database includes OS-specific feeds. Do NOT manually override Trivy findings based purely on upstream CVE version ranges — trust the scanner's OS-aware database. If a finding is suppressed, document the OS advisory that confirms the fix.

**Prevention:** Use scanners that maintain OS-specific advisory databases (Trivy, Grype, Snyk Container). Avoid lightweight scanners that only use NVD without OS feeds.

---

**4. Missing Secrets Embedded in Image Layers**

**Symptom:** A production incident reveals `AWS_SECRET_ACCESS_KEY=...` was hard-coded in an intermediate build layer that was supposed to be removed in a multi-stage build but leaked into the final image history.

**Root Cause:** `docker history` reveals environment variables set in intermediate layers using `ARG` or `ENV` remain in the image manifest even after deletion in subsequent layers. Container scanning tools like Trivy and Snyk Container include secret scanning to detect credentials in image layers.

**Diagnostic:**
```bash
# Inspect all image layers for env vars
docker history --no-trunc myapp:latest | grep -i secret

# Use Trivy secret scan mode
trivy image --scanners secret myapp:latest

# Inspect image config for embedded env vars
docker inspect myapp:latest | jq '.[].Config.Env'
```

**Fix:**
```dockerfile
# BAD: ARG leaks into image history
ARG AWS_SECRET_ACCESS_KEY
RUN deploy.sh

# GOOD: pass secrets at runtime via env vars
# Never bake secrets into build-time image
# Use: docker run -e AWS_SECRET_ACCESS_KEY=... myapp
# Or: Kubernetes Secrets mounted as env vars
```

**Prevention:** Add `trivy image --scanners secret` to CI. Enforce no-secrets-in-Dockerfiles rule via Hadolint. Use BuildKit secret mounts (`--secret id=...`) for credentials needed only at build time.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker` — containers are the subject of scanning; understanding layers and image builds is required
- `Dependency Scanning` — covers the application-layer scanning that container scanning extends to OS packages
- `CI/CD Pipeline` — container scanning runs as a CI pipeline stage after `docker build`
- `SCA (Software Composition Analysis)` — the broader practice of which container scanning is the container-specific implementation

**Builds On This (learn these next):**
- `SBOM (Software Bill of Materials)` — container scanning produces SBOMs as a formal inventory of all image components
- `Kubernetes Security` — Kubernetes admission controllers (Kyverno, OPA Gatekeeper) enforce container scan policies at deploy time
- `Supply Chain Security` — extends container scanning to verify image provenance and integrity (cosign, Sigstore, SLSA)

**Alternatives / Comparisons:**
- `Dependency Scanning` — scans application manifest files only; container scanning scans the full image including OS packages
- `SAST` — scans first-party source code; container scanning scans the built image (including third-party OS components)
- `Runtime Security (Falco)` — detects active exploitation at runtime; container scanning is a pre-deployment static check

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Scan Docker images layer-by-layer for     │
│              │ OS packages + app CVEs + misconfigs       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ OS packages in base images carry CVEs     │
│ SOLVES       │ invisible to dependency scanning          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ A clean app layer + vulnerable base image │
│              │ = a vulnerable container. Both must scan. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — after every docker build in CI   │
│              │ + continuous registry scanning            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — but use --ignore-unfixed     │
│              │ to filter noise from unpatched CVEs       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full security coverage vs scan time       │
│              │ and base-image upgrade operational cost   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your app may be clean — but the OS       │
│              │  under it might not be."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SBOM → Supply Chain Security →            │
│              │ Kubernetes Security → Sigstore            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team uses `FROM node:20-alpine` for all services. Trivy shows 0 CRITICAL/HIGH CVEs today. Next month, Alpine publishes a security advisory for `musl libc` (Alpine's C library used by nearly every binary). Every one of your 80 microservices is affected. Design the complete automated response: how does the alert reach developers, how are the 80 Dockerfiles updated, tested, and deployed — without requiring 80 separate PRs with manual review?

**Q2.** A distroless base image (`gcr.io/distroless/java17`) has no OS package manager, no shell, and no binaries beyond the JVM. Trivy reports 0 OS-level findings. A security researcher claims there is still a meaningful attack surface. What categories of vulnerabilities would Trivy NOT detect in a distroless image, and what complementary controls would you need to ensure comprehensive coverage?

