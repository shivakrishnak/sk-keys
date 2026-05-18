---
id: LNX-042
title: "Bash Scripting Conditionals and Loops"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-006, LNX-017
used_by: LNX-066
related: LNX-066, LNX-017, LNX-006
tags: [bash, shell-script, if-else, for-loop, while-loop, case, test, exit-code]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/lnx/bash-conditionals-loops/
---

## TL;DR

Bash conditionals use `if [ condition ]` (POSIX test) or `if [[ condition ]]`
(bash extended test, preferred). Common conditions: `-f file` (file exists),
`-d dir` (directory), `-z "$var"` (empty string), `$?` (last exit code).
Loops: `for item in list; do ... done`, `while read line; do ... done`
(process file lines), `for (( i=0; i<10; i++ )); do ... done` (C-style).
Key rule: `set -euo pipefail` at script start (exit on error, unbound
variables, and pipe failures). Always quote variables: `"$var"` not `$var`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-042 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | bash, if-else, for-loop, while-loop, case, test, [[ ]], exit code, set -e |
| **Prerequisites** | LNX-006, LNX-017 |

---

### The Problem This Solves

Shell scripts without error handling silently continue past failures, leaving
systems in inconsistent states. `command1; command2; command3` - if command1
fails, commands 2 and 3 still run (potentially with wrong assumptions). With
`set -euo pipefail`: the script stops at the first failure. Bash conditionals
let you check preconditions, handle errors, and write scripts that behave
predictably.

---

### Textbook Definition

**Exit code**: Every command returns a number (0-255). 0 = success.
Non-zero = failure. `$?` holds the last command's exit code. `if cmd;`
checks if cmd's exit code is 0 (truthy).

**Test command** (`[` or `test`): evaluates conditions and returns exit
code 0 (true) or 1 (false). `[[ ]]` is bash's extended test with more
features (pattern matching, no word splitting).

**Shell arithmetic**: `(( expression ))` evaluates arithmetic, returns
0 if non-zero result (truthy), 1 if zero. Different from test expression.

**IFS (Internal Field Separator)**: Shell variable that controls word
splitting. Default: space, tab, newline. Setting `IFS=` before `read`
prevents trimming.

---

### Understand It in 30 Seconds

```bash
# === Conditionals ===

# if/elif/else:
if [[ -f "/etc/app.conf" ]]; then
    echo "Config exists"
elif [[ -d "/etc/app/" ]]; then
    echo "Config dir exists"
else
    echo "No config found"
fi

# Common test conditions:
[[ -f file ]]     # file exists (regular file)
[[ -d dir ]]      # directory exists
[[ -e path ]]     # path exists (file or dir)
[[ -z "$var" ]]   # string is empty
[[ -n "$var" ]]   # string is non-empty
[[ "$a" == "$b" ]] # string equality
[[ "$a" != "$b" ]] # string inequality
[[ $n -gt 5 ]]    # numeric: greater than
[[ $n -lt 5 ]]    # numeric: less than
[[ $n -eq 5 ]]    # numeric: equal
! [[ condition ]] # negation

# Short circuit (common idiom):
[[ -f /etc/app.conf ]] || { echo "Missing config"; exit 1; }
command && echo "succeeded" || echo "failed"

# === Loops ===

# for loop over list:
for server in web1 web2 web3; do
    ssh "ubuntu@$server" "uptime"
done

# for loop over array:
servers=("web1" "web2" "web3")
for server in "${servers[@]}"; do
    echo "Checking $server"
done

# C-style for loop:
for (( i=0; i<10; i++ )); do
    echo "Iteration $i"
done

# for loop over files:
for file in /var/log/*.log; do
    echo "Processing: $file"
done

# while read - process file line by line (CORRECT):
while IFS= read -r line; do
    echo "Line: $line"
done < /etc/hosts

# while loop with condition:
COUNT=0
while [[ $COUNT -lt 5 ]]; do
    echo "Count: $COUNT"
    (( COUNT++ ))
done

# until loop (runs WHILE condition is FALSE):
until curl -sf http://localhost:8080/health; do
    echo "Waiting for service..."
    sleep 2
done
echo "Service is up!"

# break and continue:
for i in {1..10}; do
    [[ $i -eq 5 ]] && break    # stop loop at 5
    [[ $i -eq 3 ]] && continue # skip 3
    echo $i
done

# case statement:
case "$1" in
    start)   systemctl start myapp ;;
    stop)    systemctl stop myapp ;;
    restart) systemctl restart myapp ;;
    status)  systemctl status myapp ;;
    *)       echo "Usage: $0 {start|stop|restart|status}"; exit 1 ;;
esac
```

---

### First Principles

**Exit code as boolean:**
```bash
# In bash: 0 = TRUE (success), non-zero = FALSE (failure)
# This is OPPOSITE of most programming languages!

if command; then     # runs if command exits with 0
    # success
fi

# [[ ]] is just a command that returns 0 or 1:
[[ -f /etc/hosts ]]
echo $?              # 0 if file exists, 1 if not

# &&: run second if first succeeded (exit 0)
# ||: run second if first FAILED (non-zero exit)
mkdir /tmp/dir && echo "Created"   # echo only if mkdir succeeded
mkdir /tmp/dir || echo "Failed"    # echo only if mkdir failed
```

**set -euo pipefail explained:**
```bash
#!/bin/bash
set -e        # exit immediately if any command fails (non-zero exit)
set -u        # error on unbound (undefined) variables
set -o pipefail  # pipe returns failure if any command in pipe fails

# Without set -e:
rm important_file
do_other_things   # runs even though rm might have failed silently

# Without set -u:
echo $UNDEFINED_VAR   # empty string, no error (silent bug)

# Without set -o pipefail:
cat file | grep pattern | process
# if grep finds nothing (exit 1), bash sees the LAST command's exit code
# (process might exit 0 even though grep failed)
```

---

### Thought Experiment

A script to wait for a service to be ready, with timeout:

```bash
#!/bin/bash
set -euo pipefail

wait_for_service() {
    local url="$1"
    local max_wait="${2:-60}"    # default 60 seconds
    local elapsed=0
    
    echo "Waiting for: $url (max ${max_wait}s)"
    
    while ! curl -sf "$url" > /dev/null 2>&1; do
        if [[ $elapsed -ge $max_wait ]]; then
            echo "ERROR: Service not ready after ${max_wait}s" >&2
            return 1   # failure
        fi
        sleep 2
        (( elapsed += 2 ))
        echo "  Still waiting... (${elapsed}s)"
    done
    
    echo "Service ready after ${elapsed}s"
    return 0   # success
}

# Usage:
if wait_for_service "http://localhost:8080/health" 30; then
    echo "Starting tests..."
else
    echo "Service failed to start - aborting" >&2
    exit 1
fi
```

---

### Mental Model / Analogy

```
Bash conditional = security guard at a door
  if [[ condition ]]; then  <- if guard says "OK"
      do_this                  <- let them through
  else                      <- if guard says "NO"
      do_that                  <- send them away
  fi

Exit codes = traffic light
  0 (green) = success, continue
  non-zero (red) = failure, stop/handle

set -euo pipefail = automatic emergency brake on a car
  -e: if anything breaks (non-zero exit), STOP immediately
  -u: if you reference something that doesn't exist, STOP
  -o pipefail: if any part of a pipe breaks, count it as BROKEN

for loop = assembly line:
  for server in web1 web2 web3
  = "for each item on the conveyor belt, do the same operation"

while loop = quality control:
  while [[ error_count -gt 0 ]]
  = "keep retrying until the quality check passes"
  
IFS= read -r line = reading a book word by word
  IFS= says "don't split on spaces"
  read -r says "don't interpret backslashes"
  = "read exactly one line as-is, no interpretation"
```

---

### Gradual Depth - Five Levels

**Level 1:**
`if [ condition ]; then` and `fi`. `for item in list; do done`. `while
condition; do done`. `$?` for exit code. Always start scripts with
`#!/bin/bash` and `set -euo pipefail`. Quote your variables.

**Level 2:**
`[[ ]]` vs `[ ]`: use `[[ ]]` in bash (no word splitting, pattern matching
with `==`, `=~` for regex). `case` statement for multi-way branching.
`read` for reading input. `continue` and `break` in loops. `||` and `&&`
for inline conditionals. `$?`, `$#`, `$0`, `$1`, `"$@"`, `"$*"` special vars.

**Level 3:**
`declare -A` associative arrays (bash 4+). `mapfile -t array < file` to
read file into array. `printf` for formatted output (prefer over `echo`).
`local` variables in functions. `trap` for cleanup on exit:
`trap 'rm -f /tmp/myfile' EXIT`. Process substitution: `while read line;
do done < <(command)` to loop over command output.

**Level 4:**
`select` for interactive menus. Subshells: `( commands )` for isolated
environment. `exec` to replace current process. `eval` (use rarely, security
risk with untrusted input). `getopts` for option parsing. `bash -n script.sh`
for syntax check. `bash -x script.sh` for trace debugging (prints each
command before executing).

**Level 5:**
Bash job arrays for parallel processing: `pids=(); for server in ...; do
cmd & pids+=($!); done; wait "${pids[@]}"`. `coproc` for bidirectional
pipe with a subprocess. `BASH_COMMAND` and `DEBUG` trap for per-command
hooks. Custom `ERR` trap for error handling with stack traces. `FUNCNAME`
array for call stack inspection. Script performance: avoid subshells in
loops (fork overhead), use `read` + string operations over `awk/sed` in
inner loops.

---

### Code Example

**BAD - common bash scripting mistakes:**
```bash
# BAD 1: Unquoted variables (word splitting and globbing!)
files="file1 file2 file3"
rm $files          # looks fine, BUT:
filename="file with spaces"
rm $filename       # tries to rm "file", "with", "spaces" (3 files!)
# GOOD:
rm "$files"        # still wrong for list (single argument)
# For lists, use arrays:
files=("file1" "file with spaces" "file3")
rm "${files[@]}"   # correct: each array element as separate argument

# BAD 2: Processing file line by line with for loop
for line in $(cat /etc/hosts); do
    echo "$line"
done
# Problem: word-splits on spaces, processes WORDS not LINES
# 127.0.0.1   localhost  -> processed as "127.0.0.1", "localhost" separately!

# GOOD: use while read:
while IFS= read -r line; do
    echo "$line"
done < /etc/hosts

# BAD 3: Not using set -euo pipefail:
#!/bin/bash
mkdir /some/path    # fails silently if path doesn't exist
cd /some/path       # now in wrong directory!
rm -rf *            # DELETES CURRENT DIRECTORY CONTENTS!

# GOOD: fail early with set -e:
#!/bin/bash
set -euo pipefail
mkdir /some/path    # script STOPS here if mkdir fails
cd /some/path       # only runs if mkdir succeeded
rm -rf *            # safe: guaranteed to be in /some/path

# BAD 4: Checking exit code after command loses it:
command
if [[ $? -ne 0 ]]; then   # works
    echo "failed"
fi

ls /nonexistent
echo "this echo changed \$? to 0"
if [[ $? -ne 0 ]]; then  # NEVER true! echo succeeded!
    echo "ls failed"     # never printed
fi

# GOOD: check directly:
if ! ls /nonexistent 2>/dev/null; then
    echo "ls failed"
fi
```

**GOOD - robust production script pattern:**
```bash
#!/bin/bash
set -euo pipefail

# Constants:
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/deploy.log"
readonly REQUIRED_VARS=("DEPLOY_ENV" "APP_VERSION" "AWS_REGION")

# Logging:
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
error() { log "ERROR: $*" >&2; }

# Validation:
validate_environment() {
    for var in "${REQUIRED_VARS[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required variable $var is not set"
            exit 1
        fi
    done
    log "Environment validated: ENV=$DEPLOY_ENV, VERSION=$APP_VERSION"
}

# Cleanup on exit (runs even if script fails):
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        error "Deployment failed with exit code $exit_code"
        # Rollback logic here
    fi
}
trap cleanup EXIT

# Main:
main() {
    log "Starting deployment: $APP_VERSION to $DEPLOY_ENV"
    validate_environment
    
    # Loop with error handling:
    local failed=0
    for server in $(get_servers "$DEPLOY_ENV"); do
        if ! deploy_to_server "$server" "$APP_VERSION"; then
            error "Deployment to $server failed"
            (( failed++ ))
        fi
    done
    
    if [[ $failed -gt 0 ]]; then
        error "$failed server(s) failed deployment"
        exit 1
    fi
    
    log "Deployment complete: all servers updated"
}

main "$@"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`[ ]` and `[[ ]]` are the same" | `[ ]` is the POSIX `test` command - it's an external command with word splitting and globbing. `[[ ]]` is a bash keyword with additional features: `==` does glob matching, `=~` does regex, no word splitting or filename expansion inside. Always use `[[ ]]` in bash scripts. Use `[ ]` only for POSIX sh compatibility. |
| "set -e makes all scripts safe" | `set -e` has surprising behavior: it doesn't trigger in some contexts (functions used in conditions like `if function; then`, subshell exit codes in some cases, arithmetic with `(( ))`). Also: `set -e` exits on the FIRST error, which might leave cleanup undone. Use `trap 'cleanup' EXIT` alongside `set -e`. |
| "Variables are global in bash functions" | Yes, by default all variables are global in bash functions. To make a variable local: `local myvar="value"`. Without `local`: changing a variable inside a function changes it globally! This causes subtle bugs in scripts. Always use `local` for function variables. |
| "`for line in $(cat file)` processes lines" | `$(cat file)` is subject to word splitting and globbing. It processes WORDS, not LINES. `for line in a b c` with `a b c` on one line gives 3 iterations. Use `while IFS= read -r line; do ... done < file` for line-by-line processing. |
| "Comparing numbers with == works" | `==` in `[[ ]]` does STRING comparison. `[[ 10 == 9+1 ]]` is FALSE (string "10" != "9+1"). For arithmetic: use `[[ 10 -eq 10 ]]` (integer comparison) or `(( 10 == 9+1 ))` (arithmetic context). `(( ))` evaluates arithmetic, `[[ ]]` compares strings or uses `-eq/-gt/-lt` for integers. |

---

### Failure Modes & Diagnosis

**Script deletes wrong files due to glob expansion:**
```bash
# Script had:
DIR="/var/app/backups"
ls $DIR/*.tar.gz   # works fine normally

# But when no files match: bash expands to the literal string
# /var/app/backups/*.tar.gz (if nullglob not set)
# rm $DIR/*.tar.gz -> tries to rm "/var/app/backups/*.tar.gz" literally
# or with set -e: exits. Better than deleting nothing or wrong files.

# Diagnosis: add set -x to trace:
bash -x myscript.sh   # prints each command before executing

# Fix: handle empty glob explicitly:
shopt -s nullglob    # empty glob expands to nothing (not literal *)
files=("$DIR"/*.tar.gz)
if [[ ${#files[@]} -eq 0 ]]; then
    echo "No backup files found"
    exit 0
fi
# Process ${files[@]} safely
```

---

### Related Keywords

**Foundational:**
LNX-006 (Terminal), LNX-017 (Shell Scripting)

**Builds on this:**
LNX-066 (Bash Advanced Features)

**Related:**
LNX-043 (Regular Expressions)

---

### Quick Reference Card

| Syntax | Purpose |
|--------|---------|
| `set -euo pipefail` | Strict mode (fail fast) |
| `[[ -f file ]]` | File exists |
| `[[ -z "$var" ]]` | String is empty |
| `[[ "$a" == "$b" ]]` | String equality |
| `[[ $n -gt 5 ]]` | Integer greater than |
| `for x in list; do done` | Loop over list |
| `while IFS= read -r line; do done < file` | Line-by-line file |
| `for (( i=0; i<n; i++ )); do done` | C-style counter loop |
| `command \|\| { echo "failed"; exit 1; }` | Error handling |
| `trap 'cleanup' EXIT` | Run on exit |

**3 things to remember:**
1. Always start scripts with `set -euo pipefail` (fail fast, catch unset variables, catch pipe failures)
2. Use `[[ ]]` not `[ ]` in bash (no word splitting, better features)
3. Quote ALL variable expansions: `"$var"`, `"${array[@]}"` - unquoted variables cause subtle bugs

---

### Transferable Wisdom

Bash scripting patterns appear in: CI/CD pipelines (GitHub Actions shell steps,
Jenkins sh blocks), Dockerfile RUN commands, Kubernetes init containers and
lifecycle hooks, Helm chart hooks, entrypoint scripts in containers, cloud
init scripts (AWS user data, GCP startup scripts), Ansible shell/command
modules. The same `set -euo pipefail` discipline applies everywhere bash
runs.

The "exit code as boolean" model is universal in Unix: `make` stops on first
non-zero exit, `&&` chains in shell, Python `subprocess.check_call()`, Go's
`exec.Command().Run()` returning error on non-zero - all use the same convention.
Understanding it in bash makes you understand it everywhere.

---

### The Surprising Truth

`echo` behaves differently across systems. `echo -e "line1\nline2"` interprets
`\n` as newline on many systems but NOT on all (the `-e` flag is not POSIX).
On macOS, `echo` ignores `-e`. Bash's built-in `echo` vs `/bin/echo` may also
differ. The POSIX-correct alternative is `printf "line1\nline2\n"` which
consistently interprets escape sequences. This is why many shell style guides
say "prefer `printf` over `echo` in scripts." Another trap: `echo "$(command)"` 
strips trailing newlines from command output. This is usually what you want
(cleaner output), but if you're processing binary data or content that ends
with newlines, the stripping can corrupt it. The `printf "%s" "$(command)"`
pattern preserves the output except for the final newline stripping (which is
a bash limitation you can work around with tricks like appending a character).

---

### Mastery Checklist

- [ ] Can write a bash script with proper set -euo pipefail and error handling
- [ ] Can use [[ ]] for string and file tests with correct syntax
- [ ] Can iterate over file lines with while IFS= read -r
- [ ] Can use trap for cleanup on script exit
- [ ] Can quote variables correctly to prevent word splitting issues

---

### Think About This

1. You have a bash script with `set -e`. Inside a function, you run
   `grep "pattern" file`. If the pattern is not found, grep returns exit
   code 1. With `set -e`, does the script exit? What if the grep is
   inside an `if grep ...; then` construct? How does `set -e` interact
   with commands used as conditions?

2. Consider this script fragment:
   ```bash
   for file in *.txt; do rm "$file"; done
   ```
   This works fine when .txt files exist. What happens when there are NO
   .txt files? What is `$file` set to? How do you fix the script to handle
   this case? (Research: nullglob)

3. `while IFS= read -r line; do` - explain each part of this idiom:
   what does `IFS=` do (why set it empty here)? What does `-r` do?
   Why is `< file` at the end of the `done` better than `cat file |
   while read line`? (Hint: subshell and variable scope)

---

### Interview Deep-Dive

**Foundational:**
Q: What does `set -euo pipefail` do in a bash script and why is it important?
A: `set -e` (errexit): the script exits immediately when any command returns a non-zero exit code. Without it, scripts silently continue past failures. Example: `mkdir /nonexistent_path; cd /nonexistent_path; rm -rf *` - without `set -e`, if mkdir fails, `cd` still runs (to current dir), `rm -rf *` runs in current directory. `set -u` (nounset): treats references to undefined variables as errors. Without it: `rm -rf $DEPLOY_DIR/` where DEPLOY_DIR is unset becomes `rm -rf /` - catastrophic. With `set -u`: script exits with "DEPLOY_DIR: unbound variable". `set -o pipefail`: in a pipeline `cmd1 | cmd2 | cmd3`, bash normally returns the exit code of the LAST command. `pipefail` returns the exit code of the RIGHTMOST failing command. Without it: `invalid_command | grep "pattern"` - if `invalid_command` fails but `grep` succeeds, the pipeline returns 0 (success). With `pipefail`: returns the non-zero exit from `invalid_command`. Together these three make scripts fail fast and visibly, preventing the script from running subsequent commands with incorrect assumptions.

**Intermediate:**
Q: What is the difference between using for loop with command substitution vs while read for processing command output?
A: `for line in $(command)`: uses command substitution, then word-splits the output. Word splitting splits on spaces, tabs, newlines. So `"hello world"` becomes two loop iterations: "hello" and "world". Additionally, glob patterns in output are expanded (a line containing `*` becomes a list of files). This is almost never what you want for line-by-line processing. `while IFS= read -r line; do ... done < <(command)`: reads one line at a time. `IFS=` prevents leading/trailing whitespace trimming. `-r` prevents backslash interpretation. Each line is one iteration regardless of spaces. `< <(command)` uses process substitution to avoid a subshell (important: variables set in the `while` body ARE visible after the loop, unlike `command | while`). When to use each: `for item in item1 item2 item3`: fine for short static lists. `for item in $(command)`: only if output is single-word tokens with no spaces and you've verified no glob expansion. `while IFS= read -r line`: for any line-by-line file/command output processing - always prefer this. Example: `while IFS= read -r line; do echo "$line"; done < /etc/hosts` is always correct. `for line in $(cat /etc/hosts)` breaks on the first line: `127.0.0.1   localhost` becomes 2+ separate iterations.

**Expert:**
Q: How do you write a bash script that runs multiple commands in parallel and properly handles failure of any individual parallel job?
A: Bash parallel execution with proper error handling:
```bash
#!/bin/bash
set -euo pipefail

run_parallel() {
    local -a pids=()
    local -a names=()
    local failed=0
    
    # Start all jobs in background:
    for server in "$@"; do
        check_server "$server" &
        pids+=($!)
        names+=("$server")
    done
    
    # Wait for each job and collect results:
    for i in "${!pids[@]}"; do
        if ! wait "${pids[$i]}"; then
            echo "FAILED: ${names[$i]}" >&2
            (( failed++ ))
        else
            echo "OK: ${names[$i]}"
        fi
    done
    
    return $failed
}
```
Key points: (1) `&` starts background, `$!` captures PID. (2) `wait PID` blocks until that specific PID exits, returns its exit code. (3) Must capture ALL PIDs before waiting (otherwise some finish before we call wait and their status is lost... actually bash buffers exit statuses, but explicit capture is clearer). (4) `wait` without PID waits for all background jobs and returns 0 even if some failed - always wait for specific PIDs. (5) `(( failed++ ))` - arithmetic in bash; won't trigger `set -e` even if failed becomes non-zero because `(( 0 ))` exits 1 but `(( 1 ))` exits 0. (6) For output isolation (prevent interleaving), redirect each job to a temp file: `job > /tmp/job_$$.log 2>&1 &`. Advanced: use `xargs -P8 -I{} command {}` for parallel execution over a list without managing PIDs manually. GNU Parallel for sophisticated parallel workloads with retry, progress, and output management.
