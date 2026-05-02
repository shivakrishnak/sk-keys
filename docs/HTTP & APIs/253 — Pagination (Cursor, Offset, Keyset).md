---
layout: default
title: "Pagination (Cursor, Offset, Keyset)"
parent: "HTTP & APIs"
nav_order: 253
permalink: /http-apis/pagination/
number: "0253"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, HTTP Methods, HTTP Status Codes, SQL Fundamentals, Database Indexes
used_by: API Design Best Practices, GraphQL, REST
related: HATEOAS, Rate Limiting, API Throttling, Caching, HTTP Headers
tags:
  - api
  - pagination
  - database
  - performance
  - core-concept
---

# 253 — Pagination (Cursor, Offset, Keyset)

⚡ TL;DR — Pagination controls how large datasets are split into pages for API responses. Three strategies dominate: offset/limit (simple but inconsistent under inserts/deletes), cursor (stable but opaque), and keyset (efficient at depth but requires sort-key awareness).

| #253            | Category: HTTP & APIs                                                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | REST, HTTP Methods, HTTP Status Codes, SQL Fundamentals, Database Indexes |                 |
| **Used by:**    | API Design Best Practices, GraphQL, REST                                  |                 |
| **Related:**    | HATEOAS, Rate Limiting, API Throttling, Caching, HTTP Headers             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An API endpoint returns the full result set: `GET /posts` returns all 2 million posts.
The first query takes 8 seconds and returns 800 MB of JSON. The database is fully
loaded. The client's memory overflows. Mobile clients time out. The API is unusable
for any realistic dataset size.

**THE BREAKING POINT:**
Returning full result sets doesn't scale beyond a few hundred records. Real APIs
serving production traffic need to return data in chunks — exactly as many records
as the client can handle at once.

**THE INVENTION MOMENT:**
Pagination must be designed into APIs from the start. But different pagination
strategies make different trade-offs between simplicity, consistency, and performance.
The wrong choice creates subtle bugs (duplicate/missing records during inserts) or
severe performance problems (full table scans at deep pages).

---

### 📘 Textbook Definition

**Offset Pagination** uses `?page=2&size=20` or `?offset=40&limit=20` to skip a
number of rows. The database executes `LIMIT 20 OFFSET 40`. Simple to implement
but has two fundamental problems: (1) rows inserted or deleted between pages cause
skips or duplicates; (2) at large offsets (page 10,000) the database must scan and
discard all preceding rows, causing O(N) cost per page regardless of index use.

**Cursor Pagination** encodes the position of the last seen record as an opaque
token (the cursor). Clients send `?after=eyJpZCI6MTIzfQ==` to get the next page.
The server decodes the cursor, queries from that position forward. Cursors are stable
under inserts/deletes and provide O(log N) query cost. They do not support random
access to arbitrary pages.

**Keyset Pagination** (a transparent form of cursor pagination) uses the last
record's actual sort-key value: `?after_id=123&after_created=2024-01-15`. The database
executes `WHERE (created, id) > ('2024-01-15', 123) ORDER BY created, id LIMIT 20`
using an index seek. Efficient at any depth; allows the client to construct "next
page" directly; requires a stable, unique sort key per page.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pagination is how APIs hand you a dataset one page at a time, and the strategy
determines whether flipping to page 5,000 takes 5ms or 50 seconds.

**One analogy:**

> Offset pagination is like reading a book by counting from page 1 to wherever
> you want to start every time you pick it up — slower the further along you are.
> Cursor pagination is like using a bookmark — you open exactly where you left off,
> instantly, no counting. Keyset is the same bookmark, but you can read the page
> number on it.

**One insight:**
Deep offset pagination (`OFFSET 100000`) costs the database the same work whether
the result set is ordered by index or not — it scans and discards 100,000 rows.
Cursor/keyset pagination costs `O(log N)` at any depth because it's an index seek,
not a scan. For "infinite scroll" feeds, this difference is the boundary between
"usable" and "unusable" at scale.

---

### 🔩 First Principles Explanation

**THE THREE STRATEGIES COMPARED:**

```
┌─────────────────────────────────────────────────────────┐
│              Pagination Strategy Comparison             │
├─────────────┬──────────────┬──────────────┬─────────────┤
│             │ Offset       │ Cursor       │ Keyset      │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ Query param │ ?page=3&size │ ?after=TOKEN │ ?after_id=  │
│             │ =20          │              │ 123         │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ DB query    │ LIMIT 20     │ WHERE id >   │ WHERE id >  │
│             │ OFFSET 40    │ [decoded]    │ 123 LIMIT   │
│             │              │ LIMIT 20     │ 20          │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ Complexity  │ O(N) at      │ O(log N)     │ O(log N)    │
│             │ deep offset  │ any depth    │ any depth   │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ Stability   │ Unstable     │ Stable       │ Stable      │
│             │ (rows shift  │              │             │
│             │ on insert)   │              │             │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ Random      │ YES          │ NO           │ NO          │
│ access      │ GET page 50  │ must follow  │ must follow │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ Sortable    │ Any column   │ Opaque       │ Explicit    │
│             │              │              │ sort key    │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ Complexity  │ Simple       │ Medium       │ Medium      │
├─────────────┼──────────────┼──────────────┼─────────────┤
│ Best for    │ Admin UIs,   │ Feeds,       │ Feeds, APIs │
│             │ small data   │ timelines    │ with visible│
│             │              │              │ sort keys   │
└─────────────┴──────────────┴──────────────┴─────────────┘
```

**OFFSET INSTABILITY DEMO:**

```
Page 1 request: GET /posts?page=1&size=3
DB state at request time:  [A, B, C, D, E, F]
Response: [A, B, C]  ← correct

New post X inserted at the TOP (most recent):
DB state now:  [X, A, B, C, D, E, F]

Page 2 request: GET /posts?page=2&size=3
DB executes: SELECT * OFFSET 3 LIMIT 3
Response: [C, D, E]  ← C was already in page 1!

Result: C is duplicated.
If a post was deleted from page 1 between requests,
a record would be SKIPPED instead.
```

**KEYSET SQL PATTERN:**

```sql
-- Sort key: (created_at DESC, id DESC) — stable, unique
-- First page:
SELECT * FROM posts
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Subsequent pages (keyset):
SELECT * FROM posts
WHERE (created_at, id) < ('2024-01-15 10:00:00', 1234)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Index used: (created_at, id) covering index
-- Cost: O(log N) regardless of how deep into the dataset
```

**CURSOR ENCODING (opaque cursor from keyset):**

```python
import base64, json

def encode_cursor(last_item):
    payload = {"id": last_item["id"],
               "created": last_item["created_at"]}
    return base64.b64encode(
        json.dumps(payload).encode()).decode()

def decode_cursor(cursor_token):
    return json.loads(
        base64.b64decode(cursor_token).decode())

# Client sees: ?after=eyJpZCI6IDEyMzR9Cg==
# Client cannot construct cursors manually — server controls pagination
```

---

### 🧪 Thought Experiment

**SETUP:**
Twitter's home timeline API. 300 million users. Average timeline: 200 posts visible
at a time in a session. Timeline is sorted by newest-first (reverse chronological).
New tweets constantly arrive. Users scroll down ("Load more"). Some users jump to
"yesterday's timeline" link.

**OFFSET PAGINATION:**

- User on page 500: database scans and discards 10,000 tweets → 200ms query
- New tweet arrives at the top: pages 1-499 all shift — user sees duplicates on
  next scroll → terrible UX
- Duplicate tweets destroy user trust. DMs "Twitter is showing me old tweets again"

**CURSOR PAGINATION:**

- User on page 500: cursor = `eyJpZCI6IDIzMTk4fQ==` → O(log N) seek → 2ms query
- New tweet at top: cursor holds position perfectly — user continues where they left off
- "Yesterday's timeline": cursor CAN'T do this — cursors are sequential-only
- Result: Twitter needs BOTH — cursor for scrolling, separate feature for time-travel

**THE INSIGHT:**
Cursor and keyset solve the scalability and consistency problems of offset pagination
at the cost of random page access. In practice, infinite-scroll UIs (most mobile
feeds) never need random access — they only need "next" — making cursor the natural fit.
Admin UIs ("show me page 47") still need offset pagination but have small enough
datasets that performance is acceptable.

---

### 🧠 Mental Model / Analogy

> Imagine a very long sorted file cabinet with 10 million folders.
>
> Offset pagination: "Give me folders 40,001 to 40,020." The clerk walks from the
> BEGINNING, counts 40,000 folders, then hands you 20. If someone adds a folder
> while you're reading, your count is off.
>
> Cursor pagination: "Continue from where I put this bookmark." The clerk opens
> exactly at the bookmark and hands you 20 folders forward. Inserts don't affect
> the bookmark's position.
>
> Keyset: Same as cursor, but the bookmark is labelled with the folder number
> you can read — so you can tell another clerk "start from folder #40042" using
> the label, not a coded token.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
APIs serve large lists in chunks called pages. Pagination tells the API "give me
page 3 of the results" or "give me the next 20 after the last one I saw." How you
identify "where you are" in the list determines whether the API works correctly
when new data arrives and whether it stays fast when the list has millions of items.

**Level 2 — How to use it (junior developer):**
Use `?page=N&size=M` for simple admin endpoints with small datasets. For production
feeds and timelines, use cursor: the server provides an opaque `next_cursor` in the
response; send it as `?after=<cursor>` on the next request. Never try to decode or
construct cursors manually. Always follow HATEOAS `next`/`prev` links when provided.

**Level 3 — How it works (mid-level engineer):**
Keyset pagination requires a unique, indexed sort key — typically a composite
`(timestamp, id)` pair to handle same-timestamp ties. The WHERE clause encodes a
"row comparison": `(created_at, id) < (:last_created, :last_id)`. This must match
the ORDER BY clause exactly. Adding a filter (e.g., by user_id) to keyset pagination
requires a covering index on `(user_id, created_at, id)`. Cursor pagination can
hide keyset complexity: encode the keyset values into the cursor token, giving clients
an opaque API while using efficient keyset queries underneath.

**Level 4 — Why it was designed this way (senior/staff):**
The instability of offset pagination under concurrent writes is not a bug but a
fundamental property of how relational databases evaluate `OFFSET`: it is evaluated
AFTER filtering and ordering, on a snapshot read of the result set at query time.
There is no stable position in a sorted result set under inserts/deletes except one
derived from the actual data values (keyset). The engineering insight behind cursor
pagination is wrapping keyset as an opaque token to decouple clients from sort-key
schema details — enabling server-side refactoring of keyset structure without
changing the client API. Real systems (Stripe, GitHub API, Twitter v2) use cursor
pagination precisely for this reason.

---

### ⚙️ How It Works (Mechanism)

**HATEOAS Pagination Response (HAL):**

```json
GET /posts?size=20
{
  "data": [ ...20 posts... ],
  "meta": {
    "total": 15000,
    "size": 20,
    "has_next": true
  },
  "_links": {
    "self":  { "href": "/posts?size=20" },
    "first": { "href": "/posts?size=20" },
    "next":  { "href": "/posts?size=20&after=eyJpZCI6IDIwfQ==" },
    "last":  { "href": "/posts?size=20&before=LAST_CURSOR" }
  }
}
```

**Stripe-style cursor pagination (industry standard):**

```json
GET /v1/charges?limit=3
{
  "object": "list",
  "data": [ ...3 charges... ],
  "has_more": true,
  "url": "/v1/charges",
  "next_cursor": "ch_1N5Kj2ABC..."
}

GET /v1/charges?limit=3&starting_after=ch_1N5Kj2ABC...
→ returns next 3 charges after that ID
```

---

### ⚖️ Comparison Table

| Strategy             | Use Case                    | Random Access | Stability | DB Performance |
| -------------------- | --------------------------- | ------------- | --------- | -------------- |
| Offset               | Admin UIs, small data       | Yes           | Unstable  | O(N) at depth  |
| Cursor               | Feeds, timelines            | No            | Stable    | O(log N)       |
| Keyset               | Same as cursor, transparent | No            | Stable    | O(log N)       |
| Page token (GraphQL) | Connection pattern          | No            | Stable    | O(log N)       |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                       |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Offset pagination is fine for production            | At OFFSET 100,000 with 1M rows, performance degrades severely even with indexes. Cursor/keyset are needed for deep pagination |
| Cursors prevent duplicates entirely                 | Only if the sort key is truly unique and stable. Non-unique sort keys (timestamp alone) can still produce duplicates          |
| Total count is easy with cursor pagination          | Accurate total counts require `COUNT(*)` full scans — expensive. Many cursor APIs omit totals or provide estimates            |
| `LIMIT/OFFSET` and offset pagination are equivalent | Offset pagination is a convention using LIMIT/OFFSET; keyset also uses LIMIT but replaces OFFSET with a WHERE predicate       |
| Cursor = Base64 encoded JSON only                   | Cursors are opaque tokens — they CAN encode anything: timestamps, IDs, sort vectors, encrypted values                         |

---

### 🚨 Failure Modes & Diagnosis

**Duplicate Records on Page Flip (Offset Instability)**

Symptom: Users report seeing the same items on consecutive pages; analytics
show the same record IDs processing twice in ingestion pipelines.

Root Cause: Offset pagination used on a frequently-updated dataset. Inserts
near the sort order cause previously-seen rows to shift into subsequent pages.

Diagnostic:

```bash
# Check if API uses offset-style params on a live dataset:
curl "https://api.example.com/events?page=2&size=10"
# Also check: does response include a stable cursor or next_link?
```

Fix: Migrate to cursor/keyset pagination. Short-term: add a `created_after`
filter equal to the first page's earliest timestamp to approximate stability.

---

**Deep Page Timeout (Offset at Scale)**

Symptom: `GET /admin/audit-logs?page=10000` times out; slow query log shows
`filesort` with millions of rows; page 1 returns in 10ms, page 10000 in 45s.

Diagnostic:

```sql
EXPLAIN SELECT * FROM audit_logs ORDER BY id LIMIT 20 OFFSET 200000;
-- Look for "rows" in the millions despite a LIMIT of 20
```

Fix: Keyset pagination: `WHERE id > :last_id ORDER BY id LIMIT 20`. For admin
UI requiring random access to arbitrary pages, add a server-side materialized
view with pre-computed page boundaries updated periodically.

---

### 🔗 Related Keywords

- `HATEOAS` — standard approach to expose next/prev/first/last pagination links
- `API Design Best Practices` — choosing the right pagination strategy per use case
- `Caching` — cursor responses are cacheable; offset responses invalidate frequently
- `Database Indexes` — keyset pagination requires appropriate composite indexes

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  Offset      │ LIMIT N OFFSET M — simple but O(N) deep │
│  Cursor      │ ?after=TOKEN — stable, opaque, O(log N)  │
│  Keyset      │ WHERE (col,id) > (:val,:id) — transparent│
│  CHOOSE:     │ Admin UI = offset | Feed/stream = cursor  │
│  LINKS:      │ Always provide _links.next in response   │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A social feed API uses `created_at DESC` as the only sort key for cursor
pagination. Two posts are created at the exact same millisecond. Explain why this
causes pagination to break even with cursor-based pagination, and describe the
minimal schema change required to fix it.

**Q2.** You're designing a public search API with 10 million records that supports
arbitrary multi-field filtering (`?category=X&price_min=Y`). A user wants to export
all matching results using a script that fetches page after page. Compare offset
and keyset for this use case: which do you recommend, what index is needed, and
what happens to the export job if a matching record is deleted mid-export?
