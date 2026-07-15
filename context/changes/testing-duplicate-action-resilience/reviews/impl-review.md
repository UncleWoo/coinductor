<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Testing Duplicate Action Resilience Implementation Plan

- **Plan**: `context/changes/testing-duplicate-action-resilience/plan.md`
- **Scope**: Full plan (Phases 1-3 of 3)
- **Date**: 2026-07-15
- **Verdict**: NEEDS ATTENTION
- **Findings**: 0 critical, 1 warning, 1 observation

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| Plan Adherence | PASS |
| Scope Discipline | PASS |
| Safety & Quality | WARNING |
| Architecture | PASS |
| Pattern Consistency | WARNING |
| Success Criteria | PASS |

## Findings

### F1 - Session token consume is not concurrency-safe

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Safety & Quality
- **Location**: `coinductor/views.py:27-35`, `coinductor/views.py:96-106`
- **Detail**: The token lifecycle is a mutable session list. Two near-simultaneous requests with the same token can both pass the `token in tokens` check before either request persists the removal, allowing duplicate writes under concurrency.
- **Fix A ⭐ Recommended**: Move idempotency claim to an atomic persistence boundary (for example, DB-backed token claim with unique `(user, token)`), then save expense only after successful claim.
  - Strength: Eliminates replay races across workers/processes and matches reliability expectations for idempotency.
  - Tradeoff: Requires migration and slightly expands scope beyond pure session-only mechanics.
  - Confidence: MEDIUM — race is real in concurrent request handling, but current app traffic profile is unknown.
  - Blind spot: Not benchmarked against the currently configured session backend and deployment topology.
- **Fix B**: Keep session token strategy but add explicit scope note + known limitation in plan/docs ("best effort for sequential submits; concurrent replay not guaranteed").
  - Strength: Preserves current lightweight implementation and avoids schema expansion.
  - Tradeoff: Leaves a known correctness gap under concurrency.
  - Confidence: HIGH — reflects current behavior accurately.
  - Blind spot: User-facing impact frequency in production is unknown.
- **Decision**: FIXED (Fix A)

### F2 - Invalid token path silently redirects instead of surfacing feedback

- **Severity**: 👁️ OBSERVATION
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Pattern Consistency
- **Location**: `coinductor/views.py:97-100`
- **Detail**: Missing/invalid token currently redirects silently, while other invalid POST paths re-render with inline form errors. This can look like a dropped submit.
- **Fix**: Re-render home with a non-field expense form error for invalid/missing token (while keeping successful replay as silent no-op if desired by product UX).
- **Decision**: FIXED
