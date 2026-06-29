# Dashboard On-Track + Daily Limit Implementation Plan

## Overview

Implement S-01 by turning the home page into an authenticated dashboard that shows current-month budget health, a pace-aware on-track status, remaining budget, remaining days, daily limit, and a small spending-velocity indicator. The implementation keeps existing Django FBV routing and adds a focused calculation service in `budget/services.py`.

## Current State Analysis

- `home` is currently a public placeholder with no dashboard calculations (`coinductor/views.py:36-37`, `coinductor/templates/home.html:5-19`).
- Auth flows are in place and already redirect to `home` (`coinductor/urls.py:23-26`, `coinductor/settings.py:179-181`).
- Domain models exist for monthly budgets and expenses, including ownership + soft-delete fields (`budget/models.py:20-29`, `budget/models.py:50-57`, `budget/models.py:79-87`).
- No existing service/query layer computes dashboard metrics or pace-aware status.

## Desired End State

The authenticated home route (`/`) renders an S-01 dashboard for the current month with:
1. Pace-aware on-track status.
2. Remaining budget, days left, and daily limit (`remaining_budget / remaining_days`).
3. Spending velocity metric + mini indicator.
4. Explicit empty states:
   - No current-month budget: setup guidance CTA.
   - Budget exists, no expenses yet: full-allowance guidance.

### Key Discoveries:

- Existing route and auth conventions should be reused (FBV + named routes): `coinductor/urls.py:23-27`, `coinductor/views.py:8-37`.
- Monthly budget model is anchored to first day of month and supports category-level totals: `budget/models.py:15-17`, `budget/models.py:56`, `budget/models.py:61-64`.
- Soft-delete is shared across relevant models and must be explicitly filtered out in dashboard queries: `budget/models.py:20-29`.
- PRD/roadmap require this exact dashboard loop as core product behavior: `context/foundation/prd.md:45-53`, `context/foundation/prd.md:91-99`, `context/foundation/roadmap.md:87-97`.

## What We're NOT Doing

- No true browser automation stack (Playwright/Selenium) in this change; Django integration tests are the approved E2E-equivalent for S-01.
- No charting library or complex analytics UI.
- No cross-month carryover budgeting logic.
- No new app split (no `dashboard/` app); routing stays in existing `coinductor` module.
- No changes to budget setup or expense-entry forms beyond what S-01 needs to render computed state.

## Implementation Approach

Keep `home` as the dashboard entry route and protect it with `@login_required`. Move all calculation/query logic into `budget/services.py` so behavior is testable independently of the view. The view stays thin: gather service output and render `home.html`.

For monthly calculations, scope all budget and expense data to the authenticated user, current calendar month, and `is_deleted=False`. Compute velocity and on-track using the user-approved pace-aware rule, then map this to a lightweight UI indicator in the dashboard template.

## Critical Implementation Details

### Timing & lifecycle

Use a date source that respects Django timezone settings when deriving "today" and month boundaries; this prevents date-boundary drift around UTC day transitions (`coinductor/settings.py:147-152`).

### State sequencing

Derive month bounds first, aggregate budget and expense totals second, then compute remaining budget, daily limit, velocity, and on-track from the same scoped totals. Mixing per-metric scopes will create contradictory dashboard states.

## Phase 1: Dashboard Calculation Service

### Overview

Add a dedicated service module that computes dashboard metrics and pace-aware status for one user and one month.

### Changes Required:

#### 1. Dashboard metric service module

**File**: `budget/services.py`

**Intent**: Centralize dashboard calculations and scoped ORM aggregates so view/template layers consume one normalized payload.

**Contract**: Add a service entrypoint (for example `get_dashboard_metrics(user, as_of=None)`) that returns a dictionary containing totals, remaining days, daily limit, velocity values, on-track state, and empty-state flags.

#### 2. Scoped monthly aggregate queries

**File**: `budget/services.py`

**Intent**: Ensure dashboard math uses only current-month, user-owned, active records.

**Contract**: Budget totals are computed from `Budget` filtered by `(user, month=<current-month-start>, is_deleted=False)` and expense totals from `Expense` filtered by `(user, date within current month, is_deleted=False)`.

#### 3. Pace-aware on-track and velocity classification

**File**: `budget/services.py`

**Intent**: Implement the selected on-track definition and provide a stable velocity indicator payload for the template.

**Contract**: On-track is computed from spending pace vs sustainable pace (not a simple `remaining_budget >= 0` check), and service output includes a velocity status suitable for a mini indicator rendering.

#### 4. Service unit tests

**File**: `budget/tests.py`

**Intent**: Lock behavior for month scoping, soft-delete filtering, pace-aware status, and edge math outcomes.

**Contract**: Add tests that cover empty states, overspend/negative remaining budget, threshold pace behavior, user isolation, deleted row exclusion, and month-boundary correctness.

### Success Criteria:

#### Automated Verification:

- Dashboard service tests pass for metric calculations and edge cases: `python manage.py test budget.tests`
- Service output includes required keys for dashboard rendering (metrics + state flags): `python manage.py test budget.tests`

#### Manual Verification:

- Manual sanity check in Django shell confirms expected outputs for one no-budget case and one overspend case

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Auth-Protected Dashboard View Wiring

### Overview

Update the home view to enforce authentication, call the service, and pass the structured dashboard payload into template context.

### Changes Required:

#### 1. Protect dashboard route

**File**: `coinductor/views.py`

**Intent**: Ensure budget state is never rendered for anonymous requests.

**Contract**: Apply `@login_required` to `home` and keep route name/path unchanged (`''` -> `home`).

#### 2. Wire service output into view context

**File**: `coinductor/views.py`

**Intent**: Keep view logic thin by delegating calculations while still shaping template-friendly context names.

**Contract**: `home` calls the dashboard service and renders `home.html` with context fields needed for metrics, on-track status, velocity indicator, and empty-state branches.

#### 3. View/auth integration tests

**File**: `coinductor/tests.py`

**Intent**: Validate route protection and context behavior through Django's request/response stack.

**Contract**: Add tests proving anonymous users are redirected to login and authenticated users receive dashboard context for current-month data.

### Success Criteria:

#### Automated Verification:

- View integration tests pass for auth redirect and authenticated render behavior: `python manage.py test coinductor.tests`
- Home route remains resolved and login redirect still lands on `home`: `python manage.py test coinductor.tests`

#### Manual Verification:

- Anonymous browser visit to `/` redirects to login; authenticated visit renders dashboard container

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Dashboard Template UI + States

### Overview

Replace placeholder home template content with production dashboard UI that renders core metrics, velocity indicator, and explicit empty states.

### Changes Required:

#### 1. Dashboard metrics and status UI

**File**: `coinductor/templates/home.html`

**Intent**: Present on-track status, remaining budget, days left, and daily limit prominently on initial dashboard load.

**Contract**: Render user-facing S-01 metric cards/sections with clear status styling aligned to existing Tailwind palette conventions from current templates.

#### 2. Velocity mini indicator UI

**File**: `coinductor/templates/home.html`

**Intent**: Add lightweight pace feedback without introducing chart dependencies.

**Contract**: Render a compact velocity indicator driven by service-provided classification values and numbers.

#### 3. Explicit empty states

**File**: `coinductor/templates/home.html`

**Intent**: Avoid misleading zero-value dashboard when data/setup is incomplete.

**Contract**: Add two branches: (a) no current-month budget -> setup guidance CTA; (b) budget exists, no expenses yet -> full-allowance guidance while still showing meaningful context.

#### 4. UI-focused integration assertions and CSS build

**File**: `coinductor/tests.py`

**Intent**: Ensure key UI states are represented in rendered responses and static CSS build remains healthy.

**Contract**: Add assertions for critical text/state markers in authenticated dashboard responses and keep Tailwind build command part of phase verification.

### Success Criteria:

#### Automated Verification:

- Dashboard UI state tests pass for normal, no-budget, and no-expenses cases: `python manage.py test coinductor.tests`
- Tailwind CSS compiles successfully after template updates: `npm run build`

#### Manual Verification:

- Logged-in dashboard visually shows selected velocity indicator and correct state styling for on-track/off-track scenarios

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 4: S-01 End-to-End Verification (Django Stack)

### Overview

Run consolidated automated and manual checks for the full auth-to-dashboard journey using the approved Django integration testing approach.

### Changes Required:

#### 1. Consolidated test execution

**File**: `budget/tests.py`, `coinductor/tests.py`

**Intent**: Verify complete S-01 behavior after all wiring/template changes are integrated.

**Contract**: Execute test suites covering calculations, auth gating, scoped data usage, dashboard render states, and regression safety.

#### 2. Manual user-flow verification script

**File**: `context/changes/dashboard-on-track-daily-limit/plan.md` (this section), implementation runbook references in PR

**Intent**: Ensure human validation explicitly checks visible dashboard behavior across realistic states.

**Contract**: Manual flow includes login, dashboard load, state transitions after seeded data changes, and confirmation of empty-state guidance clarity.

### Success Criteria:

#### Automated Verification:

- Full Django test suite passes for affected areas: `python manage.py test budget coinductor`
- Project-wide regression check remains green: `python manage.py test`

#### Manual Verification:

- Full user flow validated: login -> dashboard metrics -> state changes reflected correctly after expense/budget data adjustments

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Testing Strategy

### Unit Tests:

- Service calculations for remaining budget, remaining days, daily limit rounding/format-safe values
- Pace-aware on-track threshold logic around boundary conditions
- Data scoping behavior (user, month, `is_deleted=False`)

### Integration Tests:

- Auth redirect behavior for `/` when anonymous
- Authenticated dashboard render with expected context/state markers
- Dashboard branches for normal, no-budget, and no-expenses states

### Manual Testing Steps:

1. Log in with an existing account and verify dashboard loads on `/`
2. Confirm no-budget state message/CTA when current-month budget is absent
3. Add current-month budget and verify no-expenses guidance state
4. Add expenses to transition from on-track to off-track and verify status + velocity indicator update
5. Confirm data from other users and soft-deleted rows does not affect displayed numbers

## Performance Considerations

- Keep dashboard aggregation query count minimal by using scoped aggregate calls, not per-category loops.
- Ensure date filters are month-bounded to avoid scanning non-relevant expense history.
- Avoid chart libraries or client-side computation for S-01; render server-side values from service output.

## Migration Notes

- No new schema migrations are required for S-01.
- This plan assumes F-02 models and migrations are already present and applied.

## References

- Related research: `context/changes/dashboard-on-track-daily-limit/research.md`
- Product requirement and acceptance criteria: `context/foundation/prd.md:45-53`, `context/foundation/prd.md:91-99`
- Slice sequencing and scope: `context/foundation/roadmap.md:87-97`
- Existing home route and auth wiring: `coinductor/urls.py:23-27`, `coinductor/views.py:36-37`
- Domain model constraints and ownership/soft-delete: `budget/models.py:20-29`, `budget/models.py:50-57`, `budget/models.py:79-87`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Dashboard Calculation Service

#### Automated

- [x] 1.1 Dashboard service tests pass for metric calculations and edge cases
- [x] 1.2 Service output includes required keys for dashboard rendering (metrics + state flags)

#### Manual

- [x] 1.3 Manual sanity check in Django shell confirms expected outputs for one no-budget case and one overspend case

### Phase 2: Auth-Protected Dashboard View Wiring

#### Automated

- [ ] 2.1 View integration tests pass for auth redirect and authenticated render behavior
- [ ] 2.2 Home route remains resolved and login redirect still lands on `home`

#### Manual

- [ ] 2.3 Anonymous browser visit to `/` redirects to login; authenticated visit renders dashboard container

### Phase 3: Dashboard Template UI + States

#### Automated

- [ ] 3.1 Dashboard UI state tests pass for normal, no-budget, and no-expenses cases
- [ ] 3.2 Tailwind CSS compiles successfully after template updates

#### Manual

- [ ] 3.3 Logged-in dashboard visually shows selected velocity indicator and correct state styling for on-track/off-track scenarios

### Phase 4: S-01 End-to-End Verification (Django Stack)

#### Automated

- [ ] 4.1 Full Django test suite passes for affected areas
- [ ] 4.2 Project-wide regression check remains green

#### Manual

- [ ] 4.3 Full user flow validated: login -> dashboard metrics -> state changes reflected correctly after expense/budget data adjustments
