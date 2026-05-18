---
id: LNX-026
title: "grep - Pattern Matching in Files"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-008, LNX-015, LNX-016
used_by: LNX-043, LNX-027
related: LNX-043, LNX-027, LNX-028, LNX-009
tags: [grep, egrep, fgrep, pattern-matching, regex, log-analysis, text-search]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/lnx/grep/
---

## TL;DR

`grep` searches files or input for lines matching a pattern.
Ubiquitous in log analysis, script debugging, and code search.
Key flags: `-r` recursive, `-i` case-insensitive, `-n` show line
numbers, `-l` list filenames only, `-v` invert match (non-matching
lines), `-E` extended regex, `-A/-B/-C` context lines. Log analysis
workflow: `grep ERROR app.log | grep -v "expected_error" | tail -50`.
`grep` is the first tool you reach for when you need to find something
in text output or files.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-026 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | grep, egrep, regular expressions, log analysis, pattern matching |
| **Prerequisites** | LNX-008, LNX-015, LNX-016 |

---

### The Problem This Solves

Application just threw an exception. Log file is 10GB. You need to find
the stack trace. `grep "NullPointerException" app.log -A 20` finds it
in seconds and shows 20 lines after the match (the stack trace). Without
grep, you'd be scrolling through 10GB manually. grep is the essential
tool for extracting signal from noise in any text-based system: logs,
configuration files, code, command output.

---

### Textbook Definition

**grep** (Global Regular Expression Print): Reads lines from files or
stdin, prints lines that match a given pattern. Pattern can be a fixed
string or a regular expression. Variants:

- `grep`: basic regular expressions (BRE)
- `grep -E` or `egrep`: extended regular expressions (ERE)
- `grep -F` or `fgrep`: fixed string (no regex, faster for literal searches)
- `grep -P`: Perl-compatible regex (PCRE, most powerful)

grep is line-oriented: it reads entire lines and outputs the line if the
pattern matches anywhere in it.

---

### Understand It in 30 Seconds

```bash
# Basic search:
grep "error" /var/log/syslog          # find lines containing "error"
grep "error" /var/log/*.log           # search multiple files
grep -r "database" /etc/              # recursive search in directory

# Essential flags:
grep -i "Error" app.log               # case-insensitive
grep -n "ERROR" app.log               # show line numbers
grep -v "DEBUG" app.log               # exclude lines matching (invert)
grep -c "ERROR" app.log               # count matching lines
grep -l "TODO" *.java                 # list files with matches only

# Context lines (crucial for log analysis):
grep -A 10 "NullPointerException" app.log  # 10 lines AFTER match
grep -B 5 "ERROR" app.log                  # 5 lines BEFORE match
grep -C 10 "EXCEPTION" app.log             # 10 lines BEFORE AND AFTER

# Extended regex:
grep -E "ERROR|WARN|FATAL" app.log        # OR pattern
grep -E "HTTP [45][0-9]{2}" access.log    # HTTP 4xx/5xx errors
grep -E "^\d{4}-\d{2}-\d{2}" log.txt     # lines starting with date

# Common patterns:
grep "ERROR" app.log | wc -l         # count errors
grep "ERROR" app.log | tail -20      # last 20 errors
grep -r "TODO" src/ | grep ".java"   # TODOs in java files
grep -P "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" access.log  # IP addresses
```

---

### First Principles

**grep's operating model:**
1. For each input line, test if the pattern matches anywhere in the line
2. If match: print the line (or perform the requested action)
3. If no match: discard the line (unless -v)

This is fundamentally a FILTER: grep transforms an input stream into a
subset output stream. This makes it composable with pipes (LNX-016).

**exit codes matter:**
- `0`: at least one line matched (grep succeeded)
- `1`: no lines matched (grep "found nothing")
- `2`: error (syntax error in pattern, file not found)

This is critical for scripting:
```bash
if grep -q "RUNNING" service.status; then
    echo "service is running"
fi
# grep -q: quiet mode (suppress output, just use exit code)
```

**BRE vs ERE:**
Basic regex: `\+` `\?` `\|` require backslash for special meaning.
Extended regex (`-E`): `+` `?` `|` are special without backslash.
In practice: always use `grep -E` to avoid confusion. `grep -E "a|b"`
is clearer than `grep "a\|b"`.

---

### Thought Experiment

Production incident: thousands of users report login failure. Logs show
the issue started at a specific time. Find the root cause in 5 minutes.

```bash
# Step 1: what's the error pattern?
grep -i "error\|exception\|fail" /var/log/myapp/app.log | tail -50

# Step 2: focus on the time window
grep "2024-01-15 14:3[0-9]" /var/log/myapp/app.log | grep -i "error"

# Step 3: what error specifically?
grep -i "AuthenticationException" /var/log/myapp/app.log | tail -10
# Output: AuthenticationException: LDAP server timeout

# Step 4: when did it start?
grep "AuthenticationException" /var/log/myapp/app.log | head -1
# Output: 2024-01-15 14:32:01 - correlation: deployment at 14:31

# Step 5: what changed at 14:31?
grep "14:31" /var/log/deploy.log
# Output: Deployed version 2.1.4 - config change: LDAP timeout 5s -> 1s

# Root cause found in 3 minutes using only grep.
```

---

### Mental Model / Analogy

grep is a **gatekeeping filter for text:**

```
Input stream:             grep filter:           Output:
"line with ERROR"  -----> pattern: "ERROR" -----> "line with ERROR"
"normal info log"  -----> NO MATCH             (discarded)
"another ERROR"    -----> pattern: "ERROR" -----> "another ERROR"
"debug output"     -----> NO MATCH             (discarded)

With -v (invert), the gate flips:
"line with ERROR"  -----> invert "ERROR" ------> (discarded)
"normal info log"  -----> NO MATCH (passes!) ---> "normal info log"

grep is a FILTER in the Unix pipeline.
chained grep is a cascading filter (AND logic):
grep "ERROR" log | grep -v "known_good_error" | grep "database"
= ERROR lines, excluding known good, that mention database
```

---

### Gradual Depth - Five Levels

**Level 1:**
`grep pattern file`, `-i` case-insensitive, `-v` invert, `-r` recursive.
`grep ERROR app.log` finds errors. `grep -v DEBUG app.log` removes debug.
Pipe to grep: `cat file | grep pattern` (or just `grep pattern file`).

**Level 2:**
`-A N`, `-B N`, `-C N` context. `-n` line numbers. `-l` list files.
`-c` count lines. `-q` quiet (for scripting). Multiple files and globs.
`-E` for extended regex. `grep "pattern1\|pattern2"` or `grep -E "p1|p2"`.
`--include` and `--exclude` for recursive search: `grep -r "TODO" . --include="*.java"`.

**Level 3:**
Regex in grep: `^` (start), `$` (end), `.` (any char), `*` (0 or more),
`+` (1 or more with -E), `?` (0 or 1 with -E), `[chars]` (character class),
`[^chars]` (negated class), `{n,m}` (repeat count with -E).
`\b` word boundary (with -E or -P). Anchoring matters for precision.
`grep -P` for Perl regex (lookahead, lookbehind, non-greedy).

**Level 4:**
`grep -o` output only matched part (not whole line). Powerful for
extracting data: `grep -oP "HTTP \K\d{3}" access.log` extracts HTTP
status codes. `-h` suppress filename in multi-file output. `--color=auto`
highlight matches. `--binary-files=text` treat binary as text.
`zgrep` = grep in compressed files. `bzgrep` for bzip2. Performance:
`grep -F` (fixed string) is faster than regex for literal strings.

**Level 5:**
`grep` in log monitoring pipelines: `tail -f app.log | grep --line-buffered "ERROR"`.
`--line-buffered` needed for real-time output in pipes. Multi-pattern from file:
`grep -F -f patterns.txt log.txt`. Approximate matching: `agrep` (not standard but
available). Parallel grep: `parallel grep pattern ::: file1 file2 file3`.
For massive log files: `ripgrep (rg)` - a modern grep replacement written
in Rust, faster on multi-core for large files, gitignore-aware, PCRE2.

---

### Code Example

**BAD - grep antipatterns:**
```bash
# BAD 1: cat | grep (useless cat)
cat /var/log/app.log | grep "ERROR"
# Just: grep "ERROR" /var/log/app.log

# BAD 2: grepping without context (seeing errors but not knowing cause)
grep "NullPointerException" app.log | tail -5
# Shows the exception line only - no context!
# Correct:
grep -A 20 "NullPointerException" app.log | tail -25

# BAD 3: case-sensitive search for log levels
grep "error" app.log   # misses "ERROR", "Error"
# Use: grep -i "error" app.log

# BAD 4: using grep to check if process is running
grep java /proc/*/comm 2>/dev/null
# pgrep is the right tool: pgrep java

# BAD 5: slow regex when literal string suffices
grep -E "literally_this_string" large.log
# Use: grep -F "literally_this_string" large.log
# -F (fixed string) is much faster for non-regex searches
```

**GOOD - production log analysis:**
```bash
# Analyze HTTP 5xx errors in nginx access log:
grep -E " [56][0-9]{2} " /var/log/nginx/access.log | \
    grep -oP "\d{3} (?=\d)" | \
    sort | uniq -c | sort -rn
# Output: count by status code

# Find all unique error types in Java app log:
grep "Exception" app.log | \
    grep -oP "\w+Exception" | \
    sort | uniq -c | sort -rn
# Output: 42 NullPointerException, 15 DatabaseException, ...

# Real-time error monitoring with alerting context:
tail -f /var/log/myapp/app.log | \
    grep --line-buffered -E "ERROR|FATAL" | \
    while read -r line; do
        echo "[ALERT] $line"
        # Could: send to monitoring system
    done

# Find all requests to a specific endpoint with response time:
grep "POST /api/users" /var/log/nginx/access.log | \
    grep -oP '"(POST [^"]+)" \d+ \d+ "\K\d+'  # extract response time

# Count errors per hour:
grep "ERROR" app.log | \
    grep -oP "^\d{4}-\d{2}-\d{2} \d{2}" | \
    sort | uniq -c
# Output: 45 2024-01-15 14 (45 errors in 14:xx hour)

# Find configuration errors across all properties files:
grep -r -n --include="*.properties" \
    -E "^\s*#|^\s*$" \
    /opt/myapp/config/ | head -20
# lines that are comments or empty (to audit config files)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "grep searches file CONTENTS" | grep searches for pattern matches in LINES. It outputs whole matching lines. To match only part of a line, use `-o` (output only matched text). grep has no awareness of structure within lines unless you use regex with capture. |
| "grep with regex automatically handles all syntax" | BRE (default) has different syntax than ERE (-E) and PCRE (-P). In BRE: `+`, `?`, `|` are literal. In ERE: they're metacharacters. Always use `-E` to avoid confusion. `grep "a+b"` matches literal "a+b". `grep -E "a+b"` matches "ab", "aab", "aaab", etc. |
| "grep -v removes matching lines" | `-v` prints lines that do NOT match. It's used to FILTER OUT patterns. `grep -v "DEBUG"` shows everything EXCEPT debug lines. Very useful for noise removal in log analysis. |
| "grep is slow on large files" | Default grep is fast. For huge files (>100GB), consider `ripgrep` (rg) which parallelizes across CPU cores and memory maps files. `grep -F` (fixed string) is faster than regex. Avoid `.*` at the start of patterns (causes backtracking). |
| "egrep and grep -E are different commands" | `egrep` is just `grep -E` (extended regex). Same for `fgrep` = `grep -F`. These aliases exist for backward compatibility. Prefer `grep -E` and `grep -F` in scripts for clarity. |

---

### Failure Modes & Diagnosis

**grep -r is very slow on large directories:**
```bash
# BAD: searching entire node_modules, .git, build output
grep -r "TODO" /opt/project
# May scan thousands of binary files and minified JS

# GOOD: use --include and --exclude-dir
grep -r "TODO" /opt/project \
    --include="*.java" \
    --exclude-dir=".git" \
    --exclude-dir="target" \
    --exclude-dir="node_modules"

# BETTER: use ripgrep (rg) - respects .gitignore automatically
rg "TODO" /opt/project
```

**grep returns exit code 1 in scripts (no matches = failure):**
```bash
# Problem: set -e causes script to exit when grep finds nothing
set -e
grep "ERROR" app.log   # if no errors: exits with 1 -> script aborts!

# FIX 1: use || true to ignore grep's exit code
grep "ERROR" app.log || true

# FIX 2: use -q and if statement
if grep -q "ERROR" app.log; then
    echo "Errors found"
else
    echo "No errors"
fi

# FIX 3: capture count and check
error_count=$(grep -c "ERROR" app.log || true)
# grep -c returns 0 when no matches (exit 1), but || true catches it
```

---

### Related Keywords

**Foundational:**
LNX-008 (Files), LNX-015 (Standard Streams), LNX-016 (Pipes)

**Builds on this:**
LNX-043 (Regular Expressions), LNX-027 (sed), LNX-028 (awk)

**Related:**
LNX-009 (File Viewing), LNX-025 (find)

---

### Quick Reference Card

| Flag | Purpose |
|------|---------|
| `-i` | Case-insensitive |
| `-v` | Invert match (non-matching lines) |
| `-n` | Show line numbers |
| `-c` | Count matching lines |
| `-l` | List filenames with matches |
| `-r` | Recursive directory search |
| `-A N` | N lines after match |
| `-B N` | N lines before match |
| `-C N` | N lines before and after |
| `-E` | Extended regex (OR, +, ?) |
| `-F` | Fixed string (no regex, fast) |
| `-P` | Perl-compatible regex |
| `-o` | Output only matching part |
| `-q` | Quiet (exit code only) |
| `--include` | Filter files by pattern |
| `--exclude-dir` | Skip directory |

**3 things to remember:**
1. `grep -C N` = context around matches - essential for log triage
2. `grep -v` = invert = remove noise, not add matches
3. `grep -q` = quiet mode for scripts (use exit code, not output)

---

### Transferable Wisdom

`grep`'s pattern of "filter lines matching a predicate" appears everywhere:
SQL WHERE clauses, Elasticsearch queries, Splunk/Datadog log queries,
Kubernetes `kubectl get pods -l app=myapp`, Java Stream's `.filter()`,
Python list comprehensions `[x for x in data if condition]`. The mental
model is the same: you have a stream, you apply a predicate, only matching
items pass through.

`grep -v` (invert/exclude) is the complement pattern: remove known noise,
keep the rest. This appears in: `.gitignore` (exclude files from tracking),
Kubernetes label selectors with `!=`, `NOT IN` SQL, stream `.filter(x -> !x.isDebug())`.
Knowing what to EXCLUDE is often more powerful than knowing what to INCLUDE.

---

### The Surprising Truth

The name "grep" comes from the `ed` editor's command `g/re/p`: globally
search for a regular expression and print. In ed (1969): `g` = global
(apply to all lines), `re` = regular expression, `p` = print. This `g/re/p`
command was so useful that Ken Thompson extracted it into a standalone
utility in 1974. The name stuck as an acronym. The `g/re/p` lineage is
why vi (built on ex, built on ed) uses `/pattern` for search and `g`
prefix for global operations. When you type `:g/pattern/d` in vim to
delete all matching lines, you're using the same `g/re/p` command from
1969 that eventually became the `grep` utility.

---

### Mastery Checklist

- [ ] Can search files and piped input for patterns using grep
- [ ] Can use -A/-B/-C context flags for log analysis
- [ ] Can combine grep with pipes to build log analysis pipelines
- [ ] Can use extended regex (-E) with OR and other metacharacters
- [ ] Can use grep -q in scripts to test for pattern existence

---

### Think About This

1. `grep "error" app.log | wc -l` gives you error count. But `grep -c "error" app.log`
   also gives error count. Are these always the same? When might they differ?
   Which is more efficient?

2. You're tailing a log file with `tail -f app.log | grep "ERROR"`. You see
   errors but with a delay - sometimes the output appears in bursts after
   10-20 lines of non-ERROR output. What is causing this buffering behavior,
   and how do you fix it?

3. `grep -r "password" /etc/` might find configuration files with hardcoded
   passwords. But it also might find many false positives (like documentation
   explaining what the password field means). How would you refine the grep
   command to find only lines with ACTUAL password values (like `password=secret`
   or `password: mysecret`) while excluding comments and documentation?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you search for a string across all files in a directory recursively?
A: `grep -r "search_string" /path/to/directory`. Key additions for real use: `-n` (line numbers) to know exactly where to find each match, `--include="*.java"` to limit to Java files only (much faster than scanning everything), `--exclude-dir=".git"` to skip version control metadata, `-l` if you only need which files contain the string. Full production command: `grep -rn "TODO" /opt/myproject --include="*.java" --exclude-dir=".git" --exclude-dir="target"`. Modern alternative: `rg "TODO"` (ripgrep) - automatically respects .gitignore, parallelizes across CPUs, faster on large codebases.

**Intermediate:**
Q: How do you find all lines in a Java application log that contain an exception, then show the 15 lines after each exception (the stack trace)?
A: `grep -A 15 "Exception\|Error" app.log`. The `-A 15` flag outputs 15 lines After each matching line. This captures the typical stack trace. Refinements: (1) The log may have "expected" exceptions. Filter them: `grep -A 15 "Exception" app.log | grep -v "ClientAbortException"`. (2) Separate stack traces visually: `grep -A 15 "Exception" app.log` shows a `--` separator between non-contiguous match groups. (3) Combined: for the most recent error, `grep -A 15 "Exception" app.log | tail -20`. (4) Real-time: `tail -f app.log | grep --line-buffered -A 15 "Exception"` - the `--line-buffered` is essential for real-time grep in pipelines (otherwise output is delayed until buffer fills).

**Expert:**
Q: Write a grep pipeline to extract the top 10 most frequent IP addresses making requests to an nginx access log, along with their request counts.
A:
```bash
grep -oP '^\d{1,3}(\.\d{1,3}){3}' /var/log/nginx/access.log \
    | sort \
    | uniq -c \
    | sort -rn \
    | head -10
```

Breakdown: `grep -oP '^\d{1,3}(\.\d{1,3}){3}'` = extract only the IP address from each line using Perl regex (`-o` = output only match, `^` = start of line, `\d{1,3}(\.\d{1,3}){3}` = IPv4 pattern). `sort` = sort IPs alphabetically so identical IPs are adjacent. `uniq -c` = count consecutive identical lines. `sort -rn` = sort numerically in reverse (highest first). `head -10` = top 10. Alternative with awk (no regex extraction needed): `awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10`. The awk version uses the first field ($1) which is the IP in standard nginx log format - simpler and faster. The grep approach works on logs where the IP isn't the first field.
