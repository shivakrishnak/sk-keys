---
id: LNX-027
title: Text Processing with sed
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-015, LNX-016, LNX-026
used_by: LNX-024, LNX-043
related: LNX-028, LNX-026, LNX-043
tags: [sed, stream-editor, text-processing, substitution, in-place-edit, regex, pipeline]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/lnx/text-processing-sed/
---

## TL;DR

`sed` (stream editor) transforms text line by line. Most important
command: `s/pattern/replacement/g` for substitution. Most important
flag: `-i` for in-place file editing. `sed -i 's/old/new/g' file.txt`
is the standard way to replace text in files without opening an editor.
`sed` is the go-to tool for: config file updates in deployment scripts,
URL transformations, field extraction, and multi-line text manipulation.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-027 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | sed, stream editor, substitution, in-place edit, regex, text transformation |
| **Prerequisites** | LNX-015, LNX-016, LNX-026 |

---

### The Problem This Solves

You need to update a config file on 50 servers: change a database host
from `db-old.example.com` to `db-new.example.com`. Opening each file
in vim 50 times is not an option. `sed -i 's/db-old.example.com/db-new.example.com/g' /etc/myapp/config.properties`
does it in one command. sed automates text transformation at scale:
deployment scripts, config generation, log processing, data migration.

---

### Textbook Definition

**sed** (stream editor): processes text by reading input line by line,
applying editing commands, and writing to output. Unlike interactive
editors, sed is non-interactive and scriptable. It maintains no cursor
or state beyond the current line (and a secondary "hold space" for
advanced use).

Key features:
- Reads input line by line into a "pattern space"
- Applies commands to the pattern space
- Outputs the pattern space (modified or not) by default
- Does not modify input files unless `-i` flag is used
- Supports regular expressions for matching and substitution

---

### Understand It in 30 Seconds

```bash
# The s command (substitute) - most common:
sed 's/old/new/' file         # replace first "old" on each line
sed 's/old/new/g' file        # replace ALL "old" on each line (g=global)
sed 's/old/new/2' file        # replace 2nd occurrence only

# Case-insensitive (GNU sed):
sed 's/error/ERROR/gi' file   # replace all, any case

# In-place editing (modify file directly):
sed -i 's/old/new/g' file     # Linux (GNU sed)
sed -i '' 's/old/new/g' file  # macOS (BSD sed) requires '' after -i

# Delete lines:
sed '/pattern/d' file         # delete lines matching pattern
sed '5d' file                 # delete line 5
sed '5,10d' file              # delete lines 5 through 10

# Print only matching lines (-n = suppress default output):
sed -n '/pattern/p' file      # similar to grep pattern file

# Append and insert:
sed '/pattern/a\new line'     # add line AFTER matching line
sed '/pattern/i\new line'     # add line BEFORE matching line

# Multiple commands:
sed -e 's/foo/bar/g' -e 's/baz/qux/g' file
# Or:
sed 's/foo/bar/g; s/baz/qux/g' file
```

---

### First Principles

**The sed processing cycle:**
For each line of input:
1. Read line into pattern space
2. Apply all commands to pattern space
3. Print pattern space (unless `-n` suppresses)
4. Clear pattern space, read next line

The `-n` flag suppresses step 3, so output only happens when you
explicitly use `p` (print) command. `sed -n 'p'` = same as `cat`.
`sed -n '/pattern/p'` = same as `grep pattern`.

**The substitution command anatomy:**
```
s/pattern/replacement/flags

s       = substitute command
/       = delimiter (can be any char: s|pattern|replacement|g)
pattern = regex or literal string to find
replacement = what to put in its place
flags:
  g = global (all occurrences, not just first)
  i = case-insensitive (GNU sed)
  p = print (with -n: print only when substitution made)
  N = replace Nth occurrence only

In replacement:
  & = the entire matched text
  \1, \2 = capture group references
```

**Alternative delimiters:**
When pattern/replacement contain `/`, use a different delimiter:
```bash
sed 's|/old/path|/new/path|g' file   # use | as delimiter
sed 's#/old/path#/new/path#g' file   # use # as delimiter
# Avoids \/ escaping: s/\/old\/path/\/new\/path/g (ugly)
```

---

### Thought Experiment

Deployment script: promote from staging to production configuration.
All staging references must become production references. Three changes:

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="/opt/myapp/config.properties"

# BAD: edit file three times (reads/writes three times)
sed -i 's/db-staging.example.com/db-prod.example.com/g' "$CONFIG_FILE"
sed -i 's/cache-staging.example.com/cache-prod.example.com/g' "$CONFIG_FILE"
sed -i 's/log.level=DEBUG/log.level=WARN/g' "$CONFIG_FILE"

# GOOD: edit once with multiple expressions
sed -i \
    -e 's/db-staging.example.com/db-prod.example.com/g' \
    -e 's/cache-staging.example.com/cache-prod.example.com/g' \
    -e 's/log.level=DEBUG/log.level=WARN/g' \
    "$CONFIG_FILE"

# BEST for complex configs: use a template system (envsubst, Ansible template)
# But sed is perfect for targeted substitutions in deployment scripts
```

---

### Mental Model / Analogy

sed is like a **conveyor belt with a spray painter:**

```
Input text (conveyor belt):
  Line 1 --> [sed transformer] --> Modified or original Line 1
  Line 2 --> [sed transformer] --> Modified or original Line 2
  Line 3 --> [sed transformer] --> Modified or original Line 3
  ...

The sed transformer has commands (spray painters):
  's/red/blue/g'  - if line contains "red", spray it blue
  '/delete/d'     - if line contains "delete", remove it
  '/insert_after/a\new line' - spray a new line after matched line

The transformer doesn't remember previous lines (stateless by default).
Each line goes in, gets processed by ALL commands, comes out.
-n = conveyor belt with a drain; only explicitly output survives.
```

---

### Gradual Depth - Five Levels

**Level 1:**
`sed 's/old/new/g' file` and `sed -i 's/old/new/g' file`. These two
cover 80% of sed use. The difference: without `-i` sed outputs to
stdout; with `-i` it modifies the file in place.

**Level 2:**
Line addressing: `5s/old/new/` (line 5 only), `5,10s/old/new/` (lines
5-10), `/pattern/s/old/new/` (lines matching pattern). Delete:
`/^#/d` (delete comment lines), `/^$/d` (delete empty lines).
Capture groups: `sed 's/\(first\) \(second\)/\2 \1/'` swap two words
(BRE). With ERE: `sed -E 's/(first) (second)/\2 \1/'`.

**Level 3:**
`-n` + `p` for filtered output (like grep). `q` to quit after N lines:
`sed '10q'` = first 10 lines. `=` prints line number. Hold space:
`h` (copy pattern to hold), `g` (get hold into pattern), `H/G` (append).
Multi-line: `N` joins next line into pattern space. `y/abc/ABC/` 
transliterates characters (like tr).

**Level 4:**
sed scripts (-f file): complex transformations in a script file.
Multi-line transformations: `N; s/\n/ /` joins two consecutive lines.
Print range between patterns:
`sed -n '/START/,/END/p' file` prints from START to END inclusive.
Delete from pattern to end: `sed '/REMOVE_FROM_HERE/,$d'`.
Conditional branching: `b` (branch), `t` (branch if substitution made),
`:label` (branch target).

**Level 5:**
sed for config generation in CI/CD: `envsubst` is often better for
full template substitution. But sed shines for targeted in-place edits.
Complex: generating nginx configs, replacing placeholders in XML/JSON.
Performance: for very large files, awk is more efficient. For simple
substitutions in pipelines: sed is the right tool. In Docker entrypoints:
`sed -i "s/\${DB_HOST}/$DB_HOST/g" config.xml` at container startup.

---

### Code Example

**BAD - sed antipatterns:**
```bash
# BAD 1: forgetting /g (replaces only first occurrence)
sed -i 's/old/new/' config.properties
# If line has: old=value, backup_old=other
# Becomes: new=value, backup_old=other (only first "old" replaced)
# Usually want: sed -i 's/old/new/g' ...

# BAD 2: using / as delimiter with paths
sed -i 's/\/old\/path\/to\/file/\/new\/path\/to\/file/g' config
# Backslash hell! Hard to read, easy to get wrong.
# Use | as delimiter:
sed -i 's|/old/path/to/file|/new/path/to/file|g' config

# BAD 3: not escaping dots in patterns (. matches any char)
sed 's/192.168.1.1/10.0.1.1/g' config
# . matches ANY character: 192X168Y1Z1 would also match!
# GOOD: escape dots:
sed 's/192\.168\.1\.1/10.0.1.1/g' config
# (in replacement, literal . is fine without escape)

# BAD 4: macOS vs Linux -i difference
sed -i 's/old/new/g' file    # Linux: works
sed -i 's/old/new/g' file    # macOS: error! requires backup suffix
sed -i '' 's/old/new/g' file # macOS: works ('' = empty backup suffix)
# For cross-platform scripts:
sed -i'.bak' 's/old/new/g' file  # works on both (creates .bak backup)
```

**GOOD - production sed patterns:**
```bash
# Config substitution in deployment (use | delimiter for paths):
deploy_config() {
    local env="$1"
    local config="/opt/myapp/config.properties"
    
    # Use pipe delimiter to avoid escaping slashes
    sed -i \
        -e "s|db.host=.*|db.host=db-${env}.example.com|" \
        -e "s|cache.host=.*|cache.host=cache-${env}.example.com|" \
        -e "s|app.environment=.*|app.environment=${env}|" \
        "$config"
}
deploy_config "production"

# Strip comments and blank lines from config file:
sed -e '/^#/d' \
    -e '/^[[:space:]]*$/d' \
    application.properties

# Extract values from properties file:
# Get value for key "server.port":
sed -n 's/^server\.port=//p' application.properties
# Output: 8080

# Replace version in Maven pom.xml (careful with XML):
sed -i "s|<version>1\.0\.0</version>|<version>2.0.0</version>|" \
    pom.xml
# Better for XML: use xmllint or Python/xslt instead

# In-place backup then edit:
sed -i.bak 's/old/new/g' config.properties
# Creates config.properties.bak before modifying

# Add line after matching line (add import after package declaration):
sed -i '/^package /a import com.example.NewClass;' MyClass.java

# Delete lines matching pattern (remove all debug logging):
sed -i '/log\.debug(/d' Application.java

# Print lines between START and END markers:
sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p' certs.pem

# Process pipeline output:
kubectl get pods -o wide | sed 's/Running/\x1b[32mRunning\x1b[0m/g'
# Colorize "Running" in green (ANSI escape codes)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`sed -i` always works the same way" | GNU sed (Linux): `-i` takes no argument (or optional extension: `-i.bak`). BSD sed (macOS): `-i` REQUIRES a suffix (even if empty: `-i ''`). Cross-platform scripts must use `-i'.bak'` or check which sed is available. |
| "sed -i modifies the original file directly" | On most implementations, `sed -i` creates a temp file, writes output to it, then replaces the original. The file inode may change. This can affect applications with open file handles. For active log files: use `truncate` or `> file`, not `sed -i`. |
| "sed . matches any character including newline" | By default, `.` in sed does NOT match newline. sed processes line by line; newlines are separators between records. To match across lines, you need `N` to join lines into the pattern space. |
| "sed is only for substitution" | sed has a full command set: `d` (delete), `p` (print), `q` (quit), `a` (append), `i` (insert), `y` (transliterate), `r` (read file), `w` (write file), `b` (branch), `t` (test branch), and more. It's a programmable stream processor. |
| "sed handles all text manipulation" | sed is optimized for line-by-line single-record processing. For multi-column data, report generation, or arithmetic: use `awk`. For JSON/XML: use `jq`, `xmllint`, or Python. The right tool principle: sed for simple substitutions, awk for structured field processing. |

---

### Failure Modes & Diagnosis

**sed -i corrupted the file:**
```bash
# Problem: sed -i with a bad pattern corrupted config.properties
# Prevention: always test without -i first
sed 's/old/new/g' config.properties | head -5  # check output first
# Then if correct:
sed -i 's/old/new/g' config.properties

# Prevention 2: backup with sed
sed -i.bak 's/old/new/g' config.properties
# Restore if wrong:
mv config.properties.bak config.properties

# Prevention 3: use a variable for the file, double-check:
CONFIG="/etc/myapp/config.properties"
echo "Editing: $CONFIG"
grep "old_value" "$CONFIG"    # verify pattern exists
sed -i "s/old_value/new_value/g" "$CONFIG"
grep "new_value" "$CONFIG"    # verify change made
```

**Substitution not working (pattern looks correct):**
```bash
# Debug: print matched lines first
sed -n 's/old/new/p' file    # shows lines where substitution was made
# If no output: pattern doesn't match

# Check for invisible characters:
cat -A file | head -5         # shows ^M for Windows line endings, $ for EOL
# Windows files with \r\n: pattern "end_of_line$" won't match because \r
# Fix Windows line endings:
sed -i 's/\r//' file          # remove carriage returns
# Or: dos2unix file

# Check for tabs vs spaces:
cat -A config.properties      # tabs show as ^I, spaces are spaces
# "key=value" with tab: "key\t=\tvalue" - your sed pattern may not match
```

---

### Related Keywords

**Foundational:**
LNX-015 (Standard Streams), LNX-016 (Pipes), LNX-026 (grep)

**Builds on this:**
LNX-028 (awk), LNX-043 (Regular Expressions)

**Related:**
LNX-024 (Shell Scripting), LNX-022 (vim)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `sed 's/old/new/g' file` | Replace all occurrences |
| `sed -i 's/old/new/g' file` | In-place edit |
| `sed -i.bak 's/old/new/g' file` | In-place with backup |
| `sed '/pattern/d' file` | Delete matching lines |
| `sed -n '/pattern/p' file` | Print only matching lines |
| `sed '5,10d' file` | Delete lines 5-10 |
| `sed -n '5,10p' file` | Print lines 5-10 |
| `sed '/pat/a\new text'` | Add line after match |
| `sed '/pat/i\new text'` | Add line before match |
| `sed 's/\r//'` | Remove Windows line endings |
| `sed '/^#/d; /^$/d'` | Remove comments and blank lines |
| `sed -E 's/(a)(b)/\2\1/'` | Swap captured groups (ERE) |

**3 things to remember:**
1. Use `|` as delimiter when pattern/replacement contains `/`
2. Always test without `-i` first: `sed 's/old/new/g' file | head -5`
3. macOS BSD sed: `-i ''` (empty string required); Linux GNU sed: `-i`

---

### Transferable Wisdom

`sed -i 's/pattern/replacement/g'` is the universal config substitution
tool in deployment automation. The pattern appears in: Ansible `lineinfile`
module (wraps sed semantics), Dockerfile RUN sed (config at build time),
Kubernetes configmap templating, Helm chart value substitution (which uses
Go templates but with the same substitution concept). When you see
`${VAR}` placeholders in config templates, sed is often what replaces them.

The streaming text transformation model (read-transform-write line by line)
is the basis for: Java's `BufferedReader` processing, Python generators,
Kafka Streams, Flink DataStream API. The key insight: you don't need to
hold the whole file in memory to process it. sed implements this for text.

---

### The Surprising Truth

sed was written in 1973 by Lee McMahon at Bell Labs, originally as a
non-interactive version of the ed editor. The same `-i` flag for
in-place editing was added much later and is NOT defined by POSIX - it
was a GNU extension that became de facto standard. POSIX-compliant sed
has no in-place editing. This is why `-i` behaves differently on macOS
(BSD sed follows a stricter POSIX-adjacent interpretation requiring an
explicit backup suffix, even if empty). Scripts using `sed -i` without
`.bak` suffix fail on macOS - a common portability bug when developers
write on Mac but deploy to Linux. The technically portable approach:
`sed 's/old/new/g' file > /tmp/file.new && mv /tmp/file.new file` - but
`sed -i.bak` is the practical cross-platform solution.

---

### Mastery Checklist

- [ ] Can use sed for in-place substitution in files
- [ ] Can delete lines matching a pattern with sed /pattern/d
- [ ] Can use alternative delimiters for paths and URLs
- [ ] Can chain multiple sed expressions with -e
- [ ] Can print only matching lines with sed -n '/pattern/p'

---

### Think About This

1. You use `sed -i 's/debug=true/debug=false/' app.properties` in a
   deployment script. After running, the change is not applied. The config
   file still contains `debug=true`. What are three possible reasons the
   substitution might have failed, and how do you diagnose each?

2. You need to update all occurrences of a hostname in a configuration
   file: `sed -i 's/old-server/new-server/g' config.xml`. But the hostname
   also appears in an XML comment that should NOT be changed:
   `<!-- migrated from old-server, 2023 -->`. How would you modify the
   sed command to skip comment lines?

3. `sed -i 's/password=.*/password=REDACTED/' app.properties` is used
   to redact passwords before sharing logs. What problems might this
   approach have for a YAML configuration file? How would you adapt
   it for the YAML format (`password: secret_value`)?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you use sed to replace a string in a file without opening an editor?
A: `sed -i 's/old_string/new_string/g' filename`. Breakdown: `-i` = in-place (modify the file, not stdout), `s` = substitute command, `old_string` = pattern to find, `new_string` = replacement, `g` = global (replace all occurrences, not just the first on each line). Without `g`: only the first occurrence on each line is replaced. Important: test without `-i` first to verify the output: `sed 's/old_string/new_string/g' filename | head -20`. For macOS (BSD sed): `sed -i '' 's/old_string/new_string/g' filename` (requires empty string argument). For paths with slashes, use a different delimiter: `sed -i 's|/old/path|/new/path|g' filename`.

**Intermediate:**
Q: Write a sed command to extract all IPv4 addresses from a log file.
A: `grep -oP '\d{1,3}(\.\d{1,3}){3}' logfile` - actually grep with -o is cleaner for extraction. But with sed: `sed -n 's/.*\([0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\).*/\1/p' logfile`. Using ERE is cleaner: `sed -En 's/.*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*/\1/p' logfile`. But this only extracts the LAST IP per line if there are multiple. For extraction tasks with complex patterns: prefer `grep -oP` (Perl regex) or `awk`. sed is better for substitution than extraction. The key technique: `sed -n 's/pattern/\1/p'` where `\1` is a capture group - suppresses output (`-n`) then explicitly prints (`p`) only lines where substitution succeeded.

**Expert:**
Q: How do you use sed to process a file and replace configuration values that are set by environment variables at container startup?
A: Pattern for Docker/Kubernetes entrypoint scripts:
```bash
#!/bin/sh
# Substitute environment variables in config template:
sed -e "s|\${DB_HOST}|${DB_HOST}|g" \
    -e "s|\${DB_PORT}|${DB_PORT:-5432}|g" \
    -e "s|\${APP_ENV}|${APP_ENV:-production}|g" \
    /opt/app/config.template > /opt/app/config.properties

# Alternatively, envsubst (part of gettext):
envsubst < /opt/app/config.template > /opt/app/config.properties
```

The sed approach with `${VAR}` in double quotes evaluates the shell variable before sed sees it. Security consideration: if the environment variable contains `/`, `&`, `\`, or newlines, the sed substitution breaks or creates unexpected behavior. For production: validate environment variables before substitution, or use `envsubst` which handles shell variable escaping correctly. For complex templating: Consul Template, Helm, or proper config management (Ansible) are more robust. sed is fine for simple substitutions in controlled environments (Docker containers where you control the variable values), not for user-provided untrusted input.
