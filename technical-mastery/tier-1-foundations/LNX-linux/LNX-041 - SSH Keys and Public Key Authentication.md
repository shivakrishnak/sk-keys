---
id: LNX-041
title: "SSH Keys and Public Key Authentication"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-023, CRY-001
used_by: LNX-058, LNX-057
related: LNX-058, CRY-001, IAM-001
tags: [ssh, public-key, private-key, ssh-keygen, authorized-keys, known-hosts, RSA, Ed25519]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/lnx/ssh-keys/
---

## TL;DR

SSH public key authentication replaces passwords with asymmetric cryptography.
`ssh-keygen -t ed25519` generates a key pair (private key stays on your
machine, public key goes to the server's `~/.ssh/authorized_keys`). Once
set up: `ssh user@server` connects without password. Never share your private
key. Use Ed25519 (modern, fast, secure) over RSA. Use a passphrase to
encrypt the private key on disk. SSH agent (`ssh-add`) holds decrypted keys
in memory so you don't type passphrase every time.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-041 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | ssh, public key, private key, authorized_keys, known_hosts, Ed25519, RSA, ssh-agent |
| **Prerequisites** | LNX-023, CRY-001 |

---

### The Problem This Solves

Password authentication has problems: passwords can be brute-forced, shared,
leaked, or phished. SSH keys solve this: the private key never leaves your
machine, the server only stores the public key (mathematically derived from
the private key but not reversible). Compromise of the server's authorized_keys
file doesn't reveal anything useful - attackers still need your private key.
Key-based auth also enables automation: CI/CD pipelines can deploy without
storing passwords.

---

### Textbook Definition

**Asymmetric cryptography**: Uses a mathematically linked key pair. Data
encrypted with the public key can only be decrypted with the private key.
A signature made with the private key can be verified with the public key.

**SSH public key authentication**: The client proves identity by signing
a challenge with the private key. The server verifies the signature against
the stored public key. The private key itself is never transmitted.

**~/.ssh/authorized_keys**: File on the server containing public keys of
authorized users. One public key per line. The server checks this file
when a client attempts key-based login.

**~/.ssh/known_hosts**: Records the public key (fingerprint) of each server
you've connected to. Prevents MITM attacks: if a server's key changes,
SSH warns you.

**Key types:** RSA (older, still common, 4096-bit recommended), Ed25519
(modern, small key, fast, recommended), ECDSA (elliptic curve, less common).

---

### Understand It in 30 Seconds

```bash
# STEP 1: Generate a key pair (on your local machine):
ssh-keygen -t ed25519 -C "your_email@example.com"
# Saves: ~/.ssh/id_ed25519 (private - NEVER share this!)
#        ~/.ssh/id_ed25519.pub (public - copy this to servers)

# Or RSA (if ed25519 not supported by target):
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# STEP 2: Copy public key to server:
ssh-copy-id user@server           # automatic (if password login enabled)
# OR manually:
cat ~/.ssh/id_ed25519.pub         # copy this string
ssh user@server                   # login with password once
mkdir -p ~/.ssh
echo "paste-your-public-key-here" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# STEP 3: Connect without password:
ssh user@server                   # uses key automatically

# View your public key:
cat ~/.ssh/id_ed25519.pub
# ssh-ed25519 AAAA...longstring... your_email@example.com

# SSH agent (hold decrypted key in memory):
eval "$(ssh-agent -s)"            # start agent
ssh-add ~/.ssh/id_ed25519         # add key (enter passphrase once)
ssh-add -l                        # list keys in agent

# Use a specific key (for different servers):
ssh -i ~/.ssh/other_key user@server

# Disable password auth on server (after keys work!):
# Edit /etc/ssh/sshd_config:
# PasswordAuthentication no
# ChallengeResponseAuthentication no
systemctl restart sshd            # apply sshd_config changes

# Check who can connect (view authorized keys):
cat ~/.ssh/authorized_keys

# Permission requirements (SSH is strict about this!):
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519       # private key
chmod 644 ~/.ssh/id_ed25519.pub   # public key
```

---

### First Principles

**How the authentication handshake works:**

```
Client                              Server
------                              ------
"I want to authenticate as alice
 using key ed25519 with
 fingerprint AAAA..."
                                    Check: is AAAA... in
                                    ~/.ssh/authorized_keys?
                                    YES -> proceed

                                    "Here is a random challenge:
                                     nonce = 0xDEADBEEF..."
Sign(challenge, private_key)
= signature S
"Here is S"
                                    Verify(S, challenge, public_key)
                                    if VALID -> AUTH SUCCESS
                                    "Authenticated!"

What the server learns: alice has the private key
What the server NEVER learns: the private key itself
What an attacker who steals authorized_keys learns: nothing useful
  (they have public keys, which don't grant access)
```

**known_hosts protection:**
```bash
# First connection to a new server:
# The authenticity of host 'example.com (1.2.3.4)' can't be established.
# ED25519 key fingerprint is SHA256:abc123...
# Are you sure you want to continue connecting (yes/no)?

# After yes: fingerprint saved in ~/.ssh/known_hosts
# Next connection: fingerprint checked against saved one
# If different: WARNING! REMOTE HOST IDENTIFICATION HAS CHANGED!
# (Could mean: server reinstalled, or MITM attack)

# View known_hosts:
cat ~/.ssh/known_hosts
# example.com ssh-ed25519 AAAA...pubkey...

# Remove entry (if you know the server changed legitimately):
ssh-keygen -R example.com    # remove from known_hosts
```

---

### Thought Experiment

CI/CD pipeline needs to deploy to a production server:

```bash
# WRONG: Store username/password in CI/CD secrets
# PASSWORD=mysecretpassword -> visible in logs, shared with all pipelines

# CORRECT: Dedicated deploy key

# On CI/CD server (or locally for CI setup):
ssh-keygen -t ed25519 -f /tmp/deploy_key -N ""  # -N "" = no passphrase
# (No passphrase: CI/CD can use key without human interaction)

# View the public key:
cat /tmp/deploy_key.pub
# ssh-ed25519 AAAA... ci-deploy-key

# On production server, add ONLY this key for deployment:
# (as deploy user, not root)
echo "command=\"/opt/deploy/deploy.sh\",no-pty,from=\"10.0.1.0/24\" ssh-ed25519 AAAA..." \
    >> /home/deploy/.ssh/authorized_keys
# command= : restricts this key to ONLY run deploy.sh (not arbitrary commands)
# no-pty: no interactive terminal (prevents manual login)
# from= : only accept from CI/CD server subnet

# In CI/CD environment: store private key as a secret
# CI/CD job:
# ssh -i $DEPLOY_PRIVATE_KEY deploy@prod.example.com
# (Actually runs: /opt/deploy/deploy.sh - command-restricted key)
```

---

### Mental Model / Analogy

```
Private key = unique padlock key (only you have it)
Public key = padlock (anyone can put data IN, only you can open it)

Server's authorized_keys = list of padlocks the server accepts

Authentication:
  Server: "I found your padlock in authorized_keys.
           Here's a locked box."
  You: "Here's the box opened with my key."
  Server: "Only someone with that padlock key could open it.
           You're authenticated."

known_hosts = your address book of server identities
  First visit: "I'm recording this server's ID card: fingerprint XYZ"
  Next visit: "Is this the same ID card? YES -> safe. NO -> STOP!"

ssh-agent = keychain in memory
  "Hold my unlocked key while I work today.
   I unlock it once with my passphrase,
   agent reuses it without me re-entering passphrase."

Passphrase on private key = encryption of the key file on disk
  If someone steals your laptop and copies id_ed25519:
  Without passphrase: they immediately have your key
  With passphrase: they have an encrypted blob (must crack the passphrase)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`ssh-keygen -t ed25519`, `ssh-copy-id user@server`, `ssh user@server`.
That's key-based SSH. Set `PasswordAuthentication no` in sshd_config
after keys work. These 3 steps are the core workflow.

**Level 2:**
Multiple keys for different servers: `ssh -i ~/.ssh/specific_key user@server`.
`~/.ssh/config` file for defaults per host. `ssh-agent` + `ssh-add` to
avoid re-entering passphrase. `authorized_keys` format: one key per line.
View fingerprint: `ssh-keygen -lf ~/.ssh/id_ed25519.pub`.

**Level 3:**
`authorized_keys` options: `command="cmd"` (restrict key to one command),
`from="IP/subnet"` (restrict by source IP), `no-pty` (no terminal),
`no-port-forwarding`, `expiry-time="20250101"`. Certificate-based SSH
(ssh-cert): SSH CA signs user keys, server trusts CA instead of individual
keys - scalable for many servers. `ForwardAgent yes` in ssh config (with
caution): forwards ssh-agent socket so you can ssh from one server to
another using your local keys.

**Level 4:**
SSH jump hosts: `ssh -J jumphost finalserver` (proxy through a bastion).
`~/.ssh/config`: `ProxyJump` option for multi-hop. ssh-agent forwarding
security risks: on a compromised host, root can use your forwarded agent.
Prefer `ProxyJump` over `ForwardAgent`. SSH certificates (not keys): CA
signs certificates with expiry, revocation, principals. HashKnownHosts:
hashes server names in known_hosts (privacy, but harder to maintain).

**Level 5:**
OpenSSH 8.3+ deprecates RSA SHA-1 (require `PubkeyAcceptedAlgorithms +ssh-rsa`
for old servers). FIDO2/U2F hardware keys: `ssh-keygen -t ecdsa-sk` creates
a key backed by a hardware token (YubiKey). The private key never exists in
software - hardware generates signatures. `ssh-agent` PKCS#11 provider:
SSH agent using keys stored in HSM or smart card. SSH certificates for
ephemeral access: HashiCorp Vault SSH engine signs short-lived certificates
(1 hour TTL) - no static authorized_keys needed.

---

### Code Example

**BAD - SSH key security mistakes:**
```bash
# BAD 1: No passphrase (for personal keys)
ssh-keygen -t ed25519 -N ""   # empty passphrase
# If your laptop is stolen, the unencrypted private key gives
# immediate access to all your servers

# GOOD: Use a passphrase for personal keys (not CI/CD):
ssh-keygen -t ed25519
# Enter passphrase: [use a strong passphrase]
# Use ssh-agent so you only enter it once per session

# BAD 2: Permissive authorized_keys for CI/CD key:
echo "ssh-ed25519 AAAA... ci-key" >> ~/.ssh/authorized_keys
# This key can now: execute any command, access any file,
# start any service, do anything the user can do

# GOOD: Restrict the CI/CD key:
echo 'command="/opt/deploy/run-deploy.sh",no-pty,no-x11-forwarding,no-agent-forwarding,from="10.0.1.0/24" ssh-ed25519 AAAA... ci-key' \
    >> ~/.ssh/authorized_keys

# BAD 3: Disabling password auth before verifying key works:
# Edit sshd_config: PasswordAuthentication no
systemctl restart sshd
# If your key doesn't work: you're locked out!

# CORRECT ORDER:
# 1. Add your public key to authorized_keys
# 2. Test: open a NEW terminal, try ssh with key (don't close current one)
# 3. Verify it works WITHOUT password
# 4. THEN disable password authentication
```

**GOOD - ~/.ssh/config for multi-server management:**
```
# ~/.ssh/config - SSH client configuration

# Default settings for all hosts:
Host *
    ServerAliveInterval 30    # send keepalive every 30s
    ServerAliveCountMax 3     # disconnect after 3 missed keepalives
    AddKeysToAgent yes        # auto-add to ssh-agent
    IdentityFile ~/.ssh/id_ed25519

# Production servers via bastion:
Host prod-bastion
    HostName bastion.example.com
    User deploy
    IdentityFile ~/.ssh/prod_ed25519

Host prod-* !prod-bastion
    ProxyJump prod-bastion
    User ubuntu
    IdentityFile ~/.ssh/prod_ed25519

# Specific server with different key and user:
Host legacy-server
    HostName 10.0.5.100
    User admin
    IdentityFile ~/.ssh/legacy_rsa
    PubkeyAcceptedAlgorithms +ssh-rsa
    HostKeyAlgorithms +ssh-rsa

# GitHub (use specific key for git operations):
Host github.com
    IdentityFile ~/.ssh/github_ed25519
    User git
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "SSH keys are stored on the server" | Only the PUBLIC key is stored on the server (in authorized_keys). The PRIVATE key is on the client and never transmitted. The server cannot reconstruct the private key from the public key (asymmetric cryptography). |
| "If I copy my private key to multiple machines, it's the same key" | Yes, one key pair can be used from multiple client machines. But this is a security trade-off: if any of those machines is compromised, the key is compromised. Best practice: generate separate keys per machine per purpose. |
| "known_hosts is a security annoyance" | known_hosts prevents man-in-the-middle attacks. Without it: you could be connecting to an attacker's server, providing your private key signature (which proves identity but not the destination). The "host changed" warning is critical to investigate, not dismiss. |
| "Ed25519 is less secure than RSA-4096" | Ed25519 is MORE secure and much faster. RSA security depends on the difficulty of factoring large numbers; RSA-2048 is considered safe for now but not long-term. Ed25519 uses elliptic curve cryptography (Curve25519) which provides 128 bits of security with only a 32-byte key, compared to RSA-4096 providing ~140 bits with a 512-byte key. Ed25519 is the modern standard. |
| "Disabling root SSH login is enough security" | Disabling root login (`PermitRootLogin no`) helps but isn't enough alone. Also: disable password authentication (`PasswordAuthentication no`), use fail2ban for brute force protection, restrict SSH to specific IPs with firewall rules, and use non-standard port (minor obfuscation). Layered security. |

---

### Failure Modes & Diagnosis

**SSH key authentication fails (still asking for password):**
```bash
# Symptom: ssh user@server still prompts for password despite adding key
# Debug: verbose mode shows what's happening
ssh -vvv user@server 2>&1 | head -50
# Look for lines like:
# debug1: Offering public key: /home/user/.ssh/id_ed25519 ED25519
# debug1: Authentications that can continue: publickey,password
# debug1: Next authentication method: publickey
# Server declined key -> check authorized_keys and permissions

# Most common causes:
# 1. Wrong permissions on .ssh directory or files:
ls -la ~/.ssh/                      # must be 700
ls -la ~/.ssh/authorized_keys       # must be 600
# Fix:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 2. authorized_keys not writable or has wrong ownership:
ls -la ~/.ssh/authorized_keys   # must be owned by the user
stat ~/.ssh/authorized_keys

# 3. Wrong public key format in authorized_keys:
cat ~/.ssh/authorized_keys   # should be ONE LINE per key: "type key comment"
# Common mistake: copying with line breaks, missing "ssh-ed25519" prefix

# 4. SELinux context issue (RHEL/CentOS):
ls -Z ~/.ssh/   # check SELinux context
restorecon -Rv ~/.ssh/   # restore correct context

# 5. sshd_config not allowing pubkey:
grep -i pubkeyauthentication /etc/ssh/sshd_config
# Should be: PubkeyAuthentication yes (or absent - default yes)
```

---

### Related Keywords

**Foundational:**
LNX-023 (Networking), CRY-001 (Cryptography)

**Builds on this:**
LNX-058 (SSH Advanced Configuration), LNX-057 (Security Hardening)

**Related:**
IAM-001 (Identity Management), SEC-001 (Security)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ssh-keygen -t ed25519` | Generate Ed25519 key pair |
| `ssh-copy-id user@server` | Copy public key to server |
| `ssh -vvv user@server` | Debug SSH connection |
| `ssh -i ~/.ssh/key user@server` | Use specific key |
| `ssh-add ~/.ssh/id_ed25519` | Add key to agent |
| `ssh-add -l` | List keys in agent |
| `ssh-keygen -lf ~/.ssh/id_ed25519.pub` | View fingerprint |
| `ssh-keygen -R hostname` | Remove host from known_hosts |
| `chmod 700 ~/.ssh` | Fix .ssh permissions |
| `chmod 600 ~/.ssh/authorized_keys` | Fix authorized_keys perms |

**3 things to remember:**
1. Private key stays on YOUR machine (NEVER share it); public key goes to server's authorized_keys
2. Permissions must be exact: `chmod 700 ~/.ssh` and `chmod 600 ~/.ssh/authorized_keys` (SSH refuses if too open)
3. Use Ed25519 (`ssh-keygen -t ed25519`) over RSA - it's smaller, faster, and more secure

---

### Transferable Wisdom

SSH public key authentication is the same concept as: GitHub/GitLab "Deploy
Keys" and "SSH Keys in settings" (same authorized_keys model), AWS EC2
key pairs (public key embedded in instance at launch), GCP OS Login (SSH keys
managed via GCP IAM), Kubernetes `kubectl` authentication (client certificates
use same asymmetric principle), GPG/PGP signing (same asymmetric model for
email/commit signing), JWT RS256 tokens (private key signs, public key verifies).

The pattern: generate asymmetric key pair, distribute public key to anyone
who needs to verify you, keep private key safe. This appears in TLS certificates,
code signing, package signing (apt, rpm), Docker image signing (cosign),
and virtually every modern authentication system.

---

### The Surprising Truth

The famous "70% of all SSH servers are vulnerable to this" claim refers to
weak keys generated on low-entropy systems (embedded devices, VMs that
haven't seeded /dev/random yet). In 2012 researchers scanned the internet
and found 5.57% of RSA public keys shared prime factors with at least one
other key - allowing immediate factoring and private key reconstruction.
This happened because some embedded systems generate keys during first boot
with identical low-entropy state. The fix: wait for sufficient entropy before
generating keys. Modern `ssh-keygen` uses /dev/urandom (which has been
cryptographically safe since kernel 4.8 on Linux - it uses the same pool
as /dev/random but never blocks). The Ed25519 key generation is particularly
fast and requires less entropy than RSA key generation, making it less
susceptible to low-entropy issues on embedded systems.

---

### Mastery Checklist

- [ ] Can generate an Ed25519 key pair with a passphrase
- [ ] Can copy a public key to a remote server and verify key-based login
- [ ] Can use ssh-agent to avoid re-entering passphrase
- [ ] Can configure ~/.ssh/config for multiple servers
- [ ] Can restrict an authorized_keys entry to a specific command or IP

---

### Think About This

1. You add your public key to a server's authorized_keys. SSH with your
   private key fails with "Permission denied (publickey)". You check:
   the key is correct in authorized_keys. What are the other most likely
   causes, and in what order would you check them? (Hint: permissions,
   SELinux, sshd_config, home directory permissions.)

2. Your CI/CD pipeline uses a deploy key with `command=` restriction in
   authorized_keys. An attacker compromises the CI/CD server and has
   access to the deploy private key. What can they do with it? What can
   they NOT do? How does the `command=` restriction mitigate the compromise?

3. Agent forwarding (`ForwardAgent yes`) allows you to ssh from server A
   to server B using your local keys without copying them to server A.
   But this is considered a security risk. Why? Under what specific threat
   model does agent forwarding create vulnerability? What is the safer
   alternative for multi-hop SSH?

---

### Interview Deep-Dive

**Foundational:**
Q: How does SSH public key authentication work? What is the difference between the public key and the private key?
A: SSH public key authentication uses asymmetric cryptography (specifically, digital signatures). Key pair: the private key is kept secret on the client. The public key is derived from the private key mathematically but cannot be reversed - you cannot compute the private key from the public key. Authentication protocol: (1) Client initiates: "I want to authenticate as alice using this public key." (2) Server checks if that public key is in alice's `~/.ssh/authorized_keys`. If yes: (3) Server generates a random challenge. (4) Client signs the challenge with the private key (signature proves possession of private key). (5) Client sends the signature. (6) Server verifies the signature using the public key. If valid: authentication succeeds. The private key never leaves the client. Even if the server is compromised and an attacker gets the authorized_keys file: they have public keys, which allow signature VERIFICATION but not SIGNATURE CREATION. They still need the private key to authenticate. This is fundamentally more secure than passwords because the "secret" (private key) is never transmitted.

**Intermediate:**
Q: How do you set up SSH key-based authentication for a CI/CD pipeline that needs to deploy to production servers, with least-privilege access?
A: Least-privilege SSH for CI/CD: (1) Generate a dedicated deploy key with no passphrase (automation needs it): `ssh-keygen -t ed25519 -f deploy_key -N "" -C "ci-deploy"`. (2) Store the PRIVATE key in CI/CD secrets vault (never in code). (3) On production servers, add the PUBLIC key to the deploy user's authorized_keys WITH restrictions: `command="/opt/scripts/deploy.sh",no-pty,no-x11-forwarding,no-agent-forwarding,no-port-forwarding,from="10.0.1.0/24" ssh-ed25519 AAAA... ci-deploy`. Option breakdown: `command=` restricts to ONLY this script (no shell access). `no-pty` prevents interactive terminal. `from=` restricts source IP to CI/CD subnet. (4) The deploy user is a service account with only necessary permissions. (5) CI/CD job: `ssh -i $DEPLOY_KEY -o StrictHostKeyChecking=yes -o UserKnownHostsFile=./known_hosts deploy@prod.example.com` (with known_hosts checked into repo for host verification). (6) Rotate keys periodically. Monitor: if the deploy script is ever executed outside CI/CD hours, that's anomalous. Audit all uses: `grep "Accepted publickey" /var/log/auth.log | grep "ci-deploy"`.

**Expert:**
Q: Explain SSH certificates and how they solve the scaling problem of managing authorized_keys across hundreds of servers.
A: Problem: with 500 servers and 100 engineers, managing authorized_keys means 500 x 100 = 50,000 key entries to update when someone joins or leaves. SSH certificates solve this with a PKI model: (1) Create an SSH Certificate Authority (CA): `ssh-keygen -t ed25519 -f ssh_ca`. (2) Configure all servers to trust the CA: in `/etc/ssh/sshd_config`: `TrustedUserCAKeys /etc/ssh/ssh_ca.pub`. Now any key SIGNED by this CA is trusted. (3) Sign a user's key: `ssh-keygen -s ssh_ca -I "alice@example.com" -n "ubuntu,ec2-user" -V +8h alice_key.pub`. Creates `alice_key-cert.pub`. `-n` = principals (which usernames), `-V` = validity (8 hours). (4) User connects with `ssh -i alice_key` (SSH auto-finds the cert). Server checks: is this cert signed by a trusted CA? Valid principals? Not expired? (5) When Alice leaves: her cert expires in 8 hours. No need to touch any server. For automation: HashiCorp Vault SSH Secrets Engine signs certificates automatically after authenticating to Vault via LDAP/Okta. Each developer gets a fresh 1-hour cert. No static keys on servers at all. Revocation: add cert serial to `/etc/ssh/revoked_keys` on servers. Or reduce TTL (8h max = maximum exposure window). The scaling advantage: N servers x M users -> just 1 CA public key on each server. Adding/removing users = stop signing their certs. No SSH access in 8 hours (or immediately with revocation).
