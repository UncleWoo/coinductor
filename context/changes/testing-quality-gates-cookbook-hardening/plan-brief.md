# Testing Quality Gates Cookbook Hardening — Plan Brief

> Full plan: `context/changes/testing-quality-gates-cookbook-hardening/plan.md`

## What & Why

This change introduces the first operational CI quality gate for the project and hardens the cookbook instructions that describe how to run and extend gates. The goal is to move from “quality gates described in strategy” to “quality gates enforced and repeatable” with minimal scope.

## Starting Point

The repo currently has no `.github/workflows/*` pipeline, while required gates are already defined in `context/foundation/test-plan.md` (§5). Existing local test confidence is built around `python manage.py test`, but there is no shared CI status-check path yet.

## Desired End State

A GitHub Actions workflow runs Django tests on `pull_request` and `push` to `main` with Python 3.13, giving immediate status-check feedback. Cookbook sections §6.5 and §6.6 are no longer placeholders and provide a clear runbook plus explicit deferred follow-ups for later gate expansion.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) | Source |
| --- | --- | --- | --- |
| Minimum gate scope | CI test gate + cookbook hardening | Fastest path to enforce required gate with least implementation risk. | Plan |
| Trigger policy | `pull_request` and `push` on `main` | Balances pre-merge safety with post-merge protection. | Plan |
| Python version | 3.13 | Matches declared project stack and local environment expectations. | Plan |
| Canonical CI command | `python manage.py test` | Reuses stable existing suite with no tooling migration overhead. | Plan |
| Cookbook coverage | Fill §6.5 + §6.6 only | Closes this phase without scope creep into unrelated sections. | Plan |
| Deferred-gate handling | Explicit deferred map with entry criteria | Prevents silent loss of lint/typecheck/e2e commitments. | Plan |

## Scope

**In scope:**
- Add `.github/workflows/test-gate.yml` for Django test gate.
- Validate canonical local test gate command.
- Populate cookbook §6.5 and §6.6 with operational guidance and deferred map.
- Capture manual verification evidence in change folder.

**Out of scope:**
- Introducing new lint/typecheck/e2e tooling in this change.
- Visual/multimodal gate implementation.
- Runtime feature refactors unrelated to gate/cookbook hardening.

## Architecture / Approach

Use one minimal CI workflow as the hard enforcement layer, then align documentation around the same canonical command. This creates a single source of operational truth: local and CI both run the same test gate, while deferred gates are explicitly tracked for follow-up slices.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. CI Test Gate Bootstrap | Working GH Actions test gate on PR/push(main) | CI setup drift or dependency mismatch |
| 2. Cookbook Hardening + Deferred Map | Practical runbook + explicit deferred-gate commitments | Ambiguous docs that fail adoption |
| 3. Verification Evidence + Rollout Sync | Auditable proof and synchronized rollout artifacts | Incomplete close-out state |

**Prerequisites:** GitHub Actions enabled, repository has valid Python test environment from `requirements.txt`, baseline tests pass locally.
**Estimated effort:** ~2-3 sessions across 3 phases.

## Open Risks & Assumptions

- Assumes `python manage.py test` remains an acceptable full-suite gate runtime in CI for current project size.
- Assumes no immediate requirement to enforce lint/typecheck before next quality-gate follow-up slice.
- CI branch protection rules may require manual repo-level adjustment outside repository files.

## Success Criteria (Summary)

- New CI workflow consistently reports test status checks on PR/push(main).
- Cookbook provides actionable local+CI runbook and explicit deferred-gate map.
- Manual verification evidence exists and rollout artifacts are synchronized without pending blockers.
