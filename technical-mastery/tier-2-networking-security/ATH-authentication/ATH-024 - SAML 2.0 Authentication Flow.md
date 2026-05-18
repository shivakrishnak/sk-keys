---
id: ATH-024
title: "SAML 2.0 Authentication Flow"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-022
used_by: ATH-056, ATH-059
related: ATH-022, ATH-041, ATH-059
tags:
  - security
  - authentication
  - saml
  - sso
  - enterprise
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/authentication/saml-2-0-authentication-flow/
---

⚡ **TL;DR** - SAML 2.0 (Security Assertion Markup Language) is the
enterprise standard for SSO, predating OIDC by a decade. An Identity
Provider (IdP: Okta, ADFS, Azure AD) issues XML-based signed assertions
that the Service Provider (SP: your application) trusts. SAML is
verbose (XML vs JWT), browser-only (relies on redirects and POST),
but is deeply embedded in enterprise IdPs. If your application
integrates with corporate SSO, you likely encounter SAML.

---

### 📊 Entry Metadata

| #024 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-022 OIDC | |
| **Used by:** | ATH-056, ATH-059 | |
| **Related:** | ATH-022 OIDC, ATH-041 Kerberos, ATH-059 Federated Architecture | |

---

### 📘 Textbook Definition

SAML 2.0 (OASIS standard, 2005) is an XML-based framework for
exchanging authentication and authorization data between an Identity
Provider (IdP) and Service Provider (SP). The SP redirects
unauthenticated users to the IdP with a SAML AuthnRequest. The
IdP authenticates the user and returns a digitally signed SAML
Response containing an Assertion (identity claims, attributes,
session expiry) via browser POST or redirect binding. The SP
validates the assertion's signature, checks recipient/audience,
verifies conditions (validity window), and establishes a local
session for the authenticated user.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│           SAML 2.0 SP-Initiated SSO Flow               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. User hits SP: GET https://app.example.com/page     │
│  2. SP: not authenticated, generate AuthnRequest:      │
│     <samlp:AuthnRequest                                │
│       AssertionConsumerServiceURL=".../acs"            │
│       Destination="https://idp.okta.com/sso/saml"     │
│       ID="_uuid123" .../>                              │
│  3. SP Base64+deflate encodes, redirects to IdP:       │
│     GET https://idp.okta.com/sso/saml?SAMLRequest=...  │
│                                                        │
│  4. User authenticates at IdP                          │
│  5. IdP generates signed SAML Response:                │
│     <samlp:Response>                                   │
│       <Assertion>                                      │
│         <Subject>alice@corp.com</Subject>              │
│         <Conditions NotBefore=".." NotOnOrAfter=".."   │
│           <AudienceRestriction>https://app</Audience>  │
│         </Conditions>                                  │
│         <AttributeStatement>                           │
│           <Attribute Name="roles">EDITOR</Attribute>   │
│         </AttributeStatement>                          │
│       </Assertion>                                     │
│       <Signature>...</Signature>                       │
│     </samlp:Response>                                  │
│  6. IdP POSTs response to SP ACS endpoint              │
│  7. SP validates: signature, audience, NotOnOrAfter    │
│  8. SP creates local session                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security SAML 2.0 configuration**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http)
        throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .anyRequest().authenticated()
        )
        .saml2Login(saml2 -> saml2
            .relyingPartyRegistrationRepository(
                relyingPartyRegistrationRepository())
            .loginPage("/login")
            .defaultSuccessUrl("/dashboard")
        )
        .saml2Logout(Customizer.withDefaults()); // SLO
    return http.build();
}

@Bean
public RelyingPartyRegistrationRepository
        relyingPartyRegistrationRepository() {
    RelyingPartyRegistration registration =
        RelyingPartyRegistrations
            // Load IdP metadata from Okta/ADFS
            .fromMetadataLocation(
                "https://corp.okta.com/app/.../sso/saml/metadata")
            .registrationId("okta")
            .assertingPartyMetadata(party -> party
                .entityId("https://corp.okta.com")
            )
            .entityId("https://app.example.com")
            .build();
    return new InMemoryRelyingPartyRegistrationRepository(
        registration);
}
```

**Example - FAILURE: SAML XML signature wrapping attack**

```xml
<!-- XML Signature Wrapping (XSW) attack -->
<!-- Vulnerability: SP validates signature but matches
     the WRONG element as the assertion content -->

<!-- Original valid assertion (simplified): -->
<Response ID="resp1">
  <Assertion ID="assert1">
    <Subject>legit@corp.com</Subject>
    <Signature><!-- valid signature over assert1 --></Signature>
  </Assertion>
</Response>

<!-- XSW: attacker wraps assertion in extra element -->
<Response ID="resp1">
  <Assertion ID="assert1">                 ← signature matches
    <Subject>legit@corp.com</Subject>
    <Signature><!-- valid sig --></Signature>
  </Assertion>
  <Assertion ID="assert2">                 ← attacker assertion
    <Subject>admin@corp.com</Subject>      ← attacker identity
  </Assertion>                              SP uses WRONG assert
</Response>
<!-- If SP processes the last assertion (assert2) after validating
     assert1's signature: attacker authenticates as admin -->

Fix: Use a hardened SAML library (OpenSAML, Spring Security SAML2)
  that validates the signature covers the assertion being processed,
  and does not allow multiple assertions in a single response
  unless each is independently signed and validated.
```

---

*Authentication category: ATH | Entry: ATH-024 | v5.0*