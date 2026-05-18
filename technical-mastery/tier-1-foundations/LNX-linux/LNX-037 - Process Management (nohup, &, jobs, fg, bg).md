---
id: LNX-037
title: "Process Management (nohup, &, jobs, fg, bg)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-013, LNX-006
used_by: LNX-047, LNX-060
related: LNX-013, LNX-047, LNX-031
tags: [nohup, background, jobs, fg, bg, disown, screen, tmux, process-control, shell-job]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/lnx/process-management-jobs/
---

## TL;DR

Linux shell job control: `command &` runs it in the background (still tied
to terminal). `nohup command &` runs it immune to terminal hangup (logout
won't kill it). `jobs` lists background jobs in current shell. `fg %1`
brings job 1 to foreground. `bg %1` resumes a suspended job in background.
`Ctrl+Z` suspends current foreground job. `disown %1` detaches job from
shell (won't receive SIGHUP on exit). For persistent sessions that survive
SSH disconnect: use `tmux` or `screen`. For production daemons: use
`systemd` (not nohup).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-037 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | nohup, background jobs, fg, bg, jobs, disown, job control, tmux, screen |
| **Prerequisites** | LNX-013, LNX-006 |

---

### The Problem This Solves

You SSH into a server to run a database migration that takes 30 minutes.
If your SSH connection drops halfway through, the migration process dies
(SIGHUP). Data could be left in an inconsistent state. Solutions: `nohup
migration.sh &` (basic), `tmux new -s migration` then run inside tmux
(better - keeps interactive output visible), `systemd-run` (proper daemonization).
Understanding job control saves you from accidentally killing long-running
work by closing a terminal.

---

### Textbook Definition

**Job control**: The shell's mechanism for managing groups of processes
(called "jobs"). A job is a pipeline or single command started from a
shell. Jobs can be in three states: foreground (currently has terminal),
background running, or stopped (suspended).

**SIGHUP (Signal Hangup)**: Signal sent to a process group when the
controlling terminal closes (user logs out, SSH connection drops). Default
action: terminate. This is why processes die when you close the terminal.

**Session and process group**: Every process belongs to a process group.
Process groups belong to a session. Sessions have a controlling terminal.
When the terminal closes, all processes in the session receive SIGHUP.

**nohup**: Wrapper that sets SIGHUP to SIG_IGN (ignore) before exec'ing
the command. Also redirects stdout to `nohup.out` if stdout is a terminal.

---

### Understand It in 30 Seconds

```bash
# Run in background (still tied to terminal - SIGHUP kills it on logout):
long-running-command &
# Shell prints: [1] 12345   ([job_number] PID)

# Suspend current foreground process:
Ctrl+Z   # -> "[1]+ Stopped    long-running-command"

# List all background/stopped jobs:
jobs
# [1]+ Stopped    long-running-command
# [2]  Running    another-command &

# Resume stopped job in background:
bg %1   # job 1 continues running in background

# Bring job to foreground:
fg %1   # job 1 comes to foreground

# Detach from terminal completely (run immune to logout):
nohup long-running-command &
# Creates nohup.out for stdout/stderr
# Process continues if you log out

# Detach an already-running background job:
command &       # start it
jobs            # see job number [1]
disown %1       # detach - no longer in shell's job list
# Now safe to close terminal

# Better for long sessions: tmux
tmux new -s mysession      # create named session
# ... run your commands ...
Ctrl+b, d                  # detach from tmux (session keeps running)
# SSH disconnect - session persists
tmux attach -t mysession   # reconnect from new SSH session

# Or: screen
screen -S mysession        # create named screen session
Ctrl+a, d                  # detach
screen -r mysession        # reattach

# Check if nohup'd process is still running after logout:
pgrep -f "long-running-command"
cat nohup.out              # view output
```

---

### First Principles

**Why processes die when you close the terminal:**

```
Terminal close sequence:
  1. Terminal device (pty) is closed
  2. Kernel sends SIGHUP to the session's foreground process group
  3. SIGHUP default action: terminate
  4. Child processes inherit SIGHUP -> all die

Process hierarchy:
  bash (PID 100, session leader, controlling terminal: /dev/pts/0)
    -> sleep 1000 & (PID 101, job [1])
    -> vim file.txt (PID 102, foreground)

Close terminal: SIGHUP -> bash (PID 100) -> SIGHUP -> all children
Result: sleep 1000 AND vim both die

nohup sleep 1000 &:
  1. nohup forks
  2. Child: signal(SIGHUP, SIG_IGN) <- ignore SIGHUP
  3. exec("sleep", ...)
  4. Terminal closes -> SIGHUP to process group
  5. sleep: SIG_IGN -> process survives

disown %1 in bash:
  bash removes the process from its "notify-on-SIGHUP" list
  bash will NOT send SIGHUP to the process when bash exits
```

**jobs vs processes:**
`jobs` shows jobs for the CURRENT SHELL ONLY. If you ssh in a new
terminal, `jobs` is empty (different shell, different session). Use
`ps aux | grep command` to find processes across all sessions.

---

### Thought Experiment

You started a deployment script: `./deploy.sh &`. Then you realized you need
to run it with nohup because your SSH might disconnect.

```bash
# The process is already running as [1] PID 5678

# Option 1: disown (best - removes from shell's job control):
disown %1
# Now: shell exits won't send SIGHUP to 5678
# Process keeps running, but stdout is still connected to terminal
# (nohup.out not created - disown doesn't redirect stdout)

# Problem: process output goes to the terminal
# When terminal closes, writes to terminal FD cause SIGPIPE

# Option 2: redirect output too (via /proc):
# Terminal window stays open or redirect output to file in advance

# Correct approach from the start:
nohup ./deploy.sh > /tmp/deploy.log 2>&1 &
# nohup: ignores SIGHUP
# > /tmp/deploy.log 2>&1: stdout AND stderr to log file
# &: background
# Now: safe to close terminal, check progress with: tail -f /tmp/deploy.log

# Even better for interactive monitoring:
tmux new -s deploy
./deploy.sh
# Ctrl+b, d to detach
# tmux attach -t deploy to reconnect from anywhere
```

---

### Mental Model / Analogy

```
Shell = a manager's desk at work
Foreground job = task on the manager's desk (getting full attention)
Background job (&) = task given to an assistant (working independently)
Ctrl+Z = pausing the task on the desk, setting it aside
jobs = list of all tasks the manager is tracking
fg = picking a set-aside task back up
bg = telling the paused assistant to continue working

SIGHUP problem:
Terminal = the manager's DESK itself
Close terminal = manager leaves work
All tasks tracked by this desk = "sent home" (SIGHUP)

nohup = "task doesn't depend on this manager's desk"
         (immune to SIGHUP - job keeps going even if desk is gone)

tmux/screen = a SEPARATE persistent desk
              Manager can leave and come back to the same desk
              Tasks never know the manager left
              
systemd = a professional task management system
          (not a desk, it's the whole office infrastructure)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`command &` runs in background. `Ctrl+Z` suspends. `fg` brings it back.
`nohup command &` survives logout. `jobs` lists what's running. That's
the 90% case for interactive use.

**Level 2:**
`%1`, `%2` job identifiers. `%command_name` selects by name: `fg %sleep`.
`disown` vs `nohup`: nohup sets SIG_IGN before exec; disown removes from
shell's job table after starting. tmux vs screen: tmux is newer, splits
panes, more scriptable. screen is older, more universally installed.

**Level 3:**
`setsid command &`: creates a new session for the command (complete
detachment from controlling terminal). `kill -CONT PID` = resume suspended
process (equivalent to bg). `kill -STOP PID` = suspend process (equivalent
to Ctrl+Z). Shell job spec: `kill %1` (kill job 1), `kill %+` (kill most
recent job). `wait %1` in scripts: wait for background job to complete.

**Level 4:**
`systemd-run --unit=myjob ./script.sh`: run a transient systemd unit.
Better than nohup for one-off tasks: logs go to journald, you can monitor
with `systemctl status myjob`. Job arrays in bash: `jobs -l` shows PIDs.
`$!` variable = PID of last background command. Process substitution
`<(command)` uses FDs (not background jobs) for anonymous pipes. GNU
parallel: properly manages many background processes with job control.

**Level 5:**
Controlling terminal acquisition: `setsid()` syscall creates new session,
detaches from controlling terminal. `TIOCNOTTY` ioctl: release controlling
terminal without creating new session. These are how proper daemons
double-fork: fork once (parent exits), setsid() (become session leader),
fork again (prevent terminal reacquisition). Libraries like `daemon(3)`
implement this pattern. Modern approach: systemd service files with
`Type=forking` or `Type=simple` replace manual double-fork daemon patterns.

---

### Code Example

**BAD - nohup misuse:**
```bash
# BAD 1: Forgetting to redirect stderr
nohup ./script.sh &
# Output goes to nohup.out
# But if script writes to STDERR and nohup.out fills disk...
# Better: explicit redirect
nohup ./script.sh > /var/log/script.log 2>&1 &

# BAD 2: Not capturing the PID
nohup long-migration.sh > /tmp/migration.log 2>&1 &
# If it fails partway through, how do you find it?
# GOOD: capture PID
nohup long-migration.sh > /tmp/migration.log 2>&1 &
MIGRATION_PID=$!
echo $MIGRATION_PID > /tmp/migration.pid
echo "Migration running as PID $MIGRATION_PID"
echo "Monitor: tail -f /tmp/migration.log"

# BAD 3: Using nohup for production services
nohup java -jar myapp.jar &
# No auto-restart on crash, no log management,
# no dependency ordering, no resource limits
# Use systemd instead!

# GOOD: systemd service file for persistent processes
# /etc/systemd/system/myapp.service:
# [Unit]
# Description=My Application
# After=network.target
# [Service]
# ExecStart=/usr/bin/java -jar /opt/myapp/myapp.jar
# Restart=always
# User=myapp
# [Install]
# WantedBy=multi-user.target
```

**GOOD - reliable background job pattern:**
```bash
#!/bin/bash
# run-background-job.sh: Run a job that survives terminal close
# and provides monitoring

JOB_NAME="$1"
JOB_CMD="$2"
LOG_DIR="/var/log/jobs"
mkdir -p "$LOG_DIR"

LOG_FILE="${LOG_DIR}/${JOB_NAME}-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="${LOG_DIR}/${JOB_NAME}.pid"

# Check if already running:
if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
    echo "Job $JOB_NAME already running (PID: $(cat $PID_FILE))"
    exit 1
fi

# Start the job:
nohup bash -c "$JOB_CMD" > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "Started: $JOB_NAME (PID: $(cat $PID_FILE))"
echo "Logs: $LOG_FILE"
echo "Monitor: tail -f $LOG_FILE"
echo "Stop: kill \$(cat $PID_FILE)"
```

---

### Comparison Table

| Method | Survives logout | Output | Reconnect | Best for |
|--------|-----------------|--------|-----------|---------|
| `command &` | No (SIGHUP kills) | Terminal | No | Short tasks |
| `nohup cmd &` | Yes | nohup.out | No | One-off long tasks |
| `disown` | Yes | Terminal (may break) | No | Already running jobs |
| `screen` | Yes | Screen session | Yes | Interactive sessions |
| `tmux` | Yes | tmux session | Yes | Interactive sessions |
| `systemd` | Yes | journald | Via journalctl | Production daemons |
| `cron` | N/A | /var/mail or file | N/A | Scheduled tasks |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "nohup makes a process a proper daemon" | nohup only ignores SIGHUP and redirects stdout. A proper daemon also: closes all FDs, calls setsid() to detach from terminal, changes working directory to /, drops privileges. Use systemd for production daemons. nohup is for "I don't want this to die if I log out." |
| "Ctrl+Z kills the process" | Ctrl+Z sends SIGSTOP (actually SIGTSTP in terminal context), which PAUSES the process. The process is suspended in memory, not terminated. `fg` or `bg` resumes it. `kill %1` actually terminates it. |
| "Background jobs continue if you close the terminal" | By default NO - background `command &` jobs receive SIGHUP when the controlling terminal closes and terminate. Only nohup, disown, tmux/screen, or setsid prevent this. |
| "disown is the same as nohup" | nohup sets SIG_IGN for SIGHUP BEFORE the process starts. disown removes the process from the shell's job table AFTER it's running, preventing the shell from sending SIGHUP on exit. Key difference: nohup also redirects stdout; disown does not. |
| "jobs shows all background processes" | `jobs` only shows jobs for the CURRENT SHELL SESSION. Processes started in other terminals, by other users, or via systemd are NOT shown. Use `ps aux` or `pgrep` to find processes outside your shell. |

---

### Failure Modes & Diagnosis

**Process dies on terminal close despite nohup:**
```bash
# You ran: nohup ./script.sh &
# After logout, the process is gone. Why?

# Most likely: the script writes to stdout/stderr that's still the terminal
# nohup redirects stdout to nohup.out IF stdout is a terminal
# but if you already redirected stdout: nohup.out isn't created
# and the terminal FD is still inherited for writes

# Check if nohup.out was created:
ls -la nohup.out    # should exist and have content

# Better approach with explicit redirect:
nohup ./script.sh > /tmp/myscript.log 2>&1 &
# BOTH stdout and stderr go to the log file
# Process completely detached from terminal output

# Debug: wrap with strace to see signal handling:
nohup strace -e signal -p PID 2>&1 | head -20
```

---

### Related Keywords

**Foundational:**
LNX-013 (Processes), LNX-006 (Terminal)

**Builds on this:**
LNX-047 (Process Signals), LNX-060 (Process Scheduling)

**Related:**
LNX-031 (systemd), OSY-015 (Process States)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `command &` | Run in background |
| `Ctrl+Z` | Suspend foreground job |
| `jobs` | List jobs in this shell |
| `fg %N` | Bring job N to foreground |
| `bg %N` | Resume job N in background |
| `disown %N` | Detach job N from shell |
| `nohup cmd &` | Run immune to logout |
| `tmux new -s name` | New persistent session |
| `Ctrl+b, d` | Detach from tmux |
| `tmux attach -t name` | Reconnect to tmux session |
| `$!` | PID of last background command |

**3 things to remember:**
1. `command &` = background but DIES on logout; `nohup command &` = survives logout
2. Ctrl+Z suspends (pauses) the process - not kills it; use `fg` to resume
3. For production: use `systemd`, not nohup; for interactive sessions: use `tmux`

---

### Transferable Wisdom

The terminal/process relationship (controlling terminal, session, process groups)
is the foundation for understanding: Docker container process model (PID 1 in
container receives SIGTERM on stop, must properly handle signals), Kubernetes
pod lifecycle (kubelet sends SIGTERM to PID 1, then SIGKILL after grace period),
SSH port forwarding (connection dies = SIGHUP = process dies), CI/CD build agents
(why long-running jobs need proper session management), shell scripting (why
`wait $PID` is needed to capture exit codes of background jobs).

tmux's multiplexing pattern (persistent server keeps sessions alive, clients
connect/disconnect) appears in: database connection pools, WebSocket server
architecture, language server protocol (LSP editor integration). The principle:
decouple the work from the client connection lifetime.

---

### The Surprising Truth

`Ctrl+Z` (SIGTSTP) and `Ctrl+C` (SIGINT) work because the terminal driver
sends signals, not because bash is intercepting keystrokes. The kernel's
tty driver (line discipline layer) sees `^Z` and sends SIGTSTP to the
foreground process group. This happens BEFORE bash ever sees the character.
This means: even programs that catch signals can be stopped with `Ctrl+Z`
(unless they explicitly block SIGTSTP). Programs like `sudo` use SIGTSTP
handling to prevent unauthorized users from pausing privileged processes.
The reason `Ctrl+C` sends SIGINT (not just EOF) is that the terminal
driver is designed to interrupt foreground processes without closing the
terminal - so the shell survives and you see a new prompt. If you want
to send the actual characters Ctrl+Z or Ctrl+C to a program (not as signals):
`stty susp undef` disables the suspend character; `stty intr undef` disables
the interrupt character.

---

### Mastery Checklist

- [ ] Can start, suspend, resume, and terminate background jobs
- [ ] Can use nohup correctly with output redirect
- [ ] Can start and detach a tmux session that persists after SSH disconnect
- [ ] Can use disown on an already-running job
- [ ] Understands why background processes die on terminal close and how to prevent it

---

### Think About This

1. You run `./long-running-process.sh &` and then `exit`. The process dies.
   You run the same command but this time follow it with `disown`. Then `exit`.
   The process continues. Explain the exact kernel mechanism that makes these
   two scenarios different. What specific signal did the first process receive
   that the second one did not?

2. `tmux` and `screen` both solve the "survive SSH disconnect" problem, but
   through a completely different mechanism than `nohup`. Explain how tmux
   achieves session persistence. (Hint: think about the controlling terminal
   and which process is the session leader.)

3. You have a bash script that runs 5 jobs in parallel with `&`. The script
   later calls `wait`. If one of the background jobs fails (non-zero exit code),
   what does `wait` return? How would you write a script that runs 5 parallel
   jobs, detects if ANY of them failed, and exits with a non-zero status?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between running a command with & and with nohup?
A: `command &`: runs the command as a background job IN THE CURRENT SHELL SESSION. The process is still part of the terminal's process group and session. When you logout (terminal closes), the shell receives SIGHUP and broadcasts it to its process groups - killing background jobs too. `nohup command &`: the `nohup` wrapper sets SIGHUP to SIG_IGN (ignored) in the child BEFORE exec'ing the actual command. It also redirects stdout to `nohup.out` if stdout is a terminal. When you logout: SIGHUP is sent but the process ignores it and survives. Key limitation: `nohup` only solves SIGHUP. If the process writes to a closed terminal FD, it may get SIGPIPE. Best practice: `nohup command > /path/to/logfile 2>&1 &` - explicitly redirects both stdout and stderr away from the terminal. For production services: use systemd (handles auto-restart, dependency ordering, proper logging, resource limits).

**Intermediate:**
Q: You SSH into a server, start a long database migration with nohup, and then your SSH session drops. When you reconnect, how do you verify the migration is still running and check its progress?
A: Finding the process: (1) `pgrep -f "migration_script_name"` - search by command name. (2) `ps aux | grep migration` - more detail. (3) `cat /tmp/migration.pid` - if the script saved its PID. Checking progress: (4) `tail -f /tmp/migration.log` - if output was redirected to a log file (`nohup ./migrate.sh > /tmp/migration.log 2>&1 &`). (5) `cat /proc/PID/fd/1` via lsof to find where stdout went: `lsof -p PID | grep stdout`. (6) Check nohup.out: `tail -f nohup.out` (default nohup output file). Process status: (7) `ls /proc/PID/status` - confirms process exists. (8) `strace -p PID -e trace=read,write` - see what it's currently reading/writing (for debugging). Database-specific: (9) Connect to the database and check migration progress tables if the migration tracks state. Prevention for next time: run inside `tmux new -s migration`, then `Ctrl+b d` to detach - reconnect with `tmux attach -t migration` to see live output from a new SSH session.

**Expert:**
Q: Explain the double-fork daemonization pattern and why modern Linux replaced it with systemd service types.
A: Classic double-fork pattern (from Stevens' APUE): (1) First fork + parent exits: orphan child, PID 1 (init) adopts it. This detaches from the calling shell's process group. (2) setsid(): child becomes session leader AND gets a new session with no controlling terminal. Terminal close can't affect it. (3) Second fork + first child exits: prevents the daemon from ever reacquiring a controlling terminal (only session leaders can acquire one). The double-fork's second child is NOT a session leader, so `open("/dev/tty")` can never make it the controlling terminal owner. (4) chdir("/"), umask(0), close all FDs, reopen 0/1/2 to /dev/null: complete environment cleanup. Why systemd replaced it: double-fork complicates PID tracking (parent exits twice, final PID differs from original). systemd couldn't reliably track which process was the daemon. Solutions: `Type=forking` with `PIDFile=` (daemon writes its PID). But this creates startup races. Better: `Type=simple` or `Type=notify`. Type=simple: systemd considers the service started when exec() happens (no fork needed, no double-fork). Type=notify: service sends sd_notify("READY=1") when truly ready. Type=exec: started when exec() completes. Modern pattern: don't daemonize at all. Write a simple single-process server that reads from systemd socket (socket activation). Let systemd handle process supervision, log management (journald), and dependency ordering. The double-fork is now a historical artifact - write process, not daemon.
