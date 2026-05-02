---
layout: default
title: "Secret Scanning"
parent: "CI/CD"
nav_order: 1012
permalink: /ci-cd/secret-scanning/
number: "1012"
category: CI/CD
difficulty: ★★★
depends_on: CI/CD Pipeline, Git, Dependency Scanning, Container Scanning
used_by: SBOM, Supply Chain Security, Security Policy Enforcement
related: SAST, Dependency Scanning, Container Scanning, SCA
tags:
  - cicd
  - security
  - git
  - devops
  - deep-dive
---

# 1012 — Secret Scanning

⚡ TL;DR — Secret scanning automatically detects API keys, passwords, and tokens committed to source code before they reach production or get exposed in public repositories.

| #1012 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Git, Dependency Scanning, Container Scanning | |
| **Used by:** | SBOM, Supply Chain Security, Security Policy Enforcement | |
| **Related:** | SAST, Dependency Scanning, Container Scanning, SCA | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer pushes a hotfix at 11pm. The changes include a temporary config file with `AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE` to debug a production issue. The fix works, they clean up the code — but the key stays in `config.local.js` which is still tracked in git. The file is committed, pushed, and merged to main. Three weeks later, a GitHub Actions log accidentally prints environment variables. A security researcher sees the key in a public GitHub repository within 6 minutes of the push.

**THE BREAKING POINT:**
Secrets in source code are an extreme confidence violation: a committed secret is immediately in git history, potentially replicated to dozens of developer machines, CI runners, mirrors, and GitHub's servers. Deleting the commit is insufficient — `git log` is immutable, `git reflog` survives, and GitHub's "remove sensitive data" process requires force-push and cache invalidation. The cost of remediation (rotate key, audit access logs, patch affected systems) far exceeds the cost of the entire secret scanning toolchain.

**THE INVENTION MOMENT:**
This is exactly why secret scanning exists: intercept credentials before they ever leave the developer's machine or enter the remote repository — making accidental exposure a caught error at code review time, not a 3am incident.

---

### 📘 Textbook Definition

**Secret scanning** is the automated detection of hard-coded credentials, API keys, tokens, certificates, and other sensitive values in source code, git history, CI/CD logs, and container images. It operates in two modes: **pre-commit** (blocking the commit before it enters git history) using tools like `git-secrets`, `detect-secrets`, or pre-commit hooks; and **repository-level** scanning (GitHub Advanced Security, GitGuardian, TruffleHog) which continuously scans the full git history and all new commits against a database of secret patterns (regular expressions for known credential formats: AWS access keys, GitHub tokens, Stripe keys, private keys). Secret scanning is the CI/CD security complement to dependency scanning (which finds vulnerable code) — covering the orthogonal risk of exposed credentials.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Automatically catch passwords and API keys committed to code before attackers find them first.

**One analogy:**
> Secret scanning is like a spell-checker for security. A spell-checker catches typos before your email is sent. Secret scanning catches committed credentials before your push is permanently recorded in git history. Both work best when they run before the irreversible action — not after.

**One insight:**
The critical window is the 6 minutes between `git push` and when GitHub indexes public repositories for public research tools like TruffleHog and GitGuardian. Once a secret is in a public commit, it must be treated as compromised — full stop. Secret scanning's value is entirely in its shift-left positioning: catching secrets at `git commit` time is 1000x cheaper than rotating compromised credentials under incident conditions.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Git commits are immutable records — once pushed remotely, a secret cannot be truly erased without destructive history rewriting.
2. Secrets have recognisable patterns — AWS keys start with `AKIA`, JWTs have three base64 segments, PEM headers are distinctive.
3. Entropy is a signal — random strings with high Shannon entropy are statistically likely to be secrets, not human-readable content.

**DERIVED DESIGN:**
Given that secrets are patternable and git history is permanent, secret scanning has two fundamentally different deployment positions:

**Pre-commit hooks** (detect-secrets, git-secrets): run on the developer's machine before `git commit` — highest value, prevents entry into history entirely. Requires developer tooling setup and can be bypassed with `--no-verify`.

**CI/CD scanning** (TruffleHog, GitGuardian): scans on push to remote origin — catches what pre-commit missed, runs in an environment developers cannot bypass. Scans the diff (fast) or full history (thorough).

**Repository-level continuous scanning** (GitHub Advanced Security, GitGuardian): scans the entire repository history and all future commits, alerting on any historical or new secret — catches secrets committed before the tool was enabled.

The detection mechanism combines two approaches:
1. **Pattern matching**: regex patterns for known secret formats (>1000 patterns in tools like TruffleHog v3, covering AWS, GCP, Azure, GitHub, Stripe, Twilio, etc.)
2. **Entropy analysis**: strings with Shannon entropy > 3.5 on strings > 20 characters are flagged as potentially random secrets, regardless of format.

**THE TRADE-OFFS:**
**Gain:** Secrets caught before they become incidents. Audit trail of secret access. Shift-left security without friction for developers following process.
**Cost:** False positives — high-entropy strings (base64-encoded data, encoded configs, test fixtures) generate noise. Pattern matching requires constant maintenance as new secret formats emerge. Pre-commit hooks require developer buy-in and can be bypassed.

---

### 🧪 Thought Experiment

**SETUP:**
A two-person startup pushes their MVP to a public GitHub repo. They're moving fast. Backend developer hardcodes a Stripe live API key in `stripe-config.js` to test payments. Commits Sunday night. Merges to main.

**WHAT HAPPENS WITHOUT SECRET SCANNING:**
Monday morning: Automated bots indexing GitHub find `sk_live_...` in the public commit. Within hours, fraudulent Stripe charges begin on the startup's account. Stripe detects anomalous activity and freezes the account — blocking all legitimate customer payments. The startup spends Monday rotating keys, auditing transaction logs, and filing a Stripe dispute. The MVP launch is delayed 3 days.

**WHAT HAPPENS WITH SECRET SCANNING:**
GitHub secret scanning is enabled (free for public repos). Developer commits `sk_live_...`. GitHub detects the Stripe secret pattern within seconds of the push. GitHub automatically notifies Stripe (Secret Scanning Partner Program). Stripe invalidates the key before any bot can use it. GitHub alerts the developer via email. Developer rotates to an environment variable. Zero fraudulent charges. Five-minute fix.

**THE INSIGHT:**
Secret scanning at platform level can trigger automatic revocation through vendor partnerships — making even a brief exposure recoverable. The value is not just detection: the GitHub-to-Stripe notification pipeline converts a potential incident into a non-event in under 10 minutes.

---

### 🧠 Mental Model / Analogy

> Secret scanning is like an airport metal detector, but for your codebase. A metal detector checks everyone departing to catch prohibited items before they board the plane. Secret scanning checks every commit before it boards the remote repository. The airport analogy has an important layer: the detector at departure is the pre-commit hook (catches it before the journey begins), and customs at the destination is the CI scanner (catches anything that slipped through).

- "Airport metal detector at departure" → pre-commit hook (git-secrets, detect-secrets)
- "Customs inspection at destination" → CI/CD scanner (TruffleHog, GitGuardian)
- "Prohibited items list" → regex pattern database (>1000 known secret formats)
- "Passenger's carry-on" → git commit diff
- "Full luggage X-ray" → full git history scan
- "Item confiscated" → secret alert + required rotation

Where this analogy breaks down: an airport can physically confiscate a prohibited item — but once a secret is in a public git commit, detection doesn't undo the exposure. Rotation (changing the secret) is still required even after detection. The earlier the detection, the lower the blast radius.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Sometimes developers accidentally save passwords or secret keys in their code files alongside the real code. Secret scanning automatically checks for this and alerts developers before those credentials get published online, where attackers could use them.

**Level 2 — How to use it (junior developer):**
Enable GitHub secret scanning in repository Settings → Code security. Install `detect-secrets` as a pre-commit hook locally: `pip install detect-secrets` → `detect-secrets scan > .secrets.baseline` → add to pre-commit config. Never hardcode credentials; use environment variables, `dotenv` files (gitignored), or secret managers (AWS Secrets Manager, HashiCorp Vault). If a secret is accidentally committed: immediately rotate it (generate a new key, invalidate the old one) — deleting the commit is secondary and insufficient.

**Level 3 — How it works (mid-level engineer):**
TruffleHog v3 (the industry standard) operates in three modes: (1) scanning git commits using regex detectors (each detector is a Go struct that matches a pattern and optionally makes an API call to verify the secret is live), (2) scanning file content with entropy analysis for non-pattern secrets, and (3) CI mode scanning only the diff since the last clean commit. TruffleHog has 700+ detectors covering specific services; each detector can do live verification (actually call the API with the potential key to confirm it's a real, active secret) — reducing false positives from test keys or example values. GitHub Advanced Security pushes alerts directly to the Security tab and can notify provider partners for automatic revocation.

**Level 4 — Why it was designed this way (senior/staff):**
The shift from entropy-only detection (early gitleaks) to pattern-specific + verified detection (TruffleHog v3) addressed the false positive problem that made early tools unusable. High entropy detection alone generates alerts on every base64 blob, compressed binary, and hash — burying real findings in noise. Provider-specific patterns with verification collapsed false positive rates from ~80% to ~5%. GitHub's Secret Scanning Partner Program (2019) formalised platform-level automation: GitHub sends detected secrets to partner APIs for immediate invalidation, creating a response loop that's faster than any human can react. The emerging "push protection" feature (block push if secret detected) mirrors the pre-commit model but enforced server-side — removing the bypass vector of `--no-verify` on the client.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│  SECRET SCANNING EXECUTION MODES        │
├─────────────────────────────────────────┤
│                                         │
│  MODE 1: PRE-COMMIT (client-side)       │
│  git commit triggered                   │
│  → detect-secrets / git-secrets hook    │
│  → scan staged files against patterns  │
│  → HIGH ENTROPY string detected?        │
│  → PATTERN match (AKIA*, sk_live*, ...)?│
│  → BLOCK commit + show findings         │
│  → Developer fixes → re-commit          │
│                                         │
│  MODE 2: CI DIFF SCAN (server-side)     │
│  git push → CI triggered                │
│  → TruffleHog scans commit diff         │
│  → Pattern match engine (700+ patterns) │
│  → Live verification API call           │
│  → VERIFIED secret → FAIL + alert      │
│                                         │
│  MODE 3: FULL HISTORY SCAN              │
│  → All branches + full git history      │
│  → Detects secrets committed months ago │
│  → GitHub Advanced Security continuous  │
│                                         │
│  PARTNER NOTIFICATION:                  │
│  GitHub detects → POST to partner API   │
│  → Stripe/AWS/GH auto-revoke token      │
│  → Notification sent to committer email │
└─────────────────────────────────────────┘
```

**Pattern detection internals:**
Each detector uses a primary regex to find candidate strings, then applies secondary validation (length check, character set, checksum — AWS keys have a built-in character constraint). TruffleHog's Go-based detector pipeline achieves ~50MB/s throughput on git history. For a repo with 10 years of history and 100k commits, a full scan typically completes in 2–8 minutes.

**Entropy calculation:**
Shannon entropy H(X) = -Σ p(x) log₂ p(x). A random 32-character string has H ≈ 4–5 bits/char. English prose has H ≈ 1–2 bits/char. Most secret scanning tools flag strings with H > 3.5 bits/char over 20+ characters as high-entropy candidates.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes code with DB_PASSWORD=...
  → git add config.js
  → git commit
  → pre-commit hook fires [← YOU ARE HERE]
     detect-secrets scans staged files
     → HIGH ENTROPY: "xK9#mP2$nR7..." in config.js
     → BLOCKED: potential secret detected
  → Developer moves to .env (gitignored)
  → git commit passes
  → git push → CI scanner confirms clean
  → Code merged
```

**FAILURE PATH:**
```
Pre-commit hook bypassed: git commit --no-verify
  → Secret enters local git history
  → git push → CI scanner misses (regex gap)
  → Merges to main
  → GitHub indexes public repo
  → External bot detects within 6 minutes
  → Credentials used by attacker
  → Observable: anomalous API usage in logs
```

**WHAT CHANGES AT SCALE:**
At 500+ repositories, a centralised secret management audit dashboard becomes essential. GitGuardian or GitHub Advanced Security provide org-level dashboards showing secrets detected per repo, remediation SLA compliance, and repeat offender patterns. Engineering teams set policy: secrets must be rotated within 24 hours of detection, breached SLA escalates to manager, repeat offenders require mandatory security training. Platform teams automate `.gitignore` template enforcement across all repos.

---

### 💻 Code Example

**Example 1 — detect-secrets pre-commit setup:**
```bash
# Install detect-secrets
pip install detect-secrets

# Create baseline (baseline captures known/accepted secrets)
detect-secrets scan > .secrets.baseline

# Add pre-commit hook configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install hooks
pre-commit install

# Now: any commit with a new high-entropy string is blocked
```

**Example 2 — TruffleHog CI scan (GitHub Actions):**
```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning
on: [push, pull_request]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history for complete coverage

      - name: TruffleHog OSS scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified
          # --only-verified: only report confirmed live secrets
          # (eliminates test/example key false positives)
```

**Example 3 — Correct secret management pattern:**
```bash
# BAD: hardcoded in source code
DATABASE_URL=postgres://user:p4ssw0rd@db:5432/mydb

# BAD: in a .env file committed to git
echo "DB_PASSWORD=secret123" >> .env
git add .env  # DON'T DO THIS
```
```bash
# GOOD: .env gitignored, loaded at runtime from secret manager
# .gitignore contains: .env

# Production: inject via environment (CI/CD or Kubernetes)
kubectl create secret generic db-creds \
  --from-literal=password=YOUR_PASSWORD

# Local dev: use .env.example with placeholder values
echo "DB_PASSWORD=<replace-with-your-dev-password>" \
  > .env.example
git add .env.example  # template only — no real values
```

**Example 4 — Remediating a committed secret:**
```bash
# If secret was committed — ROTATE FIRST, THEN clean
# Step 1: Rotate the credential immediately
# (assume exposed — generate new key in AWS/Stripe/etc.)

# Step 2: Remove from git history (git rebase)
# For recent commit:
git rebase -i HEAD~3
# Set offending commit to 'edit', then:
git reset HEAD^
# Remove secret file from tracked files
git add -p  # re-add everything except the secret
git commit --amend
git rebase --continue

# Step 3: Force push (notify team)
git push --force-with-lease origin main

# Step 4: Notify GitHub to purge from cache
# GitHub: Settings → Contact Support → Cache invalidation
```

---

### ⚖️ Comparison Table

| Tool | Pre-commit | CI Scan | History Scan | Live Verify | Free |
|---|---|---|---|---|---|
| **GitHub Advanced Security** | No | Yes | Yes | No | No (GHAS) |
| TruffleHog v3 | Yes | Yes | Yes | Yes | Yes |
| GitGuardian | No | Yes | Yes | No | Limited |
| detect-secrets | Yes | Yes | No | No | Yes |
| git-secrets (AWS) | Yes | No | No | No | Yes |
| Gitleaks | Yes | Yes | Yes | No | Yes |

How to choose: Use **TruffleHog** in CI for its verified-only mode (lowest false positive rate) and history scanning. Use **detect-secrets** as the pre-commit hook (developer-side, fast). Enable **GitHub Advanced Security** on GitHub for the Partner Program auto-revocation feature on public and enterprise repos. Use **GitGuardian** for org-level dashboards and SLA tracking at scale.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Deleting a file removes the secret | Git history is permanent. The secret exists in every commit before deletion and in every developer's local clone. Rotation is the only effective remediation. |
| Private repositories are safe | Private repo secrets can be exposed via: compromised team member account, GitHub data breach, accidental visibility change, or forks that become public. Treat private repos as "less exposed," not "safe." |
| Environment variables in CI logs are safe | CI log output is commonly captured, searchable, and retained for months. `echo $SECRET` in CI scripts permanently embeds credentials in log archives. Use `--add-mask` in GitHub Actions to redact secrets from logs. |
| `--no-verify` bypass means pre-commit is useless | Pre-commit hooks catch honest mistakes (the majority of incidents). CI-level scanning (server-enforced) catches malicious bypasses. Both layers together provide defence-in-depth. |
| Rotating the key is enough after exposure | After rotation, also audit the access logs for the old key (what was accessed with it?), check all dependent services that used it, and review why the secret was in source in the first place. |
| Secret scanning only applies to source code | Secrets appear in: Docker image history (`docker history`), CI/CD logs, container environment variables, Kubernetes ConfigMaps, Helm values files, Terraform state files. Scan all surfaces. |

---

### 🚨 Failure Modes & Diagnosis

**1. Secret Scanned But Not Rotated After Alert**

**Symptom:** GitGuardian shows 47 open secret alerts. Team acknowledges alerts but considers them "low risk" in a private repo. Six months later, repo accidentally becomes public for 15 minutes before being caught.

**Root Cause:** Culture of treating secret alerts as informational rather than mandatory action items. No SLA on secret rotation. Alert fatigue from false positives.

**Diagnostic:**
```bash
# Query GitGuardian API for unresolved secrets
curl -H "Authorization: Token $GG_TOKEN" \
  "https://api.gitguardian.com/v1/incidents?status=TRIGGERED" \
  | jq '[.results[] | {id, date: .date, severity: .severity}]'

# Check GitHub secret scanning alerts
gh api \
  /repos/{owner}/{repo}/secret-scanning/alerts \
  --jq '.[] | select(.state == "open") | {number, secret_type}'
```

**Fix:** Implement mandatory rotation SLA: all secret alerts must be resolved within 24 hours. Auto-assign alerts to committer. Create runbook: detect → rotate → document → close alert.

**Prevention:** Set GitHub secret scanning push protection to block pushes containing detected secrets (Settings → Code and automation → Code security → Push protection).

---

**2. False Positives Block Developer Workflow**

**Symptom:** Every PR fails secret scanning due to base64-encoded test fixtures in unit tests. Developers start ignoring or bypassing alerts.

**Root Cause:** Entropy-only detection without pattern matching flags any high-entropy string. Test fixtures with `"expectedResponse": "eyJhbGciOiJIUzI1NiJ9..."` (base64-encoded test JWT) triggers false positive on every run.

**Diagnostic:**
```bash
# See which detectors are triggering
trufflehog git file://. --json 2>&1 | \
  jq '.DetectorName' | sort | uniq -c | sort -rn

# Check false positive rate
trufflehog git file://. --only-verified --json | \
  jq 'select(.Verified == true) | .DetectorName'
# --only-verified drastically reduces false positives
```

**Fix:**
```bash
# Use TruffleHog's --only-verified flag
trufflehog git file://. --only-verified

# Or add allow-list in detect-secrets baseline
detect-secrets audit .secrets.baseline
# Mark known false positives as "whitelisted" with reason
```

**Prevention:** Use `--only-verified` in CI. Maintain a `.secrets.baseline` for accepted false positives with documented reasons. Review and trim the baseline quarterly.

---

**3. Terraform State File Exposes Secrets**

**Symptom:** `terraform.tfstate` is committed to git. The state file contains plain-text RDS passwords, certificate private keys, and IAM access keys generated by Terraform.

**Root Cause:** Terraform state files contain the full output of all resources — including sensitive outputs (passwords, keys). Developers treat them as config files and commit them.

**Diagnostic:**
```bash
# Search terraform state for high-entropy strings
cat terraform.tfstate | python3 -c "
import sys, json, re
state = json.load(sys.stdin)
for r in state.get('resources', []):
  for i in r.get('instances', []):
    for k, v in i.get('attributes', {}).items():
      if isinstance(v, str) and len(v) > 20:
        entropy = sum(-v.count(c)/len(v) *
          __import__('math').log2(v.count(c)/len(v))
          for c in set(v))
        if entropy > 3.5:
          print(f'{k}: entropy={entropy:.2f}')
"
```

**Fix:**
```hcl
# terraform.tfstate → ALWAYS in .gitignore
# Use remote state with encryption:
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true  # AES-256 at rest
    dynamodb_table = "terraform-lock"
  }
}
```

**Prevention:** Terraform state must use remote backend (S3+DynamoDB, Terraform Cloud) from day 1. Add `*.tfstate` and `*.tfstate.backup` to `.gitignore` in the project template. Run `trufflehog filesystem terraform.tfstate` as a separate check.

---

**4. Secrets in Container Image Environment Variables**

**Symptom:** `docker inspect myapp:prod | jq '.[].Config.Env'` reveals `DATABASE_PASSWORD=prod_p4ssw0rd` embedded in the image.

**Root Cause:** Developer added `ENV DATABASE_PASSWORD=...` in Dockerfile or passed `--build-arg` that became a permanent layer. Image is pushed to registry accessible to all engineers.

**Diagnostic:**
```bash
# Inspect all environment variables in image
docker inspect myapp:prod | \
  jq '.[].Config.Env[]' | grep -iE "(pass|key|secret|token)"

# Check image history for leaked build args
docker history --no-trunc myapp:prod | \
  grep -iE "(pass|secret|key|token)"

# Use Trivy secret scanner
trivy image --scanners secret myapp:prod
```

**Fix:**
```dockerfile
# BAD: secrets baked into image layers
ENV DATABASE_PASSWORD=prod_password

# GOOD: secrets injected at runtime only
# In Kubernetes:
# envFrom: - secretRef: name: db-credentials
# Never bake secrets into image builds
```

**Prevention:** Add `trivy image --scanners secret` to CI pipeline post-build. Enforce no-ENV-secrets via Hadolint (rule: DL3025). Use BuildKit `--secret` mount for build-time secrets.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Git` — secret scanning operates on git commits and history; understanding git objects and commit structure is required
- `CI/CD Pipeline` — server-side secret scanning runs as a CI stage; understanding pipeline architecture is required
- `Dependency Scanning` — the parallel practice; dependency scanning finds vulnerable code, secret scanning finds exposed credentials

**Builds On This (learn these next):**
- `Supply Chain Security` — secret scanning is one layer; full supply chain security extends to verifying artifact provenance and build pipeline integrity
- `SBOM` — SBOMs document all components; secret scanning documents the security hygiene of credentials management alongside component inventory
- `Kubernetes Secrets` — proper secrets management (what secret scanning enforces) relies on external secret stores and Kubernetes Secret objects

**Alternatives / Comparisons:**
- `SAST` — scans first-party code for logic vulnerabilities; secret scanning specifically targets credential patterns in code rather than code logic flaws
- `Container Scanning` — scans Docker images for CVEs and embedded secrets (complementary); secret scanning covers the source code and git history layer
- `HashiCorp Vault` — secret management solution (where secrets should live); secret scanning enforces that secrets are NOT in source code

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automated detection of credentials and    │
│              │ tokens in source code and git history     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Accidentally committed secrets remaining  │
│ SOLVES       │ in git history and being exposed publicly │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Deleting a file doesn't remove a secret — │
│              │ rotation is always required after detection│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — pre-commit + CI + continuous     │
│              │ repo scanning as three complementary layers│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip — tune with --only-verified    │
│              │ to eliminate false positive alert fatigue │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Catches credential exposure vs            │
│              │ false positive noise requiring tuning     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Spell-checker for security —             │
│              │  catch before the irreversible push."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Supply Chain Security → SBOM →            │
│              │ HashiCorp Vault → SLSA                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer on your team commits a Stripe live API key. Your pre-commit hook was not installed. Your CI secret scanner catches it 3 minutes after push — but the repository is public. Trace every step of the complete incident response: from the moment the scanner fires to the moment you can confirm the blast radius is contained and the secret is safe. What time-sensitive actions must happen in what order, and what information do you need at each step?

**Q2.** Your engineering team has 200 engineers across 50 repositories. The secret scanning dashboard shows an average of 15 new secret alerts per week. 70% are false positives (base64 test fixtures, example keys in documentation). Design a system — combining tooling configuration, process, and incentive structure — that reduces the false positive rate below 10% while ensuring genuine secrets are never ignored or treated as noise.

