---
layout: default
title: "Environment Variables"
parent: "Linux"
nav_order: 136
permalink: /linux/environment-variables/
number: "0136"
category: Linux
difficulty: ★☆☆
depends_on: Shell (bash, zsh), Linux File System Hierarchy, Users and Groups
used_by: Shell Scripting, Docker, CI/CD, Systemd, Node.js
related: Shell (bash, zsh), Shell Scripting, Process Management
tags:
  - linux
  - os
  - internals
  - foundational
---

# 136 — Environment Variables

⚡ TL;DR — Environment variables are named key-value strings every process inherits from its parent, used to configure software without hardcoding values.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine deploying the same application to development, staging, and production. Without environment variables you would hardcode database hostnames, API keys, and log levels directly into source code. Every environment change requires a code edit, a recompile, and a redeployment. Worse, your API keys are now in version control for every developer — and every attacker — to see.

**THE BREAKING POINT:**
A developer accidentally commits the production database password to GitHub. The incident response team spends hours rotating credentials and scanning repos. Meanwhile the CI pipeline fails because no one updated the hardcoded staging URL after a server migration.

**THE INVENTION MOMENT:**
This is exactly why Environment Variables were created. They separate configuration from code — letting the same binary run anywhere by reading its context from the surrounding process environment, not from compiled-in constants.

---

### 📘 Textbook Definition

An environment variable is a named string stored in a process's environment block — a key-value table inherited by every child process created via `fork()` + `exec()`. The kernel initialises this block from the parent's environment at process creation. Variables persist for the lifetime of the process and can be read, set, or unset by the process itself or any child it spawns.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Named configuration values that every process carries and passes to its children.

**One analogy:**

> Think of environment variables as sticky notes attached to an office worker. Before starting a task, they check their notes: "use server B today", "speak in French". Their assistant inherits copies of those notes automatically when they begin sub-tasks.

**One insight:**
Every process has its own copy of the environment — changes inside a child never propagate back to the parent. This is why `export VAR=value` in a subshell has no effect on the calling shell.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every process has an independent copy of the environment block.
2. Children inherit environment at `exec()` time — not continuously.
3. Keys are case-sensitive strings; values are always strings (no types).

**DERIVED DESIGN:**
At `fork()`, the kernel copies the parent's address space including the environment pointer array (`char **envp`). At `exec()`, the new program receives this array as its third argument alongside `argc`/`argv`. Because it is a copy, `setenv()` inside the child only modifies that copy — the parent's environment is untouched.

Shell builtins like `export` mark a variable for inclusion in child environments. Without `export`, a variable exists only in the shell's local scope and is never copied to children.

**THE TRADE-OFFS:**
**Gain:** Zero-cost configuration injection with no IPC required — the OS delivers config automatically at process birth.
**Cost:** Strings only (no structured types), child cannot communicate back to parent, and sensitive values (passwords) are visible to any process with the same UID via `/proc/<pid>/environ`.

---

### 🧪 Thought Experiment

**SETUP:**
You write a Node.js server that connects to a database. You want it to work on your laptop (`localhost:5432`) and on production (`db.prod.internal:5432`) without changing code.

**WHAT HAPPENS WITHOUT Environment Variables:**
You hardcode `localhost:5432`. The server works locally. You push to production — the server crashes on startup: "connection refused". You edit the source, rebuild the Docker image, push again. Two hours later you realise you also hardcoded the password. You repeat the cycle, this time with an accidental secret in git history.

**WHAT HAPPENS WITH Environment Variables:**

```js
const db = process.env.DATABASE_URL;
```

On your laptop: `DATABASE_URL=postgresql://localhost:5432/dev node server.js`
On production: the orchestrator injects `DATABASE_URL=postgresql://db.prod.internal:5432/prod`. Same binary, correct behaviour in both environments.

**THE INSIGHT:**
Environment variables cleanly separate the concern of _what to run_ from _how to configure it_ — the executable becomes a generic template that the environment instantiates.

---

### 🧠 Mental Model / Analogy

> Environment variables are like a traveller's passport. Before leaving home (forking), the traveller gets a passport (environment copy). The passport says their nationality (configuration). Officials in each country (child processes) read the passport. The traveller can update their own passport (setenv in child) but that doesn't change the original at the passport office (parent process).

- "Passport office" → parent process environment
- "Getting a copy at border" → `fork()` + environment inheritance
- "Stamps added abroad" → `setenv()` inside child
- "Original passport unchanged" → parent environment unaffected

Where this analogy breaks down: a real passport can be renewed and the original updated — but an environment change in a child can never propagate back to the parent at all.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Environment variables are named settings that every program reads when it starts. They are like a configuration file but delivered automatically by the operating system. Set `DATABASE_URL` once and every program that reads it uses the right database.

**Level 2 — How to use it (junior developer):**
In bash: `export PORT=3000` makes `PORT` available to all programs launched from that shell session. Read in code with `process.env.PORT` (Node.js) or `os.getenv("PORT")` (Python). Persist across reboots by adding `export PORT=3000` to `~/.bashrc` or `/etc/environment`. Never hardcode secrets — inject them via environment.

**Level 3 — How it works (mid-level engineer):**
The shell maintains two tables: local variables (shell-only) and exported variables (inherited by children). `export` moves a variable from local to exported. At `execve()`, the kernel passes the exported table as `envp[]` — a null-terminated array of `KEY=VALUE` strings. The libc function `getenv()` scans this array linearly. Programs can also read `/proc/self/environ` directly; values are NUL-separated in that file.

**Level 4 — Why it was designed this way (senior/staff):**
The `execve()` signature (`argv`, `envp`) was designed in Unix V7 (1979). Passing config as strings was the simplest possible mechanism that required no new kernel primitives. The copy-on-exec model avoids shared state between parent and child — critical for security isolation. The downside is the O(n) linear scan in `getenv()`, but environment blocks are small (typically < 4 KB, hard-limited by `ARG_MAX`). Modern alternatives like config files or secrets managers exist precisely because env vars have no type safety, no access control per variable, and expose sensitive data in `/proc`.

---

### ⚙️ How It Works (Mechanism)

**1. Shell variable creation:**

```bash
MYVAR="hello"       # local only — not exported
export MYVAR        # now exported — children inherit it
export NEWVAR="hi"  # shorthand — create + export in one step
```

**2. Inheritance at fork/exec:**

```
Parent Shell
  envp[]: [PATH=..., HOME=..., MYVAR=hello, ...]
       │
       │ fork() — copy of envp[]
       ▼
  Child Process (e.g., node server.js)
       │  reads process.env.MYVAR → "hello"
       │  setenv("MYVAR", "changed") — only in THIS process
       ▼
  Grandchild (if exec'd from child)
       │  inherits MYVAR="changed"
```

**3. Reading from code:**

```python
import os
# Returns None if not set — never crash on missing var
db_url = os.getenv("DATABASE_URL", "postgresql://localhost/dev")
```

**4. Scope rules:**

- `VAR=x command` — sets `VAR` only for that single command
- `export VAR=x` — persists for entire shell session
- `unset VAR` — removes from environment
- `env` — lists all exported variables

**5. Special variables:**
| Variable | Purpose |
|---|---|
| `PATH` | Directories searched for executables |
| `HOME` | Current user's home directory |
| `USER` | Current username |
| `SHELL` | Path to user's login shell |
| `LANG` | Locale and character encoding |
| `TERM` | Terminal type for ncurses apps |
| `PS1` | Shell prompt format |

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  ENV VARIABLE LIFECYCLE                     │
└─────────────────────────────────────────────┘

 System boot (/etc/environment loaded by PAM)
       │
       ▼
 Login shell started (reads ~/.bashrc)
       │  export DATABASE_URL=postgresql://...
       ▼
 Developer runs: node server.js   ← YOU ARE HERE
       │  execve() passes envp[]
       ▼
 Node.js process reads process.env.DATABASE_URL
       │
       ▼
 Database connection established
```

**FAILURE PATH:**
`DATABASE_URL` not set → `process.env.DATABASE_URL` is `undefined` → `TypeError: cannot read property 'split' of undefined` → server crashes on startup, not at connection time.

**WHAT CHANGES AT SCALE:**
In containers (Docker/Kubernetes), env vars are injected by the orchestrator — developers never set them on hosts. Kubernetes Secrets project sensitive values from etcd into pod env at scheduling time. At scale the risk is env var sprawl: hundreds of variables with no documentation or ownership, breaking when silently removed.

---

### 💻 Code Example

**Example 1 — BAD: hardcoded configuration:**

```python
# BAD — hardcoded, env-specific, secret in source
conn = psycopg2.connect(
    "postgresql://admin:password123@db.prod/myapp"
)
```

**Example 1 — GOOD: environment-driven configuration:**

```python
import os

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError(
        "DATABASE_URL environment variable is required"
    )
conn = psycopg2.connect(db_url)
```

**Example 2 — Per-command override:**

```bash
# Temporarily override for one command only
DATABASE_URL=postgresql://localhost/test pytest tests/

# Verify what a program will see before running it
env DATABASE_URL=test python -c "import os; print(os.environ)"
```

**Example 3 — .env file pattern (development only):**

```bash
# .env file (NEVER commit to git)
DATABASE_URL=postgresql://localhost:5432/dev
API_KEY=dev-key-12345
DEBUG=true

# Load it in bash
set -a; source .env; set +a
node server.js
```

```bash
# .gitignore — ALWAYS include
.env
.env.local
*.env
```

---

### ⚖️ Comparison Table

| Method               | Type Safety    | Secret Safety       | Scope              | Best For                     |
| -------------------- | -------------- | ------------------- | ------------------ | ---------------------------- |
| **Environment Vars** | None (strings) | Medium              | Process + children | Config injection, containers |
| Config files         | Structured     | Medium              | File-level         | Complex structured config    |
| Secrets manager      | Typed          | High                | Explicit fetch     | Production secrets           |
| Command-line args    | None           | Low (visible in ps) | Process only       | One-time overrides           |
| Hard-coded           | N/A            | None                | Compiled in        | Never — except defaults      |

How to choose: use environment variables for deployment config (URLs, ports, feature flags) and use a secrets manager (Vault, AWS Secrets Manager) for credentials — then inject the fetched secret into environment at startup.

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Setting an env var in a child script affects the parent shell | It never does — each process has its own copy; `source script.sh` is the only way to affect the current shell          |
| Environment variables are secure for secrets                  | Any process with same UID can read them via `/proc/<pid>/environ`; use secrets managers for production credentials     |
| `export VAR=x` in ~/.bashrc persists system-wide              | It only applies to interactive shells started by that user; system services read from `/etc/environment` or unit files |
| Env vars survive reboot automatically                         | They only persist if declared in startup files (`.bashrc`, `/etc/environment`, systemd unit files)                     |
| All processes share the same environment                      | Each process has an independent copy; changes in one process never affect siblings                                     |

---

### 🚨 Failure Modes & Diagnosis

**Missing Required Variable**

**Symptom:**
Application crashes on startup with `NullPointerException`, `KeyError`, or `TypeError` referencing a config value.

**Root Cause:**
Code calls `os.getenv("VAR")` and gets `None`, then passes it to a function expecting a string.

**Diagnostic Command:**

```bash
# Print all env vars for a running process
cat /proc/<pid>/environ | tr '\0' '\n' | grep VAR
# Or check before launch
env | grep DATABASE
```

**Fix:**

```python
# BAD — crash on missing
url = os.getenv("DATABASE_URL").split("@")[1]

# GOOD — fail fast with clear message
url = os.getenv("DATABASE_URL")
if not url:
    raise EnvironmentError(
        "DATABASE_URL must be set. "
        "Example: postgresql://user:pass@host/db"
    )
```

**Prevention:**
Validate all required environment variables at application startup before any work begins.

---

**Secret Leakage via Logging**

**Symptom:**
Sensitive credentials appear in application logs, error traces, or monitoring dashboards.

**Root Cause:**
Code logs the full environment or concatenates secret variables into error messages.

**Diagnostic Command:**

```bash
# Audit logs for common secret patterns
grep -r "password\|secret\|key" /var/log/app/ \
  --include="*.log" | head -20
```

**Fix:**

```python
# BAD — logs all environment including secrets
logger.info(f"Starting with config: {os.environ}")

# GOOD — log only safe keys
SAFE_KEYS = {"DATABASE_HOST", "PORT", "DEBUG"}
safe_config = {
    k: v for k, v in os.environ.items()
    if k in SAFE_KEYS
}
logger.info(f"Starting with config: {safe_config}")
```

**Prevention:**
Never log `os.environ` or full config objects; allowlist the keys safe to log.

---

**Variable Not Exported (Child Doesn't See It)**

**Symptom:**
A script sets a variable but the program it launches can't find it.

**Root Cause:**
Variable was set without `export` — it exists in the shell's local scope only.

**Diagnostic Command:**

```bash
# Show only exported (child-visible) variables
export -p | grep MYVAR
# Or use printenv (only shows exported vars)
printenv MYVAR
```

**Fix:**

```bash
# BAD — local only
MYVAR=hello
node app.js   # process.env.MYVAR is undefined

# GOOD — exported
export MYVAR=hello
node app.js   # process.env.MYVAR === "hello"
```

**Prevention:**
Use `export` for any variable intended to be read by child processes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Shell (bash, zsh)` — env vars are managed and inherited through the shell's fork/exec model
- `Users and Groups` — env vars are scoped to processes running under a UID
- `Process Management` — understanding process trees explains why env changes don't propagate upward

**Builds On This (learn these next):**

- `Shell Scripting` — scripts manipulate env vars extensively for portability
- `Docker` — containers use env vars as the primary configuration injection mechanism
- `Systemd` — unit files expose `Environment=` and `EnvironmentFile=` directives

**Alternatives / Comparisons:**

- `Configuration Files` — structured typed config, better for complex hierarchical settings
- `Command-line Arguments` — per-invocation overrides, visible in `ps` output (avoid for secrets)
- `Secrets Managers (Vault, AWS SSM)` — proper solution for credentials in production

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Named key=value strings every process     │
│              │ inherits from its parent at exec() time   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Config hardcoded in source forced         │
│ SOLVES       │ recompile for every environment change    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Child gets a COPY — changes never         │
│              │ propagate back to parent                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Injecting env-specific config into        │
│              │ containers, CI/CD pipelines, services     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Storing structured/typed config or        │
│              │ production secrets (use secrets mgr)      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero-cost injection vs strings-only,      │
│              │ no type safety, visible in /proc          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Config that travels with the process,    │
│              │  not baked into the binary"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Shell Scripting → Docker → Secrets Mgr   │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A containerised microservice reads its database URL from `DATABASE_URL` at startup and caches the connection. The Kubernetes operator rotates the secret and updates the environment variable in the pod spec. The pod is NOT restarted. What does the running process see, and what must the operator do to make the rotation effective? Trace the full sequence of events.

**Q2.** Two processes owned by the same user run simultaneously. Process A stores a session token in an environment variable. Process B is a malicious script launched by the same user. What does B need to do to read A's session token, and what kernel or OS mechanism — if any — prevents this? How does this change if A and B are containers on the same host?
