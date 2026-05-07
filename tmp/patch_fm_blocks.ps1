Set-Location "c:\ASK\MyWorkspace\sk-keys"
$enc=[System.Text.UTF8Encoding]::new($false)
$c=[System.IO.File]::ReadAllText("GENERATOR_PROMPT.md",$enc)

# arrow character used in the file
$larr = [char]0x2190  # ←

$new_fm = "Front matter rules:`r`n  - id: <CODE>-<NNN>`r`n  - title: <Keyword Name>`r`n  - category: <Full Category Name>`r`n  - tier: <tier-N-name>`r`n  - folder: <CODE-folder-name>`r`n  - difficulty: star`r`n  - depends_on: CODE-NNN, CODE-NNN`r`n  - used_by: CODE-NNN, CODE-NNN`r`n  - related: CODE-NNN, CODE-NNN`r`n  - tags: #tag1, #tag2, #tag3`r`n  - status: draft`r`n  - version: 1"
$new_fm = $new_fm.Replace("star", "★☆☆ | ★★☆ | ★★★")

$new_fm2 = "Front matter (use exact values for the chosen category):`r`n  id: <CODE>-<NNN>`r`n  title: <Keyword Name>`r`n  category: <Full Category Name>`r`n  tier: <tier-N-name>`r`n  folder: <CODE-folder-name>`r`n  difficulty: star`r`n  depends_on: CODE-NNN, CODE-NNN`r`n  used_by: CODE-NNN, CODE-NNN`r`n  related: CODE-NNN, CODE-NNN`r`n  tags: #tag1, #tag2, #tag3`r`n  status: draft`r`n  version: 1"
$new_fm2 = $new_fm2.Replace("star", "★☆☆ | ★★☆ | ★★★")

# ── Block 1: batch-of-10 prompt ──
$idx1 = $c.IndexOf("Front matter rules:`r`n  - layout: default")
Write-Host "Block1 idx=$idx1"
if ($idx1 -ge 0) {
    $endmarker = "`r`n  - tags: #tag1, #tag2, #tag3"
    $endIdx = $c.IndexOf($endmarker, $idx1)
    if ($endIdx -ge 0) {
        $endIdx += $endmarker.Length
        $old1 = $c.Substring($idx1, $endIdx - $idx1)
        $c = $c.Remove($idx1, $endIdx - $idx1).Insert($idx1, $new_fm)
        Write-Host "✅ Block 1 replaced"
    } else {
        Write-Host "❌ Block 1 end not found"
    }
}

# ── Block 2: category-focused prompt ──
$idx2 = $c.IndexOf("Front matter (use exact values for the chosen category):`r`n  layout: default")
Write-Host "Block2 idx=$idx2"
if ($idx2 -ge 0) {
    $endmarker2 = "`r`n  tags: #tag1, #tag2, #tag3"
    $endIdx2 = $c.IndexOf($endmarker2, $idx2)
    if ($endIdx2 -ge 0) {
        $endIdx2 += $endmarker2.Length
        $c = $c.Remove($idx2, $endIdx2 - $idx2).Insert($idx2, $new_fm2)
        Write-Host "✅ Block 2 replaced"
    } else {
        Write-Host "❌ Block 2 end not found"
    }
}

[System.IO.File]::WriteAllText("GENERATOR_PROMPT.md", $c, $enc)
Write-Host "Saved. Len=$($c.Length)"
Write-Host "layout: default remaining: $(([regex]::Matches($c,'layout: default')).Count)"
