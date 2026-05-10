# reorganize_batch2.ps1 - Fix JVM temp file, add SEC gap stubs, create GCP category
# Run: pwsh -ExecutionPolicy Bypass -File tmp\reorganize_batch2.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

# ─────────────────────────────────────────────────────────────────────────────
# PART 1: Fix JVM temp file -> rename to JVM-076
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n=== Fix JVM temp file ==="
$jvmDir = 'dictionary\tier-3-java\JVM-java-jvm-internals'
$tmpFile = "$jvmDir\_tmp_JVM-006_JVM-002 - JVM.md"
if (Test-Path $tmpFile) {
    $raw = [System.IO.File]::ReadAllText($tmpFile, [System.Text.Encoding]::UTF8)
    # Update to JVM-076 as an archived/legacy entry
    $raw = $raw -replace '(?m)^id:\s+\S+', 'id: JVM-076'
    $raw = $raw -replace '(?m)^nav_order:\s+\d+', 'nav_order: 76'
    $raw = $raw -replace '(?m)^status:\s+\S+', 'status: draft'
    $raw = $raw -replace '(?m)^version:\s+\d+', 'version: 0'
    $raw = $raw -replace '(?m)^title:\s+"?JVM"?', 'title: JVM Architecture (Overview)'
    $raw = $raw -replace '(?m)^number:\s+\S+', 'folder: JVM-java-jvm-internals'
    if ($raw -notmatch '(?m)^folder:') {
        $raw = $raw -replace '(?m)^number:\s+.+', 'folder: JVM-java-jvm-internals'
    }
    # Add/fix the permalink
    $raw = $raw -replace '(?m)^permalink:\s+\S+', 'permalink: /jvm/jvm-architecture-overview/'
    # Remove the 'number:' field if still present
    $raw = $raw -replace '(?m)^number:\s+.+\n?', ''
    $newPath = "$jvmDir\JVM-076 - JVM Architecture (Overview).md"
    [System.IO.File]::WriteAllText($newPath, $raw, $enc)
    Remove-Item $tmpFile -Force
    Write-Host "  Renamed _tmp file -> JVM-076"
} else {
    Write-Host "  _tmp file not found, skipping"
}

# ─────────────────────────────────────────────────────────────────────────────
# PART 2: Add stubs to fill SEC gaps
# Gaps: 008-012, 022, 026-027, 029, 039, 046, 052-054
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n=== SEC: Add stubs to fill gaps ==="
$secDir = 'dictionary\tier-2-networking-security\SEC-security'

$secStubs = @(
    @{id='SEC-008'; title='Security Architecture Principles';                   nav=8;  diff='★★☆'; slug='security-architecture-principles'}
    @{id='SEC-009'; title='Cryptography for Application Developers';            nav=9;  diff='★★☆'; slug='cryptography-for-application-developers'}
    @{id='SEC-010'; title='Public Key Infrastructure (PKI) Basics';             nav=10; diff='★★☆'; slug='public-key-infrastructure-pki-basics'}
    @{id='SEC-011'; title='TLS and Secure Protocols for Developers';            nav=11; diff='★★☆'; slug='tls-and-secure-protocols-for-developers'}
    @{id='SEC-012'; title='Password and Credential Security Basics';            nav=12; diff='★☆☆'; slug='password-and-credential-security-basics'}
    @{id='SEC-022'; title='API Authentication Patterns';                        nav=22; diff='★★☆'; slug='api-authentication-patterns'}
    @{id='SEC-026'; title='Role-Based and Attribute-Based Access Control';      nav=26; diff='★★☆'; slug='role-based-and-attribute-based-access-control'}
    @{id='SEC-027'; title='API Authorization Design Patterns';                  nav=27; diff='★★★'; slug='api-authorization-design-patterns'}
    @{id='SEC-029'; title='Certificate Pinning and Trust Anchors';              nav=29; diff='★★★'; slug='certificate-pinning-and-trust-anchors'}
    @{id='SEC-039'; title='Cryptographic Misuse and Common Errors';             nav=39; diff='★★★'; slug='cryptographic-misuse-and-common-errors'}
    @{id='SEC-046'; title='Service-to-Service Security Patterns';               nav=46; diff='★★★'; slug='service-to-service-security-patterns'}
    @{id='SEC-052'; title='Advanced Authentication Attack Patterns';            nav=52; diff='★★★'; slug='advanced-authentication-attack-patterns'}
    @{id='SEC-053'; title='OAuth 2.0 Security Analysis';                        nav=53; diff='★★★'; slug='oauth-2-0-security-analysis'}
    @{id='SEC-054'; title='Cryptographic Security Evaluation';                  nav=54; diff='★★★'; slug='cryptographic-security-evaluation'}
)

foreach ($s in $secStubs) {
    $fname = "$secDir\$($s.id) - $($s.title).md"
    if (Test-Path $fname) { Write-Host "  SKIP (exists): $($s.id)"; continue }
    $titleField = if ($s.title -match ':') { "`"$($s.title)`"" } else { $s.title }
    $content = @"
---
id: $($s.id)
title: $titleField
category: Security
tier: tier-2-networking-security
folder: SEC-security
difficulty: $($s.diff)
depends_on:
used_by:
related:
tags:
  - security
  - appsec
status: draft
version: 0
layout: default
parent: "Security"
grand_parent: "Technical Dictionary"
nav_order: $($s.nav)
permalink: /security/$($s.slug)/
---
"@
    [System.IO.File]::WriteAllText($fname, $content, $enc)
    Write-Host "  Created: $($s.id) - $($s.title)"
}

# ─────────────────────────────────────────────────────────────────────────────
# PART 3: Create GCP Cloud category
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n=== Create GCP Cloud - Google Cloud Platform ==="
$gcpDir = 'dictionary\tier-6-infrastructure-devops\GCP-cloud-gcp'
New-Item -ItemType Directory -Path $gcpDir -Force | Out-Null

$gcpStubs = @(
    @{id='GCP-001'; title='What Is GCP and the Google Cloud Model';            nav=1; diff='★☆☆'; slug='what-is-gcp'}
    @{id='GCP-002'; title='The GCP Service Landscape -- A Map';                nav=2; diff='★☆☆'; slug='gcp-service-landscape'}
    @{id='GCP-003'; title='GCP vs AWS vs Azure -- Key Differences';           nav=3; diff='★★☆'; slug='gcp-vs-aws-vs-azure'}
    @{id='GCP-004'; title='GCP Well-Architected Pillars';                      nav=4; diff='★★☆'; slug='gcp-well-architected-pillars'}
    @{id='GCP-005'; title='The GCP Ecosystem Map';                             nav=5; diff='★☆☆'; slug='gcp-ecosystem-map'}
    @{id='GCP-006'; title='Google Compute Engine (GCE)';                       nav=6; diff='★★☆'; slug='google-compute-engine'}
    @{id='GCP-007'; title='Google Kubernetes Engine (GKE)';                    nav=7; diff='★★☆'; slug='google-kubernetes-engine'}
    @{id='GCP-008'; title='Google Cloud Run';                                   nav=8; diff='★★☆'; slug='google-cloud-run'}
    @{id='GCP-009'; title='Google Cloud Functions';                             nav=9; diff='★★☆'; slug='google-cloud-functions'}
    @{id='GCP-010'; title='Google Cloud Storage (GCS)';                        nav=10; diff='★☆☆'; slug='google-cloud-storage'}
    @{id='GCP-011'; title='Google BigQuery';                                    nav=11; diff='★★☆'; slug='google-bigquery'}
    @{id='GCP-012'; title='Google Cloud Pub/Sub';                               nav=12; diff='★★☆'; slug='google-cloud-pubsub'}
    @{id='GCP-013'; title='Google Cloud Spanner';                               nav=13; diff='★★★'; slug='google-cloud-spanner'}
    @{id='GCP-014'; title='Google Cloud SQL';                                   nav=14; diff='★★☆'; slug='google-cloud-sql'}
    @{id='GCP-015'; title='Google Cloud Firestore';                             nav=15; diff='★★☆'; slug='google-cloud-firestore'}
    @{id='GCP-016'; title='Google Cloud IAM';                                   nav=16; diff='★★☆'; slug='google-cloud-iam'}
    @{id='GCP-017'; title='Google Cloud VPC Networking';                        nav=17; diff='★★☆'; slug='google-cloud-vpc'}
    @{id='GCP-018'; title='Google Cloud Load Balancing';                        nav=18; diff='★★☆'; slug='google-cloud-load-balancing'}
    @{id='GCP-019'; title='Google Cloud CDN';                                   nav=19; diff='★★☆'; slug='google-cloud-cdn'}
    @{id='GCP-020'; title='Google Cloud Armor';                                 nav=20; diff='★★☆'; slug='google-cloud-armor'}
    @{id='GCP-021'; title='Google Vertex AI';                                   nav=21; diff='★★★'; slug='google-vertex-ai'}
    @{id='GCP-022'; title='Google Cloud Dataflow';                              nav=22; diff='★★★'; slug='google-cloud-dataflow'}
    @{id='GCP-023'; title='Google Cloud Composer (Airflow)';                    nav=23; diff='★★☆'; slug='google-cloud-composer'}
    @{id='GCP-024'; title='Cloud Monitoring and Logging (Cloud Operations)';   nav=24; diff='★★☆'; slug='cloud-monitoring-and-logging'}
    @{id='GCP-025'; title='GCP Cost Management and Billing';                    nav=25; diff='★★☆'; slug='gcp-cost-management'}
)

foreach ($s in $gcpStubs) {
    $fname = "$gcpDir\$($s.id) - $($s.title).md"
    $titleField = if ($s.title -match ':') { "`"$($s.title)`"" } else { $s.title }
    $content = @"
---
id: $($s.id)
title: $titleField
category: Cloud - GCP
tier: tier-6-infrastructure-devops
folder: GCP-cloud-gcp
difficulty: $($s.diff)
depends_on:
used_by:
related:
tags:
  - gcp
  - cloud
  - infrastructure
status: draft
version: 0
layout: default
parent: "Cloud - GCP"
grand_parent: "Technical Dictionary"
nav_order: $($s.nav)
permalink: /cloud-gcp/$($s.slug)/
---
"@
    [System.IO.File]::WriteAllText($fname, $content, $enc)
    Write-Host "  Created: $($s.id) - $($s.title)"
}

# GCP index.md
$gcpIdxContent = @"
---
layout: default
title: "Cloud - GCP"
parent: "Technical Dictionary"
nav_order: 26
has_children: true
permalink: /cloud-gcp/
---

# Cloud - GCP

Google Cloud Platform services covering compute (GCE, GKE, Cloud Run), storage (GCS, BigQuery, Spanner), messaging (Pub/Sub), networking (VPC, Load Balancing, Armor), AI/ML (Vertex AI), observability, and GCP vs AWS vs Azure decision frameworks.

**Keywords:** GCP-001--GCP-025 (25 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| GCP-001 | What Is GCP and the Google Cloud Model | ★☆☆ |
| GCP-002 | The GCP Service Landscape -- A Map | ★☆☆ |
| GCP-003 | GCP vs AWS vs Azure -- Key Differences | ★★☆ |
| GCP-004 | GCP Well-Architected Pillars | ★★☆ |
| GCP-005 | The GCP Ecosystem Map | ★☆☆ |
| GCP-006 | Google Compute Engine (GCE) | ★★☆ |
| GCP-007 | Google Kubernetes Engine (GKE) | ★★☆ |
| GCP-008 | Google Cloud Run | ★★☆ |
| GCP-009 | Google Cloud Functions | ★★☆ |
| GCP-010 | Google Cloud Storage (GCS) | ★☆☆ |
| GCP-011 | Google BigQuery | ★★☆ |
| GCP-012 | Google Cloud Pub/Sub | ★★☆ |
| GCP-013 | Google Cloud Spanner | ★★★ |
| GCP-014 | Google Cloud SQL | ★★☆ |
| GCP-015 | Google Cloud Firestore | ★★☆ |
| GCP-016 | Google Cloud IAM | ★★☆ |
| GCP-017 | Google Cloud VPC Networking | ★★☆ |
| GCP-018 | Google Cloud Load Balancing | ★★☆ |
| GCP-019 | Google Cloud CDN | ★★☆ |
| GCP-020 | Google Cloud Armor | ★★☆ |
| GCP-021 | Google Vertex AI | ★★★ |
| GCP-022 | Google Cloud Dataflow | ★★★ |
| GCP-023 | Google Cloud Composer (Airflow) | ★★☆ |
| GCP-024 | Cloud Monitoring and Logging (Cloud Operations) | ★★☆ |
| GCP-025 | GCP Cost Management and Billing | ★★☆ |
"@
[System.IO.File]::WriteAllText("$gcpDir\index.md", $gcpIdxContent, $enc)
Write-Host "`n  Created GCP index.md"

Write-Host "`n=== Summary ==="
$jvmCount = (Get-ChildItem 'dictionary\tier-3-java\JVM-java-jvm-internals\JVM-*.md').Count
$secCount  = (Get-ChildItem 'dictionary\tier-2-networking-security\SEC-security\SEC-*.md').Count
$gcpCount  = (Get-ChildItem 'dictionary\tier-6-infrastructure-devops\GCP-cloud-gcp\GCP-*.md').Count
Write-Host "JVM: $jvmCount files (expected 76)"
Write-Host "SEC: $secCount files (expected 142)"
Write-Host "GCP: $gcpCount files (expected 25)"
