---
id: ATH-032
title: "Refresh Token Patterns in Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-010, ATH-031
used_by: ATH-033, ATH-045, ATH-046, ATH-054
related: ATH-010, ATH-031, ATH-033
tags:
  - security
  - authentication
  - refresh-token
  - token-rotation
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/authentication/refresh-token-patterns-in-authentication/
---

⚡ **TL;DR** - Refresh tokens extend authentication sessions without
requiring re-login. They are long-lived (days to weeks), while access
tokens are short-lived (minutes to hours). The security model: short
access tokens limit the blast radius of token theft; refresh tokens
must be treated as session credentials. The critical pattern is
refresh token rotation: every use of a refresh token issues a new one
and invalidates the old. Detecting reuse of an invalidated refresh
token indicates token theft - invalidate the entire family.

---

### 📊 Entry Metadata

| #032 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-010 Token Auth, ATH-031 Bearer Tokens | |
| **Used by:** | ATH-033, ATH-045, ATH-046, ATH-054 | |
| **Related:** | ATH-010 Tokens, ATH-031 Bearer, ATH-033 PKCE | |

---

### 📘 Textbook Definition

Refresh tokens are long-lived credentials used to obtain new
access tokens without requiring user re-authentication. An
access token is short-lived (15 min - 1 hour) to limit
exposure if stolen; when it expires, the client presents the
refresh token to the authorization server's token endpoint
to receive a new access token (and optionally a new refresh
token). Refresh token rotation (RFC 6749 security best
practices) requires that each use of a refresh token issues
a new refresh token and invalidates the previous one. If a
previously-used refresh token is presented again (indicating
theft or a racing condition), the entire token family is revoked.

---

### ⚙️ How It Works (Mechanism)

**Token family and refresh rotation:**

```
┌────────────────────────────────────────────────────────┐
│         Refresh Token Rotation Security                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Normal flow:                                          │
│  Login -> RT1, AT1 (expires 15min)                     │
│  AT1 expires -> use RT1 -> RT2, AT2, RT1 invalidated   │
│  AT2 expires -> use RT2 -> RT3, AT3, RT2 invalidated   │
│                                                        │
│  Token theft detection:                                │
│  Attacker steals RT2                                   │
│  Legit client: uses RT2 -> RT3, AT3                    │
│  Attacker: uses RT2 again (it was already used)        │
│  Server: RT2 was already redeemed AND RT3 was issued   │
│    -> This means RT2 was stolen after redemption       │
│    -> Revoke ENTIRE token family (RT1, RT2, RT3, AT3)  │
│    -> Force re-authentication                          │
│                                                        │
│  STORAGE:                                              │
│  Web: httpOnly, Secure, SameSite=Strict cookie         │
│  Mobile: platform secure enclave / keychain            │
│  Server (server-side rendered): session-backed         │
│  SPA: tricky - avoid localStorage (XSS risk)           │
│        use httpOnly cookie from auth server            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Refresh token rotation with family revocation**

```java
@Service
@Transactional
public class RefreshTokenService {

    public TokenPair refreshTokens(String presentedToken) {
        String tokenHash = sha256Hex(presentedToken);
        RefreshToken stored = refreshTokenRepo
            .findByTokenHash(tokenHash)
            .orElseThrow(InvalidTokenException::new);

        if (stored.isRevoked()) {
            // Token reuse detected: this RT was already used
            // Entire family compromised - revoke all
            refreshTokenRepo
                .revokeFamily(stored.getFamilyId());
            throw new TokenTheftDetectedException(
                "Token reuse detected - session invalidated");
        }

        if (stored.isExpired()) {
            throw new TokenExpiredException();
        }

        // Revoke the used token
        stored.setRevoked(true);
        refreshTokenRepo.save(stored);

        // Issue new token (same family)
        String newRaw = generateSecureToken();
        RefreshToken newToken = new RefreshToken(
            sha256Hex(newRaw),
            stored.getUserId(),
            stored.getFamilyId(), // same family
            Instant.now().plus(30, ChronoUnit.DAYS));
        refreshTokenRepo.save(newToken);

        String newAccessToken = jwtService.issue(
            stored.getUserId());
        return new TokenPair(newRaw, newAccessToken);
    }
}
```

---

*Authentication category: ATH | Entry: ATH-032 | v5.0*