---
name: review-changes
description: |
  Production-grade code reviewer that audits all changes made during a session or between two points
  in git history. Dispatches 3 parallel agents (code quality, security/performance, and Codex external
  validation) to produce a unified review report with severity-based findings.
  With --fix flag, automatically fixes all CRITICAL and HIGH issues after review.
  Use when the user says "review changes", "review what we did", "milestone review", "audit changes",
  "check my work", "review session", "code review", "review-changes", "auto-fix", "fix my code",
  or wants a quality gate before committing, pushing, or creating a PR.
  Also trigger when the user asks to "validate the code", "check for issues", or "review before merge".
version: 1.0.0
category: development
depends: [observability-audit, feature-context]
---

# Review Changes — Milestone Reviewer

Production-grade code review that dispatches 3 parallel agents to audit all changes made
during a session. Combines internal Claude analysis with external Codex validation for
cross-engine confidence.

## Flags

- **`--fix`** — After generating the review report, automatically fix all CRITICAL and HIGH issues.
  Groups fixes by category and commits them. If invoked as `/review-changes --fix`, the skill
  reviews first, then applies fixes without asking for confirmation.
  Also trigger `--fix` when the user says "auto-fix", "fix my code", "clean up my code",
  "fix issues", or "fix and review".

## Why 3 Agents

Single-pass reviews have blind spots. By splitting concerns across specialized agents and
adding an external engine (Codex), we get:

- **Deeper analysis** — each agent focuses on its domain instead of rushing through everything
- **Cross-validation** — when Claude and Codex agree on an issue, confidence is high
- **Speed** — parallel execution means 3x the coverage in ~1x the time

## The Flow

```
User triggers review
        |
        v
[0] Scope Detection — git diff to determine what changed
        |
        v
[1] Parallel Dispatch ─────┬──── Agent 1: Code Quality & Patterns (Claude)
        |                   ├──── Agent 2: Security & Performance (Claude)
        |                   └──── Agent 3: External Validation (Codex CLI)
        v
[2] Merge & Deduplicate findings
        |
        v
[3] Severity Classification & Report
        |
        v
[4] Present to User with Action Items
        |
        v (only if --fix)
[5] Auto-Fix — apply fixes for CRITICAL and HIGH issues, commit grouped by category
```

## Step 0: Scope Detection

Determine what to review:

1. **Detect the default branch** (do NOT hardcode `main`):
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   if [ -z "$DEFAULT_BRANCH" ]; then
     if git show-ref --verify --quiet refs/remotes/origin/main 2>/dev/null; then
       DEFAULT_BRANCH="main"
     elif git show-ref --verify --quiet refs/remotes/origin/master 2>/dev/null; then
       DEFAULT_BRANCH="master"
     fi
   fi
   ```
2. Run `git diff --staged` and `git diff` to capture all current changes
3. If no changes exist, check recent commits with `git log --oneline -10` and ask the user
   which range to review (e.g., "last 3 commits", "since branch diverged from $DEFAULT_BRANCH")
4. Once the scope is clear, collect the full diff:
   - For uncommitted changes: `git diff` + `git diff --staged`
   - For commit range: `git diff <base>..<head>`
   - For branch review: `git diff $DEFAULT_BRANCH...HEAD`
4. Also list all changed files with `git diff --name-only <range>` to give agents file context
5. Read surrounding code for changed files — agents need full file context, not just diffs

Save the diff output and file list — all 3 agents receive the same input.

## Step 1: Parallel Agent Dispatch

Launch all 3 agents simultaneously using the Agent tool. Each receives:
- The full diff
- The list of changed files
- Instructions specific to their review domain

### Agent 1: Code Quality & Patterns (Claude Subagent)

Prompt the Agent tool (general-purpose) with:

```
You are a senior code reviewer focused on CODE QUALITY and PATTERNS.

Review the following changes and report issues organized by severity.
Only report findings where you are >80% confident of a genuine issue.
Do NOT report stylistic preferences unless they violate project conventions.

## Your Checklist (37 points)

**Architecture & Design:**
1. DRY violations — duplicated logic that should be extracted
2. Single Responsibility — functions/files doing too much (>50 lines / >800 lines)
3. Dead code — unused imports, unreachable branches, commented-out code
4. Prop drilling — props passed through 3+ levels (suggest context/composition)
5. Naming — misleading names, single-letter vars in complex contexts, magic numbers
6. Enum usage — multiple type values should use enums, not string literals or arrays
7. Centralized constants — shared facts imported from shared modules, not redeclared
8. Shared schemas — validation schemas defined once and reused, not duplicated
9. Refactoring completeness — if renamed/changed, all call sites updated, no stale references
10. Single source of truth — no duplicated type definitions or validation rules
11. Reuse existing code — search for existing hooks/utils/constants before creating new ones

**Type Safety & Data:**
12. Type correctness — any types, missing null checks, unsafe casts
13. Immutability — direct mutation where spread/map/filter is safer
14. Error handling — empty catch blocks, unhandled promise rejections, swallowed errors
15. Error handling fidelity — error types match actual failure mode, messages include context
16. Zod nullability — explicit null/undefined handling, no truthy/falsy traps hiding 0 or ""
17. Collection key collision — unique keys for iterable elements, no array indices when items reorder
18. Nullish coalescing — use `??` instead of `||` for defaults when `0` or `""` are valid values

**Framework Patterns (React/Next.js):**
19. useEffect dependency arrays & cleanup — missing or incorrect dependencies. **All timeouts, intervals, event listeners, and subscriptions created inside effects MUST be cleaned up in the return function** (e.g. `clearTimeout`, `clearInterval`, `removeEventListener`). Flag any `setTimeout`/`setInterval`/`addEventListener` inside a useEffect without a corresponding cleanup.
20. Render-phase state updates — setState during render causing loops
21. List keys — array index as key when items can reorder
22. Client/Server boundary — useState/useEffect in Server Components
23. Closure staleness — event handlers capturing outdated state
24. Modal/dialog UX — forms in modals implement unsaved changes warnings
25. Form patterns — react-hook-form + zod for all forms, no manual validation
26. Fixed navigation — use explicit routes instead of `router.back()` (breaks with multi-page flows)
27. Explicit component props — specify `variant` and similar props explicitly, don't rely on defaults

**Structural Quality:**
28. Module cohesion — files contain related functionality, not grab-bag utils
29. Discoverability — public APIs well-named, file/directory names match purpose
30. Flat is better than nested — max 2 levels of indentation, use guard clauses and early returns
31. Function argument discipline — max 2 required args; 3+ use options object; no boolean flag args
32. Hardcoded colors — extract to CSS variables or design token constants
33. Hardcoded API routes — extract to route constants

**Transaction & Data Integrity:**
34. Minimize transaction hold time — no external I/O (HTTP, queues, S3), heavy computation, or long awaits inside DB transactions
35. Terminal states are sticky — status updates check current state before overwriting; terminal states protected from regression
36. Write-then-read — after create/update/upsert, use the returned record instead of re-fetching (avoids replication lag)
37. Simple locking — default to standard transaction isolation; avoid SERIALIZABLE for simple upserts; bounded retries with backoff

**Observability & Debuggability:**
38. Failure-path context — new error paths include enough domain context (IDs, operation, state) to debug the failing operation without adding logs after the fact
39. Error taxonomy — code distinguishes expected/user/dependency failures from invariant bugs where the stack supports it (typed errors, error codes, is_transient flags)
40. Async boundary visibility — new jobs/webhooks/workers expose stable IDs and explicit start/success/failure/dead-letter states

## Changed Files:
{FILE_LIST}

## Diff:
{DIFF}

For each finding, report:
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW
- **File:Line**: exact location
- **Issue**: what's wrong
- **Fix**: concrete suggestion with code if applicable

End with a summary count by severity.
```

### Agent 2: Security & Performance (Claude Subagent)

Prompt the Agent tool (general-purpose) with:

```
You are a senior code reviewer focused on SECURITY and PERFORMANCE.

Review the following changes and report issues organized by severity.
Only report findings where you are >80% confident of a genuine issue.
Skip unchanged code unless it has CRITICAL security vulnerabilities.

## Your Checklist (20 points)

**Security (CRITICAL priority):**
1. Hardcoded credentials — API keys, passwords, tokens, connection strings in source
2. SQL injection — string concatenation in queries instead of parameterized queries
3. XSS — unescaped user input rendered in HTML/JSX
4. Path traversal — user-controlled file paths without sanitization
5. CSRF — state-changing endpoints without CSRF tokens
6. Auth bypass — protected routes missing auth checks
7. Sensitive data in logs — tokens, passwords, PII in log statements
8. Output sanitization — user-controlled data escaped before rendering or logging

**Performance:**
9. N+1 queries — loop-based data fetching instead of JOINs/batch operations (check for DB calls inside loops)
10. Algorithm efficiency — O(n²) when O(n log n) or O(n) exists
11. Missing memoization — expensive computations without useMemo/useCallback/React.memo
12. Bundle size — large library imports where tree-shakeable alternatives exist
13. Blocking operations — synchronous I/O in async contexts
14. Race conditions — concurrent state mutations, missing locks, stale closures in async flows
15. Bounded concurrency — Promise.all on unbounded arrays without concurrency limits
16. Unbounded IN clauses — SQL/ORM queries with user-controlled array sizes

**Patterns & Boundaries:**
17. Server/client import boundaries — server-only code not imported in client components
18. Form patterns — proper validation library usage, no manual validation in handlers
19. SDK/library documentation conformance — APIs used as documented, no deprecated methods
20. Test staleness — tests for changed code updated, no assertions on old behavior

**Observability:**
21. Structured logging — new boundary code (API handlers, queue consumers, external calls) emits structured logs with stable event names and severity, not console.log/print
22. Correlation propagation — request/job/trace IDs are preserved across service and async boundaries in new code
23. Sensitive data redaction — new logs/errors do not leak secrets, tokens, or PII (check for full request/response body logging)
24. Critical-path telemetry — new endpoints/jobs expose at least minimal success/failure/latency signals (metrics or structured logs)
25. Error tracking artifacts — production exceptions include release/environment metadata; frontend changes include source maps where applicable
26. Alertability — failures, retry exhaustion, or dead-letter outcomes in new code are externally observable, not silent

**Observability escalation:** If 1+ hard blocker (items 21-22 fail on critical path) or 2+ medium issues from items 23-26, recommend `/observability-audit` in the review report.

## Changed Files:
{FILE_LIST}

## Diff:
{DIFF}

For each finding, report:
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW
- **File:Line**: exact location
- **Issue**: what's wrong
- **Fix**: concrete suggestion with code if applicable

End with a summary count by severity.
```

### Agent 3: External Validation (Codex CLI)

First, check if Codex CLI is available: `command -v codex >/dev/null 2>&1`

**If Codex is available**, use Bash to run:

**Security: NEVER interpolate diff content or file lists directly into shell command strings.**
Always write the diff to a temp file and use a single-quoted heredoc for the prompt:

```bash
DIFF_FILE=$(mktemp /tmp/review-diff-XXXXXX.txt)
trap "rm -f $DIFF_FILE" EXIT
git diff <range> > "$DIFF_FILE"

cat <<'PROMPT_EOF' | codex -a never exec -
You are a code reviewer performing an independent audit. Review the changes in
the file referenced below for correctness, completeness, and potential issues.
Be critical — flag anything that looks wrong, fragile, or could cause bugs in production.

Focus on:
1. Logic errors and edge cases the author may have missed
2. Behavioral regressions — does this change break existing functionality?
3. Missing error handling at system boundaries (user input, external APIs)
4. Incomplete implementations — TODOs, placeholder code, half-finished features
5. Unintended side effects or hidden coupling between changed files
6. Input validation gaps at trust boundaries
7. Concurrency issues and data consistency

Read the diff from: <DIFF_FILE_PATH>

For each finding report: Severity (CRITICAL/HIGH/MEDIUM/LOW), File:Line, Issue, Fix suggestion.
End with a summary count.
PROMPT_EOF
```

Replace `<DIFF_FILE_PATH>` with the actual path returned by `mktemp`.

**If Codex is NOT available**, launch a third Claude subagent (Agent tool, general-purpose) with the same prompt. Label its findings as `[External Agent]` instead of `[Codex Agent]`.

## Step 2: Merge & Deduplicate

Once all 3 agents return:

1. **Collect** all findings into a single list
2. **Deduplicate** — if two or more agents flag the same issue (same file, same line, similar description):
   - Keep the most detailed version
   - Note cross-validation: `[Confirmed by 2/3 agents]` or `[Confirmed by all 3 agents]`
   - **Boost confidence** — cross-validated issues are almost certainly real
3. **Unique findings** — issues only one agent caught get tagged with their source:
   `[Quality Agent]`, `[Security Agent]`, or `[Codex Agent]`

## Step 3: Severity Classification & Report

Organize the unified findings into a structured report:

### Output Format

```markdown
# Code Review Report

**Scope:** {description of what was reviewed}
**Files reviewed:** {count}
**Review mode:** 3-agent parallel (Claude Quality + Claude Security + Codex Validation)
**Fix mode:** {enabled / disabled}

---

## CRITICAL ({count})
> Issues that MUST be fixed before merge. Security vulnerabilities, data loss risks, crash bugs.

### 1. [File:Line] Issue Title
**Source:** [Quality Agent] [Confirmed by 2/3 agents]
**Issue:** Description
**Fix:**
```suggestion
code fix here
```

---

## HIGH ({count})
> Issues that SHOULD be fixed. Bugs, missing error handling, performance problems.

...

## MEDIUM ({count})
> Code quality issues. DRY violations, naming, missing types.

...

## LOW ({count})
> Best practices, documentation, minor improvements.

...

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | X     | BLOCK  |
| HIGH     | X     | WARN   |
| MEDIUM   | X     | INFO   |
| LOW      | X     | NOTE   |

### Verdict: {APPROVE / WARN / BLOCK}
- **APPROVE** — No CRITICAL or HIGH issues
- **WARN** — HIGH issues present (conditional approval)
- **BLOCK** — CRITICAL issues detected, must fix before merge

### Cross-Validation Confidence
- {N} issues confirmed by multiple agents (high confidence)
- {N} issues from single agent (review recommended)
```

## Step 4: Present & Act

1. Present the full report to the user
2. If `--fix` flag is **NOT** set:
   - If verdict is **BLOCK** or **WARN**, offer to fix: "Want me to fix the CRITICAL/HIGH issues now?"
   - If verdict is **APPROVE**, confirm: "Changes look good. Ready to commit/push/PR."
3. If `--fix` flag **IS** set, proceed directly to Step 5.

## Step 5: Auto-Fix (only with --fix flag)

When `--fix` is active, apply fixes for all CRITICAL and HIGH severity findings:

1. **Read each affected file** in full before making changes
2. **Apply fixes** using the Edit tool — one finding at a time, verifying each fix
3. **Group and commit** fixes by category:
   ```bash
   git add <files>
   git commit -m "refactor: <category description> (review-changes --fix)"
   ```
4. **Re-validate** — after all fixes, run a quick single-agent pass on the changed files
   to confirm no regressions were introduced
5. **Report** — append a fix summary to the review report:
   ```
   ## Auto-Fix Summary
   - {N} CRITICAL issues fixed
   - {N} HIGH issues fixed
   - {N} issues skipped (require manual intervention — listed below)
   ```

### Fix Philosophy: Obvious Code

When applying fixes, prefer simple and verbose over complex and clever:
- A 3-line `if/else` is better than a clever ternary with side effects
- Named constants are better than inline numbers, even if "obvious"
- An options object with named fields is better than positional boolean args
- Explicit `=== null` is better than relying on falsy coercion that hides `0` and `""`
- A function that does one thing and says so in its name is better than one that secretly does two

### What NOT to auto-fix

Skip these and mark as "requires manual intervention":
- Findings where the fix would change public API contracts
- Findings that require architectural decisions (e.g., "split this into microservices")
- Findings where the correct fix is ambiguous (multiple valid approaches)
- Findings in generated code or third-party vendored files

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/review/`
- **Checkpoint frequency:** After Step 2 (merge & deduplicate findings)
- **Subagent delegation:** All 3 review agents (Step 1), re-validation after auto-fix (Step 5)

## When to Skip Agents

- If changes are < 20 lines, use a single Claude subagent with the combined checklist instead of 3 parallel agents
- If the user says "quick review", skip Agent 3 (Codex) and merge findings from Agents 1 & 2 only
- If Codex is unavailable, automatically fall back to a third Claude subagent

## Confidence Filtering Rules

These apply to ALL agents:

- Only report findings with >80% confidence of a genuine issue
- Do NOT flag stylistic preferences unless they violate project conventions
- Skip unchanged code issues unless they are CRITICAL security concerns
- Consolidate similar findings — don't list the same pattern 5 times across 5 files
- Prioritize bugs, security vulnerabilities, and data loss risks over style

---

## Feature Context Integration

When a feature-context is active, this skill writes review findings:

1. **After review completes:** Write the severity summary (CRITICAL/HIGH/MEDIUM/LOW counts) to feature-context
2. **After auto-fix:** Write which issues were auto-fixed and which remain
3. **Data written:** finding count by severity, files reviewed, auto-fix results, escalation decisions (e.g. to observability-audit)
