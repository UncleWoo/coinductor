# Testing Duplicate Action Resilience — Plan Brief

> Full plan: `context/changes/testing-duplicate-action-resilience/plan.md`

## What & Why

This change closes risk #4 from the test rollout: duplicate submit/retry creating extra expense side effects. Because dashboard guidance is calculated from summed expenses, replayed writes can immediately distort daily limit and on-track status, so resilience must be enforced at request boundary.

## Starting Point

`add-expense` currently saves a new row on every valid POST, then redirects (PRG). That prevents browser resubmission prompts, but does not provide deterministic single-use semantics for replayed requests with the same intent.

## Desired End State

A replay of the same submit intent is treated as no-op, while a deliberate second submit from a freshly rendered form remains allowed. Integration tests prove this contract and verify metrics stay correct under replay vs intentional-repeat scenarios.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) |
| --- | --- | --- |
| Scope focus | `add-expense` primary + smoke confidence around surrounding flow | Risk #4 is accounting duplication, concentrated in expense creation path. |
| Replay strategy | Session-scoped single-use idempotency token | Gives deterministic replay blocking without payload heuristics or schema changes. |
| UX on replay | Silent no-op + PRG redirect | Preserves existing low-friction dashboard behavior. |
| Intentional duplicate handling | Allowed via fresh token | Identical values can be legitimate separate expenses. |
| Test strategy | Integration-first in `HomeDashboardViewTests` | Highest signal at request/persistence/metrics boundary where risk manifests. |
| Manual evidence | 3-scenario smoke matrix artifact | Distinguishes replay prevention from valid intentional second submit. |

## Scope

**In scope:**
- Duplicate/retry contract tests for `add-expense`
- Session-scoped token issue/consume flow
- Replay no-op behavior + intentional second-submit preservation
- Manual verification artifact for three replay scenarios

**Out of scope:**
- Endpoint refactor
- DB-backed global idempotency ledger
- Broad dedupe heuristics by payload/time window
- Browser e2e automation

## Architecture / Approach

Keep existing FBV architecture. Add hidden idempotency token to expense form, store active token state in session, consume token once on successful processing, and treat replayed token as no-op redirect. Back this with integration assertions on write count and metrics outputs.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Duplicate contract characterization | Executable replay vs intentional-repeat behavior tests | Wrong contract assumptions before hardening |
| 2. Idempotency token hardening | Runtime single-use token enforcement in `add-expense` path | Token lifecycle bugs creating false positives/negatives |
| 3. Regression and evidence | Stability run + manual 3-scenario smoke artifact | Incomplete proof of real-world replay behavior |

**Prerequisites:** Baseline and abuse phases are complete; current test suite green.
**Estimated effort:** ~2-3 sessions across 3 phases.

## Open Risks & Assumptions

- Assumption: session-scoped protection is sufficient for this phase (single user, dashboard flow).
- Risk: token lifecycle edge cases (stale token reuse, page-back behavior) may require small helper adjustments.
- Risk: future multi-device or API clients could need stronger DB-backed idempotency semantics.

## Success Criteria (Summary)

- Replay submit does not create extra expense rows or inflate spending metrics.
- Intentional second submit from fresh form still creates legitimate second row.
- Manual smoke artifact confirms double-click, retry replay, and fresh-token scenarios.
