---
id: LNX-024
title: "Shell Scripting Basics (bash, shebang, variables)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-015, LNX-016, LNX-012
used_by: LNX-042, LNX-030
related: LNX-042, LNX-066, LNX-030
tags: [bash, shell-scripting, shebang, variables, functions, exit-codes, automation]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/lnx/shell-scripting-basics/
---

## TL;DR

A shell script is a text file of commands, starting with a shebang
(`#!/bin/bash`), made executable with `chmod +x`. Variables: `VAR=value`
(no spaces), referenced as `$VAR`. Exit codes: 0 = success, non-zero
= failure. `set -euo pipefail` at the top makes scripts fail fast on
errors. Shell scripting is the glue that holds Linux automation together:
deployments, backups, monitoring, and CI/CD pipelines all rely on it.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-024 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | bash, shell script, shebang, variables, functions, exit codes |
| **Prerequisites** | LNX-015, LNX-016, LNX-012 |

---

### The Problem This Solves

Manual server administration: run 10 commands in sequence, copy the
output of one into the next, repeat for 50 servers. Shell scripts
automate this: write once, run anywhere. Deploy code, rotate logs,
backup databases, check system health, restart failed services. Shell
scripting is the universal automation language of Linux system
administration.

---

### Textbook Definition

A **shell script** is a text file containing shell commands that are
executed sequentially by the shell interpreter. The interpreter is
specified in the first line: `#!/bin/bash` (shebang + path to bash).

Key concepts:
- **Shebang**: `#!/path/to/interpreter` on the first line
- **Variables**: store values, referenced with `$`
- **Exit code**: every command exits with 0 (success) or non-zero (failure)
- **Control flow**: if/elif/else, for, while, case
- **Functions**: named command groups for reuse
- **Positional parameters**: `$1`, `$2`, ... = script arguments

---

### Understand It in 30 Seconds

```bash
#!/bin/bash
# Minimal viable shell script

# Set fail-fast options:
set -euo pipefail
# -e: exit on any error
# -u: error on undefined variables
# -o pipefail: fail if any command in a pipeline fails

# Variables (no spaces around =):
NAME="World"
COUNT=42
TODAY=$(date +%Y-%m-%d)   # capture command output

echo "Hello, $NAME!"
echo "Count is: $COUNT"
echo "Today is: $TODAY"

# Check arguments:
if [ $# -eq 0 ]; then
    echo "Usage: $0 <environment>" >&2
    exit 1
fi
ENVIRONMENT="$1"   # first argument

# If/else:
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode"
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo "Running in staging mode"
else
    echo "Unknown environment: $ENVIRONMENT" >&2
    exit 1
fi

# For loop:
for server in web1 web2 web3; do
    echo "Deploying to $server..."
done
```

---

### First Principles

**The shebang line:**
`#!/bin/bash` tells the kernel: run this file using `/bin/bash` as the
interpreter. Without it: the kernel tries to run the file as machine code
(fails). Or the current shell tries to interpret it (might work accidentally
if you're using bash, but unreliable).
`#!/usr/bin/env bash`: more portable - finds bash in PATH, handles installations
at non-standard locations (macOS, nix, conda environments).

**Exit codes are the contract:**
Every command, every script, every function returns an exit code.
0 = success. 1-255 = various failure codes. `$?` = exit code of the last command.
This is how commands communicate status to the shell and to callers.
`set -e` exploits this: if any command returns non-zero, stop immediately.
Without it: a failed command is ignored and the script keeps running
(potentially with incorrect state).

**Variable scoping:**
```bash
MY_VAR=value          # shell variable (local to current shell)
export MY_VAR=value   # environment variable (inherited by children)
local MY_VAR=value    # function-local (inside functions only)
```

---

### Thought Experiment

A deployment script WITHOUT `set -euo pipefail`:
```bash
#!/bin/bash
wget https://example.com/myapp.jar  # fails (wrong URL)
# wget exits with error, but script continues!
cp myapp.jar /opt/myapp/            # copies nothing or partial download
systemctl restart myapp             # restarts with corrupted file
# Production is now running a broken application
```

The same script WITH `set -euo pipefail`:
```bash
#!/bin/bash
set -euo pipefail
wget https://example.com/myapp.jar  # fails
# Script STOPS HERE (non-zero exit from wget)
# cp and systemctl are never run
# Production continues running the old, working version
```

`set -euo pipefail` is the difference between a script that silently
corrupts production and one that fails loudly with minimal damage.

---

### Mental Model / Analogy

A shell script is like a **recipe in a kitchen:**

```
Shebang (#!/bin/bash) = "Use this chef to make this recipe"
  (the interpreter who follows the instructions)

Variables = ingredients list:
  FLOUR=500g
  EGGS=3
  (assign once, reference throughout)

exit code = recipe step outcome:
  0 = "step completed successfully"
  1+ = "something went wrong - stop? continue?"

set -e = "if any step fails, stop cooking"
  Without it: use burnt cake as a base for the next layer
  With it: notice the burned step and start over

Functions = sub-recipes you can reuse:
  prep_vegetables() { wash, cut, season; }
  Call it multiple times in the main recipe

$1, $2 = recipe variations:
  "Make this recipe for $1 people with $2 protein"
  ./recipe.sh 4 chicken
```

---

### Gradual Depth - Five Levels

**Level 1:**
shebang + set -euo pipefail + variables + echo. That's a functional script.
Add arguments with `$1`, `$2`, `$#` (count). Exit with `exit 0` (success)
or `exit 1` (failure). stderr with `>&2`.

**Level 2:**
Functions: `function_name() { commands; return 0; }`. Call: `function_name arg`.
Arrays: `ITEMS=("a" "b" "c")`. Access: `${ITEMS[0]}`, all: `${ITEMS[@]}`.
String operations: `${VAR#prefix}` (remove prefix), `${VAR%suffix}` (remove suffix),
`${VAR/old/new}` (replace first), `${VAR//old/new}` (replace all).

**Level 3:**
Process management in scripts: `command &` runs in background. `wait PID`
waits for it. `$!` = last background PID. `trap 'cleanup' EXIT SIGTERM SIGINT`
= run cleanup function when script exits (for temp files, process cleanup).
`mktemp` for safe temp files. `$(command)` vs `` `command` `` (prefer $()).

**Level 4:**
Here documents for multi-line input:
```bash
cat <<EOF
line 1
line 2
EOF
```
`read -r line` for reading input. `IFS` (Input Field Separator) controls
splitting. `getopts` for proper option parsing. Shell arithmetic:
`$((A + B))`. `bc` for floating point: `echo "3.14 * 2" | bc`.

**Level 5:**
Production-grade scripting: linting with shellcheck. Testing with bats
(Bash Automated Testing System). Error handling with trap + cleanup functions.
Concurrent execution with parallel and wait. Configuration management
scripts (though at scale: Ansible, Terraform are better). Script idempotency:
writing scripts that can be safely re-run (check before act pattern).

---

### Code Example

**BAD - unsafe script patterns:**
```bash
#!/bin/bash
# BAD: no set -euo pipefail
# BAD: no error handling
# BAD: spaces in variable assignment
DIR = /tmp/myapp   # SYNTAX ERROR: spaces around =
mkdir $DIR         # unquoted: breaks on spaces/special chars
cd $DIR            # if cd fails, script continues in wrong dir!
rm -rf *           # DANGEROUS if cd failed: deletes everything!
```

**GOOD - production-quality script structure:**
```bash
#!/usr/bin/env bash
# Script: deploy.sh - Deploy myapp to server
# Usage: ./deploy.sh <environment> <version>

set -euo pipefail
set -x   # optional: print each command before executing (debug mode)

# Constants:
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/myapp/deploy.log"
readonly APP_DIR="/opt/myapp"

# Log function:
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Cleanup function - runs on exit (success or failure):
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log "ERROR: Deployment failed with exit code $exit_code"
        # Could: rollback, send alert, etc.
    fi
    rm -f "/tmp/myapp-deploy-$$"   # $$ = current PID (unique temp name)
}
trap cleanup EXIT

# Argument validation:
if [ $# -ne 2 ]; then
    echo "Usage: $0 <environment> <version>" >&2
    echo "  environment: dev|staging|production" >&2
    echo "  version: e.g., 1.2.3" >&2
    exit 1
fi

ENVIRONMENT="$1"
VERSION="$2"

# Validate environment:
case "$ENVIRONMENT" in
    dev|staging|production)
        log "Deploying version $VERSION to $ENVIRONMENT"
        ;;
    *)
        echo "Invalid environment: $ENVIRONMENT" >&2
        exit 1
        ;;
esac

# Main deployment logic:
deploy() {
    local env="$1"
    local version="$2"
    
    log "Downloading myapp-${version}.jar..."
    wget -q "https://artifacts.example.com/myapp-${version}.jar" \
        -O "/tmp/myapp-deploy-$$"
    
    log "Stopping old service..."
    sudo systemctl stop myapp || true   # || true: don't fail if not running
    
    log "Installing new version..."
    sudo cp "/tmp/myapp-deploy-$$" "${APP_DIR}/myapp.jar"
    sudo chown myapp:myapp "${APP_DIR}/myapp.jar"
    
    log "Starting service..."
    sudo systemctl start myapp
    
    log "Verifying deployment..."
    sleep 5
    if ! curl -sf "http://localhost:8080/health" > /dev/null; then
        log "Health check failed!"
        return 1
    fi
    
    log "Deployment successful!"
}

deploy "$ENVIRONMENT" "$VERSION"
```

---

### Script Structure Reference

```
#!/usr/bin/env bash       <- shebang (always first line!)
set -euo pipefail         <- fail-fast options (always third!)
                           
# Constants (readonly):
readonly VAR="value"

# Variables:
VAR="value"

# Functions:
function_name() {
    local var="$1"   # local scope inside function
    echo "$var"
    return 0         # explicit return code
}

# Main logic:
main() {
    function_name "arg"
}

# Call main:
main "$@"            # pass all script arguments to main

# Exit codes:
exit 0    # success
exit 1    # generic failure
exit 2    # usage error (wrong arguments)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Shell scripts are safe without error handling" | Without `set -e`, a script continues after command failures. `wget fails -> cp /dev/null -> systemctl restart broken_app` is a real failure mode. `set -euo pipefail` is non-optional for production scripts. |
| "Variables don't need quotes: `$VAR` is fine" | Unquoted: `rm $FILE` where FILE="my file.txt" becomes `rm my file.txt` -> tries to remove `my` and `file.txt` separately. Quote ALL variable expansions: `rm "$FILE"`. The only exception: arithmetic `$((VAR + 1))`. |
| "exit 0 means the script ran but found nothing" | exit 0 always means SUCCESS. If grep finds no matches: exit 1 (failure). If find finds no files: exit 0 (success). Know the exit code semantics of the commands you use. |
| "#!/bin/bash and #!/usr/bin/env bash are the same" | `/bin/bash` requires bash to be at that specific path. `/usr/bin/env bash` finds bash in PATH - more portable across distros (Homebrew macOS: bash may be at `/opt/homebrew/bin/bash`). |
| "set -e catches all errors" | `set -e` doesn't catch errors in: compound commands where the failing command isn't the last, commands in `if` conditions, commands in `while`/`until` conditions, or functions called with `!`. It's useful but not complete. Pair with `trap 'log "Error at line $LINENO"' ERR` for better coverage. |

---

### Failure Modes & Diagnosis

**Script stops with "unbound variable":**
```bash
# Error: bash: MY_VAR: unbound variable
# Cause: set -u + using undefined variable
MY_VAR=""    # you think this sets it to empty string
echo "${MY_VAR:-}"  # safe: uses empty string if unset
# Or: check if set:
if [ -n "${MY_VAR:-}" ]; then ...

# Safe default value:
VALUE="${MY_VAR:-default_value}"
```

**"Argument list too long" in for loop:**
```bash
# BAD: glob expands to too many files
for file in /logs/*.log; do   # 100,000 .log files = ARG_MAX exceeded

# GOOD: use find + read
while IFS= read -r -d '' file; do
    process "$file"
done < <(find /logs -name "*.log" -print0)
# -print0 and -d '' handle filenames with spaces
```

**Security: command injection:**
```bash
# BAD: user input in command
filename="$1"
cat "$1"   # if filename = "; rm -rf /", command becomes: cat ; rm -rf /
           # (with unquoted $1 in some contexts)

# GOOD: validate input first
if [[ "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    cat "$filename"
else
    echo "Invalid filename" >&2
    exit 1
fi
```

---

### Related Keywords

**Foundational:**
LNX-015 (Standard Streams), LNX-016 (Pipes)

**Builds on this:**
LNX-042 (Bash Advanced Features), LNX-066 (Bash Advanced Scripting),
LNX-030 (Cron Jobs)

**Related:**
LNX-043 (Regular Expressions), LNX-047 (Process Signals)

---

### Quick Reference Card

| Concept | Syntax |
|---------|--------|
| Shebang | `#!/usr/bin/env bash` |
| Fail-fast | `set -euo pipefail` |
| Variable | `VAR=value` (no spaces) |
| Reference | `"$VAR"` (always quote!) |
| Command output | `VAR=$(command)` |
| First argument | `$1` |
| Argument count | `$#` |
| Last exit code | `$?` |
| Current PID | `$$` |
| If check | `if [ condition ]; then ... fi` |
| For loop | `for x in list; do ... done` |
| Function | `name() { ... ; return 0; }` |
| Stderr output | `echo "error" >&2` |
| Exit success | `exit 0` |
| Exit failure | `exit 1` |

**3 things to remember:**
1. Always start with `set -euo pipefail` - makes scripts fail fast on errors
2. Always quote variables: `"$VAR"` not `$VAR` (prevents word-splitting on spaces)
3. Validate all external input before using in commands (prevents injection)

---

### Transferable Wisdom

Shell scripting is the foundation of all Linux automation, but it has
clear limits. Scripts that grow beyond 200 lines: consider Python (better
data structures, error handling, testing). Scripts that need parallel
coordination: Ansible (idempotent, declarative, scales to thousands of hosts).
Scripts that manage cloud resources: Terraform (state tracking, plan/apply).
The principle: use shell for OS-level glue between programs; use a real
programming language for business logic; use specialized tools for
infrastructure management.

The `set -euo pipefail` pattern and exit code convention appear in all
deployment tooling. Docker RUN: each command must succeed or the build fails.
GitHub Actions steps: non-zero exit code fails the job. The convention
transfers everywhere: 0 = success, non-zero = failure.

---

### The Surprising Truth

The `$(( ))` arithmetic in bash uses 64-bit signed integers. Bash has
NO native floating-point support. `echo $((3/2))` = `1` (integer division,
not 1.5). Engineers expecting decimal math from bash get silently wrong
results. Fix: use `bc -l` (arbitrary precision): `echo "3 / 2" | bc -l` = `1.50000000000000000000`. Or use Python: `python3 -c "print(3/2)"` = `1.5`. This is one of the reasons shell scripting is unsuitable for anything involving calculations beyond integer arithmetic. Another surprise: bash integers overflow silently at 2^63 - 1 (about 9.2 x 10^18). No warning, just wrong results.

---

### Mastery Checklist

- [ ] Can write a working script with shebang, set -euo pipefail, and proper structure
- [ ] Can use variables correctly with proper quoting
- [ ] Can write if/elif/else, for loops, and functions
- [ ] Can handle script arguments and validate them
- [ ] Can implement a trap-based cleanup function

---

### Think About This

1. You have `set -e` in your script. You run `grep pattern file` and grep
   finds no matches (exit code 1). Your script terminates. But you wanted
   it to continue (no matches is a valid case). How do you handle this
   without removing `set -e`?

2. Your script creates a temp directory, does work in it, and should
   delete it on exit - whether the script succeeds or fails. How do you
   implement this with `trap`? What happens if the script is killed with
   SIGKILL?

3. `local VAR=$(failing_command)` with `set -e` does NOT exit the script
   on failure. Why not? How do you correctly capture command output AND
   check for errors in the same operation?

---

### Interview Deep-Dive

**Foundational:**
Q: What does `set -euo pipefail` do in a shell script and why is it recommended?
A: It enables three safety behaviors: (1) `-e` (errexit): script exits immediately when any command returns non-zero exit code. Without it, failed commands are silently ignored and the script keeps running with potentially incorrect state. (2) `-u` (nounset): treats references to undefined variables as errors. Without it, `$UNDEFINED_VAR` silently expands to empty string, causing subtle bugs (e.g., `rm -rf "$DIR/"` where DIR is empty = `rm -rf /`). (3) `-o pipefail`: pipeline's exit code is the exit code of the rightmost non-zero command. Without it, `failing_cmd | wc -l` exits 0 (wc succeeded on empty input). Together, they make scripts fail loudly and immediately when something goes wrong, rather than silently continuing with bad state. The alternative is explicitly checking `$?` after every command - `set -euo pipefail` automates this.

**Intermediate:**
Q: Write a function that creates a temp file, does some work, and guarantees cleanup even if the script is killed.
A:
```bash
#!/usr/bin/env bash
set -euo pipefail

TMPFILE=""

cleanup() {
    local exit_code=$?
    if [ -n "$TMPFILE" ] && [ -f "$TMPFILE" ]; then
        rm -f "$TMPFILE"
        echo "Cleaned up $TMPFILE" >&2
    fi
    exit $exit_code
}
trap cleanup EXIT SIGTERM SIGINT

do_work() {
    TMPFILE=$(mktemp /tmp/myapp.XXXXXXXX)
    echo "Working with $TMPFILE..."
    # Do work...
    process_data > "$TMPFILE"
    cat "$TMPFILE"
    # TMPFILE cleaned up by trap on EXIT
}

do_work
```

Key points: `trap cleanup EXIT` runs on ANY exit (normal, error, Ctrl+C). `mktemp` creates a uniquely named temp file safely. SIGKILL (kill -9) cannot be trapped - it's the one case where cleanup doesn't run. For SIGKILL resilience: use PID-named files and a separate cleanup process, or use systemd's temporary file management.

**Expert:**
Q: How would you make a shell script idempotent so it can be safely re-run even if it failed halfway through?
A: Idempotency means: running the script multiple times produces the same result as running it once. Strategies: (1) Check before act: `[ -f /opt/myapp/myapp.jar ] || wget -O /opt/myapp/myapp.jar https://...` (only download if not present). (2) Use atomic operations: copy to temp file, then `mv` into place (mv is atomic). (3) Idempotent service control: `systemctl is-active myapp && systemctl restart myapp || systemctl start myapp`. (4) Track state: write state files: `echo "downloaded" > /tmp/deploy-state/step1.done` and check them: `[ -f /tmp/deploy-state/step1.done ] || do_step1`. (5) Use idempotent tools instead: instead of raw scripts, use Ansible (built-in idempotency), or systemd unit files (declarative desired state). The key principle: each step should either succeed (already done or done now) or fail loudly. Never leave the system in a partial state that prevents re-running.
