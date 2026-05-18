---
id: LNX-016
title: "Pipes and Redirection (|, >, >>, <)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-015
used_by: LNX-024, LNX-026
related: LNX-015, LNX-026, LNX-043
tags: [pipes, redirection, shell, composition, stdin, stdout, filtering]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/lnx/pipes-and-redirection/
---

## TL;DR

Pipes (`|`) connect command output to command input, enabling
command composition. Redirection (`>`, `>>`, `<`) connects
commands to files. Together they form the Unix composition
model: build complex analysis from simple tools. `grep ERROR
app.log | sort | uniq -c | sort -rn | head -10` finds the
top 10 most common errors - no programming required.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-016 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | pipe, redirection, shell, composition, grep, awk, sort, uniq |
| **Prerequisites** | LNX-015 |

---

### The Problem This Solves

Data analysis, log investigation, and system administration require
combining tools: find errors, count them, sort by frequency, show
top results. Without pipes, you'd need: write output to temp file,
run next command reading that file, write to another temp file, repeat.
Pipes eliminate temp files and enable real-time streaming: output
flows directly from one command's output to the next's input.

---

### Textbook Definition

A **pipe** (`|`) connects the stdout of the left command to the
stdin of the right command. All commands in a pipeline run
simultaneously, with the kernel's pipe buffer coordinating flow.

**Redirection operators:**
- `>`: redirect stdout to file (truncate/create)
- `>>`: redirect stdout to file (append)
- `<`: redirect stdin from file
- `2>`: redirect stderr to file
- `2>&1`: merge stderr into stdout
- `&>`: redirect stdout+stderr to file (bash)
- `<<EOF`: here document (inline stdin)
- `<<<`: here string (single string as stdin)

---

### Understand It in 30 Seconds

```bash
# Count lines in a file:
wc -l /var/log/syslog

# Filter and count (pipe):
grep "ERROR" /var/log/app.log | wc -l

# Sort, deduplicate, count occurrences:
grep "ERROR" app.log | sort | uniq -c | sort -rn | head -10

# Redirect output to file:
ls /etc > etc_files.txt

# Append to file:
date >> timestamps.txt

# Use file as input:
sort < unsorted.txt > sorted.txt

# Combine: search file, save matches:
grep "WARN" app.log > warnings.txt

# tee: write to file AND pipe to next command:
ps aux | tee processes.txt | wc -l
# processes.txt has the full ps output; wc counts lines

# Discard output:
noisy-command > /dev/null 2>&1
```

---

### First Principles

**Why pipes are powerful:**
Each Unix tool does one thing: grep filters, sort sorts, uniq deduplicates,
wc counts, head/tail limits output. None of them need to know about
each other. Pipes compose them at runtime. This is the Open/Closed
principle at the OS level: tools are closed for modification but open
for composition.

**Pipeline execution:**
```bash
grep "ERROR" app.log | sort | uniq -c | sort -rn
```
The shell:
1. Creates 3 pipe buffers (between 4 commands)
2. Starts all 4 processes simultaneously
3. grep reads app.log, writes matches to pipe 1
4. sort reads pipe 1, writes sorted to pipe 2
5. uniq -c reads pipe 2, writes counted to pipe 3
6. sort -rn reads pipe 3, writes to terminal
Back-pressure: if sort's buffer fills, grep blocks until sort reads more.

**Redirection vs piping:**
```bash
cmd > file        # output goes to file (file = destination)
cmd < file        # input comes from file (file = source)
cmd1 | cmd2       # output of cmd1 is input of cmd2 (no file involved)
cmd1 | tee file | cmd2  # branching: file + cmd2 both get output
```

---

### Thought Experiment

You need to find the top 5 IP addresses causing the most 404 errors
in an nginx access log. Without pipes:

```bash
# Without pipes - 4 temp files and 5 commands:
grep "404" access.log > /tmp/404s.txt
awk '{print $1}' /tmp/404s.txt > /tmp/ips.txt
sort /tmp/ips.txt > /tmp/sorted.txt
uniq -c /tmp/sorted.txt > /tmp/counted.txt
sort -rn /tmp/counted.txt | head -5
rm /tmp/404s.txt /tmp/ips.txt /tmp/sorted.txt /tmp/counted.txt
```

With pipes - one line, no temp files, streaming:
```bash
grep "404" access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -5
```

Same result. The pipe version processes data as a stream: each line
flows through all 5 stages without writing to disk. For a 10GB log
file: pipe version uses kilobytes of memory (pipe buffers); temp file
version uses 10GB+ of disk space.

---

### Mental Model / Analogy

Pipes are like an **assembly line**:

```
Raw material (log file)
  |
  v
[Station 1: grep]  -> filters out non-ERROR lines
  | (pipe)
  v
[Station 2: sort]  -> arranges ERROR lines alphabetically
  | (pipe)
  v
[Station 3: uniq -c] -> counts consecutive duplicates
  | (pipe)
  v
[Station 4: sort -rn] -> reorders by count (highest first)
  | (pipe)
  v
[Station 5: head -10] -> takes only top 10
  |
  v
Output to terminal (or file)

Each station starts working immediately
When Station 1 produces output, Station 2 processes it right away
No waiting for Station 1 to finish all work first
```

---

### Gradual Depth - Five Levels

**Level 1:**
`|` connects stdout to stdin. `>` saves to file. `>>` appends. `<`
reads from file. `2>/dev/null` discards errors. Most log analysis
uses: grep | sort | uniq | head/tail.

**Level 2:**
`tee` branches a pipe: writes to file AND passes to stdout (for next
command). `xargs` converts stdin lines into command arguments.
`xargs -I {} cmd {}` uses each line as an argument. `find . -name "*.log" | xargs grep "ERROR"` = search for ERROR in all log files.

**Level 3:**
Process substitution: `<(cmd)` makes command output appear as a file.
`diff <(sort file1) <(sort file2)` compares sorted versions without
temp files. Here documents: `cat <<EOF\n...\nEOF` for multi-line
input in scripts. Named pipes (FIFOs) for persistent IPC: `mkfifo pipe;
producer > pipe & consumer < pipe`.

**Level 4:**
Subshells and pipe scope: variables set inside a pipe are in a subshell
and lost after the pipe ends. `while read line; do count=$((count+1)); done < file`
- the count variable IS available after (bash reads loop runs in current shell).
But: `cat file | while read line; do count=$((count+1)); done` - count is LOST
(while runs in a subshell). Always redirect with `< file` instead of
piping from cat.

**Level 5:**
In application development, pipes are the model for stream processing:
Java Streams API, Python generators, RxJava observables all implement
the same producer/consumer/transform pattern. Kafka topics are named
persistent pipes. Unix Domain Sockets are bidirectional pipes between
processes. Understanding shell pipes = understanding reactive stream
processing fundamentals.

---

### Code Example

**BAD - common pipeline mistakes:**
```bash
# BAD 1: useless use of cat (UUOC)
cat file.txt | grep "ERROR"
# grep can read files directly:
grep "ERROR" file.txt   # faster, no cat overhead

# BAD 2: losing variables in subshells
total=0
cat numbers.txt | while read n; do
    total=$((total + n))
done
echo $total   # prints 0! (total modified in subshell, not parent)

# BAD 3: not checking pipe exit codes
find /logs -name "*.log" | grep "ERROR" | wc -l
# If find fails (permission), output is 0 with no error indication

# BAD 4: overwriting file while reading it
sort file.txt > file.txt   # DESTROYS file!
# shell opens file.txt for writing FIRST (truncates to 0 bytes)
# then sort tries to read an empty file
```

**GOOD - correct pipeline patterns:**
```bash
# GOOD 1: grep reads files directly
grep -r "ERROR" /var/log/myapp/

# GOOD 2: redirect instead of cat pipe for variable scope
total=0
while read n; do
    total=$((total + n))
done < numbers.txt
echo $total   # correct!

# GOOD 3: use pipefail to catch failures
set -o pipefail
find /logs -name "*.log" | grep "ERROR" | wc -l
# Now: script fails if find fails

# GOOD 4: never overwrite while reading
sort file.txt > file_sorted.txt && mv file_sorted.txt file.txt

# GOOD 5: tee for debugging pipelines
grep "ERROR" app.log \
  | tee /tmp/errors.txt \
  | sort \
  | tee /tmp/sorted.txt \
  | uniq -c \
  | sort -rn

# GOOD 6: xargs for batch operations
find /old-logs -name "*.log" -mtime +30 | xargs rm -f
# Deletes logs older than 30 days

# GOOD 7: parallel processing with xargs
find . -name "*.txt" | xargs -P 4 -I{} gzip {}
# Compress files in parallel (4 concurrent processes)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Pipeline commands run sequentially" | All commands in a pipeline start simultaneously. They run in parallel, connected by pipe buffers. grep, sort, uniq, and head all run at the same time. |
| "`cat file \| cmd` and `cmd < file` are identical" | Nearly, but: piping from cat starts an extra cat process, uses a pipe buffer, and puts the while loop in a subshell (losing variable changes). `< file` is more efficient and avoids subshell issues. |
| "Pipes can pass binary data" | Pipes pass bytes, not text. `dd if=/dev/urandom bs=1M count=100 | gzip > random.gz` works - binary data piped through gzip. Text processing commands (grep, sed, awk) may misbehave on binary data. |
| "The pipe exit code is the first command's" | The exit code of a pipeline is the last command's exit code. `grep "x" file | wc -l`: if grep finds nothing (exit 1), wc still exits 0, so the pipeline exit code is 0. Use `set -o pipefail` to make the pipeline fail if any command fails. |
| "You can't pipe to commands that need file names" | `xargs` converts piped input to command arguments. `find . | xargs grep "pattern"` - grep receives filenames as arguments, not piped input. |

---

### Failure Modes & Diagnosis

**Variable lost after pipe:**
```bash
# Symptom: counter is 0 after the loop
count=0
cat numbers.txt | while IFS= read -r line; do
    count=$((count + 1))
done
echo "Count: $count"   # prints: Count: 0

# Cause: cat | while creates a subshell for the while loop
# Any variables set in subshell are lost when it exits

# Fix: use stdin redirection instead:
count=0
while IFS= read -r line; do
    count=$((count + 1))
done < numbers.txt
echo "Count: $count"   # prints: Count: N (correct!)

# Alternative (bash 4+): lastpipe option
set +m; shopt -s lastpipe
cat numbers.txt | while IFS= read -r line; do count=$((count+1)); done
echo $count  # works with lastpipe (last pipe segment in current shell)
```

**Pipeline failure not detected:**
```bash
# Symptom: pipeline "succeeds" even though early command failed
nonexistent_command | wc -l
echo $?   # 0 (wc succeeded with 0 input lines!)

# Diagnosis: check each command individually
nonexistent_command
echo $?   # 127 (command not found)

# Fix: enable pipefail in scripts
set -o pipefail
nonexistent_command | wc -l   # now exits with nonexistent_command's code
echo $?   # 127
```

**Security: privilege in pipes:**
```bash
# Risk: piping to commands that run with elevated privileges
# Can be exploited if the pipe source is user-controlled

# BAD: piping user input to bash
echo "$user_input" | bash   # NEVER DO THIS (command injection!)

# BAD: unvalidated URL in command
curl "$user_url" | bash     # arbitrary code execution risk

# GOOD: always validate input before using in pipelines
# Especially: never pipe untrusted data to sh, bash, eval, etc.
```

---

### Related Keywords

**Foundational:**
LNX-015 (Standard Streams)

**Builds on this:**
LNX-026 (grep), LNX-027 (sed), LNX-028 (awk),
LNX-024 (Shell Scripting)

**Related:**
LNX-043 (Regular Expressions), OSY-046 (IPC)

---

### Quick Reference Card

| Operator | Effect |
|----------|--------|
| `cmd1 \| cmd2` | Pipe stdout of cmd1 to stdin of cmd2 |
| `cmd > file` | Redirect stdout to file (overwrite) |
| `cmd >> file` | Redirect stdout to file (append) |
| `cmd < file` | Redirect stdin from file |
| `cmd 2> file` | Redirect stderr to file |
| `cmd > f 2>&1` | Redirect stdout+stderr to file |
| `cmd \| tee file` | Copy to file AND stdout |
| `cmd1 \| xargs cmd2` | Use cmd1 output as cmd2 arguments |
| `cmd <<< "text"` | Use text string as stdin |
| `diff <(cmd1) <(cmd2)` | Use command output as files |

**3 things to remember:**
1. Pipelines run all commands simultaneously (parallel), not sequentially
2. Variables set inside `cmd | while read` loops are lost (subshell) - use `while read < file` instead
3. Default exit code is from the LAST command - use `set -o pipefail` to catch failures anywhere in the pipeline

---

### Transferable Wisdom

The pipe concept is the foundation of stream processing:
- Java Stream API: `.filter().map().reduce()` - functional pipeline
- Apache Spark: transformation chain on RDDs/DataFrames
- Kafka Streams: filter, map, join, aggregate on event streams
- Unix pipe: same concept, implemented with processes

The key insight: each stage transforms a stream without knowing what
came before or after. This enables composition of independent, reusable
stages - the same architectural principle as microservices (each service
does one thing), functional programming (functions compose), and reactive
systems (operators transform streams).

**Backpressure** in shell pipes (fast producer blocks when pipe buffer
full) is the same mechanism in Reactive Streams spec (publishers block
or drop when subscriber is slow). Understanding shell pipe backpressure
= understanding reactive stream backpressure at a fundamental level.

---

### The Surprising Truth

The shell pipe `|` creates an in-memory byte channel with NO disk I/O
whatsoever. Processing a 10GB log file through a pipeline uses constant
memory (pipe buffers are 64KB on Linux). The data streams through and
is discarded once processed. But there's a subtle trap: `grep pattern bigfile | sort | head -10` - the `sort` command MUST buffer ALL grep output to memory (because it needs to see all input before it can sort). For a 10GB file with millions of matches, `sort` will use gigabytes of RAM or spill to disk. The `grep | head` without sort: constant memory. Adding `sort` after grep: O(n) memory. Lesson: sort in a pipeline is the "memory bomb" stage - always put it as late as possible, after other filters have reduced the data.

---

### Mastery Checklist

- [ ] Can construct multi-stage pipelines for log analysis
- [ ] Can redirect stdout, stderr independently and combined
- [ ] Can explain why variables are lost in `cat | while read` and how to fix it
- [ ] Can use tee to branch pipeline output
- [ ] Can explain why pipe commands run in parallel

---

### Think About This

1. You run `head -1 largefile.txt | wc -c`. The file is 10GB. How
   much of the file does `head -1` actually read? What happens to
   the read position after head exits? What signal does wc send when
   it receives head's output and head exits?

2. In a pipeline `cmd1 | cmd2 | cmd3`, if cmd2 crashes (segfault),
   what happens to cmd1 and cmd3? Are they also killed? What signal
   do they receive? How does the shell know the pipeline failed?

3. `find . -name "*.log" -exec grep "ERROR" {} \;` vs
   `find . -name "*.log" | xargs grep "ERROR"`. Both search for
   ERROR in all log files. Which is faster, and why? What are the
   limits of each approach?

**TYPE G:** Design a real-time log analysis pipeline for 200 nginx
access log files across 200 servers, with requirements: (1) detect
when error rate exceeds 1% in any 60-second window, (2) identify
the top 10 error-generating endpoints, (3) alert within 30 seconds
of threshold crossing, (4) process without writing to disk. How
would you implement this using shell pipeline concepts, and where
do you need to go beyond standard Unix pipes to a proper streaming
system?

---

### Interview Deep-Dive

**Foundational:**
Q: What does the `|` (pipe) operator do? How does it differ from `>`?
A: The pipe operator `|` connects the stdout of the left command to the stdin of the right command. Data flows between programs in memory (no disk). The right command starts immediately and processes data as the left command produces it. `>` redirects stdout to a FILE. The file must exist (or is created), everything is written to disk. Key differences: pipe is in-memory (faster, no disk usage), connects two running programs. `>` creates/overwrites a file, data is stored persistently. `cmd1 | cmd2` means cmd2 receives its input from cmd1. `cmd > file` means cmd's output is saved to disk. They compose: `cmd1 | cmd2 > file` pipes cmd1's output to cmd2 and saves cmd2's output to a file.

**Intermediate:**
Q: Why does this fail to update the count variable: `cat numbers.txt | while read n; do count=$((count+1)); done; echo $count`?
A: When a command appears to the right of a pipe, bash runs it in a subshell (a child process). Variables modified in the subshell (like count) exist only in that subshell's memory. When the subshell exits (the while loop finishes), those changes are discarded - the parent shell's count variable is unchanged. Solution: use stdin redirection instead of piping from cat: `while read n; do count=$((count+1)); done < numbers.txt`. Now the while loop runs in the current shell, not a subshell, and count persists. Alternative: use bash's process substitution or the `lastpipe` option. This is a subtle but common bash scripting bug that leads to counters always being zero after loops.

**Expert:**
Q: In a pipeline of 5 commands, command 3 runs out of memory and crashes. Explain exactly what happens to commands 1, 2, 4, and 5.
A: When command 3 exits abnormally, its read end (stdin pipe from cmd2) and write end (stdout pipe to cmd4) are closed. What happens to each: (1) cmd2 is still running and writing to its stdout pipe. But cmd3's read end is now closed. When cmd2 tries to write to the full pipe buffer, the kernel sends SIGPIPE to cmd2 (broken pipe). cmd2 exits. Then cmd1 also receives SIGPIPE when it tries to write to cmd2's (now closed) stdin. (2) cmd4 is still running, trying to read from its stdin pipe. But cmd3's write end is now closed. cmd4 gets EOF on its stdin and exits normally (reads 0 bytes). cmd5 similarly gets EOF from cmd4's early exit. (3) The shell collects exit codes: cmd3's non-zero exit code is captured. With `set -o pipefail`, the pipeline's exit code is the rightmost non-zero exit code. Without pipefail, only cmd5's exit code matters. SIGPIPE default action is to terminate the process silently - many commands are written to handle this gracefully. Java applications that ignore SIGPIPE need to handle the broken pipe IOException instead.
