<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Minimal Auth Scaffold

- **Plan**: context/changes/minimal-auth-scaffold/plan.md
- **Scope**: Phase 1-4 (Full Plan)
- **Date**: 2026-06-26
- **Verdict**: NEEDS ATTENTION
- **Findings**: [0 critical] [2 warnings] [1 observation]

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| Plan Adherence | WARNING |
| Scope Discipline | PASS |
| Safety & Quality | PASS |
| Architecture | PASS |
| Pattern Consistency | WARNING |
| Success Criteria | PASS |

## Findings

### F1 — Procfile release command degraded

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Plan Adherence
- **Location**: Procfile:1-2
- **Detail**: Plan specified: `release: npm install && npm run build && migrate && collectstatic`. Current Procfile has the full command commented out on line 1, with only `release: python manage.py migrate` active. Tailwind CSS will NOT build on Railway deploy — styles will break.
- **Fix**: Uncomment line 1 and remove the duplicate line 2 so the release command builds CSS, installs deps, migrates, and collects static.
  - Strength: Restores planned deploy behavior; matches commit fc61e06 which explicitly added the full release chain.
  - Tradeoff: Deploy time increases ~10-15s for npm install/build.
  - Confidence: HIGH — this exact command worked in earlier commits.
  - Blind spot: Haven't verified Railway env has Node.js available.
- **Decision**: ACCEPTED — Railway's new Railpack system auto-handles deps; old Nixpacks commands caused build conflicts. Simplified Procfile is correct for new system.

### F2 — Home view defined inline in urls.py

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Pattern Consistency
- **Location**: coinductor/urls.py:23-24
- **Detail**: The `home` view function is defined inline in urls.py while other views (signup, logout_view) live in views.py. Inconsistent module organization.
- **Fix**: Move home() to views.py and import in urls.py.
- **Decision**: FIXED

### F3 — railway.json not created (intentional removal)

- **Severity**: ℹ️ OBSERVATION
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Plan Adherence
- **Location**: N/A (missing file)
- **Detail**: Plan Phase 1 specified creating railway.json with Nixpacks config. Commit 0fe9eb1 explicitly removed it with message "remove railway.json and nixpacks.toml". This appears intentional — Railway auto-detects buildpacks from package.json + requirements.txt.
- **Fix**: Document deviation in plan epilogue (or no action if acceptable).
- **Decision**: SKIPPED — Same reasoning as F1; Railpack auto-detection makes explicit config unnecessary.
