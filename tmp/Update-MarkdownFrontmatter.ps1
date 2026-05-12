# ============================================================
# GitHub Pages Docs Navigation Updater
# Usage: .\Update-MarkdownFrontmatter.ps1
#
# Recursively updates navigation frontmatter for all folders and
# markdown files under the docs directory.
#
# SAFE:
# - Uses .NET UTF-8 I/O (preserves emojis / box drawing chars)
# - Only rewrites the top frontmatter/header block
# - Leaves the body content untouched
# ============================================================

param(
    [Parameter(Mandatory=$false)][string]$DocsPath = "docs",
    [Parameter(Mandatory=$false)][string]$RootTitle = "Documentation"
)

$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
$WorkspaceRoot = Get-Location

function Read-Utf8File {
    param([string]$FilePath)
    return [System.IO.File]::ReadAllText($FilePath, $Utf8NoBom)
}

function Write-Utf8File {
    param([string]$FilePath, [string]$Content)
    [System.IO.File]::WriteAllText($FilePath, $Content, $Utf8NoBom)
}

function Get-FileNumber {
    param([string]$Filename)
    if ($Filename -match '(\d{3})') { return [int]$matches[1] }
    return $null
}

function ConvertTo-TitleCaseText {
    param([string]$Text)
    $clean = ($Text -replace '[-_]+', ' ').Trim()
    if ([string]::IsNullOrWhiteSpace($clean)) { return $Text }
    $ti = [System.Globalization.CultureInfo]::InvariantCulture.TextInfo
    return $ti.ToTitleCase($clean.ToLower())
}

function Get-TitleFromFilename {
    param([string]$Filename)
    $title = $Filename -replace '\.md$', ''
    $title = [regex]::Replace($title, '^[^\x00-\x7F]+\s*', '')
    $title = $title -replace '^\d{3}\s*[^\w\s]?\s*', ''
    $title = $title.Trim()
    if ($title -cmatch '^[a-z0-9\-_ ]+$') {
        return ConvertTo-TitleCaseText $title
    }
    return $title
}

function Slugify {
    param([string]$Text)
    $slug = $Text.ToLowerInvariant()
    $slug = $slug -replace '[^\p{L}\p{Nd}\s-]', ''
    $slug = $slug -replace '\s+', '-'
    $slug = $slug -replace '-+', '-'
    return $slug.Trim('-')
}

function Get-ExistingFrontmatter {
    param([string]$FilePath)

    $raw = Read-Utf8File -FilePath $FilePath
    $lines = $raw -split "`r?`n"
    $result = @{}

    $i = 0
    while ($i -lt $lines.Count -and $lines[$i].Trim() -eq '') { $i++ }
    if ($i -ge $lines.Count -or $lines[$i].Trim() -ne '---') { return $result }

    $i++
    while ($i -lt $lines.Count -and $lines[$i].Trim() -ne '---') {
        if ($lines[$i] -match '^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$') {
            $key = $matches[1]
            $value = $matches[2].Trim()
            $value = $value.Trim('"')
            $result[$key] = $value
        }
        $i++
    }
    return $result
}

function Get-BodyContent {
    param([string]$FilePath)

    $raw = Read-Utf8File -FilePath $FilePath
    $lines = $raw -split "`r?`n"
    $i = 0
    $total = $lines.Count

    while ($i -lt $total -and $lines[$i].Trim() -eq '') { $i++ }
    while ($i -lt $total -and $lines[$i].Trim() -eq '---') {
        $i++
        while ($i -lt $total -and $lines[$i].Trim() -ne '---') { $i++ }
        if ($i -lt $total) { $i++ }
        while ($i -lt $total -and $lines[$i].Trim() -eq '') { $i++ }
    }

    if ($i -lt $total) {
        return ($lines[$i..($total - 1)] -join "`n")
    }
    return ''
}

function Set-Frontmatter {
    param(
        [string]$FilePath,
        [string]$Title,
        [string]$Parent,
        $NavOrder,
        [string]$Permalink,
        [bool]$HasChildren
    )

    $body = Get-BodyContent -FilePath $FilePath
    $lines = @(
        '---',
        'layout: default',
        ('title: "{0}"' -f $Title)
    )

    if (-not [string]::IsNullOrWhiteSpace($Parent)) {
        $lines += ('parent: "{0}"' -f $Parent)
    }
    if ($NavOrder -ne $null) {
        $lines += ('nav_order: {0}' -f [int]$NavOrder)
    }
    if ($HasChildren) {
        $lines += 'has_children: true'
    }
    $lines += ('permalink: {0}' -f $Permalink)
    $lines += '---'
    $lines += ''

    $frontmatter = ($lines -join "`n")
    $final = $frontmatter + $body.TrimStart()
    Write-Utf8File -FilePath $FilePath -Content $final
}

function Get-RelativePathString {
    param([string]$RootPath, [string]$FullPath)

    $root = [System.IO.Path]::GetFullPath($RootPath)
    $full = [System.IO.Path]::GetFullPath($FullPath)

    $rootTrimmed = $root.TrimEnd('\')
    $fullTrimmed = $full.TrimEnd('\')

    if ($fullTrimmed.Equals($rootTrimmed, [System.StringComparison]::OrdinalIgnoreCase)) {
        return ''
    }

    $prefix = $rootTrimmed + '\'
    if ($full.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $full.Substring($prefix.Length).Replace('\', '/')
    }

    throw "Path '$FullPath' is not inside root '$RootPath'."
}

function Get-RelativeDirKey {
    param([string]$FullPath, [string]$RootPath)
    return Get-RelativePathString -RootPath $RootPath -FullPath $FullPath
}

function Get-ParentDirKey {
    param([string]$DirKey)
    if ([string]::IsNullOrWhiteSpace($DirKey)) { return $null }
    $idx = $DirKey.LastIndexOf('/')
    if ($idx -lt 0) { return '' }
    return $DirKey.Substring(0, $idx)
}

$DocsFullPath = Join-Path $WorkspaceRoot $DocsPath
if (-not (Test-Path $DocsFullPath)) {
    Write-Host "ERROR: docs path not found: $DocsFullPath" -ForegroundColor Red
    exit 1
}

$TopLevelIndexNavOrder = @{
    'java' = 2
    'spring' = 3
    'Distributed Systems' = 4
    'Databases' = 5
    'Messaging & Streaming' = 6
    'Networking & HTTP' = 7
    'OS & Systems' = 8
    'System Design' = 9
    'DSA' = 10
    'Software Design' = 11
    'Cloud & Infrastructure' = 12
    'DevOps & SDLC' = 13
}

$TopLevelFileNavOrder = @{
    'TECHNICAL_DICTIONARY.md' = 14
    'GITHUB_PAGES_GUIDE.md' = 15
    'SETUP_SUMMARY.md' = 16
    'IMPLEMENTATION_COMPLETE.md' = 17
    'MARKDOWN_AUTOMATION_GUIDE.md' = 18
    'COPILOT_MARKDOWN_INTEGRATION.md' = 19
    'AUTOMATION_SETUP_COMPLETE.md' = 20
}

Write-Host "`n=== GitHub Pages Docs Navigation Updater ===" -ForegroundColor Cyan
Write-Host "Docs path : $DocsFullPath" -ForegroundColor Cyan
Write-Host "Root title: $RootTitle`n" -ForegroundColor Cyan

# Discover directories that participate in navigation
$directories = Get-ChildItem -Path $DocsFullPath -Directory -Recurse | Sort-Object FullName
$allDirPaths = @($DocsFullPath) + ($directories | ForEach-Object { $_.FullName })

$dirMeta = @{}
foreach ($dirPath in $allDirPaths) {
    $indexPath = Join-Path $dirPath 'index.md'
    $relKey = Get-RelativeDirKey -FullPath $dirPath -RootPath $DocsFullPath

    if ($dirPath -ne $DocsFullPath -and -not (Test-Path $indexPath)) { continue }

    $existing = if (Test-Path $indexPath) { Get-ExistingFrontmatter -FilePath $indexPath } else { @{} }
    $folderName = Split-Path $dirPath -Leaf
    $title = if ($relKey -eq '') {
        if ($existing.ContainsKey('title')) { $existing['title'] } else { $RootTitle }
    } else {
        if ($existing.ContainsKey('title')) { $existing['title'] } else { ConvertTo-TitleCaseText $folderName }
    }

    $dirMeta[$relKey] = [ordered]@{
        DirPath = $dirPath
        IndexPath = $indexPath
        Exists = (Test-Path $indexPath)
        Title = $title
        Existing = $existing
        ParentKey = if ($relKey -eq '') { $null } else { Get-ParentDirKey -DirKey $relKey }
        Children = @()
    }
}

# Build page records: folder index pages + regular markdown pages
$pages = @()
foreach ($key in $dirMeta.Keys) {
    $meta = $dirMeta[$key]
    $existing = $meta.Existing
    $pages += [pscustomobject]@{
        Key = if ($key -eq '') { '__docs_root__' } else { "dir:$key" }
        FilePath = $meta.IndexPath
        Title = $meta.Title
        ExistingTitle = $existing['title']
        ExistingNavOrder = if ($existing.ContainsKey('nav_order') -and $existing['nav_order'] -match '^\d+$') { [int]$existing['nav_order'] } else { $null }
        ParentTitle = if ($key -eq '') { $null } else { $dirMeta[$meta.ParentKey].Title }
        ParentKey = $meta.ParentKey
        IsIndex = $true
        DirKey = $key
        FileNumber = $null
        OverrideNavOrder = if ($key -ne '' -and $meta.ParentKey -eq '' -and $TopLevelIndexNavOrder.ContainsKey((Split-Path $meta.DirPath -Leaf))) { $TopLevelIndexNavOrder[(Split-Path $meta.DirPath -Leaf)] } else { $null }
        RelativeFile = if ($key -eq '') { 'index.md' } else { "$key/index.md" }
    }
}

$mdFiles = Get-ChildItem -Path $DocsFullPath -Recurse -File -Filter '*.md' | Where-Object { $_.Name -ne 'index.md' } | Sort-Object FullName
foreach ($file in $mdFiles) {
    $dirKey = Get-RelativeDirKey -FullPath $file.DirectoryName -RootPath $DocsFullPath
    if (-not $dirMeta.ContainsKey($dirKey)) { continue }

    $existing = Get-ExistingFrontmatter -FilePath $file.FullName
    $fallbackTitle = Get-TitleFromFilename -Filename $file.Name
    $rawBaseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $title = if ($existing.ContainsKey('title')) {
        if ($existing['title'] -eq $rawBaseName) { $fallbackTitle } else { $existing['title'] }
    } else {
        $fallbackTitle
    }
    $relFile = Get-RelativePathString -RootPath $DocsFullPath -FullPath $file.FullName

    $pages += [pscustomobject]@{
        Key = "file:$relFile"
        FilePath = $file.FullName
        Title = $title
        ExistingTitle = if ($existing.ContainsKey('title')) { $existing['title'] } else { $null }
        ExistingNavOrder = if ($existing.ContainsKey('nav_order') -and $existing['nav_order'] -match '^\d+$') { [int]$existing['nav_order'] } else { $null }
        ParentTitle = $dirMeta[$dirKey].Title
        ParentKey = $dirKey
        IsIndex = $false
        DirKey = $dirKey
        FileNumber = Get-FileNumber -Filename $file.Name
        OverrideNavOrder = if ($dirKey -eq '' -and $TopLevelFileNavOrder.ContainsKey($file.Name)) { $TopLevelFileNavOrder[$file.Name] } else { $null }
        RelativeFile = $relFile
    }
}

# Assign children per parent group
foreach ($page in $pages) {
    if ($page.ParentKey -ne $null -and $dirMeta.ContainsKey($page.ParentKey)) {
        $dirMeta[$page.ParentKey].Children += $page.Key
    }
}

# Resolve nav orders: preserve existing, then filename numbers, then assign remaining after max existing
$parentGroups = $pages | Where-Object { $_.ParentKey -ne $null } | Group-Object ParentKey
foreach ($group in $parentGroups) {
    $siblings = @($group.Group)
    $used = New-Object 'System.Collections.Generic.HashSet[int]'
    foreach ($s in $siblings) {
        if ($s.OverrideNavOrder -ne $null) { [void]$used.Add($s.OverrideNavOrder) }
        elseif ($s.ExistingNavOrder -ne $null) { [void]$used.Add($s.ExistingNavOrder) }
        elseif ($s.FileNumber -ne $null) { [void]$used.Add($s.FileNumber) }
    }
    $next = if ($used.Count -gt 0) { (($used | Measure-Object -Maximum).Maximum + 1) } else { 1 }
    foreach ($s in ($siblings | Sort-Object Title)) {
        if ($s.OverrideNavOrder -ne $null) {
            $s | Add-Member -NotePropertyName ResolvedNavOrder -NotePropertyValue $s.OverrideNavOrder -Force
        } elseif ($s.ExistingNavOrder -eq $null -and $s.FileNumber -eq $null) {
            while ($used.Contains($next)) { $next++ }
            $s | Add-Member -NotePropertyName ResolvedNavOrder -NotePropertyValue $next -Force
            [void]$used.Add($next)
            $next++
        } else {
            $s | Add-Member -NotePropertyName ResolvedNavOrder -NotePropertyValue ($(if ($s.ExistingNavOrder -ne $null) { $s.ExistingNavOrder } else { $s.FileNumber })) -Force
        }
    }
}

# Root page nav order
foreach ($rootPage in ($pages | Where-Object { $_.ParentKey -eq $null })) {
    $rootOrder = if ($rootPage.ExistingNavOrder -ne $null) { $rootPage.ExistingNavOrder } else { 1 }
    $rootPage | Add-Member -NotePropertyName ResolvedNavOrder -NotePropertyValue $rootOrder -Force
}

# Write all pages
$updated = 0
foreach ($page in ($pages | Sort-Object FilePath)) {
    $hasChildren = $false
    if ($page.IsIndex -and $dirMeta.ContainsKey($page.DirKey)) {
        $hasChildren = ($dirMeta[$page.DirKey].Children.Count -gt 0)
    }

    $permalink = if ($page.IsIndex) {
        if ($page.DirKey -eq '') { '/' }
        else {
            $segments = @()
            foreach ($seg in ($page.DirKey -split '/')) { if ($seg) { $segments += (Slugify $seg) } }
            '/' + ($segments -join '/') + '/'
        }
    } else {
        $relNoExt = [System.IO.Path]::ChangeExtension($page.RelativeFile, $null).TrimEnd('.')
        $segments = @()
        foreach ($seg in ($relNoExt -split '/')) {
            if ($seg) {
                if ($seg -eq 'index') { continue }
                $name = if ($seg -eq [System.IO.Path]::GetFileNameWithoutExtension($page.RelativeFile)) { Slugify $page.Title } else { Slugify $seg }
                $segments += $name
            }
        }
        '/' + ($segments -join '/') + '/'
    }

    Set-Frontmatter -FilePath $page.FilePath `
                    -Title $page.Title `
                    -Parent $page.ParentTitle `
                    -NavOrder $page.ResolvedNavOrder `
                    -Permalink $permalink `
                    -HasChildren $hasChildren

    Write-Host "[OK] $($page.RelativeFile)" -ForegroundColor Green
    Write-Host "     title: $($page.Title) | parent: $($page.ParentTitle) | nav_order: $($page.ResolvedNavOrder) | permalink: $permalink"
    $updated++
}

Write-Host "`nDone - updated $updated markdown files under $DocsPath.`n" -ForegroundColor Green
