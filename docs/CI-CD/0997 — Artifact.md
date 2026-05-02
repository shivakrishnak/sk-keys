---
layout: default
title: "Artifact"
parent: "CI/CD"
nav_order: 997
permalink: /ci-cd/artifact/
number: "0997"
category: CI/CD
difficulty: ★☆☆
depends_on: Build Stage, Pipeline, Version Control
used_by: Artifact Registry, Continuous Delivery, Deployment Pipeline
related: Artifact Registry, Docker Image, Build Stage
tags:
  - cicd
  - build
  - devops
  - foundational
---

# 0997 — Artifact

⚡ TL;DR — A CI/CD artifact is the immutable, versioned output of a build stage — the JAR, Docker image, or binary that gets tested and deployed rather than the raw source code.

| #0997 | Category: CI/CD | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Build Stage, Pipeline, Version Control | |
| **Used by:** | Artifact Registry, Continuous Delivery, Deployment Pipeline | |
| **Related:** | Artifact Registry, Docker Image, Build Stage | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team deploys by SSH-ing into a production server and running `git pull && mvn package`. Every deployment re-downloads dependencies, recompiles, and produces a new binary directly on the production server. If a Maven Central repository is unreachable during deployment, the production update fails. If the Java version on the server differs from development, the compiled output differs. If two servers are updated at slightly different times, they run slightly different code.

**THE BREAKING POINT:**
Deploying from source means production is a compilation environment, not a runtime environment. Every deployment is a build — non-reproducible, environment-dependent, and slow. There's no way to roll back to an exact previous version because the previous binary was never preserved.

**THE INVENTION MOMENT:**
This is exactly why artifacts exist: build once, store the result, deploy that frozen output everywhere — no recompilation, no environmental variation, instant rollback by re-deploying the previous artifact.

---

### 📘 Textbook Definition

A **CI/CD artifact** is the versioned, immutable output produced by the build stage of a CI/CD pipeline. Artifacts include compiled binaries (JAR, .NET DLL), container images (Docker), compressed archives (ZIP, TAR), installation packages (RPM, DEB), or cloud function deployment packages (ZIP). Each artifact is tagged with a unique identifier — typically the Git commit SHA or a semantic version — making it traceable to the exact source code that produced it. Artifacts are stored in an artifact registry and promoted through pipeline stages; the same artifact runs in staging and production.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An artifact is a frozen snapshot of your software — ready to run, not to compile.

**One analogy:**
> A software artifact is like a frozen meal. Instead of cooking from scratch every time (compiling from source), you cook once, freeze the result, and reheat it as needed. The frozen meal is identical every time it's served. You can also freeze multiple batches — version 1.2 and version 1.3 — and quickly serve the older one if the new one tastes wrong.

**One insight:**
The critical rule: **build once, deploy many times**. If you rebuild the artifact for each environment (staging, production), you're deploying different binaries — potentially with different compilation outcomes. Only the exact same binary that passed staging tests should reach production.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An artifact is immutable — once built, its content never changes.
2. An artifact is versioned — uniquely identified (commit SHA or semantic version).
3. An artifact is environment-agnostic — the same artifact runs in staging and production.

**DERIVED DESIGN:**
Immutability means the artifact tag must not be reusable. `myapp:latest` is not a valid artifact tag in a CD pipeline — `latest` can be overwritten. `myapp:sha-a3f8c21` is immutable and traceable. When a deployment fails, re-deploying the previous `sha-9f2a1bc` artifact takes 60 seconds because the binary already exists in the registry.

Version traceability connects the artifact to its provenance: which commit produced it, which tests passed, which developer authored the triggering PR. This chain is the audit trail for compliance and incident investigation.

**THE TRADE-OFFS:**
**Gain:** Reproducible, traceable deployments. Instant rollback. No production recompilation risk.
**Cost:** Artifact storage costs. Registry management (cleanup policies for old artifacts). Build infrastructure to produce artifacts reliably.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams deploy the same codebase to production. Team A rebuilds from source on the production server. Team B deploys a pre-built artifact.

**WHAT HAPPENS WITH TEAM A:**
Friday deployment: Maven Central has a 30-second timeout. The pom.xml references a dependency with a version range `[1.2,)`. Maven resolves to `1.2.3` — the newest version. Staging (built Monday) used `1.2.1`. Production now runs `1.2.3`, which has a subtle API change. Tests pass in staging, fail in production. "But it passed in staging!" — because staging ran a different binary.

**WHAT HAPPENS WITH TEAM B:**
Friday deployment: The pre-built Docker image `myapp:sha-a3f8c21` is pulled from the registry (built on Monday, used in staging). It runs identically in production because it's the exact same binary. Maven Central is not involved. Dependency version is baked into the frozen image.

**THE INSIGHT:**
"It passed in staging" is only trustworthy if staging and production ran the same binary. Artifacts make that guarantee. Source-based deployments cannot.

---

### 🧠 Mental Model / Analogy

> An artifact is like a sealed, stamped, certified package. A pharmaceutical company doesn't produce pills on-site at each pharmacy — they manufacture in a certified facility, seal the batch, stamp it with a lot number (version), and ship identical packages everywhere. If a batch is recalled, the lot number identifies exactly which packages to pull.

- "Sealed package" → immutable artifact
- "Lot number" → commit SHA or version tag
- "Certified manufacturing facility" → CI pipeline build stage
- "Shipped to each pharmacy identically" → same image deployed to staging and production
- "Batch recall using lot number" → rollback by re-deploying previous artifact version

Where this analogy breaks down: pharmaceutical packages degrade over time; software artifacts do not. But artifact registries do implement retention policies — old artifacts are eventually purged, which could limit rollback windows.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When developers' code is built by the CI system, it produces a single file (or small set of files) that contains everything needed to run the software. That file — the artifact — is stored and labelled with the exact code version it came from. Deploying means copying that pre-made file to a server, not rebuilding from scratch.

**Level 2 — How to use it (junior developer):**
In Java: `mvn package` produces a `target/myapp-1.0.0.jar`. In Docker: `docker build -t myapp:$(git rev-parse --short HEAD) .` produces a Docker image. Upload the artifact to a registry (Nexus, AWS ECR, GitHub Packages). Tag it with the Git commit SHA. In your CD pipeline, downstream stages reference this exact tag — never rebuild.

**Level 3 — How it works (mid-level engineer):**
Docker images are the dominant artifact format for modern deployments. An image contains the application binary, runtime (JRE, Node.js), and OS filesystem layers. It's identified by a digest (SHA256 hash of all layers) — completely immutable. The tag (`:sha-abc123`) is a pointer to the digest. Re-tagging is possible but the digest itself never changes. Artifact registries (ECR, GCR, Nexus, JFrog Artifactory) store and serve images efficiently using content-addressable layer deduplication.

**Level 4 — Why it was designed this way (senior/staff):**
The "build once, ship everywhere" principle traces back to package management in Unix (RPM, DEB) in the 1990s. Docker containers made it universal by bundling the runtime environment with the application. This solved the dependency hell problem that plagued traditional deployments. The next evolution is `SBOM` (Software Bill of Materials) — a machine-readable manifest of every dependency in an artifact, enabling automated vulnerability scanning of what's actually deployed, not just what's declared in source.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│         ARTIFACT LIFECYCLE                  │
├─────────────────────────────────────────────┤
│  SOURCE: code at commit sha-a3f8c21         │
│         ↓                                   │
│  BUILD STAGE                                │
│   - Compile source → myapp.jar              │
│   - Docker build → image layers             │
│   - Tag: myapp:sha-a3f8c21                  │
│         ↓                                   │
│  PUSH TO REGISTRY                           │
│   - AWS ECR / JFrog Artifactory             │
│   - Stored with digest + tag                │
│         ↓                                   │
│  TEST STAGE                                 │
│   - Pull: myapp:sha-a3f8c21                 │
│   - Run tests AGAINST this image            │
│         ↓ PASS                              │
│  STAGING DEPLOY                             │
│   - Pull: myapp:sha-a3f8c21                 │
│   - Staging runs this exact image           │
│         ↓ VALIDATED                         │
│  PRODUCTION DEPLOY                          │
│   - Pull: myapp:sha-a3f8c21 ← SAME IMAGE    │
│   - Production runs this exact image        │
│         ↓                                   │
│  RETAINED IN REGISTRY                       │
│   - Rollback: redeploy sha-9f2a1bc easily   │
└─────────────────────────────────────────────┘
```

**Content-addressed storage:** Docker images are stored by SHA256 digest. Tags are pointers. Two images with different tags but the same digest are the same image. Layer deduplication means the base OS layer (e.g., `eclipse-temurin:21-jre`) is stored once and shared across all images that use it — significant storage savings.

**Artifact promotion:** In enterprise pipelines, an artifact may be "promoted" between repositories. The same image in `mycompany/snapshots/myapp:sha-abc` is re-tagged to `mycompany/releases/myapp:1.2.3` after passing all tests. No rebuild — just a new tag pointing to the same digest. JFrog Artifactory's promotion API implements this pattern.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Build stage: mvn package + docker build
  → myapp:sha-a3f8c21 pushed to ECR [← YOU ARE HERE]
  → Test stage pulls sha-a3f8c21
  → 289 tests pass → image validated
  → CD: staging pulls sha-a3f8c21
  → Staging smoke tests pass
  → Production pulls sha-a3f8c21 (the same image)
  → Production runs stably
  → sha-a3f8c21 retained in registry for rollback
```

**FAILURE PATH:**
```
Production: errors spike → roll back needed
  → Identify previous stable: sha-9f2a1bc
  → kubectl set image deployment/myapp \
      myapp=mycompany/myapp:sha-9f2a1bc
  → Previous image pulled from registry (already cached)
  → Rollback complete in 60 seconds
  → No rebuild, no environment risk
```

**WHAT CHANGES AT SCALE:**
At 1000 microservices each building multiple times per day, artifact storage is a cost centre. Retention policies must balance rollback needs with storage costs: keep all artifacts for 30 days, then only tagged releases indefinitely. Vulnerability scanning (Trivy, Grype) must scan artifacts rather than source code — what's in the deployed image (transitive dependencies, base OS packages) is what actually matters.

---

### 💻 Code Example

**Example 1 — Build and tag artifact in CI:**
```bash
# In CI pipeline — build and push artifact with commit SHA tag
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="myorg/myapp:${COMMIT_SHA}"

# Build the Docker image
docker build -t "${IMAGE_TAG}" .

# Push to registry
docker push "${IMAGE_TAG}"

# Also tag as 'latest' for convenience (but use SHA for deploys)
docker tag "${IMAGE_TAG}" myorg/myapp:latest
docker push myorg/myapp:latest

echo "Artifact: ${IMAGE_TAG}"
```

**Example 2 — BAD vs GOOD: reusing mutable tags:**
```bash
# BAD: deploy using 'latest' tag
# 'latest' changes every build — you don't know what you deployed
kubectl set image deployment/myapp myapp=myorg/myapp:latest

# GOOD: deploy using immutable commit SHA tag
# You can audit exactly what code is running
kubectl set image deployment/myapp \
  myapp=myorg/myapp:sha-a3f8c21

# Even better: use the full digest for absolute immutability
kubectl set image deployment/myapp \
  myapp=myorg/myapp@sha256:abc123def456...
```

**Example 3 — Inspect artifact contents and scanning:**
```bash
# Check what's inside a Docker artifact
docker inspect myorg/myapp:sha-a3f8c21

# View image layers and sizes
docker history myorg/myapp:sha-a3f8c21

# Scan artifact for known vulnerabilities
trivy image myorg/myapp:sha-a3f8c21
# Output: vulnerabilities by severity in all packages
# including OS packages (apt), language packages (Maven)
```

---

### ⚖️ Comparison Table

| Artifact Type | Size | Runtime Included | Portability | Best For |
|---|---|---|---|---|
| **Docker Image** | 50–500 MB | Yes | Anywhere Docker runs | Most modern applications |
| JAR / Fat JAR | 10–100 MB | No (needs JVM) | JVM hosts only | Java apps on managed infra |
| ZIP / TAR | 1–50 MB | No (needs interpreter) | Environment-specific | Lambda functions, scripted apps |
| RPM / DEB | 1–50 MB | No | Linux distro-specific | System services on dedicated VMs |
| OCI Image | Same as Docker | Yes | OCI-compliant runtimes | Standards-compliant containerised apps |

How to choose: Default to Docker images for new services — they bundle the runtime, are universally supported, and work identically everywhere. Use JARs only on managed PaaS platforms (Elastic Beanstalk, Heroku) where the runtime is provided. Use Lambda ZIPs for serverless functions.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `latest` is a valid artifact tag for deployments | `latest` is mutable — it changes every build. Use commit SHA or semantic version for deployment tracking and rollback capability |
| Artifacts should be rebuilt for each environment | The same artifact must be used in all environments. Rebuilding introduces the risk of different binaries in staging and production |
| Artifacts expire with time | Artifacts (Docker images) are permanent until explicitly deleted. Registries require explicit retention policies to manage storage costs |
| Artifact size doesn't matter | Large images (1+ GB) significantly slow down deployment cold starts and node scale-up. Image size is a deployment performance measure |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing Artifact — Deployment Blocked**

**Symptom:** Deployment pipeline fails with "image not found" or "artifact does not exist." Production deployment blocked.

**Root Cause:** Retention policy deleted the artifact. Or build stage failed silently and never pushed the artifact. Or the tag was wrong.

**Diagnostic:**
```bash
# Verify artifact exists in registry
aws ecr describe-images \
  --repository-name myapp \
  --image-ids imageTag=sha-a3f8c21
# If missing: check build stage logs for push errors
```

**Fix:** Check build stage logs. Ensure the push step has retry logic. For immediate recovery: redeploy the previous known-good artifact.

**Prevention:** Implement artifact retention policy: never delete artifacts younger than 90 days. Alert when artifact count in a tag series drops unexpectedly.

---

**2. Artifact Mismatch Between Environments**

**Symptom:** "It worked in staging" — but production runs a different version of the code.

**Root Cause:** Pipeline doesn't enforce the same image tag between staging deploy and production deploy. Someone manually deployed a different tag to production.

**Diagnostic:**
```bash
# Check exactly what image is running
kubectl get deployment myapp -o yaml \
  | grep "image:"
# Compare staging vs production image SHA
kubectl get deployment myapp -n staging \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get deployment myapp -n production \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

**Fix:** Make the image tag an explicit pipeline input passed between stages, not a separately specified value.

**Prevention:** Pipeline design: staging and production deploy stages must reference the exact same `IMAGE_TAG` variable from the build stage output.

---

**3. Artifact Contains Known Vulnerabilities**

**Symptom:** Security scan alerts: critical CVE in the deployed Docker image. The vulnerability is in the base OS image packages.

**Root Cause:** Base image (`eclipse-temurin:21-jre`) has accumulated OS-level vulnerabilities since it was last refreshed. Application image inherits all base image vulnerabilities.

**Diagnostic:**
```bash
# Scan running image for CVEs
trivy image \
  --severity HIGH,CRITICAL \
  myorg/myapp:sha-a3f8c21
# Output: CVE-2024-XXXX in libssl 1.1.1, fix in 1.1.1w
```

**Fix:** Rebuild with `--no-cache` to fetch the latest base image. Update to a base image version with the patch.

**Prevention:** Add `trivy` or `grype` scan to the pipeline as a build stage gate. Fail builds if CRITICAL vulnerabilities are found. Set up weekly base image refresh builds.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Build Stage` — the pipeline stage that produces the artifact; no build stage, no artifact
- `Pipeline` — artifacts flow through pipeline stages; understanding the pipeline is needed to understand where artifacts fit
- `Version Control` — artifact versions trace back to specific commits; Git SHA is the standard artifact identifier

**Builds On This (learn these next):**
- `Artifact Registry` — the storage system where artifacts are pushed, stored, and pulled for deployment
- `Continuous Delivery` — the practice that treats each artifact as a potential production release
- `Container Scanning` — the security practice of scanning Docker artifacts for vulnerabilities before deployment

**Alternatives / Comparisons:**
- `Docker Image` — the dominant form of deployment artifact for containerised applications
- `SBOM (Software Bill of Materials)` — the manifest of all components inside an artifact, enabling vulnerability analysis

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Immutable, versioned build output:        │
│              │ JAR, Docker image, or binary              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Non-reproducible source-based deploys     │
│ SOLVES       │ with environmental variation              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Build once, deploy everywhere — staging   │
│              │ and prod must run the same binary         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — any CD pipeline must produce     │
│              │ and promote versioned artifacts           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — even serverless functions use       │
│              │ deployment packages (ZIP artifacts)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reproducibility + rollback vs storage     │
│              │ cost and registry management overhead     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The frozen meal: cook once, serve many   │
│              │  times — never cook at the table"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Artifact Registry → Container Scanning    │
│              │ → SBOM → Dependency Scanning              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team builds a Java microservice and packages it as a Docker image. The base image is `eclipse-temurin:21-jre-alpine`. Over 3 months, the base image has received 4 OS security patches. Your application image was last rebuilt 3 months ago. Describe the complete chain of ownership: who is responsible for detecting the vulnerability, what tool detects it specifically, what the fix process looks like, and how you'd prevent this from recurring without rebuilding every image daily.

**Q2.** A compliance auditor asks: "How can you prove that exactly the same software that passed your security tests is what's running in production?" Design the artifact traceability chain — from developer commit to running container — that would provide a satisfying and verifiable answer. What information must be stored at each step, and what commands would produce the evidence?

