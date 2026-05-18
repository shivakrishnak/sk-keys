---
id: LNX-103
title: "Custom Linux Kernel Build and Configuration"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-028, LNX-030, LNX-079
used_by: LNX-107, LNX-111
related: LNX-028, LNX-030, LNX-079, LNX-107, LNX-111
tags: [kernel-build, kernel-configuration, menuconfig, kconfig, kernel-compile, make-bzimage, kernel-modules, grub-kernel, kernel-parameters, config-boot, kconfig-fragments, minimized-kernel, embedded-linux, kernel-hardening-config, kernel-lockdown, kcov, kasan, linux-6.x, kernel-version, kernel-patches, kernel-patches-workflow]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 103
permalink: /technical-mastery/lnx/custom-linux-kernel-build/
---

## TL;DR

Building a custom Linux kernel requires: **(1)** Get source (`git clone
torvalds/linux` or tarball); **(2)** Configure (`make menuconfig`, `make
localmodconfig` to start from running kernel); **(3)** Compile
(`make -j$(nproc) bzImage modules`); **(4)** Install
(`make modules_install && make install`); **(5)** Update bootloader
(`update-grub` or grub2-mkconfig). Key use cases: (a) minimal kernel for
embedded/containers (strip to 1-2MB), (b) security hardening (enable
CONFIG_SECURITY_LOCKDOWN_LSM, CONFIG_KASLR), (c) performance tuning (HZ
rate, PREEMPT model), (d) enabling experimental features (eBPF CO-RE,
io_uring). `make localmodconfig` + `make kvm_guest.config` = practical
starting point for VM kernels. Warning: always keep previous kernel
in GRUB as fallback - testing a new kernel that panics is easily
recovered from if you can reboot to the old one.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-103 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | kernel build, kconfig, menuconfig, custom kernel, kernel modules, minimal kernel, kernel hardening |
| **Prerequisites** | LNX-028 (kernel basics), LNX-030 (boot process), LNX-079 (kernel tuning) |

---

### The Problem This Solves

**Problem 1**: A container-optimized Linux distribution (like Bottlerocket, Flatcar)
needs a kernel with NO unused drivers (no USB, no PCI devices not in the hardware,
no filesystem types not used). A stock RHEL 8 kernel: ~10MB compressed, loads
dozens of modules for hardware you don't have. A minimized container-host kernel:
2-3MB, 30% less memory at boot, faster boot, smaller attack surface (fewer
kernel code paths = fewer potential vulnerabilities).

**Problem 2**: A security researcher needs to test a kernel patch for CVE-2022-0847
(Dirty Pipe). The patch is in the upstream kernel but not yet backported to the
distribution kernel. Custom build: apply the upstream patch to the current
distribution kernel, verify it compiles, deploy to test VM, verify the CVE
is no longer exploitable.

---

### Textbook Definition

**Linux kernel build system**: The `kbuild` system. Configuration managed by
`Kconfig` files (distributed throughout the kernel source tree). User interface:
`make menuconfig` (ncurses), `make xconfig` (Qt), `make nconfig`. Configuration
stored in `.config` file.

**Kernel configuration options:**
| Type | Meaning |
|------|---------|
| `y` (yes/built-in) | Compiled into kernel vmlinux |
| `m` (module) | Compiled as loadable module (.ko) |
| `n` (not set) | Not compiled |

**Key artifacts after build:**
| File | Description |
|------|-------------|
| `arch/x86/boot/bzImage` | Compressed bootable kernel image |
| `vmlinux` | Uncompressed ELF kernel (for debugging) |
| `System.map` | Kernel symbol table |
| `*.ko` files | Loadable kernel modules |

---

### Understand It in 30 Seconds

```bash
# === Full kernel build walkthrough ===

# 1. Install build dependencies:
# RHEL/CentOS:
yum install -y gcc make bc openssl-devel elfutils-libelf-devel \
    flex bison perl ncurses-devel rpm-build

# 2. Get kernel source:
# Method A: Official tarball:
curl -O https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.tar.xz
tar xf linux-6.6.tar.xz
cd linux-6.6/

# Method B: Git (for kernel development):
git clone --depth=1 https://github.com/torvalds/linux.git
cd linux/

# 3. Configure the kernel:

# Option A: Start from running kernel config (best for first build):
cp /boot/config-$(uname -r) .config
make olddefconfig  # apply new options with their defaults

# Option B: Minimal config for current hardware:
make localmodconfig  # only enable modules currently loaded!
# < This dramatically reduces build time >

# Option C: Interactive menu (for exploration):
make menuconfig
# Navigate: arrow keys, Enter to select, Y/M/N to set
# Search: press / to search for option name

# Option D: Base VM config + modifications:
make kvm_guest.config  # pre-tuned for VMs (no physical device drivers)

# 4. Enable specific features (direct .config editing):
# Enable kernel lockdown (security):
echo "CONFIG_SECURITY_LOCKDOWN_LSM=y" >> .config
echo "CONFIG_LOCK_DOWN_KERNEL_FORCE_INTEGRITY=n" >> .config
# Regenerate with new options resolved:
make olddefconfig

# 5. Compile (most time-consuming step):
# -j$(nproc): parallel jobs = number of CPU cores
time make -j$(nproc) bzImage modules
# On 8-core machine with SSD: ~10-15 minutes
# On 2-core VM: ~45-90 minutes

# Check output:
ls -la arch/x86/boot/bzImage
# -rw-r--r-- 1 root root 12345678 May 16 14:00 arch/x86/boot/bzImage
file arch/x86/boot/bzImage
# Linux kernel x86 boot executable bzImage

# 6. Install:
make modules_install  # installs .ko files to /lib/modules/$(kernel-version)/
make install          # copies bzImage, System.map to /boot/, updates symlinks

# 7. Update GRUB:
# Debian/Ubuntu:
update-grub
# RHEL/CentOS:
grub2-mkconfig -o /boot/grub2/grub.cfg  # BIOS
# or:
grub2-mkconfig -o /boot/efi/EFI/redhat/grub.cfg  # UEFI

# 8. Reboot to new kernel:
reboot
# Select new kernel at GRUB menu (or it's default)

# Verify:
uname -r
# 6.6.0  <- custom built kernel!

# If boot fails: at GRUB, select PREVIOUS kernel
# (kerbuild installs new kernel without removing old)
```

---

### First Principles

```
Why custom kernel builds matter:

The Linux kernel is a single codebase supporting:
  - Embedded systems (IoT sensors, 64KB RAM)
  - Desktop PCs (human interaction, USB, audio)
  - Server systems (high throughput, ECC memory, NUMA)
  - Supercomputers (MPI, high-speed interconnects)
  - Mobile devices (ARM, power optimization)
  - Container hosts (minimal footprint, security)

This breadth requires: configurability.
  A single precompiled kernel binary cannot optimally serve all.
  Distribution kernels make conservative choices:
  - Include broad hardware support (you might have any hardware)
  - Enable many filesystem types (you might use any)
  - Use general-purpose scheduler settings
  - Include debugging infrastructure (safer for users)
  
  Custom kernel: optimize for specific workload.

Kconfig system:
  Every feature/driver is a Kconfig entry
  Dependencies: "FEATURE_X depends on FEATURE_Y"
  Auto-resolved: enabling X auto-enables Y if required
  Stored in: .config file (plain text, one option per line)
  
  Example .config entries:
  CONFIG_EXT4_FS=y               # ext4 built-in
  CONFIG_BTRFS_FS=m              # btrfs as module
  CONFIG_FAT_FS=n                # FAT not compiled
  # CONFIG_FAT_FS is not set     # alternative "not set" form

Build process internals:
  1. Kconfig reads all Kconfig files, resolves dependencies
  2. C preprocessor: CONFIG_X options become #define CONFIG_X
  3. GCC compiles each subsystem into object files
  4. Linker links all objects into vmlinux (ELF executable)
  5. objcopy strips, compress with gzip/lzo/xz -> vmlinuz
  6. arch-specific boot stub prepended -> bzImage
  
Versioning:
  EXTRAVERSION in Makefile: customize kernel name
  Example: Linux 6.6.0-mykernel-20240516 (customized)
  
  In .config:
  CONFIG_LOCALVERSION="-mykernel-20240516"
  Result: uname -r -> 6.6.0-mykernel-20240516

Key configuration areas:

PREEMPTION model (scheduler responsiveness):
  CONFIG_PREEMPT_NONE (server default):
    No preemption in kernel code paths
    Best throughput (fewer context switches)
    Worst latency (kernel code holds CPU until done)
    For: web servers, databases, batch jobs
    
  CONFIG_PREEMPT_VOLUNTARY:
    Code can voluntarily yield at specific points
    Balance: good throughput, decent latency
    For: general-purpose desktops
    
  CONFIG_PREEMPT (full preemption):
    Kernel code can be preempted anywhere safe
    Best latency (responsive to interrupts)
    Worst throughput (more context switches)
    For: real-time applications, audio workstations
    
  CONFIG_PREEMPT_RT (PREEMPT-RT patch):
    Not in mainline kernel, separate patchset
    Hard real-time latency guarantees (<100 microseconds)
    For: industrial control, medical devices

Timer frequency (HZ):
  CONFIG_HZ_100 (100 ticks/second = 10ms tick):
    Low overhead, good for servers
    Wakes up processes every 10ms minimum
    Good: battery life, server throughput
    
  CONFIG_HZ_250 (250 ticks/second = 4ms tick):
    Balanced, desktop default in many distros
    
  CONFIG_HZ_1000 (1000 ticks/second = 1ms tick):
    High overhead, best timer precision
    Wastes CPU on timer interrupts on servers
    For: low-latency trading, real-time applications

Security hardening options:
  CONFIG_RANDOMIZE_BASE (KASLR):
    Kernel Address Space Layout Randomization
    Randomizes kernel load address at boot
    Mitigates: kernel pointer leaks (attacker can't predict address)
    
  CONFIG_SECURITY_LOCKDOWN_LSM:
    Prevents user-space from modifying running kernel
    Blocks: loading unsigned modules, /dev/mem access, kprobes
    Levels: INTEGRITY (sign checking), CONFIDENTIALITY (stricter)
    Enabled by UEFI Secure Boot on most distros
    
  CONFIG_SLAB_FREELIST_RANDOM:
    Randomize slab allocator freelist
    Mitigates: heap spray attacks
    
  CONFIG_FORTIFY_SOURCE:
    Compile-time and runtime buffer overflow detection
    For standard library functions (memcpy, strcpy etc.)
```

---

### Thought Experiment

Building a minimal container-host kernel:

```bash
# Goal: minimal kernel for a container host
# Requirements: Docker/containerd, NVMe, 10Gbps networking, btrfs
# Target: <4MB compressed kernel, 30-second boot time, minimal memory

# Start: allnoconfig (everything disabled)
make allnoconfig  # generates .config with everything off

# Enable minimum required features using kconfig fragments:
cat > minimal-container.config << 'EOF'
# Base system
CONFIG_64BIT=y
CONFIG_SMP=y
CONFIG_PRINTK=y
CONFIG_MODULES=y
CONFIG_MODULE_UNLOAD=y

# Filesystem support
CONFIG_TMPFS=y
CONFIG_PROC_FS=y
CONFIG_SYSFS=y
CONFIG_DEVTMPFS=y
CONFIG_EXT4_FS=y
CONFIG_BTRFS_FS=y
CONFIG_OVERLAY_FS=y  # required for Docker overlay2

# Block devices
CONFIG_NVME_CORE=y
CONFIG_BLK_DEV_NVME=y

# Networking
CONFIG_NET=y
CONFIG_INET=y
CONFIG_VETH=y  # virtual ethernet (container networking)
CONFIG_BRIDGE=y  # bridge networking
CONFIG_NETFILTER=y
CONFIG_NF_TABLES=y  # nftables
CONFIG_IP_NF_IPTABLES=y

# Container-specific
CONFIG_NAMESPACES=y
CONFIG_UTS_NS=y
CONFIG_IPC_NS=y
CONFIG_PID_NS=y
CONFIG_NET_NS=y
CONFIG_CGROUPS=y
CONFIG_CGROUP_FREEZER=y
CONFIG_CPUSETS=y
CONFIG_CGROUP_CPUACCT=y
CONFIG_CGROUP_BLKIO=y
CONFIG_MEMCG=y
CONFIG_SECCOMP=y

# Security
CONFIG_SECURITY=y
CONFIG_SECURITY_SELINUX=y
CONFIG_RANDOMIZE_BASE=y  # KASLR
EOF

# Merge fragments into .config:
./scripts/kconfig/merge_config.sh .config minimal-container.config

# Resolve unresolved dependencies:
make olddefconfig

# Build:
time make -j$(nproc) bzImage modules 2>&1 | tail -5
# real 4m23s  <- only 4 minutes for minimal kernel!

# Check kernel size:
ls -lh arch/x86/boot/bzImage
# -rw-r--r-- ... 2.8M May 16 14:22 arch/x86/boot/bzImage
# 2.8MB vs 10MB for distribution kernel!

# Functional test in QEMU (before deploying to real hardware):
qemu-system-x86_64 \
    -kernel arch/x86/boot/bzImage \
    -append "console=ttyS0 root=/dev/vda rw" \
    -drive file=test-disk.img,format=raw \
    -enable-kvm \
    -nographic
# If boot successful: deploy to test hardware
```

---

### Mental Model / Analogy

```
Kernel build = building a custom car for a specific racetrack

Factory car (distribution kernel):
  Designed for "all roads" (all hardware, all use cases)
  Includes: radio, AC, rear seats, spare tire compartment
  These are "all road" features (useful for some drivers)
  On a racetrack: radio, AC, rear seats are dead weight
  
Custom race car (custom kernel):
  Remove everything not needed for THIS race (this workload)
  Disable: USB audio (no sound card on servers)
  Disable: FAT filesystem (no Windows-compatible drives needed)
  Disable: Bluetooth (no Bluetooth on servers)
  Tune: engine (scheduler for server throughput, not desktop responsiveness)
  Tune: suspension (HZ=100 for server, not HZ=1000 for low-latency)
  
Kconfig = parts catalog for custom build:
  CONFIG_USB_AUDIO=y: "include USB audio support"
  CONFIG_USB_AUDIO=m: "include as optional addon (loadable module)"
  CONFIG_USB_AUDIO=n: "don't include (saves space, build time)"
  
  Kconfig dependencies = parts compatibility:
  "USB audio requires USB core"
  If you disable USB core: USB audio is automatically disabled too
  
.config = build order document:
  Written after you make choices
  Passed to factory (compiler) to build your custom kernel
  Reproducible: same .config = same kernel (deterministic)
  
make menuconfig = interactive parts catalog browser:
  Browse categories: Networking, Filesystems, Security
  Navigate to exact component
  Toggle Y/M/N (built-in, module, excluded)
  
make bzImage = factory assembly:
  Compiler builds each component (subsystem)
  Linker assembles into one executable
  Compressor shrinks it (gzip/xz) -> bzImage
  
localmodconfig = "take only parts I currently use":
  Like: "look at my current car, list only the parts installed"
  Then order exactly those parts for the new car
  Result: minimal config for THIS machine's hardware
  
KASLR = security feature equivalent of changing car VIN:
  Randomizes where kernel loads in memory at boot
  Attacker can't predict address -> exploit harder
  Like: randomizing which parking spot your car uses each day
```

---

### Gradual Depth - Five Levels

**Level 1:**
Why custom kernels exist. Distribution kernels vs custom. Basic build commands:
`make menuconfig`, `make -j$(nproc)`, `make install`. GRUB and kernel selection.
How to revert to previous kernel if new one doesn't boot.

**Level 2:**
localmodconfig for minimal builds. .config format: y/m/n. Key configuration
areas: HZ, PREEMPT model, filesystem types. make olddefconfig for handling
new options. modules_install and make install steps. EXTRAVERSION for naming.

**Level 3:**
Kconfig fragments for reproducible configurations. Security hardening options:
KASLR, LOCKDOWN, FORTIFY_SOURCE. Building for specific use cases: container
host, embedded, real-time. PREEMPT_RT patchset for hard real-time. Kernel
modules: when to use m vs y. Cross-compilation for ARM/other architectures.

**Level 4:**
Kernel debug features: KASAN (kernel address sanitizer), KCOV (code coverage),
lockdep (lock dependency checker). These are for development/testing only
(huge overhead in production). CONFIG_DYNAMIC_DEBUG for per-message debug
control. Building and applying kernel patches (git format-patch, git am).
Maintaining a kernel patchset against upstream. RPM/DEB package creation from
kernel build (`make rpm-pkg` or `make deb-pkg`).

**Level 5:**
Kconfig internals: Kconfig language spec, dependency resolution algorithm.
Kbuild system: Makefiles throughout kernel source, recursive make, ccache
integration. Kernel CI: 0day bot, KernelCI, automated testing of new patches.
LTO (Link-Time Optimization) for kernel: reduces size, enables cross-file
optimizations. CFI (Control Flow Integrity) for kernel security: requires LTO.
Clang kernel compilation: alternative to GCC, required for CFI and some
ARM security features. Compiler plugin for kernel hardening: stackprotector,
RANDSTRUCT, STRUCTLEAK. Module signing for secure boot: generate signing key,
sign all modules, MOK enrollment.

---

### Code Example

**BAD - building kernel without safety checks:**
```bash
# BAD: no config validation, no fallback plan

# Delete the existing .config and start from scratch with no plan:
make defconfig  # generic default, may not match your hardware AT ALL
make -j$(nproc)
make install  # installs over current kernel
reboot
# Risk: if new kernel panics, no fallback! 
# (If make install replaces /boot/vmlinuz symlink only)

# BAD: building in /boot (no space):
make INSTALL_PATH=/boot install  # /boot is typically 500MB, not enough
# df -h /boot: 100% after install!

# BAD: single-core build (takes 10x longer):
make bzImage  # no -j: uses single CPU core
# 8-core machine: 90 minutes instead of 10 minutes

# BAD: no backup of .config after build:
# System reinstalled, .config lost, can't reproduce custom kernel
```

```bash
# GOOD: safe kernel build procedure

# Verify all tools installed BEFORE starting:
gcc --version || { echo "gcc not installed"; exit 1; }
make --version || { echo "make not installed"; exit 1; }
ls /usr/include/openssl/ssl.h || yum install -y openssl-devel

# Use distribution config as base (ensures boot compatibility):
cp /boot/config-$(uname -r) .config

# Apply only needed customizations:
# Example: enable KASLR if not already:
grep CONFIG_RANDOMIZE_BASE .config
# If not set: add it:
echo "CONFIG_RANDOMIZE_BASE=y" >> .config

# Resolve dependencies (will not change options unless needed):
make olddefconfig
# Shows: "new config options set to default: X Y Z"

# Build with all CPUs:
make -j$(nproc) bzImage modules 2>&1 | tee /tmp/kernel-build.log
# Check for errors:
tail -5 /tmp/kernel-build.log
# If: "arch/x86/boot/bzImage" -> success

# Install with PRESERVATION of old kernel:
# make install: does NOT delete old kernel, adds new entry to GRUB
make modules_install  # /lib/modules/$(version)/
make install          # /boot/vmlinuz-$(version), /boot/config-$(version)

# Update GRUB with both old and new kernels:
grub2-mkconfig -o /boot/grub2/grub.cfg

# VERIFY both kernels in GRUB:
grep menuentry /boot/grub2/grub.cfg | grep -v echo
# menuentry 'Linux 6.6.0-custom' ...   <- new
# menuentry 'Linux 5.14.0-362.8.1' ... <- old fallback!

# Save .config for reproducibility:
cp .config /boot/config-$(make kernelversion)-$(date +%Y%m%d)

# Test in VM first (if production system):
qemu-system-x86_64 -enable-kvm \
    -kernel arch/x86/boot/bzImage \
    -append "console=ttyS0 root=/dev/vda rw" \
    -drive file=/dev/YOUR_TEST_DISK,format=raw \
    -m 1G -smp 4 -nographic
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Custom kernels are only for advanced users/kernel developers" | Custom kernel builds are used by: (a) Hardware vendors (NVidia ships DKMS modules that build against any kernel, Android OEMs build custom kernels for specific hardware), (b) Container OS vendors (Bottlerocket, Flatcar, Talos all ship custom minimized kernels optimized for container workloads), (c) Embedded systems engineers (every embedded Linux product - router, camera, IoT device - runs a custom-configured kernel), (d) Real-time system engineers (industrial automation, medical devices requiring PREEMPT_RT). The "advanced user" reputation comes from the era when kernel compilation required manually resolving dependencies and dealing with SCSI/IDE driver conflicts (1998-2005). Modern tooling (Kconfig, make localmodconfig, DKMS, RPM packaging) makes kernel builds routine for system engineers. |
| "`make menuconfig` should be used to configure every option carefully" | For 99% of custom kernel builds, the correct approach is NOT manually going through menuconfig item by item (there are 10,000+ config options). The practical approach: (a) `cp /boot/config-$(uname -r) .config && make olddefconfig`: start from working distribution config, accept defaults for new options. (b) `make localmodconfig`: strip unused modules from the distribution config. (c) Make targeted changes: add specific options you need (CONFIG_KASLR=y, CONFIG_BTRFS=y). (d) Use Kconfig fragments for reproducible changes (./scripts/kconfig/merge_config.sh). `menuconfig` is useful for: exploring what options exist, understanding kernel subsystem structure, making a few targeted changes visually. Not useful for: complete kernel configuration from scratch. |
| "A custom kernel must be from the latest upstream source" | The kernel version depends on your goal: (1) For applying a specific patch not yet in distribution: cherry-pick the patch onto the distribution kernel. Start from `/boot/config-$(uname -r)`, apply the patch with `git cherry-pick`, rebuild. Minimal changes from known-working configuration. (2) For enabling a new feature (eBPF CO-RE, io_uring): check if the distribution kernel already has it (often backported). If not: latest stable LTS from kernel.org (NOT latest mainline/rc). Latest mainline (`torvalds/linux master`) has unmerged experimental code, not suitable for production. (3) For embedded: maintain against a specific LTS branch (e.g., 6.6.x as long-term support). Always: test in VMs/staging before production deployment. |
| "Building with `make defconfig` gives a good starting point" | `make defconfig` generates a minimal generic configuration that is NOT specific to your hardware. It may: (a) Miss drivers for your actual network card or disk controller, (b) Enable drivers for hardware you don't have (wasted compile time), (c) Not include security features your distribution kernel has. The result: a kernel that may not boot on your hardware, or if it does, is not optimized for it. The correct starting points: `make localmodconfig` (starts from running kernel's loaded modules - guaranteed to work for your hardware), `cp /boot/config-$(uname -r) .config && make olddefconfig` (inherits ALL distribution settings, only adds new), or a known-good config from a reference system. `make defconfig` is appropriate for: cross-compiling for a completely different architecture where no reference config exists. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: kernel panics at boot ===
# Screen shows: "Kernel panic - not syncing: ..." 

# Immediately available diagnosis:
# 1. Take a photo of the panic message (if physical console)
# 2. Note: last messages before panic

# Common panic causes after custom build:

# A. Missing filesystem driver:
# Panic: VFS: Unable to mount root fs on unknown-block(8,1)
# Fix: ensure root filesystem type is compiled in (=y, not =m):
# If root is ext4: CONFIG_EXT4_FS=y (not =m!)
# Modules cannot be loaded BEFORE root filesystem is mounted
# Solution: built-in (=y) for root filesystem, initrd for early modules

# B. Missing initrd/initramfs:
# Panic: initrd: could not find /sbin/init
# After custom install: need to rebuild initrd for new kernel:
dracut --force /boot/initramfs-$(uname -r).img $(uname -r)
# or: update-initramfs -u -k $(uname -r)

# C. Missing NVME or SCSI driver:
# Panic: Unable to mount root fs, can't access /dev/nvme0n1
# Fix: ensure nvme driver is built-in:
# CONFIG_NVME_CORE=y
# CONFIG_BLK_DEV_NVME=y

# Recovery: at GRUB prompt, select previous working kernel
# (ensure you have a grub entry for the old kernel!)
grub2-mkconfig -o /boot/grub2/grub.cfg  # always run before rebooting!

# === Failure: module not found after custom build ===
modprobe some_module
# modprobe: FATAL: Module some_module not found in directory /lib/modules/6.6.0

# Cause: forgot to run make modules_install
# Or: module not compiled (=n in .config)

# Check if module was compiled:
find /path/to/kernel/source -name "some_module.ko" 2>/dev/null
# If not found: not compiled, check .config

# Check if modules installed:
ls /lib/modules/$(uname -r)/
# If directory missing: make modules_install was not run

# Run it:
cd /path/to/kernel/source
make modules_install

# === Failure: build fails with "No rule to make target" ===
make -j$(nproc) bzImage
# make: *** No rule to make target 'arch/x86/boot/bzImage'

# Cause 1: running make in wrong directory
# Must be in kernel source root:
ls Makefile  # should see kernel Makefile
cd /path/to/linux-6.6/  # ensure you're in kernel source root

# Cause 2: .config not generated:
ls .config  # must exist
# If missing: copy from /boot or run make defconfig

# Cause 3: missing build tools:
make -j$(nproc) bzImage 2>&1 | head -20
# gcc: command not found  <- install gcc
# flex: command not found  <- install flex, bison
```

---

### Related Keywords

**Foundational:**
LNX-028 (kernel basics), LNX-030 (boot process), LNX-079 (kernel tuning)

**Builds on this:**
LNX-107 (immutable infrastructure), LNX-111 (kernel architecture)

**Related:**
LNX-107 (immutable Linux infrastructure), LNX-111 (kernel architecture)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `cp /boot/config-$(uname -r) .config` | Start from running kernel config |
| `make localmodconfig` | Strip to currently-loaded modules |
| `make menuconfig` | Interactive configuration browser |
| `make olddefconfig` | Apply new options with defaults |
| `make -j$(nproc) bzImage modules` | Compile kernel and modules |
| `make modules_install && make install` | Install to /boot and /lib/modules |
| `grub2-mkconfig -o /boot/grub2/grub.cfg` | Update GRUB with new kernel |
| `uname -r` | Verify running kernel version |

**3 things to remember:**
1. Always keep the previous kernel in GRUB. `make install` adds a new GRUB entry without removing the old one. Run `grub2-mkconfig` after `make install`. If the new kernel panics, reboot to old kernel from GRUB.
2. Root filesystem drivers must be built-in (`=y`), not as modules (`=m`). Modules can't be loaded until the root filesystem is mounted. `make localmodconfig` handles this correctly; custom configs must verify manually.
3. Start from the distribution `.config` via `cp /boot/config-$(uname -r) .config && make olddefconfig`, not from scratch. Distribution configs include security patches, hardware quirks, and tested defaults you don't want to recreate.

---

### Transferable Wisdom

Kernel build configuration principles transfer directly to: container image
building (FROM scratch + only what you need = minimal attack surface, same
principle as minimal kernel), application binary configuration (JVM flags =
runtime config, gcc flags = compile config, both affect behavior/performance),
Terraform module configuration (Kconfig options = Terraform variables with
dependencies and defaults). The kbuild dependency resolution (enabling
CONFIG_X auto-enables CONFIG_Y) is the same as: Maven/Gradle dependency
resolution (adding dependency A pulls transitive dependencies), package
manager dependency resolution (apt install X pulls required packages), Ansible
role dependency (role A requires role B). localmodconfig's approach (snapshot
current state, build only what's needed) is the same as: `pip freeze >
requirements.txt` (lock exact dependencies from running environment), `npm
ci` (install exactly locked versions, not latest), Docker multi-stage builds
(runtime image contains only what production needs). KASLR/ASLR (randomize
address layout) is the same defense-in-depth concept as: database port
randomization (not default 5432/3306), microservice port randomization, JWT
secret rotation (attacker can't predict the secret). The PREEMPT_NONE vs
PREEMPT_VOLUNTARY vs PREEMPT trade-off (throughput vs latency) is the same
as: TCP Nagle algorithm (batch=throughput vs low-latency), Kafka batch size
(larger=throughput, smaller=latency), database commit interval.

---

### The Surprising Truth

The Linux kernel source code is approximately 30 million lines of code and
contains over 10,000 Kconfig configuration options. A fully configured
kernel (all options enabled where possible) takes ~2 hours to compile on
a powerful workstation. Yet `make localmodconfig` on a typical server
produces a configuration with only 500-700 active options, and compiles in
under 5 minutes on the same machine.

This means: a typical server uses less than 7% of the kernel's code. The
remaining 93% is drivers for hardware you don't have, filesystems you don't
use, network protocols never configured, and debug infrastructure never
enabled. Every line of that unused code is still present in memory (as
kernel data structures, device probes, etc.) when using a distribution kernel.
Kernel developers debate how much this matters for security: more code = more
attack surface, but the kernel's security model limits most vulnerabilities
to kernel-level attackers. For embedded systems and container hosts where
every byte of RAM matters: custom minimal kernels with <10% of the standard
feature set are the only reasonable choice.

---

### Mastery Checklist

- [ ] Can clone kernel source, configure with localmodconfig, compile, and install a custom kernel
- [ ] Understands y/m/n Kconfig options and why root filesystem must be built-in (=y)
- [ ] Can update GRUB after kernel install and verify the old kernel is preserved as fallback
- [ ] Knows key security configuration options: KASLR, LOCKDOWN, FORTIFY_SOURCE
- [ ] Can diagnose a kernel panic at boot from the error message (missing driver, missing initrd)

---

### Think About This

1. Design a kernel configuration for a dedicated Kubernetes node running
   containerized Java microservices. The node has: NVMe SSDs, 25Gbps NICs
   (Mellanox), no USB/Bluetooth/sound, runs CentOS 8 base but will use a
   custom kernel. What Kconfig subsystems are essential vs can be disabled?
   Which PREEMPT setting is appropriate? What HZ setting? What security options
   should be enabled? How would your configuration differ for a node running
   real-time financial trading applications?

2. You need to apply a security patch (for a new CVE) to production kernels
   running kernel 5.14 (distribution kernel). The patch exists in the upstream
   6.6 kernel as a single commit. Describe the process: how do you cherry-pick
   the commit onto 5.14? How do you verify it applies cleanly? How do you test
   the patched kernel before deploying to production? What is your rollback
   plan? How do you distribute the new kernel to 200 production servers?

3. A colleague argues that custom kernels are a security risk: "more custom
   code = more attack surface, and we lose automatic security updates from
   the distribution." Build a counter-argument: in what scenarios does a
   custom minimal kernel REDUCE attack surface vs a distribution kernel?
   How can custom kernel updates be automated to match distribution kernel
   security patch cadence? When is the colleague's argument valid (i.e.,
   when should you NOT use a custom kernel)?

---

### Interview Deep-Dive

**Foundational:**
Q: Walk me through how you would build and install a custom Linux kernel.
A: KERNEL BUILD PROCESS: (1) GET SOURCE: `git clone --depth=1 https://github.com/torvalds/linux.git` for latest mainline, or download stable tarball from kernel.org. For practical builds: often start from distribution's source RPM (`rpm -ivh kernel-6.x.src.rpm`) which has distribution patches applied. (2) CONFIGURE: Start from running kernel config: `cp /boot/config-$(uname -r) .config && make olddefconfig`. This inherits all tested distribution settings. For minimal build: `make localmodconfig` strips to only currently-loaded modules. Interactive exploration: `make menuconfig`. (3) MAKE TARGETED CHANGES: Edit .config directly or use menuconfig to enable specific features. E.g., enable KASLR: `echo CONFIG_RANDOMIZE_BASE=y >> .config && make olddefconfig` to resolve any new dependencies. (4) COMPILE: `time make -j$(nproc) bzImage modules` - parallelize across all CPUs. Output: `arch/x86/boot/bzImage` (bootable kernel), all `.ko` module files. (5) INSTALL: `make modules_install` copies `.ko` files to `/lib/modules/$(version)/`. `make install` copies bzImage, System.map to /boot/, creates initramfs. (6) UPDATE GRUB: `grub2-mkconfig -o /boot/grub2/grub.cfg`. VERIFY both old and new kernels appear in GRUB config. (7) REBOOT: Select new kernel at GRUB, verify with `uname -r`. SAFETY: Never remove old kernel before testing new one. Always ensure GRUB has fallback entry. Test in VM first for production systems. Keep the .config file archived for reproducibility.

**Expert:**
Q: What are the key kernel configuration decisions for a high-performance container host, and how do they differ from a real-time system?
A: CONTAINER HOST CONFIGURATION: (1) PREEMPT_NONE: Container workloads are server workloads - maximize throughput, not responsiveness. PREEMPT_NONE means kernel code paths run to completion without preemption, fewer context switches, better throughput. (2) HZ=100: 100 timer interrupts per second (10ms tick). Container workloads don't need sub-millisecond timer precision. HZ=100 reduces wasted CPU cycles on timer processing. For comparison: HZ=1000 burns CPU but adds nothing for throughput. (3) Namespace and cgroup subsystems: all must be compiled in (y) - they're required for container isolation. CONFIG_NAMESPACES, CONFIG_UTS_NS, CONFIG_PID_NS, CONFIG_NET_NS, CONFIG_CGROUPS, CONFIG_MEMCG, CONFIG_CGROUP_BLKIO. (4) Filesystem: overlay filesystem (CONFIG_OVERLAY_FS=y) for container image layering. (5) eBPF: CONFIG_BPF=y, CONFIG_BPF_SYSCALL=y, CONFIG_BPF_JIT=y for Cilium and observability. (6) Security: KASLR, SECCOMP (for seccomp-bpf container profiles), AppArmor/SELinux for MAC. (7) Minimal drivers: disable PCI devices not in the server, USB HID, audio, Bluetooth. REAL-TIME SYSTEM DIFFERENCES: (1) CONFIG_PREEMPT_RT: PREEMPT-RT patchset makes the entire kernel preemptible. Real-time kernel: when a high-priority interrupt arrives, it can preempt even kernel code. Container host: kernel code runs to completion (cannot be preempted). This is the OPPOSITE - RT sacrifices throughput for deterministic latency. (2) HZ=1000 or tickless (CONFIG_NO_HZ_FULL): RT systems may need 1ms timer resolution. (3) Isolate CPUs (isolcpus=): dedicated CPU cores for real-time tasks, no kernel threads or IRQs. `CONFIG_CPU_ISOLATION=y`. (4) IRQ affinity: bind interrupts to non-real-time CPUs. (5) Disable CPU frequency scaling (CONFIG_CPU_FREQ_GOVERNORS for power savings): real-time needs deterministic CPU speed, not power-saving throttling. TLDR: Container host = throughput (PREEMPT_NONE, HZ=100, lean on namespaces/cgroups). Real-time = latency (PREEMPT_RT, isolated CPUs, deterministic interrupt handling). Attempting both simultaneously requires careful partitioning - container workloads and RT workloads should run on separate CPUs or separate nodes.
