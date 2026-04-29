##############################################################################
#  New-DictionaryEntry.ps1
#  Scaffolds a new dictionary entry from _entry-template.md
#
#  Usage:
#    .\New-DictionaryEntry.ps1 -Number 016 -Name "GC Roots" -Category "Java"
#    .\New-DictionaryEntry.ps1 -Number 139 -Name "CAP Theorem" -Category "DistributedSystems"
#
#  Category aliases (case-insensitive, partial match):
#    Java | Spring | DistributedSystems | Databases | Messaging |
#    Networking | OS | SystemDesign | DSA | SoftwareDesign |
#    Cloud | DevOps | Testing
##############################################################################

param(
    [Parameter(Mandatory)][string]$Number,
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$Category
)

# Star chars for difficulty rating
$star  = [char]0x2605  # ★
$ostar = [char]0x2606  # ☆

# ── Category metadata ─────────────────────────────────────────────────────────
$meta = [ordered]@{
    "Java"               = @{ Dir = "Java";                   Parent = "Java Fundamentals"           }
    "Spring"             = @{ Dir = "Spring";                 Parent = "Spring & Spring Boot"         }
    "DistributedSystems" = @{ Dir = "Distributed Systems";    Parent = "Distributed Systems"          }
    "Databases"          = @{ Dir = "Databases";              Parent = "Databases"                    }
    "Messaging"          = @{ Dir = "Messaging & Streaming";  Parent = "Messaging & Streaming"        }
    "Networking"         = @{ Dir = "Networking & HTTP";      Parent = "Networking & HTTP"            }
    "OS"                 = @{ Dir = "OS & Systems";           Parent = "OS & Systems"                 }
    "SystemDesign"       = @{ Dir = "System Design";          Parent = "System Design"                }
    "DSA"                = @{ Dir = "DSA";                    Parent = "Data Structures & Algorithms" }
    "SoftwareDesign"     = @{ Dir = "Software Design";        Parent = "Software Design"              }
    "Cloud"              = @{ Dir = "Cloud & Infrastructure"; Parent = "Cloud & Infrastructure"       }
    "DevOps"             = @{ Dir = "DevOps & SDLC";          Parent = "DevOps & SDLC"                }
    "Testing"            = @{ Dir = "Testing";                Parent = "Testing & Clean Code"         }
}

# Default difficulty per category
$difficultyMap = @{
    "Java"               = "$star$star$ostar"
    "Spring"             = "$star$star$ostar"
    "DistributedSystems" = "$star$star$star"
    "Databases"          = "$star$star$ostar"
    "Messaging"          = "$star$star$ostar"
    "Networking"         = "$star$star$ostar"
    "OS"                 = "$star$star$star"
    "SystemDesign"       = "$star$star$star"
    "DSA"                = "$star$star$ostar"
    "SoftwareDesign"     = "$star$ostar$ostar"
    "Cloud"              = "$star$star$ostar"
    "DevOps"             = "$star$ostar$ostar"
    "Testing"            = "$star$ostar$ostar"
}

# Normalize category input — exact match first, then partial
$categoryNorm = $Category -replace "\s", ""
$key = $null
foreach ($k in $meta.Keys) {
    if ($k -ieq $categoryNorm) { $key = $k; break }
}
if (-not $key) {
    foreach ($k in $meta.Keys) {
        if ($k -ilike "*$categoryNorm*" -or $categoryNorm -ilike "*$k*") { $key = $k; break }
    }
}
if (-not $key) {
    Write-Error "Unknown category '$Category'. Valid: $($meta.Keys -join ' | ')"
    exit 1
}

$dir        = $meta[$key].Dir
$parent     = $meta[$key].Parent
$difficulty = $difficultyMap[$key]
$num        = $Number.PadLeft(3, '0')
$emDash     = [char]0x2014   # —

# ── Paths ─────────────────────────────────────────────────────────────────────
$docsRoot     = Join-Path $PSScriptRoot "docs"
$targetDir    = Join-Path $docsRoot $dir
$fileName     = "$num $emDash $Name.md"
$filePath     = Join-Path $targetDir $fileName
$templatePath = Join-Path $PSScriptRoot "_entry-template.md"

if (-not (Test-Path $templatePath)) {
    Write-Error "Template not found: $templatePath"
    exit 1
}
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Write-Host "Created directory: $targetDir" -ForegroundColor Cyan
}
if (Test-Path $filePath) {
    Write-Warning "File already exists: $filePath"
    $overwrite = Read-Host "Overwrite? (y/N)"
    if ($overwrite -ne 'y') { exit 0 }
}

# Build a default tag list from category key + number
$categoryTag = "#$($key.ToLower())"
$defaultTags = "$categoryTag, #$num, #TODO_more_tags"

# Read template, replace placeholders, write output
$content = Get-Content -Path $templatePath -Raw -Encoding UTF8
$content = $content -replace 'TEMPLATE_NUM',        $num
$content = $content -replace 'TEMPLATE_NAME',       $Name
$content = $content -replace 'TEMPLATE_CATEGORY',   $parent
$content = $content -replace 'TEMPLATE_DIFFICULTY', $difficulty
$content = $content -replace '#TODO_tag1, #TODO_tag2, #TODO_tag3', $defaultTags
$content = $content -replace '#TODO_tag1, #TODO_tag2',             $defaultTags

$content | Set-Content -Path $filePath -Encoding UTF8

Write-Host ""
Write-Host "Created: $fileName" -ForegroundColor Green
Write-Host "  Path:  $filePath" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Fill all TODO sections in the file"
Write-Host "  2. .\Update-MarkdownFrontmatter.ps1"
Write-Host "  3. git add docs/ && git commit -m 'Add $num $emDash $Name' && git push"
Write-Host ""
