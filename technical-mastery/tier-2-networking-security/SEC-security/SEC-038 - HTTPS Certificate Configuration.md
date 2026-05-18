---
id: SEC-038
title: "HTTPS Certificate Configuration"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-004, SEC-005, SEC-006, SEC-007, SEC-014, SEC-016
used_by: SEC-039, SEC-067, SEC-079, SEC-090
related: SEC-004, SEC-005, SEC-006, SEC-007, SEC-014, SEC-016, SEC-079, SEC-090
tags:
  - security
  - https
  - tls
  - certificates
  - hsts
  - ssl
  - nginx
  - letsencrypt
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/sec/https-certificate-configuration/
---

⚡ TL;DR - HTTPS = HTTP over TLS. Proper HTTPS configuration
requires: correct TLS version (1.2+, 1.3 preferred), secure
cipher suites, valid certificate chain, and HSTS header.

**Minimum viable HTTPS configuration:**
- Disable TLS 1.0 and TLS 1.1 (deprecated, known attacks)
- Enable TLS 1.2 and TLS 1.3
- Cipher suites: ECDHE forward secrecy + AES-GCM authenticated encryption
- Valid certificate from trusted CA (Let's Encrypt is free, auto-renewable)
- HSTS header: `Strict-Transport-Security: max-age=31536000`
  (tells browsers: this domain is HTTPS-only for 1 year)
- Test with: `testssl.sh` (CLI), SSL Labs (web)

**Common misconfigurations:**
- Allowing HTTP alongside HTTPS without redirect
- Incomplete certificate chain (intermediate CAs missing)
- Expired certificate (clients see warnings, may not connect)
- TLS 1.0/1.1 still enabled (downgrade attack surface)
- Weak cipher suites (RC4, DES, 3DES, anonymous DH)
- Self-signed certificate in production (client trust error)

---

| #038 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | TLS/SSL, X.509 Certificates, PKI, Cipher Suites, CA, HTTPS | |
| **Used by:** | Session Security, CORS, TLS Config Best Practices, TLS Protocol Attacks | |
| **Related:** | TLS, PKI, HSTS, Certificate Pinning, TLS 1.3 Design | |

---

### 🔥 The Problem This Solves

**PLAINTEXT HTTP IS UNACCEPTABLE:**
Without HTTPS, every request and response is plaintext over
the network. Coffee shop Wi-Fi: the access point operator
sees every username/password, every session cookie, every
page you load. ISPs can log all HTTP traffic. Any network
hop (router, proxy) can read and modify responses. A "coffee
shop attack" injects advertising or malware into HTTP pages.
Password entered on HTTP = password visible to network.

**MISCONFIGURED HTTPS IS ALMOST AS BAD:**
A certificate that has expired = users see browser warnings
and many bypass them (training users to ignore security warnings).
TLS 1.0 enabled = POODLE/BEAST downgrade attacks possible.
Weak cipher suites = key exchange breakable with modern hardware.
Missing HSTS = SSL stripping attacks redirect HTTP→HTTPS
traffic before reaching the server. Mixed content (HTTPS page
loading HTTP resources) = those resources can be intercepted.

**CERTIFICATE EXPIRY IS A COMMON PRODUCTION INCIDENT:**
Certificate expiry is one of the top causes of unexpected
outages. When a certificate expires: browser refuses connection.
API clients fail with TLS errors. Users see "Your connection
is not private" and cannot proceed. Automate renewal
(Let's Encrypt + certbot) and set calendar reminders 60 days
before expiry as backup.

---

### 📘 Textbook Definition

**TLS (Transport Layer Security):** A cryptographic protocol
that provides authenticated, encrypted communication over
a network. HTTPS = HTTP over TLS. Current versions: TLS 1.2
(widely deployed), TLS 1.3 (current best practice).
Deprecated: SSL (all versions), TLS 1.0, TLS 1.1.

**X.509 Certificate:** A digital document that binds a public
key to an entity (domain name, organization). Contains:
subject (who this cert is for), issuer (CA that signed it),
validity period (not-before, not-after), public key, and
signature from issuer. When a browser connects to example.com:
it receives the server's certificate, verifies the CA signature,
and checks that the cert is for `example.com` and is not expired.

**Certificate Authority (CA):** A trusted third party that
signs certificates after verifying the applicant's identity.
Types:
- **DV (Domain Validated):** Proves you control the domain.
  Let's Encrypt, most certificates. Valid for: encryption.
  No proof of who the organization is.
- **OV (Organization Validated):** Proves the legal organization
  identity. More expensive, more validation.
- **EV (Extended Validation):** Highest validation, once
  showed green bar in browsers. Modern browsers deprecated
  EV indicators - minimal practical difference today.

**Certificate Chain:** Certificates form a chain.
Server cert → Intermediate CA cert → Root CA cert.
Browsers trust Root CAs (pre-installed). Server must send
the full chain (server + intermediate) for browsers to verify.
If intermediate is missing: some clients fail ("incomplete chain").

**HSTS (HTTP Strict Transport Security):**
Response header: `Strict-Transport-Security: max-age=31536000`
When a browser receives this: it stores the policy for `max-age`
seconds. For any future request to this domain: the browser
forces HTTPS, even if the user types `http://`. Prevents
SSL stripping attacks (where an attacker intercepts HTTP→HTTPS
redirect and serves HTTP). `includeSubDomains` extends policy to
all subdomains. `preload` submits the domain to HSTS preload
list (browsers hardcode these domains as HTTPS-only before
first contact).

**OCSP Stapling:** Server fetches a signed "this certificate
is valid" response from the CA (OCSP responder) and includes
("staples") it in the TLS handshake. Client doesn't need a
separate OCSP request. Faster TLS handshake + no privacy
leakage (OCSP checks would tell CA which sites clients visit).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Proper HTTPS requires: TLS 1.2+, ECDHE cipher suites,
valid certificate chain, HSTS header, HTTP→HTTPS redirect.
Use testssl.sh or SSL Labs to verify. Let's Encrypt for free
automated certificates.

**One analogy:**
> HTTPS is like a sealed, tamper-evident courier envelope.
> HTTP is like a postcard - anyone who handles it reads it.
> TLS version selection is choosing the material: TLS 1.0/1.1
> envelopes have known weaknesses (easy to open and reseal).
> TLS 1.3 envelopes have the strongest material (perfect
> forward secrecy: even if the private key is later stolen,
> past traffic cannot be decrypted). HSTS is telling the
> courier company: "I only ever use sealed envelopes for
> communications with me; refuse any postcards on my behalf."
> Certificate validation is verifying the courier is who
> they say they are (not an impostor intercepting deliveries).

---

### 🔩 First Principles Explanation

**TLS 1.2 vs TLS 1.3 - what changed and why:**

```
TLS HANDSHAKE COMPARISON:

TLS 1.2 HANDSHAKE (2 round trips):

  Client → Server:  ClientHello
    - Supported TLS versions
    - Supported cipher suites (list of options)
    - Random value (client_random)
    
  Server → Client:  ServerHello + Certificate + ServerHelloDone
    - Selected TLS version
    - Selected cipher suite
    - Server's certificate (with public key)
    - Server random
    
  Client → Server:  ClientKeyExchange + ChangeCipherSpec + Finished
    - Key exchange data (depends on cipher suite)
    - "Now encrypting" signal
    - Encrypted Finished message
    
  Server → Client:  ChangeCipherSpec + Finished
    - "Now encrypting" signal
    - Encrypted Finished
    
  Total: 2 round trips before data transfer begins.
  Weak cipher support: RSA key exchange (no forward secrecy),
    RC4, 3DES, MD5, SHA-1 (all now forbidden in best-practice configs)

TLS 1.3 HANDSHAKE (1 round trip):

  Client → Server:  ClientHello
    - Only TLS 1.3 (no version negotiation downgrade)
    - Key share (ECDHE parameters pre-sent in first message)
    - Supported groups
    
  Server → Client:  ServerHello + EncryptedExtensions 
                    + Certificate + CertificateVerify + Finished
    - Everything encrypted starting here
    - Server's key share
    - Certificate (now encrypted!)
    
  Client → Server:  Finished + Data
    - Client now has enough to compute session key
    - Data can start in same flight as Finished
    
  Total: 1 round trip before data (vs 2 for TLS 1.2).
  
  TLS 1.3 IMPROVEMENTS:
  - Removed: RSA key exchange, RC4, 3DES, MD5, SHA-1 (all gone)
  - Required: ECDHE (forward secrecy built-in, not optional)
  - Encrypted handshake: certificate is encrypted
    (observer can't see what cert server sends)
  - 0-RTT resumption: subsequent connections can send data
    in the first message (0 round trips for resumed sessions)
    Caveat: 0-RTT is vulnerable to replay attacks for
    non-idempotent requests. Disable 0-RTT for POST endpoints.

FORWARD SECRECY (why ECDHE is required):

  WITHOUT FORWARD SECRECY (RSA key exchange):
    - Session key encrypted with server's long-term private key
    - If private key is later stolen: all past recorded traffic
      can be decrypted (retroactive decryption)
    - Nation-state adversaries record TLS traffic to decrypt later
    
  WITH FORWARD SECRECY (ECDHE):
    - Session key derived from ephemeral (per-connection) key pair
    - Ephemeral keys discarded after session ends
    - If private key is stolen: past sessions still safe
      (those keys were temporary and no longer exist)
    - TLS 1.3 mandates ECDHE: forward secrecy is not optional
```

---

### 🧪 Thought Experiment

**SCENARIO: Why HSTS is critical for banking sites**

```
ATTACK: SSL Stripping without HSTS

SETUP:
  User: connected to attacker's Wi-Fi (coffee shop, airport)
  Attacker: controls the network (man-in-the-middle position)
  bank.com: supports HTTPS, has HTTP→HTTPS redirect
  NO HSTS configured

ATTACK FLOW:
  1. User types: bank.com (no https://)
  2. Browser sends: HTTP GET bank.com (HTTP, plaintext)
  3. Attacker intercepts: HTTP request reaches attacker first
  4. Attacker connects to bank.com via HTTPS (legit connection)
  5. Attacker receives: 302 Redirect to https://bank.com
  6. Attacker forwards to victim: 200 OK (serves HTTP page)
  7. User: sees bank.com content, no HTTPS indicator
  8. User: enters credentials on attacker's HTTP page
  9. Attacker: captures credentials, forwards to real bank.com
  10. User: thinks they logged in successfully. Never knew.

WITH HSTS:
  1. User: previously visited bank.com (received HSTS header)
  2. Browser: stored HSTS policy for bank.com (max-age=31536000)
  3. User types: bank.com (any form)
  4. Browser: REJECTS connecting via HTTP without even trying
     Internally converts to: https://bank.com before sending
  5. First request is HTTPS: attacker cannot intercept the redirect
     because there IS no redirect - browser goes HTTPS directly
  
  Result: SSL stripping attack is impossible if:
    a) User previously visited the site and received HSTS, OR
    b) Site is in HSTS preload list (browser knows before first visit)

HSTS PRELOAD LIST:
  Submit domain at hstspreload.org
  Requirements: valid HTTPS, HSTS header with:
    max-age >= 31536000
    includeSubDomains
    preload
  
  All major browsers include preloaded domains.
  First-visit SSL stripping is impossible for preloaded domains.
  Removal from preload list takes months - plan before adding.
```

---

### 🧠 Mental Model / Analogy

> HTTPS configuration is like configuring a bank vault.
> TLS version = the vault model (TLS 1.0 = old vault with known
> weaknesses, TLS 1.3 = modern vault with best available technology).
> Cipher suites = the lock mechanism (some mechanisms have been
> cracked, others are currently unbreakable).
> Certificate = the vault's identity badge (signed by a trusted
> authority - the CA - proving this is the real vault).
> Certificate chain = the chain of trust from the vault badge
> through your bank's authority to the global authority.
> HSTS = the rule that clients should always use the vault,
> never walk in through the back door (HTTP).
> OCSP stapling = the vault's proof of validity, presented
> proactively rather than forcing the client to independently
> verify. testssl.sh is the security auditor who tests all
> these elements systematically.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
HTTPS encrypts communication between your browser and a website.
Setting it up requires a certificate (from Let's Encrypt - free)
and web server configuration. The certificate proves the site
is who it says it is. The encryption prevents eavesdropping.
HSTS is an additional setting that tells browsers "always use
HTTPS for this site, never HTTP." Test your setup at
ssllabs.com/ssltest - aim for A+ grade.

**Level 2 - How to use it (junior developer):**
Get a free certificate from Let's Encrypt using certbot:
`certbot --nginx -d example.com`. Certbot configures nginx,
sets up auto-renewal. Verify: `certbot renew --dry-run`.
Add HSTS header in nginx: `add_header Strict-Transport-Security "max-age=31536000" always;`. Redirect HTTP to HTTPS:
`return 301 https://$host$request_uri;`. Test with SSL Labs.

**Level 3 - How it works (mid-level engineer):**
TLS handshake: server presents certificate. Client validates
against trusted CA roots. Both sides negotiate cipher suite.
Key exchange (ECDHE): both parties contribute to session key.
Session key never transmitted: derived independently on both
sides using ECDHE. Certificate chain: server sends both its
cert AND the intermediate CA cert. Browser traces chain to
a root CA it trusts. OCSP stapling: server periodically
fetches signed "cert is valid" proof from CA, includes in
handshake. Without stapling: browser makes separate OCSP
request (slower, leaks browsing data to CA). Certificate
Transparency: all certificates must be logged in public CT logs.
Browsers check CT during handshake. Rogue CA-issued certs
are detectable via CT.

**Level 4 - Why it was designed this way (senior/staff):**
PKI (Public Key Infrastructure) distributes trust through CA
chains because creating a direct trust relationship between
every browser and every server is impractical. Instead:
browsers trust ~100 root CAs; CAs verify domain ownership
and sign certificates; browsers verify signatures. This model
has weaknesses: a compromised CA (DigiNotar 2011) can issue
fraudulent certificates for any domain. Certificate Transparency
was designed as a detection mechanism (fraudulent certs appear
in CT logs, allowing domain owners to detect unauthorized
certificates). HSTS preloading removed the "first visit"
attack window that SSL stripping exploited. TLS 1.3 removed
all known-weak algorithms (RSA key exchange, RC4, etc.) by
not including them in the protocol at all (vs 1.2 which lists
them as options that must be disabled in configuration).

**Level 5 - Mastery (distinguished engineer):**
Certificate Pinning (HPKP - HTTP Public Key Pinning) was
deprecated after several high-profile self-DoS incidents
(Smashing Security episode: site pins wrong key, certificate
rotation breaks all access). Mobile app pinning still used
but requires careful key rotation procedures. CAA (DNS
Certification Authority Authorization) DNS record restricts
which CAs can issue certs for your domain - cheap, effective
supply chain control. mTLS (mutual TLS) adds client certificate
authentication: both sides present certificates. Used for
service-to-service authentication (microservices, zero-trust).
Certificate management at scale (hundreds of services,
short-lived certificates) drives adoption of certificate
automation tools (SPIFFE/SPIRE for workload identity,
cert-manager for Kubernetes, Vault PKI secrets engine).

---

### ⚙️ How It Works (Mechanism)

**Certificate validation during TLS handshake:**

```
CERTIFICATE VALIDATION STEPS:

1. Server sends: certificate + intermediate CA certificate(s)

2. Browser checks certificate validity:
   a) Is the certificate's subject (CN or SAN) = hostname we connected to?
      CN: example.com, SAN: DNS:example.com, DNS:www.example.com
      Wildcard: *.example.com (matches api.example.com, not a.b.example.com)
   
   b) Is the certificate expired?
      Not-Before: 2024-01-01 ≤ NOW ≤ Not-After: 2025-01-01
   
   c) Is the issuer's signature valid?
      Server cert signed by: Intermediate CA X
      Browser verifies: Intermediate CA X's signature on server cert
   
   d) Is the Intermediate CA trusted?
      Intermediate cert signed by: Root CA Y
      Browser verifies: Root CA Y's signature on Intermediate cert
      Root CA Y must be in browser's trust store
   
   e) Is the certificate revoked?
      OCSP: online check (or stapled response)
      CRL: Certificate Revocation List download
   
   f) Is the certificate in CT logs?
      Certificate Transparency: server includes SCT (Signed
      Certificate Timestamp) proving the cert was logged.
      Without SCT: Chrome rejects the certificate (since 2018).

3. All checks pass → TLS handshake proceeds with key exchange
   Any check fails → Browser shows error or refuses connection
   
CERTIFICATE CHAIN EXAMPLE:

  Server Certificate (your-domain.com)
    Signed by → Let's Encrypt R3 (Intermediate CA)
  
  Let's Encrypt R3 Certificate
    Signed by → ISRG Root X1 (Root CA)
    OR signed by → DST Root CA X3 (cross-signed for compatibility)
  
  ISRG Root X1 / DST Root CA X3
    → In browser's trust store (pre-installed)
  
  Server MUST send: [server cert + Let's Encrypt R3 cert]
  Server does NOT send: Root CA (browsers have it already)
  
  COMMON MISTAKE: Only sending server cert (missing intermediate)
    Modern Chrome: usually still works (AIA fetching)
    OpenSSL s_client / curl: "verify error: unable to get local issuer certificate"
    Fix: include fullchain.pem (not just cert.pem) in nginx ssl_certificate
```

---

### 💻 Code Example

**nginx TLS configuration for A+ SSL Labs score:**

```nginx
# /etc/nginx/conf.d/example.conf

# HTTP → HTTPS redirect (catches all HTTP traffic)
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    
    # Redirect all HTTP to HTTPS (301 = permanent)
    return 301 https://$host$request_uri;
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;
    
    # Certificate files (Let's Encrypt via certbot)
    # ssl_certificate = server cert + intermediate chain
    # Use fullchain.pem, NOT cert.pem alone
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # TLS versions: 1.2 minimum, 1.3 preferred
    # Disable TLS 1.0 and 1.1 (deprecated, known attacks)
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Cipher suites for TLS 1.2 (TLS 1.3 uses built-in secure suites)
    # ECDHE: forward secrecy
    # AES-256-GCM: authenticated encryption
    # AES-128-GCM: faster, still secure
    # Excludes: RC4, DES, 3DES, MD5, anonymous, export ciphers
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    # Note: off = client chooses from server's list
    #   (modern clients choose best available; off is now recommended)
    
    # ECDH curve (for ECDHE key exchange)
    ssl_ecdh_curve X25519:prime256v1:secp384r1;
    
    # DH parameters for legacy DHE (generate once):
    # openssl dhparam -out /etc/nginx/dhparam.pem 4096
    # ssl_dhparam /etc/nginx/dhparam.pem;
    
    # Session resumption (performance optimization)
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;  # Tickets have forward secrecy concerns
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;
    resolver 1.1.1.1 8.8.8.8 valid=300s;
    resolver_timeout 5s;
    
    # Security headers
    add_header Strict-Transport-Security
      "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# TESTING:
# testssl.sh --full example.com
# ssllabs.com/ssltest (web)
# Check for: A+ grade, no warnings, all ciphers forward secret
```

---

### ⚖️ Comparison Table

| TLS Version | Status | Key Exchange | Forward Secrecy | Recommendation |
|:---|:---|:---|:---|:---|
| **SSL 2.0** | Deprecated 1996 | RSA | No | Disable (vulnerability) |
| **SSL 3.0** | Deprecated 2015 | RSA | No | Disable (POODLE) |
| **TLS 1.0** | Deprecated 2021 | RSA/DHE | Optional | Disable |
| **TLS 1.1** | Deprecated 2021 | RSA/DHE | Optional | Disable |
| **TLS 1.2** | Current | ECDHE/DHE | Required if configured | Enable with strong ciphers |
| **TLS 1.3** | Current (best) | ECDHE only | Mandatory | Enable, preferred |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| A self-signed certificate provides the same encryption as a CA-signed certificate | Self-signed and CA-signed certificates provide identical encryption strength - both use the same cryptographic algorithms. The difference is AUTHENTICATION (not encryption). A CA-signed certificate proves to clients that the server is who it claims to be, because a trusted third party (CA) verified and signed the certificate. A self-signed certificate provides no such proof - anyone can create one claiming to be any domain. In production: clients will see "Your connection is not private" warnings, many will refuse to connect, and API clients will fail with certificate validation errors. Self-signed certs are acceptable for internal development environments where manual trust override is acceptable. |
| HTTPS protects users from a malicious website | HTTPS provides: encryption (data in transit cannot be read) and authentication (the server is who the certificate says it is). HTTPS does NOT protect against: a legitimate server serving malicious content, phishing sites with valid Let's Encrypt certificates, malware on the user's device, compromised backend systems. A phishing site `paypa1.com` with a valid DV certificate has HTTPS (padlock) but is malicious. Users confuse the padlock with "safe site" when it only means "connection to THIS server is encrypted and authenticated." DV certificates are trivially obtained for malicious domains. |

---

### 🚨 Failure Modes & Diagnosis

**Common TLS/certificate failures:**

```
FAILURE 1: Expired certificate
  Symptom: Browser: "Your connection is not private (NET::ERR_CERT_DATE_INVALID)"
    curl: SSL certificate problem: certificate has expired
  
  Prevention: Let's Encrypt + certbot with auto-renewal cron:
    0 12 * * * certbot renew --quiet
  
  Monitoring: check-ssl-cert script or monitoring service
    (Pingdom, StatusCake, Uptime Robot) alerts 30/14/7 days before expiry
  
  Emergency fix if expired: certbot renew --force-renewal

FAILURE 2: Incomplete certificate chain
  Symptom:
    curl: SSL certificate problem: unable to get local issuer certificate
    Some browsers: work (AIA fetching), others: error
  
  Test: openssl s_client -connect example.com:443 -verify_chain
    Look for "verify error" lines
  
  Fix: nginx: use fullchain.pem (not cert.pem)
    certbot provides both in /etc/letsencrypt/live/domain/
    fullchain.pem = server cert + all intermediate certs
    cert.pem = server cert only

FAILURE 3: TLS 1.0/1.1 still enabled
  Detection: testssl.sh --protocols example.com
    → shows TLS 1.0: offered (vulnerable)
  
  Risk: POODLE (SSLv3, TLS 1.0), BEAST (TLS 1.0)
  Fix: ssl_protocols TLSv1.2 TLSv1.3;
    (Remove TLSv1 and TLSv1.1 from protocols list)
  
  Caveat: disabling TLS 1.0/1.1 breaks older clients
    (IE 11 on Windows 7, Java 7). Audit client base first.

FAILURE 4: Certificate Subject Mismatch
  Symptom: 
    curl: SSL: certificate subject name 'old.example.com'
    does not match target host name 'example.com'
  
  Cause: certificate issued for wrong domain, or
    connection to IP (not hostname), or
    www vs non-www mismatch
  
  Fix: issue certificate with correct SAN list
    certbot: -d example.com -d www.example.com -d api.example.com
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `TLS/SSL Protocol` - the underlying protocol
- `X.509 Certificates` - certificate format and validation
- `PKI` - the trust hierarchy
- `Cipher Suites` - encryption algorithm negotiation

**Builds on this:**
- `Session Security` - cookies require HTTPS for Secure attribute
- `TLS Config Best Practices` - advanced cipher suite selection
- `TLS Protocol Attacks` - POODLE, BEAST, CRIME, BREACH

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TLS VERSIONS │ Enable: TLS 1.2, TLS 1.3                  │
│              │ Disable: TLS 1.0, TLS 1.1, SSL (all)      │
├──────────────┼───────────────────────────────────────────┤
│ CIPHERS      │ ECDHE + AES-GCM + SHA256/384              │
│              │ Disable: RC4, DES, 3DES, EXPORT, ANON     │
├──────────────┼───────────────────────────────────────────┤
│ CERTIFICATE  │ fullchain.pem (server + intermediates)    │
│              │ Let's Encrypt + certbot for auto-renewal  │
├──────────────┼───────────────────────────────────────────┤
│ HSTS         │ max-age=31536000; includeSubDomains        │
│              │ Add preload only after testing             │
├──────────────┼───────────────────────────────────────────┤
│ TESTING      │ testssl.sh --full <domain>                │
│              │ ssllabs.com/ssltest → aim for A+          │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Configure what is secure by default; explicitly disable
everything insecure - never maintain an 'allow unless explicitly
blocked' posture." TLS 1.2 + TLS 1.3 with explicit protocol list
is "deny all, allow specific." Nginx `ssl_protocols` defaults
to "allow widely" - if you don't configure it explicitly,
older protocols may remain enabled. The principle is: in
security configuration, an explicit allowlist (only TLS 1.2
and 1.3) is safer than a denylist (all protocols except
TLS 1.0 and 1.1) because new protocols/ciphers added by
software updates are denied by default with an allowlist
but allowed by default with a denylist. Apply this
"deny by default" principle to cipher suites, HTTP methods,
file access, user permissions, and network ingress rules.

---

### 💡 The Surprising Truth

Let's Encrypt issued its 3 billionth certificate in 2023.
Before Let's Encrypt (pre-2016): certificates cost $50-300
per year per domain, required manual submission and validation,
and typically had 1-2 year validity periods. The operational
burden (cost + manual renewal process) was a significant
barrier to HTTPS adoption. The percentage of web pages loaded
over HTTPS globally: ~30% in 2016. In 2024: ~90%+ on Chrome.
Free, automated certificate issuance (Let's Encrypt) and
browser UI changes (Chrome marking HTTP sites as "Not Secure"
in 2018) drove this adoption faster than any security
education campaign could have. The engineering decision to
make security the easy path (certbot automates everything)
was more effective than making security the required path.
Removing friction from secure defaults is as important as
defining them.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONFIGURE** nginx or Apache with TLS 1.2+, forward-secret
   cipher suites, certificate chain, and HSTS header.
2. **OBTAIN** a Let's Encrypt certificate using certbot and
   configure auto-renewal.
3. **TEST** a server using testssl.sh and interpret the output
   to identify configuration weaknesses.
4. **DIAGNOSE** certificate errors: expired, incomplete chain,
   subject mismatch - and know the fix for each.

---

### 🎯 Interview Deep-Dive

**Q: How would you configure HTTPS on a new web server?
What makes a TLS configuration "secure"?**

*Why they ask:* Tests practical TLS configuration knowledge,
understanding of what makes TLS secure vs just "using HTTPS."

*Strong answer includes:*
- Obtain certificate: Let's Encrypt via certbot, or commercial CA.
  Use fullchain.pem (server + intermediate chain) for nginx/Apache.
  Configure auto-renewal (certbot renew cron job).
- TLS versions: enable only TLS 1.2 and TLS 1.3.
  Disable TLS 1.0 and TLS 1.1 (deprecated, known attacks).
- Cipher suites: ECDHE for key exchange (forward secrecy),
  AES-GCM or ChaCha20-Poly1305 for authenticated encryption.
  Disable: RC4, DES, 3DES, anonymous, export ciphers.
- HSTS: Strict-Transport-Security header with 1-year max-age.
  includeSubDomains if all subdomains support HTTPS.
- HTTP→HTTPS redirect.
- OCSP Stapling for performance and privacy.
- Testing: testssl.sh, SSL Labs (target A+ grade).
- What makes it secure: forward secrecy (ECDHE means past sessions
  safe even if private key compromised), authenticated encryption
  (AES-GCM detects tampering), no known-weak algorithms, HSTS
  prevents SSL stripping.