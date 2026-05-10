Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$cats = @(
    @{code='CSF';path='dictionary\tier-1-foundations\CSF-cs-fundamentals'},
    @{code='DSA';path='dictionary\tier-1-foundations\DSA-data-structures'},
    @{code='LNX';path='dictionary\tier-1-foundations\LNX-linux'},
    @{code='OSY';path='dictionary\tier-1-foundations\OSY-operating-systems'},
    @{code='API';path='dictionary\tier-2-networking-security\API-http-apis'},
    @{code='NET';path='dictionary\tier-2-networking-security\NET-networking'},
    @{code='SEC';path='dictionary\tier-2-networking-security\SEC-security'},
    @{code='DPT';path='dictionary\tier-5-distributed-architecture\DPT-design-patterns'},
    @{code='DST';path='dictionary\tier-5-distributed-architecture\DST-distributed-systems'},
    @{code='MSV';path='dictionary\tier-5-distributed-architecture\MSV-microservices'},
    @{code='SAP';path='dictionary\tier-5-distributed-architecture\SAP-software-architecture'},
    @{code='SYD';path='dictionary\tier-5-distributed-architecture\SYD-system-design'}
)
foreach ($c in $cats) {
    $files = @(Get-ChildItem "$($c.path)\*.md" | Where-Object { $_.Name -ne 'index.md' -and !$_.Name.StartsWith('_') })
    $nums  = $files | ForEach-Object { if ($_.BaseName -match '^[A-Z]+-0*(\d+)') { [int]$Matches[1] } else { 0 } }
    $high  = if ($nums) { ($nums | Measure-Object -Maximum).Maximum } else { 0 }
    $idxRaw = if (Test-Path "$($c.path)\index.md") { [IO.File]::ReadAllText("$($c.path)\index.md") } else { '' }
    $claim  = if ($idxRaw -match 'Keywords.*\((\d+) terms\)') { $Matches[1] } else { '?' }
    Write-Host "$($c.code) | files=$($files.Count) | highest=$high | index_claims=$claim"
}
