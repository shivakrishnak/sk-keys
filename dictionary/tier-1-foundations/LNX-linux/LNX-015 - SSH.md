---
version: 2
layout: default
title: "SSH"
parent: "Linux"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /linux/ssh/
id: LNX-015
category: Linux
difficulty: ★☆☆
depends_on: Networking, Linux File System Hierarchy, Users and Groups
used_by: CI/CD, Shell Scripting, SCP / rsync, Git & Branching Strategy
related: SCP / rsync, VPN, TLS/SSL
tags:
  - linux
  - networking
  - security
  - foundational
---

# LNX-015 - SSH

⚡ TL;DR - SSH is an encrypted protocol for secure remote shell access and file transfer over an untrusted network, replacing plaintext tools like Telnet and rsh.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In the early 1990s, sysadmins used `telnet` and `rsh` to access remote servers. These protocols sent every keystroke - including usernames, passwords, and commands - as plaintext over the network. Anyone on the same network segment with a packet sniffer could capture credentials in seconds.

**THE BREAKING POINT:**
In 1994, a packet sniffer was discovered on a university network that had silently captured over 100,000 passwords from telnet sessions in a single month. Sysadmins had no way to know their credentials were already compromised. A single compromised router anywhere between client and server exposed everything.

**THE INVENTION MOMENT:**
This is exactly why SSH (Secure Shell) was created. Tatu Ylönen released SSH-1 in 1995 after his university network was compromised. It encrypts the entire session - credentials, commands, output - making network eavesdropping useless.

---

### 📘 Textbook Definition

SSH (Secure Shell) is a cryptographic network protocol defined in RFC 4251–4254 that provides secure remote login, command execution, and data transfer over an untrusted network. It uses a client-server model where the server runs `sshd` on port 22. Authentication is via password or public-key cryptography. The protocol negotiates a session key using Diffie-Hellman key exchange and encrypts all subsequent traffic with a symmetric cipher (AES by default). SSH-2 is the current standard; SSH-1 is deprecated due to design flaws.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SSH gives you a secure encrypted terminal on a remote machine over any network.

**One analogy:**

> SSH is like a sealed armoured tube connecting your keyboard to a remote computer. Even if someone physically intercepts the tube, they see only scrambled noise. To open the connection you can use a password (something you know) or a key pair (something you have) - like a padlock and key that only you own.

**One insight:**
The most powerful feature of SSH is not just encryption - it's public-key authentication. Your private key never leaves your machine. The server stores only a public key fingerprint. Even if the server is fully compromised, the attacker cannot recover your private key.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Both parties must agree on a shared secret for encryption without ever transmitting that secret.
2. The server must prove its identity before the client sends credentials (prevents MITM).
3. The client must authenticate before gaining access.

**DERIVED DESIGN:**
**Shared secret without transmission:** SSH uses Diffie-Hellman key exchange. Both sides exchange public values; an observer learns the public values but cannot compute the shared secret without solving the discrete logarithm problem.

**Server identity proof:** On first connection the client sees the server's host key fingerprint and stores it in `~/.ssh/known_hosts`. On every subsequent connection the server presents the same key; any mismatch (possible MITM) triggers a warning.

**Client authentication - two mechanisms:**

1. Password auth: password is sent encrypted over the established channel.
2. Public-key auth: the server sends a challenge encrypted with the client's registered public key. Only the client (with the private key) can decrypt and respond - the private key is never transmitted.

**THE TRADE-OFFS:**
**Gain:** Strong encryption, no credential transmission (key-based auth), tunnelling capabilities.
**Cost:** Key management complexity (rotating, distributing, revoking keys at scale), SSH key sprawl in large organisations.

---

### 🧪 Thought Experiment

**SETUP:**
You SSH from your laptop to a production server across the internet. Your ISP, the backbone routers, and the server's datacenter can all observe packets in transit.

**WHAT HAPPENS WITHOUT SSH (with Telnet):**
Every packet contains plaintext ASCII. An observer captures: `login: admin`, `password: mysecretpass`, `sudo systemctl restart nginx`. In 10 minutes they have credentials and full knowledge of what you did on the server. They can replay those credentials immediately.

**WHAT HAPPENS WITH SSH:**
The observer sees: encrypted bytes. The handshake reveals which cipher suite was negotiated - but not the session key. Commands and responses are indistinguishable from random noise. Even if they capture the entire session and store it, they cannot decrypt it without the session key, which was never transmitted.

**THE INSIGHT:**
Encryption transforms the problem of "secure channel" into "key management" - a far more tractable problem. The hard part moves from "prevent all eavesdropping" (impossible on a shared internet) to "protect your private key file" (manageable with file permissions and a passphrase).

---

### 🧠 Mental Model / Analogy

> SSH is like a bank vault door with a combination known only to you and the bank. Before you enter, the bank proves it's the real bank by showing you a seal you've verified before. You prove your identity with a unique physical key (private key) that you've never handed to anyone - the bank only has a mold of the lock (public key). Traffic through the vault door is invisible to anyone outside.

- "Bank's seal you've verified before" → server host key in `known_hosts`
- "Your unique physical key" → SSH private key (`~/.ssh/id_rsa`)
- "Mold of the lock at the bank" → `~/.ssh/authorized_keys` on server
- "Vault door" → encrypted SSH channel
- "Combination vault opens" → Diffie-Hellman session key negotiation

Where this analogy breaks down: a physical key can be copied if stolen; an SSH private key protected by a passphrase requires the passphrase to use, so a stolen key file is useless without the passphrase.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
SSH lets you control a computer that is far away as if you were sitting in front of it - but all communication is scrambled so no one else can spy on what you type or see.

**Level 2 - How to use it (junior developer):**
`ssh user@hostname` opens a remote terminal. Generate a key pair with `ssh-keygen -t ed25519`. Copy your public key to the server with `ssh-copy-id user@hostname`. After that, you log in without a password. Use `~/.ssh/config` to store hostnames and usernames so you can just type `ssh myserver`.

**Level 3 - How it works (mid-level engineer):**
SSH negotiates in three phases: (1) version and algorithm negotiation, (2) key exchange (Diffie-Hellman) to establish a shared symmetric key, (3) user authentication. For key-based auth, the server sends a random challenge signed by the client's private key - proving possession without transmitting the key. Port forwarding (`-L local:remote`, `-R remote:local`) tunnels arbitrary TCP through the encrypted SSH channel, enabling access to services behind firewalls.

**Level 4 - Why it was designed this way (senior/staff):**
SSH-2 (RFC 4251) was redesigned from SSH-1 to fix a critical flaw: SSH-1 used a single session key vulnerable to a length-extension attack. SSH-2 uses separate encryption and MAC keys derived from the DH exchange. The protocol is layered: Transport Layer (encryption), User Auth Layer, Connection Layer (multiplexed channels). This layering is why SSH supports tunnelling, X11 forwarding, and agent forwarding as independent features built on the same transport.

---

### ⚙️ How It Works (Mechanism)

**SSH handshake sequence:**

```
┌─────────────────────────────────────────────┐
│  SSH HANDSHAKE FLOW                         │
└─────────────────────────────────────────────┘

Client                    Server (sshd on :22)
  │                              │
  │── TCP SYN ─────────────────▶│
  │◀─ TCP SYN-ACK ──────────────│
  │── TCP ACK ─────────────────▶│
  │                              │
  │── "SSH-2.0-OpenSSH_8.9" ──▶│
  │◀─ "SSH-2.0-OpenSSH_8.9" ───│ version exchange
  │                              │
  │── Client KEX init ─────────▶│
  │◀─ Server KEX init + host key│ DH key exchange
  │── DH client value ─────────▶│
  │◀─ DH server value + sig ────│ session key established
  │                              │
  │── Auth request ────────────▶│
  │◀─ Auth challenge ───────────│ pubkey: sign challenge
  │── Signed response ─────────▶│
  │◀─ Auth success ─────────────│
  │                              │
  │◀══ encrypted channel ═══════│ shell/commands
```

**Key files:**

```
~/.ssh/id_ed25519        # private key (keep secret)
~/.ssh/id_ed25519.pub    # public key (share freely)
~/.ssh/known_hosts       # server host keys you trust
~/.ssh/authorized_keys   # (on server) allowed client pubkeys
~/.ssh/config            # client connection configuration
/etc/ssh/sshd_config     # server configuration
```

**Common operations:**

```bash
# Generate key (ed25519 is preferred over RSA in 2024)
ssh-keygen -t ed25519 -C "user@host"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server

# Connect
ssh user@server.example.com

# Connect with specific key
ssh -i ~/.ssh/deploy_key user@server

# Local port forwarding (access server's DB locally)
# Forwards localhost:5433 to db:5432 via jump host
ssh -L 5433:db.internal:5432 user@jumphost

# Remote port forwarding (expose local port on server)
ssh -R 8080:localhost:3000 user@server

# Run a single command
ssh user@server 'df -h'

# Verbose mode for debugging
ssh -vvv user@server
```

**`~/.ssh/config` example:**

```
Host prod
    HostName prod.example.com
    User deploy
    IdentityFile ~/.ssh/id_prod
    Port 22

Host dev
    HostName 192.168.1.100
    User ubuntu
    IdentityFile ~/.ssh/id_dev
    ForwardAgent yes
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  SSH SESSION LIFECYCLE                      │
└─────────────────────────────────────────────┘

 Developer: ssh user@server.example.com
       │
       ▼
 TCP connect to :22
       │
       ▼
 Version + cipher negotiation
       │
       ▼
 DH key exchange → shared session key
       │
       ▼
 Server host key verification (known_hosts)
       │  ← YOU ARE HERE
       ▼
 Client authentication (password or pubkey)
       │
       ▼
 Encrypted shell session opened
       │
       ▼
 Commands executed, output returned encrypted
       │
       ▼
 Session closed: keys discarded (forward secrecy)
```

**FAILURE PATH:**
Host key mismatch → "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!" → connection aborted. This protects against MITM. Must be resolved by verifying the server's new fingerprint out-of-band.

**WHAT CHANGES AT SCALE:**
At scale, per-user SSH key management becomes a security and operational nightmare - thousands of `authorized_keys` entries with no expiry. Modern approaches use short-lived certificates (HashiCorp Vault SSH CA) that expire automatically, and bastion hosts / jump servers to centralise access auditing.

---

### 💻 Code Example

**Example 1 - BAD: weak key, password auth enabled:**

```bash
# BAD - RSA-1024 is broken; no passphrase on key
ssh-keygen -t rsa -b 1024 -N ""
```

```
# /etc/ssh/sshd_config - BAD
PermitRootLogin yes
PasswordAuthentication yes
```

**Example 1 - GOOD: strong key, hardened server config:**

```bash
# GOOD - ed25519 with passphrase
ssh-keygen -t ed25519 -C "user@hostname" \
  -f ~/.ssh/id_ed25519
# Enter passphrase when prompted
```

```
# /etc/ssh/sshd_config - GOOD
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
MaxAuthTries 3
ClientAliveInterval 300
AllowUsers deploy ubuntu
```

**Example 2 - SSH agent (avoid re-entering passphrase):**

```bash
# Start ssh-agent (usually done in .bashrc)
eval "$(ssh-agent -s)"

# Add key (asks passphrase once)
ssh-add ~/.ssh/id_ed25519

# List loaded keys
ssh-add -l

# Forward agent to server (use with trusted servers only)
ssh -A user@jumphost
ssh user@internal-server  # uses forwarded agent
```

**Example 3 - SSH tunnelling for database access:**

```bash
# Access production postgres securely from laptop
# without opening DB port to internet
ssh -N -L 5433:localhost:5432 user@prod-server &
# Now connect your DB tool to localhost:5433
psql -h localhost -p 5433 -U myuser mydb
```

---

### ⚖️ Comparison Table

| Auth Method            | Security  | Usability         | Best For                  |
| ---------------------- | --------- | ----------------- | ------------------------- |
| **Public Key**         | Very High | High (with agent) | Automation, developers    |
| Password               | Medium    | Medium            | Quick one-off access      |
| SSH Certificates       | Very High | High at scale     | Enterprise, many servers  |
| Kerberos/GSSAPI        | High      | Complex setup     | Corporate AD environments |
| Hardware key (YubiKey) | Highest   | Medium            | High-security access      |

How to choose: always prefer public-key auth; use SSH certificates when managing more than 10 servers; add hardware keys for privileged access to production.

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                         |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| SSH encrypts only the password                                    | SSH encrypts the entire session including all commands, outputs, and file transfers                                             |
| Changing SSH port from 22 to another improves security            | Obscurity is not security; port scanners find it in seconds. Proper key-based auth + firewall rules matter                      |
| Sharing a private key between machines is fine                    | Each machine should have its own private key; sharing private keys violates the core security model                             |
| ForwardAgent is safe on any server                                | Agent forwarding allows any root user on the server to use your agent to authenticate as you; only use on fully trusted servers |
| `authorized_keys` on the server is where you put your private key | `authorized_keys` holds PUBLIC keys of clients permitted to connect; the private key NEVER leaves your machine                  |

---

### 🚨 Failure Modes & Diagnosis

**Host Key Changed (MITM Warning)**

**Symptom:**
`WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` - connection fails.

**Root Cause:**
Server was rebuilt (legitimate) or a MITM attack is intercepting the connection (security incident). Both look identical to the client.

**Diagnostic Command:**

```bash
# Verify fingerprint out-of-band (e.g., AWS console)
ssh-keyscan -H server.example.com 2>/dev/null | \
  ssh-keygen -lf -

# If server was legitimately rebuilt, remove old key
ssh-keygen -R server.example.com
```

**Fix:**
Only remove the old key from `known_hosts` after verifying the new fingerprint through a trusted channel (cloud console, phone call to admin).

**Prevention:**
Use SSH certificates or a bastion host with a managed `known_hosts` file updated by configuration management.

---

**Permission Too Open on Key File**

**Symptom:**
`Permissions 0644 for '/home/user/.ssh/id_ed25519' are too open. It is required that your private key files are NOT accessible by others.` - SSH refuses to use the key.

**Root Cause:**
Key file has world-readable or group-readable permissions. SSH refuses to use it as a security protection.

**Diagnostic Command:**

```bash
ls -la ~/.ssh/
stat ~/.ssh/id_ed25519
```

**Fix:**

```bash
chmod 600 ~/.ssh/id_ed25519
chmod 700 ~/.ssh/
```

**Prevention:**
`ssh-keygen` sets correct permissions automatically; only breaks when files are copied or synced without preserving permissions.

---

**Authentication Failure with Valid Key**

**Symptom:**
`Permission denied (publickey)` even though the key is correct.

**Root Cause:**
Multiple possible causes: wrong user, wrong key in `authorized_keys`, SELinux labels on `authorized_keys`, home directory permissions too permissive.

**Diagnostic Command:**

```bash
# Verbose client output - shows every auth attempt
ssh -vvv user@server 2>&1 | grep -A3 "Offering\|denied"

# On server - check auth log
journalctl -u sshd -f
tail -f /var/log/auth.log

# Check authorized_keys permissions on server
ls -la ~/.ssh/authorized_keys
# Must be: -rw------- (600) or -rw-r--r-- (644)
# Home dir must NOT be world-writable: drwx------ (700)
```

**Fix:**

```bash
# Fix common permission issue
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**Prevention:**
Use `ssh-copy-id` to add keys - it sets correct permissions automatically.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Networking` - TCP/IP, port 22, network routing are the transport layer SSH runs over
- `Users and Groups` - SSH authenticates as a specific user with specific permissions
- `Linux File System Hierarchy` - SSH config files live in standard locations (`~/.ssh/`, `/etc/ssh/`)

**Builds On This (learn these next):**

- `SCP / rsync` - file copy tools that use SSH as their transport
- `Git & Branching Strategy` - git over SSH uses public-key auth for repository access
- `CI/CD` - pipelines use SSH keys to deploy to servers and access repositories

**Alternatives / Comparisons:**

- `VPN` - encrypts all traffic at the network level; SSH is application-level, per-connection
- `mTLS` - mutual certificate auth for service-to-service, not human terminal access
- `Telnet / rsh` - plaintext predecessors replaced by SSH; never use these

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Encrypted remote shell protocol using     │
│              │ public-key or password authentication     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Telnet/rsh sent credentials in plaintext  │
│ SOLVES       │ - readable by any network observer        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Private key NEVER leaves your machine -   │
│              │ server only holds your public key         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Remote server access, automated deploys,  │
│              │ secure file transfer, port forwarding     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Service-to-service auth inside a cluster  │
│              │ (use mTLS/service mesh instead)           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Strong encryption vs key management       │
│              │ complexity at scale                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A sealed armoured tube between your      │
│              │  keyboard and a remote machine"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SCP/rsync → SSH Certificates → Vault SSH │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your CI/CD pipeline needs to deploy to 50 production servers using SSH. The naive approach stores a single deploy private key in the CI system. Trace what happens if that CI system is compromised - what can the attacker access, how long do they have access, and what design change would limit the blast radius? Consider short-lived SSH certificates versus long-lived keys.

**Q2.** SSH agent forwarding allows you to authenticate to Server B from Server A using your local SSH key, without copying the key to Server A. Under what conditions is this safe and under what conditions does it create a security vulnerability? Trace the exact attack path when agent forwarding is exploited on a compromised Server A.
