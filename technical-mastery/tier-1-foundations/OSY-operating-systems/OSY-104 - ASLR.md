---
id: OSY-104
title: ASLR - Address Space Layout Randomization
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-009, OSY-054, OSY-055, OSY-103
used_by: []
related: OSY-103, OSY-105, OSY-107
tags:
  - ASLR
  - security
  - exploit-mitigation
  - memory-layout
  - Linux
  - stack-protection
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 104
permalink: /technical-mastery/osy/aslr/
---

## TL;DR

ASLR (Address Space Layout Randomization) randomizes the
virtual addresses of stack, heap, libraries, and executable
at process startup. Makes exploit development harder:
attackers can't hard-code jump addresses for return-oriented
programming (ROP). Requires PIE (Position-Independent
Executable) to fully protect code segment. Bypass: brute
force (32-bit), info leaks, JIT spraying.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-104 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | ASLR, PIE, exploit mitigation, ROP, address randomization |
| **Prerequisites** | OSY-009, OSY-054, OSY-055, OSY-103 |

---

### How ASLR Works

```
Without ASLR (static addresses):
  Process virtual address layout (always the same):
    0x00400000: code (text segment)
    0x00600000: data segment
    0x7fff0000: stack
    0x7f8a0000: libc.so loaded here
    0x7f8b0000: libpthread.so loaded here
    
  Attacker exploits buffer overflow:
    Overwrites return address with: 0x7f8a1234 (known libc function)
    Works every time: addresses are predictable
    
With ASLR (randomized addresses):
  Process 1:
    0x564a3c00: code
    0x7f29d000: libc.so
    0x7ffce000: stack base
    
  Process 2 (same binary, restarted):
    0x55c3e000: code
    0x7fe91000: libc.so
    0x7ffd2000: stack base
    
  Randomization entropy:
    64-bit Linux: 28 bits of ASLR entropy for libraries = 268M positions
    64-bit stack: 20 bits = 1M positions
    Brute force: infeasible for 64-bit
    32-bit: only 8 bits of entropy = 256 positions -> feasible to brute force
    
  What gets randomized:
    Stack base address
    Heap base address (mmap base)
    Shared library load addresses (libc, etc.)
    Code segment: ONLY if PIE (see below)
```

---

### PIE: Completing ASLR Protection

```
Without PIE (non-PIE executable):
  Code segment (text): ALWAYS at the same virtual address!
  Example: /usr/bin/myapp always at 0x400000
  
  ASLR protects: heap, stack, libraries
  ASLR does NOT protect: the code itself (without PIE)
  
  ROP (Return-Oriented Programming) attack:
    Buffer overflow: overwrite return address
    Target: gadgets WITHIN the executable (code at predictable address!)
    Chain gadgets to: call exec("/bin/sh") or similar
    Works even with ASLR (code address is known)
    
PIE (Position-Independent Executable):
  Compile with: gcc -fPIE -pie OR gcc -fpic
  ELF type: ET_DYN (dynamic/shared) instead of ET_EXEC
  Result: code segment loaded at random address
  
  Full ASLR + PIE:
    ALL segments randomized: code, heap, stack, libraries
    Attacker must know ALL target addresses (impossible without info leak)
    
  Check if binary has PIE:
    file /usr/bin/nginx
    # "ELF 64-bit LSB pie executable" = PIE enabled
    # "ELF 64-bit LSB executable" = NO PIE
    
    checksec --file=/usr/bin/java
    # Output:
    # RELRO: Full
    # STACK CANARY: Canary found
    # NX: NX enabled
    # PIE: PIE enabled  <- ASLR fully effective
    # RPATH: No RPATH
    
  Java (JVM):
    JVM is PIE: yes (since JDK 8 on Linux)
    JIT-compiled code: loaded at random address (ASLR applies)
    But: JIT spraying attack possible (fill JIT cache with controlled bytes)
    Mitigation: JIT code randomization (JEP: planned/partial)
```

---

### ASLR Levels in Linux

```bash
# Check ASLR level:
cat /proc/sys/kernel/randomize_va_space

# Values:
# 0: disabled (ASLR off; static addresses)
# 1: partial randomization
#    - stack
#    - shared library positions
#    - NOT: heap (predictable)
# 2: full randomization (recommended)
#    - stack
#    - heap
#    - shared libraries
#    - code (if PIE)

# Enable full ASLR:
echo 2 > /proc/sys/kernel/randomize_va_space
# Or permanently:
echo 'kernel.randomize_va_space=2' >> /etc/sysctl.conf
sysctl -p

# Verify randomization (run same binary twice, check maps):
cat /proc/$(pgrep sleep)/maps | grep heap
# heap address changes between restarts

# Disable ASLR for debugging (need known addresses):
setarch $(uname -m) -R /usr/bin/gdb ./program
# -R: disable ASLR for this invocation only
# Or: ulimit -s unlimited (disables stack randomization)
```

---

### ASLR Bypass Techniques

```
1. Brute force (32-bit only):
   32-bit Linux: ~8-12 bits entropy = 256-4096 positions
   Brute force: run exploit hundreds of times; eventually works
   Fix: 64-bit systems (too many positions to brute force)
   
2. Information leak (info leak vulnerabilities):
   Format string vulnerability leaks a pointer
   Pointer reveals: base address of code/library
   Calculate: all other addresses = base + known offset
   Fix: prevent information leaks (bound checking, format string protection)
   
3. JIT spraying (JavaScript/JVM):
   Fill JIT code cache with chosen bytes (via crafted JS/Java)
   Flip: find a byte sequence that looks like an instruction
   Use: known addresses within the JIT-compiled code
   Partial mitigation: JIT code randomization, execute-only memory
   
4. Heap feng shui (heap grooming):
   Manipulate heap layout to place controlled data at known relative offset
   Combine with: partial overwrite (overwrite only low bytes of address)
   Works when: ASLR randomizes high bits but low bits are predictable
   
Practical implication for engineers:
  ASLR significantly raises the bar for exploitation
  ASLR + PIE + stack canaries + NX = defense in depth
  No mitigation is 100% bypass-proof
  Assume compromise is possible; layer defenses accordingly
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "ASLR prevents all buffer overflow exploits" | ASLR raises the difficulty but doesn't prevent all exploits. Info leaks bypass ASLR by revealing addresses. 32-bit systems are vulnerable to brute force. JIT spraying bypasses on JVM targets. ASLR is one layer of defense-in-depth, not a complete solution. |
| "ASLR protects the code segment" | Only if the binary is compiled as PIE (Position-Independent Executable). Without PIE, the code segment loads at a fixed address regardless of ASLR. Always compile with -fPIE -pie for executables and verify with `checksec` or `file`. |
| "Disabling ASLR in development is safe since it's local" | Developer machines with ASLR disabled that become accessible (VPN, misconfiguration) are immediately more exploitable. Better: use debugger-specific ASLR disable (`setarch -R ./program`) per-invocation rather than system-wide. |

---

### Quick Reference Card

| Concept | Detail |
|---------|--------|
| Check ASLR level | `cat /proc/sys/kernel/randomize_va_space` |
| Enable full ASLR | `echo 2 > /proc/sys/kernel/randomize_va_space` |
| Check PIE | `file /binary` or `checksec --file=/binary` |
| Compile with PIE | `gcc -fPIE -pie` or CMake: `PIE ON` |
| 64-bit entropy | 28 bits for libraries (~268M positions) |
| 32-bit entropy | 8-12 bits (~256-4096 positions; brute-forceable) |
| Bypass: info leak | One pointer leak reveals all addresses |
| ASLR levels | 0=off, 1=partial, 2=full |
