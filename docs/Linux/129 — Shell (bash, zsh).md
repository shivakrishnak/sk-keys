---
layout: default
title: "Shell (bash, zsh)"
parent: "Linux"
nav_order: 129
permalink: /linux/shell-bash-zsh/
number: "0129"
category: Linux
difficulty: ★☆☆
depends_on: Linux File System Hierarchy, Users and Groups
used_by: Shell Scripting, SSH, Pipes and Redirection, grep / awk / sed
related: Shell Scripting, Pipes and Redirection, stdin / stdout / stderr
tags:
  - linux
  - os
  - foundational
  - internals
---

# 129 — Shell (bash, zsh)

⚡ TL;DR — A shell is the command-line interpreter that translates your text commands into system calls, giving you interactive and scriptable control over a Linux system.

| #129            | Category: Linux                                                 | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Linux File System Hierarchy, Users and Groups                   |                 |
| **Used by:**    | Shell Scripting, SSH, Pipes and Redirection, grep / awk / sed   |                 |
| **Related:**    | Shell Scripting, Pipes and Redirection, stdin / stdout / stderr |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The Linux kernel is a collection of system calls — functions like `open()`, `fork()`, `execve()`. To run a program without a shell, you would need to write C code, compile it, and invoke `execve()` directly. Every administrative task — listing files, killing a process, copying a config — would require a compiled binary or a direct hardware interface. There would be no interactive way to issue commands to a running system.

**THE BREAKING POINT:**
In the earliest days, operators interacted with computers through punched cards or teletype terminals. The terminal was hardware; what turned keystrokes into program invocations was missing. Without an interactive interpreter, administration required pre-compiled batch jobs — inflexible, slow to iterate, and inaccessible to non-programmers.

**THE INVENTION MOMENT:**
The Unix shell (Thompson shell, 1971; Bourne shell, 1979) was the breakthrough: a program that reads text commands, parses them into program names and arguments, forks a child process, and executes the named program. This is exactly why the shell exists: to bridge human-readable command text and the kernel's binary system call interface.

---

### 📘 Textbook Definition

A **shell** is an interactive command-line interpreter and scripting environment that provides a user interface to the operating system kernel. It parses command-line input into program names, arguments, and I/O redirections; forks child processes via `fork()`; and executes programs via `execve()`. The shell also provides: variable assignment, control flow (if/while/for), pipeline construction (`|`), I/O redirection (`>`, `<`, `2>&1`), job control (`bg`, `fg`), and interactive features (history, tab completion, prompts). **Bash** (Bourne Again Shell, 1989) is the default shell on most Linux distributions. **Zsh** (Z Shell, 1990) is the default on macOS (since Catalina) and offers enhanced interactive features. Both implement the POSIX shell standard.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The shell is the layer between you and the Linux kernel — you type commands, the shell runs programs.

**One analogy:**

> The shell is like a restaurant waiter. You (the human) speak English and say "I'll have the pasta." The waiter (shell) translates that into a kitchen order (syscall) in the format the kitchen (kernel) understands, then brings you the result. Without the waiter, you'd need to walk into the kitchen and talk directly to the chef (kernel) in binary.

**One insight:**
The shell is itself just a program — it has no special kernel privileges. When you type `ls`, the shell calls `fork()` to copy itself, then `execve("/bin/ls", ...)` in the child. `ls` runs as a child process of the shell. The shell then `wait()`s for it to finish. Understanding this explains why `export` affects child processes but not the parent.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The shell is a user-space program — it uses system calls like any other program.
2. Shell command execution = `fork()` + `execve()` + `wait()`.
3. Built-in commands (`cd`, `export`) run IN the shell process; external commands run in a forked child.

**DERIVED DESIGN:**

```
SHELL COMMAND EXECUTION MODEL:

  User types: ls -la /home

  Shell process (PID 1234)
    │
    ├─ Parse: command="ls", args=["-la", "/home"]
    │
    ├─ fork()  ──────────────────────────────────┐
    │                                            │ Child PID 1235
    │                               execve("/bin/ls", ["-la", "/home"])
    │                                            │
    │                               ls runs, writes to stdout
    │                                            │
    ├─ wait(1235)  ◄──────────────────────────── exit(0)
    │
    └─ Shell prints prompt, waits for next command
```

**Why built-ins must run in the shell process:**
`cd /tmp` must change the shell's own working directory. If `cd` ran in a child process, the child's directory change would be invisible to the parent shell. So `cd`, `export`, `source`, `alias`, `exec` are built into the shell — they modify the shell's own state directly.

**Shell startup files (when they run):**

| File              | When sourced                  |
| ----------------- | ----------------------------- |
| `/etc/profile`    | Login shells (all users)      |
| `~/.bash_profile` | Login shells (bash, per-user) |
| `~/.bashrc`       | Interactive non-login shells  |
| `~/.bash_logout`  | On logout from login shell    |
| `~/.zshrc`        | Interactive zsh sessions      |
| `~/.zprofile`     | Login zsh sessions            |

**THE TRADE-OFFS:**
**Gain:** Universally available, no compilation needed, powerful composition via pipes.
**Cost:** Bash scripts have subtle quoting/whitespace traps; performance is poor for data processing at scale (use Python/awk instead). Bash is Turing-complete but not designed for large programs.

---

### 🧪 Thought Experiment

**SETUP:**
You need to perform a task: count how many times the word "ERROR" appears in a log file `/var/log/app.log`.

**WHAT HAPPENS WITHOUT A SHELL:**
You must write a C program: `#include <stdio.h>`, open the file with `fopen()`, read line by line with `fgets()`, use `strstr()` to find "ERROR", increment a counter, print the result, compile with `gcc`, run the binary. 15 minutes of work.

**WHAT HAPPENS WITH A SHELL:**

```bash
grep -c "ERROR" /var/log/app.log
```

One command. Under one second. The shell parses the command, finds `/usr/bin/grep`, forks a child, executes grep with those arguments, grep reads the file and prints the count, the shell waits and returns to the prompt. The entire interaction took 2 seconds including typing.

**THE INSIGHT:**
The shell's power comes from composition: combining small, focused Unix tools (`grep`, `awk`, `sort`, `wc`) with pipes and redirection. Each tool does one thing well. The shell is the glue. This is the Unix philosophy: "Write programs that do one thing and do it well. Write programs to work together."

---

### 🧠 Mental Model / Analogy

> The shell is the REPL (Read-Eval-Print Loop) of the operating system. It reads a command, evaluates it by translating it into system calls, prints the output, and loops back for the next command. Every shell session is an interactive conversation with the OS.

- "Read" → shell reads input from stdin (usually terminal)
- "Eval" → shell parses, expands variables, forks, execve
- "Print" → output of child process goes to stdout (terminal)
- "Loop" → shell prints prompt, waits for next input

**Where this analogy breaks down:** Unlike a language REPL (Python, Node), the shell does not maintain in-memory state between commands — it maintains only: current directory, exported environment variables, and shell variables. The data produced by one command does not persist unless you redirect to a file or capture in a variable.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The shell is the program you type commands into. When you open a terminal window and type `ls`, the shell is the thing running in that window — it takes your text, runs the right program (`ls`), and shows you the result.

**Level 2 — How to use it (junior developer):**
Know the essential navigation commands: `cd`, `ls`, `pwd`, `mkdir`, `rm`, `cp`, `mv`. Use tab completion to avoid typos. Use `history` and `Ctrl+R` to find previous commands. Understand `~` (home), `.` (current dir), `..` (parent dir). Set `PS1` to customise your prompt. Source `.bashrc` with `. ~/.bashrc` or `. ~/.zshrc` after changes (without logging out).

**Level 3 — How it works (mid-level engineer):**
The shell process has a file descriptor table inherited from its parent (typically `sshd` or the terminal emulator). When you run a command with `> file.txt`, the shell opens `file.txt` (getting fd 3), then `dup2(3, STDOUT_FILENO)` in the child before `execve()` — the child program writes to what it thinks is stdout but is actually the file. Job control (`bg`, `fg`, `Ctrl+Z`) uses POSIX signals: `SIGTSTP` stops the foreground process; `SIGCONT` resumes it. The shell manages a process group (PGID) to send signals to entire pipelines at once.

**Level 4 — Why it was designed this way (senior/staff):**
Bash was designed for POSIX compatibility and scripting portability, not interactive experience. Zsh adds: better tab completion (menu-based), spelling correction, shared history across sessions, extended globbing (`**`). Fish shell takes a different philosophy: no POSIX compatibility, but interactive UX first. The `exec` builtin replaces the shell with another program (no fork) — used in container `CMD` directives to ensure the process runs as PID 1, enabling proper signal handling (especially `SIGTERM` for graceful shutdown).

---

### ⚙️ How It Works (Mechanism)

**Complete command execution sequence:**

```
┌──────────────────────────────────────────────────────┐
│       SHELL COMMAND PROCESSING PIPELINE              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. LEXING: tokenise input into words                │
│     "grep -c ERROR /var/log/app.log"                 │
│     → ["grep", "-c", "ERROR", "/var/log/app.log"]   │
│                                                      │
│  2. PARSING: identify command structure              │
│     command=grep, args=["-c","ERROR","file"]         │
│                                                      │
│  3. EXPANSION (in order):                           │
│     a. Brace expansion:  {a,b}c → ac bc             │
│     b. Tilde expansion:  ~/foo → /home/alice/foo     │
│     c. Parameter expand: $VAR → value               │
│     d. Command subst:    $(cmd) → output of cmd     │
│     e. Arithmetic:       $((1+1)) → 2               │
│     f. Word splitting:   split on IFS (space/tab)   │
│     g. Glob expansion:   *.log → file1.log file2.log │
│     h. Quote removal:    remove quotes from tokens  │
│                                                      │
│  4. REDIRECTION SETUP                               │
│     If ">" or "|", set up fd redirections           │
│                                                      │
│  5. FORK + EXEC                                     │
│     fork() → child execve() → parent wait()         │
│                                                      │
│  6. OUTPUT: child writes to (possibly redirected)   │
│     stdout; parent shell gets exit code             │
└──────────────────────────────────────────────────────┘
```

**Bash vs Zsh key differences:**

| Feature          | Bash                        | Zsh                           |
| ---------------- | --------------------------- | ----------------------------- |
| Default on       | Most Linux distros          | macOS (Catalina+)             |
| Tab completion   | Basic                       | Advanced (menu, descriptions) |
| History sharing  | Per-session                 | Can share across sessions     |
| Array syntax     | `arr=(a b c)`               | `arr=(a b c)` + assoc arrays  |
| Glob support     | Basic `*`, `?`              | Extended `**` recursive glob  |
| Spell check      | No                          | Yes (`setopt correct`)        |
| POSIX compliance | Near-full                   | Near-full (in emulation)      |
| Config file      | `.bashrc` / `.bash_profile` | `.zshrc` / `.zprofile`        |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Engineer SSH's into server
    ↓
sshd authenticates, forks, setuid(alice)
    ↓
sshd exec's alice's login shell: /bin/bash
    ↓
bash sources /etc/profile, ~/.bash_profile
    ↓
bash prints PS1 prompt, reads stdin
    ← YOU ARE HERE (interactive shell loop)
    ↓
Engineer types: journalctl -u nginx --since today
    ↓
bash parses, forks, execve(/usr/bin/journalctl ...)
    ↓
journalctl queries systemd journal, writes to stdout
    ↓
bash waits, prints prompt again
```

**FAILURE PATH:**

```
Command typo: "grpe -c ERROR file.log"
    ↓
bash attempts execve on "grpe" — PATH search fails
    ↓
bash returns: "grpe: command not found" (exit code 127)
    ↓
Script using "set -e" exits immediately on error
```

**WHAT CHANGES AT SCALE:**
In production automation, interactive shells give way to non-interactive shells running scripts. At scale, Ansible, Terraform, and CI/CD pipelines invoke shell scripts remotely — the shell becomes the automation substrate. Performance matters: a shell script looping over 10,000 files is O(n) process forks; use `awk` or Python for bulk operations. Shell startup time becomes significant when scripts are invoked millions of times (e.g., CGI scripts) — use compiled languages for performance-critical paths.

---

### 💻 Code Example

**Example 1 — Basic navigation and inspection:**

```bash
# Where am I?
pwd            # print working directory

# List files with details
ls -lah        # long format, all files, human sizes

# Navigate
cd /var/log    # go to /var/log
cd ..          # go up one level
cd ~           # go home
cd -           # go back to previous dir (like "back" button)

# Check shell info
echo $SHELL    # → /bin/bash or /bin/zsh
echo $0        # current shell name
bash --version
```

**Example 2 — Variables and expansion:**

```bash
# Variable assignment (no spaces around =)
NAME="alice"
echo "Hello, $NAME"          # → Hello, alice
echo "Shell: ${SHELL}"       # braces for clarity

# Command substitution
TODAY=$(date +%Y-%m-%d)
LINES=$(wc -l < /var/log/app.log)
echo "Log has $LINES lines today: $TODAY"

# Arithmetic
COUNT=5
echo $((COUNT * 2 + 1))      # → 11
```

**Example 3 — The difference between built-ins and externals:**

```bash
# cd is a BUILT-IN — runs in the current shell process
type cd      # → cd is a shell builtin
cd /tmp      # changes THIS shell's working directory

# ls is EXTERNAL — runs in a child process
type ls      # → ls is /bin/ls
ls /tmp      # forks a child, execs /bin/ls

# export modifies the shell's environment (built-in)
export MYVAR="hello"
# Child processes WILL inherit MYVAR
bash -c 'echo $MYVAR'    # → hello

# Unset only modifies the shell (built-in)
unset MYVAR
```

**Example 4 — Shell configuration (Bash):**

```bash
# ~/.bashrc — runs for every interactive non-login bash
# Add to ~/.bashrc:

# Better history
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups
shopt -s histappend

# Better prompt with git branch
parse_git_branch() {
  git branch 2>/dev/null | sed -n 's/* \(.*\)/(\1)/p'
}
PS1='\u@\h:\w$(parse_git_branch)\$ '

# Useful aliases
alias ll='ls -lah'
alias la='ls -A'
alias grep='grep --color=auto'
alias ..='cd ..'
```

---

### ⚖️ Comparison Table

| Shell      | Interactive UX | Scripting | POSIX  | Default On             | Best For               |
| ---------- | -------------- | --------- | ------ | ---------------------- | ---------------------- |
| **Bash**   | Good           | Excellent | Yes    | Most Linux             | Scripting, portability |
| Zsh        | Excellent      | Excellent | Near   | macOS                  | Interactive daily use  |
| Fish       | Best           | Limited   | No     | None                   | Beginners, interactive |
| Dash       | Minimal        | Fast      | Yes    | `/bin/sh` some distros | Fast script execution  |
| Sh (POSIX) | Minimal        | Portable  | Strict | POSIX systems          | Maximum portability    |

**How to choose:** Use bash for scripts you'll deploy on servers (maximum compatibility). Use zsh or fish interactively for productivity. Never use bash-specific features in scripts with `#!/bin/sh` shebang — use `#!/bin/bash` explicitly.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                       |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------- |
| `cd` runs as a child process like other commands | `cd` is a shell built-in; it runs in the current shell process because only the shell can change its own working directory    |
| `.bashrc` is sourced for every bash session      | `.bashrc` is only sourced for interactive non-login shells; SSH logins source `.bash_profile` instead                         |
| `export VAR=value` makes a variable permanent    | `export` only sets the variable for the current session and its children; it is gone after logout unless added to `~/.bashrc` |
| Quoting doesn't matter for simple values         | `rm $FILE` where `FILE="my file.txt"` deletes two things: `my` and `file.txt`; always quote: `rm "$FILE"`                     |
| `#!/bin/sh` and `#!/bin/bash` are the same       | `/bin/sh` may be `dash` (Debian/Ubuntu) with no bashisms; `#!/bin/bash` guarantees bash-specific features work                |
| The shell runs commands sequentially by default  | Pipelines run concurrently — `cat file                                                                                        | grep pattern | wc -l` runs all three processes in parallel |

---

### 🚨 Failure Modes & Diagnosis

**"Command Not Found" Despite Tool Being Installed**

**Symptom:**
`myapp: command not found` even though `which myapp` shows a path.

**Root Cause:**
The binary's directory is not in `PATH`, or PATH was set incorrectly (e.g., in `.bash_profile` which was not sourced).

**Diagnostic Command:**

```bash
echo $PATH
which myapp    # returns nothing if not in PATH
type myapp     # shows if it's a builtin, function, alias, or file
# Or: where is the binary actually?
find / -name myapp -type f 2>/dev/null
```

**Fix:**

```bash
# Add to ~/.bashrc or ~/.bash_profile
export PATH="$PATH:/usr/local/myapp/bin"
source ~/.bashrc
```

**Prevention:**
Set PATH in `/etc/environment` or `/etc/profile.d/myapp.sh` for system-wide availability.

---

**Script Works Interactively but Fails in Cron/CI**

**Symptom:**
Script runs fine when executed manually; fails silently or with "command not found" when run by cron or CI.

**Root Cause:**
Cron and CI run with minimal PATH (typically `/usr/bin:/bin`). Interactive shells have a much richer PATH from `.bashrc`/`.bash_profile`. Cron also doesn't source `~/.bashrc`.

**Diagnostic Command:**

```bash
# Simulate cron's environment
env -i PATH=/usr/bin:/bin HOME=/root bash -c 'yourscript.sh'
```

**Fix:**

```bash
# At top of script: set explicit full PATH
PATH=/usr/local/bin:/usr/bin:/bin
# OR use absolute paths for all commands
/usr/bin/python3 /path/to/script.py
```

**Prevention:**
Always use absolute paths in cron scripts; add `#!/usr/bin/env bash` and set PATH explicitly.

---

**Quoting Bug Causes Silent Data Deletion**

**Symptom:**
`rm $DIR/*` where `DIR` is unexpectedly empty; deletes files in the current directory.

**Root Cause:**
When `$DIR` is empty, `rm /*` expands to removing everything in the root (or current) directory. Unquoted variables that are empty or contain spaces cause word splitting.

**Diagnostic Command:**

```bash
# Debug expansions before running destructive commands
set -x    # enables execution trace
echo "rm $DIR/*"   # always echo before rm in scripts
```

**Fix:**

```bash
# WRONG: unquoted, dangerous
rm $DIR/*

# GOOD: quoted, fails safely if DIR is unset/empty
rm "${DIR:?Error: DIR is not set}"/*
# :? causes immediate exit with error if DIR is unset/empty
```

**Prevention:**
Use `set -euo pipefail` at the top of every bash script: `-e` exits on error, `-u` treats unset variables as errors, `-o pipefail` catches pipe failures.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Linux File System Hierarchy` — the shell navigates and manipulates the filesystem hierarchy
- `Users and Groups` — the shell runs as a specific user; identity governs what commands can do

**Builds On This (learn these next):**

- `Shell Scripting` — writing programs using shell commands and control flow
- `Pipes and Redirection` — composing commands with stdin/stdout
- `stdin / stdout / stderr` — the I/O model the shell manages for every command
- `grep / awk / sed` — the text-processing tools most commonly used via the shell

**Alternatives / Comparisons:**

- `SSH` — SSH delivers a remote shell session over an encrypted tunnel
- `tmux / screen` — terminal multiplexers that persist shell sessions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Interactive interpreter between human     │
│              │ text commands and kernel system calls     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No interactive way to issue commands      │
│ SOLVES       │ to a running Linux system                 │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Built-ins (cd, export) run in the shell   │
│              │ process itself; externals fork a child    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always for interactive admin; bash for    │
│              │ scripts; zsh/fish for productivity        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use shell for performance-critical  │
│              │ loops over large datasets (use awk/Python)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Convenience vs. performance; portability  │
│              │ (bash) vs. UX (zsh/fish)                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The shell is just a program that does    │
│              │  fork+exec on your behalf"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Shell Scripting → Pipes and Redirection   │
│              │ → grep / awk / sed                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** When you SSH into a server and run `export MYVAR=hello`, then close the session and SSH again, `MYVAR` is gone. But when you run `echo "export MYVAR=hello" >> ~/.bashrc` and start a new SSH session, `MYVAR` is present. Explain precisely what happens at each step — what the shell does when it starts, which files it sources, and why `export` in one session cannot survive to the next without modifying a startup file.

**Q2.** A shell script runs `CMD=$(expensive_command)` — capturing the output of a long-running program. The `expensive_command` writes its result to stdout but also writes progress messages to stderr. The script then passes `$CMD` to another program. What does `$CMD` contain? What happens to the progress messages? How would you capture both stdout and stderr into separate variables simultaneously, and what system-level mechanism (fork/pipe/fd) does the shell use to implement command substitution `$()`?
