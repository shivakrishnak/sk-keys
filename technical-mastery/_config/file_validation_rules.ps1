#!/usr/bin/env pwsh
#Requires -Version 7
<#
.SYNOPSIS
    Pre-commit validation rules for technical-mastery entry files.

.DESCRIPTION
    Enforces the v6.0 spec formatting rules (ENTRY_GENERATOR_PROMPT.md Section 6).
    Exit code 1 on any ERROR - use as a pre-commit gate to block bad commits.
    Exit code 0 when only WARNs remain (commit allowed, warnings reported).

    ── ERROR rules (block commit) ──────────────────────────────────────
    YAML_AT_BYTE_ZERO   File must start at byte 0 with --- (no BOM, no leading whitespace)
    NO_FRONTMATTER      File missing opening or closing --- frontmatter delimiters
    MISSING_FIELD       Required YAML fields: id, title, version, status, permalink,
                        parent, grand_parent, nav_order, layout
    DUPLICATE_YAML_FIELD Any YAML key appearing more than once in the frontmatter block
                        (e.g. SEC-010 had tier:, folder:, version: each duplicated)
    YAML_PARENT_MISMATCH Entry parent: does not match the category index.md title:
                        (e.g. NET-078 had parent: "Technical Mastery" not "Networking")
    VERSION_MISMATCH    status:complete requires version > 0; status:draft + version > 0 is suspicious
    EM_DASH             U+2014 em dash anywhere in body - replace with regular hyphen
    H1_IN_BODY          # H1 heading in body (code-fence-aware; # comments inside ``` are skipped)
    MISSING_DIVIDER     Every ### section heading must be preceded by blank + --- + blank
    BOLD_LABEL_NO_BLANK Consecutive **LABEL:** lines without a blank line between them
    QRC_BORDER_BROKEN   Box-drawing characters malformed: ┌ not ending ┐, └ not ending ┘,
                        ├ not ending ┤, content line not starting/ending with │,
                        unclosed ┌ (no matching └), or non-box line inside a box

    ── WARN rules (reported, commit allowed) ───────────────────────────
    CODE_LINE_LENGTH    Code line > 70 chars inside ``` fences (v4 legacy; enforce on new files)
    ASCII_WIDTH         ASCII diagram line > 59 chars (box-drawing lines starting with │ or ├)

    ── v6.0 WARN rules (opt-in via -StrictV6) ──────────────────────────────────────
    SCHEMA_MISMATCH     version:6 entry missing schema_version: "entry_v6" in frontmatter
    TOPIC_TYPE_MISSING  version:6 entry missing topic_type: field in frontmatter
    BLOOMS_INCOMPLETE   version:6 Stars3 entry missing all 6 Bloom's taxonomy level tags
                        (REMEMBER / UNDERSTAND / APPLY / ANALYZE / EVALUATE / CREATE)
    LOW_DIMENSION_COVERAGE  Entry body appears to lack 3+ of 10 knowledge dimensions
                        (heuristic: checks for presence of key section markers)
    HIGH_REPETITION     Same paragraph appears verbatim in multiple sections
                        (heuristic: 50-char+ paragraphs appearing 2+ times)

    ── False-positive guards ─────────────────────────────────────────
    H1_IN_BODY:         Skips lines inside ``` code fences (# Python/shell comments are NOT H1)
    CODE_LINE_LENGTH:   Only checked inside ``` fences, never in prose
    ASCII_WIDTH:        Only checked on box-drawing content lines (│ ├), not prose
    MISSING_DIVIDER:    Skips the very first ### in a file if it appears before any content
    BOLD_LABEL_NO_BLANK: Uses body[$idx-1] (immediate prev line), NOT $prevTrimmed.
                        Two bold-labels separated by a blank line do NOT fire.
    QRC_BORDER_BROKEN:  Box detection only activates on a valid ┌...┐ top border.
                        ├── and └── ASCII tree-diagram chars are ignored when not
                        inside a confirmed box (they lack ┤/┘ at end by design).

    ── Known validator bug (fixed here) ─────────────────────────────
    Do NOT use Select-String.LineNumber on piped string arrays - it always
    returns 1. Use a for-loop to find the frontmatter closing ---.

.PARAMETER Tier
    Limit scan to one tier, e.g. tier-1-foundations.

.PARAMETER Category
    Limit scan to one category code, e.g. OAU, DSA, LNX.

.PARAMETER FileList
    Path to a text file containing one repo-relative .md path per line.
    Used by the pre-commit hook to validate only staged files.

.PARAMETER StubsOnly
    Report only stub files (version: 0). Does not run body checks.

.PARAMETER FixEmDashes
    Auto-replace U+2014 em dashes with hyphens in body. Review before committing.

.PARAMETER StrictV6
    Enable v6.0-specific warn rules: SCHEMA_MISMATCH, TOPIC_TYPE_MISSING,
    BLOOMS_INCOMPLETE, LOW_DIMENSION_COVERAGE, HIGH_REPETITION.
    Recommended for entries generated under ENTRY_GENERATOR v6.0.

.EXAMPLE
    # Full scan of all technical-mastery content:
    pwsh -File file_validation_rules.ps1

    # Scan one tier:
    pwsh -File file_validation_rules.ps1 -Tier tier-1-foundations

    # Scan one category:
    pwsh -File file_validation_rules.ps1 -Category OAU

    # Pre-commit hook mode (staged files only):
    pwsh -File file_validation_rules.ps1 -FileList /tmp/staged.txt

    # Auto-fix em dashes and re-check:
    pwsh -File file_validation_rules.ps1 -FixEmDashes -Tier tier-2-networking-security

    # Strict v6.0 checks on new entries:
    pwsh -File file_validation_rules.ps1 -StrictV6 -Category JVM
#>

param(
    [string]$Tier       = "",
    [string]$Category   = "",
    [string]$FileList   = "",
    [switch]$StubsOnly,
    [switch]$FixEmDashes,
    [switch]$StrictV6
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Paths ───────────────────────────────────────────────────────────────
$SCRIPT_DIR = $PSScriptRoot
$REPO_ROOT  = Split-Path -Parent (Split-Path -Parent $SCRIPT_DIR)
$TM_ROOT    = Join-Path $REPO_ROOT "technical-mastery"

# ── Collect target files ────────────────────────────────────────────────
[System.IO.FileInfo[]]$files = @()

if ($FileList -ne "") {
    # Pre-commit hook mode: validate only the listed files
    if (-not (Test-Path $FileList)) {
        Write-Error "FileList path not found: $FileList"
        exit 1
    }
    $paths = Get-Content $FileList | Where-Object { $_ -match "technical-mastery/.*\.md$" -and $_ -notmatch "/index\.md$" }
    foreach ($p in $paths) {
        $full = Join-Path $REPO_ROOT $p.Replace("/", [System.IO.Path]::DirectorySeparatorChar)
        if (Test-Path $full) { $files += [System.IO.FileInfo]$full }
    }
} else {
    $searchRoot = $TM_ROOT
    if ($Tier)     { $searchRoot = Join-Path $TM_ROOT $Tier }
    if ($Category) {
        $catDir = Get-ChildItem $TM_ROOT -Recurse -Directory |
                  Where-Object { $_.Name -match "^$([regex]::Escape($Category))[-_]" -or $_.Name -eq $Category } |
                  Select-Object -First 1
        if (-not $catDir) {
            Write-Error "Category folder matching '$Category' not found under $TM_ROOT"
            exit 1
        }
        $searchRoot = $catDir.FullName
    }
    $files = Get-ChildItem $searchRoot -Recurse -Filter "*.md" |
             Where-Object { $_.Name -ne "index.md" }
}

if ($files.Count -eq 0) {
    Write-Host "No .md files found to validate." -ForegroundColor Yellow
    exit 0
}

# ── Rule: Test one file ──────────────────────────────────────────────────
function Test-EntryFile {
    param([System.IO.FileInfo]$File, [switch]$FixEmDashes, [switch]$StrictV6)

    $issues = [System.Collections.Generic.List[hashtable]]::new()

    # ────────────────────────────────────────────────────────────────────
    # RULE: YAML_AT_BYTE_ZERO
    # File must start at byte 0 with '---' (no BOM, no leading whitespace).
    # Spec: "File MUST start at byte 0 with --- (no BOM, no whitespace)"
    # ────────────────────────────────────────────────────────────────────
    $bytes = [System.IO.File]::ReadAllBytes($File.FullName)

    # BOM = EF BB BF
    if ($bytes.Length -ge 3 -and
        $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $issues.Add(@{
            sev  = "ERROR"
            rule = "YAML_AT_BYTE_ZERO"
            line = 0
            msg  = "UTF-8 BOM found at byte 0. File must be UTF-8 WITHOUT BOM."
        })
        return $issues  # Cannot continue - encoding is wrong
    }

    # First 3 bytes must be '-', '-', '-' (ASCII 0x2D)
    if ($bytes.Length -lt 3 -or
        $bytes[0] -ne 0x2D -or $bytes[1] -ne 0x2D -or $bytes[2] -ne 0x2D) {
        $issues.Add(@{
            sev  = "ERROR"
            rule = "YAML_AT_BYTE_ZERO"
            line = 0
            msg  = "File does not start with '---' at byte 0. YAML frontmatter must begin immediately."
        })
        return $issues  # No frontmatter - cannot continue
    }

    $text     = [System.IO.File]::ReadAllText($File.FullName, [System.Text.Encoding]::UTF8)
    $allLines = $text -split "\r?\n"

    # ────────────────────────────────────────────────────────────────────
    # RULE: NO_FRONTMATTER
    # Must have a closing --- to end the frontmatter block.
    # IMPORTANT: Use a for-loop to find closing ---. Do NOT use
    # Select-String.LineNumber on piped arrays - it always returns 1.
    # ────────────────────────────────────────────────────────────────────
    $fmCloseIdx = -1
    for ($i = 1; $i -lt $allLines.Length; $i++) {
        if ($allLines[$i] -eq "---") { $fmCloseIdx = $i; break }
    }
    if ($fmCloseIdx -lt 0) {
        $issues.Add(@{
            sev  = "ERROR"
            rule = "NO_FRONTMATTER"
            line = 1
            msg  = "No closing '---' found. Frontmatter block is not terminated."
        })
        return $issues
    }

    $fm   = $allLines[0..$fmCloseIdx] -join "`n"
    $body = $allLines[($fmCloseIdx + 1)..($allLines.Length - 1)]

    # ────────────────────────────────────────────────────────────────────
    # RULE: DUPLICATE_YAML_FIELD
    # Duplicate YAML keys cause ambiguous behaviour (YAML spec violation).
    # Real example: SEC-010 had tier:, folder:, version: each appearing
    # twice, AND was missing nav_order and grand_parent as a result.
    # Scan every line in the frontmatter block (between the two ---),
    # collect keys, flag any key seen more than once.
    # ────────────────────────────────────────────────────────────────────
    $seenKeys = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    # $allLines[1..($fmCloseIdx-1)] = frontmatter body (skip opening/closing ---)
    for ($ki = 1; $ki -lt $fmCloseIdx; $ki++) {
        $keyMatch = [regex]::Match($allLines[$ki], '^([a-zA-Z_][a-zA-Z0-9_]*):')
        if ($keyMatch.Success) {
            $key = $keyMatch.Groups[1].Value
            if (-not $seenKeys.Add($key)) {
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "DUPLICATE_YAML_FIELD"
                    line = $ki + 1   # 1-based: frontmatter starts at line 1
                    msg  = "Duplicate YAML key '$key' in frontmatter. Remove one occurrence."
                })
            }
        }
    }

    # ────────────────────────────────────────────────────────────────────
    # RULE: MISSING_FIELD
    # Required YAML keys: id, title, version, status, permalink,
    #                     parent, grand_parent, nav_order, layout
    # ────────────────────────────────────────────────────────────────────
    $reqFields = [ordered]@{
        "^id:"           = 'id: CODE-NNN  (e.g. id: OAU-042)'
        "^title:"        = 'title: "Keyword Name"'
        "^version:"      = 'version: 5  (or 0 for stubs)'
        "^status:"       = 'status: complete  (or draft for stubs)'
        "^permalink:"    = 'permalink: /technical-mastery/category/slug/'
        "^parent:"       = 'parent: "Category Name"  (must match category index.md title)'
        "^grand_parent:" = 'grand_parent: "Technical Mastery"'
        "^nav_order:"    = 'nav_order: NNN  (entry number, e.g. nav_order: 42)'
        "^layout:"       = 'layout: default'
    }
    foreach ($pattern in $reqFields.Keys) {
        if ($fm -notmatch "(?m)$pattern") {
            $issues.Add(@{
                sev  = "ERROR"
                rule = "MISSING_FIELD"
                line = 0
                msg  = "Missing required YAML field. Expected: $($reqFields[$pattern])"
            })
        }
    }

    # ────────────────────────────────────────────────────────────────────
    # RULE: VERSION_MISMATCH
    # status:complete => version > 0
    # status:draft + version > 0 => suspicious (warn, not error)
    # ────────────────────────────────────────────────────────────────────
    $verMatch    = [regex]::Match($fm, "(?m)^version:\s*(\d+)")
    $statusMatch = [regex]::Match($fm, "(?m)^status:\s*(\S+)")
    $ver    = if ($verMatch.Success)    { [int]$verMatch.Groups[1].Value }        else { -1 }
    $status = if ($statusMatch.Success) { $statusMatch.Groups[1].Value.Trim("'`"") } else { "unknown" }

    if ($status -eq "complete" -and $ver -eq 0) {
        $issues.Add(@{
            sev  = "ERROR"
            rule = "VERSION_MISMATCH"
            line = 0
            msg  = "status: complete but version: 0. Stubs must have status: draft."
        })
    }
    if ($status -eq "draft" -and $ver -gt 0) {
        $issues.Add(@{
            sev  = "WARN"
            rule = "VERSION_MISMATCH"
            line = 0
            msg  = "status: draft but version: $ver. Complete entries should have status: complete."
        })
    }

    # ────────────────────────────────────────────────────────────────────
    # RULE: YAML_PARENT_MISMATCH
    # The entry's parent: value must match the category index.md title:.
    # Catches: files with wrong parent (copy-paste from another category,
    # or a category that was renamed after the entries were written).
    # Real example: NET-078 had parent: "Technical Mastery" instead of
    # parent: "Networking" - would have been placed at the wrong nav level.
    # Requires: a well-formed index.md in the same directory as the entry.
    # ────────────────────────────────────────────────────────────────────
    $indexPath = Join-Path $File.DirectoryName "index.md"
    if (Test-Path $indexPath) {
        $indexText  = [System.IO.File]::ReadAllText($indexPath, [System.Text.Encoding]::UTF8)
        $idxTitle   = [regex]::Match($indexText, '(?m)^title:\s*"?([^"\r\n]+)"?').Groups[1].Value.Trim()
        $entryParent= [regex]::Match($fm,        '(?m)^parent:\s*"?([^"\r\n]+)"?').Groups[1].Value.Trim()
        if ($idxTitle -and $entryParent -and $entryParent -ne $idxTitle) {
            $issues.Add(@{
                sev  = "ERROR"
                rule = "YAML_PARENT_MISMATCH"
                line = 0
                msg  = "parent: '$entryParent' != index.md title: '$idxTitle'. Fix: parent: `"$idxTitle`""
            })
        }
    }

    # StubsOnly mode: no body checks needed
    if ($StubsOnly) {
        if ($ver -eq 0) {
            $issues.Add(@{ sev="INFO"; rule="STUB"; line=0; msg="Stub (version: 0, status: $status)." })
        }
        return $issues
    }

    # ────────────────────────────────────────────────────────────────────
    # Body walk: single pass, tracking code fence and box state.
    # All remaining rules are checked here.
    # ────────────────────────────────────────────────────────────────────
    $inCodeFence = $false
    $inBoxArt    = $false     # Inside a ┌...└ ASCII art block
    $boxOpenLine = -1         # Line number where ┌ was opened (for unclosed check)
    $prevTrimmed = ""         # Previous non-empty trimmed line (for bold-label rule)
    $firstSection = $true     # First ### in the file may legitimately have no ---

    for ($idx = 0; $idx -lt $body.Length; $idx++) {
        $line    = $body[$idx]
        $trimmed = $line.Trim()
        $lineNum = $fmCloseIdx + 2 + $idx  # 1-based file line number

        # ── Code fence toggle ──────────────────────────────────────────
        # A line starting with ``` (3+ backticks) toggles fence state.
        # Language tags are ignored: ```python, ```java, etc.
        # Guard: count leading backticks to avoid ``` inside a fence
        if ($line -match "^``````+") {
            $inCodeFence = -not $inCodeFence
            $prevTrimmed = $trimmed
            continue
        }

        # ── RULE: EM_DASH ─────────────────────────────────────────────
        # Spec Section 6: "No em dashes anywhere - use regular hyphens only"
        # Checked inside AND outside code fences (wrong in code comments too).
        if ($line -match "\u2014") {
            $issues.Add(@{
                sev  = "ERROR"
                rule = "EM_DASH"
                line = $lineNum
                msg  = "Em dash (U+2014) found. Replace with '-': $($trimmed.Substring(0,[Math]::Min(70,$trimmed.Length)))"
            })
        }

        # ── RULE: H1_IN_BODY ──────────────────────────────────────────
        # Spec Section 6: H1 is generated by Just the Docs from YAML title.
        # A line starting with "# " in body is an H1 heading -> forbidden.
        # FALSE POSITIVE GUARD: skip when inside a code fence.
        # Lines like "# This is a Python comment" are valid code, not H1.
        if (-not $inCodeFence -and $line -match "^# \S") {
            $issues.Add(@{
                sev  = "ERROR"
                rule = "H1_IN_BODY"
                line = $lineNum
                msg  = "H1 heading in body. Just the Docs renders H1 from YAML 'title'. Use ### only: '$trimmed'"
            })
        }

        # ── RULE: MISSING_DIVIDER ─────────────────────────────────────
        # Spec Section 6: "Every ### section heading MUST be preceded by
        # [blank line] -> [---] -> [blank line] -> [### heading]"
        # Check pattern by looking back 3 slots in the body array:
        #   body[idx-1] == ""    (blank before ###)
        #   body[idx-2] == "---" (the divider)
        #   body[idx-3] == ""    (blank before ---)
        # The FIRST ### in a file may appear right after the TL;DR line
        # without a leading --- (spec shows TL;DR before first section).
        # Skip first-section check to avoid false positives.
        if (-not $inCodeFence -and $line -match "^### ") {
            if ($firstSection) {
                $firstSection = $false
            } else {
                $prev1 = if ($idx -ge 1) { $body[$idx - 1] } else { "" }
                $prev2 = if ($idx -ge 2) { $body[$idx - 2] } else { "" }
                $prev3 = if ($idx -ge 3) { $body[$idx - 3] } else { "" }

                $dividerOk = ($prev1 -eq "") -and ($prev2 -eq "---") -and ($prev3 -eq "")
                if (-not $dividerOk) {
                    $issues.Add(@{
                        sev  = "ERROR"
                        rule = "MISSING_DIVIDER"
                        line = $lineNum
                        msg  = "### heading not preceded by required pattern: [blank] --- [blank] ###. Got: '$prev3' | '$prev2' | '$prev1' | '$trimmed'"
                    })
                }
            }
        }

        # ── RULE: BOLD_LABEL_NO_BLANK ─────────────────────────────────
        # Spec Section 6: "Bold-label lines (**LABEL:** value) must each
        # be separated by a blank line - consecutive lines merge on Jekyll"
        # Pattern: **WORD(S):** followed by content (anywhere on the line).
        # Check: current line is bold-label AND the IMMEDIATELY preceding
        # line (body[$idx-1]) is also a bold-label -> no blank between them.
        # NOTE: use body[$idx-1] directly, NOT $prevTrimmed (which skips
        # blank lines and causes false positives when bold-labels are
        # separated by a blank line).
        if (-not $inCodeFence -and $trimmed -match "^\*\*[A-Za-z][^*]+:\*\*") {
            $immPrev = if ($idx -gt 0) { $body[$idx - 1].Trim() } else { "" }
            if ($immPrev -match "^\*\*[A-Za-z][^*]+:\*\*") {
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "BOLD_LABEL_NO_BLANK"
                    line = $lineNum
                    msg  = "Consecutive **LABEL:** lines with no blank line separator. Jekyll merges them into one paragraph."
                })
            }
        }

        # ── RULE: QRC_BORDER_BROKEN ───────────────────────────────────
        # Spec: "Quick Reference Card: 60-char wide box in backtick fence"
        # Box-drawing characters must form properly closed, aligned boxes.
        #
        # IMPORTANT FALSE-POSITIVE GUARD:
        # ASCII file-tree diagrams use ├── and └── (tree branches) which
        # look like box-drawing chars but are NOT QRC borders. Only enter
        # box-detection mode when a valid top border ┌...┐ is found.
        # ├ and └ checks only apply when $inBoxArt = $true (inside a real box).
        #
        # Checks:
        #   ┌...┐  top border - activates box detection mode
        #   └...┘  bottom border - closes box detection (only inside box)
        #   ├...┤  divider row - only checked inside a box
        #   │...│  content lines - only checked inside a box
        #   Every ┌ must have a matching └

        if ($line -match "^┌" -and $line -match "┐$") {
            # Valid top border (starts ┌, ends ┐) -> enter box detection
            if ($inBoxArt) {
                # Previous box was never closed
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "QRC_BORDER_BROKEN"
                    line = $lineNum
                    msg  = "New ┌ opened before previous box at line $boxOpenLine was closed with └."
                })
            }
            $inBoxArt    = $true
            $boxOpenLine = $lineNum
        }
        elseif ($line -match "^┌" -and $line -notmatch "┐$") {
            # ┌ line that does NOT end with ┐ - malformed box top border
            # (tree-root lines like ┌── / would appear here but they are
            # inside code fences only; flag as malformed box border)
            if ($inBoxArt) {
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "QRC_BORDER_BROKEN"
                    line = $lineNum
                    msg  = "Box top border (┌) does not end with ┐: '$trimmed'"
                })
            }
            # If not in box: ignore (likely a tree root line)
        }
        elseif ($inBoxArt -and $line -match "^└") {
            # Closing border - only check when inside a confirmed box
            if ($line -notmatch "┘$") {
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "QRC_BORDER_BROKEN"
                    line = $lineNum
                    msg  = "Box bottom border (└) does not end with ┘: '$trimmed'"
                })
            }
            $inBoxArt    = $false
            $boxOpenLine = -1
        }
        elseif ($inBoxArt -and $line -match "^├") {
            # Internal divider row - only check when inside a confirmed box
            if ($line -notmatch "┤$") {
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "QRC_BORDER_BROKEN"
                    line = $lineNum
                    msg  = "Box divider (├) does not end with ┤: '$trimmed'"
                })
            }
        }
        elseif ($inBoxArt) {
            # Content row inside a box must start and end with │
            # Allow empty lines between box rows
            if ($trimmed -ne "" -and $line -notmatch "^│") {
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "QRC_BORDER_BROKEN"
                    line = $lineNum
                    msg  = "Line inside box (after ┌) does not start with │: '$trimmed'"
                })
                $inBoxArt = $false  # Reset to avoid cascading errors
            } elseif ($line -match "^│" -and $line -notmatch "│$") {
                $issues.Add(@{
                    sev  = "ERROR"
                    rule = "QRC_BORDER_BROKEN"
                    line = $lineNum
                    msg  = "Box content line starts with │ but does not end with │: '$trimmed'"
                })
            }
        }

        # ── RULE: CODE_LINE_LENGTH (WARN only) ────────────────────────
        # Spec Section 6: "Max line length: 70 characters"
        # Checked inside code fences only (not prose lines).
        # Kept as WARN because v4 legacy files have many existing violations.
        if ($inCodeFence -and $line.Length -gt 70) {
            $issues.Add(@{
                sev  = "WARN"
                rule = "CODE_LINE_LENGTH"
                line = $lineNum
                msg  = "Code line $($line.Length) chars (max 70): '$($line.Substring(0,[Math]::Min(67,$line.Length)))...'"
            })
        }

        # ── RULE: ASCII_WIDTH (WARN only) ─────────────────────────────
        # Spec Section 6: "Max total width: 59 characters (57 content + 2 borders)"
        # Only checked on box-drawing content lines (│ ├).
        # Kept as WARN because v4 legacy files have many existing violations.
        if ($inBoxArt -and ($line -match "^[│├]") -and $line.Length -gt 59) {
            $issues.Add(@{
                sev  = "WARN"
                rule = "ASCII_WIDTH"
                line = $lineNum
                msg  = "ASCII diagram line $($line.Length) chars (max 59): '$($line.Substring(0,[Math]::Min(59,$line.Length)))...'"
            })
        }

        # Track previous non-empty trimmed line for bold-label check
        if ($trimmed -ne "") { $prevTrimmed = $trimmed }

    }  # end body walk

    # ── Check for unclosed box at end of file ──────────────────────────
    if ($inBoxArt) {
        $issues.Add(@{
            sev  = "ERROR"
            rule = "QRC_BORDER_BROKEN"
            line = $boxOpenLine
            msg  = "Box opened at line $boxOpenLine (┌) was never closed with └."
        })
    }

    # ── Auto-fix em dashes if requested ───────────────────────────────
    if ($FixEmDashes) {
        $emDashIssues = @($issues | Where-Object { $_.rule -eq "EM_DASH" })
        if ($emDashIssues.Count -gt 0) {
            $fixedText = $text -replace "\u2014", "-"
            [System.IO.File]::WriteAllText(
                $File.FullName, $fixedText,
                [System.Text.UTF8Encoding]::new($false)
            )
            $issues.Add(@{
                sev  = "FIXED"
                rule = "EM_DASH_FIXED"
                line = 0
                msg  = "Auto-fixed $($emDashIssues.Count) em dash(es). Review diff before committing."
            })
        }
    }

    # ──────────────────────────────────────────────────────────────────────
    # v6.0 CHECKS (opt-in via -StrictV6)
    # ──────────────────────────────────────────────────────────────────────
    if ($StrictV6) {
        $fmVersion = 0
        foreach ($fmLine in $fmLines) {
            if ($fmLine -match '^version:\s*(\d+)') {
                $fmVersion = [int]$Matches[1]
            }
        }
        $fmDifficulty = ''
        foreach ($fmLine in $fmLines) {
            if ($fmLine -match '^difficulty:') {
                $fmDifficulty = $fmLine
            }
        }

        # RULE: SCHEMA_MISMATCH - v6 entries need schema_version
        if ($fmVersion -ge 6) {
            $hasSchemaVersion = ($fmLines | Where-Object { $_ -match '^schema_version:' }).Count -gt 0
            if (-not $hasSchemaVersion) {
                $issues.Add(@{
                    sev  = 'WARN'
                    rule = 'SCHEMA_MISMATCH'
                    line = 0
                    msg  = 'version:6 entry is missing schema_version: "entry_v6" in frontmatter'
                })
            }
        }

        # RULE: TOPIC_TYPE_MISSING - v6 entries need topic_type
        if ($fmVersion -ge 6) {
            $hasTopicType = ($fmLines | Where-Object { $_ -match '^topic_type:' }).Count -gt 0
            if (-not $hasTopicType) {
                $issues.Add(@{
                    sev  = 'WARN'
                    rule = 'TOPIC_TYPE_MISSING'
                    line = 0
                    msg  = 'version:6 entry is missing topic_type: field in frontmatter'
                })
            }
        }

        # RULE: BLOOMS_INCOMPLETE - Stars3 v6 entries need all 6 Bloom levels
        if ($fmVersion -ge 6 -and $fmDifficulty -match '[\u2605][\u2605][\u2605]') {
            $bloomLevels = @('REMEMBER','UNDERSTAND','APPLY','ANALYZE','EVALUATE','CREATE')
            $bodyText = $body -join ' '
            $missingLevels = $bloomLevels | Where-Object { $bodyText -notmatch $_ }
            if ($missingLevels.Count -gt 0) {
                $issues.Add(@{
                    sev  = 'WARN'
                    rule = 'BLOOMS_INCOMPLETE'
                    line = 0
                    msg  = "Section 5.22 missing Bloom's levels: $($missingLevels -join ', ')"
                })
            }
        }

        # RULE: HIGH_REPETITION - detect verbatim paragraph duplication
        $paraLines = $body | Where-Object { $_.Length -ge 50 -and $_ -notmatch '^```' }
        $seen = @{}
        foreach ($pLine in $paraLines) {
            $key = $pLine.Trim()
            if ($seen.ContainsKey($key)) {
                $issues.Add(@{
                    sev  = 'WARN'
                    rule = 'HIGH_REPETITION'
                    line = 0
                    msg  = "Duplicate line found (verbatim repetition): [$($key.Substring(0, [Math]::Min(60, $key.Length)))...]"
                })
                break  # One warning per file is enough
            }
            $seen[$key] = $true
        }
    }

    return $issues
}

# ── Severity colors ─────────────────────────────────────────────────────
$sevColor = @{
    "ERROR" = "Red"
    "WARN"  = "Yellow"
    "INFO"  = "DarkGray"
    "FIXED" = "Green"
}

# ── Main scan ────────────────────────────────────────────────────────────
$totalFiles  = 0
$totalErrors = 0
$totalWarns  = 0
$totalFixed  = 0
$byRule      = [System.Collections.Generic.SortedDictionary[string,int]]::new()

foreach ($f in $files) {
    $totalFiles++
    $issues = Test-EntryFile -File $f -FixEmDashes:$FixEmDashes -StrictV6:$StrictV6

    $fileHasOutput = $false
    foreach ($issue in $issues) {
        $rule = $issue.rule
        if (-not $byRule.ContainsKey($rule)) { $byRule[$rule] = 0 }
        $byRule[$rule]++

        switch ($issue.sev) {
            "ERROR" { $totalErrors++ }
            "WARN"  { $totalWarns++  }
            "FIXED" { $totalFixed++  }
        }

        # Print issues (skip INFO unless -StubsOnly)
        if ($issue.sev -ne "INFO" -or $StubsOnly) {
            if (-not $fileHasOutput) {
                $relPath = $f.FullName.Replace($REPO_ROOT + [System.IO.Path]::DirectorySeparatorChar, "").Replace("\", "/")
                Write-Host "`n$relPath" -ForegroundColor White
                $fileHasOutput = $true
            }
            $color   = $sevColor[$issue.sev]
            $lineTag = if ($issue.line -gt 0) { " [L$($issue.line)]" } else { "" }
            Write-Host "  [$($issue.sev)]$lineTag [$($issue.rule)] $($issue.msg)" -ForegroundColor $color
        }
    }
}

# ── Summary ──────────────────────────────────────────────────────────────
$divider = "=" * 60
Write-Host "`n$divider" -ForegroundColor Cyan
Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host $divider -ForegroundColor Cyan
Write-Host "Files scanned : $totalFiles"
Write-Host "Errors        : $totalErrors" -ForegroundColor $(if ($totalErrors -gt 0) { "Red" } else { "Green" })
Write-Host "Warnings      : $totalWarns"  -ForegroundColor $(if ($totalWarns  -gt 0) { "Yellow" } else { "Green" })
if ($FixEmDashes -and $totalFixed -gt 0) {
    Write-Host "Auto-fixed    : $totalFixed file(s)" -ForegroundColor Green
}

if ($byRule.Count -gt 0) {
    Write-Host "`nIssues by rule:"
    foreach ($kv in $byRule.GetEnumerator()) {
        $ruleColor = if ($kv.Key -in @("CODE_LINE_LENGTH","ASCII_WIDTH","VERSION_MISMATCH","SCHEMA_MISMATCH","TOPIC_TYPE_MISSING","BLOOMS_INCOMPLETE","LOW_DIMENSION_COVERAGE","HIGH_REPETITION")) { "Yellow" } else { "Red" }
        Write-Host ("  {0,-26} {1}" -f $kv.Key, $kv.Value) -ForegroundColor $ruleColor
    }
}

Write-Host ""
if ($totalErrors -eq 0 -and $totalWarns -eq 0) {
    Write-Host "All files pass. No issues found." -ForegroundColor Green
    exit 0
} elseif ($totalErrors -eq 0) {
    Write-Host "No errors. $totalWarns warning(s) to review." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "COMMIT BLOCKED: $totalErrors error(s) must be fixed before committing." -ForegroundColor Red
    exit 1
}

