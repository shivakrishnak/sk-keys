---
id: ATH-025
title: "Social Login Implementation"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-022
used_by: ATH-044, ATH-050
related: ATH-022, ATH-026, ATH-033
tags:
  - security
  - authentication
  - social-login
  - oauth
  - oidc
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/authentication/social-login-implementation/
---

⚡ **TL;DR** - Social login ("Sign in with Google/GitHub/Apple") uses
OIDC (or OAuth 2.0 with a user-info endpoint) to delegate authentication
to a trusted third-party IdP. The implementation is not just an API
call - it requires account linking (what happens when the user signs
in with Google AND email separately?), email verification trust, and
handling provider-side account deletion or deactivation. Get these
wrong and you have account takeover vectors.

---

### 📊 Entry Metadata

| #025 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-022 OIDC | |
| **Used by:** | ATH-044, ATH-050 | |
| **Related:** | ATH-022 OIDC, ATH-026 Magic Link, ATH-033 PKCE | |

---

### 📘 Textbook Definition

Social login (federated identity) uses an external Identity
Provider (Google, GitHub, Facebook, Apple) as the authentication
authority via OIDC or OAuth 2.0. The application receives an
ID Token or access token representing a verified user identity
and maps it to a local account. Implementation requires decisions
on: account linking strategy (provider-specific sub vs email
as primary key), handling multiple providers for the same
user, behavior when provider reports unverified email, and
what happens when the user deletes their social account.

---

### ⚙️ How It Works (Mechanism)

**Account linking strategy:**

```
┌────────────────────────────────────────────────────────┐
│         Social Login Account Linking                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STRATEGY 1: Use provider sub as primary identifier    │
│  google_sub: "104356789012345678901"                   │
│  github_sub: "12345678"                                │
│  Pros: unique, stable, provider controls               │
│  Cons: one account per provider (no linking by default)│
│                                                        │
│  STRATEGY 2: Link by email (common but risky)          │
│  User signs in with Google (alice@gmail.com)           │
│  → find existing account with that email              │
│  → link Google provider to that account               │
│  Risk: Google reports email as verified, but:          │
│    - Some providers report unverified emails as "email" │
│    - Attacker registers Google account with victim's   │
│      email → links to victim's account                │
│                                                        │
│  SAFE EMAIL LINKING RULE:                              │
│  Only link by email if:                                │
│  1. Provider explicitly marks email_verified=true      │
│  2. Provider is trusted (Google, Apple - verified)     │
│  3. Never auto-link without manual confirmation email  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security social login + account linking**

```java
@Service
public class OidcUserAccountLinkingService
        implements OAuth2UserService<OidcUserRequest,
                                     OidcUser> {

    @Override
    public OidcUser loadUser(OidcUserRequest request)
            throws OAuth2AuthenticationException {
        // Load the OIDC user from the IdP
        OidcUser oidcUser = delegate.loadUser(request);

        String providerId = request
            .getClientRegistration().getRegistrationId();
        String providerSub = oidcUser.getSubject();
        String email = oidcUser.getEmail();
        boolean emailVerified =
            Boolean.TRUE.equals(oidcUser.getEmailVerified());

        // Find existing linked account
        Optional<User> byProvider = userRepo
            .findByProviderAndSub(providerId, providerSub);
        if (byProvider.isPresent()) {
            return buildOidcUser(byProvider.get(), oidcUser);
        }

        // Safe email linking: only if verified
        if (emailVerified && email != null) {
            Optional<User> byEmail = userRepo
                .findByEmail(email);
            if (byEmail.isPresent()) {
                // Link this provider to existing account
                linkProvider(byEmail.get(), providerId,
                    providerSub);
                return buildOidcUser(byEmail.get(), oidcUser);
            }
        }

        // No existing account: create new
        User newUser = createUserFromOidc(
            oidcUser, providerId, providerSub);
        return buildOidcUser(newUser, oidcUser);
    }
}
```

**Example - BAD: linking by unverified email**

```java
// BAD: link by email regardless of email_verified claim
public User findOrCreateUser(OidcUser oidcUser) {
    String email = oidcUser.getEmail();
    return userRepo.findByEmail(email)
        .orElseGet(() -> createUser(oidcUser));
    // If email_verified = false:
    //   Attacker creates Google account with
    //   victim@example.com (unverified)
    //   → your app links to victim's account
    //   → attacker can log in as victim
}

// GOOD: require email_verified = true before linking
public User findOrCreateUser(OidcUser oidcUser) {
    boolean verified = Boolean.TRUE.equals(
        oidcUser.getEmailVerified());
    if (!verified) {
        throw new OAuth2AuthenticationException(
            "Email must be verified to use social login");
    }
    // Now safe to link by email
    return userRepo.findByEmail(oidcUser.getEmail())
        .orElseGet(() -> createUser(oidcUser));
}
```

---

*Authentication category: ATH | Entry: ATH-025 | v5.0*