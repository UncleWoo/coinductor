# Testing Critical Path Baseline Implementation Plan

## Overview

Implement rollout Phase 1 from `context/foundation/test-plan.md` by establishing integration-first protection for risks #1, #2, and #5: incorrect dashboard guidance, degraded expense-entry flow usability, and dashboard-state rendering regressions.

## Current State Analysis

The codebase already has dashboard metrics service logic and substantial tests, but coverage is uneven against the new risk-map contracts. Existing patterns are Django `TestCase` with server-rendered integration checks (`coinductor/tests.py`, `budget/tests.py`), while known fragility remains in copy-heavy assertions and inconsistent view-context shape on some render branches.

## Desired End State

Phase 1 is complete when:
- risk #1 is protected by deterministic service and integration assertions for recalculation/state transitions;
- risk #2 is protected by submit/redirect/update integration checks that proxy the ≤3 taps guardrail without introducing new browser tooling;
- risk #5 is protected by explicit state-branch assertions (`no_budget`, `no_expenses`, metrics state), with durable manual verification evidence committed in this change folder.

### Key Discoveries:

- `budget/services.py:47-108` is already the source of truth for dashboard math and state branching.
- `coinductor/views.py:44-169` handles all dashboard actions, but context contract consistency differs by render path.
- `coinductor/templates/home.html:19-261` contains critical state branches and user-visible signals for Phase-1 risks.
- Prior reviews flagged velocity-status contract/test fragility and asked for durable manual evidence (`context/changes/ui-improvements/reviews/impl-review.md`, `context/changes/dashboard-on-track-daily-limit/reviews/impl-review.md`).

## What We're NOT Doing

- Adding browser E2E tooling in this phase.
- Solving infra/configuration-heavy quality concerns (explicitly excluded in `test-plan.md` §7).
- Refactoring dashboard business logic beyond what is required to stabilize risk-contract behavior.
- Fixing unrelated failing tests outside risks #1/#2/#5 unless they directly block this phase’s verification commands.

## Implementation Approach

Use an integration-first strategy aligned with existing Django patterns:
1. align and stabilize baseline test/view contracts that Phase-1 assertions rely on;
2. add or adjust targeted service and home-view tests around the risk-map behaviors;
3. validate with focused suites plus one aggregate run, then store manual verification notes under `reviews/`.

## Critical Implementation Details

### State sequencing

Every render path that returns `home.html` must expose the same minimum dashboard state contract used by tests (`dashboard`, `empty_state`, `on_track`, velocity classification), otherwise risk #5 checks become false negatives tied to branch-specific context omissions.

## Phase 1: Baseline Contract Alignment

### Overview

Stabilize the existing dashboard test harness and view-context contract so Phase-1 risk tests fail only for real regressions, not setup inconsistencies.

### Changes Required:

#### 1. Home view context contract normalization

**File**: `coinductor/views.py`

**Intent**: Ensure every `home.html` render branch provides a consistent dashboard context contract for risk-state assertions.

**Contract**: All `home` render paths expose the same required state keys used by the dashboard template and integration tests.

#### 2. Baseline dashboard test fixture normalization

**File**: `coinductor/tests.py`

**Intent**: Remove baseline fixture/assertion inconsistencies that obscure risk-focused failures.

**Contract**: Dashboard test setup, login usage, and state-assertion entry points are coherent and reusable for subsequent risk checks.

### Success Criteria:

#### Automated Verification:

- Home dashboard test module runs without setup/contract errors: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Dashboard view render branches satisfy required context contract assertions: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`

#### Manual Verification:

- Login to dashboard and trigger at least one form-validation re-render path; confirm dashboard shell still renders expected status area

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Risk-Focused Protection Tests

### Overview

Implement targeted protection for risk #1, #2, and #5 using service-level and integration-level tests with behavior-first oracles.

### Changes Required:

#### 1. Recalculation and pace-boundary protections (risk #1)

**File**: `budget/tests.py`

**Intent**: Guard daily-limit/on-track correctness against month-scope, tolerance-boundary, and transition regressions.

**Contract**: Service tests assert behavior outcomes (not copied implementation internals) for budget/expense changes and boundary conditions.

#### 2. Expense submit/redirect/update flow protections (risk #2)

**File**: `coinductor/tests.py`

**Intent**: Protect quick-add flow usability proxy via request/response behavior and immediate state update checks.

**Contract**: Integration tests cover valid submit redirect, invalid submit inline errors, and post-submit dashboard state updates in authenticated context.

#### 3. Dashboard state-branch protections (risk #5)

**File**: `coinductor/tests.py`, `coinductor/templates/home.html`

**Intent**: Ensure `no_budget`, `no_expenses`, and metrics states render correct user-facing signals and remain assertion-stable.

**Contract**: Tests assert branch-specific behavior with minimal critical user-visible markers plus stable state contracts.

### Success Criteria:

#### Automated Verification:

- Service risk tests for dashboard math and pace boundaries pass: `./.venv/bin/python3 manage.py test budget.tests.DashboardMetricsServiceTests`
- Home dashboard integration tests for state branches and expense flow pass: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Combined app-level regression pass remains green for touched areas: `./.venv/bin/python3 manage.py test budget coinductor`

#### Manual Verification:

- Validate `no_budget`, `no_expenses`, and metrics states in browser and confirm displayed status aligns with seeded data changes
- Submit one valid and one invalid expense from dashboard; confirm redirect/error behavior matches expected flow

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Verification Evidence and Rollout Readiness

### Overview

Finalize Phase-1 completion evidence, preserving a durable manual verification artifact and confirming command-level readiness for subsequent rollout phases.

### Changes Required:

#### 1. Manual verification artifact

**File**: `context/changes/testing-critical-path-baseline/reviews/manual-verification.md` (new)

**Intent**: Record concise, auditable human verification outcomes for the Phase-1 risk scenarios.

**Contract**: Note includes date, tested scenarios mapped to risks #1/#2/#5, and explicit outcome summary.

#### 2. Plan progress synchronization

**File**: `context/changes/testing-critical-path-baseline/plan.md`

**Intent**: Keep progress tracking mechanically aligned with completed automated/manual criteria.

**Contract**: `## Progress` remains the single source of truth with unchanged step titles and per-step checkbox updates.

### Success Criteria:

#### Automated Verification:

- Final targeted + aggregate verification commands executed for this phase set: `./.venv/bin/python3 manage.py test budget.tests.DashboardMetricsServiceTests`, `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`, `./.venv/bin/python3 manage.py test budget coinductor`

#### Manual Verification:

- `reviews/manual-verification.md` exists with completed scenario outcomes for risks #1/#2/#5 and no unresolved findings

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Testing Strategy

### Unit Tests:

- Service-level checks for month-scoped totals, tolerance thresholds, and state transitions in `DashboardMetricsServiceTests`

### Integration Tests:

- Home route auth + dashboard rendering contract
- Expense add POST flow (valid/invalid) with recalculated dashboard feedback
- Dashboard branch assertions for `no_budget`, `no_expenses`, and metrics state

### Manual Testing Steps:

1. Sign in and verify dashboard status area renders.
2. Trigger each dashboard state (`no_budget`, `no_expenses`, metrics) with seeded data.
3. Submit valid expense and verify redirected state update.
4. Submit invalid expense and verify inline errors without flow break.
5. Record outcomes in `reviews/manual-verification.md`.

## Performance Considerations

- Keep tests deterministic and scoped to avoid introducing slow end-to-end layers in baseline phase.
- Prefer targeted test classes in inner loop, with one aggregate run as regression backstop.

## Migration Notes

- No schema migration expected in this phase.
- If data assumptions are needed for test setup, use model-level setup only; do not alter production migrations.

## References

- Phase source: `context/foundation/test-plan.md`
- Related prior research: `context/changes/add-expense-three-taps/research.md`
- Prior implementation lessons: `context/changes/dashboard-on-track-daily-limit/plan.md`
- Prior review findings: `context/changes/dashboard-on-track-daily-limit/reviews/impl-review.md`
- Prior review findings: `context/changes/ui-improvements/reviews/impl-review.md`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Baseline Contract Alignment

#### Automated

- [x] 1.1 Home dashboard test module runs without setup/contract errors — cbb3888
- [x] 1.2 Dashboard view render branches satisfy required context contract assertions — cbb3888

#### Manual

- [x] 1.3 Login to dashboard and trigger at least one form-validation re-render path; confirm dashboard shell still renders expected status area — cbb3888

### Phase 2: Risk-Focused Protection Tests

#### Automated

- [x] 2.1 Service risk tests for dashboard math and pace boundaries pass — 538b5a6
- [x] 2.2 Home dashboard integration tests for state branches and expense flow pass — 538b5a6
- [x] 2.3 Combined app-level regression pass remains green for touched areas — 538b5a6

#### Manual

- [x] 2.4 Validate `no_budget`, `no_expenses`, and metrics states in browser and confirm displayed status aligns with seeded data changes — 538b5a6
- [x] 2.5 Submit one valid and one invalid expense from dashboard; confirm redirect/error behavior matches expected flow — 538b5a6

### Phase 3: Verification Evidence and Rollout Readiness

#### Automated

- [x] 3.1 Final targeted + aggregate verification commands executed for this phase set — cc21a0a

#### Manual

- [x] 3.2 `reviews/manual-verification.md` exists with completed scenario outcomes for risks #1/#2/#5 and no unresolved findings — cc21a0a
