---
id: SEC-009
title: "Password Storage Anti-Pattern"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-002, SEC-008
used_by: SEC-010, SEC-037, SEC-038
related: SEC-001, SEC-002, SEC-008, SEC-010, SEC-037, SEC-038, SEC-021
tags:
  - security
  - passwords
  - hashing
  - bcrypt
  - argon2
  - credential-security
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/sec/password-storage-anti-pattern/
---

⚡ TL;DR - Passwords must NEVER be stored in plain text or
with reversible encryption. They must be hashed with a
slow, salted hashing algorithm specifically designed for
passwords: bcrypt, Argon2id, or scrypt. Regular hashing
algorithms (SHA-256, MD5) are designed to be FAST - which
is exactly wrong for passwords (makes brute-force feasible).
bcrypt with cost factor 12 makes each hash take ~300ms on
modern hardware. A GPU that can compute 10 billion SHA-256
hashes/second can compute only ~30,000 bcrypt/second.
Password cracking time: SHA-256 without salt = seconds for
common passwords. bcrypt cost 12 = 9+ years for 8-char
random passwords against modern GPU rigs. Salt prevents
rainbow table attacks and ensures duplicate passwords have
different hashes. This is not theoretical: LinkedIn (2012,
117M SHA-1 passwords cracked), RockYou (2009, 32M plain
text), Adobe (2013, 153M poorly encrypted) are real breaches
where storage anti-patterns led to mass credential exposure.

---

| #009 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, CIA Triad, AuthN/AuthZ/Audit | |
| **Used by:** | Hashing vs Encryption vs Encoding, Authentication Decision Tree | |
| **Related:** | CIA Triad, Authentication, Hashing vs Encryption, Bcrypt, OWASP A07 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (LinkedIn 2012):**
LinkedIn stored 6.5 million password hashes using SHA-1
without salt. An attacker breached the database. Published
the hashes. Within 3 days: 90% of the 6.5M hashes cracked
using precomputed rainbow tables. Because SHA-1 is fast
(1 billion hashes/second on a GPU): brute force was
trivial. Because no salt: identical passwords produced
identical hashes (all "password123" accounts cracked at
once). Result: 6.5M LinkedIn users' passwords exposed.
Most users reused those passwords elsewhere. Credential
stuffing attacks used LinkedIn credentials to access Gmail,
banking, and other services for years afterward.
In 2016, it emerged the full breach was 117M accounts.
Total cost (2016 class action settlement): $1.25M.

---

### 📘 Textbook Definition

**The Password Storage Problem:**
Servers must verify passwords at login. This requires
being able to compare the user's submitted password to
the stored value. Two options:
(A) Store the password in a form that allows comparison
    (plain text or reversible encryption) - catastrophic
    if database is breached.
(B) Store a one-way transformation of the password (hash)
    and apply the same transformation to the submitted
    password to compare - breach-resistant.

Option B is correct. The key properties required:

**Salt:** A random value added to the password before
hashing. Different salt for every user. Prevents:
(1) Rainbow table attacks (precomputed hash-to-password
tables cannot account for per-user salts), (2) Identical
passwords producing identical hashes (attacker cannot
infer that 1,000 users have the same weak password).

**Slowness (Cost Factor):** Password hashing algorithms
are intentionally slow to make brute force expensive.
bcrypt (1999): cost factor 10-12 (2^10 to 2^12 iterations).
At cost 12: ~300ms per hash on modern hardware.
Argon2id (2015 Password Hashing Competition winner): memory-
hard (requires large memory allocation, defeats GPU-based
cracking since GPUs have limited memory per core). Preferred
for new systems.

**Modern Standard (2024):**
- New systems: Argon2id (m=65536 KB, t=3 iterations, p=4)
- Existing bcrypt systems: bcrypt cost 12 (or 13 on fast hardware)
- Legacy systems still on MD5/SHA: MUST migrate immediately

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Passwords must be stored as bcrypt or Argon2id hashes with
per-user salt - fast hashes (SHA-256, MD5) make GPU cracking
trivial, plain text or reversible encryption = catastrophe
when the database is inevitably breached.

**One analogy:**
> Storing passwords with bcrypt is like a locksmith who
> can verify that a key fits a lock without keeping a
> copy of the key. The lock (hash) can be checked with
> the original key (password), but the lock alone cannot
> be reverse-engineered into the key. A safe that stores
> the key itself (plain text) - when the safe is stolen,
> all keys are compromised. A safe that stores only the
> lock (bcrypt hash) - when stolen, the attacker still
> has to manufacture each key from scratch (brute force),
> which takes years per key.

---

### 🔩 First Principles Explanation

**The mathematics of hash cracking:**

```
SHA-256 performance (NVIDIA RTX 4090, 2023):
  ~82 billion SHA-256 hashes per second

bcrypt cost 12 performance (same hardware):
  ~30,000 bcrypt hashes per second

Ratio: SHA-256 is 2,700,000x faster than bcrypt cost 12.

CRACKING A DATABASE OF 10 MILLION PASSWORDS:

Scenario 1: SHA-256 without salt
  Attacker precomputes rainbow table:
    - Top 1 billion passwords hashed with SHA-256
    - Lookup: O(1) per hash
    - Time to crack all 10M passwords = minutes
    - Cost: cloud compute for table generation = ~$100

Scenario 2: SHA-256 with salt (per-user random salt)
  Rainbow tables don't work (unique salt per user)
  Must brute force each password individually
  Time per password: 1 second ÷ 82 billion/sec =
    0.000000012 seconds per attempt
  8-char alphanumeric space: 62^8 = 218 trillion combos
  Time to crack one 8-char random password:
    218T ÷ 82B = 2,658 seconds = 44 minutes
  For 10M passwords: 10M × 44 min / (number of GPUs)
    With 100 GPUs: 10M × 44min / 100 = 73 hours
  CONCLUSION: Fast but feasible for common passwords.
  Dictionary + rules attacks crack 80% in hours.

Scenario 3: bcrypt cost 12 with salt
  30,000 bcrypt/second on RTX 4090
  8-char alphanumeric: 218 trillion combos
  Time per password: 218T ÷ 30K = 7.3 billion seconds
    = 231 years (one GPU)
  With 100 GPUs: 2.3 years per random 8-char password
  Common passwords (still crack first):
    "password": ~0.03 seconds (in dictionary)
    "P@ssw0rd1": ~few minutes (common mutation)
    Random 8+ char: ~years
  CONCLUSION: Common passwords still crack quickly.
  Random/complex passwords become impractical to crack.

PRACTICAL ADVICE:
  bcrypt/Argon2 does NOT protect weak passwords (dictionary).
  It does protect all strong passwords completely.
  Combined: require strong passwords + use bcrypt/Argon2.
  Also: rate-limit login attempts + implement MFA.
```

---

### 🧪 Thought Experiment

**SCENARIO: Your database is stolen. What gets exposed?**

```
COMPANY: 1 million user accounts stolen.

CASE A: Plain text passwords
  Attacker immediately has: all 1M passwords.
  Attacker action: credential stuffing against Gmail, banks,
    other services (assuming password reuse).
  Users affected: all 1M, plus all their accounts elsewhere.
  Time to crack: 0 seconds. Instant.
  Notification required: YES (all users, immediately)
  Remediation: force password reset for all 1M users

CASE B: MD5 without salt
  Attacker has 1M MD5 hashes.
  CrackStation dictionary: 15 billion MD5 entries precomputed.
  Time to crack: run entire DB against lookup table.
    80% of users with common passwords: <1 minute.
    Remaining 20%: GPU brute force, hours for 8-char or less.
  Users affected: ~800,000 (80% have common passwords)
  Notification required: YES (all users - can't distinguish)

CASE C: bcrypt cost 12 with random salt
  Attacker has 1M bcrypt hashes.
  No rainbow table possible (per-user salt).
  Must brute force each hash individually.
  Time to crack common passwords (top 10,000 dictionary):
    10,000 passwords × 1M users × 33µsec = 333 seconds
    → all users with "password123" type passwords cracked
  Time to crack 8-char random passwords:
    231 years per user with one GPU.
    Even with 10,000 GPUs: 8.4 years per user.
  Users with weak passwords: still cracked quickly.
  Users with strong passwords: effectively protected.
  Notification: still required (breach of database)
  Practical outcome: attacker focuses on the weak passwords
    (still valuable for credential stuffing), abandons
    the strong ones (not worth the compute cost).

LESSON:
  bcrypt does not make a breach consequence-free.
  It does make strong passwords effectively uncrackable.
  Defense against breach: bcrypt + mandatory strong passwords
    + MFA (so cracked passwords cannot be used alone).
```

---

### 🧠 Mental Model / Analogy

> Password hashing is like a one-way hash function in
> mathematics: easy to compute in one direction,
> computationally infeasible to reverse. The "cost factor"
> in bcrypt is like adding deliberate complexity to the
> hash function: instead of O(1) computation, it requires
> O(2^cost) computations. For the legitimate server (verifying
> one password at login): cost 12 = 300ms = acceptable.
> For an attacker trying to crack 1 million passwords:
> 300ms × 1M = 3.5 days PER password (single GPU). The
> asymmetry: login verification costs the server 300ms.
> Password cracking costs the attacker years. This asymmetry
> is the security property bcrypt was designed to provide.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Never store passwords directly. Instead, store a scrambled
version (a "hash") that cannot be unscrambled. When a user
logs in, scramble what they typed and compare the scrambled
versions. Use special slow scrambling that makes guessing
very hard.

**Level 2 - How to use it (junior developer):**
Use bcrypt (Java: Spring Security's BCryptPasswordEncoder,
Python: passlib's bcrypt) with cost factor 12. Never use
MD5 or SHA-256 for passwords. Never store plain text. Never
build your own password storage: use the library. The library
handles salt automatically.

**Level 3 - How it works (mid-level engineer):**
bcrypt stores: version + cost factor + 22-char salt + 31-char
hash in a single string ("$2b$12$[salt][hash]"). The full
bcrypt output contains everything needed to verify: algorithm,
cost, salt, hash. Salt is randomly generated at hash creation.
Verification: extract salt from stored hash, apply same
algorithm with same cost and that salt to submitted password,
compare hashes. If matching: password correct.

**Level 4 - Why it was designed this way (senior/staff):**
bcrypt was designed by Niels Provos and David Mazieres
(1999) specifically because they saw MD5 being used for
password storage and recognized it was being misused (MD5
designed for message integrity, not password storage).
Their key insight: the cost of legitimate verification is
linear (you hash once per login), while the cost of
cracking is proportional to the hash rate (you hash billions
of times). Making the hash deliberately slow shifts the
economic calculation: legitimate operations cost milliseconds,
malicious cracking costs years. Argon2id (2015) adds
memory-hardness: the algorithm requires large memory
allocations per hash. Modern GPUs have thousands of cores
but limited memory per core. Memory-hard algorithms
cannot be efficiently parallelized on GPUs - the memory
bottleneck limits parallelism. Argon2id is now the recommended
choice for new systems.

**Level 5 - Mastery (distinguished engineer):**
Password storage at scale introduces operational challenges.
Cost factor tuning: as hardware gets faster, cost factor
must be increased to maintain cracking resistance. Benchmark
your production hardware: target 100-300ms per hash for
bcrypt, adjust cost factor accordingly. Migration: when
upgrading cost factor (from 10 to 12), existing hashes must
be re-hashed. Strategy: on next successful login, re-hash
with new cost factor and store. Background migration: batch
process inactive accounts. Rollover period: 3-6 months until
all active accounts migrated. For very large systems (100M+
users): argon2id with pepper (application-level secret key
XORed with hash before storage) adds a second layer: even
if the database is stolen, the hash cannot be cracked without
also stealing the application secret. Separation of concerns:
database breach alone is insufficient.

---

### ⚙️ How It Works (Mechanism)

**bcrypt algorithm internals:**

```
INPUT: password "MyP@ssw0rd!", cost_factor=12

1. GENERATE SALT (22 base64 chars = 128 bits of entropy)
   salt = "eIAqH8bPT9c8FW8EMIX2Au"
   (Generated with CSPRNG - cryptographically secure RNG)

2. EXPAND KEY (Eksblowfish key setup)
   - Initialize Blowfish cipher with password + salt
   - Execute 2^12 (4,096) iterations of key expansion
   - Each iteration: expand with password, then with salt
   - This loop is the "cost": 2^12 = 4,096 Blowfish operations
   - Result: expanded key state (P-boxes and S-boxes)

3. ENCRYPT (ECB mode with fixed plaintext)
   - Encrypt the 64-bit constant "OrpheanBeholderScryDoubt"
   - 64 times
   - Using the expanded key from step 2

4. OUTPUT FORMAT
   "$2b$12$eIAqH8bPT9c8FW8EMIX2AuXXXXXXXXXXXXXXXXXXXXX"
    [ver][cost][      22-char salt      ][31-char hash]
   Version: 2b (current bcrypt version)
   Cost: 12 (2^12 = 4,096 iterations)
   Salt: embedded in output (no need to store separately)

VERIFICATION:
  Take stored hash → extract salt + cost
  Apply bcrypt with same salt + cost to input password
  Compare 31-char hash portion
  Match → password correct (in O(time of one hash))
```

---

### 💻 Code Example

**Bad to Good - all common password storage mistakes:**

```python
import os, hashlib, bcrypt
from argon2 import PasswordHasher  # argon2-cffi library

# BAD #1: Plain text storage
class UserServiceBad1:
    def create_user(self, username, password):
        # NEVER store passwords in plain text
        self.db.save(username=username, password=password)

# BAD #2: MD5 without salt (LinkedIn 2012 pattern)
class UserServiceBad2:
    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()
    # Single GPU cracks common passwords in seconds.
    # Rainbow tables crack the whole database.

# BAD #3: SHA-256 with static (application-wide) salt
STATIC_SALT = "my_app_salt_2024"  # Same for all users!
class UserServiceBad3:
    def hash_password(self, password):
        # Per-user salt required. Application-wide salt
        # doesn't prevent: if two users have same password,
        # their hashes are identical → mass cracking of
        # all instances of common passwords at once.
        return hashlib.sha256(
            (STATIC_SALT + password).encode()
        ).hexdigest()

# GOOD: bcrypt with automatic per-user salt
class UserServiceGood_bcrypt:
    COST_FACTOR = 12  # ~300ms on modern hardware. Benchmark and adjust.

    def hash_password(self, password: str) -> str:
        # bcrypt auto-generates random per-user salt
        # Returns a single string with version+cost+salt+hash
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=self.COST_FACTOR)
        )
        return hashed.decode("utf-8")

    def verify_password(self, password: str,
                        stored_hash: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )

# BEST: Argon2id (memory-hard, 2015 PHC winner)
class UserServiceBest_argon2:
    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=3,        # 3 iterations
            memory_cost=65536,  # 64 MB memory required
            parallelism=4,      # 4 parallel threads
            hash_len=32,        # 256-bit hash
            salt_len=16         # 128-bit salt (auto-generated)
        )

    def hash_password(self, password: str) -> str:
        return self.ph.hash(password)  # salt auto-generated

    def verify_password(self, password: str,
                        stored_hash: str) -> bool:
        try:
            return self.ph.verify(stored_hash, password)
        except Exception:
            return False
```

---

### ⚖️ Comparison Table

| Algorithm | Designed For | GPU Speed (RTX 4090) | 8-char Random Crack Time | Salt | Use Today? |
|:---|:---|:---|:---|:---|:---|
| **MD5** | Checksums | 82B/sec | Minutes | No (needed separately) | NEVER for passwords |
| **SHA-256** | Integrity | 82B/sec | Hours | No (needed separately) | NEVER for passwords |
| **bcrypt (cost 12)** | Passwords | 30K/sec | 231 years | Built-in | Yes (legacy systems) |
| **scrypt** | Passwords + memory-hard | 5K/sec | Longer | Built-in | Acceptable |
| **Argon2id** | Passwords + memory-hard | ~3K/sec | 1000+ years | Built-in | **Best choice** |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| bcrypt is slow so it will hurt performance | bcrypt cost 12 takes ~300ms per hash on modern hardware. This is only for login operations (when the user submits their password). It does NOT affect any other requests (reading data, API calls, etc.). If your app has 1,000 concurrent logins/second: you need ~300 cores dedicated to bcrypt. Most applications have far fewer logins (login is a small fraction of requests). And: the 300ms is perceived as "slightly slow login" not "broken performance." The trade-off is: 300ms login delay prevents GPU-assisted password cracking. This is a very worthwhile trade-off. |
| If I salt with SHA-256, it's as good as bcrypt | SHA-256 with salt is faster than SHA-256 without salt (no rainbow tables). But it is still 2.7 million times faster than bcrypt. Salted SHA-256 resists rainbow tables but NOT GPU brute force. A dedicated GPU can try 82 billion SHA-256 hashes per second. Against a bcrypt hash (30K/sec): this GPU effectively becomes 2.7 million times slower. The salt prevents precomputation. The slow algorithm (bcrypt) prevents brute force. Both are required. SHA-256 + salt gives you one of the two required properties. |

---

### 🚨 Failure Modes & Diagnosis

**Failure: Discovering plain text passwords in production**

**How to find it:**
```python
# Audit: check if any password columns look like plain text
# (Any plain text or non-bcrypt hash should be treated as an emergency)
import re

def audit_password_column(db_cursor):
    db_cursor.execute("SELECT password FROM users LIMIT 100")
    rows = db_cursor.fetchall()

    for row in rows:
        pwd = row[0]
        # bcrypt outputs look like: $2b$12$[53 chars]
        if re.match(r'^\$2[ab]\$\d{2}\$', pwd):
            print("bcrypt: GOOD")
        elif re.match(r'^\$argon2', pwd):
            print("Argon2: GOOD (best)")
        elif len(pwd) in (32, 40, 64):
            print(f"POSSIBLE MD5/SHA1/SHA256 hash (length={len(pwd)}): BAD")
        else:
            print(f"POSSIBLE PLAIN TEXT (sample: {pwd[:4]}...): CRITICAL")
```

**Emergency response if plain text found:**
```
1. IMMEDIATE: Notify security team + legal.
2. EMERGENCY: Force password reset for all users
   (clear all passwords, require reset at next login).
3. NOTIFY: GDPR/CCPA notification to users within 72h.
4. REMEDIATION: Replace storage with bcrypt/Argon2 BEFORE
   users reset passwords (so new passwords are stored correctly).
5. CHECK: Did the same database exposure also leak email
   addresses? Are users at risk of credential stuffing?
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication vs Authorization vs Auditing` - context for why passwords matter
- `CIA Triad` - confidentiality of credentials

**Builds on this:**
- `Hashing vs Encryption vs Encoding` - when to use which
- `Bcrypt` - deep technical dive into the algorithm
- `Authentication Decision Tree` - choosing authentication mechanisms

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ALGORITHM    │ Argon2id (new) / bcrypt cost 12 (legacy)  │
│ TO USE       │ NEVER: MD5, SHA-1, SHA-256 for passwords  │
├──────────────┼───────────────────────────────────────────┤
│ SALT         │ Per-user, random, auto-generated by lib   │
│              │ Prevents rainbow tables + duplicate detect│
├──────────────┼───────────────────────────────────────────┤
│ SPEED        │ bcrypt cost 12: ~300ms on modern hardware │
│              │ Argon2id (64MB, 3t): ~400ms              │
│              │ Target: 100-300ms. Benchmark per hardware │
├──────────────┼───────────────────────────────────────────┤
│ REAL BREACH  │ LinkedIn 2012: 117M SHA-1 without salt   │
│ EXAMPLES     │ 90% cracked in 3 days                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fast hashes = fast cracking.            │
│              │  bcrypt = slow by design. Salt = unique. │
│              │  Strong password + bcrypt = impractical  │
│              │  to crack. Use the library. Not homemade."│
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Legitimate operations and malicious operations have
different computational requirements." bcrypt exploits this
asymmetry: a server verifying one password at login needs
300ms (acceptable). An attacker cracking a database of 10M
passwords needs to compute 10M hashes (unacceptable cost).
The same principle applies to: CAPTCHA (hard for bots,
acceptable for humans), proof-of-work in blockchain (easy
to verify, hard to compute), and API rate limiting (100
requests/minute is fine for legitimate users, prevents
automated abuse). In all cases: make the legitimate
operation fast enough and the malicious operation expensive
enough that the economics favor the defender.

---

### 💡 The Surprising Truth

bcrypt stores the salt IN the hash output. This is intentional
and by design. The bcrypt output string is:
`$2b$12$[22-char base64 salt][31-char base64 hash]`
The salt is not secret. If an attacker has the bcrypt hash,
they also have the salt (it is literally in the string).
This is fine because: the salt's purpose is to prevent
rainbow tables and prevent identical passwords from having
identical hashes - not to be kept secret. The hash
computation is the expensive operation that prevents
brute force, not the secrecy of the salt. This confuses
many developers who think: "if the salt is public, it's
insecure." The truth: salt privacy is not a security
property of bcrypt. Hash cost factor is the security
property. bcrypt's self-contained output format is a
feature: you only need to store one string per user,
and that string contains everything needed for verification.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why MD5/SHA-256 are wrong for passwords
   (designed to be fast = GPU-crackable at 82B/sec) and
   why bcrypt is right (deliberately slow = 30K/sec).
2. **EXPLAIN** what a salt does (prevents rainbow tables,
   prevents identical password detection) and why it is
   stored in the bcrypt output (not secret, just per-user).
3. **IMPLEMENT** bcrypt or Argon2id password hashing and
   verification using a standard library (not from scratch).
4. **IDENTIFY** the correct response when discovering plain
   text or MD5 passwords in a production database.

---

### 🎯 Interview Deep-Dive

**Q: How should passwords be stored in a database? What
are the common mistakes?**

*Why they ask:* This is a fundamental security question
that separates security-aware developers from others.
Every developer who handles user accounts should know this.

*Strong answer includes:*
- Should be: bcrypt (cost 12+) or Argon2id with per-user salt.
  Never reversible (no encryption, no plain text).
- Common mistakes:
  (1) Plain text (catastrophic - immediate exposure on breach).
  (2) MD5/SHA-1/SHA-256 (too fast - GPU can crack 82B/sec).
  (3) SHA-256 with application-wide static salt (no rainbow
      tables, but still GPU-crackable AND identical passwords
      have identical hashes → mass cracking of common passwords).
  (4) bcrypt but cost factor too low (cost 4-6 = <1ms → too fast).
  (5) "Rolling your own" password hashing (almost always wrong).
- Why bcrypt: the adaptive cost factor can be increased as
  hardware gets faster, maintaining the same crack-time
  guarantee over time.
- Supplementary: even with bcrypt, weak passwords (dictionary
  words, common patterns) are still quickly cracked. Require
  strong passwords + deploy MFA so that even cracked passwords
  cannot be used alone.