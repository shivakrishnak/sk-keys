---
id: LNX-066
title: "Bash Advanced Features (arrays, functions, expansion)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-004, LNX-014
used_by: LNX-070, LNX-099
related: LNX-004, LNX-014, LNX-070
tags: [bash, arrays, associative-arrays, functions, parameter-expansion, process-substitution, here-string, strict-mode, trap, arithmetic]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 66
permalink: /technical-mastery/lnx/bash-advanced-features/
---

## TL;DR

Bash arrays: `arr=(a b c)`, `${arr[0]}`, `${arr[@]}`, `${#arr[@]}`.
Associative arrays: `declare -A map; map[key]=value; ${map[key]}`.
Functions: `fn() { local var=val; ... }`. Parameter expansion: `${var:-default}`,
`${var#prefix}`, `${var%suffix}`, `${var/old/new}`, `${var^^}` (uppercase).
Arithmetic: `$(( expr ))`. Process substitution: `diff <(cmd1) <(cmd2)`.
Here-string: `cmd <<< "string"`. Strict mode: `set -euo pipefail`. `trap`
for cleanup. These features transform bash from a "glue script" tool to a
capable automation language.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-066 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | bash, arrays, associative arrays, functions, parameter expansion, arithmetic, trap, strict mode |
| **Prerequisites** | LNX-004 (Shell basics), LNX-014 (Text processing) |

---

### The Problem This Solves

**Problem 1**: A deployment script exits successfully even though a critical
`git pull` failed mid-script. Without `set -euo pipefail`, bash continues
running after errors. With strict mode: any unhandled error exits immediately,
piped command failures are caught, and unset variable references error out
instead of silently expanding to empty string.

**Problem 2**: A script needs to process a list of servers, tracking which
succeeded and which failed. Simple positional parameters can't hold dynamic
lists. Bash associative arrays: `declare -A results; results[server1]=success;
results[server2]=failed` - then iterate and report. Without arrays: requires
awkward temp files or fragile string splitting.

---

### Textbook Definition

**Bash arrays**: Indexed arrays (`arr[0]`, `arr[1]`, ...) and associative
arrays (`arr[key]=value`). Unlike most languages, bash array indices don't
need to be consecutive. Arrays can contain strings with spaces.

**Parameter expansion**: Bash's built-in string manipulation: prefix/suffix
stripping, substitution, case conversion, default values, substring
extraction. Avoids calling external tools (awk, sed) for simple operations.

**Process substitution** `<(cmd)`: Makes the output of a command appear as
a file (via named pipe). Allows commands that expect file arguments to work
with command output. `diff <(sort file1) <(sort file2)`.

**Here-string** `<<<`: Feeds a string as stdin to a command. `read var <<<
"hello"` sets `var=hello`. Simpler than echo piping.

**Strict mode** (`set -euo pipefail`): `-e` = exit on error. `-u` = error
on unset variables. `-o pipefail` = pipe fails if any component fails.

---

### Understand It in 30 Seconds

```bash
# === Arrays ===
# Indexed array:
arr=("one" "two" "three")
echo "${arr[0]}"        # one (0-indexed)
echo "${arr[@]}"        # all elements: one two three
echo "${#arr[@]}"       # 3 (count)
echo "${arr[@]:1:2}"    # slice: two three (start=1, len=2)
arr+=("four")           # append

# Loop (correct way):
for item in "${arr[@]}"; do
    echo "$item"   # handles elements with spaces correctly
done

# Indices:
for i in "${!arr[@]}"; do
    echo "$i: ${arr[$i]}"
done

# Associative array (must declare -A first):
declare -A servers
servers[web1]="10.0.1.1"
servers[web2]="10.0.1.2"
servers[db1]="10.0.2.1"

echo "${servers[web1]}"        # 10.0.1.1
echo "${!servers[@]}"          # keys: web1 web2 db1
echo "${servers[@]}"           # values

for host in "${!servers[@]}"; do
    echo "$host -> ${servers[$host]}"
done

# === Functions ===
greet() {
    local name=$1         # local: visible only in function
    local upper="${name^^}"   # bash string expansion (uppercase)
    echo "Hello, $upper!"
    return 0              # explicit return code (0=success)
}
greet "world"   # Hello, WORLD!
echo $?         # 0 (last return code)

# Return value via echo (capture with $(...)):
get_date() {
    echo "$(date +%Y-%m-%d)"
}
today=$(get_date)   # captures function's stdout

# === Parameter expansion ===
var="Hello World"

# Default values:
echo "${var:-default}"     # if var unset/empty: use "default"
echo "${var:=assign}"      # if var unset/empty: assign and use "assign"
echo "${var:+alt}"         # if var SET and non-empty: use "alt"
echo "${var:?error msg}"   # if var unset/empty: print error and exit

# String manipulation:
path="/usr/local/bin/myapp"
echo "${path#*/}"          # strip shortest prefix: usr/local/bin/myapp
echo "${path##*/}"         # strip longest prefix: myapp (basename)
echo "${path%/*}"          # strip shortest suffix: /usr/local/bin (dirname)
echo "${path%%/*}"         # strip longest suffix: (empty - starts with /)

file="archive.tar.gz"
echo "${file%.*}"          # archive.tar (remove last extension)
echo "${file%%.*}"         # archive (remove all extensions)

# Substitution:
echo "${var/World/Bash}"   # Hello Bash (first match)
echo "${var//l/L}"         # HeLLo WorLd (all matches)

# Case conversion (bash 4+):
str="Hello World"
echo "${str^^}"            # HELLO WORLD (uppercase all)
echo "${str,,}"            # hello world (lowercase all)
echo "${str^}"             # Hello World (capitalize first char)

# Length:
echo "${#var}"             # 11 (string length)
echo "${#arr[@]}"          # array length

# Substring:
echo "${var:6:5}"          # World (offset=6, length=5)

# === Arithmetic ===
x=5
y=3
echo $(( x + y ))          # 8
echo $(( x ** y ))         # 125 (power: x^y)
echo $(( x % y ))          # 2 (modulo)

# Increment/decrement:
(( x++ ))                  # x is now 6 (in-place arithmetic)
(( count = 10 ))           # assignment in arithmetic context

# Arithmetic in conditions:
if (( x > y )); then
    echo "x is greater"
fi

# === Process substitution ===
# diff two sorted files without creating temp files:
diff <(sort file1.txt) <(sort file2.txt)

# Compare current vs previous git state:
diff <(git show HEAD:config.yaml) config.yaml

# Read multiple command outputs in a while loop:
while IFS= read -r line; do
    echo "processing: $line"
done < <(find /var/log -name "*.log" -newer /tmp/marker)
# < <(...) = redirect from process substitution

# === Here-strings ===
# Feed string to command expecting stdin:
read -r first last <<< "John Doe"
echo "$first $last"   # John Doe

# Parse output without a pipe (avoids subshell variable scope issues):
while IFS=: read -r user pass uid gid rest; do
    echo "User: $user, UID: $uid"
done <<< "$(getent passwd)"

# === Strict mode ===
set -euo pipefail    # near top of every script

# -e: exit if any command returns non-zero
# -u: error if unset variable used (${UNDEFINED} = error, not empty string)
# -o pipefail: whole pipe fails if any command fails
#   Without: "false | true" = success (true determines result)
#   With:    "false | true" = failure (false part is caught)

# Exception: allow a command to fail without exiting:
result=$(some-command || true)  # "|| true" prevents -e from triggering

# === trap: cleanup on exit/signals ===
TMPFILE=$(mktemp)

cleanup() {
    rm -f "$TMPFILE"
    echo "Cleaned up."
}
trap cleanup EXIT     # run cleanup when script exits (any reason)
trap cleanup INT TERM # also on Ctrl+C and kill

echo "Working with $TMPFILE"
some-operation > "$TMPFILE"
# Even if script fails here, trap EXIT ensures cleanup runs
```

---

### First Principles

**Why arrays over space-separated strings:**
```bash
# BAD: space-separated strings break with spaces in values:
servers="web-1 web-2 app server web-3"  # all on one line
for s in $servers; do   # BROKEN: splits on ALL whitespace
    echo "$s"
done
# What if a server name has a space? (pathological, but shows the issue)

# Also broken: command output with spaces:
files="file with spaces.txt another.txt"
for f in $files; do   # BROKEN: iterates: "file", "with", "spaces.txt", ...
    process "$f"
done

# GOOD: arrays handle arbitrary strings correctly:
files=()
while IFS= read -r line; do
    files+=("$line")          # adds entire line as one element
done < <(find . -name "*.txt")

for f in "${files[@]}"; do    # correct: each file as one element
    process "$f"
done

# GOOD: associative array for structured data:
declare -A config
config[host]="db.example.com"
config[port]="5432"
config[db]="myapp"

connect "${config[host]}" "${config[port]}" "${config[db]}"
```

**Parameter expansion vs external tools:**
```bash
# Benchmarked difference: parameter expansion vs external tools

# BAD (slow): calling external process for each operation:
filename=$(basename "$path")        # fork + exec basename
dirname=$(dirname "$path")          # fork + exec dirname
upper=$(echo "$str" | tr 'a-z' 'A-Z')   # fork + exec echo + tr

# GOOD (fast): built-in parameter expansion:
filename="${path##*/}"              # no fork, pure bash
dir="${path%/*}"                    # no fork, pure bash
upper="${str^^}"                    # no fork, pure bash (bash 4+)

# Significant in loops:
# BAD: 1000 iterations * 2 forks = 2000 process spawns
for item in "${arr[@]}"; do
    base=$(basename "$item")
    process "$base"
done

# GOOD: 1000 iterations, 0 extra forks
for item in "${arr[@]}"; do
    process "${item##*/}"
done
```

---

### Thought Experiment

Deployment script with strict mode and cleanup:

```bash
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'   # safer IFS (newlines and tabs only, not spaces)

# ======= Configuration =======
readonly DEPLOY_DIR="/opt/myapp"
readonly BACKUP_DIR="/opt/backups"
readonly SERVICE_NAME="myapp"
readonly TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# ======= State tracking =======
declare -A step_status     # associative array: step -> pass/fail
BACKUP_PATH=""             # will be set by backup function

# ======= Cleanup trap =======
cleanup() {
    local exit_code=$?
    echo ""
    echo "--- Deployment Summary ---"
    for step in "${!step_status[@]}"; do
        echo "  $step: ${step_status[$step]}"
    done
    
    if [[ $exit_code -ne 0 && -n "$BACKUP_PATH" ]]; then
        echo ""
        echo "ROLLBACK: restoring from $BACKUP_PATH"
        tar xzf "$BACKUP_PATH" -C "$(dirname "$DEPLOY_DIR")" 2>/dev/null || true
        systemctl restart "$SERVICE_NAME" 2>/dev/null || true
    fi
    exit $exit_code
}
trap cleanup EXIT

# ======= Steps =======
do_backup() {
    echo "[1/4] Creating backup..."
    mkdir -p "$BACKUP_DIR"
    BACKUP_PATH="$BACKUP_DIR/myapp-$TIMESTAMP.tar.gz"
    tar czf "$BACKUP_PATH" "$DEPLOY_DIR"
    step_status[backup]="OK ($BACKUP_PATH)"
}

do_deploy() {
    echo "[2/4] Deploying..."
    local artifact=${1:?artifact path required}   # :? = exit if empty
    tar xzf "$artifact" -C "$DEPLOY_DIR"
    step_status[deploy]="OK"
}

do_test() {
    echo "[3/4] Smoke test..."
    local result
    result=$(curl -sf "http://localhost:8080/health" 2>&1 || true)
    if [[ "$result" != *'"status":"up"'* ]]; then
        step_status[test]="FAILED: $result"
        return 1
    fi
    step_status[test]="OK"
}

do_reload() {
    echo "[4/4] Reloading service..."
    systemctl reload "$SERVICE_NAME"
    step_status[reload]="OK"
}

# ======= Main =======
do_backup
do_deploy "${1}"     # first arg = artifact path
do_test
do_reload

echo ""
echo "Deployment complete."
```

---

### Mental Model / Analogy

```
Bash parameter expansion = Swiss Army knife for strings
  Carry it with you everywhere - no need to call a locksmith (awk/sed)
  for small string jobs

  ${var#prefix}  = Knife: cut a little from the front
  ${var##prefix} = Saw: cut all the way from the front
  ${var%suffix}  = Scissors: trim a little from the back
  ${var%%suffix} = Shears: trim all the way from the back
  ${var/old/new} = Marker: replace one instance
  ${var//old/new}= Paint roller: replace all instances
  ${var^^}       = CAPS LOCK for variables

Arrays = labeled filing cabinets
  Indexed array = numbered folders: folder[0], folder[1], ...
  Associative array = tabbed folders: folder[web1], folder[db]
  "${arr[@]}" = "give me ALL folders in one go"
  "${!arr[@]}" = "give me all the LABELS on the folders"

Process substitution <(...) = temporary file that writes itself:
  Usually: cmd > tmpfile; other_cmd tmpfile; rm tmpfile
  With <(cmd): "pretend this is a file, but it's actually cmd's output"
  diff <(sort a) <(sort b) = "sort a into a temp file, sort b into another,
  diff them, then throw both temp files away automatically"

set -euo pipefail = circuit breaker
  -e: electricity stops if any wire breaks (error)
  -u: short circuit if you touch an unmarked wire (unset variable)
  -o pipefail: the whole pipe is broken if any section fails
  Without it: errors silently pass through like a loose connection
```

---

### Gradual Depth - Five Levels

**Level 1:**
Arrays (`arr=(a b c)`, `${arr[@]}`), basic functions, `local` variables,
parameter expansion (`${var:-default}`, `${var##*/}` for basename).
`set -e` for error detection. `trap EXIT` for cleanup. Here-strings `<<<`.

**Level 2:**
Associative arrays (`declare -A`). Process substitution `<(cmd)`.
Advanced parameter expansion: `${var:offset:len}`, `${var//find/replace}`.
`set -euo pipefail` with exception patterns (`|| true`, `set +e`). IFS
manipulation for splitting. `printf` for safe output formatting.

**Level 3:**
Nameref variables (`declare -n ref=$1; ref=value`). Array slicing
`${arr[@]:start:len}`. Indirect variable references `${!varname}`.
`mapfile`/`readarray` for reading into arrays. `compgen -v` for variable
names. Co-processes `coproc`. `bash -x` debugging and `PS4` customization.
`BASH_LINENO`, `BASH_SOURCE`, `FUNCNAME` for stack traces.

**Level 4:**
`extglob`: extended globbing patterns (`!(*.log)`, `*(pattern)`).
`globstar` (`**` recursive glob). `shopt -s dotglob` for hidden files.
Custom `PROMPT_COMMAND` and `PS1` with dynamic content. `readline` key
bindings and `bind` command. Bash job control (`bg`, `fg`, `jobs`,
`disown`). `complete`/`compgen` for custom tab completion. `$BASH_REMATCH`
with `[[ =~ ]]` regex matching.

**Level 5:**
Bash performance: array operations vs grep/awk trade-offs for large
datasets. `time` and profiling with `PS4='$(date +%N) '`. When to switch
from bash to Python/Go (complexity threshold: >300 lines, needs data
structures, error handling complexity). `bash --norc --noprofile` for
clean environments. `declare -r` (readonly), `declare -x` (export),
`declare -i` (integer). `eval` and `declare -n` for metaprogramming
(risks: code injection - never eval user input).

---

### Code Example

**BAD - common bash mistakes:**
```bash
# BAD 1: No strict mode, errors silently pass through:
#!/bin/bash
# (no set -euo pipefail)
cp important-file.txt /nonexistent/dir/
echo "Files copied successfully"    # PRINTS THIS! (cp failed silently)

# BAD 2: Unquoted array elements (word splitting breaks with spaces):
files=(file1.txt "file with spaces.txt" file3.txt)
for f in ${files[@]}; do    # WRONG: unquoted, space splits elements
    process $f              # WRONG: unquoted, breaks on spaces
done
# "file with spaces.txt" becomes 3 separate arguments!

# GOOD:
for f in "${files[@]}"; do  # quoted ${arr[@]} preserves element boundaries
    process "$f"             # quoted variable preserves spaces
done

# BAD 3: Ignoring function return values:
get_db_connection() {
    mysql -h db.host -u user -p"$PASS" mydb 2>/dev/null
    # If this fails, caller can't know
}
get_db_connection
do_query   # runs even if connection failed!

# GOOD:
get_db_connection() {
    if ! mysql -h db.host -u user -p"$PASS" mydb 2>/dev/null; then
        echo "ERROR: Cannot connect to database" >&2
        return 1
    fi
    return 0
}
if ! get_db_connection; then
    exit 1
fi
```

**GOOD - production deployment pattern:**
```bash
#!/bin/bash
set -euo pipefail

# Safe temporary file handling:
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Read config into associative array:
declare -A config
while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" == \#* ]] && continue  # skip blank/comments
    config[$key]="${value}"
done < /etc/myapp/deploy.conf

# Validate required config:
required_keys=(host port user deploy_path)
missing=()
for key in "${required_keys[@]}"; do
    [[ -n "${config[$key]:-}" ]] || missing+=("$key")
done
if [[ ${#missing[@]} -gt 0 ]]; then
    echo "ERROR: Missing config keys: ${missing[*]}" >&2
    exit 1
fi

# Use config:
echo "Deploying to ${config[host]}:${config[port]}"
rsync -avz --delete \
    ./dist/ "${config[user]}@${config[host]}:${config[deploy_path]}"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`$array` and `${array[@]}` are the same" | `$array` expands to ONLY `${array[0]}` (the first element). `${array[@]}` expands to ALL elements as separate words (with proper quoting). `${array[*]}` expands all elements into ONE word (space-separated). Always use `"${array[@]}"` when iterating to preserve elements with spaces. `$array` for arrays is a common bug that silently drops all but the first element. |
| "`set -e` catches all errors" | `set -e` only exits on errors in certain positions: NOT in conditions (`if cmd; then`), NOT on the left side of `&&`/`||`, NOT in a list with `||` after it. Example: `set -e; false || echo "handled"` - does NOT exit because false is followed by `||`. Also: function failures are caught, but only if the function is not the condition of an `if`. The combination `-euo pipefail` catches more cases but still has gotchas. Reading `help set` and the bash manual's error handling section reveals the precise rules. |
| "Local variables in functions are truly isolated" | `local` makes a variable local to the function and its child functions. BUT: if a function sets a local variable `x=5`, and calls another function that uses `x` (without declaring its own local `x`), the child function SEES the parent's local `x`. This is dynamic scoping, not lexical. Practical bug: `local IFS=$'\n'` in a function affects all functions called from within it. Always `local` all variables you don't want to leak, in every function. Also: `local` does NOT prevent modifications to global variables if you use `declare -g` or just assign to a global without `local`. |
| "Process substitution `<(cmd)` is the same as pipes" | They differ in: (1) Scope - commands in `<(cmd)` run in a subshell, so variable assignments inside don't persist to the parent. (2) Implementation - process substitution creates a named pipe (FIFO) or `/dev/fd/N` file descriptor. (3) Usage - you can use MULTIPLE `<(cmd)` in one command (`diff <(a) <(b)`) vs a pipeline which only has one stdin. (4) Direction - `<(cmd)` = read from command; `>(cmd)` = write to command (rarer). The key advantage of `< <(cmd)` over `cmd | while read` is that the `while` loop runs in the current shell (not a subshell), so variable modifications in the loop body persist to the parent script. |
| "`trap EXIT` only runs on successful exit" | `trap EXIT` runs when the script exits for ANY reason: normal completion, `set -e` error exit, explicit `exit 1`, `kill -TERM` (if trapped separately), or uncaught error. It does NOT automatically run on: `kill -9` (SIGKILL - cannot be trapped, process is immediately terminated by kernel) or system crash. Best practice: `trap 'cleanup; exit' INT TERM EXIT` - cleanup runs whether you `exit 0`, crash due to error (`set -e`), or receive Ctrl+C (INT). For `kill -9` resilience: write state to disk early, use lock files and clean up on the next startup. |

---

### Failure Modes & Diagnosis

**Debugging bash scripts:**
```bash
# Mode 1: trace execution (print every command before running):
bash -x myscript.sh        # adds + before each command
# Or inline:
set -x    # enable from this point
...       # commands with trace
set +x    # disable trace

# Customize trace prefix for timestamps:
PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
set -x

# Mode 2: Find where a variable is set wrong:
# Trace with conditional breakpoints:
trap 'echo "At line $LINENO: var=$var"' DEBUG
# Runs before every command - shows variable state evolution

# Mode 3: Stack trace on error:
err_handler() {
    echo "ERROR at line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
    local i=0
    echo "Call stack:"
    while caller $i; do
        (( i++ ))
    done
}
trap err_handler ERR    # run on any unhandled error (with set -e)

# Common bug: unquoted variables with spaces:
# Symptom: "No such file or directory" for a file that exists
filename="my file.txt"
cat $filename    # BROKEN: becomes: cat my file.txt (two args)
cat "$filename"  # CORRECT: "my file.txt" as one argument

# Debug: add -x to see what bash actually passes:
bash -x script.sh
# + cat my file.txt    <- see the broken expansion
# + cat 'my file.txt'  <- see the correct expansion
```

---

### Related Keywords

**Foundational:**
LNX-004 (Shell basics), LNX-014 (Text processing)

**Builds on this:**
LNX-070 (Shell Customization)

**Related:**
LNX-065 (POSIX compatibility - what's bash-specific vs POSIX sh)

---

### Quick Reference Card

| Construct | Purpose |
|-----------|---------|
| `arr=(a b c)` | Create indexed array |
| `"${arr[@]}"` | Expand all array elements (quoted) |
| `"${!arr[@]}"` | All array indices/keys |
| `declare -A map` | Create associative array |
| `${var:-default}` | Use default if unset/empty |
| `${var##*/}` | Strip longest prefix (basename) |
| `${var%/*}` | Strip shortest suffix (dirname) |
| `set -euo pipefail` | Strict mode (top of every script) |

**3 things to remember:**
1. Always quote array expansion: `"${arr[@]}"` not `${arr[@]}` - unquoted breaks with spaces
2. `set -euo pipefail` at the top of every non-trivial script - catches silent failures
3. `${var##*/}` = basename, `${var%/*}` = dirname - no fork needed for simple path manipulation

---

### Transferable Wisdom

Bash arrays and parameter expansion concepts appear in: Ansible templates
(Jinja2 `{{ item.name }}`), Helm templates (Go templates `{{ .Values.name }}`),
and Terraform variables - all are variations of "text with substitution."
The trap/cleanup pattern maps to: Python `try/finally`, Java `try-with-resources`,
Go `defer` statements. `set -euo pipefail` is the shell equivalent of
"strict mode" in JavaScript (`"use strict"`) or enabling compiler warnings
in C (`-Wall -Wextra`). Process substitution `<(cmd)` solves the same
problem as Python's `tempfile.NamedTemporaryFile` or Java's `PipedInputStream`:
making command output appear as a file without actually writing to disk.
Understanding bash arrays and parameter expansion makes you better at ALL
shell scripting - understanding the base language makes it easier to recognize
what DevOps tools (Ansible, Helm, GitHub Actions) do at the template layer.

---

### The Surprising Truth

Bash arrays were not added until bash 2.0 (1996), and associative arrays
not until bash 4.0 (2009). For 25+ years, shell scripts dealt with lists
using space-separated strings and positional parameters - the `"${arr[@]}"`
pattern was considered an advanced feature. The consequence: millions of
production scripts were written using the "naive" space-separated approach
(e.g., `servers="web1 web2 db1"` then `for s in $servers`) and they work
UNTIL a hostname with a space or special character appears. This is why
"it always worked before" bugs appear when paths or names with spaces hit
legacy scripts. The deeper lesson: bash's design has accumulated features
over decades, which means many "correct" approaches changed. Code written
to the bash 1.x idioms (early 1990s) still runs today but misses 30 years
of safer patterns. A bash script from 2000 and one from 2024 look completely
different for the same task. `shellcheck` (released 2012) was transformative:
it's the linter that explicitly tells you "this was the old way, this is
the safe way."

---

### Mastery Checklist

- [ ] Can use indexed and associative arrays correctly with proper quoting
- [ ] Can write functions with local variables and return codes
- [ ] Knows the key parameter expansion patterns (default, basename, suffix strip)
- [ ] Uses `set -euo pipefail` at the top of production scripts
- [ ] Can use `trap EXIT` for cleanup and process substitution `<(cmd)`

---

### Think About This

1. Write a bash function `validate_config` that takes a config file path,
   reads key=value pairs into an associative array, validates that a set of
   required keys are present, and returns 0 on success or 1 with an error
   message listing missing keys. The function should handle blank lines,
   comment lines starting with `#`, and values containing `=` characters.

2. A pipeline `cat file | grep pattern | sort | head -1` prints the right
   answer but exits with code 0 even when `grep` matches nothing (empty result)
   and subsequent steps "succeed" on empty input. With `set -o pipefail`, when
   exactly does this pipeline fail? Is that the behavior you want? Describe
   the approach to "fail if no matches found" while still using a pipeline.

3. A colleague writes `for f in $(find /data -name "*.csv"); do process "$f";
   done`. This script worked for 2 years then failed when a file was created
   with a space in the name. Rewrite this using a bash array or `while read`
   approach that correctly handles filenames with spaces, newlines, and other
   special characters.

---

### Interview Deep-Dive

**Foundational:**
Q: What does `set -euo pipefail` do, and why should you use it?
A: It sets three bash options that make scripts more robust against silent failures: `-e` (errexit): Exit immediately if any command returns a non-zero exit code. Without it: `cp file.txt /nonexistent/dir; echo "Done"` prints "Done" even though cp failed. With it: script exits at the cp failure. Exception: commands in `if` conditions, after `||`, or in `&&` lists are exempt (they're expected to potentially fail). `-u` (nounset): Treat references to unset variables as errors. Without it: `echo "Path: $DEPLOY_PATH"` silently expands to `echo "Path: "` if DEPLOY_PATH is not set. With it: script exits with "DEPLOY_PATH: unbound variable". Prevents bugs where a typo in a variable name silently becomes empty string (e.g., `rm -rf "$TMP_DIR/"` where `TMP_DIR` is unset becomes `rm -rf "/"`). `-o pipefail`: A pipeline returns the exit status of the LAST command by default. Without pipefail: `false | true` exits 0 (true determines result). With pipefail: any non-zero exit in the pipeline causes the whole pipeline to fail. Critical for: `cmd | grep pattern | process` - grep returns 1 if no matches, which should indicate "no data found." Usage: `set -euo pipefail` on line 2 of every production script (line 1 is `#!/bin/bash`). Common exception patterns: `${var:-}` for variables that might be unset but that's OK. `command || true` when you want to continue after a failure. `set +e; risky-command; set -e` for temporary error tolerance sections.

**Expert:**
Q: What is the difference between `${arr[@]}` and `${arr[*]}`, and when does it matter?
A: Both expand all elements of an array, but they differ in how they handle quoting and word splitting: `${arr[@]}` (unquoted): identical to `${arr[*]}` - both expand to all elements separated by the first character of IFS (usually space). Both susceptible to word splitting on elements with spaces. `"${arr[@]}"` (double-quoted): each element becomes its own separate word. Spaces WITHIN elements are preserved as part of that element. This is the safe form. `"${arr[*]}"` (double-quoted): ALL elements are joined into a SINGLE word with IFS separator. Useful when you want a comma-separated list: `IFS=, ; echo "${arr[*]}"`. Practical examples: `arr=("file one.txt" "file two.txt")` - `for f in "${arr[@]}"`: iterates as 2 items: "file one.txt" and "file two.txt". - `for f in "${arr[*]}"`: iterates as 1 item: "file one.txt file two.txt" (all joined). - `for f in ${arr[@]}`: iterates as 4 items: "file", "one.txt", "file", "two.txt" (word splitting!). The mental model: `"${arr[@]}"` = bash expands the array, putting each element in quotes automatically. Always use `"${arr[@]}"` for iteration and for passing arrays to functions. Use `"${arr[*]}"` only when you explicitly want a joined string.
