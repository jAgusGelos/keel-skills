---
name: context-management
description: >
  Reusable context management protocol for long-running AI agent tasks. Prevents context
  window exhaustion, preserves critical state across compactions, and maintains coherence
  over many iterations. Use this skill as a foundation protocol inside any multi-step
  workflow skill (cc-cc-powerful-iterations, multiple-iterations-reasoning, three-experts,
  tdd, problem-solver, spec-first, e2e-agent, etc.). Trigger when a task will span 10+
  tool calls, multiple phases, or when the agent detects context pressure (approaching
  60% window usage). Also trigger when the user says "manage context", "don't lose track",
  "this is a long task", or when a skill's instructions say "apply context-management
  protocol".
version: 1.0.0
category: persistence
depends: [feature-context]
---

# Context Management Protocol

Prevent context loss, maintain coherence, and survive compactions in long-running agent tasks.

## Why This Exists

AI agents working on complex tasks fail predictably: context windows fill with verbose tool
outputs, critical decisions get compacted away, and the agent loses track of what it already
tried. Research shows failure rates quadruple when task duration doubles. This protocol solves
that with three mechanisms: **external memory** (disk survives compaction), **context hygiene**
(keep the window clean), and **checkpoint discipline** (resume without loss).

## The Three Pillars

```
                    ┌─────────────────────┐
                    │   Context Window     │
                    │  (working memory)    │
                    │                      │
                    │  Recent turns only   │
                    │  Compact results     │
                    │  Current phase focus │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │  External   │  │  Context   │  │ Checkpoint │
     │  Memory     │  │  Hygiene   │  │ Discipline │
     │             │  │            │  │            │
     │ .workspace/ │  │ Subagents  │  │ Phase gates│
     │ scratchpad  │  │ Truncation │  │ Resume pts │
     │ files       │  │ Delegation │  │ State snaps│
     └────────────┘  └────────────┘  └────────────┘
```

---

## Pillar 1: External Memory (Scratchpad Files)

Write structured state to disk so it survives context compaction and session boundaries.

### File Structure

At task start, create this structure:

```
.workspace/ctx/{skill-name}/
├── state.md          # Current task state (single source of truth)
└── decisions.md      # Key decisions with rationale (append-only)
```

Each skill uses its own subdirectory (e.g., `.workspace/ctx/cc-cc/`, `.workspace/ctx/tdd/`).
When running **multiple instances** of the same skill concurrently, add a task-id suffix:
```
.workspace/ctx/{skill-name}-{task-id}/
```

### state.md Format

```markdown
# Task State
<!-- Updated at each checkpoint. This is what the agent reads after compaction. -->

## Objective
[1-2 sentences: what we're building/solving]

## Current Phase
[Phase name and step number]

## Key Constraints
- [Constraint 1]
- [Constraint 2]

## Progress
- [x] Phase 1: [what was done, key outcome]
- [x] Phase 2: [what was done, key outcome]
- [ ] Phase 3: [what needs to happen next] <-- CURRENT
- [ ] Phase 4: [pending]

## Active Context
<!-- Only what matters RIGHT NOW for the current phase -->
- Working in: [file paths]
- Blocked by: [nothing / description]
- Last output: [1-line summary of most recent significant result]

## Artifacts
- [path/to/spec.md] — engineering spec
- [path/to/test-file.spec.ts] — test file
```

### decisions.md Format

```markdown
# Decisions Log
<!-- Append-only. Never edit past entries. -->

## [D1] 2026-03-10 — Chose PostgreSQL over Redis for queue
- **Context:** Need persistent job queue with exactly-once semantics
- **Alternatives considered:** Redis Streams, SQS
- **Why this:** ACID guarantees, existing Prisma setup, no new infra
- **Impact:** Affects Phase 3 schema design

## [D2] 2026-03-10 — Use subagent for test execution
- **Context:** Test suite output is 500+ lines, would flood context
- **Why this:** Keep main context clean, only need pass/fail + failure details
```

### When to Write

| Event | Action |
|-------|--------|
| Task starts | Create `state.md` with objective, constraints, initial plan |
| Phase completes | Update `state.md` progress section |
| Non-obvious decision made | Append to `decisions.md` |
| Before a risky operation | Checkpoint `state.md` with current state |
| After compaction detected | Re-read `state.md` before next action |

### When to Re-Read State (Compaction Triggers)

Re-read your `state.md` on these **mechanical triggers** — do not rely on introspection:
- At the **start of every new session** or conversation continuation
- After a **system summary/compaction message** appears in conversation
- Every **15 tool calls** during a long phase (set a mental counter)
- When you **cannot cite a specific detail** from a phase you completed earlier

**Recovery procedure:** Read `.workspace/ctx/{skill-dir}/state.md` → orient → continue from `Current Phase`.

---

## Pillar 2: Context Hygiene

Keep the context window focused on what matters for the current step.

### Rule 1: Delegate Verbose Operations to Subagents

Operations producing ~100+ lines of output should generally run in a subagent. Use judgment
— structured output up to ~150 lines may be worth keeping if the main agent needs to act on
specifics.

**Always delegate:**
- Test suite execution (return: pass/fail + first 3 failures)
- Large file reads (return: relevant sections only)
- Log/error analysis (return: summary + key entries)
- Search across many files (return: top N matches with context)
- Build/compile checks (return: success or error list)

**Subagent result template:**
```
## [Operation] Result
- **Status:** pass/fail/partial
- **Key findings:** [2-5 bullet points]
- **Details needed:** [only if the main agent needs to act on specifics]
- **Files touched:** [list if relevant]
```

### Rule 2: Summarize Before Moving On

After completing a phase, before starting the next:
1. Write a 3-5 line summary of what was accomplished
2. Update `state.md` with the summary
3. Drop mental attachment to the details — they're on disk now

### Rule 3: One Phase in Focus

Only load context relevant to the current phase. Don't re-read files from Phase 1
when you're executing Phase 3, unless Phase 3 explicitly depends on those details.

### Rule 4: Prefer Compact Tool Outputs

When reading files, use `offset` and `limit` to read only the relevant section.
When searching, use `head_limit` to cap results. When running commands, pipe through
`head` or `tail` if full output isn't needed.

---

## Pillar 3: Checkpoint Discipline

Create explicit save points so the task can resume cleanly from any phase.

### Phase Gate Protocol

Before transitioning between phases:

```
1. CHECKPOINT — Update state.md (progress, current phase, active context)
2. VALIDATE  — Does state.md have enough info to resume cold? Read it back and verify.
3. ANNOUNCE  — Tell the user: "Phase N complete. Starting Phase N+1: [description]"
4. PROCEED   — Begin the next phase with a fresh mental frame
```

### Checkpoint Triggers

Create a checkpoint (update `state.md`) when:
- A phase or sub-phase completes
- A significant decision is made
- An unexpected discovery changes the plan
- Before any operation that might fail (deploy, large refactor, migration)
- Every 15-20 tool calls in a long phase (time-based checkpoint)

### Resume Protocol

When resuming (new session, after compaction, or user returns):

```
1. READ    — .workspace/ctx/{skill-dir}/state.md
2. READ    — .workspace/ctx/{skill-dir}/decisions.md (scan for recent entries)
3. ORIENT  — Identify current phase and next action
4. VERIFY  — Check that referenced files/artifacts still exist
5. ANNOUNCE — "Resuming from Phase N, Step M: [what's next]"
6. CONTINUE — Pick up from the checkpoint
```

---

## Integration Guide for Other Skills

Skills that run long workflows should reference this protocol. Add this to your skill:

```markdown
## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/{skill-name}/`
- **Checkpoint frequency:** [after each cycle / after each phase / every N steps]
- **Subagent delegation:** [list operations that must be delegated]
```

### Mapping to Common Skills

| Skill | Scratchpad Dir | Checkpoint At | Delegate |
|-------|---------------|---------------|----------|
| `cc-cc-powerful-iterations` | `.workspace/ctx/cc-cc/` | After Steps 1, 2, 3, 4 | Codex execution, Claude validation |
| `multiple-iterations-reasoning` | `.workspace/ctx/iterations/` | After each round (gate + changelog) | Codex validation, self-consistency checks |
| `three-experts` | `.workspace/ctx/three-experts/` | After each deliberation round | Sub-point factual resolution |
| `tdd` | `.workspace/ctx/tdd/` | After each red-green-refactor cycle | Test execution, lint/type checks |
| `problem-solver` | `.workspace/ctx/problem-solver/` | After each step (1-7) | Test execution, three-experts, iterations |
| `spec-first` | `.workspace/ctx/spec-first/` | After Steps 2, 5, 6, 7 | Parallel research threads, three-experts |
| `e2e-agent` | `.workspace/ctx/e2e/` | After Steps 0, 1, 3, 5 | Claude/Codex test writing, Codex review |
| `review-changes` | `.workspace/ctx/review/` | After Step 2 (merge) | All 3 review agents |

### Minimal Integration (3 lines)

For skills that just need basic protection, add these three instructions:

```
1. At task start: create .workspace/ctx/{skill}/ with state.md
2. At phase transitions: update state.md progress section
3. For outputs >100 lines: delegate to subagent, capture summary only
```

---

## Decision: When to Apply This Protocol

Not every task needs full context management. Use this decision tree:

```
Is the task likely to exceed 20 tool calls?
├─ No  → Skip protocol. Just do the work.
├─ Yes → Will it have 3+ distinct phases?
│   ├─ No  → Use Minimal Integration (3 lines above)
│   └─ Yes → Will it involve verbose tool outputs (tests, builds, large reads)?
│       ├─ No  → Use Pillar 1 (scratchpad) + Pillar 3 (checkpoints)
│       └─ Yes → Use Full Protocol (all 3 pillars)
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Instead |
|-------------|-------------|---------|
| Keeping full test output in context | 500+ lines that compress into "14 passed, 2 failed" | Delegate to subagent |
| Re-reading entire files every phase | Wastes tokens on unchanged content | Read once, note relevant sections in state.md |
| No scratchpad ("I'll remember") | Compaction will erase it | Always write state.md |
| Over-detailed state.md | 200-line state file defeats the purpose | Keep under 50 lines; use `## Artifacts` for large content |
| Checkpoint only at the end | Lose everything if interrupted mid-task | Checkpoint at every phase gate |
| Reading state.md every tool call | Wastes tokens when you haven't lost context | Only after compaction or session resume |

---

## Quality Checklist

Before completing a long-running task, verify:

- [ ] `state.md` reflects final state (all phases marked complete)
- [ ] `decisions.md` captures non-obvious choices
- [ ] No verbose tool outputs remain in context that could have been delegated
- [ ] User received phase transition announcements
- [ ] Task artifacts are in their final locations (not just in scratchpad)
