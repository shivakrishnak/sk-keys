---
id: ATH-041
title: "Kerberos Protocol"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-040
used_by: ATH-042, ATH-056
related: ATH-040, ATH-042, ATH-056
tags:
  - security
  - authentication
  - kerberos
  - enterprise
  - tickets
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/authentication/kerberos-protocol/
---

⚡ **TL;DR** - Kerberos is the authentication protocol powering
Windows Active Directory. It uses tickets: the user authenticates
once to the Key Distribution Center (KDC), receives a Ticket
Granting Ticket (TGT), then exchanges it for service-specific
tickets without re-entering credentials (single sign-on). Passwords
are never transmitted - only keys derived from the password. The
attack: Kerberoasting extracts service ticket hashes and cracks
them offline. Mitigation: use strong, long, random passwords for
service accounts (they generate the crackable hashes).

---

### 📊 Entry Metadata

| #041 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-040 Certificate Auth | |
| **Used by:** | ATH-042, ATH-056 | |
| **Related:** | ATH-040 Certificate Auth, ATH-042 LDAP, ATH-056 Enterprise Architecture | |

---

### 📘 Textbook Definition

Kerberos (MIT, 1980s; RFC 4120) is a network authentication
protocol using symmetric-key cryptography and a trusted third
party (the Key Distribution Center, KDC). The KDC has two
components: the Authentication Server (AS) and the Ticket
Granting Server (TGS). Authentication is ticket-based: the user
receives a Ticket Granting Ticket (TGT) from the AS after
initial authentication; the TGT is then used to obtain service
tickets from the TGS without re-entering credentials. Service
tickets are encrypted with the service's long-term key and
presented by the client directly to the service for
authentication.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            Kerberos Authentication Flow                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Client -> AS: "I am alice" (plaintext)             │
│  2. AS -> Client:                                      │
│     - Session key, encrypted with alice's password key │
│     - TGT, encrypted with KDC's secret key             │
│  3. Client decrypts session key with alice's password  │
│     (client never receives its own password key)       │
│                                                        │
│  4. Client -> TGS:                                     │
│     - TGT (opaque to client, encrypted for KDC)        │
│     - Authenticator: {alice, timestamp}               │
│       encrypted with session key                       │
│     - Service requested: HTTP/web.corp.com             │
│  5. TGS: validates TGT, returns service ticket         │
│     encrypted with web.corp.com's secret key           │
│                                                        │
│  6. Client -> web.corp.com:                            │
│     - Service ticket (encrypted for web.corp.com)      │
│  7. web.corp.com: decrypts ticket, verifies alice      │
│     Authentication complete without password sent      │
│                                                        │
│  ATTACK: Kerberoasting                                 │
│  Any authenticated user can request a service ticket   │
│  for any registered service (encrypted with svc key)   │
│  Attacker: request ticket, extract hash, crack offline │
│  Mitigation: managed service accounts with 120-char    │
│  random passwords (uncrackable in practice)            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Detecting Kerberoasting in Active Directory**

```powershell
# Detect service accounts with weak SPNs (Kerberoasting targets)
# Run as Domain Admin:
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} `
    -Properties ServicePrincipalName, PasswordLastSet,
    PasswordNeverExpires |
    Where-Object { $_.PasswordNeverExpires -eq $true } |
    Select-Object SamAccountName, ServicePrincipalName,
        PasswordLastSet, PasswordNeverExpires |
    Export-Csv kerberoastable_accounts.csv

# Remediation: convert vulnerable accounts to Managed
# Service Accounts (MSA) or Group Managed Service Accounts
# (gMSA) - these have 240-character auto-rotating passwords
# that are computationally infeasible to crack
New-ADServiceAccount -Name "web-service-gMSA" `
    -DNSHostName "web.corp.com" `
    -PrincipalsAllowedToRetrieveManagedPassword "Web-Servers"
```

**Example - Java service authenticating via Kerberos (SPNEGO)**

```java
// SPNEGO = HTTP negotiation mechanism for Kerberos
// Allows web services to use Kerberos auth transparently
@Configuration
@EnableWebSecurity
public class KerberosSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            )
            .addFilterBefore(
                spnegoAuthenticationProcessingFilter(),
                BasicAuthenticationFilter.class
            );
        return http.build();
    }

    @Bean
    public SpnegoAuthenticationProcessingFilter
            spnegoAuthenticationProcessingFilter() {
        SpnegoAuthenticationProcessingFilter filter =
            new SpnegoAuthenticationProcessingFilter();
        filter.setAuthenticationManager(
            authenticationManager());
        return filter;
    }
}
// Clients with valid Kerberos TGT authenticate
// transparently (browser sends Negotiate token)
```

---

*Authentication category: ATH | Entry: ATH-041 | v5.0*