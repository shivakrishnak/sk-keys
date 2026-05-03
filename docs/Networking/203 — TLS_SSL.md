---
layout: default
title: "TLS/SSL"
parent: "Networking"
nav_order: 203
permalink: /networking/tls-ssl/
number: "0203"
category: Networking
difficulty: ★★☆
depends_on: Certificate Authority, HTTP & APIs, OSI Model
used_by: Networking, Microservices, HTTP & APIs, Security
related: mTLS, Certificate Authority, HTTP & APIs, DNS, CDN
tags:
  - networking
  - tls
  - ssl
  - https
  - encryption
  - certificates
  - handshake
---

# 203 — TLS/SSL

⚡ TL;DR — TLS (Transport Layer Security) is the protocol that encrypts network communication (the "S" in HTTPS). It provides: (1) **Encryption** (eavesdroppers can't read traffic), (2) **Authentication** (server identity verified via certificate), (3) **Integrity** (data can't be tampered with in transit). SSL is the deprecated predecessor; TLS 1.2 and TLS 1.3 are current. TLS 1.3 simplified the handshake (1-RTT vs 2-RTT), removed weak cipher suites, and added forward secrecy by default.

---

### 🔥 The Problem This Solves

Without TLS, HTTP traffic is plaintext: any network node between your browser and the server (ISP, router, coffee shop WiFi operator) can read your credentials, session tokens, and data. TLS solves three problems simultaneously: (1) Confidentiality: encrypt traffic so intermediaries can't read it; (2) Authentication: verify you're talking to the real server (not an impostor), using certificate authorities; (3) Integrity: detect any in-transit modification via MAC (Message Authentication Code).

---

### 📘 Textbook Definition

**TLS (Transport Layer Security):** A cryptographic protocol providing secure communication over a network. Operates at Layer 6/7 (presentation/application). Successor to SSL (Secure Sockets Layer, now deprecated). Current versions: TLS 1.2 (2008, widely supported), TLS 1.3 (2018, recommended). A TLS session is established via a **handshake** where peers agree on cipher suite, exchange keys (via asymmetric crypto), and derive symmetric session keys for bulk data encryption.

**Certificate:** An X.509 document containing a public key, identity information (domain name), issuer (Certificate Authority), validity period, and the CA's digital signature. Browsers/clients trust certificates signed by CAs in their trust store.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
TLS = envelope and lock for internet traffic. Your data is sealed in an encrypted envelope (encryption), the lock has the server's name on it (authentication), and a wax seal ensures it wasn't tampered with (integrity).

**One analogy:**

> TLS is like sending valuables in a locked, tamper-evident bag to a verified recipient. The courier (internet infrastructure) can only see the outside address label but cannot open the bag or modify the contents without detection. The recipient's identity is pre-verified by a trusted authority (Certificate Authority) whose approval appears on the bag. If the bag shows signs of tampering, the recipient refuses it.

---

### 🔩 First Principles Explanation

**WHY THREE PROPERTIES TOGETHER:**

```
Encryption alone:
  You encrypt your credit card to a public key.
  But HOW do you know the public key belongs to your bank?
  A MITM attacker gives you THEIR public key instead.
  → Need authentication

Authentication alone (without encryption):
  Server proves identity, but traffic is still plaintext.
  → Need encryption

Both without integrity:
  Attacker can flip bits in encrypted traffic to modify data
  (CBC padding oracle, bit-flipping attacks on CTR mode)
  → Need integrity (AEAD cipher suites: AES-GCM, ChaCha20-Poly1305)

TLS provides all three together — inseparable in design.
```

**TLS 1.2 HANDSHAKE:**

```
Client                                Server
  │                                      │
  │ ── ClientHello ──────────────────→   │
  │    TLS version: 1.2                  │
  │    Random: 32 bytes                  │
  │    Cipher suites: [ECDHE-RSA-AES128-GCM-SHA256, ...]
  │    Extensions: SNI (hostname), ALPN  │
  │                                      │
  │ ←── ServerHello + Certificate ───    │
  │    Server chooses cipher suite       │
  │    Server certificate (X.509)        │
  │    ServerKeyExchange (ECDHE params)  │
  │    CertificateRequest (for mTLS)     │
  │    ServerHelloDone                   │
  │                                      │
  │ Client: verify certificate           │
  │    ✓ Signed by trusted CA            │
  │    ✓ Not expired                     │
  │    ✓ Hostname matches SNI            │
  │    ✓ Not revoked (OCSP)              │
  │                                      │
  │ ── ClientKeyExchange ────────────→   │
  │    ECDHE: client's public key        │
  │    Both derive pre-master secret     │
  │    → Master secret → session keys   │
  │                                      │
  │ ── ChangeCipherSpec + Finished ──→   │
  │ ←── ChangeCipherSpec + Finished ──   │
  │                                      │
  │ ═══ Encrypted Application Data ════  │

2 round trips (2-RTT) before first data
```

**TLS 1.3 IMPROVEMENTS:**

```
TLS 1.3 vs 1.2:
  1. 1-RTT handshake (vs 2-RTT):
     Client sends key_share in ClientHello
     Server responds + sends certificate + Finished
     Client can send application data in first request after server response

  2. 0-RTT session resumption (for returning clients):
     Client sends early data with resumed session ticket
     Risk: replay attacks (0-RTT data can be replayed)
     Mitigation: only use 0-RTT for non-state-changing requests (GET, not POST)

  3. Removed weak algorithms:
     ❌ RSA key exchange (no forward secrecy)
     ❌ CBC cipher modes (CBC padding oracle attacks)
     ❌ SHA-1, MD5 (broken hash functions)
     ❌ Static DH (no forward secrecy)

  4. Forward secrecy mandatory:
     Only ephemeral key exchange: ECDHE, DHE
     Session key derived from ephemeral keys
     Even if server's private key is stolen later: past sessions can't be decrypted
     Each session has unique keys (no long-term encryption keys)

  5. Encrypted handshake:
     In TLS 1.2: server certificate is sent in plaintext
     In TLS 1.3: certificate sent encrypted (only client Hello metadata visible)
```

**CIPHER SUITES:**

```
TLS 1.2 cipher suite naming:
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
  ECDHE: key exchange algorithm (ephemeral ECDH)
  RSA:   authentication algorithm (server cert is RSA)
  AES_128_GCM: symmetric encryption + integrity (AEAD)
  SHA256: PRF for key derivation

TLS 1.3 cipher suite (simplified — key exchange removed, always ECDHE):
TLS_AES_128_GCM_SHA256
  AES_128_GCM: symmetric encryption (AEAD cipher)
  SHA256: hash algorithm for HKDF key derivation

Recommended TLS 1.2 suites (ordered by security):
  1. TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (strongest)
  2. TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  3. TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
  4. TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

Deprecated (do NOT use):
  ❌ TLS_RSA_WITH_AES_128_CBC_SHA (no forward secrecy, CBC mode)
  ❌ TLS_DES_40_CBC_SHA (export grade, trivially breakable)
  ❌ Any suite with NULL, ANON, RC4, MD5, SHA1 in name
```

**SNI (SERVER NAME INDICATION):**

```
Problem: one IP address, multiple domains (shared hosting, CDN)
  Server at 1.2.3.4 hosts: example.com, company.com, shop.example.com
  Which certificate to present? Server doesn't know until TLS handshake.
  But certificate is presented DURING handshake.

SNI solution: client includes hostname in ClientHello extension
  Client: "I want to connect to example.com" (SNI in ClientHello)
  Server: "Ah, example.com — I'll present example.com's certificate"

Note: SNI is NOT encrypted in TLS 1.2 (visible to eavesdroppers)
  You can see which hostname a client is connecting to, even if content encrypted
  ESNI (Encrypted SNI) / ECH (Encrypted ClientHello) in TLS 1.3:
    Encrypts SNI using CDN's public key (Cloudflare, etc.)
    Prevents ISP/network from seeing destination hostname
```

---

### 🧪 Thought Experiment

**FORWARD SECRECY VS DECRYPT LATER:**
Without forward secrecy (TLS 1.2 with RSA key exchange): an attacker records all encrypted TLS traffic today. In 5 years, a quantum computer (or law enforcement subpoena) obtains the server's private RSA key. The attacker can now decrypt ALL past recorded traffic.

With forward secrecy (ECDHE): each session uses fresh ephemeral keys. The server's long-term private key only signs the ephemeral key exchange — it cannot decrypt session traffic. Even with the private key, past sessions cannot be decrypted. This is why TLS 1.3 mandates forward secrecy (ECDHE only).

---

### 🧠 Mental Model / Analogy

> TLS has a two-phase security system. The handshake is like meeting a new business partner: you exchange business cards (certificates), verify each other's credentials through a trusted verification service (Certificate Authority), and exchange a secret password in a tamper-proof way (ECDHE key exchange). After the handshake, all subsequent conversation uses a one-time cipher (symmetric session keys) that you both derived from that initial exchange. Even if someone recorded the entire conversation and later stole the original business cards (private keys), they can't work out what the one-time cipher was — that's forward secrecy.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** TLS encrypts internet traffic (the "S" in HTTPS). It proves the server is who it claims (via certificate from a trusted authority), encrypts all data, and detects tampering. TLS 1.3 is faster (1-RTT) and more secure than TLS 1.2.

**Level 2:** TLS handshake: client says hello (cipher suites), server presents certificate, client verifies it, both derive session keys using ECDHE (ephemeral Diffie-Hellman), then communicate via AES-GCM encryption. SNI tells the server which certificate to use when one IP hosts multiple domains. TLS 1.3: removed all weak algorithms, made forward secrecy mandatory.

**Level 3:** Certificate chain validation: your browser has ~130 trusted root CAs (Mozilla/Apple trust stores). A server cert is usually signed by an intermediate CA, which is signed by a root CA. Browser validates the entire chain. OCSP (Online Certificate Status Protocol): real-time cert revocation check. OCSP stapling: server includes a pre-fetched OCSP response in TLS handshake (avoids client making separate HTTP request, improves privacy). Certificate Transparency (CT) logs: all CAs must log every certificate issued to public CT logs, enabling detection of misissued certs.

**Level 4:** Record protocol vs handshake protocol: TLS is two protocols in one. The handshake protocol (complex key exchange, certificate verification) runs first. The record protocol (bulk data encryption/decryption using AES-GCM) runs for all application data. AEAD (Authenticated Encryption with Associated Data): AES-256-GCM is both an encryption algorithm (confidentiality) and a MAC (integrity) simultaneously — you cannot decrypt successfully if the ciphertext was modified. This is why TLS 1.3 dropped separate MAC algorithms (no more HMAC-SHA256 as a separate step). Post-quantum TLS: NIST standardised ML-KEM (Kyber) for post-quantum key exchange; TLS 1.3 extensions already support hybrid classical+PQC key exchange (X25519Kyber768). Chrome and Firefox are testing PQC hybrid TLS today.

---

### ⚙️ How It Works (Mechanism)

```bash
# Test TLS configuration of a server
openssl s_client -connect example.com:443 -tls1_3
# Shows: certificate chain, cipher suite, TLS version

# Check which TLS versions a server supports
nmap --script ssl-enum-ciphers -p 443 example.com

# View certificate details
echo | openssl s_client -connect example.com:443 2>/dev/null | \
  openssl x509 -noout -text | head -50

# Check certificate expiry (critical for monitoring)
echo | openssl s_client -connect example.com:443 2>/dev/null | \
  openssl x509 -noout -dates

# Test HTTPS with curl (verbose TLS info)
curl -v https://example.com 2>&1 | grep -E "TLS|SSL|cipher|protocol"

# Check OCSP stapling
openssl s_client -connect example.com:443 -status 2>/dev/null | \
  grep -A 5 "OCSP Response"

# Nginx: configure TLS 1.3 + strong ciphers
# nginx.conf:
# ssl_protocols TLSv1.2 TLSv1.3;
# ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
# ssl_prefer_server_ciphers off;  # TLS 1.3: client choice
# ssl_session_timeout 1d;
# ssl_session_cache shared:SSL:10m;
# ssl_stapling on;  # OCSP stapling
# ssl_stapling_verify on;

# Let's Encrypt certificate issuance (ACME protocol)
certbot certonly --nginx -d example.com --email admin@example.com
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
TLS 1.3 Handshake (1-RTT):

Browser connects to https://shop.example.com

→ ClientHello:
   Supported: TLS 1.3
   Cipher suites: [TLS_AES_256_GCM_SHA384, TLS_AES_128_GCM_SHA256, ...]
   SNI: "shop.example.com"
   key_share: client's ECDH public key (X25519)
   supported_groups: X25519, P-256

← ServerHello:
   Chosen cipher: TLS_AES_256_GCM_SHA384
   key_share: server's ECDH public key (X25519)
   [Both sides now derive: pre-master secret → master secret → session keys]

← {Certificate}: shop.example.com cert (encrypted with handshake key)
   Issued by: Let's Encrypt Authority X3
   Signed by: ISRG Root X1 (trusted root in browser)
   Valid: 2024-01-01 to 2024-04-01
   SAN: shop.example.com

← {CertificateVerify}: server proves it has cert's private key
   Signature over handshake transcript using server's private key

← {Finished}: HMAC over handshake transcript (integrity)

→ {Finished}: client confirms

→ {Application Data}: HTTP GET /products (encrypted with session key)
← {Application Data}: HTTP 200 response (encrypted)

Entire handshake: 1 round trip
First data: immediately after client Finished
```

---

### 💻 Code Example

```python
# TLS client with certificate verification (Python)
import ssl
import urllib.request
import socket

def create_tls_context(min_version: str = "TLS_1_3") -> ssl.SSLContext:
    """Create a secure TLS context with modern settings."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # Minimum TLS version
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Only allow strong cipher suites (for TLS 1.2 fallback)
    context.set_ciphers(
        "ECDHE+AESGCM:ECDHE+CHACHA20:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK"
    )

    # Enable hostname verification (default in PROTOCOL_TLS_CLIENT)
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    # Load system trust store
    context.load_default_certs()

    return context

def fetch_with_tls(url: str) -> str:
    """Fetch URL with strict TLS verification."""
    context = create_tls_context()

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=context) as resp:
        # Inspect TLS connection details
        return resp.read().decode()

def inspect_tls_connection(hostname: str, port: int = 443) -> dict:
    """Inspect TLS connection details for a host."""
    context = ssl.create_default_context()

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            cipher = ssock.cipher()
            version = ssock.version()

            return {
                "tls_version": version,
                "cipher_suite": cipher[0],
                "bits": cipher[2],
                "subject": dict(x[0] for x in cert.get('subject', [])),
                "issuer": dict(x[0] for x in cert.get('issuer', [])),
                "valid_from": cert.get('notBefore'),
                "valid_until": cert.get('notAfter'),
                "san": [v for _, v in cert.get('subjectAltName', [])],
            }

# Example
info = inspect_tls_connection("google.com")
print(f"TLS Version: {info['tls_version']}")  # TLSv1.3
print(f"Cipher: {info['cipher_suite']}")
```

---

### ⚖️ Comparison Table

| Aspect                   | TLS 1.2                      | TLS 1.3                  | SSL 3.0 (deprecated) |
| ------------------------ | ---------------------------- | ------------------------ | -------------------- |
| Handshake round trips    | 2-RTT                        | 1-RTT (0-RTT resumption) | 2-RTT                |
| Forward secrecy          | Optional (configurable)      | Mandatory (ECDHE only)   | No                   |
| Key exchange             | RSA or DHE/ECDHE             | ECDHE/DHE only           | RSA                  |
| Weak cipher suites       | Present (need config)        | Removed                  | Many weak ciphers    |
| Certificate in plaintext | Yes                          | No (encrypted)           | Yes                  |
| Security status          | Acceptable (hardened config) | Recommended              | Insecure (POODLE)    |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                             |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SSL and TLS are interchangeable terms       | SSL 2.0 and 3.0 are deprecated due to critical vulnerabilities (POODLE, DROWN). When people say "SSL certificate" they mean an X.509 certificate used with TLS. The protocol is TLS; certificate format is X.509                    |
| HTTPS means the website is trustworthy/safe | HTTPS means the connection is encrypted and server identity is verified (to the certificate owner). The website can still serve malware, phishing, or have vulnerabilities. Cert issuers verify domain control, not website content |
| TLS prevents server from seeing your data   | TLS encrypts data in transit between client and server. The SERVER decrypts the data — TLS only prevents third parties (intermediaries, ISPs) from reading it. The server has full access to plaintext                              |

---

### 🚨 Failure Modes & Diagnosis

**Certificate Expiry — Service Outage**

```bash
# Monitor certificate expiry (critical for production)
# Check expiry date
echo | openssl s_client -connect api.example.com:443 2>/dev/null | \
  openssl x509 -noout -enddate
# notAfter=Apr 15 00:00:00 2024 GMT

# Days until expiry (bash)
EXPIRY=$(echo | openssl s_client -connect api.example.com:443 2>/dev/null | \
  openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -jf "%b %d %T %Y %Z" "$EXPIRY" +%s)
DAYS_LEFT=$(( (EXPIRY_EPOCH - $(date +%s)) / 86400 ))
echo "Certificate expires in $DAYS_LEFT days"

# Prometheus-based monitoring (common pattern):
# node_exporter blackbox_exporter: probe_ssl_earliest_cert_expiry gauge
# Alert: probe_ssl_earliest_cert_expiry - time() < 30 * 24 * 3600

# Let's Encrypt auto-renewal check
systemctl status certbot.timer  # should be active
# Manual renewal test:
certbot renew --dry-run

# Certificate chain issues (incomplete chain):
openssl s_client -connect api.example.com:443 -verify_return_error 2>&1 | \
  grep -E "verify error|OK"
# "verify error:num=21:unable to verify the first certificate"
# → Missing intermediate certificate in server config
# Fix: concatenate server cert + intermediate cert in certificate file
cat server.crt intermediate.crt > fullchain.crt
```

---

### 🔗 Related Keywords

**Prerequisites:** `Certificate Authority`, `HTTP & APIs`, `OSI Model`

**Related:** `mTLS`, `Certificate Authority`, `HTTP & APIs`, `DNS`, `CDN`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TLS PROVIDES │ Encryption + Authentication + Integrity   │
│ TLS 1.3      │ 1-RTT, mandatory forward secrecy, removes │
│              │ weak ciphers, encrypted certificate       │
├──────────────┼───────────────────────────────────────────┤
│ HANDSHAKE    │ ECDHE key exchange → derive session keys  │
│ SESSION KEY  │ AES-256-GCM (AEAD: encrypt + MAC in one)  │
├──────────────┼───────────────────────────────────────────┤
│ CERT CHAIN   │ Leaf → Intermediate → Root CA → trust     │
│ FORWARD SEC  │ Ephemeral keys: past sessions unreadable  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Envelope + lock + wax seal for internet  │
│              │ traffic — encrypt, authenticate, protect" │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A major e-commerce company is migrating their TLS configuration from TLS 1.0/1.1 to TLS 1.3 only. (a) Explain the attack implications of TLS 1.0/1.1 that justify the migration (BEAST, POODLE, DROWN — describe each attack mechanism briefly). (b) The migration introduces compatibility concerns: legacy payment terminals may only support TLS 1.2 — design the migration strategy (parallel endpoints, monitoring by TLS version, phased rollout). (c) Performance analysis: TLS 1.3 0-RTT session resumption can be used for returning customers' browsers — explain the security trade-off (replay attack risk on 0-RTT data, why POST requests should never use 0-RTT, how QUIC uses 0-RTT for performance). (d) Certificate pinning: mobile apps can pin the server's certificate (or public key) to prevent MITM even with a rogue CA. Explain the risk of cert pinning in production (pin expiry = app outage), and describe the HPKP (HTTP Public Key Pinning) standard and why it was deprecated in favour of Expect-CT + Certificate Transparency monitoring.
