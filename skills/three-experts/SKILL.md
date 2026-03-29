---
name: three-experts
description: |
  Multi-expert deliberation framework for complex engineering decisions. Simulates 3
  domain-specific experts reasoning step-by-step through a problem, challenging each
  other's assumptions, and converging on a consensus solution grounded in real project
  code and architecture. Features 6 consolidated expert roles with concrete review scopes,
  structured distrust directives, and ADR-format output. Use this skill when the user
  faces architecture decisions, refactoring strategies, debugging multi-layer issues,
  API/data model design, edge-case test generation, or any complex engineering problem
  that benefits from multiple perspectives. Trigger when the user says "three experts",
  "expert deliberation", "multi-perspective", "debate this", "architecture review",
  "think through this from multiple angles", "expert panel", "deliberate on", or asks
  for a decision with tradeoffs analyzed from different viewpoints.
---

# Three Experts

A multi-expert deliberation framework that simulates 3 domain-specific experts reasoning
step-by-step through a complex engineering problem. Each expert runs as an independent
Agent subagent with a concrete review mandate, structured scope boundaries, and distrust
directives. Experts reason one step at a time, share with the group, challenge each other
with evidence, and converge on a consensus.

## Why This Exists

Complex engineering decisions have tradeoffs that look different depending on your role.
A Guardian optimizes for safety, an Architect for structure, a Performance expert for
efficiency. By simulating these perspectives reasoning together — visible step by step,
challenging each other — you get a decision that accounts for concerns a single viewpoint
would miss. Grounding this in real project code prevents generic thought exercises.

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
[3] Deliberation Rounds (step-by-step visible reasoning)
      |    - Research-before-opinion (cite evidence, not assumptions)
      |    - Self-deliberation + position per expert
      |    - Challenges with sub-point resolution
      |    - Rotating devil's advocate
      |    - Structured distrust (verify, don't trust)
      |    - Wrong experts drop out
      |
      v
[3.5] Voting Round (each expert commits to a position)
      |
      v
[4] Consensus & ADR Output (Architecture Decision Record format)
```

## Step 1: Repository Exploration (Mandatory)

Before any expert speaks, explore the repository to ground deliberation in reality.

**What to do:**

1. **Read project docs** — Check for `AGENTS.md`, `CLAUDE.md`, `README.md`, or knowledge
   base files in the project root or `.claude/` directory. If `memory-bank/repo-context.md`
   exists, read it first — it may eliminate the need for further exploration.

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

---

## Step 2: Expert Selection

Select 3 experts from the 6 consolidated roles below. Each role covers multiple
responsibility domains so that any combination of 3 provides broad coverage.

### The 6 Expert Roles

---

#### Role 1: Guardian
**Domain:** Security + Compliance + Resilience + Error Handling

**What they review:**
- **Security surface:** Input validation and sanitization on all user/external inputs. Authentication centralized with token expiry and session management. Authorization enforced at every layer (gateway, service, database) with least-privilege. Injection vectors: SQL, XSS, CSRF, command injection, unsafe deserialization. Secrets management: no hardcoded credentials, vault-based storage, rotation policy. Cryptography: TLS 1.2+ in transit, AES-256 at rest, no deprecated algorithms (MD5, SHA-1). Dependency vulnerabilities: CVE scanning, no unpatched high/critical packages
- **Compliance & privacy:** PII identification and data classification. Data minimization (only collect what's needed). Consent management and granular opt-in/opt-out. Retention policies per data type with automated deletion. Right to deletion (GDPR Art. 17) propagated to all systems. Audit trails: tamper-resistant, who accessed what and when. Encryption at rest and in transit for PII
- **Resilience:** Circuit breakers on all external dependency calls with sensible thresholds. Retry policies: exponential backoff + jitter, retry budget limits. Explicit timeouts on every network call (no infinite waits). Graceful degradation: fallback behavior defined (stale cache, limited mode). Bulkheads: failure isolation between subsystems. Health checks: liveness and readiness probes, dependency health propagation. Idempotency: retryable operations produce same result on re-execution
- **Error handling:** Domain exceptions vs infrastructure exceptions (not generic catch-all). Errors bubble up with context added at each layer, never swallowed silently. Recovery strategies explicit per failure point: retry, fallback, compensating transaction, or fail-fast. User-facing errors translated to meaningful messages, no internal details exposed. Resource cleanup in error paths (finally blocks, try-with-resources). Every caught exception logged with context (what, who, what they tried)

**Does NOT review:** Performance optimization, code style, UI/UX patterns, test coverage numbers, feature correctness.

**Red flags they catch:**
`eval()` with user input | SQL string concatenation | secrets in source/logs | disabled CSRF | overly permissive CORS | missing auth middleware | PII in logs or plaintext | empty catch blocks | `catch(e) { return null }` | retry without backoff | no timeout on HTTP client | no circuit breaker fallback | health check always returning 200 | PII stored without encryption | no retention policy | no audit trail on data access

**Questions they force:**
- "What happens if this input is 10MB of garbage?"
- "Who can call this endpoint and what's the blast radius if their token is stolen?"
- "What happens to the user when this line throws?"
- "If step 3 of 5 fails, what state is the system in?"
- "If a user requests deletion today, how long until their data is fully purged?"

---

#### Role 2: Architect
**Domain:** Architecture + DDD + Distributed Systems + Over-Engineering Detection

**What they review:**
- **Structure:** Module boundaries with clear separation of concerns, no circular dependencies. Coupling analysis: depend on abstractions, not implementations. Cohesion: related functionality grouped, not scattered. SOLID principles applied where they add value. Scalability: components scale independently, state externalized. Design pattern appropriateness: patterns match the problem, not forced
- **Domain design:** Bounded contexts clearly defined with consistent internal models. Ubiquitous language: code uses domain terms matching what stakeholders say. Aggregates: transactional consistency boundaries correct, not too large or too small. Domain events: meaningful business events at aggregate boundaries, not CRUD notifications. Anti-corruption layers at context boundaries. Domain logic in domain objects, not leaked into services/controllers (anemic model detection)
- **Distribution:** Communication patterns: async preferred over sync for cross-service, sync choices documented. Consistency model explicit per operation (strong, eventual, causal). Service discovery mechanism defined, no hardcoded URLs. Data ownership: each piece owned by exactly one service, no shared databases. Workflow orchestration via saga/choreography, not distributed transactions. Event schema versioning
- **Over-engineering detection:** YAGNI violations: abstractions for hypothetical future use with no evidence. Premature generalization: interfaces/factories/strategies with exactly one implementation. Indirection depth: how many files must a developer traverse to understand a feature. Configuration explosion: settings for things that never change. Abstraction justification: every layer needs 2+ concrete consumers or documented extension plan

**Does NOT review:** Line-level security posture, performance benchmarks, test implementation details, deployment configuration, CSS/styling.

**Red flags they catch:**
God classes with 20+ responsibilities | circular dependencies | business logic in controllers | infrastructure concerns in domain layer | anemic domain model (entities with only getters/setters) | aggregate spanning 10+ tables | shared database between services | synchronous chain of 4+ services | distributed transaction (2PC) across services | hardcoded service URLs | factory with 1 type | strategy pattern with 1 strategy | 6-layer call stack to save a record | custom ORM wrapper around ORM | `AbstractBaseHandler<T,R,E>` used once

**Questions they force:**
- "If we replace this database/queue/cache, how many files change?"
- "Can a new developer understand the boundaries in 30 minutes?"
- "What business invariant does this aggregate protect?"
- "How many implementations does this interface have today, and what's the evidence for more?"
- "If I deleted this abstraction and inlined the code, what would break?"

---

#### Role 3: Performance & Data
**Domain:** Performance + DB/Data Modeling + Concurrency + Cost

**What they review:**
- **Algorithmic:** O(n^2) or worse in hot paths, unnecessary nested iterations. Memory leaks, unbounded caches, large allocations in loops. Network chattiness (many small calls vs batching), missing connection pooling. Response time targets defined per endpoint (p95), measured and alerted
- **Database & data modeling:** Normalization: at least 3NF for transactional data, intentional denormalization documented. Constraints: NOT NULL, UNIQUE, CHECK, foreign keys at database level. Indexing: on PKs, FKs, and actual query patterns. Data types: correct type and size for usage. Migrations: reversible, tested, no data loss on rollback. Query patterns: no unbounded IN clauses, pagination on all list queries, no SELECT * in production. Data lifecycle: retention, archival, soft-delete vs hard-delete documented
- **Concurrency:** Shared mutable state identified, documented, and protected. No check-then-act on shared state, atomic operations on concurrent maps. Deadlock prevention: lock ordering documented, nested critical sections minimized. Thread pool sizing: appropriate, named threads, explicit shutdown. Correct concurrent collection usage (ConcurrentHashMap, not synchronized HashMap)
- **Cost & efficiency:** Resource sizing based on measured load, not guesses. Auto-scaling with ceilings and scale-in policies. Storage lifecycle: hot/warm/cold tiering. Logging cost: high-cardinality label guards, log level hygiene. Reserved capacity where steady-state baseline exists. All resources tagged for cost attribution

**Does NOT review:** Security vulnerabilities, business logic correctness, API design conventions, documentation quality, accessibility.

**Red flags they catch:**
`SELECT *` without LIMIT | `for` loop making HTTP calls per iteration | missing indexes on FK/WHERE columns | synchronous I/O in async handlers | no pagination on list endpoints | N+1 query patterns | VARCHAR(MAX) everywhere | no created_at/updated_at timestamps | missing FK constraints | separate `containsKey()+put()` on ConcurrentMap | blocking I/O in parallel stream | no auto-scaling ceiling | metrics with unbounded cardinality | idle resources 24/7 | no cost tags

**Questions they force:**
- "What's the p95 latency at 10x current traffic?"
- "How does this behave when the cache is cold?"
- "What happens when this table has 100M rows?"
- "Can two threads reach this code simultaneously?"
- "What does this cost per month at current scale and at 10x?"

---

#### Role 4: Quality & Observability
**Domain:** Testing + Observability + Debuggability

**What they review:**
- **Testing:** Coverage >80% for critical modules, >70% overall, enforced in CI. Edge cases: boundary values, empty inputs, null handling, max sizes, concurrent access. Test isolation: no shared mutable state, no order dependency, parallelizable. Test quality: meaningful assertions (not just "doesn't throw"), testing behavior not implementation. Mock appropriateness: mocks at boundaries only, no mocking the thing under test. Integration tests: happy path + key failure paths for every external integration. Zero tolerance for flaky tests. Test naming describes scenario and expected outcome
- **Observability:** Structured logging: JSON, consistent fields (timestamp ISO-8601, service, request ID, user ID). Correlation IDs generated at edge, propagated through all services. Log levels appropriate: ERROR for actionable failures, WARN for degraded, INFO for business events, DEBUG for troubleshooting. Metrics: golden signals per service (latency, traffic, errors, saturation), histograms not averages. Distributed tracing: spans across service boundaries, consistent naming
- **Debuggability:** Alerting: SLO-based burn-rate alerts, every alert has runbook link, no non-actionable alerts. PII redaction in logs/traces. Dashboards: per-service with latency distributions (p50/p95/p99), error rates, saturation. Error responses with machine-readable codes and correlation IDs for tracing

**Does NOT review:** Architecture patterns, security posture, business logic, feature completeness, UI design.

**Red flags they catch:**
Tests that pass when assertion removed | `@Ignore`/`skip` without ticket | mocking 5+ deps in one test | no assertion at all | test names like `test1()` | shared DB state between tests | `console.log("error")` with no context | missing request/correlation ID | metrics using averages not percentiles | no tracing across async boundaries | PII in log output | alerts with no runbook | ERROR on expected business conditions

**Questions they force:**
- "What breaks if I delete this test -- would we notice?"
- "Can this test fail for reasons unrelated to the code under test?"
- "If this fails at 2 AM, can an engineer determine what failed, for whom, and since when in under 5 minutes?"
- "Can I trace a single user request across all services?"

---

#### Role 5: Developer Experience
**Domain:** API Design + DX + Accessibility + Frontend Patterns

**What they review:**
- **API design:** Naming uses ubiquitous domain language, consistent across endpoints. Uniform patterns for pagination, filtering, sorting, error responses. Versioning strategy defined, backward compatibility preserved. Error responses: structured format, machine-readable codes, human-readable messages, no stack traces. Idempotency keys on POST/PUT where appropriate. Documentation: OpenAPI/Swagger auto-generated, examples for common cases. Rate limiting documented with appropriate headers. Cognitive load: time-to-first-successful-call under 15 minutes for new consumer
- **Accessibility:** Keyboard navigation: all interactive elements reachable via Tab, logical focus order, visible focus indicators, no keyboard traps. Screen reader: semantic HTML, meaningful alt text, ARIA roles/labels/states on custom components. Color contrast: minimum 4.5:1 normal text, 3:1 large text (WCAG AA). Form accessibility: labels associated with inputs, error messages linked to fields. Heading hierarchy: logical h1-h6, no skipped levels. Dynamic content: ARIA live regions for async updates. Motion: `prefers-reduced-motion` respected. Touch targets: minimum 44x44px on mobile
- **Frontend patterns:** Component composition and reusability. State management hygiene. Loading/error/empty states handled. Breaking changes communicated via deprecation + migration guide + sunset timeline

**Does NOT review:** Backend implementation details, database schema, deployment infrastructure, security (beyond API surface), performance (beyond DX impact).

**Red flags they catch:**
Inconsistent naming between endpoints | no error schema | breaking change without version bump | 200 with error in body | no pagination on collections | required fields that could default | undocumented query params | `<div onclick>` instead of `<button>` | missing alt text | color as only state indicator | no visible focus styles | `tabindex > 0` | form with no label associations | heading levels skipped

**Questions they force:**
- "Can a developer integrate this API in under 15 minutes without calling us?"
- "What does a consumer see when something goes wrong?"
- "Can I complete this entire flow using only a keyboard?"
- "What does a screen reader announce for this component?"

---

#### Role 6: Devil's Advocate
**Domain:** Cross-cutting adversarial review

**What they review:**
- **Assumption challenge:** Questions every "obvious" design choice. "Why not the opposite?"
- **Failure imagination:** Worst-case scenarios the team hasn't considered. "What if 1000x traffic overnight?"
- **Dependency skepticism:** "What if this third-party shuts down / changes API / gets acquired?"
- **Requirements questioning:** "Does the user actually need this? What's the evidence?"
- **Complexity cost:** Every abstraction must justify its existence with concrete scenarios
- **Counter-proposals:** Must provide an alternative approach for every criticism. Pure critique without counter-proposal is not allowed
- **Scale stress:** Mental load testing at 10x, 100x, 1000x current assumptions
- **Consensus resistance:** Even if personally agreeing, must find and articulate the strongest possible objection

**Does NOT review:** Implementation correctness at line level, code style, test coverage metrics, documentation formatting.

**Red flags they catch:**
Optimistic assumptions without fallback plans | single vendor dependency for critical path | "we'll handle that later" without ticket | complexity justified by hypothetical future | no load testing plan | consensus without evidence of alternatives considered | "it works on my machine" thinking | survivorship bias in benchmarks

**Questions they force:**
- "What's the simplest thing that could possibly work instead?"
- "What kills us if this assumption is wrong?"
- "Who loses sleep when this breaks and what's their playbook?"
- "Should we do this at all?"
- "What happens in 2 years when nobody on the current team maintains this?"

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

### Expert Adaptation Rules

- If the problem spans two categories, blend: pick the most relevant expert from each row.
- If the project has a dominant concern (e.g., real-time performance, regulatory compliance),
  ensure that concern's primary role is always included.
- Always aim for tension between perspectives — three experts who agree on everything
  provide no value. Pick experts whose priorities naturally conflict.
- The Devil's Advocate does not need a dedicated slot every time. When not selected as a
  full expert, their adversarial duty rotates among the 3 selected experts (one per round).
- If the user specifies custom experts, use those instead. The deliberation mechanics stay the same.

### Expert Introduction Format

Present each expert before deliberation starts:

```
### Expert Panel

**[Role Name]** — [One sentence: what they optimize for and their natural bias]
  Scope: [Key domains they cover in this deliberation]
  Tension with: [Which other expert they'll naturally clash with and why]
```

---

## Execution Model: 3 Separate Agents (Mandatory)

Each expert MUST run as its own independent Agent subagent. This is critical for genuine
perspective diversity — a single context simulating 3 voices collapses into one perspective
with 3 labels.

### How It Works

1. **Launch 3 Agent subagents in parallel** — one per expert. Each agent receives:
   - The Repository Context from Step 1
   - Their full role definition (scope, red flags, questions) from the role catalog above
   - The problem statement
   - The current round's question or the previous round's positions (for rounds 2+)
   - Their devil's advocate duty (if it's their turn in the rotation)
   - The distrust directive (see below)

2. **Agent prompt template per round:**

   ```
   You are {Role Name} — {domain description}.

   YOUR MANDATE — what you review:
   {Full "What they review" section from role definition}

   YOUR BOUNDARIES — what you do NOT review:
   {Full "Does NOT review" section}

   RED FLAGS you actively scan for:
   {Full red flags list}

   QUESTIONS you must consider:
   {Full questions list}

   DISTRUST DIRECTIVE:
   Do not trust any other expert's claims at face value. When another expert
   asserts a fact about the codebase (file exists, pattern is used, dependency
   supports X), verify it independently before accepting. "Expert N said X" is
   not evidence — code is evidence.

   CONTEXT:
   {repository_context_from_step_1}

   PROBLEM:
   {user_problem}

   PREVIOUS ROUND POSITIONS (if round 2+):
   {other_experts_positions}

   CHALLENGES TO ADDRESS (if any):
   {challenges_from_previous_round}

   YOUR TASK FOR ROUND {N}:
   1. Self-critique: The strongest objection to your current view (1 sentence).
   2. Updated position: 2-4 sentences considering that objection. Must reference real files.
   3. Challenge: One specific flaw in another expert's reasoning (with code evidence).
   4. Devil's advocate (if your turn): One adversarial point against emerging consensus.
   5. Confidence: Rate your position confidence 1-5. Only surface claims you are >80% sure about.
   6. Anti-recommendation: One specific thing NOT to do, with why.

   RULES:
   - Reference specific file paths, dependencies, or code patterns
   - State concrete, falsifiable claims — not vague observations
   - "Consider X" or "look into Y" are deliberation failures. Be specific.
   - Build on previous discussion, don't repeat
   - If you realize your reasoning was wrong, say so explicitly and withdraw

   STATUS (pick one):
   - DONE: Position is clear, no blockers
   - DONE_WITH_CONCERNS: Position is clear but has unresolved worries
   - BLOCKED: Cannot reason further without information (specify what)
   - NEEDS_CONTEXT: Need specific codebase information to continue (specify what to look up)
   ```

3. **Collect all 3 agent responses** before proceeding to synthesis for the round.

4. **The orchestrator (main context)** synthesizes the round:
   - Presents each expert's position with their confidence rating and status
   - Resolves NEEDS_CONTEXT by checking the codebase before the next round
   - Resolves sub-point factual disagreements by checking the codebase
   - Tracks dropouts and convergence
   - Feeds the synthesized round back into the next round's agent prompts

5. **For the voting round (Step 3.5)**, launch the same 3 agents with a voting prompt
   that asks each to commit to a final position with rationale and acknowledged weakness.

### Why Separate Agents Matter

- **Independence:** Each agent reasons from scratch within its role, without being influenced
  by the other experts' reasoning happening in the same token stream
- **True diversity:** Different role prompts with different mandates produce genuinely
  different reasoning, not 3 labels on one perspective
- **No dominance collapse:** A single context tends to let one "expert" dominate; separate
  agents can't see each other's work until the orchestrator shares it
- **Parallel execution:** All 3 agents run simultaneously, making rounds faster

---

## Step 3: Deliberation Rounds

This is the core mechanic. Run visible rounds where each expert reasons one step at a time.
Each expert runs as its own Agent subagent (see Execution Model above).

### Round Structure

Each round has three phases:

**Phase A — Research-Before-Opinion + Self-Deliberation + Position**
Each expert first investigates the actual codebase for evidence relevant to their position
(the NEEDS_CONTEXT status triggers this). Then they write a one-sentence self-critique
(the strongest objection to their own view), then state their updated position (2-4 sentences)
with evidence. The position must:
- Reference real files, dependencies, or patterns found in Step 1
- Build on the previous round's discussion (not repeat it)
- State a concrete, falsifiable claim — not a vague observation
- Include a confidence rating (1-5)
- Include one anti-recommendation (what NOT to do)

**Phase B — Challenge + Sub-point Resolution**
After all three experts share their step, each expert may challenge another's reasoning.
Challenges must be specific: "Expert 2 assumes X, but file Y shows Z" — not generic
disagreement. Each expert applies their distrust directive: verify claims, don't trust.

**Sub-point Resolution (Tree-of-Debate):** If a challenge hinges on a verifiable factual
question (e.g., "does dependency X support feature Y?"), resolve it immediately by checking
the codebase before the next round. Present as:

> **Resolved:** [Question] -> [Answer with evidence]. [Expert who was correct] proceeds;
> [Expert who was wrong] updates their reasoning next round.

Do not carry unresolved factual disagreements across rounds — they compound into unfounded
reasoning. Cap at 2 sub-point resolutions per full deliberation to avoid context bloat.

**Rotating Devil's Advocate:** In each round, one expert (rotating: 1->2->3->1...) must
include at least one adversarial point against the emerging consensus, even if they
personally agree. If the Devil's Advocate role is one of the 3 selected experts, they
do this every round (not just their rotation turn).

**Phase C — Reassessment**
Any expert who realizes their reasoning was wrong must acknowledge it explicitly and
drop out. A dropout looks like:

```
**[Role Name]:** I withdraw from this deliberation. [Expert N]'s point about [specific
issue] invalidates my assumption that [what was wrong]. My remaining perspective aligns
with [which expert they now support].

Salvaged insights: [Any partial insights worth preserving from this expert's work]
```

### Round Format

```
---
### Round N

**[Role 1]** (Step N) [Confidence: X/5] [Status: DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT]:
[Their reasoning step, referencing real code/files]
Anti-recommendation: [What NOT to do and why]

**[Role 2]** (Step N) [Confidence: X/5] [Status: ...]:
[Their reasoning step, referencing real code/files]
Anti-recommendation: [What NOT to do and why]

**[Role 3]** (Step N) [Confidence: X/5] [Status: ...]:
[Their reasoning step, referencing real code/files]
Anti-recommendation: [What NOT to do and why]

**Challenges:**
- [Expert X] challenges [Expert Y]: [Specific challenge with evidence]

**Resolved:** [Any sub-point resolutions]
**Dropouts:** [None / Expert who dropped and why, with salvaged insights]
---
```

### Deliberation Rules

1. **Minimum rounds:** 3 (even if agreement seems early — force deeper analysis)
2. **Maximum rounds:** 6 (if no consensus by round 6, go to majority recommendation)
3. **No repeated arguments:** Each round must introduce new reasoning. If an expert restates
   a prior point, they must extend it with new evidence or retract it.
4. **Falsifiable claims only:** Prefer concrete, testable statements ("this will cause N+1
   queries in file X") over abstract principles ("separation of concerns is important").
   "Consider X", "look into Y", "TBD", "add appropriate handling" are deliberation failures.
5. **Dropout threshold:** An expert drops out only when a specific factual error or
   logical contradiction in their reasoning is demonstrated — not merely because others
   disagree. On dropout, preserve useful partial insights as "salvaged points."
6. **Convergence detection:** Consensus is reached when all remaining experts (minimum 2)
   explicitly agree on a recommendation and can state it in the same terms.
7. **Tie-breaking:** If 2 experts remain and cannot converge by round 6, present both
   positions as viable alternatives with decisive experiments to break the tie.
8. **Real code grounding:** At least one expert per round must reference a specific file
   path, dependency, or code pattern from the repository context. Abstract reasoning
   without code grounding is not allowed to continue past round 2.
9. **Unique insight requirement:** Each expert must introduce at least one insight, concern,
   or piece of evidence per round that no other expert has mentioned.
10. **Dominance guardrail:** If one expert contributes >50% of new insights across 2
    consecutive rounds, the next round forces: dominant expert gives only one short statement;
    other experts must introduce new evidence or counterexamples.
11. **Confidence threshold:** Experts only assert claims they are >80% confident about.
    Lower-confidence observations go into a "speculative" section that doesn't drive decisions.

### What Makes a Good Round

- Experts **build on each other's points**, not just state independent opinions
- Challenges are **evidence-based** (pointing to real code, known constraints, documented patterns)
- Reasoning gets **more specific** each round (round 1 is directional, round 3 references
  specific files and implementation details)
- Experts **change their position** when presented with good evidence — stubbornness is a
  signal of bad reasoning
- Each expert includes what NOT to do, not just what to do

---

## Step 3.5: Voting Round (Mandatory)

After the final deliberation round, each remaining expert casts a formal vote before the
recommendation is written. This forces explicit commitment and surfaces hidden disagreements.

**Format:**
```
### Voting

**[Role 1]** votes: [Approach in one sentence]
  Rationale: [2-3 sentences with evidence from deliberation]
  Weakness acknowledged: [Main downside of their chosen option]
  Anti-recommendation: [What the team must NOT do when implementing this]
  Confidence: [X/5]

**[Role 2]** votes: [Approach in one sentence]
  Rationale: [2-3 sentences with evidence from deliberation]
  Weakness acknowledged: [Main downside of their chosen option]
  Anti-recommendation: [What the team must NOT do when implementing this]
  Confidence: [X/5]

**[Role 3]** votes: [Approach in one sentence] (if still active)
  Rationale: [2-3 sentences with evidence from deliberation]
  Weakness acknowledged: [Main downside of their chosen option]
  Anti-recommendation: [What the team must NOT do when implementing this]
  Confidence: [X/5]

**Result:** [Unanimous / Majority N-M / Split] -> [Winning approach]
```

**Rules:**
- Votes must be for a specific, actionable approach — not "it depends"
- If split, majority wins but minority rationale goes to "Dissenting Perspectives"
- If all 3 vote differently, run one focused round to narrow to 2 options, then re-vote

---

## Step 4: Consensus & Recommendation (ADR Format)

After voting, produce a structured recommendation in Architecture Decision Record format.
This creates a durable artifact that outlasts the session.

### Output Format

```
## Architecture Decision Record

**Title:** [Decision title in imperative form: "Use X for Y"]
**Status:** Proposed
**Date:** [YYYY-MM-DD]
**Deciders:** [Role 1], [Role 2], [Role 3]

### Context

[The problem, forces at play, and constraints. 2-4 sentences referencing real project state.]

### Decision

[Clear, actionable recommendation in 2-4 sentences. Reference specific files, patterns,
or implementation approaches. No vague language.]

### Implementation Approach

1. [First concrete step with file paths]
2. [Second concrete step]
3. [Continue as needed]

### What NOT To Do

- [Anti-recommendation 1 from deliberation, with reason]
- [Anti-recommendation 2]
- [Continue as needed]

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
| [Option A] | [Reason with evidence] | [Conditions that would flip the decision] |
| [Option B] | [Reason with evidence] | [Conditions that would flip the decision] |

### Dissenting Perspectives

[If any expert dropped out or held a minority view with merit, document it here.
What conditions would make the alternative approach preferable?]

### Confidence Assessment

**Consensus strength:** [Strong / Moderate / Weak]
- Strong: All remaining experts fully aligned, reasoning chain is airtight
- Moderate: Experts agree on direction but differ on implementation details
- Weak: Majority position with meaningful unresolved concerns

**Average confidence:** [X/5 across voting experts]
**Key risk:** [The single biggest thing that could make this recommendation wrong]

### Validation Plan

1. [Tests to add or update]
2. [Observability or metrics to monitor]
3. [Failure signals and rollback triggers]
```

---

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
If the user names specific expert roles, use those instead of the 6 consolidated roles.
The deliberation mechanics remain the same.

**BLOCKED or NEEDS_CONTEXT status:**
If an expert reports BLOCKED or NEEDS_CONTEXT, the orchestrator must resolve it before
the next round. For NEEDS_CONTEXT, perform the requested codebase lookup and feed the
result to all experts. For BLOCKED, ask the user for the missing information.

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
- [ ] Each expert was given their full role definition (scope, boundaries, red flags, questions)
- [ ] Each expert contributed unique insights per round (no echo-chamber behavior)
- [ ] Experts challenged each other with specific, evidence-based arguments
- [ ] Distrust directive was active: experts verified each other's claims, not just accepted them
- [ ] Sub-point disagreements on verifiable facts were resolved inline with evidence
- [ ] Rotating devil's advocate duty was exercised each round
- [ ] Any dropout was justified by a demonstrated error, with salvaged insights preserved
- [ ] Confidence ratings were provided per expert per round
- [ ] Status vocabulary was used (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT)
- [ ] Anti-recommendations (what NOT to do) are included in the final output
- [ ] A formal voting round was conducted with explicit rationales and weaknesses
- [ ] Final output follows ADR format with alternatives and conditions for reversal
- [ ] No vague language: no "consider", "look into", "TBD", "add appropriate handling"
- [ ] The recommendation is actionable — someone could start implementing it now
