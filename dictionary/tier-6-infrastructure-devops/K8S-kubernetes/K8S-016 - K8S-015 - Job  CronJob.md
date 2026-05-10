---
version: 1
layout: default
title: "Job  CronJob"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /kubernetes/job-cronjob/
id: K8S-016
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "Deployment"]
used_by: ["Batch Processing", "Database Migrations"]
related: ["Pod", "Deployment", "ConfigMap", "Secret"]
tags: [kubernetes, job, cronjob, batch, scheduled, k8s]
---

# Job / CronJob

## ⚡ TL;DR

A **Job** runs a Pod to completion (exit 0) - for batch tasks. A **CronJob** creates Jobs on a schedule (cron syntax). Neither self-heals after completion - they're finite, not continuous. Use for: data migrations, report generation, ML training runs.

---

## 🔥 Problem This Solves

Some workloads need to run once and finish: batch ETL jobs, database migrations, nightly reports. Deployments keep Pods running indefinitely. Jobs run them to completion and track success/failure.

---

## 📘 Textbook Definition

A Job creates one or more Pods and retries until a specified number complete successfully. A CronJob creates Jobs periodically on a Cron schedule.

---

## ⏱️ 30 Seconds

```yaml
# Job
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  completions: 1
  parallelism: 1
  backoffLimit: 3 # retry up to 3 times
  template:
    spec:
      restartPolicy: OnFailure # Never or OnFailure (not Always)
      containers:
        - name: migration
          image: my-app:1.1
          command: ["./migrate.sh"]

---
# CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *" # 2 AM every day
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: report
              image: reporter:1.0
```

---

## 🔩 First Principles

- Job `restartPolicy` must be `OnFailure` or `Never` (not `Always`)
- `completions`: total successful runs required (default 1)
- `parallelism`: concurrent Pod count
- Job finishes when `completions` successful completions happen
- CronJob keeps last 3 successful / 1 failed Job by default (configurable)

---

## 🧪 Thought Experiment

You're running a database migration as part of deployment. Running it as a Deployment Pod would restart the migration on failure indefinitely - potentially running it multiple times and corrupting data. A Job with `completions=1` + idempotent migration script runs once, retries on transient failure, and tracks success/failure cleanly.

---

## 🧠 Mental Model / Analogy

A Job is like a **contractor** hired for a specific task: "fix the pipes." When done, they leave. A Deployment is a **permanent employee** who keeps working indefinitely. A CronJob is a **cleaning crew** scheduled every Monday at 9am - a new contractor crew each time.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Job runs a task until it succeeds. CronJob runs it on a schedule (like cron).

**Level 2 - Practitioner**: `backoffLimit` controls retry count. Failed Pods are kept for log inspection. `ttlSecondsAfterFinished` auto-deletes completed Jobs.

**Level 3 - Advanced**: `concurrencyPolicy: Forbid` prevents CronJob from spawning new Job if previous still running. `Allow` (default) = multiple Jobs can overlap. `Replace` = cancel old, start new.

**Level 4 - Expert**: Indexed Jobs (`completionMode: Indexed`) assign unique index to each Pod (useful for parallel data processing: Pod 0 processes partition 0, etc.). `activeDeadlineSeconds` sets overall Job timeout. Parallel work queue: `completions > 1, parallelism > 1`.

---

## ⚙️ How It Works

### Job Completion Patterns

| Pattern              | `completions` | `parallelism` | Use case                    |
| -------------------- | ------------- | ------------- | --------------------------- |
| Single task          | 1             | 1             | DB migration                |
| Fixed count parallel | N             | M             | Process N files in parallel |
| Work queue           | unset         | M             | Pull from queue until empty |
| Indexed              | N             | M             | Sharded batch (Job 0...N-1) |

### CronJob Schedule Syntax

```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6, Sun=0)
  0 2 * * *    → 2:00 AM daily
  */5 * * * *  → Every 5 minutes
  0 0 1 * *    → Midnight on 1st of every month
```

### Cleanup

```yaml
# Auto-delete finished Job after 100 seconds
spec:
  ttlSecondsAfterFinished: 100

# CronJob: keep last N completed/failed Jobs
spec:
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
```

---

## 🔄 E2E Flow: Nightly Report CronJob

```
CronJob triggers at 2:00 AM
  → Creates Job object
  → Job creates Pod
  → Pod runs report generator
  → Report uploaded to S3
  → Pod exits 0 → Job status: Complete
  → Old Job deleted (per successfulJobsHistoryLimit)
```

---

## ⚖️ Comparison Table

|               | Job                        | CronJob                    | Deployment             |
| ------------- | -------------------------- | -------------------------- | ---------------------- |
| **Purpose**   | Run-to-completion          | Scheduled batch            | Always-running service |
| **Restarts**  | On failure (limited)       | On failure (limited)       | Always                 |
| **When done** | Pod kept (logs), Job stays | Job kept per history limit | Never "done"           |
| **Use case**  | Migration, ETL run         | Nightly reports, cleanup   | API server, worker     |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                         |
| ---------------------------------------- | ------------------------------------------------------------------------------- |
| "Job Pods are deleted on completion"     | Pods stay for log inspection; use `ttlSecondsAfterFinished` to clean up         |
| "CronJob guarantees exactly-once"        | Job may create multiple Pods on failure; design migrations idempotently         |
| "`restartPolicy: Always` works for Jobs" | Jobs require `OnFailure` or `Never`                                             |
| "CronJob runs exactly on time"           | CronJob has `startingDeadlineSeconds` - can miss schedule if controller is down |

---

## 🚨 Failure Modes

| Failure                    | Symptom               | Fix                                                                        |
| -------------------------- | --------------------- | -------------------------------------------------------------------------- |
| Migration runs twice       | Data inconsistency    | Make migrations idempotent (IF NOT EXISTS, UPSERT)                         |
| Missed CronJob schedule    | Job not created       | Check `startingDeadlineSeconds`; CronJob missed > 100 triggers = suspended |
| Job backoff limit exceeded | Job status: Failed    | Fix bug, then delete+recreate Job                                          |
| Zombie old Jobs pile up    | API Server overloaded | Set `ttlSecondsAfterFinished` and history limits                           |

---

## 🔗 Related Keywords

- [Pod](/kubernetes/pod/) - created by Job
- [Deployment](/kubernetes/deployment/) - for always-running services
- [ConfigMap](/kubernetes/configmap/) - inject job configuration
- [Secret](/kubernetes/secret/) - inject credentials

---

## 📌 Quick Reference Card

```bash
# Create and run a Job
kubectl create job test-job --image=busybox -- echo "hello"

# List Jobs / CronJobs
kubectl get jobs
kubectl get cronjobs

# Watch Job progress
kubectl describe job db-migration

# Get logs from Job Pod
kubectl logs -l job-name=db-migration

# Manually trigger CronJob
kubectl create job --from=cronjob/nightly-report manual-run-001

# Delete completed Jobs
kubectl delete jobs --field-selector status.successful=1
```

---

## 🧠 Think About This

Why must migrations be idempotent even when using a Job? Because `backoffLimit > 1` means the migration can run multiple times on transient failure. And in distributed systems, network timeouts mean "did it actually run or not?" is uncertain. Write migrations that check current state and skip if already applied - this is safer than relying on Job's at-most-once guarantee.
