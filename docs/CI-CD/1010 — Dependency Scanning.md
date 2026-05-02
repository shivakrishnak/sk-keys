---
layout: default
title: "Dependency Scanning"
parent: "CI/CD"
nav_order: 1010
permalink: /ci-cd/dependency-scanning/
number: "1010"
category: CI/CD
difficulty: ★★☆
depends_on: SCA, Pipeline, Artifact Registry
used_by: Container Scanning, SBOM, Secret Scanning
related: SCA, Container Scanning, SBOM
tags:
  - cicd
  - security
  - devops
  - intermediate
  - dependencies
---

# 1010 — Dependency Scanning

⚡ TL;DR — Dependency scanning automatically checks every declared library in your project's manifest files against CVE databases, alerting and blocking builds when known vulnerabilities are found in your direct or transitive dependencies.

| #1010 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SCA, Pipeline, Artifact Registry | |
| **Used by:** | Container Scanning, SBOM, Secret Scanning | |
| **Related:** | SCA, Container Scanning, SBOM | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team's `package.json` lists `lodash: "^4.17.11"`. Lodash 4.17.11 has a known prototype pollution vulnerability (CVE-2019-10744, CVSS 9.8). The team uses lodash daily and never questions it — it was added two years ago and just works. Without automated scanning, the team could run this vulnerability for years, unaware that any application using `lodash.set()` with user-controlled paths is exploitable.

**THE BREAKING POINT:**
Development teams add dependencies quickly and rarely audit them systematically. Vulnerability databases publish new CVEs for popular libraries constantly. Manual auditing of 150+ transitive dependencies every sprint is not feasible — it simply doesn't happen. Known vulnerabilities sit in production for months or years.

**THE INVENTION MOMENT:**
This is exactly why dependency scanning exists: automate the tedious, error-prone process of cross-referencing every package version against CVE databases — making it a standard, non-negotiable CI pipeline step that requires zero manual effort.

---

### 📘 Textbook Definition

**Dependency scanning** is a CI/CD security practice that parses application manifest files (pom.xml, package.json, requirements.txt, Gemfile.lock) and resolves the complete dependency tree, then cross-references each package version against known vulnerability databases (NVD, OSV, GitHub Advisory Database). It is the practical implementation of Software Composition Analysis (SCA) focused specifically on the `dependencies` section of build manifests. Dependency scanning tools generate reports with CVE IDs, CVSS scores, affected versions, and remediation advice (upgrade to version X.Y.Z). It runs as a fast CI pipeline gate and as continuous monitoring for post-deployment alerts.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Automatically check every library in your `pom.xml` or `package.json` against the known security vulnerability list.

**One analogy:**
> Dependency scanning is like a customs officer checking every item in your shipment against a list of prohibited materials. You packed the box — but some items inside may be on a restricted list you didn't know about. The customs check catches them without requiring you to memorise the entire prohibited items catalogue.

**One insight:**
The relationship between dependency scanning and SCA is: SCA is the practice and strategy; dependency scanning is the specific technical operation of scanning manifest files for CVEs. In daily developer vocabulary, the terms are often used interchangeably.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Manifest files declare intent (what the developer wants); the lock file records reality (exact installed versions).
2. CVEs are discovered continuously — a dependency clean today may be vulnerable tomorrow.
3. Transitive dependencies carry equal vulnerability risk as direct dependencies.

**DERIVED DESIGN:**
Dependency scanning must use lock files (not just manifests) for accuracy. `pom.xml` might declare `spring-boot-starter-web: 3.0.0`, but the actual resolved version of every transitive dependency is captured in the resolved dependency tree. Scanning `package.json` misses the actual installed versions; scanning `package-lock.json` is exact. The Maven Dependency Plugin's `dependency:tree` output reveals the complete resolved tree.

Continuous monitoring extends beyond CI: the dependency graph doesn't change unless you redeploy, but the CVE database does. Snyk and GitHub Advanced Security watch the CVE databases and alert when a new CVE affects an already-deployed application — without requiring a new commit.

**THE TRADE-OFFS:**
**Gain:** Automated systematic coverage, fast feedback (typically 1–3 minutes), continuous monitoring catches new CVEs in deployed apps.
**Cost:** Can generate many findings, requiring triage and prioritisation. Version upgrades may introduce breaking changes. Over-aggressive blocking (fail on any CVE regardless of severity) can be counterproductive.

---

### 🧪 Thought Experiment

**SETUP:**
A Node.js app has 200 dependencies (direct + transitive). A security advisory is published for `minimist` (used for CLI argument parsing, a transitive dep 4 levels deep).

**WHAT HAPPENS WITHOUT DEPENDENCY SCANNING:**
The `minimist` CVE is published. No one at the company knows minimist is in the application. Six months later, a security researcher finds the app is vulnerable. The company must now urgently trace the dependency chain, understand the impact, and patch under pressure.

**WHAT HAPPENS WITH DEPENDENCY SCANNING (Dependabot):**
CVE published for `minimist`. GitHub Dependabot detects it matches the version in `package-lock.json`. Within 24 hours: automated PR created — "Bump minimist from 1.2.5 to 1.2.6 to fix CVE-2021-44906." Developer reviews, merges in 10 minutes. Patched.

**THE INSIGHT:**
The same CVE — hours of proactive patching vs weeks of reactive fire-fighting. The only difference is automation. Dependency scanning makes the routine work of security patching trivially low-effort.

---

### 🧠 Mental Model / Analogy

> Dependency scanning is like subscribing to product safety recall notifications. When a product you own is recalled, you get an email immediately. Without the subscription, you'd only learn about the recall if you happened to read the news or if something went wrong. Dependency scanning is that subscription — for every library your application uses.

- "Product recall notification" → CVE alert for a library version
- "Subscribing" → enabling Dependabot / Snyk on your repo
- "Products you own" → packages in your dependency tree
- "Recall email" → automated PR or alert with fix version
- "Returning the defective product" → upgrading to patched version

Where this analogy breaks down: product recalls don't create substitute products — upgrades do. An upgrade might change API behaviour (breaking change), requiring testing. The subscription (dependency scanning) finds the problem; fixing it (upgrading and testing) still requires engineering effort.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every library your app uses can potentially have security issues discovered later. Dependency scanning checks all your libraries automatically against a list of known security problems, and tells you which ones to update.

**Level 2 — How to use it (junior developer):**
Enable GitHub Dependabot via `.github/dependabot.yml`. Dependabot creates automated PRs for security updates — merge them promptly. Or run `npm audit` / `mvn dependency-check:check` locally and in CI. Review findings by severity: address Critical and High immediately; schedule Medium and Low as part of routine maintenance. Never use `npm audit --fix` blindly — review what it changes.

**Level 3 — How it works (mid-level engineer):**
The scanner parses the lock file to extract all exact versions. It queries the package vulnerability database (npm Advisory Database for Node, Maven OSS Index for Java, PyPI Safety DB for Python). Matching uses version ranges: CVE-2021-44906 affects minimist `>= 1.0.0 < 1.2.6` — if installed version falls in that range, finding reported. In CI integration (Snyk CLI, OWASP Dependency Check), a CVSS threshold determines whether the check is a warning or a build failure. GitHub's Dependabot integrates version constraint resolution — it knows which versions are compatible with your existing constraints and creates a PR for the specific fix version.

**Level 4 — Why it was designed this way (senior/staff):**
Dependency scanning tooling evolved in response to the explosion of open-source consumption driven by package managers (npm 2010, Maven Central). The "supply chain attack" threat emerged with incidents like the left-pad removal (2016 — availability, not security), event-stream compromise (2018 — malicious code injection), and the SolarWinds attack (2020 — build system compromise). These shifted the threat model from "scan library CVEs" to "verify library provenance and integrity." The SBOM mandate from the US Executive Order (2021) and the SLSA (Supply Levels for Software Artifacts) framework represent the current frontier — requiring not just "is this version vulnerable?" but "can we verify this library actually came from the published source and wasn't tampered with in transit?"

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│     DEPENDENCY SCANNING EXECUTION           │
├─────────────────────────────────────────────┤
│  Input: package-lock.json / pom.xml          │
│                                             │
│  STEP 1: Parse manifest / lock file          │
│  [lodash@4.17.11, express@4.18.1, ...]      │
│                                             │
│  STEP 2: Resolve full dependency tree        │
│  Direct + transitive:                       │
│  express@4.18.1                             │
│  ├─ body-parser@1.20.1                      │
│  │   └─ qs@6.11.0 (no CVE)                  │
│  └─ accepts@1.3.8                           │
│  lodash@4.17.11 ← CVE-2019-10744            │
│  minimist@1.2.5 ← CVE-2021-44906            │
│                                             │
│  STEP 3: Query vulnerability DB              │
│  lodash 4.17.11 → CVE-2019-10744 CVSS 9.8  │
│  minimist 1.2.5 → CVE-2021-44906 CVSS 9.8  │
│                                             │
│  STEP 4: Policy evaluation                  │
│  CVSS >= 9.0 → CRITICAL → FAIL BUILD        │
│                                             │
│  STEP 5: Report + Remediation               │
│  lodash: upgrade to 4.17.21                 │
│  minimist: upgrade to 1.2.6                 │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer adds new dependency: `axios@0.21.0`
  → PR opened → CI triggered
  → Dependency scan: scan package-lock.json [← YOU ARE HERE]
  → axios@0.21.0 → CVE-2021-3749 (SSRF) / CVSS 7.5 / High
  → Policy: High → block PR
  → GitHub PR: ✗ "Dependency scan: High CVE in axios@0.21.0"
  → Dependabot creates suggestion: upgrade to 0.21.4
  → Developer updates package.json → axios@0.21.4
  → Re-scan: 0.21.4 no CVE → PASS
  → PR: ✓ → merge allowed
```

**CONTINUOUS MONITORING:**
```
(Day 0): Application deployed with axios@0.21.4 — clean
  → (Day 90): CVE-2023-XXXX published for axios@0.21.4
  → Snyk/Dependabot detects match in repository
  → Automated PR: "Security update: axios 0.21.4 → 1.6.0"
  → Slack alert: "axios CVE in payment-service"
  → NO new commit needed to trigger detection
```

**WHAT CHANGES AT SCALE:**
At 100+ repos, 50+ Dependabot PRs open simultaneously. Teams implement auto-merge policies: patch-level security updates auto-merge if CI passes; minor/major require manual review. The "dependency update PR queue" itself must be managed — stale PRs accumulate technical debt. A centralised security dashboard aggregates CVE SLA compliance across all repos.

---

### 💻 Code Example

**Example 1 — Dependabot with auto-merge for security patches:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"  # check daily for security updates
    # Group non-security updates to reduce PR noise
    groups:
      non-security:
        applies-to: version-updates  # not security updates
        update-types:
          - "minor"
          - "patch"
    open-pull-requests-limit: 5
```

```yaml
# .github/workflows/dependabot-auto-merge.yml
name: Dependabot Auto-Merge
on: pull_request

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - uses: actions/checkout@v4
      - name: Dependabot metadata
        id: meta
        uses: dependabot/fetch-metadata@v2
      - name: Auto-merge security patches
        if: |
          steps.meta.outputs.update-type == 'version-update:semver-patch' &&
          steps.meta.outputs.dependency-type == 'direct:production'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Example 2 — OWASP Dependency Check suppression:**
```xml
<!-- owasp-suppressions.xml -->
<suppressions>
  <!--
    CVE-2022-XXXX: Affects test-scope dependency only.
    Not present in production artifact.
    Verified by: security@example.com on 2025-01-15.
    Review date: 2025-07-15.
  -->
  <suppress>
    <cve>CVE-2022-XXXX</cve>
    <gav
      regex="true">com\.example:test-helper:.*</gav>
  </suppress>
</suppressions>
```

**Example 3 — npm audit in CI:**
```yaml
- name: Audit dependencies
  run: |
    # --audit-level=high: fail only on High or Critical
    npm audit --audit-level=high --omit=dev
    # --omit=dev: skip devDependencies (not in production)
    # For detailed output:
    npm audit --json > audit-report.json
    echo "Findings:"
    cat audit-report.json | \
      jq '.vulnerabilities | to_entries[] |
        select(.value.severity == "high" or
               .value.severity == "critical") |
        {name: .key, severity: .value.severity,
         fix: .value.fixAvailable}'
```

---

### ⚖️ Comparison Table

| Tool | Ecosystems | Speed | Free | Auto-PRs | Best For |
|---|---|---|---|---|---|
| **Dependabot** | npm, Maven, pip, Go, Docker | Fast | Yes (GitHub) | Yes | GitHub repos, automated PRs |
| Snyk | 10+ ecosystems | Fast | Limited | Yes | Developer experience, accuracy |
| OWASP Dep Check | Java, .NET, Python, Ruby | Medium | Yes | No | On-premise, compliance |
| npm audit | npm only | Very fast | Yes | No | JavaScript quick check |
| Trivy | Multi + OS packages | Fast | Yes | No | Docker + manifest combined |

How to choose: Enable Dependabot on all GitHub repositories as the free baseline. Add Snyk in CI for more accurate triage and developer-friendly UX. Use OWASP Dependency Check in air-gapped environments where external SaaS isn't permitted.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `npm audit fix` always makes the application safer | `npm audit fix --force` can apply semver-incompatible upgrades that break the application. Always review what `--force` changes; test before deploying |
| Test dependencies don't need scanning | Test dependencies can be exploited via CI/CD pipeline attacks (supply chain). They also sometimes leak into production builds. Scan all dependencies; just deprioritise test-only CVEs |
| Dependency scanning covers Docker base image vulnerabilities | Manifest-based dependency scanning only scans language packages (npm, Maven). Docker image OS package vulnerabilities (apt, rpm) require container scanning (Trivy, Grype) |
| One CVE per library means one fix | A library may have multiple CVEs requiring multiple upgrades. Always scan after upgrading to confirm the new version resolves all findings |

---

### 🚨 Failure Modes & Diagnosis

**1. Dependency Scanning Blocks Build With No Available Fix**

**Symptom:** Every build fails: OWASP Dependency Check finds CVE in `legacy-lib 1.0.0`. No newer version exists. Project abandoned.

**Root Cause:** Threshold set to fail on any CVE. No exception process.

**Diagnostic:**
```bash
# Check if fix version exists
snyk test --json | jq '.vulnerabilities[] |
  select(.identifiers.CVE[] | contains("CVE-20XX-YYYY")) |
  {fixedIn}'
# If null → no published fix
```

**Fix:** Add a documented suppression with risk acceptance:
```xml
<suppress>
  <cve>CVE-20XX-YYYY</cve>
  <notes>
    No fix available for legacy-lib 1.0.0.
    Mitigated by: network isolation (not internet-facing).
    Risk accepted. Review: 2025-07-01.
  </notes>
</suppress>
```

**Prevention:** Define a vulnerability exception workflow before implementing the tool. Blocking without a fix path breaks developer workflow.

---

**2. Lock File Not Committed — Scanning Finds Wrong Versions**

**Symptom:** Dependency scan reports no findings. But `npm install` pulled a newer version with a CVE that the scan missed because it queried the version range in `package.json` rather than the resolved version in `package-lock.json`.

**Root Cause:** `package-lock.json` is `.gitignore`-d (a common mistake). Scanner reads `package.json` version ranges instead of exact resolved versions — "^4.17.11" matches any 4.x.x, but scanner tested the minimum 4.17.11.

**Diagnostic:**
```bash
# Verify lock file is committed
git ls-files | grep package-lock.json
# If nothing returned → lock file is gitignored
cat .gitignore | grep lock
```

**Fix:** Remove lock files from `.gitignore`. Commit `package-lock.json`, `yarn.lock`, `Pipfile.lock`. Configure scanner to use lock files.

**Prevention:** All lock files must be committed to version control. This is also a reproducibility requirement (same versions on every `npm ci`).

---

**3. Scan Result Inconsistency — Different CVEs Found Locally vs CI**

**Symptom:** `npm audit` locally shows 0 findings. CI shows 3 High CVEs. Or vice versa.

**Root Cause:** Local and CI use different Node versions, different npm registries, or local has stale advisory database cached.

**Diagnostic:**
```bash
# Compare Node and npm versions
node --version && npm --version
# Check advisory database staleness
npm audit --json | jq '.auditReportVersion'
# Force refresh
npm audit --force
```

**Fix:** Use `npm ci` (not `npm install`) in CI — it uses exact lock file versions. Pin Node version in CI to match local development.

**Prevention:** `npm ci` instead of `npm install` in all CI pipelines. Pin Node version in `.nvmrc` and CI environment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SCA (Software Composition Analysis)` — dependency scanning is the core operation of SCA; understanding SCA provides the full context
- `Pipeline` — dependency scanning runs as a CI pipeline stage; understanding pipeline structure is required
- `Artifact Registry` — artifacts contain the dependencies that are scanned; registries can also integrate scanning

**Builds On This (learn these next):**
- `Container Scanning` — extends dependency scanning to Docker OS packages in addition to language packages
- `SBOM (Software Bill of Materials)` — the formal output of dependency scanning: a machine-readable inventory of all components
- `Secret Scanning` — the parallel practice of scanning for committed credentials alongside scanning for vulnerable dependencies

**Alternatives / Comparisons:**
- `SCA` — the broader practice of which dependency scanning is the primary implementation
- `Container Scanning` — adds OS-level package scanning to the dependency scanning scope
- `SAST` — scans first-party code for vulnerabilities; dependency scanning scans third-party code

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Auto-check all package manifests (pom.xml,│
│              │ package.json) against CVE databases       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Known vulnerabilities in imported         │
│ SOLVES       │ libraries sitting undetected in production │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Scan lock files (exact versions), not just │
│              │ manifests (version ranges) for accuracy   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — enable Dependabot as baseline    │
│              │ for all projects with external deps       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — but tune severity thresholds:│
│              │ don't fail builds on Medium/Low CVEs      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Automated CVE detection vs upgrade churn  │
│              │ and potential breaking changes in fixes   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Product recall notifications for your    │
│              │  imported libraries — automatic, instant" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Container Scanning → SBOM                 │
│              │ → Secret Scanning → Supply Chain          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team's CI pipeline runs dependency scanning (Snyk) on every PR. Average findings per PR: 4 (2 Critical, 2 High). The team merges 30 PRs per week. At this rate, the team must address 60 CVE findings per week on top of feature development. Half of the Critical findings are in test-only dependencies. Design a complete triage and prioritisation strategy that reduces the active security work to a sustainable level while maintaining a genuine security posture — not just suppressing everything.

**Q2.** The `colors` npm package (very popular, 150M weekly downloads) was deliberately sabotaged by its maintainer in January 2022 — new code was published that prints garbage to the terminal for any application using it. This was not a CVE vulnerability — the code worked as published, just maliciously. How would standard dependency scanning have detected or NOT detected this attack? What complementary security controls would need to be in place to catch intentional malicious code injection in widely-used open-source packages?

