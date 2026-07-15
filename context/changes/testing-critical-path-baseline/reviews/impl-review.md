<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Testing Critical Path Baseline Implementation Plan

- **Plan**: `context/changes/testing-critical-path-baseline/plan.md`
- **Scope**: Full plan (Phases 1-3 of 3)
- **Date**: 2026-07-14
- **Verdict**: NEEDS ATTENTION
- **Findings**: 0 critical, 4 warnings, 1 observation

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| Plan Adherence | WARNING |
| Scope Discipline | WARNING |
| Safety & Quality | WARNING |
| Architecture | PASS |
| Pattern Consistency | WARNING |
| Success Criteria | PASS |

## Findings

### F1 — Planned service-boundary expansion in `budget/tests.py` not completed

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Plan Adherence
- **Location**: `budget/tests.py`
- **Detail**: Phase 2 planned additional/adjusted `DashboardMetricsServiceTests` coverage for boundary behavior. Implemented test additions in `budget/tests.py` focus on quick-add negative amount validation (`ExpenseQuickAddFormTests`) rather than expanding the service-boundary scenarios described in the phase.
- **Fix A ⭐ Recommended**: Add the missing service-boundary tests in `DashboardMetricsServiceTests`.
  - Strength: Aligns implementation with stated Phase 2 intent and keeps service risk coverage explicit.
  - Tradeoff: Adds more test maintenance surface.
  - Confidence: HIGH — target suite already exists and is passing.
  - Blind spot: None significant.
- **Fix B**: Update `plan.md` with an addendum that the existing service suite was accepted as sufficient and the phase centered on discovered negative-amount risk.
  - Strength: Keeps plan and actual scope synchronized without additional code churn.
  - Tradeoff: Leaves boundary coverage at current depth.
  - Confidence: MEDIUM — depends on whether current service tests are considered enough for risk #1.
  - Blind spot: No fresh gap analysis beyond current passing suite.
- **Decision**: FIXED (Applied Fix A — added service transition coverage in `DashboardMetricsServiceTests`)

### F2 — Bug-driven scope expansion is justified but undocumented in plan intent

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Scope Discipline
- **Location**: `budget/forms.py`, `budget/models.py`, `budget/migrations/0005_alter_expense_amount.py`
- **Detail**: The change added model/form validation + migration for negative expense amounts based on manual testing discovery. This is a good fix but was not reflected in the phase intent text/addendum, so plan-to-implementation traceability is weaker.
- **Fix**: Add a short scope-addendum note in `plan.md` (or review decision log) that this extra work was a manual-test-discovered blocker resolved in Phase 2.
- **Decision**: FIXED (Added Phase 2 scope addendum in `plan.md` for the negative-amount blocker)

### F3 — Expense positivity is only app-layer validated, not DB-enforced

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Safety & Quality
- **Location**: `budget/models.py:89`
- **Detail**: `MinValueValidator(0.01)` prevents negatives via model/form validation, but there is no database `CHECK` constraint. Direct SQL/bulk operations can still persist invalid negative values.
- **Fix**: Add `CheckConstraint(amount__gte=Decimal("0.01"))` on `Expense` with a data migration strategy for pre-existing invalid rows.
- **Decision**: FIXED (Added DB check constraint + data-normalizing migration `0006_expense_expense_amount_gte_0_01`)

### F4 — `budget-setup` IntegrityError path discards form error feedback

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Safety & Quality
- **Location**: `coinductor/views.py:123-132`
- **Detail**: In `action == "budget-setup"`, if `budget_form.save()` raises `IntegrityError`, an error is attached to the form but execution then falls through to the generic redirect path, losing inline error feedback and masking the form issue.
- **Fix**: Mirror the invalid-form branch by re-rendering `home.html` with populated context immediately after adding the non-field error.
- **Decision**: FIXED (IntegrityError path now re-renders `home.html` with inline form error context)

### F5 — Budget setup form performs N+1 budget lookups in initialization

- **Severity**: 👀 OBSERVATION
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Pattern Consistency
- **Location**: `budget/forms.py:20-31`
- **Detail**: `BudgetSetupForm.__init__` queries current-month budget per category (`.filter(...).first()` in a loop). This is acceptable at current scale but diverges from more batched query patterns used elsewhere.
- **Fix**: Optionally prefetch current-month budgets once and map by category id for O(1) lookups during field construction.
- **Decision**: FIXED (Batched budget lookup in `BudgetSetupForm.__init__` to remove N+1 pattern)
