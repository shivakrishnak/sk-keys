---
id: OSY-087
title: Linux Kernel Module
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-003, OSY-009, OSY-010, OSY-086
used_by: []
related: OSY-086, OSY-088, OSY-097
tags:
  - kernel-module
  - Linux
  - kernel-programming
  - device-driver
  - eBPF
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 87
permalink: /technical-mastery/osy/linux-kernel-module/
---

## TL;DR

Linux kernel modules (LKMs) are object files loaded into the
kernel at runtime to add functionality without rebooting.
Used for device drivers, filesystems, and kernel extensions.
A module bug crashes the kernel (no isolation). Modern
alternative: eBPF for safe, sandboxed kernel extensions.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-087 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | kernel module, LKM, device driver, eBPF, kernel programming |
| **Prerequisites** | OSY-003, OSY-009, OSY-010, OSY-086 |

---

### What Is a Kernel Module?

```
Normal user program:
  Application code -> glibc -> syscall -> kernel -> hardware
  
Kernel module:
  Module code runs INSIDE the kernel
  Same privilege as kernel itself (Ring 0)
  Direct access to: kernel data structures, hardware registers,
    other kernel subsystems (network stack, VFS, scheduler)
  
Module vs. built-in:
  Built-in: compiled into vmlinuz, always present
  Module (LKM): separate .ko file, loaded when needed
  
Module loading:
  insmod module.ko    # Load module
  rmmod module        # Remove module
  modprobe module     # Load with dependency resolution
  lsmod               # List loaded modules
  
Module file: /lib/modules/$(uname -r)/kernel/drivers/...

Common module types:
  - Device drivers: GPU, NIC, storage controllers
  - Filesystems: ext4, btrfs, overlay (used by Docker)
  - Network filters: iptables, nftables, Netfilter
  - Security: SELinux, AppArmor (as modules)
  - Observability: eBPF (modern approach)
```

---

### Module Structure (Minimal Example)

```c
// minimal_module.c - Hello World kernel module
// Build: requires kernel headers matching running kernel

#include <linux/module.h>   // MODULE_* macros
#include <linux/kernel.h>   // printk()
#include <linux/init.h>     // module_init(), module_exit()

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Engineer");
MODULE_DESCRIPTION("Minimal kernel module for learning");
MODULE_VERSION("1.0");

// Called when module is loaded (insmod)
static int __init minimal_init(void) {
    // printk: like printf but for kernel log
    // KERN_INFO: log level (DEBUG, INFO, WARNING, ERR, CRIT)
    printk(KERN_INFO "minimal_module: loaded\n");
    return 0;  // 0 = success; non-zero = load failed
}

// Called when module is unloaded (rmmod)
static void __exit minimal_exit(void) {
    printk(KERN_INFO "minimal_module: unloaded\n");
}

module_init(minimal_init);
module_exit(minimal_exit);
```

```makefile
# Kbuild Makefile
obj-m += minimal_module.o

all:
	make -C /lib/modules/$(shell uname -r)/build \
	     M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build \
	     M=$(PWD) clean
```

---

### Why Modules Are Dangerous

```
BAD: Kernel module bug behavior
  
  A kernel module runs in Ring 0 with the same privileges
  as the kernel itself. When a module crashes:
  
  User program null pointer dereference:
    -> SIGSEGV signal sent to process
    -> Process terminated
    -> Rest of system unaffected
    
  Kernel module null pointer dereference:
    -> Kernel panic (or OOPS if non-fatal)
    -> Entire system may halt
    -> All processes terminated
    -> Uptime reset to 0
    
  Exploitable module bugs (privilege escalation):
    A vulnerability in a kernel module can:
    1. Escalate a normal user to root
    2. Escape from a container (if module is loaded by host)
    3. Install rootkits by modifying kernel data structures
    
  Famous examples:
    - CVE-2009-1185 (udev): kernel module privilege escalation
    - NVIDIA drivers: frequent kernel panics in early versions
    - Many NIC drivers: memory corruptions, info leaks

GOOD: eBPF as safe alternative
  
  eBPF programs run in kernel space BUT:
  - Verified before loading (eBPF verifier checks: no loops,
    no invalid memory access, no kernel address disclosure)
  - Cannot panic the kernel (worst case: the eBPF program fails)
  - Cannot modify arbitrary kernel data
  - Sandboxed: only accesses allowed maps and helper functions
  
  eBPF replaces modules for:
    Observability: Cilium, Pixie, BPFTrace
    Network filtering: XDP (eXpress Data Path)
    Security: Falco, Tetragon
    
  For DEVICE DRIVERS: still requires kernel modules (no eBPF equiv)
```

---

### Module Security Considerations

```
Attack surface from kernel modules:
  
  1. Supply chain (third-party modules)
     Unsigned modules: anyone can provide a .ko file
     Fix: kernel lockdown mode (Secure Boot path)
          module signature verification:
          CONFIG_MODULE_SIG_FORCE=y
     
  2. Device driver exploitation
     NIC/GPU drivers parse external data (packets, frames)
     Buffer overflows in driver = kernel memory corruption
     IOMMU (Input-Output Memory Management Unit) limits DMA blast
     
  3. Container escape via kernel modules
     A container can load kernel modules if:
       - Running as root with CAP_SYS_MODULE
       - Or in privileged container mode
     Once loaded: module can access full kernel, break isolation
     Fix: never run containers with CAP_SYS_MODULE
     Monitor: audit rules for init_module syscall
     
Module security commands:
  # Check if module signing is enforced
  cat /sys/kernel/security/lockdown
  
  # List loaded modules with signed status
  grep -r '' /sys/module/*/parameters/ 2>/dev/null
  
  # Prevent module loading (locked-down system)
  echo 1 > /proc/sys/kernel/modules_disabled
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Kernel modules are like plugins (safe to load/unload)" | Kernel modules run in Ring 0 with full kernel privileges. A buggy module can corrupt kernel data structures and crash the system. Loading a module from an unknown source is equivalent to running untrusted code as root - but worse. |
| "eBPF is just a better kernel module" | eBPF and kernel modules are for different use cases. eBPF: safe, sandboxed, observability/networking/security hooks. Modules: required for device drivers, new syscalls, new filesystems. eBPF cannot implement a new filesystem or NIC driver. |
| "You need to reboot to load a kernel module" | No, that's the point. Modules load at runtime with `insmod`/`modprobe`. Reboot is only needed for modules baked into the kernel image itself. LKMs are loaded dynamically while the system runs. |

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `insmod module.ko` | Load module from file |
| `modprobe module` | Load module + dependencies |
| `rmmod module` | Remove loaded module |
| `lsmod` | List loaded modules |
| `modinfo module.ko` | Show module metadata |
| `dmesg \| tail` | View module load/unload messages |
| `cat /proc/modules` | Raw module list with addresses |
| `ls /lib/modules/$(uname -r)/` | Available modules directory |
