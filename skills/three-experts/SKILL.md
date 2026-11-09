---
name: three-experts
description: |
  Multi-expert deliberation framework for complex engineering decisions. Simulates 3
  domain-specific experts reasoning step-by-step through a problem, challenging each
  other's assumptions, and converging on a consensus solution grounded in real project
  code and architecture. Features 6 consolidated expert roles with concrete review scopes,
  structured distrust directives, Codex cross-validation, and ADR-format output. Use this
  skill when the user faces architecture decisions, refactoring strategies, debugging
  multi-layer issues, API/data model design, edge-case test generation, or any complex
  engineering problem that benefits from multiple perspectives. Trigger when the user says
  "three experts", "expert deliberation", "multi-perspective", "debate this", "architecture
  review", "think through this from multiple angles", "expert panel", "deliberate on", or
  asks for a decision with tradeoffs analyzed from different viewpoints.
version: 2.1.0
category: reasoning
depends: []
---

# Three Experts

A multi-expert deliberation framework that simulates 3 domain-specific experts reasoning
step-by-step through a complex engineering problem. Each expert runs as an independent
Agent subagent with a concrete review mandate, scope boundaries, and distrust directives.
Experts reason one step at a time, challenge each other with evidence, and converge on a
consensus. A Codex adversarial review validates the final recommendation before output.

## Process Overview

```
User's Problem
      |
      v
[1] Repository Exploration (gather real context)
      |
      v
[2] Expert Selection (pick 3 from 6 consolidated roles)
      |
      v
[3] Deliberation Rounds (3-6 rounds, step-by-step visible reasoning)
      |
      v
[3.5] Voting Round (each expert commits to a position)
      |
      v
[3.75] Codex Adversarial Review (independent cross-engine validation)
      |
      v
[4] Consensus & ADR Output (Architecture Decision Record format)
```

## Step 1: Repository Exploration (Mandatory)

Before any expert speaks, explore the repository to ground deliberation in reality.

1. **Read project docs** — Check `AGENTS.md`, `CLAUDE.md`, `README.md`, or knowledge base
   files. If `memory-bank/repo-context.md` exists, read it first — it may eliminate the
   need for further exploration.

2. **Read config files** — `package.json`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`,
   `go.mod`, `docker-compose.yml`, `.env.example`, or equivalent. Extract language,
   framework, dependencies, database, and runtime info.

3. **Search for relevant code** — Use Glob and Grep to locate files, services, components,
   or modules mentioned in the problem. Read key files for current implementation.

4. **Build a context brief** — Compile into a structured summary for all experts:
   - Tech stack with versions
   - Relevant file paths (real, verified)
   - Existing patterns and conventions
   - Current state of what is being discussed
   - Known constraints (performance, security, compatibility)

**Effort cap (adaptive):** Scale search effort to repo size:
- Small repo (<50 files): ~6 targeted searches
- Medium repo (50-500 files): ~12 targeted searches
- Large repo (500+ files): ~18 targeted searches, prioritize files mentioned in the problem

Present the context brief before deliberation under a `## Repository Context` header.

---

## Step 2: Expert Selection

Select 3 experts from the 6 consolidated roles below. Each role covers multiple
responsibility domains so that any combination of 3 provides broad coverage.

### The 6 Expert Roles

---

#### Role 1: Guardian
**Domain:** Security + Compliance + Resilience + Error Handling

**What they review:**
- **Security surface:** Input validation/sanitization on all external inputs. Auth centralized with token expiry/session management. Authorization at every layer with least-privilege. Injection vectors (SQL, XSS, CSRF, command injection, unsafe deserialization). Secrets management (no hardcoded creds, vault-based, rotation). Crypto (TLS 1.2+, AES-256 at rest, no deprecated algorithms). Dependency CVE scanning
- **Compliance & privacy:** PII identification/classification. Data minimization. Consent management. Retention policies with automated deletion. Right to deletion propagated to all systems. Tamper-resistant audit trails. Encryption at rest/transit for PII
- **Resilience:** Circuit breakers on external calls. Retry with exponential backoff + jitter. Explicit timeouts on every network call. Graceful degradation with defined fallbacks. Bulkheads for failure isolation. Health checks (liveness + readiness). Idempotency on retryable operations
- **Error handling:** Domain vs infrastructure exceptions (no generic catch-all). Errors bubble with context, never swallowed. Recovery strategies explicit per failure point. User-facing errors translated, no internals exposed. Resource cleanup in error paths. Every caught exception logged with context

**Does NOT review:** Performance optimization (beyond resilience-related thresholds like circuit breaker tuning), code style, UI/UX patterns, test coverage numbers, feature correctness.

**Red flags:** `eval()` with user input | SQL string concatenation | secrets in source/logs | disabled CSRF | overly permissive CORS | missing auth middleware | PII in logs/plaintext | empty catch blocks | `catch(e) { return null }` | retry without backoff | no timeout on HTTP client | no circuit breaker fallback | health check always returning 200 | PII without encryption | no retention policy | no audit trail

**Questions they force:**
- "What happens if this input is 10MB of garbage?"
- "Who can call this endpoint and what's the blast radius if their token is stolen?"
- "If step 3 of 5 fails, what state is the system in?"

---

#### Role 2: Architect
**Domain:** Architecture + DDD + Distributed Systems + Over-Engineering Detection

**What they review:**
- **Structure:** Module boundaries, no circular dependencies. Coupling (depend on abstractions). Cohesion (related functionality grouped). Scalability (components scale independently, state externalized). Design patterns match the problem, not forced
- **Domain design:** Bounded contexts with consistent internal models. Ubiquitous language matching stakeholder terms. Aggregates with correct transactional boundaries. Domain events at aggregate boundaries. Anti-corruption layers at context boundaries. Domain logic in domain objects (anemic model detection)
- **Distribution:** Async preferred over sync for cross-service. Consistency model explicit per operation. No hardcoded service URLs. Each data piece owned by one service. Saga/choreography, not distributed transactions. Event schema versioning
- **Over-engineering detection:** YAGNI violations (abstractions for hypothetical use). Premature generalization (interfaces with 1 implementation). Indirection depth (files to traverse per feature). Configuration for things that never change

**Does NOT review:** Line-level security, performance benchmarks, test implementation, deployment config, CSS/styling.

**Red flags:** God classes (20+ responsibilities) | circular dependencies | business logic in controllers | anemic domain model | aggregate spanning 10+ tables | shared DB between services | synchronous chain of 4+ services | distributed 2PC | hardcoded service URLs | factory/strategy with 1 type | 6-layer call stack to save a record | `AbstractBaseHandler<T,R,E>` used once

**Questions they force:**
- "If we replace this database/queue/cache, how many files change?"
- "Can a new developer understand the boundaries in 30 minutes?"
- "How many implementations does this interface have today?"

---

#### Role 3: Performance & Data
**Domain:** Performance + DB/Data Modeling + Concurrency + Cost

**What they review:**
- **Algorithmic:** O(n^2) in hot paths, unnecessary nested iterations. Memory leaks, unbounded caches. Network chattiness (many small calls vs batching). Missing connection pooling. Response time targets per endpoint (p95)
- **Database & data modeling:** Normalization (3NF for transactional, intentional denormalization documented). Constraints (NOT NULL, UNIQUE, CHECK, FKs). Indexing on PKs, FKs, and query patterns. Correct data types. Reversible migrations. No unbounded IN clauses, pagination on all lists, no SELECT * in production. Data lifecycle (retention, archival, soft vs hard delete)
- **Concurrency:** Shared mutable state identified and protected. No check-then-act on shared state. Deadlock prevention (lock ordering). Thread pool sizing. Correct concurrent collection usage
- **Cost & efficiency:** Resource sizing based on measured load. Auto-scaling with ceilings. Storage tiering. Log cost hygiene. Cost attribution tags

**Does NOT review:** Security vulnerabilities, business logic correctness, API design conventions, documentation, accessibility.

**Red flags:** `SELECT *` without LIMIT | loop with HTTP calls per iteration | missing indexes on FK/WHERE | synchronous I/O in async handlers | no pagination | N+1 queries | VARCHAR(MAX) everywhere | no timestamps | missing FK constraints | no auto-scaling ceiling | metrics with unbounded cardinality

**Questions they force:**
- "What's the p95 latency at 10x current traffic?"
- "What happens when this table has 100M rows?"
- "Can two threads reach this code simultaneously?"

---

#### Role 4: Quality & Observability
**Domain:** Testing + Observability + Debuggability

**What they review:**
- **Testing:** Coverage >80% critical, >70% overall, enforced in CI. Edge cases (boundaries, nulls, max sizes, concurrency). Test isolation (no shared state, parallelizable). Meaningful assertions (behavior, not implementation). Mocks at boundaries only. Integration tests for happy + failure paths. Zero flaky tests. Descriptive test names
- **Observability:** Structured JSON logging with consistent fields. Correlation IDs from edge through all services. Appropriate log levels (ERROR=actionable, WARN=degraded, INFO=business, DEBUG=troubleshooting). Golden signal metrics per service (latency, traffic, errors, saturation) as histograms. Distributed tracing across boundaries
- **Debuggability:** SLO-based burn-rate alerts with runbook links. PII redaction in logs/traces. Per-service dashboards (p50/p95/p99, error rates, saturation). Error responses with machine-readable codes and correlation IDs

**Does NOT review:** Architecture patterns, security posture, business logic, feature completeness, UI design.

**Red flags:** Tests that pass when assertion removed | `@Ignore`/`skip` without ticket | mocking 5+ deps | no assertion | test names like `test1()` | shared DB state between tests | `console.log("error")` with no context | missing correlation ID | averages not percentiles | no tracing across async | PII in logs | alerts without runbook

**Questions they force:**
- "What breaks if I delete this test — would we notice?"
- "If this fails at 2 AM, can an engineer determine what failed in under 5 minutes?"
- "Can I trace a single user request across all services?"

---

#### Role 5: Developer Experience
**Domain:** API Design + DX + Accessibility + Frontend Patterns

**What they review:**
- **API design:** Domain-language naming, consistent across endpoints. Uniform pagination/filtering/sorting/error patterns. Versioning with backward compatibility. Structured error responses (machine-readable codes, no stack traces). Idempotency keys on POST/PUT. Auto-generated OpenAPI docs with examples. Rate limiting with headers. Time-to-first-successful-call under 15 minutes
- **Accessibility:** Keyboard navigation (Tab reach, logical focus order, visible indicators, no traps). Screen reader support (semantic HTML, alt text, ARIA). Color contrast (4.5:1 normal, 3:1 large — WCAG AA). Form accessibility (labels, linked error messages). Logical heading hierarchy. ARIA live regions for dynamic content. `prefers-reduced-motion` respected. Touch targets >= 44x44px
- **Frontend patterns:** Component composition/reusability. State management hygiene. Loading/error/empty states handled. Breaking changes via deprecation + migration guide + sunset timeline

**Does NOT review:** Backend implementation, database schema, deployment infra, security (beyond API surface), performance (beyond DX impact).

**Red flags:** Inconsistent endpoint naming | no error schema | breaking change without version bump | 200 with error in body | no pagination on collections | `<div onclick>` instead of `<button>` | missing alt text | color as only state indicator | no visible focus styles | `tabindex > 0` | form without labels | skipped heading levels

**Questions they force:**
- "Can a developer integrate this API in under 15 minutes without calling us?"
- "Can I complete this entire flow using only a keyboard?"
- "What does a screen reader announce for this component?"

---

#### Role 6: Devil's Advocate
**Domain:** Cross-cutting adversarial review

**What they review:**
- **Assumption challenge:** Questions every "obvious" design choice. "Why not the opposite?"
- **Failure imagination:** Worst-case scenarios the team hasn't considered
- **Dependency skepticism:** "What if this third-party shuts down / changes API?"
- **Requirements questioning:** "Does the user actually need this? What's the evidence?"
- **Complexity cost:** Every abstraction must justify its existence with concrete scenarios
- **Counter-proposals:** Must provide an alternative for every criticism (pure critique not allowed)
- **Scale stress:** Mental load testing at 10x, 100x, 1000x current assumptions
- **Consensus resistance:** Even if agreeing, must articulate the strongest possible objection

**Does NOT review:** Implementation correctness at line level, code style, test coverage metrics, documentation formatting.

**Red flags:** Optimistic assumptions without fallback | single vendor dependency for critical path | "we'll handle that later" without ticket | complexity justified by hypothetical future | no load testing plan | consensus without alternatives considered

**Questions they force:**
- "What's the simplest thing that could possibly work instead?"
- "What kills us if this assumption is wrong?"
- "Should we do this at all?"

---

### Expert Selection Matrix

| Problem Type | Expert 1 | Expert 2 | Expert 3 |
|---|---|---|---|
| Architecture decisions | Architect | Performance & Data | Devil's Advocate |
| API / data model design | Architect | Developer Experience | Guardian |
| Debugging multi-layer | Performance & Data | Quality & Observability | Guardian |
| New fullstack feature | Architect | Developer Experience | Quality & Observability |
| Refactoring / tech debt | Architect | Performance & Data | Quality & Observability |
| Security / compliance | Guardian | Architect | Devil's Advocate |
| Performance crisis | Performance & Data | Quality & Observability | Devil's Advocate |
| Frontend / UX overhaul | Developer Experience | Quality & Observability | Architect |
| Incident post-mortem | Guardian | Quality & Observability | Devil's Advocate |
| Greenfield / new service | Architect | Guardian | Devil's Advocate |
| Migration / stack upgrade | Performance & Data | Architect | Quality & Observability |

### Expert Adaptation Rules

- If the problem spans two categories, blend: pick the most relevant expert from each row.
- If the project has a dominant concern (e.g., compliance, real-time perf), ensure that
  concern's primary role is always included.
- Always aim for tension — three experts who agree on everything provide no value.
- The Devil's Advocate does not need a dedicated slot every time. When not selected,
  their adversarial duty rotates among the 3 selected experts (one per round).
- If the user specifies custom experts, use those. The deliberation mechanics stay the same.

### Expert Introduction Format

```
### Expert Panel

**[Role Name]** — [What they optimize for and their natural bias]
  Scope: [Key domains in this deliberation]
  Tension with: [Which expert they'll clash with and why]
```

---

## Execution Model: 3 Persistent Agents (Mandatory)

Each expert MUST run as its own independent Agent subagent (`subagent_type: expert`,
defined in `${CLAUDE_PLUGIN_ROOT}/agents/expert.md`: Opus, effort high). A single context simulating
3 voices collapses into one perspective with 3 labels. When this skill is installed as
the `keel-skills` plugin, the agent types are namespaced: `keel-skills:expert`,
`keel-skills:explorer` and `keel-skills:codex-fallback-auditor`. If neither name is
available, use `general-purpose` with the agent file's instructions in the prompt. Separate agents ensure genuine
independence, true diversity, no dominance collapse, and parallel execution.

**Launch once, continue with SendMessage.** The 3 agents are launched in round 1 only.
Every later round and the voting round are follow-up messages to the SAME three agents
(`SendMessage` with the agent's name or ID): each expert keeps the evidence it already
verified in the repo, so a round costs one message plus the targeted lookups the new
challenges need, not a fresh 50k start plus a re-exploration. Measured over 30 sessions,
fresh-per-round agents averaged ~100 requests each; a continued agent needs 15-25.
Never relaunch an expert between rounds unless its agent is gone (then relaunch it with
its round-1 prompt plus the paths of its own previous position files).

**Positions live on disk, digests travel.** Every round, each expert writes its full
reasoning to `.workspace/ctx/three-experts/<feature>-r<N>-<role-slug>.md` and returns to
the orchestrator ONLY the digest below (at most 15 lines). The orchestrator synthesizes
from the digests and opens a full file only for a point it must adjudicate. The next
round's message references the synthesis and the other experts' files by path; an
expert that needs the full argument reads the file. The digest is not evidence, the
file is.

### Agent Prompt Template

Round 1: launch 3 `expert` subagents in parallel, one per expert. Each receives:

```
You are {Role Name} — {domain description}.

YOUR MANDATE: {What they review — from role definition}
YOUR BOUNDARIES: {Does NOT review — from role definition}
RED FLAGS: {Red flags list}
KEY QUESTIONS: {Questions list}

DISTRUST DIRECTIVE:
Do not trust other experts' claims at face value. When another expert asserts
a fact about the codebase, verify it independently. "Expert N said X" is not
evidence — code is evidence.

CONTEXT: {repository_context_from_step_1}
PROBLEM: {user_problem}
FEATURE SLUG: {feature_slug}
YOUR POSITION FILE THIS ROUND: .workspace/ctx/three-experts/{feature_slug}-r{N}-{role_slug}.md
SYNTHESIS OF PREVIOUS ROUND (round 2+): {path_to_synthesis_file}
OTHER EXPERTS' FILES (round 2+): {paths_to_their_position_files}
CHALLENGES TO ADDRESS: {challenges_from_previous_round}

YOUR TASK FOR ROUND {N}:
1. Self-critique: Strongest objection to your current view (1 sentence)
2. Updated position: 2-4 sentences with real file references
3. Challenge: One specific flaw in another expert's reasoning (with code evidence)
4. Devil's advocate (if your turn): One adversarial point against emerging consensus
5. Confidence: 1-5. Only surface claims you are >80% sure about
6. Anti-recommendation: One specific thing NOT to do, with why

RULES:
- Reference specific file paths, dependencies, or code patterns
- State concrete, falsifiable claims — not vague observations
- "Consider X" or "look into Y" are deliberation failures. Be specific.
- Build on previous discussion, don't repeat
- If your reasoning was wrong, say so explicitly and withdraw
- Do not re-verify what you already established in earlier rounds; verify what is new

OUTPUT CONTRACT:
- Write your FULL reasoning (all 6 task items, with file references) to your position file.
- Reply with ONLY this digest (at most 15 lines):
  POSITION: <2 sentences>
  CHALLENGE: <expert>: <1 sentence + file:line>
  DEVIL'S ADVOCATE: <1 sentence, or "not my turn">
  ANTI-RECOMMENDATION: <1 sentence>
  CONFIDENCE: <1-5>
  STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
  FILE: <path of your position file>
```

Collect the 3 digests. The orchestrator synthesizes each round: presents positions,
resolves NEEDS_CONTEXT via codebase lookup (delegate it to an `explorer` subagent when
it is more than a grep), resolves factual sub-points, tracks dropouts and convergence,
writes the synthesis to `.workspace/ctx/three-experts/<feature>-r<N>-synthesis.md`, and
sends round N+1 to each expert with `SendMessage`: the synthesis path, the challenges
addressed to that expert, the other experts' file paths, and the round's task. Keep the
message short; the files carry the argument.

---

## Step 3: Deliberation Rounds

Each round has three phases:

**Phase A — Research + Position:** Each expert investigates evidence, writes a one-sentence
self-critique, then states their position (2-4 sentences) with file references, confidence
rating, and an anti-recommendation.

**Phase B — Challenge + Resolution:** Experts challenge each other with specific evidence
("Expert 2 assumes X, but file Y shows Z"). Sub-point factual disagreements are resolved
immediately by checking the codebase. Cap: 2 sub-point resolutions per deliberation.

> **Resolved:** [Question] -> [Answer with evidence]. [Correct expert] proceeds;
> [Wrong expert] updates next round.

**Rotating Devil's Advocate:** Each round, one expert (rotating 1->2->3->1) must include
an adversarial point against emerging consensus, even if they agree. If Role 6 is selected,
they do this every round.

**Phase C — Reassessment:** Experts with demonstrated errors drop out:

```
**[Role Name]:** I withdraw. [Expert N]'s point about [issue] invalidates my
assumption that [X]. My perspective now aligns with [expert].
Salvaged insights: [Partial insights worth preserving]
```

### Round Format

```
### Round N

**[Role 1]** (Step N) [Confidence: X/5] [Status: ...]:
[Reasoning with real code/file references]
Anti-recommendation: [What NOT to do]

**[Role 2]** (Step N) [Confidence: X/5] [Status: ...]:
[Reasoning with real code/file references]
Anti-recommendation: [What NOT to do]

**[Role 3]** (Step N) [Confidence: X/5] [Status: ...]:
[Reasoning with real code/file references]
Anti-recommendation: [What NOT to do]

**Challenges:** [Specific challenges with evidence]
**Resolved:** [Sub-point resolutions]
**Dropouts:** [None / Expert + reason + salvaged insights]
```

### Deliberation Rules

1. **Minimum 2 rounds, then the exit check**: after round 2, go straight to the voting
   round only if ALL hold: no expert is BLOCKED or NEEDS_CONTEXT; every challenge raised
   has a recorded resolution or withdrawal; the remaining experts state the decisive
   points in the same terms. If any fails, round 3 is mandatory (round-1 agreement alone
   never satisfies the check; see Edge Cases)
2. **Maximum 6 rounds** — if no consensus by round 6, go to majority recommendation
3. **No repeated arguments** — each round must introduce new reasoning or evidence
4. **Falsifiable claims only** — concrete, testable statements. "Consider X" = failure
5. **Dropout on demonstrated error** — not merely because others disagree. Preserve salvaged insights
6. **Convergence** — consensus when all remaining experts (min 2) agree and state it in same terms
7. **Tie-breaking** — if 2 experts can't converge by round 6, present both with decisive experiments
8. **Code grounding** — at least one expert per round must reference a specific file path.
   Abstract reasoning without code grounding cannot continue past round 2
9. **Unique insight** — each expert must add something no other has mentioned, per round
10. **Dominance guardrail** — if one expert contributes >50% of insights across 2 consecutive
    rounds, next round forces: dominant expert gives only one short statement, others lead
11. **Confidence threshold** — only assert claims >80% confident. Lower-confidence observations
    go to a "speculative" section that doesn't drive decisions

---

## Step 3.5: Voting Round (Mandatory)

Each remaining expert casts a formal vote, requested with `SendMessage` to its existing
agent (never a fresh agent: the vote must come from the context that argued the rounds):

```
### Voting

**[Role 1]** votes: [Approach in one sentence]
  Rationale: [2-3 sentences with evidence]
  Weakness acknowledged: [Main downside]
  Anti-recommendation: [What NOT to do when implementing]
  Confidence: [X/5]

**[Role 2]** votes: [Approach in one sentence]
  ...

**[Role 3]** votes: [Approach in one sentence] (if still active)
  ...

**Result:** [Unanimous / Majority N-M / Split] -> [Winning approach]
```

**Rules:** Votes must be specific and actionable (not "it depends"). Majority wins but
minority rationale goes to "Dissenting Perspectives". If all 3 vote differently, run one
focused round to narrow to 2, then re-vote.

---

## Step 3.75: Codex Adversarial Review

After voting, run an independent Codex validation to catch blind spots that all 3 Claude
agents might share due to same-model bias. This is the cross-engine check.

Use the hardened `codex exec` invocation — sandbox bypass, stdin redirect, timeout,
file-based prompt and output. A bare `codex exec "..."` without these flags can hang in
sandboxed environments (stdin left open, or a sandbox that blocks Codex's own shell
tools). NEVER interpolate the problem,
context, or consensus text directly into the shell command string — write them to a
file with the Write tool and have Codex read it from disk:

1. **Write the deliberation dossier** to a temp file (Write tool), containing three
   sections: `## Problem` (the user's problem), `## Repository Context` (the Step 1
   context brief), and `## Consensus Recommendation` (the voting result + rationale).

2. **Run the hardened invocation:**

```bash
PROMPT_FILE=$(mktemp /tmp/three-experts-codex-XXXXXX.txt)
CODEX_OUT=$(mktemp /tmp/three-experts-codex-XXXXXX.jsonl)
CODEX_ERR=$(mktemp /tmp/three-experts-codex-XXXXXX.err)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# DOSSIER_FILE = the file written in step 1 (path expands OUTSIDE the quoted heredoc)
printf 'Read this file in full FIRST: %s\n\n' "$DOSSIER_FILE" > "$PROMPT_FILE"

cat >> "$PROMPT_FILE" <<'PROMPT_EOF'
You are an adversarial reviewer validating an architecture decision made by 3 expert
agents. The file above contains the problem, the repository context, and the consensus
recommendation. Your job is to find flaws, blind spots, or risks the experts missed.
Be critical and specific.

Review for:
1. FACTUAL ERRORS — Do the experts' claims about the codebase match reality? Verify file paths, dependency capabilities, and API contracts they referenced.
2. MISSED ALTERNATIVES — Is there a simpler or more proven approach the experts didn't consider?
3. HIDDEN RISKS — What failure modes, scale issues, or operational costs did they overlook?
4. OVER-ENGINEERING — Is the recommendation more complex than the problem requires?
5. ASSUMPTION GAPS — What assumptions are they making that aren't validated by evidence?

For each finding:
- Severity: CRITICAL (recommendation is wrong) / HIGH (significant risk missed) / MEDIUM (blind spot worth noting)
- Issue: What's wrong
- Evidence: Why you believe this (reference specific files or patterns)
- Suggestion: What should change in the recommendation

End with: ENDORSE (recommendation is sound) / AMEND (recommendation needs specific changes) / REJECT (fundamental flaw, reconsider)
PROMPT_EOF

CODEX_ANSWER=$(mktemp /tmp/three-experts-codex-XXXXXX.answer.md)
CODEX_STATUS=$(mktemp /tmp/three-experts-codex-XXXXXX.status)
if python3 "${CLAUDE_PLUGIN_ROOT}/scripts/codex/codex-status.py" preflight > "$CODEX_STATUS"; then
  timeout 360 codex exec --json -C "$REPO_ROOT" --skip-git-repo-check \
    --dangerously-bypass-approvals-and-sandbox "$(cat "$PROMPT_FILE")" \
    < /dev/null > "$CODEX_OUT" 2> "$CODEX_ERR"
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/codex/codex-status.py" classify --exit $? --out "$CODEX_OUT" \
    --answer-file "$CODEX_ANSWER" > "$CODEX_STATUS"
fi
cat "$CODEX_STATUS"   # status=ok -> the review is in $CODEX_ANSWER
```

`status=ok` means `$CODEX_ANSWER` holds the review. Clean up the `/tmp/three-experts-*`
temp files after integrating the findings. Classification and the quota memo follow
`${CLAUDE_PLUGIN_ROOT}/scripts/codex/README.md` (only terminal JSONL events count; stderr is ignored).

**Fallback:** any other status (`not-installed`, `quota`, `capacity`, `auth`, `timeout`,
`failed`) means Codex is unavailable: launch ONE `codex-fallback-auditor` subagent
(`${CLAUDE_PLUGIN_ROOT}/agents/codex-fallback-auditor.md`: Sonnet, read-only) with the same prompt file
(same dossier, same adversarial mandate, same ENDORSE / AMEND / REJECT output). Do not skip
the adversarial review, but never re-invoke Codex and never wait for a quota reset. Label
the ADR's "Codex Validation" section `Claude-only; Codex unavailable: <status>` so nobody
reads it as a Codex verdict.

**Integration:** If Codex returns AMEND or REJECT:
- Present Codex findings to the user alongside the expert consensus
- Incorporate valid criticisms into the ADR's "Risks" and "Alternatives" sections
- If REJECT, flag the specific flaw and suggest reconvening experts on that point

---

## Step 4: Consensus & Recommendation (ADR Format)

Produce a structured Architecture Decision Record incorporating expert deliberation
and Codex validation.

```
## Architecture Decision Record

**Title:** [Decision in imperative form: "Use X for Y"]
**Status:** Proposed
**Date:** [YYYY-MM-DD]
**Deciders:** [Role 1], [Role 2], [Role 3] + Codex validation

### Context

[Problem, forces, and constraints. 2-4 sentences referencing real project state.]

### Decision

[Clear, actionable recommendation in 2-4 sentences. Reference specific files, patterns,
or implementation approaches.]

### Implementation Approach

1. [First concrete step with file paths]
2. [Second concrete step]
3. [Continue as needed]

### What NOT To Do

- [Anti-recommendation 1 from deliberation, with reason]
- [Anti-recommendation 2]

### Consequences

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative:**
- [Cost 1 — with mitigating factor]
- [Cost 2 — with mitigating factor]

### Alternatives Considered

| Alternative | Why rejected | When it would be better |
|---|---|---|
| [Option A] | [Reason with evidence] | [Conditions that flip the decision] |
| [Option B] | [Reason with evidence] | [Conditions that flip the decision] |

### Dissenting Perspectives

[Minority views with merit. Conditions that would make the alternative preferable.]

### Codex Validation

**Verdict:** [ENDORSE / AMEND / REJECT]
[Summary of Codex findings, if any. Amendments incorporated above.]

### Confidence Assessment

**Consensus strength:** [Strong / Moderate / Weak]
**Average confidence:** [X/5 across voting experts]
**Key risk:** [Single biggest thing that could make this recommendation wrong]

### Validation Plan

1. [Tests to add or update]
2. [Observability or metrics to monitor]
3. [Failure signals and rollback triggers]
```

---

## Edge Cases

- **Problem too simple:** Say so. Suggest asking directly instead of 3-expert deliberation.
- **Experts agree from round 1:** Force deeper analysis. Round 2: each must identify a risk
  others haven't mentioned. Genuine consensus is confirmed only by the round-2 exit check
  (rule 1), never by round-1 agreement; if the check fails, round 3 runs.
- **No relevant code (greenfield):** Experts reason about conventions and config constraints.
  Acknowledge the limitation in the context brief.
- **Custom experts:** User-specified roles replace the 6 roles. Mechanics stay the same.
- **BLOCKED/NEEDS_CONTEXT:** Orchestrator resolves before next round. NEEDS_CONTEXT triggers
  codebase lookup. BLOCKED prompts the user for missing information.
- **No repository available:** State limitation, request minimum context from user, label
  output `Context-Limited Deliberation`, list assumptions to validate when code is available.

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/three-experts/`
- **Checkpoint frequency:** After each deliberation round
- **Subagent delegation:** Sub-point factual resolution (codebase lookups during challenges,
  as `explorer`)
- **Files:** `<feature>-r<N>-<role>.md` (expert positions), `<feature>-r<N>-synthesis.md`
  (orchestrator synthesis per round)

## Quality Checklist

Before presenting the final recommendation, verify:
- [ ] Repository explored, real file paths in expert reasoning
- [ ] Experts launched once (`expert` type) and continued with SendMessage; positions
      written to `.workspace/ctx/three-experts/`, digests only in the orchestrator
- [ ] At least 2 deliberation rounds occurred, and round 3+ ran whenever the exit check failed
- [ ] Each expert received full role definition (scope, boundaries, red flags, questions)
- [ ] Each expert contributed unique insights per round
- [ ] Experts challenged each other with evidence-based arguments
- [ ] Distrust directive active: experts verified claims, not just accepted
- [ ] Sub-point factual disagreements resolved inline with evidence
- [ ] Rotating devil's advocate exercised each round
- [ ] Dropouts justified by demonstrated error, with salvaged insights
- [ ] Confidence ratings provided per expert per round
- [ ] Anti-recommendations included in final output
- [ ] Formal voting round conducted with rationales and weaknesses
- [ ] Codex adversarial review completed (or fallback used)
- [ ] Codex findings integrated into ADR (if AMEND or REJECT)
- [ ] Final output follows ADR format with alternatives and reversal conditions
- [ ] No vague language: no "consider", "look into", "TBD", "add appropriate handling"
- [ ] Recommendation is actionable — someone could start implementing now
