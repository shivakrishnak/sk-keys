---
id: LNX-015
title: "Standard Streams (stdin, stdout, stderr)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006
used_by: LNX-016, LNX-024, LNX-036
related: LNX-016, LNX-036, LNX-006
tags: [stdin, stdout, stderr, streams, file-descriptors, io, redirection]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/lnx/standard-streams/
---

## TL;DR

Every Linux process has three standard streams: stdin (fd=0,
keyboard input), stdout (fd=1, normal output), stderr (fd=2,
error output). Programs read from stdin and write to stdout/stderr
without caring if it's a terminal, file, or pipe. This abstraction
enables composability: `program1 | program2` connects stdout of
program1 to stdin of program2. In containers: stdout+stderr are
captured as container logs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-015 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | stdin, stdout, stderr, file descriptors, fd, streams, Unix philosophy |
| **Prerequisites** | LNX-006 |

---

### The Problem This Solves

Programs need input and need to output results and errors. But
they shouldn't need to know whether they're reading from a
keyboard, a file, or another program's output. The standard
streams abstraction: every program gets three pre-opened "files"
(0, 1, 2) that work the same way regardless of what's connected
to them. This enables the Unix composition model: tools that do
one thing well, composed with pipes.

---

### Textbook Definition

**Standard input (stdin)**: file descriptor 0. Default: keyboard.
Programs read input from here. Closed (EOF) = no more input.

**Standard output (stdout)**: file descriptor 1. Default: terminal.
Programs write normal output here. Buffered (typically line-buffered
when connected to a terminal, fully-buffered when redirected to file).

**Standard error (stderr)**: file descriptor 2. Default: terminal
(same as stdout, but separate stream). Programs write error messages,
warnings, and diagnostics here. Always unbuffered (or line-buffered)
so errors appear immediately.

A **file descriptor** is a small integer (index into the process's
file descriptor table) that refers to an open file/pipe/socket/etc.
fd 0, 1, 2 are opened by the kernel before the process starts.

---

### Understand It in 30 Seconds

```bash
# Redirecting stdout:
ls /etc > file_list.txt     # stdout goes to file
ls /etc >> file_list.txt    # append stdout to file

# Redirecting stderr:
command 2> errors.txt       # stderr goes to file
command 2>/dev/null         # discard errors

# Redirect both:
command > output.txt 2>&1   # stdout + stderr to same file
command &> output.txt       # shorthand (bash only)

# Reading from file as stdin:
wc -l < file_list.txt       # stdin from file

# Pipes (connect stdout of one to stdin of next):
ls /etc | wc -l             # count files in /etc
ps aux | grep java          # find java processes
cat access.log | grep ERROR | wc -l  # count errors

# /dev/null - the null device (discard anything written):
command > /dev/null 2>&1    # discard all output
command 2>/dev/null         # discard only errors

# Mixing stdout and stderr:
ls /exists /notexist > out.txt 2> err.txt
# out.txt: /exists listing
# err.txt: "ls: /notexist: No such file or directory"
```

---

### First Principles

**File descriptors are just indices:**
```
Process file descriptor table:
  fd 0 -> open file (stdin):  keyboard / pipe / file
  fd 1 -> open file (stdout): terminal / pipe / file
  fd 2 -> open file (stderr): terminal / file

When you run: ls > out.txt
  Shell: opens out.txt, gets fd 3
  Shell: dup2(3, 1): makes fd 1 point to out.txt
  Shell: closes fd 3
  Shell: fork+exec ls
  ls: writes to fd 1 (which is now out.txt, not terminal)
  ls has no idea it's writing to a file, not a terminal
```

**Why separate stderr:**
If errors went to stdout, you couldn't use `cmd | nextcmd` reliably
because nextcmd would receive both data and errors intermixed. With
stderr separate: stdout contains only clean data (parseable), stderr
contains human-readable diagnostics. This is why `grep ERROR log |
wc -l` works correctly - wc counts only clean grep output, not
grep's error messages about unreadable files.

---

### Thought Experiment

Consider: `grep "ERROR" /var/log/app/*.log | sort | uniq -c | sort -rn | head -20`

This pipeline:
1. grep searches all .log files for "ERROR" -> writes matches to stdout
2. sort sorts the matches alphabetically -> writes to stdout
3. uniq -c counts consecutive duplicates -> writes "count line" to stdout
4. sort -rn sorts by count (highest first) -> writes to stdout
5. head -20 takes first 20 lines -> writes to stdout (which is your terminal)

Each program reads from stdin and writes to stdout without knowing
what's before or after it. This is the Unix philosophy: small tools,
composed via streams. The entire analysis pipeline is built from
programs that existed before this specific use case was imagined.

---

### Mental Model / Analogy

Standard streams are like **tubes in a building:**

```
Every room (process) has three tubes pre-installed:
  
  Tube 0 (stdin): INTAKE tube
    By default: connected to keyboard input
    Can be connected to: file, previous room's output tube
    
  Tube 1 (stdout): OUTPUT tube
    By default: connected to your screen display
    Can be connected to: file, next room's intake tube
    
  Tube 2 (stderr): ALARM tube
    By default: also connected to your screen display
    (separate so alarms don't mix with normal output)
    
  /dev/null = the trash chute
    Anything put in it vanishes
    
  Piping: connect Room A's output tube directly to Room B's intake tube
  (The rooms don't know they're connected - they just use their tubes)
```

---

### Gradual Depth - Five Levels

**Level 1:**
stdout = normal output. stderr = errors. `>` redirects stdout to file.
`2>` redirects stderr. `|` pipes stdout to next command. `2>/dev/null`
discards error messages.

**Level 2:**
`2>&1` redirects stderr to stdout. Order matters: `cmd > file 2>&1`
(stderr to where stdout is going = file) vs `cmd 2>&1 > file` (stderr
to where stdout CURRENTLY goes = terminal, THEN redirect stdout to file).
Process substitution: `diff <(cmd1) <(cmd2)` - both outputs as "files."

**Level 3:**
Named pipes (FIFOs): `mkfifo /tmp/mypipe`. Used for inter-process
communication between programs that don't know about each other.
`echo data > /tmp/mypipe &; cat /tmp/mypipe` - blocking write/read.
Here strings: `wc -w <<< "hello world"` (string as stdin without
creating a file). Here documents: `cat <<EOF...EOF` for multi-line stdin.

**Level 4:**
Buffering details: stdout is line-buffered when connected to a terminal
(flushes on newline), fully-buffered when connected to a pipe/file
(flushes when buffer is full - typically 8KB). This causes the "grep
works in terminal but output delayed in pipe" problem. Fix: `stdbuf -oL`
forces line-buffered. In Java: System.out.flush() or use PrintWriter.
stderr is always unbuffered (writes immediately).

**Level 5:**
In containers (Docker/Kubernetes): stdout and stderr of PID 1 are
captured by the container runtime and stored as container logs. `docker
logs`, `kubectl logs` retrieve them. Design principle: applications
should write logs to stdout (JSON format), not to files. The container
platform aggregates them. This is the 12-factor app log principle.
Implications: no log rotation needed in the app; log aggregation (Loki,
ELK) handles collection; structured logs (JSON) enable filtering.

---

### Code Example

**BAD - mixing stdout and stderr incorrectly:**
```bash
# BAD 1: discards both output and errors silently
command > /dev/null   # only stdout discarded, stderr still shows
# If you want to discard everything:
command > /dev/null 2>&1

# BAD 2: wrong order of redirections
command 2>&1 > output.txt
# stderr goes to fd 1's CURRENT destination (terminal)
# THEN stdout goes to output.txt
# Result: stdout in file, stderr on terminal (NOT what you wanted)

# BAD 3: running grep and checking exit code without capturing
ls /nonexistent | grep "something"  # grep always exits 0
# because: ls writes error to stderr, nothing to stdout
# grep reads empty stdin, finds nothing, exits with error
# BUT: piped exit code is LAST command's exit code
echo $?  # might show 1 (grep's exit code for no match)
```

**GOOD - correct stream handling:**
```bash
# GOOD 1: correct redirect order (stderr to same file as stdout)
command > output.txt 2>&1
# Read: redirect stdout to file, THEN redirect stderr to stdout
# Both end up in output.txt

# GOOD 2: separate stdout and stderr for analysis
myapp > output.log 2> error.log
# Allows: wc -l error.log (count errors without parsing output)

# GOOD 3: tee - write to file AND display on terminal
myapp 2>&1 | tee app.log
# Shows output in real time AND saves to file

# GOOD 4: check exit codes in pipeline with pipefail
set -o pipefail   # in scripts: pipeline fails if any command fails
find /logs -name "*.log" | grep "error" | wc -l
# Without pipefail: wc reports 0 even if find fails (permission denied)
# With pipefail: script fails if find, grep, or wc fails

# GOOD 5: explicit stdin for interactive commands in scripts
echo "yes" | apt install -y nginx 2>&1
# OR: use the -y flag and redirect stdin from /dev/null:
apt install -y nginx < /dev/null 2>&1
```

**Java and standard streams:**
```java
// BAD: mixing application logs with system.out
System.out.println("Starting application...");  // goes to stdout
System.err.println("Configuration loaded");     // goes to stderr
// Random mix: no structure, hard to parse in log aggregation

// GOOD: use proper logging framework (outputs to stdout in containers)
// logback.xml for container deployment:
// <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
//   <encoder><pattern>%d{"dd-MM-yyyy HH:mm:ss.SSS"} %-5level [%thread] %logger - %msg%n</pattern></encoder>
// </appender>
// JSON encoder for structured logs:
// <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>

// Reading from stdin in Java (for pipes):
import java.util.Scanner;
Scanner sc = new Scanner(System.in);  // reads from stdin
while (sc.hasNextLine()) {
    String line = sc.nextLine();
    // process line
}
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "stderr goes to a log file" | By default stderr goes to the TERMINAL, same as stdout. They appear in the same terminal but are different streams. `command > file` redirects only stdout; errors still appear in terminal. |
| "`2>&1` means redirect to fd 2 then to fd 1" | `2>&1` means "redirect fd 2 to wherever fd 1 currently points." The `&` indicates fd number. Order matters: the assignment is evaluated left to right. |
| "Piping captures stderr too" | `cmd1 | cmd2` only pipes stdout. stderr still goes to the terminal. To also pipe stderr: `cmd1 2>&1 | cmd2` (merge stderr into stdout first). |
| "stdout is always printed immediately" | When connected to a pipe or file, stdout is buffered (typically 8KB). Output may not appear until the buffer fills. This causes confusing delays in pipelines. Use stdbuf or explicit flush calls. |
| "`> file` and `>> file` are the same" | `>` truncates (overwrites) the file before writing. `>>` appends. Running a script with `> logfile` twice will only keep the second run's output. Use `>>` to accumulate logs. |

---

### Failure Modes & Diagnosis

**Output appears out of order in pipeline:**
```bash
# Symptom: expected ordered output but some lines appear late or mixed
./generate-data.sh | process-data.sh

# Cause: generate-data.sh buffers stdout (8KB)
# process-data.sh starts and waits; generate writes to buffer;
# when buffer full, all 8KB flushes at once -> batch processing

# Diagnosis: check if output is line-by-line or in chunks
./generate-data.sh | pv -l   # pv shows transfer rate

# Fix: disable buffering
stdbuf -oL ./generate-data.sh | process-data.sh
# stdbuf -oL: set stdout to line-buffered mode

# For Python scripts: python3 -u ./generate.py (unbuffered)
# For Java: System.out.flush() after each println
```

**Pipeline hides errors:**
```bash
# Symptom: command fails silently in pipeline
find /logs -name "*.log" 2>/dev/null | wc -l
# Shows 0 but you think there should be log files
# Cause: find failed (permission denied) - error silently discarded

# Diagnosis: run without /dev/null redirect first
find /logs -name "*.log"
# Shows: "find: /logs: Permission denied"

# Fix: either fix permissions or capture error:
find /logs -name "*.log" 2>find_errors.txt | wc -l
cat find_errors.txt   # see what failed
```

**Security: sensitive data in stderr/stdout:**
```bash
# Risk: passwords printed to stdout go into container logs
# In Kubernetes: anyone with 'kubectl logs' access sees them

# BAD: logging database URL with password
echo "Connecting to: $DB_URL"   # includes password in URL!
# Goes to stdout -> container log -> log aggregation system

# GOOD: log without sensitive parts
echo "Connecting to database at $DB_HOST:$DB_PORT/$DB_NAME"
# Never log: passwords, tokens, private keys

# Audit: check if secrets are in your logs:
kubectl logs myapp-pod | grep -i "password\|token\|secret\|key"
```

---

### Related Keywords

**Foundational:**
LNX-006 (Terminal), LNX-014 (Process Basics)

**Builds on this:**
LNX-016 (Pipes and Redirection), LNX-036 (File Descriptors),
LNX-024 (Shell Scripting)

**Related:**
CTR-001 (Containers - stdout as logs), OBS-001 (Observability)

---

### Quick Reference Card

| Symbol | Meaning |
|--------|---------|
| `cmd > file` | stdout to file (overwrite) |
| `cmd >> file` | stdout to file (append) |
| `cmd 2> file` | stderr to file |
| `cmd 2>/dev/null` | discard stderr |
| `cmd > f 2>&1` | stdout+stderr to file |
| `cmd &> file` | stdout+stderr to file (bash shorthand) |
| `cmd < file` | stdin from file |
| `cmd1 \| cmd2` | pipe stdout of cmd1 to stdin of cmd2 |
| `cmd 2>&1 \| cmd2` | pipe stdout+stderr to cmd2 |
| `cmd \| tee file` | write to file AND show on terminal |

**3 things to remember:**
1. `> file 2>&1` = both streams to file (order matters: stdout first, then merge stderr)
2. Pipes connect stdout only; to pipe stderr use `2>&1 |`
3. In containers: write logs to stdout (not files) - platform captures them

---

### Transferable Wisdom

The standard streams concept is the basis of Unix composability.
Every programming language has equivalents: Java's `System.in`,
`System.out`, `System.err`. Python's `sys.stdin`, `sys.stdout`,
`sys.stderr`. Go's `os.Stdin`, `os.Stdout`, `os.Stderr`. The
12-factor app principle "treat logs as event streams" is a direct
application: write to stdout, let the platform collect.

The **everything is a file** philosophy (file descriptors for
files, pipes, sockets, devices) appears throughout Linux. The
same read/write interface works regardless of the underlying
resource. This abstraction is why: `cat /dev/urandom | head -c 16 | base64` works (urandom is a file descriptor), `echo "test" | nc -l 1234` works (network socket is a file descriptor), and `strace -p PID` shows system calls as read/write operations.

---

### The Surprising Truth

When you pipe commands together in a pipeline like `cmd1 | cmd2 | cmd3`,
all three commands start SIMULTANEOUSLY, not sequentially. The kernel
creates all processes at once and connects them with in-memory pipe
buffers. `cmd2` can start reading from `cmd1` before `cmd1` has finished
writing. `cmd3` can start before `cmd2` finishes. This is why long
pipelines on multi-core systems can be significantly faster than
sequential processing: each stage runs in parallel, with the pipeline
acting as a producer-consumer queue. The only synchronization: each
command blocks when its input buffer is empty (waiting for upstream)
or when its output buffer is full (waiting for downstream to consume).
This is backpressure - the same concept used in Reactive Streams,
Akka, and Kafka.

---

### Mastery Checklist

- [ ] Can redirect stdout, stderr, and both to files correctly
- [ ] Can explain why `2>&1` order matters
- [ ] Can create pipelines that correctly handle errors and edge cases
- [ ] Can explain why applications should write logs to stdout in containers
- [ ] Can troubleshoot buffering issues in pipelines

---

### Think About This

1. `ls | head -1` shows one file. Does `ls` still list all files before
   head terminates? What happens to the ls process when head gets its
   one line and exits? What signal does head send to ls, and what does
   this mean for command composition?

2. A shell script runs `output=$(./generate.sh)`. What happens to
   generate.sh's stderr? What if generate.sh crashes (exit code 1)?
   What does `$output` contain? How do you capture both stdout and
   stderr into a variable?

3. Docker captures container stdout+stderr as logs. If your Java
   application uses logback and writes to both stdout (INFO level)
   and a file (all levels), what are the trade-offs in a Kubernetes
   deployment? What does log shipping look like for each approach?

**TYPE G:** Design a log pipeline for a 500-node cluster where each
node runs 10 microservices, each writing JSON logs to stdout. Requirements:
(1) logs available within 5 seconds of writing, (2) queryable by
trace ID, service, level, and time range, (3) retained for 30 days,
(4) alerts fire within 60 seconds of error rate exceeding threshold,
(5) no application code changes. What does the complete pipeline look
like from stdout to alert?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between stdout and stderr, and why do they exist as separate streams?
A: Both stdout (fd 1) and stderr (fd 2) default to the terminal. The difference: stdout is for normal program output (data, results), stderr is for error messages, warnings, and diagnostics. They're separate so you can redirect them independently. `cmd > data.txt` captures the data (stdout) to a file while errors still appear on the terminal - you see problems immediately. `cmd | nextcmd` pipes only stdout to the next command; stderr still appears in your terminal as warnings, not mixed into the data stream. If everything went to one stream, you couldn't distinguish between "the command's data output" and "the command's error messages" in a pipeline.

**Intermediate:**
Q: Explain what `command > output.txt 2>&1` does and why the order of `2>&1` matters.
A: This redirects both stdout and stderr to output.txt. The order matters because redirections are evaluated left to right: (1) `> output.txt` redirects fd 1 (stdout) to point at output.txt. (2) `2>&1` makes fd 2 (stderr) point to wherever fd 1 currently points - which is now output.txt. Result: both streams go to output.txt. Wrong order: `command 2>&1 > output.txt`. Now: (1) `2>&1` makes stderr point to wherever stdout CURRENTLY points - which is the terminal. (2) `> output.txt` redirects stdout to output.txt. Result: stdout goes to file, stderr goes to terminal. Common mistake: writing `> output.txt 2>&1` in the "wrong order" thinking about it as "redirect stderr to stdout" rather than "redirect stderr to wherever stdout is now pointing."

**Expert:**
Q: How does the Unix pipe actually work at the kernel level, and what are the performance implications for high-throughput data pipelines?
A: A pipe is a kernel-managed circular buffer (typically 64KB on Linux). `cmd1 | cmd2`: (1) kernel creates the pipe (two file descriptors: write end and read end); (2) both processes start simultaneously; (3) cmd1 writes to the write end (fd 1 remapped to pipe write end); (4) cmd2 reads from the read end (fd 0 remapped to pipe read end); (5) if the buffer fills (cmd1 writing faster than cmd2 reads), cmd1 blocks in write() until space available; (6) if buffer is empty, cmd2 blocks in read() until cmd1 writes more. Performance implications: (1) each pipe is a kernel buffer - context switches for each write/read; (2) throughput limited by buffer size and context switch overhead; (3) for high-throughput: avoid many small writes (use larger write chunks); (4) stdbuf can adjust stdio buffering; (5) for very high throughput (>1GB/s), consider shared memory (mmap) instead of pipes; (6) in practice: pipes are efficient for typical log processing (100MB/s range); bottleneck is usually CPU processing, not the pipe mechanism.
