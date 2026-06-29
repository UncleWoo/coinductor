<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Dashboard On-Track + Daily Limit Implementation Plan

- **Plan**: `context/changes/dashboard-on-track-daily-limit/plan.md`
- **Scope**: Full plan (Phases 1-4)
- **Date**: 2026-06-29
- **Verdict**: NEEDS ATTENTION
- **Findings**: 0 critical, 3 warnings, 1 observation

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| Plan Adherence | WARNING |
| Scope Discipline | PASS |
| Safety & Quality | WARNING |
| Architecture | PASS |
| Pattern Consistency | PASS |
| Success Criteria | WARNING |

## Findings

### F1 — Missing threshold-boundary unit test for pace tolerance

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Plan Adherence
- **Location**: `budget/services.py:38-41`, `budget/tests.py:84-216`
- **Detail**: Plan expected explicit threshold behavior coverage; service implements a 5% tolerance band, but tests do not assert boundary behavior around that threshold.
- **Fix**: Add one focused test at the tolerance edge (inside/outside 5%) in `DashboardMetricsServiceTests`.
- **Decision**: FIXED

### F2 — No-budget CTA points to admin area

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Safety & Quality
- **Location**: `coinductor/templates/home.html:25`
- **Detail**: “Set monthly budget” links to `{% url 'admin:index' %}`, which is often unavailable to non-staff users, creating a dead-end path for regular users.
- **Fix A ⭐ Recommended**: Keep CTA but change it to a user-facing route placeholder you control (e.g., future budget setup URL with clear fallback text).
  - Strength: Preserves UX intent without relying on admin privileges.
  - Tradeoff: Needs interim route/placeholder handling before S-03 exists.
  - Confidence: MEDIUM — depends on near-term S-03 routing decisions.
  - Blind spot: Current production user role assumptions were not exhaustively audited.
- **Fix B**: Keep admin link but explicitly label it “Admin budget setup” and conditionally show it only for staff users.
  - Strength: Honest behavior now; avoids misleading non-staff users.
  - Tradeoff: Non-staff still lacks direct setup path in S-01.
  - Confidence: HIGH — consistent with Django auth role checks.
  - Blind spot: Does not solve budget setup discoverability for normal users.
- **Decision**: FIXED (Fix A)

### F3 — UI tests do not assert status/velocity branch correctness

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Success Criteria
- **Location**: `coinductor/tests.py:75-96`, `coinductor/templates/home.html:67-73`
- **Detail**: Tests cover presence of text/sections but do not assert specific on-track/off-track label behavior or velocity-status branch rendering.
- **Fix**: Add assertions for badge text (`On track`/`Off track`) and at least one velocity-status branch output in view tests.
- **Decision**: FIXED

### F4 — Manual verifications are checked without durable repo evidence

- **Severity**: 👀 OBSERVATION
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Success Criteria
- **Location**: `context/changes/dashboard-on-track-daily-limit/plan.md:327-338`
- **Detail**: Manual checks are marked complete, but no concise artifact (note/log/screenshot reference) is stored alongside the change for auditability.
- **Fix**: Add a short manual verification note file under `context/changes/dashboard-on-track-daily-limit/reviews/` for future runs.
- **Decision**: FIXED
