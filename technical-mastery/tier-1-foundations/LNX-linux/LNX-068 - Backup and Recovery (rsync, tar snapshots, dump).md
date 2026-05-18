---
id: LNX-068
title: "Backup and Recovery (rsync, tar snapshots, dump)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-009, LNX-032
used_by: LNX-099, LNX-102
related: LNX-009, LNX-032, LNX-048
tags: [rsync, tar, backup, rsnapshot, borgbackup, 3-2-1, incremental-backup, recovery, dump-restore, full-backup]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 68
permalink: /technical-mastery/lnx/backup-and-recovery/
---

## TL;DR

Linux backup tools: **rsync** (`-avz --delete`) for incremental sync,
`-e ssh` for remote. **tar** for snapshots (`tar czf backup.tar.gz /data`).
**rsnapshot** for space-efficient snapshots using hard links. **borgbackup**
for dedup, encryption, compression. 3-2-1 rule: 3 copies, 2 different media,
1 offsite. Critical: test restores regularly - untested backups are not
backups. `--exclude` patterns, `--one-file-system` to avoid crossing mount
points. `--bwlimit` for bandwidth control. Recovery: `tar xzf backup.tar.gz`,
`rsync` restores are self-healing.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-068 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | rsync, tar, backup, rsnapshot, borgbackup, 3-2-1, incremental, recovery |
| **Prerequisites** | LNX-009 (Disk management), LNX-032 (File permissions) |

---

### The Problem This Solves

**Problem 1**: A production server's disk fails. Without backups: all data
is lost, application is down until rebuilt from scratch. With rsync backups
to a remote server: restore by rsync-ing back from the backup server. With
borgbackup: any point-in-time snapshot is restorable in minutes.

**Problem 2**: Database was corrupted by a bad migration at 3pm. You need
to restore to the 2:55pm state. Without incremental point-in-time backups:
you're rolling back to last night's backup, losing hours of transactions.
With hourly rsnapshot or borgbackup: restore to 2:55pm snapshot in minutes.

---

### Textbook Definition

**rsync**: Network/local file synchronization tool. Transfers only changed
files/blocks (delta transfer). Uses its own efficient protocol over SSH or
rsync daemon. Key advantage: interrupted transfers can be resumed. Space-
efficient when combined with hard links for snapshots.

**tar (Tape ARchive)**: Creates archives of files/directories preserving
metadata (permissions, ownership, timestamps). `.tar` = uncompressed.
`.tar.gz` (`.tgz`) = gzip compressed. `.tar.bz2` = bzip2. `.tar.xz` = xz
(best ratio, slower). Supports incremental backups via `--listed-incremental`.

**3-2-1 rule**: 3 copies of data, on 2 different storage media, with
1 copy offsite. Protects against: disk failure (copy 2), device failure
or fire (copy 3 offsite), ransomware (offsite + version history).

**borgbackup (borg)**: Deduplicating archiver with compression and encryption.
New backup only stores UNIQUE data blocks not already in the repository.
A 1GB daily backup where only 100MB changed: stores 100MB (plus small
metadata), not 1GB.

---

### Understand It in 30 Seconds

```bash
# === rsync: the workhorse ===

# Sync local directory to remote (the trailing slash matters!):
rsync -avz /local/data/ user@backup-server:/remote/data/
# -a = archive mode: recursive + preserve permissions, ownership, timestamps, symlinks
# -v = verbose
# -z = compress during transfer
# Note: /local/data/ WITH trailing slash = sync contents of data/
#        /local/data  WITHOUT trailing slash = sync the data/ dir itself

# Mirror (delete files on dest that don't exist in src):
rsync -avz --delete /local/data/ user@backup-server:/remote/data/

# Exclude patterns:
rsync -avz --exclude '*.log' --exclude 'tmp/' --exclude '.git/' \
    /local/data/ user@backup-server:/remote/data/

# Bandwidth limit (useful for backup over metered connections):
rsync -avz --bwlimit=10000 /data/ backup:/backup/  # 10 MB/s max

# Don't cross filesystem boundaries (avoid copying /proc, /sys, etc.):
rsync -avz --one-file-system / backup:/fullbackup/

# Dry run (show what WOULD be done without doing it):
rsync -avzn --delete /src/ dest/    # -n = dry run

# Progress bar:
rsync -avz --progress /data/ backup:/backup/

# Resume an interrupted large file transfer:
rsync -avz --partial /data/largefile.tar.gz backup:/backup/

# === tar: snapshots ===

# Create compressed archive:
tar czf backup-$(date +%Y%m%d).tar.gz /var/www/html/

# List contents without extracting:
tar tzf backup-2024-01-15.tar.gz | head -20

# Extract:
tar xzf backup-2024-01-15.tar.gz            # extract in current dir
tar xzf backup-2024-01-15.tar.gz -C /restore/  # extract to specific dir
tar xzf backup-2024-01-15.tar.gz var/www/html/index.html  # extract specific file

# Preserve permissions and ownership (important for restoring system dirs):
tar czf --same-owner --same-permissions backup.tar.gz /etc/

# Don't backup across mount points:
tar czf backup.tar.gz --one-file-system /

# Incremental backup (only changed files since last full):
# First run: creates the "listed" file (database of files):
tar czf full-backup.tar.gz \
    --listed-incremental=/var/backup/incremental.snar /data/
# Second run: only backs up changed files:
tar czf incr-backup-$(date +%Y%m%d).tar.gz \
    --listed-incremental=/var/backup/incremental.snar /data/

# === rsnapshot: snapshot backups with hard links ===
# Install: apt install rsnapshot
# Configure: /etc/rsnapshot.conf

# Key settings:
# snapshot_root /backup/snapshots/
# backup /var/www/ localhost/
# backup /etc/ localhost/
# backup_script /usr/bin/rsync-mysql-dump.sh localhost/mysql/
# retain daily 7    # keep 7 daily snapshots
# retain weekly 4   # keep 4 weekly snapshots
# retain monthly 12 # keep 12 monthly snapshots

rsnapshot daily     # run daily backup
rsnapshot weekly    # run weekly backup
rsnapshot configtest  # verify config syntax

# Result in /backup/snapshots/:
# daily.0/  <- most recent daily (today)
# daily.1/  <- yesterday
# daily.2/  <- 2 days ago
# weekly.0/ <- most recent weekly
# Unchanged files: hard links (no extra disk space)
# Changed files: new copy in the newer snapshot

# === borgbackup ===
# Install: apt install borgbackup

# Initialize repository (encrypted, zstd compression):
borg init --encryption=repokey-blake2 /backup/myrepo

# Create a backup (named by date):
borg create --compression zstd \
    /backup/myrepo::$(date +%Y-%m-%dT%H:%M:%S) \
    /var/www/html/ /etc/ /var/lib/myapp/

# List archives:
borg list /backup/myrepo

# Show sizes (compressed, deduplicated):
borg info /backup/myrepo

# Restore from a specific snapshot:
cd /restore-target/
borg extract /backup/myrepo::2024-01-15T14:00:00 var/www/html/

# Verify backup integrity:
borg check /backup/myrepo

# Prune old backups (keep: 7 daily, 4 weekly, 6 monthly):
borg prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6 /backup/myrepo
```

---

### First Principles

**rsync delta transfer algorithm:**
```
rsync on source machine:
  Split each file into fixed-size blocks (typically 700 bytes)
  Send: block checksums to destination

rsync on destination:
  For each block in existing destination file:
    Compute rolling checksum
    Check against source checksums
  
  Result:
  - Identical blocks: send back: "use your existing block at offset X"
  - Changed/new blocks: these will be sent fresh

rsync back to source:
  Receives: list of which blocks are identical (no send) vs changed (send these)
  Sends ONLY the changed blocks + reconstruction instructions

Total transfer: sum of changed blocks (typically much smaller than whole file)

Example:
  File: 1 GB log file, 100 MB new appended content
  rsync sends: ~100 MB (just the new blocks) + small overhead
  vs: scp would always send 1 GB
  
  Edge case: if file is reordered (sort, shuffle): many blocks "changed"
  rsync still works but delta transfer won't help much
  tarball of sorted content: usually similar size regardless of order
```

**3-2-1 rule coverage:**
```
Why 3 copies?
  - Copy 1: the original (on production server)
  - Copy 2: local backup (fast restore, protects disk failure)
  - Copy 3: offsite/cloud (protects against fire, flood, ransomware)
  2 copies: one failure = permanent data loss
  3 copies: two simultaneous failures = permanent data loss (much less likely)

Why 2 different media?
  - Don't put both copies on the same array/NAS/disk type
  - RAID is NOT backup: RAID protects against single disk failure
    but: ransomware, logic errors, accidental deletion affect the array as a unit
  - Example: copy 2 on different physical server; copy 3 on tape or cloud

Why 1 offsite?
  Fire, flood, physical theft removes all local copies simultaneously
  Cloud storage, different datacenter, or physical media rotation (tape to vault)

Common failures of 3-2-1 in practice:
  - "Cloud backup" = same cloud account, same region -> not truly offsite
  - Backup jobs run, restore never tested -> backup may be unrestorable
  - No versioning: ransomware encrypts files -> backup syncs encrypted files
    (solution: keep multiple versions, point-in-time recovery)
```

---

### Thought Experiment

Designing a backup strategy for a web application:

```bash
# Application: Nginx + PostgreSQL + user-uploaded files
# Requirements: RPO=1hr (max 1 hour data loss), RTO=4hr (restore in 4hr)

# === Database backup (critical, needs point-in-time) ===
# PostgreSQL continuous archiving + base backup:
# 1. Enable WAL archiving (in postgresql.conf):
#    archive_mode = on
#    archive_command = 'rsync %p backup-server:/pgwal/%f'
# 2. Nightly base backup:
cron_pgbackup() {
    PGPASSWORD="$PGPASS" pg_basebackup \
        -h localhost -U backup_user \
        -Ft -z -Xs -P \
        -D /tmp/pgbackup/
    
    rsync -avz /tmp/pgbackup/ backup-server:/pgbackup/$(date +%Y%m%d)/
    rm -rf /tmp/pgbackup/
}
# Recovery: WAL replay from base backup to any point in time (PITR)

# === File backup (user uploads) ===
# Hourly rsync to local backup:
rsync -avz --delete \
    /var/www/uploads/ \
    /backup/uploads/current/

# Nightly borgbackup to offsite:
borg create --compression zstd \
    user@offsite-server:/backup/uploads::$(date +%Y-%m-%dT%H:%M) \
    /var/www/uploads/

borg prune --keep-daily 30 --keep-monthly 12 \
    user@offsite-server:/backup/uploads

# === Configuration backup ===
# Weekly tar of /etc and nginx configs:
tar czf /backup/config-$(date +%Y%m%d).tar.gz \
    /etc/ /etc/nginx/ /etc/postgresql/ \
    --exclude=/etc/ssl/private/

rsync -avz /backup/ backup-server:/config-backup/

# === Restore test (CRITICAL - do monthly) ===
# Full recovery drill:
# 1. Spin up a test VM
# 2. Restore latest borgbackup archive to test VM
# 3. Restore PostgreSQL from base backup + WAL
# 4. Verify application runs correctly
# 5. Document restore time (is it within RTO=4hr?)
echo "Restore test procedure documented at: /opt/runbooks/restore-procedure.md"
```

---

### Mental Model / Analogy

```
Backup strategies = insurance policies

No backup = no insurance:
  "It will probably be fine" -> one disk crash = everything gone

rsync --delete (mirror) = robbery insurance only:
  Protects against hardware failure (disk dies, restore from copy)
  Does NOT protect against: "I accidentally deleted everything"
  (delete syncs to backup immediately), ransomware (sync encrypted files)

Versioned snapshots (rsnapshot, borgbackup) = full insurance with history:
  Hardware failure: restore from any snapshot
  Accidental deletion: restore from before the deletion
  Ransomware: restore from before infection
  "What was the state 3 days ago?": any snapshot available

3-2-1 rule = comprehensive disaster coverage:
  Local disk failure: covered by copy 2 (local NAS)
  Office fire: covered by copy 3 (offsite/cloud)
  Ransomware all local: covered by offline copy 3
  Cloud account compromise: not covered if all in one account

Untested backup = fire extinguisher that might be empty:
  "We have backups" + "we've never done a restore test"
  = unknown reliability
  = not actually a backup, just hope

RTO/RPO = insurance terms:
  RPO (Recovery Point Objective) = "how much data can we afford to lose?"
  -> Hourly backups = max 1 hour data loss = RPO = 1 hour
  RTO (Recovery Time Objective) = "how long can we be down?"
  -> "We need to be back up within 4 hours" = RTO = 4 hours
  Different data has different RPO/RTO: config file (RPO=1 day, fine),
  financial transactions (RPO=0, needs synchronous replication)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`tar czf backup.tar.gz /dir` for snapshots. `rsync -avz src/ dst/` for sync.
`--delete` for mirroring. Extract: `tar xzf backup.tar.gz`. 3-2-1 rule.
Test your restores.

**Level 2:**
rsnapshot for automated rotating snapshots. borgbackup for dedup+encryption.
`rsync --exclude` patterns. `--one-file-system`. Bandwidth limiting
`--bwlimit`. Cron-based automation. Pre-backup hooks (database dump before
rsync). RPO vs RTO.

**Level 3:**
Incremental tar with `--listed-incremental`. Postgres PITR (point-in-time
recovery) with WAL archiving. MySQL binlog for PITR. LVM snapshots for
consistent backups without downtime. `rsync --checksum` (verify by content
not mtime). `rdiff-backup` (reverse incremental: keeps latest as full,
stores diffs backward).

**Level 4:**
ZFS snapshots: `zfs snapshot pool/dataset@backup-name`, `zfs send/receive`
for replication. Backup encryption at rest: borg's `--encryption=repokey`,
gpg-encrypted tarballs. Backup monitoring: Prometheus alerts on backup age,
backup size anomalies. Backup bandwidth calculation: `10 GB/day * 365 =
3.65 TB/year` compressed. `restic` (borgbackup alternative in Go: same
concepts, easier setup).

**Level 5:**
S3-compatible backup targets: `aws s3 sync`, `rclone`, borg with
`borgmatic`. Immutable backups: S3 Object Lock, Wasabi, Backblaze B2
compliance mode (ransomware-resistant). Continuous data protection (CDP):
streaming WAL to S3 in real-time (Barman, WAL-G for PostgreSQL). Backup
SLA testing automation: monthly automated restore drill, verification
script. Multi-site replication: active-passive vs active-active, DRBD for
block-level synchronization, `rsync` limitations for large file stores
vs object storage.

---

### Code Example

**BAD - common backup mistakes:**
```bash
# BAD 1: Backup without testing (the most dangerous mistake):
# Cron runs rsync every night to backup-server
# No one has tested restore in 18 months
# Disk failure happens: rsync destination is corrupt
# = 18 months of "backups" that don't work

# GOOD: Monthly automated restore test:
#!/bin/bash
# test-restore.sh: monthly backup verification
BACKUP_PATH="$1"
RESTORE_DIR=$(mktemp -d)
# Extract to temp dir:
tar xzf "$BACKUP_PATH" -C "$RESTORE_DIR" 2>&1
# Verify key files:
for critical in etc/nginx/nginx.conf var/www/html/index.html; do
    [[ -f "$RESTORE_DIR/$critical" ]] || {
        echo "ALERT: Missing critical file: $critical"
        exit 1
    }
done
rm -rf "$RESTORE_DIR"
echo "Restore test passed: $(date)"

# BAD 2: rsync with --delete mirroring without versioning:
rsync -avz --delete /data/ backup:/data/
# Accidental: rm -rf /data/important/ at 2pm
# rsync runs at 3pm: --delete removes it from backup too!
# Now both copies are missing the directory

# GOOD: Keep versions with rsnapshot or borg, not just a mirror

# BAD 3: Not excluding unnecessary paths:
tar czf full-backup.tar.gz /
# Includes: /proc, /sys, /dev, /run (virtual filesystems - gigabytes of garbage)
# And /tmp, swap files, core dumps

# GOOD:
tar czf backup.tar.gz / \
    --one-file-system \   # don't cross mount points
    --exclude=/proc \
    --exclude=/sys \
    --exclude=/dev \
    --exclude=/run \
    --exclude=/tmp \
    --exclude=/var/tmp \
    --exclude="*.core" \
    --exclude="*.swap"
```

**GOOD - automated backup with monitoring:**
```bash
#!/bin/bash
# daily-backup.sh: production daily backup with alerting
set -euo pipefail

BACKUP_DEST="backup-server.internal:/backup/$(hostname)"
LOG_FILE="/var/log/backup.log"
ALERT_EMAIL="ops@company.com"
MAX_AGE_HOURS=25   # alert if no backup in 25 hours

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG_FILE"; }

alert() {
    echo "$*" | mail -s "BACKUP ALERT: $(hostname)" "$ALERT_EMAIL" 2>/dev/null || true
    log "ALERT: $*"
}

# Database dump before backup:
log "Starting backup"
if ! pg_dump -U backup myapp > /tmp/myapp.sql 2>>"$LOG_FILE"; then
    alert "Database dump failed!"
    exit 1
fi
gzip -f /tmp/myapp.sql

# Rsync with size logging:
BEFORE=$(df -k /data | awk 'NR==2{print $3}')
if ! rsync -avz --delete --stats \
    --exclude='*.log' --exclude='tmp/' \
    /data/ "$BACKUP_DEST/data/" \
    /tmp/myapp.sql.gz "$BACKUP_DEST/db/" \
    >> "$LOG_FILE" 2>&1; then
    alert "rsync backup failed! Check $LOG_FILE"
    exit 1
fi
AFTER=$(df -k /data | awk 'NR==2{print $3}')

# Touch a timestamp marker (for monitoring):
touch /var/run/last-backup-success
log "Backup completed. Data: $(( (AFTER-BEFORE)/1024 )) MB transferred"

# Cleanup old dump:
rm -f /tmp/myapp.sql.gz
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "RAID is a backup" | RAID protects against DISK FAILURE (a hardware redundancy mechanism), not data loss. RAID does nothing for: accidental deletion (immediately on all disks in the array), ransomware (encrypts data on all disks simultaneously), logical corruption (bug writes bad data everywhere), fire/theft (the entire RAID system is gone). A RAID-5 array with 4 disks: one disk fails and is replaced = no data loss. You delete /data/ = data gone from all disks. RAID provides availability (no downtime on disk failure), not data protection. A backup strategy requires both RAID (for availability) AND separate copies. |
| "Cloud sync (Dropbox, Google Drive) is a backup" | Cloud sync services sync files bidirectionally - if you delete a file locally, it's deleted from the cloud (usually). They also sync file corruption. Some offer version history (Dropbox 30 days, Google Drive 30 days), which helps somewhat. But: (1) Version history may cost extra. (2) Sync deletes on "disaster" scenarios (ransomware encrypts and syncs). (3) No guaranteed retention. True cloud backup uses dedicated backup tools (AWS Backup, Backblaze B2, borgbackup to Wasabi) with explicit retention policies and immutability options. |
| "rsync --delete is safe because it's incremental" | `--delete` removes files from the destination that no longer exist in the source. "Incremental" only means it transfers changed files efficiently. `--delete` makes rsync a MIRROR, not a backup. If your source is the production server and you accidentally delete a directory, the next rsync run will faithfully delete that directory from the backup too. `--delete` without versioning = single point of failure. Safe use: `--delete` is appropriate for MIRRORING (keeping an exact copy for disaster recovery), but you still need a separate VERSIONED backup. |
| "A compressed tar archive preserves all file metadata" | tar preserves: file contents, permissions (mode bits), ownership (user/group), timestamps (mtime). It does NOT preserve: ACLs (Access Control Lists) by default (use `--acls`), extended attributes (`--xattrs`), SELinux contexts (`--selinux`). For system backups where security labels matter: `tar --acls --xattrs --selinux czf backup.tar.gz /etc/`. Also: numeric vs symbolic ownership: use `-p` (same owner) with `--numeric-owner` to avoid owner name lookup issues when restoring on different systems. |
| "Backing up /etc is enough for system recovery" | /etc contains configuration but NOT: installed binaries (/usr/bin, /usr/lib), application code (/opt, /var/www), user data (/home), database files. A full system restore requires: package list (`dpkg --get-selections`), all application files, databases (via dump, not raw files - PostgreSQL raw files are not portable across versions), and /etc. A practical "full system backup" strategy: /etc (small, critical configs), application data directories (/opt, /var/www, /srv), database dumps (not raw data files), package list for reinstalling. The OS itself is usually faster to reinstall than restore - boot from ISO, `apt install --set-selections`, then restore /etc and data. |

---

### Failure Modes & Diagnosis

**Backup verification and recovery drill:**
```bash
# Scenario: Need to verify backup integrity and measure restore time

# Step 1: Verify borgbackup repository:
borg check --verbose /backup/myrepo
# Checks: manifest, archive integrity, all block checksums
# Expected: "Finished, all archives okay."

# Step 2: Measure restore time for RPO/RTO planning:
time borg extract --dry-run /backup/myrepo::2024-01-15T14:00:00
# Dry run shows how many files would be extracted and estimated size

# Step 3: Actual partial restore test:
mkdir /tmp/restore-test
borg extract /backup/myrepo::2024-01-15T14:00:00 \
    --destination /tmp/restore-test \
    var/www/html/
# Verify key file exists and has correct content:
md5sum /var/www/html/index.html /tmp/restore-test/var/www/html/index.html
# Both should match

# Step 4: rsync dry run to see what would be synced:
rsync -avzn --delete /data/ backup:/backup/data/ 2>&1 | tail -20
# Shows: send vs delete list, transfer size
# Check: is anything being deleted that shouldn't be?

# Step 5: Check backup freshness (for monitoring):
find /backup/ -name "*.tar.gz" -newer /backup/.last_success | head
# If empty: no new backups since last success marker
last_backup=$(stat -c %Y /backup/.last_success 2>/dev/null || echo 0)
now=$(date +%s)
age=$(( (now - last_backup) / 3600 ))
if (( age > 25 )); then
    echo "WARNING: Last backup was $age hours ago!"
fi
```

---

### Related Keywords

**Foundational:**
LNX-009 (Disk management), LNX-032 (File permissions)

**Builds on this:**
LNX-099 (Fleet management), LNX-102 (Storage at scale)

**Related:**
LNX-048 (Cron/scheduling), LNX-009 (Disk/storage)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `rsync -avz src/ dst/` | Incremental sync |
| `rsync -avz --delete src/ dst/` | Mirror (delete extra in dst) |
| `rsync -avz --exclude='*.log' src/ dst/` | Exclude patterns |
| `tar czf backup.tar.gz /dir` | Create compressed archive |
| `tar xzf backup.tar.gz -C /restore` | Extract to directory |
| `borg create repo::$(date +%Y%m%dT%H%M) /data` | Create borg snapshot |
| `borg list repo` | List archives |
| `borg extract repo::ARCHIVE path/to/file` | Restore file |

**3 things to remember:**
1. 3-2-1 rule: 3 copies, 2 media types, 1 offsite - AND test restores monthly
2. `rsync --delete` = mirror (not versioned backup); use rsnapshot or borgbackup for versioned snapshots
3. Backup the database via dump (`pg_dump`, `mysqldump`), not raw data files - raw files are not portable across versions

---

### Transferable Wisdom

Backup concepts appear everywhere: Git is a version control system with
snapshot semantics (borgbackup and rsnapshot are inspired by Git's content-
addressable storage). Docker image layers are content-addressed overlays -
same deduplication principle as borgbackup. Cloud provider backup services
(AWS Backup, GCP Cloud Backup) implement the 3-2-1 rule at scale. WAL-G
for PostgreSQL = continuous cloud backup by streaming WAL files. Kubernetes
Velero: namespace-level backups of cluster state and PersistentVolumes.
The RPO/RTO framework applies to: database replication (RPO=0 with sync
replication), multi-region DR (RTO depends on failover automation speed),
Kubernetes cluster recovery (RTO determined by etcd restore time). The
principle "test your restores, not just your backups" applies to everything
that needs to be reliable: test your runbooks, test your CI/CD rollback,
test your DR procedures - untested = unreliable.

---

### The Surprising Truth

rsync's delta transfer algorithm was described by Andrew Tridgell in his
1996 PhD thesis "Efficient Algorithms for Sorting and Synchronization" at
Australian National University - and the implementation became one of the
most widely deployed network tools in history. The algorithm's insight:
to synchronize files between two systems without sending the full file,
you can compute rolling checksums over fixed-size blocks and only transfer
blocks that differ. This is the same concept used by zsync (for ISO
downloads), binary delta updates in software distribution (apt and yum
both use binary deltas), and even the "deduplication" in borgbackup/restic.
The surprising implication: rsync never gained wide adoption for HOME
backup despite being ideal for it - most users use cloud sync services that
have worse deduplication and versioning. rsync remains dominant in the
domain where it was designed for: server-to-server backup by professionals.
The second surprise: the most common backup failure mode is not technical
but organizational - organizations have backup systems but lack restore
RUNBOOKS. When the actual disaster happens, no one knows the restore
commands, the encryption key is stored in the encrypted system, and the
restore takes 12 hours instead of 1 hour. The backup tooling is the easy
part; the operational procedure is where most backup strategies actually fail.

---

### Mastery Checklist

- [ ] Can use rsync for incremental sync and mirroring with --delete
- [ ] Can create tar archives and restore them correctly
- [ ] Understands 3-2-1 backup rule and why RAID is not a backup
- [ ] Knows the difference between rsync mirror and versioned snapshots
- [ ] Understands the importance of regular restore testing

---

### Think About This

1. A colleague claims "we're fine, we have rsync --delete running hourly
   to our backup server." Design a scenario where this backup strategy
   fails catastrophically (protects against disk failure but not another
   class of threat), and propose the minimum additional steps to make
   it a proper backup strategy that satisfies the 3-2-1 rule.

2. You need to design a backup strategy for a PostgreSQL database that:
   (a) allows point-in-time recovery to any second in the last 7 days,
   (b) has RPO of 0 (no committed transaction can be lost), (c) has
   offsite backup. Explain what PostgreSQL features (WAL archiving, base
   backup) make this possible and how rsync or borgbackup fits into the
   solution.

3. A monthly backup restore test fails: `borgbackup extract` succeeds
   but the application fails to start with "corrupted database file." The
   database backup was done by rsyncing the live PostgreSQL data directory
   while it was running. Explain why this doesn't work, what the correct
   approach is, and how to design a pre-backup hook that ensures a
   consistent database snapshot.

---

### Interview Deep-Dive

**Foundational:**
Q: Explain the rsync `--delete` option and when it is appropriate vs dangerous.
A: `rsync --delete` makes the destination an exact mirror of the source: it removes from the destination any files that no longer exist in the source. Without `--delete`: rsync only ADDS/UPDATES files - deleted source files persist in destination indefinitely. With `--delete`: destination after each sync = exact copy of source at that moment. Appropriate uses: (1) Disaster recovery mirror: you want a hot standby that exactly mirrors production. If production fails, failover to the mirror. (2) Web server content deployment: deploy new version = rsync with --delete ensures stale files are removed from web root. (3) Multi-region sync: keeping two clusters in sync for DR. Dangerous without versioning: if a file is accidentally deleted from source (rm -rf by mistake), `--delete` propagates the deletion to backup immediately. Next sync: deletion replicated. Both copies: gone. Mitigation: add `--backup` flag: `rsync -avz --delete --backup --backup-dir=/backup/$(date +%Y%m%d) /src/ /dst/`. This moves deleted/overwritten files to the backup directory instead of permanently removing them. Or better: use rsnapshot or borgbackup which maintain VERSION HISTORY. rsync with --delete is an excellent SYNCHRONIZATION tool but a dangerous BACKUP tool without additional version retention.

**Expert:**
Q: How would you design a zero-downtime database backup for PostgreSQL?
A: PostgreSQL raw data files on disk during a running database are NOT a consistent snapshot - pages are being written mid-transaction when rsync reads them. A raw file copy without coordination = corrupt backup that may not be restorable. Correct approaches, in order of preference: (1) WAL-based PITR (most flexible): Enable `archive_mode=on` and `archive_command` to copy WAL files to backup storage as they're generated. Nightly: run `pg_basebackup -Ft -z -Xs -P` (streaming base backup, doesn't block writes). Recovery: extract base backup, replay WAL files to any desired timestamp - exact point-in-time recovery. Tools: Barman, WAL-G, pgBackRest. (2) pg_dump (logical, always consistent): `pg_dump -Fc mydb > mydb.dump` - uses MVCC to take a consistent snapshot view (no blocking). Limitation: restoring 100GB dump takes hours; no point-in-time recovery between dumps. Good for: smaller databases, schema migrations, cross-version migrations. (3) LVM snapshot (filesystem-level): `pg_start_backup()` (prepares the database for snapshot), create LVM/ZFS snapshot of the data directory (instant, consistent), `pg_stop_backup()`. Then rsync/archive the frozen snapshot. This gives a consistent block-level snapshot. Limitation: requires LVM or ZFS on the database filesystem. The wrong approach: `rsync -avz /var/lib/postgresql/ backup:` while running. This produces an inconsistent backup with partially-written pages that will fail to start. The PostgreSQL manual is explicit: raw file copies require either pg_start/stop_backup() coordination or `pg_basebackup` which handles the WAL coordination internally.
