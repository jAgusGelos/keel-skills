#!/usr/bin/env bash
# fetch-and-filter.sh — Environment detection, PR fetch, and comment filtering
# Called by repo-standards-mining skill (Steps 0-3)
#
# Usage: bash scripts/fetch-and-filter.sh [PR_COUNT] [--since YYYY-MM-DD]
#
# Outputs:
#   $OUT_DIR/raw/prs-metadata.json       — PR metadata
#   $OUT_DIR/raw/inline-{N}.json         — Inline review comments per PR
#   $OUT_DIR/raw/reviews-{N}.json        — Review objects per PR
#   $OUT_DIR/raw/discussion-{N}.json     — Discussion comments per PR
#   $OUT_DIR/raw/filtered-comments.json  — All substantive comments after filtering

set -euo pipefail

# --- Platform Detection ---
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if ! echo "$REMOTE_URL" | grep -qi "github"; then
  echo "ERROR: Only GitHub is currently supported. GitLab support is planned."
  echo "Detected remote: $REMOTE_URL"
  exit 1
fi

# --- Preflight Checks ---
if ! command -v gh &>/dev/null; then
  echo "ERROR: gh CLI not found. Install it: https://cli.github.com/"
  exit 1
fi
if ! gh auth status &>/dev/null; then
  echo "ERROR: gh CLI not authenticated. Run: gh auth login"
  exit 1
fi
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq not found. Install it: https://jqlang.github.io/jq/"
  exit 1
fi

# --- Repo Info ---
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name -q .name)

# --- Tech Stack Detection ---
TECH_STACK=""
if [ -f "package.json" ]; then
  TECH_STACK="$TECH_STACK,javascript"
  grep -q '"react"' package.json 2>/dev/null && TECH_STACK="$TECH_STACK,react"
  grep -q '"next"' package.json 2>/dev/null && TECH_STACK="$TECH_STACK,nextjs"
  grep -q '"typescript"' package.json 2>/dev/null && TECH_STACK="$TECH_STACK,typescript"
fi
[ -f "go.mod" ] && TECH_STACK="$TECH_STACK,go"
[ -f "Cargo.toml" ] && TECH_STACK="$TECH_STACK,rust"
{ [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; } && TECH_STACK="$TECH_STACK,python"
TECH_STACK="${TECH_STACK#,}"  # trim leading comma

# --- Output Directory ---
OUT_DIR=".workspace/repo-standards-mining"
mkdir -p "$OUT_DIR/raw" "$OUT_DIR/batches" "$OUT_DIR/analysis" "$OUT_DIR/output"

# --- Parse Arguments ---
PR_COUNT="${1:-200}"
SINCE_FILTER=""
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --since) SINCE_FILTER="--search merged:>$2"; shift 2 ;;
    *) shift ;;
  esac
done

# --- Report Environment ---
echo "Platform: GitHub ($OWNER/$REPO)"
echo "Tech stack: ${TECH_STACK:-none detected}"
echo "Output: $OUT_DIR/"

# --- Confirmation: Count Available PRs ---
PR_AVAILABLE=$(gh api "search/issues?q=repo:$OWNER/$REPO+is:pr+is:merged&per_page=1" -q '.total_count' 2>/dev/null || echo "$PR_COUNT")
if [ "$PR_AVAILABLE" -lt "$PR_COUNT" ]; then
  PR_COUNT=$PR_AVAILABLE
fi
echo ""
echo "PRs available: $PR_AVAILABLE merged"
echo "PRs to fetch:  $PR_COUNT"
echo ""

# --- Bulk Fetch ---
gh pr list --state merged --limit "$PR_COUNT" $SINCE_FILTER \
  --json number,title,author,files,reviewDecision,additions,deletions,mergedAt \
  > "$OUT_DIR/raw/prs-metadata.json"

ACTUAL_COUNT=$(jq 'length' "$OUT_DIR/raw/prs-metadata.json")
API_CALLS=1
FETCH_ERRORS=0

echo "Fetching review data for $ACTUAL_COUNT PRs..."

jq -r '.[].number' "$OUT_DIR/raw/prs-metadata.json" | while read -r PR_NUM; do
  # Inline review comments
  if ! gh api "repos/$OWNER/$REPO/pulls/$PR_NUM/comments" --paginate \
    > "$OUT_DIR/raw/inline-$PR_NUM.json" 2>/dev/null; then
    FETCH_ERRORS=$((FETCH_ERRORS + 1))
  fi
  API_CALLS=$((API_CALLS + 1))

  # Review objects
  if ! gh api "repos/$OWNER/$REPO/pulls/$PR_NUM/reviews" --paginate \
    > "$OUT_DIR/raw/reviews-$PR_NUM.json" 2>/dev/null; then
    FETCH_ERRORS=$((FETCH_ERRORS + 1))
  fi
  API_CALLS=$((API_CALLS + 1))

  # Discussion comments
  if ! gh api "repos/$OWNER/$REPO/issues/$PR_NUM/comments" --paginate \
    > "$OUT_DIR/raw/discussion-$PR_NUM.json" 2>/dev/null; then
    FETCH_ERRORS=$((FETCH_ERRORS + 1))
  fi
  API_CALLS=$((API_CALLS + 1))

  # Progress
  if [ $((API_CALLS % 75)) -lt 4 ]; then
    echo "  ...${API_CALLS} API calls so far"
  fi

  # Circuit breaker
  if [ "$API_CALLS" -gt 3500 ]; then
    echo "WARNING: Approaching GitHub rate limit (${API_CALLS} calls). Stopping fetch."
    break
  fi
done

echo "Fetch complete: $ACTUAL_COUNT PRs, ~$API_CALLS API calls, $FETCH_ERRORS errors."

if [ "$FETCH_ERRORS" -gt 0 ]; then
  ERROR_PCT=$((FETCH_ERRORS * 100 / ACTUAL_COUNT))
  if [ "$ERROR_PCT" -gt 20 ]; then
    echo "WARNING: ${ERROR_PCT}% of PRs had fetch errors. Data quality may be affected."
  fi
fi

# --- Pre-filter Comments ---
# Bot authors to exclude (case-insensitive match)
BOT_AUTHORS="dependabot|renovate|codecov|sonarcloud|github-actions|vercel|netlify|snyk|greenkeeper|semantic-release|allcontributors|mergify|kodiakhq|stale"

# Approval-only patterns to exclude
APPROVAL_REGEX="^(LGTM|Approved|:shipit:|Looks good|Ship it)\\s*$"

# CI/bot boilerplate prefixes to exclude
BOILERPLATE_REGEX="^(Coverage|Build|Deploy|Test|Pipeline|Merged)"

echo "Filtering comments..."
echo "  Bot authors excluded: $BOT_AUTHORS"
echo "  Min comment length: 15 chars"

# The calling agent should use these rules to build filtered-comments.json:
# 1. Merge all inline-*.json, reviews-*.json, discussion-*.json into unified format
# 2. Apply BOT_AUTHORS, APPROVAL_REGEX, BOILERPLATE_REGEX, and length filters
# 3. Write result to $OUT_DIR/raw/filtered-comments.json

echo ""
echo "Environment ready. Agent should now:"
echo "  1. Merge raw comment files into unified format"
echo "  2. Apply filters (bots, approvals, boilerplate, length)"
echo "  3. Write $OUT_DIR/raw/filtered-comments.json"
echo "  4. Report: {filtered} of {total} comments are substantive"
