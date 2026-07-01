# UI Improvements (S-04) Implementation Plan

## Overview

Implement a distinctive Coinductor visual identity across core user-facing screens without changing business behavior. The redesign introduces a brand token layer and reusable UI building blocks while preserving S-01/S-02 flow expectations.

## Current State Analysis

Core templates rely mostly on default Tailwind utility composition and blue/slate defaults, with styling repeated inline across files. There is no theme extension in Tailwind config, and tests currently include class-coupled assertions on velocity bar widths.

## Desired End State

Coinductor has a recognizable, consistent visual language on base layout, dashboard, and authentication pages using palette tokens: `#FFFFFF` (primary surface), `#EAA430` (accent), and `#2B2B2B` (charcoal text/contrast layer). Shared UI blocks reduce template duplication, subtle interaction polish is present, and no core UX flow regresses.

### Key Discoveries:

- `tailwind.config.js:1-10` currently has `theme.extend` empty, so tokenization must be added from scratch.
- `coinductor/templates/base.html:10-23` and `coinductor/templates/home.html:5-87` use repeated slate/blue utility patterns.
- `coinductor/templates/registration/login.html:4-57`, `signup.html:4-70`, and `logged_out.html:4-23` duplicate card/form/button styling.
- `coinductor/tests.py:74-75` and `99` assert specific width classes (`w-1/3`, `w-2/3`), which should be minimized during visual refactor.

## What We're NOT Doing

- Reworking dashboard business logic or S-01 calculations.
- Building a full design system/component library beyond high-repeat blocks.
- Changing auth workflows, routes, or data model.
- Adding heavy animations or non-essential visual effects.

## Implementation Approach

Add brand tokens in Tailwind and a thin semantic style layer, then refactor high-repeat template blocks into partials/classes and apply the new look to core pages. Keep desktop-first composition per decision, with explicit mobile adaptation checks before completion.

## Critical Implementation Details

Desktop-first polish is accepted for this slice, but manual validation must still confirm mobile usability and preserve the quick-entry guardrail shape. Template refactors should avoid coupling semantic meaning to fragile utility strings so tests can assert behavior and content rather than stylistic internals.

## Phase 1: Brand Foundation and Tokens

### Overview

Define the visual contract (colors, typography, spacing accents, radii, shadows, focus states) and make it available project-wide.

### Changes Required:

#### 1. Tailwind theme extension and semantic style hooks

**File**: `tailwind.config.js`

**Intent**: Introduce brand tokens for palette and shared visual primitives, enabling non-default Coinductor styling.

**Contract**: `theme.extend` includes named tokens for white, accent `#EAA430`, and charcoal `#2B2B2B`, plus supporting radius/shadow/typography values used by templates.

**File**: `static/css/input.css`

**Intent**: Add reusable semantic utility groupings for common blocks (page shell, card, button, badge, form controls).

**Contract**: `@layer components` (and, if needed, `@layer base`) defines stable semantic classes consumed by templates.

### Success Criteria:

#### Automated Verification:

- Tailwind build outputs CSS with new brand token classes available.
- Existing Django test suite still passes before template adoption changes.

#### Manual Verification:

- Accent `#EAA430` and charcoal `#2B2B2B` are visible in baseline shell styles.
- Focus state remains clearly visible on interactive controls.

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Phase 2: Shared UI Building Blocks

### Overview

Reduce duplication by introducing reusable template partials and standardized semantic classes for repeated blocks.

### Changes Required:

#### 1. Reusable partials for repeated UI patterns

**File**: `coinductor/templates/partials/ui_card.html` (new)

**Intent**: Standardize card shell structure used across dashboard and auth screens.

**Contract**: Partial accepts block content and applies canonical brand card class set.

**File**: `coinductor/templates/partials/ui_badge.html` (new)

**Intent**: Normalize status badge styling (on-track/off-track and related labels).

**Contract**: Partial supports variant input (success/warn/danger/neutral) mapped to semantic classes.

#### 2. Base-level shared controls

**File**: `coinductor/templates/base.html`

**Intent**: Align top navigation and message area to the new visual language.

**Contract**: Header/nav/message wrappers use new semantic classes rather than repeated raw blue/slate utilities.

### Success Criteria:

#### Automated Verification:

- Templates render with new partial includes without template resolution errors.
- Existing route-level tests still pass after partial extraction.

#### Manual Verification:

- Shared card/badge/button treatment is visually consistent across at least two different pages.
- Navigation/messages retain readability and hierarchy with new palette.

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Phase 3: Core Screen Restyling (Desktop-first, Mobile-safe)

### Overview

Apply the new identity to dashboard and auth experiences while preserving behavior and information architecture.

### Changes Required:

#### 1. Dashboard restyle

**File**: `coinductor/templates/home.html`

**Intent**: Move dashboard visuals to the branded system with clearer hierarchy, spacing polish, and subtle interaction refinement.

**Contract**: Existing context branches (`no_budget`, `no_expenses`, metrics, velocity states) remain intact; only presentation contracts change.

#### 2. Auth screen restyle

**File**: `coinductor/templates/registration/login.html`
**File**: `coinductor/templates/registration/signup.html`
**File**: `coinductor/templates/registration/logged_out.html`

**Intent**: Bring auth surfaces into the same brand language for first-session consistency.

**Contract**: Form semantics, validation rendering, and route actions are unchanged; styling migrates to semantic classes/tokens.

### Success Criteria:

#### Automated Verification:

- Django tests pass with restyled templates.
- No template context key regressions on dashboard/auth routes.

#### Manual Verification:

- Core pages present a clearly non-default Tailwind look aligned to chosen palette.
- Desktop layout polish is complete and mobile layout remains usable for key actions.

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Phase 4: Test Hardening and Final Acceptance

### Overview

Stabilize verification by reducing brittle style-coupled test expectations and locking final acceptance criteria for S-04.

### Changes Required:

#### 1. UI test assertion strategy update

**File**: `coinductor/tests.py`

**Intent**: Prefer semantic/behavioral assertions while retaining only essential style checks.

**Contract**: Tests still guarantee status and state rendering correctness; non-essential class-fragment dependencies are removed or reduced.

#### 2. Final acceptance checklist alignment

**File**: `context/changes/ui-improvements/plan.md`

**Intent**: Record completion evidence expectations for branded look, accessibility-safe focus/contrast, and no UX flow regressions.

**Contract**: `## Progress` and manual verification steps represent the final done gate for S-04.

### Success Criteria:

#### Automated Verification:

- Updated test suite passes with reduced brittle class coupling.
- No regressions detected in dashboard/auth route behavior checks.

#### Manual Verification:

- Brand identity is consistent across base, dashboard, and auth screens.
- Contrast and focus indicators remain clear on interactive elements.
- Primary user flows continue working without added friction.

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Testing Strategy

### Unit Tests:

- Preserve dashboard/auth route expectations in `coinductor/tests.py`.
- Validate that state-driven copy and status indicators still render correctly.

### Integration Tests:

- Authenticated dashboard flow remains functional after restyling.
- Auth form flow (signup/login/logout pages) remains intact with unchanged behavior.

### Manual Testing Steps:

1. Log in and review dashboard states (no budget, no expenses, with expenses) for visual consistency and readability.
2. Verify signup/login/logout screens reflect the new brand styles and error presentation remains clear.
3. Confirm keyboard focus visibility and basic mobile usability on core actions.

## Performance Considerations

Keep CSS additions focused on semantic layers over deep utility explosion. Avoid heavy animation; use lightweight transitions only.

## Migration Notes

No data migration required. This is presentation-layer and test-assertion refactor work.

## References

- Roadmap slice: `context/foundation/roadmap.md` (S-04 entry)
- Tailwind baseline: `tailwind.config.js:1-10`
- Base shell: `coinductor/templates/base.html:10-35`
- Dashboard template: `coinductor/templates/home.html:5-87`
- Auth templates: `coinductor/templates/registration/login.html:4-57`, `coinductor/templates/registration/signup.html:4-70`, `coinductor/templates/registration/logged_out.html:4-23`
- Current UI assertions: `coinductor/tests.py:71-75`, `95-100`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Brand Foundation and Tokens

#### Automated

- [x] 1.1 Tailwind build outputs CSS with new brand token classes available.
- [x] 1.2 Existing Django test suite still passes before template adoption changes.

#### Manual

- [ ] 1.3 Accent `#EAA430` and charcoal `#2B2B2B` are visible in baseline shell styles.
- [ ] 1.4 Focus state remains clearly visible on interactive controls.

### Phase 2: Shared UI Building Blocks

#### Automated

- [ ] 2.1 Templates render with new partial includes without template resolution errors.
- [ ] 2.2 Existing route-level tests still pass after partial extraction.

#### Manual

- [ ] 2.3 Shared card/badge/button treatment is visually consistent across at least two different pages.
- [ ] 2.4 Navigation/messages retain readability and hierarchy with new palette.

### Phase 3: Core Screen Restyling (Desktop-first, Mobile-safe)

#### Automated

- [ ] 3.1 Django tests pass with restyled templates.
- [ ] 3.2 No template context key regressions on dashboard/auth routes.

#### Manual

- [ ] 3.3 Core pages present a clearly non-default Tailwind look aligned to chosen palette.
- [ ] 3.4 Desktop layout polish is complete and mobile layout remains usable for key actions.

### Phase 4: Test Hardening and Final Acceptance

#### Automated

- [ ] 4.1 Updated test suite passes with reduced brittle class coupling.
- [ ] 4.2 No regressions detected in dashboard/auth route behavior checks.

#### Manual

- [ ] 4.3 Brand identity is consistent across base, dashboard, and auth screens.
- [ ] 4.4 Contrast and focus indicators remain clear on interactive elements.
- [ ] 4.5 Primary user flows continue working without added friction.
