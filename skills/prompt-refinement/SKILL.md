---
name: prompt-refinement
description: |
  Qualify, score, and rewrite raw prompts into high-quality, execution-ready prompts for AI
  coding assistants (Claude Code, Codex, Copilot, and similar). Use this skill whenever the
  user wants to refine a prompt, assess prompt quality, improve execution confidence, add
  missing engineering context, decompose a large request into focused prompt chains, or
  optimize a prompt before sending it to an AI agent. Also trigger when the user mentions
  "improve this prompt", "prompt quality", "refine my request", "prompt engineering", or
  wants to ensure their prompt will succeed before execution.
version: 1.0.0
category: reasoning
depends: []
---

# Prompt Refinement

Transform a raw user prompt into a high-quality, execution-ready prompt optimized for AI coding assistants.

## Core Rule: Resolve Before Assuming

Never fabricate file paths, versions, APIs, architecture details, or any factual claim. But also: never leave something as `[unknown]` without first trying to resolve it from the repository. This skill runs inside projects that have real code, docs, and often an `AGENTS.md`, `CLAUDE.md`, `README.md`, `package.json`, `pyproject.toml`, or similar project documentation.

**Resolution order (mandatory):**
1. Search the codebase — use Glob, Grep, and Read to find the actual files, services, tech stack, and patterns
2. Check project docs — read `AGENTS.md`, `CLAUDE.md`, `README.md`, memory banks, or any doc referenced in the project root
3. Check config files — `package.json`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `.env.example`, `docker-compose.yml`, etc.
4. Only after exhausting 1-3, use `[unknown]` for genuinely unresolvable information

The goal is to produce a prompt with real, verified context — not placeholders.

## Operating Modes

Before starting, determine which mode applies:

**Mode A — Questions First** (when repo exploration still leaves critical gaps):
After completing Step 1 (repo exploration), if any single critical blocker remains unresolved (missing definition of done, unknown execution target, or unbounded scope), ask up to 3 targeted clarifying questions and stop. Most of the time, repo exploration resolves enough that this mode is unnecessary.

**Mode B — Proceed with Resolved Context** (default — most prompts land here after repo exploration):
Analyze and rewrite using the real context gathered from the repository. Tag the few remaining unknowns only if they genuinely couldn't be resolved from code, docs, or config files.

## Process

### Step 1: Explore the Repository (Mandatory)

Before analyzing the prompt, gather real context from the project. This step is non-negotiable — it is what separates a useful refined prompt from one full of placeholders.

**What to do:**

1. **Read project docs** — Look for `AGENTS.md`, `CLAUDE.md`, `README.md`, or any memory bank / knowledge base files in the project root or `.claude/` directory. These contain architectural decisions, patterns, tech stack, and conventions.

2. **Read config files** — Check `package.json`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `docker-compose.yml`, `.env.example`, or equivalent. Extract: language, framework, dependencies, scripts, database, and runtime info.

3. **Search for relevant code** — Based on what the user's prompt mentions (even vaguely), use Glob and Grep to locate the actual files, services, components, or modules involved. For example:
   - User says "payment service" → `Grep` for "payment", `Glob` for `**/payment*`
   - User says "authentication" → `Grep` for "auth", check routes, middleware, services
   - User says "the API" → check routes directory, controller files, API handlers

4. **Build a context summary** — Compile what you found into a structured context block:
   - Tech stack (with versions from config files)
   - Relevant file paths (real, verified)
   - Existing patterns and conventions (from AGENTS.md or code)
   - Related services or dependencies
   - Current state of what the user wants to change

**Effort cap:** Limit repo exploration to ~10 targeted searches (Glob/Grep/Read calls). If you haven't found what you need after 10 searches, move on with what you have and flag the gaps. Don't spelunk endlessly.

This context summary feeds directly into the analysis and rewrite steps. The more you resolve here, the higher the confidence score and the more useful the refined prompt.

### Step 2: Analyze the Prompt (with repo context)

Evaluate across five dimensions. Score each 0 (Weak), 1 (Adequate), or 2 (Strong).

| Dimension            | 0 (Weak) | 1 (Adequate) | 2 (Strong) |
|----------------------|----------|---------------|------------|
| Clarity              | Multiple interpretations possible, core intent unclear | Intent identifiable but some ambiguity remains | Single clear interpretation, no guessing needed |
| Specificity          | No files, services, or components named | Some targets named or discoverable from context | Exact files, functions, and components identified |
| Context Completeness | Missing tech stack, structure, and constraints | Partial context — some gaps fillable from repo | Full context: stack, files, patterns, current state |
| Actionability        | No definition of done, unclear what "finished" means | General goal clear but success criteria vague | Discrete task with explicit, testable definition of done |
| Scope Control        | Unbounded — could touch many systems | Bounded but may need decomposition | Single logical unit of work, one-pass executable |

### Step 3: Score Confidence

**Base score:** Sum of all 5 dimension scores (max 10).

**Blocker penalties** (subtract 2 each if present):
- Missing definition of done
- Unknown execution target (no files, services, or components identified after repo exploration)
- Unsafe/unbounded scope (could touch many systems with no boundary)

**Floor:** Final score cannot go below 0. If penalties push it negative, use 0.

**Final score → Confidence level:**

| Score   | Confidence |
|---------|------------|
| 9-10    | Very High — Could be handed to a junior dev as a task ticket with zero follow-up. |
| 7-8     | High — Minor ambiguities the AI can resolve with reasonable assumptions. |
| 4-6     | Medium — The AI will need to make meaningful assumptions or ask questions. |
| 0-3     | Low — High risk of off-target results or hallucinated context. |

**Short-circuit:** If the prompt scores 9-10 after repo exploration, skip the full rewrite. Instead, present the analysis and suggest only minor tweaks. Don't over-engineer prompts that are already strong.

Write 2-3 sentences justifying the score. Reference specific gaps or strengths.

### Step 4: Rewrite the Prompt

Apply these principles (all are guidance, not rigid rules — adapt to the task):

**Structure:**
- Begin with a clear action verb and expected output
- Use numbered steps for multi-step tasks
- Consider XML tags for organization on longer prompts
- End with explicit, testable success criteria

**Clarity:**
- Be direct — state what to do, not what to avoid
- Replace vague references ("the code", "it") with exact identifiers when known
- Reframe negations as affirmative instructions

**Context (from Step 1 exploration):**
- Use the real tech stack and versions found in config files
- Reference actual file paths discovered via Glob/Grep
- Embed relevant code snippets found during exploration
- Include conventions and patterns from AGENTS.md/CLAUDE.md
- Explain the "why" — business or architectural rationale improves decisions
- Only use `[unknown]` for info that genuinely could not be found in the repo

**Scope:**
- If too broad, decompose into a prompt chain (see Step 5)
- Each prompt should map to one logical unit of work

**Reasoning:**
- For complex tasks, consider assigning a role
- For multi-step reasoning: "First analyze..., then implement..."
- For straightforward tasks, keep it simple — zero-shot with clear instructions

**Output steering:**
- Specify desired format when it matters (code only, diff, file-by-file)

#### Refined Prompt Template

Adapt this structure to the task (use XML tags only when they add clarity):

```
<role>Act as a [specific engineering role] working in [project/repo].</role>

<objective>[Action verb + exact task + expected deliverable]</objective>

<context>
- Why: [business or technical rationale]
- Current behavior: [describe or mark unknown]
- Desired behavior: [describe]
- Relevant files: [paths or [unknown]]
- Tech stack: [specifics or [assumption: ...]]
</context>

<constraints>
- [Positive constraint: use X]
- [Performance/security requirements]
- [Scope boundary]
</constraints>

<tasks>
1. [First concrete step]
2. [Second concrete step]
3. [Implementation]
4. [Validation + tests]
</tasks>

<success_criteria>
- [Observable outcome 1]
- [Observable outcome 2]
- [Tests that must pass]
</success_criteria>
```

### Step 5: Decompose if Needed (Prompt Chaining)

When scope is too large for one pass, produce a chain:

- Prompt 1: Discovery + plan
- Prompt 2: Implement part A
- Prompt 3: Implement part B
- Prompt 4: Validation, tests, cleanup

Each sub-prompt must be independently executable with clear inputs/outputs.

## Output Format

**Required sections** (always include):

```
## Repository Context Resolved

{Summary of what was found: tech stack, relevant files, patterns, conventions}

## Prompt Analysis

| Dimension            | Score | Justification |
|----------------------|-------|---------------|
| Clarity              | {0-2} | {one sentence} |
| Specificity          | {0-2} | {one sentence} |
| Context Completeness | {0-2} | {one sentence} |
| Actionability        | {0-2} | {one sentence} |
| Scope Control        | {0-2} | {one sentence} |

**Blockers:** {list any, or "None"}
**Total Score:** {N}/10 → **Confidence: {level}**

{2-3 sentence justification}

## Refined Prompt

{The rewritten prompt, ready to copy and use}

## Changes Made

{Bulleted list of what was changed and why}
```

**Optional sections** (include when applicable):

```
## Clarifying Questions (Mode A only)

{Up to 3 targeted questions}

## Assumptions Used (Mode B only)

{Bulleted list of assumptions made, each tagged [assumption]}

## Prompt Chain (only if decomposed)

{Numbered sub-prompts for phased execution}
```

## Examples

### Example 1: Vague Prompt — Repo Exploration Resolves Most Gaps

**Raw:** "Add authentication to my app"

**Step 1 exploration found:**
- `package.json` → Next.js 14, React 18, Prisma ORM, PostgreSQL
- `README.md` → "E-commerce app with product catalog and cart"
- `Glob "**/auth*"` → no existing auth files
- `src/app/` → App Router structure, routes: `/`, `/products`, `/cart`, `/dashboard`
- `AGENTS.md` → "Use NextAuth.js for auth when implemented. Credentials provider first."
- `prisma/schema.prisma` → User model not yet defined

**Analysis (post-exploration):**

| Dimension            | Score | Justification |
|----------------------|-------|---------------|
| Clarity              | 1     | "Authentication" is still broad but AGENTS.md narrows it to NextAuth + Credentials. |
| Specificity          | 1     | Repo exploration found the stack and file structure, but user didn't specify which routes to protect. |
| Context Completeness | 2     | Tech stack, framework, database, and auth strategy all resolved from repo. |
| Actionability        | 0     | No definition of done — which routes need protection? What happens for unauthenticated users? |
| Scope Control        | 0     | Still a multi-step feature, needs decomposition. |

**Blockers:** Missing definition of done (-2), unbounded scope (-2)
**Total Score:** 0/10 → **Confidence: Low**

Repo exploration resolved tech stack and auth strategy, but two critical questions remain. Switching to Mode A.

**Clarifying Questions:**
1. Which routes need protection? (e.g., `/dashboard` and `/cart` require login, `/products` stays public)
2. What should happen for unauthenticated users? (redirect to login, show modal, return 401)
3. Should we decompose this into phases? (Phase 1: signup/login + protect routes, Phase 2: OAuth, Phase 3: roles/permissions)

### Example 2: Decent Prompt — Mode B (Proceed with Resolved Context)

**Raw:** "Fix the bug in the payment service where duplicate charges happen when users double-click submit"

**Step 1 exploration found:**
- `Grep "payment"` → `src/services/payment/checkout.ts`, `src/routes/api/checkout.ts`
- `Grep "submit"` in components → `src/components/CheckoutForm.tsx`
- `package.json` → Next.js 14, Stripe SDK 14.x, Prisma ORM
- `AGENTS.md` → "All API routes use Stripe for payments, no idempotency keys implemented yet"
- No debounce logic found in CheckoutForm.tsx

**Analysis (post-exploration):**

| Dimension            | Score | Justification |
|----------------------|-------|---------------|
| Clarity              | 2     | Bug and trigger clearly described. |
| Specificity          | 2     | Repo exploration resolved exact file paths and stack. |
| Context Completeness | 2     | Tech stack, files, and current idempotency state all confirmed from code/docs. |
| Actionability        | 2     | Clear bug with a clear fix target and known files. |
| Scope Control        | 2     | Single bug, single fix. |

**Blockers:** None
**Total Score:** 10/10 → **Confidence: Very High**

All context was resolved from the repository. File paths confirmed via Grep, tech stack from package.json, idempotency gap confirmed from AGENTS.md. No assumptions needed.

**Refined Prompt:**

```
Fix the duplicate charge bug in the payment checkout flow triggered by double-clicking submit.

<context>
- Payment service: src/services/payment/checkout.ts
- API route: src/routes/api/checkout.ts
- Frontend form: src/components/CheckoutForm.tsx
- Stack: Next.js 14, Stripe SDK 14.x, Prisma ORM
- Current state: no idempotency key, no client-side debounce (confirmed from AGENTS.md and code)
</context>

<tasks>
1. In CheckoutForm.tsx: disable submit button on click, show loading state, re-enable only on error
2. In checkout.ts: generate idempotency key (user ID + cart hash) and pass to Stripe PaymentIntent creation
3. In the API route: add 30-second in-flight payment guard per user before creating new PaymentIntent
</tasks>

<constraints>
- Use Stripe's built-in idempotency_key parameter
- Idempotency key must be deterministic (same cart = same key)
- Do not change the Stripe API version or payment flow structure
</constraints>

<success_criteria>
- Double-clicking submit creates exactly one PaymentIntent in Stripe
</success_criteria>
```

**Changes Made:**
- Resolved all file paths from codebase (no assumptions needed)
- Confirmed tech stack from package.json
- Confirmed idempotency gap from AGENTS.md
- Added three-layer fix with specific file targets per task
- Used Stripe's native idempotency_key parameter
- Defined single testable success criterion

## Quality Checklist

Before finalizing, verify:
- [ ] Repository was explored (Step 1 completed — this is mandatory)
- [ ] File paths in the prompt are real (verified via Glob/Grep, not guessed)
- [ ] Tech stack and versions come from config files, not assumptions
- [ ] Refined prompt is directly executable (no guessing required)
- [ ] Success criteria are testable and explicit
- [ ] Scope is realistic for one pass (or split into chain)
- [ ] Remaining `[unknown]` tags are genuinely unresolvable from the repo
- [ ] Language is direct, concrete, and unambiguous
- [ ] The "why" is included for architectural context
