---
layout: default
title: "Pipeline as Code"
parent: "CI/CD"
nav_order: 1005
permalink: /ci-cd/pipeline-as-code/
number: "1005"
category: CI/CD
difficulty: ★★☆
depends_on: Continuous Integration, Pipeline, Version Control
used_by: Jenkins, GitHub Actions, GitLab CI, Tekton
related: Infrastructure as Code, GitOps, CI/CD
tags:
  - cicd
  - devops
  - git
  - intermediate
  - bestpractice
---

# 1005 — Pipeline as Code

⚡ TL;DR — Pipeline as Code stores CI/CD pipeline definitions in version-controlled files alongside application source, making the delivery process auditable, reviewable, and reproducible just like the code it builds.

| #1005 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Continuous Integration, Pipeline, Version Control | |
| **Used by:** | Jenkins, GitHub Actions, GitLab CI, Tekton | |
| **Related:** | Infrastructure as Code, GitOps, CI/CD | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A CI pipeline is configured by clicking through a Jenkins GUI: "Build step 1: run maven. Build step 2: deploy." The configuration lives in Jenkins' internal database. When a developer accidentally changes the build configuration, there's no diff, no PR, no review — just a changed state that nobody approved. When a security engineer wants to ensure all builds include a SAST scan, they must click through every job in the Jenkins UI manually. When the Jenkins server is lost, all pipeline configuration is gone.

**THE BREAKING POINT:**
UI-configured pipelines are invisible to code review, unversioned, not reproducible after disaster, and impossible to audit. They violate every principle applied to application code — but for the CI/CD process itself.

**THE INVENTION MOMENT:**
This is exactly why Pipeline as Code was created: treat the pipeline definition with the same discipline as the code it builds — version-controlled, peer-reviewed, testable, and recoverable.

---

### 📘 Textbook Definition

**Pipeline as Code** is the practice of defining CI/CD pipelines in machine-readable text files (typically YAML or a DSL like Groovy) that are stored in version control alongside the application source code. These files are the authoritative definition of the build, test, and deployment process. Changes to pipelines go through the same pull-request review process as code changes. The pipeline definition is automatically discovered and used by the CI/CD tool (e.g., `Jenkinsfile` for Jenkins, `.github/workflows/` for GitHub Actions, `.gitlab-ci.yml` for GitLab CI).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store your build instructions in a file in your repo — not in a CI tool's UI.

**One analogy:**
> Pipeline as Code is like writing a cooking recipe in a cookbook instead of keeping it in your head. With the recipe written down, any cook can follow it exactly. Anyone can improve the recipe by proposing changes. If the original cook leaves, the recipe still exists. Without it, every cook improvises — and the dish comes out different every time.

**One insight:**
The most important consequence of Pipeline as Code is not convenience — it's **accountability**. When a pipeline change removes the security scan, that removal is a commit, visible in git log, approved in a PR, attributed to an author. The same change via a GUI is invisible. Pipeline as Code makes the delivery process auditable as a first-class concern.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The pipeline definition must be stored in the same version control system as the code.
2. Pipeline changes go through the same review process as code changes.
3. The pipeline definition is the single source of truth — no manual config in CI tools UI.

**DERIVED DESIGN:**
Storing pipelines in version control enables: (a) branching — each feature branch can have its own pipeline variant, (b) history — `git log Jenkinsfile` shows every pipeline change, (c) revert — `git revert` restores a previous known-good pipeline, (d) discovery — CI tools read the pipeline from the repo commit being built, ensuring tests run on the same commit that defined them.

The separation between pipeline definition (in your repo) and pipeline execution (in the CI tool) is clean. The CI tool is a generic executor; your repo contains the specific instructions.

**THE TRADE-OFFS:**
**Gain:** Auditability, reviewability, reproducibility, disaster recovery, branch-specific pipelines.
**Cost:** Pipeline files can become large and complex. Requires developers to understand CI YAML/DSL in addition to their application code. Secrets cannot be stored in the file (they go in CI tool's secret management).

---

### 🧪 Thought Experiment

**SETUP:**
A security policy requires all builds to run OWASP dependency checks. The CI pipelines are configured via UI.

**WHAT HAPPENS WITHOUT PIPELINE AS CODE:**
The security team must navigate to each of 30 Jenkins jobs and add the OWASP step manually. Two weeks later, a new developer creates a new job from scratch — no OWASP step, because the template wasn't updated. Six months later, a developer refactors a job and inadvertently removes the OWASP step — nobody notices because there's no diff.

**WHAT HAPPENS WITH PIPELINE AS CODE:**
The security team opens a PR to a shared pipeline template file. The PR adds the OWASP step. All 30 repos that `include:` this template automatically get the step after merge. New jobs created from the template include it by default. If a developer removes it from their `Jenkinsfile`, the PR shows the removal explicitly — the security team can block the merge.

**THE INSIGHT:**
Pipeline as Code transforms security and compliance from a manual, invisible process into a visible, reviewable, enforceable one. The pipeline config file is as important to audit as the application code.

---

### 🧠 Mental Model / Analogy

> Pipeline as Code is to CI/CD what `Dockerfile` is to container builds. Before Dockerfile, building a Docker image meant a manual sequence of `docker run`, `apt-get`, `docker commit`. The Dockerfile made the process explicit, portable, and reproducible. Pipeline as Code does the same for the entire delivery process.

- "Dockerfile FROM" → pipeline executor definition (image to run in)
- "Dockerfile RUN" → pipeline step commands
- "docker build" → CI tool executing the pipeline
- "Dockerfile in repo" → pipeline YAML/Jenkinsfile in repo
- "Build the image anywhere" → run the pipeline on any compatible CI runner

Where this analogy breaks down: a Dockerfile defines immutable layers; a pipeline is mutable (runs on new commits), passes state between steps, and interacts with external services (registries, clusters) — far more dynamic than a container build.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of clicking buttons in a CI tool's website to configure what the computer should do when you push code, you write those instructions in a text file stored in your code repository. Anyone can read it, change it with a review, and the CI tool follows it automatically.

**Level 2 — How to use it (junior developer):**
Create the pipeline file in the correct location for your CI tool: `.github/workflows/ci.yml` for GitHub Actions, `Jenkinsfile` at the repo root for Jenkins, `.gitlab-ci.yml` for GitLab CI. Commit it to version control. The CI tool discovers and uses it automatically. Changes to the pipeline file go through PR review like any other code change. Use the CI tool's secret management (GitHub Secrets, Jenkins Credentials) for credentials — never put secrets in the file.

**Level 3 — How it works (mid-level engineer):**
CI tools discover pipeline files by convention (filename/path) or by explicit configuration (Jenkins "Multibranch Pipeline" scans the repo for Jenkinsfiles). The pipeline file is read at the commit SHA being built — so the pipeline that runs on commit `abc123` is the one defined in the Jenkinsfile at commit `abc123`. This means a PR that changes both application code and the pipeline to test it atomically carries both changes together — the new test infrastructure is tested in the same PR that requires it.

**Level 4 — Why it was designed this way (senior/staff):**
Jenkins pioneered Pipeline as Code with `Jenkinsfile` in 2014 (building on a previous "Job DSL" plugin). The key innovation was "the Jenkinsfile at the commit is what runs" — not a separately-configured job in Jenkins UI. This addressed the disconnect between what the code expects and what the CI job provides. GitHub Actions (2018) took this further: the trigger definition, secret references, and workflow steps are all in the YAML file. GitLab CI made it the default from the start. The maturation of this practice is codified in the "Config as Code" movement — treating all operational configuration (pipelines, infrastructure, policies) with software engineering discipline.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│     PIPELINE AS CODE — DISCOVERY MODEL      │
├─────────────────────────────────────────────┤
│  REPOSITORY AT COMMIT abc123:               │
│  ├─ src/main/java/...                       │
│  ├─ src/test/java/...                       │
│  ├─ pom.xml                                 │
│  └─ Jenkinsfile (pipeline definition)       │
│                                             │
│  CI TOOL (Jenkins / GitHub Actions):        │
│  1. Webhook received: commit abc123 pushed  │
│  2. Checkout repo at commit abc123          │
│  3. Read Jenkinsfile at abc123              │
│     (NOT from a separate config database)   │
│  4. Execute pipeline defined in that file   │
│                                             │
│  KEY: pipeline and code are atomic          │
│  A PR that adds a new test class AND adds   │
│  the CI step to run it carries BOTH changes │
│  together — testable in the same PR         │
└─────────────────────────────────────────────┘
```

**Shared pipeline templates** (DRY principle):
```yaml
# GitHub Actions: reusable workflow
# .github/workflows/shared-java-ci.yml
on:
  workflow_call:
    inputs:
      java-version: { type: string, default: '21' }
    secrets:
      registry-token: { required: true }

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: ${{ inputs.java-version }} }
      - run: mvn verify
```

```yaml
# In each service repo: call the shared pipeline
name: CI
on: [ push, pull_request ]
jobs:
  ci:
    uses: myorg/.github/.github/workflows/shared-java-ci.yml@main
    with:
      java-version: '21'
    secrets:
      registry-token: ${{ secrets.REGISTRY_TOKEN }}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer opens PR:
  - Modifies application code
  - Modifies .github/workflows/ci.yml +adds new test stage
  → PR shows diff of BOTH code and pipeline changes
  → Code reviewer sees new test stage added — approves
  → Merge → CI runs new pipeline from merged commit
  → New test stage runs successfully [← YOU ARE HERE]
  → Next commits also run the new stage automatically
```

**FAILURE PATH:**
```
Developer modifies pipeline to skip security scan:
  - Removes security stage from ci.yml
  → PR shows: security stage removed
  → Security team's CODEOWNER rule: requires approval
  → Security engineer rejects PR: "SAST removal requires justification"
  → Pipeline change blocked by process — same as code change
```

**WHAT CHANGES AT SCALE:**
At 100+ repositories, maintaining 100 separate pipeline files diverges over time. Teams use shared pipeline templates (reusable workflows in GitHub Actions, `.gitlab-ci.yml` `include:` templates in GitLab, Jenkins Shared Libraries). Teams define "golden path" pipeline templates that encapsulate standards. Individual repos customise; the platform team owns the shared template. This creates a natural governance mechanism — standards are enforced via the template, not per-repo enforcement.

---

### 💻 Code Example

**Example 1 — Jenkinsfile with compliance enforcement:**
```groovy
// Jenkinsfile
@Library('company-shared-lib@v2.1') _

// All pipelines must call the company standard wrapper
compliancePipeline {
    // Service-specific overrides
    buildTool = 'maven'
    deployEnvironments = ['staging', 'production']
    notifyChannel = '#payments-team'

    // Extension point for service-specific steps
    additionalTestStages {
        stage('Performance Test') {
            sh './run-perf-tests.sh'
        }
    }
}

// compliancePipeline enforces:
// - SAST scan (mandatory, cannot be overridden)
// - Dependency check (mandatory)
// - Docker image build + push (mandatory)
// Service can add steps but not remove mandatory ones
```

**Example 2 — Pipeline file as infrastructure-as-code with CODEOWNERS:**
```bash
# .github/CODEOWNERS
# Security team must approve any pipeline changes
.github/workflows/      @myorg/security-team

# Platform team must approve shared templates
.github/workflows/reusable-*.yml @myorg/platform-team

# Application teams own their own pipelines
# (but CODEOWNERS for workflows/ means security always reviews)
```

---

### ⚖️ Comparison Table

| Pipeline Definition | Auditable | Branch-Specific | Disaster Recovery | Review Process | Best For |
|---|---|---|---|---|---|
| **Pipeline as Code (YAML/DSL)** | Yes (git history) | Yes (per-branch file) | Yes (in repo) | Yes (PR review) | All modern teams |
| UI-configured (Jenkins GUI) | No | Manual copy | No (CI-server-only) | No | Legacy systems only |
| Script-based (Makefile/scripts) | Partial | Manual variant | Yes (in repo) | Yes (PR review) | Local dev, simple builds |
| Shared Library (Jenkins) | Yes | N/A (reusable) | Yes | Yes | Enterprise multi-repo |

How to choose: Always use Pipeline as Code for new projects. If running Jenkins, migrate from UI-configured jobs to Declarative Pipeline + Jenkinsfile. Only use UI configuration when the CI tool doesn't support any form of file-based configuration.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Pipeline as Code means fully specifying everything in YAML | Large pipelines can `include:` or `uses:` shared templates. The principle is version control, not verbosity. Reusing common components is encouraged |
| Secrets can be stored in the pipeline file | Secrets must NEVER be in pipeline files (committed to Git). Use the CI tool's secrets management. The pipeline file references secret names; values stay in secure storage |
| Pipeline as Code only applies to YAML | Jenkinsfile (Groovy DSL), Bazel BUILD files, Gradle scripts — any file-based, version-controlled pipeline definition counts as Pipeline as Code |
| One pipeline file per repo is always sufficient | Large monorepos or complex products may have multiple pipeline files (different workflows for different triggers). The principle is version control, not one-file-per-repo |

---

### 🚨 Failure Modes & Diagnosis

**1. Pipeline File Diverges Across Repos**

**Symptom:** 30 repos each have a slightly different `ci.yml`. Service A runs tests differently from Service B. Compliance scan is enabled in 18 repos and disabled in 12.

**Root Cause:** No shared template. Each repo copied-then-modified the pipeline file independently. No enforcement mechanism.

**Diagnostic:**
```bash
# Compare pipeline files across repos
# (requires local clones of all repos)
for repo in repos/*/; do
  echo "=== $repo ==="
  grep -c "security-scan" "$repo/.github/workflows/ci.yml" \
    && echo "HAS security scan" \
    || echo "MISSING security scan"
done
```

**Fix:** Create a shared pipeline template. Migrate all repos to reference it. Use CODEOWNERS to enforce changes go through platform team.

**Prevention:** Provide a golden-path template at project creation time. Make using the template the path of least resistance.

---

**2. Pipeline Change Enables Accidental Bypass of Security Gate**

**Symptom:** A developer removes `security-scan` from the pipeline to "speed up" tests for a Friday deadline. The change is merged without security team review.

**Root Cause:** No CODEOWNERS rule requiring security team approval for pipeline file changes. Or CODEOWNERS rules exist but weren't enforced (branch protection not configured).

**Diagnostic:**
```bash
# Check branch protection rules
gh api repos/myorg/myapp/branches/main/protection \
  | jq '.required_pull_request_reviews'
# Check CODEOWNERS
cat .github/CODEOWNERS | grep workflows
```

**Fix:** Set CODEOWNERS for `.github/workflows/`. Enable "Require review from code owners" in branch protection settings.

**Prevention:** Include pipeline file ownership rules in the standard repo setup template. Audit monthly.

---

**3. PR Changes Break Other Branches' Pipelines**

**Symptom:** A developer merges a change to a shared `include:` template. All 50 repos that reference it via `@main` immediately pick up the broken change.

**Root Cause:** Shared templates referenced by mutable branch tag (`@main`) instead of versioned tag.

**Diagnostic:**
```bash
# Find all repos referencing main branch of shared template
grep -r "uses: myorg/.github/.github/workflows/.*@main" \
  repos/*/
# These are all at risk of broken includes
```

**Fix:** Version shared templates with semantic tags:
```yaml
# BAD: mutable — any change to main breaks all consumers immediately
uses: myorg/.github/.github/workflows/java-ci.yml@main

# GOOD: pinned version — consumers upgrade deliberately
uses: myorg/.github/.github/workflows/java-ci.yml@v2.1.0
```

**Prevention:** Publish shared pipeline templates using semantic versioning. Require teams to upgrade versions explicitly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — Pipeline as Code is the mechanism for defining CI processes; CI is the practice context
- `Pipeline` — the concept of ordered stages being automated; Pipeline as Code is how that definition is stored
- `Version Control` — Pipeline as Code stores definitions in version control; understanding Git is required

**Builds On This (learn these next):**
- `GitHub Actions` — uses Pipeline as Code via `.github/workflows/*.yml` YAML files
- `Jenkins` — pioneered Pipeline as Code with Jenkinsfile; applies the practice with Groovy DSL
- `Infrastructure as Code` — the same principle applied to infrastructure; Pipeline as Code is its CI/CD equivalent

**Alternatives / Comparisons:**
- `Infrastructure as Code` — applies the same version-control-everything principle to server and cloud infrastructure
- `GitOps` — extends Pipeline as Code to deployment — the cluster's desired state is also in Git

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ CI/CD pipelines defined in version-       │
│              │ controlled files alongside app source     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ UI-configured pipelines are invisible,    │
│ SOLVES       │ unversioned, unreviewed, unrecoverable    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The pipeline definition is as important   │
│              │ to audit as the code it delivers          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — any CI/CD setup benefits from    │
│              │ Pipeline as Code over UI configuration    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — there is no valid reason to prefer  │
│              │ UI-only pipeline configuration            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Auditability + reproducibility vs         │
│              │ developers learning pipeline YAML/DSL     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A recipe in the cookbook, not only in    │
│              │  the chef's head"                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GitHub Actions → GitLab CI → GitOps       │
│              │ → Infrastructure as Code                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A platform engineer proposes making all 50 microservice repos use the same shared GitHub Actions workflow via `uses: myorg/.github/.github/workflows/java-ci.yml@v2`. One team argues: "Our service is special — we need a custom pipeline." List three valid reasons for pipeline variation that would justify a custom pipeline, and three that would NOT justify it (and should instead be addressed via template parameters or extension points). How would you structure the template to accommodate legitimate customisation without breaking the shared standard?

**Q2.** A developer on your team says: "Pipeline as Code is just security theatre — if a malicious developer wants to bypass the SAST scan, they can just remove it from the Jenkinsfile in their branch, merge quickly without review, and the insecure code ships." Construct the complete defence: CODEOWNERS rules, branch protection settings, code owner review requirements, and escalation process that would prevent this — and explain which specific GitHub/GitLab setting is the critical one that makes the others effective.

