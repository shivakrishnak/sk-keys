---
id: LNX-102
title: "Linux Storage Architecture at Scale (LVM, RAID, Ceph)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-059, LNX-060
used_by: LNX-104
related: LNX-059, LNX-060, LNX-104
tags: [lvm, logical-volume-manager, pvcreate, vgcreate, lvcreate, lvextend, mdadm, software-raid, raid-0, raid-1, raid-5, raid-6, raid-10, ceph, cephfs, rbd, rados, osd, mon, crush-map, distributed-storage, erasure-coding, bluestore, glusterfs, storage-pools, thin-provisioning, snapshots, dm-cache, bcache, nvme, zfs-linux, stratis]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 102
permalink: /technical-mastery/lnx/linux-storage-architecture-lvm-raid-ceph/
---

## TL;DR

Linux storage architecture has three primary layers: **(1) LVM** (Logical Volume
Manager) - abstract physical disks into flexible logical volumes; resize,
snapshot, thin-provision without downtime. Commands: `pvcreate`, `vgcreate`,
`lvcreate`, `lvextend`. **(2) Software RAID** (`mdadm`) - combine disks for
redundancy and/or performance. RAID-1 (mirror, survives 1 disk), RAID-5
(parity, survives 1 disk, read performance), RAID-6 (double parity, survives
2 disks), RAID-10 (mirror+stripe, survives 1 disk per mirror pair). **(3)
Distributed storage** (Ceph) - pool of storage daemons (OSDs) presenting
block (RBD), filesystem (CephFS), or object (RADOS) interfaces at petabyte
scale. Ceph: `ceph status`, `ceph osd pool create`. For cloud-native: Ceph RBD
is the backing store for most Kubernetes persistent volumes in self-hosted clusters.
Single-node: LVM + software RAID. Multi-node scale: Ceph or cloud-native block
(AWS EBS, GCP PD).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-102 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | LVM, software RAID, mdadm, Ceph, distributed storage, storage architecture, logical volumes |
| **Prerequisites** | LNX-059 (filesystem), LNX-060 (disk management) |

---

### The Problem This Solves

**Problem 1**: A database server has a 1TB partition that is 95% full. The
server has a second 500GB disk that was added for this purpose. Without LVM:
need to create a new filesystem on the second disk, migrate data, update
application config. With LVM: `pvcreate /dev/sdb && vgextend datavg /dev/sdb
&& lvextend -l +100%FREE /dev/datavg/datalv && resize2fs /dev/datavg/datalv`.
No downtime, no data migration. The existing filesystem grows in place.

**Problem 2**: A cluster needs distributed storage for 200 Kubernetes pods
that each need ReadWriteOnce persistent volumes. Without Ceph: 200 local SSDs
(expensive, no sharing, no live migration). With Ceph RBD: pool of storage
nodes, each pod gets an RBD image from the pool. Pods can be rescheduled to
any node (volume follows). Capacity grows by adding OSD nodes. 99.99%
availability via replication.

---

### Textbook Definition

**LVM (Logical Volume Manager)**: A device mapper target that provides
abstraction between physical storage devices and logical volumes used by
filesystems. Three layers: Physical Volumes (PV) - actual block devices;
Volume Groups (VG) - pool of PVs; Logical Volumes (LV) - virtual partitions
carved from VG.

**Software RAID (mdadm)**: Kernel-based RAID implementation using the md
(multiple devices) driver. Combines block devices into arrays with redundancy
(RAID-1/5/6/10) or performance (RAID-0) or both (RAID-10).

**Ceph**: Open-source distributed storage system providing: RADOS (object
storage core), RBD (block devices backed by RADOS), CephFS (POSIX filesystem
backed by RADOS), RGW (S3/Swift-compatible object gateway).

**RAID comparison:**
| Level | Disks | Survives | Read speed | Write speed | Capacity |
|-------|-------|----------|-----------|------------|---------|
| RAID-0 | 2+ | 0 failures | N * disk | N * disk | 100% |
| RAID-1 | 2 | 1 failure | 2 * disk | 1 * disk | 50% |
| RAID-5 | 3+ | 1 failure | (N-1) * disk | (N-1) * disk | (N-1)/N |
| RAID-6 | 4+ | 2 failures | (N-2) * disk | (N-2) * disk | (N-2)/N |
| RAID-10 | 4+ | 1 per mirror | N/2 * disk | N/2 * disk | 50% |

---

### Understand It in 30 Seconds

```bash
# === LVM: flexible logical volume management ===

# Scenario: add new disk /dev/sdb, grow existing LV
# Step 1: Create Physical Volume
pvcreate /dev/sdb
pvs  # list physical volumes
# PV         VG     Fmt  PSize  PFree
# /dev/sda2  rootvg lvm2 100g   0g
# /dev/sdb          lvm2 200g   200g  <- new disk

# Step 2: Extend Volume Group with new PV
vgextend rootvg /dev/sdb
vgs  # list volume groups
# VG     PV  LV  SN  Attr   VSize  VFree
# rootvg  2   3   0   wz--n- 300g   200g  <- 200g free now

# Step 3: Extend Logical Volume
lvextend -l +100%FREE /dev/rootvg/datalv  # use all free space
# or: lvextend -L +50G /dev/rootvg/datalv  # add exactly 50G

# Step 4: Grow filesystem (no unmount needed for ext4!):
resize2fs /dev/rootvg/datalv
# xfs: xfs_growfs /mnt/data (XFS cannot shrink, only grow)

# Verify:
df -h /mnt/data
# /dev/mapper/rootvg-datalv  290G  85G  205G  30%  /mnt/data

# LVM snapshot (instant, for backup):
lvcreate -L 10G -s -n datalv_snap /dev/rootvg/datalv
# Creates point-in-time snapshot using 10GB copy-on-write space
# Mount snapshot (read-only) for backup:
mount -o ro /dev/rootvg/datalv_snap /mnt/snapshot
# Backup, then remove:
lvremove /dev/rootvg/datalv_snap

# === Software RAID with mdadm ===

# Create RAID-10 array from 4 disks:
mdadm --create /dev/md0 --level=10 --raid-devices=4 \
    /dev/sda /dev/sdb /dev/sdc /dev/sdd

# Monitor sync progress:
cat /proc/mdstat
# Personalities : [raid10]
# md0 : active raid10 sdd[3] sdc[2] sdb[1] sda[0]
#       419430400 blocks [4/4] [UUUU]
#       [===>................]  resync = 16.1% (...)
# < Wait for resync to complete before heavy I/O >

# Check array status:
mdadm --detail /dev/md0
# State : clean
# Active Devices : 4
# Working Devices : 4
# Failed Devices : 0

# Simulate disk failure:
mdadm --fail /dev/md0 /dev/sda
mdadm --detail /dev/md0 | grep -E "State|Failed"
# State : clean, degraded  <- still running!
# Failed Devices : 1

# Add replacement disk:
mdadm --add /dev/md0 /dev/sde  # new disk
# RAID auto-rebuilds

# Persist RAID config:
mdadm --detail --scan >> /etc/mdadm.conf

# === Ceph distributed storage ===

# Check cluster health:
ceph status
# cluster:
#   id: abc123
#   health: HEALTH_OK
# services:
#   mon: 3 daemons, quorum node1,node2,node3
#   osd: 12 OSDs: 12 up, 12 in
# data:
#   pools: 3 pools, 192 pgs
#   usage: 2.5 TiB / 12 TiB

# Create a storage pool for Kubernetes RBD volumes:
ceph osd pool create kubernetes 128  # 128 placement groups
rbd pool init kubernetes

# Create an RBD image (block device):
rbd create --size 20G kubernetes/myvolume
rbd info kubernetes/myvolume
# name: myvolume, size 20 GiB

# Map and format as block device on a node:
rbd map kubernetes/myvolume
# /dev/rbd0
mkfs.ext4 /dev/rbd0
mount /dev/rbd0 /mnt/ceph-volume

# Ceph OSD status (disk health):
ceph osd tree
# ID  CLASS  WEIGHT   TYPE NAME       STATUS  REWEIGHT  PRI-AFF
# -1        12.00000  root default
# -3         4.00000    host node1
#  0  hdd    2.00000      osd.0         up   1.00000   1.00000
#  1  hdd    2.00000      osd.1         up   1.00000   1.00000
# ...
```

---

### First Principles

```
Storage abstraction layers on Linux:

Hardware layer:
  NVMe SSD, SATA SSD, HDD, SAN LUN, NVMe-oF
  Block device: /dev/nvme0n1, /dev/sda, /dev/sdb

LVM layer (optional, single-node):
  Purpose: flexibility (resize, snapshot, thin provisioning)
  
  Physical Volumes (PV): wrap block devices in LVM metadata
    pvcreate /dev/sda /dev/sdb /dev/sdc
    
  Volume Group (VG): pool of PVs, allocates in 4MB extents
    vgcreate datavg /dev/sda /dev/sdb /dev/sdc
    Total size = sum of all PV sizes
    
  Logical Volumes (LV): virtual block devices from VG
    lvcreate -L 100G -n dblv datavg
    Result: /dev/datavg/dblv (use like a regular block device)
    
  LVM thin provisioning:
    Create thin pool (overcommit storage):
    lvcreate --type thin-pool -L 1T -n thinpool datavg
    Create thin volume (appears as 500GB, uses only actual data):
    lvcreate --type thin -V 500G --thinpool thinpool -n thinlv datavg
    Benefit: allocate 10TB of "thin" LVs from 1TB pool
    Risk: pool overcommit (all thin volumes fill up simultaneously)
    
  LVM snapshots (COW - Copy on Write):
    Point-in-time snapshot of an LV
    Initial size: 0 (shares extents with original)
    When original changes: old extent copied to snapshot
    Snapshot "grows" as original changes
    Used for: online backup, testing changes (snapshot before apply)

RAID layer (optional, local redundancy):
  Software RAID (mdadm) operates on raw block devices
  Creates: /dev/md0 (virtual block device from array)
  
  RAID-1 (mirroring): write goes to BOTH disks simultaneously
    Read: can read from either disk (faster reads)
    Failure tolerance: 1 disk failure
    Capacity: 50% (2 disks = 1 disk usable)
    
  RAID-5 (distributed parity):
    Data striped across N-1 disks, parity on Nth
    Parity rotates: disk 1 has parity for stripe 1,
                    disk 2 has parity for stripe 2, etc.
    Failure tolerance: 1 disk
    Write penalty: every write = read old data + read old parity
                   + write new data + write new parity (4 I/Os)
    RAID-5 write hole: if crash during write, parity inconsistent
    Mitigation: battery-backed write cache, or use RAID-6 or RAID-10
    
  RAID-6 (double parity):
    Like RAID-5 but with TWO parity blocks per stripe
    Can survive ANY two simultaneous disk failures
    Important for large disk arrays: RAID-5 rebuild risk
    During RAID-5 rebuild (which reads ALL remaining disks):
      If a second disk fails: data loss!
    RAID-6 tolerates the second failure during rebuild
    
  RAID-10 (stripe of mirrors):
    Create pairs of mirrors, then stripe across pairs
    Performance: writes to 2 disks, reads from best
    Failure tolerance: 1 disk per mirror pair (worst case 1, best case N/2)
    Best choice for: databases (write performance + reliability)

Distributed storage (Ceph):
  Scale-out: add nodes to increase capacity and throughput
  No single point of failure: data replicated across failure domains
  
  RADOS (Reliable Autonomic Distributed Object Store):
    Core storage layer: stores objects (not files or blocks)
    Each object: ID + data + metadata
    
  CRUSH map: determines object placement
    "Place replicas of object X on OSD 3, 7, 12"
    Rules: "always place in different failure domains (racks)"
    CRUSH = Controlled Replication Under Scalable Hashing
    
  OSDs (Object Storage Daemons):
    One per disk, manage storage and replication
    Self-healing: if OSD fails, peer OSDs re-replicate its data
    
  Monitors:
    3 or 5 per cluster (quorum-based)
    Store cluster map (CRUSH map, OSD map)
    
  BlueStore (default):
    OSD directly manages raw block device (not ext4/xfs)
    Bypasses filesystem overhead
    Better performance, checksums for data integrity
    
  Placement Groups (PGs):
    Objects mapped to PGs (via hash)
    PGs mapped to OSDs (via CRUSH)
    Allows Ceph to move minimal data when OSDs are added/removed
    Rule of thumb: 100-200 PGs per OSD for most workloads
    
  Replication vs Erasure Coding:
    Replication (3x default): 3 full copies across different OSDs
      Simple, fast reads, fast recovery from failure
      Cost: 3x storage overhead
    Erasure coding (EC): like RAID-6 but distributed
      EC 4+2: 6 shards, need any 4 to reconstruct (2 failures tolerable)
      Cost: 1.5x storage overhead (6 shards for 4x data)
      Tradeoff: slower writes (calculate parity), slower recovery
      Use for: cold storage, archival (large objects, infrequent reads)
```

---

### Thought Experiment

Storage design for a production Kubernetes cluster:

```bash
# Requirements:
# - 50 nodes, each with 2x NVMe SSDs
# - Need: ReadWriteOnce PVs for stateful apps (databases)
# - Need: ReadWriteMany PVs for shared content (media files)
# - 99.99% availability requirement
# - 50TB total storage capacity needed

# === Option A: Local storage + LVM ===
# Each node: 2x NVMe in RAID-1 (mirror), LVM on top
# PVs: local, high performance (NVMe RAID-1)
# Kubernetes: localVolume provisioner (StorageClass: local-storage)
#
# Pros: maximum IOPS (direct NVMe), simple
# Cons: pod must be scheduled to specific node (no live migration),
#       node failure = PV unavailable until node recovers,
#       ReadWriteMany impossible (can't share local disk)

# Each node setup:
mdadm --create /dev/md0 --level=1 --raid-devices=2 \
    /dev/nvme0n1 /dev/nvme1n1
pvcreate /dev/md0
vgcreate data /dev/md0
# Kubernetes local volume provisioner manages LVs from this VG

# === Option B: Ceph cluster (3-replica RBD) ===
# 50 nodes contribute storage to Ceph pool
# Kubernetes: Rook-Ceph operator
# PVCs automatically provision Ceph RBD images

# Install Rook-Ceph operator:
kubectl apply -f https://raw.githubusercontent.com/rook/rook/master/deploy/...

# StorageClass for RBD:
kubectl apply -f - << 'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: replicapool
  imageFormat: "2"
  imageFeatures: layering
reclaimPolicy: Retain
allowVolumeExpansion: true
EOF

# StatefulSet with Ceph RBD PVC:
# volumeClaimTemplates:
# - metadata:
#     name: data
#   spec:
#     accessModes: [ "ReadWriteOnce" ]
#     storageClassName: rook-ceph-block
#     resources:
#       requests:
#         storage: 100Gi

# Pros: pod can run on any node (volume travels with pod),
#       live migration works,
#       ReadWriteMany via CephFS (not RBD)
# Cons: ~20-30% overhead vs local IOPS (network traversal),
#       Ceph operational complexity

# === Option C: Hybrid ===
# Local NVMe (Ceph OSD on same disks) + Rook Ceph
# Ceph prefers local OSD for reads (CRUSH locality rule)
# Best of both: Ceph flexibility + near-local performance

# Ceph CRUSH rule for node-local primary reads:
ceph osd getcrushmap -o /tmp/crushmap.bin
crushtool -d /tmp/crushmap.bin -o /tmp/crushmap.txt
# Edit: add rule that prefers local OSD for primary reads
# crushtool -c /tmp/crushmap.txt -o /tmp/crushmap.bin
# ceph osd setcrushmap -i /tmp/crushmap.bin

# Capacity math:
# 50 nodes * 2x 1TB NVMe = 100TB raw
# Ceph 3-replica: 100TB / 3 = 33TB usable (meets 50TB? No, need bigger disks)
# Ceph EC 4+2: 100TB * 4/6 = 66TB usable (meets 50TB requirement)
```

---

### Mental Model / Analogy

```
LVM = warehouse shelving system:

Physical disks (PVs) = warehouse floor sections
  "Section A: 100 sqm, Section B: 200 sqm"
  Each section is independent, different sizes

Volume Group (VG) = entire warehouse floor:
  Combine sections into one managed pool
  "Total warehouse: 300 sqm"
  Can add sections later (vgextend)

Logical Volumes (LVs) = adjustable shelving units:
  Allocate from warehouse: "This department gets 150 sqm"
  LVM extents = shelf modules (4MB each)
  Resize: "Give this department 50 more sqm" (lvextend)
  No physical rearrangement needed!

Thin provisioning = "Furniture rental commitment":
  Promise 500 sqm to departments, only have 300 sqm
  Works if departments don't actually USE all promised space
  Risk: if they all fill up simultaneously - overcommit!

LVM snapshot = photography of warehouse at a moment:
  Photo taken instantly
  As warehouse changes: remember what changed (COW)
  Can "restore" to photo state by rewinding changes

RAID = redundant storage buildings:

RAID-1 = twin buildings (mirror):
  Same documents stored in both buildings
  If one burns down: other has everything
  Write: must update both buildings simultaneously
  Read: can use either building (faster)
  Cost: 2x building = 1x usable

RAID-5 = library with parity index:
  Books stored across 3 shelves + 1 "checksum shelf"
  If one shelf collapses: reconstruct from other 2 + checksum
  Read: across all 3 data shelves (fast)
  Write: must update checksum when any shelf changes

RAID-6 = library with TWO parity indexes:
  Survives 2 shelf collapses
  Important for large libraries: recovering from 1 collapse takes time,
  during which a 2nd collapse would lose everything (RAID-5 risk)

Ceph = city-wide distributed library system:

OSDs = neighborhood libraries (one per disk):
  Each stores thousands of books (objects)
  Self-organizing: if a library closes, other libraries
  redistribute copies (self-healing)

CRUSH map = city librarian's placement rules:
  "Store 3 copies, never in same neighborhood block"
  If earthquake hits one block: other blocks safe

Monitors = city council (3-5 nodes, quorum):
  Maintain the official map of where all libraries are
  Without quorum: no operations (safety: no split-brain)

RBD = virtual "library card" that becomes a book collection:
  Your database thinks it has a local hard drive
  Actually: millions of objects spread across dozens of OSDs
  Performance: multiple OSDs read/write in parallel

Erasure coding (Ceph EC) = compressed archival:
  Instead of 3 full copies: encode data into 6 shards (4 data + 2 parity)
  Reconstruct from any 4 of 6 shards
  Like RAID-6 but distributed across many machines
```

---

### Gradual Depth - Five Levels

**Level 1:**
LVM concepts: PV, VG, LV. Basic commands: pvcreate, vgcreate, lvcreate, lvextend.
RAID levels: RAID-1 (mirror) and RAID-10 (mirror+stripe) for redundancy.
Software RAID with mdadm basics. Why distributed storage (Ceph) is needed at scale.

**Level 2:**
LVM snapshots: creating, mounting, backup workflow. LVM thin provisioning:
when to use, risks of overcommit. RAID-5 vs RAID-6 trade-offs. RAID recovery:
failed disk, mdadm --add for replacement. Ceph architecture: OSD, Monitor, CRUSH.
`ceph status` and `ceph health` for cluster monitoring. Rook-Ceph for Kubernetes.

**Level 3:**
LVM cache (dm-cache, bcache): NVMe as cache tier for HDD. dm-thin for production
thin provisioning. RAID write hole and mitigation (battery-backed cache, RAID-6).
Ceph placement groups: calculation, impact on performance. Ceph BlueStore vs
FileStore. Erasure coding vs replication trade-offs. CRUSH map customization
for rack-aware placement. CephFS vs RBD for different workloads.

**Level 4:**
LVM mirror (mirroring at LVM layer, not RAID). LVM RAID types (lv --type raid1/raid5).
dm-multipath for SAN multipath. Ceph RADOS gateway (S3/Swift API). Ceph MDS
(Metadata Server) for CephFS scalability. Ceph scrubbing and deep-scrubbing
for data integrity. OSD replacement procedure. Ceph monitoring with Prometheus
and mgr/prometheus module. Performance tuning: OSD journal, BlueStore
cache sizing.

**Level 5:**
Ceph CRUSH algorithm internals: stable hashing, tree traversal for OSD
selection. RADOS protocol: PG states (active, clean, recovering, degraded,
inconsistent). Ceph's approach to consistency: RADOS provides strong
consistency per-object. File sharding in CephFS: how MDS handles large
directories. Ceph-volume: replacing ceph-disk for OSD provisioning. Ceph
stretch mode for multi-datacenter deployments. NVMe-oF with Ceph for
ultra-low latency distributed block storage. Comparing Ceph with AWS EBS:
architectural differences, when self-hosted Ceph beats cloud block storage.
ZFS on Linux: alternative to LVM+ext4+RAID (integrated compression,
deduplication, snapshots).

---

### Code Example

**BAD - ad-hoc disk management without LVM:**
```bash
# BAD: Direct partition on disk, no LVM
# Scenario: /dev/sda1 (100GB) is 95% full
# "Solution": add /dev/sdb as new mount point
mkfs.ext4 /dev/sdb
mount /dev/sdb /data2
# Now application must be reconfigured to use /data2
# OR must copy all data from /data to /data2 (hours of downtime)
# AND: /data still only 100GB, must either use two paths
#      or migrate entirely

# BAD: no RAID, single disk for critical data
# Risk: disk failure = data loss, immediate downtime
# No warning before failure (SMART tools not configured)

# BAD: Ceph pool with too few or too many placement groups
ceph osd pool create mypool 1  # 1 PG = single OSD bottleneck!
# or
ceph osd pool create mypool 65536  # 65536 PGs = too much memory overhead
# Rule of thumb: 100-200 PGs per OSD (for a 10-OSD cluster: 1024-2048 PGs)
```

```bash
# GOOD: LVM-based storage for flexibility

# Step 1: Initial setup - 3 disks for database storage
pvcreate /dev/sdb /dev/sdc /dev/sdd
vgcreate dbvg /dev/sdb /dev/sdc /dev/sdd
lvcreate -l 80%VG -n dblv dbvg  # use 80% of VG for data LV
lvcreate -l 10%VG -n loglv dbvg  # 10% for log LV
# (leave 10% free for snapshots and emergencies)

mkfs.xfs /dev/dbvg/dblv
mkfs.xfs /dev/dbvg/loglv
mount /dev/dbvg/dblv /var/lib/postgresql/data
mount /dev/dbvg/loglv /var/lib/postgresql/wal

# When dblv is 95% full and new disk arrives:
pvcreate /dev/sde
vgextend dbvg /dev/sde
lvextend -l +100%FREE /dev/dbvg/dblv
xfs_growfs /var/lib/postgresql/data
# Done: zero downtime, no data migration

# Pre-backup snapshot (online, consistent):
# First: tell PostgreSQL to checkpoint:
psql -c "CHECKPOINT; SELECT pg_start_backup('pre-snapshot');"
lvcreate -L 20G -s -n dblv_snap /dev/dbvg/dblv
psql -c "SELECT pg_stop_backup();"
# Mount snapshot and backup:
mount -o ro /dev/dbvg/dblv_snap /mnt/snapshot
rsync -a /mnt/snapshot/ backup-server:/backups/pg/
umount /mnt/snapshot
lvremove -f /dev/dbvg/dblv_snap

# GOOD: RAID-10 setup for high-performance database storage:
mdadm --create /dev/md0 --level=10 --raid-devices=4 \
    --chunk=128 \  # 128KB chunks (good for database I/O pattern)
    /dev/nvme0n1 /dev/nvme1n1 /dev/nvme2n1 /dev/nvme3n1
# LVM on top of RAID-10:
pvcreate /dev/md0
vgcreate fastvg /dev/md0
lvcreate -l 90%VG -n fastlv fastvg
mkfs.xfs -f -d agcount=32 /dev/fastvg/fastlv  # 32 AG for parallelism
mount -o noatime,nodiratime,logbufs=8 /dev/fastvg/fastlv /var/lib/postgresql
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "LVM adds significant performance overhead" | LVM is a device mapper kernel driver. The overhead for simple linear LVs is <1% for most workloads - it's a thin software layer between the block device and filesystem. Measured: random 4KB read latency: direct block device vs LVM LV: ~2-5 microsecond difference on NVMe. This is negligible. LVM thin provisioning adds more overhead (copy-on-write tracking), but even thin LVs are measured in single-digit percentage overhead. The flexibility (online resize, snapshots, thin provisioning) is worth the <1% overhead for almost all workloads. The exception: extreme latency-sensitive workloads (<10 microseconds target) should test LVM vs direct device, but this is unusual. |
| "RAID-5 is obsolete and should never be used" | RAID-5 has a real failure risk: the "RAID-5 write hole" (if crash during write, parity is inconsistent) and the "URE (Unrecoverable Read Error) risk during rebuild" (large HDDs have 1 in 10^14 bit URE rate; a 4TB disk rebuild may read 4TB = statistically likely to hit a URE, causing rebuild failure and data loss). HOWEVER: RAID-5 is fine for: NVMe SSDs (much lower URE rate), smaller arrays (3-4 disks), arrays with battery-backed write cache (mitigates write hole), read-heavy workloads. The recommendation to "always use RAID-6 or RAID-10" applies primarily to: large HDD arrays (8+ disks), arrays without battery-backed cache, write-intensive workloads. For a 3-disk NVMe array in a server: RAID-5 is reasonable. For a 12-disk HDD array in production: use RAID-6 or RAID-10. |
| "Ceph requires dedicated hardware and is only for large-scale deployments" | Rook-Ceph can run on 3+ Kubernetes nodes with as little as 1 additional disk per node. A minimal Ceph cluster: 3 nodes, 1 OSD per node (3 OSDs total), 3-replica replication. Minimum useful capacity: 3 * disk_size / 3 = 1x disk size per node (with 3-replica). Recommended minimum for production: 3 nodes with 2+ disks each. Rook-Ceph automates all the complexity: OSD provisioning, monitor deployment, health monitoring, Kubernetes StorageClass creation. For a 5-10 node Kubernetes cluster: Rook-Ceph is completely appropriate. It provides ReadWriteMany (CephFS), ReadWriteOnce (RBD), and S3-compatible object storage (RGW) - three storage types from one deployment. |
| "Software RAID is inferior to hardware RAID" | Modern software RAID (Linux mdadm) is equal to or better than most hardware RAID in several dimensions: (1) CPU overhead: modern CPUs have hardware XOR acceleration for RAID-5/6 parity; mdadm uses it; overhead is <2% even for writes. (2) Reliability: hardware RAID cards with batteries can fail silently (firmware bugs, battery failure), losing data with no warning. mdadm failure is visible in OS logs and /proc/mdstat. (3) RAID-5 write hole: most hardware RAID cards have battery-backed write cache that protects against this; mdadm on NVMe with filesystem journal provides similar protection. (4) Recovery: mdadm array is readable on any Linux system with any SATA controller. Hardware RAID requires same controller model to recover. (5) Performance: hardware RAID adds latency (PCIe communication); mdadm runs in kernel directly. For enterprise features (proprietary cache algorithms): some hardware RAID cards outperform mdadm, but these are expensive. For most workloads: mdadm on NVMe is the better choice. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: RAID-5 degraded - one disk failed ===
# Alert: /dev/md0 is degraded

cat /proc/mdstat
# md0 : active raid5 sdc[2] sdb[1] sda[0]
#       200000000 blocks level 5, 64k chunk, [3/2] [_UU]
# ^ [3/2] means: 3 disks expected, only 2 up!
# ^ [_UU]: first disk (U=up, _=down) is sda - failed!

# Identify failed disk:
mdadm --detail /dev/md0 | grep -E "failed|State"
# State : clean, degraded  <- still running!
# /dev/sda: failed

# Check SMART data on failed disk:
smartctl -a /dev/sda
# SMART overall-health: FAILED!  <- disk hardware failure

# Add replacement disk (physically replaced /dev/sda with new disk):
mdadm --add /dev/md0 /dev/sda  # or /dev/sde if using a new slot

# Monitor rebuild:
watch cat /proc/mdstat
# [=>.................]  recovery = 6.3% (50GB/790GB finish in ~2h)

# IMPORTANT: DO NOT heavy I/O during rebuild!
# During rebuild: one disk failure = data loss (RAID-5 with 2 failed)

# === Failure: LVM VG not found after reboot ===
# df shows: /mnt/data not mounted

vgs  # lists no VGs!
pvs  # no PVs found

# Debug: are the disks present?
lsblk
# /dev/sdb  (disk present, but no LVM label shown)

# Rescan LVM metadata:
pvscan  # scans for PVs
vgscan  # scans for VGs
# If found: vgchange -ay datavg  # activate VG
# If not found: check disk:
hexdump -C /dev/sdb | head -20
# If: all zeros -> disk initialized but LVM metadata gone
# If: "LABELONE" seen -> LVM header present, try:
pvs -v --config "devices { scan = '/dev/sdb' }"

# === Failure: Ceph HEALTH_WARN - OSD down ===
ceph status
# health: HEALTH_WARN
# 1 osds down
# Degraded data: 1.5% (15 GB/1 TiB)

ceph osd tree
# ID  ...  STATUS
# 5   hdd  2.0 TiB  osd.5  down   <- osd.5 is down

# Identify which node hosts osd.5:
ceph osd find 5
# {"osd": 5, "host": "node3"}

# Check the OSD process on node3:
ssh node3 systemctl status ceph-osd@5
# Active: failed (Result: exit-code)

# Check logs:
ssh node3 journalctl -u ceph-osd@5 | tail -20
# bluestore: read error at offset 1024, size 512, status -5 (EIO)
# ^ Disk read error! Physical disk issue on node3

# Check disk SMART:
ssh node3 smartctl -a /dev/sde  # the disk backing osd.5

# Ceph will re-replicate data from remaining OSDs automatically
# Watch recovery:
ceph pg stat
# 192 active+clean, 12 active+recovering
# Recovery speed: 85 MB/s (recovering from degraded)
```

---

### Related Keywords

**Foundational:**
LNX-059 (filesystem), LNX-060 (disk management)

**Builds on this:**
LNX-104 (Linux observability platform)

**Related:**
LNX-104 (observability platform design)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `pvcreate /dev/sdb` | Initialize disk as LVM PV |
| `vgextend myvg /dev/sdb` | Add disk to VG |
| `lvextend -l +100%FREE /dev/vg/lv` | Extend LV to fill VG |
| `resize2fs /dev/vg/lv` | Grow ext4 filesystem to match LV |
| `mdadm --detail /dev/md0` | RAID array status |
| `cat /proc/mdstat` | RAID sync progress |
| `ceph status` | Ceph cluster health |
| `ceph osd tree` | OSD topology and status |

**3 things to remember:**
1. LVM layer sequence: `pvcreate` -> `vgcreate` -> `lvcreate`. Extending: `vgextend` (add PV to VG) -> `lvextend` (grow LV) -> `resize2fs`/`xfs_growfs` (grow filesystem). XFS can only grow (not shrink); ext4 can do both.
2. RAID-5 rebuild risk: during rebuild, a second disk failure causes data loss. For large HDD arrays: use RAID-6 (tolerates 2 failures). For NVMe: RAID-5 is acceptable. RAID-10 = best performance + reliability for databases.
3. Ceph: 3 replicas = 33% storage efficiency, erasure coding (4+2) = 67% efficiency. Minimum cluster: 3 nodes with 1 OSD each. Rook-Ceph operator is the standard Kubernetes deployment method.

---

### Transferable Wisdom

LVM's abstraction (physical -> pool -> logical) is the same pattern as:
AWS EBS volume management (physical disks in AWS -> EBS volume pools -> EBS
volumes), Kubernetes PersistentVolume/PersistentVolumeClaim (physical storage
-> StorageClass -> PV -> PVC), database tablespaces (filesystem -> tablespace
pool -> tables/indexes). The RAID redundancy concepts transfer to: Kafka
partition replication (partition has 3 replicas across 3 brokers = RAID-1
analog), Cassandra replication factor (RF=3 across 3 DCs = RAID-6 analog),
distributed database quorum writes (write to 2 of 3 nodes = RAID-1 analog).
Ceph's CRUSH placement algorithm is the same challenge as: Kubernetes node
affinity/anti-affinity (spread pods across zones), Cassandra rack-aware
placement (spread replicas across racks), consistent hashing in distributed
caches (stable placement when nodes change). The "thin provisioning" concept
appears in: AWS EC2 EBS thin provisioning (you pay for what you use, not
allocated space), cloud database serverless (Aurora Serverless scales storage
on demand), container overlay filesystems (shared base layer, copy-on-write
per container - same concept as LVM snapshots).

---

### The Surprising Truth

Ceph was originally developed by Sage Weil as his PhD thesis at UC Santa
Cruz (published 2007). The CRUSH algorithm (Controlled Replication Under
Scalable Hashing) was the core contribution: a mathematical approach to
determining where to place data in a cluster that is: stable (most data
stays in place when nodes are added/removed), deterministic (any node can
calculate placement without looking it up), failure-domain-aware (replicas
placed in different racks/datacenters). Weil went on to found Inktank (2011),
which was acquired by Red Hat in 2014 for $175 million. Today, Ceph is the
standard storage backend for OpenStack and Kubernetes in large self-hosted
deployments, and the CRUSH algorithm is one of the most elegant solutions
in distributed systems.

The surprise: a PhD thesis became the storage infrastructure for a significant
fraction of the world's private cloud infrastructure. Red Hat ceph storage
and open-source Ceph via Rook now powers storage for many of the world's
largest enterprise Kubernetes deployments.

---

### Mastery Checklist

- [ ] Can create an LVM setup (PV, VG, LV) and extend it without downtime
- [ ] Understands RAID-1, RAID-5, RAID-6, and RAID-10 trade-offs
- [ ] Can set up a software RAID array with mdadm and handle disk failure
- [ ] Understands Ceph architecture (OSD, Monitor, CRUSH) at a conceptual level
- [ ] Can explain when to use LVM, software RAID, and Ceph for different scale requirements

---

### Think About This

1. Design storage for a high-availability PostgreSQL database: requirements are
   1TB data, 99.999% durability, ability to grow online, and <1ms write latency.
   Compare: (a) Local NVMe with LVM + RAID-10; (b) Ceph RBD with 3-replica;
   (c) AWS EBS io2 with Multi-Attach. For each: what is the failure tolerance,
   what is the maximum write latency, what is the cost model, and what is the
   operational complexity? Which would you recommend, and what additional
   measures are needed for 99.999% durability?

2. A Ceph cluster is showing `HEALTH_WARN: 1 osd down, degraded data 5%`.
   Walk through your investigation and recovery process. What is the risk
   to data while in this state? At what point does the situation become data
   loss risk? If the OSD comes back with disk errors (not just a temporary
   crash): what is your replacement procedure, and how long will the cluster
   be degraded? What Ceph parameters affect recovery speed, and what are
   the trade-offs of fast vs slow recovery?

3. An organization is choosing between: (a) RAID-10 with LVM on each server
   (server-local storage), (b) Ceph cluster shared across 20 servers, and
   (c) Cloud block storage (AWS EBS or GCP PD). They run 100 VMs and a
   Kubernetes cluster. Analyze each choice by: storage efficiency (% of
   raw capacity usable), failure scenarios, operational complexity, and
   cost at scale (10 PB of raw storage). What is the "right" choice for
   a startup vs a large enterprise?

---

### Interview Deep-Dive

**Foundational:**
Q: Explain LVM and why it's used instead of partitioning disks directly.
A: LVM PROBLEM STATEMENT: Traditional disk partitioning (fdisk, parted) is inflexible. Partition sizes are fixed: if you allocate 100GB for the database partition and it fills up, you cannot grow it without: stopping the database, creating a new partition on a different disk, copying all data, updating configuration. LVM solves this by adding two abstraction layers between physical disks and filesystems. LVM ARCHITECTURE: (1) Physical Volumes (PV): `pvcreate /dev/sdb` wraps a block device with LVM metadata. Think of it as adding the disk to "LVM's inventory." (2) Volume Group (VG): `vgcreate datavg /dev/sdb /dev/sdc` pools multiple PVs into one storage pool. VG manages allocations in 4MB "extents" across all PVs. (3) Logical Volumes (LV): `lvcreate -L 100G -n dblv datavg` carves a 100GB virtual block device from the VG. The filesystem (ext4, XFS, etc.) is created on the LV. KEY BENEFITS: (1) Online resize: `lvextend -l +100%FREE /dev/datavg/dblv && resize2fs /dev/datavg/dblv` - grows the LV and filesystem while running, zero downtime. Just add a new disk to the VG first: `pvcreate /dev/sdd && vgextend datavg /dev/sdd`. (2) Snapshots: `lvcreate -L 10G -s -n snap /dev/datavg/dblv` creates an instant, consistent point-in-time snapshot for backup - without stopping the application. The snapshot uses copy-on-write: only blocks that change after snapshot creation are stored separately. (3) Thin provisioning: allocate more logical space than physical, relying on not all LVs filling simultaneously. (4) Abstraction: `lvmove` moves extents between PVs transparently (useful for disk replacement without downtime). WHEN TO AVOID LVM: Extremely latency-sensitive workloads should benchmark LVM vs direct device. LVM overhead is typically <1% but measurable. Some all-NVMe high-frequency trading systems avoid LVM for the last microsecond of latency.

**Expert:**
Q: When would you choose Ceph over local storage for Kubernetes, and what are the operational challenges?
A: DECISION FRAMEWORK - CHOOSE CEPH WHEN: (1) Pod mobility required: if a pod runs on node-A and the node fails, local storage loses the data (or requires waiting for node-A to recover). Ceph RBD volumes can be mounted on any node - Kubernetes can reschedule the pod to node-B and the volume follows immediately. Essential for: stateful applications that must survive node failures with fast recovery. (2) ReadWriteMany required: local storage and basic cloud block (EBS, GCP PD) are ReadWriteOnce - only one node can mount. CephFS provides ReadWriteMany: multiple pods on multiple nodes mount the same volume simultaneously. Essential for: shared content (media files), distributed builds, shared configuration. (3) Storage efficiency: at large scale, Ceph erasure coding (4+2) provides 67% storage efficiency vs 50% for RAID-10. On 100TB raw: Ceph EC = 67TB usable vs RAID-10 = 50TB. (4) Multi-tenant environments: Ceph quotas, pool-level rate limiting, RBAC for storage access. CHOOSE LOCAL STORAGE WHEN: (1) Minimum latency required: NVMe local storage = 50-100 microseconds. Ceph RBD over 10Gbps network = 200-500 microseconds (additional network traversal). For latency-sensitive databases: local NVMe is often required. (2) Simple operations: no Ceph infrastructure to manage. (3) Pods never migrate: stateful applications with affinity rules that keep pods on specific nodes can safely use local storage. CEPH OPERATIONAL CHALLENGES: (1) Capacity planning: placement groups must be sized correctly at creation (hard to change later). Under-PGs = hot OSDs, over-PGs = memory overhead. (2) OSD failure handling: Ceph automatically re-replicates on OSD failure (self-healing), but this causes significant I/O on remaining OSDs. Must monitor recovery bandwidth and throttle if impacting production. (3) Monitor quorum: if 2 of 3 monitors fail, cluster enters read-only mode. Monitors must be on reliable nodes, preferably on separate failure domains. (4) Version management: Ceph upgrade procedure is well-documented but disruptive if done wrong. Rook-Ceph operator significantly simplifies this. (5) Performance tuning: BlueStore cache sizing, OSD memory allocation, PG autoscaling. RECOMMENDATION: For Kubernetes clusters where pod mobility and ReadWriteMany are important: Rook-Ceph is the best self-hosted option. For maximum simplicity or latency-critical workloads: cloud-native block storage (EBS, GCP PD) or local storage with pod affinity. Most production Kubernetes deployments use both: Ceph for general-purpose PVCs, local NVMe for databases.
