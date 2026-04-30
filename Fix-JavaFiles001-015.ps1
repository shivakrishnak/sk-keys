
# Fix-JavaFiles001-015.ps1
# Updates Java files 001-015 to comply with new instructions:
# - Complete frontmatter (number, category, difficulty, depends_on, used_by, tags)
# - H1 title after frontmatter
# - Inline backtick tags
# - Metadata bar as markdown table (replacing Unicode box)
# - Removes old 🏷️ Tags lines

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

$meta = @{
  "001" = @{
    title="JVM (Java Virtual Machine)"; cat="Java & JVM Internals"; diff="★★☆"
    dep="JRE, JDK"; used="JRE, JDK, Bytecode, Class Loader"
    tags="#java, #jvm, #internals, #foundational"
    itags='`#java` `#jvm` `#internals` `#foundational`'
  }
  "002" = @{
    title="JRE (Java Runtime Environment)"; cat="Java & JVM Internals"; diff="★☆☆"
    dep="JVM"; used="JDK, Application Deployment"
    tags="#java, #jvm, #internals, #foundational"
    itags='`#java` `#jvm` `#internals` `#foundational`'
  }
  "003" = @{
    title="JDK (Java Development Kit)"; cat="Java & JVM Internals"; diff="★☆☆"
    dep="JRE, JVM"; used="javac, javadoc, jdb, Maven, Gradle"
    tags="#java, #jvm, #internals, #foundational"
    itags='`#java` `#jvm` `#internals` `#foundational`'
  }
  "004" = @{
    title="Bytecode"; cat="Java & JVM Internals"; diff="★★☆"
    dep="JVM, javac"; used="JIT Compiler, Class Loader, JVM"
    tags="#java, #jvm, #internals, #deep-dive"
    itags='`#java` `#jvm` `#internals` `#deep-dive`'
  }
  "005" = @{
    title="Class Loader"; cat="JVM Internals"; diff="★★☆"
    dep="JVM, Bytecode"; used="JIT Compiler, Spring, Hibernate, OSGi, Tomcat"
    tags="#java, #jvm, #internals, #classloading, #intermediate"
    itags='`#java` `#jvm` `#internals` `#classloading` `#intermediate`'
  }
  "006" = @{
    title="Stack Memory"; cat="JVM Memory"; diff="★★☆"
    dep="JVM, Thread"; used="Every method call, Recursion, JIT Compiler"
    tags="#java, #jvm, #memory, #internals, #intermediate"
    itags='`#java` `#jvm` `#memory` `#internals` `#intermediate`'
  }
  "007" = @{
    title="Heap Memory"; cat="JVM Memory"; diff="★★☆"
    dep="JVM, GC, Stack Memory"; used="Every object allocation, GC, Spring, Hibernate"
    tags="#java, #jvm, #memory, #gc, #internals, #intermediate"
    itags='`#java` `#jvm` `#memory` `#gc` `#internals` `#intermediate`'
  }
  "008" = @{
    title="Metaspace"; cat="JVM Memory"; diff="★★☆"
    dep="JVM, Class Loader, Heap Memory"; used="Every loaded class, Spring, Hibernate"
    tags="#java, #jvm, #memory, #internals, #classloading, #intermediate"
    itags='`#java` `#jvm` `#memory` `#internals` `#classloading` `#intermediate`'
  }
  "009" = @{
    title="Stack Frame"; cat="JVM Memory"; diff="★★★"
    dep="Stack Memory, JVM, Bytecode, Thread"; used="Every method invocation, JIT Compiler, Debugger"
    tags="#java, #jvm, #memory, #internals, #deep-dive"
    itags='`#java` `#jvm` `#memory` `#internals` `#deep-dive`'
  }
  "010" = @{
    title="Operand Stack"; cat="JVM Internals"; diff="★★★"
    dep="Stack Frame, Bytecode, Local Variable Table"; used="Every bytecode instruction, JIT Compiler"
    tags="#java, #jvm, #internals, #bytecode, #deep-dive"
    itags='`#java` `#jvm` `#internals` `#bytecode` `#deep-dive`'
  }
  "011" = @{
    title="Local Variable Table"; cat="JVM Internals"; diff="★★★"
    dep="Stack Frame, Bytecode, Operand Stack"; used="Every method execution, Debugger, JIT Compiler"
    tags="#java, #jvm, #internals, #memory, #bytecode, #deep-dive"
    itags='`#java` `#jvm` `#internals` `#memory` `#bytecode` `#deep-dive`'
  }
  "012" = @{
    title="Object Header"; cat="JVM Internals"; diff="★★★"
    dep="JVM, Heap Memory, Bytecode"; used="GC, Synchronized, JIT Compiler"
    tags="#java, #jvm, #memory, #internals, #deep-dive"
    itags='`#java` `#jvm` `#memory` `#internals` `#deep-dive`'
  }
  "013" = @{
    title="Escape Analysis"; cat="JVM Internals"; diff="★★★"
    dep="JVM, Heap Memory, Stack Memory, JIT Compiler"; used="GC, JIT Compiler, Stack Frame"
    tags="#java, #jvm, #internals, #jit, #deep-dive"
    itags='`#java` `#jvm` `#internals` `#jit` `#deep-dive`'
  }
  "014" = @{
    title="Memory Barrier"; cat="JVM Internals"; diff="★★★"
    dep="JVM, Java Memory Model, volatile, CPU Cache"; used="volatile, synchronized, Happens-Before, JIT Compiler"
    tags="#java, #jvm, #concurrency, #internals, #deep-dive"
    itags='`#java` `#jvm` `#concurrency` `#internals` `#deep-dive`'
  }
  "015" = @{
    title="Happens-Before"; cat="JVM Internals"; diff="★★★"
    dep="Java Memory Model, Memory Barrier, volatile, synchronized, Thread"; used="volatile, synchronized, final, Thread.start, Thread.join"
    tags="#java, #jvm, #concurrency, #internals, #deep-dive"
    itags='`#java` `#jvm` `#concurrency` `#internals` `#deep-dive`'
  }
}

function Remove-UnicodeBoxBlock {
  param([string]$text)
  $lines = $text -split "`n"
  $result = [System.Collections.Generic.List[string]]::new()
  $i = 0
  while ($i -lt $lines.Count) {
    $l = $lines[$i]
    # Detect start of Unicode box code block
    if ($l.Trim() -eq '```') {
      # Check if next non-empty line has box drawing chars
      $j = $i + 1
      while ($j -lt $lines.Count -and $lines[$j].Trim() -eq '') { $j++ }
      if ($j -lt $lines.Count -and ($lines[$j] -match '[┌│├└]')) {
        # Skip until closing ```
        $i = $j
        while ($i -lt $lines.Count -and $lines[$i].Trim() -ne '```') { $i++ }
        $i++ # skip closing ```
        continue
      }
    }
    $result.Add($l)
    $i++
  }
  return $result -join "`n"
}

$javaDir = "C:\ASK\MyWorkspace\sk-keys\docs\Java"

foreach ($num in ($meta.Keys | Sort-Object)) {
  $m = $meta[$num]
  $files = Get-ChildItem -Path $javaDir -Filter "$num*" -File
  if ($files.Count -eq 0) { Write-Host "NOT FOUND: $num" -ForegroundColor Red; continue }
  $file = $files[0]

  $content = [System.IO.File]::ReadAllText($file.FullName, $utf8NoBom)
  $lines = $content -split "`r?`n"

  # Find frontmatter end
  $fmEnd = -1
  if ($lines.Count -gt 0 -and $lines[0].Trim() -eq '---') {
    for ($i = 1; $i -lt $lines.Count; $i++) {
      if ($lines[$i].Trim() -eq '---') { $fmEnd = $i; break }
    }
  }

  if ($fmEnd -lt 0) { Write-Host "No frontmatter: $($file.Name)" -ForegroundColor Yellow; continue }

  # Extract existing nav frontmatter fields
  $existFm = @{}
  for ($i = 1; $i -lt $fmEnd; $i++) {
    if ($lines[$i] -match '^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$') {
      $existFm[$matches[1]] = $matches[2].Trim('"')
    }
  }

  # Build new frontmatter
  $newFmLines = @(
    '---',
    'layout: default',
    ('title: "{0}"' -f $existFm['title']),
    ('parent: "{0}"' -f $existFm['parent']),
    ('nav_order: {0}' -f $existFm['nav_order']),
    ('permalink: {0}' -f $existFm['permalink']),
    ('number: "{0}"' -f $num),
    ('category: {0}' -f $m.cat),
    ('difficulty: {0}' -f $m.diff),
    ('depends_on: {0}' -f $m.dep),
    ('used_by: {0}' -f $m.used),
    ('tags: {0}' -f $m.tags),
    '---'
  )
  $newFm = $newFmLines -join "`n"

  # Get body after frontmatter
  $body = ($lines[($fmEnd + 1)..($lines.Count - 1)] -join "`n")

  # Remove 🏷️ Tags line (and trailing newline)
  $body = [regex]::Replace($body, '(?m)^🏷️ Tags[^\n]*\n?', '')

  # Remove Unicode box code blocks
  $body = Remove-UnicodeBoxBlock -text $body

  # Clean up excessive blank lines
  $body = [regex]::Replace($body, "`n{3,}", "`n`n")
  $body = $body.TrimStart("`n")

  # Find TL;DR line position
  $tldrMatch = [regex]::Match($body, '(?m)^⚡ TL;DR[^\n]*')
  if (-not $tldrMatch.Success) { Write-Host "No TL;DR in: $($file.Name)" -ForegroundColor Yellow; continue }

  $tldr = $tldrMatch.Value
  $afterTldr = $body.Substring($tldrMatch.Index + $tldrMatch.Length).TrimStart("`n")
  # Remove leading --- after TL;DR if it's directly next
  if ($afterTldr.StartsWith('---')) {
    $afterTldr = $afterTldr.Substring(3).TrimStart("`n")
  }

  # Build metadata table
  $metaTable = @(
    "| #$num | Category: $($m.cat) | Difficulty: $($m.diff) |",
    '|:---|:---|:---|',
    ("| **Depends on:** | {0} | |" -f $m.dep),
    ("| **Used by:** | {0} | |" -f $m.used)
  ) -join "`n"

  # Build final content
  $parts = @(
    $newFm,
    '',
    "# $num — $($m.title)",
    '',
    $m.itags,
    '',
    $tldr,
    '',
    $metaTable,
    '',
    '---',
    '',
    $afterTldr.TrimEnd()
  )
  $final = ($parts -join "`n") + "`n"

  [System.IO.File]::WriteAllText($file.FullName, $final, $utf8NoBom)
  Write-Host "Updated: $($file.Name)" -ForegroundColor Green
}

Write-Host "`nDone!" -ForegroundColor Cyan

