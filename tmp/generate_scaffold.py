#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_scaffold.py
====================
Pre-generates v3.0 scaffold .md files for sk-keys dictionary entries.

Each scaffold has:
  - Correct YAML frontmatter (auto-filled from existing frontmatter + registry)
  - All 22 required sections in correct order with [FILL:...] stubs
  - Proper --- separators before every ### heading
  - Conditional sections 5.13, 5.14, 5.15 included with [FILL] stubs

The AI only needs to replace [FILL:...] stubs with actual content.
This reduces AI output by ~50% and eliminates structural errors.

Usage:
  python tmp/generate_scaffold.py <CODE> <START> [END]
  python tmp/generate_scaffold.py DST 061 065
  python tmp/generate_scaffold.py JVM 037

Output:
  Writes directly to dictionary/<tier>/<folder>/<CODE>-<NNN> - <title>.md
  Existing file is overwritten with scaffold.
  Prints summary of [FILL] stubs that need content.
"""

import os
import re
import sys
from pathlib import Path

BASE = Path(r"C:\ASK\MyWorkspace\sk-keys")
DICT_BASE = BASE / "dictionary"

# Full category registry
CATEGORIES = {
    "CSF": {"name": "CS Fundamentals - Paradigms",    "tier": "tier-1-foundations",              "folder": "CSF-cs-fundamentals",      "slug": "cs-fundamentals"},
    "DSA": {"name": "Data Structures & Algorithms",   "tier": "tier-1-foundations",              "folder": "DSA-data-structures",      "slug": "data-structures"},
    "OSY": {"name": "Operating Systems",              "tier": "tier-1-foundations",              "folder": "OSY-operating-systems",    "slug": "operating-systems"},
    "LNX": {"name": "Linux",                          "tier": "tier-1-foundations",              "folder": "LNX-linux",                "slug": "linux"},
    "NET": {"name": "Networking",                     "tier": "tier-2-networking-security",      "folder": "NET-networking",           "slug": "networking"},
    "API": {"name": "HTTP & APIs",                    "tier": "tier-2-networking-security",      "folder": "API-http-apis",            "slug": "http-apis"},
    "SEC": {"name": "Security",                       "tier": "tier-2-networking-security",      "folder": "SEC-security",             "slug": "security"},
    "JVM": {"name": "Java & JVM Internals",           "tier": "tier-3-java",                     "folder": "JVM-java-jvm-internals",   "slug": "jvm"},
    "JLG": {"name": "Java Language",                  "tier": "tier-3-java",                     "folder": "JLG-java-language",        "slug": "java-language"},
    "JCC": {"name": "Java Concurrency",               "tier": "tier-3-java",                     "folder": "JCC-java-concurrency",     "slug": "java-concurrency"},
    "SPR": {"name": "Spring Core",                    "tier": "tier-3-java",                     "folder": "SPR-spring-core",          "slug": "spring-core"},
    "DBF": {"name": "Database Fundamentals",          "tier": "tier-4-data",                     "folder": "DBF-database-fundamentals","slug": "database-fundamentals"},
    "NDB": {"name": "NoSQL & Distributed Databases",  "tier": "tier-4-data",                     "folder": "NDB-nosql-distributed",    "slug": "nosql-distributed"},
    "CCH": {"name": "Caching",                        "tier": "tier-4-data",                     "folder": "CCH-caching",              "slug": "caching"},
    "DAT": {"name": "Data Fundamentals",              "tier": "tier-4-data",                     "folder": "DAT-data-fundamentals",    "slug": "data-fundamentals"},
    "BIG": {"name": "Big Data & Streaming",           "tier": "tier-4-data",                     "folder": "BIG-bigdata-streaming",    "slug": "bigdata-streaming"},
    "DST": {"name": "Distributed Systems",            "tier": "tier-5-distributed-architecture", "folder": "DST-distributed-systems",  "slug": "distributed-systems"},
    "MSV": {"name": "Microservices",                  "tier": "tier-5-distributed-architecture", "folder": "MSV-microservices",        "slug": "microservices"},
    "SYD": {"name": "System Design",                  "tier": "tier-5-distributed-architecture", "folder": "SYD-system-design",        "slug": "system-design"},
    "SAP": {"name": "Software Architecture Patterns", "tier": "tier-5-distributed-architecture", "folder": "SAP-software-architecture","slug": "software-architecture"},
    "DPT": {"name": "Design Patterns",                "tier": "tier-5-distributed-architecture", "folder": "DPT-design-patterns",      "slug": "design-patterns"},
    "CTR": {"name": "Containers",                     "tier": "tier-6-infrastructure-devops",    "folder": "CTR-containers",           "slug": "containers"},
    "K8S": {"name": "Kubernetes",                     "tier": "tier-6-infrastructure-devops",    "folder": "K8S-kubernetes",           "slug": "kubernetes"},
    "AWS": {"name": "Cloud - AWS",                    "tier": "tier-6-infrastructure-devops",    "folder": "AWS-cloud-aws",            "slug": "cloud-aws"},
    "AZR": {"name": "Cloud - Azure",                  "tier": "tier-6-infrastructure-devops",    "folder": "AZR-cloud-azure",          "slug": "cloud-azure"},
    "CCD": {"name": "CI/CD",                          "tier": "tier-6-infrastructure-devops",    "folder": "CCD-cicd",                 "slug": "cicd"},
    "GIT": {"name": "Git & Branching Strategy",       "tier": "tier-6-infrastructure-devops",    "folder": "GIT-git-branching",        "slug": "git-branching"},
    "MVN": {"name": "Maven & Build Tools",            "tier": "tier-6-infrastructure-devops",    "folder": "MVN-maven-build",          "slug": "maven-build"},
    "CDQ": {"name": "Code Quality",                   "tier": "tier-6-infrastructure-devops",    "folder": "CDQ-code-quality",         "slug": "code-quality"},
    "TST": {"name": "Testing",                        "tier": "tier-6-infrastructure-devops",    "folder": "TST-testing",              "slug": "testing"},
    "OBS": {"name": "Observability & SRE",            "tier": "tier-6-infrastructure-devops",    "folder": "OBS-observability-sre",    "slug": "observability-sre"},
    "IAC": {"name": "Infrastructure as Code",         "tier": "tier-6-infrastructure-devops",    "folder": "IAC-infrastructure-code",  "slug": "infrastructure-code"},
    "HTM": {"name": "HTML",                           "tier": "tier-7-frontend",                 "folder": "HTM-html",                 "slug": "html"},
    "CSS": {"name": "CSS",                            "tier": "tier-7-frontend",                 "folder": "CSS-css",                  "slug": "css"},
    "JSC": {"name": "JavaScript",                     "tier": "tier-7-frontend",                 "folder": "JSC-javascript",           "slug": "javascript"},
    "TSC": {"name": "TypeScript",                     "tier": "tier-7-frontend",                 "folder": "TSC-typescript",           "slug": "typescript"},
    "RCT": {"name": "React",                          "tier": "tier-7-frontend",                 "folder": "RCT-react",                "slug": "react"},
    "ANG": {"name": "Angular",                        "tier": "tier-7-frontend",                 "folder": "ANG-angular",              "slug": "angular"},
    "NDJ": {"name": "Node.js",                        "tier": "tier-7-frontend",                 "folder": "NDJ-nodejs",               "slug": "nodejs"},
    "NPM": {"name": "npm & Package Management",       "tier": "tier-7-frontend",                 "folder": "NPM-npm-packages",         "slug": "npm-packages"},
    "WBP": {"name": "Webpack & Build Tools",          "tier": "tier-7-frontend",                 "folder": "WBP-webpack-build",        "slug": "webpack-build"},
    "AIF": {"name": "AI Foundations",                 "tier": "tier-8-artificial-intelligence",  "folder": "AIF-ai-foundations",       "slug": "ai-foundations"},
    "LLM": {"name": "LLMs & Prompt Engineering",      "tier": "tier-8-artificial-intelligence",  "folder": "LLM-llms-prompt-eng",      "slug": "llms-prompt-eng"},
    "RAG": {"name": "RAG & Agents & LLMOps",          "tier": "tier-8-artificial-intelligence",  "folder": "RAG-rag-agents-llmops",    "slug": "rag-agents-llmops"},
    "AIP": {"name": "AI Product Engineering",         "tier": "tier-8-artificial-intelligence",  "folder": "AIP-ai-product",           "slug": "ai-product"},
    "ASY": {"name": "Async & Background Processing",  "tier": "tier-9-professional-domain",      "folder": "ASY-async-background",     "slug": "async-background"},
    "DGN": {"name": "Document Generation",            "tier": "tier-9-professional-domain",      "folder": "DGN-document-generation",  "slug": "document-generation"},
    "FIN": {"name": "Financial Services Domain",      "tier": "tier-9-professional-domain",      "folder": "FIN-financial-domain",     "slug": "financial-domain"},
    "PLT": {"name": "Platform & Modern SWE",          "tier": "tier-9-professional-domain",      "folder": "PLT-platform-swe",         "slug": "platform-swe"},
    "BHV": {"name": "Behavioral & Leadership",        "tier": "tier-9-professional-domain",      "folder": "BHV-behavioral-leadership","slug": "behavioral-leadership"},
}

# Approved tags (for reference in stubs)
DOMAIN_TAGS = [
    "distributed", "architecture", "pattern", "algorithm", "datastructure",
    "deep-dive", "advanced", "foundational", "intermediate", "performance",
    "security", "observability", "async", "streaming", "caching", "database",
    "networking", "concurrency", "memory", "gc", "internals", "api",
    "microservices", "containers", "cloud", "devops", "testing", "cicd",
    "frontend", "browser", "rendering", "ai", "llm", "rag", "agents",
]

# ── Helpers ───────────────────────────────────────────────────────────────

def read_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter fields from an existing file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            return {}
        end = text.find("\n---", 3)
        if end == -1:
            return {}
        fm_text = text[3:end]
        fields = {}
        # Multi-line tags (YAML list)
        tags = []
        in_tags = False
        for line in fm_text.splitlines():
            if re.match(r"^tags:", line):
                in_tags = True
                continue
            if in_tags:
                m = re.match(r"^\s+-\s+(\S+)", line)
                if m:
                    tags.append(m.group(1))
                else:
                    in_tags = False
            m = re.match(r"^(\w+):\s*(.*)$", line)
            if m:
                fields[m.group(1)] = m.group(2).strip().strip('"\'')
        if tags:
            fields["_tags"] = tags
        return fields
    except Exception as e:
        print(f"  WARN: could not read frontmatter from {path}: {e}")
        return {}


def find_file(cat_dir: Path, code: str, nnn: str) -> Path | None:
    """Find existing file matching CODE-NNN - *.md"""
    matches = list(cat_dir.glob(f"{code}-{nnn} - *.md"))
    return matches[0] if matches else None


def title_to_slug(title: str) -> str:
    """Convert title to URL-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[()&/]", "", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def yaml_quote_title(title: str) -> str:
    """Double-quote title if it contains ': ' (colon-space)."""
    if ": " in title:
        return f'"{title}"'
    return title


# ── Scaffold content builder ──────────────────────────────────────────────

def build_scaffold(code: str, nnn: str, cat: dict, fm: dict,
                   title: str, filename: str) -> str:
    """Build the complete scaffold markdown content."""
    id_str      = f"{code}-{nnn}"
    cat_name    = cat["name"]
    tier        = cat["tier"]
    folder      = cat["folder"]
    cat_slug    = cat["slug"]
    difficulty  = fm.get("difficulty", "★★☆")
    nav_order   = int(nnn)
    keyword_slug = title_to_slug(title)
    permalink   = f"/{cat_slug}/{keyword_slug}/"
    yaml_title  = yaml_quote_title(title)

    # Preserve existing dep fields if they look like CODE-NNN IDs
    def clean_dep(field):
        raw = fm.get(field, "").strip()
        if not raw or raw.lower() in ("", "null", "~"):
            return ""
        parts = [p.strip() for p in raw.split(",")]
        valid = [p for p in parts if re.match(r"^[A-Z]{3}-\d{3}$", p)]
        return ", ".join(valid) if valid else ""

    depends_on = clean_dep("depends_on")
    used_by    = clean_dep("used_by")
    related    = clean_dep("related")

    # Tags: preserve approved existing tags, else suggest placeholders
    existing_tags = fm.get("_tags", [])
    valid_tags = [t for t in existing_tags
                  if t in DOMAIN_TAGS or t in [
                      "java", "jvm", "spring", "springboot", "javascript",
                      "typescript", "react", "angular", "nodejs", "python",
                      "docker", "kubernetes", "linux", "aws", "azure", "gcp",
                      "pattern", "algorithm", "datastructure", "protocol",
                      "deep-dive", "foundational", "intermediate", "advanced",
                      "mental-model", "tradeoff", "antipattern", "bestpractice",
                      "thought-experiment", "first-principles", "production", "diagnosis",
                  ]]
    tags_block = "\n".join(f"  - {t}" for t in valid_tags) if valid_tags else (
        "  - [FILL: tag1]  # from approved taxonomy\n"
        "  - [FILL: tag2]\n"
        "  - [FILL: tag3]"
    )

    title_upper = title.upper()

    return f"""---
id: {id_str}
title: {yaml_title}
category: {cat_name}
tier: {tier}
folder: {folder}
difficulty: {difficulty}
depends_on: {depends_on}
used_by: {used_by}
related: {related}
tags:
{tags_block}
status: complete
version: 1
layout: default
parent: "{cat_name}"
grand_parent: "Technical Dictionary"
nav_order: {nav_order}
permalink: {permalink}
---

# {id_str} - {title_upper}

[FILL: TL;DR - one sentence, max 25 words. Format: "⚡ TL;DR - ..."]

| Metadata | | |
|:---|:---|:---|
| **Depends on:** | {depends_on} | |
| **Used by:** | {used_by} | |
| **Related:** | {related} | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
[FILL: concrete pain scenario, 100-200 words. What breaks, slows, or fails without this concept?]

**THE BREAKING POINT:**
[FILL: the specific failure event that made this invention necessary]

**THE INVENTION MOMENT:**
[FILL: who invented this, when, and the key insight that made it possible]

**EVOLUTION:**
[FILL: timeline of key milestones, e.g. "1979: X invented Y. 2007: Z adopted it. Today: ..."]

---

### 📘 Textbook Definition

[FILL: 2-4 sentences. Precise technical definition using correct terminology. Bold the keyword name on first mention.]

---

### ⏱️ Understand It in 30 Seconds

**One line:** [FILL: ≤15 words]

> [FILL: analogy in blockquote — use a concrete, everyday comparison]

**One insight:** [FILL: the non-obvious key insight — what makes this different from naive solutions]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [FILL: first irreducible truth about this concept]
2. [FILL: second irreducible truth]
3. [FILL: third irreducible truth]

**DERIVED DESIGN:**
[FILL: how the invariants lead to the specific design. Show the logical chain: because of invariant 1, we must do X. Because of invariant 2, we cannot do Y.]

**THE TRADE-OFFS:**
**Gain:** [FILL: what you get by using this]
**Cost:** [FILL: what you give up or accept]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [FILL: complexity that is irreducible — inherent to the problem]
**Accidental:** [FILL: complexity that is a consequence of implementation choices]

---

### 🧪 Thought Experiment

**SETUP:** [FILL: concrete scenario — a specific system doing a specific thing]

**WHAT HAPPENS WITHOUT {title_upper}:**
[FILL: the failure scenario — be specific about what breaks, how, and what the user observes]

**WHAT HAPPENS WITH {title_upper}:**
[FILL: the success scenario — contrasted clearly with the failure above]

**THE INSIGHT:** [FILL: the single sentence that captures what the thought experiment reveals]

---

### 🧠 Mental Model / Analogy

> [FILL: primary analogy in blockquote. Must be a concrete everyday object or process, not another technical concept]

**Mapping:**
- **[analogy element 1]** -> [concept element 1]
- **[analogy element 2]** -> [concept element 2]
- **[analogy element 3]** -> [concept element 3]
- **[analogy element 4]** -> [concept element 4]

Where this analogy breaks down: [FILL: one sentence — what the analogy gets wrong or oversimplifies]

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
[FILL: no jargon, everyday language, 3-5 sentences]

**Level 2 - How to use it (junior developer):**
[FILL: practical how-to — APIs, config, CLI commands. What do you actually do?]

**Level 3 - How it works (mid-level engineer):**
[FILL: internal mechanism — algorithms, data structures, network flows. How does it work internally?]

**Level 4 - Why it was designed this way (senior/staff):**
[FILL: design decisions, alternatives considered, trade-offs made. Why is it THIS way and not another?]

**Expert Thinking Cues:**
- "[FILL: diagnostic signal/pattern]" -> [FILL: what it means and what to check/do]
- "[FILL: diagnostic signal/pattern]" -> [FILL: what it means and what to check/do]
- "[FILL: diagnostic signal/pattern]" -> [FILL: what it means and what to check/do]

---

### ⚙️ How It Works (Mechanism)

[FILL: step-by-step technical walkthrough. Include an ASCII diagram or code block showing the mechanism. Max 59 chars wide for ASCII.]

---

### 🔄 The Complete Picture - End-to-End Flow

[FILL: ASCII flow diagram showing the complete system context — what comes before, during, and after. Mark the current concept with "<- YOU ARE HERE". Max 59 chars wide.]

**FAILURE PATH:**
[FILL: what happens when the mechanism fails — specific error conditions and observable symptoms]

**WHAT CHANGES AT SCALE:**
[FILL: how behavior changes at high load, large data volumes, or many distributed nodes]

---

### 💻 Code Example

**BAD - [FILL: name the antipattern]:**
```java
// BAD: [FILL: why this approach fails]
// [FILL: code showing the wrong way, ≤70 chars per line]
```

**GOOD - [FILL: name the correct pattern]:**
```java
// GOOD: [FILL: why this approach works]
// [FILL: code showing the right way, ≤70 chars per line]

// How to verify correctness:
// [FILL: test/verification approach]
```

---

### ⚖️ Comparison Table

| | {title} | [FILL: Alternative 1] | [FILL: Alternative 2] |
|:---|:---|:---|:---|
| [FILL: criterion] | [fill] | [fill] | [fill] |
| [FILL: criterion] | [fill] | [fill] | [fill] |
| [FILL: criterion] | [fill] | [fill] | [fill] |
| Use case | [fill] | [fill] | [fill] |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "[FILL: misconception 1]" | [FILL: reality — 3-5 sentences explaining why the misconception is wrong and what is actually true] |
| "[FILL: misconception 2]" | [FILL: reality] |
| "[FILL: misconception 3]" | [FILL: reality] |
| "[FILL: misconception 4]" | [FILL: reality] |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: [FILL: failure mode name]**

**Symptom:** [FILL: observable production symptom — metrics, logs, user impact]
**Root Cause:** [FILL: technical explanation of why this happens]
**Diagnostic:**
```bash
# [FILL: real diagnostic command — must be an actual runnable command]
[FILL: command]
```
**Fix:** [FILL: BAD approach first, then GOOD approach]
**Prevention:** [FILL: how to prevent this before it happens]

**Failure Mode 2: [FILL: failure mode name]**

**Symptom:** [FILL]
**Root Cause:** [FILL]
**Diagnostic:**
```bash
[FILL: command]
```
**Fix:** [FILL]
**Prevention:** [FILL]

**Failure Mode 3: Security - [FILL: security failure mode name]**

**Symptom:** [FILL: security incident — what the attacker does and what is exposed]
**Root Cause:** [FILL: the vulnerability — why this is exploitable]
**Diagnostic:**
```bash
[FILL: security diagnostic command]
```
**Fix:** [FILL: security remediation]
**Prevention:** [FILL: security hardening measures]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [FILL: CODE-NNN] - [Keyword] ([why it must be understood first])

**Builds On This (learn these next):**
- [FILL: CODE-NNN] - [Keyword] ([what this concept enables])
- [FILL: CODE-NNN] - [Keyword] ([what else builds on this])

**Alternatives / Comparisons:**
- [FILL: CODE-NNN] - [Keyword] ([how it compares / when to choose one over the other])

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | [FILL: core concept - 1 line]  |
+------------------+--------------------------------+
| PROBLEM SOLVED   | [FILL: the pain it solves]     |
+------------------+--------------------------------+
| KEY INSIGHT      | [FILL: non-obvious insight]    |
+------------------+--------------------------------+
| USE WHEN         | [FILL: specific condition]     |
+------------------+--------------------------------+
| AVOID WHEN       | [FILL: when NOT to use]        |
+------------------+--------------------------------+
| TRADE-OFF        | [FILL: gain vs cost]           |
+------------------+--------------------------------+
| ONE-LINER        | "[FILL: memorable insight]"    |
+------------------+--------------------------------+
| NEXT EXPLORE     | [FILL: CODE-NNN; CODE-NNN]     |
+------------------+--------------------------------+
```

**If you remember only 3 things:**
1. [FILL: most important insight]
2. [FILL: second most important insight]
3. [FILL: third most important insight]

**Interview one-liner:**
"[FILL: 3-5 sentence interview-ready answer covering what it is, how it works, and key trade-off]"

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
[FILL: 1-2 sentences capturing the meta-lesson — the pattern that applies to 10 other concepts]

**Where else this pattern appears:**
- **[FILL: Domain 1]:** [FILL: how the same principle manifests in this domain]
- **[FILL: Domain 2]:** [FILL: how the same principle manifests in this domain]
- **[FILL: Domain 3]:** [FILL: how the same principle manifests in this domain]

---

### 💡 The Surprising Truth

[FILL: exactly ONE counterintuitive or perspective-shifting fact. Must be 2-4 sentences. Must be specific and factually accurate. Must reveal something the reader would NOT naturally arrive at.]

---

### 🧠 Think About This Before We Continue

**Q1 ([FILL: E|A|B|C|D|F] - [FILL: type label]):** [FILL: question — must NOT be answerable from this entry alone]
*Hint:* [FILL: WHERE to look, not the answer — point to a specific concept, system, or mechanism to investigate]

**Q2 ([FILL: different type from Q1]):** [FILL: question]
*Hint:* [FILL: where to look]

**Q3 ([FILL: different type from Q1 and Q2]):** [FILL: question]
*Hint:* [FILL: where to look]
"""


# ── Main ──────────────────────────────────────────────────────────────────

def scaffold_entry(code: str, nnn_int: int, cat: dict) -> tuple[str, bool]:
    """Scaffold one entry. Returns (filename, was_existing)."""
    nnn     = f"{nnn_int:03d}"
    id_str  = f"{code}-{nnn}"
    tier    = cat["tier"]
    folder  = cat["folder"]
    cat_dir = DICT_BASE / tier / folder

    if not cat_dir.exists():
        print(f"  ERROR: folder not found: {cat_dir}")
        return "", False

    # Read existing file if present
    existing = find_file(cat_dir, code, nnn)
    fm = {}
    title = ""
    filename = f"{id_str} - KEYWORD.md"

    if existing:
        fm = read_frontmatter(existing)
        title = fm.get("title", "").strip().strip('"\'') or existing.stem.split(" - ", 1)[-1]
        filename = existing.name
        was_existing = True
    else:
        title = f"KEYWORD {nnn}"
        filename = f"{id_str} - {title}.md"
        was_existing = False

    out_path = cat_dir / filename
    content  = build_scaffold(code, nnn, cat, fm, title, filename)

    out_path.write_text(content, encoding="utf-8")
    lines = content.count("\n") + 1
    fill_count = content.count("[FILL")

    status = "updated" if was_existing else "created"
    print(f"  {id_str}  {filename}")
    print(f"    -> {status}: {lines} lines, {fill_count} [FILL] stubs to complete")

    return filename, was_existing


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    code = sys.argv[1].upper()
    try:
        start = int(sys.argv[2])
        end   = int(sys.argv[3]) if len(sys.argv) > 3 else start
    except ValueError:
        print(f"ERROR: START and END must be integers (e.g. 061 or 61)")
        sys.exit(1)

    if code not in CATEGORIES:
        print(f"ERROR: Unknown category '{code}'. Valid: {', '.join(sorted(CATEGORIES))}")
        sys.exit(1)

    cat = CATEGORIES[code]
    print(f"\nScaffolding {code} ({cat['name']}) entries {start:03d}–{end:03d}")
    print(f"Target: dictionary/{cat['tier']}/{cat['folder']}/\n")

    scaffolded = []
    for n in range(start, end + 1):
        fname, existed = scaffold_entry(code, n, cat)
        if fname:
            scaffolded.append((f"{code}-{n:03d}", fname, existed))
        print()

    print(f"{'='*60}")
    print(f"Scaffolded {len(scaffolded)} file(s). Next steps:\n")
    print("1. For each file, replace ALL [FILL:...] stubs with")
    print("   actual v3.0 content (see copilot-instructions.md spec).")
    print()
    print("2. Key stubs to fill (in order):")
    print("   - TL;DR (section 5.2)")
    print("   - The Problem This Solves (section 5.4) — 4 sub-parts")
    print("   - Textbook Definition (5.5)")
    print("   - First Principles invariants (5.7)")
    print("   - Thought Experiment (5.8)")
    print("   - Mental Model / Analogy (5.9)")
    print("   - Four Levels (5.10) + Expert Cues")
    print("   - How It Works + flow diagram (5.11, 5.12)")
    print("   - Code Example BAD/GOOD (5.13)")
    print("   - Comparison Table (5.14)")
    print("   - 4+ Misconceptions (5.16)")
    print("   - 3+ Failure Modes incl. 1 security (5.17)")
    print("   - Related Keywords CODE-NNN IDs (5.18)")
    print("   - Quick Reference Card (5.19)")
    print("   - Transferable Wisdom + 3 examples (5.20)")
    print("   - The Surprising Truth (5.21)")
    print("   - 3 Think questions with Hints (5.22)")
    print()
    print("3. Verify compliance:")
    print(f"   python tmp/check_all_categories.py -c {code} --v3-only")
    print()
    print("4. Commit:")
    ids = " ".join(s[0] for s in scaffolded)
    first_id = scaffolded[0][0] if scaffolded else "?"
    last_id  = scaffolded[-1][0] if scaffolded else "?"
    print(f"   git add dictionary/{cat['tier']}/{cat['folder']}/")
    print(f'   git commit -m "upgrade: ->v3.0 {first_id}-{last_id} {cat["name"]}"')


if __name__ == "__main__":
    main()
