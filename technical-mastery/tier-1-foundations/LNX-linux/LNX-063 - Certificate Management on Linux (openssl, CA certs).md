---
id: LNX-063
title: "Certificate Management on Linux (openssl, CA certs)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-033, LNX-057
used_by: LNX-058
related: LNX-033, LNX-057, LNX-026
tags: [openssl, TLS, certificates, CA, x509, CSR, self-signed, certificate-store, certbot, PKCS12]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 63
permalink: /technical-mastery/lnx/certificate-management-linux/
---

## TL;DR

Linux certificate management: **openssl** for creating keys/CSRs/certs,
inspecting certificates. System CA bundle: `/etc/ssl/certs/` (Ubuntu/Debian)
or `/etc/pki/tls/certs/` (RHEL). Add custom CA: copy to
`/usr/local/share/ca-certificates/` + `update-ca-certificates` (Ubuntu) or
`/etc/pki/ca-trust/source/anchors/` + `update-ca-trust` (RHEL). Let's
Encrypt via `certbot` for public-facing TLS. Self-signed certs for internal:
`openssl req -x509 -newkey rsa:4096`. `openssl s_client -connect host:443`
to debug TLS. Cert expiry check: `openssl x509 -enddate -noout`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-063 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | openssl, TLS, x509, CA, certificates, CSR, self-signed, certbot, PKCS12 |
| **Prerequisites** | LNX-033 (SSH - key concepts), LNX-057 (Security) |

---

### The Problem This Solves

**Problem 1**: A corporate internal service needs HTTPS but is not
publicly accessible. certbot won't work (no public DNS). Create a private
CA, sign internal certificates with it, and distribute the CA certificate to
all clients. `update-ca-certificates` makes tools like `curl`, `wget`,
`git` trust the internal CA automatically.

**Problem 2**: curl fails with "SSL certificate problem: certificate has
expired". The server's certificate expired. How to check: `openssl s_client
-connect server:443 | openssl x509 -noout -enddate`. How to replace: get
new cert from CA or certbot, install it, reload nginx/apache. How to prevent:
set up monitoring with `certbot renew --dry-run` cron or `ssl_expiry`
monitoring check.

---

### Textbook Definition

**X.509 certificate**: A digital document binding a public key to an
identity (domain name, organization). Contains: subject (who), issuer (CA),
validity period, public key, signature by issuer's private key, Subject
Alternative Names (SANs) for additional hostnames.

**Certificate Authority (CA)**: An entity that signs certificates, vouching
for the subject's identity. Browser/OS trust stores include a list of
"root CAs" (Mozilla, Google, Microsoft maintain these lists). Any certificate
signed by a chain leading to a trusted root CA is trusted.

**CSR (Certificate Signing Request)**: A message from a key holder to a CA.
Contains: public key, desired subject information. The CA verifies identity,
signs the CSR, and returns the certificate.

**TLS handshake**: Client connects -> server presents certificate -> client
verifies chain to trusted CA -> negotiate cipher -> symmetric encryption
established. The certificate proves the server IS who it claims to be
(prevents MITM).

---

### Understand It in 30 Seconds

```bash
# === Inspect a certificate ===
openssl x509 -in certificate.pem -noout -text    # full text output
openssl x509 -in certificate.pem -noout -subject  # who issued to
openssl x509 -in certificate.pem -noout -issuer   # who signed it
openssl x509 -in certificate.pem -noout -enddate  # expiry date
openssl x509 -in certificate.pem -noout -fingerprint  # SHA1 fingerprint

# Check certificate from a live server:
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
    | openssl x509 -noout -enddate
# notAfter=Jan  1 00:00:00 2025 GMT

# Multiple quick checks:
echo | openssl s_client -connect example.com:443 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates

# === Create a private key and CSR ===
# Generate 4096-bit RSA key:
openssl genrsa -out myapp.key 4096
# or ECDSA (smaller, faster):
openssl ecparam -name prime256v1 -genkey -noout -out myapp.key

# Create CSR (sends to CA for signing):
openssl req -new -key myapp.key -out myapp.csr \
    -subj "/CN=myapp.example.com/O=MyOrg/C=US"
# View CSR:
openssl req -in myapp.csr -noout -text

# === Create a self-signed certificate (development/internal) ===
# Simple:
openssl req -x509 -newkey rsa:4096 -keyout myapp.key -out myapp.crt \
    -days 365 -nodes \
    -subj "/CN=myapp.internal/O=MyOrg/C=US"
# -x509 = self-sign (no CA), -nodes = no password on key (for servers)

# With Subject Alternative Names (required by modern browsers):
openssl req -x509 -newkey rsa:4096 -keyout myapp.key -out myapp.crt \
    -days 365 -nodes \
    -subj "/CN=myapp.internal" \
    -addext "subjectAltName=DNS:myapp.internal,DNS:myapp,IP:10.0.1.50"

# === Build a private CA ===
# Step 1: Create CA key and self-signed root cert:
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
    -out ca.crt \
    -subj "/CN=MyOrg Internal CA/O=MyOrg/C=US"
# ca.crt = the root CA certificate to distribute to clients

# Step 2: Create server key and CSR:
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj "/CN=myservice.internal/O=MyOrg/C=US"

# Step 3: Sign the server CSR with the CA:
cat > ext.cnf << 'EOF'
[req]
req_extensions = v3_req
[v3_req]
subjectAltName = @alt_names
[alt_names]
DNS.1 = myservice.internal
DNS.2 = myservice
IP.1 = 10.0.1.100
EOF

openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out server.crt -days 365 -sha256 \
    -extfile ext.cnf -extensions v3_req

# Step 4: Verify the certificate chain:
openssl verify -CAfile ca.crt server.crt
# server.crt: OK

# === Install custom CA (system-wide trust) ===
# Ubuntu/Debian:
cp ca.crt /usr/local/share/ca-certificates/myorg-ca.crt
update-ca-certificates
# Verify:
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt server.crt

# RHEL/CentOS/Fedora:
cp ca.crt /etc/pki/ca-trust/source/anchors/myorg-ca.crt
update-ca-trust extract
# Verify:
openssl verify -CAfile /etc/pki/tls/certs/ca-bundle.crt server.crt

# === Let's Encrypt with certbot ===
apt install certbot python3-certbot-nginx   # Ubuntu

# Obtain and auto-configure nginx:
certbot --nginx -d example.com -d www.example.com

# Standalone (no web server running):
certbot certonly --standalone -d example.com

# Certificate location:
# /etc/letsencrypt/live/example.com/fullchain.pem  (cert + chain)
# /etc/letsencrypt/live/example.com/privkey.pem    (private key)

# Auto-renew (certbot installs a systemd timer or cron):
certbot renew --dry-run   # test renewal

# === Convert between formats ===
# PEM to PKCS12 (Java keystore format):
openssl pkcs12 -export -in server.crt -inkey server.key \
    -out server.p12 -name myapp

# PKCS12 to PEM:
openssl pkcs12 -in server.p12 -out server.pem -nodes

# DER to PEM:
openssl x509 -in cert.der -inform DER -out cert.pem
```

---

### First Principles

**X.509 certificate chain verification:**
```
Client wants to connect to myapp.internal

Server presents:
  [Server Cert]
    Subject: myapp.internal
    Issuer: MyOrg Internal CA
    Valid: 2024-01-01 to 2025-01-01
    Public Key: (server's public key)
    Signature: (signed with CA's private key)

Client's verification process:
  1. Check server cert validity period: is today within range?
  2. Check Subject (or SAN): does it match "myapp.internal"?
  3. Find issuer cert: look for "MyOrg Internal CA" in trust store
     - Check /etc/ssl/certs/ (or /etc/pki/tls/certs/ca-bundle.crt)
     - FOUND: ca.crt (because we ran update-ca-certificates)
  4. Verify signature: did CA's private key sign this cert?
     openssl verify: hash(server_cert_content) == decrypt(signature, CA_pubkey)?
  5. Check CA cert: is the CA itself trusted?
     - Root CA: self-signed (issuer == subject)
     - Is it in the system trust store? YES
  6. TRUSTED: proceed with TLS handshake

Without CA in trust store:
  Step 3 fails: "unable to get local issuer certificate"
  Or: "self-signed certificate" (if self-signed without CA)
```

**SAN (Subject Alternative Names) - why it matters:**
```
Old behavior (before 2000): CN (Common Name) = hostname check
  CN=myapp.internal  <- browsers matched this

Modern behavior (since ~2017): SAN required
  Chrome/Firefox 58+: IGNORE CN, ONLY check SAN
  No SAN in cert -> cert error regardless of CN

Proper SAN configuration:
  openssl -addext "subjectAltName=DNS:myapp.internal,DNS:myapp,IP:10.0.0.50"

Wildcard certs:
  *.example.com  covers: api.example.com, www.example.com
  NOT: api.sub.example.com (wildcard = one level only)
  NOT: example.com itself (wildcard doesn't cover bare domain)
  SAN: DNS:*.example.com, DNS:example.com (cover both)
```

---

### Thought Experiment

Setting up internal PKI for a microservices environment:

```bash
#!/bin/bash
# internal-pki.sh: Create CA and issue service certificates

# === Root CA ===
mkdir -p /etc/myorg-ca/{private,certs,newcerts}
chmod 700 /etc/myorg-ca/private
echo "01" > /etc/myorg-ca/serial
touch /etc/myorg-ca/index.txt

# Generate CA key (protect with password in production):
openssl genrsa -out /etc/myorg-ca/private/ca.key 4096
chmod 400 /etc/myorg-ca/private/ca.key

# Self-sign CA certificate (10 year validity):
openssl req -x509 -new -nodes \
    -key /etc/myorg-ca/private/ca.key \
    -sha256 -days 3650 \
    -out /etc/myorg-ca/certs/ca.crt \
    -subj "/CN=MyOrg Root CA/O=MyOrg/C=US/emailAddress=security@myorg.com"

echo "CA created: /etc/myorg-ca/certs/ca.crt"

# === Issue service certificate ===
issue_cert() {
    SERVICE=$1
    SANS=$2   # comma-separated: DNS:api.myorg.internal,IP:10.0.1.50

    mkdir -p "/etc/myorg-ca/services/$SERVICE"
    
    # Generate service key:
    openssl genrsa -out "/etc/myorg-ca/services/$SERVICE/$SERVICE.key" 2048

    # Create CSR config with SANs:
    cat > "/tmp/$SERVICE.cnf" << EOF
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[v3_req]
subjectAltName = $SANS
EOF

    # Create CSR:
    openssl req -new \
        -key "/etc/myorg-ca/services/$SERVICE/$SERVICE.key" \
        -out "/tmp/$SERVICE.csr" \
        -subj "/CN=$SERVICE.myorg.internal/O=MyOrg/C=US" \
        -config "/tmp/$SERVICE.cnf"

    # Sign with CA:
    openssl x509 -req \
        -in "/tmp/$SERVICE.csr" \
        -CA /etc/myorg-ca/certs/ca.crt \
        -CAkey /etc/myorg-ca/private/ca.key \
        -CAcreateserial \
        -out "/etc/myorg-ca/services/$SERVICE/$SERVICE.crt" \
        -days 365 -sha256 \
        -extfile "/tmp/$SERVICE.cnf" \
        -extensions v3_req

    echo "Certificate issued: /etc/myorg-ca/services/$SERVICE/$SERVICE.crt"
    echo "Expires: $(openssl x509 -in /etc/myorg-ca/services/$SERVICE/$SERVICE.crt -noout -enddate)"
}

# Issue certs for services:
issue_cert "api-gateway" "DNS:api.myorg.internal,DNS:api-gateway,IP:10.0.1.10"
issue_cert "user-service" "DNS:users.myorg.internal,DNS:user-service,IP:10.0.1.11"

# === Distribute CA to all hosts ===
# Copy CA cert to all servers, then:
# Ubuntu/Debian: update-ca-certificates
# RHEL: update-ca-trust extract
echo ""
echo "Distribute to servers:"
echo "  cp /etc/myorg-ca/certs/ca.crt /usr/local/share/ca-certificates/myorg-ca.crt"
echo "  update-ca-certificates"
```

---

### Mental Model / Analogy

```
Certificates = government-issued ID cards

Private CA = a company's HR department issuing employee badges
  HR (CA) has the stamp/seal (private key)
  Employee badge (certificate) = "This person is John Smith, expires 2025"
  Badge is stamped by HR's official seal
  
  To verify: check the badge -> look at the seal -> is the seal from a trusted HR dept?
  (verify cert -> check issuer -> is issuer in trust store?)

Public CA (Let's Encrypt, DigiCert) = a government DMV
  Everyone trusts the DMV's ID cards
  Browser trust store = list of recognized government agencies

Self-signed cert = homemade ID card
  "I certify that I am John Smith" - signed by yourself
  Browser says: "Why should I trust that?"
  Fine for development/internal (everyone knows you), useless externally

CSR = filling out the ID application form
  You provide your info + passport photo (public key)
  You submit to the DMV (CA)
  DMV verifies, stamps it, returns the official ID

update-ca-certificates = teaching the browser/OS to recognize a new ID agency
  "Our company also accepts MyOrg-issued badges"
  After running: curl, wget, git, Java all trust certs signed by MyOrg CA

SAN = the "also valid for" section on an ID card
  "This ID is valid for John Smith and also for 'John' and '10.0.1.50'"
  Modern browsers require SANs - CN-only IDs are rejected

certbot = a robot that goes to the DMV for you every 90 days
  Auto-renews before expiry (90-day Let's Encrypt certs)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`openssl x509 -in cert.pem -noout -enddate` for expiry. `openssl s_client
-connect host:443` for debugging. Adding trusted CA to system:
`update-ca-certificates` (Ubuntu) or `update-ca-trust` (RHEL). `certbot`
for Let's Encrypt. Self-signed cert creation.

**Level 2:**
Building an internal CA. CSR workflow. SAN requirements. PEM vs DER vs
PKCS12 formats. `openssl verify -CAfile ca.crt server.crt`. Checking
full chain: `openssl s_client -connect host:443 -showcerts`. `curl -v`
for TLS debugging. Certificate transparency logs.

**Level 3:**
OCSP (Online Certificate Status Protocol) for real-time revocation checks.
CRL (Certificate Revocation List). OCSP stapling. Certificate pinning.
HSTS (HTTP Strict Transport Security). Certificate transparency (CT) logs.
`openssl ca` for a proper CA with database tracking. ACME protocol (used
by certbot/Let's Encrypt). `openssl s_server` for test TLS servers.

**Level 4:**
mTLS (mutual TLS): both client and server present certificates. Used in
service meshes (Istio, Linkerd). Client certificate authentication in nginx
(`ssl_client_certificate`, `ssl_verify_client on`). Java trust store vs
key store (JKS, PKCS12). `keytool` for Java certificate management. SPIFFE
(Secure Production Identity Framework for Everyone): standardized workload
identities via X.509 certs.

**Level 5:**
PKCS#11 for hardware security modules (HSMs). Certificate lifecycle automation
(Vault PKI, cert-manager in Kubernetes, Netflix's Lemur). Short-lived certs
(hours) vs long-lived certs (years): trade-offs in revocation vs rotation.
CA/B Forum baseline requirements (what public CAs must follow). Post-quantum
cryptography migration: NIST-approved algorithms (Kyber, Dilithium) and
X.509 extensions for hybrid certs. Certificate Transparency (CT) log
monitoring for unauthorized certificate issuance (phishing detection).

---

### Code Example

**BAD - certificate mistakes:**
```bash
# BAD 1: Creating cert without SAN (works in curl but fails in Chrome):
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
    -days 365 -nodes \
    -subj "/CN=myapp.internal"
# Chrome/Firefox error: ERR_CERT_COMMON_NAME_INVALID (no SAN!)

# GOOD: Always add subjectAltName:
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
    -days 365 -nodes \
    -subj "/CN=myapp.internal" \
    -addext "subjectAltName=DNS:myapp.internal,DNS:localhost,IP:127.0.0.1"

# BAD 2: Trusting certificate from unknown URL:
curl --insecure https://internal-service/api
# -k/--insecure: disables ALL certificate verification
# MITM attacks succeed completely with this flag

# GOOD: add the internal CA to system trust store:
# echo "/path/to/ca.crt" >> /etc/ssl/certs/ca-certificates.crt  (BAD - don't edit directly)
cp ca.crt /usr/local/share/ca-certificates/
update-ca-certificates
# Now: curl https://internal-service/api (no -k needed)

# BAD 3: Private key stored with wrong permissions:
chmod 644 server.key   # world-readable!
# Anyone on the system can read the private key -> impersonate the server!

# GOOD: private keys must be 600 (owner read-only) or 400:
chmod 400 server.key    # read-only by owner
chown root server.key   # or the service user
```

**GOOD - cert expiry monitoring:**
```bash
#!/bin/bash
# check-cert-expiry.sh: Monitor certificate expiration

WARN_DAYS=30
CRIT_DAYS=7

check_cert_file() {
    local certfile=$1
    local expiry_date
    expiry_date=$(openssl x509 -in "$certfile" -noout -enddate 2>/dev/null | cut -d= -f2)
    if [[ -z "$expiry_date" ]]; then
        echo "ERROR: Cannot read $certfile"
        return 2
    fi
    
    expiry_epoch=$(date -d "$expiry_date" +%s)
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
    
    subject=$(openssl x509 -in "$certfile" -noout -subject 2>/dev/null | sed 's/subject=//')
    
    if [[ $days_left -lt $CRIT_DAYS ]]; then
        echo "CRITICAL: $certfile ($subject) expires in $days_left days!"
        return 2
    elif [[ $days_left -lt $WARN_DAYS ]]; then
        echo "WARNING: $certfile ($subject) expires in $days_left days"
        return 1
    else
        echo "OK: $certfile ($subject) expires in $days_left days"
        return 0
    fi
}

check_remote_cert() {
    local host=$1
    local port=${2:-443}
    
    cert=$(echo | openssl s_client -connect "$host:$port" \
        -servername "$host" 2>/dev/null | openssl x509 2>/dev/null)
    if [[ -z "$cert" ]]; then
        echo "ERROR: Cannot connect to $host:$port"
        return 2
    fi
    
    echo "$cert" > /tmp/check_cert_$$.pem
    check_cert_file /tmp/check_cert_$$.pem
    rm -f /tmp/check_cert_$$.pem
}

# Check files:
for cert in /etc/nginx/ssl/*.crt /etc/letsencrypt/live/*/cert.pem; do
    [[ -f "$cert" ]] && check_cert_file "$cert"
done

# Check remote:
for host in example.com api.example.com; do
    check_remote_cert "$host"
done
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "HTTPS with any certificate is secure against eavesdropping" | HTTPS with a valid certificate (even self-signed if trusted by client) provides encryption. But certificate validation is what prevents MITM. If the client uses `-k` / `--insecure` or trusts all certificates, an attacker can present their own certificate and decrypt the traffic. HTTPS security = encryption AND certificate validation. Self-signed certs are secure if the client explicitly trusts them (not via skip-verify). |
| "Let's Encrypt certificates are less secure than paid CA certs" | Let's Encrypt uses the same X.509 standard, the same RSA/ECDSA algorithms, and the same chain of trust as any other CA. The difference is validation level: DV (Domain Validated, Let's Encrypt) only verifies you control the domain. OV (Organization Validated) and EV (Extended Validation, green bar) verify organizational identity. For encryption security, they are identical. The "paid CA = more secure" perception is a marketing artifact. |
| "You need to restart the service to pick up a new certificate" | It depends on the service and how certificates are loaded. Nginx and Apache use `reload` (graceful): `nginx -s reload` or `systemctl reload nginx` - reloads config including certificates with zero downtime. A full `restart` drops existing connections. For certbot auto-renewal: it issues a `reload` after renewal (not restart). Some services support hot reload of certificates (Java with a custom SSLContext reload). Certbot's `--deploy-hook` handles this automatically. |
| "A wildcard certificate covers all subdomains at any depth" | A wildcard cert (`*.example.com`) covers EXACTLY ONE level of subdomain: `api.example.com` YES, `www.example.com` YES, but `api.v2.example.com` NO (two levels deep, wildcard doesn't match). The bare domain `example.com` is also NOT covered by `*.example.com` - you need an explicit SAN for `DNS:example.com` in addition to `DNS:*.example.com`. Common mistake: getting a wildcard cert and wondering why the bare domain shows a cert error. |
| "The certificate file contains the private key" | The certificate (`.crt`/`.pem`) contains the PUBLIC key and metadata signed by the CA. The private key is a separate file (`.key`). The certificate is public - it's sent to every client during TLS. The private key must be kept secret. A certificate without its private key is useless for TLS. A private key without the certificate is also useless. They must be paired. CSR (Certificate Signing Request) is also public - you send it to the CA, and they return the signed certificate. The private key never leaves your server. |

---

### Failure Modes & Diagnosis

**TLS certificate errors - complete diagnosis:**
```bash
# Error 1: "certificate has expired" or "certificate is not yet valid"
# Diagnose:
echo | openssl s_client -connect myservice:443 2>/dev/null \
    | openssl x509 -noout -dates
# notBefore=Jan  1 00:00:00 2020 GMT
# notAfter=Jan  1 00:00:00 2021 GMT   <- expired!

# Fix: obtain new cert (certbot renew or generate new self-signed)
# Immediate temporary fix for self-signed:
openssl req -x509 -key existing.key -out new.crt -days 365 \
    -addext "subjectAltName=DNS:myservice.internal"

# Error 2: "cannot verify certificate" or "self-signed certificate in chain"
# Check full chain:
echo | openssl s_client -connect myservice:443 -showcerts 2>/dev/null
# If chain shows: s:/CN=myservice  i:/CN=MyOrg CA
#                 s:/CN=MyOrg CA   i:/CN=MyOrg CA  (self-signed root)
# Client doesn't have "MyOrg CA" in trust store

# Fix: distribute CA cert and update trust store
openssl verify -CAfile myorg-ca.crt myservice.crt
# myservice.crt: OK  (if CA is correct)

# Error 3: "hostname mismatch" 
echo | openssl s_client -connect myservice:443 2>/dev/null \
    | openssl x509 -noout -text | grep -A2 "Subject Alternative"
# No SANs or wrong hostnames!
# Fix: reissue cert with correct SANs

# Error 4: Check nginx is loading the right cert:
nginx -T 2>/dev/null | grep "ssl_certificate "
# Then: openssl x509 -in THAT_FILE -noout -text
```

---

### Related Keywords

**Foundational:**
LNX-033 (SSH - key/cert concepts), LNX-057 (Security)

**Builds on this:**
LNX-058 (SSH Advanced)

**Related:**
LNX-026 (Networking - TLS/HTTPS context)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `openssl x509 -in cert.pem -noout -enddate` | Check cert expiry |
| `openssl s_client -connect host:443` | Debug TLS connection |
| `openssl req -x509 -newkey rsa:2048 -keyout k.pem -out c.pem -days 365 -nodes` | Self-signed cert |
| `openssl genrsa -out key.pem 4096` | Generate private key |
| `openssl req -new -key k.pem -out req.csr` | Create CSR |
| `openssl verify -CAfile ca.crt cert.crt` | Verify cert chain |
| `update-ca-certificates` | Rebuild CA bundle (Ubuntu) |
| `update-ca-trust extract` | Rebuild CA bundle (RHEL) |

**3 things to remember:**
1. Always include `subjectAltName` (SAN) - modern browsers require it, CN alone is not accepted
2. Private keys must be `chmod 400` and never shared; the `.crt` file is public (sent to every client)
3. `update-ca-certificates` (Ubuntu) or `update-ca-trust extract` (RHEL) after adding a CA to the system trust store

---

### Transferable Wisdom

Certificate concepts appear in: Kubernetes uses TLS everywhere - etcd, API
server, kubelets all use certificates. `cert-manager` automates certificate
lifecycle in Kubernetes (requests, renewal, distribution as Secrets). AWS
ACM (Certificate Manager) = certbot in the cloud: auto-renews public certs
for ALB/CloudFront. mTLS in service meshes (Istio, Linkerd): every service
gets a SPIFFE-formatted certificate for mutual authentication. Docker image
signing (Notary/Cosign): images signed with X.509 certificates. JWT tokens
use public/private keys but not X.509 format (though they solve a similar
problem: "proving identity"). The trust hierarchy concept (root CA -> intermediate
CA -> leaf cert) appears in organizational hierarchies: top-level admin grants
intermediate managers authority, who grant end users access.

---

### The Surprising Truth

The CA/B Forum baseline requirements state that public CA-signed certificates
can have a maximum validity of 397 days (since 2020, down from 825 days in
2018, down from multi-year). Apple's Safari enforces 398-day maximum - ANY
certificate with longer validity is rejected. This is intentional: shorter-
lived certificates force more frequent renewal, ensuring that if a private
key is compromised, the damage window is limited. The surprising implication:
Let's Encrypt chose 90-day certificates not as a limitation but as a
SECURITY FEATURE. Shorter validity = smaller breach window + forced automation
(you can't manually renew every 90 days for 1000 services, so you MUST
automate). Companies that relied on 2-3 year certificates started having
mass outages when these certificates expired and nobody remembered to renew
them. The 90-day limit + automated renewal (certbot) was the correct
engineering response to the human failure mode of "manual certificate management
at scale." This is why Google, Microsoft, and Apple are pushing for even
shorter certificate lifetimes (proposals exist for 47-day maximums by 2025).

---

### Mastery Checklist

- [ ] Can inspect certificates (openssl x509 -noout -text, -enddate, -subject)
- [ ] Can create self-signed certificates with SAN for internal use
- [ ] Can add a custom CA to the Linux system trust store
- [ ] Can debug TLS certificate errors using openssl s_client
- [ ] Understands the CA chain verification process

---

### Think About This

1. A developer's curl command fails with "SSL: certificate problem: unable
   to get local issuer certificate" when connecting to an internal API.
   The API uses a certificate signed by your company's internal CA. Walk
   through the complete diagnosis using `openssl s_client` commands to
   understand the certificate chain, then describe the solution to make it
   work for ALL tools on the server (curl, wget, git, Python requests, etc.)
   without using `--insecure`.

2. You're setting up mTLS between microservices where both the client and
   server must present valid certificates. Using your internal CA, describe
   the certificate generation steps for both the server and client, the
   configuration in nginx to require client certificates, and how a client
   would present its certificate in a curl request.

3. A colleague argues that Let's Encrypt 90-day certificates are more work
   than annual purchased certificates because they need more frequent renewal.
   Argue the counter-position: why shorter certificate lifetimes are actually
   BETTER for security and operations at scale, and why the "more work"
   argument fails when automation is used.

---

### Interview Deep-Dive

**Foundational:**
Q: What happens when a browser encounters an HTTPS certificate it doesn't trust?
A: When a browser connects to HTTPS, it performs certificate chain validation: (1) SERVER PRESENTS CERTIFICATE: during TLS handshake, server sends its certificate (and optionally intermediate CA certificates). (2) CHAIN BUILDING: browser builds a chain: server cert -> intermediate CA(s) -> root CA. Root CA must be in the browser's (or OS's) trust store. (3) VALIDATION CHECKS (all must pass): (a) Time: is today within notBefore and notAfter dates? (b) Hostname: does the hostname match the CN or a SAN entry? Wildcards checked: `*.example.com` matches `api.example.com` but not `api.sub.example.com`. (c) Signature: verify each cert in chain is signed by the cert above it. Use the issuer's public key to verify the signature. (d) Revocation: check OCSP (if OCSP stapling is used) or CRL. (e) Key usage: is the cert authorized for "serverAuth"? (f) Path length: for CAs, is path depth within allowed limit? FAILURE RESULTS: expired = ERR_CERT_DATE_INVALID. Hostname mismatch = ERR_CERT_COMMON_NAME_INVALID. Unknown CA = ERR_CERT_AUTHORITY_INVALID. Self-signed (root = leaf) = ERR_CERT_AUTHORITY_INVALID. Each error type maps to a specific presentation (warning page, red lock, etc.). For self-signed and internal CA certs: the only correct fix is adding the CA to the trust store (not clicking "proceed anyway" in production). The trust store on Linux: `/etc/ssl/certs/ca-certificates.crt` (Ubuntu) or `/etc/pki/tls/certs/ca-bundle.crt` (RHEL). Updated by `update-ca-certificates` or `update-ca-trust extract`.

**Expert:**
Q: Explain mTLS and how you would set it up for microservice-to-microservice communication.
A: mTLS (mutual TLS) extends regular TLS by requiring BOTH parties to present valid certificates. In regular TLS: only the server is authenticated (client is anonymous). In mTLS: client also presents a certificate, server verifies it. Use case: microservice authentication without API keys or passwords. If service A has a valid certificate signed by the internal CA, service B can trust it is who it claims to be. Setup with internal CA: (1) SHARED CA: all services must trust the same CA (install CA cert system-wide or in service-specific trust). (2) SERVICE CERTIFICATES: each service gets its own key+cert. Example for service A: `openssl genrsa -out service-a.key 2048 && openssl req -new -key service-a.key -out service-a.csr -subj "/CN=service-a"` then sign with internal CA. The CN or a custom extension can encode the service identity. (3) SERVER CONFIGURATION (nginx): `ssl_certificate /certs/service-b.crt; ssl_certificate_key /certs/service-b.key; ssl_client_certificate /certs/ca.crt; ssl_verify_client on;` - server requires client cert signed by ca.crt. (4) CLIENT CONFIGURATION: `curl --cert service-a.crt --key service-a.key --cacert ca.crt https://service-b/api`. Or in code: configure SSLContext with both truststore (CA cert) and keystore (client cert+key). SPIFFE standard: defines URI-format identities (`spiffe://cluster/service/service-a`) embedded as SANs in certificates. Istio/Linkerd generate SPIFFE certs for every pod via a component called the CA (Citadel in Istio). The sidecar proxies (Envoy) terminate and initiate mTLS transparently - application code doesn't need to handle certificates at all. This is why service meshes are a common choice for zero-trust microservice security.
