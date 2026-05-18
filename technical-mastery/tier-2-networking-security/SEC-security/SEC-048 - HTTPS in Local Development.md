---
id: SEC-048
title: "HTTPS in Local Development"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-002, SEC-003, SEC-012, SEC-038, SEC-039
used_by: SEC-074
related: SEC-002, SEC-003, SEC-012, SEC-038, SEC-039, SEC-074
tags:
  - security
  - https
  - local-development
  - mkcert
  - tls
  - certificates
  - secure-cookies
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/sec/https-for-local-development/
---

⚡ TL;DR - Many security features only work over HTTPS:
Secure cookies, SameSite cookies, HSTS, modern browser APIs
(Geolocation, Service Workers, WebCrypto). If you develop on
HTTP, you cannot test these features accurately. `mkcert`
creates locally-trusted certificates in 60 seconds.

**Setup in two commands:**
```bash
# Install mkcert (macOS)
brew install mkcert
mkcert -install  # Installs local CA into OS/browser trust stores

# Create certificate for localhost
mkcert localhost 127.0.0.1 ::1
# Creates: localhost+2.pem (cert), localhost+2-key.pem (key)
```

Then configure your dev server to use these files. Done.
Your browser trusts the certificate natively (no warnings).

---

| #048 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTPS and TLS Basics, SSL/TLS Certificates, Security Headers, HTTPS Certificate Configuration, Session Security | |
| **Used by:** | TLS Configuration Best Practices | |
| **Related:** | TLS, Certificates, Secure Cookies, SameSite, mkcert, ngrok | |

---

### 🔥 The Problem This Solves

**FEATURES THAT REQUIRE HTTPS AND BREAK ON HTTP:**

```
SECURE COOKIE ATTRIBUTE:
  Set-Cookie: session=abc; Secure; HttpOnly; SameSite=Lax
  
  The 'Secure' attribute means the cookie is ONLY sent over HTTPS.
  On HTTP (localhost): the Secure cookie is never sent.
  Test behavior: login works locally (HTTP, cookie sent),
    fails in staging/production (HTTPS, Secure cookie required,
    but locally you didn't test with Secure attribute).
  
  Result: "It worked on my machine" - but the Secure attribute
  was suppressing the cookie in production. Bug found in production.

SAMESITE=NONE;SECURE (required for third-party cookies):
  If your app sets cookies that need to be sent cross-site
  (e.g., OAuth flows, embedded content), you need:
  SameSite=None; Secure
  
  Browsers IGNORE SameSite=None on HTTP connections.
  Cannot test this behavior without HTTPS.

SERVICE WORKERS (PWA features):
  Service workers only register on HTTPS (or localhost).
  But: localhost exception exists in Chrome/Firefox.
  Custom hostname (app.local): requires HTTPS.

WEBAUTHN / FIDO2 (Passkeys):
  Passkeys are bound to an HTTPS origin.
  Cannot test WebAuthn at all on HTTP (even localhost).
  Must use HTTPS or 127.0.0.1 (not custom hostnames).

GEOLOCATION API:
  Chrome requires HTTPS or localhost for Geolocation.
  Android Chrome: requires HTTPS (no localhost exception on mobile).

HSTS PRELOADING BEHAVIOR:
  Cannot test HSTS behavior locally on HTTP.
  Testing HTTPS locally: verify HSTS header is sent,
  HTTPS redirect works, HSTS preload criteria are met.

MIXED CONTENT BLOCKING:
  When testing HTTPS in staging: mixed content warnings
  may appear for resources loaded over HTTP.
  Local HTTPS testing catches these before staging deployment.
```

---

### 📘 Textbook Definition

**Local HTTPS Development:** Running your development server
with TLS (HTTPS) to accurately replicate production security
behavior, particularly for browser APIs and cookie attributes
that require a secure context.

**Secure Context:** A browser concept (W3C specification).
A window or worker is in a "secure context" if it is:
- Delivered over HTTPS with a valid certificate
- `localhost` or `127.0.0.1` (exception for local development)
- A custom hostname over HTTPS with a trusted certificate

Many modern Web APIs are restricted to secure contexts.

**mkcert:** A simple tool by Filippo Valsorda that creates
locally-trusted TLS certificates. It installs its own
Certificate Authority (CA) into the OS trust store and
browser trust stores. Certificates signed by this local CA
are automatically trusted by browsers on that machine - no
certificate warnings.

**Self-signed certificates vs mkcert:**
- Self-signed: browser shows "NET::ERR_CERT_AUTHORITY_INVALID"
  warning. Developers click "proceed anyway" repeatedly.
  Security warning becomes noise (trains developers to ignore warnings).
- mkcert: browser trusts the certificate silently.
  Same user experience as production HTTPS.
  Better developer experience and trains correct security habits.

**ngrok:** A tunneling service that creates a public HTTPS URL
for your local server. External services (Stripe webhooks,
GitHub webhooks) can send HTTP requests to your local server.
Useful for: testing webhooks, testing mobile apps against
local backend, sharing in-progress work with teammates.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Use `mkcert` to get a locally-trusted TLS certificate for
localhost in 60 seconds, then configure your dev server
to use it. Your browser accepts it without warnings,
and Secure cookies work exactly as they do in production.

**One analogy:**
> Local HTTPS is like a full dress rehearsal vs a costume fitting.
> Testing security features on HTTP (localhost) is a costume fitting:
> you verify the costume fits, but the lighting is wrong, the stage
> isn't set, and the audience isn't there. Secure cookie behavior,
> browser HTTPS requirements, mixed content blocking - none of these
> apply in the fitting room (HTTP localhost).
> HTTPS in local development is the full dress rehearsal:
> same lighting (browser security model), same stage (HTTPS context),
> same costume (Secure cookies, SameSite, etc.).
> Bugs caught in dress rehearsal are far cheaper than bugs
> discovered on opening night (production incident).

---

### 🔩 First Principles Explanation

**How mkcert works and why it's trusted:**

```
PKI REVIEW (why certificate trust works):

  Normal HTTPS: Let's Encrypt (public CA) issues cert for example.com.
  Browser trusts Let's Encrypt (in its built-in CA root store).
  Browser trusts example.com's cert (because LE signed it).
  
  Self-signed cert: Your server creates its own cert AND signs it.
  Browser: "This cert signed by nobody I know. UNSAFE."
  Result: ERR_CERT_AUTHORITY_INVALID warning.

MKCERT APPROACH:

  Step 1: mkcert creates a local Certificate Authority (CA):
    Private key: ~/.local/share/mkcert/rootCA-key.pem
    Root certificate: ~/.local/share/mkcert/rootCA.pem
  
  Step 2: mkcert -install → installs rootCA.pem into:
    OS trust store (macOS Keychain, Windows Cert Store, Linux /usr/local/share/ca-certificates/)
    Firefox NSS trust store (separately, since Firefox has its own)
    Chrome uses OS trust store (handled by OS install)
  
  Step 3: mkcert localhost 127.0.0.1 ::1 → creates cert:
    localhost+2.pem (certificate, signed by local CA)
    localhost+2-key.pem (private key)
  
  Browser behavior:
    Sees: cert for localhost, signed by mkcert Local CA
    Checks: is mkcert Local CA in trust store? YES (we installed it)
    Result: trusts the cert. No warning. Green padlock.
  
  SECURITY NOTE: The rootCA-key.pem is the local CA private key.
    Anyone with this key can create trusted certs for any domain.
    This is why mkcert-generated certs should NEVER be used in
    production or shared environments. They are only for local
    development on that specific machine.

DEV SERVER CONFIGURATION:

  The certificate files are just TLS cert + key.
  Any server that supports TLS can use them.
  
  Configuration differs by server/framework:
  
  Node.js (https module):
    const https = require('https');
    const fs = require('fs');
    const options = {
      key: fs.readFileSync('localhost+2-key.pem'),
      cert: fs.readFileSync('localhost+2.pem'),
    };
    https.createServer(options, app).listen(443);
  
  Python (Flask):
    app.run(ssl_context=('localhost+2.pem', 'localhost+2-key.pem'))
  
  nginx:
    server {
      listen 443 ssl;
      ssl_certificate /path/to/localhost+2.pem;
      ssl_certificate_key /path/to/localhost+2-key.pem;
    }
  
  Vite (React dev server):
    vite.config.js:
    import { defineConfig } from 'vite';
    import basicSsl from '@vitejs/plugin-basic-ssl';
    // OR: use mkcert plugin
    import mkcert from 'vite-plugin-mkcert';
    export default defineConfig({
      plugins: [mkcert()],  // Handles mkcert automatically
      server: { https: true }
    });
  
  Create React App:
    HTTPS=true npm start  # Self-signed cert (browser warning)
    # Better: use react-scripts with mkcert certs via HTTPS options

NGROK FOR EXTERNAL ACCESS:

  Local server: http://localhost:3000
  ngrok: ngrok http 3000
  Public URL: https://abc123.ngrok.io → proxies to localhost:3000
  
  Use cases:
    Stripe webhooks: configure Stripe dashboard to POST to ngrok URL
    GitHub webhooks: same pattern
    Mobile app testing: phone accesses ngrok URL (no localhost)
    Sharing with remote teammate: send ngrok URL
  
  Limitation: URL changes on every ngrok restart (free plan).
    Fix: ngrok paid plan (reserved domains) or cloudflare tunnel.
  
  Security note: ngrok URL is publicly accessible.
    Don't expose development data or admin interfaces via ngrok.
    Protect with basic auth if needed: ngrok http -auth "user:pass" 3000
```

---

### 🧪 Thought Experiment

**SCENARIO: OAuth 2.0 flow broken in staging but not in development**

```
PROBLEM:
  Developer builds OAuth 2.0 login (Google SSO).
  Works perfectly on http://localhost:3000.
  Deployed to staging (https://staging.example.com): OAuth fails.
  Error: redirect_uri_mismatch from Google.

ROOT CAUSE INVESTIGATION:
  Step 1: Check registered redirect URIs in Google Console:
    http://localhost:3000/auth/callback ← for local dev
    https://staging.example.com/auth/callback ← for staging
  
  Step 2: Trace the actual redirect URI being sent:
    Local: redirect_uri=http://localhost:3000/auth/callback (matches)
    Staging: redirect_uri=http://staging.example.com/auth/callback (MISMATCH!)
  
  Problem found: the redirect URI is built as:
    redirect_uri = request.scheme + "://" + request.host + "/auth/callback"
    
    Local: request.scheme = "http" → builds HTTP URL
    Staging: nginx reverse proxy, app sees scheme="http" even though
      nginx serves HTTPS. App builds HTTP redirect URI.
      Google registered HTTPS URI, app sends HTTP → mismatch.

SECONDARY PROBLEM (discovered while fixing):
  The session cookie was not set with the 'Secure' attribute:
  Set-Cookie: session=abc123; HttpOnly; SameSite=Lax
  (missing Secure attribute)
  
  During OAuth flow: browser makes cross-origin requests.
  Session cookie without Secure: works on HTTP dev,
  but in staging: cookie is sent on HTTP subrequests
  that should be HTTPS-only. Security audit would flag this.
  
  Had developer tested with local HTTPS: they would have
  seen the Secure attribute requirement BEFORE staging deployment.

PREVENTION WITH LOCAL HTTPS:
  Test entire OAuth flow on https://localhost:3000 (mkcert cert).
  1. redirect_uri built correctly as HTTPS (matches Google console)
  2. Secure cookie attribute tested locally (not discovered at staging)
  3. CORS behavior with HTTPS origins tested (not just HTTP)
  3. All cross-origin cookie behavior (SameSite) accurately tested.
  
  Result: staging environment confirms correct behavior,
  not discovers new bugs.
```

---

### 🧠 Mental Model / Analogy

> Setting up local HTTPS is like installing the full production
> safety system on a car during the design phase.
>
> Testing on HTTP localhost is like designing a car in a wind
> tunnel without actually simulating wind: you can test the
> basic mechanics (doors open, wheels turn), but the aerodynamics
> (security features that require HTTPS) are invisible.
>
> When the car goes on the real road (production):
> the wind creates unexpected problems (Secure cookies don't send,
> Service Workers don't register, WebAuthn doesn't work).
>
> mkcert is the wind tunnel upgrade: same physical setup,
> but now the actual environmental conditions (browser HTTPS
> requirements) are accurately simulated during development.
> Aerodynamic problems (security feature incompatibilities)
> are discovered in the design phase, not on the test track.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Some browser features only work on secure HTTPS websites, not plain HTTP. Even on localhost. When developers test on `http://localhost`, those features work differently than in production. mkcert is a simple tool that creates a trusted HTTPS certificate for localhost in 60 seconds, so your browser treats your local dev server exactly like a real HTTPS website.

**Level 2 - How to use it (junior developer):**
`brew install mkcert && mkcert -install && mkcert localhost 127.0.0.1`. This creates two files: `localhost+2.pem` (certificate) and `localhost+2-key.pem` (private key). Point your dev server at these files. For Vite: `vite-plugin-mkcert`. For webpack dev server: set `https: {key: '...key.pem', cert: '...pem'}`. Your browser now shows the green lock for localhost. Secure cookies work. Test OAuth flows. Test SameSite behavior.

**Level 3 - How it works (mid-level engineer):**
mkcert installs a local root CA into the OS/browser trust stores. All certificates signed by this local CA are automatically trusted by browsers on your machine. The certificate files mkcert generates are standard PEM-format TLS cert and key - any web server or Node.js HTTPS server can use them. For Docker-based development: bind-mount the mkcert certificates into the container or generate them inside the container (mkcert works on Linux). For team environments: each developer runs mkcert locally (the generated certs are unique to each machine and should not be shared).

**Level 4 - Why it was designed this way (senior/staff):**
The browser's "secure context" requirement exists because many powerful APIs (Geolocation, Service Workers, WebCrypto, WebAuthn) have significant privacy and security implications. Restricting them to HTTPS ensures the user is on an authenticated, encrypted connection before granting access. The localhost exception (`127.0.0.1` and `localhost`) was added to accommodate development workflows. But custom hostnames (like `myapp.local` pointing to `127.0.0.1`) don't get the localhost exception - they need real HTTPS. mkcert allows using custom hostnames with HTTPS in development: `mkcert myapp.local` creates a trusted cert for that hostname. This enables a production-like setup (custom subdomain routing) in development without real DNS or certificates.

**Level 5 - Mastery (distinguished engineer):**
Enterprise development environments often need HTTPS for entire microservice stacks (service-to-service HTTPS, mutual TLS). Tooling: `mkcert` for individual services, or a development Certificate Authority that the team shares (using Vault PKI secrets engine in development mode, or step-ca from Smallstep). step-ca provides an ACME-compatible CA: each service can use standard ACME certificate management (same as Let's Encrypt) against the development CA. This gives you zero-config HTTPS across all services via `certbot` or `acme.sh` pointing at the dev CA endpoint. Production parity: ACME certificate rotation is tested in development, not only in production.

---

### ⚙️ How It Works (Mechanism)

**mkcert installation and certificate lifecycle:**

```
MKCERT SETUP (cross-platform):

macOS:
  brew install mkcert nss  # nss for Firefox support
  mkcert -install          # Install root CA
  mkcert localhost 127.0.0.1 ::1  # Generate cert

Linux (Ubuntu/Debian):
  sudo apt install libnss3-tools
  curl -JLO https://dl.filippo.io/mkcert/latest?for=linux/amd64
  chmod +x mkcert-v*-linux-amd64
  sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert
  mkcert -install
  mkcert localhost 127.0.0.1 ::1

Windows:
  choco install mkcert     # Or: winget install mkcert
  mkcert -install
  mkcert localhost 127.0.0.1 ::1

DOCKER DEVELOPMENT WITH HTTPS:
  # Option 1: Mount host mkcert certs into container
  # Get mkcert root dir:
  mkcert -CAROOT  # e.g., /Users/you/Library/Application Support/mkcert
  
  # Generate cert for container hostname
  mkcert app.local 127.0.0.1
  
  # docker-compose.yml:
  services:
    web:
      volumes:
        - ./app.local+1.pem:/certs/cert.pem:ro
        - ./app.local+1-key.pem:/certs/key.pem:ro
      environment:
        - TLS_CERT=/certs/cert.pem
        - TLS_KEY=/certs/key.pem
  
  # Option 2: Generate cert inside container (mkcert binary)
  # More complex: requires extracting CA cert from container
  # and installing in host trust store. Option 1 is simpler.

CERTIFICATE VALIDITY PERIOD:
  mkcert certificates are valid for 825 days (~2 years).
  You don't need to renew frequently.
  If certificate expires: just run mkcert again.
```

---

### 💻 Code Example

**Framework-specific HTTPS dev server setup:**

```javascript
// Vite (React, Vue, Svelte) - easiest approach
// npm install -D vite-plugin-mkcert

// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import mkcert from 'vite-plugin-mkcert';

export default defineConfig({
    server: {
        https: true,  // Enable HTTPS
        port: 3000,
    },
    plugins: [
        react(),
        mkcert(),  // Automatically runs mkcert and configures HTTPS
        // First run: installs mkcert if not present, generates cert
        // Subsequent runs: reuses existing cert
    ],
});
// Access: https://localhost:3000 (no browser warning)
```

```python
# Flask with HTTPS
# pip install flask

# Generate cert first: mkcert localhost 127.0.0.1
# Creates: localhost+1.pem, localhost+1-key.pem

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "HTTPS Development Server"

if __name__ == '__main__':
    app.run(
        host='localhost',
        port=5000,
        ssl_context=(
            'localhost+1.pem',
            'localhost+1-key.pem'
        ),
        debug=True
    )
# Access: https://localhost:5000
```

```bash
# nginx reverse proxy for local HTTPS
# nginx.conf for local development:

server {
    listen 443 ssl;
    server_name localhost;
    
    ssl_certificate     /path/to/localhost+2.pem;
    ssl_certificate_key /path/to/localhost+2-key.pem;
    
    location / {
        proxy_pass http://localhost:8080;  # App on HTTP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        # X-Forwarded-Proto: tells the app it's being served over HTTPS
        # Important for building correct redirect URIs in OAuth flows
    }
}

server {
    listen 80;
    server_name localhost;
    return 301 https://$host$request_uri;  # HTTP → HTTPS redirect
}
```

---

### ⚖️ Comparison Table

| Approach | Browser Trust | Setup Time | Suitable For | Limitation |
|:---|:---|:---|:---|:---|
| **HTTP localhost** | N/A (no TLS) | None | Basic development | Missing Secure cookies, Service Workers |
| **Self-signed cert** | Warning shown | 5 min | When mkcert unavailable | Trains devs to click through warnings |
| **mkcert** | Trusted (no warning) | 2 min | Local machine dev | Not shareable; machine-specific |
| **ngrok** | Trusted (ngrok CA) | 2 min | Webhook testing, external access | URL changes; public exposure |
| **Cloudflare Tunnel** | Trusted | 10 min | Team-shared tunnel | Requires Cloudflare account |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| localhost always exempted from HTTPS requirements | `localhost` and `127.0.0.1` do get a "secure context" exemption in modern browsers for most APIs. However: (1) custom hostnames like `myapp.local` (even pointing to 127.0.0.1 via /etc/hosts) do NOT get this exemption, (2) some APIs require HTTPS even on localhost in certain mobile browser configurations, (3) the exemption doesn't mean Secure cookies work on HTTP localhost - they don't. Secure cookies require HTTPS regardless of the host. Testing cookie behavior accurately requires HTTPS even on localhost. |
| mkcert root CA key is a security risk | mkcert's root CA key (`~/.local/share/mkcert/rootCA-key.pem`) could theoretically be used to create certificates trusted by your machine for any domain, enabling MITM attacks. This is why mkcert is development-only. The risk is limited to your local machine: only your OS and browsers trust this CA. It's not in public CA stores. If your development machine is compromised, the root CA key being there is the least of your problems. Treat the mkcert CA key like any other private key: don't share it, don't commit it to version control. But don't treat it as a higher-than-normal security risk for typical development use. |

---

### 🚨 Failure Modes & Diagnosis

**Common HTTPS local dev issues:**

```
ISSUE: mkcert cert not trusted (browser still shows warning)
  
  Cause: Firefox has its own certificate trust store (NSS).
    mkcert -install only handles Firefox if 'nss' is installed:
    brew install nss (macOS)
    sudo apt install libnss3-tools (Linux)
    Then re-run: mkcert -install
  
  Also: Firefox must be closed when mkcert -install runs.

ISSUE: Secure cookies not sent on HTTPS localhost
  
  Check: is the cookie actually set with 'Secure' attribute?
  Browser DevTools → Application → Cookies
  Look for: Secure column = YES
  If Secure = NO: code is not setting the Secure attribute.
  
  Note: In Chrome, there's an exception:
    Cookies without Secure attribute on localhost ARE sent via HTTPS.
    But if Secure IS set, they're not sent via HTTP.
    Test in Firefox for stricter behavior.

ISSUE: ngrok webhook URL rejected by external service
  
  Cause: ngrok URL changes on every restart (free plan).
  Fix: re-configure external service (Stripe, GitHub) webhook
    URL each time. OR upgrade to paid ngrok for stable domain.
    OR use: cloudflare tunnel (free, stable subdomain).

ISSUE: "Warning: certificate expired" in CI/CD Docker test
  
  Cause: mkcert cert mounted into CI container, but
    mkcert root CA not in container's trust store.
  
  Fix: copy mkcert root CA into container:
    CAROOT=$(mkcert -CAROOT)
    docker cp $CAROOT/rootCA.pem my-container:/usr/local/share/ca-certificates/
    docker exec my-container update-ca-certificates
  
  Better fix: use a self-signed cert for CI testing
    (CI doesn't need browser trust), or use http in unit tests
    and HTTPS only in integration tests with a real cert.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `HTTPS and TLS Basics` - how HTTPS works
- `SSL/TLS Certificates` - certificate concepts
- `Session Security` - Secure cookie attribute behavior
- `HTTPS Certificate Configuration` - production TLS setup

**Builds on this:**
- `TLS Configuration Best Practices` - TLS hardening beyond basic setup

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INSTALL      │ brew install mkcert && mkcert -install    │
├──────────────┼───────────────────────────────────────────┤
│ CREATE CERT  │ mkcert localhost 127.0.0.1 ::1            │
│              │ → localhost+2.pem + localhost+2-key.pem   │
├──────────────┼───────────────────────────────────────────┤
│ FIREFOX      │ brew install nss; then mkcert -install    │
├──────────────┼───────────────────────────────────────────┤
│ VITE         │ vite-plugin-mkcert (auto-handles all)     │
├──────────────┼───────────────────────────────────────────┤
│ WEBHOOKS     │ ngrok http 3000 → temporary HTTPS URL     │
├──────────────┼───────────────────────────────────────────┤
│ NEVER        │ Commit mkcert CA key or cert to git       │
│              │ Use mkcert certs in production            │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Test in an environment that matches production constraints."
The further your development environment diverges from
production, the more bugs you discover in production
rather than development. HTTP vs HTTPS is a significant
divergence with measurable consequences for security features.
The principle extends beyond HTTPS: test with production-like
data volumes (performance divergence), production-like
infrastructure (Docker/Kubernetes in dev), production-like
network conditions (latency simulation), and production-like
security constraints (HTTPS, strict CSP, no debug mode).
Each deviation is a class of bugs that can only be discovered
in production. The cost of "production-like development environment"
is setup time. The cost of "bugs discovered in production"
is incident response, customer impact, and security exposure.
The economics favor investment in environment parity.

---

### 💡 The Surprising Truth

Google Chrome's security team decided in 2019 that `SameSite=Lax`
would become the DEFAULT for cookies that don't specify SameSite
at all (rather than `SameSite=None` which was the previous default).
This change rolled out in Chrome 80 (February 2020).
The immediate effect: thousands of web applications that
hadn't thought about SameSite at all suddenly had broken OAuth
flows and cross-site form submissions. Developers who tested
on HTTP localhost didn't see this change during development
because SameSite behavior differs between HTTP and HTTPS contexts.
The change primarily affected HTTPS origins. Testing on HTTP
localhost with SameSite=Lax cookies gives a false signal:
everything appears to work. Deploying to HTTPS production:
SameSite constraints apply strictly, and cross-site flows break.
This was one of the most widespread "works locally, breaks in
production" incidents of 2020 - caused by the HTTP vs HTTPS
development gap.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **SET UP** mkcert for localhost HTTPS development and configure
   a dev server (Node.js, Python, nginx) to use the generated certs.
2. **EXPLAIN** which browser features require HTTPS/secure context and
   cannot be accurately tested on HTTP localhost.
3. **CONFIGURE** ngrok for local webhook testing with an external service.
4. **TROUBLESHOOT** certificate trust issues (Firefox NSS, Docker containers).

---

### 🎯 Interview Deep-Dive

**Q: Why might you need HTTPS in local development? What tool
would you use and how?**

*Why they ask:* Tests understanding of the browser's security
model and practical tooling knowledge. Good signal for security-aware
developers who have actually dealt with these issues.

*Strong answer includes:*
- Specific browser features that require HTTPS: Secure cookies,
  SameSite=None, Service Workers, WebAuthn/Passkeys, Geolocation.
  Without local HTTPS: can't accurately test these.
- Real-world example: OAuth flow that works on HTTP localhost
  fails in staging because redirect URI scheme mismatch (HTTP vs HTTPS).
  Or: Secure cookies not sent on HTTP, discovered in production.
- Tool: mkcert. Install: `brew install mkcert && mkcert -install`.
  Generate: `mkcert localhost 127.0.0.1`. Browser trusts the cert
  (no warning) because mkcert installs a local CA into trust stores.
- Difference from self-signed: self-signed shows browser warning,
  mkcert is silently trusted. Better developer experience and
  doesn't train developers to click through security warnings.
- For webhooks: ngrok creates a public HTTPS tunnel to localhost.
  Use case: Stripe/GitHub webhooks during development.
- Key insight: mkcert is development-only. The CA key it installs
  is local to your machine. Never use mkcert certs in production.