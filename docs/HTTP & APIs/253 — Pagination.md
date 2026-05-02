---
layout: default
title: "Pagination"
parent: "HTTP & APIs"
nav_order: 253
permalink: /http-apis/pagination/
number: "0253"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: REST, HTTP, Database Queries
used_by: REST APIs, List Endpoints, Data Export
related: API Design Best Practices, HATEOAS, Cursor-based Pagination
tags:
  - api
  - pagination
  - cursor
  - offset
  - rest
  - beginner
---

# 253 — Pagination

⚡ TL;DR — Pagination splits large result sets into smaller pages so that APIs return manageable chunks of data rather than millions of rows at once; the three main approaches are **offset pagination** (`?page=2&size=20` — simple but has skip performance problems), **cursor pagination** (`?cursor=xyz` — performant for large datasets, used by Twitter/Facebook), and **keyset pagination** (`?after_id=100` — similar to cursor, uses a stable sorting key).

| #253 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | REST, HTTP, Database Queries | |
| **Used by:** | REST APIs, List Endpoints, Data Export | |
| **Related:** | API Design Best Practices, HATEOAS, Cursor-based Pagination | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`GET /api/users` returns all 5 million users in the database in one response. The
response is 500MB of JSON. The server executes `SELECT * FROM users` — a full table scan.
Serialized to JSON: 30 seconds. The client: crashes attempting to parse 500MB into memory.
Even at 10,000 users: 10MB response per call is wasteful when the user only needs
to display the first page of 20 results. Without pagination: the API transfers and
processes data the consumer will never use.

---

### 📘 Textbook Definition

**Pagination** in REST APIs is the mechanism to divide a large result set into discrete
pages, returning a subset of results per request. Three main strategies:
(1) **Offset pagination** (`OFFSET N LIMIT M` in SQL): stateless, random-access pages,
simple implementation, but performance degrades at high offsets (DB must skip N rows).
(2) **Cursor pagination**: server returns an opaque cursor (often base64-encoded
sort-key + id) that points to the position in the result set; client sends cursor to
get the next page — stable under inserts/deletes, performant at any depth.
(3) **Keyset pagination** (seek method): client sends the last seen key value
(`?after_id=5000`) enabling `WHERE id > 5000 LIMIT 20` — uses index efficiently,
avoids full OFFSET scan. Response typically includes: data array, total count, and
navigation links or next cursor.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pagination chunks large lists into manageable pages — choose offset (simple) for small
datasets, cursor/keyset (performant) for large or frequently-updated datasets.

**One analogy:**
> Pagination is like a book's table of contents + chapters.
> Instead of giving you every page of a 1000-page book at once, the librarian gives you
> Chapter 3 (pages 45-60). Your bookmark (cursor) lets you pick up exactly where you left off.
> The page number approach (offset) works fine for small sections but is slow if you need
> to "skip to page 700 of 1000" — the librarian must physically count 700 pages.
> The bookmark approach (cursor) goes directly to the marked position.

---

### 🔩 First Principles Explanation

**THREE PAGINATION STRATEGIES:**

```
1. OFFSET PAGINATION:
   URL: GET /api/users?page=3&size=20
   SQL: SELECT * FROM users ORDER BY created_at LIMIT 20 OFFSET 40

   ✅ Simple to implement
   ✅ Random access (jump to any page)
   ✅ Total count easy to compute
   ❌ Performance: OFFSET 1000000 = DB scans 1,000,000 rows to discard
   ❌ Inconsistency: if rows inserted/deleted between pages, items skipped or duplicated
   Use for: small datasets (<100K rows), admin UIs with "go to page N" navigation

2. CURSOR PAGINATION:
   URL: GET /api/posts?cursor=eyJpZCI6MTAwLCJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSJ9&limit=20
   Cursor = base64({"id": 100, "created_at": "2024-01-15"})
   SQL: SELECT * FROM posts
        WHERE (created_at, id) < ('2024-01-15', 100)
        ORDER BY created_at DESC, id DESC
        LIMIT 20

   ✅ O(log N) performance via index — no full OFFSET scan
   ✅ Stable under inserts/deletes (cursor is an absolute position)
   ✅ Ideal for infinite scroll / feed-based UIs
   ❌ No random access (can't jump to page 500)
   ❌ Total count not available (or expensive to compute)
   ❌ Cursor is opaque — client must not parse it
   Use for: large datasets, social media feeds, real-time data

3. KEYSET PAGINATION (seek method):
   URL: GET /api/events?after_id=5000&limit=20
   SQL: SELECT * FROM events WHERE id > 5000 ORDER BY id LIMIT 20

   ✅ O(log N) via primary key index
   ✅ Simple to implement (no encoding required)
   ✅ Stable — no rows skipped/duplicated
   ❌ Forward-only navigation (no previous page without re-fetching)
   ❌ Requires unique, sequential ordering key (id or timestamp)
   Use for: event logs, audit trails, append-only collections
```

**RESPONSE STRUCTURE:**

```json
// Offset pagination response
{
  "data": [ {...}, {...}, {...} ],
  "pagination": {
    "page": 3,
    "size": 20,
    "total": 437,
    "totalPages": 22
  },
  "_links": {
    "self": "/api/users?page=3&size=20",
    "next": "/api/users?page=4&size=20",
    "prev": "/api/users?page=2&size=20",
    "first": "/api/users?page=1&size=20",
    "last": "/api/users?page=22&size=20"
  }
}

// Cursor pagination response
{
  "data": [ {...}, {...}, {...} ],
  "pagination": {
    "nextCursor": "eyJpZCI6MTIwLCJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNiJ9",
    "prevCursor": "eyJpZCI6MTAxLCJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSJ9",
    "hasMore": true
  }
}
```

---

### 🧪 Thought Experiment

**SCENARIO:** Twitter-style home timeline with 100M tweets.

```
OFFSET PAGINATION (bad for this use case):
  GET /timeline?page=5000&size=20
  SQL: SELECT * FROM tweets ORDER BY created_at DESC LIMIT 20 OFFSET 99980
  → DB must scan and discard 99,980 rows before returning 20
  → At scale: timeout / unacceptably slow
  → User adding new tweet between pages 4999 and 5000:
    → First tweet on page 5000 is same as last tweet on page 4999 (duplicate)

CURSOR PAGINATION (correct):
  Initial: GET /timeline?limit=20
  ← {data: [...20 tweets...], nextCursor: "eyJ0aW1lc3RhbXAiOiAxNzA1MDAwMDAwLCAiaWQiOiA5OTk5OX0"}

  User scrolls down: GET /timeline?cursor=eyJ0aW1lc3RhbXAiOiAxNzA1MDAwMDAwLCAiaWQiOiA5OTk5OX0&limit=20
  SQL: SELECT * FROM tweets
       WHERE (created_at, id) < (1705000000, 99999)  ← cursor decoded
       ORDER BY created_at DESC, id DESC
       LIMIT 20
  → Index seek: O(log N). Same performance at scroll position 10 or 10,000.
  → New tweets added: they're ahead of the cursor, page content is stable.
```

---

### 🧠 Mental Model / Analogy

> Offset pagination is counting by hand; cursor pagination is using a bookmark.
> Offset: "Give me results starting at position 10,000." Server: counts to 10,000, then returns 20.
> Cursor: "Give me results after this bookmark." Server: opens the book at the bookmark, returns 20.
> The bookmark never gets slower to use, no matter how deep in the book you are.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is:**
Pagination splits a big list into pages so the API doesn't return millions of records at once. Page numbers are simple; "cursors" are smarter bookmarks that work faster for huge datasets.

**Level 2 — How to use it:**
Spring Data: `PagingAndSortingRepository.findAll(PageRequest.of(page, size))`.
Returns `Page<T>` with content, total elements, and total pages. Add `?page=0&size=20`
as query params. For cursor-based: use a `WHERE id > lastSeenId` query with `LIMIT`.

**Level 3 — How it works:**
Offset pagination generates `LIMIT + OFFSET` SQL. At `OFFSET 100000`, PostgreSQL must
traverse 100,000 index entries before returning 20 — effectively an O(N) scan.
Cursor pagination replaces OFFSET with a `WHERE (sort_col, id) < (cursor_val)` predicate
that uses a composite index directly — O(log N). The cursor must encode the full sort key
(not just ID) to handle ties in the sort column. Encoding in base64 is intentional:
clients must treat it opaque; if cursor encoding changes (e.g., adding a new sort tiebreaker),
it doesn't break client code. Cursor rotation: always set an expiry on cursors (especially
for search-engine-backed pagination) to avoid indefinite cursor validity.

**Level 4 — Why it was designed this way:**
Cursor pagination's opaque design prevents clients from constructing cursors, making
the API free to change its pagination implementation. The composite sort key `(timestamp, id)`
handles the common problem: if dozens of records share the same timestamp, a cursor of
just the timestamp is ambiguous — `(timestamp, id)` is always unique. Facebook's Graph API,
Twitter Firehose, and GitHub's API all use cursor pagination for timeline/stream data.
HATEOAS (Hypermedia as the Engine of Application State) formalizes pagination links in
the response, eliminating clients hardcoding `/api/users?page=X` URL construction —
clients follow `_links.next` — URLs can change without breaking clients.

---

### ⚙️ How It Works (Mechanism)

```
CURSOR ENCODING:

  Cursor payload: { "sort_val": "2024-01-15T10:30:00Z", "id": 5432 }
  Encoded: Base64URL("2024-01-15T10:30:00Z|5432")
         = "MjAyNC0wMS0xNVQxMDozMDowMFp8NTQzMg"

  Decoding on server:
  1. Base64URL decode → "2024-01-15T10:30:00Z|5432"
  2. Parse → timestamp=2024-01-15T10:30:00Z, id=5432
  3. WHERE clause:
     WHERE (created_at, id) < ('2024-01-15T10:30:00Z', 5432)
     ORDER BY created_at DESC, id DESC
     LIMIT 20
  4. Encode last result as next cursor

  Index used: (created_at, id) composite index
  → Seek to position without scanning all previous rows
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
CLIENT PAGINATION FLOW (cursor):

  Page 1: GET /api/posts?limit=20
  ← 200 OK { data: [post1..post20], nextCursor: "cursor_A", hasMore: true }

  Page 2: GET /api/posts?cursor=cursor_A&limit=20
  ← 200 OK { data: [post21..post40], nextCursor: "cursor_B", hasMore: true }

  Page N: GET /api/posts?cursor=cursor_X&limit=20
  ← 200 OK { data: [lastPosts], nextCursor: null, hasMore: false }
  → Client: no more data, stop fetching
```

---

### 💻 Code Example

```java
// Spring Boot: cursor pagination for events
@GetMapping("/api/v1/events")
public ResponseEntity<CursorPage<EventDto>> getEvents(
        @RequestParam(required = false) String cursor,
        @RequestParam(defaultValue = "20") int limit) {

    // Decode cursor (if present)
    EventCursor decodedCursor = cursor != null
        ? CursorCodec.decode(cursor)
        : null;

    // Keyset query: WHERE (created_at, id) < (cursor_ts, cursor_id)
    List<Event> events = eventRepository.findPage(decodedCursor, limit + 1);

    // Extra item signals "has more"
    boolean hasMore = events.size() > limit;
    List<Event> page = hasMore ? events.subList(0, limit) : events;

    // Encode cursor from last item
    String nextCursor = hasMore
        ? CursorCodec.encode(page.get(page.size() - 1))
        : null;

    return ResponseEntity.ok(CursorPage.<EventDto>builder()
        .data(page.stream().map(this::toDto).collect(toList()))
        .nextCursor(nextCursor)
        .hasMore(hasMore)
        .build());
}

// Spring Data JPA custom query
@Query("""
    SELECT e FROM Event e
    WHERE (:cursorAt IS NULL OR e.createdAt < :cursorAt
        OR (e.createdAt = :cursorAt AND e.id < :cursorId))
    ORDER BY e.createdAt DESC, e.id DESC
    """)
List<Event> findPage(
    @Param("cursorAt") Instant cursorAt,
    @Param("cursorId") Long cursorId,
    Pageable pageable);

// Cursor encode/decode
public class CursorCodec {
    public static String encode(Event event) {
        String raw = event.getCreatedAt().toEpochMilli() + "|" + event.getId();
        return Base64.getUrlEncoder().encodeToString(raw.getBytes(UTF_8));
    }
    public static EventCursor decode(String encoded) {
        String raw = new String(Base64.getUrlDecoder().decode(encoded), UTF_8);
        String[] parts = raw.split("\\|");
        return new EventCursor(Instant.ofEpochMilli(Long.parseLong(parts[0])),
                               Long.parseLong(parts[1]));
    }
}
```

---

### ⚖️ Comparison Table

| Strategy | Performance | Random Access | Stable Under Mutations | Implementation |
|---|---|---|---|---|
| **Offset (page/size)** | O(N) for large offsets | ✅ Yes | ❌ Skips/duplicates | Simple |
| **Cursor** | O(log N) via index | ❌ No | ✅ Yes | Medium |
| **Keyset (after_id)** | O(log N) via index | ❌ Forward only | ✅ Yes | Simple |
| **Seek with HATEOAS** | O(log N) | ❌ Via links only | ✅ Yes | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Offset pagination is fine for all sizes | Acceptable up to ~50K rows. Beyond that: OFFSET 100000 performance degrades significantly in PostgreSQL/MySQL |
| Cursor pagination requires total count | Cursor pagination intentionally omits total count (expensive with cursor). Users get `hasMore: true/false`. If total count needed: separate `GET /api/events/count` endpoint |
| Page size should be fixed | Allow client-controlled `?limit=N` with a server-enforced maximum (e.g., max 100). Flexible for different UI needs |

---

### 🚨 Failure Modes & Diagnosis

**Duplicate/Missing Items in Offset Pagination**

**Symptom:** User on page 3 of a feed; a new post is added. Page 4 now shows an item
the user already saw on page 3 (or an item is skipped entirely).

**Root Cause:** Offset-based pagination over a mutable result set. New inserts shift OFFSET positions.

**Fix:**
```sql
-- If you must use offset: freeze the sort order with a created_at timestamp anchor
-- returned with page 1, used for all subsequent pages:
SELECT * FROM posts
WHERE created_at <= :anchorTimestamp    ← user's session anchor
ORDER BY created_at DESC
LIMIT 20 OFFSET :offset

-- Better fix: switch to cursor pagination for feed/timeline use cases
```

---

### 🔗 Related Keywords

- `HATEOAS` — hypermedia pagination links (`_links.next`) in REST responses
- `API Design Best Practices` — pagination is a core REST API design concern
- `Database Indexing` — composite index `(sort_col, id)` required for cursor pagination

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ OFFSET        │ ?page=3&size=20, simple, small datasets  │
│ CURSOR        │ ?cursor=xxx, O(log N), large/feeds       │
│ KEYSET        │ ?after_id=5000, append-only logs         │
├──────────────┼───────────────────────────────────────────┤
│ RESPONSE     │ { data: [], nextCursor: "...",            │
│              │   hasMore: true/false }                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Chunk results; cursor for scale"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HATEOAS → API Design Best Practices      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You're designing a "search for orders" endpoint: users can filter by status, date range, and customer name. Results should be paginated. The Product Manager wants "go to page N" navigation (offset) AND the Engineering team wants cursor pagination for performance. These are mutually exclusive. How do you design the API to satisfy both requirements? What techniques (client-side paging over a cursor result set, page-anchor strategies, separate endpoints) could reconcile this tension, and what are their tradeoffs?
