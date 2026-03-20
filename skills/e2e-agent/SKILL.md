---
name: e2e-agent
description: |
  End-to-end testing agent that writes valuable Cypress tests grounded in real user behavior.
  Uses the cc-cc dual-engine pattern: Claude writes tests from the user's perspective (informed
  by memory-bank product context), Codex independently validates them, and a synthesis pass
  merges the best of both. Use when the user says "add e2e", "write e2e tests", "cypress tests",
  "end to end", "e2e agent", "test user flows", "integration tests with cypress", "add cypress",
  "test this feature e2e", or wants to ensure a feature works from the user's perspective.
  Also trigger when the user asks to "test the happy path", "test critical flows", or
  "make sure this works for real users".
version: 1.0.0
category: development
depends: [cc-cc-powerful-iterations, memory-bank]
---

# E2E Agent — Valuable Cypress Tests from the User's Perspective

Writes E2E tests that verify real user value, not just DOM presence. Every test answers the
question: "Can the user accomplish what they came here to do?"

## Philosophy

Most E2E tests are worthless. They check that buttons exist, inputs render, and pages load —
things that break loudly anyway. Valuable E2E tests verify **critical user journeys**: the
flows where failure means lost revenue, broken trust, or data corruption.

This agent thinks like the user before writing a single line of Cypress.

## The Pyramid Rule

E2E tests are expensive. Only test at this level what **cannot** be caught by unit or
integration tests:

- Cross-page navigation flows
- Multi-step forms with server-side validation
- Auth-gated workflows end-to-end
- Payment / checkout / destructive operations
- Real-time features (notifications, websockets, polling)
- Third-party integration touchpoints (from your side)

If a unit test can catch it → don't write an E2E test for it.

## The Cycle

```
User Request
      |
      v
[0] Context Gathering — memory-bank + codebase analysis
      |
      v
[1] Journey Mapping — identify critical user flows to test
      |
      v
[2] Parallel Execution ──┬── Claude Agent: writes tests from user perspective
      |                   └── Codex CLI: independently writes/validates tests
      v
[3] Synthesis — merge best of both engines
      |
      v
[4] Codex Review — final validation pass
      |
      v
[5] Scaffold & Deliver — install, configure, deliver tests
```

## Step 0: Context Gathering

Before writing any test, understand who the user is and what they care about.

### Read Memory Bank (if available)

Check for `memory-bank/` in the project root. If it exists, read in this order:

1. **`memory-bank/product-context.md`** — User personas, user flows, UX decisions, pain points.
   This is the most important file. It tells you what the user actually does in the app.
2. **`memory-bank/project-brief.md`** — What the product does, success criteria, target users.
3. **`memory-bank/system-patterns.md`** — Architecture, routing structure, key abstractions.
4. **`memory-bank/tech-context.md`** — Stack details, API patterns, auth mechanism.
5. **`memory-bank/active-context.md`** — Current focus, recent changes (what to test now).

If memory-bank doesn't exist, scan the codebase directly:
- Read `README.md` for product context
- Read `package.json` for stack and existing test setup
- Scan `src/pages/`, `src/app/`, `app/` for route structure
- Look for existing tests (`**/*.test.*`, `**/*.spec.*`, `cypress/`)
- Read key page/component files to understand user flows

### Extract User Mental Model

From the context gathered, build an internal model:

- **Who is the user?** (persona, goals, frustrations)
- **What are the critical journeys?** (sign up → onboard → first value moment)
- **Where does failure hurt most?** (payment, data submission, auth)
- **What are the happy paths vs edge cases?**

This model drives every test you write.

## Step 1: Journey Mapping

Produce a prioritized list of user journeys to test. Present to the user for approval
before writing any code.

### Priority Framework

| Priority | What to Test | Example |
|----------|-------------|---------|
| P0 - Critical | Flows where failure = lost revenue or data | Checkout, signup, data submission |
| P1 - High | Core value flows the user does daily | Dashboard load, CRUD on main entities |
| P2 - Medium | Secondary flows with moderate impact | Settings changes, profile updates |
| P3 - Low | Nice-to-have coverage | Empty states, tooltips, minor UI |

### Journey Format

For each journey, define:

```markdown
### Journey: [Name]
**Priority:** P0/P1/P2/P3
**User Goal:** What the user is trying to accomplish
**Preconditions:** Auth state, data state, feature flags
**Steps:**
1. User does X
2. System responds with Y
3. User sees Z
**Success Criteria:** What proves this journey works
**Failure Impact:** What happens if this breaks in prod
```

Present 5-8 journeys ranked by priority. Ask the user: "These are the flows I'd test first.
Want to adjust priorities or add/remove any?"

## Step 2: Parallel Execution (cc-cc pattern)

Once journeys are approved, launch both engines with the same context.

### Claude Subagent: User-Perspective Test Writer

Use the Agent tool (general-purpose) with this prompt:

```
You are a Cypress E2E test engineer who thinks like an end user, not a developer.

## Context
{MEMORY_BANK_CONTEXT or CODEBASE_CONTEXT}

## User Journeys to Test
{APPROVED_JOURNEYS}

## Your Task
Write Cypress E2E tests for each approved journey. Follow these rules strictly:

### Test Design Rules

1. **Test user outcomes, not implementation details**
   - BAD: `cy.get('.MuiButton-root').should('exist')`
   - GOOD: `cy.get('[data-cy="submit-order"]').click(); cy.contains('Order confirmed').should('be.visible')`

2. **Use data-cy attributes for selection**
   - Every selector uses `[data-cy="..."]` attributes
   - Generate a list of required data-cy attributes at the end
   - For text content that IS the thing being tested (headings, labels), `cy.contains()` is fine

3. **Each test is independent** — runs in isolation via `it.only`
   - Use `beforeEach` for shared setup
   - Never depend on test execution order
   - Reset state programmatically (API calls, db:seed, localStorage clear)

4. **Programmatic auth** — never test login via UI (except the login test itself)
   ```javascript
   Cypress.Commands.add('login', (email, password) => {
     cy.request('POST', '/api/auth/login', { email, password }).then((resp) => {
       window.localStorage.setItem('token', resp.body.token)
     })
   })
   ```

5. **Wait on network, not time**
   - NEVER use `cy.wait(N)` with a number
   - ALWAYS intercept and alias: `cy.intercept('GET', '/api/data').as('getData'); cy.wait('@getData')`

6. **Assert on visible user outcomes**
   - After form submit → assert success message or redirect
   - After delete → assert item removed from list
   - After error → assert user-facing error message
   - Think: "What would the user check with their eyes?"

7. **Test the unhappy path too**
   - Invalid input → proper validation messages
   - Network failure → graceful error handling
   - Unauthorized access → proper redirect
   - Empty states → helpful guidance message

8. **Group by user journey, not by page**
   ```javascript
   describe('Checkout Flow', () => {
     // Not: describe('CartPage', () => ...)
   })
   ```

### File Structure
```
cypress/
├── e2e/
│   ├── auth/
│   │   └── login.cy.js
│   ├── [feature]/
│   │   └── [journey].cy.js
│   └── smoke/
│       └── critical-paths.cy.js    ← P0 tests only, runs on every deploy
├── support/
│   ├── commands.js                  ← Custom commands (login, resetDb, etc.)
│   └── e2e.js                       ← Global hooks
└── fixtures/
    └── [feature]/
        └── [data].json              ← Test data
```

### Output Format
For each journey, produce:
1. The test file with complete, runnable Cypress code
2. A list of `data-cy` attributes that need to be added to the app
3. Any custom commands needed in `support/commands.js`
4. Any fixtures needed
```

### Codex CLI: Independent Test Validator

Run Codex to independently write or validate the same tests:

```bash
codex -a never exec "You are a Cypress E2E testing expert. Given the following app context and user journeys, write production-quality Cypress tests.

Focus on:
1. Testing real user outcomes, not DOM structure
2. Using data-cy selectors (list all needed at the end)
3. Intercepting network requests instead of arbitrary waits
4. Independent tests with programmatic state setup
5. Both happy and unhappy paths
6. Edge cases: empty states, concurrent actions, slow networks

App Context:
{CONTEXT}

User Journeys:
{JOURNEYS}

Write complete, runnable test files. Include custom commands and fixtures."
```

**Fallback:** If Codex is unavailable, launch a second Claude subagent with the same prompt.

## Step 3: Synthesis

Once both engines return:

1. **Compare test coverage** — did both engines cover the same journeys? Did one catch edge
   cases the other missed?
2. **Compare test quality** — which engine wrote more resilient selectors? Better assertions?
   More realistic user flows?
3. **Merge the best of both:**
   - Take the most comprehensive test for each journey
   - Add edge cases caught by only one engine
   - Unify selector strategy (always `data-cy`)
   - Unify custom commands (deduplicate)
   - Ensure consistent file structure
4. **Verify independence** — mentally run each test with `it.only`. Would it pass alone?

## Step 4: Codex Review

Send the synthesized tests back to Codex for validation:

```bash
codex -a never exec "Review these Cypress E2E tests for quality. Check:
1. Are tests truly independent? (no shared state between tests)
2. Are selectors resilient? (data-cy, not CSS classes)
3. Are waits explicit? (network aliases, not cy.wait(N))
4. Do assertions test user-visible outcomes?
5. Are unhappy paths covered?
6. Would these tests catch a real regression?
7. Are there any flaky patterns? (race conditions, timing issues)

Flag issues and suggest fixes.

Tests:
{SYNTHESIZED_TESTS}"
```

Incorporate valid feedback. Skip stylistic suggestions.

## Step 5: Scaffold & Deliver

### Check Existing Setup

```bash
# Check if Cypress is already installed
ls cypress.config.* 2>/dev/null
cat package.json | grep cypress
```

### If Cypress Not Installed

Provide installation instructions (don't auto-install without asking):

```markdown
## Setup Required

Run these commands to set up Cypress:

\`\`\`bash
npm install -D cypress
npx cypress open  # First-time setup creates directory structure
\`\`\`

Then add to `package.json` scripts:
\`\`\`json
{
  "scripts": {
    "cy:open": "cypress open",
    "cy:run": "cypress run",
    "cy:smoke": "cypress run --spec 'cypress/e2e/smoke/**'"
  }
}
\`\`\`
```

### Deliver

Present to the user:

1. **Journey map** — which flows are covered and at what priority
2. **Test files** — complete, runnable Cypress code
3. **Required data-cy attributes** — list of attributes to add to the app, organized by
   component/page
4. **Custom commands** — `support/commands.js` additions
5. **Config** — `cypress.config.js` if needed
6. **Smoke suite** — which tests should run on every deploy (P0 only)

### Data-Cy Attribute Report

Always end with a consolidated list:

```markdown
## Required data-cy Attributes

Add these attributes to your components for the tests to work:

| Component/Page | Element | Attribute | Used By Test |
|---------------|---------|-----------|--------------|
| LoginForm | Email input | `data-cy="login-email"` | auth/login.cy.js |
| LoginForm | Submit button | `data-cy="login-submit"` | auth/login.cy.js |
| ... | ... | ... | ... |
```

## Cypress Configuration Reference

When generating `cypress.config.js`, use these best practices:

```javascript
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000', // Adapt to project
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    // Retry on CI only
    retries: {
      runMode: 2,     // cy:run (CI)
      openMode: 0,    // cy:open (local)
    },
    setupNodeEvents(on, config) {
      // Register tasks here (db:seed, etc.)
    },
  },
})
```

## Anti-Pattern Blacklist

Never write tests that do any of these:

| Anti-Pattern | Why It's Bad | Do Instead |
|---|---|---|
| `cy.wait(3000)` | Flaky, slow | `cy.wait('@alias')` or assertion retry |
| `cy.get('.btn-primary')` | Breaks on style changes | `cy.get('[data-cy="submit"]')` |
| Test A depends on Test B's state | Coupled, fragile | Independent setup in `beforeEach` |
| `cy.get('#root').should('exist')` | Tests nothing useful | Assert user-visible outcome |
| Login via UI in every test | Slow, flaky | `cy.login()` custom command |
| `cy.visit()` to third-party sites | Unreliable, blocked | Stub or use API |
| Hardcoded test data inline | Unmaintainable | Use fixtures |
| `expect(true).to.be.true` | Meaningless assertion | Assert actual behavior |
| Testing implementation (`store.dispatch`) | Couples to internals | Test user-facing result |

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/e2e/`
- **Checkpoint frequency:** After Steps 0 (context), 1 (journeys), 3 (synthesis), 5 (delivery)
- **Subagent delegation:** Claude/Codex test writing (Step 2), Codex review (Step 4)

## When to Skip the Full Cycle

- **Single test for a specific feature:** Skip journey mapping (Step 1). Go straight to writing
  the test with context from Step 0.
- **Quick smoke test:** Write only P0 tests, skip Codex engine, skip review.
- **Codex unavailable:** Use two Claude subagents instead. Same pattern, different second engine.
