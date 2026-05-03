---
layout: default
title: "Image Provenance / SBOM"
parent: "Containers"
nav_order: 854
permalink: /containers/image-provenance-sbom/
number: "0854"
category: Containers
difficulty: ★★★
depends_on: Docker Image, OCI Standard, Image Scanning, Image Tag Strategy, Docker BuildKit
used_by: CI/CD, Container Security, Container Runtime Interface (CRI)
related: Image Scanning, OCI Standard, Image Tag Strategy, Container Security, Docker BuildKit
tags:
  - containers
  - security
  - devops
  - advanced
  - bestpractice
  - production
---

# 854 — Image Provenance / SBOM

⚡ TL;DR — Image provenance and SBOMs provide a cryptographically verifiable record of what is in a container image and how it was built, enabling supply chain security and compliance.

| #854 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker Image, OCI Standard, Image Scanning, Image Tag Strategy, Docker BuildKit | |
| **Used by:** | CI/CD, Container Security, Container Runtime Interface (CRI) | |
| **Related:** | Image Scanning, OCI Standard, Image Tag Strategy, Container Security, Docker BuildKit | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In December 2020, the SolarWinds supply chain attack embedded malicious code in a legitimate software build process, affecting 18,000+ organisations. In 2021, the `ua-parser-js` npm package was compromised — malicious versions were downloaded by millions of developers and CI systems. In the container world: a developer pulls `node:18.12` from Docker Hub. What is actually in that image? Which specific packages, which versions, which transitive dependencies? Did the image come from the official repository? Was the image tampered with in the registry? Was it built on a compromised build server?

**THE BREAKING POINT:**
Without provenance and SBOM, every container image is a black box. You know the tag (`node:18.12`), but you cannot verify: who built it, when, from which source, with which tools, and whether it has been modified since build. Supply chain attacks exploit this opacity — inserting malicious code at any point between source code and running container.

**THE INVENTION MOMENT:**
This is exactly why image provenance and SBOMs were developed — cryptographic attestations that prove WHERE an image came from, WHAT it contains, and that it has NOT been tampered with since being built by a trusted party.

---

### 📘 Textbook Definition

An **SBOM (Software Bill of Materials)** is a structured inventory of all components in a software artifact: packages, libraries, licenses, versions, and dependency relationships. For container images, an SBOM lists every OS package and language-level dependency in every layer. **Image provenance** refers to the cryptographically verifiable record of where an image came from: which CI/CD pipeline built it, which source commit, which builder, when, and with what inputs. **Sigstore/Cosign** provides the tooling to sign images and attach attestations (including SBOMs) as OCI artifacts, enabling signature verification before deployment. Together, provenance and SBOM are the foundation of **supply chain security** (SLSA — Supply-chain Levels for Software Artifacts) for container images.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An SBOM is a container image's ingredient list, and provenance is its certificate of authenticity — together they prove what's inside and that it hasn't been tampered with.

**One analogy:**
> A pharmaceutical drug has two documents. The ingredient list (SBOM) tells you exactly what is in the pill: active ingredient, dosage, excipients, fillers. The certificate of authenticity (provenance) certifies that this specific batch was manufactured by Pfizer at the Kalamazoo facility on March 15th, tested by batch #44521, and has not been adulterated since leaving the factory. Without both documents, you can't know if the pill is genuine or counterfeit. Container images need the same regime: ingredient list + certificate of authenticity.

**One insight:**
The key property of provenance is *cryptographic non-repudiation*. Anyone can claim "I built this image." With Sigstore/Cosign, the claim is backed by a cryptographic signature verifiable against a public key — and the transparency log (Rekor) makes the claim publicly auditable. Even if an attacker compromises your registry and replaces an image, the signature on the replacement won't match your known build pipeline's public key.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An OCI image digest (SHA256) is content-addressed — any tampering changes the digest.
2. A cryptographic signature over the digest proves the signer vouches for the image.
3. An SBOM provides the component inventory necessary for vulnerability management and compliance.
4. Provenance attestations provide the build origin evidence necessary for SLSA compliance.

**DERIVED DESIGN:**

**SBOM formats:**
- **SPDX** (Software Package Data Exchange): Linux Foundation standard, widely used in regulated industries
- **CycloneDX**: OWASP standard, designed for security use cases 
- Both are machine-readable JSON/XML listing: package names, versions, licenses, download locations, checksums

**Sigstore/Cosign signing model:**
```
┌──────────────────────────────────────────────────────────┐
│         Image Signing with Cosign                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  CI builds image: myapp@sha256:abc123                    │
│       ↓                                                  │
│  cosign sign --key cosign.key myapp@sha256:abc123        │
│       ↓                                                  │
│  Signature stored as OCI artifact in registry:           │
│  myapp:<sha-tag>.sig → signature blob                    │
│  (points to original image digest)                       │
│       ↓                                                  │
│  Verification at deploy time:                            │
│  cosign verify --key cosign.pub myapp:latest             │
│  → looks up signature artifact in registry               │
│  → verifies signature against image digest               │
│  → PASS: image from trusted builder                      │
│  → FAIL: tampered or unsigned → reject                   │
│                                                          │
│  Transparency log (Rekor):                               │
│  → signature entry published to public tamper-evident    │
│    append-only log                                       │
│  → anyone can audit when image was signed and by whom    │
└──────────────────────────────────────────────────────────┘
```

**SBOM attachment (OCI Referrers API):**
```bash
# Generate SBOM with Syft
syft myapp:latest -o spdx-json > sbom.spdx.json

# Attach SBOM to image in registry (OCI v1.1 Referrers API)
cosign attach sbom \
  --sbom sbom.spdx.json \
  --type spdx \
  myapp@sha256:abc123

# SBOM is now stored as OCI artifact pointing to the image
# Discoverable via: cosign download sbom myapp:latest
```

**SLSA framework:**
Supply chain Levels for Software Artifacts defines 4 levels of supply chain integrity:
- L0: no guarantees
- L1: build process documented (provenance exists)
- L2: build service generates signed provenance
- L3: builds are isolated, provenance is non-forgeable
- L4: two-party review for all changes (highest)

**THE TRADE-OFFS:**

**Gain:** Supply chain attack detection, vulnerability management via SBOM, compliance (SBOM mandated by US Executive Order 14028), trusted deployment.

**Cost:** Significant tooling setup (Sigstore, key management). SBOM generation adds CI time. OCI v1.1 Referrers API support required in registry. Admission webhook enforcement required for policy compliance.

---

### 🧪 Thought Experiment

**SETUP:**
Your company's registry stores `payment-service:latest`. An attacker gains write access to the registry and replaces the image with a malicious version that exfiltrates credit card numbers while appearing to process payments normally.

**WHAT HAPPENS WITHOUT PROVENANCE:**
Kubernetes pulls `payment-service:latest`. The digest is different (image was replaced), but the tag still resolves. No check catches the replacement. The malicious image is deployed, starts processing payments, and exfiltrates data. Detected only when credit card fraud is reported.

**WHAT HAPPENS WITH COSIGN SIGNATURE VERIFICATION:**
The new malicious image has digest `sha256:evil999`. The Kyverno admission policy checks: `cosign verify --key ci.pub payment-service:sha256:evil999`. The image has no valid signature (the attacker doesn't have the CI private key). Kyverno rejects the pod: `"Image signature verification failed: no valid signature found"`. The malicious image never runs. The registry breach is immediately detected (the rejection tells you something unauthorized tried to deploy).

**THE INSIGHT:**
Signature verification converts a registry security boundary into a cryptographic one. Even if an attacker has registry write access, they cannot deploy without the CI private key. This is defence in depth: registry access control (prevent write) + signature verification (detect and block after write).

---

### 🧠 Mental Model / Analogy

> Image provenance and SBOM are like the supply chain documentation for aircraft components. A jet engine part has: a Bill of Materials (what alloys, what tolerances, from which supplier), a manufacturing certificate (made by Rolls-Royce, on this date, by this batch), and a chain of custody record (inspected at every stage). Airlines don't accept parts without complete documentation, even if the part looks fine. Container deployments at high-security organisations apply the same standard: no image without SBOM (what's in it), no image without signed provenance (who made it), no image without chain-of-custody (what registry stored it).

Mapping:
- "Bill of Materials" → SBOM (all packages, versions, licenses)
- "Manufacturing certificate" → build provenance (CI job, commit, timestamp)
- "Chain of custody" → OCI digest + registry event log
- "Airline won't accept undocumented part" → admission controller rejects unsigned image

Where this analogy breaks down: aircraft parts don't change after manufacturing. A container image can technically be re-tagged (though not re-signed) — the OCI digest provides the immutable identifier, not the tag.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An SBOM is a container image's ingredient list — all the software packages and libraries it contains. Provenance is the image's birth certificate — proof of who built it, when, and where. Together they answer: "What is this image, and can I trust it?"

**Level 2 — How to use it (junior developer):**
Generate an SBOM with `syft myapp:latest -o cyclonedx-json > sbom.json`. Sign your image with `cosign sign --key cosign.key myapp@sha256:xxx`. In your Kubernetes cluster, install Kyverno or OPA Gatekeeper with a policy that requires all pods to use signed images. When a pod starts, the policy checks the signature before allowing it.

**Level 3 — How it works (mid-level engineer):**
**SBOM generation:** Syft (or Trivy, Grype) parses image layers to extract package manifests (OS: dpkg, rpm, apk; language: pip, npm, maven). Output is SPDX or CycloneDX JSON listing every component. **Signing:** Cosign signs by computing the sha256 of the image manifest, creating a PKCS#8 signature with the private key, and storing the signature as a sibling OCI artifact in the registry (same repo, tag format: `sha256-<digest>.sig`). **Verification:** `cosign verify` fetches the sig artifact, verifies the signature against the public key, and checks the signature covers the correct image manifest digest. **Keyless signing** (Sigstore/Fulcio): instead of managing a private key, CI authenticates to Fulcio (Sigstore's certificate authority) using an OIDC token (GitHub Actions, Google Workload Identity). Fulcio issues a short-lived certificate. Cosign signs with this ephemeral key. The certificate and signature are stored in Rekor (transparency log). Verification: check Rekor for signing event, verify certificate chain to Fulcio CA.

**Level 4 — Why it was designed this way (senior/staff):**
The keyless signing approach (OIDC + Fulcio + Rekor) was designed to solve the key management problem: traditional code signing requires managing private keys (generating, storing, rotating, revoking). This is operationally expensive and a security risk (key compromise = all past and future signatures compromised). Keyless signing uses OIDC identity (GitHub Actions run_id, Google service account, etc.) as the signer identity — ephemeral keys that automatically expire. The transparency log (Rekor) provides auditability: every signing event is publicly recorded, enabling detection of unauthorised signing even with compromised keys. The OCI Referrers API (v1.1) was specifically designed to support supply chain artifacts (SBOMs, signatures, Syft attestations) alongside the images they describe — enabling them to travel together through registries as a unit of trust.

---

### ⚙️ How It Works (Mechanism)

**Complete SBOM + signing pipeline:**
```
┌──────────────────────────────────────────────────────────┐
│       Supply Chain Security Pipeline (CI)                │
├──────────────────────────────────────────────────────────┤
│  docker buildx build → myapp@sha256:abc123               │
│       ↓                                                  │
│  Syft: scan image → sbom.spdx.json                       │
│  (list: nginx 1.25.3, libssl 3.0.11, etc.)               │
│       ↓                                                  │
│  cosign sign --key ci.key myapp@sha256:abc123            │
│  → stores: registry/myapp:sha256-abc123.sig              │
│       ↓                                                  │
│  cosign attach sbom --sbom sbom.spdx.json                │
│  → stores: registry/myapp:sha256-abc123.sbom             │
│       ↓                                                  │
│  cosign attest --key ci.key \                            │
│    --predicate build-provenance.json myapp@sha256:abc123 │
│  → stores: registry/myapp:sha256-abc123.att              │
│  (OCI Referrers API: all are linked to original image)   │
└──────────────────────────────────────────────────────────┘
```

**Admission control (Kubernetes):**
```yaml
# Kyverno policy: reject unsigned images
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  rules:
  - name: check-image-signed
    match:
      resources:
        kinds: ["Pod"]
    verifyImages:
    - imageReferences:
      - "registry.example.com/myapp:*"
      attestors:
      - entries:
        - keys:
            publicKeys: |-
              -----BEGIN PUBLIC KEY-----
              MFkwEwYH... (cosign public key)
              -----END PUBLIC KEY-----
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer commits → CI builds image
  → Syft: generates SBOM ← YOU ARE HERE
  → Cosign: signs image digest
  → SBOM, sig, provenance attached to image in registry
  → kubectl apply deployment
  → Kyverno: verifies signature → PASS
  → Pod starts
  → Security: SBOM queryable for CVE management
```

**FAILURE PATH:**
```
Unsigned or tampered image deployed:
  → Kyverno: cosign verify fails (no valid sig)
  → Pod creation denied: "image failed signature verification"
  → Alert: deployment blocked → security team notified
  → Attacker cannot deploy without CI private key
```

**WHAT CHANGES AT SCALE:**
At scale, signature verification adds 50–200ms latency per pod start (registry lookup for sig artifact). Cache signature verification results to reduce latency. SBOMs must be queryable at scale: store in a graph database (DependencyTrack) for cross-service vulnerability queries like "which services use log4j 2.14.x?" At 10,000 images, SBOM storage and management is a platform concern.

---

### 💻 Code Example

**Example 1 — Generate SBOM with Syft:**
```bash
# Install Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh

# Generate SBOM in multiple formats
syft myapp:latest -o spdx-json=sbom.spdx.json
syft myapp:latest -o cyclonedx-json=sbom.cyclonedx.json
syft myapp:latest -o table   # Human-readable for debugging
```

**Example 2 — Sign image with Cosign:**
```bash
# Generate signing key pair
cosign generate-key-pair  # Creates cosign.key + cosign.pub

# Sign an image (sign the specific digest, not mutable tag)
cosign sign --key cosign.key \
  registry.example.com/myapp@sha256:abc123def456

# Verify signature
cosign verify --key cosign.pub \
  registry.example.com/myapp@sha256:abc123def456

# Keyless signing (GitHub Actions / OIDC)
# No private key needed — uses GitHub OIDC token
cosign sign registry.example.com/myapp@sha256:abc123   # prompts for OIDC
```

**Example 3 — Attach SBOM as OCI artifact:**
```bash
# Attach SBOM to image (stored as OCI referrer)
cosign attach sbom \
  --sbom sbom.spdx.json \
  --type spdx \
  registry.example.com/myapp@sha256:abc123

# Download and verify SBOM
cosign download sbom registry.example.com/myapp:latest
# Prints SBOM JSON to stdout

# List all OCI referrers (sig, sbom, attestations)
cosign tree registry.example.com/myapp:latest
```

**Example 4 — Full CI/CD pipeline (GitHub Actions):**
```yaml
- name: Build and push image
  run: |
    docker buildx build \
      --tag ${{ env.REGISTRY }}/myapp:${{ github.sha }} \
      --push .

- name: Generate SBOM
  run: |
    syft ${{ env.REGISTRY }}/myapp:${{ github.sha }} \
      -o cyclonedx-json > sbom.json

- name: Sign image and attach SBOM
  env:
    COSIGN_EXPERIMENTAL: "1"  # Keyless mode
  run: |
    cosign sign \
      ${{ env.REGISTRY }}/myapp@${{ steps.build.outputs.digest }}
    
    cosign attach sbom \
      --sbom sbom.json --type cyclonedx \
      ${{ env.REGISTRY }}/myapp@${{ steps.build.outputs.digest }}
```

---

### ⚖️ Comparison Table

| Tool | Function | Format | Integration | Best For |
|---|---|---|---|---|
| **Syft** | SBOM generation | SPDX, CycloneDX, table | Trivy, cosign, DependencyTrack | SBOM generation |
| Cosign | Image signing + SBOM attachment | OCI artifacts | Kyverno, Tekton, GitHub Actions | Signing + verification |
| Trivy | SBOM generation + CVE scanning | SPDX, CycloneDX + CVE | Tekton, GitHub Actions | Combined scan+SBOM |
| Grype | CVE scanning from SBOM | SBOM input | Syft pipeline | CVE analysis from SBOM |
| DependencyTrack | SBOM management platform | SPDX, CycloneDX | Syft, Trivy | Enterprise SBOM governance |

How to choose: Syft + Cosign is the de facto open-source standard. Trivy for combined scanning+SBOM. DependencyTrack for enterprise SBOM management and cross-service vulnerability queries.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "An image scan replaces an SBOM" | Image scanning checks an SBOM against a CVE database at a point in time. The SBOM is the persistent record — it can be re-scanned later against new CVE databases, and it serves compliance/audit purposes beyond just CVE detection. |
| "Signing an image means it has no vulnerabilities" | Signing proves identity (who built it) and integrity (not tampered). It says nothing about the image's security posture. A signed image can contain critical CVEs. |
| "SBOMs are only for compliance, not operations" | SBOMs enable operational capabilities: "show me all services using log4j 2.14.x" — queryable across your entire fleet's SBOMs. This is critical for rapid incident response to zero-days. |
| "Keyless signing with Sigstore requires trusting Sigstore" | The transparency log (Rekor) is publicly auditable — it provides auditability without requiring trust in Sigstore itself. Verification checks the OIDC identity claim and the CA certificate chain. |
| "Signature verification at admission time is optional" | If you sign images but don't enforce signature verification at admission, signatures provide no security value — nothing prevents unsigned images from being deployed. Both signing AND verification are required. |

---

### 🚨 Failure Modes & Diagnosis

**Signature verification fails for all pods after key rotation**

**Symptom:**
All pod deployments fail: `"signature verification failed: no valid signatures found"`. Key was rotated but old images are still referenced in deployments.

**Root Cause:**
Old images were signed with the old private key. The admission policy's public key was updated to the new key. Old-signed images fail verification.

**Diagnostic Command / Tool:**
```bash
# Check which key signed the current image
cosign verify --key old-cosign.pub registry.example.com/myapp:latest

# List signatures and their public key identifiers
cosign tree registry.example.com/myapp:latest
```

**Fix:**
Re-sign old images with the new key during the key rotation window, or maintain both old and new public keys in the admission policy during transition. Create a rotation runbook that covers re-signing of all production images.

**Prevention:**
Key rotation procedure must include: (1) re-sign ALL currently deployed images with new key before updating policy, (2) verify all images pass with new key, (3) update admission policy, (4) revoke old key. Never update admission policy before re-signing running images.

---

**SBOM not attached causing compliance failures**

**Symptom:**
Compliance scan reports: "1,247 images missing SBOM". Audit findings trigger regulatory review.

**Root Cause:**
SBOM generation was added to the CI pipeline but old images pre-dating the requirement have no SBOM. Or SBOM generation fails silently (no exit-code 1) in CI.

**Diagnostic Command / Tool:**
```bash
# Check if image has attached SBOM
cosign download sbom registry.example.com/myapp:latest
# If no SBOM: "Error: no SBOMs found for registry.example.com/myapp:latest"
```

**Fix:**
Backfill SBOMs for existing images: run Syft against each image and attach. Add policy: admission webhook rejects images with no SBOM attached (similar to signature enforcement).

**Prevention:**
SBOM generation step must use `set -e` and fail the CI job if Syft fails. Use DependencyTrack to continuously monitor SBOM coverage across all images.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker Image` — image provenance describes the creation of Docker/OCI images
- `OCI Standard` — OCI v1.1 Referrers API is how SBOMs and signatures are attached to images
- `Image Scanning` — scanning uses SBOMs to find CVEs; understand scanning before provenance

**Builds On This (learn these next):**
- `CI/CD` — provenance and SBOM generation happen in CI/CD pipelines
- `Container Security` — provenance/SBOM are supply chain security layers
- `Container Runtime Interface (CRI)` — admission controllers at the CRI level enforce image signature verification

**Alternatives / Comparisons:**
- `Image Scanning` — detects CVEs using SBOM; complementary, not alternative
- `Image Tag Strategy` — immutable tags + digest references are prerequisites for meaningful provenance
- `Container Security` — provenance/SBOM are advanced components of the container security model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ SBOM = ingredient list for image layers.  │
│              │ Provenance = signed build certificate.    │
│              │ Together: what + undeniable proof of who. │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Supply chain attacks: tampered images,    │
│ SOLVES       │ compromised builds, unknown components    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Signing+SBOM without admission            │
│              │ enforcement is theatre. The value is      │
│              │ REJECTING unsigned images at startup.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Production clusters, regulated workloads, │
│              │ multi-tenant platforms, US EO compliance  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Local dev environments (overhead)         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Supply chain security vs tooling          │
│              │ complexity + CI overhead + key management │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Sign your images: an attacker who can    │
│              │  write to your registry can't deploy      │
│              │  without your private key"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Image Scanning → OCI Standard →           │
│              │ Container Runtime Interface (CRI)         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your company generates SBOMs for all images and stores them in DependencyTrack. A zero-day CVE is published affecting `curl 7.88.1` — a component present in 47 of your 200 production services' base images. Using the SBOM data, trace the complete incident response workflow from CVE publication to all affected services patched: what queries you run, how you prioritise by criticality (internet-facing vs internal), how you trigger rebuilds, and how you verify the fix was applied. What is the minimum time from CVE publication to all affected services patched, and what is the manual bottleneck?

**Q2.** Sigstore's keyless signing relies on a centralised transparency log (Rekor) operated by the Linux Foundation. A security researcher argues: "If Rekor is compromised or becomes unavailable, your entire signing infrastructure breaks — this is a dangerous single point of trust." Analyse this argument: what would actually happen to existing image signatures if Rekor were unavailable? What would happen to new signing operations? How does Sigstore's transparency log design mitigate vs introduce centralisation risk, and what alternative architectures exist (self-hosted Rekor, in-toto, SLSA with Tekton Chains) that distribute trust?

