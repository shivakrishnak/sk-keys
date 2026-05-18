---
id: ATH-012
title: "Multi-Factor Authentication (MFA) Basics"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-003, ATH-006
used_by: ATH-013, ATH-027, ATH-028, ATH-029, ATH-036
related: ATH-003, ATH-013, ATH-036
tags:
  - security
  - authentication
  - mfa
  - 2fa
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/authentication/multi-factor-authentication-mfa-basics/
---

⚡ **TL;DR** - Multi-Factor Authentication requires a user to present
proof from two or more distinct factor categories: something you know
(password), something you have (phone, hardware key), or something
you are (biometrics). A password alone can be stolen without physical
access. MFA requires stealing both the password AND physical control
of the second factor - a dramatically higher attack cost. Most account
takeovers use stolen passwords; MFA blocks ~99% of them.

---

### 📊 Entry Metadata

| #012 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-003, ATH-006 | |
| **Used by:** | ATH-013, ATH-027, ATH-028, ATH-029, ATH-036 | |
| **Related:** | ATH-003 Three Factors, ATH-013 TOTP, ATH-036 Phishing-Resistant MFA | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Password databases leak constantly. Credential stuffing
attacks try leaked passwords against other services.
Phishing tricks users into entering passwords on fake sites.
Malware steals passwords from browser keystores. A password
is a secret that can be stolen remotely, silently, and at
scale. Once stolen, it provides full account access until
someone notices.

MFA makes a stolen password insufficient. The attacker
also needs the TOTP code (valid 30 seconds), or the SMS
code (sent to the user's phone), or the hardware key
(physically in the user's pocket). Most attacks operate
at scale remotely; MFA forces either a near-real-time
phishing attack or physical theft.

**GOOGLE'S FINDING (2019):**

MFA blocks: 100% of automated bot attacks, 96% of bulk
phishing attacks, 76% of targeted attacks (for TOTP).
Hardware keys (FIDO2): 100% across all three categories.

---

### 📘 Textbook Definition

Multi-Factor Authentication (MFA), also called Two-Factor
Authentication (2FA) when exactly two factors are used,
requires authentication using credentials from two or more
distinct factor categories. The three NIST-defined categories
are: knowledge factors (something you know: password, PIN),
possession factors (something you have: TOTP app, SMS, hardware
key), and inherence factors (something you are: fingerprint,
face, voice). Using two factors from the same category
(password + security question) is not true MFA.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One factor can be stolen remotely. Two factors from different
categories requires both a remote theft AND physical control.

**The factor categories:**

```
KNOW:  Password, PIN, security answers
HAVE:  TOTP app (Authenticator), SMS, hardware key
ARE:   Fingerprint, Face ID, voice print

MFA = at least two from different categories
  Password (KNOW) + TOTP code (HAVE) = MFA ✓
  Password (KNOW) + PIN (KNOW) = NOT MFA (same category)
  Password (KNOW) + Face ID (ARE) = MFA ✓
```

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              MFA Authentication Flow                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STEP 1: First Factor (Knowledge)                      │
│  User: alice@company.com / password1234                │
│  Server: credential correct → PARTIAL auth             │
│          (session marked: mfa_pending)                 │
│          → prompt for second factor                    │
│                                                        │
│  STEP 2: Second Factor (Possession)                    │
│  User: opens Authenticator app → copies 6-digit code  │
│        enters: 847291                                  │
│  Server: verify TOTP code against user's secret        │
│          code valid + not yet used → FULL auth         │
│          → issue session / access token                │
│                                                        │
│  ATTACKER WITH STOLEN PASSWORD:                        │
│  Step 1: correct (attacker has password)               │
│  Step 2: fails (attacker does not have phone)          │
│          → authentication blocked                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**MFA method comparison:**

| Method | Phishing resistant | No phone needed | UX friction |
|---|---|---|---|
| TOTP (Authenticator app) | No | Yes | Medium |
| SMS OTP | No | No | Low |
| Email OTP | No | No | Medium |
| Hardware key (FIDO2) | **Yes** | Yes | Low |
| Push notification | No | No | Very low |
| Passkey | **Yes** | Yes (device) | Very low |

---

### 💻 Code Examples

**Example - MFA flow in Spring Security (two-step)**

```java
@Controller
public class AuthController {

    // STEP 1: Verify password, redirect to MFA step
    @PostMapping("/login")
    public String login(@RequestParam String email,
                        @RequestParam String password,
                        HttpSession session) {
        User user = userService.authenticate(email, password);
        if (user == null) {
            return "redirect:/login?error";
        }
        // Mark session as pending MFA
        session.setAttribute("mfa_pending_user", user.getId());
        // Redirect to second factor prompt
        return "redirect:/login/mfa";
    }

    // STEP 2: Verify TOTP code, complete authentication
    @PostMapping("/login/mfa")
    public String verifyMfa(@RequestParam String totpCode,
                            HttpSession session) {
        Long userId = (Long) session.getAttribute(
            "mfa_pending_user");
        if (userId == null) {
            return "redirect:/login"; // session expired
        }
        if (!totpService.verify(userId, totpCode)) {
            return "redirect:/login/mfa?error";
        }
        // Both factors verified: establish full session
        session.removeAttribute("mfa_pending_user");
        session.setAttribute("authenticated_user", userId);
        return "redirect:/dashboard";
    }
}
```

**Example - FAILURE: MFA bypass via account recovery**

```
Attack:
  1. Attacker has victim's email + password (stolen/phished)
  2. Login requires TOTP (attacker does not have phone)
  3. Attacker clicks "Forgot password?" instead of MFA step
  4. Password reset goes to victim's email
  5. Attacker uses email account access (from same breach)
     to complete password reset
  6. New password set → new login → no MFA challenge for
     password reset flow → account compromised

Fix:
  Password reset MUST require MFA verification
  (or backup codes), not bypass it.
  Recovery codes must be displayed at enrollment and
  treated as high-value secrets.
  Email-based recovery should still require a second signal
  (device trust, SMS to different channel) when MFA is enrolled.
```

---

*Authentication category: ATH | Entry: ATH-012 | v5.0*