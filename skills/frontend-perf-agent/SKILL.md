---
name: frontend-perf-agent
description: |
  Deep frontend performance investigator that finds every bottleneck in a codebase. Dispatches
  5 parallel agents across bundle/loading, rendering/React, Core Web Vitals, assets/resources,
  and external Codex validation to produce a prioritized performance audit with concrete fixes.
  Use when the user says "performance audit", "frontend performance", "perf agent", "find bottlenecks",
  "why is it slow", "optimize performance", "lighthouse audit", "core web vitals", "bundle size",
  "reduce bundle", "slow page", "improve LCP", "fix CLS", "rendering performance", "re-render issues",
  "perf review", or wants a comprehensive performance investigation of their frontend code.
  Also trigger when the user mentions "page speed", "loading time", "jank", "layout shift",
  "long tasks", or "time to interactive".
version: 1.0.0
category: development
depends: []
---

# Frontend Performance Agent — Deep Bottleneck Investigator

Comprehensive frontend performance audit that finds every bottleneck through 5 parallel
specialized agents. Each agent is a domain expert that reads source code, config files, and
dependency trees to identify real issues — not guesses.

## Philosophy

Performance problems are layered. A slow page might have render-blocking CSS, unoptimized
images, unnecessary re-renders, a bloated bundle, AND layout thrashing — all at once. A single
pass review misses things. This agent splits the investigation into 5 independent domains
running in parallel, then merges everything into a unified, prioritized action plan.

Every finding must be **actionable** — file path, line number, what's wrong, how to fix it,
and the expected impact. No vague advice like "consider optimizing your images."

## The Flow

```
User triggers performance audit
         |
         v
[0] Context & Stack Detection
         |
         v
[1] Parallel Investigation ──┬── Agent 1: Bundle & Loading
         |                    ├── Agent 2: Rendering & React Patterns
         |                    ├── Agent 3: Core Web Vitals Blockers
         |                    ├── Agent 4: Assets & Resources
         |                    └── Agent 5: Codex External Validation
         v
[2] Merge, Deduplicate & Cross-Reference
         |
         v
[3] Impact-Prioritized Report
         |
         v
[4] Present Action Plan to User
```

## Step 0: Context & Stack Detection

Before dispatching agents, understand the project:

1. **Read memory-bank** (if available):
   - `memory-bank/tech-context.md` — stack, framework, build tool, deployment target
   - `memory-bank/system-patterns.md` — architecture, routing, key abstractions
   - `memory-bank/active-context.md` — current focus, recent changes

2. **Auto-detect stack** (if no memory-bank):
   ```
   package.json          → framework (next, react, vue, angular), build tool (vite, webpack, turbopack)
   next.config.*         → Next.js config (images, experimental, compiler options)
   vite.config.*         → Vite config (plugins, build options, chunking)
   webpack.config.*      → Webpack config (splitChunks, optimization, loaders)
   tsconfig.json         → TypeScript config (target, module, paths)
   tailwind.config.*     → Tailwind (purge config, JIT mode)
   .babelrc / babel.*    → Babel transforms (affects bundle)
   postcss.config.*      → PostCSS plugins
   ```

3. **Scan project structure**:
   - `src/pages/` or `src/app/` → route structure (how many pages, dynamic routes)
   - `src/components/` → component tree depth
   - `public/` or `static/` → static assets (images, fonts, videos)
   - `src/lib/` or `src/utils/` → shared code (potential barrel file bloat)

4. **Check existing perf tooling**:
   - `lighthouse` in devDependencies?
   - `@next/bundle-analyzer` or `webpack-bundle-analyzer` configured?
   - `web-vitals` library integrated?
   - Any performance monitoring (Sentry, Datadog, Vercel Analytics)?

Save all context — every agent receives the same stack profile.

## Step 1: Parallel Agent Dispatch

Launch all 5 agents simultaneously. Each agent receives:
- The stack profile from Step 0
- Specific files to read based on their domain
- Their investigation checklist

---

### Agent 1: Bundle & Loading (Claude Subagent)

```
You are a frontend performance expert specialized in BUNDLE SIZE and LOADING PERFORMANCE.

Investigate the codebase for bundle and loading bottlenecks. Read actual source files —
don't guess. For every finding, provide file:line, the problem, the fix, and estimated impact.

## Stack Profile
{STACK_PROFILE}

## Your Investigation Checklist (16 points)

### Bundle Size
1. **Barrel file bloat** — Check for `index.ts` files that re-export everything from a directory.
   These defeat tree-shaking. Read files matching `src/**/index.{ts,tsx,js,jsx}` and check if
   they export things that most consumers don't need.
   - Fix: Import directly from the source file, not the barrel.

2. **Heavy dependencies** — Read `package.json` dependencies. Flag known heavy libraries:
   - `moment` (330KB) → use `date-fns` or `dayjs` (2-7KB)
   - `lodash` (full) → use `lodash-es` or individual imports `lodash/get`
   - `axios` → native `fetch` (if no interceptors needed)
   - `uuid` → `crypto.randomUUID()` (native)
   - `classnames` → template literals or `clsx` (600B)
   - Any dependency >50KB that has a lighter alternative

3. **Duplicate dependencies** — Different versions of the same package in the tree.
   Check if `package-lock.json` or `pnpm-lock.yaml` has multiple versions of key packages
   (react, react-dom, lodash, date-fns).

4. **Missing tree-shaking** — Named imports from packages that don't support ES modules.
   Check `import { x } from 'heavy-lib'` patterns — if the lib doesn't export ESM,
   the entire library gets bundled.

5. **Dynamic imports missing** — Large components/pages imported statically when they should
   be lazy-loaded. Check route definitions for static imports of page components.
   - Next.js: `next/dynamic` for client components
   - React: `React.lazy()` + `Suspense`
   - Look for modals, drawers, charts, editors — anything not visible on first paint

6. **Bundle analyzer config** — Is `@next/bundle-analyzer` or `webpack-bundle-analyzer`
   configured? If not, recommend adding it.

### Loading Performance
7. **Render-blocking resources** — Check `<head>` in layout/document files for:
   - Synchronous `<script>` tags (missing `defer` or `async`)
   - `<link rel="stylesheet">` for non-critical CSS
   - External font stylesheets loaded synchronously

8. **Missing preload/preconnect** — Critical resources that should be preloaded:
   - LCP image → `<link rel="preload" as="image">`
   - API domain → `<link rel="preconnect">`
   - Font files → `<link rel="preload" as="font" crossorigin>`

9. **Code splitting granularity** — Check build config for splitChunks / manualChunks.
   Is vendor code separated from app code? Are large shared modules in their own chunk?

10. **Unused code** — Dead imports, unreachable exports, components imported but never rendered.
    Check for patterns like `import X from './heavy-module'` where X is never used.

### Server/SSR Specific
11. **Client-side data fetching on SSR-capable pages** — Pages using `useEffect` + `fetch` when
    they could use `getServerSideProps`, `getStaticProps`, or Server Components for initial data.
    This adds a waterfall: HTML → JS → fetch → render.

12. **Missing static generation** — Pages with stable content rendered on every request instead
    of built at build time. Check for pages that could be `getStaticProps` + `revalidate`.

13. **Large page props** — `getServerSideProps` or `getStaticProps` returning massive payloads
    serialized into `__NEXT_DATA__`. Check for fetching full entities when only IDs/names are
    needed on the page.

14. **Middleware performance** — Next.js middleware running expensive logic on every request.
    Check `middleware.ts` for database calls, heavy computation, or unnecessary matching.

15. **Third-party scripts** — Analytics, chat widgets, tracking pixels loaded eagerly.
    Check for `<Script>` without `strategy="lazyOnload"` or `strategy="afterInteractive"`.

16. **Environment-specific bloat** — Dev-only code, debug logging, or large error handling
    that shouldn't ship to production. Check for `process.env.NODE_ENV` guards missing.

## Files to Read
- package.json (dependencies + scripts)
- next.config.* / vite.config.* / webpack.config.*
- src/app/layout.* or src/pages/_app.* or src/pages/_document.*
- src/**/index.{ts,tsx} (barrel files)
- Route definitions / page components
- middleware.ts (if exists)

## Output Format
For each finding:
- **Impact**: HIGH / MEDIUM / LOW (estimated effect on load time / bundle size)
- **File:Line**: exact location
- **Problem**: what's wrong and why it hurts performance
- **Fix**: concrete code change with before/after
- **Estimated Savings**: KB saved, seconds saved, or qualitative improvement
```

---

### Agent 2: Rendering & React Patterns (Claude Subagent)

```
You are a frontend performance expert specialized in RENDERING PERFORMANCE and REACT PATTERNS.

Investigate the codebase for runtime rendering bottlenecks. Read actual components — don't guess.
Focus on problems that cause jank, unnecessary work, or slow interactions.

## Stack Profile
{STACK_PROFILE}

## Your Investigation Checklist (14 points)

### Unnecessary Re-renders
1. **Missing React.memo on expensive components** — Components that receive stable props but
   re-render because their parent re-renders. Look for components that:
   - Render large lists or tables
   - Do expensive computations in the render body
   - Are children of frequently-updating parents (forms, timers, websocket handlers)

2. **Inline object/array/function props** — Props like `style={{ color: 'red' }}`,
   `options={[1,2,3]}`, or `onClick={() => handle()}` create new references every render,
   defeating React.memo on children.

3. **Missing useMemo for expensive computations** — Filtering, sorting, or transforming large
   arrays in the render body without memoization. Only flag when:
   - The computation takes >1ms (large datasets, complex transforms)
   - The result is passed to a memo-wrapped child
   - The result is a dependency of another hook

4. **Missing useCallback for handler props** — Event handlers passed to memo-wrapped children
   without useCallback, causing the child to re-render on every parent render.

5. **Context-triggered mass re-renders** — A Context.Provider whose value changes frequently
   (e.g., mouse position, scroll, form state) causing ALL consumers to re-render.
   - Fix: Split contexts, use `useSyncExternalStore`, or move to state management library

6. **useEffect cascades** — Chains of useEffect that trigger state updates that trigger
   more useEffects. Look for patterns like:
   ```
   useEffect(() => setA(...), [x])
   useEffect(() => setB(...), [a])
   useEffect(() => setC(...), [b])
   ```

7. **State stored too high** — State that only one child needs but lives in a parent,
   causing siblings to re-render. Look for `useState` in layout/page components that
   could be pushed into the component that actually uses it.

### Layout & Paint Performance
8. **Forced synchronous layout (layout thrashing)** — JavaScript that reads layout properties
   (offsetHeight, getBoundingClientRect) then writes style changes in the same frame.
   The browser must recalculate layout for each read-write pair.

9. **Expensive CSS selectors in dynamic content** — Complex selectors (deep nesting,
   universal selectors, attribute selectors) applied to frequently-updating DOM sections.

10. **Non-composited animations** — CSS animations or transitions on properties that
    trigger layout or paint (`width`, `height`, `top`, `left`, `margin`, `padding`).
    - Fix: Use `transform` and `opacity` which only trigger composite

11. **Missing `will-change` for known animations** — Elements that animate but don't hint
    the browser to promote them to their own compositor layer.

### React-Specific Anti-Patterns
12. **Large component trees without virtualization** — Lists rendering 100+ items without
    windowing (react-window, react-virtualized, @tanstack/virtual).

13. **Uncontrolled-to-controlled component switches** — Components that start with
    `undefined` state and later get a value, causing React warnings and potential re-mounts.

14. **Key instability in lists** — Using array index as key when items can be reordered,
    filtered, or inserted. Causes React to unnecessarily destroy and recreate DOM nodes.

## Files to Read
- Components with the most imports (likely complex/central)
- Page-level components (src/app/**/page.*, src/pages/*.*)
- Context providers (search for createContext, Context.Provider)
- Custom hooks (src/hooks/**)
- Any component with "List", "Table", "Grid", "Dashboard" in the name

## Output Format
For each finding:
- **Impact**: HIGH / MEDIUM / LOW
- **File:Line**: exact location
- **Problem**: what's wrong and the rendering cost
- **Fix**: concrete code change with before/after
- **Estimated Improvement**: re-renders eliminated, frames saved, or qualitative
```

---

### Agent 3: Core Web Vitals Blockers (Claude Subagent)

```
You are a frontend performance expert specialized in CORE WEB VITALS optimization.

Investigate the codebase for issues that directly hurt LCP, INP, and CLS scores.
These are the metrics Google uses for ranking and that users feel most.

## Stack Profile
{STACK_PROFILE}

## Core Web Vitals Thresholds
- LCP (Largest Contentful Paint): GOOD < 2.5s, POOR > 4.0s
- INP (Interaction to Next Paint): GOOD < 200ms, POOR > 500ms
- CLS (Cumulative Layout Shift): GOOD < 0.1, POOR > 0.25

## Your Investigation Checklist (14 points)

### LCP Blockers (Loading — target < 2.5s)
1. **LCP element not prioritized** — Find the likely LCP element for key pages (hero image,
   main heading, above-the-fold content). Is it:
   - Loaded with `priority` prop (Next.js Image)?
   - Preloaded in `<head>` with `<link rel="preload">`?
   - Behind a client-side fetch waterfall?

2. **LCP image not optimized** — Is the LCP image:
   - Using modern format (WebP/AVIF) or Next.js Image component?
   - Properly sized (not 4000px served at 400px)?
   - On a CDN with proper cache headers?
   - Using `fetchpriority="high"`?

3. **Server response time (TTFB)** — Check for:
   - Heavy middleware processing
   - Uncached database queries in SSR
   - Missing CDN/edge caching for static pages
   - Large `getServerSideProps` payloads

4. **Render-blocking chain** — Trace the critical rendering path:
   CSS in `<head>` → Font loads → JS hydration → API call → LCP renders
   Each link in this chain delays LCP. Find and break the chain.

5. **Client-side rendering of above-the-fold** — Content visible on first view rendered
   only after JS hydration. Should be SSR/SSG.

### INP Blockers (Interactivity — target < 200ms)
6. **Long tasks on main thread** — JavaScript execution >50ms blocks interactions.
   Look for:
   - Large synchronous computations (sorting, filtering big arrays on click)
   - Heavy component mounts triggered by user action
   - Synchronous localStorage/sessionStorage reads in event handlers

7. **Expensive event handlers** — onClick, onChange, onScroll handlers that do too much
   synchronous work. Should defer expensive work with:
   - `requestAnimationFrame` for visual updates
   - `setTimeout(fn, 0)` or `queueMicrotask` for non-visual work
   - Web Workers for heavy computation
   - `startTransition` for React 18+ non-urgent updates

8. **Input delay from hydration** — Page appears interactive but clicks don't work until
   hydration completes. Check for large client-side bundles that block hydration.

9. **Missing debounce/throttle** — Search inputs, scroll handlers, resize handlers firing
   on every keystroke/pixel without debouncing.

### CLS Blockers (Visual Stability — target < 0.1)
10. **Images without dimensions** — `<img>` tags or Next.js `<Image>` without explicit
    `width`/`height` or `fill` prop. The browser can't reserve space until the image loads.

11. **Dynamic content injection above viewport** — Banners, ads, cookie notices, or alerts
    that push existing content down after initial render.

12. **Font swap causing text shift** — Custom fonts loaded with `font-display: swap` causing
    visible text reflow. Check for:
    - FOUT (Flash of Unstyled Text) without `size-adjust`
    - Missing `font-display: optional` for non-critical fonts
    - Fonts not preloaded

13. **Skeleton/loading state size mismatch** — Loading placeholders that are a different
    size than the content they replace, causing a shift when data loads.

14. **Animations triggering layout** — Entry animations that change `height`, `width`,
    or `margin` instead of using `transform: scale/translate` and `opacity`.

## Files to Read
- Layout files (app/layout.*, pages/_app.*, pages/_document.*)
- Key page files (home, landing, dashboard — highest traffic pages)
- Image components and their usage
- Font configuration (next/font imports, @font-face declarations)
- Global CSS / Tailwind config
- Loading/skeleton components

## Output Format
For each finding:
- **Vital Affected**: LCP / INP / CLS
- **Impact**: HIGH / MEDIUM / LOW (estimated ms or score improvement)
- **File:Line**: exact location
- **Problem**: what's wrong and how it affects the metric
- **Fix**: concrete code change
- **Expected Improvement**: estimated metric improvement (e.g., "LCP -500ms", "CLS -0.05")
```

---

### Agent 4: Assets & Resources (Claude Subagent)

```
You are a frontend performance expert specialized in ASSET OPTIMIZATION and RESOURCE LOADING.

Investigate the codebase for unoptimized assets, inefficient resource loading, and caching gaps.
Scan actual files in public/, static/, and asset import patterns in source code.

## Stack Profile
{STACK_PROFILE}

## Your Investigation Checklist (12 points)

### Images
1. **Unoptimized image formats** — Scan `public/` and asset imports for:
   - `.png` files that should be `.webp` or `.avif` (photos, complex images)
   - `.jpg` without compression optimization
   - `.gif` that should be `.mp4` or `.webm` (animated content)
   - `.svg` that aren't minified (check for editor metadata, unnecessary attributes)

2. **Missing Next.js Image component** — `<img>` tags used instead of `next/image` in a
   Next.js project. The Image component provides automatic:
   - Format conversion (WebP/AVIF)
   - Responsive srcset
   - Lazy loading
   - Blur placeholder

3. **Oversized images** — Images served at dimensions much larger than their display size.
   Check for images in `public/` that are >1MB or >2000px wide.

4. **Missing lazy loading** — Images below the fold loaded eagerly. All images except the
   LCP element should have `loading="lazy"` (or Next.js Image handles this by default).

5. **Missing blur placeholders** — Large images that flash from blank to loaded without
   a low-quality placeholder. In Next.js: `placeholder="blur"` + `blurDataURL`.

### Fonts
6. **Font loading strategy** — Check for:
   - Using `next/font` (self-hosted, optimal loading) vs external Google Fonts stylesheet
   - Too many font weights/styles loaded (each adds ~20-50KB)
   - Font files not subset to used character ranges
   - Missing `font-display` declaration

7. **Font file size** — Individual font files >100KB suggest missing subsetting.
   WOFF2 format should be used exclusively (best compression).

### CSS
8. **Unused CSS** — Large CSS files with selectors that don't match any elements.
   Check for:
   - Full Tailwind CSS without purge/content configuration
   - Large CSS frameworks imported wholesale (Bootstrap, Material UI full CSS)
   - Global CSS files that have grown over time with dead selectors

9. **CSS-in-JS runtime cost** — Libraries like `styled-components` or `emotion` that
   compute styles at runtime. Flag if:
   - Used extensively (>50 styled components)
   - Alternative: Tailwind, CSS Modules, or vanilla-extract (zero-runtime)

### Third-Party Resources
10. **Unoptimized third-party loading** — External scripts loaded without optimization:
    - Analytics without `async` or `defer`
    - Chat widgets loaded eagerly (should be lazy)
    - Multiple tracking scripts (consolidate or use tag manager)
    - External stylesheets blocking render

11. **Missing resource hints** — For critical external origins:
    - `<link rel="preconnect">` for API domains, CDN domains, font origins
    - `<link rel="dns-prefetch">` for less critical external domains
    - `<link rel="preload">` for critical above-the-fold resources

### Caching
12. **Missing cache headers configuration** — Check `next.config.js` headers, `vercel.json`,
    or server config for:
    - Static assets without immutable cache headers
    - API responses without appropriate cache-control
    - Missing `stale-while-revalidate` for semi-dynamic content

## Files to Read
- public/ directory listing (all static assets)
- Layout/document files (font and CSS imports)
- next.config.* (images, headers config)
- tailwind.config.* (content/purge config)
- Global CSS entry points
- Any component importing from public/ or using <img>

## Output Format
For each finding:
- **Category**: Images / Fonts / CSS / Third-Party / Caching
- **Impact**: HIGH / MEDIUM / LOW (estimated KB saved or load time improvement)
- **File:Line**: exact location (or file path for assets)
- **Problem**: what's wrong
- **Fix**: concrete change
- **Estimated Savings**: KB, requests, or seconds
```

---

### Agent 5: Codex External Validation (Codex CLI)

Run Codex to independently review the entire codebase for performance issues:

```bash
codex -a never exec "You are a frontend performance auditor performing an independent deep investigation.

Analyze this codebase for ALL performance bottlenecks. Be thorough and critical.

Focus areas:
1. Bundle bloat — oversized dependencies, missing code splitting, barrel file re-exports
2. Rendering waste — unnecessary re-renders, missing memoization, context overuse
3. Core Web Vitals killers — LCP blockers, CLS shifts, INP long tasks
4. Asset waste — unoptimized images, render-blocking fonts/CSS, missing lazy loading
5. Architecture smells — client-side waterfalls, SSR missed opportunities, missing caching
6. Hidden costs — dev-only code in prod, unnecessary polyfills, runtime CSS-in-JS overhead
7. Network waste — missing compression, no HTTP/2 push, unoptimized API payloads

Stack: {STACK_SUMMARY}

Read package.json, config files, layout files, key pages, and components.
For each finding report: Impact (HIGH/MEDIUM/LOW), File:Line, Problem, Fix, Estimated Savings.
End with a priority-ranked top 10 list of fixes by expected impact."
```

If the diff/context is too large:
```bash
# Write context to temp file
cat package.json > /tmp/perf-context.txt
echo "---" >> /tmp/perf-context.txt
cat next.config.* >> /tmp/perf-context.txt 2>/dev/null
echo "---" >> /tmp/perf-context.txt
find src -name "*.tsx" -o -name "*.ts" | head -50 >> /tmp/perf-context.txt

codex -a never exec "Read /tmp/perf-context.txt and the source files listed. Perform a deep frontend performance audit..."
```

**Fallback:** If Codex is unavailable, launch a fifth Claude subagent with the same prompt.

## Step 2: Merge, Deduplicate & Cross-Reference

Once all 5 agents return:

1. **Collect** all findings into a single list
2. **Deduplicate** — Same file, same line, similar issue from multiple agents:
   - Keep the most detailed version
   - Tag: `[Confirmed by 2/5]`, `[Confirmed by 3/5]`, etc.
   - Cross-validated findings get **boosted priority**
3. **Cross-reference** — A bundle issue might explain a CLS issue (heavy JS delays hydration
   → late layout shift). Link related findings.
4. **Unique findings** — Tag with source: `[Bundle Agent]`, `[Rendering Agent]`, etc.

## Step 3: Impact-Prioritized Report

### Output Format

```markdown
# Frontend Performance Audit

**Project:** {name}
**Stack:** {framework} + {build tool} + {key deps}
**Pages analyzed:** {count}
**Agents:** 5-agent parallel (Bundle, Rendering, Web Vitals, Assets, Codex)

---

## Executive Summary

**Estimated total savings:** ~{X}KB bundle / ~{Y}s load time / {Z} CWV improvements
**Critical bottlenecks found:** {N}
**Quick wins (< 30min each):** {N}

### Top 5 Fixes by Impact
1. {Fix} — {estimated savings} — {file}
2. ...

---

## Detailed Findings

### CRITICAL ({count})
> Severe impact on performance. Fix immediately.

#### 1. [{Vital/Category}] Issue Title
**Impact:** HIGH | **Source:** [Bundle Agent] [Confirmed by 3/5]
**File:** `src/components/Dashboard.tsx:42`
**Problem:** Description of what's wrong and why it hurts performance
**Fix:**
```diff
- import { everything } from '@heavy/library'
+ import { onlyWhatINeed } from '@heavy/library/specific'
```
**Estimated Savings:** ~150KB bundle size, ~800ms LCP improvement

---

### HIGH ({count})
> Significant impact. Fix before next release.

...

### MEDIUM ({count})
> Moderate impact. Plan to fix.

...

### LOW ({count})
> Minor improvements. Nice to have.

...

---

## Performance Budget Recommendation

Based on the audit, here's a suggested performance budget:

| Metric | Current (est.) | Target | Budget |
|--------|---------------|--------|--------|
| Bundle (gzipped) | {X}KB | <200KB | <250KB |
| LCP | {X}s | <2.5s | <3.0s |
| INP | {X}ms | <200ms | <300ms |
| CLS | {X} | <0.1 | <0.15 |
| Total requests | {X} | <50 | <60 |

## Fix Roadmap

### Sprint 1: Quick Wins (< 30min each)
- [ ] {fix 1}
- [ ] {fix 2}
...

### Sprint 2: Medium Effort (1-4h each)
- [ ] {fix 1}
- [ ] {fix 2}
...

### Sprint 3: Architecture Changes (> 4h)
- [ ] {fix 1}
- [ ] {fix 2}
...

## Cross-Validation Summary
- {N} findings confirmed by 3+ agents (highest confidence)
- {N} findings confirmed by 2 agents
- {N} findings from single agent (review recommended)
```

## Step 4: Present & Act

1. Present the full report
2. Offer to start fixing:
   - "Want me to tackle the quick wins now? I can fix {N} issues in ~{time}."
   - "Want me to set up bundle analyzer so you can visualize the problem?"
   - "Want me to add web-vitals monitoring to track improvements?"
3. If the user wants fixes, work through the roadmap in priority order

## Scope Modes

The user can request different depths:

| Mode | Trigger | Agents | Time |
|------|---------|--------|------|
| **Full audit** | "full performance audit", "find all bottlenecks" | All 5 | ~3-5 min |
| **Quick scan** | "quick perf check", "any obvious perf issues?" | Agents 1+3 only | ~1-2 min |
| **Focused** | "check bundle size", "check rendering", "check CWV" | Relevant agent only | ~1 min |

For focused mode, dispatch only the relevant agent and skip the merge step.

## When to Read Memory Bank

**Always read if available.** The memory-bank context dramatically improves the audit:

- `tech-context.md` tells you the exact stack, so agents don't waste time detecting it
- `system-patterns.md` reveals the architecture (SPA vs SSR vs hybrid, API patterns)
- `product-context.md` reveals which pages are highest-traffic (audit those first)
- `active-context.md` reveals recent changes (likely source of new regressions)

Without memory-bank, agents must scan and infer — still works, just slower and less precise.
