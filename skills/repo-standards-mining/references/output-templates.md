# Output Templates

## Engineering Standards Document

Write to `$OUT_DIR/output/engineering-standards.md`:

```markdown
# Engineering Standards — {Repo Name}

> Auto-extracted from {N} merged PRs ({date range}).
> {M} review comments analyzed. {P} patterns identified.
> Mode: {full (cc-cc cross-validated) | quick (single-engine)}

## How This Was Generated

Mined from real PR review behavior — not aspirational guidelines,
but what your team actually enforces in code review.

**Confidence axes:**
- **Frequency:** low (<3 PRs) | medium (3-4) | high (5+)
- **Reviewer breadth:** single (1 reviewer) | few (2) | many (3+)
- **Engine agreement:** single | both (cc-cc cross-validated)

---

## Category: {category_name}

### {N}. {Pattern Title}
**Freq:** {N} PRs | **Reviewers:** {list} | **Classification:** {universal|strong-convention|personal-preference}
**Rule:** {suggested_rule}
**Evidence:** {paraphrased examples}
**Detection:** `{detection_command}` or "Manual review required"

---

## Summary

| Category | Patterns | High Freq | Multi-Reviewer | New (not in review-changes) |
|----------|----------|-----------|----------------|----------------------------|
| ...      | ...      | ...       | ...            | ...                        |

## Gap Analysis vs /review-changes

### New Patterns (not currently checked)
{list with promotion target recommendations}

### Partially Covered (could be strengthened)
{list with specific gaps}

### Already Covered
{count} patterns are already handled by the current checklist.
```

---

## Promotion Proposals

Write to `$OUT_DIR/output/promotion-proposals.md`:

```markdown
## Promotion Proposals

### Tier 1: Enforcement (lint/config)
{patterns with automatable detection_command → propose lint rule or CI check}

### Tier 2: Test Templates
{patterns about missing tests → propose test template or coverage rule}

### Tier 3: review-changes Checklist

#### For Agent 1 (Code Quality & Patterns):
**{next_number}. {pattern_key}** — {one-line description}
Detection: `{command}`

#### For Agent 2 (Security & Performance):
**{next_number}. {pattern_key}** — {one-line description}
Detection: `{command}`

### Tier 4: CLAUDE.md Conventions
{patterns that are repo-wide and cross-cutting → propose CLAUDE.md rule}

### Not Promoted
{personal-preference patterns or low-confidence → listed but not proposed}
```

---

## Summary Dashboard

Present after all analysis:

```
=== Repo Standards Mining Complete ===

Repository:      {OWNER/REPO}
Tech stack:      {detected}
PRs analyzed:    {N}
Comments:        {TOTAL} total, {FILTERED} substantive
Batches run:     {B} ({mode: cc-cc | quick})
Patterns found:  {P} total
  - Universal:       {U} (3+ reviewers)
  - Strong convention: {S} (2 reviewers)
  - Personal pref:   {PP} (1 reviewer, not promoted)

Gap analysis vs /review-changes:
  - New:              {N} (not currently checked)
  - Partially covered: {PC} (could be strengthened)
  - Already covered:  {A} (no action needed)

Promotion proposals:
  - Lint/config:      {L}
  - Test templates:   {T}
  - review-changes:   {R}
  - CLAUDE.md:        {C}

Output files:
  - Standards doc:       $OUT_DIR/output/engineering-standards.md
  - Promotion proposals: $OUT_DIR/output/promotion-proposals.md
  - Unified patterns:    $OUT_DIR/analysis/unified-patterns.json
  - Gap analysis:        $OUT_DIR/analysis/gap-analysis.md
```
