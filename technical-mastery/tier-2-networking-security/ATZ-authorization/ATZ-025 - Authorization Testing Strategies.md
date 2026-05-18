---
id: ATZ-025
title: "Authorization Testing Strategies"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-013, ATZ-015, ATZ-042
used_by: ATZ-042, ATZ-043, ATZ-044, ATZ-053
related: ATZ-042, ATZ-043, ATZ-044
tags:
  - security
  - authorization
  - testing
  - access-control
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/authorization/authorization-testing-strategies/
---

⚡ **TL;DR** - Authorization bugs (accessing data you shouldn't) are
the #1 OWASP vulnerability. They are hard to find with standard
functional testing because "the feature works for the authorized
user" is not the same as "unauthorized users cannot access it."
Effective authorization testing requires explicit negative testing:
for every protected resource, verify access with: no credentials,
wrong role, different tenant, and a lower-privileged user in the
same role. Automate this with a dedicated test matrix.

---

### 📊 Entry Metadata

| #025 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC, ATZ-015 ABAC, ATZ-042 Broken Access Control | |
| **Used by:** | ATZ-042, ATZ-043, ATZ-044, ATZ-053 | |
| **Related:** | ATZ-042 Broken Access Control, ATZ-043 IDOR, ATZ-044 Forced Browsing | |

---

### 📘 Textbook Definition

Authorization testing is the process of verifying that a system
enforces its access control policies correctly - that principals
with insufficient permissions cannot access protected resources
or perform unauthorized actions. Unlike authentication testing
(can you prove who you are?), authorization testing asks: once
identity is established, are the boundaries enforced? Testing
approaches include: role matrix testing (verify each role can
and cannot perform expected actions), horizontal privilege
escalation testing (can User A access User B's data?), vertical
privilege escalation testing (can a user perform admin actions?),
and forced browsing (can unauthenticated users access protected
endpoints directly?).

---

### ⚙️ How It Works (Mechanism)

**Authorization test matrix approach:**

```
┌────────────────────────────────────────────────────────┐
│         Authorization Test Matrix                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Endpoint: GET /orders/{orderId}                       │
│                                                        │
│  Test cases (each should be automated):                │
│  1. No credentials      -> 401 Unauthorized            │
│  2. Invalid token       -> 401 Unauthorized            │
│  3. Own order (user A)  -> 200 OK                      │
│  4. Other user's order  -> 403 or 404 (tenant isolation│
│                            IDOR check)                 │
│  5. VIEWER role: own    -> 200 OK                      │
│  6. VIEWER role: others -> 403/404                     │
│  7. ADMIN role: any     -> 200 OK                      │
│                                                        │
│  Endpoint: DELETE /orders/{orderId}                    │
│  1. No credentials      -> 401                         │
│  2. VIEWER role own     -> 403 (no delete perm)        │
│  3. EDITOR own order    -> 204 OK                      │
│  4. EDITOR other order  -> 403/404 (IDOR)              │
│  5. ADMIN any order     -> 204 OK                      │
│                                                        │
│  This matrix should be executed automatically          │
│  on every PR (not just manually during pentests)       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Boot authorization test (JUnit 5)**

```java
@SpringBootTest
@AutoConfigureMockMvc
class OrderAuthorizationTest {

    @Autowired MockMvc mockMvc;

    @Test
    @WithMockUser(username="alice", roles={"CUSTOMER"})
    void customerCanReadOwnOrder() throws Exception {
        // alice is the owner of order-001
        mockMvc.perform(get("/orders/order-001"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(username="bob", roles={"CUSTOMER"})
    void customerCannotReadOtherUsersOrder()
            throws Exception {
        // bob is NOT the owner of order-001 (owned by alice)
        // IDOR check: bob should get 403 or 404
        mockMvc.perform(get("/orders/order-001"))
            .andExpect(status().isIn(403, 404));
    }

    @Test
    void unauthenticatedUserCannotReadAnyOrder()
            throws Exception {
        mockMvc.perform(get("/orders/order-001"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(username="alice", roles={"CUSTOMER"})
    void customerCannotDeleteAnyOrder() throws Exception {
        mockMvc.perform(delete("/orders/order-001"))
            .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username="admin", roles={"ADMIN"})
    void adminCanDeleteAnyOrder() throws Exception {
        mockMvc.perform(delete("/orders/order-001"))
            .andExpect(status().isNoContent());
    }
}
```

**Example - BAD: only testing happy path**

```java
// BAD: only tests that the authorized user CAN access
// Never tests that unauthorized users CANNOT
@Test
void testGetOrder() {
    Response response = given()
        .header("Authorization", "Bearer " + adminToken)
        .get("/orders/order-001");
    assertThat(response.statusCode()).isEqualTo(200);
}
// This test passes even if the endpoint has no auth at all
// (anyone can access it without a token)

// GOOD: always add negative test cases alongside happy path
// Test what SHOULD fail, not just what SHOULD succeed
```

---

*Authorization category: ATZ | Entry: ATZ-025 | v5.0*