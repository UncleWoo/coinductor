# Add Expense in Three Taps Implementation Plan

## Overview

Implement S-02 so authenticated users can add an expense (amount, category, date) directly from dashboard in ≤3 taps/clicks, with instant recalculation of budget metrics and on-track status after save.

## Current State Analysis

`home` is already the authenticated dashboard surface and metrics come from `get_dashboard_metrics`, but there is no expense-entry POST flow, no expense form, and no dashboard quick-add UI.

### Key Discoveries:

- Dashboard rendering and auth boundary are centralized in `home` (`coinductor/views.py:39-52`).
- Route topology is minimal and FBV-based (`coinductor/urls.py:23-27`).
- Recalculation logic already exists in one service (`budget/services.py:47-108`).
- `Expense` ownership constraints already exist at model level (`budget/models.py:92-97`).
- Current dashboard tests already validate state rendering and context keys (`coinductor/tests.py:13-105`).

## Desired End State

Users can submit a quick-add expense form from dashboard with amount, category, and prefilled-editable date. On success, they are returned to dashboard and see updated `Spent this month`, `Daily limit`, and status/velocity immediately. On failure, inline form errors are shown without losing entered values.

## What We're NOT Doing

- No API/SPA/HTMX flow for expense creation in this slice.
- No advanced recurring-expense automation.
- No charting or extra analytics panels.
- No broad dashboard redesign beyond adding quick-add UX.

## Implementation Approach

Use server-rendered POST-Redirect-GET on the existing `home` view to keep architecture consistent and avoid duplicate-submit issues. Introduce a lightweight `ModelForm` for `Expense` creation with user-scoped categories and model-level validation, render quick-add inline near top dashboard metrics, and reuse existing metrics service for instant post-save recalculation.

## Critical Implementation Details

### State sequencing

For success path use PRG strictly: validate/save expense in POST, then redirect to `home` and recompute metrics there. For invalid POST, re-render `home` with bound form and existing dashboard context so inline errors and metric cards are both visible.

### User experience spec

Date must default to today but remain editable. Entry remains allowed in `no_budget` state with warning visible, so users are not blocked before S-03.

## Phase 1: Expense Form and Validation Layer

### Overview

Create a dedicated quick-add form for `Expense` with user-safe category scoping and predictable field validation behavior.

### Changes Required:

#### 1. Expense quick-add form

**File**: `budget/forms.py`

**Intent**: Encapsulate expense input validation and user-scoped category choices for dashboard quick-add.

**Contract**: Add form exposing `amount`, `category`, `date` (and optional `description` if included), require `user` injection for category queryset scoping, and ensure save binds `expense.user` correctly.

#### 2. Form-focused tests

**File**: `budget/tests.py` (or `budget/test_forms.py` if split)

**Intent**: Prove category ownership and validation behavior at the form boundary.

**Contract**: Add tests for valid create, invalid category ownership, invalid required fields, and default date behavior.

### Success Criteria:

#### Automated Verification:

- Form tests pass for validation and ownership scenarios: `./.venv/bin/python manage.py test budget.tests`
- Existing budget service tests remain green: `./.venv/bin/python manage.py test budget.tests.DashboardMetricsServiceTests`

#### Manual Verification:

- In Django shell or dev UI, form rejects cross-user category and accepts valid same-user category

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Dashboard POST Flow Wiring

### Overview

Extend dashboard controller flow to handle expense creation and success/error states while preserving metrics recomputation.

### Changes Required:

#### 1. Home POST handling with PRG

**File**: `coinductor/views.py`

**Intent**: Enable expense creation from dashboard with robust submit behavior and instant recalculation after save.

**Contract**: `home` handles GET and POST; POST validates bound quick-add form, saves expense, redirects to `home` on success, and re-renders dashboard with bound errors on failure.

#### 2. Route compatibility check

**File**: `coinductor/urls.py`

**Intent**: Keep route naming stable while supporting dashboard POST.

**Contract**: Existing `home` route name/path remain unchanged (`''`, `name='home'`); no breaking auth-route changes.

#### 3. Integration tests for POST and recalculation

**File**: `coinductor/tests.py`

**Intent**: Verify anonymous protection, successful expense creation, and updated dashboard metrics after redirect.

**Contract**: Add tests for valid POST create, invalid POST with inline errors, and metric delta assertions after successful submit.

### Success Criteria:

#### Automated Verification:

- Home integration tests pass including POST create/error paths: `./.venv/bin/python manage.py test coinductor.tests.HomeDashboardViewTests`
- Affected app suites pass together: `./.venv/bin/python manage.py test budget coinductor`

#### Manual Verification:

- Submitting valid expense from dashboard creates row and returns user to updated dashboard
- Submitting invalid expense shows inline errors without clearing entered values

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Inline Quick-Add Dashboard UX

### Overview

Add a top-of-dashboard quick-add card optimized for ≤3 taps/clicks with clear feedback and no-budget compatibility.

### Changes Required:

#### 1. Quick-add form UI in dashboard

**File**: `coinductor/templates/home.html`

**Intent**: Give users one-screen expense entry with fast defaults and immediate context.

**Contract**: Render inline form card near top metrics; include amount, category selector (all active user categories), and prefilled-editable date.

#### 2. Feedback and state messaging

**File**: `coinductor/templates/home.html`, `coinductor/templates/base.html` (if message rendering adjustment needed)

**Intent**: Ensure user understands submit result and current budget state while maintaining low friction.

**Contract**: Successful submit shows confirmation (messages banner or equivalent), errors show inline, no-budget warning remains visible while allowing entry.

#### 3. UI assertions in integration tests

**File**: `coinductor/tests.py`

**Intent**: Guard against regressions in quick-add rendering and key state branches.

**Contract**: Add assertions for quick-add presence, on-track/off-track continuity, and no-budget branch with usable expense entry.

### Success Criteria:

#### Automated Verification:

- Dashboard UI tests pass for quick-add presence and state branches: `./.venv/bin/python manage.py test coinductor.tests`
- Tailwind build succeeds after template changes: `npm run build`

#### Manual Verification:

- Expense can be added from dashboard in ≤3 interactions in common path (amount + submit with prefilled defaults)
- Updated dashboard metrics and status are visible immediately after save

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 4: End-to-End Verification and Stability Pass

### Overview

Run final verification across form, view, and dashboard behavior for S-02 with focus on guardrail compliance and regression safety.

### Changes Required:

#### 1. Consolidated automated run

**File**: test files touched in Phases 1-3

**Intent**: Confirm full S-02 flow is stable across targeted and broad suites.

**Contract**: Execute targeted and full Django test runs, plus CSS build.

#### 2. Manual flow validation

**File**: `context/changes/add-expense-three-taps/plan.md` (this checklist)

**Intent**: Confirm real-user interaction quality around tap count and instant feedback.

**Contract**: Validate login -> quick-add -> recalculation loop, invalid-input recovery, and no-budget-compatible entry behavior.

### Success Criteria:

#### Automated Verification:

- Full affected suites pass: `./.venv/bin/python manage.py test budget coinductor`
- Project baseline passes: `./.venv/bin/python manage.py test`
- CSS pipeline remains healthy: `npm run build`

#### Manual Verification:

- End-to-end dashboard entry flow works with clear success/error feedback
- No regressions in auth routing or existing S-01 metric cards

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Testing Strategy

### Unit Tests:

- Expense form validation and ownership boundaries
- Required fields and default date behavior
- Existing service math remains stable after expense creation flow integration

### Integration Tests:

- Auth-protected dashboard POST behavior
- Successful quick-add creates expense and recalculates displayed metrics
- Invalid quick-add preserves user inputs and shows inline errors

### Manual Testing Steps:

1. Log in and submit quick-add expense with default date from dashboard.
2. Confirm spent/limit/status values change right after redirect.
3. Trigger validation error (e.g., empty amount) and verify inline messages.
4. Repeat in no-budget state and confirm entry still works with warning present.
5. Confirm flow remains within ≤3 interactions for common path.

## Performance Considerations

- Keep recalculation to existing aggregate service calls; avoid extra per-category queries in submit path.
- Keep form rendering server-side and lightweight to preserve perceived responsiveness.

## Migration Notes

- No schema migration required for S-02 by default.
- If form/test changes expose missing indexes later, treat as follow-up optimization outside this slice.

## References

- Related research: `context/changes/add-expense-three-taps/research.md`
- S-02 roadmap definition: `context/foundation/roadmap.md:101-112`
- PRD requirements: `context/foundation/prd.md:67-69`, `context/foundation/prd.md:86-87`
- Current dashboard/controller/service: `coinductor/views.py:39-52`, `coinductor/templates/home.html:19-87`, `budget/services.py:47-108`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Expense Form and Validation Layer

#### Automated

- [x] 1.1 Form tests pass for validation and ownership scenarios — e7afe81
- [x] 1.2 Existing budget service tests remain green — e7afe81

#### Manual

- [x] 1.3 Form rejects cross-user category and accepts valid same-user category — e7afe81

### Phase 2: Dashboard POST Flow Wiring

#### Automated

- [x] 2.1 Home integration tests pass including POST create/error paths — 5a45609
- [x] 2.2 Affected app suites pass together — 5a45609

#### Manual

- [x] 2.3 Valid dashboard submit creates expense and returns updated dashboard — 5a45609
- [x] 2.4 Invalid dashboard submit shows inline errors without clearing entered values — 5a45609

### Phase 3: Inline Quick-Add Dashboard UX

#### Automated

- [x] 3.1 Dashboard UI tests pass for quick-add presence and state branches — ba59ef1
- [x] 3.2 Tailwind build succeeds after template changes — ba59ef1

#### Manual

- [x] 3.3 Expense can be added from dashboard in ≤3 interactions in common path — ba59ef1
- [x] 3.4 Updated dashboard metrics and status are visible immediately after save — ba59ef1

### Phase 4: End-to-End Verification and Stability Pass

#### Automated

- [x] 4.1 Full affected suites pass — 7ac7481
- [x] 4.2 Project baseline passes — 7ac7481
- [x] 4.3 CSS pipeline remains healthy — 7ac7481

#### Manual

- [x] 4.4 End-to-end dashboard entry flow works with clear success/error feedback — 7ac7481
- [x] 4.5 No regressions in auth routing or existing S-01 metric cards — 7ac7481
