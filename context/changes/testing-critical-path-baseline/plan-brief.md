# Testing Critical Path Baseline — Plan Brief

> Full plan: `context/changes/testing-critical-path-baseline/plan.md`

## What & Why

This plan implements rollout Phase 1 from `context/foundation/test-plan.md` for risks #1, #2, and #5. The goal is to establish a stable integration-first safety net for dashboard guidance correctness, expense-entry flow behavior, and dashboard state rendering before later rollout phases add broader coverage. This reduces regression risk on the app’s core daily-feedback loop.

## Starting Point

The project already has dashboard logic in `budget/services.py`, a home-based dashboard view in `coinductor/views.py`, and broad but uneven tests in `budget/tests.py` and `coinductor/tests.py`. Prior reviews identified contract fragility (especially around `velocity_status`) and asked for durable manual-verification evidence.

## Desired End State

After this plan lands, risk-critical dashboard behaviors are protected by deterministic service + integration tests and a consistent view-context contract across render paths. Expense submit/redirect/update behavior is verified as the chosen proxy for the ≤3 taps guardrail in this phase. Manual verification evidence exists as a committed artifact in the change folder.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) |
| --- | --- | --- |
| Scope handling | Keep strict phase scope | Avoids derailing Phase 1 with unrelated failures while still fixing blockers tied to risks #1/#2/#5. |
| Guardrail verification | Integration proxy, not browser click-count tooling | Delivers high signal quickly using existing Django stack without adding premature E2E complexity. |
| Assertion style | Behavior-first (context + minimal user-visible markers) | Reduces brittleness from copy/style churn while preserving user-meaningful regression detection. |
| Verification command shape | Targeted suites plus one aggregate run | Balances fast iteration with a reliable regression backstop. |
| Manual evidence | Commit note under `reviews/` | Preserves auditable verification history aligned with prior implementation-review findings. |

## Scope

**In scope:**
- Normalize home dashboard context contract where required by risk assertions.
- Add/adjust service and integration tests for risks #1/#2/#5.
- Execute agreed automated commands and commit manual verification evidence.

**Out of scope:**
- New browser E2E tooling.
- Infra/configuration-heavy quality work.
- Unrelated test-suite stabilization outside Phase-1 risks.

## Architecture / Approach

Use current Django architecture as-is: service-layer dashboard computations (`budget/services.py`), home view orchestration (`coinductor/views.py`), and server-rendered state branches (`coinductor/templates/home.html`). The plan prioritizes test-contract hardening and branch-complete risk assertions rather than introducing new runtime components.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Baseline Contract Alignment | Stable view/test contracts for dashboard state assertions | False negatives from inconsistent render-path context |
| 2. Risk-Focused Protection Tests | Explicit protections for recalculation, flow behavior, and state branches | Hidden regressions in core dashboard loop |
| 3. Verification Evidence and Rollout Readiness | Final command-level verification + durable manual note | Non-auditable manual completion |

**Prerequisites:** `context/foundation/test-plan.md` Phase 1 active; change folder created (`testing-critical-path-baseline`).
**Estimated effort:** ~2-3 implementation sessions across 3 phases.

## Open Risks & Assumptions

- Existing unrelated failures may still exist; only blockers tied to risks #1/#2/#5 are addressed in this phase.
- Integration-level proxy for ≤3 taps assumes no immediate requirement for real-device click-count instrumentation.
- Dashboard template evolution can still affect copy-dependent assertions unless behavior-first style is applied consistently.

## Success Criteria (Summary)

- Risk #1/#2/#5 protections are represented by passing targeted service + integration tests.
- Combined regression command for touched apps passes after Phase-1 changes.
- Manual verification outcomes for critical states/flows are committed in `context/changes/testing-critical-path-baseline/reviews/manual-verification.md`.
