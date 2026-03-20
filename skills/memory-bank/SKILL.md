---
name: memory-bank
description: |
  Preserve and restore project knowledge across Claude Code sessions using a structured
  memory-bank/ directory. Use this skill whenever the user mentions "memory bank", "init memory",
  "update context", "save project context", "preserve knowledge", "project knowledge", "mb init",
  "mb update", "remember this for next time", or "save what we learned". Also trigger when the
  user explicitly asks to restore context from a previous session or wants persistent project
  knowledge beyond a single conversation.
version: 1.0.0
category: persistence
depends: []
---

# Memory Bank

Maintain structured, project-scoped context that persists across Claude Code sessions.

## Why Memory Bank vs Auto-Memory

| | Memory Bank | Auto-Memory (~/.claude/) |
|---|---|---|
| Scope | Project (repo root) | Global/per-project path |
| Structure | 5 specialized files | 1 generic MEMORY.md |
| Shareability | Git-committable, team-visible | Personal, not shared |
| Format | Strict templates, scannable | Freeform |

---

## Operations

### 1. INIT — Create memory-bank from scratch

**Trigger:** user says "mb init", "init memory", or you detect no `memory-bank/` directory when the user explicitly asks for it.

**Steps:**

1. Create `memory-bank/` in the project root.
2. **Codebase analysis (Tier 0):** Before reading config files, scan the directory tree (top-level + one level deep in `src/`, `app/`, `lib/`, `packages/`) to understand project shape. Then read 2-3 key source files — entry points detected from config (e.g., `main` field in package.json) or common patterns (`src/index.*`, `src/main.*`, `app.*`, `main.*`). Use this to generate a richer project-brief even when README is missing or minimal.
3. Auto-detect project info by reading available files. Scan in tiers:
   - **Tier 1 (identity):** `README.md`, `README.*`
   - **Tier 2 (stack):** `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle*`, `*.csproj`, `Gemfile`, `composer.json`
   - **Tier 3 (config):** `tsconfig.json`, `vite.config.*`, `webpack.config.*`, `.eslintrc*`, `prettier.config.*`
   - **Tier 4 (infra):** `docker-compose.yml`, `Dockerfile*`, `.env.example`, `terraform/*.tf`
   - **Tier 5 (CI/docs):** `.github/workflows/*` (first file), `Makefile`, `justfile`
   - **Tier 6 (workspace):** `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json` (monorepo detection)
4. Populate each of the 5 files using the templates below, filling in what you can.
5. For anything you cannot determine, ask the user concise questions grouped by file. Do NOT ask about things already resolved from source.
6. Write all 5 files.
7. Report what was auto-populated vs what needs user input.

**Edge cases:**
- **Empty repo:** Create all 5 files with template skeletons, mark sections as `<to be determined>`.
- **Monorepo:** Note workspace structure in `system-patterns.md`, list packages/apps found.
- **memory-bank/ partially exists:** Read existing files, create only missing ones, do not overwrite.

### 2. UPDATE — Refresh memory-bank with current state

**Trigger:** user says "mb update", "update context", "save project context", or explicitly asks to save session knowledge.

**Steps:**

1. Read all 5 existing memory-bank files.
2. Read relevant project config files (same tiers as INIT) to detect changes.
3. For each file that has changed information:
   - **Add** new entries reflecting current state.
   - **Prune** stale entries: completed tasks, resolved challenges, outdated info.
   - **Preserve** user edits — do not overwrite manual changes without asking.
4. Timestamp all changes in `active-context.md` using ISO-8601 format (`YYYY-MM-DD`).
5. Write only the files that actually changed.
6. Report what was updated and what was pruned.

**Pruning rules:**
- Completed tasks: remove from "Next Steps".
- Resolved challenges: remove from "Open Challenges".
- Decisions: keep all decisions that still influence the codebase. Only archive decisions that are fully superseded. When in doubt, keep.
- Session log: keep last 15 entries. Move older entries to `memory-bank/archive/sessions.md` (create if needed).

**Edge cases:**
- **Missing files:** Recreate from template, then update.
- **Conflicting info:** Ask user which version is correct rather than guessing.

### 3. READ — Restore context at session start

**Trigger:** user explicitly asks for context restoration ("memory bank", "load context", "project knowledge"), or you detect `memory-bank/` and the user asks you to resume previous work.

**Steps:**

1. Check if `memory-bank/` exists in the project root.
2. If it exists, read all 5 files in this order:
   - `project-brief.md` — what is this project
   - `tech-context.md` — what tools and stack
   - `system-patterns.md` — how is it built
   - `product-context.md` — how it behaves for users
   - `active-context.md` — what's happening now
3. Summarize the restored context in 3-8 bullets (scale with project complexity).
4. Highlight any open blockers or unresolved challenges.
5. Offer to continue from the most recent "Next Steps".

**Edge cases:**
- **Some files missing:** Read what exists, note what's missing, offer to run INIT to fill gaps.
- **Stale active-context:** If last update is >14 days old, flag it and suggest an UPDATE before proceeding.

---

## File Templates

Every file follows a strict format. Use bullet points for entries. Each entry should be concise (aim for 1-3 lines, max 5). Brief cross-references between files are allowed when necessary.

### memory-bank/project-brief.md

```markdown
# Project Brief

## Identity
- Name: <project name>
- Repo: <repo URL or "local only">
- Description: <one-line summary>

## Goals
- <goal 1>
- <goal 2>
- <goal 3>

## Target Users
- <user type>: <what they need>

## Non-Goals
- <explicit non-goal>

## Success Criteria
- <measurable outcome>
```

### memory-bank/product-context.md

```markdown
# Product Context

## User-Facing Behavior
- <key behavior>

## UX Decisions
- <decision>: <rationale>

## Key User Flows
- <flow name>: <step1> -> <step2> -> <step3>

## API Surface
- <endpoint/command>: <purpose>

## Known Issues
- <issue>: <status>
```

### memory-bank/system-patterns.md

```markdown
# System Patterns

## Architecture
- Style: <monolith/microservices/serverless/monorepo/etc.>
- Entry point: <main file or command>

## Key Abstractions
- <name>: <what it represents>

## Design Patterns
- <pattern>: <where and why>

## Component Relationships
- <A> -> <B>: <relationship>

## Directory Structure
- <dir/>: <purpose>

## Critical Paths
- <operation>: <file1> -> <file2> -> <file3>
```

### memory-bank/tech-context.md

```markdown
# Tech Context

## Stack
- Language: <lang> <version>
- Framework: <framework> <version>
- Runtime: <runtime> <version>

## Key Dependencies
- <dep>@<version>: <why used>

## Dev Setup
- Install: <command>
- Run: <command>
- Test: <command>
- Build: <command>
- Lint: <command>

## Infrastructure
- Hosting: <where>
- CI/CD: <what>
- Database: <what>

## Constraints
- <constraint>: <reason>

## Environment Variables
- <VAR_NAME>: <purpose> (required/optional)
```

### memory-bank/active-context.md

```markdown
# Active Context

## Current Focus
<!-- Updated: YYYY-MM-DD -->
- <what you're working on>

## Open Challenges
<!-- Updated: YYYY-MM-DD -->
- <challenge>: <status>

## Recent Decisions
<!-- Updated: YYYY-MM-DD -->
- [YYYY-MM-DD] <decision>: <rationale>

## Next Steps
<!-- Updated: YYYY-MM-DD -->
- [ ] <task 1>
- [ ] <task 2>

## Session Log
- [YYYY-MM-DD] <what was accomplished>
```

---

## Rules

1. **Bullet points preferred** — use structured entries, not paragraphs. Brief inline context is acceptable when it adds clarity.
2. **Keep entries concise** — aim for 1-3 lines per entry, 5 lines max. If longer, split into sub-entries.
3. **Timestamp active-context.md** — every section gets `<!-- Updated: YYYY-MM-DD -->`, every decision and log entry gets `[YYYY-MM-DD]`.
4. **Prune by relevance, not age** — remove completed/resolved/superseded items. Keep durable decisions regardless of age.
5. **Minimize duplication** — each fact has a primary home in one file. Brief cross-references (e.g., "see system-patterns.md") are fine.
6. **Keep it scannable** — a new session should restore full context from all 5 files in under 60 seconds of reading.
7. **Ask, don't guess** — if you cannot determine something from source files, ask the user.
8. **Preserve user edits** — if a user manually edited a file, respect their structure and content.
9. **Never store secrets** — no tokens, passwords, API keys, or private credentials. If detected, remove immediately and warn the user.
10. **Manage growth** — archive session logs beyond 15 entries to `memory-bank/archive/sessions.md`.

---

## File Ownership Guide

| Information | Primary File |
|---|---|
| Project name, goals, users, scope | `project-brief.md` |
| UI/UX, user flows, API surface | `product-context.md` |
| Architecture, patterns, directory layout | `system-patterns.md` |
| Stack, deps, dev commands, infra | `tech-context.md` |
| Current work, decisions, tasks, log | `active-context.md` |

---

## Example Session Flows

**First time — new project:**
1. User: "mb init"
2. Agent reads README, package.json, tsconfig.json
3. Agent creates all 5 files, fills detected info
4. Agent: "Created memory-bank. Auto-populated stack (Next.js 14, Prisma, PostgreSQL) and project description from README. Questions: Who are the target users? What are the current priorities?"
5. User answers, agent updates files

**Returning — new session:**
1. User: "memory bank" or "load context"
2. Agent reads all 5 files
3. Agent: "Context restored. Project: [X]. Stack: [Y]. Last session you [Z]. Open challenges: [A]. Next steps: [B, C]. Want to continue with B?"

**End of session:**
1. User: "mb update"
2. Agent reads current memory-bank + project files
3. Agent: "Updated active-context.md: added session log, completed 2 tasks, added 3 next steps. Tech-context.md: updated React version to 19."

---

## Git Integration

Recommend committing `memory-bank/` to version control:

```bash
git add memory-bank/
git commit -m "docs: update memory-bank context"
```

This shares project knowledge with the team and future AI sessions.
If a team prefers local-only, add `memory-bank/` to `.gitignore`.
