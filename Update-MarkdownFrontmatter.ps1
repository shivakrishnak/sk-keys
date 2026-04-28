# ============================================================
# GitHub Pages Auto-Frontmatter Generator
# Usage: .\Update-MarkdownFrontmatter.ps1 -SectionPath "docs\java" -ParentTitle "Java Fundamentals"
# SAFE: Uses .NET UTF-8 I/O - preserves all emojis and special characters
# ONLY replaces the top frontmatter block, body is written back unchanged
# ============================================================
param(
    [Parameter(Mandatory=$true)][string]$SectionPath,
    [Parameter(Mandatory=$true)][string]$ParentTitle,
    [Parameter(Mandatory=$false)][string]$BasePermalink = $null
)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
function Get-FileNumber { param([string]$Filename); if ($Filename -match "(\d{3})") { return [int]$matches[1] }; return $null }
function Get-TitleFromFilename {
    param([string]$Filename)
    $t = $Filename -replace "\.md$", ""
    $t = [regex]::Replace($t, "^[^\x00-\x7F]+\s*", "")
    $t = $t -replace "^\d{3}\s*[^\w\s]?\s*", ""
    return $t.Trim()
}
function New-Permalink {
    param([string]$Title, [string]$Section)
    $slug = $Title.ToLower() -replace "[^\w\s-]", "" -replace "\s+", "-" -replace "-+", "-"
    $slug = $slug.Trim("-")
    if ($Section) { return "/$Section/$slug/" }; return "/$slug/"
}
function Get-BodyContent {
    param([string]$FilePath)
    $raw = [System.IO.File]::ReadAllText($FilePath, (New-Object System.Text.UTF8Encoding $false))
    $lines = $raw -split "`r?`n"
    $i = 0; $total = $lines.Count
    while ($i -lt $total -and $lines[$i].Trim() -eq "") { $i++ }
    while ($i -lt $total -and $lines[$i].Trim() -eq "---") {
        $i++
        while ($i -lt $total -and $lines[$i].Trim() -ne "---") { $i++ }
        if ($i -lt $total) { $i++ }
        while ($i -lt $total -and $lines[$i].Trim() -eq "") { $i++ }
    }
    if ($i -lt $total) { return ($lines[$i..($total-1)] -join "`n") }
    return ""
}
function Set-Frontmatter {
    param([string]$FilePath, [string]$Title, [string]$Parent, [int]$NavOrder, [string]$Permalink)
    $body = Get-BodyContent -FilePath $FilePath
    $fm = "---`nlayout: default`ntitle: `"$Title`"`nparent: `"$Parent`"`nnav_order: $NavOrder`npermalink: $Permalink`n---`n`n"
    [System.IO.File]::WriteAllText($FilePath, ($fm + $body.TrimStart()), (New-Object System.Text.UTF8Encoding $false))
}
Write-Host "`n=== GitHub Pages Frontmatter Generator ===" -ForegroundColor Cyan
Write-Host "Section : $SectionPath" -ForegroundColor Cyan
Write-Host "Parent  : $ParentTitle`n" -ForegroundColor Cyan
if (-not (Test-Path $SectionPath)) { Write-Host "ERROR: Path not found: $SectionPath" -ForegroundColor Red; exit 1 }
if (-not $BasePermalink) { $BasePermalink = (Split-Path -Leaf $SectionPath).ToLower() -replace "\s+", "-" }
$mdFiles = Get-ChildItem -Path $SectionPath -Filter "*.md" -File | Where-Object { $_.Name -ne "index.md" } | Sort-Object Name
if ($mdFiles.Count -eq 0) { Write-Host "No markdown files found.`n" -ForegroundColor Yellow; exit 0 }
Write-Host "Files found: $($mdFiles.Count)`n" -ForegroundColor Yellow
$ok = 0
foreach ($file in $mdFiles) {
    try {
        $num = Get-FileNumber -Filename $file.Name
        $title = Get-TitleFromFilename -Filename $file.Name
        $order = if ($num) { $num } else { $ok + 1 }
        $link = New-Permalink -Title $title -Section $BasePermalink
        Set-Frontmatter -FilePath $file.FullName -Title $title -Parent $ParentTitle -NavOrder $order -Permalink $link
        Write-Host "[OK] $($file.Name)" -ForegroundColor Green
        Write-Host "     title: $title  |  nav_order: $order  |  url: $link"
        $ok++
    } catch {
        Write-Host "[ERR] $($file.Name) - $_" -ForegroundColor Red
    }
}
Write-Host "`nDone - $ok / $($mdFiles.Count) files updated.`n" -ForegroundColor Green