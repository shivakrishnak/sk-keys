---
id: ATZ-034
title: "Capability-Based Security"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-007, ATZ-010, ATZ-013
used_by: ATZ-036, ATZ-048, ATZ-058
related: ATZ-010, ATZ-022, ATZ-036
tags:
  - security
  - authorization
  - capability-based
  - access-control
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/authorization/capability-based-security/
---

⚡ **TL;DR** - Capability-based security inverts the traditional
access control model. Instead of "identity checks permission at the
resource", capabilities are unforgeable tokens that grant access.
Possessing the capability is sufficient: no identity check needed.
Think of a capability like a key: whoever holds the key can open
the lock - you don't need to show ID. Modern examples: signed
S3 pre-signed URLs, OAuth tokens (as limited capabilities), and
OCAP (Object Capabilities) in distributed systems. Capabilities
simplify delegation: give someone the token, they have the access.

---

### 📊 Entry Metadata

| #034 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-007 Permissions, ATZ-010 ACL, ATZ-013 RBAC | |
| **Used by:** | ATZ-036, ATZ-048, ATZ-058 | |
| **Related:** | ATZ-010 ACL, ATZ-022 Delegation, ATZ-036 ReBAC | |

---

### 📘 Textbook Definition

Capability-based security is an access control paradigm in which
unforgeable tokens (capabilities) represent the right to perform
an action on a resource. Possession of a valid capability grants
access without requiring identity verification. Capabilities
are: unforgeable (cryptographically signed or stored in a
secure system), delegatable (holder can give capability to
another), revocable (the authority that issued the capability
can invalidate it), and scoped (each capability grants a
specific set of operations). Capability-based systems avoid
the Confused Deputy Problem: a deputy service can only perform
actions it has been explicitly given capabilities for.

---

### ⚙️ How It Works (Mechanism)

**Capability vs ACL model:**

```
┌────────────────────────────────────────────────────────┐
│         ACL vs Capability Model                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ACL MODEL (traditional):                              │
│  Resource /file keeps a list: {alice: rw, bob: r}      │
│  Request: alice asks to write /file                    │
│  System: check /file ACL for alice -> allow            │
│  Problem: "Confused Deputy" - a service with many      │
│  permissions can be tricked into using wrong perm      │
│                                                        │
│  CAPABILITY MODEL:                                     │
│  Resource issues tokens: token_A=write_file_capability │
│  Alice holds token_A (capability)                      │
│  Request: present token_A to write /file               │
│  System: token_A valid, not revoked? -> allow          │
│  Confused Deputy: service has only capabilities        │
│  given to it -> cannot be tricked into using others    │
│                                                        │
│  MODERN EXAMPLES:                                      │
│  S3 pre-signed URL: a URL is a capability              │
│    - Signed by AWS, expires, grants exactly one action │
│    - Share the URL: recipient has that access          │
│    - No identity verification needed                   │
│  OAuth access token: limited capability                │
│    - Scoped to specific resources and actions          │
│    - Bearer of token has access (bearer token)         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - S3 pre-signed URL as capability**

```java
@Service
public class DocumentDownloadService {

    private final S3Presigner presigner;

    // Issue a time-limited capability to download a document
    // No authentication needed at download time
    public String generateDownloadCapability(
            String s3Key, Duration validity) {
        GetObjectPresignRequest presignRequest =
            GetObjectPresignRequest.builder()
                .signatureDuration(validity)
                .getObjectRequest(GetObjectRequest.builder()
                    .bucket("documents-bucket")
                    .key(s3Key)
                    .build())
                .build();

        PresignedGetObjectRequest presigned =
            presigner.presignGetObject(presignRequest);

        // This URL IS the capability
        // Anyone with this URL can download the file
        // until validity expires (15 min, 1 hour, etc.)
        return presigned.url().toString();
    }
}

// Controller - requires auth to GET the capability URL
@GetMapping("/documents/{id}/download-url")
@PreAuthorize("hasPermission(#id, 'Document', 'read')")
public String getDownloadUrl(@PathVariable String id) {
    String s3Key = docRepo.getS3Key(id);
    return downloadService.generateDownloadCapability(
        s3Key, Duration.ofMinutes(15));
    // At download time: no auth needed (capability model)
    // Only auth needed: to GET the capability URL
}
```

---

*Authorization category: ATZ | Entry: ATZ-034 | v5.0*