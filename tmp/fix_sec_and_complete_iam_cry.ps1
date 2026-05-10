# Fix SEC category and complete IAM/CRY creation
# Run with: pwsh -ExecutionPolicy Bypass -File tmp\fix_sec_and_complete_iam_cry.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)
$tier2 = 'dictionary\tier-2-networking-security'
$secBase = "$tier2\SEC-security"
$iamBase = "$tier2\IAM-iam-access"
$cryBase = "$tier2\CRY-cryptography"

# ─── Helper: get frontmatter field ──────────────────────────────────────────
function Get-FM($raw, $field) {
    if ($raw -match "(?m)^$([regex]::Escape($field)):\s*(.+)") { $Matches[1].Trim() }
    else { '' }
}

# ─── Helper: migrate SEC file to IAM or CRY ─────────────────────────────────
function Migrate-SecFile($srcName, $newId, $destBase, $newCat, $newFolder, $catSlug, $newNav) {
    $srcPath = "$secBase\$srcName"
    if (-not (Test-Path $srcPath)) { Write-Host "MISSING: $srcName"; return $false }
    $raw = [System.IO.File]::ReadAllText($srcPath, [System.Text.Encoding]::UTF8)

    $oldId = Get-FM $raw 'id'
    $oldTitle = (Get-FM $raw 'title') -replace '^"', '' -replace '"$', ''
    $slugTitle = $oldTitle -replace '[^a-zA-Z0-9]', '-' -replace '-+', '-' -replace '^-|-$', '' | ForEach-Object { $_.ToLower() }

    $raw = $raw -replace '(?m)^id:\s+\S+',                "id: $newId"
    $raw = $raw -replace '(?m)^category:\s+Security',      "category: $newCat"
    $raw = $raw -replace '(?m)^folder:\s+\S+',             "folder: $newFolder"
    $raw = $raw -replace '(?m)^parent:\s+"Security"',      "parent: `"$newCat`""
    $raw = $raw -replace '(?m)^nav_order:\s+\d+',          "nav_order: $newNav"
    $raw = $raw -replace '(?m)^permalink:\s+/security/\S+/', "permalink: /$catSlug/$slugTitle/"
    if ($raw -match "permalink: /security/") {
        $raw = $raw -replace 'permalink: /security/[^\n]+', "permalink: /$catSlug/$slugTitle/"
    }
    if ($oldId -and $oldTitle) {
        $raw = $raw -replace "(?m)^# $([regex]::Escape($oldId))\s+-\s+", "# $newId - "
    }

    $newName = "$newId - $oldTitle.md"
    [System.IO.File]::WriteAllText("$destBase\$newName", $raw, $enc)
    Remove-Item $srcPath -Force
    Write-Host "  $oldId ($($oldTitle.Substring(0, [Math]::Min(40,$oldTitle.Length)))) -> $newId"
    return $true
}

# ─── 1. Move IAM-related files from SEC to IAM ──────────────────────────────
Write-Host "`n=== Migrating IAM files from SEC ==="
$iamMoves = @(
    @{src='SEC-008 - Authentication vs Authorization.md';           id='IAM-006'; nav=6}
    @{src='SEC-022 - Session Management Security.md';               id='IAM-007'; nav=7}
    @{src='SEC-026 - OAuth2 Security Model.md';                     id='IAM-008'; nav=8}
    @{src='SEC-027 - JWT Security.md';                              id='IAM-009'; nav=9}
    @{src='SEC-046 - mTLS and Service-to-Service Authentication.md';id='IAM-010'; nav=10}
    @{src='SEC-052 - JWT Algorithm Confusion Attacks.md';           id='IAM-011'; nav=11}
    @{src='SEC-053 - OAuth2 Attack Vectors.md';                     id='IAM-012'; nav=12}
)
foreach ($m in $iamMoves) {
    Migrate-SecFile $m.src $m.id $iamBase 'Identity & Access Management' 'IAM-iam-access' 'iam-access' $m.nav
}

# ─── 2. Move CRY-related files from SEC to CRY ──────────────────────────────
Write-Host "`n=== Migrating CRY files from SEC ==="
$cryMoves = @(
    @{src='SEC-009 - Encryption Basics.md';                           id='CRY-006'; nav=6}
    @{src='SEC-010 - Public Key Cryptography (PKI).md';               id='CRY-007'; nav=7}
    @{src='SEC-011 - Hashing and Password Storage.md';                id='CRY-008'; nav=8}
    @{src='SEC-012 - HTTPS and TLS Basics.md';                        id='CRY-009'; nav=9}
    @{src='SEC-029 - Certificate Management Lifecycle.md';            id='CRY-010'; nav=10}
    @{src='SEC-039 - Cryptographic Failures.md';                      id='CRY-011'; nav=11}
    @{src='SEC-054 - Cryptographic Protocol Design Flaws.md';         id='CRY-012'; nav=12}
)
foreach ($m in $cryMoves) {
    Migrate-SecFile $m.src $m.id $cryBase 'Cryptography' 'CRY-cryptography' 'cryptography' $m.nav
}

# ─── 3. Rebuild SEC index from actual remaining files ────────────────────────
Write-Host "`n=== Rebuilding SEC index ==="
$secFiles = Get-ChildItem "$secBase\*.md" | Where-Object { $_.Name -ne 'index.md' } | Sort-Object Name

$tableRows = foreach ($f in $secFiles) {
    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $id   = Get-FM $raw 'id'
    $title = (Get-FM $raw 'title') -replace '^"', '' -replace '"$', ''
    $diff  = Get-FM $raw 'difficulty'
    if ($id) { "| $id | $title | $diff |" }
}

$secCount = $secFiles.Count
$highestSec = $secFiles | ForEach-Object { if ($_.Name -match '^SEC-(\d+)') { [int]$Matches[1] } } | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum

$secIdxHead = @"
---
layout: default
title: "Security"
parent: "Technical Dictionary"
nav_order: 7
has_children: true
permalink: /security/
---

# Security

Application security (AppSec), web attacks (OWASP), vulnerability management, secrets management, security testing (SAST/DAST/pentest), and secure SDLC. Authentication and authorization are in Identity & Access Management. Cryptography is in Cryptography.

**Keywords:** SEC-001--SEC-$($highestSec.ToString('D3')) ($secCount terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
"@
$secIdxContent = $secIdxHead + ($tableRows -join "`n") + "`n"
[System.IO.File]::WriteAllText("$secBase\index.md", $secIdxContent, $enc)
Write-Host "Rebuilt: SEC index ($secCount terms)"

# ─── 4. Rebuild IAM index from actual files ───────────────────────────────────
Write-Host "`n=== Rebuilding IAM index ==="
$iamFiles = Get-ChildItem "$iamBase\*.md" | Where-Object { $_.Name -ne 'index.md' } | Sort-Object Name
$iamRows = foreach ($f in $iamFiles) {
    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $id    = Get-FM $raw 'id'
    $title = (Get-FM $raw 'title') -replace '^"', '' -replace '"$', ''
    $diff  = Get-FM $raw 'difficulty'
    if ($id) { "| $id | $title | $diff |" }
}
$iamCount = $iamFiles.Count
$iamIdxHead = @"
---
layout: default
title: "Identity & Access Management"
parent: "Technical Dictionary"
nav_order: 8
has_children: true
permalink: /iam-access/
---

# Identity & Access Management

Session management, tokens (JWT, Access, Refresh), OAuth 2.0 flows, OpenID Connect (OIDC), SAML, SSO, MFA, Passkeys, RBAC, ABAC, and access control.

**Keywords:** IAM-001--IAM-$(([int](($iamFiles | ForEach-Object { if ($_.Name -match '^IAM-(\d+)') { [int]$Matches[1] } } | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum)).ToString('D3'))) ($iamCount terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
"@
$iamIdxContent = $iamIdxHead + ($iamRows -join "`n") + "`n"
[System.IO.File]::WriteAllText("$iamBase\index.md", $iamIdxContent, $enc)
Write-Host "Rebuilt: IAM index ($iamCount terms)"

# ─── 5. Rebuild CRY index from actual files ───────────────────────────────────
Write-Host "`n=== Rebuilding CRY index ==="
$cryFiles = Get-ChildItem "$cryBase\*.md" | Where-Object { $_.Name -ne 'index.md' } | Sort-Object Name
$cryRows = foreach ($f in $cryFiles) {
    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $id    = Get-FM $raw 'id'
    $title = (Get-FM $raw 'title') -replace '^"', '' -replace '"$', ''
    $diff  = Get-FM $raw 'difficulty'
    if ($id) { "| $id | $title | $diff |" }
}
$cryCount = $cryFiles.Count
$cryMax = $cryFiles | ForEach-Object { if ($_.Name -match '^CRY-(\d+)') { [int]$Matches[1] } } | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum

$cryIdxHead = @"
---
layout: default
title: "Cryptography"
parent: "Technical Dictionary"
nav_order: 9
has_children: true
permalink: /cryptography/
---

# Cryptography

Encryption (AES, RSA), hashing (Bcrypt, SHA-256), PKI, TLS, digital signatures, key management, HSM, password storage, and advanced cryptographic research (ZKPs, post-quantum, homomorphic encryption).

**Keywords:** CRY-001--CRY-$($cryMax.ToString('D3')) ($cryCount terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
"@
$cryIdxContent = $cryIdxHead + ($cryRows -join "`n") + "`n"
[System.IO.File]::WriteAllText("$cryBase\index.md", $cryIdxContent, $enc)
Write-Host "Rebuilt: CRY index ($cryCount terms)"

# ─── Summary ────────────────────────────────────────────────────────────────
$finalSec = (Get-ChildItem "$secBase\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
$finalIam = (Get-ChildItem "$iamBase\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
$finalCry = (Get-ChildItem "$cryBase\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
Write-Host "`n=== Final counts ==="
Write-Host "SEC: $finalSec"
Write-Host "IAM: $finalIam"
Write-Host "CRY: $finalCry"
