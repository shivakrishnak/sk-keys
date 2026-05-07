$file = "c:\ASK\MyWorkspace\sk-keys\GENERATOR_PROMPT.md"
$enc  = [System.Text.UTF8Encoding]::new($false)
$c    = [System.IO.File]::ReadAllText($file, $enc)
$nl   = "`r`n"

Write-Host "Loaded $($c.Length) chars"

# ══════════════════════════════════════════════════════════════
# 1. Simple "How to Use" — single entry example
# ══════════════════════════════════════════════════════════════

$c = $c.Replace(
@"
Generate dictionary entry for keyword: Event Loop
Number: 1293
Category: JavaScript
Difficulty: ★★★

Follow the Technical Dictionary Generator prompt v2.1 exactly.
"@,
@"
Generate dictionary entry:
  ID:         JSC-NNN
  Keyword:    Event Loop
  Category:   JavaScript
  Tier:       tier-7-frontend
  Folder:     JSC-javascript
  Difficulty: ★★★

Follow Master Prompt v2.1 and ID System v3.0 exactly.
"@
)
Write-Host "1: single entry example done"

# ══════════════════════════════════════════════════════════════
# 2. Simple "How to Use" — batch example
# ══════════════════════════════════════════════════════════════

$c = $c.Replace(
@"
Generate dictionary entries for keywords 1291–1295:
- JavaScript Engine (V8) (1291)
- Call Stack (JS) (1292)
- Event Loop (1293)
- Task Queue (Macrotask) (1294)
- Microtask Queue (1295)

Follow the Technical Dictionary Generator prompt v2.1 exactly.
Generate each as a separate markdown file.
"@,
@"
Generate dictionary entries JSC-001 through JSC-005:

  JSC-001 | JavaScript Engine (V8) | ★★★
  JSC-002 | Call Stack (JS)         | ★☆☆
  JSC-003 | Event Loop              | ★★★
  JSC-004 | Task Queue (Macrotask)  | ★★☆
  JSC-005 | Microtask Queue         | ★★☆

Category:   JavaScript
Tier:       tier-7-frontend
Folder:     JSC-javascript

Follow Master Prompt v2.1 and ID System v3.0 exactly.
Generate each as a separate markdown file.
"@
)
Write-Host "2: batch example done"

# ══════════════════════════════════════════════════════════════
# 3. Simple "How to Use" — continue from last
# ══════════════════════════════════════════════════════════════

$c = $c.Replace(
@"
Continue dictionary generation from entry [NNNN].
Next batch: [KEYWORD 1] through [KEYWORD 5].
Follow the Technical Dictionary Generator prompt v2.1 exactly.
"@,
@"
Continue dictionary generation for category: [CODE]
Last generated: [CODE]-[NNN]
Next batch: [CODE]-[NNN] through [CODE]-[NNN]

Follow Master Prompt v2.1 and ID System v3.0 exactly.
"@
)
Write-Host "3: continue from last done"

# ══════════════════════════════════════════════════════════════
# 4. Step 1 batch workflow — Front matter rules block
# ══════════════════════════════════════════════════════════════

$c = $c.Replace(
@"
Front matter rules:
  - layout: default
  - title: "<Keyword Name>"
  - parent: "<Category Title>"         ← must match category folder's index.md title exactly
  - nav_order: <NNNN>                  ← the global keyword number (integer, 4-digit)
  - permalink: /<category-slug>/<keyword-slug>/
  - number: "<NNNN>"
  - category: <Category Title>
  - difficulty: ★☆☆ | ★★☆ | ★★★
  - depends_on: Keyword1, Keyword2
  - used_by: Keyword1, Keyword2
  - related: Keyword1, Keyword2
  - tags: #tag1, #tag2, #tag3
"@,
@"
Front matter rules:
  - id: <CODE>-<NNN>              ← category code + sequence, e.g. JSC-003
  - title: <Keyword Name>         ← exact name, no quotes
  - category: <Full Category Name>
  - tier: <tier-N-name>           ← from Section 2 registry
  - folder: <CODE-folder-name>    ← from Section 2 registry
  - difficulty: ★☆☆ | ★★☆ | ★★★
  - depends_on: CODE-NNN, CODE-NNN   ← full IDs, not keyword names
  - used_by: CODE-NNN, CODE-NNN
  - related: CODE-NNN, CODE-NNN
  - tags: #tag1, #tag2, #tag3     ← # prefixed, comma-separated
  - status: draft
  - version: 1
"@
)
Write-Host "4: batch workflow front matter done"

# ══════════════════════════════════════════════════════════════
# 5. Category-focused batch — Front matter block
# ══════════════════════════════════════════════════════════════

$c = $c.Replace(
@"
Front matter (use exact values for the chosen category):
  layout: default
  title: "<Keyword Name>"
  parent: "<Category Title>"         ← exact title from mapping table below
  nav_order: <NNNN>                  ← global keyword number (integer, 4-digit)
  permalink: /<category-slug>/<keyword-slug>/
  number: "<NNNN>"
  category: <Category Title>
  difficulty: ★☆☆ | ★★☆ | ★★★
  depends_on: Keyword1, Keyword2
  used_by: Keyword1, Keyword2
  related: Keyword1, Keyword2
  tags: #tag1, #tag2, #tag3
"@,
@"
Front matter (use exact values for the chosen category):
  id: <CODE>-<NNN>              ← category code + sequence, e.g. JVM-036
  title: <Keyword Name>         ← exact name, no quotes
  category: <Full Category Name>
  tier: <tier-N-name>           ← from Section 2 registry
  folder: <CODE-folder-name>    ← from Section 2 registry
  difficulty: ★☆☆ | ★★☆ | ★★★
  depends_on: CODE-NNN, CODE-NNN   ← full IDs, not keyword names
  used_by: CODE-NNN, CODE-NNN
  related: CODE-NNN, CODE-NNN
  tags: #tag1, #tag2, #tag3     ← # prefixed, comma-separated
  status: draft
  version: 1
"@
)
Write-Host "5: category-focused front matter done"

# ══════════════════════════════════════════════════════════════
# 6. Update "Follow v2.1 exactly" references in batch workflow
# ══════════════════════════════════════════════════════════════

$c = $c.Replace(
"Follow GENERATOR_PROMPT.md v2.1 spec exactly for every entry.",
"Follow GENERATOR_PROMPT.md v2.1 (content) and ID System v3.0 (IDs/files) exactly."
)

$c = $c.Replace(
"Follow GENERATOR_PROMPT.md v2.1 spec exactly.",
"Follow GENERATOR_PROMPT.md v2.1 (content) and ID System v3.0 (IDs/files) exactly."
)

$c = $c.Replace(
"Follow GENERATOR_PROMPT.md v2.1 (content rules) exactly.",
"Follow GENERATOR_PROMPT.md v2.1 (content) and ID System v3.0 (IDs/files) exactly."
)

Write-Host "6: v2.1 spec references updated"

# ══════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════

[System.IO.File]::WriteAllText($file, $c, $enc)
Write-Host "`n✅ ALL DONE. File saved. Length: $($c.Length)"

# ── Final validation ──────────────────────────────────────────
Write-Host "`n─── VALIDATION ───"
Write-Host "layout: default remaining: $(([regex]::Matches($c, 'layout: default')).Count)"
Write-Host "nav_order: NNNN remaining: $(([regex]::Matches($c, 'nav_order: NNNN')).Count)"
Write-Host "number: NNNN remaining:    $(([regex]::Matches($c, 'number: .NNNN.')).Count)"
Write-Host "Follow v2.1 + v3.0 refs:  $(([regex]::Matches($c, 'ID System v3\.0')).Count)"
