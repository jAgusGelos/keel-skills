---
name: feature-context
description: |
  Per-feature context persistence across Claude Code sessions. The middle layer between
  context-management (session-scoped) and memory-bank (project-scoped). Tracks spec iterations,
  decisions, implementation progress, review feedback, and user inputs for a single feature
  over days or weeks. Survives session restarts and context compaction.
  Use this skill whenever the user mentions "feature context", "init feature", "start feature",
  "resume feature", "continue feature", "feature trace", "feature done", "complete feature",
  "archive feature", "what was I working on", "pick up where I left off", or when starting
  work on a named ticket/feature that will span multiple sessions. Also trigger when spec-first
  starts planning a named feature and no feature context exists yet, or when the user says
  "save feature progress", "feature status", "feature decisions", or asks to see what happened
  on a feature across sessions.
version: 1.0.0
category: persistence
depends: []
---

# Feature Context

Persist per-feature knowledge across sessions. Every feature gets a trace of what happened,
what was decided, and what comes next — so a fresh session can resume without loss.

## Why This Exists

Developers lose context between sessions. Sumanyu manually copies chat history to new sessions.
Duc loses track of customer ops work across long sessions. `context-management` only survives
within a session. `memory-bank` is project-scoped — too broad for per-feature work. This skill
fills the gap: feature-scoped persistence that lives for days or weeks, then archives on merge.

```
memory-bank/              PROJECT scope (permanent)
.features/{id}/           FEATURE scope (days-weeks)     <-- this skill
.workspace/ctx/{skill}/   SESSION scope (ephemeral)
```

**Boundary rule:**
- Only useful for current execution? -> `.workspace/ctx/`
- Useful until feature merges? -> `.features/`
- Should influence future unrelated features? -> `memory-bank/`

---

## File Structure

```
.features/
  registry.json                 # Machine-owned index (auto-generated, never hand-edit)
  {feature-id}/
    meta.json                   # Machine-readable: status, branch, timestamps, artifacts
    status.md                   # Human-readable resume summary (<40 lines)
    trace.md                    # Append-only timeline of all events
    decisions.md                # Append-only feature decisions with rationale
  .archive/
    {feature-id}/
      meta.json                 # Preserved
      summary.md                # Compressed final record
      decisions.md              # Preserved for auditability
```

**Ownership:** Only this skill writes to `meta.json`, `status.md`, and `registry.json`.
Other skills provide event data; this skill writes it. This prevents multi-writer drift.

`trace.md` and `decisions.md` are also written by this skill, using data provided by
other skills through the WRITE operation.

---

## Operations

### 1. INIT — Create feature context

**Trigger:** User says "init feature", "start feature {id}", or `spec-first` starts planning
a named feature without existing context.

**Steps:**

1. Parse feature ID from user input.
   - If ticket number only (e.g., "PROJ-421"), ask for a short slug or auto-generate:
     `PROJ-421-oauth-payments`
   - If no ticket, use: `feature-YYYYMMDD-{slug}`

**Security: Validate the feature ID before using it as a path:**
- Strip any characters other than `[a-zA-Z0-9._-]`
- Reject IDs containing `..`, `/`, or `\`
- Truncate to 100 characters max
- Verify the resolved path is within the project directory

2. Check if `.features/{id}/` already exists.
   - Status `active`: offer to RESUME instead.
   - Status `completed`/`archived`: ask if this is a new iteration.
3. Create `.features/` directory if it does not exist.
4. Create `.features/{id}/` with all template files (see Templates below).
5. Create or update `.features/registry.json` with the new entry.
6. Log initial event to `trace.md`.
7. Announce: "Feature context created at `.features/{id}/`. All skills will log to this trace."

**Edge cases:**
- `.features/` does not exist: create it.
- `registry.json` does not exist: create it with the new entry.
- User provides no title: ask for one — it is required for `status.md` and `registry.json`.

### 2. WRITE — Log events from other skills

**Trigger:** Another skill has completed a significant step on an active feature. This is
called programmatically, not by the user directly.

**Protocol for skills writing to feature context:**

1. **Resolve active feature:**
   - If feature ID is explicitly known (passed from calling skill): use it.
   - Otherwise read `registry.json` and match by current git branch name.
   - If multiple active features match or no match: ask the user.
2. **Receive event data** from the calling skill:
   - `skill`: name of the calling skill (e.g., "spec-first", "three-experts")
   - `event`: short summary of what happened
   - `type`: one of `spec-iteration`, `deliberation`, `user-decision`, `implementation`,
     `review`, `pr-feedback`, `rca`, `lifecycle`
   - `decision` (optional): if a feature-scoped decision was made, include:
     - `title`, `context`, `alternatives`, `chosen`, `rationale`, `impact`
   - `artifacts` (optional): updated artifact paths (plan, todo, PR number)
   - `phase` (optional): new phase if it changed
3. **Append to `trace.md`:**
   - Format: `- [YYYY-MM-DD HH:MM] {skill} — {event}`
   - Group entries by date using `### YYYY-MM-DD` headers.
   - If today's date header does not exist, add it.
4. **If decision provided:** Append to `decisions.md` using `[FD-N]` format.
   Increment N from the last entry.
5. **Update `meta.json`:** Set `lastUpdated`, `lastSkill`, and optionally `phase`,
   `artifacts`, `blockers`. Add event to `recentEvents` (keep last 20).
6. **Regenerate `status.md`** from `meta.json` + last 10 trace entries + decisions summary.
   Keep under 40 lines.

**Sensitive data rules:**
- NEVER store API keys, tokens, passwords, PII, or customer data.
- Redact prod data: use counts/patterns only, no raw records.
- If sensitive content is detected, warn the user before writing.

### 3. RESUME — Load feature context at session start

**Trigger:** User says "continue {feature-id}", "resume {feature}", "pick up where I left
off", or a new session starts on a branch that matches an active feature.

**Steps:**

1. **Find the feature:**
   - If user provided an explicit feature ID: use it.
   - Otherwise check `registry.json` for a branch match against the current git branch.
   - If multiple active features exist and none match: list them and ask.
   - If no `.features/` directory exists: inform user, offer to INIT.
2. **Read feature context:**
   - Read `meta.json` — machine-readable state.
   - Read `status.md` — human-readable summary.
   - Read last 30 lines of `trace.md` — recent activity.
   - Read `decisions.md` — all feature-scoped decisions.
3. **Bridge to session context (optional):**
   - If `context-management` is active and `.workspace/ctx/{skill}/state.md` exists,
     prepend a `## Feature Context` section with: objective, phase, key context, blockers.
   - If `context-management` is not active: this skill handles resume directly.
4. **Stale check:** If `meta.json.lastUpdated` is >14 days old, warn the user and suggest
   completing or archiving the feature.
5. **Announce:** "Resuming {title}. Phase: {phase}. Last session: {date}."
   Then present the key context bullets from `status.md`.

### 4. COMPLETE — Freeze and summarize

**Trigger:** User says "feature done", "complete feature {id}", or PR is confirmed merged.

**Steps:**

1. Update `meta.json`: set status to `completed`, record completion date.
2. Generate `summary.md` by reading all feature files:
   - Duration (start to completion)
   - Session count (count date headers in `trace.md`)
   - Key decisions (from `decisions.md` — only those still relevant)
   - Lessons learned (ask user, or infer from review feedback in trace)
   - Metrics: spec iterations, review rounds, decisions made
3. Log final event to `trace.md`: `feature-context — Feature completed.`
4. Update `registry.json`: move entry from `active` to `archived` section with path.
5. **Promotion suggestions:** Scan `decisions.md` for patterns worth promoting:
   - Architecture patterns -> `memory-bank/system-patterns.md`
   - Recurring lessons -> `memory-bank/active-context.md` or `CLAUDE.md`
   - Review patterns -> `pr-learning`
   Present suggestions to user. Do not auto-promote.

### 5. ARCHIVE — Move to cold storage

**Trigger:** User says "archive feature {id}". Manual only — no automatic archival.

**Steps:**

1. Move `.features/{id}/` to `.features/.archive/{id}/`.
2. Keep: `meta.json`, `summary.md`, `decisions.md` (for auditability).
3. Delete: `trace.md`, `status.md` (compressed into `summary.md`).
4. Update `registry.json`.

### 6. LIST — Show active features

**Trigger:** User says "list features", "active features", "what features am I working on".

**Steps:**

1. Read `registry.json`.
2. Present active features: ID, title, phase, last updated, branch.
3. If any are stale (>14 days), flag them.

---

## File Templates

### registry.json

```json
{
  "active": [],
  "archived": []
}
```

Active entry shape:
```json
{
  "id": "PROJ-421-oauth-payments",
  "title": "Add OAuth2 to Payments API",
  "status": "active",
  "branch": "feat/PROJ-421-oauth-payments",
  "started": "2026-03-10",
  "lastUpdated": "2026-03-14",
  "phase": "implementing"
}
```

### meta.json

```json
{
  "id": "{feature-id}",
  "title": "{Feature Title}",
  "status": "init",
  "branch": "{branch-name}",
  "ticket": "{PROJ-421 or null}",
  "created": "YYYY-MM-DD",
  "lastUpdated": "YYYY-MM-DDTHH:MM:SSZ",
  "lastSkill": null,
  "phase": "planning",
  "artifacts": {
    "plan": null,
    "todo": null,
    "pr": null
  },
  "blockers": [],
  "recentEvents": []
}
```

### status.md

```markdown
# {ID}: {Title}

## Current State
- **Phase:** {planning | implementing | reviewing | hardening}
- **Last session:** {YYYY-MM-DD}
- **Blocked by:** {nothing | description}

## Key Context for Resume
- {Most important thing to know}
- {Current approach or key decision}
- {What's done and what's remaining}

## Progress
- [x] {Completed phase}
- [ ] {Current phase} <-- CURRENT
- [ ] {Future phase}

## Artifacts
- Plan: {path or "not yet"}
- TODO: {path or "not yet"}
- Branch: {branch-name}
- PR: {#number or "not yet"}
```

### trace.md

```markdown
# Feature Trace: {Title}

<!-- Append-only. Format: [YYYY-MM-DD HH:MM] {skill} -- {event} -->

### {YYYY-MM-DD}

- [{HH:MM}] feature-context — Feature initialized: "{title}"
```

### decisions.md

```markdown
# Feature Decisions: {Title}

<!-- Append-only. For project-wide decisions, use memory-bank/ -->
```

Decision entry format (appended when a decision is made):
```markdown
## [FD-{N}] {YYYY-MM-DD} — {Decision title}
- **Context:** {Why this decision was needed}
- **Source:** {skill name or "user input"}
- **Alternatives:** {What else was considered}
- **Chosen:** {What was decided}
- **Rationale:** {Why, with evidence}
- **Impact:** {What this affects downstream}
```

### summary.md (generated on COMPLETE)

```markdown
# Feature Summary: {Title}

## Outcome
- **ID:** {feature-id}
- **Duration:** {start} -> {end} ({N} days)
- **Sessions:** {N}
- **PR:** #{number}
- **Status:** Completed

## What Was Built
- {1-3 sentence summary}

## Key Decisions
- [FD-1] {Decision}: {rationale}
- [FD-3] {Decision}: {rationale}

## Lessons Learned
- {Lesson 1}
- {Lesson 2}

## Metrics
- Spec iterations: {N}
- Review rounds: {N}
- Decisions made: {N}
```

---

## Size Management

| File | Strategy | Threshold |
|------|----------|-----------|
| `status.md` | Regenerated from meta.json + trace tail | Always <40 lines |
| `trace.md` | Rotate: move older entries to `trace-history.md`, keep recent 200 lines | At 300 lines |
| `decisions.md` | Never pruned (append-only) | Unlimited |
| `meta.json` | `recentEvents` capped at 20 entries | N/A |

When `trace.md` exceeds 300 lines:
1. Move all entries except the most recent 200 lines to `trace-history.md`.
2. Add a note at the top of `trace.md`: `<!-- Older entries in trace-history.md -->`
3. RESUME only reads `trace.md` (recent), not `trace-history.md`.

---

## Integration with Other Skills

Skills do not write directly to feature files. They provide event data, and this skill
writes it. Here is what each skill provides:

| Skill | Events provided | Includes decisions? |
|-------|----------------|-------------------|
| `spec-first` | Request captured, research done, unknowns resolved, plan generated, plan approved | Yes (architecture decisions from Steps 4-5) |
| `three-experts` | Deliberation started, consensus reached, dissent noted | Yes (architecture decisions) |
| `review-changes` | Review complete, findings summary, blocking issues | Sometimes (if findings change design) |
| `fix-pr-comments` | Comments loaded, comments resolved, design-changing feedback | Sometimes |
| `tdd` | Task started, task complete with test results | No |
| `stress-test` | Deal-breaker found, plan revision needed | Yes (if plan changes) |
| `create-pr` | PR created with number and URL | No |
| `start-investigation` | RCA started, RCA complete | Sometimes |

**Auto-init:** `spec-first` should invoke INIT when it starts planning a named feature
and no `.features/{id}/` exists.

**Bridge with context-management:** On session resume, `context-management` can check
`registry.json` for an active feature matching the current branch and prepend feature
context to the session scratchpad. This bridge is optional — this skill works standalone.

---

## Rules

1. **Single writer** — only this skill writes to `meta.json`, `status.md`, `registry.json`.
   Other skills provide data through the WRITE operation.
2. **Append-only logs** — never edit past entries in `trace.md` or `decisions.md`.
3. **Status under 40 lines** — `status.md` is regenerated, not manually maintained.
4. **No secrets** — never store API keys, tokens, passwords, PII, or customer data.
   Redact prod data observations (counts/patterns only).
5. **Ask, don't assume** — if feature ID is ambiguous, ask the user. Never guess.
6. **Manual archive only** — no automatic archival. The user decides when to archive.
7. **Preserve decisions on archive** — `decisions.md` is always kept for auditability.
8. **Git-committable by default** — `.features/` is meant to be committed. Teams can
   gitignore it if they prefer local-only.
9. **Promotion is explicit** — feature learnings are suggested for promotion to
   `memory-bank` on COMPLETE, but never auto-promoted.
10. **Timestamps use ISO-8601** — `YYYY-MM-DD` for dates, `YYYY-MM-DDTHH:MM:SSZ` for
    precise timestamps in `meta.json`.

---

## Example Flows

**Starting a new feature:**
1. User: "start feature PROJ-421 OAuth payments"
2. Agent creates `.features/PROJ-421-oauth-payments/` with all files
3. Agent: "Feature context created. Ready to track this feature across sessions."

**Resuming next day:**
1. User: "continue PROJ-421"
2. Agent reads `status.md`: "Phase: implementing. Last session: yesterday. Key context: ..."
3. Agent: "Resuming PROJ-421. You were implementing Task 2.1. Review found 1 HIGH issue."

**Completing after merge:**
1. User: "feature done PROJ-421"
2. Agent generates `summary.md`, suggests promoting adapter pattern to `memory-bank`
3. Agent: "Feature completed. Duration: 5 days, 7 sessions, 5 decisions. Archive when ready."

**Listing active work:**
1. User: "what features am I working on?"
2. Agent reads `registry.json`: "2 active features: PROJ-421 (implementing), PROJ-455 (planning)"
