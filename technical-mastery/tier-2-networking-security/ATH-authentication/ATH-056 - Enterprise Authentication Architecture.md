---
id: ATH-056
title: "Enterprise Authentication Architecture"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-022, ATH-024, ATH-042, ATH-053, ATH-054, ATH-055
used_by: ATH-057, ATH-058, ATH-059
related: ATH-053, ATH-057, ATH-058
tags:
  - security
  - authentication
  - enterprise
  - architecture
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/authentication/enterprise-authentication-architecture/
---

⚡ **TL;DR** - Enterprise authentication architecture combines
an identity provider (Okta, Azure AD, Ping Identity) as the central
source of truth for user identity, federated via SAML 2.0 or OIDC
to all internal and external applications. Employees authenticate
once (SSO) and access all applications without re-entering
credentials. Every app delegates authentication to the IdP -
no app stores passwords. Privileged access management (PAM) adds
just-in-time elevation for admin operations.

---

### 📊 Entry Metadata

| #056 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-022 OIDC, ATH-024 SAML, ATH-042 LDAP, ATH-053 Auth Server, ATH-054 Distributed Sessions, ATH-055 Credential Mgr | |
| **Used by:** | ATH-057, ATH-058, ATH-059 | |
| **Related:** | ATH-053 Auth Server, ATH-057 IdP Design, ATH-058 Multi-Cloud | |

---

### 📘 Textbook Definition

Enterprise authentication architecture is the end-to-end
identity infrastructure for an organization: how employees
authenticate, how applications delegate authentication, how
service accounts are managed, and how privileged access is
controlled. Core components: an Identity Provider (IdP) -
the authoritative source of employee identity, often backed
by Active Directory; a Single Sign-On (SSO) layer - one
login session grants access to all federated applications;
a Privileged Access Management (PAM) system (CyberArk,
HashiCorp Vault) for managing admin credentials; device
identity management (MDM + certificate-based auth); and
a governance layer (access reviews, provisioning, lifecycle
management) to ensure least-privilege is maintained.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Enterprise Authentication Architecture         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  HR SYSTEM (source of truth for identity)              │
│     |  SCIM provisioning (auto-create accounts)        │
│     v                                                  │
│  IDENTITY PROVIDER (Okta / Azure AD)                   │
│  - User store: AD or cloud directory                   │
│  - MFA: TOTP, push, FIDO2                              │
│  - SSO: OIDC + SAML 2.0 for app federation             │
│  - Device trust: MDM certificate validation            │
│     |                                                  │
│  APPLICATIONS (SP / Relying Party):                    │
│  - Internal apps: SAML/OIDC SSO via IdP               │
│  - External SaaS: federated via SAML/OIDC              │
│  - No app stores user passwords                        │
│     |                                                  │
│  PRIVILEGED ACCESS:                                    │
│  - Admin access: PAM system (CyberArk/Vault)           │
│  - Just-in-time: request elevation -> approval ->      │
│                  time-limited admin credential         │
│  - All admin sessions: recorded and audited            │
│     |                                                  │
│  AUDIT + COMPLIANCE:                                   │
│  - All auth events: IdP + app audit logs               │
│  - Quarterly access reviews: entitlement recertification│
│  - SCIM de-provisioning: offboarding auto-revokes access│
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OIDC federation with enterprise IdP**

```java
// Spring Security OIDC configuration
// Delegate ALL authentication to corporate IdP (Okta)
// No passwords stored in the application
@Configuration
@EnableWebSecurity
public class OidcSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .anyRequest().authenticated()
            )
            // Redirect to Okta for authentication
            .oauth2Login(oauth2 -> oauth2
                .defaultSuccessUrl("/dashboard", true)
                .failureUrl("/login?error")
                // userInfoEndpoint: map IdP claims to
                // Spring Security authorities
                .userInfoEndpoint(userInfo -> userInfo
                    .oidcUserService(customOidcUserService()))
            )
            // Also configure for OAuth2 resource server
            // if this app is also an API
            .oauth2ResourceServer(rs -> rs
                .jwt(jwt -> jwt
                    .jwkSetUri(
                        "${okta.oauth2.issuer}/v1/keys")));
        return http.build();
    }
}
// Result: users log in via Okta, get SSO across all apps
// App never sees user passwords
// Offboarded employees: disabled in Okta, all apps locked
```

---

*Authentication category: ATH | Entry: ATH-056 | v5.0*