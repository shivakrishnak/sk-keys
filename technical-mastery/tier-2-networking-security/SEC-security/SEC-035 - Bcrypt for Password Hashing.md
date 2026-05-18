---
id: SEC-035
title: "Bcrypt for Password Hashing"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-014, SEC-016, SEC-020
used_by: SEC-099
related: SEC-014, SEC-016, SEC-020, SEC-099
tags:
  - security
  - password-hashing
  - bcrypt
  - argon2
  - key-derivation
  - authentication
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/sec/bcrypt-for-password-hashing/
---

⚡ TL;DR - For storing passwords, use bcrypt, Argon2, or scrypt.
NEVER use MD5, SHA-1, SHA-256, or any fast hash function.

**Why fast hashes are wrong for passwords:**
Fast hashes (SHA-256) can compute 10+ billion hashes per second
on a GPU. An attacker with a leaked database can try all common
passwords in minutes. Bcrypt is intentionally slow: ~100-400
ms per hash (depending on work factor). At 10 billion SHA-256/sec
vs ~100 bcrypt/sec on the same hardware: bcrypt is 100 million
times harder to brute-force.

**Bcrypt properties:**
- Adaptive: work factor (cost) can be increased as CPUs get faster
- Self-contained: bcrypt output includes the salt and work factor
  - no need to store salt separately
- Per-password random salt: prevents rainbow table attacks
- Industry standard: available in all major languages, battle-tested

**Modern choice: Argon2id over bcrypt for new systems.**
Argon2 won the Password Hashing Competition (2015), uses
memory-hardness (expensive for GPU/ASIC attacks), and has
explicit parameters (memory, time, parallelism). bcrypt remains
completely acceptable and widely deployed.

---

| #035 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Cryptography Basics, Authentication, Security Fundamentals | |
| **Used by:** | Authentication Best Practices | |
| **Related:** | Cryptography Basics, Authentication, Argon2/scrypt | |

---

### 🔥 The Problem This Solves

**THE CREDENTIAL BREACH PROBLEM:**
Databases get breached. This is a reality of production
security. The question is not "will my database be leaked?"
but "when it is leaked, what damage is done?" If passwords
are stored as plaintext: every user's password is immediately
known. If stored as fast hashes (MD5, SHA-256): GPU clusters
crack them in hours to days. If stored with bcrypt/Argon2:
cracking takes centuries for strong passwords, years for
weak ones. Proper password hashing converts an existential
security failure (all accounts compromised) into a limited
failure (weak passwords may eventually be cracked,
strong passwords are computationally infeasible to crack).

**WHY SALTING MATTERS:**
Without salt: two users with password "password123" have
identical hashes. An attacker who cracks one cracks all.
Rainbow tables (precomputed hash→password mappings) reduce
cracking to table lookups. With unique random salt per
password: even identical passwords produce different hashes.
Rainbow tables are useless. Each password must be cracked
individually. Bcrypt generates the salt automatically and
stores it in the output - developers cannot forget to salt.

---

### 📘 Textbook Definition

**Password Hashing:** A one-way transformation of a password
into a fixed-length hash value designed to make reversing
the transformation computationally infeasible.

**Password Hashing Function vs. Cryptographic Hash Function:**
SHA-256 is designed to be FAST (needed for digital signatures,
HMAC, checksums). Password hashing functions are designed
to be SLOW (needed to make brute-force attacks expensive).
These are completely different design goals.

**Bcrypt:**
A password hashing function designed in 1999 by Niels Provos
and David Mazieres. Based on Blowfish cipher. Key features:

- **Work factor (cost):** An integer (typically 10-14) that
  controls how many iterations are performed. Work factor 10 =
  2^10 = 1024 iterations. Increasing by 1 doubles the time.
  Allows algorithm to remain slow as hardware improves.

- **Embedded salt:** Bcrypt generates a random 128-bit salt
  for each password. The salt is embedded in the output hash.
  Output format: `$2b$12$[22-char-salt][31-char-hash]`
  where 12 is the work factor. No separate salt storage needed.

- **Output:** 60-character string starting with `$2b$` (or `$2a$`).
  This string contains everything needed to verify a password.

**Work factor selection (2024 guidelines):**
- Minimum: 10 (OWASP recommendation)
- Interactive (login): 10-12 (100-400ms)
- High-value (admin, financial): 12-14 (400ms-1.6s)
- Never below 10. Adjust upward as hardware improves.
- Target ~300ms verification time as a practical benchmark.

**Argon2 (recommended for new systems):**
Winner of Password Hashing Competition (2015).
Three variants: Argon2d (GPU resistance), Argon2i (side-channel
resistance), Argon2id (recommended: both properties).
Parameters: memory cost (KB), time cost (iterations),
parallelism. Memory-hardness makes GPU/ASIC attacks expensive.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Password hashing is using a deliberately slow algorithm
(bcrypt/Argon2) instead of a fast hash (SHA-256) so that
an attacker who steals the database still needs billions of
years to reverse-engineer all the passwords.

**One analogy:**
> A fast hash is like a combination lock with 1,000 combinations -
> someone can try all combinations in minutes. Bcrypt is like
> a vault lock that takes 300ms to test each combination.
> With 1 million possible passwords: SHA-256 takes 0.1ms to
> test all (total: 100 seconds). Bcrypt at 300ms: 300,000 seconds
> = 3.5 days. For 1 billion passwords (GPU attack): SHA-256
> = 1 second. Bcrypt = 95 years. The slowness IS the security feature.

---

### 🔩 First Principles Explanation

**Why adaptive hashing defeats hardware advances:**

```
FAST HASH ATTACK MATH:

SHA-256 speed (2024 hardware):
  Consumer GPU: ~10 billion hashes/second
  Hash farm (8x 4090): ~80 billion hashes/second
  
  Password: 8 lowercase letters (26^8 = 208 billion combos)
  Time to brute-force: 208B / 80B = 2.6 seconds
  
  8 chars upper+lower+digit+symbol: 94^8 = 6.1 trillion
  Time: 6.1T / 80B = 76 seconds
  
  Conclusion: short passwords cracked in under 2 minutes.
  Common password wordlists (millions of entries): seconds.
  Pwned Passwords list (847M): seconds.

BCRYPT ATTACK MATH:

Bcrypt work factor 12 speed (2024 hardware):
  Consumer GPU: ~200-500 hashes/second
  Hash farm (8x 4090): ~4000 hashes/second
  
  8 lowercase letters (208B combos):
  Time: 208B / 4000 = 52 million seconds = ~1.6 years
  
  Bcrypt work factor 14:
  Factor 14 = factor 12 * 4 (two increments, doubles each)
  Speed: ~1000 hashes/second (hash farm)
  8 lowercase: 208B / 1000 = 208M seconds = 6.6 years
  
  For a STRONG password (16+ chars, mixed): computationally
  infeasible (10^20+ combinations at 300ms/hash).

WHY ADAPTIVE MATTERS:

2000: Work factor 10 → 100ms (acceptable)
2010: Work factor 10 → 10ms (CPUs improved)
      Solution: increase to work factor 12 → 100ms
2020: Work factor 12 → 30ms (GPUs much faster)
      Solution: increase to work factor 14 → 100ms
2030: Work factor 14 → ??? (future hardware)
      Solution: increase work factor again

With fast hashes (SHA-256): no work factor to increase.
As hardware improves, security continuously degrades.
Only mitigation: add salt (prevents rainbow tables) but
doesn't help with raw speed attacks.

HOW THE BCRYPT OUTPUT IS STRUCTURED:
$2b$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jWMUW
|  |  |   |22 chars |      |31 chars|
|  |  |   |  salt    |      |  hash  |
|  |  |   \- The random 22-char salt (encoded)
|  |  \----- Work factor: 12 (= 2^12 = 4096 iterations)
|  \-------- Version: 2b (preferred), 2a (legacy)
\----------- BCrypt identifier

Everything needed to verify is in this single string.
Verification: bcrypt.checkpw(password, stored_hash)
  - Library extracts salt from stored_hash
  - Library extracts work factor from stored_hash
  - Library computes hash with same salt and work factor
  - Compares result to stored_hash in constant time
```

---

### 🧪 Thought Experiment

**SCENARIO: Migrating existing MD5-hashed passwords to bcrypt**

```
PROBLEM: Legacy application stores passwords as MD5.
  Database leaked. All user passwords are at risk.
  
NAIVE APPROACH (wrong):
  Step 1: Hash all existing MD5 hashes with bcrypt
  bcrypt(md5_hash) where md5_hash = MD5(password)
  
  Problem: now verifying requires md5(submitted) then bcrypt-check.
  But MD5 of password is weak: if attacker has the MD5 hash,
  they can crack it without ever touching bcrypt.
  The md5 layer is the weak link.

BETTER APPROACH: Gradual migration on login
  
  Phase 1: Add new column 'password_hash' to users table.
    Old passwords in 'password_md5' column.
    New users: bcrypt goes in 'password_hash'.
    Old users: bcrypt column is NULL.
  
  Phase 2: On EVERY successful login:
    user = get_user(username)
    submitted_password = request.password
    
    if user.password_hash:  # Already migrated
      if bcrypt.checkpw(submitted_password, user.password_hash):
        login_success()
    else:  # Still on MD5
      if md5(submitted_password) == user.password_md5:
        # Login OK - migrate NOW
        new_hash = bcrypt.hashpw(submitted_password, bcrypt.gensalt(12))
        user.password_hash = new_hash
        user.password_md5 = None  # Remove MD5 hash
        db.save(user)
        login_success()
  
  Phase 3: After 6-12 months: require password reset
    for users who never logged in (still NULL password_hash).
    Lock their accounts until they reset via email.
  
  Phase 4: Drop password_md5 column.
  
  OUTCOME: Active users get migrated transparently.
    Inactive users have password reset forced.
    No MD5 hashes remain after Phase 3.
    No user ever notices the migration.
```

---

### 🧠 Mental Model / Analogy

> Password hashing is like a combination padlock that takes
> 300ms per combination attempt - by design. The lock is on
> your data. A thief who steals the lock (database) can
> try combinations, but at 300ms each, even 1 billion attempts
> takes 9.5 years. Meanwhile, a fast hash is a combination
> lock that opens in 0.0001ms per attempt: 1 billion combinations
> in 100 seconds. The lock material (algorithm) matters as
> much as the number of combinations (password complexity).
> Bcrypt's slowness is the feature. Upgrading CPUs and GPUs
> is matched by increasing the work factor (adding more
> tumblers to the lock), keeping the attack cost constant
> over time.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When storing passwords: never store the actual password.
Never use MD5 or SHA-256 (these are too fast - hackers can
try millions per second). Use bcrypt or Argon2 instead.
These are SLOW by design - taking ~300ms per verification.
That makes them safe: even if the database is stolen,
cracking each password takes too long to be practical.

**Level 2 - How to use it (junior developer):**
Python: `pip install bcrypt`. Hash: `bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))`. Verify: `bcrypt.checkpw(password.encode(), stored_hash)`. JavaScript/Node: `npm install bcrypt`. Java: Spring Security has `BCryptPasswordEncoder`. Never compare directly - always use the library's checkpw/verify function (constant-time comparison). Store the 60-character bcrypt output in the database as a varchar(60).

**Level 3 - How it works (mid-level engineer):**
Bcrypt applies 2^work_factor rounds of Blowfish-based key
expansion. The work factor is logarithmic: factor 12 takes
4x longer than factor 10. Salt prevents rainbow tables and
ensures different hashes for identical passwords. The `$2b$`
prefix distinguishes bcrypt from other algorithms stored in
the same column. The verify function is safe to call even
for timing attacks because bcrypt is already slow - the
natural slowness eclipses any timing difference from
character-by-character comparison (but still use the library's
verify function, not `==`).

**Level 4 - Why it was designed this way (senior/staff):**
Bcrypt was designed in 1999 specifically for the problem
that CPU performance improvements would make future hash
attacks faster. The work factor abstraction was the key
insight: by making the number of rounds a parameter stored
in the hash output, the same password hash format remains
usable across hardware generations by increasing the work
factor in new hashes while still verifying old hashes
(old hashes store their own work factor). This "self-describing"
output format means: no schema migration needed to increase
security. New user registrations use higher work factors;
old hashes remain verifiable until users change their passwords.

**Level 5 - Mastery (distinguished engineer):**
Argon2 improves on bcrypt by adding memory-hardness.
BCrypt is limited to 4KB of memory usage by design.
Modern attacks use custom ASICs and FPGAs that reduce
memory to silicon area - cheap at 4KB. Argon2 allows
specifying memory cost in megabytes (typically 64MB-1GB).
An Argon2 hash requiring 512MB of memory means an ASIC
attack needs 512MB of RAM per parallel cracking attempt.
At current DRAM prices, parallelizing 1 million simultaneous
Argon2 guesses requires 512TB of RAM - economically infeasible.
BCrypt's lack of memory-hardness is its primary weakness
compared to Argon2. For new systems: Argon2id with
`m=65536, t=3, p=4` is the recommended baseline (OWASP).
For systems already using bcrypt: no urgent need to migrate
if work factor is adequate (>=10); bcrypt remains strong
against CPU attacks.

---

### ⚙️ How It Works (Mechanism)

**Bcrypt algorithm overview:**

```
BCRYPT ALGORITHM (simplified):

Input: password (up to 72 bytes), salt (16 bytes), cost

Step 1: Generate Blowfish subkeys from password + salt
  P-array: 18 32-bit subkeys (P1-P18)
  S-boxes: four 256-entry S-boxes
  Initialize with pi digits, then modify with password + salt:
    For i = 1 to 2^cost:  ← This is the "cost" loop
      ExBlowfishSetup(P, S, password)
      ExBlowfishSetup(P, S, salt)
  
  This setup step is the expensive part. 2^10 = 1024 rounds
  at cost 10. 2^12 = 4096 rounds at cost 12.

Step 2: Encrypt a 192-bit constant 64 times
  Output: the bcrypt hash (192 bits = 24 bytes)

Step 3: Encode and combine with metadata
  Format: $2b$COST$SALT22HASH31
  Total: 60 characters

VERIFICATION:
  Input: submitted_password, stored_bcrypt_string
  Parse stored_bcrypt_string → extract cost, salt
  Compute: bcrypt(submitted_password, extracted_salt, cost)
  Compare: computed_hash == stored_hash (constant-time)
  
  CRITICAL: The SAME salt and cost are used for verification.
  This is why bcrypt is self-contained: all parameters
  needed for verification are embedded in the stored string.
  
  No need to store salt, cost, or version separately.
  One column, one value, complete verification capability.

CONSTANT-TIME COMPARISON:
  bcrypt.checkpw() in Python uses hmac.compare_digest internally
  This prevents timing attacks where an attacker measures
  response time to determine how many characters match.
  Direct == comparison leaks timing info; compare_digest doesn't.
```

---

### 💻 Code Example

**Password hashing in Python and Node.js:**

```python
# Python with bcrypt library
import bcrypt

# BAD: Fast hash - NEVER use for passwords
import hashlib
bad_hash = hashlib.sha256(b"password123").hexdigest()
# Result: b4bcae... - cracks in 0.01ms with GPU

# BAD: MD5 - extremely dangerous, no salt
md5_hash = hashlib.md5(b"password123").hexdigest()
# 482c81... - rainbow tables crack instantly

# GOOD: bcrypt with appropriate work factor
def hash_password(plain_password: str) -> bytes:
    """Hash password with bcrypt. Returns 60-byte hash."""
    password_bytes = plain_password.encode('utf-8')
    # gensalt(12) = work factor 12 = ~400ms on modern hardware
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed  # Store this in database (60 bytes)

def verify_password(plain_password: str, stored_hash: bytes) -> bool:
    """
    Verify password against bcrypt hash.
    Uses constant-time comparison internally.
    """
    password_bytes = plain_password.encode('utf-8')
    # checkpw extracts salt from stored_hash, recomputes, compares
    return bcrypt.checkpw(password_bytes, stored_hash)

# Usage:
hashed = hash_password("user_password_here")
# hashed: b'$2b$12$...'  (60 bytes, store in varchar(60))

is_valid = verify_password("user_password_here", hashed)
# True

is_invalid = verify_password("wrong_password", hashed)
# False

# ARGON2 (preferred for new systems, Python):
# pip install argon2-cffi
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,      # iterations
    memory_cost=65536,  # 64MB RAM
    parallelism=4,    # 4 parallel threads
    hash_len=32,      # 32-byte hash output
    salt_len=16,      # 16-byte salt
)

def hash_password_argon2(plain_password: str) -> str:
    return ph.hash(plain_password)

def verify_password_argon2(plain_password: str,
                            stored_hash: str) -> bool:
    try:
        ph.verify(stored_hash, plain_password)
        return True
    except VerifyMismatchError:
        return False

# Rehash detection (when parameters change):
def login_and_upgrade(plain_password: str,
                       stored_hash: str,
                       user_id: int) -> bool:
    if verify_password_argon2(plain_password, stored_hash):
        if ph.check_needs_rehash(stored_hash):
            # Parameters upgraded: rehash and save
            new_hash = hash_password_argon2(plain_password)
            update_user_password_hash(user_id, new_hash)
        return True
    return False
```

---

### ⚖️ Comparison Table

| Algorithm | Speed | Memory Hard | GPU Resistance | Recommendation |
|:---|:---|:---|:---|:---|
| **MD5** | Extremely fast | No | Very poor | NEVER for passwords |
| **SHA-256** | Very fast | No | Poor | NEVER for passwords |
| **SHA-512** | Fast | No | Poor | NEVER for passwords |
| **bcrypt** | Slow (adjustable) | No (4KB) | Medium | Good for existing systems |
| **scrypt** | Slow (adjustable) | Yes | Better | Acceptable |
| **Argon2id** | Slow (adjustable) | Yes | Best | Preferred for new systems |
| **PBKDF2** | Slow (adjustable) | No | Medium | FIPS-compliant environments |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Adding salt makes SHA-256 secure for passwords | Salting prevents rainbow tables and identical-hash detection. It does NOT slow down the hash computation. SHA-256 with salt is still ~10 billion operations per second on GPU hardware. Salt solves ONE weakness (precomputed tables) but not the fundamental problem (speed). You must use an intentionally slow function (bcrypt, Argon2) in addition to salting. In fact, bcrypt handles salting automatically - you don't need to add a salt yourself. |
| Bcrypt with a high work factor makes any password secure | Work factor slows down cracking but password entropy still matters. bcrypt(work=14, password="abc") is still vulnerable if the attacker knows you use short passwords. At work factor 14 and 10,000 guesses/second: a 3-character lowercase password (17,576 combos) takes 1.8 seconds to fully exhaust. Strong work factor protects strong passwords much longer; it doesn't make weak passwords immune. Pair high work factors with password strength requirements (minimum length, not common). |

---

### 🚨 Failure Modes & Diagnosis

**Common password storage errors:**

```
ERROR 1: Truncation at 72 bytes (bcrypt limitation)
  Bcrypt accepts at most 72 bytes of password input.
  Passwords longer than 72 bytes are SILENTLY truncated.
  "password123" + 100 chars = same hash as "password123"
  
  Attack: if attacker guesses first 72 chars (which user typed
    as 73+), they can log in as the user.
  
  Fix for Argon2: no truncation issue.
  Fix for bcrypt: pre-hash with SHA-256 before bcrypt:
    bcrypt(sha256(password), salt)
    SHA-256 output is 32 bytes (< 72): no truncation.
    But: introduces complexity. For new systems, just use Argon2.
  
  Practical: 72 bytes is sufficient for passwords up to 72
    ASCII chars. Only affects very long passwords.

ERROR 2: Wrong encoding (bytes vs string)
  Python: bcrypt requires bytes, not str.
    Wrong: bcrypt.hashpw(password, salt) where password is str
    Error: TypeError or silent encoding issues
    Right: bcrypt.hashpw(password.encode('utf-8'), salt)
  
  Symptom: checkpw() returns False even with correct password.

ERROR 3: Work factor too low
  Work factor 4 or 6: < 1ms per hash. Provides no protection.
  
  Testing: bcrypt.gensalt(4) is sometimes used in tests for speed.
  DON'T use in production.
  
  Audit: query database for stored bcrypt hashes and check
    work factor in the $2b$XX$ prefix. All should be >= 10.

ERROR 4: Hashing after the fact (timing issues)
  Login: retrieve user, compute bcrypt, compare.
  If user doesn't exist: return "invalid" immediately (fast).
  If user exists: compute bcrypt (slow ~300ms), then return "invalid".
  
  Timing attack: attacker can determine if username exists
    by measuring response time.
  Fix: always compute bcrypt, even for non-existent users:
    def login(username, password):
      user = get_user(username)
      # Compute bcrypt ALWAYS (even for fake user) to normalize timing
      dummy_hash = get_dummy_hash()  # Precomputed at startup
      check_hash = user.password_hash if user else dummy_hash
      valid = bcrypt.checkpw(password.encode(), check_hash)
      if valid and user:
        return login_success(user)
      return login_failure()
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Cryptography Basics` - hash functions vs encryption
- `Authentication Fundamentals` - why passwords need protection
- `Security Headers` - cookies, session handling

**Builds on this:**
- `Authentication Best Practices` - bcrypt as part of auth design
- `Cryptography` - deeper dive into hash function design

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ NEVER USE    │ MD5, SHA-1, SHA-256, SHA-512 for passwords│
│              │ Fast hashes = crackable in seconds on GPU  │
├──────────────┼───────────────────────────────────────────┤
│ USE          │ bcrypt (work factor 12+) for existing code │
│              │ Argon2id (m=65536, t=3, p=4) for new code  │
├──────────────┼───────────────────────────────────────────┤
│ WORK FACTOR  │ Min: 10 (OWASP). Target: ~300ms per verify │
│              │ Check: extract $2b$XX$ from stored hashes  │
├──────────────┼───────────────────────────────────────────┤
│ VERIFY       │ bcrypt.checkpw() - uses constant-time      │
│              │ NEVER: stored_hash == compute_hash(input)  │
├──────────────┼───────────────────────────────────────────┤
│ SALT         │ Automatic (embedded in bcrypt output)      │
│              │ 60-char stored value contains everything   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Algorithm selection must match the problem constraints."
Fast hashes (SHA-256) are designed for performance: they're
used in digital signatures, TLS, checksums, and HMAC because
speed is desirable in those contexts. Using SHA-256 for
password hashing is choosing the wrong tool for the job -
not a mistake in SHA-256, but a mismatch between the algorithm's
design goals (fast) and password storage requirements (slow).
This principle generalizes: always ask "what properties does
this algorithm optimize for, and do those properties match
my requirements?" Encryption optimizes for reversibility
(wrong for passwords). Fast hashes optimize for throughput
(wrong for passwords). Adaptive slow hashes optimize for
tunable brute-force resistance (correct for passwords).

---

### 💡 The Surprising Truth

Bcrypt limits passwords to 72 bytes (72 ASCII characters).
Any characters beyond 72 are silently ignored. This means
"correcthorsebatterystaple" + 100 random characters has
the same bcrypt hash as "correcthorsebatterystaple" + 100
DIFFERENT random characters. The security implication: if
an attacker knows the first 72 characters of a user's password,
they can authenticate as that user regardless of the remaining
characters. In practice: 72 bytes exceeds most real password
lengths. But high-security systems that require passphrases
longer than 72 characters should use Argon2 (no truncation
limit) or pre-hash with SHA-256 before bcrypt (SHA-256
output is 32 bytes, well under the limit). This is one
of several reasons Argon2 is preferred for new systems.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the fundamental difference between fast cryptographic
   hashes (SHA-256) and password hashing functions (bcrypt/Argon2)
   and WHY the difference matters under GPU attack conditions.
2. **IMPLEMENT** bcrypt password hashing in your primary language
   with correct work factor, bytes encoding, and constant-time verification.
3. **AUDIT** a database schema and identify password hashes with
   insufficient work factors by inspecting the stored hash format.
4. **MIGRATE** an existing application from MD5/SHA to bcrypt using
   the gradual on-login migration pattern.

---

### 🎯 Interview Deep-Dive

**Q: How should passwords be stored? Why can't you just use SHA-256?**

*Why they ask:* Tests whether the candidate understands the
difference between cryptographic hash functions and password
hashing functions - a fundamental security knowledge gap.

*Strong answer includes:*
- SHA-256 is designed to be fast. ~10 billion SHA-256 per second
  on a consumer GPU. An attacker with a breached database can
  try all common passwords (top 10 billion) in ~1 second.
- Bcrypt/Argon2 are designed to be slow. ~100-500 bcrypt per second
  on the same GPU. Same 10B passwords = 20-100 million seconds =
  years to centuries. The slowness is the feature.
- Bcrypt adds automatic salting: random 16-byte salt per password.
  No two identical passwords produce the same hash. Rainbow tables
  (precomputed SHA-256 → password) are useless against bcrypt.
- Work factor: logarithmic parameter. Increasing by 1 doubles time.
  As hardware improves: increase work factor to maintain attack cost.
  SHA-256 has no equivalent adjustment mechanism.
- Recommendation: bcrypt (rounds=12) for existing systems,
  Argon2id (m=65536, t=3, p=4) for new systems.
- Never store plaintext, never use MD5/SHA for passwords.
- OWASP Password Storage Cheat Sheet covers the complete guidance.