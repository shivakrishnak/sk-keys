---
id: ATZ-057
title: "Formal Access Control Models (Bell-LaPadula, Biba)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-006, ATZ-056
used_by: ATZ-058, ATZ-060
related: ATZ-056, ATZ-058, ATZ-059
tags:
  - security
  - authorization
  - formal-models
  - bell-lapadula
  - biba
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/authorization/formal-access-control-models-bell-lapadula-biba/
---

⚡ **TL;DR** - Bell-LaPadula (1973) and Biba (1977) are the
foundational formal access control models for mandatory access
control (MAC) in classified government/military systems. Bell-
LaPadula focuses on confidentiality: "no read up, no write down"
(a user at SECRET cannot read TOP SECRET, and cannot write to
UNCLASSIFIED to leak secrets). Biba focuses on integrity: "no
write up, no read down" (a low-integrity process cannot corrupt
a high-integrity object). These models underpin modern SELinux,
AppArmor, and MLS (Multi-Level Security) systems.

---

### 📊 Entry Metadata

| #057 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-006 RBAC, ATZ-056 Formal RBAC | |
| **Used by:** | ATZ-058, ATZ-060 | |
| **Related:** | ATZ-056 Formal RBAC, ATZ-058 Policy Language Design, ATZ-059 ABAC/XACML | |

---

### 📘 Textbook Definition

Mandatory Access Control (MAC) models formalize access
restrictions based on security labels assigned to subjects
(users/processes) and objects (files/data), independent of
owner discretion. Bell-LaPadula (BLP, 1973): designed for
confidentiality in US DoD classified systems. Classification
levels: Unclassified < Confidential < Secret < Top Secret.
Simple Security Property (ss-property): no read up (a subject
at level L cannot read objects above L). Star Property
(*-property): no write down (a subject at level L cannot
write to objects below L - prevents declassification). Biba
(1977): designed for integrity. Integrity levels: low < medium
< high. Low-watermark: a subject cannot write to objects at
a higher integrity level. No-read-down: a subject cannot read
objects at lower integrity (to prevent contamination).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│     Bell-LaPadula vs Biba Models                       │
├─────────────────────┬──────────────────────────────────┤
│  Model              │ Policy                           │
├─────────────────────┼──────────────────────────────────┤
│  Bell-LaPadula      │ Goal: CONFIDENTIALITY            │
│  (1973)             │ No read UP (no read above clearance│
│  DoD/Military       │ No write DOWN (no downgrade data)│
│                     │ "Reads flow up, writes flow up"  │
│                     │ Result: classified data never    │
│                     │ leaked to lower clearance        │
├─────────────────────┼──────────────────────────────────┤
│  Biba (1977)        │ Goal: INTEGRITY                  │
│  Commercial systems │ No write UP (no corrupt high-    │
│                     │   integrity with low-integrity)  │
│                     │ No read DOWN (don't contaminate  │
│                     │   yourself with low-integrity)   │
│                     │ "Reads flow down, writes flow up"│
│                     │ Result: untrusted processes      │
│                     │ cannot corrupt trusted data      │
├─────────────────────┼──────────────────────────────────┤
│  Clark-Wilson       │ Goal: INTEGRITY (commercial)     │
│  (1987)             │ Transactions must go through     │
│                     │ transformation procedures (TPs)  │
│                     │ Not simple read/write model      │
│                     │ Closer to real business logic    │
└─────────────────────┴──────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Simulated BLP policy enforcement in code**

```java
// Bell-LaPadula: no read up, no write down
// Used as a demonstration model (not literal BLP)
public class BlpAccessControl {

    enum SecurityLevel { UNCLASSIFIED, CONFIDENTIAL,
                         SECRET, TOP_SECRET }

    public boolean canRead(SecurityLevel subjectLevel,
                            SecurityLevel objectLevel) {
        // ss-property: no read UP
        // Subject can only read at or below their level
        return subjectLevel.ordinal()
            >= objectLevel.ordinal();
    }

    public boolean canWrite(SecurityLevel subjectLevel,
                             SecurityLevel objectLevel) {
        // *-property: no write DOWN
        // Subject can only write at or above their level
        // Prevents leaking classified info to lower levels
        return subjectLevel.ordinal()
            <= objectLevel.ordinal();
    }
}

// Example: SELinux type enforcement uses similar principles
// Process: allowed to access only objects with matching label
// semanage fcontext -a -t httpd_sys_content_t "/webroot(/.*)?"
// httpd process: can read httpd_sys_content_t files
// Cannot read: passwd_t (password files), etc.
// This is Mandatory Access Control independent of Unix perms
```

---

*Authorization category: ATZ | Entry: ATZ-057 | v5.0*