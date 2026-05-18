---
id: OAU-029
title: "Device Authorization Flow (RFC 8628)"
category: OAuth 2.0 & OpenID Connect
tier: tier-2-networking-security
folder: OAU-oauth
difficulty: ★★☆
depends_on: OAU-006, OAU-007, OAU-017, OAU-018
used_by: OAU-036, OAU-043, OAU-050
related: OAU-009, OAU-010, OAU-018, OAU-021, OAU-022
tags:
  - security
  - oauth
  - device-flow
  - iot
  - cli
  - rfc-8628
status: complete
version: 5
layout: default
parent: "OAuth 2.0 & OpenID Connect"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/oauth/device-authorization-flow/
---

⚡ TL;DR - The Device Authorization Flow (RFC 8628) solves
OAuth for devices that can't handle browser redirects: smart
TVs, CLI tools (`gh auth login`, `az login`), IoT sensors.
Phase 1: device POSTs to `/device_authorization`, receives
`device_code`, `user_code` (short, human-typable), and
`verification_uri`. Phase 2: device displays the user_code
and polls `/token` with `grant_type=urn:ietf:params:oauth:
grant-type:device_code`. In parallel, the user opens
verification_uri on a different device (phone/laptop), enters
the user_code, and approves. Once approved, the next device
poll returns tokens. No redirect_uri required.

---

### 🔥 The Problem This Solves

**THE INPUT-CONSTRAINED DEVICE PROBLEM:**

Standard OAuth 2.0 requires: a browser (for redirect to AS),
a redirect_uri that the AS can send the authorization code to,
and a capable browser that can handle cookies, JavaScript, and
URL navigation. Devices like Apple TV, Roku, CLI tools in
headless environments, and IoT sensors have none of these.
They may have no browser, no way to receive inbound HTTP
redirects, and no keyboard for entering passwords.

**THE SOLUTION:**

Decouple the user interaction (which happens on a capable
device - phone or computer) from the requesting device (which
only needs to make HTTP POST requests). The device polls;
the user authenticates on their own device.

---

### 📘 Textbook Definition

The OAuth 2.0 Device Authorization Grant (RFC 8628) is a grant
type designed for devices that cannot open a browser window or
receive redirects. It introduces a two-phase, two-device
interaction model:

**Phase 1 - Device Authorization Request:**
The device POSTs `client_id` and `scope` to the AS's device
authorization endpoint (`/device_authorization`). The AS
responds with: `device_code` (opaque, for the device's polling),
`user_code` (short human-readable code, e.g., "WDJB-MJHT"),
`verification_uri` (where the user should go on a browser),
`verification_uri_complete` (optional: URI with user_code
pre-filled for QR code use), `expires_in` (TTL for both
codes), and `interval` (minimum seconds between polls).

**Phase 2 - Polling + User Authentication:**
The device polls `POST /token` with `grant_type=urn:ietf:
params:oauth:grant-type:device_code` and `device_code`.
The AS returns `authorization_pending` (keep polling),
`slow_down` (back off), or the token response on success.
Concurrently, the user navigates to `verification_uri`,
enters `user_code`, authenticates, and consents.

---

### ⏱️ Understand It in 30 Seconds

**The two-track dance:**

```
DEVICE TRACK:              USER TRACK (different device)
                           
POST /device_authorization  →→ "Visit example.com/device"
← device_code, user_code       "Enter code: WDJB-MJHT"
← verification_uri             
                            User opens browser → logs in
Poll: POST /token           → enters WDJB-MJHT → approves
  ↓ authorization_pending   
  ↓ authorization_pending   
  ↓ tokens returned ←←←←←← (AS links device_code to session)
```

**The key insight:**
The `user_code` is the bridge. It's short enough to type
(8 characters, no ambiguous chars like 0/O/1/I), has an expiry
(typically 15 minutes), and ties the user's browser session
to the device's poll session.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  DEVICE AUTHORIZATION FLOW (RFC 8628)                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  DEVICE                       AS (Authorization Server)   │
│                                                           │
│  POST /device_authorization                               │
│    client_id=device-client                                │
│    scope=openid profile                                   │
│                         ←───────────────────────────────  │
│  200 OK:                                                  │
│    device_code=GmRhmhcxhwAzkoEqiMEg_DnyEysNkuNhszIySk    │
│    user_code=WDJB-MJHT                                    │
│    verification_uri=https://example.com/device            │
│    verification_uri_complete=.../device?user_code=WDJB... │
│    expires_in=1800                                        │
│    interval=5                                             │
│                                                           │
│  [DEVICE LOOP - every interval seconds]                   │
│  POST /token                                              │
│    grant_type=urn:ietf:params:oauth:grant-type:           │
│               device_code                                 │
│    device_code=GmRhmhcxhwAzkoEqiMEg_DnyEysNkuNhszIySk    │
│    client_id=device-client                                │
│                                                           │
│  POLL RESPONSES:                                          │
│    authorization_pending → keep polling at interval       │
│    slow_down → increase interval by 5s, keep polling      │
│    access_denied → user denied → stop, show error         │
│    expired_token → device_code expired → restart          │
│    200 OK → tokens issued → break loop                    │
│                                                           │
│  [PARALLEL - on user's device]                            │
│  User → browser → https://example.com/device             │
│       → enters "WDJB-MJHT"                               │
│       → AS validates user_code (maps to device_code)      │
│       → user logs in + consents                           │
│       → AS marks device_code as authorized                │
│       → next device poll returns tokens                   │
└──────────────────────────────────────────────────────────┘
```

```mermaid
sequenceDiagram
  participant D as Device (TV/CLI)
  participant AS as Authorization Server
  participant B as User's Browser

  D->>AS: POST /device_authorization (client_id, scope)
  AS-->>D: device_code, user_code="WDJB-MJHT", verification_uri

  D->>D: Display "Go to example.com/device, enter WDJB-MJHT"

  loop Poll every interval seconds
    D->>AS: POST /token (grant=device_code, device_code)
    AS-->>D: 400 authorization_pending
  end

  B->>AS: GET /device (user opens verification_uri)
  B->>AS: Enter user_code "WDJB-MJHT"
  B->>AS: Authenticate + consent
  AS-->>AS: Mark device_code as authorized

  D->>AS: POST /token (next poll)
  AS-->>D: 200 OK: access_token, refresh_token
```

---

### 💻 Code Example

**Example 1 - BAD then GOOD: Device flow poll loop:**

```python
# BAD: Polls at fixed interval, ignores slow_down,
#   no expiry handling, no error code routing

def bad_device_poll(device_code, client_id):
    while True:
        resp = requests.post(TOKEN_ENDPOINT, data={
            'grant_type': (
                'urn:ietf:params:oauth:grant-type:device_code'
            ),
            'device_code': device_code,
            'client_id': client_id,
        })
        if resp.status_code == 200:
            return resp.json()
        time.sleep(5)  # WRONG: ignores slow_down
        # WRONG: no expired_token check
        # WRONG: no access_denied check
```

```python
# GOOD: Full RFC 8628-compliant poll loop
# WHY: slow_down must increase interval by 5 per spec.
#   Ignoring it can cause rate limiting or AS rejection.

import time, requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class DeviceAuthResponse:
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: Optional[str]
    expires_in: int
    interval: int

TOKEN_ENDPOINT = "https://as.example.com/token"
DEVICE_AUTH_ENDPOINT = (
    "https://as.example.com/device_authorization"
)
GRANT_TYPE_DEVICE = (
    "urn:ietf:params:oauth:grant-type:device_code"
)

def start_device_authorization(
    client_id: str,
    scope: str,
) -> DeviceAuthResponse:
    resp = requests.post(DEVICE_AUTH_ENDPOINT, data={
        'client_id': client_id,
        'scope': scope,
    })
    resp.raise_for_status()
    data = resp.json()
    return DeviceAuthResponse(
        device_code=data['device_code'],
        user_code=data['user_code'],
        verification_uri=data['verification_uri'],
        verification_uri_complete=data.get(
            'verification_uri_complete'
        ),
        expires_in=data['expires_in'],
        interval=data.get('interval', 5),
    )

def poll_for_tokens(
    device_auth: DeviceAuthResponse,
    client_id: str,
) -> dict:
    """Poll /token until approved, denied, or expired."""
    interval = device_auth.interval
    deadline = time.time() + device_auth.expires_in

    while time.time() < deadline:
        time.sleep(interval)

        resp = requests.post(TOKEN_ENDPOINT, data={
            'grant_type': GRANT_TYPE_DEVICE,
            'device_code': device_auth.device_code,
            'client_id': client_id,
        })

        if resp.status_code == 200:
            return resp.json()   # SUCCESS

        error_data = resp.json()
        error = error_data.get('error', '')

        if error == 'authorization_pending':
            # Normal: user hasn't approved yet. Keep polling.
            continue

        elif error == 'slow_down':
            # AS says we're polling too fast.
            # MUST increase interval by 5 seconds per RFC.
            interval += 5
            continue

        elif error == 'access_denied':
            # User explicitly denied authorization.
            raise DeviceFlowDeniedError(
                "User denied the authorization request."
            )

        elif error == 'expired_token':
            # device_code TTL expired before user acted.
            raise DeviceFlowExpiredError(
                "Authorization timed out. "
                "Please start a new device login."
            )

        else:
            raise DeviceFlowError(
                f"Unexpected error: {error}"
            )

    raise DeviceFlowExpiredError("Device code TTL reached.")

# Usage:
device_auth = start_device_authorization(
    client_id='my-cli-app',
    scope='openid profile read:data',
)
print(
    f"Go to: {device_auth.verification_uri}\n"
    f"Enter code: {device_auth.user_code}"
)
# Optionally: display QR code for verification_uri_complete
tokens = poll_for_tokens(device_auth, 'my-cli-app')
print(f"Access token: {tokens['access_token'][:20]}...")
```

**Example 2 - CLI tool pattern (like `gh auth login`):**

```bash
# What `gh auth login` does under the hood (Device Flow):

# Step 1: Device sends auth request
POST https://github.com/login/device/code
  client_id=Iv1.b507a08c87ecfe98
  scope=user,gist,read:org

# AS responds:
{
  "device_code": "3584d83530557fdd1f46af8289938c8ef79f9dc5",
  "user_code": "WDJB-MJHT",
  "verification_uri": "https://github.com/login/device",
  "expires_in": 899,
  "interval": 5
}

# CLI displays:
# ! First copy your one-time code: WDJB-MJHT
# Press Enter to open github.com in your browser...

# Step 2: CLI polls while user authenticates in browser
POST https://github.com/login/oauth/access_token
  client_id=Iv1.b507a08c87ecfe98
  device_code=3584d83530557fdd1f46af8289938c8ef79f9dc5
  grant_type=urn:ietf:params:oauth:grant-type:device_code

# Responses during wait:
{"error":"authorization_pending"}
{"error":"authorization_pending"}

# After user enters WDJB-MJHT and approves:
{
  "access_token": "gho_16C7e42F292c6912E7710c838347Ae178B4a",
  "token_type": "bearer",
  "scope": "gist,read:org,user"
}
```

---

### ⚖️ Comparison Table

| Flow | Browser Required | Redirect URI | Use Case |
|---|---|---|---|
| **Authorization Code** | Yes (on same device) | Yes | Web apps, mobile (with PKCE) |
| **Device Authorization** | Yes (on any device) | No | Smart TV, CLI, IoT, kiosk |
| **Client Credentials** | No | No | M2M, no user context |
| **ROPC** | No | No | Legacy only, deprecated |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The device must have a network connection to the user's device | The device and the user's device are completely independent. They are linked only through the AS: the user enters the user_code on the verification page; the AS matches it to the device_code. The device only needs outbound HTTPS to the AS (for the poll). The user's device only needs a browser that can reach the AS. They never communicate with each other. |
| Polling faster than the `interval` is fine since the connection is fast | The `interval` field in the device authorization response is the MINIMUM time between polls. Polling faster is a protocol violation and will trigger `slow_down` responses from compliant ASs. Each `slow_down` increases your required interval by 5 seconds. Aggressive polling can result in the device being rate-limited or blocked. |
| The device flow is only for hardware devices | The Device Authorization Flow is used in any context where a browser redirect is inconvenient or impossible: CLI tools (GitHub CLI, Azure CLI, Google Cloud CLI), Jupyter notebooks authenticating to APIs, server-side scripts running in headless environments, and gaming console apps. The "device" is just a client that can't handle redirects. |
| After entering the user_code, authentication is immediate | There is a polling loop delay. The device polls at `interval` seconds (e.g., every 5 seconds). After the user approves, the device must wait until the next poll cycle to receive tokens. This means up to `interval` seconds of delay after user action - typically 5 seconds. |

---

### 🚨 Failure Modes & Diagnosis

**Device Loop Not Stopping on `access_denied`**

**Symptom:**
After the user clicks "Deny" on the authorization page, the
CLI tool keeps running and polling indefinitely. Eventually
it may timeout on its own (when `expires_in` is reached),
but the user experience is confusing.

**Root Cause:**
Poll loop only checks for `status_code == 200` and continues
on any other response without checking `error` field. Does not
handle `access_denied`.

**Fix:**
Always explicitly handle all error codes per RFC 8628:
`authorization_pending` (continue), `slow_down` (back off +
continue), `access_denied` (stop + show friendly "denied"
message), `expired_token` (stop + prompt to restart).

---

**`user_code` Expiry Before User Acts**

**Symptom:**
User flow: TV shows code → user is distracted → comes back
15 minutes later → types code → AS says "invalid code".
Next device poll: `expired_token`.

**Root Cause:**
`expires_in` for the device_code/user_code pair is typically
900 seconds (15 minutes). After that, both codes are invalid.

**Fix:**
Display the expiry time to the user ("Code expires in 15
minutes"). When the device receives `expired_token`, restart
the entire device authorization request (new device_code, new
user_code) and prompt the user to try again with the new code.
Do not reuse the old user_code.

---

### 🔗 Related Keywords

**Prerequisites:**
- `OAuth 2.0 Roles` - understanding who plays which part
- `Grant Types Overview` - context for this as one grant type

**Builds On:**
- `OAuth 2.0 Threat Model (RFC 6819)` - security concerns for device flow
- `Pushed Authorization Requests (PAR)` - enhanced AS interaction patterns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PHASE 1      │ POST /device_authorization                 │
│ (device →AS) │ → device_code, user_code, verify_uri      │
├──────────────┼───────────────────────────────────────────┤
│ PHASE 2      │ User: browser → verify_uri → enter code   │
│ (user auth)  │ Device: poll POST /token every interval   │
├──────────────┼───────────────────────────────────────────┤
│ POLL CODES   │ authorization_pending → keep polling       │
│              │ slow_down → interval += 5, keep polling    │
│              │ access_denied → stop, show error           │
│              │ expired_token → restart from phase 1       │
│              │ 200 OK → tokens returned, done             │
├──────────────┼───────────────────────────────────────────┤
│ USE CASES    │ Smart TV, CLI (gh/az login), IoT, kiosk   │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ No redirect_uri needed. No browser on      │
│              │ device. User_code links the two devices.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Device gets user_code, user types it on  │
│              │  their phone; device polls until approved."│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Device Authorization Flow is for input-constrained devices:
   no browser redirect. Phase 1: device gets user_code. Phase 2:
   user enters it on their own device; device polls for tokens.

2. `slow_down` error MUST increase polling interval by 5 seconds
   per RFC 8628. Ignoring it violates the spec and triggers
   progressive backoff enforcement.

3. `expired_token` means the user_code TTL expired (typically
   15 minutes). Restart from phase 1 with a new device
   authorization request - never reuse expired codes.
