<p align="center">
  <img src="https://img.shields.io/badge/skills-24-blue?style=for-the-badge" alt="24 skills" />
  <img src="https://img.shields.io/badge/Claude_Code-plugin-blueviolet?style=for-the-badge" alt="Claude Code plugin" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License" />
  <img src="https://img.shields.io/github/stars/jAgusGelos/keel-skills?style=for-the-badge" alt="Stars" />
</p>

# keel-skills

**The most comprehensive Claude Code skill library for software engineering.** 24 production-grade skills that turn Claude into a senior engineering team — planning features before writing code, reviewing every diff against a 26-point checklist, resolving PR comments autonomously, and shipping with confidence.

Built by [Keel AI](https://github.com/jAgusGelos) from hundreds of hours of real-world usage across startups and engineering teams.

---

## Why this exists

Claude Code is powerful out of the box. But without structured workflows, you get inconsistent results — plans that miss edge cases, reviews that catch syntax but not architecture, and features that need rework after the first PR comment.

**keel-skills solves this by encoding battle-tested engineering workflows as reusable skills:**

- **Plan before you code** — `spec-first` produces architecture decisions and milestones before a single line is written
- **Multiple perspectives** — `three-experts` simulates 3 domain experts debating your design
- **Catch what linters miss** — `review-changes` runs 3 parallel agents checking for N+1 queries, race conditions, unbounded IN clauses, and 23 more patterns
- **Never lose context** — `feature-context` persists decisions and progress across sessions so you pick up right where you left off
- **Autonomous PR resolution** — `fix-pr-comments` fetches, classifies, fixes, and resolves reviewer comments without manual intervention

## Quick start

```bash
# Add the marketplace
claude plugin marketplace add jAgusGelos/keel-skills

# Install all 24 skills in one command
claude plugin install keel-skills
```

That's it. Every skill is now available in your Claude Code sessions.

```bash
# Or load locally for development/testing
claude --plugin-dir /path/to/keel-skills/
```

## What you get

### The complete development lifecycle

```
  Plan            Build           Review          Ship
   |                |               |               |
   v                v               v               v
spec-first ----> implement ----> review-changes --> create-pr
   |                |               |               |
   +-- three-experts|               +-- observability-audit
   +-- stress-test  +-- tdd                         +-- fix-pr-comments
                    +-- e2e-agent                    +-- pr-learning
```

Every stage is covered. Skills invoke each other automatically — `spec-first` calls `three-experts` for architecture decisions, `review-changes` escalates to `observability-audit` when it finds monitoring gaps, `fix-pr-comments` feeds `pr-learning` to improve future reviews.

---

### Skill categories

<details>
<summary><b>Reasoning (4 skills)</b> — Think before you act</summary>

| Skill | What it does |
|---|---|
| `prompt-refinement` | Scores and rewrites raw prompts into execution-ready instructions |
| `multiple-iterations-reasoning` | Progressive refinement with dual-engine (Claude + Codex) validation |
| `three-experts` | 3 domain experts debate your design and converge on consensus |
| `problem-solver` | 7-step structured problem-solving: understand, decompose, design, implement, test, review, deliver |

</details>

<details>
<summary><b>Development (12 skills)</b> — Build with confidence</summary>

| Skill | What it does |
|---|---|
| `spec-first` | Full planning workflow: research, gap analysis, architecture decisions, plan.md + todo.md |
| `spec-first-cc-cc` | Same pipeline but every step cross-validated by Claude + Codex |
| `cc-cc-powerful-iterations` | Dual-engine iteration combining Claude Code with OpenAI Codex CLI |
| `stress-test` | Adversarially validates your plan against real docs and POC code before you build |
| `tdd` | Strict red-green-refactor cycles — writes the test first, always |
| `review-changes` | 26-point code review: DRY, type safety, React patterns, async, N+1, races, and more |
| `observability-audit` | "Can you debug this at 2 AM?" — checks logging, tracing, alerts, correlation IDs |
| `e2e-agent` | Writes Cypress tests grounded in real user behavior using dual-engine pattern |
| `frontend-perf-agent` | 5 parallel agents: bundle, rendering, Core Web Vitals, assets, external validation |
| `backend-perf-agent` | 5 parallel agents: queries, schema, API/middleware, caching, external validation |
| `style-guide` | Define and enforce UI/UX design tokens, component patterns, and a11y standards |
| `simple-feature-workflow` | Guided feature dev with human-in-the-loop at every stage |

</details>

<details>
<summary><b>DevOps (3 skills)</b> — Ship and iterate</summary>

| Skill | What it does |
|---|---|
| `create-pr` | Auto-detects platform (GitHub/GitLab/Bitbucket), writes contextual PR summary |
| `fix-pr-comments` | Fetches, classifies, and autonomously resolves PR reviewer comments |
| `review-pr-comments` | Categorizes feedback: actionable, question, nitpick, praise, AI-generated |

</details>

<details>
<summary><b>Persistence (4 skills)</b> — Never lose context</summary>

| Skill | What it does |
|---|---|
| `memory-bank` | Structured project knowledge that survives across sessions |
| `feature-context` | Per-feature decisions, progress, and review feedback across days/weeks |
| `context-management` | Prevents context window exhaustion in long-running tasks |
| `pr-learning` | Captures PR review patterns and promotes recurring ones to repo improvements |

</details>

<details>
<summary><b>Meta (1 skill)</b> — The brain</summary>

| Skill | What it does |
|---|---|
| `keel-orchestration` | Cross-invocation routing table — ensures multi-skill flows chain correctly |

</details>

---

## Workflow chains

Skills don't work in isolation. They form chains that cover complete engineering workflows:

```
Plan validation     spec-first --> stress-test --> implement
Pre-commit          review-changes --fix --> create-pr
PR feedback         fix-pr-comments (autonomous resolver)
Learning loop       fix-pr-comments --> pr-learning --> review-changes updates
Observability       review-changes --> escalate --> observability-audit (deep)
Feature lifecycle   feature-context init --> spec-first --> build --> review --> ship --> complete
```

The `keel-orchestration` skill carries the full routing table — Claude loads it automatically when orchestrating multi-skill flows, so chains work without manual intervention.

---

## Examples

**Plan a feature before coding:**
```
> /spec-first Add a real-time notification system with WebSocket support
```
Claude runs research, gap analysis, invokes `three-experts` for architecture decisions, and produces `plan.md` + `todo.md` with milestones and verification criteria.

**Review everything you changed:**
```
> /review-changes
```
3 parallel agents audit your diff against 26 patterns. Add `--fix` to auto-resolve CRITICAL and HIGH findings.

**Resolve PR comments hands-free:**
```
> /fix-pr-comments
```
Fetches all unresolved comments, classifies them, implements fixes, resolves threads, and polls until clean.

**Stress-test your plan before building:**
```
> /stress-test
```
Adversarially challenges every claim in your plan — checks real docs, runs POC code, and flags what would break in production.

**TDD from the start:**
```
> /tdd Build a rate limiter with sliding window
```
Writes the failing test first, implements the minimum code to pass, refactors. Repeat until done.

---

## How it works

Each skill is a `SKILL.md` file with:
- **Trigger description** — tells Claude when to activate the skill
- **Structured workflow** — step-by-step instructions Claude follows
- **Cross-invocation rules** — which other skills to call and when
- **Dependency metadata** — `depends: [skill-a, skill-b]` for validation

```yaml
---
name: review-changes
description: |
  Production-grade code reviewer that audits all changes...
version: 1.0.0
category: development
depends: [observability-audit, feature-context]
---
```

All 24 skills ship as a single monolith plugin. This is intentional — Claude Code has no inter-plugin dependency resolution, and our workflow chains go up to 7 skills deep. Partial installs would silently degrade cross-invocation chains.

---

## Ecosystem & compatibility

### Optimized for React/Next.js/Node.js

Several skills include checklist items, file path conventions, and examples tuned for the **React / Next.js / Node.js** ecosystem. This is where the skills were battle-tested. They will still work in other stacks, but you may see framework-specific items that don't apply to your project.

Skills with React/Next.js/Node.js focus:
- `review-changes` — checklist includes React hooks, Server Components, and Next.js patterns
- `frontend-perf-agent` — rendering agent checks React-specific patterns (memo, useCallback, Context)
- `backend-perf-agent` — ORM checks focus on Prisma, TypeORM, Sequelize
- `e2e-agent` — generates Cypress tests with npm/Node.js conventions
- `style-guide` — audits CSS/Tailwind/React component patterns

All other skills (planning, reasoning, persistence, DevOps) are **fully stack-agnostic**.

### Optional dependencies

Some skills leverage external tools when available. They auto-detect availability and fall back gracefully:

| Dependency | Used by | Fallback |
|---|---|---|
| [OpenAI Codex CLI](https://github.com/openai/codex) | `cc-cc-powerful-iterations`, `review-changes`, `spec-first-cc-cc`, `multiple-iterations-reasoning`, `frontend-perf-agent`, `backend-perf-agent`, `e2e-agent` | Second Claude subagent |
| [`gh` CLI](https://cli.github.com/) | `create-pr`, `fix-pr-comments`, `review-pr-comments`, `pr-learning` | Required for GitHub repos |
| [`glab` CLI](https://gitlab.com/gitlab-org/cli) | `create-pr`, `fix-pr-comments`, `review-pr-comments` | Required for GitLab repos |

### .workspace/ directory

Several skills write scratchpad files to `.workspace/` in your project root (context checkpoints, iteration logs, etc.). Add it to your `.gitignore` to avoid committing these files:

```bash
echo '.workspace/' >> .gitignore
```

---

## Contributing

```bash
# Clone and test locally
git clone https://github.com/jAgusGelos/keel-skills.git
cd keel-skills
claude --plugin-dir ./

# Validate after changes
./scripts/validate-deps.sh
claude plugin validate ./
```

**Adding a skill:** Create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`, `version`, `category`, `depends`). If it invokes other skills, add them to `depends:` and update `keel-orchestration`. Run `validate-deps.sh` to verify.

See [CLAUDE.md](./CLAUDE.md) for developer instructions.

---

## License

MIT

---

<p align="center">
  <sub>Built with <a href="https://claude.com/claude-code">Claude Code</a> by <a href="https://github.com/jAgusGelos">Keel AI</a></sub>
</p>
