# UI Improvements (S-04) — Plan Brief

> Full plan: `context/changes/ui-improvements/plan.md`

## What & Why

We are giving Coinductor a distinctive UI identity so it no longer looks like a default Tailwind template. The goal is a clean fintech look that feels trustworthy and modern while preserving existing budget/expense flows and responsiveness.

## Starting Point

Current templates use repeated inline Tailwind utilities with default blue/slate styling and no shared theme tokens. Tailwind config has no custom `theme.extend`, and auth/dashboard screens duplicate many visual patterns.

## Desired End State

Core surfaces (base layout, dashboard, auth) share a consistent branded style based on `#FFFFFF`, `#EAA430`, and `#2B2B2B`. Reusable styling primitives reduce template drift, interactions have subtle polish, and user flows continue to work without regressions.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) | Source |
| --- | --- | --- | --- |
| Surface scope | Base + dashboard + auth only | Highest visible impact with controlled risk. | Plan |
| Brand direction | Clean fintech | Distinctive but maintainable for MVP speed. | Plan |
| Palette | White + `#EAA430` + `#2B2B2B` | Clear brand identity with strong readability baseline. | Plan |
| Token depth | Foundational tokens + semantic classes | Establishes durable consistency without full system overbuild. | Plan |
| Reuse model | Selective partials for repeated blocks | Reduces duplication while preserving current architecture. | Plan |
| Motion level | Subtle transitions/focus polish only | Better perceived quality with low performance/accessibility risk. | Plan |
| Responsive priority | Desktop-first then mobile hardening | Matches user preference while still protecting mobile usability. | Plan |
| Test strategy | Prefer semantic assertions, keep essential class checks | Makes refactors safer by reducing brittle style coupling. | Plan |

## Scope

**In scope:** token layer in Tailwind/CSS, reusable UI partials/classes, restyle of base/dashboard/auth, UI test hardening.

**Out of scope:** business-logic changes, full component library, auth/data-model redesign, heavy animation system.

## Architecture / Approach

Use Tailwind `theme.extend` for brand tokens and `@layer` semantic classes as a stable styling contract, then migrate repeated template patterns into selective partials and apply them across core pages. Keep behavioral templates/context logic intact; only presentation and related test assertions are refactored.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Brand Foundation and Tokens | Brand tokens + semantic style hooks | Token choices leak inconsistently into templates |
| 2. Shared UI Building Blocks | Reusable card/badge/control patterns | Over-refactor can create template churn |
| 3. Core Screen Restyling | Branded base/dashboard/auth surfaces | Visual change may accidentally impact mobile ergonomics |
| 4. Test Hardening and Final Acceptance | Stable semantic test posture + done gate | Missing assertions could hide UI regressions |

**Prerequisites:** F-01, F-02, S-01 complete.
**Estimated effort:** ~2-3 sessions across 4 phases.

## Open Risks & Assumptions

- Desktop-first emphasis must not degrade mobile quick-action usability.
- Semantic class naming must stay consistent to avoid recreating utility sprawl.
- Some legacy class assertions may still be needed where width/state cues are contract-relevant.

## Success Criteria (Summary)

- Coinductor has a visibly distinct branded UI on base/dashboard/auth screens.
- Focus/contrast quality remains accessibility-safe for interactive controls.
- Existing dashboard/auth flows continue working with no behavior regressions.
