############################################################################
# Fix-KeywordFiles.ps1
############################################################################
$base = "C:\ASK\MyWorkspace\sk-keys\docs"
$boxTL = [char]0x250C
$boxBL = [char]0x2514
$categories = @(
    @{ Dir = "Java";          Parent = "Java Fundamentals"; PBase = "/java/";        Nums = 51..65   }
    @{ Dir = "Testing";       Parent = "Testing";           PBase = "/testing/";     Nums = 412..423 }
    @{ Dir = "Clean Code";    Parent = "Clean Code";        PBase = "/clean-code/";  Nums = 424..433 }
    @{ Dir = "DevOps & SDLC"; Parent = "DevOps & SDLC";    PBase = "/devops-sdlc/"; Nums = 450..460 }
)
$catIndexes = @(
    @{ Dir="Testing";       Title="Testing";       Parent="Documentation"; NavOrder=13; Permalink="/testing/";     Desc="Testing strategies: Unit, Integration, TDD, BDD, Mutation Testing."; Range="412-423"; Count=12 }
    @{ Dir="Clean Code";    Title="Clean Code";    Parent="Documentation"; NavOrder=14; Permalink="/clean-code/";  Desc="Clean code principles: Cohesion, Coupling, Abstraction, Technical Debt."; Range="424-433"; Count=10 }
    @{ Dir="DevOps & SDLC"; Title="DevOps & SDLC"; Parent="Documentation"; NavOrder=15; Permalink="/devops-sdlc/"; Desc="DevOps practices: CI/CD, Blue-Green, GitOps, SRE, Error Budget, IaC."; Range="450-460"; Count=11 }
)
function Slugify([string]$n) {
    ($n.ToLower() -replace '[^a-z0-9\s\-]','' -replace '\s+','-' -replace '-+','-').Trim('-')
}
function Fix-File($fp, $parent, $pbase, $nums) {
    $enc = [System.Text.Encoding]::UTF8
    $c = [System.IO.File]::ReadAllText($fp, $enc)
    $fn = Split-Path $fp -Leaf
    $mod = $false
    $nm = [regex]::Match($fn, '^\d+')
    if (-not $nm.Success) { return }
    $num = [int]$nm.Value
    if ($nums -and ($num -notin $nums)) { return }
    $hm = [regex]::Match($c, '(?m)^#\s*\d+\s*[—\-]+\s*(.+?)\s*$')
    $title = if ($hm.Success) { $hm.Groups[1].Value.Trim() } else { $fn -replace '^\d+\s*.{1,3}\s*','' -replace '\.md$','' }
    $slug = Slugify $title
    $perm = "${pbase}${slug}/"
    if ($c -notmatch '(?m)^layout:\s') {
        $nf = "layout: default`r`ntitle: `"$title`"`r`nparent: `"$parent`"`r`nnav_order: $num`r`npermalink: $perm`r`n"
        $fi = $c.IndexOf("`n")
        if ($fi -ge 0) { $c = $c.Substring(0,$fi+1) + $nf + $c.Substring($fi+1); $mod = $true }
    }
    $bi = $c.IndexOf($boxTL)
    if ($bi -ge 0) {
        $lb = [Math]::Max(0,$bi-15); $before = $c.Substring($lb,$bi-$lb)
        if ($before -notmatch '```') {
            $ei = $c.IndexOf($boxBL,$bi)
            if ($ei -ge 0) {
                $le = $c.IndexOf("`n",$ei); if ($le -eq -1) { $le = $c.Length } else { $le++ }
                $bt = $c.Substring($bi,$le-$bi)
                $fc = '```' + "`r`n" + $bt + '```' + "`r`n"
                $c = $c.Substring(0,$bi) + $fc + $c.Substring($le); $mod = $true
            }
        }
    }
    if ($mod) { [System.IO.File]::WriteAllText($fp,$c,$enc); Write-Host "  FIXED : $fn" -ForegroundColor Green }
    else { Write-Host "  OK    : $fn" -ForegroundColor DarkGray }
}
function Make-Index($ci) {
    $d = Join-Path $base $ci.Dir; $ip = Join-Path $d "index.md"
    if ((Test-Path $ip) -and ([System.IO.File]::ReadAllText($ip) -match 'has_children:')) {
        Write-Host "  OK    : index.md in $($ci.Dir)" -ForegroundColor DarkGray; return
    }
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    $body = "---`nlayout: default`ntitle: `"$($ci.Title)`"`nparent: `"$($ci.Parent)`"`nnav_order: $($ci.NavOrder)`nhas_children: true`npermalink: $($ci.Permalink)`n---`n`n# $($ci.Title)`n`n$($ci.Desc)`n`n**Keywords:** $($ci.Range) ($($ci.Count) terms)`n"
    [System.IO.File]::WriteAllText($ip, $body, [System.Text.Encoding]::UTF8)
    Write-Host "  CREATED: index.md -> $($ci.Dir)" -ForegroundColor Cyan
}
Write-Host "`n=== Category index.md ===" -ForegroundColor Yellow
$catIndexes | ForEach-Object { Make-Index $_ }
Write-Host "`n=== Fix keyword files ===" -ForegroundColor Yellow
foreach ($cat in $categories) {
    $dp = Join-Path $base $cat.Dir; Write-Host "`n  [$($cat.Dir)]" -ForegroundColor Magenta
    if (-not (Test-Path $dp)) { Write-Host "  MISSING: $dp" -ForegroundColor Red; continue }
    Get-ChildItem $dp -Filter "*.md" | Where-Object {$_.Name -ne "index.md"} | Sort-Object Name | ForEach-Object {
        Fix-File $_.FullName $cat.Parent $cat.PBase $cat.Nums
    }
}
Write-Host "`n=== Done ===" -ForegroundColor Green
