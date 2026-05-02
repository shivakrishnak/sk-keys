---
layout: default
title: "Shell Scripting"
parent: "Linux"
nav_order: 130
permalink: /linux/shell-scripting/
number: "0130"
category: Linux
difficulty: ★★☆
depends_on: Shell (bash, zsh), Pipes and Redirection, stdin / stdout / stderr
used_by: CI/CD, Cron Jobs, Systemd / Init System, Linux Security Hardening
related: Shell (bash, zsh), grep / awk / sed, find / xargs
tags:
  - linux
  - os
  - intermediate
  - production
---

# 130 — Shell Scripting

⚡ TL;DR — Shell scripting turns sequences of shell commands into reusable, automated programs — replacing manual repetition with reliable, version-controlled automation.

| #130            | Category: Linux                                                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Shell (bash, zsh), Pipes and Redirection, stdin / stdout / stderr |                 |
| **Used by:**    | CI/CD, Cron Jobs, Systemd / Init System                           |                 |
| **Related:**    | Shell (bash, zsh), grep / awk / sed, find / xargs                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A deployment process involves 15 steps: stop the service, back up the database, pull the new artifact, update config, restart the service, verify health. Without scripting, a human performs each step manually, typing commands at a terminal. On the third deployment this month, the engineer forgets step 7 (update config). The service starts with old config, silently breaks, and the team spends three hours debugging. The deployment takes 45 minutes; the engineer is the bottleneck.

**THE BREAKING POINT:**
Human execution of multi-step processes has two fatal flaws: it is slow, and it is inconsistent. Step order mistakes, typos, and forgotten steps cause hard-to-reproduce failures. Worse: the process lives in the engineer's head, not in version control. When that engineer leaves, the knowledge leaves too.

**THE INVENTION MOMENT:**
Shell scripting converts the human procedure into a machine-executable text file. It runs the same steps in the same order, every time, without forgetting. The file can be reviewed, tested, and committed to Git. This is exactly why shell scripting was invented: to encode operational knowledge as executable, repeatable automation.

---

### 📘 Textbook Definition

A **shell script** is an executable text file containing a sequence of shell commands, control flow statements, and variable assignments, interpreted line-by-line by a shell (typically bash). The first line — the **shebang** (`#!/bin/bash`) — specifies the interpreter. Shell scripts provide: conditional logic (`if`/`elif`/`else`), loops (`for`, `while`, `until`), functions, variables, command substitution, and process control. They have access to the full Unix tool ecosystem via pipes and redirection. Shell scripts are the primary mechanism for system administration automation, CI/CD pipelines, and operational tooling on Linux systems.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A shell script is a text file full of commands that the shell executes one by one, just as if you had typed them yourself.

**One analogy:**

> A shell script is a recipe card. Instead of a chef memorising 20 steps and improvising, the recipe card lists exactly what to do, in order, every time. The recipe is reproducible: anyone following it gets the same dish. You can hand the card to anyone — or leave it in the recipe book for next year.

**One insight:**
The power of shell scripts is not in the language itself — bash is a weak programming language. The power is in access to the entire Unix tool ecosystem. `sort`, `grep`, `awk`, `curl`, `jq`, `find` are all programs the script can invoke. The script is the conductor; Unix tools are the orchestra.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A script is a batch of shell commands with a stored execution context.
2. `#!/bin/bash` line tells the kernel which interpreter to exec.
3. Exit codes (`0` = success, non-zero = failure) are the script's communication protocol.

**DERIVED DESIGN:**

```bash
#!/bin/bash
# Shebang: kernel reads this, execs /bin/bash with script as arg

# set -e: exit immediately on error (critical for safety)
# set -u: treat unset variables as errors
# set -o pipefail: fail if any pipe stage fails
set -euo pipefail

# Variables
APP_DIR="/opt/myapp"
BACKUP_DIR="/var/backup/myapp"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function definition
backup_app() {
    local src="$1"    # local: scoped to function
    local dest="$2"
    echo "Backing up $src to $dest"
    tar -czf "${dest}/backup_${TIMESTAMP}.tar.gz" "$src"
}

# Conditional
if [[ ! -d "$APP_DIR" ]]; then
    echo "ERROR: App dir $APP_DIR not found" >&2
    exit 1   # non-zero exit = failure
fi

# Function call
backup_app "$APP_DIR" "$BACKUP_DIR"

echo "Done. Exit code: $?"  # $? = exit code of last command
```

**CONTROL FLOW:**

```
if/elif/else:                   for loop:
  if [[ condition ]]; then        for file in *.log; do
    cmd                             process "$file"
  elif [[ other ]]; then          done
    cmd
  else                          while loop:
    cmd                           while read -r line; do
  fi                                process "$line"
                                  done < input.txt

case/esac:
  case "$VAR" in
    "start") start_service ;;
    "stop")  stop_service  ;;
    *)       echo "Unknown" ;;
  esac
```

**THE TRADE-OFFS:**
**Gain:** Zero dependencies (bash is available on every Linux system), fast to write, full Unix tool access.
**Cost:** Subtle bugs with quoting and whitespace; poor for complex data structures; no type safety; difficult to unit test; slow for large data (each command is a process fork).

---

### 🧪 Thought Experiment

**SETUP:**
Your team deploys a web service 10 times per week. The deployment has 12 steps. Three engineers rotate on-call deployment duty.

**WHAT HAPPENS WITHOUT SCRIPTING:**
Each engineer follows a shared document. Engineer A interprets step 6 differently than Engineer B. On Friday evening, Engineer C is tired and skips step 9 (verifying DB migration). The new code runs against an unmigrated schema. Data corruption. 4-hour incident.

**WHAT HAPPENS WITH SCRIPTING:**

```bash
#!/bin/bash
set -euo pipefail

./scripts/stop_service.sh
./scripts/backup_db.sh
./scripts/deploy_artifact.sh "$VERSION"
./scripts/run_migrations.sh
./scripts/update_config.sh "$ENV"
./scripts/start_service.sh
./scripts/verify_health.sh

echo "Deployment $VERSION to $ENV: SUCCESS"
```

Step 9 (`run_migrations`) cannot be skipped. If it fails, `set -e` aborts the script. Every engineer's deployment is identical. The script is in Git — diffs show every change. The incident doesn't happen.

**THE INSIGHT:**
Scripts encode process as code. When the process changes, you update the script and commit. The diff is the audit trail. The test is the next deployment.

---

### 🧠 Mental Model / Analogy

> A shell script is a macro recorder for your terminal. Every command you type and every result you expect is recorded into the macro. When you press "play," the macro runs every step in sequence, stopping if anything fails. The macro is a file you can share with teammates and commit to Git.

- "Recording the macro" → writing the script
- "Playing the macro" → executing `./deploy.sh`
- "The macro stopping on error" → `set -e` + non-zero exit code
- "Macro stored on disk" → script file in version control

**Where this analogy breaks down:** Unlike a recorded macro (which is a fixed replay), shell scripts have real logic — conditions, loops, functions, dynamic values. They are genuine programs, not just playbacks.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A shell script is a text file containing commands you would otherwise type manually, so the computer can run them automatically without you being there.

**Level 2 — How to use it (junior developer):**
Create a file `deploy.sh`, add `#!/bin/bash` as the first line, then your commands. Make it executable with `chmod +x deploy.sh`, run it with `./deploy.sh`. Use variables (`NAME=value`), conditionals (`if [[ ... ]]; then`), and always add `set -euo pipefail` at the top to catch errors. Use `"$VAR"` (quoted) to avoid word-splitting bugs.

**Level 3 — How it works (mid-level engineer):**
The kernel sees the shebang, and runs the equivalent of `exec /bin/bash deploy.sh`. Bash reads the file line by line, performing expansion (variable, glob, command substitution) and executing each command. `set -e` is implemented as: after every simple command, check `$?`; if non-zero, call `exit $?`. Functions create a new scope for `local` variables but share the global scope otherwise. `source script.sh` (or `. script.sh`) runs the script in the CURRENT shell process — no fork; changes to variables and cwd are visible in the calling shell.

**Level 4 — Why it was designed this way (senior/staff):**
Bash's design prioritises backward compatibility above all else. The quoting model, word-splitting, and globbing were designed in 1979 for the Bourne shell and have remained backward-compatible for 45 years — at the cost of a counterintuitive syntax full of edge cases. ShellCheck (static analysis) catches the most dangerous patterns. For complex automation, modern practice moves to Python (better data structures, error handling, testing) or purpose-built tools (Ansible, Terraform). Shell scripts remain the lingua franca for one-off glue, CI/CD steps, and system initialization — their ubiquity is their advantage.

---

### ⚙️ How It Works (Mechanism)

**Script execution flow:**

```
┌──────────────────────────────────────────────────────┐
│         SCRIPT EXECUTION LIFECYCLE                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. ./deploy.sh called                              │
│     Kernel reads first 2 bytes: #!                  │
│     Extracts interpreter: /bin/bash                 │
│     Exec: /bin/bash ./deploy.sh                     │
│                                                      │
│  2. Bash initialises:                               │
│     - Non-interactive: sources $BASH_ENV if set     │
│     - NOT ~/.bashrc (non-interactive!)               │
│                                                      │
│  3. Bash reads script line by line                  │
│     For each line:                                  │
│     a. Skip comments (#)                            │
│     b. Handle set -e/-u/-o pipefail flags           │
│     c. Expand variables, globs, command subst       │
│     d. Fork + exec external commands                │
│     e. Check exit code → abort if set -e + non-zero │
│                                                      │
│  4. Script exits with exit code of last command     │
│     (or explicit exit N)                            │
└──────────────────────────────────────────────────────┘
```

**Exit code conventions:**

```bash
exit 0     # success
exit 1     # general error
exit 2     # misuse of shell builtins
exit 126   # command found but not executable
exit 127   # command not found
exit 128+N # signal N killed the script (e.g., 130 = SIGINT)

# Check last command's exit code:
if command; then
    echo "success"
else
    echo "failed with code $?"
fi
```

**Passing and returning values:**

```bash
# Functions can't return values — only exit codes (0-255)
# Use stdout to "return" data from functions:

get_version() {
    cat /etc/myapp/version.txt  # prints to stdout
}

VERSION=$(get_version)  # capture stdout into variable
echo "Version: $VERSION"

# Passing multiple return values via global vars (anti-pattern)
# or via output to temp file
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
CI/CD pipeline triggers deploy.sh
    ↓
Jenkins/GitHub Actions runs: bash deploy.sh prod v2.3.1
    ↓
Script validates args, checks environment
    ↓
Script stops service, backs up, deploys artifact
    ← YOU ARE HERE (script orchestrates the steps)
    ↓
Script runs migrations, updates config, starts service
    ↓
Script runs health check: curl http://localhost/health
    ↓
Curl returns 200 → script exits 0 → CI marks success
```

**FAILURE PATH:**

```
Migration step fails (exit code 1)
    ↓
set -e triggers: script exits immediately
    ↓
Service is still stopped (rollback NOT automatic)
    ↓
CI marks job failed, alerts on-call
    ↓
Observable: script exits mid-run, service is down
Prevention: explicitly write rollback logic on failure
```

**WHAT CHANGES AT SCALE:**
At high deployment frequency, shell scripts hit limits: no unit testing framework, subtle race conditions when scripts run in parallel, no structured error reporting. Teams migrate to Ansible (idempotent, parallel, structured) or custom Python automation. CI/CD platforms (GitHub Actions, Tekton) replace ad-hoc scripts with composable, testable workflows. Shell scripts survive as the atomic unit within these larger systems.

---

### 💻 Code Example

**Example 1 — Safe script template (always start with this):**

```bash
#!/bin/bash
# Script: deploy.sh
# Usage: ./deploy.sh <environment> <version>

set -euo pipefail  # exit on error, unset vars, pipe fails

# Script directory (reliable regardless of where you call from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Constants
LOG_FILE="/var/log/deploy.log"

# Logging function
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
die() { log "ERROR: $*" >&2; exit 1; }

# Argument validation
[[ $# -ne 2 ]] && die "Usage: $0 <env> <version>"
ENV="$1"
VERSION="$2"

[[ "$ENV" =~ ^(dev|staging|prod)$ ]] || die "Invalid env: $ENV"

log "Starting deployment of $VERSION to $ENV"
```

**Example 2 — Loops and conditionals:**

```bash
#!/bin/bash
set -euo pipefail

# Process all .log files older than 7 days
ARCHIVE_DIR="/var/archive"
mkdir -p "$ARCHIVE_DIR"

while IFS= read -r -d '' file; do
    filename=$(basename "$file")
    log "Archiving: $filename"
    gzip -c "$file" > "${ARCHIVE_DIR}/${filename}.gz" \
      && rm "$file"
done < <(find /var/log/app -name "*.log" -mtime +7 -print0)
# -print0 and read -d '' handle filenames with spaces safely
```

**Example 3 — Error handling and cleanup:**

```bash
#!/bin/bash
set -euo pipefail

TMPDIR=$(mktemp -d)  # create temp dir

# ALWAYS clean up, even on error
cleanup() {
    local exit_code=$?
    rm -rf "$TMPDIR"
    if [[ $exit_code -ne 0 ]]; then
        echo "Script failed with code $exit_code" >&2
        # Optional: send alert, rollback, etc.
    fi
    exit $exit_code
}
trap cleanup EXIT   # run cleanup on any exit

# Do work in temp dir
cd "$TMPDIR"
curl -sS -o artifact.tar.gz "https://releases.myapp.com/$VERSION"
tar -xzf artifact.tar.gz
./install.sh

# cleanup runs automatically here
```

**Example 4 — Parallel execution with wait:**

```bash
#!/bin/bash
set -euo pipefail

# Run multiple tasks in parallel
run_checks() {
    local host="$1"
    ssh "$host" "systemctl status myapp" \
      && echo "✓ $host: healthy" \
      || echo "✗ $host: FAILED"
}

# Launch in parallel, capture PIDs
pids=()
for host in web01 web02 web03; do
    run_checks "$host" &   # & = background
    pids+=($!)             # $! = PID of last bg process
done

# Wait for all to complete, check any failures
failed=0
for pid in "${pids[@]}"; do
    wait "$pid" || failed=1
done

[[ $failed -eq 0 ]] || { echo "Some checks failed"; exit 1; }
echo "All hosts healthy"
```

---

### ⚖️ Comparison Table

| Tool             | Language      | Idempotency  | Parallelism       | Best For                       |
| ---------------- | ------------- | ------------ | ----------------- | ------------------------------ |
| **Shell script** | Bash          | Manual       | Manual (& + wait) | Glue code, simple automation   |
| Ansible          | YAML + Python | Built-in     | Yes (forks)       | Config management, multi-host  |
| Python script    | Python        | Manual       | Via threads/async | Complex logic, data processing |
| Makefile         | Make DSL      | Target-based | Yes (-j flag)     | Build automation, task runners |
| GitHub Actions   | YAML + shell  | Per-run      | Matrix builds     | CI/CD pipelines                |

**How to choose:** Shell scripts for single-server operations up to ~100 lines. Python when you need data structures, proper error handling, or unit tests. Ansible for multi-host config management and idempotent state enforcement.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | --- | --------------------------------------------------------- |
| `set -e` catches all errors                      | `set -e` doesn't trigger in subshells, inside `if` conditions, in `&&` / `                                             |     | ` chains, or in functions called as part of a conditional |
| Variables are local by default                   | Variables are global unless explicitly declared `local` inside a function                                              |
| `[ ]` and `[[ ]]` are interchangeable            | `[[ ]]` is bash-specific but safer (no word splitting, supports `&&`/`\|\|`); use `[[ ]]` in bash scripts              |
| You can `return` a string from a function        | Functions can only return exit codes (0-255); use command substitution `$(func)` to capture stdout as a "return value" |
| Quoting variables is optional                    | `rm $DIR` where `DIR="/my folder"` runs `rm /my folder` (two args); always quote: `rm "$DIR"`                          |
| `exit` in a sourced script exits the script only | `exit` in a sourced (`.` or `source`) script exits the CALLING shell, not just the sourced file                        |

---

### 🚨 Failure Modes & Diagnosis

**Silent Failure Due to Missing `set -e`**

**Symptom:**
Deployment script appears to succeed; service fails in production. Investigation reveals a critical step returned exit code 1 but the script continued.

**Root Cause:**
Script missing `set -e`; a command fails silently; subsequent steps run against a broken state.

**Diagnostic Command:**

```bash
# Run script in debug/trace mode
bash -x ./deploy.sh 2>&1 | tee /tmp/deploy_trace.log
# -x prints each command and its expanded args before execution
```

**Fix:**

```bash
# Add at the top of every script:
set -euo pipefail
```

**Prevention:**
Lint scripts with ShellCheck (`shellcheck deploy.sh`); enforce in CI.

---

**Unquoted Variable Causes Data Loss**

**Symptom:**
Script deletes wrong files; `rm $LOG_DIR/*.log` with `LOG_DIR=""` becomes `rm /*.log`.

**Root Cause:**
Empty or unset variable; shell expands to unintended path.

**Diagnostic Command:**

```bash
# Test expansion before running:
echo "Would delete: ${LOG_DIR}/*.log"
# With set -u, unset variable causes immediate error
```

**Fix:**

```bash
# Use :? operator to fail on unset:
rm "${LOG_DIR:?LOG_DIR is not set}"/*.log
```

**Prevention:**
`set -u` + always quote variables + ShellCheck.

---

**Script Works on Dev, Fails in CI (Missing Tool)**

**Symptom:**
Script calls `jq` or `yq`; works on engineer's Mac; fails in CI container with "command not found."

**Root Cause:**
Tool is installed locally but not in the CI container image.

**Diagnostic Command:**

```bash
# Check all external commands used in the script:
grep -oE '[a-z][a-z0-9_-]+' script.sh | \
  sort -u | xargs -I{} which {} 2>/dev/null
```

**Fix:**
Add tool to Dockerfile or CI configuration; use `command -v jq || apt-get install -y jq` as a dependency check.

**Prevention:**
Define all tool dependencies in a `requirements.sh` or install script; test scripts in the same Docker image used by CI.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Shell (bash, zsh)` — scripting is writing programs in the shell language
- `Pipes and Redirection` — the primary composition mechanism in shell scripts
- `stdin / stdout / stderr` — how scripts communicate with callers and tools

**Builds On This (learn these next):**

- `grep / awk / sed` — text processing tools most scripts depend on
- `find / xargs` — file discovery and batch operations
- `Cron Jobs` — scheduling scripts to run automatically
- `CI/CD` — shell scripts are the execution primitive in most pipelines

**Alternatives / Comparisons:**

- `Python scripting` — better for complex logic, data structures, and unit-testable automation
- `Ansible` — idempotent config management; replaces shell scripts for multi-host operations
- `Makefile` — target-based task runner with dependency tracking

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Executable text file of shell commands    │
│              │ with control flow and variables           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Manual repetition is slow, inconsistent, │
│ SOLVES       │ and not in version control                │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "set -euo pipefail" turns bash from       │
│              │ silent-failure mode to fail-fast safety   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automating system tasks, glue between     │
│              │ tools, CI/CD steps up to ~100 lines       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex data processing, many conditionals│
│              │ unit-testable logic → use Python          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Ubiquity + simplicity vs. fragility +     │
│              │ weak typing + hard to test                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Scripts are the memory of your           │
│              │  operational knowledge — commit them"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ grep / awk / sed → find / xargs →        │
│              │ Cron Jobs                                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A shell script contains: `FILES=$(find /var/log -name "*.log")` followed by `for f in $FILES; do process "$f"; done`. The script works perfectly on a test machine where all log filenames are simple words. On production, one log file is named `access 2024.log` (with a space). Trace exactly what happens when bash expands `$FILES` in the `for` loop, why the space causes the loop to process three items instead of two, and rewrite the loop correctly using the `find ... -print0 | while read -r -d ''` pattern — explaining what each flag does.

**Q2.** A deployment script runs two services in parallel using `&`, collects their PIDs, and uses `wait` to join them. Service A takes 30 seconds and succeeds. Service B takes 5 seconds and fails with exit code 1. The `wait` loop checks each PID's exit code. If `set -e` is active, does the script exit when Service B fails at the 5-second mark, or does it wait for Service A to complete first? Explain the interaction between background processes, `wait`, and `set -e` — and describe how `trap ERR` changes the behaviour.
