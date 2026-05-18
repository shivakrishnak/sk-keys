---
id: LNX-058
title: "SSH Advanced Configuration (.ssh/config, ProxyJump)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-033
used_by: LNX-063, LNX-057
related: LNX-033, LNX-057, LNX-063
tags: [ssh, .ssh/config, ProxyJump, ControlMaster, agent-forwarding, ssh-tunnel, bastion, multiplexing]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/lnx/ssh-advanced-configuration/
---

## TL;DR

`~/.ssh/config` eliminates repetitive SSH flags by defining Host stanzas
with `IdentityFile`, `User`, `Port`, `ProxyJump`. `ProxyJump` replaces
manual `-J` bastion hops (single: `ssh -J bastion target`, multi-hop:
`ssh -J bastion1,bastion2 target`). `ControlMaster auto` + `ControlPath`
multiplexes multiple sessions over one TCP connection (fast subsequent
connections). Agent forwarding (`ForwardAgent yes` / `ssh-add`) allows
using local SSH keys on remote hosts. Tunneling: `-L` (local forward),
`-R` (remote forward), `-D` (SOCKS proxy).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-058 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | ssh, .ssh/config, ProxyJump, ControlMaster, tunneling, bastion, agent-forwarding |
| **Prerequisites** | LNX-033 (SSH basics) |

---

### The Problem This Solves

**Problem 1**: Connecting to production servers requires: specific SSH key,
specific username, a bastion host, a non-standard port. Without config:
`ssh -i ~/.ssh/prod_rsa -l ec2-user -p 2222 -J ec2-user@bastion.example.com:2222 10.0.1.50`.
With `~/.ssh/config`: `ssh prod-web1`. Minutes of typing vs two words.

**Problem 2**: An Ansible deployment triggers 50 SSH connections to the same
host. Each connection: TCP handshake + TLS + key exchange = 200-500ms.
50 connections = 10-25 seconds overhead. With `ControlMaster`: first
connection opens a master, all 50 subsequent connections reuse it
via a Unix socket = milliseconds overhead.

---

### Textbook Definition

**`~/.ssh/config`**: SSH client configuration file. Defines per-host settings
using `Host` blocks with specific match patterns. Settings: `HostName`
(actual IP/hostname), `User`, `Port`, `IdentityFile`, `ProxyJump`,
`ControlMaster`, `ControlPath`, `ForwardAgent`, `ServerAliveInterval`.

**ProxyJump**: Connects through one or more intermediate "jump" hosts
before reaching the destination. Each jump host establishes a TCP
tunnel to the next. The client's TCP streams are nested (no full agent
forwarding needed). Multiple hops: comma-separated. Replaces the older
`ProxyCommand ssh -W` pattern.

**ControlMaster**: Connection multiplexing. The first SSH connection opens
a control socket at `ControlPath`. Subsequent SSH connections to the same
host reuse the existing TCP connection via that socket. Dramatically
reduces connection overhead for repeated connections (Ansible, deployment
scripts, frequent logins).

**Agent forwarding** (`ForwardAgent`): Makes the SSH agent (local key store)
available on the remote host. The remote `ssh` commands can use your local
private keys without the key being on the remote host. Security risk:
any root user on the jump host can use your forwarded agent.

---

### Understand It in 30 Seconds

```bash
# === ~/.ssh/config structure ===
cat ~/.ssh/config

# Example:
# == DEFAULTS for all hosts ==
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes

# == Bastion / jump host ==
Host bastion
    HostName bastion.example.com
    User ec2-user
    Port 22
    IdentityFile ~/.ssh/prod_rsa

# == Production servers via bastion ==
Host prod-*
    User ec2-user
    Port 22
    IdentityFile ~/.ssh/prod_rsa
    ProxyJump bastion

# == Specific production server ==
Host prod-web1
    HostName 10.0.1.50

Host prod-db1
    HostName 10.0.2.10
    User dbadmin
    IdentityFile ~/.ssh/db_rsa

# == Development server ==
Host dev
    HostName 203.0.113.100
    User developer
    Port 2222
    IdentityFile ~/.ssh/dev_rsa

# Now: connect with just:
ssh prod-web1     # uses all prod-* + prod-web1 settings
ssh dev           # uses dev settings

# === ProxyJump (bastion / jump hosts) ===
# Single hop through bastion:
ssh -J ec2-user@bastion.example.com:22 ec2-user@10.0.1.50

# Multi-hop (bastion -> dmz-host -> target):
ssh -J ec2-user@bastion.com,ec2-user@dmz-host.internal ec2-user@10.0.3.100

# Config equivalent (cleaner):
# Host target
#   ProxyJump bastion,dmz-host

# === ControlMaster (connection multiplexing) ===
Host *
    ControlMaster auto
    ControlPath ~/.ssh/ctrl-%r@%h:%p
    ControlPersist 10m
# ControlMaster auto: use existing master if available, else create one
# ControlPath: Unix socket path for the control connection
#   %r=username, %h=hostname, %p=port (makes it unique per connection target)
# ControlPersist 10m: keep master alive 10 min after last client disconnects

# Check active control connections:
ls ~/.ssh/ctrl-*     # active control sockets

# Close a specific master:
ssh -O exit dev

# === Agent Forwarding ===
# Add key to agent first:
ssh-add ~/.ssh/prod_rsa
ssh-add -l                  # list keys in agent

# Connect with forwarding:
ssh -A bastion              # -A = ForwardAgent
# Or in config:
# Host bastion
#   ForwardAgent yes

# On bastion, you can now ssh to internal hosts using your LOCAL key:
# ssh 10.0.1.50   <- uses forwarded agent (your local key)

# More secure alternative: ProxyJump (no agent needed on jump host)

# === SSH Tunnels ===
# LOCAL port forward (-L): access remote service via local port
ssh -L 5432:db.internal:5432 bastion
# Now: localhost:5432 -> bastion -> db.internal:5432 (PostgreSQL)
# Useful: access database on private network via bastion

# REMOTE port forward (-R): expose local service on remote host
ssh -R 8080:localhost:3000 dev-server
# On dev-server: port 8080 -> your local port 3000
# Useful: test webhooks (expose local webhook receiver to internet)

# DYNAMIC SOCKS proxy (-D): proxy all traffic via SSH
ssh -D 8888 bastion
# Configure browser to use SOCKS5 proxy localhost:8888
# All traffic routed through bastion (browse as if on bastion's network)

# Tunnels in background (-N = no command, -f = background):
ssh -fN -L 5432:db.internal:5432 bastion
# Persistent tunnel, no interactive shell needed
```

---

### First Principles

**~/.ssh/config resolution order:**
```
SSH resolves settings by FIRST match wins:
  1. Command-line options (highest priority)
  2. ~/.ssh/config (first matching Host block wins per setting)
  3. /etc/ssh/ssh_config (system-wide defaults)

Example config with matching order:
  Host prod-web1
      HostName 10.0.1.50
      # This matches first, sets HostName

  Host prod-*
      User ec2-user
      IdentityFile ~/.ssh/prod_rsa
      ProxyJump bastion
      # This also matches prod-web1, provides User and IdentityFile
      # (HostName already set by more specific block)

  Host *
      ServerAliveInterval 60
      # Applies to ALL hosts including prod-web1

Final effective settings for "ssh prod-web1":
  HostName         = 10.0.1.50          (from prod-web1 block)
  User             = ec2-user            (from prod-* block)
  IdentityFile     = ~/.ssh/prod_rsa     (from prod-* block)
  ProxyJump        = bastion             (from prod-* block)
  ServerAliveInterval = 60              (from * block)
```

**ProxyJump TCP nesting:**
```
Local machine -> [TCP to bastion:22] -> [TCP tunnel inside SSH] -> target

What happens:
  1. Local SSH connects to bastion.example.com:22
  2. Authenticates to bastion
  3. Opens a TCP tunnel channel through the SSH connection
     (ssh channel type: "direct-tcpip")
  4. Target SSH connection runs INSIDE this tunnel channel
  5. Target sees connection coming from bastion (not local machine)

vs. old ProxyCommand method:
  ProxyCommand ssh -W %h:%p bastion
  # Requires a shell on bastion to run the -W command
  # ProxyJump is more efficient (kernel-level tunnel, no shell)

Multi-hop:
  Local -> [TCP] -> bastion -> [tunnel] -> dmz -> [tunnel] -> target
  Each hop is a "direct-tcpip" channel inside the previous SSH connection
  Local machine handles all encryption/decryption for each hop
  No keys needed on intermediate hosts (unlike agent forwarding)
```

**ControlMaster socket mechanism:**
```
First connection "ssh prod-web1":
  1. TCP connect to 10.0.1.50:22
  2. Full SSH handshake: KEX, auth, channel open
  3. Creates Unix socket: ~/.ssh/ctrl-ec2-user@10.0.1.50:22
  4. Serves as ControlMaster (master process)
  5. Interactive session starts (or command runs)

Second connection "ssh prod-web1" (30 seconds later):
  1. Checks for existing socket: ~/.ssh/ctrl-ec2-user@10.0.1.50:22
  2. Socket exists! Connect to it (Unix domain socket, microseconds)
  3. Request new channel from master (no TCP, no SSH handshake!)
  4. Interactive session starts
  Connection time: ~5ms instead of 200ms+

Ansible runs 50 tasks on prod-web1:
  Without ControlMaster: 50 * 250ms = 12.5 seconds connection overhead
  With ControlMaster: 250ms (first) + 49 * 5ms = 0.5 seconds total
  = 25x speedup for connection overhead
```

---

### Thought Experiment

Setting up a complete multi-tier access configuration:

```bash
# Infrastructure:
# Internet -> bastion.example.com (public)
# Inside: 10.0.1.0/24 (web tier), 10.0.2.0/24 (data tier)
# Bastion: ec2-user / ~/.ssh/prod_rsa
# Web servers: webadmin / ~/.ssh/prod_rsa
# DB servers: dbadmin / ~/.ssh/db_rsa (different key!)

cat > ~/.ssh/config << 'EOF'
# == GLOBAL DEFAULTS ==
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
    ControlMaster auto
    ControlPath ~/.ssh/ctrl-%r@%h:%p
    ControlPersist 10m

# == BASTION ==
Host bastion prod-bastion
    HostName bastion.example.com
    User ec2-user
    IdentityFile ~/.ssh/prod_rsa
    # No ProxyJump: bastion is the first hop

# == WEB TIER (all 10.0.1.x) ==
Host prod-web-*
    User webadmin
    IdentityFile ~/.ssh/prod_rsa
    ProxyJump bastion

Host prod-web-1
    HostName 10.0.1.10

Host prod-web-2
    HostName 10.0.1.11

# == DB TIER (different key) ==
Host prod-db-*
    User dbadmin
    IdentityFile ~/.ssh/db_rsa
    ProxyJump bastion
    # Extra: prevent agent forwarding to DB hosts (security)
    ForwardAgent no

Host prod-db-1
    HostName 10.0.2.10

# == Tunnel aliases ==
Host tunnel-db
    HostName bastion.example.com
    User ec2-user
    IdentityFile ~/.ssh/prod_rsa
    LocalForward 5432 10.0.2.10:5432
    LocalForward 5433 10.0.2.11:5432
    # Connect two DB ports through one tunnel:
    # ssh tunnel-db  -> localhost:5432 and localhost:5433 both available

EOF
chmod 600 ~/.ssh/config

# Now usage is trivial:
ssh prod-web-1       # EC2 web server 1 via bastion, no flags needed
ssh prod-db-1        # DB server, different key, via bastion
ssh tunnel-db        # opens DB tunnels (connect with psql -h localhost -p 5432)

# Ansible inventory (uses SSH config automatically):
# [webservers]
# prod-web-1
# prod-web-2
# [databases]
# prod-db-1
# Ansible uses ~/.ssh/config for all connection settings
```

---

### Mental Model / Analogy

```
~/.ssh/config = the phone contacts book with smart groups

Without config:
  ssh -i ~/.ssh/prod_rsa -l ec2-user -p 22 -J ec2-user@bastion:22 10.0.1.50
  (like dialing the full international number every time)

With config:
  ssh prod-web1
  (like pressing "Work" in contacts, it knows the number)

Host stanzas = contact groups with inheritance:
  "prod-*" group: everyone in this group uses the bastion key, username, jump
  "prod-web1" individual: just adds the specific IP
  "Host *" fallback: applies to ALL contacts (like a default area code)

ProxyJump = a corporate building with reception:
  You tell reception: "I need to reach the server room on floor 10"
  Reception escorts you (tunnels you) past security to floor 10
  The server room sees you arriving via reception, not from street directly
  ProxyJump: your SSH tunnel goes THROUGH reception, nested inside

ControlMaster = keeping the revolving door spinning:
  First person enters: opens the door (full TCP+SSH handshake)
  Next 49 people: the door is already spinning, just walk through
  ControlPersist 10m: door keeps spinning for 10 min after last person

Agent forwarding = bringing your keyring to someone else's office:
  Your keys stay in your hands (local agent)
  The remote office can request you "open" any lock you have keys for
  BUT: the office manager (root on remote host) can borrow your keyring
  while you're there (security risk!)

ProxyJump > Agent forwarding (security principle):
  ProxyJump: your keys NEVER touch the bastion (no agent on bastion)
  Agent forwarding: your key identity IS available on bastion
  For security-sensitive environments: ProxyJump only, no ForwardAgent
```

---

### Gradual Depth - Five Levels

**Level 1:**
`~/.ssh/config` basics: `Host`, `HostName`, `User`, `Port`, `IdentityFile`.
`ProxyJump` for bastion access. `ssh -J bastion target` shorthand.
`ssh-add` to add keys to agent. `ssh-copy-id` to install public key.
ServerAliveInterval to prevent disconnects.

**Level 2:**
`ControlMaster`/`ControlPath`/`ControlPersist` for multiplexing. Local
tunnel (`-L`) for database port forwarding. Pattern matching in Host
(`prod-*`). `ssh -O` for control: `ssh -O check host` (is master up?),
`ssh -O exit host` (close master). `AddKeysToAgent yes` to auto-add keys.
`IdentitiesOnly yes` to prevent trying other keys (speeds up auth when
server limits attempts).

**Level 3:**
`DynamicForward` (SOCKS) for network browsing through SSH. `-R` remote
forwarding for webhook testing. `ssh -N -f` for background tunnels.
`LocalCommand` for pre-connect scripts. `Match` blocks (more powerful than
`Host`): match on user, hostname, OS, etc. `SSHFS` (SSH filesystem mount):
mount remote directories locally via SSH. `autossh`: auto-restart broken
SSH tunnels (useful for persistent tunnels).

**Level 4:**
SSH certificate authentication: instead of per-server `authorized_keys`,
users and hosts have certificates signed by a CA (`ssh-keygen -s ca_key
-I identity user_key.pub`). Certificates can have validity periods,
host restrictions, extensions. HashKnownHosts (security): hash hostname
in known_hosts to prevent exposing server topology. `ssh -G host` to
see effective config for a host (debug config resolution). Bastion host
hardening: `ForceCommand internal-sftp` (SFTP only), `AllowTcpForwarding no`,
`PermitTunnel no`.

**Level 5:**
OpenSSH FIDO2/hardware key support: `ssh-keygen -t ecdsa-sk` (security
key authentication with YubiKey). Certificate authorities for SSH in
cloud: AWS EC2 Instance Connect, GCP OS Login - inject keys temporarily.
SSH CA for bastion-less access: all servers trust a central CA; users get
short-lived certificates. Jump proxy pattern in Kubernetes: `kubectl exec`
is conceptually similar (proxy through API server). The entire SSH control
protocol (OpenSSH multiplexing) is documented in `~/.ssh/ctrl-*` socket
messages and can be inspected with `ssh -v`.

---

### Code Example

**BAD - manual SSH commands without config:**
```bash
# BAD: typing full SSH commands every time:
# Connecting to prod server:
ssh -i ~/.ssh/prod_key.pem -l ec2-user \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -J ec2-user@bastion.prod.example.com:2222 \
    10.0.1.50 "sudo systemctl status nginx"
# Problems: 
# 1. Key path hardcoded, easy to get wrong
# 2. StrictHostKeyChecking=no is a security risk (MITM vulnerability)
# 3. Impossible to remember, error-prone
# 4. Not reusable in scripts

# BAD: using agent forwarding for all connections:
Host *
    ForwardAgent yes
# Risk: any root on any intermediate host can use your key

# GOOD: use ProxyJump (no agent needed on jump hosts):
Host prod-*
    ProxyJump bastion
    # Bastion never sees or uses your key
    # Your keys are only used locally
```

**GOOD - complete .ssh/config with security best practices:**
```
# ~/.ssh/config - production SSH configuration

# ======= GLOBAL DEFAULTS =======
Host *
    # Connection reliability:
    ServerAliveInterval 60
    ServerAliveCountMax 3
    
    # Connection multiplexing (significant speedup):
    ControlMaster auto
    ControlPath ~/.ssh/ctrl-%r@%h:%p
    ControlPersist 10m
    
    # Key management:
    AddKeysToAgent yes
    IdentitiesOnly yes   # don't try random keys from agent

# ======= BASTION =======
Host bastion
    HostName bastion.example.com
    User ec2-user
    Port 22
    IdentityFile ~/.ssh/aws-prod.pem
    ForwardAgent no     # never forward agent to bastion

# ======= PRODUCTION (via bastion) =======
Host prod-*
    User deploy
    Port 22
    IdentityFile ~/.ssh/aws-prod.pem
    ProxyJump bastion   # bastion jump, no agent needed
    ForwardAgent no

Host prod-web-1
    HostName 10.0.1.10

Host prod-web-2
    HostName 10.0.1.11

# ======= DATABASE (different key, no forwarding) =======
Host prod-db-*
    User dbadmin
    IdentityFile ~/.ssh/aws-db.pem
    ProxyJump bastion
    ForwardAgent no

Host prod-db-1
    HostName 10.0.2.10

# ======= DATABASE TUNNEL =======
Host db-tunnel
    HostName bastion.example.com
    User ec2-user
    IdentityFile ~/.ssh/aws-prod.pem
    LocalForward 15432 10.0.2.10:5432
    # ssh db-tunnel  ->  localhost:15432 connects to prod-db-1:5432
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`ForwardAgent yes` is always needed to reach servers via a bastion" | No. `ProxyJump` (modern, since OpenSSH 7.3) tunnels the final connection THROUGH the bastion without the bastion ever having access to your key. The bastion sees only a TCP stream, not the SSH authentication. Agent forwarding is only needed if you want to RUN SSH commands FROM the bastion host to other servers (bastion as a starting point, not a transparent proxy). `ProxyJump` is the right tool for "connect THROUGH bastion to target". Agent forwarding is a security risk - avoid unless necessary. |
| "ControlMaster causes connection failures if the master dies" | With `ControlMaster auto` (not `yes`), if the master socket is gone or the master has died: SSH automatically falls back to creating a new direct connection. `auto` means "use master if available, create new connection if not". Using `ControlMaster yes` would fail if master is down - that's why `auto` is the recommended setting. Stale sockets from crashed connections: remove them with `rm ~/.ssh/ctrl-*` or `ssh -O exit host`. |
| "SSH tunnels are bidirectional by default" | Local forward (`-L local_port:dest:dest_port`) is ONE direction: you access a remote service via a local port. Remote forward (`-R remote_port:local:local_port`) is the OTHER direction: the remote host can access your local service. They are NOT bidirectional. For bidirectional access, you need both an `-L` and `-R` tunnel, or use a VPN (more appropriate for production). Dynamic forward (`-D`) creates a SOCKS proxy that can route any connection, which is effectively multi-directional. |
| "~/.ssh/config settings apply only to ssh, not to scp or sftp" | All OpenSSH client tools (ssh, scp, sftp, rsync-over-ssh, ansible, git-over-ssh, sshfs) read `~/.ssh/config`. This means: `scp prod-web1:/var/log/app.log .` works using all the prod-web1 config settings (ProxyJump, IdentityFile, User, etc.). Ansible inventory files can list hostnames from `~/.ssh/config` and all connection settings are automatically applied. Git: if your `~/.gitconfig` uses `git@github.com:...` URLs, the `github.com` Host block in `~/.ssh/config` applies to git operations. |
| "`known_hosts` checking can be safely disabled for dynamic environments" | `StrictHostKeyChecking no` disables MITM protection. In dynamic cloud environments where IPs are frequently reused, managing known_hosts is inconvenient - but the correct solution is NOT to disable host key checking. Use: `StrictHostKeyChecking accept-new` (accept new hosts, reject changed keys), or `UserKnownHostsFile /dev/null` ONLY for truly ephemeral environments where MITM is not a concern (local test VM). For cloud: use SSH certificates (host certificates signed by a CA) to get host verification without IP-based known_hosts management. |

---

### Failure Modes & Diagnosis

**ControlMaster causing stale connection issues:**
```bash
# Symptom: ssh prod-web1 hangs after network interruption
# The master TCP connection died but socket file persists

# Check for stale socket:
ls -la ~/.ssh/ctrl-deploy@10.0.1.10:22
# Socket exists but master is dead

# Check master status:
ssh -O check prod-web1
# ssh: /home/user/.ssh/ctrl-deploy@10.0.1.10:22: stale connection

# Fix: close the stale master:
ssh -O exit prod-web1
# or: remove socket manually:
rm ~/.ssh/ctrl-deploy@10.0.1.10:22

# Now reconnect normally:
ssh prod-web1   # creates new master

# Prevent: ControlPersist with timeout auto-cleans:
# ControlPersist 10m  <- master closes 10 min after last client
# Stale sockets are cleaned up automatically after this period

# Debug connection issues in detail:
ssh -vvv prod-web1 2>&1 | head -50
# Look for: "Connecting to control socket", "Entering interactive session"
# -v = verbose, -vv = more verbose, -vvv = most verbose
```

---

### Related Keywords

**Foundational:**
LNX-033 (SSH Basics)

**Builds on this:**
LNX-063 (Certificate Management), LNX-057 (Security Hardening)

**Related:**
LNX-033 (SSH), LNX-026 (Networking)

---

### Quick Reference Card

| Config | Purpose |
|--------|---------|
| `Host NAME` | Define a host alias |
| `HostName` | Actual IP/hostname |
| `User` | Login username |
| `IdentityFile` | Path to private key |
| `ProxyJump` | Jump through bastion(s) |
| `ControlMaster auto` | Connection multiplexing |
| `ControlPath ~/.ssh/ctrl-%r@%h:%p` | Socket path for multiplexing |
| `ControlPersist 10m` | Keep master alive 10 min |
| `ForwardAgent yes/no` | Agent forwarding |

**Tunneling quick reference:**

| Flag | Direction | Use Case |
|------|-----------|---------|
| `-L 5432:db:5432` | Local port -> remote service | Access DB via bastion |
| `-R 8080:localhost:3000` | Remote port -> local | Expose local to remote |
| `-D 8888` | SOCKS proxy | Route all traffic via SSH |

**3 things to remember:**
1. Use `ProxyJump` instead of `ForwardAgent` for bastion access - safer (key never touches bastion)
2. `ControlMaster auto` + `ControlPersist` dramatically speeds up repeated SSH connections (Ansible, deployments)
3. First match wins in `~/.ssh/config` - specific host blocks first, wildcards after

---

### Transferable Wisdom

SSH config patterns appear in: Ansible inventory files use `~/.ssh/config`
host definitions automatically - you can reference config aliases in inventory.
Git over SSH uses `~/.ssh/config` for GitHub/GitLab - `Host github.com`
block can specify different keys per account. Kubernetes `kubectl` has its
own `~/.kube/config` (same concept: named contexts with connection parameters).
`rsync` over SSH uses `~/.ssh/config` transparently. The ProxyJump concept
is architecturally identical to: HTTP proxy (`CONNECT` method), SOCKS proxy,
VPN gateway, Kubernetes API server as proxy to pod (kubectl exec), AWS Systems
Manager Session Manager (proxy without bastion). Connection multiplexing
appears in: HTTP/2 streams, gRPC multiplexing, database connection pools,
Unix domain sockets for IPC - all share the "single connection, multiple
logical channels" pattern.

---

### The Surprising Truth

The `ControlMaster` connection multiplexing feature was designed for one use
case: making Ansible (and similar tools) faster. Before `ControlMaster`, an
Ansible playbook with 100 tasks on one server would open 100 TCP connections,
each requiring a full SSL/TLS-like handshake. On a server behind a bastion
host (ProxyJump), this meant 200 TCP connections and 200 handshakes. With
ControlMaster, that becomes 1 TCP connection + 100 lightweight channel opens
= approximately 100x speedup for connection overhead. The deeper insight:
the SSH protocol itself was designed around this multiplexing concept - it's
called an "SSH multiplexer" in the protocol spec. SSH channels (the
"direct-tcpip", "session", "x11" channel types) are all multiplexed over
a single TCP connection. ControlMaster simply exposes this existing
multiplexing to new SSH client processes. The practical takeaway: `ControlMaster
auto` + `ControlPersist 10m` should be in every developer's `~/.ssh/config`.
The 5-minute one-time setup saves hours across a career of SSH usage. It's
one of the highest ROI configurations in the entire Linux ecosystem, yet
a majority of developers don't have it configured.

---

### Mastery Checklist

- [ ] Can write a ~/.ssh/config with Host stanzas, IdentityFile, User, ProxyJump
- [ ] Understands ProxyJump vs ForwardAgent trade-offs (security model)
- [ ] Can configure ControlMaster and diagnose stale socket issues
- [ ] Can set up local port forwarding for database access via bastion
- [ ] Can debug SSH connection issues with -vvv

---

### Think About This

1. Your CI/CD pipeline (GitHub Actions) deploys to 5 servers in a private
   VPC. Currently, each deployment step opens a new SSH connection. The
   pipeline takes 8 minutes and SSH overhead is measurable. How would you
   configure the SSH client in the CI/CD environment to reduce connection
   overhead? Consider that CI/CD is ephemeral (no persistent `~/.ssh/config`
   state between runs) and the control socket approach has limitations.

2. A developer asks why `ForwardAgent yes` is needed to SSH from the bastion
   to internal servers. You know that `ProxyJump` would be more secure.
   Explain the security difference: what does the bastion "see" in each case,
   and what attack is possible with agent forwarding that isn't possible
   with ProxyJump?

3. You need to connect to a PostgreSQL database (port 5432) on a server
   that only allows SSH access (port 22, behind a bastion). Write (a) the
   SSH command to create a persistent background tunnel, (b) the psql
   command to connect through the tunnel, (c) how to make this tunnel
   auto-restart if the connection drops.

---

### Interview Deep-Dive

**Foundational:**
Q: Explain SSH ProxyJump and when you would use it over agent forwarding.
A: ProxyJump (`-J` or `ProxyJump` in config) creates a nested tunnel: your SSH client connects to the jump host (bastion), then opens a TCP tunnel channel THROUGH that connection to the final target. Your SSH authentication to the target happens entirely within the tunnel - the jump host sees only encrypted TCP bytes, never your private key or credentials. Configuration: `ssh -J user@bastion final-target` or in `~/.ssh/config`: `Host final-target; ProxyJump bastion`. When to use: accessing servers in a private subnet through a public bastion host. Multiple hops: `ProxyJump bastion1,bastion2` creates a chain. Agent forwarding is the older approach: your SSH agent (key store) is forwarded to the jump host, so the jump host can use your keys to connect further. Problem: the jump host has access to your agent while the forwarded connection is active. Any root user on the jump host can use your forwarded agent to impersonate you on OTHER servers. Use ProxyJump when: you want transparent access through a bastion without trusting the bastion with your credentials. Use ForwardAgent only when: you actually want to run SSH commands FROM the jump host (not just through it), you trust the jump host's root users, and ProxyJump doesn't meet your needs. The security principle: ProxyJump = zero trust on bastion, your keys never leave your machine. ForwardAgent = transitive trust, bastion can act as you.

**Expert:**
Q: How would you set up SSH ControlMaster to speed up Ansible deployments, and what are the failure modes?
A: ControlMaster makes Ansible ~100x faster for SSH connection overhead. Setup in SSH config: `ControlMaster auto`, `ControlPath ~/.ssh/ctrl-%r@%h:%p`, `ControlPersist 10m`. With Ansible: Ansible uses OpenSSH as its transport by default and automatically benefits from ControlMaster. In Ansible config (`ansible.cfg`): `[ssh_connection]; ssh_args = -o ControlMaster=auto -o ControlPersist=60s`. Ansible also has its own pipelining (`pipelining = True`) that reuses SSH connections for multiple module executions without full reconnection. How it works: the first Ansible task opens an SSH connection to the host. The ControlMaster socket is created at `~/.ssh/ctrl-user@host:port`. All subsequent tasks (all 100 of them) connect via the Unix socket in milliseconds. After the playbook completes, the master stays alive for `ControlPersist` duration (10m). Failure modes: (1) Stale socket after network interruption: master TCP connection dies, socket file persists, new connections hang waiting for socket response. Fix: `ssh -O exit host` or `rm ~/.ssh/ctrl-*`. (2) Multiple concurrent Ansible runs conflict: two playbooks hit the same host simultaneously, both try to be ControlMaster. `ControlMaster auto` handles this gracefully (second one just uses the existing master). (3) Different users: socket is per `%r@%h:%p`, so root vs. deploy user get separate sockets - no conflict. (4) CI/CD environments: ephemeral containers don't have persistent `~/.ssh/config` or socket directories. Solution: pass `-o ControlMaster=auto -o ControlPath=/tmp/ctrl-%r@%h:%p -o ControlPersist=60s` in Ansible ssh_args or create a temp config file at pipeline start. Performance impact: typical Ansible playbook with 50 tasks on one host goes from 25 seconds (SSH overhead) to < 1 second overhead.
