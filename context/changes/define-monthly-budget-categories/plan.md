# Define Monthly Budget Categories Implementation Plan

## Overview

Implement S-03 so authenticated users can define and edit current-month category budgets directly from the dashboard, including optional custom category creation during setup. Saving budgets must immediately unlock dashboard daily-limit guidance and preserve existing S-01 behavior.

## Current State Analysis

The domain layer already supports user-owned categories and monthly budgets, but there is no user-facing budget setup flow yet. The dashboard currently shows a no-budget placeholder, and `home` is GET-only with no form handling for S-03.

## Desired End State

From the dashboard no-budget state, a user can set current-month category amounts (with optional custom category addition), submit once, and immediately see dashboard metrics recalculate with no-budget state cleared when at least one category has a positive amount.

### Key Discoveries:

- `Budget` already enforces uniqueness per `(user, category, month)` and month normalization constraints (`budget/models.py:56-64`).
- Default predefined categories are seeded automatically for each user (`budget/signals.py:10-17`, `budget/tests.py:48-67`).
- Dashboard empty-state placeholder explicitly defers S-03 (`coinductor/templates/home.html:19-31`).
- Existing dashboard math already reads monthly budgets, so S-03 can unlock current metrics without changing service contract (`budget/services.py:56-83`).
- `home` route is canonical and auth-protected, matching S-01/S-02 architecture decisions (`coinductor/views.py:39-52`, `coinductor/urls.py:23`).

## What We're NOT Doing

- No multi-month budget management UI (past/future month switching).
- No category deletion/archive management flow in S-03.
- No budget history/versioning UI.
- No changes to S-01 calculation formula or velocity rules.

## Implementation Approach

Use dashboard-owned, action-dispatched POST handling on `home` to support budget setup without new primary routes. Implement a dedicated budget setup form layer for current-month per-category amounts with idempotent upsert semantics. Keep predefined categories as baseline while allowing custom category creation in the same flow, guarded by ownership and uniqueness validation.

## Critical Implementation Details

### State sequencing

Budget setup and upcoming expense quick-add must coexist on `home`; use explicit POST action routing so each form path is isolated and testable. On successful budget submit, redirect back to `home` (PRG) so metrics are recomputed from persisted rows and duplicate-submit risk is avoided.

## Phase 1: Budget Setup Form Layer

### Overview

Introduce form primitives for current-month budget setup and controlled custom category creation.

### Changes Required:

#### 1. Budget setup forms and validation

**File**: `budget/forms.py` (new)

**Intent**: Provide reusable validation for per-category amount input and custom category entry from dashboard.

**Contract**: Add form components that accept `user` context, validate amounts as `>= 0`, enforce "at least one amount > 0" across submitted budgets, and validate custom category names against user-scoped uniqueness.

#### 2. Budget form layer tests

**File**: `budget/tests.py` (or split test module under `budget/`)

**Intent**: Lock correctness for amount rules, category ownership, and custom category uniqueness behavior.

**Contract**: Add tests for valid submission, all-zero rejection, negative amount rejection, duplicate custom category rejection, and cross-user safety.

### Success Criteria:

#### Automated Verification:

- Budget form validation tests pass for positive/zero/negative and uniqueness scenarios: `./.venv/bin/python manage.py test budget.tests`
- Existing model ownership + dashboard service tests remain green: `./.venv/bin/python manage.py test budget.tests`

#### Manual Verification:

- In dev UI/shell, custom category creation works for a new name and is blocked for duplicate user category names

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Phase 2: Dashboard POST Orchestration and Upsert

### Overview

Wire action-dispatched POST handling into `home` to process budget setup submits safely and idempotently.

### Changes Required:

#### 1. Home action dispatch for budget setup

**File**: `coinductor/views.py`

**Intent**: Add clear POST branching so budget setup can coexist with dashboard GET and future S-02 expense action.

**Contract**: `home` supports POST with explicit action token for budget setup; successful branch persists data then redirects to `home`, invalid branch re-renders with bound errors.

#### 2. Current-month budget upsert behavior

**File**: `coinductor/views.py` (or helper in `budget/services.py` if extracted)

**Intent**: Ensure repeated edits update current-month category budgets without duplicate-row failures.

**Contract**: For each submitted category amount, persist using create-or-update semantics keyed by `(user, category, month_start)` and revive soft-deleted rows if needed.

#### 3. View integration tests for budget POST

**File**: `coinductor/tests.py`

**Intent**: Verify end-to-end POST behavior and no-budget state transition at the route level.

**Contract**: Add tests for valid submit redirect + saved budgets, invalid submit error rendering, action branch isolation, and unchanged auth redirect behavior.

### Success Criteria:

#### Automated Verification:

- Home integration tests pass for budget POST success/error branches: `./.venv/bin/python manage.py test coinductor.tests.HomeDashboardViewTests`
- Combined impacted suites pass: `./.venv/bin/python manage.py test budget coinductor`

#### Manual Verification:

- From no-budget dashboard, submitting valid amounts returns to dashboard with no-budget state cleared
- Invalid submit keeps user on dashboard with visible inline errors and preserved inputs

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Phase 3: Dashboard Budget Setup UI Integration

### Overview

Replace the S-03 placeholder with a working budget setup interface in dashboard no-budget/edit contexts.

### Changes Required:

#### 1. No-budget setup panel UI

**File**: `coinductor/templates/home.html`

**Intent**: Convert current placeholder CTA into a real setup form users can complete without leaving dashboard.

**Contract**: In no-budget state, render current-month category amount inputs, optional custom category input, CSRF-protected submit, and inline validation messages.

#### 2. Edit path visibility

**File**: `coinductor/templates/home.html`

**Intent**: Allow user to revise current-month budgets after initial setup.

**Contract**: Render accessible "edit monthly budget" trigger/section for authenticated users with existing budgets, reusing same action contract as setup.

#### 3. UI-oriented integration assertions

**File**: `coinductor/tests.py`

**Intent**: Guard template branches and key text/form presence for S-03.

**Contract**: Add assertions for setup form visibility in `no_budget`, successful transition to metrics state, and custom-category validation error rendering.

### Success Criteria:

#### Automated Verification:

- Dashboard template integration tests pass for no-budget/setup/edit branches: `./.venv/bin/python manage.py test coinductor.tests`
- Tailwind build remains healthy after template updates: `npm run build`

#### Manual Verification:

- User can complete current-month budget setup from dashboard in one flow without admin usage
- After save, dashboard metrics reflect entered budget totals immediately

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Phase 4: S-03 Final Verification and Stability

### Overview

Run consolidated verification to ensure S-03 works reliably and does not regress S-01/S-02-adjacent dashboard behavior.

### Changes Required:

#### 1. Consolidated automated regression run

**File**: test files touched in Phases 1-3

**Intent**: Validate S-03 behavior alongside existing dashboard and model guarantees.

**Contract**: Execute targeted and broad Django test commands and confirm frontend build success.

#### 2. Manual product-loop verification

**File**: `context/changes/define-monthly-budget-categories/plan.md` (this checklist)

**Intent**: Confirm user-visible success criteria for setup completion and immediate metric feedback.

**Contract**: Validate no-budget -> setup -> recalculated dashboard loop plus edit flow and custom category behavior.

### Success Criteria:

#### Automated Verification:

- Targeted suites pass for budget + dashboard features: `./.venv/bin/python manage.py test budget coinductor`
- Full project test suite passes: `./.venv/bin/python manage.py test`
- CSS pipeline passes: `npm run build`

#### Manual Verification:

- End-to-end setup flow works and exits no-budget state when at least one category budget is positive
- Editing current-month budgets updates dashboard values without duplicate/constraint errors

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase. Phase blocks use plain bullets — the corresponding `- [ ]` checkboxes for these items live in the `## Progress` section at the bottom of the plan.

---

## Testing Strategy

### Unit Tests:

- Budget setup validation logic (`>=0`, at least one `>0`, uniqueness for custom category)
- User ownership and category-scoped safety for budget persistence
- Upsert behavior for existing current-month budgets

### Integration Tests:

- `home` POST action routing for budget setup success and error branches
- Dashboard no-budget to metrics-state transition after budget submit
- Edit existing budget flow and custom category creation from dashboard

### Manual Testing Steps:

1. Log in with user that has no current-month budgets and open dashboard.
2. Submit valid category amounts (and optionally a custom category) from setup section.
3. Confirm redirect to dashboard with no-budget state cleared and metrics updated.
4. Submit invalid payload (all zeros or negative amount) and verify inline errors.
5. Edit existing current-month budget values and confirm updated totals on dashboard.

## Performance Considerations

- Keep save path bounded to current-month category set; avoid unnecessary cross-month queries.
- Reuse existing dashboard aggregation service after submit rather than duplicating calculations in view.

## Migration Notes

- No schema migration required if custom categories reuse existing `Category` model.
- If constraints around category naming need extension later, handle as follow-up change.

## References

- Product requirements: `context/foundation/prd.md:63-65`, `context/foundation/prd.md:95-99`
- Roadmap S-03 definition: `context/foundation/roadmap.md:114-125`
- Current dashboard flow: `coinductor/views.py:39-52`, `coinductor/templates/home.html:19-31`
- Domain constraints and defaults: `budget/models.py:56-64`, `budget/signals.py:10-17`, `budget/tests.py:48-67`
- S-02 architecture alignment: `context/changes/add-expense-three-taps/plan.md`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Budget Setup Form Layer

#### Automated

- [x] 1.1 Budget form validation tests pass for positive/zero/negative and uniqueness scenarios — d4f4461
- [x] 1.2 Existing model ownership + dashboard service tests remain green — d4f4461

#### Manual

- [x] 1.3 Custom category creation works for new names and is blocked for duplicate user names — d4f4461

### Phase 2: Dashboard POST Orchestration and Upsert

#### Automated

- [x] 2.1 Home integration tests pass for budget POST success/error branches — fc249fc
- [x] 2.2 Combined impacted suites pass — fc249fc

#### Manual

- [x] 2.3 Valid no-budget submit redirects and clears no-budget state — fc249fc
- [x] 2.4 Invalid submit shows inline errors with preserved inputs — fc249fc

### Phase 3: Dashboard Budget Setup UI Integration

#### Automated

- [x] 3.1 Dashboard template integration tests pass for no-budget/setup/edit branches — 825ea9a
- [x] 3.2 Tailwind build remains healthy after template updates — 825ea9a

#### Manual

- [x] 3.3 User can complete current-month budget setup from dashboard without admin — 825ea9a
- [x] 3.4 Dashboard metrics reflect saved budget totals immediately — 825ea9a

### Phase 4: S-03 Final Verification and Stability

#### Automated

- [x] 4.1 Targeted suites pass for budget + dashboard features
- [x] 4.2 Full project test suite passes
- [x] 4.3 CSS pipeline passes

#### Manual

- [x] 4.4 End-to-end setup flow exits no-budget state with at least one positive category budget
- [x] 4.5 Editing current-month budgets updates dashboard without constraint errors
