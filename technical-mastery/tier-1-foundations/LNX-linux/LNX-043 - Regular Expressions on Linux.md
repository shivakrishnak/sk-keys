---
id: LNX-043
title: "Regular Expressions on Linux"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-017, LNX-016
used_by: LNX-066
related: LNX-016, LNX-017, LNX-066
tags: [regex, grep, sed, awk, regular-expression, pattern, PCRE, ERE, BRE]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/lnx/regular-expressions/
---

## TL;DR

Regular expressions (regex) are patterns that match text. Linux tools:
`grep "pattern" file` (search), `sed 's/old/new/g' file` (replace),
`awk '/pattern/{print $2}' file` (extract). Core patterns: `.` (any char),
`*` (zero or more), `+` (one or more), `?` (zero or one), `^` (line start),
`$` (line end), `[abc]` (character class), `\d` or `[0-9]` (digit).
Use `grep -E` or `egrep` for extended regex (ERE). Use `grep -P` for
PCRE (Perl-compatible, full power). Master `grep -E` and basic sed/awk
for 90% of text processing needs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-043 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | regex, grep, sed, awk, regular expression, pattern matching, ERE, BRE, PCRE |
| **Prerequisites** | LNX-017, LNX-016 |

---

### The Problem This Solves

Searching log files for errors: `grep "ERROR" app.log` finds lines with
ERROR but also "ERRORED", "NO_ERROR". `grep -E "^ERROR\b"` finds lines
starting with exactly "ERROR" as a word. Extracting IP addresses from
logs: `grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' access.log` extracts
all IPs. Regex is the foundation of structured text processing in Linux.

---

### Textbook Definition

**Regular Expression (regex)**: A sequence of characters that defines a
search pattern. Used by text processing tools to match, extract, and
transform text.

**BRE (Basic Regular Expressions)**: The default regex flavor in `grep`
and `sed`. Special characters like `+`, `?`, `|`, `{n}`, `(groups)`
must be escaped with `\` to have special meaning.

**ERE (Extended Regular Expressions)**: Supported by `grep -E` (or `egrep`)
and `awk`. Special characters `+`, `?`, `|`, `{n}`, `(groups)` work
without escaping. ERE is more readable.

**PCRE (Perl-Compatible Regular Expressions)**: Supported by `grep -P`.
Full regex power: lookahead, lookbehind, named groups, `\d`, `\w`, `\s`.
Most powerful but not available everywhere.

---

### Understand It in 30 Seconds

```bash
# === Core patterns ===
# . = any single character
# * = zero or more of previous
# + = one or more of previous (ERE)
# ? = zero or one of previous (ERE)
# ^ = start of line
# $ = end of line
# [abc] = any of: a, b, c
# [a-z] = range: lowercase letter
# [^abc] = NOT a, b, or c
# \d = digit [0-9] (PCRE only; use [0-9] in ERE)
# | = OR (ERE)
# (abc) = group
# {n} = exactly n times (ERE)
# {n,m} = n to m times (ERE)
# \b = word boundary (PCRE)

# === grep examples ===
grep "error" app.log                # lines containing "error"
grep -i "error" app.log             # case insensitive
grep -v "DEBUG" app.log             # lines NOT containing DEBUG
grep -n "error" app.log             # show line numbers
grep -c "error" app.log             # count matching lines
grep -o "ERROR.*" app.log           # show only matched part
grep -E "ERROR|WARN" app.log        # ERE: ERROR or WARN
grep -E "^[0-9]{4}-[0-9]{2}" app.log  # lines starting with date
grep -P "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" access.log  # PCRE IP

# Extract specific pattern:
grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' access.log  # extract IPs
grep -oE '"GET [^"]*"' access.log    # extract GET requests

# === sed examples ===
sed 's/foo/bar/' file.txt            # replace first foo per line
sed 's/foo/bar/g' file.txt           # replace all foo per line
sed 's/foo/bar/gi' file.txt          # case insensitive
sed -i 's/foo/bar/g' file.txt        # edit in-place (modifies file!)
sed -n '10,20p' file.txt             # print lines 10-20
sed '/pattern/d' file.txt            # delete lines matching pattern
sed 's/^\s*//' file.txt              # strip leading whitespace

# === awk examples ===
awk '{print $1}' file.txt            # print first field (space-delimited)
awk -F: '{print $1}' /etc/passwd     # use : as delimiter, print first field
awk '/error/{print $0}' app.log      # print lines matching "error"
awk '{sum += $5} END {print sum}' file  # sum column 5
awk 'NR==5' file.txt                 # print line 5
awk 'NR>=5 && NR<=10' file.txt       # print lines 5-10
```

---

### First Principles

**BRE vs ERE vs PCRE comparison:**
```
Pattern: match one or more digits

BRE (grep without -E):
  grep '[0-9]\+' file     # \+ needed for "one or more"
  grep '[0-9][0-9]*' file # alternative: digit followed by zero-or-more

ERE (grep -E):
  grep -E '[0-9]+' file   # + works without escaping (more readable)

PCRE (grep -P):
  grep -P '\d+' file      # \d shorthand for [0-9]

Pattern: match "color" or "colour"
BRE: grep 'colou\?r' file      # \? = zero or one
ERE: grep -E 'colou?r' file    # ? = zero or one
PCRE: grep -P 'colou?r' file

Pattern: match either "cat" or "dog"
BRE: grep 'cat\|dog' file      # \| for alternation
ERE: grep -E 'cat|dog' file    # | works directly
PCRE: grep -P 'cat|dog' file

Recommendation: use ERE (grep -E) by default in scripts.
Use PCRE (grep -P) when you need \d, \w, \s, lookahead/lookbehind.
```

**Anchors and word boundaries:**
```bash
# ^ and $ anchor to line start/end:
echo "error in database" | grep "^error"    # matches (starts with error)
echo "no error found" | grep "^error"       # no match
echo "has error" | grep "error$"            # no match
echo "has an error" | grep "error$"         # matches (ends with error)

# \b word boundary (PCRE only):
echo "errors found" | grep -P "\berror\b"    # no match (errors != error)
echo "error found" | grep -P "\berror\b"     # matches

# Equivalent in ERE (using [^a-zA-Z] to approximate):
echo "errors found" | grep -E "(^|[^a-zA-Z])error([^a-zA-Z]|$)"  # no match
```

---

### Thought Experiment

Parsing Apache access logs to find slow requests (> 5 seconds):

```bash
# Sample log line:
# 1.2.3.4 - - [01/Jan/2025:12:00:00 +0000] "GET /api/heavy HTTP/1.1" 200 1234 5.234

# Fields: IP - - [date] "method path protocol" status bytes response_time

# Find slow requests (response time > 5.0):
awk '$NF > 5.0 {print $7, $NF}' access.log
# $NF = last field (response time), $7 = request path

# Find 5xx errors in last hour:
START=$(date -d "1 hour ago" "+%d/%b/%Y:%H")
grep -E "^\S+ - - \[$START" access.log | awk '$9 >= 500'

# Top 10 most requested endpoints:
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head 10

# Extract unique IPs that made 500 errors:
grep -E '" 500 ' access.log | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | \
    sort -u

# One-liner to find IPs with >100 requests (potential DoS):
awk '{print $1}' access.log | sort | uniq -c | \
    awk '$1 > 100 {print $2, $1}' | sort -rn
```

---

### Mental Model / Analogy

```
Regex = smart search terms (wildcards on steroids)

Shell glob:  *.log = "any filename ending in .log"
             Simple: only works on filenames

Regex: .*\.log$ = "any text ending with .log"
             Powerful: works on any text, not just filenames

.   = wildcard for ONE character (like ? in shell globs)
.*  = wildcard for ANY number of characters (like * in shell globs)
    (but different: .* matches in the MIDDLE, shell * can't)

^error = "the word error at the START of the line"
         (like requiring the first word to be "error")

error$ = "the word error at the END of the line"
         (like requiring the last word to be "error")

[aeiou] = "any vowel" (character menu: choose one)
[^aeiou] = "anything that's NOT a vowel" (excluded menu)

BRE = strict mode (special chars need backslash)
ERE = friendly mode (special chars work as-is)
PCRE = expert mode (shortcuts like \d, lookaheads)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`grep "string" file` (literal search), `grep -i` (case insensitive),
`grep -v` (invert), `grep -n` (line numbers), `grep -r` (recursive).
`sed 's/old/new/g'` (replace). These cover basic text searching and
editing.

**Level 2:**
ERE with `grep -E`: character classes `[0-9]`, anchors `^$`, quantifiers
`+?*`, alternation `|`, groups `()`. `awk` for field extraction with `-F`
separator. `grep -o` to extract only the matched portion. `sed -i` for
in-place editing (backup: `sed -i.bak`).

**Level 3:**
Named groups in PCRE: `(?P<name>pattern)`. Lookahead: `(?=pattern)`,
lookbehind: `(?<=pattern)`. Non-greedy: `.*?`. `awk` programs: `BEGIN`,
`END`, `NR` (line number), `NF` (field count), associative arrays in awk.
sed multi-line operations, `sed -n '/start/,/end/p'` for range extraction.

**Level 4:**
`perl -pe 's/pattern/replacement/g'` for complex transformations (Perl
regex in one-liners). `python3 -c "import re, sys; ..."` for complex
extraction. `ripgrep (rg)`: faster alternative to grep with better defaults.
`jq` for JSON, `xmllint` for XML - when regex isn't the right tool.

**Level 5:**
Catastrophic backtracking: regex engine performance degradation on
ambiguous patterns with many alternatives. `(a+)+` matching "aaaaaX" -
exponential backtracking. PCRE atomic groups `(?>pattern)` and possessive
quantifiers `++` prevent backtracking. Log aggregation systems (Elasticsearch,
Splunk) use their own regex derivatives. Go's RE2 library (used by Kubernetes,
Prometheus) guarantees linear-time matching - no backtracking, no lookaheads.
Understanding which regex engine you're using matters for both correctness
and performance.

---

### Code Example

**BAD - regex mistakes:**
```bash
# BAD 1: Using grep without -E for extended patterns (BRE confusion):
grep "error|warning" app.log   # BRE: searches for literal "error|warning"
# Finds nothing (no literal | in log), missing warning lines!

# GOOD: use -E for alternation:
grep -E "error|warning" app.log  # finds lines with either

# BAD 2: Greedy matching capturing too much:
echo "start middle end" | grep -oE "start.*end"
# Output: "start middle end" (greedy: matches as much as possible)
# If line was: "start thing1 end start thing2 end"
# Output: entire line (greedy matches from first start to LAST end)

# GOOD: use non-greedy (PCRE only):
echo "start middle end" | grep -oP "start.*?end"
# Or: use character class to exclude the separator:
echo "<tag>content</tag>" | grep -oE "<tag>[^<]*</tag>"  # works in ERE

# BAD 3: sed in-place without backup:
sed -i 's/old_config/new_config/g' /etc/nginx/nginx.conf
# If you made a mistake: original gone! No recovery.

# GOOD: backup before in-place edit:
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
sed -i 's/old_config/new_config/g' /etc/nginx/nginx.conf
# Or: sed -i.bak 's/...' file  (creates file.bak automatically)

# BAD 4: Parsing structured data (HTML, JSON, XML) with regex:
curl https://api.example.com/data.json | grep -o '"id":[0-9]*'
# Works for simple cases but breaks with:
# - Nested JSON
# - Different field ordering
# - Whitespace variations
# - Unicode characters

# GOOD: use the right tool for structured data:
curl https://api.example.com/data.json | jq '.id'
```

**GOOD - practical regex patterns:**
```bash
# Validate IP address format:
is_valid_ip() {
    local ip="$1"
    if [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
        # Check each octet is 0-255:
        IFS='.' read -ra octets <<< "$ip"
        for octet in "${octets[@]}"; do
            if [[ $octet -gt 255 ]]; then
                return 1
            fi
        done
        return 0
    fi
    return 1
}

# Extract version numbers from a file:
grep -oE '[0-9]+\.[0-9]+\.[0-9]+' pom.xml | head -1

# Find Java classes that import a specific package:
grep -rlE "^import org\.springframework" src/main/java/

# Parse nginx access log for response time stats:
awk '{
    time = $NF
    sum += time
    count++
    if (time > max) max = time
    if (min == 0 || time < min) min = time
}
END {
    printf "Count: %d, Avg: %.3f, Min: %.3f, Max: %.3f\n",
           count, sum/count, min, max
}' /var/log/nginx/access.log

# Find lines with invalid email format for reporting:
grep -vP "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" emails.txt

# Multi-line sed: replace between markers:
sed -n '/BEGIN/,/END/p' config.txt   # print between BEGIN and END
sed '/BEGIN/,/END/d' config.txt      # delete between BEGIN and END
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`*` means any characters in regex (like in shell)" | In regex, `*` means "zero or more of the PREVIOUS character or group." To match "any characters," you need `.*` (`.` = any char, `*` = zero or more of it). Shell glob `*.log` maps to regex `.*\.log$`. They look similar but are different languages with different rules. |
| "Regex can parse HTML/XML/JSON perfectly" | Regex can match patterns in text, but cannot parse nested structures (like HTML tags, nested JSON). The classic example: regex cannot reliably parse HTML because tags can nest arbitrarily. Use proper parsers: `jq` for JSON, `xmllint` for XML, `python3 -c "from html.parser import..."` for HTML. Regex works for simple patterns but fails on structured, nested formats. |
| "`grep 'pattern'` and `grep -E 'pattern'` are the same" | In BRE (no -E): `+`, `?`, `|`, `()`, `{}` are literal characters. In ERE (-E): they're special (metacharacters). `grep 'a+b'` matches literal "a+b". `grep -E 'a+b'` matches "ab", "aab", "aaab", etc. The difference causes subtle bugs when not using -E. |
| "Regex is the same across all Linux tools" | Each tool has its own regex engine and dialect. `grep` BRE, `grep -E` ERE, `grep -P` PCRE, `awk` ERE with minor differences, `sed` BRE, Python `re` (PCRE-like), Go RE2 (no lookaheads). Some features work in one dialect but not another. Always test patterns with the specific tool you're using. |
| "Dot (.) matches any character including newline" | By default, `.` does NOT match newline (`\n`). `grep -E "start.+end"` won't match if "end" is on a different line. PCRE `grep -P "(?s)start.+end"` (the `(?s)` flag enables dot-matches-newline). In sed and awk, `.` also doesn't match newline in single-line mode. Multi-line matching requires different approaches. |

---

### Failure Modes & Diagnosis

**Greedy matching causes too-broad matches:**
```bash
# Problem: extracting JSON values
echo '{"name":"Alice","role":"admin"}' | grep -oE '"[^"]*":"[^"]*"'
# Correctly outputs: "name":"Alice" and "role":"admin"

# But with greedy:
echo '{"name":"Alice","role":"admin"}' | grep -oE '".*"'
# Greedy: matches from first " to LAST " -> entire string!

# Fix: use character class to exclude delimiter:
grep -oE '"[^"]*"' file   # matches content between quotes (not crossing quotes)
# Or: use PCRE non-greedy:
grep -oP '".*?"'           # non-greedy: stops at first "

# Debugging: add -o to see only matched portions:
echo 'test string' | grep -oE "pattern"
# Shows exactly what's being matched, revealing greedy issues
```

---

### Related Keywords

**Foundational:**
LNX-017 (Shell Scripting Basics), LNX-016 (Text Processing)

**Builds on this:**
LNX-066 (Bash Advanced Features)

**Related:**
LNX-042 (Bash Conditionals)

---

### Quick Reference Card

| Pattern | Meaning |
|---------|---------|
| `.` | Any single character |
| `*` | Zero or more of previous |
| `+` | One or more (ERE) |
| `?` | Zero or one (ERE) |
| `^` | Start of line |
| `$` | End of line |
| `[abc]` | Any of: a, b, c |
| `[^abc]` | NOT a, b, or c |
| `\d` | Digit (PCRE only) |
| `a\|b` | a or b (ERE: `a|b`) |

**grep flags:** `-i` case-insensitive, `-v` invert, `-o` match only, `-E` ERE, `-P` PCRE, `-r` recursive

**3 things to remember:**
1. Use `grep -E` for extended regex (makes `+`, `?`, `|` work without backslash)
2. In regex `*` means "zero or more of previous" not "any characters" - use `.*` for "any characters"
3. Don't parse JSON/HTML/XML with regex - use `jq`, `xmllint`, or a parser

---

### Transferable Wisdom

Regex is universal: Java `Pattern.compile()`, Python `import re`, JavaScript
`/pattern/`, Go `regexp.MustCompile()`, Elasticsearch query DSL, Nginx
`location ~`, Spring `@PathVariable` with regex, log aggregation tool
(Logstash grok patterns are named regex patterns). The same patterns appear
everywhere. Mastering regex in `grep`/`sed`/`awk` translates directly.

The PCRE engine is particularly widespread: Nginx, Apache, PHP, Perl, Python
`re` module, JavaScript (with minor differences), PostgreSQL `~` operator,
grep -P all use PCRE or PCRE-compatible engines. Go and Rust deliberately
chose RE2 (linear-time guarantee) over PCRE. Understanding the trade-off
(PCRE power/backtracking risk vs RE2 safety) is an advanced pattern.

---

### The Surprising Truth

The `.*` pattern in a regex (greedy, any characters, unlimited) is computationally
safe in most contexts but can cause "catastrophic backtracking" in specific
patterns. The regex `^(a+)+$` matching "aaaaaX" causes some engines to take
exponential time: the engine tries every possible way to group the "a"s before
concluding no match. This vulnerability (ReDoS - Regular Expression Denial of
Service) is a real security issue: crafted input to a vulnerable regex can
bring a web server to its knees. OWASP lists it as a security concern. Node.js,
Java, Python - all use backtracking regex engines vulnerable to ReDoS. The
exploit: find a web app that validates input with regex, craft input that
triggers catastrophic backtracking, send it repeatedly. Defense: use RE2
(Go, Rust, or the `re2` library), or validate regex patterns with a ReDoS
detector (e.g., `safe-regex` npm package), or set regex timeout limits.

---

### Mastery Checklist

- [ ] Can use grep with -E for extended patterns including alternation and quantifiers
- [ ] Can use sed for in-place substitution with proper backup
- [ ] Can use awk to extract specific fields from structured text
- [ ] Can write a regex to match common patterns (IP, email, date)
- [ ] Understands the difference between BRE, ERE, and PCRE

---

### Think About This

1. You want to extract all email addresses from a log file. You write:
   `grep -oE "[a-zA-Z0-9.]+@[a-zA-Z0-9.]+\.[a-zA-Z]{2,4}" emails.txt`.
   But valid email addresses like `user+tag@example.com` and
   `"user name"@example.com` are missed, while `not.an.email@.domain`
   is wrongly matched. What are the fundamental limitations of regex
   for email validation? When is "good enough" acceptable?

2. `sed -i 's/password=.*/password=REDACTED/g' config.txt` is meant
   to redact passwords from a config file. What happens if the value
   contains special characters like `&` or `\`? (Test with
   `password=abc&def`.) How does sed interpret `&` in the replacement
   string?

3. A log monitoring system uses regex to alert on errors: `grep -E
   "(ERROR|CRITICAL)" app.log`. A developer names a new status
   "NONCRITICAL" and now the alert triggers on every NONCRITICAL event.
   How would you fix the regex to match CRITICAL but not NONCRITICAL?
   What regex construct do you need?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between grep, sed, and awk? When do you use each?
A: All three process text, but for different purposes: `grep`: searches for patterns and filters lines. Use when you want to FIND lines containing a pattern. `-E` for extended regex, `-v` to invert, `-o` for only matched portion. Best for: "find all lines with ERROR," "count occurrences." `sed` (stream editor): transforms text - substitutions, deletions, insertions. Use when you want to MODIFY text. `'s/old/new/g'` replaces text. `-i` for in-place editing. Best for: "replace all occurrences of 'foo' with 'bar'," "delete lines matching pattern." `awk`: processes structured text with field separation. Use when you want to EXTRACT and COMPUTE. Fields: `$1`, `$2`... Delimiter with `-F`. Supports variables, arrays, arithmetic, `BEGIN`/`END` blocks. Best for: "print column 3 of CSV," "sum the 5th field," "count unique values in a column." Rule of thumb: start with grep (do I need to FILTER?), then sed (do I need to SUBSTITUTE?), then awk (do I need to EXTRACT/COMPUTE?). For complex transformations: consider Python or perl.

**Intermediate:**
Q: How would you use awk to analyze an Apache/nginx access log and find the top 5 slowest API endpoints?
A: Apache Combined Log Format includes the request and response time. `awk -F'"' '{print $2}' access.log` extracts the request field. For response time (usually the last field): `awk '{print $NF, $7}' access.log` extracts response time and path. Full pipeline:
```bash
# Parse: extract path and response time (assumed last field)
awk '{
    time = $NF       # last field = response time in seconds
    path = $7        # 7th field = request path (after method)
    # Track max response time per path:
    if (time > max[path]) max[path] = time
    count[path]++
    sum[path] += time
}
END {
    for (path in sum) {
        avg = sum[path] / count[path]
        printf "%.3f avg  %.3f max  %d calls  %s\n",
               avg, max[path], count[path], path
    }
}' access.log | sort -rn | head -5
```
Key awk concepts used: `NF` (number of fields), `$NF` (last field), associative arrays (`max[path]`, `count[path]`), `END` block for final processing, `printf` for formatted output. This approach handles thousands of log lines efficiently in a single pass.

**Expert:**
Q: What is ReDoS (Regular Expression Denial of Service) and how do you prevent it in a web application?
A: ReDoS occurs when a regex engine takes exponential time to determine "no match" on crafted input. Mechanism: backtracking regex engines (NFA-based) try all possible ways to match before giving up. The vulnerability pattern: nested quantifiers like `(a+)+`, `(a|a)+`, or `(a*)*`. Example: `^(a+)+$` matching "aaaaaaaX" - the engine tries every grouping of the "a"s (exponential combinations) before determining no match. Real attack: input like "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaX" (many a's + one invalid char) causes exponential backtracking. Prevention strategies: (1) Input length limits: limit string length before regex evaluation. (2) Safe regex libraries: use RE2 (Go's built-in, Rust regex crate, or `re2` binding for Python/Java/Node). RE2 guarantees O(n) time by avoiding backtracking (trades away lookaheads/lookbehinds). (3) Regex auditing: tools like `safe-regex` (npm), regexploit, or REWORKD detect vulnerable patterns. (4) Timeout: set regex evaluation timeout (Java `Pattern` can be evaluated in a thread with interrupt). (5) Avoid catastrophic patterns: never write `(pattern+)+` or `(a|b+)+`-type structures. Test your regex against edge cases with regex analyzers. Detection: `curl -X POST -d '{"input":"aaaaaaaaaaaaaaX"}' /api/validate` - if response takes >1 second, ReDoS is possible.
