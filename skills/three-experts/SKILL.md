---
name: three-experts
description: |
  Multi-expert deliberation framework for complex engineering decisions. Simulates 3
  domain-specific experts reasoning step-by-step through a problem, challenging each
  other's assumptions, and converging on a consensus solution grounded in real project
  code and architecture. Use this skill when the user faces architecture decisions,
  refactoring strategies, debugging multi-layer issues, API/data model design, edge-case
  test generation, or any complex engineering problem that benefits from multiple
  perspectives. Trigger when the user says "three experts", "expert deliberation",
  "multi-perspective", "debate this", "architecture review", "think through this from
  multiple angles", "expert panel", "deliberate on", or asks for a decision with
  tradeoffs analyzed from different viewpoints.
version: 1.0.0
category: reasoning
depends: [feature-context]
---

# Three Experts

A multi-expert deliberation framework that simulates 3 domain-specific experts reasoning
step-by-step through a complex engineering problem. Each expert writes one step of
reasoning, shares it with the group, and all advance together. If an expert realizes
their reasoning is wrong, they acknowledge it and drop out. The process continues until
the remaining experts converge on a consensus.

## Why This Exists

Complex engineering decisions have tradeoffs that look different depending on your role.
A system architect optimizes for extensibility, a security specialist for attack surface,
a DBA for query performance. By simulating these perspectives reasoning together — visible
step by step, challenging each other — you get a decision that accounts for concerns a
single viewpoint would miss. Grounding this in real project code prevents it from becoming
a generic thought exercise.

## Process Overview

```
User's Problem
      |
      v
[1] Repository Exploration (gather real context)
      |
      v
[2] Expert Selection (pick 3 based on problem type)
      |
      v
[3] Deliberation Rounds (step-by-step visible reasoning)
      |    - Self-deliberation + position per expert
      |    - Challenges with sub-point resolution
      |    - Rotating devil's advocate
      |    - Wrong experts drop out
      |
      v
[3.5] Voting Round (each expert commits to a position)
      |
      v
[4] Consensus & Recommendation (converged solution with tradeoffs)
```

## Step 1: Repository Exploration (Mandatory)

Before any expert speaks, explore the repository to ground deliberation in reality.
This is what makes the skill useful — experts reason about real files, real architecture,
and real constraints.

**What to do:**

1. **Read project docs** — Check for `AGENTS.md`, `CLAUDE.md`, `README.md`, or knowledge
   base files in the project root or `.claude/` directory. Extract architectural decisions,
   conventions, and constraints.

2. **Read config files** — Check `package.json`, `tsconfig.json`, `pyproject.toml`,
   `Cargo.toml`, `go.mod`, `docker-compose.yml`, `.env.example`, or equivalent. Extract
   language, framework, dependencies, scripts, database, and runtime info.

3. **Search for relevant code** — Based on what the problem mentions, use Glob and Grep
   to locate actual files, services, components, or modules involved. Read key files to
   understand current implementation.

4. **Build a context brief** — Compile findings into a structured summary that all experts
   will reference:
   - Tech stack with versions
   - Relevant file paths (real, verified)
   - Existing patterns and conventions
   - Current state of what is being discussed
   - Known constraints (performance, security, compatibility)

**Effort cap:** Limit to ~12 targeted searches. Don't spelunk endlessly — gather enough
to ground the experts, then move on.

Present the context brief before deliberation begins under a `## Repository Context` header.

## Step 2: Expert Selection

Select 3 experts based on the problem type. Use the presets below as defaults, but adapt
if the specific problem calls for different expertise.

### Expert Presets

| Problem Type | Expert 1 | Expert 2 | Expert 3 |
|---|---|---|---|
| Architecture Decisions | System Architect | Performance Engineer | Security Specialist |
| Refactoring Strategy | Senior Developer | QA Lead | Tech Lead |
| Debugging Multi-Layer Issues | Backend Engineer | DevOps Engineer | DBA |
| API / Data Model Design | API Designer | DBA | Frontend Consumer |
| Edge-Case Test Generation | QA Engineer | Security Tester | Systems Thinker |

### Expert Adaptation Rules

- If the problem spans two categories, blend: pick the most relevant expert from each.
- If the project has a dominant concern (e.g., real-time performance, regulatory compliance),
  replace the least relevant expert with a domain specialist.
- Always aim for tension between perspectives — three experts who agree on everything
  provide no value. Pick experts whose priorities naturally conflict.

### Expert Introduction Format

Present each expert before deliberation starts:

```
### Expert Panel

**[Expert 1 Title]** — [One sentence on what they optimize for and their perspective bias]
**[Expert 2 Title]** — [One sentence on what they optimize for and their perspective bias]
**[Expert 3 Title]** — [One sentence on what they optimize for and their perspective bias]
```

## Execution Model: 3 Separate Agents (Mandatory)

Each expert MUST run as its own independent Agent subagent. This is critical for genuine
perspective diversity — a single context simulating 3 voices collapses into one perspective
with 3 labels. Separate agents produce truly independent reasoning.

### How It Works

1. **Launch 3 Agent subagents in parallel** — one per expert. Each agent receives:
   - The Repository Context from Step 1
   - Their assigned expert role, perspective bias, and what they optimize for
   - The problem statement
   - The current round's question or the previous round's positions (for rounds 2+)
   - Their devil's advocate duty (if it's their turn in the rotation)

2. **Agent prompt template per round:**

   ```
   You are {Expert Title} — {perspective description}.
   You optimize for: {optimization focus}.
   Your bias: {perspective bias}.

   CONTEXT:
   {repository_context_from_step_1}

   PROBLEM:
   {user_problem}

   PREVIOUS ROUND POSITIONS (if round 2+):
   {other_experts_positions}

   CHALLENGES TO ADDRESS (if any):
   {challenges_from_previous_round}

   YOUR TASK FOR ROUND {N}:
   1. Self-critique: Write one sentence — the strongest objection to your current view.
   2. Updated position: 2-4 sentences considering that objection. Must reference real files.
   3. Challenge: Identify one specific flaw in another expert's reasoning (with evidence).
   4. Devil's advocate (if your turn): One adversarial point against the emerging consensus.

   RULES:
   - Reference specific file paths, dependencies, or code patterns
   - State concrete, falsifiable claims — not vague observations
   - Build on previous discussion, don't repeat
   - If you realize your reasoning was wrong, say so explicitly and withdraw
   ```

3. **Collect all 3 agent responses** before proceeding to synthesis for the round.

4. **The orchestrator (main context)** synthesizes the round:
   - Presents each expert's position
   - Resolves sub-point factual disagreements by checking the codebase
   - Tracks dropouts and convergence
   - Feeds the synthesized round back into the next round's agent prompts

5. **For the voting round (Step 3.5)**, launch the same 3 agents with a voting prompt
   that asks each to commit to a final position with rationale and acknowledged weakness.

### Why Separate Agents Matter

- **Independence:** Each agent reasons from scratch within its role, without being influenced
  by the other experts' reasoning happening in the same token stream
- **True diversity:** An architect agent and a security agent genuinely think differently
  when they're separate processes vs. simulated voices in one context
- **No dominance collapse:** A single context tends to let one "expert" dominate; separate
  agents can't see each other's work until the orchestrator shares it
- **Parallel execution:** All 3 agents run simultaneously, making rounds faster

## Step 3: Deliberation Rounds

This is the core mechanic. Run visible rounds where each expert reasons one step at a time.
Each expert runs as its own Agent subagent (see Execution Model above).

### Round Structure

Each round has three phases:

**Phase A — Self-Deliberation + Position**
Each expert first writes a one-sentence self-critique (the strongest objection to their own
current view), then states their updated position (2-4 sentences) considering that objection.
This prevents weak arguments from surviving unchallenged. The position must:
- Reference real files, dependencies, or patterns found in Step 1
- Build on the previous round's discussion (not repeat it)
- State a concrete, falsifiable claim — not a vague observation

**Phase B — Challenge + Sub-point Resolution**
After all three experts share their step, each expert may challenge another's reasoning.
Challenges must be specific: "Expert 2 assumes X, but file Y shows Z" — not generic
disagreement.

**Sub-point Resolution (Tree-of-Debate):** If a challenge hinges on a verifiable factual
question (e.g., "does dependency X support feature Y?", "does file Z use pattern W?"),
resolve it immediately by checking the codebase before the next round. Present as:

> **Resolved:** [Question] → [Answer with evidence]. [Expert who was correct] proceeds;
> [Expert who was wrong] updates their reasoning next round.

Do not carry unresolved factual disagreements across rounds — they compound into unfounded
reasoning. Cap at 2 sub-point resolutions per full deliberation to avoid context bloat.

**Rotating Devil's Advocate:** In each round, one expert (rotating: 1→2→3→1...) must include
at least one adversarial point against the emerging consensus, even if they personally agree.
This prevents premature convergence without sacrificing a domain perspective slot.

**Phase C — Reassessment**
Any expert who realizes their reasoning was wrong must acknowledge it explicitly and
drop out. A dropout looks like:

```
**[Expert Title]:** I withdraw from this deliberation. [Expert N]'s point about [specific
issue] invalidates my assumption that [what was wrong]. My remaining perspective aligns
with [which expert they now support].
```

### Round Format

```
---
### Round N

**[Expert 1]** (Step N): [Their reasoning step, referencing real code/files]

**[Expert 2]** (Step N): [Their reasoning step, referencing real code/files]

**[Expert 3]** (Step N): [Their reasoning step, referencing real code/files]

**Challenges:**
- [Expert X] challenges [Expert Y]: [Specific challenge with evidence]

**Dropouts:** [None / Expert who dropped and why]
---
```

### Deliberation Rules

1. **Minimum rounds:** 3 (even if agreement seems early — force deeper analysis)
2. **Maximum rounds:** 6 (if no consensus by round 6, go to majority recommendation)
3. **No repeated arguments:** Each round must introduce new reasoning. If an expert restates a prior point, they must extend it with new evidence or retract it.
4. **Falsifiable claims:** Prefer concrete, testable statements ("this will cause N+1 queries in file X") over abstract principles ("separation of concerns is important").
5. **Dropout threshold:** An expert drops out only when a specific factual error or
   logical contradiction in their reasoning is demonstrated — not merely because others
   disagree. When dropping, preserve useful partial insights as "salvaged points."
6. **Convergence detection:** Consensus is reached when all remaining experts (minimum 2)
   explicitly agree on a recommendation and can state it in the same terms
7. **Tie-breaking:** If 2 experts remain and cannot converge by round 6, present both
   positions as viable alternatives with decisive experiments to break the tie
8. **Real code grounding:** At least one expert per round must reference a specific file
   path, dependency, or code pattern from the repository context. Abstract reasoning
   without code grounding is not allowed to continue past round 2
9. **Unique insight requirement:** Each expert must introduce at least one insight, concern,
   or piece of evidence per round that no other expert has mentioned. Rephrasing another
   expert's point does not count — extend it with a new risk, edge case, or counter-condition.
10. **Dominance guardrail:** If one expert contributes >50% of new insights across 2
    consecutive rounds, the next round forces: dominant expert gives only one short statement;
    other experts must introduce new evidence or counterexamples. This prevents lazy agent
    collapse where one perspective drowns out the others.

### What Makes a Good Round

- Experts **build on each other's points**, not just state independent opinions
- Challenges are **evidence-based** (pointing to real code, known constraints, documented patterns)
- Reasoning gets **more specific** each round (round 1 might be directional, round 3 should
  reference specific files and implementation details)
- Experts **change their position** when presented with good evidence — stubbornness is a
  signal of bad reasoning

## Step 3.5: Voting Round (Mandatory)

After the final deliberation round, each remaining expert casts a formal vote before the
recommendation is written. This forces explicit commitment and surfaces hidden disagreements.
Research shows voting rounds improve reasoning accuracy by ~13% (Town Hall Debate Prompting, 2025).

**Format:**
```
### Voting

**[Expert 1]** votes: [Approach in one sentence]
  Rationale: [2-3 sentences with evidence from deliberation]
  Weakness acknowledged: [Main downside of their chosen option]

**[Expert 2]** votes: [Approach in one sentence]
  Rationale: [2-3 sentences with evidence from deliberation]
  Weakness acknowledged: [Main downside of their chosen option]

**[Expert 3]** votes: [Approach in one sentence] (if still active)
  Rationale: [2-3 sentences with evidence from deliberation]
  Weakness acknowledged: [Main downside of their chosen option]

**Result:** [Unanimous / Majority N-M / Split] → [Winning approach]
```

**Rules:**
- Votes must be for a specific, actionable approach — not "it depends"
- If split, majority wins but minority rationale goes to "Dissenting Perspectives"
- If all 3 vote differently, run one focused round to narrow to 2 options, then re-vote

## Step 4: Consensus & Recommendation

After voting, produce a structured recommendation.

### Output Format

```
## Deliberation Summary

**Problem:** [One-sentence restatement]
**Rounds:** [N rounds, M experts remaining at consensus]
**Dropped experts:** [Who dropped and why, or "None"]

## Recommendation

[Clear, actionable recommendation in 2-4 sentences. Reference specific files, patterns,
or implementation approaches.]

## Implementation Approach

1. [First concrete step with file paths]
2. [Second concrete step]
3. [Continue as needed]

## Tradeoffs Acknowledged

| Decision | Benefit | Cost | Mitigating Factor |
|---|---|---|---|
| [Choice made] | [What you gain] | [What you sacrifice] | [How to reduce the cost] |

## Dissenting Perspectives

[If any expert dropped out or held a minority view that still has merit, document it
here. What conditions would make the alternative approach preferable?]

## Confidence Assessment

**Consensus strength:** [Strong / Moderate / Weak]
- Strong: All remaining experts fully aligned, reasoning chain is airtight
- Moderate: Experts agree on direction but differ on implementation details
- Weak: Majority position with meaningful unresolved concerns

**Key risk:** [The single biggest thing that could make this recommendation wrong]

## Validation Plan

1. [Tests to add or update]
2. [Observability or metrics to monitor]
3. [Failure signals and rollback triggers]
```

## Example: Architecture Decision

**User's problem:** "Should we switch from REST to GraphQL for our API layer?"

**Step 1 output (abbreviated):**
```
## Repository Context
- Stack: Node.js 20, Express 4.x, PostgreSQL 15, Prisma ORM
- API: 47 REST endpoints in src/routes/, average 3 joins per query
- Frontend: React 18 SPA, uses react-query for data fetching
- CLAUDE.md: "Avoid introducing new paradigms without migration path"
- Current pain: frontend makes 4-6 API calls per page load (src/pages/Dashboard.tsx)
```

**Step 2 output:**
```
### Expert Panel
**System Architect** — Optimizes for long-term maintainability and migration safety.
**Performance Engineer** — Optimizes for query efficiency and payload size.
**Frontend Consumer** — Optimizes for developer experience and data fetching simplicity.
```

**Deliberation proceeds for 4 rounds, Performance Engineer challenges System Architect's
assumption about N+1 queries, Frontend Consumer provides evidence from Dashboard.tsx
showing the real pain point is over-fetching, not endpoint count...**

**Final recommendation references specific files and proposes a BFF pattern as compromise.**

## Handling Edge Cases

**Problem is too simple for 3 experts:**
If the problem doesn't warrant multi-perspective analysis (e.g., "should I use const or
let here?"), say so. Suggest the user ask directly instead of using this framework.
Only activate deliberation for genuinely complex decisions.

**Experts all agree from round 1:**
Force deeper analysis anyway. Agreement on the surface often hides disagreement on
implementation details. In round 2, each expert must identify a risk or edge case the
others haven't mentioned. If they still agree after round 3, that's genuine consensus.

**Repository has no relevant code:**
If the project is empty or the problem is greenfield, experts should reason about
conventions, industry patterns, and the constraints found in config files. Acknowledge
the lack of existing code in the context brief.

**User specifies custom experts:**
If the user names specific expert roles, use those instead of presets. The deliberation
mechanics remain the same.

## Fallback: No Repository Available

If the repo is empty or inaccessible:
1. State the limitation upfront
2. Request the minimum required context from the user (tech stack, key files, constraints)
3. Run deliberation clearly labeled `Context-Limited Deliberation`
4. List assumptions that must be validated once real code is available

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/three-experts/`
- **Checkpoint frequency:** After each deliberation round
- **Subagent delegation:** Sub-point factual resolution (codebase lookups during challenges)

## Quality Checklist

Before presenting the final recommendation, verify:
- [ ] Repository was explored and real file paths appear in expert reasoning
- [ ] At least 3 rounds of deliberation occurred
- [ ] Each expert contributed unique insights per round (no echo-chamber behavior)
- [ ] Experts challenged each other with specific, evidence-based arguments
- [ ] Sub-point disagreements on verifiable facts were resolved inline with evidence
- [ ] Rotating devil's advocate duty was exercised each round
- [ ] Any dropout was justified by a demonstrated error, not just disagreement
- [ ] A formal voting round was conducted with explicit rationales
- [ ] Final recommendation includes concrete implementation steps with file paths
- [ ] Tradeoffs are documented with both costs and mitigating factors
- [ ] Dissenting perspectives are preserved for future reference
- [ ] The recommendation is actionable — someone could start implementing it now

---

## Feature Context Integration

When a feature-context is active, this skill writes deliberation summaries:

1. **After each deliberation round:** Write the round summary (accepted improvements, discarded suggestions, consensus) to feature-context
2. **After final consensus:** Write the final recommendation and plan updates to feature-context
3. **Data written:** expert identities, round count, accepted/discarded counts, final recommendation, dissenting views
