---
id: LNX-096
title: "Kernel Crash Analysis (kdump, crash tool, kernel oops)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-062, LNX-087, LNX-093
used_by: LNX-097
related: LNX-087, LNX-097, LNX-062
tags: [kdump, crash-tool, kernel-oops, kernel-panic, vmcore, kexec, kernel-crash-dump, kernel-debug, crash-analysis, oops-message, call-trace, backtrace, crash-bt, crash-log, crash-ps, crash-vm, kernel-debugging, kasan, dmesg-oops]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 96
permalink: /technical-mastery/lnx/kernel-crash-analysis/
---

## TL;DR

When the Linux kernel crashes (oops or panic), `kdump` captures the kernel
memory as a crash dump (`/var/crash/vmcore`). The `crash` tool performs
post-mortem analysis: `crash /boot/vmlinux /var/crash/vmcore` gives an
interactive shell. Essential commands: `bt` (backtrace of crash), `log` (kernel
log buffer = last dmesg), `ps` (process list at crash), `vm PID` (virtual
memory of a process), `files PID` (open files). Kernel oops anatomy: read
the `IP:` (instruction pointer = which function crashed), `Call Trace:` (call
stack = how we got there), `RIP:` (64-bit instruction pointer), and the reason
(NULL pointer dereference, use-after-free, BUG_ON). `kernel.panic_on_oops=1`
makes oops trigger a panic (and thus kdump) instead of continuing.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-096 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | kdump, crash tool, kernel oops, kernel panic, vmcore, kexec, crash analysis |
| **Prerequisites** | LNX-062 (CPU), LNX-087 (tracing), LNX-093 (troubleshooting) |

---

### The Problem This Solves

**Problem 1**: A production kernel panicked at 2 AM. System rebooted. No
information is available about why. Without kdump: the only evidence is the
brief message on the console (if someone was watching) or the last dmesg
entries (which may have been cleared). With kdump: a complete memory snapshot
of the crashed kernel is saved to disk. The next morning, engineers can
analyze exactly which function crashed, which process triggered it, the full
kernel call stack, and the memory state at the time of the crash.

**Problem 2**: A vendor's kernel module causes occasional oops (NULL pointer
dereference) that doesn't panic the system but corrupts state over time.
Without kernel debug: "something is wrong with the vendor module" - no more
detail. With oops analysis: the exact line number in the module source, the
register values, the call trace showing which code path triggered the bug.
The vendor has everything they need to reproduce and fix the issue.

---

### Textbook Definition

**Kernel oops**: A non-fatal kernel error condition where the kernel detects
an illegal operation (NULL pointer dereference, BUG_ON() assertion, stack
corruption). The kernel logs extensive diagnostic information and may continue
running (possibly in a degraded state) or panic, depending on configuration.

**Kernel panic**: A fatal, non-recoverable kernel error. The kernel halts
immediately, displaying an error message. Triggered by: double fault, BUG()
macro, panic(), or `kernel.panic_on_oops=1` when an oops occurs.

**kdump**: A Linux mechanism for capturing the kernel's memory at crash time.
Uses kexec to pre-load a second ("capture") kernel into reserved memory. When
the production kernel crashes: kexec switches to the capture kernel, which
saves the crashed kernel's memory to disk as `vmcore`.

**crash tool**: Post-mortem analysis tool for kernel crash dumps. Provides
an interactive shell with commands to inspect the crashed kernel's state.

---

### Understand It in 30 Seconds

```bash
# === Reading a kernel oops message ===

# Example oops in dmesg:
# [12345.678901] BUG: kernel NULL pointer dereference,
#   address: 0000000000000008
# [12345.678902] #PF: supervisor read access in kernel mode
# [12345.678903] #PF: error_code(0x0000) - not-present page
# [12345.678904] PGD 0 P4D 0
# [12345.678905] Oops: 0000 [#1] SMP PTI
#
# [12345.678906] CPU: 3 PID: 12345 Comm: mymodule tainted: G OE
# [12345.678907] Hardware name: ... Dell ...
# [12345.678908] RIP: 0010:my_module_read+0x3c/0x80 [my_module]
#                           ^^^^^^^^^^^^^^^^^^^^^^^^
#                           FUNCTION that crashed: my_module_read
#                           offset 0x3c into the function (60 bytes)
#
# [12345.678909] RSP: 0018:ffffc90001234567 EFLAGS: 00010286
# [12345.678910] RAX: 0000000000000000 RBX: ffff888012345678 RCX: 0000000000000008
#                ^^^^^^^^^^^^^^^^^^^^^^^^^
#                RAX = 0 (NULL pointer that was dereferenced + 8 byte offset = 0x8)
#
# [12345.678911] Call Trace:
# [12345.678912]  <TASK>
# [12345.678913]  vfs_read+0x9c/0x180
# [12345.678914]  ksys_read+0x65/0xe0
# [12345.678915]  __x64_sys_read+0x19/0x20
# [12345.678916]  do_syscall_64+0x57/0x80
# [12345.678917]  entry_SYSCALL_64_after_hwframe+0x72/0xdc
# [12345.678918]  </TASK>
# Read BOTTOM to TOP for call stack:
# entry_SYSCALL_64 -> do_syscall_64 -> sys_read -> ksys_read
#   -> vfs_read -> my_module_read  <- CRASHED HERE

# === Decoding oops: addr2line (get exact source line) ===
# Get the kernel base address offset:
cat /proc/kallsyms | grep my_module_read
# ffffffffc0123456 t my_module_read  [my_module]

# my_module_read is at 0xffffffffc0123456
# Crash at my_module_read+0x3c = 0xffffffffc0123456 + 0x3c = 0xffffffffc0123492

# With debug symbols:
addr2line -e /lib/modules/$(uname -r)/extra/my_module.ko.debug 0x3c
# /src/my_module/my_module.c:87: my_module_read
# Line 87 in source! That's where the NULL dereference occurred.

# === kdump setup ===
# Install:
yum install -y kexec-tools crash  # RHEL/CentOS
apt install -y kdump-tools crash  # Ubuntu/Debian

# Reserve memory for crash kernel (in /etc/default/grub):
# GRUB_CMDLINE_LINUX="... crashkernel=auto"
# For manual: crashkernel=256M (256MB reserved for capture kernel)
# Apply:
grub2-mkconfig -o /boot/grub2/grub.cfg
# Reboot required for crashkernel parameter

# Enable kdump service:
systemctl enable kdump
systemctl start kdump
systemctl status kdump

# Verify kdump is loaded:
cat /proc/iomem | grep "Crash kernel"
# 62000000-6fffffff : Crash kernel  <- reserved memory range

# Test kdump (CAUTION: triggers system crash/reboot!):
# echo c > /proc/sysrq-trigger  # Force kernel crash for testing
# (Use only in test environments!)

# Configure dump path (/etc/kdump.conf):
cat /etc/kdump.conf
# path /var/crash          <- where to save vmcore
# core_collector makedumpfile -l --message-level 1 -d 31
#   -d 31: filter: skip free pages (reduce dump size)
#   -l: compress lzo

# === crash tool: analyze vmcore ===
# Open crash dump:
crash /boot/vmlinux-$(uname -r) /var/crash/vmcore
# (requires matching vmlinux debug info)
# Alternative: crash /usr/lib/debug/lib/modules/$(uname -r)/vmlinux /var/crash/vmcore

# crash> commands:
crash> bt
# Shows backtrace of the crash task (stack trace at time of panic)
# #0  machine_kexec at arch/x86/kernel/machine_kexec_64.c:380
# #1  __crash_kexec at kernel/crash_core.c:109
# #2  panic at kernel/panic.c:339
# #3  oops_end at arch/x86/kernel/dumpstack.c:368
# ...
# #9  my_module_read at /src/my_module/my_module.c:87

crash> bt -a
# Backtrace of ALL processes at time of crash (for analysis)

crash> log
# Shows kernel ring buffer (dmesg) at time of crash
# Includes the oops message, kernel version, etc.

crash> ps
# Process list at crash time:
# PID PPID CPU   TASK    ST    %MEM  VSZ  RSS  COMM
# 0     0    0  ... RU    0.0    0    0  [swapper/0]
# 1     0    0  ... IN    0.0   32    3  systemd
# 12345 1    3  ... RU   0.2  1234  567  myapp <- this was running!

crash> vm 12345
# Virtual memory map of process 12345 at crash time
# Shows all virtual memory areas (VMAs) with permissions

crash> files 12345
# Open file descriptors of process 12345 at crash time
# fd 0 (stdin), fd 1 (stdout), fd 2 (stderr), fd N (connections)

crash> sys
# System information: kernel version, uptime, hostname at crash time

crash> struct task_struct ffff888012345678
# Dump the task_struct of a process (kernel data structure)

crash> quit
```

---

### First Principles

```
Kernel oops anatomy:

1. Error classification:
   BUG: kernel NULL pointer dereference  <- NULL deref
   BUG: unable to handle page fault      <- invalid memory access
   BUG: KASAN: use-after-free            <- freed memory accessed
   BUG: kernel stack overflow            <- stack too deep
   WARN_ON: <condition>                  <- warning, not fatal
   BUG_ON: <condition>                   <- fatal assertion failure
   general protection fault              <- invalid memory segment
   
2. Address and access type:
   address: 0000000000000008
   ^ 8 bytes into NULL (= struct member offset)
   ^ Classic sign: accessing member of NULL pointer
   
   address: dead000000000100 (POISON_POINTER_DEREF)
   ^ Use-after-free: freed memory marked with poison value
   
3. CPU and task context:
   CPU: 3 PID: 12345 Comm: myapp Tainted: G OE
   ^ CPU number, PID, process name
   ^ Tainted: G = proprietary driver loaded
              O = out-of-tree module
              E = unsigned module
   
4. Instruction pointer (where crash occurred):
   RIP: 0010:my_module_read+0x3c/0x80 [my_module]
   ^ function name, offset in function, function length
   ^ Extract: function = my_module_read, offset = 0x3c
   
5. Registers at crash:
   RAX RBX RCX RDX RSI RDI RBP RSP
   R8-R15, CS, SS, EFLAGS
   ^ RAX often holds the NULL/invalid pointer value
   ^ RIP is the instruction that crashed
   
6. Call Trace (read bottom to top):
   entry_SYSCALL_64 <- user space called read()
   do_syscall_64
   __x64_sys_read
   ksys_read
   vfs_read
   my_module_read <- CRASHED HERE
   ^ Full execution path that led to crash

kdump / kexec mechanism:
  Boot time:
    crashkernel= parameter reserves memory (e.g., 256MB)
    kdump kernel + initramfs loaded into reserved memory via kexec_load()
    Reserved memory is marked off-limits to production kernel
    
  At crash time (panic() called):
    machine_kexec(): switches to capture kernel
    CPU switches to capture kernel's code at entry point
    Capture kernel boots with minimal init
    
  Capture kernel:
    Sees original kernel's memory as /dev/vmcore (old_mem)
    makedumpfile reads /dev/vmcore, writes to /var/crash/vmcore
    Applies filtering (skip free pages, compress)
    After save: reboots (or halts if configured)
    
  vmcore file:
    ELF format with PT_LOAD segments = physical memory ranges
    Header: registers, crashed CPU state
    crash tool maps virtual addresses to physical via page tables

crash tool architecture:
  Opens vmcore as read-only file
  Reads kernel's page tables to translate virtual addresses
  Knows kernel data structure layouts from vmlinux ELF debug info
  DWARF debug info in vmlinux: function names, line numbers, types
  
  bt (backtrace):
    Reads stack from crash task's kernel stack
    Unwinds frames using frame pointers or DWARF unwind info
    Resolves addresses to function names via kallsyms
  
  ps (process list):
    Reads init_task.tasks linked list (all processes in kernel)
    Dumps task_struct for each: pid, state, comm (name), mm
  
  vm (virtual memory):
    Reads process's mm_struct -> vma_list (virtual memory areas)
    Shows each VMA: start, end, flags, backing file
  
  log (kernel ring buffer):
    Reads log_buf[] from kernel memory
    Decodes prb (printk ring buffer) format

oops vs panic distinction:
  oops: NOT fatal by default
    Kernel logs the error, marks process as killed
    Tries to continue (may be unstable)
    Subsequent operations may fail or corrupt data
    
  panic: FATAL
    Kernel halts immediately
    Console shows panic message
    kdump triggered (if configured)
    
  kernel.panic_on_oops=1:
    Converts any oops to panic
    Triggers kdump for oops too (not just panics)
    Recommended for production: unstable after oops anyway
    
  kernel.panic=30:
    30 seconds after panic: automatic reboot
    Useful for production: recover without human intervention
```

---

### Thought Experiment

Analyzing a production kernel panic from kdump:

```bash
# Scenario: Critical database server panicked, kdump captured vmcore
# File: /var/crash/2024-05-17-14:32:00/vmcore

# Step 1: Open with crash tool
crash /usr/lib/debug/vmlinux-5.15.0-101-generic \
      /var/crash/2024-05-17-14:32:00/vmcore

# Step 2: View the crash log
crash> log
# [456789.123] BUG: kernel NULL pointer dereference, address: 0000000000000000
# [456789.124] RIP: 0010:nvme_complete_rq+0x48/0xc0 [nvme]
# [456789.125] Call Trace:
# [456789.126]  blk_mq_end_request+0x43/0x60
# [456789.127]  nvme_irq+0x123/0x200 [nvme]
# ...
# Conclusion: NVMe driver's interrupt handler crashed (NULL pointer)

# Step 3: Identify which process was running
crash> ps | grep -v "^  0" | head -5
# PID  PPID  CPU  TASK  ST  COMM
# 1234  890   3   addr  RU  postgres  <- active process at crash

# Step 4: Check for I/O in flight
crash> files 1234
# FD  TYPE  INODE  FILE   NAME
# 0   CHR         tty    /dev/tty
# 3   REG         12345  /var/lib/pgsql/data/base/16384/1249
# ^ Postgres had open files, was reading/writing at crash time

# Step 5: Examine NVMe module state
crash> mod -s nvme
# NAME    SIZE     TAINTED  OBJ_FILE
# nvme    98304    OE       /lib/modules/5.15.0-101/kernel/drivers/nvme/host/nvme.ko
# Tainted O = out-of-tree module (could be modified vendor version)

# Step 6: Check if driver version matches known bugs
# From crash log: nvme_complete_rq+0x48
# Translate to source line:
# addr2line -e nvme.ko.debug 0x48
# Result: nvme.c:435: nvme_complete_rq
# Line 435: struct nvme_ns *ns = req->rq_disk->private_data;
# ^ rq_disk is NULL! Disk was removed/unregistered while I/O in flight

# Conclusion: NVMe hot-remove race condition
# The NVMe drive was removed (or controller reset) while I/O was in flight
# I/O completion callback tried to access the device struct (now NULL)
# Fix: vendor NVMe driver update that handles device removal gracefully
```

---

### Mental Model / Analogy

```
Kernel oops/panic = airplane black box + flight recorder

Production server = airplane in flight
Kernel = autopilot system controlling everything

Kernel oops = "warning light" in cockpit
  Autopilot detected something wrong (NULL pointer, invalid state)
  Logs detailed diagnostic information
  Tries to continue flying (system stays up)
  But might be unstable (like flying with one engine)
  
Kernel panic = autopilot EMERGENCY SHUTDOWN
  Too dangerous to continue (double fault, critical corruption)
  System immediately stops
  Like an emergency landing (unplanned reboot)

kdump = flight data recorder (black box):
  Installed BEFORE the flight (kdump service running)
  Pre-loaded rescue kernel in reserved memory (co-pilot with recording equipment)
  When emergency occurs: rescue system takes over
    Main autopilot crashed? -> rescue system activates (kexec)
    Records everything into vmcore (saves black box data)
    Then lands the plane (reboots)

vmcore = black box data:
  Complete state of ALL systems at moment of crash
  Memory contents, CPU registers, running processes
  Can be analyzed AFTER the flight by engineers (crash tool)

crash tool = accident investigation lab:
  bt (backtrace): "what was the plane doing exactly?"
  log: "what did the instrumentation log before crash?"
  ps: "which systems were active at time of crash?"
  vm: "what memory was each system using?"
  
addr2line = flight manual lookup:
  "RIP: nvme_complete_rq+0x48" = "autopilot step 72 in procedure NVMe-read"
  addr2line: "procedure NVMe-read step 72 = manual page 435"
  -> exact source code line where the crash occurred

kernel.panic_on_oops=1 = "declare emergency on ANY warning":
  Any warning (oops) -> treat as full emergency (panic + kdump)
  Trade-off: more downtime (crash+reboot vs continue degraded)
  But: ensures every problem is recorded (no missed incidents)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Difference between oops (non-fatal) and panic (fatal). `dmesg` for kernel
error messages. What a kernel crash looks like in system logs. kdump as a
concept (captures memory on crash). Common crash causes: NULL dereference,
BUG_ON, stack overflow.

**Level 2:**
Reading oops messages: RIP, Call Trace, tainted flag. `kernel.panic_on_oops`
sysctl. kdump setup: `crashkernel=` boot parameter, kdump service. `crash`
tool basics: bt, log, ps. Using `addr2line` to get source line from function+offset.
`/var/crash/` directory structure.

**Level 3:**
crash tool advanced commands: vm (memory map), files (open files), struct
(kernel structures), module (module list), kmem (kernel memory). makedumpfile
filter levels (-d flag). KASAN (Kernel Address Sanitizer): use-after-free
detection in kernels compiled with KASAN. Oops taint flags meaning (G, O, E,
W, etc.). `kernel.core_pattern` for userspace core dumps. Decoding register
values in oops messages.

**Level 4:**
kdump over network (netdump): save vmcore to remote server instead of local
disk. makedumpfile compression levels and formats (lzo, snappy, zlib). Filtered
dumps for large RAM (256GB server: makedumpfile can filter 90% of pages).
Debugging live kernel with `crash` + `/proc/kcore` (live analysis without crash).
KGDB (kernel gdb): live kernel debugging via serial or USB with full gdb.
Kernel function tracing with kprobes (see LNX-087) as alternative to crash dumps.

**Level 5:**
Kernel KASAN internals: shadow memory (1 byte per 8 bytes of memory), red zones,
quarantine queue for freed objects. KMSAN (Kernel Memory SANitizer): uninitialized
memory read detection. UBSAN (Undefined Behavior SANitizer) for kernel. Kernel
objtool: static analysis for stack validation and ORC unwinder generation.
Writing a kernel panic notifier (`panic_notifier_list`): execute custom code
before kdump captures (e.g., flush application buffers, log custom state).
RISC-V and ARM64 kernel crash analysis: different register sets, different
call convention. kdump in Kubernetes: crash-recovery from container crashes
requires kexec at host level.

---

### Code Example

**BAD - kernel module with NULL dereference (common mistake):**
```c
// BAD: kernel module that will cause a NULL pointer oops
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>

struct my_device {
    int state;
    char *data;
};

static struct my_device *global_device;  // Initially NULL

static ssize_t my_read(struct file *file,
                       char __user *buf,
                       size_t count,
                       loff_t *ppos)
{
    // BAD: no NULL check before dereferencing!
    int state = global_device->state;  // CRASH if global_device == NULL
    //          ^^^^^^^^^^^^^^^^^^^^^^
    // If device not initialized: BUG: kernel NULL pointer dereference
    // RIP: my_read+0x18/0x40 [my_module]
    // RAX: 0000000000000000 (NULL pointer)
    
    // Also BAD: no NULL check on data pointer
    char *data = global_device->data;
    // If data is NULL: second dereference = crash at data+0 or later
    
    return copy_to_user(buf, data, count);
}
```

```c
// GOOD: defensive NULL checks and KASAN-safe patterns
static ssize_t my_read_safe(struct file *file,
                            char __user *buf,
                            size_t count,
                            loff_t *ppos)
{
    // GOOD: check for NULL before any dereference
    if (unlikely(!global_device)) {
        pr_warn("my_module: read called but device not initialized\n");
        return -ENODEV;
    }
    
    // GOOD: check data pointer too
    if (unlikely(!global_device->data)) {
        pr_err("my_module: device data is NULL (init incomplete?)\n");
        return -ENOMEM;
    }
    
    // GOOD: bounds check before copy
    size_t avail = strlen(global_device->data);
    count = min(count, avail - (size_t)*ppos);
    if (count == 0)
        return 0;
    
    if (copy_to_user(buf, global_device->data + *ppos, count))
        return -EFAULT;
    
    *ppos += count;
    return count;
}
```

**GOOD - reading and understanding an oops:**
```bash
# Oops from production:
# [  123.456789] BUG: kernel NULL pointer dereference,
#   address: 0000000000000008
# [  123.456790] RIP: 0010:nvme_ns_head_submit_bio+0x48/0xc0 [nvme-core]
# [  123.456791] Code: 48 8b 47 08  <- instruction bytes at crash
# [  123.456792] RSP: 0018:ffffc90001234xxx EFLAGS: 00010246
# [  123.456793] RAX: 0000000000000000  <- RAX = 0 (NULL)
# [  123.456794] RBX: ffff888012345678  <- RBX = some struct
# [  123.456795] Call Trace:
# [  123.456796]  submit_bio+0x6c/0x150
# [  123.456797]  ext4_io_submit+0x45/0x60
# [  123.456798]  ext4_writepages+0x123/0x800
# [  123.456799]  do_writepages+0x4c/0x120

# Analysis:
# 1. Address: 0x0000000000000008 = 8 bytes into a NULL struct
#    = struct member at offset 8 of a NULL pointer
#    nvme_ns_head_submit_bio+0x48: accessing ptr->field where ptr = NULL

# 2. Call trace (bottom to top):
#    do_writepages <- OS writing dirty pages to disk
#    ext4_writepages <- ext4 filesystem layer
#    ext4_io_submit <- submitting I/O
#    submit_bio <- block layer
#    nvme_ns_head_submit_bio <- NVMe driver layer <- CRASH

# 3. Decode the exact instruction:
# 48 8b 47 08 = mov rax, [rdi+0x8]  (x86-64 instruction)
# = load value from address [rdi+8] into rax
# rdi was 0 (NULL struct pointer)! So: load from address 8 = fault

# 4. Get source line:
addr2line -e /lib/modules/$(uname -r)/kernel/drivers/nvme/\
  host/nvme-core.ko.debug 0x48
# Result: drivers/nvme/host/core.c:750: nvme_ns_head_submit_bio
# Line 750: struct nvme_ns *ns = nvme_find_path(head);
# If nvme_find_path returns NULL and not checked: crash on ns->... at +8
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Kernel panic is always a kernel bug" | Kernel panics can be triggered by: (1) hardware failures (bad RAM, CPU errors, failing disks), (2) buggy third-party modules (the tainted flag in the oops indicates if non-mainline code was loaded), (3) hardware incompatibility (driver bug for specific hardware), (4) misconfigured kernel parameters, (5) genuine kernel bugs (rare in stable kernels). Check the Tainted flag: `G` = proprietary module, `O` = out-of-tree module. If tainted: the vendor's module is the prime suspect. KASAN-detected issues (use-after-free) are almost always code bugs in drivers or modules. |
| "kdump requires significant RAM overhead" | kdump's reserved memory (`crashkernel=`) is typically 128-256MB for systems with < 64GB RAM, and can be `auto` (kernel calculates). The capture kernel is minimal (no GUI, no full init). For large RAM systems: makedumpfile with filtering (-d 31) can reduce the vmcore from 128GB to 2-4GB by skipping free pages, zero pages, and cache. Modern kdump implementations efficiently handle even 1TB+ memory servers. The overhead: reserved memory (128-256MB permanently unavailable) + crash analysis overhead (makedumpfile runs only at crash time). |
| "The Call Trace shows the cause of the crash" | The Call Trace shows the EXECUTION PATH that LED to the crash. The function at the TOP of the trace is where the crash occurred (the symptom). The ROOT CAUSE is typically in the calling code: which function passed an invalid pointer? which function freed memory too early? Look at the functions just BELOW the crash point in the trace - they are the callers that provided the bad state. In the nvme example: the crash is in nvme_ns_head_submit_bio, but the actual bug might be in the NVMe multipath code that returned a NULL pointer to it. |
| "Only kernel code crashes can be analyzed with crash tool" | `crash` can analyze any kernel-level issue: (1) memory corruption in userspace process (via crash> vm, examining MMU state), (2) hung processes (why is a process stuck?), (3) driver state at crash time, (4) network socket state (via `crash> net`), (5) filesystem state (via `crash> files`). Additionally, `crash` works on LIVE systems with `/proc/kcore` for non-destructive kernel inspection (limited but useful). The crash tool is the universal kernel forensics tool. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: kdump not capturing ===

# Check kdump service:
systemctl status kdump
# Active: failed (Reason: no crashkernel= parameter in kernel cmdline)

# Verify crashkernel parameter:
cat /proc/cmdline | grep crashkernel
# If absent: add to GRUB_CMDLINE_LINUX, then grub2-mkconfig + reboot

# Verify reserved memory:
cat /proc/iomem | grep -i crash
# 100000000-17fffffff : System RAM
# 17c000000-17fffffff : Crash kernel  <- should see this

# Test kdump (lab only!):
# echo c > /proc/sysrq-trigger
# System will crash and reboot, vmcore saved to /var/crash/

# === Failure: crash tool can't load vmcore ===
crash /boot/vmlinux-5.15.0 /var/crash/vmcore
# crash: invalid kernel virtual address: ffffffff81234567
# Cause: vmlinux doesn't match kernel (wrong version)

# Get correct vmlinux:
# For RHEL/CentOS: kernel-debuginfo package
yum install -y kernel-debuginfo-$(uname -r)
# vmlinux at: /usr/lib/debug/lib/modules/$(uname -r)/vmlinux

# For Ubuntu:
apt install linux-image-$(uname -r)-dbgsym
# vmlinux at: /usr/lib/debug/boot/vmlinux-$(uname -r)

# === Analyzing hardware-triggered panics ===
# MCE (Machine Check Exception): hardware errors
dmesg | grep -i "mce\|hardware error\|corrected"
# [  123.4] mce: Hardware Error: CPU 0, CORE 0
# [  123.4] HARDWARE ERROR: Bank 5: 8c000000000000
# [  123.4] MCA: DRAM ECC error detected

# Decode MCE code:
mcelog --client
# Or: rasdaemon for persistent hardware error logging

# EDAC (Error Detection And Correction) for RAM errors:
cat /sys/devices/system/edac/mc/mc0/ue_count  # Uncorrectable errors
cat /sys/devices/system/edac/mc/mc0/ce_count  # Correctable errors
# ue_count > 0: RAM failure - replace DIMM

# === crash tool: useful commands reference ===
# crash> help        <- list all commands
# crash> bt          <- backtrace of crashed process
# crash> bt -a       <- backtrace all processes
# crash> log         <- kernel ring buffer at crash time
# crash> ps          <- process list at crash
# crash> ps -k       <- kernel threads only  
# crash> vm 1234     <- virtual memory map of PID 1234
# crash> files 1234  <- open files of PID 1234
# crash> net         <- network state (sockets, interfaces)
# crash> mod         <- loaded kernel modules
# crash> sys         <- kernel version, uptime, hostname
# crash> struct task_struct <addr>  <- dump task_struct
# crash> kmem -i     <- kernel memory info
# crash> swap        <- swap usage at crash time
```

---

### Related Keywords

**Foundational:**
LNX-062 (CPU), LNX-087 (tracing and debugging)

**Builds on this:**
LNX-097 (Linux security incidents)

**Related:**
LNX-093 (performance troubleshooting)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `dmesg | grep -i "oops\|bug\|panic"` | Find kernel errors in log |
| `systemctl enable kdump` | Enable crash dump capture |
| `cat /proc/iomem | grep Crash` | Verify kdump memory reserved |
| `crash /vmlinux /var/crash/vmcore` | Open crash dump |
| `crash> bt` | Backtrace at crash |
| `crash> log` | Kernel log at crash |
| `crash> ps` | Process list at crash |
| `addr2line -e module.ko.debug 0xOFFSET` | Get source line |

**3 things to remember:**
1. Oops = non-fatal kernel error (system may continue unstably). Panic = fatal halt. `kernel.panic_on_oops=1` converts any oops to a panic, triggering kdump.
2. Read the Call Trace BOTTOM to TOP: bottom = entry point (syscall), top = where crash occurred. The crash function is at the top; the root cause is in its caller.
3. kdump requires `crashkernel=auto` boot parameter AND `systemctl enable kdump` BEFORE a crash. You cannot enable it after the fact - set it up in advance on all production systems.

---

### Transferable Wisdom

Kernel crash analysis skills transfer to: JVM crash analysis (hs_err_pid
files are equivalent to kernel oops - signal name, thread stack, heap state),
C/C++ core dump analysis (`gdb ./program core` = equivalent to `crash vmlinux
vmcore`), .NET crash dumps (`createdump` + `dotnet-dump`), Go crash dumps
(goroutine dump on panic), Node.js v8 heap snapshots. The debugging methodology
is universal: identify where the crash occurred (RIP/IP = instruction pointer),
read the call stack (backtrace), examine the state at crash time (registers,
memory). The principle "capture state at the moment of failure" (kdump for
kernel, core dumps for processes) prevents the common frustration of "the
problem is gone, I can't reproduce it." Always configure crash capture on
production systems BEFORE incidents occur.

---

### The Surprising Truth

Linux kernel oops messages contain the complete CPU register state at the
time of crash. A skilled engineer can reconstruct exactly what the code was
doing: RAX/RBX/RCX are function arguments (calling convention). RSP points
to the stack. RIP points to the crashing instruction. The raw instruction
bytes in the oops (the "Code:" line: `48 8b 47 08`) can be decoded by hand
using the x86-64 instruction reference: `48 8b` = REX.W MOV r/m64; `47 08`
= address [rdi+0x8]. Translation: "load 8 bytes from [rdi+8] into rax." If
rdi was NULL (0): crash at address 8. This information is enough to reconstruct
the bug WITHOUT the source code.

The kdump mechanism using kexec was originally designed for rolling kernel
upgrades without rebooting (loading a new kernel in place). The same mechanism
was repurposed for crash dump capture. kexec (kernel execute) can load a new
kernel into memory and switch to it - used for: (a) live kernel patching
(kpatch/livepatch for security fixes), (b) kdump capture kernel, (c) fast
reboot (kexec reboot skips BIOS/UEFI initialization, 10x faster than hardware
reset). Modern Kubernetes uses kexec-based fast reboot for OS upgrades in
managed Kubernetes services to reduce node restart time from 5 minutes to 30
seconds.

---

### Mastery Checklist

- [ ] Can read a kernel oops message and identify the crashed function, call trace, and likely cause
- [ ] Has configured kdump with crashkernel= parameter and knows how to verify it is active
- [ ] Can open a vmcore with the crash tool and run bt, log, ps commands
- [ ] Understands the difference between kernel oops and panic, and why panic_on_oops is recommended
- [ ] Can use addr2line to translate a function+offset from an oops to the exact source line

---

### Think About This

1. A production server crashes every 7-10 days without any obvious pattern.
   kdump is not configured. Design a complete observability strategy for
   capturing the next crash: what needs to be set up before the next crash
   occurs? What information would you want to capture automatically? How would
   you preserve the vmcore (large file) efficiently on a server with limited
   disk space? What would be your analysis workflow the next morning?

2. A kernel oops shows: RIP: nvme_complete_rq+0x48 with address 0 and the
   tainted flag shows 'O' (out-of-tree module). The call trace shows: nvme IRQ
   handler -> NVMe completion -> crash. The vendor claims "this is a kernel
   bug." Walk through the evidence available in the oops message that you would
   use to evaluate this claim, and describe what additional evidence you would
   gather to determine if it is the vendor's module or a kernel bug.

3. Your team proposes "we don't need kdump because we have excellent application
   logging." Argue both for and against this position. In what scenarios would
   application logging be sufficient, and in what scenarios is kernel-level crash
   capture irreplaceable? What is the overlap between application observability
   (distributed tracing, structured logs) and kernel crash analysis?

---

### Interview Deep-Dive

**Foundational:**
Q: What is kdump and how do you set it up on a Linux system?
A: KDUMP OVERVIEW: kdump is the Linux kernel crash dump mechanism. When the kernel crashes (panic), kdump saves a complete snapshot of the kernel's memory to disk (/var/crash/vmcore). This allows post-mortem analysis of WHAT caused the crash, WHICH process was running, and WHAT state the system was in - exactly what you need to diagnose and fix kernel bugs or hardware issues. HOW IT WORKS: kdump uses kexec to pre-load a second "capture" kernel into a reserved memory region. At boot: you reserve memory with `crashkernel=auto` boot parameter. This memory is off-limits to the normal kernel. When the normal kernel panics: kexec switches execution to the capture kernel (in the reserved memory). The capture kernel boots minimally, reads the crashed kernel's memory via /dev/vmcore, and saves it to disk with makedumpfile. SETUP STEPS: (1) Add `crashkernel=auto` to GRUB_CMDLINE_LINUX in /etc/default/grub; (2) Run `grub2-mkconfig -o /boot/grub2/grub.cfg` and reboot; (3) Install: `yum install kexec-tools crash kernel-debuginfo`; (4) Enable: `systemctl enable --now kdump`; (5) Verify: `cat /proc/iomem | grep Crash` (should show reserved memory range); (6) Test in lab: `echo c > /proc/sysrq-trigger` (triggers crash for testing). ANALYSIS: After a crash, vmcore is in /var/crash/. Analyze with: `crash /usr/lib/debug/lib/modules/$(uname -r)/vmlinux /var/crash/vmcore`. Commands: `bt` (backtrace), `log` (dmesg at crash), `ps` (processes). PRODUCTION RECOMMENDED SETTINGS: `/etc/kdump.conf`: `path /var/crash` and `core_collector makedumpfile -l --message-level 1 -d 31` (filter free pages to reduce dump size from 128GB to ~5GB). Also set `kernel.panic_on_oops=1` and `kernel.panic=30` (reboot 30 seconds after panic to restore service automatically).

**Expert:**
Q: You receive a vmcore from a kernel panic. Walk through your complete analysis workflow to identify the root cause.
A: COMPLETE VMCORE ANALYSIS WORKFLOW: (1) DETERMINE KERNEL VERSION AND MATCH DEBUG SYMBOLS: `crash --version` then open: `crash /path/to/vmlinux /var/crash/vmcore`. If vmlinux doesn't match: get exact kernel version with `strings vmcore | grep "Linux version"` then install matching kernel-debuginfo package. (2) GET THE CRASH SUMMARY: `crash> sys` - shows kernel version, hostname, uptime, crash time. `crash> log` - the entire kernel ring buffer up to crash. This is your PRIMARY evidence: the oops message with RIP, registers, and Call Trace. (3) IDENTIFY THE CRASH FUNCTION: From the log: `RIP: 0010:function_name+0xOFFSET/0xTOTAL [module_name]`. The function is where the crash occurred. Get source line: `addr2line -e /path/to/module.ko.debug 0xOFFSET`. (4) READ THE CALL TRACE (bottom to top): identifies the execution path. Entry point (syscall) is at the bottom; crash is at the top. The function BELOW the crash function is the caller that passed bad state. (5) EXAMINE REGISTER VALUES: From the log: RAX RBX RCX etc. For NULL pointer: RAX=0 or other register=0. For use-after-free: register contains POISON value (dead000000000100). (6) IDENTIFY THE CRASHED PROCESS: `crash> ps` then look for task in "RU" (running) state. `crash> bt -a` to see all processes' stacks (some may be in syscalls, some sleeping). (7) EXAMINE THE CRASH TASK: `crash> bt` (backtrace of crashed task specifically). `crash> task` (task_struct details). `crash> vm PID` (memory map). (8) CHECK FOR MODULES: `crash> mod` - are there out-of-tree modules? Tainted kernel? O (out-of-tree) or E (unsigned) taint = prime suspect. (9) CORRELATE WITH HARDWARE: check for MCE events in `crash> log`. Was disk I/O in flight? `crash> files <PID>` shows open file descriptors. (10) DOCUMENT CONCLUSION: "Crash was in function X, caused by NULL pointer at offset Y. Called by function Z. Process 1234 (myapp) was running. Module ABC (out-of-tree) was loaded and its interrupt handler was in the call chain. Root cause hypothesis: race condition in ABC module's device removal path. Recommended action: update ABC module to version N.N which fixes CVE-YYYY-NNNN."
