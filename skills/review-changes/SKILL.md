---
name: review-changes
description: |
  Production-grade two-stage code reviewer that audits all changes made during a session or between
  two points in git history. Stage 1 verifies spec/requirement compliance before Stage 2 dispatches
  4 parallel agents (architecture/types, framework/structure, security/performance, and Codex
  external validation) to produce a unified review report with severity-based findings.
  With --fix flag, automatically fixes all CRITICAL and HIGH issues after review.
  With --light flag, runs ONLY Agent 1A (Architecture/Design/Types) inside a single subagent,
  for fast per-milestone quality gates (used by /spec-first-cc-cc between milestones).
  Use when the user says "review changes", "review what we did", "milestone review", "audit changes",
  "check my work", "review session", "code review", "review-changes", "auto-fix", "fix my code",
  or wants a quality gate before committing, pushing, or creating a PR.
  Also trigger when the user asks to "validate the code", "check for issues", or "review before merge".
version: 1.1.0
category: development
depends: [observability-audit, feature-context]
---

# Review Changes — Two-Stage Milestone Reviewer

Production-grade two-stage code review. **Stage 1** checks whether the implementation matches
what was requested (spec compliance). **Stage 2** dispatches 4 parallel agents to audit
architecture/types, framework/structure, security/performance, and correctness. Combines
internal Claude analysis with external Codex validation for cross-engine confidence.

## Flags

- **`--fix`** — After generating the review report, automatically fix all CRITICAL and HIGH issues.
  Groups fixes by category and commits them. If invoked as `/review-changes --fix`, the skill
  reviews first, then applies fixes without asking for confirmation.
  Also trigger `--fix` when the user says "auto-fix", "fix my code", "clean up my code",
  "fix issues", or "fix and review".

- **`--light`** — Lightweight review mode. Runs **only Agent 1A (Architecture, Design & Types)**
  and skips Stage 1 (Spec Compliance) and all other Stage 2 agents (1B, 2, 3). Designed for
  fast per-milestone quality gates inside larger workflows (e.g. `/spec-first-cc-cc`) where
  a full 4-agent pass is overkill at each step.
  **Always dispatched via the Agent tool** — the entire light-mode review (including orchestration,
  report generation, and `--fix` application when combined) runs inside a single subagent so the
  main conversation context stays clean. See "Light Mode" below for the full contract.
  Combinable with `--fix` (e.g. `/review-changes --light --fix`) to also auto-fix CRITICAL/HIGH
  findings surfaced by Agent 1A. By default `--fix` targets CRITICAL/HIGH only; the caller's
  dispatch message may widen that scope (the `/spec-first` and `/spec-first-cc-cc` milestone
  gates override it to ALL severities — when a dispatch message specifies a scope, it wins).

## Why 5 Subagents

Full mode runs five subagents total: the Stage 1 spec-compliance reviewer plus the four
parallel Stage 2 agents (1A, 1B, 2, and Codex). Single-pass reviews have blind spots.
By splitting concerns across specialized agents and adding an external engine (Codex)
for independent validation, we get:

- **Deeper analysis** — each agent focuses on its domain instead of rushing through everything
- **Cross-validation** — when Claude and Codex agree on an issue, confidence is high
- **Speed** — parallel execution means 4x the coverage in ~1x the time

## The Flow

```
User triggers review
        |
        +--> [--light mode] --> Dispatch a single Agent tool subagent that runs
        |                        Agent 1A only (Architecture/Design/Types), builds
        |                        a light report, and — if --fix — applies fixes.
        |                        See "Light Mode" below.
        |
        v (default / full mode)
[0] Scope Detection — git diff to determine what changed
        |
        v
[0.5] Spec Source Detection — locate plan.md, issue, or task description
        |
        v
[0.6] Project Conventions Detection — read AGENTS.md/CLAUDE.md/.claude/rules/*
        |   into {PROJECT_CONVENTIONS}, echo the file list + count, assert non-empty
        |   when a rules dir exists, then inject verbatim into every subagent below
        |   (mandatory preflight gate — no agent dispatches until this passes)
        |
        v
[1] STAGE 1: Spec Compliance Review (Claude Subagent)
        |   - Compare implementation against requirements
        |   - Flag missing, extra, or divergent functionality
        |
        v
[2] STAGE 2: Parallel Dispatch ─────┬──── Agent 1A: Architecture, Design & Types (Claude)
        |                            ├──── Agent 1B: Framework, Structure & Data Integrity (Claude)
        |                            ├──── Agent 2: Security & Performance (Claude)
        |                            └──── Agent 3: External Validation (Codex CLI)
        v
[3] Merge & Deduplicate findings (both stages)
        |
        v
[4] Severity Classification & Report
        |
        v
[5] Present to User with Action Items
        |
        v (only if --fix)
[6] Auto-Fix — apply fixes for CRITICAL and HIGH issues, commit grouped by category
```

## Light Mode (`--light`)

**Purpose.** A fast, single-agent quality gate for use between milestones in larger
workflows (e.g. `/spec-first-cc-cc`) where running the full 4-agent pass (3 Claude agents +
Codex) would be disproportionate. Light mode runs **only Agent 1A (Architecture,
Design & Types)**. Nothing else from Stages 1 or 2 runs.

**Dispatch contract.** Light mode is ALWAYS executed inside a single Agent tool
subagent (`subagent_type: reviewer`, defined in `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md`: Opus,
effort high; when this repo is installed as a plugin the type is namespaced
`keel-skills:reviewer`, and every `subagent_type: reviewer` below means that name; fall back to
`general-purpose` only if that type is missing). The main
conversation never runs Agent 1A inline, never
performs the scope detection steps for light mode, and never touches the repo beyond
launching the subagent and relaying its output. This keeps the caller's context clean
(critical when invoked per-milestone from `/spec-first-cc-cc`, which would otherwise
accumulate review noise across many iterations).

**When `--light` is detected:**

1. Skip Steps 0, 0.5, 1, and Step 2's other three agents (1B, 2, 3). Skip Step 3's
   merge/dedupe logic and Step 4's report aggregation (there is nothing to merge).
2. Launch a single Agent tool subagent with the prompt below. The subagent is
   responsible for: detecting scope (git diff), reading affected files, running the
   Agent 1A checklist, producing the light report, and — if `--fix` was also passed —
   applying CRITICAL/HIGH fixes and committing them grouped by category.
3. Relay the subagent's final report back to the caller verbatim. Do not re-analyze,
   re-dedupe, or re-format.

**Subagent prompt (light mode, Agent tool, `subagent_type: reviewer`):**

```
You are running `/review-changes --light` as an isolated subagent. Your entire job is
Agent 1A of the review-changes skill — Architecture, Design & Types — applied to the
current working tree's changes. Nothing else.

## Steps you own

1. Detect scope. Default branch via:
     DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
     (fall back to origin/main, then origin/master)
   Collect the diff:
     - Uncommitted: `git diff` + `git diff --staged`
     - Branch review: `git diff $DEFAULT_BRANCH...HEAD`
     - If nothing staged/unstaged and no branch divergence, ask the caller what range to review.
   List changed files with `git diff --name-only <range>` and read them in full for context.

1b. Load this repo's OWN rules. List and read in full every convention file that exists:
     ROOT=$(git rev-parse --show-toplevel)
     ls "$ROOT"/AGENTS.md "$ROOT"/CLAUDE.md "$ROOT"/.cursorrules \
        "$ROOT"/.claude/rules/*.md "$ROOT"/.cursor/rules/*.md* 2>/dev/null
    AGENTS.md / CLAUDE.md may `@import` other rule files — follow and read those too.
    These rules are authoritative: a violation of one is a genuine finding (checklist
    item 0), never a "stylistic preference". If none exist, note that and continue.
    Echo the resolved file list with its count before reviewing (e.g.
    "Conventions loaded (7): …") and put a `**Conventions enforced:**` line in the report
    header. If the globs return zero files BUT a `.claude/rules/` directory exists, that is a
    load failure — retry discovery, do not review with zero rules.

1c. Budget (hard limit). This gate gets at most ~40 tool calls in total, the reads of
   steps 1 and 1b included: batch them (one Bash call can `cat` several files; one Grep
   can cover several symbols). If the diff exceeds ~600 changed lines, review it in two
   batches grouped by directory and merge the findings. Never explore beyond the changed
   files and the modules they import directly. Measured over 72 gates, the unbounded
   version averaged 111 requests and 65 tool calls per run, most of it re-discovering
   the repo instead of reading the diff.

2. Run the Agent 1A checklist below against the diff. Only report findings with
   >80% confidence of a genuine issue. Do NOT flag stylistic preferences — EXCEPT
   violations of the repo rules loaded in step 1b, which you MUST report (item 0).

3. If `--fix` was ALSO passed (the caller will tell you in the dispatch message),
   apply fixes for CRITICAL and HIGH findings using Edit — or for ALL severities if
   the dispatch message overrides the scope (e.g. spec-first milestone gates); the
   dispatch message wins. Commit grouped by category with messages like
   `refactor: <category> (review-changes --light --fix)`.
   Re-read each file fully before editing. Skip findings that require architectural
   decisions, change public API contracts, or are ambiguous — list those as "requires
   manual intervention".

## Agent 1A Checklist (22 points — SAME as full mode)

0. **(authoritative) Project convention compliance** — the diff obeys EVERY rule in the
   repo convention files loaded in step 1b. Flag each violation individually, citing the
   rule and its source file (e.g. `.claude/rules/typescript.md`). A written project rule
   overrides the "no stylistic preferences" guidance — if the repo bans it, it is a
   finding (severity HIGH unless the rule implies lower).

**Architecture & Design:**
1. DRY violations — duplicated logic that should be extracted
2. Single Responsibility — functions/files doing too much (>50 lines / >800 lines). For React components: evaluate EACH component independently — a parent that has extracted children still fails if the parent itself has useState/useQuery/useMemo + >30-40 lines of JSX with its own logic (e.g., inline filter selects, complex conditional rendering). The presence of child components does NOT excuse a bloated parent.
3. Inline step/phase comments → extract to named methods — sequential comments like `// Step 1:`, `// Step 2:`, `// Phase 2:`, `// First do X, then Y` inside a function body are a code smell: each labeled block is a candidate for extraction into a named helper. If a block needs a comment label to be understood, that label should become the function name. **Exception:** comments explaining *why* (non-obvious rationale, invariants, workarounds, performance warnings) are valid. This rule targets comments that describe *what* the block does, not *why*.
4. Dead code — unused imports, unreachable branches, commented-out code
5. Prop drilling — props passed through 3+ levels (suggest context/composition)
6. Naming — misleading names, single-letter vars in complex contexts, magic numbers
7. Enum usage — multiple type values should use enums, not string literals or arrays
8. Centralized constants — shared facts imported from shared modules, not redeclared
9. Shared schemas — validation schemas defined once and reused, not duplicated
10. Refactoring completeness — if renamed/changed, all call sites updated, no stale references
11. Single source of truth — no duplicated type definitions or validation rules
12. Reuse existing code — search for existing hooks/utils/constants before creating new ones. **Actionable check for NEW helpers:** for every function/helper/constant the diff DEFINES (especially in test files, `*.utils.ts`, `*.lib.ts`, or any new file), actively grep the nearest shared dir (`utils/`, `lib/`, `common/`, `helpers/`) AND sibling files of the same kind for an existing export of the same name or shape BEFORE accepting it as new. A diff-scoped read makes a freshly-duplicated helper look self-consistent; only the cross-file grep reveals it already exists. A match is a DRY finding — import the existing one (extend it if it lacks a variant), don't redefine. This is the single most common review miss: the duplicate lives entirely inside a new, internally-coherent file.
20. **(HIGH) Delete every comment the code does not strictly require.** The bar is: *remove the comment — can a competent reader still understand the code?* If yes, the comment MUST go. Comments rot, duplicate the code, and double the maintenance surface. The ONLY comments that survive are ones the reader cannot reconstruct from identifiers, types, and control flow alone — typically **negative invariants** (why something is intentionally absent), **cross-file constraints** (that break non-locally if violated), or **workarounds for external bugs** (with link). Everything else — rationale for decisions, WHAT-summaries, doc-style field descriptions, "guard against X", "for perf", "see related", section headers, reminders to future maintainers — gets deleted. **Flag every single offender individually**, do not consolidate.
21. **(HIGH)** Named callbacks for `map` / `filter` / `reduce` with non-trivial logic — inline arrows with real logic (parsing, validation, range checks, multi-condition predicates) hide intent from the call-site. Extract as a named function. If the callback needs closure over outer variables, use the factory-returning-fn pattern so the call-site reads as `arr.filter(isEventWithinWindow(start, end))`, not `arr.filter((e) => isEventWithinWindow(e, start, end))`. **Exception:** trivial passthroughs like `x => x.id` or tuple builders for `Map`/`Set` such as `q => [q.id, q]` may remain inline. **Bonus:** name variables by content, not by structure (`questionsById` > `questionMap`).

**Type Safety & Data:**
13. Type correctness — any types, missing null checks, unsafe casts
14. Immutability — direct mutation where spread/map/filter is safer
15. Error handling — empty catch blocks, unhandled promise rejections, swallowed errors
16. Error handling fidelity — error types match actual failure mode, messages include context
17. Zod nullability — explicit null/undefined handling, no truthy/falsy traps hiding 0 or ""
18. Collection key collision — unique keys for iterable elements, no array indices when items reorder
19. Nullish coalescing — use `??` instead of `||` for defaults when `0` or `""` are valid values

## Output format

Return a compact Markdown report:

# Code Review Report — Light Mode

**Scope:** {description of what was reviewed}
**Files reviewed:** {count}
**Conventions enforced:** {comma-separated rule files loaded in step 1b, with count — or "NONE FOUND" only if the repo genuinely has no rule files/directory}
**Agent:** Architecture, Design & Types (1A)
**Fix mode:** {enabled / disabled}

## Findings

### CRITICAL ({count})
#### 1. [File:Line] Issue Title
**Issue:** ...
**Fix:** ...

### HIGH ({count})
...

### MEDIUM ({count})
...

### LOW ({count})
...

## Out-of-scope observations
- file:line — short description
- (or "None")

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | X     | BLOCK  |
| HIGH     | X     | WARN   |
| MEDIUM   | X     | INFO   |
| LOW      | X     | NOTE   |

### Verdict: {APPROVE / WARN / BLOCK}
- BLOCK — any CRITICAL issues
- WARN — HIGH issues present
- APPROVE — no CRITICAL or HIGH

{If --fix was applied, append:}

## Auto-Fix Summary
- {N} CRITICAL issues fixed
- {N} HIGH issues fixed
- {N} issues skipped (require manual intervention — listed below)
- Commits created: {list with SHAs}
```

**Light mode NEVER runs:** Stage 1 (spec compliance), Agent 1B, Agent 2 (security/perf),
Agent 3 (Codex). If the caller needs those, they must invoke `/review-changes` without
`--light` (e.g. final review at end of feature).

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
5. Also list all changed files with `git diff --name-only <range>` to give agents file context
6. Read surrounding code for changed files — agents need full file context, not just diffs
7. **Stacked branches — review against the TRUE base, and judge findings against HEAD, not the diff.**
   If this branch targets another feature branch rather than `$DEFAULT_BRANCH` (a PR stacked on
   another PR), detect the real base — `gh pr view --json baseRefName` when a PR exists, else the
   merge-base — and diff against THAT, so the review scope matches what the PR actually adds.
   Critically: a guard, check, or fix that lives in the BASE branch is NOT in this branch's diff,
   yet it IS present in the file at HEAD. Before reporting that something is "missing" (an absent
   expiry fence, auth check, validation), confirm it against the FULL FILE at HEAD — not just the
   diff hunks — or you will raise a false positive for code that exists just outside the changeset.
   The reverse also holds: don't assume base code is correct just because it's unchanged; read it
   when the new surface's correctness depends on it.

Save the diff output and file list — all agents receive the same input.

## Step 0.5: Spec Source Detection

Before reviewing code quality, determine what the implementation was supposed to do. Search
for spec sources in this priority order:

1. **plan.md** — Check `.workspace/features/*/plan.md` for any feature plan matching the changed files.
   Use the most recently modified plan that references files or directories in the diff.
2. **todo.md** — Check `.workspace/features/*/todo.md` alongside the plan for task-level requirements.
3. **Git branch name / commit messages** — Extract the feature name or ticket ID from the branch
   name (e.g., `feature/add-user-search`) and recent commit messages in the review range.
4. **Issue / PR description** — If reviewing a branch, run `gh pr view --json body,title` or
   `gh issue view <id>` to fetch the original task description.
5. **User-provided context** — If the user explicitly stated what the task was ("implement X"),
   use that as the spec.

If **no spec source is found**, log `[Spec Compliance: SKIPPED — no spec/plan/issue found]`
in the report and proceed directly to Stage 2. Do not fabricate requirements.

Collect the spec into a `{SPEC_CONTEXT}` variable for the Stage 1 agent.

## Step 0.6: Project Conventions Detection

Before dispatching any review agent, load the repository's OWN coding rules so every
subagent reviews against **this** project's standards, not just the generic checklists.
A written project rule is authoritative: a violation of it is a real finding, never a
"stylistic preference". This is the step that catches things like a banned `as` cast,
a required error-tagging convention, or a mandated file/test-naming pattern — rules the
generic checklists do not know about.

Discover and read, in full, every convention source that exists (skip silently if absent):

```bash
ROOT=$(git rev-parse --show-toplevel)
# Top-level agent/rule manifests
ls "$ROOT"/AGENTS.md "$ROOT"/CLAUDE.md "$ROOT"/.cursorrules 2>/dev/null
# Rule directories (Claude + Cursor)
ls "$ROOT"/.claude/rules/*.md "$ROOT"/.cursor/rules/*.md* 2>/dev/null
```

Read every file found with the Read tool. `AGENTS.md` / `CLAUDE.md` frequently `@import`
other rule files (e.g. `@AGENTS.md`, `@.claude/rules/typescript.md`) — follow those
references and read the targets too. Concatenate the contents into a `{PROJECT_CONVENTIONS}`
variable, each section prefixed with its source path (e.g. `=== .claude/rules/typescript.md ===`)
so agents can cite the rule they break.

If no convention files exist, set `{PROJECT_CONVENTIONS}` to
`"No project-specific rule files found."` and proceed.

`{PROJECT_CONVENTIONS}` MUST be passed verbatim into EVERY subagent — Stage 1, all four
Stage 2 agents (including the Codex external validator), and the light-mode agent. No
review subagent is dispatched without the project's own rules in its context.

### Mandatory preflight gate (do NOT dispatch any agent until this passes)

This step is the single most common point of silent failure: the review runs, but the
agents never actually received the repo's own rules, so a banned `as any`, a missing
`sentryContext`, or a duplicated constant sails through as "no findings". Close that hole
with an explicit, visible gate:

1. **Enumerate and echo.** Run the discovery globs above and print the resolved file list
   to the user verbatim, e.g.:
   ```
   Conventions loaded (7): AGENTS.md, CLAUDE.md, .claude/rules/typescript.md,
   .claude/rules/nestjs.md, .claude/rules/react.md, .claude/rules/testing.md, ...
   ```
   Counting and showing the files is what makes "the rules were loaded" auditable instead
   of assumed.
2. **Follow @imports.** If `AGENTS.md`/`CLAUDE.md` `@import` other files (e.g. `@AGENTS.md`,
   `@.claude/rules/*.md`), resolve and read those too. A manifest that is just `@AGENTS.md`
   counts as ZERO rules until you follow it — do not stop at the manifest.
3. **Assert non-empty when the repo clearly has rules.** If the globs find zero files BUT a
   `.claude/rules/` or `.cursor/rules/` directory exists, treat it as a load failure, say so,
   and retry the discovery before dispatching. Never proceed reporting "No project rules" when
   a rules directory is sitting right there.
4. **Verify injection.** The exact `{PROJECT_CONVENTIONS}` block you echoed is the block that
   goes into every dispatch prompt below — Stage 1, Agents 1A/1B/2, Codex, and light mode.
   Do not summarize, truncate, or paraphrase it per agent.
5. **Make it auditable in the report.** The final report header MUST carry a
   `**Conventions enforced:**` line listing every rule file that was loaded (see Step 4). A
   review whose header shows zero rule files on a repo that has a `.claude/rules/` directory
   is a failed review, not a clean one.

## Step 1: Stage 1 — Spec Compliance Review

Launch a Claude subagent via the Agent tool with the spec context, diff, and file list.
This runs BEFORE Stage 2 and gates the review — if the implementation does not match what
was requested, code quality is secondary.

### Spec Compliance Agent (Claude Subagent)

Prompt the Agent tool with:

```
You are a senior engineer performing a SPEC COMPLIANCE review. Your job is to verify
that the implementation matches what was requested — nothing more, nothing less.

You are NOT reviewing code quality, style, or performance. You are ONLY checking whether
the right thing was built.

## Spec / Requirements:
{SPEC_CONTEXT}

## Changed Files:
{FILE_LIST}

## Diff:
{DIFF}

## Your Checklist (10 points)

**Requirement Coverage:**
1. All requirements addressed — every requirement from the spec has corresponding implementation
2. No partial implementations — features are complete, not stubbed or half-finished
3. No missing edge cases explicitly called out in the spec

**Scope Integrity:**
4. No scope creep — no features, endpoints, components, or behaviors added beyond what was requested
5. No gold plating — no unnecessary abstractions, premature optimizations, or "nice to have" additions
6. No silent removals — existing functionality not removed unless the spec explicitly calls for it

**Contract Conformance:**
7. Function signatures match spec — parameter names, types, return types match what was planned
8. API contracts match spec — endpoints, HTTP methods, request/response shapes, status codes as specified
9. Data model matches spec — table names, column names, types, constraints, relationships as planned
10. UI behavior matches spec — components, interactions, routing, state management as described

For each finding, report:
- **Severity**: CRITICAL (requirement missed or wrong feature built) / HIGH (partial implementation
  or significant deviation) / MEDIUM (minor scope creep or slight contract mismatch) / LOW (cosmetic
  deviation from spec, naming differences)
- **Requirement**: which spec requirement this relates to
- **Issue**: what's wrong
- **Evidence**: quote the relevant spec section AND the relevant code/diff section
- **Fix**: what needs to change to match the spec

End with:
- A coverage summary: X of Y requirements fully implemented
- A scope verdict: CLEAN (no creep) / MINOR CREEP (low-severity additions) / SIGNIFICANT CREEP (unnecessary features added)
- A compliance verdict: PASS / PARTIAL / FAIL
```

### Stage 1 Output

The Stage 1 findings appear in the final report under `## Stage 1: Spec Compliance` before
the Stage 2 findings. If Stage 1 verdict is FAIL (missed requirements or wrong feature built),
the overall review verdict is automatically **BLOCK** regardless of Stage 2 results.

## Step 2: Stage 2 — Parallel Agent Dispatch

**Dispatch order matters — launch Codex (Agent 3) FIRST, then the Claude agents.**
Codex is by far the slowest reviewer (it reads the full diff + every convention file +
explores the repo — easily 3-4 min and ~1M input tokens, vs ~70s for each Claude agent),
so it is the wall-clock bottleneck. Start it before everything else so its runtime overlaps
the Claude agents instead of being tacked on at the end.

Concretely:

1. **Launch Codex (Agent 3) first, via Bash with `run_in_background: true`** (see Agent 3
   below for the exact command — it writes to a file with its own `timeout`, NOT a pipe).
   Do NOT put the Codex Bash call in the same synchronous tool-call block as the Claude
   agents and then wait on all of them together — that was observed to get Codex killed by
   an external signal (exit 144) when the block closed after the faster Claude agents had
   already returned. Background it so it owns its own lifecycle.
2. **Then launch the 3 Claude agents** (1A, 1B, 2) simultaneously using the Agent tool.
3. When the Claude agents finish, await the Codex background task (it has been running the
   whole time). Total wall-clock ≈ `max(Codex, Claude agents)` ≈ Codex, not the sum.

Each agent receives:
- The full diff
- The list of changed files
- Instructions specific to their review domain

### Agent 1A: Architecture, Design & Types (Claude Subagent)

Prompt the Agent tool (`subagent_type: reviewer`) with:

```
You are a senior code reviewer focused on ARCHITECTURE, DESIGN, and TYPE SAFETY.

Review the following changes and report issues organized by severity.
Only report findings where you are >80% confident of a genuine issue.
Do NOT report stylistic preferences — EXCEPT anything covered by the Project
Conventions section below, which is authoritative (see checklist item 0).

## Project Conventions (authoritative — read FIRST)

{PROJECT_CONVENTIONS}

The rules above are THIS repo's own standards. A violation of any of them is a genuine
finding, never a "stylistic preference", and you MUST report it — cite the source file
of the rule (e.g. `.claude/rules/typescript.md`). Severity is HIGH unless the rule's own
wording implies lower. This includes things the generic checklist would otherwise wave
through (e.g. a banned `as` cast that "looks safe", a required Sentry/error tag, a
mandated naming or import-ordering convention).

## Scope Boundary (strict)

Your checklist below is the COMPLETE scope of your review. You are one of five
specialized reviewers; the other four cover everything else.

- Analyze and report ONLY issues that match your checklist items.
- If you notice an issue outside your checklist, do NOT analyze it. Add a
  single-line entry at the end under `## Out-of-scope observations`:
  `file:line — short description`. No severity, no fix.
- Depth over breadth — it's better to find all DRY violations on your list than
  to also flag a race condition that belongs to another agent.

## Your Checklist (22 points)

0. **(authoritative) Project convention compliance** — the diff obeys EVERY rule in the
   Project Conventions section above. Flag each violation individually, citing the rule
   and its source file. A written project rule overrides the "no stylistic preferences"
   guidance — if the repo bans it, it is a finding.

**Architecture & Design:**
1. DRY violations — duplicated logic that should be extracted
2. Single Responsibility — functions/files doing too much (>50 lines / >800 lines). For React components: evaluate EACH component independently — a parent that has extracted children still fails if the parent itself has useState/useQuery/useMemo + >30-40 lines of JSX with its own logic (e.g., inline filter selects, complex conditional rendering). The presence of child components does NOT excuse a bloated parent.
3. Inline step/phase comments → extract to named methods — sequential comments like `// Step 1:`, `// Step 2:`, `// Phase 2:`, `// First do X, then Y` inside a function body are a code smell: each labeled block is a candidate for extraction into a named helper. If a block needs a comment label to be understood, that label should become the function name. **Exception:** comments explaining *why* (non-obvious rationale, invariants, workarounds, performance warnings) are valid. This rule targets comments that describe *what* the block does, not *why*.
4. Dead code — unused imports, unreachable branches, commented-out code
5. Prop drilling — props passed through 3+ levels (suggest context/composition)
6. Naming — misleading names, single-letter vars in complex contexts, magic numbers
7. Enum usage — multiple type values should use enums, not string literals or arrays
8. Centralized constants — shared facts imported from shared modules, not redeclared
9. Shared schemas — validation schemas defined once and reused, not duplicated
10. Refactoring completeness — if renamed/changed, all call sites updated, no stale references
11. Single source of truth — no duplicated type definitions or validation rules
12. Reuse existing code — search for existing hooks/utils/constants before creating new ones. **Actionable check for NEW helpers:** for every function/helper/constant the diff DEFINES (especially in test files, `*.utils.ts`, `*.lib.ts`, or any new file), actively grep the nearest shared dir (`utils/`, `lib/`, `common/`, `helpers/`) AND sibling files of the same kind for an existing export of the same name or shape BEFORE accepting it as new. A diff-scoped read makes a freshly-duplicated helper look self-consistent; only the cross-file grep reveals it already exists. A match is a DRY finding — import the existing one (extend it if it lacks a variant), don't redefine. This is the single most common review miss: the duplicate lives entirely inside a new, internally-coherent file.
20. **(HIGH) Delete every comment the code does not strictly require.** The bar is: *remove the comment — can a competent reader still understand the code?* If yes, the comment MUST go. Comments rot, duplicate the code, and double the maintenance surface. The ONLY comments that survive are ones the reader cannot reconstruct from identifiers, types, and control flow alone — typically **negative invariants** (why something is intentionally absent), **cross-file constraints** (that break non-locally if violated), or **workarounds for external bugs** (with link). Everything else — rationale for decisions, WHAT-summaries, doc-style field descriptions, "guard against X", "for perf", "see related", section headers, reminders to future maintainers — gets deleted. **Flag every single offender individually**, do not consolidate.
21. **(HIGH)** Named callbacks for `map` / `filter` / `reduce` with non-trivial logic — inline arrows with real logic (parsing, validation, range checks, multi-condition predicates) hide intent from the call-site. Extract as a named function. If the callback needs closure over outer variables, use the factory-returning-fn pattern so the call-site reads as `arr.filter(isEventWithinWindow(start, end))`, not `arr.filter((e) => isEventWithinWindow(e, start, end))`. **Exception:** trivial passthroughs like `x => x.id` or tuple builders for `Map`/`Set` such as `q => [q.id, q]` may remain inline. **Bonus:** name variables by content, not by structure (`questionsById` > `questionMap`).

**Type Safety & Data:**
13. Type correctness — any types, missing null checks, unsafe casts
14. Immutability — direct mutation where spread/map/filter is safer
15. Error handling — empty catch blocks, unhandled promise rejections, swallowed errors
16. Error handling fidelity — error types match actual failure mode, messages include context
17. Zod nullability — explicit null/undefined handling, no truthy/falsy traps hiding 0 or ""
18. Collection key collision — unique keys for iterable elements, no array indices when items reorder
19. Nullish coalescing — use `??` instead of `||` for defaults when `0` or `""` are valid values

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

After the severity summary, append:

## Out-of-scope observations
- file:line — short description
- (or write "None" if no out-of-scope items were noticed)
```

### Agent 1B: Framework, Structure & Data Integrity (Claude Subagent)

Prompt the Agent tool (`subagent_type: reviewer`) with:

```
You are a senior code reviewer focused on FRAMEWORK PATTERNS, STRUCTURAL QUALITY,
and DATA INTEGRITY.

Review the following changes and report issues organized by severity.
Only report findings where you are >80% confident of a genuine issue.
Do NOT report stylistic preferences — EXCEPT anything covered by the Project
Conventions section below, which is authoritative (see checklist item 0).

## Project Conventions (authoritative — read FIRST)

{PROJECT_CONVENTIONS}

The rules above are THIS repo's own standards. A violation of any of them is a genuine
finding, never a "stylistic preference", and you MUST report it — cite the source file
of the rule. Severity is HIGH unless the rule's own wording implies lower. This includes
framework/structure conventions the generic checklist does not know (mandated file
naming, directory roles, migration/entity patterns, test-naming rules, etc.).

## Scope Boundary (strict)

Your checklist below is the COMPLETE scope of your review. You are one of five
specialized reviewers; the other four cover everything else.

- Analyze and report ONLY issues that match your checklist items.
- If you notice an issue outside your checklist, do NOT analyze it. Add a
  single-line entry at the end under `## Out-of-scope observations`:
  `file:line — short description`. No severity, no fix.
- Depth over breadth — it's better to find all DRY violations on your list than
  to also flag a race condition that belongs to another agent.

## Your Checklist (39 points)

0. **(authoritative) Project convention compliance** — the diff obeys EVERY rule in the
   Project Conventions section above. Flag each violation individually, citing the rule
   and its source file. A written project rule overrides the "no stylistic preferences"
   guidance.

**Framework Patterns (React/Next.js):**
1. useEffect dependency arrays & cleanup — missing or incorrect dependencies. **All timeouts, intervals, event listeners, and subscriptions created inside effects MUST be cleaned up in the return function** (e.g. `clearTimeout`, `clearInterval`, `removeEventListener`). Flag any `setTimeout`/`setInterval`/`addEventListener` inside a useEffect without a corresponding cleanup.
2. Render-phase state updates — setState during render causing loops
3. List keys — array index as key when items can reorder
4. Client/Server boundary — useState/useEffect in Server Components
5. Closure staleness — event handlers capturing outdated state
6. Modal/dialog UX — forms in modals implement unsaved changes warnings
7. Form patterns — react-hook-form + zod for all forms, no manual validation
8. Fixed navigation — use explicit routes instead of `router.back()` (breaks with multi-page flows)
9. Explicit component props — specify `variant` and similar props explicitly, don't rely on defaults
9a. **Route-guard early-return bypass — reason about EVERY entry path, not the diff.** For each early-return / short-circuit in an auth, onboarding, or flow guard (`beforeLoad`, `loader`, middleware, route HOC) that EXEMPTS a path from a downstream check, enumerate every way that path can be entered — direct URL nav, browser back/forward, deep link, refresh — and confirm the skipped checks are safe to skip on ALL of them, not just the redirect the guard itself issues. A blanket `if (pathname.startsWith('/x')) return` that was added "to avoid a redirect loop" is a finding whenever `/x` is also reachable by manual navigation AND the early-return skips a security/flow check (e.g. a pending-invite or unverified-email gate) that must still apply there. The correct shape is usually: exempt only the guard's OWN destination from its OWN redirect, and run the other checks before exempting it. When a guard's control flow changes, also verify a test covers direct navigation to each exempted route.
9b. **DTO shaping via the serialization layer, not hand-rolled mappers (NestJS / class-transformer stacks).** When the repo's convention is class-validator/class-transformer DTOs formatting data on the way out, flag NEW ad-hoc mapper functions (`toXxxDto()`, object literals rebuilding a response field by field) that duplicate what the DTO class already does. Hand-written mappers drift out of sync with the Swagger/DTO definition — fields silently missing, nullability mismatched — and scatter presentation logic into services. The fix: express the shaping in the DTO class itself (`@Expose`, `@Transform`, `@Exclude`, serialization groups, constructor mapping) so the declared contract and the runtime output cannot diverge. **Exception:** transformations the serialization layer genuinely can't express (cross-entity aggregation, computed fields needing extra queries), or repos that don't use class-transformer at all.

**Structural Quality:**
10. Module cohesion — files contain related functionality, not grab-bag utils
11. Discoverability — public APIs well-named, file/directory names match purpose
12. Flat is better than nested — max 2 levels of indentation, use guard clauses and early returns
13. Function argument discipline — max 2 required args; 3+ use options object; no boolean flag args
14. Hardcoded colors — extract to CSS variables or design token constants
15. Hardcoded API routes — extract to route constants

**Transaction & Data Integrity:**
16. Minimize transaction hold time — no external I/O (HTTP, queues, S3), heavy computation, or long awaits inside DB transactions
17. Terminal states are sticky — status updates check current state before overwriting; terminal states protected from regression
18. Write-then-read — after create/update/upsert, use the returned record instead of re-fetching (avoids replication lag)
19. Simple locking — default to standard transaction isolation; avoid SERIALIZABLE for simple upserts; bounded retries with backoff

**Observability & Debuggability:**
20. Failure-path context — new error paths include enough domain context (IDs, operation, state) to debug the failing operation without adding logs after the fact
21. Error taxonomy — code distinguishes expected/user/dependency failures from invariant bugs where the stack supports it (typed errors, error codes, is_transient flags)
22. Async boundary visibility — new jobs/webhooks/workers expose stable IDs and explicit start/success/failure/dead-letter states

**Distributed-Systems Robustness (failure-mode reasoning — DO NOT just read the diff statically; trace what happens under crash, retry, redelivery, and concurrency):**
23. Partial-failure between external I/O and local commit — when code performs an external side-effect (payment/subscription create, file upload, message send) and THEN records it locally, reason about a crash/timeout BETWEEN the two. Does a retry mint a second external resource? Is the idempotency key stable across retries of the SAME logical operation, or does it change (e.g. a counter/generation bumped before the retry) and defeat dedup? Is the orphan left by the crash detectable AND reconcilable — or does the reconciliation query filter out exactly that partial-failure state (e.g. `WHERE external_id IS NOT NULL` skips rows that have a customer but never recorded the subscription)? Also check at-least-once delivery: a redelivered/late webhook for a now-terminal entity must be a safe no-op.
24. Cross-sibling invariant consistency — when SEVERAL handlers/branches share a guard or invariant (a status fence against a terminal state, an idempotency key, an ownership check, a period fence), verify EVERY sibling applies it. Read them as a GROUP, not in isolation — the bug is almost always the one handler of N that omits the shared guard, and it looks locally correct so a per-file pass misses it. Enumerate the siblings (e.g. all `apply*`/`handle*` methods in a service, all branches of a dispatch) and diff their guards against each other.
25. New code inheriting out-of-diff global config — when new routes/handlers rely on app-global config NOT present in the diff (body-parser limits, global route prefixes/versioning, CORS, default middleware, auth interceptors), review that config against the new surface's needs even though the line isn't in the changeset. An unauthenticated webhook inheriting a 50MB body limit is a DoS surface; a third-party callback under a versioned `/v1` prefix churns its URL on every API version. Do NOT scope yourself to changed lines when the new code's correctness depends on unchanged global config.
26. Atomic claim / compare-and-set over check-then-act — a dedup, claim, or status guard on shared state must be a SINGLE atomic write (`UPDATE … SET … WHERE <precondition>` then check affected rows, or `INSERT … ON CONFLICT DO NOTHING`), never a SELECT/read followed by a separate INSERT/UPDATE. Two concurrent deliveries both pass the read and both act. Flag a webhook/idempotency claim, a counter/balance update, or a "if not exists then insert" implemented as read-then-write.
27. Idempotency key on every external mutating call in a retryable path — each create/charge/meter/send to an external API that a retry, timeout, or at-least-once delivery can repeat must carry a STABLE idempotency key (same logical op → same key). Additive endpoints (usage metering, counters) double-count without one; resource creates leak duplicates. Flag a mutating SDK call in a webhook/job/retry path with no key, or a key that varies across retries of the same operation.
28. Reset ALL cycle-derived state when reusing or transitioning an entity — when a row is recycled into a new cycle/generation (re-subscribe, re-open, new billing period, reset-to-pending), reset EVERY field derived from the prior cycle (high-water marks, counters, last-reported anchors, period bounds, cached totals), not just the obvious one. Leftover values from the previous cycle silently suppress or corrupt the new one. Flag a partial reset that updates some cycle fields but leaves siblings stale.
29. Transaction work uses the transaction's manager, not the default repository — code inside `manager.transaction(...)` / a `@Transactional` scope must issue its writes through the transaction's EntityManager. Calling the default injected repository (`this.repo`) opens a SEPARATE connection outside the transaction, so a rollback does not undo it and the "commits/rolls back together" guarantee is false. Also flag a comment asserting a transactional/atomic guarantee the code does not actually provide.
30. Discriminate the event sub-type/reason before treating it as authoritative — a webhook/event handler must filter on the specific sub-type or reason (Stripe `billing_reason`, event subtype, message kind, status transition) before running logic that assumes the expected trigger. Treating every event of the broad type as the authoritative case fires close-out/finalization on the wrong event. Match on the most specific identifier the payload carries (subscription id over customer id), never a broader one that can collide.
31. Unique + lookup indexes on external-identity columns — a column holding an external system's id (customer/subscription/account/tenant id) that handlers query on every delivery needs a UNIQUE constraint (the CAS/dedup paths assume duplicates are impossible — enforce it) and an index (webhook lookups otherwise full-scan). Flag a new such column added without both.

**Data-Model & Readability (backend / ORM repos — favor the fewest context-rich entities, readable reads, and compile-time-safe queries over cleverness):**
32. One context-rich entity over many specialized tables — flag a NEW table/entity whose only job is to encode one status or variant of a relationship an existing entity could carry as a `type` enum + `status` enum + nullable actor/timestamp columns (keep multiple rows, take the latest row per parent as the source of truth). Several side tables for the states of one relationship is the smell.
33. Nullable FK + upsert over mirrored create/link branches — when a flow splits into "the related row exists, link it" vs "it does not, create it", flag it if making one foreign key nullable would let both paths collapse into a single upsert-first sequence. A uniform upsert has fewer states than mirrored `if/else` create/link branches.
34. Joins + entity getters over hand-written CTEs / raw SQL on read paths — flag a raw-SQL CTE, `repository.query(...)`, or a positional-column array building a read/aggregation where a `createQueryBuilder(...).leftJoinAndSelect(...)` plus a plain entity getter (simple loops over loaded relations) would read clearly. Loading slightly more data for a read path a new developer understands at a glance is the preferred trade. Reinforces the repo's TypeORM-over-raw-SQL rule.
35. TypeORM built-ins for compile-time safety — prefer `.findOne`, `.save(.create(...))`, and the entity definitions over raw SQL or a hand-written mirror type; an entity change should throw a compile-time error, not fail silently at runtime. Let the DTO own response shaping (see 9b) instead of defining an intermediate type.
36. Domain vocabulary, not implementation mechanics — flag names drawn from the internal mechanism (`cell`, `bucket`, `grid`, `cte`, `matrix`) in domain service code where the domain nouns (e.g. `list`/`item`/`credential`/`member`) are what the reader expects. A reader should not have to learn your internals to change the file.
37. Side effects through `on<Entity><Event>` non-await lifecycle hooks — flag a Slack message, audit-log write, or other background side effect inlined in the middle of business logic instead of a non-`await` `on*` hook called at the END of the service method that owns the event; the hook must live in the service that owns that event (a member-accepted event belongs with member logic, not admin-user logic), and its name/location must match the event the ticket asked for.

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

After the severity summary, append:

## Out-of-scope observations
- file:line — short description
- (or write "None" if no out-of-scope items were noticed)
```

### Agent 2: Security & Performance (Claude Subagent)

Prompt the Agent tool (`subagent_type: reviewer`) with:

```
You are a senior code reviewer focused on SECURITY and PERFORMANCE.

Review the following changes and report issues organized by severity.
Only report findings where you are >80% confident of a genuine issue.
Skip unchanged code unless it has CRITICAL security vulnerabilities.

## Project Conventions (authoritative — read FIRST)

{PROJECT_CONVENTIONS}

The rules above are THIS repo's own standards. A violation of any security/performance/
observability rule there (e.g. a required error class, a mandated Sentry tag on
cross-tenant lookups, a banned logging pattern) is a genuine finding, never a "stylistic
preference" — report it and cite the source file. Severity follows the rule's intent
(security conventions are typically HIGH or CRITICAL).

## Scope Boundary (strict)

Your checklist below is the COMPLETE scope of your review. You are one of five
specialized reviewers; the other four cover everything else.

- Analyze and report ONLY issues that match your checklist items.
- If you notice an issue outside your checklist, do NOT analyze it. Add a
  single-line entry at the end under `## Out-of-scope observations`:
  `file:line — short description`. No severity, no fix.
- Depth over breadth — it's better to find all DRY violations on your list than
  to also flag a race condition that belongs to another agent.

## Your Checklist (28 points)

0. **(authoritative) Project convention compliance** — the diff obeys EVERY security/
   performance/observability rule in the Project Conventions section above. Flag each
   violation individually, citing the rule and its source file.

**Security (CRITICAL priority):**
1. Hardcoded credentials — API keys, passwords, tokens, connection strings in source
2. SQL injection — string concatenation in queries instead of parameterized queries
3. XSS — unescaped user input rendered in HTML/JSX
4. Path traversal — user-controlled file paths without sanitization
5. CSRF — state-changing endpoints without CSRF tokens
6. Auth bypass — protected routes missing auth checks
7. Sensitive data in logs — tokens, passwords, PII in log statements
8. Output sanitization — user-controlled data escaped before rendering or logging

**Performance:** — for EVERY performance finding, quantify the impact when possible (e.g. "N queries → 1 batched query", "O(n²) → O(n log n)", approximate rows/calls/bytes saved). A quantified finding is far more actionable than a named pattern.
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
20. Test staleness & quality — (a) tests for changed code are updated, no assertions on old behavior; (b) new/changed tests verify behavior through the PUBLIC interface, not implementation. Flag tests that mock internal collaborators, assert on private methods, or hit the DB directly instead of the public API. Diagnostic: if renaming an internal function would break the test, it is testing implementation, not behavior — brittle, rewrite against observable behavior.
21. New dependencies — any package added to the manifest is vetted for: maintenance status (last release date, open-issue ratio, archived/deprecated flags), known CVEs (flag if a safer version or a maintained alternative exists), and bundle impact (size + tree-shakeability vs. a lighter alternative). Flag any new dep that is unmaintained, vulnerable, or disproportionately heavy for its use. Quantify when possible (added KB, CVE IDs).

**Observability:**
22. Structured logging — new boundary code (API handlers, queue consumers, external calls) emits structured logs with stable event names and severity, not console.log/print
23. Correlation propagation — request/job/trace IDs are preserved across service and async boundaries in new code
24. Sensitive data redaction — new logs/errors do not leak secrets, tokens, or PII (check for full request/response body logging)
25. Critical-path telemetry — new endpoints/jobs expose at least minimal success/failure/latency signals (metrics or structured logs)
26. Error tracking artifacts — production exceptions include release/environment metadata; frontend changes include source maps where applicable
27. Alertability — failures, retry exhaustion, or dead-letter outcomes in new code are externally observable, not silent

**Observability escalation:** If 1+ hard blocker (items 22-23 fail on critical path) or 2+ medium issues from items 24-27, recommend `/observability-audit` in the review report.

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

After the severity summary, append:

## Out-of-scope observations
- file:line — short description
- (or write "None" if no out-of-scope items were noticed)
```

### Agent 3: External Validation (Codex CLI, checklist mode)

Codex no longer re-runs the generic quality lists (Agents 1A, 1B and 2 own those). It answers a fixed
31-item checklist focused on what escaped every gate in real runs: acceptance criteria without proof,
behavior never executed, validators not run, weakened tests, limits that hide results, broken contracts.
The checklist and its answer format live in `references/codex-checklist-review.md`; the shared helpers and
the unavailable-Codex policy live in `${CLAUDE_PLUGIN_ROOT}/scripts/codex/README.md` (read it once per session).

**Before dispatch: the evidence file.** Write `.workspace/ctx/review/review-evidence.md` following
`references/review-evidence.md` (HEAD, tree fingerprint, validator/test commands with exit codes and
output tails, the plan's scenario commands and outputs, and what was not run and why). Check it with
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/codex/evidence.py check .workspace/ctx/review/review-evidence.md`; exit 6 means
stale, so re-run and rewrite it first. Codex verifies this file instead of running whole suites (whole-suite
runs inside Codex hit the timeout).

**Launch this FIRST and in the background** (`run_in_background: true`), see Step 2's dispatch-order note.

**Security: NEVER interpolate diff content or file lists directly into shell command strings.** Write
them to temp files; the prompt is a single-quoted heredoc.

```bash
CODEX_HELPERS=${CLAUDE_PLUGIN_ROOT}/scripts/codex
CHECKLIST=${CLAUDE_PLUGIN_ROOT}/skills/review-changes/references/codex-checklist-review.md
EVIDENCE="$(git rev-parse --show-toplevel)/.workspace/ctx/review/review-evidence.md"
DIFF_FILE=$(mktemp /tmp/review-diff-XXXXXX.txt)
PROMPT_FILE=$(mktemp /tmp/review-prompt-XXXXXX.txt)
CODEX_OUT=$(mktemp /tmp/review-codex-XXXXXX.jsonl)
CODEX_ERR=$(mktemp /tmp/review-codex-XXXXXX.err)
CODEX_ANSWER=$(mktemp /tmp/review-codex-XXXXXX.answer.md)
CODEX_STATUS=$(mktemp /tmp/review-codex-XXXXXX.status)
CODEX_MISSING=$(mktemp /tmp/review-codex-XXXXXX.missing)
REPO_ROOT=$(git rev-parse --show-toplevel)
git diff <range> > "$DIFF_FILE"

CONV_FILES=$(ls "$REPO_ROOT"/AGENTS.md "$REPO_ROOT"/CLAUDE.md "$REPO_ROOT"/.cursorrules \
  "$REPO_ROOT"/.claude/rules/*.md "$REPO_ROOT"/.cursor/rules/*.md* 2>/dev/null | tr '\n' ' ')
{
  printf 'Read these files in full FIRST:\n'
  printf '1. The checklist you must answer: %s\n' "$CHECKLIST"
  printf '2. The diff under review: %s\n' "$DIFF_FILE"
  printf '3. The evidence file (commands already run, with outputs): %s\n' "$EVIDENCE"
  printf '4. The spec source (plan/todo/issue): %s\n' "<SPEC_PATHS or 'none'>"
  printf '5. Project convention files (for R11; follow their @imports): %s\n\n' "$CONV_FILES"
} > "$PROMPT_FILE"

cat >> "$PROMPT_FILE" <<'PROMPT_EOF'
You are an independent reviewer. Answer EVERY item of the checklist in file 1, Tier 1 first, using its
exact answer format: one line per ID, `ID | PASS|FAIL|N-A|NOT-CHECKED | severity | file:line or command |
issue | fix`. N-A needs a concrete reason. Do not skip IDs; use NOT-CHECKED if you run out of time.
Verify claims against the repository and the evidence file; re-run at most 2 bounded, deterministic
commands (never whole suites). Then the optional `OTHER (max 5)` section. Do not modify any file.
PROMPT_EOF

# One hardened attempt, never retried for this gate (see ${CLAUDE_PLUGIN_ROOT}/scripts/codex/README.md).
# Bypass flag: Codex's bubblewrap sandbox fails on some kernels. `< /dev/null`: otherwise Codex waits for stdin EOF.
if python3 "$CODEX_HELPERS/codex-status.py" preflight > "$CODEX_STATUS"; then
  timeout 600 codex exec --json -C "$REPO_ROOT" --skip-git-repo-check \
    --dangerously-bypass-approvals-and-sandbox "$(cat "$PROMPT_FILE")" \
    < /dev/null > "$CODEX_OUT" 2> "$CODEX_ERR"
  python3 "$CODEX_HELPERS/codex-status.py" classify --exit $? --out "$CODEX_OUT" \
    --answer-file "$CODEX_ANSWER" > "$CODEX_STATUS" \
  && python3 "$CODEX_HELPERS/checklist.py" parse --checklist "$CHECKLIST" \
    --answer "$CODEX_ANSWER" --missing-out "$CODEX_MISSING" >> "$CODEX_STATUS"
fi
echo "status_file=$CODEX_STATUS answer=$CODEX_ANSWER missing=$CODEX_MISSING"; cat "$CODEX_STATUS"
```

Fill `<SPEC_PATHS>` with the spec source found in Step 0.5 (paths to plan.md/todo.md, or a temp file
holding the issue/PR text) before writing the prompt file.

**Routing on the status file** (after the Claude agents return):

| Status file says | What runs next | Report label |
|---|---|---|
| `status=ok` + `result=complete` | nothing | none |
| `status=ok` + `result=partial` | fallback subagent answers only the IDs in `$CODEX_MISSING` | `Claude-led; Codex partial: <missing count> items` |
| `status=ok` + `result=invalid-output` | fallback answers the full checklist | `Claude-only; Codex unavailable: invalid-output` |
| any other `status=` (`quota`, `capacity`, `auth`, `timeout`, `failed`, `not-installed`) | fallback answers the full checklist | `Claude-only; Codex unavailable: <status>[ until <until>]` |

The fallback is ONE Agent tool subagent (`subagent_type: reviewer`; `general-purpose` if missing) given the
same prompt file and the list of IDs to answer, writing its lines to a file. Then build the final table:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/codex/checklist.py merge --checklist "$CHECKLIST" \
  --primary "$CODEX_ANSWER" --primary-label "<Codex | Codex (partial)>" \
  --secondary <fallback-answer-file> --secondary-label "External Agent"
```

Never re-invoke Codex for this review, never wait for a quota reset, and never turn "Codex unavailable"
into a WARN or BLOCK: the verdict comes from what the agents found (Step 4 rules). Never write "Codex
approved" or "cross-validated by Codex" unless the status was `ok`.

## Step 3: Merge & Deduplicate

Once the Stage 1 agent and all 4 Stage 2 agents return:

1. **Collect** all findings into a single list
2. **Deduplicate** — if two or more agents flag the same issue (same file, same line, similar description):
   - Keep the most detailed version
   - Note cross-validation: `[Confirmed by 2/4 agents]`, `[Confirmed by 3/4 agents]`, or `[Confirmed by all 4 agents]`
   - **Boost confidence** — cross-validated issues are almost certainly real
3. **Unique findings** — issues only one agent caught get tagged with their source:
   `[Architecture Agent]`, `[Framework Agent]`, `[Security Agent]`, or `[Codex Agent]`
4. **Codex checklist lines** — every `FAIL` line of the merged checklist table (Agent 3 routing) becomes a
   finding with the line's severity, tagged `[Codex Agent]`, `[Codex (partial)]` or `[External Agent]` as
   merged. `OTHER` items are findings too. `PASS` and `N-A` lines are not findings; keep the merged table for
   the report's Codex coverage line.
5. **Out-of-scope observations** — merge the `Out-of-scope observations` lists
   from Agents 1A, 1B, 2, and 3 into a single deduplicated list. For each entry:
   - If the responsible agent (or Codex) already reported the same `file:line`
     as a full finding, **drop** the out-of-scope note — the full finding wins.
   - If no agent caught it as a full finding, keep the note as a hint in the
     dedicated report section (see Step 4). Do NOT upgrade it to a finding —
     it was flagged without full analysis.

## Step 4: Severity Classification & Report

Organize the unified findings into a structured report:

### Output Format

```markdown
# Code Review Report

**Scope:** {description of what was reviewed}
**Files reviewed:** {count}
**Spec source:** {plan.md / PR description / branch name / user context / none}
**Conventions enforced:** {comma-separated rule files loaded in Step 0.6, with count — e.g. "7 files: AGENTS.md, .claude/rules/typescript.md, …" — or "NONE FOUND" only if the repo genuinely has no rule files/directory}
**Review mode:** Two-stage (Spec Compliance + 4-agent parallel Code Quality)
**Fix mode:** {enabled / disabled}
**Codex:** {complete, 31/31 | Claude-led; Codex partial: <n> items | Claude-only; Codex unavailable: <status>[ until <time>]}
**Evidence:** {review-evidence.md fresh at <head> | stale or missing: <why>}

---

## Stage 1: Spec Compliance

**Spec source:** {source description or "No spec found — stage skipped"}

### Requirements Coverage: {X of Y implemented}
### Scope Verdict: {CLEAN / MINOR CREEP / SIGNIFICANT CREEP}
### Compliance Verdict: {PASS / PARTIAL / FAIL}

{If findings exist, list them here by severity with the same format as Stage 2}

{If no spec was found: "[Spec Compliance: SKIPPED — no spec/plan/issue found]"}

---

## Stage 2: Code Quality

### CRITICAL ({count})
> Issues that MUST be fixed before merge. Security vulnerabilities, data loss risks, crash bugs.

#### 1. [File:Line] Issue Title
**Source:** [Architecture Agent] [Confirmed by 2/4 agents]
**Issue:** Description
**Fix:**
```suggestion
code fix here
```

---

### HIGH ({count})
> Issues that SHOULD be fixed. Bugs, missing error handling, performance problems.

...

### MEDIUM ({count})
> Code quality issues. DRY violations, naming, missing types.

...

### LOW ({count})
> Best practices, documentation, minor improvements.

...

---

## Out-of-scope Observations

Notes from Agents 1A/1B/2/3 about items outside their assigned checklist. These
were NOT fully analyzed — treat as hints for manual follow-up, not as findings.
Entries already captured as full findings above have been dropped.

- file:line — short description [noticed by: Architecture Agent]
- file:line — short description [noticed by: Framework Agent]
- ...

(or: "None")

---

## Summary

| Stage | Severity | Count | Status |
|-------|----------|-------|--------|
| 1     | CRITICAL | X     | BLOCK  |
| 1     | HIGH     | X     | WARN   |
| 2     | CRITICAL | X     | BLOCK  |
| 2     | HIGH     | X     | WARN   |
| 2     | MEDIUM   | X     | INFO   |
| 2     | LOW      | X     | NOTE   |

### Verdict: {APPROVE / WARN / BLOCK}
- **BLOCK** — Stage 1 compliance FAIL, OR any CRITICAL issues in either stage
- **WARN** — Stage 1 PARTIAL compliance, OR HIGH issues present (conditional approval)
- **APPROVE** — Stage 1 PASS (or skipped), no CRITICAL or HIGH issues

### Cross-Validation Confidence
- {N} issues confirmed by multiple agents (high confidence)
- {N} issues from single agent (review recommended)
```

## Step 5: Present & Act

1. Present the full report to the user
2. **Clean up temp files (mandatory).** As you present the findings, delete every
   temporary artifact this review created — nothing must leak into the workspace or
   `/tmp`. The Agent 3 snippet deliberately has NO EXIT trap (a backgrounded run's
   EXIT fires in a different shell), so this explicit cleanup is the only one:
   ```bash
   rm -f /tmp/review-diff-*.txt /tmp/review-prompt-*.txt /tmp/review-codex-*
   ```
   This is safe to run unconditionally — `--fix` (Step 6) edits real source files via
   the Edit tool and never reads these temps. The review scratchpad
   (`.workspace/ctx/review/`) is cleared at the very end (Step 6 if `--fix`, otherwise
   here): `rm -rf .workspace/ctx/review/`.
3. If `--fix` flag is **NOT** set:
   - If verdict is **BLOCK** or **WARN**, offer to fix: "Want me to fix the CRITICAL/HIGH issues now?"
   - If verdict is **APPROVE**, confirm: "Changes look good. Ready to commit/push/PR."
4. If `--fix` flag **IS** set, proceed directly to Step 6.

## Step 6: Auto-Fix (only with --fix flag)

When `--fix` is active, apply fixes for all CRITICAL and HIGH severity findings:

1. **Read each affected file** in full before making changes
2. **Apply fixes** using the Edit tool — one finding at a time, verifying each fix
3. **Group and commit** fixes by category:
   ```bash
   git add <files>
   git commit -m "refactor: <category description> (review-changes --fix)"
   ```
4. **Re-validate** — after all fixes, run a quick single-agent pass on the changed files
   to confirm no regressions were introduced. Fixes change the tree, so
   `evidence.py check .workspace/ctx/review/review-evidence.md` now exits 6: re-run the evidence
   commands and rewrite the file before any further review pass (never reuse stale evidence). Do NOT
   re-invoke Codex to confirm fixes; a confirmation pass is Claude-only and scoped to the fix diffs
   (parent..commit of each fix).
5. **Report** — append a fix summary to the review report:
   ```
   ## Auto-Fix Summary
   - {N} CRITICAL issues fixed
   - {N} HIGH issues fixed
   - {N} issues skipped (require manual intervention — listed below)
   ```
6. **Final cleanup** — once fixes are committed and the summary is presented, remove any
   remaining temporary artifacts and the review scratchpad:
   ```bash
   rm -f /tmp/review-diff-*.txt /tmp/review-prompt-*.txt /tmp/review-codex-*
   rm -rf .workspace/ctx/review/
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
- **Checkpoint frequency:** After Step 3 (merge & deduplicate findings)
- **Subagent delegation:** Spec compliance agent (Step 1), all 4 review agents (Step 2), re-validation after auto-fix (Step 6)

## When to Skip Agents

- If `--light` is passed, run ONLY Agent 1A inside a single subagent — see "Light Mode" above
- If changes are < 20 lines, use a single Claude subagent with the combined checklist instead of 4 parallel agents
- If the user says "quick review", skip Agent 3 (Codex), merging findings from Agents 1A, 1B & 2 only
- If Codex is unavailable (preflight or classify says anything but `ok`), the Claude fallback answers the same checklist once; see Agent 3's routing table. Never retry Codex, never block on it.

## Confidence Filtering Rules

These apply to ALL agents:

- Only report findings with >80% confidence of a genuine issue
- Do NOT flag stylistic preferences — UNLESS they violate a rule in the
  `{PROJECT_CONVENTIONS}` loaded in Step 0.6. Every agent receives those rules in its
  prompt, so "it violates a project convention" is now a verifiable claim, not a guess:
  cite the rule's source file. A written repo rule is authoritative and always reportable.
- Skip unchanged code issues unless they are CRITICAL security concerns
- Consolidate similar findings — don't list the same pattern 5 times across 5 files
- Prioritize bugs, security vulnerabilities, and data loss risks over style

### Scope Discipline (Claude agents 1A, 1B, and 2)

Each Claude agent's checklist is the *entire* scope of its review. Depth in
the assigned domain beats breadth across domains — another agent already owns
the rest. Rules:

- Do NOT analyze issues outside your checklist. Do not spend reasoning budget
  on them.
- If you incidentally notice something clearly outside your scope, record it
  under a final `## Out-of-scope observations` section as a single line:
  `file:line — one-sentence description`. No severity. No fix. No code block.
- If an issue straddles two checklists (e.g. a perf problem caused by a type
  bug), report it under yours only if your checklist explicitly covers it;
  otherwise leave it for the responsible agent.
- Codex (Agent 3) is scoped by its own checklist (`references/codex-checklist-review.md`) plus at most
  5 `OTHER` items; it does not repeat the Claude agents' lists.
- Stage 1 (spec compliance) is also exempt — its scope is already narrow and
  orthogonal to Stage 2.

---

## Feature Context Integration

When a feature-context is active, this skill writes review findings:

1. **After review completes:** Write the severity summary (CRITICAL/HIGH/MEDIUM/LOW counts) to feature-context
2. **After auto-fix:** Write which issues were auto-fixed and which remain
3. **Data written:** finding count by severity, files reviewed, auto-fix results, escalation decisions (e.g. to observability-audit)
