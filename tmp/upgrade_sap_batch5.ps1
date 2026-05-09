$d = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SAP-software-architecture"

# ── Helper: remove Entry Metadata block ──────────────────────────────
function Remove-EntryMetadata($c) {
    [regex]::Replace($c,
        "\r?\n---\r?\n\r?\n### [^\r\n]*Entry Metadata[\s\S]*?---\r?\n",
        "`n---`n")
}

# ── Helper: insert Field/Value table after TL;DR line ─────────────────
function Insert-FieldTable($c, $table) {
    [regex]::Replace($c, "(⚡ TL;DR - [^\r\n]+)(\r?\n)", "`$1`$2`n$table`n")
}

# ══════════════════════════════════════════════════════════════
# SAP-046 – YAGNI
# ══════════════════════════════════════════════════════════════
$fp = "$d\SAP-046 - YAGNI (You Aren't Gonna Need It).md"
$c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

# YAML
$oldYAML = @"
---
layout: default
title: "YAGNI (You Aren't Gonna Need It)"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /software-architecture/yagni/
id: SAP-046
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Agile Development, KISS, Refactoring, Technical Debt
used_by: All development, Feature planning, Architecture decisions
related: KISS, DRY, SOLID Principles, Technical Debt, Agile
tags:
  - architecture
  - principles
  - agile
  - intermediate
  - design
---
"@
$newYAML = @"
---
id: SAP-046
title: "YAGNI (You Aren't Gonna Need It)"
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-043, SAP-045
used_by:
related: SAP-043, SAP-044, SAP-045
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /software-architecture/yagni/
---
"@
$c = $c.Replace($oldYAML, $newYAML)

# Remove Entry Metadata
$c = Remove-EntryMetadata $c

# Field/Value table
$table = @"

| Field | Value |
|---|---|
| **ID** | SAP-046 |
| **Depends on** | SAP-043 - SOLID Principles, SAP-045 - KISS |
| **Used by** | - |
| **Related** | SAP-043, SAP-044 - DRY, SAP-045 - KISS |
"@
$c = Insert-FieldTable $c $table

[IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
Write-Host "SAP-046: YAML + Entry Metadata done"

# ══════════════════════════════════════════════════════════════
# SAP-047 – Law of Demeter
# ══════════════════════════════════════════════════════════════
$fp = "$d\SAP-047 - Law of Demeter.md"
$c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

$oldYAML = @"
---
layout: default
title: "Law of Demeter"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /software-architecture/law-of-demeter/
id: SAP-047
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming, Coupling, Encapsulation
used_by: OO design, API design, Code review, Refactoring
related: Tell Don't Ask, Encapsulation, Coupling, SOLID Principles
tags:
  - architecture
  - principles
  - oop
  - intermediate
  - coupling
---
"@
$newYAML = @"
---
id: SAP-047
title: Law of Demeter
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-043, SAP-051
used_by:
related: SAP-043, SAP-048, SAP-051
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /software-architecture/law-of-demeter/
---
"@
$c = $c.Replace($oldYAML, $newYAML)
$c = Remove-EntryMetadata $c
$table = @"

| Field | Value |
|---|---|
| **ID** | SAP-047 |
| **Depends on** | SAP-043 - SOLID Principles, SAP-051 - Coupling |
| **Used by** | - |
| **Related** | SAP-043, SAP-048 - Tell Don't Ask, SAP-051 - Coupling |
"@
$c = Insert-FieldTable $c $table
[IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
Write-Host "SAP-047: YAML + Entry Metadata done"

# ══════════════════════════════════════════════════════════════
# SAP-048 – Tell Don't Ask
# ══════════════════════════════════════════════════════════════
$fp = "$d\SAP-048 - Tell Don't Ask.md"
$c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

$oldYAML = @"
---
layout: default
title: "Tell Don't Ask"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /software-architecture/tell-dont-ask/
id: SAP-048
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming, Encapsulation, Law of Demeter
used_by: OO design, Domain Model design, Code review
related: Law of Demeter, Encapsulation, Anemic Domain Model, Command Pattern
tags:
  - architecture
  - principles
  - oop
  - intermediate
  - design
---
"@
$newYAML = @"
---
id: SAP-048
title: Tell Don't Ask
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-043, SAP-047
used_by:
related: SAP-047, SAP-049
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /software-architecture/tell-dont-ask/
---
"@
$c = $c.Replace($oldYAML, $newYAML)
$c = Remove-EntryMetadata $c
$table = @"

| Field | Value |
|---|---|
| **ID** | SAP-048 |
| **Depends on** | SAP-043 - SOLID Principles, SAP-047 - Law of Demeter |
| **Used by** | - |
| **Related** | SAP-047 - Law of Demeter, SAP-049 - CQS |
"@
$c = Insert-FieldTable $c $table
[IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
Write-Host "SAP-048: YAML + Entry Metadata done"

# ══════════════════════════════════════════════════════════════
# SAP-049 – Command-Query Separation (CQS)
# ══════════════════════════════════════════════════════════════
$fp = "$d\SAP-049 - Command-Query Separation (CQS).md"
$c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

$oldYAML = @"
---
layout: default
title: "Command-Query Separation (CQS)"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /software-architecture/command-query-separation/
id: SAP-049
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Object-Oriented Design, Side Effects, Immutability
used_by: API design, Domain model design, CQRS architecture
related: CQRS, Tell Don't Ask, Idempotency, Event Sourcing
tags:
  - architecture
  - principles
  - oop
  - advanced
  - cqrs
---
"@
$newYAML = @"
---
id: SAP-049
title: "Command-Query Separation (CQS)"
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-043, SAP-048
used_by:
related: SAP-018, SAP-048
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /software-architecture/command-query-separation/
---
"@
$c = $c.Replace($oldYAML, $newYAML)
$c = Remove-EntryMetadata $c
$table = @"

| Field | Value |
|---|---|
| **ID** | SAP-049 |
| **Depends on** | SAP-043 - SOLID Principles, SAP-048 - Tell Don't Ask |
| **Used by** | - |
| **Related** | SAP-018 - CQRS, SAP-048 - Tell Don't Ask |
"@
$c = Insert-FieldTable $c $table
[IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
Write-Host "SAP-049: YAML + Entry Metadata done"

# ══════════════════════════════════════════════════════════════
# SAP-050 – Cohesion
# ══════════════════════════════════════════════════════════════
$fp = "$d\SAP-050 - Cohesion.md"
$c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

$oldYAML = @"
---
layout: default
title: "Cohesion"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /software-architecture/cohesion/
id: SAP-050
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Object-Oriented Design, Module Design, SOLID Principles
used_by: Class design, Module design, Microservice boundary design
related: Coupling, SOLID Principles, Single Responsibility Principle, Connascence
tags:
  - architecture
  - principles
  - design
  - intermediate
  - module-design
---
"@
$newYAML = @"
---
id: SAP-050
title: Cohesion
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-043
used_by:
related: SAP-051, SAP-052
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /software-architecture/cohesion/
---
"@
$c = $c.Replace($oldYAML, $newYAML)
$c = Remove-EntryMetadata $c
$table = @"

| Field | Value |
|---|---|
| **ID** | SAP-050 |
| **Depends on** | SAP-043 - SOLID Principles |
| **Used by** | - |
| **Related** | SAP-051 - Coupling, SAP-052 - Connascence |
"@
$c = Insert-FieldTable $c $table
[IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
Write-Host "SAP-050: YAML + Entry Metadata done"

# ══════════════════════════════════════════════════════════════
# SAP-051 – Coupling
# ══════════════════════════════════════════════════════════════
$fp = "$d\SAP-051 - Coupling.md"
$c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

$oldYAML = @"
---
layout: default
title: "Coupling"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 51
permalink: /software-architecture/coupling/
id: SAP-051
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Object-Oriented Design, Module Design, Cohesion
used_by: API design, Module design, Microservice design, Code review
related: Cohesion, Connascence, Law of Demeter, Dependency Inversion Principle
tags:
  - architecture
  - principles
  - design
  - intermediate
  - module-design
---
"@
$newYAML = @"
---
id: SAP-051
title: Coupling
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-043
used_by:
related: SAP-050, SAP-052
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 51
permalink: /software-architecture/coupling/
---
"@
$c = $c.Replace($oldYAML, $newYAML)
$c = Remove-EntryMetadata $c
$table = @"

| Field | Value |
|---|---|
| **ID** | SAP-051 |
| **Depends on** | SAP-043 - SOLID Principles |
| **Used by** | - |
| **Related** | SAP-050 - Cohesion, SAP-052 - Connascence |
"@
$c = Insert-FieldTable $c $table
[IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
Write-Host "SAP-051: YAML + Entry Metadata done"

# ══════════════════════════════════════════════════════════════
# SAP-052 – Connascence
# ══════════════════════════════════════════════════════════════
$fp = "$d\SAP-052 - Connascence.md"
$c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

$oldYAML = @"
---
layout: default
title: "Connascence"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /software-architecture/connascence/
id: SAP-052
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Coupling, Cohesion, Object-Oriented Design
used_by: Advanced code review, Refactoring, Architecture analysis
related: Coupling, Cohesion, Law of Demeter, Tell Don't Ask, SOLID Principles
tags:
  - architecture
  - principles
  - advanced
  - coupling
  - deep-dive
---
"@
$newYAML = @"
---
id: SAP-052
title: Connascence
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-050, SAP-051
used_by:
related: SAP-050, SAP-051
tags:
  - architecture
  - principles
  - deep-dive
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /software-architecture/connascence/
---
"@
$c = $c.Replace($oldYAML, $newYAML)
$c = Remove-EntryMetadata $c
$table = @"

| Field | Value |
|---|---|
| **ID** | SAP-052 |
| **Depends on** | SAP-050 - Cohesion, SAP-051 - Coupling |
| **Used by** | - |
| **Related** | SAP-050 - Cohesion, SAP-051 - Coupling |
"@
$c = Insert-FieldTable $c $table
[IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
Write-Host "SAP-052: YAML + Entry Metadata done"

Write-Host ""
Write-Host "All batch 5 YAML + Entry Metadata updates complete."
