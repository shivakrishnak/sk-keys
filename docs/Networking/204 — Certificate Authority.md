---
layout: default
title: "Certificate Authority"
parent: "Networking"
nav_order: 204
permalink: /networking/certificate-authority/
number: "0204"
category: Networking
difficulty: ★★☆
depends_on: TLS/SSL, DNS
used_by: Networking, Microservices, mTLS, Security
related: TLS/SSL, mTLS, DNS, Zero Trust Networking, CDN
tags:
  - networking
  - certificate-authority
  - ca
  - pki
  - x509
  - lets-encrypt
  - cert-rotation
---

# 204 — Certificate Authority

⚡ TL;DR — A Certificate Authority (CA) is a trusted entity that digitally signs X.509 certificates, vouching that a public key belongs to a specific identity (domain, organisation, or person). The entire HTTPS trust model rests on CAs: browsers trust ~130 root CAs (built into OS/browser trust stores), and any cert signed by a trusted CA is accepted. Types: Public CAs (DigiCert, Let's Encrypt — for internet-facing services), Private CAs (for internal services, mTLS, Kubernetes). Let's Encrypt automated certificate issuance via ACME protocol, making HTTPS free and ubiquitous.

---

### 🔥 The Problem This Solves

How does your browser know that `https://bank.com` is really your bank and not an attacker? Anyone can generate a public/private key pair. The CA solves this by acting as a notary: it verifies your identity (domain control, or organisation identity for EV certs), signs your public key with its own private key, creating a certificate. Since the CA's public key is pre-installed in every browser/OS, your browser can verify the CA's signature on your certificate — thus trusting your identity transitively.

---

### 📘 Textbook Definition

**Certificate Authority (CA):** A trusted third party that issues and signs digital certificates, establishing a chain of trust in Public Key Infrastructure (PKI). A certificate is an X.509 document binding a public key to an identity (subject), signed by the CA's private key. The CA's own certificate (root certificate) is pre-distributed in trust stores (Windows, macOS, Linux, browsers, Android, iOS). Certificate signing creates a **certificate chain**: Leaf cert → Intermediate CA → Root CA → trust store.

**PKI (Public Key Infrastructure):** The set of roles, policies, hardware, software, and procedures to create, manage, distribute, use, store, revoke, and otherwise handle digital certificates.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CA = trusted notary for internet identity. It signs your certificate, proving your domain/identity to anyone who trusts the CA. Browsers trust ~130 root CAs by default; any cert signed by them (or their delegates) is accepted.

**One analogy:**

> A CA is like a government passport office. Anyone can have a photo ID, but only a government-issued passport (signed by the state = CA) is trusted internationally. When you present your passport at a border (TLS handshake), the border officer trusts it because they trust the issuing government (root CA). The government doesn't have to be present — its stamp (signature) on the passport is sufficient proof of identity.

---

### 🔩 First Principles Explanation

**TRUST CHAIN:**

```
Root CA (e.g., ISRG Root X1 — Let's Encrypt's root)
  Stored in OS/browser trust store
  Self-signed (signs itself)
  Long-lived (10-25 years), kept OFFLINE in air-gapped HSMs

  → Signs Intermediate CA (e.g., Let's Encrypt Authority R11)
    Intermediate CA cert: signed by Root CA
    Intermediate CAs are online (can issue certs)
    2-3 year lifetime; can be revoked without replacing root

    → Signs Leaf Certificate (e.g., example.com)
      Contains: public key, domain name, validity (90 days for Let's Encrypt)
      Signed by Intermediate CA's private key

Browser validation:
  1. Browser receives: example.com cert + intermediate cert
  2. Checks intermediate CA cert signature using root CA's public key (in trust store)
  3. Checks example.com cert signature using intermediate CA's public key
  4. Valid chain → trust the server's public key
```

**WHY INTERMEDIATE CAs:**

```
If Root CA private key is compromised:
  → EVERY certificate ever signed by this root is now untrustworthy
  → All browsers would need root CA removed from trust store
  → Catastrophic for internet

Intermediate CA layer:
  Root CA kept OFFLINE (air-gapped hardware security module)
  Intermediate CA: online, can issue millions of certs
  If intermediate CA is compromised: revoke it, issue new intermediate
  Root CA signs a new intermediate → no change to browser trust stores

Further isolation: Root CA signs → cross-signed by multiple roots
  Let's Encrypt's ISRG Root X1 was cross-signed by IdenTrust DST Root CA X3
  → Compatibility with older Android devices that didn't have ISRG Root X1
```

**DOMAIN VALIDATION (DV) VS ORGANISATION VALIDATION (OV) VS EXTENDED VALIDATION (EV):**

```
DV (Domain Validation) — most common:
  CA verifies: does the applicant control the domain?
  Methods:
    DNS challenge: add a TXT record with random token
    HTTP challenge: serve a file at /.well-known/acme-challenge/TOKEN
    Email challenge: email to admin@domain.com / webmaster@domain.com
  Automated (ACME protocol = Let's Encrypt)
  Certificate shows: "Issued to: example.com"
  Security: prevents impersonation of domain, NOT of organisation
  Free via Let's Encrypt; 90-day TTL

OV (Organisation Validation):
  CA verifies: domain control + organisation legal existence
  CA does: check business registry, verify phone number, verify address
  Takes: 1-3 business days
  Certificate shows: organisation name in Subject
  Cost: $100-500/year

EV (Extended Validation):
  CA verifies: full legal identity, physical location, operational status
  Takes: 1-5 business days, more documentation
  Browsers USED TO show green bar + organisation name (deprecated in Chrome 2019)
  Still used for: compliance requirements, trust signals in some contexts
  Cost: $200-1000/year
  Trend: DV with CT logs largely replaced EV's trust role

Wildcard certificates:
  *.example.com → covers: www.example.com, api.example.com, etc.
  But NOT: *.*.example.com (only one level)
  Let's Encrypt supports wildcards via DNS challenge only
```

**CERTIFICATE TRANSPARENCY (CT):**

```
Problem: CAs can issue fraudulent certs for domains they don't control.
  (Has happened: DigiNotar 2011 issued *.google.com to Iranian government)

Solution: Certificate Transparency (RFC 6962)
  All CAs MUST log every issued certificate to public CT logs
  CT logs: append-only, cryptographically verifiable (Merkle tree)
  Browsers require SCTs (Signed Certificate Timestamps) in certificates
  SCT = proof that cert was submitted to a CT log

Benefit:
  If a CA issues a rogue cert for your domain:
  → Cert appears in CT logs
  → CT monitoring services (crt.sh, Facebook CT Monitor) alert domain owner
  → Domain owner can demand cert revocation

You can monitor your domain's certs:
  curl -s 'https://crt.sh/?q=%.example.com&output=json' | jq '.[].name_value'
```

**LET'S ENCRYPT + ACME:**

```
ACME (Automated Certificate Management Environment):
  Protocol for automated cert issuance/renewal without human involvement
  Let's Encrypt implements ACME; certbot is the popular client

ACME HTTP-01 challenge flow:
  1. certbot requests cert for example.com from Let's Encrypt CA
  2. CA: "prove you control example.com"
     → CA provides token: abc123
  3. certbot: creates file at http://example.com/.well-known/acme-challenge/abc123
  4. CA: fetches the file, verifies token
  5. CA: issues cert (if valid), signs it with Intermediate CA
  6. certbot: stores cert + key in /etc/letsencrypt/live/example.com/
  7. certbot timer: renews cert at 60 days (before 90-day expiry)

ACME DNS-01 challenge (for wildcard certs):
  3. certbot creates DNS TXT record: _acme-challenge.example.com = token
  4. CA: queries DNS, verifies TXT record
  5. CA: issues cert (works for *.example.com)

Let's Encrypt scale (2024):
  ~400 million active certificates
  ~3 million certs issued per day
  Free; funded by Mozilla, Chrome, Cisco
```

**PRIVATE CA (FOR INTERNAL SERVICES):**

```
Use case: internal service mTLS (you don't want public CA for internal services)
  Options:
    1. Kubernetes cert-manager + self-signed CA
    2. HashiCorp Vault PKI Secrets Engine
    3. AWS ACM Private CA ($400/month)
    4. CFSSL (Cloudflare's PKI toolkit)
    5. Istio/SPIRE (for service mesh identity)

cert-manager in Kubernetes:
  Automates: certificate issuance, rotation, Kubernetes Secret management
  Issuers: Let's Encrypt (for external), self-signed, Vault, ACME
  CertificateRequest → Certificate resource → TLS Secret
  Automatic renewal: renews at 2/3 of cert lifetime
```

---

### 🧪 Thought Experiment

**THE COMPROMISED CA SCENARIO:**
In 2011, DigiNotar (Dutch CA) was compromised. Attackers issued certificates for google.com, \*.google.com, and other major domains. Iranian users were subjected to MITM attacks on Gmail and other Google services. The fake certificates were valid (signed by a trusted CA). The attack worked because browsers trusted DigiNotar root CA. Response: Google Chrome added certificate pinning for google.com (hardcoded cert hash). DigiNotar was removed from all browser trust stores within days → company went bankrupt. This is why Certificate Transparency now exists: the fraudulent certs would have appeared in CT logs immediately, alerting Google's monitoring.

---

### 🧠 Mental Model / Analogy

> PKI is like an international notary system. Your passport (certificate) was issued by your government (CA). When you visit another country (server), they trust your passport because they recognise the issuing government's stamp. But governments have delegates: embassies (intermediate CAs) can issue visa documents (intermediate certs) on behalf of the foreign ministry (root CA). The foreign ministry keeps the master stamp in a vault (offline root CA) and only uses it to authenticate embassies — embassies do the day-to-day work. If an embassy goes rogue, its authority is revoked and a new one established, without changing the master stamp.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A CA is a trusted authority that vouches for identities. It signs certificates that say "this public key belongs to example.com." Browsers trust ~130 root CAs pre-installed in your OS. Let's Encrypt gives free automated certificates via the ACME protocol. Certificate chains: your cert is signed by an intermediate CA, which is signed by a root CA.

**Level 2:** Three validation levels: DV (domain control only, automated), OV (+ organisation verification), EV (full legal identity, mostly deprecated). Certificate Transparency: all issued certs logged publicly — you can monitor for unauthorised certs for your domain via crt.sh. OCSP (Online Certificate Status Protocol): real-time revocation checks (OCSP stapling avoids privacy leak).

**Level 3:** X.509 certificate structure: version, serial number, subject (CN, O, OU), issuer, validity (notBefore/notAfter), public key, extensions (SAN, keyUsage, extendedKeyUsage, basicConstraints), signature algorithm, signature. Critical extensions: BasicConstraints (is CA: true/false), SubjectAltName (list of domains the cert is valid for), KeyUsage (digital signature, key encipherment), ExtendedKeyUsage (server authentication, client authentication). Wildcard limitations: \*.example.com covers one level only; international domains (IDNs) require Punycode encoding in CN/SAN.

**Level 4:** CA security operations: Root CA keys stored in FIPS 140-2 Level 4 HSMs (Hardware Security Modules), air-gapped from internet, in physically secured facilities. Ceremony: Root CA signing events are filmed, audited by independent CPA, with multiple key custodians each holding a share of the root key (Shamir Secret Sharing). WebTrust and CAB Forum (CA/Browser Forum) establish requirements all trusted CAs must meet — annual audits by Big 4 accounting firms. Violation = removal from browser trust stores (death sentence for a CA). The CAB Forum also sets certificate lifetime limits: maximum 398 days for publicly trusted DV/OV certificates (moved from 2 years, driving toward 90 days by 2026 per Apple/Google proposals).

---

### ⚙️ How It Works (Mechanism)

```bash
# Generate a private CA (for internal use)
# Step 1: generate root CA key and cert
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -key ca-key.pem -sha256 \
  -subj "/C=US/O=MyOrg/CN=MyOrg Root CA" \
  -days 3650 -out ca-cert.pem

# Step 2: generate service key and CSR (Certificate Signing Request)
openssl genrsa -out payment-service-key.pem 2048
openssl req -new -key payment-service-key.pem \
  -subj "/CN=payment-service" \
  -out payment-service.csr

# Step 3: sign with CA (including SAN extension)
cat > ext.cnf << 'EOF'
[req]
distinguished_name = req_distinguished_name
[req_distinguished_name]
[v3_req]
subjectAltName = DNS:payment-service,DNS:payment-service.production.svc.cluster.local
EOF

openssl x509 -req -in payment-service.csr \
  -CA ca-cert.pem -CAkey ca-key.pem \
  -CAcreateserial -sha256 -days 365 \
  -extfile ext.cnf -extensions v3_req \
  -out payment-service-cert.pem

# Verify certificate
openssl x509 -in payment-service-cert.pem -noout -text | \
  grep -A 5 "Subject Alternative Name"

# cert-manager in Kubernetes: automated cert issuance
kubectl apply -f - << 'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: payment-service-tls
  namespace: production
spec:
  secretName: payment-service-tls-secret
  duration: 24h        # short-lived
  renewBefore: 8h      # renew at 16h
  subject:
    organizations:
    - "MyOrg"
  dnsNames:
  - payment-service
  - payment-service.production.svc.cluster.local
  issuerRef:
    name: internal-ca-issuer
    kind: ClusterIssuer
EOF

# Monitor CT logs for your domain
curl -s 'https://crt.sh/?q=%.example.com&output=json' | \
  jq '.[].name_value' | sort -u
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Let's Encrypt Certificate Issuance (ACME HTTP-01):

1. You run: certbot certonly --nginx -d example.com

2. certbot → Let's Encrypt ACME API:
   "I want a certificate for example.com"

3. Let's Encrypt → certbot:
   "Complete this challenge to prove domain control"
   Provides: token = "random-string-abc"

4. certbot → web server:
   Creates: http://example.com/.well-known/acme-challenge/random-string-abc
   File content: "random-string-abc.account-thumbprint"

5. Let's Encrypt → HTTP GET:
   "http://example.com/.well-known/acme-challenge/random-string-abc"
   Verifies response matches expected value

6. Let's Encrypt → certbot:
   Challenge passed! Issuing certificate.

7. Let's Encrypt:
   - Generates cert with:
     Subject: CN=example.com
     SAN: DNS:example.com
     Validity: 90 days
     Signed by: Let's Encrypt Intermediate CA (R11)
   - Logs cert to Certificate Transparency logs (required)
   - Returns cert chain: leaf cert + intermediate cert

8. certbot saves:
   /etc/letsencrypt/live/example.com/fullchain.pem  (cert + intermediate)
   /etc/letsencrypt/live/example.com/privkey.pem    (private key)

9. nginx configured: ssl_certificate fullchain.pem; ssl_certificate_key privkey.pem;

10. Auto-renewal: certbot timer runs daily; renews at 60 days before expiry
```

---

### 💻 Code Example

```python
# Validate and inspect a certificate (Python)
import ssl
import socket
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def inspect_certificate(hostname: str, port: int = 443) -> dict:
    """Fetch and inspect a server's TLS certificate."""
    # Get raw certificate bytes
    context = ssl.create_default_context()

    with socket.create_connection((hostname, port), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            # Get DER-encoded cert
            der_cert = ssock.getpeercert(binary_form=True)

    # Parse with cryptography library
    cert = x509.load_der_x509_certificate(der_cert, default_backend())

    # Extract key details
    now = datetime.datetime.utcnow()
    days_until_expiry = (cert.not_valid_after - now).days

    # Get SANs (Subject Alternative Names)
    try:
        san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        sans = san_ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        sans = []

    return {
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "valid_from": cert.not_valid_before.isoformat(),
        "valid_until": cert.not_valid_after.isoformat(),
        "days_until_expiry": days_until_expiry,
        "sans": sans,
        "serial_number": str(cert.serial_number),
        "expired": days_until_expiry < 0,
        "expiring_soon": 0 <= days_until_expiry <= 30,
    }

# Certificate health check
def check_cert_health(hostname: str) -> str:
    info = inspect_certificate(hostname)
    if info["expired"]:
        return f"CRITICAL: Certificate EXPIRED for {hostname}"
    elif info["expiring_soon"]:
        return f"WARNING: Certificate expires in {info['days_until_expiry']} days"
    else:
        return f"OK: Certificate valid for {info['days_until_expiry']} days"

# print(check_cert_health("example.com"))
```

---

### ⚖️ Comparison Table

| CA Type                    | Use Case                       | Cost               | Validation          | Automation        |
| -------------------------- | ------------------------------ | ------------------ | ------------------- | ----------------- |
| Let's Encrypt              | Internet-facing HTTPS          | Free               | DV (domain control) | Full (ACME)       |
| DigiCert/Sectigo           | Enterprise HTTPS               | $100-1000/yr       | DV/OV/EV            | ACME or manual    |
| AWS ACM (public)           | AWS services (CloudFront, ALB) | Free               | DV                  | Automatic renewal |
| AWS ACM Private CA         | Internal services, mTLS        | $400/mo + per-cert | Custom              | API/cert-manager  |
| Vault PKI                  | Internal PKI, Kubernetes       | Free (open source) | Custom              | API/cert-manager  |
| cert-manager (self-signed) | Kubernetes development/test    | Free               | None (self-signed)  | Automatic         |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More expensive certificate = more secure         | Security of the cryptographic protection is identical for DV, OV, and EV certs (same key strength, same TLS encryption). Price and validation level affect trust signal for users, not cryptographic security                                                                                                   |
| Self-signed certs are fine for internal services | Self-signed certs are fine for development/testing, but for production internal services: use a private CA (Vault, cert-manager). Private CA provides cert revocation, audit trails, chain of trust, and automated rotation — self-signed certs have none of these                                              |
| Certificate revocation (CRL/OCSP) always works   | CRL/OCSP is unreliable: (a) OCSP servers can be slow or down; (b) Browsers often cache OCSP responses or use "soft fail" (if OCSP unreachable, allow connection anyway); (c) CRL files can be megabytes in size. CT monitoring + short-lived certs (90 days) is more effective than CRL/OCSP for most scenarios |

---

### 🚨 Failure Modes & Diagnosis

**Certificate Chain Incomplete — Browser Shows Untrusted**

```bash
# Symptom: browser shows "Certificate not trusted" or "SEC_ERROR_UNKNOWN_ISSUER"
# or curl error: "SSL certificate problem: unable to get local issuer certificate"

# Diagnose: check certificate chain
openssl s_client -connect example.com:443 -showcerts 2>/dev/null | \
  grep -E "BEGIN CERTIFICATE|subject|issuer"
# Should show: leaf cert + intermediate cert(s) → root CA
# If only one cert shown: missing intermediate certificate

# Check certificate chain online
# ssllabs.com or badssl.com

# Fix: concatenate certs in nginx
cat server.crt intermediate.crt > fullchain.crt
# nginx config: ssl_certificate /path/to/fullchain.crt;

# Let's Encrypt: certbot automatically provides fullchain.pem
# Use: ssl_certificate /etc/letsencrypt/live/domain/fullchain.pem

# Check if cert is in CT logs
curl -s "https://crt.sh/?q=example.com&output=json" | jq 'length'
# Should return > 0 (certs exist in logs)

# Check OCSP status
openssl ocsp -issuer intermediate.crt \
             -cert server.crt \
             -url "$(openssl x509 -in server.crt -noout -ocsp_uri)" \
             -resp_text 2>/dev/null | grep "Cert Status"
# Good result: "Cert Status: good"
# Bad: "Cert Status: revoked"
```

---

### 🔗 Related Keywords

**Prerequisites:** `TLS/SSL`, `DNS`

**Related:** `TLS/SSL`, `mTLS`, `Zero Trust Networking`, `DNS`, `CDN`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROOT CA      │ Pre-installed in OS/browser trust store   │
│ INTERMEDIATE │ Online CA that issues leaf certs; revocable│
│ LEAF CERT    │ Your server/service cert; signed by interm│
├──────────────┼───────────────────────────────────────────┤
│ DV           │ Domain control only; automated; free (LE)  │
│ OV/EV        │ Organisation verified; paid; mostly legacy │
├──────────────┼───────────────────────────────────────────┤
│ LET'S ENCRYPT│ Free, 90-day, automated via ACME           │
│ CT LOGS      │ All certs logged; crt.sh for monitoring    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Trusted notary that signs your identity  │
│              │ — browsers trust what CAs vouch for"      │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design a comprehensive PKI strategy for a financial institution with: internet-facing services (banking app, public API), internal microservices (mTLS), developer tooling, and a mobile banking app. (a) Determine which CA type to use for each use case: Let's Encrypt for internet-facing (ACME automation), AWS ACM Private CA for internal mTLS (Kubernetes cert-manager integration), and a dedicated intermediate CA for mobile certificate pinning. (b) Certificate pinning for the mobile app: explain why pinning the CA's public key (not the leaf cert) is safer than pinning the leaf cert (shorter-lived, can rotate without app update), and design the pin rotation process. (c) Certificate automation pipeline: describe the end-to-end flow for auto-issuance and rotation of internal mTLS certs using cert-manager + Vault PKI: how does cert-manager request a cert from Vault, how does Vault authenticate the request (Kubernetes auth method: pod JWT), and how does cert-manager update the Kubernetes Secret without downtime? (d) Post-quantum readiness: NIST standardised ML-KEM (Kyber) and ML-DSA (Dilithium) in 2024. Design a migration plan: how do you issue hybrid X.509 certificates (classical RSA + post-quantum), and how does your certificate chain remain compatible with existing TLS clients that don't support PQC algorithms?
