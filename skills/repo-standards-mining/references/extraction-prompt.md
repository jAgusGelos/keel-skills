# Extraction Prompt Template

Pass this prompt to `/cc-cc-powerful-iterations` (or single Claude subagent in `--quick` mode).
Replace `{N}`, `{X}`, `{TOTAL_BATCHES}`, and `{BATCH_DATA}` before use.

**IMPORTANT:** Tell cc-cc to skip or abbreviate prompt refinement — the data is already curated.
Do NOT modify the output format during prompt refinement.

---

You are a senior engineering consultant analyzing PR review comment summaries to extract
a team's implicit coding standards.

IMPORTANT: Do NOT modify the output format during prompt refinement. The downstream
aggregation pipeline depends on this exact JSON schema.

Read these PR review summaries from {N} merged PRs. Find PATTERNS — things reviewers
repeatedly care about, enforce, or reject.

## Output Format (STRICT — output valid JSON array)

```json
[
  {
    "pattern_key": "short-kebab-case-label",
    "category": "one of: architecture, naming, type-safety, error-handling, framework-patterns, structural-quality, data-integrity, security, performance, testing, documentation, dependency-management",
    "frequency": 3,
    "severity": "blocking | strong-preference | nice-to-have",
    "reviewers": ["bob", "carol"],
    "description": "1-2 sentences explaining what the team expects",
    "evidence": ["paraphrased example 1", "paraphrased example 2"],
    "suggested_rule": "Concise, actionable rule statement (1 sentence)",
    "detection_command": "bash/grep/lint command to detect violations, or null if not automatable"
  }
]
```

## Extraction Rules

- Only report patterns that appear in 2+ PRs (not one-off opinions)
- Distinguish between universal standards (3+ reviewers) and personal preferences (1 reviewer)
- Note which reviewers enforce which patterns by name
- Look for IMPLICIT standards — things reviewers flag without citing a written rule
- Pay attention to what gets REQUESTED FOR CHANGES vs what gets approved as-is
- If a pattern is detectable via a bash command, grep, or lint rule, provide the detection_command

## PR Review Summaries (Batch {X}/{TOTAL_BATCHES}):

{BATCH_DATA}
