<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Domain Models & Migrations Implementation Plan

- **Plan**: `context/changes/domain-models-migrations/plan.md`
- **Scope**: Phase 1-4 of 4
- **Date**: 2026-06-29
- **Verdict**: NEEDS ATTENTION
- **Findings**: 0 critical, 4 warnings, 2 observations

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| Plan Adherence | WARNING |
| Scope Discipline | WARNING |
| Safety & Quality | WARNING |
| Architecture | PASS |
| Pattern Consistency | PASS |
| Success Criteria | WARNING |

## Findings

### F1 — Budget/Expense can cross-link to another user's category

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Safety & Quality
- **Location**: `budget/models.py:44-49,66-71`
- **Detail**: `Budget.user` and `Expense.user` are independent of `category.user`, so a record can point to a category owned by a different user.
- **Fix**: Enforce ownership consistency (`category.user == user`) in model validation and add tests for mismatch rejection.
  - Strength: Prevents tenant-mixing at write time.
  - Tradeoff: Adds validation path to model save/forms.
  - Confidence: HIGH — direct schema behavior confirms risk.
  - Blind spot: None significant.
- **Decision**: FIXED (Fix now)

### F2 — Signal lacks idempotency guard for default-category seeding

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Safety & Quality
- **Location**: `budget/signals.py:10-17`
- **Detail**: `post_save` receiver has no `dispatch_uid`; category rows also lack a `(user, name)` uniqueness guard. Duplicate inserts are possible if handler registration or create path runs more than once.
- **Fix**: Add `dispatch_uid` on receiver and enforce uniqueness for Category by `(user, name)`.
  - Strength: Makes default seeding robust and deterministic.
  - Tradeoff: Adds one migration for category uniqueness.
  - Confidence: HIGH — standard Django signal hardening pattern.
  - Blind spot: Existing duplicate rows would need cleanup before unique migration.
- **Decision**: FIXED (Fix now)

### F3 — Automated Phase 1 import check is not reproducible as written

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Success Criteria
- **Location**: `context/changes/domain-models-migrations/plan.md:95`
- **Detail**: `python -c "from budget.models import ..."` fails without Django setup; rerun of this exact check returned non-zero.
- **Fix**: Update criterion command to use Django setup (`DJANGO_SETTINGS_MODULE=...` + `django.setup()`) or `manage.py shell -c`.
- **Decision**: FIXED (Fix now)

### F4 — First-day-of-month validator was added but not planned

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Plan Adherence
- **Location**: `budget/models.py:15-17,50`
- **Detail**: Plan contract required a `DateField` for month but did not include runtime validator enforcement; implementation added stricter behavior.
- **Fix**: Either document this stricter rule in plan addendum or remove validator for strict plan parity.
- **Decision**: FIXED (Fix now)

### F5 — Scaffold stubs committed though out of scope

- **Severity**: 👀 OBSERVATION
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Scope Discipline
- **Location**: `budget/views.py:1-3`, `budget/tests.py:1-3`
- **Detail**: Placeholder stubs were committed even though this stream was data-layer-focused.
- **Fix**: Remove stubs now or keep intentionally with a short note in the plan.
- **Decision**: FIXED (Fix now)

### F6 — Manual checks are marked complete but only externally evidenced

- **Severity**: 👀 OBSERVATION
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Success Criteria
- **Location**: `context/changes/domain-models-migrations/plan.md:286-322`
- **Detail**: Diff cannot independently prove manual admin/signup checks; completion relies on operator confirmation.
- **Fix**: Optionally automate highest-value manual flows in tests.
- **Decision**: FIXED (Fix now)
