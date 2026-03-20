---
name: create-pr
description: |
  Create a pull/merge request from the current branch with auto-detected platform,
  proper formatting, and contextual summary. 100% portable — works on GitHub, GitLab,
  and Bitbucket without hardcoded repo names, branch names, or usernames.
  Use when the user says "create pr", "open pr", "pull request", "submit pr",
  "create merge request", "open mr", "pr create", "push and pr", "open a pull request",
  "send pr", "make a pr", or wants to submit their current branch for review.
version: 1.0.0
category: devops
depends: [feature-context]
---

# Create PR — Portable Pull/Merge Request Creator

Creates a well-formatted pull/merge request from the current branch. Auto-detects the
git platform, base branch, and CLI tool — works identically on GitHub, GitLab, and
Bitbucket without any hardcoded values.

## Portability

Everything is auto-detected at runtime:

- **Base branch** — detected from `refs/remotes/origin/HEAD`, falls back to checking `main`/`master`
- **Remote platform** — parsed from `git remote get-url origin` (GitHub, GitLab, Bitbucket, self-hosted)
- **CLI tool** — `gh` for GitHub, `glab` for GitLab, API fallback for Bitbucket
- **Repo identifier** — extracted from remote URL (supports HTTPS and SSH formats)
- **Current branch** — `git branch --show-current`

No values are ever hardcoded.

## Step 0: Detect Environment

Run these commands and store the results for all subsequent steps:

```bash
# 1. Base branch detection
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$BASE" ]; then
  git fetch origin 2>/dev/null
  BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
fi
if [ -z "$BASE" ]; then
  if git show-ref --verify --quiet refs/remotes/origin/main 2>/dev/null; then
    BASE="main"
  elif git show-ref --verify --quiet refs/remotes/origin/master 2>/dev/null; then
    BASE="master"
  else
    echo "ERROR: Cannot determine base branch. Set it with: git remote set-head origin <branch>"
    exit 1
  fi
fi

# 2. Current branch
CURRENT=$(git branch --show-current)

# 3. Remote URL and platform detection
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
  echo "ERROR: No 'origin' remote configured."
  exit 1
fi

# Detect platform from URL
if echo "$REMOTE_URL" | grep -qi "github.com"; then
  PLATFORM="github"
elif echo "$REMOTE_URL" | grep -qi "gitlab.com"; then
  PLATFORM="gitlab"
elif echo "$REMOTE_URL" | grep -qi "bitbucket.org"; then
  PLATFORM="bitbucket"
else
  PLATFORM="unknown"
fi

# 4. Extract owner/repo (handles both HTTPS and SSH)
REPO_ID=$(echo "$REMOTE_URL" | sed -E 's#^(https?://[^/]+/|git@[^:]+:)##' | sed 's/\.git$//')

# 5. CLI tool availability
if [ "$PLATFORM" = "github" ]; then
  if command -v gh &>/dev/null && gh auth status &>/dev/null; then
    CLI="gh"
  else
    echo "ERROR: 'gh' CLI not found or not authenticated. Install: https://cli.github.com"
    exit 1
  fi
elif [ "$PLATFORM" = "gitlab" ]; then
  if command -v glab &>/dev/null && glab auth status &>/dev/null; then
    CLI="glab"
  else
    echo "ERROR: 'glab' CLI not found or not authenticated. Install: https://gitlab.com/gitlab-org/cli"
    exit 1
  fi
elif [ "$PLATFORM" = "bitbucket" ]; then
  CLI="api"
  echo "NOTE: Bitbucket has no official CLI. Will use API if needed."
fi
```

Store all detected values: `BASE`, `CURRENT`, `PLATFORM`, `REPO_ID`, `CLI`.

## Step 1: Pre-Flight Checks

Before creating the PR, verify the branch is in a valid state:

### 1.1 Not on base branch

```bash
if [ "$CURRENT" = "$BASE" ]; then
  echo "ERROR: You are on the base branch ($BASE). Create a feature branch first."
  exit 1
fi
```

If on the base branch, abort and tell the user to create a feature branch.

### 1.2 Uncommitted changes

```bash
git status --porcelain
```

If there are uncommitted changes, **warn** the user:
- "You have uncommitted changes. Want me to commit them first, or create the PR with only committed changes?"
- Do NOT auto-commit. Wait for user decision.

### 1.3 Remote tracking branch

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
```

If no upstream exists, push with tracking:

```bash
git push -u origin "$CURRENT"
```

### 1.4 Branch is up to date with remote

```bash
git fetch origin "$CURRENT" 2>/dev/null
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$CURRENT" 2>/dev/null)
```

If local is ahead of remote, push:

```bash
git push origin "$CURRENT"
```

## Step 2: Gather Context

Collect all the information needed to write a meaningful PR description.

### 2.1 Commit history since diverging

```bash
git log "origin/$BASE".."$CURRENT" --oneline
```

Read every commit message. These tell you what was done.

### 2.2 Changed files summary

```bash
git diff "origin/$BASE"..."$CURRENT" --stat
```

This shows which files were touched and how much.

### 2.3 Full diff

```bash
git diff "origin/$BASE"..."$CURRENT"
```

Read the full diff to understand what actually changed. Do not rely solely on commit messages — they can be misleading. The diff is the source of truth.

## Step 3: Generate PR

### 3.1 Draft title and body

Based on the diff and commits:

- **Title:** Concise, under 72 characters, describes *what* changed (not the branch name). Use imperative mood ("Add", "Fix", "Update", not "Added", "Fixed").
- **Body:** Structured with:
  - `## Summary` — 3-5 bullet points describing the changes and *why* they were made
  - `## Changes` — files and areas affected, grouped logically
  - `## Test Plan` — how to verify the changes work (manual steps, automated tests, etc.)

### 3.2 Create the PR

**GitHub:**

```bash
gh pr create --base "$BASE" --title "the pr title" --body "$(cat <<'EOF'
## Summary
- First change description
- Second change description
- Third change description

## Changes
- `path/to/file.ts` — what changed and why
- `path/to/other.ts` — what changed and why

## Test Plan
- [ ] Step to verify change 1
- [ ] Step to verify change 2
EOF
)"
```

**GitLab:**

```bash
glab mr create --target-branch "$BASE" --title "the mr title" --description "$(cat <<'EOF'
## Summary
- First change description

## Changes
- files affected

## Test Plan
- verification steps
EOF
)"
```

**Bitbucket:** Inform the user that Bitbucket has no official CLI and provide a direct link:
```
https://bitbucket.org/{REPO_ID}/pull-requests/new?source={CURRENT}&dest={BASE}
```

## Step 4: Present Result

After successful creation:

1. Show the PR/MR URL
2. Show the title and summary
3. Mention any warnings (uncommitted changes, unpushed commits that were pushed)

```
PR created successfully:
  URL: https://github.com/{owner}/{repo}/pull/{number}
  Title: {title}
  Base: {base} <- {current}
```

## Error Handling

| Error | Response |
|-------|----------|
| Not a git repository | "This directory is not a git repository." |
| No remote configured | "No 'origin' remote found. Add one with `git remote add origin <url>`." |
| CLI not installed | Show install link for the detected platform |
| CLI not authenticated | Show auth command: `gh auth login` / `glab auth login` |
| No commits on branch | "No commits found on this branch relative to {base}. Make some changes first." |
| PR already exists | Show existing PR URL and ask if user wants to update it |

## When to Skip Steps

- If user says "quick pr" or "just push and pr" — skip the detailed body, use commit messages as bullets
- If there is only 1 commit — use its message as the PR title and body
- If user provides a title/description — use those instead of generating

---

## Feature Context Integration

When a feature-context is active, this skill writes PR linkage:

1. **After PR creation:** Write the PR URL, branch name, and base branch to feature-context
2. **Data written:** PR URL, PR number, branch name, base branch, reviewer assignments if any
