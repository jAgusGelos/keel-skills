---
name: codebase-best-practices
description: |
  Investigate a codebase to detect its tech stack, component patterns, and architectural decisions.
  Fetch industry best practices for each detected technology via web search. Compare actual code
  patterns against best practices using cc-cc dual-engine validation. Generate markdown documentation
  files (.ai-patterns/) that any agent working on the repo can reference. Documents both standard
  best practices being followed AND non-standard patterns the team has chosen deliberately.
  Use when: "codebase best practices", "audit best practices", "document patterns", "what patterns
  does this codebase follow", "generate coding guidelines", "best practices audit", "code patterns",
  "stack best practices", "how should I write code here", "document conventions", "codebase audit",
  "pattern documentation", "generate patterns", "coding standards from code", "investigate codebase",
  "what are the conventions", "document best practices", "codebase conventions", "engineering guidelines".
---

# Codebase Best Practices

Investigate the codebase. Detect the stack. Fetch best practices. Compare. Generate pattern docs.
Uses cc-cc dual-engine for analysis quality. Output goes to `.ai-patterns/` for agent consumption.

## The Flow

```
[0] Detect environment + parse arguments
[1] Stack detection — scan package files, configs, imports
[2] Architecture scan — map components, layers, patterns
[3] Fetch best practices — web search per technology
[4] Compare via cc-cc — actual patterns vs best practices (dual-engine)
[5] Generate pattern documentation
[6] Present summary + offer refinement
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `--layer <layer>` | (all) | Limit scan to: `frontend`, `backend`, `infra`, or `all` |
| `--quick` | off | Skip cc-cc. Single Claude subagent analysis. Faster, less thorough. |
| `--output <dir>` | `.ai-patterns` | Output directory for generated docs |
| `--skip-fetch` | off | Skip web search. Use only codebase analysis (offline mode). |

## Step 0: Environment Detection

1. Check if inside a git repo. If not, warn and continue (patterns are still useful).
2. Parse arguments from user input.
3. Read `memory-bank/repo-context.md` if it exists — use as starting context to avoid
   redundant exploration. If it doesn't exist, proceed with full detection.
4. Set `$OUT_DIR` to the output directory (default `.ai-patterns/`).

## Step 1: Stack Detection

Scan the project to build a complete technology inventory.

### What to scan

| Signal | Files to check |
|---|---|
| Languages | `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.py`, `*.go`, `*.rs`, `*.java`, etc. |
| Package managers | `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml` |
| Frameworks | imports/requires in source files, config files (`vite.config`, `next.config`, `angular.json`) |
| Styling | `tailwind.config`, `postcss.config`, `.css` imports, styled-components usage |
| State management | imports of `zustand`, `redux`, `mobx`, `pinia`, `vuex`, `recoil`, `jotai` |
| Data fetching | imports of `react-query`, `swr`, `apollo`, `urql`, `axios`, `fetch` wrappers |
| ORM/DB | `drizzle.config`, `prisma/schema.prisma`, `sequelize`, `typeorm`, `knex`, `sqlalchemy` |
| Auth | `better-auth`, `next-auth`, `passport`, `clerk`, `supabase auth` |
| Testing | `jest.config`, `vitest.config`, `cypress.config`, `playwright.config`, `.mocharc` |
| CI/CD | `.github/workflows/`, `.gitlab-ci.yml`, `Dockerfile`, `docker-compose.yml` |
| Validation | imports of `zod`, `joi`, `yup`, `ajv`, `class-validator` |
| Linting | `.eslintrc`, `biome.json`, `.prettierrc`, `rustfmt.toml` |

### Output

Write stack inventory to `$OUT_DIR/_stack.json`:

```json
{
  "detected_at": "ISO timestamp",
  "languages": ["TypeScript"],
  "frontend": {
    "framework": "React 19",
    "styling": "Tailwind CSS 4",
    "state": "Zustand 5",
    "data_fetching": "@tanstack/react-query 5",
    "routing": "react-router-dom 7",
    "canvas": "@xyflow/react 12"
  },
  "backend": {
    "runtime": "Bun",
    "framework": "Hono",
    "orm": "Drizzle ORM",
    "database": "PostgreSQL (Neon)",
    "validation": "Zod",
    "auth": "better-auth"
  },
  "testing": {},
  "infra": {},
  "linting": {}
}
```

## Step 2: Architecture Scan

For each detected layer, investigate actual code patterns using subagents.

### Frontend patterns to detect

Spawn a Claude subagent to investigate:

1. **Component structure** — functional vs class, file naming, co-location of styles/tests
2. **State patterns** — where state lives (store vs local vs URL), how it flows
3. **Data fetching** — hook patterns, caching strategy, error/loading handling
4. **Styling approach** — utility-first vs component classes, dark theme implementation
5. **Type patterns** — how types are organized, shared types vs co-located
6. **Layout architecture** — page/layout/component hierarchy, routing patterns
7. **Form handling** — validation approach, controlled vs uncontrolled
8. **Error boundaries** — error handling strategy in UI
9. **Import patterns** — barrel exports, path aliases, relative vs absolute

### Backend patterns to detect

Spawn a separate Claude subagent to investigate:

1. **Route organization** — file-per-resource, middleware chains, auth patterns
2. **Service layer** — business logic separation, dependency injection or not
3. **Database patterns** — schema organization, migration strategy, query patterns
4. **Validation** — where validation happens, schema sharing with frontend
5. **Error handling** — error types, HTTP status mapping, error response format
6. **API design** — REST conventions, pagination, filtering, versioning
7. **Middleware** — chain structure, context passing, guard patterns
8. **Type sharing** — how types flow between frontend and backend

### Output per layer

Each subagent writes findings as structured JSON to `$OUT_DIR/_scan-{layer}.json`:

```json
{
  "layer": "frontend",
  "patterns": [
    {
      "area": "state-management",
      "pattern": "Zustand stores with flat state + actions in same create()",
      "evidence": ["orchestrator/src/store/workflowStore.ts", "orchestrator/src/store/navStore.ts"],
      "frequency": "consistent"
    }
  ]
}
```

## Step 3: Fetch Best Practices

For each technology in `_stack.json`, fetch current best practices via web search.

### Search strategy

Per technology, run 2-3 targeted searches:

```
"{technology} {version} best practices {year}"
"{technology} recommended patterns production"
"{technology} common mistakes anti-patterns"
```

Examples:
- `"React 19 best practices 2026"`
- `"Zustand 5 recommended patterns production"`
- `"Drizzle ORM best practices PostgreSQL"`
- `"Hono framework middleware patterns"`
- `"Tailwind CSS 4 best practices"`

### What to extract

From search results, extract:
- **Official recommendations** from framework/library docs
- **Community consensus** patterns (widely adopted, multiple sources agree)
- **Common anti-patterns** to avoid
- **Version-specific** guidance (especially for major versions)

### Output

Write to `$OUT_DIR/_best-practices-raw.json`:

```json
{
  "technology": "Zustand 5",
  "practices": [
    {
      "rule": "Use selectors to prevent unnecessary re-renders",
      "source": "official docs / community consensus",
      "importance": "high",
      "category": "performance"
    }
  ]
}
```

### Skip-fetch mode

If `--skip-fetch` is active, skip this step entirely. Step 4 will compare only
against general software engineering principles.

## Step 4: Compare via CC-CC

This is the core analysis step. Use `/cc-cc-powerful-iterations` to produce high-quality,
cross-validated comparison between actual codebase patterns and fetched best practices.

### Prepare the comparison prompt

Build a structured prompt containing:
1. The stack inventory (`_stack.json`)
2. The architecture scan results (`_scan-*.json`)
3. The fetched best practices (`_best-practices-raw.json`)
4. Instructions to compare and classify each pattern

### Classification categories

For each detected pattern, classify as:

| Status | Meaning |
|---|---|
| `FOLLOWS` | Codebase follows the industry best practice |
| `DEVIATES` | Codebase uses a different approach — document both the standard and the deviation |
| `TEAM_CONVENTION` | Not a standard best practice, but a deliberate team choice worth documenting |
| `MISSING` | Best practice not implemented — potential improvement opportunity |
| `ANTI_PATTERN` | Codebase uses a known anti-pattern |

### Important: respect team conventions

If the codebase consistently uses a pattern that differs from the "standard" best practice,
do NOT flag it as wrong. Instead, document it as `DEVIATES` or `TEAM_CONVENTION` with:
- What the standard says
- What the team does instead
- Why the team's approach might be intentional (infer from context)

This is documentation, not a code review. The goal is to help future agents understand
how this specific codebase works, not to enforce external standards.

### CC-CC execution

1. Invoke `/cc-cc-powerful-iterations` with the comparison prompt
2. Claude analyzes the patterns and produces initial comparison
3. Codex cross-validates, catching missed patterns or misclassifications
4. Synthesis merges the best analysis from both engines
5. Codex reviews the final synthesis

### Quick mode

If `--quick`, use a single Claude subagent instead of cc-cc. Same prompt and
classification categories. Tag results with `"engine": "single"`.

### Output

Write to `$OUT_DIR/_comparison.json`:

```json
[
  {
    "area": "state-management",
    "pattern": "Zustand stores with flat state + actions",
    "status": "FOLLOWS",
    "best_practice": "Keep Zustand stores flat with co-located actions",
    "evidence": ["workflowStore.ts", "navStore.ts"],
    "notes": "Consistent with official Zustand recommendations",
    "importance": "high"
  },
  {
    "area": "styling",
    "pattern": "No component library — all custom Tailwind",
    "status": "TEAM_CONVENTION",
    "best_practice": "Use established component library (shadcn, Radix, etc.)",
    "evidence": ["All components are custom-built"],
    "notes": "Deliberate choice for full control. Agents must build UI with Tailwind utilities, not import component libraries.",
    "importance": "medium"
  }
]
```

## Step 5: Generate Pattern Documentation

Transform the comparison results into agent-consumable markdown files.

### File structure

```
$OUT_DIR/
├── _stack.json                    # Raw stack detection (intermediate)
├── _scan-frontend.json            # Raw architecture scan (intermediate)
├── _scan-backend.json             # Raw architecture scan (intermediate)
├── _best-practices-raw.json       # Raw fetched practices (intermediate)
├── _comparison.json               # Raw comparison results (intermediate)
├── README.md                      # Index + how to use these docs
├── frontend-patterns.md           # Frontend conventions + best practices
├── backend-patterns.md            # Backend conventions + best practices
├── data-model-patterns.md         # DB schema + query patterns
├── api-patterns.md                # API design conventions
├── type-patterns.md               # TypeScript type organization
└── anti-patterns.md               # Known anti-patterns to avoid
```

Files prefixed with `_` are intermediate artifacts. The `.md` files are the consumable output.

### Document format

Each pattern document follows this structure:

```markdown
# {Layer} Patterns

> Auto-generated by codebase-best-practices. Last run: {date}
> Stack: {relevant technologies}

## {Area}

### How this codebase does it

{Description of the actual pattern with file references}

### Best practice reference

{What industry best practices recommend}

### Status: {FOLLOWS | DEVIATES | TEAM_CONVENTION | MISSING | ANTI_PATTERN}

{Notes explaining the classification. For DEVIATES/TEAM_CONVENTION, explain
what the standard says AND why the team's approach is valid or intentional.}

---
```

### README.md

```markdown
# Codebase Patterns — {project name}

Generated: {date}
Stack: {one-line summary}

These docs describe how this codebase is structured and what conventions to follow
when writing new code. Read these before making changes.

## Quick reference

| Area | Convention | File |
|---|---|---|
| State management | Zustand flat stores | [frontend-patterns.md](frontend-patterns.md#state-management) |
| ... | ... | ... |

## Files

- [frontend-patterns.md](frontend-patterns.md) — React, styling, state, data fetching
- [backend-patterns.md](backend-patterns.md) — Hono routes, services, middleware
- [data-model-patterns.md](data-model-patterns.md) — Drizzle schema, migrations, queries
- [api-patterns.md](api-patterns.md) — REST conventions, pagination, validation
- [type-patterns.md](type-patterns.md) — TypeScript organization, shared types
- [anti-patterns.md](anti-patterns.md) — What NOT to do

## How agents should use this

1. Read the relevant pattern file before modifying that layer
2. Follow documented conventions — even if they deviate from "standard" best practices
3. If adding a new pattern, check if an existing convention covers it
4. TEAM_CONVENTION patterns are intentional — do not "fix" them to match external standards
```

### Anti-patterns file

Consolidate all `ANTI_PATTERN` and `MISSING` findings into `anti-patterns.md`.
These are actionable improvement opportunities, not just documentation.

## Step 6: Summary + Refinement

Present to the user:

1. **Stack summary** — detected technologies
2. **Pattern count** — how many patterns found per layer
3. **Classification breakdown** — how many FOLLOWS / DEVIATES / TEAM_CONVENTION / MISSING / ANTI_PATTERN
4. **Key findings** — top 5 most important patterns (by importance)
5. **Anti-patterns** — any ANTI_PATTERN findings that need attention
6. **Output location** — where docs were written

Ask if they want to:
- Refine any specific area
- Add manual conventions not detected in code
- Change any classifications
- Regenerate specific files

## Cross-Invocation Rules

- **Reads** `memory-bank/repo-context.md` for initial context (avoids redundant exploration)
- **Uses** `cc-cc-powerful-iterations` for Step 4 comparison (dual-engine validation)
- **Feeds** `review-changes` — pattern docs can inform the review checklist
- **Feeds** `memory-bank` — significant findings can be promoted to repo-context.md
- **Reads** `repo-standards-mining` output if it exists — deduplicates against PR-mined patterns

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/codebase-best-practices/`
- **Checkpoint frequency:** After Steps 1, 2, 3, 4 (before each major transition)
- **Subagent delegation:** Stack scan (Step 1-2), web fetch (Step 3), cc-cc (Step 4), doc generation (Step 5)

## Error Handling

- If web search fails or is unavailable, fall back to `--skip-fetch` mode automatically
- If cc-cc fails (Codex unavailable), fall back to `--quick` mode automatically
- If `memory-bank/repo-context.md` doesn't exist, do full exploration (slower but works)
- If a layer has no detectable patterns, skip it and note in summary
