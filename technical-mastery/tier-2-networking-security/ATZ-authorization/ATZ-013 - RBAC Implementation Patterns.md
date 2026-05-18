---
id: ATZ-013
title: "RBAC Implementation Patterns"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-006, ATZ-007, ATZ-008
used_by: ATZ-014, ATZ-015, ATZ-026, ATZ-036
related: ATZ-006, ATZ-007, ATZ-014
tags:
  - security
  - authorization
  - rbac
  - implementation
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/authorization/rbac-implementation-patterns/
---

⚡ **TL;DR** - RBAC has three practical implementation levels: flat
(users → roles → permissions, one hop), hierarchical (roles inherit
from parent roles), and constrained (separation of duty rules prevent
conflicting roles). The database schema that underlies it matters
for performance. The architectural choice between inline checks,
framework annotations, and centralized policy enforcement determines
how well the system scales and how easy policy changes are to deploy.

---

### 📊 Entry Metadata

| #013 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-006, ATZ-007, ATZ-008 | |
| **Used by:** | ATZ-014, ATZ-015, ATZ-026, ATZ-036 | |
| **Related:** | ATZ-006 RBAC, ATZ-007 Permissions, ATZ-014 Hierarchical RBAC | |

---

### 📘 Textbook Definition

RBAC implementation patterns describe the specific approaches
to structuring the role-permission model in database schemas,
application code, and policy enforcement. The three NIST-defined
RBAC levels are: Core RBAC (flat user-role-permission), Hierarchical
RBAC (roles inherit from parent roles), and Constrained RBAC
(separation of duty constraints). Implementation choices include:
inline (permission checks scattered through business logic),
annotation-based (declarative method-level security), and
externalized (centralized policy engine queried at enforcement
points).

---

### ⚙️ How It Works (Mechanism)

**RBAC database schema:**

```
┌────────────────────────────────────────────────────────┐
│           Core RBAC Database Schema                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  users          roles            permissions           │
│  ────────────   ──────────────   ──────────────────    │
│  id PK          id PK            id PK                 │
│  email          name             action (read/write..) │
│  ...            description      resource_type         │
│                                  resource_id (or *)    │
│                                                        │
│  user_roles (junction)    role_permissions (junction)  │
│  ──────────────────────   ──────────────────────────   │
│  user_id FK               role_id FK                   │
│  role_id FK               permission_id FK             │
│                           (or inline conditions)       │
│                                                        │
│  QUERY: can user 42 perform "orders:write"?            │
│  SELECT 1                                              │
│  FROM user_roles ur                                    │
│  JOIN role_permissions rp ON rp.role_id = ur.role_id   │
│  JOIN permissions p ON p.id = rp.permission_id         │
│  WHERE ur.user_id = 42                                 │
│    AND p.action = 'orders:write'                       │
│  LIMIT 1;                                              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security RBAC with database-backed roles**

```java
// UserDetailsService loads roles from DB
@Service
public class DbUserDetailsService
        implements UserDetailsService {

    @Override
    public UserDetails loadUserByUsername(String email)
            throws UsernameNotFoundException {
        User user = userRepo.findByEmail(email)
            .orElseThrow(() -> new UsernameNotFoundException(
                email));

        // Load roles from DB (with permission denormalization)
        List<GrantedAuthority> authorities = user.getRoles()
            .stream()
            .map(role -> new SimpleGrantedAuthority(
                "ROLE_" + role.getName()))
            .collect(Collectors.toList());

        return new org.springframework.security.core
            .userdetails.User(
                user.getEmail(),
                user.getPasswordHash(),
                authorities
            );
    }
}

// Controller: declarative role check
@RestController
public class OrderController {

    @GetMapping("/orders")
    @PreAuthorize("hasAnyRole('VIEWER', 'EDITOR', 'ADMIN')")
    public List<Order> listOrders() { ... }

    @DeleteMapping("/orders/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteOrder(@PathVariable Long id) { ... }
}
```

**Example - BAD vs GOOD: inline vs declarative permission checks**

```java
// BAD: inline permission checks scattered in business logic
@GetMapping("/orders/{id}")
public Order getOrder(@PathVariable Long id,
                      @AuthUser User user) {
    Order order = orderRepo.findById(id).orElseThrow();
    // Authorization check buried in business logic
    boolean isViewer = user.getRoles().stream()
        .anyMatch(r -> r.getName().equals("VIEWER")
            || r.getName().equals("EDITOR")
            || r.getName().equals("ADMIN"));
    if (!isViewer) throw new ForbiddenException();
    return order;
}
// Problems:
// - String comparisons for roles (typos = silent bugs)
// - Changing roles means grep-and-replace across codebase
// - Untestable in isolation (business logic mixed with auth)

// GOOD: declarative, centralized role definition
@GetMapping("/orders/{id}")
@PreAuthorize("hasAnyRole('VIEWER', 'EDITOR', 'ADMIN')")
public Order getOrder(@PathVariable Long id) {
    return orderRepo.findById(id).orElseThrow();
}
// Role check is declared at the API boundary
// Business logic is pure - no auth code
// Change roles = change annotation, not business code
```

**Example - Separation of duty constraint (Constrained RBAC)**

```java
// Business rule: no user can be both REQUESTER and APPROVER
// (financial fraud prevention - four-eyes principle)

@Component
public class SoDConstraintValidator {

    private static final Map<String, Set<String>> CONFLICTS =
        Map.of(
            "PURCHASE_REQUESTER",
                Set.of("PURCHASE_APPROVER"),
            "PAYMENT_INITIATOR",
                Set.of("PAYMENT_AUTHORIZER")
        );

    public void validateRoleAssignment(
            Long userId, String newRole) {
        Set<String> userRoles = roleRepo
            .findRoleNames(userId);
        Set<String> conflicts = CONFLICTS
            .getOrDefault(newRole, Set.of());
        Set<String> violation = userRoles.stream()
            .filter(conflicts::contains)
            .collect(Collectors.toSet());
        if (!violation.isEmpty()) {
            throw new SoDViolationException(
                "Cannot assign " + newRole +
                ": conflicts with " + violation);
        }
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-013 | v5.0*