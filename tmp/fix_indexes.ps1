# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\fix_indexes.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

# ── 1. Create IAC index.md ────────────────────────────────────────────────────
$iacIndex = @'
---
layout: default
title: "Infrastructure as Code"
parent: "Technical Dictionary"
nav_order: 33
has_children: true
permalink: /infrastructure-as-code/
---

# Infrastructure as Code

Terraform, Ansible, Pulumi, AWS CDK, Helm, GitOps, IaC security, enterprise-scale automation, and platform engineering with IaC.

**Keywords:** IAC-001–IAC-047 (47 terms)

| ID      | Keyword                                                    | Difficulty |
|---------|------------------------------------------------------------|------------|
| IAC-001 | What Is Infrastructure as Code                             | ★☆☆        |
| IAC-002 | IaC vs Manual Infrastructure -- The Mental Model           | ★☆☆        |
| IAC-003 | The IaC Ecosystem Map (Terraform, Pulumi, Ansible, CDK)    | ★☆☆        |
| IAC-004 | Declarative vs Imperative IaC                              | ★☆☆        |
| IAC-005 | IaC in Production -- What to Expect                        | ★☆☆        |
| IAC-006 | Terraform Basics (providers, resources, state)             | ★☆☆        |
| IAC-007 | Terraform HCL Syntax                                       | ★☆☆        |
| IAC-008 | Terraform State                                            | ★☆☆        |
| IAC-009 | Terraform Plan and Apply                                   | ★☆☆        |
| IAC-010 | Terraform Modules                                          | ★☆☆        |
| IAC-011 | Terraform Variables and Outputs                            | ★☆☆        |
| IAC-012 | Terraform Providers                                        | ★☆☆        |
| IAC-013 | Terraform Remote State                                     | ★★☆        |
| IAC-014 | Terraform Workspaces                                       | ★★☆        |
| IAC-015 | Terraform Backends                                         | ★★☆        |
| IAC-016 | Terraform Import                                           | ★★☆        |
| IAC-017 | Ansible Basics (playbooks, inventory, roles)               | ★★☆        |
| IAC-018 | AWS CDK (Cloud Development Kit)                            | ★★☆        |
| IAC-019 | Pulumi -- IaC with Real Languages                          | ★★☆        |
| IAC-020 | Helm -- Kubernetes Package Manager                         | ★★☆        |
| IAC-021 | GitOps Workflow for IaC                                    | ★★☆        |
| IAC-022 | Terraform State Locking and Drift Detection                | ★★☆        |
| IAC-023 | Terraform Testing (Terratest, checkov)                     | ★★☆        |
| IAC-024 | Crossplane -- Kubernetes-Native IaC                        | ★★☆        |
| IAC-025 | Open Policy Agent (OPA) for IaC                            | ★★☆        |
| IAC-026 | IaC Security Scanning (tfsec, Bridgecrew)                  | ★★☆        |
| IAC-027 | Immutable Infrastructure Pattern                           | ★★☆        |
| IAC-028 | Idempotency in IaC                                         | ★★☆        |
| IAC-029 | Secret Management in IaC                                   | ★★☆        |
| IAC-030 | IaC Module Versioning Strategy                             | ★★☆        |
| IAC-031 | Packer -- Machine Image Building                           | ★★☆        |
| IAC-032 | Terraform Provider Development                             | ★★★        |
| IAC-033 | Terraform Enterprise and Cloud (Remote Operations)         | ★★★        |
| IAC-034 | Multi-Cloud IaC Strategy                                   | ★★★        |
| IAC-035 | IaC at Enterprise Scale (Terragrunt, Atlantis)             | ★★★        |
| IAC-036 | IaC Drift and Reconciliation Strategy                      | ★★★        |
| IAC-037 | IaC Compliance Enforcement                                 | ★★★        |
| IAC-038 | IaC Architecture Strategy                                  | ★★★        |
| IAC-039 | Platform Engineering with IaC                              | ★★★        |
| IAC-040 | Golden Path Templates and Internal Developer Platform      | ★★★        |
| IAC-041 | IaC Tool Selection Framework                               | ★★★        |
| IAC-042 | IaC Abstraction Layer Design                               | ★★★        |
| IAC-043 | Desired State Convergence Theory                           | ★★★        |
| IAC-044 | IaC Language Design Research                               | ★★★        |
| IAC-045 | IaC Trade-off Framing                                      | ★★★        |
| IAC-046 | Infrastructure Automation Mental Model                     | ★★★        |
| IAC-047 | Mutable vs Immutable Infrastructure Thinking               | ★★★        |
'@
[System.IO.File]::WriteAllText(
    'dictionary\tier-6-infrastructure-devops\IAC-infrastructure-code\index.md',
    $iacIndex, $enc)
Write-Host "Created: IAC index.md"

# ── 2. Create AIP index.md ────────────────────────────────────────────────────
$aipIndex = @'
---
layout: default
title: "AI Product Engineering"
parent: "Technical Dictionary"
nav_order: 47
has_children: true
permalink: /ai-product/
---

# AI Product Engineering

Building production AI products: UX patterns, testing, cost engineering, latency, safety, compliance, monetization, and AI product strategy.

**Keywords:** AIP-001–AIP-040 (40 terms)

| ID      | Keyword                                                          | Difficulty |
|---------|------------------------------------------------------------------|------------|
| AIP-001 | What Is AI Product Engineering                                   | ★☆☆        |
| AIP-002 | The AI Product Mental Model (UX + LLM + Data Pipeline)           | ★☆☆        |
| AIP-003 | AI Product vs Traditional Software -- Key Differences            | ★☆☆        |
| AIP-004 | The AI Product Ecosystem Map                                     | ★☆☆        |
| AIP-005 | Building AI Products -- What Teams Actually Face                 | ★☆☆        |
| AIP-006 | AI Product Requirements and Acceptance Criteria                  | ★☆☆        |
| AIP-007 | Prototyping with LLMs (Rapid Iteration)                          | ★☆☆        |
| AIP-008 | Feedback Loops and Human-in-the-Loop Design                      | ★☆☆        |
| AIP-009 | AI Feature Flags and Gradual Rollouts                            | ★☆☆        |
| AIP-010 | AI Product Metrics (Beyond Accuracy)                             | ★☆☆        |
| AIP-011 | AI UX Patterns (Suggestions, Auto-Complete, Explanation)         | ★★☆        |
| AIP-012 | AI Product Testing Strategy (Unit, Integration, Eval)            | ★★☆        |
| AIP-013 | AI Data Pipeline Design                                          | ★★☆        |
| AIP-014 | AI Content Moderation and Safety Filters                         | ★★☆        |
| AIP-015 | AI Cost Engineering (Token Budget, Caching Strategy)             | ★★☆        |
| AIP-016 | AI Latency Management (Streaming, Background, Prefetch)          | ★★☆        |
| AIP-017 | AI Fallback and Degradation Strategies                           | ★★☆        |
| AIP-018 | AI Feature Discoverability and Onboarding                        | ★★☆        |
| AIP-019 | AI Explainability for End Users                                  | ★★☆        |
| AIP-020 | AI Personalization and Context Management                        | ★★☆        |
| AIP-021 | AI Data Privacy and Compliance (GDPR, CCPA, AI Act)              | ★★☆        |
| AIP-022 | AI Model Versioning in Products                                  | ★★☆        |
| AIP-023 | AI Output Caching and Consistency                                | ★★☆        |
| AIP-024 | AI Error Handling and Recovery                                   | ★★☆        |
| AIP-025 | AI A/B Testing and Experiment Design                             | ★★☆        |
| AIP-026 | AI Accessibility in Products                                     | ★★☆        |
| AIP-027 | AI Product Architecture at Scale                                 | ★★★        |
| AIP-028 | AI Multi-Tenancy and Isolation                                   | ★★★        |
| AIP-029 | AI Regulatory Compliance (EU AI Act, FDA AI/ML)                  | ★★★        |
| AIP-030 | AI Model Marketplace and Provider Lock-In                        | ★★★        |
| AIP-031 | AI Product Strategy (Embedded vs Standalone)                     | ★★★        |
| AIP-032 | AI Monetization Models                                           | ★★★        |
| AIP-033 | AI Competitive Moats and Defensibility                           | ★★★        |
| AIP-034 | Responsible AI Product Design                                    | ★★★        |
| AIP-035 | AI Product Engineering Research Frontiers                        | ★★★        |
| AIP-036 | Human-AI Collaboration Design Research                           | ★★★        |
| AIP-037 | AI Product Trade-off Framing (Capability vs Safety vs UX)        | ★★★        |
| AIP-038 | AI Product Mental Model (Probabilistic Output Thinking)          | ★★★        |
| AIP-039 | Build vs Buy vs Fine-Tune Decision Mental Model                  | ★★★        |
| AIP-040 | AI Product Failure Mode Thinking                                 | ★★★        |
'@
[System.IO.File]::WriteAllText(
    'dictionary\tier-8-artificial-intelligence\AIP-ai-product\index.md',
    $aipIndex, $enc)
Write-Host "Created: AIP index.md"

# ── 3. Add OBS-022-026 rows to OBS index ─────────────────────────────────────
$obsPath = 'dictionary\tier-6-infrastructure-devops\OBS-observability-sre\index.md'
$obsContent = [System.IO.File]::ReadAllText($obsPath, [System.Text.Encoding]::UTF8)

# Update count line
$obsContent = $obsContent.Replace(
    '**Keywords:** OBS-001–OBS-056 (51 terms)',
    '**Keywords:** OBS-001–OBS-056 (56 terms)')

# Insert orphan rows after OBS-021 row (before OBS-027)
$obsContent = $obsContent.Replace(
    '| OBS-027 | AppDynamics -- APM',
    "| OBS-022 | AWS CloudWatch Dashboards                                 | ★★★        |`n| OBS-023 | AWS CloudWatch Log Insights                               | ★★★        |`n| OBS-024 | AWS CloudWatch Alarms                                     | ★★★        |`n| OBS-025 | AWS X-Ray (Distributed Tracing)                           | ★★★        |`n| OBS-026 | Actionable Alerting Patterns                              | ★★★        |`n| OBS-027 | AppDynamics -- APM")

[System.IO.File]::WriteAllText($obsPath, $obsContent, $enc)
Write-Host "Updated: OBS index.md (added OBS-022-026)"

Write-Host "`nAll indexes fixed."
