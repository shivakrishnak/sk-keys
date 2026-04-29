##############################################################################
#  New-DictionaryEntry.ps1
#  Scaffolds a new dictionary entry from the master template.
#
#  Usage:
#    .\New-DictionaryEntry.ps1 -Number 016 -Name "GC Roots" -Category "Java"
#    .\New-DictionaryEntry.ps1 -Number 103 -Name "IoC" -Category "Spring"
#    .\New-DictionaryEntry.ps1 -Number 139 -Name "CAP Theorem" -Category "Distributed Systems"
##############################################################################

param(
    [Parameter(Mandatory)][string]$Number,      # e.g. 016  or  139
    [Parameter(Mandatory)][string]$Name,        # e.g. "GC Roots"
    [Parameter(Mandatory)][string]$Category     # e.g. "Java", "Spring", "Databases" …
)

# ── Category metadata ────────────────────────────────────────────────────────
$meta = @{
    "Java"                  = @{ Emoji = "☕"; Dir = "Java";                    Parent = "Java Fundamentals" }
    "Spring"                = @{ Emoji = "🌱"; Dir = "Spring";                  Parent = "Spring & Spring Boot" }
    "Distributed Systems"   = @{ Emoji = "🔗"; Dir = "Distributed Systems";     Parent = "Distributed Systems" }
    "Databases"             = @{ Emoji = "💾"; Dir = "Databases";               Parent = "Databases" }
    "Messaging"             = @{ Emoji = "📨"; Dir = "Messaging & Streaming";   Parent = "Messaging & Streaming" }
    "Networking"            = @{ Emoji = "🌐"; Dir = "Networking & HTTP";       Parent = "Networking & HTTP" }
    "OS"                    = @{ Emoji = "🖥️"; Dir = "OS & Systems";            Parent = "OS & Systems" }
    "System Design"         = @{ Emoji = "🏗️"; Dir = "System Design";          Parent = "System Design" }
    "DSA"                   = @{ Emoji = "🔧"; Dir = "DSA";                     Parent = "Data Structures & Algorithms" }
    "Software Design"       = @{ Emoji = "🧩"; Dir = "Software Design";        Parent = "Software Design" }
    "Cloud"                 = @{ Emoji = "☁️"; Dir = "Cloud & Infrastructure"; Parent = "Cloud & Infrastructure" }
    "DevOps"                = @{ Emoji = "🔄"; Dir = "DevOps & SDLC";          Parent = "DevOps & SDLC" }
    "Testing"               = @{ Emoji = "🧪"; Dir = "Testing";                Parent = "Testing & Clean Code" }
}

# Normalize category input
$key = $Category
if (-not $meta.ContainsKey($key)) {
    # Try partial match
    $matched = $meta.Keys | Where-Object { $_ -like "*$Category*" } | Select-Object -First 1
    if ($matched) {
        $key = $matched
        Write-Host "🔍 Matched category '$Category' → '$key'" -ForegroundColor Cyan
    } else {
        Write-Error "❌ Unknown category '$Category'. Valid: $($meta.Keys -join ', ')"
        exit 1
    }
}

$emoji  = $meta[$key].Emoji
$dir    = $meta[$key].Dir
$parent = $meta[$key].Parent

# ── Pad number ────────────────────────────────────────────────────────────────
$num = $Number.PadLeft(3, '0')

# ── Build paths ──────────────────────────────────────────────────────────────
$docsRoot = Join-Path $PSScriptRoot "docs"
$targetDir = Join-Path $docsRoot $dir
$fileName  = "$emoji $num — $Name.md"
$filePath  = Join-Path $targetDir $fileName

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

if (Test-Path $filePath) {
    Write-Warning "⚠️  File already exists: $filePath"
    $overwrite = Read-Host "Overwrite? (y/N)"
    if ($overwrite -ne 'y') { exit 0 }
}

# ── Generate content ─────────────────────────────────────────────────────────
$content = @"
---
number: $num
category: $parent
difficulty: ★★☆
depends_on: TODO_Concept1, TODO_Concept2
used_by: TODO_Consumer1, TODO_Consumer2
tags: #TODO_tag1, #TODO_tag2
---

# $emoji $num — $Name

⚡ TL;DR — TODO: one sentence that captures the essence.

\`\`\`
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #$num        │ Category: $parent$(Get-Space -text $parent -width 36)│ Difficulty: ★★☆          │
├──────────────┼─────────────────────────────────────────────────────────────────┤
│ Depends on:  │ TODO_Concept1, TODO_Concept2                                    │
│ Used by:     │ TODO_Consumer1, TODO_Consumer2                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
\`\`\`

---

## 📘 Textbook Definition

> TODO: Formal, precise definition — as you would find it in a spec, RFC, or textbook.

---

## 🟢 Simple Definition (Easy)

> TODO: One short paragraph. Explain to a complete beginner or non-developer.

---

## 🔵 Simple Definition (Elaborated)

> TODO: 2-3 paragraphs. Explain to a mid-level developer.
> Include _what it does_, _how it's used_, and _why it matters_.

---

## 🔩 First Principles Explanation

> TODO: Start from zero. What problem existed first? What insight led to this solution?

\`\`\`
Problem → Insight → Solution
\`\`\`

---

## ❓ Why Does This Exist (Why Before What)

> TODO: What would the world look like WITHOUT this concept?
> What pain does it remove?

---

## 🧠 Mental Model / Analogy

> TODO: A real-world metaphor that makes this concept stick in memory.
> _"Think of $Name like a ..."_

---

## ⚙️ How It Works (Mechanism)

> TODO: Internal details. Data flow, algorithm, state machine, or architecture diagram.

\`\`\`
Step 1 → Step 2 → Step 3
            ↓
         Result
\`\`\`

---

## 🔄 How It Connects (Mini-Map)

> TODO: Show how this concept links to others in the same ecosystem.

\`\`\`
          [Concept A]
               ↓
[Concept B] → [$Name] → [Concept C]
               ↑
          [Concept D]
\`\`\`

---

## 💻 Code Example

> TODO: Minimal, runnable code that demonstrates the concept.

\`\`\`java
// TODO: Add code example
\`\`\`

---

## 🔁 Flow / Lifecycle (if applicable)

> TODO: If this concept involves steps or state changes, show the full flow.
> Remove this section if not applicable.

\`\`\`
1. [first event]
        ↓
2. [next step]
        ↓
3. [outcome]
\`\`\`

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| TODO misconception 1 | TODO correction 1 |
| TODO misconception 2 | TODO correction 2 |
| TODO misconception 3 | TODO correction 3 |

---

## 🔥 Pitfalls in Production

**Pitfall 1: TODO Name**
> TODO: What breaks and how to fix it.

**Pitfall 2: TODO Name**
> TODO: What breaks and how to fix it.

---

## 🔗 Related Keywords

- **[TODO Keyword A]** — one-line description of the relationship
- **[TODO Keyword B]** — one-line description of the relationship
- **[TODO Keyword C]** — one-line description of the relationship

---

## 📌 Quick Reference Card

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ TODO: one-line essence                       │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ TODO: when to apply this                    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ TODO: when NOT to use this                  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "TODO: memorable summary"                   │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ TODO: ConceptA → ConceptB → ConceptC        │
└─────────────────────────────────────────────────────────────┘
\`\`\`

---

## 🧠 Think About This Before We Continue

**Q1.** TODO: question 1
**Q2.** TODO: question 2
**Q3.** TODO: question 3
"@

# ── Helper: padding ──────────────────────────────────────────────────────────
function Get-Space {
    param([string]$text, [int]$width)
    $spaces = $width - $text.Length
    if ($spaces -lt 1) { return " " }
    return " " * $spaces
}

# ── Write file ──────────────────────────────────────────────────────────────
$content | Set-Content -Path $filePath -Encoding UTF8
Write-Host ""
Write-Host "✅ Created: $filePath" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open and fill all TODO sections in the file"
Write-Host "  2. Run: .\Update-MarkdownFrontmatter.ps1"
Write-Host "  3. Git: git add docs/ && git commit -m `"Add $num — $Name`" && git push"
Write-Host ""

