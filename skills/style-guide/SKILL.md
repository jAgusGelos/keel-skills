---
name: style-guide
description: |
  Define, maintain, and enforce a UI/UX Style Guide with design tokens, component patterns,
  and accessibility standards. Integrates with memory-bank for project-aware generation.
  Use this skill when the user mentions "style guide", "design system", "UI guidelines",
  "UX conventions", "design tokens", "sg init", "sg update", "sg audit", "sg teach",
  "component patterns", "color palette", "typography system", "design philosophy",
  "anti-pattern", "AI slop", "modern CSS", or when creating/modifying UI components
  and wanting consistency checks. Also trigger when the user asks to audit accessibility,
  check color contrast, enforce design consistency, or teach brand context.
version: 1.1.0
category: development
depends: [memory-bank]
---

# Style Guide

Define, maintain, and enforce a project's UI/UX style guide through structured files in `style-guide/`.

## Command Router

Interpret user intent:
- `sg init` or "create style guide" → run **INIT**
- `sg update` or "sync style guide" → run **UPDATE**
- `sg audit` or "check style violations" → run **AUDIT**
- `sg teach` or "teach brand context" → run **TEACH**
- If ambiguous, ask: "Do you want to INIT, UPDATE, AUDIT, or TEACH the style guide?"

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

1. Read `style-guide/design-context.md` if it exists (from `/sg teach`)
2. Read memory-bank files (see integration section above)
3. Run auto-detection workflow
4. **Detect tech stack and generate context-aware design system** (see below)
5. Create `style-guide/` directory
6. Generate 8 files using templates below, populated with real data
7. Where no data detected, use defaults marked with `<!-- DEFAULT: update with actual values -->`
8. Report: which memory-bank files read, which design sources detected, which files need manual review

### Design System Generation from Context

When no existing design system is detected, generate a complete one from the project description, design-context, and detected stack:

**Step 1 — Tech stack detection:**
- Scan `package.json`, framework configs, and imports to identify: React, Vue, Svelte, Angular, Astro, SolidJS, etc.
- Detect CSS approach: Tailwind, CSS Modules, styled-components, vanilla CSS, Sass, etc.
- Detect component library: shadcn/ui, Radix, Headless UI, MUI, Chakra, Ant Design, etc.
- Output determines token format (CSS vars, Tailwind config, JS theme object, etc.)

**Step 2 — Generate design tokens:**
- **Colors:** Use OKLCH color space (see Modern CSS Defaults). Generate primary, secondary, accent from brand context or industry defaults. Build neutral scale, semantic colors (success/warning/error/info), and surface colors for light/dark. Every color as OKLCH with hex fallback.
- **Typography:** Fluid type scale using `clamp()` (see Modern CSS Defaults). Select font families based on product type — not Inter or Roboto unless explicitly requested. Include a distinctive display font recommendation.
- **Spacing:** 4pt base grid. Generate scale from 2px to 96px. Map to token names (2xs through 4xl).
- **Border radius:** Generate contextual scale (sharp for fintech, rounded for consumer, pill for playful).
- **Shadows:** Generate elevation scale (sm/md/lg/xl) tuned to the visual tone. Use `color-mix()` for shadow colors.

**Step 3 — Generate component patterns by product type:**
- **SaaS dashboard:** Data tables, stat cards, sidebar nav, command palette, filter bars
- **E-commerce:** Product cards, cart drawer, checkout flow, rating stars, price display
- **Content/blog:** Article layout, reading progress, TOC sidebar, author cards
- **Dev tools:** Code blocks, terminal output, diff views, status badges, log viewers
- **Social/community:** Feed cards, avatar groups, reaction bars, comment threads
- Match detected product type from design-context or memory-bank, generate relevant patterns

**Step 4 — Industry-specific recommendations:**
- **Fintech:** Conservative palette, high contrast, tabular number fonts, explicit error states
- **Healthcare:** Calming blues/greens, large touch targets (44px min), clear status indicators
- **Dev tools:** Dark mode first, monospace emphasis, dense information display, syntax highlighting tokens
- **Consumer SaaS:** Warm palette, generous whitespace, illustration-friendly, onboarding-focused
- **E-commerce:** High-contrast CTAs, trust signals, price hierarchy, urgency without anxiety

**Edge cases:**
- **style-guide/ partially exists:** Read existing files, create only missing ones
- **Mature design system detected:** Document it rather than inventing new patterns
- **No UI in project:** Create minimal skeleton, note that full guide is deferred
- **design-context.md exists:** Use it as primary source for brand decisions; override memory-bank defaults

---

## Operation: UPDATE

**Trigger:** "sg update", "sync style guide", or after significant UI changes.

1. Re-read memory-bank files and re-run auto-detection
2. Compare detected values against current style-guide files
3. Update changed files, preserve stable decisions and manual customizations
4. Add changelog entry at bottom of each modified file: `- [YYYY-MM-DD] Updated [section] from [source]`
5. Report changes and flag any conflicts

---

## Operation: TEACH

**Trigger:** `sg teach`, "teach brand context", "set design context", or when user provides brand/audience/tone information for persistent reuse.

The TEACH command captures design context once and stores it persistently so all future style guide operations and UI work can reference it without re-asking.

### Interview flow (ask only what is missing):

1. **Brand identity** — "What is the brand name? Describe it in one sentence."
2. **Industry/domain** — "What industry or product category? (e.g., fintech, healthcare SaaS, dev tools, e-commerce)"
3. **Target audience** — "Who are the primary users? Technical level, age range, context of use."
4. **Visual tone** — "Pick 3 adjectives for the visual feel. (e.g., minimal + warm + professional)"
5. **Personality** — "If the product were a person, how would they speak? (e.g., direct but friendly, formal and precise)"
6. **Existing brand assets** — "Any existing colors, fonts, or logos to respect? Paste hex codes or font names."
7. **Anti-references** — "Any products or styles you explicitly do NOT want to look like?"
8. **Platform targets** — "Primary platforms? (web desktop, mobile web, native app, all)"

### Storage:

Write answers to `style-guide/design-context.md`:

```markdown
# Design Context
<!-- Generated by /sg teach — [YYYY-MM-DD] -->
<!-- This file is read by all style-guide operations and UI generation tasks -->

## Brand
- Name: <brand name>
- One-liner: <one-sentence description>
- Industry: <industry/domain>

## Audience
- Primary: <user description, technical level, context>
- Platform: <web/mobile/native/all>

## Visual Direction
- Tone: <3 adjectives>
- Personality: <speaking style>
- Anti-references: <what to avoid>

## Existing Assets
- Colors: <hex codes or "none">
- Fonts: <font names or "none">
- Logo: <description or "none">

## Change Log
- [YYYY-MM-DD] Initial teach session
```

### Integration:

- **INIT** reads `style-guide/design-context.md` before memory-bank (takes precedence for brand-specific decisions)
- **UPDATE** re-reads design-context and flags if brand direction has changed
- **AUDIT** uses design-context to validate tone consistency in component patterns
- All UI generation tasks should read this file when it exists

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

## Anti-Pattern Database (AI Slop Detection)

When generating UI code, reviewing components, or running AUDIT, actively flag these patterns that signal AI-generated, generic, or low-effort design. These are not inherently wrong but become problems when applied without intention.

### Color anti-patterns
- **Cyan-on-dark (#00FFD1 / #0FF / cyan-400 on dark backgrounds):** The default "techy" AI palette. Use warmer or more muted accent colors unless the brand genuinely calls for it.
- **Purple-to-blue gradients (violet-600 to blue-500):** Overused in AI-generated hero sections and CTAs. If a gradient is needed, derive it from the brand palette, not from a generic purple-blue ramp.
- **Gradient text on metrics/numbers:** Applying `background-clip: text` gradients to dashboard numbers or KPIs. Use solid, high-contrast colors for data readability.
- **Neon glow effects (`box-shadow` with saturated cyan/purple):** Drop these unless the product is explicitly cyberpunk-themed.

### Typography anti-patterns
- **Inter or Roboto as default without reasoning:** These are fine fonts, but choosing them because they are the AI default is not a design decision. Select typography that matches the brand personality. Consider: Source Serif 4, DM Sans, Geist, Satoshi, General Sans, Cabinet Grotesk, or domain-appropriate alternatives.
- **Uniform font weight across all text:** AI tends to generate everything in regular (400) or medium (500). Use the full weight range: light for large display, semibold for labels, bold for headings.

### Layout anti-patterns
- **Identical card grids with uniform spacing:** Three cards in a row, all same height, same padding, same border-radius. Break the grid with varied card sizes, featured cards, or asymmetric layouts where appropriate.
- **Centered-everything layouts:** Centered headings, centered paragraphs, centered buttons. Left-align body text. Center only hero text, CTAs, and intentionally symmetric sections.
- **Hero section formula:** Large heading + subheading + two buttons (primary + ghost) + abstract gradient blob. If the hero looks like every SaaS landing page, rethink the layout.

### Animation anti-patterns
- **Bounce/elastic easing on everything (`cubic-bezier(0.68, -0.55, 0.27, 1.55)`):** Elastic easing is for playful micro-interactions, not for modals, dropdowns, or page transitions. Prefer ease-out for enters, ease-in for exits.
- **Fade-up on scroll for every section:** Entrance animations lose impact when every element does the same thing. Be selective — animate what matters.
- **Infinite shimmer on non-loading elements:** Skeleton shimmer is for loading states only.

### Component anti-patterns
- **Glassmorphism everywhere (`backdrop-blur` + semi-transparent backgrounds):** Use glass effects sparingly for overlays or floating elements, not as the default card style.
- **Oversized border-radius on containers (24px+):** Large radius works for cards and modals. It looks wrong on full-width sections, tables, or dense UI.
- **Icon-heavy interfaces with no text labels:** Icons alone are ambiguous. Pair with labels, especially on primary navigation.

### AUDIT integration
When running `sg audit`, add a **5. AI Slop check** that scans for these patterns:
- Grep for `#00FF`, `#0ff`, `cyan-400`, `cyan-500` in non-brand-approved contexts
- Grep for `backdrop-filter: blur` usage count — flag if >3 instances outside overlays
- Grep for `background-clip: text` on data display components
- Flag uniform `border-radius` values >20px on non-card elements
- Check animation easing values for elastic/bounce on non-micro-interaction elements

---

## Modern CSS Defaults

All generated CSS tokens and component styles should prefer modern CSS features. When the project supports them (check browserslist or build target), use these over legacy equivalents.

### OKLCH over HSL for color definitions

OKLCH provides perceptually uniform lightness, making color scales and accessible contrast calculations predictable. Generate all color tokens in OKLCH with hex fallbacks:

```css
:root {
  /* OKLCH: lightness (0-1), chroma (0-0.4), hue (0-360) */
  --color-primary: oklch(0.55 0.2 250);      /* hex fallback: #3b82f6 */
  --color-primary-light: oklch(0.85 0.08 250); /* hex fallback: #dbeafe */
  --color-primary-dark: oklch(0.35 0.2 250);   /* hex fallback: #1e40af */

  /* Generating accessible pairs: keep chroma, adjust lightness */
  --color-text-on-primary: oklch(0.98 0.01 250);
}
```

When building color scales, keep hue and chroma constant and step lightness evenly from 0.95 (50) to 0.25 (950). This produces visually consistent scales that HSL cannot achieve.

### Fluid typography with clamp()

Replace fixed font sizes and media-query breakpoints with fluid `clamp()` values. The formula is `clamp(min, preferred, max)` where preferred uses viewport units:

```css
:root {
  /* fluid type scale — no breakpoints needed */
  --text-xs:   clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-sm:   clamp(0.875rem, 0.8rem + 0.35vw, 1rem);
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg:   clamp(1.125rem, 0.95rem + 0.75vw, 1.375rem);
  --text-xl:   clamp(1.25rem, 1rem + 1.25vw, 1.75rem);
  --text-2xl:  clamp(1.5rem, 1.1rem + 2vw, 2.25rem);
  --text-3xl:  clamp(1.875rem, 1.2rem + 3.5vw, 3rem);
  --text-4xl:  clamp(2.25rem, 1.3rem + 5vw, 4rem);

  /* fluid spacing follows the same pattern */
  --space-sm:  clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-md:  clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg:  clamp(1.5rem, 1rem + 2.5vw, 3rem);
  --space-xl:  clamp(2rem, 1.2rem + 4vw, 4.5rem);
}
```

### Container queries over media queries

For component-level responsive behavior, prefer `@container` over `@media`. Components should respond to their container's size, not the viewport:

```css
.card-grid {
  container-type: inline-size;
}

@container (min-width: 600px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
}

@container (min-width: 900px) {
  .card-grid { grid-template-columns: repeat(3, 1fr); }
}
```

Reserve `@media` for page-level layout changes (sidebar collapse, navigation mode). Use `@container` for everything inside components.

### color-mix() for derived colors

Generate hover, active, and disabled states using `color-mix()` instead of separate tokens for every state:

```css
:root {
  --color-primary: oklch(0.55 0.2 250);
  --color-primary-hover: color-mix(in oklch, var(--color-primary) 85%, black);
  --color-primary-active: color-mix(in oklch, var(--color-primary) 75%, black);
  --color-primary-disabled: color-mix(in oklch, var(--color-primary) 40%, transparent);
  --color-primary-subtle: color-mix(in oklch, var(--color-primary) 10%, var(--color-surface));
}
```

### light-dark() for theme switching

Use `light-dark()` for tokens that change between color schemes, reducing duplication:

```css
:root {
  color-scheme: light dark;
  --color-surface: light-dark(oklch(0.99 0 0), oklch(0.15 0 0));
  --color-text: light-dark(oklch(0.2 0 0), oklch(0.9 0 0));
  --color-border: light-dark(oklch(0.85 0 0), oklch(0.3 0 0));
}
```

### Height animations with grid rows

Animate element height without knowing the content height, using `grid-template-rows`:

```css
.collapsible {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 300ms ease-out;
}

.collapsible[aria-expanded="true"] {
  grid-template-rows: 1fr;
}

.collapsible > .inner {
  overflow: hidden;
}
```

This replaces the `max-height` hack and works with unknown content heights. Use for accordions, expandable sections, and collapsible panels.

### Template integration

When generating `style-guide/colors.md`, use OKLCH as the primary format. When generating `style-guide/typography.md`, use `clamp()` for the type scale. When generating `style-guide/spacing-layout.md`, recommend container queries and fluid spacing. The animation template already covers easing; add the `grid-template-rows` pattern to `style-guide/animations.md`.

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
<!-- Format: OKLCH primary with hex fallbacks (see Modern CSS Defaults) -->

## Primary Palette
- Primary: oklch(<L> <C> <H>) / <hex> — main brand/action color
- Primary hover: color-mix(in oklch, var(--color-primary) 85%, black) / <hex>
- Primary light: oklch(<L+0.3> <C*0.4> <H>) / <hex> — backgrounds, subtle emphasis
- Secondary: oklch(<L> <C> <H>) / <hex> — supporting color
- Accent: oklch(<L> <C> <H>) / <hex> — highlights, badges

## Neutrals (OKLCH scale — constant hue, stepping lightness)
- White: oklch(0.99 0 0) / #ffffff
- Gray 50: oklch(0.97 0.005 <neutral-hue>) / <hex>
- Gray 100–800: <oklch per step, lightness from 0.93 to 0.30>
- Gray 900: oklch(0.25 0.005 <neutral-hue>) / <hex>
- Black: oklch(0.15 0 0) / <hex>

## Semantic Colors
- Success: oklch(<L> <C> <H>) / <hex> — confirmations, positive
- Warning: oklch(<L> <C> <H>) / <hex> — caution, pending
- Error: oklch(<L> <C> <H>) / <hex> — destructive, validation errors
- Info: oklch(<L> <C> <H>) / <hex> — informational

## Derived States (use color-mix instead of separate tokens)
- Hover: color-mix(in oklch, <base> 85%, black)
- Active: color-mix(in oklch, <base> 75%, black)
- Disabled: color-mix(in oklch, <base> 40%, transparent)
- Subtle: color-mix(in oklch, <base> 10%, var(--color-surface))

## Dark Mode (use light-dark() when supported)
- Background: light-dark(oklch(0.99 0 0), oklch(0.15 0 0))
- Surface: light-dark(oklch(0.97 0 0), oklch(0.20 0 0))
- Text primary: light-dark(oklch(0.20 0 0), oklch(0.93 0 0))
- Text secondary: light-dark(oklch(0.40 0 0), oklch(0.70 0 0))
- Border: light-dark(oklch(0.85 0 0), oklch(0.30 0 0))

## Usage Rules
- Minimum contrast: 4.5:1 normal text, 3:1 large text (WCAG AA)
- Never use color as sole state indicator — pair with icons/text
- Semantic colors must not be repurposed
- Use tokens/variables, never hardcoded hex in components
- Prefer OKLCH for new tokens; provide hex fallbacks for older browsers
- Use color-mix() for derived states instead of manual hex values

## Anti-patterns to avoid
- Cyan-on-dark (#00FFD1, #0FF) unless brand-approved
- Purple-to-blue gradients as default hero/CTA treatment
- Gradient text (background-clip: text) on data/metrics
- Neon glow box-shadows with saturated accent colors

## Migration Notes
- <legacy value>: replace with <token>
```

### style-guide/typography.md

```markdown
# Typography System
<!-- Source: [detected — e.g., tailwind config, Google Fonts import] -->
<!-- Format: Fluid clamp() values (see Modern CSS Defaults) -->

## Font Families
- Primary: <font> — <fallback stack>
- Display: <font> — <fallback stack> (headings, hero text — optional but recommended)
- Monospace: <font> — <fallback stack>
- NOTE: Avoid Inter/Roboto as defaults unless they match the brand. Consider: DM Sans, Geist, Satoshi, General Sans, Cabinet Grotesk, Source Serif 4, or domain-appropriate alternatives.

## Type Scale (fluid with clamp)
- H1: clamp(2.25rem, 1.3rem + 5vw, 4rem) / 1.1 / 700 — page titles
- H2: clamp(1.875rem, 1.2rem + 3.5vw, 3rem) / 1.2 / 600 — section headings
- H3: clamp(1.5rem, 1.1rem + 2vw, 2.25rem) / 1.25 / 600 — subsection headings
- H4: clamp(1.25rem, 1rem + 1.25vw, 1.75rem) / 1.3 / 600 — card titles
- H5: clamp(1.125rem, 0.95rem + 0.75vw, 1.375rem) / 1.4 / 600 — small headings
- Body: clamp(1rem, 0.9rem + 0.5vw, 1.125rem) / 1.6 / 400 — standard text
- Body small: clamp(0.875rem, 0.8rem + 0.35vw, 1rem) / 1.5 / 400 — secondary info
- Label: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem) / 1.4 / 500 — buttons, form labels, tags
- Caption: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem) / 1.3 / 400 — timestamps, metadata

## Rules
- Minimum body text: 16px (1rem) at any viewport
- Max line length: 65-75 characters for body (use ch unit: max-width: 70ch)
- Sequential heading hierarchy (no skipping levels)
- Use clamp() for fluid sizing; no media query breakpoints for font sizes
- Use rem in implementation, document px for design reference
- Use the full weight range: light (300) for large display, regular (400) for body, semibold (600) for labels, bold (700) for headings

## Prohibitions
- No unauthorized font families
- No font sizes outside the scale
- No uniform font weight across all text (vary weight by purpose)
- No fixed px font sizes where clamp() is available
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

## Fluid Spacing (use clamp for responsive values)
- --space-sm: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem)
- --space-md: clamp(1rem, 0.8rem + 1vw, 1.5rem)
- --space-lg: clamp(1.5rem, 1rem + 2.5vw, 3rem)
- --space-xl: clamp(2rem, 1.2rem + 4vw, 4.5rem)

## Usage Rules
- Inside components: use smaller tokens (2xs–sm)
- Between components: use medium tokens (md–xl)
- Between sections: use large tokens (xl–3xl)
- No arbitrary pixel values — always use the scale
- Use @container queries for component-level responsive behavior
- Reserve @media queries for page-level layout changes only

## Container Queries (prefer over media queries for components)
- Wrap component containers with `container-type: inline-size`
- Use `@container (min-width: Xpx)` for responsive component layouts
- Components should respond to their container, not the viewport

## Prohibitions
- Hardcoded one-off spacing values
- @media queries inside component styles (use @container instead)
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
- All 8 files exist in `style-guide/` (7 templates + design-context.md if /sg teach was run)
- Templates populated with project-specific data (not all placeholders)
- Colors use OKLCH format with hex fallbacks
- Typography uses fluid clamp() values
- Memory-bank warning shown if missing
- Detection sources listed in report
- Anti-pattern checks noted in report if any detected

**UPDATE complete when:**
- Changed decisions synchronized across files
- Each modified file has changelog entry
- Conflicts flagged to user
- design-context.md changes reflected in dependent files

**AUDIT complete when:**
- Findings grouped by severity with file:line + rule + fix
- AI slop check included (check #5)
- Or explicit "No violations detected" if clean

**TEACH complete when:**
- `style-guide/design-context.md` written with all answered fields
- Unanswered fields marked with `<!-- PENDING: ask user -->`
- Confirmation shown: which fields captured, which still need input
