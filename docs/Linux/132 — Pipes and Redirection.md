---
layout: default
title: "Pipes and Redirection"
parent: "Linux"
nav_order: 132
permalink: /linux/pipes-and-redirection/
number: "0132"
category: Linux
difficulty: ★☆☆
depends_on: stdin / stdout / stderr, Shell (bash, zsh)
used_by: Shell Scripting, grep / awk / sed, find / xargs
related: stdin / stdout / stderr, Shell Scripting, Shell (bash, zsh)
tags:
  - linux
  - os
  - foundational
  - internals
---

# 132 — Pipes and Redirection

⚡ TL;DR — Pipes (`|`) and redirection (`>`, `<`, `2>`) connect programs by wiring their stdin/stdout/stderr to each other or to files, turning small tools into powerful data processing pipelines.

| #132            | Category: Linux                                 | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | stdin / stdout / stderr, Shell (bash, zsh)      |                 |
| **Used by:**    | Shell Scripting, grep / awk / sed, find / xargs |                 |
| **Related:**    | stdin / stdout / stderr, Shell Scripting        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You want to find all unique IP addresses in an nginx access log, sorted by frequency. Without pipes, you'd need to: (1) write a program that reads the log, (2) extracts IPs, (3) sorts them, (4) counts duplicates, (5) sorts by count, (6) displays results. That's one monolithic program, or five intermediate temp files. Reuse is impossible — you'd rewrite this logic for every log format.

**THE BREAKING POINT:**
Unix had `grep` (search), `sort` (sort), `uniq` (deduplicate), `awk` (extract fields), `wc` (count). Each was a complete, tested tool. But they were islands — no way to connect them without writing to disk and reading back.

**THE INVENTION MOMENT:**
Doug McIlroy invented the pipe in 1972 and described it as: "Write programs to handle text streams, because that is a universal interface." The shell pipe `|` connects one program's stdout directly to the next's stdin — in memory, with no disk I/O. In one line: `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10`. This is exactly why pipes exist: to compose small, focused tools into pipelines that outperform any monolithic program.

---

### 📘 Textbook Definition

A **pipe** (`|`) is an anonymous, kernel-managed buffer that connects the stdout (fd 1) of one process to the stdin (fd 0) of another. It is a unidirectional, first-in-first-out (FIFO) channel backed by a 64KB kernel buffer. **Redirection** is the shell mechanism for replacing a process's stdin, stdout, or stderr with a file, device, or another file descriptor. The two operators serve different purposes: pipes connect programs to programs; redirection connects programs to files/devices. Together they implement the Unix philosophy of composable tools: each program does one thing, reads from stdin, writes to stdout, and can be composed freely with others.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pipe (`|`) = connect program's output directly into next program's input; Redirection (`>`, `<`) = connect program to a file instead of the screen or keyboard.

**One analogy:**

> Water pipes connect a well to a filter to a tap. The `|` pipe in Unix is the same idea: it connects the outlet of one program to the inlet of the next. Redirection (`>`) is like diverting the tap into a bucket (file) instead of your glass. Redirection (`<`) is like using a water bottle (file) as the source instead of the well.

**One insight:**
Pipes run all connected programs simultaneously. When you type `cat bigfile | grep ERROR | wc -l`, all three programs are running in parallel. `cat` writes to the pipe; `grep` reads from one end and writes to the next; `wc` counts as data arrives. This isn't sequential — it's a concurrent data flow with backpressure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A pipe is a kernel FIFO buffer — not a file on disk.
2. Writers block when the pipe buffer is full; readers block when empty.
3. Processes in a pipeline run concurrently, not sequentially.

**DERIVED DESIGN:**

```
HOW THE SHELL BUILDS A PIPE:

Shell sees: cmd1 | cmd2

  1. pipe(pipefd)    → creates [read_fd=3, write_fd=4]

  2. fork() child1:
     dup2(write_fd, STDOUT) → child1's stdout = pipe write end
     close(read_fd)          → child1 doesn't need read end
     execve(cmd1)

  3. fork() child2:
     dup2(read_fd, STDIN)   → child2's stdin = pipe read end
     close(write_fd)         → child2 doesn't need write end
     execve(cmd2)

  4. Shell closes both pipe FDs
     (only children hold them now)

  5. cmd1 writes to stdout → data flows to pipe buffer
     cmd2 reads from stdin → data flows from pipe buffer

  6. cmd1 exits → write end of pipe closes → cmd2 gets EOF
```

**Redirection operators:**

| Operator               | Meaning                                   |
| ---------------------- | ----------------------------------------- |
| `cmd > file`           | Redirect stdout to file (overwrite)       |
| `cmd >> file`          | Redirect stdout to file (append)          |
| `cmd < file`           | Redirect stdin from file                  |
| `cmd 2> file`          | Redirect stderr to file                   |
| `cmd 2>&1`             | Redirect stderr to same as stdout         |
| `cmd &> file`          | Redirect stdout AND stderr to file (bash) |
| `cmd > /dev/null 2>&1` | Discard all output                        |

**THE TRADE-OFFS:**
**Gain:** No disk I/O between stages, concurrent execution, universal composability.
**Cost:** 64KB pipe buffer — high-throughput producers can fill it and block. Debugging a multi-stage pipeline is harder than reading from/to files. Pipelines are hard to partially retry.

---

### 🧪 Thought Experiment

**SETUP:**
You want the top 10 most frequent error messages in a log file. The log has 50 million lines and is 10GB.

**WHAT HAPPENS WITHOUT PIPES:**
Option A: Write a Python program to read the file, filter errors, aggregate counts, sort, print top 10. Takes 45 minutes to code, 3 minutes to run.

Option B: Shell pipeline:

```bash
grep "ERROR" app.log | \
  awk '{print $5}' | \
  sort | \
  uniq -c | \
  sort -rn | \
  head -10
```

30 seconds to write, 20 seconds to run (streaming: never loads entire file into memory).

**WHAT HAPPENS WITH PIPES:**
Each tool runs concurrently. `grep` streams lines; `awk` extracts the field immediately; `sort` buffers and sorts; `uniq -c` counts; final `sort -rn` re-sorts by count; `head -10` takes the top 10 and signals upstream tools to stop. The 10GB file is never fully loaded into memory by any single process — each tool processes it in 64KB chunks.

**THE INSIGHT:**
Pipes implement streaming computation. Each stage is a filter. The Unix pipeline is a poor man's stream processing engine — and for log analysis it's often more practical than Spark.

---

### 🧠 Mental Model / Analogy

> An assembly line in a factory. Each workstation (program) takes a component from the conveyor (stdin), does one transformation (its job), and puts it back on the conveyor (stdout). The pipe `|` is the conveyor belt between workstations. Redirection `>` is like taking the final product off the line and boxing it in a crate (file) for later.

- "Conveyor belt" → pipe (kernel FIFO buffer)
- "Workstation" → program in the pipeline
- "Raw material arriving" → stdin
- "Processed component leaving" → stdout
- "Boxing the final product" → `> file` (output redirection)
- "Reading from a crate of parts" → `< file` (input redirection)

**Where this analogy breaks down:** Conveyor belts are sequential — one item at a time. Unix pipes are concurrent byte streams — multiple items are "in transit" simultaneously, limited only by the pipe buffer size.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Pipe `|` takes what one command prints and feeds it directly as input to the next command. Redirection `>` saves what a command prints into a file instead of showing it on screen. They let you chain commands together without temporary files.

**Level 2 — How to use it (junior developer):**
`cat file | grep pattern | wc -l` — count matching lines. `cmd > output.txt` — save output. `cmd 2>&1 | tee log.txt` — see output AND save it. `sort file | uniq` — sorted unique lines. Always chain: small tools, each doing one thing. `tee` is your friend for debugging — it duplicates stdout to both a file and the next pipe stage.

**Level 3 — How it works (mid-level engineer):**
The kernel allocates a pipe buffer (typically 64KB, configurable via `fcntl(F_SETPIPE_SZ)`). The write end is fd 1 of the upstream process; the read end is fd 0 of the downstream. When the buffer is full, `write()` on the upstream blocks. When the buffer is empty, `read()` on the downstream blocks. EOF on the read end occurs when all write-end FDs are closed. Programs in a pipeline are in the same process group — `Ctrl+C` sends `SIGINT` to all of them simultaneously.

**Level 4 — Why it was designed this way (senior/staff):**
The pipe buffer size (64KB default in Linux) is a deliberate balance: large enough for smooth streaming, small enough to apply backpressure quickly. The 2012 Linux change to dynamically-sized pipes (up to 1MB) addressed throughput at cost of memory. Named pipes (FIFOs) extend the model to unrelated processes and across reboots. Socket pairs extend it across the network. The fundamental design — blocking on full/empty — implements backpressure without explicit flow control. This is the same principle used in modern streaming systems (Kafka, Reactive Streams): when the consumer is slow, the producer blocks rather than overflowing.

---

### ⚙️ How It Works (Mechanism)

**Complete pipeline example:**

```
Command: grep ERROR app.log | sort | uniq -c | sort -rn | head -5

┌──────────────────────────────────────────────────────┐
│              PIPELINE EXECUTION                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ grep    → [pipe1] → sort    → [pipe2] → uniq -c     │
│                                    → [pipe3] → sort  │
│                                    → [pipe4] → head  │
│                                                      │
│ All 5 processes run concurrently                     │
│ Each blocks when its input pipe is empty             │
│ or its output pipe is full                           │
│                                                      │
│ grep reads app.log from disk (sequential I/O)        │
│ sort must buffer ALL input before producing output   │
│   (sort is NOT a streaming operation)                │
│   → grep fills pipe1 until sort's buffer fills       │
│   → grep blocks; sort drains; sort writes to pipe2  │
│                                                      │
│ head -5: after reading 5 lines, closes its stdin    │
│   → pipe4 write end gets SIGPIPE                    │
│   → sort -rn (writing to pipe4) gets SIGPIPE        │
│   → entire pipeline terminates                       │
└──────────────────────────────────────────────────────┘
```

**`tee` — splitting a stream:**

```bash
# See output AND save it — without running the command twice
make 2>&1 | tee build.log
# tee writes to both stdout (next pipe) AND the file

# Useful debugging pattern:
cat bigfile | tee /dev/tty | process > output.txt
# /dev/tty always writes to the terminal, bypassing redirections
```

**`xargs` — convert stdin lines to arguments:**

```bash
# Find all .log files and compress them
find /var/log -name "*.log" -mtime +30 | xargs gzip
# xargs reads lines from stdin and passes them as arguments
# to the specified command (gzip here)

# With parallel execution (4 at a time)
find /var/log -name "*.log" -mtime +30 | xargs -P4 gzip
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Engineer runs:
  journalctl -u nginx --since today | grep "502" | wc -l
    ↓
Shell creates two pipes:
  pipe1: journalctl stdout → grep stdin
  pipe2: grep stdout → wc stdin
    ↓
All three processes fork and exec concurrently
    ← YOU ARE HERE (pipe connects programs)
    ↓
journalctl reads systemd journal, writes 502-containing lines
    ↓
grep filters for "502", writes matching lines to pipe2
    ↓
wc -l counts lines, writes count to stdout (terminal)
    ↓
journalctl exits → grep gets EOF → wc gets EOF → prints count
```

**FAILURE PATH:**

```
nginx has 50,000 502 errors today
    ↓
journalctl writes 50,000 lines to pipe1
    ↓
grep can't read fast enough → pipe1 buffer fills
    ↓
journalctl's write() blocks (backpressure works correctly)
    ↓
Eventually drains; no data lost; just slower throughput
```

**WHAT CHANGES AT SCALE:**
In production log pipelines, shell pipes hit limits: single-machine, single-threaded per stage (except explicit parallelism), no fault tolerance. Tools like `logstash`, `fluentd`, and `vector` replace shell pipelines for multi-machine fan-out. `parallel` (GNU parallel) adds parallelism to single-stage bottlenecks. For terabyte-scale log analysis, Spark or Flink implement the same pipeline model distributed across a cluster.

---

### 💻 Code Example

**Example 1 — Classic text processing pipeline:**

```bash
# Top 10 IPs from nginx access log
awk '{print $1}' /var/log/nginx/access.log \
  | sort \
  | uniq -c \
  | sort -rn \
  | head -10

# Count unique HTTP status codes
awk '{print $9}' /var/log/nginx/access.log \
  | sort \
  | uniq -c \
  | sort -rn
```

**Example 2 — Redirection patterns:**

```bash
# Save stdout, see errors on terminal
./build.sh > build_output.txt

# Save stderr separately
./build.sh > output.txt 2> errors.txt

# Save both to same file (stderr merged with stdout)
./build.sh > all_output.txt 2>&1

# Discard all output (run silently)
./cron_job.sh > /dev/null 2>&1

# Append to existing log
echo "[$(date)] Job complete" >> /var/log/cron.log
```

**Example 3 — `tee` for debugging pipelines:**

```bash
# Debug: see intermediate output without breaking pipeline
cat large_file.csv \
  | grep "active" \
  | tee /dev/stderr \      # show intermediate data on stderr
  | awk -F, '{print $3}' \
  | sort -u

# Save and process simultaneously
curl -sS https://api.example.com/data \
  | tee /var/cache/api_response.json \
  | jq '.items[].name'
```

**Example 4 — Here-doc and process substitution:**

```bash
# Feed multi-line data to a command
mysql -u app -p mydb <<SQL
  SELECT count(*) FROM users WHERE created_at > NOW() - INTERVAL 1 DAY;
SQL

# Process substitution: diff two sorted outputs without temp files
diff <(sort file1.txt) <(sort file2.txt)

# Merge two sorted streams
sort -m <(sort file1.txt) <(sort file2.txt) > merged_sorted.txt
```

---

### ⚖️ Comparison Table

| Mechanism         | Disk I/O   | Persistence    | Composability | Best For                        |
| ----------------- | ---------- | -------------- | ------------- | ------------------------------- |
| **Pipe (\|)**     | None       | No (in-memory) | Excellent     | Same-machine data flow          |
| Redirection (>)   | Write      | File persists  | Manual        | Saving output to disk           |
| Temp file         | Read+write | Disk           | Manual        | Re-usable intermediate data     |
| Named pipe (FIFO) | None       | Path persists  | Good          | Unrelated process communication |
| Socket            | None       | Ephemeral      | Good          | Cross-machine data flow         |

**How to choose:** Use pipes for in-process chaining (fastest, no disk). Use redirection when you need the output saved. Use named pipes when two unrelated processes need to communicate without a network.

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                 |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Commands in a pipeline run one after the other               | All commands in a pipeline run concurrently; they are synchronised by the pipe buffer (full/empty blocking)                                                                                                             |
| `cmd > file 2>&1` and `cmd 2>&1 > file` are the same         | Order matters: `> file 2>&1` redirects stdout to file THEN makes stderr = stdout (file). `2>&1 > file` makes stderr = stdout (terminal) THEN redirects stdout to file. stderr still goes to terminal in the second form |
| Pipes use disk space                                         | Pipes are in-memory kernel buffers (no disk I/O) — that's why they're faster than temp files                                                                                                                            |
| `echo "text" \| command` is the same as `command <<< "text"` | Both work; `<<<` (here-string) is slightly more efficient (no pipe, no fork); but `echo \| cmd` is more portable across shells                                                                                          |
| The pipeline exit code is the last command's exit code       | Without `set -o pipefail`, yes. With `pipefail`, the exit code is the rightmost non-zero exit code from any stage                                                                                                       |
| Closing the read end of a pipe crashes the writer            | The writer receives SIGPIPE and typically exits with code 141; it's the normal mechanism for stopping upstream producers when consumers are done                                                                        |

---

### 🚨 Failure Modes & Diagnosis

**Silent Failure: Pipeline Swallows Error Exit Code**

**Symptom:**
`process_data | sort | output > results.txt` — the overall command succeeds (exit 0) even when `process_data` fails (exit 1). CI marks the job green; bad data silently enters the output.

**Root Cause:**
Default shell behaviour: pipeline exit code = exit code of the LAST command. `sort` succeeds even on empty input → pipeline = 0.

**Diagnostic Command:**

```bash
echo "${PIPESTATUS[@]}"    # bash: shows exit code of each stage
# Or: use set -o pipefail
```

**Fix:**

```bash
set -o pipefail
process_data | sort | output > results.txt
# Now: non-zero from any stage = pipeline exit code = error
```

**Prevention:**
Always add `set -euo pipefail` at the top of scripts; check `${PIPESTATUS[@]}` when debugging.

---

**Broken Pipe (SIGPIPE) Causes Unexpected Termination**

**Symptom:**
Script shows "Broken pipe" error; partial output written; non-zero exit code.

**Root Cause:**
Downstream command (e.g., `head -1`) closes its stdin after reading what it needs. Upstream command (e.g., `cat bigfile`) gets SIGPIPE when trying to write to the closed pipe.

**Diagnostic Command:**

```bash
# Check exit code
echo $?      # 141 = SIGPIPE (128+13)
# This is NORMAL for head, yes, less, etc.
```

**Fix:**

```bash
# Ignore SIGPIPE in scripts where it's expected:
trap '' PIPE
cat bigfile | head -1
# Or: check for SIGPIPE exit code explicitly
```

**Prevention:**
SIGPIPE is normal for pipelines involving `head`/`tail`/`yes`. For strict scripts, handle exit code 141 as non-fatal.

---

**Pipe Buffer Deadlock**

**Symptom:**
A script that both writes to and reads from the same pipe hangs forever.

**Root Cause:**
Parent process writes to pipe while waiting to read from same pipe. Pipe buffer fills (64KB); write blocks. Parent is blocked on write and never reaches the read. Deadlock.

**Diagnostic Command:**

```bash
strace -p <PID>  # shows process blocked in write() syscall
# In another terminal: lsof -p <PID> | grep pipe
```

**Fix:**
Ensure reading and writing happen in separate processes (fork); never have one process both produce and consume the same pipe without a fork.

**Prevention:**
Use `tee` and process substitution instead of manually managing pipe FDs.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `stdin / stdout / stderr` — pipes and redirection are mechanisms for connecting these streams
- `Shell (bash, zsh)` — the shell creates pipes and redirections between commands

**Builds On This (learn these next):**

- `Shell Scripting` — scripts use pipes and redirection as their primary data flow mechanism
- `grep / awk / sed` — the most common tools in Unix pipelines
- `find / xargs` — file discovery and batch operations via pipes

**Alternatives / Comparisons:**

- `Named Pipes (FIFOs)` — persistent pipes with filesystem paths for unrelated processes
- `Socket Pairs` — bidirectional pipes for IPC and network communication

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ | connects stdout→stdin between programs; │
│              │ >, <, 2> connect programs to files        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Programs needed to compose without        │
│ SOLVES       │ intermediate disk writes                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pipeline programs run concurrently;       │
│              │ pipe buffer provides backpressure         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Chaining Unix tools for text processing,  │
│              │ log analysis, data transformation         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data has complex structure → use Python   │
│              │ or a real streaming framework             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Speed (in-memory, concurrent) vs.         │
│              │ debugging difficulty, no fault tolerance  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pipes are the original stream processor: │
│              │  concurrent, in-memory, composable"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ grep / awk / sed → find / xargs →        │
│              │ Shell Scripting                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You run `cat /dev/urandom | head -c 1M | base64 > encoded.txt`. There are three programs in this pipeline, all running concurrently. `cat /dev/urandom` can generate data indefinitely. `head -c 1M` stops after reading 1MB. Trace what happens to `cat /dev/urandom` after `head` has consumed 1MB and closes its stdin — which signal is sent, from where, to whom — and why this design (SIGPIPE) is more efficient than having `cat` poll whether the downstream consumer has finished.

**Q2.** A production deployment script uses: `build_artifacts | upload_to_s3 | notify_slack`. The `upload_to_s3` step fails halfway through (S3 returns an error, exit code 1). Without `set -o pipefail`, what do the shell and `notify_slack` see? With `pipefail` enabled, what happens differently? Now consider: `upload_to_s3` had already uploaded 50% of the artifacts before failing — how does this reveal the fundamental limitation of pipe-based orchestration compared to a transactional deployment system?
