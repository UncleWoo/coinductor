# Testing Quality Gates Cookbook Hardening Implementation Plan

## Overview

Implement rollout Phase 4 from `context/foundation/test-plan.md` by establishing a durable, minimal CI quality gate for existing Django tests and codifying repeatable quality-gate instructions in the cookbook.

## Current State Analysis

The project has a working local Django test suite (`manage.py test`) and mature risk-focused integration tests, but no repository CI workflow enforcing required checks on pull requests or mainline pushes. Cookbook section §6.5 is still placeholder-only, so contributors lack one canonical local/CI runbook for test gates.

## Desired End State

This change is complete when a CI workflow automatically runs `python manage.py test` on `pull_request` and `push` to `main` using Python 3.13, and the cookbook clearly documents how to run the same gate locally and in CI, including explicit deferred follow-ups for lint/typecheck/e2e/visual/hook gates.

### Key Discoveries:

- `context/foundation/test-plan.md:74-84` marks lint+typecheck and unit+integration as required gates, but no workflows currently exist.
- `.github/workflows/*` is absent, so there is no active CI status-check surface yet.
- `package.json:5-11` contains only Tailwind build/watch scripts and no JS/Python quality gate scripts.
- `requirements.txt` and existing plans use direct `python manage.py test` as the canonical test-entry pattern in this repository.

## What We're NOT Doing

- Introducing lint/typecheck tooling in this slice.
- Adding e2e automation, visual diff tooling, or multimodal checks.
- Refactoring existing app/runtime logic unrelated to quality gates.
- Reworking historical rollout plans beyond this change folder and cookbook updates in `context/foundation/test-plan.md`.

## Implementation Approach

Use the smallest operational gate first: add one CI workflow that runs the existing full Django suite with Python 3.13 on PR and main pushes. Then harden `test-plan.md` cookbook sections with practical runbook steps and a deferred follow-up map that makes future gate expansion explicit.

## Critical Implementation Details

### State sequencing

The CI workflow should be added and validated before cookbook hardening is finalized so documentation reflects the exact command and trigger semantics actually running in the repository.

## Phase 1: CI Test Gate Bootstrap

### Overview

Create the first required operational quality gate by wiring existing Django tests into GitHub Actions.

### Changes Required:

#### 1. Add workflow for test gate

**File**: `.github/workflows/test-gate.yml` (new)

**Intent**: Enforce regression protection in CI for PR and mainline changes using the current repository test command.

**Contract**: Workflow triggers on `pull_request` and `push` to `main`, uses Python 3.13, installs dependencies from `requirements.txt`, and runs `python manage.py test` as the canonical gate command.

#### 2. Align plan progress tracking

**File**: `context/changes/testing-quality-gates-cookbook-hardening/plan.md`

**Intent**: Track phase completion via the canonical Progress section contract.

**Contract**: Phase 1 rows are flipped only when workflow file is present and local verification command passes.

### Success Criteria:

#### Automated Verification:

- Workflow file is syntactically valid and present at `.github/workflows/test-gate.yml`
- Local canonical gate passes: `./.venv/bin/python3 manage.py test`

#### Manual Verification:

- A PR or push run shows the new workflow executing and reporting a status check for the repository

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Cookbook Hardening + Deferred Map

### Overview

Replace cookbook placeholders for quality gates with a practical runbook and explicit deferred expansion map.

### Changes Required:

#### 1. Populate cookbook quality-gate section

**File**: `context/foundation/test-plan.md`

**Intent**: Provide actionable local and CI gate usage instructions for the current repository baseline.

**Contract**: Section `6.5` documents canonical local command, CI workflow path, expected trigger behavior, and how to read gate outcomes.

#### 2. Document deferred follow-ups

**File**: `context/foundation/test-plan.md`

**Intent**: Make non-implemented gates explicit to prevent silent scope loss.

**Contract**: Section `6.6` records deferred gates (lint/typecheck/e2e/post-edit-hook/visual) with entry criteria for follow-up changes.

### Success Criteria:

#### Automated Verification:

- Test plan remains readable and includes non-placeholder content in sections `6.5` and `6.6`
- Canonical local gate remains green after documentation updates: `./.venv/bin/python3 manage.py test`

#### Manual Verification:

- A teammate can follow `6.5` instructions to run local and CI gate flow without additional tribal knowledge
- Deferred gates and rationale are explicitly visible in cookbook text

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Verification Evidence + Rollout Sync

### Overview

Finalize operational evidence and synchronize rollout state for this cross-cutting quality gate slice.

### Changes Required:

#### 1. Add manual verification artifact

**File**: `context/changes/testing-quality-gates-cookbook-hardening/reviews/manual-verification.md` (new)

**Intent**: Capture auditable proof that CI gate execution and cookbook instructions were verified.

**Contract**: Artifact records date, trigger used (PR/push), observed status-check result, and cookbook usability notes.

#### 2. Synchronize rollout status

**File**: `context/foundation/test-plan.md`, `context/changes/testing-quality-gates-cookbook-hardening/plan.md`

**Intent**: Keep rollout and change-level state aligned with completed quality-gate hardening.

**Contract**: Phase 4 row status in `test-plan.md` reflects completion intent and plan Progress rows are fully synchronized.

### Success Criteria:

#### Automated Verification:

- Canonical gate command remains green: `./.venv/bin/python3 manage.py test`
- Change plan Progress section includes complete phase state updates for Phase 3

#### Manual Verification:

- `reviews/manual-verification.md` exists with CI status-check evidence and cookbook validation notes
- No unresolved blockers remain for starting next quality-gate follow-up change

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Testing Strategy

### Unit Tests:

- No new unit tests in this change; rely on existing project unit coverage through canonical full-suite execution.

### Integration Tests:

- No new integration tests in this change; validate integration confidence via the full Django suite gate.

### Manual Testing Steps:

1. Run local `./.venv/bin/python3 manage.py test`.
2. Trigger CI via PR or push and confirm `test-gate` workflow status check appears.
3. Follow cookbook `6.5` runbook as written and confirm steps are sufficient.
4. Confirm deferred-gate map in `6.6` is explicit and actionable.

## Performance Considerations

- Full-suite gate is intentionally simple and reliable for current repository size; optimize with test splitting only if CI time becomes a measured bottleneck.

## Migration Notes

- No database or data migration is part of this change.
- Deferred follow-up should introduce lint/typecheck/e2e in separate slices to keep this rollout atomic.

## References

- Rollout source: `context/foundation/test-plan.md`
- Progress contract: `.github/skills/10x-plan/references/progress-format.md`
- Similar completed rollout plans:
  - `context/changes/testing-critical-path-baseline/plan.md`
  - `context/changes/testing-abuse-validation-boundaries/plan.md`
  - `context/changes/testing-duplicate-action-resilience/plan.md`
- Dependency baseline: `requirements.txt`

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: CI Test Gate Bootstrap

#### Automated

- [x] 1.1 CI workflow for Django test gate exists and is valid — fa2dba8
- [x] 1.2 Local canonical gate command passes (`./.venv/bin/python3 manage.py test`) — fa2dba8

#### Manual

- [x] 1.3 New workflow run appears as a status check on PR or push — 3cd6921

### Phase 2: Cookbook Hardening + Deferred Map

#### Automated

- [x] 2.1 Cookbook sections `6.5` and `6.6` are populated and non-placeholder — d995d23
- [x] 2.2 Canonical local gate remains green after cookbook updates — d995d23

#### Manual

- [x] 2.3 Cookbook runbook is usable without undocumented steps — d995d23
- [x] 2.4 Deferred follow-up map is explicit for lint/typecheck/e2e/visual/hook gates — d995d23

### Phase 3: Verification Evidence + Rollout Sync

#### Automated

- [x] 3.1 Canonical gate command remains green after final sync — 1b4a8b2
- [x] 3.2 Progress and rollout status artifacts are synchronized — 1b4a8b2

#### Manual

- [x] 3.3 `reviews/manual-verification.md` exists with CI and cookbook evidence — 1b4a8b2
- [x] 3.4 No unresolved blocker remains for follow-up quality-gate expansion — 1b4a8b2
