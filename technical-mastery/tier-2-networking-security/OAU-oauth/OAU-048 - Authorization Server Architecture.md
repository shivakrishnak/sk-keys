---
id: OAU-048
title: "Authorization Server Architecture"
category: OAuth 2.0 & OpenID Connect
tier: tier-2-networking-security
folder: OAU-oauth
difficulty: ★★★
depends_on: OAU-007, OAU-009, OAU-013, OAU-023, OAU-030
used_by: OAU-050, OAU-054, OAU-057, OAU-058
related: OAU-007, OAU-009, OAU-023, OAU-030, OAU-050, OAU-057
tags:
  - architecture
  - oauth
  - authorization-server
  - design
  - keycloak
  - spring-authorization-server
status: complete
version: 5
layout: default
parent: "OAuth 2.0 & OpenID Connect"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/oauth/authorization-server-architecture/
---

⚡ TL;DR - An Authorization Server (AS) is a system boundary
that concentrates authentication, consent, and token issuance
into a single trust anchor for an organization's APIs. Its
internal components: (1) Authentication subsystem (login,
MFA, social login, federation); (2) Client registry (stores
registered clients, their metadata, redirect URIs, allowed
grants); (3) Token service (signs JWTs, manages opaque token
store, handles rotation); (4) Consent engine (records user
grants, displays consent UI); (5) Endpoint layer (/authorize,
/token, /introspect, /revoke, /par, /userinfo); (6) OIDC
discovery (/.well-known/openid-configuration). At scale, each
component has independent scalability and failure profiles.
Token issuance and JWKS endpoints must be highly available -
they are in the critical path of every API call.

---

### 🔥 The Problem This Solves

**AUTHENTICATION SPRAWL WITHOUT A CENTRAL AS:**

Without a central AS, each API reinvents: user login forms,
session management, token issuance, key rotation, consent
tracking, MFA, federation with external IdPs, client
registration. This leads to inconsistent security postures
across services, no single place to revoke a user's access,
no unified audit trail, and no way to enforce policies
(MFA for high-sensitivity APIs, rate limiting on token
requests) consistently. The AS is the security control plane
for all OAuth-protected APIs.

---

### 📘 Textbook Definition

An Authorization Server (RFC 6749 §1.1) is a server that
"authenticates the resource owner and obtains authorization,
issues access tokens to the client after successfully
authenticating the resource owner and obtaining authorization."

**Core responsibilities:**

**1. Client Registry:**
Stores client registrations: `client_id`, authentication
methods, allowed grant types, registered redirect URIs,
allowed scopes, token lifetimes, metadata. May support
dynamic client registration (RFC 7591).

**2. Token Service:**
Issues access tokens (JWT or opaque), refresh tokens,
ID tokens (for OIDC). Handles token signing (RS256, ES256),
key management, rotation. For opaque tokens: stores
token-to-claim mapping in a backend store (Redis, DB).

**3. Authorization/Consent Engine:**
Tracks which users have authorized which scopes for which
clients. Shows consent UI on first access and on scope
changes. Records consent for re-use until revoked.

**4. Authentication Subsystem:**
Handles user authentication: password, MFA, social login,
SAML federation, LDAP. This may be delegated to an
external Identity Provider (IdP) in some architectures.

**5. Endpoint Layer:**
`/authorize` - authorization endpoint
`/token` - token endpoint
`/.well-known/openid-configuration` - OIDC discovery
`/userinfo` - OIDC userinfo endpoint
`/introspect` - token introspection (RFC 7662)
`/revoke` - token revocation (RFC 7009)
`/par` - pushed authorization requests (RFC 9126)
`/jwks` - public key set for token verification

---

### ⏱️ Understand It in 30 Seconds

**The components and data flows:**

```
        EXTERNAL IdPs           CLIENT APPS
              │                      │
              │ SAML/OIDC             │ /authorize
              ▼                      │ /token
    ┌─────────────────────────────────┐
    │    AUTHORIZATION SERVER         │
    │                                 │
    │  [Auth Subsystem]               │
    │   ↕ User login, MFA, SSO        │
    │  [Consent Engine]               │
    │   ↕ User grants, revocations    │
    │  [Client Registry]              │
    │   ↕ Registered clients          │
    │  [Token Service]                │
    │   ↕ Sign JWTs / store opaques   │
    │  [Key Manager]                  │
    │   ↕ Rotate signing keys         │
    └──────────────┬──────────────────┘
                   │ Tokens
                   ▼
    ┌──────────────────────────────┐
    │  JWKS Endpoint (public keys) │
    │  /introspect (opaque tokens) │
    └────────────────┬─────────────┘
                     │
                     ▼
              RESOURCE SERVERS
              (validate tokens)
```

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  AS COMPONENT FAILURE PROFILES & SCALABILITY              │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  COMPONENT      │ FAILOVER MODE  │ SCALE STRATEGY         │
│─────────────────┼────────────────┼────────────────────── │
│ Token issuance  │ Critical (sync)│ Stateless (JWT) →     │
│  (/token)       │                │  horizontal scale     │
│                 │                │  Opaque → Redis        │
│─────────────────┼────────────────┼────────────────────── │
│ JWKS endpoint   │ Critical (sync)│ Cache at CDN/RS       │
│  (/jwks.json)   │ (RS cache helps│  JWKS cacheable 24h   │
│                 │ if AS is down) │                        │
│─────────────────┼────────────────┼────────────────────── │
│ /authorize      │ Non-critical   │ Session affinity       │
│  (browser flow) │ (users retry)  │  or distributed        │
│                 │                │  session store          │
│─────────────────┼────────────────┼────────────────────── │
│ Consent store   │ Degradable     │ DB cluster + cache     │
│                 │ (re-ask consent│                        │
│                 │ on failure)    │                        │
│─────────────────┼────────────────┼────────────────────── │
│ Client registry │ Cacheable      │ DB + in-memory cache   │
│                 │ (low write rate│ (TTL ~5min)            │
│                 │  high read)    │                        │
│─────────────────┼────────────────┼────────────────────── │
│ Auth subsystem  │ Often external │ External IdP           │
│  (login, MFA)   │ (IdP SLA)      │  responsibility        │
│                                                           │
│  KEY INSIGHT: JWT access tokens allow RS to validate      │
│  offline (no AS call per request). This is the primary    │
│  scalability advantage of JWT over opaque tokens.         │
│  JWKS cache at RS = RS works even if AS is briefly down.  │
└──────────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
  C[Client App] --> AZ[/authorize\nAuth + Consent]
  AZ --> AUTH_SS[Authentication\nSubsystem]
  AZ --> CONSENT[Consent Engine\nUser grant storage]
  C --> TK[/token\nToken issuance]
  TK --> TOKEN_SVC[Token Service\nSign JWT / store opaque]
  TK --> CLIENT_REG[Client Registry\nValidate client + redirect_uri]
  TOKEN_SVC --> KEY_MGR[Key Manager\nRS256/ES256 signing keys]
  KEY_MGR --> JWKS[/jwks\nPublic keys for RS]
  TK --> REVOKE[/revoke\nToken invalidation]
  TK --> INTROSPECT[/introspect\nOpaque token info]
  AZ --> DISCOVER[/.well-known/openid-configuration\nAS metadata]

  RS[Resource Servers] --> JWKS
  RS --> INTROSPECT
```

---

### 💻 Code Example

**Example 1 - Spring Authorization Server: minimal setup:**

```java
// Spring Authorization Server 1.x - registered client config
// The client registry is the core of the AS configuration

@Configuration
public class AuthorizationServerConfig {

    @Bean
    public RegisteredClientRepository clientRepository() {
        RegisteredClient webapp = RegisteredClient
            .withId(UUID.randomUUID().toString())
            .clientId("my-webapp")
            .clientSecret(
                "{bcrypt}" + new BCryptPasswordEncoder()
                    .encode("client-secret-from-vault")
            )
            .clientAuthenticationMethod(
                ClientAuthenticationMethod.CLIENT_SECRET_BASIC
            )
            .authorizationGrantType(
                AuthorizationGrantType.AUTHORIZATION_CODE
            )
            .authorizationGrantType(
                AuthorizationGrantType.REFRESH_TOKEN
            )
            .redirectUri(
                "https://app.example.com/callback"
            )
            .scope(OidcScopes.OPENID)
            .scope("read:accounts")
            .scope("write:accounts")
            .tokenSettings(TokenSettings.builder()
                .accessTokenTimeToLive(Duration.ofMinutes(15))
                .refreshTokenTimeToLive(Duration.ofDays(7))
                .reuseRefreshTokens(false)   // Enable RTR
                .authorizationCodeTimeToLive(
                    Duration.ofMinutes(5)
                )
                .build()
            )
            .clientSettings(ClientSettings.builder()
                .requireAuthorizationConsent(true)
                .requireProofKey(true)  // Require PKCE
                .build()
            )
            .build();

        RegisteredClient serviceClient = RegisteredClient
            .withId(UUID.randomUUID().toString())
            .clientId("my-service")
            .clientSecret(/* from vault */)
            .clientAuthenticationMethod(
                ClientAuthenticationMethod.CLIENT_SECRET_BASIC
            )
            .authorizationGrantType(
                AuthorizationGrantType.CLIENT_CREDENTIALS
            )
            .scope("read:internal-data")
            .tokenSettings(TokenSettings.builder()
                .accessTokenTimeToLive(Duration.ofMinutes(15))
                .build()
            )
            .build();

        // Production: use JdbcRegisteredClientRepository
        // not InMemoryRegisteredClientRepository
        return new InMemoryRegisteredClientRepository(
            webapp, serviceClient
        );
    }

    @Bean
    public JWKSource<SecurityContext> jwkSource() {
        // Keys managed here - rotated periodically
        RSAKey rsaKey = Jwks.generateRsa();
        JWKSet jwkSet = new JWKSet(rsaKey);
        return (selector, context) ->
            selector.select(jwkSet);
    }

    @Bean
    public AuthorizationServerSettings authSettings() {
        return AuthorizationServerSettings.builder()
            // All endpoint URLs configured here
            .issuer("https://as.example.com")
            .authorizationEndpoint("/authorize")
            .tokenEndpoint("/token")
            .jwkSetEndpoint("/jwks")
            .tokenRevocationEndpoint("/revoke")
            .tokenIntrospectionEndpoint("/introspect")
            .oidcUserInfoEndpoint("/userinfo")
            .build();
    }
}
```

**Example 2 - Custom claims in JWT tokens (token customizer):**

```java
// Spring Authorization Server: add custom claims to AT/ID token

@Bean
public OAuth2TokenCustomizer<JwtEncodingContext> tokenCustomizer(
    UserService userService
) {
    return (context) -> {
        // Customize access tokens
        if (OAuth2TokenType.ACCESS_TOKEN.equals(
                context.getTokenType())) {

            String username = context.getPrincipal()
                .getName();
            UserDetails user = userService.loadUser(username);

            context.getClaims()
                // Add custom claims used by resource servers
                .claim("user_id", user.getId())
                .claim("tenant_id", user.getTenantId())
                .claim("roles", user.getRoles())
                // Add audience explicitly (RFC 9068)
                .audience(List.of(
                    "https://api.example.com"
                ));
        }

        // Customize ID tokens
        if (OidcParameterNames.ID_TOKEN.equals(
                context.getTokenType().getValue())) {
            String nonce = (String) context
                .getAuthorizationRequest()
                .getAdditionalParameters()
                .get("nonce");
            if (nonce != null) {
                context.getClaims().claim("nonce", nonce);
            }
        }
    };
}
```

---

### ⚖️ Comparison Table

| AS Choice | Self-Hosted vs. Cloud | Scale | Customization | Key Limitation |
|---|---|---|---|---|
| **Keycloak** | Self-hosted | Horizontal (stateless mode) | High (SPIs, themes) | Operational overhead |
| **Spring Authorization Server** | Self-hosted (embedded) | Horizontal | Highest (code-level) | Build and maintain yourself |
| **Auth0** | Cloud SaaS | Fully managed | Medium (Actions) | Vendor dependency |
| **Okta** | Cloud SaaS | Fully managed | Medium | Cost at scale |
| **AWS Cognito** | Cloud SaaS | Managed | Low | Limited flows |
| **Dex / Hydra** | Self-hosted | Horizontal | Moderate | Integration effort |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The AS must be available for every API call | With JWT access tokens, the RS validates tokens offline using the cached JWKS public keys. The AS only needs to be available for token issuance (login, refresh). If the AS goes down briefly, existing valid JWT ATs continue to work at all RSes. This is the key scalability property of JWT: the AS is out of the hot path for token validation. Opaque tokens do require the AS to be available for every call (introspection). |
| Keycloak or Auth0 can be configured to satisfy all requirements without customization | Every organization eventually hits the "custom claims" wall: you need user attributes, tenant IDs, or custom authorization data in the token that the AS doesn't know about by default. Most AS products support some form of token customization (Keycloak SPIs, Auth0 Actions, Spring token customizers), but this almost always requires code. Plan for token customization from the start. |
| Authorization and authentication are the same subsystem | Many AS products conflate them, but they are logically separate. Authentication = who is the user (identity). Authorization = what can they do (grants, consents, scopes). Separating them architecturally means authentication can be delegated to an external IdP (corporate LDAP, social providers) while authorization logic remains in the AS. OIDC provides the bridge: authentication result becomes an ID token, then authorization grants AT to access APIs. |
| Token signing keys should never change | Key rotation is mandatory security practice. RSA keys should be rotated at least annually (some compliance frameworks require quarterly). The AS must publish multiple active signing keys in JWKS (current + recent) to avoid 401 errors during rotation when some RSes have cached the old key set. RS should cache JWKS with a max-age and re-fetch on validation failure (unknown kid). |

---

### 🚨 Failure Modes & Diagnosis

**JWKS Cache Stale After Key Rotation**

**Symptom:**
After rotating signing keys on the AS, a subset of API calls
return 401 "invalid signature" for newly issued tokens.
The issue resolves itself after 5-15 minutes.

**Root Cause:**
Resource servers cached the old JWKS (public keys). After
key rotation, the AS issues new tokens signed with the new
key. RSes with stale JWKS cache fail signature verification
because the new key's `kid` (key ID) isn't in their cached
key set.

**Fix:**
1. RS: on JWT signature verification failure with unknown `kid`,
   re-fetch JWKS immediately (bypass cache). Retry validation.
2. AS: keep the old key in JWKS for at least 2x the JWKS
   cache TTL after rotation. Never remove a key from JWKS
   while tokens signed by it might still be valid.
3. Monitor: alert on elevated 401 rates after any key rotation
   event. Key rotation should be a zero-downtime operation.

```python
# RS: JWKS cache with forced refresh on unknown kid
from cachetools import TTLCache

_jwks_cache = TTLCache(maxsize=1, ttl=3600)

def get_signing_key(token: str):
    header = jwt.get_unverified_header(token)
    kid = header.get('kid')

    keys = _jwks_cache.get('keys')
    if keys is None:
        keys = fetch_jwks()
        _jwks_cache['keys'] = keys

    key = keys.get(kid)
    if key is None:
        # Unknown kid: force refresh (key rotation case)
        keys = fetch_jwks()
        _jwks_cache['keys'] = keys
        key = keys.get(kid)

    if key is None:
        raise ValueError(f"Unknown signing key: {kid}")
    return key
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authorization Code Flow` - primary browser-based flow
- `Client Credentials Grant` - service-to-service flow

**Builds On:**
- `Authorization Server Clustering` - HA and scaling
- `JWKS and Public Key Discovery` - key management detail
- `Authorization Server Metadata Discovery` - discovery endpoint

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE         │ Auth, Consent, Client Registry,           │
│ COMPONENTS   │ Token Service, Key Manager, Endpoints     │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ /token, /jwks: must be HA                 │
│ ENDPOINTS    │ /authorize: degradable (user retries)     │
├──────────────┼───────────────────────────────────────────┤
│ JWT AT SCALE │ RS validates offline → AS out of hot path │
│              │ Opaque AT → introspection per API call    │
├──────────────┼───────────────────────────────────────────┤
│ KEY          │ Rotate annually (min). Multiple keys in   │
│ ROTATION     │ JWKS. RS: re-fetch on unknown kid.        │
├──────────────┼───────────────────────────────────────────┤
│ CHOOSE AS    │ Self-hosted: Keycloak / Spring Auth Server│
│              │ SaaS: Auth0, Okta. Embedded: Spring.      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "AS = trust anchor. JWT AT = offline      │
│              │  validation. JWKS = RS key distribution." │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The AS concentrates auth, consent, and token issuance.
   Its critical components are the token service and JWKS
   endpoint - these are in the critical path of every login.
   The /authorize endpoint is more forgiving (users retry).

2. JWT access tokens allow resource servers to validate
   offline using cached JWKS public keys. The AS is NOT in
   the hot path for every API call - only for token issuance
   and refresh. This is why JWT AT scales better than opaque.

3. Key rotation is mandatory. Keep the old key in JWKS for
   2x the cache TTL after rotation. RSes must re-fetch JWKS
   on unknown `kid` to handle rotation gracefully.
