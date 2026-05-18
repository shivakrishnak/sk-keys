---
id: ATH-055
title: "Credential Manager and Secret Rotation"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-007, ATH-030, ATH-048
used_by: ATH-056, ATH-057, ATH-058
related: ATH-030, ATH-048, ATH-056
tags:
  - security
  - authentication
  - credentials
  - secret-rotation
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/authentication/credential-manager-and-secret-rotation/
---

⚡ **TL;DR** - Service credentials (API keys, database passwords,
JWT signing keys) must be stored in a secrets manager (AWS Secrets
Manager, HashiCorp Vault, GCP Secret Manager) rather than in
environment variables or config files. Rotation is the practice
of periodically replacing these credentials with new ones - without
service downtime. Vault's dynamic secrets (database credentials
generated on-demand, valid for 1 hour) eliminate the need for
rotation by making credentials inherently short-lived.

---

### 📊 Entry Metadata

| #055 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-007 Password Hashing, ATH-030 API Key Auth, ATH-048 Workload Identity | |
| **Used by:** | ATH-056, ATH-057, ATH-058 | |
| **Related:** | ATH-030 API Keys, ATH-048 Workload Identity, ATH-056 Enterprise Auth | |

---

### 📘 Textbook Definition

A credential manager (secrets manager) is a system for secure
storage, access control, and auditing of secrets: passwords,
API keys, certificates, and JWT signing keys. Secret rotation
is the practice of periodically replacing a secret with a new
value - to limit the exposure window if a secret is compromised.
Zero-downtime rotation requires: storing both old and new
credentials simultaneously during the transition period, updating
consumers to use the new credential before invalidating the
old one, and automating the rotation lifecycle. Dynamic secrets
(Vault database secrets engine) eliminate the rotation problem
by generating short-lived, one-use credentials on demand.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Secret Rotation Strategies                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STATIC SECRETS (traditional):                         │
│  - API key stored in secrets manager                   │
│  - Application fetches at startup or per-request       │
│  - Rotation: new key generated, old invalidated        │
│  - Risk window: time between compromise and rotation   │
│                                                        │
│  ROTATION FLOW (zero-downtime):                        │
│  1. Generate new secret (keep old active)              │
│  2. Update secrets manager with new secret             │
│  3. Trigger config reload in all consumers             │
│     (k8s secret + restart, or dynamic reload)          │
│  4. Verify consumers are using new secret              │
│  5. Invalidate old secret                              │
│  Challenge: step 3 = rolling restart, brief dual-key   │
│                                                        │
│  DYNAMIC SECRETS (Vault):                              │
│  - No stored long-lived credential                     │
│  - App requests: "give me db credentials"              │
│  - Vault creates a real DB user with TTL=1hour         │
│  - Returns username + password to app                  │
│  - After 1 hour: DB user deleted automatically         │
│  - Breach: attacker has 1-hour-max window              │
│  - No rotation needed: never long-lived                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Vault dynamic database credentials in Java**

```java
@Component
public class VaultDatabaseCredentials {

    private final VaultTemplate vaultTemplate;

    // Get fresh DB credentials from Vault each time
    // Vault creates a real Postgres user with TTL
    public DataSource createDataSource() {
        // Request dynamic credentials from Vault
        // Path: database/creds/my-app-role
        VaultResponse response = vaultTemplate
            .read("database/creds/my-app-role");
        // Response: username + password (valid for 1 hour)
        // Vault auto-revokes after TTL
        String username =
            (String) response.getData().get("username");
        String password =
            (String) response.getData().get("password");
        long leaseDurationSec =
            response.getLeaseDuration();

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://db:5432/app");
        config.setUsername(username);
        config.setPassword(password);
        // Connection pool max lifetime < Vault lease TTL
        // Ensures no connection uses expired credentials
        config.setMaxLifetime(
            (leaseDurationSec - 60) * 1000);
        return new HikariDataSource(config);
    }
}
```

---

*Authentication category: ATH | Entry: ATH-055 | v5.0*