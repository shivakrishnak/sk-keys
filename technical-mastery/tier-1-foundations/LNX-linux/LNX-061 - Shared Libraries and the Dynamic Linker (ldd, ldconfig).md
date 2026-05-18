---
id: LNX-061
title: "Shared Libraries and the Dynamic Linker (ldd, ldconfig)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-005, LNX-050
used_by: LNX-062, LNX-082
related: LNX-050, LNX-005, LNX-082
tags: [shared-libraries, dynamic-linker, ldd, ldconfig, LD_LIBRARY_PATH, ELF, soname, rpath, dlopen]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/lnx/shared-libraries-dynamic-linker/
---

## TL;DR

Shared libraries (`.so` files) are loaded at runtime by the dynamic linker
(`ld.so`/`ld-linux.so`). `ldd /usr/bin/app` shows which shared libraries
a binary needs. `ldconfig` rebuilds the linker cache (`/etc/ld.so.cache`)
from `/etc/ld.so.conf` paths. `LD_LIBRARY_PATH` overrides search paths
at runtime (dev use only - security risk in production). Library naming:
`libfoo.so.1.2.3` (full), `libfoo.so.1` (soname), `libfoo.so` (linker name).
`dlopen()` for runtime loading. Missing library errors: "error while loading
shared libraries" - fix with `ldconfig` or `LD_LIBRARY_PATH`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-061 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | shared-libraries, dynamic linker, ldd, ldconfig, LD_LIBRARY_PATH, ELF, soname, rpath |
| **Prerequisites** | LNX-005 (Filesystem basics), LNX-050 (Kernel Modules) |

---

### The Problem This Solves

**Problem 1**: A Java application ships with native C libraries (e.g.,
snappy, lz4 for compression). After deployment, the application fails with
"error while loading shared libraries: libsnappy.so.1: cannot open shared
object file: No such file or directory". The library exists but the linker
cache doesn't know about it. Fix: add the library's directory to
`/etc/ld.so.conf.d/` and run `ldconfig`.

**Problem 2**: Two applications need different versions of the same library
(libssl.so.1.0 vs libssl.so.1.1). They can't share one installation.
Solution: package each with its own library in a private directory, use
`rpath` or `LD_LIBRARY_PATH` at startup to point to the right version.
This is what `conda` environments and Docker containers do.

---

### Textbook Definition

**Shared library (`.so`)**: ELF binary containing compiled code and data
that multiple programs can use simultaneously. Loaded into memory once and
mapped into each process's address space (read-only sections truly shared,
COW for writable). Reduces disk usage and memory footprint vs static linking.

**Dynamic linker/loader** (`ld-linux-x86-64.so.2`): The OS program loader.
At process startup: reads the ELF binary's `PT_INTERP` segment to find the
dynamic linker, runs the dynamic linker, which: resolves shared library
locations, loads them into the process address space, resolves symbols
(function addresses), and then hands control to the program's `main()`.

**Library naming convention:**
- **Real name**: `libfoo.so.1.2.3` (major.minor.patch)
- **soname**: `libfoo.so.1` (major version only, symlink to real name). Embedded in the library during compilation. Used by the dynamic linker at runtime.
- **Linker name**: `libfoo.so` (symlink to soname). Used by the compiler at build time (`-lfoo`).

**ldconfig**: Scans library directories listed in `/etc/ld.so.conf` (and
`/etc/ld.so.conf.d/*.conf`), creates symlinks for sonames, and writes
the binary cache `/etc/ld.so.cache`. The dynamic linker reads this cache
for fast library location.

---

### Understand It in 30 Seconds

```bash
# === Find libraries a binary needs ===
ldd /usr/bin/python3
# Output:
#   linux-vdso.so.1 (0x00007ffd...)     <- virtual, in kernel
#   libc.so.6 => /lib/x86_64.../libc.so.6 (0x...)
#   libpthread.so.0 => /lib/.../libpthread.so.0 (0x...)
#   /lib64/ld-linux-x86-64.so.2 (0x...)  <- dynamic linker itself

# SECURITY WARNING: never use ldd on untrusted binaries!
# ldd actually EXECUTES the binary with LD_TRACE_LOADED_OBJECTS=1
# Use objdump -p binary | grep NEEDED for untrusted binaries:
objdump -p /usr/bin/python3 | grep NEEDED
# NEEDED   libc.so.6
# NEEDED   libpthread.so.0

# === Show soname of a library ===
objdump -p /lib/x86_64-linux-gnu/libc.so.6 | grep SONAME
# SONAME   libc.so.6

# === Library search path ===
# Default paths (in order):
# 1. DT_RPATH / DT_RUNPATH in the ELF binary
# 2. LD_LIBRARY_PATH environment variable
# 3. /etc/ld.so.cache (built from /etc/ld.so.conf)
# 4. /lib, /usr/lib (hardcoded fallback)

# === Add a library directory to the system ===
# Option 1: Add to ld.so.conf.d:
echo "/opt/myapp/lib" > /etc/ld.so.conf.d/myapp.conf
ldconfig   # rebuild cache
ldconfig -v | grep myapp   # verify path is included

# Option 2: Check if a library is in the cache:
ldconfig -p | grep libssl   # list all libssl entries in cache
# ldconfig -p: print the cache

# === LD_LIBRARY_PATH (dev/debug only) ===
# Override library paths at runtime:
export LD_LIBRARY_PATH=/opt/myapp/lib:$LD_LIBRARY_PATH
./myapp   # now finds libraries in /opt/myapp/lib first

# DANGER for production:
# - can be set maliciously to preload attacker's libraries
# - ignored for setuid/setgid programs (security measure)

# === Library versioning ===
ls -la /lib/x86_64-linux-gnu/ | grep libssl
# libssl.so -> libssl.so.1.1    (linker name -> soname)
# libssl.so.1.1 -> libssl.so.1.1.1k  (soname -> real name)
# libssl.so.1.1.1k               (real name, actual file)

# When you call: -lssl at compile time
#   ld finds: libssl.so (linker name symlink)
#   follows to: libssl.so.1.1 (soname embedded in binary)
# At runtime:
#   ld.so finds: libssl.so.1.1 in cache
#   loads: libssl.so.1.1.1k

# === Diagnose "error while loading shared libraries" ===
# Run the failing binary:
./myapp
# error while loading shared libraries: libfoo.so.1: cannot open

# Step 1: Find where the library actually is:
find / -name "libfoo.so*" 2>/dev/null
# /opt/vendor/lib/libfoo.so.1.2.3

# Step 2: Add to ld.so.conf:
echo "/opt/vendor/lib" > /etc/ld.so.conf.d/vendor.conf
ldconfig

# Step 3: Verify:
ldconfig -p | grep libfoo   # should show libfoo.so.1 -> /opt/vendor/lib/libfoo.so.1.2.3
./myapp   # should work now

# === dlopen: runtime dynamic loading ===
# In C:
# void *handle = dlopen("libfoo.so.1", RTLD_LAZY);
# void (*func)(void) = dlsym(handle, "foo_function");
# func();
# dlclose(handle);
# Used by: plugin systems, language runtimes (Python ctypes, Java JNI)
```

---

### First Principles

**Dynamic linking resolution at program startup:**
```
./myapp launched:
         |
         v
Kernel: reads ELF header -> finds PT_INTERP: /lib64/ld-linux-x86-64.so.2
         |
         v
Kernel: loads ld-linux-x86-64.so.2 first
         |
         v
Dynamic linker (ld-linux) starts, reads myapp's:
  .dynamic section: lists NEEDED libraries
  DT_NEEDED: libssl.so.1.1
  DT_NEEDED: libc.so.6
  DT_RPATH:  /opt/myapp/lib  (if baked into binary via rpath)
         |
         v
For each NEEDED library:
  1. Check DT_RPATH entries
  2. Check LD_LIBRARY_PATH (if not setuid)
  3. Search /etc/ld.so.cache
  4. Search /lib, /usr/lib
  -> Found: /lib/x86_64-linux-gnu/libssl.so.1.1 -> libssl.so.1.1.1k
         |
         v
mmap() the library into process address space:
  Text segment (code): PROT_READ|PROT_EXEC (shared between all users)
  Data segment: PROT_READ|PROT_WRITE (CoW, per-process)
         |
         v
Symbol resolution (lazy or immediate based on RTLD_LAZY/RTLD_NOW):
  Lazy: PLT/GOT entries initially point to resolver stub
        On first call: resolver stub finds function address, patches GOT
        Subsequent calls: go directly to function (GOT is now patched)
  Immediate: all symbols resolved before main() runs
         |
         v
main() called - program runs
```

**soname versioning mechanism:**
```
Library installed:
  /usr/lib/libfoo.so.1.2.3  <- actual file

ldconfig creates/updates:
  /usr/lib/libfoo.so.1 -> libfoo.so.1.2.3  (soname symlink)
  /usr/lib/libfoo.so   -> libfoo.so.1       (linker name symlink, dev package)

Compile time (-lfoo):
  linker finds: libfoo.so -> libfoo.so.1 -> libfoo.so.1.2.3
  embeds in binary: DT_SONAME = libfoo.so.1 (major version only)

Runtime (program starts):
  needs: libfoo.so.1  (from DT_SONAME)
  finds via ldconfig cache: libfoo.so.1 -> libfoo.so.1.2.3
  loads: libfoo.so.1.2.3

Library updated to 1.2.4 (patch - backward compatible):
  New file: libfoo.so.1.2.4
  ldconfig updates: libfoo.so.1 -> libfoo.so.1.2.4
  Programs using libfoo.so.1 now get 1.2.4 automatically

Library updated to 2.0 (breaking change - new major version):
  New file: libfoo.so.2.0.0
  New soname: libfoo.so.2
  ldconfig creates: libfoo.so.2 -> libfoo.so.2.0.0
  Old programs: still get libfoo.so.1 (unchanged symlink)
  New programs: link against -lfoo -> libfoo.so -> libfoo.so.2
  BOTH can coexist on the same system
```

---

### Thought Experiment

Deploying an application with private library versions:

```bash
# Problem: myapp needs libssl.so.1.0, but system has libssl.so.1.1
# Can't change system libraries (other apps need 1.1)

# Solution: bundle the required library with the application

mkdir -p /opt/myapp/lib
# Copy specific version:
cp /path/to/libssl.so.1.0.2k /opt/myapp/lib/

# Option 1: Use LD_LIBRARY_PATH in startup script:
cat > /opt/myapp/start.sh << 'EOF'
#!/bin/bash
export LD_LIBRARY_PATH=/opt/myapp/lib:$LD_LIBRARY_PATH
exec /opt/myapp/bin/myapp "$@"
EOF
chmod +x /opt/myapp/start.sh

# Option 2: Embed rpath at compile time (better - no env var):
# During compilation:
# gcc -Wl,-rpath,/opt/myapp/lib -o myapp myapp.c -lssl
# or:
# gcc -Wl,-rpath,'$ORIGIN/../lib' -o myapp myapp.c -lssl
# $ORIGIN = directory of the executable (portable rpath)

# Check embedded rpath:
objdump -x /opt/myapp/bin/myapp | grep -E "RPATH|RUNPATH"
# RPATH    /opt/myapp/lib
# or: readelf -d /opt/myapp/bin/myapp | grep -E "RPATH|RUNPATH"

# Option 3: patchelf to set rpath on existing binary:
patchelf --set-rpath '/opt/myapp/lib' /opt/myapp/bin/myapp
# Modifies the ELF binary's rpath directly (useful for pre-compiled binaries)

# Verify:
ldd /opt/myapp/bin/myapp
# libssl.so.1.0.0 => /opt/myapp/lib/libssl.so.1.0.2k (0x...)
# Uses the private library, not the system one
```

---

### Mental Model / Analogy

```
Shared libraries = specialized tool rental shops in a city

Without shared libraries (static linking):
  Every workshop (program) buys and stores ALL the tools it needs
  100 workshops each store a full set of wrenches, drills, etc.
  Huge space (disk/RAM) wasted with identical copies

With shared libraries (dynamic linking):
  One rental shop for each tool type (libssl, libc, libz, etc.)
  Workshops rent tools as needed from the shops
  All 100 workshops can use the same physical wrench simultaneously
  (memory-mapped shared code pages, copy-on-write for data)

soname = shop's "version contract":
  "I need the v1 wrench shop (libssl.so.1)" - embedded in the program
  The city can upgrade to newer v1 wrenches (1.1.1 -> 1.1.2)
  without changing the contract (program recompile not needed)
  v2 wrenches open a different shop (libssl.so.2 != libssl.so.1)

ldconfig = the city's business directory:
  Lists every rental shop and its current location
  Rebuilt when new shops open (/etc/ld.so.conf changes)
  Programs look in this directory before searching the whole city
  Out-of-date directory = "cannot find shop" errors

LD_LIBRARY_PATH = personal shortlist override:
  "Before checking the directory, try these specific shops first"
  Useful when testing with a private shop (dev testing)
  Dangerous if malicious: attacker can substitute their fake shop
  (Ignored for root-owned programs: setuid binaries can't be hijacked)

rpath = the program's own personal shop list:
  Embedded IN the program binary ("I always use shops at /opt/myapp/lib")
  Can't be overridden by LD_LIBRARY_PATH (less flexible but more secure)
  $ORIGIN = "the same neighborhood as this program"
```

---

### Gradual Depth - Five Levels

**Level 1:**
`ldd binary` to see required libraries. The three symlinks (libfoo.so ->
libfoo.so.1 -> libfoo.so.1.2.3). `ldconfig` to rebuild the cache after
adding libraries. Fix "cannot open shared object file": find the .so file,
add its directory to `/etc/ld.so.conf.d/`, run `ldconfig`. `LD_LIBRARY_PATH`
for development.

**Level 2:**
`ldconfig -p` to list cache contents. `objdump -p binary | grep NEEDED`
(safe alternative to ldd for untrusted binaries). rpath vs RUNPATH in ELF.
`patchelf` for modifying existing binaries. Symbol versioning
(`nm -D library.so` to list exported symbols). `LD_PRELOAD`: force-load
a library before all others (used for malloc replacements like jemalloc,
tcmalloc; also used for debugging with custom interceptors).

**Level 3:**
PLT/GOT (Procedure Linkage Table / Global Offset Table): the lazy binding
mechanism. First call to an external function: PLT stub calls the resolver,
which patches GOT with the real address. Second call: GOT gives address
directly (no resolver). `LD_BIND_NOW=1` forces immediate binding (for
profiling, detecting missing symbols at startup). `ld --version-script`:
control symbol visibility in shared libraries (export only specific symbols).
`__attribute__((visibility("hidden")))` in GCC.

**Level 4:**
Position-Independent Executable (PIE) and ASLR: modern executables are
PIE (linked with `-fPIE -pie`), enabling ASLR randomization of their
load address. Combined with RELRO (Relocation Read-Only): after linking,
the GOT is marked read-only (prevents GOT overwrite exploits). `checksec`:
audits binary for security features (PIE, RELRO, stack canary, NX). Library
copy-on-write: `mmap(MAP_PRIVATE)` shares pages between processes;
on write, the kernel creates a private copy.

**Level 5:**
ELF linker scripts: control exactly how sections are laid out in the output
file. GNU symbol versioning (`map` files): allows multiple versions of the
same symbol in one library (critical for glibc backward compatibility).
`glibc` defines `__memcpy_sse2`, `__memcpy_avx_unaligned`, etc., and the
dynamic linker uses CPU feature detection via `IFUNC` (indirect function)
to dispatch to the optimal implementation at program start. Link-time
optimization (LTO) and whole-program optimization: inlining across library
boundaries. Musl libc vs glibc: trade-offs for static linking and container
base images.

---

### Code Example

**BAD - library issues:**
```bash
# BAD 1: using ldd on an untrusted binary:
ldd /tmp/downloaded-binary
# ldd actually RUNS the binary with special env var
# A malicious binary can execute code when traced with ldd!

# GOOD: use objdump or readelf for untrusted binaries:
objdump -p /tmp/downloaded-binary | grep NEEDED
readelf -d /tmp/downloaded-binary | grep NEEDED

# BAD 2: setting LD_LIBRARY_PATH in /etc/profile:
# echo "export LD_LIBRARY_PATH=/opt/mylib/lib" >> /etc/profile
# This applies to ALL users and ALL programs
# Any SUID binary that loads the wrong library = privilege escalation!

# GOOD: use /etc/ld.so.conf.d/ for system-wide library paths,
# or rpath for application-specific paths:
echo "/opt/mylib/lib" > /etc/ld.so.conf.d/mylib.conf
ldconfig

# BAD 3: copying .so files without running ldconfig:
cp libfoo.so.1.2.3 /usr/local/lib/
# Programs still can't find it! ldconfig cache is stale.

# GOOD: always run ldconfig after adding libraries:
cp libfoo.so.1.2.3 /usr/local/lib/
ldconfig
# Verify:
ldconfig -p | grep libfoo
```

**GOOD - packaging application with private libraries:**
```bash
#!/bin/bash
# deploy-app.sh: deploy app with bundled private libraries

APP_DIR=/opt/myapp
LIB_DIR=$APP_DIR/lib

mkdir -p "$LIB_DIR" "$APP_DIR/bin"

# Copy application binary and libraries:
cp /build/myapp "$APP_DIR/bin/"
cp /build/libs/libcustom.so.2.1.0 "$LIB_DIR/"

# Create soname symlink:
cd "$LIB_DIR"
ln -sf libcustom.so.2.1.0 libcustom.so.2
ln -sf libcustom.so.2 libcustom.so

# Embed rpath (so the binary finds its libraries without LD_LIBRARY_PATH):
patchelf --set-rpath '$ORIGIN/../lib' "$APP_DIR/bin/myapp"

# Verify:
ldd "$APP_DIR/bin/myapp" | grep custom
# libcustom.so.2 => /opt/myapp/lib/libcustom.so.2.1.0 (0x...)

echo "Deployment complete. Test with: $APP_DIR/bin/myapp"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`ldd` is safe to run on any binary" | ldd actually executes the binary with `LD_TRACE_LOADED_OBJECTS=1` set. A malicious binary can detect this environment variable and behave differently - or just run its payload. Never use `ldd` on untrusted binaries. Safe alternative: `objdump -p /binary | grep NEEDED` (reads ELF headers without executing) or `readelf -d /binary | grep NEEDED`. |
| "Running ldconfig once is a permanent fix" | ldconfig writes the cache file `/etc/ld.so.cache`. This cache IS persistent - it survives reboots. However, if you ADD new library files, MOVE libraries, or INSTALL packages with new libraries, you must run `ldconfig` again to update the cache. Package managers (apt, yum) run `ldconfig` automatically after installing packages that include libraries. Manual `cp` of .so files requires manual `ldconfig`. |
| "All .so files in /usr/lib are automatically found" | The dynamic linker searches paths listed in `/etc/ld.so.conf` and `/etc/ld.so.conf.d/*.conf`, plus the cache. `/usr/lib` and `/lib` are typically in the default paths, but `/usr/local/lib` is NOT always included. Many sysadmins are surprised when they compile something, install it to `/usr/local/lib/`, and programs can't find it. Fix: `echo "/usr/local/lib" >> /etc/ld.so.conf && ldconfig`. |
| "LD_PRELOAD is only used for malicious purposes" | LD_PRELOAD has legitimate uses: replacing malloc with jemalloc/tcmalloc (memory performance), injecting profiling code (Valgrind, Sanitizers), debugging (intercept and log specific function calls), testing with mock implementations. `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 ./myapp` uses jemalloc for this run. It IS also a classic privilege escalation vector if system has setuid binaries that can be influenced - but that's misuse. LD_PRELOAD is ignored for setuid/setgid processes. |
| "Static linking avoids all library dependency problems" | Static linking embeds ALL library code into the binary, eliminating runtime shared library dependencies. But: (1) Binary size grows dramatically (10-50x for some programs). (2) Security updates: if libssl has a CVE, statically-linked binaries must be RECOMPILED and REDEPLOYED - dynamic linking just means updating the .so file. (3) glibc static linking has gotchas: NSS (name service resolution, `/etc/hosts`, DNS) uses dynamic loading even in "static" glibc. Alpine Linux with musl libc is truly statically linkable. Docker Go binaries are often static (`CGO_ENABLED=0`), making them truly standalone. |

---

### Failure Modes & Diagnosis

**"error while loading shared libraries" - complete diagnosis:**
```bash
# Error:
./myapp: error while loading shared libraries: libcrypto.so.1.0.2: cannot open shared object file: No such file or directory

# Step 1: Find where the library is:
find / -name "libcrypto.so*" 2>/dev/null
# /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1  <- different version!
# /opt/openssl-1.0/lib/libcrypto.so.1.0.2     <- right version

# Step 2: Check what exact version is needed:
ldd myapp | grep crypto
# libcrypto.so.1.0.2 => not found

# Step 3: Add path to ldconfig:
echo "/opt/openssl-1.0/lib" > /etc/ld.so.conf.d/openssl-1.0.conf
ldconfig

# Step 4: Verify:
ldconfig -p | grep "libcrypto.so.1.0.2"
# libcrypto.so.1.0.2 (libc6,x86-64) => /opt/openssl-1.0/lib/libcrypto.so.1.0.2
ldd myapp   # should show: libcrypto.so.1.0.2 => /opt/openssl-1.0/lib/...

# Alternative: check if version compatibility exists:
# Maybe libcrypto.so.1.1 is backward-compatible with 1.0.2?
# Check if a soname symlink is missing:
ls -la /opt/openssl-1.0/lib/libcrypto*
# libcrypto.so.1.0.2 (real file)
# Missing: libcrypto.so.1.0 symlink!
ln -sf libcrypto.so.1.0.2 /opt/openssl-1.0/lib/libcrypto.so.1.0
ldconfig
```

---

### Related Keywords

**Foundational:**
LNX-005 (Filesystem), LNX-050 (Kernel Modules)

**Builds on this:**
LNX-062 (Memory Management), LNX-082 (Syscall Interface)

**Related:**
LNX-050 (Kernel Modules - similar concept for kernel code loading)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ldd /path/to/binary` | Show required shared libraries |
| `objdump -p binary \| grep NEEDED` | Safe alternative to ldd |
| `ldconfig` | Rebuild shared library cache |
| `ldconfig -p \| grep libfoo` | Check if library is in cache |
| `ldconfig -v` | Verbose: show all paths scanned |
| `readelf -d binary \| grep RPATH` | Show embedded rpath |
| `patchelf --set-rpath PATH binary` | Set rpath on existing binary |
| `/etc/ld.so.conf.d/*.conf` | Add library search paths |

**3 things to remember:**
1. soname (`libfoo.so.1`) is what gets embedded in binaries - run `ldconfig` after adding libraries so the cache maps soname to the real file
2. Never use `ldd` on untrusted binaries (it executes them); use `objdump -p | grep NEEDED` instead
3. Fix "cannot open shared object file": find the .so, add its directory to `/etc/ld.so.conf.d/`, run `ldconfig`

---

### Transferable Wisdom

Shared library concepts appear in: Java's JNI (native libraries via
`System.loadLibrary()` uses `dlopen()` under the hood). Python's `ctypes`
and native extension modules (`.cpython-39-x86_64-linux-gnu.so`). Node.js
native addons (`.node` files = renamed `.so` files loaded via dlopen). Docker
images: Alpine uses musl libc (smaller, statically-linkable) vs Ubuntu's
glibc. `scratch` Docker images (zero base): work only with truly static
binaries. Go binaries with `CGO_ENABLED=0`: statically linked, no .so
dependencies = perfect for distroless containers. The concept of "loaded
at runtime, symbol resolution via table" = the Plugin Pattern in software.
Every plugin system (browser extensions, IDE plugins, Java ServiceLoader)
is a high-level abstraction of dlopen/dlsym.

---

### The Surprising Truth

The dynamic linker performs a security optimization that most developers don't
know about: when a setuid or setgid program starts, the dynamic linker
IGNORES `LD_LIBRARY_PATH`, `LD_PRELOAD`, and other library override mechanisms.
This is a critical security boundary. Without this rule: any user could
create a fake `libssl.so` in a directory, set `LD_LIBRARY_PATH` to point
to it, and run a setuid program like `sudo`. The setuid program would load
the attacker's fake SSL library, which could intercept passwords. The rule
prevents this. The deeper implication: this is WHY `LD_LIBRARY_PATH` is
"only for development" - it works fine for normal user programs but is
silently ignored exactly when it would be most dangerous (privilege escalation
vectors). Attackers who understand this principle specifically hunt for
setuid programs that use `dlopen()` with paths derived from environment
variables (not `LD_PRELOAD`, but the actual code calling dlopen with an
attacker-controlled path) - a different but related vulnerability class.

---

### Mastery Checklist

- [ ] Understands the three-name library naming convention (real, soname, linker name)
- [ ] Can use ldd and objdump to find library dependencies
- [ ] Can fix "cannot open shared object file" errors (find library, add path, ldconfig)
- [ ] Understands the library search order (rpath, LD_LIBRARY_PATH, cache, default)
- [ ] Knows why LD_LIBRARY_PATH is a security risk for system-wide use

---

### Think About This

1. A compiled application works on the developer's machine but fails on
   the production server with "error while loading shared libraries:
   libcustom.so.3: cannot open shared object file". The library exists
   at `/opt/vendor/lib64/libcustom.so.3.1.0`. Design a complete fix
   that works both immediately (without reboot) and permanently (survives
   reboot). Name at least two different approaches and explain the trade-offs.

2. A Java application that uses JNI native libraries (`.so` files bundled
   in the JAR) crashes with `UnsatisfiedLinkError`. The `.so` is extracted
   to `/tmp/app-native/` at startup. What library search mechanism should
   be used to ensure the JVM finds it? What are the security implications
   of the different approaches?

3. You're building a Docker image that needs to be as small as possible (a
   microservice). The application is written in Go. Explain: (a) what
   `CGO_ENABLED=0 go build` does differently in terms of shared libraries,
   (b) why this enables using `FROM scratch` as the Docker base image,
   (c) what would prevent a C/C++ application from doing the same.

---

### Interview Deep-Dive

**Foundational:**
Q: What happens when a Linux program starts? Describe the dynamic linking process.
A: Program startup involves several phases: (1) KERNEL LOADER: when you execute a program, the kernel reads its ELF header. It finds `PT_INTERP` segment specifying the dynamic linker (typically `/lib64/ld-linux-x86-64.so.2`). Kernel maps both the program and the dynamic linker into memory. (2) DYNAMIC LINKER runs: reads the program's `.dynamic` section to find DT_NEEDED entries (required library names like `libssl.so.1.1`). (3) LIBRARY LOCATION: for each needed library, searches in order: (a) DT_RPATH/DT_RUNPATH embedded in the binary, (b) LD_LIBRARY_PATH environment variable (ignored for setuid), (c) `/etc/ld.so.cache` (built by `ldconfig`), (d) default paths `/lib`, `/usr/lib`. (4) LOADING: maps each library into the process address space using `mmap()`. Shared libraries' text (code) pages are shared between all processes (single physical memory page). Data pages start shared but become per-process on write (copy-on-write). (5) SYMBOL RESOLUTION: with lazy binding (default), PLT entries initially point to a resolver stub. On first function call, the stub resolves the symbol's address and patches the GOT entry. Subsequent calls go directly through the GOT. (6) INIT CODE: runs library constructors (`__attribute__((constructor))` functions or `.init_array` entries). (7) `main()` called. Practical implication: `ldd` shows you all this resolution. "Not found" in ldd output = library missing from search path = program will crash on startup.

**Expert:**
Q: What is the soname system and why does it enable backward-compatible library updates?
A: The soname system solves a critical problem: how to update a library without breaking programs that depend on it. Three-name convention: (1) Real name: `libssl.so.1.1.1k` - the actual file with full version. (2) soname: `libssl.so.1.1` - embedded in the library at compile time with `-Wl,-soname,libssl.so.1.1`. Represents the ABI (binary interface) version. Created as a symlink by `ldconfig`. (3) Linker name: `libssl.so` - used by the compiler (`-lssl`). Symlink maintained by the dev package. How it enables updates: when a program is compiled with `-lssl`, the linker follows: `libssl.so` (linker name) -> `libssl.so.1.1` (soname). The soname `libssl.so.1.1` is embedded in the compiled binary. At runtime: the dynamic linker looks up `libssl.so.1.1` in the ldconfig cache. `ldconfig` has a symlink: `libssl.so.1.1` -> `libssl.so.1.1.1k`. When OpenSSL releases `1.1.1m` (same soname): install the new file, update `ldconfig`'s symlink to point to `1.1.1m`. All existing programs now get `1.1.1m` automatically (zero recompile, zero redeploy). The ABI contract: changing the soname major version (`.so.1` -> `.so.2`) signals an ABI break - callers using the old binary interface continue to get `so.1` (old code); new programs get `so.2`. Both can coexist on the same system. This is how glibc has maintained backward compatibility since 1995 - `GLIBC_2.5` symbols still work on modern glibc (they resolve to the old implementations via symbol versioning).
