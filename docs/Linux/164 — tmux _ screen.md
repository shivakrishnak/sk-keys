---
layout: default
title: "tmux / screen"
parent: "Linux"
nav_order: 164
permalink: /linux/tmux-screen/
number: "0164"
category: Linux
difficulty: ★☆☆
depends_on: Linux File System Hierarchy
used_by: DevOps, Shell Scripting, Linux Administration
related: Linux File System Hierarchy, SSH, Shell Scripting
tags:
  - linux
  - os
  - devops
  - tools
---

# 164 — tmux / screen

⚡ TL;DR — `tmux` and `screen` are terminal multiplexers that keep sessions alive after SSH disconnects, split terminals into multiple panes/windows, and allow re-attachment from any client — eliminating the "my process died when I closed my laptop" problem.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You SSH into a production server, start a database migration that will take 45 minutes, and your laptop battery dies. SSH disconnects. SIGHUP is sent to the shell. The migration process dies mid-way. The database is in a half-migrated state. You've now caused data corruption.

**THE BREAKING POINT:**
Every long-running process started over SSH is vulnerable to network instability, laptop sleep, VPN timeouts, and accidental terminal closure. The process runs as a child of the SSH shell; when SSH exits, SIGHUP propagates to all its children, and they die unless explicitly immune (`nohup`).

**THE INVENTION MOMENT:**
`screen` (1987) solved this by creating a daemon process that holds the terminal session. The user connects to a `screen` session — the actual process is a child of the screen daemon, not of SSH. When SSH disconnects, the screen daemon (and all its child processes) continue running. The user can SSH back in and `screen -r` to re-attach to the running session and see the output as if they never disconnected.

`tmux` (2007) is the modern replacement: richer features (true split panes, scriptable, better Unicode support, client-server model), active development, and the de facto standard for terminal multiplexing.

---

### 📘 Textbook Definition

A **terminal multiplexer** is a program that creates a virtual terminal session managed by a persistent daemon process, decoupled from any specific SSH or physical terminal connection. Multiple clients can attach to and detach from the session. Within a session, the multiplexer provides: **windows** (named tabs), **panes** (split views within a window), and **persistent history**.

**tmux** (terminal multiplexer) uses a client-server model: `tmux` server runs as a background daemon; `tmux` client connects to the server via a Unix socket (`/tmp/tmux-<uid>/default`). All sessions, windows, and panes exist on the server and persist when clients disconnect.

**GNU screen** is the older predecessor; still available and sometimes present when tmux is not.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
tmux decouples your terminal session from your SSH connection — close your laptop, SSH back later, and find everything exactly as you left it.

**One analogy:**

> tmux is like a shared whiteboard in a meeting room. You walk in (SSH connect), start writing (run commands), and when you leave the room (close SSH), the whiteboard stays. Anyone with access can walk in later (re-attach) and see exactly what was written. Multiple people can write on the whiteboard at the same time (shared sessions), and you can divide the whiteboard into sections (panes). The whiteboard exists independently of any specific person being in the room.

**One insight:**
The key mental shift: your terminal session is not owned by your SSH connection — it's owned by the tmux server. SSH is just a client viewing the session. This is also why tmux enables pair programming: two SSH connections can attach to the same session and see real-time changes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. tmux server is a background daemon — it persists regardless of client connections.
2. All processes running inside tmux are children of the tmux server, not of the SSH session.
3. Detaching from a session does not send SIGHUP to the processes inside.
4. Sessions are persistent until explicitly killed (or server rebooted).
5. Keyboard shortcuts in tmux use a **prefix key** (`Ctrl+b` by default) to distinguish tmux commands from input to the running program.

**DERIVED DESIGN:**

**Client-server architecture:**

```
[SSH client] ─── [SSH daemon] ─── [tmux client]
                                        │
                                [Unix socket]
                                        │
                               [tmux server (daemon)]
                                        │
                    ┌───────────────────┼─────────────────┐
                 Session 1          Session 2          Session 3
                    │
            ┌───────┴───────┐
          Window 1       Window 2
             │
       ┌─────┴─────┐
     Pane 1    Pane 2
       │
  [bash] → processes (migration, build, etc.)
```

When SSH disconnects: `[tmux client]` exits, but `[tmux server]` and everything below it continues running.

**THE TRADE-OFFS:**
**Gain:** SSH-disconnect resilience; multi-pane workflow; session sharing; scriptable; pairs well with vim/emacs.
**Cost:** Learning curve (prefix key, command syntax); tmux-inside-tmux confusion; `screen` conflicts on some systems; server process adds complexity.

---

### 🧪 Thought Experiment

**SETUP:**
You're deploying to a remote server over an unstable VPN. Task: run a 30-minute database migration.

**WITHOUT tmux:**

```bash
ssh server
python migrate.py  # starts running
# VPN drops at 15 minutes
# SSH disconnects → SIGHUP → migrate.py dies
# Migration is 50% complete → database in inconsistent state
# Monday morning: panic
```

**WITH tmux:**

```bash
ssh server
tmux new -s migration   # create named session
python migrate.py       # starts running in tmux
# Ctrl+b d              # detach (or VPN drops — same effect)
# Migration continues! tmux server is still running.

# SSH back in (any time, any laptop):
ssh server
tmux attach -t migration   # re-attach
# See exactly where migration is, scroll through history
```

**WITH tmux for monitoring:**

```bash
# Split-pane monitoring during migration:
tmux new -s deploy
# Pane 1: run migration
python migrate.py
# Ctrl+b %              # split pane vertically
# Pane 2: watch logs
tail -f /var/log/app/migration.log
# Ctrl+b "              # split horizontally
# Pane 3: monitor DB
watch -n 5 "psql -c 'SELECT COUNT(*) FROM users'"
```

**THE INSIGHT:**
tmux isn't just about SSH resilience — it's a workflow tool. Developers keep persistent sessions with specific layouts (editor, tests, logs) that survive reboots, reconnects, and context switches.

---

### 🧠 Mental Model / Analogy

> tmux is like a bank vault (persistent, always on) vs a safe deposit box visit (SSH connection, temporary). When you go to the bank (SSH), you access the vault (tmux server). You can open drawers (sessions), organise documents in folders (windows), and spread documents across the desk (panes). When you leave the bank (SSH disconnect), the vault door closes but everything inside stays exactly as you left it. Next visit (SSH back), you open the vault and find everything in the same state. Other authorised people can visit the vault simultaneously and see what you've arranged.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
tmux keeps your terminal sessions alive even after you close your SSH connection. You can split your terminal into multiple panes, run different things in each, come back later, and find everything where you left it. It's like having multiple persistent remote terminals instead of one that disappears when your connection drops.

**Level 2 — How to use it (junior developer):**
Essential commands: `tmux` (new session), `tmux new -s name` (named session), `tmux ls` (list sessions), `tmux attach -t name` (attach to session). Inside tmux, all commands start with `Ctrl+b` (prefix): `d` (detach), `c` (new window), `n/p` (next/prev window), `%` (split vertically), `"` (split horizontally), arrow keys (switch panes), `[` (scroll mode), `?` (help). Customise `~/.tmux.conf`.

**Level 3 — How it works (mid-level engineer):**
tmux server creates a Unix domain socket (`/tmp/tmux-<UID>/default`). The client connects via this socket. The server maintains the terminal state (character buffer, cursor position, scrollback) as an in-memory structure. Processes run inside pseudo-terminals (ptys) managed by the tmux server. When the last client detaches, the server keeps all ptys open and continues to process output (buffer up to scrollback limit). On re-attach, the client redraws the terminal from the server's buffer. This is why you can scroll back through output that happened while detached (up to the scrollback limit). Sessions survive reboots only if the server is preserved (e.g., in a VM snapshot or via tmux plugins like `tmux-resurrect`).

**Level 4 — Why it was designed this way (senior/staff):**
tmux's client-server model is superior to screen's monolithic model because it cleanly separates session state from client display. In screen, the session and display are tightly coupled; nested screen sessions and window splitting are limited. tmux's use of Unix sockets means: multiple simultaneous clients to the same session (pair programming), complete client crash doesn't affect the session, and scripting via `tmux send-keys` and `tmux new-session -d` enables programmatic terminal automation. The `tmux-resurrect` plugin addresses the only remaining weakness (server restart loses sessions) by serialising session state to disk and restoring on server start — enabling persistent workflow across machine reboots.

---

### ⚙️ How It Works (Mechanism)

**Session management:**

```bash
# Create sessions
tmux                          # unnamed session
tmux new -s deployment        # named session
tmux new -s monitoring -d     # create detached

# List sessions
tmux ls
# deployment: 1 windows (created ...) [220x50]

# Attach
tmux attach                   # last session
tmux attach -t deployment     # specific session
tmux a -t deploy              # abbreviated

# Detach (inside tmux)
# Ctrl+b d

# Kill session
tmux kill-session -t deployment

# Kill all sessions
tmux kill-server
```

**Window and pane management (inside tmux):**

```
Prefix = Ctrl+b (default)

WINDOWS:
  Prefix c        - new window
  Prefix ,        - rename current window
  Prefix n/p      - next/previous window
  Prefix 0-9      - jump to window by number
  Prefix w        - list windows (interactive)
  Prefix &        - kill window

PANES:
  Prefix %        - split vertically (left/right)
  Prefix "        - split horizontally (top/bottom)
  Prefix ←→↑↓     - navigate between panes
  Prefix z        - zoom/unzoom current pane
  Prefix x        - kill pane
  Prefix q        - show pane numbers (jump by number)
  Prefix {/}      - swap pane position

COPY MODE (scroll + search):
  Prefix [        - enter copy mode
  / or ?          - search forward/back
  q               - exit copy mode
  Space           - begin selection
  Enter           - copy selection
  Prefix ]        - paste
```

**Essential `~/.tmux.conf` customisation:**

```bash
# ~/.tmux.conf

# Change prefix to Ctrl+a (like screen)
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# Enable mouse (click to switch panes, resize)
set -g mouse on

# Start windows and panes at 1, not 0
set -g base-index 1
setw -g pane-base-index 1

# Increase scrollback buffer
set -g history-limit 50000

# Enable 256 colors + true color
set -g default-terminal "screen-256color"
set-option -ga terminal-overrides ",xterm-256color:Tc"

# Reload config with Prefix r
bind r source-file ~/.tmux.conf \; display "Reloaded!"

# Split panes in current directory
bind % split-window -h -c "#{pane_current_path}"
bind '"' split-window -v -c "#{pane_current_path}"

# Status bar
set -g status-position bottom
set -g status-left "#[fg=green]#S "
set -g status-right " %H:%M %d-%b-%y"
```

**Scripting with tmux:**

```bash
#!/bin/bash
# Setup a development environment in tmux

SESSION="devenv"

# Kill existing session if it exists
tmux kill-session -t $SESSION 2>/dev/null

# Create new session with editor in first window
tmux new-session -d -s $SESSION -n editor -x 220 -y 50

# Window 1: editor
tmux send-keys -t $SESSION:editor "cd ~/myproject && vim" Enter

# Create window 2: servers
tmux new-window -t $SESSION -n servers

# Split window 2 into 3 panes
tmux send-keys -t $SESSION:servers \
  "cd ~/myproject && npm run dev" Enter
tmux split-window -h -t $SESSION:servers
tmux send-keys -t $SESSION:servers \
  "cd ~/myproject && docker-compose up" Enter
tmux split-window -v -t $SESSION:servers
tmux send-keys -t $SESSION:servers \
  "cd ~/myproject && tail -f logs/app.log" Enter

# Create window 3: test runner
tmux new-window -t $SESSION -n tests
tmux send-keys -t $SESSION:tests \
  "cd ~/myproject && npm test -- --watch" Enter

# Select editor window and attach
tmux select-window -t $SESSION:editor
tmux attach-session -t $SESSION
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  SSH disconnect and re-attach flow             │
└────────────────────────────────────────────────┘

 Developer SSH → server
       │
       ▼
 tmux new -s deploy
 ┌─────────────────────────────────────┐
 │ tmux server (background daemon)     │
 │ Session: deploy                     │
 │   Window 1: migration script        │
 │   python migrate.py  [RUNNING]      │
 │   Window 2: monitoring              │
 │   tail -f /var/log/app.log          │
 └─────────────────────────────────────┘
       │
       ▼
 Network drops / laptop closes
 SSH connection terminates
 SIGHUP → tmux client exits
       │
       ▼
 tmux server: still running
 python migrate.py: still running (child of server)
 Output buffered in scrollback (history-limit lines)
       │
       ▼
 Developer opens new laptop, SSHs back in
       │
       ▼
 tmux ls
 # deploy: 2 windows (created ...) [220x50] (detached)
       │
       ▼
 tmux attach -t deploy
 ┌─────────────────────────────────────┐
 │ Same session, same state            │
 │ Migration: 87% complete             │
 │ Scrollback shows output from while  │
 │ developer was disconnected          │
 └─────────────────────────────────────┘
```

---

### 💻 Code Example

**Example — Server maintenance script with tmux:**

```bash
#!/bin/bash
# Run maintenance task in tmux; provide monitoring

TASK_SESSION="maintenance-$(date +%Y%m%d-%H%M)"
LOG_FILE="/var/log/maintenance/$(date +%Y%m%d).log"
mkdir -p "$(dirname $LOG_FILE)"

# Check if tmux is available
if ! command -v tmux &>/dev/null; then
  echo "tmux not installed; running directly (unsafe)"
  exec "$@"
fi

# Create session with two panes
tmux new-session -d -s "$TASK_SESSION" -x 200 -y 50

# Main pane: run the task with logging
tmux send-keys -t "$TASK_SESSION" \
  "exec $@ 2>&1 | tee -a $LOG_FILE; echo 'Task complete: '\$?" \
  Enter

# Split: monitor log
tmux split-window -h -t "$TASK_SESSION"
tmux send-keys -t "$TASK_SESSION" \
  "tail -f $LOG_FILE" Enter

# Return focus to task pane
tmux select-pane -t "$TASK_SESSION":0.0

echo "Task running in tmux session: $TASK_SESSION"
echo "Attach: tmux attach -t $TASK_SESSION"
echo "Log: $LOG_FILE"
echo ""
echo "Attaching now (Ctrl+b d to detach)..."
sleep 1
tmux attach -t "$TASK_SESSION"
```

---

### ⚖️ Comparison Table

| Feature            | tmux                  | GNU screen     | nohup                  |
| ------------------ | --------------------- | -------------- | ---------------------- |
| Split panes        | Yes (flexible)        | Basic (2-pane) | No                     |
| Named sessions     | Yes                   | Yes            | No                     |
| Re-attach          | Yes                   | Yes            | No                     |
| Scripting API      | Excellent             | Limited        | No                     |
| Active development | Yes                   | Minimal        | N/A                    |
| Config file        | `~/.tmux.conf`        | `~/.screenrc`  | N/A                    |
| Pair programming   | Yes (shared sessions) | Yes            | No                     |
| Use today          | Preferred             | Legacy systems | Simple background jobs |

How to choose: tmux for all new work and development; screen if tmux unavailable; `nohup command &` only for truly simple background jobs that don't need monitoring or output review.

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                        |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Closing the terminal kills processes in tmux   | Closing the terminal window closes the tmux client; the tmux server and all processes continue running                                                         |
| `tmux kill-session` stops background processes | `kill-session` terminates the shell in tmux panes, which causes child processes to receive SIGHUP; processes may continue if they ignore SIGHUP or use `nohup` |
| tmux sessions survive server reboots           | The tmux server is a process; on reboot, all sessions are lost. Use `tmux-resurrect` plugin to save/restore layout.                                            |
| `screen` and `tmux` are interchangeable        | They have different keybindings, config formats, and feature sets; `screen` is largely unmaintained since 2015                                                 |
| Using tmux-in-tmux is fine                     | Nested tmux requires remapping the inner prefix key; accidental nesting causes confusing input routing                                                         |

---

### 🚨 Failure Modes & Diagnosis

**Cannot Re-attach: "no sessions"**

**Symptom:**
`tmux attach` returns "no sessions" despite having started a session earlier.

**Root Cause A:**
Server process was killed (system reboot, OOM, explicit kill-server).

**Root Cause B:**
Session was created as a different user (root vs your user); sockets are per-user.

**Diagnostic Commands:**

```bash
# List sessions for current user
tmux ls
ls /tmp/tmux-$(id -u)/

# List sessions for root (if you ran tmux as root)
sudo tmux ls
ls /tmp/tmux-0/

# Check if server is running
pgrep -a tmux

# Attach to root session from user shell
sudo tmux attach -t mysession
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Linux File System Hierarchy` — tmux uses `/tmp` for its socket (`/tmp/tmux-<uid>/`); config lives in `~/.tmux.conf`; understanding the role of these paths is helpful

**Builds On This (learn these next):**

- `SSH` — tmux solves the core SSH disconnect problem; understanding why SSH sessions send SIGHUP on disconnect is the motivation for tmux
- `Shell Scripting` — tmux's `send-keys` scripting enables powerful automation of terminal workflows

**Alternatives / Comparisons:**

- `nohup` — simple SSH-disconnect immunity for a single command; no re-attach, no panes, no sessions; for simple background tasks
- `GNU screen` — tmux predecessor; similar concept, less features; present on some legacy systems
- `byobu` — wrapper around tmux/screen with enhanced status bar; used on Ubuntu by default

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Terminal multiplexer: persistent sessions │
│              │ that survive SSH disconnect + split panes │
├──────────────┼───────────────────────────────────────────┤
│ START        │ tmux new -s name                          │
│ ATTACH       │ tmux attach -t name  (or: tmux a)         │
│ LIST         │ tmux ls                                   │
│ DETACH       │ Ctrl+b d (inside tmux)                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY COMBOS   │ Ctrl+b c  — new window                    │
│ (inside tmux)│ Ctrl+b %  — split vertical               │
│              │ Ctrl+b "  — split horizontal              │
│              │ Ctrl+b ↑↓←→ — navigate panes             │
│              │ Ctrl+b z  — zoom pane                     │
│              │ Ctrl+b [  — scroll mode                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Processes are children of the tmux server,│
│              │ not of SSH — SSH disconnect does nothing  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Shared whiteboard that stays after you   │
│              │ leave the room"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ tmux-resurrect → tmux plugins → zellij    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're setting up a shared tmux session for remote pair programming. Explain: (a) the exact Unix socket mechanism that allows two SSH users to share the same tmux session, (b) what user permissions are required and why, (c) the security implications of sharing a session (both users have equal control), and (d) how `tmate` (a tool built on tmux) extends this model for internet-accessible pair programming — specifically what the architectural difference is from running tmux on a shared server.

**Q2.** A DevOps engineer suggests running critical production services as background tmux sessions rather than as systemd services. Systematically compare these two approaches: process supervision (restart on crash), logging (persistence, rotation, structured output), boot persistence (starts automatically on reboot), security (running as non-root, resource limits), and observability (metrics collection, health checks) — concluding with when each approach is appropriate and what the correct tool for a production service is.
