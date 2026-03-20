---
name: style-guide
description: |
  Define, maintain, and enforce a UI/UX Style Guide with design tokens, component patterns,
  and accessibility standards. Integrates with memory-bank for project-aware generation.
  Use this skill when the user mentions "style guide", "design system", "UI guidelines",
  "UX conventions", "design tokens", "sg init", "sg update", "sg audit", "component patterns",
  "color palette", "typography system", "design philosophy", or when creating/modifying UI
  components and wanting consistency checks. Also trigger when the user asks to audit
  accessibility, check color contrast, or enforce design consistency across the codebase.
version: 1.0.0
category: development
depends: []
---

# Style Guide

Define, maintain, and enforce a project's UI/UX style guide through structured files in `style-guide/`.

## Command Router

Interpret user intent:
- `sg init` or "create style guide" → run **INIT**
- `sg update` or "sync style guide" → run **UPDATE**
- `sg audit` or "check style violations" → run **AUDIT**
- If ambiguous, ask: "Do you want to INIT, UPDATE, or AUDIT the style guide?"

## Shared Rules

- Keep all outputs in `style-guide/` directory
- Token-based and implementation-oriented — no vague design prose
- Prefer existing project conventions over inventing new patterns
- If a mature design system exists, document and align to it — don't replace it
- Bullet-point format in all generated files (same philosophy as memory-bank)
- When multiple design systems coexist (e.g., Tailwind + CSS vars + component library), Tier 1 takes precedence; higher tiers supplement without overriding

---

## Memory Bank Integration

**This skill depends on memory-bank for project-aware generation.**

### On INIT (required check):
1. Check if `memory-bank/` exists
2. If present, read in order:
   - `memory-bank/project-brief.md` → extract goals, target users, success criteria → feeds `design-philosophy.md` (Product Intent, Target Users)
   - `memory-bank/product-context.md` → extract UX decisions, user flows, known issues → feeds `design-philosophy.md` (Experience Rules) and `components.md` (which patterns are needed)
   - `memory-bank/tech-context.md` → extract framework, CSS approach, dependencies → determines which design system to align with, which token format to use
   - `memory-bank/system-patterns.md` → extract architecture, component organization → informs `components.md` structure and `spacing-layout.md` layout patterns
3. If `memory-bank/` missing:
   - Warn: "memory-bank/ not found. Style guide will use codebase inference only. Run `mb init` first for context-aware generation."
   - Proceed with auto-detection only
   - Mark memory-bank-dependent sections with `<!-- NEEDS CONTEXT: run mb init, then sg update -->`

### On UPDATE:
- Re-read memory-bank files if they exist
- If `product-context.md` changed → review `design-philosophy.md` and `components.md`
- If `tech-context.md` changed (framework switch) → flag ALL style-guide files for review
- If `project-brief.md` changed (new users/goals) → review `design-philosophy.md` and `accessibility.md`

### Conflict resolution:
- Memory-bank provides **intent** (what the project wants to be)
- Auto-detection provides **reality** (what the code currently does)
- When they disagree: flag the conflict, ask user which to follow, document the decision

---

## Auto-Detection (runs in INIT and UPDATE)

Scan for existing design tokens and systems in priority order:

**Tier 1 — CSS/Tailwind foundations:**
- `tailwind.config.*` → extract theme colors, spacing, fonts, breakpoints
- `postcss.config.*` → confirm Tailwind pipeline
- CSS files with `:root` custom properties → extract variable values

**Tier 2 — Token systems:**
- `theme.ts`, `theme.js`, `tokens.json`, `design-tokens.json`
- Style-dictionary config files

**Tier 3 — Component libraries:**
- `components.json` (shadcn/ui) → extract baseColor, style, cssVariables
- `package.json` deps: `@mui/*`, `@chakra-ui/*`, `antd`, `@radix-ui/*`, `@headlessui/*`

**Tier 4 — Global stylesheets:**
- `globals.css`, `global.scss`, `App.css`, `index.css`
- Extract color values, font declarations, spacing patterns, media queries

Higher tiers supplement lower tiers. Tier 1 values take precedence on conflicts.

---

## Operation: INIT

**Trigger:** "sg init", "create style guide", or no `style-guide/` when user asks for design guidance.

1. Read memory-bank files (see integration section above)
2. Run auto-detection workflow
3. Create `style-guide/` directory
4. Generate 7 files using templates below, populated with real data
5. Where no data detected, use defaults marked with `<!-- DEFAULT: update with actual values -->`
6. Report: which memory-bank files read, which design sources detected, which files need manual review

**Edge cases:**
- **style-guide/ partially exists:** Read existing files, create only missing ones
- **Mature design system detected:** Document it rather than inventing new patterns
- **No UI in project:** Create minimal skeleton, note that full guide is deferred

---

## Operation: UPDATE

**Trigger:** "sg update", "sync style guide", or after significant UI changes.

1. Re-read memory-bank files and re-run auto-detection
2. Compare detected values against current style-guide files
3. Update changed files, preserve stable decisions and manual customizations
4. Add changelog entry at bottom of each modified file: `- [YYYY-MM-DD] Updated [section] from [source]`
5. Report changes and flag any conflicts

---

## Operation: AUDIT

**Trigger:** "sg audit", "check style violations", or when user asks about design consistency.

### Scan scope:
- Include: `src/`, `app/`, `pages/`, `components/`, `styles/` (and equivalents)
- Exclude: `node_modules/`, build output, test files, token/theme definition files
- User can override scope: "sg audit src/components/"

### Checks:

**1. Color audit** — read `style-guide/colors.md` for approved palette
- Grep for hex (`#[0-9a-fA-F]{3,8}`), rgb/rgba, hsl/hsla, named CSS colors
- Flag values not in approved token list
- Exclude: SVG files, config files, comments

**2. Typography audit** — read `style-guide/typography.md`
- Grep for `font-family`, `font-size`, `font-weight`, `line-height` declarations
- Flag values not matching approved scale

**3. Spacing audit** — read `style-guide/spacing-layout.md`
- Grep for padding/margin/gap with values not on the spacing scale
- Flag hardcoded pixel values where tokens should be used

**4. Accessibility audit** — read `style-guide/accessibility.md`
- `<img` without `alt` attribute
- Interactive elements without `aria-label` or visible label
- `onClick` on non-interactive elements without `role="button"` + `tabIndex`
- `outline: none` or `outline: 0` without custom focus style
- Missing `<label>` associations for form inputs

### Report format:
```
## Style Guide Audit Report — [YYYY-MM-DD]

### Summary
- Errors: N (accessibility violations)
- Warnings: N (style inconsistencies)
- Info: N (suggestions)

### Errors (accessibility)
- [file:line] [rule violated] — [fix recommendation]

### Warnings (inconsistencies)
- [file:line] [rule violated] — [fix recommendation]

### Info (suggestions)
- [file:line] [suggestion]
```

---

## File Templates

### style-guide/design-philosophy.md

```markdown
# Design Philosophy

## Product Intent
<!-- Source: memory-bank/project-brief.md -->
- Goal: <one-line project purpose>
- Primary users: <user type — technical level, context>
- Secondary users: <additional segments>
- UX success criteria: <what "good" looks like>

## Core Principles
- <Principle name>: <one-line rule>
- <Principle name>: <one-line rule>
- <Principle name>: <one-line rule>
- Accessible by default: inclusion is not optional

## Experience Rules
<!-- Source: memory-bank/product-context.md -->
- Clarity: <rules about information hierarchy>
- Feedback: <rules about state communication>
- Consistency: <rules about pattern reuse>

## Tone & Personality
- Visual tone: <e.g., "Professional but approachable">
- Language style: <e.g., "Direct, action-oriented microcopy">
- Emotional goal: <e.g., "Users feel confident and in control">

## Change Control
- Update when: product goals change, user research reveals new needs, tech stack shifts
```

### style-guide/colors.md

```markdown
# Color System
<!-- Source: [detected — e.g., tailwind.config.ts, :root variables] -->

## Primary Palette
- Primary: <hex> — main brand/action color
- Primary hover: <hex>
- Primary light: <hex> — backgrounds, subtle emphasis
- Secondary: <hex> — supporting color
- Accent: <hex> — highlights, badges

## Neutrals
- White: <hex>
- Gray 50–900: <hex per step>
- Black: <hex>

## Semantic Colors
- Success: <hex> — confirmations, positive
- Warning: <hex> — caution, pending
- Error: <hex> — destructive, validation errors
- Info: <hex> — informational

## Dark Mode (if applicable)
- Background: <hex>
- Surface: <hex>
- Text primary/secondary: <hex>

## Usage Rules
- Minimum contrast: 4.5:1 normal text, 3:1 large text (WCAG AA)
- Never use color as sole state indicator — pair with icons/text
- Semantic colors must not be repurposed
- Use tokens/variables, never hardcoded hex in components

## Migration Notes
- <legacy value>: replace with <token>
```

### style-guide/typography.md

```markdown
# Typography System
<!-- Source: [detected — e.g., tailwind config, Google Fonts import] -->

## Font Families
- Primary: <font> — <fallback stack>
- Monospace: <font> — <fallback stack>

## Type Scale
- H1: <size>px / <line-height> / <weight> — page titles
- H2: <size>px / <line-height> / <weight> — section headings
- H3: <size>px / <line-height> / <weight> — subsection headings
- H4: <size>px / <line-height> / <weight> — card titles
- H5: <size>px / <line-height> / <weight> — small headings
- Body: <size>px / <line-height> / <weight> — standard text
- Body small: <size>px / <line-height> / <weight> — secondary info
- Label: <size>px / <weight> — buttons, form labels, tags
- Caption: <size>px / <weight> — timestamps, metadata

## Rules
- Minimum body text: 16px
- Max line length: 65-75 characters for body
- Sequential heading hierarchy (no skipping levels)
- Use rem in implementation, document px for design reference

## Prohibitions
- No unauthorized font families
- No font sizes outside the scale
```

### style-guide/spacing-layout.md

```markdown
# Spacing & Layout
<!-- Source: [detected — e.g., tailwind spacing, CSS custom properties] -->

## Spacing Scale
- 2xs: 4px (0.25rem)
- xs: 8px (0.5rem)
- sm: 12px (0.75rem)
- md: 16px (1rem)
- lg: 24px (1.5rem)
- xl: 32px (2rem)
- 2xl: 48px (3rem)
- 3xl: 64px (4rem)

## Breakpoints
- Mobile: 0–639px
- Tablet: 640–1023px
- Desktop: 1024–1279px
- Wide: 1280px+

## Grid
- Columns: <e.g., 12-column desktop, 4-column mobile>
- Gutter: <value>
- Max content width: <value>

## Usage Rules
- Inside components: use smaller tokens (2xs–sm)
- Between components: use medium tokens (md–xl)
- Between sections: use large tokens (xl–3xl)
- No arbitrary pixel values — always use the scale

## Prohibitions
- Hardcoded one-off spacing values
```

### style-guide/components.md

```markdown
# Component Patterns
<!-- Source: memory-bank/product-context.md, memory-bank/system-patterns.md, detected library -->

## Source of Truth
- Library: <shadcn/ui | MUI | Chakra | custom>
- Config: <file path>

## Buttons
- Primary: <bg color>, <text color>, <padding>, <border-radius>
  - Hover/Active/Disabled/Focus states
- Secondary: outlined variant, same sizing
- Destructive: <error color>, requires confirmation
- Ghost: transparent, minimal padding

## Inputs
- Text field: <height>, <padding>, <border>, <border-radius>
  - Focus/Error/Disabled states
  - Label above, helper text below

## Cards
- Background: <color>, Border: <spec>, Padding: <token>, Radius: <value>

## Modals
- Overlay: black 50% opacity
- Container: centered, max-width, focus trap required
- Close: top-right icon, Escape key

## Navigation
- Desktop: <pattern>
- Mobile: <pattern>

## Empty States
- Centered, illustration/icon + heading + description + CTA

## Loading States
- Skeleton screens for layout-known content
- Spinner for actions/buttons
- Minimum display: 300ms

## State Matrix
- Default / Hover / Focus / Active / Disabled / Loading — per key component
```

### style-guide/accessibility.md

```markdown
# Accessibility Standards

## Baseline
- WCAG Target: Level AA (2.1)
- Normal text contrast: 4.5:1 minimum
- Large text contrast: 3:1 minimum
- UI components/graphics: 3:1 minimum

## Focus Management
- Visible focus indicators on all interactive elements
- Focus ring: 2px solid <primary>, 2px offset
- Never `outline: none` without custom focus style
- Modal/dialog focus trapping required
- Return focus to trigger on close

## Keyboard Navigation
- All functionality available via keyboard
- Tab: between interactive elements
- Enter/Space: activate buttons/links
- Escape: close modals/dropdowns
- Arrow keys: within component groups
- Skip-to-content link as first focusable element

## ARIA Patterns
- Images: `alt` required; decorative = `alt=""`
- Icon-only buttons: `aria-label` required
- Forms: `<label>` with `htmlFor` or `aria-label`
- Live regions: `aria-live="polite"` for updates
- Modals: `role="dialog"`, `aria-modal="true"`
- Loading: `aria-busy="true"` on containers

## Motion
- Respect `prefers-reduced-motion`
- No content flashing >3 times/second

## Testing Checklist
- [ ] Full keyboard navigation
- [ ] Screen reader test (VoiceOver/NVDA)
- [ ] All images have alt text
- [ ] Color contrast verified
- [ ] 200% zoom — no content loss
- [ ] Focus management in modals/dynamic content
```

### style-guide/animations.md

```markdown
# Animation & Motion

## Principles
- Purpose: communicate state changes, guide attention, provide feedback
- Subtlety: enhance, never distract or delay
- Performance: prefer transforms and opacity (GPU-accelerated)
- Accessibility: respect `prefers-reduced-motion`

## Duration Scale
- Fast: 100ms — hover, focus, color shifts
- Normal: 200ms — dropdowns, tooltips, fade
- Moderate: 300ms — modals, panels, slides
- Slow: 500ms — page transitions

## Easing
- Ease out: `cubic-bezier(0.0, 0.0, 0.2, 1)` — entering elements
- Ease in: `cubic-bezier(0.4, 0.0, 1, 1)` — exiting elements
- Ease in-out: `cubic-bezier(0.4, 0.0, 0.2, 1)` — moving/resizing

## Common Patterns
- Modal enter: fade 200ms + scale 0.95→1.0
- Dropdown: fade 200ms + translateY -4px→0
- Toast: slide-in 300ms from right
- Skeleton shimmer: 1.5s linear infinite

## Reduced Motion
- Replace transforms with opacity fades
- Reduce durations to <=100ms
- Disable looping animations except essential spinners

## Prohibitions
- Never animate layout properties (width, height, top, left)
- Never block interaction during animation
- No auto-play video without user consent
- Max stagger: 50ms between children
```

---

## Completion Criteria

**INIT complete when:**
- All 7 files exist in `style-guide/`
- Templates populated with project-specific data (not all placeholders)
- Memory-bank warning shown if missing
- Detection sources listed in report

**UPDATE complete when:**
- Changed decisions synchronized across files
- Each modified file has changelog entry
- Conflicts flagged to user

**AUDIT complete when:**
- Findings grouped by severity with file:line + rule + fix
- Or explicit "No violations detected" if clean
