---
name: simple-feature-workflow
description: |
  Guided feature development workflow with human-in-the-loop at every stage.
  Linear pipeline: prompt refinement, planning, expert deliberation, milestone-driven
  implementation, continuous code review, and PR creation. Designed for features where
  the developer wants full visibility and control over every decision.
  Use this skill when the user says "simple feature", "guided workflow", "step by step feature",
  "feature workflow", "walk me through building", "help me build", or wants a structured
  approach to implementing a feature with review gates and expert input at each stage.
version: 1.0.0
category: development
depends: [prompt-refinement, spec-first, spec-first-cc-cc, three-experts, review-changes, create-pr]
---

# simple-feature-workflow

Guided feature development workflow with human-in-the-loop at every stage.
Linear pipeline: prompt refinement, planning, expert deliberation, milestone-driven
implementation, continuous code review, and PR creation. Designed for features where
the developer wants full visibility and control over every decision.

Use this skill when the user says "simple feature", "guided workflow", "step by step feature",
"feature workflow", "walk me through building", "help me build", or wants a structured
approach to implementing a feature with review gates and expert input at each stage.

---

## OPERATING RULES

1. **Human-in-the-loop always.** Never advance to the next phase without explicit user confirmation.
2. **Show your work.** Display refined prompts, plans, expert suggestions (accepted AND discarded), and review results.
3. **One phase at a time.** Complete each phase fully before moving on.
4. **Fix before advancing.** Review issues must be resolved before proceeding to the next milestone.
5. **No silent decisions.** If you make a choice, explain it. If you discard something, show it.

---

## PHASE 1: PROMPT CAPTURE & REFINEMENT

### Step 1 — Capture the raw prompt

Ask the user: **"What feature do you want to build?"**

Collect their raw input. Store it as `raw_prompt`.

### Step 2 — Refine the prompt

Invoke `/prompt-refinement` on the raw prompt.

**MANDATORY OUTPUT — Show the user:**

```
┌─────────────────────────────────────────────────┐
│  PROMPT REFINEMENT RESULTS                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  RAW PROMPT:                                    │
│  {raw_prompt}                                   │
│                                                 │
│  REFINED PROMPT:                                │
│  {refined_prompt}                               │
│                                                 │
│  CHANGES MADE:                                  │
│  - {change_1}                                   │
│  - {change_2}                                   │
│  - ...                                          │
│                                                 │
│  CONFIDENCE: {score}/10                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

Ask: **"Does this refined prompt capture what you want? Edit or confirm."**

Wait for confirmation. If the user edits, re-refine and show again.

---

## PHASE 2: PLANNING MODE SELECTION

### Step 3 — Choose planning engine

Present the choice:

```
How would you like to plan this feature?

  [A] Spec-First — Full spec-first workflow: research, gap analysis,
      architecture decisions, plan.md + todo.md
  [B] Spec-First CC-CC (Dual Engine) — Same spec-first pipeline but
      every step runs through Claude + Codex in parallel for
      cross-validated architecture decisions and plans

Option B is recommended for complex features or when you want
two independent engines validating every planning decision.
```

Wait for the user to select A or B.

### Step 4 — Generate the plan

**If A (Spec-First):**
- Invoke `/spec-first` with the refined prompt.
- Produces plan.md and todo.md with architecture decisions, milestones, and verification criteria.

**If B (Spec-First CC-CC):**
- Invoke `/spec-first-cc-cc` with the refined prompt.
- Runs the full spec-first pipeline with dual-engine cross-validation at every step.
- Produces cross-validated plan.md and todo.md with engine agreement notes.

### Step 5 — Present and iterate on the plan

**MANDATORY OUTPUT — Show the full plan:**

```
┌─────────────────────────────────────────────────┐
│  FEATURE PLAN                                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  SUMMARY: {one_line_summary}                    │
│                                                 │
│  ARCHITECTURE DECISIONS:                        │
│  1. {decision_1} — {rationale}                  │
│  2. {decision_2} — {rationale}                  │
│                                                 │
│  MILESTONES:                                    │
│  M1: {milestone_1} — {verification}             │
│  M2: {milestone_2} — {verification}             │
│  M3: {milestone_3} — {verification}             │
│                                                 │
│  FILES TO MODIFY:                               │
│  - {file_1} — {what_changes}                    │
│  - {file_2} — {what_changes}                    │
│                                                 │
│  RISKS:                                         │
│  - {risk_1}                                     │
│                                                 │
└─────────────────────────────────────────────────┘
```

Ask: **"Review the plan. Want to change anything? Confirm when ready."**

Iterate until the user confirms. Each iteration shows the updated plan in full.

---

## PHASE 3: EXPERT DELIBERATION

### Step 6 — Three Experts review

Invoke `/three-experts` with the confirmed plan as input.

**For EACH deliberation round**, show the user:

```
┌─────────────────────────────────────────────────┐
│  THREE EXPERTS — Round {N}                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  ACCEPTED IMPROVEMENTS:                         │
│  + {improvement_1} — proposed by {expert}       │
│  + {improvement_2} — proposed by {expert}       │
│                                                 │
│  DISCARDED SUGGESTIONS:                         │
│  - {discarded_1} — reason: {why_discarded}      │
│  - {discarded_2} — reason: {why_discarded}      │
│                                                 │
│  CURRENT CONSENSUS: {summary}                   │
│                                                 │
└─────────────────────────────────────────────────┘

Review the results above.
- Confirm to proceed with accepted improvements
- Or rescue any discarded suggestion you want to keep
```

Wait for user approval each round. If the user wants to rescue a discarded suggestion,
add it to the accepted list and continue deliberation.

### Step 7 — Final expert recommendation

After all rounds complete, show the final consolidated recommendation:

```
┌─────────────────────────────────────────────────┐
│  EXPERT CONSENSUS — FINAL                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  RECOMMENDATION: {summary}                      │
│                                                 │
│  PLAN UPDATES:                                  │
│  ~ {update_1}                                   │
│  ~ {update_2}                                   │
│                                                 │
│  UPDATED MILESTONES:                            │
│  M1: {milestone_1_updated}                      │
│  M2: {milestone_2_updated}                      │
│  M3: {milestone_3_updated}                      │
│                                                 │
│  DISSENTING VIEWS (for your awareness):         │
│  * {dissent_1}                                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

Ask: **"Experts are done. Ready to start implementation?"**

---

## PHASE 4: IMPLEMENTATION

### Step 8 — Milestone-driven implementation

For each milestone in the plan:

1. **Announce the milestone:**
   ```
   ══════════════════════════════════════════
    MILESTONE {N}: {milestone_name}
   ══════════════════════════════════════════
   ```

2. **Implement** the milestone using spec-first principles:
   - Follow the plan exactly.
   - Write code that satisfies the milestone's verification criteria.
   - Run tests if applicable.

3. **Run `/review-changes`** scoped to the milestone's changes.

4. **Show review results:**
   ```
   ┌─────────────────────────────────────────────────┐
   │  MILESTONE {N} REVIEW                           │
   ├─────────────────────────────────────────────────┤
   │                                                 │
   │  FINDINGS:                                      │
   │  {severity} {finding_1}                         │
   │  {severity} {finding_2}                         │
   │                                                 │
   │  STATUS: {PASS / NEEDS_FIX}                     │
   │                                                 │
   └─────────────────────────────────────────────────┘
   ```

5. **If NEEDS_FIX:** Fix all CRITICAL and HIGH issues automatically. Show what was fixed.
   Re-run review to confirm. Repeat until clean.

6. **Confirm milestone completion** with the user before moving to the next one.

### Step 9 — Full feature review

After ALL milestones are complete:

1. Run `/review-changes` on the **entire feature** (all changes from start to now).

2. Fix any remaining issues found across the full diff.

3. **Show final results:**
   ```
   ┌─────────────────────────────────────────────────┐
   │  FULL FEATURE REVIEW                            │
   ├─────────────────────────────────────────────────┤
   │                                                 │
   │  TOTAL FINDINGS: {count}                        │
   │  CRITICAL: {n}  HIGH: {n}  MEDIUM: {n}  LOW: {n}│
   │                                                 │
   │  ALL CRITICAL/HIGH FIXED: {yes/no}              │
   │                                                 │
   │  FILES CHANGED: {count}                         │
   │  LINES ADDED: {n}  LINES REMOVED: {n}          │
   │                                                 │
   │  FEATURE STATUS: READY FOR PR                   │
   │                                                 │
   └─────────────────────────────────────────────────┘
   ```

---

## PHASE 5: SHIP

### Step 10 — PR creation

Ask the user:

```
Feature is ready! What would you like to do?

  [A] Create PR now — I'll run /create-pr
  [B] Review the diff first — I'll show the full diff
  [C] Done for now — I'll leave changes uncommitted
```

**If A:** Invoke `/create-pr`. Show the PR URL when done.
**If B:** Show the full diff, then ask again.
**If C:** Summarize what was accomplished and exit.

---

## PHASE SUMMARY

```
Phase 1: Prompt Capture & Refinement    → /prompt-refinement
Phase 2: Planning Mode Selection         → /spec-first or /spec-first-cc-cc
Phase 3: Expert Deliberation             → /three-experts (with per-round approval)
Phase 4: Implementation                  → Milestone-driven + /review-changes per milestone
Phase 5: Ship                            → /review-changes (full) + /create-pr
```

---

## CONTEXT MANAGEMENT

- If context is getting long, summarize completed phases into a scratchpad note.
- Always preserve: the refined prompt, the current plan, and the current milestone.
- After each phase, checkpoint critical state.

---

## ANTI-PATTERNS — DO NOT

- Skip showing the refined prompt to the user
- Auto-advance phases without user confirmation
- Hide discarded expert suggestions
- Skip per-milestone reviews
- Create a PR without asking
- Implement without a confirmed plan
