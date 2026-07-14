# Testing Abuse Validation Boundaries — Plan Brief

> Full plan: `context/changes/testing-abuse-validation-boundaries/plan.md`

## What & Why

This change delivers Phase 2 of the test rollout: request-boundary protection for ownership abuse and malformed input handling. The goal is to make sure unauthorized or tampered dashboard POST payloads cannot mutate another user’s data and that server-side validation stays consistent with UI expectations.

## Starting Point

The app already has ownership and validation logic in forms/models, and all dashboard mutations are routed through one `home` POST action switch. Existing tests cover key happy-path and selected invalid cases, but do not comprehensively assert cross-user abuse contracts across all four actions.

## Desired End State

All dashboard POST actions (`add-expense`, `add-category`, `delete-category`, `budget-setup`) have explicit integration contracts for anonymous, cross-user forged, and malformed payload scenarios. Failing behaviors are minimally hardened without architecture refactor, and manual smoke evidence is recorded in a durable review artifact.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) |
| --- | --- | --- |
| Scope breadth | Cover all 4 POST actions | Risks #3 and #6 apply to every mutation path, not just expense flow. |
| Unauthorized contract style | Stable no-op/no-write behavior, preserving branch UX | Aligns with existing PRG + inline-error behavior while preventing mutation leaks. |
| Test layer priority | Integration-first in `HomeDashboardViewTests` | Request boundary is the core risk surface in this phase. |
| Delivery sequence | Ownership abuse first, validation matrix second | Prioritizes highest-impact security risk before broader malformed input matrix. |
| Runtime changes policy | Minimal hardening only where tests fail | Limits blast radius and avoids scope creep into architecture refactor. |
| Manual proof format | 4-action smoke table in `reviews/manual-verification.md` | Gives auditable evidence that contracts work end-to-end. |

## Scope

**In scope:**
- Integration tests for anon and cross-user abuse attempts on all four actions
- Minimum malformed-input contract matrix per action
- Minimal runtime hardening needed to satisfy new contracts
- Manual verification artifact with explicit outcomes

**Out of scope:**
- Endpoint architecture refactor
- Browser/e2e automation
- Infra/CI quality-gate work
- Broad UX redesign

## Architecture / Approach

Use the existing `home` action multiplexer as the single contract surface. Expand integration tests to assert response + persistence behavior per action and scenario type. Keep form/model checks as supporting safeguards, and only patch runtime branches that tests prove unsafe.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Ownership abuse contracts | Full anon/cross-user request-boundary coverage for all actions | Missing one action leaves exploitable gap |
| 2. Validation boundary matrix | Stable malformed-input behavior contracts per action | Over-testing can bloat suite without extra signal |
| 3. Minimal hardening + evidence | Targeted fixes + auditable manual smoke matrix | Scope creep into refactor instead of hardening |

**Prerequisites:** Phase 1 (`testing-critical-path-baseline`) already completed; current test suite green.
**Estimated effort:** ~2-3 sessions across 3 phases.

## Open Risks & Assumptions

- Assumption: current action-level response contracts (redirect vs inline errors) are acceptable and should remain stable.
- Risk: some malformed-input cases may reveal deeper constraints that suggest follow-up refactor outside this phase.
- Risk: adding broad matrix tests can increase maintenance cost if not kept contract-focused.

## Success Criteria (Summary)

- Unauthorized and forged request attempts cannot mutate protected user data.
- Malformed payloads are consistently rejected with predictable response behavior.
- Manual smoke evidence confirms four-action contracts and no data leakage side effects.
