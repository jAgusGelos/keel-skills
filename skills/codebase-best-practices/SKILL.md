---
name: codebase-best-practices
description: |
  Investigate a codebase to detect its tech stack, component patterns, and architectural decisions.
  Fetch industry best practices for each detected technology via web search. Compare actual code
  patterns against best practices using cc-cc dual-engine validation. Generate two outputs:
  (1) .ai-patterns/ documentation for humans and agents wanting context, and
  (2) rules/ directory with short, imperative, enforceable rules that agents auto-load via CLAUDE.md.
  Documents both standard best practices being followed AND non-standard patterns the team has chosen.
  Use when: "codebase best practices", "audit best practices", "document patterns", "what patterns
  does this codebase follow", "generate coding guidelines", "best practices audit", "code patterns",
  "stack best practices", "how should I write code here", "document conventions", "codebase audit",
  "pattern documentation", "generate patterns", "coding standards from code", "investigate codebase",
  "what are the conventions", "document best practices", "codebase conventions", "engineering guidelines",
  "generate rules", "codebase rules", "domain rules".
---

# Codebase Best Practices

Investigate the codebase. Detect the stack. Fetch best practices. Compare. Generate pattern docs
AND enforceable rules. Uses cc-cc dual-engine for analysis quality.

Two outputs:
- `.ai-patterns/` — detailed documentation explaining WHY patterns exist (for context)
- `rules/` — short imperative directives telling agents WHAT to do (for enforcement)

## The Flow

```
[0] Detect environment + parse arguments
[1] Stack detection — scan package files, configs, imports
[2] Architecture scan — map components, layers, patterns
[3] Fetch best practices — web search per technology
[4] Compare via cc-cc — actual patterns vs best practices (dual-engine)
[5] Generate pattern documentation (.ai-patterns/)
[5b] Generate rule files (rules/)
[5c] Wire CLAUDE.md / AGENTS.md
[6] Present summary + offer refinement
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `--layer <layer>` | (all) | Limit scan to: `frontend`, `backend`, `infra`, or `all` |
| `--quick` | off | Skip cc-cc. Single Claude subagent analysis. Faster, less thorough. |
| `--output <dir>` | `.ai-patterns` | Output directory for pattern docs |
| `--skip-fetch` | off | Skip web search. Use only codebase analysis (offline mode). |
| `--rules-dir <dir>` | `rules` | Output directory for rule files |
| `--no-rules` | off | Skip rule generation (Steps 5b, 5c). Only generate .ai-patterns/ |
| `--no-wire` | off | Skip CLAUDE.md/AGENTS.md modification (Step 5c) |

## Step 0: Environment Detection

1. Check if inside a git repo. If not, warn and continue (patterns are still useful).
2. Parse arguments from user input.
3. Read `memory-bank/repo-context.md` if it exists — use as starting context to avoid
   redundant exploration. If it doesn't exist, proceed with full detection.
4. Set `$OUT_DIR` to the output directory (default `.ai-patterns/`).
5. Set `$RULES_DIR` to the rules directory (default `rules/`).

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

### What to extract

From search results, extract:
- **Official recommendations** from framework/library docs
- **Community consensus** patterns (widely adopted, multiple sources agree)
- **Common anti-patterns** to avoid
- **Version-specific** guidance (especially for major versions)

### Output

Write to `$OUT_DIR/_best-practices-raw.json`.

### Skip-fetch mode

If `--skip-fetch` is active, skip this step entirely. Step 4 will compare only
against general software engineering principles.

## Step 4: Compare via CC-CC

Use `/cc-cc-powerful-iterations` to produce high-quality, cross-validated comparison
between actual codebase patterns and fetched best practices.

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

Write to `$OUT_DIR/_comparison.json` with fields: area, pattern, status, best_practice,
evidence, notes, importance (high/medium/low).

## Step 5: Generate Pattern Documentation

Transform the comparison results into agent-consumable markdown files in `$OUT_DIR/`.

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

{Notes explaining the classification.}

---
```

### Anti-patterns file

Consolidate all `ANTI_PATTERN` and `MISSING` findings into `anti-patterns.md`.

## Step 5b: Generate Rule Files

Transform the comparison results into short, imperative, enforceable rules in `$RULES_DIR/`.

Skip this step if `--no-rules` is active.

### Key principle

`.ai-patterns/` explains WHY. `rules/` tells agents WHAT TO DO.

| Aspect | `.ai-patterns/` | `rules/` |
|---|---|---|
| Audience | Humans + agents wanting context | Agents executing tasks |
| Purpose | Explain patterns, document deviations | Enforce conventions |
| Format | Long-form docs with evidence | Short imperative bullets |
| Loading | Read on demand | Auto-loaded via CLAUDE.md |
| Tone | Descriptive | Imperative |

### Rules directory structure

```
$RULES_DIR/
├── _meta.json          # Generation metadata
├── README.md           # Human-readable index
├── frontend.md         # React, styling, state, data fetching rules
├── backend.md          # Routes, services, middleware, DB rules
├── api.md              # REST conventions, validation, error responses
├── types.md            # TypeScript organization, shared types
├── testing.md          # Testing conventions (only if detected)
└── infra.md            # CI/CD, Docker, deployment (only if detected)
```

One file per layer. Only generate files for layers with detected rules.

### Rule file format

Pure markdown. No YAML, no custom DSLs. Maximum compatibility across Claude Code,
Codex, Cursor, Copilot.

Each file follows this structure:

```markdown
# Frontend Rules

> Auto-generated by codebase-best-practices | {date}
> Stack: {relevant technologies}

## State Management

- MUST use Zustand with flat state + co-located actions. Do not nest state objects.
- MUST use selectors (`useStore(s => s.field)`) to prevent unnecessary re-renders.
- MUST NOT introduce Redux, MobX, Jotai, or any other state library.

## Styling

- MUST use Tailwind utility classes directly. No CSS modules, no styled-components.
- PREFER composing utilities over extracting @apply classes.

## Data Fetching

- MUST use @tanstack/react-query hooks for all server state.
- MUST NOT use useEffect + useState for API calls.

## Custom

<!-- Rules below this line are manually maintained. The skill will not overwrite them. -->
```

### Rule keywords (RFC 2119)

| Keyword | Severity | When to use |
|---|---|---|
| `MUST` | Mandatory | Violating this breaks conventions or causes bugs |
| `MUST NOT` | Prohibition | Known anti-pattern or explicitly rejected approach |
| `SHOULD` | Strong recommendation | Consistently followed but exceptions exist |
| `SHOULD NOT` | Discouraged | Suboptimal for this codebase |
| `PREFER X over Y` | Preference | Two valid approaches, team chose X |

### Classification-to-rule mapping

| Classification | Importance | Becomes rule? | Rule keyword |
|---|---|---|---|
| `FOLLOWS` | high | Yes | `MUST` or `SHOULD` |
| `FOLLOWS` | medium | Yes | `SHOULD` |
| `FOLLOWS` | low | No | Stays in .ai-patterns/ only |
| `DEVIATES` | high/medium | Yes | `PREFER X` + `MUST NOT Y` |
| `DEVIATES` | low | No | Stays in .ai-patterns/ only |
| `TEAM_CONVENTION` | any | Yes | `SHOULD` or `PREFER` |
| `MISSING` | high | Yes | `SHOULD` (aspirational) |
| `MISSING` | medium/low | No | Stays in .ai-patterns/ only |
| `ANTI_PATTERN` | any | Always | `MUST NOT` |

A single comparison item can produce 0, 1, or 2 rules. For example, a `DEVIATES` item
produces both "PREFER X" and "MUST NOT Y (the standard alternative)".

### When to include examples in rules

Only when the rule is ambiguous without one:

```markdown
- MUST define route handlers as separate const functions, not inline lambdas.
  ```ts
  // Correct
  const listWorkflows = async (c: Context) => { ... };
  app.get("/workflows", listWorkflows);

  // Wrong
  app.get("/workflows", async (c) => { ... });
  ```
```

If the rule is self-evident (e.g., "MUST use Zustand"), skip the example.

### Area-to-file mapping

```
state-management  -> frontend.md
styling           -> frontend.md
data-fetching     -> frontend.md
component-*       -> frontend.md
form-*            -> frontend.md
routing           -> frontend.md
route-*           -> backend.md
service-*         -> backend.md
database-*        -> backend.md
middleware-*       -> backend.md
module-*          -> backend.md
api-*             -> api.md
pagination        -> api.md
validation        -> api.md
serialization     -> api.md
type-*            -> types.md
import-*          -> types.md
error-handling    -> backend.md (server) or frontend.md (client)
auth-*            -> backend.md (server) or frontend.md (client)
i18n              -> frontend.md
```

### Custom section preservation

Each rule file ends with a `## Custom` section. On re-runs, the skill:

1. Reads existing rule files
2. Extracts everything below `## Custom` (including the header)
3. Generates new rules from fresh comparison data
4. Appends the preserved `## Custom` section

This lets teams add manual rules the skill can't detect.

### _meta.json schema

```json
{
  "generated_at": "ISO timestamp",
  "skill_version": "codebase-best-practices@1.1",
  "stack_summary": "React 19, Tailwind 4, Zustand 5, Hono, Drizzle, PostgreSQL",
  "rule_counts": {
    "frontend": 12,
    "backend": 8,
    "api": 6,
    "types": 4
  },
  "total_rules": 30,
  "from_classifications": {
    "FOLLOWS": 14,
    "DEVIATES": 5,
    "TEAM_CONVENTION": 6,
    "ANTI_PATTERN": 3,
    "MISSING": 2
  }
}
```

## Step 5c: Wire CLAUDE.md / AGENTS.md

Skip this step if `--no-wire` is active.

### Integration approach

Append (or replace) a `## Codebase Rules` section in the project's CLAUDE.md that
directs agents to read the relevant rules file before modifying code.

### CLAUDE.md section

```markdown
## Codebase Rules

Before modifying code, read the relevant rules file for the layer you are working on:

- `rules/frontend.md` — React, styling, state, data fetching
- `rules/backend.md` — Routes, services, middleware, database
- `rules/api.md` — REST conventions, validation, error responses
- `rules/types.md` — TypeScript organization, shared types

These rules are auto-generated by `codebase-best-practices` and reflect this project's
actual conventions. Follow them even if they differ from generic best practices.
For full context on WHY a rule exists, see `.ai-patterns/`.
```

### Idempotent insertion

1. Read CLAUDE.md. Search for `## Codebase Rules` header.
2. If found: replace from that header to the next `##` header (or EOF).
3. If not found: append the block at the end.
4. Only list rule files that actually exist (skip empty layers).

### AGENTS.md

If `AGENTS.md` exists, apply the same idempotent insertion. If it does not exist,
do NOT create it — only modify existing files.

## Step 6: Summary + Refinement

Present to the user:

1. **Stack summary** — detected technologies
2. **Pattern count** — how many patterns found per layer
3. **Classification breakdown** — FOLLOWS / DEVIATES / TEAM_CONVENTION / MISSING / ANTI_PATTERN
4. **Rule count** — how many rules generated per layer file
5. **Key findings** — top 5 most important patterns
6. **Anti-patterns** — any ANTI_PATTERN findings that need attention
7. **Output locations** — where docs and rules were written
8. **CLAUDE.md changes** — what was modified

If rules were regenerated (re-run), also show:
- Rules added / removed / reworded since last run

Ask if they want to:
- Refine any specific area
- Add manual conventions not detected in code
- Change any classifications
- Regenerate specific files

## Cross-Invocation Rules

- **Reads** `memory-bank/repo-context.md` for initial context (avoids redundant exploration)
- **Uses** `cc-cc-powerful-iterations` for Step 4 comparison (dual-engine validation)
- **Feeds** `review-changes` — pattern docs and rules can inform the review checklist
- **Feeds** `memory-bank` — significant findings can be promoted to repo-context.md
- **Reads** `repo-standards-mining` output if it exists — deduplicates against PR-mined patterns

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/codebase-best-practices/`
- **Checkpoint frequency:** After Steps 1, 2, 3, 4 (before each major transition)
- **Subagent delegation:** Stack scan (Step 1-2), web fetch (Step 3), cc-cc (Step 4), doc generation (Step 5), rule generation (Step 5b)

## Error Handling

- If web search fails or is unavailable, fall back to `--skip-fetch` mode automatically
- If cc-cc fails (Codex unavailable), fall back to `--quick` mode automatically
- If `memory-bank/repo-context.md` doesn't exist, do full exploration (slower but works)
- If a layer has no detectable patterns, skip it and note in summary
- If CLAUDE.md doesn't exist, create it with just the Codebase Rules section
