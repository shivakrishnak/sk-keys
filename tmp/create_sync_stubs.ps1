# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\create_sync_stubs.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Write-Stub {
    param(
        [string]$FilePath,
        [string]$Id,
        [string]$Title,
        [string]$Category,
        [string]$Tier,
        [string]$Folder,
        [string]$Difficulty,
        [string]$Parent,
        [string[]]$Tags,
        [string]$Slug,
        [string]$NavOrder
    )
    $titleVal = if ($Title -match ': ') { "`"$Title`"" } else { $Title }
    $tagLines = ($Tags | ForEach-Object { "  - $_" }) -join "`n"
    $content = @"
---
id: $Id
title: $titleVal
category: $Category
tier: $Tier
folder: $Folder
difficulty: $Difficulty
depends_on:
used_by:
related:
tags:
$tagLines
status: draft
version: 0
layout: default
parent: "$Parent"
grand_parent: "Technical Dictionary"
nav_order: $NavOrder
permalink: /$Slug/
---
"@
    [System.IO.File]::WriteAllText($FilePath, $content, $enc)
}

$created = 0

# ── LNX-070 to LNX-073 ───────────────────────────────────────────────────────
$lnxBase = "dictionary\tier-1-foundations\LNX-linux"
$lnxStubs = @(
    @{ n=70; t="Linux Networking Stack Internals";              d="★★★"; slug="linux/linux-networking-stack-internals" }
    @{ n=71; t="Linux Memory Management (mm subsystem)";        d="★★★"; slug="linux/linux-memory-management-mm-subsystem" }
    @{ n=72; t="Container Runtime Internals (runc, containerd)";d="★★★"; slug="linux/container-runtime-internals-runc-containerd" }
    @{ n=73; t="POSIX Standard";                                d="★★★"; slug="linux/posix-standard" }
)
foreach ($s in $lnxStubs) {
    $id  = "LNX-0$($s.n)"
    $fp  = "$lnxBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub -FilePath $fp -Id $id -Title $s.t -Category "Linux" `
            -Tier "tier-1-foundations" -Folder "LNX-linux" `
            -Difficulty $s.d -Parent "Linux" `
            -Tags @("linux","internals","deep-dive") `
            -Slug $s.slug -NavOrder $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $fp" }
}

# ── OSY-065 to OSY-075 ───────────────────────────────────────────────────────
$osyBase = "dictionary\tier-1-foundations\OSY-operating-systems"
$osyStubs = @(
    @{ n=65; t="RCU (Read-Copy-Update)";                    d="★★★"; slug="operating-systems/rcu-read-copy-update" }
    @{ n=66; t="Real-Time OS (RTOS) Concepts";              d="★★★"; slug="operating-systems/real-time-os-rtos-concepts" }
    @{ n=67; t="NUMA Scheduler";                            d="★★★"; slug="operating-systems/numa-scheduler" }
    @{ n=68; t="io_uring Internals";                        d="★★★"; slug="operating-systems/io-uring-internals" }
    @{ n=69; t="OS Kernel Design Patterns";                 d="★★★"; slug="operating-systems/os-kernel-design-patterns" }
    @{ n=70; t="Formal OS Verification (seL4)";             d="★★★"; slug="operating-systems/formal-os-verification-sel4" }
    @{ n=71; t="Hardware Transactional Memory (HTM)";       d="★★★"; slug="operating-systems/hardware-transactional-memory-htm" }
    @{ n=72; t="Memory Consistency Models (x86 TSO, ARM)";  d="★★★"; slug="operating-systems/memory-consistency-models" }
    @{ n=73; t="Virtual Machine Monitor (Hypervisor) Theory";d="★★★"; slug="operating-systems/virtual-machine-monitor-hypervisor-theory" }
    @{ n=74; t="Capability-Based OS Design";                d="★★★"; slug="operating-systems/capability-based-os-design" }
    @{ n=75; t="POSIX Standard";                            d="★★★"; slug="operating-systems/posix-standard" }
)
foreach ($s in $osyStubs) {
    $id  = "OSY-0$($s.n)"
    $fp  = "$osyBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub -FilePath $fp -Id $id -Title $s.t -Category "Operating Systems" `
            -Tier "tier-1-foundations" -Folder "OSY-operating-systems" `
            -Difficulty $s.d -Parent "Operating Systems" `
            -Tags @("os","internals","deep-dive") `
            -Slug $s.slug -NavOrder $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $fp" }
}

# ── NET-065 to NET-078 ───────────────────────────────────────────────────────
$netBase = "dictionary\tier-2-networking-security\NET-networking"
$netStubs = @(
    @{ n=65; t="BGP Route Selection / ECMP";                    d="★★★"; slug="networking/bgp-route-selection-ecmp" }
    @{ n=66; t="OSPF / IGP Interior Routing";                   d="★★★"; slug="networking/ospf-igp-interior-routing" }
    @{ n=67; t="Network Namespaces (Deep)";                     d="★★★"; slug="networking/network-namespaces-deep" }
    @{ n=68; t="RDMA (Remote Direct Memory Access)";            d="★★★"; slug="networking/rdma-remote-direct-memory-access" }
    @{ n=69; t="NIC Offloading (TSO, GRO, RSS)";                d="★★★"; slug="networking/nic-offloading-tso-gro-rss" }
    @{ n=70; t="TCP Protocol Design Rationale (Cerf-Kahn)";     d="★★★"; slug="networking/tcp-protocol-design-rationale" }
    @{ n=71; t="IP Protocol Design Philosophy (RFC 791)";       d="★★★"; slug="networking/ip-protocol-design-philosophy-rfc-791" }
    @{ n=72; t="DNS System Design Rationale (Mockapetris)";     d="★★★"; slug="networking/dns-system-design-rationale" }
    @{ n=73; t="QUIC Protocol Design (IETF RFC 9000)";          d="★★★"; slug="networking/quic-protocol-design-ietf-rfc-9000" }
    @{ n=74; t="BGP Internet Architecture Theory";              d="★★★"; slug="networking/bgp-internet-architecture-theory" }
    @{ n=75; t="Software-Defined Networking (SDN) Theory";      d="★★★"; slug="networking/software-defined-networking-sdn-theory" }
    @{ n=76; t="Network Calculus / QoS Theory";                 d="★★★"; slug="networking/network-calculus-qos-theory" }
    @{ n=77; t="Internet Architecture Theory (RFC 1958)";       d="★★★"; slug="networking/internet-architecture-theory-rfc-1958" }
    @{ n=78; t="HTTP Protocol Evolution Theory";                d="★★★"; slug="networking/http-protocol-evolution-theory" }
)
foreach ($s in $netStubs) {
    $id  = "NET-0$($s.n)"
    $fp  = "$netBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub -FilePath $fp -Id $id -Title $s.t -Category "Networking" `
            -Tier "tier-2-networking-security" -Folder "NET-networking" `
            -Difficulty $s.d -Parent "Networking" `
            -Tags @("networking","deep-dive","protocol") `
            -Slug $s.slug -NavOrder $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $fp" }
}

# ── API-077 to API-082 ───────────────────────────────────────────────────────
$apiBase = "dictionary\tier-2-networking-security\API-http-apis"
$apiStubs = @(
    @{ n=77; t="HTTP/2 Design Rationale (RFC 7540)";            d="★★★"; slug="http-apis/http2-design-rationale-rfc-7540" }
    @{ n=78; t="HTTP/3 over QUIC Design Rationale (RFC 9114)";  d="★★★"; slug="http-apis/http3-over-quic-design-rationale-rfc-9114" }
    @{ n=79; t="gRPC Protocol Specification Design";            d="★★★"; slug="http-apis/grpc-protocol-specification-design" }
    @{ n=80; t="GraphQL Specification Design (Lee Byron)";      d="★★★"; slug="http-apis/graphql-specification-design-lee-byron" }
    @{ n=81; t="OpenAPI Specification Design";                  d="★★★"; slug="http-apis/openapi-specification-design" }
    @{ n=82; t="WebSocket Protocol RFC 6455 Design";            d="★★★"; slug="http-apis/websocket-protocol-rfc-6455-design" }
)
foreach ($s in $apiStubs) {
    $id  = "API-0$($s.n)"
    $fp  = "$apiBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub -FilePath $fp -Id $id -Title $s.t -Category "HTTP & APIs" `
            -Tier "tier-2-networking-security" -Folder "API-http-apis" `
            -Difficulty $s.d -Parent "HTTP & APIs" `
            -Tags @("api","protocol","deep-dive") `
            -Slug $s.slug -NavOrder $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $fp" }
}

# ── SEC-071 to SEC-156 ───────────────────────────────────────────────────────
$secBase = "dictionary\tier-2-networking-security\SEC-security"
$secStubs = @(
    @{ n="071"; t="OWASP A05 - Security Misconfiguration (Deep)";d="★★★";slug="security/owasp-a05-security-misconfiguration-deep";tags=@("security","owasp","intermediate") }
    @{ n="072"; t="Cryptographic Failures";                     d="★★★";slug="security/cryptographic-failures";tags=@("security","cryptography","advanced") }
    @{ n="073"; t="Vulnerable and Outdated Components";         d="★★☆";slug="security/vulnerable-and-outdated-components";tags=@("security","owasp","bestpractice") }
    @{ n="074"; t="Brute-Force Attack";                         d="★★☆";slug="security/brute-force-attack";tags=@("security","attack","intermediate") }
    @{ n="075"; t="Credential Stuffing";                        d="★★★";slug="security/credential-stuffing";tags=@("security","attack","advanced") }
    @{ n="076"; t="Timing Attack";                              d="★★★";slug="security/timing-attack";tags=@("security","cryptography","advanced") }
    @{ n="077"; t="Replay Attack";                              d="★★★";slug="security/replay-attack";tags=@("security","attack","advanced") }
    @{ n="078"; t="Man-in-the-Middle Attack";                   d="★★☆";slug="security/man-in-the-middle-attack";tags=@("security","attack","intermediate") }
    @{ n="079"; t="DDoS Attack";                                d="★★☆";slug="security/ddos-attack";tags=@("security","attack","intermediate") }
    @{ n="080"; t="Phishing";                                   d="★☆☆";slug="security/phishing";tags=@("security","attack","foundational") }
    @{ n="081"; t="Social Engineering";                         d="★★☆";slug="security/social-engineering";tags=@("security","attack","intermediate") }
    @{ n="082"; t="Supply Chain Attack";                        d="★★★";slug="security/supply-chain-attack";tags=@("security","attack","advanced") }
    @{ n="083"; t="Prompt Injection (AI Security)";             d="★★★";slug="security/prompt-injection-ai-security";tags=@("security","ai","advanced") }
    @{ n="084"; t="Input Sanitization vs Escaping";             d="★★☆";slug="security/input-sanitization-vs-escaping";tags=@("security","bestpractice","intermediate") }
    @{ n="085"; t="Content Security Policy (CSP)";              d="★★★";slug="security/content-security-policy-csp";tags=@("security","browser","advanced") }
    @{ n="086"; t="Security Headers (HSTS, X-Frame-Options)";   d="★★★";slug="security/security-headers-hsts-x-frame-options";tags=@("security","http","advanced") }
    @{ n="087"; t="Secrets Management";                         d="★★☆";slug="security/secrets-management";tags=@("security","devops","intermediate") }
    @{ n="088"; t="Environment Variables for Secrets";          d="★☆☆";slug="security/environment-variables-for-secrets";tags=@("security","devops","foundational") }
    @{ n="089"; t=".env File Pattern";                          d="★☆☆";slug="security/env-file-pattern";tags=@("security","devops","foundational") }
    @{ n="090"; t="Vault (HashiCorp)";                          d="★★★";slug="security/vault-hashicorp";tags=@("security","devops","advanced") }
    @{ n="091"; t="API Key Security";                           d="★★☆";slug="security/api-key-security";tags=@("security","api","intermediate") }
    @{ n="092"; t="Rate Limiting for Security";                 d="★★☆";slug="security/rate-limiting-for-security";tags=@("security","api","intermediate") }
    @{ n="093"; t="Brute-Force Prevention";                     d="★★☆";slug="security/brute-force-prevention";tags=@("security","bestpractice","intermediate") }
    @{ n="094"; t="Account Lockout Policy";                     d="★★★";slug="security/account-lockout-policy";tags=@("security","authentication","advanced") }
    @{ n="095"; t="DDoS Protection";                            d="★★★";slug="security/ddos-protection";tags=@("security","reliability","advanced") }
    @{ n="096"; t="WAF (Web Application Firewall)";             d="★★★";slug="security/waf-web-application-firewall";tags=@("security","networking","advanced") }
    @{ n="097"; t="Penetration Testing";                        d="★★★";slug="security/penetration-testing";tags=@("security","testing","advanced") }
    @{ n="098"; t="Red Team / Blue Team";                       d="★★★";slug="security/red-team-blue-team";tags=@("security","testing","advanced") }
    @{ n="099"; t="SAST (Static Application Security Testing)"; d="★★☆";slug="security/sast-static-application-security-testing";tags=@("security","testing","intermediate") }
    @{ n="100"; t="DAST (Dynamic Application Security Testing)";d="★★★";slug="security/dast-dynamic-application-security-testing";tags=@("security","testing","advanced") }
    @{ n="101"; t="SCA (Software Composition Analysis)";        d="★★★";slug="security/sca-software-composition-analysis";tags=@("security","testing","advanced") }
    @{ n="102"; t="SBOM (Software Bill of Materials)";          d="★★★";slug="security/sbom-software-bill-of-materials";tags=@("security","devops","advanced") }
    @{ n="103"; t="CVE (Common Vulnerabilities and Exposures)"; d="★★☆";slug="security/cve-common-vulnerabilities-exposures";tags=@("security","foundational","intermediate") }
    @{ n="104"; t="CVSS Score";                                 d="★★★";slug="security/cvss-score";tags=@("security","advanced","production") }
    @{ n="105"; t="Security Audit";                             d="★★★";slug="security/security-audit";tags=@("security","testing","advanced") }
    @{ n="106"; t="SIEM (Security Information and Event Management)";d="★★★";slug="security/siem-security-information-event-management";tags=@("security","observability","advanced") }
    @{ n="107"; t="Security Logging and Monitoring";            d="★★★";slug="security/security-logging-and-monitoring";tags=@("security","observability","advanced") }
    @{ n="108"; t="Incident Response";                          d="★★★";slug="security/incident-response";tags=@("security","production","advanced") }
    @{ n="109"; t="RASP (Runtime Application Self-Protection)"; d="★★★";slug="security/rasp-runtime-application-self-protection";tags=@("security","advanced","production") }
    @{ n="110"; t="Dependency Scanning";                        d="★★☆";slug="security/dependency-scanning";tags=@("security","devops","intermediate") }
    @{ n="111"; t="Container Security Scanning";                d="★★★";slug="security/container-security-scanning";tags=@("security","containers","advanced") }
    @{ n="112"; t="Secret Scanning (in Git)";                   d="★★★";slug="security/secret-scanning-in-git";tags=@("security","git","advanced") }
    @{ n="113"; t="Threat vs Vulnerability vs Risk";            d="★☆☆";slug="security/threat-vs-vulnerability-vs-risk";tags=@("security","foundational","mental-model") }
    @{ n="114"; t="Malware Overview";                           d="★☆☆";slug="security/malware-overview";tags=@("security","foundational","attack") }
    @{ n="115"; t="Firewall (Conceptual)";                      d="★☆☆";slug="security/firewall-conceptual";tags=@("security","networking","foundational") }
    @{ n="116"; t="HTTPS Overview (Conceptual)";                d="★☆☆";slug="security/https-overview-conceptual";tags=@("security","networking","foundational") }
    @{ n="117"; t="Nonrepudiation";                             d="★☆☆";slug="security/nonrepudiation";tags=@("security","foundational","cryptography") }
    @{ n="118"; t="Security vs Privacy";                        d="★☆☆";slug="security/security-vs-privacy";tags=@("security","foundational","mental-model") }
    @{ n="119"; t="Password Security Basics";                   d="★☆☆";slug="security/password-security-basics";tags=@("security","foundational","authentication") }
    @{ n="120"; t="What is a Security Vulnerability";           d="★☆☆";slug="security/what-is-a-security-vulnerability";tags=@("security","foundational","mental-model") }
    @{ n="121"; t="Security Policy (Conceptual)";               d="★☆☆";slug="security/security-policy-conceptual";tags=@("security","foundational","bestpractice") }
    @{ n="122"; t="CORS Security Implications";                 d="★★☆";slug="security/cors-security-implications";tags=@("security","browser","intermediate") }
    @{ n="123"; t="Insecure Direct Object Reference (IDOR)";    d="★★☆";slug="security/insecure-direct-object-reference-idor";tags=@("security","owasp","intermediate") }
    @{ n="124"; t="Clickjacking";                               d="★★☆";slug="security/clickjacking";tags=@("security","browser","intermediate") }
    @{ n="125"; t="Open Redirect";                              d="★★☆";slug="security/open-redirect";tags=@("security","attack","intermediate") }
    @{ n="126"; t="Session Hijacking / Token Theft";            d="★★☆";slug="security/session-hijacking-token-theft";tags=@("security","attack","intermediate") }
    @{ n="127"; t="OWASP API Security Top 10";                  d="★★☆";slug="security/owasp-api-security-top-10";tags=@("security","api","intermediate") }
    @{ n="128"; t="CIS Benchmarks (Security Hardening)";        d="★★☆";slug="security/cis-benchmarks-security-hardening";tags=@("security","bestpractice","intermediate") }
    @{ n="129"; t="mTLS (Mutual TLS)";                          d="★★★";slug="security/mtls-mutual-tls";tags=@("security","networking","advanced") }
    @{ n="130"; t="Memory Safety Vulnerabilities";              d="★★★";slug="security/memory-safety-vulnerabilities";tags=@("security","advanced","internals") }
    @{ n="131"; t="Side-Channel Attack (Deep)";                 d="★★★";slug="security/side-channel-attack-deep";tags=@("security","advanced","cryptography") }
    @{ n="132"; t="Container Security Hardening";               d="★★★";slug="security/container-security-hardening";tags=@("security","containers","advanced") }
    @{ n="133"; t="Network Segmentation Security";              d="★★★";slug="security/network-segmentation-security";tags=@("security","networking","advanced") }
    @{ n="134"; t="Compliance-Driven Security (PCI-DSS, SOX, GDPR)";d="★★★";slug="security/compliance-driven-security-pci-dss-sox-gdpr";tags=@("security","advanced","bestpractice") }
    @{ n="135"; t="OWASP LLM Top 10";                           d="★★★";slug="security/owasp-llm-top-10";tags=@("security","ai","advanced") }
    @{ n="136"; t="Agent Permission Model";                     d="★★★";slug="security/agent-permission-model";tags=@("security","ai","advanced") }
    @{ n="137"; t="Zero-Day Vulnerability";                     d="★★★";slug="security/zero-day-vulnerability";tags=@("security","attack","advanced") }
    @{ n="138"; t="Threat Intelligence (MITRE ATT&CK)";         d="★★★";slug="security/threat-intelligence-mitre-attack";tags=@("security","advanced","production") }
    @{ n="139"; t="Defense in Depth Architecture";              d="★★★";slug="security/defense-in-depth-architecture";tags=@("security","architecture","advanced") }
    @{ n="140"; t="Security Architecture Review";               d="★★★";slug="security/security-architecture-review";tags=@("security","architecture","advanced") }
    @{ n="141"; t="Digital Forensics (Basics)";                 d="★★★";slug="security/digital-forensics-basics";tags=@("security","advanced","production") }
    @{ n="142"; t="Exploit Development (Conceptual)";           d="★★★";slug="security/exploit-development-conceptual";tags=@("security","advanced","deep-dive") }
    @{ n="143"; t="Cryptographic Primitive Design";             d="★★★";slug="security/cryptographic-primitive-design";tags=@("security","cryptography","deep-dive") }
    @{ n="144"; t="Formal Security Proofs";                     d="★★★";slug="security/formal-security-proofs";tags=@("security","cryptography","deep-dive") }
    @{ n="145"; t="Provable Security (Reduction Theory)";       d="★★★";slug="security/provable-security-reduction-theory";tags=@("security","cryptography","deep-dive") }
    @{ n="146"; t="Elliptic Curve Cryptography (Theory)";       d="★★★";slug="security/elliptic-curve-cryptography-theory";tags=@("security","cryptography","deep-dive") }
    @{ n="147"; t="Post-Quantum Cryptography";                  d="★★★";slug="security/post-quantum-cryptography";tags=@("security","cryptography","deep-dive") }
    @{ n="148"; t="Secure Multiparty Computation";              d="★★★";slug="security/secure-multiparty-computation";tags=@("security","cryptography","deep-dive") }
    @{ n="149"; t="Zero-Knowledge Proofs";                      d="★★★";slug="security/zero-knowledge-proofs";tags=@("security","cryptography","deep-dive") }
    @{ n="150"; t="Homomorphic Encryption";                     d="★★★";slug="security/homomorphic-encryption";tags=@("security","cryptography","deep-dive") }
    @{ n="151"; t="TLS Protocol Design Rationale";              d="★★★";slug="security/tls-protocol-design-rationale";tags=@("security","networking","deep-dive") }
    @{ n="152"; t="OAuth 2.0 Specification Design Rationale";   d="★★★";slug="security/oauth-20-specification-design-rationale";tags=@("security","authentication","deep-dive") }
    @{ n="153"; t="Capability-Based Security Model";            d="★★★";slug="security/capability-based-security-model";tags=@("security","advanced","deep-dive") }
    @{ n="154"; t="Security Protocol Verification (BAN Logic)"; d="★★★";slug="security/security-protocol-verification-ban-logic";tags=@("security","cryptography","deep-dive") }
    @{ n="155"; t="Threat Modeling Formal Methods";             d="★★★";slug="security/threat-modeling-formal-methods";tags=@("security","advanced","deep-dive") }
    @{ n="156"; t="Applied Cryptography Research";              d="★★★";slug="security/applied-cryptography-research";tags=@("security","cryptography","deep-dive") }
)
foreach ($s in $secStubs) {
    $id  = "SEC-$($s.n)"
    $fp  = "$secBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub -FilePath $fp -Id $id -Title $s.t -Category "Security" `
            -Tier "tier-2-networking-security" -Folder "SEC-security" `
            -Difficulty $s.d -Parent "Security" `
            -Tags $s.tags `
            -Slug $s.slug -NavOrder ([int]$s.n)
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $fp" }
}

Write-Host "`nTotal created: $created"
