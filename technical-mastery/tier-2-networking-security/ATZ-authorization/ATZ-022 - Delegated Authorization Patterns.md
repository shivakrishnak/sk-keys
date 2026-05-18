---
id: ATZ-022
title: "Delegated Authorization Patterns"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-013, ATZ-015, ATZ-017
used_by: ATZ-040, ATZ-047, ATZ-050
related: ATZ-017, ATZ-021, ATZ-023
tags:
  - security
  - authorization
  - delegation
  - oauth
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/authorization/delegated-authorization-patterns/
---

⚡ **TL;DR** - Delegated authorization lets User A grant User B (or
a service) the ability to act on A's behalf, within a constrained
scope. OAuth 2.0 scopes are the canonical implementation: a user
grants an app read:email permission without giving it full account
access. The critical design constraint: delegation must be bounded -
you cannot delegate more than you have, delegation must be revocable,
and delegation chains (A delegates to B who delegates to C) compound
risk at each hop.

---

### 📊 Entry Metadata

| #022 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC, ATZ-015 ABAC, ATZ-017 OAuth Scopes | |
| **Used by:** | ATZ-040, ATZ-047, ATZ-050 | |
| **Related:** | ATZ-017 OAuth Scopes, ATZ-021 Inheritance, ATZ-023 Service Accounts | |

---

### 📘 Textbook Definition

Delegated authorization is the mechanism by which a principal
(user, service, or role) grants another principal the ability to
perform specific actions on its behalf. The core constraint is
non-amplification: a delegatee cannot obtain permissions the
delegator does not possess. Patterns include: OAuth 2.0 scope
delegation (user to application), impersonation (admin acting as
user), service account delegation (user authorizing a scheduled
job), and cross-tenant delegation (user in org A granting limited
access to service in org B).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Delegated Authorization Patterns               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PATTERN 1: OAuth 2.0 Scope Delegation                 │
│  Principal: user (has: read + write + admin)           │
│  Delegate: third-party app                             │
│  Grant: scope=read_email (subset only)                 │
│  Constraint: app cannot get write even if it asks     │
│                                                        │
│  PATTERN 2: Impersonation (break-glass)                │
│  Principal: support agent                              │
│  Delegate: can act as customer (bounded scope)         │
│  Constraint: logged, time-limited, specific purpose    │
│  All actions attributed to agent@support.com not user  │
│                                                        │
│  PATTERN 3: Service Account Delegation                 │
│  Principal: alice@corp.com                             │
│  Delegate: nightly-report-job (runs as alice's context)│
│  Constraint: only permitted files, only specific time  │
│  Revocation: revoking alice's access revokes job too   │
│                                                        │
│  DELEGATION CHAIN RISK:                                │
│  A (admin) -> B (manager) -> C (contractor)            │
│  C acts with A's delegated authority                   │
│  If B is compromised: A's authority is exposed         │
│  Mitigation: limit delegation depth (max 1 hop)        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Service account delegation with bound permissions**

```java
@Service
public class DelegatedActionService {

    @Transactional
    public DelegationToken createDelegation(
            String delegatorUserId,
            String delegateeServiceId,
            Set<String> requestedScopes,
            Duration validity) {
        // Fetch delegator's actual permissions
        Set<String> delegatorPerms = permissionService
            .getPermissions(delegatorUserId);

        // Non-amplification: intersection only
        Set<String> grantedScopes = requestedScopes.stream()
            .filter(delegatorPerms::contains)
            .collect(Collectors.toSet());

        if (grantedScopes.isEmpty()) {
            throw new InsufficientPermissionsException(
                "Delegator lacks all requested scopes");
        }

        return delegationTokenRepo.save(new DelegationToken(
            UUID.randomUUID().toString(),
            delegatorUserId,
            delegateeServiceId,
            grantedScopes,
            Instant.now().plus(validity),
            false // not revoked
        ));
    }

    public boolean isAuthorized(String delegationTokenId,
                                 String requiredScope) {
        DelegationToken token = delegationTokenRepo
            .findById(delegationTokenId)
            .orElseThrow();
        return !token.isRevoked()
            && !token.isExpired()
            && token.getScopes().contains(requiredScope)
            // Also verify the original delegator still has
            // the permission (dynamic check)
            && permissionService.hasPermission(
                token.getDelegatorUserId(), requiredScope);
    }
}
```

**Example - BAD: delegation without scope bounding**

```java
// BAD: delegatee gets delegator's full permission set
public void delegate(String delegatorId,
                      String delegateeId) {
    // Copy all permissions to the delegatee
    Set<String> perms = permissionService
        .getPermissions(delegatorId);
    permissionService.grantAll(delegateeId, perms);
    // Problem: delegatee now has full access
    // If admin delegates to a contractor: contractor
    // has admin-equivalent permissions
}

// GOOD: explicit scope list, intersection enforced
// Only grant what was explicitly requested AND delegator has
```

---

*Authorization category: ATZ | Entry: ATZ-022 | v5.0*