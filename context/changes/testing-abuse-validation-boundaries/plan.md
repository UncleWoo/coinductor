# Testing Abuse Validation Boundaries Implementation Plan

## Overview

Implement Phase 2 from `context/foundation/test-plan.md` by locking request-boundary protections for ownership abuse (risk #3) and untrusted-input validation drift (risk #6) across all dashboard POST actions.

## Current State Analysis

The app already enforces ownership and core validation in forms/models, but request-level contract coverage is incomplete: tests focus mostly on happy-path and selected invalid expense cases, while cross-user forged payload behavior is not comprehensively asserted for all actions.

## Desired End State

Phase is complete when all four actions (`add-expense`, `add-category`, `delete-category`, `budget-setup`) have explicit integration tests for anon and cross-user abuse attempts, plus a minimum malformed-input matrix that verifies stable no-write behavior and predictable response contracts.

### Key Discoveries:

- All mutable dashboard actions are multiplexed in one request entry point (`coinductor/views.py:43-177`), so request-boundary contracts must be tested per `action`.
- Ownership enforcement exists but is distributed (form queryset scoping + model clean checks) (`budget/forms.py:116-148`, `budget/models.py:72-77`, `budget/models.py:106-111`).
- Existing integration tests already establish the canonical style (`coinductor/tests.py`): POST to `reverse("home")`, assert redirect or inline form errors, and verify DB side effects.
- Only anonymous POST for `add-expense` is currently covered at request boundary; equivalent checks for other actions are missing (`coinductor/tests.py`).

## What We're NOT Doing

- No refactor of the action-multiplexer architecture into separate endpoints.
- No browser/e2e automation in this phase.
- No broad UX redesign; only behavior-preserving hardening where tests reveal true gaps.
- No infra/pipeline work (covered later in quality-gates phase).

## Implementation Approach

Integration-first test expansion in `coinductor/tests.py` will define abuse/validation contracts for all four actions. Runtime code changes are allowed only as minimal hardening needed to satisfy those contracts. Existing form/model protections remain the baseline; this phase closes request-level blind spots.

## Critical Implementation Details

### State sequencing

Because all actions share one view function, each abuse/validation test must assert both response shape and persistence effect (no write/no unauthorized mutation). This prevents false confidence from status-code-only assertions in mixed PRG + inline-error branches.

## Phase 1: Ownership Abuse Request Contracts

### Overview

Add request-level contract tests for anonymous and cross-user attempts across all dashboard actions.

### Changes Required:

#### 1. Cross-user and anonymous contract tests for all actions

**File**: `coinductor/tests.py`

**Intent**: Prove that unauthorized actors cannot read/mutate another user’s data through forged POST payloads.

**Contract**: Add integration tests covering anon and cross-user attempts for `add-expense`, `add-category`, `delete-category`, and `budget-setup`; assert zero unauthorized writes/mutations and stable response contract per action.

#### 2. Shared abuse-fixture setup

**File**: `coinductor/tests.py`

**Intent**: Keep ownership-abuse scenarios deterministic and easy to extend.

**Contract**: Introduce reusable fixtures for two users, separate category sets, and seeded budget/expense records to support cross-user assertions without brittle duplication.

### Success Criteria:

#### Automated Verification:

- Ownership abuse integration tests pass: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Existing ownership validation tests remain green: `./.venv/bin/python3 manage.py test budget.tests.OwnershipValidationTests`

#### Manual Verification:

- As anonymous user, each POST action redirects to login and creates no unauthorized data side effects
- As authenticated user A, forged references to user B categories are rejected or no-op without data leakage

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Validation Boundary Contract Matrix

### Overview

Establish a minimum malformed-input matrix per action to prevent server-side validation drift.

### Changes Required:

#### 1. Malformed payload integration matrix

**File**: `coinductor/tests.py`

**Intent**: Ensure invalid, missing, and nonsensical payloads are handled consistently at request boundary.

**Contract**: Add contract tests per action for malformed IDs/types, missing required fields, and nonsensical values; assert expected redirect or inline-error branch plus no unintended writes.

#### 2. Targeted form/model regression checks (only if needed)

**File**: `budget/tests.py` (only if gaps are exposed)

**Intent**: Pinpoint root-cause behavior when request-level tests expose lower-layer validation gaps.

**Contract**: Add narrow tests in form/model suites only for newly discovered boundary conditions required to stabilize request-level contract.

### Success Criteria:

#### Automated Verification:

- Validation matrix tests pass in home integration suite: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Budget form and expense form regressions remain green: `./.venv/bin/python3 manage.py test budget.tests.BudgetSetupFormTests budget.tests.ExpenseQuickAddFormTests`

#### Manual Verification:

- For each action, malformed payloads do not create or mutate protected records
- Inline errors remain user-visible where branch contract expects re-render behavior

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Minimal Hardening and Verification Evidence

### Overview

Apply only necessary runtime hardening revealed by tests, then capture durable manual evidence for the four-action smoke matrix.

### Changes Required:

#### 1. Minimal runtime hardening for failing contracts

**File**: `coinductor/views.py` (and `budget/forms.py` only if required)

**Intent**: Close proven request-boundary gaps with minimal blast radius and without architectural refactor.

**Contract**: Implement smallest behavior-preserving fixes needed for ownership and malformed-input contracts; keep existing route and PRG/error semantics intact.

#### 2. Manual verification artifact

**File**: `context/changes/testing-abuse-validation-boundaries/reviews/manual-verification.md` (new)

**Intent**: Provide auditable smoke evidence for anon/cross-user/malformed scenarios across all four actions.

**Contract**: Record date, action-by-action scenario table, expected vs observed outcome, and unresolved findings (if any).

### Success Criteria:

#### Automated Verification:

- Home integration suite passes with abuse + validation contracts: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Combined affected app suites pass: `./.venv/bin/python3 manage.py test budget coinductor`

#### Manual Verification:

- `reviews/manual-verification.md` exists with 4-action smoke matrix (anon + cross-user + malformed) and explicit pass/fail outcomes
- No unauthorized data mutation is observable after smoke scenarios

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Testing Strategy

### Unit Tests:

- Keep unit/form/model additions minimal and only when request-level contract tests expose a lower-layer gap.
- Prioritize ownership invariants and validation boundaries over broad coverage expansion.

### Integration Tests:

- Expand `HomeDashboardViewTests` as canonical request-boundary contract suite for all four actions.
- Assert both response contract and persistence side effects for each abuse scenario.

### Manual Testing Steps:

1. Run anonymous POST attempts for each action and verify redirect + no write.
2. Run authenticated cross-user forged payload attempts and verify no unauthorized mutation.
3. Run malformed payload attempts per action and verify contract-consistent error handling.
4. Document outcomes in `reviews/manual-verification.md`.

## Performance Considerations

- Keep new tests deterministic and scoped to avoid suite bloat.
- Reuse fixtures to minimize repeated setup overhead in integration tests.

## Migration Notes

- No schema migration is planned for this phase.
- If a failing contract suggests data-level hardening, treat migration as explicit follow-up instead of implicit scope creep.

## References

- Phase source: `context/foundation/test-plan.md`
- Prior baseline phase: `context/changes/testing-critical-path-baseline/plan.md`
- Related ownership review history: `context/changes/domain-models-migrations/reviews/impl-review.md`
- Related pattern reference: `context/changes/add-expense-three-taps/plan.md`
- Runtime entry point: `coinductor/views.py:43-177`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Ownership Abuse Request Contracts

#### Automated

- [x] 1.1 Ownership abuse integration tests pass
- [x] 1.2 Existing ownership validation tests remain green

#### Manual

- [ ] 1.3 Anonymous POST actions redirect to login with no unauthorized side effects
- [ ] 1.4 Cross-user forged references do not mutate protected records

### Phase 2: Validation Boundary Contract Matrix

#### Automated

- [ ] 2.1 Validation matrix tests pass in home integration suite
- [ ] 2.2 Budget and expense form regression tests remain green

#### Manual

- [ ] 2.3 Malformed payloads per action do not create or mutate protected records
- [ ] 2.4 Inline error behavior remains stable where expected

### Phase 3: Minimal Hardening and Verification Evidence

#### Automated

- [ ] 3.1 Home integration suite passes with abuse and validation contracts
- [ ] 3.2 Combined affected app suites pass

#### Manual

- [ ] 3.3 `reviews/manual-verification.md` exists with full 4-action smoke matrix and outcomes
- [ ] 3.4 No unauthorized data mutation is observable after manual smoke scenarios
