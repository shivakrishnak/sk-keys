---
layout: default
title: "Spring Batch Job / Step / Tasklet"
parent: "Spring Core"
nav_order: 2121
permalink: /spring/spring-batch-job-step-tasklet/
number: "2121"
category: Spring Core
difficulty: ★★★
depends_on: Spring Batch, Spring Core
used_by: Spring Batch ItemReader / ItemProcessor / ItemWriter, Spring Batch Chunk Processing
related: Spring Batch, Quartz Scheduler, Spring State Machine
tags:
  - java
  - spring
  - dataengineering
  - advanced
---

# 2121 — Spring Batch Job / Step / Tasklet

⚡ **TL;DR —** A Job is a named batch process composed of Steps; a Tasklet is the simplest Step type executing arbitrary single-operation logic in one transaction.

| Metadata | Values |
|---|---|
| **Depends on** | Spring Batch, Spring Core |
| **Used by** | Spring Batch ItemReader / ItemProcessor / ItemWriter, Spring Batch Chunk Processing |
| **Related** | Spring Batch, Quartz Scheduler, Spring State Machine |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** You have a complex nightly ETL: clean temp tables, import CSV, validate data, load to data warehouse, send a report email. You write one giant method. It fails mid-way. You have no record of which phase succeeded, and rerunning repeats all prior phases, causing duplicates and overwritten data.

**THE BREAKING POINT:** Multi-phase batch processes need: independent phases with different error handling; phases that can be skipped on restart if already completed; conditional branching (if validation fails, route to a notification step instead of the load step); and a per-phase audit trail. None of this exists in a single-method approach.

**THE INVENTION MOMENT:** Spring Batch models a batch process as a **Job** — a named, ordered collection of **Steps**. Each Step is independently tracked and can be individually restarted. A **Tasklet** covers simple one-shot operations (file deletion, stored procedure calls). Chunk-oriented Steps cover high-volume pipelines. Conditional flow between Steps is expressed as a declarative state machine using `ExitStatus` strings.

---

### 📘 Textbook Definition

In Spring Batch, a **Job** is the top-level batch entity — identified by name, parameterized by `JobParameters`, and constrained so the same `JobInstance` (name + parameters) can only complete once. A **Step** is an independent, ordered unit of work within a Job with its own `StepExecution`, status, and restart semantics. A **Tasklet** is a functional interface with a single method `execute(StepContribution, ChunkContext) → RepeatStatus` used for arbitrary non-chunk work. Steps are orchestrated by a **Job flow** which may be sequential, conditional (routing on `ExitStatus`), or parallel (via `split()`).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Job is the process, Step is the phase, Tasklet is the simplest unit of step work.

> Think of a Job as a recipe, Steps as individual cooking instructions, and a Tasklet as a simple instruction that doesn't involve an assembly line — like "preheat the oven" before the production line starts.

**One insight:** The distinction between Tasklet and chunk-oriented steps is between "do this thing once" and "do this thing for every record in a dataset" — and Spring Batch chooses the correct transaction model for each automatically.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **A JobInstance completes exactly once** — same name + same parameters = same instance; cannot COMPLETE twice
2. **Steps execute and record independently** — each Step has its own `StepExecution`; prior COMPLETED steps are skipped on restart
3. **Tasklet runs in a single transaction** — the entire `execute()` body is one TX; return `RepeatStatus.FINISHED` or `RepeatStatus.CONTINUABLE`
4. **ExitStatus drives step routing** — `on("COMPLETED").to(step2)`, `on("FAILED").to(notifyStep)` — string-based, not enum-based
5. **Steps are non-overlapping by default** — sequential unless explicitly parallelized with `split()`

**DERIVED DESIGN:**

The `ExitStatus`-based flow emerged from enterprise reality: a validation step returning `"VALIDATION_FAILED"` must route to a notification step, not a data load step. String-based exit codes allow custom routing semantics without modifying the framework's flow engine.

**THE TRADE-OFFS:**

**Gain:** Fine-grained restart (only the failed step reruns); conditional branching without custom orchestration code; clear separation of concerns between phases; per-step audit trail.

**Cost:** Requires upfront design thinking to decompose a job correctly into steps — over-decomposition adds Job Repository overhead; under-decomposition loses restart granularity; step-to-step data sharing requires careful `ExecutionContext` management.

---

### 🧪 Thought Experiment

**SETUP:** A job has 3 steps: (1) validate input file, (2) load records to DB, (3) archive the input file.

**WHAT HAPPENS WITHOUT PROPER STEP DESIGN:** Steps 1 and 3 are collapsed into Step 2. Step 2 fails halfway through the load. On restart, Step 2 re-validates (wasting time) and tries to archive a file that hasn't been fully loaded yet. You've lost restart granularity and introduced state bugs.

**WHAT HAPPENS WITH PROPER STEP DESIGN:** Step 1 completes (COMPLETED status persisted). Step 2 fails at record 25,000. On restart, Spring Batch sees Step 1 is COMPLETED — skips it automatically. Step 2 resumes at the last committed chunk offset. Step 3 runs only after Step 2 completes successfully.

**THE INSIGHT:** Step decomposition is an architectural decision that determines restart granularity. Design steps around natural transaction boundaries and phase independence, not code organization. The finer the steps, the less work is repeated on failure — but every step boundary has overhead.

---

### 🧠 Mental Model / Analogy

> A movie production has a Script (Job), Scenes (Steps), and individual camera shots (Tasklets). The director's script has conditional directions: "if Scene 3 is rained out (EXIT STATUS = RAIN), film Scene 3b indoors instead of going to Scene 4."

- **Movie production** → Job (named, parameterized, runs once)
- **Scene** → Step (independent, tracked, can be restarted)
- **Camera shot** → Tasklet (atomic operation, one transaction)
- **Director's conditional script** → Job flow with `on().to()` routing
- **Continuity notes** → `ExecutionContext` (state passed between steps)
- **Production log** → Job Repository (records what ran when and how)

Where this analogy breaks down: Unlike film, Spring Batch Steps don't share memory directly — they communicate through the serialized `ExecutionContext`, which limits the size and type of data that can be passed between steps.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Job is the whole batch task. A Step is one phase of that task. A Tasklet is a step that does exactly one thing — like cleaning up temp files before the real processing begins.

**Level 2 — How to use it (junior developer):**
Define a `Job` bean with `JobBuilder`, a `Step` bean with `StepBuilder`. For simple work, implement `Tasklet` returning `RepeatStatus.FINISHED`. For chunked work, use `.chunk(size)`. Connect steps with `.next()` for sequential flow or `.on("FAILED").to(otherStep)` for conditional routing.

**Level 3 — How it works (mid-level engineer):**
`JobLauncher` creates a `JobExecution`, then iterates the step sequence managed by `JobFlowExecutor`. For each step, a `StepExecution` is created and `Step.execute(StepExecution)` is called. For Tasklet steps, `TaskletStep` wraps the Tasklet in a `TransactionTemplate` and calls `execute()` in a loop until `RepeatStatus.FINISHED` or an exception. The step's `ExitStatus` propagates into `JobFlowExecutor` which pattern-matches against declared `on()` transitions to determine the next step.

**Level 4 — Why it was designed this way (senior/staff):**
The `ExitStatus` string model is deliberately open — the framework defines `COMPLETED`, `FAILED`, `STOPPED`, `UNKNOWN`, but applications can return any string. This avoids enum coupling between framework and application code. The `RepeatStatus.CONTINUABLE` return from Tasklet enables polling patterns — keep calling `execute()` until an external resource is ready — without spawning threads or using a scheduler. The step simply loops within a single `StepExecution`, sleeping between calls, and the framework treats each call as one transaction.

---

### ⚙️ How It Works (Mechanism)

```
[Job.execute(JobExecution)]
        │
        ▼
[JobFlowExecutor iterates steps]
        │
        ├── Step 1 (Tasklet)
        │   ┌──────────────────────────────┐
        │   │ TX begin                     │
        │   │ tasklet.execute()            │
        │   │ → RepeatStatus.FINISHED      │
        │   │ TX commit                    │
        │   │ StepExecution: COMPLETED     │
        │   │ ExitStatus evaluated         │
        │   └──────────────────────────────┘
        │
        │ ExitStatus pattern match:
        ├── "COMPLETED" → Step 2 (Chunk)
        └── "FAILED"    → Step 2b (Notify)

[Step 2 — Chunk-oriented]
  read×N → process×N → write(N) → TX commit
  StepExecution: readCount, writeCount saved
        │
        ▼
[Step 3 — Tasklet: archive file]
        │
        ▼
[JobExecution: COMPLETED]
```

**Key types:**
- `SimpleJob` — sequential step list, used by `JobBuilder`
- `FlowJob` — conditional state machine, used with `on().to()`
- `TaskletStep` — wraps a `Tasklet` in a transaction loop
- `FaultTolerantStepBuilder` — adds skip/retry to chunk steps
- `StepContribution` — accumulates read/write/skip counts for the current TX
- `ChunkContext` — provides access to `StepContext` and attribute store

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[JobLauncher.run(job, params)]
      │ ← YOU ARE HERE
      ▼
[JobRepository: JobExecution STARTED]
      │
      ▼
[Step 1 — Tasklet: validateFile]
  TX: execute() → RepeatStatus.FINISHED
  StepExecution: COMPLETED, exitCode=COMPLETED
      │
      ▼
[Step 2 — Chunk: loadRecords]
  Chunk loop: read→process→write→commit
  StepExecution: COMPLETED, readCount=50000
      │
      ▼
[Step 3 — Tasklet: archiveFile]
  TX: execute() → RepeatStatus.FINISHED
  StepExecution: COMPLETED
      │
      ▼
[JobExecution: COMPLETED]
```

**FAILURE PATH:**
```
[Step 2 fails at record 25,001]
      │
      ▼
[StepExecution: FAILED]
[JobExecution: FAILED]
      │ (restart with same JobParameters)
      ▼
[Step 1: COMPLETED → automatically SKIPPED]
[Step 2: FAILED → resumes from chunk offset 25000]
[Step 3: runs after Step 2 COMPLETED]
```

**WHAT CHANGES AT SCALE:**
For parallel step execution, `split()` in the `JobBuilder` runs a set of flows concurrently on a `TaskExecutor`. Each parallel flow has independent `StepExecution` records. The `JobExecution` waits for all splits to complete before proceeding to the next step. This is suitable when Step A and Step B have no data dependencies.

---

### 💻 Code Example

**BAD — monolithic Tasklet doing everything:**
```java
@Bean
public Tasklet monolithicTasklet() {
    return (contribution, chunkContext) -> {
        // No restart granularity — all or nothing
        validateFile();       // Step 1 work
        loadAllRecords();     // Step 2 work (no chunking)
        archiveFile();        // Step 3 work
        return RepeatStatus.FINISHED;
    };
}
```

**GOOD — proper Job/Step decomposition with conditional flow:**
```java
@Bean
public Job importJob(
        JobRepository repo,
        Step validateStep,
        Step loadStep,
        Step archiveStep,
        Step notifyStep) {
    return new JobBuilder("importJob", repo)
        .start(validateStep)
            .on("FAILED").to(notifyStep)
        .from(validateStep)
            .on("COMPLETED").to(loadStep)
        .from(loadStep)
            .next(archiveStep)
        .end()
        .build();
}

@Bean
public Step validateStep(
        JobRepository repo,
        PlatformTransactionManager tm) {
    return new StepBuilder("validateStep", repo)
        .tasklet(validateTasklet(), tm)
        .build();
}

@Bean
public Tasklet validateTasklet() {
    return (contribution, context) -> {
        String path = (String) context
            .getStepContext()
            .getJobParameters()
            .get("input.file");
        if (!Files.exists(Path.of(path))) {
            // Signal conditional routing via ExitStatus
            contribution.setExitStatus(
                new ExitStatus("FAILED",
                    "Input file not found: " + path));
        }
        return RepeatStatus.FINISHED;
    };
}

@Bean
public Step loadStep(
        JobRepository repo,
        PlatformTransactionManager tm,
        ItemReader<Record> reader,
        ItemWriter<Record> writer) {
    return new StepBuilder("loadStep", repo)
        .<Record, Record>chunk(1000, tm)
        .reader(reader)
        .writer(writer)
        .faultTolerant()
        .skipLimit(100)
        .skip(DataAccessException.class)
        .build();
}

// Promote step context to job context for later steps
@Bean
public ExecutionContextPromotionListener promotionListener() {
    ExecutionContextPromotionListener l =
        new ExecutionContextPromotionListener();
    l.setKeys(new String[]{"output.path"});
    return l;
}
```

---

### ⚖️ Comparison Table

| Aspect | Tasklet Step | Chunk-Oriented Step |
|---|---|---|
| **Use case** | Single operation (file op, proc) | High-volume read/process/write |
| **Transaction** | Whole Tasklet body in one TX | Per-chunk transaction |
| **Restart granularity** | Reruns from beginning | Resumes from last chunk offset |
| **Memory model** | You control (no buffering) | Bounded by chunk size |
| **Complexity** | Low | Medium–High |
| **Loop support** | `CONTINUABLE` for polling | Natural — reader returns null |
| **Skip/Retry** | Manual in your code | Declarative via builder |
| **Best for** | Setup, teardown, notifications | ETL, data migration, reports |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Tasklet is only for trivial jobs" | Tasklets can call complex services, invoke stored procs, or orchestrate external systems. The constraint is one transaction for the whole `execute()` call, not simplicity of the logic inside. |
| "Steps always run in order" | By default yes, but `on().to()` conditional flows can branch, skip steps, or terminate early based on `ExitStatus` string patterns. |
| "FAILED JobExecution means all steps failed" | Only the step that failed has FAILED status. All prior COMPLETED steps are preserved and won't re-execute on restart. |
| "You can share state between steps with Spring beans" | Sharing mutable state via singleton beans causes race conditions in partitioned/parallel jobs. Use `ExecutionContext` for cross-step data passing. |
| "ExitStatus and BatchStatus are the same thing" | `BatchStatus` is the internal framework enum (COMPLETED, FAILED, STOPPED). `ExitStatus` is the application-defined string used for conditional routing. Both exist on `StepExecution`. |
| "`allowStartIfComplete(true)` makes a step restart always" | It makes the step eligible to re-run even if previously COMPLETED — useful for idempotent steps like file cleanup that must always run. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Step skipped on restart when it should re-execute**

**Symptom:** After a job failure, a restart skips a step that you expected to re-run.
**Root Cause:** The step previously completed — Spring Batch correctly skips COMPLETED steps. You expected re-execution because you forgot to add `allowStartIfComplete(true)` to an always-run step.
**Diagnostic:**
```sql
SELECT step_name, status, exit_code
FROM batch_step_execution
WHERE job_execution_id = (
    SELECT job_execution_id FROM batch_job_execution
    WHERE job_instance_id = ? ORDER BY create_time DESC
    LIMIT 1
)
ORDER BY start_time;
```
**Fix:**
```java
// Force re-execution even if previously COMPLETED
return new StepBuilder("cleanupStep", repo)
    .tasklet(cleanupTasklet(), tm)
    .allowStartIfComplete(true)  // always runs on restart
    .build();
```
**Prevention:** Apply `allowStartIfComplete(true)` to idempotent steps like file cleanup, notification, and metadata initialization.

**Mode 2: `JobInstanceAlreadyCompleteException` blocks rerun**

**Symptom:** `JobInstanceAlreadyCompleteException: A job instance already exists and is complete for parameters={}`.
**Root Cause:** Empty `JobParameters` were used and a previous run with the same empty parameters already COMPLETED.
**Diagnostic:**
```sql
SELECT ji.job_name, je.status, je.create_time
FROM batch_job_instance ji
JOIN batch_job_execution je
  ON ji.job_instance_id = je.job_instance_id
WHERE je.status = 'COMPLETED'
AND ji.job_name = 'importJob';
```
**Fix:**
```java
// Add unique run identifier to create a new JobInstance
jobLauncher.run(job, new JobParametersBuilder()
    .addLocalDate("date", LocalDate.now())
    .addLong("run.id", System.currentTimeMillis())
    .toJobParameters());
```
**Prevention:** Always include a date or timestamp parameter to differentiate daily runs.

**Mode 3: Cross-step data not found — `ExecutionContext` confusion**

**Symptom:** Data written to `ExecutionContext` in Step 1 returns null when read in Step 3.
**Root Cause:** Data was written to the *Step* `ExecutionContext` (step-scoped) but read from the *Job* `ExecutionContext` (job-scoped) — different objects.
**Diagnostic:**
```java
// In Step 1 tasklet — writes to STEP context
context.getStepContext().getStepExecution()
    .getExecutionContext().put("filePath", path);  // STEP scope

// In Step 3 tasklet — reads from JOB context
context.getStepContext().getStepExecution()
    .getJobExecution().getExecutionContext()
    .getString("filePath");  // JOB scope → null!
```
**Fix:** Use `ExecutionContextPromotionListener` to automatically promote step keys to job scope after step completion, or write directly to `getJobExecution().getExecutionContext()`.
**Prevention:** Use Step context for restart-checkpoint data (reader offsets) and Job context for cross-step communication. Document which keys belong to which scope.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Spring Batch (2120) — overall framework, Job Repository, chunk model
- Spring Core — DI, `@Configuration`, bean lifecycle

**Builds On This (learn these next):**
- Spring Batch ItemReader / ItemProcessor / ItemWriter (2122) — the I/O contracts for chunk steps
- Spring Batch Chunk Processing (2123) — the transaction and retry mechanics inside chunk steps

**Alternatives / Comparisons:**
- Spring State Machine — for complex workflow state machines that exceed Spring Batch's step-routing capabilities
- AWS Step Functions — cloud-native managed workflow; replaces Job flow for serverless architectures
- Quartz Scheduler — triggers Spring Batch jobs on a schedule; doesn't define internal job structure

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS   │ Job=process, Step=phase,          │
│              │ Tasklet=atomic unit of work        │
│ PROBLEM      │ Multi-phase restartable batch     │
│ KEY INSIGHT  │ ExitStatus strings drive routing  │
│ USE WHEN     │ Multi-phase ETL; skip-done steps  │
│ AVOID WHEN   │ Single-shot scripts               │
│ TRADE-OFF    │ Step design upfront vs flexibility│
│ ONE-LINER    │ Job → [Step1 → Step2 → Step3]    │
│ NEXT EXPLORE │ ItemReader / Processor / Writer   │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(A — System Interaction)** A Tasklet step calls an external REST API and sets `ExitStatus` based on the response. If the API is down, the Tasklet throws a `ConnectException`. How does Spring Batch differentiate between a "FAILED" business outcome and a transient infrastructure failure, and how would you configure the step to retry on transient errors without routing to the failure branch?

2. **(C — Design Trade-off)** You're designing a 5-step import job. Steps 2 and 3 each take 30 minutes. Should you combine them into one step or keep them separate? What are the trade-offs for restart granularity, transaction semantics, and `ExecutionContext` management?

3. **(E — First Principles)** `RepeatStatus.CONTINUABLE` causes a Tasklet to be called repeatedly in a loop. What is the transaction boundary for each loop iteration, and why does this design enable polling patterns without requiring an external scheduler or dedicated thread?
