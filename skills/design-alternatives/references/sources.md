# Research Sources — design-alternatives skill

Compiled 2026-07-09 from a 3-thread web research pass (31 sources read) plus an audit of
the last ~25 PRs of a production web app. Condensed here so future skill iterations can revisit the
evidence without re-researching.

## AI design skills & tooling

1. **Anthropic `frontend-design` skill** — https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md
   Names the three "AI default" aesthetics and bans them as defaults; two-pass method
   (token plan → self-critique → build); ground choices in the subject's own world;
   "spend your boldness in one place"; copy is design material.
2. **Anthropic `web-artifacts-builder` skill** — https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md
   Single-file self-contained HTML artifact tooling; hard-ban list: "excessive centered
   layouts, purple gradients, uniform rounded corners, Inter font".
3. **awesome-claude-skills** — https://github.com/travisvn/awesome-claude-skills
   Ecosystem pattern: design skills are knowledge-injection (rules, tokens, component
   docs), incl. official shadcn/ui skill (https://ui.shadcn.com/docs/skills).
4. **superdesign blog: Why AI Design Looks Generic** — https://superdesign.dev/blog/why-ai-design-looks-generic
   "Distributional convergence" root cause; fix = separate taste direction / visual
   exploration / implementation spec; reference feeding; adjective-feedback diagnostic.
5. **superdesign (tool)** — https://github.com/superdesigndev/superdesign
   Parallel UI variations on an infinite canvas, stored as local HTML mockups in
   `.superdesign/` — validates "alternatives as throwaway HTML".
6. **vibecodekit: AI Slop Design Fix Guide** — https://vibecodekit.dev/ai-slop-design
   Slop-tells catalog; DESIGN.md lock-in at project root; 3-hue cap (60/30/10); type
   scale ratios; borderless hierarchy ladder; 8pt grid; APCA targets; squint test.
7. **Roger Wong: Beyond the Prompt** — https://rogerwong.me/2025/04/beyond-the-prompt
   8-tool bake-off; Subframe won via MidJourney-style "four coded options in miniature"
   → pick a direction before committing. Simultaneous comparison beats sequential.
8. **Alex Lavaee: Why My AI-Generated UI Looked Generic** — https://alexlavaee.me/blog/lessons-learned-designing-with-ai/
   `research/designs` sandbox of standalone mockups; narrow sequential commands beat
   one mega-prompt; machine-readable design language; decompress generation into phases.
9. **UI/UX Pro Max writeup** — https://medium.com/@abhinav.dobhal/the-end-of-ai-slop-how-ui-ux-pro-max-is-solving-the-design-crisis-in-ai-generated-code-bbc23995f0e0
   67 named UI styles (naming a style gives the model a concrete distribution); industry
   guardrails; hierarchical MASTER.md + per-page overrides.
10. **Vercel: Figma & custom design systems in v0** — https://vercel.com/blog/working-with-figma-and-custom-design-systems-in-v0
    Anchor generation to real artifacts (Figma frames, Tailwind config as token source);
    v0's sequential history is the weaker comparison model vs side-by-side.

## Intentional UI best practices

11. **Refactoring UI (Wathan/Schoger)** — https://refactoringui.com/
    Hierarchy via de-emphasis; grayscale-first; defined spacing/type scales (≥25% jumps);
    3-tier buttons; destructive ≠ automatically red-bold; 8-10 grays, never true black.
12. **Emil Kowalski design-eng reference** — https://github.com/emilkowalski/skills/blob/main/skills/emil-design-eng/SKILL.md
    Animate by frequency, not taste; numeric duration table (≤300ms everyday UI); easing
    decision tree; `prefers-reduced-motion`; transform/opacity only.
13. **NN/g: Empty States** — https://www.nngroup.com/articles/empty-state-interface-design/
    Empty state = status + teach + direct CTA; loading must never masquerade as no-data.
14. **NN/g: Progressive Disclosure** — https://www.nngroup.com/articles/progressive-disclosure/
    Primary/secondary split by task frequency; max 2 disclosure levels.
15. **Linear: Why Is Quality So Rare?** — https://linear.app/now/why-is-quality-so-rare
    Quality as a per-decision filter, not a polish pass; craft is the differentiator in
    the AI era.
16. **Karri Saarinen's 10 rules (Figma blog)** — https://www.figma.com/blog/karri-saarinens-10-rules-for-crafting-products-that-stand-out/
    "The spec is the baseline, not the finish line"; specificity is the anti-generic
    mechanism; reduce scope to increase quality.
17. **The shadcn Trap** — https://freedesignmd.com/blog/shadcn-looks-generic
    Generic = accepted defaults, tokens are the fix ("tokens move every screen at once");
    5 de-genericizing token changes; design.md consumed by agent instructions; tweakcn.
18. **Practical UI (Dannaway)** — https://www.practical-ui.com/
    Logic-driven design (every detail has an articulable reason); one interactive color;
    ≥48px targets; spacing in 4/8 multiples.
19. **Imperavi: Semantic Colors** — https://imperavi.com/blog/designing-semantic-colors-for-your-system/
    Primitives → semantic → component token layers; name by purpose, never pigment;
    start minimal and grow.
20. **Vercel Geist** — https://vercel.com/geist/introduction
    Identity through owned constraints; materials as presets (arbitrary per-screen
    choices structurally removed).

## Design-first workflows & decision capture

21. **Crazy 8s — Open Practice Library** — https://openpracticelibrary.com/practice/crazy-8s/
    Time-boxed forced breadth → structured presentation → dot-vote → ONE consolidated
    concept; hybrid/merge outcomes are normal and must be captured.
22. **Style Tiles** — http://styletil.es/
    Decouple "which visual direction" from "which layout"; iterate on the cheap axis;
    Listen → Interpret → Define → Iterate.
23. **Logo Design Love: How many options** — https://www.logodesignlove.com/how-many-options
    "Best three: one safe, one adventurous, one scary"; too many options →
    frankensteining; alternatives differ in risk/strategy.
24. **Designer's Field Guide: design alternatives sustainably** — https://thedesignersfieldguide.substack.com/p/how-to-approach-creating-design-alternatives
    Each alternative = distinct strategic approach anchored to the problem statement;
    without explicit rationale, options are indistinguishable from AI variant spam.
25. **Max Böck: Prototyping an App in Static HTML** — https://mxb.dev/blog/prototyping-app-with-static-html/
    HTML beats pixel canvas when requirements churn; realistic ugly data; a URL
    stakeholders can resize/hover beats a static image; mockup structure pre-decides
    implementation structure.
26. **NN/g: Prototype fidelity** — https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/
    Fidelity = 3 independent dials (interactivity / visual / content); for direction
    decisions: high visual + real content, low interactivity; roughness signals status.
27. **NN/g: GenUI vs Vibe Coding** — https://www.nngroup.com/articles/genui-vs-vibe/
    Vague prompts silently delegate design decisions to the AI — the argument for an
    explicit design gate.
28. **AI Builder Club: Vibe Design workflow** — https://www.aibuilderclub.com/blog/vibe-design-ai-ui-workflow
    Generate many, curate ruthlessly, screenshot-compare HTML candidates side by side;
    admits token governance is the gap (fixed by real-token mockups).
29. **UX Pilot: Vibe Designing** — https://uxpilot.ai/blogs/vibe-design
    Breadth-first "5 of 50" directions; governed style reference (tokens + negative
    prompts embedded in every generation).
30. **GitHub Spec Kit: spec-driven.md** — https://github.com/github/spec-kit/blob/main/spec-driven.md
    Gated markdown artifacts with pre-implementation gates; verified gap: NO design
    phase exists in Spec Kit — the design gate fills a real hole in agentic SDD.
31. **Martin Fowler: ADR** — https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
    Decision/Context/Options/Consequences one-pager; immutable + superseding; writing
    the record is itself the convergence mechanism.

## Internal evidence — production PR audit (last ~25 PRs, 2026-07)

Recurring anti-patterns that motivated this skill: one page shell for everything
(members/credentials/compliance/groups/admin-users structurally identical);
Card-as-universal-container incl. first-run accept-invitation flow (#578, #593);
intent-communicating copy deleted rather than designed (#591, #597, #621 subtitle
purges); convergence toward stock shadcn — bespoke pieces removed, none added (#597
pill-toggle → default Select); ad-hoc className at call sites instead of base variants
(`w-2/5`, `rounded-xl`, `max-w-sm`); generic feedback vocabulary (toast + spinner +
copy-pasted destructive div instead of ErrorState); no domain visual language for a
credentials product; page chrome redesigned 3× in 4 PRs as ticket side effects.
Strengths preserved by this skill's constraints: ui/→base/→shared/→pages layering,
semantic-token-only styling, systematic state handling, single-source chrome config.
