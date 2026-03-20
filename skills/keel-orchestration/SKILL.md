---
name: keel-orchestration
description: |
  Model-invoked routing table for multi-skill orchestration. NOT user-invokable.
  This skill is automatically loaded by Claude when orchestrating multi-skill flows.
  It carries all cross-invocation rules and workflow chain definitions to ensure
  skills invoke each other correctly rather than reimplementing overlapping logic.
  Claude should consult this skill whenever executing a workflow that spans multiple
  keel-skills, to determine which skill to invoke next and how data flows between them.
version: 1.0.0
category: meta
depends: []
---

# Keel Orchestration — Cross-Invocation Routing Table

This skill defines how keel-skills invoke, feed, and read each other. When executing
any multi-skill workflow, Claude MUST follow these rules to maintain correct orchestration.

## Cross-Invocation Rules

Skills should invoke other skills (not reimplement their logic) when functionality overlaps:

1. `cc-cc-powerful-iterations` invokes `prompt-refinement` for Step 1 (prompt refinement)
2. `spec-first` invokes `three-experts` for Step 5 (architecture deliberation)
3. `spec-first` suggests `/stress-test` after plan generation (Step 8)
4. `fix-pr-comments` feeds `pr-learning` (after resolving PR comments, capture patterns)
5. `pr-learning` Phase 2 updates `review-changes` (promote recurring patterns to checklist)
6. `feature-context` is read by `context-management` on session resume (bridges feature -> session scope)
7. `spec-first` creates or resumes `feature-context` when planning a named feature
8. `three-experts` writes deliberation summaries to `feature-context`
9. `review-changes` writes review findings to `feature-context`
10. `fix-pr-comments` writes resolution log to `feature-context`
11. `stress-test` writes validation findings to `feature-context`
12. `create-pr` writes PR linkage to `feature-context`
13. On merge, orchestrator marks `feature-context` completed and suggests archive
14. Durable lessons from `feature-context` are promoted to `memory-bank` explicitly, not automatically
15. `review-changes` escalates to `observability-audit` when observability checks find hard blockers or 2+ medium issues
16. `observability-audit` reads `memory-bank` for stack detection (optional, works without it)
17. `observability-audit` uses `three-experts` for architectural observability tradeoffs (sampling, vendor choice, cardinality)
18. `observability-audit` feeds `review-changes` with recurring observability patterns for checklist promotion

## Workflow Chains

```
Plan validation:     spec-first -> (optional) /stress-test -> implement
Pre-commit:          /review-changes --fix -> /create-pr
PR feedback:         /fix-pr-comments (autonomous resolver)
Learning loop:       /fix-pr-comments -> /pr-learning -> review-changes updates
Observability:       /review-changes (lightweight) -> escalate -> /observability-audit (deep)
Feature lifecycle:   /feature init -> spec-first -> implement -> review-changes -> create-pr -> /feature complete
Feature resume:      session start -> feature-context RESUME -> context-management bridge -> continues
```

## Routing Logic

When Claude is in a multi-skill flow, it should:

1. **Check this routing table** before invoking any skill
2. **Follow the chain** — if skill A produces output that skill B needs, invoke B next
3. **Never reimplement** — if a rule says "skill A invokes skill B for X", use `/skill-b` instead of reimplementing X
4. **Respect data flow** — `feeds` means the output of one skill becomes input for another; `reads` means one skill reads another's persisted artifacts
5. **Feature context integration** — any skill that produces findings or decisions should write them to `feature-context` if a feature context is active

## Skill Categories

| Category | Skills |
|---|---|
| **Reasoning** | prompt-refinement, multiple-iterations-reasoning, three-experts, problem-solver |
| **Persistence** | memory-bank, feature-context, context-management, pr-learning |
| **Development** | cc-cc-powerful-iterations, spec-first, spec-first-cc-cc, stress-test, tdd, review-changes, style-guide, e2e-agent, frontend-perf-agent, backend-perf-agent, observability-audit, simple-feature-workflow |
| **DevOps** | create-pr, review-pr-comments, fix-pr-comments |
| **Meta** | keel-orchestration |
