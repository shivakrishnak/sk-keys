---
id: LNX-098
title: "NFS and Network File Systems on Linux"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-037, LNX-059
used_by: LNX-099
related: LNX-037, LNX-059, LNX-099
tags: [nfs, network-file-system, nfsv4, nfsv3, mount-cifs, smbfs, sshfs, nfs-performance, rsize-wsize, hard-soft-mount, nfsstat, showmount, exports, autofs, nfs-kerberos, rdma-nfs, glusterfs, nfs-tuning, network-storage, distributed-filesystem]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 98
permalink: /technical-mastery/lnx/nfs-network-file-systems/
---

## TL;DR

NFS (Network File System) allows Linux systems to access remote filesystems
over the network as if they were local. Key versions: NFSv3 (stateless,
uses multiple ports, no native ACLs) vs NFSv4 (stateful, single port 2049,
native ACLs, Kerberos authentication). Mount: `mount -t nfs server:/export
/mnt/remote`. Critical mount options: `rsize=1048576,wsize=1048576` (1MB
read/write block size for performance), `hard` vs `soft` (hard = retry
forever on server failure, soft = fail after timeout), `noresvport,nofail`
for production. `nfsstat -c` for client statistics. `showmount -e server`
to list available exports. For SMB/Windows shares: `mount -t cifs
//server/share /mnt -o credentials=/etc/.creds`. For SSH-based:
`sshfs user@host:/path /mnt`. NFS performance bottleneck: always check
network bandwidth first, then NFS options.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-098 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | NFS, NFSv4, CIFS, SSHFS, network storage, mount options, exports, nfsstat, showmount |
| **Prerequisites** | LNX-037 (networking), LNX-059 (filesystem) |

---

### The Problem This Solves

**Problem 1**: A development team needs 10 servers to share the same code
repository files. Without NFS: copy files to all 10 servers manually before
each deploy, or use rsync (still separate copies, sync lag). With NFS: mount
one NFS export to all 10 servers. They all read from the same files. One update
on the NFS server is instantly visible to all 10 clients. No synchronization
needed.

**Problem 2**: An HPC (High Performance Computing) cluster runs scientific
jobs. Each job needs to read 50GB of input data. Without network storage:
copy 50GB to each compute node before each job (hours of setup per job). With
NFS: compute nodes mount the data directly. Large rsize=1048576 (1MB read
blocks) enables near-network-bandwidth throughput. Job starts immediately.

---

### Textbook Definition

**NFS (Network File System)**: A distributed filesystem protocol originally
developed by Sun Microsystems (RFC 1094, 1989). Allows a client to mount
a remote directory as if it were a local filesystem. The NFS server exports
directories; NFS clients mount those exports.

**Key NFS components:**
| Component | Role |
|-----------|------|
| `nfsd` | Kernel NFS server daemon |
| `mountd` | Mount request handler (NFSv3) |
| `rpcbind` | Port mapper for RPC services (NFSv3) |
| `/etc/exports` | Server-side export configuration |
| `exportfs` | Export management command |
| `nfsstat` | NFS statistics |
| `showmount` | List server exports |

**NFSv3 vs NFSv4 comparison:**
| Feature | NFSv3 | NFSv4 |
|---------|-------|-------|
| State | Stateless | Stateful |
| Ports | Multiple (rpcbind, mountd, nfsd) | Single (2049/tcp) |
| Authentication | AUTH_SYS (uid/gid, spoofable) | RPCSEC_GSS/Kerberos |
| ACLs | No | Yes (NFSv4 ACLs) |
| Locking | nlm (separate) | Built-in |
| Firewall | Difficult (random ports) | Easy (single port) |
| Performance | Good | Better (compound operations) |

---

### Understand It in 30 Seconds

```bash
# === Server side: exporting a directory ===

# Install NFS server (RHEL/CentOS):
yum install -y nfs-utils

# Configure exports (/etc/exports):
cat /etc/exports
# /data/shared    192.168.1.0/24(rw,sync,no_subtree_check)
# /data/readonly  *(ro,sync,no_subtree_check,root_squash)
#
# Options:
# rw: read-write; ro: read-only
# sync: write to disk before reply (safe, slower)
# async: reply before writing to disk (fast, risk on crash)
# no_subtree_check: avoid subtree checking (performance + avoid rename issues)
# root_squash: map root (uid=0) from client to nobody (default, secure)
# no_root_squash: DANGEROUS - client root = server root
# all_squash: map all users to nobody

# Export and start:
exportfs -ra      # reload exports
systemctl enable --now nfs-server

# Verify:
showmount -e localhost
# Export list for localhost:
# /data/shared   192.168.1.0/24
# /data/readonly *

# === Client side: mounting NFS ===

# Basic mount (auto-detects best version):
mount -t nfs server:/data/shared /mnt/shared

# Specify NFSv4:
mount -t nfs4 server:/data/shared /mnt/shared

# Performance-optimized mount (for large file transfers):
mount -t nfs server:/data/shared /mnt/shared \
    -o rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,\
       noresvport,nofail,_netdev

# Options breakdown:
# rsize=1048576: read block size 1MB (default was 32KB, huge difference!)
# wsize=1048576: write block size 1MB
# hard: if server unreachable, retry forever (processes hang but don't die)
# soft: if server unreachable, fail after timeout (processes get EIO error)
# timeo=600: 60 second timeout (in 0.1s units: 600 = 60s)
# retrans=2: retry 2 times before error
# noresvport: don't require reserved port (works through NAT)
# nofail: allow boot to continue if mount fails
# _netdev: requires network before mount (for /etc/fstab)

# Verify mount:
mount | grep nfs
# server:/data/shared on /mnt/shared type nfs4 (rw,...)
df -h /mnt/shared
# server:/data/shared  100G  45G  55G  45%  /mnt/shared

# === NFS statistics ===
nfsstat -c  # client statistics
# Client rpc stats:
# calls  retrans   authrefrsh
# 123456  0         0       <- retrans=0: good, no retransmissions
#
# Client nfs v4:
# null      read      write  ...
# 0         12345     6789   ...

nfsstat -s  # server statistics

# Detailed mount options:
cat /proc/mounts | grep nfs
# server:/data nfs4 rw,relatime,vers=4.2,rsize=1048576,wsize=1048576,...

# === /etc/fstab entry for persistent mount ===
cat /etc/fstab
# server:/data/shared  /mnt/shared  nfs4  \
#   rw,rsize=1048576,wsize=1048576,hard,timeo=600,_netdev,nofail  0  0

# Test without rebooting:
mount -a  # mount all /etc/fstab entries

# === Other network filesystems ===

# CIFS/SMB (Windows shares):
yum install -y cifs-utils
cat /etc/.smbcreds
# username=myuser
# password=secret123
chmod 600 /etc/.smbcreds  # protect credentials file!

mount -t cifs //winserver/share /mnt/windows \
    -o credentials=/etc/.smbcreds,uid=1000,gid=1000,\
       iocharset=utf8,vers=3.0

# SSHFS (SSH-based, no server-side config needed):
yum install -y fuse-sshfs  # or: apt install sshfs
sshfs user@remotehost:/remote/path /mnt/ssh
# Uses SSH key authentication
# Unmount: fusermount -u /mnt/ssh

# AutoFS (automatic mounting on demand):
# /etc/auto.master:
# /mnt/auto /etc/auto.nfs --timeout=600
# /etc/auto.nfs:
# shared -fstype=nfs4,rw,rsize=1048576,wsize=1048576 server:/data/shared
# Access /mnt/auto/shared -> auto-mounts on demand, unmounts after timeout
```

---

### First Principles

```
How NFS works (NFSv4 protocol):

Client creates mount point:
  mount -t nfs4 server:/export /mnt/remote
  Kernel: call NFS client code
  NFS client: TCP connection to server:2049

RPC (Remote Procedure Call) layer:
  NFS operations are RPC calls
  Each filesystem operation becomes an RPC:
    OPEN: open a file
    READ: read data from file
    WRITE: write data to file
    CLOSE: close file
    GETATTR: get file attributes (stat())
    SETATTR: set attributes (chmod, chown)
    LOOKUP: directory entry lookup (ls)
    READDIR: list directory
    RENAME: rename file
    REMOVE: delete file
    LINK/SYMLINK: create links
  
  NFSv4 COMPOUND operations:
    Multiple operations in a single RPC call
    PUTFH + OPEN + READ in one round-trip
    vs NFSv3: separate RPC per operation
    Result: fewer round-trips, better WAN performance

Stateful operation (NFSv4):
  Server tracks open file state per client
  "Open delegation": server delegates file to client
    Client can cache reads/writes locally without RPC for every op
    Client notifies server when done (CLOSE)
  "Lease": client's state expires if it doesn't refresh
    Prevents stale locks from crashed clients

rsize/wsize impact:
  Without optimization (default 32KB):
    Read 1GB file = 1GB/32KB = 32,768 NFS READ RPCs
    Each RPC: network round-trip (~1ms on LAN)
    = 32,768ms = 32 seconds just in round-trips!
    (Plus actual data transfer time)
  
  With optimization (rsize=1MB):
    Read 1GB file = 1GB/1MB = 1,024 NFS READ RPCs
    Round-trips: 1,024ms = 1 second
    Plus data transfer: 1GB at 1Gbps = 8 seconds
    Total: ~9 seconds (vs 32 seconds!)
  
  Maximum useful rsize: min(NIC bandwidth capacity, server throughput)
  For 1Gbps NIC: rsize=1048576 (1MB) is optimal
  For 10Gbps NIC: rsize=1048576 is still typical (NFS overhead limits)

NFS security (AUTH_SYS vs Kerberos):
  AUTH_SYS (default):
    Client sends: UID, GID, supplementary GIDs in each RPC
    Server trusts these values
    PROBLEM: any client can claim to be uid=0 (root)!
    Only safe within trusted network (same team's LAN)
    
  Kerberos (sec=krb5, krb5i, krb5p):
    krb5: authentication only (no encryption)
    krb5i: authentication + integrity (HMAC, no encryption)
    krb5p: authentication + encryption (full privacy)
    
    Requires: Kerberos KDC (MIT Kerberos or Active Directory)
    Client: kinit (get Kerberos ticket)
    NFS uses RPCSEC_GSS to negotiate Kerberos
    
    idmapping: NFSv4 uses name@domain (not uid/gid)
    nfs-idmapd: maps name to uid (requires matching domain config)
    /etc/idmapd.conf: Domain = example.com

hard vs soft mount decision:
  hard (recommended for shared data):
    Server unreachable: processes hang (I/O blocked)
    Server recovers: processes resume (no data loss)
    Use for: application data, databases, shared code
    
  soft (use only for read-only, non-critical):
    Server unreachable after timeout: EIO error to application
    Application must handle the error
    Risk: application may see partial writes as success
    Use for: /opt software mounts, read-only reference data
    With: retrans=2, timeo=30 (6 second total timeout)
```

---

### Thought Experiment

NFS performance tuning for HPC workload:

```bash
# HPC cluster: 100 compute nodes reading 50GB input files from NFS server
# Problem: jobs take 45 minutes, 30 of which is reading data
# NFS server: 10Gbps NIC, ZFS storage
# Clients: 10Gbps NICs

# Current mount (default settings):
mount -t nfs4 nfsserver:/data /mnt/data
# Performance: 125 MB/s (default rsize=32KB)

# Diagnosis:
nfsstat -c | grep read
# read: 12,345,678 calls  (too many small reads!)

# Check current mount options:
cat /proc/mounts | grep nfsserver
# nfsserver:/data nfs4 rw,relatime,vers=4.2,rsize=32768,wsize=32768,...
# rsize=32768 (32KB): way too small for 10Gbps!

# Fix 1: Large rsize/wsize:
umount /mnt/data
mount -t nfs4 nfsserver:/data /mnt/data \
    -o rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,\
       noresvport,proto=tcp

# Test: read 1GB file:
time dd if=/mnt/data/testfile.1gb of=/dev/null bs=1M
# Before: 45 seconds (125 MB/s - bottlenecked by small rsize)
# After:  8 seconds  (1.2 GB/s - near wire speed for 10Gbps)

# Fix 2: NFS over RDMA (if InfiniBand available):
# Mount with proto=rdma:
mount -t nfs4 nfsserver:/data /mnt/data \
    -o rsize=1048576,wsize=1048576,proto=rdma,port=20049

# Fix 3: async mounting (for temporary jobs, not persistent data):
mount -t nfs4 nfsserver:/data /mnt/data -o async
# async: client doesn't wait for server to confirm write to disk
# ONLY for: read-only data, or data you can recreate if lost
# NOT for: anything important - crash during async = data loss

# After tuning: 45 min total -> 15 min (30 min saved = just data I/O)
```

---

### Mental Model / Analogy

```
NFS = remote hard drive over a network cable

Local filesystem: read file = ask local disk (fast, same machine)
NFS: read file = ask remote server (slow: network round-trip added)

The rsize/wsize = how big are the "packages" sent:
  rsize=32KB: like mailing documents page-by-page (32 pages per envelope)
    1GB file = 32,768 envelopes, 32,768 trips to mailbox
  rsize=1MB: like mailing documents 1000 pages per envelope
    1GB file = 1,024 envelopes, 1,024 trips to mailbox
    Less overhead, faster overall

hard vs soft mount = contract with the post office:
  hard: "hold my package until post office opens, I'll wait"
    Package arrives eventually (when server recovers)
    Process hangs but doesn't lose data
    Good for: important documents (application data)
  
  soft: "return package if not delivered in 1 hour"
    After timeout: you get the package back (EIO error)
    You have to handle the return (application error handling)
    Good for: low-stakes deliveries (read-only reference data)

NFSv3 vs NFSv4 = old mail system vs modern courier:
  NFSv3: uses multiple offices (multiple ports - rpcbind, mountd)
    Stateless: each letter is independent, no tracking
    Firewall-unfriendly: need multiple firewall exceptions
    Authentication: "trust the return address" (spoofable uid/gid)
    
  NFSv4: single office, single address (one port: 2049)
    Stateful: package tracked from start to finish
    Firewall-friendly: one exception for port 2049
    Authentication with Kerberos: verified ID, secure
    Compound operations: "deliver multiple packages in one trip"

root_squash = security policy:
  "All deliveries claiming to be from the CEO (uid=0 = root)
   must be signed as 'anonymous delivery' (nobody)"
  Prevents: malicious client claiming to be root
  Without it: root on ANY NFS client has root on NFS server!

NFS over RDMA = direct machine-to-machine data highway:
  Traditional NFS over TCP: data travels through OS network stack
  RDMA: NFS storage controller writes DIRECTLY to client RAM
  Bypasses OS, near-zero CPU overhead
  Ultra-low latency (<1ms) and max throughput (200Gbps+)
  Used in: HPC, AI training (GPU servers reading datasets)
```

---

### Gradual Depth - Five Levels

**Level 1:**
What NFS is: accessing remote directories as if local. Basic mount command.
`/etc/exports` for server configuration. `showmount -e server` to view exports.
`nfsstat` for statistics. Hard vs soft mount meaning. Why rsize/wsize matter.

**Level 2:**
NFSv3 vs NFSv4 differences (single port, stateful, ACLs). Mount options:
rsize, wsize, hard, soft, timeo, retrans, noresvport, nofail, _netdev. `nfsstat`
reading (calls, retransmissions). CIFS/SMB mount (`mount -t cifs`). SSHFS as
simple alternative. `/etc/fstab` NFS entries. `exportfs -ra` for reloading
exports.

**Level 3:**
NFSv4 idmapping (name@domain), nfs-idmapd configuration. Kerberos NFS (sec=
krb5/krb5i/krb5p). NFS performance tuning: optimal rsize/wsize selection.
`/proc/net/rpc/nfs` for client stats. AutoFS for on-demand mounting. `nfsstat
-s` server statistics. NFS4 delegations (client-side caching for open files).
`mount.nfs` debugging with `-vvv`. Common NFS errors: stale file handle, no
such file or directory (server not exporting).

**Level 4:**
NFS over RDMA: InfiniBand or RoCE protocol, performance comparison. NFS pNFS
(parallel NFS): distribute data across multiple servers, stripe at block level.
NFS with HA: floating IP + NFS server failover (DRBD, Corosync/Pacemaker). NFS
security hardening: `sec=krb5p` for full encryption, `no_root_squash` risks,
`anonuid=/anongid=` for anonymous mapping. NFSv4.2 features: server-side copy
(COPY operation avoids round-trip), hole punching, labeled NFS (SELinux labels).
`rpcdebug` for NFS kernel debug logging.

**Level 5:**
NFS kernel internals: `struct nfs_server`, `struct nfs4_client`, NFSv4 session
mechanism (sequence IDs, slot tables). NFS over TCP vs UDP: TCP reliable
delivery eliminates the need for soft mount retransmission logic. pNFS data
servers and metadata server separation. GlusterFS and CephFS as alternatives:
distributed, scale-out, no single server bottleneck. NFS at Kubernetes scale:
multiple pods mounting same NFS export, NFSv4.1 client-side caching, ReadWriteMany
PVs in Kubernetes via NFS. NFS in the cloud: AWS EFS (NFSv4 managed), Azure
Files (CIFS or NFS), GCP Filestore.

---

### Code Example

**BAD - insecure and unperformant NFS configuration:**
```bash
# BAD: /etc/exports with dangerous options:
/data  *(rw,sync,no_root_squash,no_subtree_check)
#       ^                ^^^^^^^^^^^^^^^
#       wildcard IP      no_root_squash: ROOT ON ANY CLIENT = ROOT ON SERVER!
#       allows ANY       This is equivalent to giving root access to anyone
#       machine to mount  who can reach this machine. NEVER in production.

# BAD: mount without performance options (default rsize=32KB):
mount -t nfs fileserver:/data /mnt/data
# 50GB file reads will be 10x slower than necessary
# No hard/soft specified: inherits default "hard" but no timeout configured

# BAD: storing CIFS credentials in mount command:
mount -t cifs //server/share /mnt -o \
    username=admin,password=MySecret123,domain=CORP
# Password visible in: ps aux, /proc/mounts, bash history, logs!
```

```bash
# GOOD: secure and performant NFS setup

# Server /etc/exports (secure):
# Specific subnet only, root_squash enabled, no wildcard
/data/shared  192.168.10.0/24(rw,sync,root_squash,no_subtree_check)
/data/public  *(ro,sync,root_squash,no_subtree_check)
# Explanation:
# 192.168.10.0/24: only trusted subnet, not wildcard
# root_squash: root on client maps to nobody (secure default)
# no_subtree_check: prevents rename race condition (recommended)
# sync: data on disk before reply (safe)
# ro for public: read-only for public data

# Reload and verify:
exportfs -ra
showmount -e localhost

# GOOD: client mount with performance and reliability options:
mount -t nfs4 nfsserver:/data/shared /mnt/shared \
    -o rsize=1048576,wsize=1048576,\
       hard,timeo=600,retrans=2,\
       noresvport,\
       nofail,\
       _netdev,\
       vers=4.2

# GOOD: /etc/fstab (persistent mount):
# nfsserver:/data/shared  /mnt/shared  nfs4 \
#   rw,rsize=1048576,wsize=1048576,hard,timeo=600,_netdev,nofail 0 0

# GOOD: CIFS with credentials file:
cat > /etc/.smbcredentials << 'EOF'
username=svcaccount
password=ServicePass123
domain=CORP
EOF
chmod 600 /etc/.smbcredentials  # readable only by root
chown root:root /etc/.smbcredentials

mount -t cifs //winserver/share /mnt/windows \
    -o credentials=/etc/.smbcredentials,\
       uid=1000,gid=1000,\
       iocharset=utf8,\
       vers=3.0,\
       seal  # encrypt SMB3 traffic
# Credentials NOT visible in ps or logs
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`no_root_squash` is needed for the application to work" | `no_root_squash` is almost never actually required and is extremely dangerous. It means that root (uid=0) on any NFS CLIENT has root access on the NFS SERVER - including modifying /etc/passwd, reading /etc/shadow, creating SUID binaries. Applications rarely need root access to NFS files. If the application runs as a specific user: configure NFS exports to serve files owned by that user, or use `anonuid` to map the application's UID. If root access is genuinely needed: use NFSv4 with Kerberos (`sec=krb5`) which authenticates the root user cryptographically (not just by claiming uid=0). In cloud environments: AWS EFS, Azure Files, and GCP Filestore all default to root_squash precisely because of this security risk. |
| "NFS performance is inherently poor because it's network-based" | Default NFS mount options (rsize=32KB, wsize=32KB) are indeed slow - designed for 1990s networks. With proper tuning (rsize=1048576, wsize=1048576) on modern 10Gbps networks: NFS can deliver 1+ GB/s read throughput, comparable to local SATA SSD. AWS EFS with 10Gbps Enhanced Networking: 1+ GB/s sustained reads. The confusion is: engineers observe poor default NFS performance, conclude "NFS is slow," never tune it. NFS over RDMA (InfiniBand) achieves even higher throughput (100Gbps+) with lower latency than TCP. pNFS (parallel NFS) distributes data across multiple storage servers, scaling throughput linearly with server count. |
| "A `soft` mount is safer because the application doesn't hang" | `soft` mounts can cause DATA CORRUPTION. With `soft` mount: if a WRITE operation times out (server temporarily unreachable), the NFS client returns EIO to the application and discards the write. The application may consider the write successful (if it doesn't check the return code carefully) while the data was NEVER written to the server. The server then recovers, but the data is lost. This is why `hard` mounts are recommended for any data you care about. With `hard` mounts: the process blocks (hangs) until the server recovers. This is the CORRECT behavior - data integrity is preserved. The "hanging" behavior is a feature, not a bug. For cloud environments: use `timeo` and `retrans` with hard mounts to control retry behavior without risking data corruption. |
| "NFS exports are only visible via showmount" | `showmount -e server` queries the NFS MOUNT daemon (mountd) which is separate from the NFS server itself. Some servers disable mountd for security or run NFSv4-only (which doesn't use mountd). Additionally: firewalls may block the mountd port while allowing NFS port 2049. You can have a valid NFSv4 export that doesn't show in `showmount`. To verify NFSv4 exports: `cat /proc/fs/nfsd/exports` on the server, or attempt mounting directly: `mount -t nfs4 server:/ /mnt` (NFSv4 pseudo root). Also: `nfsconf` command and systemctl status nfs-server for service status. For debugging invisible exports: `rpcdebug -m nfsd` and check server logs. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: "Stale file handle" error ===
ls /mnt/nfs/
# ls: cannot access '/mnt/nfs/dir': Stale file handle

# Cause: NFS server rebooted and file/directory was deleted or moved
# while client had an open reference. The inode/filehandle on server
# no longer exists but client still holds a reference.

# Fix: unmount and remount:
umount -l /mnt/nfs  # -l: lazy unmount (even if busy)
mount -t nfs4 server:/export /mnt/nfs -o [options]

# Or: restart autofs if using it:
systemctl restart autofs

# === Failure: NFS mount hangs at boot ===
# System boot stuck waiting for NFS mount

# Cause: NFS server unreachable during boot
# Fix 1: add _netdev and nofail to /etc/fstab:
# server:/export /mnt/nfs nfs4 rw,_netdev,nofail 0 0
# _netdev: wait for network before mounting
# nofail: allow boot even if mount fails

# Fix 2: use AutoFS (mounts on demand, not at boot)

# === Failure: slow NFS performance ===
# Application takes 10x longer when reading from NFS

# Diagnose current options:
cat /proc/mounts | grep nfs
# server:/data nfs4 rw,vers=4.2,rsize=32768,wsize=32768,...
# ^ rsize=32768: only 32KB! That's the problem.

# Check nfsstat retransmissions:
nfsstat -c | grep retrans
# retrans: 1234  <- high retransmissions = network issues or server overloaded

# Network bandwidth check:
iperf3 -c nfsserver  # test raw network speed client->server
# Expected: near line rate (10Gbps = ~9.4 Gbps in iperf)
# If low: network bottleneck (not NFS configuration)

# Fix: remount with optimal options:
umount /mnt/data
mount -t nfs4 server:/data /mnt/data \
    -o rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2

# Test improvement:
dd if=/mnt/data/test.1gb of=/dev/null bs=1M
# Compare throughput before/after

# === Failure: permission denied on NFS mount ===
ls -la /mnt/nfs/
# ls: cannot open directory '/mnt/nfs/': Permission denied

# Check 1: UID mapping (NFSv4 idmapping):
id  # local uid=1001
# On server: does user with uid=1001 have access?
# NFSv4: checks user@domain mapping
cat /etc/idmapd.conf  # Domain must match on client and server!

# Check 2: NFSv4 ACLs:
nfs4_getfacl /mnt/nfs/directory  # show NFSv4 ACLs

# Check 3: root_squash and UID mismatch:
# You're running as root (uid=0), root_squash is on:
# root -> mapped to nobody (uid=65534)
# nobody probably doesn't have access to files owned by uid=1001

# Fix: run application as the correct non-root user
# Or (INSECURE): add no_root_squash to exports
```

---

### Related Keywords

**Foundational:**
LNX-037 (networking), LNX-059 (filesystem)

**Builds on this:**
LNX-099 (fleet management)

**Related:**
LNX-099 (Ansible fleet management)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `showmount -e SERVER` | List available NFS exports |
| `mount -t nfs4 server:/export /mnt` | Mount NFSv4 share |
| `mount -t nfs ... -o rsize=1048576,wsize=1048576` | Performance mount |
| `nfsstat -c` | Client NFS statistics |
| `exportfs -ra` | Reload /etc/exports |
| `cat /proc/mounts | grep nfs` | View active NFS mounts with options |
| `umount -l /mnt/nfs` | Force unmount (lazy) |
| `sshfs user@host:/path /mnt` | SSHFS mount |

**3 things to remember:**
1. Always set `rsize=1048576,wsize=1048576` for performance-sensitive NFS mounts. Default 32KB blocks cause 30x more RPC calls than necessary.
2. Use `hard` mount for application data (hangs on server failure but never corrupts data). Use `soft` only for read-only non-critical data where an EIO error is acceptable.
3. Never use `no_root_squash` in production exports unless using Kerberos authentication. Root on any client = root on server.

---

### Transferable Wisdom

NFS concepts transfer directly to cloud storage: AWS EFS = managed NFSv4 (same
mount options: rsize=1048576,wsize=1048576 are the AWS EFS recommended settings),
Azure Files NFS = NFSv4.1, GCP Filestore = NFS. Kubernetes ReadWriteMany
persistent volumes use NFS (or equivalent) under the hood - multiple pods
mount the same export. The hard/soft mount decision maps to: database transaction
durability (sync vs async, fsync guarantees), network queue configuration
(hard = blocking, soft = drop with error), distributed system consistency
(strong consistency = hard mode, eventual consistency = soft mode). The
rsize/wsize tuning insight (default is 10x too small) applies to: database
network fetch size (PostgreSQL default_statistics_target, MySQL InnoDB fetch
buffer), HTTP/2 stream settings (initial window size), message queue consumer
batch size (Kafka max.poll.records). The root_squash security principle (don't
trust claimed identity from remote systems) maps to: JWT token verification
(don't trust user-provided JWT without signature verification), API gateway
identity claims (validate the identity, don't trust headers directly).

---

### The Surprising Truth

NFS was designed by Sun Microsystems in 1984 and first shipped in 1989 in
SunOS 2.0. It was designed to work on the slow, unreliable networks of the
1980s (10 Mbps Ethernet with high collision rates). The protocol's stateless
design (NFSv3 and earlier) was specifically chosen because state management
was considered too risky on unreliable networks - if the server crashed and
lost state, clients could resume from scratch. The default `rsize=32KB` comes
from this era, when sending 32KB chunks over an unreliable network was
considered appropriately conservative.

30 years later, engineers still deploy NFS with these 1980s defaults on 10/25/100
Gbps networks, then wonder why performance is poor. The recommended optimization
(rsize=1048576 = 1MB) was known since the mid-2000s when 1Gbps networks became
common, but many infrastructure guides were never updated. Every major cloud
provider's NFS documentation explicitly states "use rsize=1048576,wsize=1048576"
in their best practices - because the default 32KB was designed for a world
where the entire internet's backbone was slower than a single modern SSD.

---

### Mastery Checklist

- [ ] Can configure an NFS server export with appropriate security options (root_squash, specific subnet)
- [ ] Can mount NFS with performance-optimized options (rsize/wsize 1MB) and explain why defaults are insufficient
- [ ] Understands the trade-off between hard and soft mounts and when to use each
- [ ] Can diagnose common NFS issues: stale file handle, permission denied, slow performance
- [ ] Can set up CIFS and SSHFS mounts as alternatives to NFS

---

### Think About This

1. Design a high-availability NFS setup for a Kubernetes cluster that needs
   ReadWriteMany persistent volumes. Requirements: survive single server failure,
   consistent performance, data must not be lost. What components would you use
   (load balancer, DRBD, Corosync/Pacemaker, or cloud-managed NFS)? What
   are the performance trade-offs of each approach? How would you handle the
   scenario where a pod is writing to NFS when the primary NFS server fails?

2. A scientific computing cluster reads 1TB datasets in parallel across 200
   compute nodes. The current NFS server is a single machine with 12Gbps of
   network. With 200 nodes, the theoretical demand is 200 * desired_throughput.
   At what per-node read throughput does the NFS server become the bottleneck?
   How would you design a solution that scales to 200 nodes without NFS server
   becoming a single point of throughput bottleneck? Consider both technical
   approaches (pNFS, distributed filesystems, caching) and operational trade-offs.

3. An application team reports that their NFS-backed application "loses data"
   occasionally during network disruptions. They are using soft mounts with
   `timeo=30,retrans=2`. Explain exactly what is happening at the protocol
   level during a 30-second network disruption: (a) what errors does the
   application receive, (b) what data is at risk, (c) what data is safe. Design
   a migration plan to hard mounts - what application changes are needed to
   handle the different failure behavior? What operational procedures are needed
   to avoid boot-time hangs?

---

### Interview Deep-Dive

**Foundational:**
Q: Explain NFS mount options and which ones you would use for a production application server.
A: NFS MOUNT OPTIONS FOR PRODUCTION: The most important options with explanations: PERFORMANCE: `rsize=1048576,wsize=1048576`: Read/write block sizes of 1MB. Default is 32KB - 30x smaller than optimal for modern networks. Each NFS READ or WRITE RPC call transfers this much data. With default 32KB on 1Gbps: reading 1GB = 32,768 RPC calls. With 1MB: 1,024 RPC calls - 30x fewer round-trips. For network storage, round-trip count matters as much as bandwidth. RELIABILITY: `hard`: if the NFS server is unreachable, the kernel retries indefinitely. The application process blocks (hangs) but does NOT receive an error. When the server recovers, the application resumes as if nothing happened. This is the SAFE option for application data - no data corruption. `soft`: after `retrans` failed retries, the kernel returns EIO to the application. Risk: application may not handle EIO, or may consider writes successful when they failed. For read-only mounts of non-critical data: `soft,timeo=30,retrans=2` (6 seconds total). TIMEOUT: `timeo=600`: 60 seconds (unit = 0.1s). For `hard` mount: this is the per-RPC timeout before retrying. `retrans=2`: retry 2 times before giving up (for soft) or before logging a message (for hard). BOOT/CLOUD: `nofail`: allow system to boot even if this mount fails. `_netdev`: wait for network before attempting mount. Essential for /etc/fstab entries. `noresvport`: don't require a privileged source port. Needed for cloud environments with NAT/firewalls. PROTOCOL: `vers=4.2` (or `vers=4.1`): specify NFSv4.2 explicitly. Avoids fallback to NFSv3 which has worse performance. EXAMPLE: `mount -t nfs4 server:/data /mnt -o rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,nofail,_netdev`

**Expert:**
Q: Compare NFSv3 and NFSv4 from a security and operational perspective, and when would you choose each?
A: NFSV3 ARCHITECTURE AND LIMITATIONS: NFSv3 uses multiple network services: (1) rpcbind (portmapper) on port 111; (2) mountd on a random dynamic port; (3) nfsd on port 2049; (4) statd and lockd on random ports for file locking. This makes firewall rules complex (you need to pin mountd/statd/lockd to specific ports). Authentication: AUTH_SYS only - the client sends its UID and GID in every RPC call. The server TRUSTS these values. Any client claiming uid=0 gets root access unless root_squash is configured. No encryption, no cryptographic authentication. Security implication: NFSv3 is only safe inside a TRUSTED network segment where all clients are controlled systems. NFSV4 IMPROVEMENTS: Single port (2049/tcp) - one firewall rule. Stateful: server tracks client open file state, enabling delegation (client can cache reads/writes without per-operation RPC calls). Compound operations: multiple operations in one RPC (OPEN + READ in one round-trip reduces latency on WAN). Integrated locking (no separate lockd). Kerberos authentication support: `sec=krb5` (auth only), `sec=krb5i` (auth + integrity), `sec=krb5p` (auth + encryption). NFSv4 ACLs: full POSIX+ ACL semantics. UID/GID sent as name@domain strings with server-side mapping - eliminates uid spoofing. CHOOSE NFSV3 WHEN: legacy infrastructure that doesn't support NFSv4, specific NFSv3-only applications, or migrations where changing version risks compatibility. CHOOSE NFSV4 WHEN: any new deployment, security requirements exist (Kerberos), firewall traversal needed, WAN or high-latency environments (compound operations help). KERBEROS SETUP REQUIREMENT: Both client and server need Kerberos tickets. This requires: Active Directory or MIT KDC deployment, keytab files on both client and server, nfs-idmapd with matching Domain setting, proper DNS (Kerberos is DNS-sensitive). Operational complexity: Kerberos adds a critical dependency (KDC must be reachable for NFS to work). For internal trusted networks: NFSv4 with default AUTH_SYS (not Kerberos) is a reasonable middle ground - single port, stateful, better performance, without Kerberos complexity. For multi-tenant or zero-trust environments: NFSv4 + Kerberos + `sec=krb5p` (encrypted NFS) is the correct choice.
