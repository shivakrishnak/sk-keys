# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\update_indexes.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Append-IndexRows {
    param([string]$IndexPath, [string]$OldCountLine, [string]$NewCountLine, [string]$NewRows)
    $content = [System.IO.File]::ReadAllText($IndexPath, [System.Text.Encoding]::UTF8)
    # Update keyword count line
    $content = $content.Replace($OldCountLine, $NewCountLine)
    # Append new rows before the last newline
    $content = $content.TrimEnd() + "`n" + $NewRows + "`n"
    [System.IO.File]::WriteAllText($IndexPath, $content, $enc)
    Write-Host "Updated: $IndexPath"
}

# ── SYD: 62 -> 77 ────────────────────────────────────────────────────────────
$sydIdx = "dictionary\tier-5-distributed-architecture\SYD-system-design\index.md"
$sydRows = @"
| SYD-063 | What is Scalability (Conceptual)                     | ★☆☆ |
| SYD-064 | What is a Cache (System Design Context)              | ★☆☆ |
| SYD-065 | What is a Message Queue (Conceptual)                 | ★☆☆ |
| SYD-066 | What is Database Replication (Basic)                 | ★☆☆ |
| SYD-067 | CDN Architecture Pattern                             | ★★☆ |
| SYD-068 | Connection Pooling (System Design)                   | ★★☆ |
| SYD-069 | Cache Invalidation Strategies                        | ★★★ |
| SYD-070 | Blob Storage Design                                  | ★★☆ |
| SYD-071 | Payment System Design                                | ★★★ |
| SYD-072 | File Storage System Design (Dropbox/S3)              | ★★★ |
| SYD-073 | Email System Design                                  | ★★★ |
| SYD-074 | Game Leaderboard Design                              | ★★★ |
| SYD-075 | Booking and Reservation System Design                | ★★★ |
| SYD-076 | Real-Time Collaboration System Design                | ★★★ |
| SYD-077 | Global Key-Value Store Design                        | ★★★ |
"@
Append-IndexRows $sydIdx "**Keywords:** SYD-001–SYD-062 (62 terms)" "**Keywords:** SYD-001–SYD-077 (77 terms)" $sydRows

# ── DPT: 72 -> 84 ────────────────────────────────────────────────────────────
$dptIdx = "dictionary\tier-5-distributed-architecture\DPT-design-patterns\index.md"
$dptRows = @"
| DPT-073 | Dependency Inversion vs Dependency Injection             | ★★★ |
| DPT-074 | SOLID - Single Responsibility Principle                  | ★★☆ |
| DPT-075 | SOLID - Open/Closed Principle                            | ★★☆ |
| DPT-076 | SOLID - Liskov Substitution Principle                    | ★★★ |
| DPT-077 | SOLID - Interface Segregation Principle                  | ★★☆ |
| DPT-078 | SOLID - Dependency Inversion Principle                   | ★★★ |
| DPT-079 | Repository Pattern                                       | ★★☆ |
| DPT-080 | Reactor Pattern                                          | ★★★ |
| DPT-081 | Anti-Pattern: Shotgun Surgery                            | ★★☆ |
| DPT-082 | Anti-Pattern: Feature Envy                               | ★★☆ |
| DPT-083 | Anti-Pattern: Circular Dependencies                      | ★★★ |
| DPT-084 | Inbox Pattern                                            | ★★★ |
"@
Append-IndexRows $dptIdx "**Keywords:** DPT-001–DPT-072 (72 terms)" "**Keywords:** DPT-001–DPT-084 (84 terms)" $dptRows

# ── DST: 77 -> 85 ────────────────────────────────────────────────────────────
$dstIdx = "dictionary\tier-5-distributed-architecture\DST-distributed-systems\index.md"
$dstRows = @"
| DST-078 | Replication Lag                                          | ★★★        |
| DST-079 | Write-Ahead Log (Distributed)                            | ★★★        |
| DST-080 | Distributed Rate Limiting                                | ★★★        |
| DST-081 | Phi Accrual Failure Detector                             | ★★★        |
| DST-082 | Global Sequence Number                                   | ★★★        |
| DST-083 | Distributed Cache Coherence                              | ★★★        |
| DST-084 | Compaction in Distributed Logs                           | ★★★        |
| DST-085 | Deterministic Simulation Testing                         | ★★★        |
"@
Append-IndexRows $dstIdx "**Keywords:** DST-001–DST-077 (77 terms)" "**Keywords:** DST-001–DST-085 (85 terms)" $dstRows

# ── MSV: 77 -> 85 ────────────────────────────────────────────────────────────
$msvIdx = "dictionary\tier-5-distributed-architecture\MSV-microservices\index.md"
$msvRows = @"
| MSV-078 | Platform Engineering                                    | ★★★ |
| MSV-079 | Internal Developer Platform (IDP)                       | ★★★ |
| MSV-080 | GraphQL Federation (Microservices)                      | ★★★ |
| MSV-081 | Dead Letter Queue Strategy                              | ★★★ |
| MSV-082 | Progressive Delivery                                    | ★★★ |
| MSV-083 | Multi-Tenancy in Microservices                          | ★★★ |
| MSV-084 | FinOps for Microservices                                | ★★★ |
| MSV-085 | Service Catalog                                         | ★★☆ |
"@
Append-IndexRows $msvIdx "**Keywords:** MSV-001–MSV-077 (77 terms)" "**Keywords:** MSV-001–MSV-085 (85 terms)" $msvRows

# ── SAP: 76 -> 86 ────────────────────────────────────────────────────────────
$sapIdx = "dictionary\tier-5-distributed-architecture\SAP-software-architecture\index.md"
$sapRows = @"
| SAP-077 | Conway's Law                                               | ★★☆        |
| SAP-078 | Inverse Conway Maneuver                                    | ★★★        |
| SAP-079 | Technical Debt Quantification                              | ★★★        |
| SAP-080 | Architecture Trade-off Analysis Method (ATAM)              | ★★★        |
| SAP-081 | Software Architecture Anti-Patterns                        | ★★★        |
| SAP-082 | Feature Toggle Architecture                                | ★★☆        |
| SAP-083 | Strangler Fig for Monolith-to-Service Migration            | ★★★        |
| SAP-084 | Service-Oriented Architecture (SOA)                        | ★★☆        |
| SAP-085 | API-First Architecture                                     | ★★☆        |
| SAP-086 | Composable Architecture                                    | ★★★        |
"@
Append-IndexRows $sapIdx "**Keywords:** SAP-001–SAP-076 (76 terms)" "**Keywords:** SAP-001–SAP-086 (86 terms)" $sapRows

# ── CSF: 80 -> 85 ────────────────────────────────────────────────────────────
$csfIdx = "dictionary\tier-1-foundations\CSF-cs-fundamentals\index.md"
$csfRows = @"
| CSF-081 | Abstraction Levels in Computing                          | ★☆☆        |
| CSF-082 | Computational Complexity Overview                        | ★★☆        |
| CSF-083 | Formal Reasoning in Software                             | ★★★        |
| CSF-084 | Software Correctness and Proof                           | ★★★        |
| CSF-085 | Cross-Paradigm Design Patterns                           | ★★★        |
"@
Append-IndexRows $csfIdx "**Keywords:** CSF-001–CSF-080 (80 terms · 30 original + 50 gap-fill)" "**Keywords:** CSF-001–CSF-085 (85 terms · 30 original + 55 gap-fill)" $csfRows

# ── LNX: already 73 (synced) ─────────────────────────────────────────────────
# Index already had LNX-070–073 rows, just the files were missing - no index update needed

# ── OSY: already 75 (synced) ─────────────────────────────────────────────────
# Index already had OSY-065–075 rows, just the files were missing - no index update needed

# ── NET: already 78 (synced) ─────────────────────────────────────────────────
# Index already had NET-065–078 rows, just the files were missing - no index update needed

# ── API: already 82 (synced) ─────────────────────────────────────────────────
# Index already had API-077–082 rows, just the files were missing - no index update needed

# ── SEC: already 156 (synced) ────────────────────────────────────────────────
# Index already had SEC-071–156 rows, just the files were missing - no index update needed

Write-Host "`nAll indexes updated."
