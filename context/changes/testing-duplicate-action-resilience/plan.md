# Testing Duplicate Action Resilience Implementation Plan

## Overview

Implement Phase 3 from `context/foundation/test-plan.md` by preventing duplicate submit/retry from creating extra expense side effects, while preserving intentional second expense entries.

## Current State Analysis

`add-expense` currently persists a new `Expense` row for every valid POST and then redirects. This gives PRG behavior but does not guarantee single-use semantics for replayed requests (double-click/retry). Because dashboard metrics are sum-based, duplicate rows directly distort remaining budget, daily limit, and pacing signals.

## Desired End State

Repeated submit/retry with the same form intent is treated as a no-op, while a legitimate second submit (fresh form/token) still creates a second expense. Integration tests prove replay resilience and metrics correctness, and manual evidence confirms the three critical user scenarios.

### Key Discoveries:

- Expense create path is direct save on valid POST (`coinductor/views.py:46-54`, `budget/forms.py:143-147`).
- Metrics consume aggregated expense sum, so duplicates inflate accounting outputs (`budget/services.py:62-73`, `budget/services.py:89-90`).
- Existing duplicate-safe pattern already exists for budgets via upsert (`budget/forms.py:72-77`), but not for expenses.
- Current integration suite has strong request-contract patterns and is the cheapest high-signal place to enforce replay behavior (`coinductor/tests.py`).

## What We're NOT Doing

- No endpoint architecture refactor (still using `home` action multiplexer).
- No broad dedupe heuristics based on payload+time windows.
- No DB migration for global idempotency ledger in this phase.
- No e2e/browser automation in this phase.

## Implementation Approach

Introduce a session-scoped, single-use idempotency token for `add-expense`. Token is rendered with the expense form, consumed once on successful processing, and replay attempts with the same token become silent no-op redirects. A new token (fresh form render) allows intentional second identical expense creation.

## Critical Implementation Details

### State sequencing

Replay protection must execute before persistence but after basic action routing. Token consume flow must be single-use and tied to the active session so a repeated POST cannot pass twice, while a fresh GET-rendered form can produce a new valid submit path.

## Phase 1: Duplicate Contract Characterization

### Overview

Define executable request contracts for duplicate resilience before changing runtime behavior.

### Changes Required:

#### 1. Integration tests for replay and intentional second submit

**File**: `coinductor/tests.py`

**Intent**: Codify how duplicate retries and intentional repeated entries should behave at HTTP boundary.

**Contract**: Add integration tests that assert: same-token replay is no-op (no second write), fresh-token second submit creates second row, and both paths preserve expected PRG response behavior.

#### 2. Metrics overlap assertions (risk #4 + #1)

**File**: `coinductor/tests.py`, `budget/tests.py` (only if needed)

**Intent**: Ensure replay resilience prevents metric drift from accidental duplicate persistence.

**Contract**: Assert `total_spent`/`remaining_budget` changes exactly once for replayed submit and changes twice only for intentional second submit.

### Success Criteria:

#### Automated Verification:

- Duplicate-contract integration tests pass: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Existing metrics service tests remain green: `./.venv/bin/python3 manage.py test budget.tests.DashboardMetricsServiceTests`

#### Manual Verification:

- Double-click style replay does not create a second expense row
- Intentional second submit from freshly rendered form still creates a second row

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Idempotency Token Hardening

### Overview

Implement session-scoped single-use token enforcement for `add-expense`.

### Changes Required:

#### 1. Token plumbing in expense form request flow

**File**: `coinductor/views.py`, `coinductor/templates/partials/expense_form.html`

**Intent**: Carry a single-use token through render and submit so replay can be deterministically identified.

**Contract**: Expense form includes hidden idempotency token; `add-expense` branch validates and consumes token from session registry before save; replayed token returns silent no-op redirect.

#### 2. Minimal helper wiring for token lifecycle

**File**: `coinductor/views.py` (and optional helper colocated in same module)

**Intent**: Keep token generation/consume lifecycle explicit and testable without architecture churn.

**Contract**: Introduce minimal lifecycle helpers for issue + consume semantics scoped to authenticated session and `add-expense` action only.

### Success Criteria:

#### Automated Verification:

- Home integration suite passes with token replay protections: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Combined affected suites pass: `./.venv/bin/python3 manage.py test budget coinductor`

#### Manual Verification:

- Replaying same request/token no longer creates duplicate expense entry
- New form render produces new token that allows intentional second identical expense

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Regression and Verification Evidence

### Overview

Finalize duplicate-resilience protection with evidence artifact and stability checks.

### Changes Required:

#### 1. Manual verification artifact for replay scenarios

**File**: `context/changes/testing-duplicate-action-resilience/reviews/manual-verification.md` (new)

**Intent**: Record auditable outcomes for the three critical resilience scenarios.

**Contract**: Capture pass/fail table for (a) double-click replay, (b) network retry replay, (c) intentional second submit with fresh token; include observed accounting behavior.

#### 2. Plan progress synchronization

**File**: `context/changes/testing-duplicate-action-resilience/plan.md`

**Intent**: Keep execution state aligned with completed automated/manual criteria.

**Contract**: `## Progress` rows are the only source of completion state and are updated stepwise.

### Success Criteria:

#### Automated Verification:

- Final integration suite for duplicate contracts passes: `./.venv/bin/python3 manage.py test coinductor.tests.HomeDashboardViewTests`
- Aggregate affected suites stay green: `./.venv/bin/python3 manage.py test budget coinductor`

#### Manual Verification:

- `reviews/manual-verification.md` exists with 3-scenario duplicate smoke outcomes
- No accidental duplicate accounting side effects observed in replay scenarios

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Testing Strategy

### Unit Tests:

- Keep unit-level additions minimal; prioritize integration contracts around request replay semantics.
- Add targeted lower-layer tests only if integration failures reveal helper-level gaps.

### Integration Tests:

- Use `HomeDashboardViewTests` as primary contract suite for replay/no-op/new-token behavior.
- Assert both persistence side effects and dashboard metric correctness.

### Manual Testing Steps:

1. Submit expense and immediately replay same request/token (double-click simulation).
2. Simulate retry of same submit payload/token and verify no second write.
3. Submit same values again from freshly rendered form and verify intentional second write.
4. Record outcomes in `reviews/manual-verification.md`.

## Performance Considerations

- Session-scoped token registry should remain bounded and action-specific.
- Test matrix should stay focused on high-signal replay scenarios to avoid suite bloat.

## Migration Notes

- No schema migration is planned.
- If future requirements demand cross-device/global idempotency, treat DB-backed token ledger as follow-up slice.

## References

- Phase source: `context/foundation/test-plan.md`
- Related prior slice: `context/changes/add-expense-three-taps/plan.md`
- Related baseline protection: `context/changes/testing-critical-path-baseline/plan.md`
- Related abuse-contract baseline: `context/changes/testing-abuse-validation-boundaries/plan.md`
- Runtime entry path: `coinductor/views.py:43-177`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Duplicate Contract Characterization

#### Automated

- [x] 1.1 Duplicate-contract integration tests pass — 1f7af71
- [x] 1.2 Existing metrics service tests remain green — 1f7af71

#### Manual

- [x] 1.3 Replay submit does not create a second expense row — 431de16
- [x] 1.4 Intentional second submit from fresh form creates second row — 431de16

### Phase 2: Idempotency Token Hardening

#### Automated

- [x] 2.1 Home integration suite passes with token replay protections — 3abd987
- [x] 2.2 Combined affected suites pass — 3abd987

#### Manual

- [x] 2.3 Replaying same token is a no-op without duplicate write — 431de16
- [x] 2.4 Fresh-token submit allows intentional second identical expense — 431de16

### Phase 3: Regression and Verification Evidence

#### Automated

- [x] 3.1 Final duplicate-contract integration suite passes — 431de16
- [x] 3.2 Aggregate affected suites stay green — 431de16

#### Manual

- [x] 3.3 `reviews/manual-verification.md` exists with 3-scenario smoke outcomes — 431de16
- [x] 3.4 No accidental duplicate accounting side effects observed in replay scenarios — 431de16
