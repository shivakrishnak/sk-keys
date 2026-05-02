---
layout: default
title: "find / xargs"
parent: "Linux"
nav_order: 142
permalink: /linux/find-xargs/
number: "0142"
category: Linux
difficulty: ★★☆
depends_on: Linux File System Hierarchy, Shell (bash, zsh), Pipes and Redirection
used_by: Shell Scripting, CI/CD, grep / awk / sed
related: grep / awk / sed, Shell Scripting, stdin / stdout / stderr
tags:
  - linux
  - os
  - internals
  - intermediate
---

# 142 — find / xargs

⚡ TL;DR — `find` locates files by any attribute (name, size, age, permissions); `xargs` feeds those results as arguments to another command — together they batch-process arbitrary collections of files.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to: delete all `.log` files older than 7 days in `/var/log`, change permissions on every `.sh` file in a project directory, or run `grep` on only the Java source files in a 10,000-file repository. Without `find`, you must manually list directories, filter by hand, and run commands one-by-one.

**THE BREAKING POINT:**
A disk cleanup script uses `rm /var/log/*.log` — but the glob fails silently when no files match, and doesn't recurse into subdirectories. Two weeks later the disk is full because log files in nested directories were never deleted. The script gave no error; it just did nothing useful.

**THE INVENTION MOMENT:**
This is exactly why `find` was created. It traverses the entire directory tree, applies any combination of filters (name, age, size, permissions, type), and executes commands on every matching file — recursively, reliably, with no glob limitations.

---

### 📘 Textbook Definition

`find` is a command that traverses the filesystem tree from a starting point, evaluating a boolean expression (built from predicates like `-name`, `-mtime`, `-size`, `-type`) against each entry, and executing an action (print, delete, execute command) on matching entries. `xargs` reads items from stdin (typically file paths from `find`) and executes a specified command with those items as arguments, batching them to avoid "argument list too long" errors and optionally parallelising execution.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`find` walks the filesystem and selects files; `xargs` gives those files to another command.

**One analogy:**

> `find` is a warehouse manager who walks every aisle and shelf, picking items that match a description (older than 30 days, weighs over 5 kg, in aisle B). `xargs` is the forklift operator who takes the manager's list and moves all matching items to the truck — but loads them in efficient batches rather than one trip per item.

**One insight:**
`xargs` is critical because shell argument lists have a hard size limit (`ARG_MAX`, typically 2 MB). Running `rm $(find . -name '*.tmp')` crashes with "Argument list too long" for large result sets. `xargs` automatically batches the arguments, calling the command multiple times in small groups if needed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. File selection must be decoupled from the action — the same selection logic works with any command.
2. Filesystem traversal must handle arbitrarily deep directory trees.
3. Command argument lists have a system size limit; batching is required for large result sets.

**DERIVED DESIGN:**
`find` implements a DFS (depth-first search) traversal of the directory tree. At each node it evaluates a predicate expression tree (AND/OR/NOT of individual tests) against the node's metadata without reading file content. This makes it very fast for attribute-based searches.

`xargs` buffers its stdin input and constructs command invocations of up to `ARG_MAX` bytes each, calling the target command multiple times if needed. The `-0` flag (used with `find -print0`) handles filenames containing spaces or newlines by using NUL as delimiter instead of newline/whitespace — this is critical for correctness in production scripts.

**THE TRADE-OFFS:**
**Gain:** Reliable recursive file selection with complex multi-criteria filters; works with any command; handles arbitrary file counts.
**Cost:** `find` expression syntax is complex and easy to mis-order; `-exec {} +` vs `-exec {} \;` have different performance and error behaviour; xargs parallelism (`-P`) can overload the target system.

---

### 🧪 Thought Experiment

**SETUP:**
A log rotation script needs to delete all `.log` files older than 7 days across a nested directory structure with 10,000 files, including some with spaces in their names.

**WHAT HAPPENS WITHOUT find/xargs:**

```bash
rm /var/log/app/*.log  # fails to recurse into subdirs
# Files with spaces: rm /var/log/app/my app.log → two args!
# Argument list too long if shell glob matches >ARG_MAX bytes
```

Result: some files deleted, some not, silent partial success.

**WHAT HAPPENS WITH find/xargs:**

```bash
find /var/log/app -name "*.log" -mtime +7 -print0 | \
  xargs -0 rm -f
```

find walks all subdirectories, `-mtime +7` selects files older than 7 days, `-print0` uses NUL delimiter for safe handling of spaces, `xargs -0` passes them to `rm` in efficient batches. All matching files deleted, correctly, regardless of names or count.

**THE INSIGHT:**
`find -print0 | xargs -0` is the only reliable way to handle arbitrary filenames (including spaces, newlines, special characters) in shell pipelines. Any pipeline using newline-delimited filenames will silently misprocess filenames with spaces.

---

### 🧠 Mental Model / Analogy

> `find` is a detective who searches every room in a building using a specific profile: "find me anyone over 40, wearing a red hat, who has been here more than 30 minutes." The detective creates a list. `xargs` is the bouncer who takes that list and escorts each person to the exit — but walks them out in groups of 20 (batches) rather than one at a time.

- "Every room in the building" → recursive filesystem traversal
- "Over 40, red hat, 30+ minutes" → `-type f -name '*.log' -mtime +7`
- "Creates a list" → `find` outputs matching paths
- "Bouncer with batches" → xargs batches paths into command invocations

Where this analogy breaks down: xargs can run multiple bouncer instances in parallel (`-P N`) — multiplying throughput for independent operations like file compression or checksumming.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`find` searches for files matching criteria you specify — name, age, size, file type — throughout entire directory trees, including subdirectories. `xargs` takes a list of things (usually filenames from find) and passes them as arguments to another command.

**Level 2 — How to use it (junior developer):**
`find . -name "*.java"` finds all Java files under current directory. `find /tmp -mtime +7 -delete` deletes files older than 7 days. `find . -type f -name "*.py" | xargs grep "TODO"` searches all Python files for TODO. The `-type f` flag restricts to files only (not directories). Use `find ... -print0 | xargs -0 command` when filenames might contain spaces.

**Level 3 — How it works (mid-level engineer):**
`find` evaluates predicates in left-to-right order with short-circuit evaluation (like `&&`). Put cheap tests first (`-type`, `-name`) before expensive ones (`-mtime`, `-size`, `-exec`) to avoid unnecessary stat() calls. `-exec command {} \;` runs the command once per file; `-exec command {} +` (or `xargs`) batches multiple files into one command invocation — dramatically faster for large result sets. `find -maxdepth 1` restricts to current directory only (no recursion).

**Level 4 — Why it was designed this way (senior/staff):**
find's predicate expression evaluates to true/false per file — it is a mini boolean calculator applied to filesystem metadata. The design decision to make `-exec {} +` automatically batch was driven by the Unix V7 era where spawning a process per file was expensive. Modern inotify-based tools (watchexec, fswatch) complement find by providing real-time event detection instead of full-tree scans — important for large monorepos where `find . -name "*.js"` takes seconds. xargs `-P` parallel mode is underused: it can compress 100 files with gzip in parallel, using all CPU cores, without writing a single line of Python.

---

### ⚙️ How It Works (Mechanism)

**find predicate evaluation:**

```
┌─────────────────────────────────────────────┐
│  find /var/log -type f -name "*.log"        │
│       -mtime +7 -size +1M                  │
└─────────────────────────────────────────────┘

For each filesystem entry:
  1. lstat() — get metadata (type, size, timestamps)
  2. Evaluate predicates left to right:
     -type f    → is it a regular file? (NO → skip)
     -name *.log→ does name match? (NO → skip)
     -mtime +7  → older than 7 days? (NO → skip)
     -size +1M  → larger than 1MB? (NO → skip)
  3. All true → apply action (-print/-delete/-exec)
```

**Essential find predicates:**

```bash
# By name (glob patterns)
find . -name "*.log"         # case-sensitive
find . -iname "*.Log"        # case-insensitive

# By type
find . -type f               # regular files
find . -type d               # directories
find . -type l               # symbolic links

# By age (mtime = last modified)
find . -mtime -7             # modified in last 7 days
find . -mtime +30            # modified > 30 days ago
find . -newer reference.txt  # newer than a reference file

# By size
find . -size +100M           # larger than 100 MB
find . -size -1k             # smaller than 1 KB
find . -empty                # zero-byte files

# By permissions
find . -perm 644             # exact permission
find . -perm /u+x            # user has execute bit

# By owner
find . -user apache          # owned by user apache
find . -group www-data       # owned by group

# Logical operators
find . -name "*.log" -o -name "*.tmp"   # OR
find . -not -name "*.java"             # NOT
find . -name "*.js" ! -path "*/node_modules/*" # NOT path

# Depth limiting
find . -maxdepth 2           # don't recurse deeper than 2
find . -mindepth 1           # skip the starting directory
```

**Actions:**

```bash
# Print (default action)
find . -name "*.log" -print

# Delete — CAREFUL: permanent
find /tmp -mtime +7 -delete

# Execute once per file
find . -name "*.sh" -exec chmod +x {} \;

# Execute once with all files batched (faster)
find . -name "*.log" -exec gzip {} +

# Safer: use xargs with NUL delimiter
find . -name "*.log" -print0 | xargs -0 gzip
```

**xargs key options:**

```bash
# Basic usage
find . -name "*.log" | xargs grep "ERROR"

# NUL-delimited (handles spaces in names)
find . -name "*.log" -print0 | xargs -0 grep "ERROR"

# Parallel execution (4 workers)
find . -name "*.jpg" -print0 | \
  xargs -0 -P 4 -I {} convert {} {}.webp

# Limit arguments per command invocation
find . -name "*.log" | xargs -n 100 rm

# Prompt before each execution
find . -name "*.bak" | xargs -p rm

# Substitute placeholder for each item
find . -name "*.csv" -print0 | \
  xargs -0 -I{} cp {} /backup/{}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  LOG CLEANUP: delete old logs               │
└─────────────────────────────────────────────┘

 Cron job triggers at 2am
       │
       ▼
find /var/log/app \
  -type f -name "*.log" -mtime +30  ← YOU ARE HERE
       │  matches N files (any N)
       ▼
-print0  (NUL-delimited output)
       │
       ▼
xargs -0 -P 4 gzip
       │  compresses in 4 parallel workers
       ▼
Compressed files remain for archival
       │
       ▼
find /var/log/app \
  -name "*.log.gz" -mtime +90 -delete
       │
       ▼
Old archives permanently deleted
```

**FAILURE PATH:**
`find` encounters a directory it cannot read (permission denied) → prints error to stderr but continues (exits 1) → xargs never receives those files → silent partial completion. Use `find ... 2>/dev/null` to suppress permission errors if you don't own some directories.

**WHAT CHANGES AT SCALE:**
For repositories with millions of files, `find` can take minutes just to traverse the directory tree (lstat() per file is expensive at scale). Faster alternatives: `fd` (parallelised, respects .gitignore), `locate` (pre-indexed DB, near-instant but stale), or inotify-based event systems for real-time file monitoring without scanning.

---

### 💻 Code Example

**Example 1 — BAD: unsafe glob, no recursion:**

```bash
# BAD — glob expands in shell (ARG_MAX limit)
#       no recursion, no space safety
rm /var/log/*.log

# Also BAD — newlines in filenames break xargs
find . -name "*.log" | xargs rm
```

**Example 1 — GOOD: NUL-safe, recursive, batched:**

```bash
# GOOD — NUL delimiter, recursive, handles any filename
find /var/log -name "*.log" -mtime +30 -print0 | \
  xargs -0 rm -f
```

**Example 2 — Find and process Java files:**

```bash
# Count lines in all Java files, show total
find src/ -name "*.java" -type f -print0 | \
  xargs -0 wc -l | tail -1

# Find Java files modified today, run checkstyle
find src/ -name "*.java" -newer yesterday.marker \
  -print0 | \
  xargs -0 java -jar checkstyle.jar -c style.xml
```

**Example 3 — Parallel image conversion:**

```bash
# Convert all PNG images to WebP using 8 CPU cores
find images/ -name "*.png" -print0 | \
  xargs -0 -P 8 -I{} \
    convert {} "$(dirname {})/$(basename {} .png).webp"

# -P 8: 8 parallel workers
# -I{}: replace {} with each filename
```

**Example 4 — Safe batch delete with confirmation:**

```bash
# Dry run: see what would be deleted
find /tmp -name "*.tmp" -mtime +1 -print

# Count matches first
find /tmp -name "*.tmp" -mtime +1 | wc -l

# Delete with confirmation per file (small sets)
find /tmp -name "*.tmp" -mtime +1 \
  -ok rm {} \;
# -ok prompts "< rm ... /tmp/file.tmp>?" before each
```

---

### ⚖️ Comparison Table

| Tool         | Recursion   | Speed     | Respects .gitignore | Best For                            |
| ------------ | ----------- | --------- | ------------------- | ----------------------------------- |
| **find**     | Yes         | Medium    | No                  | Production scripts, complex filters |
| fd           | Yes         | Fast      | Yes                 | Developer workflows, large repos    |
| locate       | Pre-indexed | Very fast | No                  | Quick name lookups (stale DB)       |
| glob (`**/`) | Limited     | Fast      | No                  | Simple shell one-liners             |
| rg (ripgrep) | Yes         | Fastest   | Yes                 | Searching file _contents_           |

How to choose: use `find` in production scripts (universal, no extra install); use `fd` in development for speed and .gitignore awareness; use `locate` for instant interactive name search (run `updatedb` to refresh).

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                      |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------- |
| `find . -name "\*.log"                        | xargs rm` is safe                                                                                                            | Filenames with spaces will be split into multiple arguments; always use `-print0 | xargs -0` |
| `find -mtime 7` means "exactly 7 days old"    | It means "between 7 and 8 days old" (integer days); use `-mtime +7` for "older than 7 days"                                  |
| `-exec {} \;` and `-exec {} +` are equivalent | `\;` runs the command once per file (N invocations); `+` batches all files into as few invocations as possible (much faster) |
| `find -delete` is recoverable                 | `-delete` permanently removes files with no trash/recycle bin; always dry-run with `-print` first                            |
| xargs is only for find                        | xargs works with any newline- or NUL-delimited stdin: `cat file_list.txt \| xargs -0 process`                                |

---

### 🚨 Failure Modes & Diagnosis

**"Argument list too long" Error**

**Symptom:**
`rm $(find . -name "*.tmp")` fails with "bash: /bin/rm: Argument list too long".

**Root Cause:**
Shell expands `$(...)` and passes all paths as a single command line, exceeding `ARG_MAX` (~2 MB on Linux).

**Diagnostic Command:**

```bash
# Check ARG_MAX on your system
getconf ARG_MAX

# Count files to see if you'll hit the limit
find . -name "*.tmp" | wc -l
```

**Fix:**

```bash
# GOOD — xargs handles batching automatically
find . -name "*.tmp" -print0 | xargs -0 rm -f
# Or simpler:
find . -name "*.tmp" -delete
```

**Prevention:**
Never use `$(find ...)` expansion directly as command arguments; always pipe through xargs.

---

**find -delete Removes More Than Expected**

**Symptom:**
`find . -type d -name tmp -delete` deletes directories and their contents unexpectedly.

**Root Cause:**
`-delete` on a directory deletes it only if empty; if combined with `-type d` without `-empty`, it errors on non-empty dirs — but if used carelessly without `-type` restriction, it deletes matching files AND matching directory trees.

**Diagnostic Command:**

```bash
# ALWAYS dry-run first with -print
find . -type d -name tmp -print
# Verify output before replacing -print with -delete
```

**Fix:**

```bash
# Delete empty tmp directories only
find . -type d -name tmp -empty -delete

# Delete entire tmp directories including contents
find . -type d -name tmp \
  -exec rm -rf {} + 2>/dev/null
```

**Prevention:**
Treat `find -delete` and `find -exec rm` as irreversible operations; always run with `-print` first.

---

**Permissions Denied on Some Directories**

**Symptom:**
`find /var/log` outputs errors mixed with results: "find: '/var/log/private': Permission denied".

**Root Cause:**
The running user lacks read permission on some directories; find reports this to stderr and continues.

**Diagnostic Command:**

```bash
# Separate errors from results
find /var/log -name "*.log" 2>/dev/null  # suppress errors
find /var/log -name "*.log" 2>&1 1>/dev/null  # errors only
```

**Fix:**

```bash
# Run with sudo if you need those directories
sudo find /var/log -name "*.log" -mtime +7 -delete

# Or suppress permission errors if they're expected
find /var/log -name "*.log" -mtime +7 \
  -delete 2>/dev/null
```

**Prevention:**
Run find as root for system directories; use sudo only for the find command, not the entire script.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Linux File System Hierarchy` — find traverses the filesystem; knowing FHS helps target searches correctly
- `Shell (bash, zsh)` — find is a shell command; output is piped to other shell commands
- `Pipes and Redirection` — the pipe `|` and xargs combination is the core usage pattern

**Builds On This (learn these next):**

- `Shell Scripting` — find + xargs is a fundamental pattern in automated maintenance scripts
- `CI/CD` — pipelines use find to locate build artifacts, source files, and test outputs
- `grep / awk / sed` — commonly paired with find to filter file contents after find selects the files

**Alternatives / Comparisons:**

- `fd` — faster modern find replacement with .gitignore support and simpler syntax
- `locate/updatedb` — pre-indexed name search (instant but stale); no content/attribute filters
- `glob patterns` — sufficient for simple same-directory file matching without recursion

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ find: recursive filesystem search by      │
│              │ attribute; xargs: batched arg passing     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shell globs don't recurse, can't filter   │
│ SOLVES       │ by age/size, hit ARG_MAX limit            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Always use -print0 | xargs -0 to safely   │
│              │ handle filenames with spaces              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Log cleanup, batch file processing,       │
│              │ searching source trees by attribute       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Content search (use grep/rg); real-time   │
│              │ monitoring (use inotify/fswatch)          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Powerful filtering vs complex syntax;     │
│              │ -exec {} + vs \; for performance          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "find selects files from millions;        │
│              │  xargs delivers them in safe batches"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ fd → GNU parallel → inotifywait          │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A nightly cron job runs `find /data -name "*.parquet" -mtime +90 -delete` to remove old data files. The job runs as root. A developer accidentally creates a symlink: `/data/current → /critical-system-data/`. Trace what `find` does when it encounters this symlink, what gets deleted, and what flag you would add to `find` to prevent this scenario. Does the answer change if it's a directory bind-mount instead of a symlink?

**Q2.** `xargs -P 8` runs 8 parallel workers processing files. Each worker calls `ffmpeg` to transcode a video. After 10 minutes, 3 workers have crashed with OOM errors, 5 are still running, and 2 of the original files are left in a partially-transcoded state. Explain how xargs handles worker failures, what state the output files are in, and redesign the pipeline so that partial failures don't corrupt the output.
