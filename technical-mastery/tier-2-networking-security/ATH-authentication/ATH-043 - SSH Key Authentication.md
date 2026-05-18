---
id: ATH-043
title: "SSH Key Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-040
used_by: ATH-048, ATH-055
related: ATH-040, ATH-048, ATH-055
tags:
  - security
  - authentication
  - ssh
  - public-key
  - devops
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/authentication/ssh-key-authentication/
---

⚡ **TL;DR** - SSH key authentication replaces passwords for server
access with asymmetric cryptography: the private key never leaves
the client, the public key is installed on servers. Authentication
is a challenge-response: the server encrypts a challenge with the
public key; only the holder of the private key can decrypt and
respond. The operational problem: SSH keys accumulate (engineers
add keys and forget them), are hard to revoke at scale, and have
no central management. Use certificate-based SSH (SSH CAs) for
teams larger than ~20 engineers - much easier to rotate and revoke.

---

### 📊 Entry Metadata

| #043 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-040 Certificate Auth | |
| **Used by:** | ATH-048, ATH-055 | |
| **Related:** | ATH-040 Certificates, ATH-048 Service Identity, ATH-055 Credential Manager | |

---

### 📘 Textbook Definition

SSH key authentication uses asymmetric cryptography for
authenticating to SSH servers. The user generates an RSA, ECDSA,
or Ed25519 key pair; the public key is added to
`~/.ssh/authorized_keys` on the server. During authentication,
the SSH server sends a challenge encrypted with the public key;
the client signs it with its private key; the server verifies
the signature. This eliminates password exposure to remote
servers. SSH certificates (OpenSSH CA) extend this model:
instead of distributing individual public keys to all servers,
servers trust an SSH Certificate Authority; users receive
short-lived certificates signed by the CA, eliminating the need
for per-server key distribution.

---

### ⚙️ How It Works (Mechanism)

**SSH key vs SSH certificate:**

```
┌────────────────────────────────────────────────────────┐
│         SSH Key vs SSH Certificate                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SSH KEY (traditional):                                │
│  User: generate key pair                               │
│  Admin: add public key to each server's authorized_keys│
│  100 servers: 100 authorized_keys files to maintain   │
│  Revoke: find and remove key from all 100 servers      │
│  Key rotated: repeat for all servers                   │
│  No expiry: key valid until manually removed           │
│                                                        │
│  SSH CERTIFICATE (recommended for teams):              │
│  CA: create SSH Certificate Authority (private CA key) │
│  Server: trust CA (one line in sshd_config)            │
│  User: request cert from CA (short-lived, 8-24 hours)  │
│    Certificate: signed by CA, includes principals,     │
│    not-before, not-after, extensions                   │
│  Revoke: don't issue new cert (old cert expires)       │
│  100 servers: all updated in one sshd_config line      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - SSH CA certificate issuance (HashiCorp Vault)**

```bash
# Vault SSH CA engine: issues short-lived SSH certs
# Certificates expire after 8 hours - no manual revocation

# Setup: enable SSH secrets engine
vault secrets enable -path=ssh ssh

# Configure server CA
vault write ssh/config/ca \
    generate_signing_key=true

# Create role for engineers
vault write ssh/roles/engineers \
    key_type=ca \
    allowed_users="*" \
    ttl="8h" \
    max_ttl="24h" \
    extensions='{"permit-pty":"","permit-user-rc":""}' \
    default_extensions='{"permit-pty":""}'

# Server config: trust Vault CA
# /etc/ssh/sshd_config
# TrustedUserCAKeys /etc/ssh/vault_ca.pub

# User: get a certificate
vault ssh -role=engineers -mode=ca \
    user@server.example.com
# Vault: authenticates user (via LDAP/OIDC), issues cert
# cert_serial stored in Vault for audit trail
# cert expires in 8h: no manual revocation needed
```

**Example - BAD: private key without passphrase**

```bash
# BAD: unprotected private key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
# -N "" means no passphrase
# If laptop is stolen: attacker has immediate SSH access
# to all servers with this public key

# GOOD: always protect with passphrase
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
# Enter passphrase: <strong random passphrase>
# Use ssh-agent to avoid typing passphrase repeatedly
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

*Authentication category: ATH | Entry: ATH-043 | v5.0*