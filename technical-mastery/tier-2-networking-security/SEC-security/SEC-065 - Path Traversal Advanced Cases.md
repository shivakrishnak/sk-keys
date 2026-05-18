---
id: SEC-065
title: "Path Traversal (Advanced)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★★
depends_on: SEC-001, SEC-013, SEC-016, SEC-041, SEC-052, SEC-055
used_by: SEC-068, SEC-079
related: SEC-001, SEC-013, SEC-016, SEC-041, SEC-052, SEC-055
tags:
  - security
  - path-traversal
  - directory-traversal
  - file-read
  - owasp-a01
  - canonicalization
  - null-byte
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/sec/path-traversal-advanced/
---

⚡ TL;DR - Path traversal allows attackers to read (or write)
files outside the intended directory by using `../` sequences
in filenames. Advanced variants use URL encoding (`%2e%2e%2f`),
null bytes (`file.php%00.jpg`), Unicode (`%c0%af` on old Java),
and archive slip (zip files with `../` in entry names). Fix:
resolve to canonical path, then verify the result starts with
the allowed base directory.

---

| #065 | Category: Security | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Input Validation, File Upload Security, Security Code Review | |
| **Used by:** | SAST, Security Performance Testing | |
| **Related:** | File Upload Security (SEC-052), Injection, SSRF | |

---

### 🔥 The Problem This Solves

**WHY PATH TRAVERSAL IS STILL COMMON:**

```
BASIC PATH TRAVERSAL:
  GET /api/files/download?name=report.pdf
  
  Server code:
    String filename = request.getParameter("name");
    File file = new File("/var/app/uploads/" + filename);
    return readFile(file);
  
  Attack:
    GET /api/files/download?name=../../../../etc/passwd
    
    File path: /var/app/uploads/../../../../etc/passwd
    Resolves to: /etc/passwd  (../../.. navigates up past /var/app/uploads)
    Returns: contents of /etc/passwd

ADVANCED VARIANTS:

1. URL ENCODING:
   Name: ..%2F..%2F..%2Fetc%2Fpasswd
   %2F = /
   
   If server decodes %2F before stripping ../: bypass works.
   If server strips ../ before decoding %2F: bypass works.
   
   Double encoding: ..%252F..%252F (server decodes once: ..%2F..%2F
   then application decodes again: ../../../../)

2. NULL BYTE INJECTION (Java <1.7.0, PHP <5.3.4):
   filename: ../../../../etc/passwd%00.jpg
   
   %00 = null byte (0x00)
   Some file operations treat null as string terminator.
   Result: file.open("...../etc/passwd\0.jpg") reads /etc/passwd.
   The .jpg suffix was there to pass filename extension validation.
   Null byte truncated the filename before the extension.
   
   PATCHED in modern Java/PHP but may exist in legacy systems or C extensions.

3. UNICODE/UTF-8 OVERLONG ENCODING (historical):
   %c0%af = Unicode "overlong" encoding of /
   Accepted by old Java URL parsers as equivalent to /.
   Patched in Java 5+.

4. WINDOWS PATH TRAVERSAL:
   Windows paths: both / and \ are separators.
   ..\..\..\windows\system32\drivers\etc\hosts
   
   URL-encoded: ..%5C..%5C (Windows backslash = %5C)
   If running on Windows and server does not normalize:
   bypass works even if / is blocked.

5. ZIP SLIP (Archive Path Traversal):
   A ZIP file containing:
     good_file.txt  → extracted to /app/uploads/good_file.txt
     ../../../etc/cron.d/malicious → extracted to /etc/cron.d/malicious !
   
   The path ../../../ in the ZIP entry name traverses up to /etc/cron.d/
   when the archive is extracted with unzip/ZipInputStream.
   
   REAL IMPACT:
     Attacker uploads ZIP with entry: ../../../app/config/application.yml
     Extracts: overwrites application configuration.
     Or: ../../../app/config/app.properties = new JDBC password.
     Or: on servers with cron: ../../../etc/cron.d/backdoor
```

---

### 📘 Textbook Definition

**Path Traversal:** A vulnerability where user-supplied input is
used to construct a file path without proper validation or
canonicalization. Using `../` sequences, an attacker navigates
outside the intended directory to read, write, or delete files.

**Canonicalization:** Resolving all `.`, `..`, symlinks, and
encoding to a single "canonical" (normalized) absolute path.
`/var/app/../uploads/../../etc/passwd` canonicalizes to `/etc/passwd`.

**Archive Slip (Zip Slip):** A specific form of path traversal
where a ZIP/TAR/JAR archive file contains entries with `../`
in their paths. Extracting the archive without path normalization
writes files outside the target directory.

**OWASP Category:** A01 (Broken Access Control) in 2021.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Path traversal = `../` in a filename walks up directory levels
to reach files outside the intended directory. Canonical path
resolution then prefix check is the only reliable defense.

**One analogy:**
> Path traversal is like a building's elevator where a guest
> types their floor and the elevator follows the instructions literally.
>
> Guest floor request: "3" → elevator goes to floor 3. Expected.
> Attacker request: "3, then go down 5 floors" → elevator goes to floor -2.
>
> The elevator didn't validate that "3, then go down 5 floors"
> was outside the permitted range (floors 1-10).
>
> Canonical path fix: the elevator first computes where it will end up
> (floor -2), THEN checks: is floor -2 within the allowed range (1-10)?
> If not: refused.

---

### 🔩 First Principles Explanation

**Canonical path validation - the only reliable fix:**

```
THE CANONICAL PATH PATTERN:

  VULNERABLE:
    def download_file(base_dir: str, filename: str) -> bytes:
        # Naive join - vulnerable
        file_path = base_dir + "/" + filename
        with open(file_path, 'rb') as f:
            return f.read()
    
    download_file("/var/app/uploads", "../../../../etc/passwd")
    # Opens: /etc/passwd
  
  ALSO VULNERABLE (strip "../" only):
    filename = filename.replace("../", "")
    # Input: "....//....//....//etc/passwd"
    # After replace: "../../../../etc/passwd"  (../ was in the middle!)
    # Still traverses.
  
  CORRECT (resolve canonical path, then verify prefix):
    import os
    
    def safe_file_read(base_dir: str, filename: str) -> bytes:
        # Resolve canonical path (resolves all .., ., symlinks)
        base_dir_resolved = os.path.realpath(base_dir)
        
        # Join paths - NOT string concatenation
        requested_path = os.path.join(base_dir_resolved, filename)
        
        # Resolve canonical path of the requested file
        canonical_path = os.path.realpath(requested_path)
        
        # CRITICAL: verify canonical path starts with base_dir
        # Use os.path.commonpath for reliable prefix check
        if not canonical_path.startswith(base_dir_resolved + os.sep):
            raise PermissionError(
                f"Path traversal attempt detected: {filename}"
            )
        
        # Canonicalized path is within allowed directory - safe to read
        with open(canonical_path, 'rb') as f:
            return f.read()
    
    EXPLANATION:
      os.path.realpath() resolves: /../ sequences, symlinks, ./ sequences
      to the actual filesystem path.
      
      /var/app/uploads/../../../../etc/passwd
      → after realpath: /etc/passwd
      
      Check: does "/etc/passwd" start with "/var/app/uploads/"?
      → NO → raise PermissionError
      
      /var/app/uploads/report.pdf
      → after realpath: /var/app/uploads/report.pdf
      
      Check: does "/var/app/uploads/report.pdf" start with "/var/app/uploads/"?
      → YES → allowed
  
  NOTE on symlinks:
    If /var/app/uploads/ contains a symlink pointing to /etc/:
    The canonical path of /var/app/uploads/passwd_link would be /etc/passwd.
    This would FAIL the prefix check (correctly!).
    Symlinks can be used to escape the base directory - the canonical
    path check catches symlink escapes too.
```

```java
// Java canonical path validation:

import java.io.*;
import java.nio.file.*;

public class SafeFileReader {
    
    private final Path baseDir;
    
    public SafeFileReader(String baseDirPath) throws IOException {
        // Resolve at construction time (fails early if invalid)
        this.baseDir = Paths.get(baseDirPath)
                            .toRealPath()  // Canonical, must exist
                            .normalize();
    }
    
    public byte[] readFile(String filename) throws IOException {
        // Normalize the requested path
        Path requestedPath = baseDir.resolve(filename).normalize();
        
        // CRITICAL: verify it's still within baseDir
        if (!requestedPath.startsWith(baseDir)) {
            throw new SecurityException(
                "Path traversal: " + filename
            );
        }
        
        return Files.readAllBytes(requestedPath);
    }
}
```

**ZIP Slip prevention:**

```java
// Safe ZIP extraction:

import java.util.zip.*;
import java.io.*;
import java.nio.file.*;

public class SafeUnzip {
    
    public static void extract(File zipFile, File destDir)
            throws IOException {
        
        Path destPath = destDir.toPath().toRealPath();
        
        try (ZipInputStream zis = new ZipInputStream(
                new FileInputStream(zipFile))) {
            
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                
                // Normalize entry name
                Path entryPath = destPath.resolve(entry.getName())
                                         .normalize();
                
                // CHECK: entry must be inside destDir
                if (!entryPath.startsWith(destPath)) {
                    throw new SecurityException(
                        "ZIP Slip detected: " + entry.getName()
                    );
                }
                
                if (entry.isDirectory()) {
                    Files.createDirectories(entryPath);
                } else {
                    Files.createDirectories(entryPath.getParent());
                    Files.copy(zis, entryPath,
                               StandardCopyOption.REPLACE_EXISTING);
                }
                
                zis.closeEntry();
            }
        }
    }
}
```

---

### 🧪 Thought Experiment

**SCENARIO: Bypassing naive ../  stripping**

```
BYPASS TECHNIQUES FOR NAIVE FILTERS:

1. Nested traversal (double-/../):
   Filter: filename.replace("../", "")
   Bypass: "....//....//etc/passwd"
   After filter: "../../etc/passwd"  (the middle ../ was removed,
                                      leaving outer .. and /)
   
2. URL-decoded after filter:
   Filter: strip "../" from raw input before URL decoding
   Bypass: "%2e%2e%2fetc%2fpasswd" (URL-encoded ../../etc/passwd)
   After filter: "%2e%2e%2fetc%2fpasswd" (filter did not match)
   After URL decode: "../../etc/passwd"
   
3. Case variation (Windows):
   Filter: strip "../" (case-sensitive)
   Bypass: "..\/" (backslash + forward slash on Windows)
   
4. Non-standard encoding:
   Filter: strip "../" literal
   Bypass: "%2e%2e/" (".." URL-encoded, "/" literal)
   After decode: "../"  (filter already ran)
   
LESSON: String-based filtering of path traversal is always bypassable.
There are too many encoding variants to enumerate.

THE ONLY RELIABLE APPROACH:
  1. Do NOT filter input.
  2. Resolve the path to canonical form (after all decoding).
  3. Check the canonical path against the allowed base directory.
  
  The canonical path has exactly one representation. There is no
  encoding trick that changes the result of realpath() because
  realpath() works at the filesystem level, not string level.
```

---

### 🧠 Mental Model / Analogy

> Path traversal is like a library where you can request books
> by section/shelf number.
>
> Library rule: "You can access the public section (shelves 1-100)."
>
> Normal request: "Give me shelf 42, book 7." → Public section. Allowed.
>
> Path traversal: "Give me shelf 42, then go back 50 shelves (shelf -8)."
> Shelf -8 is the restricted archive. The librarian follows the instruction.
>
> The librarian needs to:
> 1. Compute: shelf 42, back 50 = shelf -8.
> 2. Then check: is shelf -8 in the public section (1-100)?
> 3. No → refuse.
>
> NOT: "Remove any 'go back' instructions before processing" (bypassable).
> YES: "Compute the final shelf number, THEN check if it's in range" (reliable).
>
> realpath() = computing the final shelf number.
> startsWith(base_dir) = checking if it's in the public section.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Path traversal means using `../` in a filename to go "up" a directory level. By chaining many `../`, an attacker can reach system files outside the intended folder. Fix: resolve the full path first, then check it's still inside the allowed folder.

**Level 2 - How to use it (junior developer):**
Never concatenate user input directly into file paths. Use `os.path.join()` (Python) or `Paths.get().resolve()` (Java). After joining, call `os.path.realpath()` (Python) or `normalize().toRealPath()` (Java) to get the canonical path. Then check: does the canonical path start with the allowed base directory? If not: reject. This approach handles all variants: `../`, URL encoding, null bytes, symlinks.

**Level 3 - How it works (mid-level engineer):**
The canonical path approach works because `realpath()` / `toRealPath()` operates at the filesystem level: it asks the OS to resolve the actual path, which has exactly one canonical representation. No string manipulation, no encoding variants. The result is either inside the base directory or it isn't. This catches: `../` sequences, URL-encoded variants (after web framework decodes them), symlinks pointing outside the base, null byte truncation (doesn't apply to modern path resolution). ZIP Slip: the same principle - resolve each entry's path, then check it's within the destination directory before extracting.

**Level 4 - Why it was designed this way (senior/staff):**
Path traversal persists because developers think about it at the string level ("strip `../`") rather than the semantic level ("what is the actual file this path resolves to?"). String-level defenses fail because there are many equivalent string representations of the same path. The canonical path approach works at the semantic level - it asks the OS what file this actually refers to, regardless of string representation. The `realpath()` function has been in POSIX since the 1990s; the insight of using it for security validation (as the first step, before any file operation) is the key. In languages that use path objects (Python's `pathlib`, Java's `java.nio.file.Path`): path manipulation methods like `resolve()` and `normalize()` operate semantically, making this pattern cleaner.

**Level 5 - Mastery (distinguished engineer):**
Advanced ZIP Slip: tar archives have the same vulnerability. `.tar.gz` files with entry names containing `../` extract outside the destination. Python's `tarfile.extract()` had this vulnerability; `tarfile.extractall()` was patched to filter `../` in Python 3.12. In older Python: use `tarfile.getmembers()` to inspect entries before extraction, checking each member's name for `../`. Archive libraries across languages have had ZIP Slip vulnerabilities: Go's `archive/zip`, Ruby's `rubygems`, and npm's package extraction. SLSA (Supply Chain Levels for Software Artifacts) framework addresses archive security in build systems. In cloud: if your CI/CD pipeline extracts artifacts from untrusted sources, ZIP Slip in the extraction step can compromise build machines.

---

### ⚙️ How It Works (Mechanism)

```
CANONICAL PATH RESOLUTION:

  Input: /var/app/uploads/../../../../etc/passwd
  
  Step 1: normalize() resolves . and ..
    /var/app/uploads → 4 levels up from uploads:
      /var/app/uploads → /var/app → /var → / → /etc
    After normalization: /etc/passwd
  
  Step 2: toRealPath() resolves symlinks
    If /etc is a symlink to /private/etc (macOS):
    toRealPath: /private/etc/passwd
  
  Step 3: startsWith check
    Does "/private/etc/passwd" start with "/var/app/uploads/"?
    NO → SecurityException

  Input: /var/app/uploads/reports/Q1-2024.pdf
  
  Step 1: normalize() - already normal (no . or ..)
    /var/app/uploads/reports/Q1-2024.pdf
  
  Step 2: toRealPath() - no symlinks
    /var/app/uploads/reports/Q1-2024.pdf
  
  Step 3: startsWith check
    Does "...uploads/reports/Q1-2024.pdf" start with ".../uploads/"?
    YES → allowed, read file
```

```mermaid
flowchart TD
    A[User input: filename] --> B[os.path.join(base_dir, filename)]
    B --> C[os.path.realpath - canonical form]
    C --> D{canonical.startswith\nbase_dir + sep?}
    D -->|Yes| E[Safe: read/write file]
    D -->|No| F[SecurityException: traversal]
```

---

### 💻 Code Example

**Python: complete path traversal safe utility:**

```python
import os
from pathlib import Path

class SafeFileServer:
    """
    File server with path traversal protection.
    Resolves canonical paths and validates against base dir.
    """
    
    def __init__(self, base_dir: str):
        # Resolve at init: fails fast if base_dir doesn't exist
        self._base = Path(base_dir).resolve()
    
    def _safe_path(self, filename: str) -> Path:
        """
        Resolve filename relative to base_dir.
        Raises PermissionError if path traversal detected.
        """
        # Join and normalize (handles .., ./, //)
        candidate = (self._base / filename).resolve()
        
        # Verify: candidate is inside self._base
        # Path.is_relative_to() available in Python 3.9+
        try:
            candidate.relative_to(self._base)
        except ValueError:
            raise PermissionError(
                f"Path traversal blocked: {filename!r}"
            )
        
        return candidate
    
    def read(self, filename: str) -> bytes:
        path = self._safe_path(filename)
        if not path.is_file():
            raise FileNotFoundError(filename)
        return path.read_bytes()
    
    def write(self, filename: str, data: bytes) -> None:
        path = self._safe_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


# Usage:
server = SafeFileServer("/var/app/uploads")

# Safe:
server.read("report.pdf")         # /var/app/uploads/report.pdf

# Blocked:
server.read("../../../../etc/passwd")  # PermissionError
server.read("%2e%2e%2fetc%2fpasswd")   # PermissionError (after URL decode)
server.read("../../../etc/shadow")     # PermissionError
```

---

### ⚖️ Comparison Table

| Defense | Works for | Fails for |
|:---|:---|:---|
| **Strip `../` from string** | Basic `../` | Encoded, nested, backslash variants |
| **Regex on raw input** | Some variants | Double-encoding, non-standard separators |
| **Canonical path + prefix check** | ALL variants | Nothing (complete defense) |
| **Allowlist filename chars (`[a-zA-Z0-9._-]`)** | Most cases | Legitimate files with spaces or unicode |
| **Rename to UUID on storage** | File read via filename | Write traversal (if path used for output) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "We strip `../` from input, so we're safe." | String-based `../` removal is reliably bypassable. Double-dot bypass: `....//` after removing `../` leaves `../`. URL encoding: `%2e%2e%2f` decodes to `../` after your filter. Backslash: `..\` on Windows. Null bytes: `..%00`. The canonical path approach is the ONLY reliable defense because it works at the filesystem level, not the string level. `realpath()` returns the same result regardless of how the path was encoded or formatted as a string. There is no encoding trick that changes the actual file a canonical path points to. |
| "Archive extraction is safe because we only extract to a temp directory." | Extracting to a temp directory does not prevent ZIP Slip. The attack writes files OUTSIDE the temp directory: `../../../etc/cron.d/backdoor`. The extracted file ends up at `/etc/cron.d/backdoor`, not in the temp directory. The temp directory is the intended target; ZIP Slip escapes it. The fix: check every entry's canonical path against the target directory before extracting. Do not assume that the destination directory limits where files will be written. |

---

### 🚨 Failure Modes & Diagnosis

**Testing for path traversal:**

```
TESTING:

Basic test:
  GET /api/files?name=../../../../etc/passwd
  GET /api/files?name=..%2F..%2F..%2Fetc%2Fpasswd
  GET /api/files?name=....//....//etc/passwd
  
  Expected: 400 Bad Request or 403 Forbidden
  Vulnerable: returns file contents or different error (file not found vs. permission)

Windows-specific:
  GET /api/files?name=..\..\..\..\windows\system32\drivers\etc\hosts
  GET /api/files?name=..%5C..%5C..%5Cwindows%5Csystem32%5Chosts

ZIP Slip test:
  Create a ZIP with a malicious entry:
  
  Python:
    import zipfile
    with zipfile.ZipFile('evil.zip', 'w') as zf:
        zf.writestr('../../../tmp/evil.txt', 'traversal test')
  
  Upload evil.zip to the target.
  Check if /tmp/evil.txt was created.

SAST detection:
  Grep for file operations with user input:
    grep -rn "new File.*request\|getParameter.*path\|open.*param" src/
  
  Semgrep: taint analysis from request parameters to file operations.
  
  For ZIP: check ZipInputStream.getNextEntry() - is entry name validated?
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10` - A01 Broken Access Control
- `Input Validation` - general input validation
- `File Upload Security` - related file handling security

**Builds on this:**
- `SAST` - automated path traversal detection
- `Security Performance Testing` - traversal testing methodology

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BASIC ATTACK │ ../../../../etc/passwd                    │
│ ENCODED      │ %2e%2e%2f..%2fetc%2fpasswd               │
│ DOUBLE ENC   │ %252e%252e%252f                           │
│ WIN          │ ..\..\..\windows\system32\hosts           │
│ ZIP SLIP     │ ../../../etc/cron.d/malicious in ZIP entry│
├──────────────┼───────────────────────────────────────────┤
│ THE FIX      │ realpath/resolve → check startsWith(base) │
├──────────────┼───────────────────────────────────────────┤
│ PYTHON       │ Path(base / filename).resolve()           │
│              │ .relative_to(base) or raise PermissionError│
│ JAVA         │ Paths.get(base).resolve(name).normalize() │
│              │ .startsWith(base) or throw SecurityException│
├──────────────┼───────────────────────────────────────────┤
│ OWASP        │ A01 Broken Access Control (2021)          │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Validate at the semantic level, not the syntactic level."
Path traversal is most commonly "defended" with string-level
sanitization (strip `../`). This fails because the same semantic
path (the actual file) can be expressed in many syntactic forms
(different encodings, case, separator variants).
The reliable approach: resolve to the single canonical
semantic representation FIRST, then validate.
This principle recurs across security:
- URL validation: parse the URL to extract the hostname, then
  check hostname against allowlist - not string matching.
- Email validation: use a proper RFC 5321 parser, not regex -
  email has many valid forms that simple regex misses.
- SQL injection: parameterized queries (semantic: value as data)
  vs. escaping (syntactic: modify the string) - parameterized
  queries are reliable; escaping has encoding bypass cases.
- HTML injection/XSS: DOM APIs (semantic: text node vs. HTML
  element) vs. string sanitization (syntactic: remove <script>) -
  DOM text nodes cannot contain HTML, strings can always be
  re-encoded to contain HTML.
The pattern: any time you are manipulating a string that will be
interpreted by another system (filesystem, database, HTML parser),
use the target system's semantic primitives directly, not string
operations.

---

### 💡 The Surprising Truth

ZIP Slip (Zip Slip, discovered and named by Snyk Security Research
in 2018) affected not just Java applications but virtually every
language's archive extraction library: Python's zipfile (patched),
Go's archive/zip (patched), .NET's ZipArchive (patched), Ruby's
Gem::Package (patched), and popular build tools like Jenkins,
Apache Ant, gradle's zipTree, and hundreds of open-source projects.
The researchers found 1,000+ affected projects on GitHub.
The vulnerability had existed in some of these libraries for
over a decade. Archive extraction is a common task, but the
"check the entry name for path traversal before extracting" step
was routinely omitted.
The most impactful case: npm's package installation process
was vulnerable to ZIP Slip via tarball archives. Since npm
installs packages from potentially untrusted sources, a malicious
npm package could escape the node_modules directory and write
files anywhere the npm process had write access.
This is patched in modern npm, but it illustrates how foundational
operations (extracting a ZIP, installing a package) can have
path traversal vulnerabilities that weren't considered during design.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why string-based `../` stripping fails and what bypasses
   exist (encoded, double, nested, null byte).
2. **IMPLEMENT** canonical path validation in Python and Java:
   `realpath()` or `toRealPath()`, then `startsWith(base_dir)`.
3. **FIX** ZIP extraction code to check each entry's canonical path
   against the destination directory before extracting.
4. **TEST** for all major path traversal variants including ZIP Slip.

---

### 🎯 Interview Deep-Dive

**Q: What is path traversal? How would you prevent it in a Java file download API?**

*Why they ask:* Common vulnerability in file-handling code.
Tests understanding of canonicalization vs. string sanitization.

*Strong answer covers:*
- Attack: `filename=../../../../etc/passwd` navigates outside the
  intended directory via `../` sequences.
- Why string filtering fails: encoded variants (`%2e%2e%2f`), double
  encoding, nested traversal bypass string-based `../` removal.
- Correct fix: canonical path validation.
  `Paths.get(baseDir).resolve(filename).normalize()` then
  `.startsWith(baseDir)`. Throws SecurityException if outside base.
- Why realpath works: operates at filesystem level - regardless of
  encoding, the OS resolves to exactly one canonical path.
- ZIP Slip: archive entries with `../` in their names extract outside
  the destination. Fix: same canonical path check per entry before extraction.
- Symlinks: `realpath()` resolves symlinks - a symlink in the base dir
  pointing to `/etc/` would be caught by the prefix check. Intentional.
- Python equivalent: `Path(base / filename).resolve().relative_to(base)`
- OWASP A01 (Broken Access Control).