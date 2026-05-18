---
id: ATZ-041
title: "Privilege Escalation Attacks"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-006, ATZ-011, ATZ-013, ATZ-042
used_by: ATZ-050, ATZ-054
related: ATZ-042, ATZ-043, ATZ-044
tags:
  - security
  - authorization
  - privilege-escalation
  - owasp
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/authorization/privilege-escalation-attacks/
---

⚡ **TL;DR** - Privilege escalation is when a lower-privileged
principal gains higher privileges than they should have. Vertical
escalation: regular user becomes admin. Horizontal escalation:
user accesses another user's resources at the same privilege level.
Root causes: missing server-side role checks (client sends
`role=admin`), overly permissive role assignments, flawed role
inheritance logic, or unintended admin endpoints that lack
authorization checks. Prevention: explicit role validation on every
request, deny-by-default policies, and regular permission audits.

---

### 📊 Entry Metadata

| #041 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-006 RBAC, ATZ-011 Superuser, ATZ-013 RBAC Patterns, ATZ-042 Broken Access | |
| **Used by:** | ATZ-050, ATZ-054 | |
| **Related:** | ATZ-042 Broken Access Control, ATZ-043 IDOR, ATZ-044 Forced Browsing | |

---

### 📘 Textbook Definition

Privilege escalation (PrivEsc) is an attack where an entity
(user, process, service) gains access rights or permissions
beyond what was authorized. Vertical privilege escalation
elevates from lower to higher privilege tier (user -> admin,
read-only -> read-write). Horizontal privilege escalation
accesses resources of another entity at the same privilege
level (user A accesses user B's data). Common attack vectors:
parameter tampering (changing `role=user` to `role=admin`),
mass assignment (binding admin-only fields from HTTP body),
insecure direct object references, JWT claim manipulation,
race conditions in permission checks, and exploiting group
inheritance chains that inadvertently grant excess privilege.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Privilege Escalation Vectors                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. PARAMETER TAMPERING (most common)                  │
│  Request: POST /api/users/123                          │
│  Body: {"role":"admin"}     <- user controls this      │
│  Vulnerable code: user.setRole(body.role)              │
│  Fix: NEVER bind role from request body               │
│                                                        │
│  2. MASS ASSIGNMENT (Spring/Rails)                     │
│  @Data class User {                                    │
│    private String email;                               │
│    private String role;  <- should be server-only      │
│  }                                                     │
│  @PostMapping: new User(requestBody)                   │
│  Fix: use DTOs, @JsonIgnore on sensitive fields        │
│                                                        │
│  3. JWT CLAIM MANIPULATION                             │
│  Header: {"alg":"none"}                                │
│  Claims: {"sub":"user","roles":["admin"]}              │
│  Server not validating sig: "valid admin token"        │
│  Fix: always validate sig + pin algorithm              │
│                                                        │
│  4. ROLE INHERITANCE LOOP                              │
│  RoleA inherits from RoleB                             │
│  RoleB inherits from RoleA                             │
│  RoleC inherits from RoleA                             │
│  User with RoleC -> traversal -> admin permissions     │
│  Fix: DAG not cycles; explicit audit of inheritance    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Mass assignment vulnerability**

```java
// BAD: binds ALL JSON fields including privileged ones
@PostMapping("/users/{id}")
public User updateUser(@PathVariable Long id,
                        @RequestBody User user) {
    // If request body includes {"role":"ADMIN"}:
    // user.role = ADMIN -> privilege escalation
    return userRepository.save(user);
}

// GOOD: use a DTO that excludes privileged fields
@PostMapping("/users/{id}")
public User updateUser(@PathVariable Long id,
                        @RequestBody UpdateUserDto dto) {
    // UpdateUserDto only has: email, name, phone
    // NO role, NO isAdmin, NO permissions
    User existing = userRepository.findById(id)
        .orElseThrow(NotFoundException::new);
    // Only current user can update their own profile
    verifyOwnership(existing, getCurrentUser());
    existing.setEmail(dto.getEmail());
    existing.setName(dto.getName());
    return userRepository.save(existing);
}
```

---

*Authorization category: ATZ | Entry: ATZ-041 | v5.0*