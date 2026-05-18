---
id: LNX-028
title: Text Processing with awk
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-015, LNX-016, LNX-026, LNX-027
used_by: LNX-043, LNX-024
related: LNX-027, LNX-026, LNX-043
tags: [awk, text-processing, field-processing, data-extraction, log-analysis, reporting, CSV]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/lnx/text-processing-awk/
---

## TL;DR

`awk` processes text line by line, splitting each line into fields.
`$1` = first field, `$2` = second, `$NF` = last field. Print only
the third column: `awk '{print $3}'`. Add conditions: `awk '$3 > 100
{print $1, $3}'`. awk is the right tool when grep (line-level) and
sed (substitution) aren't enough: when you need field extraction,
column arithmetic, conditional logic, or summary aggregation from
structured text like log files, CSV, or command output.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-028 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | awk, field processing, text analysis, log processing, gawk, reporting |
| **Prerequisites** | LNX-015, LNX-016, LNX-026, LNX-027 |

---

### The Problem This Solves

`ps aux` output has 11 columns. You need the 5th column (virtual memory)
for all processes where the 4th column (CPU%) exceeds 10. grep can't do
column-aware filtering. sed can substitute but can't calculate. awk can:
`ps aux | awk '$3 > 10.0 {print $1, $2, $3, $5}'` - filter by column,
print selected columns. awk handles structured text (fixed-width columns,
space/comma-delimited) with conditional logic and aggregation.

---

### Textbook Definition

**awk** (named after creators: Aho, Weinberger, Kernighan): A
pattern-scanning and processing language. Processes input line by line,
splitting each line into fields based on a field separator (FS, default:
whitespace). Supports: conditional matching, arithmetic, string functions,
arrays, and built-in variables.

awk's processing model:
```
BEGIN { startup code }      # runs once before any input
/pattern/ { action }        # runs when line matches pattern
condition { action }        # runs when condition is true
{ action }                  # runs for EVERY line
END { summary code }        # runs once after all input
```

Variants: `gawk` (GNU awk, most feature-rich), `mawk` (fast), `nawk`,
`awk` (typically links to one of these on Linux systems).

---

### Understand It in 30 Seconds

```bash
# Basic field access ($0=whole line, $1=first, $NF=last):
echo "Alice 30 Engineer" | awk '{print $1}'     # Alice
echo "Alice 30 Engineer" | awk '{print $2}'     # 30
echo "Alice 30 Engineer" | awk '{print $NF}'    # Engineer (last)
echo "Alice 30 Engineer" | awk '{print $1, $3}' # Alice Engineer

# Print specific fields from command output:
df -h | awk '{print $1, $5}'          # filesystem and use%
ps aux | awk '{print $1, $3, $11}'    # user, cpu%, command
ls -l | awk '{print $5, $9}'          # size, filename

# Conditional: print only rows where 3rd field > 1000
awk '$3 > 1000 {print}' data.txt

# Pattern matching:
awk '/ERROR/ {print}' app.log          # lines matching ERROR (like grep)
awk '/ERROR/ {print $1, $2}' app.log   # date/time of errors

# Skip header (NR > 1 = not the first row):
df -h | awk 'NR > 1 {print $5, $1}'

# Custom field separator (-F option):
awk -F: '{print $1}' /etc/passwd       # first field (username)
awk -F, '{print $2}' data.csv         # second column of CSV

# Calculations:
df -h | awk 'NR>1 {sum += $3} END {print "Total used:", sum}'
```

---

### First Principles

**awk's data model:**
- `NR`: current record (line) number
- `NF`: number of fields in current line
- `$0`: entire current line
- `$1`, `$2`, ..., `$NF`: individual fields
- `FS`: field separator (default: whitespace - any run of spaces/tabs)
- `OFS`: output field separator (default: space)
- `RS`: record separator (default: newline)

**Pattern-action model:**
awk is a rule engine:
```
/pattern/ { action }  = IF line matches pattern THEN do action
condition { action }  = IF condition is true THEN do action
{ action }            = do action for EVERY line (no condition = always)
BEGIN { action }      = do action once at START (before reading input)
END { action }        = do action once at END (after all input)
```

Multiple patterns apply independently:
```awk
/ERROR/ { error_count++ }
/WARN/  { warn_count++ }
END     { print "Errors:", error_count, "Warnings:", warn_count }
```

---

### Thought Experiment

Nginx access log. Business wants: total request count, error count
(5xx), and top 5 endpoint by request count. This is a report from
structured text - perfect for awk:

```bash
# Single awk program to generate a log report:
awk '
{
    total++
    # Extract status code (field 9 in combined log format)
    status = $9
    if (status >= 500) errors++
    
    # Extract endpoint (field 7 = request path)
    endpoint = $7
    endpoints[endpoint]++
}
END {
    print "Total requests:", total
    print "5xx errors:", errors
    print "Error rate:", (errors/total)*100 "%"
    print ""
    print "Top endpoints:"
    
    # Sort by count (awk arrays are unsorted - use asorti in gawk)
    for (ep in endpoints) {
        print endpoints[ep], ep
    }
}
' /var/log/nginx/access.log | sort -rn | head -7
```

This replaces: grep + sed + python script with one awk program.

---

### Mental Model / Analogy

awk is like a **spreadsheet with row-level programming:**

```
Input (each line = one row):
  "Alice 85 Engineering"
  "Bob   92 Marketing"
  "Carol 78 Engineering"

awk splits into columns automatically:
  $1=name, $2=score, $3=dept

awk rules = spreadsheet formulas applied per row:
  $2 > 80          = "score > 80" filter
  {print $1, $2}   = "print columns 1 and 2"
  {total += $2}    = "sum column 2" (accumulate)
  END {print total/NR}  = "print average after all rows"

Unlike a spreadsheet:
- Works on ANY structured text (no GUI needed)
- Processes billions of rows efficiently
- Can mix pattern matching with field operations
```

---

### Gradual Depth - Five Levels

**Level 1:**
`awk '{print $1}'` and `awk -F: '{print $1}' /etc/passwd`. Field
extraction from command output is the #1 use case. Learn `$1`, `$NF`,
`NR`, `-F` for separator. This handles 60% of awk use.

**Level 2:**
Conditions: `awk '$3 > 100 {print $1}'`. Pattern matching:
`awk '/ERROR/ {print}'`. Skip header: `awk 'NR>1'`. Multiple fields
in print: `awk '{print $1, $3}'` (space-separated) vs
`awk '{print $1 "," $3}'` (comma-separated). BEGIN/END for totals.

**Level 3:**
Built-in functions: `length($0)`, `substr($2, 1, 5)`, `split($0, arr, ",")`,
`gsub(/pattern/, "replacement")`, `match($0, /pattern/)`.
Arrays: `count[$1]++` accumulates counts by key. `for (key in arr)`
iterates array. `printf` for formatted output: `printf "%-20s %5d\n", $1, $2`.

**Level 4:**
Multiple input files: awk processes all files as one input stream;
`FILENAME` contains current file name. `getline` reads from files/commands.
`system("cmd")` runs shell commands. Custom RS for multi-line records:
`RS=""` makes blank lines the record separator (paragraph mode). Pipes:
`print | "sort -rn"` in awk programs.

**Level 5:**
awk for ETL: processing large datasets (CSV, TSV, log files) without
loading into memory. awk has O(1) memory: processes one record at a
time. Contrast with Python/pandas which loads entire dataset. For 1TB
log files: awk is still viable. gawk extensions: POSIX compliance,
network I/O, TCP client/server, bitwise operations. In production:
awk for log aggregation scripts, metrics collection, report generation.
Modern alternatives: `miller (mlr)` for CSV/JSON, Python pandas for
analytics, but awk remains faster for simple aggregations.

---

### Code Example

**BAD - using wrong tool instead of awk:**
```bash
# BAD: using cut when fields aren't fixed-width
ps aux | cut -c 66-   # cutting by character position - fragile!
# Better:
ps aux | awk '{print $11}'  # print command name (field 11)

# BAD: multiple grep/sed to extract data
df -h | grep -v "Filesystem" | sed 's/%//' | awk '{print $5}'
# The grep -v and sed are unnecessary with awk:
df -h | awk 'NR>1 {gsub(/%/,"",$5); print $5}'

# BAD: not using awk for CSV when you should
cat data.csv | cut -d, -f2  # cut doesn't handle quoted fields!
# "field1","field,with,commas","field3"
# cut breaks on the comma inside quotes!
# Better: awk -F, handles simple CSV
# Best: use python csv module for quoted fields
```

**GOOD - production awk patterns:**
```bash
# Extract username and shell from /etc/passwd, tab-separated:
awk -F: '{printf "%-20s %s\n", $1, $7}' /etc/passwd

# Count HTTP status codes in nginx log:
awk '{count[$9]++} END {for (s in count) print count[s], s}' \
    /var/log/nginx/access.log | sort -rn

# Find processes using more than 1% CPU:
ps aux | awk 'NR>1 && $3 > 1.0 {print $1, $2, $3, $11}'

# Sum file sizes in a directory listing:
ls -l | awk 'NR>1 && /^-/ {total += $5} END {
    printf "Total: %.2f MB\n", total/1024/1024
}'

# Parse application log, report average response time by endpoint:
# Log format: timestamp endpoint status response_time_ms
awk '
$3 == 200 {
    count[$2]++
    total[$2] += $4
}
END {
    printf "%-40s %8s %12s\n", "Endpoint", "Count", "Avg(ms)"
    for (ep in count) {
        printf "%-40s %8d %12.1f\n", ep, count[ep],
               total[ep]/count[ep]
    }
}
' app.log | sort -k3 -rn

# Convert CSV to INSERT statements for database seeding:
awk -F, 'NR>1 {
    gsub(/'"'"'/, "'\'''\''", $2)   # escape single quotes
    printf "INSERT INTO users VALUES (%s, '"'"'%s'"'"', '"'"'%s'"'"');\n",
           $1, $2, $3
}' users.csv

# Calculate percentile from response times (95th percentile):
awk '{times[NR]=$1}
END {
    asort(times)
    p95 = int(NR * 0.95)
    print "p95:", times[p95], "ms"
}' response_times.txt
```

---

### awk Quick Reference

```
BUILT-IN VARIABLES:
  NR     Current record (line) number
  NF     Number of fields in current record
  $0     Entire current record
  $1..$NF  Individual fields
  FS     Field separator (default: whitespace)
  OFS    Output field separator (default: space)
  RS     Record separator (default: newline)
  FILENAME  Current filename
  
BUILT-IN FUNCTIONS:
  length(str)        Length of string
  substr(str,s,l)    Substring from position s, length l
  split(str,arr,sep) Split string into array
  sub(re,rep,str)    Replace first match
  gsub(re,rep,str)   Replace all matches
  match(str,re)      Find regex, sets RSTART/RLENGTH
  sprintf(fmt,...)   Formatted string (like printf)
  toupper/tolower    Case conversion
  int(x)             Integer part
  
OPERATORS:
  + - * / %         Arithmetic
  > >= < <= == !=   Comparison (numeric or string)
  ~ !~              Regex match / not match
  && ||             Logical AND/OR
  !                 Logical NOT
  ? :               Ternary
  
CONTROL FLOW:
  if (cond) { ... } else { ... }
  while (cond) { ... }
  for (init; cond; incr) { ... }
  for (key in array) { ... }
  next     Skip to next record
  exit     Stop processing
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "awk fields are split by whitespace strictly" | Default FS is whitespace, but any RUN of spaces/tabs counts as one separator. Leading whitespace is ignored. For CSV with commas: `awk -F,`. For colon: `awk -F:`. For tab: `awk -F'\t'`. For regex: `awk -F'[,;|]'`. |
| "awk arrays need to be declared" | awk arrays are dynamically typed hash maps. `count[$1]++` auto-creates the entry. `for (key in arr)` iterates all keys (in undefined order). `delete arr[key]` removes an entry. No size limit (memory-bounded). |
| "awk processes the whole file into memory" | awk processes one record (line) at a time. Memory usage is constant regardless of file size. Only arrays and variables accumulate (be careful with `arr[line]++` for millions of unique lines). awk can process files larger than RAM. |
| "awk is only for simple one-liners" | awk is a Turing-complete programming language. It has conditionals, loops, functions, arrays, and string operations. Production awk scripts can be hundreds of lines for complex report generation. For very complex logic: Python is clearer, but for structured text processing, awk is often the most efficient. |
| "awk's -F',' handles all CSV" | awk -F, handles simple CSV but NOT RFC 4180 CSV with quoted fields containing commas: `"Smith, John",42`. awk splits on the literal comma inside the quotes. For properly-quoted CSV: use Python's csv module, `mlr`, or `csvkit`. |

---

### Failure Modes & Diagnosis

**awk prints wrong fields after column count changes:**
```bash
# Problem: ps output changed between kernel versions
ps aux | awk '{print $5}'    # was correct, now shows wrong column

# Debug: print field numbers
ps aux | head -3 | awk '{for(i=1;i<=NF;i++) print i, $i}'
# Output shows each field number and value
# Identify which field number has what you want

# Better: use pattern matching instead of field position
ps aux | awk '/java/ {print $1, $2, $11}'
# Or: use a more specific tool (pgrep, ps -p)
```

**Numeric comparison with mixed types:**
```bash
# Problem: "10" > "9" is TRUE numerically but FALSE as strings!
echo "10 9" | awk '{if ($1 > $2) print "first is larger"}'
# Output: first is larger (correct - numeric comparison)

# But string comparison:
echo -e "apple\nbanana" | awk '{arr[NR]=$0}
    END {if (arr[1] > arr[2]) print arr[1]; else print arr[2]}'
# String comparison: "banana" > "apple" (alphabetically)

# awk decides: if both look like numbers, compare numerically.
# To force string comparison: (a "" ) > (b "")
# Force numeric: +$1 > +$2
```

---

### Related Keywords

**Foundational:**
LNX-015 (Standard Streams), LNX-016 (Pipes), LNX-026 (grep), LNX-027 (sed)

**Builds on this:**
LNX-043 (Regular Expressions), LNX-024 (Shell Scripting)

**Related:**
LNX-028 is often paired with sed and grep in text processing pipelines

---

### Quick Reference Card

| Pattern | Purpose |
|---------|---------|
| `awk '{print $1}'` | First field of each line |
| `awk '{print $NF}'` | Last field of each line |
| `awk 'NR>1'` | Skip first line (header) |
| `awk -F: '{print $1}'` | Colon-separated |
| `awk '/pattern/ {print}'` | Lines matching pattern |
| `awk '$3 > 100 {print}'` | Conditional on field value |
| `awk '{sum+=$3} END {print sum}'` | Sum a column |
| `awk '{count[$1]++} END {...}'` | Count by key |
| `awk 'NR==5'` | Print line 5 only |
| `awk '{gsub(/old/,"new"); print}'` | Replace in field |
| `awk '{printf "%-10s %5d\n",$1,$2}'` | Formatted output |

**3 things to remember:**
1. `$1` to `$NF` are fields; `$0` is the whole line; `NR` is line count
2. awk is the right tool when grep/sed isn't enough: field arithmetic, aggregation
3. BEGIN{} for setup, END{} for summary; main block {} runs per line

---

### Transferable Wisdom

awk's field-based processing model is the ancestor of modern data tools.
Apache Spark's DataFrame API, SQL SELECT with WHERE, Pandas df filtering
- all implement the same pattern-action model on structured data. The mental
model: define columns, apply conditions, produce output. awk does this for
text; SQL does it for relational data; Spark does it for distributed datasets.

`count[$field]++` in awk is the MapReduce pattern in miniature: map (extract
key per record) + reduce (accumulate per key). When you see `for (k in count)
print count[k], k | "sort -rn"` - you've implemented word count (the
"Hello World" of MapReduce) in awk. This pattern scales: Hadoop MapReduce,
Spark, Flink all implement the same conceptual pattern on distributed data.

---

### The Surprising Truth

awk was created in 1977 by Alfred V. Aho, Peter J. Weinberger, and Brian
W. Kernighan at Bell Labs. The "k" in awk is Kernighan - the same Kernighan
who co-wrote "The C Programming Language" and co-authored "The Unix Programming
Environment." Kernighan designed awk's C-like syntax deliberately. The
language was so useful that it was included in the first POSIX standard.
Today, gawk (GNU awk) adds features not in the original: `PROCINFO`, TCP/IP
networking via `/inet/`, true multi-dimensional arrays, and first-class
function expressions. But the basic `NR`, `NF`, `$1`, `BEGIN`, `END` model
from 1977 is unchanged and still the right tool for structured text processing
nearly 50 years later. The "one-liner" that awk programs are often used as
was deliberate design: Kernighan wanted patterns that could be typed at the
command line without writing a script file.

---

### Mastery Checklist

- [ ] Can extract specific fields from command output using awk
- [ ] Can filter rows based on field values
- [ ] Can aggregate data using arrays and END blocks
- [ ] Can use awk with custom field separators for CSV/TSV
- [ ] Can combine awk with other tools in pipelines for log analysis

---

### Think About This

1. `awk '{count[$1]++} END {for (k in count) print count[k], k}'`
   groups and counts by the first field. But the output order of
   `for (k in count)` is undefined in awk. How do you produce
   sorted output from this awk program without modifying the awk code
   itself?

2. You have a 100GB nginx access log. You need the total data transferred
   (field 10, bytes) and average response size. Python pandas would load
   the file into memory (not viable). How would you write an awk one-liner
   to compute these statistics in constant memory? What is the memory
   complexity of your solution?

3. `awk -F, '{print $2}' data.csv` works for simple CSV but breaks on:
   `"Smith, John",Engineer,42`. Explain exactly WHY it breaks (trace
   what awk sees). What are your options for handling RFC 4180-compliant
   CSV with quoted fields in shell pipelines?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you print the second column of output from a command using awk?
A: `command | awk '{print $2}'`. For example: `df -h | awk '{print $2}'` prints the Size column. `ps aux | awk '{print $2}'` prints the PID column. Key variables: `$1` = first field, `$2` = second, `$NF` = last field (NF = Number of Fields). Default field separator is whitespace (any run of spaces/tabs). For different separators: `awk -F:` for colon, `awk -F,` for comma. To skip header: `awk 'NR>1 {print $2}'` (NR = record/line number, NR>1 skips line 1). For formatted output: `awk '{printf "%-10s\n", $2}'` (left-aligned, 10 chars wide).

**Intermediate:**
Q: Write an awk command to parse an nginx access log and show the total bytes transferred per unique IP address.
A:
```bash
awk '{bytes[$1] += $10}
END {
    for (ip in bytes) {
        printf "%-15s %d\n", ip, bytes[ip]
    }
}' /var/log/nginx/access.log | sort -k2 -rn | head -20
```

Explanation: `bytes[$1] += $10` - use IP ($1 in combined log format) as array key, accumulate bytes ($10 is bytes sent). `END` block runs after all lines are processed. `for (ip in bytes)` iterates all accumulated IPs. `sort -k2 -rn` sorts by second column (bytes) numerically in reverse. `head -20` shows top 20. Note: `$10` may be `-` (dash) when nginx logs no body size (e.g., 304 Not Modified). You can handle this: `$10 != "-" { bytes[$1] += $10 }`.

**Expert:**
Q: You need to calculate the 95th and 99th percentile response times from a 50GB log file with one response time (in ms) per line. Memory is limited to 2GB. How do you approach this?
A: Sorting a 50GB file + taking percentile is the naive approach but requires ~50GB disk and memory for the sort. Better approaches: (1) Reservoir sampling: keep a random sample of N response times in memory (e.g., 1M samples), then calculate percentile from the sample. This is approximate but uses constant memory. (2) Histogram approach: if response times are bounded (e.g., 0-10000ms), maintain a count per millisecond bucket (10,001 counts = ~80KB). After processing: sum counts from lowest to find 95th/99th percentile.

```bash
# Histogram approach with awk (exact, constant ~80KB memory):
awk '
{
    ms = int($1)   # or $1 if already integer
    if (ms > 10000) ms = 10000  # cap at 10 seconds
    hist[ms]++
    total++
}
END {
    p95_target = int(total * 0.95)
    p99_target = int(total * 0.99)
    cumulative = 0
    for (ms = 0; ms <= 10000; ms++) {
        cumulative += hist[ms]
        if (!p95 && cumulative >= p95_target) p95 = ms
        if (!p99 && cumulative >= p99_target) p99 = ms
    }
    print "p95:", p95 "ms"
    print "p99:", p99 "ms"
}
' response_times.log
```

This processes 50GB with constant memory (10,001 integer counters). The key insight: you don't need all the data simultaneously - you need the distribution. Bucket counting is the standard technique for percentile calculation on large datasets. This same approach is used in production monitoring systems (Prometheus histograms, HdrHistogram library) for memory-efficient percentile tracking.
