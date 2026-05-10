# create_tier3_keywords.ps1
# Creates missing keyword stub files and rebuilds indexes for tier-3-java.
# Run with: pwsh -ExecutionPolicy Bypass -File tmp\create_tier3_keywords.ps1

Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Write-File($path, $content) {
    [System.IO.File]::WriteAllText($path, $content, $enc)
}

function New-Stub($base, $id, $title, $cat, $tier, $folder, $diff, $parent, $tagLines, $slug) {
    $safeTitle = $title -replace ' / ', '  ' -replace '/', ''
    $fname     = "$base\$id - $safeTitle.md"
    if (Test-Path $fname) { Write-Host "SKIP (exists): $id"; return }
    $yTitle    = if ($title -match ': ') { "`"$title`"" } else { $title }
    $navOrder  = [int]($id -replace '[A-Z]+-0*', '')
    $content = @"
---
id: $id
title: $yTitle
category: $cat
tier: $tier
folder: $folder
difficulty: $diff
depends_on:
used_by:
related:
tags:
$tagLines
status: draft
version: 0
layout: default
parent: "$parent"
grand_parent: "Technical Dictionary"
nav_order: $navOrder
permalink: $slug
---
"@
    Write-File $fname $content
    Write-Host "Created: $id - $title"
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — NEW JVM KEYWORDS (JVM-067 to JVM-075)
# ─────────────────────────────────────────────────────────────────────────────
$jvmBase = 'dictionary\tier-3-java\JVM-java-jvm-internals'
$jvmCat  = 'Java & JVM Internals'
$jvmTier = 'tier-3-java'
$jvmFld  = 'JVM-java-jvm-internals'
$jvmPar  = 'Java & JVM Internals'
$jvmTags2 = "  - java`n  - jvm`n  - internals`n  - foundational"
$jvmTags3 = "  - java`n  - jvm`n  - internals`n  - advanced"

$jvmNew = @(
    @{id='JVM-067';title='Method Area';                              diff='★★☆';slug='/jvm/method-area/';              tags=$jvmTags2},
    @{id='JVM-068';title='PC Register (Program Counter)';            diff='★★★';slug='/jvm/pc-register/';               tags=$jvmTags3},
    @{id='JVM-069';title='Native Method Stack';                      diff='★★★';slug='/jvm/native-method-stack/';       tags=$jvmTags3},
    @{id='JVM-070';title='JVM Flags (-Xms, -Xmx, -XX: Flags)';      diff='★★☆';slug='/jvm/jvm-flags/';                tags=$jvmTags2},
    @{id='JVM-071';title='Heap Dump';                                diff='★★☆';slug='/jvm/heap-dump/';                tags=$jvmTags2},
    @{id='JVM-072';title='Thread Dump';                              diff='★★☆';slug='/jvm/thread-dump/';              tags=$jvmTags2},
    @{id='JVM-073';title='Class Loading Delegation Model';           diff='★★★';slug='/jvm/class-loading-delegation/'; tags=$jvmTags3},
    @{id='JVM-074';title='Compressed OOPs';                         diff='★★★';slug='/jvm/compressed-oops/';          tags=$jvmTags3},
    @{id='JVM-075';title='Class Data Sharing (CDS / AppCDS)';       diff='★★★';slug='/jvm/class-data-sharing/';       tags=$jvmTags3}
)

foreach ($kw in $jvmNew) {
    New-Stub $jvmBase $kw.id $kw.title $jvmCat $jvmTier $jvmFld $kw.diff $jvmPar $kw.tags $kw.slug
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — NEW JCC KEYWORDS (JCC-078 to JCC-086)
# ─────────────────────────────────────────────────────────────────────────────
$jccBase = 'dictionary\tier-3-java\JCC-java-concurrency'
$jccCat  = 'Java Concurrency'
$jccTier = 'tier-3-java'
$jccFld  = 'JCC-java-concurrency'
$jccPar  = 'Java Concurrency'
$jccTags1 = "  - java`n  - concurrency`n  - foundational"
$jccTags2 = "  - java`n  - concurrency`n  - intermediate"
$jccTags3 = "  - java`n  - concurrency`n  - advanced"

$jccNew = @(
    @{id='JCC-078';title='Daemon Threads';                           diff='★★☆';slug='/java-concurrency/daemon-threads/';              tags=$jccTags2},
    @{id='JCC-079';title='Thread Priority';                          diff='★★☆';slug='/java-concurrency/thread-priority/';             tags=$jccTags2},
    @{id='JCC-080';title='ThreadFactory';                            diff='★★☆';slug='/java-concurrency/thread-factory/';              tags=$jccTags2},
    @{id='JCC-081';title='Immutable Object Pattern';                 diff='★★☆';slug='/java-concurrency/immutable-object-pattern/';    tags=$jccTags2},
    @{id='JCC-082';title='Producer-Consumer Pattern';                diff='★★☆';slug='/java-concurrency/producer-consumer-pattern/';  tags=$jccTags2},
    @{id='JCC-083';title='Liveness Issues (Livelock / Starvation)'; diff='★★☆';slug='/java-concurrency/liveness-issues/';             tags=$jccTags2},
    @{id='JCC-084';title='ABA Problem';                              diff='★★★';slug='/java-concurrency/aba-problem/';                tags=$jccTags3},
    @{id='JCC-085';title='Work-Stealing Algorithm';                  diff='★★★';slug='/java-concurrency/work-stealing-algorithm/';    tags=$jccTags3},
    @{id='JCC-086';title='Thread Groups (Legacy)';                   diff='★☆☆';slug='/java-concurrency/thread-groups/';              tags=$jccTags1}
)

foreach ($kw in $jccNew) {
    New-Stub $jccBase $kw.id $kw.title $jccCat $jccTier $jccFld $kw.diff $jccPar $kw.tags $kw.slug
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — NEW JLG KEYWORDS (JLG-054 to JLG-084)
# ─────────────────────────────────────────────────────────────────────────────
$jlgBase = 'dictionary\tier-3-java\JLG-java-language'
$jlgCat  = 'Java Language'
$jlgTier = 'tier-3-java'
$jlgFld  = 'JLG-java-language'
$jlgPar  = 'Java Language'
$jlgTags0 = "  - java`n  - language`n  - foundational`n  - mental-model"
$jlgTags1 = "  - java`n  - language`n  - foundational"
$jlgTags2 = "  - java`n  - language`n  - intermediate"
$jlgTags3 = "  - java`n  - language`n  - advanced"

$jlgNew = @(
    @{id='JLG-054';title='Java Program Structure (class, method, main)';  diff='★☆☆';slug='/java-language/java-program-structure/';         tags=$jlgTags0},
    @{id='JLG-055';title='Variables and Data Types in Java';               diff='★☆☆';slug='/java-language/variables-data-types/';            tags=$jlgTags1},
    @{id='JLG-056';title='Control Flow (if/else, for, while)';             diff='★☆☆';slug='/java-language/control-flow/';                    tags=$jlgTags1},
    @{id='JLG-057';title='Java Arrays (Basics)';                           diff='★☆☆';slug='/java-language/java-arrays-basics/';              tags=$jlgTags1},
    @{id='JLG-058';title='Classes and Objects (Basics)';                   diff='★☆☆';slug='/java-language/classes-and-objects-basics/';      tags=$jlgTags1},
    @{id='JLG-059';title='Packages and Imports';                           diff='★☆☆';slug='/java-language/packages-and-imports/';            tags=$jlgTags1},
    @{id='JLG-060';title='Java Standard Library Overview (java.lang, java.util)';diff='★☆☆';slug='/java-language/standard-library-overview/';tags=$jlgTags1},
    @{id='JLG-061';title='Inheritance and Polymorphism';                   diff='★☆☆';slug='/java-language/inheritance-and-polymorphism/';    tags=$jlgTags1},
    @{id='JLG-062';title='Primitive Types and Wrapper Classes';             diff='★☆☆';slug='/java-language/primitive-types-wrapper-classes/'; tags=$jlgTags1},
    @{id='JLG-063';title='Enums';                                          diff='★★☆';slug='/java-language/enums/';                           tags=$jlgTags2},
    @{id='JLG-064';title='String Methods (Common Operations)';              diff='★★☆';slug='/java-language/string-methods/';                  tags=$jlgTags2},
    @{id='JLG-065';title='Java DateTime API (java.time)';                  diff='★★☆';slug='/java-language/java-datetime-api/';               tags=$jlgTags2},
    @{id='JLG-066';title='Try-with-Resources';                             diff='★★☆';slug='/java-language/try-with-resources/';              tags=$jlgTags2},
    @{id='JLG-067';title='Comparable vs Comparator';                       diff='★★☆';slug='/java-language/comparable-vs-comparator/';        tags=$jlgTags2},
    @{id='JLG-068';title='Iterators and Iterable';                         diff='★★☆';slug='/java-language/iterators-and-iterable/';          tags=$jlgTags2},
    @{id='JLG-069';title='Java 8 Features Overview (streams, lambdas, Optional)';diff='★★☆';slug='/java-language/java-8-features-overview/'; tags=$jlgTags2},
    @{id='JLG-070';title='equals() and hashCode() Contract';               diff='★★☆';slug='/java-language/equals-hashcode-contract/';        tags=$jlgTags2},
    @{id='JLG-071';title='instanceof and Type Casting';                    diff='★★☆';slug='/java-language/instanceof-type-casting/';         tags=$jlgTags2},
    @{id='JLG-072';title='Text Blocks (Java 15+)';                         diff='★★☆';slug='/java-language/text-blocks/';                     tags=$jlgTags2},
    @{id='JLG-073';title='Switch Expressions (Java 14+)';                  diff='★★☆';slug='/java-language/switch-expressions/';              tags=$jlgTags2},
    @{id='JLG-074';title='Java Interfaces (Practical Usage)';              diff='★★☆';slug='/java-language/java-interfaces-practical/';       tags=$jlgTags2},
    @{id='JLG-075';title='Java NIO (Non-Blocking I/O)';                    diff='★★☆';slug='/java-language/java-nio/';                        tags=$jlgTags2},
    @{id='JLG-076';title='MethodHandles';                                  diff='★★★';slug='/java-language/methodhandles/';                   tags=$jlgTags3},
    @{id='JLG-077';title='Java Agents (java.lang.instrument)';             diff='★★★';slug='/java-language/java-agents/';                     tags=$jlgTags3},
    @{id='JLG-078';title='Class File Format (javap)';                      diff='★★★';slug='/java-language/class-file-format-javap/';         tags=$jlgTags3},
    @{id='JLG-079';title='JFR (Java Flight Recorder) Deep Dive';           diff='★★★';slug='/java-language/jfr-deep-dive/';                   tags=$jlgTags3},
    @{id='JLG-080';title='Hidden Classes (Java 15+)';                      diff='★★★';slug='/java-language/hidden-classes/';                  tags=$jlgTags3},
    @{id='JLG-081';title='java.util.concurrent.Flow (Reactive Java)';      diff='★★★';slug='/java-language/java-util-concurrent-flow/';       tags=$jlgTags3},
    @{id='JLG-082';title='String Deduplication (GC Feature)';              diff='★★★';slug='/java-language/string-deduplication/';            tags=$jlgTags3},
    @{id='JLG-083';title='JEP (Java Enhancement Proposal) Process';        diff='★★★';slug='/java-language/jep-process/';                     tags=$jlgTags3},
    @{id='JLG-084';title='Project Amber Design Rationale';                 diff='★★★';slug='/java-language/project-amber-design-rationale/';  tags=$jlgTags3}
)

foreach ($kw in $jlgNew) {
    New-Stub $jlgBase $kw.id $kw.title $jlgCat $jlgTier $jlgFld $kw.diff $jlgPar $kw.tags $kw.slug
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — NEW SPR KEYWORDS (SPR-071 to SPR-098)
# ─────────────────────────────────────────────────────────────────────────────
$sprBase = 'dictionary\tier-3-java\SPR-spring-core'
$sprCat  = 'Spring Core'
$sprTier = 'tier-3-java'
$sprFld  = 'SPR-spring-core'
$sprPar  = 'Spring Core'
$sprTags0 = "  - java`n  - spring`n  - foundational`n  - mental-model"
$sprTags1 = "  - java`n  - spring`n  - foundational"
$sprTags2 = "  - java`n  - spring`n  - springboot`n  - intermediate"
$sprTags3 = "  - java`n  - spring`n  - advanced`n  - deep-dive"

$sprNew = @(
    @{id='SPR-071';title='@Component / @Service / @Repository';                   diff='★☆☆';slug='/spring/component-service-repository/';           tags=$sprTags1},
    @{id='SPR-072';title='@SpringBootApplication';                                 diff='★☆☆';slug='/spring/springbootapplication/';                  tags=$sprTags1},
    @{id='SPR-073';title='@RestController / @Controller';                          diff='★★☆';slug='/spring/restcontroller-controller/';               tags=$sprTags2},
    @{id='SPR-074';title='@RequestMapping / @GetMapping / @PostMapping';           diff='★★☆';slug='/spring/request-mapping/';                        tags=$sprTags2},
    @{id='SPR-075';title='@RequestBody / @ResponseBody';                           diff='★★☆';slug='/spring/requestbody-responsebody/';                tags=$sprTags2},
    @{id='SPR-076';title='@PathVariable / @RequestParam';                          diff='★★☆';slug='/spring/pathvariable-requestparam/';               tags=$sprTags2},
    @{id='SPR-077';title='Spring Profiles (@Profile, application.yml)';            diff='★★☆';slug='/spring/spring-profiles/';                         tags=$sprTags2},
    @{id='SPR-078';title='Spring Validation (@Valid, @NotNull)';                   diff='★★☆';slug='/spring/spring-validation/';                       tags=$sprTags2},
    @{id='SPR-079';title='Exception Handling (@ExceptionHandler, @ControllerAdvice)';diff='★★☆';slug='/spring/exception-handling/';                   tags=$sprTags2},
    @{id='SPR-080';title='Spring Cache Abstraction (@Cacheable)';                  diff='★★☆';slug='/spring/spring-cache-abstraction/';                tags=$sprTags2},
    @{id='SPR-081';title='Spring Events (ApplicationEvent, @EventListener)';       diff='★★☆';slug='/spring/spring-events/';                          tags=$sprTags2},
    @{id='SPR-082';title='Conditional Beans (@ConditionalOnProperty)';             diff='★★☆';slug='/spring/conditional-beans/';                      tags=$sprTags2},
    @{id='SPR-083';title='ResponseEntity and HTTP Status Handling';                diff='★★☆';slug='/spring/responseentity/';                          tags=$sprTags2},
    @{id='SPR-084';title='Spring Boot DevTools';                                   diff='★☆☆';slug='/spring/spring-boot-devtools/';                    tags=$sprTags1},
    @{id='SPR-085';title='Spring Retry';                                           diff='★★☆';slug='/spring/spring-retry/';                           tags=$sprTags2},
    @{id='SPR-086';title='MockMvc';                                                diff='★★☆';slug='/spring/mockmvc/';                                tags=$sprTags2},
    @{id='SPR-087';title='@MockBean / @SpyBean';                                   diff='★★☆';slug='/spring/mockbean-spybean/';                        tags=$sprTags2},
    @{id='SPR-088';title='Spring Context Refresh (AbstractApplicationContext)';    diff='★★★';slug='/spring/spring-context-refresh/';                  tags=$sprTags3},
    @{id='SPR-089';title='Bean Definition Registry';                               diff='★★★';slug='/spring/bean-definition-registry/';                tags=$sprTags3},
    @{id='SPR-090';title='Spring Boot AOT Compilation (Spring 6)';                 diff='★★★';slug='/spring/spring-boot-aot-compilation/';             tags=$sprTags3},
    @{id='SPR-091';title='Spring + Virtual Threads (Spring 6.1)';                  diff='★★★';slug='/spring/spring-virtual-threads/';                  tags=$sprTags3},
    @{id='SPR-092';title='Spring Security OAuth2 Resource Server';                 diff='★★★';slug='/spring/spring-security-oauth2-resource-server/';  tags=$sprTags3},
    @{id='SPR-093';title='Spring Data REST';                                       diff='★★★';slug='/spring/spring-data-rest/';                        tags=$sprTags3},
    @{id='SPR-094';title='Spring Native Image Support';                            diff='★★★';slug='/spring/spring-native-image-support/';             tags=$sprTags3},
    @{id='SPR-095';title='Spring Framework Design Rationale';                      diff='★★★';slug='/spring/spring-framework-design-rationale/';       tags=$sprTags3},
    @{id='SPR-096';title='Project Reactor Design (Reactive Streams Spec)';         diff='★★★';slug='/spring/project-reactor-design/';                  tags=$sprTags3},
    @{id='SPR-097';title='Spring Boot Auto-Configuration Algorithm';               diff='★★★';slug='/spring/spring-boot-auto-configuration-algorithm/'; tags=$sprTags3},
    @{id='SPR-098';title='Spring Test Context Management';                         diff='★★★';slug='/spring/spring-test-context-management/';          tags=$sprTags3}
)

foreach ($kw in $sprNew) {
    New-Stub $sprBase $kw.id $kw.title $sprCat $sprTier $sprFld $kw.diff $sprPar $kw.tags $kw.slug
}

Write-Host "`n--- Stub creation complete ---"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — UPDATE JVM index.md (append new rows only)
# ─────────────────────────────────────────────────────────────────────────────
$jvmIdx = 'dictionary\tier-3-java\JVM-java-jvm-internals\index.md'
$jvmContent = [System.IO.File]::ReadAllText($jvmIdx)

# Replace the keywords count line and append new rows
$jvmNewRows = @"
| JVM-067 | Method Area | ★★☆ |
| JVM-068 | PC Register (Program Counter) | ★★★ |
| JVM-069 | Native Method Stack | ★★★ |
| JVM-070 | JVM Flags (-Xms, -Xmx, -XX: Flags) | ★★☆ |
| JVM-071 | Heap Dump | ★★☆ |
| JVM-072 | Thread Dump | ★★☆ |
| JVM-073 | Class Loading Delegation Model | ★★★ |
| JVM-074 | Compressed OOPs | ★★★ |
| JVM-075 | Class Data Sharing (CDS / AppCDS) | ★★★ |
"@

$jvmContent = $jvmContent -replace '\*\*Keywords:\*\*.*?\(66 terms\)', '**Keywords:** JVM-001--JVM-075 (75 terms)'
# Append new rows at end (after last existing row)
$jvmContent = $jvmContent.TrimEnd() + "`n" + $jvmNewRows.TrimStart()
Write-File $jvmIdx $jvmContent
Write-Host "Updated JVM index.md"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — REBUILD JCC index.md (full table from actual files)
# ─────────────────────────────────────────────────────────────────────────────
$jccIdx = 'dictionary\tier-3-java\JCC-java-concurrency\index.md'

$jccTable = @"
**Keywords:** JCC-001--JCC-086 (86 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| JCC-001 | Why Concurrency Is Hard | ★☆☆ |
| JCC-002 | The Thread Safety Problem - A Mental Model | ★☆☆ |
| JCC-003 | Java Concurrency Approach - History and Philosophy | ★☆☆ |
| JCC-004 | Concurrency vs Parallelism in Java | ★☆☆ |
| JCC-005 | The Java Concurrency Ecosystem Map | ★☆☆ |
| JCC-006 | Thread (Java) | ★☆☆ |
| JCC-007 | Runnable | ★☆☆ |
| JCC-008 | Callable | ★☆☆ |
| JCC-009 | Future | ★☆☆ |
| JCC-010 | CompletableFuture | ★★★ |
| JCC-011 | Thread Lifecycle | ★★☆ |
| JCC-012 | Thread States | ★★☆ |
| JCC-013 | synchronized | ★★☆ |
| JCC-014 | volatile | ★★★ |
| JCC-015 | wait / notify / notifyAll | ★★★ |
| JCC-016 | ReentrantLock | ★★★ |
| JCC-017 | ReadWriteLock | ★★★ |
| JCC-018 | StampedLock | ★★★ |
| JCC-019 | ThreadLocal | ★★★ |
| JCC-020 | Java Memory Model (JMM) | ★★★ |
| JCC-021 | Race Condition | ★★☆ |
| JCC-022 | CAS (Compare-And-Swap) | ★★★ |
| JCC-023 | Optimistic Locking (Java) | ★★★ |
| JCC-024 | Executor | ★★☆ |
| JCC-025 | ExecutorService | ★★☆ |
| JCC-026 | ThreadPoolExecutor | ★★★ |
| JCC-027 | ForkJoinPool | ★★★ |
| JCC-028 | Virtual Threads (Project Loom) | ★★★ |
| JCC-029 | Carrier Thread | ★★★ |
| JCC-030 | Continuation | ★★★ |
| JCC-031 | Semaphore (Java) | ★★☆ |
| JCC-032 | CountDownLatch | ★★☆ |
| JCC-033 | CyclicBarrier | ★★★ |
| JCC-034 | Phaser | ★★★ |
| JCC-035 | BlockingQueue | ★★☆ |
| JCC-036 | ConcurrentHashMap | ★★★ |
| JCC-037 | CopyOnWriteArrayList | ★★★ |
| JCC-038 | Atomic Classes | ★★★ |
| JCC-039 | VarHandle | ★★★ |
| JCC-040 | Structured Concurrency | ★★★ |
| JCC-041 | Scoped Values | ★★★ |
| JCC-042 | Thread Dump Analysis | ★★★ |
| JCC-043 | Deadlock Detection (Java) | ★★★ |
| JCC-044 | Lock Striping | ★★★ |
| JCC-045 | Actor Model | ★★★ |
| JCC-046 | Concurrency Architecture Patterns in Java | ★★★ |
| JCC-047 | Virtual Thread Migration Strategy (Loom) | ★★★ |
| JCC-048 | Concurrent System Design at Scale | ★★★ |
| JCC-049 | Lock-Free Algorithm Strategy | ★★★ |
| JCC-050 | Thread Model Selection Framework | ★★★ |
| JCC-051 | Java Memory Model Specification Deep Dive | ★★★ |
| JCC-052 | Lock-Free Data Structure Design | ★★★ |
| JCC-053 | Concurrent Algorithm Research | ★★★ |
| JCC-054 | Structured Concurrency Design Principles | ★★★ |
| JCC-055 | Concurrency-First Thinking | ★★★ |
| JCC-056 | Shared State Risk Intuition | ★★★ |
| JCC-057 | Thread Safety Trade-off Framing | ★★★ |
| JCC-058 | ScheduledExecutorService | ★★☆ |
| JCC-059 | CompletableFuture Composition Patterns | ★★☆ |
| JCC-060 | Parallel Streams | ★★☆ |
| JCC-061 | Fork-Join Framework Pattern | ★★☆ |
| JCC-062 | Thread Interruption and Cancellation | ★★☆ |
| JCC-063 | CompletionService | ★★☆ |
| JCC-064 | Condition Interface (Lock Conditions) | ★★☆ |
| JCC-065 | Amdahl's Law | ★★★ |
| JCC-066 | Thread Pinning (Virtual Threads Problem) | ★★★ |
| JCC-067 | JMM Happens-Before - Deep Rules | ★★★ |
| JCC-068 | Lock-Free Data Structures | ★★★ |
| JCC-069 | Memory Visibility Diagnostics (jstack, JFR) | ★★★ |
| JCC-070 | False Sharing (Java Context) | ★★★ |
| JCC-071 | Busy-Wait vs Blocking | ★★★ |
| JCC-072 | JSR 133 - Java Memory Model Specification | ★★★ |
| JCC-073 | Project Loom Design Rationale | ★★★ |
| JCC-074 | Structured Concurrency Theory | ★★★ |
| JCC-075 | Reactive Streams Specification | ★★★ |
| JCC-076 | Actor Model Theory (Erlang / Akka Roots) | ★★★ |
| JCC-077 | Lock-Free Algorithm Theory (CAS Foundations) | ★★★ |
| JCC-078 | Daemon Threads | ★★☆ |
| JCC-079 | Thread Priority | ★★☆ |
| JCC-080 | ThreadFactory | ★★☆ |
| JCC-081 | Immutable Object Pattern | ★★☆ |
| JCC-082 | Producer-Consumer Pattern | ★★☆ |
| JCC-083 | Liveness Issues (Livelock / Starvation) | ★★☆ |
| JCC-084 | ABA Problem | ★★★ |
| JCC-085 | Work-Stealing Algorithm | ★★★ |
| JCC-086 | Thread Groups (Legacy) | ★☆☆ |
"@

$jccNew = @"
---
layout: default
title: "Java Concurrency"
parent: "Technical Dictionary"
nav_order: 9
has_children: true
permalink: /java-concurrency/
---

# Java Concurrency

Java threading, synchronization, concurrent data structures, executors, virtual threads, Project Loom, and the Java Memory Model.

$jccTable
"@
Write-File $jccIdx $jccNew
Write-Host "Rebuilt JCC index.md (86 entries)"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — REBUILD JLG index.md (full table from actual files + new)
# ─────────────────────────────────────────────────────────────────────────────
$jlgIdx = 'dictionary\tier-3-java\JLG-java-language\index.md'

$jlgTable = @"
**Keywords:** JLG-001--JLG-084 (84 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| JLG-001 | What Is Java - History and Philosophy | ★☆☆ |
| JLG-002 | The Java Ecosystem Map (SE, EE, ME, Android) | ★☆☆ |
| JLG-003 | Why Java Is Still Dominant | ★☆☆ |
| JLG-004 | Java vs Other JVM Languages (Kotlin, Scala, Groovy) | ★☆☆ |
| JLG-005 | Java Versioning and LTS Release Strategy | ★☆☆ |
| JLG-006 | Java EE / J2EE Overview | ★☆☆ |
| JLG-007 | JSP (Java Server Pages) | ★★☆ |
| JLG-008 | Java Servlet | ★★☆ |
| JLG-009 | Java Collections Deep Dive (List, Map, Set) | ★★☆ |
| JLG-010 | Java Exception Hierarchy (Checked vs Unchecked) | ★★☆ |
| JLG-011 | Java Keywords (static, final, volatile, synchronized, transient) | ★★☆ |
| JLG-012 | Java File IO and Serialization | ★★☆ |
| JLG-013 | Java Abstract Classes vs Interfaces | ★★☆ |
| JLG-014 | Java Access Modifiers | ★☆☆ |
| JLG-015 | Java Constructors Deep Dive | ★★☆ |
| JLG-016 | Java Memory Management (Stack vs Heap Practical) | ★★☆ |
| JLG-017 | Java 8 to Java 17 Migration Guide | ★★★ |
| JLG-018 | Java 17 Features (Records, Sealed, Pattern Matching) | ★★☆ |
| JLG-019 | Java Profiling (YourKit, JFR) | ★★★ |
| JLG-020 | Java Performance Tuning | ★★★ |
| JLG-021 | String Pool / String Interning | ★★☆ |
| JLG-022 | Autoboxing / Unboxing | ★★☆ |
| JLG-023 | Integer Cache | ★★★ |
| JLG-024 | Generics | ★★☆ |
| JLG-025 | Type Erasure | ★★★ |
| JLG-026 | Bounded Wildcards | ★★★ |
| JLG-027 | Covariance / Contravariance | ★★★ |
| JLG-028 | Varargs | ★★☆ |
| JLG-029 | Reflection | ★★★ |
| JLG-030 | Annotation Processing (APT) | ★★★ |
| JLG-031 | Serialization / Deserialization | ★★☆ |
| JLG-032 | Records (Java 16+) | ★★☆ |
| JLG-033 | Sealed Classes (Java 17+) | ★★★ |
| JLG-034 | Pattern Matching (Java 21+) | ★★★ |
| JLG-035 | invokedynamic | ★★★ |
| JLG-036 | Optional | ★★☆ |
| JLG-037 | Stream API | ★★☆ |
| JLG-038 | Functional Interfaces | ★★☆ |
| JLG-039 | Method References | ★★☆ |
| JLG-040 | Lambda Expressions | ★★☆ |
| JLG-041 | Java Version Migration Strategy (8 to 17 to 21) | ★★★ |
| JLG-042 | Java API Design at Scale | ★★★ |
| JLG-043 | Java Modularity Strategy (JPMS) | ★★★ |
| JLG-044 | Java Performance Profiling at Scale | ★★★ |
| JLG-045 | Java in Polyglot Architecture | ★★★ |
| JLG-046 | Java Language Specification Deep Dive | ★★★ |
| JLG-047 | Project Valhalla - Value Types and Primitives | ★★★ |
| JLG-048 | Project Panama - Foreign Function and Memory API | ★★★ |
| JLG-049 | Java Language Design History and Rationale | ★★★ |
| JLG-050 | Java API Design Thinking | ★★★ |
| JLG-051 | Language Feature Trade-off Framing | ★★★ |
| JLG-052 | Java Ecosystem Selection Framework | ★★★ |
| JLG-053 | Java Module System (JPMS, Java 9+) | ★★☆ |
| JLG-054 | Java Program Structure (class, method, main) | ★☆☆ |
| JLG-055 | Variables and Data Types in Java | ★☆☆ |
| JLG-056 | Control Flow (if/else, for, while) | ★☆☆ |
| JLG-057 | Java Arrays (Basics) | ★☆☆ |
| JLG-058 | Classes and Objects (Basics) | ★☆☆ |
| JLG-059 | Packages and Imports | ★☆☆ |
| JLG-060 | Java Standard Library Overview (java.lang, java.util) | ★☆☆ |
| JLG-061 | Inheritance and Polymorphism | ★☆☆ |
| JLG-062 | Primitive Types and Wrapper Classes | ★☆☆ |
| JLG-063 | Enums | ★★☆ |
| JLG-064 | String Methods (Common Operations) | ★★☆ |
| JLG-065 | Java DateTime API (java.time) | ★★☆ |
| JLG-066 | Try-with-Resources | ★★☆ |
| JLG-067 | Comparable vs Comparator | ★★☆ |
| JLG-068 | Iterators and Iterable | ★★☆ |
| JLG-069 | Java 8 Features Overview (streams, lambdas, Optional) | ★★☆ |
| JLG-070 | equals() and hashCode() Contract | ★★☆ |
| JLG-071 | instanceof and Type Casting | ★★☆ |
| JLG-072 | Text Blocks (Java 15+) | ★★☆ |
| JLG-073 | Switch Expressions (Java 14+) | ★★☆ |
| JLG-074 | Java Interfaces (Practical Usage) | ★★☆ |
| JLG-075 | Java NIO (Non-Blocking I/O) | ★★☆ |
| JLG-076 | MethodHandles | ★★★ |
| JLG-077 | Java Agents (java.lang.instrument) | ★★★ |
| JLG-078 | Class File Format (javap) | ★★★ |
| JLG-079 | JFR (Java Flight Recorder) Deep Dive | ★★★ |
| JLG-080 | Hidden Classes (Java 15+) | ★★★ |
| JLG-081 | java.util.concurrent.Flow (Reactive Java) | ★★★ |
| JLG-082 | String Deduplication (GC Feature) | ★★★ |
| JLG-083 | JEP (Java Enhancement Proposal) Process | ★★★ |
| JLG-084 | Project Amber Design Rationale | ★★★ |
"@

$jlgNew = @"
---
layout: default
title: "Java Language"
parent: "Technical Dictionary"
nav_order: 8
has_children: true
permalink: /java-language/
---

# Java Language

Java language fundamentals, collections, generics, reflection, modern features (records, sealed classes, pattern matching), functional APIs, and creator-level language specification.

$jlgTable
"@
Write-File $jlgIdx $jlgNew
Write-Host "Rebuilt JLG index.md (84 entries)"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — REBUILD SPR index.md (full table from actual files + new)
# ─────────────────────────────────────────────────────────────────────────────
$sprIdx = 'dictionary\tier-3-java\SPR-spring-core\index.md'

$sprTable = @"
**Keywords:** SPR-001--SPR-098 (98 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| SPR-001 | What Is Spring - History and Philosophy | ★☆☆ |
| SPR-002 | The Spring Ecosystem Map | ★☆☆ |
| SPR-003 | Why Spring Boot Changed Java Development | ★☆☆ |
| SPR-004 | Spring vs Jakarta EE vs Micronaut vs Quarkus | ★☆☆ |
| SPR-005 | Spring in Production - What to Expect | ★☆☆ |
| SPR-006 | Spring Batch | ★★★ |
| SPR-007 | Spring Batch Job / Step / Tasklet | ★★★ |
| SPR-008 | Spring Batch ItemReader / ItemProcessor / ItemWriter | ★★★ |
| SPR-009 | Spring Batch Chunk Processing | ★★★ |
| SPR-010 | Spring Cloud Overview | ★★★ |
| SPR-011 | Spring Cloud Config | ★★★ |
| SPR-012 | Spring Cloud Gateway | ★★★ |
| SPR-013 | Spring Cloud Service Discovery (Eureka) | ★★★ |
| SPR-014 | Spring Cloud Load Balancer | ★★★ |
| SPR-015 | Spring Cloud Circuit Breaker | ★★★ |
| SPR-016 | Micronaut Framework | ★★★ |
| SPR-017 | Micronaut vs Spring Boot | ★★★ |
| SPR-018 | Quarkus Framework | ★★★ |
| SPR-019 | IoC (Inversion of Control) | ★☆☆ |
| SPR-020 | DI (Dependency Injection) | ★☆☆ |
| SPR-021 | ApplicationContext | ★★☆ |
| SPR-022 | BeanFactory | ★★☆ |
| SPR-023 | Bean | ★☆☆ |
| SPR-024 | Bean Lifecycle | ★★☆ |
| SPR-025 | Bean Scope | ★★☆ |
| SPR-026 | BeanPostProcessor | ★★★ |
| SPR-027 | BeanFactoryPostProcessor | ★★★ |
| SPR-028 | @Autowired | ★★☆ |
| SPR-029 | @Qualifier / @Primary | ★★☆ |
| SPR-030 | @Configuration / @Bean | ★★☆ |
| SPR-031 | Circular Dependency | ★★★ |
| SPR-032 | CGLIB Proxy | ★★★ |
| SPR-033 | JDK Dynamic Proxy | ★★★ |
| SPR-034 | AOP (Aspect-Oriented Programming) | ★★☆ |
| SPR-035 | Aspect | ★★☆ |
| SPR-036 | Advice | ★★☆ |
| SPR-037 | Pointcut | ★★☆ |
| SPR-038 | JoinPoint | ★★☆ |
| SPR-039 | Weaving | ★★★ |
| SPR-040 | DispatcherServlet | ★★☆ |
| SPR-041 | HandlerMapping | ★★★ |
| SPR-042 | Filter vs Interceptor | ★★☆ |
| SPR-043 | @Transactional | ★★☆ |
| SPR-044 | Transaction Propagation | ★★★ |
| SPR-045 | Transaction Isolation Levels | ★★★ |
| SPR-046 | N+1 Problem | ★★★ |
| SPR-047 | Lazy vs Eager Loading | ★★☆ |
| SPR-048 | HikariCP | ★★☆ |
| SPR-049 | Auto-Configuration | ★★★ |
| SPR-050 | Spring Boot Actuator | ★★☆ |
| SPR-051 | Spring Boot Startup Lifecycle | ★★★ |
| SPR-052 | WebFlux / Reactive | ★★★ |
| SPR-053 | Mono / Flux | ★★★ |
| SPR-054 | Backpressure (Spring) | ★★★ |
| SPR-055 | Spring Security | ★★★ |
| SPR-056 | Spring Data JPA | ★★☆ |
| SPR-057 | Spring Cloud | ★★★ |
| SPR-058 | Spring Boot Testing | ★★☆ |
| SPR-059 | Spring Architecture at Scale | ★★★ |
| SPR-060 | Spring Migration Strategy (MVC to WebFlux) | ★★★ |
| SPR-061 | Spring Boot Configuration Strategy | ★★★ |
| SPR-062 | Spring Security Architecture Design | ★★★ |
| SPR-063 | Microservice Decomposition with Spring Cloud | ★★★ |
| SPR-064 | Spring Framework Internals Deep Dive | ★★★ |
| SPR-065 | Spring Reactive Model (Project Reactor Internals) | ★★★ |
| SPR-066 | Spring Native and GraalVM Integration | ★★★ |
| SPR-067 | Spring Specification and Extension Points | ★★★ |
| SPR-068 | IoC-First Thinking | ★★★ |
| SPR-069 | Spring Configuration Trade-off Framing | ★★★ |
| SPR-070 | Framework Selection Mental Model | ★★★ |
| SPR-071 | @Component / @Service / @Repository | ★☆☆ |
| SPR-072 | @SpringBootApplication | ★☆☆ |
| SPR-073 | @RestController / @Controller | ★★☆ |
| SPR-074 | @RequestMapping / @GetMapping / @PostMapping | ★★☆ |
| SPR-075 | @RequestBody / @ResponseBody | ★★☆ |
| SPR-076 | @PathVariable / @RequestParam | ★★☆ |
| SPR-077 | Spring Profiles (@Profile, application.yml) | ★★☆ |
| SPR-078 | Spring Validation (@Valid, @NotNull) | ★★☆ |
| SPR-079 | Exception Handling (@ExceptionHandler, @ControllerAdvice) | ★★☆ |
| SPR-080 | Spring Cache Abstraction (@Cacheable) | ★★☆ |
| SPR-081 | Spring Events (ApplicationEvent, @EventListener) | ★★☆ |
| SPR-082 | Conditional Beans (@ConditionalOnProperty) | ★★☆ |
| SPR-083 | ResponseEntity and HTTP Status Handling | ★★☆ |
| SPR-084 | Spring Boot DevTools | ★☆☆ |
| SPR-085 | Spring Retry | ★★☆ |
| SPR-086 | MockMvc | ★★☆ |
| SPR-087 | @MockBean / @SpyBean | ★★☆ |
| SPR-088 | Spring Context Refresh (AbstractApplicationContext) | ★★★ |
| SPR-089 | Bean Definition Registry | ★★★ |
| SPR-090 | Spring Boot AOT Compilation (Spring 6) | ★★★ |
| SPR-091 | Spring + Virtual Threads (Spring 6.1) | ★★★ |
| SPR-092 | Spring Security OAuth2 Resource Server | ★★★ |
| SPR-093 | Spring Data REST | ★★★ |
| SPR-094 | Spring Native Image Support | ★★★ |
| SPR-095 | Spring Framework Design Rationale | ★★★ |
| SPR-096 | Project Reactor Design (Reactive Streams Spec) | ★★★ |
| SPR-097 | Spring Boot Auto-Configuration Algorithm | ★★★ |
| SPR-098 | Spring Test Context Management | ★★★ |
"@

$sprNew = @"
---
layout: default
title: "Spring Core"
parent: "Technical Dictionary"
nav_order: 10
has_children: true
permalink: /spring/
---

# Spring Core

Spring IoC/DI, AOP, MVC, transactions, data access, reactive programming, Spring Boot, Spring Security, Spring Batch, Spring Cloud, and creator-level framework design theory.

> **Note:** SPR-005 (Spring in Production) and SPR-057 (Spring Cloud) provide entry-level and working-level views respectively of Spring Cloud integration.

$sprTable
"@
Write-File $sprIdx $sprNew
Write-Host "Rebuilt SPR index.md (98 entries)"

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n=== COMPLETE ==="
Write-Host "JVM: 9 new stubs (JVM-067 to JVM-075), index updated to 75 terms"
Write-Host "JCC: 9 new stubs (JCC-078 to JCC-086), index rebuilt to 86 terms"
Write-Host "JLG: 31 new stubs (JLG-054 to JLG-084), index rebuilt to 84 terms"
Write-Host "SPR: 28 new stubs (SPR-071 to SPR-098), index rebuilt to 98 terms"
Write-Host "Total new stub files: 77"
