# SEC SPLIT: Create IAM (Identity & Access Management) and CRY (Cryptography)
# Moves SEC-013-036 to IAM and SEC-037-054 + SEC-143-156 to CRY
# Run with: pwsh -ExecutionPolicy Bypass -File tmp\create_iam_cry.ps1

Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)
$tier2 = 'dictionary\tier-2-networking-security'
$secBase = "$tier2\SEC-security"
$iamBase = "$tier2\IAM-iam-access"
$cryBase = "$tier2\CRY-cryptography"

New-Item -ItemType Directory -Force -Path $iamBase | Out-Null
New-Item -ItemType Directory -Force -Path $cryBase | Out-Null

# ─── Helper: migrate file to new category ───────────────────────────────────
function Migrate-File($srcPath, $newId, $newCat, $newFolder, $newPermalink, $newNav) {
    if (-not (Test-Path $srcPath)) { Write-Host "MISSING: $srcPath"; return }
    $raw = [System.IO.File]::ReadAllText($srcPath, [System.Text.Encoding]::UTF8)

    $catSlug = if ($newId.StartsWith('IAM')) { 'iam-access' } else { 'cryptography' }
    $oldId = if ($raw -match '(?m)^id:\s+(\S+)') { $Matches[1] } else { '' }

    $raw = $raw -replace '(?m)^id:\s+\S+',                              "id: $newId"
    $raw = $raw -replace '(?m)^category:\s+Security',                   "category: $newCat"
    $raw = $raw -replace '(?m)^folder:\s+\S+',                          "folder: $newFolder"
    $raw = $raw -replace '(?m)^tier:\s+\S+',                            'tier: tier-2-networking-security'
    $raw = $raw -replace '(?m)^parent:\s+"Security"',                   "parent: `"$newCat`""
    $raw = $raw -replace '(?m)^nav_order:\s+\d+',                       "nav_order: $newNav"
    $raw = $raw -replace '(?m)^permalink:\s+/security/([^/]+)/',        "permalink: /$catSlug/$newPermalink/"
    if ($raw -match "permalink: /security/") {
        $raw = $raw -replace 'permalink: /security/([^/\n]+)/', "permalink: /$catSlug/$newPermalink/"
    }
    if ($oldId) { $raw = $raw -replace "(?m)^# $([regex]::Escape($oldId))\s+-\s+", "# $newId - " }

    $srcName = Split-Path $srcPath -Leaf
    $newName = $srcName -replace '^SEC-\d+ - ', "$newId - "
    $destBase = if ($newId.StartsWith('IAM')) { $iamBase } else { $cryBase }
    [System.IO.File]::WriteAllText("$destBase\$newName", $raw, $enc)
    Remove-Item $srcPath -Force
    Write-Host "Migrated: $srcName -> $newName"
}

# ─── IAM L0 orientation stubs ───────────────────────────────────────────────
$iamStubs = @(
    @{id='IAM-001';title='What Is Identity and Access Management';  diff='★☆☆'; slug='what-is-identity-and-access-management'; nav=1}
    @{id='IAM-002';title='The IAM Ecosystem Map (OAuth, JWT, SAML, Passkeys)'; diff='★☆☆'; slug='the-iam-ecosystem-map'; nav=2}
    @{id='IAM-003';title='Authentication vs Authorization Mental Model'; diff='★☆☆'; slug='authentication-vs-authorization-mental-model'; nav=3}
    @{id='IAM-004';title='The IAM Security Threat Landscape'; diff='★☆☆'; slug='the-iam-security-threat-landscape'; nav=4}
    @{id='IAM-005';title='IAM in Production -- What Engineers Face'; diff='★☆☆'; slug='iam-in-production-what-engineers-face'; nav=5}
)
foreach ($s in $iamStubs) {
    $tq = if ($s.title -match ': ') { "`"$($s.title)`"" } else { $s.title }
    $content = @"
---
id: $($s.id)
title: $tq
category: Identity & Access Management
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: $($s.diff)
depends_on:
used_by:
related:
tags:
  - security
  - iam
  - foundational
status: draft
version: 0
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Dictionary"
nav_order: $($s.nav)
permalink: /iam-access/$($s.slug)/
---
"@
    [System.IO.File]::WriteAllText("$iamBase\$($s.id) - $($s.title).md", $content, $enc)
    Write-Host "Created: $($s.id)"
}

# ─── CRY L0 orientation stubs ────────────────────────────────────────────────
$cryStubs = @(
    @{id='CRY-001';title='What Is Cryptography and Why It Matters'; diff='★☆☆'; slug='what-is-cryptography-and-why-it-matters'; nav=1}
    @{id='CRY-002';title='The Cryptography Ecosystem Map (Hashing, Encryption, PKI, TLS)'; diff='★☆☆'; slug='the-cryptography-ecosystem-map'; nav=2}
    @{id='CRY-003';title='Symmetric vs Asymmetric Mental Model'; diff='★☆☆'; slug='symmetric-vs-asymmetric-mental-model'; nav=3}
    @{id='CRY-004';title='When Cryptography Fails -- Common Mistakes'; diff='★☆☆'; slug='when-cryptography-fails-common-mistakes'; nav=4}
    @{id='CRY-005';title='Cryptography in Production -- What Engineers Face'; diff='★☆☆'; slug='cryptography-in-production-what-engineers-face'; nav=5}
)
foreach ($s in $cryStubs) {
    $tq = if ($s.title -match ': ') { "`"$($s.title)`"" } else { $s.title }
    $content = @"
---
id: $($s.id)
title: $tq
category: Cryptography
tier: tier-2-networking-security
folder: CRY-cryptography
difficulty: $($s.diff)
depends_on:
used_by:
related:
tags:
  - security
  - cryptography
  - foundational
status: draft
version: 0
layout: default
parent: "Cryptography"
grand_parent: "Technical Dictionary"
nav_order: $($s.nav)
permalink: /cryptography/$($s.slug)/
---
"@
    [System.IO.File]::WriteAllText("$cryBase\$($s.id) - $($s.title).md", $content, $enc)
    Write-Host "Created: $($s.id)"
}

# ─── Migrate IAM files: SEC-013 to SEC-036 → IAM-006 to IAM-029 ─────────────
$iamMoves = @(
    @{src='SEC-013 - Session-Based Authentication.md';                      id='IAM-006'; nav=6;  slug='session-based-authentication'}
    @{src='SEC-014 - Token-Based Authentication.md';                        id='IAM-007'; nav=7;  slug='token-based-authentication'}
    @{src='SEC-015 - Access Token.md';                                      id='IAM-008'; nav=8;  slug='access-token'}
    @{src='SEC-016 - Refresh Token.md';                                     id='IAM-009'; nav=9;  slug='refresh-token'}
    @{src='SEC-017 - HttpOnly Cookie.md';                                   id='IAM-010'; nav=10; slug='httponly-cookie'}
    @{src='SEC-018 - Secure Cookie Flag.md';                                id='IAM-011'; nav=11; slug='secure-cookie-flag'}
    @{src='SEC-019 - SameSite Cookie.md';                                   id='IAM-012'; nav=12; slug='samesite-cookie'}
    @{src='SEC-020 - JWT Anatomy (Header, Payload, Signature).md';          id='IAM-013'; nav=13; slug='jwt-anatomy-header-payload-signature'}
    @{src='SEC-021 - JWT Verification Without DB Lookup.md';                id='IAM-014'; nav=14; slug='jwt-verification-without-db-lookup'}
    @{src='SEC-022 - JWT Security Vulnerabilities.md';                      id='IAM-015'; nav=15; slug='jwt-security-vulnerabilities'}
    @{src='SEC-023 - JWT Algorithm Confusion Attack.md';                    id='IAM-016'; nav=16; slug='jwt-algorithm-confusion-attack'}
    @{src='SEC-024 - OAuth 2.0 Authorization Code Flow.md';                 id='IAM-017'; nav=17; slug='oauth-2-0-authorization-code-flow'}
    @{src='SEC-025 - OAuth 2.0 Client Credentials Flow.md';                 id='IAM-018'; nav=18; slug='oauth-2-0-client-credentials-flow'}
    @{src='SEC-026 - OAuth 2.0 PKCE.md';                                    id='IAM-019'; nav=19; slug='oauth-2-0-pkce'}
    @{src='SEC-027 - OAuth 2.0 Implicit Flow (deprecated).md';              id='IAM-020'; nav=20; slug='oauth-2-0-implicit-flow-deprecated'}
    @{src='SEC-028 - OpenID Connect (OIDC).md';                             id='IAM-021'; nav=21; slug='openid-connect-oidc'}
    @{src='SEC-029 - SAML (Security Assertion Markup Language).md';         id='IAM-022'; nav=22; slug='saml-security-assertion-markup-language'}
    @{src='SEC-030 - SSO (Single Sign-On).md';                              id='IAM-023'; nav=23; slug='sso-single-sign-on'}
    @{src='SEC-031 - MFA  2FA.md';                                          id='IAM-024'; nav=24; slug='mfa-2fa'}
    @{src='SEC-032 - TOTP (Time-Based One-Time Password).md';               id='IAM-025'; nav=25; slug='totp-time-based-one-time-password'}
    @{src='SEC-033 - Passkeys  WebAuthn.md';                                id='IAM-026'; nav=26; slug='passkeys-webauthn'}
    @{src='SEC-034 - RBAC (Role-Based Access Control).md';                  id='IAM-027'; nav=27; slug='rbac-role-based-access-control'}
    @{src='SEC-035 - ABAC (Attribute-Based Access Control).md';             id='IAM-028'; nav=28; slug='abac-attribute-based-access-control'}
    @{src='SEC-036 - ACL (Access Control List).md';                         id='IAM-029'; nav=29; slug='acl-access-control-list'}
)
foreach ($m in $iamMoves) {
    Migrate-File "$secBase\$($m.src)" $m.id 'Identity & Access Management' 'IAM-iam-access' $m.slug $m.nav
}

# ─── Migrate CRY files: SEC-037-054 → CRY-006-023, SEC-143-156 → CRY-024-037 ─
$cryMoves = @(
    @{src='SEC-037 - Hashing (Bcrypt, Argon2, SHA-256).md';                id='CRY-006'; nav=6;  slug='hashing-bcrypt-argon2-sha-256'}
    @{src='SEC-038 - Encryption (AES, RSA).md';                            id='CRY-007'; nav=7;  slug='encryption-aes-rsa'}
    @{src='SEC-039 - Encoding (Base64).md';                                id='CRY-008'; nav=8;  slug='encoding-base64'}
    @{src='SEC-040 - Hashing vs Encryption vs Encoding.md';                id='CRY-009'; nav=9;  slug='hashing-vs-encryption-vs-encoding'}
    @{src='SEC-041 - Symmetric vs Asymmetric Encryption.md';               id='CRY-010'; nav=10; slug='symmetric-vs-asymmetric-encryption'}
    @{src='SEC-042 - Public Key  Private Key.md';                          id='CRY-011'; nav=11; slug='public-key-private-key'}
    @{src='SEC-043 - PKI (Public Key Infrastructure).md';                  id='CRY-012'; nav=12; slug='pki-public-key-infrastructure'}
    @{src='SEC-044 - Digital Signature.md';                                id='CRY-013'; nav=13; slug='digital-signature'}
    @{src='SEC-045 - Certificate Authority (CA).md';                       id='CRY-014'; nav=14; slug='certificate-authority-ca'}
    @{src='SEC-046 - TLS Certificate Lifecycle.md';                        id='CRY-015'; nav=15; slug='tls-certificate-lifecycle'}
    @{src='SEC-047 - Certificate Pinning.md';                              id='CRY-016'; nav=16; slug='certificate-pinning'}
    @{src='SEC-048 - Key Management.md';                                   id='CRY-017'; nav=17; slug='key-management'}
    @{src='SEC-049 - Hardware Security Module (HSM).md';                   id='CRY-018'; nav=18; slug='hardware-security-module-hsm'}
    @{src='SEC-050 - Key Rotation.md';                                     id='CRY-019'; nav=19; slug='key-rotation'}
    @{src='SEC-051 - Envelope Encryption.md';                              id='CRY-020'; nav=20; slug='envelope-encryption'}
    @{src='SEC-052 - Password Storage Best Practices.md';                  id='CRY-021'; nav=21; slug='password-storage-best-practices'}
    @{src='SEC-053 - Salt (Cryptographic).md';                             id='CRY-022'; nav=22; slug='salt-cryptographic'}
    @{src='SEC-054 - Rainbow Table Attack.md';                             id='CRY-023'; nav=23; slug='rainbow-table-attack'}
    @{src='SEC-143 - Cryptographic Primitive Design.md';                   id='CRY-024'; nav=24; slug='cryptographic-primitive-design'}
    @{src='SEC-144 - Formal Security Proofs.md';                           id='CRY-025'; nav=25; slug='formal-security-proofs'}
    @{src='SEC-145 - Provable Security (Reduction Theory).md';             id='CRY-026'; nav=26; slug='provable-security-reduction-theory'}
    @{src='SEC-146 - Elliptic Curve Cryptography (Theory).md';             id='CRY-027'; nav=27; slug='elliptic-curve-cryptography-theory'}
    @{src='SEC-147 - Post-Quantum Cryptography.md';                        id='CRY-028'; nav=28; slug='post-quantum-cryptography'}
    @{src='SEC-148 - Secure Multiparty Computation.md';                    id='CRY-029'; nav=29; slug='secure-multiparty-computation'}
    @{src='SEC-149 - Zero-Knowledge Proofs.md';                            id='CRY-030'; nav=30; slug='zero-knowledge-proofs'}
    @{src='SEC-150 - Homomorphic Encryption.md';                           id='CRY-031'; nav=31; slug='homomorphic-encryption'}
    @{src='SEC-151 - TLS Protocol Design Rationale.md';                    id='CRY-032'; nav=32; slug='tls-protocol-design-rationale'}
    @{src='SEC-152 - OAuth 2.0 Specification Design Rationale.md';         id='CRY-033'; nav=33; slug='oauth-2-0-specification-design-rationale'}
    @{src='SEC-153 - Capability-Based Security Model.md';                  id='CRY-034'; nav=34; slug='capability-based-security-model'}
    @{src='SEC-154 - Security Protocol Verification (BAN Logic).md';       id='CRY-035'; nav=35; slug='security-protocol-verification-ban-logic'}
    @{src='SEC-155 - Threat Modeling Formal Methods.md';                   id='CRY-036'; nav=36; slug='threat-modeling-formal-methods'}
    @{src='SEC-156 - Applied Cryptography Research.md';                    id='CRY-037'; nav=37; slug='applied-cryptography-research'}
)
foreach ($m in $cryMoves) {
    Migrate-File "$secBase\$($m.src)" $m.id 'Cryptography' 'CRY-cryptography' $m.slug $m.nav
}

# ─── Update SEC index: remove moved rows ─────────────────────────────────────
$secIdxPath = "$secBase\index.md"
$secIdx = [System.IO.File]::ReadAllText($secIdxPath, [System.Text.Encoding]::UTF8)

# Remove IAM rows (013-036)
foreach ($n in 13..36) {
    $pad = $n.ToString('D3')
    $secIdx = $secIdx -replace "(?m)^\| SEC-$pad \|[^\n]+\n", ''
}
# Remove CRY rows (037-054, 143-156)
foreach ($n in (@(37..54) + @(143..156))) {
    $pad = $n.ToString('D3')
    $secIdx = $secIdx -replace "(?m)^\| SEC-$pad \|[^\n]+\n", ''
}
# Update count line
$remaining = (Get-ChildItem "$secBase\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
$secIdx = $secIdx -replace '\*\*Keywords:\*\*\s+SEC-001[^(]+\(\d+ terms\)', "**Keywords:** SEC-001--SEC-156 ($remaining terms)"
[System.IO.File]::WriteAllText($secIdxPath, $secIdx, $enc)
Write-Host "Updated: SEC index ($remaining remaining terms)"

# ─── Create IAM index.md ─────────────────────────────────────────────────────
$iamIndex = @'
---
layout: default
title: "Identity & Access Management"
parent: "Technical Dictionary"
nav_order: 8
has_children: true
permalink: /iam-access/
---

# Identity & Access Management

Authentication protocols, authorization patterns, JWT, OAuth 2.0, OIDC, SAML, SSO, MFA, Passkeys, RBAC, ABAC, and access control fundamentals.

**Keywords:** IAM-001--IAM-029 (29 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| IAM-001 | What Is Identity and Access Management | ★☆☆ |
| IAM-002 | The IAM Ecosystem Map (OAuth, JWT, SAML, Passkeys) | ★☆☆ |
| IAM-003 | Authentication vs Authorization Mental Model | ★☆☆ |
| IAM-004 | The IAM Security Threat Landscape | ★☆☆ |
| IAM-005 | IAM in Production -- What Engineers Face | ★☆☆ |
| IAM-006 | Session-Based Authentication | ★★☆ |
| IAM-007 | Token-Based Authentication | ★★☆ |
| IAM-008 | Access Token | ★★☆ |
| IAM-009 | Refresh Token | ★★☆ |
| IAM-010 | HttpOnly Cookie | ★★☆ |
| IAM-011 | Secure Cookie Flag | ★★☆ |
| IAM-012 | SameSite Cookie | ★★★ |
| IAM-013 | JWT Anatomy (Header, Payload, Signature) | ★★☆ |
| IAM-014 | JWT Verification Without DB Lookup | ★★★ |
| IAM-015 | JWT Security Vulnerabilities | ★★★ |
| IAM-016 | JWT Algorithm Confusion Attack | ★★★ |
| IAM-017 | OAuth 2.0 Authorization Code Flow | ★★★ |
| IAM-018 | OAuth 2.0 Client Credentials Flow | ★★★ |
| IAM-019 | OAuth 2.0 PKCE | ★★★ |
| IAM-020 | OAuth 2.0 Implicit Flow (deprecated) | ★★★ |
| IAM-021 | OpenID Connect (OIDC) | ★★★ |
| IAM-022 | SAML (Security Assertion Markup Language) | ★★★ |
| IAM-023 | SSO (Single Sign-On) | ★★☆ |
| IAM-024 | MFA / 2FA | ★★☆ |
| IAM-025 | TOTP (Time-Based One-Time Password) | ★★★ |
| IAM-026 | Passkeys / WebAuthn | ★★★ |
| IAM-027 | RBAC (Role-Based Access Control) | ★★☆ |
| IAM-028 | ABAC (Attribute-Based Access Control) | ★★★ |
| IAM-029 | ACL (Access Control List) | ★★☆ |
'@
[System.IO.File]::WriteAllText("$iamBase\index.md", $iamIndex, $enc)
Write-Host "Created: IAM index.md"

# ─── Create CRY index.md ─────────────────────────────────────────────────────
$cryIndex = @'
---
layout: default
title: "Cryptography"
parent: "Technical Dictionary"
nav_order: 9
has_children: true
permalink: /cryptography/
---

# Cryptography

Hashing, symmetric/asymmetric encryption, PKI, TLS, digital signatures, key management, HSM, password storage, and advanced cryptographic research (ZKPs, post-quantum, homomorphic encryption).

**Keywords:** CRY-001--CRY-037 (37 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| CRY-001 | What Is Cryptography and Why It Matters | ★☆☆ |
| CRY-002 | The Cryptography Ecosystem Map (Hashing, Encryption, PKI, TLS) | ★☆☆ |
| CRY-003 | Symmetric vs Asymmetric Mental Model | ★☆☆ |
| CRY-004 | When Cryptography Fails -- Common Mistakes | ★☆☆ |
| CRY-005 | Cryptography in Production -- What Engineers Face | ★☆☆ |
| CRY-006 | Hashing (Bcrypt, Argon2, SHA-256) | ★★☆ |
| CRY-007 | Encryption (AES, RSA) | ★★☆ |
| CRY-008 | Encoding (Base64) | ★☆☆ |
| CRY-009 | Hashing vs Encryption vs Encoding | ★★☆ |
| CRY-010 | Symmetric vs Asymmetric Encryption | ★★☆ |
| CRY-011 | Public Key / Private Key | ★★☆ |
| CRY-012 | PKI (Public Key Infrastructure) | ★★★ |
| CRY-013 | Digital Signature | ★★★ |
| CRY-014 | Certificate Authority (CA) | ★★☆ |
| CRY-015 | TLS Certificate Lifecycle | ★★★ |
| CRY-016 | Certificate Pinning | ★★★ |
| CRY-017 | Key Management | ★★★ |
| CRY-018 | Hardware Security Module (HSM) | ★★★ |
| CRY-019 | Key Rotation | ★★★ |
| CRY-020 | Envelope Encryption | ★★★ |
| CRY-021 | Password Storage Best Practices | ★★☆ |
| CRY-022 | Salt (Cryptographic) | ★★☆ |
| CRY-023 | Rainbow Table Attack | ★★★ |
| CRY-024 | Cryptographic Primitive Design | 🔬 |
| CRY-025 | Formal Security Proofs | 🔬 |
| CRY-026 | Provable Security (Reduction Theory) | 🔬 |
| CRY-027 | Elliptic Curve Cryptography (Theory) | 🔬 |
| CRY-028 | Post-Quantum Cryptography | 🔬 |
| CRY-029 | Secure Multiparty Computation | 🔬 |
| CRY-030 | Zero-Knowledge Proofs | 🔬 |
| CRY-031 | Homomorphic Encryption | 🔬 |
| CRY-032 | TLS Protocol Design Rationale | 🔬 |
| CRY-033 | OAuth 2.0 Specification Design Rationale | 🔬 |
| CRY-034 | Capability-Based Security Model | 🔬 |
| CRY-035 | Security Protocol Verification (BAN Logic) | 🔬 |
| CRY-036 | Threat Modeling Formal Methods | 🔬 |
| CRY-037 | Applied Cryptography Research | 🔬 |
'@
[System.IO.File]::WriteAllText("$cryBase\index.md", $cryIndex, $enc)
Write-Host "Created: CRY index.md"

Write-Host "`n=== IAM + CRY creation complete ==="
Write-Host "IAM: 5 L0 stubs + 24 moved from SEC = 29 terms"
Write-Host "CRY: 5 L0 stubs + 32 moved from SEC = 37 terms"
$secRemaining = (Get-ChildItem "$secBase\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
Write-Host "SEC: $secRemaining remaining terms"
