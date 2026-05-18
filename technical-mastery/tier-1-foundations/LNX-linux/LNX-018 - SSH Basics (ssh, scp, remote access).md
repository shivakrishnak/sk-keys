---
id: LNX-018
title: "SSH Basics (ssh, scp, remote access)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-011
used_by: LNX-041, LNX-058
related: LNX-041, LNX-058, NET-001
tags: [ssh, scp, remote-access, secure-shell, keys, port-forwarding, tunneling]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/lnx/ssh-basics/
---

## TL;DR

SSH (Secure Shell) provides encrypted remote terminal access to
Linux servers. `ssh user@host` connects interactively. `scp
file user@host:path` copies files. `ssh-keygen` generates key
pairs; public key goes on server (~/.ssh/authorized_keys), private
key stays local. Key-based auth is more secure than passwords
and is required for automation. Port 22 is the default; always
restrict SSH access in production firewalls.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-018 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | SSH, scp, remote access, key authentication, port forwarding |
| **Prerequisites** | LNX-011 |

---

### The Problem This Solves

Pre-SSH: Telnet and rsh sent everything in plaintext - credentials,
commands, and data visible to anyone on the network. SSH (1995)
replaced them with encrypted, authenticated remote access. Today:
the only secure way to administrate remote Linux servers, transfer
files, and tunnel network connections. Required for every cloud
server, every CI/CD pipeline connecting to servers, and every
developer connecting to dev/staging environments.

---

### Textbook Definition

**SSH (Secure Shell)** is a cryptographic network protocol that
provides: (1) encrypted communication channel (AES, ChaCha20),
(2) server authentication (verifies you're connecting to the right
server, prevents MITM), (3) client authentication (password or
public-key), (4) multiple sub-protocols: interactive shell,
file transfer (SCP/SFTP), port forwarding.

Components:
- **SSH client**: `ssh` command (connects to server)
- **SSH server**: `sshd` daemon (listens on port 22)
- **Key pair**: private key (client, secret) + public key (server)

---

### Understand It in 30 Seconds

```bash
# Connect to a server:
ssh alice@192.168.1.100          # by IP
ssh alice@server.example.com    # by hostname
ssh -p 2222 alice@host          # non-standard port

# Generate SSH key pair:
ssh-keygen -t ed25519 -C "alice@example.com"
# Creates: ~/.ssh/id_ed25519 (private) + ~/.ssh/id_ed25519.pub (public)

# Copy public key to server (enables key-based login):
ssh-copy-id alice@server.example.com
# OR manually: append public key to server's ~/.ssh/authorized_keys

# Copy files:
scp localfile.txt alice@server:/home/alice/    # upload
scp alice@server:/home/alice/file.txt ./       # download
scp -r localdir/ alice@server:/home/alice/     # upload directory

# Run single command without interactive shell:
ssh alice@server "df -h"
ssh alice@server "systemctl status nginx"

# Port forwarding (tunnel):
ssh -L 8080:localhost:80 alice@server  # local:8080 -> server:80
ssh -N -L 5432:db.internal:5432 alice@jumphost  # database tunnel
```

---

### First Principles

**Asymmetric cryptography for authentication:**
SSH key pairs use public-key cryptography (Ed25519 or RSA). The
private key stays on your local machine - NEVER shared. The public
key goes on the server. Authentication:
1. Server sends a random challenge
2. Client signs the challenge with private key
3. Server verifies the signature using the stored public key
4. If valid: authenticated (no password required)

Private key: never leaves your machine. Even if an attacker sees
your network traffic, they can't authenticate without the private key.

**Host key verification (prevents MITM):**
First connection: "The authenticity of host X cannot be established.
Are you sure you want to continue connecting?" - server's public
host key is unknown. After accepting: key stored in `~/.ssh/known_hosts`.
Subsequent connections: if server's key changes (potential MITM or
server rebuild), SSH warns: "WARNING: REMOTE HOST IDENTIFICATION
HAS CHANGED!" - do NOT proceed without verifying.

---

### Thought Experiment

You're deploying a Java application to a production server via CI/CD.
The pipeline needs to: copy the new jar, stop the old service, start the new one.

Without SSH keys (password auth):
- How does CI/CD know the password? Store in CI config (security risk).
- Password rotation requires updating CI config.
- No way to limit which commands CI can run.

With SSH keys:
- Generate a dedicated CI/CD key pair
- Add public key to server's authorized_keys
- Private key stored in CI secrets (encrypted, audited)
- Restrict: `command="/opt/deploy/deploy.sh" ssh-ed25519 AAAA...`
  (forced command - CI can ONLY run that specific deploy script)
- Revoke: remove public key from authorized_keys (instantly revokes access)

Key-based SSH is not just more secure - it enables automation,
fine-grained access control, and easy revocation.

---

### Mental Model / Analogy

SSH is like a **secured building with key card access:**

```
Building = remote server
Front desk guard (sshd) = SSH daemon on port 22

Regular door (password auth):
  Guard checks if your password matches the server's records
  Problem: someone can watch you enter the code (eavesdrop)
  Problem: guard needs to know your password (shared secret)
  
Key card system (key-based auth):
  Your card (private key): only you have it, never shown to guard
  Card reader data (public key): installed at the door
  Authentication: card reader verifies your card is valid
    without you ever handing over the card
  
Host keys = the building's unique ID badge on the door
  First visit: you record the building's ID
  Later visits: if ID changed (different building?), alarms!
  
Port forwarding = asking the guard to run a telephone wire
  from inside the building to your desk:
  Secure connection from your laptop to an internal server
  via the SSH tunnel through the perimeter
```

---

### Gradual Depth - Five Levels

**Level 1:**
`ssh user@host` connects. `scp` copies files. `ssh-keygen -t ed25519`
generates keys. `ssh-copy-id user@host` installs your public key.
Key-based auth is more secure than password. Never share your
private key (~/.ssh/id_ed25519).

**Level 2:**
`~/.ssh/config` file simplifies connections:
```
Host production
    HostName prod.example.com
    User deploy
    IdentityFile ~/.ssh/deploy_key
    Port 2222
```
Then: `ssh production` instead of `ssh -p 2222 -i ~/.ssh/deploy_key deploy@prod.example.com`.
Port forwarding: `-L local:host:remote` (local forward), `-R remote:host:local` (reverse), `-D port` (SOCKS proxy).

**Level 3:**
SSH agent: `ssh-add ~/.ssh/id_ed25519` loads key into agent.
Subsequent SSH connections use the agent (no passphrase prompts).
`ssh-add -l` lists loaded keys. `SSH_AUTH_SOCK` env var points to
agent socket. Agent forwarding (`-A` flag): allows remote server to
use your LOCAL agent's keys (for git pull from remote server using
your local GitHub key). CAUTION: agent forwarding allows root on
remote server to use your keys - only forward to trusted hosts.

**Level 4:**
`ssh -J jumphost target` - jump host (bastion) connections without
multiple SSH hops. `ProxyJump` in .ssh/config. rsync for efficient
file sync: `rsync -avz --progress local/ user@host:remote/` (only
transfers changed bytes, much faster than scp for large directories).
Multiplexing: `ControlMaster auto` + `ControlPath` in .ssh/config -
multiple SSH sessions share one TCP connection (faster for scripts
that make many short connections).

**Level 5:**
Certificate-based SSH: instead of managing authorized_keys on every
server, use SSH CAs. CA signs user's key; servers trust the CA.
User credentials: short-lived certificates (1-24 hours). No per-server
key installation. Central revocation. HashiCorp Vault SSH Secrets
Engine: issues on-demand, short-lived SSH certificates. No standing
access - access is just-in-time. This is the enterprise production
pattern for SSH access at scale.

---

### Code Example

**BAD - SSH security anti-patterns:**
```bash
# BAD 1: password authentication enabled (brute-force risk)
# /etc/ssh/sshd_config:
PasswordAuthentication yes   # should be: no

# BAD 2: root login allowed
PermitRootLogin yes          # should be: no (or prohibit-password)

# BAD 3: private key with world-readable permissions
chmod 644 ~/.ssh/id_ed25519  # SSH refuses to use it AND it's exposed!
# Required:
chmod 600 ~/.ssh/id_ed25519

# BAD 4: agent forwarding to untrusted hosts
ssh -A untrusted-server   # root on untrusted-server can use YOUR keys!

# BAD 5: no passphrase on private key
ssh-keygen -t ed25519     # hit enter for no passphrase
# If laptop stolen, key is immediately usable
# Use a strong passphrase + ssh-agent to avoid repeated prompts

# BAD 6: trusting all host keys automatically
# StrictHostKeyChecking no in config
# Disables MITM protection - never do this in production
```

**GOOD - secure SSH configuration and usage:**
```bash
# GOOD 1: generate strong key with passphrase
ssh-keygen -t ed25519 -C "alice@company.com"
# Passphrase: use a memorable but strong passphrase
# Add to agent for the day:
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519   # enter passphrase once

# GOOD 2: secure sshd configuration
# /etc/ssh/sshd_config (on server):
Port 22
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
MaxAuthTries 3
LoginGraceTime 30s
AllowUsers alice bob deploy
# Apply: systemctl restart sshd

# GOOD 3: ~/.ssh/config for multiple servers
Host dev
    HostName dev.example.com
    User alice
    IdentityFile ~/.ssh/id_ed25519
    ForwardAgent no   # explicit: no agent forwarding

Host bastion
    HostName bastion.prod.example.com
    User alice
    IdentityFile ~/.ssh/deploy_key

Host prod-web-*
    User deploy
    IdentityFile ~/.ssh/deploy_key
    ProxyJump bastion   # go through bastion host
    
# Usage:
ssh prod-web-1   # goes through bastion automatically

# GOOD 4: CI/CD deployment key (restricted)
# Generate deployment key pair:
ssh-keygen -t ed25519 -C "ci-deploy" -f ~/.ssh/ci_deploy_key

# On server, in authorized_keys - restrict what CI can do:
command="/opt/deploy/deploy.sh",no-port-forwarding,\
no-X11-forwarding,no-agent-forwarding \
ssh-ed25519 AAAA... ci-deploy

# Now: ssh with this key ONLY runs deploy.sh, nothing else

# GOOD 5: rsync for large file sync (faster than scp)
rsync -avz --progress \
    --exclude='.git/' \
    --exclude='*.log' \
    ./app/ deploy@prod:/opt/myapp/
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "SSH tunnels data unencrypted if you forward a port" | SSH port forwarding encrypts ALL traffic through the SSH tunnel, even if the forwarded protocol (like HTTP) is unencrypted. `ssh -L 8080:internal-http-server:80` - your browser connects to localhost:8080, traffic is encrypted over SSH to the server, then goes unencrypted to the internal server. The internet-facing leg is always encrypted. |
| "Disabling password auth breaks sudo/su" | Disabling SSH password auth only affects the SSH LOGIN mechanism. sudo and su on the server itself still work using PAM (local authentication). Disabling SSH passwords does not affect local server authentication. |
| "The public key is what you keep secret" | The PRIVATE key is secret. The public key can (and should) be distributed freely - it's designed to be shared. Your public key goes on every server you want to access, in GitHub, etc. The private key stays on your local machine. |
| "scp is always safe for large transfers" | scp uses an older protocol and has been deprecated in favor of rsync or sftp. For large files: rsync (resumes interrupted transfers, only sends changed bytes). For interactive file browsing: sftp. |
| "Known_hosts warnings mean you should reconnect" | "REMOTE HOST IDENTIFICATION HAS CHANGED" is a serious security warning. It means either: (a) server was rebuilt (legitimate), or (b) MITM attack. ALWAYS verify before proceeding. Contact the server admin via a different channel to confirm. |

---

### Failure Modes & Diagnosis

**Permission denied (publickey):**
```bash
# Error: Permission denied (publickey)
# Step 1: verify key is loaded in agent
ssh-add -l           # lists loaded keys
# If empty: ssh-add ~/.ssh/id_ed25519

# Step 2: verify public key is on the server
ssh-copy-id user@server   # installs it if password still works
# OR manually check: cat ~/.ssh/id_ed25519.pub
# Verify it appears in server's: cat ~/.ssh/authorized_keys

# Step 3: check permissions on server
# SSH is strict: wrong permissions = key auth disabled!
# Required:
chmod 700 ~/.ssh/                   # (on server)
chmod 600 ~/.ssh/authorized_keys    # (on server)

# Step 4: debug with verbose output
ssh -vvv user@server   # shows exactly why auth is failing
# Look for: "Offering public key" then "Authentications that can continue"
```

**Known hosts warning (server key changed):**
```bash
# Error: WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
# BEFORE proceeding: verify with server admin via separate channel

# If server was legitimately rebuilt:
ssh-keygen -R server.example.com   # remove old key from known_hosts
# Then reconnect - you'll be asked to accept the new key

# Check what key is expected:
ssh-keyscan server.example.com     # shows server's current host key
# Compare with what you have:
ssh-keygen -F server.example.com   # shows stored key
```

**Security: SSH brute force attacks:**
```bash
# View failed SSH attempts:
grep "Failed password" /var/log/auth.log | tail -20
# Or:
journalctl -u sshd | grep "Invalid user" | tail -20

# Protection checklist:
# 1. Disable password auth (PasswordAuthentication no)
# 2. Change port (Port 2222 - reduces script-kiddie noise)
# 3. Install fail2ban (bans IPs after N failed attempts)
# 4. Use firewall to allow SSH only from known IPs
iptables -A INPUT -p tcp --dport 22 -s trusted-ip -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
```

---

### Related Keywords

**Foundational:**
LNX-011 (Users and Groups), LNX-010 (File Permissions)

**Builds on this:**
LNX-041 (SSH Keys and Public Key Auth - advanced),
LNX-058 (SSH Advanced Configuration)

**Related:**
NET-001 (Networking), SEC-001 (Security), CRY-001 (Cryptography)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ssh user@host` | Connect to remote server |
| `ssh -p 2222 user@host` | Connect on non-standard port |
| `ssh-keygen -t ed25519` | Generate Ed25519 key pair |
| `ssh-copy-id user@host` | Install public key on server |
| `ssh-add ~/.ssh/id_ed25519` | Load key into SSH agent |
| `ssh-add -l` | List keys in agent |
| `scp file user@host:path` | Upload file |
| `scp user@host:file ./` | Download file |
| `scp -r dir/ user@host:path` | Upload directory |
| `ssh -L local:host:remote user@server` | Local port forward |
| `ssh -J jump target` | Connect via jump host |

**3 things to remember:**
1. Private key stays local (chmod 600), public key goes on server (authorized_keys)
2. `ssh-keygen -t ed25519` - Ed25519 is the modern recommended algorithm
3. Disable PasswordAuthentication in sshd_config when using keys - otherwise brute force is still possible

---

### Transferable Wisdom

SSH key authentication is the model for all **challenge-response
authentication**: GitLab/GitHub SSH keys (push/pull without password),
AWS EC2 key pairs (instance launch), GCP OS Login, TLS client
certificates. The private key = identity credential; public key =
access grant. The same public-key infrastructure concept (asymmetric
crypto for identity) underlies TLS/HTTPS, JWT signing, and code signing.

**Port forwarding** is the primitive behind: VPN tunnels (OpenVPN
uses the same tunnel concept over TLS), Kubernetes port-forward
(`kubectl port-forward`), ngrok (exposes local ports via reverse
tunnel). The mental model is identical: establish a secure tunnel,
traffic flows through it transparently.

---

### The Surprising Truth

Ed25519 (the modern SSH key algorithm) generates a 32-byte private
key and a 32-byte public key - far smaller than RSA-2048 (256 bytes
key, 512+ bytes PKCS format). Yet Ed25519 provides equivalent security
to RSA-3072 or RSA-4096. The reason: Ed25519 uses elliptic curve
cryptography over Curve25519, which operates in a mathematical space
where 256-bit keys are already computationally infeasible to break with
known algorithms - including quantum computers (though not indefinitely
future-proof). RSA-2048 is considered borderline insecure against
future threats. The practical takeaway: `ssh-keygen -t ed25519` is
faster to generate, creates smaller keys, is faster to compute, and is
MORE secure than `ssh-keygen -t rsa -b 2048`. Yet many systems default
to RSA for compatibility with older SSH implementations.

---

### Mastery Checklist

- [ ] Can generate an Ed25519 key pair and install the public key
- [ ] Can configure ~/.ssh/config for multiple servers
- [ ] Can set up and use SSH agent to avoid repeated passphrase entry
- [ ] Can diagnose "Permission denied (publickey)" errors
- [ ] Can explain the security difference between password and key-based auth

---

### Think About This

1. You generate an SSH key pair with `ssh-keygen`. The private key
   has a passphrase. You add it to ssh-agent. Now you can ssh without
   entering the passphrase. If someone compromises your running system
   and reads `/proc/$SSH_AGENT_PID/mem`, can they extract your private
   key? What does this mean for your threat model with ssh-agent?

2. A junior engineer suggests: "Let's disable SSH completely on production
   servers and use AWS Systems Manager Session Manager instead." What
   are the security advantages of this approach? What operational
   challenges does it introduce?

3. You need to allow a CI/CD system to deploy to production servers.
   The traditional approach: SSH key pair, public key in authorized_keys.
   The modern approach: short-lived SSH certificates via HashiCorp Vault.
   What specific security properties does the certificate approach provide
   that the key pair approach does not?

**TYPE G:** Design a zero-trust SSH access system for 500 production
servers where: (1) no standing SSH access for any engineer, (2) access
requires approval from a second engineer, (3) every command run via
SSH is recorded and searchable, (4) access automatically expires after
4 hours, (5) works for both human engineers and CI/CD automation.
What components does this system require?

---

### Interview Deep-Dive

**Foundational:**
Q: How does SSH key authentication work and why is it more secure than password authentication?
A: SSH key authentication uses asymmetric cryptography. The process: (1) You generate a key pair: private key (stays on your machine, chmod 600) and public key (placed on server in ~/.ssh/authorized_keys). (2) When you connect, the server sends a random challenge. (3) Your SSH client signs the challenge using the private key. (4) Server verifies the signature using the stored public key. If valid: authenticated. Why more secure than passwords: (1) The private key is never transmitted over the network (unlike passwords). (2) Public key is not secret - it can be on many servers without risk. (3) Immune to phishing (the server verifies mathematical proof, not a string you type). (4) Immune to replay attacks (challenge is random each time). (5) No brute force possible (key is too long). (6) Enables automation without storing passwords in plaintext.

**Intermediate:**
Q: Your CI/CD pipeline needs SSH access to deploy to production. How do you securely configure this?
A: (1) Generate a dedicated key pair for CI: `ssh-keygen -t ed25519 -C "ci-deploy" -f ci_deploy_key` - no passphrase (CI can't enter one). (2) Add public key to server's authorized_keys with restrictions: `command="/opt/deploy/deploy.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAA... ci-deploy`. The `command=` prefix means this key can ONLY run that specific script, nothing else. (3) Store private key in CI secrets management (GitHub Secrets, GitLab CI Variables, Jenkins Credentials) - encrypted at rest, not visible in logs. (4) Use a separate key per environment (dev, staging, prod) so a prod key compromise doesn't affect other environments. (5) Rotate keys periodically (quarterly). (6) Audit: review authorized_keys on production servers monthly. (7) Consider alternatives: short-lived certificates from Vault SSH Secrets Engine eliminate the need for key rotation.

**Expert:**
Q: Explain SSH certificate-based authentication and why large organizations prefer it over traditional key-based authentication.
A: Traditional key-based auth problem at scale: each authorized_keys file must list every approved public key. Adding/removing access means updating authorized_keys on every server. For 500 servers x 50 engineers = 25,000 key entries to manage. Certificate-based auth: (1) A Certificate Authority (CA) signs user's public keys, creating a certificate with metadata (valid principals, expiry time, extensions). (2) Servers are configured to trust the CA's public key (one line in sshd_config). (3) When connecting, user presents the certificate. Server verifies signature from trusted CA and checks expiry. (4) Access is granted based on the certificate's principals matching the server's AllowedUserCertPrincipals. Advantages: (1) No per-server authorized_keys management. (2) Certificates can have short TTL (1-24 hours) - no standing access, no need to revoke individual keys. (3) Centralized issuance audit trail. (4) Rich metadata: can embed audit info in certificate. Implementation: HashiCorp Vault SSH Secrets Engine - engineers authenticate to Vault (via OIDC/LDAP), Vault issues short-lived SSH cert, engineer connects to server with the cert. The cert expires; no cleanup needed. This is the modern enterprise pattern for SSH access governance.
