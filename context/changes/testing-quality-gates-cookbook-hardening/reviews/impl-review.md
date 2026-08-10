<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Testing Quality Gates Cookbook Hardening Implementation Plan

- **Plan**: `context/changes/testing-quality-gates-cookbook-hardening/plan.md`
- **Scope**: Phases 1-3 of 3
- **Date**: 2026-07-15
- **Verdict**: NEEDS ATTENTION
- **Findings**: 0 critical, 3 warnings, 0 observations

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| Plan Adherence | WARNING |
| Scope Discipline | PASS |
| Safety & Quality | WARNING |
| Architecture | PASS |
| Pattern Consistency | WARNING |
| Success Criteria | PASS |

## Findings

### F1 — GitHub Actions are not pinned to immutable SHAs

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Safety & Quality
- **Location**: `.github/workflows/test-gate.yml:14,17`
- **Detail**: CI uses mutable action tags (`actions/checkout@v4`, `actions/setup-python@v5`), which leaves a supply-chain update surface if upstream tags move.
- **Fix**: Pin both actions to immutable full commit SHAs (optionally annotate with the human-readable tag in comments).
  - Strength: Removes mutable-tag drift without changing workflow behavior.
  - Tradeoff: Requires periodic SHA maintenance during action upgrades.
  - Confidence: HIGH — standard hardening practice for CI workflows.
  - Blind spot: None significant.
- **Decision**: FIXED

### F2 — Phase 1 progress SHA does not match workflow-introducing commit

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Plan Adherence
- **Location**: `context/changes/testing-quality-gates-cookbook-hardening/plan.md:202-203`
- **Detail**: Progress rows `1.1` and `1.2` reference `3cd6921`, while `.github/workflows/test-gate.yml` history shows the workflow was introduced in `fa2dba8`. This weakens auditability of progress-to-commit evidence.
- **Fix A ⭐ Recommended**: Correct the Phase 1 SHA evidence in plan progress to reference the commit that actually introduced the workflow file.
  - Strength: Restores traceability between recorded progress and repository history.
  - Tradeoff: Rewrites historical metadata in the plan.
  - Confidence: HIGH — direct `git log` evidence for the workflow file.
  - Blind spot: Did not validate whether team intentionally uses phase-close commit SHA rather than introducing commit SHA.
- **Fix B**: Keep current SHA and add an explicit note in the plan clarifying that phase rows carry phase-close commit SHA, not introducing commit SHA.
  - Strength: Preserves existing recorded metadata unchanged.
  - Tradeoff: Keeps mismatch against file-level history and can confuse future reviewers.
  - Confidence: MEDIUM — depends on team convention for progress evidence semantics.
  - Blind spot: Convention is not currently codified in this plan.
- **Decision**: FIXED via Fix A

### F3 — Rollout status table conflicts with per-phase completion notes

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Pattern Consistency
- **Location**: `context/foundation/test-plan.md:54-55,128-129`
- **Detail**: The §3 rollout table marks phases 2 and 3 as `not started`, while §6.6 states those phases were completed. Conflicting status surfaces can mislead future planning and test-rollout decisions.
- **Fix**: Synchronize the §3 status table rows for phases 2 and 3 with the completed rollout state and corresponding change folders.
- **Decision**: FIXED
