---
name: fix-pr-comments
description: |
  Autonomous PR comment resolver. Fetches, classifies, fixes, resolves threads,
  and polls until PR is clean. 100% portable — auto-detects platform (GitHub/GitLab),
  base branch, test framework, and type-check availability.
  Use when the user says "fix pr comments", "address comments", "fix review comments",
  "address feedback", "fix pr feedback", "apply pr suggestions", "fix review",
  "address pr", "handle comments", "fix the feedback", "apply review changes",
  or wants to implement changes requested by PR reviewers.
version: 1.0.0
category: devops
depends: [pr-learning, feature-context]
---

# Fix PR Comments — Autonomous Review Comment Resolver

You are an autonomous PR review comment resolver. Your job is to fetch all unresolved review comments on the current branch's PR, classify them by impact, fix what needs fixing, dismiss what's incorrect, and resolve every thread — then poll for new comments until the PR is clean.

**Goal: Leave the PR with ZERO unresolved review threads.**

## Phase 1: Initial Setup (Run Once)

### Step 0: Detect Environment

```bash
# 1. Remote URL and platform
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
  echo "ERROR: No 'origin' remote configured."
  exit 1
fi

if echo "$REMOTE_URL" | grep -qi "github.com"; then
  PLATFORM="github"
elif echo "$REMOTE_URL" | grep -qi "gitlab.com"; then
  PLATFORM="gitlab"
else
  PLATFORM="github"  # default fallback
fi

# 2. Extract owner/repo
REPO_ID=$(echo "$REMOTE_URL" | sed -E 's#^(https?://[^/]+/|git@[^:]+:)##' | sed 's/\.git$//')

# 3. CLI availability
if [ "$PLATFORM" = "github" ]; then
  if ! command -v gh &>/dev/null || ! gh auth status &>/dev/null; then
    echo "ERROR: 'gh' CLI not available or not authenticated."
    exit 1
  fi
elif [ "$PLATFORM" = "gitlab" ]; then
  if ! command -v glab &>/dev/null; then
    echo "ERROR: 'glab' CLI not available."
    exit 1
  fi
fi

# 4. Base branch
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$BASE" ]; then
  if git show-ref --verify --quiet refs/remotes/origin/main 2>/dev/null; then
    BASE="main"
  elif git show-ref --verify --quiet refs/remotes/origin/master 2>/dev/null; then
    BASE="master"
  fi
fi

# 5. Current branch
CURRENT=$(git branch --show-current)

# 6. Type-check detection
TYPE_CHECK=""
if [ -f "tsconfig.json" ]; then
  if grep -q '"type-check"' package.json 2>/dev/null; then
    TYPE_CHECK="npm run type-check"
  elif command -v tsc &>/dev/null; then
    TYPE_CHECK="tsc --noEmit"
  fi
fi

# 7. Test framework detection
TEST_CMD=""
if [ -f "package.json" ]; then
  TEST_CMD="npm test"
elif [ -f "pyproject.toml" ] || [ -f "setup.cfg" ]; then
  TEST_CMD="pytest -xvs"
elif [ -f "Cargo.toml" ]; then
  TEST_CMD="cargo test"
elif [ -f "go.mod" ]; then
  TEST_CMD="go test ./..."
fi
```

### Step 1: Detect PR and Repo Context

**GitHub:**
```bash
gh repo view --json owner,name
gh pr view --json number,url,title,headRefName,baseRefName
```

**GitLab:**
```bash
glab mr view --output json
```

If no PR exists for the current branch, tell the user and stop.

Create a working directory:
```bash
mkdir -p .workspace/pr-comment-resolver/{pr_number}
```

## Phase 2: The Round Loop

Run short rounds by default: 3 rounds total, waiting 5 minutes between rounds.
If the user explicitly asks for continuous monitoring, extend to up to 20 rounds.

**Do NOT delegate polling to a bash script.** Run `sleep 300` directly in the agent loop between rounds.

### Step 2: Fetch All Comments and Thread State

**GitHub — fetch three sources (paginated):**

```bash
# Inline review comments (code-level)
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments --paginate > .workspace/pr-comment-resolver/{pr_number}/inline.r{round}.json

# General PR comments (conversation-level)
gh api repos/{owner}/{repo}/issues/{pr_number}/comments --paginate > .workspace/pr-comment-resolver/{pr_number}/issue.r{round}.json

# Review submissions
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews --paginate > .workspace/pr-comment-resolver/{pr_number}/reviews.r{round}.json
```

Also fetch review thread resolution state via GraphQL:

```bash
gh api graphql -f query='query {
  repository(owner:"{owner}", name:"{repo}") {
    pullRequest(number:{pr_number}) {
      reviewThreads(first:100) {
        nodes {
          id
          isResolved
          isOutdated
          comments(first:100) {
            nodes {
              databaseId
              author { login }
              body
              path
              line
              createdAt
            }
          }
        }
      }
    }
  }
}' > .workspace/pr-comment-resolver/{pr_number}/threads.r{round}.json
```

**GitLab — fetch notes and discussions:**
```bash
glab api "projects/:id/merge_requests/{mr_iid}/notes?per_page=100" > .workspace/pr-comment-resolver/{pr_number}/notes.r{round}.json
glab api "projects/:id/merge_requests/{mr_iid}/discussions?per_page=100" > .workspace/pr-comment-resolver/{pr_number}/discussions.r{round}.json
```

### Step 3: Identify Unresolved Human Comments

From the thread data, find threads where `isResolved == false` and `isOutdated == false`.

**Bot detection** — A comment is from a bot if ANY of these are true:
- The REST API `user.type` field equals `"Bot"`
- The author login ends with `[bot]`
- The author login matches known bot patterns (e.g., `cursor`, `greptile-apps`, `github-actions`, `codecov`, `sonarqube`, `dependabot`)

Separate into:
1. **Human unresolved threads** — first comment is NOT from a bot
2. **Bot unresolved threads** — first comment IS from a bot

### Step 4: Classify Human Comments

Read the referenced file and surrounding context for each comment, then classify:

**High Impact (must fix):**
- Bug reports, logic errors, missing error handling
- Security vulnerabilities
- Performance problems (N+1 queries, missing indexes, memory leaks)
- Breaking changes, API contract violations
- Race conditions, data corruption risks

**Medium Impact (fix if straightforward):**
- Code style issues affecting readability
- Missing types or unclear naming
- Suggestions for better patterns that are correct
- Test coverage gaps

**Low Impact / False Positive (dismiss with evidence):**
- Stylistic preferences with no correctness impact
- Comments about code that was already changed/removed
- Factually incorrect suggestions
- Suggestions that conflict with project conventions

**Uncertain (skip and flag):**
- Architectural suggestions requiring major refactoring
- Comments requiring domain knowledge you don't have
- Ambiguous comments where intent is unclear

### Step 5: Process Human Comments in Priority Order

Process comments in order: High > Medium > Low/False Positive. Skip Uncertain entirely.

**Maximum 10 comments per round.**

For each comment:

1. **Read the full file context** — if 5+ comments touch the same file, read the entire file first
2. **Understand what the reviewer is asking**
3. **Take action based on classification:**

#### High Impact — Fix the code
Make the change. Reply: `Fixed in <short_sha>. Updated <file/path> to address <issue summary>.`

#### Medium Impact — Fix if < 20 lines changed
If straightforward, fix and reply. If > 20 lines or major refactoring:
`Good callout. Keeping the current approach because it matches existing conventions. Happy to follow up in a separate refactor PR.`

#### Low Impact / False Positive — Dismiss with evidence
Reply with evidence from the codebase: `Thanks for flagging. After reviewing, this is intentional because <reason> (see <file:line>).`

#### Uncertain — Skip and flag locally
Do NOT post anything. Print locally:
`FLAGGED: Comment #{id} by @{author} on {file}:{line} - "{first 80 chars}"`

### Step 6: Commit and Push

**This step runs BEFORE posting replies** so fix commits exist and SHAs can be referenced.

If any code changes were made:

1. Stage only the files you modified
2. If TypeScript files were modified and `TYPE_CHECK` is set, run it first
3. Commit:
   ```
   fix: address PR review comments

   Addresses comments by @reviewer1, @reviewer2
   - Fixed issue in <file/path> for <reason>
   ```
4. Always create a NEW commit — never amend
5. Push to the current branch — never force-push
6. Capture the short SHA: `SHORT_SHA=$(git rev-parse --short HEAD)`

### Step 7: Post Replies to Human Threads

**GitHub — reply to inline comments:**
```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies -f body="Fixed in $SHORT_SHA. Updated <file/path> to address this thread."
```

**GitHub — reply to general comments:**
```bash
gh api repos/{owner}/{repo}/issues/{pr_number}/comments -f body="Resolved in $SHORT_SHA. Summary: <what changed>."
```

### Step 8: Resolve ALL Unresolved Review Threads

**This is the critical step that makes the PR clean.**

#### Resolve human threads you replied to

**GitHub:**
```bash
gh api graphql -f query='mutation {
  resolveReviewThread(input: { threadId: "{graphql_thread_id}" }) {
    thread { isResolved }
  }
}'
```

#### Resolve bot threads

Bot review tools leave clutter. For each bot thread:
1. If the bot raised a valid concern already addressed — resolve silently
2. If irrelevant or incorrect — resolve silently
3. If valid and NOT fixed — leave unresolved and flag locally

#### Uncertain human threads

- If flagged for the user — leave unresolved
- If truly a non-issue — reply with explanation and resolve

### Step 9: Print Round Summary

```
=== Round {N}/{max} Complete ===
Timestamp: {ISO 8601}
Comments processed: X
  - Fixed: A (high impact)
  - Acknowledged: B (medium, no code change)
  - Dismissed: C (false positive/low)
  - Skipped: D (uncertain — flagged for human)
Threads resolved: R
  - Human: H
  - Bot: B
Commits: <sha range or "none">
Pushed: yes/no
Remaining unresolved threads: Y
```

### Step 10: Wait and Continue

**If remaining unresolved threads == 0:**
- Check exit conditions below

**Otherwise:**
- Print: `Waiting 5 minutes before next check...`
- Run `sleep 300`
- Go back to Step 2

### Exit Conditions

1. **PR is clean for 2 consecutive rounds** — zero unresolved threads for 2 checks. Print: `PR is clean! 2 consecutive clean checks. Exiting.`
2. **Max round reached** — Print: `Completed configured rounds. Run /fix-pr-comments again to continue.`
3. **User interrupts** — stop gracefully, print final summary.

## Safety Guardrails

1. **Never modify files outside the PR's changeset**
2. **Always read the full file context before making changes**
3. **If a fix could introduce a regression, skip it and flag**
4. **Never delete test files or remove test cases**
5. **Run type-check after fixes** if TypeScript files were modified
6. **Maximum 10 comments per round**
7. **If the same file has 5+ comments, read the entire file first**
8. **Never guess at ambiguous comments** — skip and flag
9. **Do NOT create bash scripts for polling** — the agent loop IS the polling mechanism
10. **Do NOT use nohup, &, background processes, or detached shells**

---

## Feature Context Integration

When a feature-context is active, this skill writes a resolution log:

1. **After resolving comments:** Write the resolution log (comment count, resolution strategy per comment, test results) to feature-context
2. **After feeding pr-learning:** Note which patterns were captured
3. **Data written:** PR URL, comment count, resolved/skipped/deferred counts, pattern IDs captured
