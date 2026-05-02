---
layout: default
title: "Jenkins"
parent: "CI/CD"
nav_order: 999
permalink: /ci-cd/jenkins/
number: "0999"
category: CI/CD
difficulty: ★★☆
depends_on: Continuous Integration, Pipeline, Pipeline as Code
used_by: Build Stage, Test Stage, Deployment Pipeline
related: GitHub Actions, GitLab CI, Tekton
tags:
  - cicd
  - devops
  - build
  - intermediate
---

# 0999 — Jenkins

⚡ TL;DR — Jenkins is an open-source automation server that runs CI/CD pipelines defined as code (Jenkinsfile), offering unmatched plugin flexibility at the cost of operational complexity.

| #0999 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Continuous Integration, Pipeline, Pipeline as Code | |
| **Used by:** | Build Stage, Test Stage, Deployment Pipeline | |
| **Related:** | GitHub Actions, GitLab CI, Tekton | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
It's 2011. A team wants automated builds triggered by Git commits. Options: cron jobs running `make`, custom shell scripts on shared servers, or paying for one of a handful of expensive proprietary build systems. Every team writes their own automation from scratch. No shared plugins, no build history UI, no integration with version control systems, no artifact archiving. Automation exists but is artisanal and non-transferable.

**THE BREAKING POINT:**
Custom automation doesn't scale. The 3rd build script is fine; the 30th is a maintenance nightmare. No visualisation of what's running, no notification system, no plugin ecosystem, no standard way to define "a build."

**THE INVENTION MOMENT:**
This is exactly why Jenkins was created: an open-source, extensible automation server that standardised how builds are triggered, executed, monitored, and shared — with a plugin ecosystem that made it adaptable to any technology stack.

---

### 📘 Textbook Definition

**Jenkins** is an open-source Java-based automation server used for building, testing, and deploying software. It was forked from Hudson in 2011 and has since become one of the most widely deployed CI/CD tools. Jenkins executes pipelines defined either through its web UI (freestyle projects) or as code via `Jenkinsfile` (Declarative or Scripted Pipeline DSL based on Groovy). It distributes work across a controller-and-agent architecture, where the controller (master) orchestrates jobs and agents (nodes) execute build steps. Its plugin ecosystem (2000+ plugins) enables integration with virtually any tool in the software development ecosystem.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Jenkins is a build server that watches your code and runs your pipeline automatically — fully customisable with 2000+ plugins.

**One analogy:**
> Jenkins is like a master chef who coordinates a large restaurant kitchen. The head chef (Jenkins controller) receives orders (pipeline triggers), delegates cooking tasks (build steps) to line cooks (agents), tracks each task's progress, and serves the final dish (deployment). The head chef follows the recipe (Jenkinsfile) stored in the pantry (source repository).

**One insight:**
Jenkins' greatest strength — its plugin ecosystem and Groovy-based DSL — is also its greatest weakness. Every plugin version combination is a potential conflict. Every Groovy pipeline is a custom program. At scale, Jenkins becomes an operational burden that justified the newer generation of cloud-native CI tools.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Controllers orchestrate — they schedule jobs, store state, and host the UI.
2. Agents execute — they run actual build steps in isolated workspaces.
3. Pipelines are code — Jenkinsfile defines what to do, stored in the repo.

**DERIVED DESIGN:**
The controller-agent separation allows horizontal scaling of execution capacity: add more agents when build queues grow. Agents can be specialised — a Windows agent for .NET builds, a Linux agent for Java, a macOS agent for iOS. Dynamic agents (ephemeral Kubernetes pods spun up per build) solve the "idle agent" waste problem.

Declarative Pipeline enforces a structured, human-readable syntax that catches common mistakes. Scripted Pipeline allows arbitrary Groovy — powerful but dangerous, as it becomes a general-purpose program that can do anything (including causing security incidents).

**THE TRADE-OFFS:**
**Gain:** Maximum flexibility. Runs anywhere. 2000+ plugins. Self-hosted = no run-minute billing.
**Cost:** Controller is a stateful single point of failure. Maintaining Jenkins version + plugin compatibility is a significant ongoing operational cost. Security hardening is the team's responsibility. Groovy DSL complexity grows over time.

---

### 🧪 Thought Experiment

**SETUP:**
A team of 20 engineers considers Jenkins vs GitHub Actions for their CI/CD.

**WHAT HAPPENS WITH JENKINS:**
Month 1: Pipeline is working. Month 3: A plugin update breaks the build. Month 6: The Jenkins controller's disk is full — build history corrupted. Month 12: The team has 3 Jenkinsfile variants across 15 repos, each slightly different. A Jenkins admin role emerges as a full-time concern. New engineers spend 2 days onboarding to the Jenkins-specific Groovy syntax.

**WHAT HAPPENS WITH GITHUB ACTIONS:**
Month 1: Pipelines defined in YAML, no server to manage. Month 12: Team uses shared reusable workflows across 15 repos. No Jenkins admin role. New engineers use their existing YAML knowledge. Run-minute billing is $200/month vs $0 (but significant ops time) for Jenkins.

**THE INSIGHT:**
Jenkins is the right choice when control, customisation, or compliance requirements outweigh operational simplicity. The tradeoff is explicit: maximum control at maximum operational cost. Modern cloud-native CI tools trade flexibility for simplicity and zero operations.

---

### 🧠 Mental Model / Analogy

> Jenkins is like a highly customisable Swiss Army knife. It can do everything, and you can add new tools (plugins) at will. But the more tools you add, the heavier it gets, and the harder it is to find the right blade when you need it quickly. A specialist knife (GitHub Actions for GitHub repositories) may be less flexible but much easier to use for its specific purpose.

- "Swiss Army knife body" → Jenkins core
- "Blades and tools" → Jenkins plugins
- "Carrying the knife" → running and maintaining the Jenkins server
- "Finding the right blade" → configuring and composing plugins correctly
- "Specialist knife" → purpose-built CI tools (GitHub Actions, CircleCI)

Where this analogy breaks down: Jenkins plugins can conflict with each other in ways that Swiss Army knife tools cannot. Plugin compatibility matrix management is one of Jenkins' most painful operational aspects.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Jenkins is a computer program that automatically builds and tests your code every time you make a change. You tell it what to do by writing a script (Jenkinsfile), and it runs that script on its own computers whenever triggered.

**Level 2 — How to use it (junior developer):**
Create a `Jenkinsfile` in your repository root. Use Declarative Pipeline syntax. Define `stages` with `steps`. Jenkins polls your repo or receives a webhook. Agents are configured in Jenkins UI or as Kubernetes pod templates. Use `sh` steps to run shell commands. Use `post { always { junit ... } }` to archive test results. Blue Ocean plugin provides a visual pipeline editor.

**Level 3 — How it works (mid-level engineer):**
The Jenkins controller stores job configuration, build history, and pipeline state in `$JENKINS_HOME`. On trigger, the controller schedules the job to an available agent matching the `label` in the `agent` block. The agent receives the pipeline definition via the Remoting protocol (TCP/JNLP). Workspace is created on the agent's disk. Steps execute as OS processes. Results (logs, artifacts) are collected back to the controller. Shared Libraries (`@Library`) allow reusing pipeline code across repos.

**Level 4 — Why it was designed this way (senior/staff):**
Jenkins chose Groovy as the pipeline DSL because it runs on the JVM (Jenkins is Java) and allows arbitrary programming constructs. This made it powerful but introduced complexity. CloudBees (Jenkins' commercial sponsor) introduced Declarative Pipeline in 2017 to enforce a structured, limited DSL — reducing the "everybody writes their own magic Groovy" problem. The controller-agent model predates containers; migration to ephemeral Kubernetes agents was a retrofit using the `kubernetes` plugin. Jenkins' architecture wasn't designed for horizontal scaling of the controller — the "Jenkins at scale" problem (thousands of jobs, hundreds of agents) requires careful JVM tuning, disk I/O optimisation, and often a controller cluster (using CasC — Configuration as Code).

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│        JENKINS EXECUTION ARCHITECTURE       │
├─────────────────────────────────────────────┤
│  CONTROLLER (master)                        │
│  - Receives webhook from GitHub             │
│  - Reads Jenkinsfile from repo              │
│  - Schedules job to agent queue             │
│  - Stores build logs + results              │
│  - Hosts UI dashboard                       │
│         ↓ Remoting/JNLP                     │
│  AGENT (executor node)                      │
│  - Checkout source code                     │
│  - Execute pipeline steps                   │
│  - Run: sh 'mvn test'                       │
│  - Collect: JUnit XML, artifacts            │
│  - Report results back to controller        │
└─────────────────────────────────────────────┘
```

**Declarative Pipeline structure:**
```groovy
// Jenkinsfile (Declarative)
pipeline {
    // Run on any agent, or label: 'linux'
    agent { label 'linux' }

    environment {
        // Available to all stages
        JAVA_OPTS = '-Xmx512m'
    }

    stages {
        stage('Build') {
            steps {
                sh 'mvn --batch-mode package -DskipTests'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn --batch-mode test'
            }
            post {
                always {
                    // Archive test results regardless of outcome
                    junit 'target/surefire-reports/*.xml'
                    jacoco execPattern: 'target/jacoco.exec'
                }
            }
        }
        stage('Docker Build') {
            steps {
                script {
                    def tag = env.GIT_COMMIT.take(7)
                    sh "docker build -t myapp:${tag} ."
                    sh "docker push myapp:${tag}"
                }
            }
        }
    }

    post {
        failure {
            slackSend channel: '#ci-alerts',
              message: "Build FAILED: ${env.BUILD_URL}"
        }
    }
}
```

**Kubernetes dynamic agents:** Instead of fixed permanent agents, spin up a pod per build:
```groovy
agent {
    kubernetes {
        yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.9-eclipse-temurin-21
    command: [ "cat" ]
    tty: true
  - name: docker
    image: docker:dind
    securityContext:
      privileged: true
'''
    }
}
```

Each build gets a fresh pod, isolated from other builds, deleted after completion.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer pushes to GitHub
  → GitHub webhook → Jenkins controller notified
  → Controller: reads Jenkinsfile [← YOU ARE HERE]
  → Kubernetes pod spawned as build agent
  → Agent: git checkout → mvn test → docker build
  → Results sent to controller
  → Pod terminated (ephemeral agent)
  → Build result: GREEN
  → GitHub PR: ✓ all checks passed
  → Slack notification: "#4821 passed: feature/new-checkout"
```

**FAILURE PATH:**
```
mvn test fails → stage marked FAILED
  → post { failure { slackSend ... } } executes
  → JUnit XML archived (test failure details visible in UI)
  → Kubernetes pod terminated
  → Controller: build #4821 marked FAILURE
  → GitHub PR: ✗ — merge blocked
```

**WHAT CHANGES AT SCALE:**
At 500+ jobs, the Jenkins controller's JVM heap must be tuned (4–8 GB). Build history takes 10s+ to load in the UI. Plugin conflicts increase with more plugins installed. Solutions: Jenkins Configuration as Code (JCasC) for reproducible controller config; the Jenkins Operations Center (CloudBees) for multi-controller federation; migrating performance-sensitive pipelines to GitHub Actions while keeping complex orchestration in Jenkins.

---

### 💻 Code Example

**Example 1 — Parallel stages in Declarative Pipeline:**
```groovy
stage('Quality Gates') {
    parallel {
        stage('Unit Tests') {
            steps {
                sh 'mvn test -pl :unit-tests'
            }
        }
        stage('Static Analysis') {
            steps {
                sh 'mvn checkstyle:check pmd:check'
            }
        }
        stage('Security Scan') {
            steps {
                // OWASP dependency check
                sh 'mvn org.owasp:dependency-check-maven:check'
            }
        }
    }
}
```

**Example 2 — Shared Library usage:**
```groovy
// Jenkinsfile in application repo
@Library('my-shared-lib@main') _

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Calls src/vars/dockerBuild.groovy
                // in the shared library repo
                dockerBuild(
                    imageName: 'myapp',
                    registry: 'myorg'
                )
            }
        }
    }
}
```

---

### ⚖️ Comparison Table

| CI Tool | Hosting | Config | Flexibility | Ops Cost | Best For |
|---|---|---|---|---|---|
| **Jenkins** | Self-hosted | Groovy DSL | Very High | Very High | Complex pipelines, air-gapped |
| GitHub Actions | Hosted | YAML | High | None | GitHub repositories |
| GitLab CI | Self/Hosted | YAML | High | Low–Medium | GitLab repositories |
| CircleCI | Hosted | YAML | Medium | None | Speed-focused teams |
| Tekton | Kubernetes | YAML (CRDs) | Very High | Medium | Cloud-native K8s pipelines |

How to choose: Use GitHub Actions for GitHub-hosted repositories — it's integrated, zero-ops, and sufficient for most teams. Choose Jenkins when you need: on-premises execution (air-gapped environments), complex orchestration logic beyond YAML DSL capabilities, or want to avoid per-minute billing at very high build volumes.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Jenkins is outdated and should be replaced immediately | Jenkins is still widely deployed, actively maintained, and appropriate for many use cases — especially air-gapped environments and complex orchestration |
| Freestyle projects are deprecated | Freestyle projects still work but lack Pipeline-as-Code benefits. New projects should always use Declarative Pipeline (Jenkinsfile) |
| Jenkins master failure only affects new builds | Jenkins master stores ALL build history and job configuration. Master failure without backup means losing the entire CI history and configuration |
| More plugins = better Jenkins | Each plugin adds compatibility risk. Minimise installed plugins; use pipeline steps instead of UI-configured plugins where possible |
| Declarative and Scripted Pipeline are interchangeable | Declarative Pipeline is structured (enforces syntax), easier to maintain. Scripted Pipeline is full Groovy, more powerful but much harder to audit and maintain |

---

### 🚨 Failure Modes & Diagnosis

**1. Jenkins Master Disk Full — Builds Queue Forever**

**Symptom:** Builds stop starting. Jenkins UI shows jobs queued but no agents picking them up. Controller disk usage at 100%.

**Root Cause:** Build logs and workspace files accumulate. Default configuration keeps all builds forever. 10,000 builds × 10 MB logs = 100 GB.

**Diagnostic:**
```bash
# Check disk usage on Jenkins master
df -h $JENKINS_HOME
# Find large directories
du -sh $JENKINS_HOME/jobs/*/builds/ | sort -rh | head -20
# Check for workspace accumulation
du -sh $JENKINS_HOME/workspace/* | sort -rh | head -10
```

**Fix:** Configure build retention in pipeline:
```groovy
options {
    buildDiscarder(logRotator(
        numToKeepStr: '20',    // keep last 20 builds
        artifactNumToKeepStr: '5'
    ))
}
```

**Prevention:** Set build retention policy on every job. Schedule workspace cleanup with periodic scripts.

---

**2. Plugin Conflict After Update Breaks Pipeline**

**Symptom:** After updating Jenkins or a plugin, pipelines fail with `NoSuchMethodError` or `ClassCastException`.

**Root Cause:** Plugin A depends on Plugin B version 2.x, but Plugin B was updated to 3.x which changed its API. Jenkins doesn't enforce plugin dependency version constraints strictly.

**Diagnostic:**
```bash
# Check Jenkins system log for plugin errors
# UI: Manage Jenkins → System Log → All Jenkins logs
# Or check logs on container
docker logs jenkins-controller | grep -i "plugin\|ERROR" \
  | tail -50
```

**Fix:** Roll back the updated plugin in: Manage Jenkins → Manage Plugins → Installed. Test in a staging Jenkins before updating production.

**Prevention:** Never update plugins directly on the production Jenkins controller. Use JCasC + Docker to maintain a tested Jenkins configuration in version control. Test plugin updates in a staging environment first.

---

**3. Build Queue Starvation — Agents Idle But Jobs Wait**

**Symptom:** Jobs queue for 30+ minutes. Jenkins shows 10 online agents but no jobs are assigned to them.

**Root Cause:** Jobs specify an agent `label` that doesn't match any available agent. Or the agent is online but executor count is 0. Or node is in "suspended" state.

**Diagnostic:**
```bash
# Via Jenkins CLI
java -jar jenkins-cli.jar \
  -s http://jenkins-host:8080/ \
  list-jobs | head -20

# Check agent status via REST API
curl -s http://jenkins/computer/api/json \
  | jq '.computer[] | {name:.displayName, offline:.offline,
         executors:.numExecutors}'
```

**Fix:** Check agent labels match pipeline `agent { label ... }`. Set executor count > 0 on agents. Investigate offline agents (disk full, Java crash, network partition).

**Prevention:** Monitor agent availability with a Prometheus plugin. Alert when queued build wait time exceeds 5 minutes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — Jenkins implements CI; understanding the practice is required before configuring the tool
- `Pipeline as Code` — Jenkins' Jenkinsfile is an implementation of Pipeline as Code; this concept is the foundation
- `Pipeline` — Jenkins' core model is the pipeline of stages; understanding pipeline structure is needed

**Builds On This (learn these next):**
- `Pipeline as Code` — Jenkinsfile is Pipeline as Code; understanding this concept improves Jenkins maintainability
- `GitOps` — an alternative deployment model that can replace Jenkins' deployment stages
- `Tekton` — a cloud-native alternative for Kubernetes-based CI/CD that addresses Jenkins' architectural limitations

**Alternatives / Comparisons:**
- `GitHub Actions` — hosted CI/CD tightly integrated with GitHub; zero operations; most common Jenkins alternative for cloud teams
- `GitLab CI` — similar hosted CI with stronger SCM integration and no separate tool
- `CircleCI` — hosted CI focused on speed and simplicity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Open-source automation server running     │
│              │ CI/CD pipelines via Jenkinsfile           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No standard, extensible tool for          │
│ SOLVES       │ automated builds in any environment       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Maximum flexibility + plugin ecosystem =  │
│              │ maximum operational complexity            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Air-gapped networks, complex pipeline      │
│              │ logic, or high-volume builds (no billing) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Team wants zero-ops CI on GitHub-hosted   │
│              │ repos — GitHub Actions is simpler         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full control + free at scale vs           │
│              │ significant ongoing operational burden    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The Swiss Army knife of CI — does        │
│              │  everything, maintained by you"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GitHub Actions → GitLab CI → Tekton       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your company runs Jenkins on a single VM with 50 jobs averaging 20 builds per day each. The Jenkins controller has 8 GB RAM, 200 GB disk. Three months from now, the team will triple in size and build frequency. Design the Jenkins architecture that would handle 150 jobs at 60 builds/day — covering controller sizing, agent strategy (ephemeral Kubernetes vs static), build history retention, and the monitoring you'd put in place to detect capacity issues before they cause outages.

**Q2.** Your team is migrating from Jenkins to GitHub Actions for a set of 30 pipelines. 25 pipelines are straightforward and already mapped to YAML equivalents. But 5 pipelines use advanced Groovy scripted logic: dynamic stage generation based on runtime conditions, shared library functions with 500 lines of Groovy, and cross-job artifact passing. Describe your migration strategy for these 5 complex pipelines — specifically addressing what GitHub Actions can replicate natively vs what requires architectural changes to the pipeline logic itself.

