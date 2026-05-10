# create_tier3_jph_and_gaps.ps1
# Creates JPH (JPA & Hibernate) category + fills gaps in JLG and JCC.
# Run with: pwsh -ExecutionPolicy Bypass -File tmp\create_tier3_jph_and_gaps.ps1

Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Write-File($path, $content) {
    [System.IO.File]::WriteAllText($path, $content, $enc)
}

function New-Stub {
    param($base, $id, $title, $cat, $tier, $folder, $diff, $parent, $tagLines, $slug, $dep='', $usedBy='', $rel='')
    $safeTitle = $title -replace '/', '' -replace '\*', '' -replace '\?', '' -replace '<', '' -replace '>', '' -replace '\\', '' -replace '\|', '' -replace '"', ''
    $fname = Join-Path $base "$id - $safeTitle.md"
    if (Test-Path $fname) { Write-Host "SKIP (exists): $id"; return }
    $yTitle = if ($title -match ': ') { "`"$title`"" } else { $title }
    $navOrder = [int]($id -replace '[A-Z]+-0*', '')
    $content = @"
---
id: $id
title: $yTitle
category: $cat
tier: $tier
folder: $folder
difficulty: $diff
depends_on: $dep
used_by: $usedBy
related: $rel
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

# =============================================================================
# PART 1 — CREATE JPH (JPA & Hibernate) CATEGORY
# =============================================================================
$jphDir  = 'dictionary\tier-3-java\JPH-jpa-hibernate'
$jphCat  = 'JPA & Hibernate'
$jphTier = 'tier-3-java'
$jphFld  = 'JPH-jpa-hibernate'
$jphPar  = 'JPA & Hibernate'

New-Item -ItemType Directory -Path $jphDir -Force | Out-Null
Write-Host "Created folder: $jphDir"

# Tag sets
$t0  = "  - java`n  - database`n  - foundational`n  - mental-model"
$t1  = "  - java`n  - database`n  - jpa`n  - foundational"
$t2  = "  - java`n  - jpa`n  - database`n  - intermediate"
$t3  = "  - java`n  - jpa`n  - hibernate`n  - advanced`n  - deep-dive"
$t3s = "  - java`n  - spring`n  - jpa`n  - advanced"

$jphKeywords = @(
    # L0 - Orientation (5)
    @{id='JPH-001';title='The Object-Relational Mismatch Problem';         diff='★☆☆';slug='/jpa-hibernate/object-relational-mismatch/';      tags=$t0},
    @{id='JPH-002';title='What is ORM (Object-Relational Mapping)';        diff='★☆☆';slug='/jpa-hibernate/what-is-orm/';                     tags=$t0},
    @{id='JPH-003';title='JPA vs JDBC - Why ORM Exists';                   diff='★☆☆';slug='/jpa-hibernate/jpa-vs-jdbc/';                     tags=$t0},
    @{id='JPH-004';title='Hibernate as JPA Implementation';                diff='★☆☆';slug='/jpa-hibernate/hibernate-as-jpa-implementation/';  tags=$t0},
    @{id='JPH-005';title='JPA Ecosystem Map (Hibernate, EclipseLink, MyBatis)';diff='★☆☆';slug='/jpa-hibernate/jpa-ecosystem-map/';           tags=$t0},
    # L1 - Foundational (10)
    @{id='JPH-006';title='@Entity';                                         diff='★☆☆';slug='/jpa-hibernate/entity-annotation/';               tags=$t1},
    @{id='JPH-007';title='@Id and @GeneratedValue';                         diff='★☆☆';slug='/jpa-hibernate/id-generatedvalue/';               tags=$t1},
    @{id='JPH-008';title='@Table and @Column';                              diff='★☆☆';slug='/jpa-hibernate/table-column-annotations/';        tags=$t1},
    @{id='JPH-009';title='EntityManager';                                   diff='★★☆';slug='/jpa-hibernate/entity-manager/';                  tags=$t1},
    @{id='JPH-010';title='Persistence Context';                             diff='★★☆';slug='/jpa-hibernate/persistence-context/';             tags=$t1},
    @{id='JPH-011';title='Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)';diff='★★☆';slug='/jpa-hibernate/entity-lifecycle/';            tags=$t1},
    @{id='JPH-012';title='JPA Configuration (persistence.xml, application.properties)';diff='★☆☆';slug='/jpa-hibernate/jpa-configuration/';  tags=$t1},
    @{id='JPH-013';title='JPQL (Java Persistence Query Language)';          diff='★★☆';slug='/jpa-hibernate/jpql/';                           tags=$t1},
    @{id='JPH-014';title='Spring Data JPA Repository';                      diff='★★☆';slug='/jpa-hibernate/spring-data-jpa-repository/';     tags=$t1},
    @{id='JPH-015';title='CrudRepository and JpaRepository';               diff='★★☆';slug='/jpa-hibernate/crudrepository-jparepository/';   tags=$t1},
    # L2 - Working (15)
    @{id='JPH-016';title='@OneToOne';                                       diff='★★☆';slug='/jpa-hibernate/onetoone/';                        tags=$t2},
    @{id='JPH-017';title='@OneToMany and @ManyToOne';                       diff='★★☆';slug='/jpa-hibernate/onetomany-manytoone/';             tags=$t2},
    @{id='JPH-018';title='@ManyToMany';                                     diff='★★☆';slug='/jpa-hibernate/manytomany/';                      tags=$t2},
    @{id='JPH-019';title='@JoinColumn and @JoinTable';                      diff='★★☆';slug='/jpa-hibernate/joincolumn-jointable/';            tags=$t2},
    @{id='JPH-020';title='FetchType (LAZY vs EAGER)';                       diff='★★☆';slug='/jpa-hibernate/fetchtype-lazy-eager/';            tags=$t2},
    @{id='JPH-021';title='CascadeType';                                     diff='★★☆';slug='/jpa-hibernate/cascadetype/';                     tags=$t2},
    @{id='JPH-022';title='@Query (Spring Data JPA)';                        diff='★★☆';slug='/jpa-hibernate/query-annotation/';                tags=$t2},
    @{id='JPH-023';title='Derived Query Methods (findBy, countBy)';         diff='★★☆';slug='/jpa-hibernate/derived-query-methods/';           tags=$t2},
    @{id='JPH-024';title='Pagination and Sorting (Pageable, Sort)';         diff='★★☆';slug='/jpa-hibernate/pagination-sorting/';              tags=$t2},
    @{id='JPH-025';title='@Transactional with JPA';                         diff='★★☆';slug='/jpa-hibernate/transactional-with-jpa/';          tags=$t2},
    @{id='JPH-026';title='N+1 Problem (ORM Context)';                       diff='★★☆';slug='/jpa-hibernate/n-plus-1-problem/';                tags=$t2},
    @{id='JPH-027';title='HQL (Hibernate Query Language)';                  diff='★★☆';slug='/jpa-hibernate/hql/';                             tags=$t2},
    @{id='JPH-028';title='@NamedQuery and Native Queries';                  diff='★★☆';slug='/jpa-hibernate/named-native-queries/';            tags=$t2},
    @{id='JPH-029';title='DTO Projections in Spring Data JPA';              diff='★★☆';slug='/jpa-hibernate/dto-projections/';                 tags=$t2},
    @{id='JPH-030';title='Hibernate Session vs EntityManager';              diff='★★☆';slug='/jpa-hibernate/session-vs-entitymanager/';        tags=$t2},
    # L3 - Intermediate (12)
    @{id='JPH-031';title='First Level Cache (Persistence Context Cache)';   diff='★★★';slug='/jpa-hibernate/first-level-cache/';               tags=$t3},
    @{id='JPH-032';title='Second Level Cache (Ehcache, Redis)';             diff='★★★';slug='/jpa-hibernate/second-level-cache/';              tags=$t3},
    @{id='JPH-033';title='Query Cache';                                     diff='★★★';slug='/jpa-hibernate/query-cache/';                     tags=$t3},
    @{id='JPH-034';title='Criteria API';                                    diff='★★★';slug='/jpa-hibernate/criteria-api/';                    tags=$t3},
    @{id='JPH-035';title='EntityGraph (Solving N+1)';                       diff='★★★';slug='/jpa-hibernate/entity-graph/';                    tags=$t3},
    @{id='JPH-036';title='Optimistic Locking (@Version)';                   diff='★★★';slug='/jpa-hibernate/optimistic-locking/';              tags=$t3},
    @{id='JPH-037';title='Pessimistic Locking (LockModeType)';              diff='★★★';slug='/jpa-hibernate/pessimistic-locking/';             tags=$t3},
    @{id='JPH-038';title='Inheritance Mapping Strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS)';diff='★★★';slug='/jpa-hibernate/inheritance-mapping/'; tags=$t3},
    @{id='JPH-039';title='@Embedded and @Embeddable';                       diff='★★★';slug='/jpa-hibernate/embedded-embeddable/';             tags=$t3},
    @{id='JPH-040';title='@ElementCollection';                              diff='★★★';slug='/jpa-hibernate/element-collection/';              tags=$t3},
    @{id='JPH-041';title='Spring Data Specifications';                      diff='★★★';slug='/jpa-hibernate/spring-data-specifications/';      tags=$t3s},
    @{id='JPH-042';title='Hibernate Validator (Bean Validation)';           diff='★★★';slug='/jpa-hibernate/hibernate-validator/';             tags=$t3},
    # L4 - Expert (9)
    @{id='JPH-043';title='Hibernate Batch Processing';                      diff='★★★';slug='/jpa-hibernate/hibernate-batch-processing/';      tags=$t3},
    @{id='JPH-044';title='Hibernate Statistics and Monitoring';             diff='★★★';slug='/jpa-hibernate/hibernate-statistics/';            tags=$t3},
    @{id='JPH-045';title='Connection Pooling with JPA (HikariCP)';         diff='★★★';slug='/jpa-hibernate/connection-pooling-jpa/';          tags=$t3},
    @{id='JPH-046';title='Multi-Tenancy in JPA and Hibernate';             diff='★★★';slug='/jpa-hibernate/multi-tenancy/';                   tags=$t3},
    @{id='JPH-047';title='Hibernate Envers (Auditing and History)';         diff='★★★';slug='/jpa-hibernate/hibernate-envers/';                tags=$t3},
    @{id='JPH-048';title='Hibernate vs MyBatis vs JOOQ';                   diff='★★★';slug='/jpa-hibernate/hibernate-vs-mybatis-jooq/';       tags=$t3},
    @{id='JPH-049';title='@Converter and AttributeConverter';               diff='★★★';slug='/jpa-hibernate/attribute-converter/';             tags=$t3},
    @{id='JPH-050';title='Dirty Checking and Flush Mode';                   diff='★★★';slug='/jpa-hibernate/dirty-checking-flush/';            tags=$t3},
    @{id='JPH-051';title='QueryDSL with JPA';                               diff='★★★';slug='/jpa-hibernate/querydsl/';                        tags=$t3s},
    # L4.5 - Architect (3)
    @{id='JPH-052';title='JPA at Scale - Architecture Patterns';            diff='★★★';slug='/jpa-hibernate/jpa-at-scale/';                    tags=$t3},
    @{id='JPH-053';title='ORM Selection Framework';                         diff='★★★';slug='/jpa-hibernate/orm-selection-framework/';         tags=$t3},
    @{id='JPH-054';title='Spring Data JPA Architecture Design';             diff='★★★';slug='/jpa-hibernate/spring-data-jpa-architecture/';   tags=$t3s},
    # L5 - Creator (2)
    @{id='JPH-055';title='JPA Specification (JSR 338 / Jakarta Persistence)';diff='★★★';slug='/jpa-hibernate/jpa-specification/';            tags=$t3},
    @{id='JPH-056';title='Hibernate Internals Deep Dive';                   diff='★★★';slug='/jpa-hibernate/hibernate-internals/';             tags=$t3}
)

foreach ($kw in $jphKeywords) {
    New-Stub $jphDir $kw.id $kw.title $jphCat $jphTier $jphFld $kw.diff $jphPar $kw.tags $kw.slug
}

# =============================================================================
# PART 2 — JPH index.md
# =============================================================================
$jphIdx = @"
---
layout: default
title: "JPA & Hibernate"
parent: "Technical Dictionary"
nav_order: 11
has_children: true
permalink: /jpa-hibernate/
---

# JPA & Hibernate

JPA specification, Hibernate ORM, Spring Data JPA, entity mapping, relationships, caching, locking, query APIs, and production-grade ORM architecture patterns.

**Keywords:** JPH-001--JPH-056 (56 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| JPH-001 | The Object-Relational Mismatch Problem | ★☆☆ |
| JPH-002 | What is ORM (Object-Relational Mapping) | ★☆☆ |
| JPH-003 | JPA vs JDBC - Why ORM Exists | ★☆☆ |
| JPH-004 | Hibernate as JPA Implementation | ★☆☆ |
| JPH-005 | JPA Ecosystem Map (Hibernate, EclipseLink, MyBatis) | ★☆☆ |
| JPH-006 | @Entity | ★☆☆ |
| JPH-007 | @Id and @GeneratedValue | ★☆☆ |
| JPH-008 | @Table and @Column | ★☆☆ |
| JPH-009 | EntityManager | ★★☆ |
| JPH-010 | Persistence Context | ★★☆ |
| JPH-011 | Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED) | ★★☆ |
| JPH-012 | JPA Configuration (persistence.xml, application.properties) | ★☆☆ |
| JPH-013 | JPQL (Java Persistence Query Language) | ★★☆ |
| JPH-014 | Spring Data JPA Repository | ★★☆ |
| JPH-015 | CrudRepository and JpaRepository | ★★☆ |
| JPH-016 | @OneToOne | ★★☆ |
| JPH-017 | @OneToMany and @ManyToOne | ★★☆ |
| JPH-018 | @ManyToMany | ★★☆ |
| JPH-019 | @JoinColumn and @JoinTable | ★★☆ |
| JPH-020 | FetchType (LAZY vs EAGER) | ★★☆ |
| JPH-021 | CascadeType | ★★☆ |
| JPH-022 | @Query (Spring Data JPA) | ★★☆ |
| JPH-023 | Derived Query Methods (findBy, countBy) | ★★☆ |
| JPH-024 | Pagination and Sorting (Pageable, Sort) | ★★☆ |
| JPH-025 | @Transactional with JPA | ★★☆ |
| JPH-026 | N+1 Problem (ORM Context) | ★★☆ |
| JPH-027 | HQL (Hibernate Query Language) | ★★☆ |
| JPH-028 | @NamedQuery and Native Queries | ★★☆ |
| JPH-029 | DTO Projections in Spring Data JPA | ★★☆ |
| JPH-030 | Hibernate Session vs EntityManager | ★★☆ |
| JPH-031 | First Level Cache (Persistence Context Cache) | ★★★ |
| JPH-032 | Second Level Cache (Ehcache, Redis) | ★★★ |
| JPH-033 | Query Cache | ★★★ |
| JPH-034 | Criteria API | ★★★ |
| JPH-035 | EntityGraph (Solving N+1) | ★★★ |
| JPH-036 | Optimistic Locking (@Version) | ★★★ |
| JPH-037 | Pessimistic Locking (LockModeType) | ★★★ |
| JPH-038 | Inheritance Mapping Strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS) | ★★★ |
| JPH-039 | @Embedded and @Embeddable | ★★★ |
| JPH-040 | @ElementCollection | ★★★ |
| JPH-041 | Spring Data Specifications | ★★★ |
| JPH-042 | Hibernate Validator (Bean Validation) | ★★★ |
| JPH-043 | Hibernate Batch Processing | ★★★ |
| JPH-044 | Hibernate Statistics and Monitoring | ★★★ |
| JPH-045 | Connection Pooling with JPA (HikariCP) | ★★★ |
| JPH-046 | Multi-Tenancy in JPA and Hibernate | ★★★ |
| JPH-047 | Hibernate Envers (Auditing and History) | ★★★ |
| JPH-048 | Hibernate vs MyBatis vs JOOQ | ★★★ |
| JPH-049 | @Converter and AttributeConverter | ★★★ |
| JPH-050 | Dirty Checking and Flush Mode | ★★★ |
| JPH-051 | QueryDSL with JPA | ★★★ |
| JPH-052 | JPA at Scale - Architecture Patterns | ★★★ |
| JPH-053 | ORM Selection Framework | ★★★ |
| JPH-054 | Spring Data JPA Architecture Design | ★★★ |
| JPH-055 | JPA Specification (JSR 338 / Jakarta Persistence) | ★★★ |
| JPH-056 | Hibernate Internals Deep Dive | ★★★ |
"@
Write-File 'dictionary\tier-3-java\JPH-jpa-hibernate\index.md' $jphIdx
Write-Host "Created JPH index.md (56 entries)"

# =============================================================================
# PART 3 — NEW JLG KEYWORDS (JLG-085 to JLG-094)
# Socket programming, OOP gaps, networking, utility gaps
# =============================================================================
$jlgBase = 'dictionary\tier-3-java\JLG-java-language'
$jlgCat  = 'Java Language'
$jlgTier = 'tier-3-java'
$jlgFld  = 'JLG-java-language'
$jlgPar  = 'Java Language'

$jlgNew = @(
    @{id='JLG-085';title='Java Socket API (Socket, ServerSocket)';              diff='★★☆';slug='/java-language/java-socket-api/';              tags="  - java`n  - networking`n  - intermediate`n  - protocol"},
    @{id='JLG-086';title='UDP Sockets (DatagramSocket, DatagramPacket)';        diff='★★★';slug='/java-language/udp-sockets/';                  tags="  - java`n  - networking`n  - advanced`n  - protocol"},
    @{id='JLG-087';title='Java NIO Channels (SocketChannel, Selector)';         diff='★★★';slug='/java-language/java-nio-channels/';             tags="  - java`n  - networking`n  - advanced`n  - async"},
    @{id='JLG-088';title='Java HttpClient (java.net.http, Java 11+)';           diff='★★☆';slug='/java-language/java-httpclient/';               tags="  - java`n  - networking`n  - intermediate`n  - api"},
    @{id='JLG-089';title='Nested Classes, Inner Classes, Anonymous Classes';    diff='★★☆';slug='/java-language/nested-inner-anonymous-classes/'; tags="  - java`n  - language`n  - intermediate`n  - oop"},
    @{id='JLG-090';title='Method Overloading vs Overriding';                    diff='★☆☆';slug='/java-language/overloading-vs-overriding/';     tags="  - java`n  - language`n  - foundational`n  - oop"},
    @{id='JLG-091';title='StringBuilder and StringBuffer';                      diff='★★☆';slug='/java-language/stringbuilder-stringbuffer/';    tags="  - java`n  - language`n  - intermediate`n  - performance"},
    @{id='JLG-092';title='Java Logging (SLF4J, Logback, java.util.logging)';   diff='★★☆';slug='/java-language/java-logging/';                  tags="  - java`n  - language`n  - intermediate`n  - observability"},
    @{id='JLG-093';title='Regular Expressions in Java (java.util.regex)';       diff='★★☆';slug='/java-language/java-regex/';                    tags="  - java`n  - language`n  - intermediate"},
    @{id='JLG-094';title='Object Cloning (Cloneable, copy constructors)';       diff='★★★';slug='/java-language/object-cloning/';                tags="  - java`n  - language`n  - advanced`n  - pattern"}
)

foreach ($kw in $jlgNew) {
    New-Stub $jlgBase $kw.id $kw.title $jlgCat $jlgTier $jlgFld $kw.diff $jlgPar $kw.tags $kw.slug
}

# Update JLG index.md - append new rows + update count
$jlgIdx = 'dictionary\tier-3-java\JLG-java-language\index.md'
$jlgContent = [System.IO.File]::ReadAllText($jlgIdx)
$jlgContent = $jlgContent -replace '\*\*Keywords:\*\*.*?\(84 terms\)', '**Keywords:** JLG-001--JLG-094 (94 terms)'
$jlgNewRows = @"
| JLG-085 | Java Socket API (Socket, ServerSocket) | ★★☆ |
| JLG-086 | UDP Sockets (DatagramSocket, DatagramPacket) | ★★★ |
| JLG-087 | Java NIO Channels (SocketChannel, Selector) | ★★★ |
| JLG-088 | Java HttpClient (java.net.http, Java 11+) | ★★☆ |
| JLG-089 | Nested Classes, Inner Classes, Anonymous Classes | ★★☆ |
| JLG-090 | Method Overloading vs Overriding | ★☆☆ |
| JLG-091 | StringBuilder and StringBuffer | ★★☆ |
| JLG-092 | Java Logging (SLF4J, Logback, java.util.logging) | ★★☆ |
| JLG-093 | Regular Expressions in Java (java.util.regex) | ★★☆ |
| JLG-094 | Object Cloning (Cloneable, copy constructors) | ★★★ |
"@
$jlgContent = $jlgContent.TrimEnd() + "`n" + $jlgNewRows.TrimStart()
Write-File $jlgIdx $jlgContent
Write-Host "Updated JLG index.md (94 entries)"

# =============================================================================
# PART 4 — NEW JCC KEYWORDS (JCC-087 to JCC-092)
# Remaining multithreading / concurrency gaps
# =============================================================================
$jccBase = 'dictionary\tier-3-java\JCC-java-concurrency'
$jccCat  = 'Java Concurrency'
$jccTier = 'tier-3-java'
$jccFld  = 'JCC-java-concurrency'
$jccPar  = 'Java Concurrency'

$jccNew = @(
    @{id='JCC-087';title='Double-Checked Locking Pattern';                   diff='★★★';slug='/java-concurrency/double-checked-locking/';      tags="  - java`n  - concurrency`n  - pattern`n  - advanced"},
    @{id='JCC-088';title='ExecutorService Rejection Policies';               diff='★★★';slug='/java-concurrency/rejection-policies/';           tags="  - java`n  - concurrency`n  - advanced`n  - production"},
    @{id='JCC-089';title='Concurrent Queue Variants (LinkedBlockingQueue, SynchronousQueue, DelayQueue)';diff='★★☆';slug='/java-concurrency/concurrent-queue-variants/'; tags="  - java`n  - concurrency`n  - intermediate`n  - datastructure"},
    @{id='JCC-090';title='Thread Safety Annotations (@GuardedBy, @ThreadSafe)';diff='★★☆';slug='/java-concurrency/thread-safety-annotations/';  tags="  - java`n  - concurrency`n  - intermediate`n  - bestpractice"},
    @{id='JCC-091';title='synchronized Block vs synchronized Method';        diff='★★☆';slug='/java-concurrency/synchronized-block-vs-method/'; tags="  - java`n  - concurrency`n  - intermediate`n  - foundational"},
    @{id='JCC-092';title='Java Reactive Programming (RxJava)';               diff='★★★';slug='/java-concurrency/rxjava/';                       tags="  - java`n  - concurrency`n  - advanced`n  - async`n  - streaming"}
)

foreach ($kw in $jccNew) {
    New-Stub $jccBase $kw.id $kw.title $jccCat $jccTier $jccFld $kw.diff $jccPar $kw.tags $kw.slug
}

# Update JCC index.md - append new rows + update count
$jccIdx = 'dictionary\tier-3-java\JCC-java-concurrency\index.md'
$jccContent = [System.IO.File]::ReadAllText($jccIdx)
$jccContent = $jccContent -replace '\*\*Keywords:\*\*.*?\(86 terms\)', '**Keywords:** JCC-001--JCC-092 (92 terms)'
$jccNewRows = @"
| JCC-087 | Double-Checked Locking Pattern | ★★★ |
| JCC-088 | ExecutorService Rejection Policies | ★★★ |
| JCC-089 | Concurrent Queue Variants (LinkedBlockingQueue, SynchronousQueue, DelayQueue) | ★★☆ |
| JCC-090 | Thread Safety Annotations (@GuardedBy, @ThreadSafe) | ★★☆ |
| JCC-091 | synchronized Block vs synchronized Method | ★★☆ |
| JCC-092 | Java Reactive Programming (RxJava) | ★★★ |
"@
$jccContent = $jccContent.TrimEnd() + "`n" + $jccNewRows.TrimStart()
Write-File $jccIdx $jccContent
Write-Host "Updated JCC index.md (92 entries)"

# =============================================================================
# SUMMARY
# =============================================================================
Write-Host "`n=== COMPLETE ==="
Write-Host "JPH (JPA & Hibernate): NEW category with 56 stubs created"
Write-Host "JLG: 10 new stubs (JLG-085 to JLG-094) - socket/networking/OOP gaps"
Write-Host "JCC:  6 new stubs (JCC-087 to JCC-092) - concurrency/multithreading gaps"
Write-Host "Total new stub files: 72"
