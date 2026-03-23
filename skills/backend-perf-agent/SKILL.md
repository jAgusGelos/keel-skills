---
name: backend-perf-agent
description: |
  Deep backend and database performance investigator that finds every bottleneck in server-side
  code, queries, schema design, caching, and infrastructure. Dispatches 5 parallel agents across
  query/ORM analysis, schema/indexing, API/middleware, caching/connection management, and external
  Codex validation to produce a prioritized performance audit with concrete fixes.
  Use when the user says "backend performance", "db performance", "database audit", "query optimization",
  "slow queries", "N+1", "find backend bottlenecks", "API slow", "server performance", "optimize queries",
  "database review", "connection pool", "caching strategy", "index optimization", "schema review",
  "backend audit", or wants a comprehensive performance investigation of their backend code.
  Also trigger when the user mentions "EXPLAIN ANALYZE", "query plan", "slow endpoint", "timeout",
  "pool exhaustion", "memory leak server", "event loop lag", or "transaction deadlock".
version: 1.0.0
category: development
depends: []
---

# Backend Performance Agent — Deep Bottleneck Investigator

Comprehensive backend and database performance audit that finds every bottleneck through 5
parallel specialized agents. Each agent reads actual source code, schema files, ORM models,
and config to identify real issues with concrete fixes.

## Philosophy

Backend performance problems are invisible until they hit production at scale. A query that
runs fine with 100 rows becomes a disaster with 100K. A missing index costs nothing on dev
but causes page timeouts in prod. This agent investigates everything: from ORM patterns in
application code to schema design, missing indexes, connection management, caching gaps,
and API middleware overhead.

Every finding must be **actionable** — file path, line number (or table/column), what's
wrong, how to fix it, and the expected impact at scale.

## The Flow

```
User triggers backend audit
         |
         v
[0] Context & Stack Detection
         |
         v
[1] Parallel Investigation ──┬── Agent 1: Query & ORM Patterns
         |                    ├── Agent 2: Schema & Indexing
         |                    ├── Agent 3: API & Middleware
         |                    ├── Agent 4: Caching & Connections
         |                    └── Agent 5: Codex External Validation
         v
[2] Merge, Deduplicate & Cross-Reference
         |
         v
[3] Impact-Prioritized Report
         |
         v
[4] Present Action Plan to User
```

## Step 0: Context & Stack Detection

Before dispatching agents, understand the project:

1. **Read memory-bank** (if available):
   - `memory-bank/tech-context.md` — stack, DB engine, ORM, hosting, infra
   - `memory-bank/system-patterns.md` — architecture, API patterns, data flow
   - `memory-bank/active-context.md` — current focus, recent changes

2. **Auto-detect stack** (if no memory-bank):
   ```
   package.json          → runtime (node, bun, deno), framework (next, express, fastify, nestjs)
   prisma/schema.prisma  → Prisma ORM + DB engine (postgresql, mysql, sqlite, mongodb)
   drizzle.config.*      → Drizzle ORM
   knexfile.*            → Knex query builder
   typeorm.config.*      → TypeORM
   sequelize.config.*    → Sequelize
   supabase/config.toml  → Supabase (PostgreSQL + Edge Functions)
   docker-compose.yml    → DB services (postgres, redis, mongo, mysql)
   .env / .env.example   → DATABASE_URL, REDIS_URL, connection strings
   migrations/           → Migration files (reveal schema history)
   ```

3. **Identify DB engine and version** from connection strings or config:
   - PostgreSQL, MySQL/MariaDB, MongoDB, SQLite, PlanetScale, Neon, Supabase
   - Redis/Valkey/DragonflyDB for caching layer

4. **Scan project structure**:
   - `src/api/` or `src/routes/` or `app/api/` → API endpoints
   - `src/services/` or `src/lib/` → business logic layer
   - `src/repositories/` or `src/models/` → data access layer
   - `prisma/` or `drizzle/` or `migrations/` → schema definitions
   - `src/middleware/` → middleware chain
   - `src/jobs/` or `src/workers/` or `src/queues/` → background processing

Save all context — every agent receives the same stack profile.

## Step 1: Parallel Agent Dispatch

Launch all 5 agents simultaneously. Each receives:
- The stack profile from Step 0
- Specific files to read based on their domain
- Their investigation checklist

---

### Agent 1: Query & ORM Patterns (Claude Subagent)

```
You are a backend performance expert specialized in QUERY PATTERNS and ORM USAGE.

Investigate the codebase for query-level bottlenecks. Read actual source files — services,
repositories, API handlers, and ORM model definitions. For every finding, provide file:line,
the problem, the fix, and estimated impact at scale.

## Stack Profile
{STACK_PROFILE}

## Your Investigation Checklist (16 points)

### N+1 and Query Multiplication
1. **N+1 query patterns** — The #1 backend performance killer. Look for:
   - Loops that execute a query per iteration (`for/forEach/map` with await inside)
   - ORM lazy-loading that fires per-row (Prisma `.posts()` in a loop, Sequelize get methods)
   - GraphQL resolvers that fetch per-field without dataloader
   - Fix: batch with `WHERE id IN (...)`, use `include`/`join`/`with`, add dataloader

2. **Unbounded IN clauses** — `WHERE id IN (...)` with thousands of IDs. The query planner
   struggles with huge IN lists and can fall back to sequential scans.
   - Fix: batch into chunks of 500-1000, or use temp tables / `ANY(array)` in PostgreSQL

3. **SELECT * patterns** — Fetching all columns when only a few are needed. Wastes memory,
   bandwidth, and prevents index-only scans.
   - Fix: explicit column selection (`select` in Prisma, `.select()` in Knex/Drizzle)

4. **Missing eager loading** — Related data fetched in separate queries when it could be
   joined. Check for sequential awaits:
   ```
   const user = await getUser(id)
   const posts = await getPostsByUser(id)  // Should be a join or include
   const comments = await getCommentsByUser(id)  // Another round trip
   ```

5. **Redundant queries** — Same data fetched multiple times in the same request cycle.
   Check for the same query appearing in middleware AND handler AND service layer.

### Query Efficiency
6. **Missing pagination** — Endpoints that return unbounded result sets. Any `findMany()`
   or `SELECT` without `LIMIT` on a growing table is a ticking bomb.
   - Flag: `findMany()` without `take`, raw queries without `LIMIT`
   - Fix: cursor-based pagination (`cursor` + `take` in Prisma, `WHERE id > $cursor LIMIT N`)

7. **OFFSET pagination on large tables** — `OFFSET 10000` forces the DB to scan and discard
   10K rows. Gets exponentially slower as offset grows.
   - Fix: cursor/keyset pagination (`WHERE id > last_seen_id ORDER BY id LIMIT N`)

8. **Expensive string operations in queries** — `LIKE '%term%'` (leading wildcard),
   `LOWER(column)` without functional index, regex in WHERE clause.
   - Fix: full-text search (GIN index + tsvector in PG), trigram index for LIKE

9. **Unoptimized aggregations** — `COUNT(*)` on large tables without materialized counters,
   complex GROUP BY without supporting indexes.
   - Fix: maintain counters in a separate table, add composite indexes for GROUP BY columns

10. **Date/time query anti-patterns** — Functions on indexed columns (`WHERE DATE(created_at) = ...`)
    that prevent index usage. Implicit type coercion in date comparisons.
    - Fix: range queries (`WHERE created_at >= $start AND created_at < $end`)

### ORM-Specific
11. **Prisma-specific issues:**
    - Multiple PrismaClient instances (exhausts connection pool)
    - Missing `relationLoadStrategy: "join"` for nested includes
    - `findFirst` without unique constraint (scans until first match)
    - Interactive transactions with external API calls inside (holds connection)

12. **TypeORM/Sequelize-specific issues:**
    - Lazy relations loading N+1 silently
    - Missing `relations` option on find methods
    - Synchronize mode on in production

13. **Raw query injection risks** — String interpolation in raw SQL instead of parameterized
    queries. Both a security AND performance issue (prevents query plan caching).

### Transaction Management
14. **Long-running transactions** — Transactions that hold locks while doing:
    - External API calls (HTTP requests inside a transaction)
    - File I/O or S3 uploads
    - Complex computation
    - Fix: do external work outside the transaction, only wrap DB operations

15. **Missing transactions where needed** — Multi-step operations that should be atomic
    but aren't. Look for sequential writes without transaction wrapper:
    ```
    await createOrder(data)      // succeeds
    await deductInventory(id)    // fails — order exists without inventory deduction
    ```

16. **Deadlock-prone patterns** — Multiple transactions acquiring locks in different orders.
    Look for concurrent updates to the same tables from different code paths without
    consistent lock ordering.

## Files to Read
- All files in src/services/, src/repositories/, src/models/
- API route handlers (src/api/**, app/api/**/route.ts)
- Prisma schema (prisma/schema.prisma) or ORM config
- Any file with "query", "db", "repository", "dao" in the name
- GraphQL resolvers if applicable

## Output Format
For each finding:
- **Impact**: CRITICAL / HIGH / MEDIUM / LOW (at current scale + projected at 10x)
- **File:Line**: exact location
- **Problem**: what's wrong and why it degrades under load
- **Current Query**: the problematic query or code pattern
- **Optimized Version**: the fixed query or code with explanation
- **Estimated Impact**: queries eliminated, response time improvement, or load capacity gain
```

---

### Agent 2: Schema & Indexing (Claude Subagent)

```
You are a database performance expert specialized in SCHEMA DESIGN and INDEXING STRATEGY.

Investigate the schema, migrations, and index configuration for structural bottlenecks.
Read the actual schema files, migration history, and query patterns to find missing or
incorrect indexes, type problems, and design issues.

## Stack Profile
{STACK_PROFILE}

## Your Investigation Checklist (14 points)

### Index Analysis
1. **Missing indexes on foreign keys** — Every foreign key column MUST have an index.
   Unindexed FKs cause sequential scans on JOIN and ON DELETE CASCADE operations.
   - Read schema for all relation fields / foreign key columns
   - Verify each has a corresponding index

2. **Missing composite indexes** — Queries with multi-column WHERE clauses need composite
   indexes in the correct order (equality columns first, then range columns).
   - Cross-reference query patterns in application code with existing indexes

3. **Redundant indexes** — Indexes that are prefixes of other composite indexes waste
   write performance and disk. Example: INDEX(a) is redundant if INDEX(a, b) exists.

4. **Missing partial indexes** — Tables with soft-delete (`deleted_at IS NULL`) or status
   columns where most queries filter on active records. A partial index is much smaller:
   `CREATE INDEX ... WHERE deleted_at IS NULL`

5. **Missing covering indexes** — Frequently-run queries that could be served entirely from
   the index (index-only scans) with INCLUDE columns. Avoids heap table lookups.

6. **Wrong index type** — Using B-tree for full-text search (should be GIN), or B-tree
   for JSONB containment queries (should be GIN). Index type reference:
   - B-tree: equality, range, sorting (default, most queries)
   - GIN: full-text search, JSONB containment, array operations
   - BRIN: time-series data with natural ordering
   - Hash: equality-only (rare, B-tree usually better)

### Schema Design
7. **Data type problems:**
   - `int` for IDs that will exceed 2.1B → use `bigint`
   - `varchar(255)` habit from MySQL → use `text` in PostgreSQL (no perf difference)
   - `timestamp` without timezone → use `timestamptz`
   - `float` for money → use `numeric(precision, scale)`
   - `UUID v4` as primary key → causes index fragmentation (random order). Use UUIDv7
     (time-ordered) or bigint with sequences

8. **Missing constraints** — Tables without:
   - `NOT NULL` on columns that should never be null (prevents bad data, helps optimizer)
   - `UNIQUE` constraints where business logic demands uniqueness
   - `CHECK` constraints for valid ranges/enums
   - Foreign key constraints (data integrity + optimizer hints)

9. **Table bloat indicators** — Tables without proper VACUUM strategy, especially:
   - High-write tables with frequent updates/deletes
   - Tables with TOAST'd columns (large text/jsonb)
   - Check for `autovacuum_vacuum_scale_factor` overrides

10. **Missing partitioning** — Large tables (>10M rows) with time-based queries that
    would benefit from range partitioning. Common candidates:
    - Event/log tables
    - Analytics/metrics tables
    - Audit trail tables

### Migration Safety
11. **Dangerous migration patterns:**
    - `ALTER TABLE ... ADD COLUMN ... DEFAULT` on large tables (rewrites entire table in PG < 11)
    - `CREATE INDEX` without `CONCURRENTLY` (locks table for writes)
    - Dropping columns that are still referenced
    - Renaming columns (breaks running application during deploy)

12. **Schema drift** — ORM schema out of sync with actual database. Check if Prisma schema
    matches migrations, or if manual SQL changes were applied outside the ORM.

### Denormalization Opportunities
13. **Expensive JOINs that could be denormalized** — Queries joining 4+ tables on every
    request. Consider:
    - Materialized views for read-heavy aggregations
    - Denormalized columns for frequently-joined data
    - JSONB columns for nested data that's always read together

14. **Missing counter caches** — Counting related rows on every request
    (`COUNT(*) FROM comments WHERE post_id = $1`) instead of maintaining a
    `comments_count` column on the parent table.

## Files to Read
- prisma/schema.prisma or equivalent ORM schema
- migrations/ directory (all migration files)
- SQL files in the project (*.sql)
- Seed files (reveal data shape and volume expectations)
- Any file defining indexes explicitly

## Output Format
For each finding:
- **Impact**: CRITICAL / HIGH / MEDIUM / LOW
- **Table/Column**: affected table and columns
- **Problem**: what's wrong and the performance implication
- **Fix**: exact SQL or schema change
- **Estimated Impact**: query speed improvement, disk savings, or write overhead trade-off
```

---

### Agent 3: API & Middleware (Claude Subagent)

```
You are a backend performance expert specialized in API DESIGN and MIDDLEWARE PERFORMANCE.

Investigate the API layer for bottlenecks: slow endpoints, middleware overhead, response
payload problems, missing async patterns, and architecture-level issues.

## Stack Profile
{STACK_PROFILE}

## Your Investigation Checklist (12 points)

### Endpoint Performance
1. **Sequential awaits (request waterfalls)** — Multiple independent async operations
   awaited one after another instead of in parallel:
   ```
   const user = await getUser(id)          // 50ms
   const orders = await getOrders(userId)   // 80ms
   const notifications = await getNotifs()  // 40ms
   // Total: 170ms sequential
   ```
   Fix: `Promise.all([getUser(id), getOrders(userId), getNotifs()])` → 80ms parallel

2. **Over-fetching in API responses** — Endpoints returning full entity objects when
   clients need only a subset. Wastes serialization time, bandwidth, and DB work.
   - Check for endpoints returning >10KB JSON responses
   - Look for nested objects included by default

3. **Missing response streaming** — Large list endpoints that buffer the entire response
   in memory before sending. Should stream for >1000 items.

4. **Sync-heavy request handlers** — CPU-intensive operations blocking the event loop:
   - JSON parsing of huge payloads
   - Image processing / PDF generation in the request cycle
   - Complex regex on user input
   - Cryptographic operations (bcrypt rounds too high, sync crypto methods)
   - Fix: offload to worker threads, background jobs, or queues

5. **Missing request validation at the edge** — Validation happening deep in the service
   layer after expensive operations. Validate input FIRST (zod, joi, ajv) to fail fast.

### Middleware Chain
6. **Heavy middleware on every route** — Auth checks, logging, rate limiting running on
   routes that don't need them (public endpoints, health checks, static assets).
   - Fix: selective middleware application per route group

7. **Middleware doing database queries on every request** — Session lookup, permission
   checks, or feature flag fetching that hits the DB per request without caching.

8. **Missing compression** — Responses >1KB sent without gzip/brotli compression.
   Check for `compression` middleware in Express or equivalent.

### Background Processing
9. **Missing queue for heavy operations** — Expensive tasks done synchronously in the
   request cycle when they should be queued:
   - Email sending
   - Webhook delivery
   - Report generation
   - Image/video processing
   - Third-party API calls with retries

10. **Missing retry logic with backoff** — External API calls that fail silently or
    retry immediately in a tight loop without exponential backoff.

### Error & Timeout Handling
11. **Missing timeouts on external calls** — HTTP requests to third-party APIs without
    timeout configuration. A slow upstream can cascade and exhaust your connection pool.
    - Fix: set explicit timeouts (5-10s for APIs, 30s max for file downloads)

12. **Error responses leaking internals** — Stack traces, SQL queries, or internal paths
    exposed in error responses. Both a security AND performance debugging issue
    (noisy logs, no structured error codes for client retry logic).

## Files to Read
- API route handlers (src/api/**, app/api/**/route.ts, src/routes/**)
- Middleware files (src/middleware/**, middleware.ts)
- Server entry point (src/server.ts, src/index.ts, src/app.ts)
- Queue/job definitions (src/jobs/**, src/workers/**)
- Error handling (src/lib/errors.*, src/utils/error-handler.*)

## Output Format
For each finding:
- **Impact**: CRITICAL / HIGH / MEDIUM / LOW
- **File:Line**: exact location
- **Problem**: what's wrong and the latency/throughput impact
- **Fix**: concrete code change with before/after
- **Estimated Impact**: ms saved per request, throughput gained, or reliability improvement
```

---

### Agent 4: Caching & Connection Management (Claude Subagent)

```
You are a backend performance expert specialized in CACHING STRATEGIES and CONNECTION MANAGEMENT.

Investigate the codebase for missing caching layers, connection pool misconfigurations,
resource leaks, and infrastructure-level bottlenecks.

## Stack Profile
{STACK_PROFILE}

## Your Investigation Checklist (14 points)

### Connection Pooling
1. **Pool size misconfiguration** — Default pool sizes are often too small or too large.
   Rules of thumb:
   - Pool size = (CPU cores * 2) + effective_spindle_count (for physical disks)
   - Serverless: pool size 1-5 per function instance, use external pooler (PgBouncer, Supabase pooler)
   - Too small: requests queue waiting for connections → timeouts
   - Too large: DB overwhelmed with connections → OOM, context switching overhead

2. **Multiple connection pool instances** — Creating ORM client / pool in module scope
   per file or per request instead of sharing a singleton.
   - Prisma: multiple `new PrismaClient()` calls
   - Knex: multiple `knex({...})` instances
   - pg: multiple `new Pool()` instances
   - Fix: single instance in a shared module, imported everywhere

3. **Connection leaks** — Connections acquired but not released:
   - `pool.connect()` without matching `client.release()` in error paths
   - Transactions not committed/rolled back on error
   - Long-lived connections not returning to pool (missing `idle_timeout`)

4. **Missing connection pooler for serverless** — Direct DB connections from Lambda/Edge
   Functions without PgBouncer, Supabase pooler, or Neon's connection pooler.
   Each invocation opens a new connection → pool exhaustion at scale.

### Caching Strategy
5. **No caching layer** — Read-heavy data fetched from DB on every request without any
   caching. Look for:
   - Configuration/settings queries on every request
   - User profile/permissions fetched per API call
   - Static reference data (countries, categories, plans) queried per request
   - Fix: in-memory cache (node-cache, lru-cache), Redis, or HTTP cache headers

6. **Cache without invalidation strategy** — Cache set but never cleared when data changes.
   Stale data served indefinitely.
   - Check for `cache.set()` without corresponding `cache.del()` on mutations
   - Fix: TTL-based expiry + event-based invalidation on writes

7. **Cache stampede risk** — When cache expires, all concurrent requests hit the DB
   simultaneously to rebuild it.
   - Fix: stale-while-revalidate pattern, mutex/lock on cache rebuild, probabilistic early expiry

8. **Missing HTTP cache headers** — API responses for stable data without `Cache-Control`,
   `ETag`, or `Last-Modified` headers. The CDN and browser can't cache anything.
   - Check: `GET` endpoints for public/semi-static data

9. **Caching too much or wrong things** — Caching highly dynamic data with long TTL
   (serving stale), or caching user-specific data in shared cache (data leaks).

### Resource Management
10. **Missing rate limiting** — Public API endpoints without request throttling. A single
    client can exhaust DB connections and server resources.
    - Check for rate-limit middleware on auth endpoints (login, register, password reset)
    - Check for per-user limits on data-heavy endpoints

11. **Memory leaks in long-running processes** — Patterns that accumulate memory:
    - Growing Maps/Sets/arrays that are never pruned
    - Event listeners registered but never removed
    - Closures capturing large objects in long-lived scopes
    - Streams not properly destroyed on error

12. **Missing graceful shutdown** — Server not draining connections and finishing in-flight
    requests on SIGTERM. Check for `process.on('SIGTERM', ...)` handler that:
    - Stops accepting new connections
    - Waits for in-flight requests to complete
    - Closes DB pools and Redis connections
    - Exits cleanly

### Observability Gaps
13. **No query logging/monitoring** — No way to identify slow queries in production.
    Check for:
    - Prisma: `log: ['query']` or Prisma Optimize
    - pg: `log_min_duration_statement` in PostgreSQL config
    - Application-level query timing middleware

14. **Missing health check endpoint** — No endpoint that verifies DB connectivity, Redis
    availability, and service health for load balancers and monitoring.
    - Should check: DB ping, Redis ping, disk space, memory usage

## Files to Read
- Database client initialization (src/lib/db.*, src/lib/prisma.*, src/db/*)
- Redis/cache client initialization (src/lib/redis.*, src/lib/cache.*)
- Environment config (.env.example, config files)
- Server startup file (src/server.ts, src/index.ts)
- Middleware chain (src/middleware/**)
- Docker/deployment config (docker-compose.yml, Dockerfile)

## Output Format
For each finding:
- **Impact**: CRITICAL / HIGH / MEDIUM / LOW
- **File:Line or Config**: exact location
- **Problem**: what's wrong and the failure mode under load
- **Fix**: concrete change with before/after
- **Estimated Impact**: connections saved, cache hit rate, or failure prevention
```

---

### Agent 5: Codex External Validation (Codex CLI)

**Pre-check:** Verify Codex is available: `command -v codex >/dev/null 2>&1`
If Codex is NOT available, launch a fifth Claude subagent (Agent tool, general-purpose) with the same prompt below.

**If Codex is available**, run:

```bash
codex -a never exec "You are a backend and database performance auditor performing an independent deep investigation.

Analyze this codebase for ALL backend and database performance bottlenecks. Be thorough and critical.

Focus areas:
1. Query patterns — N+1, unbounded SELECTs, missing pagination, SELECT *, sequential queries
2. Schema & indexes — missing indexes on FKs and WHERE columns, wrong types, missing constraints
3. API layer — sequential awaits, over-fetching, missing validation, sync-heavy handlers
4. Caching — missing cache layers, no invalidation, no HTTP cache headers
5. Connections — pool sizing, leaks, missing pooler for serverless, multiple instances
6. Transactions — long-running, missing where needed, deadlock risks, external calls inside tx
7. Resource management — memory leaks, missing graceful shutdown, no rate limiting
8. Architecture — synchronous work that should be queued, missing background jobs, blocking event loop

Stack: {STACK_SUMMARY}

Read package.json, ORM schema, migration files, API handlers, services, and config files.
For each finding report: Impact (CRITICAL/HIGH/MEDIUM/LOW), File:Line, Problem, Fix, Estimated Impact.
End with a priority-ranked top 10 list of fixes by expected impact at scale."
```

**Fallback:** If Codex is unavailable (detected via `command -v codex`), launch a fifth Claude subagent with the same prompt.

## Step 2: Merge, Deduplicate & Cross-Reference

Once all 5 agents return:

1. **Collect** all findings into a single list
2. **Deduplicate** — Same table/file, same issue from multiple agents:
   - Keep the most detailed version
   - Tag: `[Confirmed by 2/5]`, `[Confirmed by 3/5]`, etc.
   - Cross-validated findings get **boosted priority**
3. **Cross-reference** — Link related findings across domains:
   - Missing index (Agent 2) explains slow query (Agent 1)
   - No caching (Agent 4) explains high DB load (Agent 1)
   - Sequential awaits (Agent 3) combined with N+1 (Agent 1) = multiplicative problem
4. **Unique findings** — Tag with source agent

## Step 3: Impact-Prioritized Report

### Output Format

```markdown
# Backend & Database Performance Audit

**Project:** {name}
**Stack:** {runtime} + {framework} + {ORM} + {DB engine}
**Agents:** 5-agent parallel (Query/ORM, Schema/Indexing, API/Middleware, Caching/Connections, Codex)

---

## Executive Summary

**Critical bottlenecks found:** {N}
**Estimated queries eliminable:** ~{N} per request cycle
**Quick wins (< 30min each):** {N}

### Top 5 Fixes by Impact
1. {Fix} — {estimated improvement} — {file/table}
2. ...

---

## Detailed Findings

### CRITICAL ({count})
> Must fix. Causes timeouts, data loss, or cascading failures under load.

#### 1. [{Domain}] Issue Title
**Impact:** CRITICAL | **Source:** [Query Agent] [Confirmed by 3/5]
**File:** `src/services/orderService.ts:87`
**Problem:** N+1 query inside a loop fetching order items per order
**Current:**
```typescript
const orders = await prisma.order.findMany()
for (const order of orders) {
  order.items = await prisma.orderItem.findMany({ where: { orderId: order.id } })
}
```
**Optimized:**
```typescript
const orders = await prisma.order.findMany({
  include: { items: true },
  relationLoadStrategy: 'join',
})
```
**Estimated Impact:** Reduces 101 queries to 1 query for 100 orders. ~200ms → ~5ms.

---

### HIGH ({count})
...

### MEDIUM ({count})
...

### LOW ({count})
...

---

## Schema Health Summary

| Table | Rows (est.) | Missing Indexes | Type Issues | Partitioning Candidate |
|-------|------------|-----------------|-------------|----------------------|
| orders | 500K+ | FK: user_id | - | No |
| events | 10M+ | composite: user_id, created_at | timestamp → timestamptz | Yes (by month) |
| ... | ... | ... | ... | ... |

## Connection & Caching Summary

| Resource | Current Config | Recommended | Issue |
|----------|---------------|-------------|-------|
| DB Pool | default (10) | 20 (4 cores) | Under-provisioned |
| Redis | not configured | Add for sessions, config | No caching layer |
| ... | ... | ... | ... |

## Fix Roadmap

### Sprint 1: Quick Wins (< 30min each)
- [ ] Add missing indexes on foreign keys
- [ ] Fix N+1 queries with includes/joins
- [ ] Add LIMIT to unbounded queries
...

### Sprint 2: Medium Effort (1-4h each)
- [ ] Implement cursor pagination replacing OFFSET
- [ ] Add Redis caching layer for hot data
- [ ] Set up connection pooler for serverless
...

### Sprint 3: Architecture Changes (> 4h)
- [ ] Offload heavy operations to background queues
- [ ] Partition large tables
- [ ] Add materialized views for complex aggregations
...

## Cross-Validation Summary
- {N} findings confirmed by 3+ agents (highest confidence)
- {N} findings confirmed by 2 agents
- {N} findings from single agent (review recommended)
```

## Step 4: Present & Act

1. Present the full report
2. Offer to start fixing:
   - "Want me to tackle the quick wins now? I can add the missing indexes and fix N+1s."
   - "Want me to generate the migration files for schema changes?"
   - "Want me to set up the caching layer?"
3. If the user wants fixes, work through the roadmap in priority order

## Scope Modes

| Mode | Trigger | Agents | Focus |
|------|---------|--------|-------|
| **Full audit** | "full backend audit", "find all bottlenecks" | All 5 | Everything |
| **Quick scan** | "quick db check", "any obvious query issues?" | Agents 1+2 only | Queries + schema |
| **Focused** | "check caching", "review indexes", "audit API layer" | Relevant agent only | Single domain |

## When to Read Memory Bank

**Always read if available.** The memory-bank dramatically improves the audit:

- `tech-context.md` tells you the exact DB engine, ORM, and hosting (skip detection)
- `system-patterns.md` reveals data flow, API architecture, queue setup
- `product-context.md` reveals which features are highest-traffic (audit those first)
- `active-context.md` reveals recent changes (likely source of new regressions)

## DB Engine-Specific Notes

### PostgreSQL
- Check for `pg_stat_statements` availability (slow query log)
- Partial indexes are powerful — use for soft-delete patterns
- BRIN indexes for time-series tables (100x smaller than B-tree)
- `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` for detailed query plans

### MySQL
- Check `innodb_buffer_pool_size` (should be ~70-80% of available RAM)
- No partial indexes — use generated columns + index instead
- `FORCE INDEX` hints if optimizer chooses wrong plan
- Check for MyISAM tables that should be InnoDB

### MongoDB
- Check for missing indexes on query fields (`explain("executionStats")`)
- Look for `$lookup` (join) in aggregation pipelines — expensive at scale
- Check for unbounded `find()` without `limit()`
- Schema design: embedding vs referencing decision review

### SQLite
- Only relevant for dev/small deployments
- Check WAL mode enabled for concurrent reads
- Single-writer limitation — no connection pool needed
