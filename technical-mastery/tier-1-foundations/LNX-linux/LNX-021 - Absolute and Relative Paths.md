---
id: LNX-021
title: Absolute and Relative Paths
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-007
used_by: LNX-008, LNX-010
related: LNX-007, LNX-008, LNX-025
tags: [paths, absolute, relative, filesystem, navigation, pwd, cd]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/lnx/absolute-and-relative-paths/
---

## TL;DR

Absolute paths start from `/` (root) and always work regardless
of current directory: `/etc/nginx/nginx.conf`. Relative paths
start from the current directory and depend on where you are:
`../config/nginx.conf`. Absolute paths are safer in scripts;
relative paths are faster to type interactively. Production
scripts should always use absolute paths to avoid broken-context
bugs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-021 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | absolute path, relative path, /, .., pwd, cd, filesystem navigation |
| **Prerequisites** | LNX-007 |

---

### The Problem This Solves

When a script runs `cat config.yaml`, does it find the file?
Depends on where the script was run from (the current directory).
If the script is in /opt/myapp but run from /home/alice, it looks
for /home/alice/config.yaml - wrong. Absolute paths eliminate this
ambiguity. Understanding the difference prevents the most common
scripting bug: "works when I run it manually but fails in cron/systemd."

---

### Textbook Definition

**Absolute path**: starts with `/` (root directory). Specifies the
complete path from the filesystem root. Always unambiguous, always
refers to the same file regardless of current directory.
Examples: `/etc/passwd`, `/var/log/nginx/access.log`, `/home/alice/.bashrc`

**Relative path**: starts with `.` (current directory), `..` (parent),
or directly with a filename/directory name. Interpreted relative to
the process's current working directory (CWD). The same relative path
means different files depending on the CWD.
Examples: `config.yaml`, `./start.sh`, `../logs/app.log`, `../../etc/nginx`

Special notation:
- `.`: current directory
- `..`: parent directory
- `~`: current user's home directory (shell expands this)
- `~alice`: alice's home directory

---

### Understand It in 30 Seconds

```bash
# Absolute paths (always start with /):
/etc/nginx/nginx.conf          # config file
/var/log/myapp/app.log         # log file
/home/alice/scripts/deploy.sh  # script in alice's home

# Relative paths (start from where you are now):
pwd                            # show current directory: /home/alice
ls scripts/                    # look in ./scripts/ (current dir/scripts)
cat ../config.yaml             # one level up, then config.yaml
./deploy.sh                    # run deploy.sh in current directory

# Tilde expansion (shell only):
cd ~               # go to your home directory (/home/alice)
cd ~/documents     # go to /home/alice/documents
cat ~/.bashrc      # read /home/alice/.bashrc
cp file ~alice/    # copy to alice's home dir

# Convert relative to absolute:
realpath ../config.yaml   # shows the absolute path of a relative path
readlink -f ./symlink     # shows real path, resolving symlinks too

# Path segments:
/var/log/nginx/access.log
  /      = root
  var    = first directory
  log    = subdirectory
  nginx  = subdirectory
  access.log = filename
```

---

### First Principles

**Current working directory (CWD) is a process property:**
Every process has a CWD. When you open a terminal, the shell's CWD
is usually your home directory. When you `cd /tmp`, the shell's CWD
changes. When you run a script, the script inherits the CWD of the
shell that ran it. When cron runs a script, the CWD might be `/` or
the home directory. This is why relative paths in scripts are fragile.

**Path resolution algorithm:**
```
/var/log/../log/nginx = /var/log/nginx
  (.. goes up one level, then down into log)

./script.sh = current_directory + /script.sh

~alice/file = /home/alice/file (shell expands ~ to home dir)
             (note: ~ expansion is a SHELL feature, not kernel feature)
             (~ does NOT work in scripts when not run through bash)
```

---

### Thought Experiment

Your Java application has this in its config:
```
log.dir=logs/myapp/
```

The application reads this file and writes logs to `logs/myapp/`.

**Scenario A**: You start the application from `/opt/myapp`:
- CWD = `/opt/myapp`
- Logs go to: `/opt/myapp/logs/myapp/` ✓ (expected location)

**Scenario B**: The systemd service starts the application:
- systemd default CWD might be `/` or the user's home
- Logs go to: `/logs/myapp/` or `/home/appuser/logs/myapp/` (wrong!)
- Error: "cannot create directory /logs/myapp: Permission denied"

**Fix**: Use absolute path:
```
log.dir=/var/log/myapp/
```
Now it works regardless of CWD.

This is the #1 reason production applications should use absolute
paths for all file references.

---

### Mental Model / Analogy

Paths are like **giving directions:**

```
Absolute path = GPS coordinates / full street address
  "1600 Pennsylvania Avenue NW, Washington DC"
  Works from anywhere - no context needed
  
Relative path = directions from your current location
  "Go two blocks north, turn left"
  Only works if you know where you're starting from
  
. (dot) = "here" (your current location)
.. (dotdot) = "one block back"
~ (tilde) = "your home address"

Script with relative paths = giving directions from an
  unknown starting point - they might be right, might be wrong
  depending on where the person started
  
Script with absolute paths = giving the full address -
  always unambiguous, always correct
```

---

### Gradual Depth - Five Levels

**Level 1:**
Absolute = starts with `/`, always works. Relative = starts from CWD.
`. ` = here, `..` = parent, `~` = home. Scripts: use absolute paths
for reliability.

**Level 2:**
`realpath file` converts relative to absolute. `dirname /path/to/file`
= `/path/to` (directory part). `basename /path/to/file` = `file` (filename
part). These are useful in scripts: `SCRIPT_DIR="$(dirname "$(realpath "$0")")"` 
gets the directory where the script lives, regardless of CWD.

**Level 3:**
Symlinks create apparent paths: `/usr/bin/python3` might be a symlink to
`/usr/bin/python3.10`. `realpath` resolves symlinks to canonical path.
`readlink -f path` = same. Security: `../` traversal in web apps = path
traversal vulnerability. User provides `../../etc/passwd` as a filename
-> server reads `/etc/passwd`. Always sanitize paths from external input.

**Level 4:**
Script best practice:
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# SCRIPT_DIR = absolute path of directory containing this script
# Works even if script is called with relative path or via symlink
CONFIG="$SCRIPT_DIR/../config/app.yaml"  # relative to script's location
```

**Level 5:**
In distributed systems: paths on one node may not exist on another.
Docker containers: `/app/config.yaml` inside the container vs
`/data/myapp/config.yaml` on host (mounted via volume). File paths
in microservices should be configuration values, not hardcoded.
Kubernetes ConfigMaps/Secrets: mounted at a specific absolute path
in the container, configured by the platform administrator.

---

### Code Example

**BAD - relative paths in scripts:**
```bash
#!/bin/bash
# BAD: relative path - breaks when script is run from wrong directory
cat config.yaml   # works only if CWD is the script's directory!

# BAD: tilde in non-interactive contexts
scp ~/file.txt server:~/   # ~ may not expand in all contexts

# BAD: relative path in systemd service
[Service]
ExecStart=./start.sh   # CWD is undefined - this will fail
```

**GOOD - absolute paths in scripts:**
```bash
#!/bin/bash
# GOOD: get script's directory, compute paths relative to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config/app.yaml"
LOG_DIR="/var/log/myapp"    # absolute, always correct

# Read config relative to script location (not CWD):
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config not found: $CONFIG_FILE" >&2
    exit 1
fi

# Good Java property (absolute path):
# application.properties:
# logging.file.name=/var/log/myapp/app.log
# NOT: logging.file.name=logs/app.log (relative!)

# Good systemd service:
[Service]
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/start.sh   # absolute path
# And in start.sh:
# use absolute paths for all file references
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`./script.sh` and `script.sh` are the same" | In bash: `script.sh` searches PATH for a file named script.sh. `./script.sh` explicitly runs script.sh in the current directory. If there's a system command named `script`, they differ. For running local scripts: always use `./`. |
| "Tilde (`~`) works everywhere" | `~` is expanded by the SHELL. Inside double-quoted strings in scripts it may not expand. In Java properties files: never expands. In Python os.path: never expands (use `os.path.expanduser('~')` explicitly). |
| "Absolute paths are always long" | `/tmp/file.txt` is an absolute path with just 14 characters. Absolute means "starts from root", not "is long." Relative paths can be longer (../../../../some/deep/path/file.txt). |
| "Current directory `.` is the same as home directory `~`" | `.` = wherever you are NOW (may change with cd). `~` = your home directory (fixed). After `cd /tmp`, `.` = /tmp but `~` = /home/alice. |
| "Relative paths can't go above the root" | `../../../../../../..` will stop at `/` (the root). You cannot go above root. Any number of `..` from root is still root: `cd /; cd ../../../` = you're still at `/`. |

---

### Failure Modes & Diagnosis

**Script works in terminal but fails in cron:**
```bash
# Symptom: script works when you run it; cron says "file not found"
# Cause: cron's CWD is / (or home); relative paths resolve differently

# Diagnosis:
# Add to cron for debugging:
* * * * * /bin/bash -c 'pwd >> /tmp/cron-debug.txt'
# Check what CWD cron uses

# Fix: use absolute paths in the script
# Check with:
cat /tmp/cron-debug.txt  # shows: / or /home/username

# Permanent fix: in the script, set absolute paths:
cd /opt/myapp || { echo "Cannot find /opt/myapp"; exit 1; }
# Then relative paths work from the expected location
```

**Path traversal security issue:**
```bash
# Vulnerability: user provides filename that escapes directory
# Insecure:
user_file="../../etc/passwd"
cat "/uploads/$user_file"   # reads /uploads/../../etc/passwd = /etc/passwd!

# Secure: normalize and validate path
safe_dir="/uploads"
requested_path="$safe_dir/$user_file"
canonical=$(realpath "$requested_path" 2>/dev/null)
if [[ "$canonical" != "$safe_dir"/* ]]; then
    echo "Path traversal detected!" >&2
    exit 1
fi
cat "$canonical"
```

---

### Related Keywords

**Foundational:**
LNX-007 (Linux File System Hierarchy), LNX-008 (Files and Directories)

**Builds on this:**
LNX-025 (find), LNX-024 (Shell Scripting), LNX-046 (Filesystem Internals)

**Related:**
LNX-035 (File Links), SEC-001 (Security - path traversal)

---

### Quick Reference Card

| Path | Type | Meaning |
|------|------|---------|
| `/etc/nginx/nginx.conf` | Absolute | Always this exact file |
| `config/app.yaml` | Relative | Relative to CWD |
| `./script.sh` | Relative | script.sh in CWD |
| `../config.yaml` | Relative | One level up, then config.yaml |
| `../../etc/nginx` | Relative | Two levels up, then etc/nginx |
| `~/documents` | Tilde | Home directory + /documents |
| `~alice/scripts` | Tilde | alice's home + /scripts |

**Useful commands:**

| Command | Purpose |
|---------|---------|
| `pwd` | Show current working directory |
| `realpath file` | Convert relative to absolute path |
| `dirname /path/file` | Get directory part of a path |
| `basename /path/file` | Get filename part of a path |

**3 things to remember:**
1. Absolute paths start with `/` and work from anywhere
2. Scripts: use `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` to get the script's own directory
3. Validate user-provided paths against a safe base directory to prevent path traversal attacks

---

### Transferable Wisdom

The absolute vs relative path distinction applies to every system
that has hierarchical naming: URLs (absolute: `https://example.com/path`,
relative: `../images/logo.png`), Java imports (fully qualified:
`com.example.MyClass` vs simple: `MyClass` depends on the current
package), file paths in Docker (COPY relative to build context),
and Kubernetes volume mounts (always absolute paths). The same mental
model applies everywhere: absolute = unambiguous from a global root;
relative = depends on context.

---

### The Surprising Truth

The `..` (dotdot) in a path does NOT always resolve to the logical
parent directory when symlinks are involved. If `/logs` is a symlink
to `/data/application/logs`, then `cd /logs; cd ..` takes you to `/`
(the parent of the symlink entry), NOT to `/data/application/`. This
is shell behavior. But `realpath /logs/..` = `/data/application` (resolves
the actual filesystem path). This distinction between the shell's logical
view (with `..` going up through symlinks) and the filesystem's physical
view (following symlinks to their targets) is a subtle trap in scripts
that navigate directory trees containing symlinks.

---

### Mastery Checklist

- [ ] Can explain the difference between absolute and relative paths with examples
- [ ] Can construct relative paths using `.` and `..` notation
- [ ] Can explain why relative paths in cron jobs or systemd services cause problems
- [ ] Can write the SCRIPT_DIR pattern to get a script's own directory
- [ ] Can explain path traversal vulnerability and how to prevent it

---

### Think About This

1. A script contains `cd "$(dirname "$0")"` at the start. When is this
   sufficient, and when does it fail? Consider the case where the script
   is called via a symlink. What's the more robust alternative?

2. `/proc/self` is a symlink to `/proc/PID` where PID is the current
   process. If you do `realpath /proc/self`, what do you get? What does
   this tell you about how the operating system implements the "current
   process" concept using the filesystem namespace?

3. In a Dockerfile, `COPY ./config /app/config` copies from the build
   context. The build context root is determined by the `docker build .`
   command (the `.` is the context). What are absolute vs relative paths
   in a Dockerfile relative to? What happens if you try `COPY ../config`?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between an absolute path and a relative path?
A: An absolute path starts with `/` and specifies the complete path from the filesystem root. It's unambiguous regardless of the current directory. Example: `/etc/nginx/nginx.conf` always refers to exactly that file. A relative path is interpreted relative to the current working directory (CWD). Example: `config/nginx.conf` means "config/nginx.conf in whatever directory I'm currently in." If CWD is `/opt/myapp`, it resolves to `/opt/myapp/config/nginx.conf`. If CWD is `/`, it resolves to `/config/nginx.conf`. The same relative path refers to different files depending on where you run the command. In production scripts, always use absolute paths to avoid "works manually but fails in cron" bugs caused by different CWD contexts.

**Intermediate:**
Q: How would you write a script that correctly finds its own configuration file regardless of where it's called from?
A: Use this pattern: `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`. Breaking it down: `${BASH_SOURCE[0]}` = the script's filename as called (works for sourced scripts, not just executed ones). `dirname` extracts the directory portion. `cd` changes to that directory. `pwd` prints the absolute path of that directory. The `&&` ensures we get the result only if cd succeeds. Now you can use: `CONFIG="$SCRIPT_DIR/../config/app.yaml"`. This works even if the script is called with a relative path, via symlink (mostly - symlinks are tricky), or from a completely different directory. For absolute correctness with symlinks: `realpath "${BASH_SOURCE[0]}"` then `dirname` on the result.

**Expert:**
Q: A web application receives a filename parameter from the user and reads the file from an uploads directory. What path traversal vulnerability exists and how do you prevent it?
A: The vulnerability: if the user provides `../../etc/passwd` as the filename, the code `file_path = "/uploads/" + user_filename` = `/uploads/../../etc/passwd` = `/etc/passwd` after path normalization. The app reads and returns the system password file. In Java/Python: never concatenate user input to a path prefix without validation. The correct defense: (1) Get the canonical (resolved, absolute) path: Java: `new File(baseDir, userFilename).getCanonicalPath()`; Python: `os.path.realpath(os.path.join(base_dir, user_filename))`. (2) Verify the canonical path starts with the allowed base directory: `if (!canonicalPath.startsWith(allowedBaseDir + File.separator)) throw SecurityException`. (3) Also validate the filename itself: allow only alphanumeric, dots, hyphens, underscores using a whitelist regex. (4) If using OS-level file access, the application process should not have read access to files outside its sandbox. Defense in depth: filesystem permissions + path validation. One layer is not enough.
