$em = [char]0x2014
$enc = [System.Text.UTF8Encoding]::new($false)
$base = "c:\ASK\MyWorkspace\sk-keys\"

$fixes = @(
    @{ rel = "dictionary\tier-5-distributed-architecture\DST-distributed-systems\DST-015 $em Total Order Partial Order.md"; old = "/distributed-systems/total-order-partial-order/"; nw = "/distributed-systems/dst-015-total-order-partial-order/" }
    @{ rel = "dictionary\tier-5-distributed-architecture\DST-distributed-systems\DST-026 $em Fencing Epoch.md"; old = "/distributed-systems/fencing-epoch/"; nw = "/distributed-systems/dst-026-fencing-epoch/" }
    @{ rel = "dictionary\tier-5-distributed-architecture\DST-distributed-systems\DST-029 $em Two-Phase Commit.md"; old = "/distributed-systems/two-phase-commit/"; nw = "/distributed-systems/dst-029-two-phase-commit/" }
    @{ rel = "dictionary\tier-5-distributed-architecture\DST-distributed-systems\DST-031 $em Three-Phase Commit.md"; old = "/distributed-systems/three-phase-commit/"; nw = "/distributed-systems/dst-031-three-phase-commit/" }
    @{ rel = "dictionary\tier-2-networking-security\API-http-apis\API-037 $em API Keys.md"; old = "/http-apis/api-keys/"; nw = "/http-apis/api-037-api-keys/" }
    @{ rel = "dictionary\tier-2-networking-security\API-http-apis\API-053 $em Pagination.md"; old = "/http-apis/pagination/"; nw = "/http-apis/api-053-pagination/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-037 $em CyclicBarrier.md"; old = "/java-concurrency/cyclicbarrier/"; nw = "/java-concurrency/jcc-037-cyclicbarrier/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-038 $em Phaser.md"; old = "/java-concurrency/phaser/"; nw = "/java-concurrency/jcc-038-phaser/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-039 $em BlockingQueue.md"; old = "/java-concurrency/blockingqueue/"; nw = "/java-concurrency/jcc-039-blockingqueue/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-040 $em ConcurrentHashMap.md"; old = "/java-concurrency/concurrenthashmap/"; nw = "/java-concurrency/jcc-040-concurrenthashmap/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-041 $em CopyOnWriteArrayList.md"; old = "/java-concurrency/copyonwritearraylist/"; nw = "/java-concurrency/jcc-041-copyonwritearraylist/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-042 $em Atomic Classes.md"; old = "/java-concurrency/atomic-classes/"; nw = "/java-concurrency/jcc-042-atomic-classes/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-043 $em VarHandle.md"; old = "/java-concurrency/varhandle/"; nw = "/java-concurrency/jcc-043-varhandle/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-046 $em Thread Dump Analysis.md"; old = "/java-concurrency/thread-dump-analysis/"; nw = "/java-concurrency/jcc-046-thread-dump-analysis/" }
    @{ rel = "dictionary\tier-3-java\JCC-java-concurrency\JCC-047 $em Deadlock Detection (Java).md"; old = "/java-concurrency/deadlock-detection-java/"; nw = "/java-concurrency/jcc-047-deadlock-detection/" }
    @{ rel = "dictionary\tier-3-java\JVM-java-jvm-internals\JVM-030 $em G1GC.md"; old = "/java/g1gc/"; nw = "/java/jvm-030-g1gc/" }
    @{ rel = "dictionary\tier-6-infrastructure-devops\TST-testing\TST-054 $em SonarQube Quality Gate.md"; old = "/testing/sonarqube-quality-gate/"; nw = "/testing/tst-054-sonarqube-quality-gate/" }
)

$fixed = 0
$skipped = 0
$missing = 0

foreach ($d in $fixes) {
    $p = $base + $d.rel
    if (-not (Test-Path $p)) {
        Write-Host "MISSING: $($d.rel)"
        $missing++
        continue
    }
    $c = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
    $c2 = $c -replace [regex]::Escape("permalink: $($d.old)"), "permalink: $($d.nw)"
    if ($c -ne $c2) {
        [System.IO.File]::WriteAllText($p, $c2, $enc)
        $fixed++
        Write-Host "FIXED: $(Split-Path $p -Leaf)"
    } else {
        Write-Host "SKIP (no match): $(Split-Path $p -Leaf)"
        $skipped++
    }
}

Write-Host ""
Write-Host "Results: Fixed=$fixed  Skipped=$skipped  Missing=$missing"
