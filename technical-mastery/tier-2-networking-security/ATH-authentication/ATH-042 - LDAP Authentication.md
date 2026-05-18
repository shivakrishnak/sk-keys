---
id: ATH-042
title: "LDAP Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-041
used_by: ATH-056
related: ATH-041, ATH-056
tags:
  - security
  - authentication
  - ldap
  - enterprise
  - active-directory
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/authentication/ldap-authentication/
---

⚡ **TL;DR** - LDAP (Lightweight Directory Access Protocol) is the
protocol for querying and authenticating against directory services
like Active Directory and OpenLDAP. Authentication is a "bind"
operation: send username + password to the LDAP server, which
validates and returns success/failure. Always use LDAPS (LDAP over
TLS) or StartTLS - plain LDAP transmits credentials in cleartext.
The top security risk: LDAP injection (user input in search filters
without escaping) allows enumeration of all users and groups.

---

### 📊 Entry Metadata

| #042 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-041 Kerberos | |
| **Used by:** | ATH-056 | |
| **Related:** | ATH-041 Kerberos, ATH-056 Enterprise Architecture | |

---

### 📘 Textbook Definition

LDAP (RFC 4511) is a protocol for accessing and maintaining
distributed directory information services. In authentication
contexts, LDAP is used to validate credentials via the "bind"
operation: a client sends a Distinguished Name (DN) and
password; the LDAP server validates and returns a success or
failure code. LDAP directories (Active Directory, OpenLDAP,
389 Directory Server) store user accounts, group memberships,
and organizational hierarchies. After authentication, LDAP
searches retrieve group membership to populate user roles.
Security requirements: use TLS (LDAPS on port 636 or StartTLS
on 389), use a service account bind DN with read-only access,
escape all user-supplied input in LDAP search filters.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            LDAP Authentication Flow                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. App: connect to LDAP server (port 636 LDAPS)       │
│  2. App: bind with service account                     │
│     DN: cn=ldap-svc,ou=service,dc=corp,dc=com          │
│     Password: (read-only service account)              │
│  3. App: search for user by email:                     │
│     filter: (&(objectClass=person)                     │
│               (mail=alice@corp.com))                   │
│     Result: CN=Alice Smith,OU=Finance,DC=corp,DC=com   │
│                                                        │
│  4. App: bind with user's DN + entered password        │
│     DN: CN=Alice Smith,OU=Finance,DC=corp,DC=com       │
│     Password: <what alice typed>                       │
│  5. If bind succeeds: alice is authenticated           │
│  6. App: search alice's group memberships              │
│     filter: (member=CN=Alice Smith,OU=Finance,...)     │
│     Result: [Finance-All, Reports-Readers, VPN-Users]  │
│  7. Map groups to application roles                    │
│                                                        │
│  LDAP INJECTION:                                       │
│  Input: alice)(uid=*))(|(uid=*                         │
│  Filter becomes: (&(uid=alice)(uid=*))(|(uid=*)(pw=X)) │
│  This returns ALL users - enumeration attack           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring LDAP authentication with injection prevention**

```java
@Configuration
@EnableWebSecurity
public class LdapSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            )
            .formLogin(Customizer.withDefaults());
        return http.build();
    }

    @Bean
    public LdapAuthenticationProvider ldapAuthProvider() {
        BindAuthenticator authenticator =
            new BindAuthenticator(contextSource());
        // {0} is replaced with the filtered/escaped
        // username - Spring LDAP escapes it automatically
        authenticator.setUserDnPatterns(new String[]{
            "cn={0},ou=users,dc=corp,dc=com"
        });

        DefaultLdapAuthoritiesPopulator populator =
            new DefaultLdapAuthoritiesPopulator(
                contextSource(),
                "ou=groups,dc=corp,dc=com");
        populator.setGroupRoleAttribute("cn");
        populator.setGroupSearchFilter(
            "(member={0})");

        return new LdapAuthenticationProvider(
            authenticator, populator);
    }

    @Bean
    public DefaultSpringSecurityContextSource contextSource() {
        DefaultSpringSecurityContextSource ctx =
            new DefaultSpringSecurityContextSource(
                "ldaps://ad.corp.com:636/dc=corp,dc=com");
        ctx.setUserDn("cn=ldap-svc,ou=svc,dc=corp,dc=com");
        ctx.setPassword(ldapServicePassword);
        return ctx;
    }
}
```

**Example - BAD: LDAP injection via unescaped username**

```java
// BAD: string concatenation in LDAP filter
String username = request.getParameter("username");
String filter = "(&(uid=" + username
    + ")(objectClass=person))";
// If username = "admin)(uid=*))(|(uid=*"
// Filter: (&(uid=admin)(uid=*))(|(uid=*))(objectClass=p))
// Returns ALL users. Password check bypassed.

// GOOD: use Spring LDAP which escapes filter values,
// or manually escape with LdapEncoder.filterEncode()
String safeUsername = LdapEncoder.filterEncode(username);
String filter = "(&(uid=" + safeUsername
    + ")(objectClass=person))";
```

---

*Authentication category: ATH | Entry: ATH-042 | v5.0*