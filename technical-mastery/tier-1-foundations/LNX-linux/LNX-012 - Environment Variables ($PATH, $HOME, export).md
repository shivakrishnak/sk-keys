---
id: LNX-012
title: "Environment Variables ($PATH, $HOME, export)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006
used_by: LNX-024, LNX-030
related: LNX-006, LNX-024, LNX-070
tags: [environment-variables, PATH, export, shell, configuration, env]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/lnx/environment-variables/
---

## TL;DR

Environment variables are key=value pairs inherited by every
process from its parent. `$PATH` tells the shell where to find
commands. `export VAR=value` makes a variable available to child
processes. Configuration via environment variables is the 12-factor
app standard for production deployments. Every container deployment
uses `ENV` and `-e` flags to inject configuration this way.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-012 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | environment variables, PATH, HOME, export, shell, 12-factor |
| **Prerequisites** | LNX-006 |

---

### The Problem This Solves

Applications need configuration: database URLs, API keys, feature
flags. Hard-coding these in source code is a security disaster (keys
in git). Reading from files requires file management. Environment
variables solve this: they're injected at runtime, differ per
environment (dev/staging/prod), and never appear in version control.
Docker's `-e DB_URL=...` and Kubernetes ConfigMaps/Secrets use this
mechanism universally.

---

### Textbook Definition

An **environment variable** is a named string value associated with
a process's environment. Every process inherits environment variables
from its parent process. Variables are stored in the process's
address space and passed to child processes via fork()/exec().

Key properties:
- **Inherited**: child processes get copies of parent's environment
- **Not shared**: modifying a variable in one process does NOT affect
  parent or sibling processes
- **String-only**: all values are strings (no integers, no booleans)
- **Convention**: uppercase names (PATH, HOME, JAVA_HOME)

---

### Understand It in 30 Seconds

```bash
# View all environment variables:
env                    # prints all var=value pairs
printenv               # same as env
echo $PATH             # print one specific variable

# Set a variable (current shell only, NOT exported to children):
MY_VAR=hello
echo $MY_VAR           # works in current shell
bash -c 'echo $MY_VAR' # empty! not exported

# Export a variable (available to child processes):
export MY_VAR=hello
bash -c 'echo $MY_VAR' # prints: hello

# Unset a variable:
unset MY_VAR

# Common critical variables:
echo $PATH     # /usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
echo $HOME     # /home/alice
echo $USER     # alice
echo $SHELL    # /bin/bash
echo $JAVA_HOME # /usr/lib/jvm/java-17-openjdk

# One-time variable for a single command:
DB_URL=postgres://localhost/mydb java -jar app.jar
# DB_URL is only in the environment of that java process
```

---

### First Principles

**How PATH works:**
When you type `ls`, the shell doesn't know where `ls` is. It searches
each directory in $PATH in order, left to right, looking for an
executable named `ls`. First match wins. This is why:
- `which ls` shows `/bin/ls` (found in /bin, which is in PATH)
- If /usr/local/bin is before /usr/bin in PATH, your custom version
  of a command takes precedence over the system version
- If PATH is broken (empty or missing /bin), even `ls` fails:
  "ls: command not found"

**Export = copy into child's environment:**
```bash
MY_VAR=hello                 # variable in current shell
bash                         # start child shell
echo $MY_VAR                 # empty: MY_VAR not exported
exit                         # back to parent

export MY_VAR=hello          # exported variable
bash                         # start child shell
echo $MY_VAR                 # prints: hello
MY_VAR=modified              # change in child
exit                         # back to parent
echo $MY_VAR                 # still: hello (child cannot affect parent)
```

---

### Thought Experiment

You deploy the same Java jar to dev, staging, and production. The
database URL is different in each. Three approaches:

A) Hardcode in code: `String url = "prod-db.example.com"`. Deploy
   fails in dev. You change code for dev. Now code doesn't work in prod.
   Plus the DB password is in git history forever.

B) Config file: `db.url=prod-db.example.com` in application.properties.
   Three separate config files. Must ensure the right file is on each
   server. Config with secrets can accidentally be committed to git.

C) Environment variable: `DB_URL=dev-db.example.com java -jar app.jar`.
   Same jar everywhere. Different env vars per environment. Docker:
   `-e DB_URL=...`. Kubernetes: ConfigMap/Secret -> env var. No secrets
   in code or files. This is the 12-factor app approach.

Option C is the modern standard.

---

### Mental Model / Analogy

Environment variables are like **name tags on boxes** in a delivery
system:

```
Parent process (factory) → creates boxes (child processes)
Each box inherits the factory's labels (environment variables)
  
When you update a label on a box (child process):
  - The box sees the new label
  - The factory label doesn't change
  - Other boxes still have the original label
  
Adding a new label to a box (set variable in child):
  - Only THAT box has the new label
  - Siblings don't see it
  - Factory doesn't know about it
  
export = printing the label BEFORE shipping (before forking child)
  - All future boxes get that label in their starting set
```

---

### Gradual Depth - Five Levels

**Level 1:**
env prints variables. export sets them for child processes. $PATH
determines command lookup. $HOME is your home directory. For Java
apps: set DB_URL, API_KEY, LOG_LEVEL via environment variables,
not hardcoded values.

**Level 2:**
.bashrc loads for interactive non-login shells. .bash_profile loads
for login shells. To persist a variable: add `export VAR=value` to
~/.bashrc (user) or /etc/environment (system-wide). For services:
set in systemd unit file with `Environment=VAR=value` or
`EnvironmentFile=/etc/myapp/env`.

**Level 3:**
Variable expansion: `${VAR:-default}` = use VAR if set, else "default".
`${VAR:?error}` = fail with error if VAR is unset. `${VAR/old/new}`
= string substitution. Subshell capture: `FILES=$(ls /etc)`.
Process substitution: `diff <(env | sort) <(env2 | sort)`.

**Level 4:**
Linux kernel passes environment via exec() in a string array following
the argument list in the process's memory. The environment can be
read from /proc/PID/environ (null-separated). Maximum environment
size: ARG_MAX (typically 2MB). Security: environment variables can
be read by any user via /proc if process is owned by that user; root
can read any process's environment. Secrets in env vars: visible in
`ps auxe`, in /proc/PID/environ.

**Level 5:**
Secret management at scale: environment variables for secrets are
problematic at production scale. Issues: visible in ps output, in
container inspection (`docker inspect`), in crash dumps, in logging
(if an app logs its environment). Better: Vault, AWS Secrets Manager,
Kubernetes sealed secrets. Pattern: env var contains the REFERENCE
(e.g., secret ARN), not the secret itself; app fetches secret at startup
from the vault using the reference and the app's IAM role/service account.

---

### Code Example

**BAD - hardcoded configuration:**
```bash
# BAD 1: hardcoded secrets in application code
# (application.properties)
spring.datasource.url=jdbc:postgresql://prod.db.example.com/mydb
spring.datasource.password=super_secret_password_123

# BAD 2: secret in Dockerfile (baked into image layer!)
ENV DB_PASSWORD=super_secret_password_123
# This is in every image layer - visible in docker history

# BAD 3: logging environment (exposes secrets)
printenv >> /var/log/myapp/startup.log
# Anyone with log access sees all secrets
```

**GOOD - environment-based configuration:**
```bash
# GOOD 1: Spring Boot reads env vars automatically
# (application.properties uses ${ENV_VAR:default} syntax)
spring.datasource.url=${DB_URL:jdbc:postgresql://localhost/mydb}
spring.datasource.password=${DB_PASSWORD}
# In Java:
# System.getenv("DB_URL") returns the value

# GOOD 2: Docker - inject at runtime, not build time
# Dockerfile:
FROM eclipse-temurin:17-jre
COPY app.jar /app/
CMD ["java", "-jar", "/app/app.jar"]
# No ENV with secrets in Dockerfile!

# Run with secrets injected:
docker run \
  -e DB_URL=jdbc:postgresql://prod.db.example.com/mydb \
  -e DB_PASSWORD="${DB_PASSWORD}" \  # from local env
  myapp:latest

# GOOD 3: systemd service with environment file
# /etc/systemd/system/myapp.service
[Service]
User=myapp
EnvironmentFile=/etc/myapp/myapp.env  # separate file, chmod 600
ExecStart=/opt/myapp/start.sh

# /etc/myapp/myapp.env (chmod 600, owned by root:myapp)
DB_URL=jdbc:postgresql://prod.db.example.com/mydb
DB_PASSWORD=secret   # this file is permission-protected

# GOOD 4: PATH manipulation (add custom directory first)
export PATH="/opt/myapp/bin:$PATH"
# Prepend to preserve existing PATH entries
```

---

### Startup File Loading Order

```
Interactive Login Shell (ssh login, su -, console login):
  1. /etc/profile          (system-wide)
  2. /etc/profile.d/*.sh   (system-wide additions)
  3. ~/.bash_profile       (user-specific, login-only)
  4. ~/.bashrc             (user-specific, if sourced by .bash_profile)

Interactive Non-Login Shell (new terminal in GUI, bash command):
  1. /etc/bash.bashrc      (system-wide, non-login)
  2. ~/.bashrc             (user-specific)

Non-Interactive Shell (scripts, cron, systemd):
  None of the above!
  (Only variables passed explicitly or set with EnvironmentFile)
  This is why: "variable works in terminal but not in cron"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Setting a variable makes it available everywhere" | A variable without `export` only exists in the current shell. Even with export, it only exists in that shell and its children. A different terminal has a different environment. |
| "Child processes can modify parent environment" | Child processes get a COPY of the parent's environment. Modifying a variable in a child does not affect the parent. Environment flows down (parent to child), never up. |
| "Environment variables are secure for secrets" | Env vars are visible in `ps auxe`, `/proc/PID/environ` (readable by process owner), `docker inspect`, and often in crash reports. They're better than hardcoding in source, but not suitable for high-security secrets. Use a secrets manager. |
| ".bashrc changes apply to current session immediately" | After modifying .bashrc, you must `source ~/.bashrc` or open a new terminal. The current session already has its environment loaded. |
| "$PATH order doesn't matter" | Order matters critically. The shell finds the FIRST match in PATH. If /usr/local/bin/python3 and /usr/bin/python3 both exist, whichever directory appears first in PATH determines which `python3` you get. |

---

### Failure Modes & Diagnosis

**"Command not found" after installing software:**
```bash
# Symptom: installed java but java: command not found
which java                  # shows nothing
echo $PATH                  # doesn't include /usr/lib/jvm/...

# Diagnosis: java installed but not in PATH
ls /usr/lib/jvm/            # java-17-openjdk is here

# Fix: add to PATH
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
java -version               # now works

# Make permanent: add those two lines to ~/.bashrc

# For system-wide (all users, all services):
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' \
  >> /etc/environment
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> /etc/environment
# NOTE: /etc/environment doesn't source other files, just key=value
```

**Variable works in terminal but not in cron/systemd:**
```bash
# Symptom: script works in terminal; fails in cron
# Cause: cron doesn't load .bashrc or .bash_profile

# Diagnosis: cron uses minimal environment
# Check cron's environment:
* * * * * env > /tmp/cron-env.txt
cat /tmp/cron-env.txt  # minimal: HOME, LOGNAME, SHELL, PATH

# Fix for cron: set variables explicitly in crontab
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
PATH=/usr/local/bin:/usr/bin:/bin:$JAVA_HOME/bin
0 2 * * * /opt/myapp/backup.sh

# Fix for systemd: use EnvironmentFile or Environment directive
[Service]
Environment=JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
EnvironmentFile=/etc/myapp/env
```

**Security: secrets leaking through environment:**
```bash
# Risk: secrets visible to other users
# On a multi-user system, anyone can see process env:
ps auxe | grep java  # -e flag shows environment

# Also: /proc is readable by process owner:
cat /proc/$(pgrep java)/environ | tr '\0' '\n' | grep PASSWORD

# Mitigation: don't put secrets directly in env vars
# Use secret references instead:
AWS_SECRET_ID=arn:aws:secretsmanager:us-east-1:123:secret:db-pass
# App fetches actual value at startup using AWS SDK
```

---

### Related Keywords

**Foundational:**
LNX-006 (The Linux Terminal), LNX-024 (Shell Scripting)

**Builds on this:**
LNX-070 (Shell Customization), LNX-030 (Cron Jobs),
LNX-031 (systemd Services)

**Related:**
CTR-001 (Containers), K8S-031 (ConfigMaps and Secrets)

---

### Quick Reference Card

| Variable | Meaning |
|----------|---------|
| `$PATH` | Colon-separated list of command search directories |
| `$HOME` | Current user's home directory |
| `$USER` or `$LOGNAME` | Current username |
| `$SHELL` | Path to current shell |
| `$JAVA_HOME` | Java installation directory (convention) |
| `$PWD` | Current working directory |
| `$TERM` | Terminal type |
| `$EDITOR` | Default text editor |
| `$?` | Exit code of last command |

**3 things to remember:**
1. `export` makes variables available to child processes; without it, they're shell-local
2. PATH is searched left to right; prepend your custom paths to take priority
3. .bashrc is NOT loaded by cron or systemd; set variables explicitly in those contexts

---

### Transferable Wisdom

The 12-factor app principle "Store config in the environment" is
directly derived from Unix environment variable conventions. Docker,
Kubernetes (ConfigMap as env vars), AWS Lambda (env vars), and Heroku
all implement the same pattern. Understanding Linux env vars = understanding
how ALL modern deployment systems handle configuration.

The one-way inheritance model (parent to child, never child to parent)
is a fundamental system design principle: **information flows down
the hierarchy**. This is why orchestrators (Kubernetes) inject config
into pods, not the other way around. The same principle applies to
function scope in programming languages and to tree structures in
distributed systems (Zookeeper, etcd).

---

### The Surprising Truth

When you run `export DB_PASSWORD=secret` in a bash script, every
child process spawned from that script can see the password via
`/proc/$$/environ`. On a shared Linux system, another user with
root access can see it too. But even on a single-user system, the
password appears in `ps auxe` output while the Java process runs.
Security tools like `aws-vault` and `vault agent` work around this
by: (1) storing the secret in the process's memory without environment
variables, (2) using Unix domain sockets for communication, or (3)
passing secrets via stdin rather than command-line arguments or
environment. The "secure" version of env-var configuration is one
of the most nuanced topics in production security.

---

### Mastery Checklist

- [ ] Can explain why `export` is required for child process inheritance
- [ ] Can modify PATH correctly (prepend, not replace)
- [ ] Can add persistent environment variables for a user and for a service
- [ ] Can explain why a script that works in terminal fails in cron
- [ ] Can explain the security risks of storing secrets in env vars

---

### Think About This

1. You run `export MY_VAR=hello` in your terminal, then run a Python
   script. The Python script creates a subprocess. Can the subprocess
   see `MY_VAR`? What if the Python script does `os.environ['MY_VAR'] = 'changed'`?
   Does your terminal see 'changed' after the Python script exits?

2. Kubernetes Secrets are base64-encoded but not encrypted by default
   in etcd. When you inject a Secret as an environment variable into
   a pod, the secret value appears in the container's environment.
   Who on the cluster can see this value? What does this mean for
   your threat model?

3. Your deployment pipeline sets `NODE_ENV=production` and deploys
   to production servers. A developer accidentally sets `NODE_ENV=development`
   in their local environment and pushes a change. How does environment
   variable inheritance interact with your CI/CD pipeline's environment?

**TYPE G:** Design a secrets management system for a 200-service
microservices platform. Requirements: (1) no secrets in environment
variables directly (too easy to leak), (2) no secrets in code or
config files, (3) secret rotation without service restarts, (4)
audit log of every secret access, (5) works in Kubernetes and bare
metal VMs. What architecture would you use?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between setting a variable with `VAR=value` vs `export VAR=value`?
A: Without export: the variable exists only in the current shell (bash process). Child processes spawned from that shell (commands, scripts, other programs) do NOT inherit it. With export: the variable is added to the shell's exported environment. Any child process spawned via fork()+exec() receives a copy of this variable in its environment. The export flag is a property of the variable in the current shell - it tells bash to include it when constructing the environment for child processes. Key point: changes in child processes never propagate back to the parent.

**Intermediate:**
Q: How do environment variables get from a Kubernetes Secret into a Java application's environment?
A: The flow: (1) Secret stored in etcd (Kubernetes backing store), (2) kubelet on the node fetches the Secret value from the API server, (3) kubelet sets up the pod's container environment with the secret value (either directly as env var, or mounted as a file), (4) when the container runtime (containerd/runc) starts the JVM process, it passes the environment array to exec(), (5) JVM process inherits the environment, (6) Java code reads via System.getenv("DB_PASSWORD"). Security concerns: value is plaintext in the container's /proc/PID/environ, visible in docker/crictl inspect, stored unencrypted in etcd by default (enable KMS encryption). Better pattern: reference to secret manager ARN/path in env var, fetch actual value at startup using workload identity.

**Expert:**
Q: A microservices platform has 500 services, each needing different database credentials. Explain the security risks of using environment variables for these credentials and describe a better architecture.
A: Risks: (1) env vars visible in container inspect, /proc, ps auxe; (2) secrets often logged by apps on startup; (3) rotation requires pod restart; (4) no audit trail of who accessed which secret; (5) secrets baked into Kubernetes Secret YAML in git (before base64 decoding, often stored in plaintext in repos); (6) all containers on a node can see each other's env if they have host access. Better architecture: (1) Workload Identity - each service has a Kubernetes service account bound to a cloud IAM role (AWS IRSA, GCP Workload Identity); (2) Secret Manager - secrets stored in Vault/AWS SM with IAM-gated access; (3) Sidecar/Init Container - Vault Agent sidecar fetches secret at startup, writes to in-memory tmpfs volume, Java app reads file; (4) Automatic Rotation - Vault handles rotation, new secret written to file, app watches file for changes (no restart needed); (5) Audit - every secret access logged with service identity, timestamp, IP. The env var contains only the Vault path or IAM role reference, not the actual secret.
