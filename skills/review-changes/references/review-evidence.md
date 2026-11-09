# Review evidence file (FULL review)

Before a FULL review, the reviewing session writes `.workspace/ctx/review/review-evidence.md`. Codex (and its
Claude fallback) verify this file instead of running whole suites themselves: whole-suite runs inside Codex hit
its timeout (exit 124) and burn its quota.

## Contract

```markdown
# Review evidence
- head: <output of `git rev-parse HEAD`>
- tree: <tree value from `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/codex/evidence.py fingerprint`>
- base: <base ref and sha>
- reviewed-baseline: <sha of the last reviewed commit, or "none">

## Validators and tests
| Command | Exit | Output tail (last ~10 lines) |
|---|---|---|
| <exact command> | 0 | ... |

## Scenarios
| Scenario (from plan/issue) | Command or steps | Observed output | Correct? |
|---|---|---|---|

## Not run
- <validator or scenario>: <why: needs credentials, paid call over cap, no runnable surface, ...>
```

Rules:
- `head` and `tree` come from `evidence.py fingerprint` run right after the last command in the file.
- Commands are the repo's own validators (build, typecheck, lint, test, spec validators, migration checks) plus
  the scenario commands the plan declares. Record real exit codes; never paste a green result you did not run.
- **Staleness:** before dispatching the reviewers, and again after every fix applied during the review (Step 6
  of review-changes, or a plandimp fix loop), run `evidence.py check .workspace/ctx/review/review-evidence.md`.
  Exit 6 means the evidence is stale: re-run the commands and rewrite the file before any further review pass.
- The file lives under `.workspace/`, which the fingerprint excludes, so writing it never makes it stale.
