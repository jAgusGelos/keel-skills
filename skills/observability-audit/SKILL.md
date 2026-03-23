---
name: observability-audit
description: |
  Deep production observability and debuggability auditor. Answers the question: "If this fails
  at 2 AM, can an engineer quickly determine what failed, where, for whom, since which release,
  and what to do next?" Dispatches 3 parallel agents (critical path coverage, telemetry quality,
  operability) across a tiered checklist — core blockers, coverage checks, and maturity checks.
  Works for any tech stack. Use when the user says "observability audit", "debuggability review",
  "check observability", "are we logging enough", "production debugging", "can we debug this",
  "make this debuggable", "audit logging", "check our traces", "tracing coverage", "SLO review",
  "alert quality", "monitoring audit", "error tracking review", "check our metrics",
  "observability gaps", "is this debuggable", "production readiness", "can we diagnose failures",
  "correlation IDs", "context propagation", "are our alerts good", "MTTR review",
  "blind spots in monitoring", "we had an outage and couldn't debug", "error visibility",
  "I need good logs", "on-call visibility", "incident readiness", "OpenTelemetry audit",
  "structured logging check", or wants to ensure their system is diagnosable in production.
version: 1.0.0
category: development
depends: [memory-bank, three-experts, review-changes]
---

# Observability Audit — Deep Debuggability Investigator

Code that works but cannot be debugged in production is a liability. This skill audits whether
a system is **diagnosable**, **monitorable**, and **actionable** when things go wrong.

**Core question:** Can we diagnose and act on failures in the top critical production paths?

Every finding must be **actionable** — file path, line number, what is missing, how to add it,
and the debugging scenario it enables. No vague advice like "add more logging."

## Philosophy

The canonical 3 pillars of observability:
- **Logs** tell you what happened
- **Metrics** tell you how much, how often, and whether the system is degrading
- **Traces** tell you where time and errors flowed across boundaries

Plus the cross-cutting pieces that make them useful in production:
- **Context propagation** — correlation IDs, trace context across async boundaries
- **Error tracking** — centralized capture with grouping, breadcrumbs, release metadata
- **Alertability** — symptom-based alerts with ownership and runbooks
- **Incident readiness** — can on-call reconstruct a timeline and determine blast radius?

OpenTelemetry is the default standard for naming, propagation, and correlation. The skill is
vendor-neutral — it works whether the project exports to Sentry, Datadog, Grafana, Honeycomb,
CloudWatch, New Relic, or a self-hosted stack.

## The Flow

```
User triggers observability audit
         |
         v
[0] Context & Stack Detection
         |
         v
[1] Critical Path Mapping
         |
         v
[2] Parallel Investigation ──┬── Agent 1: Critical Path Coverage
         |                    ├── Agent 2: Telemetry Quality
         |                    └── Agent 3: Operability
         v
[3] Merge, Deduplicate & Score
         |
         v
[4] Present Observability Audit Report
```

## Scope Modes

| Mode | Trigger | What happens |
|------|---------|--------------|
| **Full** | "full observability audit", "audit all monitoring" | All 3 agents, full checklist |
| **Quick** | "quick observability check", "any logging gaps?" | Single critical path, core blockers only (cross-pillar) |
| **Focused** | "check our tracing", "review SLOs", "audit alerts" | Single agent on the relevant pillar |

**Quick mode** audits minimum production diagnosability of ONE critical path across all pillars:
structured logs with correlation IDs, top-path error capture, golden-signal metrics, at least
one actionable alert, and ownership/runbook pointer.

## Step 0: Context & Stack Detection

Before dispatching agents, understand the observability posture:

1. **Read memory-bank** (if available — this is optional, skill works without it):
   - `memory-bank/tech-context.md` — stack, hosting, infra
   - `memory-bank/system-patterns.md` — architecture, API patterns
   - `memory-bank/active-context.md` — current focus

2. **Detect observability stack** by scanning dependencies and config:
   ```
   Logging:    winston/pino/bunyan (Node) | structlog/loguru (Python) | zap/zerolog/slog (Go) | slf4j/logback (Java) | tracing/env_logger (Rust)
   Metrics:    prom-client/@opentelemetry/* (Node) | prometheus_client (Python) | prometheus/client_golang (Go) | micrometer (Java)
   Tracing:    @opentelemetry/sdk-trace-* | dd-trace | jaeger-client | zipkin
   Errors:     @sentry/* | @bugsnag/* | @datadog/* | newrelic | @honeycombio/*
   Infra:      docker-compose.yml (Grafana/Prometheus/Jaeger/Loki), k8s configs, CI/CD
   ```

   **Security:** NEVER read `.env`, `.env.local`, `.env.production`, or any env file containing real credentials. Only read `.env.example` or `.env.sample`. When reporting findings about connection strings or credentials, show the pattern and location, not the actual value. When agents report findings about sensitive data in logs, redact actual secret values in the report. Show pattern and location, not the value.

3. **Detect execution model**: request/response service, SPA/SSR, workers/cron/queues, event-driven, CLI/batch

4. **Scan for observability artifacts**: centralized logger, metrics setup, tracing init, health endpoints, alert definitions, dashboards

5. **Build observability profile** — all agents receive this same context.

## Step 1: Critical Path Mapping

**Do not audit telemetry in the abstract.** Map the paths that matter first.

Select the top 3-5 critical paths using these criteria (highest combination wins):
- **User/business impact** — revenue, auth, core workflow
- **Failure frequency or uncertainty** — new code, complex logic, external dependencies
- **External dependency exposure** — third-party APIs, payment providers, AI calls
- **Operational pain / historical incidents** — paths that have caused outages before

For each critical path, trace the full journey: entry point → business logic → data access → external calls → response/outcome.

At minimum, audit **3 critical paths end-to-end** in Full mode, **1 path** in Quick mode.

## Step 2: Master Checklist (Tiered)

The checklist is organized in 3 tiers by operational impact. Only report findings that
materially affect production diagnosability.

### Tier 1: Core Blockers (must-have for any production system)

These gaps mean you **cannot debug failures** in the affected paths.

1. **No centralized structured logger** — log calls use console.log/print/fmt.Println with free-text messages that cannot be parsed, searched, or correlated
2. **Swallowed errors** — empty catch blocks, catch-and-ignore, promises without .catch(), unhandled rejections not captured
3. **No error tracking service** — errors only appear in stdout with no aggregation, grouping, or alerting
4. **No correlation ID propagation** — requests/jobs have no ID linking logs, traces, and errors for the same operation
5. **Missing system boundary logging** — HTTP requests to external services, queue publishes, DB operations without logging outcome/duration/failure
6. **No health check endpoint** — no /health or /healthz verifying DB, cache, and critical dependency connectivity
7. **Sensitive data in logs/errors** — PII, tokens, passwords, API keys appearing in log statements or error reports
8. **No alerts defined** — metrics may exist but nobody is notified when things break; customers report incidents first
9. **Broken async context propagation** — trace/correlation context lost across queue publish/consume, background jobs, event handlers

### Tier 2: Coverage Checks (important for reliable incident response)

These gaps make incidents **slower to diagnose and resolve**.

10. **Missing log levels** — everything at INFO, errors logged as INFO, debug noise in production
11. **Missing log context** — log entries without request ID, user ID, service name, or operation context
12. **Missing operation outcome logging** — significant operations (API calls, DB writes, queue publishes) without success/failure logging
13. **Missing RED metrics** — service endpoints without Rate, Errors, Duration instrumentation
14. **Averages instead of percentiles** — response time as average hiding tail latency; no p50/p90/p95/p99
15. **No tracing setup** — cannot trace requests across service boundaries or identify bottleneck spans
16. **Auto-instrumentation only, no custom spans** — business logic is one opaque span; cannot identify which part is slow
17. **Missing span attributes** — spans without user ID, order ID, feature flag state, or business identifiers
18. **Errors not recorded on spans** — trace shows span succeeded when it caught and handled an error internally
19. **Missing error boundaries** — frontend: no ErrorBoundary; backend: no global error handler middleware
20. **Poor error classification** — all errors treated the same; no distinction between transient/permanent/bug
21. **Missing error context/breadcrumbs** — errors reported without the state that caused them
22. **Frontend-backend trace disconnection** — frontend errors not connected to backend traces
23. **Alert on causes not symptoms** — alerting on CPU > 80% instead of error rate exceeds SLO burn rate
24. **Missing alert severity** — all alerts same priority; no page-worthy vs ticket-worthy distinction
25. **Missing dependency health visibility** — no circuit breakers or health tracking for downstream services

### Tier 3: Maturity Checks (excellence for mature systems)

These improve **day-to-day debugging and operational posture**.

26. **No SLOs defined** — no formal definition of what "healthy" means; no error budgets
27. **SLOs without burn-rate tracking** — SLOs exist but no mechanism to track budget consumption
28. **Missing SLI instrumentation** — SLOs defined but metrics feeding them not collected or measured incorrectly
29. **Missing runbooks** — alerts fire with no documentation on what to check or how to mitigate
30. **Missing readiness probe** — no /ready endpoint; traffic arrives before service is initialized
31. **Missing sampling strategy** — either 100% sampling (expensive) or no config (may drop important traces)
32. **Trace-log disconnection** — logs and traces exist independently; cannot click a span and see its logs
33. **Missing service map** — no visibility into which services call which or failure propagation paths
34. **No trace-based testing** — tracing breaks silently; no test assertions verify spans are emitted correctly
35. **Missing audit trail** — state-changing operations with no record of who did what and when
36. **No error fingerprinting** — similar errors not grouped; same bug creates hundreds of separate issues
37. **Missing business metrics** — no visibility into orders/signups/conversions per minute
38. **Ownership metadata missing** — no clear owner for services, jobs, or alerts
39. **Change-event visibility missing** — deploys, migrations, feature flags, config changes not emitted as observable events
40. **No synthetic/canary checks** — no proactive verification of critical user journeys

## Step 2: Parallel Agent Dispatch

Launch all 3 agents simultaneously. Each receives the observability profile from Step 0,
the critical paths from Step 1, and their investigation focus.

---

### Agent 1: Critical Path Coverage

```
You are an observability expert focused on END-TO-END COVERAGE of critical production paths.

For each critical path identified in Step 1, trace the full journey and verify:
- Every boundary (HTTP, queue, DB, external API) has logging and timing
- Correlation context flows through the entire path without breaks
- Errors at any point are captured, classified, and surfaced
- The path emits enough metrics to detect degradation

Check Tier 1 items: 1-2, 4-5, 9
Check Tier 2 items: 12, 15-18, 22
Check Tier 3 items: 32-34

For every finding: file:line, what is missing, concrete fix, and the debugging scenario enabled.
Severity: CRITICAL / HIGH / MEDIUM / LOW
```

### Agent 2: Telemetry Quality

```
You are an observability expert focused on TELEMETRY QUALITY — logs, metrics, and error tracking.

Investigate the quality and completeness of the telemetry stack:
- Logging: structured? levels? context fields? redaction?
- Metrics: RED/USE patterns? histograms? business metrics? cardinality?
- Error tracking: centralized? grouped? breadcrumbs? release metadata? source maps?

Check Tier 1 items: 1, 3, 7
Check Tier 2 items: 10-11, 13-14, 19-21
Check Tier 3 items: 26-28, 35-37

For every finding: file:line, what is missing, concrete fix, and the debugging scenario enabled.
Severity: CRITICAL / HIGH / MEDIUM / LOW
```

### Agent 3: Operability

```
You are an observability expert focused on INCIDENT RESPONSE and OPERATIONAL READINESS.

Investigate whether the system supports rapid incident diagnosis and resolution:
- Can on-call reconstruct a timeline from telemetry?
- Can blast radius be determined by tenant/user/endpoint/region?
- Do alerts exist? Are they symptom-based with severity and ownership?
- Do runbooks exist? Do health/readiness probes work?
- Are deploys, migrations, and config changes observable events?

Check Tier 1 items: 6, 8
Check Tier 2 items: 23-25
Check Tier 3 items: 29-31, 38-40

For every finding: file:line or config path, what is missing, concrete fix, and the operational
scenario enabled.
Severity: CRITICAL / HIGH / MEDIUM / LOW
```

---

## Step 3: Merge, Deduplicate & Score

1. **Collect** all findings into a single list
2. **Deduplicate** — same file/same gap from multiple agents:
   - Keep the most detailed version
   - Tag: `[Confirmed by 2+ agents]` — cross-validated findings get boosted priority
3. **Cross-reference** — link related findings across agents:
   - Missing correlation ID (Agent 1) explains inability to join logs (Agent 2)
   - No alerts (Agent 3) combined with no metrics (Agent 2) = complete blind spot
4. **Score by tier**: Core Blockers found = CRITICAL/HIGH, Coverage gaps = MEDIUM/HIGH, Maturity gaps = MEDIUM/LOW

## Step 4: Output Format

```markdown
# Observability Audit Report

**Project:** {name}
**Stack:** {runtime} + {framework} + {observability tools detected}
**Critical paths audited:** {N}
**Mode:** {Full / Quick / Focused}

---

## Executive Verdict: {Diagnosable / Fragile / Opaque}

- **Diagnosable** — Core blockers resolved, coverage is solid, incidents can be triaged quickly
- **Fragile** — Some telemetry exists but significant gaps in correlation, alerting, or coverage
- **Opaque** — Major blind spots; production failures require adding logs after the incident starts

## Pillar Coverage

| Pillar                 | Status                     |
|------------------------|----------------------------|
| Structured Logging     | {Strong / Partial / Weak}  |
| Metrics & SLOs         | {Strong / Partial / Weak}  |
| Distributed Tracing    | {Strong / Partial / Weak}  |
| Error Tracking         | {Strong / Partial / Weak}  |
| Alertability           | {Strong / Partial / Weak}  |
| Incident Readiness     | {Strong / Partial / Weak}  |

## Core Blockers ({count})
> You cannot debug failures in these areas.

### 1. [CRITICAL] Issue Title
**File:** `path:line` or `Missing`
**Gap:** what is missing and the debugging scenario it blocks
**Fix:**
```suggestion
concrete code fix
```
**Debug scenario enabled:** "When X fails, you can now Y"

---

## Coverage Gaps ({count})
> Incidents will be slower to diagnose.
...

## Maturity Improvements ({count})
> Polish for operational excellence.
...

---

## Critical Debug Questions This System Cannot Yet Answer
1. "Which user was affected by this error?"
2. "How long has this been happening?"
3. "What changed right before this started?"
...

## DORA Impact Assessment (optional)
> How observability gaps affect delivery metrics.
- **Recovery time risk:** {assessment — e.g., "No correlation IDs means MTTR increases by ~Xh for cross-service issues"}
- **Change failure visibility:** {assessment}
- **Deployment regression detection:** {assessment}

---

## Recommended Actions

### Immediate Blockers (highest leverage)
- [ ] Fix 1 — what and why
- [ ] Fix 2

### Critical-Path Coverage
- [ ] Fix 3
- [ ] Fix 4

### Operational Maturity
- [ ] Fix 5
- [ ] Fix 6

## Cross-Validation Summary
- {N} findings confirmed by 2+ agents (highest confidence)
- {N} findings from single agent (review recommended)
```

After presenting the report:
1. Offer to start fixing: "Want me to set up the centralized logger and correlation ID middleware?"
2. Work through fixes in priority order if accepted
3. Suggest running `/review-changes` after implementing fixes to validate

## Integration with Other Skills (all optional)

These integrations enhance the audit but are NOT required. The skill works standalone.

- **Reads `memory-bank`** (if exists): Uses tech-context.md and system-patterns.md to detect stack faster
- **Invokes `three-experts`** (when needed): For architectural observability tradeoffs — sampling vs cost, vendor choice, high-cardinality label design, privacy vs diagnostic richness. Recommended preset: SRE + Backend Engineer + DevOps Engineer
- **Feeds `review-changes`**: Recurring code-level patterns discovered by the audit can be proposed as new checklist items via the standard promotion path

## Escalation from review-changes

When `review-changes` runs its lightweight observability checks and finds issues, use
**severity-weighted escalation**:
- **Any hard blocker** (Tier 1 fail) → recommend `/observability-audit` immediately
- **2+ medium issues** (Tier 2 fails) → recommend `/observability-audit --focused`
- **Low-signal cosmetic misses** → note in review, do not escalate

Path sensitivity matters: missing observability in a payment flow is not the same as missing
it in an internal admin screen.

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/observability-audit/`
- **Checkpoint frequency:** After Step 3 (merge & score findings)
- **Subagent delegation:** All 3 audit agents (Step 2)

## Success Criteria

Before presenting the final report, verify:
- [ ] Observability stack was detected and documented
- [ ] Critical paths were explicitly identified with selection rationale
- [ ] All 3 agents investigated actual source files, not just config
- [ ] Findings reference real file paths or explicitly state "Missing"
- [ ] Every finding includes a concrete fix with code example
- [ ] Every finding includes the debugging scenario it enables
- [ ] Executive verdict is justified by the findings
- [ ] Actions are organized by leverage (blockers → coverage → maturity)
- [ ] Cross-references between pillars are identified
