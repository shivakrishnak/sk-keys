---
layout: default
title: "grep / awk / sed"
parent: "Linux"
nav_order: 141
permalink: /linux/grep-awk-sed/
number: "0141"
category: Linux
difficulty: ★★☆
depends_on: Shell (bash, zsh), stdin / stdout / stderr, Pipes and Redirection
used_by: Shell Scripting, Observability & SRE, CI/CD
related: find / xargs, Shell Scripting, stdin / stdout / stderr
tags:
  - linux
  - os
  - internals
  - intermediate
---

# 141 — grep / awk / sed

⚡ TL;DR — `grep` finds lines matching a pattern; `awk` processes structured text field-by-field; `sed` edits text streams in place — together they form the Unix text processing pipeline.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have a 500 MB nginx access log. You need to find all requests returning 500 errors from IP 203.0.113.1, extract the requested URL and timestamp, sum the response sizes, and output a report. Without text tools you would write a Python script, load the file into memory, parse each line, filter and aggregate. Every one-off log analysis becomes a full programming task.

**THE BREAKING POINT:**
Production is on fire. You need to answer in 30 seconds: "How many 5xx errors in the last 1000 log lines? Which endpoint is most affected?" Firing up a Python interpreter, writing code, and debugging it takes 10 minutes you don't have.

**THE INVENTION MOMENT:**
This is exactly why `grep`, `awk`, and `sed` were created. They compose into powerful pipelines that answer complex text analysis questions in single commands, processing gigabytes of logs in seconds.

---

### 📘 Textbook Definition

`grep` (Global Regular Expression Print) scans input line-by-line and prints lines matching a regular expression. `awk` is a pattern-action language that splits each line into fields and applies user-defined rules — it is a complete programming language embedded in a single command. `sed` (Stream Editor) applies editing commands (substitution, deletion, insertion) to a stream of text without opening a file in a text editor. All three follow the Unix filter model: read stdin, write stdout, composable via pipes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
grep finds lines, awk processes fields, sed transforms text — pipe them together to analyse any log file.

**One analogy:**

> Think of a text file as a river of lines. `grep` is a net that only lets through lines containing a pattern. `awk` is a factory that takes each line, cuts it into labelled parts (field 1, field 2…), and does arithmetic on them. `sed` is a painter's tape tool — it finds specific words and replaces or deletes them as each line flows past.

**One insight:**
The power isn't in any single tool — it's the pipe chain. Each tool does one thing perfectly and hands its output to the next. `grep 'ERROR' app.log | awk '{print $5}' | sort | uniq -c | sort -rn` answers "what are the most common error sources?" in milliseconds, without loading the whole file into memory.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All three are stream processors — they never need to hold the full file in memory.
2. All three are line-oriented — they process one line at a time.
3. All three follow the filter model — stdin in, stdout out, composable by default.

**DERIVED DESIGN:**
`grep` applies a compiled regular expression to each line using the NFA/DFA engine (BRE by default, ERE with `-E`, PCRE with `-P`). It outputs matching lines — nothing else. This simplicity makes it extremely fast (GNU grep can scan GBs/second).

`awk` implements a pattern-action model: `pattern { action }`. It automatically splits each line into fields by a separator (default: whitespace), storing them as `$1`, `$2`, …, `$NF`. Built-in variables like `NR` (line number) and `NF` (field count) enable positional operations. BEGIN/END blocks run once before/after processing.

`sed` applies a script of editing commands to each line: `s/pattern/replacement/flags` for substitution, `d` for delete, `p` for print, `i` for insert. The `-i` flag edits files in-place (with a backup suffix recommended).

**THE TRADE-OFFS:**
**Gain:** Stream processing scales to arbitrary file sizes with O(1) memory; composable; available everywhere.
**Cost:** Regular expression syntax varies between tools; complex logic becomes unreadable awk/sed scripts — use Python when logic exceeds ~5 lines.

---

### 🧪 Thought Experiment

**SETUP:**
You have a log file with lines like:
`2024-01-15 10:23:45 ERROR 192.168.1.1 /api/users 500 245ms`

You need: count of 500 errors, unique IPs, average response time.

**WHAT HAPPENS WITHOUT grep/awk/sed:**

```python
import statistics
errors = []
ips = set()
times = []
with open('app.log') as f:
    for line in f:
        parts = line.split()
        if parts[2] == 'ERROR' and parts[5] == '500':
            errors.append(line)
            ips.add(parts[3])
            times.append(int(parts[6].rstrip('ms')))
print(f"Errors: {len(errors)}, IPs: {len(ips)}, "
      f"Avg: {statistics.mean(times)}ms")
```

15 lines of Python, requires Python interpreter, file to write.

**WHAT HAPPENS WITH grep/awk/sed:**

```bash
grep 'ERROR.*500 ' app.log | \
  awk '{count++; ips[$4]=1;
        t=substr($7,1,length($7)-2);
        total+=t}
   END {print "Errors:", count,
        "IPs:", length(ips),
        "Avg:", total/count "ms"}'
```

Two lines. No file. Sub-second on 100 MB log.

**THE INSIGHT:**
The stream model means the pipeline processes 100 MB with the same ~constant memory footprint whether the file is 1 MB or 10 GB. Each tool holds exactly one line at a time in memory.

---

### 🧠 Mental Model / Analogy

> Think of a production assembly line. `grep` is the quality control inspector who removes defective parts before they enter the line — only good parts proceed. `awk` is the CNC machine that reads part numbers and dimensions, applies formulas, and stamps summary cards. `sed` is the labelling machine that finds specific text on labels and prints them corrected. The conveyor belt (pipe) connects them all.

- "Quality control inspector" → grep pattern matching
- "Only good parts proceed" → only matching lines pass
- "CNC machine reading dimensions" → awk field splitting
- "Applying formulas, stamping cards" → awk arithmetic + print
- "Labelling machine with corrections" → sed substitution

Where this analogy breaks down: the tools process lines sequentially, not in parallel, though GNU parallel can parallelise across file chunks.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
grep is a powerful search tool that finds lines in a file containing specific words or patterns. awk extracts specific columns from structured text (like a CSV splitter). sed finds and replaces text throughout a file, like a powerful command-line find-and-replace.

**Level 2 — How to use it (junior developer):**
`grep "error" app.log` finds all lines with "error". `grep -i "error"` is case-insensitive. `grep -n "error"` shows line numbers. `awk '{print $1, $3}' file` prints columns 1 and 3. `awk -F: '{print $1}' /etc/passwd` splits on `:` and prints first field (usernames). `sed 's/foo/bar/g' file` replaces every "foo" with "bar". `sed -i.bak 's/foo/bar/g' file` edits in-place with a `.bak` backup.

**Level 3 — How it works (mid-level engineer):**
grep compiles the regex to an NFA, converts to DFA, then scans line bytes against the DFA — this is why `grep -F` (fixed string, no regex) is faster for literals: no NFA needed. awk tokenises each line by `FS` (field separator), stores fields in `$0`…`$NF`, and evaluates pattern-action pairs — patterns are regex or expressions, actions are C-like code. sed maintains a pattern space (current line) and hold space (persistent buffer); the `d` command clears and skips to the next line; `N` appends next line to the pattern space (enables multi-line matching).

**Level 4 — Why it was designed this way (senior/staff):**
All three were designed in the 1970s for the original Unix pipeline philosophy: each tool does one thing, output is text, compose via pipes. grep's algorithm (Thompson NFA → DFA) is still the fastest correct implementation of regex search. awk (named for Aho, Weinberger, Kernighan) was designed as a prototyping language for data transformation before Python existed — its pattern-action model is still unmatched for line-oriented data. sed's hold space is a Turing-complete side channel; people have implemented Fibonacci, sorting, and even basic HTTP servers in sed — which proves both its power and its unreadability at scale.

---

### ⚙️ How It Works (Mechanism)

**grep internals:**

```
┌─────────────────────────────────────────────┐
│  grep 'ERROR|WARN' app.log                  │
└─────────────────────────────────────────────┘

For each line:
  1. Apply compiled regex (NFA/DFA)
  2. If match: write line to stdout
  3. If no match: discard

Key: uses Boyer-Moore + bit-parallel matching
     → can skip ahead multiple bytes at a time
     → extremely fast on long non-matching lines
```

**grep key options:**

```bash
grep 'pattern' file          # basic match
grep -i 'pattern' file       # case-insensitive
grep -v 'pattern' file       # invert (lines NOT matching)
grep -n 'pattern' file       # show line numbers
grep -c 'pattern' file       # count matching lines
grep -r 'pattern' dir/       # recursive directory search
grep -l 'pattern' dir/*      # list files containing match
grep -E 'pat1|pat2' file     # extended regex (alternation)
grep -P '\d{4}-\d{2}-\d{2}' file  # Perl regex
grep -A3 'ERROR' file        # 3 lines After match
grep -B3 'ERROR' file        # 3 lines Before match
grep -C3 'ERROR' file        # 3 lines Context (before+after)
grep -o 'pattern' file       # only the matching part
```

**awk key patterns:**

```bash
# Print specific fields
awk '{print $1, $3}' file

# Field separator
awk -F: '{print $1}' /etc/passwd

# Conditional action
awk '$3 > 100 {print $0}' file

# Built-in variables
awk '{print NR, NF, $0}' file  # line num, field count, line

# Aggregation
awk '{sum += $5} END {print "Total:", sum}' file

# Count occurrences
awk '{counts[$2]++}
   END {for (k in counts) print k, counts[k]}' file

# BEGIN block (run once before file)
awk 'BEGIN{FS=","; OFS="\t"}
     {print $1, $3}' data.csv

# Pattern + action
awk '/ERROR/{errors++} /WARN/{warns++}
   END {print "E:", errors, "W:", warns}' app.log
```

**sed key commands:**

```bash
# Substitution: replace first occurrence per line
sed 's/foo/bar/' file

# Replace ALL occurrences per line
sed 's/foo/bar/g' file

# Case-insensitive replace
sed 's/foo/bar/gi' file

# In-place edit with backup
sed -i.bak 's/localhost/prod.db/g' config.yaml

# Delete lines matching pattern
sed '/^#/d' file               # delete comment lines
sed '/^[[:space:]]*$/d' file   # delete blank lines

# Print only matching lines (like grep)
sed -n '/ERROR/p' file

# Print specific line range
sed -n '10,20p' file

# Insert line after match
sed '/pattern/a\New line after' file

# Multi-command with -e
sed -e 's/foo/bar/g' -e 's/baz/qux/g' file
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  LOG ANALYSIS PIPELINE                      │
└─────────────────────────────────────────────┘

app.log (500 MB on disk)
       │
       ▼
grep 'HTTP 5[0-9][0-9]' app.log
       │  only error lines pass ← YOU ARE HERE (grep)
       ▼
awk '{print $7}'
       │  extract URL field
       ▼ ← YOU ARE HERE (awk)
sort
       │  group same URLs together
       ▼
uniq -c
       │  count occurrences
       ▼
sort -rn
       │  sort by count descending
       ▼
head -10
       │
       ▼
Top 10 error URLs printed
Total memory: ~1 line buffer per tool (~constant)
```

**FAILURE PATH:**
Regex syntax error → grep exits 2 with "invalid expression" → pipeline outputs nothing → check with `echo "test" | grep 'pattern'` first.

**WHAT CHANGES AT SCALE:**
For multi-GB logs on a single machine, GNU parallel splits the file and runs grep/awk across CPU cores: `parallel grep 'ERROR' ::: *.log`. For petabyte-scale log analysis, streaming the logs to Elasticsearch, Splunk, or Athena (S3 logs) is more appropriate — these tools are not designed for distributed execution.

---

### 💻 Code Example

**Example 1 — Log analysis pipeline:**

```bash
# Find top 10 most requested endpoints from nginx log
# Log format: IP - - [date] "METHOD /path HTTP/1.1" STATUS bytes
awk '{print $7}' /var/log/nginx/access.log | \
  sort | uniq -c | sort -rn | head -10

# Count 5xx errors by hour
grep 'HTTP/1.1" 5' /var/log/nginx/access.log | \
  awk '{print substr($4, 2, 14)}' | \
  sort | uniq -c
# substr($4,2,14) extracts YYYY:HH from [DD/Mon/YYYY:HH:MM:SS]
```

**Example 2 — Config file modification:**

```bash
# Change database host in all config files
# BAD — no backup, risky
sed -i 's/localhost/db.prod.internal/g' config/*.yaml

# GOOD — with backup extension
sed -i.bak 's/localhost/db.prod.internal/g' \
  config/*.yaml

# Verify changes before committing
diff config/database.yaml config/database.yaml.bak
```

**Example 3 — Extract structured data:**

```bash
# Parse /etc/passwd: get home dirs for users with UID > 1000
awk -F: '$3 > 1000 {print $1, $6}' /etc/passwd

# Find all Java processes and their heap settings
ps aux | grep java | grep -v grep | \
  awk '{for(i=1;i<=NF;i++){
    if($i ~ /-Xmx/) print $2, $i
  }}'
# $2 is PID, matches -Xmx flag in command line
```

**Example 4 — Multi-tool pipeline for incident response:**

```bash
#!/bin/bash
# Quick incident report: errors in last 100 lines
LOG=/var/log/app/app.log

echo "=== Last 100 lines error summary ==="
tail -100 "$LOG" | \
  grep -E 'ERROR|FATAL' | \
  awk '{
    split($1, d, "-"); split($2, t, ":");
    ts = d[1]"-"d[2]"-"d[3]" "t[1]":"t[2];
    level[$3]++;
    last_ts = ts
  }
  END {
    for (l in level) printf "%s: %d\n", l, level[l]
    print "Last event:", last_ts
  }'
```

---

### ⚖️ Comparison Table

| Tool      | Strength            | Speed        | Complexity | Best For                        |
| --------- | ------------------- | ------------ | ---------- | ------------------------------- |
| **grep**  | Pattern matching    | Fastest      | Simple     | Finding lines, counting matches |
| **awk**   | Field processing    | Fast         | Medium     | Column extraction, aggregation  |
| **sed**   | Text transformation | Fast         | Medium     | Find/replace, line deletion     |
| Python    | General purpose     | Slower start | High       | Complex multi-file analysis     |
| cut       | Field extraction    | Very fast    | Minimal    | Simple fixed-delimiter columns  |
| sort/uniq | Sorting/counting    | Fast         | Minimal    | Frequency counts, deduplication |

How to choose: start with grep for filtering, add awk for field processing, add sed for transformation; switch to Python when the pipeline exceeds one screen of commands or requires complex state.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                             |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `sed -i` is safe without a backup extension | `-i ''` (no backup) on macOS works but `-i` alone fails; always use `-i.bak` for portability and safety                             |
| grep -E and grep -P are the same            | -E is POSIX Extended Regex; -P is Perl-compatible Regex (PCRE) — PCRE supports lookaheads, backreferences, `\d`, etc.; ERE does not |
| awk and sed can only process text files     | Both process any byte stream; awk can parse binary-looking text, sed can manipulate any stdin stream                                |
| `grep 'pattern' file` loads the whole file  | grep reads line-by-line in a buffer; memory usage is constant regardless of file size                                               |
| sed `s/old/new/` replaces all occurrences   | Without `/g` flag, only the FIRST occurrence per line is replaced                                                                   |

---

### 🚨 Failure Modes & Diagnosis

**Regex Works in Testing but Not in Script**

**Symptom:**
A grep command works in the terminal but produces no output when the same file is processed in a shell script.

**Root Cause:**
The file uses Windows line endings (`\r\n`). The pattern matches the content but the `\r` before the newline causes unexpected behaviour, especially in awk field splitting.

**Diagnostic Command:**

```bash
# Check for carriage returns
file app.log
cat -A app.log | head -3  # shows ^M for \r
hexdump -C app.log | head -3
```

**Fix:**

```bash
# Convert to Unix line endings
sed -i 's/\r//' file.txt
# Or
tr -d '\r' < windows.txt > unix.txt
```

**Prevention:**
Configure git to normalise line endings; use `dos2unix` on files from Windows systems.

---

**sed -i Behaves Differently on macOS vs Linux**

**Symptom:**
`sed -i 's/foo/bar/' file` works on Linux but fails on macOS with "invalid command code".

**Root Cause:**
GNU sed (`-i[SUFFIX]`) and BSD sed (`-i extension`) have incompatible syntax for in-place editing.

**Diagnostic Command:**

```bash
sed --version 2>/dev/null && echo "GNU" || echo "BSD/macOS"
```

**Fix:**

```bash
# Portable form — works on both macOS and Linux
sed -i.bak 's/foo/bar/' file

# Or use perl for truly portable in-place editing
perl -pi -e 's/foo/bar/g' file
```

**Prevention:**
Always include a backup extension with `sed -i`; test scripts on target OS.

---

**awk Floating Point Precision**

**Symptom:**
awk arithmetic produces results like `0.600000000001` instead of `0.6`.

**Root Cause:**
awk uses IEEE 754 double-precision floating point internally; decimal fractions cannot always be represented exactly in binary.

**Diagnostic Command:**

```bash
echo "1.1 1.1 1.1" | awk '{print $1 + $2 + $3}'
# May output: 3.3 or 3.30000000000000X
```

**Fix:**

```bash
# Use printf for formatted output
echo "1.1 1.1 1.1" | \
  awk '{printf "%.2f\n", $1 + $2 + $3}'
```

**Prevention:**
Always use `printf "%.Nf"` for financial or precise decimal output in awk.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Shell (bash, zsh)` — grep/awk/sed run in the shell; pipelines and quoting are shell concepts
- `stdin / stdout / stderr` — all three tools are filter commands that read stdin and write stdout
- `Pipes and Redirection` — the pipe `|` operator is what makes these tools compose into powerful pipelines

**Builds On This (learn these next):**

- `find / xargs` — combines filesystem traversal with grep/awk/sed for processing many files
- `Shell Scripting` — grep/awk/sed are the workhorses of non-trivial shell scripts
- `Observability & SRE` — log analysis in production relies heavily on these tools

**Alternatives / Comparisons:**

- `Python` — more readable for complex logic; worse for quick interactive analysis
- `jq` — specialised JSON processor (like awk for JSON)
- `cut` — simpler field extraction for fixed-delimiter files (no regex, no conditions)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ grep: line filter; awk: field processor;  │
│              │ sed: stream text transformer              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Ad-hoc log/text analysis required writing │
│ SOLVES       │ full programs for one-off queries         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Stream processing: O(1) memory regardless │
│              │ of file size; compose via pipes           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Log analysis, config editing, data        │
│              │ extraction from structured text           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ JSON/XML parsing (use jq/xmllint);        │
│              │ >5 lines of logic (use Python instead)    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Speed + universality vs readability;      │
│              │ cryptic at complexity, readable at basic  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "grep finds it, awk measures it,          │
│              │  sed changes it — pipe them together"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ find/xargs → jq → Python scripts         │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You need to grep through 50 GB of compressed log files (`.gz`) across 16 CPU cores. Decompressing them all first takes 20 minutes. Designing a pipeline using `zcat`, `grep`, and GNU `parallel` can do it in 2 minutes without uncompressing to disk. Sketch that pipeline and explain why it is faster, what its memory footprint is, and what failure mode you need to handle if a `.gz` file is corrupted.

**Q2.** `sed 's/password=.*/password=REDACTED/g'` is used to sanitise a config file for logging. A developer points out this could still leak data. Identify at least two scenarios where this regex fails to properly redact sensitive values, and write a corrected sed or awk command that handles them.
