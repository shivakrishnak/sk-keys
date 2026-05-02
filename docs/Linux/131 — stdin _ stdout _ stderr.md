---
layout: default
title: "stdin / stdout / stderr"
parent: "Linux"
nav_order: 131
permalink: /linux/stdin-stdout-stderr/
number: "0131"
category: Linux
difficulty: ★☆☆
depends_on: Shell (bash, zsh), Operating System
used_by: Pipes and Redirection, Shell Scripting, grep / awk / sed
related: Pipes and Redirection, Shell (bash, zsh), File Permissions (chmod, chown)
tags:
  - linux
  - os
  - foundational
  - internals
---

# 131 — stdin / stdout / stderr

⚡ TL;DR — Every Linux process has three open streams by default: stdin (input from keyboard), stdout (normal output), and stderr (error output) — the universal I/O contract that makes Unix tools composable.

| #131            | Category: Linux                                          | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Shell (bash, zsh), Operating System                      |                 |
| **Used by:**    | Pipes and Redirection, Shell Scripting, grep / awk / sed |                 |
| **Related:**    | Pipes and Redirection, Shell (bash, zsh)                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In the 1960s, programs received their input from specific hardware devices (punch cards, tape drives) and wrote output to specific printers or display hardware. To connect two programs — pass the output of one as input to the next — you had to physically rewire hardware or write intermediate files with hardcoded paths. There was no concept of a program-to-program data flow independent of hardware.

**THE BREAKING POINT:**
This model made programs brittle and non-composable. A sort program could only sort data from a tape drive. A filter program could only read from a card reader. You could not connect them without hardware changes or custom integration code.

**THE INVENTION MOMENT:**
Ken Thompson and Dennis Ritchie designed Unix with a key abstraction: every process has three pre-opened, abstract **file descriptors** — 0 (stdin), 1 (stdout), 2 (stderr) — that represent data streams with no hardcoded source or destination. The shell can then connect these streams between programs with pipes and redirections. This is exactly why stdin/stdout/stderr exist: to make every Unix program a composable unit with a universal I/O interface.

---

### 📘 Textbook Definition

**stdin** (standard input, file descriptor 0), **stdout** (standard output, file descriptor 1), and **stderr** (standard error, file descriptor 2) are three pre-opened file descriptors that every POSIX process inherits at creation. They are abstractions over whatever underlying I/O channel is connected to them — typically: stdin connected to the terminal keyboard, stdout connected to the terminal display, stderr also connected to the terminal display (but separately, allowing independent redirection). Programs read input from fd 0, write normal output to fd 1, and write error messages to fd 2 — without knowing whether these are a terminal, a file, a pipe, or a socket. The shell can redirect them with `>`, `<`, `2>`, `>>`, `|`, allowing arbitrary composition of programs.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Stdin is your program's inbox, stdout is its outbox, and stderr is its error log — three separate streams every process has by default.

**One analogy:**

> Think of a program as a postal sorting station. It has three slots in the wall: an **in** slot (stdin — letters arrive here), an **out** slot (stdout — sorted mail goes here), and a **reject** slot (stderr — problem mail and error notes go here). The genius of Unix is that these three slots are connected to whatever you want: a keyboard, a file, another sorting station's output — without changing the sorting station itself.

**One insight:**
The separation of stdout and stderr is what makes automated processing reliable. When you pipe `command | wc -l` to count output lines, only stdout travels through the pipe. Error messages go to stderr, which goes to the terminal — you see errors while stdout is being processed downstream. Without this separation, error messages would corrupt your data pipeline.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. File descriptors 0, 1, 2 are opened before `main()` is called — every C program receives them.
2. The kernel doesn't care what is connected to fd 0/1/2 — it's just a file descriptor.
3. Programs that read from fd 0 and write to fd 1 work universally in any pipeline.

**DERIVED DESIGN:**

```
FILE DESCRIPTOR TABLE (per process):

Process A:
┌──────────────────────────────────────────────┐
│ fd │ Description     │ Connected To           │
├────┼─────────────────┼───────────────────────┤
│  0 │ stdin           │ /dev/pts/0 (terminal)  │
│  1 │ stdout          │ /dev/pts/0 (terminal)  │
│  2 │ stderr          │ /dev/pts/0 (terminal)  │
│  3 │ (open file)     │ /var/log/app.log        │
└──────────────────────────────────────────────┘

After: command > output.txt
┌──────────────────────────────────────────────┐
│ fd │ Description     │ Connected To           │
├────┼─────────────────┼───────────────────────┤
│  0 │ stdin           │ /dev/pts/0 (terminal)  │
│  1 │ stdout          │ output.txt (file)      │
│  2 │ stderr          │ /dev/pts/0 (terminal)  │
└──────────────────────────────────────────────┘
```

**How `fork()` + redirection works:**

```
Shell forks child, then (in child, before exec):
  open("output.txt") → fd 3
  dup2(3, 1)          → fd 1 now points to output.txt
  close(3)
  execve("command")   → command writes to fd 1 = file
```

**THE TRADE-OFFS:**
**Gain:** Universal composability — any program that reads stdin and writes stdout can be connected to any other.
**Cost:** Byte streams carry no structure — the receiving program must parse the output format itself. This is why tools like `jq` (JSON pipe) and structured logging exist: to impose structure on the raw byte stream.

---

### 🧪 Thought Experiment

**SETUP:**
You run: `find /var/log -name "*.log" 2>/dev/null | wc -l`

**WHAT HAPPENS WITHOUT STDERR SEPARATION:**
`find` encounters a directory it can't read (permission denied) and prints the error. Without separation, the error message goes into stdout, travels through the pipe, and `wc -l` counts it as a valid line. Your count is inflated by the number of permission-denied errors. Your pipeline is corrupted by diagnostic noise.

**WHAT HAPPENS WITH STDERR SEPARATION:**
`2>/dev/null` redirects fd 2 (stderr) to `/dev/null` (discarding errors). Permission-denied messages never enter the pipe. `wc -l` counts only actual filenames. The count is accurate. The errors are silently discarded (which may or may not be what you want — you could redirect to a log file instead with `2>errors.log`).

**THE INSIGHT:**
Separating stdout from stderr is what makes automated data pipelines trustworthy. The contract: stdout is for data, stderr is for metadata (errors, progress, warnings). Any tool that violates this contract (writes errors to stdout) breaks every pipeline it participates in.

---

### 🧠 Mental Model / Analogy

> stdin, stdout, and stderr are like a factory assembly line's three conveyor belts. Belt 0 (stdin) brings raw materials into the factory. Belt 1 (stdout) carries finished products out. Belt 2 (stderr) carries rejected parts and quality-control notes to the foreman. The factory (program) never knows or cares where the materials come from or where the finished products go — it just reads from belt 0 and writes to belts 1 and 2.

- "Raw materials conveyor (belt 0)" → stdin (fd 0)
- "Finished products conveyor (belt 1)" → stdout (fd 1)
- "QC reject belt (belt 2)" → stderr (fd 2)
- "Connecting factories" → pipes (`|`)
- "Routing products to a warehouse" → redirection (`>`, `>>`)

**Where this analogy breaks down:** Unlike physical conveyor belts, these are not flowing continuously — programs read in blocks (buffered I/O), and the stream doesn't "arrive" until the upstream program writes it. Buffering behaviour (line-buffered vs. fully-buffered) affects latency in pipelines.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every program on Linux has three built-in connections: one for receiving input (stdin), one for sending output (stdout), and one for sending error messages (stderr). By default, stdin comes from the keyboard and both stdout and stderr display on your screen.

**Level 2 — How to use it (junior developer):**
In shell: `cmd < input.txt` feeds a file as stdin; `cmd > output.txt` captures stdout to a file; `cmd 2> errors.txt` redirects stderr. Combine: `cmd > out.txt 2> err.txt`. To discard errors: `cmd 2>/dev/null`. To merge stderr into stdout: `cmd 2>&1`. In code: `System.out.println()` writes to stdout; `System.err.println()` writes to stderr. In Python: `print("error", file=sys.stderr)`.

**Level 3 — How it works (mid-level engineer):**
File descriptors are integers that index into the kernel's per-process file descriptor table. Fd 0/1/2 are just reserved by convention. `dup2(src, dest)` makes two FDs point to the same open file description. When a process forks, the child inherits copies of all FDs. The shell sets up redirections in the child between `fork()` and `execve()` — the program itself never knows its FDs were redirected. Buffering: stdout is line-buffered when connected to a terminal, fully-buffered when connected to a pipe or file (affects flush timing).

**Level 4 — Why it was designed this way (senior/staff):**
The decision to make stdin/stdout abstract streams (not device-specific) was Unix's key philosophical break from earlier OS design. The `|` pipe operator (added to Unix in 1972) was the practical realisation: programs don't need to know about each other to be composed. The design exposed a tension: fully-buffered stdout in pipelines introduces latency (data doesn't flush until the buffer is full). This is why `stdbuf -oL command` (line-buffered) or `unbuffer command` (from expect) exist for real-time pipeline processing. Modern alternatives (structured pipes with JSON/msgpack) trade composability overhead for richer semantics.

---

### ⚙️ How It Works (Mechanism)

**FD redirection in shell:**

```bash
# Redirect stdout to file (fd 1 → file)
ls -la > listing.txt

# Redirect stderr to file (fd 2 → file)
find / -name "*.conf" 2> errors.txt

# Redirect both to same file
command > all_output.txt 2>&1
# 2>&1 means: make fd 2 a copy of fd 1
# ORDER MATTERS: > must come before 2>&1

# WRONG: this sends stderr to OLD stdout (terminal),
#        then stdout to file:
command 2>&1 > file.txt   # stderr still goes to terminal!

# Append instead of overwrite
command >> output.txt

# Read from file as stdin
wc -l < myfile.txt

# /dev/null: the black hole
command > /dev/null 2>&1  # discard everything
```

**Here-doc and here-string:**

```bash
# Here-document: multi-line stdin
cat <<EOF
Line 1
Line 2
EOF

# Here-string: single string as stdin
base64 --decode <<< "SGVsbG8gV29ybGQ="
```

**Process substitution (bash/zsh):**

```bash
# Compare output of two commands (no temp files)
diff <(sort file1.txt) <(sort file2.txt)
# <(...) creates a named pipe; sort writes to it;
# diff reads from two "files" that are actually pipes
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
User types: grep "ERROR" app.log | wc -l

Shell sets up pipe: fd pair [read_end, write_end]
    ↓
Fork child1 (grep):
  dup2(write_end, stdout)  ← grep's stdout → pipe
  execve grep "ERROR" app.log
    ↓
Fork child2 (wc):
  dup2(read_end, stdin)   ← wc's stdin ← pipe
    ← YOU ARE HERE (data flows through pipe)
  execve wc -l
    ↓
grep reads app.log, writes matching lines to stdout (pipe)
    ↓
wc reads from stdin (pipe), counts lines, writes count to stdout
    ↓
Shell waits for both children, prints prompt
```

**FAILURE PATH:**

```
grep fails to open app.log (permission denied)
    ↓
grep writes error to fd 2 (stderr → terminal)
grep writes nothing to fd 1 (stdout → pipe)
    ↓
wc reads 0 bytes → prints "0"
    ↓
User sees: error message on terminal + "0" as output
Shell exit code: 2 (grep's exit code, last in pipe)
```

**WHAT CHANGES AT SCALE:**
In high-throughput log processing pipelines, buffer sizes become critical. A pipeline producer writing 100MB/s into a pipe will block when the pipe buffer (typically 64KB) fills — if the consumer is slow. This causes backpressure. In real-time monitoring, `stdbuf -oL` forces line-buffered output from intermediate tools; without it, metrics appear in bursts rather than continuously, breaking dashboards and alerting.

---

### 💻 Code Example

**Example 1 — The three streams in a program:**

```bash
#!/bin/bash
# Reading from stdin
echo "Enter your name:"
read -r name          # reads from fd 0 (stdin)

# Writing to stdout
echo "Hello, $name"   # writes to fd 1 (stdout)

# Writing to stderr
echo "Debug: name='$name'" >&2  # writes to fd 2

# Read stdin from file when called as: script.sh < input.txt
while IFS= read -r line; do
    echo "Processing: $line"
done
```

**Example 2 — Capturing stderr separately:**

```bash
# Capture stdout and stderr into separate variables
stdout=$(command 2>/tmp/stderr_cap)
stderr=$(cat /tmp/stderr_cap)

# Or use process substitution (bash 4+):
{ stdout=$(command 2>&3); } 3>&1
# Complex; prefer the temp file approach for clarity
```

**Example 3 — In Java (standard streams):**

```java
import java.util.Scanner;

public class StreamDemo {
    public static void main(String[] args) {
        // stdin: System.in
        Scanner sc = new Scanner(System.in);
        String line = sc.nextLine();

        // stdout: System.out (buffered, flushed on newline)
        System.out.println("You said: " + line);

        // stderr: System.err (often unbuffered)
        System.err.println("Warning: processing " + line);
        // stderr goes to fd 2; stdout to fd 1
        // in a pipeline: 2>/dev/null suppresses warnings
    }
}
```

**Example 4 — In Python:**

```python
import sys

# Read from stdin (line by line)
for line in sys.stdin:
    line = line.rstrip('\n')

    # Write to stdout (fd 1)
    print(f"Processed: {line}")

    # Write to stderr (fd 2)
    print(f"Debug: line length={len(line)}", file=sys.stderr)

# Flush explicitly if output is piped
sys.stdout.flush()
```

---

### ⚖️ Comparison Table

| Stream     | FD  | Default destination | Typical use                 | Redirectable?        |
| ---------- | --- | ------------------- | --------------------------- | -------------------- |
| **stdin**  | 0   | Terminal keyboard   | Command input, file content | Yes (`< file`)       |
| **stdout** | 1   | Terminal display    | Normal output, data         | Yes (`> file`, `\|`) |
| **stderr** | 2   | Terminal display    | Errors, warnings, logs      | Yes (`2>file`)       |
| Custom fd  | 3+  | (not pre-opened)    | App-specific logging        | Yes (manual `exec`)  |

**How to choose when writing programs:** Write data to stdout, errors/diagnostics to stderr. Never mix them. Programs that follow this contract work in every pipeline automatically.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                    |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `2>&1` merges stderr INTO stdout's file           | `2>&1` makes fd 2 a duplicate of fd 1 AT THAT MOMENT; changing fd 1 later doesn't affect fd 2                                              |
| `/dev/null` is a file that stores discarded data  | `/dev/null` is a special device file; anything written to it is discarded by the kernel immediately; reading from it returns EOF           |
| stdout and stderr appear in order                 | The kernel interleaves fd 1 and fd 2 writes non-deterministically; their order on the terminal may differ from write order                 |
| `echo "error" > file.txt` captures error messages | `>` redirects stdout only (fd 1); error messages go to stderr (fd 2) and still appear on the terminal                                      |
| Programs always read from the keyboard            | Programs read from fd 0, which the shell connects to the keyboard by default; with `< file`, they read from a file without any code change |
| Closing stdin causes programs to crash            | Well-written programs detect EOF on stdin (read returns 0 bytes) and exit cleanly; poorly written ones may hang waiting for more input     |

---

### 🚨 Failure Modes & Diagnosis

**Script Output Missing in Log File**

**Symptom:**
`./script.sh > output.log` — output.log is empty or incomplete; some output appeared on the terminal.

**Root Cause:**
Script writes errors to stderr; only stdout is redirected to the log. Errors go to terminal, not the log.

**Diagnostic Command:**

```bash
./script.sh > output.log 2>&1  # capture both streams
# OR redirect each separately:
./script.sh > output.log 2> errors.log
```

**Fix:**
Add `2>&1` to capture stderr; or review which stream each message should use.

**Prevention:**
In scripts, always use `>&2` for error messages; document where to look for errors vs. output.

---

**Pipeline Hangs: Downstream Consumer Never Gets EOF**

**Symptom:**
A pipeline like `producer | consumer` runs forever; consumer seems to be waiting.

**Root Cause:**
Producer has exited but left fd 1 (write end of pipe) open in a child process. Kernel sends EOF only when ALL holders of the write end close it.

**Diagnostic Command:**

```bash
# Find processes holding the pipe open
lsof | grep pipe
ps aux | grep consumer
```

**Fix:**
Ensure producer and all its forked children close stdout before exiting; use `exec >& /dev/null` to close inherited FDs in child processes.

**Prevention:**
In scripts that fork background jobs, close unneeded FDs: `(producer >&3; exec 3>&-) | consumer`.

---

**Buffering Causes Lost Data at Pipe End**

**Symptom:**
A Python/C program writes to stdout in a pipeline; at program crash, the last N lines are missing from the output file.

**Root Cause:**
stdout is fully-buffered when connected to a pipe (not a terminal). On crash, the internal buffer is not flushed — data is lost.

**Diagnostic Command:**

```bash
# Python: check buffering mode
python3 -c "import sys; print(sys.stdout.line_buffering)"

# Force unbuffered Python:
python3 -u script.py | consumer
```

**Fix:**
Use `python3 -u` (unbuffered) or call `sys.stdout.flush()` after critical writes; in C, call `fflush(stdout)` or `setvbuf(stdout, NULL, _IOLBF, 0)`.

**Prevention:**
Always flush stdout before exit; use line-buffering in pipelines with `stdbuf -oL` or `-u` flags.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Shell (bash, zsh)` — the shell connects stdin/stdout/stderr between programs
- `Operating System` — file descriptors are a kernel abstraction

**Builds On This (learn these next):**

- `Pipes and Redirection` — the mechanism for connecting stdin/stdout between programs
- `Shell Scripting` — scripts use stdin/stdout/stderr for all I/O
- `grep / awk / sed` — these tools are designed around the stdin-stdout contract

**Alternatives / Comparisons:**

- `Sockets` — network-based streams with similar read/write semantics but over a network
- `Named Pipes (FIFOs)` — like pipes but with a filesystem path; persist between unrelated processes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Three pre-opened file descriptors:        │
│              │ fd0=input, fd1=data output, fd2=errors    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Programs needed a universal I/O interface │
│ SOLVES       │ independent of hardware                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Separating stdout and stderr is what      │
│              │ makes data pipelines trustworthy          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always: every program I/O goes through    │
│              │ these streams                             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never write errors to stdout in programs  │
│              │ meant to be used in pipelines             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Universal composability vs. unstructured  │
│              │ byte streams (need to parse format)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "stdout is data; stderr is the operator   │
│              │  channel — never mix them"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pipes and Redirection → Shell Scripting   │
│              │ → grep / awk / sed                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A program written in C uses `fprintf(stderr, "Processing...\n")` for progress updates and `printf("%s\n", result)` for final output. You run it in a pipeline: `myprogram | sort | wc -l`. You see progress messages on the terminal while the pipeline runs. Now you redirect everything: `myprogram 2>&1 | sort | wc -l`. What changes? Does `wc -l` now count the progress messages too? Why or why not — and what happens to the ordering of progress messages vs. output lines when both are merged into the pipe?

**Q2.** You have a pipeline: `producer.py | processor.py | consumer.py`. The `producer.py` script runs for 10 minutes and generates 1 million lines. Midway through, `processor.py` crashes with an unhandled exception. Describe what happens to each part of the pipeline: does `producer.py` keep running? Does `consumer.py` get an EOF? What signal does the kernel send, and to which process? How would `set -o pipefail` in the calling bash script affect the observable exit code of the entire pipeline?
