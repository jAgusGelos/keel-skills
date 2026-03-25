# Unified Category Taxonomy

Aligned with `/review-changes` (Agent 1/2) and `/pr-learning` taxonomies.
Use ONLY these categories when extracting and classifying patterns.

| Category | review-changes Agent | pr-learning Equivalent |
|---|---|---|
| `architecture` | Agent 1: Architecture & Design | boundary violation |
| `naming` | Agent 1: Architecture & Design | naming / discoverability |
| `type-safety` | Agent 1: Type Safety & Data | correctness bug |
| `error-handling` | Agent 1: Type Safety & Data | correctness bug |
| `framework-patterns` | Agent 1: Framework Patterns | accessibility / React quality |
| `structural-quality` | Agent 1: Structural Quality | duplication / single source of truth |
| `data-integrity` | Agent 1: Transaction & Data Integrity | performance / query shape |
| `security` | Agent 2: Security | correctness bug |
| `performance` | Agent 2: Performance | performance / query shape |
| `testing` | Agent 2: Patterns & Boundaries | missing validation / test gap |
| `documentation` | (none — propose new) | docs / invariants gap |
| `dependency-management` | (none — propose new) | (none) |

## Agent Assignment Rule

When proposing `/review-changes` additions:
- Categories mapping to **Agent 1** → add to Code Quality & Patterns checklist
- Categories mapping to **Agent 2** → add to Security & Performance checklist
- Categories with "(none)" → propose as new checklist items to the most relevant agent
