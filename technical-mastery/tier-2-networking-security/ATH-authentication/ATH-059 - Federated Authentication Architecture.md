---
id: ATH-059
title: "Federated Authentication Architecture"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-022, ATH-024, ATH-025, ATH-056, ATH-057, ATH-058
used_by: ATH-060, ATH-065
related: ATH-057, ATH-058, ATH-065
tags:
  - security
  - authentication
  - federation
  - architecture
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/authentication/federated-authentication-architecture/
---

⚡ **TL;DR** - Federation means "I trust your IdP to assert
identity, so I accept your users." Organization A and Organization
B federate their IdPs so that a user authenticated by IdP-A can
access resources at Organization B without a separate account.
B2B federation (contractor access, partner portals) uses SAML or
OIDC. The trust model is: B's Service Provider (SP) trusts A's
IdP assertions because B configured A's signing certificate.
Cross-domain attribute mapping (A's `department` claim = B's
`role`) is the engineering complexity.

---

### 📊 Entry Metadata

| #059 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-022 OIDC, ATH-024 SAML, ATH-025 Social Login, ATH-056 Enterprise, ATH-057 IdP Design, ATH-058 Multi-Cloud | |
| **Used by:** | ATH-060, ATH-065 | |
| **Related:** | ATH-057 IdP Design, ATH-058 Multi-Cloud, ATH-065 Trust Chain | |

---

### 📘 Textbook Definition

Federated authentication is an arrangement where two or more
organizations establish mutual trust such that users
authenticated by one organization's IdP (the Identity Provider
or Issuer) can access resources at another organization (the
Service Provider or Relying Party) without re-authentication.
The trust is established through cryptographic means: the SP
is configured with the IdP's X.509 certificate (SAML) or JWKS
endpoint URL (OIDC), and the SP validates all assertions using
these. Common federation patterns: B2B federation (partner
access), consumer federation (social login: trust Google,
GitHub), enterprise-to-SaaS (employees access SaaS apps via
corporate SSO), and government/cross-agency (e.g., FedRAMP,
EU eIDAS).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Federated Authentication Trust Model           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SETUP (one-time per federation relationship):         │
│  Org A (IdP): share SAML metadata XML or OIDC          │
│              discovery URL (.well-known/openid-config) │
│  Org B (SP):  configure Org A as trusted IdP           │
│              register SP at Org A (SAML SP metadata)   │
│  Trust anchor: IdP signing certificate or JWKS URL     │
│                                                        │
│  AUTHENTICATION FLOW:                                  │
│  1. User at Org A visits Org B's application           │
│  2. App redirects to Org B's SP → initiates SSO        │
│  3. SP redirects to Org A's IdP (SAML redirect)        │
│  4. User authenticates at Org A's IdP                  │
│  5. IdP sends SAML assertion to SP (signed)            │
│  6. SP validates signature using IdP cert              │
│  7. SP maps assertions: NameID, attributes, roles      │
│  8. User is logged in to Org B's app                   │
│  No Org B account needed - identity is federated       │
│                                                        │
│  ATTRIBUTE MAPPING:                                    │
│  IdP says: department=Engineering                      │
│  SP maps to: role=developer                            │
│  Custom mapping: org-specific transformation rules     │
│  Challenge: mismatched semantics between orgs          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - SAML B2B federation configuration in Spring**

```java
// Spring Security SAML: trust an external partner IdP
// Partner's users can log in to your application
@Configuration
@EnableWebSecurity
public class SamlFederationConfig {

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        http.saml2Login(saml2 -> saml2
            .relyingPartyRegistrationRepository(
                relyingPartyRegistrations()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/partner/**").authenticated()
                .anyRequest().authenticated());
        return http.build();
    }

    @Bean
    public RelyingPartyRegistrationRepository
            relyingPartyRegistrations() {
        // Register Partner A as a trusted IdP
        // They share their SAML metadata XML
        RelyingPartyRegistration partnerA =
            RelyingPartyRegistrations
                .fromMetadataLocation(
                    // Partner's SAML metadata URL
                    "https://partner-a.com/saml/metadata")
                .registrationId("partner-a")
                // Your SP's entityId
                .entityId("https://myapp.com/saml/metadata")
                // Attribute mapping
                .nameIdFormat(
                    "urn:oasis:names:tc:SAML:2.0:" +
                    "nameid-format:emailAddress")
                .build();
        return new InMemoryRelyingPartyRegistrationRepository(
            partnerA);
    }
}
// Attribute mapping: partner sends role=admin
// Map to your internal role via UserDetailsService
```

---

*Authentication category: ATH | Entry: ATH-059 | v5.0*