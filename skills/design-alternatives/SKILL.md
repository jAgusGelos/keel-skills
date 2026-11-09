---
name: design-alternatives
description: |
  Frontend design gate — explore 2-4 distinct visual/UX directions as a single
  self-contained HTML file BEFORE implementing any UI. Use whenever a feature adds or
  reshapes a screen, page, dialog, or significant component, and the visual direction has
  not been explicitly decided yet. Triggered as a mandatory step by /spec-first and
  /spec-first-cc-cc for UI-touching features, and directly when the user says
  "design alternatives", "design gate", "alternativas de diseño", "mockup", "maquetá
  opciones", "how should this screen look", "explore designs", "UI options", "diseñá
  el frontend primero", or complains that shipped UI looks generic / templated / without
  intention. Produces design-alternatives.html (ticket summary + side-by-side directions
  built with the project's REAL design tokens + tradeoffs table + decision footer) and
  DESIGN.md (the chosen direction as an ADR-style record with UI acceptance criteria)
  in the feature's planning folder (.workspace/features/<feature>/). The user picks a
  direction before any implementation code is written.
version: 1.0.0
category: development
depends: []
---

# Design Alternatives — Frontend Design Gate

Generic UI is the residue of unmade decisions. This skill forces the design decisions to
happen — visibly, comparably, and BEFORE implementation — instead of emerging as
defaults during coding. It produces one self-contained HTML artifact where the user
compares 2-4 genuinely different directions rendered with the project's real design
tokens, picks one, and gets the decision recorded as implementable acceptance criteria.

Two failure modes this kills:

1. **Generic UI**: when nobody decides hierarchy, copy, states, and identity up front,
   the model outputs the statistical center of its training data — the same
   header + table + pagination shell for every screen, Cards as universal containers,
   stock component defaults everywhere.
2. **Design discovered at the end**: the user only sees how the feature looks after the
   implementation is done, when changing direction is expensive.

## Inputs

Before starting, resolve:

- **The brief**: ticket/spec text, or the confirmed feature request when invoked from
  spec-first / spec-first-cc-cc (Step 1 output). If neither exists, ask for a 2-4
  sentence problem statement.
- **Feature folder**: `.workspace/features/<feature-name>/` — the same folder the
  spec-first artifacts live in. Create it if missing. All outputs go here.
- **Affected app**: which frontend app the feature lands in (drives token extraction).

## Step 1: Design Brief — the intent contract

Write the brief before any visual exploration. It is 10 lines, not a document:

1. **Subject & user**: who lands on this screen and in what situation.
2. **The screen's ONE job**: what the user must accomplish. If two actions compete for
   "primary", the screen's purpose isn't decided — resolve it now (ask the user one
   question if needed).
3. **Hero**: which single element is visually dominant. "A table" is not an answer —
   ask what insight belongs above it (counts, coverage, expiring-soon, next action).
4. **Page archetype**: list / detail / settings-form / focused-flow / dashboard /
   first-run. Archetypes must NOT share one visual skin — a first-run invitation
   acceptance page is a brand moment, not a settings card.
5. **Data states**: what populated, empty, loading, and error genuinely look like for
   this feature (empty state = status + teach + CTA, never a bare string).
6. **Density**: dense ops surface or airy focused surface — a choice, not an accident.
7. **Constraints**: design-system rules from the project (layering conventions, token
   discipline, existing shared components that must be reused or extended).

Check the project's rules/AGENTS/CLAUDE files and existing `base/`–`shared/` components
so alternatives extend the real design system instead of ignoring it.

## Step 2: Design cache — extract tokens once, reuse every run

The mockup must look like the actual app, or the comparison is fiction. Token
extraction is done ONCE per repo and cached at **`.workspace/design/`** — do NOT
re-derive it on every invocation.

**Cache-first flow:**

1. If `.workspace/design/` exists, run the freshness check (below). Fresh → use the
   cache directly and skip to Step 3. Stale → regenerate only the stale parts.
2. If it doesn't exist, build it now (one-time cost):

```
.workspace/design/
├── tokens.css          # extracted CSS variables, ready to inline into any mockup:
│                       #   :root { ... }  (light)  +  .dark { ... }  (dark, if the
│                       #   app has dark mode) + font-family/size/radius/spacing vars.
│                       #   Header comment lists the SOURCE file paths it was
│                       #   extracted from (used by the freshness check).
├── design-context.md   # everything else worth not re-discovering:
│                       #   - token source paths per app
│                       #   - type scale, radius personality, spacing conventions
│                       #   - inventory of existing base/ and shared/ components
│                       #     (what exists, what variants they expose)
│                       #   - domain visual vocabulary so far (status tones, entity
│                       #     icons/accents) and known gaps
│                       #   - app shell notes (sidebar/topbar structure) for honest
│                       #     mockup context
└── mockup-shell.html   # reusable artifact skeleton: tokens inlined + document
                        # chrome CSS + mock app shell (sidebar/header/body) +
                        # controls + toggle JS, with TODO-comment slots. COPY it
                        # to the feature folder as the starting point — never
                        # build the artifact from scratch, never link to it
                        # (artifacts stay self-contained and frozen).
```

**Building the cache:** locate the token source — semantic CSS variables
(`globals.css`, `tokens.css`, `themes/*.css`), Tailwind theme config, or
styled-components theme. Example (a Next.js app): `apps/enterprise/src/styles/globals.css` +
`src/styles/themes/*.css` expose `--background`, `--foreground`, `--primary`,
`--border`, `--status-*`, etc. Copy the ACTUAL values of the active palette into
`tokens.css` (light + dark), then write `design-context.md` from the same research
pass.

**Freshness check (cheap):** the `tokens.css` header lists its source files; if any
source is newer than the cache (`find <sources> -newer .workspace/design/tokens.css`),
re-extract. `design-context.md` staleness is tolerable — refresh opportunistically
when you notice drift (new base component, new token), and append rather than rebuild.

**Using it:** inline `tokens.css` into the mockup's `<style>` block and write plain
CSS against those variables. No Tailwind build, no CDN, no external fonts/images —
the file must open from disk with zero network access. If a token the design needs
doesn't exist yet (e.g. a domain accent), that is itself a finding: propose it in the
alternative, list it in the tradeoffs table, and note it as a gap in
`design-context.md`.

Note: `.workspace/` is typically gitignored — the cache is per-machine. Missing cache
is never an error; it just means this is the first run on this checkout.

## Step 3: Generate 2-4 alternatives — directions, not re-skins

Default to 3: **one safe, one adventurous, one bold** (from the client's perspective).
Use 2 when the disagreement axis is genuinely binary; never more than 4 (invites
frankensteining without commitment).

Each alternative must be a **distinct strategy** — different layout, information
architecture, or interaction model — never a color/spacing re-skin of its siblings.
Plan each one on paper first (in thinking): name, one-line point of view, ASCII
wireframe, and its **signature element** — the one thing this direction will be
remembered by, drawn from the product's own domain (its objects, vocabulary,
materials), not from generic dashboard imagery.

Then self-critique before building: *"would I produce this exact design for any similar
brief?"* If yes for any alternative, it's a default, not a choice — revise it.

### Anti-generic ban list (applies to every alternative)

Never as defaults: centered hero + badge + exactly-3 icon cards; purple/indigo
gradients; 1px gray borders on every card; Card as universal container; uniform
border-radius middle values; floating gradient orbs; scattered micro-animations;
lorem ipsum; numbered markers (01/02/03) when content isn't a sequence; stock icon +
bare string as an empty state. Any of these may appear only as a justified choice.

### Craft floor (constant across alternatives — distinctiveness lives in direction)

- Hierarchy must survive grayscale: size/weight/position carry the scan order, color
  only reinforces. Squint test: purpose readable at thumbnail size.
- 2-3 text colors, 2 font weights, spacing on the project's scale with bigger gaps
  between groups than within them; body ≥16px equivalent (respect app conventions);
  line length 45-75ch for reading surfaces.
- Buttons in three tiers (solid primary / outline secondary / link tertiary), ONE
  primary per screen. Secondary actions use absence of color, not a second color.
- WCAG 4.5:1 contrast for body text; visible focus; ≥44px touch targets.

### Content requirements (per alternative)

- **Real copy**: actual titles, subtitles, button labels, error messages written for
  THIS feature. Microcopy is a design deliverable — it's how a screen reveals
  intention. Generic copy ("No items yet") is the verbal equivalent of default zinc.
- **Realistic ugly data**: long names, non-ASCII characters, missing avatars, extreme
  counts — a direction that only works with pretty data is untested.
- **All four data states**: populated, empty (status + teach + CTA), loading, error —
  reachable via in-page toggles. States are where directions actually differ.

## Step 4: Build design-alternatives.html (delegated to ONE subagent)

One self-contained file at `.workspace/features/<feature-name>/design-alternatives.html`.
**The orchestrator does NOT write this file.** It dispatches one `general-purpose`
subagent that builds it and returns the path plus the comparison table; the HTML never
passes through the orchestrator's context. Measured over 30 sessions, orchestrators that
wrote the file inline spent 12.7% of their whole context on this skill, most of it HTML
heredocs that were only ever read once, by a browser.

**Dispatch (one Agent call; wait for its notification, no polling).** The subagent
receives, verbatim in its prompt:

1. The brief from Step 1 and the ticket's acceptance criteria.
2. The cache paths from Step 2: `.workspace/design/mockup-shell.html`, the tokens file,
   the component inventory. Instruction: **start by COPYING `mockup-shell.html`**
   (tokens, document chrome, mock app shell, toggles are already there) and fill its
   slots; never rebuild the skeleton from scratch. If the build produces a new reusable
   block (a mock component, a state pattern, a chrome vocabulary piece), add it back to
   `mockup-shell.html` so the next run starts richer.
3. The 2-4 directions planned in Step 3, each with: name, one-line point of view, ASCII
   wireframe, signature element, real copy, and the ugly-data cases to render. Plus the
   anti-generic ban list, the craft floor, and the content requirements from Step 3,
   copied in full (the subagent has not loaded this skill).
4. The as-is baseline instruction: which component files hold the current UI (from the
   Step 2 research), so the baseline tab mirrors real class names, paddings, type sizes,
   layout and copy, never approximated from memory.
5. The file structure contract below, and the self-check: before returning, render a
   headless screenshot (`google-chrome --headless --screenshot=...`) and fix any layout
   breakage.
6. The return contract: absolute path of the HTML, the comparison table and the
   recommendation as markdown (at most ~40 lines), and nothing else. No HTML in the reply.

Vanilla HTML + CSS + minimal JS (tab switching, state toggles, theme/viewport toggles).
Structure the subagent must produce:

1. **Header — the brief**: ticket ID + title, 2-4 sentence summary of what the
   ticket/spec asks, the acceptance criteria the UI must satisfy, and the design
   brief's key answers (one job, hero, archetype). This is what lets the user judge
   every alternative against the same yardstick.
2. **As-is baseline tab (MANDATORY when the surface already exists)**: the first tab
   reproduces the CURRENT production UI faithfully — read the real component code
   (exact class names, paddings, type sizes, layout, copy) from the current
   branch/release and mirror those values; never approximate from memory. Label it
   "As-is today — baseline, not a candidate". When the app is runnable, screenshot
   the real screen and verify the reproduction against it before presenting. The
   whole point of the artifact is knowing how the UI will actually look; a decision
   judged against an idealized or misremembered current state is fiction. For brand
   new surfaces, the baseline is the nearest existing sibling screen instead.
3. **Alternative tabs**: one full-width section per direction, switchable. Per
   alternative: name + one-line point of view + signature element callout, then the
   mockup rendered at realistic app width (include the app shell — sidebar/topbar —
   simplified, so context is honest). State toggles (populated / empty / loading /
   error) and, if the app has one, a light/dark toggle. A narrow-viewport toggle
   (constrain to ~400px) when mobile behavior matters.
4. **Comparison table**: one row per criterion — fit to acceptance criteria,
   implementation effort / reuse of existing base-shared components, new tokens or
   variants required, information density & scalability, risk (novel vs established
   pattern), accessibility notes. One column per alternative.
5. **Recommendation**: which direction the skill recommends and why, in 2-3 sentences.
   Recommend — don't decide.
6. **Decision footer**: a visible block listing each alternative with space for the
   verdict, explicitly inviting hybrid picks ("A's layout with C's summary strip").

Keep it honest roughness: no animation polish, no exhaustive breakpoints. The file
communicates *direction*, and visible roughness correctly signals "not final".

When the subagent's notification arrives, read its reply (path + table). Do NOT `cat`
or `Read` the HTML into the orchestrator's context; open it in the browser (Step 5).

## Step 5: Present and STOP for the decision

**Open the file in the user's browser yourself** (`xdg-open <abs-path>` on Linux,
`open` on macOS) — don't make the user copy a path. Also print the absolute path
prominently as fallback. The headless-screenshot self-check already ran inside the
build subagent (Step 4, item 5); if its reply reports unresolved breakage, send it back
to the same subagent with `SendMessage` rather than patching the HTML yourself.

Then ask ONE question: which direction (or hybrid) to proceed with. Do NOT start
implementation, do NOT write plan/todo content that assumes a direction, until the
user answers.

## Step 6: Record the decision — DESIGN.md

On selection, write `.workspace/features/<feature-name>/DESIGN.md` (ADR-style, becomes
the implementable contract):

```markdown
# Design Direction: [Feature Name]

> Decided [date] via design-alternatives. Mockup: ./design-alternatives.html

## Context
[Ticket + the design brief: one job, hero, archetype, density]

## Options considered
- **[A name]** — [one-line strategy] — [chosen/rejected: why]
- **[B name]** — [one-line strategy] — [chosen/rejected: why]

## Decision
[Chosen direction + any hybrid modifications, described concretely]

## Design tokens & components
- Tokens used / proposed: [list; flag any NEW token or cva variant to add]
- Existing components reused: [base/shared components]
- New/extended components: [what gets built, at which layer]

## UI acceptance criteria
- [ ] [Hierarchy commitment — e.g. "summary strip above the table is the hero"]
- [ ] [Microcopy commitments — the actual title/subtitle/empty-state copy from the mockup]
- [ ] [All four data states implemented as designed (empty = icon + teach + CTA)]
- [ ] [Signature element present: ...]
- [ ] [No ad-hoc className overrides on base components — new variants go in the base layer]
```

The UI acceptance criteria feed the plan's Conformance Criteria and the todo's Verify
subtasks; the implementation review checks the diff against DESIGN.md and the mockup.

## Integration with spec-first / spec-first-cc-cc

When invoked as the design gate (Step 5b of those workflows):

- Runs after research/three-experts, BEFORE plan.md is drafted, so the plan encodes the
  chosen direction instead of leaving design to the implementation session.
- Reuses the Step 1-confirmed request and Step 2 research (don't re-explore).
- plan.md references DESIGN.md in a "Design Direction" section; todo.md tasks that
  build UI reference the UI acceptance criteria; NEXT_SESSION_PROMPT.md lists
  DESIGN.md and design-alternatives.html as mandatory reading.
- **The gate is NON-OPTIONAL for features with UI.** If the ticket is a feature and it
  touches any user-visible surface, the gate runs — no exceptions for size, "obvious"
  designs, or schedule pressure. "It's just a small table page" is NOT a skip reason;
  identical table pages are exactly how generic UI compounds.
- The only exemptions:
  1. **No user-visible UI** (backend, CLI, invisible refactor).
  2. **Bugfix** — restoring already-decided behavior/appearance. But if the "fix"
     introduces a new visual treatment, state, or layout that didn't exist before,
     that's design work in disguise → the gate runs.
  In both cases record the skip and its reason in findings.md.

## Anti-patterns

1. **Re-skins as alternatives** — three shades of the same layout is one option
   presented three times. Directions must differ in strategy.
2. **Fictional tokens** — mocking with colors/fonts the app doesn't have makes the
   comparison meaningless and the winner unimplementable.
3. **Lorem ipsum / pretty data** — copy and ugly data are load-bearing decision inputs.
4. **Skipping states** — populated-only mockups hide where directions differ most.
5. **Deciding instead of recommending** — the human picks; the generator doesn't
   self-select (gate independence).
6. **Skipping DESIGN.md** — an unpicked or unrecorded decision evaporates; the
   implementation session will regress to defaults.
7. **Polishing the mockup** — animation and pixel-perfection burn time and falsely
   signal "done". Direction fidelity: hierarchy, tokens, copy, states.
8. **Mockup drift** — if implementation deviates from DESIGN.md deliberately, update
   DESIGN.md with the reason; never let them silently diverge.
9. **Idealized baseline** — rendering the current UI prettier, cleaner, or otherwise
   different from how it actually looks today. The baseline must be read from the
   real component code (and checked against a real screenshot when possible); an
   inaccurate baseline invalidates every comparison built on it.

## Quality checklist

- [ ] Design brief written (one job, hero, archetype, density, states) before mockups
- [ ] Design cache checked FIRST: `.workspace/design/tokens.css` + `design-context.md`
      + `mockup-shell.html` reused when fresh, created only if missing, re-extracted
      only if sources are newer
- [ ] Artifact started as a COPY of `mockup-shell.html`; new reusable blocks fed back
      into the shell
- [ ] Tokens in the mockup come from the cache (extracted from the project's real
      stylesheet, light + dark if applicable) — never invented
- [ ] 2-4 alternatives, each a distinct strategy with a named signature element
- [ ] Self-critique ran: no alternative is the "any similar brief" default
- [ ] Ban list respected; craft floor met in all alternatives
- [ ] Real copy + realistic ugly data + four data states, toggleable in-page
- [ ] HTML is fully self-contained (opens from disk, no network) with the ticket
      summary in the header
- [ ] As-is baseline tab present (existing surfaces), reproduced from the REAL
      component code — exact spacing/type/copy — and verified against a screenshot
      of the running app when available
- [ ] Comparison table + recommendation + decision footer present
- [ ] STOPPED for the user's pick; hybrid choices captured concretely
- [ ] DESIGN.md written with UI acceptance criteria; referenced from plan/todo when
      inside a spec-first flow
