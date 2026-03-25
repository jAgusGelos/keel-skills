---
name: repo-standards-mining
description: |
  Reverse-engineer a team's real engineering standards from merged PR review history.
  Fetches up to 200 PRs, extracts recurring review patterns via /cc-cc-powerful-iterations,
  and proposes improvements through pr-learning's promotion ladder (lint > test > skill >
  CLAUDE.md). The fastest way to bootstrap review standards for any codebase. GitHub only.
  Use when: "mine standards", "extract best practices", "learn from PRs", "repo standards",
  "engineering standards", "analyze PR history", "what patterns does this team follow",
  "build coding guidelines", "bootstrap review rules", "what do reviewers care about",
  "reverse-engineer coding style", "audit review quality", "what does this team enforce",
  "unwritten rules", "review patterns", "coding standards from PRs", "infer team conventions".
version: 1.0.0
category: development
depends: [cc-cc-powerful-iterations, pr-learning, review-changes]
---

# Repo Standards Mining

Collect merged PR review data. Extract recurring patterns. Propose durable improvements
via pr-learning's promotion ladder. GitHub only — abort on non-GitHub remotes.

## The Flow

```
[0] Detect environment, parse arguments
[1] Confirm with user (PR count, time estimate)
[2] Fetch PRs + comments (scripts/fetch-and-filter.sh)
[3] Filter noise (deterministic bot/approval/length rules)
[4] Summarize each PR (map phase — control token budget)
[5] Chunk into batches of ~20 PR summaries
[6] Per batch: isolated subagent → /cc-cc-powerful-iterations
[7] Aggregate across batches (deduplicate, rank, classify)
[8] Write patterns to pr-learning pattern-log
[9] Gap analysis vs /review-changes checklist
[10] Generate standards doc + promotion proposals
[11] Interactive approval → apply adopted changes
```

## Arguments

| Flag | Default | Effect |
|---|---|---|
| `<number>` | 200 | PR count. Passed to `scripts/fetch-and-filter.sh`. |
| `--since YYYY-MM-DD` | (none) | Filter PRs merged after date. |
| `--category <cat>` | (all) | Drop patterns outside this category in Step 7. |
| `--quick` | off | Skip cc-cc. Single Claude subagent per batch. ~5-10 min. |
| `--diff-previous` | off | Compare against last run's `unified-patterns.json`. |

## Step 0-3: Environment Detection, Fetch, Filter

Run `scripts/fetch-and-filter.sh` with parsed arguments. The script handles:
- Platform detection (GitHub only), repo info, tech stack detection
- Preflight checks (gh CLI installed and authenticated, jq available)
- Confirmation gate with PR count and time estimate
- Bulk fetch of PR metadata, inline comments, reviews, and discussion comments
- Circuit breaker at 3500 API calls

After the script completes, merge raw comment files into unified format and apply
deterministic filters:
- Exclude bot authors (`dependabot|renovate|codecov|sonarcloud|github-actions|vercel|netlify|snyk|greenkeeper|semantic-release|allcontributors|mergify|kodiakhq|stale`)
- Exclude approval-only messages (`LGTM`, `Approved`, `Looks good`, `Ship it`)
- Exclude comments shorter than 15 characters
- Exclude CI boilerplate (`Coverage...`, `Build...`, `Deploy...`, `Pipeline...`)

Write result to `$OUT_DIR/raw/filtered-comments.json`.

Report: `{filtered} of {total} comments are substantive review feedback.`
If < 50 substantive comments, confirm with user before continuing.
If > 20% fetch errors, warn about data quality.

## Step 4: Summarize Each PR

Do NOT pass raw comments to cc-cc. Summarize each PR into a compact digest first.

Per-PR summary format:
```json
{
  "pr": 123, "title": "Add user auth", "author": "alice",
  "reviewers": ["bob", "carol"], "decision": "approved",
  "files": ["src/auth.ts"], "additions": 150, "deletions": 30,
  "comment_count": 8,
  "summary_bullets": [
    "bob requested error handling for token expiry edge case",
    "carol flagged missing input validation on email field"
  ]
}
```

Rules:
- Max 5 bullets per PR. Prioritize: changes_requested > inline > discussion.
- Format: `"{reviewer} {verb} {what}"` — max 120 chars each.
- Preserve reviewer names (enables reviewer-breadth analysis downstream).
- Drop pure positive feedback.

Write to `$OUT_DIR/analysis/pr-summaries.json`. Each summary is ~200 tokens.

## Step 5: Chunk into Batches

Split PR summaries into batches of ~20 each:
- Up to 100 PRs: 5 batches
- 100-200 PRs: up to 10 batches
- Minimum batch size: 10 (merge undersized remainder into last batch)

Write each to `$OUT_DIR/batches/batch-{N}.json`.

A batch of 20 summaries ≈ 4K tokens + 1.5K prompt = ~6K total. Safe for all models.

## Step 6: Per-Batch Analysis

**Spawn each batch in an isolated subagent** to prevent context accumulation.

For each batch:

1. Spawn a Claude subagent: "Read `$OUT_DIR/batches/batch-{N}.json` and invoke
   `/cc-cc-powerful-iterations` with the prompt from `references/extraction-prompt.md`.
   Write output to `$OUT_DIR/analysis/batch-{N}-patterns.json`.
   Tell cc-cc to skip or abbreviate prompt refinement — data is already curated."

2. Use the locked-format extraction prompt from `references/extraction-prompt.md`.
   Categories must come from `references/taxonomy.md`.

3. Verify output is valid JSON. If malformed, retry once requesting JSON-only output.

4. Write checkpoint: `{"batch": N, "status": "complete", "patterns_found": P, "timestamp": "ISO"}`.
   Append to `$OUT_DIR/checkpoint.json`.

Report after each batch: `Batch {N}/{TOTAL} complete. {P} patterns found. ({elapsed})`

### Quick Mode (`--quick`)

Replace cc-cc with a single Claude subagent per batch. Same extraction prompt and locked
JSON format. Tag all patterns with `"engine_agreement": "single"`.

### Resume

Read `$OUT_DIR/checkpoint.json` before starting. Skip completed batches.

## Step 7: Cross-Batch Aggregation

1. Parse all `batch-{N}-patterns.json` files (valid JSON enforced by locked format).
2. Deduplicate by `pattern_key`: sum frequencies, union reviewers, keep longest description,
   keep any non-null `detection_command`.
3. Rank by total frequency (descending).
4. Filter: keep patterns with frequency >= 3 PRs, OR flagged by both engines in 2+ batches.
   Apply `--category` filter if set.
5. Classify each pattern:
   - `universal` — 3+ different reviewers
   - `strong-convention` — 2 reviewers consistently
   - `personal-preference` — 1 reviewer only
6. Score confidence on three axes:
   - `frequency_confidence`: low (<3) | medium (3-4) | high (5+)
   - `reviewer_breadth`: single (1) | few (2) | many (3+)
   - `engine_agreement`: single | both

### Unified patterns schema

```json
{
  "pattern_key": "string",
  "category": "string (from taxonomy)",
  "frequency": 5,
  "severity": "blocking | strong-preference | nice-to-have",
  "reviewers": ["alice", "bob", "carol"],
  "description": "string",
  "evidence": ["string"],
  "suggested_rule": "string",
  "detection_command": "string | null",
  "classification": "universal | strong-convention | personal-preference",
  "frequency_confidence": "low | medium | high",
  "reviewer_breadth": "single | few | many",
  "engine_agreement": "single | both",
  "status": "NEW_PATTERN | KNOWN_PATTERN"
}
```

### Cross-reference with pr-learning

Read `.workspace/pr-learning/pattern-log.md` if it exists. Tag matching `pattern_key`
entries as `KNOWN_PATTERN`, others as `NEW_PATTERN`.

Write to `$OUT_DIR/analysis/unified-patterns.json`.

### Diff Against Previous Run (`--diff-previous`)

If active and previous `unified-patterns.json` exists, tag each pattern as
`ADDED`, `REMOVED`, `CHANGED`, or `STABLE`. Write `$OUT_DIR/analysis/delta-report.md`.

## Step 8: Write to pr-learning Pattern Log

Write all `NEW_PATTERN` entries to `.workspace/pr-learning/pattern-log.md` using
pr-learning's format:

```markdown
### {pattern_key}
- Source: repo-standards-mining ({date})
- Source PRs: #{list}
- Category: {from taxonomy}
- Scope: repo-wide
- Why it matters: {description}
- Promotion target: {determined in Step 10}
- Confidence: {frequency_confidence}
```

This closes the bidirectional loop with `/pr-learning`.

## Step 9: Gap Analysis

### Parse review-changes checklist

In `.claude/skills/review-changes/SKILL.md`:
- **Agent 1:** Numbered lines under first `## Your Checklist (N points)`. Extract via `^\d+\.\s+(.+)$`.
- **Agent 2:** Same pattern, second occurrence.

If format doesn't match, warn user and skip gap analysis rather than producing bad mappings.

### Tag each mined pattern

- `ALREADY_COVERED` — existing item substantially handles this
- `PARTIALLY_COVERED` — similar item exists, doesn't fully match
- `NEW` — not in current checklist

Use `references/taxonomy.md` agent-mapping to assign NEW patterns to Agent 1 or Agent 2.

Write to `$OUT_DIR/analysis/gap-analysis.md`.

## Step 10: Standards Document + Promotion Proposals

### Standards document

Use template from `references/output-templates.md`. Write to `$OUT_DIR/output/engineering-standards.md`.
Fill every section only with evidence-backed standards. Omit empty sections.

### Promotion proposals

Use pr-learning's promotion ladder — choose the **narrowest durable home**:

1. **Lint/config rule** — if `detection_command` is automatable
2. **Test template** — if pattern is about missing tests
3. **review-changes checklist** — add to Agent 1 or Agent 2 per taxonomy mapping
4. **CLAUDE.md convention** — if many skills should inherit this rule

Use template from `references/output-templates.md`. Write to `$OUT_DIR/output/promotion-proposals.md`.

### Summary dashboard

Use dashboard template from `references/output-templates.md`. Present to user.

## Step 11: Interactive Approval

### Propose adoption

For each HIGH frequency + multi-reviewer pattern with a promotion target:

```
Pattern: {pattern_key}
Rule: "{suggested_rule}"
Evidence: found in {N} PRs, enforced by {reviewers}
Promotion: {tier} — {specific target}
Detection: {command or "manual"}

→ Adopt? (y/n/edit)
```

Wait for user response. Collect all decisions.

### Apply approved changes

- **Tier 1 (lint/config):** Create or edit the relevant config file. If unclear which, ask.
- **Tier 3 (review-changes):** Edit SKILL.md, add checklist item, increment point count.
- **Tier 4 (CLAUDE.md):** Append concise rule (1-2 lines).
- **Standalone doc:** Ask user where to save (default: `docs/`).

### Commit

Stage only modified config files. Do NOT stage `.workspace/`.

```bash
# Only commit if there are staged changes
if ! git diff --cached --quiet; then
  git commit -m "chore: add engineering standards from PR mining ({N} patterns adopted)"
fi
```
