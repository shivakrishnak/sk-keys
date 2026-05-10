# rebuild_indexes.ps1 - Rebuild index.md for CRY, BIG, JVM, SEC, GCP (and update GCP index)
# Run: pwsh -ExecutionPolicy Bypass -File tmp\rebuild_indexes.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Get-FM($raw, $field) {
    if ($raw -match "(?m)^$([regex]::Escape($field)):\s*`"?([^`"\n]+)`"?") { $Matches[1].Trim() }
    else { '' }
}

function Rebuild-Index($dir, $code, $catName, $navOrder, $permalink, $desc, $navOrderInTier) {
    $files = Get-ChildItem "$dir\*.md" | Where-Object { $_.Name -ne 'index.md' } | Sort-Object Name
    $count = $files.Count
    $maxNum = ($files | ForEach-Object { if ($_.Name -match "^$code-(\d+)") { [int]$Matches[1] } } | Sort-Object -Descending | Select-Object -First 1)
    $maxStr = "{0:D3}" -f $maxNum

    $rows = foreach ($f in $files) {
        $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
        $id   = Get-FM $raw 'id'
        $title = Get-FM $raw 'title'
        $diff  = Get-FM $raw 'difficulty'
        if ($id) { "| $id | $title | $diff |" }
    }

    $header = @"
---
layout: default
title: "$catName"
parent: "Technical Dictionary"
nav_order: $navOrderInTier
has_children: true
permalink: $permalink
---

# $catName

$desc

**Keywords:** $code-001--$code-$maxStr ($count terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
"@
    $content = $header + ($rows -join "`n") + "`n"
    [System.IO.File]::WriteAllText("$dir\index.md", $content, $enc)
    Write-Host "  $code index rebuilt: $count terms (max=$maxStr)"
}

# ─── CRY ─────────────────────────────────────────────────────────────────────
Write-Host "=== Rebuilding CRY index ==="
Rebuild-Index `
    'dictionary\tier-2-networking-security\CRY-cryptography' `
    'CRY' 'Cryptography' 9 '/cryptography/' `
    'Encryption (AES, RSA), hashing (Bcrypt, SHA-256), PKI, TLS, digital signatures, key management, HSM, password storage, post-quantum cryptography, and advanced cryptographic research (ZKPs, homomorphic encryption).' `
    9

# ─── BIG ─────────────────────────────────────────────────────────────────────
Write-Host "=== Rebuilding BIG index ==="
Rebuild-Index `
    'dictionary\tier-4-data\BIG-bigdata-streaming' `
    'BIG' 'Big Data & Streaming' 16 '/big-data/' `
    'Hadoop, Spark (RDD, DataFrame, Streaming), Flink, Apache Beam, windowing, watermarks, Lambda/Kappa architectures, Databricks, Apache Airflow, dbt, and big data platform design.' `
    16

# ─── JVM ─────────────────────────────────────────────────────────────────────
Write-Host "=== Rebuilding JVM index ==="
Rebuild-Index `
    'dictionary\tier-3-java\JVM-java-jvm-internals' `
    'JVM' 'Java & JVM Internals' 8 '/jvm/' `
    'JVM architecture, bytecode, class loading, garbage collection (Serial, G1, ZGC), memory model (heap, stack, Metaspace), JIT compilation, performance profiling, and GraalVM.' `
    8

# ─── SEC ─────────────────────────────────────────────────────────────────────
Write-Host "=== Rebuilding SEC index ==="
Rebuild-Index `
    'dictionary\tier-2-networking-security\SEC-security' `
    'SEC' 'Security' 7 '/security/' `
    'Application security (AppSec), web attack vectors (OWASP Top 10, XSS, CSRF, SQLi, SSRF, command injection), secrets management, security testing (SAST/DAST/pentest), secure SDLC, and DevSecOps. Authentication and authorization are in Identity & Access Management. Cryptographic algorithms are in Cryptography.' `
    7

# ─── GCP ─────────────────────────────────────────────────────────────────────
Write-Host "=== Rebuilding GCP index ==="
Rebuild-Index `
    'dictionary\tier-6-infrastructure-devops\GCP-cloud-gcp' `
    'GCP' 'Cloud - GCP' 26 '/cloud-gcp/' `
    'Google Cloud Platform: Compute (GCE, GKE, Cloud Run, Functions), storage (GCS, BigQuery, Spanner, Firestore), messaging (Pub/Sub), networking (VPC, Load Balancing, Armor, CDN), AI/ML (Vertex AI), data engineering (Dataflow, Composer), and GCP vs AWS vs Azure decision frameworks.' `
    26

Write-Host "`nDone!"
